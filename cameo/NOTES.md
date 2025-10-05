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

## Photo Capture Flow

### Goal
Capture three photos: left, right, and center face positions for use in Veo 3 video generation.

### Approach Options

#### Option 1: Simple State Machine (Current Focus)
Build a straightforward state machine with text-based directions:
- State: 'center' | 'left' | 'right' | 'complete'
- Detect face position using yaw angle
- Auto-capture when face is stable in correct position
- Visual feedback showing current requirement

#### Option 2: Gemini Live Integration (Future Enhancement)
Originally considered using Gemini Live for conversational guidance, but deferred due to architecture complexity.

**Key Finding about Google AI Studio:**
When examining the official Gemini Live example from https://aistudio.google.com/apps/bundled/live_audio, noticed:
- Code uses `process.env.GEMINI_API_KEY` but doesn't expose it
- Google AI Studio runs in a **controlled/sandboxed environment**
- The environment injects API keys server-side
- WebSocket connections are proxied through Google's infrastructure
- Not a pure client-side application

**Implementation Options for Gemini Live:**
1. **Client-side with exposed key** (Quick prototype):
   ```typescript
   // .env.local
   NEXT_PUBLIC_GEMINI_API_KEY=your_key_here
   
   // In component
   const client = new GoogleGenAI({
     apiKey: process.env.NEXT_PUBLIC_GEMINI_API_KEY,
   });
   ```
   Works but exposes API key in browser bundle.

2. **Server-side proxy** (Production approach):
   - Create Next.js API route
   - Browser ↔ Next.js API ↔ Gemini API
   - API key stays server-side
   - More secure but adds complexity

**Decision:** Focus on state machine mechanics first. Gemini Live conversational interface is a nice-to-have feature for later.

## Auto-Capture State Machine Implementation

### Status: ✅ Complete and Working!

Successfully implemented a flexible auto-capture system for left, right, and center face shots.

### Core Features Implemented

1. **Zone Detection**
   - Yaw angle thresholds:
     - Left: yaw < -15°
     - Right: yaw > 15°
     - Center: |yaw| < 10°
   - Flexible capture order (no prescribed sequence)

2. **Stability Tracking**
   - Monitors how long face stays in a zone
   - 2.5 second hold required for auto-capture
   - Visual countdown (3, 2, 1) during stabilization
   - Resets when face moves to different zone

3. **Cooldown System**
   - 1.5 second cooldown after each capture
   - Prevents immediate recapture of same zone
   - Reduces "jittery" behavior
   - User can recapture by returning after cooldown

4. **Visual Feedback**
   - Progress indicator: 3 dots showing capture status
   - Counter display: (2/3) shows progress
   - Countdown overlay: "Capturing Center in 2s"
   - Success flash: Animated "✓ Center Captured!" message
   - Completion banner: "✓ All Photos Captured!"
   - Active zone highlighting: Blue border on current zone
   - Captured zone styling: Green border with shadow + checkmark

5. **User Controls**
   - Reset All button: Clear all captures and start over
   - Only appears when at least one photo captured
   - Recapture capability: Return to any zone to retake

### Implementation Details

**State Management:**
```typescript
type CapturedImages = {
  left: string | null;
  center: string | null;
  right: string | null;
};

type StabilityState = {
  zone: FaceZone;
  startTime: number | null;
};
```

**Key Constants:**
- Capture duration: 2500ms (2.5 seconds)
- Cooldown period: 1500ms (1.5 seconds)
- Countdown update interval: 100ms
- Canvas resolution: 640x480

**Capture Process:**
1. Detect current face zone from yaw angle
2. Start stability timer when zone detected
3. Update countdown every 100ms
4. Capture canvas as base64 PNG after 2.5s
5. Apply 1.5s cooldown to prevent immediate recapture
6. Show success animation
7. User can recapture any position by returning to it

### UX Enhancements

**Animations:**
- `animate-pulse`: Countdown overlay pulsing effect
- `animate-ping`: Success flash on capture
- Smooth transitions on border colors
- 800ms "just captured" indicator duration

**Color Coding:**
- Gray: Uncaptured zones (neutral state)
- Blue: Current active zone (where face is pointing)
- Green: Captured zones (complete with checkmark)
- Red: Reset button (clear all)

**Progressive Disclosure:**
- Reset button only shows when needed
- Progress indicators update in real-time
- Completion banner appears when all three captured
- Instructions always visible at bottom

## Multi-Step Workflow Implementation

### Status: ✅ Complete and Working!

Successfully implemented a conditional rendering system for a three-step workflow.

