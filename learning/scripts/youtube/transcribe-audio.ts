/**
 * Transcribe audio file using Google Cloud Speech-to-Text v2
 * 
 * Usage:
 *   npx ts-node scripts/youtube/transcribe-audio.ts youtube/kCc8FmEb1nY/audio.mp3
 */

import { v2, protos } from '@google-cloud/speech';
import { Storage } from '@google-cloud/storage';
import * as fs from 'fs/promises';
import * as path from 'path';

interface SegmentInfo {
  text: string;
  start: number;  // seconds (start time of this segment)
  end: number;    // seconds (end time of this segment)
  confidence: number;
}

interface TranscriptResult {
  video_id?: string;
  audio_file: string;
  total_duration: number;
  segments: SegmentInfo[];
  full_transcript: string;
  transcribed_at: string;
}

async function uploadToGCS(audioFile: string, projectId: string): Promise<string> {
  const storage = new Storage({ projectId });
  const bucketName = `${projectId}-speech-transcripts`;
  const fileName = `transcripts/${Date.now()}-${path.basename(audioFile)}`;
  
  // Ensure bucket exists
  const [buckets] = await storage.getBuckets();
  const bucketExists = buckets.some(b => b.name === bucketName);
  
  if (!bucketExists) {
    console.log(`📦 Creating bucket: ${bucketName}`);
    await storage.createBucket(bucketName, {
      location: 'US',
      storageClass: 'STANDARD',
    });
  }
  
  const bucket = storage.bucket(bucketName);
  const blob = bucket.file(fileName);
  
  console.log(`📤 Uploading to GCS: gs://${bucketName}/${fileName}`);
  await blob.save(await fs.readFile(audioFile));
  
  return `gs://${bucketName}/${fileName}`;
}

