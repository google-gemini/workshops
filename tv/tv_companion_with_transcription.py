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

"""HDMI TV Companion with real-time transcription pipeline

Combines continuous TV transcription with video streaming to Gemini Live API
"""

import asyncio
import base64
import io
import json
import os
import queue
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime

import cv2
import numpy as np
import pyaudio
import pychromecast
from google import genai
from google.cloud import speech
from google.genai import types
from mem0 import MemoryClient
from PIL import Image
from scenedetect import AdaptiveDetector, ContentDetector, HistogramDetector, SceneManager
from scenedetect.backends import VideoCaptureAdapter

if sys.version_info < (3, 11, 0):
    import exceptiongroup
    import taskgroup

    asyncio.TaskGroup = taskgroup.TaskGroup
    asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024
STREAMING_LIMIT = 240000  # 4 minutes (Google Cloud Speech limit)

MODEL = "gemini-2.5-flash-preview-native-audio-dialog"

# HDMI capture device settings
HDMI_VIDEO_DEVICE = "/dev/video4"
HDMI_AUDIO_TARGET = "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo"

client = genai.Client()

# TV Companion configuration
CONFIG = {
    "response_modalities": ["AUDIO"],
    # TODO: For demo, hardcoding The Big Sleep info. In production, should dynamically
    # pull film title, year, cast, director from TMDB/Wikipedia for whatever is being watched
    "system_instruction": (
        """You are an intelligent TV companion with deep knowledge of film and television.

You can both provide insightful commentary AND control the TV for users.

## TV Control Capabilities:
- Search for and play any movie or show using search_and_play_content
- Pause playback with pause_playback
- Access user's viewing history with search_user_history
- Toggle watching mode on/off for automatic scene commentary

## Commentary Style:
When you receive scene packages (dialogue + screenshots), provide insightful commentary that enhances the viewing experience.

Be curious and analytical:
- Point out interesting cinematography, lighting, and visual composition
- Comment on acting performances, dialogue delivery, and character dynamics
- Identify genre conventions, directorial techniques, and storytelling methods
- Ask thought-provoking questions about what we're seeing
- Make connections between scenes and build understanding of the narrative
- Share relevant context about film history, techniques, or cultural significance
- Suggest things to watch for in upcoming moments

Strike a balance between being informative and conversational - like watching with a knowledgeable film buff friend who notices details others might miss.

Feel free to suggest movies to watch or help users find content they're interested in. Only comment when you have something genuinely insightful to add. Silence is perfectly fine when scenes speak for themselves."""
    ),
    "tools": [
        {
            "function_declarations": [
                # {
                #     "name": "search_film_context",
                #     "description": (
                #         "Search comprehensive film knowledge including cast bios,"
                #         " crew info, plot analysis, themes, and production details."
                #         " Use this when you encounter something interesting that"
                #         " deserves deeper commentary."
                #     ),
                #     "parameters": {
                #         "type": "object",
                #         "properties": {
                #             "query": {
                #                 "type": "string",
                #                 "description": (
                #                     "What to search for (e.g., 'Humphrey Bogart"
                #                     " career', 'film noir lighting techniques',"
                #                     " 'Howard Hawks directing style', 'Raymond"
                #                     " Chandler vs William Faulkner writing"
                #                     " differences')"
                #                 ),
                #             }
                #         },
                #         "required": ["query"],
                #     },
                # },
                {
                    "name": "search_and_play_content",
                    "description": (
                        "Search for and start playing a movie or show on the TV" " using Google TV's universal search"
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Movie or show title to search for",
                            }
                        },
                        "required": ["title"],
                    },
                },
                {
                    "name": "search_user_history",
                    "description": (
                        "Search the user's personal viewing history and past"
                        " questions. Use this to recall what the user has"
                        " previously asked about, movies they've watched, or topics"
                        " they've discussed."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": (
                                    "Optional: What to search for in user's history"
                                    " (e.g., 'Humphrey Bogart questions', 'film"
                                    " noir discussions', 'previous movies"
                                    " watched'). Leave blank to get recent"
                                    " activity."
                                ),
                            }
                        },
                        "required": [],  # No required params - query is optional
                    },
                },
                {
                    "name": "start_watching_mode",
                    "description": ("Start automatically commenting on scenes as they happen"),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
                {
                    "name": "stop_watching_mode",
                    "description": "Stop automatic scene commentary",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
                {
                    "name": "pause_playback",
                    "description": "Pause the currently playing content on TV",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
                # {
                #     "name": "resume_playback",
                #     "description": "Resume or play the paused content on TV",
                #     "parameters": {
                #         "type": "object",
                #         "properties": {},
                #         "required": [],
                #     },
                # },
                # {
                #     "name": "describe_current_scene",
                #     "description": (
                #         "Analyze what just happened in the most recent scene"
                #     ),
                #     "parameters": {
                #         "type": "object",
                #         "properties": {},
                #         "required": [],
                #     },
                # },
            ]
        }
    ],
}


