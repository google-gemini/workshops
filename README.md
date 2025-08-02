This `README.md` serves as the top-level directory for the Gemini Meetup Workshops repository.

---

# 🌟 Gemini Meetup Workshops

Welcome to the **Gemini Meetup Workshops** repository! This collection is a dynamic showcase of projects and demonstrations built using Google's Gemini models and related AI technologies. Designed for hands-on learning, each subproject explores unique applications of large language models (LLMs), from creating AI agents that play games to generating dynamic content and integrating AI with hardware.

Whether you're looking to understand multi-agent systems, delve into real-time AI applications, or see how LLMs can be fine-tuned for specific tasks, you'll find a wealth of practical examples here.

---

## 🗺️ Workshop Directory

Below is an organized list of all subprojects within this repository, with a brief description of what each one offers:

*   **[`adventure/`](./adventure/)** - A text-based dungeon adventure game demonstrating dynamic, interactive storytelling using CrewAI and Gemini agents.
*   **[`artifacts/`](./artifacts/)** - Explores AI-driven content creation, showcasing how LLMs can dynamically generate and refine interactive web experiences (HTML, CSS, JS, images).
*   **[`bricks/`](./bricks/)** - An end-to-end pipeline for fine-tuning Gemini to understand natural language and generate precise LDraw (MPD) instructions for brick models.
*   **[`cost/`](./cost/)** - A hypothetical cost-comparison of Gemini vs. GPT vs. Llama 3 for a popular app, along with accompanying slides.
*   **[`doodles/`](./doodles/)** - Demonstrates a pipeline for transforming static bitmap images into dynamic, interactive, and animatable Scalable Vector Graphics (SVGs).
*   **[`factuality/`](./factuality/)** - A quick Perplexity-clone built with CrewAI that summarizes, cites, and redacts news content.
*   **[`games/`](./games/)** - Shows how to play multi-agent games with Gemini using PettingZoo and CrewAI.
*   **[`history/`](./history/)** - An interactive visualizer designed to make the complex evolution and key concepts of Large Language Models (LLMs) accessible through dynamic animations.
*   **[`kundali/`](./kundali/)** - A Jyotish guru implemented as a CrewAI agent performing Kundali Milan (Vedic astrology compatibility).
*   **[`podcast/`](./podcast/)** - An innovative, AI-driven pipeline for automatically generating engaging podcast-style video content from headlines.
*   **[`prisoner/`](./prisoner/)** - Explores LLM agents in game theory, simulating the classic Prisoner's Dilemma with two distinct AI agents in a Streamlit interface.
*   **[`recap/`](./recap/)** - A recap of key learnings and achievements since starting the Gemini workshops.
*   **[`roast/`](./roast/)** - An AI Roast Battle Arena showcasing a dynamic, multi-agent AI system designed to host uncensored roast battles between LLMs.
*   **[`scripts/`](./scripts/)** - Provides a robust framework for generating various types of content, including presentation slides and factual summaries, powered by LLMs.
*   **[`smash/`](./smash/)** - Showcases a cutting-edge AI agent capable of playing a fighting game by observing the game state and controlling a virtual gamepad, powered by an LLM.
*   **[`tv/`](./tv/)** - An advanced LLM-powered assistant designed to be a "TV Companion," offering film commentary, trivia, and even TV control through voice commands.
*   **[`utils/`](./utils/)** - A practical demonstration of integrating LLMs into applications, showcasing automated content generation and robust development practices.
*   **[`waker/`](./waker/)** - A real-time AI gaming companion for The Legend of Zelda: Wind Waker that combines voice interaction, visual understanding, and direct game control.
*   **[`wearable/`](./wearable/)** - Demonstrates how to embed Gemini on a Raspberry Pi Zero W with an Adafruit Voice Bonnet, using Google Speech-to-Text and Text-to-Speech.

---

## 🚀 Getting Started

To explore any of the workshop projects:

