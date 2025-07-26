---
title: "Building an AI Gaming Companion: Wind Waker Voice Chat"
theme: seriph
background: https://cover.sli.dev
transition: slide-left
---

# AI Gaming Companion for Wind Waker

## Peter Danenberg

---

# Five Core Features

<v-clicks>

- 🗣️ **Live Conversation** - Gemini 2.5 native audio dialog
- 👁️ **Live Vision** - Real-time game state analysis  
- 📚 **RAG Walkthrough** - Semantic search over guides
- 🧠 **Episodic Memory** - Remembers your gameplay
- 🎮 **Game Actuation** - Plays songs, controls character

</v-clicks>

---

# Architecture

<v-clicks>

- **Audio Pipeline** - PyAudio ↔ Gemini Live API with pre-buffering
- **Vision System** - mss screenshots → gemini-2.0-flash-lite → JSON
- **Knowledge Base** - Official walkthrough → embeddings → numpy search
- **Controller Daemon** - Separate process for shared game control

</v-clicks>

---

# Key Friction Points

<v-clicks>

- **Audio Interruption** - Vision calls blocked event loop (fixed with asyncio.to_thread)
- **Controller Timing** - Microsecond button presses don't register in games
- **Musical Precision** - Wind Waker songs need exact 60 BPM timing + beat resets
- **Native Live API Vision** - Responds to every frame; separate models work better

</v-clicks>

---

# Demo Time!

<div class="text-center text-2xl mt-20">
"It's been awhile, Gemini; what's the last major thing we did?"
</div>

---

# Thanks!

<div class="text-center">
github.com/google-gemini/workshops
</div>
