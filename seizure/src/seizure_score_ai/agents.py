"""
Multi-Agent Clinical Reasoning System using Google Agent Development Kit (ADK)

This module implements a three-agent pipeline using Google's ADK framework for 
processing clinical notes and calculating ILAE outcome scores.

Architecture:
    Agent 1: Clinical Information Extractor → extracts structured data
    Agent 2: ILAE Score Calculator → calculates outcome score
    Agent 3: Concise Explanation Reporter → generates user-friendly summary
"""

from google.adk import Runner
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.genai import types
import os
from dotenv import load_dotenv
import json
import uuid
import asyncio
import re
from typing import Dict, Tuple

# Load environment variables
load_dotenv(verbose=True)
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    os.environ["GEMINI_API_KEY"] = api_key

GEMINI_MODEL = "gemini-3-flash-preview"


def run_agent(agent: LlmAgent, prompt: str, app_name: str) -> str:
    """
    Run an ADK agent with a prompt and return the response.
    
    Args:
        agent: The LlmAgent to run
        prompt: The text prompt
        app_name: Application name for session
        
    Returns:
        The agent's response as a string
    """
    session_service = InMemorySessionService()
    session_id = str(uuid.uuid4())
    user_id = "default_user"
    
    # Create session and runner
    asyncio.run(session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id))
    runner = Runner(app_name=app_name, agent=agent, session_service=session_service)
    
    # Create message and run agent
    message = types.Content(parts=[types.Part(text=prompt)], role="user")
    
    # Collect response from event stream
    response_text = ""
    for event in runner.run(user_id=user_id, session_id=session_id, new_message=message):
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text
    
    return response_text


def create_clinical_extractor_agent() -> LlmAgent:
    """Creates the Clinical Information Extractor agent."""
    
    instruction = """You are a clinical information extractor. Extract these entities from the clinical note:

1. **Presence of seizure freedom** (Yes/No/I don't know)
2. **Presence of auras** (Yes/No/I don't know)
3. **Baseline seizure days (pre-treatment)** (Numeric value or "I don't know")
4. **Seizure days per year (post-treatment)** (Numeric value or "I don't know")

For each entity, provide the value and exact supporting text from the note.

**Output only valid JSON in this format:**

{
  "presence_of_seizure_freedom": {
    "value": "...",
    "supporting_text": "..."
  },
  "presence_of_auras": {
    "value": "...",
    "supporting_text": "..."
  },
  "baseline_seizure_days": {
    "value": "...",
    "supporting_text": "..."
  },
  "seizure_days_per_year": {
    "value": "...",
    "supporting_text": "..."
  }
}"""

    return LlmAgent(
        name="ClinicalInformationExtractor",
        model=GEMINI_MODEL,
        instruction=instruction,
        description="Extracts structured clinical information from patient notes"
    )


def create_ilae_calculator_agent() -> LlmAgent:
    """Creates the ILAE Score Calculator agent."""
    
    instruction = """You are a medical expert specializing in epilepsy. Calculate the ILAE score using these criteria:

**ILAE Outcome Scale:**
- **Class 1**: Completely seizure free; no auras
- **Class 2**: Only auras; no other seizures
- **Class 3**: 1 to 3 seizure days per year; ± auras
- **Class 4**: 4 seizure days per year to 50% reduction of baseline seizure days; ± auras
- **Class 5**: Less than 50% reduction of baseline seizure days; ± auras
- **Class 6**: More than 100% increase of baseline seizure days; ± auras

Provide detailed reasoning citing the supporting texts. If you cannot determine the score, set "ilae_score" to "indeterminate".

**Output only valid JSON in this format:**

{
  "ilae_score": "...",
  "detailed_explanation": "..."
}"""

    return LlmAgent(
        name="ILAEScoreCalculator",
        model=GEMINI_MODEL,
        instruction=instruction,
        description="Calculates ILAE outcome scores based on clinical data"
    )


