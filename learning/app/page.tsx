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

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import ConceptGraph from './components/ConceptGraph';
import ConceptDetails from './components/ConceptDetails';
import SocraticDialogue from './components/SocraticDialogue';
import LibrarySelector from './components/LibrarySelector';

type Library = {
  id: string;
  title: string;
  author: string;
  type: string;
  conceptGraphPath: string;
  embeddingsPath: string;
  description: string;
  color: string;
  workspaceType?: 'python' | 'lisp';
  sourceFile?: string;
  stats: {
    totalConcepts: number;
    estimatedHours: number;
  };
};

type ConceptGraphData = {
  metadata: any;
  concepts?: any[];
  nodes?: any[];
  edges: any[];
};

type MasteryRecord = {
  conceptId: string;
  masteredAt: number;
};

function HomeContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [selectedLibraryId, setSelectedLibraryId] = useState<string | null>(null);
  const [conceptGraphData, setConceptGraphData] = useState<ConceptGraphData | null>(null);
  const [selectedConceptId, setSelectedConceptId] = useState<string | null>(null);
  const [dialogueOpen, setDialogueOpen] = useState(false);
  const [masteredConcepts, setMasteredConcepts] = useState<Map<string, MasteryRecord>>(new Map());

  // Load libraries on mount
  useEffect(() => {
    fetch('/data/libraries.json')
      .then(res => res.json())
      .then(data => {
        setLibraries(data.libraries);
        
        // Priority: URL param > localStorage > show selector
        const urlLibrary = searchParams.get('library');
        if (urlLibrary && data.libraries.find((l: Library) => l.id === urlLibrary)) {
          setSelectedLibraryId(urlLibrary);
        } else {
          const saved = localStorage.getItem('selectedLibrary');
          if (saved && data.libraries.find((l: Library) => l.id === saved)) {
            setSelectedLibraryId(saved);
          }
          // No fallback - show library selector if nothing is set
        }
      })
      .catch(err => console.error('Failed to load libraries:', err));
  }, [searchParams]);

  // Load concept graph when library changes
  useEffect(() => {
    if (!selectedLibraryId) return;
    
    const library = libraries.find(l => l.id === selectedLibraryId);
    if (!library) return;

    fetch(library.conceptGraphPath)
      .then(res => res.json())
      .then(data => setConceptGraphData(data))
      .catch(err => console.error('Failed to load concept graph:', err));
    
    // Update localStorage
    localStorage.setItem('selectedLibrary', selectedLibraryId);
    
    // Only update URL if it's different from current URL param
    const currentUrlLibrary = searchParams.get('library');
    if (currentUrlLibrary !== selectedLibraryId) {
      router.replace(`?library=${selectedLibraryId}`, { scroll: false });
    }
  }, [selectedLibraryId, libraries, router, searchParams]);

  // Load mastered concepts from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(`pcg-mastery-${selectedLibraryId}`);
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
      localStorage.setItem(`pcg-mastery-${selectedLibraryId}`, JSON.stringify(obj));
    }
  }, [masteredConcepts, selectedLibraryId]);

  // Show library selector if not ready
  if (!selectedLibraryId || !conceptGraphData || libraries.length === 0) {
    return (
      <LibrarySelector 
        libraries={libraries}
        onSelect={setSelectedLibraryId}
      />
    );
  }

  const selectedLibrary = libraries.find(l => l.id === selectedLibraryId)!;
  
  // Accept both 'concepts' and 'nodes' field names
  const concepts = conceptGraphData.concepts || conceptGraphData.nodes || [];
  
  const selectedConcept = selectedConceptId
    ? concepts.find((c) => c.id === selectedConceptId) || null
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
  const totalConcepts = concepts.length;
  const masteredCount = masteredConcepts.size;
  const masteredPercent = Math.round((masteredCount / totalConcepts) * 100);

  // Ready concepts: all prerequisites mastered, but not yet mastered itself
  const readyConcepts = concepts.filter(c => 
    !masteredConcepts.has(c.id) &&
    c.prerequisites.every((p: string) => masteredConcepts.has(p))
  );

  // Locked concepts: missing at least one prerequisite
  const lockedConcepts = concepts.filter(c =>
    !masteredConcepts.has(c.id) &&
    c.prerequisites.some((p: string) => !masteredConcepts.has(p))
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
    return concepts.filter(c =>
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
        <div className="flex items-center justify-between">
          <div>
            <button 
              onClick={() => {
                setSelectedLibraryId(null);
                localStorage.removeItem('selectedLibrary');
                router.replace('/', { scroll: false });
              }}
              className="text-sm text-slate-300 hover:text-white mb-1 transition-colors"
            >
              ← Back to Libraries
            </button>
            <h1 className="text-2xl font-bold">{selectedLibrary.title}</h1>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden relative">
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
        {/* On mobile: full-screen overlay when concept selected */}
        {/* On desktop: fixed sidebar */}
        <div className={`
          flex-[3] p-4 overflow-auto
          md:relative md:block
          ${selectedConcept 
            ? 'fixed inset-0 z-50 w-full bg-white' 
            : 'hidden md:block'
          }
        `}>
          {/* Mobile close button */}
          {selectedConcept && (
            <button
              onClick={() => setSelectedConceptId(null)}
              className="md:hidden fixed top-4 right-4 z-10 bg-white rounded-full p-2 shadow-lg border border-slate-200 hover:bg-slate-100"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
          
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
            allConcepts={concepts}
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
          embeddingsPath={selectedLibrary.embeddingsPath}
          workspaceType={selectedLibrary.workspaceType || 'python'}
          initialSourceFile={selectedLibrary.sourceFile || '/data/pytudes/tsp.md'}
          libraryType={selectedLibrary.type}
          onMasteryAchieved={handleMasteryAchieved}
        />
      )}
    </div>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<div className="h-screen flex items-center justify-center">Loading...</div>}>
      <HomeContent />
    </Suspense>
  );
}
