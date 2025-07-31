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

"""Test universal search for Google TV Streamer"""

import subprocess
import time


def test_adb_connection():
    """Test ADB connection to Google TV Streamer"""
    print("🔗 Testing ADB connection...")

    # Connect to device
    print("📡 Connecting to 192.168.50.221...")
    connect_result = subprocess.run(["adb", "connect", "192.168.50.221"], capture_output=True, text=True)

    if "connected" in connect_result.stdout.lower():
        print("✅ ADB connected successfully")
    else:
        print(f"⚠️ Connection result: {connect_result.stdout.strip()}")

    # Test device is responsive
    print("🧪 Testing device responsiveness...")
    test_result = subprocess.run(
        ["adb", "shell", "echo", "test"],
        capture_output=True,
        text=True,
        timeout=5,
    )

    if test_result.returncode == 0 and "test" in test_result.stdout:
        print("✅ Device responsive")
        return True
    else:
        print("❌ Device not responsive")
        return False


def test_universal_search_debug():
    """Test universal search with debugging and longer delays"""
    print(f"\n🌟 Testing Universal Search (KEYCODE_SEARCH approach)")
    print("📺 Watch your TV screen carefully during each step")

    # Step 1: Open search overlay
    print(f"\n🔧 Step 1: Opening universal search overlay...")
    print(f"💻 Command: adb shell input keyevent KEYCODE_SEARCH")
    subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_SEARCH"])
    print("⏳ Waiting 3 seconds - should see search overlay...")
    time.sleep(3)

    # Step 2: Type query
    print(f"\n🔧 Step 2: Typing search query...")
    print(f"💻 Command: adb shell input text 'The%sBig%sSleep'")
    subprocess.run(["adb", "shell", "input", "text", "The%sBig%sSleep"])
    print("⏳ Waiting 3 seconds - should see text in search box...")
    time.sleep(3)

    # Step 3: Submit search
    print(f"\n🔧 Step 3: Submitting search...")
    print(f"💻 Command: adb shell input keyevent KEYCODE_ENTER")
    subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_ENTER"])
    print("⏳ Waiting 5 seconds - should see search results...")
    time.sleep(5)

    # Step 4: Try to select first result
    print(f"\n🔧 Step 4: Selecting first result...")
    print(f"💻 Command: adb shell input keyevent KEYCODE_ENTER")
    subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_ENTER"])
    print("⏳ Waiting 5 seconds - should start playing content...")
    time.sleep(5)

    print("\n🎬 Universal search sequence complete!")
    print("📺 What happened on your TV?")


def test_universal_search_alternate():
    """Try alternate approach with DPAD navigation"""
    print(f"\n🌟 Testing Universal Search with DPAD navigation")
    print("📺 Alternative approach - navigate to result manually")

    # Step 1: Open search
    print(f"\n🔧 Step 1: Opening search...")
    subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_SEARCH"])
    time.sleep(3)

    # Step 2: Type query
    print(f"\n🔧 Step 2: Typing query...")
    subprocess.run(["adb", "shell", "input", "text", "The%sBig%sSleep"])
    time.sleep(3)

    # Step 3: Submit search
    print(f"\n🔧 Step 3: Submitting search...")
    subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_ENTER"])
    time.sleep(5)

    # Step 4: Navigate down to first result (maybe search box is selected)
    print(f"\n🔧 Step 4: Navigate down to results...")
    subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_DPAD_DOWN"])
    time.sleep(2)

    # Step 5: Select result
    print(f"\n🔧 Step 5: Select result...")
    subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_ENTER"])
    time.sleep(5)

    print("\n🎬 Alternate search complete!")


def main():
    """Run universal search debugging"""
    print("🧪 Universal Search Debug for Google TV Streamer")
    print("=" * 60)
    print("📺 Make sure your TV is on and showing the home screen!")

    # Test connection first
    if not test_adb_connection():
        print("\n❌ Cannot proceed without ADB connection")
        return

    # Test the universal search approach with debugging
    test_universal_search_debug()

    print("\n" + "=" * 60)
    print("❓ Did that work? If not, let's try the alternate approach...")
    input("Press Enter to try alternate approach (or Ctrl+C to quit)")

    test_universal_search_alternate()

    print("\n✅ Testing complete!")
    print("💡 Let me know which approach worked!")


if __name__ == "__main__":
    main()
