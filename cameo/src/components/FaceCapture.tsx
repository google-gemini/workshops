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

import { useFaceDetection, CapturedImages } from '@/hooks/useFaceDetection';

type FaceCaptureProps = {
  onComplete: (images: CapturedImages) => void;
};

export function FaceCapture({ onComplete }: FaceCaptureProps) {
  const { 
    videoRef, 
    canvasRef, 
    yaw, 
    isReady, 
    capturedImages, 
    currentZone, 
    countdown,
    justCaptured,
    resetCaptures 
  } = useFaceDetection();

  const getZoneName = (zone: string | null) => {
    if (!zone) return 'None';
    return zone.charAt(0).toUpperCase() + zone.slice(1);
  };
  
  const captureCount = Object.values(capturedImages).filter(img => img !== null).length;
  const allCaptured = captureCount === 3;

  return (
    <div className="flex flex-col items-center gap-6 p-8">
      <h1 className="text-3xl font-bold">Face Capture</h1>
      
      {/* Progress indicator */}
      <div className="flex items-center gap-2 text-sm">
        <span className="font-semibold">Progress:</span>
        <div className="flex gap-1">
          {[1, 2, 3].map(i => (
            <div
              key={i}
              className={`w-3 h-3 rounded-full ${
                i <= captureCount ? 'bg-green-500' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
        <span className="text-gray-600">({captureCount}/3)</span>
      </div>
      
      {/* Main canvas for live feed */}
      <div className="relative">
        {/* Hidden video element */}
        <video
          ref={videoRef}
          className="hidden"
          playsInline
        />
        
        {/* Canvas for drawing */}
        <canvas
          ref={canvasRef}
          width={640}
          height={480}
          className="border-2 border-gray-300 rounded-lg"
        />
        
        {/* Countdown overlay */}
        {countdown !== null && currentZone && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="bg-black bg-opacity-70 text-white px-6 py-4 rounded-lg text-2xl font-bold animate-pulse">
              Capturing {getZoneName(currentZone)} in {countdown}s
            </div>
          </div>
        )}
        
        {/* Capture success flash */}
        {justCaptured && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none animate-ping">
            <div className="bg-green-500 bg-opacity-30 text-white px-8 py-6 rounded-lg text-3xl font-bold">
              ✓ {getZoneName(justCaptured)} Captured!
            </div>
          </div>
        )}
        
        {/* All complete indicator */}
        {allCaptured && (
          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-4 py-2 rounded-lg font-semibold shadow-lg">
            ✓ All Photos Captured!
          </div>
        )}
      </div>

      {/* Status display */}
      <div className="text-xl font-mono">
        {isReady ? (
          <>
            Yaw: <span className="font-bold">{yaw.toFixed(1)}°</span>
            {' - '}
            Zone: <span className="font-bold">{getZoneName(currentZone)}</span>
          </>
        ) : (
          'Loading camera...'
        )}
      </div>

      {/* Captured images display */}
      <div className="w-full max-w-4xl">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-semibold">Captured Images</h2>
          {captureCount > 0 && (
            <button
              onClick={resetCaptures}
              className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Reset All
            </button>
          )}
        </div>
        <div className="grid grid-cols-3 gap-4">
          {/* Left */}
          <div className="flex flex-col items-center">
            <div className="text-sm font-medium mb-2 flex items-center gap-2">
              {capturedImages.left && <span className="text-green-500 text-lg">✓</span>}
              Left
            </div>
            <div className={`w-full aspect-[4/3] border-2 rounded-lg overflow-hidden bg-gray-100 transition-all ${
              capturedImages.left 
                ? 'border-green-400 shadow-lg' 
                : currentZone === 'left' 
                ? 'border-blue-400 shadow-md' 
                : 'border-gray-300'
            }`}>
              {capturedImages.left ? (
                <img 
                  src={capturedImages.left} 
                  alt="Left pose" 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  Turn left
                </div>
              )}
            </div>
          </div>

          {/* Center */}
          <div className="flex flex-col items-center">
            <div className="text-sm font-medium mb-2 flex items-center gap-2">
              {capturedImages.center && <span className="text-green-500 text-lg">✓</span>}
              Center
            </div>
            <div className={`w-full aspect-[4/3] border-2 rounded-lg overflow-hidden bg-gray-100 transition-all ${
              capturedImages.center 
                ? 'border-green-400 shadow-lg' 
                : currentZone === 'center' 
                ? 'border-blue-400 shadow-md' 
                : 'border-gray-300'
            }`}>
              {capturedImages.center ? (
                <img 
                  src={capturedImages.center} 
                  alt="Center pose" 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  Face forward
                </div>
              )}
            </div>
          </div>

          {/* Right */}
          <div className="flex flex-col items-center">
            <div className="text-sm font-medium mb-2 flex items-center gap-2">
              {capturedImages.right && <span className="text-green-500 text-lg">✓</span>}
              Right
            </div>
            <div className={`w-full aspect-[4/3] border-2 rounded-lg overflow-hidden bg-gray-100 transition-all ${
              capturedImages.right 
                ? 'border-green-400 shadow-lg' 
                : currentZone === 'right' 
                ? 'border-blue-400 shadow-md' 
                : 'border-gray-300'
            }`}>
              {capturedImages.right ? (
                <img 
                  src={capturedImages.right} 
                  alt="Right pose" 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  Turn right
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Continue button */}
      {allCaptured && (
        <button
          onClick={() => onComplete(capturedImages)}
          className="mt-4 px-8 py-4 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-lg font-semibold transition-colors shadow-lg hover:shadow-xl"
        >
          Continue to Voice Recording →
        </button>
      )}

      {/* Instructions */}
      <div className="text-sm text-gray-600 max-w-2xl text-center">
        Hold your face steady in each position (left, center, right) for 3 seconds to auto-capture.
        You can recapture any position by returning to it.
      </div>
    </div>
  );
}
