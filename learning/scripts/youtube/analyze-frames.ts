/**
 * Analyze video frames with Gemini, correlating with audio transcript
 * 
 * Usage:
 *   npx ts-node scripts/youtube/analyze-frames.ts <video-id>
 *   npx ts-node scripts/youtube/analyze-frames.ts kCc8FmEb1nY
 * 
 * Prerequisites:
 *   - youtube/{video-id}/video.mp4 (from download-media.sh)
 *   - youtube/{video-id}/audio-transcript.json (from transcribe-audio.ts)
 */

import { GoogleGenerativeAI } from "@google/generative-ai";
import { z } from "zod";
import * as fs from "fs/promises";
import * as path from "path";
import ffmpeg from "fluent-ffmpeg";
import { zodToGeminiSchema } from "../../lib/gemini-utils.js";

// Schema for structured frame analysis
const frameAnalysisSchema = z.object({
  // Visual content
  visual_description: z.string().describe(
    "Detailed description of what's visible in the frame (code, slides, person, IDE, etc.)"
  ),
  
  // Code extraction (if present)
  code_content: z.string().optional().describe(
    "Any code visible on screen, extracted as text. Empty if no code visible."
  ),
  
  // Text/slides (if present)
  slide_content: z.string().optional().describe(
    "Any presentation slides, diagrams, or text visible. Empty if none."
  ),
  
  // Context linking
  visual_audio_alignment: z.enum([
    "highly_relevant",    // Visual directly shows what's being discussed
    "somewhat_relevant",  // Visual provides context
    "transitional",       // Frame caught during a transition
    "unrelated"          // Visual doesn't match audio (rare)
  ]).describe("How well the visual content aligns with the audio transcript"),
  
  // Key concepts
  key_concepts: z.array(z.string()).describe(
    "Main programming concepts, functions, or ideas visible in this frame"
  ),
  
  // Quality indicators
  is_code_readable: z.boolean().optional().describe(
    "Is code on screen clear and readable? (if code present)"
  ),
});

type FrameAnalysis = z.infer<typeof frameAnalysisSchema>;

interface TranscriptSegment {
  text: string;
  start: number;
  end: number;
  confidence: number;
}

interface Transcript {
  audio_file: string;
  total_duration: number;
  segments: TranscriptSegment[];
  full_transcript: string;
  transcribed_at: string;
}

interface EnrichedResult {
  segment_index: number;
  timestamp: number;
  audio_text: string;
  audio_start: number;
  audio_end: number;
  frame_path: string;
  analysis: FrameAnalysis;
}

interface FailedFrame {
  segment_index: number;
  timestamp: number;
  audio_text: string;
  error_type: string;
  error_message: string;
}

/**
 * Extract a single frame from video at specified timestamp
 */
async function extractFrameAtTimestamp(
  videoPath: string,
  timestamp: number,
  outputPath: string
): Promise<void> {
  return new Promise((resolve, reject) => {
    ffmpeg(videoPath)
      .seekInput(timestamp)
      .frames(1)
      .outputOptions(['-q:v 2'])  // High quality JPEG
      .output(outputPath)
      .on("end", () => resolve())
      .on("error", (err) => reject(new Error(`Frame extraction failed: ${err.message}`)))
      .run();
  });
}

/**
 * Analyze a frame with Gemini, providing audio context
 */
async function analyzeFrameWithTranscript(
  genAI: GoogleGenerativeAI,
  framePath: string,
  audioText: string,
  timestamp: number,
  verbose: boolean = false
): Promise<FrameAnalysis> {
  const frameData = await fs.readFile(framePath, { encoding: "base64" });
  
  const prompt = `
You are analyzing a frame from a programming tutorial video.

**Timestamp:** ${timestamp.toFixed(2)}s
**Audio transcript at this moment:** "${audioText}"

Analyze what's visible in this frame and how it relates to what's being said.
Extract any code, text, or key concepts visible.
Focus on technical content that would help someone understand what's being taught.
  `.trim();
  
  const model = genAI.getGenerativeModel({
    model: "gemini-2.5-flash",
    generationConfig: {
      responseMimeType: "application/json",
      responseSchema: zodToGeminiSchema(frameAnalysisSchema),
    },
  });
  
  const result = await model.generateContent([
    {
      inlineData: {
        mimeType: "image/jpeg",
        data: frameData,
      },
    },
    { text: prompt },
  ]);
  
  const response = result.response;
  const text = response.text();
  
  if (verbose) {
    console.log(`\n🔍 Raw Gemini response:\n${text}\n`);
  }
  
  return frameAnalysisSchema.parse(JSON.parse(text));
}

