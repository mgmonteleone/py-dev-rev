#!/bin/bash
# Validation script for DevRev MCP Server monitoring configuration
# 
# Usage: ./validate-config.sh [PROJECT_ID]
#
# This script validates:
# - GCP project access
# - Cloud Monitoring API enabled
# - Notification channels exist
# - Alert policies are valid
# - Dashboard JSON is valid

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get project ID from argument or gcloud config
PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No project ID specified and no default project configured${NC}"
    echo "Usage: $0 [PROJECT_ID]"
    exit 1
fi

echo "Validating monitoring configuration for project: $PROJECT_ID"
echo "=================================================="
echo ""

# Check gcloud authentication
echo -n "Checking gcloud authentication... "
if gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Check project access
echo -n "Checking project access... "
if gcloud projects describe "$PROJECT_ID" &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Cannot access project: $PROJECT_ID"
    exit 1
fi

# Check Cloud Monitoring API
echo -n "Checking Cloud Monitoring API... "
if gcloud services list --project="$PROJECT_ID" --filter="name:monitoring.googleapis.com" --format="value(name)" | grep -q monitoring; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC} Not enabled"
    echo "Enable with: gcloud services enable monitoring.googleapis.com --project=$PROJECT_ID"
fi

# Check notification channels
echo -n "Checking notification channels... "
CHANNEL_COUNT=$(gcloud alpha monitoring channels list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null | wc -l)
if [ "$CHANNEL_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Found $CHANNEL_COUNT channel(s)"
else
    echo -e "${YELLOW}⚠${NC} No channels configured"
    echo "Create channels with: gcloud alpha monitoring channels create --help"
fi

# Validate alert-policies.yaml
echo -n "Validating alert-policies.yaml... "
if [ -f "$SCRIPT_DIR/alert-policies.yaml" ]; then
    # Check for placeholder values
    if grep -q "NOTIFICATION_CHANNEL_ID" "$SCRIPT_DIR/alert-policies.yaml"; then
        echo -e "${YELLOW}⚠${NC} Contains placeholder NOTIFICATION_CHANNEL_ID"
    elif grep -q "PROJECT_ID" "$SCRIPT_DIR/alert-policies.yaml"; then
        echo -e "${YELLOW}⚠${NC} Contains placeholder PROJECT_ID"
    else
        echo -e "${GREEN}✓${NC}"
    fi
else
    echo -e "${RED}✗${NC} File not found"
fi

# Validate dashboard.json
echo -n "Validating dashboard.json... "
if [ -f "$SCRIPT_DIR/dashboard.json" ]; then
    if python3 -m json.tool "$SCRIPT_DIR/dashboard.json" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Valid JSON"
    else
        echo -e "${RED}✗${NC} Invalid JSON"
    fi
else
    echo -e "${RED}✗${NC} File not found"
fi

# Check for existing alert policies
echo -n "Checking existing alert policies... "
POLICY_COUNT=$(gcloud alpha monitoring policies list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null | wc -l)
echo "Found $POLICY_COUNT existing policy(ies)"

# Check for existing dashboards
echo -n "Checking existing dashboards... "
DASHBOARD_COUNT=$(gcloud monitoring dashboards list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null | wc -l)
echo "Found $DASHBOARD_COUNT existing dashboard(s)"

echo ""
echo "=================================================="
echo "Validation complete!"
echo ""

# Summary and next steps
if grep -q "NOTIFICATION_CHANNEL_ID\|PROJECT_ID" "$SCRIPT_DIR/alert-policies.yaml" 2>/dev/null; then
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Replace placeholders in alert-policies.yaml:"
    echo "   - PROJECT_ID: $PROJECT_ID"
    echo "   - NOTIFICATION_CHANNEL_ID: (get from 'gcloud alpha monitoring channels list')"
    echo ""
fi

if [ "$CHANNEL_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}Create notification channels:${NC}"
    echo "gcloud alpha monitoring channels create \\"
    echo "  --display-name='DevRev Alerts' \\"
    echo "  --type=email \\"
    echo "  --channel-labels=email_address=alerts@example.com"
    echo ""
fi

echo -e "${GREEN}To apply configuration:${NC}"
echo "1. Apply alert policies:"
echo "   gcloud alpha monitoring policies create --policy-from-file=alert-policies.yaml"
echo ""
echo "2. Import dashboard:"
echo "   gcloud monitoring dashboards create --config-from-file=dashboard.json"
echo ""

