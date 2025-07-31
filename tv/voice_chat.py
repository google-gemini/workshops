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
HDMI capture card audio/video test using pipewire_python
"""

import base64
import io
import os
import subprocess
import sys
import tempfile
import threading
import time

import cv2
import pyaudio
from PIL import Image
from pipewire_python.controller import Controller


def enumerate_audio_devices():
    """Enumerate all PyAudio input devices"""

    print("📋 Enumerating PyAudio input devices...")

    pya = pyaudio.PyAudio()

    print("📋 Available PyAudio input devices:")
    for i in range(pya.get_device_count()):
        info = pya.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:  # Only input devices
            print(f"  {i}: {info['name']}")
            print(f"     Channels: {info['maxInputChannels']}")
            print(f"     Sample Rate: {info['defaultSampleRate']}")
            print()

    pya.terminate()


def test_direct_pyaudio():
    """Test direct PyAudio capture with Gemini-compatible settings"""

    print("🎤 Testing direct PyAudio capture...")

    pya = pyaudio.PyAudio()

    # Find HDMI device
    hdmi_device = None
    for i in range(pya.get_device_count()):
        info = pya.get_device_info_by_index(i)
        if "USB3.0 Video" in info["name"]:
            hdmi_device = i
            print(f"✓ Found HDMI device: {info['name']}")
            break

    if hdmi_device is None:
        print("❌ HDMI device not found")
        pya.terminate()
        return

    try:
        # Try Gemini-compatible settings directly
        stream = pya.open(
            format=pyaudio.paInt16,  # s16 (Gemini format)
            channels=1,  # Mono (Gemini requirement)
            rate=16000,  # 16kHz (Gemini rate)
            input=True,
            input_device_index=hdmi_device,
            frames_per_buffer=1024,
        )

        print("🎉 PyAudio opened HDMI device with Gemini settings!")

        # Test reading some data
        total_bytes = 0
        for i in range(10):
            data = stream.read(1600)  # 0.1 second of 16kHz mono s16
            chunk_size = len(data)
            total_bytes += chunk_size
            print(f"   Read chunk {i+1}: {chunk_size} bytes (total: {total_bytes})")

        stream.stop_stream()
        stream.close()

        print(f"✓ Total PyAudio capture: {total_bytes} bytes")

    except Exception as e:
        print(f"❌ PyAudio error: {e}")
        import traceback

        traceback.print_exc()

    pya.terminate()


def test_audio_quality():
    """Test pw-cat audio quality by recording to file and playing back"""

    print("🎵 Testing pw-cat audio quality (Gemini format)...")

    test_file = "/tmp/hdmi_gemini_test.wav"

    # Remove existing file
    if os.path.exists(test_file):
        os.unlink(test_file)

    try:
        # Record 5 seconds with Gemini settings
        cmd = [
            "pw-cat",
            "--record",
            test_file,
            "--target",
            "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo",
            "--rate",
            "16000",
            "--channels",
            "1",
            "--format",
            "s16",
        ]

        print(f"🎤 Recording 5 seconds with Gemini settings...")
        print(f"   Command: {' '.join(cmd)}")

        result = subprocess.run(cmd, timeout=5, capture_output=True, text=True)

        if os.path.exists(test_file):
            file_size = os.path.getsize(test_file)
            print(f"✓ Recorded {file_size} bytes to {test_file}")
            print(f"🎧 Play back with: pw-cat --playback {test_file}")
            print(f"🔊 Or with: ffplay {test_file}")
        else:
            print("❌ No file created")
            if result.stderr:
                print(f"Error: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("✓ Recording completed (5 second timeout)")
        if os.path.exists(test_file):
            file_size = os.path.getsize(test_file)
            print(f"✓ Recorded {file_size} bytes to {test_file}")
            print(f"🎧 Play back with: pw-cat --playback {test_file}")
            print(f"🔊 Or with: ffplay {test_file}")
    except Exception as e:
        print(f"❌ Recording error: {e}")


def test_hdmi_video_capture():
    """Test HDMI video capture and frame processing"""

    print("🎥 Testing HDMI video capture...")

    # Open HDMI capture device
    cap = cv2.VideoCapture("/dev/video4")

    if not cap.isOpened():
        print("❌ Cannot open HDMI video capture device /dev/video4")
        return

    # Set resolution (optional - device will use native if possible)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    print("✓ HDMI video capture device opened")

    # Let device fully initialize
    print("⏱️  Letting capture device stabilize...")
    time.sleep(1.0)

    try:
        frame_count = 0
        for i in range(5):  # Capture 5 test frames
            ret, frame = cap.read()
            if not ret:
                print(f"❌ Failed to read frame {i+1}")
                break

            frame_count += 1

            # Convert BGR → RGB (OpenCV uses BGR, PIL expects RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert to PIL Image
            img = Image.fromarray(frame_rgb)
            original_size = img.size

            # Scale down for Gemini (like Get_started_LiveAPI.py)
            img.thumbnail([1024, 1024])
            thumbnail_size = img.size

            # Save frame to temp file for inspection
            temp_file = tempfile.NamedTemporaryFile(suffix=f"_frame_{frame_count}.jpg", delete=False, dir="/tmp")
            img.save(temp_file.name, format="jpeg")
            temp_file.close()

            # Convert to base64 for Gemini Live API
            image_io = io.BytesIO()
            img.save(image_io, format="jpeg")
            image_io.seek(0)

            image_bytes = image_io.read()
            image_b64 = base64.b64encode(image_bytes).decode()

            print(f"   Frame {frame_count}:")
            print(f"     Original: {original_size}")
            print(f"     Thumbnail: {thumbnail_size}")
            print(f"     Base64 length: {len(image_b64)} chars")
            print(f"     Saved to: {temp_file.name}")

            # Small delay between frames
            time.sleep(0.5)

        print(f"✓ Successfully captured {frame_count} video frames")
        print("📤 Ready for Gemini Live API: {'mime_type': 'image/jpeg', 'data': base64_string}")

    except Exception as e:
        print(f"❌ Video capture error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        cap.release()


def get_hdmi_audio_target():
    """Get HDMI capture card audio target"""

    print("🎯 Using HDMI capture card audio target...")

    # HDMI capture card audio source from pactl list sources
    hdmi_target = "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo"

    print(f"✓ HDMI audio target: {hdmi_target}")
    return hdmi_target


def test_hdmi_capture():
    """Test capturing HDMI audio stream directly"""

    print("🎬 Setting up HDMI audio capture...")

    # Get HDMI target - use device name
    hdmi_target = get_hdmi_audio_target()

    try:
        # Create controller
        audio_controller = Controller()

        # Configure for HDMI audio stream (Gemini-compatible)
        audio_controller.set_config(
            rate=16000,  # Gemini sample rate
            channels=1,  # Gemini mono requirement
            _format="s16",  # Fixed format for pw-cat
            target=hdmi_target,  # Use HDMI target
            verbose=True,  # See what's happening
        )

        print(f"✓ Configured to capture from HDMI stream {hdmi_target}")

        # Test 1: Record to regular file
        print("\n📼 Test 1: Recording to file for 5 seconds...")
        test_file = "/tmp/hdmi_test.wav"

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

    fifo_path = "/tmp/hdmi_audio_fifo"

    print("\n🔄 Test 2: Continuous FIFO streaming test...")

    hdmi_target = get_hdmi_audio_target()

    try:
        # Remove existing FIFO if present
        if os.path.exists(fifo_path):
            os.unlink(fifo_path)

        # Create named pipe
        os.mkfifo(fifo_path)
        print(f"✓ Created FIFO at {fifo_path}")

        # Set up controller
        audio_controller = Controller()
        audio_controller.set_config(rate=16000, channels=1, _format="s16", target=hdmi_target)

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

    fifo_path = "/tmp/hdmi_direct_fifo"

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
                "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo",
                "--rate",
                "16000",
                "--channels",
                "1",
                "--format",
                "s16",
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
            "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo",
            "--rate",
            "16000",
            "--channels",
            "1",
            "--format",
            "s16",
            "--raw",  # Output raw PCM data, not WAV
        ]

        print(f"🎤 Running: {' '.join(cmd)}")

        # Start pw-cat as subprocess
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("👂 Reading raw audio from pw-cat stdout...")

        total_bytes = 0
        for i in range(10):
            # Read chunks directly from pw-cat stdout
            data = process.stdout.read(1600)  # ~0.1 sec at 16kHz mono s16

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
    print("🧪 Testing HDMI capture card audio with pipewire_python + PyAudio")
    print("📺 Make sure HDMI source is playing audio!")
    print()

    # Enumerate PyAudio devices
    enumerate_audio_devices()

    # Test direct PyAudio capture
    test_direct_pyaudio()

    # Test audio quality by recording to file
    test_audio_quality()

    # Test HDMI video capture
    test_hdmi_video_capture()

    # Basic file recording test
    # test_hdmi_capture()

    # FIFO streaming test with library
    # test_fifo_capture()

    # Direct pw-cat test
    # test_direct_pwcat()

    # Stdout streaming test
    # test_stdout_streaming()

    print("\n🎉 Tests completed!")
