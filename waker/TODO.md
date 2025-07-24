# Wind Waker Voice Chat - TODO

*Updated: July 22, 2025*

## Email Demo - Key Capabilities to Showcase

When sending out the demo email, make sure to highlight these five core innovations:

1. **Gemini Live (Native Audio)**: Real-time voice conversation with near-zero latency using the native audio dialog model
2. **Personalization (Episodic Memory)**: mem0 integration that remembers user's specific gameplay history and past conversations
3. **In-game Actuation**: Direct game control capabilities (playing Wind Waker songs, future sailing controls)
4. **RAG-based Walkthrough**: Semantic search over game guides for accurate, spoiler-free assistance
5. **Multimodal State-parsing**: Real-time vision analysis to understand what's happening on screen

These capabilities combine to create an AI gaming companion that can see what you see, remember what you've done, and actively help you play.

**Personal Note**: My daughter and I spent about 4 hours debugging this system yesterday - her gaming expertise was invaluable in identifying tool selection issues and testing the conversational flow!

## Demo Scenario - Showcasing Key Capabilities

**Goal**: Demonstrate visual parsing, actuation, episodic memory, and walkthrough recall in a natural conversation.

### Demo Script:

**User**: "It's been awhile, Gemini; what's the last major thing we did?"  
**Gemini**: *[Uses search_user_history]* "Looking at your recent activity... You were at Dragon Roost Island helping Valoo the dragon. You asked about getting the dragon's scale and were working on calming Valoo by dealing with the monster in the volcano."

**User**: "Ok, what should we do next?"  
**Gemini**: *[Uses search_walkthrough]* "After obtaining Din's Pearl from the dragon, you need to sail to Forest Haven to get Farore's Pearl. The Great Deku Tree there will give you the next pearl after you complete the Forbidden Woods dungeon."

**User**: "Ok, can you play Wind's Requiem?"  
**Gemini**: *[Uses actuation]* "Playing Wind's Requiem now to change the wind direction..." *[Actuates: Up, Left, Right on Wind Waker]* "There you go! The wind is now blowing southeast toward Forest Haven."

**User**: "Ok, sailing now. Can you stop the boat when you see something interesting?"  
**Gemini**: *[Uses periodic see_game_screen]* "I'll keep watch and let you know when I spot anything important like islands, enemies, or treasure!"

*[After periodic vision checks...]*  
**Gemini**: "I see a submarine periscope to your right! And there's a platform with a treasure chest ahead. Want to check either of those out?"

### Capabilities Demonstrated:
- **Visual Parsing**: Checking game screen for navigation and threats
- **Actuation**: Playing Wind Waker songs, potential sailing controls
- **Episodic Memory**: Recalling user's previous visits and actions
- **Walkthrough Recall**: Providing accurate game progression guidance

---

## ✅ Fix vision analysis performance (2-10 second delay)

Switched vision model to `gemini-2.0-flash-lite`, which is fast enough to be used synchronously. An attempt to make the tool call async was unsuccessful; the model would either get stuck in a loop calling the tool or give confusing "tool in progress" updates. The current synchronous approach with the faster model has acceptable latency.

## ✅ Add episodic memory with mem0

Successfully integrated mem0 for conversational memory, though with limitations:
- Only captures user queries extracted from tool calls (no audio transcription)
- Had to make storage async to avoid 2-3 second blocking delays
- Memory search integrated into walkthrough tool for context-aware responses

## ✅ Basic controller actuation working

Successfully implemented controller passthrough daemon that allows LLM to play Wind's Requiem and other songs. The daemon forwards user controller inputs while accepting JSON commands from the voice chat for LLM actuation.

### ✅ Wind Waker song playback working

After extensive debugging:
- Fixed C-stick mapping (was using wrong analog stick)
- Implemented proper button hold timing (0.2s minimum)
- Added beat reset hack for 3/4 songs
- Calculated correct timing: 60 BPM = 1 second per note
- All 6 Wind Waker songs now play reliably

## ✅ Fix Z button mapping issue

Fixed by implementing proper GameCube shoulder mapping:
- L and R are now analog triggers (ABS_Z/ABS_RZ)
- Z remains digital button (BTN_TR)
- This matches GameCube controller behavior

## Re-add sail_to tool with actual game actuation

The `sail_to` tool was temporarily removed because it was distracting Gemini from using the walkthrough search. Once the core functionality is solid, re-add it with actual game control capabilities (keyboard/controller input) so it can actually sail Link to destinations rather than just pretending.

## Enable parallel tool calling

Right now it can only do one thing at a time - either look at the screen OR search the walkthrough, but not both. For complex questions like "what should I do here?" it really needs to do both simultaneously. The function calling is all sequential which feels dumb.

## ✅ ~~Build walkthrough search system~~

