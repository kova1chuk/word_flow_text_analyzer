# Manual Setup Guide for GitHub Actions

Since you don't have `gcloud` installed locally, here's how to set up GitHub Actions authentication manually using the Google Cloud Console.

## Step 1: Create Service Account in Google Cloud Console

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/
   - Select your project: `word-flow-text-analyzer`

2. **Navigate to IAM & Admin:**
   - Go to: IAM & Admin → Service Accounts

3. **Create Service Account:**
   - Click "Create Service Account"
   - Name: `github-actions`
   - Description: `GitHub Actions Service Account`
   - Click "Create and Continue"

4. **Grant Roles:**
   - Click "Select a role" and add these roles one by one:
     - **Artifact Registry → Artifact Registry Writer**
     - **Cloud Run → Cloud Run Admin**
     - **IAM → Service Account User**
     - **Storage → Storage Object Viewer**
   - Click "Continue"
   - Click "Done"

## Step 2: Create Service Account Key

1. **Find your service account:**
   - In the Service Accounts list, click on `github-actions@word-flow-text-analyzer.iam.gserviceaccount.com`

2. **Create key:**
   - Go to the "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose "JSON" format
   - Click "Create"
   - The key file will download automatically

3. **Get base64-encoded key:**
   - Open the downloaded JSON file
   - Copy all the content
   - Go to: https://www.base64encode.org/
   - Paste the JSON content and encode it
   - Copy the base64-encoded result

## Step 3: Add GitHub Secrets

1. **Go to your GitHub repository:**
   - Visit your repository on GitHub
   - Go to: Settings → Secrets and variables → Actions

2. **Add secrets:**
   - Click "New repository secret"
   - Add `GCP_PROJECT_ID` with value: `word-flow-text-analyzer`
   - Click "New repository secret" again
   - Add `GCP_SA_KEY` with the base64-encoded key from Step 2

## Step 4: Create Artifact Registry Repository

1. **Go to Artifact Registry:**
   - In Google Cloud Console, go to: Artifact Registry → Repositories

2. **Create repository:**
   - Click "Create Repository"
   - Name: `word-flow-repo`
   - Format: `Docker`
   - Location: `europe-central2`
   - Description: `Word Flow Text Analyzer container repository`
   - Click "Create"

## Step 5: Enable Required APIs

1. **Go to APIs & Services:**
   - In Google Cloud Console, go to: APIs & Services → Library

2. **Enable these APIs:**
   - Search for and enable:
     - **Artifact Registry API**
     - **Cloud Build API**
     - **Cloud Run API**
     - **IAM API**

## Step 6: Test the Setup

1. **Push a change to trigger the workflow:**
   ```bash
   git add .
   git commit -m "Test GitHub Actions authentication"
   git push origin main
   ```

2. **Check GitHub Actions:**
   - Go to your repository → Actions tab
   - Monitor the workflow execution

## Alternative: Use Cloud Build Instead

If GitHub Actions continues to have issues, you can use Cloud Build directly:

1. **Install gcloud locally** (optional):
   ```bash
   # On macOS with Homebrew
   brew install google-cloud-sdk
   
   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate and deploy:**
   ```bash
   gcloud auth login
   gcloud config set project word-flow-text-analyzer
   gcloud builds submit --config cloudbuild.yaml .
   ```

## Troubleshooting

### If GitHub Actions still fails:

1. **Check the service account permissions:**
   - Go to IAM & Admin → IAM
   - Find your service account and verify it has the required roles

2. **Verify the repository exists:**
   - Go to Artifact Registry → Repositories
   - Ensure `word-flow-repo` exists in `europe-central2`

3. **Check the base64 encoding:**
   - Make sure the service account key was properly base64-encoded
   - The encoded string should be very long

4. **Try manual deployment:**
   - Use the `deploy.sh` script if you can install gcloud locally
   - Or use Cloud Build directly

### Common Issues:

- **"Permission denied"**: Service account missing required roles
- **"Repository not found"**: Repository not created in correct location
- **"Invalid key"**: Base64 encoding issue or wrong key format
- **"API not enabled"**: Required APIs not enabled in the project

## Next Steps

After setting up the authentication:

1. The GitHub Actions workflow should automatically deploy on pushes to main
2. You can monitor deployments in the Actions tab
3. The service will be available at the Cloud Run URL provided in the workflow output 