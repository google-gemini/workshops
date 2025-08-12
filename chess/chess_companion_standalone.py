"""Standalone Chess Companion - Real-time chess game analysis with AI commentary

Forked from TV companion architecture for chess-specific analysis:
- Move detection via consensus vision instead of scene detection
- Chess position analysis instead of film context
- Vector search through historical games database
- Expert chess commentary via Gemini Live
"""

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
from chess_vision_test import consensus_piece_detection
import cv2
from google import genai
from google.cloud import speech
from google.genai import types
from mem0 import MemoryClient
import numpy as np
from PIL import Image
from position_features import extract_position_features
import pyaudio
from stockfish_pool import StockfishEnginePool, create_quick_analysis_pool
from vector_search import ChessVectorSearch, SearchResult

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
HDMI_AUDIO_TARGET = (
    "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo"
)

MODEL = "gemini-2.5-flash-preview-native-audio-dialog"

# Chess companion configuration
CHESS_CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": (
        """You are an expert chess companion with deep knowledge of chess theory, tactics, strategy, and chess history.

You can provide insightful commentary AND control the TV for chess content.

## TV Control Capabilities:
- Search for and play chess videos using search_and_play_content  
- Pause playback with pause_playback
- Access user's viewing history with search_user_history
- Toggle watching mode on/off for automatic move commentary

## Chess Commentary Style:
When you receive move packages (position + analysis + historical context), provide expert chess commentary that enhances understanding:

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

Feel free to suggest chess content to watch or help users find specific games. Only comment when you have something genuinely insightful to add about the position or moves.
"""
    ),
    "tools": [{
        "function_declarations": [
            {
                "name": "search_similar_positions",
                "description": (
                    "Search the chess games database for positions similar to"
                    " the current board position. Use this to provide"
                    " historical context and compare with master games."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Description of position characteristics to"
                                " search for (e.g., 'kingside attack with piece"
                                " sacrifice', 'endgame rook and pawn',"
                                " 'tactical pin and fork themes')"
                            ),
                        },
                        "fen": {
                            "type": "string",
                            "description": (
                                "Optional: FEN string for exact position"
                                " matching"
                            ),
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "analyze_current_position",
                "description": (
                    "Get detailed engine analysis of the current board position"
                    " including best moves, evaluation, and tactical themes"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "search_and_play_content",
                "description": (
                    "Search for and start playing chess content on the TV using"
                    " Google TV's universal search. Works well with queries"
                    " like 'magnus carlsen vs hikaru nakamura' or 'world"
                    " championship 2023'"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": (
                                "Chess game, tournament, or players to"
                                " search for"
                            ),
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
                    "Start automatically commenting on moves as they happen"
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
                "description": "Stop automatic move commentary",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "pause_playbook",
                "description": (
                    "Pause the currently playing chess content on TV"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        ]
    }],
}


class FENHistory:
  """Manages FEN detection history to handle noise and detect stable moves"""

  def __init__(self, window_size=10):
    self.fen_window = []  # [(fen, timestamp, confidence), ...]
    self.confirmed_moves = []  # [(old_fen, new_fen, move, timestamp), ...]
    self.window_size = window_size
    self.current_stable_fen = None
    self.last_move_time = 0

  def add_detection(self, fen, confidence=1.0):
    """Add FEN detection with confidence score"""
    timestamp = time.time()
    self.fen_window.append((fen, timestamp, confidence))

    # Keep only recent detections
    cutoff_time = timestamp - 10  # Keep last 10 seconds
    self.fen_window = [
        (f, t, c) for f, t, c in self.fen_window if t > cutoff_time
    ]

    if len(self.fen_window) > self.window_size:
      self.fen_window = self.fen_window[-self.window_size :]

  def get_stable_fen(self, min_confirmations=3, min_stability_time=2.0):
    """Get FEN confirmed by multiple recent detections"""
    if len(self.fen_window) < min_confirmations:
      return None

    # Get recent detections
    now = time.time()
    recent_window = [
        (f, t, c) for f, t, c in self.fen_window if now - t < min_stability_time
    ]

    if len(recent_window) < min_confirmations:
      return None

    # Count FEN occurrences in recent window
    fen_counts = {}
    for fen, timestamp, confidence in recent_window:
      if fen and not fen.startswith("Invalid"):
        fen_counts[fen] = fen_counts.get(fen, 0) + confidence

    if not fen_counts:
      return None

    # Return most frequent stable FEN
    stable_fen = max(fen_counts.items(), key=lambda x: x[1])[0]

    # Require minimum confirmations
    if fen_counts[stable_fen] >= min_confirmations:
      return stable_fen

    return None

  def detect_move_transition(self, new_stable_fen):
    """Detect when position has clearly changed"""
    if not new_stable_fen or not self.current_stable_fen:
      if new_stable_fen and not self.current_stable_fen:
        # First position detected
        self.current_stable_fen = new_stable_fen
        print(f"🎯 Initial stable position: {new_stable_fen}")
        return None
      return None

    if new_stable_fen != self.current_stable_fen:
      # Position changed - record the move
      old_fen = self.current_stable_fen
      timestamp = time.time()

      # Avoid rapid fire detections
      if timestamp - self.last_move_time < 1.0:
        print(f"⏸️  Ignoring rapid position change (< 1s since last)")
        return None

      self.confirmed_moves.append((old_fen, new_stable_fen, timestamp))
      self.current_stable_fen = new_stable_fen
      self.last_move_time = timestamp

      print(
          f"♟️  Stable move detected: {old_fen[:20]}... ->"
          f" {new_stable_fen[:20]}..."
      )
      return (old_fen, new_stable_fen)

    return None


class PositionBuffer:
  """Buffers chess position data for analysis and commentary"""

  def __init__(self, move_number: int):
    self.move_number = move_number
    self.position_fen = None
    self.move_played = None
    self.previous_fen = None

    # Analysis data
    self.engine_analysis = None
    self.position_features = None
    self.similar_positions = []

    # Context data
    self.commentary_lines = []
    self.board_screenshot = None
    self.start_time = time.time()

  def add_position(self, fen: str, previous_fen: str = None):
    """Set the chess position for this buffer"""
    self.position_fen = fen
    self.previous_fen = previous_fen
    if previous_fen:
      self.move_played = self.extract_move_played(previous_fen, fen)

  def extract_move_played(self, old_fen: str, new_fen: str) -> str:
    """Extract the move played between two positions"""
    try:
      # Create boards from FENs
      old_board = chess.Board(old_fen)
      new_board = chess.Board(new_fen)

      # Find the move that transforms old_board to new_board
      for move in old_board.legal_moves:
        test_board = old_board.copy()
        test_board.push(move)
        if (
            test_board.fen().split()[0] == new_board.fen().split()[0]
        ):  # Compare just position
          return old_board.san(move)  # Return in algebraic notation

      return "Unknown move"
    except Exception:
      return "Invalid move"

  def add_commentary(self, text: str):
    """Add a commentary line with timestamp"""
    elapsed = time.time() - self.start_time
    timestamp = f"{int(elapsed//60):02d}:{elapsed%60:05.2f}"
    self.commentary_lines.append(f"[{timestamp}] {text}")

  def add_screenshot(self, image_data):
    """Add board screenshot"""
    self.board_screenshot = image_data

  def create_move_package(self) -> dict:
    """Create a complete move package for the model"""
    duration = time.time() - self.start_time
    commentary_text = (
        "\n".join(self.commentary_lines) if self.commentary_lines else ""
    )

    package = {
        "type": "move_analysis",
        "move_number": self.move_number,
        "duration": f"{duration:.1f}s",
        "position": self.position_fen,
        "move_played": self.move_played,
        "previous_position": self.previous_fen,
        "commentary": commentary_text,
    }

    # Add analysis data if available
    if self.engine_analysis:
      package["engine_analysis"] = self.engine_analysis
    if self.position_features:
      package["position_features"] = self.position_features
    if self.similar_positions:
      package["similar_positions"] = self.similar_positions
    if self.board_screenshot:
      package["board_screenshot"] = self.board_screenshot

    return package


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

        # Remove noisy logging - only log major milestones
        if chunks_sent % 500 == 0:  # Log every 50 seconds instead
          print(f"📡 Audio buffer: {chunks_sent} chunks processed")

      except Exception as e:
        print(f"❌ Audio feed error: {e}")
        break

  def generator(self):
    """Generator that yields audio chunks for Google Cloud Speech"""
    chunks_yielded = 0
    while not self.closed:
      try:
        chunk = self._buff.get(timeout=1.0)
        if chunk is None:
          print("📡 Audio generator: received termination signal")
          return

        chunks_yielded += 1
        # Remove noisy logging - only log major milestones
        if chunks_yielded % 500 == 0:  # Log every 50 seconds instead
          print(f"📡 Audio generator: {chunks_yielded} chunks yielded")

        yield chunk
      except queue.Empty:
        print("⚠️ Audio generator: timeout waiting for chunk")
        continue


class ChessCompanionStandalone:
  """Standalone Chess Companion - Complete chess analysis system"""

  def __init__(self):
    self.audio_in_queue = None
    self.out_queue = None
    self.session = None
    self.shared_cap = None

    # Gemini client
    self.client = genai.Client()

    # User microphone input
    self.pya = None
    self.mic_stream = None

    # Episodic memory
    self.memory_client = self._init_memory_client()

    # Watching mode control
    self.watching_mode = True  # Default: auto-send moves (for testing)

    # Chess-specific components
    self.vector_search = ChessVectorSearch()
    self.engine_pool = create_quick_analysis_pool(pool_size=4)

    # Position tracking
    self.current_position = None
    self.move_counter = 0
    self.max_position_duration = 120  # 2 minutes max per position

    # FEN history for noise handling
    self.fen_history = FENHistory()

    # Speech recognition
    self.speech_client = speech.SpeechClient()
    self.speech_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SEND_SAMPLE_RATE,
        language_code="en-US",
        max_alternatives=1,
    )
    self.streaming_config = speech.StreamingRecognitionConfig(
        config=self.speech_config, interim_results=True
    )

    print("♟️  Chess Companion initialized")
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
          project_id="proj_I6CXbVIrt0AFlWE0MU3TyKxkkYJam2bHm8nUxgEu",
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

  async def detect_move_changes(self):
    """Chess move detection via consensus vision with noise handling"""
    print("♟️  Starting chess move detection...")

    # Initialize shared video capture
    self.shared_cap = cv2.VideoCapture(HDMI_VIDEO_DEVICE)
    if not self.shared_cap.isOpened():
      print(f"❌ Cannot open HDMI video device {HDMI_VIDEO_DEVICE}")
      return

    self.shared_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    self.shared_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    print("✅ HDMI capture ready for move detection")
    detection_count = 0

    while self.shared_cap:
      try:
        detection_count += 1
        ret, frame = self.shared_cap.read()

        print(f"📺 Detection #{detection_count}: Frame captured = {ret}")
        if frame is not None:
          print(f"📏 Frame shape: {frame.shape}")

        if not ret:
          print("⚠️  Failed to capture frame for move detection")
          await asyncio.sleep(1)
          continue

        # Save frame to temporary file for consensus detection
        temp_path = await self.save_frame_to_temp(frame)

        # Use consensus vision to detect position
        print(f"🔍 Running consensus detection #{detection_count}...")
        result = await consensus_piece_detection(
            temp_path, n=5, min_consensus=3
        )
        new_fen = result["consensus_fen"]

        print(f"🎯 FEN detected: {new_fen if new_fen else 'None'}")
        print(f"📊 Consensus details: {result.get('details', 'No details')}")

        # Clean up temp file
        os.unlink(temp_path)

        # Add to FEN history for noise handling
        if new_fen and not new_fen.startswith("Invalid"):
          confidence = result.get("confidence", 1.0)
          self.fen_history.add_detection(new_fen, confidence)

          # Check for stable position changes
          stable_fen = self.fen_history.get_stable_fen(
              min_confirmations=3, min_stability_time=1.5
          )
          print(
              f"📈 Stable FEN: {stable_fen if stable_fen else 'None'}"
          )

          # Detect move transitions using FEN history
          move_transition = self.fen_history.detect_move_transition(stable_fen)

          if move_transition:
            old_fen, new_stable_fen = move_transition
            if self.is_legal_transition(old_fen, new_stable_fen):
              print(
                  f"✅ Legal move confirmed: {old_fen} ->"
                  f" {new_stable_fen}"
              )
              await self.handle_new_move(old_fen, new_stable_fen, frame)
            else:
              print(
                  f"❌ Illegal transition detected, ignoring: {old_fen}"
                  f" -> {new_stable_fen}"
              )

        await asyncio.sleep(1)  # Check every 1 second (faster detection)

      except Exception as e:
        print(f"❌ Move detection error: {e}")
        traceback.print_exc()
        await asyncio.sleep(5)  # Wait longer on error

  async def save_frame_to_temp(self, frame) -> str:
    """Save video frame to temporary file for vision analysis"""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
      temp_path = temp_file.name

    # Convert frame and save
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img.save(temp_path)

    return temp_path

  def is_legal_transition(self, old_fen: str, new_fen: str) -> bool:
    """Check if transition between positions represents a legal chess move"""
    if not old_fen or not new_fen:
      return False

    try:
      old_board = chess.Board(old_fen)
      new_board = chess.Board(new_fen)

      # Check if any legal move from old position leads to new position
      for move in old_board.legal_moves:
        test_board = old_board.copy()
        test_board.push(move)
        if test_board.fen().split()[0] == new_board.fen().split()[0]:
          return True

      return False
    except Exception:
      return False

  async def handle_new_move(self, old_fen: str, new_fen: str, frame):
    """Handle detection of a new chess move"""
    # Finalize previous position if it exists
    if self.current_position is not None:
      await self._finalize_current_position()

    # Start new position analysis
    await self._start_new_position(old_fen, new_fen, frame)

  async def _finalize_current_position(self):
    """Finalize current position analysis and send if in watching mode"""
    if self.current_position is None:
      return

    move_package = self.current_position.create_move_package()
    print(
        f"📦 Finalizing move {move_package['move_number']}:"
        f" {move_package.get('move_played', 'Unknown')}"
    )

    if self.watching_mode:
      try:
        await self.out_queue.put(move_package)
        print(f"📤 Auto-sent move package (watching mode)")
      except:
        print(f"⚠️  Failed to queue move package")
    else:
      print(f"📦 Discarded move package (non-watching mode)")

  async def _start_new_position(self, old_fen: str, new_fen: str, frame):
    """Start analysis of new chess position"""
    self.move_counter += 1
    self.current_position = PositionBuffer(self.move_counter)
    self.current_position.add_position(new_fen, old_fen)

    print(
        f"♟️  Started analyzing move {self.move_counter}:"
        f" {self.current_position.move_played}"
    )

    # Add board screenshot
    try:
      frame_data = self._convert_frame_to_base64(frame)
      self.current_position.add_screenshot(frame_data)
    except Exception as e:
      print(f"❌ Error adding screenshot: {e}")

    # Start background analysis
    asyncio.create_task(self._analyze_position_async(self.current_position))

  async def _analyze_position_async(self, position_buffer: PositionBuffer):
    """Analyze position asynchronously to avoid blocking move detection"""
    try:
      fen = position_buffer.position_fen

      # 1. Extract deterministic features
      print(f"🔍 Extracting features for move {position_buffer.move_number}...")
      position_buffer.position_features = extract_position_features(fen)

      # 2. Get engine analysis
      print(f"🔧 Getting engine analysis...")
      position_buffer.engine_analysis = await self._get_engine_analysis(fen)

      # 3. Search for similar positions
      print(f"📚 Searching for similar positions...")
      query = self._create_position_query(
          position_buffer.position_features, position_buffer.engine_analysis
      )
      position_buffer.similar_positions = await self.vector_search.search(
          query, top_k=3
      )

      print(f"✅ Completed analysis for move {position_buffer.move_number}")

    except Exception as e:
      print(f"❌ Position analysis error: {e}")
      traceback.print_exc()

  async def _get_engine_analysis(self, fen: str) -> dict:
    """Get Stockfish analysis of position"""
    try:
      engine = self.engine_pool.get_engine()
      board = chess.Board(fen)

      # Quick analysis (0.5 seconds)
      info = await asyncio.to_thread(
          engine.analyse, board, chess.engine.Limit(time=0.5)
      )

      self.engine_pool.return_engine(engine)

      return {
          "evaluation": (
              info.get(
                  "score",
                  chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE),
              ).relative.cp
              if info.get("score")
              else 0
          ),
          "best_move": (
              str(info.get("pv", [None])[0]) if info.get("pv") else None
          ),
          "depth": info.get("depth", 0),
      }

    except Exception as e:
      print(f"❌ Engine analysis failed: {e}")
      return {"evaluation": 0, "best_move": None, "depth": 0}

  def _create_position_query(
      self, features: dict, engine_analysis: dict
  ) -> str:
    """Create search query from position characteristics"""
    query_parts = []

    # Add game phase
    if features.get("game_phase"):
      query_parts.append(features["game_phase"])

    # Add material situation
    material = features.get("material", {})
    if material.get("material_balance", 0) > 200:
      query_parts.append("material advantage")
    elif material.get("material_balance", 0) < -200:
      query_parts.append("material disadvantage")

    # Add pawn structure themes
    pawn_structure = features.get("pawn_structure", {})
    if pawn_structure.get("doubled_pawns", {}).get("total", 0) > 0:
      query_parts.append("doubled pawns")
    if pawn_structure.get("isolated_pawns", {}).get("total", 0) > 0:
      query_parts.append("isolated pawns")
    if pawn_structure.get("passed_pawns", {}).get("total", 0) > 0:
      query_parts.append("passed pawns")

    # Add tactical elements
    if engine_analysis.get("evaluation", 0) > 300:
      query_parts.append("tactical advantage")
    elif engine_analysis.get("evaluation", 0) < -300:
      query_parts.append("tactical problems")

    return " ".join(query_parts) if query_parts else "chess position analysis"

  async def monitor_position_duration(self):
    """Monitor position duration and finalize long positions"""
    print("⏱️  Starting position duration monitor...")

    while True:
      if (
          self.current_position is not None
          and time.time() - self.current_position.start_time
          > self.max_position_duration
      ):

        print(
            f"⏱️  Position {self.current_position.move_number} exceeded "
            f"{self.max_position_duration}s, finalizing..."
        )
        await self._finalize_current_position()

        # Don't start new position - wait for actual move detection
        self.current_position = None

      await asyncio.sleep(15)  # Check every 15 seconds

  async def listen_user_audio(self):
    """Capture audio from user microphone"""
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
        await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

    except Exception as e:
      print(f"❌ User audio capture error: {e}")
      raise

  async def transcribe_tv_audio(self):
    """Continuously transcribe TV audio and add to current position"""
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

        # Add to current position buffer
        if self.current_position is not None:
          self.current_position.add_commentary(transcript)
          print(
              f"📝 Added to Position {self.current_position.move_number}:"
              f" {transcript[:50]}..."
          )

  async def send_realtime(self):
    """Send move packages and user audio to Gemini Live API"""
    packages_sent = 0

    while True:
      msg = await self.out_queue.get()

      # Handle user microphone audio
      if isinstance(msg, dict) and msg.get("mime_type") == "audio/pcm":
        await self.session.send_realtime_input(audio=msg)
        continue

      # Handle move packages
      if isinstance(msg, dict) and msg.get("type") == "move_analysis":
        packages_sent += 1
        move_num = msg.get("move_number", "?")
        duration = msg.get("duration", "?")

        print(
            f"📤 Sending Move Package #{packages_sent} (Move {move_num},"
            f" {duration}) to Gemini"
        )

        # Build Content parts list
        parts = []

        # Add move text with analysis
        if msg["position"]:
          move_text = f"""Move {move_num} ({duration}):

Position: {msg['position']}
Move played: {msg.get('move_played', 'Unknown')}"""

          if msg.get("engine_analysis"):
            engine = msg["engine_analysis"]
            move_text += f"\nEngine evaluation: {engine.get('evaluation', 0)}"
            move_text += f"\nBest move: {engine.get('best_move', 'Unknown')}"

          if msg.get("commentary"):
            move_text += f"\n\nCommentary:\n{msg['commentary']}"

          parts.append({"text": move_text})
          print(f"📝 Added move analysis for Move {move_num}")

        # Add board screenshot if available
        if msg.get("board_screenshot"):
          parts.append({
              "inline_data": {
                  "mime_type": msg["board_screenshot"]["mime_type"],
                  "data": msg["board_screenshot"]["data"],
              }
          })
          print(f"📸 Added board screenshot for Move {move_num}")

        # Send as complete client content turn
        if parts:
          content = {"role": "user", "parts": parts}
          await self.session.send_client_content(
              turns=content, turn_complete=True
          )
          print(f"📤 Sent complete move package: {len(parts)} parts")
        else:
          print(f"⚠️ No content to send for Move {move_num}")

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
          print(f"♟️ Chess Companion: {text}")
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
    """Handle chess-specific tool calls"""
    function_responses = []

    for fc in tool_call.function_calls:
      print(f"\n🔧 Chess tool call: {fc.name}")
      print(f"   Args: {fc.args}")

      if fc.name == "search_similar_positions":
        query = fc.args.get("query", "")

        print(f"📚 Searching similar positions: {query}")

        try:
          search_results = await self.vector_search.search(query, top_k=5)

          # Format results for model
          results_data = []
          for result in search_results:
            results_data.append({
                "similarity": result.similarity,
                "players": (
                    f"{result.metadata['white_player']} vs"
                    f" {result.metadata['black_player']}"
                ),
                "game_phase": result.metadata["game_phase"],
                "evaluation": result.metadata["stockfish_eval"],
                "description": result.description[:200],
                "strategic_themes": result.strategic_themes,
                "fen": result.fen,
            })

          result = {
              "query": query,
              "results_found": len(results_data),
              "similar_positions": results_data,
          }

        except Exception as e:
          result = {"error": f"Search failed: {e}"}

      elif fc.name == "analyze_current_position":
        print("🔍 Analyzing current position...")

        if self.current_position and self.current_position.position_fen:
          result = {
              "position": self.current_position.position_fen,
              "move_played": self.current_position.move_played,
              "features": self.current_position.position_features,
              "engine_analysis": self.current_position.engine_analysis,
              "status": "analysis_complete",
          }
        else:
          result = {
              "status": "no_position",
              "message": "No current position detected",
          }

      elif fc.name == "start_watching_mode":
        print("👁️ Starting watching mode - will auto-comment on moves")
        self.watching_mode = True
        result = {
            "status": "watching_mode_started",
            "message": "Now automatically commenting on moves",
        }

      elif fc.name == "stop_watching_mode":
        print("👁️ Stopping watching mode")
        self.watching_mode = False
        result = {
            "status": "watching_mode_stopped",
            "message": "Automatic move commentary disabled",
        }

      else:
        result = {"error": f"Unknown function: {fc.name}"}

      function_responses.append(
          types.FunctionResponse(id=fc.id, name=fc.name, response=result)
      )

    # Send tool responses
    if function_responses:
      await self.session.send_tool_response(
          function_responses=function_responses
      )

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

  async def run(self):
    """Main chess companion loop"""
    print("♟️  Starting Standalone Chess Companion...")
    print("🎧 Make sure to use headphones to prevent audio feedback!")
    print("💡 Type 'q' to quit")
    print("🎯 Chess move detection and analysis ready")

    try:
      async with (
          self.client.aio.live.connect(
              model=MODEL, config=CHESS_CONFIG
          ) as session,
          asyncio.TaskGroup() as tg,
      ):
        self.session = session
        self.audio_in_queue = asyncio.Queue()
        self.out_queue = asyncio.Queue(maxsize=20)

        # Start all tasks
        send_text_task = tg.create_task(self.send_text())
        tg.create_task(self.send_realtime())
        tg.create_task(self.listen_user_audio())
        tg.create_task(self.transcribe_tv_audio())
        tg.create_task(self.detect_move_changes())  # Chess-specific
        tg.create_task(self.monitor_position_duration())  # Chess-specific
        tg.create_task(self.receive_audio())
        tg.create_task(self.play_audio())

        await send_text_task
        raise asyncio.CancelledError("User requested exit")

    except asyncio.CancelledError:
      print("👋 Chess Companion stopped")
    except Exception as e:
      traceback.print_exception(e)
    finally:
      # Clean up chess-specific resources
      if hasattr(self, "engine_pool"):
        self.engine_pool.cleanup()

      # Clean up audio resources
      if self.mic_stream:
        self.mic_stream.close()
      if self.pya:
        self.pya.terminate()

      # Clean up video resources
      if self.shared_cap:
        self.shared_cap.release()


if __name__ == "__main__":
  companion = ChessCompanionStandalone()
  asyncio.run(companion.run())
