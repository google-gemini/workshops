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


class ChessVisionPipeline:
    """Chess position detection pipeline using Roboflow models"""
    
    def __init__(self, debug_dir=None):
        api_key = os.getenv("ROBOFLOW_API_KEY")
        if not api_key:
            raise ValueError("ROBOFLOW_API_KEY environment variable required")
        
        self.client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key=api_key
        )
        
        # Setup debug directory
        if debug_dir:
            self.debug_dir = Path(debug_dir)
            self.debug_dir.mkdir(exist_ok=True)
        else:
            self.debug_dir = None
    
    def segment_board(self, image_path):
        """Run chessboard segmentation to find board location"""
        print(f"🎯 Running board segmentation on: {image_path}")
        
        result = self.client.infer(
            image_path, 
            model_id="chessboard-segmentation/1"
        )
        
        print(f"📊 Segmentation result: {len(result.get('predictions', []))} predictions")
        return result
    
    def segment_board_direct(self, pil_image):
        """Run chessboard segmentation directly on PIL Image"""
        print(f"🎯 Running board segmentation on PIL Image: {pil_image.size}")
        
        result = self.client.infer(
            pil_image, 
            model_id="chessboard-segmentation/1"
        )
        
        print(f"📊 Segmentation result: {len(result.get('predictions', []))} predictions")
        return result
    
    def extract_best_board_crop(self, image_path, segmentation_result, confidence_threshold=0.7, padding=0.02):
        """Extract and crop the best board prediction above confidence threshold"""
        
        predictions = segmentation_result.get("predictions", [])
        if not predictions:
            print("❌ No board predictions found")
            return None
            
        # Find first prediction above threshold
        best_prediction = None
        for i, prediction in enumerate(predictions):
            confidence = prediction.get('confidence', 0)
            print(f"🔍 Checking board prediction #{i+1}: confidence={confidence:.4f}")
            
            if confidence >= confidence_threshold:
                best_prediction = prediction
                print(f"✅ Using board prediction #{i+1} (confidence: {confidence:.4f})")
                break
        
        if not best_prediction:
            print(f"❌ No board predictions above confidence threshold {confidence_threshold}")
            # Fall back to highest confidence prediction
            best_prediction = max(predictions, key=lambda p: p.get('confidence', 0))
            print(f"🔄 Falling back to highest confidence: {best_prediction.get('confidence', 0):.4f}")
        
        # Load and crop image
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
        
        print(f"📐 Board bounding box: ({x_min:.1f}, {y_min:.1f}) to ({x_max:.1f}, {y_max:.1f})")
        
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
        
        # Save cropped board
        if self.debug_dir:
            timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
            confidence_str = f"{prediction.get('confidence', 0):.4f}".replace('.', '_')
            cropped_path = self.debug_dir / f"board_crop_640x640_{timestamp}_conf_{confidence_str}.png"
        else:
            cropped_path = f"temp_board_crop_{datetime.now().strftime('%H%M%S_%f')[:-3]}.png"
        
        cropped_640.save(cropped_path)
        print(f"✂️ Saved board crop (640x640): {cropped_path}")
        
        return {
            'path': str(cropped_path),
            'image': cropped_640,
            'confidence': prediction.get('confidence', 0),
            'bbox': (crop_x_min, crop_y_min, crop_x_max, crop_y_max),
            'original_prediction': prediction
        }
    
    def detect_pieces(self, board_image_path, model_id="chess.comdetection/4"):
        """Detect chess pieces on a cropped board image"""
        print(f"🎯 Detecting pieces on: {board_image_path}")
        print(f"🎯 Using model: {model_id}")
        
        try:
            result = self.client.infer(board_image_path, model_id=model_id)
            
            predictions = result.get("predictions", [])
            print(f"✅ Piece detection completed! Found {len(predictions)} detections")
            
            # Count detections by piece type
            piece_counts = {}
            for prediction in predictions:
                piece_class = prediction.get("class", "unknown")
                piece_counts[piece_class] = piece_counts.get(piece_class, 0) + 1
            
            print(f"📊 Piece detection summary:")
            print(f"   Total detections: {len(predictions)}")
            for piece, count in sorted(piece_counts.items()):
                print(f"   {piece}: {count}")
            
            return result
            
        except Exception as e:
            print(f"❌ Piece detection failed: {e}")
            return None

    def detect_pieces_direct(self, pil_image, model_id="chess.comdetection/4"):
        """Detect chess pieces directly on PIL Image (no file I/O)"""
        print(f"🎯 Detecting pieces on PIL Image: {pil_image.size}")
        print(f"🎯 Using model: {model_id}")
        
        try:
            result = self.client.infer(pil_image, model_id=model_id)
            
            predictions = result.get("predictions", [])
            print(f"✅ Piece detection completed! Found {len(predictions)} detections")
            
            # Count detections by piece type
            piece_counts = {}
            for prediction in predictions:
                piece_class = prediction.get("class", "unknown")
                piece_counts[piece_class] = piece_counts.get(piece_class, 0) + 1
            
            print(f"📊 Piece detection summary:")
            print(f"   Total detections: {len(predictions)}")
            for piece, count in sorted(piece_counts.items()):
                print(f"   {piece}: {count}")
            
            return result
            
        except Exception as e:
            print(f"❌ Piece detection failed: {e}")
            return None
    
    def pieces_to_fen(self, piece_detections, board_image_path, model_id):
        """Convert piece detections to FEN notation"""
        print(f"🎯 Converting piece detections to FEN...")
        
        # Get board dimensions
        img = Image.open(board_image_path)
        board_width, board_height = img.size
        print(f"📏 Board dimensions: {board_width}x{board_height}")
        
        return self._pieces_to_fen_impl(piece_detections, board_width, board_height, model_id)
    
    def pieces_to_fen_from_dimensions(self, piece_detections, board_width, board_height, model_id):
        """Convert piece detections to FEN notation using provided dimensions (no file I/O)"""
        print(f"🎯 Converting piece detections to FEN...")
        print(f"📏 Board dimensions: {board_width}x{board_height}")
        
        return self._pieces_to_fen_impl(piece_detections, board_width, board_height, model_id)
    
    def _pieces_to_fen_impl(self, piece_detections, board_width, board_height, model_id):
        """Internal implementation for pieces to FEN conversion"""
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
        print(f"🎯 Generated FEN: {fen}")
        
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

    def extract_bbox_from_segmentation(self, segmentation_result, confidence_threshold=0.7):
        """Extract best bounding box from segmentation results"""
        predictions = segmentation_result.get("predictions", [])
        if not predictions:
            print("❌ No segmentation predictions found")
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
            print(f"❌ No predictions above threshold {confidence_threshold}")
            # Fall back to highest confidence prediction
            best_prediction = max(predictions, key=lambda p: p.get('confidence', 0))
            print(f"🔄 Using highest confidence: {best_prediction.get('confidence', 0):.4f}")
        
        # Extract bounding box coordinates
        if 'x' not in best_prediction or 'y' not in best_prediction:
            print("❌ Invalid bounding box format")
            return None
            
        center_x = best_prediction['x']
        center_y = best_prediction['y'] 
        width = best_prediction['width']
        height = best_prediction['height']
        
        # Convert to corner coordinates
        x_min = int(center_x - width / 2)
        y_min = int(center_y - height / 2)
        x_max = int(center_x + width / 2)
        y_max = int(center_y + height / 2)
        
        print(f"📐 Bounding box: ({x_min}, {y_min}) to ({x_max}, {y_max})")
        
        return {
            "coords": (x_min, y_min, x_max, y_max),
            "confidence": best_prediction.get('confidence', 0)
        }


