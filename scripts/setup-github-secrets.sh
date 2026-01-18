#!/bin/bash
# Setup GitHub Secrets for Integration Tests
# This script helps you configure GitHub Actions to run integration tests

set -e

echo "🔐 GitHub Secrets Setup for DevRev SDK"
echo "========================================"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo ""
    echo "Install it with:"
    echo "  macOS:   brew install gh"
    echo "  Linux:   See https://github.com/cli/cli#installation"
    echo "  Windows: See https://github.com/cli/cli#installation"
    echo ""
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo ""
    echo "Run: gh auth login"
    echo ""
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found."
    echo ""
    echo "Would you like to:"
    echo "  1. Enter API token manually"
    echo "  2. Exit and create .env file first"
    echo ""
    read -p "Choice (1 or 2): " choice
    
    if [ "$choice" = "2" ]; then
        echo ""
        echo "Create a .env file with:"
        echo "  cp .env.sample .env"
        echo "  # Edit .env and add your DEVREV_API_TOKEN"
        echo ""
        exit 0
    fi
    
    echo ""
    read -sp "Enter your DevRev API token: " api_token
    echo ""
else
    # Try to read from .env
    if grep -q "^DEVREV_API_TOKEN=" .env; then
        api_token=$(grep "^DEVREV_API_TOKEN=" .env | cut -d'=' -f2-)
        
        # Check if it's the placeholder
        if [ "$api_token" = "your-api-token-here" ] || [ -z "$api_token" ]; then
            echo "⚠️  .env file exists but DEVREV_API_TOKEN is not set."
            echo ""
            read -sp "Enter your DevRev API token: " api_token
            echo ""
        else
            echo "✅ Found DEVREV_API_TOKEN in .env file"
            echo ""
            read -p "Use this token for GitHub secret? (y/n): " use_env
            
            if [ "$use_env" != "y" ]; then
                echo ""
                read -sp "Enter your DevRev API token: " api_token
                echo ""
            fi
        fi
    else
        echo "⚠️  .env file exists but DEVREV_API_TOKEN is not set."
        echo ""
        read -sp "Enter your DevRev API token: " api_token
        echo ""
    fi
fi

# Validate token is not empty
if [ -z "$api_token" ]; then
    echo "❌ API token cannot be empty"
    exit 1
fi

# Validate token format (basic check - should start with "ey" for JWT)
if [[ ! "$api_token" =~ ^ey ]]; then
    echo "⚠️  Warning: Token doesn't look like a valid JWT (should start with 'ey')"
    read -p "Continue anyway? (y/n): " continue
    if [ "$continue" != "y" ]; then
        exit 1
    fi
fi

echo ""
echo "📤 Setting GitHub secret DEVREV_API_TOKEN..."

# Set the secret
if gh secret set DEVREV_API_TOKEN --body "$api_token"; then
    echo "✅ Secret DEVREV_API_TOKEN set successfully!"
else
    echo "❌ Failed to set secret"
    exit 1
fi

echo ""
echo "🔍 Verifying secret was set..."
if gh secret list | grep -q "DEVREV_API_TOKEN"; then
    echo "✅ Secret verified!"
else
    echo "❌ Secret not found in list"
    exit 1
fi

echo ""
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "  1. Push a commit to trigger CI workflow"
echo "  2. Check GitHub Actions tab to see integration tests run"
echo "  3. Integration tests will run automatically on:"
echo "     - Every push to main"
echo "     - Every pull request"
echo "     - Daily at 6 AM UTC (scheduled)"
echo ""
echo "To test locally:"
echo "  export DEVREV_API_TOKEN=\"\$api_token\""
echo "  pytest tests/integration/ -v -m integration"
echo ""

