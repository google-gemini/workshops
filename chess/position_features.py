import chess
from typing import Dict, List, Set
from collections import defaultdict

def extract_position_features(fen: str) -> dict:
    """Extract all deterministic features from a position"""
    
    board = chess.Board(fen)
    
    features = {
        # Basic position info
        "to_move": "white" if board.turn == chess.WHITE else "black",
        "move_number": board.fullmove_number,
        "halfmove_clock": board.halfmove_clock,
        
        # Material analysis
        "material": analyze_material(board),
        
        # Pawn structure
        "pawn_structure": analyze_pawn_structure(board),
        
        # Piece activity
        "piece_activity": analyze_piece_activity(board),
        
        # King safety
        "king_safety": analyze_king_safety(board),
        
        # Board control
        "board_control": analyze_board_control(board),
        
        # Game phase
        "game_phase": determine_game_phase(board),
        
        # Special situations
        "special": analyze_special_situations(board)
    }
    
    return features

def calculate_material_balance(board: chess.Board) -> float:
    """Calculate material balance from White's perspective"""
    piece_values = {
        chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
    }
    
    white_material = sum(
        piece_values[piece.piece_type] 
        for piece in board.piece_map().values() 
        if piece.color == chess.WHITE
    )
    
    black_material = sum(
        piece_values[piece.piece_type] 
        for piece in board.piece_map().values() 
        if piece.color == chess.BLACK
    )
    
    return white_material - black_material

def analyze_material(board: chess.Board) -> dict:
    """Analyze material balance and piece counts"""
    
    material_balance = calculate_material_balance(board)
    
    white_pieces = len([p for p in board.piece_map().values() if p.color == chess.WHITE])
    black_pieces = len([p for p in board.piece_map().values() if p.color == chess.BLACK])
    
    return {
        "balance": material_balance,
        "white_pieces": white_pieces,
        "black_pieces": black_pieces,
        "total_pieces": white_pieces + black_pieces
    }

def analyze_pawn_structure(board: chess.Board) -> dict:
    """Analyze pawn structure characteristics"""
    
    return {
        "doubled_pawns": find_doubled_pawns(board),
        "isolated_pawns": find_isolated_pawns(board), 
        "passed_pawns": find_passed_pawns(board),
        "pawn_islands": count_pawn_islands(board),
        "advanced_pawns": find_advanced_pawns(board)
    }

def find_doubled_pawns(board: chess.Board) -> dict:
    """Find doubled pawns for both colors"""
    doubled = {"white": [], "black": []}
    
    for color in [chess.WHITE, chess.BLACK]:
        pawns = board.pieces(chess.PAWN, color)
        files_with_pawns = defaultdict(list)
        
        for square in pawns:
            file_char = chess.square_name(square)[0]
            files_with_pawns[file_char].append(square)
        
        for file_char, squares in files_with_pawns.items():
            if len(squares) > 1:
                color_name = "white" if color == chess.WHITE else "black"
                doubled[color_name].append(file_char)
    
    return doubled

def find_isolated_pawns(board: chess.Board) -> dict:
    """Find isolated pawns (no friendly pawns on adjacent files)"""
    isolated = {"white": [], "black": []}
    
    for color in [chess.WHITE, chess.BLACK]:
        pawns = board.pieces(chess.PAWN, color)
        pawn_files = set()
        
        for square in pawns:
            file_char = chess.square_name(square)[0]
            pawn_files.add(file_char)
        
        for square in pawns:
            file_char = chess.square_name(square)[0]
            file_index = ord(file_char) - ord('a')
            
            # Check adjacent files
            has_adjacent = False
            for adjacent_file_index in [file_index - 1, file_index + 1]:
                if 0 <= adjacent_file_index <= 7:
                    adjacent_file = chr(ord('a') + adjacent_file_index)
                    if adjacent_file in pawn_files:
                        has_adjacent = True
                        break
            
            if not has_adjacent:
                color_name = "white" if color == chess.WHITE else "black"
                isolated[color_name].append(file_char)
    
    return isolated

def find_passed_pawns(board: chess.Board) -> dict:
    """Find passed pawns (no enemy pawns can stop them)"""
    passed = {"white": [], "black": []}
    
    for color in [chess.WHITE, chess.BLACK]:
        enemy_color = not color
        pawns = board.pieces(chess.PAWN, color)
        enemy_pawns = board.pieces(chess.PAWN, enemy_color)
        
        for square in pawns:
            file_char = chess.square_name(square)[0]
            rank = chess.square_rank(square)
            file_index = ord(file_char) - ord('a')
            
            # Check if any enemy pawn can stop this pawn
            is_passed = True
            
            for enemy_square in enemy_pawns:
                enemy_file_char = chess.square_name(enemy_square)[0]
                enemy_rank = chess.square_rank(enemy_square)
                enemy_file_index = ord(enemy_file_char) - ord('a')
                
                # Check if enemy pawn is on same file or adjacent files
                if abs(file_index - enemy_file_index) <= 1:
                    # Check if enemy pawn is ahead of our pawn
                    if color == chess.WHITE and enemy_rank > rank:
                        is_passed = False
                        break
                    elif color == chess.BLACK and enemy_rank < rank:
                        is_passed = False
                        break
            
            if is_passed:
                color_name = "white" if color == chess.WHITE else "black"
                passed[color_name].append(file_char)
    
    return passed