/**
 * Process a batch of segments concurrently
 */
async function processBatch(
  batch: Array<{ segment: TranscriptSegment; index: number }>,
  videoPath: string,
  framesDir: string,
  genAI: GoogleGenerativeAI,
  totalSegments: number,
  verbose: boolean
): Promise<{ successes: EnrichedResult[], failures: FailedFrame[] }> {
  const results = await Promise.all(
    batch.map(async ({ segment, index }) => {
      const timestamp = (segment.start + segment.end) / 2;
      const framePath = path.join(
        framesDir,
        `frame_${index.toString().padStart(4, "0")}.jpg`
      );
      
      console.log(`[${index + 1}/${totalSegments}] Processing segment at ${formatTimestamp(timestamp)}`);
      console.log(`   Audio: "${segment.text.substring(0, 60)}${segment.text.length > 60 ? '...' : ''}"`);
      
      try {
        // Extract frame
        process.stdout.write(`   📸 Extracting frame... `);
        await extractFrameAtTimestamp(videoPath, timestamp, framePath);
        console.log(`✅`);
        
        // Analyze with Gemini
        process.stdout.write(`   🔍 Analyzing with Gemini... `);
        const analysis = await analyzeFrameWithTranscript(
          genAI,
          framePath,
          segment.text,
          timestamp,
          verbose
        );
        console.log(`✅`);
        
        console.log(`   📝 Visual: ${analysis.visual_description.substring(0, 60)}...`);
        console.log(`   🔗 Alignment: ${analysis.visual_audio_alignment}`);
        if (analysis.key_concepts.length > 0) {
          console.log(`   💡 Concepts: ${analysis.key_concepts.join(", ")}`);
        }
        console.log();
        
        return {
          success: true,
          result: {
            segment_index: index,
            timestamp,
            audio_text: segment.text,
            audio_start: segment.start,
            audio_end: segment.end,
            frame_path: framePath,
            analysis,
          }
        };
      } catch (err: any) {
        // Extract error type for better reporting
        let errorType = "UNKNOWN";
        let errorMessage = err.message || String(err);
        
        if (errorMessage.includes("RECITATION")) {
          errorType = "RECITATION";
        } else if (errorMessage.includes("SAFETY")) {
          errorType = "SAFETY";
        } else if (errorMessage.includes("rate limit") || errorMessage.includes("429")) {
          errorType = "RATE_LIMIT";
        } else if (errorMessage.includes("timeout")) {
          errorType = "TIMEOUT";
        }
        
        console.log(`❌ FAILED (${errorType})`);
        console.log(`   Error: ${errorMessage.substring(0, 100)}${errorMessage.length > 100 ? '...' : ''}`);
        console.log();
        
        return {
          success: false,
          failure: {
            segment_index: index,
            timestamp,
            audio_text: segment.text,
            error_type: errorType,
            error_message: errorMessage,
          }
        };
      }
    })
  );
  
  // Separate successes and failures
  const successes: EnrichedResult[] = [];
  const failures: FailedFrame[] = [];
  
  for (const result of results) {
    if (result.success && result.result) {
      successes.push(result.result);
    } else if (!result.success && result.failure) {
      failures.push(result.failure);
    }
  }
  
  return { successes, failures };
}

/**
 * Process all segments, extracting frames and analyzing with Gemini
 */
