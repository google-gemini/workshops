# Little Schemer Dialectic Project - Complete Design Summary

## Project Overview
**Goal:** Convert any educational artifact (Python notebooks, text, etc.) into an interactive Little Schemer-style dialectic - a Socratic Q&A teaching system.

**Key Collaborators:** User and Peter Norvig  
**Core Insight:** Every educational text has an implicit Pedagogical Concept Graph (PCG). Extract it well, and dialectic generation becomes straightforward.

---

## Architecture: Three-Phase System

### **STEP ZERO: PCG Extraction** ← THE CORE INNOVATION
Extract the hidden concept graph from source materials. This is the hard problem that makes everything else possible.

### **Step 1: Interactive Graph UI**
Visualize the PCG and allow user navigation through concepts.

### **Step 2: Dialectic Generation**
Generate Little Schemer-style Q&A conversations from the PCG.

---

## The Pedagogical Concept Graph (PCG)

### Definition
A directed acyclic graph (DAG) where:
- **Nodes** = Concepts (skills, ideas, techniques)
- **Edges** = Prerequisite relationships ("A requires B")
- **Properties** = Learning objectives, examples, mastery criteria, misconceptions

### Key Insight
**PCG is a projection of a full knowledge graph**, focusing specifically on the "requires" relationship. Other relationships (contrasts_with, example_of, generalizes_to) enrich the dialectic but don't affect teaching order.

### Structure
```python
PCG = {
    "nodes": [
        {
            "id": "concept_name",
            "description": "Brief explanation",
            "prerequisites": ["concept_a", "concept_b"],  # Creates edges
            
            # Learning design
            "learning_objectives": [
                "Read and understand X",
                "Write basic X",
                "Apply X to novel problems"
            ],
            
            # Assessment
            "mastery_indicators": [
                {
                    "skill": "syntax_recognition",
                    "description": "Can identify structure",
                    "difficulty": "basic",  # basic/intermediate/advanced
                    "test_method": "Show example, ask to identify parts"
                }
            ],
            
            # Content
            "examples": [
                {
                    "content": "[x**2 for x in range(10)]",
                    "explanation": "Creates list of squares",
                    "when_to_show": "first_introduction"
                }
            ],
            
            # Common issues
            "misconceptions": [
                "Students think variable leaks outside comprehension"
            ],
            
            # Metadata
            "difficulty": "intermediate",
            "estimated_time_minutes": 15,
            
            # Optional: Other pedagogical relationships
            "pedagogical_relations": {
                "syntactic_sugar_for": ["for_loop_with_append"],
                "contrasts_with": ["map_function"],
                "generalizes_to": ["generator_expression"]
            }
        }
    ],
    "edges": [
        {"from": "list_comprehension", "to": "for_loop", "type": "requires"}
    ]
}
```

---

## PCG Extraction Pipeline (Multi-Pass)

### Pass 0: Semantic Chunking (LLM-Based)
**Problem:** Can't extract line-by-line (loses context) or by fixed paragraphs (breaks semantic units).

**Solution:** Use LLM to identify semantic boundaries.

```python
def llm_semantic_chunk(document):
    """
    LLM determines where semantic teaching units begin/end.
    Keeps explanations with examples, code with context.
    """
    
    # For notebooks: Show cell structure
    # For text: Show headings/structure as hint
    
    prompt = """
    Chunk this educational material into semantic teaching units.
    Each chunk should be a complete "teachable concept".
    
    Rules:
    - Keep explanations with their examples
    - Keep code with surrounding context
    - Don't split in middle of example
    - A chunk might be 1-5 paragraphs depending on completeness
    
    Return: List of chunks with boundaries and rationale
    """
    
    return llm.extract_structured(prompt)
```

**Adaptive Strategy:**
- **Short documents (<8k tokens):** Full document at once
- **Medium (8-20k):** Hierarchical - identify sections, then chunk each section
- **Long (>20k):** Hierarchical + streaming with sliding window

### Pass 1: Extract Structure
**Focus:** Concepts, dependencies, relationships