def count_pawn_islands(board: chess.Board) -> dict:
    """Count pawn islands (groups of connected pawns)"""
    islands = {"white": 0, "black": 0}
    
    for color in [chess.WHITE, chess.BLACK]:
        pawns = board.pieces(chess.PAWN, color)
        pawn_files = set()
        
        for square in pawns:
            file_char = chess.square_name(square)[0]
            pawn_files.add(file_char)
        
        # Count contiguous groups of files
        if not pawn_files:
            continue
            
        sorted_files = sorted(list(pawn_files))
        island_count = 1
        
        for i in range(1, len(sorted_files)):
            prev_file_index = ord(sorted_files[i-1]) - ord('a')
            curr_file_index = ord(sorted_files[i]) - ord('a')
            
            if curr_file_index - prev_file_index > 1:
                island_count += 1
        
        color_name = "white" if color == chess.WHITE else "black"
        islands[color_name] = island_count
    
    return islands

def find_advanced_pawns(board: chess.Board) -> dict:
    """Find pawns that have advanced past the 4th/5th rank"""
    advanced = {"white": [], "black": []}
    
    for color in [chess.WHITE, chess.BLACK]:
        pawns = board.pieces(chess.PAWN, color)
        
        for square in pawns:
            rank = chess.square_rank(square)
            file_char = chess.square_name(square)[0]
            
            # White pawns advanced past 4th rank, Black pawns advanced past 5th rank
            if (color == chess.WHITE and rank >= 4) or (color == chess.BLACK and rank <= 3):
                color_name = "white" if color == chess.WHITE else "black"
                advanced[color_name].append(f"{file_char}{rank+1}")
    
    return advanced

def analyze_piece_activity(board: chess.Board) -> dict:
    """Analyze piece activity and mobility"""
    
    return {
        "mobility_scores": calculate_mobility_scores(board),
        "active_pieces": find_most_active_pieces(board),
        "trapped_pieces": find_potentially_trapped_pieces(board)
    }

def calculate_mobility_scores(board: chess.Board) -> dict:
    """Calculate mobility (number of legal moves) for each piece type"""
    mobility = {"white": {}, "black": {}}
    
    for color in [chess.WHITE, chess.BLACK]:
        color_name = "white" if color == chess.WHITE else "black"
        
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            pieces = board.pieces(piece_type, color)
            total_mobility = 0
            
            for square in pieces:
                piece_moves = len([
                    move for move in board.legal_moves 
                    if move.from_square == square
                ])
                total_mobility += piece_moves
            
            piece_name = chess.piece_name(piece_type)
            mobility[color_name][piece_name] = total_mobility
    
    return mobility

def find_most_active_pieces(board: chess.Board) -> list[str]:
    """Find pieces with high mobility"""
    active_pieces = []
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_moves = len([
                move for move in board.legal_moves 
                if move.from_square == square
            ])
            
            if piece_moves >= 5:  # Arbitrary threshold for "active"
                square_name = chess.square_name(square)
                piece_name = piece.symbol()
                active_pieces.append(f"{piece_name}{square_name}")
    
    return active_pieces

def find_potentially_trapped_pieces(board: chess.Board) -> list[str]:
    """Find pieces with very low mobility (potentially trapped)"""
    trapped = []
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type != chess.PAWN:  # Don't count pawns
            piece_moves = len([
                move for move in board.legal_moves 
                if move.from_square == square
            ])
            
            if piece_moves <= 1:  # Very limited mobility
                square_name = chess.square_name(square)
                piece_name = piece.symbol()
                trapped.append(f"{piece_name}{square_name}")
    
    return trapped

def analyze_king_safety(board: chess.Board) -> dict:
    """Analyze king safety for both sides"""
    
    return {
        "castling_status": analyze_castling_status(board),
        "king_positions": get_king_positions(board),
        "pawn_shields": analyze_pawn_shields(board)
    }

def analyze_castling_status(board: chess.Board) -> dict:
    """Check castling rights and whether kings have castled"""
    
    return {
        "white_can_castle_kingside": board.has_kingside_castling_rights(chess.WHITE),
        "white_can_castle_queenside": board.has_queenside_castling_rights(chess.WHITE),
        "black_can_castle_kingside": board.has_kingside_castling_rights(chess.BLACK),
        "black_can_castle_queenside": board.has_queenside_castling_rights(chess.BLACK),
        "white_has_castled": not board.has_castling_rights(chess.WHITE),
        "black_has_castled": not board.has_castling_rights(chess.BLACK)
    }

def get_king_positions(board: chess.Board) -> dict:
    """Get current king positions"""
    
    white_king = board.king(chess.WHITE)
    black_king = board.king(chess.BLACK)
    
    return {
        "white_king": chess.square_name(white_king) if white_king else None,
        "black_king": chess.square_name(black_king) if black_king else None
    }

