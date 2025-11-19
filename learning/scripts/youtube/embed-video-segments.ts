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

import { GoogleGenAI } from "@google/genai";
import fs from 'fs/promises';
import path from 'path';

// Types
interface VideoSegment {
  segment_index: number;
  timestamp: number;
  audio_text: string;
  audio_start: number;
  audio_end: number;
  frame_path: string;
  analysis?: {
    visual_description?: string;
    code_content?: string;
    slide_content?: string;
    visual_audio_alignment?: string;
    key_concepts?: string[];
  };
  concept_mapping?: {
    concept_id: string;
    confidence: number;
    reasoning?: string;
  };
}

interface SegmentMappingsData {
  video_id: string;
  video_title?: string;
  total_segments: number;
  mapped_segments: number;
  segments: VideoSegment[];
  metadata?: any;
}

interface EmbeddedVideoSegment extends VideoSegment {
  video_id: string;
  embedding: number[];
  embedding_model: string;
  embedding_text: string; // What was actually embedded (for debugging)
}

interface EmbeddingResult {
  video_id: string;
  video_title?: string;
  segments: EmbeddedVideoSegment[];
  metadata: {
    total_embeddings: number;
    embedded_at: string;
    embedding_model: string;
    embedding_dimensions: number;
    source_file: string;
  };
}

// Create rich text for embedding from all available content
function createEmbeddingText(segment: VideoSegment, conceptName?: string): string {
  const parts: string[] = [];
  
  // Add audio transcript
  if (segment.audio_text && segment.audio_text.trim()) {
    parts.push(`Transcript: ${segment.audio_text}`);
  }
  
  // Add visual description
  if (segment.analysis?.visual_description) {
    parts.push(`Visual: ${segment.analysis.visual_description}`);
  }
  
  // Add code content (high value for technical videos)
  if (segment.analysis?.code_content && segment.analysis.code_content.trim()) {
    parts.push(`Code: ${segment.analysis.code_content}`);
  }
  
  // Add slide content
  if (segment.analysis?.slide_content && segment.analysis.slide_content.trim()) {
    parts.push(`Slides: ${segment.analysis.slide_content}`);
  }
  
  // Add key concepts
  if (segment.analysis?.key_concepts && segment.analysis.key_concepts.length > 0) {
    parts.push(`Key Concepts: ${segment.analysis.key_concepts.join(', ')}`);
  }
  
  // Add mapped concept name (helps with semantic search)
  if (conceptName) {
    parts.push(`Teaching: ${conceptName}`);
  }
  
  return parts.join('\n\n');
}

// Embed a single video segment
async function embedSegment(
  ai: GoogleGenAI,
  segment: VideoSegment,
  videoId: string,
  modelName: string,
  conceptName?: string
): Promise<EmbeddedVideoSegment> {
  const embeddingText = createEmbeddingText(segment, conceptName);
  
  if (!embeddingText.trim()) {
    throw new Error(`Segment ${segment.segment_index} has no content to embed`);
  }
  
  const result = await ai.models.embedContent({
    model: modelName,
    contents: [embeddingText],
  } as any);
  
  if (!result.embeddings || !result.embeddings[0] || !result.embeddings[0].values) {
    throw new Error(`Failed to generate embedding for segment: ${segment.segment_index}`);
  }
  
  return {
    ...segment,
    video_id: videoId,
    embedding: result.embeddings[0].values,
    embedding_model: modelName,
    embedding_text: embeddingText,
  };
}

// Load concept graph to get human-readable concept names
async function loadConceptNames(videoId: string): Promise<Map<string, string>> {
  const conceptGraphPath = path.join(
    process.cwd(),
    `youtube/${videoId}/concept-graph.json`
  );
  
  try {
    const data = JSON.parse(await fs.readFile(conceptGraphPath, 'utf-8'));
    const conceptMap = new Map<string, string>();
    
    for (const concept of data.concepts || []) {
      conceptMap.set(concept.id, concept.name);
    }
    
    return conceptMap;
  } catch (error) {
    console.log(`⚠️  Could not load concept names: ${error}`);
    return new Map();
  }
}

