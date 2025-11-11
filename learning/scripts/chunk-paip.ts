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

// Types for our chunk structure
interface Chunk {
  chunk_id: string;
  topic: string;
  text: string;
  concepts: string[];
  chunk_type: 'definition' | 'example' | 'explanation' | 'exercise' | 'overview';
  section?: string;
  token_estimate?: number;
  // Provenance metadata for linking back to source
  source_file?: string;          // Filename: "tsp.md"
  heading_path?: string[];       // ["The Traveling Salesperson Problem", "Greedy TSP Algorithm"]
  markdown_anchor?: string;      // "greedy-tsp-algorithm-greedy_tsp"
  start_line?: number;           // Line number where chunk starts in source
  end_line?: number;             // Line number where chunk ends
}

interface ChunkingResult {
  chunks: Chunk[];
  metadata: {
    total_chunks: number;
    source_file: string;
    chunked_at: string;
  };
}

// Chunking prompt - now generic for any technical/educational content
function buildChunkingPrompt(markdown: string): string {
  return `You are a content analyzer. Your task is to semantically chunk this document into meaningful, self-contained units.

**CHUNKING RULES:**
1. Each chunk should be a complete, self-contained unit of information
2. Keep related content together: concept definition → explanation → example
3. Ideal chunk size: 300-800 tokens (roughly 1-3 paragraphs)
4. Split at natural boundaries: topic changes, section breaks, before new concepts
5. Code examples should stay with their explanations
6. Don't split mid-concept or mid-example

**CHUNK TYPES:**
- "definition": Formal definition or introduction of a new concept
- "example": Code examples with explanations
- "explanation": Deep dive into how/why something works
- "exercise": Practice problems or challenges
- "overview": Section introductions or summaries

**CONCEPT TAGGING:**
Identify key concepts and tag them with kebab-case IDs (e.g., "functional-programming", "recursion", "data-structures").
Extract concepts directly from the content - be specific and use the terminology from the document.

Here's the markdown to chunk:

---
${markdown}
---

Return a JSON object with this structure:
{
  "chunks": [
    {
      "chunk_id": "unique-kebab-case-id",
      "topic": "Brief topic description",
      "text": "The actual chunk text (preserve markdown formatting)",
      "concepts": ["concept-id-1", "concept-id-2"],
      "chunk_type": "definition" | "example" | "explanation" | "exercise" | "overview",
      "section": "1.1" (if identifiable from headers)
    }
  ]
}

IMPORTANT: 
- Return ONLY valid JSON, no markdown code fences
- Include ALL the text, don't summarize or skip content
- Preserve code blocks exactly as they appear
`;
}

// Basic validation
function validateChunks(chunks: Chunk[]): string[] {
  const issues: string[] = [];
  
  if (chunks.length === 0) {
    issues.push("❌ No chunks generated!");
    return issues;
  }
  
  // Check for suspiciously short chunks
  const tooShort = chunks.filter(c => c.text.length < 50);
  if (tooShort.length > 0) {
    issues.push(`⚠️  ${tooShort.length} chunks are very short (<50 chars)`);
  }
  
  // Check for very long chunks
  const tooLong = chunks.filter(c => c.text.length > 3000);
  if (tooLong.length > 0) {
    issues.push(`⚠️  ${tooLong.length} chunks are very long (>3000 chars)`);
  }
  
  // Check for missing concepts
  const missingConcepts = chunks.filter(c => !c.concepts || c.concepts.length === 0);
  if (missingConcepts.length > 0) {
    issues.push(`⚠️  ${missingConcepts.length} chunks have no concept tags`);
  }
  
  // Check for duplicate IDs
  const ids = chunks.map(c => c.chunk_id);
  const duplicates = ids.filter((id, i) => ids.indexOf(id) !== i);
  if (duplicates.length > 0) {
    issues.push(`❌ Duplicate chunk IDs found: ${[...new Set(duplicates)].join(', ')}`);
  }
  
  return issues;
}

