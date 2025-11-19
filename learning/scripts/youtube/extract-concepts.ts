import { GoogleGenAI } from "@google/genai";
import * as fs from "fs";
import * as path from "path";
import { zodToGeminiSchema } from "../../lib/gemini-utils.js";
import {
  audioTranscriptSchema,
  conceptGraphSchema,
  type AudioTranscript,
  type ConceptGraph,
} from "./types.js";

// ============================================================================
// Prompt Construction
// ============================================================================

function buildPrompt(transcript: string, videoDuration: number, videoId: string): string {
  return `You are an expert at analyzing educational programming tutorials and extracting pedagogical concept graphs.

Analyze this 3-hour programming tutorial transcript and extract 20-30 salient PEDAGOGICAL concepts that are taught in depth.

IMPORTANT DISTINCTIONS:
- ✅ Extract concepts that are TAUGHT DEEPLY (explained, demonstrated, implemented)
- ❌ Ignore tools that are merely MENTIONED IN PASSING (VS Code, terminal commands, etc.)
- ✅ "Attention Mechanism" - taught over 30 minutes with theory + implementation
- ❌ "Git" - mentioned once as a tool used incidentally

For each concept:
1. **Precise pedagogical description** - What is being taught, not just named
2. **Prerequisites** - Based on teaching order and logical dependencies
3. **Difficulty level** - basic/intermediate/advanced based on prerequisites

Guidelines:
- Focus on WHAT IS TAUGHT, not what is used as a tool
- Distinguish between "core concepts" and "implementation details"
- Look for concepts that span multiple segments (theory → implementation → examples)
- Use snake_case for IDs (e.g., "attention_mechanism")

Video Details:
- Duration: ${Math.floor(videoDuration)} seconds (${Math.floor(videoDuration / 60)} minutes)
- Video ID: ${videoId}
- Title: "Let's build GPT: from scratch, in code, spelled out"
- Author: "Andrej Karpathy"

TRANSCRIPT:
${transcript}

Return a complete concept graph with metadata and 20-30 pedagogical concepts.`;
}

// ============================================================================
// Main Extraction Logic
// ============================================================================

async function extractConcepts(videoId: string): Promise<void> {
  console.log(`\n🎓 CONCEPT EXTRACTION`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
  console.log(`📹 Video ID: ${videoId}\n`);

  // Paths
  const videoDir = path.join(process.cwd(), "youtube", videoId);
  const transcriptPath = path.join(videoDir, "audio-transcript.json");
  const outputPath = path.join(videoDir, "concept-graph.json");

  // Check if transcript exists
  if (!fs.existsSync(transcriptPath)) {
    throw new Error(`❌ Transcript not found: ${transcriptPath}`);
  }

  console.log(`📖 Reading transcript...`);
  const raw = JSON.parse(fs.readFileSync(transcriptPath, "utf-8"));
  const transcriptData = audioTranscriptSchema.parse(raw);

  console.log(`   Duration: ${Math.floor(transcriptData.total_duration / 60)} minutes`);
  console.log(`   Segments: ${transcriptData.segments.length}`);
  console.log(`   Transcript length: ${transcriptData.full_transcript.length} characters\n`);

  // Initialize Gemini
  console.log(`🤖 Initializing Gemini 2.5 Flash...`);
  const ai = new GoogleGenAI({});

  // Build prompt
  console.log(`📝 Building prompt...\n`);
  const prompt = buildPrompt(
    transcriptData.full_transcript,
    transcriptData.total_duration,
    videoId
  );

  // Call Gemini
  console.log(`🔮 Calling Gemini for concept extraction...`);
  console.log(`   (This may take 30-60 seconds for a long transcript)\n`);

  const startTime = Date.now();

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: prompt,
    config: {
      responseMimeType: "application/json",
      responseJsonSchema: zodToGeminiSchema(conceptGraphSchema),
    },
  });

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`✅ Received response in ${elapsed}s\n`);

  // Parse response
  if (!response.text) {
    throw new Error("No response text received from Gemini");
  }

  // Save raw response for debugging
  const rawResponsePath = path.join(videoDir, "concept-graph-raw.json");
  console.log(`💾 Saving raw response to: ${rawResponsePath}`);
  fs.writeFileSync(rawResponsePath, response.text);
  console.log(`   Response length: ${response.text.length} characters\n`);

  let conceptGraph: ConceptGraph;
  try {
    conceptGraph = conceptGraphSchema.parse(JSON.parse(response.text));
  } catch (error) {
    console.error(`\n❌ JSON Parse Error: ${error}`);
    console.error(`\nFirst 500 chars of response:`);
    console.error(response.text.slice(0, 500));
    console.error(`\n...`);
    console.error(`\nLast 500 chars of response:`);
    console.error(response.text.slice(-500));
    throw error;
  }

  // Add extraction timestamp
  conceptGraph.metadata.extracted_at = new Date().toISOString();
  conceptGraph.metadata.total_concepts = conceptGraph.nodes.length;

  // Save
  console.log(`💾 Saving concept graph...`);
  fs.writeFileSync(outputPath, JSON.stringify(conceptGraph, null, 2));

  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`✅ EXTRACTION COMPLETE`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
  console.log(`📊 Extracted ${conceptGraph.nodes.length} concepts`);
  console.log(`📁 Saved to: ${outputPath}\n`);

  // Print sample concepts
  console.log(`🎯 Sample concepts:\n`);
  conceptGraph.nodes.slice(0, 5).forEach((node, i) => {
    console.log(`   ${i + 1}. ${node.name} (${node.difficulty})`);
    console.log(`      ${node.description.slice(0, 80)}...`);
    console.log(`      Prerequisites: ${node.prerequisites.length > 0 ? node.prerequisites.join(", ") : "none"}\n`);
  });
}

// ============================================================================
// CLI Interface
// ============================================================================

const videoId = process.argv[2];

if (!videoId) {
  console.error(`Usage: tsx extract-concepts.ts <video_id>`);
  console.error(`Example: tsx extract-concepts.ts kCc8FmEb1nY`);
  process.exit(1);
}

extractConcepts(videoId).catch((error) => {
  console.error(`\n❌ Error extracting concepts:`, error);
  process.exit(1);
});
