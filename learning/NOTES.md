# Pedagogical Concept Graph (PCG) - Design Notes

## Question: Is the PCG a Union of the Three JSON Files?

**Short answer:** Almost, but not quite a simple union!

## The Multi-Layer Structure

The complete PCG is assembled from three complementary passes, each focusing on a different cognitive task:

### Pass 1: Structure (The Skeleton 🦴)
**File:** `paip-chapter-1-pcg-pass1.json`

**Purpose:** Extract the graph topology and basic concept information

**Contains:**
- Graph nodes with:
  - `id` (unique identifier)
  - `name` (human-readable)
  - `description` (brief explanation)
  - `prerequisites` (list of concept IDs)
  - `difficulty` (basic/intermediate/advanced)
  - `section` (chapter reference)
- Graph edges defining prerequisite relationships
- Statistics about graph structure

**Key output:** This creates the DAG (Directed Acyclic Graph) structure

**Status:** ✅ Complete (33 concepts, 45 edges)

---

### Pass 2: Mastery Criteria (The Flesh 🧠)
**File:** `paip-chapter-1-pcg-pass2-sample.json`

**Purpose:** Design learning objectives and assessment for each concept

**Enriches existing nodes with:**
- `learning_objectives` - what students should be able to DO
- `mastery_indicators` - specific testable skills with difficulty levels
- `examples` - code/text demonstrating the concept
- `misconceptions` - common student errors
- `key_insights` - important takeaways

**Key insight:** This doesn't create new nodes, it adds pedagogical flesh to the skeleton from Pass 1

**Status:** 🚧 Sample only (3 of 33 concepts enriched as proof-of-concept)

---

### Pass 3: Exercise Mapping (Assessment Layer 📝)
**File:** `paip-chapter-1-pcg-pass3.json`

**Purpose:** Map textbook exercises to concepts they test

**Contains:**
- `exercises` array with:
  - Exercise prompt and context
  - `tests_concepts` - which concepts this exercise assesses
  - Which `mastery_indicators` it probes
  - Example solutions
  - Common mistakes and hints
- `concept_to_exercises` - reverse index (concept → exercises)
- `exercise_progressions` - recommended orderings

**Key insight:** Exercises are separate from concepts but reference them. This is a distinct layer, not merged into concept nodes.

**Status:** ✅ Complete (5 exercises mapped to 10 concepts)

---

## How They Merge Together

### The Complete PCG Structure

```json
{
  "metadata": {
    "combined from all three passes"
  },
  
  "concepts": [
    {
      // From Pass 1 (structure):
      "id": "recursion",
      "name": "Recursion",
      "description": "Functions calling themselves to solve problems",
      "prerequisites": ["defun", "function_application", "list_accessors"],
      "difficulty": "advanced",
      "section": "1.6",
      
      // Added from Pass 2 (mastery):
      "learning_objectives": [
        "Identify the base case and recursive case",
        "Trace execution mentally",
        "Explain termination reasoning",
        "Write recursive functions"
      ],
      
      "mastery_indicators": [
        {
          "skill": "base_case_identification",
          "description": "Can identify stopping condition",
          "difficulty": "basic",
          "test_method": "Show function, ask to point out base case"
        },
        {
          "skill": "recursive_writing",
          "description": "Can write recursive function for novel problem",
          "difficulty": "advanced",
          "test_method": "Give problem, ask to implement recursively"
        }
      ],
      
      "examples": [
        {
          "content": "(defun first-name (name) ...)",
          "explanation": "Recursive function stripping titles",
          "when_to_show": "first_introduction",
          "demonstrates": ["base_case", "recursive_case"]
        }
      ],
      
      "misconceptions": [
        {
          "misconception": "Recursion is mysterious or magical",
          "reality": "It's just a function call to itself",
          "correction_strategy": "Show it's identical to any function call"
        }
      ],
      
      "key_insights": [
        "Every recursive function has at least one base case",
        "Each recursive call must make progress toward base case",
        "Use 'leap of faith' - trust the recursive call works"
      ]
    }
  ],
  
  "edges": [
    /* From Pass 1 - prerequisite relationships */
    {"from": "recursion", "to": "defun", "type": "requires"}
  ],
  
  "exercises": [
    /* From Pass 3 - separate assessment layer */
    {
      "id": "ex_1_2",
      "title": "Exponentiation function",
      "tests_concepts": [
        {
          "concept_id": "recursion",
          "mastery_indicators": [
            "recursive_writing",
            "base_case",
            "termination_reasoning"
          ],
          "weight": "primary"
        }
      ]
    }
  ],
  
  "concept_to_exercises": {
    /* From Pass 3 - reverse index for lookups */
    "recursion": {
      "exercises": ["ex_1_1", "ex_1_2", "ex_1_3", "ex_1_4", "ex_1_5"],
      "note": "All exercises can be solved recursively"
    }
  }
}
```

---

## Merge Strategy

### Pass 1 + Pass 2: Deep Merge
- **Operation:** Merge on `concept.id`
- **Result:** Complete concept nodes with structure AND pedagogy
- **Implementation:**
  ```python
  for concept in pass2_concepts:
      pass1_concept = find_by_id(pass1, concept.id)
      pass1_concept.update({
          "learning_objectives": concept.learning_objectives,
          "mastery_indicators": concept.mastery_indicators,
          "examples": concept.examples,
          "misconceptions": concept.misconceptions,
          "key_insights": concept.key_insights
      })
  ```

### Pass 3: Separate Layer
- **Operation:** Keep exercises as separate array
- **Relationship:** Exercises reference concepts via `concept_id`
- **Reverse index:** `concept_to_exercises` enables fast lookup
- **Why separate?** Exercises are not concepts; they're assessment instruments

---

## Current Status & Next Steps

### What We Have ✅
1. **Pass 1 complete:** All 33 concepts with structure
2. **Pass 2 sample:** 3 concepts fully enriched (proof-of-concept)
3. **Pass 3 complete:** All 5 chapter exercises mapped

### What's Missing 🚧
- **Pass 2 full enrichment:** Need to enrich remaining 30 concepts
- **Merge script:** Tool to combine all three passes into single PCG
- **Validation:** Check consistency across passes

### Implementation Plan
1. Complete Pass 2 enrichment for all concepts
2. Write merge utility: `bin/pcg_merge.py`
3. Validate merged PCG:
   - All concept_ids referenced in Pass 3 exist in Pass 1
   - No orphaned mastery_indicators
   - Prerequisite chains are valid
4. Generate final: `paip-chapter-1-pcg-complete.json`

---

## Design Rationale

### Why Multi-Pass?

**Cognitive separation:** Each pass is a distinct cognitive task:
- **Pass 1:** "What are the concepts and how do they relate?" (graph thinking)
- **Pass 2:** "How do we teach and assess each concept?" (pedagogical design)
- **Pass 3:** "Which exercises test which concepts?" (assessment mapping)

**LLM focus:** Each prompt can focus on one type of extraction without cognitive overload

**Incremental refinement:** Can validate structure before investing in detailed pedagogy

**Alternative considered:** Single-pass extraction with structured output
- **Pros:** Simpler, one API call per concept
- **Cons:** Harder to prompt well, lower quality, all-or-nothing

**Decision:** Multi-pass provides better quality at cost of complexity

### Why Exercises Separate?

**Different entity type:** Exercises are not concepts; they're instruments to measure concept mastery

**Many-to-many relationship:** One exercise can test multiple concepts; one concept tested by multiple exercises

**Reusability:** Same concept graph can be used with different exercise sets

**Queryability:** Need to ask both:
- "Which exercises test recursion?" → `concept_to_exercises`
- "Which concepts does ex_1_2 test?" → `exercises[].tests_concepts`

---

## Key Insights from This Discussion

1. **PCG is multi-layered, not flat**
   - Structure layer (DAG)
   - Pedagogy layer (objectives, assessment)
   - Exercise layer (assessment instruments)

2. **Passes 1+2 merge, Pass 3 stays separate**
   - Merge creates complete concept nodes
   - Exercises reference concepts but remain distinct

3. **Pass 2 sample validates the approach**
   - 3 concepts show the enrichment pattern
   - Ready to scale to all 33 concepts

4. **The complete PCG enables dialectic generation**
   - Structure tells us teaching order (topological sort)
   - Pedagogy tells us what to teach and how to assess
   - Exercises provide ready-made assessment problems

---

## Files in This Collection

```
learning/
├── CONTEXT.md                           # Overall project design
├── NOTES.md                             # This file - implementation notes
├── paip-chapter-1.md                    # Source material
├── paip-chapter-1-pcg-pass1.json        # Structure extraction (complete)
├── paip-chapter-1-pcg-pass2-sample.json # Mastery criteria (sample: 3/33)
└── paip-chapter-1-pcg-pass3.json        # Exercise mapping (complete)
```

---

## Future Work

### Immediate
- [ ] Complete Pass 2 enrichment (30 more concepts)
- [ ] Write merge script
- [ ] Validate merged PCG

### Short-term
- [ ] Extract PCG from another chapter (test generalization)
- [ ] Build simple dialectic generator using merged PCG
- [ ] Test with real learner

### Long-term
- [ ] Graph visualization UI
- [ ] Interactive dialectic system
- [ ] Multi-artifact support
- [ ] Automated PCG extraction pipeline

---

## Discovering Root Nodes: Visual Learning Entry Points

### The Root Node Problem

After implementing the reversed arrows (showing learning progression), we examined the visualization and made an important observation:

**Question:** "Does the graph imply that REPL and Symbols are both roots?"

**Answer:** Yes! Both have:
- ✓ Arrows pointing OUT (to dependent concepts)
- ✓ NO arrows pointing IN (no prerequisites)
- **Conclusion:** These are ROOT nodes - valid starting points for learning

### Semantic Validation

These roots make pedagogical sense for PAIP Chapter 1:

1. **Interactive REPL**
   - You need a REPL environment to experiment with Lisp
   - Hands-on, exploratory learning style
   - "Learn by doing" entry point

2. **Symbols**
   - The fundamental data type in Lisp
   - Building block for everything else
   - "Learn theory first" entry point

Both are legitimate starting points. Different learners with different backgrounds and preferences might choose different entry points.

### UX Design: Onboarding New Learners

**Challenge:** When a user first views the graph, how do we help them start?

**Recommendation:** Guided but non-prescriptive approach

#### Proposed Solution

**1. Visual Highlighting of Roots**
- Add subtle glow or special border to root nodes
- Use distinctive styling (e.g., lighter shade of green)
- Optional "START HERE" badge

**2. Welcome Modal on First Visit**
```
Welcome to PAIP Chapter 1!

This graph shows how Lisp concepts build on each other.
Start with one of the highlighted "root" concepts:

• Interactive REPL - Learn by experimenting
• Symbols - Understand Lisp's fundamental data type

Click a concept to see details, then follow arrows to see what's next!
```

**3. User Choice**
- Let the user click to choose their starting point
- No forced path - respects learner autonomy
- Graph remains explorable and non-linear

#### Design Rationale

**Preserves Autonomy:**
- Different learners have different backgrounds
- REPL-experienced developers might prefer hands-on start
- Theory-first learners might prefer Symbols

**Reduces Decision Paralysis:**
- Makes it clear there are only 2 starting points (not 33)
- Simplifies the initial learning decision

**Educational:**
- Tooltip explains how to read the graph
- Sets expectations for how arrows show progression

**Non-Intrusive:**
- After dismissing welcome message, free exploration
- No persistent UI clutter

#### Alternative Approach: Opinionated Pedagogy

