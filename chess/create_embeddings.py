# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List
from google import genai
from google.genai import types
import numpy as np


class ChessEmbeddingGenerator:

  def __init__(self):
    # Configure Gemini for embeddings
    if "GOOGLE_API_KEY" not in os.environ:
      raise ValueError("GOOGLE_API_KEY environment variable required")

    self.client = genai.Client()

  def create_embedding_text(self, position: dict) -> str:
    """Combine LLM analysis with human commentary for optimal search"""

    parts = []
    
    # Start with LLM systematic analysis
    enhanced_desc = position.get("enhanced_description", {})
    if enhanced_desc.get("description"):
        parts.append(enhanced_desc["description"])

    # Add human expert commentary when available
    human_commentary = position.get("human_commentary", {})
    if human_commentary.get("description"):
        parts.append(f"Expert insight: {human_commentary['description']}")

    # Add LLM structured elements as searchable keywords
    strategic_themes = enhanced_desc.get("strategic_themes", [])
    if strategic_themes:
      parts.append(f"Strategic themes: {', '.join(strategic_themes)}")

    tactical_elements = enhanced_desc.get("tactical_elements", [])
    if tactical_elements:
      parts.append(f"Tactical elements: {', '.join(tactical_elements)}")

    # Add human-extracted themes if available
    human_themes = human_commentary.get("strategic_themes", [])
    if human_themes and human_themes != strategic_themes:
      parts.append(f"Expert themes: {', '.join(human_themes)}")

    # Add key squares from both sources
    llm_squares = enhanced_desc.get("key_squares", [])
    human_squares = human_commentary.get("key_squares", [])
    all_squares = list(set(llm_squares + human_squares))
    if all_squares:
      parts.append(f"Key squares: {', '.join(all_squares)}")

    # Add some position facts for additional searchability
    features = position.get("position_features", {})
    if features.get("game_phase"):
      parts.append(f"Game phase: {features['game_phase']}")

    # Add opening if available
    context = position.get("game_context", {})
    if context.get("eco"):
      parts.append(f"Opening: {context['eco']}")

    return ". ".join(filter(None, parts))

  async def create_embeddings_batch(
      self, texts: List[str], batch_size: int = 100, max_concurrent: int = 20
  ) -> List[List[float]]:
    """Create embeddings using API batching for maximum speed"""
    
    # Split into batches for the API
    text_batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
    
    print(f"   Processing {len(texts)} texts in {len(text_batches)} batches of {batch_size}")
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch(batch_with_idx):
        batch, batch_idx = batch_with_idx
        async with semaphore:
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.client.models.embed_content(
                        model="gemini-embedding-001",
                        contents=batch,
                        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
                    )
                )
                return (batch_idx, [e.values for e in result.embeddings])
            except Exception as e:
                print(f"   ❌ Batch {batch_idx} error: {e}")
                return (batch_idx, [None] * len(batch))
    
    # Process all batches concurrently
    all_embeddings = [None] * len(texts)
    batch_tasks = [process_batch((batch, i)) for i, batch in enumerate(text_batches)]
    
    completed_batches = 0
    for task in asyncio.as_completed(batch_tasks):
        batch_idx, batch_embeddings = await task
        
        # Insert batch results into correct positions
        start_idx = batch_idx * batch_size
        for i, embedding in enumerate(batch_embeddings):
            if start_idx + i < len(all_embeddings):
                all_embeddings[start_idx + i] = embedding
        
        completed_batches += 1
        completed_texts = min(completed_batches * batch_size, len(texts))
        print(f"   Progress: {completed_texts}/{len(texts)} embeddings created ({completed_batches}/{len(text_batches)} batches)")
    
    return all_embeddings


