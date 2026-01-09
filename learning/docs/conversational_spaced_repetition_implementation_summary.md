# Conversational Spaced Repetition Implementation Summary

This document details the implementation of the **Conversational Spaced Repetition** system, a proactive learning tool that replaces traditional flashcards with natural dialogue.

## Motivation: The Future of Learning & Review

Flashcards (like Anki) are highly effective because they utilize two core principles of learning:
1.  **Active Recall**: You must retrieve information from your brain, not just recognize it.
2.  **Spaced Repetition**: You review concepts at optimal intervals based on forgetting curves.

**The Problem**: While effective, flashcards are often boring, tedious to create, and isolate knowledge into fragments.

**Our Solution**: The future of this textbook app is to allow students to review concepts seamlessly through conversation. We have built a system that maintains the mathematical efficiency of spaced repetition but removes the friction.
-   **No Manual Cards**: You don't create cards; the agent automatically extracts what is worth remembering.
-   **Conversational Review**: Instead of flipping a card, the agent says, *"Hey, remember that concept we discussed last week? How does it work?"*
-   **Natural Assessment**: You don't grade yourself ("Easy/Hard"). The agent interprets your answer and grades your understanding naturally.

This enables efficient learning using spaced repetition and active recall without the chore of creating flashcards.

---

## Implementation Status

All core components of the design have been completed:

- [x] **Memory Store**: `lib/memory-store.ts` handles persistence of memories and FSRS state.
- [x] **FSRS Scheduler**: `lib/spaced-repetition.ts` implements the scheduling algorithm.
- [x] **Review API**: `/api/review-dialogue` drives the multi-concept review conversation.
- [x] **Review UI**: `ReviewDialogue.tsx` provides the chat interface and learning dashboard.
- [x] **Learning Integration**: `socratic-dialogue` API now writes initial memories during learning.

---

## Active Recall Implementation

Active recall is implemented not through static Q&A, but through a **Review Dialogue**. The agent is prompted to "probe" specific concepts that are due for review.

### How it Works
1.  The system identifies "due" concepts where retrievability < 90%.
2.  The **Review Dialogue** component opens a chat session focused on these concepts.
3.  The agent uses **past memories** (notes from previous learning sessions) to ask personalized questions.
4.  As the user replies, the agent internally scores their "understanding" (0.0 - 1.0). (Note: this "LLM-as-a-judge" approach can be finnicky. It's worth discussing whether this is the best approach to grade user's understanding.)
5.  This score immediately updates the FSRS "stability" metric, pushing the next review further out (if successful) or bringing it closer (if struggling).

### Relevant Code
- **UI Component**: [ReviewDialogue.tsx](../app/components/ReviewDialogue.tsx) - Handles the chat interface and progress tracking.
- **Backend Logic**: [Review Dialogue Route](../app/api/review-dialogue/route.ts) - The system prompt here (`buildReviewPrompt`) instructs the AI to:
    > "naturally probe their recall... focus on concepts with lower retention first... assess their understanding from their responses (0-1 scale)"

---

## Spaced Repetition System (FSRS) implementation

We implemented a simplified **Free Spaced Repetition Scheduler (FSRS)** algorithm. It calculates two key metrics for every concept:
1.  **Stability (S)**: The number of days until retrievability drops to 90%.
2.  **Retrievability (R)**: The probability (0-1) that the user can currently recall the concept.

### The Algorithm
The core formula for the forgetting curve is exponential decay:

$$ R(t) = 0.9^{\frac{t}{S}} $$

Where:
*   $t$ is days elapsed since the last review.
*   $S$ is the stability (days).
*   $0.9$ is the target retrievability constant.

### Review Scheduling
A concept is marked "Due" when $R < 0.9$. The scheduling logic sorts reviews by **priority**, which is calculated based on:
1.  Low Retrievability (most urgent).
2.  High Difficulty (harder concepts prioritized).
3.  Overdue time (concepts ignored for too long get a boost).

### Relevant Code
The core logic resides in [lib/spaced-repetition.ts](../lib/spaced-repetition.ts).

**Key Functions:**
- [`calculateRetrievability`](../lib/spaced-repetition.ts#L55): Implements the exponential decay formula.
- [`getReviewPriority`](../lib/spaced-repetition.ts#L112): Determines which concepts to show first.
- [`calculateNextInterval`](../lib/spaced-repetition.ts#L203): Updates stability based on the review outcome (Understanding score 0-1).

### Spacing Logic (Code Snippet)
Here is how the next interval is calculated based on the agent's assessment:

```typescript
// From lib/spaced-repetition.ts

export function calculateNextInterval(
  currentStability: number,
  understanding: number, // 0.0 to 1.0 from agent assessment
  difficulty: number
): number {
  let multiplier: number;
  
  if (understanding >= 0.7) {
    // Good recall - large increase (2.2-2.5x)
    multiplier = 2.0 + understanding;
  } else if (understanding >= 0.3) {
    // Medium recall - maintenance (0.8-1.5x)
    multiplier = 0.5 + understanding;
  } else {
    // Poor recall - harsh reset (0.2-0.5x)
    multiplier = 0.2 + understanding;
  }
  
  // Harder concepts (higher difficulty) get smaller intervals
  const difficultyAdjustment = 1 - (difficulty * 0.3);
  
  return currentStability * multiplier * difficultyAdjustment;
}
```

---

## Future Work

While the core loop is functional, the following items from the original plan remains as future enhancements:

1.  **Backend Sync**: Currently uses `localStorage`. Need to move `saveConceptStates` to a proper database.
2.  **Voice Integration**: Allow reviews to happen via voice mode (using Gemini Live) for seamless conversation.
3.  **Parameter Tuning**: Advanced tuning of FSRS parameters (decay factor, etc.) based on aggregate user data.
