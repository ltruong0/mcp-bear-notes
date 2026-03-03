# Multi-stage build for MCP Bear Notes Server
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src /app/src

# Create directory for Bear database mount
RUN mkdir -p /bear-data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Add metadata
LABEL maintainer="Lee Truong"
LABEL description="MCP Server for Bear Notes integration"
LABEL version="0.1.0"

# Run the MCP server
CMD ["python", "-m", "mcp_bear_notes.server"]