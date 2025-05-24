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
    echo "Xvfb logs:"
    # Attempt to cat Xvfb log if it exists, common paths
    cat /var/log/Xorg.1.log || cat ~/.local/share/xorg/Xorg.1.log || echo "No Xvfb log found."
    kill $XVFB_PID
    exit 1
  fi
done
echo "Xvfb started successfully."

# IMPORTANT SCRIPT MODIFICATION SUGGESTIONS:
# 1. In `virtual_controller.py`, change `n64_core_path` to just the core filename:
#    `n64_core_path = "parallel_n64_libretro.so"` (or your chosen core's .so name)
#    And remove the `if not os.path.exists(n64_core_path):` check for it.
#
# 2. For Docker, simplify `run.sh` to:
#    `#!/bin/sh`
#    `poetry run python virtual_controller.py`
#    This removes the need for `git ls-files` and `entr` in the container.
#    If you do this, you can remove `git` and `entr` from apt-get in Dockerfile.

echo "Starting application via run.sh..."
# This assumes run.sh is in the WORKDIR /home/$USERNAME/app
./run.sh

# Clean up Xvfb when the main application exits
echo "Application finished. Cleaning up Xvfb..."
kill $XVFB_PID
wait $XVFB_PID || true # Wait, but don't fail if Xvfb is already gone
echo "Exiting entrypoint."
