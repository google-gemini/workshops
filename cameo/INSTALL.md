# Installation Guide

## Prerequisites

- Node.js 18+ and npm
- ffmpeg installed on your system
- Google Cloud account with Gemini API access
- ElevenLabs account with API key

## Install ffmpeg

### macOS:
```bash
brew install ffmpeg
```

### Ubuntu/Debian:
```bash
sudo apt-get install ffmpeg
```

### Windows:
Download from: https://ffmpeg.org/download.html

## Setup

### 1. Install Dependencies

```bash
cd cameo
npm install
npm install @google/genai
```

### 2. Environment Variables

Create `cameo/.env.local`:

```bash
# Google Gemini API (for Veo 3)
GOOGLE_GENAI_API_KEY=your_google_api_key_here

# ElevenLabs API (for voice cloning)
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

**Get API Keys:**
- Google Gemini: https://aistudio.google.com/apikey
- ElevenLabs: https://elevenlabs.io/api

### 3. Start Development Server

```bash
npm run dev
```

### 4. Test the Pipeline

Open in browser:
- Test audio swap: http://localhost:3000/test-swap.html
- Test full generation: http://localhost:3000/test-generate.html

## Verify Installation

```bash
# Check ffmpeg
ffmpeg -version

# Check Node version
node --version  # Should be 18+

# Check dependencies
npm list @google/genai
npm list @elevenlabs/elevenlabs-js
npm list fluent-ffmpeg
```

## Troubleshooting

**"ffmpeg not found" error:**
- Make sure ffmpeg is in your PATH
- Restart terminal after installation

**"Invalid API key" error:**
- Verify `.env.local` exists in `cameo/` directory
- Check API keys are valid and not expired
- Restart dev server after adding env vars

**Module not found errors:**
- Run `npm install` again
- Delete `node_modules` and run `npm install`

## Ready to Go! 🚀

You're now ready to generate AI videos with voice cloning!

Try the test pages:
1. `/test-swap.html` - Test audio swapping only
2. `/test-generate.html` - Test full video generation pipeline
