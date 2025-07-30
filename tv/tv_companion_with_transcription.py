"""HDMI TV Companion with real-time transcription pipeline

Combines continuous TV transcription with video streaming to Gemini Live API
"""

import asyncio
import base64
from datetime import datetime
import io
import queue
import subprocess
import sys
import threading
import time
import traceback
import cv2
from google import genai
from google.cloud import speech
from google.genai import types
from PIL import Image
from scenedetect import AdaptiveDetector, ContentDetector, HistogramDetector, SceneManager
from scenedetect.backends import VideoCaptureAdapter

if sys.version_info < (3, 11, 0):
  import taskgroup, exceptiongroup

  asyncio.TaskGroup = taskgroup.TaskGroup
  asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

# Audio settings
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
STREAMING_LIMIT = 240000  # 4 minutes (Google Cloud Speech limit)

MODEL = "gemini-2.5-flash-preview-native-audio-dialog"

# HDMI capture device settings
HDMI_VIDEO_DEVICE = "/dev/video4"
HDMI_AUDIO_TARGET = (
    "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo"
)

client = genai.Client()

# TV Companion configuration
CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": (
        """You are an intelligent TV companion. You receive complete scene packages containing:
- A screenshot of what's on screen when the scene started
- All dialogue/audio that occurred during that scene
- Scene duration and number

Your role:
- Analyze each complete scene context (visual + audio together)
- Only speak when you have something genuinely interesting to say
- Don't comment on every scene - be selective and thoughtful
- You might comment on plot developments, visual storytelling, acting, cinematography, or interesting moments
- Consider both what you see and what you hear together

Stay natural and conversational. You're watching TV with a friend."""
    ),
}


class SceneBuffer:
  """Buffers visual and audio content for a single scene"""

  def __init__(self, scene_number: int):
    self.scene_number = scene_number
    self.frames = []  # Store multiple frames per scene
    self.transcripts = []
    self.start_time = time.time()

  def add_frame(self, frame_data, is_initial=False):
    """Add a frame to this scene"""
    elapsed = time.time() - self.start_time
    timestamp = f"{int(elapsed//60):02d}:{elapsed%60:05.2f}"

    frame_entry = {
        "data": frame_data,
        "timestamp": timestamp,
        "is_initial": is_initial,
    }
    self.frames.append(frame_entry)

    frame_type = "initial" if is_initial else "periodic"
    print(
        f"📸 Added {frame_type} frame to Scene {self.scene_number} at"
        f" {timestamp}"
    )

  def add_transcript(self, text: str):
    """Add a transcript line with timestamp"""
    elapsed = time.time() - self.start_time
    timestamp = f"{int(elapsed//60):02d}:{elapsed%60:05.2f}"
    self.transcripts.append(f"[{timestamp}] {text}")

  def get_duration(self) -> float:
    """Get scene duration in seconds"""
    return time.time() - self.start_time

  def create_scene_package(self) -> dict:
    """Create a complete scene package for the model"""
    duration = self.get_duration()
    transcript_text = "\n".join(self.transcripts) if self.transcripts else ""

    return {
        "type": "scene_package",
        "scene_number": self.scene_number,
        "duration": f"{duration:.1f}s",
        "transcript": transcript_text,
        "frames": self.frames,
        "summary": (
            f"Scene {self.scene_number} ({duration:.1f}s):"
            f" {len(self.transcripts)} dialogue lines,"
            f" {len(self.frames)} frames"
        ),
    }


