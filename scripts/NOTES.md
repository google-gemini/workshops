# ../Scripts Development Notes

Generated from git commit history on 2025-08-02

## Development Timeline

### Commit 1: Artifacts, pre-commit, factuality (#26) (811775f)

# NOTES.md - Commit 811775f: Artifacts, Pre-commit, Factuality

This commit is a substantial leap forward in the project's maturity and capabilities, touching on several critical areas: establishing a robust local development environment, streamlining artifact generation and deployment, integrating code quality tools, and laying the groundwork for a significant new "factuality" feature. The primary problem being solved here is the evolution from a nascent project to a more production-ready, sustainable codebase with improved developer ergonomics and automated content delivery. It's about solidifying foundations while rapidly iterating on core functionality.

A key technical highlight is the introduction of `scripts/run.sh`. This shell script establishes a canonical local development loop, addressing the common pain points of environment setup and rapid iteration. It leverages `venv` for isolated Python environments, `pip-tools` for deterministic dependency management (complete with `pip-compile --generate-hashes` for security and reproducibility), and `entr` for intelligent live-reloading of the main application whenever relevant files change. This creates a highly responsive feedback loop for developers. From an architectural perspective, this script formalizes our Python dependency and execution strategy, ensuring consistency across developer machines and setting a standard for how our Python applications are run and managed locally.

Beyond the dev environment, this commit significantly refines our artifact generation and deployment workflows, particularly for various slide decks. We're now producing "cost-comparison," "recap," and "factuality" slides as part of our `github-pages` deployment, consolidating these distinct content sets under a unified strategy. This involved careful pathing (`Fix cost directory`), iterative workflow design (experimenting with `matrix` versus explicit enumeration in CI/CD), and proper artifact naming. A crucial challenge overcome during this phase, specific to our LLM integration, was an API key regression and `1.5-pro` truncating results. The pragmatic solution was to downgrade to `1.5-flash` as a workaround, a critical operational detail that highlights the dynamic nature of working with external LLM APIs and our ability to adapt.

Finally, this commit introduces the "factuality" feature, which is described as summarizing news. This represents the inception of a new core capability, likely leveraging LLMs to provide factual content or summaries, potentially addressing hallucination concerns. Alongside this, `pre-commit` hooks were integrated and refined, enforcing code style and quality standards from the very beginning of the commit lifecycle. This dramatically improves code consistency and reduces the overhead of code reviews for style issues. The inclusion of `README` files and Apache licenses further underscores the push towards a well-documented and officially licensed project.
