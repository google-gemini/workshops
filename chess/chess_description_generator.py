from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List, Optional
import json
import asyncio
import concurrent.futures
from pathlib import Path
import os
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class ChessPositionDescription(BaseModel):
    """Enhanced chess position description"""
    description: str = Field(description="Rich natural language description suitable for vector search")
    strategic_themes: List[str] = Field(description="Key strategic concepts", default_factory=list)
    tactical_elements: List[str] = Field(description="Tactical motifs present", default_factory=list)
    key_squares: List[str] = Field(description="Important squares in the position", default_factory=list)

class ChessDescriptionGenerator:
    def __init__(self):
        # Configure safety settings - Gemini is way too aggressive for chess content
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        # Use Flash-Lite for cost efficiency
        gemini_kwargs = {
            "model": "gemini-2.0-flash-lite",
            "temperature": 0.3,
            "max_output_tokens": 400,
            "safety_settings": safety_settings
        }
        
        # Add API key explicitly if available
        if "GOOGLE_API_KEY" in os.environ:
            gemini_kwargs["google_api_key"] = os.environ["GOOGLE_API_KEY"]
            
        self.model = ChatGoogleGenerativeAI(**gemini_kwargs)
        
    def create_description_chain(self):
        """Create LangChain chain for chess descriptions"""
        
        prompt_template = ChatPromptTemplate.from_template("""
You are a chess grandmaster creating rich, searchable descriptions of chess positions.

POSITION DATA:
- FEN: {fen}
- Last move: {last_move} (move {move_number})
- To move: {to_move}
- Game phase: {game_phase}

COMPUTER ANALYSIS:
- Stockfish evaluation: {evaluation} ({evaluation_type})
- Best move: {best_move}
- Alternative moves: {alternatives}

POSITION FEATURES:
- Material: {material_description}
- King safety: {king_safety_description}  
- Board control: {board_control_description}
- Pawn structure: {pawn_structure_description}
- Piece activity: {piece_activity_description}

GAME CONTEXT:
- Players: {white_player} vs {black_player}
- Tournament: {event}
- Opening: {eco}

EXPERT COMMENTARY (from historical games):
{expert_commentary}

LIVE COMMENTARY CONTEXT:
{live_commentary}

Create a rich 3-4 sentence description that captures:
1. The strategic situation and key themes
2. Tactical opportunities and threats  
3. The critical decision points
4. Historical/opening context when relevant
5. **Incorporate expert commentary insights when available**

When expert commentary exists, weave those insights into your analysis. Expert commentary often contains move-specific insights, psychological context, and historical patterns that should enhance your systematic analysis.

Focus on concepts that would help find similar positions: piece coordination, pawn structures, tactical motifs, strategic plans, king safety issues, material imbalances, endgame techniques.

Make it engaging and educational - as if explaining to an intermediate player watching a live game.
""")

        # Use structured output like the translator
        structured_llm = self.model.with_structured_output(ChessPositionDescription)
        
        return prompt_template | structured_llm

    def format_position_data(self, position: dict) -> dict:
        """Format position data for the prompt"""
        
        features = position.get("position_features", {})
        context = position.get("game_context", {})
        analysis = position.get("stockfish_analysis", {})
        
        # Format material situation
        material = features.get("material", {})
        balance = material.get("balance", 0)
        if balance == 0:
            material_desc = "Material equal"
        elif balance > 0:
            material_desc = f"White ahead by {balance} points"
        else:
            material_desc = f"Black ahead by {abs(balance)} points"
            
        # Format evaluation
        eval_score = analysis.get("evaluation", 0)
        eval_type = analysis.get("evaluation_type", "cp")
        if eval_type == "mate":
            eval_desc = f"Mate in {analysis.get('mate_in', '?')}"
        else:
            eval_desc = f"{eval_score:+.1f}"
            
        # Format king safety
        king_safety = features.get("king_safety", {})
        castling = king_safety.get("castling_status", {})
        white_castled = castling.get("white_has_castled", False)
        black_castled = castling.get("black_has_castled", False)
        
        if white_castled and black_castled:
            king_desc = "Both kings castled"
        elif white_castled:
            king_desc = "White castled, Black king in center"
        elif black_castled:
            king_desc = "Black castled, White king in center"  
        else:
            king_desc = "Both kings in center"
            
        # Format board control
        board_control = features.get("board_control", {})
        open_files = board_control.get("open_files", [])
        if open_files:
            control_desc = f"Open files: {', '.join(open_files)}"
        else:
            control_desc = "No open files"
            
        return {
            "fen": position.get("fen", ""),
            "last_move": position.get("last_move", ""),
            "move_number": position.get("move_number", ""),
            "to_move": features.get("to_move", ""),
            "game_phase": features.get("game_phase", ""),
            "evaluation": eval_desc,
            "evaluation_type": eval_type,
            "best_move": analysis.get("best_move_san", ""),
            "alternatives": "Multiple options" if analysis.get("principal_variation") else "",
            "material_description": material_desc,
            "king_safety_description": king_desc,
            "board_control_description": control_desc,
            "pawn_structure_description": self.format_pawn_structure(features.get("pawn_structure", {})),
            "piece_activity_description": self.format_piece_activity(features.get("piece_activity", {})),
            "white_player": context.get("white_player", ""),
            "black_player": context.get("black_player", ""),
            "event": context.get("event", ""),
            "eco": context.get("eco", ""),
            "expert_commentary": self.format_expert_commentary(position),
            "live_commentary": position.get("live_commentary", "No commentary available")
        }
    
    def format_expert_commentary(self, position: dict) -> str:
        """Format expert commentary from PGN when available"""
        
        human_commentary = position.get("human_commentary", {})
        if not human_commentary:
            return "No expert commentary available for this position."
        
        commentary_parts = []
        
        # Add main commentary description
        if human_commentary.get("description"):
            commentary_parts.append(f"Expert analysis: {human_commentary['description']}")
        
        # Add strategic themes from expert
        expert_themes = human_commentary.get("strategic_themes", [])
        if expert_themes:
            commentary_parts.append(f"Expert identifies themes: {', '.join(expert_themes)}")
        
        # Add tactical elements from expert  
        expert_tactics = human_commentary.get("tactical_elements", [])
        if expert_tactics:
            commentary_parts.append(f"Expert notes tactical: {', '.join(expert_tactics)}")
            
        # Add raw commentary snippet for context
        raw_commentary = human_commentary.get("raw_commentary", "")
        if raw_commentary and len(raw_commentary.strip()) > 10:
            commentary_parts.append(f"Original annotation: \"{raw_commentary[:100]}...\"")
        
        return " | ".join(commentary_parts) if commentary_parts else "No expert commentary available for this position."
    
    def format_pawn_structure(self, pawn_structure: dict) -> str:
        """Format pawn structure into readable description"""
        elements = []
        
        doubled = pawn_structure.get("doubled_pawns", {})
        if doubled.get("white") or doubled.get("black"):
            elements.append("doubled pawns")
            
        isolated = pawn_structure.get("isolated_pawns", {})  
        if isolated.get("white") or isolated.get("black"):
            elements.append("isolated pawns")
            
        passed = pawn_structure.get("passed_pawns", {})
        if passed.get("white") or passed.get("black"):
            elements.append("passed pawns")
            
        return ", ".join(elements) if elements else "normal pawn structure"
    
    def format_piece_activity(self, piece_activity: dict) -> str:
        """Format piece activity into readable description"""
        active = piece_activity.get("active_pieces", [])
        trapped = piece_activity.get("trapped_pieces", [])
        
        if active and trapped:
            return f"Active: {', '.join(active[:2])}. Trapped: {', '.join(trapped[:2])}"
        elif active:
            return f"Active pieces: {', '.join(active[:3])}"
        elif trapped:
            return f"Trapped pieces: {', '.join(trapped[:2])}"
        else:
            return "Balanced piece activity"

