# ../Prisoner Development Notes

Generated from git commit history on 2025-08-02

## Development Timeline

### Commit 1: Adventure (#63) (13bddfa)

## NOTES.md: Commit 13bddfa - Adventure: Prisoner's Dilemma Simulation

This commit introduces a fascinating new "adventure" into our project: a full-fledged simulation of the classic **Prisoner's Dilemma** game, pitting two distinct AI agents against each other. The goal here isn't just a simple game, but to explore how modern LLMs (specifically Gemini and DeepSeek via LiteLLM) can behave as strategic, adaptive players in a multi-turn game theory scenario, all presented through an interactive Streamlit UI.

### Problem Solved: Simulating Strategic AI Behavior in a Game Theory Context

We wanted to move beyond simple one-off prompts and build a system where AI agents could make sequential, informed decisions based on game history and predefined personalities. The Prisoner's Dilemma is a perfect testbed for this, as it forces a trade-off between individual gain and mutual cooperation. A key challenge was reliably orchestrating multi-turn interactions, maintaining game state, and extracting structured decisions from the LLMs.

### Technical Approach & Key Architectural Decisions

1.  **CrewAI Orchestration:** The core of the simulation relies on `CrewAI`. Each player (Gemini and DeepSeek) is instantiated as a `crewai.Agent`, allowing us to define their roles, goals, and backstories which directly influence their LLM prompting. This agent-centric design provides a clean abstraction for managing each player's turn.
2.  **Structured LLM Output with Pydantic:** To ensure the game logic can reliably interpret the agents' moves, we've implemented a strict output schema using `Pydantic` models (`NextMove`). This includes an `Enum` for `Move` (COOPERATE/DEFECT) and a `thought` string. The `PydanticOutputParser` from Langchain is then used in `crewai.Task` to guide the LLM's output. This is a critical architectural decision for robustness, aiming to prevent malformed or ambiguous responses.
3.  **Dynamic Game State Management:** The `GameState` dataclass centrally manages the game's progression. It tracks `turns`, `players`, `max_turns`, and `cumulative_scores`. Crucially, `GameState.get_summary()` provides a JSON representation of the *entire game history* to the LLMs at each turn. This means agents aren't just making isolated decisions; they're reacting to past plays, enabling more complex strategies. We explicitly *don't* pass `max_turns` to the agents' `game_state` summary, making the game effectively an "unknown length" dilemma for them, which can influence their long-term vs. short-term strategic thinking.
4.  **Defined Agent Personalities:** We've gone a step further than generic LLMs. The `make_agent` function allows assigning `strategy` traits (e.g., "adaptive", "ruthless", "bluff-master") and `lore` (e.g., "sun-tzu", "wildcard"). These are programmatically woven into the agent's `backstory` prompt, allowing us to explicitly test different behavioral archetypes within the game. For this initial run, both agents are set to "bluff-master" with "wildcard" lore, which is designed to elicit interesting, non-deterministic play.
5.  **Streamlit for Interactive Visualization:** The entire simulation is wrapped in a Streamlit application, making it easy to run, observe the game flow turn-by-turn, and inspect the agents' moves and reasoning.

### Challenges Overcome (and still present)

The primary challenge this commit highlights, rather than fully overcoming, is the **consistency of LLM structured output**. While `PydanticOutputParser` is used to enforce a `NextMove` schema, the `transcript.md` clearly shows a `crewai.utilities.converter.ConverterError` occurring on Turn 3. This indicates that despite explicit instructions in the prompt (`Return valid JSON and just JSON (no code fences): {parser.get_format_instructions()}`), the LLM still sometimes wraps its JSON output in markdown code fences (e.g., ````json\n...\n````) or otherwise deviates from strict JSON. This is a common pain point when relying on LLMs for programmatic interaction and will need further robust error handling or stricter output enforcement in future iterations.

Another subtle challenge is the "meta-prompting" for agent personalities. The qualitative results in the transcript (Gemini's "long-term mind game" thought, DeepSeek's consistent self-maximization) show that the backstories *do* influence the LLMs' reasoning, but predicting the exact emergent behavior from these high-level strategy descriptions remains an interesting, complex problem.

### Implementation Details That Matter

*   **Dependency Management:** `poetry` is used, as seen by `poetry.lock` and `pyproject.toml`, ensuring a reproducible environment.
*   **LLM Configuration:** Each `LLM` instance in `prisoner.py` sets a `temperature=1.2`, encouraging more creative and less conservative play from the agents. Crucially, Gemini's `safety_settings` are set to `BLOCK_NONE` for all categories. This is a very deliberate choice for a game like Prisoner's Dilemma, where "defection" or "ruthless" strategies might otherwise trigger content filters, preventing the agent from executing its intended role.
*   **Clear Prompting:** The `Task` descriptions for the agents are meticulously crafted using `textwrap.dedent` and f-strings to clearly convey the game context and the expected output format.

This commit lays a robust foundation for experimenting with multi-agent LLM simulations, even as it reveals some of the inherent difficulties in achieving perfectly parseable structured output from current models. The next steps will likely involve refining the output parsing to gracefully handle or self-correct these JSON formatting issues.

### Commit 2: Add license (d0ddacf)

## d0ddacf: Add license

This commit tackles a crucial, often-overlooked aspect of software development: legal groundwork. Up until this point, the `prisoner` project was effectively under "all rights reserved" copyright, making it legally ambiguous for external use, contribution, or even broader internal distribution. The core problem we're solving is removing this legal impediment, clearly defining the terms under which the code can be used, modified, and shared. This clarity is essential for encouraging adoption, fostering an open-source ecosystem around the project, and generally making it viable for collaborative development.

The technical approach was direct and industry-standard: we've formally adopted the Apache License, Version 2.0. This wasn't a casual choice; it's a key architectural decision from a project governance perspective. The Apache 2.0 license is highly permissive, allowing for broad usage, commercial application, and modification, provided attribution is maintained and any significant changes are noted. This aligns perfectly with the goals of promoting widespread use and contributions, especially in environments where integration into proprietary systems might be desired. The "Copyright 2025 Google LLC" further establishes the project's intellectual property ownership under a widely-recognized entity.

For implementation, we've embedded the full Apache 2.0 license boilerplate, including the copyright notice, directly at the top of `prisoner/prisoner.py`. This ensures that anyone encountering or reviewing this foundational file immediately understands the terms of use. While this commit focuses on `prisoner.py`, it establishes the precedent for the entire project. The expectation is that all new source files will follow suit, and a top-level `LICENSE` file will likely be added soon to provide comprehensive project-wide license information. This move lays the essential legal groundwork, transforming the project from a private endeavor into something ready for wider engagement.
