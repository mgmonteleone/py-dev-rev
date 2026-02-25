# DevRev MCP Server - Cloud Run Deployment

This directory contains configuration files for deploying the DevRev MCP Server to Google Cloud Run with secure token-based authentication.

## Architecture

- **Container Registry**: Artifact Registry (preferred over Container Registry)
- **Deployment**: Cloud Run with `--allow-unauthenticated` for public access
- **Authentication**: Bearer token via `MCP_AUTH_TOKEN` secret
- **Secrets**: Google Secret Manager with Cloud Run runtime service account access
- **CI/CD**: GitHub Actions with Workload Identity Federation (WIF)

## Prerequisites

1. **Google Cloud CLI** installed and configured:
   ```bash
   gcloud --version
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable required APIs**:
   ```bash
   gcloud services enable \
     cloudbuild.googleapis.com \
     run.googleapis.com \
     artifactregistry.googleapis.com \
     secretmanager.googleapis.com \
     iamcredentials.googleapis.com
   ```

3. **Create Artifact Registry repository** (if not exists):
   ```bash
   gcloud artifacts repositories create devrev-mcp \
     --repository-format=docker \
     --location=us-central1 \
     --description="DevRev MCP Server Docker images"
   ```

4. **Get your project number** (needed for IAM):
   ```bash
   PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
   echo $PROJECT_NUMBER
   ```

## Setup: Create Secrets in Google Secret Manager

### 1. Create DevRev API Token Secret

```bash
# Create the secret (interactive)
gcloud secrets create devrev-api-token \
  --replication-policy=automatic \
  --data-file=-

# Or from environment variable
echo -n "$DEVREV_API_TOKEN" | gcloud secrets create devrev-api-token \
  --replication-policy=automatic \
  --data-file=-
```

### 2. Create MCP Auth Token Secret

```bash
# Create the secret (interactive)
gcloud secrets create mcp-auth-token \
  --replication-policy=automatic \
  --data-file=-

# Or from environment variable
echo -n "$MCP_AUTH_TOKEN" | gcloud secrets create mcp-auth-token \
  --replication-policy=automatic \
  --data-file=-
```

### 3. Grant Cloud Run Service Account Access to Secrets

```bash
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
COMPUTE_SA="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

# Grant access to devrev-api-token
gcloud secrets add-iam-policy-binding devrev-api-token \
  --member=serviceAccount:$COMPUTE_SA \
  --role=roles/secretmanager.secretAccessor

# Grant access to mcp-auth-token
gcloud secrets add-iam-policy-binding mcp-auth-token \
  --member=serviceAccount:$COMPUTE_SA \
  --role=roles/secretmanager.secretAccessor
```

## Deployment Methods

### Method 1: Deploy with Cloud Build (Recommended)

This method builds the Docker image and deploys to Cloud Run in one step:

```bash
# Deploy from the project root
gcloud builds submit \
  --config=deploy/cloudbuild.yaml \
  --substitutions=_REGION=us-central1

# Or with a version tag
gcloud builds submit \
  --config=deploy/cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_TAG_NAME=v1.2.3
```

### Method 2: Deploy with service.yaml

This method uses a declarative YAML configuration:

```bash
# First, update PROJECT_ID and PROJECT_NUMBER in service.yaml
sed -i "s/PROJECT_ID/$(gcloud config get-value project)/g" deploy/service.yaml
sed -i "s/PROJECT_NUMBER/$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')/g" deploy/service.yaml

# Deploy the service
gcloud run services replace deploy/service.yaml --region=us-central1
```

### Method 3: Manual Docker Build and Deploy

```bash
# Build the image
docker build -t gcr.io/$(gcloud config get-value project)/devrev-mcp-server:latest .

# Push to Container Registry
docker push gcr.io/$(gcloud config get-value project)/devrev-mcp-server:latest

# Deploy to Cloud Run
gcloud run deploy devrev-mcp-server \
  --image=gcr.io/$(gcloud config get-value project)/devrev-mcp-server:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=300s \
  --concurrency=80 \
  --set-env-vars=MCP_TRANSPORT=streamable-http,MCP_HOST=0.0.0.0,MCP_PORT=8080,MCP_LOG_FORMAT=json,MCP_LOG_LEVEL=INFO \
  --set-secrets=DEVREV_API_TOKEN=devrev-api-token:latest
