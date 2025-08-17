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
            
            # Broadcast context extraction (if frame provided)
            broadcast_task = None
            if frame is not None:
                broadcast_task = asyncio.create_task(
                    self._extract_broadcast_context(frame)
                )
            
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
            results = []
            results.append(await stockfish_task)  # Stockfish analysis
            results.append(await vector_task)    # Similar games
            
            if broadcast_task:
                results.append(await broadcast_task)  # Broadcast context
            else:
                results.append({})
            
            # Store results in position entry
            position_entry["stockfish_analysis"] = results[0]
            position_entry["similar_positions"] = results[1]
            position_entry["broadcast_context"] = results[2]
            
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
            print(f"🎯 Query perspective determined: {final_result}")
            return final_result
            
        except Exception as e:
            print(f"❌ Query perspective determination failed: {e}")
            return "white"  # Safe fallback
    
    async def _get_stockfish_analysis_database_format(self, fen: str, move_context: str) -> dict:
        """Get Stockfish analysis in database format"""
        try:
            engine = self.engine_pool.get_engine()
            
            # Build complete FEN with determined turn
            if move_context and move_context in ["white", "black"]:
                active_color = 'w' if move_context == 'white' else 'b'
                fen_to_analyze = f"{fen} {active_color} KQkq - 0 1"
                print(f"🔧 Built FEN for {move_context}: {fen_to_analyze}")
            else:
                # Fallback to white to move
                fen_to_analyze = f"{fen} w KQkq - 0 1"
                print(f"🔧 Using fallback FEN (white to move): {fen_to_analyze}")
            
            board = chess.Board(fen_to_analyze)
            
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
            print(f"❌ Engine analysis failed: {e}")
            return {
                "evaluation": 0.0,
                "evaluation_type": "error",
                "error": str(e),
            }
    
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
        """Extract broadcast context using separate vision model"""
        try:
            frame_data = self._convert_frame_to_base64(frame)
            
            prompt = """Analyze this chess broadcast and extract relevant context for commentary.

PRIORITIZE IF VISIBLE:
- Tournament/match information
- Player time remaining  
- Match scores/game significance
- Player stress indicators (heart rates, expressions)
- Ratings or titles

THEN DESCRIBE any other notable broadcast elements that would help a commentator understand:
- The stakes and pressure level
- Human drama or storyline
- Technical broadcast details worth mentioning

Return as JSON with 'structured_data' for key fields and 'additional_context' for everything else:

{
  "structured_data": {
    "players": {"white": "Player Name", "black": "Player Name"},
    "times": {"white": "mm:ss", "black": "mm:ss"},
    "heart_rates": {"white": 95, "black": 88},
    "match_info": "Tournament name, game significance",
    "ratings": {"white": 2650, "black": 2700}
  },
  "additional_context": "Free-form description of other notable elements, broadcast-specific features, atmosphere, human drama, etc."
}

Only include what's clearly visible. Omit fields rather than guessing."""
            
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
            
            context = json.loads(response.text)
            print(f"🎥 Broadcast context extracted successfully")
            return context
            
        except Exception as e:
            print(f"⚠️ Broadcast context extraction failed: {e}")
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
