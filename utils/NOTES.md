# ../Utils Development Notes

Generated from git commit history on 2025-08-02

## Development Timeline

### Commit 1: Artifacts, pre-commit, factuality (#26) (811775f)

# NOTES.md

## Commit 811775f: Artifacts, pre-commit, factuality

This significant commit represents a multi-faceted advancement in the project, primarily focusing on enhancing our demonstration capabilities through automated artifact generation, establishing robust code quality gates, and introducing a powerful new "factuality" feature. The core problem being addressed was the need to dynamically produce presentable content (like cost comparisons of LLMs, or factual summaries) and deploy it seamlessly, while simultaneously fortifying our development practices against common pitfalls.

From a technical standpoint, the "Factuality" feature introduces a sophisticated LLM-driven news summarization capability. We've integrated `langchain_google_genai` to interface with Google's Gemini models, with `newsapi` serving as our external data source for real-time article fetching. A key challenge overcome here was a persistent truncation issue observed with `gemini-1.5-pro` models, necessitating a strategic pivot to `gemini-1.5-flash` as a more reliable alternative for our use case. Furthermore, we encountered and addressed an API key regression where the `ChatGoogleGenerativeAI` constructor wasn't reliably picking up the API key, requiring an explicit `genai.configure()` workaround. It's worth noting that model safety settings were deliberately set to `BLOCK_NONE` across all categories, reflecting an intentional decision to prioritize unfiltered model output for research or demonstration purposes. The addition of a `pyparsing`-based utility `extract_fenced_code` suggests an architectural decision to robustly handle and extract structured data, potentially from LLM outputs themselves.

Beyond the new feature, this commit solidifies our developer experience and deployment pipeline. We've rolled out `pre-commit` hooks to enforce code hygiene and consistency, ensuring that common formatting issues or linting errors are caught before code lands in the repository. For artifact generation and deployment, the commit introduces comprehensive workflows to build and publish various "slides" (covering cost comparisons, feature recaps, and the new factuality demonstrations) directly to GitHub Pages. An interesting iterative decision in the CI/CD setup was the move from a `matrix` strategy back to explicit enumeration for deploying these artifacts, likely to simplify the workflow or address specific nuances of GitHub Pages deployments for multiple content types. The introduction of `utils` modules with a `params_default.py` template further refines our API key management, ensuring secure and consistent configuration across environments. This commit, while broad in scope, lays crucial groundwork for future development and showcases the project's evolving capabilities.
