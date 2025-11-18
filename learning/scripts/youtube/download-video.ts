/**
 * Download YouTube video and extract audio using youtubei.js
 * 
 * Usage:
 *   npx ts-node scripts/youtube/download-video.ts <video-id-or-url>
 *   npx ts-node scripts/youtube/download-video.ts sg_fuEzFw0g
 *   npx ts-node scripts/youtube/download-video.ts https://www.youtube.com/watch?v=sg_fuEzFw0g
 */

import { Innertube, UniversalCache } from 'youtubei.js/web';
import * as fs from 'fs/promises';
import * as path from 'path';
import { createWriteStream } from 'fs';

interface DownloadResult {
  video_id: string;
  title: string;
  audio_path: string;
  duration: number;
  downloaded_at: string;
}

function extractVideoId(input: string): string {
  // If it's already just an ID
  if (/^[a-zA-Z0-9_-]{11}$/.test(input)) {
    return input;
  }
  
  // Extract from URL
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
    /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
  ];
  
  for (const pattern of patterns) {
    const match = input.match(pattern);
    if (match) return match[1];
  }
  
  throw new Error(`Invalid YouTube URL or video ID: ${input}`);
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
}

function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
  return `${m}:${s.toString().padStart(2, '0')}`;
}

async function downloadVideo(videoInput: string): Promise<DownloadResult> {
  const videoId = extractVideoId(videoInput);
  console.log(`📹 Downloading video: ${videoId}`);
  console.log(`🔗 URL: https://www.youtube.com/watch?v=${videoId}\n`);

  // Initialize Innertube
  const innertube = await Innertube.create({ 
    cache: new UniversalCache(true),
  });

  // Get video info
  console.log('🔍 Fetching video info...');
  const info = await innertube.getInfo(videoId);
  
  const title = info.basic_info.title || 'Unknown';
  const duration = info.basic_info.duration || 0;
  
  console.log(`📝 Title: ${title}`);
  console.log(`⏱️  Duration: ${formatDuration(duration)}\n`);

  // Create output directory
  const outputDir = path.join('youtube', videoId);
  await fs.mkdir(outputDir, { recursive: true });

  // Download audio stream
  const audioPath = path.join(outputDir, 'audio.mp3');
  console.log(`💾 Downloading audio to: ${audioPath}`);
  console.log('⏳ Please wait...\n');

  // Get the best audio format
  const format = info.chooseFormat({ 
    type: 'audio',
    quality: 'best',
  });

  if (!format) {
    throw new Error('No audio format available for this video');
  }

  console.log(`🎵 Format: ${format.mime_type}`);
  console.log(`📊 Bitrate: ${format.bitrate ? Math.round(format.bitrate / 1000) + ' kbps' : 'unknown'}\n`);

  // Download the stream
  const stream = await innertube.download(videoId, {
    type: 'audio',
    quality: 'best',
    format: 'mp4', // This will be audio-only MP4/M4A
  });

  // Write to file with progress tracking
  const fileStream = createWriteStream(audioPath);
  let downloadedBytes = 0;
  let lastProgressUpdate = Date.now();

  // Convert ReadableStream to Node stream and track progress
  const reader = stream.getReader();
  let done = false;

  while (!done) {
    const { value, done: streamDone } = await reader.read();
    done = streamDone;
    
    if (value) {
      downloadedBytes += value.length;
      fileStream.write(Buffer.from(value));
      
      // Update progress every 500ms
      const now = Date.now();
      if (now - lastProgressUpdate > 500) {
        process.stdout.write(`\r📥 Downloaded: ${formatBytes(downloadedBytes)}`);
        lastProgressUpdate = now;
      }
    }
  }

  fileStream.end();
  await new Promise<void>((resolve, reject) => {
    fileStream.on('finish', () => resolve());
    fileStream.on('error', reject);
  });

  console.log(`\r📥 Downloaded: ${formatBytes(downloadedBytes)} ✅\n`);

  // Save metadata
  const metadataPath = path.join(outputDir, 'metadata.json');
  const metadata = {
    video_id: videoId,
    title,
    duration,
    url: `https://www.youtube.com/watch?v=${videoId}`,
    channel: info.basic_info.channel?.name || 'Unknown',
    view_count: info.basic_info.view_count || 0,
    downloaded_at: new Date().toISOString(),
  };

  await fs.writeFile(metadataPath, JSON.stringify(metadata, null, 2));
  console.log(`💾 Saved metadata to: ${metadataPath}`);

  return {
    video_id: videoId,
    title,
    audio_path: audioPath,
    duration,
    downloaded_at: metadata.downloaded_at,
  };
}

// Main execution
const videoInput = process.argv[2];

if (!videoInput) {
  console.error('Usage: npx ts-node scripts/youtube/download-video.ts <video-id-or-url>');
  console.error('Examples:');
  console.error('  npx ts-node scripts/youtube/download-video.ts sg_fuEzFw0g');
  console.error('  npx ts-node scripts/youtube/download-video.ts https://www.youtube.com/watch?v=sg_fuEzFw0g');
  process.exit(1);
}

downloadVideo(videoInput)
  .then((result) => {
    console.log('\n✨ Download complete!');
    console.log(`\n📁 Files saved to: youtube/${result.video_id}/`);
    console.log(`\nNext step: Transcribe the audio`);
    console.log(`  npx ts-node scripts/youtube/transcribe-audio.ts ${result.audio_path}`);
  })
  .catch(err => {
    console.error('\n💥 Download failed:', err.message);
    process.exit(1);
  });
