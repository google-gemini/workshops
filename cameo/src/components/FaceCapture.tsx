'use client';

import { useFaceDetection } from '@/hooks/useFaceDetection';

export function FaceCapture() {
  const { videoRef, canvasRef, yaw, isReady } = useFaceDetection();

  return (
    <div className="flex flex-col items-center gap-4 p-8">
      <h1 className="text-3xl font-bold">Face Detection Test</h1>
      
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
      </div>

      {/* Yaw angle display */}
      <div className="text-xl font-mono">
        {isReady ? (
          <>
            Yaw: <span className="font-bold">{yaw.toFixed(1)}°</span>
            {yaw < -15 && ' (Left)'}
            {yaw > 15 && ' (Right)'}
            {yaw >= -15 && yaw <= 15 && ' (Center)'}
          </>
        ) : (
          'Loading camera...'
        )}
      </div>
    </div>
  );
}