```

## Setup: Configure GitHub Actions for Automated Deployment

### 1. Create Workload Identity Federation (WIF) Configuration

WIF allows GitHub Actions to authenticate to Google Cloud without storing JSON keys.

```bash
# Create a service account for GitHub Actions
gcloud iam service-accounts create github-actions-deployer \
  --display-name="GitHub Actions Cloud Run Deployer"

# Grant Cloud Build and Cloud Run permissions
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member=serviceAccount:github-actions-deployer@$(gcloud config get-value project).iam.gserviceaccount.com \
  --role=roles/cloudbuild.builds.editor

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member=serviceAccount:github-actions-deployer@$(gcloud config get-value project).iam.gserviceaccount.com \
  --role=roles/run.admin

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member=serviceAccount:github-actions-deployer@$(gcloud config get-value project).iam.gserviceaccount.com \
  --role=roles/iam.serviceAccountUser
```

### 2. Create Workload Identity Pool and Provider

```bash
PROJECT_ID=$(gcloud config get-value project)

# Create the workload identity pool
gcloud iam workload-identity-pools create github \
  --project=$PROJECT_ID \
  --location=global \
  --display-name="GitHub Actions"

# Create the workload identity provider
gcloud iam workload-identity-pools providers create-oidc github \
  --project=$PROJECT_ID \
  --location=global \
  --workload-identity-pool=github \
  --display-name="GitHub" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri=https://token.actions.githubusercontent.com

# Get the provider resource name
PROVIDER=$(gcloud iam workload-identity-pools providers describe github \
  --project=$PROJECT_ID \
  --location=global \
  --workload-identity-pool=github \
  --format='value(name)')
echo "Provider: $PROVIDER"
```

### 3. Configure Service Account Impersonation

```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
REPO_OWNER="mgmonteleone"  # Change to your GitHub username
REPO_NAME="py-dev-rev"

# Allow GitHub Actions to impersonate the service account
# Note: principalSet requires the GCP project NUMBER, not the project ID
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-deployer@$PROJECT_ID.iam.gserviceaccount.com \
  --project=$PROJECT_ID \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github/attribute.repository/$REPO_OWNER/$REPO_NAME"
```

### 4. Add GitHub Secrets

Add these secrets to your GitHub repository (Settings > Secrets and variables > Actions):

```
GCP_PROJECT_ID: <your-project-id>
GCP_REGION: us-central1
WIF_PROVIDER: <provider-resource-name-from-step-2>
WIF_SERVICE_ACCOUNT: github-actions-deployer@<project-id>.iam.gserviceaccount.com
```

## Verify Deployment

1. **Get the service URL**:
   ```bash
   gcloud run services describe devrev-mcp-server \
     --region=us-central1 \
     --format='value(status.url)'
   ```

2. **Test the health endpoint**:
   ```bash
   SERVICE_URL=$(gcloud run services describe devrev-mcp-server --region=us-central1 --format='value(status.url)')
   curl $SERVICE_URL/health
   ```

3. **Test MCP endpoint with authentication**:
   ```bash
   SERVICE_URL=$(gcloud run services describe devrev-mcp-server --region=us-central1 --format='value(status.url)')
   MCP_AUTH_TOKEN="your-mcp-auth-token"

   curl -X POST $SERVICE_URL/mcp/v1/initialize \
     -H "Authorization: Bearer $MCP_AUTH_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}'
   ```

4. **View logs**:
   ```bash
   gcloud run services logs read devrev-mcp-server --region=us-central1 --limit=50
   ```

## Configuration

### Environment Variables

The following environment variables are set in the deployment:

- `MCP_TRANSPORT=streamable-http` - Use HTTP transport for Cloud Run
- `MCP_HOST=0.0.0.0` - Bind to all interfaces
- `MCP_PORT=8080` - Cloud Run default port
- `MCP_LOG_FORMAT=json` - Structured logging for Cloud Logging
- `MCP_LOG_LEVEL=INFO` - Production log level

### Secrets from Secret Manager

- `DEVREV_API_TOKEN` - DevRev API token (mounted from Secret Manager)
- `MCP_AUTH_TOKEN` - Bearer token for MCP endpoint authentication (mounted from Secret Manager)

### Resource Limits

- **Memory**: 512Mi (sufficient for MCP server operations)
- **CPU**: 1 vCPU (adequate for concurrent requests)
- **Concurrency**: 80 requests per instance
- **Timeout**: 300s (5 minutes for long-running MCP sessions)
- **Auto-scaling**: 0-10 instances (scales to zero when idle)

### Customizing Deployment

Edit `deploy/cloudbuild.yaml` substitutions to customize:

```yaml
substitutions:
  _REGION: 'us-central1'           # GCP region
  _SERVICE_NAME: 'devrev-mcp-server'  # Cloud Run service name
  _REPO: 'devrev-mcp'              # Artifact Registry repository
  _IMAGE: 'devrev-mcp-server'      # Image name
  _CPU: '1'                        # CPU allocation
  _MEMORY: '512Mi'                 # Memory allocation
  _TAG_NAME: 'latest'              # Image tag (set by CI/CD)
