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