If the textbook author believes one path is strictly superior:
- Default-select one root (e.g., "Interactive REPL") with highlight
- Still allow clicking on other root (Symbols)
- Nudges without forcing

**Our choice:** Keep it non-prescriptive. The book itself doesn't mandate a strict order for these foundational concepts.

### Implementation Status

- [x] Arrow direction reversed to show learning flow
- [x] Root nodes identified (Interactive REPL, Symbols)
- [ ] Visual styling for root nodes (TODO)
- [ ] Welcome modal/tooltip (TODO)
- [ ] First-visit detection (localStorage) (TODO)

---

## Learning Path Progression: Design Decisions

### The Core Challenge

Once a learner starts at a root concept (e.g., "Interactive REPL" or "Symbols"), **how should they progress through the graph?**

Key questions:
1. What order should concepts be learned?
2. How do we respect both **prerequisites** and **difficulty levels**?
3. How do we provide guidance without forcing a single path?
4. How do we visually communicate progress and next steps?

---

### Progression Strategy Options

#### Option 1: "Greedy Ready" ⭐ *Recommended*

**Algorithm:**
```javascript
function getRecommendedNext(masteredConcepts) {
  // Find all concepts whose prerequisites are satisfied
  const ready = concepts.filter(c => 
    !masteredConcepts.includes(c.id) &&
    c.prerequisites.every(p => masteredConcepts.includes(p))
  );
  
  // Sort by difficulty (basic → intermediate → advanced)
  // Tie-breaker: which unlocks more concepts?
  return ready.sort((a, b) => {
    if (a.difficulty !== b.difficulty) {
      return difficultyRank[a.difficulty] - difficultyRank[b.difficulty];
    }
    return countUnlocks(b) - countUnlocks(a);
  }).slice(0, 5); // Top 5 recommendations
}
```

**How it works:**
1. At any moment, identify all concepts whose prerequisites are **satisfied**
2. Among "ready to learn" concepts, **prioritize by difficulty**: Basic → Intermediate → Advanced
3. Within same difficulty, prefer concepts that unlock more downstream concepts
4. Present top 3-5 as recommendations; user chooses

**Example progression from Symbols:**
```
Symbols ✓ (mastered)
  ↓
Ready: Lists, Quote, Variables, FunctionRefSyntax, Assignment (all Basic)
User picks: Lists ✓
  ↓
Ready: ListAccessors, ListConstructors, NIL, Sublists, Quote, Variables, ... (all Basic)
User picks: NIL ✓
  ↓
Ready: [previous] + NestedExpressions (newly unlocked)
  ↓
... continues ...
```

**Pros:**
- ✅ Respects dependencies (never suggests something you're not ready for)
- ✅ Natural difficulty progression (build foundation before tackling hard concepts)
- ✅ Always shows forward progress
- ✅ User retains choice among ready concepts
- ✅ Optimizes for unlocking (prefers concepts that open up more paths)

**Cons:**
- ⚠️ May jump between branches (not strict depth-first within one subtree)
- ⚠️ Requires computing "ready set" on each state change

---

#### Option 2: Depth-First by Difficulty

**Algorithm:**
1. Start at root (e.g., Symbols)
2. Follow one path, learning ALL basic concepts until hitting intermediate/advanced
3. Backtrack, try next basic path
4. Once all reachable basics are exhausted, tackle intermediates
5. Finally tackle advanced concepts

**Pros:**
- ✅ Master all easy material before harder concepts
- ✅ Builds solid foundation systematically

**Cons:**
- ❌ May get "stuck" - a basic concept deep in a branch might be blocked by intermediate concepts
- ❌ Less natural flow (why learn one branch completely before touching another?)
- ❌ Arbitrary which branch to follow first

**Verdict:** Too rigid; doesn't respect natural learning curiosity

---

#### Option 3: Breadth-First (Level-by-Level)

**Algorithm:**
1. Master root (Symbols)
2. Master ALL direct children (Lists, Quote, Variables, etc.)
3. Master all grandchildren
4. Continue level-by-level down the DAG

**Pros:**
- ✅ Systematic coverage
- ✅ Clear sense of progress (depth levels)

**Cons:**
- ❌ Ignores difficulty - might attempt advanced concepts before having sufficient foundation
- ❌ Can feel forced (why must I learn ALL siblings before any children?)
- ❌ Doesn't optimize for learning efficiency

**Verdict:** Too mechanical; treats all concepts equally regardless of difficulty

---

#### Option 4: Interest-Driven with Smart Suggestions

**Algorithm:**
1. User can click ANY node at any time to inspect status
2. System shows clear visual states (locked/ready/mastered)
3. System highlights "recommended next" using Greedy Ready algorithm
4. User can follow recommendations OR jump to any ready concept

**Pros:**
- ✅ Maximum learner autonomy
- ✅ System provides guidance without forcing
- ✅ Respects intrinsic motivation ("I'm curious about recursion!")
- ✅ Learner can optimize for their own goals

**Cons:**
- ⚠️ User might make suboptimal choices (attempting concepts before ready)
- ⚠️ Requires excellent UI to communicate locked vs. ready states
- ⚠️ Some learners prefer more structure/direction

**Verdict:** Good for advanced learners; might overwhelm beginners

---

### Our Design: Hybrid "Guided Greedy Ready"

**Approach:** Combine the structure of Greedy Ready (Option 1) with the autonomy of Interest-Driven (Option 4)

**Key principles:**
1. **Guide, don't force:** Highlight recommended next steps, but allow exploration
2. **Make readiness obvious:** Clear visual distinction between locked, ready, and mastered
3. **Provide context:** When user clicks locked concept, show prerequisite chain
4. **Celebrate progress:** Visual feedback when concepts are mastered and new concepts unlock

---

### Visual State Design

The graph uses five distinct visual states to communicate learning status:

#### 👑 Mastered (Completed)
- **Background:** Gold/yellow gradient
- **Icon:** ✓ checkmark badge
- **Border:** Solid gold (3px)
- **Opacity:** 100% (stay visible)
- **Interaction:** Click → "What this unlocked" + review learning objectives

**Why gold?** Positive reinforcement; achievement; valuable progress

#### ✨ Recommended Next (Top 3-5 ready concepts)
- **Background:** Original difficulty color (green/blue/red)
- **Glow:** Pulsing green animation (subtle, 1.5s cycle)
- **Border:** Bright green (2px)
- **Icon:** ⭐ star or sparkles
- **Interaction:** Click → "Start Learning" modal

**Why pulse?** Draws attention without being distracting; suggests "this is active/available"

#### ✅ Ready to Learn (Prerequisites met, but not top recommendation)
- **Background:** Original difficulty color
- **Brightness:** +10% brighter than locked
- **Border:** Normal
- **Opacity:** 100%
- **Interaction:** Click → "Start Learning" modal

**Why brighter?** Distinguishable from locked, but less attention-grabbing than recommended

#### 🔓 Almost Ready (Missing 1-2 prerequisites)
- **Background:** Original difficulty color
- **Opacity:** 60%
- **Border:** Dashed gray
- **Badge:** "1 away" or "2 away"
- **Interaction:** Click → Show what's blocking + shortest path

**Why show this?** Motivates learners to see they're close; helps planning

#### 🔒 Locked (Missing 3+ prerequisites)
- **Background:** Original difficulty color
- **Opacity:** 30%
- **Icon:** 🔒 padlock overlay
- **Border:** None
- **Interaction:** Click → Show prerequisite tree + shortest path to unlock

**Why locked?** Clear visual signal that this is not accessible yet

---

### Example User Journey

```
=== START ===
User lands on visualizer
Graph shows: Interactive REPL and Symbols glowing as roots
Welcome modal: "Start with Interactive REPL or Symbols!"

User clicks: Symbols
Modal displays:
  - Description
  - Learning objectives
  - Examples
  - [Start Learning] button

=== AFTER MASTERING SYMBOLS ===
Graph updates:
  ✓ Symbols → gold with checkmark
  ✨ 5 concepts start pulsing: Lists, Quote, Variables, FunctionRefSyntax, Assignment
  📊 Stats panel: "5 new concepts unlocked!"
  🎉 Subtle confetti animation (optional)

User hovers: Lists (recommended)
Tooltip: "⭐ Recommended • Basic • Unlocks 4 concepts"

User clicks: Lists
Modal: Learning objectives + [Start Learning]

=== USER GETS CURIOUS ===
User clicks: Recursion (locked, advanced, needs 5 prerequisites)
Modal shows:
  "🔒 Not ready yet! You need:
   ✓ Symbols (done!)
   🔒 Defun
   🔒 Function Application
   🔒 List Accessors
   
   📍 Shortest path:
   You → Defun → List Accessors → Function Application → Recursion
   (Estimated 3 concepts away)
   
   [Show Path on Graph] button"

User clicks: [Show Path on Graph]
Graph highlights: recommended path with animated arrows

User: "Ah, I see!" Follows the path
```

---

### Implementation Roadmap

#### Phase 1: Basic Progress Tracking ✅ *Complete*
- [x] Track masteredConcepts in localStorage
- [x] Visual distinction for mastered (gold + checkmark)
- [x] Stats panel showing mastered/in-progress/ready/locked counts
- [x] Click concept to mark as mastered/in-progress

#### Phase 2: Smart Recommendations 🚧 *Next*
- [ ] Implement `getReadyConcepts(mastered)` algorithm
- [ ] Add "Recommended Next" visual state (pulsing glow)
- [ ] Sort recommendations by difficulty + unlock potential
- [ ] Display recommended concepts in sidebar

#### Phase 3: Dependency Visualization
- [ ] Implement `getLockedReasons(conceptId, mastered)`
- [ ] Show prerequisite tree when clicking locked concept
- [ ] Calculate and display "shortest path to unlock"
- [ ] Highlight paths on graph with animated flow

#### Phase 4: Enhanced Learning Flow
- [ ] Add "Start Learning" modal with objectives
- [ ] Track "in-progress" state (started but not mastered)
- [ ] Show "What this unlocked" when completing a concept
- [ ] Add celebration animations for milestones

#### Phase 5: Pedagogical Integration
- [ ] Display learning objectives from Pass 2 data
- [ ] Show examples and misconceptions
- [ ] Link to exercises that test this concept (Pass 3)
- [ ] Track time spent per concept

---

### Design Tradeoffs

#### Autonomy vs. Guidance
**Tension:** Some learners want clear prescribed paths; others want freedom to explore

**Our choice:** Guide with recommendations, but allow clicking any ready concept
- Beginners can follow the glowing path
- Advanced learners can explore based on interest
- System always prevents tackling concepts before prerequisites are met

#### Visual Clutter vs. Information Richness
**Tension:** More visual states = more information, but also more complexity

**Our choice:** Five states is the maximum before it becomes overwhelming
- We group concepts with 3+ missing prerequisites into single "locked" state
- "Almost ready" (1-2 away) gets special treatment because it's actionable

#### Optimizing for Speed vs. Depth
**Tension:** Fastest path through graph vs. deepest understanding

**Our choice:** Recommend easiest-first, but don't prevent tackling harder concepts
- Default path builds solid foundation
- Advanced learners can skip ahead if prerequisites are met
- System never lies about readiness

---

### Future Enhancements

#### Adaptive Recommendations
Use learning history to personalize recommendations:
- If user consistently chooses advanced concepts, suggest those more
- If user struggles with a difficulty level, recommend more prerequisites
- Track time-to-mastery and adjust pace

#### Multiple Learning Styles
Offer different progression presets:
- "Breadth-first explorer" - level-by-level
- "Depth-first specialist" - one subtree at a time
- "Efficient speedrunner" - shortest path to advanced concepts
- "Thorough scholar" - revisit and reinforce frequently

#### Social Features
- Share your learning path with others
- See what path other learners took
- "Racing" mode - compete to master concepts fastest
- Collaborative learning - discuss concepts with peers

#### Spaced Repetition
- Mark mastered concepts for review after 1 week, 1 month, 3 months
- Periodic "knowledge checks" on previously mastered material
- Adjust visual state if review is needed ("needs refresh")

---

## Peirastic AI: Active Mastery Through Socratic Dialogue

### The Core Problem with Passive Learning

Simply clicking "I learned this" is **not learning**. Real mastery requires:
1. **Active demonstration** of understanding
2. **Socratic questioning** to reveal gaps
3. **Adaptive scaffolding** when struggling
4. **Celebration** of genuine insight

**Inspiration:** *The Little Schemer* dialectical style (see attached image) - learning through guided discovery, not lecture.

### Design Philosophy: Earned Progression

**Current flow (passive):**
```
User clicks concept → reads description → clicks "Mark as mastered" → unlocks next concepts
```

**Proposed flow (active):**
```
User clicks "Start Learning" 
  ↓
Enters Socratic dialogue session with LLM tutor
  ↓
For each mastery indicator:
  - Answer probing questions
  - Work through examples
  - Demonstrate understanding (not just recognition)
  ↓
System evaluates: Have all critical indicators been demonstrated?
  ↓
If YES: Grant mastery ✓ → Unlock dependents → Celebrate progress
If NO: Provide scaffolding → Continue dialogue → Build understanding
```

**Key insight:** Progression is **earned**, not claimed.

---

### Leveraging Existing Pedagogical Data

Our `concept-graph.json` already has **perfect structure** for generating dialogues:

#### Mastery Indicators = Test Instructions

```json
{
  "mastery_indicators": [
    {
      "skill": "quote_syntax",
      "difficulty": "basic",
      "test_method": "Ask: 'How do you write the list (a b c) as data?'"
    },
    {
      "skill": "evaluation_blocking",
      "difficulty": "basic",
      "test_method": "Compare: What does '(+ 2 2) return vs (+ 2 2)?"
    }
  ]
}
```

The `test_method` field is **literally instructions for the LLM** on how to test understanding!

#### Examples Provide Teaching Sequence

```json
{
  "examples": [
    {
      "content": "> 'John => JOHN",
      "when_to_show": "first_introduction",
      "demonstrates": ["quote_syntax"]
    },
    {
      "content": "> '(+ 2 2) => (+ 2 2) vs (+ 2 2) => 4",
      "when_to_show": "data_vs_code",
      "demonstrates": ["evaluation_blocking"]
    }
  ]
}
```

Use `when_to_show` to sequence examples appropriately during dialogue.

#### Misconceptions = Error Detection

```json
{
  "misconceptions": [
    {
      "misconception": "Numbers need to be quoted",
      "reality": "Numbers are self-evaluating",
      "correction_strategy": "Show that 2 and '2 both return 2"
    }
  ]
}
```

LLM watches for these patterns in student responses and provides **targeted corrections**.

---

### System Architecture

#### Core Component: ConceptMasterySession

```javascript
class ConceptMasterySession {
  constructor(conceptId, conceptData) {
    this.conceptId = conceptId;
    this.data = conceptData;  // From concept-graph.json
    this.indicatorStatus = {};  // Track which skills demonstrated
    this.conversationHistory = [];
    this.misconceptionsDetected = [];
  }
  
  async start() {
    // 1. Welcome and context
    const intro = await this.generateIntroduction();
    this.display(intro);
    
    // 2. Test each mastery indicator
    for (const indicator of this.data.mastery_indicators) {
      const passed = await this.testIndicator(indicator);
      this.indicatorStatus[indicator.skill] = passed;
      
      // If struggling, provide scaffolding
      if (!passed) {
        await this.provideScaffolding(indicator);
      }
    }
    
    // 3. Final evaluation
    return this.evaluateMastery();
  }
  
  async testIndicator(indicator) {
    // Build prompt using our pedagogical data
    const prompt = this.buildPromptForIndicator(indicator);
    
    // LLM generates Socratic question
    const llmQuestion = await this.queryLLM(prompt);
    this.display(llmQuestion);
    
    // Get student response
    const studentAnswer = await this.getUserInput();
    this.conversationHistory.push({
      role: 'student',
      content: studentAnswer
    });
    
    // Evaluate response
    const evaluation = await this.evaluateResponse(
      indicator,
      studentAnswer,
      llmQuestion
    );
    
    // Provide feedback
    this.display(evaluation.feedback);
    
    return evaluation.passed;
  }
  
  buildPromptForIndicator(indicator) {
    return {
      system: `You are a Socratic tutor for Lisp programming, inspired by 
The Little Schemer. Your role:

1. Ask probing questions to test understanding
2. Use concrete examples, not abstract explanations
3. Provide hints when the student struggles
4. Celebrate insights with enthusiasm
5. Gently correct misconceptions with counterexamples
6. Make learning feel like discovery, not drilling
7. Ask ONE question at a time, wait for response

Be encouraging, patient, and dialectical.`,
      
      context: {
        concept_name: this.data.name,
        description: this.data.description,
        skill_to_test: indicator.skill,
        skill_description: indicator.description,
        test_method: indicator.test_method,
        examples: this.data.examples,
        misconceptions: this.data.misconceptions,
        conversation_so_far: this.conversationHistory
      },
      
      instruction: `Test the student's understanding of: "${indicator.description}"

Suggested test approach: ${indicator.test_method}

Generate a Socratic question that reveals whether they truly understand this skill.
Use examples from the concept data. Be specific and concrete.`
    };
  }
  
  async evaluateResponse(indicator, studentAnswer, question) {
    // LLM evaluates whether student demonstrated understanding
    const evalPrompt = {
      system: `You are evaluating a student's response in a Socratic dialogue.
Determine if they demonstrated the required skill.`,
      
      context: {
        skill: indicator.description,
        question_asked: question,
        student_answer: studentAnswer,
        known_misconceptions: this.data.misconceptions
      },
      
      instruction: `Did the student demonstrate understanding?
      
Return JSON:
{
  "passed": true/false,
  "confidence": 0-1,
  "feedback": "Brief encouraging response",
  "misconceptions_detected": ["list of any misconceptions shown"],
  "should_scaffold": true/false
}`
    };
    
    const evaluation = await this.queryLLM(evalPrompt);
    
    // Track misconceptions for later correction
    if (evaluation.misconceptions_detected) {
      this.misconceptionsDetected.push(...evaluation.misconceptions_detected);
    }
    
    return evaluation;
  }
  
  async provideScaffolding(indicator) {
    // Break down into simpler questions
    // Show relevant examples
    // Provide hints without giving away answer
    const scaffoldPrompt = {
      system: `Student is struggling with "${indicator.description}".
Provide gentle scaffolding - a simpler related question or a helpful hint.
Don't give away the answer directly.`,
      
      context: {
        concept: this.data.name,
        struggling_with: indicator.skill,
        examples: this.data.examples,
        conversation: this.conversationHistory
      }
    };
    
    const hint = await this.queryLLM(scaffoldPrompt);
    this.display(hint);
    
    // Ask a simpler version of the question
    return await this.testIndicator(indicator);  // Retry
  }
  
  evaluateMastery() {
    // Classify by difficulty
    const basicIndicators = this.data.mastery_indicators.filter(
      i => i.difficulty === 'basic'
    );
    const intermediateIndicators = this.data.mastery_indicators.filter(
      i => i.difficulty === 'intermediate'
    );
    const advancedIndicators = this.data.mastery_indicators.filter(
      i => i.difficulty === 'advanced'
    );
    
    // Calculate pass rates
    const basicPassRate = basicIndicators.filter(
      i => this.indicatorStatus[i.skill]
    ).length / basicIndicators.length;
    
    const intermediatePassRate = intermediateIndicators.filter(
      i => this.indicatorStatus[i.skill]
    ).length / intermediateIndicators.length;
    
    const advancedPassRate = advancedIndicators.length > 0
      ? advancedIndicators.filter(i => this.indicatorStatus[i.skill]).length / advancedIndicators.length
      : 1;  // No advanced indicators = pass by default
    
    // Mastery criteria:
    // - Must pass ALL basic indicators (100%)
    // - Must pass MOST intermediate indicators (≥75%)
    // - Should pass SOME advanced indicators (≥50%)
    const mastered = 
      basicPassRate === 1.0 &&
      intermediatePassRate >= 0.75 &&
      advancedPassRate >= 0.5;
    
    return {
      mastered,
      basicPassRate,
      intermediatePassRate,
      advancedPassRate,
      indicatorsPassed: this.indicatorStatus,
      misconceptionsDetected: this.misconceptionsDetected,
      recommendation: mastered
        ? "🎉 Concept mastered! You're ready to move forward."
        : "Keep practicing - you're making good progress! Let's review a few more things."
    };
  }
}
```

---

### Example Dialogue Flow

**Teaching Quote concept:**

```
=== SESSION START ===

