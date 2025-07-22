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
- Integrated Gemini 2.5 Flash vision model for game state analysis
- Created `get_game_status` tool with structured JSON output
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

## Current Challenges

### Repository Management
- **Large files**: 24.5MB embedding files must stay out of git
- **Git state**: Need to manage rebase between vision and walkthrough features
- **Untracked files**: 49 untracked files need cleanup

### Performance Optimization
- **Memory usage**: Loading 24MB JSON for every walkthrough query
- **Embedding search**: Could optimize similarity calculations
- **Audio latency**: Pre-buffering helped but may need further tuning

### Real-World Usage Issues (Observed July 21, 2025)
- **Vision analysis too slow**: Screenshot capture and analysis takes 2-10 seconds, blocking conversation flow
- **Sequential tool calling limitation**: Can't call multiple tools simultaneously (e.g., vision + walkthrough search)
- **Tool selection imbalance**: Over-indexing on walkthrough search, under-utilizing vision analysis - needs better decision logic
- **Mixed query types**: Some questions are non-walkthrough related but system handles them reasonably well

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
- **Analysis**: Gemini 2.5 Flash vision model → structured JSON output
- **Integration**: `get_game_status` tool for proactive analysis
- **Bottleneck**: 2-10 second analysis time blocks conversation

### Knowledge System
- **Source**: Official Wind Waker walkthrough text
- **Processing**: Text chunking (1000/200 chars) → Gemini embeddings
- **Search**: Numpy dot product similarity matching
- **Storage**: 24.5MB JSON embeddings (git-excluded)

### Tool Orchestration
- **Current**: Sequential function calling via Gemini Live API
- **Limitation**: Cannot execute multiple tools simultaneously
- **Tools**: `sail_to`, `get_game_status`, `search_walkthrough`

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
*Last updated: July 21, 2025*
