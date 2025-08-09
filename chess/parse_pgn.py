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

  print(f"Parsing {pgn_file_path} with Stockfish-enhanced filtering...")
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

            # Extract positions at interesting moments
            if should_extract_position(board, move_number):
              position = {
                  "fen": board.fen(),
                  "move_number": move_number,
                  "last_move": move_san,  # Use the SAN we got before pushing
                  "game_context": metadata.copy(),
                  "position_features": None,  # Will extract next
                  "position_description": None,  # Will generate with LLM
              }
              positions.append(position)

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
  print(f"\n=== ENHANCED FILTERING COST ANALYSIS ===")
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

  # Clean up engine pool
  global _engine_pool
  if _engine_pool:
    print("   Cleaning up Stockfish engine pool...")
    _engine_pool.cleanup()
    _engine_pool = None

  return positions


def should_extract_position(board: chess.Board, move_number: int) -> bool:
  """Enhanced position extraction with optional Stockfish filtering"""

  # Skip very early opening (first 5 moves usually theory)
  if move_number < 6:
    return False

  # Skip very long games (often drawn endgames)
  if move_number > 80:
    return False

  # Always extract obvious tactical moments
  if board.is_check():
    return True

  if board.is_checkmate() or board.is_stalemate():
    return True

  # Extract positions with interesting material imbalances
  material_balance = calculate_material_balance(board)
  if abs(material_balance) > 1.5:  # Someone is significantly ahead
    return True

  # Extract every 5-6 moves to get good coverage without too many positions
  if move_number % 6 == 0:
    return True

  # Extract positions where castling rights change
  if not board.has_castling_rights(
      chess.WHITE
  ) and not board.has_castling_rights(chess.BLACK):
    # Both sides have castled or lost rights - extract occasionally
    if move_number % 8 == 0:
      return True

  # Extract some endgame positions (few pieces left)
  total_pieces = len(board.piece_map())
  if total_pieces <= 12:  # Endgame threshold
    if move_number % 4 == 0:  # More frequent sampling in endgames
      return True

  # NEW: Enhanced filtering for borderline cases - TEMPORARILY DISABLED
  if is_borderline_interesting(board, move_number):
    return quick_stockfish_check(board)

  return False


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
