import { z } from 'zod';

// ============================================================================
// Transcript Types (used by download-transcript, transcribe-audio, analyze-frames)
// ============================================================================

export const transcriptSegmentSchema = z.object({
  text: z.string(),
  start: z.number(),
  end: z.number(),
  duration: z.number().optional(),
  confidence: z.number().optional(),
});

export const audioTranscriptSchema = z.object({
  audio_file: z.string(),
  total_duration: z.number(),
  segments: z.array(transcriptSegmentSchema),
  full_transcript: z.string(),
  transcribed_at: z.string(),
});

// ============================================================================
// Concept Graph Types (used by extract-concepts, enrich-concepts, map-segments)
// ============================================================================

export const conceptNodeSchema = z.object({
  id: z.string().describe("Snake_case identifier"),
  name: z.string().describe("Human-readable concept name"),
  description: z.string().describe("Clear pedagogical description"),
  prerequisites: z.array(z.string()).describe("IDs of prerequisite concepts"),
  difficulty: z.enum(["basic", "intermediate", "advanced"]),
  time_ranges: z.array(z.object({
    start: z.number(),
    end: z.number(),
  })).optional(),
  code_examples: z.array(z.any()).optional(),
  learning_objectives: z.array(z.string()).optional(),
  common_misconceptions: z.array(z.string()).optional(),
});

export const conceptGraphSchema = z.object({
  metadata: z.object({
    title: z.string(),
    author: z.string(),
    source: z.string(),
    video_id: z.string(),
    total_duration: z.number(),
    total_concepts: z.number(),
    extracted_at: z.string(),
    enriched_at: z.string().optional(),
    enrichment_version: z.string().optional(),
  }),
  nodes: z.array(conceptNodeSchema),
});

// ============================================================================
// Video Analysis Types (used by analyze-frames, map-segments)
// ============================================================================

export const videoSegmentSchema = z.object({
  segment_index: z.number(),
  timestamp: z.number(),
  audio_text: z.string(),
  audio_start: z.number(),
  audio_end: z.number(),
  frame_path: z.string(),
  analysis: z.object({
    visual_description: z.string(),
    code_content: z.string().optional(),
    slide_content: z.string().optional(),
    visual_audio_alignment: z.enum([
      "highly_relevant",
      "somewhat_relevant",
      "transitional",
      "unrelated"
    ]),
    key_concepts: z.array(z.string()),
    is_code_readable: z.boolean().optional(),
  }),
});

export const videoAnalysisSchema = z.object({
  video_id: z.string(),
  total_segments: z.number(),
  results: z.array(videoSegmentSchema),
  analyzed_at: z.string(),
});

// ============================================================================
// Segment Mapping Types (used by map-segments-to-concepts)
// ============================================================================

export const conceptMappingSchema = z.object({
  concept_id: z.string().describe("The ID of the primary concept this segment discusses"),
  confidence: z.number().min(0).max(1).describe("Confidence score 0-1 for this mapping"),
  secondary_concepts: z.array(z.string()).optional().describe("Other concepts mentioned but not primary focus"),
  reasoning: z.string().optional().describe("Brief explanation of why this mapping was chosen")
});

export const mappedSegmentSchema = videoSegmentSchema.extend({
  concept_mapping: conceptMappingSchema.optional(),
});

export const segmentMappingsSchema = z.object({
  video_id: z.string(),
  total_segments: z.number(),
  mapped_at: z.string(),
  segments: z.array(mappedSegmentSchema),
});

// ============================================================================
// Inferred Types
// ============================================================================

export type TranscriptSegment = z.infer<typeof transcriptSegmentSchema>;
export type AudioTranscript = z.infer<typeof audioTranscriptSchema>;
export type ConceptNode = z.infer<typeof conceptNodeSchema>;
export type ConceptGraph = z.infer<typeof conceptGraphSchema>;
export type VideoSegment = z.infer<typeof videoSegmentSchema>;
export type VideoAnalysis = z.infer<typeof videoAnalysisSchema>;
export type ConceptMapping = z.infer<typeof conceptMappingSchema>;
export type MappedSegment = z.infer<typeof mappedSegmentSchema>;
export type SegmentMappings = z.infer<typeof segmentMappingsSchema>;
