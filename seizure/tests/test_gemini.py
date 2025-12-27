"""Test script to verify Gemini API is working"""
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY not found in environment")
    exit(1)

print(f"API Key found!")

# Set up client
os.environ["GEMINI_API_KEY"] = api_key
client = genai.Client()

# Simple test
print("\nTesting Gemini 2.5 Flash API...")
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Write a one-sentence summary of what epilepsy is."
    )
    print("\nSUCCESS! API is working.")
    print(f"\nResponse: {response.text}")
except Exception as e:
    print(f"\nERROR: {e}")

