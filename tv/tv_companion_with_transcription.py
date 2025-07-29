"""
HDMI TV Companion with real-time transcription pipeline
Combines continuous TV transcription with video streaming to Gemini Live API
"""

import asyncio
import base64
import io
import sys
import traceback
import subprocess
import cv2
import queue
import threading
import time
from PIL import Image

from google import genai
from google.cloud import speech

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
HDMI_VIDEO_DEVICE = '/dev/video4'
HDMI_AUDIO_TARGET = "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo"

client = genai.Client()

# TV Companion configuration
CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": """You are an intelligent TV companion. You can see what's playing via video frames and hear via transcribed text.

Your role:
- Watch TV video frames and read transcribed dialogue/audio
- Only speak when you have something genuinely interesting to say
- Don't comment on every transcript chunk - be selective
- The transcribed text will be marked as [TV]: "dialogue here"
- You might comment on plot developments, trivia, or interesting moments

Stay natural and conversational."""
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
            "pw-cat", "--record", "-",
            "--target", HDMI_AUDIO_TARGET,
            "--rate", str(SEND_SAMPLE_RATE),
            "--channels", "1",
            "--format", "s16",
            "--raw"
        ]
        
        self.audio_process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
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
                    print(f"📡 Audio buffer: {chunks_sent} chunks sent ({len(data)} bytes in last chunk)")
                    
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
                    print(f"📡 Audio generator: yielded {chunks_yielded} chunks ({len(chunk)} bytes in last)")
                    
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
        
        # Speech recognition config
        self.speech_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SEND_SAMPLE_RATE,
            language_code="en-US",
            max_alternatives=1,
        )
        
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.speech_config,
            interim_results=True
        )

    async def send_text(self):
        """Allow user to send text messages"""
        while True:
            text = await asyncio.to_thread(input, "message > ")
            if text.lower() == "q":
                break
            await self.session.send_realtime_input(text=text or ".")

    def _get_hdmi_frame(self):
        """Capture single frame from HDMI device"""
        ret, frame = self.video_cap.read()
        if not ret:
            return None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img.thumbnail([1024, 1024])

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        image_bytes = image_io.read()
        return {
            "mime_type": "image/jpeg", 
            "data": base64.b64encode(image_bytes).decode()
        }

    async def get_hdmi_frames(self):
        """Continuously capture HDMI video frames"""
        self.video_cap = await asyncio.to_thread(cv2.VideoCapture, HDMI_VIDEO_DEVICE)
        
        if not self.video_cap.isOpened():
            print(f"❌ Cannot open HDMI video device {HDMI_VIDEO_DEVICE}")
            return

        self.video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        print(f"✓ HDMI video capture started on {HDMI_VIDEO_DEVICE}")

        while True:
            frame = await asyncio.to_thread(self._get_hdmi_frame)
            if frame is None:
                continue

            # Send frame every 10 seconds to avoid overwhelming
            await asyncio.sleep(10.0)
            await self.out_queue.put(frame)

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
            self.streaming_config, 
            requests
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
                
                # Send to async queue (thread-safe)
                transcript_text = f"[TV]: {transcript}"
                try:
                    self.out_queue.put_nowait({"type": "transcript", "text": transcript_text})
                except asyncio.QueueFull:
                    print("⚠️ Transcript queue full, dropping message")

    async def send_realtime(self):
        """Send transcripts and video frames to Gemini Live API"""
        items_sent = 0
        
        while True:
            msg = await self.out_queue.get()
            
            if isinstance(msg, dict):
                if msg.get("type") == "transcript":
                    # Send transcribed text
                    items_sent += 1
                    print(f"📤 Sending transcript #{items_sent} to Gemini: {msg['text'][:50]}...")
                    await self.session.send_realtime_input(text=msg["text"])
                    
                elif "mime_type" in msg and msg["mime_type"] == "image/jpeg":
                    # Send video frame
                    items_sent += 1
                    print(f"📤 Sending video frame #{items_sent} to Gemini")
                    await self.session.send_realtime_input(media=msg)

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
            "pw-cat", "--playback", "-",
            "--rate", str(RECEIVE_SAMPLE_RATE),
            "--channels", "1", 
            "--format", "s16", "--raw"
        ]
        
        try:
            play_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            print("✓ Audio playback started with pw-cat")
            
            while True:
                bytestream = await self.audio_in_queue.get()
                play_process.stdin.write(bytestream)
                await play_process.stdin.drain()
                
        except Exception as e:
            print(f"❌ pw-cat playback error: {e}")

    async def run(self):
        """Main TV companion loop with transcription"""
        print("📺 Starting HDMI TV Companion with Transcription...")
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
                tg.create_task(self.transcribe_tv_audio())  # New transcription task
                tg.create_task(self.get_hdmi_frames())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            print("👋 TV Companion stopped")
        except Exception as e:
            if self.video_cap:
                self.video_cap.release()
            traceback.print_exception(e)

if __name__ == "__main__":
    companion = HDMITVCompanionWithTranscription()
    asyncio.run(companion.run())
