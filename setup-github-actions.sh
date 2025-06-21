#!/bin/bash

# Setup script for GitHub Actions service account
# Usage: ./setup-github-actions.sh

set -e

PROJECT_ID="word-flow-text-analyzer"
SERVICE_ACCOUNT_NAME="github-actions"
SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

echo "Setting up GitHub Actions service account for project: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "Error: Not authenticated with gcloud. Please run 'gcloud auth login'"
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable iam.googleapis.com

# Check if service account exists, create if it doesn't
echo "Checking if service account exists..."
if ! gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL 2>/dev/null; then
    echo "Service account does not exist. Creating..."
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="GitHub Actions Service Account" \
        --description="Service account for GitHub Actions CI/CD"
else
    echo "Service account already exists."
fi

# Grant necessary roles to the service account
echo "Granting necessary roles to service account..."

# Artifact Registry permissions
echo "  - Artifact Registry Writer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/artifactregistry.writer"

# Cloud Run permissions
echo "  - Cloud Run Admin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/run.admin"

# Service Account permissions
echo "  - Service Account User"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/iam.serviceAccountUser"

# Storage permissions (for Cloud Build)
echo "  - Storage Object Viewer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/storage.objectViewer"

# Create and download the service account key
echo "Creating service account key..."
KEY_FILE="github-actions-key.json"
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SERVICE_ACCOUNT_EMAIL

# Display the base64-encoded key for GitHub Secrets
echo ""
echo "=== GITHUB SECRETS SETUP ==="
echo ""
echo "1. Go to your GitHub repository:"
echo "   Settings → Secrets and variables → Actions"
echo ""
echo "2. Add these secrets:"
echo ""
echo "   GCP_PROJECT_ID:"
echo "   $PROJECT_ID"
echo ""
echo "   GCP_SA_KEY:"
echo "   $(cat $KEY_FILE | base64)"
echo ""
echo "3. The key file has been saved as: $KEY_FILE"
echo "   Keep this file secure and delete it after adding to GitHub Secrets."
echo ""
echo "=== VERIFICATION ==="
echo ""
echo "Testing service account permissions..."
gcloud auth activate-service-account --key-file=$KEY_FILE
gcloud config set project $PROJECT_ID

# Test repository access
echo "Testing Artifact Registry access..."
gcloud artifacts repositories list --location=europe-central2

echo ""
echo "Setup complete!"
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo "Key File: $KEY_FILE"
echo ""
echo "Remember to add the secrets to GitHub and delete the key file!" 