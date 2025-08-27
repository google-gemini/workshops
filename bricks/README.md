# Bricks

Fine-tuning Gemini for brick-building

Welcome to the "Bricks" project! This repository showcases a comprehensive, end-to-end pipeline for fine-tuning large language models to understand and generate highly structured data, specifically LDraw (MPD) instructions for brick models. Designed as a workshop example, it demonstrates practical applications of advanced LLM techniques for specialized domain tasks.

---

### What this project does

The "Bricks" project demonstrates an end-to-end pipeline for fine-tuning Google's Gemini 1.5 Pro model to understand natural language descriptions and generate precise LDraw (MPD) brick-building instructions. It tackles the challenge of automating the creation of detailed 3D brick model files from simple user queries, eliminating the need for tedious, manual MPD file creation.

### Key Features & Capabilities

*   **Automated Training Data Generation:** Leverages cutting-edge multimodal LLMs (like GPT-4o) to synthetically generate high-quality, structured text descriptions and diverse user queries directly from visual inputs (rendered brick models).
*   **Vertex AI Supervised Fine-Tuning:** Prepares and orchestrates the fine-tuning of Gemini 1.5 Pro on Google Cloud's Vertex AI platform using instruction-tuned datasets.
*   **LDraw MPD Generation:** Enables the fine-tuned Gemini model to translate natural language prompts into accurate, machine-readable LDraw MPD (Model Primitive Data) files.
*   **Inference Integration:** Demonstrates how to query the custom-tuned Gemini model for real-time MPD generation using LangChain.
*   **Comprehensive Project Documentation:** Includes detailed development notes and an interactive, code-driven presentation built with Slidev, making the complex process transparent and understandable.

### Quick Start / Usage

This project is designed as a detailed demonstration of an end-to-end LLM fine-tuning pipeline rather than a ready-to-run application. While full training cycles can be resource-intensive, you can explore the core components and logic:

1.  **Examine the Pipeline Scripts:**
    *   `bricks/bin/render.sh`: Renders LDraw files into images (a prerequisite for data generation).
    *   `bricks/bin/describe.py`: The heart of synthetic data generation – uses a multimodal LLM to create descriptions and queries from rendered images.
    *   `bricks/bin/examples.py`: Prepares the generated data into Vertex AI's instruction tuning (`.jsonl`) format.
    *   `bricks/bin/train.py`: Orchestrates the fine-tuning of Gemini 1.5 Pro on Vertex AI.
    *   `bricks/bin/query.py`: Demonstrates how to interact with a *fine-tuned* Gemini model endpoint for MPD generation.
2.  **Review the Generated Data:** Inspect the format of the synthetic descriptions and the instruction-tuned examples to understand the training data structure.
3.  **Explore the Presentation:** Dive into the accompanying Slidev presentation (see "Detailed Documentation" below) for a high-level overview and visual explanations.

### Technical Highlights

*   **Multi-stage AI Pipeline:** A robust, automated pipeline encompassing data rendering, synthetic data generation, data preparation, model fine-tuning, and inference.
*   **Multimodal Data Generation:** Ingenious use of `gpt-4o` to synthesize diverse training data (text descriptions + queries) directly from visual inputs (PNG renders of brick models).
*   **Structured Output with Pydantic:** Ensures reliable, parseable output from LLMs during data generation, crucial for downstream processing and data quality.
*   **Vertex AI Supervised Fine-Tuning:** Direct application of Vertex AI's SFT service with `gemini-1.5-pro-002`, showcasing best practices for custom LLM adaptation for specific tasks.
*   **Instruction Tuning Format:** Adherence to standard instruction tuning formats (`{"systemInstruction": ..., "contents": [...]}`) for efficient and effective model training on Vertex AI.
*   **Practical LLM Considerations:** Includes logic for managing token limits and exposing key hyperparameters (e.g., `EPOCHS`, `LEARNING_RATE_MULTIPLIER`) for fine-tuning optimization and experimentation.
*   **Versioned, Code-Centric Presentation:** Utilizes [Slidev](https://sli.dev/) (Markdown-based, Vue 3) for an interactive, maintainable, and deployable presentation, treating documentation as a first-class citizen.
*   **Clear Licensing:** Demonstrates how to properly license project files (Apache 2.0) for sharing and collaboration in a professional development environment.

### Links to Detailed Documentation

*   **Comprehensive Development Notes (`NOTES.md`):** For an in-depth look at the project's evolution, core problem statements, architectural decisions, and challenges faced during development, refer to the detailed [NOTES.md](NOTES.md) file.
*   **Accompanying Workshop Presentation (`slides.md`):** Explore the interactive presentation built with Slidev, which visually explains the project's architecture, methodology, and results. You can find the source in `bricks/slides/slides.md`.