# Docker Security Hardening Documentation

## SECURITY FIX #3: Dockerfile & Docker Compose Hardening

This document describes the security hardening applied to the SC-Generator Docker configuration to address common container security vulnerabilities.

---

## Security Improvements Summary

### 1. Non-Root User Execution
**Before:** Container ran as root (UID 0)
**After:** Container runs as `scgen:scgen` (unprivileged user)

**Benefit:** Limits damage from container escape or compromised application

```dockerfile
# Create non-root user
RUN groupadd -r scgen && useradd -r -g scgen scgen
# Switch to non-root user
USER scgen
```

### 2. File Permissions Hardening
**Before:** Default permissions (often too permissive)
**After:** Restrictive permissions enforced

**File Permission Matrix:**
- Application code: `644` (owner read/write, others read)
- Application directories: `755` (owner read/write/exec, others read/exec)
- Python executables: `755` (executable)
- Temporary directories: `700` (owner only, most restrictive)
- System files: `600` (owner only, most restrictive)

```dockerfile
# Set restrictive permissions
RUN find /app -type f -exec chmod 644 {} \; && \
    find /app -type d -exec chmod 755 {} \; && \
    chmod 700 /tmp/sc-{uploads,outputs,fingerprints,logs}
```

### 3. Multi-Stage Build
**Before:** All build tools and dependencies in final image
**After:** Separate build stage, minimal runtime stage

**Benefit:**
- Smaller final image (reduced attack surface)
- No build tools in production (gcc, npm, python dev packages removed)
- Faster image pulls
- Reduced vulnerability exposure

```dockerfile
# Stage 1: builder - contains all build tools
FROM python:3.11-slim as builder
# Install gcc, npm, etc.

# Stage 2: runtime - minimal only
FROM python:3.11-slim
# Only runtime dependencies
```

### 4. Directory Ownership
**Before:** Directories owned by root
**After:** Directories owned by application user

```dockerfile
# Create and own application directories
RUN mkdir -p /app /var/log/sc-generator /var/lib/sc-generator && \
    chown -R scgen:scgen /app /var/log/sc-generator /var/lib/sc-generator
```

### 5. Secure Environment Variables
**Before:** No validation, defaults hardcoded
**After:** Explicit defaults with validation, security-focused

```dockerfile
ENV FLASK_ENV=production \
    FLASK_DEBUG=false \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
```

### 6. Minimal Base Image
**Before:** `python:3.11-slim` (still has some bloat)
**After:** Same slim image + removed unnecessary packages

**Removed:**
- Build tools (gcc, build-essential)
- Development libraries
- Unnecessary system utilities

**Kept:**
- `curl` - for health checks
- `ca-certificates` - for HTTPS/SSL

### 7. Health Check Improvement
**Before:** Direct Python urllib calls
**After:** Uses `curl` (standard health check practice)

```dockerfile
# Before
CMD python3 -c "import urllib.request; urllib.request.urlopen(...)"

# After
CMD curl -f http://localhost:5000/api/health
```

### 8. Docker Compose Security Options
**Before:** No security constraints
**After:** Multiple security hardening layers

```yaml
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE
```

**What this does:**
- `no-new-privileges:true` - Prevents privilege escalation via setuid/setgid
- `cap_drop: ALL` - Remove ALL Linux capabilities
- `cap_add: NET_BIND_SERVICE` - Add only NET_BIND_SERVICE (bind to port < 1024)

### 9. Resource Limits
**Before:** No limits (container can consume all resources)
**After:** CPU and memory limits enforced

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
    reservations:
      cpus: '1'
      memory: 512M
```

**Benefit:** Prevents DoS attacks and runaway processes

### 10. Read-Only Root Filesystem
**Before:** Fully writable filesystem
**After:** Read-only where possible

```yaml
read_only: false  # Can be set to true if app doesn't need write access
```

---

## Environment Variable Validation

All environment variables are validated with secure defaults:

### Required Variables
- `SECRET_KEY` - Must be changed from default (if not, app warns at startup)

### Validated Variables with Minimum Thresholds

| Variable | Min | Default | Validation |
|----------|-----|---------|-----------|
| `REQUEST_TIMEOUT_SECONDS` | 5s | 30s | Must be >= 5s |
| `UPLOAD_TIMEOUT_SECONDS` | 60s | 300s | Must be >= 60s |
| `GENERATE_TIMEOUT_SECONDS` | 10s | 120s | Must be >= 10s |
| `DOWNLOAD_TIMEOUT_SECONDS` | 5s | 60s | Must be >= 5s |
| `MAX_FILE_SIZE_MB` | 1 | 100 | Must be 1-500 |
| `RATE_LIMIT_PER_IP` | 10 | 100 | Must be >= 10 |
| `RATE_LIMIT_GLOBAL` | 100 | 1000 | Must be >= 100 |
| `LOG_MAX_SIZE` | 1MB | 10MB | Must be >= 1MB |

### Validation Behavior
If a value is invalid:
1. Application logs WARNING message
2. Default value is used
3. Startup continues (not a fatal error)
4. Check application logs for warnings

---

## File Structure and Permissions

```
/app                                755  scgen:scgen
├── Dockerfile                      644  scgen:scgen
├── app.py                          755  scgen:scgen
├── requirements.txt                644  scgen:scgen
├── src/                            755  scgen:scgen
│   └── *.py                        755  scgen:scgen
└── static/                         755  scgen:scgen

