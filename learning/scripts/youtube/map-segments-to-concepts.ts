import fs from 'fs';
import path from 'path';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { z } from 'zod';
import { zodToGeminiSchema } from '../../lib/gemini-utils.js';
import {
  conceptMappingSchema,
  videoAnalysisSchema,
  conceptGraphSchema,
  type ConceptMapping,
  type VideoSegment,
  type MappedSegment,
  type ConceptGraph,
  type VideoAnalysis,
} from './types.js';

// Batch mapping schema for processing multiple segments at once
const batchMappingSchema = z.object({
  mappings: z.array(z.object({
    segment_index: z.number(),
    concept_id: z.string(),
    confidence: z.number().min(0).max(1),
    secondary_concepts: z.array(z.string()).optional(),
    reasoning: z.string().optional()
  }))
});

function loadVideoAnalysis(videoId: string): VideoAnalysis {
  const analysisPath = path.join(
    process.cwd(),
    `youtube/${videoId}/video-analysis.json`
  );
  const raw = JSON.parse(fs.readFileSync(analysisPath, 'utf-8'));
  return videoAnalysisSchema.parse(raw);
}

function loadConceptGraph(videoId: string): ConceptGraph {
  const conceptPath = path.join(
    process.cwd(),
    `youtube/${videoId}/concept-graph-enriched.json`
  );
  const raw = JSON.parse(fs.readFileSync(conceptPath, 'utf-8'));
  return conceptGraphSchema.parse(raw);
}

function buildConceptList(conceptGraph: ConceptGraph): string {
  return conceptGraph.nodes
    .map(c => `- ${c.id}: ${c.name} - ${c.description}`)
    .join('\n');
}

function buildBatchMappingPrompt(segments: VideoSegment[], conceptList: string): string {
  const segmentDescriptions = segments.map(seg => {
    const hasCode = seg.analysis.code_content && seg.analysis.code_content.trim().length > 0;
    return `
Segment ${seg.segment_index} at ${formatTime(seg.timestamp)}:
Audio: "${seg.audio_text}"
${hasCode ? `Code: ${seg.analysis.code_content?.substring(0, 200)}...` : ''}
`.trim();
  }).join('\n\n');

  return `
You are analyzing segments from an educational coding video and mapping each to its primary concept.

**Available concepts:**
${conceptList}

**Task:** Map each segment below to its primary concept.

Guidelines:
- Choose the MOST specific concept for each segment
- If transitional (e.g., "so let's..."), use the concept being transitioned TO
- If too generic (e.g., just "hello"), set confidence below 0.3
- Consider both audio and any code shown

**Segments to map (${segments.length} total):**
${segmentDescriptions}

Return a JSON object with a "mappings" array containing mappings for ALL ${segments.length} segments in order.
Each mapping must include: segment_index, concept_id, confidence, and optionally secondary_concepts and reasoning.
`.trim();
}

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
  return `${m}:${s.toString().padStart(2, '0')}`;
}

async function mapSegmentBatch(
  segments: VideoSegment[],
  conceptList: string,
  genAI: GoogleGenerativeAI
): Promise<Map<number, ConceptMapping>> {
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.5-flash',
    generationConfig: {
      responseMimeType: 'application/json',
      responseSchema: zodToGeminiSchema(batchMappingSchema),
    }
  });

  const prompt = buildBatchMappingPrompt(segments, conceptList);
  
  try {
    const result = await model.generateContent(prompt);
    const response = result.response;
    const text = response.text();
    const parsed = JSON.parse(text);
    
    // Convert to map for easy lookup
    const mappings = new Map<number, ConceptMapping>();
    for (const mapping of parsed.mappings) {
      mappings.set(mapping.segment_index, {
        concept_id: mapping.concept_id,
        confidence: mapping.confidence,
        secondary_concepts: mapping.secondary_concepts,
        reasoning: mapping.reasoning
      });
    }
    
    return mappings;
  } catch (error) {
    console.error(`   ❌ Error mapping batch:`, error);
    // Return empty mappings for failed batch
    return new Map();
  }
}

function backfillUnmappedSegments(segments: MappedSegment[]): MappedSegment[] {
  console.log('\n📋 Backfilling unmapped segments...');
  
  let backfilled = 0;
  
  for (let i = 0; i < segments.length; i++) {
    const seg = segments[i];
    const mapping = seg.concept_mapping;
    
    // If unmapped or low confidence
    if (!mapping || mapping.concept_id === 'unmapped' || mapping.confidence < 0.3) {
      const prev = segments[i-1]?.concept_mapping;
      const next = segments[i+1]?.concept_mapping;
      
      // If surrounded by same concept, inherit it
      if (prev && next && 
          prev.concept_id === next.concept_id &&
          prev.concept_id !== 'unmapped' &&
          prev.confidence >= 0.5 && next.confidence >= 0.5) {
        
        seg.concept_mapping = {
          concept_id: prev.concept_id,
          confidence: 0.6,
          reasoning: `Inferred from surrounding context (prev=${prev.concept_id}, next=${next.concept_id})`
        };
        backfilled++;
        console.log(`   ✓ Segment ${seg.segment_index}: inferred as ${prev.concept_id}`);
      }
      // If only one neighbor with high confidence, inherit from it
      else if (prev && prev.concept_id !== 'unmapped' && prev.confidence >= 0.6) {
        seg.concept_mapping = {
          concept_id: prev.concept_id,
          confidence: 0.5,
          reasoning: `Inferred from previous segment (${prev.concept_id})`
        };
        backfilled++;
        console.log(`   ✓ Segment ${seg.segment_index}: inferred as ${prev.concept_id} (from prev)`);
      }
      else if (next && next.concept_id !== 'unmapped' && next.confidence >= 0.6) {
        seg.concept_mapping = {
          concept_id: next.concept_id,
          confidence: 0.5,
          reasoning: `Inferred from next segment (${next.concept_id})`
        };
        backfilled++;
        console.log(`   ✓ Segment ${seg.segment_index}: inferred as ${next.concept_id} (from next)`);
      }
    }
  }
  
  console.log(`   📊 Backfilled ${backfilled} segments`);
  return segments;
}

