# TV Companion Development Notes

## Project Overview
Building an LLM-powered TV companion that can watch and comment on movies/shows, similar to the Wind Waker companion but for video content.

## Audio Capture Breakthrough

### The Problem
Initial attempts to capture Chrome audio ran into several issues:
- Using speaker monitor captured ALL system audio (feedback loop with Gemini)
- `pipewire_python` library was outdated (`--list-targets` option doesn't exist)
- FIFO approach failed because `pw-cat` expects audio files, not raw streams

### The Solution: stdout Streaming
**SUCCESS**: Direct stdout streaming with raw PCM data works perfectly!

```bash
pw-cat --record - --target "Google Chrome" --rate 48000 --channels 2 --format f32 --raw
```

Key insights:
- Use `-` for stdout instead of filename
- Add `--raw` flag for raw PCM (no WAV headers)
- Target Chrome by node name: `--target "Google Chrome"`
- Read from `subprocess.PIPE` for streaming data
- Consistent 4800-byte chunks every 0.1 seconds

## Video Capture Challenges

### Chrome Window Capture Issues
Chrome video capture has several frustrating limitations:

**Root causes:**
- **Hardware acceleration**: Chrome uses GPU rendering for video, and when not active, the GPU may not render to the window buffer that screen capture can access
- **Browser optimization**: Chrome pauses/reduces rendering for background tabs to save resources
- **DRM/Copy protection**: Some video content actively prevents background capture
- **Window compositor**: System may not update non-visible window contents

**Solutions for Chrome:**
```python
# Option 1: Force foreground (simplest)
import pyautogui
pyautogui.getWindowsWithTitle("Chrome")[0].activate()
```

```bash
# Option 2: Chrome flags (disable optimizations)
google-chrome \
  --disable-gpu-sandbox \
  --disable-web-security \
  --disable-features=VizDisplayCompositor \
  --force-color-profile=srgb
```

```bash
# Option 3: Virtual display
Xvfb :99 -screen 0 1920x1080x24 &
DISPLAY=:99 google-chrome
```

### HDMI Capture Advantages
HDMI capture hardware solves these issues completely:

✅ **Signal-level capture**: Captures the actual video signal, not window buffers
✅ **Always active**: The display is receiving the signal regardless of focus
✅ **No browser optimizations**: Bypasses all Chrome-specific rendering issues
✅ **Hardware-level**: No software copy protection at window level
✅ **Consistent quality**: What you see is what you capture

**Development Strategy:**
- **Chrome development**: Keep window in foreground, use YouTube for testing
- **HDMI demos**: Professional quality, works with any content
- **Fallback plan**: Always have both options ready

### HDMI Capture Success! 🎉

**BREAKTHROUGH**: HDMI capture card successfully bypasses HDCP protection!

![HDMI Capture Working](capture.png)

**What's working:**
- **Protected content streaming**: Netflix, Disney+, and other HDCP-protected content displays perfectly
- **No HDCP strippers needed**: The MACROSILICON USB3.0 Video capture card handles this automatically
- **High quality capture**: 1920x1080 at 60fps with excellent image quality

**Successful Implementation:**

**Video Capture:**
```bash
# View HDMI capture stream with ffplay
ffplay /dev/video4

# With specific resolution
ffplay -f v4l2 -video_size 1920x1080 -framerate 30 /dev/video4
```

**Audio Capture:**
```bash
# HDMI audio source identified
pactl list sources short
# Result: alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo

# Capture HDMI audio with pw-cat
pw-cat --record - --target "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo" \
       --rate 48000 --channels 2 --format s16le --raw
```

**Hardware Setup:**
1. Chromecast → HDMI cable → HDMI capture card → USB 3.0 → Laptop
2. **Device Detection:**
   - Video: `/dev/video4` (USB3.0 Video capture)
   - Audio: Source ID `6655` (MACROSILICON_USB3.0_Video analog-stereo)
3. **Format Support:** YUYV and MJPG formats, up to 2560x1600 resolution

**Key Success Factors:**
- ✅ **Hardware-level HDCP bypass**: No software workarounds needed
- ✅ **USB 3.0 bandwidth**: Sufficient for high-quality video streaming
- ✅ **PipeWire compatibility**: Audio capture works seamlessly
- ✅ **Multiple formats**: Both compressed (MJPG) and uncompressed (YUYV) available

This makes the HDMI approach the clear winner for professional demos with any streaming content!

## Audio Configuration for Gemini Live API

### Gemini Requirements vs HDMI Native Format
**Gemini Live API specs** (from `Get_started_LiveAPI.py`):
```python
FORMAT = pyaudio.paInt16  # s16 format
CHANNELS = 1              # Mono
SEND_SAMPLE_RATE = 16000  # 16kHz
```

**HDMI Capture native format**:
- **48kHz stereo s16** → needs conversion to **16kHz mono s16**

### Downmixing Test Results 🎵
**BREAKTHROUGH**: Confirmed pw-cat properly downmixes stereo to mono!

**Test method**: Simultaneous capture of stereo vs mono from same HDMI source
- **File size ratio**: 1.99:1 (stereo ~2x mono size) ✅
- **Audio quality test**: Aggressive stereo panning → static in mono output
- **Conclusion**: pw-cat uses proper downmixing `(left + right) / 2`, not channel dropping

This means pw-cat safely converts stereo TV audio to mono without losing content from either channel.

### Final Working Configuration
**Perfect stdout streaming** with Gemini-compatible format:

```bash
pw-cat --record - \
       --target "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo" \
       --rate 16000 --channels 1 --format s16 --raw
```

**Performance results**:
- ✅ **Consistent streaming**: 1600 bytes per 0.1-second chunk
- ✅ **Total throughput**: 16,000 bytes/second (matches 16kHz mono s16)
- ✅ **Format compatibility**: Direct feed to Gemini Live API
- ✅ **Audio quality**: Proper stereo→mono downmixing preserves all content

**Key technical specs**:
- **Resampling**: 48kHz → 16kHz (3:1 downsampling)
- **Channel mixing**: Stereo → Mono (proper downmix)
- **Format**: s16 (16-bit signed integer, matches pyaudio.paInt16)
- **Streaming**: Raw PCM via stdout (no file headers)
- **Latency**: Real-time processing, ~100ms total pipeline delay

This configuration provides broadcast-quality audio capture perfectly formatted for Gemini Live API consumption!

### PyAudio vs pw-cat Conclusion 🔧

**We tested direct PyAudio capture** to avoid subprocess overhead, but hit a critical limitation:

**PyAudio Error:**
```
Expression 'PaAlsaStream_Configure...' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 2842
❌ PyAudio error: [Errno -9997] Invalid sample rate
```

**Root cause:** PyAudio/ALSA cannot automatically convert 48kHz native → 16kHz Gemini format.

**PyAudio approach would require:**
- Manual capture at native 48kHz stereo
- Python-based downsampling (scipy.signal.resample - CPU intensive)
- Manual stereo→mono downmixing
- Buffer management for real-time conversion
- Potential latency and quality issues

**pw-cat approach provides:**
- ✅ **Professional resampling**: Optimized C algorithms with anti-aliasing
- ✅ **Real-time performance**: Designed for broadcast audio streaming
- ✅ **Quality control**: Proper downmixing without phase cancellation
- ✅ **Proven results**: 16,000 bytes/second perfect output
- ✅ **Broadcast standard**: What audio engineers use for format conversion

**Verdict: pw-cat stdout streaming is the professional solution.** 

Attempting to reimplement professional audio processing in Python would be slower, more complex, and lower quality than using the industry-standard tool.

![Complete Setup](magic.jpg)

## Content Source Strategies

### Chrome/Local Capture
**Pros:**
- Perfect for development and testing
- No HDCP copy protection issues
- Works anywhere with laptop
- Full browser control via Playwright/DevTools
- Reliable and consistent environment

**Cons:**
- Limited to browser content
- Less impressive for demos
- Requires local setup

**Actuation Methods:**
- Playwright/Selenium for browser automation
- Keyboard shortcuts (Space for pause, arrows for seek)
- Chrome DevTools Protocol for low-level control
- Direct DOM manipulation

### HDMI Capture (Hardware)
**Pros:**
- Works with any HDMI source (Netflix, cable TV, streaming boxes)
- More impressive demo factor
- Perfect for meeting rooms with existing displays
- Can capture "real" TV content

**Cons:**
- HDCP compliance unknown until tested
- Requires capture hardware setup
- More complex for development
- Limited actuation options

**Actuation Methods:**
- ADB commands for Android TV/Chromecast: `adb shell input keyevent KEYCODE_MEDIA_PAUSE`
- IR blaster for universal remote control
- HDMI CEC commands (if supported)
- Cast SDK APIs (limited to compatible apps)

## Demo Strategy

### Development Environment
Use Chrome capture for consistent, reliable development:
- YouTube videos for testing
- Controllable playback
- No HDCP issues
- Easy to set up anywhere

### Meeting Room Demos
HDMI capture from room displays:
- More impressive "wow factor"
- Real streaming service content (if HDCP allows)
- Fallback to Chrome if HDCP blocks content
- YouTube presentations always work

### Gemini Meetups/Workshops
Hybrid approach:
- Primary: HDMI capture from meeting room setup
- Fallback: Chrome capture on laptop
- Demo content: YouTube, local videos, or meeting presentations

## Technical Architecture

### Unified Controller Interface
```python
class TVController:
    def __init__(self, source_type="chrome"):
        self.source = source_type

    def pause(self):
        if self.source == "chrome":
            self.playwright_page.keyboard.press("Space")
        elif self.source == "hdmi":
            subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_MEDIA_PAUSE"])

    def get_audio_stream(self):
        if self.source == "chrome":
            return self.chrome_audio_stream()
        elif self.source == "hdmi":
            return self.hdmi_audio_stream()
```

### Audio Pipeline
1. **Chrome**: `pw-cat` stdout streaming (working!)
2. **HDMI**: Capture device audio input (TODO)
3. **Processing**: Raw PCM → Gemini Live API
4. **Output**: Route Gemini to headphones (avoid feedback)

### Video Pipeline
1. **Chrome**: Screen capture via `mss` or browser APIs
2. **HDMI**: Hardware capture device
3. **Processing**: Screenshots → base64 → Gemini Live API

## Multimodal Streaming Architecture

### The Four Streams Problem
We have four distinct streams to manage:
- **TV's audio stream**: Movie/show audio content
- **TV's video stream**: Visual content frames
- **User's audio stream**: User speaking to Gemini
- **Gemini's audio stream**: AI responses (output only)

### Streaming Strategy Options

**Option 1: Dual Audio Streams to Gemini Live**
Push both TV audio + User audio directly
- ✅ Gemini gets full audio context (music, sound effects, tone)
- ✅ No transcription latency
- ❌ Complex audio mixing/synchronization
- ❌ Gemini Live API may not handle dual audio streams well
- ❌ High bandwidth

**Option 2: User Audio + TV Transcription + Video (Recommended)**
User audio live + TV audio → Whisper → text + video frames
- ✅ Clean separation of concerns
- ✅ Reduced bandwidth
- ✅ Text easier for Gemini to process contextually
- ✅ No audio mixing complexity
- ❌ Loses audio nuance (music, sound effects)
- ❌ Transcription latency (~100-500ms)

**Option 3: Triple Stream**
All three: TV audio + User audio + TV transcription
- ✅ Maximum information, redundancy
- ❌ Most complex architecture
- ❌ Highest bandwidth
- ❌ Potential confusion from redundant info

### Recommended Implementation

**Core streaming pipeline:**
```python
# Primary streams to Gemini Live API
user_audio → Gemini Live API (real-time)
tv_audio → local Whisper → text → Gemini Live API
video_frames → Gemini Live API (every 1-2 seconds)

# Output
gemini_audio → headphones (avoid feedback)
```

**Enhancements:**
- **Audio event detection**: Sample TV audio for important moments (applause, music swells, explosions)
- **Smart transcription**: Include speaker detection, emotional tone markers in Whisper output
- **Context windows**: Send TV transcription in rolling 30-second windows
- **Selective processing**: Only transcribe when TV audio changes significantly

This approach provides conversational fluidity with the user while giving Gemini rich TV context without the complexity of dual audio streams.

## Next Steps

### Immediate (Chrome Version)
- [ ] Integrate stdout audio streaming with TV companion
- [ ] Add screen capture from Chrome tab
- [ ] Implement basic Gemini Live API integration
- [ ] Test with YouTube content

### Hardware Integration
- [ ] Test HDMI capture device
- [ ] Verify HDCP compliance with various sources
- [ ] Implement hardware audio/video capture
- [ ] Add unified source switching

### Actuation Layer
- [ ] Chrome automation with Playwright
- [ ] ADB command integration for Android TV
- [ ] Test CEC commands if available
- [ ] IR blaster research for universal control

## TV Companion Implementation Success! 🎬

### Working Solution Architecture
**BREAKTHROUGH**: Successfully combined HDMI audio/video capture with Gemini Live API!

**Final working pipeline:**
```python
# Audio: pw-cat stdout streaming (16kHz mono s16 for Gemini)
pw-cat --record - --target "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo" \
       --rate 16000 --channels 1 --format s16 --raw

# Video: OpenCV capture with PIL processing
cv2.VideoCapture('/dev/video4') → PIL.Image.thumbnail([1024, 1024]) → base64

# Streaming: Gemini Live API
session.send_realtime_input(audio=audio_data)  # Continuous audio
session.send_realtime_input(media=image_data)  # Periodic frames
```

**Key technical wins:**
- ✅ **pw-cat audio conversion**: Perfect 48kHz stereo → 16kHz mono downsampling
- ✅ **Real-time video processing**: OpenCV → PIL → base64 pipeline
- ✅ **Gemini Live API integration**: Proper use of `send_realtime_input()`
- ✅ **HDMI capture success**: Bypasses HDCP, works with protected content
- ✅ **No PyAudio complexity**: pw-cat handles all audio format conversion

### Gemini Live API Streaming Challenges

**The "Restart Phenomenon"** 🔄

**Observed behavior**: Gemini Live model starts commentary, then cuts itself off mid-sentence and restarts when receiving new information.

**Root cause analysis:**
- **Information overload**: 1fps video + continuous audio overwhelms the model
- **Context switching**: New frames interrupt ongoing speech generation
- **Competing priorities**: Model can't decide between completing thoughts vs. reacting to new input
- **Response latency**: By the time model processes frame N, frames N+1, N+2 have already arrived

**Mitigation attempts:**
1. **1 second frames** → Model commented on everything, frequent restarts
2. **5 second frames** → Some improvement, still fragmented responses  
3. **10 second frames** → ✅ Significantly better coherence, more selective commentary

**Current status**: 10-second frame intervals provide reasonable balance, but fundamental challenge remains.

### Future Architecture Solutions

**Hypothesis 1: Content-Aware Frame Sampling**
Instead of time-based frames, send frames on content changes:
```python
# Detect scene changes using computer vision
if scene_change_detected(current_frame, previous_frame):
    await session.send_realtime_input(media=current_frame)
```

**Hypothesis 2: Transcription-First Approach**
Audio → local transcription → text events → selective frame triggers:
```python
# TV audio pipeline
tv_audio → Whisper → scene_transcript → important_moment_detection → frame_capture
```

**Hypothesis 3: Separate Vision Processing**
Use dedicated vision model for scene analysis, report via tools:
```python
# Similar to Wind Waker approach
def analyze_scene():
    """Tool function for detailed scene analysis when requested"""
    return vision_model.describe(current_frame)
```

**Hypothesis 4: Context Buffering**
Maintain rolling window of recent context, pause input during responses:
```python
# Buffer recent frames/audio, pause streaming during Gemini speech
context_buffer = CircularBuffer(last_30_seconds)
if gemini.is_speaking():
    pause_input_stream()
```

**Recommended next steps:**
1. Implement scene change detection for smarter frame sampling
2. Add transcription pipeline for audio context
3. Test separate vision model approach for detailed analysis
4. Experiment with input pausing during model responses

## Scene-Based Commentary Architecture Success! 🎬

### The Context Association Problem
**Initial Issue**: Gemini couldn't connect dialogue with visuals when sent separately via `send_realtime_input()`.

**Symptoms observed:**
```
Gemini: "Wow, looks like they're having an intense dinner scene..."
Gemini: "I wonder what they're talking about?"
```

Despite receiving both dialogue transcript and scene images, the model treated them as separate, unrelated inputs rather than cohesive scene context.

### Scene Buffering Solution
**BREAKTHROUGH**: Implemented complete scene packaging that groups visual and audio content together.

**Architecture:**
```python
class SceneBuffer:
    def __init__(self, scene_number: int):
        self.frames = []          # Multiple screenshots per scene
        self.transcripts = []     # Dialogue with timestamps
        self.start_time = time.time()
    
    def create_scene_package(self) -> dict:
        return {
            "scene_number": self.scene_number,
            "duration": f"{duration:.1f}s", 
            "transcript": "\n".join(self.transcripts),
            "frames": self.frames
        }
```

**Key improvements:**
- ✅ **Complete scene context**: All dialogue + multiple visual snapshots packaged together
- ✅ **Duration tracking**: Each scene knows how long it lasted  
- ✅ **Timestamp correlation**: Dialogue and images correlated by scene timeline
- ✅ **Fallback timeout**: Long scenes (>3min) automatically finalized
- ✅ **Rich visual context**: Initial scene frame + periodic screenshots every 30s

### Scene Detection Optimization Journey

#### Adaptive vs Histogram Detector Research 📊
**AdaptiveDetector Failure**: Despite multiple sensitivity attempts, kept timing out:
```python
# All of these were too insensitive for TV content:
AdaptiveDetector(adaptive_threshold=3.0)  # Default - mostly 3min timeouts
AdaptiveDetector(adaptive_threshold=1.2)  # Still too conservative  
AdaptiveDetector(adaptive_threshold=0.8)  # Better but still insufficient
```

**Research Discovery**: Found academic paper ([arXiv:2506.00667](https://arxiv.org/pdf/2506.00667)) explaining detector selection by content type:

> **Adaptive Strategy**: For videos under 30 minutes, adaptive thresholding detects frame-to-frame changes via color histograms. These types of content typically exhibit abrupt transitions, making them ideal for change-based detection.

> **Content Strategy**: Long-form narrative content (2–3 hours) is segmented using content-based methods for sustained differences in visual appearance.

**Key insight**: TV content has "abrupt transitions" (quick cuts, scene changes, commercials) making **HistogramDetector** the optimal choice, not AdaptiveDetector.

#### HistogramDetector Success ✅
**Perfect fit for TV content:**
- ✅ **Fast cuts detection**: Excellent at catching shot changes between scenes
- ✅ **Lighting transitions**: Detects day/night, indoor/outdoor changes  
- ✅ **Mixed content handling**: Works well with shows, commercials, news
- ✅ **Reasonable sensitivity**: Some overtriggering but much better scene boundaries

**Result**: Natural scene detection at ~1-2 minute intervals instead of 3-minute timeouts.

### Video Capture Architecture Challenges

#### Device Conflict Resolution 🔧
**Problem**: Scene detection and periodic screenshots both trying to open `/dev/video4` simultaneously:
```python
# This failed - device busy error
scene_detection: cv2.VideoCapture(HDMI_VIDEO_DEVICE)  
periodic_shots:   cv2.VideoCapture(HDMI_VIDEO_DEVICE)  # ❌ Device busy
```

**Attempted Solutions:**
1. **Shared frame approach**: Store frames from scene detection for reuse
   - ❌ Introduced bugs with `None` frames
   - ❌ Complex synchronization issues

2. **Separate captures**: Let both open device independently  
   - ❌ Second capture failed silently
   - ❌ No error messages, just 0 frames captured

**Final Solution**: Single shared video capture device:
```python
# Elegant solution - one device, shared access
self.shared_cap = cv2.VideoCapture(HDMI_VIDEO_DEVICE)

# Scene detection uses it via VideoCaptureAdapter
video_adapter = VideoCaptureAdapter(self.shared_cap)

# Periodic capture uses same device
ret, frame = self.shared_cap.read()
```

#### Periodic Screenshot Logic Simplification
**Original overcomplicated logic**:
```python
# Old: Complex duration checking, sleep-first approach
await asyncio.sleep(30)  # Sleep first - misses scene beginnings!
if scene.duration > 30:  # Skip short scenes - loses context!
    capture_frame()
```

**Simplified approach**:
```python
# New: Capture-first, unconditional approach  
while True:
    if self.current_scene:
        capture_frame()  # Capture immediately - get scene beginnings!
    await asyncio.sleep(30)  # Then sleep
```

**Benefits:**
- ✅ **Capture scene beginnings**: No initial sleep delay
- ✅ **Support short scenes**: Even 10-second scenes get visual context
- ✅ **Simpler logic**: No complex duration calculations

### Gemini Live API Context Association

#### send_realtime_input() Limitation Discovery
**The problem**: Separate API calls created unrelated inputs:
```python
# This approach failed - Gemini saw these as separate events
await session.send_realtime_input(text=scene_dialogue)      # Event 1
await session.send_realtime_input(media=scene_frame_1)      # Event 2  
await session.send_realtime_input(media=scene_frame_2)      # Event 3
```

Result: Gemini processed each input independently, couldn't connect dialogue with visuals.

#### activity_start/activity_end Attempt 
**Hypothesis**: Group inputs with activity markers:
```python
await session.send_realtime_input(activity_start=types.ActivityStart())
await session.send_realtime_input(text=scene_dialogue)
await session.send_realtime_input(media=scene_frames)  
await session.send_realtime_input(activity_end=types.ActivityEnd())
```

**Failure**: WebSocket error revealed incompatibility:
```
ConnectionClosedError: received 1007 (invalid frame payload data) 
Explicit activity control is not supported when automatic activity detection is enabled.
```

**Learning**: Gemini Live has automatic activity detection - manual control conflicts with VAD (Voice Activity Detection).

#### send_client_content() Success! 🎉
**BREAKTHROUGH**: Discovered proper API for structured content:
```python
# This approach works - guaranteed content association  
parts = []
parts.append({"text": scene_dialogue})           # Add dialogue
parts.append({"inline_data": frame_1_data})      # Add frame 1  
parts.append({"inline_data": frame_2_data})      # Add frame 2

content = {"role": "user", "parts": parts}
await session.send_client_content(turns=content, turn_complete=True)
```

**Key advantages:**
- ✅ **Atomic content delivery**: All parts sent as single cohesive turn
- ✅ **Guaranteed association**: Model sees text + images together  
- ✅ **Turn completion**: `turn_complete=True` signals complete scene package
- ✅ **Structured format**: Proper Content object with multiple parts

**Result**: Gemini now receives complete scene packages like:
```json
{
  "role": "user", 
  "parts": [
    {"text": "Scene 3 (45.2s): [00:02.1] Character A: 'We need to find the treasure'"},
    {"inline_data": {"mime_type": "image/jpeg", "data": "...initial_frame..."}},
    {"inline_data": {"mime_type": "image/jpeg", "data": "...periodic_frame_1..."}},
    {"inline_data": {"mime_type": "image/jpeg", "data": "...periodic_frame_2..."}}
  ]
}
```

### Current Architecture Success Metrics

**Scene Detection Performance:**
- 📊 **Scene boundaries**: 1-2 minute natural intervals (vs 3-minute timeouts)
- 📊 **Visual context**: 2-5 frames per scene (initial + periodic)
- 📊 **Audio context**: Complete dialogue transcription per scene

**API Integration Results:**  
- ✅ **Context association**: Gemini connects dialogue with visuals
- ✅ **Commentary quality**: More coherent, contextual responses
- ✅ **Reduced fragmentation**: Complete scene packages vs scattered inputs

**Technical Reliability:**
- ✅ **Shared video capture**: No device conflicts
- ✅ **Robust scene buffering**: Handles both scene changes and timeouts  
- ✅ **Simplified periodic capture**: No complex timing logic

### Architecture Evolution Lessons

1. **Scene Detection**: Academic research crucial - detector choice depends on content type
2. **Device Management**: Shared resources better than separate instances for video capture
3. **API Design**: `send_client_content()` with structured parts > separate `send_realtime_input()` calls
4. **Context Association**: Modern LLMs need explicit content structure, not just temporal proximity
5. **Simplification**: Remove complex logic when simple approaches work better
6. **Real-time Constraints**: Video device conflicts are silent failures - always test end-to-end

The scene-based architecture now provides Gemini with rich, coherent context enabling intelligent TV commentary that connects visual and audio elements naturally!

## TV Control and Actuation Layer Development 📺

### Chromecast Discovery Integration Success
**Challenge**: Need programmatic TV control for demos - load content and seek to specific timestamps.

**Discovery Breakthrough**: `pychromecast` works perfectly for device discovery and basic control:
```bash
# Discovered Google TV Streamer automatically
🔍 Starting Chromecast discovery...
Found: Cave TV
📺 Discovered 1 device(s):
  • Cave TV at 192.168.50.221:8009
    Model: Google TV Streamer, Type: None
    UUID: 9bcb366d-9e87-31be-ff60-49bd80f60463
```

**Key Insight**: Chromecast discovery reveals the IP address needed for ADB commands - same physical device, different protocols.

### ADB Command Exploration Journey

#### Initial Complex Approaches (Failed)
**Problem**: Need to search for and play "The Big Sleep" on Google TV programmatically.

**Attempted Solutions**:
1. **Android Intent Actions**: 
   ```bash
   adb shell am start -a android.intent.action.ASSIST -e query "The Big Sleep 1946"
   adb shell am start -a android.intent.action.WEB_SEARCH -e query "The Big Sleep 1946 movie"
   ```
   **Result**: ❌ Zero effect - no visible response on TV

2. **Direct App Launching**:
   ```bash
   # Found Amazon Prime Video activity
   adb shell dumpsys package com.amazon.amazonvideo.livingroom | grep -A 1 MAIN
   adb shell am start -n com.amazon.amazonvideo.livingroom/com.amazon.ignition.IgnitionActivity
   ```
   **Result**: ✅ Launched Prime Video, but no search capability found

3. **Complex DPAD Navigation**:
   ```bash
   # Navigate to search manually
   adb shell input keyevent KEYCODE_DPAD_UP      # Go to top menu
   adb shell input keyevent KEYCODE_DPAD_RIGHT   # Navigate to search  
   adb shell input keyevent KEYCODE_ENTER        # Select search
   adb shell input text "The+Big+Sleep"
   ```
   **Result**: ⚠️ Theoretically possible but complex, app-specific, fragile

#### Universal Search Breakthrough! 🎉
**DISCOVERY**: Google TV has built-in universal search accessible via `KEYCODE_SEARCH`!

**The Magic Sequence**:
```bash
adb shell input keyevent KEYCODE_SEARCH     # Open universal search overlay
adb shell input text "The%sBig%sSleep"      # Type query (% = space)
adb shell input keyevent KEYCODE_ENTER      # Search
adb shell input keyevent KEYCODE_ENTER      # Select first result
```

**Why This Works**:
- ✅ **Universal**: Works across all streaming services (Prime, Netflix, Google Play, etc.)
- ✅ **Simple**: 4 commands vs complex menu navigation sequences
- ✅ **Reliable**: Google TV's built-in search handles content discovery
- ✅ **Content-agnostic**: Don't need to know which service has the content

**Test Results**: Successfully launched "The Big Sleep" from Google Play Movies with this approach!

### TV Companion Integration Architecture

#### Auto-Discovery with Fallback
**Hybrid Approach**: Use Chromecast discovery to find TV IP, then ADB for control:

```python
def discover_tv_ip(self):
    """Use Chromecast discovery to find Google TV IP address"""
    chromecasts, browser = pychromecast.get_listed_chromecasts(discovery_timeout=10)
    if chromecasts:
        return chromecasts[0].cast_info.host  # Extract IP for ADB
    return None

def ensure_tv_connection(self):
    if not self.tv_ip:
        self.tv_ip = self.discover_tv_ip() or "192.168.50.221"  # Fallback hardcoded
    subprocess.run(["adb", "connect", f"{self.tv_ip}:5555"])
```

**Benefits**:
- ✅ **Auto-discovery**: Works on any network without configuration
- ✅ **Fallback robustness**: Hardcoded IP for when discovery fails
- ✅ **Demo reliability**: Can quickly switch to manual IP for presentations

#### Tool Integration
**Added `search_and_play_content` tool** for Gemini:
```python
{
    "name": "search_and_play_content",
    "description": "Search for and start playing a movie or show on the TV using Google TV's universal search",
    "parameters": {
        "properties": {
            "title": {"type": "string", "description": "Movie or show title to search for"}
        }
    }
}
```

**Usage**: User can say *"Play The Big Sleep"* and Gemini executes the universal search sequence.

### Critical Performance Issue: ADB Blocking

#### The Audio Pipeline Freeze Problem 🚫
**Symptom**: When Gemini called `search_and_play_content`, entire system froze for ~14 seconds:
- Google Cloud Speech API timeout (no audio data during freeze)
- Gemini couldn't speak (audio pipeline blocked)
- Scene detection paused
- User interaction impossible

**Root Cause**: Synchronous ADB commands with `time.sleep()` waits:
```python
# This blocked the entire event loop for 14 seconds total
time.sleep(3)  # Wait for search overlay
time.sleep(3)  # Wait for text input
time.sleep(5)  # Wait for search results  
time.sleep(3)  # Wait for selection
```

#### Fire-and-Forget Solution ✅
**Architecture Change**: Tool returns immediately, ADB runs in background:

```python
def search_and_play_content(self, title: str):
    """Return immediately to keep audio flowing"""
    asyncio.create_task(self._search_and_play_async(title))
    return f"🎬 Starting search for '{title}' - this will take a few seconds"

async def _search_and_play_async(self, title: str):
    """Actually perform ADB commands asynchronously"""
    for cmd, description, wait_time in commands:
        result = await asyncio.to_thread(subprocess.run, cmd, ...)
        await asyncio.sleep(wait_time)  # Use async sleep
```

**Results**:
- ✅ **Tool response**: <1ms (instant Gemini acknowledgment)
- ✅ **Audio continuity**: No pipeline interruption
- ✅ **Background execution**: ADB commands complete ~14 seconds later
- ✅ **User experience**: Can continue talking during search

## Voice Interaction Enhancement 🎤

### User Microphone Integration
**Gap Identified**: TV companion only accepted text input, but Wind Waker voice chat had full voice interaction.

**Solution**: Added user microphone stream identical to Wind Waker implementation:
```python
# Added to TV companion
self.pya = None           # PyAudio instance  
self.mic_stream = None    # User microphone stream

async def listen_user_audio(self):
    """Capture audio from user microphone (like Wind Waker voice chat)"""
    # Identical implementation to waker/voice_chat.py
    self.mic_stream = await asyncio.to_thread(self.pya.open, ...)
    while True:
        data = await asyncio.to_thread(self.mic_stream.read, CHUNK_SIZE)
        await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})
```

**Audio Routing Architecture**:
1. **User microphone** → Gemini Live API (for questions/commands)
2. **TV audio (HDMI)** → Google Cloud Speech → transcription → scene packages  
3. **Gemini responses** → speakers (with feedback risk - TBD)

**Capabilities Unlocked**:
- 🎤 **Voice commands**: *"Play The Big Sleep"*, *"Start watching mode"*
- 🎤 **Live questions**: *"Who is that actor?"*, *"What's happening in this scene?"*
- 🎤 **Natural interaction**: Full conversational flow while watching

## Episodic Memory Integration 🧠

### Mem0 Client Addition
**Goal**: Remember user's viewing history and preferences, similar to Wind Waker's memory system.

**Implementation**: Added mem0 client with TV-specific project ID:
```python
self.memory_client = MemoryClient(
    api_key=os.getenv("MEM0_API_KEY"),
    org_id="org_lOJM2vCRxHhS7myVb0vvaaY1rUauhqkKbg7Dg7KZ",
    project_id="proj_I6CXbVIrt0AFlWE0MU3TyKxkkYJam2bHm8nUxgEu",  # TV companion specific
)
```

**Memory Storage Strategy**: Focus on content requests rather than all interactions:
```python
# Store only when user requests content to watch
if fc.name == "search_and_play_content":
    title = fc.args.get("title", "")
    context = {
        "type": "content_request",
        "query": f"User requested to play: {title}",
        "timestamp": datetime.now(),
    }
    asyncio.create_task(self._store_memory_async(context))
```

**Search Integration**: Added `search_user_history` tool:
```python
{
    "name": "search_user_history", 
    "description": "Search the user's personal viewing history and past questions"
}
```

**Benefits**:
- 🧠 **Viewing continuity**: *"What was the last movie I watched?"*
- 🧠 **Preference learning**: Remember favorite genres, actors, directors
- 🧠 **Context awareness**: *"Continue from where we left off"*

## Watching Mode Implementation 👁️

### The Manual vs Automatic Commentary Problem
**Challenge**: Should Gemini automatically comment on every scene, or wait for user requests?

**User Request**: Simple toggle that doesn't change existing mechanics - just controls whether scene packages are auto-sent to Gemini.

### Elegant Toggle Solution
**Architecture**: Keep all scene detection, transcription, and screenshot mechanics unchanged:

```python
def __init__(self):
    self.watching_mode = False  # Default: don't auto-send scenes
    self.recent_scenes = []     # Store recent scenes for manual analysis

def _finalize_current_scene(self):
    """Send or store scene package based on watching mode"""
    scene_package = self.current_scene.create_scene_package()
    
    if self.watching_mode:
        # Auto-send to Gemini for commentary
        self.out_queue.put_nowait(scene_package)
        print(f"📤 Auto-sent scene package (watching mode)")
    else:
        # Store for manual analysis  
        self.recent_scenes.append(scene_package)
        if len(self.recent_scenes) > 5:  # Keep last 5 scenes
            self.recent_scenes.pop(0)
        print(f"📦 Stored scene package (non-watching mode)")
```

**Control Tools**:
```python
# Voice commands for mode control
"start_watching_mode"     # Begin auto-commentary
"stop_watching_mode"      # Return to manual analysis
"describe_current_scene"  # Analyze most recent stored scene
```

**Usage Patterns**:
- **Default (non-watching)**: Scenes stored locally, user asks *"What just happened?"*
- **Watching mode**: Continuous commentary as scenes change
- **On-demand**: *"Describe the current scene"* analyzes most recent scene

### Auto-Activation After Content Search
**Demo Enhancement**: Automatically start watching mode after successful content search:

```python
async def _search_and_play_async(self, title: str):
    # ... execute search commands ...
    print(f"✅ [Background] Search completed for '{title}'")
    
    # Auto-start watching mode after content loads
    await asyncio.sleep(10)  # Wait for content to start playing
    print("👁️ [Background] Auto-starting watching mode...")
    self.watching_mode = True
```

**Demo Flow**:
1. User: *"Play The Big Sleep"*
2. System: Executes search in background (14 seconds)
3. Content starts playing on TV
4. System: Automatically enables watching mode
5. Gemini: Begins providing scene-by-scene commentary

**Benefits**:
- 🎬 **Seamless demo experience**: One command starts everything
- 🎬 **Smart timing**: Waits for content to load before commentary
- 🎬 **User control**: Can still disable watching mode if desired

## Technical Integration Challenges Solved

### Audio Pipeline Stability
**Problem**: ADB blocking caused Google Cloud Speech timeout errors.
**Solution**: Fire-and-forget async tool calls maintain audio continuity.

### Device Discovery Reliability  
**Problem**: Chromecast discovery sometimes failed in different network environments.
**Solution**: Hybrid approach with auto-discovery + hardcoded fallback.

### Memory System Integration
**Problem**: Mem0 v1.1 deprecation warnings cluttering output.
**Solution**: Explicit version specification in all mem0 API calls.

### Multi-Stream Audio Management
**Challenge**: Managing user microphone + TV audio + Gemini responses without feedback.
**Current**: User mic + TV transcription working; Gemini audio routing TBD.

## Architecture Evolution Summary

**Pre-Control Era**: TV companion could watch and analyze, but couldn't interact with content.

**Post-Control Era**: Complete TV companion with:
- ✅ **Content discovery**: Universal search across all streaming services
- ✅ **Voice interaction**: Full conversational interface with users  
- ✅ **Memory system**: Remembers viewing history and preferences
- ✅ **Adaptive commentary**: Toggle between manual and automatic analysis
- ✅ **Demo readiness**: One-command content loading with auto-commentary

The TV control integration transforms the companion from a passive observer into an active participant in the viewing experience, capable of finding content, remembering preferences, and providing contextual commentary on demand.

## Film Context Knowledge Base Development 🎭

### The Generic Commentary Problem
**Challenge**: Despite successful scene buffering, Gemini's commentary remained generic:
- *"Oh wow, the atmosphere is so dark"*
- *"This looks like an intense conversation"*  
- *"The lighting creates great mood"*

**Root Cause**: Lack of film-specific knowledge. Gemini sees visuals and dialogue but has no context about:
- Plot significance of scenes
- Actor backgrounds and career highlights  
- Director's filmmaking style and techniques
- Production trivia and behind-the-scenes stories
- Cultural impact and critical reception

### Wind Waker Success Pattern
**Inspiration**: The Wind Waker companion's `search_walkthrough()` function provided rich, factual context:
- Complete game walkthrough embedded in vector database
- Real-time search during gameplay for relevant hints/context
- Eliminated hallucination by grounding responses in factual game knowledge

**Goal**: Replicate this approach for films using movie databases and Wikipedia.

### Film Data Source Research

#### IMDB API Investigation
**The $150,000 Barrier**:
```
IMDb Essential Metadata for Movies/TV/OTT (API)
Price: $150,000 + metered costs | 12 month subscription
```

**Scraping Concerns**: IMDB Terms of Service likely prohibit large-scale scraping.

**Verdict**: ❌ Completely unsuitable for indie/research projects.

#### TMDB (The Movie Database) Success! ✅
**Free Alternative with Excellent Coverage**:
- ✅ **Free API**: Just requires registration, no cost
- ✅ **Comprehensive data**: Cast, crew, plot, production details
- ✅ **Rate limits**: 40 requests/10 seconds (very reasonable)
- ✅ **Legal clarity**: Explicitly supports non-commercial use
- ✅ **Active community**: Well-maintained, accurate data

**TMDB API Results**:
```json
{
  "title": "The Big Sleep",
  "release_date": "1946-08-23",
  "overview": "Private Investigator Philip Marlowe is hired by wealthy General Sternwood...",
  "credits": {
    "cast": [{"name": "Humphrey Bogart", "character": "Philip Marlowe"}],
    "crew": [{"name": "Howard Hawks", "job": "Director"}]
  }
}
```

#### Wikipedia API Integration
**Complementary Rich Context**: TMDB provides structured data, Wikipedia provides narrative context.

**Wikipedia API Advantages**:
- ✅ **Completely free**: No rate limits or API keys
- ✅ **Rich articles**: Detailed plot analysis, production stories, cultural impact
- ✅ **Actor biographies**: Career highlights, personal background, notable roles
- ✅ **Director context**: Filmmaking style, recurring themes, other works

### Film Context Library Architecture

**Clean Separation of Concerns**:
```
tv/
├── film_context/
│   ├── __init__.py
│   ├── tmdb_client.py        # TMDB search & movie data
│   ├── wikipedia_client.py   # Wikipedia articles & biographies  
│   ├── embeddings.py         # Vector database creation (TODO)
│   └── context_search.py     # High-level search interface (TODO)
├── tv_companion_with_transcription.py
└── create_film_embeddings.py # CLI tool for building embeddings (TODO)
```

**Benefits of Library Structure**:
- ✅ **Testable independently**: `python -m film_context.tmdb_client "Movie Title"`
- ✅ **Reusable components**: Other projects could use film context search
- ✅ **Clean imports**: Main TV companion just imports high-level functions
- ✅ **Poetry integration**: All dependencies managed at project level

### TMDB Client Implementation Success

**Core Functionality**:
```python
def search_movie_with_credits(title: str, year: int = None):
    # Search TMDB -> filter by year -> get full details with cast/crew
    return movie_details_with_credits

def format_movie_summary(movie):
    # Convert TMDB data into readable text for embeddings
    return formatted_summary
```

**Technical Challenges Solved**:
1. **Date object handling**: `movie.release_date.year` vs `movie.release_date[:4]`
2. **Year filtering**: `movie.release_date.year == year` vs `str(year) in movie.release_date`
3. **Environment integration**: `os.getenv("TMDB_API_KEY")` with Poetry virtual environment

**Testing Results**:
```bash
cd tv && poetry run python -m film_context.tmdb_client "The Big Sleep" 1946
# ✅ Successfully retrieved 48 cast members, 20 crew members
# ✅ Proper year filtering and data formatting
```

### Wikipedia Client Implementation

**Hybrid Access Strategy**:
```python
async def get_wikipedia_article(name: str, content_type: str, year: int = None):
    # 1. Try direct access: "The Big Sleep (1946 film)"
    # 2. Fallback to search + first result
    # 3. Return both summary + full article text
```

**API Selection**:
- **REST API**: For article summaries and metadata
- **Action API**: For full article text content
- **Direct + Search**: Maximum success rate for finding articles

**Plain Text Success**:
```python
# Initial problem: HTML markup in article text
'<p class="mw-empty-elt"></p><p><b>Humphrey DeForest Bogart</b>...'

# Solution: explaintext=true parameter  
url = f"...&prop=extracts&format=json&explaintext=true"

# Result: Clean plain text
'Humphrey DeForest Bogart ( BOH-gart; December 25, 1899 – January 14, 1957)...'
```

**Testing Results**:
```bash
cd tv && poetry run python -m film_context.wikipedia_client "Humphrey Bogart" person
# ✅ 58,169 character article retrieved
# ✅ Clean plain text, no HTML markup
# ✅ Direct access worked, no search fallback needed
```

### Data Quality and Coverage

**TMDB Strengths**:
- ✅ **Structured metadata**: Cast, crew, runtime, genres, production companies
- ✅ **Basic plot summaries**: Good starting point for context
- ✅ **Release information**: Dates, countries, languages
- ✅ **Ratings and popularity**: Community scores and trending data

**TMDB Limitations**:
- ⚠️ **Sparse plot details**: Brief overviews, not detailed analysis
- ⚠️ **Limited trivia**: Basic production info, minimal behind-the-scenes stories
- ⚠️ **No critical analysis**: Raw data without interpretation

**Wikipedia Fills the Gaps**:
- ✅ **Rich plot analysis**: Detailed story breakdowns, themes, symbolism
- ✅ **Production stories**: Behind-the-scenes drama, filming challenges, creative decisions
- ✅ **Cultural impact**: Critical reception, influence on other films, legacy analysis
- ✅ **Personal context**: Actor relationships, career trajectories, notable performances

### Toward Vector Database Integration

**Planned Architecture** (inspired by Wind Waker):
```python
# tv/create_film_embeddings.py
async def create_film_knowledge_base(film_title: str, year: int):
    # 1. Gather comprehensive film data
    tmdb_data = await search_movie_with_credits(film_title, year)  
    wiki_film = await get_wikipedia_article(film_title, "film", year)
    
    # 2. Get cast/crew Wikipedia articles
    director = get_director(tmdb_data)
    lead_actors = get_top_cast(tmdb_data, limit=3)
    
    wiki_people = []
    for person in [director] + lead_actors:
        wiki_people.append(await get_wikipedia_article(person.name, "person"))
    
    # 3. Combine and chunk all text
    combined_text = format_combined_context(tmdb_data, wiki_film, wiki_people)
    chunks = chunk_text(combined_text, chunk_size=1000, overlap=200)
    
    # 4. Create embeddings (using Wind Waker approach)
    embeddings = create_embeddings_with_gemini(chunks)
    save_embeddings(f"{film_title}_{year}_embeddings.json", embeddings)

# tv/film_context/context_search.py  
def search_film_context(query: str, film_embeddings: str, top_k=3):
    # Identical to Wind Waker's search_walkthrough logic
    # Load embeddings, calculate similarities, return relevant chunks
```

**Enhanced Scene Package Integration**:
```python
# In SceneBuffer.create_scene_package():
def create_scene_package(self) -> dict:
    # Vector search on current scene dialogue
    relevant_context = search_film_context(self.transcript, self.film_embeddings)
    
    return {
        "transcript": transcript_text,
        "frames": self.frames,
        "film_context": relevant_context,  # Rich contextual knowledge
    }
```

**Expected Commentary Improvement**:

**Before (generic)**:
- *"This looks like a tense conversation between two people"*

**After (contextual)**:  
- *"This classic Bogart-Bacall dialogue scene showcases Howard Hawks' trademark rapid-fire exchanges. Notice how the camera work mirrors their earlier collaboration in 'To Have and Have Not' - Hawks loved these intimate two-shots that highlight their real-life chemistry."*

### Next Steps: Film Knowledge Pipeline

1. **Complete Vector Database Integration**:
   - Adapt Wind Waker's embedding creation system
   - Build film-specific search functions
   - Test context injection into scene packages

2. **Smart Film Detection**:
   - Auto-detect current film from initial scene dialogue/visuals
   - Load appropriate film knowledge base automatically
   - Handle unknown/multiple films gracefully

3. **Context Relevance Optimization**:
   - Weight search results by scene content type (dialogue vs action vs atmosphere)
   - Include temporal context (early scenes vs climax vs ending)
   - Balance film-specific knowledge with general cinematic analysis

4. **Performance and Caching**:
   - Pre-build embeddings for popular films
   - Implement efficient similarity search algorithms
   - Cache search results within scenes

The film context architecture positions the TV companion to evolve from basic scene commentary to knowledgeable film analysis, grounded in factual information rather than generic observations.

## Film Knowledge Enhancement Implementation 🎭

### Comprehensive Data Gathering Success
**BREAKTHROUGH**: Moved from selective filtering to complete cast/crew data gathering.

**Original Approach - Missed Key Contributors**:
```python
# Old: Limited to "key roles" 
key_roles = ["Director", "Writer", "Producer", "Cinematographer", "Music", "Editor"]
```
**Result**: Missed William Faulkner (Nobel Prize winner, screenplay), Leigh Brackett (legendary sci-fi writer), Max Steiner (iconic composer), and other major contributors.

**New Approach - Comprehensive Collection**:
```python
# New: Take everyone, let embeddings sort relevance
cast_articles = await gather_cast_articles(tmdb_data.credits.cast)  # All 48 actors
crew_articles = await gather_crew_articles(tmdb_data.credits.crew)  # All 20 crew (deduplicated)
```

**Results for The Big Sleep**:
- ✅ **462,665 characters** comprehensive document  
- ✅ **33 of 48 cast articles** retrieved from Wikipedia
- ✅ **17 of 20 crew articles** retrieved from Wikipedia
- ✅ **Zero missed legends** - captured Faulkner, Brackett, Steiner, etc.

### Vector Database Creation Pipeline
**Complete Embeddings Workflow**:
```bash
# 1. Generate comprehensive film document
poetry run python -m film_context.data_gatherer "The Big Sleep" 1946

# 2. Create embeddings from document  
poetry run python -m film_context.create_embeddings "The_Big_Sleep_1946_context.txt"
```

**Performance Metrics**:
- 📊 **579 embedding chunks** from comprehensive document
- 📊 **100% coverage** - no failed embeddings
- 📊 **1000-character chunks** with 200-character overlap for context preservation

### Screenplay Integration Architecture
**Created `add_screenplay.py`** for extending existing film documents:

**PDF Text Extraction**:
```python
# Using pdfplumber for reliable text extraction
with pdfplumber.open(pdf_path) as pdf:
    text_parts = [page.extract_text().strip() for page in pdf.pages if page.extract_text()]
```

**Document Enhancement Workflow**:
```bash
# 1. Add screenplay to existing context document
poetry run python -m film_context.add_screenplay Big_Sleep.pdf The_Big_Sleep_1946_context.txt

# 2. Recreate embeddings with screenplay included
poetry run python -m film_context.create_embeddings "The_Big_Sleep_1946_context_with_screenplay.txt"
```

**Enhanced Results**:
- 📊 **829 embedding chunks** (vs 579 without screenplay)
- 📊 **Scene-specific context**: Screenplay chunks provide exact dialogue and action descriptions
- 📊 **Multi-source knowledge**: TMDB + Wikipedia + Screenplay creates comprehensive understanding

### TV Companion Integration Success

#### Automatic Context Injection
**Problem**: Gemini making generic observations without film-specific knowledge.

**Solution**: Auto-inject relevant context with every scene package:
```python
async def send_realtime(self):
    # Auto-search for relevant context based on dialogue
    auto_context = await self.get_scene_context(msg["transcript"])
    
    if auto_context:
        scene_text += f"\n\n[Context from film knowledge]:\n{auto_context}"
```

**Benefits**:
- ✅ **No tool dependency**: Context provided even if Gemini doesn't call search_film_context
- ✅ **Relevant matching**: Semantic search finds pertinent information for each scene  
- ✅ **Controlled size**: Limited to 800 characters to avoid overwhelming

#### Enhanced Manual Search Tool
**Added `search_film_context` tool** for deeper analysis:
```python
{
    "name": "search_film_context",
    "description": "Search comprehensive film knowledge including cast bios, crew info, plot analysis, themes, and production details.",
    "parameters": {
        "properties": {
            "query": {"type": "string", "description": "What to search for (e.g., 'Humphrey Bogart career', 'Howard Hawks directing style')"}
        }
    }
}
```

#### Embeddings Performance Optimization
**Startup Loading**:
```python
def __init__(self):
    # Load film context embeddings once at startup (not per search)
    self.embeddings_data = self._load_embeddings()
```

**Search Performance**:
- ✅ **829 cached chunks** loaded once at startup
- ✅ **No disk I/O** during searches  
- ✅ **Semantic similarity** using Gemini embeddings + numpy dot product
- ✅ **Detailed logging** shows chunk types (Screenplay, Cast Bio, Crew Bio, etc.)

### System Prompt Evolution Journey

#### Phase 1: Over-Specification (Failed)
```python
# Too many specific examples - Gemini took them literally
"When you see Humphrey Bogart → search for 'Humphrey Bogart detective roles'"
"Notice dramatic lighting → search for 'film noir cinematography'"
```
**Result**: Gemini parroted examples ("noticing dramatic lighting") every scene, zero tool calls.

#### Phase 2: Minimal Directive (Better)
```python 
# Stripped to essentials
"Use search_film_context to find relevant information about what you see and hear, then share interesting insights."
```
**Result**: Some tool calls, but responses still generic without film context.

#### Phase 3: Film-Specific Context (Success)
```python
# TODO: For demo, hardcoding The Big Sleep info. In production, should dynamically
# pull film title, year, cast, director from TMDB/Wikipedia for whatever is being watched
"You are a TV companion watching The Big Sleep (1946), the classic film noir starring Humphrey Bogart and Lauren Bacall, directed by Howard Hawks."
```
**Result**: ✅ Specific observations, ✅ Targeted searches, ✅ Contextual commentary.

### Detailed Search Results Logging
**Added comprehensive logging** to understand embedding performance:
```python
print(f"🔍 Top {min(top_k, len(similarities))} matches:")
for i in range(min(top_k, len(similarities))):
    # Identify section type
    section_type = "Screenplay" if "MARLOWE" in text.upper() else "Cast Bio" if "was an American" in text else ...
    
    print(f"🔍 Match {i+1}: chunk {chunk_id}, score {score:.3f} ({section_type})")
    print(f"    Preview: {text[:150].replace(chr(10), ' ')}...")
```

**Logging Reveals**:
- 📊 **Search quality**: Similarity scores show relevance (0.7+ excellent, 0.4-0.6 decent)
- 📊 **Content types**: Can see if finding screenplay vs cast bio vs production info
- 📊 **Preview accuracy**: First 150 characters confirm search is finding relevant content

### Performance Metrics and Success Indicators

**Data Collection Success**:
- 🎬 **The Big Sleep comprehensive document**: 462K→830K characters with screenplay
- 🎬 **Zero missing legends**: Captured all major contributors  
- 🎬 **Multi-source integration**: TMDB + Wikipedia + Screenplay

**Vector Database Performance**:
- 🔍 **829 searchable chunks** with 100% embedding success
- 🔍 **Semantic search quality**: High relevance scores for scene-dialogue matching
- 🔍 **Startup efficiency**: One-time loading vs per-search file I/O

**Commentary Enhancement**:
- 🎭 **From generic to specific**: "Tense conversation" → "Classic Bogart-Bacall dialogue showcasing Hawks' style"
- 🎭 **Tool usage**: Gemini now calls search_film_context when encountering interesting moments
- 🎭 **Contextual grounding**: Responses backed by factual film knowledge rather than hallucination

### Next Steps: Dynamic Film Detection

**Current Limitation**: Hardcoded for The Big Sleep demo.

**Production Architecture**:
1. **Auto-detect current film** from opening credits, dialogue, or manual selection
2. **Dynamic embeddings loading** based on detected/selected film
3. **Multi-film support** with film switching detection
4. **Popular films pre-processing** for instant availability
5. **Unknown film graceful degradation** to generic commentary mode

**Implementation Plan**:
```python
# Future: Dynamic film context loading
class FilmContextManager:
    def detect_film(self, dialogue: str, visual_frame) -> Optional[str]:
        # Use opening credits, character names, distinctive dialogue
        
    def load_film_context(self, film_id: str):
        # Load appropriate embeddings for detected film
        
    def get_available_films(self) -> List[str]:
        # List pre-processed films with embeddings ready
```

This evolution from generic scene commentary to informed film analysis demonstrates the power of comprehensive knowledge bases combined with semantic search for grounding LLM responses in factual context.

## Lessons Learned

1. **Library Dependencies**: Don't trust outdated wrapper libraries - test direct tools first
2. **Audio Formats**: FIFOs don't work with format-detecting tools like `pw-cat`
3. **stdout Streaming**: Simplest approach often works best
4. **Node Targeting**: Using node names ("Google Chrome") is simpler than parsing IDs
5. **Development vs Demo**: Need both Chrome (dev) and HDMI (demo) approaches
6. **Live API Challenges**: Multimodal streaming requires careful information flow management
7. **pw-cat Excellence**: Professional audio tool beats Python audio processing every time
8. **Comprehensive Data > Filtering**: Better to have too much context than miss key contributors
9. **Semantic Search Quality**: High-quality embeddings eliminate need for complex filtering logic
10. **System Prompt Simplicity**: Specific examples often backfire; clear directives work better
11. **Film-Specific Context**: Generic prompts produce generic responses; specific film knowledge enables rich commentary
12. **Performance Optimization**: Load heavy resources (embeddings) once at startup, not per-request
13. **Logging Visibility**: Detailed search result logging crucial for debugging and optimization

## HDCP Considerations

**Likely to work:**
- YouTube content
- Meeting room presentations
- Local video files
- Cable TV (varies by provider)

**Likely blocked:**
- Netflix, Disney+, Hulu (streaming services)
- Blu-ray players
- Some cable/satellite boxes

**Mitigation:**
- Always have Chrome fallback ready
- Test demo content beforehand
- Use YouTube for reliable demos

## Recent Developments (Latest Session)

### Audio Quality Improvements 🎵

**Problem**: Choppy audio from Gemini responses in TV companion, despite being solved in Wind Waker companion.

**Root Causes Identified**:
1. **No pre-buffering**: Audio started/stopped with each chunk
2. **Blocking I/O operations**: Tool calls blocked audio processing loop
3. **Small audio queue**: Limited buffer space causing blocking

**Solutions Implemented**:

#### Pre-buffering Audio Playback
```python
# Added initial buffer collection before starting playback
initial_chunks = []
for _ in range(3):  # Buffer 3 chunks before starting
    chunk = await self.audio_in_queue.get()
    initial_chunks.append(chunk)

# Play buffered chunks first, then continue normal playback
```

#### Async Tool Operations
Made all blocking operations non-blocking:
```python
# search_film_context now async
query_response = await asyncio.to_thread(
    client.models.embed_content, ...
)

# search_user_history now async  
memories = await asyncio.to_thread(
    self.memory_client.search, ...
)
```

#### Increased Buffer Size
```python
self.out_queue = asyncio.Queue(maxsize=20)  # Increased from 10
```

**Results**: ✅ Smooth audio playback matching Wind Waker companion quality.

### Tool Feedback Loop Resolution 🔄

**Problem**: Infinite feedback loop in watching mode:
1. Scene finalized and sent to Gemini
2. Gemini calls `describe_current_scene` 
3. Sends same scene again
4. Loop continues indefinitely

**Root Cause**: Tools designed for non-watching mode conflicted with auto-sent scene packages.

**Solution**: Selective tool disabling in watching mode:
```python
# Tools disabled in watching mode (no-op with empty response)
- search_film_context     # Was causing repeated calls
- describe_current_scene  # Was analyzing wrong scenes

# Tools enabled in watching mode (essential user controls)  
- search_and_play_content  # For switching movies
- search_user_history      # For episodic memory
- pause_playback          # For media control
- resume_playback         # For media control
```

**Key Learning**: `continue` in tool loop created empty `function_responses`, blocking Gemini. Fixed by returning empty `{}` response instead.

### Scene Management Simplification 🎬

**Problem**: Complex `recent_scenes` storage created confusion and feedback loops.

**User Request**: "Only want current scene on stack. No backlog of scenes."

**Architecture Simplification**:
```python
# Removed
self.recent_scenes = []  # No more scene storage

# Updated finalization  
def _finalize_current_scene(self):
    if self.watching_mode:
        self.out_queue.put_nowait(scene_package)  # Send once
        print("📤 Auto-sent scene package")
    else:
        print("📦 Discarded scene package")  # Just discard

# Updated describe_current_scene to work on live scene only
if self.current_scene is not None:
    scene_package = self.current_scene.create_scene_package()
    self.out_queue.put_nowait(scene_package)
```

**Benefits**:
- ✅ **No storage complexity**: Scenes exist only while being built
- ✅ **Clear separation**: Watching mode vs non-watching mode behavior
- ✅ **Eliminates feedback loops**: Can't repeatedly analyze old scenes

### Media Control Tools Addition 📺

**New Capabilities**: Added pause/resume functionality via ADB commands:

```python
# New tools
{
    "name": "pause_playback",
    "description": "Pause the currently playing content on TV"
},
{
    "name": "resume_playback", 
    "description": "Resume or play the paused content on TV"
}

# Implementation
async def _send_media_key_async(self, keycode: str) -> bool:
    cmd = ["adb", "shell", "input", "keyevent", keycode]
    result = await asyncio.to_thread(subprocess.run, cmd, ...)
    return result.returncode == 0
```

**Usage**: Users can now say "Pause the movie" or "Resume playback" for direct TV control.

### System Instruction Evolution 📝

**Problem**: Gemini forgot it could control TV after focusing system prompt on film analysis.

**Solution**: Comprehensive system instruction covering both capabilities:

```python
"system_instruction": (
    """You are an intelligent TV companion with deep knowledge of film and television.

You can both provide insightful commentary AND control the TV for users.

## TV Control Capabilities:
- Search for and play any movie or show using search_and_play_content
- Pause/resume playback with pause_playback and resume_playback  
- Access user's viewing history with search_user_history
- Toggle watching mode on/off for automatic scene commentary

## Commentary Style:
[Enhanced film analysis guidelines...]
"""
)
```

**Result**: ✅ Gemini now remembers all its capabilities while maintaining high-quality commentary.

### Technical Debt Resolution 🔧

**Fixed Multiple Issues**:
1. **Audio pipeline blocking**: All tool operations now async
2. **Device resource conflicts**: Proper shared video capture handling  
3. **Tool response completeness**: Always send responses, even for disabled tools
4. **Memory efficiency**: Removed unnecessary scene storage
5. **User experience**: Smooth audio during background operations

### Architecture Maturity Assessment

**Current State**: TV companion now matches Wind Waker companion in:
- ✅ **Audio quality**: Smooth, uninterrupted playback
- ✅ **Tool reliability**: No blocking operations
- ✅ **User control**: Full voice interaction + TV control
- ✅ **Memory integration**: Episodic memory with viewing history
- ✅ **Contextual intelligence**: Film-specific knowledge base

**Remaining Challenges**:
- 🔄 **Dynamic film detection**: Still hardcoded for The Big Sleep
- 🔄 **Multi-film support**: Need automatic film switching
- 🔄 **Context optimization**: Better relevance scoring for embeddings

The TV companion has evolved from a basic scene commentator to a sophisticated multimodal AI assistant capable of intelligent film analysis, TV control, and natural conversation while maintaining technical reliability comparable to the Wind Waker reference implementation.
