#!/usr/bin/env python3
"""Chess vision proof-of-concept: analyze chess board screenshots."""

import argparse
import base64
import json
from pathlib import Path
import re
import sys
from textwrap import dedent
from typing import List
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from PIL import Image
from difflib import SequenceMatcher


# Pydantic models for structured output
class ChessPieceLocation(BaseModel):
  square: str = Field(description="Square like 'e1', 'a8'")
  piece: str = Field(
      description=(
          "Piece like 'king', 'queen', 'rook', 'bishop', 'knight', 'pawn'"
      )
  )
  color: str = Field(description="'white' or 'black'")


class ChessPosition(BaseModel):
  pieces: List[ChessPieceLocation] = Field(
      description='List of all pieces visible on the board'
  )


class BoundingBox(BaseModel):
  """Represents a bounding box with its 2D coordinates and associated label."""
  box_2d: List[int] = Field(description="2D coordinates [y_min, x_min, y_max, x_max] normalized to 0-1000")
  label: str = Field(description="Label for the detected object")


class BoundingBoxResponse(BaseModel):
  """Response containing detected bounding boxes."""
  bounding_boxes: List[BoundingBox] = Field(description="List of detected bounding boxes")


def image_to_base64(image_path: str) -> str:
  """Convert image to base64 string."""
  with open(image_path, 'rb') as f:
    return base64.b64encode(f.read()).decode('utf-8')


def convert_oneshot_to_fen(oneshot_text: str) -> str:
  """Convert oneshot format to FEN notation."""
  board = [['.' for _ in range(8)] for _ in range(8)]

  piece_map = {
      'king': {'white': 'K', 'black': 'k'},
      'queen': {'white': 'Q', 'black': 'q'},
      'rook': {'white': 'R', 'black': 'r'},
      'rooks': {'white': 'R', 'black': 'r'},  # Handle plural
      'bishop': {'white': 'B', 'black': 'b'},
      'bishops': {'white': 'B', 'black': 'b'},  # Handle plural
      'knight': {'white': 'N', 'black': 'n'},
      'knights': {'white': 'N', 'black': 'n'},  # Handle plural
      'pawn': {'white': 'P', 'black': 'p'},
      'pawns': {'white': 'P', 'black': 'p'},  # Handle plural
  }

  # Parse white pieces
  white_section = re.search(
      r'\*\*White Pieces:\*\*(.*?)(?:\*\*Black Pieces:|$)',
      oneshot_text,
      re.DOTALL,
  )
  if white_section:
    for line in white_section.group(1).strip().split('\n'):
      line = line.strip()
      if line.startswith('*') and ':' in line:
        # Extract piece type and squares from "*   King: e1" format
        colon_pos = line.find(':')
        piece_part = (
            line[1:colon_pos].strip().lower()
        )  # Remove * and get piece type
        squares_part = line[colon_pos + 1 :].strip()  # Get squares part

        if piece_part in piece_map:
          squares = [s.strip() for s in squares_part.split(',')]
          for square in squares:
            if len(square) == 2 and square[0].isalpha() and square[1].isdigit():
              col = ord(square[0]) - ord('a')
              row = 8 - int(square[1])
              if 0 <= col < 8 and 0 <= row < 8:
                board[row][col] = piece_map[piece_part]['white']

  # Parse black pieces
  black_section = re.search(
      r'\*\*Black Pieces:\*\*(.*)', oneshot_text, re.DOTALL
  )
  if black_section:
    for line in black_section.group(1).strip().split('\n'):
      line = line.strip()
      if line.startswith('*') and ':' in line:
        # Extract piece type and squares from "*   King: e8" format
        colon_pos = line.find(':')
        piece_part = (
            line[1:colon_pos].strip().lower()
        )  # Remove * and get piece type
        squares_part = line[colon_pos + 1 :].strip()  # Get squares part

        if piece_part in piece_map:
          squares = [s.strip() for s in squares_part.split(',')]
          for square in squares:
            if len(square) == 2 and square[0].isalpha() and square[1].isdigit():
              col = ord(square[0]) - ord('a')
              row = 8 - int(square[1])
              if 0 <= col < 8 and 0 <= row < 8:
                board[row][col] = piece_map[piece_part]['black']

  # Convert board to FEN
  fen_parts = []
  for row in board:
    fen_row = ''
    empty_count = 0
    for cell in row:
      if cell == '.':
        empty_count += 1
      else:
        if empty_count > 0:
          fen_row += str(empty_count)
          empty_count = 0
        fen_row += cell
    if empty_count > 0:
      fen_row += str(empty_count)
    fen_parts.append(fen_row)

  return '/'.join(fen_parts)