```python
def pass1_extract_structure(chunks, global_context):
    """
    Extract concepts and prerequisite relationships.
    This forms the DAG structure.
    """
    
    pcg = PedagogicalConceptGraph()
    
    for i, chunk in enumerate(chunks):
        context = {
            "global_summary": global_context.summary,
            "concepts_so_far": [c.name for c in pcg.concepts],
            "previous_chunk": chunks[i-1] if i > 0 else None,
            "current_chunk": chunk,
            "next_chunk": chunks[i+1] if i < len(chunks)-1 else None
        }
        
        prompt = f"""
        Extract concepts from this chunk with sliding window context.
        
        Focus ONLY on structure:
        1. Concept name and brief description
        2. Prerequisites (MANDATORY - what MUST be understood first?)
        3. Pedagogical relationships (optional: contrasts_with, generalizes_to, etc.)
        4. Difficulty estimate
        
        Don't worry about examples or assessment yet.
        
        Context: {context}
        """
        
        concepts = llm.extract_concepts(prompt)
        pcg.add_concepts(concepts)
    
    # Validate: Must be DAG, no cycles
    assert is_dag(pcg)
    
    return pcg
```

### Pass 2: Extract Mastery Criteria
**Focus:** Learning objectives, assessment design, examples

```python
def pass2_extract_mastery_criteria(pcg, chunks):
    """
    Now that we have concept structure, design assessment.
    """
    
    for concept in pcg.concepts:
        relevant_chunks = find_chunks_mentioning(concept, chunks)
        
        prompt = f"""
        You previously identified this concept:
        - Name: {concept.name}
        - Prerequisites: {concept.prerequisites}
        
        Source material:
        {relevant_chunks}
        
        Design mastery assessment:
        
        1. LEARNING OBJECTIVES: What should student DO? (concrete, measurable)
        2. MASTERY INDICATORS: How to test each skill? (with difficulty levels)
        3. EXAMPLES: Best examples to illustrate concept
        4. MISCONCEPTIONS: Common student errors
        
        Think like a teacher designing an assessment.
        """
        
        criteria = llm.extract_mastery(prompt)
        concept.add_criteria(criteria)
    
    return pcg
```

### Pass 3: Global Validation & Refinement (Optional)
- Check for concept redundancy/overlap
- Validate prerequisite chains make sense
- Ensure coverage (all material concepts extracted)
- Fill gaps (missing examples, unclear objectives)

---

## Context Management for Extraction

### Hierarchical Context
```
┌─ Global Context (always present)
│   ├─ Document summary
│   ├─ Main topics covered
│   └─ Target audience/assumed knowledge
│
├─ Sliding Window (current focus)
│   ├─ Previous chunk (what came before)
│   ├─ Current chunk (extract from here)
│   └─ Next chunk (look-ahead context)
│
└─ Accumulating State
    └─ Concepts identified so far (avoid duplication)
```

This ensures:
- LLM understands "as we saw earlier" references
- LLM can anticipate "as we'll see later" forward refs
- Dependencies reference already-extracted concepts
- No duplicate concept extraction

---

## Mastery Assessment System

### How Mastery Works

**Extracted during PCG creation:**
```python
concept.mastery_indicators = [
    {
        "skill": "syntax_recognition",
        "difficulty": "basic",
        "test": "Can identify [expr for var in iterable] structure"
    },
    {
        "skill": "generation",
        "difficulty": "intermediate", 
        "test": "Can write comprehension for novel problem"
    }
]
```

**Tracked during dialectic:**
```python
mastery_tracker = {
    "syntax_recognition": 0.0,  # Confidence 0.0-1.0
    "generation": 0.0,
    "filtering": 0.0
}

# After each student response
evaluation = llm.evaluate_response(question, response, concept)
# Returns evidence for each skill (0.0-1.0)

# Update tracker
for skill, evidence in evaluation.skill_evidence.items():
    mastery_tracker[skill] = update_confidence(
        current=mastery_tracker[skill],
        evidence=evidence
    )
```

**Mastery threshold:**
- All basic skills ≥ 0.8
- Most intermediate skills ≥ 0.7
- Some evidence of advanced skills ≥ 0.6

**Key insight:** LLM evaluates responses against extracted mastery indicators, providing structured evidence for each skill demonstrated.

---

## User Interface: Graph as First-Class Feature

### The Graph IS the Interface

**Three-panel layout:**
```
┌──────────┬────────────────┬───────────┐
│  Concept │   Dialectic    │  Context  │
│  Graph   │   (main area)  │   Panel   │
│  (mini)  │                │           │
│          │  Q: What does  │ Progress: │
│  [●]→[⟳] │     [x**2 for  │ Learning: │
│   ↓      │     x in ...]  │ list comp │
│  [⚬][🔒] │     return?    │           │
│          │                │ 2/4 skills│
│          │  A: [Student   │ mastered  │
│          │     types...]  │           │
└──────────┴────────────────┴───────────┘

Legend:
● Mastered  ⟳ Learning  ⚬ Ready  🔒 Locked
```

