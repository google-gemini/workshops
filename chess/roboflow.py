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
import time

class ChessVisionPipeline:
    """Chess vision pipeline for board segmentation and piece detection"""
    
    def __init__(self, debug_dir=None):
        api_key = os.getenv("ROBOFLOW_API_KEY")
        if not api_key:
            raise ValueError("ROBOFLOW_API_KEY environment variable required")
        
        self.client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key=api_key
        )
        
        self.debug_dir = None
        if debug_dir:
            self.debug_dir = Path(debug_dir)
            self.debug_dir.mkdir(exist_ok=True)
    
    def segment_board_direct(self, pil_image):
        """Run board segmentation on PIL Image"""
        try:
            result = self.client.infer(pil_image, model_id="chessboard-segmentation/1")
            return result
        except Exception as e:
            print(f"❌ Board segmentation failed: {e}")
            return {}
    
    def extract_bbox_from_segmentation(self, segmentation_result, confidence_threshold=0.7):
        """Extract best bounding box from segmentation result"""
        predictions = segmentation_result.get("predictions", [])
        if not predictions:
            return None
            
        # Find best prediction above threshold
        best_prediction = None
        for prediction in predictions:
            confidence = prediction.get('confidence', 0)
            if confidence >= confidence_threshold:
                best_prediction = prediction
                break
        
        if not best_prediction:
            best_prediction = max(predictions, key=lambda p: p.get('confidence', 0))
        
        # Extract bounding box coordinates
        center_x = best_prediction['x']
        center_y = best_prediction['y'] 
        width = best_prediction['width']
        height = best_prediction['height']
        
        # Convert to corner coordinates
        x_min = center_x - width / 2
        y_min = center_y - height / 2
        x_max = center_x + width / 2
        y_max = center_y + height / 2
        
        return {
            "coords": (int(x_min), int(y_min), int(x_max), int(y_max)),
            "confidence": best_prediction.get('confidence', 0)
        }
    
    def detect_pieces_direct(self, pil_image, model_id="chess.comdetection/4"):
        """Run piece detection on PIL Image"""
        try:
            result = self.client.infer(pil_image, model_id=model_id)
            return result
        except Exception as e:
            print(f"❌ Piece detection failed: {e}")
            return None
    
    def pieces_to_fen_from_dimensions(self, piece_detections, board_width, board_height, model_id):
        """Convert piece detections to FEN notation using provided dimensions"""
        return self._pieces_to_fen_impl(piece_detections, board_width, board_height, model_id)
    
    def _pieces_to_fen_impl(self, piece_detections, board_width, board_height, model_id):
        """Internal implementation for pieces to FEN conversion"""
        # Create 8x8 grid mapping
        square_width = board_width / 8
        square_height = board_height / 8
        
        # Initialize empty 8x8 board
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Normalize piece labels for this model
        predictions = piece_detections.get("predictions", [])
        normalized_predictions = self._normalize_piece_labels(predictions, model_id)
        
        # Only log individual detections if there are issues
        issues_found = 0
        
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
            
            # Check bounds and assign to board
            if 0 <= row < 8 and 0 <= col < 8:
                # Handle conflicts (multiple pieces in same square)
                if board[row][col] is None or confidence > board[row][col]["confidence"]:
                    if board[row][col] is not None:
                        print(f"⚠️ Square conflict: replacing {board[row][col]['normalized_class']} with {normalized_class} at ({row},{col})")
                        issues_found += 1
                    board[row][col] = {
                        "piece": original_class, 
                        "normalized_class": normalized_class,
                        "confidence": confidence
                    }
                # else: keep existing higher-confidence piece (no log spam)
            else:
                print(f"❌ Out of bounds detection: {normalized_class} at grid ({row}, {col})")
                issues_found += 1
        
        if issues_found == 0:
            print(f"✅ Processed {len(normalized_predictions)} detections cleanly")
        else:
            print(f"⚠️ Processed {len(normalized_predictions)} detections with {issues_found} issues")
        
        # Convert to FEN notation
        fen = self.board_to_fen_string(board)
        print(f"🎯 Generated FEN: {fen}")
        
        return fen, board
    
    def _normalize_piece_labels(self, detections, model_id):
        """Convert model-specific labels to standard FEN symbols"""
        # Model configs for piece mapping
        MODEL_CONFIGS = {
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
        
        config = MODEL_CONFIGS.get(model_id, {})
        mapping = config.get("piece_mapping", {})
        ignore_classes = config.get("ignore_classes", [])
        
        # Only log unusual piece counts for debugging
        if len(detections) < 10 or len(detections) > 35:  
            print(f"📊 Unusual piece count: {len(detections)} detections")
            piece_counts = {}
            for detection in detections:
                piece_class = detection.get("class", "unknown")
                piece_counts[piece_class] = piece_counts.get(piece_class, 0) + 1
            for piece, count in sorted(piece_counts.items()):
                if count > 0:
                    print(f"   {piece}: {count}")
        
        normalized_detections = []
        for detection in detections:
            original_class = detection.get("class", "unknown")
            
            # Skip ignored classes entirely
            if original_class in ignore_classes:
                continue
                
            if original_class in mapping:
                detection["normalized_class"] = mapping[original_class]
            else:
                print(f"⚠️ Unknown piece class for {model_id}: {original_class}")
                detection["normalized_class"] = "?"
            normalized_detections.append(detection)
        
        return normalized_detections
    
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


async def roboflow_piece_detection(image_path, debug_dir=None, **kwargs):
    """Roboflow-based chess position detection (replaces Gemini consensus)
    
    Args:
        image_path: Path to chess board image
        debug_dir: Optional debug directory for saving intermediate images
        **kwargs: Ignored (for compatibility with consensus_piece_detection interface)
        
    Returns:
        dict: {"consensus_fen": str, "board_confidence": float, "method": "roboflow"}
    """
    try:
        pipeline = ChessVisionPipeline(debug_dir=debug_dir)
        
        print(f"🎯 Running Roboflow chess position detection...")
        
        # Step 1: Board segmentation
        result = pipeline.segment_board_direct(image_path)
        
        # Step 2: Extract best board prediction
        bbox = pipeline.extract_bbox_from_segmentation(result)
        if not bbox:
            return {"consensus_fen": None, "error": "Board segmentation failed"}
        
        # Step 3: Crop board region
        img = Image.open(image_path) if isinstance(image_path, str) else image_path
        board_crop = img.crop(bbox['coords'])
        board_crop_640 = board_crop.resize((640, 640), Image.LANCZOS)
        
        # Step 4: Piece detection  
        piece_result = pipeline.detect_pieces_direct(board_crop_640, model_id="chess.comdetection/4")
        
        if not piece_result:
            return {"consensus_fen": None, "error": "Piece detection failed"}
        
        # Step 5: Convert to FEN
        fen, board_grid = pipeline.pieces_to_fen_from_dimensions(
            piece_result, 
            640, 640,
            "chess.comdetection/4"
        )
        
        print(f"✅ Roboflow detection complete: {fen}")
        
        return {
            "consensus_fen": fen,
            "board_confidence": bbox['confidence'],
            "piece_count": len(piece_result.get("predictions", [])),
            "method": "roboflow"
        }
        
    except Exception as e:
        print(f"❌ Roboflow detection failed: {e}")
        return {"consensus_fen": None, "error": str(e)}