1.  **Clone this repository:**
    ```bash
    git clone https://github.com/google-gemini/workshops.git
    cd workshops
    ```
2.  **Navigate to the desired project directory:** Each subproject is self-contained. For example, to explore the `smash` project:
    ```bash
    cd smash/
    ```
3.  **Read the project's `README.md`:** Every subproject has its own `README.md` with detailed instructions on setup, prerequisites, and how to run the specific demonstration.
4.  **Install dependencies and run:** Follow the instructions within each project's `README.md` to install Python dependencies (often with `pip install -r requirements.txt` or `poetry install`), set up API keys, and launch the application.

---

## 🏷️ Categories

To help you find projects of interest, here's a categorization of the workshops:

### AI Agents & Multi-Agent Systems
Projects demonstrating how multiple AI agents can interact, collaborate, or compete to achieve complex goals.
*   **[`adventure/`](./adventure/)** - Multi-agent dungeon master and player agents.
*   **[`factuality/`](./factuality/)** - CrewAI agents for news summarization.
*   **[`games/`](./games/)** - Multi-agent game playing with PettingZoo and CrewAI.
*   **[`kundali/`](./kundali/)** - A CrewAI agent for astrological compatibility.
*   **[`prisoner/`](./prisoner/)** - Two AI agents playing the Prisoner's Dilemma.
*   **[`roast/`](./roast/)** - Multiple AI models engaging in a roast battle with a judge.

### AI in Gaming & Interactive Experiences
Projects focused on integrating AI, particularly LLMs, into games and real-time interactive systems.
*   **[`adventure/`](./adventure/)** - AI-driven text-based dungeon adventure.
*   **[`games/`](./games/)** - AI agents playing multi-agent games.
*   **[`prisoner/`](./prisoner/)** - LLM agents in a game theory simulation.
*   **[`roast/`](./roast/)** - AI-powered roast battle as an entertainment experience.
*   **[`smash/`](./smash/)** - LLM agent controlling a fighting game character.
*   **[`tv/`](./tv/)** - Real-time AI film critic and controller.
*   **[`waker/`](./waker/)** - Real-time AI gaming companion for Wind Waker with voice and control.

### Creative Content & Media Generation
Projects showcasing LLMs' ability to generate dynamic web content, multimedia, and structured data.
*   **[`artifacts/`](./artifacts/)** - AI-powered dynamic web content generation.
*   **[`doodles/`](./doodles/)** - Dynamic SVG storytelling and visualization.
*   **[`podcast/`](./podcast/)** - Automated AI podcast video generation.
*   **[`scripts/`](./scripts/)** - LLM-powered content generation for presentations and summaries.

### Tools & Utilities
Practical applications and utilities leveraging LLMs for various tasks, including information retrieval, analysis, and automation.
*   **[`cost/`](./cost/)** - LLM cost comparison utility.
*   **[`factuality/`](./factuality/)** - News summarization and redaction tool.
*   **[`scripts/`](./scripts/)** - Framework for automated informational asset creation.
*   **[`tv/`](./tv/)** - AI assistant for home entertainment control and commentary.
*   **[`utils/`](./utils/)** - General LLM demonstration for content generation and cost comparisons.

### Hardware Integration
Projects demonstrating how Gemini can be embedded or interact with physical hardware.
*   **[`wearable/`](./wearable/)** - Embedding Gemini on a Raspberry Pi Zero W for voice interaction.

### Specialized AI & Fine-tuning
Projects focusing on fine-tuning LLMs for specific domains or highly structured data generation.
*   **[`bricks/`](./bricks/)** - Fine-tuning Gemini for generating LDraw brick-building instructions.

### Learning & Conceptual Exploration
Projects designed to illustrate core concepts of LLMs or provide overviews of the workshop series.
*   **[`history/`](./history/)** - Interactive visualizer for LLM history and concepts.
*   **[`recap/`](./recap/)** - Overview and recap of lessons learned from the workshops.

---

We hope you enjoy exploring these diverse applications of Gemini and AI!