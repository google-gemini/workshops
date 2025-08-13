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

def parse_args():
    parser = argparse.ArgumentParser(description="Chess Companion with simplified board analysis")
    parser.add_argument("--debug", action="store_true", 
                       help="Save debug images (HDMI captures and crops)")
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
- Toggle watching mode on/off for automatic position commentary

## Chess Commentary Style:
When you receive position analysis packages (position + analysis + historical context), provide expert chess commentary that enhances understanding:

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

Feel free to suggest chess content to watch or help users find specific games. Only comment when you have something genuinely insightful to add about the position.
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
        ]
    }],
}


class TVAudioStream:
    """Captures TV audio using pw-cat and provides it as a stream for transcription"""

    def __init__(self):
        import queue
        self._buff = queue.Queue()  # Use sync queue for Google Cloud Speech compatibility
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

                self._buff.put(data)  # Sync put to sync queue
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
                chunk = self._buff.get(timeout=1.0)  # Sync get with timeout
                if chunk is None:
                    print("📡 Audio generator: received termination signal")
                    return

                chunks_yielded += 1
                # Remove noisy logging - only log major milestones
                if chunks_yielded % 500 == 0:  # Log every 50 seconds instead
                    print(f"📡 Audio generator: {chunks_yielded} chunks yielded")

                yield chunk
            except:
                print("⚠️ Audio generator: timeout waiting for chunk")
                continue


