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

set -e # Exit on any error

XVFB_PID=""
LK_SERVER_PID=""
FFMPEG_PID=""

cleanup() {
  echo "Caught signal or script ending, cleaning up..."
  if [ -n "$FFMPEG_PID" ] && ps -p $FFMPEG_PID > /dev/null; then
    echo "Stopping FFmpeg (PID: $FFMPEG_PID)..."
    kill $FFMPEG_PID || true
  fi
  if [ -n "$LK_SERVER_PID" ] && ps -p $LK_SERVER_PID > /dev/null; then
    echo "Stopping LiveKit server (PID: $LK_SERVER_PID)..."
    kill $LK_SERVER_PID || true
  fi
  if [ -n "$XVFB_PID" ] && ps -p $XVFB_PID > /dev/null; then
    echo "Stopping Xvfb (PID: $XVFB_PID)..."
    kill $XVFB_PID || true
  fi
  wait
  echo "Cleanup finished."
}

trap cleanup SIGINT SIGTERM SIGQUIT EXIT

XVFB_LOG="/tmp/xvfb_run.log"
echo "Starting Xvfb on display $DISPLAY (Log: $XVFB_LOG)..."
Xvfb $DISPLAY -screen 0 1024x768x24 -nolisten tcp -ac > "$XVFB_LOG" 2>&1 &
XVFB_PID=$!

echo "Waiting for Xvfb to initialize on $DISPLAY (PID: $XVFB_PID)..."
ATTEMPTS=0
MAX_ATTEMPTS=20
until xdpyinfo -display $DISPLAY > /dev/null 2>&1; do
  if ! ps -p $XVFB_PID > /dev/null; then
    echo "Xvfb process (PID: $XVFB_PID) died prematurely!"
    cat "$XVFB_LOG" || echo "$XVFB_LOG not found."
    exit 1
  fi
  sleep 0.5
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
    echo "Xvfb failed to start accepting connections on $DISPLAY after $MAX_ATTEMPTS attempts."
    cat "$XVFB_LOG" || echo "$XVFB_LOG not found."
    exit 1
  fi
done
echo "Xvfb started successfully on $DISPLAY."

echo "Starting LiveKit server in --dev mode..."
livekit-server --dev &
LK_SERVER_PID=$!

echo "Waiting for LiveKit server to be ready on port 7880 (HTTP/WHIP) (PID: $LK_SERVER_PID)..."
LK_ATTEMPTS=0
LK_MAX_ATTEMPTS=40
HTTP_READY=0
until [ "$HTTP_READY" -eq 1 ]; do
  if ! ps -p $LK_SERVER_PID > /dev/null; then
    echo "LiveKit server process (PID: $LK_SERVER_PID) died prematurely!"
    exit 1
  fi
  if nc -z -w1 localhost 7880; then # Check main HTTP port
    echo "LiveKit HTTP/WHIP port 7880 is ready."
    HTTP_READY=1
  fi
  sleep 0.5
  LK_ATTEMPTS=$((LK_ATTEMPTS + 1))
  if [ "$LK_ATTEMPTS" -ge "$LK_MAX_ATTEMPTS" ]; then
    echo "LiveKit server failed to start listening on port 7880 after $LK_MAX_ATTEMPTS attempts."
    exit 1
  fi
done
echo "LiveKit server started successfully."

# WHIP endpoint for --dev mode.
# The stream key 'smashbot_stream' will become part of the room name or stream identifier.
# For WHIP, the stream key is often part of the URL path or an HTTP header,
# depending on the SFU. LiveKit's ingress system handles this.
# In --dev mode, LiveKit might create a room named after the stream key or participant.
# For WHIP, we need a Bearer token, even in --dev mode for the default ingress.
# The lktool can generate this: lktool token --dev --publish --room smashbot_stream --identity ffmpeg_publisher
# For simplicity now, we'll try the default ingress which might not require a token if unprotected in --dev
# OR we might need to create an ingress first even in --dev.
# The example used http://localhost:7880/ingress/default_ingress
# Let's use the WHIP URL format that includes the stream key for the room.
# A common WHIP pattern is for FFmpeg to POST an SDP offer.
# LiveKit's WHIP endpoint might be simpler: it expects the stream directly.

