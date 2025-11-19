import { GoogleGenAI } from "@google/genai";
import * as fs from "fs";
import * as path from "path";
import { zodToGeminiSchema } from "../../lib/gemini-utils.js";
import {
  audioTranscriptSchema,
  conceptGraphSchema,
  type ConceptGraph,
} from "./types.js";

// ============================================================================
// Prompt Construction
// ============================================================================

function buildValidationPrompt(conceptGraph: ConceptGraph, transcript: string): string {
  const conceptList = conceptGraph.nodes
    .map((c, i) => `${i + 1}. ${c.name} (${c.difficulty})
   ID: ${c.id}
   Prerequisites: ${c.prerequisites.length > 0 ? c.prerequisites.join(", ") : "none"}
   Description: ${c.description}`)
    .join("\n\n");

  return `Fix any prerequisite issues in this pedagogical concept graph.

Look for:
- Backwards dependencies (simple concept requiring complex one that uses it)
- Missing obvious prerequisites (advanced concept missing clear foundation)
- Circular dependencies (A→B→A loops)

CONCEPTS:
${conceptList}

TRANSCRIPT (teaching order context):
${transcript.slice(0, 15000)}

Return the complete fixed concept graph with corrected prerequisites.`;
}

// ============================================================================
// Main Validation Logic
// ============================================================================

async function validatePrerequisites(videoId: string): Promise<void> {
  console.log(`\n🔍 PREREQUISITE VALIDATION`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);

  // Paths
  const videoDir = path.join(process.cwd(), "youtube", videoId);
  const conceptGraphPath = path.join(videoDir, "concept-graph.json");
  const transcriptPath = path.join(videoDir, "audio-transcript.json");

  // Load data
  console.log(`📖 Loading concept graph and transcript...`);
  const conceptGraph = conceptGraphSchema.parse(
    JSON.parse(fs.readFileSync(conceptGraphPath, "utf-8"))
  );
  const transcriptData = audioTranscriptSchema.parse(
    JSON.parse(fs.readFileSync(transcriptPath, "utf-8"))
  );

  const prereqsBefore = conceptGraph.nodes.reduce((sum, n) => sum + n.prerequisites.length, 0);
  console.log(`   ${conceptGraph.nodes.length} concepts, ${prereqsBefore} prerequisites\n`);

  // Call Gemini
  console.log(`🔮 Fixing prerequisites...\n`);
  const ai = new GoogleGenAI({});
  const prompt = buildValidationPrompt(conceptGraph, transcriptData.full_transcript);

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: prompt,
    config: {
      responseMimeType: "application/json",
      responseJsonSchema: zodToGeminiSchema(conceptGraphSchema),
    },
  });

  if (!response.text) {
    throw new Error("No response received");
  }

  // Parse and save
  const fixedGraph = conceptGraphSchema.parse(JSON.parse(response.text));
  fixedGraph.metadata.prerequisites_validated_at = new Date().toISOString();

  fs.writeFileSync(conceptGraphPath, JSON.stringify(fixedGraph, null, 2));

  const prereqsAfter = fixedGraph.nodes.reduce((sum, n) => sum + n.prerequisites.length, 0);
  
  console.log(`✅ Done! ${prereqsBefore} → ${prereqsAfter} prerequisites`);
  console.log(`📁 Saved to: ${conceptGraphPath}`);
  console.log(`💡 Review: git diff ${conceptGraphPath}\n`);
}

// ============================================================================
// CLI Interface
// ============================================================================

const videoId = process.argv[2];

if (!videoId) {
  console.error(`Usage: tsx validate-prerequisites.ts <video_id>`);
  console.error(`Example: tsx validate-prerequisites.ts kCc8FmEb1nY`);
  process.exit(1);
}

validatePrerequisites(videoId).catch((error) => {
  console.error(`\n❌ Error validating prerequisites:`, error);
  process.exit(1);
});
