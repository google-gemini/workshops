# TV Companion System Design

## Overview

The TV Companion is a real-time multimodal AI system that watches television content alongside users, providing intelligent commentary, film analysis, and voice-controlled TV interaction. The system combines computer vision, audio processing, natural language understanding, and device control to create an interactive viewing experience.

## System Architecture

### High-Level Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input Layer   │    │ Processing Core │    │  Output Layer   │
│                 │    │                 │    │                 │
│ • HDMI Capture  │───▶│ • Scene Buffer  │───▶│ • Audio Output  │
│ • User Mic      │    │ • Transcription │    │ • TV Control    │
│ • Chrome Audio  │    │ • AI Processing │    │ • Memory Store  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Architecture Patterns

1. **Scene-Based Processing**: Content is segmented into coherent scenes using computer vision
2. **Multimodal Context Packaging**: Audio transcripts and visual frames are bundled together
3. **Knowledge-Grounded Responses**: AI commentary is enhanced with film-specific knowledge bases
4. **Asynchronous Tool Execution**: TV control and searches run without blocking audio pipeline

## Input Layer Design

### Video Capture Sources

**HDMI Hardware Capture (Primary)**
- Device: `/dev/video4` (MACROSILICON USB3.0 Video capture)
- Resolution: 1920x1080 @ 30fps
- Formats: YUYV (uncompressed), MJPG (compressed)
- Advantages: Bypasses HDCP, works with protected content

**Chrome Window Capture (Development)**
- Method: Screen capture via OpenCV/PIL
- Limitations: Requires foreground window, browser optimizations
- Use case: Development and testing environment

### Audio Capture Pipeline

**TV Audio Stream**
```bash
pw-cat --record - \
       --target "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo" \
       --rate 16000 --channels 1 --format s16 --raw
```

**User Microphone Stream**
```python
# PyAudio capture for user voice commands
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
```

**Audio Format Conversion**
- Native HDMI: 48kHz stereo s16
- Gemini API: 16kHz mono s16
- Conversion: pw-cat handles resampling and stereo→mono downmixing

## Processing Core Design

### Scene Detection Architecture

```python
class SceneBuffer:
    def __init__(self, scene_number: int):
        self.frames = []          # Visual snapshots
        self.transcripts = []     # Dialogue with timestamps
        self.start_time = time.time()
    
    def create_scene_package(self) -> dict:
        return {
            "scene_number": self.scene_number,
            "duration": f"{duration:.1f}s",
            "transcript": "\n".join(self.transcripts),
            "frames": self.frames,
            "film_context": relevant_knowledge  # From vector search
        }
```

**Scene Change Detection**
- Algorithm: HistogramDetector (optimal for TV content with quick cuts)
- Trigger conditions: Visual transitions, lighting changes, shot changes
- Fallback: 3-minute timeout for long scenes
- Performance: 1-2 minute natural scene boundaries

### Transcription Pipeline

**Google Cloud Speech API**
- Input: 16kHz mono PCM from TV audio
- Output: Real-time transcription with timestamps
- Integration: Transcripts added to current scene buffer

### Knowledge Base Integration

**Film Context Architecture**
```
film_context/
├── tmdb_client.py        # Movie metadata and cast/crew
├── wikipedia_client.py   # Rich articles and biographies
├── data_gatherer.py      # Comprehensive data collection
├── create_embeddings.py  # Vector database creation
└── add_screenplay.py     # Screenplay integration
```

**Vector Search Pipeline**
1. Comprehensive data gathering (TMDB + Wikipedia + Screenplay)
2. Text chunking (1000 chars with 200 char overlap)
3. Gemini embeddings creation (579-829 chunks per film)
4. Semantic search during scene analysis
5. Context injection into scene packages

## AI Processing Layer

### Gemini Live API Integration

**Streaming Architecture**
```python
# User voice → Real-time input
await session.send_realtime_input(audio=user_audio_data)

# Scene packages → Structured content
content = {"role": "user", "parts": [
    {"text": scene_dialogue},
    {"inline_data": frame_1_data},
    {"inline_data": frame_2_data}
]}
await session.send_client_content(turns=content, turn_complete=True)
```

**Commentary Modes**
- **Watching Mode**: Auto-send scene packages for continuous commentary
- **Manual Mode**: Store scenes locally, analyze on user request
- **Tool Integration**: Film context search, TV control, memory queries

### Tool System Design

**Core Tools**
```python
tools = [
    "search_and_play_content",    # TV content search and playback
    "pause_playback",             # Media control
    "resume_playback",            # Media control
    "search_film_context",        # Knowledge base queries
    "search_user_history",        # Episodic memory
    "start_watching_mode",        # Commentary control
    "stop_watching_mode",         # Commentary control
    "describe_current_scene"      # On-demand analysis
]
```