```

## Cost Optimization

1. **Scale to zero**: With `min-instances=0`, the service scales to zero when idle, minimizing costs.

2. **Right-size resources**: Start with 512Mi/1 CPU and monitor. Adjust if needed:
   ```bash
   gcloud run services update devrev-mcp-server \
     --region=us-central1 \
     --memory=1Gi \
     --cpu=2
   ```

3. **Monitor usage**:
   ```bash
   # View metrics in Cloud Console
   gcloud run services describe devrev-mcp-server --region=us-central1
   ```

4. **Set budget alerts** in Google Cloud Console to track spending.

## Troubleshooting

### Container fails to start

Check logs for errors:
```bash
gcloud run services logs read devrev-mcp-server --region=us-central1 --limit=100
```

### Secret access denied

Ensure the compute service account has access:
```bash
gcloud secrets add-iam-policy-binding devrev-api-token \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### Health check failures

Verify the health endpoint is responding:
```bash
# Port-forward to test locally
gcloud run services proxy devrev-mcp-server --region=us-central1
curl http://localhost:8080/health
```

## Security Considerations

### Public Access with Bearer Token Authentication

The deployment uses `--allow-unauthenticated` for public HTTP access, but requires `MCP_AUTH_TOKEN` bearer token for MCP endpoint calls:

```bash
# Health endpoint (no auth required)
curl https://devrev-mcp-server-xxx.run.app/health

# MCP endpoint (requires bearer token)
curl -X POST https://devrev-mcp-server-xxx.run.app/mcp/v1/initialize \
  -H "Authorization: Bearer $MCP_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Secret Management Best Practices

1. **Secrets in Secret Manager**: Never commit secrets to Git
   - `devrev-api-token` - DevRev API credentials
   - `mcp-auth-token` - MCP bearer token

2. **Service Account Permissions**: Cloud Run runtime SA has minimal permissions
   - Only access to required secrets via IAM bindings
   - No direct access to other GCP resources

3. **Workload Identity Federation**: GitHub Actions uses WIF instead of JSON keys
   - No long-lived credentials stored in GitHub
   - Time-limited OIDC tokens for each deployment

### Network Security

1. **CORS**: Configure allowed origins via `MCP_CORS_ALLOWED_ORIGINS` environment variable.

2. **Rate limiting**: The server includes built-in rate limiting (120 RPM by default). Adjust via `MCP_RATE_LIMIT_RPM`.

3. **Cloud Run Security**:
   - Runs in isolated containers
   - Automatic HTTPS with managed certificates
   - DDoS protection via Google Cloud Armor (optional)

### Audit and Monitoring

1. **Cloud Logging**: All requests logged in JSON format
   ```bash
   gcloud run services logs read devrev-mcp-server --region=us-central1
   ```

2. **Cloud Monitoring**: Set up alerts for error rates, latency, etc.

3. **Secret Access Audit**: Monitor secret access in Cloud Audit Logs
   ```bash
   gcloud logging read "resource.type=secretmanager.googleapis.com" --limit=50
   ```

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [DevRev MCP Server Documentation](../README.md)