LLM: "Welcome! Today we're exploring the Quote special form in Lisp.

Let's start with a quick experiment. What do you think this returns?
    (+ 2 2)

Try to predict before checking the REPL!"

Student: "4"

LLM: "Exactly! ✓ The addition evaluates to 4.

Now, what about this one?
    '(+ 2 2)

Notice the single quote mark at the front. What do you predict?"

Student: "Maybe... it returns the list (+ 2 2)?"

LLM: "Perfect! 🎉 That's exactly right!

The quote prevents evaluation - it says 'treat this as data, 
not code to run.'

So what happens when we evaluate these?
    John        vs    'John
    
One will cause an error. Which one, and why?"

Student: "John will error because it's not defined?"

LLM: "Excellent reasoning! ✓ 

Without the quote, Lisp tries to look up John as a variable.
With the quote, it's just the symbol JOHN itself.

✓ You understand evaluation blocking!

Now let's test your ability to apply this...

I want to create a list containing the symbols A, B, and C.
How would you write that expression?"

Student: "(list a b c)"

LLM: "Hmm, think carefully - what would Lisp do with a, b, and c 
if they're not quoted?

Try running that in your REPL. What error do you get?"

Student: "Oh! It says A is unbound. I need: (list 'a 'b 'c)"

LLM: "Yes! 🎉 Or even simpler: '(a b c)

When you quote the whole list, everything inside is data.

✓ You know when to use quote!

=== MASTERY EVALUATION ===
✓ quote_syntax: Passed
✓ evaluation_blocking: Passed  
✓ when_to_quote: Passed

🎉 Concept mastered! Quote unlocked 2 new concepts:
   - Quoted vs Unquoted
   - Special Forms
   