class TVAudioStream:
  """Captures TV audio using pw-cat and provides it as a stream for transcription"""

  def __init__(self):
    self._buff = queue.Queue()
    self.closed = True
    self.audio_process = None

  async def __aenter__(self):
    self.closed = False
    # Start pw-cat process for TV audio
    cmd = [
        "pw-cat",
        "--record",
        "-",
        "--target",
        HDMI_AUDIO_TARGET,
        "--rate",
        str(SEND_SAMPLE_RATE),
        "--channels",
        "1",
        "--format",
        "s16",
        "--raw",
    ]

    self.audio_process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # Start feeding audio data into buffer
    asyncio.create_task(self._feed_buffer())
    return self

  async def __aexit__(self, type, value, traceback):
    self.closed = True
    if self.audio_process:
      self.audio_process.terminate()
      await self.audio_process.wait()
    self._buff.put(None)  # Signal generator to terminate

  async def _feed_buffer(self):
    """Read audio from pw-cat and put into buffer"""
    chunk_size = int(SEND_SAMPLE_RATE / 10)  # 100ms chunks
    bytes_expected = chunk_size * 2  # 2 bytes per s16 sample
    chunks_sent = 0

    while not self.closed:
      try:
        data = await self.audio_process.stdout.read(bytes_expected)
        if not data:
          print(f"📡 No more audio data from pw-cat")
          break

        self._buff.put(data)
        chunks_sent += 1

        if chunks_sent % 50 == 0:  # Log every 5 seconds
          print(
              f"📡 Audio buffer: {chunks_sent} chunks sent ({len(data)} bytes"
              " in last chunk)"
          )

      except Exception as e:
        print(f"❌ Audio feed error: {e}")
        break

  def generator(self):
    """Generator that yields audio chunks for Google Cloud Speech"""
    chunks_yielded = 0
    while not self.closed:
      try:
        chunk = self._buff.get(timeout=1.0)  # 1 second timeout
        if chunk is None:
          print("📡 Audio generator: received termination signal")
          return

        chunks_yielded += 1
        if chunks_yielded % 50 == 0:  # Log every 5 seconds
          print(
              f"📡 Audio generator: yielded {chunks_yielded} chunks"
              f" ({len(chunk)} bytes in last)"
          )

        yield chunk
      except queue.Empty:
        print("⚠️ Audio generator: timeout waiting for chunk")
        continue


