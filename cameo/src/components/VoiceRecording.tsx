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

import { useVoiceRecording } from '@/hooks/useVoiceRecording';
import { CapturedImages } from '@/hooks/useFaceDetection';

type VoiceRecordingProps = {
  capturedImages: CapturedImages;
  onComplete: (audio: Blob) => void;
};

export function VoiceRecording({ capturedImages, onComplete }: VoiceRecordingProps) {
  const {
    state,
    timeRemaining,
    audioBlob,
    audioURL,
    startRecording,
    stopRecording,
    resetRecording,
  } = useVoiceRecording(10000);

  return (
    <div className="flex flex-col items-center gap-6 p-8">
      <h1 className="text-3xl font-bold">Voice Recording</h1>

      {/* Preview captured images */}
      <div className="w-full max-w-3xl">
        <h2 className="text-lg font-semibold mb-3">Your Captured Photos</h2>
        <div className="grid grid-cols-3 gap-4">
          {Object.entries(capturedImages).map(([zone, image]) => (
            image && (
              <div key={zone} className="flex flex-col items-center">
                <div className="text-sm font-medium mb-1 text-gray-600 capitalize">
                  {zone}
                </div>
                <img 
                  src={image} 
                  alt={zone}
                  className="w-full rounded-lg border-2 border-gray-300"
                />
              </div>
            )
          ))}
        </div>
      </div>

      {/* Recording interface */}
      <div className="w-full max-w-2xl mt-8">
        <div className="bg-white rounded-2xl shadow-lg p-8 space-y-6">
          <div className="text-center">
            <h3 className="text-xl font-semibold mb-2">Record Your Message</h3>
            <p className="text-gray-600">
              Record a 10-second voice clip that will be used for your video
            </p>
          </div>

          {/* Recording status */}
          {state === 'idle' && (
            <div className="flex flex-col items-center gap-4 py-8">
              <div className="w-32 h-32 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center cursor-pointer transition-all shadow-lg hover:shadow-xl"
                onClick={startRecording}>
                <svg className="w-16 h-16 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                  <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
              </div>
              <p className="text-lg font-medium text-gray-700">Click to start recording</p>
            </div>
          )}

          {state === 'recording' && (
            <div className="flex flex-col items-center gap-4 py-8">
              <div className="w-32 h-32 rounded-full bg-red-500 flex items-center justify-center animate-pulse">
                <svg className="w-16 h-16 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                  <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
              </div>
              <div className="text-center">
                <p className="text-4xl font-bold text-red-500">{timeRemaining}s</p>
                <p className="text-gray-600 mt-2">Recording...</p>
              </div>
              <button
                onClick={stopRecording}
                className="mt-4 px-6 py-3 bg-gray-800 hover:bg-gray-900 text-white rounded-lg font-medium transition-colors"
              >
                Stop Recording
              </button>
            </div>
          )}

          {state === 'completed' && audioURL && (
            <div className="flex flex-col items-center gap-4 py-8">
              <div className="w-32 h-32 rounded-full bg-green-500 flex items-center justify-center">
                <svg className="w-16 h-16 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
              </div>
              <p className="text-lg font-medium text-green-600">Recording complete!</p>
              
              {/* Audio playback */}
              <div className="w-full mt-4">
                <audio 
                  controls 
                  src={audioURL}
                  className="w-full"
                />
              </div>

              {/* Action buttons */}
              <div className="flex gap-4 mt-4">
                <button
                  onClick={resetRecording}
                  className="px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors"
                >
                  Re-record
                </button>
                <button
                  onClick={() => audioBlob && onComplete(audioBlob)}
                  className="px-8 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold transition-colors shadow-lg hover:shadow-xl"
                >
                  Continue to Generate Video →
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Instructions */}
      <div className="text-sm text-gray-600 max-w-2xl text-center">
        Record a personalized message that will be synced with your captured images to create your video.
      </div>
    </div>
  );
}
