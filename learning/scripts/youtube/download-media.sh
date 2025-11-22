#!/usr/bin/env bash
# scripts/youtube/download-media.sh
# Usage: ./download-media.sh VIDEO_ID

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 VIDEO_ID"
    echo "Example: $0 kCc8FmEb1nY"
    exit 1
fi

VIDEO_ID="$1"
VIDEO_URL="https://www.youtube.com/watch?v=${VIDEO_ID}"
OUTPUT_DIR="youtube/${VIDEO_ID}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "📹 Downloading media for: ${VIDEO_ID}"
echo "🔗 URL: ${VIDEO_URL}"
echo ""

# Download audio in background
echo "🎵 Starting audio download..."
(
    yt-dlp \
        -x \
        --audio-format mp3 \
        --audio-quality 0 \
        "${VIDEO_URL}" \
        -o "${OUTPUT_DIR}/audio.mp3" \
        --progress \
        --newline \
        2>&1 | while IFS= read -r line; do
            echo "[AUDIO] $line"
        done
    echo "✅ Audio download complete!"
) &
AUDIO_PID=$!

# Download video (no audio) in background
echo "🎬 Starting video download (no audio)..."
(
    yt-dlp \
        -f "bestvideo[height<=720]" \
        --no-audio \
        "${VIDEO_URL}" \
        -o "${OUTPUT_DIR}/video.mp4" \
        --progress \
        --newline \
        2>&1 | while IFS= read -r line; do
            echo "[VIDEO] $line"
        done
    echo "✅ Video download complete!"
) &
VIDEO_PID=$!

# Wait for both to complete
echo ""
echo "⏳ Waiting for downloads to complete..."
echo "   Audio PID: ${AUDIO_PID}"
echo "   Video PID: ${VIDEO_PID}"
echo ""

# Wait for both processes
wait $AUDIO_PID
AUDIO_EXIT=$?

wait $VIDEO_PID
VIDEO_EXIT=$?

# Check results
echo ""
if [ $AUDIO_EXIT -eq 0 ] && [ $VIDEO_EXIT -eq 0 ]; then
    echo "🎉 Both downloads completed successfully!"
    
    # Show file sizes
    if [ -f "${OUTPUT_DIR}/audio.mp3" ]; then
        AUDIO_SIZE=$(du -h "${OUTPUT_DIR}/audio.mp3" | cut -f1)
        echo "   📊 Audio: ${AUDIO_SIZE}"
    fi
    
    if [ -f "${OUTPUT_DIR}/video.mp4" ]; then
        VIDEO_SIZE=$(du -h "${OUTPUT_DIR}/video.mp4" | cut -f1)
        echo "   📊 Video: ${VIDEO_SIZE}"
    fi
    
    echo ""
    echo "📁 Files saved to: ${OUTPUT_DIR}/"
    exit 0
else
    echo "❌ Download failed!"
    [ $AUDIO_EXIT -ne 0 ] && echo "   Audio exit code: ${AUDIO_EXIT}"
    [ $VIDEO_EXIT -ne 0 ] && echo "   Video exit code: ${VIDEO_EXIT}"
    exit 1
fi