class ChessCompanionSimplified:
    """Simplified Chess Companion - Current board analysis only"""

    def __init__(self, debug_mode=False):
        # Core state - just current board
        self.current_board = None
        self.current_analysis = None
        self.analyzing = False
        self.commentary_buffer = []  # Recent commentary for current board
        
        # Watching mode - default to True for demo
        self.watching_mode = True
        
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
        self.vector_search = ChessVectorSearch()
        self.engine_pool = create_quick_analysis_pool(pool_size=4)
        
        # Audio components
        self.pya = None
        self.mic_stream = None
        self.shared_cap = None
        
        # Memory and speech
        self.memory_client = self._init_memory_client()
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

    async def detect_board_changes(self):
        """Detect when board position changes and analyze"""
        print("♟️  Starting board position detection...")
        
        # Initialize video capture
        self.shared_cap = cv2.VideoCapture(HDMI_VIDEO_DEVICE)
        if not self.shared_cap.isOpened():
            print(f"❌ Cannot open HDMI video device {HDMI_VIDEO_DEVICE}")
            return

        self.shared_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.shared_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        print("✅ HDMI capture ready")

        detection_count = 0
        
        while True:
            try:
                detection_count += 1
                ret, frame = self.shared_cap.read()
                
                if not ret:
                    print("⚠️  Failed to capture frame")
                    await asyncio.sleep(2)
                    continue

                # Save frame and detect position
                temp_path = await self.save_frame_to_temp(frame)
                
                print(f"🔍 Detection #{detection_count}: Running consensus...")
                result = await consensus_piece_detection(
                    temp_path, n=7, min_consensus=3,
                    debug_dir=str(self.debug_dir) if self.debug_mode else None
                )
                
                new_fen = result["consensus_fen"]
                os.unlink(temp_path)  # Cleanup
                
                # Validate FEN before proceeding
                if new_fen and self.is_valid_fen(new_fen):
                    if new_fen != self.current_board:
                        print(f"🆕 New board detected: {new_fen[:30]}...")
                        await self.on_board_change(new_fen, frame)
                    else:
                        print(f"📍 Same board: {new_fen[:30]}...")
                elif new_fen and not self.is_valid_fen(new_fen):
                    print(f"❌ Invalid FEN returned: {new_fen[:50]}...")
                else:
                    print(f"❌ No FEN detected")

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                print(f"❌ Board detection error: {e}")
                traceback.print_exc()
                await asyncio.sleep(5)

    async def on_board_change(self, new_fen: str, frame):
        """Handle new board position detected"""
        print(f"🎯 Board changed from {self.current_board} to {new_fen}")
        
        # Update current state
        self.current_board = new_fen
        self.current_analysis = None
        self.commentary_buffer = []  # Fresh start for new position
        
        # Start analysis (don't wait for it)
        if not self.analyzing:
            asyncio.create_task(self.analyze_current_board(frame))

    async def analyze_current_board(self, frame=None):
        """Create full database-style entry for live position"""
        if self.analyzing or not self.current_board:
            return
            
        self.analyzing = True
        print(f"🔍 Creating full database entry for: {self.current_board[:30]}...")
        
        try:
            # Import database functions
            from build_database import generate_quick_description
            from chess_description_generator import enhance_single_position_with_retry, ChessDescriptionGenerator
            
            # Create position in database format
            position_entry = {
                "fen": self.current_board,
                "move_number": None,  # Unknown for live positions
                "last_move": None,    # Could try to infer later
                "game_context": {},   # Empty for live
                "position_features": extract_position_features(self.current_board),
                "stockfish_analysis": await self._get_stockfish_analysis_database_format(),
                "timestamp": datetime.now().isoformat(),
                "commentary": list(self.commentary_buffer),  # Live commentary buffer
            }
            
            # Add board screenshot if available
            if frame is not None:
                try:
                    position_entry["board_screenshot"] = self._convert_frame_to_base64(frame)
                except Exception as e:
                    print(f"❌ Screenshot error: {e}")

            print(f"🤖 Generating LLM-enhanced description with commentary context...")
            # Add LLM-enhanced description with live commentary context
            generator = ChessDescriptionGenerator()
            chain = generator.create_description_chain()
            semaphore = asyncio.Semaphore(1)  # Single concurrent for live
            
            # Enhance position entry with commentary context for better descriptions
            if self.commentary_buffer:
                recent_commentary = " ".join(self.commentary_buffer[-5:])  # Last 5 commentary lines
                position_entry["live_commentary"] = recent_commentary
                print(f"📺 Including commentary context: {recent_commentary[:100]}...")
            
            _, enhanced_desc, error = await enhance_single_position_with_retry(
                (position_entry, 0), generator, chain, semaphore
            )
            
            if enhanced_desc and not error:
                position_entry["enhanced_description"] = enhanced_desc
                print(f"✅ LLM description generated")
            else:
                print(f"⚠️ LLM description failed, using template: {error}")
                # Fallback to template description
                position_entry["enhanced_description"] = {
                    "description": generate_quick_description(position_entry),
                    "strategic_themes": [],
                    "tactical_elements": [],
                    "key_squares": [],
                    "generated_by": "template-fallback"
                }
            
            # Add simple vector search mentions
            position_entry["similar_positions"] = await self._get_simple_similar_games()
            
            # Store complete database-style entry
            self.current_analysis = position_entry
            print(f"✅ Full database entry complete for {self.current_board[:30]}...")

            # Auto-send if watching mode
            if self.watching_mode:
                await self.send_analysis_to_gemini(position_entry)

        except Exception as e:
            print(f"❌ Analysis error: {e}")
            traceback.print_exc()
        finally:
            self.analyzing = False

    async def send_analysis_to_gemini(self, analysis):
        """Send analysis to Gemini Live for commentary"""
        try:
            # Format analysis for Gemini
            analysis_text = self._format_analysis_for_gemini(analysis)
            
            # Show what we're sending to Gemini
            print(f"\n📤 SENDING TO GEMINI:")
            print("=" * 50)
            print(analysis_text)
            print("=" * 50)
            
            content = {"role": "user", "parts": [{"text": analysis_text}]}
            await self.session.send_client_content(turns=content, turn_complete=True)
            print(f"✅ Sent analysis to Gemini (watching mode)")
            
        except Exception as e:
            print(f"❌ Failed to send analysis: {e}")

    def _format_analysis_for_gemini(self, database_entry) -> str:
        """Format complete database entry for Gemini Live"""
        
        # Use the rich LLM description as primary content
        enhanced = database_entry.get("enhanced_description", {})
        description = enhanced.get("description", "Position analysis unavailable")
        
        text = f"""CHESS POSITION ANALYSIS:

{description}

STRATEGIC ELEMENTS:
- Strategic themes: {', '.join(enhanced.get('strategic_themes', ['None']))}
- Tactical elements: {', '.join(enhanced.get('tactical_elements', ['None']))}
- Key squares: {', '.join(enhanced.get('key_squares', ['None']))}
"""
        
        # Add engine specifics
        engine = database_entry.get("stockfish_analysis", {})
        if engine:
            eval_score = engine.get('evaluation', 0)
            eval_type = engine.get('evaluation_type', 'cp')
            best_move = engine.get('best_move_san', '?')
            
            if eval_type == 'mate':
                mate_in = engine.get('mate_in', '?')
                eval_text = f"Mate in {mate_in}"
            else:
                eval_text = f"{eval_score:+.1f}"
            
            text += f"\nENGINE ANALYSIS: {eval_text}, best move: {best_move}"
        
        # Simple similar games mention
        similar = database_entry.get("similar_positions", [])
        if similar:
            text += f"\n\nSIMILAR MASTER GAMES: "
            mentions = []
            for game in similar[:2]:  # Top 2 games
                result_emoji = {"1-0": "1-0", "0-1": "0-1", "1/2-1/2": "½-½"}.get(game.get('result', '*'), game.get('result', '*'))
                mentions.append(f"{game['game']} ({result_emoji})")
            text += ", ".join(mentions)
        
        # Recent commentary if available (selective for live model)
        commentary = database_entry.get("commentary", [])
        if commentary:
            # For live model, only include most recent impactful commentary
            recent = commentary[-2:] if len(commentary) >= 2 else commentary
            commentary_text = " ".join(recent)
            
            # Only include if commentary seems relevant (contains chess terms)
            chess_terms = ['move', 'piece', 'attack', 'defense', 'advantage', 'pressure', 'critical', 'tactical', 'strategic']
            if any(term in commentary_text.lower() for term in chess_terms):
                text += f"\n\nLIVE CONTEXT: {commentary_text[:150]}..."  # Limit length
        
        # Add explicit request for commentary
        text += f"\n\nPlease provide your expert chess commentary on this position. What should players be thinking about? What are the key plans and ideas?"
        
        return text

    def is_valid_fen(self, fen: str) -> bool:
        """Check if a string is a valid FEN"""
        try:
            chess.Board(fen)
            return True
        except (ValueError, TypeError):
            return False

    async def save_frame_to_temp(self, frame) -> str:
        """Save video frame to temporary file for vision analysis"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_path = temp_file.name

        # Convert frame and save - normalize before vision analysis
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img.thumbnail((1024, 1024), Image.LANCZOS)  # Normalize for better vision results
        img.save(temp_path)

        return temp_path

    async def _get_engine_analysis(self, fen: str) -> dict:
        """Get Stockfish analysis of position (simple format)"""
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

    async def _get_stockfish_analysis_database_format(self) -> dict:
        """Get Stockfish analysis in database format"""
        try:
            engine = self.engine_pool.get_engine()
            board = chess.Board(self.current_board)

            # Quick analysis (0.5 seconds) 
            info = await asyncio.to_thread(
                engine.analyse, board, chess.engine.Limit(time=0.5)
            )

            self.engine_pool.return_engine(engine)

            # Extract evaluation score (same format as build_database.py)
            score = info["score"].white()
            if score.is_mate():
                eval_score = 10000 if score.mate() > 0 else -10000
                eval_type = "mate"
                mate_in = abs(score.mate())
            else:
                eval_score = score.score() / 100.0
                eval_type = "cp"
                mate_in = None

            best_move = info["pv"][0] if info.get("pv") else None
            best_move_san = board.san(best_move) if best_move else None

            return {
                "evaluation": eval_score,
                "evaluation_type": eval_type,
                "mate_in": mate_in,
                "best_move": str(best_move) if best_move else None,
                "best_move_san": best_move_san,
                "principal_variation": [str(move) for move in info.get("pv", [])[:5]],
                "depth": info.get("depth"),
                "nodes": info.get("nodes"),
                "time": info.get("time"),
            }

        except Exception as e:
            print(f"❌ Engine analysis failed: {e}")
            return {
                "evaluation": 0.0,
                "evaluation_type": "error",
                "error": str(e),
            }

    def _create_position_query(self, features: dict, engine_analysis: dict) -> str:
        """Create search query from position characteristics"""
        query_parts = []

        # Add game phase
        if features.get("game_phase"):
            query_parts.append(features["game_phase"])

        # Add material situation
        material = features.get("material", {})
        if material.get("balance", 0) > 2:
            query_parts.append("material advantage")
        elif material.get("balance", 0) < -2:
            query_parts.append("material disadvantage")

        # Add pawn structure themes
        pawn_structure = features.get("pawn_structure", {})
        if pawn_structure.get("doubled_pawns", {}).get("white") or pawn_structure.get("doubled_pawns", {}).get("black"):
            query_parts.append("doubled pawns")
        if pawn_structure.get("isolated_pawns", {}).get("white") or pawn_structure.get("isolated_pawns", {}).get("black"):
            query_parts.append("isolated pawns")
        if pawn_structure.get("passed_pawns", {}).get("white") or pawn_structure.get("passed_pawns", {}).get("black"):
            query_parts.append("passed pawns")

        # Add tactical elements
        if engine_analysis.get("evaluation", 0) > 300:
            query_parts.append("tactical advantage")
        elif engine_analysis.get("evaluation", 0) < -300:
            query_parts.append("tactical problems")

        return " ".join(query_parts) if query_parts else "chess position analysis"

    async def _get_simple_similar_games(self):
        """Get vector search with just game outcomes for passing mention"""
        try:
            # Use existing query generation
            if not self.current_analysis:
                features = extract_position_features(self.current_board)
                engine = await self._get_engine_analysis(self.current_board)
            else:
                features = self.current_analysis.get("position_features", {})
                engine = self.current_analysis.get("stockfish_analysis", {})
            
            query = self._create_position_query(features, engine)
            print(f"🔍 Vector search query for similar games: '{query}'")
            
            results = await self.vector_search.search(query, top_k=3)
            print(f"📚 Found {len(results)} similar games for mention")
            
            # Simple format: just mention games and outcomes
            simple_results = []
            for result in results:
                white = result.metadata.get('white_player', 'Unknown')
                black = result.metadata.get('black_player', 'Unknown') 
                outcome = result.metadata.get('result', '*')
                simple_results.append({
                    "game": f"{white} vs {black}",
                    "result": outcome,
                    "similarity": result.similarity
                })
            return simple_results
            
        except Exception as e:
            print(f"⚠️ Similar games search failed: {e}")
            return []

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
                await self.session.send_realtime_input(audio={"data": data, "mime_type": "audio/pcm"})

        except Exception as e:
            print(f"❌ User audio capture error: {e}")
            raise

    async def transcribe_tv_audio(self):
        """Continuously transcribe TV audio and add to commentary buffer"""
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

            # Only process final results to avoid spam
            if result.is_final and transcript.strip():
                transcripts_received += 1
                print(f"📝 Transcribed #{transcripts_received}: {transcript}")

                # Add to commentary buffer (for current board context)
                self.commentary_buffer.append(transcript)
                # Keep only last 10 commentary lines
                if len(self.commentary_buffer) > 10:
                    self.commentary_buffer = self.commentary_buffer[-10:]
                
                print(f"📝 Added to commentary buffer: {transcript[:50]}...")

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
                # Trigger analysis if not already done
                if not self.current_analysis and self.current_board:
                    await self.analyze_current_board()
                
                result = {
                    "current_board": self.current_board,
                    "analysis_available": self.current_analysis is not None,
                    "status": "analysis_complete" if self.current_analysis else "no_analysis"
                }

            elif fc.name == "search_similar_positions":
                query = fc.args.get("query", "")
                print(f"📚 Searching similar positions: {query}")

                try:
                    search_results = await self.vector_search.search(query, top_k=5)
                    
                    results_data = []
                    for result in search_results:
                        results_data.append({
                            "similarity": result.similarity,
                            "players": f"{result.metadata.get('white_player', '?')} vs {result.metadata.get('black_player', '?')}",
                            "description": result.description[:200],
                            "fen": result.fen,
                        })

                    result = {
                        "query": query,
                        "results_found": len(results_data),
                        "similar_positions": results_data,
                    }

                except Exception as e:
                    result = {"error": f"Search failed: {e}"}

            elif fc.name == "start_watching_mode":
                self.watching_mode = True
                result = {"status": "watching_mode_started"}
                print("👁️ Watching mode ON")

            elif fc.name == "stop_watching_mode":
                self.watching_mode = False
                result = {"status": "watching_mode_stopped"}
                print("👁️ Watching mode OFF")

            else:
                result = {"error": f"Unknown function: {fc.name}"}

            function_responses.append(
                types.FunctionResponse(id=fc.id, name=fc.name, response=result)
            )

        if function_responses:
            await self.session.send_tool_response(function_responses=function_responses)

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
        """Main simplified chess companion loop"""
        print("♟️  Starting Simplified Chess Companion...")
        print("👁️ Watching mode: Automatic analysis and commentary")
        print("🎧 Make sure to use headphones to prevent audio feedback!")
        print("💡 Type 'q' to quit")

        try:
            async with (
                self.client.aio.live.connect(model=MODEL, config=CHESS_CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                self.audio_in_queue = asyncio.Queue()

                # Start all tasks
                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.detect_board_changes())  # Main detection loop
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
    companion = ChessCompanionSimplified(debug_mode=args.debug)
    asyncio.run(companion.run())
