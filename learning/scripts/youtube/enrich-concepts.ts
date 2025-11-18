import { GoogleGenAI } from "@google/genai";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
import { zodToGeminiSchema } from "../../lib/gemini-utils.js";

// ============================================================================
// Schemas
// ============================================================================

// What Gemini outputs: ONLY pedagogical enrichment
const pedagogicalEnrichmentSchema = z.object({
  learning_objectives: z.array(z.string())
    .describe("3-5 specific, measurable learning goals starting with action verbs"),
  
  mastery_indicators: z.array(z.object({
    skill: z.string().describe("Short identifier for this skill (e.g., 'base_case_identification')"),
    description: z.string().describe("What mastery of this skill demonstrates"),
    difficulty: z.enum(["basic", "intermediate", "advanced"]),
    test_method: z.string().describe("Concrete way to assess this skill in Socratic dialogue"),
  })).describe("CRITICAL: These determine when students can progress to next concepts"),
  
  misconceptions: z.array(z.object({
    misconception: z.string().describe("Common incorrect belief about this concept"),
    reality: z.string().describe("What is actually true"),
    correction_strategy: z.string().describe("How to guide student from misconception to reality"),
  })),
  
  key_insights: z.array(z.string())
    .describe("2-4 fundamental truths or 'aha moments' about this concept"),
  
  // Optional: Let Gemini add more if useful
  practical_applications: z.array(z.string()).optional()
    .describe("Real-world uses or applications of this concept"),
  
  common_gotchas: z.array(z.string()).optional()
    .describe("Practical pitfalls or tricky aspects when implementing"),
  
  debugging_tips: z.array(z.string()).optional()
    .describe("How to debug issues related to this concept"),
});

type PedagogicalEnrichment = z.infer<typeof pedagogicalEnrichmentSchema>;

// Final enriched concept structure (what we save to disk)
const enrichedConceptSchema = z.object({
  // Original concept metadata
  id: z.string(),
  name: z.string(),
  description: z.string(),
  prerequisites: z.array(z.string()),
  difficulty: z.enum(["beginner", "intermediate", "advanced"]),
  time_ranges: z.array(z.object({
    start: z.number(),
    end: z.number(),
  })),
  
  // Code examples (merged deterministically)
  code_examples: z.array(z.object({
    segment_index: z.number(),
    timestamp: z.number(),
    code: z.string(),
    rationale: z.string(),
    teaching_context: z.string(),
  })),
  
  // Pedagogical enrichment (from Gemini)
  learning_objectives: z.array(z.string()),
  mastery_indicators: z.array(z.object({
    skill: z.string(),
    description: z.string(),
    difficulty: z.enum(["basic", "intermediate", "advanced"]),
    test_method: z.string(),
  })),
  misconceptions: z.array(z.object({
    misconception: z.string(),
    reality: z.string(),
    correction_strategy: z.string(),
  })),
  key_insights: z.array(z.string()),
  practical_applications: z.array(z.string()).optional(),
  common_gotchas: z.array(z.string()).optional(),
  debugging_tips: z.array(z.string()).optional(),
});

type EnrichedConcept = z.infer<typeof enrichedConceptSchema>;

// ============================================================================
// Load Input Data
// ============================================================================

function loadConceptGraph(videoId: string): any {
  const conceptPath = path.join(
    process.cwd(),
    `youtube/${videoId}/concept-graph.json`
  );
  return JSON.parse(fs.readFileSync(conceptPath, "utf-8"));
}

function loadCodeMappings(videoId: string): any {
  const mappingsPath = path.join(
    process.cwd(),
    `youtube/${videoId}/code-concept-mappings.json`
  );
  return JSON.parse(fs.readFileSync(mappingsPath, "utf-8"));
}

function loadTranscript(videoId: string): any {
  const transcriptPath = path.join(
    process.cwd(),
    `youtube/${videoId}/audio-transcript.json`
  );
  return JSON.parse(fs.readFileSync(transcriptPath, "utf-8"));
}