### Architecture Decision: Single Page with Step State

**Chose conditional rendering over separate routes for:**
1. **Data persistence** - All assets (images + audio) stay in memory
2. **Smooth UX** - No page reloads between steps
3. **Simpler state** - Everything in one component hierarchy
4. **Natural flow** - Wizard/checkout-style pattern

### Step Flow Implementation

**Step Types:**
```typescript
type Step = 'capture' | 'voice' | 'generate';
```

**State Management:**
```typescript
const [currentStep, setCurrentStep] = useState<Step>('capture');
const [capturedImages, setCapturedImages] = useState<CapturedImages | null>(null);
const [voiceRecording, setVoiceRecording] = useState<Blob | null>(null);
```

**Conditional Rendering Pattern:**
```typescript
{currentStep === 'capture' && (
  <FaceCapture onComplete={(images) => {
    setCapturedImages(images);
    setCurrentStep('voice');
  }} />
)}

{currentStep === 'voice' && capturedImages && (
  <VoiceRecording onComplete={(audio) => {
    setVoiceRecording(audio);
    setCurrentStep('generate');
  }} />
)}
```

### UI Components

1. **Progress Indicator**
   - Sticky header showing all three steps
   - Visual state: current (blue), completed (green), pending (gray)
   - Checkmarks for completed steps
   - Back button for navigation

2. **Step Transitions**
   - "Continue" buttons appear when step complete
   - Smooth component mounting/unmounting
   - No page reloads or route changes

## Voice Recording Implementation

### Status: ✅ Complete and Working!

Successfully implemented browser-based voice recording with 10-second limit.

### Core Features

1. **MediaRecorder API Integration**
   - Browser native audio recording
   - WebM audio format (widely supported)
   - 10-second maximum duration
   - Auto-stop when time limit reached

2. **Recording States**
   ```typescript
   type RecordingState = 'idle' | 'recording' | 'completed';
   ```

3. **Real-time Countdown**
   - Updates every 100ms
   - Shows remaining time during recording
   - Large, visible countdown display

4. **Audio Playback Preview**
   - Native HTML5 audio player
   - Play/pause controls
   - Waveform visualization (via browser default)

5. **Re-record Capability**
   - Reset button to start over
   - Cleans up previous Blob/URL
   - Returns to idle state

### Hook Architecture: `useVoiceRecording`

**Responsibilities:**
- Manage MediaRecorder lifecycle
- Handle audio permissions
- Track recording state and time
- Generate audio Blob and URL
- Cleanup on unmount

**Key Implementation Details:**
```typescript
const mediaRecorderRef = useRef<MediaRecorder | null>(null);
const chunksRef = useRef<Blob[]>([]);
const timerRef = useRef<NodeJS.Timeout | null>(null);

// Auto-stop after maxDuration
timerRef.current = setInterval(() => {
  const elapsed = Date.now() - startTimeRef.current;
  const remaining = Math.max(0, maxDuration - elapsed);
  setTimeRemaining(Math.ceil(remaining / 1000));
  
  if (remaining <= 0) {
    stopRecording();
  }
}, 100);
```

**Cleanup Pattern:**
```typescript
useEffect(() => {
  return () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    if (audioURL) {
      URL.revokeObjectURL(audioURL);
    }
  };
}, [audioURL]);
```

### Component: `VoiceRecording`

**Features:**
1. **Image Preview**
   - Shows captured photos for context
   - 3-column grid layout
   - Labeled with zone names

2. **Recording Interface**
   - Idle state: Red microphone button
   - Recording state: Animated pulse + countdown
   - Completed state: Green checkmark + audio player

3. **Visual States**
   - Icons: Microphone (idle/recording), Checkmark (completed)
   - Colors: Red (recording), Green (success)
   - Animations: Pulse effect during recording

4. **User Controls**
   - Click to start recording
   - "Stop Recording" button (manual stop)
   - "Re-record" button (reset)
   - "Continue" button (proceed to next step)

### Audio Format Considerations

**Current: WebM Audio**
```typescript
const mediaRecorder = new MediaRecorder(stream, {
  mimeType: 'audio/webm',
});
```

**Browser Support:**
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ⚠️ May need fallback (check compatibility)

**Future Enhancement:**
If Safari compatibility needed, add format detection:
```typescript
const getSupportedMimeType = () => {
  const types = ['audio/webm', 'audio/mp4', 'audio/ogg'];
  return types.find(type => MediaRecorder.isTypeSupported(type));
};
```

### Error Handling

