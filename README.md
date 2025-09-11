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