// ============================================================================
// Helper Functions
// ============================================================================

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function getCodeExamplesForConcept(conceptId: string, codeMappings: any): any[] {
  return codeMappings.unique_snippets
    .filter((snippet: any) => snippet.concepts.includes(conceptId))
    .map((snippet: any) => ({
      segment_index: snippet.primary_segment,
      timestamp: snippet.timestamp,
      code: snippet.code,
      rationale: snippet.rationale,
      teaching_context: snippet.teaching_context,
    }));
}


// ============================================================================
// Build Enrichment Prompt
// ============================================================================

function buildEnrichmentPrompt(
  concept: any,
  codeExamples: any[],
  fullTranscript: string,
  prerequisites: any[]
): string {
  const prerequisiteNames = prerequisites
    .filter(p => p)
    .map(p => p.name)
    .join(", ");
  
  const codeExamplesText = codeExamples.length > 0
    ? codeExamples
        .map(ex => `
[${formatTime(ex.timestamp)}] ${ex.teaching_context}

\`\`\`python
${ex.code}
\`\`\`

Why this matters: ${ex.rationale}
`)
        .join("\n---\n")
    : "No code examples identified for this concept.";

  return `You are designing comprehensive pedagogical metadata for a programming concept from Andrej Karpathy's GPT tutorial video.

**Concept:**
${concept.name}
Description: ${concept.description}
Difficulty Level: ${concept.difficulty}
Prerequisites: ${prerequisiteNames || "None"}

**Full video transcript:**
${fullTranscript}

**Code examples related to this concept:**
${codeExamplesText}

**Your task:**
Generate comprehensive pedagogical enrichment that will power an interactive Socratic learning system.

1. **Learning Objectives** (3-5 specific, measurable goals)
   - Start with action verbs: "Explain...", "Implement...", "Identify...", "Debug...", "Apply..."
   - Make them specific to what Karpathy actually teaches
   - Progress from understanding → application → mastery

2. **Mastery Indicators** (3-6 assessable skills)
   - CRITICAL: These determine when students can unlock dependent concepts
   - Progress: basic → intermediate → advanced
   - Each needs: skill identifier, description, difficulty, concrete test method
   - Test methods must be actionable in Socratic dialogue (questions to ask, code to write, etc.)
   - Think: "How would I know the student truly understands this?"

3. **Common Misconceptions** (2-4 realistic errors)
   - What do beginners actually get wrong about this?
   - Include: the misconception, the reality, and how to correct it
   - Ground in actual transcript if Karpathy addresses these

4. **Key Insights** (2-4 fundamental truths)
   - The "aha moments" that make this concept click
   - Memorable, foundational understanding
   - Often things Karpathy explicitly emphasizes

**Optional enrichment (add if relevant):**
- practical_applications: Real-world uses beyond this tutorial
- common_gotchas: Tricky implementation details or edge cases
- debugging_tips: How to diagnose and fix issues with this concept

**Guidelines:**
- Be authentic to Karpathy's teaching style and this video's content
- Reference actual code examples when relevant (use timestamps)
- Make mastery indicators TESTABLE via dialogue (not vague)
- Misconceptions should be realistic for someone learning transformers/GPT
- Balance rigor with accessibility

Return valid JSON matching the schema.`.trim();
}

// ============================================================================
// Enrich Single Concept
// ============================================================================