// Main embedding function
async function embedVideoSegments(videoId: string, outputPath?: string) {
  console.log('🎬 Video Segment Embedding Generator\n');
  
  // Construct input path from video ID
  const inputPath = path.join(process.cwd(), `youtube/${videoId}/segment-concept-mappings.json`);
  
  // Read segment mappings file
  console.log(`📖 Reading ${inputPath}...`);
  
  let segmentData: SegmentMappingsData;
  try {
    const fileContent = await fs.readFile(inputPath, 'utf-8');
    segmentData = JSON.parse(fileContent);
    console.log(`✅ Loaded ${segmentData.segments.length} segments`);
    console.log(`   Video ID: ${segmentData.video_id}`);
    console.log(`   Title: ${segmentData.video_title || 'N/A'}\n`);
  } catch (error) {
    console.error(`❌ Failed to read file: ${error}`);
    process.exit(1);
  }
  
  // Load concept names for richer embeddings
  console.log('📚 Loading concept names...');
  const conceptNames = await loadConceptNames(segmentData.video_id);
  console.log(`   Found ${conceptNames.size} concept names\n`);
  
  // Initialize Gemini
  const apiKey = process.env.GOOGLE_API_KEY;
  if (!apiKey) {
    console.error('❌ GOOGLE_API_KEY not found in environment!');
    process.exit(1);
  }
  
  const ai = new GoogleGenAI({ apiKey });
  const modelName = 'gemini-embedding-001';
  
  console.log(`🔢 Using model: ${modelName}`);
  console.log(`📊 Processing ${segmentData.segments.length} segments...\n`);
  
  // Process segments with progress tracking
  const embeddedSegments: EmbeddedVideoSegment[] = [];
  const batchSize = 10; // Video segments can be larger, so smaller batches
  const totalSegments = segmentData.segments.length;
  
  for (let i = 0; i < totalSegments; i += batchSize) {
    const batch = segmentData.segments.slice(i, Math.min(i + batchSize, totalSegments));
    const batchNum = Math.floor(i / batchSize) + 1;
    const totalBatches = Math.ceil(totalSegments / batchSize);
    
    console.log(`   [Batch ${batchNum}/${totalBatches}] Processing segments ${i + 1}-${Math.min(i + batchSize, totalSegments)}...`);
    
    try {
      // Process batch in parallel
      const batchPromises = batch.map(segment => {
        const conceptName = segment.concept_mapping?.concept_id
          ? conceptNames.get(segment.concept_mapping.concept_id)
          : undefined;
        return embedSegment(ai, segment, segmentData.video_id, modelName, conceptName);
      });
      const batchResults = await Promise.all(batchPromises);
      
      embeddedSegments.push(...batchResults);
      console.log(`      ✅ Embedded ${batchResults.length} segments`);
      
      // Rate limiting - be nice to the API
      if (i + batchSize < totalSegments) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
    } catch (error) {
      console.log(`      ❌ Batch failed: ${error}`);
      console.log(`      Retrying segments individually...`);
      
      // Fallback: try each segment individually
      for (const segment of batch) {
        try {
          const conceptName = segment.concept_mapping?.concept_id
            ? conceptNames.get(segment.concept_mapping.concept_id)
            : undefined;
          const embedded = await embedSegment(ai, segment, segmentData.video_id, modelName, conceptName);
          embeddedSegments.push(embedded);
          console.log(`      ✅ Embedded segment ${segment.segment_index}`);
          await new Promise(resolve => setTimeout(resolve, 500));
        } catch (segmentError) {
          console.log(`      ❌ Failed segment ${segment.segment_index}: ${segmentError}`);
        }
      }
    }
  }
  
  console.log(`\n✅ Successfully embedded ${embeddedSegments.length}/${totalSegments} segments\n`);
  
  // Validation
  if (embeddedSegments.length === 0) {
    console.error('❌ No embeddings generated!');
    process.exit(1);
  }
  
  const embeddingDimensions = embeddedSegments[0].embedding.length;
  console.log(`🔍 Embedding dimensions: ${embeddingDimensions}`);
  
  // Verify all embeddings have same dimensions
  const dimensionMismatch = embeddedSegments.filter(s => s.embedding.length !== embeddingDimensions);
  if (dimensionMismatch.length > 0) {
    console.log(`⚠️  Warning: ${dimensionMismatch.length} segments have mismatched dimensions`);
  }
  
  // Create output
  const output: EmbeddingResult = {
    video_id: segmentData.video_id,
    video_title: segmentData.video_title,
    segments: embeddedSegments,
    metadata: {
      total_embeddings: embeddedSegments.length,
      embedded_at: new Date().toISOString(),
      embedding_model: modelName,
      embedding_dimensions: embeddingDimensions,
      source_file: inputPath,
    },
  };
  
  // Save to file
  const finalOutputPath = outputPath || path.join(process.cwd(), `youtube/${videoId}/segment-embeddings.json`);
  await fs.writeFile(finalOutputPath, JSON.stringify(output, null, 2));
  console.log(`\n💾 Saved embeddings to ${finalOutputPath}`);
  
  // Display sample
  console.log('\n📊 Summary:');
  console.log(`   Video ID: ${segmentData.video_id}`);
  console.log(`   Total embeddings: ${embeddedSegments.length}`);
  console.log(`   Embedding model: ${modelName}`);
  console.log(`   Dimensions: ${embeddingDimensions}`);
  console.log(`   File size: ${(JSON.stringify(output).length / 1024 / 1024).toFixed(2)} MB`);
  
  // Show a sample embedding with YouTube link
  const sample = embeddedSegments[Math.floor(embeddedSegments.length / 2)];
  console.log(`\n📝 Sample Embedding:`);
  console.log(`   Segment: ${sample.segment_index}`);
  console.log(`   Video ID: ${sample.video_id}`);
  console.log(`   Timestamp: ${sample.timestamp.toFixed(2)}s`);
  console.log(`   Concept: ${sample.concept_mapping?.concept_id || 'N/A'}`);
  console.log(`   Audio: "${sample.audio_text.substring(0, 60)}..."`);
  console.log(`   Vector: [${sample.embedding.slice(0, 5).map(v => v.toFixed(4)).join(', ')}...] (${sample.embedding.length}D)`);
  
  // Stats by concept
  const conceptCounts = new Map<string, number>();
  for (const seg of embeddedSegments) {
    if (seg.concept_mapping?.concept_id) {
      const count = conceptCounts.get(seg.concept_mapping.concept_id) || 0;
      conceptCounts.set(seg.concept_mapping.concept_id, count + 1);
    }
  }
  
  console.log(`\n📈 Embeddings by Concept (Top 10):`);
  const sortedConcepts = Array.from(conceptCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);
  
  for (const [conceptId, count] of sortedConcepts) {
    const name = conceptNames.get(conceptId) || conceptId;
    console.log(`   ${name}: ${count} segments`);
  }
  
  console.log('\n✨ Done! Video segments are now embedded with full YouTube provenance.\n');
  console.log('💡 Use video_id + timestamp to render embedded players or deep links in your UI.\n');
}

// Parse command line arguments
function parseArgs(): { videoId: string; outputPath?: string } {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`
Usage: npx tsx scripts/youtube/embed-video-segments.ts <video-id> [output.json]

Arguments:
  video-id                 YouTube video ID (e.g., kCc8FmEb1nY)
  output.json              (optional) Path for output embeddings file
                           Default: youtube/<video-id>/segment-embeddings.json

Examples:
  npx tsx scripts/youtube/embed-video-segments.ts kCc8FmEb1nY
  npx tsx scripts/youtube/embed-video-segments.ts kCc8FmEb1nY custom-output.json

Features:
  ✓ Preserves full YouTube video provenance (video_id, timestamp, frame_path)
  ✓ Stores primitives (video_id, timestamp) for flexible UI rendering
  ✓ Creates rich embeddings from audio + visuals + code + slides + concepts
  ✓ Enables semantic search with results that can jump to video moments
`);
    process.exit(0);
  }
  
  return {
    videoId: args[0],
    outputPath: args[1],
  };
}

// Run it
const { videoId, outputPath } = parseArgs();
embedVideoSegments(videoId, outputPath).catch(console.error);