LIVEKIT_WHIP_URL="http://127.0.0.1:7880/whip/smashbot_stream" # Using a common WHIP path structure
# Alternatively, using the /ingress/ path if that's LiveKit's default --dev WHIP path:
# LIVEKIT_WHIP_URL="http://127.0.0.1:7880/ingress/default_ingress"
# Consult LiveKit --dev mode docs for exact WHIP ingest URL or if token is needed.
# The example you found "http://localhost:7880/ingress/default_ingress" is a good bet for --dev.

FFMPEG_LOG="/tmp/ffmpeg.log"
echo "Starting FFmpeg to stream $DISPLAY via WHIP to $LIVEKIT_WHIP_URL (Log: $FFMPEG_LOG)..."

# FFmpeg command for WHIP (Video only for now to simplify)
# This assumes FFmpeg's WHIP output will handle the HTTP POST and SDP exchange.
# The exact command might need tweaking based on FFmpeg version and LiveKit's WHIP expectations.
# The "-protocol_whitelist file,http,https,tcp,tls,udp,rtp" might be needed if FFmpeg complains about http output.
ffmpeg -nostdin -loglevel error \
  -f x11grab -framerate 30 -video_size 1024x768 -i $DISPLAY \
  -c:v libvpx -crf 30 -b:v 1M -deadline realtime -cpu-used 4 \
  -pix_fmt yuv420p \
  -flags +global_header \
  -f webm \
  -method POST \
  -content_type "application/sdp" \ # Often required for WHIP to send offer
"$LIVEKIT_WHIP_URL" > "$FFMPEG_LOG" 2>&1 &

# A more direct WHIP approach if FFmpeg's generic HTTP output handles it:
# The example you found:
# ffmpeg -f x11grab -video_size 1280x720 -i :1 \
#        -f pulse -i default \ # We'll skip audio for now
#        -c:v libvpx -crf 30 -b:v 1M \
#        -c:a libopus \
#        -f webm -content_type video/webm \  <-- This one is simpler for FFmpeg's direct output if WHIP endpoint expects raw WebM
#        http://localhost:7880/ingress/default_ingress

# LET'S TRY THE SIMPLER WEBM POSTING APPROACH FROM YOUR EXAMPLE FIRST (VIDEO ONLY)
LIVEKIT_WHIP_URL_INGRESS="http://127.0.0.1:7880/ingress/default_ingress"
ffmpeg -nostdin -loglevel error \
  -f x11grab -framerate 30 -video_size 1024x768 -i $DISPLAY \
  -c:v libvpx-vp9 -deadline realtime -cpu-used 8 -b:v 1500k -maxrate 2000k -crf 32 -threads 4 -row-mt 1 \
  -pix_fmt yuv420p \
  -f webm \
  -content_type "video/webm" \
  "$LIVEKIT_WHIP_URL_INGRESS" > "$FFMPEG_LOG" 2>&1 &

FFMPEG_PID=$!

echo "Waiting briefly for FFmpeg to start (PID: $FFMPEG_PID)..."
sleep 5 # Increased sleep for WHIP negotiation
if ! ps -p $FFMPEG_PID > /dev/null; then
  echo "FFmpeg process (PID: $FFMPEG_PID) failed to start or exited prematurely."
  cat "$FFMPEG_LOG" || echo "$FFMPEG_LOG not found"
  exit 1
fi
echo "FFmpeg WHIP seems to have started."

echo "Starting application (virtual_controller.py via run_docker.sh) in foreground..."
./run_docker.sh

echo "Application run_docker.sh has exited."
