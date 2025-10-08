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

# Generate documentation for all workshop subprojects

echo "🚀 Generating documentation for all workshop subprojects..."

# Regular subprojects (full analysis)
SUBPROJECTS=(
  "adventure"
  "artifacts"
  "bricks"
  "chess"
  "cost"
  "data"
  "doodles"
  "factuality"
  "games"
  "history"
  "kundali"
  "podcast"
  "prisoner"
  "recap"
  "roast"
  "scripts"
  "utils"
  "wearable"
)

# Process regular subprojects
for project in "${SUBPROJECTS[@]}"; do
  if [ -d "../$project" ]; then
    if [ -f "../$project/README.md" ]; then
      echo ""
      echo "⏭️  Skipping $project (README.md already exists)"
    else
      echo ""
      echo "📝 Processing $project..."
      poetry run python generate-docs.py "../$project" || echo "❌ Failed to process $project (continuing...)"
    fi
  else
    echo "⚠️  Skipping $project (directory not found)"
  fi
done

# Special cases
# waker: notes-only
if [ -d "../waker" ]; then
  if [ -f "../waker/NOTES.md" ]; then
    echo ""
    echo "⏭️  Skipping waker (NOTES.md already exists)"
  else
    echo ""
    echo "🎮 Processing waker (NOTES-only)..."
    poetry run python generate-docs.py "../waker" --notes-only || echo "❌ Failed to process waker (continuing...)"
  fi
else
  echo "⚠️  Skipping waker (directory not found)"
fi

# tv: readme-only since it has comprehensive NOTES.md
if [ -d "../tv" ]; then
  if [ -f "../tv/README.md" ]; then
    echo ""
    echo "⏭️  Skipping tv (README.md already exists)"
  else
    echo ""
    echo "📺 Processing tv (README-only)..."
    poetry run python generate-docs.py "../tv" --readme-only || echo "❌ Failed to process tv (continuing...)"
  fi
else
  echo "⚠️  Skipping tv (directory not found)"
fi

echo ""
echo "🎉 All documentation generation complete!"
