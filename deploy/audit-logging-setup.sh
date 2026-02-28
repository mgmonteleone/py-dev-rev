#!/usr/bin/env bash
# Audit Logging Infrastructure Setup for DevRev MCP Server
# Sets up immutable audit log storage for compliance.
#
# Usage:
#   ./deploy/audit-logging-setup.sh --project=my-project
#   ./deploy/audit-logging-setup.sh --project=my-project --retention=730 --lock
#
# This script creates:
#   1. A GCS bucket with a retention policy for audit log storage
#   2. A Cloud Logging sink that exports audit events to the bucket
#   3. IAM bindings for the sink's service account
#
# The --lock flag enables WORM (Write Once Read Many) compliance by
# permanently locking the bucket retention policy. THIS IS IRREVERSIBLE.

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
REGION="${REGION:-us-central1}"
RETENTION_DAYS="${RETENTION_DAYS:-365}"
BUCKET_NAME=""
SINK_NAME="${SINK_NAME:-mcp-audit-log-sink}"
SERVICE_NAME="${SERVICE_NAME:-devrev-mcp-server}"
PROJECT_ID="${PROJECT_ID:-}"
LOCK_BUCKET=false

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Required:
  --project=PROJECT_ID          GCP project ID

Optional:
  --region=REGION               GCS bucket region (default: us-central1)
  --retention=DAYS              Retention period in days (default: 365)
  --bucket=BUCKET_NAME          GCS bucket name (default: PROJECT_ID-mcp-audit-logs)
  --sink=SINK_NAME              Cloud Logging sink name (default: mcp-audit-log-sink)
  --service=SERVICE_NAME        Cloud Run service name (default: devrev-mcp-server)
  --lock                        Lock bucket retention policy (IRREVERSIBLE!)
  -h, --help                    Show this help message

Examples:
  $0 --project=my-project
  $0 --project=my-project --retention=730 --lock

EOF
}

# Parse command line arguments
for arg in "$@"; do
    case $arg in
        --project=*)
            PROJECT_ID="${arg#*=}"
            shift
            ;;
        --region=*)
            REGION="${arg#*=}"
            shift
            ;;
        --retention=*)
            RETENTION_DAYS="${arg#*=}"
            shift
            ;;
        --bucket=*)
            BUCKET_NAME="${arg#*=}"
            shift
            ;;
        --sink=*)
            SINK_NAME="${arg#*=}"
            shift
            ;;
        --service=*)
            SERVICE_NAME="${arg#*=}"
            shift
            ;;
        --lock)
            LOCK_BUCKET=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $arg"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$PROJECT_ID" ]; then
    log_error "PROJECT_ID is required"
    show_usage
    exit 1
fi

# Set default bucket name if not provided
if [ -z "$BUCKET_NAME" ]; then
    BUCKET_NAME="${PROJECT_ID}-mcp-audit-logs"
fi

log_info "Starting audit logging infrastructure setup"
log_info "Project: $PROJECT_ID"
log_info "Region: $REGION"
log_info "Bucket: $BUCKET_NAME"
log_info "Retention: $RETENTION_DAYS days"
log_info "Sink: $SINK_NAME"
log_info "Service: $SERVICE_NAME"
log_info "Lock bucket: $LOCK_BUCKET"
echo ""

# Step 1: Create GCS bucket with retention policy
log_info "Step 1: Creating GCS bucket with retention policy..."
if gsutil ls -b "gs://$BUCKET_NAME" &>/dev/null; then
    log_warning "Bucket gs://$BUCKET_NAME already exists, skipping creation"
else
    log_info "Creating bucket gs://$BUCKET_NAME..."
    gsutil mb -p "$PROJECT_ID" -l "$REGION" -b on "gs://$BUCKET_NAME"
    log_success "Bucket created"
fi

# Set retention policy (skip if bucket is already locked)
LOCK_STATUS=$(gsutil retention get "gs://$BUCKET_NAME" 2>/dev/null | grep -i "Locked" || echo "")
if echo "$LOCK_STATUS" | grep -qi "true"; then
    log_warning "Bucket retention policy is locked; skipping retention update"
else
    log_info "Setting retention policy to $RETENTION_DAYS days..."
    gsutil retention set "${RETENTION_DAYS}d" "gs://$BUCKET_NAME"
    log_success "Retention policy set"
fi

