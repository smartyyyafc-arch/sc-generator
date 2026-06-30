# ---- Build stage ----
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a virtual env for clean copy
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and build Node assets
COPY . .
RUN npm ci && npm run build

# ---- Production stage ----
FROM python:3.11-slim

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code and built assets from builder
COPY --from=builder /build /app

# Create a non-root user and necessary directories
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser \
    && mkdir -p /tmp/sc-uploads /tmp/sc-outputs /tmp/sc-fingerprints /tmp/sc-logs \
    && chown -R appuser:appuser /app /tmp/sc-uploads /tmp/sc-outputs /tmp/sc-fingerprints /tmp/sc-logs

USER appuser

# Expose Flask port only
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Default command
CMD ["python3", "app.py"]