### Entry Modes

**1. Guided Tour (Beginners)**
- Start at nodes with no prerequisites (graph roots)
- Linear progression through topologically-sorted concepts
- System chooses path

**2. Goal-Directed (Motivated Learners)**
```
User: "I want to learn decorators"
System: Analyzes graph, finds: 
  decorators ← closures ← functions ← variables
System: "You know functions. Let's learn closures next."
Shows path, starts dialectic
```

**3. Free Exploration (Advanced)**
```
User: Clicks on graph node
System: Checks prerequisites
  ✓ Met → "Let's begin!"
  ✗ Missing → "First learn: X, Y, Z"
```

### Knowledge Frontier

**Key UX concept:**
```python
def get_frontier(user_state, pcg):
    """Concepts user is ready to learn"""
    return [
        concept for concept in pcg.nodes
        if concept.id not in user_state.mastered
        and all(prereq in user_state.mastered 
                for prereq in concept.prerequisites)
    ]
```

**On app open:**
```
"Welcome back! You've mastered: [list of 4 concepts]

Ready to learn:
→ For-loops (builds on: lists, iteration)
→ Closures (builds on: functions, scope)

Which interests you?"
```

### Graph Interactions

**Click behaviors:**
- **Mastered node (●):** Review via abbreviated dialectic
- **Learning node (⟳):** Continue where left off
- **Ready node (⚬):** Begin dialectic
- **Locked node (🔒):** Show prerequisite path to unlock

**Visual features:**
- Highlight path from current to goal
- Show estimated time to complete
- Display difficulty progression
- Cluster related concepts

---

## Dialectic Generation (The "Easy" Part)

**Once you have a good PCG, dialectic is almost mechanical:**

```python
def generate_dialectic(concept, student_state):
    """
    Generate Little Schemer-style Q&A for a concept.
    """
    
    # Initialize mastery tracker
    tracker = {
        indicator.skill: 0.0 
        for indicator in concept.mastery_indicators
    }
    
    dialogue = []
    
    while not is_mastery_achieved(tracker):
        # Find weakest skill
        weakest = min(tracker.items(), key=lambda x: x[1])
        
        # Generate question targeting that skill
        question = llm.generate_question(
            concept=concept,
            target_skill=weakest[0],
            examples=concept.examples,
            misconceptions=concept.misconceptions,
            dialogue_history=dialogue[-3:],  # Recent context
            style="little_schemer"  # Small incremental steps
        )
        
        # Get student response
        response = await get_student_response(question)
        
        # Evaluate against mastery indicators
        evaluation = llm.evaluate_response(
            question=question,
            response=response,
            concept=concept,
            mastery_indicators=concept.mastery_indicators
        )
        
        # Update tracker
        for skill, evidence in evaluation.skill_evidence.items():
            tracker[skill] = update_confidence(tracker[skill], evidence)
        
        dialogue.append((question, response, evaluation))
    
    # Mark concept as mastered
    student_state.mastered.add(concept.id)
    
    return dialogue
```

### Little Schemer Style Guidelines

**For question generation:**
- Small incremental steps
- Concrete examples, not abstract theory
- Build on previous answers
- Anticipate wrong answers, correct gently
- Use repetition to reinforce
- Reference earlier "commandments" or principles
- Simple language, clear questions

**Example progression:**
```
Q: What does [x**2 for x in range(5)] create?
A: [0, 1, 4, 9, 16]

Q: Good! And if we wanted cubes instead?
A: [x**3 for x in range(5)]

Q: Excellent. Now only even squares?
A: [x**2 for x in range(5) if x % 2 == 0]
```

---

## Technical Considerations

### Typesetting (Important to Peter)
- Web-based, interactive
- **Markdown** with **MathJax** for math
- Syntax-highlighted code rendering
- Clean, serif aesthetic inspired by Little Schemer
- **Validation layer:** Check all markdown elements closed, LaTeX well-formed
- Consider template-based generation to enforce correctness

### Technology Stack Suggestions
- **LLM:** Claude or GPT-4 for extraction and dialogue
- **Graph:** NetworkX or similar for PCG structure
- **Frontend:** React/Vue with graph visualization (D3.js, Cytoscape.js)
- **Markdown:** Marked.js + MathJax + Prism.js for code
- **State:** Local storage or lightweight backend for progress tracking