**Microphone Access:**
```typescript
try {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  // ... proceed
} catch (error) {
  console.error('Error accessing microphone:', error);
  alert('Could not access microphone. Please grant permission.');
}
```

**Common Issues:**
- User denies permission
- No microphone available
- HTTPS required (won't work on HTTP except localhost)
- Browser doesn't support MediaRecorder

### Data Flow

1. User captures 3 photos in Step 1
2. Photos passed as props to VoiceRecording component
3. User records 10-second audio
4. Audio Blob stored in state
5. Both images + audio passed to Step 3 (Generate Video)

**Memory Management:**
- Images: Base64 encoded strings (stored in state)
- Audio: Blob object (stored in state)
- All data ready to send to backend API

## Background Segmentation Considerations

### Current Implementation: ✅ Keep Background

**Decision:** Leave the background in captured images (no segmentation).

**Rationale:**

1. **Video Generation Context**
   - Veo 3 benefits from scene context
   - Background provides lighting information
   - Better spatial composition
   - Scene consistency across angles
   - More natural-looking generated videos

2. **Simplicity First**
   - Working system in place
   - Don't add complexity prematurely
   - Focus on full pipeline integration first

3. **Voice Cloning Compatibility**
   - ElevenLabs IVC doesn't require background removal
   - Only needs clear face/mouth visibility (✓ already have)

4. **Professional Appearance**
   - Real Cameo videos often include background
   - Feels more authentic and less "floating head"
   - Users expect natural-looking videos

### When to Consider Segmentation

Add background removal if:

- ✗ Veo 3 generates weird background artifacts
- ✗ You want custom background compositing
- ✗ Face-swapping or advanced effects needed
- ✗ "Studio" or "green screen" aesthetic desired
- ✗ User explicitly requests background removal

### Implementation Options (If Needed Later)

#### Option 1: MediaPipe Selfie Segmentation
**Pros:**
- Already using MediaPipe ecosystem
- Fast browser-based processing
- Good quality for real-time use
- No server-side processing needed

**Cons:**
- Less accurate than ML models
- May struggle with complex backgrounds

**Implementation:**
```typescript
import { SelfieSegmentation } from '@mediapipe/selfie_segmentation';

const selfieSegmentation = new SelfieSegmentation({
  locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/${file}`;
  }
});

selfieSegmentation.setOptions({
  modelSelection: 1, // 0 = general, 1 = landscape
});
```

#### Option 2: rembg (Python-based)
**Pros:**
- Excellent quality (U²-Net model)
- Very reliable segmentation
- Good edge detection

**Cons:**
- Requires Python backend
- Server-side processing
- Slower than browser-based

**Implementation:**
```bash
pip install rembg
```

```python
from rembg import remove
from PIL import Image

input_image = Image.open('input.png')
output_image = remove(input_image)
output_image.save('output.png')
```

#### Option 3: BackgroundRemover.js
**Pros:**
- Pure JavaScript
- Works in browser
- Good balance of speed/quality

**Cons:**
- Larger bundle size
- Requires TensorFlow.js

**Implementation:**
```bash
npm install @imgly/background-removal
```

```typescript
import removeBackground from '@imgly/background-removal';

