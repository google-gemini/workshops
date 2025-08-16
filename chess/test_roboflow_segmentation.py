#!/usr/bin/env python3

import os
import cv2
import numpy as np
from PIL import Image
from inference_sdk import InferenceHTTPClient
from pathlib import Path
import asyncio
from datetime import datetime
import json
import requests
from huggingface_hub import InferenceClient
import argparse
import time

# Model metadata - maps model IDs to their labeling schemes
MODEL_CONFIGS = {
    "chess-pieces-22cbf/3": {
        "label_format": "underscore",
        "piece_mapping": {
            "w_king": "K", "w_queen": "Q", "w_rook": "R", 
            "w_bishop": "B", "w_knight": "N", "w_pawn": "P",
            "b_king": "k", "b_queen": "q", "b_rook": "r",
            "b_bishop": "b", "b_knight": "n", "b_pawn": "p"
        }
    },
    "chess-pieces-kaid5/3": {
        "label_format": "abbreviated", 
        "piece_mapping": {
            "WK": "K", "WQ": "Q", "WR": "R", "WB": "B", "WKN": "N", "WP": "P",
            "BK": "k", "BQ": "q", "BR": "r", "BB": "b", "BKN": "n", "BP": "p"
        }
    },
    "chesspiece-detection-twhpv/5": {
        "label_format": "hyphenated",
        "piece_mapping": {
            "white-king": "K", "white-queen": "Q", "white-rook": "R", 
            "white-bishop": "B", "white-knight": "N", "white-pawn": "P",
            "black-king": "k", "black-queen": "q", "black-rook": "r",
            "black-bishop": "b", "black-knight": "n", "black-pawn": "p"
        }
    },
    "2dcpd/2": {
        "label_format": "hyphenated",
        "piece_mapping": {
            "white-king": "K", "white-queen": "Q", "white-rook": "R", 
            "white-bishop": "B", "white-knight": "N", "white-pawn": "P",
            "black-king": "k", "black-queen": "q", "black-rook": "r",
            "black-bishop": "b", "black-knight": "n", "black-pawn": "p"
        }
    },
    "chess.comdetection/4": {
        "label_format": "hyphenated",
        "piece_mapping": {
            "white-king": "K", "white-queen": "Q", "white-rock": "R", 
            "white-bishop": "B", "white-knight": "N", "white-pawn": "P",
            "black-king": "k", "black-queen": "q", "black-rock": "r",
            "black-bishop": "b", "black-knight": "n", "black-pawn": "p"
        },
        "ignore_classes": ["board"]
    }
}

def normalize_piece_labels(detections, model_id):
    """Convert model-specific labels to standard FEN symbols"""
    config = MODEL_CONFIGS.get(model_id, {})
    mapping = config.get("piece_mapping", {})
    ignore_classes = config.get("ignore_classes", [])
    
    normalized_detections = []
    for detection in detections:
        original_class = detection.get("class", "unknown")
        
        # Skip ignored classes entirely
        if original_class in ignore_classes:
            print(f"🚫 Ignoring {original_class} detection")
            continue
            
        if original_class in mapping:
            detection["normalized_class"] = mapping[original_class]
        else:
            print(f"⚠️ Unknown piece class for {model_id}: {original_class}")
            detection["normalized_class"] = "?"
        normalized_detections.append(detection)
    
    return normalized_detections

def preprocess_for_roboflow(image_path, target_size=640):
    """Resize and pad image to target size for optimal model performance"""
    img = Image.open(image_path)
    original_size = img.size
    print(f"🔄 Preprocessing: {original_size[0]}×{original_size[1]} → {target_size}×{target_size}")
    
    # Resize maintaining aspect ratio with padding
    img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
    
    # Create square canvas with padding
    canvas = Image.new('RGB', (target_size, target_size), (0, 0, 0))
    
    # Center the image
    x = (target_size - img.width) // 2
    y = (target_size - img.height) // 2
    canvas.paste(img, (x, y))
    
    # Save preprocessed image
    preprocessed_path = f"temp_preprocessed_{target_size}x{target_size}.png"
    canvas.save(preprocessed_path)
    print(f"💾 Saved preprocessed image: {preprocessed_path}")
    
    return preprocessed_path, (x, y), (img.width, img.height), original_size

