# SC-Generator Docker Quick Start Guide

## Security Hardened Docker Setup

This guide provides quick commands to get SC-Generator running with all security hardening in place.

---

## Prerequisites

- Docker 20.10+
- Docker Compose 1.29+
- Python 3.8+ (for secret generation)
- curl (for health checks)

### Verify Prerequisites

```bash
docker --version          # Docker 20.10+
docker-compose --version  # Docker Compose 1.29+
python3 --version         # Python 3.8+
```

---

## 1. Generate Secrets

Generate a secure random SECRET_KEY:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Output example:**
```
aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX4yZ5aB6cD7eF8gH9iJ0k
```

Copy this value - you'll need it in the next step.

---

## 2. Configure Environment

### Copy template to .env

```bash
cp .env.secure .env
```

### Edit .env

```bash
nano .env  # or your preferred editor
```

**Update these critical values:**

1. **SECRET_KEY** (REQUIRED)
   ```bash
   # Find this line:
   SECRET_KEY=CHANGEME-USE_RANDOM_SECRET_key_value_here_min_32_chars
   
   # Replace with generated value:
   SECRET_KEY=aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX4yZ5aB6cD7eF8gH9iJ0k
   ```

2. **FLASK_ENV** (should already be production)
   ```bash
   FLASK_ENV=production
   ```

3. **FLASK_DEBUG** (should already be false)
   ```bash
   FLASK_DEBUG=false
   ```

4. **CORS_ORIGINS** (adjust for your domain)
   ```bash
   # For local development:
   CORS_ORIGINS=http://localhost:3000,http://localhost:8080
   
   # For production:
   CORS_ORIGINS=https://app.example.com,https://www.example.com
   ```

5. **LOG_LEVEL** (for production)
   ```bash
   LOG_LEVEL=INFO
   ```

### Secure the .env file

```bash
chmod 600 .env
ls -la .env  # Should show: -rw------- 
```

---

## 3. Create Required Directories

```bash
# Create storage directories
mkdir -p /tmp/sc-{uploads,outputs,fingerprints,logs}
mkdir -p /var/log/sc-generator

# Verify permissions (should be writable)
ls -la /tmp/sc-uploads
ls -la /var/log/sc-generator
```

---

## 4. Build Docker Image

```bash
# Build without cache (ensures latest dependencies)
docker-compose build --no-cache

# Verify build succeeded
docker images | grep sc-generator
```

Expected output shows image with ~300-400MB size.

---

## 5. Start Container

```bash
# Start in background
docker-compose up -d

# Watch startup logs (Ctrl+C to exit)
docker-compose logs -f sc-generator
```

**Expected startup output:**
```
[INFO] ==========================================
[INFO] SC-Generator Docker Entrypoint
[INFO] ==========================================
[INFO] Validating required environment variables...
[INFO] ✓ SECRET_KEY is valid (length: 60)
[INFO] Validating directory permissions...
[INFO] ✓ Directory writable: /tmp/sc-uploads
[INFO] ✓ Directory writable: /tmp/sc-outputs
[INFO] Validating timeout configuration...
[INFO] ✓ REQUEST_TIMEOUT_SECONDS: 30s
...
[INFO] ==========================================
[INFO] All validations passed!
[INFO] Starting application...
[INFO] ==========================================
 * Running on http://0.0.0.0:5000
```

---

## 6. Verify Container Status

```bash
# Check if container is running
docker-compose ps

# Should show: sc-generator ... Up (healthy)
```

### Verify Security Settings

```bash
# Verify running as non-root user
docker-compose exec sc-generator id
# Should output: uid=1000(scgen) gid=1000(scgen) groups=1000(scgen)

# Verify file permissions
docker-compose exec sc-generator ls -la /app
# All files should be owned by scgen:scgen

# Verify process privileges
docker-compose exec sc-generator ps aux
# Python process should run as scgen
```

---

## 7. Test Application

### Health Check

```bash
curl -v http://localhost:5000/api/health

# Expected response:
# HTTP/1.1 200 OK
# Content-Type: application/json
# {"status": "healthy"}
```

### Test Upload Endpoint

```bash
# Create test file
echo "test content" > test.txt

# Upload (adjust endpoint as needed)
curl -X POST -F "file=@test.txt" http://localhost:5000/api/upload

# Clean up
rm test.txt
```

### Test Rate Limiting

