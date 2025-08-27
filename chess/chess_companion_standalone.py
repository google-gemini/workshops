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

"""Standalone Chess Companion - Simplified current board analysis

Simplified from TV companion architecture for chess-specific analysis:
- Board change detection via consensus vision
- Current position analysis (no complex queuing)
- Vector search through historical games database
- Expert chess commentary via Gemini Live
"""

import argparse
import asyncio
import base64
from datetime import datetime
import io
import json
import os
from pathlib import Path
import queue
import sys
import tempfile
import time
import traceback
from typing import Dict, List, Optional

import chess
import chess.engine
# Import chess-specific components  
from chess_analyzer import ChessAnalyzer
from roboflow import roboflow_piece_detection as consensus_piece_detection
from tv_controller import ChessTVController
import cv2
from scenedetection import ChessSceneDetector
from google import genai
from google.cloud import speech
from google.genai import types
from mem0 import MemoryClient
import numpy as np
from PIL import Image
import pyaudio
from stockfish_pool import StockfishEnginePool, create_quick_analysis_pool
from vector_search import ChessVectorSearch, SearchResult


def parse_args():
  parser = argparse.ArgumentParser(
      description="Chess Companion with simplified board analysis"
  )
  parser.add_argument(
      "--debug",
      action="store_true",
      help="Save debug images (HDMI captures and crops)",
  )
  parser.add_argument(
      "--no-watch",
      action="store_true",
      help="Start with watching mode OFF (manual queries only)",
  )
  return parser.parse_args()


if sys.version_info < (3, 11, 0):
  import exceptiongroup
  import taskgroup

  asyncio.TaskGroup = taskgroup.TaskGroup
  asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

# HDMI capture device settings
HDMI_VIDEO_DEVICE = "/dev/video11"
HDMI_AUDIO_TARGET = "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo"

MODEL = "gemini-2.5-flash-preview-native-audio-dialog"

# Chess companion configuration
CHESS_CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": (
        """You are an expert chess companion with deep knowledge of chess theory, tactics, strategy, and chess history.

You can provide insightful commentary AND control the TV for chess content.

## IMPORTANT: When to Analyze Positions
ALWAYS use the `analyze_current_position` tool when users ask about:
- What should [player] do/play? (e.g. "What should Magnus do?" "What should Alireza play?")
- Current position evaluation (e.g. "How good is this position?" "Who's winning?") 
- Best moves or move suggestions (e.g. "What's the best move?" "Any good moves here?")
- Position-specific questions (e.g. "Is this winning?" "Should White attack?")

Use the `analyze_hypothetical_move` tool for "what if" questions:
- What if Magnus plays Re8? 
- What happens if White castles?
- Is Nf3 a good move here?

Use the `search_related_games` tool to find historical precedent:
- How Magnus and Hikaru handled similar positions  
- Success rates for different strategic approaches
- Common themes and patterns in comparable games
- Historical outcomes to inform current position assessment

Don't give generic chess advice - analyze the actual board position first!

## TV Control Capabilities:
- Play chess content using play_content (for ANY play/watch request: "play it", "watch Magnus vs Hikaru", etc.)
- Pause playback with pause_playback  
- Access user's viewing history with search_user_history
- Toggle watching mode on/off for automatic position commentary

Use `play_content` for ANY content playback request:
- "Play Claude vs Gemini" → Use remembered alias "GUESS THE ELO AI COMPETITION"  
- "Can you play it?" → Use context from recent conversation
- "Watch Magnus vs Hikaru" → Search and play directly

## Chess Commentary Style:
When you receive position analysis packages (from analyze_current_position), provide expert chess commentary that enhances understanding:

Be analytical and educational:
- Explain tactical themes, strategic concepts, and positional ideas
- Compare with similar master games from the historical database
- Point out key moves, blunders, and brilliant combinations  
- Discuss opening theory, middlegame plans, and endgame technique
- Analyze piece activity, king safety, and pawn structure
- Share engine evaluations and best move suggestions
- Ask thought-provoking questions about player intentions
- Connect current position to chess history and famous games

Strike a balance between being informative and conversational - like watching with a chess master who notices details others might miss.

Feel free to suggest chess content to watch or help users find specific games.
"""
    ),
    "tools": [{
        "function_declarations": [
            {
                "name": "analyze_current_position",
                "description": (
                    "Take a fresh screenshot and provide comprehensive analysis"
                    " of the current chess position. Includes engine"
                    " evaluation, strategic themes, similar master games, and"
                    " expert commentary. Use this when user asks questions"
                    " about the current board state."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Optional: User's specific question about the"
                                " position (e.g., 'What should White play?',"
                                " 'Is this winning?', 'Evaluate this position')"
                            ),
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "analyze_hypothetical_move",
                "description": (
                    "Analyze what happens if a specific move is played from"
                    " the current position. Compare the resulting evaluation"
                    " with the current position and explain the consequences."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "move_description": {
                            "type": "string",
                            "description": (
                                "The hypothetical move to analyze (e.g.,"
                                " 'rook to e8', 'takes the pawn on e5',"
                                " 'Nf3', 'castles kingside')"
                            ),
                        }
                    },
                    "required": ["move_description"],
                },
            },
            {
                "name": "play_content",
                "description": (
                    "Play chess content on the TV. Use this for ANY request to play or watch content: "
                    "'play Magnus vs Hikaru', 'can you play it?', 'watch the world championship', etc. "
                    "Automatically handles searching and playing the content."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "What to play - chess game, tournament, players, or content name"
                        }
                    },
                    "required": ["title"],
                },
            },
            {
                "name": "search_user_history",
                "description": (
                    "Search the user's personal viewing history and past chess"
                    " discussions. Use this to recall previous games watched,"
                    " positions analyzed, or questions asked."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Optional: What to search for in chess history"
                                " (e.g., 'Kasparov games', 'tactical puzzles',"
                                " 'endgame positions'). Leave blank to get"
                                " recent activity."
                            ),
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "start_watching_mode",
                "description": (
                    "Start automatically commenting on positions as they change"
                    " during live games"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "stop_watching_mode",
                "description": "Stop automatic position commentary",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "pause_playback",
                "description": (
                    "Pause the currently playing chess content on TV"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "rewind_sequence", 
                "description": "Rewind the current video to review a previous moment (uses the info-rewind-rewind-back sequence)",
                "parameters": {
                    "type": "object", 
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "search_related_games",
                "description": (
                    "Search for similar chess positions from the Nakamura vs Carlsen historical database. "
                    "Find how these masters handled comparable positions, strategic themes, and typical outcomes."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Optional: Specific aspect to focus on (e.g., 'similar pawn structures', "
                                "'tactical themes', 'Magnus in winning positions'). If blank, uses current position."
                            ),
                        },
                        "min_similarity": {
                            "type": "number",
                            "description": "Minimum similarity threshold (0.0-1.0, default 0.75)",
                        },
                        "max_results": {
                            "type": "number",
                            "description": "Maximum results to return (default 5)",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "remember_information", 
                "description": "Store important information for future reference, like content aliases, user preferences, or chess insights",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "information": {
                            "type": "string", 
                            "description": "The information to remember (e.g., 'Claude vs Gemini is actually called GUESS THE ELO AI COMPETITION on YouTube')"
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional: Category like 'content_aliases', 'preferences', 'chess_insights'"
                        }
                    },
                    "required": ["information"]
                }
            },
        ]
    }],
}


