# Wind Waker Voice Assistant - Friction Log

## Development Timeline - July 2025

### Initial Voice Chat Implementation (Commit 9752287)
**Date**: Early July 2025
**Obstacle**: Need real-time voice interaction for Wind Waker gameplay assistance
**Solution**: Built proof-of-concept with Gemini 2.5 Flash Live API
- Implemented bidirectional audio streaming with PyAudio
- Added graceful shutdown and error handling for audio device issues
- Created `.env` symlink strategy for secrets management
**Status**: ✅ Foundation established

### Sailing Navigation Tool (Commit 16ffca3)
**Obstacle**: Users needed voice commands for Wind Waker ocean navigation
**Solution**: Added `sail_to` tool with function calling
- Integrated FunctionResponse handling with types module
- Implemented tool call processing in receive_audio method
- Enabled commands like "sail to Dragon Roost Island"
**Status**: ✅ Voice-controlled gameplay foundation established

### Vision Analysis Integration (Commit 175037a)
**Obstacle**: Voice assistant was blind to actual game state on screen
**Solution**: Added comprehensive computer vision capability
- Screenshot capture using mss and PIL for fullscreen monitoring
- Integrated gemini-2.0-flash-lite vision model for game state analysis
- Created `see_game_screen` tool with structured JSON output
- Fixed PulseAudio device detection for PipeWire compatibility
- Added `mvp_chat.py` as minimal audio chat proof-of-concept

**Technical Details**:
- Vision model provides contextual analysis including Link's status, environment, UI elements
- Proactive game status checking via updated system instructions
**Status**: ✅ AI can now "see" the game

### Walkthrough Search System (Commit dabbe3d)
**Date**: July 21, 2025
**Obstacle**: Voice assistant giving inaccurate game information based on training data
**Solution**: Built semantic search over official Wind Waker walkthrough
- Created `create_embeddings.py` for Gemini embedding generation
- Added `search_walkthrough` tool with numpy dot product similarity
- Text chunking: 1000 char chunks with 200 char overlap
- Updated system prompt to prioritize walkthrough over training data
- Improved audio with pre-buffering (3 chunks) for smoother responses
- Bumped Python requirement to >=3.11, added numpy dependency

**Technical Details**:
- Uses `gemini-embedding-001` model
- Embeddings saved to `walkthrough_embeddings.json` (excluded from git)
- Enables accurate, contextual Wind Waker gameplay help
**Status**: ✅ Accurate game knowledge established

### Vision Performance Tuning (Late July 2025)
**Date**: July 22, 2025
**Obstacle**: Even with the faster `gemini-2.0-flash-lite` model, there was a desire to eliminate any blocking I/O by making the vision tool call asynchronous.
**Solution**: After experimentation, synchronous execution was retained.
- An attempt to make the `see_game_screen` tool call asynchronous was unsuccessful.
- **Problem**: When `see_game_screen` was async, the model would either get stuck in a loop of calling the tool repeatedly, or provide confusing "tool in progress" updates to the user if we returned an intermediate status.
- **Resolution**: Sticking with a synchronous call for `see_game_screen` was deemed the best user experience. The latency of `gemini-2.0-flash-lite` is acceptable, and it avoids the conversational breakdown of the async approach.
**Status**: ✅ Confirmed synchronous vision analysis is the optimal approach for now.

### Prompt Engineering for Tool Usage (Late July 2025)
**Date**: July 22, 2025
**Obstacle**: Gemini consistently preferred to hallucinate Wind Waker information rather than use the search_walkthrough tool, even with aggressive system instructions.
**Solution**: Applied Occam's Razor to drastically simplify the system prompt.
- **Initial approach**: Complex, aggressive prompt with warnings about incorrect training data, detailed examples, and behavioral patterns (~40 lines)
- **Problem**: Despite explicit instructions, Gemini would claim it would search the walkthrough but then provide answers from memory
- **Resolution**: Simplified to just 3 lines: "To answer questions about the game, use search_walkthrough. To see what's happening on screen, use see_game_screen. Keep responses short for voice chat."
- **Result**: Gemini now consistently searches the walkthrough multiple times per query, providing accurate game information
- Also removed the `sail_to` tool temporarily as it was distracting from core functionality
**Status**: ✅ Minimal prompt approach proven highly effective

