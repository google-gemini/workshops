'use client';

import { useState } from 'react';
import ConceptGraph from './components/ConceptGraph';
import ConceptDetails from './components/ConceptDetails';
import SocraticDialogue from './components/SocraticDialogue';
import conceptGraphData from '../paip-chapter-1/concept-graph.json';

export default function Home() {
  const [selectedConceptId, setSelectedConceptId] = useState<string | null>(null);
  const [dialogueOpen, setDialogueOpen] = useState(false);

  const selectedConcept = selectedConceptId
    ? conceptGraphData.concepts.find((c) => c.id === selectedConceptId) || null
    : null;

  const handleStartLearning = (conceptId: string) => {
    setDialogueOpen(true);
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-slate-900 text-white p-4">
        <h1 className="text-2xl font-bold">Pedagogical Concept Graph</h1>
        <p className="text-sm text-slate-300">PAIP Chapter 1: Introduction to Lisp</p>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Graph (70%) */}
        <div className="flex-[7] border-r">
          <ConceptGraph data={conceptGraphData} onNodeClick={setSelectedConceptId} />
        </div>

        {/* Details sidebar (30%) */}
        <div className="flex-[3] p-4 overflow-auto">
          <ConceptDetails concept={selectedConcept} onStartLearning={handleStartLearning} />
        </div>
      </div>

      {/* Socratic Dialogue Modal */}
      {selectedConcept && (
        <SocraticDialogue
          open={dialogueOpen}
          onOpenChange={setDialogueOpen}
          conceptData={selectedConcept}
        />
      )}
    </div>
  );
}