def convert_json_to_fen(json_text: str) -> str:
  """Convert JSON format to FEN notation."""
  # Strip code fences if present
  json_text = json_text.strip()
  if json_text.startswith('```json'):
    json_text = json_text[7:]  # Remove ```json
  elif json_text.startswith('```'):
    json_text = json_text[3:]  # Remove ```
  if json_text.endswith('```'):
    json_text = json_text[:-3]  # Remove trailing ```
  json_text = json_text.strip()

  try:
    data = json.loads(json_text)
  except Exception as e:
    return f'Invalid JSON: {e}'

  board = [['.' for _ in range(8)] for _ in range(8)]

  piece_map = {
      'king': {'white': 'K', 'black': 'k'},
      'queen': {'white': 'Q', 'black': 'q'},
      'rook': {'white': 'R', 'black': 'r'},
      'rooks': {'white': 'R', 'black': 'r'},  # Handle plural
      'bishop': {'white': 'B', 'black': 'b'},
      'bishops': {'white': 'B', 'black': 'b'},  # Handle plural
      'knight': {'white': 'N', 'black': 'n'},
      'knights': {'white': 'N', 'black': 'n'},  # Handle plural
      'pawn': {'white': 'P', 'black': 'p'},
      'pawns': {'white': 'P', 'black': 'p'},  # Handle plural
  }

  for color in ['white', 'black']:
    if color in data:
      for piece_type, squares in data[color].items():
        if piece_type in piece_map and squares is not None:
          if isinstance(squares, str):
            squares = [squares]
          for square in squares:
            square = square.strip()
            if len(square) == 2 and square[0].isalpha() and square[1].isdigit():
              col = ord(square[0]) - ord('a')
              row = 8 - int(square[1])
              # Add bounds checking
              if 0 <= col < 8 and 0 <= row < 8:
                board[row][col] = piece_map[piece_type][color]

  # Convert board to FEN
  fen_parts = []
  for row in board:
    fen_row = ''
    empty_count = 0
    for cell in row:
      if cell == '.':
        empty_count += 1
      else:
        if empty_count > 0:
          fen_row += str(empty_count)
          empty_count = 0
        fen_row += cell
    if empty_count > 0:
      fen_row += str(empty_count)
    fen_parts.append(fen_row)

  return '/'.join(fen_parts)


def convert_pydantic_to_fen(pydantic_result) -> str:
  """Convert Pydantic ChessPosition to FEN notation."""
  board = [['.' for _ in range(8)] for _ in range(8)]

  piece_map = {
      'king': {'white': 'K', 'black': 'k'},
      'queen': {'white': 'Q', 'black': 'q'},
      'rook': {'white': 'R', 'black': 'r'},
      'bishop': {'white': 'B', 'black': 'b'},
      'knight': {'white': 'N', 'black': 'n'},
      'pawn': {'white': 'P', 'black': 'p'},
  }

  for piece_location in pydantic_result.pieces:
    square = piece_location.square
    piece_type = piece_location.piece
    color = piece_location.color

    if len(square) == 2 and piece_type in piece_map:
      col = ord(square[0]) - ord('a')
      row = 8 - int(square[1])
      board[row][col] = piece_map[piece_type][color]

  # Convert board to FEN
  fen_parts = []
  for row in board:
    fen_row = ''
    empty_count = 0
    for cell in row:
      if cell == '.':
        empty_count += 1
      else:
        if empty_count > 0:
          fen_row += str(empty_count)
          empty_count = 0
        fen_row += cell
    if empty_count > 0:
      fen_row += str(empty_count)
    fen_parts.append(fen_row)

  return '/'.join(fen_parts)