class TVAudioStream:
  """Captures TV audio using pw-cat and provides it as a stream for transcription"""

  def __init__(self):
    self._buff = (
        queue.Queue()
    )  # Use sync queue for Google Cloud Speech compatibility
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
    
    # Wait a moment for _feed_buffer to actually start
    await asyncio.sleep(0.5)
    return self

  async def __aexit__(self, type, value, traceback):
    self.closed = True
    if self.audio_process:
      self.audio_process.terminate()
      await self.audio_process.wait()
    self._buff.put(None)  # Signal generator to terminate (sync put)

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

        # Keep milestone logging only
        if chunks_sent % 500 == 0:  # Log every 50 seconds
          print(f"📡 TV Audio: {chunks_sent} chunks processed")

      except Exception as e:
        print(f"❌ Audio feed error: {e}")
        break

  def generator(self):
    """Generator with robust timeout handling"""
    chunks_yielded = 0
    
    while not self.closed:
      try:
        chunk = self._buff.get(timeout=1.0)
        if chunk is None:
          print("📡 Audio generator: received termination signal")
          return
        
        # Reset timeout counter on successful chunk
        consecutive_timeouts = 0
        chunks_yielded += 1
        
        # Remove noisy logging - only log major milestones
        if chunks_yielded % 500 == 0:  # Log every 50 seconds instead
          print(f"📡 Audio generator: {chunks_yielded} chunks yielded")
        
        yield chunk
        
      except queue.Empty:
        # Normal silence - just continue waiting (no error counting)
        continue
      except Exception as e:
        # Actual error - log it but keep trying
        print(f"❌ Audio generator error: {e}")
        continue