Ready to continue your journey?"
```

---

### UI Integration

#### Concept Node Interactions

**When user clicks a concept node:**

```javascript
function onConceptClick(conceptId) {
  const concept = getConceptById(conceptId);
  const state = getConceptState(conceptId);
  
  if (state === 'locked') {
    showPrerequisiteModal(concept);
  } else if (state === 'ready' || state === 'recommended') {
    showLearningSessionOption(concept);
  } else if (state === 'in-progress') {
    showResumeSessionOption(concept);
  } else if (state === 'mastered') {
    showReviewOption(concept);
  }
}
```

#### Learning Session UI

```html
<div class="mastery-session-container">
  <!-- Header with progress -->
  <div class="session-header">
    <h2>Learning: <span id="concept-name">Quote</span></h2>
    <button class="close-btn">✕</button>
    
    <!-- Progress indicators -->
    <div class="mastery-progress">
      <div class="indicator passed" title="Quote syntax">
        <span class="icon">✓</span>
        <span class="label">Syntax</span>
      </div>
      <div class="indicator current" title="Evaluation blocking">
        <span class="icon">⟳</span>
        <span class="label">Blocking</span>
      </div>
      <div class="indicator pending" title="When to quote">
        <span class="icon">○</span>
        <span class="label">Usage</span>
      </div>
    </div>
  </div>
  
  <!-- Dialogue area (scrollable) -->
  <div class="dialogue-area">
    <div class="message tutor">
      <div class="avatar">🧙</div>
      <div class="content">
        Welcome! Today we're exploring the Quote special form...
      </div>
    </div>
    
    <div class="message student">
      <div class="avatar">👤</div>
      <div class="content">
        It prevents evaluation?
      </div>
    </div>
    
    <div class="message tutor celebration">
      <div class="avatar">🧙</div>
      <div class="content">
        Exactly! ✨ You've got it!
      </div>
    </div>
  </div>
  
  <!-- Input area -->
  <div class="input-area">
    <textarea 
      placeholder="Type your answer here..."
      id="student-input"
    ></textarea>
    <button id="submit-btn">Submit</button>
  </div>
  
  <!-- Optional: REPL integration -->
  <div class="repl-pane collapsible">
    <h3>Try it yourself <button>▼</button></h3>
    <div class="repl-content">
      <!-- Embedded REPL for experimentation -->
    </div>
  </div>
</div>
```

#### Visual States During Learning

**Update graph visualization to show learning state:**

```css
/* Concept node during active learning session */
.cy-node.learning-active {
  border: 3px solid #4CAF50;
  box-shadow: 0 0 20px rgba(76, 175, 80, 0.6);
  animation: pulse-learning 2s infinite;
}

/* Indicator badges on nodes */
.cy-node.learning-active::after {
  content: "📖";
  position: absolute;
  top: -10px;
  right: -10px;
  font-size: 20px;
}
```

---

### Adaptive Difficulty

#### Smart Sequencing

```javascript
async selectNextIndicator(concept, results) {
  const remaining = concept.mastery_indicators.filter(
    i => !results[i.skill]
  );
  
  // If breezing through basics, jump to intermediate/advanced
  const basicPassed = results.filter(
    r => r.difficulty === 'basic' && r.passed
  ).length;
  
  if (basicPassed >= 2) {
    // Skip remaining basics, go straight to intermediate
    return remaining.find(i => i.difficulty === 'intermediate')
      || remaining.find(i => i.difficulty === 'advanced')
      || remaining[0];
  }
  
  // Otherwise, progress through difficulty levels
  return remaining.find(i => i.difficulty === 'basic')
    || remaining.find(i => i.difficulty === 'intermediate')
    || remaining.find(i => i.difficulty === 'advanced');
}
```

#### Misconception-Driven Remediation

```javascript
async correctMisconception(misconceptionKey) {
  const misconception = this.data.misconceptions.find(
    m => m.misconception === misconceptionKey
  );
  
  if (!misconception) return;
  
  const correctionPrompt = {
    system: "Gently correct this misconception using the provided strategy.",
    context: {
      misconception: misconception.misconception,
      reality: misconception.reality,
      strategy: misconception.correction_strategy,
      conversation: this.conversationHistory
    },
    instruction: `The student showed this misconception: "${misconception.misconception}"
    
The reality is: "${misconception.reality}"

Use this strategy: "${misconception.correction_strategy}"

Generate a Socratic exchange that leads them to discover the correct understanding.
Don't just tell them - help them figure it out.`
  };
  
  const correction = await this.queryLLM(correctionPrompt);
  this.display(correction);
}
```

---

### Multi-Concept Integration

#### Referencing Prerequisites

When teaching a concept, **connect to prerequisites**:

```javascript
buildContextualPrompt(concept) {
  const prerequisites = getPrerequisites(concept.id);
  const masteredPrereqs = prerequisites.filter(p => isMastered(p.id));
  
  return {
    system: "...",
    context: {
      current_concept: concept,
      mastered_prerequisites: masteredPrereqs,
      // LLM can reference these in dialogue
      instruction: `You can reference these concepts the student already knows:
${masteredPrereqs.map(p => `- ${p.name}: ${p.description}`).join('\n')}

Build on this foundation when explaining ${concept.name}.`
    }
  };
}
```

**Example dialogue with prerequisite integration:**

```
LLM: "Remember when we learned about function application? 
When you evaluated (+ 2 2), Lisp:
  1. Evaluated each argument (2, 2)
  2. Applied + to the results
  3. Returned 4

Now, what's different when we write '(+ 2 2)?"

Student: "The quote prevents step 1?"

LLM: "Exactly! The quote stops the entire evaluation process.
It's like pressing pause before Lisp even looks at the arguments."
```

---

### Exercise Integration

#### After Mastering Concept

```javascript
async completeMastery(conceptId, results) {
  // Grant mastery
  markAsMastered(conceptId);
  unlockDependents(conceptId);
  
  // Celebrate
  showCelebration(conceptId);
  
  // Offer related exercises
  const exercises = getExercisesForConcept(conceptId);
  
  if (exercises.length > 0) {
    showExercisePrompt({
      message: `Great work mastering ${getConceptName(conceptId)}! 
      
Ready to apply your knowledge?
${exercises.length} exercise(s) await:
${exercises.map(e => `- ${e.title}`).join('\n')}`,
      options: ['Start Exercises', 'Continue Learning', 'Take a Break']
    });
  }
}
```

#### Exercise-Specific Dialogue

For exercises like "Write a robust last-name function":

```javascript
async conductExerciseSession(exerciseId) {
  const exercise = getExerciseById(exerciseId);
  
  // Show problem statement
  this.display(`Exercise: ${exercise.title}\n\n${exercise.prompt}`);
  
  // Guide through solution
  // - Clarifying requirements
  // - Identifying edge cases
  // - Testing implementation
  // - Comparing to example solutions
  
  // Use exercise.common_mistakes to provide targeted hints
  // Use exercise.hints for progressive scaffolding
}
```

---

### Advanced Features

#### Trace Visualization for Recursion

When teaching recursion, generate **step-by-step execution traces**:

```javascript
async teachRecursion(concept) {
  // Show example recursive function
  this.display(concept.examples.find(e => e.demonstrates.includes('base_case')));
  
  // Interactive tracing
  const tracePrompt = `Let's trace this execution together.
  
(first-name '(Dr John Smith))

What happens first? Does 'Dr' match the base case?`;
  
  // Build trace collaboratively with student
  // Visualize call stack
  // Highlight base case vs recursive case
}
```

#### Spaced Repetition Review

Even mastered concepts need **periodic review**:

```javascript
class SpacedRepetitionScheduler {
  getReviewSchedule(conceptId, masteryDate) {
    return {
      first_review: masteryDate + 1 * DAY,
      second_review: masteryDate + 3 * DAYS,
      third_review: masteryDate + 7 * DAYS,
      fourth_review: masteryDate + 14 * DAYS,
      fifth_review: masteryDate + 30 * DAYS
    };
  }
  
  async conductReview(conceptId) {
    // Lighter dialogue than initial learning
    // Focus on 1-2 key mastery indicators
    // If passed: extend next review interval
    // If failed: mark for re-learning
  }
}
```

---

### Implementation Roadmap

#### Phase 1: Dialogue Engine Prototype (Week 1-2)
- [ ] Build `ConceptMasterySession` class
- [ ] Implement basic prompt construction
- [ ] Test LLM dialogue generation with one concept (Quote)
- [ ] Tune prompts for Schemer-style questioning
- [ ] Implement simple mastery evaluation logic

#### Phase 2: UI Integration (Week 3)
- [ ] Design and build session UI component
- [ ] Connect to graph visualizer
- [ ] Implement "Start Learning" flow
- [ ] Add progress indicators
- [ ] Test end-to-end with real user

#### Phase 3: Adaptive Logic (Week 4)
- [ ] Implement difficulty adaptation
- [ ] Add misconception detection
- [ ] Build scaffolding system
- [ ] Test on multiple concepts

#### Phase 4: Multi-Concept Integration (Week 5)
- [ ] Prerequisite referencing in dialogue
- [ ] Exercise integration after mastery
- [ ] Unlocking and celebration animations
- [ ] Full graph progression testing

#### Phase 5: Advanced Features (Week 6+)
- [ ] Trace visualization for recursion
- [ ] Spaced repetition scheduling
- [ ] Progress analytics and insights
- [ ] Mobile responsive design

---

### Success Metrics

**How do we know this works?**

1. **Completion rate:** % of learners who master concepts vs. give up
2. **Time to mastery:** How long does it take to demonstrate understanding?
3. **Retention:** Do learners remember after 1 week? 1 month?
4. **Misconception correction:** Are common errors detected and fixed?
5. **User feedback:** Do learners feel they truly understand vs. just memorized?

**Comparison baseline:** Traditional "read and click" approach

**Target:** 
- 80%+ completion rate
- 90%+ retention after 1 week
- 75%+ learners report "genuine understanding"

---

### Key Design Principles

1. **Socratic, not lecturing** - Ask questions, don't give answers
2. **Concrete, not abstract** - Show examples, not definitions
3. **Adaptive, not rigid** - Adjust to learner's level
4. **Encouraging, not judgmental** - Celebrate insights, scaffold struggles
5. **Earned, not claimed** - Mastery must be demonstrated
6. **Connected, not isolated** - Reference prerequisites, link to exercises
7. **Spaced, not crammed** - Review over time to build lasting understanding

---

### Open Questions

**1. LLM reliability:** Can we trust LLM evaluation of correctness?
- **Mitigation:** Use multiple evaluations, confidence thresholds, human review of edge cases

**2. Gaming the system:** What if learners just guess until they pass?
- **Mitigation:** Track attempt patterns, require explanations not just answers

**3. Scope of dialogue:** How long should a session be?
- **Mitigation:** Start with 10-15 minute sessions, allow "save and resume"

**4. Accessibility:** How do we support learners with different backgrounds?
- **Mitigation:** Adaptive difficulty, optional prerequisite review, multiple explanation styles

**5. Cost:** LLM API calls for every interaction?
- **Mitigation:** Cache common question-answer pairs, use smaller models for evaluation, optimize prompt length

---

## Next.js Implementation: Interactive Graph Visualizer

### Migration Decision

After evaluating visualization approaches, we decided to build a modern web application using **Next.js 15** with the App Router. This provides:

1. **Modern React patterns** - Server and client components
2. **TypeScript support** - Type safety throughout
3. **Component architecture** - Reusable, testable UI components
4. **Fast development** - Hot module reloading, built-in dev server
5. **Production ready** - Optimized builds, static export capability

**Alternative considered:** Static HTML + vanilla JavaScript (as prototyped in `pcg-visualizer.html`)
- **Pros:** Simple, no build step, works anywhere
- **Cons:** Hard to maintain as features grow, no component reusability, manual DOM manipulation

**Decision:** Next.js provides better foundation for the rich interactive features we're planning (Socratic dialogue, progress tracking, exercise integration).

---

### Technology Stack

#### Core Framework
- **Next.js 15.1.6** - React framework with App Router
- **React 19** - Latest React features
- **TypeScript** - Type safety and better DX

#### Visualization
- **Cytoscape.js 3.32.1** - Graph visualization library
- **cytoscape-dagre 2.5.0** - Hierarchical layout algorithm

**Why Cytoscape.js?** (Re-evaluation in React context)
- Excellent API for graph manipulation
- Works well with React (ref-based initialization)
- Rich styling and interaction capabilities
- Built-in support for DAG layouts
- Performance suitable for our 33-node graph

#### UI Components
- **shadcn/ui** - High-quality React components
  - Card, Badge, Button components
- **Tailwind CSS 3** - Utility-first styling
- **Radix UI** - Headless component primitives (via shadcn)

---

### Application Structure

```
learning/
├── app/
│   ├── components/
│   │   ├── ConceptGraph.tsx        # Cytoscape graph visualization
│   │   └── ConceptDetails.tsx      # Sidebar with concept details
│   ├── layout.tsx                   # Root layout with fonts
│   ├── page.tsx                     # Main page (graph + sidebar)
│   └── globals.css                  # Global styles
├── paip-chapter-1/
│   └── concept-graph.json          # PCG data source
├── components/
│   └── ui/                          # shadcn components
│       ├── badge.tsx
│       ├── button.tsx
│       └── card.tsx
└── NOTES.md                         # This file
```

---

### Component Architecture

#### 1. ConceptGraph.tsx

**Purpose:** Renders the interactive graph visualization using Cytoscape.js

**Key features:**
- Client-side component (`'use client'`)
- Initializes Cytoscape with ref-based mounting
- Maps concept data to Cytoscape nodes/edges
- Handles layout switching (breadthfirst, dagre, cose, circle, grid)
- Implements interaction logic:
  - Click node → highlight full prerequisite chain
  - Click background → clear selection
  - Predecessor highlighting (all ancestors, not just immediate)
  
**Visual design:**
- Color coding by difficulty:
  - 🟢 Green (#4CAF50) - Basic
  - 🔵 Blue (#2196F3) - Intermediate  
  - 🔴 Red (#F44336) - Advanced
- Selected node: Orange border
- Prerequisites: Purple highlights on nodes and edges
- Unrelated nodes: Faded to 20% opacity

**Graph direction:** Edges are **semantically stored** as `{from: "dependent", to: "prerequisite"}` but **visually reversed** to show learning flow (arrows point from prerequisites to dependents).

**Props:**
```typescript
{
  data: ConceptGraphData,      // PCG JSON data
  onNodeClick?: (id: string) => void  // Callback when node clicked
}
```

#### 2. ConceptDetails.tsx

**Purpose:** Displays detailed information about the selected concept in the sidebar

**Key features:**
- Shows concept name, description, difficulty badge
- Lists prerequisites with badges
- Displays learning objectives (from Pass 2 data)
- Shows key insights (from Pass 2 data)
- "Start Learning" button (placeholder for future Socratic dialogue)

**States handled:**
- No selection: "Select a Concept" prompt
- Concept selected: Full details display

**Props:**
```typescript
{
  concept: Concept | null,
  onStartLearning?: (id: string) => void
}
```

#### 3. page.tsx (Main Application)

**Purpose:** Orchestrates the graph and sidebar components

**Key features:**
- State management for selected concept ID
- 70/30 split layout (graph : sidebar)
- Header with title and chapter info
- Passes concept data from JSON to components
- Handles "Start Learning" callback (currently shows alert)

**Layout structure:**
```
┌─────────────────────────────────────────┐
│ Header: Pedagogical Concept Graph      │
├───────────────────────┬─────────────────┤
│                       │                 │
│  ConceptGraph (70%)   │  Details (30%)  │
│                       │                 │
│  [Interactive graph]  │  [Concept info] │
│                       │  [Prerequisites]│
│                       │  [Objectives]   │
│                       │  [Start button] │
└───────────────────────┴─────────────────┘
```

---

### Data Flow

```
concept-graph.json
  ↓
