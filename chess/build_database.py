import asyncio
import json
from pathlib import Path
import sys
import chess.engine
import concurrent.futures
from typing import Optional
from parse_pgn import parse_pgn_to_positions
from position_features import extract_position_features
from stockfish_pool import create_deep_analysis_pool
from chess_description_generator import ChessDescriptionGenerator, enhance_single_position_with_retry


def analyze_single_position_with_pool(pos_with_idx, analysis_pool):
  """Analyze a single position using the provided engine pool"""
  position, idx = pos_with_idx
  engine = analysis_pool.get_engine()  # Blocks until engine available
  
  try:
    board = chess.Board(position["fen"])
    analysis = engine.analyse(board, chess.engine.Limit(depth=18))
    
    # Extract evaluation score
    score = analysis["score"].white()
    if score.is_mate():
      eval_score = 10000 if score.mate() > 0 else -10000
      eval_type = "mate"
      mate_in = abs(score.mate())
    else:
      eval_score = score.score() / 100.0
      eval_type = "cp"
      mate_in = None

    best_move = analysis["pv"][0] if analysis.get("pv") else None
    best_move_san = board.san(best_move) if best_move else None

    return (idx, {
      "evaluation": eval_score,
      "evaluation_type": eval_type,
      "mate_in": mate_in,
      "best_move": str(best_move) if best_move else None,
      "best_move_san": best_move_san,
      "principal_variation": [str(move) for move in analysis.get("pv", [])[:5]],
      "depth": analysis.get("depth"),
      "nodes": analysis.get("nodes"),
      "time": analysis.get("time"),
    })
    
  except Exception as e:
    return (idx, {
      "evaluation": 0.0,
      "evaluation_type": "error",
      "error": str(e),
    })
  finally:
    analysis_pool.return_engine(engine)