class HDMITVCompanionWithTranscription:

  def __init__(self):
    self.audio_in_queue = None
    self.out_queue = None
    self.session = None
    self.video_cap = None
    self.speech_client = speech.SpeechClient()

    # Shared video capture for both scene detection and periodic screenshots
    self.shared_cap = None

    # Speech recognition config
    self.speech_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SEND_SAMPLE_RATE,
        language_code="en-US",
        max_alternatives=1,
    )

    self.streaming_config = speech.StreamingRecognitionConfig(
        config=self.speech_config, interim_results=True
    )

    # Scene detection setup
    self.scene_manager = SceneManager()
    self.scene_manager.add_detector(HistogramDetector())
    self.scene_detection_active = False
    self.video_fps = None  # Store frame rate for timestamp calculations

    # Scene buffering
    self.current_scene = None
    self.scene_counter = 0
    self.max_scene_duration = 180  # 3 minutes max per scene
    self.periodic_screenshot_interval = (
        30  # Take screenshot every 30 seconds within scene
    )
    self._last_scene_frame = (
        None  # Store current frame for periodic capture sharing
    )

  async def send_text(self):
    """Allow user to send text messages"""
    while True:
      text = await asyncio.to_thread(input, "message > ")
      if text.lower() == "q":
        break
      await self.session.send_realtime_input(text=text or ".")

  def on_new_scene(self, frame_img, frame_num):
    """Callback invoked when PySceneDetect finds a new scene"""
    # Calculate timestamp from frame number and fps
    timestamp_seconds = frame_num / self.video_fps if self.video_fps else 0
    minutes = int(timestamp_seconds // 60)
    seconds = timestamp_seconds % 60
    timestamp_str = f"{minutes:02d}:{seconds:05.2f}"

    print(f"🎬 Scene change detected at frame {frame_num} ({timestamp_str})")

    # Send previous scene package if it exists
    if self.current_scene is not None:
      self._finalize_current_scene()

    # Start new scene
    self._start_new_scene(frame_img, frame_num, timestamp_str)

  def _finalize_current_scene(self):
    """Send the current scene package to Gemini"""
    if self.current_scene is None:
      return

    scene_package = self.current_scene.create_scene_package()
    print(f"📦 Finalizing {scene_package['summary']}")

    try:
      self.out_queue.put_nowait(scene_package)
      print(f"✓ Scene package queued for Gemini")
    except:
      print(f"⚠️ Failed to queue scene package")

  def _start_new_scene(self, frame_img, frame_num, timestamp_str):
    """Start a new scene buffer"""
    self.scene_counter += 1
    self.current_scene = SceneBuffer(self.scene_counter)

    print(
        "🔍 _start_new_scene called: frame_img is"
        f" {'None' if frame_img is None else 'present'}"
    )

    # Convert frame to our format
    if frame_img is not None:
      try:
        frame_data = self._convert_frame_to_base64(frame_img)
        self.current_scene.add_frame(frame_data, is_initial=True)
        print(
            f"🎬 Started Scene {self.scene_counter} at frame"
            f" {frame_num} ({timestamp_str})"
        )
      except Exception as e:
        print(f"❌ Error converting initial frame: {e}")
        import traceback

        traceback.print_exc()
    else:
      print(f"🎬 Started Scene {self.scene_counter} (no frame available)")

  def _convert_frame_to_base64(self, frame_img):
    """Convert OpenCV frame to base64 format for Gemini"""
    try:
      print(
          "🔧 Converting frame:"
          f" shape={frame_img.shape if hasattr(frame_img, 'shape') else 'no shape'}"
      )

      # Convert numpy array to PIL Image
      frame_rgb = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)
      img = Image.fromarray(frame_rgb)
      img.thumbnail([1024, 1024])

      image_io = io.BytesIO()
      img.save(image_io, format="jpeg")
      image_io.seek(0)

      image_bytes = image_io.read()
      print(f"🔧 Frame converted successfully: {len(image_bytes)} bytes")

      return {
          "mime_type": "image/jpeg",
          "data": base64.b64encode(image_bytes).decode(),
      }
    except Exception as e:
      print(f"❌ Frame conversion failed: {e}")
      raise

  async def run_scene_detection(self):
    """Run PySceneDetect on HDMI video stream"""
    print("🎬 Starting PySceneDetect scene detection...")

    # Initialize shared video capture
    self.shared_cap = cv2.VideoCapture(HDMI_VIDEO_DEVICE)
    if not self.shared_cap.isOpened():
      print(f"❌ Cannot open HDMI video device {HDMI_VIDEO_DEVICE}")
      return

    self.shared_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    self.shared_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Get and store frame rate for timestamp calculations
    self.video_fps = self.shared_cap.get(cv2.CAP_PROP_FPS)
    print(f"📊 Video FPS: {self.video_fps}")

    # Wrap with VideoCaptureAdapter for PySceneDetect
    video_adapter = VideoCaptureAdapter(self.shared_cap)

    print(f"✓ HDMI video capture ready for scene detection")
    print(f"🎬 Using AdaptiveDetector for scene changes")

    # Run scene detection in a separate thread (it's blocking)
    await asyncio.to_thread(self._run_scene_detection_sync, video_adapter)

  def _run_scene_detection_sync(self, video_adapter):
    """Run scene detection synchronously in a thread"""
    try:
      self.scene_detection_active = True
      # This will block and call on_new_scene callback for each scene
      self.scene_manager.detect_scenes(
          video=video_adapter, callback=self.on_new_scene
      )
    except Exception as e:
      print(f"❌ Scene detection error: {e}")
      import traceback

      traceback.print_exc()
    finally:
      self.scene_detection_active = False
      if self.shared_cap:
        self.shared_cap.release()

  async def monitor_scene_duration(self):
    """Monitor scene duration and finalize long scenes"""
    print("⏱️ Starting scene duration monitor...")

    while True:
      if (
          self.current_scene is not None
          and self.current_scene.get_duration() > self.max_scene_duration
      ):

        print(
            f"⏱️ Scene {self.current_scene.scene_number} exceeded"
            f" {self.max_scene_duration}s, finalizing..."
        )
        self._finalize_current_scene()

        # Start a new scene without a frame (we'll get one on next scene change)
        self.scene_counter += 1
        self.current_scene = SceneBuffer(self.scene_counter)
        print(f"🎬 Started Scene {self.scene_counter} (duration timeout)")

      await asyncio.sleep(10)  # Check every 10 seconds

  async def capture_periodic_screenshots(self):
    """Capture periodic screenshots within the current scene using shared capture"""
    print(f"📸 Starting periodic screenshot capture every {self.periodic_screenshot_interval}s...")
    
    # Wait for shared capture to be initialized
    while self.shared_cap is None:
      await asyncio.sleep(1)
    
    print(f"📸 Shared video capture ready for periodic screenshots")
    
    while True:
      # Capture immediately if there's a current scene
      if self.current_scene is not None:
        ret, frame = self.shared_cap.read()
        if ret:
          try:
            frame_data = self._convert_frame_to_base64(frame)
            self.current_scene.add_frame(frame_data, is_initial=False)
            print(f"✓ Added periodic frame to Scene {self.current_scene.scene_number}")
          except Exception as e:
            print(f"❌ Error adding periodic frame: {e}")
        else:
          print("⚠️ Failed to capture periodic screenshot")
      
      # Then sleep
      await asyncio.sleep(self.periodic_screenshot_interval)

  async def transcribe_tv_audio(self):
    """Continuously transcribe TV audio and send to Gemini"""
    print("🎤 Starting TV audio transcription...")

    while True:
      try:
        print("🎤 Creating new audio stream...")
        async with TVAudioStream() as stream:
          print("🎤 Audio stream created, starting transcription...")

          # Run transcription in a separate thread to avoid blocking
          await asyncio.to_thread(self._run_transcription_sync, stream)

      except Exception as e:
        print(f"❌ Transcription error: {e}")
        import traceback

        traceback.print_exc()
        await asyncio.sleep(2)  # Brief pause before restarting

  def _run_transcription_sync(self, stream):
    """Run transcription synchronously in a thread"""
    audio_generator = stream.generator()
    requests = (
        speech.StreamingRecognizeRequest(audio_content=content)
        for content in audio_generator
    )

    print("🎤 Sending requests to Google Cloud Speech...")
    responses = self.speech_client.streaming_recognize(
        self.streaming_config, requests
    )

    print("🎤 Processing responses...")
    transcripts_received = 0

    for response in responses:
      if not response.results:
        continue

      result = response.results[0]
      if not result.alternatives:
        continue

      transcript = result.alternatives[0].transcript

      # Only send final results to avoid spam
      if result.is_final and transcript.strip():
        transcripts_received += 1
        print(f"📝 Transcribed #{transcripts_received}: {transcript}")

        # Add to current scene buffer instead of sending immediately
        if self.current_scene is not None:
          self.current_scene.add_transcript(transcript)
          print(
              f"📝 Added to Scene {self.current_scene.scene_number}:"
              f" {transcript[:50]}..."
          )
        else:
          # No scene yet, create first scene
          self.scene_counter += 1
          self.current_scene = SceneBuffer(self.scene_counter)
          self.current_scene.add_transcript(transcript)
          print(
              f"📝 Started Scene {self.scene_counter} with transcript:"
              f" {transcript[:50]}..."
          )

  async def send_realtime(self):
    """Send scene packages to Gemini Live API using client_content"""
    packages_sent = 0

    while True:
      msg = await self.out_queue.get()

      if isinstance(msg, dict) and msg.get("type") == "scene_package":
        packages_sent += 1
        scene_num = msg.get("scene_number", "?")
        duration = msg.get("duration", "?")
        frames = msg.get("frames", [])

        print(
            f"📤 Sending Scene Package #{packages_sent} (Scene {scene_num},"
            f" {duration}) to Gemini"
        )

        # Build Content parts list
        parts = []

        # Add scene text if there's actual dialogue
        if msg["transcript"].strip():
          scene_text = f"""Scene {scene_num} ({duration}):

{msg['transcript']}"""
          parts.append({"text": scene_text})
          print(f"📝 Added dialogue for Scene {scene_num}")
        else:
          print(f"🔇 No dialogue for Scene {scene_num}")

        # Add all frames as image parts
        for i, frame_entry in enumerate(frames):
          frame_type = "initial" if frame_entry["is_initial"] else "periodic"
          timestamp = frame_entry["timestamp"]

          parts.append({
              "inline_data": {
                  "mime_type": frame_entry["data"]["mime_type"],
                  "data": frame_entry["data"]["data"],
              }
          })
          print(
              f"📸 Added {frame_type} frame #{i+1} for Scene"
              f" {scene_num} ({timestamp})"
          )

        # Send as complete client content turn (text + images together)
        if parts:  # Only send if we have content
          content = {"role": "user", "parts": parts}
          await self.session.send_client_content(
              turns=content, turn_complete=True
          )
          print(
              f"📤 Sent complete scene package: {len(parts)} parts (text +"
              " images together)"
          )
        else:
          print(f"⚠️ No content to send for Scene {scene_num}")

  async def receive_audio(self):
    """Receive Gemini's audio responses"""
    while True:
      turn = self.session.receive()
      async for response in turn:
        if data := response.data:
          self.audio_in_queue.put_nowait(data)
          continue
        if text := response.text:
          print(f"🎬 TV Companion: {text}")

      # Handle interruptions by clearing audio queue
      while not self.audio_in_queue.empty():
        self.audio_in_queue.get_nowait()

  async def play_audio(self):
    """Play Gemini's audio responses using pw-cat"""
    cmd = [
        "pw-cat",
        "--playback",
        "-",
        "--rate",
        str(RECEIVE_SAMPLE_RATE),
        "--channels",
        "1",
        "--format",
        "s16",
        "--raw",
    ]

    try:
      play_process = await asyncio.create_subprocess_exec(
          *cmd, stdin=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
      )

      print("✓ Audio playback started with pw-cat")

      while True:
        bytestream = await self.audio_in_queue.get()
        play_process.stdin.write(bytestream)
        await play_process.stdin.drain()

    except Exception as e:
      print(f"❌ pw-cat playback error: {e}")

  async def run(self):
    """Main TV companion loop with transcription and scene detection"""
    print(
        "📺 Starting HDMI TV Companion with Transcription & Scene Detection..."
    )
    print("🎧 Make sure to use headphones to prevent audio feedback!")
    print("💡 Type 'q' to quit")

    try:
      async with (
          client.aio.live.connect(model=MODEL, config=CONFIG) as session,
          asyncio.TaskGroup() as tg,
      ):
        self.session = session
        self.audio_in_queue = asyncio.Queue()
        self.out_queue = asyncio.Queue(maxsize=10)

        # Start all tasks
        send_text_task = tg.create_task(self.send_text())
        tg.create_task(self.send_realtime())
        tg.create_task(self.transcribe_tv_audio())
        tg.create_task(self.run_scene_detection())  # PySceneDetect
        tg.create_task(self.monitor_scene_duration())  # Scene duration monitor
        tg.create_task(
            self.capture_periodic_screenshots()
        )  # Periodic screenshots
        tg.create_task(self.receive_audio())
        tg.create_task(self.play_audio())

        await send_text_task
        raise asyncio.CancelledError("User requested exit")

    except asyncio.CancelledError:
      print("👋 TV Companion stopped")
    except Exception as e:
      traceback.print_exception(e)


if __name__ == "__main__":
  companion = HDMITVCompanionWithTranscription()
  asyncio.run(companion.run())
