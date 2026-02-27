---
icon: material/cloud-upload
---

# Production Deployment

Deploy the DevRev MCP Server to Google Cloud Run for team-wide access with per-user authentication.

## Architecture

```
┌──────────────┐     HTTPS      ┌────────────────────┐     HTTPS     ┌────────────┐
│  AI Client   │ ──────────────▶│   Cloud Run        │ ────────────▶│  DevRev    │
│  (Augment,   │  Bearer Token  │   MCP Server       │  Per-user    │  API       │
│   Claude)    │                │   (auto-scaling)   │  PAT         │            │
└──────────────┘                └────────────────────┘              └────────────┘
```

## Authentication Modes

### Per-User PAT (Recommended)

**Mode**: `MCP_AUTH_MODE=devrev-pat`

Each user sends their own DevRev Personal Access Token as the Bearer token. The server validates it against the DevRev API and creates a per-request client.

**Benefits**:
- Individual audit trails
- No shared secrets
- Users can only access their own permissions
- Token revocation is per-user

**Client configuration**:
```json
{
  "mcpServers": {
    "devrev": {
      "type": "http",
      "url": "https://devrev-mcp-server-xxx.run.app/mcp",
      "headers": {
        "Authorization": "Bearer <your-devrev-personal-access-token>"
      }
    }
  }
}
```

### Static Token (Legacy)

**Mode**: `MCP_AUTH_MODE=static-token`

All users share a single `MCP_AUTH_TOKEN`. Not recommended for production.

## Prerequisites

1. **Google Cloud CLI** installed and configured
2. **Google Cloud project** with billing enabled
3. **APIs enabled**: Cloud Run, Cloud Build, Artifact Registry, Secret Manager

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

## Deployment Steps

### 1. Create Secrets

```bash
# DevRev API token (for stdio/testing fallback)
echo -n "$DEVREV_API_TOKEN" | gcloud secrets create devrev-api-token --data-file=-

# Grant Cloud Run access
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
COMPUTE_SA="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding devrev-api-token \
  --member=serviceAccount:$COMPUTE_SA \
  --role=roles/secretmanager.secretAccessor
```

### 2. Deploy with Cloud Build

```bash
gcloud builds submit --config deploy/cloudbuild.yaml
```

### 3. Test the Deployment

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe devrev-mcp-server \
  --region=us-central1 --format='value(status.url)')

# Health check (no auth required)
curl $SERVICE_URL/health

# MCP initialize (requires your DevRev PAT)
curl -X POST $SERVICE_URL/mcp/v1/initialize \
  -H "Authorization: Bearer <your-devrev-pat>" \
  -H "Content-Type: application/json" \
  -d '{
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "test", "version": "1.0.0"}
  }'
```

## Alternative Deployments

### Docker Compose

```bash
docker compose up -d
```

### Manual Docker

```bash
docker build -t devrev-mcp-server:latest .

docker run -p 8080:8080 \
  -e DEVREV_API_TOKEN="$DEVREV_API_TOKEN" \
  -e MCP_TRANSPORT=streamable-http \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8080 \
  devrev-mcp-server:latest
```

## Security

- **Bearer token authentication** on all MCP endpoints
- **Rate limiting** with configurable limits
- **DNS rebinding protection** for HTTP transports
- **Destructive tool gating** — delete operations disabled by default
- **Domain restrictions** via `MCP_AUTH_ALLOWED_DOMAINS`
- **Health endpoint** at `/health` (unauthenticated, for load balancers)

## Further Reading

- [deploy/README.md](https://github.com/mgmonteleone/py-dev-rev/blob/main/deploy/README.md) — Detailed deployment docs
- [Workload Identity Federation](https://github.com/mgmonteleone/py-dev-rev/blob/main/deploy/README.md#automated-deployments) — GitHub Actions CI/CD