// Display sample chunks
function displaySamples(chunks: Chunk[]) {
  console.log('\n📝 SPOT CHECK - Random Samples:\n');
  
  const samples = [
    chunks[0], // First
    chunks[Math.floor(chunks.length / 2)], // Middle
    chunks[chunks.length - 1], // Last
    ...getRandomSamples(chunks, 2) // 2 random
  ];
  
  samples.forEach((chunk, i) => {
    console.log(`${'='.repeat(80)}`);
    console.log(`Sample ${i + 1}/${samples.length}`);
    console.log(`ID: ${chunk.chunk_id}`);
    console.log(`Topic: ${chunk.topic}`);
    console.log(`Type: ${chunk.chunk_type}`);
    console.log(`Concepts: ${chunk.concepts.join(', ')}`);
    console.log(`Length: ${chunk.text.length} chars`);
    
    // Show provenance information
    if (chunk.source_file) {
      console.log(`Source: ${chunk.source_file}`);
    }
    if (chunk.heading_path && chunk.heading_path.length > 0) {
      console.log(`Location: ${chunk.heading_path.join(' > ')}`);
    }
    if (chunk.markdown_anchor) {
      console.log(`Anchor: #${chunk.markdown_anchor}`);
    }
    if (chunk.start_line !== undefined) {
      console.log(`Lines: ${chunk.start_line}-${chunk.end_line}`);
    }
    
    console.log(`Preview:\n${chunk.text.substring(0, 200)}...`);
    console.log();
  });
}

function getRandomSamples<T>(arr: T[], count: number): T[] {
  const result: T[] = [];
  const used = new Set<number>();
  
  while (result.length < count && result.length < arr.length - 3) {
    const idx = Math.floor(Math.random() * arr.length);
    if (!used.has(idx) && idx !== 0 && idx !== Math.floor(arr.length / 2) && idx !== arr.length - 1) {
      used.add(idx);
      result.push(arr[idx]);
    }
  }
  
  return result;
}

// Generate GitHub-style markdown anchors
function generateAnchor(headingText: string): string {
  return headingText
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')  // Remove special chars except spaces and hyphens
    .trim()
    .replace(/\s+/g, '-');      // Replace spaces with hyphens
}

