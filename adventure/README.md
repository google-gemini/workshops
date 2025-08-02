# Dungeon Adventure using CrewAI and Gemini

This project is a text-based dungeon adventure game demonstrating a dynamic, interactive storytelling experience powered by CrewAI and Google Gemini. It moves beyond static narratives by leveraging AI agents – a Dungeon Master (DM) and multiple Player Agents – to create an evolving story. The setup showcases CrewAI's capabilities in orchestrating complex, multi-agent interactions to guide a fantasy adventure.

## Key Features & Capabilities

*   **Agent-Driven Storytelling:** Features a persistent Dungeon Master (DM) agent responsible for narrating scenes, evaluating player actions, and introducing challenges, ensuring narrative coherence.
*   **Dynamic Player Roles:** Includes multiple Player Agents with unique roles and goals, each capable of choosing a single action per turn, simplifying interaction while adding depth.
*   **CrewAI Orchestration:** Leverages CrewAI's powerful framework to manage agent interactions, dynamically creating crews for turn-based actions and passing comprehensive context (game history, player roles) for narrative consistency.
*   **Robust State Management:** Utilizes a `GameState` class to chronologically store campaign details, player actions, and scenario descriptions, enabling the DM to maintain context across turns.
*   **LLM Narrative Control:** Employs precise prompt engineering for the DM to ensure concise, focused narration that responds only to player actions and avoids inventing new characters, mitigating common LLM tendencies to drift.

## Quick Start / Usage

This project is designed to be explored interactively in a Google Colab notebook.

*   **Prerequisites:** You'll need a Google Cloud Project with the [Gemini API](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/overview) enabled to run this project.
*   **Launch in Colab:**
    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-gemini/workshops/blob/main/adventure/Dungeon_Adventure.ipynb)
*   **Run the Notebook:** Once opened in Google Colab, simply run through the cells sequentially. The notebook will guide you through setting up your API key, initializing the agents, and starting the game loop.
*   **Interact & Observe:** The game proceeds turn-by-turn. Observe the unfolding narrative and agent interactions in the output. The DM will present scenarios, and player agents will take actions, dynamically progressing the adventure.

## Technical Highlights

This project serves as an excellent demonstration of:

*   **Multi-Agent Architecture:** Shows a clear separation of concerns with dedicated DM and Player agents, each with specific roles and constraints, all orchestrated by CrewAI.
*   **Contextual Reasoning:** Implements robust context passing, where the DM receives the full `game_history` and `player_roles` as input for coherent scenario generation, crucial for long-running narratives.
*   **Prompt Engineering for Control:** Highlights the importance of meticulously crafted prompts (e.g., "Be concise," "Do not invent new characters") to steer LLM behavior, maintain narrative integrity, and overcome common challenges like LLM "hallucinations" or topic drift.
*   **Dynamic Crew Creation:** Illustrates how CrewAI crews can be dynamically created and executed for specific tasks, such as handling a single active player's turn within a larger game loop.
*   **Persistent State Management:** Demonstrates effective use of a `GameState` class to manage an evolving narrative, allowing the DM to always refer to past events and build upon the existing story.

## Links to Detailed Documentation

*   **Colab Notebook:** Explore the full code and run the adventure interactively:
    [Dungeon_Adventure.ipynb](https://colab.research.google.com/github/google-gemini/workshops/blob/main/adventure/Dungeon_Adventure.ipynb)
*   **Development Notes:** For a deeper dive into the design decisions, challenges, and architectural choices made during development, refer to the `NOTES.md` file:
    [adventure/NOTES.md](NOTES.md)