# Context Re-establishment Document for Cameo Clone Project

## Project Overview
Building a browser-based application to replicate Sora's Cameo feature - creating personalized videos with cloned voices using:
- **Veo 3** for video generation with reference photos
- **ElevenLabs IVC** for voice cloning from ~10 seconds of audio
- **ElevenLabs Voice Changer** for applying cloned voice to video
- **Gemini Live** for orchestrating the capture workflow

## Technical Stack Decision: **Full TypeScript (Next.js)**

### Architecture
```
Frontend (Browser):
- MediaPipe Face Mesh for real-time face direction detection
- Web APIs for camera/microphone capture
- Gemini Live for user guidance & orchestration
- React/Next.js with ShadCN UI components

Backend (Next.js API Routes):
- Secure API key management
- ElevenLabs API calls (voice cloning + voice changer)
- Veo 3 API calls (video generation)
- FFmpeg for video/audio merging
```

## Workflow
1. **Capture 3 face photos** (forward, left, right) - guided by MediaPipe detecting face direction
2. **Record 10 seconds of voice** for cloning
3. **Backend processes:**
   - Train ElevenLabs IVC → get `voice_id`
   - Generate Veo 3 video with reference photos → get `video_url`
   - Extract audio from generated video
   - Apply Voice Changer (with cloned voice) to video audio
   - Merge modified audio back with video using FFmpeg
4. **Return final video** to user

## Key Technical Decisions

### Why Browser-Based (Not Python)
- Zero installation barrier for users
- Native camera/mic access via Web APIs
- MediaPipe has official JavaScript/WASM support
- Gemini Live designed for web apps
- Easy deployment (Vercel)

### Why Next.js + ShadCN
- Single framework for frontend + backend
- File-based routing, built-in API routes
- TypeScript end-to-end
- Rapid prototyping with ShadCN copy-paste components
- Similar developer experience to Streamlit (which you normally use)

### Why MediaPipe (Not YOLO/Roboflow)
- Specifically designed for head pose estimation
- Lightweight, runs in browser at ~30fps
- Official Google support, well-maintained
- More appropriate than YOLO for this use case

## Current Status
Just completed architecture discussion and were **about to scaffold the Next.js project** with:
- ✅ TypeScript setup
- ✅ Tailwind CSS
- ✅ ShadCN UI components
- ✅ API routes structure
- ✅ MediaPipe integration
- ✅ Zustand for state management

## Files/Structure Discussed

```
cameo-clone/
├── src/
│   ├── app/
│   │   ├── page.tsx                    # Main capture UI
│   │   └── api/
│   │       ├── clone-voice/route.ts
│   │       ├── generate-video/route.ts
│   │       ├── change-voice/route.ts
│   │       └── merge-video/route.ts
│   ├── components/
│   │   ├── CameraCapture.tsx
│   │   ├── AudioRecorder.tsx
│   │   └── VideoPlayer.tsx
│   ├── hooks/
│   │   └── useFaceDetection.ts
│   ├── lib/
│   │   └── mediapipe.ts
│   └── store/
│       └── captureStore.ts
└── .env.local
```

## Next Steps
1. Run the scaffolding commands to create project
2. Install dependencies (MediaPipe, ElevenLabs SDK, Google AI SDK, FFmpeg)
3. Implement face detection with MediaPipe
4. Build camera capture component
5. Create audio recording component
6. Wire up backend API routes
7. Test end-to-end workflow

## Important Notes
- User typically builds in Python but acknowledged browser is better for this use case
- User has never done end-to-end TypeScript project before
- User normally uses Streamlit for rapid prototyping
- Face detection should auto-capture when user holds stable position
- Gemini Live handles orchestration/prompting (no need for CrewAI/complex agents)
- All heavy lifting done by external APIs (ElevenLabs, Veo 3, Gemini)

## Environment Variables Needed
```bash
ELEVENLABS_API_KEY=
GOOGLE_AI_API_KEY=
NEXT_PUBLIC_GEMINI_API_KEY=
```

## Dependencies to Install
```bash
npm install @mediapipe/face_mesh @mediapipe/camera_utils
npm install @google/generative-ai
npm install elevenlabs
npm install fluent-ffmpeg @types/fluent-ffmpeg
npm install zustand
```

## Key Conversation Points
- Started by outlining the workflow (7 steps)
- Discussed whether to use Python vs browser → decided browser
- Explored Gemini Live as orchestrator with tool calling
- Compared face detection options (MediaPipe won)
- Discussed state management and UI frameworks
- User asked about TypeScript backend options
- Settled on Next.js as "Streamlit for TypeScript"
- About to scaffold when user switched to local development

**Current goal:** Get the Next.js scaffold running with camera capture and MediaPipe face detection working, then build out the API routes for the processing pipeline.