page.tsx (loads JSON)
  ↓
  ├→ ConceptGraph.tsx (renders graph)
  │    ↓
  │    User clicks node
  │    ↓
  │    onNodeClick(conceptId)
  │    ↓
  └→ page.tsx (updates selectedConceptId state)
       ↓
       ConceptDetails.tsx (displays selected concept)
```

---

### Key Implementation Decisions

#### 1. Predecessor Highlighting (Full Path to Root)

**Problem:** Initially, clicking a node only highlighted immediate prerequisites, not the full learning path.

**Solution:** Use Cytoscape's `node.predecessors()` method to get ALL ancestors:

```typescript
const allPrerequisites = node.predecessors('node');  // All ancestor nodes
const allEdges = node.predecessors('edge');           // All edges in path
```

**Result:** Clicking "Variables" now highlights the complete chain: Symbols → Function Application → Variables, all the way back to root concepts.

#### 2. Dagre Layout Integration

**Problem:** Initial attempt to use dagre layout failed with "No such layout `dagre` found"

**Solution:** Import and register the dagre extension:

```typescript
import dagre from 'cytoscape-dagre';

if (typeof cytoscape !== 'undefined') {
  cytoscape.use(dagre);
}
```

**Why the check?** Prevents errors during SSR (server-side rendering) where `window` doesn't exist.

#### 3. Client vs Server Components

**Decision:** ConceptGraph must be a client component (`'use client'`) because:
- Cytoscape requires DOM access (browser-only)
- Uses React hooks (useState, useEffect, useRef)
- Handles user interactions

**Implication:** Can't use Next.js server-side data fetching in this component. Instead, data is loaded in parent (page.tsx) and passed as props.

#### 4. Layout Switching

Users can choose between 5 layout algorithms:

1. **Breadthfirst** - Classic tree layout, shows hierarchy clearly
2. **Dagre** ⭐ - Best for DAGs, good spacing, respects direction
3. **COSE (Force-directed)** - Physics-based, organic look
4. **Circle** - All nodes in circle, shows connections
5. **Grid** - Orderly grid, less semantic meaning

**Default:** Breadthfirst (most intuitive for learning paths)

**Most recommended:** Dagre (specifically designed for directed acyclic graphs)

---

### Current Features ✅

**Graph Visualization:**
- [x] Render all 33 concepts as nodes
- [x] Show 45 prerequisite relationships as directed edges
- [x] Color-code by difficulty level
- [x] Multiple layout algorithms
- [x] Smooth animations between layouts

**Interactions:**
- [x] Click node to select
- [x] Highlight full prerequisite chain (all ancestors)
- [x] Highlight prerequisite edges in path
- [x] Fade unrelated nodes
- [x] Click background to deselect

**Details Sidebar:**
- [x] Show concept name and description
- [x] Display difficulty badge with color
- [x] List prerequisites
- [x] Show learning objectives (when available)
- [x] Show key insights (when available)
- [x] "Start Learning" button (placeholder)

**Data Integration:**
- [x] Load from concept-graph.json
- [x] Support Pass 1 data (structure)
- [x] Support Pass 2 data (pedagogy) for concepts that have it
- [x] TypeScript type definitions for data shape

---

### Known Issues & Limitations

#### 1. Pass 2 Data Incomplete
**Issue:** Only 3 of 33 concepts have full pedagogical enrichment (learning objectives, mastery indicators, examples)

**Impact:** Most concepts show basic info only

**Solution:** Complete Pass 2 enrichment for remaining 30 concepts (future work)

#### 2. No Progress Tracking
**Issue:** Can't mark concepts as "mastered" or "in progress"

**Impact:** Users can't track their learning journey

**Solution:** Implement progress tracking with localStorage (planned - see "Learning Path Progression" section above)

#### 3. No Socratic Dialogue
**Issue:** "Start Learning" button just shows an alert

**Impact:** No active learning experience yet

**Solution:** Implement Peirastic AI dialogue system (planned - see "Peirastic AI" section above)

#### 4. No Exercise Integration
**Issue:** Pass 3 exercise data not displayed anywhere

**Impact:** Can't see which exercises test which concepts

**Solution:** Add exercise panel/modal showing related exercises (future work)

#### 5. Mobile Responsiveness
**Issue:** Fixed 70/30 split doesn't work well on small screens

**Impact:** Poor mobile experience

**Solution:** Add responsive breakpoints, collapsible sidebar

---

### Development Workflow

#### Setup
```bash
cd learning
npm install
```

#### Run Development Server
```bash
npm run dev
```

Then open: http://localhost:3000

#### Build for Production
```bash
npm run build
npm start
```

#### Type Checking
```bash
npx tsc --noEmit
```

---

### Performance Considerations

#### Current Performance
- **Graph rendering:** ~100-200ms for 33 nodes (fast)
- **Layout calculation:** 
  - Breadthfirst: ~50ms
  - Dagre: ~100-150ms (more complex algorithm)
  - COSE: ~500ms+ (iterative physics simulation)
- **Interaction latency:** <16ms (60 FPS)

#### Scaling Concerns
- Current graph (33 nodes, 45 edges) performs well
- If expanding to full PAIP book (all chapters):
  - Estimated: 300-500 concepts
  - May need virtualization or clustering
  - Consider graph database for queries

#### Optimization Strategies (if needed)
1. **Lazy loading:** Only load visible subgraph
2. **Memoization:** Cache layout calculations
3. **Web Workers:** Offload layout computation
4. **Canvas fallback:** Switch from SVG for larger graphs

---

### Next Steps (Implementation Roadmap)

#### Phase 1: Progress Tracking 🎯 *Next Priority*
- [ ] Add localStorage-based progress tracking
- [ ] Implement visual states (locked, ready, in-progress, mastered)
- [ ] Show statistics (X/33 concepts mastered)
- [ ] Highlight "recommended next" concepts
- [ ] Celebrate unlocking new concepts

#### Phase 2: Complete Pass 2 Data
- [ ] Enrich remaining 30 concepts with pedagogy
- [ ] Validate mastery indicators for all concepts
- [ ] Add examples and misconceptions
- [ ] Update concept-graph.json

#### Phase 3: Socratic Dialogue Integration
- [ ] Design ConceptMasterySession component
- [ ] Integrate LLM API (Gemini or GPT-4)
- [ ] Build dialogue UI modal
- [ ] Implement mastery evaluation logic
- [ ] Connect to progress tracking

#### Phase 4: Exercise Integration
- [ ] Display exercises in concept details
- [ ] Show which concepts each exercise tests
- [ ] Link exercises to mastery indicators
- [ ] Provide exercise session flow

#### Phase 5: Polish & Production
- [ ] Mobile responsive design
- [ ] Accessibility improvements (keyboard nav, screen readers)
- [ ] Performance optimization
- [ ] User testing and feedback
- [ ] Deploy to production

---

### Lessons Learned (Next.js Implementation)

#### 1. Cytoscape + React = Ref-based Initialization
Can't treat Cytoscape like a React component. Must use `useRef` for container and manual initialization in `useEffect`.

#### 2. 'use client' is Necessary for Interactive Components
Any component using browser APIs, event handlers, or React hooks needs `'use client'` directive in Next.js App Router.

#### 3. Import Registration Timing Matters
Register Cytoscape extensions (like dagre) immediately after import, before trying to use them in layouts.

#### 4. TypeScript Catches Data Shape Mismatches
Strongly typing the PCG data structure helped catch inconsistencies between Pass 1/2/3 data formats.

#### 5. Incremental Migration Works Well
Starting with a simple HTML prototype (pcg-visualizer.html), then migrating to React components, allowed us to validate the visualization approach before committing to the full framework.

#### 6. shadcn/ui Accelerates UI Development
Pre-built, customizable components (Card, Badge, Button) saved significant time compared to building from scratch.

---

### Comparison: HTML Prototype vs Next.js Implementation

| Aspect | HTML Prototype | Next.js Implementation |
|--------|----------------|------------------------|
| **Setup time** | 0 (just open in browser) | 15 min (install deps) |
| **Code organization** | Single file, mixed concerns | Modular components |
| **Maintainability** | Difficult (no structure) | Easy (clear separation) |
| **Type safety** | None | Full TypeScript |
| **State management** | Global vars + DOM queries | React state + props |
| **UI components** | Manual HTML + CSS | shadcn/ui + Tailwind |
| **Extensibility** | Hard (tightly coupled) | Easy (component props) |
| **Production ready** | No (prototype only) | Yes (build + deploy) |

**Verdict:** HTML prototype was perfect for rapid validation. Next.js is the right choice for the production application.

---

### Technical Debt & Future Refactoring

#### 1. Consolidate Graph Data Structure
Currently have three separate JSON files (pass1, pass2-sample, pass3). Should:
- Create `merge_pcg.py` utility (as discussed in earlier sections)
- Generate single `paip-chapter-1-complete.json`
- Update components to use merged structure

#### 2. Extract Graph Logic into Custom Hook
ConceptGraph.tsx is getting large. Consider:
```typescript
function useConceptGraph(data, containerRef, options) {
  // Initialize Cytoscape
  // Handle interactions
  // Manage selection state
  return { cy, selectedNode, ... }
}
```

#### 3. Centralize Difficulty Colors
Currently hardcoded in multiple places. Create:
```typescript
// utils/theme.ts
export const DIFFICULTY_COLORS = {
  basic: '#4CAF50',
  intermediate: '#2196F3',
  advanced: '#F44336',
} as const;
```

#### 4. Add Error Boundaries
Cytoscape can throw errors (invalid data, layout failures). Wrap components in error boundaries for better UX.

#### 5. Implement Proper Loading States
Currently, graph just appears. Should show:
- Loading spinner while Cytoscape initializes
- Skeleton UI while data loads
- Error message if data fetch fails

---

## Recent Improvements & Implementation Log

### Model Upgrade: Gemini 2.5 Flash (2025-01-07)

**Change:** Upgraded the Socratic dialogue LLM from `gemini-2.0-flash-exp` to `gemini-2.5-flash`

**File modified:** `learning/app/api/socratic-dialogue/route.ts`

**Rationale:**
- Gemini 2.5 Flash is described as "fast and intelligent model with best price-performance"
- Better reasoning capabilities for Socratic questioning
- Improved response quality while maintaining low latency

**Implementation:**
```typescript
model: genAI.getGenerativeModel({ 
  model: "gemini-2.5-flash"  // Previously: gemini-2.0-flash-exp
})
```

**Impact:**
- Users should experience higher quality Socratic dialogue
- Better misconception detection and correction
- More natural, context-aware responses

---

### UX Improvement: Auto-Focus Textarea After LLM Response

**Problem:** Users had to manually click the textarea after each LLM response to continue typing, breaking the conversational flow.

**Solution:** Implemented auto-focus using React refs and useEffect

**File modified:** `learning/app/components/SocraticDialogue.tsx`

**Implementation:**
1. Added `textareaRef` using `useRef<HTMLTextAreaElement>(null)`
2. Created `useEffect` that triggers on `isLoading` state change
3. Automatically focuses textarea when loading completes

```typescript
// Auto-focus textarea when loading completes
useEffect(() => {
  if (!isLoading && textareaRef.current) {
    textareaRef.current.focus();
  }
}, [isLoading]);
```

**Impact:**
- Seamless conversation flow
- No manual clicking required between exchanges
- Cursor ready immediately after LLM responds

**User feedback:** "Fucking amazing!"

---

### Structured Mastery Assessment: Tracking Learning Progress (2025-01-07)

**Problem:** After implementing the Socratic dialogue system, we realized there was no automated way to determine when a learner had actually mastered a concept. The LLM would say "Great job!" but:
- We couldn't track which specific mastery indicators were demonstrated
- We didn't know when ALL indicators were satisfied
- We couldn't automatically mark concepts as mastered in the UI
- Progress couldn't be saved or visualized

**The Question:** How can we programmatically evaluate mastery during a Socratic dialogue?

**Options Considered:**

1. **Structured JSON Output** ⭐ *Selected*
   - LLM returns both message and mastery assessment in JSON
   - Single API call per exchange
   - Gemini supports JSON schema natively
   - Progressive skill tracking across conversation
   
2. **Function Calling / Tool Use**
   - LLM calls `mark_indicator_demonstrated` function
   - More flexible, incremental tracking
   - But more complex implementation
   
3. **Separate Evaluation API Call**
   - Second API call to evaluate after each student response
   - Clean separation of concerns
   - But 2x API calls (cost + latency)

**Solution Implemented:** Structured JSON Output with JSON Schema

**Implementation Details:**

Modified `/api/socratic-dialogue/route.ts` to request structured evaluation:

```typescript
body: JSON.stringify({
  contents: geminiContents,
  generationConfig: {
    temperature: 0.7,
    maxOutputTokens: 800,
    responseMimeType: 'application/json',
    responseSchema: {
      type: 'object',
      properties: {
        message: {
          type: 'string',
          description: 'The Socratic dialogue response'
        },
        mastery_assessment: {
          type: 'object',
          properties: {
            indicators_demonstrated: {
              type: 'array',
              items: { type: 'string' },
              description: 'Array of skill IDs demonstrated in this exchange'
            },
            confidence: {
              type: 'number',
              description: 'Confidence level (0-1) in the assessment'
            },
            ready_for_mastery: {
              type: 'boolean',
              description: 'True if student has demonstrated sufficient mastery'
            },
            next_focus: {
              type: 'string',
              description: 'Which skill or area to focus on next'
            }
          },
          required: ['indicators_demonstrated', 'confidence', 'ready_for_mastery']
        }
      },
      required: ['message', 'mastery_assessment']
    }
  }
})
```

**Example LLM Response:**
```json
{
  "message": "Excellent reasoning! You clearly understand how quote prevents evaluation...",
  "mastery_assessment": {
    "indicators_demonstrated": ["quote_syntax", "evaluation_blocking"],
    "confidence": 0.9,
    "ready_for_mastery": false,
    "next_focus": "Let's explore when to use quote in practice..."
  }
}
```

**Component Integration:**

Updated `SocraticDialogue.tsx` to:
1. Track `demonstratedSkills` as a Set (accumulates across conversation)
2. Track `readyForMastery` boolean state
3. Show progress bar: "X / Y skills demonstrated"
4. Display green progress bar that fills as skills are demonstrated
5. Show "Mark as Mastered" button when `ready_for_mastery: true`

**Progress Visualization:**
```
Progress: 2 / 5 skills demonstrated
[████████░░░░░░░░░░░░░░░] 40%

