# Wind Waker Voice Chat - System Design

## Overview

The Wind Waker Voice Chat system is a real-time AI gaming companion that combines voice interaction, visual understanding, semantic knowledge retrieval, and direct game control. The architecture prioritizes low-latency audio communication while enabling sophisticated multimodal AI assistance for The Legend of Zelda: Wind Waker.

## High-Level Architecture

### Multi-Process Design

The system employs a **separation of concerns** architecture with two primary processes:

1. **Main Voice Chat Application** (`voice_chat.py`)
   - Handles real-time audio streaming with Gemini Live API
   - Manages AI tool orchestration and conversation flow
   - Performs vision analysis and knowledge retrieval
   - Coordinates with external services (controller, memory)

2. **Controller Daemon** (`controller_daemon.py`)
   - Runs as separate process with elevated permissions
   - Provides virtual controller passthrough for human + AI control
   - Exposes JSON-RPC interface on localhost:9999
   - Handles controller reconnection and fault tolerance

**Rationale**: This separation isolates privilege requirements (`/dev/uinput` access), prevents controller crashes from affecting voice chat, and enables independent scaling/debugging of each component.

## Core Components

### 1. Audio Pipeline

**Architecture**: Bidirectional streaming with pre-buffering optimization

```
Microphone → PyAudio → asyncio.Queue → Gemini Live API
                                            ↓
Speaker ← PyAudio ← Pre-buffer (3 chunks) ← Audio Response
```

**Key Design Decisions**:
- **PyAudio over alternatives**: Direct PortAudio access for minimal latency
- **Pre-buffering strategy**: 3-chunk buffer prevents audio stuttering
- **Async event loop**: `asyncio.to_thread()` for blocking I/O operations
- **Device compatibility**: PulseAudio/PipeWire detection with fallbacks

**Implementation Details**:
- Audio processing prioritized at top of `receive_audio()` loop
- Aggressive stderr suppression for clean debug output
- Queue management prevents audio cutoffs during tool execution

### 2. Vision System

**Architecture**: Hybrid screenshot + dedicated vision model

```
Game Screen → mss capture → PIL processing → Base64 encoding
                                                ↓
Structured JSON ← gemini-2.0-flash-lite ← Screenshot analysis
                                                ↓
Tool Response ← Smart filtering ← Noteworthy detection
```

**Key Design Decisions**:
- **Separate vision model over Live API streaming**: Higher precision, smart filtering
- **Synchronous execution**: Async tools caused model confusion/loops
- **Screenshot approach over game hooking**: Cross-platform compatibility
- **Structured JSON output**: Enables programmatic filtering of observations

**Rejected Approaches**:
- **Native Live API video streaming**: Caused overwhelming chatter, lower fidelity
- **Asynchronous vision tools**: Model got stuck in calling loops
- **Direct game API integration**: Platform-specific, fragile

### 3. Knowledge System (RAG)

**Architecture**: Semantic search over official walkthrough content

```
Walkthrough Text → Text chunking → Gemini embeddings → JSON storage
                                                           ↓
User Query → Query embedding → Similarity search → Top-K results
```

**Key Design Decisions**:
- **Official walkthrough over training data**: Eliminates hallucinations
- **Pre-computed embeddings**: Avoids real-time embedding latency
- **Chunking strategy**: 1000 chars with 200 char overlap preserves context
- **NumPy similarity**: Dot product for efficient vector operations

**Technical Specifications**:
- Model: `gemini-embedding-001` with `retrieval_document` task type
- Storage: 24.5MB JSON file (git-excluded)
- Search: Top-K similarity with configurable threshold
- Integration: Separate `search_walkthrough` tool for explicit knowledge queries

### 4. Controller Actuation

**Architecture**: Virtual device passthrough with JSON-RPC control

```
Physical Controller → evdev → Event filtering → uinput virtual device
                                                      ↑
AI Commands → JSON-RPC (port 9999) → Command translation
```

**Key Design Decisions**:
- **Virtual device approach**: Seamless human + AI control sharing
- **GameCube-accurate mapping**: Analog triggers, C-stick precision
- **Hot-pluggable design**: Automatic reconnection on device changes
- **Precise timing control**: Millisecond-level delays for reliable input

**Controller Mapping**:
- L/R triggers → `ABS_Z`/`ABS_RZ` (analog)
- Right stick → `ABS_RX`/`ABS_RY` (C-stick for songs)
- D-pad → `ABS_HAT0X`/`ABS_HAT0Y`
- Standard buttons → GameCube layout

### 5. Episodic Memory

**Architecture**: Asynchronous intent extraction with mem0 integration

