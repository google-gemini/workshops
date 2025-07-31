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

"""
Simple test to capture Chrome audio using pipewire_python
"""

import os
import subprocess
import sys
import threading
import time

from pipewire_python.controller import Controller


def get_chrome_target():
    """Get Chrome target - just use the node name directly"""

    print("🎯 Using Chrome node name as target...")

    # pw-record accepts node names directly as targets
    # From your pw-cli output: node.name = "Google Chrome"
    chrome_target = "Google Chrome"

    print(f"✓ Chrome target: {chrome_target}")
    return chrome_target


def test_chrome_capture():
    """Test capturing Chrome audio stream directly"""

    print("🎬 Setting up Chrome audio capture...")

    # Get Chrome target - just use node name
    chrome_target = get_chrome_target()

    try:
        # Create controller
        audio_controller = Controller()

        # Configure for Chrome's audio stream
        audio_controller.set_config(
            rate=48000,  # Match Chrome's rate from your output
            channels=2,  # Stereo
            _format="f32",  # Float32 format
            target=chrome_target,  # Use discovered target
            verbose=True,  # See what's happening
        )

        print(f"✓ Configured to capture from Chrome stream {chrome_target}")

        # Test 1: Record to regular file
        print("\n📼 Test 1: Recording to file for 5 seconds...")
        test_file = "/tmp/chrome_test.wav"

        audio_controller.record(audio_filename=test_file, timeout_seconds=5, verbose=True)

        if os.path.exists(test_file):
            file_size = os.path.getsize(test_file)
            print(f"✓ Recorded {file_size} bytes to {test_file}")
        else:
            print("✗ No file created")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


