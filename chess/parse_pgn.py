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

import concurrent.futures
import json
import time
from typing import Dict, List, Optional
import chess
import chess.engine
import chess.pgn
from position_features import calculate_material_balance, extract_position_features
from stockfish_pool import create_quick_analysis_pool

# Global counters to track Stockfish filtering cost
stockfish_calls = 0
stockfish_time = 0.0


# Global pool instance
_engine_pool = None


def get_engine_pool():
  global _engine_pool
  if _engine_pool is None:
    _engine_pool = create_quick_analysis_pool(pool_size=4)
  return _engine_pool


def analyze_position_threaded(board: chess.Board) -> bool:
  """Quick analysis using engine pool + threading"""

  def do_analysis():
    pool = get_engine_pool()
    engine = pool.get_engine()  # Blocks until engine available

    try:
      analysis = engine.analyse(board, chess.engine.Limit(depth=4, time=0.05))
      score = analysis["score"].white()

      if score.is_mate():
        return True

      eval_score = score.score() / 100.0 if score.score() else 0.0
      return abs(eval_score) > 2.0

    finally:
      pool.return_engine(engine)  # Always return engine to pool

  return do_analysis()


def quick_stockfish_check(board: chess.Board) -> bool:
  """Parallel quick check using engine pool"""
  global stockfish_calls, stockfish_time

  start_time = time.time()
  stockfish_calls += 1

  try:
    # Execute analysis in thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
      future = executor.submit(analyze_position_threaded, board)
      result = future.result(timeout=1.0)  # 1 second timeout

    stockfish_time += time.time() - start_time
    return result

  except Exception as e:
    stockfish_time += time.time() - start_time
    print(f"   ⚠️ Quick analysis failed: {e}")
    return False


def get_stockfish_evaluation(board: chess.Board) -> Optional[float]:
  """Get Stockfish evaluation in centipawns (from White's perspective)"""
  global stockfish_calls, stockfish_time

  start_time = time.time()
  stockfish_calls += 1

  try:
    def do_eval_analysis():
      pool = get_engine_pool()
      engine = pool.get_engine()

      try:
        analysis = engine.analyse(board, chess.engine.Limit(depth=6, time=0.1))
        score = analysis["score"].white()

        if score.is_mate():
          # Convert mate to large centipawn value
          mate_in = score.mate()
          return 10000 if mate_in > 0 else -10000
        else:
          # Return centipawn score
          return float(score.score()) if score.score() else 0.0

      finally:
        pool.return_engine(engine)

    # Execute analysis in thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
      future = executor.submit(do_eval_analysis)
      result = future.result(timeout=1.5)  # Slightly longer timeout for evaluation

    stockfish_time += time.time() - start_time
    return result

  except Exception as e:
    stockfish_time += time.time() - start_time
    print(f"   ⚠️ Evaluation analysis failed: {e}")
    return None


def is_borderline_interesting(board: chess.Board, move_number: int) -> bool:
  """Positions that might be interesting but heuristics are unsure"""

  # Skip very early and very late game
  if move_number < 8 or move_number > 60:
    return False

  # Check positions with small material imbalances (might hide tactics)
  material_balance = calculate_material_balance(board)
  if 0.5 <= abs(material_balance) <= 1.2:  # Small but notable imbalance
    return True

  # Positions where kings haven't castled in middlegame (risky)
  if (
      move_number > 10
      and move_number < 25
      and (
          board.has_castling_rights(chess.WHITE)
          or board.has_castling_rights(chess.BLACK)
      )
  ):
    return True

  # Complex middlegame positions (many pieces, equal material)
  total_pieces = len(board.piece_map())
  if (
      20 <= total_pieces <= 28  # Middlegame piece count
      and abs(material_balance) < 0.5
  ):  # Equal material
    return move_number % 8 == 0  # Sample some of these

  return False


