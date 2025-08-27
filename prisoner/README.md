# LLM Agents in Game Theory: Prisoner's Dilemma Simulator

This project is a fascinating exploration into the world of AI strategy, demonstrating how Large Language Models (LLMs) can be harnessed to simulate complex, multi-turn game theory scenarios. Specifically, it brings to life the classic **Prisoner's Dilemma**, allowing two distinct AI agents to strategize and interact in an evolving, turn-based game, all visualized through an intuitive Streamlit interface. It's a prime example of building sophisticated AI behaviors beyond simple, one-off prompts.

---

### What this project does

This project implements an interactive simulation of the classic Prisoner's Dilemma game, pitting two distinct AI agents against each other. It showcases how modern Large Language Models (LLMs) like Gemini and DeepSeek (via LiteLLM) can act as strategic, adaptive players in a multi-turn game theory scenario, exploring the dynamics of cooperation and defection. The entire simulation is presented through an interactive Streamlit application, making it easy to observe the game's progression and the agents' decision-making processes.

### Key features/capabilities

*   **Multi-Agent LLM Simulation:** Orchestrates two distinct AI agents, each powered by an LLM, to play the Prisoner's Dilemma, complete with defined roles, goals, and backstories using `CrewAI`.
*   **Interactive Streamlit UI:** Provides a user-friendly interface to run the simulation, visualize the game turn-by-turn, and inspect each agent's moves and their underlying reasoning.
*   **Dynamic Game State & History:** Agents receive a comprehensive, summarized history of past turns, allowing them to make informed and adaptive decisions based on the unfolding game.
*   **Configurable AI Personalities:** Define unique strategic traits (e.g., "adaptive," "ruthless," "bluff-master") and lore (e.g., "Sun-Tzu," "Wildcard") for each LLM agent, profoundly influencing their emergent behavior.
*   **Robust Structured Output:** Employs Pydantic models to enforce a strict output schema for LLM responses, ensuring reliable interpretation of moves and thoughts by the game logic.
*   **Reproducible Environment:** Manages project dependencies using `poetry` for consistent setup and execution.

### Quick start/usage

To get this project up and running and see the LLM agents in action:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/prisoner-dilemma-llm-workshop.git # Replace with actual repo URL
    cd prisoner-dilemma-llm-workshop
    ```

2.  **Set up your environment:**
    This project uses `poetry` for dependency management. Ensure you have Python 3.9+ and Poetry installed.
    ```bash
    poetry install
    ```
    *(Alternatively, if you prefer `pip`, you can generate a `requirements.txt` from `pyproject.toml` and then `pip install -r requirements.txt`)*

3.  **Configure LLM API Keys:**
    The project uses LiteLLM to interface with various LLMs. You will need to set your LLM provider API keys as environment variables. For example:
    ```bash
    export GEMINI_API_KEY="your_gemini_key_here"
    export DEEPSEEK_API_KEY="your_deepseek_key_here"
    # Other LiteLLM configurations might be needed depending on your chosen models.
    ```

4.  **Run the Streamlit application:**
    ```bash
    poetry run streamlit run prisoner/prisoner.py
    ```
    Your default web browser should automatically open to the Streamlit interface, and the simulation will begin.

### Technical highlights

*   **CrewAI Orchestration:** The core of the simulation leverages `CrewAI` to instantiate and manage each LLM agent, defining their roles, goals, and backstories to guide their strategic decision-making.
*   **Pydantic for Structured LLM Output:** A critical design choice for robust interaction, `Pydantic` models are used to enforce a specific JSON output schema for LLMs, making their responses reliably parseable by the game logic. This project also highlights the ongoing challenge of achieving perfectly consistent structured output from LLMs.
*   **Dynamic Game State Passing:** Each LLM agent receives a dynamically generated JSON summary of the *entire* game history before making their move, enabling truly adaptive and context-aware strategies, rather than isolated, one-shot decisions.
*   **Behavioral Probing through LLM Configuration:** Deliberate tuning of LLM parameters like `temperature=1.2` (for creative play) and setting `safety_settings=BLOCK_NONE` for Gemini (to allow for full strategic range, including "defection" or "ruthless" plays without content filtering) enables deeper exploration of LLM behavior in game theory.
*   **Agent Personalities:** Explores how high-level personality descriptions ("bluff-master", "wildcard") programmatically woven into agent backstories influence the emergent strategic behavior of the LLM agents.

### Links to detailed documentation

For an in-depth look at the development process, architectural decisions, and challenges encountered, please refer to the comprehensive development notes:

*   **Development Notes (`NOTES.md`):** [NOTES.md](NOTES.md)