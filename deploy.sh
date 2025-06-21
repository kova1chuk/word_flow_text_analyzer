#!/bin/bash

# Deploy script for Cloud Run
# Usage: ./deploy.sh [PROJECT_ID] [REGION]

set -e

PROJECT_ID=${1:-word-flow-text-analyzer}
REGION=${2:-europe-central2}
SERVICE_NAME="word-flow"
REPOSITORY="europe-central2-docker.pkg.dev/word-flow-text-analyzer/word-flow-repo"
IMAGE_NAME="$REPOSITORY/$SERVICE_NAME:latest"

echo "Deploying to Cloud Run..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "Repository: $REPOSITORY"
echo "Image: $IMAGE_NAME"

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "Error: Not authenticated with gcloud. Please run 'gcloud auth login'"
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Configure Docker for Artifact Registry
echo "Configuring Docker for Artifact Registry..."
gcloud auth configure-docker europe-central2-docker.pkg.dev

# Build and push the container
echo "Building and pushing container..."
docker build -t $IMAGE_NAME .
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --timeout 300 \
    --set-env-vars DEBUG=False,ALLOWED_HOSTS=*

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo "Deployment complete!"
echo "Service URL: $SERVICE_URL"
echo "API Endpoint: $SERVICE_URL/api/upload/" 