async def enhance_single_position_with_retry(position_with_idx, generator, chain, semaphore):
    """Process a single position with error handling - async with semaphore"""
    position, idx = position_with_idx
    
    async with semaphore:  # Rate limiting
        try:
            prompt_data = generator.format_position_data(position)
            result = await chain.ainvoke(prompt_data)
            
            enhanced_description = {
                "description": result.description,
                "strategic_themes": result.strategic_themes,
                "tactical_elements": result.tactical_elements,
                "key_squares": result.key_squares,
                "generated_by": "gemini-2.0-flash-lite"
            }
            
            return (idx, enhanced_description, None)  # success
            
        except Exception as e:
            return (idx, None, str(e))  # error

async def enhance_database_with_descriptions(
    input_file: str = "chess_database.json",
    output_file: str = "chess_database_enhanced.json",
    max_concurrent: int = 10  # Rate limiting for API
):
    """Parallel enhancement with ThreadPoolExecutor pattern"""
    
    print("🎯 PARALLEL CHESS DATABASE ENHANCEMENT")
    print("=" * 60)
    
    # Load existing database
    print(f"📚 Loading {input_file}")
    with open(input_file, 'r') as f:
        positions = json.load(f)
    
    print(f"   ✓ Loaded {len(positions)} positions")
    print(f"   🚀 Using {max_concurrent} concurrent workers")
    
    # Initialize generator and chain
    generator = ChessDescriptionGenerator()
    chain = generator.create_description_chain()
    
    # Prepare positions with indices  
    positions_with_idx = [(pos, i) for i, pos in enumerate(positions)]
    
    # Process with ThreadPoolExecutor (similar to Stockfish pattern)
    enhanced_count = 0
    errors = 0
    completed = 0
    
    print(f"\n🤖 Generating descriptions with Gemini 2.0 Flash-Lite (async parallel)...")
    
    # Create semaphore for rate limiting
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # Create all tasks
    tasks = [
        enhance_single_position_with_retry(pos_data, generator, chain, semaphore)
        for pos_data in positions_with_idx
    ]
    
    # Process tasks with progress tracking
    for task in asyncio.as_completed(tasks):
        try:
            idx, enhanced_desc, error = await task
            
            if error:
                print(f"   ❌ Error enhancing position {idx+1}: {error}")
                errors += 1
            else:
                positions[idx]["enhanced_description"] = enhanced_desc
                enhanced_count += 1
                
                # Show samples every 10th completion
                if completed % 10 == 0:
                    print(f"\n   📝 Sample (position {idx+1}):")
                    print(f"      Game: {positions[idx]['game_context']['white_player']} vs {positions[idx]['game_context']['black_player']}")
                    print(f"      Move: {positions[idx]['move_number']} {positions[idx]['last_move']}")
                    print(f"      Description: {enhanced_desc['description']}")
                    print(f"      Themes: {', '.join(enhanced_desc['strategic_themes'])}")
                    if enhanced_desc['tactical_elements']:
                        print(f"      Tactical: {', '.join(enhanced_desc['tactical_elements'])}")
            
            completed += 1
            if completed % 25 == 0:
                print(f"   Progress: {completed}/{len(positions)} positions processed ({enhanced_count} success, {errors} errors)")
                
        except Exception as e:
            print(f"   ❌ Task execution error: {e}")
            errors += 1
    
    # Save enhanced database
    print(f"\n💾 Saving enhanced database to {output_file}")
    with open(output_file, 'w') as f:
        json.dump(positions, f, indent=2)
    
    print(f"\n🎉 PARALLEL ENHANCEMENT COMPLETE!")
    print(f"✓ {enhanced_count} positions enhanced")
    print(f"✓ {errors} errors")
    print(f"✓ Theoretical speedup: ~{min(max_concurrent, len(positions))}x")
    print(f"✓ Ready for vector embedding creation")
    
    # Cost estimate
    avg_input_tokens = 500  # Estimated
    avg_output_tokens = 250  # Estimated
    total_input_tokens = enhanced_count * avg_input_tokens
    total_output_tokens = enhanced_count * avg_output_tokens
    
    input_cost = (total_input_tokens / 1_000_000) * 0.075
    output_cost = (total_output_tokens / 1_000_000) * 0.30
    total_cost = input_cost + output_cost
    
    print(f"\n💰 Estimated cost: ${total_cost:.2f}")
    print(f"   Input: {total_input_tokens:,} tokens (${input_cost:.2f})")
    print(f"   Output: {total_output_tokens:,} tokens (${output_cost:.2f})")

if __name__ == "__main__":
    asyncio.run(enhance_database_with_descriptions())
