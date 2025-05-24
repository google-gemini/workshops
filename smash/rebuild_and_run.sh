#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

IMAGE_NAME="smashbot"
CONTAINER_NAME="smashbot-container"

# 1. Stop and remove any existing container with the same name
echo "--- Stopping and removing existing container: $CONTAINER_NAME (if any) ---"
docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true # Suppress error if container doesn't exist
docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true   # Suppress error if container doesn't exist
echo "--- Done stopping/removing. ---"
echo

# 2. Rebuild the Docker image
echo "--- Rebuilding Docker image: $IMAGE_NAME ---"
docker build -t "$IMAGE_NAME" .
echo "--- Docker image rebuild complete. ---"
echo

# 3. Run the new container
echo "--- Running new container: $CONTAINER_NAME from image: $IMAGE_NAME ---"
# -it: Interactive TTY
# --rm: Automatically remove the container when it exits
# --device=/dev/uinput: Grant access to the uinput device
# --name: Assign a specific name to the container for easy management
# You might need --privileged if --device=/dev/uinput isn't sufficient,
# or if you encounter other permission issues inside the container.
# Use --privileged with caution.
docker run -it --rm --device=/dev/uinput --name "$CONTAINER_NAME" "$IMAGE_NAME"

echo "--- Container $CONTAINER_NAME has exited. ---"
