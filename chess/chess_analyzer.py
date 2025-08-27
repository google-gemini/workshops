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

"""Chess Analysis Engine - Isolated chess analysis logic

Provides comprehensive chess position analysis including:
- Stockfish engine evaluation (both perspectives)  
- Vector search through historical games database
- LLM-enhanced position descriptions
- Broadcast context extraction
- User query interpretation

Separated from streaming/live model orchestration for modularity.
"""

import asyncio
import base64
import io
import json
import traceback
from datetime import datetime
from typing import Dict, List, Optional

import chess
import chess.engine
import cv2
import numpy as np
from PIL import Image
from google import genai
from google.genai import types
from position_features import extract_position_features
from vector_search import ChessVectorSearch, SearchResult


class ChessAnalyzer:
    """Comprehensive chess analysis engine"""
    
    def __init__(self, vector_search: ChessVectorSearch, engine_pool, client: genai.Client):
        self.vector_search = vector_search
        self.engine_pool = engine_pool
        self.client = client
        print("🧠 Chess analyzer initialized")
    
    async def analyze_both_perspectives(
        self, 
        fen: str, 
        frame=None, 
        commentary_context: List[str] = None
    ) -> dict:
        """Run parallel white + black analysis, return both perspectives"""
        
        print(f"🧠 Analyzing both perspectives for {fen[:30]}...")
        
        white_analysis, black_analysis = await asyncio.gather(
            self.analyze_position(fen, "white", frame, commentary_context),
            self.analyze_position(fen, "black", frame, commentary_context)
        )
        
        return {
            "white": white_analysis,
            "black": black_analysis
        }
    
    async def analyze_position(
        self, 
        fen: str, 
        color: str,  # "white" or "black"
        frame=None,
        commentary_context: List[str] = None,
        user_query: str = None
    ) -> dict:
        """Complete analysis package ready for Gemini Live"""
        
        analysis_type = "user_query" if user_query else "background_monitoring"
        print(f"🔍 Analyzing position ({color} perspective, {analysis_type}): {fen[:30]}...")
        
        try:
            # Parallel execution of core analysis components
            stockfish_task = asyncio.create_task(
                self._get_stockfish_analysis_database_format(fen, color)
            )
            vector_task = asyncio.create_task(self._get_simple_similar_games(fen))
            
            # Create position entry in database format
            position_entry = {
                "fen": fen,
                "perspective": color,
                "move_number": None,  # Unknown for live positions
                "last_move": None,  # Could try to infer later
                "game_context": {},  # Empty for live
                "position_features": extract_position_features(fen),
                "timestamp": datetime.now().isoformat(),
                "commentary": list(commentary_context) if commentary_context else [],
                "user_query": user_query,
                "analysis_type": analysis_type,
                "move_context": color,
            }
            
            # Add screenshot if available
            if frame is not None:
                try:
                    position_entry["board_screenshot"] = self._convert_frame_to_base64(frame)
                except Exception as e:
                    print(f"❌ Screenshot error: {e}")
            
            # Gather analysis results
            stockfish_analysis = await stockfish_task
            similar_games = await vector_task
            
            # Store results in position entry
            position_entry["stockfish_analysis"] = stockfish_analysis
            position_entry["similar_positions"] = similar_games
            
            # Compute PV final evaluation for richer analysis
            pv = stockfish_analysis.get("principal_variation", [])
            if pv and len(pv) > 1:
                try:
                    # Use the analysis perspective color
                    starting_color = color
                    pv_final_eval = await self._evaluate_after_pv(fen, pv[:4], starting_color)
                    position_entry["stockfish_analysis"]["pv_final_evaluation"] = pv_final_eval
                    print(f"✅ PV final evaluation computed: {pv_final_eval:+.1f}")
                except Exception as e:
                    print(f"⚠️ PV final evaluation failed: {e}")
            
            # Generate LLM-enhanced description
            enhanced_desc = await self._generate_enhanced_description(position_entry)
            position_entry["enhanced_description"] = enhanced_desc
            
            # Format for Gemini Live
            position_entry["formatted_for_gemini"] = self._format_for_live_model(position_entry)
            
            print(f"✅ {color.title()} perspective analysis complete")
            return position_entry
            
        except Exception as e:
            print(f"❌ Analysis error for {color}: {e}")
            traceback.print_exc()
            return self._create_error_analysis(fen, color, str(e))
    
    async def determine_query_perspective(
        self, 
        user_query: str, 
        broadcast_context: dict
    ) -> str:
        """Determine who the user is asking about - return 'white' or 'black'"""
        try:
            print(f"🎯 Determining query perspective for: '{user_query}'")
            print(f"🎯 Broadcast context received: {json.dumps(broadcast_context, indent=2)}")
            
            prompt = f"""User question: "{user_query}"

Broadcast context: {json.dumps(broadcast_context, indent=2)}

Who is the user asking about? Return just "white" or "black" based on which player they mention.

Examples:
- "What should Magnus do?" + Magnus is black in broadcast → return "black"
- "What should Alireza play?" + Alireza is white in broadcast → return "white"
- "What's the best move?" → return "white" (default)
"""
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.0-flash-lite",
                contents=[prompt]
            )
            
            color = response.text.strip().lower()
            final_result = color if color in ["white", "black"] else "white"
            print(f"🎯 Final query perspective determined: {final_result}")
            return final_result
            
        except Exception as e:
            print(f"❌ Query perspective determination failed: {e}")
            return "white"  # Safe fallback
    
    async def _get_stockfish_analysis_database_format(self, fen: str, move_context: str) -> dict:
        """Get Stockfish analysis with fresh engine each time"""
        engine = None
        try:
            print(f"🔍 DEBUG: Input FEN: '{fen}'")
            print(f"🔍 DEBUG: Move context: '{move_context}'")
            
            # Create fresh engine every time - no pool corruption possible
            print("🆕 Creating fresh Stockfish engine...")
            engine = await asyncio.to_thread(
                chess.engine.SimpleEngine.popen_uci, "stockfish"
            )
            
            # Build complete FEN with determined turn
            if move_context and move_context in ["white", "black"]:
                active_color = 'w' if move_context == 'white' else 'b'
                fen_to_analyze = f"{fen} {active_color} - - 0 1"  # No castling rights to avoid crashes
                print(f"🔧 Built FEN for {move_context}: '{fen_to_analyze}'")
            else:
                # Fallback to white to move
                fen_to_analyze = f"{fen} w - - 0 1"  # No castling rights to avoid crashes
                print(f"🔧 Using fallback FEN (white to move): '{fen_to_analyze}'")
            
            # DEBUG: Test FEN validity before sending to Stockfish
            try:
                test_board = chess.Board(fen_to_analyze)
                print(f"✅ FEN validation passed")
            except Exception as fen_error:
                print(f"❌ INVALID FEN: {fen_error}")
                return {"evaluation": 0.0, "evaluation_type": "error", "error": f"Invalid FEN: {fen_error}"}
            
            board = chess.Board(fen_to_analyze)
            print(f"🔍 DEBUG: About to call engine.analyse with fresh engine")
            
            # Quick analysis (0.5 seconds)
            info = await asyncio.to_thread(
                engine.analyse, board, chess.engine.Limit(time=0.5)
            )
            
            print(f"✅ Fresh engine analysis completed successfully")
            
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
            
            analysis = {
                "evaluation": eval_score,
                "evaluation_type": eval_type,
                "mate_in": mate_in,
                "best_move": str(best_move) if best_move else None,
                "best_move_san": best_move_san,
                "principal_variation": [str(move) for move in info.get("pv", [])[:5]],
                "depth": info.get("depth"),
                "nodes": info.get("nodes"),
                "time": info.get("time"),
                "analysis_perspective": move_context,
                "requested_for": move_context,
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Fresh engine analysis failed: {e}")
            return {
                "evaluation": 0.0,
                "evaluation_type": "error",
                "error": str(e),
            }
        finally:
            # Always clean up the fresh engine
            if engine:
                try:
                    engine.quit()
                    print("🗑️ Fresh engine cleaned up")
                except Exception as cleanup_error:
                    print(f"⚠️ Engine cleanup failed: {cleanup_error}")
    
    async def _get_simple_similar_games(self, fen: str):
        """Get vector search with just game outcomes for passing mention"""
        try:
            features = extract_position_features(fen)
            query = self._create_position_query(features, {})
            print(f"🔍 Vector search query: '{query}'")
            
            results = await self.vector_search.search(query, top_k=3)
            print(f"📚 Found {len(results)} similar games")
            
            # Simple format: just mention games and outcomes
            simple_results = []
            for result in results:
                white = result.metadata.get("white_player", "Unknown")
                black = result.metadata.get("black_player", "Unknown")
                outcome = result.metadata.get("result", "*")
                simple_results.append({
                    "game": f"{white} vs {black}",
                    "result": outcome,
                    "similarity": result.similarity,
                })
            return simple_results
            
        except Exception as e:
            print(f"⚠️ Similar games search failed: {e}")
            return []
    
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
    
    async def _extract_broadcast_context(self, frame) -> dict:
        """Extract broadcast context - runs single model call for all context"""
        try:
            frame_data = self._convert_frame_to_base64(frame)
            
            print("🎥 Running full parallel color + rich context detection...")
            
            # Dispatch both requests in parallel (always run fresh detection)
            # color_task = asyncio.create_task(self._extract_player_colors(frame_data))
            context_task = asyncio.create_task(self._extract_rich_context(frame_data))
            
            # color_result, context_result = await asyncio.gather(color_task, context_task)
            context_result = await context_task
            
            # DEBUG: Show what each model returned
            # print(f"🔍 COLOR ASSIGNMENT MODEL RETURNED:")
            # print(json.dumps(color_result, indent=2))
            # if color_result.get("thinking"):
            #     print(f"🧠 MODEL REASONING: {color_result['thinking']}")
            print(f"🔍 RICH CONTEXT MODEL RETURNED:")
            print(json.dumps(context_result, indent=2))
            
            # Merge results - color assignment takes priority
            merged_result = context_result.copy() if context_result else {}
            
            print(f"🔍 FINAL RESULT:")
            print(json.dumps(merged_result, indent=2))
            
            print(f"🎥 Broadcast context extracted from single model call")
            return merged_result
            
        except Exception as e:
            print(f"⚠️ Broadcast context extraction failed: {e}")
            return {}
    

    async def _extract_rich_context(self, frame_data) -> dict:
        """Rich broadcast context extraction including player color assignment"""
        try:
            prompt = """Look at this chess broadcast and extract what you can clearly see:

1. Which player is White and which is Black
2. Any other broadcast details that are clearly visible

Return JSON:
{
  "structured_data": {
    "players": {"white": "Player Name", "black": "Player Name"},
    "ratings": {"white": 2650, "black": 2700},
    "times": {"white": "05:30", "black": "03:45"},
    "heart_rates": {"white": 95, "black": 88},
    "event": "Tournament/Match Name",
    "round": "Round 3", 
    "score": "2.5-1.5"
  },
  "additional_context": "Brief description of other notable broadcast elements"
}

IMPORTANT: Only include fields you can actually see clearly displayed. Omit any field (including players) if you can't determine it with confidence. Don't guess ratings, times, or heart rates."""
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.0-flash-lite",
                contents=[
                    types.Part.from_bytes(
                        data=base64.b64decode(frame_data["data"]),
                        mime_type=frame_data["mime_type"],
                    ),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            print(f"⚠️ Rich context extraction failed: {e}")
            return {}
    
    async def _generate_enhanced_description(self, position_entry: dict) -> dict:
        """Generate LLM-enhanced position description"""
        try:
            # Use existing description generator
            from chess_description_generator import enhance_single_position_with_retry, ChessDescriptionGenerator
            
            generator = ChessDescriptionGenerator()
            chain = generator.create_description_chain()
            semaphore = asyncio.Semaphore(1)
            
            # Include commentary context for better descriptions
            if position_entry.get("commentary"):
                recent_commentary = " ".join(position_entry["commentary"][-3:])
                position_entry["live_commentary"] = recent_commentary
            
            # Include user query in LLM context if provided
            user_query = position_entry.get("user_query")
            if user_query:
                position_entry["query_context"] = (
                    f"USER QUESTION: {user_query}\nPlease focus your analysis on"
                    " answering this specific question while providing comprehensive"
                    " position evaluation."
                )
            
            _, enhanced_desc, error = await enhance_single_position_with_retry(
                (position_entry, 0), generator, chain, semaphore
            )
            
            if enhanced_desc and not error:
                print(f"✅ LLM description generated")
                return enhanced_desc
            else:
                print(f"⚠️ LLM description failed, using template: {error}")
                # Fallback to template description
                from build_database import generate_quick_description
                return {
                    "description": generate_quick_description(position_entry),
                    "strategic_themes": [],
                    "tactical_elements": [],
                    "key_squares": [],
                    "generated_by": "template-fallback",
                }
                
        except Exception as e:
            print(f"❌ Enhanced description failed: {e}")
            return {"description": "Position analysis unavailable", "generated_by": "error"}
    
    def _format_for_live_model(self, database_entry: dict) -> str:
        """Format complete database entry for Gemini Live"""
        
        # Check if this is a user query-driven analysis
        user_query = database_entry.get("user_query")
        
        # Use the rich LLM description as primary content
        enhanced = database_entry.get("enhanced_description", {})
        description = enhanced.get("description", "Position analysis unavailable")
        
        # Header varies based on analysis type
        if user_query:
            text = f"""FRESH POSITION ANALYSIS

USER QUERY: {user_query}

CURRENT POSITION ANALYSIS:
{description}"""
        else:
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
            eval_score = engine.get("evaluation", 0)
            eval_type = engine.get("evaluation_type", "cp")
            best_move = engine.get("best_move_san", "?")
            
            if eval_type == "mate":
                mate_in = engine.get("mate_in", "?")
                eval_text = f"Mate in {mate_in}"
            else:
                eval_text = f"{eval_score:+.1f}"
            
            text += f"\nENGINE ANALYSIS: {eval_text}, best move: {best_move}"
            
            # Add principal variation with final evaluation if available
            pv = engine.get("principal_variation", [])
            if pv and len(pv) > 1:
                pv_moves = " ".join(pv[:4])  # Show first 4 moves
                pv_final = engine.get("pv_final_evaluation")
                
                if pv_final is not None:
                    text += f"\nPrincipal variation: {pv_moves} → {pv_final:+.1f}"
                else:
                    text += f"\nPrincipal variation: {pv_moves}"
            
            # Add move context if available  
            move_context = database_entry.get("move_context")
            if move_context and move_context in ["white", "black"]:
                text += f"\nANALYSIS PERSPECTIVE: {move_context.title()} to move"
        
        # Simple similar games mention
        similar = database_entry.get("similar_positions", [])
        if similar:
            text += f"\n\nSIMILAR MASTER GAMES: "
            mentions = []
            for game in similar[:2]:  # Top 2 games
                result_emoji = {"1-0": "1-0", "0-1": "0-1", "1/2-1/2": "½-½"}.get(
                    game.get("result", "*"), game.get("result", "*")
                )
                mentions.append(f"{game['game']} ({result_emoji})")
            text += ", ".join(mentions)
        
        # Always include recent commentary - no filtering!
        commentary = database_entry.get("commentary", [])
        if commentary:
            # Just take last 3 comments, full text
            recent_comments = commentary[-3:] if len(commentary) >= 3 else commentary
            commentary_text = "\n".join(recent_comments)  # Each on separate line
            text += f"\n\nLIVE COMMENTARY:\n{commentary_text}"
        
        # Add broadcast context for human drama and stakes
        broadcast = database_entry.get("broadcast_context", {})
        if broadcast:
            text += f"\n\nBROADCAST CONTEXT:\n"
            text += f"{json.dumps(broadcast, indent=2)}\n"
        
        # Add explicit request for commentary with context awareness
        context_instruction = ""
        if broadcast:
            context_instruction = (
                " Consider both the chess position and the broadcast context (time"
                " pressure, match stakes, player condition) in your analysis."
            )
        
        if user_query:
            text += (
                "\n\nPlease provide your expert analysis focusing specifically on"
                f" the user's question: '{user_query}'. Include broader chess"
                f" insights as relevant.{context_instruction}"
            )
        else:
            text += (
                "\n\nPlease provide your expert chess commentary on this position."
                " What should players be thinking about? What are the key plans and"
                f" ideas?{context_instruction}"
            )
        
        return text
    
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
            
            return {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode(),
            }
        except Exception as e:
            print(f"❌ Frame conversion failed: {e}")
            raise
    
    async def analyze_hypothetical_move(
        self, 
        current_fen: str, 
        move_description: str
    ) -> dict:
        """Analyze what happens if a specific move is played"""
        try:
            print(f"🤔 Analyzing hypothetical move: '{move_description}' from {current_fen[:30]}...")
            
            # Step 1: Parse the move description to algebraic notation
            parsed_move = await self._parse_move_description(move_description, current_fen)
            if not parsed_move:
                return {"error": f"Could not parse move: {move_description}"}
            
            print(f"📝 Parsed move: {move_description} → {parsed_move}")
            
            # Step 2: Apply the move to current position
            board = chess.Board(f"{current_fen} w KQkq - 0 1")  # Assume white to move for now
            
            # Try to parse and apply the move
            try:
                move = board.parse_san(parsed_move)
                board.push(move)
                new_fen = board.fen().split()[0]  # Just the position part
                print(f"✅ Move applied successfully: {current_fen[:20]}... → {new_fen[:20]}...")
            except ValueError as e:
                # Try with black to move
                try:
                    board = chess.Board(f"{current_fen} b KQkq - 0 1")
                    move = board.parse_san(parsed_move)
                    board.push(move)
                    new_fen = board.fen().split()[0]
                    print(f"✅ Move applied (black to move): {current_fen[:20]}... → {new_fen[:20]}...")
                except ValueError:
                    return {"error": f"Invalid move '{parsed_move}' for current position"}
            
            # Step 3: Get full analysis for both positions to compare PVs
            current_analysis_task = self._get_stockfish_analysis_database_format(current_fen, "white")  # Default perspective
            new_analysis_task = self._get_stockfish_analysis_database_format(new_fen, "black")  # Opposite perspective after move
            
            current_analysis, new_analysis = await asyncio.gather(current_analysis_task, new_analysis_task)
            
            # Step 4: Calculate evaluation change
            current_eval = current_analysis.get("evaluation", 0.0)
            new_eval = new_analysis.get("evaluation", 0.0)
            evaluation_change = new_eval - current_eval
            
            # Step 5: Generate human-readable analysis
            analysis_text = await self._format_hypothetical_analysis(
                move_description=move_description,
                parsed_move=parsed_move,
                current_eval=current_eval,
                new_eval=new_eval,
                evaluation_change=evaluation_change,
                current_analysis=current_analysis,
                new_analysis=new_analysis,
                current_fen=current_fen,
                new_fen=new_fen
            )
            
            return {
                "analysis": analysis_text,
                "parsed_move": parsed_move,
                "current_evaluation": current_eval,
                "new_evaluation": new_eval,
                "evaluation_change": evaluation_change,
                "assessment": "good" if evaluation_change > 0 else ("neutral" if abs(evaluation_change) < 0.2 else "questionable"),
                "best_move_after": new_analysis.get("best_move_san"),
                "principal_variation": new_analysis.get("principal_variation", []),
                "current_best_move": current_analysis.get("best_move_san"),
                "current_principal_variation": current_analysis.get("principal_variation", [])
            }
            
        except Exception as e:
            print(f"❌ Hypothetical move analysis failed: {e}")
            traceback.print_exc()
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def _parse_move_description(self, move_description: str, current_fen: str) -> str:
        """Parse natural language move description to algebraic notation"""
        try:
            prompt = f"""Current chess position (piece positions only): {current_fen}

Convert this move description to standard algebraic notation:
"{move_description}"

Examples:
- "rook to e8" → "Re8"
- "takes the pawn on e5" → "Nxe5" (if knight can take)
- "castles kingside" → "O-O"
- "queen to d4" → "Qd4"
- "knight f3" → "Nf3"

Return ONLY the move in algebraic notation, nothing else."""

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.0-flash-lite",
                contents=[prompt]
            )
            
            parsed_move = response.text.strip()
            print(f"🔍 Move parsing: '{move_description}' → '{parsed_move}'")
            return parsed_move
            
        except Exception as e:
            print(f"❌ Move parsing failed: {e}")
            return None
    
    async def _get_quick_stockfish_evaluation(self, fen: str) -> float:
        """Get quick Stockfish evaluation with fresh engine"""
        engine = None
        try:
            # Create fresh engine for quick evaluation
            print("🆕 Creating fresh engine for quick evaluation...")
            engine = await asyncio.to_thread(
                chess.engine.SimpleEngine.popen_uci, "stockfish"
            )
            
            # Build FEN with white to move (simple assumption)
            board = chess.Board(f"{fen} w - - 0 1")  # No castling rights
            
            # Very quick analysis (0.2 seconds)
            info = await asyncio.to_thread(
                engine.analyse, board, chess.engine.Limit(time=0.2)
            )
            
            # Extract just the evaluation number
            score = info["score"].white()
            if score.is_mate():
                return 10000 if score.mate() > 0 else -10000
            else:
                return score.score() / 100.0  # Convert centipawns to pawns
                
        except Exception as e:
            print(f"❌ Fresh quick evaluation failed: {e}")
            return 0.0
        finally:
            # Always clean up the fresh engine
            if engine:
                try:
                    engine.quit()
                    print("🗑️ Fresh quick evaluation engine cleaned up")
                except Exception as cleanup_error:
                    print(f"⚠️ Quick evaluation cleanup failed: {cleanup_error}")
    
    async def _format_hypothetical_analysis(
        self, 
        move_description: str,
        parsed_move: str,
        current_eval: float,
        new_eval: float,
        evaluation_change: float,
        current_analysis: dict = None,
        new_analysis: dict = None,
        current_fen: str = None,
        new_fen: str = None
    ) -> str:
        """Format hypothetical move analysis for human reading"""
        
        # Format evaluation numbers
        def format_eval(eval_val):
            if abs(eval_val) > 50:
                return f"Mate in {int(abs(eval_val) / 1000)}"
            else:
                return f"{eval_val:+.1f}"
        
        current_eval_str = format_eval(current_eval)
        new_eval_str = format_eval(new_eval)
        
        # Determine move quality
        if evaluation_change > 0.5:
            quality = "excellent"
        elif evaluation_change > 0.2:
            quality = "good" 
        elif evaluation_change > -0.2:
            quality = "neutral"
        elif evaluation_change > -0.5:
            quality = "questionable"
        else:
            quality = "poor"
        
        analysis = f"""HYPOTHETICAL MOVE ANALYSIS

Move: {move_description} ({parsed_move})

EVALUATION IMPACT:
• Current position: {current_eval_str}
• After {parsed_move}: {new_eval_str}
• Change: {evaluation_change:+.2f}

ASSESSMENT: This appears to be a {quality} move."""

        if abs(evaluation_change) < 0.1:
            analysis += " The evaluation remains essentially unchanged."
        elif evaluation_change > 0:
            analysis += f" The position improves by {evaluation_change:.2f}, indicating this is a strong choice."
        else:
            analysis += f" The position worsens by {abs(evaluation_change):.2f}, suggesting this may not be optimal."
        
        # Add principal variation comparison with final evaluations
        if current_analysis and new_analysis and current_fen and new_fen:
            current_pv = current_analysis.get("principal_variation", [])
            current_best = current_analysis.get("best_move_san")
            new_pv = new_analysis.get("principal_variation", [])
            new_best = new_analysis.get("best_move_san")
            
            analysis += f"\n\nPOSITION COMPARISON:"
            
            if current_best and current_pv and len(current_pv) > 1:
                current_line = " ".join(current_pv[:4])
                # Get evaluation after current PV
                current_pv_final_eval = asyncio.create_task(
                    self._evaluate_after_pv(current_fen, current_pv[:4], "white")
                )
                analysis += f"\n• Current best line: {current_best} {current_line}"
            
            if new_best and new_pv and len(new_pv) > 1:
                new_line = " ".join(new_pv[:4])
                # Get evaluation after new PV  
                new_pv_final_eval = asyncio.create_task(
                    self._evaluate_after_pv(new_fen, new_pv[:4], "black")
                )
                analysis += f"\n• After {parsed_move}: {new_best} {new_line}"
            
            # Wait for PV evaluations and add them
            try:
                if 'current_pv_final_eval' in locals():
                    current_final = await current_pv_final_eval
                    analysis = analysis.replace(
                        f"Current best line: {current_best} {current_line}",
                        f"Current best line: {current_best} {current_line} → {current_final:+.1f}"
                    )
                
                if 'new_pv_final_eval' in locals():
                    new_final = await new_pv_final_eval
                    analysis = analysis.replace(
                        f"After {parsed_move}: {new_best} {new_line}",
                        f"After {parsed_move}: {new_best} {new_line} → {new_final:+.1f}"
                    )
                    
                    # Add long-term assessment
                    if 'current_pv_final_eval' in locals():
                        pv_eval_change = new_final - current_final
                        if abs(pv_eval_change) > 0.3:
                            if pv_eval_change > 0:
                                assessment = "The hypothetical move leads to better long-term prospects after best play."
                            else:
                                assessment = "The hypothetical move leads to complications that favor the opponent after best play."
                            analysis += f"\n\nLONG-TERM ASSESSMENT: {assessment}"
                        
            except Exception as e:
                print(f"⚠️ PV evaluation failed: {e}")
                
        elif new_analysis:
            # Fallback to old format if current analysis missing
            best_move = new_analysis.get("best_move_san")
            pv = new_analysis.get("principal_variation", [])
            
            analysis += f"\n\nRESULTING POSITION:"
            if best_move:
                analysis += f"\n• Engine recommends: {best_move}"
            
            if pv and len(pv) > 1:
                pv_moves = " ".join(pv[:4])
                analysis += f"\n• Best continuation: {pv_moves}"
        
        return analysis
    
    async def _evaluate_after_pv(self, starting_fen: str, pv_moves: list, starting_color: str) -> float:
        """Play out principal variation and evaluate the final position"""
        try:
            # Construct proper FEN with starting color
            color_char = 'w' if starting_color == 'white' else 'b'
            full_fen = f"{starting_fen} {color_char} KQkq - 0 1"
            board = chess.Board(full_fen)
            
            # Play out the PV moves
            moves_played = 0
            for move_str in pv_moves:
                if moves_played >= 4:  # Limit to first 4 moves
                    break
                try:
                    board.push_san(move_str)
                    moves_played += 1
                except ValueError:
                    # If move can't be played, stop here
                    break
            
            # Quick evaluation of final position
            final_eval = await self._get_quick_stockfish_evaluation(board.fen().split()[0])
            print(f"🔍 PV evaluation: {' '.join(pv_moves[:moves_played])} → {final_eval:+.1f}")
            return final_eval
            
        except Exception as e:
            print(f"❌ PV evaluation failed: {e}")
            return 0.0

    def _create_error_analysis(self, fen: str, color: str, error_msg: str) -> dict:
        """Create error analysis entry"""
        return {
            "fen": fen,
            "perspective": color,
            "error": error_msg,
            "stockfish_analysis": {"evaluation": 0.0, "evaluation_type": "error"},
            "similar_positions": [],
            "broadcast_context": {},
            "enhanced_description": {"description": f"Analysis failed: {error_msg}"},
            "formatted_for_gemini": f"🚫 ANALYSIS ERROR ({color}): {error_msg}",
        }