✨ Ready for mastery!  [Mark as Mastered]
```

**Bug Fix: Concepts Without Mastery Indicators**

**Issue discovered:** "Interactive REPL" concept has no `mastery_indicators` defined (only 3 concepts in concept-graph.json have full pedagogical enrichment). When testing with this concept:
- The LLM correctly returned `ready_for_mastery: true`
- But the "Mark as Mastered" button didn't appear
- Reason: UI condition was `{totalIndicators > 0 && ...}`
- Result: Progress UI was hidden entirely for basic concepts

**Solution:** Modified `SocraticDialogue.tsx` to show two UI modes:

1. **Concepts WITH mastery indicators** (Quote, List Accessors, Recursion):
   - Show progress bar: "2 / 5 skills demonstrated"
   - Track and display individual skills
   - Show "Mark as Mastered" when ready

2. **Concepts WITHOUT mastery indicators** (Interactive REPL, Symbols, etc.):
   - Skip progress bar (no skills to track)
   - Still show "Mark as Mastered" button when LLM determines readiness
   - Fallback UI mode for basic concepts

**Code change:**
```typescript
{totalIndicators > 0 ? (
  // Full progress tracking UI
  <div className="progress-bar">...</div>
) : (
  // Fallback: Just show button when ready
  readyForMastery && (
    <Button onClick={handleMarkAsMastered}>
      Mark as Mastered
    </Button>
  )
)}
```

**Impact:**
- ✅ Works with both enriched and basic concepts
- ✅ Progressive skill tracking for detailed concepts
- ✅ LLM-driven mastery assessment for basic concepts
- ✅ Visual feedback motivates learners
- ✅ Graceful degradation for incomplete pedagogy data

**Next Steps:**
1. Complete Pass 2 enrichment for all 33 concepts (add mastery indicators)
2. Save mastered concepts to localStorage (persist progress)
3. Update graph visualization to show mastered nodes in gold
4. Unlock dependent concepts when mastery achieved
5. Implement spaced repetition for review

**Design Philosophy:**
> Mastery must be **demonstrated**, not claimed. The LLM evaluates understanding through Socratic questioning, tracking specific skills as they're revealed in conversation. The system provides guidance and structure while respecting learner autonomy.

---

## Critical TODOs & Future Directions

### 🚨 Immediate Issues

#### 1. Mastery Not Reflected in Graph Visualization
**Problem:** When a user masters a concept through Socratic dialogue, the graph visualization doesn't update to show this progress.

**Current behavior:**
- User completes dialogue session
- Clicks "Mark as Mastered"
- Modal closes... but graph looks identical
- No visual indication of achievement
- Dependent concepts don't appear "unlocked"

**Impact:**
- No sense of progression
- Can't see which concepts are now available to learn
- Undermines the entire prerequisite system

**Proposed solutions:**
1. **Visual state update:** Change mastered nodes to gold/yellow color
2. **Unlock animation:** Flash or pulse newly-unlocked concepts
3. **Update ready state:** Recalculate which concepts are now "ready to learn"
4. **Stats panel:** Show "X / 33 concepts mastered" counter

**Implementation:**
- Pass `onMasteryAchieved(conceptId)` callback from graph to dialogue
- Update graph state when mastery confirmed
- Re-render Cytoscape with new node styles
- Trigger unlock detection algorithm

**Priority:** 🔴 Critical - Core feature gap

---

#### 2. No Persistence for Mastery Progress
**Problem:** Refresh the page, lose all your progress. Users can't build knowledge over multiple sessions.

**Current behavior:**
- All progress stored only in component state
- Refreshing page resets everything to "unlearned"
- No way to resume learning journey

**Impact:**
- Discourages long-term learning
- Forces completing entire chapter in one sitting
- Can't track learning over days/weeks

**Options:**

**A. Browser localStorage** ⭐ *Simplest*
```typescript
// Save on mastery
localStorage.setItem('pcg-mastery', JSON.stringify({
  conceptId: timestamp,
  ...
}));

// Load on mount
const savedMastery = JSON.parse(localStorage.getItem('pcg-mastery') || '{}');
```

**Pros:**
- No backend required
- Works immediately
- Fast read/write
- ~5-10MB storage (plenty for our data)

**Cons:**
- Lost if user clears browser data
- Can't sync across devices
- No backup/recovery

**B. Backend Database** (Firebase, Supabase, etc.)
**Pros:**
- Persistent across devices
- Can add user accounts
- Analytics on learning patterns
- Backup/restore capability

**Cons:**
- Requires backend setup
- Auth complexity
- Hosting costs
- Slower (network latency)

**Recommendation:** Start with localStorage (A), migrate to DB later if needed

**Priority:** 🟡 High - Quality-of-life feature

---

#### 3. LLM Not Grounding in Textbook Content
**Problem:** The LLM appears to be answering from its general training knowledge, not the specific PAIP Chapter 1 text.

**Observed behavior:**
- Teaching "Interactive REPL" and "Symbols" uses generic Lisp knowledge
- Doesn't reference specific examples from Norvig's text
- Misses book's unique pedagogical style and examples
- May contradict or miss nuances from the original material

**Impact:**
- Dialogue diverges from textbook's teaching approach
- Students learning different examples/terminology than in book
- Loses value of Norvig's carefully crafted pedagogy
- Can't answer "Where can I read more about this?"

**Root cause:** Our prompt doesn't include the actual textbook content, only the metadata we extracted (concept names, learning objectives, etc.)

**Proposed solutions:**

**Option A: Quote Relevant Sections in Prompt** 🔸 *Simpler*
```typescript
// In buildSocraticPrompt():
const relevantText = getTextbookSection(conceptData.section); // e.g., "1.1"

