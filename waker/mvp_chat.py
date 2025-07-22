#!/usr/bin/env python3
"""
Minimal Audio Chat - based on Get_started_LiveAPI_NativeAudio.py
Stripped down to absolute basics to test connection
"""

import asyncio
import sys

import pyaudio
from google import genai

if sys.version_info < (3, 11, 0):
    import exceptiongroup
    import taskgroup

    asyncio.TaskGroup = taskgroup.TaskGroup
    asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

MODEL = "gemini-2.5-flash-preview-native-audio-dialog"
CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": "You are a helpful assistant. Respond immediately when the user speaks.",
}

client = genai.Client()


class MinimalAudioChat:
    def __init__(self):
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.audio_stream = None
        self.pya = pyaudio.PyAudio()

    def find_pulse_device(self):
        """Find a PulseAudio device that works with PipeWire"""
        for i in range(self.pya.get_device_count()):
            info = self.pya.get_device_info_by_index(i)
            if "pulse" in info["name"].lower() and info["maxInputChannels"] > 0:
                return info
        return self.pya.get_default_input_device_info()

    async def listen_audio(self):
        """Capture audio from microphone"""
        mic_info = self.find_pulse_device()
        print(f"🎤 Using microphone: {mic_info['name']}")

        self.audio_stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )

        while True:
            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, exception_on_overflow=False)
            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

    async def send_realtime(self):
        """Send audio data to Gemini"""
        counter = 0
        while True:
            msg = await self.out_queue.get()
            counter += 1
            if counter % 100 == 0:  # Print every 100 chunks
                print(f"📤 Sent {counter} audio chunks")
            await self.session.send_realtime_input(audio=msg)

    async def receive_audio(self):
        """Receive responses from Gemini"""
        print("🎧 Starting to listen for responses...")
        while True:
            print("⏳ Waiting for turn...")
            turn = self.session.receive()
            print("📥 Got turn, processing responses...")
            async for response in turn:
                if data := response.data:
                    print(f"🔊 Received audio data: {len(data)} bytes")
                    self.audio_in_queue.put_nowait(data)
                    continue
                if text := response.text:
                    print(f"🤖 Gemini: {text}", end="")

            # Clear audio queue on turn completion
            print("🔄 Turn completed")
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

    async def play_audio(self):
        """Play audio responses"""
        stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)

    async def run(self):
        """Main loop"""
        try:
            async with (
                client.aio.live.connect(model=MODEL, config=CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                print("✅ Connected! Say something...")

                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_audio())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            if self.audio_stream:
                self.audio_stream.close()
            self.pya.terminate()


if __name__ == "__main__":
    chat = MinimalAudioChat()
    try:
        asyncio.run(chat.run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
