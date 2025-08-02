# Interactive LLM History & Concepts Visualizer

Welcome to the `history` project, a core component of the `workshops` repository! This project is designed to make the complex evolution and key concepts of Large Language Models (LLMs) accessible and engaging through dynamic, interactive visualizations.

---

## What This Project Does

This project provides a unique, visually rich narrative of Large Language Models (LLMs), illustrating their historical development, growth patterns, and conceptual challenges like "model collapse." Moving beyond static charts, it leverages animated graphics to deliver an immersive storytelling experience, making abstract technical concepts clear and captivating for workshop participants and curious learners alike.

## Key Features & Capabilities

*   **Interactive & Animated Visualizations:** Experience LLM concepts (e.g., "hockey-stick growth," "LLM saturation," "fixed-point behavior") through compelling, dynamic SVG animations.
*   **Historical Timeline:** Explore a clear, animated timeline of significant milestones in LLM development.
*   **Dynamic Animation Triggering:** Animations are intelligently triggered only when their corresponding slide becomes visible, ensuring optimal performance and a smooth presentation flow.
*   **Scalable Vector Graphics (SVG):** All graphs are rendered as SVGs, providing crisp, high-quality visuals that scale perfectly to any screen size.
*   **Intelligent Labeling:** Programmatic control ensures labels on complex graphs are positioned dynamically to prevent overlaps, enhancing clarity.
*   **Reusable Component Architecture:** Built with reusability in mind, making it easy to integrate similar animated content into other Slidev presentations.

## Quick Start / Usage

To experience the interactive presentation:

1.  **View the Live Demo:** The complete "History of LLMs" presentation is deployed and accessible online:
    [**Launch the LLM History Slides**](https://google-gemini.github.io/workshops/history/slides/)

2.  **Run Locally (for Developers):**
    If you wish to explore, modify, or extend the project, you can run it locally:
    *   Ensure you have [Node.js](https://nodejs.org/) (with `npm`) and [Python](https://www.python.org/) installed on your system.
    *   Clone the main `workshops` repository:
        ```bash
        git clone https://github.com/google-gemini/workshops.git
        cd workshops/history
        ```
    *   Install frontend dependencies:
        ```bash
        npm install
        ```
    *   (Optional) Generate/Regenerate SVG graphs using the Python backend:
        ```bash
        python graph.py
        ```
    *   Start the Slidev presentation server:
        ```bash
        npm run slides
        ```
        This will open the presentation in your web browser, typically at `http://localhost:3030`.

## Technical Highlights

This project stands out for its blend of powerful technologies to deliver an engaging user experience:

*   **Polyglot Architecture:** It seamlessly combines **Python** (using Matplotlib and NumPy) for precise, programmatic SVG graph generation on the backend with a **JavaScript/Vue.js** frontend (powered by the **Slidev** framework).
*   **Vector-First Animation:** Instead of static images, all visualizations are **SVGs**, allowing for granular control and sophisticated "drawing" animations achieved through the **GreenSock Animation Platform (GSAP)** and its `stroke-dashoffset` technique.
*   **Smart Component Design:** A custom `AnimatableSvg.vue` component intelligently uses a `MutationObserver` to detect slide visibility, fetching and animating SVG content only when needed, significantly optimizing performance.
*   **Robust Deployment:** Employs absolute URLs for static assets to ensure reliable loading and display across various hosting environments, including GitHub Pages.
*   **Markdown-Driven Content:** Leverages Slidev's markdown-based structure for easy content creation, augmented by custom Vue components for dynamic and interactive elements.

## Links to Detailed Documentation

To dive deeper into the project's development journey, architectural decisions, and technical challenges:

*   **Development Notes:** Explore the comprehensive commit-by-commit development log, outlining the rationale behind key decisions and problem-solving approaches:
    [**History Development Notes**](NOTES.md)
*   **Live Presentation:** Access the interactive "History of LLMs" slides directly:
    [**LLM History Slides**](https://google-gemini.github.io/workshops/history/slides/)