async function segmentBackground(imageUrl: string) {
  const blob = await removeBackground(imageUrl);
  return URL.createObjectURL(blob);
}
```

#### Option 4: Server-Side API Route
**Pros:**
- Keeps client bundle small
- Can use any segmentation model
- Secure API key management

**Cons:**
- Requires backend infrastructure
- Adds latency
- Server costs

**Implementation:**
```typescript
// app/api/segment/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const { image } = await request.json();
  
  // Call segmentation service
  const segmentedImage = await removeBackground(image);
  
  return NextResponse.json({ segmentedImage });
}
```

### Recommended Approach (If Implementing)

**Phase 1: Test Without Segmentation**
1. Ship current implementation
2. Test with Veo 3
3. Gather user feedback
4. Evaluate if background causes issues

**Phase 2: Add Segmentation (If Needed)**
1. Start with MediaPipe Selfie Segmentation (easiest integration)
2. Make it optional: Toggle button "Remove Background"
3. Show side-by-side preview before capture
4. Let user choose which version to save

**Phase 3: Optimize (If Users Want It)**
1. Add better segmentation model if quality issues
2. Consider edge refinement
3. Add background blur as alternative to removal
4. Support custom background replacement

### Integration Example (If Implemented)

```typescript
// In useFaceDetection.ts
const captureImage = async (zone: FaceZone, removeBackground: boolean = false) => {
  if (!zone || !canvasRef.current) return;
  
  const canvas = canvasRef.current;
  let dataUrl = canvas.toDataURL('image/png');
  
  // Optional segmentation
  if (removeBackground) {
    dataUrl = await segmentBackground(dataUrl);
  }
  
  setCapturedImages(prev => ({
    ...prev,
    [zone]: dataUrl,
  }));
};
```

### Current Decision Matrix

| Scenario | Action | Reason |
|----------|--------|--------|
| Veo 3 handles backgrounds well | Keep as-is | No need to add complexity |
| Veo 3 has background artifacts | Add MediaPipe segmentation | Fast, easy integration |
| Users request feature | Add as optional toggle | Let user choose |
| Professional production use | Implement rembg backend | Best quality |

**Current Status:** ✅ Shipping without segmentation. Will revisit after Veo 3 testing.

## AI-Generated Script for Voice Recording

### Goal
Generate a personalized 10-second sentence for users to read, based on their captured images.

### Use Case
Instead of users improvising what to say, provide a relevant, contextual script that:
- References visual elements from their photos
- Sounds natural and conversational
- Fits within 10-second speaking time
- Makes the final video more engaging

### Implementation Approach

#### Option 1: Gemini Vision Analysis (Recommended)

**Workflow:**
1. User completes photo capture (3 images)
2. Before showing recording interface, analyze images with Gemini
3. Generate personalized script based on visual context
4. Display script prominently in recording UI
5. User reads script while recording

**Example Prompt:**
```typescript
const prompt = `
You are writing a personalized 10-second Cameo-style video message script.

Analyze these three images (left, center, right angles) of the person and generate 
a single sentence they should say that:
- Is conversational and friendly
- References something visible (clothing, setting, expression, etc.)
- Can be spoken naturally in 10 seconds or less
- Sounds like authentic Cameo content

Examples:
"Hey there! Quick message from my home office - hope this brightens your day!"
"What's up! Sending you good vibes in my favorite hoodie!"
"Hello! Just wanted to say hi from the sunny balcony!"

Return only the sentence to read, nothing else.
`;
```

**API Call:**
```typescript
// In VoiceRecording component
const [generatedScript, setGeneratedScript] = useState<string | null>(null);
const [loadingScript, setLoadingScript] = useState(true);

useEffect(() => {
  async function generateScript() {
    try {
      const response = await fetch('/api/generate-script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          images: [
            capturedImages.left,
            capturedImages.center,
            capturedImages.right
          ]
        })
      });
      
      const { script } = await response.json();
      setGeneratedScript(script);
    } catch (error) {
      console.error('Failed to generate script:', error);
      setGeneratedScript('Hey there! Sending you positive vibes today!');
    } finally {
      setLoadingScript(false);
    }
  }
  
  generateScript();
}, []);
```

**API Route (`/api/generate-script/route.ts`):**
```typescript
import { NextRequest, NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

export async function POST(request: NextRequest) {
  const { images } = await request.json();
  
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });
  
  const prompt = `[prompt from above]`;
  
  // Convert base64 images to Gemini format
  const imageParts = images.map((img: string) => ({
    inlineData: {
      data: img.split(',')[1], // Remove data:image/png;base64, prefix
      mimeType: 'image/png'
    }
  }));
  
  const result = await model.generateContent([prompt, ...imageParts]);
  const script = result.response.text().trim();
  
  return NextResponse.json({ script });
}
```

#### Option 2: Simple Template-Based (Fallback)

If AI generation fails or for MVP, use templates:

```typescript
const templates = [
  "Hey there! Sending you a quick hello from [location]!",
  "What's up! Hope you're having an amazing day!",
  "Hello! Just wanted to drop by and say hi!",
  "Hey! Sending positive vibes your way today!",
  "What's going on! Quick message just for you!"
];

const randomScript = templates[Math.floor(Math.random() * templates.length)];
```

#### Option 3: User-Customizable (Enhancement)

Allow users to:
- Accept AI-generated script
- Edit the script
- Write their own from scratch

```typescript
<div className="mb-6">
  <h3 className="font-semibold mb-2">Your Script</h3>
  <textarea
    value={script}
    onChange={(e) => setScript(e.target.value)}
    className="w-full p-3 border rounded-lg"
    rows={3}
    placeholder="What would you like to say?"
  />
  <button onClick={generateNewScript} className="mt-2 text-sm text-blue-500">
    ✨ Generate new suggestion
  </button>
