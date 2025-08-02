# TV Companion: Your AI Film Critic and Controller 🎬

Welcome to the TV Companion project! This repository showcases an advanced LLM-powered assistant designed to revolutionize your home entertainment experience. Imagine a knowledgeable friend watching alongside you, offering insightful commentary, deep-diving into film trivia, and even controlling your TV – all through natural voice commands.

This project demonstrates cutting-edge techniques in real-time multimodal AI, bridging the gap between digital content and intelligent interaction.

## What This Project Does

The TV Companion is an intelligent AI assistant that "watches" movies and shows in real-time, providing contextual commentary and responding to your voice commands. It aims to elevate your viewing experience by offering film analysis, behind-the-scenes insights, and practical TV control, making your entertainment truly interactive.

## Key Features & Capabilities

*   **Real-time Multimodal Input**: Seamlessly captures live audio and video streams from your TV (via HDMI hardware) or browser sources (e.g., Google Chrome).
*   **Intelligent Scene Analysis**: Automatically detects scene changes, transcribes dialogue, and packages visual frames with audio context for the AI, ensuring cohesive understanding.
*   **Deep Film Knowledge Base**: Integrates extensive data from TMDB, Wikipedia, and even film screenplays to provide rich, factual commentary grounded in film history, cast/crew insights, plot analysis, and production trivia.
*   **Voice-Controlled TV Actuation**: Use natural language commands to search for and play content, pause/resume playback, and more, directly on your smart TV via ADB.
*   **Episodic Memory**: Remembers your viewing history and past preferences, enabling personalized interactions like "What was the last movie I watched?"
*   **Flexible Commentary Modes**: Toggle between an automatic "watching mode" for continuous, scene-by-scene commentary, or switch to on-demand analysis for specific moments.
*   **Robust Audio Pipeline**: Ensures smooth, uninterrupted audio output from the AI, even during complex background operations like TV control or knowledge base queries.

## Quick Start / Usage

This project is a sophisticated demonstration of real-time AI, requiring specific hardware and environment setup. While a full quick-start involves setting up an HDMI capture card and configuring ADB for TV control (primarily for Linux systems with PipeWire), the core logic and AI interaction can be explored once the environment is ready.

**To explore the code and its capabilities:**
1.  Clone this repository.
2.  Install project dependencies (Poetry is recommended for dependency management).
3.  Refer to the [NOTES.md](NOTES.md) file for detailed step-by-step setup instructions for audio/video capture, TV control, and API keys.

Once the system is running, you can interact with the companion using natural voice commands (requires a microphone):

*   "Play The Big Sleep"
*   "Pause the movie"
*   "Start watching mode" (for automatic, continuous commentary)
*   "Stop watching mode"
*   "Describe the current scene"
*   "Who is Humphrey Bogart?"

## Technical Highlights

This project pushed the boundaries of real-time multimodal AI, overcoming significant challenges with innovative solutions:

*   **Pioneering Audio Capture**: Achieved robust, real-time audio streaming from system sources (e.g., Google Chrome) or HDMI inputs using `pw-cat`. This included on-the-fly resampling and stereo-to-mono downmixing perfectly tailored for the Gemini Live API.
*   **HDCP Bypass via Hardware**: Successfully captured protected streaming content (like Netflix or Disney+) directly from HDMI devices using a specific USB3.0 capture card, demonstrating a hardware-level solution for content capture challenges without requiring HDCP strippers.
*   **Atomic Multimodal Context Delivery**: Developed a unique "scene buffering" architecture that intelligently groups video frames and transcribed dialogue into a single, cohesive "scene package." This ensures Gemini interprets visual and audio context together, leading to highly coherent and contextual commentary. This was achieved by leveraging the `session.send_client_content()` API call.
*   **Responsive Control Layer**: Implemented asynchronous "fire-and-forget" commands for TV control (via ADB), preventing AI audio pipeline interruptions and ensuring a fluid user experience even during complex background operations.
*   **Intelligent Knowledge Grounding**: Built a comprehensive film knowledge base by integrating and embedding data from TMDB, Wikipedia, and full film screenplays. This vector-embedded knowledge is automatically queried to provide rich, factual, and non-hallucinated commentary, transforming generic observations into insightful film analysis.
*   **Robust Device Management**: Engineered a single, shared video capture approach to prevent device conflicts when multiple processes (like scene detection and periodic screenshots) needed to access the same HDMI capture device simultaneously.
*   **Optimized Audio Playback**: Solved choppy audio output from the AI by implementing pre-buffering strategies, asynchronous tool calls, and increased audio queue sizes, ensuring smooth, uninterrupted voice responses.

## Links to Detailed Documentation

For a deeper dive into the development journey, detailed technical decisions, troubleshooting steps, and setup instructions, please refer to:

*   [**NOTES.md**](NOTES.md): Comprehensive development notes, including problem statements, attempted solutions, and breakthrough discoveries.
*   *(Placeholder for Workshop Slides / Presentation)*