# Step 2: Lock the bucket (optional, IRREVERSIBLE)
if [ "$LOCK_BUCKET" = true ]; then
    log_warning "Checking if bucket retention policy is already locked..."

    # Check if already locked
    LOCK_STATUS=$(gsutil retention get "gs://$BUCKET_NAME" | grep -i "Retention Policy Locked" || echo "")

    if echo "$LOCK_STATUS" | grep -qi "true"; then
        log_warning "Bucket retention policy is already locked"
    else
        echo ""
        log_warning "⚠️  WARNING: You are about to PERMANENTLY LOCK the bucket retention policy!"
        log_warning "This action is IRREVERSIBLE and enforces WORM (Write Once Read Many) compliance."
        log_warning "Once locked, you CANNOT:"
        log_warning "  - Reduce the retention period"
        log_warning "  - Delete the bucket until all objects expire"
        log_warning "  - Remove the retention policy"
        echo ""
        read -p "Type 'LOCK' to confirm: " confirmation

        if [ "$confirmation" = "LOCK" ]; then
            log_info "Locking bucket retention policy..."
            gsutil retention lock "gs://$BUCKET_NAME"
            log_success "Bucket retention policy locked (WORM compliance enabled)"
        else
            log_warning "Bucket lock cancelled"
        fi
    fi
else
    log_info "Skipping bucket lock (use --lock flag to enable WORM compliance)"
fi

# Step 3: Create Cloud Logging sink
log_info "Step 3: Creating Cloud Logging sink..."
if gcloud logging sinks describe "$SINK_NAME" --project="$PROJECT_ID" &>/dev/null; then
    log_warning "Sink $SINK_NAME already exists, skipping creation"
else
    log_info "Creating sink $SINK_NAME..."

    # Create the sink with filter for audit events
    gcloud logging sinks create "$SINK_NAME" \
        "storage.googleapis.com/$BUCKET_NAME" \
        --project="$PROJECT_ID" \
        --log-filter="resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\" AND jsonPayload.event_type=\"audit\""

    log_success "Sink created"
fi

# Step 4: Grant sink service account write access to bucket
log_info "Step 4: Granting sink service account write access..."

# Get the sink's writer identity
SINK_SA=$(gcloud logging sinks describe "$SINK_NAME" --project="$PROJECT_ID" --format='value(writerIdentity)')

if [ -z "$SINK_SA" ]; then
    log_error "Failed to get sink service account"
    exit 1
fi

log_info "Sink service account: $SINK_SA"

# Grant objectCreator role
log_info "Granting objectCreator role to sink service account..."
gsutil iam ch "${SINK_SA}:objectCreator" "gs://$BUCKET_NAME"
log_success "IAM binding created"

# Step 5: Enable Data Access Audit Logs
log_info "Step 5: Data Access Audit Logs configuration..."
echo ""
log_warning "MANUAL STEP REQUIRED:"
log_warning "Enable Data Access audit logs in Cloud Console for:"
log_warning "  1. Cloud Run API:"
log_warning "     IAM & Admin > Audit Logs > Cloud Run API"
log_warning "     ✓ Enable 'Data Read'"
log_warning "     ✓ Enable 'Data Write'"
log_warning ""
log_warning "  2. Secret Manager API:"
log_warning "     IAM & Admin > Audit Logs > Secret Manager API"
log_warning "     ✓ Enable 'Data Read'"
log_warning ""
log_warning "Or use gcloud to update the IAM policy:"
log_warning "  gcloud projects get-iam-policy $PROJECT_ID > policy.yaml"
log_warning "  # Edit policy.yaml to add auditConfigs"
log_warning "  gcloud projects set-iam-policy $PROJECT_ID policy.yaml"
echo ""

# Step 6: Verify setup
log_info "Step 6: Verifying setup..."
echo ""
log_info "=== Sink Configuration ==="
gcloud logging sinks describe "$SINK_NAME" --project="$PROJECT_ID"
echo ""
log_info "=== Bucket Configuration ==="
gsutil ls -L -b "gs://$BUCKET_NAME"
echo ""

log_success "✅ Audit logging infrastructure setup complete!"
echo ""
log_info "Summary:"
log_info "  • Bucket: gs://$BUCKET_NAME"
log_info "  • Retention: $RETENTION_DAYS days"
log_info "  • Sink: $SINK_NAME"
log_info "  • Service: $SERVICE_NAME"
log_info "  • Locked: $LOCK_BUCKET"
echo ""
log_info "Next steps:"
log_info "  1. Enable Data Access audit logs (see manual step above)"
log_info "  2. Deploy your Cloud Run service with audit logging enabled"
log_info "  3. Verify logs are being exported: gsutil ls gs://$BUCKET_NAME"
echo ""

