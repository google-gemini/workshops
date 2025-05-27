set -euo pipefail # Exit on error, undefined variable, or pipe failure

IMAGE_NAME="smashbot"
CONTAINER_NAME="smashbot-container"

echo "--- Fetching latest LiveKit release tag from livekit/livekit ---"
# Fetch from livekit/livekit repository (the monorepo)
LIVEKIT_LATEST_TAG=$(curl -s https://api.github.com/repos/livekit/livekit/releases/latest \
  | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$LIVEKIT_LATEST_TAG" ]; then
  echo "Error: Failed to fetch the latest LiveKit tag from livekit/livekit."
  exit 1
fi
echo "--- Using LiveKit version: $LIVEKIT_LATEST_TAG ---"

LIVEKIT_VERSION_NUM=${LIVEKIT_LATEST_TAG#v} # Strip 'v' from tag (e.g., v1.8.4 -> 1.8.4)
# Corrected filename pattern based on your observation for livekit/livekit releases
LIVEKIT_FILENAME="livekit_${LIVEKIT_VERSION_NUM}_linux_amd64.tar.gz"
LIVEKIT_DOWNLOAD_URL="https://github.com/livekit/livekit/releases/download/${LIVEKIT_LATEST_TAG}/${LIVEKIT_FILENAME}"

echo "--- Downloading LiveKit: $LIVEKIT_FILENAME from $LIVEKIT_DOWNLOAD_URL ---"
# Download to the current directory (build context root)
curl -fSL "$LIVEKIT_DOWNLOAD_URL" -o "./${LIVEKIT_FILENAME}"
if [ $? -ne 0 ]; then
  echo "Error: Failed to download LiveKit tarball. Check URL and network."
  echo "Attempted URL: $LIVEKIT_DOWNLOAD_URL"
  # It's possible the 'latest' tag doesn't have this specific asset format,
  # or the asset name varies. Double-check releases on GitHub if this fails.
  rm -f "./${LIVEKIT_FILENAME}" # Clean up partial download
  exit 1
fi
echo "--- LiveKit download complete: ./${LIVEKIT_FILENAME} ---"
echo

echo "--- Stopping and removing existing container: $CONTAINER_NAME (if any) ---"
docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
echo "--- Done stopping/removing. ---"
echo

echo "--- Rebuilding Docker image: $IMAGE_NAME using tar to handle symlinks ---"
# The downloaded LIVEKIT_FILENAME is now part of the '.' context being tarred
tar -czh --exclude='.git' --exclude='.venv' --exclude='__pycache__' . \
  | docker build --build-arg LIVEKIT_TARBALL_ARG="${LIVEKIT_FILENAME}" -t "$IMAGE_NAME" -
echo "--- Docker image rebuild complete. ---"
echo

# Clean up the downloaded tarball from the host
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
  -p 1935:1935 \
  --name "$CONTAINER_NAME" "$IMAGE_NAME"

echo "--- Container $CONTAINER_NAME has exited. ---"
