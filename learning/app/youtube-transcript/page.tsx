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

'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function YouTubeTranscriptPage() {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [result, setResult] = useState<{ videoId: string; outputPath: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    setError('');
    setStatus('Step 1/4: Downloading video...');
    setResult(null);

    try {
      const response = await fetch('/api/youtube/transcript', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: youtubeUrl }),
      });

      // Update status while waiting
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process video');
      }

      setStatus('Step 2/4: Extracting audio...');
      
      const data = await response.json();
      
      if (data.status) {
        setStatus(data.status);
      } else {
        setStatus('Step 3/4: Transcribing with Whisper...');
      }
      
      setResult(data);
      setStatus('✅ Complete!');
    } catch (err: any) {
      setError(err.message || 'An error occurred');
      setStatus('');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
            YouTube Transcript to Markdown
          </h1>
          <p className="text-slate-600">
            Convert YouTube video transcripts to structured markdown format
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Enter YouTube URL</CardTitle>
            <CardDescription>
              Paste a YouTube video URL to extract and format its transcript
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="url" className="block text-sm font-medium mb-2">
                  YouTube URL
                </label>
                <input
                  id="url"
                  type="text"
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                  disabled={isProcessing}
                  className="w-full px-4 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                  required
                />
              </div>

              <Button
                type="submit"
                disabled={isProcessing || !youtubeUrl.trim()}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {isProcessing ? 'Processing...' : 'Process Video'}
              </Button>
            </form>

            {status && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-sm text-blue-700">{status}</p>
              </div>
            )}

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-700 whitespace-pre-line">{error}</p>
              </div>
            )}

            {result && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
                <p className="text-sm font-semibold text-green-800 mb-2">✅ Success!</p>
                <p className="text-sm text-green-700 mb-2">
                  Transcript saved to: <code className="bg-green-100 px-2 py-1 rounded">{result.outputPath}</code>
                </p>
                <p className="text-xs text-green-600 mt-2">
                  Next steps: Use <code className="bg-green-100 px-1 rounded">chunk-paip.ts</code> to process the markdown file.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg">How it works</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-slate-600 space-y-2">
            <p>1. Fetches transcript directly from YouTube (uses <code className="bg-slate-100 px-1 rounded">youtube-transcript</code> package)</p>
            <p>2. Formats transcript as markdown using <strong>Gemini API</strong> (matches learning module format)</p>
            <p>3. Saves to <code className="bg-slate-100 px-1 rounded">youtube/&#123;videoId&#125;/transcript.md</code></p>
            <p>4. Ready for semantic chunking with <code className="bg-slate-100 px-1 rounded">chunk-paip.ts</code></p>
            <p className="mt-3 pt-3 border-t border-slate-200 text-xs text-slate-500">
              💡 <strong>Note:</strong> Works with any video that has captions/subtitles. No downloads needed!
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