```bash
# Make 100 requests rapidly (adjust count as needed)
for i in {1..100}; do 
  curl -s http://localhost:5000/api/health > /dev/null
done

# If rate limit is 100 per minute, next request should fail
curl -v http://localhost:5000/api/health
# Should see: HTTP 429 Too Many Requests
```

---

## 8. View Logs

```bash
# Stream logs (real-time)
docker-compose logs -f sc-generator

# View last 100 lines
docker-compose logs --tail=100 sc-generator

# View logs from specific time
docker-compose logs --since 10m sc-generator

# Exit - Stop following: Ctrl+C
```

---

## Common Tasks

### Restart Container

```bash
docker-compose restart sc-generator
```

### Stop Container

```bash
docker-compose down
```

### Stop Container & Remove Volumes

```bash
docker-compose down -v
```

### Rebuild & Restart

```bash
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f sc-generator
```

### Execute Command in Container

```bash
docker-compose exec sc-generator <command>

# Examples:
docker-compose exec sc-generator python3 --version
docker-compose exec sc-generator ls -la /tmp/sc-uploads
docker-compose exec sc-generator df -h
```

### View Resource Usage

```bash
docker stats sc-generator

# Watch for 1 minute
docker stats --no-stream sc-generator
```

---

## Troubleshooting

### Container fails to start

**Check logs:**
```bash
docker-compose logs sc-generator | grep -i error
```

**Common issues:**
- `SECRET_KEY is not set` → Update .env with generated secret
- `Permission denied` → Run: `chmod 600 .env` and rebuild
- `Address already in use` → Port 5000 or 3000 already in use

### Health check failing

```bash
# Test endpoint manually
curl -v http://localhost:5000/api/health

# Check if curl is available in container
docker-compose exec sc-generator which curl

# Restart container
docker-compose restart sc-generator
```

### High CPU/Memory usage

```bash
# Check resource usage
docker stats sc-generator

# View application logs for errors
docker-compose logs sc-generator | grep ERROR

# Restart
docker-compose restart sc-generator
```

### Permission errors in logs

```bash
# Fix directory permissions
sudo chown -R 1000:1000 /tmp/sc-*

# Restart
docker-compose restart sc-generator
```

---

## Security Verification Checklist

Quick checklist to verify security hardening is in place:

- [ ] Container runs as non-root: `docker-compose exec sc-generator id`
- [ ] File permissions are restrictive: `docker-compose exec sc-generator ls -la /app`
- [ ] .env file is protected: `ls -la .env` (should be -rw-------)
- [ ] SECRET_KEY is set and changed: Check `.env` file
- [ ] FLASK_DEBUG is false: `grep FLASK_DEBUG .env`
- [ ] Logs show validation passed: `docker-compose logs sc-generator | grep "All validations passed"`

---

## Next Steps

1. **Read DOCKER_SECURITY.md** - Understand all security hardening details
2. **Review .env.secure** - See all available configuration options
3. **Follow DEPLOYMENT_CHECKLIST.md** - For production deployment
4. **Set up monitoring** - Configure log aggregation and alerting
5. **Configure backups** - Set up automated backups for data persistence

---

## Quick Reference

| Task | Command |
|------|---------|
| Generate SECRET_KEY | `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` |
| Copy config template | `cp .env.secure .env` |
| Secure .env file | `chmod 600 .env` |
| Build image | `docker-compose build --no-cache` |
| Start container | `docker-compose up -d` |
| View logs | `docker-compose logs -f sc-generator` |
| Test health | `curl http://localhost:5000/api/health` |
| Stop container | `docker-compose down` |
| Container status | `docker-compose ps` |
| Resource usage | `docker stats sc-generator` |
| Execute command | `docker-compose exec sc-generator <cmd>` |

---

## Support

For detailed information:
- **Docker Security**: See [DOCKER_SECURITY.md](DOCKER_SECURITY.md)
- **Deployment**: See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Configuration**: See [.env.secure](.env.secure)
- **Docker Docs**: https://docs.docker.com/
- **Docker Compose Docs**: https://docs.docker.com/compose/

---

## Important Notes

⚠️ **Security Critical:**
- Never commit `.env` file to git
- Always use `chmod 600 .env` to protect secrets
- Generate new SECRET_KEY for each environment
- Never use DEBUG mode in production
- Regularly update base images and dependencies

✅ **Best Practices:**
- Run container as non-root user (already configured)
- Use named volumes for data persistence (already configured)
- Implement logging and monitoring (configure externally)
- Regular security updates (update .env, rebuild image monthly)
- Test before production deployment (use deployment checklist)
