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
 * FSRS (Free Spaced Repetition Scheduler) Algorithm Implementation
 * 
 * This module implements a simplified version of the FSRS algorithm for
 * calculating optimal review intervals and memory retrievability.
 * 
 * Key concepts:
 * - Retrievability: Probability that you can recall something (0-1)
 * - Stability: Days until retrievability drops to 90% (increases with reviews)
 * - Difficulty: How hard the concept is for this specific user (0-1)
 */

import { ConceptState } from './memory-store';

// FSRS default parameters (can be tuned per user)
const FSRS_PARAMS = {
  // Desired retrievability threshold (when to review)
  targetRetrievability: 0.9,
  
  // Decay constant for exponential forgetting curve
  decayFactor: 0.9,
  
  // Minimum stability (1 day)
  minStability: 1,
  
  // Maximum stability (1 year)
  maxStability: 365,
};

/**
 * Calculate retrievability (probability of recall) based on time elapsed
 * 
 * Uses exponential decay: R = e^(-t/S * ln(1/0.9))
 * Where:
 *   R = retrievability
 *   t = time elapsed (days)
 *   S = stability (days until R drops to 0.9)
 */
export function calculateRetrievability(state: ConceptState): number {
  if (state.lastReview === 0) {
    // Never reviewed - assume low but not zero retrievability
    return 0.5;
  }
  
  const now = Date.now();
  const elapsedMs = now - state.lastReview;
  const elapsedDays = elapsedMs / (1000 * 60 * 60 * 24);
  
  // Exponential decay formula
  // R(t) = 0.9^(t/S) where S is stability
  const retrievability = Math.pow(FSRS_PARAMS.decayFactor, elapsedDays / state.stability);
  
  return Math.max(0, Math.min(1, retrievability));
}

/**
 * Calculate days until retrievability drops below target threshold
 */
export function getDaysUntilDue(state: ConceptState): number {
  const currentRetrievability = calculateRetrievability(state);
  
  if (currentRetrievability < FSRS_PARAMS.targetRetrievability) {
    // Already due for review
    return 0;
  }
  
  // Calculate when R will drop to target
  // From R(t) = 0.9^(t/S), solve for t when R = targetR
  // t = S * log_0.9(targetR)
  // t = S * ln(targetR) / ln(0.9)
  const daysUntilTarget = state.stability * 
    Math.log(FSRS_PARAMS.targetRetrievability) / 
    Math.log(FSRS_PARAMS.decayFactor);
  
  // Subtract time already elapsed
  const elapsedDays = (Date.now() - state.lastReview) / (1000 * 60 * 60 * 24);
  
  return Math.max(0, daysUntilTarget - elapsedDays);
}

/**
 * Check if a concept is due for review
 */
export function isDue(state: ConceptState): boolean {
  return calculateRetrievability(state) < FSRS_PARAMS.targetRetrievability;
}

/**
 * Priority score for review (higher = more urgent)
 * 
 * Factors:
 * - Lower retrievability = higher priority
 * - Higher difficulty = higher priority
 * - Overdue items get urgency boost
 */
export function getReviewPriority(state: ConceptState): number {
  const retrievability = calculateRetrievability(state);
  
  // Base priority: inverse of retrievability (lower R = higher priority)
  let priority = 1 - retrievability;
  
  // Difficulty boost (harder concepts get priority)
  priority += state.difficulty * 0.2;
  
  // Urgency boost for overdue items
  if (retrievability < FSRS_PARAMS.targetRetrievability) {
    // The more overdue, the more urgent
    const overdueBoost = (FSRS_PARAMS.targetRetrievability - retrievability) * 0.5;
    priority += overdueBoost;
  }
  
  return priority;
}

export interface DueConcept {
  conceptId: string;
  state: ConceptState;
  retrievability: number;
  priority: number;
  daysUntilDue: number;
}

/**
 * Get all concepts that are due for review, sorted by priority
 */
export function getDueForReview(states: Map<string, ConceptState>): DueConcept[] {
  const dueConcepts: DueConcept[] = [];
  
  states.forEach((state, conceptId) => {
    const retrievability = calculateRetrievability(state);
    const priority = getReviewPriority(state);
    const daysUntilDue = getDaysUntilDue(state);
    
    if (isDue(state)) {
      dueConcepts.push({
        conceptId,
        state,
        retrievability,
        priority,
        daysUntilDue,
      });
    }
  });
  
  // Sort by priority (highest first)
  return dueConcepts.sort((a, b) => b.priority - a.priority);
}

