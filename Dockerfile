# syntax=docker/dockerfile:1

# =============================================================================
# Builder Stage: Install dependencies and build the package
# =============================================================================
FROM python:3.11-slim AS builder

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy only dependency files first for better layer caching
COPY pyproject.toml ./
COPY README.md ./

# Copy source code
COPY src/ ./src/

# Install the package with MCP extras
RUN pip install --no-cache-dir ".[mcp]"

# =============================================================================
# Runtime Stage: Slim production image
# =============================================================================
FROM python:3.11-slim AS runtime

# Metadata labels
LABEL maintainer="Matthew G. Monteleone <matthewm@augmentcode.com>" \
      description="DevRev MCP Server - A Model Context Protocol server for the DevRev platform" \
      version="1.0.0" \
      org.opencontainers.image.source="https://github.com/mgmonteleone/py-dev-rev" \
      org.opencontainers.image.title="DevRev MCP Server" \
      org.opencontainers.image.description="Production-ready MCP server for DevRev API integration" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.licenses="MIT"

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/mcp/.local/bin:$PATH"

# Install runtime dependencies (curl for healthcheck)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash mcp && \
    mkdir -p /app && \
    chown -R mcp:mcp /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/devrev-mcp-server /usr/local/bin/devrev-mcp-server

# Switch to non-root user
USER mcp

# Expose the HTTP port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Set the entry point
ENTRYPOINT ["devrev-mcp-server"]

# Default command arguments
CMD ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8080"]

