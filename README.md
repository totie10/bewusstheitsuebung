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

1) Set the region (optional if always the same)
```cmd
set REGION=europe-west3
set GOOGLE_CLOUD_PROJECT=bewusstheitsuebung-api
```
2) Build and push using a simple 'latest' tag
```cmd
gcloud builds submit . --tag "%REGION%-docker.pkg.dev/%GOOGLE_CLOUD_PROJECT%/cr-repo/bewusst-api:latest"
```
✅ What this does:

Uses src/Dockerfile automatically (because the build context is src/).

Builds the container image and tags it as :latest.

Pushes the image to your Artifact Registry repository (cr-repo).

europe-west3-docker.pkg.dev/bewusstheitsuebung-api/cr-repo/bewusst-api:latest

## 6) Deploy
### 🔐 Create and Configure a Dedicated Service Account for Cloud Run

For better security, run your Cloud Run service under a **dedicated service account** with **least-privilege access** to your secrets.

#### 1️⃣ Create the Service Account

Run these commands in **Windows CMD** (or PowerShell):

```cmd
set PROJECT_ID=bewusstheitsuebung-api
set REGION=europe-west3
set RUN_SA=run-bewusst-sa

gcloud iam service-accounts create %RUN_SA% ^
  --display-name "Cloud Run SA for bewusst-api"
```
The resulting service account email will be: 
```cmd
%RUN_SA%@%PROJECT_ID%.iam.gserviceaccount.com
```

#### 2️⃣ Grant Secret Manager Access (Least Privilege)

Give this service account permission to read the GOOGLE_API_KEY secret.

```cmd
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY ^
  --member="serviceAccount:%RUN_SA%@%PROJECT_ID%.iam.gserviceaccount.com" ^
  --role="roles/secretmanager.secretAccessor"
```

✅ What this does:

Grants roles/secretmanager.secretAccessor only for the GOOGLE_API_KEY secret.

Ensures your Cloud Run service can read the secret at runtime.

Reduces blast radius by avoiding overly broad project-wide permissions.

#### Deploy
```cmd
gcloud run deploy bewusst-api --image "%REGION%-docker.pkg.dev/%GOOGLE_CLOUD_PROJECT%/cr-repo/bewusst-api:latest" --region %REGION% --no-allow-unauthenticated --service-account "%RUN_SA%@%PROJECT_ID%.iam.gserviceaccount.com" --set-secrets GOOGLE_API_KEY=GOOGLE_API_KEY:latest --set-env-vars ALLOW_ORIGINS="https://www.bewusstheitsuebung.de" --set-env-vars ALLOW_HOSTS="www.bewusstheitsuebung.de" --set-env-vars ENABLE_SECURITY_HEADERS=true --set-env-vars HSTS_MAX_AGE=31536000,HSTS_INCLUDE_SUBDOMAINS=true,HSTS_PRELOAD=false --set-env-vars REFERRER_POLICY="no-referrer" --set-env-vars PERMISSIONS_POLICY="geolocation=(), microphone=(), camera=(), payment=()" --set-env-vars X_FRAME_OPTIONS=DENY --set-env-vars CONTENT_SECURITY_POLICY="default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none';" --set-env-vars MAX_BODY_BYTES=200000 --set-env-vars CACHE_CONTROL="no-store"
```

### Debugging
List revisions:
```cmd
gcloud run revisions list --service bewusst-api --region europe-west3
```

See logs under:\
https://console.cloud.google.com/logs/viewer?project=bewusstheitsuebung-api&resource=cloud_run_revision/service_name/bewusst-api/revision_name/bewusst-api-00002-wdj

## 🔑 Local Authentication & Testing (Private Cloud Run)

Because our Cloud Run service is **not public** (`--no-allow-unauthenticated`),  
you must authenticate locally and attach a valid **OIDC token** to each request.

### 1️⃣ Authenticate Locally (Once Per Machine)

Run:

```cmd
gcloud auth application-default login
```

You will be redirected to a Google sign-in page.

✅ On the consent screen, select only:

☑ Google Cloud-Daten abrufen, bearbeiten, konfigurieren und löschen sowie die E-Mail-Adresse Ihres Google-Kontos sehen

This grants access to Google Cloud APIs and lets google-auth fetch identity tokens.
You do not need the checkbox for Cloud SQL unless your code uses Cloud SQL.

After login, verify:
```cmd
gcloud auth application-default print-access-token
```
You should see a long token string — this confirms ADC (Application Default Credentials) is set up.

### 2️⃣ Grant Yourself Invoker Access (Once)
```cmd
gcloud run services add-iam-policy-binding bewusst-api \
  --region europe-west3 \
  --member="user:YOUR_EMAIL" \
  --role="roles/run.invoker"
```
