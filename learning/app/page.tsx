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

'use client';

import { useState, useEffect } from 'react';
import ConceptGraph from './components/ConceptGraph';
import ConceptDetails from './components/ConceptDetails';
import SocraticDialogue from './components/SocraticDialogue';
import conceptGraphData from '../paip-chapter-1/concept-graph.json';

type MasteryRecord = {
  conceptId: string;
  masteredAt: number;
};

export default function Home() {
  const [selectedConceptId, setSelectedConceptId] = useState<string | null>(null);
  const [dialogueOpen, setDialogueOpen] = useState(false);
  const [masteredConcepts, setMasteredConcepts] = useState<Map<string, MasteryRecord>>(new Map());

  // Load mastered concepts from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('pcg-mastery');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        // Convert object to Map
        const map = new Map<string, MasteryRecord>(
          Object.entries(parsed).map(([id, record]) => [id, record as MasteryRecord])
        );
        setMasteredConcepts(map);
      } catch (e) {
        console.error('Failed to load mastery data:', e);
      }
    }
  }, []);

  // Save mastered concepts to localStorage whenever it changes
  useEffect(() => {
    if (masteredConcepts.size > 0) {
      // Convert Map to object for JSON storage
      const obj = Object.fromEntries(masteredConcepts.entries());
      localStorage.setItem('pcg-mastery', JSON.stringify(obj));
    }
  }, [masteredConcepts]);

  const selectedConcept = selectedConceptId
    ? conceptGraphData.concepts.find((c) => c.id === selectedConceptId) || null
    : null;

  // Determine status of selected concept
  const getConceptStatus = (conceptId: string | null): 'mastered' | 'recommended' | 'ready' | 'locked' | null => {
    if (!conceptId) return null;
    if (masteredConcepts.has(conceptId)) return 'mastered';
    if (recommendedConceptIds.has(conceptId)) return 'recommended';
    if (readyConcepts.some(c => c.id === conceptId)) return 'ready';
    if (lockedConcepts.some(c => c.id === conceptId)) return 'locked';
    return null;
  };

  const handleStartLearning = (conceptId: string) => {
    setDialogueOpen(true);
  };

  const handleMasteryAchieved = (conceptId: string) => {
    setMasteredConcepts(prev => {
      const next = new Map(prev);
      next.set(conceptId, {
        conceptId,
        masteredAt: Date.now(),
      });
      return next;
    });
  };

  // Calculate statistics
  const totalConcepts = conceptGraphData.concepts.length;
  const masteredCount = masteredConcepts.size;
  const masteredPercent = Math.round((masteredCount / totalConcepts) * 100);

  // Ready concepts: all prerequisites mastered, but not yet mastered itself
  const readyConcepts = conceptGraphData.concepts.filter(c => 
    !masteredConcepts.has(c.id) &&
    c.prerequisites.every(p => masteredConcepts.has(p))
  );

  // Locked concepts: missing at least one prerequisite
  const lockedConcepts = conceptGraphData.concepts.filter(c =>
    !masteredConcepts.has(c.id) &&
    c.prerequisites.some(p => !masteredConcepts.has(p))
  );

  // Recommended concepts: Top 3-5 ready concepts, prioritized by:
  // 1. Difficulty (basic first)
  // 2. Number of concepts they unlock
  const difficultyRank: Record<string, number> = {
    basic: 1,
    intermediate: 2,
    advanced: 3,
  };

  const countUnlocks = (conceptId: string): number => {
    return conceptGraphData.concepts.filter(c =>
      c.prerequisites.includes(conceptId)
    ).length;
  };

  const recommendedConcepts = readyConcepts
    .sort((a, b) => {
      // Sort by difficulty first
      if (a.difficulty !== b.difficulty) {
        return difficultyRank[a.difficulty] - difficultyRank[b.difficulty];
      }
      // Then by unlock potential
      return countUnlocks(b.id) - countUnlocks(a.id);
    })
    .slice(0, 5); // Top 5 recommendations

  const recommendedConceptIds = new Set(recommendedConcepts.map(c => c.id));

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-slate-900 text-white p-4">
        <h1 className="text-2xl font-bold">PAIP Chapter 1: Introduction to Lisp</h1>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Graph (70%) */}
        <div className="flex-[7] border-r">
          <ConceptGraph 
            data={conceptGraphData} 
            onNodeClick={setSelectedConceptId}
            masteredConcepts={masteredConcepts}
            recommendedConcepts={recommendedConceptIds}
            readyConcepts={new Set(readyConcepts.map(c => c.id))}
            lockedConcepts={new Set(lockedConcepts.map(c => c.id))}
          />
        </div>

        {/* Details sidebar (30%) */}
        <div className="flex-[3] p-4 overflow-auto">
          {/* Stats Dashboard */}
          <div className="mb-6 p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200 shadow-sm">
            <h3 className="text-lg font-bold mb-3 text-slate-800">Learning Progress</h3>
            
            {/* Mastery Progress */}
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-slate-700">Concepts Mastered</span>
                <span className="text-sm font-bold text-slate-900">
                  {masteredCount} / {totalConcepts} ({masteredPercent}%)
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-green-500 to-green-600 h-3 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${masteredPercent}%` }}
                />
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-2 mt-4">
              <div className="bg-white p-3 rounded-lg border border-slate-200 text-center">
                <div className="text-2xl font-bold text-green-600">{masteredCount}</div>
                <div className="text-xs text-slate-600 mt-1">Mastered</div>
              </div>
              <div className="bg-white p-3 rounded-lg border border-slate-200 text-center">
                <div className="text-2xl font-bold text-blue-600">{readyConcepts.length}</div>
                <div className="text-xs text-slate-600 mt-1">Ready</div>
              </div>
              <div className="bg-white p-3 rounded-lg border border-slate-200 text-center">
                <div className="text-2xl font-bold text-slate-400">{lockedConcepts.length}</div>
                <div className="text-xs text-slate-600 mt-1">Locked</div>
              </div>
            </div>

            {/* Encouragement Message */}
            {masteredCount > 0 && (
              <div className="mt-4 p-2 bg-green-50 rounded border border-green-200 text-center">
                <span className="text-sm text-green-700 font-medium">
                  {masteredCount === 1 && "🎉 Great start! Keep learning!"}
                  {masteredCount > 1 && masteredCount < 10 && "🚀 You're building momentum!"}
                  {masteredCount >= 10 && masteredCount < 20 && "💪 Excellent progress!"}
                  {masteredCount >= 20 && masteredCount < totalConcepts && "🔥 You're on fire!"}
                  {masteredCount === totalConcepts && "🏆 Chapter Complete! Amazing work!"}
                </span>
              </div>
            )}
          </div>

          <ConceptDetails 
            concept={selectedConcept} 
            onStartLearning={handleStartLearning}
            masteryRecord={selectedConceptId ? masteredConcepts.get(selectedConceptId) || null : null}
            conceptStatus={getConceptStatus(selectedConceptId)}
            allConcepts={conceptGraphData.concepts}
            masteredConcepts={masteredConcepts}
            recommendedConcepts={recommendedConceptIds}
            readyConcepts={new Set(readyConcepts.map(c => c.id))}
            lockedConcepts={new Set(lockedConcepts.map(c => c.id))}
            onConceptClick={setSelectedConceptId}
          />
        </div>
      </div>

      {/* Socratic Dialogue Modal */}
      {selectedConcept && (
        <SocraticDialogue
          open={dialogueOpen}
          onOpenChange={setDialogueOpen}
          conceptData={selectedConcept}
          onMasteryAchieved={handleMasteryAchieved}
        />
      )}
    </div>
  );
}