</div>
```

### UI Display

**Before Recording:**
```tsx
<div className="bg-blue-50 border-2 border-blue-300 rounded-xl p-6 mb-6">
  <div className="flex items-start gap-3">
    <span className="text-2xl">💬</span>
    <div>
      <h3 className="font-semibold text-blue-900 mb-1">
        Your Script (Read this!)
      </h3>
      {loadingScript ? (
        <p className="text-gray-600 italic">Generating personalized message...</p>
      ) : (
        <p className="text-lg text-gray-800 leading-relaxed">
          "{generatedScript}"
        </p>
      )}
    </div>
  </div>
</div>
```

**During Recording:**
Show script prominently so user can read it:
```tsx
{state === 'recording' && (
  <div className="fixed inset-x-0 bottom-20 flex justify-center px-4">
    <div className="bg-white shadow-2xl rounded-xl p-6 max-w-2xl">
      <p className="text-2xl text-center font-medium">
        "{generatedScript}"
      </p>
    </div>
  </div>
)}
```

### Benefits

1. **Better Content Quality**
   - Users don't have to think of what to say
   - More natural, engaging videos
   - Consistent messaging

2. **Faster Flow**
   - No awkward pauses thinking of content
   - Can record immediately
   - Higher completion rate

3. **Personalization**
   - AI analyzes actual images
   - References real visual elements
   - Feels custom-made

4. **Professional Feel**
   - Polished script quality
   - Cameo-like experience
   - Production value

### TODOs

- [ ] Create `/api/generate-script` API route
- [ ] Integrate Gemini Vision API for image analysis
- [ ] Design prompt for 10-second script generation
- [ ] Add script display UI to VoiceRecording component
- [ ] Implement loading state during generation
- [ ] Add fallback templates if API fails
- [ ] Test script generation with various image types
- [ ] Add edit capability for generated scripts
- [ ] Consider regenerate button for new suggestions
- [ ] Track which scripts lead to best videos (analytics)

## Test Data Management

### Status: ✅ Implemented

**Purpose:** Save captured images and audio to disk for backend testing in isolation.

**Location:** `test-data/` directory (git-ignored except for `.gitkeep`)

**API Endpoints:**
1. `POST /api/save-test-data` - Save images and audio from browser
2. `GET /api/verify-test-data` - Check what's currently saved

**Usage:**
1. Capture photos and record voice in browser
2. Navigate to "Generate Video" step
3. Click "💾 Save Test Data to Disk" button
4. Files saved to `test-data/`:
   - `test-left.png`
   - `test-center.png`
   - `test-right.png`
   - `test-audio.webm`
   - `metadata.json`

**Backend Testing:**
```bash
# Verify saved files
curl http://localhost:3000/api/verify-test-data

# Use saved files for backend development
curl -X POST http://localhost:3000/api/train-voice \
  -F "audio=@test-data/test-audio.webm"
```

### Verification: ✅ Tested and Working

**Test Date:** 2025-01-05

**Verified Output:**
```json
{
  "fileCount": 6,
  "files": [
    "test-left.png (600 KB)",
    "test-center.png (610 KB)", 
    "test-right.png (601 KB)",
    "test-audio.webm (120 KB)",
    "metadata.json (0.21 KB)",
    ".gitkeep"
  ]
}
```

**Confirmed:**
- ✅ Base64 → PNG conversion working
- ✅ Base64 → WebM audio conversion working
- ✅ Metadata generation working
- ✅ Files are valid and playable
- ✅ Ready for backend integration testing

**File Inspection:**
```bash
# View files
ls -lh test-data/

# Verify formats
file test-data/test-audio.webm  # WebM
file test-data/test-*.png       # PNG image data