/**
 * Get concepts coming up for review soon (within N days)
 */
export function getUpcomingReviews(
  states: Map<string, ConceptState>,
  withinDays: number = 3
): DueConcept[] {
  const upcoming: DueConcept[] = [];
  
  states.forEach((state, conceptId) => {
    const retrievability = calculateRetrievability(state);
    const priority = getReviewPriority(state);
    const daysUntilDue = getDaysUntilDue(state);
    
    // Not due yet, but coming soon
    if (!isDue(state) && daysUntilDue <= withinDays) {
      upcoming.push({
        conceptId,
        state,
        retrievability,
        priority,
        daysUntilDue,
      });
    }
  });
  
  // Sort by days until due (soonest first)
  return upcoming.sort((a, b) => a.daysUntilDue - b.daysUntilDue);
}

/**
 * Calculate the next optimal review interval based on current state and performance
 * 
 * @param currentStability Current stability in days
 * @param understanding How well the user demonstrated understanding (0-1)
 * @param difficulty User-specific difficulty for this concept (0-1)
 * @returns New stability value in days
 */
export function calculateNextInterval(
  currentStability: number,
  understanding: number,
  difficulty: number
): number {
  // Base multiplier depends on understanding level
  // Good recall (>0.7): 2-3x current interval
  // Medium recall (0.3-0.7): 0.8-1.2x (maintain or slight increase)
  // Poor recall (<0.3): Reset to 1-2 days
  
  let multiplier: number;
  
  if (understanding >= 0.7) {
    // Excellent recall - large increase
    // Higher understanding = higher multiplier (2.0 to 3.0)
    multiplier = 2.0 + understanding;
  } else if (understanding >= 0.3) {
    // Medium recall - small adjustment
    // Maps 0.3-0.7 to 0.8-1.2
    multiplier = 0.5 + understanding;
  } else {
    // Poor recall - reset
    // Maps 0-0.3 to 0.2-0.5
    multiplier = 0.2 + understanding;
  }
  
  // Adjust for difficulty (harder concepts need shorter intervals)
  const difficultyAdjustment = 1 - (difficulty * 0.3);
  
  // Calculate new stability
  let newStability = currentStability * multiplier * difficultyAdjustment;
  
  // Clamp to valid range
  newStability = Math.max(FSRS_PARAMS.minStability, newStability);
  newStability = Math.min(FSRS_PARAMS.maxStability, newStability);
  
  return newStability;
}

/**
 * Summary statistics for a user's learning state
 */
export interface LearningStats {
  totalConcepts: number;
  conceptsWithMemories: number;
  dueNow: number;
  dueSoon: number;  // Due within 3 days
  averageRetrievability: number;
  strongestConcept: string | null;
  weakestConcept: string | null;
}

/**
 * Calculate overall learning statistics
 */
export function getLearningStats(states: Map<string, ConceptState>): LearningStats {
  const conceptsArray = Array.from(states.entries());
  
  if (conceptsArray.length === 0) {
    return {
      totalConcepts: 0,
      conceptsWithMemories: 0,
      dueNow: 0,
      dueSoon: 0,
      averageRetrievability: 0,
      strongestConcept: null,
      weakestConcept: null,
    };
  }
  
  let totalRetrievability = 0;
  let dueNow = 0;
  let dueSoon = 0;
  let conceptsWithMemories = 0;
  let strongestRetrievability = -1;
  let weakestRetrievability = 2;
  let strongestConcept: string | null = null;
  let weakestConcept: string | null = null;
  
  conceptsArray.forEach(([conceptId, state]) => {
    const r = calculateRetrievability(state);
    totalRetrievability += r;
    
    if (state.memories.length > 0) {
      conceptsWithMemories++;
    }
    
    if (isDue(state)) {
      dueNow++;
    } else if (getDaysUntilDue(state) <= 3) {
      dueSoon++;
    }
    
    if (r > strongestRetrievability) {
      strongestRetrievability = r;
      strongestConcept = conceptId;
    }
    
    if (r < weakestRetrievability) {
      weakestRetrievability = r;
      weakestConcept = conceptId;
    }
  });
  
  return {
    totalConcepts: conceptsArray.length,
    conceptsWithMemories,
    dueNow,
    dueSoon,
    averageRetrievability: totalRetrievability / conceptsArray.length,
    strongestConcept,
    weakestConcept,
  };
}
