#!/bin/bash

# Install Google Cloud SDK on macOS
# Usage: ./install-gcloud.sh

echo "Installing Google Cloud SDK..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Google Cloud SDK
echo "Installing Google Cloud SDK via Homebrew..."
brew install google-cloud-sdk

# Initialize gcloud
echo "Initializing Google Cloud SDK..."
gcloud init

echo ""
echo "Google Cloud SDK installation complete!"
echo ""
echo "Next steps:"
echo "1. Run: ./setup-github-actions.sh"
echo "2. Add the generated secrets to GitHub"
echo "3. Push changes to trigger deployment"
echo ""
echo "Or follow the manual setup guide in MANUAL_SETUP.md" 