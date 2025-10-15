# DESIGN.md - Little PAIPer Architecture

## Purpose
This document explains the technical architecture, design decisions, and key concepts for developers who want to understand, extend, or maintain the Little PAIPer system.

**Audience:** Developers, contributors, Peter/Mike/James (technical review)

---

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [System Architecture](#system-architecture)
3. [Data Pipeline](#data-pipeline)
4. [Component Design](#component-design)
5. [Key Algorithms](#key-algorithms)
6. [Design Decisions](#design-decisions)
7. [Future Directions](#future-directions)

---

## Core Concepts

### The Pedagogical Concept Graph (PCG)

**What it is:**
- A directed acyclic graph (DAG) where nodes are concepts and edges are "requires" relationships
- Enriched with learning objectives, mastery indicators, examples, and misconceptions
- Extracted from educational materials (textbooks, notebooks, tutorials)

**Why it matters:**
- The PCG is the **essence** of a textbook - the implicit structure made explicit
- Once extracted, enables multiple learning modalities from the same source
- Graph structure supports non-linear, personalized learning paths

**Data structure:**
```json
{
  "concepts": [
    {
      "id": "recursion",
      "name": "Recursion",
      "prerequisites": ["defun", "function_application"],
      "learning_objectives": [...],
      "mastery_indicators": [...],
      "examples": [...]
    }
  ],
  "edges": [
    {"from": "recursion", "to": "defun", "type": "requires"}
  ]
}
```

---

## System Architecture

### Three-Layer Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (Next.js)              │
│  ┌──────────────┬──────────────────┐   │
│  │ ConceptGraph │ SocraticDialogue │   │
│  │ (Cytoscape)  │  (React Modal)   │   │
│  └──────────────┴──────────────────┘   │
└─────────────────┬───────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────┐
│    API Layer (Next.js API Routes)       │
│  /api/socratic-dialogue                  │
│    - RAG retrieval                       │
│    - LLM prompt construction             │
│    - Mastery assessment                  │
└─────────────────┬───────────────────────┘
                  │ Gemini API
┌─────────────────▼───────────────────────┐
│    Data Layer (Static JSON)             │
│  - concept-graph.json (PCG)             │
│  - embeddings.json (RAG)                │
│  - localStorage (progress)              │
└─────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- Next.js 15 (React 19, TypeScript)
- Cytoscape.js for graph visualization
- Tailwind CSS + shadcn/ui components
- react-markdown for rich text rendering

**Backend:**
- Next.js API Routes (serverless functions)
- Gemini 2.5 Flash for dialogue
- gemini-embedding-001 for RAG

**Data:**
- Static JSON files (no database required for MVP)
- localStorage for client-side persistence
- File-based vector search (cosine similarity)

---

## Data Pipeline

### Stage 0: PCG Extraction (Multi-Pass)

```
Pass 1: Structure Extraction
  Input: paip-chapter-1.md
  LLM Task: Identify concepts and dependencies
  Output: Concept nodes + prerequisite edges (DAG)

Pass 2: Mastery Criteria
  Input: Pass 1 output + source text
  LLM Task: Design learning objectives and assessment
  Output: Mastery indicators, examples, misconceptions

Pass 3: Exercise Mapping
  Input: Pass 1 + Pass 2 + textbook exercises
  LLM Task: Link exercises to concepts
  Output: Exercise-to-concept mappings
```

### Stage 1: RAG Pipeline (One-Time)

```
Semantic Chunking (chunk-paip.ts)
  Input: paip-chapter-1.md
  LLM Task: Split into semantic units
  Output: 92 chunks with metadata

Embedding Generation (embed-chunks.ts)
  Input: chunks.json
  API: gemini-embedding-001
  Output: 3072-dim vectors per chunk
```

### Stage 2: Runtime (Per Dialogue Turn)

```
User Input → API Route
  ↓
Load concept data + cached textbook context
  ↓
Build prompt with:
  - Concept info
  - Learning objectives
  - Textbook passages (RAG)
  - Conversation history
  ↓
Generate response (Gemini 2.5 Flash)
  ↓
Parse JSON:
  - message (dialogue)
  - mastery_assessment (structured)
  ↓
Return to client
  ↓
Update UI:
  - Show message
  - Update mastery tracker
  - Enable "Mark as Mastered" if ready
```

---

## Component Design

### ConceptGraph.tsx

**Purpose:** Interactive graph visualization using Cytoscape.js

**Key features:**
- Multiple layout algorithms (dagre, breadthfirst, force-directed)
- Hover preview mode (non-destructive)
- Click-to-select with prerequisite highlighting
- Visual states: mastered (gold), ready (green glow), locked (faded)

**Design decisions:**
- Client component (`'use client'`) - requires browser APIs
- Ref-based Cytoscape initialization (can't treat as React component)
- Arrow direction reversed at render time (semantic vs visual)

### SocraticDialogue.tsx

**Purpose:** Modal for AI-guided learning sessions

**Key features:**
- Markdown rendering with syntax highlighting
- Real-time mastery tracking (progress bar)
- Auto-focus after LLM response (UX polish)
- Client-side textbook context caching

**Design decisions:**
- Structured JSON output from LLM (not free-form)
- Progress visualization only for concepts with mastery indicators
- Graceful degradation for basic concepts without indicators

### ConceptDetails.tsx

**Purpose:** Sidebar showing concept information

**Key features:**
- Human-readable learning paths (topological sort)
- Clickable prerequisite badges (navigation)
- Status-based sorting (mastered → ready → locked)
- Empty section suppression

---

## Key Algorithms

### 1. Topological Sort (Learning Path)

```typescript
function computePrerequisiteChain(
  conceptId: string,
  allConcepts: Concept[],
  masteredConcepts: Set<string>
): string[] {
  // DFS post-order traversal
  // Excludes already-mastered concepts
  // Returns ordered list: foundation → advanced
}
```

### 2. Semantic Search (RAG)

```typescript
function cosineSimilarity(a: number[], b: number[]): number {
  // Dot product / (||a|| * ||b||)
  // Returns 0.0 (orthogonal) to 1.0 (identical)
}

function retrieveRelevantChunks(query: string, topK: number) {
  // 1. Embed query → 3072-dim vector
  // 2. Compute similarity with all chunks
  // 3. Sort by similarity
  // 4. Return top K chunks
}
```

### 3. Mastery Assessment

```typescript
function evaluateMastery(tracker: MasteryTracker): boolean {
  // All basic skills ≥ 0.8
  // Most intermediate skills ≥ 0.7
  // Some advanced skills ≥ 0.6
}
```

---

## Design Decisions

### Why Multi-Pass PCG Extraction?

**Decision:** Extract structure, pedagogy, and exercises in separate passes

**Rationale:**
- Each pass is a distinct cognitive task for the LLM
- Better quality than single-pass "do everything at once"
- Incremental validation (fix structure before investing in pedagogy)
- Can reuse Pass 1 with different Pass 2/3 layers

**Alternative considered:** Single-pass structured output
- **Rejected:** Lower quality, harder to prompt correctly

---

### Why Client-Side Caching for RAG?

**Decision:** Retrieve textbook context once per dialogue, cache on client

**Rationale:**
- Only 1 embedding API call per session (vs N calls)
- 40% faster on subsequent turns
- Minimal cost increase (~$0.0008 per dialogue)
- Simpler than server-side session management

**Alternative considered:** Re-retrieve every turn
- **Rejected:** Unnecessary API costs and latency

---

### Why Reverse Arrow Direction?

**Decision:** Store edges as `{from: dependent, to: prerequisite}` but render reversed

**Rationale:**
- Semantic clarity in data ("X requires Y")
- Visual intuitiveness in UI (arrows point from prereqs to dependents)
- Best of both worlds

**Alternative considered:** Store visual direction
- **Rejected:** Queries become awkward ("what depends on X?")

---

### Why localStorage for Progress?

**Decision:** Persist mastered concepts in browser localStorage

**Rationale:**
- Zero backend required (MVP simplicity)
- Instant read/write (<1ms)
- Sufficient for single-user, single-device usage
- Easy to migrate to backend later

**Alternative considered:** Backend database
- **Deferred:** Not blocking for MVP, adds complexity

---

## Future Directions

### Short-term (1-2 months)
- Complete Pass 2 enrichment for all 33 concepts
- Spaced repetition for review
- Exercise integration (link to concept graph)

### Medium-term (3-6 months)
- Voice interface with Gemini Live
- Model selector (Flash vs Pro vs Thinking)
- Multi-chapter support (scale to full PAIP book)

### Long-term (6+ months)
- Backend for cross-device sync
- Social features (share learning paths)
- Author tooling (graph editor, validation)
- Adaptive recommendations (learn from user behavior)

---

## Open Questions

### 1. Example Adaptation
**Question:** When user says "I'm interested in biology", can we reframe examples from "ABC" to "ATCG" without breaking them?

**Current status:** Unresolved
**Considerations:** LLM self-critique loop to validate safety

### 2. Nonlinear vs Linear
**Question:** Should we enforce strict prerequisite ordering, or allow breadth-first exploration?

**Current status:** Hybrid - guide but don't force
**Considerations:** Different learners have different preferences

### 3. Mastery Threshold Calibration
**Question:** What confidence level = "mastered"?

**Current status:** Fixed thresholds (0.8/0.7/0.6)
**Considerations:** Could learn optimal thresholds from outcomes

---

**Last updated:** 2025-01-14
**See NOTES.md for implementation details and development log**
