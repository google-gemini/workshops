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


import chess
import chess.pgn
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class GameChunk:
    """Represents a 4-move sequence from a chess game"""
    game_metadata: dict
    move_sequence: dict
    position_data: dict
    position_facts: dict
    annotations: dict
    embedding_content: str

def extract_game_metadata(game) -> dict:
    """Extract basic metadata from PGN headers"""
    headers = game.headers
    
    return {
        "white_player": headers.get("White", "Unknown"),
        "black_player": headers.get("Black", "Unknown"),
        "white_elo": int(headers.get("WhiteElo", 0)) if headers.get("WhiteElo") else None,
        "black_elo": int(headers.get("BlackElo", 0)) if headers.get("BlackElo") else None,
        "result": headers.get("Result", "*"),
        "date": headers.get("Date", ""),
        "event": headers.get("Event", ""),
        "site": headers.get("Site", ""),
        "round": headers.get("Round", ""),
        "eco": headers.get("ECO", ""),
    }

def extract_position_facts(board: chess.Board) -> dict:
    """Extract deterministic facts about the current position"""
    facts = {}
    
    # Basic material balance
    material_balance = 0
    piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, 
                   chess.ROOK: 5, chess.QUEEN: 9}
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                material_balance += value
            else:
                material_balance -= value
    
    facts["material_balance"] = material_balance
    
    # Castling rights
    castling = {"white": [], "black": []}
    if board.has_kingside_castling_rights(chess.WHITE):
        castling["white"].append("k")
    if board.has_queenside_castling_rights(chess.WHITE):
        castling["white"].append("q")
    if board.has_kingside_castling_rights(chess.BLACK):
        castling["black"].append("k")
    if board.has_queenside_castling_rights(chess.BLACK):
        castling["black"].append("q")
    
    facts["castling_rights"] = castling
    
    # Open files (simple version)
    open_files = []
    for file_idx in range(8):
        has_pawn = False
        for rank in range(8):
            square = chess.square(file_idx, rank)
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN:
                has_pawn = True
                break
        if not has_pawn:
            open_files.append(chess.FILE_NAMES[file_idx])
    
    facts["open_files"] = open_files
    
    # Game phase estimation
    piece_count = len(board.piece_map())
    if piece_count > 28:
        game_phase = "opening"
    elif piece_count > 12:
        game_phase = "middlegame"
    else:
        game_phase = "endgame"
    
    facts["game_phase"] = game_phase
    
    return facts

def extract_move_comments(game, move_numbers: List[int]) -> dict:
    """Extract comments for moves in the chunk"""
    comments = {}
    variations = []
    
    # This is simplified - full comment extraction is complex in python-chess
    # For now, just extract basic move comments if available
    
    # TODO: Implement proper comment extraction from game tree
    # This would involve walking the game tree and collecting comments
    # for the specific moves in our chunk
    
    return {
        "move_comments": comments,
        "variations": variations
    }

def format_embedding_content(moves: List[str], position_facts: dict, 
                           fen: str, eco: str, comments: dict) -> str:
    """Format chunk data into text suitable for embedding"""
    
    content_parts = []
    
    # Core move sequence
    content_parts.append(f"Moves: {' '.join(moves)}")
    
    # Position description
    content_parts.append(f"Position: {fen}")
    
    # Opening if available
    if eco:
        content_parts.append(f"Opening: {eco}")
    
    # Game phase
    game_phase = position_facts.get("game_phase", "")
    if game_phase:
        content_parts.append(f"Game phase: {game_phase}")
    
    # Material situation
    material = position_facts.get("material_balance", 0)
    if material == 0:
        content_parts.append("Material: equal")
    elif material > 0:
        content_parts.append(f"Material: White ahead by {material} points")
    else:
        content_parts.append(f"Material: Black ahead by {abs(material)} points")
    
    # Castling status
    castling = position_facts.get("castling_rights", {})
    white_castling = castling.get("white", [])
    black_castling = castling.get("black", [])
    
    if not white_castling and not black_castling:
        content_parts.append("Castling: both sides completed")
    elif white_castling and black_castling:
        content_parts.append("Castling: both sides retain rights")
    
    # Open files
    open_files = position_facts.get("open_files", [])
    if open_files:
        content_parts.append(f"Open files: {', '.join(open_files)}")
    
    # Add any human commentary
    move_comments = comments.get("move_comments", {})
    if move_comments:
        for move_num, comment in move_comments.items():
            content_parts.append(f"Commentary: {comment}")
    
    return ". ".join(content_parts)

