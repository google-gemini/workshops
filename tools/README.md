# Documentation Generation Tools

Automated documentation generation for Gemini meetup workshop subprojects.

## Overview

This tool analyzes git commit history using LLMs to create comprehensive development documentation. It generates two types of files:

- **NOTES.md**: Detailed technical development timeline reconstructed from commits
- **README.md**: User-friendly project documentation distilled from the notes

## Setup

```bash
cd tools && poetry install
```

## Usage

Generate documentation for any workshop subproject (run from tools/ directory):

```bash
# Generate both NOTES.md and README.md
cd tools && poetry run python generate-docs.py ../smash

# Generate only detailed notes
cd tools && poetry run python generate-docs.py ../waker --notes-only

# Generate README from existing NOTES.md
cd tools && poetry run python generate-docs.py ../tv --readme-only
```

## How It Works

1. **Git History Analysis**: Extracts chronological commit history for the target subdirectory
2. **LLM Commit Analysis**: Uses Gemini to analyze each commit's diff and message to understand:
   - Problems being solved
   - Technical approaches taken
   - Architectural decisions made
   - Challenges overcome
3. **Context Integration**: Incorporates existing documentation (FRICTION-LOG.md, TODO.md, etc.) for better analysis
4. **Documentation Generation**: Creates comprehensive technical notes and user-friendly README files

## Features

- ✅ Hermetic Poetry environment - no system dependencies
- ✅ Chronological development narrative preservation
- ✅ Existing documentation context integration
- ✅ Professional prompt engineering for both technical and user-facing content
- ✅ Error handling and progress tracking
- ✅ Flexible generation options (notes-only, readme-only)

## Dependencies

- Python 3.11+
- LangChain Google Vertex AI for LLM integration
- Git (for commit history analysis)

All dependencies are managed through Poetry for complete isolation.
