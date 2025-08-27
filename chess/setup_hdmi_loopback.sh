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

set -e

# Configuration
HDMI_SOURCE="/dev/video4"  # Your HDMI capture device
LOOPBACK_DEVICES="10,11"   # Output loopback device numbers
CARD_LABELS="HDMI Loop 1,HDMI Loop 2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[HDMI Setup]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[HDMI Setup]${NC} $1"
}

error() {
    echo -e "${RED}[HDMI Setup]${NC} $1"
}

cleanup() {
    log "Cleaning up HDMI loopback setup..."
    
    # Kill any ffmpeg processes we started
    if [[ -n "$FFMPEG_PID1" ]]; then
        kill $FFMPEG_PID1 2>/dev/null && log "Killed ffmpeg process $FFMPEG_PID1"
    fi
    if [[ -n "$FFMPEG_PID2" ]]; then
        kill $FFMPEG_PID2 2>/dev/null && log "Killed ffmpeg process $FFMPEG_PID2"
    fi
    
    
    # Kill any pw-cat processes
    killall -v pw-cat 2>/dev/null || true
    
    # Wait a moment for graceful shutdown
    sleep 1
    
    log "HDMI loopback cleanup complete"
}

# Set up cleanup trap
trap cleanup EXIT INT TERM

main() {
    log "Setting up HDMI loopback devices..."
    
    # 1. Kill any existing video processes
    log "Killing existing video processes..."
    sudo pkill -f "ffmpeg.*video" || true
    sudo pkill -f "v4l2" || true
    sleep 1
    
    # 2. Reset v4l2loopback module
    log "Resetting v4l2loopback module..."
    sudo modprobe -r v4l2loopback 2>/dev/null || true
    sleep 1
    
    log "Loading v4l2loopback with devices $LOOPBACK_DEVICES..."
    sudo modprobe v4l2loopback devices=2 video_nr=$LOOPBACK_DEVICES card_label="$CARD_LABELS"
    
    # 3. Check devices exist
    log "Checking loopback devices..."
    for dev in 10 11; do
        if [[ ! -e "/dev/video$dev" ]]; then
            error "Device /dev/video$dev not found!"
            exit 1
        fi
        log "✓ /dev/video$dev exists"
    done
    
    # 4. Test HDMI source
    log "Testing HDMI source $HDMI_SOURCE..."
    if [[ ! -e "$HDMI_SOURCE" ]]; then
        error "HDMI source $HDMI_SOURCE not found!"
        exit 1
    fi
    
    # Quick ffprobe test (capture any errors but don't fail)
    if timeout 3 ffprobe "$HDMI_SOURCE" >/dev/null 2>&1; then
        log "✓ HDMI source $HDMI_SOURCE is accessible"
    else
        warn "HDMI source test inconclusive (might still work)"
    fi
    
    # 5. Start single ffmpeg process with multiple outputs
    log "Starting ffmpeg process with dual outputs..."
    
    # Single process: HDMI -> both loopback devices
    ffmpeg -loglevel error -f v4l2 -video_size 1920x1080 -framerate 30 -i "$HDMI_SOURCE" \
      -f v4l2 /dev/video10 \
      -f v4l2 /dev/video11 &
    FFMPEG_PID1=$!
    log "Started ffmpeg for both outputs (PID: $FFMPEG_PID1)"
    FFMPEG_PID2=""  # No second process
    
    # 6. Wait a moment and test outputs
    sleep 2
    
    log "Testing loopback outputs..."
    for dev in 10 11; do
        if timeout 2 ffprobe "/dev/video$dev" >/dev/null 2>&1; then
            log "✓ /dev/video$dev is streaming"
        else
            warn "⚠ /dev/video$dev test failed (might need more time)"
        fi
    done
    
    # 7. Show device info
    log "HDMI loopback setup complete!"
    log "Video devices:"
    v4l2-ctl --list-devices | grep -A3 "HDMI Loop" || log "Device listing failed"
    
    log "Process IDs: ffmpeg=$FFMPEG_PID1"
    log "📺 Video: Use /dev/video10 or /dev/video11"
    log "🔊 Audio: Both Chess Companion and OBS read directly from HDMI device"
    log "Press Ctrl+C to stop and cleanup"
    
    # 8. Keep running and monitor
    while true; do
        # Check if our ffmpeg process is still running
        if ! kill -0 $FFMPEG_PID1 2>/dev/null; then
            error "ffmpeg process died (PID $FFMPEG_PID1)"
            break
        fi
        
        sleep 5
    done
}

main "$@"