async def build_chess_database(
    pgn_file: str,
    output_file: str,
    max_positions: int = 5000,
    resume: bool = True,
):
  """Complete pipeline: PGN -> Features -> Descriptions -> Database"""

  print("🏁 CHESS DATABASE BUILDER")
  print("=" * 50)

  # Check for existing intermediate files to resume from
  intermediate_file = output_file.replace(
      ".json", "_with_features_and_engine.json"
  )
  features_only_file = output_file.replace(".json", "_with_features.json")

  positions = None

  # Try to resume from most recent intermediate file
  if resume and Path(intermediate_file).exists():
    print(f"\n🔄 Resuming from {intermediate_file}")
    with open(intermediate_file, "r") as f:
      positions = json.load(f)
    print(
        f"   ✓ Loaded {len(positions)} positions with features and engine"
        " analysis"
    )
    skip_to_step = 4  # Skip to descriptions

  elif resume and Path(features_only_file).exists():
    print(f"\n🔄 Resuming from {features_only_file}")
    with open(features_only_file, "r") as f:
      positions = json.load(f)
    print(f"   ✓ Loaded {len(positions)} positions with features")
    skip_to_step = 2.5  # Skip to engine analysis

  else:
    # Check if input file exists
    if not Path(pgn_file).exists():
      print(f"❌ Error: PGN file '{pgn_file}' not found!")
      print(
          f"   Make sure your mega-2025-small.pgn is in the current directory"
      )
      return

    # Step 1: Parse PGN file
    print(f"\n📖 Step 1: Parsing {pgn_file}")
    positions = parse_pgn_to_positions(pgn_file, max_positions)

    if not positions:
      print(f"❌ No positions extracted from {pgn_file}")
      return

    print(f"   ✓ Extracted {len(positions)} positions")
    skip_to_step = 2  # Start from feature extraction

  # Step 2: Extract features for each position (skip if resuming with features)
  if skip_to_step <= 2:
    print(f"\n🔍 Step 2: Extracting position features")
    print(f"   Processing {len(positions)} positions...")

    for i, position in enumerate(positions):
      try:
        position["position_features"] = extract_position_features(
            position["fen"]
        )
      except Exception as e:
        print(f"   ⚠️  Error processing position {i+1}: {e}")
        # Skip this position or use basic features
        position["position_features"] = {"error": str(e)}

      if (i + 1) % 500 == 0:
        print(
            f"   Progress: {i+1}/{len(positions)} positions"
            f" ({((i+1)/len(positions)*100):.1f}%)"
        )

    print(f"   ✓ Features extracted for all positions")

    # Save intermediate checkpoint
    features_checkpoint = output_file.replace(".json", "_with_features.json")
    with open(features_checkpoint, "w") as f:
      json.dump(positions, f, indent=2)
    print(f"   ✓ Checkpoint saved to {features_checkpoint}")

  # Step 2.5: Pool-based Stockfish analysis of all positions  
  if skip_to_step <= 2.5:
    print(f"\n🔍 Step 2.5: Pool-based Stockfish analysis")
    print(f"   Analyzing {len(positions)} positions with 4 engines...")

    # Initialize pool ONCE before threading to avoid race condition
    analysis_pool = create_deep_analysis_pool(pool_size=4)

    try:
        # Create position list with indices
        positions_with_idx = [(pos, i) for i, pos in enumerate(positions)]
        
        # Process all positions with thread pool + engine pool
        completed = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all positions with the shared pool
            future_to_pos = {executor.submit(analyze_single_position_with_pool, pos_data, analysis_pool): pos_data 
                           for pos_data in positions_with_idx}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_pos):
                idx, analysis = future.result()
                positions[idx]["stockfish_analysis"] = analysis
                
                completed += 1
                if completed % 25 == 0:  # More frequent progress updates
                    print(f"   Progress: {completed}/{len(positions)} positions analyzed "
                          f"({(completed/len(positions)*100):.1f}%)")
        
        print(f"   ✓ Pool-based Stockfish analysis completed for all positions")

    except Exception as e:
        print(f"   ❌ Error in pool-based analysis: {e}")
        print(f"   Adding fallback analysis...")
        # Add empty analysis for positions that failed
        for position in positions:
            if "stockfish_analysis" not in position:
                position["stockfish_analysis"] = {
                    "evaluation": 0.0,
                    "evaluation_type": "error",
                    "error": "Pool analysis failed",
                }
    finally:
        # Clean up the single analysis pool
        print("   Cleaning up analysis engine pool...")
        analysis_pool.cleanup()
        
    # Save intermediate checkpoint with engine analysis
    with open(intermediate_file, "w") as f:
      json.dump(positions, f, indent=2)
    print(f"   ✓ Checkpoint saved to {intermediate_file}")

  # Step 3: Save intermediate result (positions with features and engine analysis)
  intermediate_file = output_file.replace(
      ".json", "_with_features_and_engine.json"
  )
  print(f"\n💾 Step 3: Saving intermediate results")

  try:
    with open(intermediate_file, "w") as f:
      json.dump(positions, f, indent=2)
    print(
        "   ✓ Saved positions with features and engine analysis to"
        f" {intermediate_file}"
    )
  except Exception as e:
    print(f"   ❌ Error saving intermediate file: {e}")
    return

  # Step 4: Generate LLM-enhanced descriptions using Gemini 2.0 Flash-Lite
  print(f"\n📝 Step 4: Generating LLM-enhanced descriptions")
  print(f"   Using Gemini 2.0 Flash-Lite with 10 concurrent workers...")

  # Initialize generator and chain
  generator = ChessDescriptionGenerator()
  chain = generator.create_description_chain()
  
  # Prepare positions with indices for async processing
  positions_with_idx = [(pos, i) for i, pos in enumerate(positions)]
  
  # Process with async concurrency (similar to chess_description_generator.py)
  enhanced_count = 0
  errors = 0
  completed = 0
  
  # Create semaphore for rate limiting
  semaphore = asyncio.Semaphore(10)
  
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
              # Use fallback template description
              positions[idx]["enhanced_description"] = {
                  "description": generate_quick_description(positions[idx]),
                  "strategic_themes": [],
                  "tactical_elements": [],
                  "key_squares": [],
                  "generated_by": "template-fallback"
              }
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
              print(f"   Progress: {completed}/{len(positions)} positions processed ({enhanced_count} enhanced, {errors} errors)")
              
      except Exception as e:
          print(f"   ❌ Task execution error: {e}")
          errors += 1

  print(f"   ✓ LLM enhancement completed: {enhanced_count} enhanced, {errors} errors")

  # Step 5: Analysis summary and LLM cost estimation
  print(f"\n💰 Step 5: Analysis and Cost Summary")

  # Count positions by evaluation range
  eval_ranges = {
      "winning": 0,
      "advantage": 0,
      "equal": 0,
      "disadvantage": 0,
      "losing": 0,
      "mate": 0,
      "error": 0,
  }
  tactical_positions = 0

  for pos in positions:
    analysis = pos.get("stockfish_analysis", {})
    eval_type = analysis.get("evaluation_type", "error")

    if eval_type == "mate":
      eval_ranges["mate"] += 1
      tactical_positions += 1
    elif eval_type == "error" or eval_type == "unavailable":
      eval_ranges["error"] += 1
    else:
      eval_score = analysis.get("evaluation", 0)
      if abs(eval_score) >= 3.0:
        eval_ranges["winning" if eval_score > 0 else "losing"] += 1
        tactical_positions += 1
      elif abs(eval_score) >= 1.0:
        eval_ranges["advantage" if eval_score > 0 else "disadvantage"] += 1
      else:
        eval_ranges["equal"] += 1

  print(f"   Engine Analysis Summary:")
  print(
      "   - Winning/Losing positions:"
      f" {eval_ranges['winning'] + eval_ranges['losing']}"
  )
  print(
      "   - Advantage/Disadvantage:"
      f" {eval_ranges['advantage'] + eval_ranges['disadvantage']}"
  )
  print(f"   - Roughly equal: {eval_ranges['equal']}")
  print(f"   - Checkmate positions: {eval_ranges['mate']}")
  print(f"   - Tactical positions (|eval| > 1.0): {tactical_positions}")

  # Calculate actual LLM costs
  avg_input_tokens = 500  # Estimated
  avg_output_tokens = 250  # Estimated  
  total_input_tokens = enhanced_count * avg_input_tokens
  total_output_tokens = enhanced_count * avg_output_tokens
  
  input_cost = (total_input_tokens / 1_000_000) * 0.075  # Gemini 2.0 Flash-Lite pricing
  output_cost = (total_output_tokens / 1_000_000) * 0.30
  total_llm_cost = input_cost + output_cost

  print(f"\n   LLM Enhancement Results:")
  print(f"   - Enhanced positions: {enhanced_count}/{len(positions)}")
  print(f"   - Template fallbacks: {errors}")
  print(f"   - Estimated cost: ${total_llm_cost:.2f}")
  print(f"   - Input tokens: {total_input_tokens:,} (${input_cost:.2f})")
  print(f"   - Output tokens: {total_output_tokens:,} (${output_cost:.2f})")

  # Step 6: Save final database
  print(f"\n💾 Step 6: Saving final database")

  try:
    with open(output_file, "w") as f:
      json.dump(positions, f, indent=2)
    print(f"   ✓ Database saved to {output_file}")
  except Exception as e:
    print(f"   ❌ Error saving final database: {e}")
    return

  # Step 7: Database summary
  print(f"\n📊 DATABASE SUMMARY")
  print("=" * 30)

  # Analyze the database content
  game_phases = {"opening": 0, "middlegame": 0, "endgame": 0}
  players = set()
  years = set()

  for pos in positions:
    features = pos.get("position_features", {})
    if isinstance(features, dict) and "game_phase" in features:
      phase = features["game_phase"]
      if phase in game_phases:
        game_phases[phase] += 1

    context = pos.get("game_context", {})
    if "white_player" in context:
      players.add(context["white_player"])
    if "black_player" in context:
      players.add(context["black_player"])

    if "date" in context and context["date"]:
      year = context["date"][:4] if len(context["date"]) >= 4 else None
      if year and year.isdigit():
        years.add(year)

  print(f"Total positions: {len(positions)}")
  print(
      f"Game phases: Opening({game_phases['opening']}),"
      f" Middlegame({game_phases['middlegame']}),"
      f" Endgame({game_phases['endgame']})"
  )
  print(f"Unique players: {len(players)}")
  print(
      f"Year range: {min(years) if years else 'N/A'} -"
      f" {max(years) if years else 'N/A'}"
  )

  print(f"\n🎉 SUCCESS!")
  print(f"✓ Database built: {output_file}")
  print(f"✓ Ready for similarity search implementation")
  print(f"✓ Ready for LLM enhancement (optional)")

  # Show a few sample positions
  print(f"\n📋 SAMPLE POSITIONS:")
  for i, pos in enumerate(positions[:3]):
    print(
        f"\n{i+1}. {pos['game_context']['white_player']} vs"
        f" {pos['game_context']['black_player']}"
    )
    print(f"   Move {pos['move_number']}: {pos['last_move']}")
    print(f"   {pos.get('quick_description', 'No description')}")
    print(f"   FEN: {pos['fen'][:50]}...")