async function transcribeAudio(audioFile: string): Promise<TranscriptResult> {
  console.log(`🎙️  Transcribing: ${audioFile}\n`);

  // Initialize client
  const client = new v2.SpeechClient();
  
  const projectId = process.env.GOOGLE_CLOUD_PROJECT || process.env.GCP_PROJECT;
  if (!projectId) {
    throw new Error('GOOGLE_CLOUD_PROJECT environment variable not set');
  }

  // Check file size
  const stats = await fs.stat(audioFile);
  const fileSizeMB = stats.size / (1024 * 1024);
  console.log(`📊 File size: ${fileSizeMB.toFixed(2)} MB`);
  
  let audioUri: string | undefined;
  let audioContent: Buffer | undefined;
  
  // Force batch mode for all files (testing batch code path)
  if (fileSizeMB > 0) {
    console.log(`🧪 Forcing batch mode for testing...\n`);
    audioUri = await uploadToGCS(audioFile, projectId);
  } else {
    console.log(`✅ File size OK for direct upload\n`);
    audioContent = await fs.readFile(audioFile);
  }

  // Configure recognition request
  const request: any = {
    recognizer: `projects/${projectId}/locations/global/recognizers/_`,
    config: {
      autoDecodingConfig: {},
      languageCodes: ['en-US'],
      model: 'long',  // Optimized for long-form content (videos)
      features: {
        enableAutomaticPunctuation: true,
      },
    },
  };
  
  // Add either content or uri
  if (audioUri) {
    request.uri = audioUri;
  } else {
    request.content = audioContent;
  }

  console.log('🔄 Sending to Google Cloud Speech-to-Text...');
  console.log('⏳ This may take a few minutes for long videos...\n');

  // Transcribe - use batchRecognize for GCS URIs, recognize for inline content
  let response;
  if (audioUri) {
    // Use batch recognition for GCS files
    console.log('📦 Using batch recognition for GCS file...\n');
    
    const batchRequest = {
      recognizer: `projects/${projectId}/locations/global/recognizers/_`,
      config: request.config,
      files: [{
        uri: audioUri,
      }],
      recognitionOutputConfig: {
        inlineResponseConfig: {},  // Return results inline rather than to GCS
      },
    };
    
    const [operation] = await client.batchRecognize(batchRequest);
    const operationName = operation.name!;  // Assert non-null since batchRecognize always returns a name
    console.log(`🔄 Operation started: ${operationName}\n`);
    
    console.log('⏳ Waiting for batch operation to complete...');
    console.log('   (This may take several minutes for long videos)\n');
    
    // Poll for progress using the operations client
    let lastProgress = 0;
    let pollCount = 0;
    const operationsClient = client.operationsClient;
    
    let batchResponse: any;
    const pollInterval = setInterval(async () => {
      pollCount++;
      try {
        // Use the specialized checkBatchRecognizeProgress method for proper decoding
        const operation = await client.checkBatchRecognizeProgress(operationName);
        const done = operation.done;
        
        // Cast metadata to any to access progressPercent (protobuf-generated types)
        const metadata = operation.metadata as any;
        const progress = metadata?.progressPercent || 0;
        
        // Show polling heartbeat every 4 polls (20 seconds)
        if (pollCount % 4 === 0) {
          const elapsed = (pollCount * 5) / 60;
          console.log(`💓 Polling... (${elapsed.toFixed(1)} min elapsed, status: ${done ? 'done' : 'running'})`);
        }
        
        if (progress > lastProgress) {
          lastProgress = progress;
          console.log(`⏳ Progress: ${progress}%`);
        }
        
        // Check if operation is complete
        if (done) {
          clearInterval(pollInterval);
          
          // Response is wrapped in google.protobuf.Any - need to decode it
          const anyResponse = operation.response as any;
          if (anyResponse && anyResponse.value) {
            const responseBuffer = Buffer.isBuffer(anyResponse.value)
              ? anyResponse.value
              : Buffer.from(anyResponse.value.data || anyResponse.value);
            
            batchResponse = protos.google.cloud.speech.v2.BatchRecognizeResponse.decode(responseBuffer);
          } else {
            throw new Error('Operation completed but no response value found');
          }
          
          console.log('\n✅ Batch operation complete!\n');
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : String(err);
        console.log(`⚠️  Polling attempt ${pollCount}: ${errorMessage}`);
      }
    }, 5000);  // Poll every 5 seconds
    
    // Wait for polling to detect completion
    await new Promise<void>((resolve) => {
      const checkInterval = setInterval(() => {
        if (batchResponse) {
          clearInterval(checkInterval);
          resolve();
        }
      }, 100);  // Check every 100ms
    });
    
    console.log('✅ Batch operation complete!\n');
    
    // Extract results from batch response
    const audioResult = batchResponse.results?.[audioUri];
    const transcriptResults = audioResult?.transcript;
    
    if (!transcriptResults?.results) {
      throw new Error('No transcript results found in batch response');
    }
    
    response = {
      results: transcriptResults.results,
    };
  } else {
    // Use synchronous recognition for small files
    [response] = await client.recognize(request);
  }

  // Process results - extract segments with result-level timing
  const segments: SegmentInfo[] = [];
  let fullTranscript = '';
  let lastEndTime = 0;

  for (const result of response.results || []) {
    const alternative = result.alternatives?.[0];
    if (!alternative) continue;

    const text = alternative.transcript || '';
    fullTranscript += text + ' ';

    // Extract result-level end time
    const endSecs = Number(result.resultEndOffset?.seconds || 0) + 
                   Number(result.resultEndOffset?.nanos || 0) / 1e9;
    
    segments.push({
      text,
      start: lastEndTime,
      end: endSecs,
      confidence: alternative.confidence || 0,
    });
    
    lastEndTime = endSecs;
  }

  const totalDuration = segments.length > 0 ? segments[segments.length - 1].end : 0;

  console.log(`✅ Transcribed ${segments.length} segments`);
  console.log(`⏱️  Duration: ${formatDuration(totalDuration)}`);
  console.log(`📊 Average confidence: ${(segments.reduce((sum, s) => sum + s.confidence, 0) / segments.length * 100).toFixed(1)}%\n`);

  // Show sample
  console.log('📝 Sample (first 3 segments):\n');
  segments.slice(0, 3).forEach((seg, i) => {
    console.log(`  [${i + 1}] ${seg.text}`);
  });
  console.log();

  return {
    audio_file: audioFile,
    total_duration: totalDuration,
    segments,
    full_transcript: fullTranscript.trim(),
    transcribed_at: new Date().toISOString(),
  };
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

// Main execution
const audioFile = process.argv[2];

if (!audioFile) {
  console.error('Usage: npx ts-node scripts/youtube/transcribe-audio.ts <audio-file>');
  console.error('Example: npx ts-node scripts/youtube/transcribe-audio.ts youtube/kCc8FmEb1nY/audio.mp3');
  process.exit(1);
}

transcribeAudio(audioFile)
  .then(async (result) => {
    // Save results
    const outputFile = audioFile.replace(/\.(mp3|wav|m4a)$/, '-transcript.json');
    await fs.writeFile(outputFile, JSON.stringify(result, null, 2));
    
    console.log(`💾 Saved transcript to: ${outputFile}`);
    console.log('\n✨ Done!');
  })
  .catch(err => {
    console.error('\n💥 Failed:', err.message);
    process.exit(1);
  });
