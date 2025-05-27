#!/bin/bash
set -e # Exit on any error

cleanup() {
  echo "Caught signal, cleaning up..."
  if [ -n "$APP_PID" ]; then kill $APP_PID || true; fi
  if [ -n "$FFMPEG_PID" ]; then kill $FFMPEG_PID || true; fi
  if [ -n "$LK_SERVER_PID" ]; then kill $LK_SERVER_PID || true; fi
  if [ -n "$XVFB_PID" ]; then kill $XVFB_PID || true; fi
  wait
  echo "Cleanup finished."
  exit 0
}

trap cleanup SIGINT SIGTERM SIGQUIT

XVFB_LOG="/tmp/xvfb_run.log" # Define log file path

echo "Starting Xvfb on display $DISPLAY..."
# Redirect Xvfb's stdout and stderr to a log file
Xvfb $DISPLAY -screen 0 1024x768x24 -nolisten tcp -ac > "$XVFB_LOG" 2>&1 &
XVFB_PID=$!

echo "Waiting for Xvfb to initialize on $DISPLAY (PID: $XVFB_PID)..."
ATTEMPTS=0
MAX_ATTEMPTS=20
until xdpyinfo -display $DISPLAY > /dev/null 2>&1; do
  # Check if Xvfb process is still alive
  if ! ps -p $XVFB_PID > /dev/null; then
    echo "Xvfb process (PID: $XVFB_PID) died prematurely!"
    echo "--- Contents of $XVFB_LOG ---"
    cat "$XVFB_LOG" || echo "$XVFB_LOG not found."
    echo "--- End of $XVFB_LOG ---"
    # Attempt to show other Xorg logs if they exist
    if [ -f "/var/log/Xorg.1.log" ]; then
      echo "--- /var/log/Xorg.1.log ---"
      cat /var/log/Xorg.1.log
    fi
    if [ -f "$HOME/.local/share/xorg/Xorg.1.log" ]; then
      echo "--- $HOME/.local/share/xorg/Xorg.1.log ---"
      cat "$HOME/.local/share/xorg/Xorg.1.log"
    fi
    exit 1
  fi
  sleep 0.5
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
    echo "Xvfb failed to start accepting connections on $DISPLAY after $MAX_ATTEMPTS attempts (Xvfb PID: $XVFB_PID)."
    echo "--- ps aux | grep Xvfb output ---"
    ps aux | grep '[X]vfb' # Use [X]vfb to avoid grep showing itself
    echo "--- End ps aux output ---"
    echo "--- Contents of $XVFB_LOG ---"
    cat "$XVFB_LOG" || echo "$XVFB_LOG not found."
    echo "--- End of $XVFB_LOG ---"
    # Attempt to show other Xorg logs
    if [ -f "/var/log/Xorg.1.log" ]; then
      echo "--- /var/log/Xorg.1.log ---"
      cat /var/log/Xorg.1.log
    fi
    if [ -f "$HOME/.local/share/xorg/Xorg.1.log" ]; then
      echo "--- $HOME/.local/share/xorg/Xorg.1.log ---"
      cat "$HOME/.local/share/xorg/Xorg.1.log"
    fi
    # Try a simple xset command for more info
    echo "--- Attempting xset -display $DISPLAY q ---"
    xset -display $DISPLAY q || echo "xset command also failed."
    kill $XVFB_PID || true # Kill the Xvfb process as it's not responding
    exit 1
  fi
done
echo "Xvfb started successfully on $DISPLAY."

./run_docker.sh