def create_lichess_link(fen: str) -> str:
  """Create a Lichess analysis link for the given FEN."""
  return f'https://lichess.org/analysis/{fen}'


def similarity_ratio(a: str, b: str) -> float:
  """Calculate similarity ratio between two strings (0.0 to 1.0)."""
  return SequenceMatcher(None, a, b).ratio()


def fen_board_to_squares(fen: str) -> dict:
  """Convert FEN board portion to square -> piece mapping."""
  board_part = fen.split()[0]  # Take only the board part, ignore turn/castling/etc
  squares = {}
  
  ranks = board_part.split('/')
  for rank_idx, rank in enumerate(ranks):
    file_idx = 0
    for char in rank:
      if char.isdigit():
        file_idx += int(char)  # Skip empty squares
      else:
        square = chr(ord('a') + file_idx) + str(8 - rank_idx)
        squares[square] = char
        file_idx += 1
  
  return squares


def compare_fen_positions(canonical_fen: str, test_fen: str) -> dict:
  """Compare two FEN positions and return detailed differences."""
  canonical_squares = fen_board_to_squares(canonical_fen)
  test_squares = fen_board_to_squares(test_fen)
  
  all_squares = set(canonical_squares.keys()) | set(test_squares.keys())
  
  correct = 0
  incorrect = 0
  details = []
  
  for square in sorted(all_squares):
    canonical_piece = canonical_squares.get(square, '.')
    test_piece = test_squares.get(square, '.')
    
    if canonical_piece == test_piece:
      correct += 1
    else:
      incorrect += 1
      if canonical_piece == '.' and test_piece != '.':
        details.append(f"{square}: Extra {test_piece}")
      elif canonical_piece != '.' and test_piece == '.':
        details.append(f"{square}: Missing {canonical_piece}")
      else:
        details.append(f"{square}: {canonical_piece} → {test_piece}")
  
  return {
    'correct_squares': correct,
    'incorrect_squares': incorrect,
    'accuracy': correct / (correct + incorrect) * 100 if (correct + incorrect) > 0 else 0,
    'details': details,
  }


def crop_image_with_bounding_box(image_path: str, bounding_box: BoundingBox, padding: float = 0.0, output_path: str = None) -> str:
  """Crop image using bounding box coordinates with optional padding and save the result."""
  with Image.open(image_path) as img:
    width, height = img.size
    
    # Add padding to normalized coordinates (0-1000 scale)
    padding_normalized = int(padding * 1000)  # Convert padding to 0-1000 scale
    
    # Convert normalized coordinates (0-1000) to actual pixels with optional padding
    y_min = max(0, int((bounding_box.box_2d[0] - padding_normalized) / 1000 * height))
    x_min = max(0, int((bounding_box.box_2d[1] - padding_normalized) / 1000 * width))
    y_max = min(height, int((bounding_box.box_2d[2] + padding_normalized) / 1000 * height))
    x_max = min(width, int((bounding_box.box_2d[3] + padding_normalized) / 1000 * width))
    
    # Crop the image (PIL uses left, top, right, bottom)
    cropped_img = img.crop((x_min, y_min, x_max, y_max))
    
    # Normalize cropped image to 1024px (maintain aspect ratio)
    cropped_img.thumbnail((1024, 1024), Image.LANCZOS)
    
    # Generate output filename if not provided
    if output_path is None:
      input_path = Path(image_path)
      output_path = str(input_path.parent / f"{input_path.stem}_cropped{input_path.suffix}")
    
    # Save cropped image
    cropped_img.save(output_path)
    print(f"Cropped chess board saved to: {output_path}")
    
    return output_path


