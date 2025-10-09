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
interface Chunk {
  chunk_id: string;
  topic: string;
  text: string;
  concepts: string[];
  chunk_type: string;
  section?: string;
}

interface ChunkingResult {
  chunks: Chunk[];
  metadata: {
    total_chunks: number;
    source_file: string;
    chunked_at: string;
  };
}

interface EmbeddedChunk extends Chunk {
  embedding: number[];
  embedding_model: string;
}

interface EmbeddingResult {
  chunks: EmbeddedChunk[];
  metadata: {
    total_embeddings: number;
    source_file: string;
    embedded_at: string;
    embedding_model: string;
    embedding_dimensions: number;
  };
}

// Embed a single chunk
async function embedChunk(
  ai: GoogleGenAI,
  chunk: Chunk,
  modelName: string
): Promise<EmbeddedChunk> {
  // Create rich text for embedding - includes topic and concepts for better semantic matching
  const textToEmbed = `${chunk.topic}\n\n${chunk.text}\n\nConcepts: ${chunk.concepts.join(', ')}`;
  
  const result = await ai.models.embedContent({
    model: modelName,
    contents: [textToEmbed],
  } as any); // Type assertion - SDK types may be incomplete
  
  if (!result.embeddings || !result.embeddings[0] || !result.embeddings[0].values) {
    throw new Error(`Failed to generate embedding for chunk: ${chunk.chunk_id}`);
  }
  
  return {
    ...chunk,
    embedding: result.embeddings[0].values,
    embedding_model: modelName,
  };
}

// Main embedding function
async function embedChunks(inputPath: string, outputPath?: string) {
  console.log('🧠 Embedding Generator\n');
  
  // Read chunks file
  console.log(`📖 Reading ${inputPath}...`);
  
  let chunkData: ChunkingResult;
  try {
    const fileContent = await fs.readFile(inputPath, 'utf-8');
    chunkData = JSON.parse(fileContent);
    console.log(`✅ Loaded ${chunkData.chunks.length} chunks\n`);
  } catch (error) {
    console.error(`❌ Failed to read file: ${error}`);
    process.exit(1);
  }
  
  // Initialize Gemini
  const apiKey = process.env.GOOGLE_API_KEY;
  if (!apiKey) {
    console.error('❌ GOOGLE_API_KEY not found in environment!');
    process.exit(1);
  }
  
  const ai = new GoogleGenAI({ apiKey });
  const modelName = 'gemini-embedding-001'; // Latest Google embedding model
  
  console.log(`🔢 Using model: ${modelName}`);
  console.log(`📊 Processing ${chunkData.chunks.length} chunks...\n`);
  
  // Process chunks with progress tracking
  const embeddedChunks: EmbeddedChunk[] = [];
  const batchSize = 5; // Process in small batches to avoid rate limits
  const totalChunks = chunkData.chunks.length;
  
  for (let i = 0; i < totalChunks; i += batchSize) {
    const batch = chunkData.chunks.slice(i, Math.min(i + batchSize, totalChunks));
    const batchNum = Math.floor(i / batchSize) + 1;
    const totalBatches = Math.ceil(totalChunks / batchSize);
    
    console.log(`   [Batch ${batchNum}/${totalBatches}] Processing chunks ${i + 1}-${Math.min(i + batchSize, totalChunks)}...`);
    
    try {
      // Process batch in parallel
      const batchPromises = batch.map(chunk => embedChunk(ai, chunk, modelName));
      const batchResults = await Promise.all(batchPromises);
      
      embeddedChunks.push(...batchResults);
      console.log(`      ✅ Embedded ${batchResults.length} chunks`);
      
      // Rate limiting - be nice to the API
      if (i + batchSize < totalChunks) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
    } catch (error) {
      console.log(`      ❌ Batch failed: ${error}`);
      console.log(`      Retrying chunks individually...`);
      
      // Fallback: try each chunk individually
      for (const chunk of batch) {
        try {
          const embedded = await embedChunk(ai, chunk, modelName);
          embeddedChunks.push(embedded);
          console.log(`      ✅ Embedded: ${chunk.chunk_id}`);
          await new Promise(resolve => setTimeout(resolve, 500));
        } catch (chunkError) {
          console.log(`      ❌ Failed: ${chunk.chunk_id} - ${chunkError}`);
        }
      }
    }
  }
  
  console.log(`\n✅ Successfully embedded ${embeddedChunks.length}/${totalChunks} chunks\n`);
  
  // Validation
  if (embeddedChunks.length === 0) {
    console.error('❌ No embeddings generated!');
    process.exit(1);
  }
  
  const embeddingDimensions = embeddedChunks[0].embedding.length;
  console.log(`🔍 Embedding dimensions: ${embeddingDimensions}`);
  
  // Verify all embeddings have same dimensions
  const dimensionMismatch = embeddedChunks.filter(c => c.embedding.length !== embeddingDimensions);
  if (dimensionMismatch.length > 0) {
    console.log(`⚠️  Warning: ${dimensionMismatch.length} chunks have mismatched dimensions`);
  }
  
  // Create output
  const output: EmbeddingResult = {
    chunks: embeddedChunks,
    metadata: {
      total_embeddings: embeddedChunks.length,
      source_file: chunkData.metadata.source_file,
      embedded_at: new Date().toISOString(),
      embedding_model: modelName,
      embedding_dimensions: embeddingDimensions,
    },
  };
  
  // Save to file
  const finalOutputPath = outputPath || inputPath.replace(/chunks\.json$/, 'embeddings.json');
  await fs.writeFile(finalOutputPath, JSON.stringify(output, null, 2));
  console.log(`\n💾 Saved embeddings to ${finalOutputPath}`);
  
  // Display sample
  console.log('\n📊 Summary:');
  console.log(`   Total embeddings: ${embeddedChunks.length}`);
  console.log(`   Embedding model: ${modelName}`);
  console.log(`   Dimensions: ${embeddingDimensions}`);
  console.log(`   File size: ${(JSON.stringify(output).length / 1024 / 1024).toFixed(2)} MB`);
  
  // Show a sample embedding
  const sample = embeddedChunks[Math.floor(embeddedChunks.length / 2)];
  console.log(`\n📝 Sample Embedding:`);
  console.log(`   Chunk: ${sample.chunk_id}`);
  console.log(`   Topic: ${sample.topic}`);
  console.log(`   Vector: [${sample.embedding.slice(0, 5).map(v => v.toFixed(4)).join(', ')}...] (${sample.embedding.length}D)`);
  
  console.log('\n✨ Done! Your chunks are now embedded and ready for semantic search.\n');
}

// Parse command line arguments
function parseArgs(): { inputPath: string; outputPath?: string } {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`
Usage: npx ts-node scripts/embed-chunks.ts <chunks.json> [embeddings.json]

Arguments:
  chunks.json        Path to chunks JSON file
  embeddings.json    (optional) Path for output embeddings file
                     Default: <input-dir>/embeddings.json

Examples:
  npx ts-node scripts/embed-chunks.ts paip-chapter-1/chunks.json
  npx ts-node scripts/embed-chunks.ts data/chunks.json output/embeddings.json
`);
    process.exit(0);
  }
  
  return {
    inputPath: args[0],
    outputPath: args[1],
  };
}

// Run it
const { inputPath, outputPath } = parseArgs();
embedChunks(inputPath, outputPath).catch(console.error);