def analyze_pawn_shields(board: chess.Board) -> dict:
    """Analyze pawn shields in front of kings"""
    shields = {"white": 0, "black": 0}
    
    white_king = board.king(chess.WHITE)
    black_king = board.king(chess.BLACK)
    
    if white_king:
        shields["white"] = count_pawn_shield(board, white_king, chess.WHITE)
    
    if black_king:
        shields["black"] = count_pawn_shield(board, black_king, chess.BLACK)
    
    return shields

def count_pawn_shield(board: chess.Board, king_square: int, color: chess.Color) -> int:
    """Count pawns protecting the king"""
    king_file = chess.square_file(king_square)
    king_rank = chess.square_rank(king_square)
    
    shield_count = 0
    
    # Check pawns in front of king (3 files: left, center, right)
    for file_offset in [-1, 0, 1]:
        shield_file = king_file + file_offset
        if 0 <= shield_file <= 7:
            # Look for pawns 1 or 2 ranks ahead
            for rank_offset in [1, 2]:
                if color == chess.WHITE:
                    shield_rank = king_rank + rank_offset
                else:
                    shield_rank = king_rank - rank_offset
                
                if 0 <= shield_rank <= 7:
                    shield_square = chess.square(shield_file, shield_rank)
                    piece = board.piece_at(shield_square)
                    
                    if piece and piece.piece_type == chess.PAWN and piece.color == color:
                        shield_count += 1
                        break  # Found pawn on this file
    
    return shield_count

def analyze_board_control(board: chess.Board) -> dict:
    """Analyze file control and key squares"""
    
    return {
        "open_files": find_open_files(board),
        "semi_open_files": find_semi_open_files(board),
        "closed_files": find_closed_files(board)
    }

def find_open_files(board: chess.Board) -> list[str]:
    """Find files with no pawns"""
    files_with_pawns = set()
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN:
            file_char = chess.square_name(square)[0]
            files_with_pawns.add(file_char)
    
    all_files = set('abcdefgh')
    open_files = list(all_files - files_with_pawns)
    return sorted(open_files)

def find_semi_open_files(board: chess.Board) -> dict:
    """Find files with pawns for only one side"""
    semi_open = {"white": [], "black": []}
    
    for file_char in 'abcdefgh':
        white_pawns_on_file = any(
            board.piece_at(square) and 
            board.piece_at(square).piece_type == chess.PAWN and 
            board.piece_at(square).color == chess.WHITE
            for square in chess.SQUARES
            if chess.square_name(square)[0] == file_char
        )
        
        black_pawns_on_file = any(
            board.piece_at(square) and 
            board.piece_at(square).piece_type == chess.PAWN and 
            board.piece_at(square).color == chess.BLACK
            for square in chess.SQUARES
            if chess.square_name(square)[0] == file_char
        )
        
        if white_pawns_on_file and not black_pawns_on_file:
            semi_open["black"].append(file_char)
        elif black_pawns_on_file and not white_pawns_on_file:
            semi_open["white"].append(file_char)
    
    return semi_open

def find_closed_files(board: chess.Board) -> list[str]:
    """Find files with pawns from both sides"""
    closed_files = []
    
    for file_char in 'abcdefgh':
        white_pawns_on_file = any(
            board.piece_at(square) and 
            board.piece_at(square).piece_type == chess.PAWN and 
            board.piece_at(square).color == chess.WHITE
            for square in chess.SQUARES
            if chess.square_name(square)[0] == file_char
        )
        
        black_pawns_on_file = any(
            board.piece_at(square) and 
            board.piece_at(square).piece_type == chess.PAWN and 
            board.piece_at(square).color == chess.BLACK
            for square in chess.SQUARES
            if chess.square_name(square)[0] == file_char
        )
        
        if white_pawns_on_file and black_pawns_on_file:
            closed_files.append(file_char)
    
    return closed_files

def determine_game_phase(board: chess.Board) -> str:
    """Determine if position is opening/middlegame/endgame"""
    
    # Count major pieces (not pawns or kings)
    major_pieces = 0
    for piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
        major_pieces += len(board.pieces(piece_type, chess.WHITE))
        major_pieces += len(board.pieces(piece_type, chess.BLACK))
    
    # Also consider move number
    move_number = board.fullmove_number
    
    if move_number < 15 and major_pieces > 12:
        return "opening"
    elif major_pieces <= 6:  # Few pieces left
        return "endgame"
    else:
        return "middlegame"

def analyze_special_situations(board: chess.Board) -> dict:
    """Analyze special situations like check, checkmate, stalemate"""
    
    return {
        "in_check": board.is_check(),
        "is_checkmate": board.is_checkmate(),
        "is_stalemate": board.is_stalemate(),
        "is_insufficient_material": board.is_insufficient_material(),
        "can_claim_draw": board.can_claim_draw(),
        "legal_moves_count": len(list(board.legal_moves))
    }