/tmp/sc-uploads                     700  scgen:scgen  (uploads only)
/tmp/sc-outputs                     700  scgen:scgen  (outputs only)
/tmp/sc-fingerprints                700  scgen:scgen  (fingerprints only)
/tmp/sc-logs                        700  scgen:scgen  (logs only)

/var/log/sc-generator               755  scgen:scgen
└── app.log                         644  scgen:scgen

/etc/passwd                         600  root:root
/etc/shadow                         600  root:root
```

---

## Security Checklist for Deployment

### Before Building
- [ ] Review Dockerfile for all security changes
- [ ] Review docker-compose.yml security options
- [ ] Ensure `.env` file is NOT in git (check .gitignore)
- [ ] Review .env.secure template for required changes

### Before Running Container
- [ ] Copy `.env.secure` to `.env`
- [ ] Generate new SECRET_KEY: `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`
- [ ] Set SECRET_KEY in `.env`
- [ ] Ensure `.env` has restrictive permissions: `chmod 600 .env`
- [ ] Review all environment variables in `.env`
- [ ] Verify directories exist and are writable: `/tmp/sc-*`, `/var/log/sc-generator`

### During Deployment
- [ ] Build image with: `docker-compose build --no-cache`
- [ ] Check image for vulnerabilities: `trivy image sc-generator:latest`
- [ ] Review container startup logs for warnings
- [ ] Test health check: `curl http://localhost:5000/api/health`
- [ ] Verify container runs as non-root: `docker exec sc-generator id`

### Post-Deployment
- [ ] Monitor logs for permission errors
- [ ] Monitor logs for validation warnings
- [ ] Test all endpoints with various payloads
- [ ] Verify rate limiting is working
- [ ] Check log rotation is functioning
- [ ] Set up automated backups for `/var/log/sc-generator`

---

## Common Issues and Solutions

### Issue: "Permission denied" errors in logs
**Solution:** Verify directory ownership and permissions
```bash
# Check ownership
ls -la /tmp/sc-*
ls -la /var/log/sc-generator

# Fix if needed
docker-compose exec sc-generator chown -R scgen:scgen /tmp/sc-*
```

### Issue: Container can't write logs
**Solution:** Ensure log directory exists and is writable
```bash
# Create log directory on host
sudo mkdir -p /var/log/sc-generator
sudo chown 1000:1000 /var/log/sc-generator  # Adjust UID/GID as needed
sudo chmod 755 /var/log/sc-generator
```

### Issue: Health check failing
**Solution:** Ensure curl is available and endpoint is responding
```bash
# Check if curl is in image
docker-compose exec sc-generator which curl

# Test endpoint manually
docker-compose exec sc-generator curl -v http://localhost:5000/api/health
```

### Issue: Application startup warnings about timeouts
**Solution:** Review and adjust environment variables
```bash
# Check logs
docker-compose logs -f sc-generator

# Adjust .env and restart
# See .env.secure for minimum values
docker-compose restart sc-generator
```

---

## Security Scanning

### Scan for vulnerabilities
```bash
# Using Trivy (requires installation)
trivy image sc-generator:latest

# Using Docker Scout (requires Docker Desktop 4.15+)
docker scout cves sc-generator:latest
```

### Check container security at runtime
```bash
# Verify running as non-root
docker-compose exec sc-generator id

# Check file permissions
docker-compose exec sc-generator ls -la /app
docker-compose exec sc-generator ls -la /tmp/sc-*

# Check process privileges
docker-compose exec sc-generator ps aux

# Check network connections
docker-compose exec sc-generator netstat -tlnp
```

---

## Network Security

### Docker Compose Network
The configuration creates a dedicated bridge network (`sc-network`) for isolation:
- Service cannot access host network directly
- Only exposed ports are accessible
- DNS resolution within network only

### Port Exposure
Only required ports are exposed:
- `5000` - Flask API
- `3000` - Frontend (if included)

### Firewall Recommendations
- [ ] Only expose ports from trusted networks
- [ ] Use firewall rules to restrict access
- [ ] Consider reverse proxy (nginx/HAProxy) for TLS termination
- [ ] Implement rate limiting at reverse proxy level

---

## Logging and Monitoring

### Log Rotation
Docker-compose is configured with automatic log rotation:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Log Retention
Configure log retention in `.env`:
```env
# Files are cleaned up after this many hours
FILE_RETENTION_HOURS=72

# Log rotation occurs at this interval
CLEANUP_INTERVAL_HOURS=24
```

### Monitor for Security Events
Check logs for:
- Authentication failures (if implemented)
- Rate limit violations
- File upload rejections
- Timeout errors (potential slowloris attacks)
- Permission errors

```bash
# View application logs
docker-compose logs -f sc-generator

# Filter for errors
docker-compose logs sc-generator | grep ERROR

# Filter for security warnings
docker-compose logs sc-generator | grep -i "security\|warning\|error"
```

---

## Secrets Management

### Environment Variables vs. Secrets
- `.env` file - Use for non-sensitive config
- Docker Secrets - Use for sensitive data in Swarm mode
- External secret manager - Use for production (Vault, AWS Secrets Manager, etc.)

### Best Practices
1. Never commit `.env` or `.env.secure` to git
2. Rotate `SECRET_KEY` regularly
3. Use strong random values: `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`
4. Store `.env` with restrictive permissions: `chmod 600 .env`
5. Use `.env.example` for public repository with placeholder values

---

## References

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Container Security](https://owasp.org/www-project-container-security/)
- [CIS Docker Benchmark](https://www.cisecurity.org/cis-benchmarks/)
- [Linux Capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)