### Cost/Performance
- PCG extraction: One-time cost per artifact
- Multi-pass adds API calls but improves quality
- Consider caching extracted PCGs
- Dialectic generation: Interactive, needs fast response

---

## Implementation Phases

### **Phase 0: PCG Extraction (FOCUS HERE FIRST)**
**Goal:** Prove you can reliably extract high-quality concept graphs

**Week 1-2: Semantic Chunking**
- Implement LLM-based chunking
- Test on sample notebook
- Validate chunk boundaries make sense

**Week 3-4: Multi-Pass Extraction**
- Pass 1: Structure (concepts + prerequisites)
- Pass 2: Mastery criteria
- Validate: Is it a DAG? Are dependencies logical?

**Week 5-6: Human Validation**
- Show extracted PCG to Peter Norvig
- Compare against hand-crafted graph
- Iterate on prompts based on feedback
- **This validates the core hypothesis**

### **Phase 1: Minimal Dialectic Prototype**
**Goal:** Prove good PCG → working dialectic

**Week 7:**
- Simple question generation from objectives
- Basic response evaluation
- Mastery tracking

**Week 8:**
- Test on one concept end-to-end
- Validate: Does it feel like Little Schemer?
- Get feedback from Peter

### **Phase 2: Graph UI**
**Goal:** Make PCG navigable and visible

**Week 9:**
- Interactive graph visualization
- Node states (mastered/learning/ready/locked)
- Click to navigate
- Progress tracking

**Week 10:**
- Three-panel layout
- Entry mode selection (guided/goal-directed/exploration)
- Knowledge frontier display
- Path highlighting

### **Phase 3: Polish & Rich Features**

**Week 11:**
- Typesetting improvements (markdown validation)
- Examples rendering (code highlighting)
- Adaptive pacing (faster if student excels)
- Review mode (revisit mastered concepts)

**Week 12:**
- Multi-artifact support
- Export/share progress
- Analytics (which concepts take longest?)
- Performance optimization

---

## Validation Criteria

### PCG Quality Metrics

**Structural:**
```python
def validate_pcg(pcg):
    # Must be DAG
    assert is_dag(pcg), "Contains cycles"
    
    # All nodes reachable from roots
    assert is_connected(pcg), "Orphaned concepts"
    
    # Prerequisites reference existing concepts
    assert valid_references(pcg), "Dangling prerequisites"
    
    # Reasonable size (not too granular/coarse)
    assert 5 <= len(pcg.nodes) <= 100, "Unusual concept count"
```

**Pedagogical:**
```python
def validate_pedagogy(pcg):
    # Every concept has assessment
    for concept in pcg.nodes:
        assert concept.mastery_indicators, f"{concept} missing assessment"
        assert concept.learning_objectives, f"{concept} missing objectives"
        assert concept.examples, f"{concept} missing examples"
    
    # Difficulty progression makes sense
    for edge in pcg.edges:
        prereq = pcg.get_node(edge.to)
        concept = pcg.get_node(edge.from)
        assert prereq.difficulty <= concept.difficulty, \
            f"{concept} easier than prerequisite {prereq}"
```

**Coverage:**
```python
def validate_coverage(pcg, source_material):
    # Extract all technical terms from source
    terms_in_source = extract_technical_terms(source_material)
    
    # Check coverage
    terms_in_pcg = {c.name for c in pcg.nodes}
    
    coverage = len(terms_in_pcg & terms_in_source) / len(terms_in_source)
    assert coverage > 0.8, f"Only {coverage:.0%} coverage"
    
    # Report missing
    missing = terms_in_source - terms_in_pcg
    if missing:
        print(f"Potentially missed concepts: {missing}")
```

**Human Validation (Gold Standard):**
- Show graph to Peter Norvig
- Ask: "Are dependencies correct?"
- Ask: "Are any concepts missing?"
- Ask: "Is granularity appropriate?"
- Ask: "Would this teaching order work?"

---

## Key Design Decisions Summary

### 1. **PCG is the Core**
- Not just infrastructure - it's the product
- Everything else derives from a good PCG
- Invest heavily in extraction quality

### 2. **Multi-Pass Extraction**
- Pass 1: Structure (concepts + dependencies)
- Pass 2: Mastery criteria (objectives + assessment)
- Why: Different cognitive tasks, better quality
- Alternative: Single-pass with structured output (fallback if multi-pass too slow)

### 3. **LLM-Based Semantic Chunking**
- Don't use brittle heuristics
- Let LLM determine semantic boundaries
- Works across different artifact types
- Use hierarchical approach for long documents

