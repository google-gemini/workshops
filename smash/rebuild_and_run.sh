#!/bin/bash
set -euo pipefail

IMAGE_NAME="smashbot"
CONTAINER_NAME="smashbot-container"

echo "--- Fetching latest LiveKit release tag from livekit/livekit ---"
LIVEKIT_LATEST_TAG=$(curl -s https://api.github.com/repos/livekit/livekit/releases/latest \
  | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$LIVEKIT_LATEST_TAG" ]; then
  echo "Error: Failed to fetch the latest LiveKit tag from livekit/livekit."
  exit 1
fi
echo "--- Using LiveKit version: $LIVEKIT_LATEST_TAG ---"

LIVEKIT_VERSION_NUM=${LIVEKIT_LATEST_TAG#v}
LIVEKIT_FILENAME="livekit_${LIVEKIT_VERSION_NUM}_linux_amd64.tar.gz"
LIVEKIT_DOWNLOAD_URL="https://github.com/livekit/livekit/releases/download/${LIVEKIT_LATEST_TAG}/${LIVEKIT_FILENAME}"

echo "--- Downloading LiveKit: $LIVEKIT_FILENAME from $LIVEKIT_DOWNLOAD_URL ---"
curl -fSL "$LIVEKIT_DOWNLOAD_URL" -o "./${LIVEKIT_FILENAME}"
if [ $? -ne 0 ]; then
  echo "Error: Failed to download LiveKit tarball. Check URL and network."
  rm -f "./${LIVEKIT_FILENAME}"
  exit 1
fi
echo "--- LiveKit download complete. ---"
echo

echo "--- Stopping and removing existing container: $CONTAINER_NAME (if any) ---"
docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
echo "--- Done stopping/removing. ---"
echo

echo "--- Rebuilding Docker image: $IMAGE_NAME using tar to handle symlinks ---"
tar -czh --exclude='.git' --exclude='.venv' --exclude='__pycache__' . \
  | docker build --build-arg LIVEKIT_TARBALL_ARG="${LIVEKIT_FILENAME}" -t "$IMAGE_NAME" -
echo "--- Docker image rebuild complete. ---"
echo

echo "--- Cleaning up downloaded LiveKit tarball: ./${LIVEKIT_FILENAME} ---"
rm "./${LIVEKIT_FILENAME}"
echo "--- Cleanup complete. ---"
echo

echo "--- Running new container: $CONTAINER_NAME from image: $IMAGE_NAME ---"
if [ -z "${GOOGLE_API_KEY:-}" ] && grep -q 'os.environ.get("GOOGLE_API_KEY")' utils/model.py 2> /dev/null; then
  echo "Warning: GOOGLE_API_KEY might be needed by the Python app but is not set."
fi

docker run -it --rm \
  --device=/dev/uinput \
  -p 7881:7881 \
  -p 7880:7880/tcp \
  --name "$CONTAINER_NAME" "$IMAGE_NAME"

echo "--- Container $CONTAINER_NAME has exited. ---"