class SceneBuffer:
    """Buffers visual and audio content for a single scene"""

    def __init__(self, scene_number: int):
        self.scene_number = scene_number
        self.frames = []  # Store multiple frames per scene
        self.transcripts = []
        self.start_time = time.time()

    def add_frame(self, frame_data, is_initial=False):
        """Add a frame to this scene"""
        elapsed = time.time() - self.start_time
        timestamp = f"{int(elapsed//60):02d}:{elapsed%60:05.2f}"

        frame_entry = {
            "data": frame_data,
            "timestamp": timestamp,
            "is_initial": is_initial,
        }
        self.frames.append(frame_entry)

        frame_type = "initial" if is_initial else "periodic"
        print(f"📸 Added {frame_type} frame to Scene {self.scene_number} at" f" {timestamp}")

    def add_transcript(self, text: str):
        """Add a transcript line with timestamp"""
        elapsed = time.time() - self.start_time
        timestamp = f"{int(elapsed//60):02d}:{elapsed%60:05.2f}"
        self.transcripts.append(f"[{timestamp}] {text}")

    def get_duration(self) -> float:
        """Get scene duration in seconds"""
        return time.time() - self.start_time

    def create_scene_package(self) -> dict:
        """Create a complete scene package for the model"""
        duration = self.get_duration()
        transcript_text = "\n".join(self.transcripts) if self.transcripts else ""

        return {
            "type": "scene_package",
            "scene_number": self.scene_number,
            "duration": f"{duration:.1f}s",
            "transcript": transcript_text,
            "frames": self.frames,
            "summary": (
                f"Scene {self.scene_number} ({duration:.1f}s):"
                f" {len(self.transcripts)} dialogue lines,"
                f" {len(self.frames)} frames"
            ),
        }


class TVAudioStream:
    """Captures TV audio using pw-cat and provides it as a stream for transcription"""

    def __init__(self):
        self._buff = queue.Queue()
        self.closed = True
        self.audio_process = None

    async def __aenter__(self):
        self.closed = False
        # Start pw-cat process for TV audio
        cmd = [
            "pw-cat",
            "--record",
            "-",
            "--target",
            HDMI_AUDIO_TARGET,
            "--rate",
            str(SEND_SAMPLE_RATE),
            "--channels",
            "1",
            "--format",
            "s16",
            "--raw",
        ]

        self.audio_process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Start feeding audio data into buffer
        asyncio.create_task(self._feed_buffer())
        return self

    async def __aexit__(self, type, value, traceback):
        self.closed = True
        if self.audio_process:
            self.audio_process.terminate()
            await self.audio_process.wait()
        self._buff.put(None)  # Signal generator to terminate

    async def _feed_buffer(self):
        """Read audio from pw-cat and put into buffer"""
        chunk_size = int(SEND_SAMPLE_RATE / 10)  # 100ms chunks
        bytes_expected = chunk_size * 2  # 2 bytes per s16 sample
        chunks_sent = 0

        while not self.closed:
            try:
                data = await self.audio_process.stdout.read(bytes_expected)
                if not data:
                    print(f"📡 No more audio data from pw-cat")
                    break

                self._buff.put(data)
                chunks_sent += 1

                # Remove noisy logging - only log major milestones
                if chunks_sent % 500 == 0:  # Log every 50 seconds instead
                    print(f"📡 Audio buffer: {chunks_sent} chunks processed")

            except Exception as e:
                print(f"❌ Audio feed error: {e}")
                break

    def generator(self):
        """Generator that yields audio chunks for Google Cloud Speech"""
        chunks_yielded = 0
        while not self.closed:
            try:
                chunk = self._buff.get(timeout=1.0)  # 1 second timeout
                if chunk is None:
                    print("📡 Audio generator: received termination signal")
                    return

                chunks_yielded += 1
                # Remove noisy logging - only log major milestones
                if chunks_yielded % 500 == 0:  # Log every 50 seconds instead
                    print(f"📡 Audio generator: {chunks_yielded} chunks yielded")

                yield chunk
            except queue.Empty:
                print("⚠️ Audio generator: timeout waiting for chunk")
                continue