async function processVideoSegments(videoId: string, verbose: boolean = false) {
  console.log(`🎬 Starting frame analysis for video: ${videoId}\n`);
  
  const baseDir = path.join("youtube", videoId);
  const videoPath = path.join(baseDir, "video.mp4");
  const transcriptPath = path.join(baseDir, "audio-transcript.json");
  const framesDir = path.join(baseDir, "frames");
  
  // Verify inputs exist
  try {
    await fs.access(videoPath);
    await fs.access(transcriptPath);
  } catch (err) {
    throw new Error(
      `Missing required files. Run download-media.sh and transcribe-audio.ts first.\n` +
      `Expected: ${videoPath} and ${transcriptPath}`
    );
  }
  
  // Create frames directory
  await fs.mkdir(framesDir, { recursive: true });
  
  // Load transcript
  const transcriptData = await fs.readFile(transcriptPath, "utf-8");
  const transcript: Transcript = JSON.parse(transcriptData);
  
  console.log(`📊 Transcript info:`);
  console.log(`   Total segments: ${transcript.segments.length}`);
  console.log(`   Total duration: ${formatDuration(transcript.total_duration)}\n`);
  
  // Initialize Gemini
  const apiKey = process.env.GOOGLE_API_KEY || process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error("GOOGLE_API_KEY or GEMINI_API_KEY environment variable not set");
  }
  const genAI = new GoogleGenerativeAI(apiKey);
  
  // Process segments in batches for better parallelism
  const BATCH_SIZE = 10; // Process 10 frames concurrently
  const results: EnrichedResult[] = [];
  const failures: FailedFrame[] = [];
  const startTime = Date.now();
  
  // Create batches
  const batches: Array<Array<{ segment: TranscriptSegment; index: number }>> = [];
  for (let i = 0; i < transcript.segments.length; i += BATCH_SIZE) {
    batches.push(
      transcript.segments
        .slice(i, i + BATCH_SIZE)
        .map((segment, idx) => ({ segment, index: i + idx }))
    );
  }
  
  console.log(`⚡ Processing ${transcript.segments.length} segments in ${batches.length} batches of ${BATCH_SIZE}\n`);
  
  for (const [batchIdx, batch] of batches.entries()) {
    console.log(`\n📦 Batch ${batchIdx + 1}/${batches.length}\n`);
    
    const batchResults = await processBatch(
      batch,
      videoPath,
      framesDir,
      genAI,
      transcript.segments.length,
      verbose
    );
    
    results.push(...batchResults.successes);
    failures.push(...batchResults.failures);
    
    // Brief pause between batches to avoid overwhelming the API
    if (batchIdx < batches.length - 1) {
      console.log(`⏸️  Pausing 2s before next batch...`);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  
  // Save enriched results
  const outputPath = path.join(baseDir, "video-analysis.json");
  await fs.writeFile(outputPath, JSON.stringify({
    video_id: videoId,
    analyzed_at: new Date().toISOString(),
    total_segments: transcript.segments.length,
    successful_segments: results.length,
    failed_segments: failures.length,
    results,
    failures,
  }, null, 2));
  
  const elapsedSeconds = (Date.now() - startTime) / 1000;
  
  console.log(`\n✨ Analysis complete!`);
  console.log(`   📊 Total segments: ${transcript.segments.length}`);
  console.log(`   ✅ Successful: ${results.length} (${((results.length / transcript.segments.length) * 100).toFixed(1)}%)`);
  console.log(`   ❌ Failed: ${failures.length} (${((failures.length / transcript.segments.length) * 100).toFixed(1)}%)`);
  console.log(`   ⏱️  Time: ${formatDuration(elapsedSeconds)}`);
  console.log(`   📁 Results: ${outputPath}\n`);
  
  // Print summary stats
  const alignmentCounts = results.reduce((acc, r) => {
    acc[r.analysis.visual_audio_alignment] = (acc[r.analysis.visual_audio_alignment] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  console.log(`📈 Alignment summary:`);
  Object.entries(alignmentCounts).forEach(([alignment, count]) => {
    const pct = ((count / results.length) * 100).toFixed(1);
    console.log(`   ${alignment}: ${count} (${pct}%)`);
  });
  
  const framesWithCode = results.filter(r => r.analysis.code_content).length;
  const framesWithSlides = results.filter(r => r.analysis.slide_content).length;
  console.log(`\n📊 Content summary:`);
  console.log(`   Frames with code: ${framesWithCode}`);
  console.log(`   Frames with slides: ${framesWithSlides}`);
  
  // Failure breakdown
  if (failures.length > 0) {
    console.log(`\n⚠️  Failure breakdown:`);
    const failuresByType = failures.reduce((acc, f) => {
      acc[f.error_type] = (acc[f.error_type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    Object.entries(failuresByType).forEach(([type, count]) => {
      console.log(`   ${type}: ${count}`);
    });
    
    console.log(`\n💡 Tip: Failed frames are logged in ${outputPath} under "failures"`);
  }
}

function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  
  if (h > 0) {
    return `${h}h ${m}m ${s}s`;
  }
  return `${m}m ${s}s`;
}

function formatTimestamp(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
  return `${m}:${s.toString().padStart(2, '0')}`;
}

// Main execution
const videoId = process.argv[2];
const verbose = process.argv.includes('--verbose') || process.argv.includes('-v');

if (!videoId) {
  console.error('Usage: npx ts-node scripts/youtube/analyze-frames.ts <video-id> [--verbose]');
  console.error('Example: npx ts-node scripts/youtube/analyze-frames.ts kCc8FmEb1nY');
  console.error('         npx ts-node scripts/youtube/analyze-frames.ts kCc8FmEb1nY --verbose');
  process.exit(1);
}

processVideoSegments(videoId, verbose)
  .catch(err => {
    console.error('\n💥 Analysis failed:', err.message);
    process.exit(1);
  });
