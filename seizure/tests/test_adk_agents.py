"""
Test for ADK multi-agent system.

Usage: python tests/test_adk_agents.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seizure_score_ai.agents import process_clinical_note


def test_basic_functionality():
    """Test that the ADK multi-agent pipeline works end-to-end."""
    
    # Simple test case: seizure-free patient
    clinical_note = """
    Patient post-surgery 12 months ago.
    Pre-surgery: 96 seizure days per year.
    Current: Completely seizure-free, no auras.
    """
    
    print("Testing ADK multi-agent system...")
    
    final, detailed = process_clinical_note(clinical_note)
    
    # Verify we got results
    assert 'ilae_score' in final, "Missing ILAE score"
    assert 'extracted_entities' in final, "Missing extracted entities"
    assert 'concise_explanation' in final, "Missing explanation"
    assert 'detailed_explanation' in detailed, "Missing detailed explanation"
    
    print(f"\nILAE Score: {final['ilae_score']}")
    print(f"Extracted {len(final['extracted_entities'])} entities")
    print("All tests passed!")


if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
