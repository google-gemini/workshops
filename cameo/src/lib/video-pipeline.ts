import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createReadStream, createWriteStream } from "fs";
import ffmpeg from "fluent-ffmpeg";
import fs from "fs/promises";

/**
 * Extract audio from video file
 */
export async function extractAudio(videoPath: string, audioPath: string): Promise<void> {
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

/**
 * Combine video (no audio) with new audio
 */
export async function combineVideoAudio(
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

/**
 * Convert WebM audio to MP3 format
 */
export async function convertWebmToMp3(inputPath: string, outputPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    ffmpeg(inputPath)
      .audioBitrate(192)
      .toFormat("mp3")
      .on("end", () => resolve())
      .on("error", (error) => reject(new Error(`FFmpeg conversion failed: ${error.message}`)))
      .save(outputPath);
  });
}

/**
 * Train a voice with ElevenLabs IVC
 * @returns voiceId
 */
export async function trainVoice(
  audioPath: string,
  voiceName: string,
  apiKey: string
): Promise<string> {
  const mp3Path = audioPath.replace(/\.\w+$/, '.mp3');
  
  // Convert to MP3 if needed
  if (!audioPath.endsWith('.mp3')) {
    await convertWebmToMp3(audioPath, mp3Path);
  }

  // Train voice
  const elevenlabs = new ElevenLabsClient({ apiKey });
  const voice = await elevenlabs.voices.ivc.create({
    name: voiceName,
    files: [createReadStream(mp3Path)],
  });

  return voice.voiceId;
}

/**
 * Swap audio in video with cloned voice using ElevenLabs Speech-to-Speech
 */
export async function swapAudioWithVoice(
  videoPath: string,
  voiceId: string,
  outputPath: string,
  apiKey: string,
  tempDir: string
): Promise<void> {
  const timestamp = Date.now();
  const extractedAudioPath = `${tempDir}/extracted-${timestamp}.mp3`;
  const clonedAudioPath = `${tempDir}/cloned-${timestamp}.mp3`;

  try {
    // 1. Extract audio from video
    await extractAudio(videoPath, extractedAudioPath);

    // 2. Clone voice using Speech-to-Speech
    const elevenlabs = new ElevenLabsClient({ apiKey });
    const audioStream = await elevenlabs.speechToSpeech.convert(voiceId, {
      audio: createReadStream(extractedAudioPath),
      model_id: "eleven_english_sts_v2",
    });

    // 3. Save cloned audio
    await new Promise<void>((resolve, reject) => {
      const writeStream = createWriteStream(clonedAudioPath);
      
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

    // 4. Combine video with cloned audio
    await combineVideoAudio(videoPath, clonedAudioPath, outputPath);

    // 5. Cleanup temp files
    await fs.unlink(extractedAudioPath);
    await fs.unlink(clonedAudioPath);
  } catch (error) {
    // Cleanup on error
    try {
      await fs.unlink(extractedAudioPath).catch(() => {});
      await fs.unlink(clonedAudioPath).catch(() => {});
    } catch {}
    throw error;
  }
}
