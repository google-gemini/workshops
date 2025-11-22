import { GoogleGenAI } from "@google/genai";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
import { zodToGeminiSchema } from "../../lib/gemini-utils.js";

// ============================================================================
// Zod Schema for Code-Concept Mapping
// ============================================================================

const codeMappingSchema = z.object({
  unique_snippets: z.array(z.object({
    primary_segment: z.number().describe("Main segment index where this code appears"),
    timestamp: z.number().describe("Timestamp in seconds"),
    code: z.string().describe("The actual code snippet"),
    concepts: z.array(z.string()).describe("Concept IDs this code demonstrates"),
    rationale: z.string().describe("Why this code maps to these concepts"),
    teaching_context: z.string().describe("What this code teaches"),
    duplicate_segments: z.array(z.number()).describe("Other segments with identical/similar code"),
  })),
  rejected_segments: z.array(z.object({
    segment_index: z.number(),
    reason: z.string().describe("Why this was filtered (e.g., 'Generated Shakespeare output')"),
  })),
  statistics: z.object({
    total_segments_analyzed: z.number(),
    unique_code_snippets: z.number(),
    rejected_segments: z.number(),
  }),
});

type CodeMapping = z.infer<typeof codeMappingSchema>;

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

function loadVideoAnalysis(videoId: string): any {
  const analysisPath = path.join(
    process.cwd(),
    `youtube/${videoId}/video-analysis.json`
  );
  return JSON.parse(fs.readFileSync(analysisPath, "utf-8"));
}

// ============================================================================
// Filter Segments with Code
// ============================================================================

function extractCodeSegments(videoAnalysis: any): any[] {
  return videoAnalysis.results
    .filter((seg: any) => 
      seg.analysis?.code_content && 
      seg.analysis.code_content.trim().length > 50 // Meaningful code
    )
    .map((seg: any) => ({
      segment_index: seg.segment_index,
      timestamp: seg.timestamp,
      audio_text: seg.audio_text?.substring(0, 200), // Context snippet
      code_content: seg.analysis.code_content,
      key_concepts: seg.analysis.key_concepts || [],
    }));
}

// ============================================================================
// Map Code to Concepts with Gemini
// ============================================================================

async function mapCodeToConcepts(
  conceptGraph: any,
  codeSegments: any[],
  batchSize: number = 100
): Promise<CodeMapping> {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY environment variable not set");
  }

  const ai = new GoogleGenAI({ apiKey });

  // Build concept reference
  const conceptList = conceptGraph.nodes
    .map((node: any) => `- ${node.id}: ${node.name} - ${node.description}`)
    .join("\n");

  // Batch processing
  const allMappings: CodeMapping[] = [];
  
  for (let i = 0; i < codeSegments.length; i += batchSize) {
    const batch = codeSegments.slice(i, i + batchSize);
    
    console.log(`\n📦 Processing batch ${Math.floor(i / batchSize) + 1} (segments ${i}-${i + batch.length})...`);

    const segmentList = batch
      .map((seg, idx) => 
        `### Segment ${seg.segment_index} (${seg.timestamp}s)\n` +
        `Audio: "${seg.audio_text}"\n` +
        `Code:\n\`\`\`python\n${seg.code_content}\n\`\`\``
      )
      .join("\n\n");

    const prompt = `You are analyzing teaching code from a programming video about transformers/GPT.

**Available Concepts:**
${conceptList}

**Your Task:**
1. **Filter garbage**: Reject generated outputs (Shakespeare text, model-generated gibberish)
2. **Deduplicate**: Identify unique code snippets (merge identical/similar code)
3. **Map to concepts**: Associate each unique snippet with 1-3 concept IDs
4. **Explain**: Describe what each snippet teaches

**Code Segments to Analyze:**

${segmentList}

**Instructions:**
- For duplicate code across segments, pick the BEST example (clearest, most complete)
- Only map to concepts that truly appear in the code
- Be strict about filtering non-teaching content
- Provide clear rationale for each mapping`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseJsonSchema: zodToGeminiSchema(codeMappingSchema),
      },
    });

    const batchMapping = codeMappingSchema.parse(JSON.parse(response.text));
    allMappings.push(batchMapping);
    
    console.log(`   ✅ Found ${batchMapping.unique_snippets.length} unique snippets`);
    console.log(`   🗑️  Rejected ${batchMapping.rejected_segments.length} segments`);
  }

  // Merge all batches
  return {
    unique_snippets: allMappings.flatMap(m => m.unique_snippets),
    rejected_segments: allMappings.flatMap(m => m.rejected_segments),
    statistics: {
      total_segments_analyzed: codeSegments.length,
      unique_code_snippets: allMappings.reduce((sum, m) => sum + m.unique_snippets.length, 0),
      rejected_segments: allMappings.reduce((sum, m) => sum + m.rejected_segments.length, 0),
    },
  };
}

// ============================================================================
// Main
// ============================================================================

async function main() {
  const videoId = process.argv[2];

  if (!videoId) {
    console.error("Usage: npx tsx map-code-to-concepts.ts <video-id>");
    process.exit(1);
  }

  console.log(`🔗 Mapping code to concepts for video: ${videoId}\n`);

  // Load data
  const conceptGraph = loadConceptGraph(videoId);
  const videoAnalysis = loadVideoAnalysis(videoId);

  console.log(`📊 Loaded:`);
  console.log(`   - ${conceptGraph.nodes.length} concepts`);
  
  // Debug: Check video analysis structure
  if (!videoAnalysis.results) {
    console.error(`\n❌ Error: video-analysis.json doesn't have 'results' property`);
    console.error(`Available keys: ${Object.keys(videoAnalysis).join(', ')}`);
    process.exit(1);
  }
  
  console.log(`   - ${videoAnalysis.results.length} total segments`);

  // Extract code segments
  const codeSegments = extractCodeSegments(videoAnalysis);
  console.log(`   - ${codeSegments.length} segments with code\n`);

  // Map code to concepts
  const mapping = await mapCodeToConcepts(conceptGraph, codeSegments);

  // Save output
  const outputPath = path.join(
    process.cwd(),
    `youtube/${videoId}/code-concept-mappings.json`
  );

  fs.writeFileSync(outputPath, JSON.stringify(mapping, null, 2));

  console.log(`\n✅ Mapping complete!`);
  console.log(`📄 Saved to: ${outputPath}`);
  console.log(`\n📈 Statistics:`);
  console.log(`   - Total analyzed: ${mapping.statistics.total_segments_analyzed}`);
  console.log(`   - Unique snippets: ${mapping.statistics.unique_code_snippets}`);
  console.log(`   - Rejected: ${mapping.statistics.rejected_segments}`);
}

main().catch(console.error);