**Asynchronous Execution**
- Fire-and-forget pattern for TV control (prevents audio blocking)
- Background ADB command execution
- Non-blocking knowledge base searches

## Output Layer Design

### Audio Output Pipeline

**Gemini Response Processing**
```python
# Pre-buffering for smooth playback
initial_chunks = []
for _ in range(3):
    chunk = await self.audio_in_queue.get()
    initial_chunks.append(chunk)

# Continuous playback with increased buffer
self.out_queue = asyncio.Queue(maxsize=20)
```

### TV Control Interface

**ADB Command Layer**
```python
# Universal search sequence
adb shell input keyevent KEYCODE_SEARCH     # Open search
adb shell input text "The%sBig%sSleep"      # Enter query
adb shell input keyevent KEYCODE_ENTER      # Execute search
adb shell input keyevent KEYCODE_ENTER      # Select result
```

**Device Discovery**
- Chromecast discovery for automatic IP detection
- Fallback to hardcoded IP addresses
- ADB connection management

### Memory System

**Mem0 Integration**
- Project-specific memory client
- Viewing history storage
- Preference learning
- Context-aware search

## Data Flow Architecture

### Primary Data Streams

```
HDMI Video ──┐
             ├─▶ Scene Detection ──┐
HDMI Audio ──┘                     │
                                   ├─▶ Scene Buffer ──┐
User Voice ────────────────────────┘                  │
                                                       │
Film Knowledge Base ───────────────────────────────────┼─▶ Gemini Live API
                                                       │
Memory System ─────────────────────────────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │ AI Commentary   │
                                              │ TV Control      │
                                              │ Memory Updates  │
                                              └─────────────────┘
```

### Scene Processing Workflow

1. **Capture**: Continuous video/audio capture from HDMI
2. **Detection**: HistogramDetector identifies scene boundaries
3. **Transcription**: Google Cloud Speech processes audio
4. **Buffering**: SceneBuffer accumulates frames and dialogue
5. **Context Search**: Vector search finds relevant film knowledge
6. **Package Creation**: Complete scene package with all context
7. **AI Processing**: Gemini receives structured multimodal input
8. **Response Generation**: AI provides contextual commentary
9. **Output**: Audio playback and optional TV control

## Performance Characteristics

### Latency Profile
- **Scene Detection**: Real-time (< 100ms per frame)
- **Audio Transcription**: ~200-500ms
- **Vector Search**: ~50-100ms per query
- **AI Response**: 1-3 seconds
- **Total Pipeline**: ~2-4 seconds scene-to-commentary

### Resource Requirements
- **Memory**: ~500MB for embeddings, ~200MB for buffers
- **CPU**: Moderate (scene detection, transcription)
- **Network**: Continuous (Gemini Live API, Cloud Speech)
- **Storage**: ~1MB per film knowledge base

### Scalability Considerations
- **Single-user design**: One TV, one companion instance
- **Film knowledge**: Pre-computed embeddings for popular content
- **Memory growth**: Episodic memory accumulates over time
- **Device conflicts**: Shared video capture prevents resource contention

## Error Handling & Resilience

### Failure Modes
- **HDMI capture failure**: Fallback to Chrome window capture
- **Audio pipeline interruption**: Pre-buffering and queue management
- **Network connectivity**: Graceful degradation of cloud services
- **TV control failure**: User notification, manual fallback
- **Scene detection timeout**: 3-minute automatic finalization

### Recovery Strategies
- **Device reconnection**: Automatic ADB reconnection attempts
- **Audio quality**: Multiple buffer sizes and format fallbacks
- **Knowledge base**: Local caching with cloud sync
- **Memory persistence**: Regular memory system backups

## Security & Privacy

### Data Handling
- **Local processing**: Scene detection and buffering on-device
- **Cloud services**: Transcription and AI processing via secure APIs
- **Memory storage**: User data in Mem0 with API key authentication
- **Content capture**: HDMI capture respects fair use principles

### API Security
- **Environment variables**: All API keys stored securely
- **Rate limiting**: Respect service limits (TMDB, Gemini, etc.)
- **Error logging**: Sanitized logs without sensitive data

## Future Architecture Considerations

### Dynamic Film Detection
- **Auto-detection**: Identify current film from credits/dialogue
- **Multi-film support**: Handle film changes during viewing
- **Unknown content**: Graceful degradation to generic commentary

### Enhanced Context
- **Real-time web search**: Current events, actor news
- **Social integration**: Community discussions, reviews
- **Personalization**: Learning user preferences over time

### Platform Expansion
- **Multiple capture sources**: Support various HDMI devices
- **Streaming service APIs**: Direct integration where available
- **Mobile companion**: Smartphone app for remote control

This design represents a mature, production-ready architecture for intelligent TV companionship, balancing technical sophistication with practical usability.
