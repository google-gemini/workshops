/**
 * Download YouTube transcript with timestamps
 * 
 * Usage:
 *   npx ts-node scripts/youtube/download-transcript.ts kCc8FmEb1nY
 */

import { YoutubeTranscript } from 'youtube-transcript';
import * as fs from 'fs/promises';
import * as path from 'path';

interface TranscriptSegment {
  text: string;
  start: number;  // seconds
  duration: number;  // seconds
  end: number;  // seconds
}

async function downloadTranscript(videoId: string): Promise<void> {
  console.log(`📹 Downloading transcript for video: ${videoId}`);
  console.log(`🔗 URL: https://www.youtube.com/watch?v=${videoId}\n`);

  try {
    // Fetch transcript from YouTube
    const rawTranscript = await YoutubeTranscript.fetchTranscript(videoId);
    
    console.log(`✅ Downloaded ${rawTranscript.length} segments\n`);

    // Transform to our format (convert ms to seconds)
    const transcript: TranscriptSegment[] = rawTranscript.map(item => ({
      text: item.text,
      start: item.offset / 1000,
      duration: item.duration / 1000,
      end: (item.offset + item.duration) / 1000
    }));

    // Calculate total duration
    const totalDuration = transcript[transcript.length - 1].end;
    const hours = Math.floor(totalDuration / 3600);
    const minutes = Math.floor((totalDuration % 3600) / 60);
    const seconds = Math.floor(totalDuration % 60);
    
    console.log(`⏱️  Total duration: ${hours}h ${minutes}m ${seconds}s`);
    console.log(`📊 Average segment length: ${(totalDuration / transcript.length).toFixed(2)}s\n`);

    // Show first 5 segments as sample
    console.log('📝 Sample segments (first 5):\n');
    transcript.slice(0, 5).forEach((segment, i) => {
      const timestamp = formatTimestamp(segment.start);
      console.log(`[${timestamp}] (${segment.duration.toFixed(1)}s)`);
      console.log(`  "${segment.text}"\n`);
    });

    // Show a segment from middle of video
    const midIndex = Math.floor(transcript.length / 2);
    const midSegment = transcript[midIndex];
    console.log(`📝 Sample segment from middle of video (segment ${midIndex}):\n`);
    console.log(`[${formatTimestamp(midSegment.start)}] (${midSegment.duration.toFixed(1)}s)`);
    console.log(`  "${midSegment.text}"\n`);

    // Save to file
    const outputDir = path.join(process.cwd(), 'youtube', videoId);
    await fs.mkdir(outputDir, { recursive: true });
    
    const outputFile = path.join(outputDir, 'transcript.json');
    await fs.writeFile(
      outputFile,
      JSON.stringify({
        video_id: videoId,
        video_url: `https://www.youtube.com/watch?v=${videoId}`,
        total_segments: transcript.length,
        total_duration: totalDuration,
        downloaded_at: new Date().toISOString(),
        transcript: transcript
      }, null, 2)
    );

    console.log(`💾 Saved transcript to: ${outputFile}`);
    console.log(`\n🎬 Direct link format example: https://youtu.be/${videoId}?t=${Math.floor(midSegment.start)}`);

  } catch (error) {
    console.error('❌ Error downloading transcript:', error);
    throw error;
  }
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
const videoId = process.argv[2] || 'kCc8FmEb1nY'; // Default to Karpathy's GPT video

downloadTranscript(videoId)
  .then(() => {
    console.log('\n✨ Done!');
  })
  .catch(err => {
    console.error('\n💥 Failed:', err.message);
    process.exit(1);
  });