def parse_pgn_to_positions(
    pgn_file_path: str, max_positions: int = 5000
) -> list[dict]:
  """Extract positions from your mega-2025-small.pgn"""
  global stockfish_calls, stockfish_time

  # Reset counters
  stockfish_calls = 0
  stockfish_time = 0.0
  
  positions = []
  games_processed = 0

  print(f"Parsing {pgn_file_path} with chess-significance filtering...")
  start_total = time.time()

  try:
    with open(pgn_file_path) as pgn_file:
      while len(positions) < max_positions:
        game = chess.pgn.read_game(pgn_file)
        if game is None:
          break

        # Extract game metadata
        metadata = {
            "white_player": game.headers.get("White", "Unknown"),
            "black_player": game.headers.get("Black", "Unknown"),
            "result": game.headers.get("Result", "*"),
            "date": game.headers.get("Date", ""),
            "event": game.headers.get("Event", ""),
            "eco": game.headers.get("ECO", ""),
            "white_elo": game.headers.get("WhiteElo", ""),
            "black_elo": game.headers.get("BlackElo", ""),
            "source": "mega-2025-small",
        }

        # Walk through the game and extract interesting positions
        board = game.board()
        move_number = 1
        game_id = f"{metadata['white_player']}_{metadata['black_player']}_{metadata['date']}"
        prev_eval = None  # Track previous evaluation for swing detection

        try:
          for move in game.mainline_moves():
            # Get SAN notation BEFORE pushing the move
            try:
              move_san = board.san(move)
            except ValueError:
              # Skip illegal moves
              print(f"   ⚠️  Skipping illegal move: {move}")
              continue

            # Now push the move
            board.push(move)

            # Extract positions using chess-significance filtering
            should_extract, extraction_metadata = should_extract_position_smart(board, move_number, prev_eval)
            
            if should_extract:
              # Get current evaluation (may already be in metadata)
              current_eval = extraction_metadata.get("current_eval")
              if current_eval is None:
                current_eval = get_stockfish_evaluation(board)
              
              position = {
                  "fen": board.fen(),
                  "move_number": move_number,
                  "last_move": move_san,  # Use the SAN we got before pushing
                  "game_context": metadata.copy(),
                  "position_features": None,  # Will extract next
                  "position_description": None,  # Will generate with LLM
                  "stockfish_eval": current_eval,  # Store evaluation for reference
                  # NEW: Chess significance metadata
                  "eval_swing": extraction_metadata.get("eval_swing", 0.0),
                  "selection_reason": extraction_metadata.get("selection_reason", "unknown"),
                  "tactical_significance": extraction_metadata.get("tactical_significance", 1.0),
                  "extraction_metadata": extraction_metadata,  # Full context for analysis
              }
              positions.append(position)

              # Update previous evaluation for swing detection
              prev_eval = current_eval

              # Break if we've hit our limit
              if len(positions) >= max_positions:
                break

            move_number += 1

        except Exception as e:
          print(f"   ⚠️  Error processing game {games_processed + 1}: {e}")
          continue

        games_processed += 1
        if games_processed % 10 == 0:
          print(
              f"   Progress: {games_processed} games processed,"
              f" {len(positions)} positions extracted"
          )

        # Break if we've extracted enough positions
        if len(positions) >= max_positions:
          break

  except FileNotFoundError:
    print(f"❌ Error: Could not find file {pgn_file_path}")
    return []
  except Exception as e:
    print(f"❌ Error reading PGN file: {e}")
    return []

  print(f"✓ Final: {len(positions)} positions from {games_processed} games")

  # Print cost analysis at the end
  total_time = time.time() - start_total
  print(f"\n=== SMART EVALUATION-BASED FILTERING ANALYSIS ===")
  print(f"Stockfish calls: {stockfish_calls}")
  print(
      f"Stockfish time: {stockfish_time:.1f}s"
      f" ({stockfish_time/total_time*100:.1f}% of total)"
  )
  print(
      f"Avg per call: {stockfish_time/stockfish_calls*1000:.1f}ms"
      if stockfish_calls > 0
      else "No calls"
  )
  print(f"Total parsing time: {total_time:.1f}s")
  print(f"Positions extracted: {len(positions)}")
  
  # Analyze quality of extracted positions using chess significance
  if positions:
    eval_positions = [p for p in positions if p.get("stockfish_eval") is not None]
    if eval_positions:
      # Count by selection reason
      selection_reasons = {}
      for p in positions:
        reason = p.get("selection_reason", "unknown")
        selection_reasons[reason] = selection_reasons.get(reason, 0) + 1
      
      # Count by tactical significance
      high_significance = sum(1 for p in positions if p.get("tactical_significance", 0) >= 3.0)
      medium_significance = sum(1 for p in positions if 2.0 <= p.get("tactical_significance", 0) < 3.0)
      low_significance = sum(1 for p in positions if p.get("tactical_significance", 0) < 2.0)
      
      # Count by evaluation swing ranges
      large_swings = sum(1 for p in positions if p.get("eval_swing", 0) >= 100)
      medium_swings = sum(1 for p in positions if 50 <= p.get("eval_swing", 0) < 100)
      small_swings = sum(1 for p in positions if p.get("eval_swing", 0) < 50)
      
      print(f"\n=== CHESS SIGNIFICANCE ANALYSIS ===")
      print(f"Total positions extracted: {len(positions)}")
      print(f"\nSelection reasons:")
      for reason, count in sorted(selection_reasons.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(positions) * 100
        print(f"  {reason}: {count} ({percentage:.1f}%)")
      
      print(f"\nTactical significance levels:")
      print(f"  High significance (≥3.0): {high_significance} ({high_significance/len(positions)*100:.1f}%)")
      print(f"  Medium significance (2.0-3.0): {medium_significance} ({medium_significance/len(positions)*100:.1f}%)")
      print(f"  Low significance (<2.0): {low_significance} ({low_significance/len(positions)*100:.1f}%)")
      
      print(f"\nEvaluation swing distribution:")
      print(f"  Large swings (≥1.0): {large_swings} ({large_swings/len(positions)*100:.1f}%)")
      print(f"  Medium swings (0.5-1.0): {medium_swings} ({medium_swings/len(positions)*100:.1f}%)")
      print(f"  Small/no swings (<0.5): {small_swings} ({small_swings/len(positions)*100:.1f}%)")
      
      # Calculate average tactical significance
      avg_significance = sum(p.get("tactical_significance", 0) for p in positions) / len(positions)
      avg_swing = sum(p.get("eval_swing", 0) for p in positions) / len(positions)
      
      print(f"\nQuality metrics:")
      print(f"  Average tactical significance: {avg_significance:.2f}")
      print(f"  Average evaluation swing: {avg_swing:.2f}")
      print(f"  Chess significance ratio: {(high_significance + medium_significance) / len(positions) * 100:.1f}% medium+ significance")

  # Clean up engine pool
  global _engine_pool
  if _engine_pool:
    print("   Cleaning up Stockfish engine pool...")
    _engine_pool.cleanup()
    _engine_pool = None

  return positions


def should_extract_position_smart(board: chess.Board, move_number: int, prev_eval: Optional[float] = None) -> tuple[bool, dict]:
  """Smart position extraction using chess significance only (no arbitrary sampling)
  
  Returns: (should_extract, extraction_metadata)
  """
  
  # Skip very early opening (first 5 moves usually theory)
  if move_number < 6:
    return False, {}

  # Skip very long games (often drawn endgames)  
  if move_number > 80:
    return False, {}

  # Get current evaluation for smart filtering
  current_eval = get_stockfish_evaluation(board)
  if current_eval is None:
    # Only extract material imbalances if Stockfish fails
    material_balance = calculate_material_balance(board)
    if abs(material_balance) > 1.5:
      return True, {
        "selection_reason": "material_imbalance",
        "eval_swing": 0.0,
        "tactical_significance": 1.0,
        "material_advantage": abs(material_balance)
      }
    return False, {}  # No arbitrary sampling as fallback

  # Calculate evaluation swing
  eval_swing = abs(current_eval - prev_eval) if prev_eval is not None else 0.0
  abs_eval = abs(current_eval)
  total_pieces = len(board.piece_map())
  is_endgame = total_pieces <= 12

  # Priority 1: Forced moves and game-ending positions
  if board.is_checkmate():
    return True, {
      "selection_reason": "checkmate",
      "eval_swing": eval_swing,
      "tactical_significance": 5.0,
      "current_eval": current_eval
    }

  if board.is_stalemate():
    return True, {
      "selection_reason": "stalemate", 
      "eval_swing": eval_swing,
      "tactical_significance": 4.0,
      "current_eval": current_eval
    }

  if board.is_check():
    return True, {
      "selection_reason": "check",
      "eval_swing": eval_swing, 
      "tactical_significance": 2.0,
      "current_eval": current_eval
    }

  # Priority 2: Decisive advantages
  if abs_eval >= 300:  # >= 3.00 advantage (winning)
    return True, {
      "selection_reason": "winning_advantage",
      "eval_swing": eval_swing,
      "tactical_significance": 4.0,
      "current_eval": current_eval
    }

  # Priority 3: Major evaluation swings (tactical moments)
  if eval_swing >= 150:  # >= 1.50 swing
    return True, {
      "selection_reason": "major_tactical_swing",
      "eval_swing": eval_swing,
      "tactical_significance": 4.0,
      "current_eval": current_eval,
      "prev_eval": prev_eval
    }

  if eval_swing >= 100:  # >= 1.00 swing  
    return True, {
      "selection_reason": "tactical_swing",
      "eval_swing": eval_swing,
      "tactical_significance": 3.0,
      "current_eval": current_eval,
      "prev_eval": prev_eval
    }

  # Priority 4: Significant advantages
  if abs_eval >= 200:  # >= 2.00 advantage
    return True, {
      "selection_reason": "significant_advantage",
      "eval_swing": eval_swing,
      "tactical_significance": 3.0,
      "current_eval": current_eval
    }

  # Priority 5: Moderate swings in balanced positions (often tactical)
  if prev_eval is not None and eval_swing >= 50 and abs(prev_eval) <= 50:
    return True, {
      "selection_reason": "tactical_moment_in_equal_position",
      "eval_swing": eval_swing,
      "tactical_significance": 2.5,
      "current_eval": current_eval,
      "prev_eval": prev_eval
    }

  # Priority 6: Clear advantages (especially in endgames)
  if abs_eval >= 150:  # >= 1.50 advantage
    significance = 2.5 if is_endgame else 2.0
    return True, {
      "selection_reason": "clear_advantage",
      "eval_swing": eval_swing,
      "tactical_significance": significance,
      "current_eval": current_eval,
      "is_endgame": is_endgame
    }

  # Priority 7: Endgame positions with meaningful advantage
  if is_endgame and abs_eval >= 75:  # >= 0.75 in endgame
    return True, {
      "selection_reason": "endgame_advantage",
      "eval_swing": eval_swing,
      "tactical_significance": 2.0,
      "current_eval": current_eval,
      "piece_count": total_pieces
    }

  # No arbitrary sampling - only chess-significant positions
  return False, {}


def should_extract_position(board: chess.Board, move_number: int) -> bool:
  """Legacy wrapper - calls smart extraction without previous evaluation"""
  return should_extract_position_smart(board, move_number, None)


def extract_interesting_moments(board: chess.Board, move_number: int) -> dict:
  """Extract additional context for interesting positions"""

  context = {
      "is_tactical": False,
      "is_endgame": False,
      "material_imbalance": False,
      "king_safety_issue": False,
  }

  # Tactical moments
  if board.is_check() or board.is_checkmate():
    context["is_tactical"] = True

  # Material imbalance
  material_balance = abs(calculate_material_balance(board))
  if material_balance > 2.0:
    context["material_imbalance"] = True

  # Endgame detection
  total_pieces = len(board.piece_map())
  if total_pieces <= 12:
    context["is_endgame"] = True

  # King safety issues
  if not board.has_castling_rights(
      chess.WHITE
  ) or not board.has_castling_rights(chess.BLACK):
    # Check if kings are still in center
    white_king = board.king(chess.WHITE)
    black_king = board.king(chess.BLACK)

    if white_king and chess.square_file(white_king) in [3, 4]:  # e or d file
      context["king_safety_issue"] = True
    if black_king and chess.square_file(black_king) in [3, 4]:
      context["king_safety_issue"] = True

  return context


if __name__ == "__main__":
  # Test the parser
  positions = parse_pgn_to_positions("mega-2025-small.pgn", max_positions=100)

  if positions:
    print(f"\n=== SAMPLE POSITIONS ===")
    for i, pos in enumerate(positions[:3]):
      print(f"\nPosition {i+1}:")
      print(f"  FEN: {pos['fen']}")
      print(
          f"  Game: {pos['game_context']['white_player']} vs"
          f" {pos['game_context']['black_player']}"
      )
      print(f"  Move: {pos['move_number']} ({pos['last_move']})")
  else:
    print("No positions extracted. Check your PGN file.")
