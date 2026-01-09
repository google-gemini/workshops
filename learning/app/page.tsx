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
import ReviewDialogue from './components/ReviewDialogue';

// Memory and spaced repetition imports
import { loadConceptStates, loadConceptStatesWithType, ConceptAssessment } from '@/lib/memory-store';
import { getDueForReview, getLearningStats, getUpcomingReviews, DueConcept } from '@/lib/spaced-repetition';

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

  // Tab navigation state
  const [activeTab, setActiveTab] = useState<'library' | 'review'>('library');

  // Review state
  const [dueForReview, setDueForReview] = useState<DueConcept[]>([]);
  const [upcomingReviews, setUpcomingReviews] = useState<DueConcept[]>([]);
  const [reviewDialogueOpen, setReviewDialogueOpen] = useState(false);

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

  // Load mastered concepts from localStorage AND server on mount
  useEffect(() => {
    if (!selectedLibraryId) return;

    const key = `pcg-mastery-${selectedLibraryId}`;

    // 1. Load from LocalStorage (Fast)
    const saved = localStorage.getItem(key);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        const map = new Map<string, MasteryRecord>(
          Object.entries(parsed).map(([id, record]) => [id, record as MasteryRecord])
        );
        setMasteredConcepts(map);
      } catch (e) {
        console.error('Failed to load mastery data:', e);
      }
    }

    // 2. Sync with Server (Persistence)
    fetch('/api/storage')
      .then(res => res.json())
      .then(data => {
        const serverMastery = data[key];
        if (serverMastery) {
          setMasteredConcepts(prev => {
            const next = new Map(prev); // Start with local data

            // Merge server data (server allows restoration of lost local data)
            Object.entries(serverMastery).forEach(([id, record]) => {
              // Prefer existing local data if conflict? Or server?
              // Since mastery is permanent, if it exists on server, we should have it.
              if (!next.has(id)) {
                next.set(id, record as MasteryRecord);
              }
            });

            // Update localStorage to keep it fresh
            const obj = Object.fromEntries(next.entries());
            localStorage.setItem(key, JSON.stringify(obj));

            return next;
          });
        }
      })
      .catch(err => console.error('Failed to load mastery from server:', err));

  }, [selectedLibraryId]);

  // Check for concepts due for review
  useEffect(() => {
    if (!selectedLibraryId) return;

    // 1. Initial synchronous load (fast, from localStorage)
    const initialStates = loadConceptStates(selectedLibraryId);
    setDueForReview(getDueForReview(initialStates));
    setUpcomingReviews(getUpcomingReviews(initialStates, 3));

    // 2. Async sync with server (ensure data persistence)
    loadConceptStatesWithType(selectedLibraryId).then(syncedStates => {
      setDueForReview(getDueForReview(syncedStates));
      setUpcomingReviews(getUpcomingReviews(syncedStates, 3));
    }).catch(err => console.error('Failed to sync with server:', err));
  }, [selectedLibraryId, reviewDialogueOpen]); // Refresh after review dialogue closes

  const handleStartReviewSession = () => {
    setReviewDialogueOpen(true);
  };

  const handleReviewComplete = (assessments: ConceptAssessment[]) => {
    console.log('Review completed with assessments:', assessments.length);
    // Refresh due concepts after review
    if (selectedLibraryId) {
      const conceptStates = loadConceptStates(selectedLibraryId);
      setDueForReview(getDueForReview(conceptStates));
      setUpcomingReviews(getUpcomingReviews(conceptStates, 3));
    }
  };

  // Save mastered concepts to localStorage whenever it changes
  useEffect(() => {
    if (masteredConcepts.size > 0) {
      // Convert Map to object for JSON storage
      const obj = Object.fromEntries(masteredConcepts.entries());
      const key = `pcg-mastery-${selectedLibraryId}`;
      localStorage.setItem(key, JSON.stringify(obj));

      // Sync to disk
      fetch('/api/storage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [key]: obj })
      }).catch(err => console.error('Failed to sync mastery to disk:', err));
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

  // Build concept name map for ReviewDialogue
  const conceptNames = new Map<string, string>();
  concepts.forEach(c => conceptNames.set(c.id, c.name));

  return (
    <div className="h-screen flex flex-col">
      {/* Header with Tab Navigation */}
      <header className="bg-slate-900 text-white">
        <div className="p-4 pb-0">
          <div className="flex items-center justify-between mb-3">
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

          {/* Tab Navigation */}
          <div className="flex gap-1">
            <button
              onClick={() => setActiveTab('library')}
              className={`px-4 py-2 rounded-t-lg font-medium transition-colors ${activeTab === 'library'
                ? 'bg-white text-slate-900'
                : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
            >
              Library
            </button>
            <button
              onClick={() => setActiveTab('review')}
              className={`px-4 py-2 rounded-t-lg font-medium transition-colors flex items-center gap-2 ${activeTab === 'review'
                ? 'bg-white text-slate-900'
                : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
            >
              Review
              {dueForReview.length > 0 && (
                <span className={`px-2 py-0.5 text-xs rounded-full ${activeTab === 'review'
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-blue-500 text-white'
                  }`}>
                  {dueForReview.length}
                </span>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main content - switches based on active tab */}
      {activeTab === 'library' ? (
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
                    {masteredCount === 1 && "Great start! Keep learning!"}
                    {masteredCount > 1 && masteredCount < 10 && "You're building momentum!"}
                    {masteredCount >= 10 && masteredCount < 20 && "Excellent progress!"}
                    {masteredCount >= 20 && masteredCount < totalConcepts && "You're on fire!"}
                    {masteredCount === totalConcepts && "Chapter Complete! Amazing work!"}
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
      ) : (
        /* Review Tab Content */
        <div className="flex-1 overflow-auto bg-gradient-to-br from-slate-50 to-slate-100 p-6">
          <div className="max-w-4xl mx-auto">
            {/* Review Dashboard Header */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6 hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-slate-800">Review Session</h2>
                  <p className="text-slate-600 mt-1">
                    {dueForReview.length === 0
                      ? "No concepts due for review right now!"
                      : `${dueForReview.length} concept${dueForReview.length > 1 ? 's' : ''} ready for review`}
                  </p>
                </div>
                {dueForReview.length > 0 && (
                  <button
                    onClick={handleStartReviewSession}
                    className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg font-medium transition-all duration-200 flex items-center gap-2 shadow-sm hover:shadow-md"
                  >
                    <span>Start Review</span>
                    <span className="text-blue-200 text-sm">~{Math.ceil(dueForReview.length * 2)} min</span>
                  </button>
                )}
              </div>

              {dueForReview.length === 0 && (
                <div className="text-center py-8">
                  <div className="text-6xl mb-4">🎉</div>
                  <p className="text-lg text-slate-700 font-medium">You're all caught up!</p>
                  <p className="text-sm text-slate-500 mt-2">
                    Keep learning new concepts and they'll appear here when it's time to review.
                  </p>
                  
                  {/* Demo Mode Button */}
                  <div className="mt-6 pt-6 border-t border-slate-200">
                    <p className="text-xs text-slate-400 mb-3">Demo Mode</p>
                    <button
                      onClick={() => {
                        // Inject test data with old timestamps to simulate due reviews
                        const testConcepts = concepts.slice(0, 3); // Take first 3 concepts
                        const key = `pcg-agent-memory-${selectedLibraryId}`;
                        const now = Date.now();
                        const twoDaysAgo = now - (2 * 24 * 60 * 60 * 1000);
                        
                        const testData: Record<string, any> = {};
                        testConcepts.forEach((concept, idx) => {
                          testData[concept.id] = {
                            conceptId: concept.id,
                            stability: 1, // 1 day stability means it's overdue after 1 day
                            difficulty: 0.3 + (idx * 0.1),
                            lastReview: twoDaysAgo - (idx * 12 * 60 * 60 * 1000), // Stagger by 12 hours
                            memories: [
                              {
                                id: crypto.randomUUID(),
                                conceptId: concept.id,
                                content: `Student showed initial understanding of ${concept.name} but needs more practice with edge cases.`,
                                understanding: 0.6 + (idx * 0.1),
                                timestamp: twoDaysAgo - (idx * 12 * 60 * 60 * 1000),
                                context: 'Initial learning session'
                              }
                            ]
                          };
                        });
                        
                        // Save to localStorage and trigger refresh
                        localStorage.setItem(key, JSON.stringify(testData));
                        
                        // Also sync to server
                        fetch('/api/storage', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ [key]: testData })
                        }).catch(err => console.error('Failed to sync:', err));
                        
                        // Force refresh the due concepts
                        const states = new Map(Object.entries(testData));
                        setDueForReview(getDueForReview(states as any));
                        setUpcomingReviews(getUpcomingReviews(states as any, 3));
                      }}
                      className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-sm font-medium transition-colors"
                    >
                      📚 Load Demo Review Data
                    </button>
                    <p className="text-xs text-slate-400 mt-2">
                      Adds 3 concepts with old timestamps to trigger reviews
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Due Now Section */}
            {dueForReview.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6 hover:shadow-md transition-shadow duration-200">
                <h3 className="text-lg font-bold text-slate-800 mb-4">Due Now</h3>
                <div className="space-y-3">
                  {dueForReview.map((due) => {
                    const concept = concepts.find(c => c.id === due.conceptId);
                    const retrievabilityPercent = Math.round(due.retrievability * 100);
                    return (
                      <div
                        key={due.conceptId}
                        className="flex items-center justify-between p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200 hover:border-slate-300 transition-colors duration-200"
                      >
                        <div className="flex-1 min-w-0">
                          <span className="font-medium text-slate-800">
                            {concept?.name || due.conceptId}
                          </span>
                          {due.state.memories.length > 0 && (
                            <p className="text-xs text-slate-500 mt-1 truncate">
                              Last note: "{due.state.memories[due.state.memories.length - 1].content.substring(0, 60)}..."
                            </p>
                          )}
                        </div>
                        <span className={`ml-3 px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap ${retrievabilityPercent < 50
                          ? 'bg-red-100 text-red-700'
                          : retrievabilityPercent < 70
                            ? 'bg-amber-100 text-amber-700'
                            : 'bg-green-100 text-green-700'
                          }`}>
                          {retrievabilityPercent}% retained
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Coming Up Section */}
            {upcomingReviews.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow duration-200">
                <h3 className="text-lg font-bold text-slate-800 mb-4">Coming Up</h3>
                <p className="text-sm text-slate-500 mb-3">Reviews scheduled for the next 3 days</p>
                <div className="space-y-2">
                  {upcomingReviews.map((upcoming) => {
                    const concept = concepts.find(c => c.id === upcoming.conceptId);
                    const daysUntil = Math.ceil(upcoming.daysUntilDue);
                    return (
                      <div
                        key={upcoming.conceptId}
                        className="flex items-center justify-between p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors duration-200"
                      >
                        <span className="text-slate-700 font-medium">
                          {concept?.name || upcoming.conceptId}
                        </span>
                        <span className="text-sm text-slate-500">
                          in {daysUntil} day{daysUntil > 1 ? 's' : ''}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

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
          libraryId={selectedLibraryId}
          onMasteryAchieved={handleMasteryAchieved}
        />
      )}

      {/* Review Dialogue Modal */}
      {dueForReview.length > 0 && (
        <ReviewDialogue
          open={reviewDialogueOpen}
          onOpenChange={setReviewDialogueOpen}
          dueConcepts={dueForReview}
          conceptNames={conceptNames}
          libraryId={selectedLibraryId}
          onReviewComplete={handleReviewComplete}
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
