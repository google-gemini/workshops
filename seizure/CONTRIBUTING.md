# Contributing to SeizureScoreAI

## Setup

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add your `GEMINI_API_KEY` to a `.env` file
4. Run: `streamlit run app/streamlit_app.py`

## Contributors

### AI ATL Hackathon Team

- **[Vineet Reddy](https://github.com/vineet-reddy):** Conceived the idea to analyze epilepsy clinic notes and output ILAE scores. Developed the original Named Entity Recognition (NER) system with Viresh Pati. (NER system now deprecated)
- **[Viresh Pati](https://github.com/vireshpati):** Co-designed the initial NER and designed the initial knowledge graph retrieval-augmented generation (KG RAG) system. (NER & KG RAG system now deprecated)
- **[Mukesh Paranthaman](https://github.com/MukProgram):** Co-built the backend for the original NER and KG RAG system. (NER & KG RAG system now deprecated)
- **[Sachi Goel](https://github.com/computer-s-2):** Designed the initial Streamlit frontend
- **[Ananda Badari](https://github.com/abadari3):**  Developed logic for predicting ILAE and Engel scores using knowledge graphs. (KG logic now deprecated)

### Post-Hackathon Development

- **[Vineet Reddy](https://github.com/vineet-reddy):** Complete rewrite using Google Agent Development Kit (ADK) with multi-agent architecture

---

**Citation:** The ILAE Outcome Scale is sourced from [MGH Epilepsy Service](https://seizure.mgh.harvard.edu/engel-surgical-outcome-scale/).
