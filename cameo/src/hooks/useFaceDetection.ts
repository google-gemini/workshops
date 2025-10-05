'use client';

import { useEffect, useRef, useState } from 'react';
import { initializeFaceMesh, calculateYaw } from '@/lib/mediapipe';

export type CapturedImages = {
  left: string | null;
  center: string | null;
  right: string | null;
};

type FaceZone = 'left' | 'center' | 'right' | null;

type StabilityState = {
  zone: FaceZone;
  startTime: number | null;
};

export function useFaceDetection() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [yaw, setYaw] = useState<number>(0);
  const [isReady, setIsReady] = useState(false);
  
  // Captured images state
  const [capturedImages, setCapturedImages] = useState<CapturedImages>({
    left: null,
    center: null,
    right: null,
  });
  
  // Stability tracking
  const [stability, setStability] = useState<StabilityState>({
    zone: null,
    startTime: null,
  });
  
  // Current zone based on yaw
  const [currentZone, setCurrentZone] = useState<FaceZone>(null);
  
  // Countdown for UI feedback
  const [countdown, setCountdown] = useState<number | null>(null);
  
  // Cooldown to prevent immediate recapture
  const [lastCaptureTime, setLastCaptureTime] = useState<number>(0);
  const [justCaptured, setJustCaptured] = useState<FaceZone>(null);
  
  const COOLDOWN_MS = 1500; // 1.5 second cooldown after capture

  // Capture image from canvas
  const captureImage = (zone: FaceZone) => {
    if (!zone || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const dataUrl = canvas.toDataURL('image/png');
    
    setCapturedImages(prev => ({
      ...prev,
      [zone]: dataUrl,
    }));
    
    // Set cooldown
    setLastCaptureTime(Date.now());
    setJustCaptured(zone);
    
    // Reset stability after capture
    setStability({ zone: null, startTime: null });
    setCountdown(null);
    
    // Clear "just captured" indicator after animation
    setTimeout(() => setJustCaptured(null), 800);
  };
  
  // Reset all captures
  const resetCaptures = () => {
    setCapturedImages({
      left: null,
      center: null,
      right: null,
    });
    setStability({ zone: null, startTime: null });
    setCountdown(null);
    setLastCaptureTime(0);
    setJustCaptured(null);
  };

  // Determine zone from yaw angle
  const getZoneFromYaw = (yawAngle: number): FaceZone => {
    if (yawAngle < -15) return 'left';
    if (yawAngle > 15) return 'right';
    if (Math.abs(yawAngle) < 10) return 'center';
    return null;
  };

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
          
          // Determine current zone
          const zone = getZoneFromYaw(yawAngle);
          setCurrentZone(zone);

          // Clean capture - no visualization overlay for Veo 3
        } else {
          // No face detected
          setCurrentZone(null);
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

  // Stability detection and auto-capture
  useEffect(() => {
    if (!isReady || !currentZone) {
      setStability({ zone: null, startTime: null });
      setCountdown(null);
      return;
    }
    
    // Check cooldown period
    const timeSinceLastCapture = Date.now() - lastCaptureTime;
    if (timeSinceLastCapture < COOLDOWN_MS) {
      // Still in cooldown, don't start timer
      setStability({ zone: null, startTime: null });
      setCountdown(null);
      return;
    }

    // Check if zone changed
    if (currentZone !== stability.zone) {
      // Zone changed, restart timer
      setStability({
        zone: currentZone,
        startTime: Date.now(),
      });
      setCountdown(null);
      return;
    }

    // Same zone, check elapsed time
    if (stability.startTime) {
      const checkStability = () => {
        const elapsed = Date.now() - stability.startTime!;
        const remaining = Math.max(0, 2500 - elapsed);
        
        if (remaining > 0) {
          setCountdown(Math.ceil(remaining / 1000));
        } else {
          // Stable for 2.5 seconds, capture!
          captureImage(currentZone);
        }
      };

      // Check immediately
      checkStability();

      // Set up interval to update countdown
      const interval = setInterval(checkStability, 100);
      
      return () => clearInterval(interval);
    }
  }, [currentZone, stability.zone, stability.startTime, isReady, lastCaptureTime]);

  return {
    videoRef,
    canvasRef,
    yaw,
    isReady,
    capturedImages,
    currentZone,
    countdown,
    justCaptured,
    resetCaptures,
  };
}
