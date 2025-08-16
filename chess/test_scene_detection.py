"""Test scene detection for chess companion background processing

Based on tv_companion_with_transcription.py scene detection architecture.
Tests SceneDetect library with HDMI video stream to understand scene change behavior
during live chess broadcasts.
"""

import asyncio
import cv2
import time
from datetime import datetime
from pathlib import Path

from scenedetect import SceneManager, HistogramDetector
from scenedetect.backends import VideoCaptureAdapter

# HDMI capture device settings (same as companion)
HDMI_VIDEO_DEVICE = "/dev/video11"  # Using loopback device


class ChessSceneDetectionTest:
    def __init__(self, debug_mode=True):
        self.debug_mode = debug_mode
        if self.debug_mode:
            self.debug_dir = Path("debug_scene_detection")
            self.debug_dir.mkdir(exist_ok=True)
            print(f"🐛 Debug mode: saving frames to {self.debug_dir}")
        
        # Scene detection setup with histogram detector
        self.scene_manager = SceneManager()
        self.scene_manager.add_detector(HistogramDetector(
            threshold=0.03,           # More sensitive histogram threshold
            min_scene_len=30          # 30 frames = ~1s at 30fps buffer
        ))
        self.scene_detection_active = False
        self.video_fps = None
        
        # Shared video capture
        self.shared_cap = None
        
        # Scene tracking
        self.scene_count = 0
        self.last_scene_time = None

    def on_new_scene(self, frame_img, frame_num):
        """Callback invoked when PySceneDetect finds a new scene"""
        # Calculate timestamp from frame number and fps
        timestamp_seconds = frame_num / self.video_fps if self.video_fps else 0
        minutes = int(timestamp_seconds // 60)
        seconds = timestamp_seconds % 60
        timestamp_str = f"{minutes:02d}:{seconds:05.2f}"
        
        self.scene_count += 1
        current_time = time.time()
        
        # Calculate time since last scene change
        time_since_last = "N/A"
        if self.last_scene_time:
            time_since_last = f"{current_time - self.last_scene_time:.1f}s"
        self.last_scene_time = current_time
        
        print(f"🎬 SCENE CHANGE #{self.scene_count}")
        print(f"   Frame: {frame_num} ({timestamp_str})")  
        print(f"   Time since last: {time_since_last}")
        print(f"   Real time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Save debug frame if enabled
        if self.debug_mode and frame_img is not None:
            try:
                debug_filename = f"scene_{self.scene_count:03d}_{frame_num:06d}.jpg"
                debug_path = self.debug_dir / debug_filename
                cv2.imwrite(str(debug_path), frame_img)
                print(f"   Saved: {debug_filename}")
            except Exception as e:
                print(f"   ❌ Failed to save debug frame: {e}")
        
        print()  # Empty line for readability

    async def run_scene_detection(self):
        """Run PySceneDetect on HDMI video stream"""
        print("🎬 Starting PySceneDetect scene detection test...")
        print(f"📺 Video device: {HDMI_VIDEO_DEVICE}")
        
        # Initialize shared video capture
        self.shared_cap = cv2.VideoCapture(HDMI_VIDEO_DEVICE)
        if not self.shared_cap.isOpened():
            print(f"❌ Cannot open HDMI video device {HDMI_VIDEO_DEVICE}")
            return
        
        # Set video properties (same as companion)
        self.shared_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.shared_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        # Get and store frame rate for timestamp calculations
        self.video_fps = self.shared_cap.get(cv2.CAP_PROP_FPS)
        print(f"📊 Video FPS: {self.video_fps}")
        
        # Wrap with VideoCaptureAdapter for PySceneDetect
        video_adapter = VideoCaptureAdapter(self.shared_cap)
        
        print(f"✓ HDMI video capture ready for scene detection")
        print(f"🎬 Using HistogramDetector for scene changes (min_scene_len=30)")
        print(f"🚀 Starting detection... Press Ctrl+C to stop")
        print()
        
        # Run scene detection in a separate thread (it's blocking)
        try:
            await asyncio.to_thread(self._run_scene_detection_sync, video_adapter)
        except KeyboardInterrupt:
            print("\n⏹️ Scene detection stopped by user")
        except Exception as e:
            print(f"❌ Scene detection error: {e}")
        finally:
            if self.shared_cap:
                self.shared_cap.release()
                print("✅ Video capture released")

    def _run_scene_detection_sync(self, video_adapter):
        """Run scene detection synchronously in a thread"""
        try:
            self.scene_detection_active = True
            print(f"🎬 Scene detection thread started")
            
            # This will block and call on_new_scene callback for each scene
            self.scene_manager.detect_scenes(
                video=video_adapter, 
                callback=self.on_new_scene
            )
            
        except Exception as e:
            print(f"❌ Scene detection sync error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.scene_detection_active = False
            print(f"🎬 Scene detection thread finished")


async def main():
    """Test scene detection with live HDMI feed"""
    print("🧪 Chess Scene Detection Test")
    print("📺 Make sure HDMI capture is working and chess stream is playing")
    print()
    
    tester = ChessSceneDetectionTest(debug_mode=True)
    await tester.run_scene_detection()
    
    print(f"\n📊 Final Stats:")
    print(f"   Total scenes detected: {tester.scene_count}")
    if tester.debug_mode:
        print(f"   Debug frames saved to: {tester.debug_dir}")


if __name__ == "__main__":
    asyncio.run(main())
