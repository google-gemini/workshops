import { GoogleGenAI } from "@google/genai";
import * as fs from "fs";
import * as path from "path";
import { z } from "zod";
import { zodToGeminiSchema } from "../../lib/gemini-utils.js";
import {
  audioTranscriptSchema,
  conceptGraphSchema,
  type ConceptGraph,
} from "./types.js";

// ============================================================================
// Schemas
// ============================================================================

const prerequisiteAssignmentSchema = z.object({
  concept_id: z.string(),
  prerequisites: z.array(z.string()).describe("Array of concept IDs that are prerequisites"),
  reasoning: z.string().describe("Brief explanation of why these are prerequisites"),
});

const prerequisitesResponseSchema = z.object({
  assignments: z.array(prerequisiteAssignmentSchema),
});

// ============================================================================
// Prompt Construction
// ============================================================================

function buildPrerequisitesPrompt(
  concepts: ConceptGraph["nodes"],
  transcript: string,
  videoDuration: number
): string {
  const conceptList = concepts
    .map((c, i) => `${i + 1}. **${c.id}** (${c.name}) - ${c.difficulty}\n   ${c.description}`)
    .join("\n\n");

  return `You are an expert at analyzing pedagogical dependencies in programming tutorials.

Given these ${concepts.length} concepts extracted from a programming tutorial, assign prerequisites based on:
1. **Teaching order** in the transcript - if concept B is taught immediately after A and builds on it, A is likely a prerequisite
2. **Logical dependencies** - concept A must be understood before concept B makes sense
3. **Pedagogical progression** - the instructor's intended learning path

ASSIGNMENT STRATEGY:
- Assign IMMEDIATE prerequisites (the direct building blocks)
- Preserve linear teaching progressions when the instructor teaches sequentially
- A concept can have ZERO prerequisites if it's truly foundational or standalone
- Multiple concepts can share the same prerequisites
- Avoid circular dependencies

Example thinking:
- If "residual_connections" is taught, then "layer_normalization" builds on residuals → residual_connections IS a prerequisite
- If "batch_normalization" is taught separately later → look for its immediate prerequisites in teaching order
- If "pytorch_tensors" is mentioned as context but not the focus → it may not be a prerequisite

CONCEPTS:
${conceptList}

VIDEO DETAILS:
- Duration: ${Math.floor(videoDuration / 60)} minutes
- Teaching order reveals dependencies: concepts taught sequentially often have prerequisite relationships

TRANSCRIPT (use this to identify teaching order and immediate dependencies):
${transcript}

For each concept, assign its IMMEDIATE prerequisites (by concept ID) based on teaching order and logical dependencies. Explain your reasoning briefly.`;
}

// ============================================================================
// Main Logic
// ============================================================================

async function assignPrerequisites(videoId: string): Promise<void> {
  console.log(`\n🔗 PREREQUISITE ASSIGNMENT (Pass 2 of 2)`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
  console.log(`📹 Video ID: ${videoId}\n`);

  // Paths
  const videoDir = path.join(process.cwd(), "youtube", videoId);
  const conceptGraphPath = path.join(videoDir, "concept-graph.json");
  const transcriptPath = path.join(videoDir, "audio-transcript.json");

  // Check if files exist
  if (!fs.existsSync(conceptGraphPath)) {
    throw new Error(`❌ Concept graph not found: ${conceptGraphPath}\nRun extract-concepts.ts first!`);
  }
  if (!fs.existsSync(transcriptPath)) {
    throw new Error(`❌ Transcript not found: ${transcriptPath}`);
  }

  console.log(`📖 Reading concept graph and transcript...`);
  const conceptGraph = conceptGraphSchema.parse(
    JSON.parse(fs.readFileSync(conceptGraphPath, "utf-8"))
  );
  const transcriptData = audioTranscriptSchema.parse(
    JSON.parse(fs.readFileSync(transcriptPath, "utf-8"))
  );

  console.log(`   Concepts: ${conceptGraph.nodes.length}`);
  console.log(`   Transcript: ${transcriptData.full_transcript.length} characters\n`);

  // Initialize Gemini
  console.log(`🤖 Initializing Gemini 2.5 Flash...`);
  const ai = new GoogleGenAI({});

  // Build prompt
  console.log(`📝 Building prerequisites prompt...\n`);
  const prompt = buildPrerequisitesPrompt(
    conceptGraph.nodes,
    transcriptData.full_transcript,
    transcriptData.total_duration
  );

  // Call Gemini
  console.log(`🔮 Assigning prerequisites...`);
  console.log(`   (This may take 30-60 seconds)\n`);

  const startTime = Date.now();

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: prompt,
    config: {
      responseMimeType: "application/json",
      responseJsonSchema: zodToGeminiSchema(prerequisitesResponseSchema),
    },
  });

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`✅ Received response in ${elapsed}s\n`);

  if (!response.text) {
    throw new Error("No response text received from Gemini");
  }

  // Parse and apply prerequisites
  console.log(`🔍 Parsing prerequisite assignments...`);
  const assignments = prerequisitesResponseSchema.parse(JSON.parse(response.text));

  console.log(`🔗 Applying ${assignments.assignments.length} prerequisite assignments...\n`);

  // Create a map for quick lookup
  const assignmentMap = new Map(
    assignments.assignments.map(a => [a.concept_id, a])
  );

  // Update concept graph
  let foundationalCount = 0;
  for (const node of conceptGraph.nodes) {
    const assignment = assignmentMap.get(node.id);
    if (assignment) {
      node.prerequisites = assignment.prerequisites;
      if (assignment.prerequisites.length === 0) {
        foundationalCount++;
      }
    } else {
      console.warn(`⚠️  No assignment found for concept: ${node.id}`);
    }
  }

  // Update metadata
  conceptGraph.metadata.prerequisites_assigned_at = new Date().toISOString();

  // Save back to original file (overwrite)
  console.log(`💾 Saving enriched concept graph...`);
  fs.writeFileSync(conceptGraphPath, JSON.stringify(conceptGraph, null, 2));

  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`✅ PREREQUISITE ASSIGNMENT COMPLETE`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
  console.log(`📊 Stats:`);
  console.log(`   Total concepts: ${conceptGraph.nodes.length}`);
  console.log(`   Foundational (no prerequisites): ${foundationalCount}`);
  console.log(`   With prerequisites: ${conceptGraph.nodes.length - foundationalCount}`);
  console.log(`📁 Saved to: ${conceptGraphPath}\n`);

  // Show sample assignments
  console.log(`🎯 Sample prerequisite assignments:\n`);
  assignments.assignments.slice(0, 5).forEach((a, i) => {
    const concept = conceptGraph.nodes.find(n => n.id === a.concept_id);
    console.log(`   ${i + 1}. ${concept?.name}`);
    console.log(`      Prerequisites: ${a.prerequisites.length > 0 ? a.prerequisites.join(", ") : "none (foundational)"}`);
    console.log(`      Reasoning: ${a.reasoning}\n`);
  });
}

// ============================================================================
// CLI Interface
// ============================================================================

const videoId = process.argv[2];

if (!videoId) {
  console.error(`Usage: tsx assign-prerequisites.ts <video_id>`);
  console.error(`Example: tsx assign-prerequisites.ts kCc8FmEb1nY`);
  process.exit(1);
}

assignPrerequisites(videoId).catch((error) => {
  console.error(`\n❌ Error assigning prerequisites:`, error);
  process.exit(1);
});
