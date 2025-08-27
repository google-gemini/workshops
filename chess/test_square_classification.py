#!/usr/bin/env python3
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

"""Test square-by-square chess position detection using live HDMI capture

This test:
1. Captures from actual HDMI video device
2. Uses existing segmentation + crop logic
3. Partitions board into 64 squares
4. Runs batch Roboflow classification
5. Compares with current approach
"""

import argparse
import asyncio
from datetime import datetime
from pathlib import Path
import time
import cv2
import numpy as np
from PIL import Image
# Import existing components
from roboflow import ChessVisionPipeline, roboflow_piece_detection

# HDMI capture settings (same as companion)
HDMI_VIDEO_DEVICE = "/dev/video11"


class SquareClassificationTester:
  """Test square-by-square classification vs current approach"""

  def __init__(self, debug_mode=True):
    self.debug_mode = debug_mode
    if self.debug_mode:
      self.debug_dir = Path("debug_square_classification")
      self.debug_dir.mkdir(exist_ok=True)
      print(f"🐛 Debug mode: saving frames to {self.debug_dir}")

    self.pipeline = ChessVisionPipeline(
        debug_dir=str(self.debug_dir) if self.debug_mode else None
    )

    # Video capture
    self.cap = None

  def setup_video_capture(self):
    """Initialize HDMI video capture"""
    print(f"📹 Initializing HDMI capture from {HDMI_VIDEO_DEVICE}")
    self.cap = cv2.VideoCapture(HDMI_VIDEO_DEVICE)

    if not self.cap.isOpened():
      raise ValueError(f"Cannot open video device {HDMI_VIDEO_DEVICE}")

    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    print("✅ HDMI capture ready")

  def capture_and_save_frame(self):
    """Capture current frame and save for processing"""
    if not self.cap:
      self.setup_video_capture()

    ret, frame = self.cap.read()
    if not ret:
      raise ValueError("Failed to capture frame")

    # Convert and save
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_frame = Image.fromarray(frame_rgb)

    timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
    frame_path = self.debug_dir / f"captured_frame_{timestamp}.png"
    pil_frame.save(frame_path)

    print(f"📸 Captured frame: {frame.shape[:2]} saved to {frame_path}")
    return str(frame_path), pil_frame

  def partition_board_into_squares(self, board_image):
    """Partition board crop into 64 individual square images"""
    width, height = board_image.size
    square_width = width // 8
    square_height = height // 8

    print(
        f"📐 Partitioning {width}x{height} board into"
        f" {square_width}x{square_height} squares"
    )

    squares = []
    for row in range(8):
      for col in range(8):
        left = col * square_width
        top = row * square_height
        right = left + square_width
        bottom = top + square_height

        square_crop = board_image.crop((left, top, right, bottom))
        chess_notation = f"{chr(ord('a') + col)}{8-row}"  # e.g., "e4"

        squares.append({
            "image": square_crop,
            "row": row,
            "col": col,
            "position": chess_notation,
            "coords": (left, top, right, bottom),
        })

    return squares

  def classify_squares_batch(self, squares, model_id="chess.comdetection/4"):
    """Classify all 64 squares in a single batch Roboflow call"""
    try:
      square_images = [sq["image"] for sq in squares]

      print(
          f"🔍 Running batch classification on {len(square_images)} squares"
          f" with {model_id}..."
      )

      # Single batch call to Roboflow
      results = self.pipeline.client.infer(square_images, model_id=model_id)

      # Handle both single result and list of results
      if not isinstance(results, list):
        results = [results]

      # Combine results with square metadata
      classified_squares = []
      for i, (square_meta, result) in enumerate(zip(squares, results)):
        predictions = result.get("predictions", []) if result else []
        classified_squares.append(
            {**square_meta, "predictions": predictions, "square_index": i}
        )

      print(
          "✅ Batch classification complete -"
          f" {len(classified_squares)} squares processed"
      )
      return classified_squares

    except Exception as e:
      print(f"❌ Batch square classification failed: {e}")
      return []

  def squares_to_fen(self, classified_squares, confidence_threshold=0.3):
    """Convert classified squares directly to FEN notation"""
    # Initialize 8x8 board
    board = [[None for _ in range(8)] for _ in range(8)]

    piece_mapping = {
        # Standard format (2dcpd/2 and chess.comdetection/4)
        "white-king": "K",
        "white-queen": "Q",
        "white-rook": "R",
        "white-rock": "R",
        "white-bishop": "B",
        "white-knight": "N",
        "white-pawn": "P",
        "black-king": "k",
        "black-queen": "q",
        "black-rook": "r",
        "black-rock": "r",
        "black-bishop": "b",
        "black-knight": "n",
        "black-pawn": "p",
        "empty": None,
        "board": None,
    }

    classified_count = 0
    empty_count = 0
    debug_details = []

    for square in classified_squares:
      row, col = square["row"], square["col"]
      predictions = square["predictions"]
      position = square["position"]

      if predictions:
        # Take highest confidence prediction above threshold
        valid_preds = [
            p
            for p in predictions
            if p.get("confidence", 0) >= confidence_threshold
        ]

        if valid_preds:
          best_pred = max(valid_preds, key=lambda p: p.get("confidence", 0))
          piece_class = best_pred.get("class", "").lower()
          confidence = best_pred.get("confidence", 0)

          # Map to FEN symbol
          fen_symbol = piece_mapping.get(piece_class)

          if fen_symbol:  # Valid piece
            board[row][col] = fen_symbol
            classified_count += 1
            debug_details.append(
                f"{position}: {piece_class} ({confidence:.2f}) -> {fen_symbol}"
            )
          else:
            empty_count += 1
            if piece_class not in ["empty", "board", ""]:
              debug_details.append(
                  f"{position}: UNKNOWN {piece_class} ({confidence:.2f})"
              )
        else:
          empty_count += 1
          debug_details.append(f"{position}: low confidence")
      else:
        empty_count += 1
        debug_details.append(f"{position}: no predictions")

    print(
        f"📊 Square classification: {classified_count} pieces,"
        f" {empty_count} empty"
    )

    if self.debug_mode and debug_details:
      print("🔍 Square details:")
      for detail in debug_details[:16]:  # Show first 16 for brevity
        print(f"  {detail}")
      if len(debug_details) > 16:
        print(f"  ... and {len(debug_details) - 16} more")

    return self.board_to_fen_string_from_symbols(board)

  def board_to_fen_string_from_symbols(self, board):
    """Convert 8x8 symbol board to FEN notation"""
    fen_rows = []

    for row in range(8):
      fen_row = ""
      empty_count = 0

      for col in range(8):
        symbol = board[row][col]

        if symbol is None:  # Empty square
          empty_count += 1
        else:
          # Add accumulated empty squares
          if empty_count > 0:
            fen_row += str(empty_count)
            empty_count = 0
          # Add piece symbol
          fen_row += symbol

      # Add remaining empty squares
      if empty_count > 0:
        fen_row += str(empty_count)

      fen_rows.append(fen_row)

    return "/".join(fen_rows)

  async def test_square_classification(self, model_id="chess.comdetection/4"):
    """Test the square-by-square approach and compare with current method"""
    print(f"🧪 Testing square-by-square classification with {model_id}")

    # Step 1: Capture from video device
    frame_path, pil_frame = self.capture_and_save_frame()

    # Step 2: Segment board (using existing logic)
    print("🎯 Running board segmentation...")
    segmentation_result = self.pipeline.segment_board_direct(pil_frame)
    bbox = self.pipeline.extract_bbox_from_segmentation(segmentation_result)

    if not bbox:
      print("❌ Board segmentation failed")
      return

    print(f"✅ Board detected with confidence {bbox['confidence']:.3f}")

    # Step 3: Crop board region
    board_crop = pil_frame.crop(bbox["coords"])

    if self.debug_mode:
      crop_path = self.debug_dir / "board_crop_test.png"
      board_crop.save(crop_path)
      print(f"💾 Saved board crop to {crop_path}")

    print(f"📐 Board crop: {board_crop.size}")

    # Step 4: Test square-by-square approach
    print("\n" + "=" * 50)
    print("🆕 TESTING SQUARE-BY-SQUARE APPROACH")
    print("=" * 50)

    start_time = time.time()

    # Partition into squares
    squares = self.partition_board_into_squares(board_crop)

    # Save sample squares for debugging
    if self.debug_mode:
      sample_squares = squares[::8]  # Every 8th square
      for sq in sample_squares:
        sq_path = self.debug_dir / f"square_{sq['position']}.png"
        sq["image"].save(sq_path)
      print(f"💾 Saved {len(sample_squares)} sample squares")

    # Batch classify
    classified_squares = self.classify_squares_batch(squares, model_id)

    if not classified_squares:
      print("❌ Square classification failed")
      return

    # Convert to FEN
    square_fen = self.squares_to_fen(classified_squares)
    square_time = time.time() - start_time

    print(f"🎯 Square method FEN: {square_fen}")
    print(f"⏱️  Square method time: {square_time:.2f}s")

    # Step 5: Test current approach for comparison
    print("\n" + "=" * 50)
    print("📊 TESTING CURRENT APPROACH")
    print("=" * 50)

    start_time = time.time()
    current_result = await roboflow_piece_detection(
        frame_path, debug_dir=str(self.debug_dir) if self.debug_mode else None
    )
    current_time = time.time() - start_time

    current_fen = current_result.get("consensus_fen", "FAILED")
    print(f"🎯 Current method FEN: {current_fen}")
    print(f"⏱️  Current method time: {current_time:.2f}s")

    # Step 6: Compare results
    print("\n" + "=" * 50)
    print("📋 COMPARISON RESULTS")
    print("=" * 50)
    print(f"Square method: {square_fen}")
    print(f"Current method: {current_fen}")

    if square_fen == current_fen:
      print("✅ IDENTICAL RESULTS!")
    else:
      print("⚠️  DIFFERENT RESULTS!")

      # Show differences
      if len(square_fen) == len(current_fen):
        differences = sum(1 for a, b in zip(square_fen, current_fen) if a != b)
        print(f"   Character differences: {differences}/{len(square_fen)}")

    print(
        f"⏱️  Time comparison: Square={square_time:.2f}s vs"
        f" Current={current_time:.2f}s"
    )

    # Step 7: Save full results if debug mode
    if self.debug_mode:
      results = {
          "timestamp": datetime.now().isoformat(),
          "square_method": {
              "fen": square_fen,
              "time": square_time,
              "model": model_id,
          },
          "current_method": {
              "fen": current_fen,
              "time": current_time,
              "details": current_result,
          },
          "identical": square_fen == current_fen,
      }

      import json

      results_path = self.debug_dir / "comparison_results.json"
      with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
      print(f"💾 Full results saved to {results_path}")

  def create_row_column_strips(self, board_image):
    """Create 8 horizontal strips (ranks) and 8 vertical strips (files)"""
    width, height = board_image.size
    strip_width = width // 8
    strip_height = height // 8

    print(f"📐 Creating strips from {width}x{height} board")

    strips = []

    # Create 8 horizontal strips (ranks)
    for rank in range(8):
      top = rank * strip_height
      bottom = (rank + 1) * strip_height
      rank_strip = board_image.crop((0, top, width, bottom))

      strips.append({
          "image": rank_strip,
          "type": "rank",
          "index": rank,
          "name": f"rank_{8-rank}",  # Chess rank numbering
          "coords": (0, top, width, bottom),
      })

    # Create 8 vertical strips (files)
    for file in range(8):
      left = file * strip_width
      right = (file + 1) * strip_width
      file_strip = board_image.crop((left, 0, right, height))

      strips.append({
          "image": file_strip,
          "type": "file",
          "index": file,
          "name": f"file_{chr(ord('a') + file)}",  # Chess file lettering
          "coords": (left, 0, right, height),
      })

    print(f"✅ Created {len(strips)} strips (8 ranks + 8 files)")
    return strips

  def classify_strips_batch(self, strips, model_id="chess.comdetection/4"):
    """Classify all rank/file strips in a single batch call"""
    try:
      strip_images = [strip["image"] for strip in strips]

      print(
          f"🔍 Running batch classification on {len(strip_images)} strips with"
          f" {model_id}..."
      )

      # Single batch call to Roboflow
      results = self.pipeline.client.infer(strip_images, model_id=model_id)

      # Handle both single result and list of results
      if not isinstance(results, list):
        results = [results]

      # Combine results with strip metadata
      classified_strips = []
      for i, (strip_meta, result) in enumerate(zip(strips, results)):
        predictions = result.get("predictions", []) if result else []
        classified_strips.append(
            {**strip_meta, "predictions": predictions, "strip_index": i}
        )

      print(
          f"✅ Strip classification complete - {len(classified_strips)} strips"
          " processed"
      )
      return classified_strips

    except Exception as e:
      print(f"❌ Strip classification failed: {e}")
      return []

  def strips_to_fen(
      self,
      classified_strips,
      board_width,
      board_height,
      confidence_threshold=0.3,
  ):
    """Convert strip classifications to FEN by intersecting rank/file data"""
    # Initialize 8x8 board
    board = [[None for _ in range(8)] for _ in range(8)]

    piece_mapping = {
        "white-king": "K",
        "white-queen": "Q",
        "white-rook": "R",
        "white-rock": "R",
        "white-bishop": "B",
        "white-knight": "N",
        "white-pawn": "P",
        "black-king": "k",
        "black-queen": "q",
        "black-rook": "r",
        "black-rock": "r",
        "black-bishop": "b",
        "black-knight": "n",
        "black-pawn": "p",
        "empty": None,
        "board": None,
    }

    # Separate rank and file strips
    rank_strips = [s for s in classified_strips if s["type"] == "rank"]
    file_strips = [s for s in classified_strips if s["type"] == "file"]

    print(
        f"🔍 Processing {len(rank_strips)} ranks and {len(file_strips)} files"
    )

    # Process each rank/file intersection
    for rank_strip in rank_strips:
      for file_strip in file_strips:
        rank_idx = rank_strip["index"]  # 0-7 from top
        file_idx = file_strip["index"]  # 0-7 from left

        # Find pieces that appear in both this rank and this file
        rank_pieces = self._extract_pieces_in_strip(
            rank_strip, board_width, board_height, "rank", confidence_threshold
        )
        file_pieces = self._extract_pieces_in_strip(
            file_strip, board_width, board_height, "file", confidence_threshold
        )

        # Look for intersection - pieces that appear in both strips at the same square
        square_piece = self._find_intersection_piece(
            rank_pieces,
            file_pieces,
            rank_idx,
            file_idx,
            board_width,
            board_height,
        )

        if square_piece:
          fen_symbol = piece_mapping.get(square_piece["class"].lower())
          if fen_symbol:
            board[rank_idx][file_idx] = fen_symbol

    return self.board_to_fen_string_from_symbols(board)

  def _extract_pieces_in_strip(
      self, strip, board_width, board_height, strip_type, confidence_threshold
  ):
    """Extract piece positions from a rank or file strip"""
    pieces = []
    predictions = strip.get("predictions", [])

    for pred in predictions:
      if pred.get("confidence", 0) >= confidence_threshold:
        piece_class = pred.get("class", "").lower()
        if piece_class not in ["board", "empty", ""]:
          pieces.append({
              "class": piece_class,
              "confidence": pred.get("confidence", 0),
              "x": pred.get("x", 0),
              "y": pred.get("y", 0),
              "strip_type": strip_type,
              "strip_index": strip["index"],
          })

    return pieces

  def _find_intersection_piece(
      self,
      rank_pieces,
      file_pieces,
      rank_idx,
      file_idx,
      board_width,
      board_height,
  ):
    """Find piece that exists at the intersection of this rank and file"""
    # Calculate the square boundaries
    square_width = board_width / 8
    square_height = board_height / 8

    square_left = file_idx * square_width
    square_right = (file_idx + 1) * square_width
    square_top = rank_idx * square_height
    square_bottom = (rank_idx + 1) * square_height

    # Find pieces from rank strip that fall in this file
    rank_candidates = []
    for piece in rank_pieces:
      # Convert rank strip coordinates to board coordinates
      piece_x_board = piece["x"]  # Already in board coordinates for rank strips
      if square_left <= piece_x_board <= square_right:
        rank_candidates.append(piece)

    # Find pieces from file strip that fall in this rank
    file_candidates = []
    for piece in file_pieces:
      # Convert file strip coordinates to board coordinates
      piece_y_board = piece["y"]  # Already in board coordinates for file strips
      if square_top <= piece_y_board <= square_bottom:
        file_candidates.append(piece)

    # Look for matching pieces (same class, similar position)
    for rank_piece in rank_candidates:
      for file_piece in file_candidates:
        if (
            rank_piece["class"] == file_piece["class"]
            and abs(rank_piece["confidence"] - file_piece["confidence"]) < 0.2
        ):
          return rank_piece  # Return the piece found in both strips

    return None

  async def test_strip_classification(self, model_id="chess.comdetection/4"):
    """Test the rank/file strip approach"""
    print(f"🧪 Testing strip classification with {model_id}")

    # Step 1: Capture from video device
    frame_path, pil_frame = self.capture_and_save_frame()

    # Step 2: Segment board (using existing logic)
    print("🎯 Running board segmentation...")
    segmentation_result = self.pipeline.segment_board_direct(pil_frame)
    bbox = self.pipeline.extract_bbox_from_segmentation(segmentation_result)

    if not bbox:
      print("❌ Board segmentation failed")
      return

    print(f"✅ Board detected with confidence {bbox['confidence']:.3f}")

    # Step 3: Crop board region
    board_crop = pil_frame.crop(bbox["coords"])

    if self.debug_mode:
      crop_path = self.debug_dir / "board_crop_strips.png"
      board_crop.save(crop_path)
      print(f"💾 Saved board crop to {crop_path}")

    print(f"📐 Board crop: {board_crop.size}")

    # Step 4: Create and classify strips
    print("\n" + "=" * 50)
    print("🆕 TESTING STRIP APPROACH")
    print("=" * 50)

    start_time = time.time()

    # Create strips
    strips = self.create_row_column_strips(board_crop)

    # Save sample strips for debugging
    if self.debug_mode:
      for i, strip in enumerate(strips[:4]):  # Save first 4 strips
        strip_path = self.debug_dir / f"strip_{strip['name']}.png"
        strip["image"].save(strip_path)
      print(f"💾 Saved {min(4, len(strips))} sample strips")

    # Batch classify
    classified_strips = self.classify_strips_batch(strips, model_id)

    if not classified_strips:
      print("❌ Strip classification failed")
      return

    # Convert to FEN using intersection logic
    strip_fen = self.strips_to_fen(
        classified_strips, board_crop.size[0], board_crop.size[1]
    )
    strip_time = time.time() - start_time

    print(f"🎯 Strip method FEN: {strip_fen}")
    print(f"⏱️  Strip method time: {strip_time:.2f}s")

    return strip_fen

  async def test_640_resize_detection(
      self, model_id="chess-piece-detection-lnpzs/1"
  ):
    """Test full board detection with 640x640 resize"""
    print(f"🧪 Testing 640x640 resize detection with {model_id}")

    # Step 1: Capture from video device
    frame_path, pil_frame = self.capture_and_save_frame()

    # Step 2: Segment board (using existing logic)
    print("🎯 Running board segmentation...")
    segmentation_result = self.pipeline.segment_board_direct(pil_frame)
    bbox = self.pipeline.extract_bbox_from_segmentation(segmentation_result)

    if not bbox:
      print("❌ Board segmentation failed")
      return

    print(f"✅ Board detected with confidence {bbox['confidence']:.3f}")

    # Step 3: Crop board region
    board_crop = pil_frame.crop(bbox["coords"])
    print(f"📐 Original board crop: {board_crop.size}")

    # Step 4: Resize to 640x640
    board_crop_640 = board_crop.resize((640, 640), Image.LANCZOS)
    print(f"📐 Resized board crop: {board_crop_640.size}")

    if self.debug_mode:
      crop_path = self.debug_dir / "board_crop_640.png"
      board_crop_640.save(crop_path)
      print(f"💾 Saved 640x640 crop to {crop_path}")

    # Step 5: Full board piece detection on 640x640
    print("\n" + "=" * 50)
    print("🆕 TESTING 640x640 RESIZE APPROACH")
    print("=" * 50)

    start_time = time.time()

    # Detect pieces on 640x640 image
    piece_result = self.pipeline.detect_pieces_direct(board_crop_640, model_id)

    if not piece_result:
      print("❌ 640x640 piece detection failed")
      return

    # Convert to FEN using 640x640 dimensions
    fen_640, board_grid = self.pipeline.pieces_to_fen_from_dimensions(
        piece_result, 640, 640, model_id
    )
    resize_time = time.time() - start_time

    print(f"🎯 640x640 method FEN: {fen_640}")
    print(f"⏱️  640x640 method time: {resize_time:.2f}s")

    # Step 6: Show cute board diagram for visual verification
    self._show_board_visualization(fen_640)

    return fen_640

  def _show_board_visualization(self, fen: str):
    """Show visual 8x8 board representation for manual verification"""
    try:
      import chess

      board = chess.Board(f"{fen} w KQkq - 0 1")

      print(f"\n📋 BOARD VISUALIZATION (compare with YouTube!):")
      print("   a b c d e f g h")
      for rank in range(8, 0, -1):  # 8 down to 1
        pieces_row = []
        for file in range(8):  # a to h
          square = chess.square(file, rank - 1)
          piece = board.piece_at(square)
          if piece:
            pieces_row.append(piece.symbol())
          else:
            pieces_row.append(".")
        print(f"{rank}: {' '.join(pieces_row)}")
      print()
    except Exception as e:
      print(f"⚠️ Board visualization failed: {e}")

  async def test_original_crop_size(
      self, model_id="chess-piece-detection-lnpzs/1"
  ):
    """Test hermetic: segmentation → crop → NO RESIZE → detection → baby board"""
    print(f"🧪 Testing original crop size (NO RESIZE) with {model_id}")

    # Step 1: Capture from video device
    frame_path, pil_frame = self.capture_and_save_frame()

    # Step 2: Segment board
    print("🎯 Running board segmentation...")
    segmentation_result = self.pipeline.segment_board_direct(pil_frame)
    bbox = self.pipeline.extract_bbox_from_segmentation(segmentation_result)

    if not bbox:
      print("❌ Board segmentation failed")
      return

    print(f"✅ Board detected with confidence {bbox['confidence']:.3f}")

    # Step 3: Crop board region (NO RESIZE)
    board_crop = pil_frame.crop(bbox["coords"])
    print(f"📐 Board crop: {board_crop.size} (NO RESIZE)")

    if self.debug_mode:
      crop_path = self.debug_dir / "board_crop_no_resize.png"
      board_crop.save(crop_path)
      print(f"💾 Saved no-resize crop to {crop_path}")

    # Step 4: Piece detection at original crop size
    print("\n" + "=" * 50)
    print("🆕 TESTING ORIGINAL CROP SIZE (NO RESIZE)")
    print("=" * 50)

    start_time = time.time()

    # Detect pieces on original crop
    piece_result = self.pipeline.detect_pieces_direct(board_crop, model_id)

    if not piece_result:
      print("❌ Original crop piece detection failed")
      return

    # Convert to FEN using original crop dimensions
    fen_no_resize, board_grid = self.pipeline.pieces_to_fen_from_dimensions(
        piece_result, board_crop.size[0], board_crop.size[1], model_id
    )
    no_resize_time = time.time() - start_time

    print(f"🎯 No resize method FEN: {fen_no_resize}")
    print(f"⏱️  No resize method time: {no_resize_time:.2f}s")

    # Step 5: Show baby board
    self._show_board_visualization(fen_no_resize)

    return fen_no_resize

  async def test_1024_resize_detection(
      self, model_id="chess-piece-detection-lnpzs/1"
  ):
    """Test full board detection with 1024x1024 upscale"""
    print(f"🧪 Testing 1024x1024 upscale detection with {model_id}")

    # Step 1: Capture from video device
    frame_path, pil_frame = self.capture_and_save_frame()

    # Step 2: Segment board (using existing logic)
    print("🎯 Running board segmentation...")
    segmentation_result = self.pipeline.segment_board_direct(pil_frame)
    bbox = self.pipeline.extract_bbox_from_segmentation(segmentation_result)

    if not bbox:
      print("❌ Board segmentation failed")
      return

    print(f"✅ Board detected with confidence {bbox['confidence']:.3f}")

    # Step 3: Crop board region
    board_crop = pil_frame.crop(bbox["coords"])
    print(f"📐 Original board crop: {board_crop.size}")

    # Step 4: Upscale to 1024x1024
    board_crop_1024 = board_crop.resize((1024, 1024), Image.LANCZOS)
    print(f"📐 Upscaled board crop: {board_crop_1024.size}")

    if self.debug_mode:
      crop_path = self.debug_dir / "board_crop_1024.png"
      board_crop_1024.save(crop_path)
      print(f"💾 Saved 1024x1024 crop to {crop_path}")

    # Step 5: Full board piece detection on 1024x1024
    print("\n" + "=" * 50)
    print("🆕 TESTING 1024x1024 UPSCALE APPROACH")
    print("=" * 50)

    start_time = time.time()

    # Detect pieces on 1024x1024 image
    piece_result = self.pipeline.detect_pieces_direct(board_crop_1024, model_id)

    if not piece_result:
      print("❌ 1024x1024 piece detection failed")
      return

    # Convert to FEN using 1024x1024 dimensions
    fen_1024, board_grid = self.pipeline.pieces_to_fen_from_dimensions(
        piece_result, 1024, 1024, model_id
    )
    upscale_time = time.time() - start_time

    print(f"🎯 1024x1024 method FEN: {fen_1024}")
    print(f"⏱️  1024x1024 method time: {upscale_time:.2f}s")

    # Step 6: Show cute board diagram for visual verification
    self._show_board_visualization(fen_1024)

    return fen_1024

  def cleanup(self):
    """Clean up video capture"""
    if self.cap:
      self.cap.release()


