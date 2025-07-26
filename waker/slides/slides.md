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

# Live Audio Conversation

<v-clicks>

- Near-zero latency voice interaction
- Gemini 2.5 native audio dialog model
- Real-time bidirectional streaming
- PyAudio integration with buffering

</v-clicks>

---

# Computer Vision Analysis

<v-clicks>

- Screenshots using mss library
- Analyzed with gemini-2.0-flash-lite
- Understands Link's health, location, enemies
- Structured JSON responses for game state

</v-clicks>

---

# RAG-Based Walkthrough Search

<v-clicks>

- Semantic search over official Wind Waker guide
- Text chunked into 1000-character pieces
- Gemini embeddings with numpy similarity
- More accurate than model training data

</v-clicks>

---

# Episodic Memory

<v-clicks>

- mem0 integration for conversation history
- Remembers user's gameplay progress
- Searches past actions and locations
- Async storage to avoid audio blocking

</v-clicks>

---

# Game Actuation

<v-clicks>

- Controller daemon for shared control
- Plays all 6 Wind Waker songs
- Frame-perfect timing (60 BPM)
- Beat reset hack for 3/4 time signatures

</v-clicks>

---

# The Challenges We Faced

<v-clicks>

**Audio Interruption Crisis**
- Vision calls blocked the event loop
- Fixed with asyncio.to_thread()

**Controller Timing Nightmares**
- Microsecond button presses didn't register
- C-stick vs analog stick confusion
- Musical timing requirements (60 BPM)

**Native Live API Vision**
- Responds to every frame sent
- Lower fidelity than separate models
- Separate vision pipeline proved better

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
