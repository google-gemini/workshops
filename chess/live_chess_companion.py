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

"""Live Chess Companion - Real-time chess game analysis with AI commentary

Adapts the TV companion architecture for chess-specific analysis:
- Move detection via consensus vision instead of scene detection  
- Chess position analysis instead of film context
- Vector search through historical games database
- Expert chess commentary via Gemini Live
"""

import asyncio
import base64
import io
import json
import os
import sys
import tempfile
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import cv2
import chess
import chess.engine
import numpy as np
from PIL import Image

# Add parent directory to Python path so we can import tv module
sys.path.append(str(Path(__file__).parent.parent))

# Import TV companion foundation
from tv.tv_companion_with_transcription import HDMITVCompanionWithTranscription

# Import chess-specific components
from chess_vision_test import consensus_piece_detection
from vector_search import ChessVectorSearch, SearchResult
from stockfish_pool import StockfishEnginePool, create_quick_analysis_pool
from position_features import extract_position_features

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
    "tools": [
        {
            "function_declarations": [
                {
                    "name": "search_similar_positions",
                    "description": (
                        "Search the chess games database for positions similar to the current board position. "
                        "Use this to provide historical context and compare with master games."
                    ),
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": (
                                    "Description of position characteristics to search for "
                                    "(e.g., 'kingside attack with piece sacrifice', 'endgame rook and pawn', "
                                    "'tactical pin and fork themes')"
                                ),
                            },
                            "fen": {
                                "type": "string", 
                                "description": "Optional: FEN string for exact position matching"
                            }
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "analyze_current_position", 
                    "description": (
                        "Get detailed engine analysis of the current board position including "
                        "best moves, evaluation, and tactical themes"
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
                        "Search for and start playing chess content on the TV using Google TV's universal search. "
                        "Works well with queries like 'magnus carlsen vs hikaru nakamura' or 'world championship 2023'"
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Chess game, tournament, or players to search for",
                            }
                        },
                        "required": ["title"],
                    },
                },
                {
                    "name": "search_user_history",
                    "description": (
                        "Search the user's personal viewing history and past chess discussions. "
                        "Use this to recall previous games watched, positions analyzed, or questions asked."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": (
                                    "Optional: What to search for in chess history "
                                    "(e.g., 'Kasparov games', 'tactical puzzles', 'endgame positions'). "
                                    "Leave blank to get recent activity."
                                ),
                            }
                        },
                        "required": [],
                    },
                },
                {
                    "name": "start_watching_mode",
                    "description": ("Start automatically commenting on moves as they happen during live games"),
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
                    "name": "pause_playback",
                    "description": "Pause the currently playing chess content on TV",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            ]
        }
    ],
}


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
                if test_board.fen().split()[0] == new_board.fen().split()[0]:  # Compare just position
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
        commentary_text = "\n".join(self.commentary_lines) if self.commentary_lines else ""

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


