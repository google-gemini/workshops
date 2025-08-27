# ../Doodles Development Notes

Generated from git commit history on 2025-08-02

## Development Timeline

### Commit 1: Doodles, history (#33) (db5f279)

## NOTES.md: Doodles, history (#33)

This commit introduces a new `doodles` section, marking an exciting step towards creating more dynamic and engaging visual content, specifically for illustrating the "History of LLMs" with animatable graphs and labels. The core problem being solved was how to transform static bitmap images into interactive, scalable vector graphics that could tell a development story in a visually appealing way. This goes beyond simple image display, aiming for a "vivacious" presentation that captures attention.

Our technical approach involved a multi-stage pipeline. First, we leveraged `potrace`, a powerful open-source tool, to convert bitmap images (like `iea.bmp` and `iea.png`) into `.svg` files. A key architectural decision here was the use of specific `potrace` parameters like `--group` for better SVG structure and `--turdsize 5` for despeckling – a crucial step to clean up the vectorized output and ensure smoother animations. Second, we integrated `Vivus.js`, a lightweight JavaScript library, to animate the `stroke` property of the SVG paths, effectively "drawing" the image on screen. Complementing Vivus, we pulled in `GSAP` (GreenSock Animation Platform) to handle the subsequent `fill` and `stroke-width` animations, allowing for a more sophisticated, layered reveal of the vectorized artwork.

The implementation details in `index.html` are particularly insightful. We opted for a `oneByOne` Vivus animation, ensuring paths are drawn sequentially, with `reverseStack: true` to control the drawing order. After the initial stroke animation completes, a `gsap.to` tween is triggered. This is where the magic happens: the stroke width smoothly animates down to `1`, while simultaneously, the paths fill with black, both staggered to create a natural, organic transition. This staged animation, moving from a bold outline to a refined filled shape, was a deliberate design choice to enhance the visual storytelling. While no major "challenges overcome" are explicitly detailed beyond early fixes for clicks and captions, the iterative nature implied by "First pass at animatable SVGs" and the despeckling step suggest a process of refinement to achieve the desired aesthetic and performance. The `TODO.md` file further underscores the intent to animate and "leave it up for a little while to appreciate," highlighting the emphasis on visual experience and pacing.

### Commit 2: Add license (#36) (21a92b1)

## NOTES.md

### Commit: `21a92b1` - Add license (#36)

This commit, while titled "Add license" and showing a diff that exclusively adds the Apache 2.0 license header to `doodles/index.html`, represents the culmination of a much broader and significant development effort captured within Pull Request #36. The extensive squashed commit message body reveals the true scope of work, indicating a major advancement in the project's interactive visualization and presentation capabilities.

The core problem addressed by this body of work was the need to transcend static visual representations and enable dynamic, engaging, and animatable SVG visualizations for complex data and historical timelines. Specifically, there was a drive to illustrate the "History of LLMs" through "animatable graphs with labels" and integrate these "Animatable SVGs in slides." The technical approach centered on making SVGs a primary medium for animation, likely leveraging JavaScript for intricate control over elements and CSS for styling and transitions. This move required foundational work to ensure "first pass at animatable SVGs," paving the way for interactive features like "clicks" and dynamic "captions."

Key architectural considerations revolved around designing SVG structures that could gracefully animate over time while maintaining data integrity and readability. The mention of "despeckle to 5" strongly implies a pipeline involving image vectorization (likely using `potrace` as per `TODO.md`, with `turdsize 5` directly correlating to the despeckle value), ensuring clean vector output for smooth animations. "Change CSS" indicates an iteration on presentation and styling, crucial for effective visual storytelling. Challenges likely included achieving fluid animation performance with potentially complex SVG paths, accurately synchronizing multiple animated elements along a "Timeline," and robustly implementing interactivity (e.g., event listeners for clicks) on dynamically changing SVG content. The "artifact loop" could refer to an iterative refinement process for generating and animating these visual artifacts.

The addition of the Apache 2.0 license at this stage is more than a formality; it signifies a milestone. It marks a point where the newly developed interactive content and the underlying technical mechanisms for generating and animating SVGs are deemed stable enough for broader consumption, collaboration, and formal distribution. This suggests the project is maturing, and these sophisticated visualization capabilities are now ready to be shared and built upon under clear usage terms.
