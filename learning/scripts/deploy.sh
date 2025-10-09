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

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project)}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="learning"
IMAGE_TAG="${1:-latest}"
REPOSITORY="learning"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for required API key
if [ -z "${GOOGLE_API_KEY}" ]; then
  echo -e "${YELLOW}⚠️  Warning: GOOGLE_API_KEY not set${NC}"
  echo "Export it before deploying:"
  echo "  export GOOGLE_API_KEY='your-key-here'"
  echo ""
  read -p "Continue anyway? (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

echo -e "${BLUE}🚀 Deploying learning app to Cloud Run${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Project: ${PROJECT_ID}"
echo -e "  Region: ${REGION}"
echo -e "  Service: ${SERVICE_NAME}"
echo -e "  Image Tag: ${IMAGE_TAG}"
echo ""

# Verify we're in the right directory
if [ ! -f "package.json" ]; then
  echo "❌ Error: Must run from the learning directory"
  exit 1
fi

# Create Artifact Registry repository if it doesn't exist
echo -e "${YELLOW}📦 Ensuring Artifact Registry repository exists...${NC}"
if ! gcloud artifacts repositories describe "${REPOSITORY}" \
  --location="${REGION}" \
  --project="${PROJECT_ID}" &>/dev/null; then
  echo "  Creating repository ${REPOSITORY}..."
  gcloud artifacts repositories create "${REPOSITORY}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="Docker repository for learning app" \
    --project="${PROJECT_ID}"
else
  echo "  Repository already exists ✓"
fi

# Build and push image using Cloud Build
IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:${IMAGE_TAG}"

echo ""
echo -e "${YELLOW}🏗️  Building and pushing Docker image...${NC}"
gcloud builds submit \
  --tag="${IMAGE_URL}" \
  --project="${PROJECT_ID}" \
  .

echo ""
echo -e "${YELLOW}☁️  Deploying to Cloud Run...${NC}"
gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE_URL}" \
  --region="${REGION}" \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=300 \
  --set-env-vars="NODE_ENV=production,GOOGLE_API_KEY=${GOOGLE_API_KEY}" \
  --project="${PROJECT_ID}"

# Get the service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --format='value(status.url)')

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Service URL: ${SERVICE_URL}"
echo ""
echo -e "Test your deployment:"
echo -e "  ${BLUE}curl ${SERVICE_URL}${NC}"
echo ""