def create_overlapping_chunks(game) -> List[GameChunk]:
    """Create overlapping 4-move chunks from a game"""
    chunks = []
    metadata = extract_game_metadata(game)
    
    # Collect ALL moves once to avoid repeated generator calls
    all_moves = list(game.mainline_moves())
    
    # Skip games with fewer than 4 moves
    if len(all_moves) < 4:
        return chunks
    
    # Play through the game and collect moves in SAN notation
    board = game.board()
    moves = []
    move_numbers = []
    
    # Convert to standard algebraic notation
    for move_count, move in enumerate(all_moves):
        san_move = board.san(move)
        moves.append(san_move)
        move_numbers.append(move_count + 1)
        board.push(move)
    
    # Create overlapping 4-move chunks
    for start_idx in range(len(moves) - 3):
        try:
            print(f"🔍 Creating chunk {start_idx + 1}, start_idx={start_idx}")
            
            chunk_moves = moves[start_idx:start_idx + 4]
            chunk_move_numbers = move_numbers[start_idx:start_idx + 4]
            print(f"✅ Chunk moves extracted: {chunk_moves}")
            
            # Replay to get position after these 4 moves
            chunk_board = game.board()
            print(f"✅ Fresh board created")
            
            for i in range(start_idx + 4):
                print(f"Debug: chunk {start_idx + 1}, accessing all_moves[{i}] (max valid: {len(all_moves)-1})")
                chunk_board.push(all_moves[i])
            print(f"✅ Board position replayed successfully")
            
            # Determine whose turn it is after this sequence
            to_move = "white" if chunk_board.turn == chess.WHITE else "black"
            print(f"✅ Turn determined: {to_move}")
            
            # Extract position facts
            position_facts = extract_position_facts(chunk_board)
            print(f"✅ Position facts extracted")
            
            # Extract comments (simplified for now)
            comments = extract_move_comments(game, chunk_move_numbers)
            print(f"✅ Comments extracted")
            
            # Create the chunk
            chunk = GameChunk(
                game_metadata=metadata,
                move_sequence={
                    "moves": chunk_moves,
                    "move_numbers": chunk_move_numbers,
                    "colors": ["white" if i % 2 == 0 else "black" for i in range(4)],
                    "to_move_after": to_move
                },
                position_data={
                    "fen": chunk_board.fen(),
                    "move_count": start_idx + 4,
                },
                position_facts=position_facts,
                annotations=comments,
                embedding_content=format_embedding_content(
                    chunk_moves, position_facts, chunk_board.fen(), 
                    metadata.get("eco", ""), comments
                )
            )
            print(f"✅ Chunk {start_idx + 1} created successfully")
            
            chunks.append(chunk)
            print(f"✅ Chunk {start_idx + 1} added to chunks list")
            
        except Exception as chunk_error:
            print(f"❌ Error in chunk {start_idx + 1}: {type(chunk_error).__name__}: {chunk_error}")
            import traceback
            traceback.print_exc()
            raise  # Re-raise to see full stack trace
    
    return chunks

def parse_pgn_file(pgn_file_path: str, max_games: Optional[int] = None) -> List[dict]:
    """Parse PGN file and return list of chunks"""
    chunks = []
    games_processed = 0
    
    print(f"📚 Starting to parse {pgn_file_path}")
    
    with open(pgn_file_path, 'r', encoding='utf-8') as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
                
            try:
                game_chunks = create_overlapping_chunks(game)
                
                # Convert chunks to dictionaries for JSON serialization
                for chunk in game_chunks:
                    chunk_dict = {
                        "game_metadata": chunk.game_metadata,
                        "move_sequence": chunk.move_sequence,
                        "position_data": chunk.position_data,
                        "position_facts": chunk.position_facts,
                        "annotations": chunk.annotations,
                        "embedding_content": chunk.embedding_content
                    }
                    chunks.append(chunk_dict)
                
                games_processed += 1
                
                if games_processed % 100 == 0:
                    print(f"  Processed {games_processed} games, created {len(chunks)} chunks")
                
                if max_games and games_processed >= max_games:
                    break
                    
            except Exception as e:
                print(f"⚠️  Error processing game {games_processed + 1}: {type(e).__name__}: {str(e)}")
                print(f"   Game headers: {game.headers if game else 'No game object'}")
                if game:
                    try:
                        moves = list(game.mainline_moves())
                        print(f"   Move count: {len(moves)}")
                        if len(moves) < 4:
                            print(f"   ➤ Game too short for 4-move chunks")
                    except Exception as move_error:
                        print(f"   ➤ Could not extract moves: {move_error}")
                continue
    
    print(f"✅ Completed parsing: {games_processed} games → {len(chunks)} chunks")
    return chunks

def save_chunks_to_json(chunks: List[dict], output_file: str):
    """Save chunks to JSON file"""
    print(f"💾 Saving {len(chunks)} chunks to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to {output_file}")

if __name__ == "__main__":
    # Test with small file
    input_file = "mega-2025-small.pgn"
    output_file = "chunks-small.json"
    
    # Parse PGN file
    chunks = parse_pgn_file(input_file, max_games=50)  # Limit for testing
    
    # Save to JSON
    save_chunks_to_json(chunks, output_file)
    
    # Show sample output
    if chunks:
        print("\n🔍 Sample chunk:")
        sample_chunk = chunks[0]
        print(f"Moves: {sample_chunk['move_sequence']['moves']}")
        print(f"FEN: {sample_chunk['position_data']['fen']}")
        print(f"Embedding content: {sample_chunk['embedding_content'][:200]}...")
