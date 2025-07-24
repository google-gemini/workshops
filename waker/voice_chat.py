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

"""Wind Waker Voice Chat with Gemini 2.5 Live API

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
from datetime import datetime
import io
import json
import logging
import os
import socket
import sys
import time
import traceback
import warnings
from contextlib import redirect_stderr

from google import genai
from google.genai import types
from mem0 import MemoryClient
import mss
import numpy as np
import PIL.Image
import pyaudio

# Suppress ALL warnings - nuclear option but necessary
warnings.filterwarnings("ignore")
# Also suppress via logging
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("google.genai").setLevel(logging.ERROR)

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
    "system_instruction": """You're a Wind Waker gaming companion.

    To answer questions about the game, use search_walkthrough.
    To recall what the user has done, use search_user_history.
    To see what's happening on screen, use see_game_screen.

    Keep responses short for voice chat.""",
    "tools": [{
        "function_declarations": [
            {
                "name": "see_game_screen",
                "description": (
                    "Sees and analyzes the game screen to understand what is"
                    " currently happening. This is your way of looking at the"
                    " game to answer questions about the visuals."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "The user's question about what is on screen."
                                " This provides context for the visual"
                                " analysis."
                            ),
                        }
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "search_walkthrough",
                "description": (
                    "Search Wind Waker walkthrough for accurate information"
                    " about songs, quests, locations, items, and game"
                    " mechanics. Recommended for specific game details to"
                    " ensure accuracy."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "What to search for (e.g., 'Wind's Requiem"
                                " sequence', 'Dragon Roost Island walkthrough',"
                                " 'Triforce Shard locations')"
                            ),
                        }
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "search_user_history",
                "description": (
                    "Search the user's personal game history and past actions. "
                    "Use this to recall what the user has already done, places "
                    "they've visited, items they've collected, or questions "
                    "they've previously asked. Leave query blank to get recent history."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Optional: What to search for in user's history (e.g., "
                                "'islands visited', 'songs learned', 'Dragon Roost'). "
                                "Leave blank to get recent activity."
                            ),
                        }
                    },
                    "required": [],  # No required params - query is optional
                },
            },
            {
                "name": "play_song",
                "description": (
                    "Play a Wind Waker song. Available songs:\n"
                    "- winds_requiem: Changes wind direction (Up, Left, Right)\n"
                    "- ballad_of_gales: Warps to cyclone locations (Down, Right, Left, Up)\n"
                    "- command_melody: Controls statues/companions (Left, Center, Right, Center)\n"
                    "- earth_gods_lyric: Awakens Earth Sage (Down, Down, Center, Right, Left, Center)\n"
                    "- wind_gods_aria: Awakens Wind Sage (Up, Up, Down, Right, Left, Right)\n"
                    "- song_of_passing: Changes day to night (Right, Left, Down)"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "song_name": {
                            "type": "string",
                            "enum": ["winds_requiem", "ballad_of_gales", "command_melody", 
                                     "earth_gods_lyric", "wind_gods_aria", "song_of_passing"],
                            "description": "The song to play"
                        }
                    },
                    "required": ["song_name"],
                },
            },
        ]
    }],
}


def send_controller_command(cmd):
    """Send a single controller command to the daemon"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 9999))
        sock.send(json.dumps(cmd).encode())
        sock.close()
        return True
    except Exception as e:
        print(f"⚠️  Controller command failed: {e}")
        return False


def send_controller_sequence(commands):
    """Send a sequence of controller commands with timing"""
    for cmd in commands:
        if not send_controller_command(cmd):
            return False
        # Handle delay if specified
        if 'delay' in cmd:
            time.sleep(cmd['delay'])
    return True


