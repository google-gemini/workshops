# Cameo Project - Development Notes

## Project Overview
Face detection application using Next.js 15, TypeScript, Tailwind CSS, and MediaPipe Face Mesh.

## Initial Setup Issues

### Problem: Missing Files
After initial project setup, discovered all files were missing from the `cameo` directory:
- Found empty `src/` directory
- No project files present

### Solution: Fresh Next.js Setup
Recreated the project from scratch:

```bash
cd /home/danenberg/prg/workshops
rm -rf cameo
npx create-next-app@latest cameo --typescript --tailwind --eslint
cd cameo
npm install @mediapipe/face_mesh @mediapipe/camera_utils
mkdir -p src/components src/hooks src/lib
```

## Project Structure

Created four main files:

1. **src/app/page.tsx** - Main page component
2. **src/components/FaceCapture.tsx** - Face capture UI component
3. **src/hooks/useFaceDetection.ts** - Custom hook for face detection logic
4. **src/lib/mediapipe.ts** - MediaPipe initialization and utilities

## MediaPipe SSR Issue

### Problem: Module Export Error
Encountered error when running `npm run dev`:

```
Export FaceMesh doesn't exist in target module
Module not found: Can't resolve '@mediapipe/face_mesh'
The module has no exports at all.
```

**Root Cause**: MediaPipe is a client-side only library (uses WebAssembly), but Next.js was trying to run it on the server during Server-Side Rendering (SSR).

### Solution: Dynamic Imports

Changed from static imports to dynamic imports to ensure MediaPipe only loads in the browser.

**Before (mediapipe.ts):**
```typescript
import { FaceMesh } from '@mediapipe/face_mesh';

export function initializeFaceMesh(onResults) {
  const faceMesh = new FaceMesh({...});
  // ...
}
```

**After (mediapipe.ts):**
```typescript
export async function initializeFaceMesh(onResults) {
  // Dynamic import - only loads on client
  const { FaceMesh } = await import('@mediapipe/face_mesh');
  const faceMesh = new FaceMesh({...});
  // ...
}
```

**Before (useFaceDetection.ts):**
```typescript
import { Camera } from '@mediapipe/camera_utils';

useEffect(() => {
  const camera = new Camera(video, {...});
  // ...
}, []);
```

**After (useFaceDetection.ts):**
```typescript
useEffect(() => {
  let faceMesh: any;
  let camera: any;

  (async () => {
    const { Camera } = await import('@mediapipe/camera_utils');
    faceMesh = await initializeFaceMesh(...);
    camera = new Camera(video, {...});
    // ...
  })();
}, []);
```

## Key Technical Details

### Face Detection Features
- Uses MediaPipe Face Mesh with 468 landmark points
- Calculates yaw angle (head rotation left/right)
- Real-time visualization with green dots on face
- 640x480 canvas resolution

### Yaw Calculation
Uses three key landmarks:
- Landmark 33: Left eye outer corner
- Landmark 263: Right eye outer corner  
- Landmark 1: Nose tip

Formula:
```typescript
const leftDist = nose.x - leftEye.x;
const rightDist = rightEye.x - nose.x;
const yaw = Math.atan2(rightDist - leftDist, rightDist + leftDist) * (180 / Math.PI);
```

### MediaPipe Configuration
```typescript
{
  maxNumFaces: 1,
  refineLandmarks: true,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5,
}
```

## Dependencies

### Core Dependencies
- next: 15.5.4
- react: Latest
- typescript: Latest
- tailwindcss: Latest

### MediaPipe Dependencies
- @mediapipe/face_mesh
- @mediapipe/camera_utils

MediaPipe models loaded via CDN:
```typescript
locateFile: (file) => {
  return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
}
```

## Development Commands

### Start Dev Server
```bash
cd cameo
npm run dev
```

Server runs at:
- Local: http://localhost:3000
- Network: http://172.20.10.10:3000

### Install Dependencies
```bash
npm install @mediapipe/face_mesh @mediapipe/camera_utils
```

## Git Configuration

### Files to Track
- `src/` directory (all source code)
- `package.json` and `package-lock.json`
- Configuration files: `tsconfig.json`, `next.config.ts`, etc.
- `public/` directory
- Documentation files

### Files Ignored (via .gitignore)
- `node_modules/` - Generated dependencies
- `.next/` - Next.js build output
- `out/` - Export output
- Build artifacts and temp files

Create-next-app automatically includes a comprehensive .gitignore.

## Current Status

✅ Project successfully created and configured
✅ MediaPipe SSR issue resolved with dynamic imports
✅ Face detection working with real-time yaw calculation
✅ Files staged for git commit

## Next Steps

Potential enhancements:
- Add pitch and roll calculations for full 3D head orientation
- Implement face gesture recognition
- Add recording/screenshot capabilities
- Create different visualization modes
- Add face landmark selection/filtering
- Performance optimization for lower-end devices

## Troubleshooting

### Camera Not Working
1. Check browser permissions (camera access required)
2. Verify browser console for errors (F12)
3. Ensure HTTPS or localhost (camera API requires secure context)

### Build Errors
1. Ensure all dependencies installed: `npm install`
2. Clear Next.js cache: `rm -rf .next`
3. Restart dev server

### Performance Issues
1. Reduce canvas resolution (currently 640x480)
2. Lower MediaPipe confidence thresholds
3. Reduce landmark visualization (draw fewer points)

## Resources

- [MediaPipe Face Mesh Documentation](https://google.github.io/mediapipe/solutions/face_mesh.html)
- [Next.js Documentation](https://nextjs.org/docs)
- [MediaPipe CDN Files](https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/)