def create_concise_reporter_agent() -> LlmAgent:
    """Creates the Concise Explanation Reporter agent."""
    
    instruction = """Summarize the detailed ILAE explanation into a clear, concise summary for the frontend.

**Output only valid JSON in this format:**

{
  "concise_explanation": "..."
}"""

    return LlmAgent(
        name="ConciseExplanationReporter",
        model=GEMINI_MODEL,
        instruction=instruction,
        description="Generates concise explanations of ILAE scores"
    )


def parse_json_response(response_text: str) -> Dict:
    """Parse JSON from agent response, handling potential formatting issues."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError("Could not parse response as JSON")


def process_clinical_note(clinical_note: str) -> Tuple[Dict, Dict]:
    """
    Process a clinical note through the ADK multi-agent pipeline.
    
    Args:
        clinical_note: Raw clinical note text
        
    Returns:
        Tuple of (final_output, detailed_output) where:
        - final_output contains: ilae_score, concise_explanation, extracted_entities
        - detailed_output contains: detailed_explanation
    """
    
    print("Initializing ADK multi-agent system...")
    
    # Step 1: Extract clinical information
    print("Step 1: Clinical Information Extraction...")
    extractor = create_clinical_extractor_agent()
    extraction_response = run_agent(
        extractor, 
        f"Extract clinical information from this note:\n\n{clinical_note}",
        app_name="ClinicalExtractor"
    )
    extracted_entities = parse_json_response(extraction_response)
    
    # Calculate percent reduction for context
    baseline = extracted_entities['baseline_seizure_days']['value']
    post = extracted_entities['seizure_days_per_year']['value']
    
    try:
        if str(baseline).lower() == "i don't know" or str(post).lower() == "i don't know":
            percent_reduction = "I don't know"
        else:
            baseline_val = float(baseline)
            post_val = float(post)
            percent_reduction = ((baseline_val - post_val) / baseline_val) * 100 if baseline_val > 0 else 0
    except (ValueError, TypeError):
        percent_reduction = "I don't know"
    
    # Step 2: Calculate ILAE score
    print("Step 2: ILAE Score Calculation...")
    calculator = create_ilae_calculator_agent()
    calculation_prompt = f"""Calculate the ILAE score using this information:

**Extracted Entities and Supporting Texts:**
1. Presence of seizure freedom: {extracted_entities['presence_of_seizure_freedom']['value']}
   - Supporting text: {extracted_entities['presence_of_seizure_freedom']['supporting_text']}
2. Presence of auras: {extracted_entities['presence_of_auras']['value']}
   - Supporting text: {extracted_entities['presence_of_auras']['supporting_text']}
3. Baseline seizure days: {baseline}
   - Supporting text: {extracted_entities['baseline_seizure_days']['supporting_text']}
4. Seizure days per year: {post}
   - Supporting text: {extracted_entities['seizure_days_per_year']['supporting_text']}
5. Percent reduction: {percent_reduction}

Calculate the ILAE score."""
    
    calculation_response = run_agent(calculator, calculation_prompt, app_name="ILAECalculator")
    ilae_result = parse_json_response(calculation_response)
    
    # Step 3: Generate concise explanation
    print("Step 3: Generating Concise Explanation...")
    reporter = create_concise_reporter_agent()
    concise_response = run_agent(
        reporter,
        f"Summarize this detailed explanation:\n\n{ilae_result['detailed_explanation']}",
        app_name="ConciseReporter"
    )
    concise_result = parse_json_response(concise_response)
    
    # Prepare final outputs
    final_output = {
        "ilae_score": ilae_result['ilae_score'],
        "concise_explanation": concise_result['concise_explanation'],
        "extracted_entities": extracted_entities
    }
    
    detailed_output = {
        "detailed_explanation": ilae_result['detailed_explanation']
    }
    
    print("ADK multi-agent processing complete!")
    return final_output, detailed_output