async function enrichConcept(
  concept: any,
  codeMappings: any,
  transcript: any,
  conceptGraph: any,
  ai: any
): Promise<EnrichedConcept> {
  console.log(`\n📚 Enriching: ${concept.name}`);
  
  // 1. Find code examples for this concept
  const codeExamples = getCodeExamplesForConcept(concept.id, codeMappings);
  console.log(`   📝 Found ${codeExamples.length} code examples`);
  
  // 2. Get prerequisite concepts for context
  const prerequisites = concept.prerequisites.map((preqId: string) =>
    conceptGraph.nodes.find((n: any) => n.id === preqId)
  );
  
  // 3. Build prompt with all context
  const prompt = buildEnrichmentPrompt(
    concept,
    codeExamples,
    transcript.full_transcript,
    prerequisites
  );
  
  // 4. Call Gemini with structured output (ONLY pedagogical enrichment)
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: prompt,
    config: {
      responseMimeType: "application/json",
      responseJsonSchema: zodToGeminiSchema(pedagogicalEnrichmentSchema),
    },
  });
  
  const pedagogicalEnrichment = pedagogicalEnrichmentSchema.parse(JSON.parse(response.text));
  
  console.log(`   ✅ ${pedagogicalEnrichment.learning_objectives.length} learning objectives`);
  console.log(`   ✅ ${pedagogicalEnrichment.mastery_indicators.length} mastery indicators`);
  console.log(`   ✅ ${pedagogicalEnrichment.misconceptions.length} misconceptions`);
  console.log(`   ✅ ${pedagogicalEnrichment.key_insights.length} key insights`);
  
  // 5. Merge deterministically: original metadata + code examples + pedagogical enrichment
  const enriched: EnrichedConcept = {
    id: concept.id,
    name: concept.name,
    description: concept.description,
    prerequisites: concept.prerequisites,
    difficulty: concept.difficulty,
    time_ranges: concept.time_ranges || [],
    code_examples: codeExamples,
    ...pedagogicalEnrichment,
  };
  
  return enriched;
}

// ============================================================================
// Main Processing Loop
// ============================================================================

async function enrichConcepts(videoId: string): Promise<void> {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY environment variable not set");
  }
  
  const ai = new GoogleGenAI({ apiKey });
  
  console.log(`🎓 Enriching concepts for video: ${videoId}\n`);
  
  // Load all inputs
  const conceptGraph = loadConceptGraph(videoId);
  const codeMappings = loadCodeMappings(videoId);
  const transcript = loadTranscript(videoId);
  
  console.log(`📊 Loaded:`);
  console.log(`   - ${conceptGraph.nodes.length} concepts`);
  console.log(`   - ${codeMappings.unique_snippets.length} code snippets`);
  console.log(`   - Full transcript (${Math.round(transcript.full_transcript.length / 1000)}k chars)`);
  
  const enrichedConcepts: EnrichedConcept[] = [];
  
  // Process each concept
  for (const concept of conceptGraph.nodes) {
    try {
      const enriched = await enrichConcept(
        concept,
        codeMappings,
        transcript,
        conceptGraph,
        ai
      );
      
      enrichedConcepts.push(enriched);
      
      // Rate limiting: small delay between concepts
      await new Promise(resolve => setTimeout(resolve, 1000));
      
    } catch (error) {
      console.error(`   ❌ Failed to enrich ${concept.name}:`, error);
      // Continue with other concepts even if one fails
    }
  }
  
  // Save enriched concept graph
  const outputPath = path.join(
    process.cwd(),
    `youtube/${videoId}/concept-graph-enriched.json`
  );
  
  const enrichedGraph = {
    metadata: {
      ...conceptGraph.metadata,
      enriched_at: new Date().toISOString(),
      enrichment_version: "1.0",
    },
    nodes: enrichedConcepts,
    edges: conceptGraph.edges,
  };
  
  fs.writeFileSync(outputPath, JSON.stringify(enrichedGraph, null, 2));
  
  console.log(`\n✅ Enrichment complete!`);
  console.log(`📄 Saved to: ${outputPath}`);
  console.log(`\n📈 Summary:`);
  console.log(`   - ${enrichedConcepts.length} concepts enriched`);
  console.log(`   - ${enrichedConcepts.reduce((sum, c) => sum + c.learning_objectives.length, 0)} total learning objectives`);
  console.log(`   - ${enrichedConcepts.reduce((sum, c) => sum + c.mastery_indicators.length, 0)} total mastery indicators`);
  console.log(`   - ${enrichedConcepts.reduce((sum, c) => sum + c.misconceptions.length, 0)} total misconceptions`);
}

// ============================================================================
// CLI Entry Point
// ============================================================================

async function main() {
  const videoId = process.argv[2];
  
  if (!videoId) {
    console.error("Usage: npx tsx enrich-concepts.ts <video-id>");
    console.error("\nExample: npx tsx enrich-concepts.ts kCc8FmEb1nY");
    process.exit(1);
  }
  
  await enrichConcepts(videoId);
}

main().catch(console.error);
