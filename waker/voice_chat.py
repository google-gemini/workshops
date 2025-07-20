# -*- coding: utf-8 -*-
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
Wind Waker Voice Chat with Gemini 2.5 Live API

## Setup

To install the dependencies for this script, run:

```
brew install portaudio
poetry install
```

## API key

Ensure the `GOOGLE_API_KEY` environment variable is set to the api-key
you obtained from Google AI Studio.

## Run

To run the script:

```
cd waker
poetry run python voice_chat.py
```

Start talking to Gemini about Wind Waker!
Press Ctrl+C to exit.
"""

import asyncio
import sys
import traceback

import pyaudio
from google import genai
from google.genai import types

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
    "system_instruction": """You are a helpful gaming companion for The Legend of Zelda: Wind Waker.
    You're knowledgeable about the game's mechanics, locations, items, and story.
    You can help sail to different locations and provide guidance about the game.
    Keep responses conversational and not too long since this is voice chat.""",
    "tools": [
        {"function_declarations": [
            {
                "name": "sail_to",
                "description": "Sail to a specific location in Wind Waker",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The destination to sail to (e.g., 'Dragon Roost Island', 'Windfall Island')"
                        }
                    },
                    "required": ["location"]
                }
            }
        ]}
    ]
}


class WindWakerVoiceChat:
    def __init__(self):
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.audio_stream = None
        self.pya = None
        self.client = None

    async def setup_audio(self):
        """Initialize PyAudio with error handling"""
        try:
            self.pya = pyaudio.PyAudio()
            print("✓ Audio system initialized")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize audio: {e}")
            print("Make sure you have audio devices available and portaudio installed")
            return False

    async def listen_audio(self):
        """Capture audio from microphone"""
        try:
            mic_info = self.pya.get_default_input_device_info()
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

            if __debug__:
                kwargs = {"exception_on_overflow": False}
            else:
                kwargs = {}

            while True:
                data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
                await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

        except Exception as e:
            print(f"✗ Audio capture error: {e}")
            raise

    async def send_realtime(self):
        """Send audio data to Gemini"""
        while True:
            msg = await self.out_queue.get()
            await self.session.send_realtime_input(audio=msg)

    async def receive_audio(self):
        """Receive responses from Gemini"""
        while True:
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    self.audio_in_queue.put_nowait(data)
                    continue
                if text := response.text:
                    print(f"🤖 Gemini: {text}", end="")
                    continue
                
                # Handle tool calls
                tool_call = response.tool_call
                if tool_call is not None:
                    await self.handle_tool_call(tool_call)
                    continue

            # Handle interruptions - clear audio queue
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

    async def handle_tool_call(self, tool_call):
        """Handle tool calls from Gemini"""
        function_responses = []
        for fc in tool_call.function_calls:
            print(f"\n🔧 Tool call: {fc.name}")
            
            if fc.name == "sail_to":
                location = fc.args.get("location", "unknown location")
                print(f"🚢 Sailing to {location}...")
                result = {
                    "status": "sailing", 
                    "destination": location,
                    "message": f"Setting sail for {location}! Keep an eye out for enemies and obstacles."
                }
            else:
                result = {"error": f"Unknown function: {fc.name}"}
            
            function_responses.append(types.FunctionResponse(
                id=fc.id,
                name=fc.name,
                response=result
            ))
        
        await self.session.send_tool_response(function_responses=function_responses)

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
        """Main chat loop"""
        if not await self.setup_audio():
            return

        try:
            self.client = genai.Client()  # GOOGLE_API_KEY must be set
            print("✓ Connected to Gemini")

            async with (
                self.client.aio.live.connect(model=MODEL, config=CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                print("✓ Live session established")
                print("🎮 Wind Waker Voice Chat Ready!")
                print("💬 Start talking about Wind Waker... (Ctrl+C to exit)")

                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_audio())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for chatting about Wind Waker!")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"✗ Error: {e}")
            traceback.print_exc()
        finally:
            if self.audio_stream:
                self.audio_stream.close()
            if self.pya:
                self.pya.terminate()


if __name__ == "__main__":
    chat = WindWakerVoiceChat()
    try:
        asyncio.run(chat.run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
