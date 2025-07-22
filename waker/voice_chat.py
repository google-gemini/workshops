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
import base64
import io
import json
import sys
import traceback

import mss
import PIL.Image
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

    IMPORTANT: Whenever the user asks about the current game state, what's happening on screen,
    where Link is, what enemies are around, health status, or any other information about the
    current game situation, you should ALWAYS use the get_game_status tool first to see what's
    actually happening in the game before responding.

    Keep responses conversational and not too long since this is voice chat.""",
    "tools": [
        {
            "function_declarations": [
                {
                    "name": "sail_to",
                    "description": "Sail to a specific location in Wind Waker",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The destination to sail to (e.g., 'Dragon Roost Island', 'Windfall Island')",
                            }
                        },
                        "required": ["location"],
                    },
                },
                {
                    "name": "get_game_status",
                    "description": "Get current Wind Waker game state including screenshot and metadata",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Specific question or context about what to analyze in the game (optional)",
                            }
                        },
                        "required": [],
                    },
                },
            ]
        }
    ],
}


class WindWakerVoiceChat:
    def __init__(self):
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.audio_stream = None
        self.pya = None
        self.client = None

    def find_pulse_device(self):
        """Find a PulseAudio device that works with PipeWire"""
        for i in range(self.pya.get_device_count()):
            info = self.pya.get_device_info_by_index(i)
            if "pulse" in info["name"].lower() and info["maxInputChannels"] > 0:
                return info
        return self.pya.get_default_input_device_info()

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

                # Handle code execution parts
                server_content = response.server_content
                if server_content is not None:
                    model_turn = server_content.model_turn
                    if model_turn:
                        for part in model_turn.parts:
                            if part.executable_code:
                                print(f"🧠 Gemini thinking: {part.executable_code.code}")
                            if part.code_execution_result:
                                print(f"💭 Result: {part.code_execution_result.output}")
                    continue

            # Handle interruptions - clear audio queue
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

    async def handle_tool_call(self, tool_call):
        """Handle tool calls from Gemini"""
        function_responses = []
        screenshot_to_send = None

        for fc in tool_call.function_calls:
            print(f"\n🔧 Tool call: {fc.name}")

            if fc.name == "sail_to":
                location = fc.args.get("location", "unknown location")
                print(f"🚢 Sailing to {location}...")
                result = {
                    "status": "sailing",
                    "destination": location,
                    "message": f"Setting sail for {location}! Keep an eye out for enemies and obstacles.",
                }
            elif fc.name == "get_game_status":
                print("📸 Taking game screenshot...")
                screenshot_data = self.take_screenshot()

                if screenshot_data:
                    # Get user query from function arguments if provided
                    user_query = fc.args.get("query", "")

                    # Analyze screenshot with Gemini vision
                    vision_analysis = self.analyze_screenshot_with_gemini(screenshot_data, user_query)

                    # Pass complete vision analysis with context
                    result = {"user_query": user_query, "vision_analysis": vision_analysis, "screenshot_captured": True}

                    # Store screenshot to send as separate user message
                    screenshot_to_send = screenshot_data
                else:
                    result = {
                        "user_query": fc.args.get("query", ""),
                        "vision_analysis": {"error": "Failed to capture screenshot"},
                        "screenshot_captured": False,
                    }

            else:
                result = {"error": f"Unknown function: {fc.name}"}

            function_responses.append(types.FunctionResponse(id=fc.id, name=fc.name, response=result))

        # Send tool response first
        await self.session.send_tool_response(function_responses=function_responses)

        # Skip sending screenshot as separate message since vision analysis
        # already provides detailed information to the chat model
        if screenshot_to_send:
            print("📤 Screenshot analysis complete - vision data sent via tool response")

    def analyze_screenshot_with_gemini(self, screenshot_data, user_query=""):
        """Analyze screenshot using Gemini 2.5 Flash"""
        try:
            print(f"🔍 Analyzing screenshot with Gemini 2.5 Flash...")
            print(f"🔍 User query: '{user_query}'")

            client = genai.Client()

            # Convert base64 back to bytes
            image_bytes = base64.b64decode(screenshot_data["data"])
            print(f"🔍 Decoded image: {len(image_bytes)} bytes")

            # Create the prompt
            prompt = f"""
            Analyze this Wind Waker screenshot and provide detailed observations about the current game state.

            User query: {user_query if user_query else "General game status"}

            Please observe and report on anything relevant you see, including but not limited to:
            - Current location/environment
            - Link's health and status
            - Any enemies, NPCs, or creatures
            - Items, collectibles, or interactive objects
            - UI elements and their values
            - The King of Red Lions boat status
            - Weather and environmental conditions
            - Any actions Link appears to be performing
            - Anything unusual, interesting, or noteworthy

            Focus especially on details relevant to the user's query. Return your observations as JSON.
            """

            print(f"🔍 Sending request to Gemini...")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Part.from_bytes(data=image_bytes, mime_type=screenshot_data["mime_type"]), prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )

            print(f"🔍 Received response from Gemini")
            analysis = json.loads(response.text)
            print(f"🔍 Analysis result: {analysis}")
            return analysis

        except Exception as e:
            print(f"🔍 Vision analysis error: {e}")
            traceback.print_exc()
            return {
                "location": "unknown",
                "health": "unknown",
                "enemies": [],
                "items_visible": [],
                "boat_status": "unknown",
                "weather": "unknown",
                "analysis": f"Vision analysis failed: {str(e)}",
            }

    def take_screenshot(self):
        """Take screenshot using mss, similar to Get_started_LiveAPI.py"""
        try:
            print("📷 Starting screenshot capture...")
            sct = mss.mss()
            monitor = sct.monitors[0]  # All monitors
            print(f"📷 Using monitor: {monitor}")
            screenshot = sct.grab(monitor)
            print(f"📷 Screenshot captured: {screenshot.size}")

            # Convert to PIL Image
            img = PIL.Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img.thumbnail([1024, 1024])  # Resize like in the example
            print(f"📷 Image resized to: {img.size}")

            # Convert to base64 JPEG
            image_io = io.BytesIO()
            img.save(image_io, format="jpeg")
            image_io.seek(0)

            image_bytes = image_io.read()
            print(f"📷 Screenshot converted to {len(image_bytes)} bytes")
            return {"mime_type": "image/jpeg", "data": base64.b64encode(image_bytes).decode()}
        except Exception as e:
            print(f"📸 Screenshot error: {e}")
            return None

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