def analyze_chess_image(image_path: str, prompt_level: str = 'describe'):
  """Analyze chess board image with different prompt levels."""

  # Load and encode image
  image_data = image_to_base64(image_path)

  # Different prompt levels for iteration
  prompts = {
      'describe': 'Describe what you see in this image in detail.',
      'chess': dedent("""\
            Analyze this chess position. Describe:
            - The current board setup
            - Which pieces you can see and where
            - Whose turn it appears to be
            - Any notable features (checks, captures, etc.)
            """),
      'structured': dedent("""\
            Analyze this chess position and provide:
            1. Board description (piece locations)
            2. Game phase (opening/middlegame/endgame)
            3. Material count for both sides  
            4. Any tactical elements visible
            5. Estimate of the current position evaluation
            """),
      'fen': dedent("""\
            Analyze this chess board image and extract:
            1. The position in FEN notation if possible
            2. Whose turn it is (white/black)
            3. Castling availability
            4. En passant possibilities
            5. Move number estimate

            Be as precise as possible with piece identification and square locations.
            """),
      'unstructured': dedent("""\
            Look at this chess board and tell me where every piece is located. 
            Use whatever format you think is clearest and most accurate.
            Only report pieces you can clearly see - do not guess.
            """),
      'oneshot': dedent("""\
            Analyze this chess position and list all pieces in the exact format shown below.

            Example format:
            **White Pieces:**
            * King: e1
            * Queen: d1  
            * Rooks: a1, h1
            * Bishops: c1, f1
            * Knights: c3, f3
            * Pawns: a2, b2, f2, g2, h2

            **Black Pieces:**
            * King: e8
            * Queen: d8
            * Rooks: a8, h8  
            * Bishops: c8, f8
            * Knights: b8, f6
            * Pawns: a7, b7, d4, e6, f7, g7, h7

            Now analyze the chess board in this image and provide the piece locations in exactly the same format. 
            Only list pieces you can clearly see - do not guess or infer.
            """),
      'json': dedent("""\
            Look at this chess board and identify all piece locations.
            
            Return the result as JSON in this exact format:
            {{
              "white": {{
                "king": "e1",
                "queen": "d1", 
                "rooks": ["a1", "h1"],
                "bishops": ["c1", "f1"],
                "knights": ["c3", "f3"],
                "pawns": ["a2", "b2", "f2", "g2", "h2"]
              }},
              "black": {{
                "king": "e8",
                "queen": "d8",
                "rooks": ["a8", "h8"],
                "bishops": ["c8", "f8"],
                "knights": ["b8", "f6"],
                "pawns": ["a7", "b7", "d4", "e6", "f7", "g7", "h7"]
              }}
            }}
            
            Only include pieces you can clearly see. Use empty arrays [] for piece types with no pieces.
            """),
        
        'board_detection': "Detect the chess board. Output bounding box with label.",
        
        'crop_and_detect': "Full pipeline: detect board, crop, then extract pieces",
        
        'crop_and_test_all': "Crop board, then test all four approaches",
  }

  # Handle structured output cases differently
  if prompt_level == 'pydantic':
    # Create the human message template with both text and image
    human_message = HumanMessagePromptTemplate(
        prompt=[
            PromptTemplate(
                template=(
                    'Look at this chess board and identify the exact location'
                    ' of every piece you can clearly see. Only report pieces'
                    ' that are definitely visible - do not guess.'
                )
            ),
            ImagePromptTemplate(
                input_variables=['image_data'],
                template={'url': 'data:image/png;base64,{image_data}'},
            ),
        ]
    )

    # Initialize model with structured output
    model = ChatGoogleGenerativeAI(
        model='gemini-2.5-flash-lite',
        temperature=0.1,
    ).with_structured_output(ChessPosition)

    # Create the chain
    prompt = ChatPromptTemplate.from_messages([human_message])
    chain = {'image_data': RunnablePassthrough()} | prompt | model

    # Get response
    response = chain.invoke(image_data)
    return response  # Return the structured object
    
  elif prompt_level == 'board_detection':
    # Create the human message template for bounding box detection
    human_message = HumanMessagePromptTemplate(
        prompt=[
            PromptTemplate(template=prompts[prompt_level]),
            ImagePromptTemplate(
                input_variables=['image_data'],
                template={'url': 'data:image/png;base64,{image_data}'},
            ),
        ]
    )

    # Initialize model with bounding box structured output
    model = ChatGoogleGenerativeAI(
        model='gemini-2.5-flash-lite',
        temperature=0.1,
    ).with_structured_output(BoundingBoxResponse)

    # Create the chain
    prompt = ChatPromptTemplate.from_messages([human_message])
    chain = {'image_data': RunnablePassthrough()} | prompt | model

    # Get response
    response = chain.invoke(image_data)
    
    # If we got bounding boxes, crop the image
    if response.bounding_boxes:
      chess_board_box = response.bounding_boxes[0]  # Assume first box is the chess board
      cropped_path = crop_image_with_bounding_box(image_path, chess_board_box)
      print(f"\nCropped chess board coordinates: {chess_board_box.box_2d}")
      print(f"Cropped image saved to: {cropped_path}")
    
    return response  # Return the structured object
    
  elif prompt_level == 'crop_and_detect':
    print("🔍 Step 1: Detecting chess board...")
    
    # Step 1: Detect and crop the chess board
    board_detection_response = analyze_chess_image(image_path, 'board_detection')
    
    if not board_detection_response.bounding_boxes:
      return "No chess board detected!"
    
    chess_board_box = board_detection_response.bounding_boxes[0]
    cropped_path = crop_image_with_bounding_box(image_path, chess_board_box)
    print(f"✅ Board detected and cropped to: {cropped_path}")
    
    print("\n🔍 Step 2: Extracting pieces from cropped board...")
    
    # Step 2: Extract pieces from the cropped image
    pieces_response = analyze_chess_image(cropped_path, 'pydantic')
    print(f"✅ Found {len(pieces_response.pieces)} pieces")
    
    return pieces_response  # Return the structured piece data
    
  elif prompt_level == 'crop_and_test_all':
    print("🔍 Step 1: Detecting and cropping chess board...")
    
    # Step 1: Detect and crop the chess board
    board_detection_response = analyze_chess_image(image_path, 'board_detection')
    
    if not board_detection_response.bounding_boxes:
      return "No chess board detected!"
    
    chess_board_box = board_detection_response.bounding_boxes[0]
    cropped_path = crop_image_with_bounding_box(image_path, chess_board_box)
    print(f"✅ Board detected and cropped to: {cropped_path}")
    
    # Step 2: Test all four approaches on the cropped board
    test_approaches = ['unstructured', 'oneshot', 'json', 'pydantic']
    results = {}
    
    for approach in test_approaches:
      print(f"\n🔍 Testing {approach.upper()} on cropped board...")
      try:
        result = analyze_chess_image(cropped_path, approach)
        results[approach] = result
        
        # Convert to FEN for approaches that support it
        if approach in ['oneshot', 'json', 'pydantic']:
          if approach == 'oneshot':
            fen = convert_oneshot_to_fen(result)
          elif approach == 'json':
            fen = convert_json_to_fen(result)
          elif approach == 'pydantic':
            fen = convert_pydantic_to_fen(result)
            piece_count = len(result.pieces)
            print(f"✅ Found {piece_count} pieces")
          
          print(f"FEN: {fen}")
          if fen and not fen.startswith('Invalid'):
            print(f"Lichess: {create_lichess_link(fen)}")
            
            # Add similarity comparison if canonical FEN provided
            if 'canonical_fen' in globals():
              canonical = globals()['canonical_fen']
              similarity = similarity_ratio(canonical.split()[0], fen.split()[0])
              print(f"📊 Similarity to canonical: {similarity:.3f}")
        else:
          print(f"✅ {approach} completed")
          
      except Exception as e:
        print(f"❌ Error with {approach}: {e}")
        results[approach] = f"Error: {e}"
    
    return results
  else:
    # Create the human message template with both text and image
    human_message = HumanMessagePromptTemplate(
        prompt=[
            PromptTemplate(template=prompts[prompt_level]),
            ImagePromptTemplate(
                input_variables=['image_data'],
                template={'url': 'data:image/png;base64,{image_data}'},
            ),
        ]
    )

    # Initialize model
    model = ChatGoogleGenerativeAI(
        model='gemini-2.5-flash-lite',
        temperature=0.1,
    )

    # Create the chain
    prompt = ChatPromptTemplate.from_messages([human_message])
    chain = {'image_data': RunnablePassthrough()} | prompt | model

    # Get response
    response = chain.invoke(image_data)
    return response.content


