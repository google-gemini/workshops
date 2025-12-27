# SeizureScoreAI: Multi-Agent Clinical Reasoning System

A multi-agent system designed to emulate epileptologist decision-making for ILAE outcome scoring after epilepsy surgery. Built with **Google's Agent Development Kit (ADK)**, the system uses Gemini 3 Flash models in a sequential agent pipeline to process clinical notes and evaluate post-surgical outcomes. The goal is to teach an LLM to reason like an epileptologist.

## Overview

SeizureScoreAI employs a three-agent pipeline to process clinical notes and determine ILAE (International League Against Epilepsy) outcome scores:

1. **Clinical Information Extractor**: Analyzes clinical notes to extract key metrics including:
   - Presence of seizure freedom
   - Presence of auras
   - Baseline seizure frequency (pre-treatment)
   - Post-treatment seizure frequency

2. **ILAE Score Calculator**: Applies expertise to:
   - Process extracted clinical information
   - Calculate ILAE outcome scores based on standard criteria
   - Provide detailed reasoning for score determination

3. **Concise Reporter**: Generates clear, concise summaries of:
   - Final ILAE score
   - Key factors influencing the score
   - Clinical reasoning behind the determination

## Technical Architecture

### Components

- **Frontend**: Streamlit interface for clinical note input and result display
- **Backend**: Multi-agent system built with **Google Agent Development Kit (ADK)**
- **Agent Framework**: Sequential pipeline using ADK's `LlmAgent` class
- **Model**: Gemini 3 Flash Preview (`gemini-3-flash-preview`)
- **Session Management**: In-memory session service for agent state
- **Structured Output**: JSON-formatted data for consistent processing between agents

### Data Flow

```
Clinical Note → [Agent 1: Extract] → Structured Data → [Agent 2: Calculate] → ILAE Score + Reasoning → [Agent 3: Summarize] → Final Output
```

1. Clinical note input → Information Extraction (JSON)
2. Structured entities → ILAE Score Calculation
3. Detailed analysis → Concise Reporting
4. Final output → User presentation with highlighted supporting text

## Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

```bash
# Clone the repository
git clone https://github.com/vineet-reddy/SeizureScoreAI.git
cd SeizureScoreAI

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### Usage

Run the Streamlit application:

```bash
streamlit run app/streamlit_app.py
```

The application will:
1. Accept clinical notes as input (via file upload)
2. Process them through the three-agent pipeline
3. Return ILAE scores with explanations
4. Display the clinical note with highlighted supporting text

## ILAE Outcome Scale

The system evaluates surgical outcomes based on the following scale[^1]:

| Class | Outcome |
|-------|---------|
| **1** | Completely seizure free; no auras |
| **2** | Only auras; no other seizures |
| **3** | 1-3 seizure days per year; ± auras |
| **4** | 4 seizure days per year to 50% reduction of baseline seizure days; ± auras |
| **5** | Less than 50% reduction of baseline seizure days; ± auras |
| **6** | More than 100% increase of baseline seizure days; ± auras |

[^1]: Source: [MGH Epilepsy Service - Epilepsy Surgery Outcome Scales](https://seizure.mgh.harvard.edu/engel-surgical-outcome-scale/)

## Project Structure

```
SeizureScoreAI/
├── src/
│   └── seizure_score_ai/
│       ├── __init__.py           # Package initialization
│       └── agents.py             # Multi-agent pipeline using Google ADK
├── app/
│   ├── streamlit_app.py          # Streamlit frontend
│   ├── config.toml               # Streamlit configuration
│   └── example_notes/            # Example clinical notes for demo
│       ├── ilaeclass1.txt
│       ├── ilaeclass2.txt
│       └── ilaeclass3.txt
├── scripts/
│   └── generate_clinic_notes.py  # Synthetic clinic note generator
├── tests/
│   ├── test_adk_agents.py        # ADK agent tests
│   └── test_gemini.py            # API verification test
├── data/
│   └── test_notes/               # Sample clinical notes (synthetic)
├── generated_notes/              # Generated synthetic notes
├── docs/                         # Documentation
├── .env                          # Environment variables (not in repo)
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
├── Dockerfile                    # Docker configuration
└── README.md                     # This file
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| **AI Framework** | [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) `>=0.3.0` |
| **LLM Model** | Gemini 3 Flash Preview |
| **Frontend** | Streamlit `>=1.40.0` |
| **Language** | Python 3.8+ |
| **Environment** | python-dotenv for secure API key handling |

### Key Dependencies

```
google-adk>=0.3.0
streamlit>=1.40.0
python-dotenv>=1.0.0
```

## Testing

The system includes **synthetically generated test clinical notes** in the `data/test_notes/` directory, representing various post-surgical outcomes and clinical scenarios. These notes are designed to simulate real-world inputs but **do not contain any Protected Health Information (PHI)**.

Example notes demonstrating different ILAE classes are available in `app/example_notes/` for demo purposes.

## Security Considerations

> **Important**: This system is **not HIPAA compliant**. Do not upload documents containing Protected Health Information (PHI).

- API keys are managed through environment variables (`.env` file)
- Never commit `.env` files to version control
- Streamlit Cloud secrets provide secure deployment options

## Limitations

- Requires high-quality clinical notes for accurate scoring
- LLM responses may vary slightly between runs
- System should be used as a support tool, not a replacement for clinical judgment
- Performance depends on the quality and completeness of input clinical notes
- May return "indeterminate" if key clinical information is missing from the note

## Contributing

Interested in contributing? Check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get started!

## Project History

This project originated as a proof-of-concept at the 2024 AI ATL Hackathon and has since undergone a complete architectural rewrite. The current implementation uses Google's Agent Development Kit with a multi-agent system, representing a fundamental redesign from the original NER/Knowledge Graph approach. See [CONTRIBUTING.md](CONTRIBUTING.md#project-history-and-contributors) for detailed project evolution and contributor information.

## Citation

The ILAE Outcome Scale used in this system is sourced from the Massachusetts General Hospital Epilepsy Service. For more information, visit their [Epilepsy Surgery Outcome Scales page](https://seizure.mgh.harvard.edu/engel-surgical-outcome-scale/).