# Test playback
ffplay test-data/test-audio.webm  # Linux
```

## Next Steps

**Immediate:**
- [x] Implement state machine for photo capture
- [x] Add photo storage/preview
- [x] Auto-detect and capture when face is in position
- [x] Add visual feedback and progress indicators
- [x] Implement cooldown and recapture functionality
- [x] Add multi-step workflow with conditional rendering
- [x] Implement voice recording with 10-second limit
- [x] Add audio playback and re-record functionality
- [x] Add test data saving endpoint
- [ ] Test with Veo 3 (evaluate background handling)

**Phase 2: ElevenLabs IVC Integration** ✅ Complete
- [x] Create `/api/train-voice` endpoint
- [x] Test with saved `test-data/test-audio.webm`
- [x] Handle ElevenLabs API authentication
- [x] Successfully trained voice model (voiceId: lO0LTbv7RcyY55eq1aZ6)
- [x] Verified voice quality in ElevenLabs frontend

## Voice Training Implementation

### Status: ✅ Backend Complete

Successfully implemented ElevenLabs Instant Voice Cloning (IVC) API integration with audio conversion pipeline.

### Architecture Decision: Unified Endpoint

**Design Choice:** Use a **single unified endpoint** (`/api/generate-video`) that handles voice training internally, rather than exposing voiceId to the frontend.

**Why Unified Approach:**
1. ✅ **Simpler frontend** - One API call instead of two, one less state variable
2. ✅ **Atomic operation** - All-or-nothing, easier error handling  
3. ✅ **voiceId is implementation detail** - Frontend doesn't need to know
4. ✅ **Matches user mental model** - "I have images and audio, make my video"
5. ✅ **Cleaner flow** - No weird intermediate training step

**When to Use Separate Training:**
- Users save multiple voice clones (voice library feature)
- Users generate multiple videos from same voice (reuse voiceId)
- Voice testing/preview before video generation needed
- Premium subscription with persistent voice models

**For Cameo MVP:** Unified approach is better. One video per session, voice training is an implementation detail.

### Simplified Workflow

Frontend only tracks images and audio:

```typescript
// In page.tsx - Simple state management
const [capturedImages, setCapturedImages] = useState<CapturedImages | null>(null);
const [voiceRecording, setVoiceRecording] = useState<Blob | null>(null);
// No voiceId needed! Backend handles it internally
```

**Three-Step Flow:**

1. **Step 1: Capture Photos**
   - User captures 3 face angles (left, center, right)
   - Store in `capturedImages` state
   - → Proceed to Step 2

2. **Step 2: Record Voice**
   - User records 10-second audio
   - Store Blob in `voiceRecording` state
   - → Proceed to Step 3

3. **Step 3: Generate Video**
   - Send to **single unified endpoint** `/api/generate-video`:
     - `leftImage`, `centerImage`, `rightImage` (3 photos)
     - `audio` (voice recording)
     - `prompt` (optional personalization)
   - Backend workflow (all internal):
     - Train voice with ElevenLabs → get voiceId
     - Upload images to Veo 3
     - Generate video with images + movement
     - Extract audio from generated video
     - Replace audio using Speech-to-Speech API with voiceId
     - Return final video with cloned voice
   - Frontend receives: `{ videoUrl: "https://..." }`

### Frontend Integration

**VoiceRecording component stays simple:**

```typescript
// After recording completes - just pass audio blob
const handleComplete = () => {
  onComplete(audioBlob); // That's it! No training here
};
```

**Generate video with single API call:**

```typescript
{currentStep === 'generate' && capturedImages && voiceRecording && (
  <button onClick={async () => {
    // Single unified API call with all assets
    const formData = new FormData();
    formData.append('leftImage', capturedImages.left);
    formData.append('centerImage', capturedImages.center);
    formData.append('rightImage', capturedImages.right);
    formData.append('audio', voiceRecording);
    formData.append('prompt', 'A personalized video message...');
    
    const response = await fetch('/api/generate-video', {
      method: 'POST',
      body: formData,
    });
    
    const { videoUrl } = await response.json();
    setFinalVideoUrl(videoUrl);
  }}>
    🎬 Generate My Video
  </button>
)}
```

## Audio Swap Testing

### Status: ✅ Complete and Working!

Successfully implemented and tested the `/api/swap-audio` endpoint for testing voice cloning with pre-existing video.

**Test Date:** 2025-01-05

**Test Command:**
```bash
curl -X POST http://localhost:3000/api/swap-audio \
  -F "video=@cameo/test-data/test-video.mp4" \
  -F "voiceId=lO0LTbv7RcyY55eq1aZ6"