Got this working on July 21! The semantic search with Gemini embeddings and numpy dot product similarity actually works really well. Had to chunk the text into 1000 char pieces with 200 char overlap. The 24.5MB embeddings file had to stay out of git obviously. Way more accurate than the model's training data.

## ✅ ~~Add vision analysis to voice chat~~

This was huge - commit 175037a. Used mss + PIL for screenshots and Gemini 2.5 Flash for vision analysis. Now the AI can actually "see" what's happening in the game which completely changes what it can do.

## ✅ ~~Improve audio quality~~

Fixed the choppy audio by adding pre-buffering (3 chunks) in the play_audio function. Also made the internal buffer bigger. Audio used to stutter constantly, now it's much smoother.

## Fix tool selection balance

Watching my daughter use it tonight, the system is way over-indexing on walkthrough search and barely using vision. The system prompt tells it to always search the walkthrough first, but sometimes it really needs to just look at the screen. Need smarter logic for deciding which tools to use when.

## Resolve git rebase situation

The vision commit is sitting ahead of origin/main and needs to be rebased on top of the sail_to tool. Have 2 unmerged commits that need to get sorted out. Should probably just rebase the vision stuff on top.

## Fix audio interruption from concurrent LLM requests

The live audio stream gets paused whenever other LLM requests are made (vision analysis, walkthrough search, etc.), even when running in background tasks. This suggests API-level resource contention between different model calls.

**Solutions to investigate**:
- Create separate `genai.Client()` instances for each concurrent request type
- Use different API endpoints/models to avoid resource conflicts
- As extreme fallback, isolate vision/search requests in separate processes
- Test if using Vertex AI directly instead of genai client helps

Currently working around this with initial delays, but proper concurrency would greatly improve responsiveness.

## Document sailing mode design decisions

The sailing observation mode went through many iterations before settling on the current approach. Should document:
- Why async tools don't work with native audio (API limitation)
- Why long-running functions timeout (WebSocket keepalive)
- Why we use background tasks instead of built-in async
- Why we inject observations as user turns instead of tool responses
- The careful balance needed for vision prompts (interesting vs urgent vs noteworthy)

## Optimize audio processing pipeline

The receive_audio method was heavily simplified to fix audio cutoffs, but there might be better approaches:
- Investigate using a separate thread for audio playback
- Consider buffering strategies to handle processing delays
- Test whether we can do some minimal logging without affecting audio
- Look into priority queues for audio data

## Clean up 49 untracked files

The repo is getting pretty messy with all these random files everywhere. Need to go through and figure out what should be gitignored vs actually committed. Probably a bunch of screenshots and logs and temp files.

## Optimize embedding search performance

Currently loading the entire 24MB JSON file for every single query which is obviously not great. Could cache the embeddings in memory, or use a proper vector database like pinecone or chroma. Not a huge problem yet but will definitely scale poorly.

## Add robust error handling

Lots of places where things can break - screenshot capture, missing walkthrough files, audio device weirdness with PipeWire vs PulseAudio, API rate limits, etc. Should handle these more gracefully instead of just crashing.

## Test walkthrough search accuracy

Need to actually test this systematically with real gameplay questions and see if the search results are actually useful. Should compare what the AI says vs looking up the same thing manually in the walkthrough.

## Add separate memory search tool

Currently mixing episodic memory with walkthrough search, which prevents the model from distinguishing between "what the guide says" vs "what the user did". Need a dedicated `search_user_history` tool that specifically queries the user's personal game history, visited locations, collected items, and past questions. This would enable truly personalized responses based on actual gameplay progress.

## Controller Actuation Notes (Reference)

The controller daemon implementation revealed several quirks:
- 8BitDo controllers send signed axis values (-32768 to 32767) that need normalization to 0-255
- Right analog stick axes may be swapped on some controllers (up/down = RX, left/right = RY)
- evdev and uinput use different event code constants - can't pass raw codes between them
- D-pad might send HAT axes (ABS_HAT0X/Y) instead of button events on some controllers
- Always initialize virtual controller to neutral state to prevent phantom inputs at startup

### Wind Waker Song Implementation Details

**C-Stick Mapping**:
- Wind Waker songs use the C-stick (right analog), NOT the left stick
- C_X maps directly to ABS_RX (no swap needed for LLM commands)
- C_Y maps directly to ABS_RY
- Physical controller may have swapped axes, but LLM commands use direct mapping

**Button/Axis Timing Critical**:
- Buttons must be HELD to register - add delay to press event: `{'value': 1, 'delay': 0.2}`
- Wind Waker reads C-stick positions at specific beat intervals
- 3/4 time = 60 BPM = 1 second per beat
- Hold each direction for exactly 1.0 seconds
- Return to center immediately (no delay between notes)

