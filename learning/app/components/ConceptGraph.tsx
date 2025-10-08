'use client';

import { useEffect, useRef, useState } from 'react';
import cytoscape, { Core, EdgeDefinition, NodeDefinition } from 'cytoscape';
import dagre from 'cytoscape-dagre';

// Register the dagre layout
if (typeof cytoscape !== 'undefined') {
  cytoscape.use(dagre);
}

type Concept = {
  id: string;
  name: string;
  description: string;
  difficulty: string;
  prerequisites: string[];
};

type Edge = {
  from: string;
  to: string;
  type: string;
};

type ConceptGraphData = {
  metadata: any;
  concepts: Concept[];
  edges: Edge[];
};

type MasteryRecord = {
  conceptId: string;
  masteredAt: number;
};

type ConceptGraphProps = {
  data: ConceptGraphData;
  onNodeClick?: (conceptId: string) => void;
  masteredConcepts?: Map<string, MasteryRecord>;
  recommendedConcepts?: Set<string>;
  readyConcepts?: Set<string>;
  lockedConcepts?: Set<string>;
};

export default function ConceptGraph({ 
  data, 
  onNodeClick, 
  masteredConcepts,
  recommendedConcepts,
  readyConcepts,
  lockedConcepts,
}: ConceptGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [layout, setLayout] = useState('breadthfirst');

  useEffect(() => {
    if (!containerRef.current) return;

    // Color mapping for difficulty levels
    const difficultyColors: Record<string, string> = {
      basic: '#4CAF50',
      intermediate: '#2196F3',
      advanced: '#F44336',
    };

    // Transform data for Cytoscape
    const nodes: NodeDefinition[] = data.concepts.map((concept) => {
      const isMastered = masteredConcepts?.has(concept.id) || false;
      const isRecommended = recommendedConcepts?.has(concept.id) || false;
      const isReady = readyConcepts?.has(concept.id) || false;
      const isLocked = lockedConcepts?.has(concept.id) || false;

      let classes = '';
      if (isMastered) classes = 'mastered';
      else if (isRecommended) classes = 'recommended';
      else if (isReady) classes = 'ready';
      else if (isLocked) classes = 'locked';

      return {
        data: {
          id: concept.id,
          label: concept.name,
          difficulty: concept.difficulty,
          description: concept.description,
          prerequisites: concept.prerequisites,
        },
        classes,
      };
    });

    // FLIP arrow direction for visual learning flow
    const edges: EdgeDefinition[] = data.edges.map((edge) => ({
      data: {
        source: edge.to, // FLIPPED: prerequisite as source
        target: edge.from, // FLIPPED: dependent concept as target
        type: edge.type,
      },
    }));

    // Initialize Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements: [...nodes, ...edges],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (ele) => difficultyColors[ele.data('difficulty')] || '#999',
            label: 'data(label)',
            color: '#fff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '10px',
            'font-weight': 'bold',
            width: '60px',
            height: '60px',
            'text-wrap': 'wrap',
            'text-max-width': '55px',
          },
        },
        {
          selector: 'node.mastered',
          style: {
            'background-color': '#FFD700', // Gold for mastered concepts
            'border-width': '3px',
            'border-color': '#FFA500', // Orange border
            'color': '#000', // Black text for better contrast on gold
          },
        },
        {
          selector: 'node.recommended',
          style: {
            'border-width': '3px',
            'border-color': '#4CAF50', // Bright green border
            'box-shadow': '0 0 20px rgba(76, 175, 80, 0.6)',
          },
        },
        {
          selector: 'node.ready',
          style: {
            opacity: 1.0,
          },
        },
        {
          selector: 'node.locked',
          style: {
            opacity: 0.4,
          },
        },
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#ccc',
            'target-arrow-color': '#ccc',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': '3px',
            'border-color': '#FF9800',
          },
        },
        {
          selector: 'node.highlighted',
          style: {
            'border-width': '3px',
            'border-color': '#9C27B0',
          },
        },
        {
          selector: 'edge.highlighted',
          style: {
            'line-color': '#9C27B0',
            'target-arrow-color': '#9C27B0',
            'width': 3,
          },
        },
        {
          selector: '.faded',
          style: {
            opacity: 0.2,
          },
        },
      ],
      layout: {
        name: layout,
        directed: true,
        padding: 50,
        spacingFactor: 1.5,
      },
    });

    // Node click handler
    cy.on('tap', 'node', (event) => {
      const node = event.target;
      const nodeId = node.id();
      setSelectedNode(nodeId);

      // Reset styles
      cy.elements().removeClass('highlighted faded');

      // Get ALL ancestors (full prerequisite chain to root)
      // Using breadth-first search to traverse all incoming edges
      const allPrerequisites = node.predecessors('node');
      allPrerequisites.addClass('highlighted');

      // Also highlight the edges in the path
      const allEdges = node.predecessors('edge');
      allEdges.addClass('highlighted');

      // Fade unrelated nodes
      const related = node.union(allPrerequisites).union(allEdges);
      cy.elements().difference(related).addClass('faded');

      // Callback
      if (onNodeClick) {
        onNodeClick(nodeId);
      }
    });

    // Background click handler
    cy.on('tap', (event) => {
      if (event.target === cy) {
        cy.elements().removeClass('highlighted faded');
        setSelectedNode(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [data, layout, onNodeClick, masteredConcepts]);

  const handleLayoutChange = (newLayout: string) => {
    setLayout(newLayout);
    if (cyRef.current) {
      cyRef.current.layout({ name: newLayout, directed: true, padding: 50 }).run();
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* Controls */}
      <div className="p-4 bg-slate-100 border-b flex gap-2 items-center">
        <span className="text-sm font-medium">Layout:</span>
        <select
          value={layout}
          onChange={(e) => handleLayoutChange(e.target.value)}
          className="px-3 py-1 border rounded text-sm"
        >
          <option value="breadthfirst">Breadthfirst</option>
          <option value="dagre">Dagre</option>
          <option value="cose">Force-directed</option>
          <option value="circle">Circle</option>
          <option value="grid">Grid</option>
        </select>
      </div>

      {/* Graph container */}
      <div ref={containerRef} className="flex-1 w-full" />
    </div>
  );
}
