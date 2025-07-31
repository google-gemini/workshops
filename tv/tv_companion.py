# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
HDMI TV Companion using Gemini Live API
Streams HDMI audio and video to Gemini for intelligent TV commentary
"""

import asyncio
import base64
import io
import subprocess
import sys
import tempfile
import traceback

import cv2
from google import genai
from PIL import Image

if sys.version_info < (3, 11, 0):
    import exceptiongroup
    import taskgroup

    asyncio.TaskGroup = taskgroup.TaskGroup
    asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

# Audio settings for Gemini Live API
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

MODEL = "gemini-2.5-flash-preview-native-audio-dialog"

# HDMI capture device settings
HDMI_VIDEO_DEVICE = "/dev/video4"
HDMI_AUDIO_TARGET = "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo"

client = genai.Client()

# TV Companion system configuration
CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": """You are an intelligent TV companion. You can see and hear what's playing on the TV through HDMI capture.

Your role:
- Watch and listen to TV content (movies, shows, sports, news, etc.)
- Only speak up when you have something genuinely interesting or helpful to say
- Don't feel obligated to comment on every frame - silence is perfectly fine
- Be conversational and engaging when you do speak
- You might comment on:
  * Plot developments or interesting scenes
  * Historical context or trivia
  * Technical aspects (cinematography, effects, etc.)
  * Sports play analysis or statistics
  * News context or background information
  * Funny moments or easter eggs

Stay natural and don't over-explain. Think of yourself as a knowledgeable friend watching along.""",
}


class HDMITVCompanion:
    def __init__(self):
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.audio_process = None
        self.video_cap = None

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

        # Convert BGR → RGB (OpenCV uses BGR, PIL expects RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)

        # Scale down for Gemini (same as Get_started_LiveAPI.py)
        img.thumbnail([1024, 1024])

        # Convert to base64 for Gemini Live API
        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        image_bytes = image_io.read()
        return {"mime_type": "image/jpeg", "data": base64.b64encode(image_bytes).decode()}

    async def get_hdmi_frames(self):
        """Continuously capture HDMI video frames"""
        # Initialize HDMI video capture
        self.video_cap = await asyncio.to_thread(cv2.VideoCapture, HDMI_VIDEO_DEVICE)

        if not self.video_cap.isOpened():
            print(f"❌ Cannot open HDMI video device {HDMI_VIDEO_DEVICE}")
            return

        # Set resolution (optional)
        self.video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        print(f"✓ HDMI video capture started on {HDMI_VIDEO_DEVICE}")

        while True:
            frame = await asyncio.to_thread(self._get_hdmi_frame)
            if frame is None:
                continue

            # Send frame every 1 second (same as Get_started_LiveAPI.py)
            await asyncio.sleep(1.0)
            await self.out_queue.put(frame)

    async def listen_hdmi_audio(self):
        """Capture HDMI audio using pw-cat and send to Gemini"""

        # Start pw-cat subprocess for HDMI audio capture
        cmd = [
            "pw-cat",
            "--record",
            "-",  # Write to stdout
            "--target",
            HDMI_AUDIO_TARGET,
            "--rate",
            str(SEND_SAMPLE_RATE),
            "--channels",
            "1",
            "--format",
            "s16",
            "--raw",  # Output raw PCM data, not WAV
        ]

        print(f"🎤 Starting pw-cat audio capture: {' '.join(cmd)}")

        try:
            self.audio_process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            print("✓ HDMI audio capture started with pw-cat")

            # Continuously read audio chunks from pw-cat stdout
            while True:
                # Read chunk size for Gemini (1600 bytes = ~0.1 sec at 16kHz mono s16)
                data = await self.audio_process.stdout.read(1600)

                if not data:
                    print("❌ pw-cat audio stream ended")
                    break

                await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

        except Exception as e:
            print(f"❌ pw-cat audio error: {e}")
            import traceback

            traceback.print_exc()

    async def send_realtime(self):
        """Send audio/video data to Gemini Live API"""
        while True:
            msg = await self.out_queue.get()
            if "mime_type" in msg and msg["mime_type"] == "audio/pcm":
                # Audio data
                await self.session.send_realtime_input(audio=msg)
            elif "mime_type" in msg and msg["mime_type"] == "image/jpeg":
                # Video frame data - use 'media' parameter for images
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

        # Start pw-cat subprocess for audio playback
        cmd = [
            "pw-cat",
            "--playback",
            "-",  # Read from stdin
            "--rate",
            str(RECEIVE_SAMPLE_RATE),
            "--channels",
            "1",
            "--format",
            "s16",
            "--raw",  # Input raw PCM data, not WAV
        ]

        print(f"🔊 Starting pw-cat audio playback: {' '.join(cmd)}")

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
            import traceback

            traceback.print_exc()

    async def run(self):
        """Main TV companion loop"""
        print("📺 Starting HDMI TV Companion...")
        print("🎧 Make sure to use headphones to prevent audio feedback!")
        print("💡 Type 'q' to quit, or just watch as Gemini comments on your TV content")

        try:
            async with (
                client.aio.live.connect(model=MODEL, config=CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                # Start all tasks
                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_hdmi_audio())
                tg.create_task(self.get_hdmi_frames())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            print("👋 TV Companion stopped")
        except Exception as e:
            if self.audio_process:
                self.audio_process.terminate()
                await self.audio_process.wait()
            if self.video_cap:
                self.video_cap.release()
            traceback.print_exception(e)


if __name__ == "__main__":
    companion = HDMITVCompanion()
    asyncio.run(companion.run())
