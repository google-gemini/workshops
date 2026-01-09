
import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const STORAGE_FILE = path.join(process.cwd(), 'data', 'storage.json');

// Helper to ensure data directory exists
function ensureDirectory() {
    const dir = path.dirname(STORAGE_FILE);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}

export async function GET() {
    try {
        if (!fs.existsSync(STORAGE_FILE)) {
            return NextResponse.json({});
        }
        const content = fs.readFileSync(STORAGE_FILE, 'utf-8');
        const data = JSON.parse(content);
        return NextResponse.json(data);
    } catch (error) {
        console.error('Failed to read storage:', error);
        return NextResponse.json({ error: 'Failed to read storage' }, { status: 500 });
    }
}

export async function POST(req: NextRequest) {
    try {
        const changes = await req.json();

        ensureDirectory();

        // Read existing data
        let currentData = {};
        if (fs.existsSync(STORAGE_FILE)) {
            try {
                const content = fs.readFileSync(STORAGE_FILE, 'utf-8');
                currentData = JSON.parse(content);
            } catch (e) {
                // Ignore parse errors, start fresh
            }
        }

        // Merge changes
        const newData = { ...currentData, ...changes };

        // Write back
        fs.writeFileSync(STORAGE_FILE, JSON.stringify(newData, null, 2));

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error('Failed to write storage:', error);
        return NextResponse.json({ error: 'Failed to write storage' }, { status: 500 });
    }
}
