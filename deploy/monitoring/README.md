# DevRev MCP Server - Monitoring and Alerting

This directory contains Cloud Monitoring configurations for the DevRev MCP Server audit logging system.

## Files

- **`alert-policies.yaml`**: Alert policy definitions for critical events
- **`dashboard.json`**: Cloud Monitoring dashboard for visualizing audit data

## Prerequisites

1. **GCP Project with Cloud Monitoring enabled**
2. **Cloud Run service deployed** with audit logging enabled
3. **Notification channels configured** (email, Slack, PagerDuty, etc.)

## Setup Instructions

### 1. Create Notification Channels

Create notification channels for receiving alerts:

```bash
# Email notification
gcloud alpha monitoring channels create \
  --display-name="DevRev Alerts Email" \
  --type=email \
  --channel-labels=email_address=alerts@example.com

# Slack notification (requires Slack workspace integration)
gcloud alpha monitoring channels create \
  --display-name="DevRev Alerts Slack" \
  --type=slack \
  --channel-labels=channel_name=#devrev-alerts

# List channels to get IDs
gcloud alpha monitoring channels list
```

### 2. Configure Alert Policies

Edit `alert-policies.yaml` and replace placeholders:

- `PROJECT_ID`: Your GCP project ID
- `NOTIFICATION_CHANNEL_ID`: Channel ID from step 1

Then apply the policies:

```bash
# Apply all alert policies
gcloud alpha monitoring policies create \
  --policy-from-file=deploy/monitoring/alert-policies.yaml
```

### 3. Import Dashboard

Import the dashboard into Cloud Monitoring:

```bash
# Using gcloud (requires dashboard API)
gcloud monitoring dashboards create \
  --config-from-file=deploy/monitoring/dashboard.json

# Or manually:
# 1. Go to Cloud Console > Monitoring > Dashboards
# 2. Click "Create Dashboard"
# 3. Click "JSON" tab
# 4. Paste contents of dashboard.json
# 5. Click "Save"
```

## Alert Policies

### 1. High Auth Failure Rate

**Threshold**: >10 failed auth attempts in 5 minutes

**Indicates**:
- Brute force attack attempts
- Misconfigured credentials
- Expired tokens

**Response**:
1. Review audit logs for affected user/IP
2. Check credential validity
3. Consider IP blocking if attack detected

### 2. High Destructive Operation Rate

**Threshold**: >20 delete operations in 10 minutes

**Indicates**:
- Accidental bulk deletion
- Malicious activity
- Runaway automation

**Response**:
1. Review audit logs immediately
2. Identify user/service account
3. Verify intentionality
4. Pause service if unauthorized
5. Check backup availability

### 3. Elevated Error Rate

**Threshold**: Tool failure rate >20% over 5 minutes

**Indicates**:
- DevRev API connectivity issues
- Service degradation
- Permission problems
- Code bugs

**Response**:
1. Check DevRev API status
2. Review error messages
3. Verify permissions
4. Check recent deployments

## Dashboard Widgets

### 1. Authentication Success vs Failure Rate
Line chart showing auth events over time. Helps identify authentication issues.

### 2. Tool Invocations by Category
Stacked bar chart showing tool usage by category (read, write, delete, etc.). Helps understand usage patterns.

### 3. Top 10 Users by Request Volume
Scorecard showing most active users in the last hour. Helps identify heavy users or potential abuse.

### 4. Error Rate Over Time
Line chart comparing success vs failure rates. Helps identify service degradation.

### 5. Audit Events by Action Type
Pie chart showing distribution of audit actions. Helps understand overall system usage.

## Customization

### Adjusting Alert Thresholds

Edit `alert-policies.yaml` and modify `thresholdValue` in each policy:

```yaml
conditions:
  - displayName: "Auth failure count > 10 in 5 minutes"
    conditionThreshold:
      thresholdValue: 10  # Change this value
```

### Adding Custom Widgets

Edit `dashboard.json` and add new tiles to the `tiles` array. Use the Cloud Monitoring dashboard JSON schema.

### Filtering by Environment

Add environment labels to your Cloud Run service and filter in queries:

```
resource.type="cloud_run_revision"
resource.labels.service_name="devrev-mcp-server"
resource.labels.environment="production"
jsonPayload.event_type="audit"
```

## Querying Audit Logs

### Using Cloud Console

1. Go to **Logging > Logs Explorer**
2. Use these filters:

```
# All audit events
resource.type="cloud_run_revision"
jsonPayload.event_type="audit"

# Failed authentications
jsonPayload.action="auth_failure"

# Delete operations
jsonPayload.action="tool_invocation"
jsonPayload.tool.category="delete"

# Specific user activity
jsonPayload.user.email="user@example.com"
```

### Using gcloud

```bash
# Recent audit events
gcloud logging read "resource.type=cloud_run_revision AND jsonPayload.event_type=audit" \
  --limit=50 \
  --format=json

# Failed auth attempts
gcloud logging read "jsonPayload.action=auth_failure" \
  --limit=20 \
  --format=json
```

## Maintenance

- **Review alert thresholds monthly** based on actual usage patterns
- **Update notification channels** as team members change
- **Archive old logs** according to retention policy
- **Test alerts quarterly** to ensure proper notification delivery

## Troubleshooting

### Alerts Not Firing

1. Verify notification channels are active: `gcloud alpha monitoring channels list`
2. Check alert policy status: `gcloud alpha monitoring policies list`
3. Verify logs are being generated with correct structure
4. Check filter syntax in alert policies

### Dashboard Not Showing Data

1. Verify Cloud Run service is running and generating logs
2. Check log filter syntax in dashboard widgets
3. Ensure time range is appropriate (default: last 1 hour)
4. Verify audit logging is enabled in the MCP server

### Missing Audit Events

1. Check `MCP_AUDIT_LOG_ENABLED` environment variable is set to `true`
2. Verify Cloud Run service has logging permissions
3. Check for errors in Cloud Run logs
4. Ensure audit middleware is properly configured

