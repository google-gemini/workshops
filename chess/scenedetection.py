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


import asyncio
import cv2
import time
from datetime import datetime
from pathlib import Path

from scenedetect import SceneManager, HistogramDetector
from scenedetect.backends import VideoCaptureAdapter


class ChessSceneDetector:
    """Scene change detection for chess broadcasts using PySceneDetect"""
    
    def __init__(self, debug_dir=None):
        self.debug_mode = debug_dir is not None
        if self.debug_mode:
            self.debug_dir = Path(debug_dir)
            self.debug_dir.mkdir(exist_ok=True)
        else:
            self.debug_dir = None
            
        # Scene tracking
        self.scene_count = 0
        self.last_scene_time = None
        
    async def start_detection(self, video_capture, on_scene_change_callback):
        """Start PySceneDetect scene detection"""
        print("🎬 Starting PySceneDetect scene detection...")
        
        # Capture event loop reference BEFORE entering background thread
        main_loop = asyncio.get_running_loop()
        
        scene_manager = SceneManager()
        scene_manager.add_detector(HistogramDetector(
            threshold=0.03, 
            min_scene_len=30
        ))
        
        def on_scene_change(frame_img, frame_num):
            self.scene_count += 1
            current_time = time.time()
            
            # Calculate timing
            time_since_last = "N/A"
            if self.last_scene_time:
                time_since_last = f"{current_time - self.last_scene_time:.1f}s"
            self.last_scene_time = current_time
            
            print(f"🎬 Scene change #{self.scene_count} (frame {frame_num}, {time_since_last})")
            
            # Save debug frame if enabled
            if self.debug_mode and frame_img is not None:
                self._save_debug_frame(frame_img, self.scene_count, frame_num)
            
            # Schedule callback using captured event loop reference
            try:
                main_loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(on_scene_change_callback(frame_img))
                )
                print("✅ Scene change callback scheduled successfully")
            except Exception as e:
                print(f"❌ Failed to schedule scene change callback: {e}")
        
        # Run PySceneDetect
        video_adapter = VideoCaptureAdapter(video_capture)
        print("🎬 HistogramDetector active (threshold=0.03, min_scene_len=30)")
        
        await asyncio.to_thread(
            scene_manager.detect_scenes, 
            video=video_adapter, 
            callback=on_scene_change
        )
    
    def _save_debug_frame(self, frame_img, scene_num, frame_num):
        """Save debug frame"""
        try:
            timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
            debug_filename = f"scene_{scene_num:03d}_{frame_num:06d}_{timestamp}.jpg"
            debug_path = self.debug_dir / debug_filename
            
            cv2.imwrite(str(debug_path), frame_img)
            print(f"   🐛 Saved: {debug_filename}")
            
        except Exception as e:
            print(f"   ❌ Failed to save debug frame: {e}")


async def test_scene_detection():
    """Test function for scene detection"""
    HDMI_VIDEO_DEVICE = "/dev/video11"
    
    # Initialize video capture
    cap = cv2.VideoCapture(HDMI_VIDEO_DEVICE)
    if not cap.isOpened():
        print(f"❌ Cannot open video device {HDMI_VIDEO_DEVICE}")
        return
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    async def on_scene_change(frame):
        print("   → Scene change callback triggered")
    
    # Test scene detection
    detector = ChessSceneDetector(debug_dir="debug_scene_detection")
    
    try:
        await detector.start_detection(cap, on_scene_change)
    except KeyboardInterrupt:
        print("\n⏹️ Scene detection test stopped")
    finally:
        cap.release()


if __name__ == "__main__":
    asyncio.run(test_scene_detection())
