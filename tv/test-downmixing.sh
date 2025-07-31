#!/bin/bash
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Test script to compare stereo vs mono capture from HDMI capture card
# This tests whether pw-cat properly downmixes stereo to mono or just drops a channel

echo "🎵 Testing HDMI audio downmixing: Stereo vs Mono"
echo "📺 Make sure HDMI source is playing audio with stereo content!"
echo ""

# HDMI capture device target
HDMI_TARGET="alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo"

# Output files
STEREO_FILE="/tmp/hdmi_stereo_test.wav"
MONO_FILE="/tmp/hdmi_mono_test.wav"

# Recording duration in seconds
RECORD_DURATION=10

# Clean up any existing files
rm -f "$STEREO_FILE" "$MONO_FILE"

echo "🎤 Starting simultaneous stereo and mono captures..."
echo "⏱️  Recording for $RECORD_DURATION seconds..."

# Start both captures in background
pw-cat --record "$STEREO_FILE" --target "$HDMI_TARGET" \
       --rate 48000 --channels 2 --format s16 &
STEREO_PID=$!

pw-cat --record "$MONO_FILE" --target "$HDMI_TARGET" \
       --rate 48000 --channels 1 --format s16 &
MONO_PID=$!

# Wait for recording duration
sleep "$RECORD_DURATION"

# Stop both recordings
echo "⏹️  Stopping recordings..."
kill $STEREO_PID $MONO_PID 2>/dev/null
wait $STEREO_PID $MONO_PID 2>/dev/null

echo ""
echo "📊 Comparing results:"

# Check if files were created
if [[ -f "$STEREO_FILE" && -f "$MONO_FILE" ]]; then
    # Get file sizes
    STEREO_SIZE=$(stat -c%s "$STEREO_FILE")
    MONO_SIZE=$(stat -c%s "$MONO_FILE")

    echo "📁 File sizes:"
    echo "   Stereo: $(numfmt --to=iec-i --suffix=B $STEREO_SIZE) ($STEREO_SIZE bytes)"
    echo "   Mono:   $(numfmt --to=iec-i --suffix=B $MONO_SIZE) ($MONO_SIZE bytes)"

    # Calculate ratio
    if [[ $MONO_SIZE -gt 0 ]]; then
        RATIO=$(echo "scale=2; $STEREO_SIZE / $MONO_SIZE" | bc)
        echo "   Ratio:  ${RATIO}:1"

        # Check if ratio is close to 2:1 (expected for proper stereo->mono conversion)
        if (( $(echo "$RATIO > 1.8 && $RATIO < 2.2" | bc -l) )); then
            echo "✅ File size ratio suggests proper downmixing (stereo ~2x mono size)"
        else
            echo "⚠️  Unexpected file size ratio - may indicate channel dropping"
        fi
    fi

    echo ""
    echo "🎧 Listen to both files to compare audio content:"
    echo "   Stereo: pw-cat --playback $STEREO_FILE"
    echo "   Mono:   pw-cat --playback $MONO_FILE"
    echo ""
    echo "🔍 Expected behavior:"
    echo "   - If DOWNMIXING: Mono should contain audio from both left+right channels mixed"
    echo "   - If DROPPING: Mono will be missing audio that was only in one channel"

else
    echo "❌ Error: One or both recording files were not created"
    if [[ ! -f "$STEREO_FILE" ]]; then echo "   Missing: $STEREO_FILE"; fi
    if [[ ! -f "$MONO_FILE" ]]; then echo "   Missing: $MONO_FILE"; fi
fi

echo ""
echo "🧹 Clean up files with: rm $STEREO_FILE $MONO_FILE"
