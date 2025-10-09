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

import { useEffect, useRef, useState } from 'react';
import cytoscape, { Core, EdgeDefinition, NodeDefinition } from 'cytoscape';
import dagre from 'cytoscape-dagre';
import fcose from 'cytoscape-fcose';
import cola from 'cytoscape-cola';

// Register the layout plugins
if (typeof cytoscape !== 'undefined') {
  cytoscape.use(dagre);
  cytoscape.use(fcose);
  cytoscape.use(cola);
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
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [layout, setLayout] = useState('grid');

  // Load saved layout preference from localStorage
  useEffect(() => {
    const savedLayout = localStorage.getItem('concept-graph-layout');
    if (savedLayout) {
      setLayout(savedLayout);
    }
  }, []);

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
            color: '#000',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'text-margin-y': 5,
            'font-size': '20px',
            'font-weight': 'bold',
            'text-background-color': '#ffffff',
            'text-background-opacity': 0.85,
            'text-background-padding': '3px',
            width: '25px',
            height: '25px',
            'text-wrap': 'wrap',
            'text-max-width': '120px',
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
            width: '35px', // Larger than regular nodes
            height: '35px',
            'border-width': '4px',
            'border-color': '#4CAF50', // Bright green border
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
            opacity: 0.25, // More faded to show they're not available
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
        padding: 50,
        spacingFactor: 1.5,
      } as any, // Cast to any since different layouts support different options
    });

    // Helper function to highlight prerequisite path
    const highlightPath = (node: any) => {
      // Reset styles
      cy.elements().removeClass('highlighted faded');

      // Get ALL ancestors (full prerequisite chain to root)
      const allPrerequisites = node.predecessors('node');
      allPrerequisites.addClass('highlighted');

      // Also highlight the edges in the path
      const allEdges = node.predecessors('edge');
      allEdges.addClass('highlighted');

      // Fade unrelated nodes
      const related = node.union(allPrerequisites).union(allEdges);
      cy.elements().difference(related).addClass('faded');
    };

    // Hover handler - preview mode (only if nothing is locked)
    cy.on('mouseover', 'node', (event) => {
      if (selectedNode) return; // Don't interfere with locked selection

      // Clear any existing hover timeout
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }

      // Add slight delay to reduce jitter (200ms)
      hoverTimeoutRef.current = setTimeout(() => {
        highlightPath(event.target);
      }, 200);
    });

    // Mouse out handler - clear preview
    cy.on('mouseout', 'node', () => {
      if (selectedNode) return; // Don't interfere with locked selection

      // Clear timeout if user moves away before delay completes
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
        hoverTimeoutRef.current = null;
      }

      // Clear highlights
      cy.elements().removeClass('highlighted faded');
    });

    // Click handler - locked mode (persistent + details panel)
    cy.on('tap', 'node', (event) => {
      const node = event.target;
      const nodeId = node.id();
      setSelectedNode(nodeId);

      // Highlight path
      highlightPath(node);

      // Callback to show details in right panel
      if (onNodeClick) {
        onNodeClick(nodeId);
      }
    });

    // Background click handler - unlock selection
    cy.on('tap', (event) => {
      if (event.target === cy) {
        cy.elements().removeClass('highlighted faded');
        setSelectedNode(null);
      }
    });

    // Cleanup hover timeout on unmount
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
      cy.destroy();
    };

    cyRef.current = cy;
  }, [data, layout, onNodeClick, masteredConcepts]);

  const handleLayoutChange = (newLayout: string) => {
    setLayout(newLayout);
    // Save layout preference to localStorage
    localStorage.setItem('concept-graph-layout', newLayout);
    if (cyRef.current) {
      cyRef.current.layout({ name: newLayout, padding: 50 } as any).run();
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* Controls */}
      <div className="p-4 bg-slate-100 border-b flex gap-4 items-center">
        <div className="flex gap-2 items-center">
          <span className="text-sm font-medium">Layout:</span>
          <select
            value={layout}
            onChange={(e) => handleLayoutChange(e.target.value)}
            className="px-3 py-1 border rounded text-sm"
          >
            <optgroup label="Hierarchical">
              <option value="breadthfirst">Breadthfirst</option>
              <option value="dagre">Dagre</option>
            </optgroup>
            <optgroup label="Force-Directed">
              <option value="fcose">fCOSE</option>
              <option value="cola">Cola</option>
            </optgroup>
            <optgroup label="Other">
              <option value="circle">Circle</option>
              <option value="concentric">Concentric</option>
              <option value="grid">Grid</option>
            </optgroup>
          </select>
        </div>

        {/* Legend */}
        <div className="ml-auto flex gap-4 items-center text-sm">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-yellow-400 border-2 border-orange-400"></div>
            <span className="text-slate-700">Mastered</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-green-500 border-4 border-green-500 shadow-lg"></div>
            <span className="text-slate-700 font-semibold">Ready to Learn</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-slate-400 opacity-25"></div>
            <span className="text-slate-500">Locked</span>
          </div>
        </div>
      </div>

      {/* Graph container */}
      <div ref={containerRef} className="flex-1 w-full" />
    </div>
  );
}
