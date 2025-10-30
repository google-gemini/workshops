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

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

type Concept = {
  id: string;
  name: string;
  description: string;
  difficulty: string;
  prerequisites: string[];
  learning_objectives?: string[];
  mastery_indicators?: any[];
  examples?: any[];
  misconceptions?: any[];
  key_insights?: any[];
};

type MasteryRecord = {
  conceptId: string;
  masteredAt: number;
};

type ConceptDetailsProps = {
  concept: Concept | null;
  onStartLearning?: (conceptId: string) => void;
  masteryRecord?: MasteryRecord | null;
  conceptStatus?: 'mastered' | 'recommended' | 'ready' | 'locked' | null;
  allConcepts?: Concept[];
  masteredConcepts?: Map<string, MasteryRecord>;
  recommendedConcepts?: Set<string>;
  readyConcepts?: Set<string>;
  lockedConcepts?: Set<string>;
  onConceptClick?: (conceptId: string) => void;
  embeddingsPath?: string; // Not used here, but passed down from parent
};

// Compute full prerequisite chain with topological sort
function computePrerequisiteChain(
  conceptId: string,
  allConcepts: Concept[],
  masteredConcepts: Map<string, MasteryRecord>
): string[] {
  const conceptMap = new Map(allConcepts.map(c => [c.id, c]));
  const visited = new Set<string>();
  const chain: string[] = [];

  function dfs(id: string) {
    if (visited.has(id)) return;
    if (masteredConcepts.has(id)) return; // Stop at mastered concepts
    
    visited.add(id);
    const concept = conceptMap.get(id);
    if (!concept) return;

    // Visit prerequisites first (DFS post-order gives us topological sort)
    for (const prereqId of concept.prerequisites) {
      dfs(prereqId);
    }

    // Don't include the target concept itself
    if (id !== conceptId) {
      chain.push(id);
    }
  }

  dfs(conceptId);
  return chain;
}

export default function ConceptDetails({ 
  concept, 
  onStartLearning, 
  masteryRecord, 
  conceptStatus,
  allConcepts = [],
  masteredConcepts = new Map(),
  recommendedConcepts = new Set(),
  readyConcepts = new Set(),
  lockedConcepts = new Set(),
  onConceptClick,
}: ConceptDetailsProps) {
  if (!concept) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle>Select a Concept</CardTitle>
          <CardDescription>Click on any node in the graph to see details</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const difficultyColors: Record<string, string> = {
    basic: 'bg-green-500',
    intermediate: 'bg-blue-500',
    advanced: 'bg-red-500',
  };

  const statusConfig: Record<string, { label: string; color: string; icon: string }> = {
    mastered: { label: 'Mastered', color: 'bg-yellow-500', icon: '✓' },
    recommended: { label: 'Recommended Next', color: 'bg-green-500', icon: '⭐' },
    ready: { label: 'Ready to Learn', color: 'bg-blue-500', icon: '✅' },
    locked: { label: 'Locked', color: 'bg-gray-400', icon: '🔒' },
  };

  return (
    <Card className="h-full overflow-auto">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <CardTitle>{concept.name}</CardTitle>
              {conceptStatus && statusConfig[conceptStatus] && (
                <Badge className={`${statusConfig[conceptStatus].color} text-white`}>
                  {statusConfig[conceptStatus].icon} {statusConfig[conceptStatus].label}
                </Badge>
              )}
            </div>
            <CardDescription className="mt-2">{concept.description}</CardDescription>
            {masteryRecord && (
              <div className="mt-2 text-xs text-green-600 font-medium">
                ✓ Mastered {new Date(masteryRecord.masteredAt).toLocaleDateString('en-US', { 
                  month: 'short', 
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            )}
          </div>
          <Badge className={difficultyColors[concept.difficulty]}>{concept.difficulty}</Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Prerequisites - Full Learning Path */}
        {(() => {
          const prereqChain = computePrerequisiteChain(concept.id, allConcepts, masteredConcepts);
          if (prereqChain.length === 0) return null; // Suppress if empty
          
          return (
            <div>
              <h3 className="font-semibold text-sm mb-2">
                Learning Path to {concept.name}:
              </h3>
              <p className="text-xs text-slate-500 mb-3">
                Complete these concepts in order (from foundation to advanced)
              </p>
              <div className="flex flex-wrap gap-2">
                {prereqChain
                  .map((prereqId) => {
                    const prereqConcept = allConcepts.find(c => c.id === prereqId);
                    if (!prereqConcept) return null;

                    const isMastered = masteredConcepts.has(prereqId);
                    const isReady = readyConcepts.has(prereqId) || recommendedConcepts.has(prereqId);
                    const isLocked = lockedConcepts.has(prereqId);

                    return {
                      prereqId,
                      prereqConcept,
                      isMastered,
                      isReady,
                      isLocked,
                      // Priority: mastered=1, ready=2, locked=3
                      priority: isMastered ? 1 : isReady ? 2 : 3,
                    };
                  })
                  .filter(item => item !== null)
                  .sort((a, b) => a!.priority - b!.priority) // Sort by status priority
                  .map(({ prereqId, prereqConcept, isMastered, isReady, isLocked }) => {
                    let badgeClass = 'cursor-pointer hover:opacity-80 transition-opacity';
                    let icon = '';
                    
                    if (isMastered) {
                      badgeClass += ' bg-yellow-400 text-black border-orange-400';
                      icon = '✓ ';
                    } else if (isReady) {
                      badgeClass += ' bg-green-500 text-white border-green-600 font-semibold';
                      icon = '→ ';
                    } else if (isLocked) {
                      badgeClass += ' bg-slate-300 text-slate-600 opacity-60';
                      icon = '🔒 ';
                    }

                    return (
                      <Badge
                        key={prereqId}
                        className={badgeClass}
                        onClick={() => onConceptClick?.(prereqId)}
                      >
                        {icon}{prereqConcept.name}
                      </Badge>
                    );
                  })}
              </div>
            </div>
          );
        })()}

        {/* Learning Objectives */}
        {concept.learning_objectives && concept.learning_objectives.length > 0 && (
          <div>
            <h3 className="font-semibold text-sm mb-2">Learning Objectives:</h3>
            <ul className="list-disc list-inside space-y-1 text-sm">
              {concept.learning_objectives.map((obj, i) => (
                <li key={i}>{obj}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Key Insights */}
        {concept.key_insights && concept.key_insights.length > 0 && (
          <div>
            <h3 className="font-semibold text-sm mb-2">Key Insights:</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-slate-600">
              {concept.key_insights.map((insight, i) => (
                <li key={i}>{insight}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Start Learning Button */}
        {onStartLearning && (
          <Button onClick={() => onStartLearning(concept.id)} className="w-full mt-4">
            Start Learning
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