class WindWakerVoiceChat:

  def __init__(self):
    self.audio_in_queue = None
    self.out_queue = None
    self.session = None
    self.audio_stream = None
    self.pya = None
    self.client = None
    self.memory_client = self._init_memory_client()
    self.conversation_context = []  # Track conversation flow

  def _init_memory_client(self):
    """Initialize mem0 client for episodic memory"""
    api_key = os.getenv("MEM0_API_KEY")
    if not api_key:
      print("⚠️  MEM0_API_KEY not set, episodic memory disabled")
      return None

    try:
      client = MemoryClient(
          api_key=api_key,
          org_id="org_lOJM2vCRxHhS7myVb0vvaaY1rUauhqkKbg7Dg7KZ",
          project_id="proj_WWn2wvUn2BjtqIc1BHHZQ3w7fyAwSKaMv5dnlazF",
      )
      print("✓ Episodic memory initialized")
      return client
    except Exception as e:
      print(f"⚠️  Failed to initialize memory: {e}")
      return None

  async def _store_memory_async(self, context):
    """Store memory asynchronously to avoid blocking audio"""
    try:
      await asyncio.to_thread(
          self.memory_client.add,
          messages=[{"role": "user", "content": context["query"]}],
          user_id="wind_waker_player",
          metadata={
              "game": "wind_waker",
              "timestamp": str(context["timestamp"])
          }
      )
      print(f"💾 Stored user query: {context['query'][:50]}...")
    except Exception as e:
      print(f"⚠️  Failed to store memory: {e}")

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
      print(
          "Make sure you have audio devices available and portaudio installed"
      )
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
        data = await asyncio.to_thread(
            self.audio_stream.read, CHUNK_SIZE, **kwargs
        )
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
      # Suppress all stderr output from the receive loop
      with redirect_stderr(io.StringIO()):
        turn = self.session.receive()
        async for response in turn:
          # Only log responses with actual interesting content
          has_interesting_content = False
        
          # Check if this has executable code or code results
          if response.server_content is not None:
            model_turn = response.server_content.model_turn
            if model_turn and model_turn.parts:
              for part in model_turn.parts:
                if part.executable_code or part.code_execution_result:
                  has_interesting_content = True
                  break
          
          # Or if it has tool calls
          if response.tool_call is not None:
            has_interesting_content = True
          
          # Or if it has actual text (not just audio)
          if hasattr(response, 'text') and response.text:
            has_interesting_content = True
          
          if has_interesting_content:
            print(
                f"\n📊 [{datetime.now().strftime('%H:%M:%S')}] Response type:"
                f" {type(response)}"
            )

          # Suppress warnings when accessing response attributes
          with redirect_stderr(io.StringIO()):
            # Check for text (might exist even in audio mode?)
            if hasattr(response, "text") and response.text:
              print(f"📝 TEXT FOUND: {response.text}")
              print(f"🤖 Gemini: {response.text}", end="")
          
          # Check for audio data
          if data := response.data:
            # Just queue the audio without logging
            self.audio_in_queue.put_nowait(data)
            continue

          # Handle tool calls
          tool_call = response.tool_call
          if tool_call is not None:
            print(f"🔧 Tool call details: {tool_call}")
            await self.handle_tool_call(tool_call)
            continue

          # Handle code execution parts
          server_content = response.server_content
          if server_content is not None:
            print(f"💻 Server content received")
            model_turn = server_content.model_turn
            if model_turn:
              print(
                  "   Model turn parts:"
                  f" {len(model_turn.parts) if model_turn.parts else 0}"
              )
              for part in model_turn.parts:
                if part.executable_code:
                  code = part.executable_code.code
                  print(f"🧠 Gemini thinking: {code}")
                  # Extract user intent from the code
                  if "query=" in code:
                    query_start = code.find('query="') + 7
                    query_end = code.find('"', query_start)
                    if query_end > query_start:
                      user_query = code[query_start:query_end]
                      self.conversation_context.append({
                          "type": "user_intent",
                          "query": user_query,
                          "timestamp": datetime.now(),
                      })
                if part.code_execution_result:
                  print(f"💭 Result: {part.code_execution_result.output}")
                  
                  # Store user query in memory asynchronously
                  if self.memory_client and self.conversation_context:
                    latest_context = self.conversation_context[-1]
                    if latest_context.get("query"):
                      # Fire and forget - don't await
                      asyncio.create_task(self._store_memory_async(latest_context))
            # Don't continue here - let audio processing happen
          
          # When we have interesting content, log available attributes
          elif has_interesting_content and not (response.data or response.tool_call or response.server_content):
            attrs = [attr for attr in dir(response) if not attr.startswith('_') and attr not in ['data', 'text', 'tool_call', 'server_content']]
            if attrs:
              print(f"   Other attrs: {attrs}")

        # Handle interruptions - clear audio queue
        while not self.audio_in_queue.empty():
          self.audio_in_queue.get_nowait()

  async def handle_tool_call(self, tool_call):
    """Handle tool calls from Gemini"""
    function_responses = []

    for fc in tool_call.function_calls:
      print(f"\n🔧 Tool call: {fc.name}")
      print(f"   Args: {fc.args}")

      if fc.name == "see_game_screen":
        print("📸 Seeing game screen...")
        screenshot_data = self.take_screenshot()

        if screenshot_data:
          user_query = fc.args.get("query", "")
          vision_analysis = self.analyze_screenshot_with_gemini(
              screenshot_data, user_query
          )
          result = {
              "user_query": user_query,
              "vision_analysis": vision_analysis,
              "screenshot_captured": True,
          }

        else:
          result = {
              "user_query": fc.args.get("query", ""),
              "vision_analysis": {"error": "Failed to capture screenshot"},
              "screenshot_captured": False,
          }
      elif fc.name == "search_walkthrough":
        query = fc.args.get("query", "")
        print(f"📚 Searching walkthrough for: {query}")
        search_results = self.search_walkthrough(query)
        result = {"query": query, "results": search_results}

      elif fc.name == "search_user_history":
        query = fc.args.get("query", "").strip()
        print(f"🔍 Searching user history: {'recent activity' if not query else query}")
        history_results = self.search_user_history(query)
        result = {"query": query or "recent_activity", "results": history_results}

      elif fc.name == "play_song":
        song_name = fc.args.get("song_name", "")
        print(f"🎵 Playing {song_name.replace('_', ' ').title()}...")
        result = self.play_song(song_name)

      else:
        result = {"error": f"Unknown function: {fc.name}"}

      function_responses.append(
          types.FunctionResponse(id=fc.id, name=fc.name, response=result)
      )

    # Send tool responses for synchronous tools immediately
    if function_responses:
      await self.session.send_tool_response(
          function_responses=function_responses
      )

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
          model="gemini-2.0-flash-lite",
          contents=[
              types.Part.from_bytes(
                  data=image_bytes, mime_type=screenshot_data["mime_type"]
              ),
              prompt,
          ],
          config=types.GenerateContentConfig(
              response_mime_type="application/json"
          ),
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

  def search_walkthrough(self, query, top_k=3):
    """Search walkthrough using embeddings"""
    try:
      print(f"🔍 Searching walkthrough for: '{query}'")

      # Load embeddings
      with open("walkthrough_embeddings.json", "r") as f:
        embeddings_data = json.load(f)

      print(f"🔍 Loaded {len(embeddings_data)} chunks")

      # Get query embedding
      client = genai.Client()
      query_response = client.models.embed_content(
          model="gemini-embedding-001",
          contents=query,
          config=types.EmbedContentConfig(task_type="retrieval_query"),
      )
      query_embedding = query_response.embeddings[0].values

      # Calculate similarities
      similarities = []
      for item in embeddings_data:
        similarity = np.dot(query_embedding, item["embedding"])
        similarities.append((similarity, item["text"], item["chunk_id"]))

      # Get top results
      similarities.sort(reverse=True)
      results = []
      for i in range(min(top_k, len(similarities))):
        score, text, chunk_id = similarities[i]
        print(f"🔍 Match {i+1}: chunk {chunk_id}, score {score:.3f}")
        results.append(text)

      return "\n\n---\n\n".join(results)

    except Exception as e:
      print(f"🔍 Walkthrough search error: {e}")
      traceback.print_exc()
      return f"Search failed: {e}"

  def search_user_history(self, query="", max_recent=10):
    """Search user's gameplay history or get recent memories"""
    if not self.memory_client:
      return "Memory system not available"
    
    try:
      if query:
        # Use semantic search for specific queries
        memories = self.memory_client.search(
            query=query,
            user_id="wind_waker_player",
            limit=5
        )
        print(f"💭 Found {len(memories) if memories else 0} relevant memories")
      else:
        # Get recent memories when no query
        memories = self.memory_client.get_all(
            filters={
                "user_id": "wind_waker_player"
            },
            page_size=max_recent,
            version="v2"
        )
        print(f"💭 Retrieved {len(memories) if memories else 0} recent memories")
      
      # Format memories chronologically
      if memories and isinstance(memories, list):
        history_items = []
        for m in memories:
          if isinstance(m, dict) and m.get("memory"):
            timestamp = "unknown"
            if m.get("metadata"):
              timestamp = m["metadata"].get("timestamp", "unknown")
            elif m.get("created_at"):
              timestamp = m["created_at"]
            
            history_items.append(f"[{timestamp}] {m['memory']}")
        
        # Sort by timestamp if we have them
        if history_items:
          history_items.sort()  # Assuming ISO format timestamps
          return "\n".join(history_items)
      
      return "No user history found"
      
    except Exception as e:
      print(f"⚠️  User history search failed: {e}")
      return f"Failed to retrieve history: {str(e)}"

  def play_song(self, song_name):
    """Play a Wind Waker song by name"""
    
    # Define all Wind Waker songs with their controller sequences
    songs = {
        "winds_requiem": {
            "sequence": "Up → Left → Right",
            "description": "Changes wind direction",
            "commands": [
                # Beat reset: Quick 4/4 → 3/4 transition
                {'type': 'axis', 'axis': 'STICK_X', 'value': 0, 'delay': 0.1},    # Left (4/4)
                {'type': 'axis', 'axis': 'STICK_X', 'value': 128, 'delay': 0.2},  # Back to center
                
                # Wind's Requiem: Up → Left → Right (60 BPM = 1 second per beat)
                # Up - hold for 1 beat
                {'type': 'axis', 'axis': 'C_Y', 'value': 0, 'delay': 1.0},    # Push Up and hold for 1 second
                {'type': 'axis', 'axis': 'C_Y', 'value': 128},                # Return to center instantly
                
                # Left - hold for 1 beat
                {'type': 'axis', 'axis': 'C_X', 'value': 0, 'delay': 1.0},    # Push Left and hold for 1 second
                {'type': 'axis', 'axis': 'C_X', 'value': 128},                # Return to center instantly
                
                # Right - hold for 1 beat
                {'type': 'axis', 'axis': 'C_X', 'value': 255, 'delay': 1.0},  # Push Right and hold for 1 second
                {'type': 'axis', 'axis': 'C_X', 'value': 128},                # Return to center instantly
            ]
        },
        "ballad_of_gales": {
            "sequence": "Down → Right → Left → Up",
            "description": "Warps to cyclone locations",
            "commands": [
                # No reset needed - already 4/4 time
                # Small initial pause
                {'type': 'axis', 'axis': 'C_X', 'value': 128},
                {'type': 'axis', 'axis': 'C_Y', 'value': 128, 'delay': 0.3},
                
                # Ballad of Gales: Down → Right → Left → Up
                # Down
                {'type': 'axis', 'axis': 'C_Y', 'value': 255, 'delay': 0.4},  # Push Down
                {'type': 'axis', 'axis': 'C_Y', 'value': 128, 'delay': 0.6},  # Return to center
                
                # Right
                {'type': 'axis', 'axis': 'C_X', 'value': 255, 'delay': 0.4},  # Push Right
                {'type': 'axis', 'axis': 'C_X', 'value': 128, 'delay': 0.6},  # Return to center
                
                # Left
                {'type': 'axis', 'axis': 'C_X', 'value': 0, 'delay': 0.4},    # Push Left
                {'type': 'axis', 'axis': 'C_X', 'value': 128, 'delay': 0.6},  # Return to center
                
                # Up
                {'type': 'axis', 'axis': 'C_Y', 'value': 0, 'delay': 0.4},    # Push Up
                {'type': 'axis', 'axis': 'C_Y', 'value': 128, 'delay': 0.6},  # Return to center
            ]
        },
        "command_melody": {
            "sequence": "Left → Center → Right → Center",
            "description": "Controls statues and companions",
            "commands": [
                # No reset needed - already 4/4 time
                # Small initial pause
                {'type': 'axis', 'axis': 'C_X', 'value': 128},
                {'type': 'axis', 'axis': 'C_Y', 'value': 128, 'delay': 0.3},
                
                # Command Melody: Left → Center → Right → Center
                # Left
                {'type': 'axis', 'axis': 'C_X', 'value': 0, 'delay': 0.4},    # Push Left
                {'type': 'axis', 'axis': 'C_X', 'value': 128, 'delay': 0.6},  # Return to center
                
                # Right (Center is implicit in the return)
                {'type': 'axis', 'axis': 'C_X', 'value': 255, 'delay': 0.4},  # Push Right
                {'type': 'axis', 'axis': 'C_X', 'value': 128, 'delay': 0.6},  # Return to center (final center)
            ]
        },
        "earth_gods_lyric": {
            "sequence": "Down → Down → Center → Right → Left → Center",
            "description": "Awakens the Earth Sage",
            "commands": [
                {'type': 'axis', 'axis': 'STICK_Y', 'value': 255},  # Down
                {'type': 'axis', 'axis': 'STICK_Y', 'value': 128, 'delay': 0.3},
                {'type': 'axis', 'axis': 'STICK_Y', 'value': 255},  # Down
                {'type': 'axis', 'axis': 'STICK_Y', 'value': 128, 'delay': 0.3},  # Center
                {'type': 'axis', 'axis': 'STICK_X', 'value': 255},  # Right
                {'type': 'axis', 'axis': 'STICK_X', 'value': 128, 'delay': 0.3},
                {'type': 'axis', 'axis': 'STICK_X', 'value': 0},  # Left
                {'type': 'axis', 'axis': 'STICK_X', 'value': 128, 'delay': 0.3},  # Center
            ]
        },
        "wind_gods_aria": {
            "sequence": "Up → Up → Down → Right → Left → Right",
            "description": "Awakens the Wind Sage",
            "commands": [
                {'type': 'axis', 'axis': 'STICK_Y', 'value': 0},  # Up
                {'type': 'axis', 'axis': 'STICK_Y', 'value': 128, 'delay': 0.3},
                {'type': 'axis', 'axis': 'STICK_Y', 'value': 0},  # Up
                {'type': 'axis', 'axis': 'STICK_Y', 'value': 128, 'delay': 0.3},
                {'type': 'axis', 'axis': 'STICK_Y', 'value': 255},  # Down
                {'type': 'axis', 'axis': 'STICK_Y', 'value': 128, 'delay': 0.3},
                {'type': 'axis', 'axis': 'STICK_X', 'value': 255},  # Right
                {'type': 'axis', 'axis': 'STICK_X', 'value': 128, 'delay': 0.3},
                {'type': 'axis', 'axis': 'STICK_X', 'value': 0},  # Left
                {'type': 'axis', 'axis': 'STICK_X', 'value': 128, 'delay': 0.3},
                {'type': 'axis', 'axis': 'STICK_X', 'value': 255},  # Right
                {'type': 'axis', 'axis': 'STICK_X', 'value': 128, 'delay': 0.3},
            ]
        },
        "song_of_passing": {
            "sequence": "Right → Left → Down",
            "description": "Changes day to night and vice versa",
            "commands": [
                {'type': 'axis', 'axis': 'STICK_X', 'value': 255},  # Right
                {'type': 'axis', 'axis': 'STICK_X', 'value': 128, 'delay': 0.3},
                {'type': 'axis', 'axis': 'STICK_X', 'value': 0},  # Left
                {'type': 'axis', 'axis': 'STICK_X', 'value': 128, 'delay': 0.3},
                {'type': 'axis', 'axis': 'STICK_Y', 'value': 255},  # Down
                {'type': 'axis', 'axis': 'STICK_Y', 'value': 128, 'delay': 0.3},
            ]
        }
    }
    
    if song_name not in songs:
        return {
            "success": False,
            "message": f"Unknown song: {song_name}",
            "available_songs": list(songs.keys())
        }
    
    song_info = songs[song_name]
    success = send_controller_sequence(song_info["commands"])
    
    if success:
        return {
            "success": True,
            "message": f"Playing {song_name.replace('_', ' ').title()}! {song_info['description']}.",
            "sequence": song_info["sequence"]
        }
    else:
        return {
            "success": False,
            "message": "Failed to send controller commands. Is the controller daemon running?",
            "hint": "Run: sudo python controller_daemon.py"
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
      img = PIL.Image.frombytes(
          "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
      )
      img = img.resize(
          (1024, int(1024 * img.size[1] / img.size[0])),
          PIL.Image.Resampling.LANCZOS,
      )
      print(f"📷 Image resized to: {img.size}")

      # Convert to base64 JPEG
      image_io = io.BytesIO()
      img.save(image_io, format="jpeg")
      image_io.seek(0)

      image_bytes = image_io.read()
      print(f"📷 Screenshot converted to {len(image_bytes)} bytes")
      return {
          "mime_type": "image/jpeg",
          "data": base64.b64encode(image_bytes).decode(),
      }
    except Exception as e:
      print(f"📸 Screenshot error: {e}")
      return None

  async def play_audio(self):
    """Play audio with pre-buffering"""
    # Wait for initial buffer
    initial_chunks = []
    for _ in range(3):  # Buffer 3 chunks before starting
      chunk = await self.audio_in_queue.get()
      initial_chunks.append(chunk)

    stream = await asyncio.to_thread(
        self.pya.open,
        format=FORMAT,
        channels=CHANNELS,
        rate=RECEIVE_SAMPLE_RATE,
        output=True,
        frames_per_buffer=CHUNK_SIZE * 2,  # Larger internal buffer
    )

    # Play buffered chunks first
    for chunk in initial_chunks:
      await asyncio.to_thread(stream.write, chunk)

    # Continue normal playback
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
