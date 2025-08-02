# AI Roast Battle Arena: Uncensored Wit with LLMs

Welcome to the **AI Roast Battle Arena**, a workshop project designed to showcase the creative and dynamic capabilities of Large Language Models (LLMs) in a uniquely entertaining setting!

## What This Project Does

This project demonstrates a dynamic, multi-agent AI system designed to host uncensored roast battles between large language models. It orchestrates a scenario where different AI models (like Google's Gemini and xAI's Grok) go head-to-head, delivering witty and provocative quips, while an independent third LLM (such as OpenAI's ChatGPT) acts as an impartial judge. This project serves as a compelling demonstration of multi-agent AI orchestration and the ability of LLMs to generate nuanced, context-aware, and intentionally challenging content.

## Key Features & Capabilities

*   **Multi-Agent Orchestration:** Utilizes the powerful `CrewAI` framework to define distinct roles and orchestrate complex interactions between multiple LLMs.
*   **Uncensored Quip Masters:** Features "roaster" agents (e.g., Google's Gemini, xAI's Grok) specifically configured for "no-holds-barred" comedic output, pushing the boundaries of AI-generated humor.
*   **Impartial AI Judge:** Includes a "judge" agent (e.g., OpenAI's ChatGPT) tasked with objectively evaluating roast quality based on wit, humor, and overall impact.
*   **Structured LLM Outputs:** Employs Pydantic models and output parsers to ensure that all LLM responses are structured, reliable, and easily consumable for programmatic display and evaluation.
*   **Interactive Web Application:** A user-friendly Streamlit interface allows you to initiate real-time roast battles, input "roastees," and observe the AI's dynamic exchanges.
*   **Command-Line Interface:** Offers a non-interactive mode for running multi-turn roast battles, ideal for automated testing or batch simulations.
*   **Contextual Memory:** Agents maintain a "roast history" to ensure their quips and judgments are contextually relevant and build upon previous exchanges.

## Quick Start & Usage

To get this project running, you'll need Python 3.9+ and API keys for the LLMs you wish to use (e.g., Google's Gemini, xAI's Grok, OpenAI's ChatGPT).

1.  **Clone the Repository:**
    ```bash
    git clone <YOUR_REPO_URL_HERE>
    cd roast-project # Or whatever your cloned directory is named
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: This project leverages specific configurations of `crewai`, which may be installed directly from its Git repository as per `pyproject.toml`.)*

3.  **Set Up API Keys:**
    Export your LLM API keys as environment variables. For example:
    ```bash
    export GOOGLE_API_KEY="your_gemini_api_key"
    export OPENAI_API_KEY="your_chatgpt_api_key"
    export GROK_API_KEY="your_grok_api_key" # Only if using Grok
    ```
    *Alternatively, you can use a `.env` file in the project root with these variables and a library like `python-dotenv`.*

4.  **Run the Interactive Web App (Streamlit):**
    ```bash
    streamlit run roast/app.py
    ```
    Open your browser to the URL displayed in the console (usually `http://localhost:8501`). Enter a "roastee" and start witnessing the AI wit!

5.  **Run a Command-Line Battle:**
    ```bash
    python roast/main.py --roastee "The Workshop Instructor" --turns 3
    ```
    This will execute a 3-turn roast battle directly in your terminal, showcasing the automated flow.

## Technical Highlights

*   **Advanced Multi-Agent System Design:** Delve into how `CrewAI` is leveraged to define distinct AI roles, tasks, and processes, enabling sophisticated collaborative and adversarial interactions.
*   **Controlled LLM Behavior for Comedy:** Explore the specific techniques used to guide LLMs towards creative, "no-holds-barred" comedic outputs, including direct configuration of safety settings (`BLOCK_NONE` for Gemini) and temperature tuning.
*   **Robust Output Structuring with Pydantic:** Witness the power of Pydantic models in enforcing structured JSON outputs from LLMs, transforming free-form text generation into reliable, parseable data crucial for building robust AI applications.
*   **Dynamic Conversational Context Management:** Understand how `roast_history` is managed and fed back into the LLMs' prompts to ensure coherent, reactive, and building dialogue throughout the battle.
*   **Dual Interface Versatility:** Learn about the implementation of both an interactive web UI (Streamlit) and a powerful command-line tool, catering to different user needs and automation possibilities.

## Links to Detailed Documentation

*   For in-depth development notes, architectural decisions, and challenges overcome during the creation of this project, please refer to the:
    *   [Development Notes](NOTES.md)