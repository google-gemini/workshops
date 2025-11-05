# 🤖 Smash Bot: An LLM-Powered Fighting Game Agent

> **📊 [View Presentation Slides](https://google-gemini.github.io/workshops/smash)** - Workshop presentation explaining the architecture and development journey

Welcome to the Smash Bot workshop project! This repository showcases a cutting-edge AI agent capable of playing a fighting game (like Super Smash Bros.) by observing the game state and controlling a virtual gamepad, all powered by a large language model.

## 🌟 What This Project Does

This project demonstrates how to build a robust, closed-loop AI agent that can "see," "think," and "act" within a game environment. It integrates a multimodal Large Language Model (LLM) with computer vision and a frame-accurate virtual controller to enable autonomous gameplay, pushing the boundaries of what LLMs can achieve in real-time interactive systems.

## ✨ Key Features & Capabilities

*   **Virtual Gamepad Control**: Simulates a physical gamepad at the operating system level using `python-uinput`, allowing precise, low-latency input to any compatible game or emulator.
*   **LLM-Powered Reasoning**: Integrates a multimodal LLM (e.g., Google Gemini) that processes visual game state and selects high-level strategic actions.
*   **Computer Vision (Roboflow)**: Employs an external vision model to detect and localize game characters (e.g., Mario, Donkey Kong) on the screen, providing structured spatial awareness to the LLM.
*   **Frame-Accurate Action Execution**: Translates the LLM's high-level commands into precise, timed sequences of gamepad inputs (e.g., `jump()`, `dash()`, `strong_attack()`) using Python generators.
*   **Headless Game Environment**: Runs the game emulator (RetroArch with N64 core) in a headless Linux environment (`Xvfb`) within a Docker container, enabling autonomous operation without a physical display.
*   **Real-time Video Streaming (LiveKit)**: Streams the game's visual output via WebRTC using LiveKit and FFmpeg, allowing for remote monitoring and advanced visual feedback loops.
*   **Containerized & Reproducible**: Fully Dockerized setup ensures a consistent and reproducible development and runtime environment across different machines.
*   **Debugging & Observability**: Leverages tools like LangSmith to trace the LLM's decision-making process, providing crucial insights into the agent's "mind."

## 🚀 Quick Start / Usage

This project is primarily designed for Linux environments due to its reliance on the `uinput` kernel module for virtual gamepad emulation.

1.  **Prerequisites**:
    *   **Docker**: Ensure Docker is installed and running on your Linux machine.
    *   **`uinput` module**: Your Linux kernel must have the `uinput` module loaded. You can load it with:
        ```bash
        sudo modprobe uinput
        sudo chmod 666 /dev/uinput # Grant write permissions for the user inside Docker
        ```
    *   **Google API Key**: You'll need a Google API Key with access to the Gemini model. Set it as an environment variable: `export GOOGLE_API_KEY="your_api_key_here"`

2.  **Build and Run the Bot**:
    The `rebuild_and_run.sh` script will handle the Docker build, download necessary components (like RetroArch cores and the LiveKit server), and launch the bot.

    ```bash
    # Make sure you are in the project root directory
    cd /path/to/smash-bot-repo
    # Export your Google API Key
    export GOOGLE_API_KEY="your_google_api_key"
    # Run the build and launch script
    ./rebuild_and_run.sh
    ```
    This script will:
    *   Build the Docker image.
    *   Launch the container.
    *   Start `Xvfb` (the virtual display).
    *   Launch RetroArch (with a Super Smash Bros. ROM and savestate).
    *   Start the LiveKit server.
    *   Execute the `virtual_controller.py` script, which houses the LLM agent.

3.  **Observe**:
    Once running, the bot will begin playing. You can observe its actions:
    *   **Real-time Video Stream**: Access the LiveKit server from your browser (or LiveKit client) at `ws://localhost:7881`. The bot will publish the game screen as a video stream.
    *   **Logs**: Monitor the console output from the `rebuild_and_run.sh` script to see the agent's internal decisions and actions.

## 🛠️ Technical Highlights

*   **The Multi-Modal Reasoning Loop**: We tackle the challenge of LLM game-playing by establishing a continuous loop: **Perceive** (Game Screen + Vision Model) → **Reason & Select** (Multimodal LLM with Tool Use) → **Translate & Execute** (Virtual Controller) → **Act on** (Game).
*   **Decoupling Strategy & Tactics**: The LLM focuses on high-level strategic intent (e.g., `jump()`, `dash_attack()`), while a pre-programmed "Frame-Precise Translator" handles the low-level, millisecond-accurate execution of button presses and stick movements. This gives the LLM powerful "tools" to wield.
*   **Combatting LLM Latency**: Due to the inherent ~1-2 second latency of LLM inference, the agent is designed for *anticipatory planning* rather than immediate reaction, selecting sequences of actions that unfold over time.
*   **Robust Containerization**: The Docker setup is meticulously crafted to handle complex dependencies like `Xvfb`, `uinput`, RetroArch, Flatpak (initially, then direct core download), FFmpeg, and LiveKit, ensuring a stable and reproducible environment for long-running simulations.
*   **Debugging the "Agentic Mind"**: LangSmith tracing is integrated to provide deep visibility into the LLM's prompts, image inputs, internal thoughts, and selected tool calls, crucial for understanding and refining its emergent behaviors.

## 📚 Links to Detailed Documentation

*   **Development Notes**: For an in-depth chronological breakdown of architectural decisions, challenges, and solutions during development, refer to:
    *   [`NOTES.md`](./NOTES.md) (This file is generated from git commit messages for deep dives into specific changes.)
*   **Presentation Slides**: Explore the high-level overview of the project's architecture, development journey, and key concepts presented at workshops/conferences:
    *   [`smash/slides/index.html`](./smash/slides/index.html) (Open this HTML file in your browser to view the presentation.)
    *   *Self-hosted*: The presentation is built using Slidev. You can serve it locally from the `smash/slides` directory if you have Node.js and Slidev installed.