def generate_quick_description(position: dict) -> str:
  """Generate engine-enhanced template-based description"""

  try:
    features = position.get("position_features", {})
    context = position.get("game_context", {})
    engine_analysis = position.get("stockfish_analysis", {})

    description_parts = []

    # Game phase
    game_phase = features.get("game_phase", "unknown")
    description_parts.append(f"{game_phase.title()} position")

    # Engine evaluation
    eval_score = engine_analysis.get("evaluation", 0)
    eval_type = engine_analysis.get("evaluation_type", "cp")

    if eval_type == "mate":
      mate_in = engine_analysis.get("mate_in", "?")
      if eval_score > 0:
        description_parts.append(f"White mates in {mate_in}")
      else:
        description_parts.append(f"Black mates in {mate_in}")
    elif eval_type == "cp":
      if abs(eval_score) >= 3.0:
        if eval_score > 0:
          description_parts.append(f"White winning (+{eval_score:.1f})")
        else:
          description_parts.append(f"Black winning ({eval_score:.1f})")
      elif abs(eval_score) >= 1.0:
        if eval_score > 0:
          description_parts.append(f"White advantage (+{eval_score:.1f})")
        else:
          description_parts.append(f"Black advantage ({eval_score:.1f})")
      else:
        description_parts.append(f"roughly equal ({eval_score:+.1f})")
    else:
      # Fallback to material balance
      material = features.get("material", {})
      balance = material.get("balance", 0)
      if abs(balance) > 1.5:
        if balance > 0:
          description_parts.append(f"White ahead by {abs(balance):.1f} points")
        else:
          description_parts.append(f"Black ahead by {abs(balance):.1f} points")
      else:
        description_parts.append("material roughly equal")

    # Best move from engine
    best_move = engine_analysis.get("best_move_san")
    if best_move:
      description_parts.append(f"best: {best_move}")

    # Board control
    board_control = features.get("board_control", {})
    open_files = board_control.get("open_files", [])
    if open_files and len(open_files) <= 2:  # Don't clutter if many open files
      files_str = ",".join(open_files)
      description_parts.append(
          f"open {files_str} file{'s' if len(open_files) > 1 else ''}"
      )

    # Special situations
    special = features.get("special", {})
    if special.get("in_check"):
      description_parts.append("king in check")
    elif special.get("is_checkmate"):
      description_parts.append("checkmate")

    # King safety
    king_safety = features.get("king_safety", {})
    castling = king_safety.get("castling_status", {})
    if castling.get("white_has_castled") and castling.get("black_has_castled"):
      description_parts.append("both sides castled")

    # Last move context
    last_move = position.get("last_move", "")
    if last_move:
      description_parts.append(f"after {last_move}")

    return ". ".join(description_parts).capitalize()

  except Exception as e:
    return (
        f"Position from move {position.get('move_number', '?')} - analysis"
        f" error: {str(e)}"
    )


def main():
  """Main function with command line argument handling"""

  # Default values
  pgn_file = "mega-2025-small.pgn"
  output_file = "chess_database.json"
  max_positions = 5000
  resume = True

  # Handle command line arguments
  if len(sys.argv) > 1:
    pgn_file = sys.argv[1]
  if len(sys.argv) > 2:
    max_positions = int(sys.argv[2])
  if len(sys.argv) > 3:
    output_file = sys.argv[3]
  if len(sys.argv) > 4:
    resume = sys.argv[4].lower() != "false"

  print(f"Configuration:")
  print(f"  PGN file: {pgn_file}")
  print(f"  Max positions: {max_positions}")
  print(f"  Output file: {output_file}")
  print(f"  Resume from checkpoints: {resume}")
  print(f"  LLM enhancement: Gemini 2.0 Flash-Lite (10 concurrent)")

  # Run the database builder
  asyncio.run(
      build_chess_database(pgn_file, output_file, max_positions, resume)
  )


if __name__ == "__main__":
  main()
