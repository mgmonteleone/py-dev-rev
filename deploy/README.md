# DevRev MCP Server - Cloud Run Deployment

This directory contains configuration files for deploying the DevRev MCP Server to Google Cloud Run.

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
     containerregistry.googleapis.com \
     secretmanager.googleapis.com
   ```

3. **Create the DevRev API token secret**:
   ```bash
   # Create the secret
   echo -n "your-devrev-api-token" | gcloud secrets create devrev-api-token \
     --data-file=- \
     --replication-policy=automatic

   # Grant Cloud Run access to the secret
   gcloud secrets add-iam-policy-binding devrev-api-token \
     --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
     --role=roles/secretmanager.secretAccessor
   ```

4. **Create a Dockerfile** in the project root (if not already present):
   ```dockerfile
   FROM python:3.12-slim

   WORKDIR /app

   # Install dependencies
   COPY pyproject.toml uv.lock ./
   RUN pip install --no-cache-dir -e ".[mcp]"

   # Copy application code
   COPY src/ ./src/

   # Expose port
   EXPOSE 8080

   # Run the MCP server
   CMD ["devrev-mcp-server", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8080"]
   ```

## Deployment Methods

### Method 1: Deploy with Cloud Build (Recommended)

This method builds the Docker image and deploys to Cloud Run in one step:

```bash
# Deploy from the project root
gcloud builds submit \
  --config=deploy/cloudbuild.yaml \
  --substitutions=_REGION=us-central1

# Or specify a different region
gcloud builds submit \
  --config=deploy/cloudbuild.yaml \
  --substitutions=_REGION=europe-west1
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

3. **View logs**:
   ```bash
   gcloud run services logs read devrev-mcp-server --region=us-central1 --limit=50
   ```

4. **Test MCP endpoint**:
   ```bash
   curl -X POST $SERVICE_URL/mcp/v1/initialize \
     -H "Content-Type: application/json" \
     -d '{"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}'
   ```

## Configuration

### Environment Variables

The following environment variables are set in the deployment:

- `MCP_TRANSPORT=streamable-http` - Use HTTP transport for Cloud Run
- `MCP_HOST=0.0.0.0` - Bind to all interfaces
- `MCP_PORT=8080` - Cloud Run default port
- `MCP_LOG_FORMAT=json` - Structured logging for Cloud Logging
- `MCP_LOG_LEVEL=INFO` - Production log level

### Resource Limits

- **Memory**: 512Mi (sufficient for MCP server operations)
- **CPU**: 1 vCPU (adequate for concurrent requests)
- **Concurrency**: 80 requests per instance
- **Timeout**: 300s (5 minutes for long-running MCP sessions)
- **Auto-scaling**: 0-10 instances (scales to zero when idle)

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

1. **Authentication**: The deployment uses `--allow-unauthenticated` for public access. For production, consider:
   - Removing `--allow-unauthenticated`
   - Using Cloud IAM for authentication
   - Adding MCP_AUTH_TOKEN for bearer token authentication

2. **CORS**: Configure allowed origins via `MCP_CORS_ALLOWED_ORIGINS` environment variable.

3. **Rate limiting**: The server includes built-in rate limiting (120 RPM by default). Adjust via `MCP_RATE_LIMIT_RPM`.

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [DevRev MCP Server Documentation](../README.md)

