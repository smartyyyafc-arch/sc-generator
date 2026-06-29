# ============================================================================
# SC-Generator Dockerfile - Security Hardened
# SECURITY FIX #3: File permissions, non-root user, secure defaults
# ============================================================================

# Build stage
FROM python:3.11-slim as builder

WORKDIR /tmp/build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY requirements.txt .
COPY package*.json ./
COPY . .

# Build Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Build Node dependencies
RUN npm ci --only=production && npm run build

# ============================================================================
# Runtime stage - minimal production image
# ============================================================================

FROM python:3.11-slim

# Set environment variables with secure defaults
ENV FLASK_ENV=production \
    FLASK_DEBUG=false \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user and necessary directories before installing anything
RUN groupadd -r scgen && useradd -r -g scgen scgen

# Create application directories with proper permissions
RUN mkdir -p /app /var/log/sc-generator /var/lib/sc-generator && \
    chown -R scgen:scgen /app /var/log/sc-generator /var/lib/sc-generator && \
    chmod 755 /app /var/log/sc-generator /var/lib/sc-generator

# Create temporary work directories with restricted permissions
RUN mkdir -p /tmp/sc-uploads /tmp/sc-outputs /tmp/sc-fingerprints /tmp/sc-logs && \
    chown -R scgen:scgen /tmp/sc-{uploads,outputs,fingerprints,logs} && \
    chmod 700 /tmp/sc-{uploads,outputs,fingerprints,logs}

# Install minimal runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder --chown=scgen:scgen /root/.local /home/scgen/.local

# Copy application from builder
COPY --from=builder --chown=scgen:scgen /tmp/build . .

# Copy entrypoint script
COPY --chown=scgen:scgen docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod 755 /app/docker-entrypoint.sh

# Set Python path for user-installed packages
ENV PATH=/home/scgen/.local/bin:$PATH

# Verify file permissions are correct
RUN find /app -type f -exec chmod 644 {} \; && \
    find /app -type d -exec chmod 755 {} \; && \
    find /app -name "*.py" -exec chmod 755 {} \; && \
    chmod 755 /app/docker-entrypoint.sh

# Security hardening - set read-only root filesystem where possible
# (Some paths remain writable for application functionality)
RUN chmod 600 /etc/passwd /etc/shadow /etc/group /etc/gshadow 2>/dev/null || true

# Switch to non-root user
USER scgen

# Expose only required ports
EXPOSE 5000 3000

# Health check - uses curl instead of direct Python calls
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Set security labels
LABEL security.hardened="true" \
      security.non-root="true" \
      security.readonly-root-fs="false" \
      version="1.0" \
      description="SC-Generator with security hardening"

# Entrypoint script for validation and startup
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command
CMD ["python3", "app.py"]