async def main():
  parser = argparse.ArgumentParser(
      description="Test square-by-square chess classification"
  )
  parser.add_argument(
      "--model",
      default="chess.comdetection/4",
      help="Roboflow model ID for piece classification",
  )
  parser.add_argument(
      "--no-debug",
      action="store_true",
      help="Disable debug mode (no saved images)",
  )

  args = parser.parse_args()

  tester = SquareClassificationTester(debug_mode=not args.no_debug)

  try:
    tester.setup_video_capture()
    await tester.test_square_classification(model_id=args.model)

    # Test original crop size hermetic (no resize)
    print("\n" + "=" * 60)
    print("🔄 TESTING ORIGINAL CROP SIZE (NO RESIZE)")
    print("=" * 60)
    await tester.test_original_crop_size(
        model_id="chess-piece-detection-lnpzs/1"
    )

    # Also test 640x640 resize approach
    print("\n" + "=" * 60)
    print("🔄 TESTING 640x640 RESIZE APPROACH")
    print("=" * 60)
    await tester.test_640_resize_detection(
        model_id="chess-piece-detection-lnpzs/1"
    )

    # Also test 1024x1024 upscale approach
    print("\n" + "=" * 60)
    print("🔄 TESTING 1024x1024 UPSCALE APPROACH")
    print("=" * 60)
    await tester.test_1024_resize_detection(
        model_id="chess-piece-detection-lnpzs/1"
    )

    # Also test strip approach
    print("\n" + "=" * 60)
    print("🔄 TESTING STRIP APPROACH")
    print("=" * 60)
    await tester.test_strip_classification(model_id=args.model)
  except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback

    traceback.print_exc()
  finally:
    tester.cleanup()


if __name__ == "__main__":
  asyncio.run(main())
