'use client';

import { useEffect, useRef, useState } from 'react';
import { initializeFaceMesh, calculateYaw } from '@/lib/mediapipe';

export function useFaceDetection() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [yaw, setYaw] = useState<number>(0);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    let faceMesh: any;
    let camera: any;

    // Initialize async
    (async () => {
      // Import Camera dynamically
      const { Camera } = await import('@mediapipe/camera_utils');

      // Initialize MediaPipe Face Mesh
      faceMesh = await initializeFaceMesh((results) => {
        if (!ctx) return;

        ctx.save();
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

        if (results.multiFaceLandmarks && results.multiFaceLandmarks[0]) {
          const landmarks = results.multiFaceLandmarks[0];
          const yawAngle = calculateYaw(landmarks);
          setYaw(yawAngle);

          ctx.fillStyle = 'rgba(0, 255, 0, 0.5)';
          landmarks.forEach((landmark: any) => {
            ctx.beginPath();
            ctx.arc(
              landmark.x * canvas.width,
              landmark.y * canvas.height,
              2,
              0,
              2 * Math.PI
            );
            ctx.fill();
          });
        }

        ctx.restore();
      });

      // Initialize camera
      camera = new Camera(video, {
        onFrame: async () => {
          if (video.readyState === 4) {
            await faceMesh.send({ image: video });
          }
        },
        width: 640,
        height: 480,
      });

      await camera.start();
      setIsReady(true);
    })();

    return () => {
      if (camera) camera.stop();
      if (faceMesh) faceMesh.close();
    };
  }, []);

  return {
    videoRef,
    canvasRef,
    yaw,
    isReady,
  };
}
