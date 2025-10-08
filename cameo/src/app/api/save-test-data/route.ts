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

import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const { images, audio } = await request.json();
    
    // Create test-data directory if it doesn't exist
    const testDataDir = path.join(process.cwd(), 'test-data');
    await fs.mkdir(testDataDir, { recursive: true });
    
    const savedFiles: string[] = [];
    
    // Save images (base64 → PNG)
    for (const [zone, base64Image] of Object.entries(images)) {
      if (base64Image) {
        // Remove data:image/png;base64, prefix
        const base64Data = (base64Image as string).replace(/^data:image\/\w+;base64,/, '');
        const buffer = Buffer.from(base64Data, 'base64');
        
        const filename = `test-${zone}.png`;
        const filepath = path.join(testDataDir, filename);
        await fs.writeFile(filepath, buffer);
        savedFiles.push(filename);
        console.log(`✅ Saved: ${filepath}`);
      }
    }
    
    // Save audio (base64 Blob → WebM)
    if (audio) {
      // Audio comes as base64 from Blob
      const base64Data = (audio as string).replace(/^data:audio\/\w+;base64,/, '');
      const buffer = Buffer.from(base64Data, 'base64');
      
      const filename = 'test-audio.webm';
      const filepath = path.join(testDataDir, filename);
      await fs.writeFile(filepath, buffer);
      savedFiles.push(filename);
      console.log(`✅ Saved: ${filepath}`);
    }
    
    // Save metadata for reference
    const metadata = {
      savedAt: new Date().toISOString(),
      imageCount: Object.values(images).filter(Boolean).length,
      audioSize: audio ? Buffer.byteLength((audio as string).replace(/^data:audio\/\w+;base64,/, ''), 'base64') : 0,
      audioFormat: 'webm',
      files: savedFiles,
    };
    
    const metadataFilename = 'metadata.json';
    await fs.writeFile(
      path.join(testDataDir, metadataFilename),
      JSON.stringify(metadata, null, 2)
    );
    savedFiles.push(metadataFilename);
    
    return NextResponse.json({
      success: true,
      message: 'Test data saved successfully',
      savedAt: metadata.savedAt,
      files: savedFiles,
      location: testDataDir,
    });
    
  } catch (error) {
    console.error('Error saving test data:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to save test data', 
        details: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
}
