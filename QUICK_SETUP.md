# Quick Setup Guide - Fix GitHub Actions Authentication

## The Problem

GitHub Actions is failing because it doesn't have proper authentication to Google Cloud.

## Solution: Manual Setup (No gcloud required)

### Step 1: Create Service Account (5 minutes)

1. **Go to Google Cloud Console:**
   - Visit: <https://console.cloud.google.com/>
   - Select project: `word-flow-text-analyzer`

2. **Create Service Account:**
   - Go to: IAM & Admin → Service Accounts
   - Click "Create Service Account"
   - Name: `github-actions`
   - Description: `GitHub Actions Service Account`
   - Click "Create and Continue"

3. **Grant Roles:**
   - Click "Select a role" and add these **one by one**:
     - `Artifact Registry → Artifact Registry Writer`
     - `Cloud Run → Cloud Run Admin`
     - `IAM → Service Account User`
     - `Storage → Storage Object Viewer`
   - Click "Continue" → "Done"

### Step 2: Create Service Account Key (2 minutes)

1. **Find your service account:**
   - In Service Accounts list, click: `github-actions@word-flow-text-analyzer.iam.gserviceaccount.com`

2. **Create key:**
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose "JSON" format
   - Click "Create"
   - **Save the downloaded file** (it's your private key!)

### Step 3: Get Base64 Key (1 minute)

1. **Open the downloaded JSON file**
2. **Copy ALL the content** (from `{` to `}`)
3. **Go to:** <https://www.base64encode.org/>
4. **Paste the JSON content** and click "Encode"
5. **Copy the base64 result** (very long string)

### Step 4: Add GitHub Secrets (2 minutes)

1. **Go to your GitHub repository:**
   - Visit: <https://github.com/kova1chuk/word_flow_text_analyzer>
   - Go to: Settings → Secrets and variables → Actions

2. **Add two secrets:**
   - Click "New repository secret"
   - Name: `GCP_PROJECT_ID`
   - Value: `word-flow-text-analyzer`
   - Click "Add secret"

   - Click "New repository secret" again
   - Name: `GCP_SA_KEY`
   - Value: (paste the base64-encoded key from Step 3)
   - Click "Add secret"

### Step 5: Create Artifact Registry Repository (2 minutes)

1. **Go to Artifact Registry:**
   - In Google Cloud Console: Artifact Registry → Repositories

2. **Create repository:**
   - Click "Create Repository"
   - Name: `word-flow-repo`
   - Format: `Docker`
   - Location: `europe-central2`
   - Click "Create"

### Step 6: Enable APIs (2 minutes)

1. **Go to APIs & Services:**
   - In Google Cloud Console: APIs & Services → Library

2. **Enable these APIs:**
   - Search and enable:
     - `Artifact Registry API`
     - `Cloud Build API`
     - `Cloud Run API`
     - `IAM API`

### Step 7: Test (1 minute)

1. **Push a change to trigger deployment:**

   ```bash
   git add .
   git commit -m "Test authentication fix"
   git push origin main
   ```

2. **Check GitHub Actions:**
   - Go to your repository → Actions tab
   - Watch the workflow run

## Expected Result

After completing these steps, the GitHub Actions workflow should:

- ✅ Build the Docker image
- ✅ Push to Artifact Registry
- ✅ Deploy to Cloud Run
- ✅ Show the service URL

## Troubleshooting

**If it still fails:**

1. Check that all 4 roles were added to the service account
2. Verify the base64 encoding is correct (should be very long)
3. Make sure the repository exists in `europe-central2`
4. Check that all APIs are enabled

**Need help?** Check the detailed guide in `MANUAL_SETUP.md`