### Logging and Debug Output Management (Late July 2025)
**Date**: July 22, 2025
**Obstacle**: Needed detailed logging to debug tool interactions but genai library produced thousands of verbose warnings.
**Solution**: Implemented selective logging with aggressive warning suppression.
- **Problem**: The genai library prints warnings directly to stderr whenever accessing response attributes (e.g., "Warning: there are non-text parts in the response: ['inline_data']")
- **Attempted fixes**: warnings.filterwarnings(), logging level changes - none worked because warnings were printed directly
- **Resolution**: Used contextlib.redirect_stderr() to suppress stderr output during response processing
- Added selective logging that only shows "interesting" responses (tool calls, executable code, etc.)
- Successfully captures Gemini's internal reasoning via executable_code for understanding user intent
**Status**: ✅ Clean logging achieved while preserving useful debug information

### Episodic Memory Integration with mem0 (Late July 2025)
**Date**: July 22, 2025
**Obstacle**: Wanted to add conversational memory but discovered audio-to-audio limitations and latency issues.
**Solution**: Implemented async one-sided memory storage using tool interactions.
- **Discovery**: Gemini Live API in audio mode provides no text transcripts - only audio streams
- **Latency issue**: mem0.add() calls added 2-3 seconds of blocking time, interrupting audio playback
- **Resolution**: 
  - Extract user intent from Gemini's executable_code (e.g., "query='What's on screen?'")
  - Store only user queries, not full conversations
  - Use asyncio.create_task() for fire-and-forget memory storage
  - Memory search integrated into walkthrough tool for context-aware responses
- **Limitation**: Can only capture what users asked via tool calls, not their actual spoken words
**Status**: ✅ Working episodic memory with acceptable performance trade-offs

### Controller Actuation Implementation (Late July 2025)
**Date**: July 23, 2025
**Obstacle**: Needed to enable LLM to control the game directly through controller inputs while sharing control with the user.
**Solution**: Created a separate controller passthrough daemon with JSON-RPC interface.
- **Architecture decision**: Separate daemon binary instead of thread in voice_chat.py for permission isolation and fault tolerance
- **Permission fix**: `/dev/uinput` access via `sudo modprobe uinput && sudo chmod 666 /dev/uinput`
- **Initial error**: "cannot unpack non-iterable int object" - discovered uinput.Device.emit() doesn't accept syn=False parameter
- **Passthrough issues**: 
  - evdev InputDevice.write_event() doesn't exist - had to use emit()
  - Had to filter only EV_KEY and EV_ABS events, ignoring EV_SYN and others
  - evdev and uinput use different event code constants - initially tried raw passthrough which failed
- **Axis mapping nightmare**: 
  - 8BitDo controller sent signed values (-32768 to 32767) but uinput expected 0-255
  - Right analog stick axes were reversed: physical up/down sent ABS_RX, left/right sent ABS_RY
  - First tried swapping axes in mapping but made it worse
  - Eventually kept direct mapping after much debugging with absinfo logging
- **Robust reconnection**: Added automatic controller reconnection on disconnect
- **Created install script**: Permanent udev rules for /dev/uinput permissions
**Status**: ✅ Controller passthrough working with Wind's Requiem actuation

### Wind's Requiem Song Implementation (Late July 2025)
**Date**: July 23, 2025
**Obstacle**: Getting the LLM to actually play Wind's Requiem in-game through controller actuation.
**Solution**: A journey through controller mapping, timing issues, and Wind Waker's musical mechanics.

**Discovery #1 - Wrong Stick**: Initially sent commands to left analog stick (STICK_X/Y) but Wind Waker songs use the C-stick (right analog). No wonder nothing happened!

**Discovery #2 - Axis Confusion**: Spent time debugging whether C_X mapped to RX or RY, eventually using evtest to confirm:
- C_X → ABS_RX (horizontal movement)
- C_Y → ABS_RY (vertical movement)
- No axis swap needed for LLM commands (only physical controller had swapped axes)

**Discovery #3 - Button Press Timing**: Initial implementation pressed/released buttons in microseconds:
```
Event: time 1753334798.877706, type 1 (EV_KEY), code 304 (BTN_SOUTH), value 1
Event: time 1753334798.878021, type 1 (EV_KEY), code 304 (BTN_SOUTH), value 0
```
Only 0.0003 seconds! Games need buttons HELD to register. Fixed by adding delay to press event, not release.