return `You are teaching from "Paradigms of AI Programming" by Peter Norvig.

**Concept:** ${conceptData.name}
**Section:** ${conceptData.section}

**Relevant excerpt from the textbook:**
---
${relevantText}
---

Use examples and terminology FROM THIS TEXT when teaching.
Reference page numbers when appropriate.
...`
```

**Pros:**
- Simple to implement
- Works with existing infrastructure
- LLM has full context in prompt

**Cons:**
- Large token usage (PAIP sections can be long)
- May exceed context window for complex concepts
- Manual extraction of section text needed

**Option B: RAG (Retrieval-Augmented Generation)** 🔹 *More Robust*

1. **Pre-process:** Chunk PAIP Chapter 1 into semantic sections
2. **Embed:** Convert chunks to vectors (e.g., OpenAI embeddings)
3. **Store:** Vector database (Pinecone, Weaviate, or simple in-memory)
4. **Query-time:** When teaching a concept:
   - Embed the concept + current dialogue
   - Retrieve top-K most relevant textbook chunks
   - Include in LLM prompt

```typescript
async function getRelevantTextbookChunks(concept, conversationHistory) {
  const query = `${concept.name} ${concept.description} ${getLastUserMessage(conversationHistory)}`;
  
  const results = await vectorDB.query({
    vector: await embed(query),
    topK: 3,
    filter: { chapter: 1, section: concept.section }
  });
  
  return results.map(r => r.text).join('\n---\n');
}
```

**Pros:**
- Only retrieves relevant content (efficient tokens)
- Handles long textbooks (not limited by context window)
- More accurate grounding (semantic search finds best examples)
- Can reference specific passages with citations

**Cons:**
- Requires vector database setup
- Embedding API costs (one-time for textbook, ongoing for queries)
- More complex architecture
- Chunking strategy matters (need to experiment)

**Option C: Hybrid Approach** ⭐ *Recommended*
- Start with **Option A** for immediate improvement
- Manually extract key sections for each concept
- Store in `concept-graph.json` as `textbook_excerpt` field
- Later migrate to **Option B** (RAG) when scaling to multiple chapters

**Implementation Plan:**

**Phase 1 (Quick win):**
1. Extract relevant passages from `paip-chapter-1.md` for each concept
2. Add `textbook_excerpt` field to concept-graph.json
3. Include excerpt in Socratic dialogue prompt
4. Test that LLM uses book's examples

**Phase 2 (Scalable):**
1. Chunk entire PAIP book (all chapters)
2. Generate embeddings (OpenAI or open-source)
3. Set up vector store (start with in-memory, move to Pinecone/Weaviate later)
4. Implement RAG retrieval in API route
5. Compare quality vs. Phase 1 approach

**Success metrics:**
- LLM references specific examples from book
- Uses Norvig's terminology consistently
- Can point users to relevant pages/sections
- Student feedback: "This feels like the book is teaching me"

**Priority:** 🟡 High - Quality and authenticity of learning content

---

### ✅ Visual Mastery Tracking: Graph Reflects Learning Progress (2025-01-07)

**Problem SOLVED:** Users could master concepts through Socratic dialogue, but the graph visualization didn't update to show this progress.

**Previous behavior:**
- User completes dialogue session
- Clicks "Mark as Mastered"
- Modal closes... but graph looks identical ❌
- No visual indication of achievement
- Dependent concepts don't appear "unlocked"

**Now implemented:** Full mastery visualization with persistence! ✨

**Implementation Details:**

**1. State Management in page.tsx**
```typescript
const [masteredConcepts, setMasteredConcepts] = useState<Set<string>>(new Set());

// Load from localStorage on mount
useEffect(() => {
  const saved = localStorage.getItem('pcg-mastery');
  if (saved) {
    const parsed = JSON.parse(saved);
    setMasteredConcepts(new Set(parsed));
  }
}, []);

// Save to localStorage whenever it changes
useEffect(() => {
  if (masteredConcepts.size > 0) {
    localStorage.setItem('pcg-mastery', JSON.stringify([...masteredConcepts]));
  }
}, [masteredConcepts]);
```

**2. Callback Chain**
```
SocraticDialogue: User clicks "Mark as Mastered"
        ↓
onMasteryAchieved(conceptId) callback
        ↓
page.tsx: Updates masteredConcepts Set
        ↓
ConceptGraph: Receives updated masteredConcepts prop
        ↓
Cytoscape re-renders with mastered styling
```

**3. Visual Design (ConceptGraph.tsx)**
```typescript
// Add mastery class to nodes
const isMastered = masteredConcepts?.has(concept.id) || false;
return {
  data: { ... },
  classes: isMastered ? 'mastered' : '',
};

// Cytoscape styling
{
  selector: 'node.mastered',
  style: {
    'background-color': '#FFD700',  // Gold for achievement
    'border-width': '3px',
    'border-color': '#FFA500',      // Orange border
    'color': '#000',                // Black text (contrast)
  },
}
```

**What users experience now:**
1. ✅ Complete Socratic dialogue session
2. ✅ Click "Mark as Mastered" → Alert confirms + modal closes
3. ✅ **Graph node turns GOLD instantly** 🎉
4. ✅ Progress persists across page refreshes (localStorage)
5. ✅ Clear visual distinction between mastered/unmastered concepts
6. ✅ Sense of accomplishment and progression

**Visual States:**
- **Unmastered (Basic):** Green circle
- **Unmastered (Intermediate):** Blue circle
- **Unmastered (Advanced):** Red circle
- **Mastered (Any difficulty):** 🟡 **Gold with orange border** (stands out!)

**Data Persistence:**
- Storage: Browser localStorage
- Key: `'pcg-mastery'`
- Format: JSON array of concept IDs `["interactive_repl", "symbols", ...]`
- Survives: Page refresh, browser restart
- Lost if: User clears browser data (acceptable for MVP)

**Performance:**
- localStorage read/write: <1ms (negligible)
- Graph re-render on mastery: ~50-100ms (smooth)
- No backend calls required (instant feedback)

**User Feedback:**
> "Works! See attached [screenshot showing gold node]"

**Impact:**
- ✅ Immediate visual feedback reinforces learning
- ✅ Users can track progress across sessions
- ✅ Gold color creates sense of achievement
- ✅ Fulfills core requirement from Critical TODOs

**What's Next:**
- [ ] Calculate "ready to learn" concepts (prerequisites satisfied)
- [ ] Highlight newly-unlocked concepts when mastery achieved
- [ ] Show statistics: "X / 33 concepts mastered"
- [ ] Implement "recommended next" visual state (pulsing glow)
- [ ] Add celebration animation on mastery

**Files Modified:**
- `learning/app/page.tsx` - State management + localStorage persistence
- `learning/app/components/ConceptGraph.tsx` - Visual styling for mastered nodes
- `learning/app/components/SocraticDialogue.tsx` - Callback integration

**Commit:** "Add visual mastery tracking to concept graph"

---

### 🎙️ Voice Interface: Gemini Live Integration

**Problem:** Typing back-and-forth in Socratic dialogue can feel tedious, especially for longer learning sessions.

**Proposed solution:** Integrate Gemini Live API for voice-based learning

**Benefits:**
- **Natural conversation:** Speak your answers instead of typing
- **Lower friction:** Faster response times
- **More engaging:** Feels like talking to a real tutor
- **Accessibility:** Better for learners with typing difficulties
- **Multimodal:** Can discuss code while looking at screen

**Implementation considerations:**
1. **Audio capture:** Use Web Audio API to record user speech
2. **Streaming:** Send audio chunks to Gemini Live in real-time
3. **Audio playback:** Stream LLM voice responses back to user
4. **Fallback:** Keep text interface as alternative
5. **Controls:** Push-to-talk vs continuous listening
6. **Privacy:** Clear user consent for audio recording

**Architecture sketch:**
```typescript
class VoiceEnabledDialogue {
  audioStream: MediaStream;
  geminiLiveSession: GeminiLiveSession;
  
  async startVoiceMode() {
    // Request microphone permission
    this.audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
    // Initialize Gemini Live session
    this.geminiLiveSession = await geminiLive.connect({
      model: "gemini-2.5-flash",
      config: {
        responseModality: "audio",
        speechConfig: {
          voiceConfig: { prebuiltVoiceConfig: { voiceName: "tutor-voice" } }
        }
      }
    });
    
    // Stream audio bidirectionally
    this.geminiLiveSession.sendAudio(this.audioStream);
    this.geminiLiveSession.onAudio(audio => this.playback(audio));
  }
}
```

**UI design:**
- Toggle between text/voice mode
- Visual indicator when listening
- Waveform visualization during speech
- Option to see text transcript
- "Repeat that?" button if user misses something

**Challenges:**
- Handling ambient noise and interruptions
- Managing conversation state across modalities
- Cost implications (voice API usage)
- Network latency for real-time streaming

**Priority:** Medium-high (could be game-changing for UX)

**Estimated effort:** 2-3 weeks (including testing and refinement)

---

### 🎛️ Model Selector: Optimize Experience Per Use Case

**Problem:** Different Gemini models have vastly different characteristics:
- **Speed:** Flash vs Pro vs Ultra
- **Cost:** Varies 10-100x
- **Capabilities:** Reasoning depth, context window, multimodal support
- **Response style:** Concise vs verbose, formal vs casual

**Issue:** One-size-fits-all model selection doesn't serve all learners equally well.

**Proposed solution:** Allow users to choose LLM model based on their needs

**Use cases:**
1. **Beginner mode** - Gemini 2.0 Flash Thinking
   - Patient, detailed explanations
   - More scaffolding
   - Slower pace acceptable
   
2. **Quick review mode** - Gemini 2.5 Flash
   - Fast, concise responses
   - Skip obvious questions
   - Efficient for spaced repetition
   
3. **Deep learning mode** - Gemini 2.0 Pro
   - Complex reasoning traces
   - Detailed misconception analysis
   - Multi-step problem decomposition
   
4. **Experimental mode** - Latest experimental models
   - Cutting-edge capabilities
   - Users opt-in to instability

**Implementation:**

```typescript
// Add model selector to SocraticDialogue component
const AVAILABLE_MODELS = [
  { 
    id: "gemini-2.5-flash",
    name: "Fast & Efficient",
    description: "Quick responses, great for review",
    icon: "⚡"
  },
  {
    id: "gemini-2.0-flash-thinking-exp",
    name: "Patient Tutor",
    description: "Detailed explanations, best for beginners",
    icon: "🧠"
  },
  {
    id: "gemini-2.0-pro",
    name: "Deep Reasoning",
    description: "Complex problem solving",
    icon: "🎓"
  }
] as const;