def test_fifo_capture():
    """Better FIFO streaming test with continuous reading"""

    fifo_path = "/tmp/chrome_audio_fifo"

    print("\n🔄 Test 2: Continuous FIFO streaming test...")

    chrome_target = get_chrome_target()

    try:
        # Remove existing FIFO if present
        if os.path.exists(fifo_path):
            os.unlink(fifo_path)

        # Create named pipe
        os.mkfifo(fifo_path)
        print(f"✓ Created FIFO at {fifo_path}")

        # Set up controller
        audio_controller = Controller()
        audio_controller.set_config(rate=48000, channels=2, _format="f32", target=chrome_target)

        def record_worker():
            """Record to FIFO in background"""
            print("🎤 Starting FIFO recording...")
            try:
                print(f"🎤 About to call pw-cat record to {fifo_path}")
                # Record for longer to give us time to read
                audio_controller.record(audio_filename=fifo_path, timeout_seconds=15)
                print("🎤 pw-cat record completed")
            except Exception as e:
                print(f"❌ Record error: {e}")
                import traceback

                traceback.print_exc()

        def read_worker():
            """Continuously read from FIFO"""
            time.sleep(2)  # Give recording time to start
            print("👂 Starting continuous FIFO reading...")

            total_bytes = 0
            try:
                with open(fifo_path, "rb") as f:
                    for i in range(10):  # Read 10 times
                        data = f.read(4800)  # ~0.1 sec of audio at 48kHz stereo f32
                        chunk_size = len(data)
                        total_bytes += chunk_size
                        print(f"   Read chunk {i+1}: {chunk_size} bytes (total: {total_bytes})")

                        if chunk_size == 0:
                            print("   No more data available")
                            break

                        time.sleep(0.1)  # Small delay between reads

                print(f"✓ Total read from FIFO: {total_bytes} bytes")

            except Exception as e:
                print(f"Read error: {e}")

        # Start both threads
        record_thread = threading.Thread(target=record_worker)
        read_thread = threading.Thread(target=read_worker)

        record_thread.start()
        read_thread.start()

        # Wait for completion
        read_thread.join()
        record_thread.join()

        print("✓ FIFO streaming test completed")

    except Exception as e:
        print(f"✗ FIFO Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists(fifo_path):
            os.unlink(fifo_path)


def test_direct_pwcat():
    """Test calling pw-cat directly without the library"""

    fifo_path = "/tmp/chrome_direct_fifo"

    print("\n🔧 Test 3: Direct pw-cat FIFO test...")

    try:
        # Remove existing FIFO if present
        if os.path.exists(fifo_path):
            os.unlink(fifo_path)

        # Create named pipe
        os.mkfifo(fifo_path)
        print(f"✓ Created FIFO at {fifo_path}")

        def direct_record():
            """Call pw-cat directly"""
            cmd = [
                "pw-cat",
                "--record",
                fifo_path,
                "--target",
                "Google Chrome",
                "--rate",
                "48000",
                "--channels",
                "2",
                "--format",
                "f32",
                "--verbose",
            ]
            print(f"🎤 Running: {' '.join(cmd)}")
            try:
                subprocess.run(cmd, timeout=15)
                print("🎤 Direct pw-cat completed")
            except subprocess.TimeoutExpired:
                print("🎤 Direct pw-cat timed out (expected)")
            except Exception as e:
                print(f"❌ Direct pw-cat error: {e}")

        def read_worker():
            """Read from FIFO"""
            time.sleep(3)  # Give pw-cat more time to start
            print("👂 Starting direct FIFO reading...")

            total_bytes = 0
            try:
                with open(fifo_path, "rb") as f:
                    for i in range(8):  # Read 8 times
                        data = f.read(9600)  # ~0.2 sec of audio
                        chunk_size = len(data)
                        total_bytes += chunk_size
                        print(f"   Read chunk {i+1}: {chunk_size} bytes (total: {total_bytes})")

                        if chunk_size == 0:
                            print("   No more data available")
                            break

                        time.sleep(0.2)  # Slightly longer delay

                print(f"✓ Total read from direct FIFO: {total_bytes} bytes")

            except Exception as e:
                print(f"❌ Direct read error: {e}")

        # Start both threads
        record_thread = threading.Thread(target=direct_record)
        read_thread = threading.Thread(target=read_worker)

        record_thread.start()
        read_thread.start()

        # Wait for completion
        read_thread.join()
        record_thread.join()

        print("✓ Direct pw-cat test completed")

    except Exception as e:
        print(f"✗ Direct pw-cat Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists(fifo_path):
            os.unlink(fifo_path)


def test_stdout_streaming():
    """Stream pw-cat output directly via stdout"""

    print("\n🚀 Test 4: Direct stdout streaming...")

    try:
        cmd = [
            "pw-cat",
            "--record",
            "-",  # Write to stdout!
            "--target",
            "Google Chrome",
            "--rate",
            "48000",
            "--channels",
            "2",
            "--format",
            "f32",
            "--raw",  # Output raw PCM data, not WAV
        ]

        print(f"🎤 Running: {' '.join(cmd)}")

        # Start pw-cat as subprocess
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("👂 Reading raw audio from pw-cat stdout...")

        total_bytes = 0
        for i in range(10):
            # Read chunks directly from pw-cat stdout
            data = process.stdout.read(4800)  # ~0.1 sec at 48kHz stereo f32

            if not data:
                print("   No more data from pw-cat")
                break

            chunk_size = len(data)
            total_bytes += chunk_size
            print(f"   Read chunk {i+1}: {chunk_size} bytes (total: {total_bytes})")

            time.sleep(0.1)

        process.terminate()
        process.wait()

        print(f"✓ Total streamed from stdout: {total_bytes} bytes")

    except Exception as e:
        print(f"❌ Stdout streaming error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🧪 Testing Chrome audio capture with pipewire_python")
    print("📺 Make sure Chrome is playing audio before running this!")
    print()

    # Basic file recording test
    # test_chrome_capture()

    # FIFO streaming test with library
    test_fifo_capture()

    # Direct pw-cat test
    test_direct_pwcat()

    # Stdout streaming test
    test_stdout_streaming()

    print("\n🎉 Tests completed!")