class RoboflowSegmentationTester:
    def __init__(self):
        api_key = os.getenv("ROBOFLOW_API_KEY")
        if not api_key:
            raise ValueError("ROBOFLOW_API_KEY environment variable required")
        
        self.client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key=api_key
        )
        
        # Create debug directory
        self.debug_dir = Path("debug_roboflow")
        self.debug_dir.mkdir(exist_ok=True)
        
    def capture_from_video_device(self, device="/dev/video11"):
        """Capture frame from video device (HDMI loopback)"""
        cap = cv2.VideoCapture(device)
        if not cap.isOpened():
            raise Exception(f"Cannot open video device {device}")
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise Exception("Failed to capture frame")
            
        return frame
    
    def save_frame_as_image(self, frame, filename="captured_frame.png", target_size=1024):
        """Convert CV2 frame to PIL Image, resize to target size, and save"""
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize to target size for balance of speed and accuracy
        frame_resized = cv2.resize(frame_rgb, (target_size, target_size))
        img = Image.fromarray(frame_resized)
        
        # Save resized frame
        full_path = self.debug_dir / filename
        img.save(full_path)
        print(f"💾 Saved frame (resized to {target_size}x{target_size}): {full_path}")
        
        return str(full_path), img
    
    def run_segmentation(self, image_path_or_array):
        """Run Roboflow chessboard segmentation"""
        print(f"🎯 Running segmentation on: {image_path_or_array}")
        
        result = self.client.infer(
            image_path_or_array, 
            model_id="chessboard-segmentation/1"
        )
        
        print(f"📊 Segmentation result keys: {result.keys()}")
        
        # Dump full JSON response for debugging
        print(f"\n🔍 FULL API RESPONSE:")
        print("=" * 80)
        print(json.dumps(result, indent=2, default=str))
        print("=" * 80)
        
        return result
    
    def extract_best_prediction(self, image_path, segmentation_result, confidence_threshold=0.7, padding=0.02):
        """Extract and crop only the best prediction above confidence threshold"""
        
        predictions = segmentation_result.get("predictions", [])
        if not predictions:
            print("❌ No predictions found in result")
            return None
            
        # Find first prediction above threshold
        best_prediction = None
        for i, prediction in enumerate(predictions):
            confidence = prediction.get('confidence', 0)
            print(f"🔍 Checking prediction #{i+1}: confidence={confidence:.4f}")
            
            if confidence >= confidence_threshold:
                best_prediction = prediction
                print(f"✅ Using prediction #{i+1} (confidence: {confidence:.4f})")
                break
        
        if not best_prediction:
            print(f"❌ No predictions above confidence threshold {confidence_threshold}")
            # Fall back to highest confidence prediction
            best_prediction = max(predictions, key=lambda p: p.get('confidence', 0))
            print(f"🔄 Falling back to highest confidence: {best_prediction.get('confidence', 0):.4f}")
        
        # Load image once
        img = Image.open(image_path)
        img_width, img_height = img.size
        print(f"🖼️ Processing image: {img_width}x{img_height}")
        
        # Extract bounding box coordinates
        prediction = best_prediction
        if 'x' not in prediction or 'y' not in prediction:
            print("❌ Invalid bounding box format")
            return None
            
        center_x = prediction['x']
        center_y = prediction['y'] 
        width = prediction['width']
        height = prediction['height']
        
        # Convert to corner coordinates
        x_min = center_x - width / 2
        y_min = center_y - height / 2
        x_max = center_x + width / 2
        y_max = center_y + height / 2
        
        print(f"📐 Bounding box: ({x_min:.1f}, {y_min:.1f}) to ({x_max:.1f}, {y_max:.1f})")
        
        # Convert to absolute coordinates and add padding
        abs_x_min = int(x_min)
        abs_y_min = int(y_min) 
        abs_x_max = int(x_max)
        abs_y_max = int(y_max)
        
        # Add padding
        pad_x = int(padding * (abs_x_max - abs_x_min))
        pad_y = int(padding * (abs_y_max - abs_y_min))
        
        crop_x_min = max(0, abs_x_min - pad_x)
        crop_y_min = max(0, abs_y_min - pad_y)
        crop_x_max = min(img_width, abs_x_max + pad_x)  
        crop_y_max = min(img_height, abs_y_max + pad_y)
        
        # Crop the image
        cropped = img.crop((crop_x_min, crop_y_min, crop_x_max, crop_y_max))
        
        # Resize cropped board to 640x640 for optimal piece detection
        cropped_640 = cropped.resize((640, 640), Image.Resampling.LANCZOS)
        
        # Save with descriptive filename
        timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
        confidence_str = f"{prediction.get('confidence', 0):.4f}".replace('.', '_')
        cropped_path = self.debug_dir / f"best_board_640x640_{timestamp}_conf_{confidence_str}.png"
        cropped_640.save(cropped_path)
        print(f"✂️ Saved best board crop (640x640): {cropped_path}")
        
        return {
            'path': str(cropped_path),
            'image': cropped_640,
            'confidence': prediction.get('confidence', 0),
            'bbox': (crop_x_min, crop_y_min, crop_x_max, crop_y_max),
            'original_prediction': prediction
        }
    
    def test_yolo_detection(self, image_path):
        """Test YOLO piece detection via HuggingFace Inference API"""
        print(f"\n🎯 Testing YOLO piece detection on: {image_path}")
        
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            print("❌ HF_TOKEN environment variable required")
            return None
        
        try:
            # HuggingFace InferenceClient with explicit provider
            client = InferenceClient(
                provider="hf-inference",
                api_key=hf_token
            )
            
            print("📡 Sending request to HuggingFace API...")
            
            # Simple object detection call
            detections = client.object_detection(
                image_path, 
                model="yamero999/chess-piece-detection-yolo11n"
            )
            
            print(f"✅ YOLO API Response received! Found {len(detections)} detections")
            
            # Print results
            print(f"\n🔍 YOLO DETECTION RESULTS:")
            print("=" * 80)
            for i, detection in enumerate(detections):
                print(f"Detection {i+1}:")
                print(f"  Label: {detection.label}")
                print(f"  Score: {detection.score:.4f}")
                print(f"  Box: ({detection.box.xmin:.1f}, {detection.box.ymin:.1f}) to ({detection.box.xmax:.1f}, {detection.box.ymax:.1f})")
            print("=" * 80)
            
            # Count pieces
            piece_counts = {}
            for detection in detections:
                piece_counts[detection.label] = piece_counts.get(detection.label, 0) + 1
            
            print(f"\n📊 PIECE DETECTION SUMMARY:")
            print(f"   Total detections: {len(detections)}")
            for piece, count in sorted(piece_counts.items()):
                print(f"   {piece}: {count}")
            
            return detections
            
        except Exception as e:
            print(f"❌ YOLO detection failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def compare_fen_accuracy(self, detected_fen, canonical_fen):
        """Compare detected FEN against canonical FEN square by square"""
        print(f"\n📊 Comparing FEN accuracy...")
        print(f"   Detected:  {detected_fen}")
        print(f"   Canonical: {canonical_fen}")
        
        # Parse both FENs into 8x8 grids
        def fen_to_grid(fen_board):
            grid = []
            for row_fen in fen_board.split('/'):
                row = []
                for char in row_fen:
                    if char.isdigit():
                        # Empty squares
                        row.extend(['.'] * int(char))
                    else:
                        # Piece
                        row.append(char)
                grid.append(row)
            return grid
        
        detected_grid = fen_to_grid(detected_fen)
        canonical_grid = fen_to_grid(canonical_fen)
        
        # Compare square by square
        total_squares = 64
        correct_squares = 0
        errors = []
        
        for row in range(8):
            for col in range(8):
                detected_piece = detected_grid[row][col]
                canonical_piece = canonical_grid[row][col]
                
                if detected_piece == canonical_piece:
                    correct_squares += 1
                else:
                    square_name = chr(ord('a') + col) + str(8 - row)
                    errors.append({
                        'square': square_name,
                        'detected': detected_piece,
                        'canonical': canonical_piece
                    })
        
        accuracy = (correct_squares / total_squares) * 100
        
        print(f"\n📈 ACCURACY RESULTS:")
        print(f"   Correct squares: {correct_squares}/{total_squares}")
        print(f"   Accuracy: {accuracy:.1f}%")
        
        if errors:
            print(f"\n❌ ERRORS ({len(errors)} squares):")
            for error in errors[:10]:  # Show first 10 errors
                print(f"   {error['square']}: detected '{error['detected']}' vs canonical '{error['canonical']}'")
            if len(errors) > 10:
                print(f"   ... and {len(errors) - 10} more errors")
        
        return accuracy, correct_squares, total_squares, errors
    
    def pieces_to_fen(self, piece_detections, board_image_path, model_id):
        """Convert piece detections to FEN notation"""
        print(f"\n🎯 Converting piece detections to FEN...")
        
        # Get board dimensions
        img = Image.open(board_image_path)
        board_width, board_height = img.size
        print(f"📏 Board dimensions: {board_width}x{board_height}")
        
        # Create 8x8 grid mapping
        square_width = board_width / 8
        square_height = board_height / 8
        print(f"📐 Square size: {square_width:.1f}x{square_height:.1f}")
        
        # Initialize empty 8x8 board
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Normalize piece labels for this model
        predictions = piece_detections.get("predictions", [])
        normalized_predictions = normalize_piece_labels(predictions, model_id)
        print(f"📋 Processing {len(normalized_predictions)} detections...")
        
        for i, detection in enumerate(normalized_predictions):
            # Get piece center coordinates
            center_x = detection["x"] 
            center_y = detection["y"]
            original_class = detection["class"]
            normalized_class = detection["normalized_class"]
            confidence = detection["confidence"]
            
            # Convert to grid coordinates (0-7, 0-7)
            col = int(center_x / square_width)
            row = int(center_y / square_height)
            
            print(f"  Detection {i+1}: {original_class} → {normalized_class} at ({center_x:.1f}, {center_y:.1f}) → grid ({row}, {col}) conf={confidence:.3f}")
            
            # Check bounds and assign to board
            if 0 <= row < 8 and 0 <= col < 8:
                # Handle conflicts (multiple pieces in same square)
                if board[row][col] is None or confidence > board[row][col]["confidence"]:
                    if board[row][col] is not None:
                        print(f"    ⚠️ Replacing {board[row][col]['normalized_class']} (conf={board[row][col]['confidence']:.3f}) with {normalized_class} (conf={confidence:.3f})")
                    board[row][col] = {
                        "piece": original_class, 
                        "normalized_class": normalized_class,
                        "confidence": confidence
                    }
                else:
                    print(f"    ⚠️ Keeping existing {board[row][col]['normalized_class']} (conf={board[row][col]['confidence']:.3f}) over {normalized_class} (conf={confidence:.3f})")
            else:
                print(f"    ❌ Out of bounds: grid ({row}, {col})")
        
        # Convert to FEN notation
        fen = self.board_to_fen_string(board)
        print(f"\n🎯 Generated FEN: {fen}")
        
        return fen, board
    
    def board_to_fen_string(self, board):
        """Convert 8x8 board array to FEN notation"""
        fen_rows = []
        
        # Convert each row (FEN starts from rank 8, row 0 in our array)
        for row in range(8):
            fen_row = ""
            empty_count = 0
            
            for col in range(8):
                square = board[row][col]
                
                if square is None:
                    # Empty square
                    empty_count += 1
                else:
                    # Add any accumulated empty squares
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    
                    # Add piece symbol using normalized class
                    normalized_class = square.get("normalized_class", "?")
                    fen_row += normalized_class
            
            # Add any remaining empty squares
            if empty_count > 0:
                fen_row += str(empty_count)
            
            fen_rows.append(fen_row)
        
        # Join rows with '/' 
        board_fen = "/".join(fen_rows)
        
        # Return only board position (we can't determine game state from image)
        return board_fen
    
    def test_roboflow_piece_detection(self, image_path, model_id="chess-pieces-22cbf/3"):
        """Test Roboflow piece detection (no preprocessing needed since image is already 640x640)"""
        print(f"\n🎯 Testing Roboflow piece detection on: {image_path}")
        print(f"🎯 Using model: {model_id}")
        
        try:
            print("📡 Sending request to Roboflow API (image already optimized)...")
            
            result = self.client.infer(image_path, model_id=model_id)
            
            print(f"✅ Roboflow piece detection completed!")
            print(f"📊 Result keys: {result.keys()}")
            
            # No coordinate scaling needed since we're working in native 640x640 space
            predictions = result.get("predictions", [])
            
            # Dump full JSON response for debugging
            print(f"\n🔍 PIECE DETECTION RESULTS:")
            print("=" * 80)
            print(json.dumps(result, indent=2, default=str))
            print("=" * 80)
            
            # Count detections by piece type
            piece_counts = {}
            for prediction in predictions:
                piece_class = prediction.get("class", "unknown")
                piece_counts[piece_class] = piece_counts.get(piece_class, 0) + 1
            
            print(f"\n📊 PIECE DETECTION SUMMARY:")
            print(f"   Total detections: {len(predictions)}")
            for piece, count in sorted(piece_counts.items()):
                print(f"   {piece}: {count}")
            
            return result
            
        except Exception as e:
            print(f"❌ Roboflow piece detection failed: {e}")
            import traceback
            traceback.print_exc()
            return None

def parse_args():
    parser = argparse.ArgumentParser(description="Chess board detection and piece recognition")
    parser.add_argument("--use-cached-board", 
                       help="Skip board detection, use this cropped board image path")
    parser.add_argument("--piece-model", 
                       default="chess-pieces-22cbf/3",
                       help="Roboflow piece detection model ID")
    parser.add_argument("--canonical-fen",
                       help="Compare detected FEN against this canonical position (board part only)")
    return parser.parse_args()

async def main():
    try:
        pipeline_start = time.time()
        
        args = parse_args()
        tester = RoboflowSegmentationTester()
        
        # Determine board image to use
        if args.use_cached_board:
            print(f"📋 Using cached board image: {args.use_cached_board}")
            if not os.path.exists(args.use_cached_board):
                print(f"❌ Cached board image not found: {args.use_cached_board}")
                return
            board_image_path = args.use_cached_board
            board_stage_time = 0  # No board detection time for cached images
        else:
            board_start = time.time()
            print("📹 Running full pipeline: capture → segment → crop...")
            
            # Step 1: Capture frame from video device
            capture_start = time.time()
            print("📹 Capturing frame from /dev/video11...")
            frame = tester.capture_from_video_device("/dev/video11")
            capture_time = (time.time() - capture_start) * 1000
            print(f"⏱️ Video capture: {capture_time:.1f}ms")
            
            # Step 2: Save frame
            timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
            image_path, pil_image = tester.save_frame_as_image(
                frame, f"hdmi_capture_{timestamp}.png"
            )
            
            # Step 3: Run segmentation
            segment_start = time.time()
            print("🎯 Running Roboflow segmentation...")
            result = tester.run_segmentation(image_path)
            segment_time = (time.time() - segment_start) * 1000
            print(f"⏱️ Board segmentation: {segment_time:.1f}ms")
            
            # Step 4: Extract and crop best prediction
            crop_start = time.time()
            print("✂️ Extracting best prediction...")
            best_crop = tester.extract_best_prediction(image_path, result)
            crop_time = (time.time() - crop_start) * 1000
            print(f"⏱️ Board cropping: {crop_time:.1f}ms")
            
            if not best_crop:
                print("❌ Failed to extract best prediction")
                return
                
            board_image_path = best_crop['path']
            print(f"\n🏆 Using board: {board_image_path} (confidence: {best_crop['confidence']:.4f})")
            
            board_stage_time = (time.time() - board_start) * 1000
            print(f"⏱️ Total board detection stage: {board_stage_time:.1f}ms")
        
        # Step 5: Test piece detection on board image
        piece_start = time.time()
        print(f"\n🎯 Testing piece detection with model: {args.piece_model}")
        piece_result = tester.test_roboflow_piece_detection(board_image_path, args.piece_model)
        piece_time = (time.time() - piece_start) * 1000
        print(f"⏱️ Piece detection stage: {piece_time:.1f}ms")
        
        if piece_result:
            print(f"✅ Piece detection completed successfully!")
            
            # Step 6: Convert to FEN
            fen_start = time.time()
            fen, board_grid = tester.pieces_to_fen(piece_result, board_image_path, args.piece_model)
            fen_time = (time.time() - fen_start) * 1000
            print(f"⏱️ FEN generation: {fen_time:.1f}ms")
            
            print(f"\n📋 8x8 BOARD VISUALIZATION:")
            print("   a b c d e f g h")
            for row in range(8):
                pieces_row = []
                for col in range(8):
                    square = board_grid[row][col]
                    if square:
                        normalized_class = square.get("normalized_class", "?")
                        pieces_row.append(normalized_class)
                    else:
                        pieces_row.append(".")
                print(f"{8-row}: {' '.join(pieces_row)}")
                
            print(f"\n🏁 FINAL FEN: {fen}")
            
            # Step 7: Compare against canonical FEN if provided
            if args.canonical_fen:
                accuracy, correct, total, errors = tester.compare_fen_accuracy(fen, args.canonical_fen)
            
            # Calculate and display total pipeline latency
            total_time = (time.time() - pipeline_start) * 1000
            print(f"\n⏱️ ====================== TIMING SUMMARY ======================")
            if not args.use_cached_board:
                print(f"⏱️ Board detection stage: {board_stage_time:.1f}ms")
            print(f"⏱️ Piece detection stage: {piece_time:.1f}ms")
            print(f"⏱️ FEN generation stage:  {fen_time:.1f}ms")
            print(f"⏱️ TOTAL PIPELINE LATENCY: {total_time:.1f}ms")
            
            if not args.use_cached_board:
                improvement = 40000 / total_time  # 40 seconds in ms / current time
                print(f"⏱️ Speedup vs 40s baseline: {improvement:.0f}x faster! 🚀")
            print(f"⏱️ ============================================================")
            
        else:
            print("❌ Piece detection failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