class HDMITVCompanionWithTranscription:

    def __init__(self):
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.video_cap = None
        self.speech_client = speech.SpeechClient()

        # User microphone input (like Wind Waker voice chat)
        self.pya = None
        self.mic_stream = None

        # Episodic memory
        self.memory_client = self._init_memory_client()
        self.conversation_context = []  # Track conversation flow

        # Watching mode control
        self.watching_mode = False  # Default: don't auto-send scenes

        # Shared video capture for both scene detection and periodic screenshots
        self.shared_cap = None

        # Load film context embeddings once at startup
        self.embeddings_data = self._load_embeddings()

        # TV connection management
        self.tv_ip = None  # Will be auto-discovered on first use

        # Speech recognition config
        self.speech_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SEND_SAMPLE_RATE,
            language_code="en-US",
            max_alternatives=1,
        )

        self.streaming_config = speech.StreamingRecognitionConfig(config=self.speech_config, interim_results=True)

        # Scene detection setup
        self.scene_manager = SceneManager()
        self.scene_manager.add_detector(HistogramDetector())
        self.scene_detection_active = False
        self.video_fps = None  # Store frame rate for timestamp calculations

        # Scene buffering
        self.current_scene = None
        self.scene_counter = 0
        self.max_scene_duration = 60  # 1 minutes max per scene
        self.periodic_screenshot_interval = 30  # Take screenshot every 30 seconds within scene
        self._last_scene_frame = None  # Store current frame for periodic capture sharing

    def _init_memory_client(self):
        """Initialize mem0 client for episodic memory"""
        api_key = os.getenv("MEM0_API_KEY")
        if not api_key:
            print("⚠️  MEM0_API_KEY not set, episodic memory disabled")
            return None

        try:
            client = MemoryClient(
                api_key=api_key,
                org_id="org_lOJM2vCRxHhS7myVb0vvaaY1rUauhqkKbg7Dg7KZ",
                project_id="proj_I6CXbVIrt0AFlWE0MU3TyKxkkYJam2bHm8nUxgEu",
            )
            print("✓ Episodic memory initialized")
            return client
        except Exception as e:
            print(f"⚠️  Failed to initialize memory: {e}")
            return None

    async def _store_memory_async(self, context):
        """Store memory asynchronously to avoid blocking audio"""
        try:
            await asyncio.to_thread(
                self.memory_client.add,
                messages=[{"role": "user", "content": context["query"]}],
                user_id="tv_companion_user",
                metadata={
                    "source": "tv_companion",
                    "timestamp": str(context["timestamp"]),
                },
            )
            print(f"💾 Stored user query: {context['query'][:50]}...")
        except Exception as e:
            print(f"⚠️  Failed to store memory: {e}")

    def find_pulse_device(self):
        """Find a PulseAudio device that works with PipeWire"""
        for i in range(self.pya.get_device_count()):
            info = self.pya.get_device_info_by_index(i)
            if "pulse" in info["name"].lower() and info["maxInputChannels"] > 0:
                return info
        return self.pya.get_default_input_device_info()

        # Speech recognition config
        self.speech_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SEND_SAMPLE_RATE,
            language_code="en-US",
            max_alternatives=1,
        )

        self.streaming_config = speech.StreamingRecognitionConfig(config=self.speech_config, interim_results=True)

        # Scene detection setup
        self.scene_manager = SceneManager()
        self.scene_manager.add_detector(HistogramDetector())
        self.scene_detection_active = False
        self.video_fps = None  # Store frame rate for timestamp calculations

        # Scene buffering
        self.current_scene = None
        self.scene_counter = 0
        self.max_scene_duration = 60  # 1 minutes max per scene
        self.periodic_screenshot_interval = 30  # Take screenshot every 30 seconds within scene
        self._last_scene_frame = None  # Store current frame for periodic capture sharing

    async def send_text(self):
        """Allow user to send text messages"""
        while True:
            text = await asyncio.to_thread(input, "message > ")
            if text.lower() == "q":
                break
            await self.session.send_realtime_input(text=text or ".")

    def on_new_scene(self, frame_img, frame_num):
        """Callback invoked when PySceneDetect finds a new scene"""
        # Calculate timestamp from frame number and fps
        timestamp_seconds = frame_num / self.video_fps if self.video_fps else 0
        minutes = int(timestamp_seconds // 60)
        seconds = timestamp_seconds % 60
        timestamp_str = f"{minutes:02d}:{seconds:05.2f}"

        print(f"🎬 Scene change detected at frame {frame_num} ({timestamp_str})")

        # Send previous scene package if it exists
        if self.current_scene is not None:
            self._finalize_current_scene()

        # Start new scene
        self._start_new_scene(frame_img, frame_num, timestamp_str)

    def _finalize_current_scene(self):
        """Send or discard scene package based on watching mode"""
        if self.current_scene is None:
            return

        scene_package = self.current_scene.create_scene_package()
        print(f"📦 Finalizing {scene_package['summary']}")

        if self.watching_mode:
            # Auto-send to Gemini
            try:
                self.out_queue.put_nowait(scene_package)
                print(f"📤 Auto-sent scene package (watching mode)")
            except:
                print(f"⚠️ Failed to queue scene package")
        else:
            # Just discard it - no storage
            print(f"📦 Discarded scene package (non-watching mode)")

    def _start_new_scene(self, frame_img, frame_num, timestamp_str):
        """Start a new scene buffer"""
        self.scene_counter += 1
        self.current_scene = SceneBuffer(self.scene_counter)

        print("🔍 _start_new_scene called: frame_img is" f" {'None' if frame_img is None else 'present'}")

        # Convert frame to our format
        if frame_img is not None:
            try:
                frame_data = self._convert_frame_to_base64(frame_img)
                self.current_scene.add_frame(frame_data, is_initial=True)
                print(f"🎬 Started Scene {self.scene_counter} at frame" f" {frame_num} ({timestamp_str})")
            except Exception as e:
                print(f"❌ Error converting initial frame: {e}")
                import traceback

                traceback.print_exc()
        else:
            print(f"🎬 Started Scene {self.scene_counter} (no frame available)")

    def _convert_frame_to_base64(self, frame_img):
        """Convert OpenCV frame to base64 format for Gemini"""
        try:
            print("🔧 Converting frame:" f" shape={frame_img.shape if hasattr(frame_img, 'shape') else 'no shape'}")

            # Convert numpy array to PIL Image
            frame_rgb = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img.thumbnail([1024, 1024])

            image_io = io.BytesIO()
            img.save(image_io, format="jpeg")
            image_io.seek(0)

            image_bytes = image_io.read()
            print(f"🔧 Frame converted successfully: {len(image_bytes)} bytes")

            return {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode(),
            }
        except Exception as e:
            print(f"❌ Frame conversion failed: {e}")
            raise

    async def run_scene_detection(self):
        """Run PySceneDetect on HDMI video stream"""
        print("🎬 Starting PySceneDetect scene detection...")

        # Initialize shared video capture
        self.shared_cap = cv2.VideoCapture(HDMI_VIDEO_DEVICE)
        if not self.shared_cap.isOpened():
            print(f"❌ Cannot open HDMI video device {HDMI_VIDEO_DEVICE}")
            return

        self.shared_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.shared_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # Get and store frame rate for timestamp calculations
        self.video_fps = self.shared_cap.get(cv2.CAP_PROP_FPS)
        print(f"📊 Video FPS: {self.video_fps}")

        # Wrap with VideoCaptureAdapter for PySceneDetect
        video_adapter = VideoCaptureAdapter(self.shared_cap)

        print(f"✓ HDMI video capture ready for scene detection")
        print(f"🎬 Using HistogramDetector for scene changes")

        # Run scene detection in a separate thread (it's blocking)
        await asyncio.to_thread(self._run_scene_detection_sync, video_adapter)

    def _run_scene_detection_sync(self, video_adapter):
        """Run scene detection synchronously in a thread"""
        try:
            self.scene_detection_active = True
            # This will block and call on_new_scene callback for each scene
            self.scene_manager.detect_scenes(video=video_adapter, callback=self.on_new_scene)
        except Exception as e:
            print(f"❌ Scene detection error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            self.scene_detection_active = False
            if self.shared_cap:
                self.shared_cap.release()

    async def monitor_scene_duration(self):
        """Monitor scene duration and finalize long scenes"""
        print("⏱️ Starting scene duration monitor...")

        while True:
            if self.current_scene is not None and self.current_scene.get_duration() > self.max_scene_duration:

                print(
                    f"⏱️ Scene {self.current_scene.scene_number} exceeded" f" {self.max_scene_duration}s, finalizing..."
                )
                self._finalize_current_scene()

                # Start a new scene without a frame (we'll get one on next scene change)
                self.scene_counter += 1
                self.current_scene = SceneBuffer(self.scene_counter)
                print(f"🎬 Started Scene {self.scene_counter} (duration timeout)")

            await asyncio.sleep(10)  # Check every 10 seconds

    async def capture_periodic_screenshots(self):
        """Capture periodic screenshots within the current scene using shared capture"""
        print("📸 Starting periodic screenshot capture every" f" {self.periodic_screenshot_interval}s...")

        # Wait for shared capture to be initialized
        while self.shared_cap is None:
            await asyncio.sleep(1)

        print(f"📸 Shared video capture ready for periodic screenshots")

        while True:
            # Capture immediately if there's a current scene
            if self.current_scene is not None:
                ret, frame = self.shared_cap.read()
                if ret:
                    try:
                        frame_data = self._convert_frame_to_base64(frame)
                        self.current_scene.add_frame(frame_data, is_initial=False)
                        print("✓ Added periodic frame to Scene" f" {self.current_scene.scene_number}")
                    except Exception as e:
                        print(f"❌ Error adding periodic frame: {e}")
                else:
                    print("⚠️ Failed to capture periodic screenshot")

            # Then sleep
            await asyncio.sleep(self.periodic_screenshot_interval)

    def _load_embeddings(self):
        """Load film embeddings once at startup"""
        try:
            embeddings_file = "The_Big_Sleep_1946_context_with_screenplay_embeddings.json"
            print(f"📚 Loading film embeddings from: {embeddings_file}")

            with open(embeddings_file, "r") as f:
                embeddings_data = json.load(f)

            print(f"✅ Loaded {len(embeddings_data)} embedding chunks")
            return embeddings_data

        except FileNotFoundError:
            print(f"⚠️ Embeddings file not found: {embeddings_file}")
            print(
                f"   Run: poetry run python -m film_context.create_embeddings"
                f" 'The_Big_Sleep_1946_context_with_screenplay.txt'"
            )
            return []
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            return []

    async def search_film_context(self, query, top_k=3):
        """Search film embeddings using semantic similarity"""
        try:
            print(f"🔍 Searching film context for: '{query}'")

            if not self.embeddings_data:
                return "No embeddings available - please create embeddings first"

            print(f"🔍 Using cached {len(self.embeddings_data)} chunks")

            # Get query embedding
            query_response = await asyncio.to_thread(
                client.models.embed_content,
                model="gemini-embedding-001",
                contents=query,
                config=types.EmbedContentConfig(task_type="retrieval_query"),
            )
            query_embedding = query_response.embeddings[0].values

            # Calculate similarities
            similarities = []
            for item in self.embeddings_data:
                similarity = np.dot(query_embedding, item["embedding"])
                similarities.append((similarity, item["text"], item["chunk_id"]))

            # Get top results
            similarities.sort(reverse=True)
            results = []

            print(f"🔍 Top {min(top_k, len(similarities))} matches:")
            for i in range(min(top_k, len(similarities))):
                score, text, chunk_id = similarities[i]

                # Try to identify what section this chunk comes from
                section_type = "Unknown"
                if "=== SCREENPLAY ===" in text or any(
                    keyword in text.upper() for keyword in ["FADE IN", "INT.", "EXT.", "CLOSE SHOT", "MARLOWE"]
                ):
                    section_type = "Screenplay"
                elif "=== CAST BIOGRAPHIES ===" in text or "was an American" in text or "born" in text.lower():
                    section_type = "Cast Bio"
                elif (
                    "=== CREW BIOGRAPHIES ===" in text
                    or "director" in text.lower()
                    or "cinematographer" in text.lower()
                ):
                    section_type = "Crew Bio"
                elif "=== FILM ANALYSIS ===" in text or "film" in text.lower():
                    section_type = "Film Analysis"
                elif "=== FILM OVERVIEW ===" in text or "TMDB" in text:
                    section_type = "TMDB Data"

                print(f"🔍 Match {i+1}: chunk {chunk_id}, score" f" {score:.3f} ({section_type})")
                print(f"    Preview: {text[:150].replace(chr(10), ' ')}...")
                print()

                results.append(text)

            return "\n\n---\n\n".join(results)

        except Exception as e:
            print(f"🔍 Film context search error: {e}")
            traceback.print_exc()
            return f"Search failed: {e}"

    def discover_tv_ip(self):
        """Use Chromecast discovery to find Google TV IP address"""
        try:
            print("🔍 Auto-discovering Google TV IP address...")

            # Use Chromecast discovery to find devices
            chromecasts, browser = pychromecast.get_listed_chromecasts(discovery_timeout=10)

            if chromecasts:
                cast = chromecasts[0]
                cast.wait()
                ip_address = cast.cast_info.host
                print(f"📺 Found Google TV '{cast.cast_info.friendly_name}' at:" f" {ip_address}")

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
        """Ensure we have ADB connection to TV"""
        # Use known IP address directly
        if not self.tv_ip:
            self.tv_ip = "192.168.50.221"  # Hardcoded known IP
            print(f"📺 Using known Google TV IP: {self.tv_ip}")

        try:
            # Connect ADB using known IP
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
        """Use Google TV universal search to find and start playing content (fire-and-forget)"""
        print(f"🎬 Starting search for: '{title}' (async)")

        # Fire-and-forget: start the search in background
        asyncio.create_task(self._search_and_play_async(title))

        # Return immediately to keep audio flowing
        return f"🎬 Starting search for '{title}' - this will take a few seconds"

    async def _search_and_play_async(self, title: str):
        """Actually perform the ADB search commands asynchronously"""
        try:
            print(f"🎬 [Background] Searching for: '{title}'")

            # Ensure we have TV connection first
            if not await asyncio.to_thread(self.ensure_tv_connection):
                print("❌ [Background] Could not connect to Google TV")
                return

            # Format title for ADB (replace spaces with %s)
            title_formatted = title.replace(" ", "%s")

            # Universal search sequence with proper waits
            commands = [
                (
                    ["adb", "shell", "input", "keyevent", "KEYCODE_SEARCH"],
                    "Open universal search",
                    3,
                ),
                (
                    ["adb", "shell", "input", "text", title_formatted],
                    "Type search query",
                    3,
                ),
                (
                    ["adb", "shell", "input", "keyevent", "KEYCODE_ENTER"],
                    "Submit search",
                    5,
                ),
                (
                    ["adb", "shell", "input", "keyevent", "KEYCODE_ENTER"],
                    "Select first result",
                    3,
                ),
            ]

            for cmd, description, wait_time in commands:
                print(f"🔧 [Background] {description}...")
                result = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, timeout=10)

                if result.returncode != 0:
                    print(
                        "⚠️ [Background] Command failed:"
                        f" {result.stderr.strip() if result.stderr else 'Unknown error'}"
                    )

                await asyncio.sleep(wait_time)  # Use async sleep

            print(f"✅ [Background] Search completed for '{title}'")

            # Auto-start watching mode after successful search
            await asyncio.sleep(10)  # Wait for content to start loading
            print("👁️ [Background] Auto-starting watching mode...")
            self.watching_mode = True

        except Exception as e:
            print(f"❌ [Background] Search error for '{title}': {e}")

    async def _send_media_key_async(self, keycode: str) -> bool:
        """Send a media key command to TV asynchronously"""
        try:
            # Ensure we have TV connection first
            if not await asyncio.to_thread(self.ensure_tv_connection):
                print("❌ Could not connect to Google TV for media control")
                return False

            # Send the media key command
            cmd = ["adb", "shell", "input", "keyevent", keycode]
            result = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                print(f"✅ Media key {keycode} sent successfully")
                return True
            else:
                print("⚠️ Media key failed:" f" {result.stderr.strip() if result.stderr else 'Unknown error'}")
                return False

        except Exception as e:
            print(f"❌ Media key error: {e}")
            return False

    async def search_user_history(self, query="", max_recent=10):
        """Search user's TV viewing history or get recent memories"""
        if not self.memory_client:
            return "Memory system not available"

        try:
            if query:
                # Use semantic search for specific queries
                memories = await asyncio.to_thread(
                    self.memory_client.search,
                    query=query,
                    user_id="tv_companion_user",
                    limit=5,
                )
                print(f"💭 Found {len(memories) if memories else 0} relevant memories")
            else:
                # Get recent memories when no query
                memories = await asyncio.to_thread(
                    self.memory_client.get_all,
                    filters={"user_id": "tv_companion_user"},
                    page_size=max_recent,
                    version="v2",
                )
                print(f"💭 Retrieved {len(memories) if memories else 0} recent memories")

            # Format memories chronologically
            if memories and isinstance(memories, list):
                history_items = []
                for m in memories:
                    if isinstance(m, dict) and m.get("memory"):
                        timestamp = "unknown"
                        if m.get("metadata"):
                            timestamp = m["metadata"].get("timestamp", "unknown")
                        elif m.get("created_at"):
                            timestamp = m["created_at"]

                        history_items.append(f"[{timestamp}] {m['memory']}")

                # Sort by timestamp if we have them
                if history_items:
                    history_items.sort()  # Assuming ISO format timestamps
                    return "\n".join(history_items)

            return "No user history found"

        except Exception as e:
            print(f"⚠️  User history search failed: {e}")
            return f"Failed to retrieve history: {str(e)}"

    async def listen_user_audio(self):
        """Capture audio from user microphone (like Wind Waker voice chat)"""
        try:
            self.pya = pyaudio.PyAudio()
            mic_info = self.find_pulse_device()
            print(f"🎤 Using user microphone: {mic_info['name']}")

            self.mic_stream = await asyncio.to_thread(
                self.pya.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=SEND_SAMPLE_RATE,
                input=True,
                input_device_index=mic_info["index"],
                frames_per_buffer=CHUNK_SIZE,
            )

            if __debug__:
                kwargs = {"exception_on_overflow": False}
            else:
                kwargs = {}

            while True:
                data = await asyncio.to_thread(self.mic_stream.read, CHUNK_SIZE, **kwargs)
                await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

        except Exception as e:
            print(f"❌ User audio capture error: {e}")
            raise

    async def transcribe_tv_audio(self):
        """Continuously transcribe TV audio and send to Gemini"""
        print("🎤 Starting TV audio transcription...")

        while True:
            try:
                print("🎤 Creating new audio stream...")
                async with TVAudioStream() as stream:
                    print("🎤 Audio stream created, starting transcription...")

                    # Run transcription in a separate thread to avoid blocking
                    await asyncio.to_thread(self._run_transcription_sync, stream)

            except Exception as e:
                print(f"❌ Transcription error: {e}")
                import traceback

                traceback.print_exc()
                await asyncio.sleep(2)  # Brief pause before restarting

    def _run_transcription_sync(self, stream):
        """Run transcription synchronously in a thread"""
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)

        print("🎤 Sending requests to Google Cloud Speech...")
        responses = self.speech_client.streaming_recognize(self.streaming_config, requests)

        print("🎤 Processing responses...")
        transcripts_received = 0

        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            # Only send final results to avoid spam
            if result.is_final and transcript.strip():
                transcripts_received += 1
                print(f"📝 Transcribed #{transcripts_received}: {transcript}")

                # Add to current scene buffer instead of sending immediately
                if self.current_scene is not None:
                    self.current_scene.add_transcript(transcript)
                    print(f"📝 Added to Scene {self.current_scene.scene_number}:" f" {transcript[:50]}...")
                else:
                    # No scene yet, create first scene
                    self.scene_counter += 1
                    self.current_scene = SceneBuffer(self.scene_counter)
                    self.current_scene.add_transcript(transcript)
                    print(f"📝 Started Scene {self.scene_counter} with transcript:" f" {transcript[:50]}...")

    async def send_realtime(self):
        """Send scene packages and user audio to Gemini Live API"""
        packages_sent = 0

        while True:
            msg = await self.out_queue.get()

            # Handle user microphone audio
            if isinstance(msg, dict) and msg.get("mime_type") == "audio/pcm":
                await self.session.send_realtime_input(audio=msg)
                continue

            # Handle scene packages
            if isinstance(msg, dict) and msg.get("type") == "scene_package":
                packages_sent += 1
                scene_num = msg.get("scene_number", "?")
                duration = msg.get("duration", "?")
                frames = msg.get("frames", [])

                print(f"📤 Sending Scene Package #{packages_sent} (Scene {scene_num}," f" {duration}) to Gemini")

                # Build Content parts list
                parts = []

                # Add scene text with automatic context injection
                if msg["transcript"].strip():
                    # Auto-search for relevant context based on dialogue
                    auto_context = await self.get_scene_context(msg["transcript"])

                    scene_text = f"""Scene {scene_num} ({duration}):

{msg['transcript']}"""

                    if auto_context:
                        scene_text += f"\n\n[Context from film knowledge]:\n{auto_context}"
                        print(f"🔍 Auto-injected context for Scene {scene_num}")

                    parts.append({"text": scene_text})
                    print(f"📝 Added dialogue for Scene {scene_num}")
                else:
                    print(f"🔇 No dialogue for Scene {scene_num}")

                # Add all frames as image parts
                for i, frame_entry in enumerate(frames):
                    frame_type = "initial" if frame_entry["is_initial"] else "periodic"
                    timestamp = frame_entry["timestamp"]

                    parts.append(
                        {
                            "inline_data": {
                                "mime_type": frame_entry["data"]["mime_type"],
                                "data": frame_entry["data"]["data"],
                            }
                        }
                    )
                    print(f"📸 Added {frame_type} frame #{i+1} for Scene" f" {scene_num} ({timestamp})")

                # Send as complete client content turn (text + images together)
                if parts:  # Only send if we have content
                    content = {"role": "user", "parts": parts}
                    await self.session.send_client_content(turns=content, turn_complete=True)
                    print(f"📤 Sent complete scene package: {len(parts)} parts (text +" " images together)")
                else:
                    print(f"⚠️ No content to send for Scene {scene_num}")

    async def receive_audio(self):
        """Receive Gemini's audio responses and handle tool calls"""
        while True:
            turn = self.session.receive()
            async for response in turn:
                # Audio data - queue immediately
                if data := response.data:
                    self.audio_in_queue.put_nowait(data)
                    continue

                # Text response
                if text := response.text:
                    print(f"🎬 TV Companion: {text}")
                    continue

                # Server content (for extracting user queries for memory storage)
                if response.server_content:
                    model_turn = response.server_content.model_turn
                    if model_turn and model_turn.parts:
                        for part in model_turn.parts:
                            # Extract user query for memory storage
                            if part.executable_code and "query=" in part.executable_code.code:
                                code = part.executable_code.code
                                query_start = code.find('query="') + 7
                                query_end = code.find('"', query_start)
                                if query_end > query_start:
                                    user_query = code[query_start:query_end]
                                    context = {
                                        "type": "user_intent",
                                        "query": user_query,
                                        "timestamp": datetime.now(),
                                    }
                                    self.conversation_context.append(context)

                                    # Store memory asynchronously
                                    if self.memory_client:
                                        asyncio.create_task(self._store_memory_async(context))

                # Tool calls
                if response.tool_call:
                    await self.handle_tool_call(response.tool_call)
                    continue

            # Handle interruptions by clearing audio queue
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

    async def handle_tool_call(self, tool_call):
        """Handle tool calls from Gemini"""
        function_responses = []

        for fc in tool_call.function_calls:
            print(f"\n🔧 Tool call: {fc.name}")
            print(f"   Args: {fc.args}")

            if fc.name == "search_film_context":
                # Disable in watching mode - send empty response
                if self.watching_mode:
                    print(f"🔇 search_film_context disabled in watching mode")
                    result = {}
                else:
                    query = fc.args.get("query", "")
                    print(f"📚 Searching film context for: {query}")
                    search_results = await self.search_film_context(query)

                    # Show what we're actually returning to Gemini
                    print(f"📊 Search results preview (first 200 chars):")
                    print(f"   {search_results[:200]}...")
                    print(f"📊 Total result length: {len(search_results)} characters")

                    result = {"query": query, "results": search_results}

            elif fc.name == "search_and_play_content":
                title = fc.args.get("title", "")
                print(f"🎬 TV control: searching and playing '{title}'")
                search_result = self.search_and_play_content(title)

                # Store what user requested to watch
                if self.memory_client and title.strip():
                    context = {
                        "type": "content_request",
                        "query": f"User requested to play: {title}",
                        "timestamp": datetime.now(),
                    }
                    asyncio.create_task(self._store_memory_async(context))

                result = {"title": title, "result": search_result}

            elif fc.name == "search_user_history":
                query = fc.args.get("query", "").strip()
                print("🔍 Searching user history:" f" {'recent activity' if not query else query}")
                history_results = await self.search_user_history(query)
                result = {
                    "query": query or "recent_activity",
                    "results": history_results,
                }

            elif fc.name == "start_watching_mode":
                print("👁️ Starting watching mode - will auto-comment on scenes")
                self.watching_mode = True
                result = {
                    "status": "watching_mode_started",
                    "message": "Now automatically commenting on scenes",
                }

            elif fc.name == "stop_watching_mode":
                print("👁️ Stopping watching mode - scenes will be stored for manual" " analysis")
                self.watching_mode = False
                result = {
                    "status": "watching_mode_stopped",
                    "message": "Automatic scene commentary disabled",
                }

            elif fc.name == "describe_current_scene":
                # Disable in watching mode - send empty response
                if self.watching_mode:
                    print(f"🔇 describe_current_scene disabled in watching mode")
                    result = {}
                else:
                    print("🔍 Analyzing current active scene...")
                    if self.current_scene is not None:
                        # Create scene package from current active scene
                        scene_package = self.current_scene.create_scene_package()
                        print("📤 Sending current scene for analysis:" f" {scene_package['summary']}")

                        try:
                            self.out_queue.put_nowait(scene_package)
                            result = {
                                "status": "scene_sent",
                                "message": f"Analyzing current {scene_package['summary']}",
                            }
                        except:
                            result = {
                                "status": "error",
                                "message": "Failed to send current scene for analysis",
                            }
                    else:
                        result = {
                            "status": "no_current_scene",
                            "message": "No scene currently active",
                        }

            elif fc.name == "pause_playback":
                print("⏸️ Pausing TV playback...")
                pause_result = await self._send_media_key_async("KEYCODE_MEDIA_PAUSE")
                result = {
                    "status": "pause_sent",
                    "message": ("Pause command sent to TV" if pause_result else "Failed to pause TV"),
                }

            elif fc.name == "resume_playback":
                print("▶️ Resuming TV playback...")
                play_result = await self._send_media_key_async("KEYCODE_MEDIA_PLAY")
                result = {
                    "status": "play_sent",
                    "message": ("Play command sent to TV" if play_result else "Failed to resume TV"),
                }

            else:
                result = {"error": f"Unknown function: {fc.name}"}

            # Add function response
            if result is not None:
                function_responses.append(types.FunctionResponse(id=fc.id, name=fc.name, response=result))

        # Send tool responses
        if function_responses:
            await self.session.send_tool_response(function_responses=function_responses)

    async def get_scene_context(self, transcript, similarity_threshold=0.7):
        """Automatically get relevant context for scene dialogue"""
        if not transcript.strip():
            return None

        try:
            # Search for context with a reasonable threshold
            context = await self.search_film_context(transcript, top_k=2)

            # Only return if we got useful results (basic length check)
            if context and len(context) > 100:
                print(f"🔍 Auto-context found for dialogue: '{transcript[:50]}...'")
                return context[:800]  # Limit context size to avoid overwhelming

            return None

        except Exception as e:
            print(f"🔍 Auto-context failed: {e}")
            return None

    async def play_audio(self):
        """Play Gemini's audio responses using pw-cat with pre-buffering"""
        # Wait for initial buffer
        initial_chunks = []
        for _ in range(3):  # Buffer 3 chunks before starting
            chunk = await self.audio_in_queue.get()
            initial_chunks.append(chunk)

        cmd = [
            "pw-cat",
            "--playback",
            "-",
            "--rate",
            str(RECEIVE_SAMPLE_RATE),
            "--channels",
            "1",
            "--format",
            "s16",
            "--raw",
        ]

        try:
            play_process = await asyncio.create_subprocess_exec(
                *cmd, stdin=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            print("✓ Audio playback started with pw-cat")

            # Play buffered chunks first
            for chunk in initial_chunks:
                play_process.stdin.write(chunk)
                await play_process.stdin.drain()

            # Continue normal playback
            while True:
                bytestream = await self.audio_in_queue.get()
                play_process.stdin.write(bytestream)
                await play_process.stdin.drain()

        except Exception as e:
            print(f"❌ pw-cat playback error: {e}")

    async def run(self):
        """Main TV companion loop with transcription and scene detection"""
        print("📺 Starting HDMI TV Companion with Transcription & Scene Detection...")
        print("🎧 Make sure to use headphones to prevent audio feedback!")
        print("💡 Type 'q' to quit")

        try:
            async with (
                client.aio.live.connect(model=MODEL, config=CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=20)  # Larger buffer to prevent blocking

                # Start all tasks
                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_user_audio())  # User microphone input
                tg.create_task(self.transcribe_tv_audio())
                tg.create_task(self.run_scene_detection())  # PySceneDetect
                tg.create_task(self.monitor_scene_duration())  # Scene duration monitor
                tg.create_task(self.capture_periodic_screenshots())  # Periodic screenshots
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            print("👋 TV Companion stopped")
        except Exception as e:
            traceback.print_exception(e)
        finally:
            # Clean up audio resources
            if self.mic_stream:
                self.mic_stream.close()
            if self.pya:
                self.pya.terminate()


if __name__ == "__main__":
    companion = HDMITVCompanionWithTranscription()
    asyncio.run(companion.run())