def main():
  parser = argparse.ArgumentParser(description='Chess vision analysis tool')
  parser.add_argument('image_path', help='Path to chess board image')
  parser.add_argument('prompt_level', nargs='?', default='describe',
                     help='Analysis method: describe, chess, structured, fen, unstructured, oneshot, json, pydantic, board_detection, crop_and_detect, crop_and_test_all, all')
  parser.add_argument('--fen', help='Canonical FEN position for accuracy comparison')
  
  args = parser.parse_args()

  if not Path(args.image_path).exists():
    print(f'Image file not found: {args.image_path}')
    sys.exit(1)

  # Make canonical FEN available globally for comparison
  if args.fen:
    globals()['canonical_fen'] = args.fen

  # Handle "all" option to run all FEN-generating tests
  if args.prompt_level == 'all':
    test_levels = ['oneshot', 'json', 'pydantic', 'structured']
    for i, level in enumerate(test_levels):
      if i > 0:
        print('\n' + '=' * 80)
      print(f'TESTING {level.upper()}')
      print('=' * 80)

      try:
        result = analyze_chess_image(args.image_path, level)
        print(result)

        # Convert to FEN for comparison
        if level in ['oneshot', 'json', 'pydantic']:
          print('\n' + '-' * 60)
          print('FEN CONVERSION:')

          fen = None
          if level == 'oneshot':
            fen = convert_oneshot_to_fen(result)
          elif level == 'json':
            fen = convert_json_to_fen(result)
          elif level == 'pydantic':
            fen = convert_pydantic_to_fen(result)
          
          if fen:
            print(f'FEN: {fen}')
            if not fen.startswith('Invalid'):
              print(f'Lichess: {create_lichess_link(fen)}')
              
              # Compare to canonical FEN if provided
              if args.fen:
                comparison = compare_fen_positions(args.fen, fen)
                print(f'\n📊 ACCURACY vs CANONICAL:')
                print(f'Correct squares: {comparison["correct_squares"]}/64 ({comparison["accuracy"]:.1f}%)')
                print(f'Levenshtein distance: {comparison["levenshtein_distance"]}')
                if comparison['details']:
                  print(f'Errors: {", ".join(comparison["details"][:5])}{"..." if len(comparison["details"]) > 5 else ""}')

      except Exception as e:
        print(f'Error with {level}: {e}')
    return

  # Single test mode
  print(f"Analyzing {args.image_path} with '{args.prompt_level}' prompt...")
  print('=' * 60)

  try:
    result = analyze_chess_image(args.image_path, args.prompt_level)
    print(result)

    # Convert to FEN for comparison
    if args.prompt_level in ['oneshot', 'json', 'pydantic', 'crop_and_detect']:
      print('\n' + '=' * 60)
      print('FEN CONVERSION:')

      fen = None
      if args.prompt_level == 'oneshot':
        fen = convert_oneshot_to_fen(result)
      elif args.prompt_level == 'json':
        fen = convert_json_to_fen(result)
      elif args.prompt_level in ['pydantic', 'crop_and_detect']:
        fen = convert_pydantic_to_fen(result)
      
      if fen:
        print(f'FEN: {fen}')
        if not fen.startswith('Invalid'):
          print(f'Lichess: {create_lichess_link(fen)}')
          
          # Compare to canonical FEN if provided
          if args.fen:
            comparison = compare_fen_positions(args.fen, fen)
            print(f'\n📊 ACCURACY vs CANONICAL:')
            print(f'Correct squares: {comparison["correct_squares"]}/64 ({comparison["accuracy"]:.1f}%)')
            print(f'Levenshtein distance: {comparison["levenshtein_distance"]}')
            if comparison['details']:
              print(f'Errors: {", ".join(comparison["details"][:5])}{"..." if len(comparison["details"]) > 5 else ""}')

  except Exception as e:
    print(f'Error: {e}')


if __name__ == '__main__':
  main()
