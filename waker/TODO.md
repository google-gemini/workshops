# Wind Waker Voice Chat - TODO

*Updated: July 22, 2025*

## Demo Scenario - Showcasing Key Capabilities

**Goal**: Demonstrate visual parsing, actuation, episodic memory, and walkthrough recall in a natural conversation.

### Demo Script:

**User**: "I just helped the dragon; any idea where I'm supposed to go next?"  
**Gemini**: *[Uses search_walkthrough]* "After helping Valoo the dragon at Dragon Roost Island, you need to head to Forest Haven to meet the Great Deku Tree. You'll need the Wind Waker to change wind direction for sailing."

**User**: "Have I been there before?"  
**Gemini**: *[Uses search_user_history/memory]* "Yes, actually! You visited Forest Haven yesterday around 3 PM. You were asking about the Korok ceremony and collecting the forest water."

**User**: "What direction do I need to go?"  
**Gemini**: *[Uses see_game_screen + search_walkthrough]* "Looking at your map position near Dragon Roost, you'll need to sail southeast to reach Forest Haven. It's roughly in that direction from where you are now."

**User**: "Can you play the Wind's Requiem to change the wind?"  
**Gemini**: *[Uses actuation]* "Sure! Playing Wind's Requiem now..." *[Actuates: Up, Left, Right on Wind Waker]*

**User**: "I'm going to sail and check my phone; let me know if anything comes up!"  
**Gemini**: *[Uses periodic see_game_screen]* "Got it! I'll keep an eye on the screen and alert you if enemies appear or when we reach Forest Haven."

*[After periodic checks...]*  
**Gemini**: "Heads up! There's a group of seahats approaching from the left, and I can see Forest Haven in the distance!"

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

## Ideas for later

Multiple tools per query would be cool - vision + walkthrough + game state all at once. Async vision with background screenshots for faster responses. More game-specific tools like inventory management, quest tracking, map stuff. Game actuation for sail_to and other movement commands. Maybe expand beyond Wind Waker to other games eventually.

---

**Recent commits**:
- `dabbe3d` - Walkthrough search + audio improvements
- `175037a` - Vision analysis integration
- `16ffca3` - Sail_to navigation tool
- `9752287` - Initial voice chat with Gemini Live API
