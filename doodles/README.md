# Dynamic SVG Storytelling & Visualization

This project demonstrates a powerful pipeline for transforming static bitmap images into dynamic, interactive, and animatable Scalable Vector Graphics (SVGs). It's designed to bring visual content to life, particularly for illustrating complex development stories or historical timelines, offering a vivacious and engaging presentation experience.

## Key Features/Capabilities

*   **Bitmap-to-Vector Conversion:** Seamlessly converts raster images (like `.bmp` or `.png`) into crisp, scalable `.svg` files using the open-source tool `potrace`.
*   **Sophisticated SVG Animation:** Leverages a multi-stage animation approach:
    *   `Vivus.js` "draws" SVG paths by animating their strokes.
    *   `GSAP` (GreenSock Animation Platform) handles subsequent, layered animations for fill, stroke width, and advanced sequencing.
*   **Clean Vector Output:** Incorporates despeckling (`--turdsize`) during vectorization to ensure smooth, artifact-free animations, crucial for a professional look.
*   **Staged Visual Reveal:** Implements a deliberate animation sequence, moving from a bold outline to a refined, filled shape for enhanced visual storytelling.
*   **Interactive Potential:** Designed with a foundation for incorporating interactive elements like clicks and dynamic captions (though fully implemented interactivity might be explored in future iterations).
*   **Scalable & Responsive:** Produces vector graphics that scale perfectly across different display sizes without loss of quality.

## Quick Start/Usage

To experience the animated visualizations:

1.  Clone this repository:
    ```bash
    git clone [your-repository-url]
    cd doodles # Or wherever index.html is located
    ```
2.  Open `index.html` in your preferred web browser.
    *   Observe the "drawing" animation followed by the subtle fill and stroke refinement that brings the image to life.

## Technical Highlights

This project showcases a robust technical stack and approach for advanced SVG manipulation, offering valuable insights for workshop attendees:

*   **`potrace` Integration:** Demonstrates effective use of `potrace` with specific parameters (`--group`, `--turdsize 5`, `--alphamax 1`) to optimize SVG structure and quality for animation.
*   **Hybrid Animation Workflow:** Combines `Vivus.js` for an intuitive stroke-based drawing effect with `GSAP` for precise control over subsequent properties like `fill` and `stroke-width`, creating a rich, layered effect.
*   **Sequential Path Animation:** Employs `oneByOne` Vivus animation with `reverseStack: true` to control the drawing order, leading to an impactful visual progression.
*   **Programmatic Animation Sequencing:** Illustrates triggering `GSAP` tweens precisely upon Vivus completion, ensuring synchronized and smooth transitions between distinct animation stages.
*   **Focus on Visual Pacing:** Architectural decisions (like staggered `gsap.to` tweens) emphasize creating an organic, visually pleasing flow from outline to fully realized artwork.

## Links to Detailed Documentation

For a deeper dive into the development process, technical decisions, and future plans:

*   **Development Notes:** [`NOTES.md`](./NOTES.md) - Comprehensive insights into the technical approach, architectural considerations, and challenges overcome during development.
*   **TODO List:** [`TODO.md`](./TODO.md) - Outlines current development tasks and potential future enhancements for this project.
*   **Workshop Slides:** (If applicable, link to any accompanying presentation slides here for a guided walkthrough.)