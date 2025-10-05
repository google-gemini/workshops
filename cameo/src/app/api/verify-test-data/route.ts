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