class LiveChessCompanion(HDMITVCompanionWithTranscription):
    """Live Chess Companion - Adapts TV companion architecture for chess analysis"""

    def __init__(self):
        # Initialize TV companion base with chess config
        super().__init__()
        
        # Override config for chess
        self.config = CHESS_CONFIG
        
        # Chess-specific components
        self.vector_search = ChessVectorSearch()
        self.engine_pool = create_quick_analysis_pool(pool_size=4)
        
        # Position tracking
        self.current_position = None
        self.move_counter = 0
        self.max_position_duration = 120  # 2 minutes max per position
        
        # Replace scene detection with move detection  
        self.scene_detection_active = False  # Disable scene detection
        self.move_detection_active = False
        
        print("♟️  Live Chess Companion initialized")
        print("📊 Vector search ready with chess games database")
        print("🔧 Stockfish engine pool ready for analysis")

    async def detect_move_changes(self):
        """Replace scene detection with chess move detection"""
        print("♟️  Starting chess move detection...")
        
        # Wait for shared capture to be initialized
        while self.shared_cap is None:
            await asyncio.sleep(1)

        print("✅ HDMI capture ready for move detection")
        
        current_fen = None
        
        while self.shared_cap:
            try:
                ret, frame = self.shared_cap.read()
                if not ret:
                    print("⚠️  Failed to capture frame for move detection")
                    await asyncio.sleep(1)
                    continue

                # Save frame to temporary file for consensus detection
                temp_path = await self.save_frame_to_temp(frame)
                
                # Use consensus vision to detect position
                print("🔍 Running consensus position detection...")
                result = await consensus_piece_detection(temp_path, n=5, min_consensus=3)
                new_fen = result['consensus_fen']
                
                # Clean up temp file
                os.unlink(temp_path)

                # Check for position change and legal move
                if new_fen and new_fen != current_fen and self.is_legal_transition(current_fen, new_fen):
                    print(f"♟️  Move detected: {current_fen} -> {new_fen}")
                    await self.handle_new_move(current_fen, new_fen, frame)
                    current_fen = new_fen
                elif new_fen and not new_fen.startswith('Invalid'):
                    # Valid position but no change - update current if we didn't have one
                    if current_fen is None:
                        current_fen = new_fen
                        print(f"🎯 Initial position detected: {new_fen}")

                await asyncio.sleep(2)  # Check every 2 seconds (less frequent than TV)

            except Exception as e:
                print(f"❌ Move detection error: {e}")
                await asyncio.sleep(5)  # Wait longer on error

    async def save_frame_to_temp(self, frame) -> str:
        """Save video frame to temporary file for vision analysis"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
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
        print(f"📦 Finalizing move {move_package['move_number']}: {move_package.get('move_played', 'Unknown')}")

        if self.watching_mode:
            try:
                self.out_queue.put_nowait(move_package)
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
        
        print(f"♟️  Started analyzing move {self.move_counter}: {self.current_position.move_played}")

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
            query = self._create_position_query(position_buffer.position_features, position_buffer.engine_analysis)
            position_buffer.similar_positions = await self.vector_search.search(query, top_k=3)
            
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
                engine.analyse,
                board,
                chess.engine.Limit(time=0.5)
            )
            
            self.engine_pool.return_engine(engine)
            
            return {
                "evaluation": info.get("score", chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE)).relative.cp if info.get("score") else 0,
                "best_move": str(info.get("pv", [None])[0]) if info.get("pv") else None,
                "depth": info.get("depth", 0)
            }
            
        except Exception as e:
            print(f"❌ Engine analysis failed: {e}")
            return {"evaluation": 0, "best_move": None, "depth": 0}

    def _create_position_query(self, features: dict, engine_analysis: dict) -> str:
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
            if (self.current_position is not None and 
                time.time() - self.current_position.start_time > self.max_position_duration):

                print(f"⏱️  Position {self.current_position.move_number} exceeded "
                      f"{self.max_position_duration}s, finalizing...")
                await self._finalize_current_position()

                # Don't start new position - wait for actual move detection
                self.current_position = None

            await asyncio.sleep(15)  # Check every 15 seconds

    async def handle_tool_call(self, tool_call):
        """Handle chess-specific tool calls (extends parent class)"""
        function_responses = []

        for fc in tool_call.function_calls:
            print(f"\n🔧 Chess tool call: {fc.name}")
            print(f"   Args: {fc.args}")

            if fc.name == "search_similar_positions":
                query = fc.args.get("query", "")
                fen = fc.args.get("fen", "")
                
                print(f"📚 Searching similar positions: {query}")
                
                try:
                    search_results = await self.vector_search.search(query, top_k=5)
                    
                    # Format results for model
                    results_data = []
                    for result in search_results:
                        results_data.append({
                            "similarity": result.similarity,
                            "players": f"{result.metadata['white_player']} vs {result.metadata['black_player']}",
                            "game_phase": result.metadata["game_phase"],
                            "evaluation": result.metadata["stockfish_eval"],
                            "description": result.description[:200],
                            "strategic_themes": result.strategic_themes,
                            "fen": result.fen
                        })
                    
                    result = {
                        "query": query,
                        "results_found": len(results_data),
                        "similar_positions": results_data
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
                        "status": "analysis_complete"
                    }
                else:
                    result = {
                        "status": "no_position",
                        "message": "No current position detected"
                    }

            else:
                # Fall back to parent class for standard TV tools
                return await super().handle_tool_call(tool_call)

            function_responses.append(
                {"id": fc.id, "name": fc.name, "response": result}
            )

        # Send tool responses using parent method
        if function_responses:
            await self.session.send_tool_response(function_responses=function_responses)

    async def run(self):
        """Main chess companion loop - extends parent run method"""
        print("♟️  Starting Live Chess Companion...")
        print("🎧 Make sure to use headphones to prevent audio feedback!")
        print("💡 Type 'q' to quit")
        print("🎯 Chess move detection and analysis ready")

        try:
            async with asyncio.TaskGroup() as tg:
                # Use parent class setup but with chess config
                async with self.client.aio.live.connect(model=self.MODEL, config=self.config) as session:
                    self.session = session
                    self.audio_in_queue = asyncio.Queue()
                    self.out_queue = asyncio.Queue(maxsize=20)

                    # Start parent class tasks
                    send_text_task = tg.create_task(self.send_text())
                    tg.create_task(self.send_realtime())
                    tg.create_task(self.listen_user_audio())
                    tg.create_task(self.transcribe_tv_audio())
                    
                    # Replace scene detection with move detection
                    tg.create_task(self.detect_move_changes())  # Chess-specific
                    tg.create_task(self.monitor_position_duration())  # Chess-specific
                    
                    tg.create_task(self.receive_audio())
                    tg.create_task(self.play_audio())

                    await send_text_task
                    raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            print("👋 Live Chess Companion stopped")
        except Exception as e:
            traceback.print_exception(e)
        finally:
            # Clean up chess-specific resources
            if hasattr(self, 'engine_pool'):
                self.engine_pool.cleanup()
            
            # Parent cleanup
            if self.mic_stream:
                self.mic_stream.close()
            if self.pya:
                self.pya.terminate()


if __name__ == "__main__":
    companion = LiveChessCompanion()
    asyncio.run(companion.run())
