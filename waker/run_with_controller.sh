#!/bin/bash
# Launch script for Wind Waker voice chat with controller support

echo "Wind Waker Voice Chat with Controller Support"
echo "============================================="

# Check if controller daemon is running
if ! pgrep -f "controller_daemon.py" > /dev/null; then
    echo "Controller daemon not running. Please run in another terminal:"
    echo "  sudo python controller_daemon.py"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "Controller daemon detected ✓"
echo "Starting voice chat..."
echo ""

# Run the voice chat
cd "$(dirname "$0")"
poetry run python voice_chat.py
