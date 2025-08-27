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

"""TV Control for Chess Companion - YouTube and Google TV integration

Standalone testable TV controller for chess content.
Can be run independently: python chess/tv_controller.py search "Magnus Carlsen"
"""

import argparse
import asyncio
import subprocess
import os
from typing import Optional
from datetime import datetime
import pychromecast


class ChessTVController:
    """Handles TV control for chess content - YouTube focus"""
    
    def __init__(self, memory_client=None):
        self.memory_client = memory_client
        print(f"🎬 Chess TV Controller initialized")
        
        # Try fallback IP first (fast)
        self.tv_ip = "192.168.50.220"
        print(f"📺 Trying fallback IP: {self.tv_ip}")
        
        if not self.ensure_tv_connection():
            print("❌ Fallback IP failed, running auto-discovery...")
            discovered_ip = self.discover_tv_ip()
            if discovered_ip:
                self.tv_ip = discovered_ip
            else:
                print("⚠️ Auto-discovery also failed. Keeping fallback IP as last resort.")
    
    def discover_tv_ip(self):
        """Auto-discover Google TV IP using pychromecast"""
        try:
            print("🔍 Auto-discovering Google TV IP address...")
            chromecasts, browser = pychromecast.get_listed_chromecasts(discovery_timeout=10)

            if chromecasts:
                cast = chromecasts[0]
                cast.wait()
                ip_address = cast.cast_info.host
                print(f"📺 Found Google TV '{cast.cast_info.friendly_name}' at: {ip_address}")
                
                # Clean up discovery
                pychromecast.discovery.stop_discovery(browser)
                return ip_address
            else:
                print("❌ No Chromecast/Google TV devices found on network")
                return None

        except Exception as e:
            print(f"❌ TV discovery failed: {e}")
            return None

    def ensure_tv_connection(self):
        """Ensure ADB connection to Google TV"""
        try:
            print(f"🔗 Connecting ADB to {self.tv_ip}...")
            result = subprocess.run(
                ["adb", "connect", f"{self.tv_ip}:5555"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if "connected" in result.stdout.lower() or "already connected" in result.stdout.lower():
                print(f"✅ ADB connected to {self.tv_ip}")
                return True
            else:
                print(f"⚠️ ADB connection result: {result.stdout.strip()}")
                return False

        except Exception as e:
            print(f"❌ ADB connection failed: {e}")
            return False
    
    def search_and_play_content(self, title: str):
        """Search and play chess content - fire and forget"""
        print(f"🎬 Starting search for: '{title}' (async)")
        asyncio.create_task(self._search_and_play_async(title))
        return f"🎬 Starting search for '{title}' - this will take a few seconds"
    
    async def _search_and_play_async(self, title: str):
        """Actually perform the ADB search commands"""
        try:
            print(f"🎬 [Background] Searching for: '{title}'")

            # Ensure connection first
            if not await asyncio.to_thread(self.ensure_tv_connection):
                print("❌ [Background] Could not connect to Google TV")
                return

            # Format for ADB (replace spaces with %s)
            title_formatted = title.replace(" ", "%s")

            # Universal search sequence - go to home first for reliable search
            commands = [
                (["adb", "shell", "input", "keyevent", "KEYCODE_HOME"], "Go to home screen", 3),
                (["adb", "shell", "input", "keyevent", "KEYCODE_SEARCH"], "Open search", 3),
                (["adb", "shell", "input", "text", title_formatted], "Type search", 3), 
                (["adb", "shell", "input", "keyevent", "KEYCODE_ENTER"], "Submit search", 5),
                # (["adb", "shell", "input", "keyevent", "KEYCODE_DPAD_DOWN"], "Navigate to first result", 2),
                (["adb", "shell", "input", "keyevent", "KEYCODE_ENTER"], "Select first result", 3),
            ]

            for cmd, description, wait_time in commands:
                print(f"🔧 [Background] {description}...")
                result = await asyncio.to_thread(
                    subprocess.run, cmd, capture_output=True, text=True, timeout=10
                )
                
                if result.returncode != 0:
                    print(f"⚠️ [Background] Command failed: {result.stderr.strip() if result.stderr else 'Unknown error'}")
                
                await asyncio.sleep(wait_time)

            print(f"✅ [Background] Search completed for '{title}'")

        except Exception as e:
            print(f"❌ [Background] Search error for '{title}': {e}")
    
    async def pause_playback(self):
        """Pause current playback and clear info screen overlay"""
        try:
            # Send pause command
            pause_success = await self._send_media_key_async("KEYCODE_MEDIA_PAUSE")
            if not pause_success:
                return False
            
            # Small delay to let the info screen appear
            await asyncio.sleep(1)
            
            # Send back to clear the info screen (so chess board stays visible)
            back_success = await self._send_media_key_async("KEYCODE_BACK")
            
            # Return success even if back fails - pause is the main action
            return pause_success
            
        except Exception as e:
            print(f"❌ Pause error: {e}")
            return False
    
    async def resume_playback(self):
        """Resume playback"""
        return await self._send_media_key_async("KEYCODE_MEDIA_PLAY")
    
    async def rewind_playback(self):
        """Rewind playback"""
        return await self._send_media_key_async("KEYCODE_MEDIA_REWIND")
    
    async def skip_backward(self):
        """Skip backward (usually 10-30 seconds)"""
        return await self._send_media_key_async("KEYCODE_MEDIA_SKIP_BACKWARD")
    
    async def fast_forward_playback(self):
        """Fast forward playback"""
        return await self._send_media_key_async("KEYCODE_MEDIA_FAST_FORWARD")
    
    async def skip_forward(self):
        """Skip forward (usually 10-30 seconds)"""
        return await self._send_media_key_async("KEYCODE_MEDIA_SKIP_FORWARD")
    
    async def seek_left(self):
        """Seek backward using DPAD left (UI navigation)"""
        return await self._send_media_key_async("KEYCODE_DPAD_LEFT")
    
    async def seek_right(self):
        """Seek forward using DPAD right (UI navigation)"""
        return await self._send_media_key_async("KEYCODE_DPAD_RIGHT")
    
    async def show_info(self):
        """Show playback info/controls overlay"""
        return await self._send_media_key_async("KEYCODE_INFO")
    
    async def back_key(self):
        """Send back key (dismiss overlays, go back in UI)"""
        return await self._send_media_key_async("KEYCODE_BACK")
    
    async def enter_key(self):
        """Send enter key (confirm)"""
        return await self._send_media_key_async("KEYCODE_ENTER")
    
    async def _send_media_key_async(self, keycode: str) -> bool:
        """Send media key command to TV"""
        try:
            if not await asyncio.to_thread(self.ensure_tv_connection):
                print("❌ Could not connect to Google TV for media control")
                return False

            cmd = ["adb", "shell", "input", "keyevent", keycode]
            result = await asyncio.to_thread(
                subprocess.run, cmd, capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                print(f"✅ Media key {keycode} sent successfully")
                return True
            else:
                print(f"⚠️ Media key failed: {result.stderr.strip() if result.stderr else 'Unknown error'}")
                return False

        except Exception as e:
            print(f"❌ Media key error: {e}")
            return False
    
    async def store_viewing_request(self, title: str):
        """Store what user requested to watch in mem0"""
        if self.memory_client:
            try:
                context = {
                    "type": "content_request",
                    "query": f"User requested to play: {title}",
                    "timestamp": datetime.now(),
                }
                await asyncio.to_thread(
                    self.memory_client.add,
                    messages=[{"role": "user", "content": context["query"]}],
                    user_id="chess_tv_user",
                    metadata={
                        "source": "chess_tv_controller",
                        "timestamp": str(context["timestamp"]),
                    }
                )
                print(f"💾 Stored viewing request: {title}")
            except Exception as e:
                print(f"⚠️ Failed to store memory: {e}")
    
    def test_connection(self):
        """Test ADB connection"""
        print("🧪 Testing TV connection...")
        return self.ensure_tv_connection()


# Standalone testing interface
async def main():
    parser = argparse.ArgumentParser(description="Chess TV Controller - Standalone Testing")
    parser.add_argument("command", choices=["search", "pause", "resume", "rewind", "skip_back", "ff", "skip_forward", "seek_left", "seek_right", "info", "back", "test"], 
                       help="Command to execute")
    parser.add_argument("query", nargs="?", help="Search query (for search command)")
    
    args = parser.parse_args()
    
    controller = ChessTVController()
    
    if args.command == "test":
        success = controller.test_connection()
        print(f"🧪 Connection test: {'PASS' if success else 'FAIL'}")
        
    elif args.command == "search":
        if not args.query:
            print("❌ Search requires a query. Example: python tv_controller.py search 'Magnus Carlsen'")
            return
        
        print(f"🔍 Searching for: '{args.query}'")
        result = controller.search_and_play_content(args.query)
        print(result)
        
        # Wait a bit to see the background task complete
        await asyncio.sleep(15)
        
    elif args.command == "pause":
        print("⏸️ Sending pause command...")
        success = await controller.pause_playback()
        print(f"Pause: {'SUCCESS' if success else 'FAILED'}")
        
    elif args.command == "resume":
        print("▶️ Sending resume command...")
        success = await controller.resume_playback()
        print(f"Resume: {'SUCCESS' if success else 'FAILED'}")
        
    elif args.command == "rewind":
        print("⏪ Sending rewind command...")
        success = await controller.rewind_playback()
        print(f"Rewind: {'SUCCESS' if success else 'FAILED'}")
        
    elif args.command == "skip_back":
        print("⏮️ Sending skip backward command...")
        success = await controller.skip_backward()
        print(f"Skip Back: {'SUCCESS' if success else 'FAILED'}")
        
    elif args.command == "ff":
        print("⏩ Sending fast forward command...")
        success = await controller.fast_forward_playback()
        print(f"Fast Forward: {'SUCCESS' if success else 'FAILED'}")
        
    elif args.command == "skip_forward":
        print("⏭️ Sending skip forward command...")
        success = await controller.skip_forward()
        print(f"Skip Forward: {'SUCCESS' if success else 'FAILED'}")
        
    elif args.command == "seek_left":
        print("⬅️ Sending DPAD left (seek backward)...")
        success = await controller.seek_left()
        print(f"Seek Left: {'SUCCESS' if success else 'FAILED'}")
        
    elif args.command == "seek_right":
        print("➡️ Sending DPAD right (seek forward)...")
        success = await controller.seek_right()
        print(f"Seek Right: {'SUCCESS' if success else 'FAILED'}")
        
    elif args.command == "info":
        print("ℹ️ Sending info key (show controls)...")
        success = await controller.show_info()
        print(f"Info: {'SUCCESS' if success else 'FAILED'}")
        
    elif args.command == "back":
        print("🔙 Sending back key (dismiss overlays)...")
        success = await controller.back_key()
        print(f"Back: {'SUCCESS' if success else 'FAILED'}")


if __name__ == "__main__":
    print("🎬 Chess TV Controller - Standalone Testing Mode")
    asyncio.run(main())