### 4. **Sliding Window Context**
- Previous chunk + current + next chunk
- Plus global document summary
- Plus concepts identified so far
- Handles forward/backward references

### 5. **Graph as First-Class UI**
- Users see and interact with PCG
- Multiple entry modes (guided/goal/exploration)
- Knowledge frontier shows what's accessible
- Visual progress tracking

### 6. **Mastery via LLM Evaluation**
- Extract mastery indicators during PCG creation
- LLM evaluates responses against indicators
- Track confidence per skill (0.0-1.0)
- Threshold-based mastery detection
- Allow "move on anyway" option

### 7. **Dialectic is Mechanical**
- Given good PCG, question generation is straightforward
- Target weakest skills
- Use extracted examples
- Watch for extracted misconceptions
- Little Schemer style: small steps, concrete examples

---

## Critical Success Factors

### 1. **PCG Extraction Quality**
This is THE bottleneck. If extraction is poor, everything downstream suffers.

**Focus on:**
- Accurate prerequisites (DAG structure)
- Appropriate granularity (not too fine/coarse)
- Complete coverage (don't miss concepts)
- Good examples (actual examples from material)
- Realistic mastery criteria (skills that matter)

### 2. **Peter's Validation**
His experience in teaching and curriculum design is invaluable.

**Get feedback on:**
- Are extracted dependencies correct?
- Is concept granularity right?
- Are mastery indicators meaningful?
- Does teaching order make sense?

### 3. **Start Small, Validate Early**
Don't build full system before validating PCG extraction.

**Milestone sequence:**
1. Extract PCG from one notebook → validate structure
2. Hand-craft dialectic from PCG → prove concept
3. Auto-generate dialectic → validate quality
4. Build UI → polish experience

---

## Open Questions / Future Exploration

### 1. **Optimal Chunking Strategy**
- Full document vs hierarchical vs streaming?
- Test empirically with different document sizes
- May need adaptive strategy

### 2. **Single-Pass vs Multi-Pass Extraction**
- Multi-pass seems better (different cognitive tasks)
- But single-pass might be "good enough"
- Test both, compare quality vs cost

### 3. **Mastery Threshold Calibration**
- What confidence level = "mastered"?
- Should it vary by difficulty?
- Can we learn optimal thresholds over time?

### 4. **Concept Granularity**
- What's the right size for a "concept"?
- Too fine: overwhelming, too many nodes
- Too coarse: hard to assess mastery
- May need heuristics or LLM judgment

### 5. **Multi-Modal Extensions**
- Audio dialectic (TTS + STT)
- Visual dialectic (diagrams, animations)
- Embedded programs (live coding)
- These are Phase 4+, but PCG should support them

---

## Example Prompt Templates

### Semantic Chunking Prompt
```
You are chunking educational material into semantic teaching units.
Each chunk should be a complete "teachable concept" including 
explanation, examples, and related code.

Document structure:
[provide headings/cells as hint]

Full content:
[document text]

Return a list of chunks with:
- start/end identifiers
- brief concept description
- rationale for boundaries

Rules:
- Keep explanations with examples
- Keep code with surrounding context
- Don't split mid-example
- Chunk size: 1-5 paragraphs depending on semantic completeness
```

### Structure Extraction Prompt (Pass 1)
```
Extract concepts and dependencies from this educational material.
Focus ONLY on structure.

Global context: [document summary]
Concepts identified so far: [list]

Previous chunk: [text]
Current chunk: [text]  ← EXTRACT FROM HERE
Next chunk: [text]

For each concept identify:
1. Name and brief description
2. Prerequisites (MANDATORY - what MUST be understood first?)
3. Pedagogical relationships (contrasts_with, generalizes_to, etc.)
4. Difficulty level (basic/intermediate/advanced)

Return structured JSON.
```

### Mastery Criteria Prompt (Pass 2)
```
Design mastery assessment for this concept.

Concept: [name]
Description: [text]
Prerequisites: [list]

Source material where it appears:
[relevant chunks]

Generate:

1. LEARNING OBJECTIVES (what should student DO?):
   - Concrete, measurable actions
   - Not just "understand"

2. MASTERY INDICATORS (how to test?):
   - Specific testable skills
   - Difficulty level (basic/intermediate/advanced)
   - Method to test each skill

3. EXAMPLES (best illustrations):
   - Most clear example for introduction
   - Edge cases or variations
   - When to show each

4. MISCONCEPTIONS (common errors):
   - What do students typically get wrong?
   - Why might they make this mistake?

Think like a teacher designing an assessment.
Return structured JSON.
```

### Question Generation Prompt (During Dialectic)
```
Generate the next Little Schemer-style question.

Concept: [name]
Current mastery levels: [tracker dict]
Weakest skill: [skill name] (confidence: [0.0-1.0])

Examples available: [list from concept]
Common misconceptions: [list from concept]

Recent dialogue:
[last 3 Q&A pairs]

Generate a question that:
1. Probes [weakest skill]
2. Builds on what student has shown they understand
3. Uses Little Schemer style (small incremental step)
4. Uses concrete examples, not abstract explanation
5. Anticipates wrong answers and corrects gently

Return: question text + optional hint if they struggle
```

### Response Evaluation Prompt
```
Evaluate student's response for mastery evidence.

Concept: [name]
Mastery indicators: [list with skills and difficulty]

Question: [text]
Student response: [text]

Evaluate:
1. Is response correct? (yes/no/partial)
2. What does it reveal about understanding?
3. Which mastery indicators does it demonstrate?
   - For each: evidence strength (0.0-1.0)
4. Any misconceptions revealed?
5. What should we probe next?

Return structured evaluation JSON.
```

---

## Success Metrics

### PCG Quality (Automated)
- Is DAG: ✓/✗
- Concepts have prerequisites: X%
- Concepts have mastery indicators: X%
- Concepts have examples: X%
- Coverage of source material: X%

### PCG Quality (Human Eval)
- Expert rates dependency accuracy: 1-5
- Expert rates concept granularity: 1-5
- Expert rates teaching order: 1-5
- Expert would use this graph: Y/N

### Dialectic Quality
- Students complete concepts: X%
- Time to mastery: X minutes (compare to baseline)
- Student satisfaction: 1-5
- Mastery retained after 1 week: X%

### System Usage
- Concepts mastered per session: X
- Return rate: X%
- Completion rate: X%
- User would recommend: Y/N

---

## Resources for Implementation

### LLM APIs
- OpenAI GPT-4 / Claude 3.5 Sonnet
- Consider function calling for structured extraction
- Use JSON schema validation

### Graph Libraries
- NetworkX (Python) - analysis and algorithms
- Cytoscape.js (JavaScript) - visualization
- D3.js - custom visualizations

### UI Frameworks
- React + TypeScript
- Graph visualization component
- Markdown + MathJax + Prism.js

### Storage
- Local: IndexedDB for browser storage
- Backend: PostgreSQL + graph columns
- Or: Neo4j if pure graph DB needed

---

## Project Context for Peter

**User's notes to transcribe:**
- Cotton paper notebook + fountain pen for this project
- Regular meetings about Little Schemer dialectic project

**Peter's concerns:**
- Typesetting quality (Gemini broke markdown/LaTeX before)
- Every text has tree-like concept graph
- Can we extract it reliably?

**Peter's excitement:**
- This is about knowledge representation
- Pedagogical theory (what is mastery?)
- Curriculum design (optimal teaching order)
- AI for education (can LLM do this?)

---

## The Central Hypothesis

**"If you extract a high-quality Pedagogical Concept Graph from educational materials, then generating effective dialectic becomes straightforward."**

**Test this by:**
1. Extract PCG from sample notebook
2. Validate quality with Peter
3. Generate dialectic from PCG
4. Test with real learner
5. Measure: Does it teach effectively?

**If hypothesis holds:** PCG extraction is the hard problem worth solving. Everything else follows.

---

## Getting Started (First Sprint)

**Goal:** Extract PCG from one Python notebook, validate it's correct.

**Tasks:**
1. Choose test notebook (basic Python concepts)
2. Implement semantic chunking (LLM-based)
3. Implement Pass 1 (structure extraction)
4. Validate: Is it a DAG? Dependencies logical?
5. Show to Peter, get feedback
6. Iterate on prompts based on feedback

**Success criteria:**
- Extracted graph is DAG
- All concepts have prerequisites
- Peter says "Yes, these dependencies are correct"
- Ready to move to Pass 2 (mastery criteria)

**If this works:** You've validated the core idea. Build from there.

---

That's the complete design! The key insight is that PCG extraction is the innovative hard problem, and if you solve it well, everything else (UI, dialectic, assessment) becomes tractable. Focus on extraction quality first, validate with Peter, then build the rest of the system.

Good luck with the implementation! 🚀