async def create_chess_embeddings(
    input_file: str = "chess_database.json",
    output_file: str = "chess_embeddings.json",
):
  """Convert enhanced chess database to vector embeddings"""

  print("🎯 CREATING CHESS POSITION EMBEDDINGS")
  print("=" * 50)

  # Load enhanced database
  print(f"📚 Loading {input_file}")
  with open(input_file, "r") as f:
    positions = json.load(f)

  print(f"   ✓ Loaded {len(positions)} positions")

  # Filter to only positions with enhanced descriptions
  enhanced_positions = [
      pos
      for pos in positions
      if pos.get("enhanced_description", {}).get("description")
  ]

  print(
      f"   ✓ Found {len(enhanced_positions)} positions with enhanced"
      " descriptions"
  )

  if not enhanced_positions:
    print("   ❌ No enhanced descriptions found! Run build_database.py first.")
    return

  # Initialize embedding generator
  generator = ChessEmbeddingGenerator()

  # Create embedding texts
  print(f"\n📝 Preparing embedding texts...")
  embedding_texts = []
  for i, pos in enumerate(enhanced_positions):
    embedding_text = generator.create_embedding_text(pos)
    embedding_texts.append(embedding_text)

    if i < 3:  # Show samples
      print(f"   Sample {i+1}: {embedding_text[:100]}...")

  # Generate embeddings
  print(f"\n🤖 Generating embeddings with Gemini gemini-embedding-001...")
  embeddings = await generator.create_embeddings_batch(embedding_texts)

  # Count successful embeddings
  successful_embeddings = [e for e in embeddings if e is not None]
  failed_count = len(embeddings) - len(successful_embeddings)

  print(f"   ✓ Generated {len(successful_embeddings)} embeddings")
  if failed_count > 0:
    print(f"   ⚠️  {failed_count} embeddings failed")

  # Create embedding database
  print(f"\n💾 Creating searchable embedding database...")

  embedding_db = []
  for i, (pos, embedding) in enumerate(zip(enhanced_positions, embeddings)):
    if embedding is not None:
      embedding_entry = {
          # Unique identifier
          "position_id": i,
          # Embedding vector
          "embedding": embedding,
          # Text that was embedded (for reference)
          "embedding_text": embedding_texts[i],
          # Chess-specific metadata for filtering
          "metadata": {
              "fen": pos.get("fen"),
              "game_phase": pos.get("position_features", {}).get("game_phase"),
              "to_move": pos.get("position_features", {}).get("to_move"),
              "material_balance": (
                  pos.get("position_features", {})
                  .get("material", {})
                  .get("balance", 0)
              ),
              "white_player": pos.get("game_context", {}).get("white_player"),
              "black_player": pos.get("game_context", {}).get("black_player"),
              "eco": pos.get("game_context", {}).get("eco"),
              "year": (
                  pos.get("game_context", {}).get("date", "")[:4]
                  if pos.get("game_context", {}).get("date")
                  else None
              ),
              "stockfish_eval": (
                  pos.get("stockfish_analysis", {}).get("evaluation", 0)
              ),
              "strategic_themes": (
                  pos.get("enhanced_description", {}).get(
                      "strategic_themes", []
                  )
              ),
              "tactical_elements": (
                  pos.get("enhanced_description", {}).get(
                      "tactical_elements", []
                  )
              ),
              "has_human_commentary": bool(pos.get("human_commentary")),
              "commentary_source": pos.get("human_commentary", {}).get("source"),
              "human_themes": pos.get("human_commentary", {}).get("strategic_themes", []),
          },
          # Full position data (for detailed analysis)
          "full_position": pos,
      }

      embedding_db.append(embedding_entry)

  # Save embedding database
  print(f"💾 Saving embedding database to {output_file}")
  with open(output_file, "w") as f:
    # Use compact JSON to save space since embeddings are large
    json.dump(embedding_db, f, separators=(",", ":"))

  # Calculate stats
  total_positions = len(positions)
  enhanced_positions_count = len(enhanced_positions)
  successful_embeddings_count = len(embedding_db)

  # Estimate embedding dimensions
  embedding_dim = len(embedding_db[0]["embedding"]) if embedding_db else 0

  print(f"\n🎉 EMBEDDING CREATION COMPLETE!")
  print(f"✓ Total positions in database: {total_positions:,}")
  print(f"✓ Positions with enhanced descriptions: {enhanced_positions_count:,}")
  print(f"✓ Successful embeddings created: {successful_embeddings_count:,}")
  print(f"✓ Embedding dimension: {embedding_dim}")
  print(
      f"✓ Database size: ~{len(json.dumps(embedding_db)) / 1024 / 1024:.1f} MB"
  )
  print(f"✓ Ready for similarity search!")


if __name__ == "__main__":
  asyncio.run(create_chess_embeddings(
    input_file="nakamura_carlsen_comprehensive.json",
    output_file="nakamura_carlsen_embeddings.json"
  ))
