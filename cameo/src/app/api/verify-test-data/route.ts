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

import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET() {
  try {
    const testDataDir = path.join(process.cwd(), 'test-data');
    
    // Check if directory exists
    try {
      await fs.access(testDataDir);
    } catch {
      return NextResponse.json({
        exists: false,
        message: 'test-data directory does not exist yet',
        location: testDataDir,
      });
    }
    
    // Read directory contents
    const files = await fs.readdir(testDataDir);
    
    if (files.length === 0) {
      return NextResponse.json({
        exists: true,
        empty: true,
        message: 'test-data directory is empty',
        location: testDataDir,
      });
    }
    
    // Get file stats
    const stats = await Promise.all(
      files.map(async (file) => {
        const filePath = path.join(testDataDir, file);
        const stat = await fs.stat(filePath);
        return {
          name: file,
          size: stat.size,
          sizeKB: (stat.size / 1024).toFixed(2) + ' KB',
          modified: stat.mtime.toISOString(),
        };
      })
    );
    
    return NextResponse.json({
      exists: true,
      empty: false,
      location: testDataDir,
      fileCount: files.length,
      files: stats,
    });
    
  } catch (error) {
    console.error('Error verifying test data:', error);
    return NextResponse.json(
      { 
        error: 'Failed to verify test data',
        details: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
}