**The Beat Reset Hack**:
- Problem: Starting a 3/4 song while in 4/4 or 6/4 time causes it to fail
- Can't use up/down (they control unused volume feature)
- Solution: Quick left stick tap to 4/4, then back to center
- Timing: 0.1s left, 0.2s back = 0.3s total (barely visible)
- Only needed for 3/4 songs (Wind's Requiem, Song of Passing)

**Debugging Process**:
1. Used evtest to verify virtual controller output
2. Added debug buttons between notes to confirm actuation
3. Discovered microsecond press/release wasn't registering
4. Worked backwards from game's 60 BPM requirement to calculate hold times

## Save File Locations (Reference)

Wind Waker save files are stored in locations like:
- `~/.var/app/org.libretro.RetroArch/config/retroarch/saves/dolphin-emu/User/GC/USA/Card A/01-GZLE-gczelda.gci`

These `.gci` files are useful for transporting saves between machines and are more robust than state saves. The exact path depends on your RetroArch installation and region settings.

## Fix other Wind Waker songs

Currently only Wind's Requiem, Ballad of Gales, and Command Melody are properly implemented with C-stick controls. Need to update:
- Earth God's Lyric (6/4 time - needs different BPM calculation)
- Wind God's Aria (4/4 time)
- Song of Passing (3/4 time - needs beat reset like Wind's Requiem)

## Add more controller actuation capabilities

Now that basic actuation works:
- Sailing controls (hold A to sail, left stick for direction)
- Combat moves (sword swings, shield, targeting)
- Item usage (grappling hook, boomerang, etc.)
- Menu navigation for equipment changes

## Improve beat detection/synchronization

Current beat reset hack works but is inelegant. Better solutions:
- Use vision to detect current time signature from UI
- Implement proper beat synchronization algorithm
- Detect if Wind Waker is already equipped before playing songs

## Test sailing mode with different vision models

Current implementation uses `gemini-2.0-flash-lite` for sailing observations. Should test:
- Whether `gemini-2.0-flash` provides better detection despite higher latency
- If batch processing multiple screenshots helps
- Whether different prompt strategies improve detection accuracy

## Add sailing mode memory

Currently sailing observations aren't stored in episodic memory. Could:
- Store noteworthy observations with timestamps
- Build a "sailing log" of interesting discoveries
- Use this to avoid re-reporting the same landmarks

## Investigate NON_BLOCKING behavior for long-running tools

The current `observe_sailing` implementation uses background tasks and manual async loops, but the Live API supports `behaviour = NON_BLOCKING` which might be cleaner. This would let the model call the function repeatedly until resolution, handling the async loop automatically.

**Potential benefits**:
- Eliminate custom background task management
- Let the API handle the polling/retry logic
- More natural for the model's calling patterns
- Simpler error handling and cancellation

**Implementation approach**:
```python
{
    "name": "observe_sailing",
    "description": "Monitor sailing and report noteworthy observations",
    "parameters": {...},
    "behavior": "NON_BLOCKING"  # Let model handle the polling
}
```

## Replace vision model indirection with native Live API vision

Currently we're doing screenshot → separate vision model → text → Live API, which defeats the purpose of multimodal live. Should investigate using `session.send_realtime_input(media=...)` or `session.send_client_content()` to send images directly to the live session.

**Core idea**: 
```python
# Instead of this:
screenshot = take_screenshot()
analysis = await analyze_with_separate_model(screenshot)
await session.send_client_content(turns=[{"role": "user", "parts": [{"text": analysis}]}])

# Do this:
screenshot = take_screenshot() 
await session.send_realtime_input(media=screenshot)  # Let live model see directly
```

**Challenges to solve**:
- **Filtering uninteresting frames**: Need prompting/config to avoid responding to every frame
- **User intentionality**: Distinguish between automatic monitoring vs explicit "take a look"
- **Response throttling**: Prevent overwhelming the conversation with constant observations

**API methods to explore**:
- `send_realtime_input(media=...)` - Optimized for responsiveness, no ordering guarantees
- `send_client_content(turns=...)` - Ordered context, better for deliberate analysis

This seems like exactly what the Live API multimodal capabilities were designed for - real-time visual understanding without the latency/complexity of separate model calls.

## Ideas for later

Multiple tools per query would be cool - vision + walkthrough + game state all at once. Async vision with background screenshots for faster responses. More game-specific tools like inventory management, quest tracking, map stuff. Game actuation for sail_to and other movement commands. Maybe expand beyond Wind Waker to other games eventually.

---

**Recent commits**:
- `dabbe3d` - Walkthrough search + audio improvements
- `175037a` - Vision analysis integration
- `16ffca3` - Sail_to navigation tool
- `9752287` - Initial voice chat with Gemini Live API

**Sailing Mode Timeline**:
- Initial attempt: Async tools with `NON_BLOCKING` - discovered native audio limitation
- Second attempt: Long-running function loop - hit WebSocket timeout
- Third attempt: Quick returns with `scheduling` hints - interrupted audio
- Fourth attempt: Background task with observation injection - mostly working
- Audio fixes: Moved audio processing first, removed aggressive logging
