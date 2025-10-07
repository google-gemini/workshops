#!/usr/bin/env python3
"""
Merge PCG source files into final concept graph.

Usage:
    ./merge_pcg.py paip-chapter-1/raw/*.json > paip-chapter-1/concept-graph.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def load_json(filepath: str) -> Dict:
    """Load JSON file."""
    with open(filepath) as f:
        return json.load(f)


def find_pedagogy_for_concept(pedagogy_data: Dict, concept_id: str) -> Dict | None:
    """Find pedagogy enrichment for a concept."""
    for enriched in pedagogy_data.get('concepts_enriched', []):
        if enriched['id'] == concept_id:
            return enriched
    return None


def merge_concept_with_pedagogy(concept: Dict, pedagogy: Dict | None) -> Dict:
    """Merge base concept with pedagogy data."""
    merged = concept.copy()
    
    if pedagogy:
        # Add pedagogy fields (primary data)
        for key in ['learning_objectives', 'mastery_indicators', 'examples', 
                    'misconceptions', 'key_insights']:
            if key in pedagogy:
                merged[key] = pedagogy[key]
    
    return merged


def compute_edges_from_prerequisites(concepts: List[Dict]) -> List[Dict]:
    """DERIVE edges from concept prerequisites."""
    edges = []
    for concept in concepts:
        concept_id = concept['id']
        for prereq in concept.get('prerequisites', []):
            edges.append({
                'from': concept_id,
                'to': prereq,
                'type': 'requires'
            })
    return edges


def compute_roots(concepts: List[Dict]) -> List[str]:
    """DERIVE root concepts (no prerequisites)."""
    return [c['id'] for c in concepts if not c.get('prerequisites', [])]


def compute_concept_to_exercises(exercises: List[Dict]) -> Dict[str, List[str]]:
    """DERIVE mapping from concepts to exercises that test them."""
    mapping = {}
    for exercise in exercises:
        for test in exercise.get('tests_concepts', []):
            concept_id = test['concept_id']
            if concept_id not in mapping:
                mapping[concept_id] = []
            mapping[concept_id].append(exercise['id'])
    return mapping


def compute_statistics(concepts: List[Dict], exercises: List[Dict]) -> Dict:
    """DERIVE statistics about the concept graph."""
    difficulty_counts = {}
    for concept in concepts:
        diff = concept.get('difficulty', 'unknown')
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
    
    return {
        'total_concepts': len(concepts),
        'total_exercises': len(exercises),
        'difficulty_breakdown': difficulty_counts,
        'concepts_with_pedagogy': len([c for c in concepts if 'learning_objectives' in c]),
    }


def merge_pcg(*json_files: str) -> Dict:
    """
    Merge source files into final concept graph.
    
    Order-independent: accepts files in any order, extracts by key names.
    
    Primary data (from inputs):
    - Concept nodes (id, name, description, prerequisites, difficulty)
    - Pedagogy (learning_objectives, examples, misconceptions)
    - Exercises (full exercise definitions)
    
    Derived data (computed):
    - Edges (from prerequisites)
    - Roots (concepts with no prerequisites)
    - concept_to_exercises mapping
    - Statistics
    """
    # 1. Naively merge all files (last one wins on conflicts)
    merged = {}
    for filepath in json_files:
        data = load_json(filepath)
        merged.update(data)  # Simple dict merge
    
    # 2. Extract primary data by key (order-independent!)
    base_concepts = merged.get('nodes', [])
    enriched_pedagogy_list = merged.get('concepts_enriched', [])
    exercises = merged.get('exercises', [])
    
    # 3. Build pedagogy lookup for efficient access
    pedagogy_data = {'concepts_enriched': enriched_pedagogy_list}
    
    # 4. Enrich concepts with pedagogy (primary data merge)
    enriched_concepts = []
    for concept in base_concepts:
        pedagogy = find_pedagogy_for_concept(pedagogy_data, concept['id'])
        enriched = merge_concept_with_pedagogy(concept, pedagogy)
        enriched_concepts.append(enriched)
    
    # DERIVE all computed fields
    edges = compute_edges_from_prerequisites(enriched_concepts)
    roots = compute_roots(enriched_concepts)
    concept_to_exercises = compute_concept_to_exercises(exercises)
    stats = compute_statistics(enriched_concepts, exercises)
    
    # 5. Assemble final output (use metadata from merged dict)
    metadata = merged.get('metadata', {})
    return {
        'metadata': {
            'title': metadata.get('title', 'Unknown'),
            'source': metadata.get('source', 'Unknown'),
            'author': metadata.get('author', 'Unknown'),
            'description': f"Complete concept graph with {len(enriched_concepts)} concepts and {len(exercises)} exercises",
            'roots': roots,  # DERIVED
            'statistics': stats  # DERIVED
        },
        'concepts': enriched_concepts,  # PRIMARY + enriched
        'edges': edges,  # DERIVED
        'exercises': exercises,  # PRIMARY
        'concept_to_exercises': concept_to_exercises  # DERIVED
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: merge_pcg.py file1.json file2.json [file3.json ...]", file=sys.stderr)
        print("Example: merge_pcg.py raw/*.json > concept-graph.json", file=sys.stderr)
        sys.exit(1)
    
    json_files = sys.argv[1:]
    
    result = merge_pcg(*json_files)
    
    # Output to stdout (strict, pretty formatting)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
