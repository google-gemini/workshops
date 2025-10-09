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

export async function initializeFaceMesh(
  onResults: (results: any) => void
) {
  // Dynamic import - only loads on client
  const { FaceMesh } = await import('@mediapipe/face_mesh');
  
  const faceMesh = new FaceMesh({
    locateFile: (file) => {
      return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
    },
  });

  faceMesh.setOptions({
    maxNumFaces: 1,
    refineLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
  });

  faceMesh.onResults(onResults);

  return faceMesh;
}

// Calculate yaw angle from face landmarks
export function calculateYaw(landmarks: any[]): number {
  if (!landmarks || landmarks.length < 468) return 0;

  const leftEye = landmarks[33];
  const rightEye = landmarks[263];
  const nose = landmarks[1];

  const leftDist = nose.x - leftEye.x;
  const rightDist = rightEye.x - nose.x;

  const yaw = Math.atan2(rightDist - leftDist, rightDist + leftDist) * (180 / Math.PI);

  return yaw;
}
