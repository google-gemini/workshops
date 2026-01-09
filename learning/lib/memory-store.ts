/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Memory Store for Conversational Spaced Repetition
 * 
 * Agent-written memories, stored in localStorage. The agent takes notes
 * after each conversation, extracting what's worth remembering.
 */

export interface Memory {
  id: string;
  conceptId: string;
  content: string;           // Free-form note from agent
  understanding: number;     // 0-1 score extracted by agent
  timestamp: number;
  context?: string;          // What prompted this memory
}

export interface ConceptState {
  conceptId: string;
  stability: number;         // FSRS: days until forgotten (increases with successful reviews)
  difficulty: number;        // FSRS: user-specific difficulty (0-1, higher = harder for this user)
  lastReview: number;        // Timestamp of last review
  memories: Memory[];        // Agent's notes about this concept
}

const STORAGE_KEY_PREFIX = 'pcg-agent-memory-';

/**
 * Get the storage key for a specific library
 */
function getStorageKey(libraryId: string): string {
  return `${STORAGE_KEY_PREFIX}${libraryId}`;
}


/**
 * Load all concept states from localStorage, and sync with server
 */
export async function loadConceptStatesWithType(libraryId: string): Promise<Map<string, ConceptState>> {
  if (typeof window === 'undefined') return new Map();

  const key = getStorageKey(libraryId);
  const localData = loadFromLocalStorage(key);

  // Attempt to fetch from server to get latest state
  try {
    const res = await fetch('/api/storage');
    if (res.ok) {
      const serverDataWrapper = await res.json();
      const serverData = serverDataWrapper[key];

      if (serverData) {
        // Merge server data with local data (server wins if different, simple strategy)
        // In a real app we might want more complex merging logic
        const merged = { ...localData, ...serverData };

        // Update localStorage to match server
        localStorage.setItem(key, JSON.stringify(merged));

        return new Map(Object.entries(merged));
      }
    }
  } catch (e) {
    console.error('Failed to fetch from server:', e);
  }

  return new Map(Object.entries(localData));
}

// Synchronous fallback for components that can't wait (renders using localStorage first)
export function loadConceptStates(libraryId: string): Map<string, ConceptState> {
  if (typeof window === 'undefined') return new Map();
  const key = getStorageKey(libraryId);
  const data = loadFromLocalStorage(key);
  return new Map(Object.entries(data));
}

function loadFromLocalStorage(key: string): Record<string, ConceptState> {
  try {
    const saved = localStorage.getItem(key);
    if (!saved) return {};
    return JSON.parse(saved);
  } catch (e) {
    console.error('Failed to load local data:', e);
    return {};
  }
}

/**
 * Save all concept states to localStorage
 */
export function saveConceptStates(libraryId: string, states: Map<string, ConceptState>): void {
  if (typeof window === 'undefined') return;

  try {
    const obj = Object.fromEntries(states.entries());
    const key = getStorageKey(libraryId);

    // Save to localStorage
    localStorage.setItem(key, JSON.stringify(obj));

    // Sync to disk via API
    fetch('/api/storage', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ [key]: obj })
    }).catch(err => console.error('Failed to sync state to disk:', err));

  } catch (e) {
    console.error('Failed to save concept states:', e);
  }
}

/**
 * Get or create a concept state
 */
export function getConceptState(
  states: Map<string, ConceptState>,
  conceptId: string
): ConceptState {
  const existing = states.get(conceptId);
  if (existing) return existing;

  // Create default state for new concept
  return {
    conceptId,
    stability: 1,        // Start with 1 day stability
    difficulty: 0.3,     // Default mid-range difficulty
    lastReview: 0,       // Never reviewed
    memories: [],
  };
}

/**
 * Add a memory to a concept's state
 */
export function addMemory(
  states: Map<string, ConceptState>,
  conceptId: string,
  memory: Omit<Memory, 'id' | 'timestamp'>
): Map<string, ConceptState> {
  const state = getConceptState(states, conceptId);

  const newMemory: Memory = {
    ...memory,
    id: crypto.randomUUID(),
    timestamp: Date.now(),
  };

  const updatedState: ConceptState = {
    ...state,
    memories: [...state.memories, newMemory],
    lastReview: Date.now(),
  };

  const newStates = new Map(states);
  newStates.set(conceptId, updatedState);
  return newStates;
}