class ChessCompanionSimplified:
  """Simplified Chess Companion - Current board analysis only"""

  def __init__(self, debug_mode=False, watching_mode=True):
    # Core state - just current board and analysis
    self.current_board = None
    self.current_analysis = None  # Current analysis with both perspectives
    self.analyzing = False
    self.commentary_buffer = []  # Recent commentary for current board

    # Watching mode - configurable
    self.watching_mode = watching_mode

    # Scene detection and bounding box caching
    self.current_board_mask = None  # Cached board bounding box
    self.scene_detector = None
    self.scene_detection_task = None
    self.board_mask_last_updated = None

    # Verify Roboflow API key for vision pipeline
    if not os.getenv("ROBOFLOW_API_KEY"):
      raise ValueError("ROBOFLOW_API_KEY environment variable required for vision pipeline")

    # Debug setup
    self.debug_mode = debug_mode
    if self.debug_mode:
      self.debug_dir = Path("debug_chess_frames")
      self.debug_dir.mkdir(exist_ok=True)
      print(f"🐛 Debug mode: saving frames to {self.debug_dir}")

    # Gemini client and session
    self.client = genai.Client()
    self.session = None
    self.audio_in_queue = None

    # Chess analysis components
    self.vector_search = ChessVectorSearch("nakamura_carlsen_embeddings.json")
    self.engine_pool = create_quick_analysis_pool(pool_size=4)
    self.analyzer = ChessAnalyzer(self.vector_search, self.engine_pool, self.client)
    
    # Fresh analysis task tracking
    self.fresh_analysis_task = None
    self.pending_user_query = None
    
    # Cached player colors (set once during initialization)
    self.cached_player_colors = None

    # Audio components
    self.pya = None
    self.mic_stream = None
    self.shared_cap = None

    # Memory and speech
    self.memory_client = self._init_memory_client()
    self.speech_client = speech.SpeechClient()
    
    # TV Controller
    self.tv_controller = ChessTVController(memory_client=self.memory_client)
    print("📺 TV Controller integrated")
    self.speech_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SEND_SAMPLE_RATE,
        language_code="en-US",
        max_alternatives=1,
    )
    self.streaming_config = speech.StreamingRecognitionConfig(
        config=self.speech_config, interim_results=True
    )

    print("♟️  Chess Companion (Simplified) initialized")
    print(f"👁️  Watching mode: {'ON' if self.watching_mode else 'OFF'}")
    print("📊 Vector search ready with chess games database")
    print("🔧 Stockfish engine pool ready for analysis")

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
          project_id="proj_LJWUhnYLUYsJzLVx4U7buckvgXmDyBQoA6758PQM",
      )
      print("✓ Episodic memory initialized")
      return client
    except Exception as e:
      print(f"⚠️  Failed to initialize memory: {e}")
      return None

  def find_pulse_device(self):
    """Find a PulseAudio device that works with PipeWire"""
    for i in range(self.pya.get_device_count()):
      info = self.pya.get_device_info_by_index(i)
      if "pulse" in info["name"].lower() and info["maxInputChannels"] > 0:
        return info
    return self.pya.get_default_input_device_info()

  async def send_text(self):
    """Allow user to send text messages"""
    while True:
      text = await asyncio.to_thread(input, "message > ")
      if text.lower() == "q":
        break
      await self.session.send_realtime_input(text=text or ".")

  def _convert_frame_to_base64(self, frame_img):
    """Convert OpenCV frame to base64 format for Gemini"""
    try:
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

  async def detect_initial_board_mask(self):
    """Detect initial board location on startup - no scene change needed"""
    print("🎯 Detecting initial board location...")
    
    # Initialize video capture
    self.shared_cap = cv2.VideoCapture(HDMI_VIDEO_DEVICE)
    if not self.shared_cap.isOpened():
      print(f"❌ Cannot open HDMI video device {HDMI_VIDEO_DEVICE}")
      return

    self.shared_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    self.shared_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    print("✅ HDMI capture ready")
    
    ret, frame = self.shared_cap.read()
    if ret:
      await self.update_board_mask(frame)
      print("✅ Initial board mask detected")
    else:
      print("❌ Failed to capture initial frame for board detection")

  async def start_scene_detection(self):
    """Start background scene detection for board mask updates"""
    print("🎬 Starting background scene detection...")
    
    if not self.shared_cap or not self.shared_cap.isOpened():
      print("❌ Video capture not ready for scene detection")
      return
    
    # Initialize scene detector
    debug_dir = str(self.debug_dir) if self.debug_mode else None
    self.scene_detector = ChessSceneDetector(debug_dir=debug_dir)
    
    # Define callback for scene changes
    async def on_scene_change(frame):
      print("🎬 Scene change detected - updating board mask only")
      asyncio.create_task(self.update_board_mask(frame))
    
    # Start detection
    await self.scene_detector.start_detection(self.shared_cap, on_scene_change)

  async def fast_fen_detection_loop(self):
    """Fast FEN detection using cached board mask"""
    print("♟️ Starting fast FEN detection loop...")
    
    detection_count = 0
    
    while True:
      try:
        if self.current_board_mask is None:
          print("⏳ Waiting for board mask...")
          await asyncio.sleep(2)
          continue
        
        detection_count += 1
        ret, frame = self.shared_cap.read()
        
        if not ret:
          print("⚠️  Failed to capture frame for FEN detection")
          await asyncio.sleep(2)
          continue

        # Use cached mask for fast FEN extraction
        new_fen = await self.extract_fen_with_cached_mask(frame)
        
        if new_fen and self.is_valid_fen(new_fen):
          if new_fen != self.current_board:
            print(f"🆕 Position change detected #{detection_count}: {new_fen[:30]}...")
            await self.on_board_change(new_fen, frame)
          else:
            if detection_count % 6 == 0:  # Log every 30 seconds (6 * 5s)
              print(f"📍 Position stable #{detection_count}: {new_fen[:30]}...")
        else:
          print(f"❌ Invalid/no FEN detected #{detection_count}")
        
        await asyncio.sleep(5)  # Check every 5 seconds - much faster than 30s
        
      except Exception as e:
        print(f"❌ Fast FEN detection error: {e}")
        traceback.print_exc()
        await asyncio.sleep(5)

  async def update_board_mask(self, frame):
    """Update cached board bounding box from scene change"""
    try:
      print("📐 Updating board bounding box...")
      start_time = time.time()
      
      # Step 1: Fresh screenshot → 1024x1024 (for segmentation)
      ret, screenshot = self.shared_cap.read()
      if not ret:
        print("❌ Failed to capture screenshot for board mask")
        return
      
      # Keep full resolution for higher quality
      screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
      pil_screenshot = Image.fromarray(screenshot_rgb)
      original_size = pil_screenshot.size
      
      print(f"📐 Screenshot: {screenshot.shape[:2]} → full resolution for segmentation")
      
      # Step 2: Segment to get bounding box (on full resolution)
      from roboflow import ChessVisionPipeline
      pipeline = ChessVisionPipeline(debug_dir=str(self.debug_dir) if self.debug_mode else None)
      
      segmentation_result = await asyncio.to_thread(
          pipeline.segment_board_direct, pil_screenshot
      )
      
      if segmentation_result.get("predictions"):
        bbox = pipeline.extract_bbox_from_segmentation(segmentation_result)
        
        if bbox:
          # Convert absolute coordinates to relative coordinates (0.0-1.0)
          abs_coords = bbox["coords"]  # (x_min, y_min, x_max, y_max) in full resolution
          rel_coords = (
            abs_coords[0] / original_size[0],  # x_min relative
            abs_coords[1] / original_size[1],  # y_min relative  
            abs_coords[2] / original_size[0],  # x_max relative
            abs_coords[3] / original_size[1]   # y_max relative
          )
          
          # Cache bbox as relative coordinates
          self.current_board_mask = {
            "bbox_relative": rel_coords,  # Relative coordinates (0.0-1.0)
            "confidence": bbox["confidence"], 
            "timestamp": start_time,
            "original_size": original_size  # For debugging
          }
          print(f"✅ Board mask cached (relative): {rel_coords}, confidence={bbox['confidence']:.3f}")
        else:
          print("❌ No valid bounding box extracted")
          self.current_board_mask = None
      else:
        print("❌ Board segmentation found no predictions")
        self.current_board_mask = None
      
      elapsed = time.time() - start_time
      print(f"✅ Board mask update complete in {elapsed:.1f}s")
      
    except Exception as e:
      print(f"❌ Board mask update failed: {e}")
      traceback.print_exc()
      self.current_board_mask = None

  async def extract_fen_with_cached_mask(self, frame):
    """Fast FEN extraction using cached board bounding box"""
    try:
      if not self.current_board_mask or "bbox_relative" not in self.current_board_mask:
        print("⚠️  No cached board mask - falling back")
        return await self._fallback_full_detection(frame)
      
      # Step 1: Keep screenshot at full resolution
      screenshot_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      pil_screenshot = Image.fromarray(screenshot_rgb)
      current_size = pil_screenshot.size
      
      # Step 2: Crop using relative bbox coordinates
      rel_bbox = self.current_board_mask["bbox_relative"]  # (x_min, y_min, x_max, y_max) in 0.0-1.0
      abs_bbox = (
        int(rel_bbox[0] * current_size[0]),  # x_min
        int(rel_bbox[1] * current_size[1]),  # y_min
        int(rel_bbox[2] * current_size[0]),  # x_max  
        int(rel_bbox[3] * current_size[1])   # y_max
      )
      pil_crop = pil_screenshot.crop(abs_bbox)
      
      if pil_crop.size[0] == 0 or pil_crop.size[1] == 0:
        print("❌ Empty crop from cached bbox - falling back")
        return await self._fallback_full_detection(frame)
      
      print(f"🚀 Cached crop path: {frame.shape[:2]} → crop ({pil_crop.size}) → centralized detection")
      
      # Step 3: Use centralized roboflow detection with pre-cropped board
      from roboflow import roboflow_piece_detection
      
      result = await roboflow_piece_detection(
          pil_crop,  # Pass PIL crop directly
          debug_dir=str(self.debug_dir) if self.debug_mode else None,
          skip_segmentation=True  # Skip segmentation, we already have the crop
      )
      
      if not result or not result.get("consensus_fen"):
        print("❌ Cached crop detection failed - falling back")
        return await self._fallback_full_detection(frame)
      
      fen = result["consensus_fen"]
      piece_count = result.get("piece_count", 0)
      
      if fen == "8/8/8/8/8/8/8/8":
        print(f"❌ Empty board FEN from {piece_count} pieces")
        return None
      
      print(f"🚀 Cached crop FEN: {piece_count} pieces → {fen[:20]}...")
      return fen
      
    except Exception as e:
      print(f"❌ Fast FEN extraction failed: {e}")
      return await self._fallback_full_detection(frame)

  async def _fallback_full_detection(self, frame):
    """Fallback to full consensus detection when cached approach fails"""
    print("🔄 Fallback: Running full consensus detection...")
    try:
      temp_path = await self.save_frame_to_temp(frame)
      
      result = await consensus_piece_detection(
          temp_path,
          debug_dir=str(self.debug_dir) if self.debug_mode else None,
          skip_segmentation=False  # Full detection for fallback
      )
      
      piece_count = result.get("piece_count", 0)
      if piece_count < 2:
        print(f"❌ Fallback: Only {piece_count} pieces detected")
        os.unlink(temp_path)
        return None
      
      new_fen = result["consensus_fen"]
      os.unlink(temp_path)
      
      if new_fen == "8/8/8/8/8/8/8/8":
        print(f"❌ Fallback: Empty board FEN despite {piece_count} pieces")
        return None
      
      print(f"🔄 Fallback detection complete: {new_fen[:20]}...")
      return new_fen
      
    except Exception as e:
      print(f"❌ Fallback detection failed: {e}")
      return None

  async def on_board_change(self, new_fen: str, frame):
    """Handle new board position detected"""
    print(f"🎯 Board changed from {self.current_board} to {new_fen}")

    # Show visual representation of the new position
    self._show_board_visualization(new_fen)

    # Update current state - keep commentary buffer for continuous narrative
    self.current_board = new_fen
    # Don't clear commentary_buffer - commentary flows across positions

    # Start analysis (don't wait for it)
    if not self.analyzing:
      asyncio.create_task(self.analyze_new_position(new_fen, frame))

  async def analyze_new_position(self, fen: str, frame=None):
    """Analyze new position using both perspectives"""
    if self.analyzing:
      return

    self.analyzing = True
    try:
      print(f"🧠 Analyzing new position with both perspectives: {fen[:30]}...")
      
      # Use analyzer to get both perspectives
      analyses = await self.analyzer.analyze_both_perspectives(
          fen=fen,
          frame=None,
          commentary_context=self.commentary_buffer
      )
      
      # Update current analysis (overwrite)
      self.current_analysis = analyses
      print(f"✅ Current analysis updated for {fen[:30]}...")
      
      # Auto-send if watching mode (default to white perspective)
      if self.watching_mode:
        await self.send_analysis_to_gemini(analyses["white"])
        
    except Exception as e:
      print(f"❌ Analysis error: {e}")
      traceback.print_exc()
    finally:
      self.analyzing = False

  async def send_analysis_to_gemini(self, analysis):
    """Send analysis to Gemini Live for commentary"""
    try:
      # Use pre-formatted analysis text
      analysis_text = analysis.get("formatted_for_gemini", "Analysis unavailable")

      # Show what we're sending to Gemini
      print(f"\n📤 SENDING TO GEMINI:")
      print("=" * 50)
      print(analysis_text)
      print("=" * 50)

      # Build content parts - always include text analysis
      parts = [{"text": analysis_text}]

      # Add screenshot if available
      screenshot = analysis.get("board_screenshot")
      if screenshot:
        parts.append({
            "inline_data": {
                "mime_type": screenshot["mime_type"],
                "data": screenshot["data"],
            }
        })
        print(f"📸 Including screenshot with analysis")

      content = {"role": "user", "parts": parts}
      await self.session.send_client_content(turns=content, turn_complete=True)
      print(f"✅ Sent analysis to Gemini (watching mode) - {len(parts)} parts")

    except Exception as e:
      print(f"❌ Failed to send analysis: {e}")


  def is_valid_fen(self, fen: str) -> bool:
    """Check if a string is a valid FEN"""
    try:
      chess.Board(fen)
      return True
    except (ValueError, TypeError):
      return False

  def _show_board_visualization(self, fen: str):
    """Show visual 8x8 board representation"""
    try:
      board = chess.Board(f"{fen} w KQkq - 0 1")
      
      print(f"📋 8x8 BOARD VISUALIZATION:")
      print("   a b c d e f g h")
      for rank in range(8, 0, -1):  # 8 down to 1
        pieces_row = []
        for file in range(8):  # a to h
          square = chess.square(file, rank - 1)
          piece = board.piece_at(square)
          if piece:
            pieces_row.append(piece.symbol())
          else:
            pieces_row.append(".")
        print(f"{rank}: {' '.join(pieces_row)}")
    except Exception as e:
      print(f"⚠️ Board visualization failed: {e}")

  def _format_related_games_report(self, results: list, query: str) -> str:
    """Format search results into a digestible narrative report for Gemini"""
    if not results:
      return "No similar games found in the database."
    
    # Summary statistics
    total = len(results)
    sim_range = f"{min(r['similarity'] for r in results):.2f}-{max(r['similarity'] for r in results):.2f}"
    
    # Count outcomes
    white_wins = sum(1 for r in results if r["result"] == "1-0")
    black_wins = sum(1 for r in results if r["result"] == "0-1") 
    draws = sum(1 for r in results if r["result"] == "1/2-1/2")
    
    # Most similar game (first result)
    top_game = results[0]
    
    # Build narrative report
    report = f"""🔍 RELATED GAMES ANALYSIS
Query: {query}
Found {total} similar positions (similarity range: {sim_range})

📊 HISTORICAL OUTCOMES:
• White wins: {white_wins}
• Black wins: {black_wins}  
• Draws: {draws}

🎯 MOST SIMILAR GAME ({top_game['similarity']:.3f} similarity):
{top_game['players']} → {top_game['result']}
{top_game['event']} ({top_game['date']})

Position Context: "{top_game['position_description'][:200]}{'...' if len(top_game['position_description']) > 200 else ''}"

Engine Assessment: {top_game['engine_evaluation']} (evaluation)
Recommended Move: {top_game['best_move'] or 'Not available'}
Strategic Focus: {', '.join(top_game['strategic_themes'][:3]) if top_game['strategic_themes'] else 'General position'}
Critical Squares: {', '.join(top_game['key_squares'][:3]) if top_game['key_squares'] else 'Various'}"""

    # Add pattern analysis if we have multiple games
    if len(results) >= 2:
      # Success rate analysis
      known_results = [r for r in results if r["result"] != "Unknown"]
      if known_results:
        decisive_games = len([r for r in known_results if r["result"] != "1/2-1/2"])
        if decisive_games > 0:
          success_rate = (decisive_games / len(known_results)) * 100
          report += f"\n\n🎯 POSITION TYPE ANALYSIS:\nDecisive result rate: {success_rate:.0f}% ({decisive_games}/{len(known_results)} games)."

    # Add second-best game for additional context if available
    if len(results) >= 2:
      second_game = results[1]
      report += f"\n\n🔍 ALSO RELEVANT ({second_game['similarity']:.3f} similarity):\n{second_game['players']} → {second_game['result']} ({second_game['event']})"
    
    return report
  

  async def save_frame_to_temp(self, frame) -> str:
    """Save video frame to temporary file for vision analysis"""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
      temp_path = temp_file.name

    # Convert frame and save - normalize before vision analysis
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img.thumbnail(
        (1024, 1024), Image.LANCZOS
    )  # Normalize for better vision results
    img.save(temp_path)

    return temp_path




  async def listen_user_audio(self):
    """Capture audio from user microphone for questions"""
    try:
      self.pya = pyaudio.PyAudio()
      mic_info = self.find_pulse_device()
      print(f"🎤 Using user microphone: {mic_info['name']}")

      self.mic_stream = await asyncio.to_thread(
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
            self.mic_stream.read, CHUNK_SIZE, **kwargs
        )
        # Send directly to Gemini Live for user questions
        await self.session.send_realtime_input(
            audio={"data": data, "mime_type": "audio/pcm"}
        )

    except Exception as e:
      print(f"❌ User audio capture error: {e}")
      raise

  async def transcribe_tv_audio(self):
    """Auto-restart transcription on failures with exponential backoff"""
    print("🎤 Starting TV audio transcription with auto-restart...")
    
    restart_count = 0
    max_restarts = 10
    
    while restart_count < max_restarts:
      try:
        print(f"🎤 Creating audio stream (attempt #{restart_count + 1})...")
        async with TVAudioStream() as stream:
          print("🎤 Audio stream created, starting transcription...")
          
          # Run transcription in a separate thread to avoid blocking
          await asyncio.to_thread(self._run_transcription_sync, stream)
          
          # If we get here, transcription ended normally - reset restart count
          restart_count = 0
          print("🎤 Transcription ended normally, restarting...")
          await asyncio.sleep(1)
          
      except Exception as e:
        restart_count += 1
        wait_time = min(restart_count * 2, 10)  # Exponential backoff, max 10s
        print(f"❌ Transcription failed (attempt {restart_count}/{max_restarts}): {e}")
        
        if restart_count < max_restarts:
          print(f"🔄 Restarting in {wait_time}s...")
          await asyncio.sleep(wait_time)
        else:
          print("🚫 Max transcription restart attempts reached - disabling TV audio")
          break

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

      # Only process final results to avoid spam
      if result.is_final and transcript.strip():
        transcripts_received += 1
        print(f"📝 Transcribed #{transcripts_received}: {transcript}")

        # Add to commentary buffer (for current board context)
        self.commentary_buffer.append(transcript)
        # Keep only last 10 commentary lines
        if len(self.commentary_buffer) > 10:
          self.commentary_buffer = self.commentary_buffer[-10:]

        print(
            f"📝 Commentary buffer now has {len(self.commentary_buffer)} items"
        )
        print(f"📝 Latest: {transcript}")

  async def receive_audio(self):
    """Receive Gemini's audio responses and handle tool calls"""
    while True:
      turn = self.session.receive()
      async for response in turn:
        # Audio data - queue immediately
        if data := response.data:
          await self.audio_in_queue.put(data)
          continue

        # Text response
        if text := response.text:
          print(f"♟️  Chess Companion: {text}")
          continue

        # Tool calls
        if response.tool_call:
          await self.handle_tool_call(response.tool_call)
          continue

      # Handle interruptions by clearing audio queue
      while not self.audio_in_queue.empty():
        try:
          self.audio_in_queue.get_nowait()
        except:
          break

  async def handle_tool_call(self, tool_call):
    """Handle tool calls - simplified for current board analysis"""
    function_responses = []

    for fc in tool_call.function_calls:
      print(f"🔧 Tool call: {fc.name}")

      if fc.name == "analyze_current_position":
        user_query = fc.args.get("query", "Analyze the current chess position")
        print(f"🔧 Current position analysis requested: '{user_query}'")

        # Simple: just use current analysis 
        if self.current_analysis:
          print(f"✅ Using current analysis (might be slightly stale)")
          
          # Get FRESH broadcast context instead of using stored
          print("📸 Taking fresh screenshot for broadcast context...")
          ret, frame = self.shared_cap.read()
          fresh_broadcast_context = {}
          if ret:
            fresh_broadcast_context = await self.analyzer._extract_broadcast_context(frame)
          
          # Determine perspective using FRESH broadcast context
          try:
            color = await self.analyzer.determine_query_perspective(user_query, fresh_broadcast_context)
          except:
            color = "white"
          
          # Use the requested perspective, or fall back to white
          analysis = self.current_analysis.get(color, self.current_analysis.get("white", {}))
          
          if analysis:
            print(f"🎯 Using {color} perspective")
            
            # Update user query context AND fresh broadcast context
            analysis = analysis.copy()
            analysis["user_query"] = user_query
            analysis["broadcast_context"] = fresh_broadcast_context  # USE FRESH CONTEXT
            analysis["formatted_for_gemini"] = self.analyzer._format_for_live_model(analysis)
            
            # Return analysis directly from tool (don't send separately)
            result = {
                "status": "analysis_ready",
                "analysis": analysis.get("formatted_for_gemini", "Analysis unavailable"),
                "query": user_query,
                "perspective": color
            }
            
            print(f"\n🔧 TOOL RESPONSE DEBUG:")
            print("=" * 60)
            print(f"Status: {result['status']}")
            print(f"Query: {result['query']}")
            print(f"Perspective: {result['perspective']}")
            print(f"Analysis length: {len(result.get('analysis', ''))}")
            print("\nFULL ANALYSIS CONTENT:")
            print("-" * 40)
            print(result.get('analysis', 'No analysis content'))
            print("-" * 40)
            print("=" * 60)
          else:
            result = {
                "status": "no_analysis",
                "message": "No analysis available yet. Please wait for position detection.",
            }
        else:
          # No current analysis available
          print(f"📍 No current analysis available")
          result = {
              "status": "no_analysis",
              "message": "No analysis available yet. Please wait for position detection.",
          }

      elif fc.name == "start_watching_mode":
        self.watching_mode = True
        result = {"status": "watching_mode_started"}
        print("👁️ Watching mode ON")

      elif fc.name == "stop_watching_mode":
        self.watching_mode = False
        result = {"status": "watching_mode_stopped"}
        print("👁️ Watching mode OFF")

      elif fc.name == "analyze_hypothetical_move":
        move_description = fc.args.get("move_description", "")
        print(f"🔧 Hypothetical move analysis requested: '{move_description}'")

        if self.current_board and move_description:
          try:
            # Use analyzer for hypothetical move analysis
            hypothetical_result = await self.analyzer.analyze_hypothetical_move(
              current_fen=self.current_board,
              move_description=move_description
            )
            
            result = {
              "status": "hypothetical_analysis_complete",
              "move_description": move_description,
              "analysis": hypothetical_result.get("analysis", "Analysis unavailable"),
              "evaluation_change": hypothetical_result.get("evaluation_change"),
              "new_evaluation": hypothetical_result.get("new_evaluation"),
              "best_move_after": hypothetical_result.get("best_move_after"),
              "principal_variation": hypothetical_result.get("principal_variation", [])
            }
          except Exception as e:
            print(f"❌ Hypothetical analysis failed: {e}")
            result = {
              "status": "analysis_error",
              "error": f"Could not analyze hypothetical move: {str(e)}"
            }
        else:
          result = {
            "status": "no_position",
            "message": "No current position available for hypothetical analysis."
          }

      elif fc.name == "play_content":
        title = fc.args.get("title", "")
        print(f"🎬 TV control: playing '{title}'")
        
        # Fire and forget - don't wait for anything
        self.tv_controller.search_and_play_content(title)
        
        # Store memory in background (don't await)
        if self.memory_client and title.strip():
            asyncio.create_task(self.tv_controller.store_viewing_request(title))
        
        # Quick, conversational response
        result = {
            "status": "starting", 
            "message": f"🎬 Bringing up '{title}'"
        }

      elif fc.name == "search_user_history":
        query = fc.args.get("query", "").strip()
        print(f"🔍 Searching user history: {'recent activity' if not query else query}")
        
        if self.memory_client:
            try:
                if query:
                    memories = await asyncio.to_thread(
                        self.memory_client.search,
                        query=query,
                        user_id="chess_tv_user", 
                        limit=5,
                    )
                else:
                    memories = await asyncio.to_thread(
                        self.memory_client.get_all,
                        filters={"user_id": "chess_tv_user"},
                        page_size=10,
                    )
                
                # Format memories
                if memories:
                    history_items = []
                    for m in memories:
                        if isinstance(m, dict) and m.get("memory"):
                            history_items.append(m["memory"])
                    history_text = "\n".join(history_items)
                else:
                    history_text = "No viewing history found"
                    
            except Exception as e:
                history_text = f"Failed to retrieve history: {str(e)}"
        else:
            history_text = "Memory system not available"
            
        result = {"query": query or "recent_activity", "results": history_text}

      elif fc.name == "pause_playback":
        print("⏸️ Pausing TV playback...")
        pause_result = await self.tv_controller.pause_playback()
        result = {
            "status": "paused" if pause_result else "failed",
            "message": "✅ Paused" if pause_result else "❌ Pause failed"
        }

      elif fc.name == "rewind_sequence":
        print("⏪ Executing rewind sequence...")
        try:
            await self.tv_controller.show_info()
            await asyncio.sleep(1)
            await self.tv_controller.rewind_playback() 
            await asyncio.sleep(1)
            await self.tv_controller.rewind_playback()
            await asyncio.sleep(1) 
            await self.tv_controller.rewind_playback()
            await asyncio.sleep(1) 
            await self.tv_controller.enter_key()
            await asyncio.sleep(1) 
            await self.tv_controller.pause_playback()
            result = {"status": "rewind_complete", "message": "Rewound ~10 seconds and ready for analysis"}
        except Exception as e:
            result = {"status": "rewind_failed", "error": str(e)}

      elif fc.name == "search_related_games":
        query = fc.args.get("query", "").strip()
        min_similarity = fc.args.get("min_similarity", 0.6)
        max_results = int(fc.args.get("max_results", 5))
        
        print(f"🔍 Searching related games: {query or 'current position'}")
        
        # Build query from current position if none provided
        if not query and self.current_board:
          if self.current_analysis:
            # Use enhanced description from current analysis
            white_analysis = self.current_analysis.get("white", {})
            enhanced = white_analysis.get("enhanced_description", {})
            query_parts = []
            if enhanced.get("description"):
              query_parts.append(f"Position: {enhanced['description']}")
            if enhanced.get("strategic_themes"):
              query_parts.append(f"Strategic themes: {', '.join(enhanced['strategic_themes'])}")
            if enhanced.get("tactical_elements"):
              query_parts.append(f"Tactical elements: {', '.join(enhanced['tactical_elements'])}")
            query = " ".join(query_parts) if query_parts else f"Chess position: {self.current_board}"
          else:
            query = f"Chess position: {self.current_board}"
        elif not query:
          query = "tactical chess positions"
        
        try:
          # Use existing vector search
          search_results = await self.vector_search.search(
            query=query,
            top_k=max_results,
            similarity_threshold=min_similarity
          )
          
          # Debug the search result structure
          if search_results:
            print("🔍 DEBUG: Search result structure:")
            first_result = search_results[0]
            print(f"  - Type: {type(first_result)}")
            print(f"  - Attributes: {dir(first_result)}")
            print(f"  - Metadata keys: {first_result.metadata.keys() if hasattr(first_result, 'metadata') else 'No metadata attr'}")
            
            if hasattr(first_result, 'metadata') and 'full_position' in first_result.metadata:
              full_pos = first_result.metadata['full_position']
              print(f"  - full_position keys: {full_pos.keys()}")
              if 'game_context' in full_pos:
                game_context = full_pos['game_context']
                print(f"  - game_context keys: {game_context.keys()}")
                print(f"  - white_player: {game_context.get('white_player', 'NOT FOUND')}")
          
          if search_results:
            # Format results for the model
            formatted_results = []
            for search_result in search_results:
              # Extract from actual SearchResult structure  
              game_info = search_result.metadata  # Game context is directly in metadata
              full_pos = search_result.full_position if hasattr(search_result, 'full_position') else {}
              enhanced = full_pos.get("enhanced_description", {}) if full_pos else {}
              stockfish = full_pos.get("stockfish_analysis", {}) if full_pos else {}
              
              # Get game context from the correct location
              game_context = full_pos.get("game_context", {}) if full_pos else {}
              
              formatted_result = {
                "similarity": round(search_result.similarity, 3),
                "players": f"{game_info.get('white_player', 'Unknown')} vs {game_info.get('black_player', 'Unknown')}",
                "result": game_context.get("result", "Unknown"),
                "date": game_context.get("date", "Unknown"), 
                "event": game_context.get("event", "Unknown"),
                "position_description": enhanced.get("description", ""),
                "strategic_themes": enhanced.get("strategic_themes", []),
                "tactical_elements": enhanced.get("tactical_elements", []),
                "key_squares": enhanced.get("key_squares", []),
                "engine_evaluation": stockfish.get("evaluation"),
                "best_move": stockfish.get("best_move_san"),
                "fen": search_result.metadata.get("fen", "")
              }
              formatted_results.append(formatted_result)
            
            # Generate narrative report instead of raw JSON
            report = self._format_related_games_report(formatted_results, query)
            
            result = {
              "status": "related_games_found", 
              "report": report
            }
          else:
            result = {
              "status": "no_matches",
              "query": query,
              "message": "No similar games found."
            }
            
        except Exception as e:
          print(f"❌ Related games search failed: {e}")
          result = {
            "status": "search_error", 
            "error": f"Failed to search related games: {str(e)}"
          }

      elif fc.name == "remember_information":
        information = fc.args.get("information", "")
        category = fc.args.get("category", "general")
        
        print(f"💾 Storing memory: {information[:100]}{'...' if len(information) > 100 else ''}")
        
        if self.memory_client and information.strip():
            try:
                await asyncio.to_thread(
                    self.memory_client.add,
                    messages=[{"role": "user", "content": information}],
                    user_id="chess_tv_user",
                    metadata={"category": category, "timestamp": datetime.now().isoformat()}
                )
                result = {"status": "remembered", "information": information, "category": category}
            except Exception as e:
                result = {"status": "memory_failed", "error": str(e)}
        else:
            result = {"status": "no_memory_system", "message": "Memory system not available"}

      else:
        result = {"error": f"Unknown function: {fc.name}"}

      function_responses.append(
          types.FunctionResponse(id=fc.id, name=fc.name, response=result)
      )

    if function_responses:
      print(f"\n🔧 SENDING {len(function_responses)} TOOL RESPONSES TO GEMINI")
      for i, response in enumerate(function_responses):
        print(f"Tool Response {i+1}: {response.name} (ID: {response.id})")
        if hasattr(response.response, 'get') and 'analysis' in response.response:
          analysis_len = len(response.response.get('analysis', ''))
          print(f"  → Analysis content length: {analysis_len} chars")
        print(f"  → Full response: {response.response}")
      
      await self.session.send_tool_response(
          function_responses=function_responses
      )
      print("✅ Tool responses sent to Gemini successfully")

  async def play_audio(self):
    """Play Gemini's audio responses using pw-cat with pre-buffering"""
    # Wait for initial buffer
    initial_chunks = []
    for _ in range(3):  # Buffer 3 chunks before starting
      chunk = await self.audio_in_queue.get()
      initial_chunks.append(chunk)

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

      # Play buffered chunks first
      for chunk in initial_chunks:
        play_process.stdin.write(chunk)
        await play_process.stdin.drain()

      # Continue normal playback
      while True:
        bytestream = await self.audio_in_queue.get()
        play_process.stdin.write(bytestream)
        await play_process.stdin.drain()

    except Exception as e:
      print(f"❌ pw-cat playback error: {e}")



  async def _push_analysis_error(self, error_message: str):
    """Push analysis error to live model"""
    try:
      error_text = f"🚫 POSITION ANALYSIS ERROR: {error_message}"
      content = {"role": "user", "parts": [{"text": error_text}]}
      await self.session.send_client_content(turns=content, turn_complete=True)
      print(f"📤 Error message sent to user: {error_message}")
    except Exception as e:
      print(f"❌ Failed to push error to user: {e}")


  async def run(self):
    """Main simplified chess companion loop"""
    print("♟️  Starting Simplified Chess Companion...")
    print("👁️ Watching mode: Automatic analysis and commentary")
    print("🎧 Make sure to use headphones to prevent audio feedback!")
    print("💡 Type 'q' to quit")

    try:
      async with (
          self.client.aio.live.connect(
              model=MODEL, config=CHESS_CONFIG
          ) as session,
          asyncio.TaskGroup() as tg,
      ):
        self.session = session
        self.audio_in_queue = asyncio.Queue()

        # Start all tasks
        send_text_task = tg.create_task(self.send_text())
        
        # New background architecture: scene detection + fast FEN detection
        await self.detect_initial_board_mask()  # Seed the bounding box - WAIT for this
        
        tg.create_task(self.start_scene_detection())       # Background scene detection  
        tg.create_task(self.fast_fen_detection_loop())     # Fast FEN checking
        
        tg.create_task(self.listen_user_audio())
        tg.create_task(self.transcribe_tv_audio())
        tg.create_task(self.receive_audio())
        tg.create_task(self.play_audio())

        await send_text_task

    except Exception as e:
      print(f"❌ Error: {e}")
      traceback.print_exc()
    finally:
      # Cleanup
      if hasattr(self, "engine_pool"):
        self.engine_pool.cleanup()
      if self.shared_cap:
        self.shared_cap.release()
      if self.mic_stream:
        self.mic_stream.close()
      if self.pya:
        self.pya.terminate()


if __name__ == "__main__":
  args = parse_args()
  companion = ChessCompanionSimplified(
      debug_mode=args.debug, watching_mode=not args.no_watch
  )
  asyncio.run(companion.run())