async def roboflow_piece_detection(image_path, debug_dir=None, **kwargs):
    """Roboflow-based chess position detection
    
    Args:
        image_path: Path to chess board image
        debug_dir: Optional debug directory for saving intermediate images
        **kwargs: Ignored (for compatibility with consensus_piece_detection interface)
        
    Returns:
        dict: {"consensus_fen": str, "board_confidence": float, "piece_count": int, "method": "roboflow"}
    """
    try:
        pipeline = ChessVisionPipeline(debug_dir=debug_dir)
        
        print(f"🎯 Running Roboflow chess position detection...")
        
        # Step 1: Board segmentation
        result = pipeline.segment_board(image_path)
        
        # Step 2: Extract best board prediction
        best_crop = pipeline.extract_best_board_crop(image_path, result)
        if not best_crop:
            return {"consensus_fen": None, "error": "Board segmentation failed"}
        
        # Step 3: Piece detection  
        piece_result = pipeline.detect_pieces(
            best_crop['path'], 
            model_id="chess.comdetection/4"
        )
        
        if not piece_result:
            return {"consensus_fen": None, "error": "Piece detection failed"}
        
        # Step 4: Convert to FEN
        fen, board_grid = pipeline.pieces_to_fen(
            piece_result, 
            best_crop['path'], 
            "chess.comdetection/4"
        )
        
        print(f"✅ Roboflow detection complete: {fen}")
        
        return {
            "consensus_fen": fen,
            "board_confidence": best_crop['confidence'],
            "piece_count": len(piece_result.get("predictions", [])),
            "method": "roboflow"
        }
        
    except Exception as e:
        print(f"❌ Roboflow detection failed: {e}")
        return {"consensus_fen": None, "error": str(e)}
