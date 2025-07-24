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

## Fix Z button mapping issue

Currently the Z button (mapped to RB) sends the same code as R button (RT). The L and R shoulder buttons work correctly, but we need to figure out proper Z button mapping. This might require checking what specific button codes the 8BitDo controller sends for the Z button vs other buttons.

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

## Save File Locations (Reference)

Wind Waker save files are stored in locations like:
- `~/.var/app/org.libretro.RetroArch/config/retroarch/saves/dolphin-emu/User/GC/USA/Card A/01-GZLE-gczelda.gci`

These `.gci` files are useful for transporting saves between machines and are more robust than state saves. The exact path depends on your RetroArch installation and region settings.

## Ideas for later

Multiple tools per query would be cool - vision + walkthrough + game state all at once. Async vision with background screenshots for faster responses. More game-specific tools like inventory management, quest tracking, map stuff. Game actuation for sail_to and other movement commands. Maybe expand beyond Wind Waker to other games eventually.

---

**Recent commits**:
- `dabbe3d` - Walkthrough search + audio improvements
- `175037a` - Vision analysis integration
- `16ffca3` - Sail_to navigation tool
- `9752287` - Initial voice chat with Gemini Live API