**Discovery #4 - The Beat Reset Dilemma**: 
- Wind's Requiem is in 3/4 time, but if you're already in 4/4 or 6/4, the song fails
- Can't use up/down on left stick (they control volume, not meter)
- Solution: Quick tap left (4/4) then return to center - resets to 3/4 time
- The "hack" is barely noticeable (0.3s total) but ensures 100% reliability

**Discovery #5 - Musical Timing**: 
- Wind Waker's 3/4 songs play at exactly 60 BPM
- Each beat = 1 second (60 beats/minute ÷ 60 seconds/minute)
- Had to hold each C-stick direction for exactly 1 second
- Inter-note delays caused timing issues - removed them entirely

**Technical Details**:
- Implemented generic `play_song` tool replacing single-purpose functions
- All 6 Wind Waker songs defined with proper time signatures
- Beat reset only applied to 3/4 songs (Wind's Requiem, Song of Passing)
- 4/4 songs (Ballad of Gales, Command Melody) start immediately
- Debug buttons (A,B,X,Y) helped verify actuation was working

**Result**: Wind's Requiem now plays reliably every time, with the wind changing direction as expected!
**Status**: ✅ Full Wind Waker song actuation working

### Sailing Observation Mode Implementation (Late July 2025)
**Date**: July 24, 2025
**Obstacle**: Wanted an autonomous sailing mode where Gemini monitors the ocean and alerts the user when something interesting appears.
**Solution**: A painful journey through async function limitations, WebSocket timeouts, and audio interruption issues.

**Discovery #1 - Async Tools Don't Work with Native Audio**:
- Initially tried `behavior: "NON_BLOCKING"` for async function calling
- Documentation reveals: "Asynchronous function calling is only supported in half-cascade audio generation"
- We're using native audio, so async tools are completely unsupported
- Had to abandon the built-in async approach entirely

**Discovery #2 - Long-Running Functions Timeout**:
- Tried implementing a loop inside the tool handler that would run for ~5 minutes
- WebSocket connection timed out after ~20-30 seconds with "keepalive ping timeout"
- The Live API expects functions to return within a reasonable timeframe
- Can't have long-running tool executions even with NON_BLOCKING

**Discovery #3 - Tool Responses Interrupt Audio**:
- Every tool response creates a new conversation turn
- This immediately cuts off any in-progress audio generation
- Even returning empty results or using `scheduling: "SILENT"` didn't help
- Had to completely avoid returning FunctionResponses during monitoring

**Discovery #4 - Multimodal Calls Pause Audio Stream**:
- Even when running vision analysis in a separate asyncio task, audio would pause
- Tried using the same client instance - still caused pauses
- Added initial delay (5-7 seconds) to let model finish speaking before first vision call
- Still investigating root cause - may need separate client or subprocess

**Discovery #5 - Vision Prompt Engineering is Critical**:
- "interesting" was too broad - sunny days were flagged
- "urgent" was too narrow - volcanoes and sea monsters ignored
- "noteworthy" struck the right balance
- Had to explicitly list what to look for AND what to ignore
- Model kept returning lists instead of single JSON objects

**Final Architecture**:
1. `observe_sailing` starts a background asyncio task and returns immediately
2. Background task waits 6 seconds before first vision check
3. Rapid checks every 0.5 seconds using multimodal vision
4. When something noteworthy found, uses `send_client_content` to push new user turn
5. 10-second pause after observations to let user respond
6. `stop_sailing` cancels the background task

**Technical Details**:
- Used `asyncio.create_task()` for fire-and-forget execution
- `send_client_content` with `role='user'` to inject observations
- Tracking last observation to avoid duplicate reports
- 200 max checks (~100 seconds) as safety limit

**Status**: ✅ Working sailing observation mode with acceptable audio interruptions

### Audio Processing and Logging Conflicts (Late July 2025)
**Date**: July 24, 2025
**Obstacle**: Audio kept getting cut off at critical moments, especially when logging "Server content received" messages.
**Solution**: Complete refactoring of the receive_audio method to prioritize audio data.

**Problem #1 - Logging Before Audio**:
- Original code did extensive logging and processing before handling audio chunks
- Every "interesting content" check added latency
- Audio queue was processed last, causing gaps in playback

**Problem #2 - Aggressive Queue Clearing**:
- Code was clearing the audio queue at the end of each turn
- This cut off any remaining audio that hadn't been played yet
- Was originally intended for interruption handling but was too aggressive

**Resolution**:
- Moved audio data handling to the very top of the response loop
- Added `continue` after audio queuing to skip all other processing
- Removed automatic queue clearing
- Eventually removed most logging entirely for cleaner audio flow

**Status**: ✅ Smooth audio playback without interruptions

## Current Challenges

### Repository Management
- **Large files**: 24.5MB embedding files must stay out of git
- **Git state**: Need to manage rebase between vision and walkthrough features
- **Untracked files**: 49 untracked files need cleanup

### Performance Optimization
- **Memory usage**: Loading 24MB JSON for every walkthrough query
- **Embedding search**: Could optimize similarity calculations
- **Audio latency**: Pre-buffering helped but may need further tuning

### Real-World Usage Issues (Observed July 21-22, 2025)
- **Vision analysis latency**: While switching to `gemini-2.0-flash-lite` significantly improved performance, the synchronous nature of the call still introduces a noticeable pause. An attempt at an async tool call was unsuccessful, as it caused the model to either loop calling the tool or give confusing intermediate updates.
- **Sequential tool calling limitation**: Can't call multiple tools simultaneously (e.g., vision + walkthrough search)
- **Audio-only conversational context**: Live API provides no text transcripts, limiting memory storage to tool interactions only
- **Audio cutoff issues**: Discovered that certain response handling (like `continue` after server_content) can interrupt audio playback
- **stderr pollution**: genai library prints warnings directly to stderr, requiring aggressive suppression tactics

### Error Handling
- **Missing dependencies**: Screenshot capture varies across environments
- **File dependencies**: Walkthrough search needs robust missing file handling
- **Audio device issues**: PipeWire/PulseAudio compatibility ongoing

## Key Technical Decisions

### Architecture Choices
✅ **Gemini Live API**: Real-time audio streaming over batch processing
✅ **Function calling**: Tool-based approach for game interactions
✅ **Vision integration**: Screenshot + vision model over game API hooking
✅ **Semantic search**: Embeddings over keyword search for walkthrough
✅ **Pre-buffering**: Audio quality over latency minimization

### Development Patterns
✅ **Incremental features**: Voice → Navigation → Vision → Knowledge
✅ **Error handling**: Graceful degradation when tools fail
✅ **Dependency management**: Poetry for reproducible environments
✅ **Git hygiene**: Keep large generated files out of repository

## Lessons Learned

1. **Real-time audio is hard**: Pre-buffering and device compatibility matter
2. **Vision dramatically improves usefulness**: Being able to "see" the game transforms capability
3. **Function calling enables agency**: Tools make AI assistants actionable
4. **Semantic search beats training data**: Official walkthrough more reliable than model knowledge
5. **Incremental complexity works**: Build core functionality before adding features

## Technical Architecture

### Audio Pipeline
- **Input**: PyAudio microphone capture → Gemini Live API
- **Output**: Gemini Live API → PyAudio speaker playback
- **Optimization**: Pre-buffering (3 chunks) prevents stuttering
- **Challenge**: PipeWire/PulseAudio device compatibility

### Vision System
- **Capture**: mss fullscreen screenshots → PIL image processing
- **Analysis**: gemini-2.0-flash-lite vision model → structured JSON output
- **Integration**: `see_game_screen` tool for proactive analysis

### Knowledge System
- **Source**: Official Wind Waker walkthrough text
- **Processing**: Text chunking (1000/200 chars) → Gemini embeddings
- **Search**: Numpy dot product similarity matching
- **Storage**: 24.5MB JSON embeddings (git-excluded)

### Tool Orchestration
- **Current**: Sequential function calling via Gemini Live API
- **Limitation**: Cannot execute multiple tools simultaneously
- **Tools**: `see_game_screen`, `search_walkthrough` (temporarily removed `sail_to`)

## Future Considerations

### Performance Optimization
- Async tool execution for vision analysis
- Embedding caching strategies
- Vector database migration (Pinecone, Chroma)
- Parallel tool execution architecture

### Capability Expansion
- Multi-modal query handling (vision + knowledge simultaneously)
- Game-specific tooling (inventory, quest tracking)
- Cross-game compatibility architecture
- Real-time performance monitoring

### User Experience
- Conversation flow optimization
- Context-aware tool selection
- Graceful error handling patterns
- User feedback integration loops

---
*Last updated: July 22, 2025*
