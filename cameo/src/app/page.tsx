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
import { FaceCapture } from '@/components/FaceCapture';
import { VoiceRecording } from '@/components/VoiceRecording';
import { CapturedImages } from '@/hooks/useFaceDetection';

type Step = 'capture' | 'voice' | 'generate';

type GeneratedVideo = {
  url: string;
  voiceId: string;
  stats: any;
};

export default function Home() {
  const [currentStep, setCurrentStep] = useState<Step>('capture');
  const [capturedImages, setCapturedImages] = useState<CapturedImages | null>(null);
  const [voiceRecording, setVoiceRecording] = useState<Blob | null>(null);
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedVideo, setGeneratedVideo] = useState<GeneratedVideo | null>(null);
  const [error, setError] = useState<string | null>(null);

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Progress indicator at top */}
      <div className="sticky top-0 bg-white shadow-sm z-10 py-4 px-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              {/* Step 1 */}
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold ${
                  currentStep === 'capture' 
                    ? 'bg-blue-500 text-white' 
                    : capturedImages 
                    ? 'bg-green-500 text-white' 
                    : 'bg-gray-300 text-gray-600'
                }`}>
                  {capturedImages ? '✓' : '1'}
                </div>
                <span className={`font-medium ${
                  currentStep === 'capture' ? 'text-blue-600' : capturedImages ? 'text-green-600' : 'text-gray-600'
                }`}>
                  Capture Photos
                </span>
              </div>

              {/* Arrow */}
              <div className="text-gray-400">→</div>

              {/* Step 2 */}
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold ${
                  currentStep === 'voice' 
                    ? 'bg-blue-500 text-white' 
                    : voiceRecording 
                    ? 'bg-green-500 text-white' 
                    : 'bg-gray-300 text-gray-600'
                }`}>
                  {voiceRecording ? '✓' : '2'}
                </div>
                <span className={`font-medium ${
                  currentStep === 'voice' ? 'text-blue-600' : voiceRecording ? 'text-green-600' : 'text-gray-600'
                }`}>
                  Record Voice
                </span>
              </div>

              {/* Arrow */}
              <div className="text-gray-400">→</div>

              {/* Step 3 */}
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold ${
                  currentStep === 'generate' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-300 text-gray-600'
                }`}>
                  3
                </div>
                <span className={`font-medium ${
                  currentStep === 'generate' ? 'text-blue-600' : 'text-gray-600'
                }`}>
                  Generate Video
                </span>
              </div>
            </div>

            {/* Back button */}
            {currentStep !== 'capture' && (
              <button
                onClick={() => {
                  if (currentStep === 'voice') setCurrentStep('capture');
                  if (currentStep === 'generate') setCurrentStep('voice');
                }}
                className="text-sm text-gray-600 hover:text-gray-900 font-medium"
              >
                ← Back
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Step content */}
      <div className="pt-4">
        {currentStep === 'capture' && (
          <FaceCapture 
            onComplete={(images) => {
              setCapturedImages(images);
              setCurrentStep('voice');
            }}
          />
        )}
        
        {currentStep === 'voice' && capturedImages && (
          <VoiceRecording 
            capturedImages={capturedImages}
            onComplete={(audio) => {
              setVoiceRecording(audio);
              setCurrentStep('generate');
            }}
          />
        )}
        
        {currentStep === 'generate' && capturedImages && voiceRecording && (
          <div className="flex flex-col items-center gap-6 p-8">
            <h1 className="text-3xl font-bold">🎬 Generate Your Video</h1>
            
            {!generatedVideo && (
              <>
                {/* Prompt Input */}
                <div className="w-full max-w-2xl">
                  <label className="block text-lg font-semibold mb-2">Video Prompt</label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    disabled={isGenerating}
                    className="w-full p-4 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none text-base"
                    rows={5}
                    placeholder="Example: I'm a medieval knight delivering an inspiring speech to my troops before battle. I speak with passion and determination, gesturing dramatically with my sword."
                  />
                  <p className="text-sm text-gray-600 mt-2">
                    💡 <strong>Tip:</strong> Describe the scene, dialogue, emotions, and gestures. Be specific and vivid!
                  </p>
                </div>

                {/* Generate Button */}
                <button
                  onClick={async () => {
                    if (!prompt.trim()) {
                      alert('Please enter a prompt!');
                      return;
                    }
                    
                    setIsGenerating(true);
                    setError(null);
                    
                    try {
                      // Convert base64 images to Blobs
                      const centerBlob = await fetch(capturedImages.center!).then(r => r.blob());
                      
                      const formData = new FormData();
                      formData.append('centerImage', centerBlob, 'center.png');
                      formData.append('voiceAudio', voiceRecording!, 'voice.webm');
                      formData.append('voiceName', 'My Voice Clone');
                      formData.append('prompt', prompt);

                      console.log('🎬 Starting video generation...');
                      
                      const response = await fetch('/api/generate-video', {
                        method: 'POST',
                        body: formData,
                      });

                      if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.error || 'Video generation failed');
                      }

                      const data = await response.json();
                      console.log('✅ Video generated!', data);
                      
                      setGeneratedVideo({
                        url: `/${data.outputPath}`,
                        voiceId: data.voiceId,
                        stats: data.stats,
                      });
                    } catch (err) {
                      console.error('Generation error:', err);
                      setError(err instanceof Error ? err.message : 'Unknown error occurred');
                    } finally {
                      setIsGenerating(false);
                    }
                  }}
                  disabled={isGenerating || !prompt.trim()}
                  className="px-8 py-4 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded-lg text-lg font-bold shadow-lg hover:shadow-xl transition-all disabled:cursor-not-allowed"
                >
                  {isGenerating ? '⏳ Generating...' : '🎬 Generate Video'}
                </button>

                {/* Error Display */}
                {error && (
                  <div className="w-full max-w-2xl bg-red-50 border-2 border-red-300 rounded-xl p-6">
                    <h3 className="font-semibold text-red-900 mb-2">❌ Error</h3>
                    <p className="text-red-800">{error}</p>
                  </div>
                )}

                {/* Loading State */}
                {isGenerating && (
                  <div className="w-full max-w-2xl bg-blue-50 border-2 border-blue-300 rounded-xl p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="animate-spin rounded-full h-10 w-10 border-4 border-blue-600 border-t-transparent"></div>
                      <div>
                        <p className="text-lg font-semibold text-blue-900">Creating your video...</p>
                        <p className="text-sm text-blue-700">This takes 1-2 minutes. Hang tight! 🚀</p>
                      </div>
                    </div>
                    <div className="space-y-2 text-sm text-blue-800">
                      <p>🎤 Training voice model with ElevenLabs...</p>
                      <p>🎨 Generating video with Veo 3...</p>
                      <p>🔊 Syncing audio to video...</p>
                    </div>
                  </div>
                )}

                {/* Preview assets (collapsed) */}
                {!isGenerating && (
                  <details className="w-full max-w-4xl">
                    <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-900 font-medium">
                      👀 Show captured images and voice recording
                    </summary>
                    <div className="mt-4 space-y-6">
                      <div>
                        <h3 className="font-semibold mb-2 text-sm">Captured Images:</h3>
                        <div className="grid grid-cols-3 gap-4">
                          {Object.entries(capturedImages).map(([zone, image]) => (
                            image && (
                              <img 
                                key={zone}
                                src={image} 
                                alt={zone}
                                className="w-full rounded-lg border-2 border-gray-300"
                              />
                            )
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <h3 className="font-semibold mb-2 text-sm">Voice Recording:</h3>
                        <audio 
                          controls 
                          src={URL.createObjectURL(voiceRecording)}
                          className="w-full"
                        />
                      </div>
                    </div>
                  </details>
                )}
              </>
            )}

            {/* Video Display */}
            {generatedVideo && (
              <div className="w-full max-w-3xl space-y-6">
                <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white p-6 rounded-xl text-center">
                  <h2 className="text-2xl font-bold mb-2">🎉 Your Video is Ready!</h2>
                  <p className="text-purple-100">Generation time: {(generatedVideo.stats.totalTimeMs / 1000).toFixed(1)}s</p>
                </div>
                
                <video
                  controls
                  autoPlay
                  src={generatedVideo.url}
                  className="w-full rounded-xl shadow-2xl border-4 border-purple-500"
                />
                
                <div className="grid grid-cols-2 gap-4">
                  <a
                    href={generatedVideo.url}
                    download
                    className="px-6 py-4 bg-green-600 hover:bg-green-700 text-white rounded-lg text-center font-bold shadow-lg hover:shadow-xl transition-all"
                  >
                    📥 Download Video
                  </a>
                  <button
                    onClick={() => {
                      setGeneratedVideo(null);
                      setPrompt('');
                      setError(null);
                    }}
                    className="px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold shadow-lg hover:shadow-xl transition-all"
                  >
                    🔄 Generate Another
                  </button>
                </div>

                {/* Stats */}
                <details className="text-sm text-gray-600">
                  <summary className="cursor-pointer hover:text-gray-900 font-medium">
                    📊 Generation Stats
                  </summary>
                  <div className="mt-2 p-4 bg-gray-50 rounded-lg space-y-1">
                    <p>Voice Training: {(generatedVideo.stats.voiceTrainingMs / 1000).toFixed(1)}s</p>
                    <p>Veo 3 Generation: {(generatedVideo.stats.veoGenerationMs / 1000).toFixed(1)}s</p>
                    <p>Audio Swap: {(generatedVideo.stats.audioSwapMs / 1000).toFixed(1)}s</p>
                    <p>Voice ID: <code className="bg-gray-200 px-1 rounded">{generatedVideo.voiceId}</code></p>
                  </div>
                </details>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