```
Tool Calls → Intent extraction → Async storage → mem0 API
                                                    ↓
Context queries ← Memory search ← User history retrieval
```

**Key Design Decisions**:
- **Intent-based storage**: Extract queries from `executable_code` rather than audio
- **Asynchronous writes**: `asyncio.create_task()` prevents audio blocking
- **Integration with knowledge**: Memory context enhances walkthrough search
- **User-scoped storage**: Separate memory per user/project

**Limitations**:
- Audio-only API provides no speech transcripts
- Can only capture intent from tool interactions
- 2-3 second latency for synchronous mem0 calls (solved via async)

## Data Flow & Integration

### Tool Orchestration Pattern

```
User Speech → Gemini Live API → Tool Selection → Tool Execution
                                                      ↓
Tool Response → Context Integration → AI Response → Audio Output
```

**Current Limitations**:
- Sequential tool execution only (no parallel calls)
- Tool responses interrupt ongoing audio generation
- Limited to tools that return quickly (WebSocket timeout ~30s)

### Multi-Modal Query Handling

**Vision + Knowledge Integration**:
1. User asks game-specific question
2. AI calls `see_game_screen` for current context
3. AI calls `search_walkthrough` for authoritative information
4. Combined response incorporates both visual and knowledge context

**Sailing Observation Mode**:
1. `observe_sailing` spawns background monitoring task
2. Continuous screenshot analysis every 0.5 seconds
3. "Noteworthy" events injected as user turns via `send_client_content`
4. 10-second pause after observations for user response

## Key Design Decisions & Rationale

### 1. Minimal Prompting Strategy

**Problem**: Verbose system instructions caused tool selection confusion
**Solution**: 3-line prompt focusing on core tool usage
**Result**: Consistent tool usage, accurate information retrieval

### 2. Synchronous Vision Analysis

**Problem**: Async vision tools caused model loops and confusion
**Solution**: Accept synchronous latency with fast `gemini-2.0-flash-lite` model
**Trade-off**: Slight conversation pause vs. reliable tool execution

### 3. Separate Controller Process

**Problem**: Permission requirements and fault isolation
**Solution**: Dedicated daemon with JSON-RPC interface
**Benefits**: Security isolation, independent scaling, robust reconnection

### 4. Hybrid Vision Architecture

**Problem**: Live API streaming too chatty, lower precision
**Solution**: Screenshot + dedicated vision model with smart filtering
**Benefits**: High precision, conversational control, specialized prompting

## Performance Characteristics

### Latency Profile
- **Audio round-trip**: ~200-500ms (network dependent)
- **Vision analysis**: ~1-2s (gemini-2.0-flash-lite)
- **Knowledge search**: ~100-300ms (local embeddings)
- **Controller actuation**: ~50-100ms (local JSON-RPC)

### Resource Usage
- **Memory**: ~100MB base + 24.5MB embeddings
- **CPU**: Moderate during vision analysis, low otherwise
- **Network**: Continuous audio streaming + periodic vision calls
- **Storage**: 24.5MB embeddings file (excluded from git)

## Error Handling & Resilience

### Graceful Degradation
- **Missing walkthrough**: Falls back to model knowledge
- **Vision failures**: Continues with audio-only interaction
- **Controller disconnection**: Automatic reconnection with passthrough
- **Memory service unavailable**: Disables episodic features

### Fault Tolerance
- **Audio device issues**: PulseAudio/PipeWire fallback detection
- **WebSocket timeouts**: Automatic session reconnection
- **Tool execution failures**: Error responses maintain conversation flow
- **Process crashes**: Independent controller daemon continues operation

## Future Architecture Considerations

### Scalability Improvements
- **Vector database migration**: Replace JSON embeddings with Pinecone/Chroma
- **Parallel tool execution**: Enable simultaneous vision + knowledge queries
- **Embedding caching**: Reduce memory footprint for knowledge system
- **Multi-game support**: Generalize architecture beyond Wind Waker

### Performance Optimizations
- **Native multimodal Live API**: When filtering capabilities improve
- **Streaming embeddings**: Reduce startup time and memory usage
- **Audio codec optimization**: Explore lower-latency audio formats
- **Vision model fine-tuning**: Game-specific vision model training

### User Experience Enhancements
- **Context-aware tool selection**: Smarter automatic tool orchestration
- **Conversation flow optimization**: Reduce interruptions during tool execution
- **Real-time performance monitoring**: Latency tracking and optimization
- **User feedback integration**: Learning from interaction patterns

---

*This design document reflects the architecture as of July 2025, incorporating lessons learned from extensive development and testing documented in FRICTION-LOG.md and NOTES.md.*
