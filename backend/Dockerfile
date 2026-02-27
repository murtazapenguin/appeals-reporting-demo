# Backend Dockerfile - FastAPI with Python 3.11
# Multi-stage build for optimized production images

# ============================================================================
# Base Stage - Common dependencies
# ============================================================================
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Runtime Stage - Production image
# ============================================================================
FROM base AS runtime

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch CPU version for the SDK
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install penguin-ai-sdk 0.1.7 (CPU version for containers)
COPY penguin_ai_sdk-0.1.7-py3-none-any.whl /tmp/
RUN pip install "/tmp/penguin_ai_sdk-0.1.7-py3-none-any.whl[cpu]"

# Copy application code
COPY . .

# Copy DocumentDB/RDS certificate for TLS connections
COPY global-bundle.pem /app/global-bundle.pem

# Create documents directory for uploads
RUN mkdir -p /app/documents

# Expose port
EXPOSE 8000

# Run the application with multiple workers for concurrency
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
