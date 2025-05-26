#!/bin/bash
set -e

# Start Xvfb in the background on display :1
echo "Starting Xvfb on display :1..."
Xvfb :1 -screen 0 1024x768x24 -nolisten tcp &
XVFB_PID=$!
export DISPLAY=:1

# Wait for Xvfb to be ready
echo "Waiting for Xvfb to initialize..."
ATTEMPTS=0
MAX_ATTEMPTS=20 # Wait for up to 10 seconds
until xdpyinfo -display $DISPLAY > /dev/null 2>&1; do
  sleep 0.5
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
    echo "Xvfb failed to start after $MAX_ATTEMPTS attempts."
    # Try to get some logs
    pgrep Xvfb && ps aux | grep Xvfb
    if [ -f "/var/log/Xorg.1.log" ]; then cat /var/log/Xorg.1.log; fi
    if [ -f "$HOME/.local/share/xorg/Xorg.1.log" ]; then cat "$HOME/.local/share/xorg/Xorg.1.log"; fi
    kill $XVFB_PID || true
    exit 1
  fi
done
echo "Xvfb started successfully."

echo "Starting application via run_docker.sh..." # MODIFIED
# This assumes run_docker.sh is in the WORKDIR /home/$USERNAME/app
./run_docker.sh # MODIFIED

# Clean up Xvfb when the main application exits
echo "Application finished. Cleaning up Xvfb..."
kill $XVFB_PID
wait $XVFB_PID || true # Wait, but don't fail if Xvfb is already gone
echo "Exiting entrypoint."