// Extract heading level and text from a markdown heading line
function parseHeading(line: string): { level: number; text: string } | null {
  const match = line.match(/^(#{1,6})\s+(.+)$/);
  if (!match) return null;
  return {
    level: match[1].length,
    text: match[2].trim(),
  };
}

// Enhanced section structure with provenance metadata
interface Section {
  header: string;
  content: string;
  headingPath: string[];      // Hierarchical path of headers
  anchor: string;              // Markdown anchor for this section
  startLine: number;           // Starting line number
  endLine: number;             // Ending line number
}

// Split document into sections by headers
function splitIntoSections(markdown: string, sourceFile: string): Section[] {
  const sections: Section[] = [];
  const lines = markdown.split('\n');
  
  let currentHeader = 'Introduction';
  let currentContent: string[] = [];
  let headingStack: Array<{ level: number; text: string }> = [];
  let sectionStartLine = 0;
  
  for (let lineNum = 0; lineNum < lines.length; lineNum++) {
    const line = lines[lineNum];
    const heading = parseHeading(line);
    
    if (heading && heading.level === 1) {  // Main section header
      // Save previous section if it has content
      if (currentContent.length > 0) {
        sections.push({
          header: currentHeader,
          content: currentContent.join('\n').trim(),
          headingPath: headingStack.map(h => h.text),
          anchor: generateAnchor(currentHeader),
          startLine: sectionStartLine,
          endLine: lineNum - 1,
        });
      }
      
      // Start new section
      currentHeader = heading.text;
      headingStack = [{ level: heading.level, text: heading.text }];
      currentContent = [line]; // Include the header in content
      sectionStartLine = lineNum;
    } else {
      // Update heading stack for sub-headers
      if (heading) {
        // Pop any headers at the same or deeper level
        while (headingStack.length > 0 && headingStack[headingStack.length - 1].level >= heading.level) {
          headingStack.pop();
        }
        headingStack.push({ level: heading.level, text: heading.text });
      }
      
      currentContent.push(line);
    }
  }
  
  // Add final section
  if (currentContent.length > 0) {
    sections.push({
      header: currentHeader,
      content: currentContent.join('\n').trim(),
      headingPath: headingStack.map(h => h.text),
      anchor: generateAnchor(currentHeader),
      startLine: sectionStartLine,
      endLine: lines.length - 1,
    });
  }
  
  return sections;
}

// Main chunking function
async function chunkDocument(inputPath: string, outputPath?: string) {
  console.log('🤖 Semantic Chunker (Incremental Mode)\n');
  
  // Read markdown file
  console.log(`📖 Reading ${inputPath}...`);
  
  let markdown: string;
  try {
    markdown = await fs.readFile(inputPath, 'utf-8');
    console.log(`✅ Loaded ${markdown.length} characters\n`);
  } catch (error) {
    console.error(`❌ Failed to read file: ${error}`);
    process.exit(1);
  }
  
  // Split into sections with provenance metadata
  const sourceFileName = path.basename(inputPath);
  const sections = splitIntoSections(markdown, sourceFileName);
  console.log(`📑 Split into ${sections.length} sections\n`);
  
  sections.forEach((s, i) => {
    console.log(`   ${i + 1}. ${s.header} (${s.content.length} chars)`);
  });
  console.log();
  
  // Initialize Gemini
  const apiKey = process.env.GOOGLE_API_KEY;
  if (!apiKey) {
    console.error('❌ GOOGLE_API_KEY not found in environment!');
    process.exit(1);
  }
  
  const ai = new GoogleGenAI({ apiKey });
  
  // Process each section
  console.log('🧠 Chunking each section...\n');
  
  const allChunks: Chunk[] = [];
  let chunkIdCounter = 1;
  
  for (let i = 0; i < sections.length; i++) {
    const section = sections[i];
    console.log(`   [${i + 1}/${sections.length}] Processing: ${section.header}...`);
    
    try {
      const response = await ai.models.generateContent({
        model: 'gemini-2.0-flash-exp',
        contents: buildChunkingPrompt(section.content),
        config: {
          responseMimeType: 'application/json',
          temperature: 0.3,
        },
      });
      
      const resultText = response.text;
      if (!resultText) {
        console.log(`      ⚠️  No response - skipping section`);
        continue;
      }
      
      const result: { chunks: Chunk[] } = JSON.parse(resultText);
      
      // Add provenance metadata and ensure unique IDs
      result.chunks.forEach(chunk => {
        chunk.chunk_id = `chunk-${chunkIdCounter++}-${chunk.chunk_id}`;
        chunk.source_file = sourceFileName;
        chunk.heading_path = section.headingPath;
        chunk.markdown_anchor = section.anchor;
        chunk.start_line = section.startLine;
        chunk.end_line = section.endLine;
      });
      
      allChunks.push(...result.chunks);
      console.log(`      ✅ Generated ${result.chunks.length} chunks`);
      
      // Rate limiting - be nice to the API
      if (i < sections.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
    } catch (error) {
      console.log(`      ❌ Failed: ${error}`);
      console.log(`      Skipping this section...`);
    }
  }
  
  console.log(`\n✅ Total chunks generated: ${allChunks.length}\n`);
  
  // Validate
  console.log('🔍 Validating chunks...');
  const issues = validateChunks(allChunks);
    
    if (issues.length > 0) {
      console.log('\n⚠️  Validation Issues:');
      issues.forEach(issue => console.log(`   ${issue}`));
      console.log();
    } else {
      console.log('✅ All validation checks passed!\n');
    }
    
  // Display samples
  displaySamples(allChunks);
  
  // Add metadata
  const output: ChunkingResult = {
    chunks: allChunks,
    metadata: {
      total_chunks: allChunks.length,
      source_file: path.basename(inputPath),
      chunked_at: new Date().toISOString(),
    },
  };
  
  // Determine output path
  const finalOutputPath = outputPath || inputPath.replace(/\.md$/, '-chunks.json');
  await fs.writeFile(finalOutputPath, JSON.stringify(output, null, 2));
  console.log(`\n💾 Saved chunks to ${finalOutputPath}`);
  
  // Summary stats
  console.log('\n📊 Summary:');
  console.log(`   Total chunks: ${allChunks.length}`);
  console.log(`   Avg length: ${Math.round(allChunks.reduce((sum, c) => sum + c.text.length, 0) / allChunks.length)} chars`);
  console.log(`   Chunk types: ${[...new Set(allChunks.map(c => c.chunk_type))].join(', ')}`);
  console.log(`   Concepts tagged: ${[...new Set(allChunks.flatMap(c => c.concepts))].length} unique`);
  
  console.log('\n✨ Done! Review the samples above. If they look good, proceed to embedding.\n');
}

// Parse command line arguments
function parseArgs(): { inputPath: string; outputPath?: string } {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`
Usage: npx ts-node scripts/chunk-paip.ts <input.md> [output.json]

Arguments:
  input.md   Path to markdown file to chunk
  output.json (optional) Path for output JSON file
              Default: <input>-chunks.json

Examples:
  npx ts-node scripts/chunk-paip.ts paip-chapter-1/text.md
  npx ts-node scripts/chunk-paip.ts docs/tutorial.md output/chunks.json
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
chunkDocument(inputPath, outputPath).catch(console.error);