function printMappingStats(segments: MappedSegment[], conceptGraph: ConceptGraph) {
  console.log('\n📊 Mapping Statistics:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  const conceptCounts = new Map<string, number>();
  let unmapped = 0;
  let lowConfidence = 0;
  
  for (const seg of segments) {
    const mapping = seg.concept_mapping;
    if (!mapping || mapping.concept_id === 'unmapped') {
      unmapped++;
    } else {
      conceptCounts.set(
        mapping.concept_id,
        (conceptCounts.get(mapping.concept_id) || 0) + 1
      );
      if (mapping.confidence < 0.5) {
        lowConfidence++;
      }
    }
  }
  
  console.log(`Total segments: ${segments.length}`);
  console.log(`Unmapped: ${unmapped}`);
  console.log(`Low confidence (<0.5): ${lowConfidence}`);
  console.log(`\nSegments per concept:`);
  
  const sorted = Array.from(conceptCounts.entries())
    .sort((a, b) => b[1] - a[1]);
  
  for (const [conceptId, count] of sorted) {
    const concept = conceptGraph.nodes.find(c => c.id === conceptId);
    const name = concept ? concept.name : conceptId;
    console.log(`  ${name}: ${count} segments`);
  }
}

async function mapSegmentsToConcepts(videoId: string): Promise<void> {
  console.log('\n🎯 Mapping Video Segments to Concepts');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`📹 Video ID: ${videoId}\n`);
  
  // 1. Load data
  console.log('📂 Loading data files...');
  const videoAnalysis = loadVideoAnalysis(videoId);
  const conceptGraph = loadConceptGraph(videoId);
  
  console.log(`   ✓ Loaded ${videoAnalysis.results.length} segments`);
  console.log(`   ✓ Loaded ${conceptGraph.nodes.length} concepts\n`);
  
  // 2. Build concept list for prompt
  const conceptList = buildConceptList(conceptGraph);
  
  // 3. Initialize Gemini
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error('GEMINI_API_KEY environment variable not set');
  }
  const genAI = new GoogleGenerativeAI(apiKey);
  
  // 4. Map segments in batches
  const BATCH_SIZE = 100; // Map 100 segments per API call
  console.log(`🔄 Mapping segments to concepts in batches of ${BATCH_SIZE}...`);
  
  const mappedSegments: MappedSegment[] = [];
  const batches: VideoSegment[][] = [];
  
  // Create batches
  for (let i = 0; i < videoAnalysis.results.length; i += BATCH_SIZE) {
    batches.push(videoAnalysis.results.slice(i, i + BATCH_SIZE));
  }
  
  console.log(`   Total batches: ${batches.length}\n`);
  
  for (let batchIdx = 0; batchIdx < batches.length; batchIdx++) {
    const batch = batches[batchIdx];
    const batchStart = batchIdx * BATCH_SIZE;
    
    console.log(`📦 Batch ${batchIdx + 1}/${batches.length}: segments ${batchStart}-${batchStart + batch.length - 1}`);
    
    const startTime = Date.now();
    const mappings = await mapSegmentBatch(batch, conceptList, genAI);
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    
    console.log(`   ✓ Mapped ${mappings.size}/${batch.length} segments in ${elapsed}s`);
    
    // Merge mappings with segments
    for (const segment of batch) {
      const mapping = mappings.get(segment.segment_index) || {
        concept_id: 'unmapped',
        confidence: 0,
        reasoning: 'Failed to map in batch'
      };
      
      mappedSegments.push({
        ...segment,
        concept_mapping: mapping
      });
    }
    
    // Small delay between batches to avoid rate limiting
    if (batchIdx < batches.length - 1) {
      console.log(`   ⏸️  Pausing 1s before next batch...\n`);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  
  console.log(`\n   ✓ Mapped all ${mappedSegments.length} segments\n`);
  
  // 5. Backfill unmapped segments
  const backfilled = backfillUnmappedSegments(mappedSegments);
  
  // 6. Print stats
  printMappingStats(backfilled, conceptGraph);
  
  // 7. Save results
  const outputPath = path.join(
    process.cwd(),
    `youtube/${videoId}/segment-concept-mappings.json`
  );
  
  const output = {
    video_id: videoId,
    total_segments: backfilled.length,
    mapped_at: new Date().toISOString(),
    segments: backfilled
  };
  
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
  
  console.log(`\n✅ Saved mappings to: youtube/${videoId}/segment-concept-mappings.json`);
  console.log('\n🎉 Segment-to-concept mapping complete!');
}

// CLI
const videoId = process.argv[2];

if (!videoId) {
  console.error('Usage: npx tsx map-segments-to-concepts.ts <video-id>');
  console.error('Example: npx tsx map-segments-to-concepts.ts kCc8FmEb1nY');
  process.exit(1);
}

mapSegmentsToConcepts(videoId).catch(error => {
  console.error('Error:', error);
  process.exit(1);
});
