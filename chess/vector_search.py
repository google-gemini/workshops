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

import json
import numpy as np
import asyncio
from typing import List, Dict, Tuple
from google import genai
from google.genai import types
import os
from dataclasses import dataclass

@dataclass
class SearchResult:
    position_id: int
    similarity: float
    fen: str
    description: str
    strategic_themes: List[str]
    tactical_elements: List[str]
    metadata: Dict
    full_position: Dict

class ChessVectorSearch:
    def __init__(self, embeddings_file: str = "chess_embeddings.json"):
        print(f"🔍 Loading chess embeddings from {embeddings_file}...")
        
        with open(embeddings_file, 'r') as f:
            self.embedding_db = json.load(f)
        
        # Convert embeddings to numpy arrays for faster computation
        self.embeddings_matrix = np.array([
            entry["embedding"] for entry in self.embedding_db
        ])
        
        print(f"   ✓ Loaded {len(self.embedding_db)} embeddings")
        print(f"   ✓ Embedding dimension: {self.embeddings_matrix.shape[1]}")
        
        # Configure Gemini for query embeddings (new API)
        if "GOOGLE_API_KEY" in os.environ:
            self.client = genai.Client()
    
    async def create_query_embedding(self, query_text: str) -> np.ndarray:
        """Create embedding for search query"""
        try:
            # Use new API (same as create_embeddings.py)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=[query_text],  # Note: contents expects a list
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
                )
            )
            return np.array(result.embeddings[0].values)
        except Exception as e:
            print(f"❌ Query embedding error: {e}")
            return None
    
    def cosine_similarity(self, query_embedding: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and all stored embeddings"""
        # Normalize embeddings
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        embeddings_norm = self.embeddings_matrix / np.linalg.norm(self.embeddings_matrix, axis=1, keepdims=True)
        
        # Calculate cosine similarity
        similarities = np.dot(embeddings_norm, query_norm)
        return similarities
    
    def filter_by_metadata(self, results: List[SearchResult], filters: Dict) -> List[SearchResult]:
        """Filter search results by metadata criteria"""
        filtered = []
        
        for result in results:
            include = True
            
            # Apply filters
            for key, value in filters.items():
                if key == "game_phase" and result.metadata.get("game_phase") != value:
                    include = False
                    break
                elif key == "to_move" and result.metadata.get("to_move") != value:
                    include = False
                    break
                elif key == "min_eval" and result.metadata.get("stockfish_eval", 0) < value:
                    include = False
                    break
                elif key == "max_eval" and result.metadata.get("stockfish_eval", 0) > value:
                    include = False
                    break
                elif key == "player" and value not in [result.metadata.get("white_player"), result.metadata.get("black_player")]:
                    include = False
                    break
                elif key == "strategic_themes" and not any(theme in result.strategic_themes for theme in value):
                    include = False
                    break
            
            if include:
                filtered.append(result)
        
        return filtered
    
    async def search(
        self, 
        query: str, 
        top_k: int = 10, 
        similarity_threshold: float = 0.5,
        filters: Dict = None
    ) -> List[SearchResult]:
        """Search for similar chess positions"""
        
        print(f"🔍 Searching for: '{query}'")
        
        # Create query embedding
        query_embedding = await self.create_query_embedding(query)
        if query_embedding is None:
            return []
        
        # Calculate similarities
        similarities = self.cosine_similarity(query_embedding)
        
        # Create results
        results = []
        for i, similarity in enumerate(similarities):
            if similarity >= similarity_threshold:
                db_entry = self.embedding_db[i]
                
                result = SearchResult(
                    position_id=db_entry["position_id"],
                    similarity=float(similarity),
                    fen=db_entry["metadata"]["fen"],
                    description=db_entry["full_position"]["enhanced_description"]["description"],
                    strategic_themes=db_entry["metadata"]["strategic_themes"],
                    tactical_elements=db_entry["metadata"]["tactical_elements"],
                    metadata=db_entry["metadata"],
                    full_position=db_entry["full_position"]
                )
                results.append(result)
        
        # Sort by similarity
        results.sort(key=lambda x: x.similarity, reverse=True)
        
        # Apply metadata filters
        if filters:
            results = self.filter_by_metadata(results, filters)
        
        # Return top results
        final_results = results[:top_k]
        
        print(f"   ✓ Found {len(final_results)} results (from {len(results)} above threshold)")
        
        return final_results
    
    def print_results(self, results: List[SearchResult]):
        """Pretty print search results"""
        for i, result in enumerate(results, 1):
            print(f"\n🏆 Result {i} (similarity: {result.similarity:.3f})")
            print(f"   Players: {result.metadata['white_player']} vs {result.metadata['black_player']}")
            print(f"   Phase: {result.metadata['game_phase']}, To move: {result.metadata['to_move']}")
            print(f"   Evaluation: {result.metadata['stockfish_eval']}")
            print(f"   Themes: {', '.join(result.strategic_themes)}")
            if result.tactical_elements:
                print(f"   Tactical: {', '.join(result.tactical_elements)}")
            print(f"   Description: {result.description[:200]}...")

# Test/Demo function
async def test_search():
    """Test the vector search functionality"""
    
    search_engine = ChessVectorSearch()
    
    # Test queries
    test_queries = [
        "kingside attack with piece activity",
        "endgame material advantage",
        "tactical threats and trapped pieces",
        "middlegame central control",
        "pawn storm counterplay"
    ]
    
    for query in test_queries:
        print("\n" + "="*60)
        results = await search_engine.search(query, top_k=3)
        search_engine.print_results(results)
        
        # Test with filters
        if results:
            print(f"\n🔍 Same query filtered to endgames:")
            filtered_results = await search_engine.search(
                query, 
                top_k=3,
                filters={"game_phase": "endgame"}
            )
            search_engine.print_results(filtered_results)

if __name__ == "__main__":
    asyncio.run(test_search())
