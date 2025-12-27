# Deploy to Google Cloud Run

## Prerequisites

1. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
2. A Google Cloud project with billing enabled
3. Your `GEMINI_API_KEY` set in your local environment

## Quick Deploy

### 1. Set your API key locally (if not already set)

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 2. Authenticate with Google Cloud

```bash
gcloud auth login
```

View your projects:
```bash
gcloud projects list
```

Set your project:
```bash
gcloud config set project YOUR_PROJECT_ID
```

### 3. Enable required APIs

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

### 4. Deploy to Cloud Run

From the project root directory:

```bash
gcloud run deploy seizure-score-ai \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY"
```

This command:
- Builds the Docker image using Cloud Build
- Deploys to Cloud Run
- Automatically pulls `GEMINI_API_KEY` from your local environment

### 5. Access your app

After deployment, you'll see a URL like:
```
https://seizure-score-ai-xxxxx-uc.a.run.app
```

## Updating the Deployment

Just re-run the deploy command:

```bash
gcloud run deploy seizure-score-ai \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY"
```


