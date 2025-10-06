import { GoogleGenAI } from "@google/genai";
import { NextRequest, NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";
import sizeOf from "image-size";
import { trainVoice, swapAudioWithVoice } from "@/lib/video-pipeline";

export async function POST(request: NextRequest) {
  const startTime = Date.now();
  console.log("🎬 Starting unified video generation pipeline...");

  try {
    const formData = await request.formData();
    const leftImageFile = formData.get("leftImage") as File | null;
    const centerImageFile = formData.get("centerImage") as File | null;
    const rightImageFile = formData.get("rightImage") as File | null;
    const voiceAudioFile = formData.get("voiceAudio") as File;
    const videoFile = formData.get("video") as File | null; // Optional: skip Veo 3 generation
    const prompt = formData.get("prompt") as string;
    const voiceName = (formData.get("voiceName") as string) || "My Voice Clone";

    // Validation
    if (!videoFile && !centerImageFile) {
      return NextResponse.json(
        { error: "Must provide either 'video' file or at least 'centerImage' for generation" },
        { status: 400 }
      );
    }

    if (!videoFile && !prompt) {
      return NextResponse.json(
        { error: "Prompt required when generating new video with Veo 3" },
        { status: 400 }
      );
    }

    if (!voiceAudioFile) {
      return NextResponse.json(
        { error: "No voice audio provided" },
        { status: 400 }
      );
    }

    // Create directories for generated videos (public) and temp files
    const publicDir = path.join(process.cwd(), "public", "generated");
    const tempDir = path.join(process.cwd(), "tmp");
    await fs.mkdir(publicDir, { recursive: true });
    await fs.mkdir(tempDir, { recursive: true });

    const timestamp = Date.now();
    const leftImagePath = leftImageFile ? path.join(tempDir, `left-${timestamp}.png`) : "";
    const centerImagePath = centerImageFile ? path.join(tempDir, `center-${timestamp}.png`) : "";
    const rightImagePath = rightImageFile ? path.join(tempDir, `right-${timestamp}.png`) : "";
    const voiceAudioPath = path.join(tempDir, `voice-${timestamp}.webm`);
    const veoVideoPath = path.join(tempDir, `veo-${timestamp}.mp4`);
    const finalVideoPath = path.join(publicDir, `generated-video-${timestamp}.mp4`);

    // Write files to disk
    console.log("📝 Writing input files to disk...");
    
    if (leftImageFile) {
      const imageBuffer = Buffer.from(await leftImageFile.arrayBuffer());
      await fs.writeFile(leftImagePath, imageBuffer);
    }
    
    if (centerImageFile) {
      const imageBuffer = Buffer.from(await centerImageFile.arrayBuffer());
      await fs.writeFile(centerImagePath, imageBuffer);
    }
    
    if (rightImageFile) {
      const imageBuffer = Buffer.from(await rightImageFile.arrayBuffer());
      await fs.writeFile(rightImagePath, imageBuffer);
    }

    const audioBuffer = Buffer.from(await voiceAudioFile.arrayBuffer());
    await fs.writeFile(voiceAudioPath, audioBuffer);

    // ========================================
    // STEP 1: Train Voice with ElevenLabs
    // ========================================
    console.log("🎤 Step 1/5: Training voice with ElevenLabs...");
    const step1Start = Date.now();

    const voiceId = await trainVoice(
      voiceAudioPath,
      voiceName,
      process.env.ELEVENLABS_API_KEY!
    );

    console.log(`✅ Voice trained! ID: ${voiceId} (${Date.now() - step1Start}ms)`);

    // ========================================
    // STEP 2-4: Get Video (Generate or Use Provided)
    // ========================================
    let step2Time = 0;
    let pollCount = 0;
    
    if (videoFile) {
      // Use provided video - skip Veo 3 generation
      console.log("📹 Step 2/5: Using provided video file (skipping Veo 3)...");
      const videoStart = Date.now();
      
      const videoBuffer = Buffer.from(await videoFile.arrayBuffer());
      await fs.writeFile(veoVideoPath, videoBuffer);
      
      // Verify it's valid
      const stats = await fs.stat(veoVideoPath);
      console.log(`✅ Video loaded: ${(stats.size / 1024 / 1024).toFixed(2)} MB (${Date.now() - videoStart}ms)`);
      
      step2Time = Date.now() - videoStart;
    } else {
      // Generate with Veo 3
      console.log("🎥 Step 2/5: Generating video with Veo 3...");
      const step2Start = Date.now();

      const ai = new GoogleGenAI({
        apiKey: process.env.GOOGLE_GENAI_API_KEY,
      });

      // Read image and convert to base64 string
      const imageFileBuffer = await fs.readFile(centerImagePath);
      const imageBase64 = imageFileBuffer.toString('base64');

      // Detect image aspect ratio to choose video format
      const dimensions = sizeOf(imageFileBuffer);
      const aspectRatio = dimensions.width! / dimensions.height!;
      
      // Choose video aspect ratio based on source image
      let videoAspectRatio: "16:9" | "9:16";
      if (aspectRatio > 1) {
        videoAspectRatio = "16:9"; // Landscape source → landscape video
        console.log(`   Source is landscape (${dimensions.width}x${dimensions.height}) → using 16:9`);
      } else {
        videoAspectRatio = "9:16"; // Portrait source → portrait video
        console.log(`   Source is portrait (${dimensions.width}x${dimensions.height}) → using 9:16`);
      }

      console.log("   Generating video from center image");

      let operation = await ai.models.generateVideos({
        model: "veo-3.0-generate-001",
        prompt: prompt,
        image: {
          imageBytes: imageBase64,
          mimeType: "image/png",
        },
        config: {
          aspectRatio: videoAspectRatio, // Match source image
          resolution: "720p",
          personGeneration: "allow_adult",
          negativePrompt: "cartoon, drawing, low quality, distorted face, blurry",
        },
      });

      // ========================================
      // STEP 3: Poll until video is ready
      // ========================================
      console.log("⏳ Step 3/5: Waiting for Veo 3 to complete generation...");
      while (!operation.done) {
        pollCount++;
        console.log(`   Polling... (${pollCount} - ${Math.floor((Date.now() - step2Start) / 1000)}s elapsed)`);
        await new Promise((resolve) => setTimeout(resolve, 10000)); // Poll every 10 seconds
        operation = await ai.operations.getVideosOperation({
          operation: operation,
        });
      }

      console.log(`✅ Video generated! (${Date.now() - step2Start}ms, ${pollCount} polls)`);

      // ========================================
      // DEBUG: Inspect operation response
      // ========================================
      console.log("🔍 DEBUG: Operation response structure:");
      console.log("  - operation.done:", operation.done);
      console.log("  - operation.response keys:", operation.response ? Object.keys(operation.response) : "null/undefined");
      
      if (operation.response?.generatedVideos) {
        console.log("  - generatedVideos length:", operation.response.generatedVideos.length);
        console.log("  - generatedVideos[0] keys:", operation.response.generatedVideos[0] ? Object.keys(operation.response.generatedVideos[0]) : "null/undefined");
      } else {
        console.log("  - generatedVideos: MISSING!");
        console.log("  - Full response:", JSON.stringify(operation.response, null, 2));
      }

      // Verify we have the video in the response
      if (!operation.response?.generatedVideos?.[0]?.video) {
        console.log("⚠️ Video not in response, refetching operation...");
        operation = await ai.operations.getVideosOperation({
          operation: operation,
        });
        
        console.log("🔍 After refetch - response keys:", operation.response ? Object.keys(operation.response) : "null/undefined");
        
        if (!operation.response?.generatedVideos?.[0]?.video) {
          console.error("❌ Video still not available after refetch");
          console.error("Full response:", JSON.stringify(operation.response, null, 2));
          throw new Error("Video was generated but not available in response. Check logs above for response structure.");
        }
      }

      // ========================================
      // STEP 4: Download video from Veo 3
      // ========================================
      console.log("⬇️ Step 4/5: Downloading video from Veo 3...");
      const step4Start = Date.now();

      await ai.files.download({
        file: operation.response.generatedVideos[0].video,
        downloadPath: veoVideoPath,
      });

      // Poll for file to appear on disk AND stabilize
      console.log("   Waiting for file download to complete...");
      let stats;
      let previousSize = 0;
      let stableCount = 0;
      const maxRetries = 30; // 30 retries
      const retryDelay = 500; // 500ms between retries
      const requiredStableChecks = 3; // File size must be stable for 3 consecutive checks

      for (let i = 0; i < maxRetries; i++) {
        try {
          stats = await fs.stat(veoVideoPath);
          
          if (stats.size > 0) {
            // Check if size has stabilized
            if (stats.size === previousSize) {
              stableCount++;
              console.log(`   File size stable: ${(stats.size / 1024 / 1024).toFixed(2)} MB (${stableCount}/${requiredStableChecks})`);
              
              if (stableCount >= requiredStableChecks) {
                console.log("   ✅ Download complete - file size stabilized");
                break; // File is stable!
              }
            } else {
              // Size changed - reset stability counter
              console.log(`   Downloading... ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
              stableCount = 0;
              previousSize = stats.size;
            }
          }
        } catch (error: any) {
          if (error.code !== 'ENOENT') {
            throw error; // Unexpected error, re-throw
          }
          console.log(`   File not created yet... (attempt ${i + 1}/${maxRetries})`);
        }
        
        if (i === maxRetries - 1) {
          throw new Error(`Video file did not stabilize after ${(maxRetries * retryDelay) / 1000}s: ${veoVideoPath}`);
        }
        
        await new Promise(resolve => setTimeout(resolve, retryDelay));
      }

      // Extra safety: wait a bit more to ensure OS has flushed buffers
      console.log("   Waiting for OS buffer flush...");
      await new Promise(resolve => setTimeout(resolve, 1000));

      console.log(`✅ Video downloaded: ${(stats!.size / 1024 / 1024).toFixed(2)} MB (${Date.now() - step4Start}ms)`);
      
      step2Time = Date.now() - step2Start;
    }

    // ========================================
    // STEP 5: Swap Audio (Speech-to-Speech)
    // ========================================
    console.log("🔊 Step 5/5: Swapping audio with cloned voice...");
    const step5Start = Date.now();

    await swapAudioWithVoice(
      veoVideoPath,
      voiceId,
      finalVideoPath,
      process.env.ELEVENLABS_API_KEY!,
      tempDir
    );

    console.log(`✅ Audio swapped! (${Date.now() - step5Start}ms)`);

    // ========================================
    // Save final output
    // ========================================
    const outputDir = path.join(process.cwd(), "test-data");
    await fs.mkdir(outputDir, { recursive: true });
    const outputPath = path.join(outputDir, `generated-video-${timestamp}.mp4`);
    await fs.copyFile(finalVideoPath, outputPath);

    // Cleanup temp files (DISABLED for debugging - compare original vs swapped)
    console.log("🧹 Skipping cleanup - keeping temp files for comparison");
    console.log("   Original Veo video:", veoVideoPath);
    console.log("   Final swapped video:", outputPath);
    // const filesToDelete = [
    //   voiceAudioPath,
    //   veoVideoPath,
    //   finalVideoPath,
    // ];
    // 
    // if (centerImagePath) {
    //   filesToDelete.push(centerImagePath);
    // }
    // 
    // await Promise.all(filesToDelete.map(f => fs.unlink(f)));

    const totalTime = Date.now() - startTime;
    console.log(`🎉 SUCCESS! Total pipeline time: ${Math.floor(totalTime / 1000)}s`);

    // Return relative path from public directory
    const relativePath = `generated/generated-video-${timestamp}.mp4`;
    
    return NextResponse.json({
      success: true,
      outputPath: relativePath,
      voiceId: voiceId,
      stats: {
        totalTimeMs: totalTime,
        voiceTrainingMs: Date.now() - step1Start,
        veoGenerationMs: step2Time,
        audioSwapMs: Date.now() - step5Start,
        pollCount: pollCount,
        skippedVeo3: !!videoFile,
      },
      message: `Video generated successfully!`,
    });
  } catch (error: any) {
    console.error("❌ Pipeline error:", error);
    return NextResponse.json(
      { error: error.message || "Failed to generate video" },
      { status: 500 }
    );
  }
}
