#!/bin/bash

# Setup script for Artifact Registry permissions
# Usage: ./setup-permissions.sh

set -e

PROJECT_ID="word-flow-text-analyzer"
REGION="europe-central2"
REPOSITORY="word-flow-repo"
SERVICE_ACCOUNT_EMAIL=""

echo "Setting up Artifact Registry permissions for project: $PROJECT_ID"
echo "Region: $REGION"
echo "Repository: $REPOSITORY"

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

# Check if repository exists, create if it doesn't
echo "Checking if repository exists..."
if ! gcloud artifacts repositories describe $REPOSITORY --location=$REGION 2>/dev/null; then
    echo "Repository does not exist. Creating..."
    gcloud artifacts repositories create $REPOSITORY \
        --repository-format=docker \
        --location=$REGION \
        --description="Word Flow Text Analyzer container repository"
else
    echo "Repository already exists."
fi

# Get the current user/service account
CURRENT_USER=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
echo "Current authenticated user: $CURRENT_USER"

# Grant Artifact Registry permissions to the current user
echo "Granting Artifact Registry permissions..."
gcloud artifacts repositories add-iam-policy-binding $REPOSITORY \
    --location=$REGION \
    --member="user:$CURRENT_USER" \
    --role="roles/artifactregistry.writer"

# If using a service account, also grant permissions to it
if [ ! -z "$SERVICE_ACCOUNT_EMAIL" ]; then
    echo "Granting permissions to service account: $SERVICE_ACCOUNT_EMAIL"
    gcloud artifacts repositories add-iam-policy-binding $REPOSITORY \
        --location=$REGION \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="roles/artifactregistry.writer"
fi

# Configure Docker for Artifact Registry
echo "Configuring Docker for Artifact Registry..."
gcloud auth configure-docker europe-central2-docker.pkg.dev --quiet

# Test repository access
echo "Testing repository access..."
gcloud artifacts repositories describe $REPOSITORY --location=$REGION

echo "Setup complete!"
echo "Repository URL: europe-central2-docker.pkg.dev/$PROJECT_ID/$REPOSITORY"
echo "You can now build and push images to this repository." 