# Deploying Learning App to Google Cloud Run

This guide walks you through deploying the Pedagogical Concept Graph learning app to Google Cloud Run.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Enable required APIs:**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

4. **Google API Key** with Gemini API access

## Step 1: Enable Next.js Standalone Build

Update `next.config.ts` to enable standalone output:

```typescript
const nextConfig: NextConfig = {
  output: 'standalone', // Add this line
  // ... rest of config
};
```

## Step 2: Build and Push Docker Image

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export APP_NAME="learning-app"

# Build the image using Cloud Build (recommended)
gcloud builds submit --tag gcr.io/$PROJECT_ID/$APP_NAME

# Alternative: Build locally and push
# docker build -t gcr.io/$PROJECT_ID/$APP_NAME .
# docker push gcr.io/$PROJECT_ID/$APP_NAME
```

## Step 3: Deploy to Cloud Run

```bash
gcloud run deploy $APP_NAME \
  --image gcr.io/$PROJECT_ID/$APP_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="your-gemini-api-key-here" \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0
```

## Step 4: Get Your App URL

```bash
gcloud run services describe $APP_NAME --region $REGION --format 'value(status.url)'
```

The output will be your public URL: `https://learning-app-xxxxx.run.app`

## Environment Variables

Set these in the Cloud Run console or via CLI:

- `GOOGLE_API_KEY` - Your Gemini API key (required)

## Updating the Deployment

After making code changes:

```bash
# Rebuild and redeploy in one command
gcloud builds submit --tag gcr.io/$PROJECT_ID/$APP_NAME && \
gcloud run deploy $APP_NAME \
  --image gcr.io/$PROJECT_ID/$APP_NAME \
  --region $REGION \
  --platform managed
```

## Cost Estimation

- **Free tier**: 2 million requests/month, 180,000 vCPU-seconds
- **After free tier**: ~$0.10 per 1M requests
- **With minimal traffic**: Expect $0-5/month

Cloud Run scales to zero, so you only pay when someone is using the app!

## Troubleshooting

### Check logs
```bash
gcloud run services logs read $APP_NAME --region $REGION
```

### Test container locally
```bash
docker build -t learning-app-test .
docker run -p 3000:3000 -e GOOGLE_API_KEY="your-key" learning-app-test
# Visit http://localhost:3000
```

### Common issues

1. **"Module not found"**: Ensure all dependencies are in `package.json` (not just devDependencies for runtime deps)
2. **API key errors**: Double-check the env var name matches what's in your code (`GOOGLE_API_KEY`)
3. **Build timeouts**: Increase Cloud Build timeout: `--timeout=20m`

## Security Notes

- ✅ API key is set as environment variable (not in code)
- ✅ Container runs as non-root user (nextjs)
- ✅ Embeddings are read-only (baked into image)
- ⚠️ App is public by default (add auth if needed for private use)

## Next Steps

- Set up CI/CD with Cloud Build triggers
- Add custom domain with Cloud Run domain mapping
- Enable Cloud CDN for faster global access
- Add authentication if needed (Firebase Auth, Identity Platform)

---

**Ready to share with Peter!** 🚀 Just send him the Cloud Run URL.
