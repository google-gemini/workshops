'use client';

import { useState } from 'react';
import { FaceCapture } from '@/components/FaceCapture';
import { VoiceRecording } from '@/components/VoiceRecording';
import { CapturedImages } from '@/hooks/useFaceDetection';

type Step = 'capture' | 'voice' | 'generate';

export default function Home() {
  const [currentStep, setCurrentStep] = useState<Step>('capture');
  const [capturedImages, setCapturedImages] = useState<CapturedImages | null>(null);
  const [voiceRecording, setVoiceRecording] = useState<Blob | null>(null);

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
            <h1 className="text-3xl font-bold">Generate Video</h1>
            <p className="text-gray-600">Coming soon: Veo 3 integration</p>
            
            {/* Preview assets */}
            <div className="w-full max-w-4xl space-y-6">
              <div>
                <h3 className="font-semibold mb-2">Captured Images:</h3>
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
                <h3 className="font-semibold mb-2">Voice Recording:</h3>
                <audio 
                  controls 
                  src={URL.createObjectURL(voiceRecording)}
                  className="w-full"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
