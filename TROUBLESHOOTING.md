# Troubleshooting Guide

## Artifact Registry Authentication Issues

### Error: "Unauthenticated request. Unauthenticated requests do not have permission"

This error occurs when the service account or user doesn't have the necessary permissions to upload artifacts to the Artifact Registry repository.

### Solution Steps:

#### 1. Run the Setup Script
```bash
./setup-permissions.sh
```

This script will:
- Enable required APIs
- Create the repository if it doesn't exist
- Grant proper permissions to your account
- Configure Docker for Artifact Registry

#### 2. Manual Permission Setup

If the script doesn't work, manually set up permissions:

```bash
# Set project
gcloud config set project word-flow-text-analyzer

# Enable APIs
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# Create repository (if it doesn't exist)
gcloud artifacts repositories create word-flow-repo \
  --repository-format=docker \
  --location=europe-central2 \
  --description="Word Flow Text Analyzer container repository"

# Grant permissions to your user account
gcloud artifacts repositories add-iam-policy-binding word-flow-repo \
  --location=europe-central2 \
  --member="user:$(gcloud auth list --filter=status:ACTIVE --format='value(account)')" \
  --role="roles/artifactregistry.writer"

# Configure Docker
gcloud auth configure-docker europe-central2-docker.pkg.dev --quiet
```

#### 3. GitHub Actions Service Account Setup

For GitHub Actions CI/CD, ensure your service account has the correct permissions:

1. **Create a service account** (if you haven't already):
   ```bash
   gcloud iam service-accounts create github-actions \
     --display-name="GitHub Actions Service Account"
   ```

2. **Grant necessary roles**:
   ```bash
   # Artifact Registry permissions
   gcloud projects add-iam-policy-binding word-flow-text-analyzer \
     --member="serviceAccount:github-actions@word-flow-text-analyzer.iam.gserviceaccount.com" \
     --role="roles/artifactregistry.writer"

   # Cloud Run permissions
   gcloud projects add-iam-policy-binding word-flow-text-analyzer \
     --member="serviceAccount:github-actions@word-flow-text-analyzer.iam.gserviceaccount.com" \
     --role="roles/run.admin"

   # Service Account permissions
   gcloud projects add-iam-policy-binding word-flow-text-analyzer \
     --member="serviceAccount:github-actions@word-flow-text-analyzer.iam.gserviceaccount.com" \
     --role="roles/iam.serviceAccountUser"
   ```

3. **Create and download the key**:
   ```bash
   gcloud iam service-accounts keys create ~/github-actions-key.json \
     --iam-account=github-actions@word-flow-text-analyzer.iam.gserviceaccount.com
   ```

4. **Add to GitHub Secrets**:
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add `GCP_SA_KEY` with the base64-encoded content of the key file:
     ```bash
     cat ~/github-actions-key.json | base64
     ```

#### 4. Verify Repository Access

Test if you can access the repository:

```bash
# List repositories
gcloud artifacts repositories list --location=europe-central2

# Describe the specific repository
gcloud artifacts repositories describe word-flow-repo --location=europe-central2
```

#### 5. Test Docker Push

Test if you can push to the repository:

```bash
# Build a test image
docker build -t europe-central2-docker.pkg.dev/word-flow-text-analyzer/word-flow-repo/word-flow:test .

# Push the image
docker push europe-central2-docker.pkg.dev/word-flow-text-analyzer/word-flow-repo/word-flow:test
```

### Common Issues and Solutions

#### Issue: "Repository does not exist"
**Solution**: Create the repository using the setup script or manual commands above.

#### Issue: "Permission denied"
**Solution**: Ensure your account has the `artifactregistry.writer` role.

#### Issue: "Docker authentication failed"
**Solution**: Run `gcloud auth configure-docker europe-central2-docker.pkg.dev --quiet`

#### Issue: "Service account key invalid"
**Solution**: Regenerate the service account key and update GitHub secrets.

### Required IAM Roles

For the service account to work properly, it needs these roles:
- `roles/artifactregistry.writer` - Upload images to Artifact Registry
- `roles/run.admin` - Deploy to Cloud Run
- `roles/iam.serviceAccountUser` - Use service accounts

### Testing the Setup

After setting up permissions, test the deployment:

```bash
# Manual deployment
./deploy.sh

# Or test individual steps
docker build -t europe-central2-docker.pkg.dev/word-flow-text-analyzer/word-flow-repo/word-flow:latest .
docker push europe-central2-docker.pkg.dev/word-flow-text-analyzer/word-flow-repo/word-flow:latest
```

### Getting Help

If you're still having issues:

1. Check the Google Cloud Console → IAM & Admin → IAM
2. Verify the service account has the correct roles
3. Check the Artifact Registry → Repositories section
4. Review Cloud Build logs for detailed error messages 