import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { NextRequest, NextResponse } from "next/server";
import fs from "fs/promises";
import { createReadStream } from "fs";
import path from "path";
import ffmpeg from "fluent-ffmpeg";

async function convertWebmToMp3(inputPath: string, outputPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    ffmpeg(inputPath)
      .audioBitrate(192)
      .toFormat("mp3")
      .on("end", () => resolve())
      .on("error", (error) => reject(new Error(`FFmpeg conversion failed: ${error.message}`)))
      .save(outputPath);
  });
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const audioFile = formData.get("audio") as File;
    const voiceName = (formData.get("name") as string) || "My Voice Clone";

    if (!audioFile) {
      return NextResponse.json({ error: "No audio file provided" }, { status: 400 });
    }

    // Create temp directory
    const tempDir = path.join(process.cwd(), "tmp");
    await fs.mkdir(tempDir, { recursive: true });
    
    const timestamp = Date.now();
    const webmPath = path.join(tempDir, `upload-${timestamp}.webm`);
    const mp3Path = path.join(tempDir, `converted-${timestamp}.mp3`);

    // Write WebM to disk
    const buffer = Buffer.from(await audioFile.arrayBuffer());
    await fs.writeFile(webmPath, buffer);

    // Convert WebM → MP3 at 192kbps
    await convertWebmToMp3(webmPath, mp3Path);

    // Call ElevenLabs IVC API
    const elevenlabs = new ElevenLabsClient({
      apiKey: process.env.ELEVENLABS_API_KEY,
    });

    const voice = await elevenlabs.voices.ivc.create({
      name: voiceName,
      files: [createReadStream(mp3Path)],
    });

    // Cleanup temp files
    await fs.unlink(webmPath);
    await fs.unlink(mp3Path);

    return NextResponse.json({
      success: true,
      voiceId: voice.voiceId,
      name: voiceName,
      message: "Voice clone created successfully",
    });

  } catch (error: any) {
    console.error("Voice training error:", error);
    return NextResponse.json(
      { error: error.message || "Failed to train voice" },
      { status: 500 }
    );
  }
}
