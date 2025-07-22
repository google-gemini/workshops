import base64
import json

from google import genai
from google.genai import types


def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks


def create_embeddings():
    client = genai.Client()

    # Read walkthrough
    with open("walkthrough.txt", "r") as f:
        text = f.read()

    # Split into chunks
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks")

    # Create embeddings
    embeddings_data = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}")

        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=chunk,
            config=types.EmbedContentConfig(task_type="retrieval_document"),
        )

        embeddings_data.append({"chunk_id": i, "text": chunk, "embedding": response.embeddings[0].values})

    # Save to file
    with open("walkthrough_embeddings.json", "w") as f:
        json.dump(embeddings_data, f)

    print("Embeddings saved!")


if __name__ == "__main__":
    create_embeddings()