```

**Result:** ✅ Success
```json
{
  "success": true,
  "outputPath": "test-data/final-swapped-video.mp4",
  "message": "Audio swapped successfully! Check test-data/final-swapped-video.mp4"
}
```

**Pipeline Verified:**
- ✅ Video upload and disk write
- ✅ Audio extraction from video (ffmpeg)
- ✅ ElevenLabs Speech-to-Speech API integration
- ✅ Voice cloning with trained model (voiceId: lO0LTbv7RcyY55eq1aZ6)
- ✅ Audio stream handling and file write
- ✅ Video/audio recombination (ffmpeg)
- ✅ Temp file cleanup
- ✅ Output saved to test-data/

**Performance:**
- Total pipeline execution: ~30-60 seconds (estimated)
- Ready for integration into unified `/api/generate-video` endpoint

**Next:** Test voice quality in final video to validate cloning accuracy.

## Production Architecture: Backend Orchestration

### Clean Architecture Pattern

**Frontend Responsibilities (Minimal):**
- Capture 3 face photos
- Record 10-second audio
- Trigger video generation (single API call)
- Display progress updates
- Show/download final video

**Backend Responsibilities (Heavy Lifting):**
- Train voice clone internally (ElevenLabs IVC)
- Upload images to Veo 3
- Generate video with polling
- Download generated video
- Extract audio from video
- Replace audio with cloned voice (Speech-to-Speech)
- Combine video + cloned audio
- Upload final video to storage
- Manage temporary files/cleanup
- Handle errors and retries

### Full Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
├─────────────────────────────────────────────────────────────────┤
│  Step 1: Capture Photos    → capturedImages                    │
│  Step 2: Record Voice       → voiceRecording                    │
│  Step 3: Generate Video     → Call /api/generate-video          │
│                               (send images + audio + prompt)     │
│                              Display progress                    │
│                              Show final video                    │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND: /api/generate-video                 │
│                         (Unified Endpoint)                       │
├─────────────────────────────────────────────────────────────────┤
│  Input: { leftImage, centerImage, rightImage, audio, prompt }  │
│                                                                  │
│  0. 🎤 Train voice clone (internal)                             │
│     Status: "Training your voice..."                            │
│     - Convert audio WebM → MP3                                  │
│     - POST /v1/voices/ivc/create                                │
│     - Get voiceId (kept internal)                               │
│     - Takes ~5 seconds                                          │
│                                                                  │
│  1. ✅ Upload images to Veo 3                                   │
│     Status: "Uploading images..."                               │
│                                                                  │
│  2. ⏳ Start Veo 3 video generation                             │
│     Status: "Generating video..."                               │
│     - Create operation with prompt + images                      │
│     - Poll operation.done every 10s                             │
│     - Can take 2-5 minutes                                      │
│                                                                  │
│  3. ✅ Download generated video                                 │
│     Status: "Downloading video..."                              │
│     - Save to tmp/job-{uuid}/veo3-video.mp4                    │
│                                                                  │
│  4. 🎵 Extract audio from video                                 │
│     Status: "Extracting audio..."                               │
│     - ffmpeg -i video.mp4 -vn -acodec copy audio.aac           │
│                                                                  │
│  5. 🎤 Replace audio with cloned voice                          │
│     Status: "Applying your voice..."                            │
│     - POST /v1/speech-to-speech/{voiceId}                       │
│     - Send extracted audio                                      │
│     - Receive audio with cloned voice                           │
│                                                                  │
│  6. 🎬 Combine video + cloned audio                             │
│     Status: "Finalizing video..."                               │
│     - ffmpeg -i video.mp4 -i cloned-audio.mp3 final.mp4        │
│                                                                  │
│  7. ☁️ Upload to storage (GCS/S3)                               │
│     Status: "Uploading..."                                      │
│                                                                  │
│  8. 🧹 Cleanup temporary files                                  │
│     - Delete tmp/job-{uuid}/ directory                          │
│     - Optional: Delete voiceId from ElevenLabs                  │
│                                                                  │
│  Output: { videoUrl: "https://..." }                            │
└─────────────────────────────────────────────────────────────────┘
```

### Frontend State Management

**Maximally simplified state:**

```typescript
const [capturedImages, setCapturedImages] = useState<CapturedImages | null>(null);
const [voiceRecording, setVoiceRecording] = useState<Blob | null>(null);
const [videoStatus, setVideoStatus] = useState<VideoStatus>({
  status: 'idle' | 'processing' | 'complete' | 'error',
  currentStep: string,
  progress: number, // 0-100
  videoUrl: string | null,
  error: string | null,
});
```

**Single Unified API Call:**

```typescript
// Create FormData with all assets
const formData = new FormData();
formData.append('leftImage', capturedImages.left);   // Base64 or Blob
formData.append('centerImage', capturedImages.center);
formData.append('rightImage', capturedImages.right);
formData.append('audio', voiceRecording);             // Blob
formData.append('prompt', 'A personalized video message from me to you!');

const response = await fetch('/api/generate-video', {
  method: 'POST',
  body: formData,
});

const { videoUrl } = await response.json();
// Or use SSE for progress updates (see below)
```

### Cost Optimization

**ElevenLabs:**
- Voice training: ~10 credits per clone (happens once per video)
- Speech-to-Speech: ~1 credit per second (~5-10 seconds typical)
- Voice cleanup: Can optionally delete voiceId after use (free up quota)
- Estimate: $0.50-1.00 per video

**Veo 3:**
- Video generation: TBD (check pricing)
- Estimate: $1-5 per video

**Total estimated cost: $1.50-6.00 per video**

