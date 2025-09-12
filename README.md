## Setup free-tier google API key

### 1. Create a free Google AI Studio account
1. Go to [Google AI Studio](https://aistudio.google.com).
2. Sign in with your Google account (free).
3. Navigate to [API Keys](https://aistudio.google.com/app/apikey) → **Create API key**.
4. Copy the key shown.

### 2. Store your API key locally (do not commit it!)
Set an environment variable called `GOOGLE_API_KEY`.

## 0) Prerequisites (One-Time Setup)

Before deploying this service to Google Cloud Run, make sure you have the following set up:

1. **Google Cloud Account & Project**
   - Create a [Google Cloud account](https://cloud.google.com/).
   - In the [Cloud Console](https://console.cloud.google.com/), create a new project.
   - Note the **PROJECT_ID** of the project (you will need it for deployment).

2. **Enable Billing**
   - Billing must be enabled on the project to use Cloud Run and API Gateway.
   - You can enable billing in the [Billing section of the Console](https://console.cloud.google.com/billing).

3. **Install the Google Cloud CLI**
   - [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install) for your platform.
   - After installation, open a new terminal (or the *Google Cloud SDK Shell* on Windows) and run:

   ```bash
   gcloud init
   gcloud auth login
   gcloud config set project PROJECT_ID
   gcloud config set run/region europe-west3   # Choose the region closest to your users
   ```
## 1) Enable all required APIs
```bash
   gcloud services enable run.googleapis.com apigateway.googleapis.com servicemanagement.googleapis.com servicecontrol.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```
## 2) Store Your Gemini API Key in Secret Manager

To keep your API key secure (and out of source control), store it in **Google Secret Manager**.  
This secret will later be mounted into the Cloud Run container as an environment variable.

### Create the Secret

```bash
  echo -n "YOUR_GOOGLE_API_KEY" | gcloud secrets create GOOGLE_API_KEY --data-file=-
```

## 3) Create an Artifact Registry repository for your image
```bash
    gcloud artifacts repositories create cr-repo \
      --repository-format=docker \
      --location=europe-west3 \
      --description="Containers for LLM API"
```

We’ll push the container here via Cloud Build.

## 4) Security Layer in FastAPI
```bash
gcloud run deploy bewusst-api \
  --image "$IMAGE" \
  --set-secrets GOOGLE_API_KEY=GOOGLE_API_KEY:latest \
  --set-env-vars ALLOW_ORIGINS="https://www.bewusstheitsuebung.de" \
  --set-env-vars ALLOW_HOSTS="www.bewusstheitsuebung.de" \
  --set-env-vars ENABLE_HTTPS_REDIRECT=true \
  --set-env-vars ENABLE_SECURITY_HEADERS=true \
  --set-env-vars HSTS_MAX_AGE=31536000,HSTS_INCLUDE_SUBDOMAINS=true,HSTS_PRELOAD=false \
  --set-env-vars REFERRER_POLICY="no-referrer" \
  --set-env-vars PERMISSIONS_POLICY="geolocation=(), microphone=(), camera=(), payment=()" \
  --set-env-vars X_FRAME_OPTIONS=DENY \
  --set-env-vars CONTENT_SECURITY_POLICY="default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none';" \
  --set-env-vars MAX_BODY_BYTES=200000 \
  --set-env-vars CACHE_CONTROL="no-store"
```

## 5) Build & Push with Cloud Build (Windows CMD, using `:latest` tag)

If you're on **Windows CMD** and want the simplest way to build and push your container, just use a `:latest` tag — no timestamps needed.

```cmd
:: 1) Set the region (optional if always the same)
set REGION=europe-west3
set GOOGLE_CLOUD_PROJECT=bewusstheitsuebung-api

:: 2) Build and push using a simple 'latest' tag
gcloud builds submit src --tag "%REGION%-docker.pkg.dev/%GOOGLE_CLOUD_PROJECT%/cr-repo/bewusst-api:latest"
```
✅ What this does:

Uses src/Dockerfile automatically (because the build context is src/).

Builds the container image and tags it as :latest.

Pushes the image to your Artifact Registry repository (cr-repo).