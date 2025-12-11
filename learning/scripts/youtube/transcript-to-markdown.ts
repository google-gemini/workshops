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

/**
 * YouTube Transcript to Markdown Converter
 * 
 * Uses Gemini API to extract transcript from YouTube video and format it as markdown.
 * The markdown output can then be processed by chunk-paip.ts for semantic chunking.
 * 
 * Usage:
 *   npx ts-node scripts/youtube/transcript-to-markdown.ts <youtube-url> [output.md]
 * 
 * Example:
 *   npx ts-node scripts/youtube/transcript-to-markdown.ts "https://www.youtube.com/watch?v=kCc8FmEb1nY"
 */

import { GoogleGenAI } from "@google/genai";
import { YoutubeTranscript } from 'youtube-transcript';
import * as fs from 'fs/promises';
import * as path from 'path';

// Extract video ID from various YouTube URL formats
function extractVideoId(url: string): string | null {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
    /^([a-zA-Z0-9_-]{11})$/,
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return match[1];
  }
  return null;
}

// Format timestamp as HH:MM:SS or MM:SS
function formatTimestamp(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
  return `${m}:${s.toString().padStart(2, '0')}`;
}

/**
 * Main function: Extract YouTube transcript and convert to markdown using Gemini
 */
async function transcriptToMarkdown(youtubeUrl: string, outputPath?: string): Promise<void> {
  console.log('📹 YouTube Transcript to Markdown Converter\n');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  // Extract video ID
  const videoId = extractVideoId(youtubeUrl);
  if (!videoId) {
    throw new Error(`Invalid YouTube URL format: ${youtubeUrl}`);
  }

  console.log(`📹 Video ID: ${videoId}`);
  console.log(`🔗 URL: ${youtubeUrl}\n`);

  // Check for API key
  const apiKey = process.env.GOOGLE_API_KEY;
  if (!apiKey) {
    throw new Error('GOOGLE_API_KEY not found in environment variables');
  }

  // Step 1: Download raw transcript from YouTube
  console.log('\n📥 Step 1: Downloading transcript from YouTube...');
  let rawTranscript: Array<{ text: string; offset: number; duration: number }>;
  
  try {
    rawTranscript = await YoutubeTranscript.fetchTranscript(videoId);
    
    if (!rawTranscript || rawTranscript.length === 0) {
      throw new Error('Transcript is empty. The video may not have captions available.');
    }
    
    console.log(`   ✅ Downloaded ${rawTranscript.length} transcript segments\n`);
    
    // Debug: Show first segment structure (only in verbose mode)
    // console.log(`   📋 Sample segment:`, rawTranscript[0]);
  } catch (error: any) {
    throw new Error(`Failed to download transcript: ${error.message}\n   Tip: The video may not have captions enabled.`);
  }

  // Step 2: Combine transcript segments into full text with timestamps
  console.log('📝 Step 2: Processing transcript segments...');
  
  if (rawTranscript.length === 0) {
    throw new Error('Transcript is empty. The video may not have captions available.');
  }
  
  const transcriptSegments = rawTranscript.map((item, index) => {
    if (!item || typeof item.offset === 'undefined' || typeof item.duration === 'undefined') {
      throw new Error(`Invalid transcript segment at index ${index}: ${JSON.stringify(item)}`);
    }
    return {
      text: item.text || '',
      timestamp: item.offset / 1000, // Convert ms to seconds
      duration: item.duration / 1000,
    };
  });

  if (transcriptSegments.length === 0) {
    throw new Error('Failed to process transcript segments');
  }

  const lastSegment = transcriptSegments[transcriptSegments.length - 1];
  if (!lastSegment || typeof lastSegment.timestamp === 'undefined') {
    throw new Error(`Invalid last segment: ${JSON.stringify(lastSegment)}`);
  }
  
  const totalDuration = lastSegment.timestamp + lastSegment.duration;
  
  // Combine into full transcript text with timestamp markers
  const fullTranscriptText = transcriptSegments
    .map(seg => `[${formatTimestamp(seg.timestamp)}] ${seg.text}`)
    .join('\n');

  console.log(`   ✅ Processed ${transcriptSegments.length} segments`);
  console.log(`   ⏱️  Total duration: ${formatTimestamp(totalDuration)}\n`);

  // Step 3: Use Gemini to format transcript as structured markdown
  console.log('🤖 Step 3: Formatting transcript as markdown using Gemini...');
  const ai = new GoogleGenAI({ apiKey });

  const formattingPrompt = `You are a content formatter. Convert this YouTube video transcript into a well-structured markdown document.

Video URL: ${youtubeUrl}
Video ID: ${videoId}
Total Duration: ${formatTimestamp(totalDuration)}
Number of segments: ${transcriptSegments.length}

TRANSCRIPT (with timestamps):
${fullTranscriptText.substring(0, 200000)}${fullTranscriptText.length > 200000 ? '\n[... transcript continues ...]' : ''}

Requirements:
1. Create a clear markdown structure:
   - Use # for main title (infer from transcript content)
   - Use ## for major sections/topics (group related segments)
   - Use ### for subtopics
   - Preserve natural flow and meaning

2. Formatting guidelines:
   - Remove redundant timestamp markers, but keep key timestamps at section breaks
   - If code is discussed, format it in code blocks with appropriate language tags
   - Use markdown formatting for emphasis, lists, code, etc.
   - Group related content into logical sections
   - Maintain the original meaning and flow

3. Structure:
   - Start with a title based on the video content
   - Organize content into logical sections
   - Use clear headings to separate topics
   - Preserve technical terminology and code examples

4. Quality:
   - Remove filler words ("um", "uh") if they don't affect meaning
   - Fix obvious transcription errors
   - Maintain natural speech flow where appropriate
   - Keep all important technical content

Return ONLY the markdown content, no additional commentary or explanations.`;

  try {
    console.log('   🔮 Calling Gemini to format transcript...');
    const startTime = Date.now();

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: formattingPrompt,
      config: {
        temperature: 0.3, // Lower temperature for more consistent formatting
        maxOutputTokens: 32000, // Allow for long transcripts
      },
    });

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log(`   ✅ Received formatted markdown (${elapsed}s)\n`);

    // Extract markdown content
    if (!response.text) {
      throw new Error('No text response from Gemini');
    }
    const markdownContent = response.text.trim();

    if (!markdownContent || markdownContent.length < 100) {
      throw new Error('Received empty or very short markdown from Gemini');
    }

    console.log(`📊 Transcript Statistics:`);
    console.log(`   - Length: ${markdownContent.length} characters`);
    console.log(`   - Estimated words: ~${Math.round(markdownContent.length / 5)}`);
    console.log(`   - Preview (first 300 chars):`);
    console.log(`   ${markdownContent.substring(0, 300).replace(/\n/g, '\n   ')}...\n`);

    // Step 4: Determine output path
    const defaultOutputPath = path.join(
      process.cwd(),
      'youtube',
      videoId,
      'transcript.md'
    );
    const finalOutputPath = outputPath || defaultOutputPath;

    // Create output directory if needed
    const outputDir = path.dirname(finalOutputPath);
    await fs.mkdir(outputDir, { recursive: true });

    // Step 4: Save markdown file
    console.log('💾 Step 4: Saving markdown transcript...');
    await fs.writeFile(finalOutputPath, markdownContent, 'utf-8');
    console.log(`   ✅ Saved to: ${finalOutputPath}\n`);

    // Step 6: Provide next steps
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    console.log('✨ Success! Transcript converted to markdown.\n');
    console.log('📝 Next steps:');
    console.log(`   1. Review the markdown: ${finalOutputPath}`);
    console.log(`   2. Chunk it using: npx ts-node scripts/chunk-paip.ts "${finalOutputPath}"`);
    console.log(`   3. Generate embeddings: npx ts-node scripts/embed-chunks.ts <chunks-output.json>\n`);

  } catch (error: any) {
    console.error('\n❌ Error processing video:');
    console.error(`   ${error.message}`);
    
    if (error.message.includes('transcript') || error.message.includes('captions')) {
      console.error('\n💡 Tip: The video may not have captions available.');
      console.error('   Try a different video or check if captions are enabled.\n');
    }
    
    throw error;
  }
}

// Parse command line arguments
function parseArgs(): { url: string; outputPath?: string } {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error('Usage: npx ts-node scripts/youtube/transcript-to-markdown.ts <youtube-url> [output.md]');
    console.error('\nExample:');
    console.error('  npx ts-node scripts/youtube/transcript-to-markdown.ts "https://www.youtube.com/watch?v=kCc8FmEb1nY"');
    process.exit(1);
  }

  return {
    url: args[0],
    outputPath: args[1],
  };
}

// Main execution
const { url, outputPath } = parseArgs();

transcriptToMarkdown(url, outputPath)
  .then(() => {
    process.exit(0);
  })
  .catch((error) => {
    console.error(`\n💥 Failed: ${error.message}`);
    process.exit(1);
  });

