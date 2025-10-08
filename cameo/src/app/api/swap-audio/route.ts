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

import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { NextRequest, NextResponse } from "next/server";
import fs from "fs/promises";
import { createReadStream, createWriteStream } from "fs";
import path from "path";
import ffmpeg from "fluent-ffmpeg";

// Extract audio from video
async function extractAudio(videoPath: string, audioPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    ffmpeg(videoPath)
      .noVideo()
      .audioCodec("libmp3lame")
      .audioBitrate(192)
      .toFormat("mp3")
      .on("end", () => resolve())
      .on("error", (error) => reject(new Error(`Audio extraction failed: ${error.message}`)))
      .save(audioPath);
  });
}

// Combine video (no audio) with new audio
async function combineVideoAudio(
  videoPath: string,
  audioPath: string,
  outputPath: string
): Promise<void> {
  return new Promise((resolve, reject) => {
    ffmpeg(videoPath)
      .input(audioPath)
      .outputOptions([
        "-c:v copy", // Copy video codec (no re-encoding)
        "-c:a aac", // AAC audio codec
        "-map 0:v:0", // Map video from first input
        "-map 1:a:0", // Map audio from second input
        "-shortest", // Match shortest stream duration
      ])
      .on("end", () => resolve())
      .on("error", (error) =>
        reject(new Error(`Video/audio combination failed: ${error.message}`))
      )
      .save(outputPath);
  });
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const videoFile = formData.get("video") as File;
    const voiceId = formData.get("voiceId") as string;

    if (!videoFile) {
      return NextResponse.json(
        { error: "No video file provided" },
        { status: 400 }
      );
    }

    if (!voiceId) {
      return NextResponse.json(
        { error: "No voiceId provided" },
        { status: 400 }
      );
    }

    console.log(`🎬 Starting audio swap for voiceId: ${voiceId}`);

    // Create temp directory
    const tempDir = path.join(process.cwd(), "tmp");
    await fs.mkdir(tempDir, { recursive: true });

    const timestamp = Date.now();
    const videoPath = path.join(tempDir, `video-${timestamp}.mp4`);
    const extractedAudioPath = path.join(tempDir, `extracted-${timestamp}.mp3`);
    const clonedAudioPath = path.join(tempDir, `cloned-${timestamp}.mp3`);
    const finalVideoPath = path.join(tempDir, `final-${timestamp}.mp4`);

    // 1. Write video to disk
    console.log("📝 Writing video to disk...");
    const videoBuffer = Buffer.from(await videoFile.arrayBuffer());
    await fs.writeFile(videoPath, videoBuffer);

    // 2. Extract audio from video
    console.log("🎵 Extracting audio from video...");
    await extractAudio(videoPath, extractedAudioPath);

    // 3. Call ElevenLabs Speech-to-Speech API
    console.log("🎤 Applying voice clone with Speech-to-Speech API...");
    const elevenlabs = new ElevenLabsClient({
      apiKey: process.env.ELEVENLABS_API_KEY,
    });

    const audioStream = await elevenlabs.speechToSpeech.convert(voiceId, {
      audio: createReadStream(extractedAudioPath),
      model_id: "eleven_english_sts_v2", // Speech-to-Speech model
    });

    // 4. Save cloned audio to disk
    console.log("💾 Saving cloned audio...");
    await new Promise<void>((resolve, reject) => {
      const writeStream = createWriteStream(clonedAudioPath);

      // Convert async iterator to stream
      (async () => {
        try {
          for await (const chunk of audioStream) {
            writeStream.write(chunk);
          }
          writeStream.end();
        } catch (error) {
          reject(error);
        }
      })();

      writeStream.on("finish", () => resolve());
      writeStream.on("error", reject);
    });

    // 5. Combine original video with cloned audio
    console.log("🎬 Combining video with cloned audio...");
    await combineVideoAudio(videoPath, clonedAudioPath, finalVideoPath);

    // 6. Save to test-data for inspection
    const outputPath = path.join(process.cwd(), "test-data", "final-swapped-video.mp4");
    await fs.copyFile(finalVideoPath, outputPath);

    console.log(`✅ Success! Video saved to: test-data/final-swapped-video.mp4`);

    // 7. Cleanup temp files
    await fs.unlink(videoPath);
    await fs.unlink(extractedAudioPath);
    await fs.unlink(clonedAudioPath);
    await fs.unlink(finalVideoPath);

    return NextResponse.json({
      success: true,
      outputPath: "test-data/final-swapped-video.mp4",
      message: "Audio swapped successfully! Check test-data/final-swapped-video.mp4",
    });
  } catch (error: any) {
    console.error("❌ Audio swap error:", error);
    return NextResponse.json(
      { error: error.message || "Failed to swap audio" },
      { status: 500 }
    );
  }
}