/**
 * Update FSRS parameters after a review
 */
export function updateFSRSParameters(
  states: Map<string, ConceptState>,
  conceptId: string,
  understanding: number // 0-1, where 1 is perfect recall
): Map<string, ConceptState> {
  const state = getConceptState(states, conceptId);

  // FSRS-like parameter update
  // Higher understanding increases stability, lowers difficulty
  // Lower understanding decreases stability, increases difficulty

  // Stability update (simplified FSRS)
  // On good recall (>0.7): multiply stability by 1.5-2.5 based on understanding
  // On poor recall (<0.3): reset to near-initial values
  // In between: small adjustments
  let newStability: number;
  let newDifficulty: number;

  if (understanding >= 0.7) {
    // Good recall - increase stability
    const multiplier = 1.5 + understanding; // 2.2-2.5x for good recall
    newStability = Math.min(state.stability * multiplier, 365); // Cap at 1 year
    newDifficulty = state.difficulty * 0.9; // Concept getting easier
  } else if (understanding <= 0.3) {
    // Poor recall - reset stability
    newStability = 1; // Back to 1 day
    newDifficulty = Math.min(state.difficulty + 0.1, 1); // Concept is harder than thought
  } else {
    // Medium recall - small adjustments
    newStability = state.stability * (0.8 + understanding * 0.4); // 0.92-1.08x
    newDifficulty = state.difficulty; // No change
  }

  const updatedState: ConceptState = {
    ...state,
    stability: newStability,
    difficulty: Math.max(0.1, Math.min(1, newDifficulty)), // Clamp 0.1-1
    lastReview: Date.now(),
  };

  const newStates = new Map(states);
  newStates.set(conceptId, updatedState);
  return newStates;
}

/**
 * Get memories for a specific concept
 */
export function getMemoriesForConcept(
  states: Map<string, ConceptState>,
  conceptId: string
): Memory[] {
  const state = states.get(conceptId);
  return state?.memories || [];
}

/**
 * Get recent memories across all concepts (for context in conversations)
 */
export function getRecentMemories(
  states: Map<string, ConceptState>,
  limit: number = 10
): Memory[] {
  const allMemories: Memory[] = [];

  states.forEach((state) => {
    allMemories.push(...state.memories);
  });

  // Sort by timestamp descending and take the most recent
  return allMemories
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(0, limit);
}

/**
 * Clear all memory data for a library (for testing/reset)
 */
export function clearMemoryData(libraryId: string): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(getStorageKey(libraryId));
}

/**
 * Get concepts with their memories for the review API
 * Returns concept data enriched with memories for multi-concept review conversations
 */
export interface ConceptWithMemories {
  conceptId: string;
  memories: Memory[];
  stability: number;
  difficulty: number;
  lastReview: number;
}

export function getConceptsWithMemories(
  states: Map<string, ConceptState>,
  conceptIds: string[]
): ConceptWithMemories[] {
  return conceptIds.map(conceptId => {
    const state = getConceptState(states, conceptId);
    return {
      conceptId,
      memories: state.memories,
      stability: state.stability,
      difficulty: state.difficulty,
      lastReview: state.lastReview,
    };
  });
}

/**
 * Batch update FSRS parameters for multiple concepts after a review session
 */
export interface ConceptAssessment {
  conceptId: string;
  understanding: number;
  newMemory?: {
    content: string;
    understanding: number;
    context?: string;
  };
}

export function batchUpdateFSRS(
  states: Map<string, ConceptState>,
  assessments: ConceptAssessment[]
): Map<string, ConceptState> {
  let updatedStates = new Map(states);

  for (const assessment of assessments) {
    // Update FSRS parameters
    updatedStates = updateFSRSParameters(
      updatedStates,
      assessment.conceptId,
      assessment.understanding
    );

    // Add new memory if provided
    if (assessment.newMemory) {
      updatedStates = addMemory(updatedStates, assessment.conceptId, {
        conceptId: assessment.conceptId,
        content: assessment.newMemory.content,
        understanding: assessment.newMemory.understanding,
        context: assessment.newMemory.context,
      });
    }
  }

  return updatedStates;
}