function ModelSelector({ selected, onChange }) {
  return (
    <div className="model-selector">
      {AVAILABLE_MODELS.map(model => (
        <button
          key={model.id}
          onClick={() => onChange(model.id)}
          className={selected === model.id ? 'active' : ''}
        >
          <span className="icon">{model.icon}</span>
          <span className="name">{model.name}</span>
          <span className="description">{model.description}</span>
        </button>
      ))}
    </div>
  );
}
```

**API changes:**
```typescript
// POST /api/socratic-dialogue
{
  conceptId: string,
  conversationHistory: Message[],
  conceptData: any,
  model?: string  // NEW: optional model override
}
```

**Persistence:**
- Save user's preferred model in localStorage
- Allow per-session overrides
- Track which models users find most effective

**Analytics opportunities:**
- Which models lead to better mastery outcomes?
- Do beginners actually prefer slower, detailed models?
- Cost vs. effectiveness tradeoffs

**UI placement:**
- Settings menu in dialogue header
- Tooltip explaining differences
- Show estimated response time per model

**Challenges:**
- API key management (different models, different quotas)
- Cost control (prevent abuse of expensive models)
- Prompt adaptation (different models may need different prompting styles)
- Consistency (switching mid-session could be jarring)

**Priority:** Medium (nice-to-have, not blocking core functionality)

**Estimated effort:** 1 week (UI + API + testing)

---

### Other TODOs (Carried Forward)

From earlier sections, still pending:

#### Progress Tracking (Phase 1)
- [ ] Track masteredConcepts in localStorage
- [ ] Visual distinction for mastered (gold + checkmark)
- [ ] Stats panel showing mastered/in-progress/ready/locked counts
- [ ] Click concept to mark as mastered/in-progress

#### Smart Recommendations (Phase 2)
- [ ] Implement `getReadyConcepts(mastered)` algorithm
- [ ] Add "Recommended Next" visual state (pulsing glow)
- [ ] Sort recommendations by difficulty + unlock potential
- [ ] Display recommended concepts in sidebar

#### Complete Pass 2 Data
- [ ] Enrich remaining 30 concepts with pedagogy
- [ ] Validate mastery indicators for all concepts
- [ ] Add examples and misconceptions
- [ ] Update concept-graph.json

#### Exercise Integration (Phase 4)
- [ ] Display exercises in concept details
- [ ] Show which concepts each exercise tests
- [ ] Link exercises to mastery indicators
- [ ] Provide exercise session flow

---

### Appendix: Package Versions

```json
{
  "dependencies": {
    "next": "^15.1.6",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "cytoscape": "^3.32.1",
    "cytoscape-dagre": "^2.5.0"
  },
  "devDependencies": {
    "typescript": "^5.7.3",
    "@types/node": "^22.10.5",
    "@types/react": "^19.0.6",
    "@types/react-dom": "^19.0.2",
    "tailwindcss": "^3.4.17",
    "postcss": "^8.4.49",
    "autoprefixer": "^10.4.20"
  }
}
```

---

*Last updated: 2025-01-06*
*See CONTEXT.md for complete project design document*
# Pedagogical Concept Graph (PCG) - Visualization Notes

## Overview

This document captures design decisions and technical discussions around visualizing the Pedagogical Concept Graph for PAIP Chapter 1.

## Visualization Library Selection

### Libraries Evaluated

We considered three JavaScript visualization libraries for rendering the PCG:

#### 1. **Cytoscape.js** ⭐ *Selected*
- **Strengths:**
  - Excellent for directed acyclic graphs (DAGs)
  - Built-in layouts specifically for hierarchical graphs (breadthfirst, dagre)
  - Easy to style nodes and edges
  - Good performance for medium-sized graphs (33 nodes)
  - Rich interaction API (click, hover, selection)
  - Well-documented and actively maintained
  
- **Use cases:** Network diagrams, dependency graphs, prerequisite trees
- **Verdict:** Best fit for PCG visualization

#### 2. **D3.js**
- **Strengths:**
  - Most flexible and powerful
  - Complete control over every visual aspect
  - Beautiful, custom visualizations possible
  
- **Weaknesses:**
  - Steeper learning curve
  - More code required for basic features
  - Need to implement graph layout algorithms manually
  
- **Use cases:** Custom, highly-tailored visualizations; data journalism
- **Verdict:** Overkill for our needs

#### 3. **Sigma.js**
- **Strengths:**
  - Optimized for large graphs (thousands of nodes)
  - WebGL rendering for performance
  
- **Weaknesses:**
  - Less suitable for DAGs
  - Fewer built-in hierarchical layouts
  - Better for network exploration than learning paths
  
- **Use cases:** Social networks, large-scale graph exploration
- **Verdict:** Not ideal for structured learning graphs

### Final Decision: Cytoscape.js

**Rationale:** Cytoscape.js offers the best balance of ease-of-use, built-in support for hierarchical layouts, and features specifically suited for dependency/prerequisite graphs.

---

## Visualization Approaches Considered

We identified three potential visualization strategies corresponding to the three passes of PCG generation:

### Option A: Structure Only (Pass 1) ⭐ *Selected*
- **Data source:** `paip-chapter-1-pcg-pass1.json`
- **Shows:**
  - Concept nodes with names and difficulty levels
  - Prerequisite edges (dependency relationships)
  - Basic metadata (section, description)
- **Color coding:** By difficulty (Basic/Intermediate/Advanced)
- **Layout:** Hierarchical (breadthfirst or dagre)
- **Interactions:**
  - Click node → show details
  - Highlight dependencies when selected
  - Filter by difficulty
  - Multiple layout options

**Why we chose this:** Clean, focused, and sufficient for understanding the learning structure. Avoids overwhelming users with too much information upfront.

### Option B: Structure + Mastery (Pass 1 + Pass 2)
- Everything from Option A, plus:
  - Mastery indicators for each concept
  - Learning objectives
  - Example code snippets on hover/click
  - Misconceptions and key insights
- **Complexity:** Medium
- **Use case:** More detailed learning support

### Option C: Complete View (All 3 Passes)
- Everything from Options A & B, plus:
  - Exercise-to-concept mappings
  - Exercise difficulty and estimated time
  - Multiple solution approaches
  - Common mistakes and hints
- **Complexity:** High
- **Use case:** Complete learning platform with integrated exercises

**Decision:** Start with Option A, incrementally add complexity later if needed.

---

## Graph Direction Convention: A Critical Design Decision

### The Problem

During implementation, we discovered an important ambiguity in how to represent the graph edges:

**Semantic meaning vs. Visual flow**

The JSON data represents edges as:
```json
{"from": "prefix_notation", "to": "interactive_repl", "type": "requires"}
```

This means: **"prefix_notation requires interactive_repl"** (semantically correct ✓)

However, when visualized, this creates arrows pointing:
```
prefix_notation → interactive_repl
```

This makes `interactive_repl` look like a **leaf** (dead end) rather than a **root** (starting point).

### The Confusion

For a **learning path visualization**, we typically want:
- Arrows to show "what you can learn next"
- Start at prerequisites (roots), follow arrows forward to advanced concepts
- Natural flow: `interactive_repl → prefix_notation` (learn REPL first, THEN prefix notation)

But our semantic meaning is backwards from the visual learning flow!

### The Solution: Flip Arrows at Render Time

**Decision:** Keep the data structure semantic meaning, but reverse arrow direction during visualization.

**Why this approach:**
1. **Data stays semantically correct:** "X requires Y" is intuitive in code
2. **Visualization shows learning progression:** Arrows flow from prerequisites to dependent concepts
3. **Best of both worlds:** Semantic correctness + visual intuitiveness

**Implementation:**
```javascript
// In visualizer code:
elements: [
  ...data.edges.map(e => ({
    data: { 
      source: e.to,    // FLIP: prerequisite as source
      target: e.from,  // FLIP: dependent concept as target
      type: e.type
    }
  }))
]
```

### Query Implications

**Important:** This reversal is **only for visualization**. The underlying data structure remains optimal for all common queries:

#### Query 1: What prerequisites does X need?
```javascript
function getPrerequisites(nodeId) {
  return edges
    .filter(e => e.from === nodeId)
    .map(e => e.to);
}
// No inversion needed ✓
```

#### Query 2: I finished X, what's next?
```javascript
function whatCanILearnNext(completedNodeId) {
  return edges
    .filter(e => e.to === completedNodeId)
    .map(e => e.from);
}
// No inversion needed ✓
```

#### Query 3: Full dependency tree for X
```javascript
function getAllPrerequisites(nodeId) {
  // BFS/DFS following edges where e.from === nodeId
  // No inversion needed ✓
}
```

#### Query 4: What depends on X?
```javascript
function getDependents(nodeId) {
  return edges
    .filter(e => e.to === nodeId)
    .map(e => e.from);
}
// No inversion needed ✓
```

**Conclusion:** The data structure "X requires Y" supports all queries naturally. We only flip arrows for visual intuition—the semantic model stays clean.

---

## Implementation Details

### File Structure
```
learning/
├── paip-chapter-1-pcg-pass1.json   # Graph data
├── pcg-visualizer.html              # Interactive visualizer
└── NOTES.md                         # This file
```

### Visualizer Features

#### Core Interactions
- **Node click:** Display detailed information (ID, section, difficulty, prerequisites, description)
- **Dependency highlighting:** When node selected, highlight prerequisites (purple), fade unrelated nodes
- **Empty space click:** Clear highlights and selections

#### Controls
- **Layout selector:** Choose between 5 layout algorithms
  - Breadthfirst (hierarchical)
  - Dagre (hierarchical with better spacing)
  - Force-directed (COSE)
  - Circle
  - Grid
- **Difficulty filter:** Show only Basic/Intermediate/Advanced concepts
- **Reset button:** Return to default view

#### Visual Design
- **Color coding:**
  - 🟢 Green: Basic concepts
  - 🔵 Blue: Intermediate concepts
  - 🔴 Red: Advanced concepts
- **Selection indicator:** Orange border, increased size
- **Dependency highlight:** Purple border
- **Faded state:** 20% opacity for unrelated nodes

#### Statistics Panel
- Total concepts: 33
- Breakdown by difficulty
- Total dependencies: 45
- Maximum depth: 6

### Running the Visualizer

```bash
cd learning
python -m http.server 8000
```

Then open: http://localhost:8000/pcg-visualizer.html

---

## Future Enhancements

### Potential Additions (from Option B/C)

1. **Mastery indicators:** Show learning objectives and assessment criteria on hover
2. **Exercise integration:** Link exercises to concepts they test
3. **Progress tracking:** Mark concepts as "learned" or "in progress"
4. **Learning path suggestions:** Recommend optimal learning sequences
5. **Search functionality:** Find concepts by name/keyword
6. **Export views:** Save current graph view as image/PDF
7. **Multiple chapters:** Support for other PAIP chapters beyond Chapter 1

### Technical Improvements

1. **Responsive design:** Better mobile/tablet support
2. **Animation controls:** Speed up/slow down layout animations
3. **Custom layouts:** Implement domain-specific layout algorithm optimized for learning graphs
4. **Keyboard navigation:** Arrow keys to navigate between connected concepts
5. **Zoom/pan persistence:** Remember view state across sessions

---

## Lessons Learned

### 1. Graph Direction Matters
The direction of edges in a dependency graph has both **semantic** and **visual** implications. Design your data model for semantic clarity, then adapt the visualization to match user expectations.

### 2. Start Simple
We consciously chose Option A (structure only) over Options B/C. It's easier to add complexity than to remove it. The simple version is already useful and provides a solid foundation.

### 3. Interactive Exploration > Static Diagrams
The ability to filter, highlight dependencies, and explore different layouts makes the graph much more useful than a static image. Interactivity is worth the implementation effort.

### 4. Library Choice Matters
Cytoscape.js made this implementation straightforward. Trying to build this with D3.js would have taken 3-5x more code. Choose tools that match your problem domain.

---

## References

- **Cytoscape.js Documentation:** https://js.cytoscape.org/
- **PAIP Book:** Norvig, Peter. "Paradigms of Artificial Intelligence Programming" (1992)
- **Graph Layout Algorithms:** Sugiyama, Dagre, Force-directed (COSE)
