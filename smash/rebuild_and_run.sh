#!/bin/bash
set -e

IMAGE_NAME="smashbot"
CONTAINER_NAME="smashbot-container"

echo "--- Stopping and removing existing container: $CONTAINER_NAME (if any) ---"
docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
echo "--- Done stopping/removing. ---"
echo

echo "--- Rebuilding Docker image: $IMAGE_NAME using tar to handle symlinks ---"
# Ensure you are in the project root when running this script
tar -czh --exclude='.git' --exclude='.venv' --exclude='__pycache__' . | docker build -t "$IMAGE_NAME" -
echo "--- Docker image rebuild complete. ---"
echo

echo "--- Running new container: $CONTAINER_NAME from image: $IMAGE_NAME ---"

docker run -it --rm \
  --device=/dev/uinput \
  -e GOOGLE_API_KEY \
  --name "$CONTAINER_NAME" "$IMAGE_NAME"

echo "--- Container $CONTAINER_NAME has exited. ---"