**Immediate (Testing):**
- [x] Create `/api/swap-audio` test endpoint
- [x] Test Speech-to-Speech with test-data/video.mp4
- [x] Use existing voiceId: `lO0LTbv7RcyY55eq1aZ6`
- [ ] Validate voice quality in real video context (play final-swapped-video.mp4)
- [ ] Measure audio extraction/swap latency (add timing logs)

**Phase 3: Unified Video Generation Endpoint** ← CURRENT FOCUS
- [ ] Create `/api/generate-video` endpoint (unified)
- [ ] Accept `leftImage`, `centerImage`, `rightImage`, `audio`, `prompt`
- [ ] Backend pipeline:
  - [ ] Train voice internally (call ElevenLabs IVC, get voiceId)
  - [ ] Upload images to Veo 3
  - [ ] Generate video with Veo 3 SDK
  - [ ] Extract audio from generated video (ffmpeg)
  - [ ] Replace audio using Speech-to-Speech with voiceId
  - [ ] Combine video + cloned audio (ffmpeg)
  - [ ] Upload to GCS/return URL
- [ ] Implement progress tracking (SSE or polling)
- [ ] Handle errors and cleanup temp files

**Frontend (Simpler Now!):**
- [ ] No changes needed to VoiceRecording component  
- [ ] Add generate video UI in Step 3
- [ ] Single API call with FormData (images + audio)
- [ ] Display progress updates
- [ ] Show/play final video

**Phase 4: Audio Swap & Final Assembly (Deprecated)**
- This is now part of the unified /api/generate-video endpoint
- [ ] ~~Create `/api/swap-audio` endpoint~~
- [ ] ~~Use ElevenLabs voice model for narration~~
- [ ] ~~Replace Veo 3 video audio with cloned voice~~
- [ ] Use ffmpeg or cloud service for audio swap
- [ ] Generate final downloadable video
- [ ] Add sharing options

**Phase 5: AI Script Generation** (Enhancement)
- [ ] Create Gemini Vision API integration
- [ ] Generate personalized script from captured images
- [ ] Display script in voice recording UI
- [ ] Add script editing capability
- [ ] Implement fallback templates
- [ ] Test script quality and timing

**Future Enhancements:**
- [ ] Add pitch and roll calculations for full 3D head orientation
- [ ] Implement Gemini Live conversational guidance
- [ ] Add background segmentation (if Veo 3 requires it)
- [ ] Export functionality for captured assets
- [ ] Multi-user session management
- [ ] Save projects for later completion
- [ ] Video gallery/history
- [ ] Social sharing features
- [ ] Build complete Cameo clone workflow

## Troubleshooting

### Camera Not Working
1. Check browser permissions (camera access required)
2. Verify browser console for errors (F12)
3. Ensure HTTPS or localhost (camera API requires secure context)

### Microphone Not Working
1. Check browser permissions (microphone access required)
2. Verify browser console for errors (F12)
3. Ensure HTTPS or localhost (MediaRecorder requires secure context)
4. Test in different browser (Safari may have issues)

### Build Errors
1. Ensure all dependencies installed: `npm install`
2. Clear Next.js cache: `rm -rf .next`
3. Restart dev server

### Performance Issues
1. Reduce canvas resolution (currently 640x480)
2. Lower MediaPipe confidence thresholds
3. Reduce landmark visualization (draw fewer points)

### Capture Not Triggering
1. Check yaw angle thresholds (may need adjustment)
2. Verify face is fully visible (all landmarks detected)
3. Ensure stable hold for full 2.5 seconds
4. Wait for cooldown period to complete (1.5s)

### Audio Issues
1. Recording too quiet: Check microphone input levels
2. Audio not playing: Verify browser supports WebM audio
3. Recording cuts off early: Check 10-second timer logic
4. Memory leak: Ensure URL.revokeObjectURL called on cleanup

## Resources

- [MediaPipe Face Mesh Documentation](https://google.github.io/mediapipe/solutions/face_mesh.html)
- [MediaPipe Selfie Segmentation](https://google.github.io/mediapipe/solutions/selfie_segmentation.html)
- [Next.js Documentation](https://nextjs.org/docs)
- [MediaPipe CDN Files](https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/)
- [Google AI Studio Live Audio Example](https://aistudio.google.com/apps/bundled/live_audio)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Gemini Vision API](https://ai.google.dev/gemini-api/docs/vision)
- [MediaRecorder API](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [Veo 3 Documentation](https://deepmind.google/technologies/veo/)
- [ElevenLabs IVC API](https://elevenlabs.io/docs)
