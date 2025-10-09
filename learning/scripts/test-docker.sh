#!/bin/bash
set -e

# Configuration
IMAGE_NAME="learning-app"
IMAGE_TAG="${1:-local}"
CONTAINER_NAME="learning-test"
PORT="${PORT:-3000}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verify we're in the right directory
if [ ! -f "package.json" ]; then
  echo "❌ Error: Must run from the learning directory"
  exit 1
fi

# Function to build the image
build() {
  echo -e "${YELLOW}🏗️  Building Docker image...${NC}"
  docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
  echo -e "${GREEN}✅ Build complete!${NC}"
}

# Function to run the container
run() {
  # Stop any existing container
  if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}🛑 Stopping existing container...${NC}"
    docker stop "${CONTAINER_NAME}" >/dev/null 2>&1 || true
    docker rm "${CONTAINER_NAME}" >/dev/null 2>&1 || true
  fi

  echo -e "${BLUE}🚀 Starting container in foreground mode...${NC}"
  echo -e "  App URL: ${BLUE}http://localhost:${PORT}${NC}"
  echo -e "  Press ${YELLOW}Ctrl+C${NC} to stop"
  echo ""
  docker run --rm \
    --name "${CONTAINER_NAME}" \
    -p "${PORT}:3000" \
    -e NODE_ENV=production \
    "${IMAGE_NAME}:${IMAGE_TAG}"
}

# Function to stop the container
stop() {
  echo -e "${YELLOW}🛑 Stopping container...${NC}"
  docker stop "${CONTAINER_NAME}" 2>/dev/null || echo "Container not running"
  docker rm "${CONTAINER_NAME}" 2>/dev/null || echo "Container not found"
  echo -e "${GREEN}✅ Container stopped and removed${NC}"
}

# Function to show logs
logs() {
  docker logs -f "${CONTAINER_NAME}"
}

# Function to show status
status() {
  if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${GREEN}✅ Container is running${NC}"
    docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
  else
    echo -e "${YELLOW}⚠️  Container is not running${NC}"
  fi
}

# Main command handling
case "${2:-build-and-run}" in
  build)
    build
    ;;
  run)
    run
    ;;
  stop)
    stop
    ;;
  restart)
    stop
    build
    run
    ;;
  logs)
    logs
    ;;
  status)
    status
    ;;
  build-and-run)
    build
    run
    ;;
  *)
    echo "Usage: $0 [tag] [command]"
    echo ""
    echo "Commands:"
    echo "  build-and-run  Build and run container (default)"
    echo "  build          Build image only"
    echo "  run            Run existing image"
    echo "  stop           Stop and remove container"
    echo "  restart        Stop, rebuild, and run"
    echo "  logs           Show container logs"
    echo "  status         Show container status"
    echo ""
    echo "Examples:"
    echo "  $0                    # Build and run with 'local' tag"
    echo "  $0 v1.0.0 build       # Build with 'v1.0.0' tag"
    echo "  $0 local stop         # Stop the container"
    echo "  $0 local logs         # View logs"
    exit 1
    ;;
esac
