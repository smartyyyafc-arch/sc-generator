# SC-Generator Docker Deployment Checklist

## SECURITY FIX #3: Deployment Security Checklist

This checklist ensures all security hardening is properly implemented and verified before deploying SC-Generator to production.

---

## Pre-Deployment Phase

### Environment Configuration

- [ ] **Generated SECRET_KEY**
  - Command: `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`
  - Copy output to `.env` as `SECRET_KEY=<value>`
  - Verify: At least 48 characters, random values

- [ ] **Created .env from template**
  - Copy `.env.secure` to `.env`: `cp .env.secure .env`
  - Verify file permissions: `ls -la .env` (should show `-rw------- `)
  - Restrict permissions: `chmod 600 .env`

- [ ] **Reviewed all environment variables**
  - [ ] `FLASK_ENV=production`
  - [ ] `FLASK_DEBUG=false`
  - [ ] `SECRET_KEY` is set and changed from default
  - [ ] `LOG_LEVEL=INFO` or `LOG_LEVEL=WARNING` (never DEBUG in prod)
  - [ ] `RATE_LIMIT_ENABLED=true`
  - [ ] `CORS_ORIGINS` does not contain `*` (specify exact domains)
  - [ ] All timeout values meet minimum thresholds (see .env.secure for details)
  - [ ] `MAX_FILE_SIZE_MB` is appropriate for use case

- [ ] **Excluded .env from version control**
  ```bash
  # Verify .env is in .gitignore
  grep -E "^\.env" .gitignore
  
  # Verify .env is not tracked
  git status | grep -v ".env"
  ```

- [ ] **Verified directory structure**
  ```bash
  # All required directories exist
  mkdir -p /tmp/sc-{uploads,outputs,fingerprints,logs}
  mkdir -p /var/log/sc-generator
  ```

### Code Review

- [ ] **Reviewed Dockerfile changes**
  - [ ] Multi-stage build is present (builder and runtime stages)
  - [ ] Non-root user is created (scgen:scgen)
  - [ ] USER scgen is set before CMD
  - [ ] File permissions are restrictive
  - [ ] Build tools removed from runtime stage
  - [ ] Entrypoint script is copied and executable

- [ ] **Reviewed docker-compose.yml changes**
  - [ ] `user: scgen:scgen` is set
  - [ ] `security_opt: [no-new-privileges:true]` is present
  - [ ] `cap_drop: [ALL]` is present
  - [ ] Resource limits are set (cpu and memory)
  - [ ] Health check is configured
  - [ ] Logging driver is json-file with rotation

- [ ] **Reviewed .dockerignore file**
  - [ ] `.env` files are excluded
  - [ ] `.git` and `.github` are excluded
  - [ ] `node_modules` and `__pycache__` are excluded
  - [ ] `.env*` pattern matches all .env variants

### Security Verification

- [ ] **Reviewed DOCKER_SECURITY.md**
  - [ ] Understand all security changes
  - [ ] Aware of permission model
  - [ ] Know how to troubleshoot common issues

- [ ] **Scanned for hardcoded secrets**
  ```bash
  # Search for hardcoded secrets in code
  grep -r "SECRET_KEY\|password\|api_key" src/ --include="*.py"
  grep -r "FLASK_SECRET\|AUTH_TOKEN" . --include="*.py" --include="*.js"
  
  # Should only find variable references, not actual values
  ```

- [ ] **Verified no debugging code remains**
  ```bash
  # Search for debug statements
  grep -r "print(\|pdb\|breakpoint()" src/ --include="*.py"
  
  # Should find nothing or only in test files
  ```

---

## Build Phase

### Docker Image Build

- [ ] **Build Docker image without cache**
  ```bash
  docker-compose build --no-cache
  ```
  Expected output: No errors, shows multi-stage build

- [ ] **Verify image was created**
  ```bash
  docker images | grep sc-generator
  # Should show image with appropriate size
  ```

- [ ] **Check image for vulnerabilities** (optional, requires tools)
  ```bash
  # Using Trivy
  trivy image sc-generator:latest
  
  # Using Docker Scout
  docker scout cves sc-generator:latest
  
  # Review results, known vulnerabilities are acceptable if not exploitable
  ```

- [ ] **Verify image layers**
  ```bash
  docker history sc-generator:latest
  # Should show:
  # - builder stage
  # - runtime stage with only essential dependencies
  # - No gcc, npm, or build tools in final layers
  ```

### Image Analysis

- [ ] **Check final image size**
  ```bash
  docker images sc-generator:latest --format "{{.Size}}"
  # Typical size: 200-400MB (slim base + Python + dependencies)
  # If > 1GB, probably includes build stage incorrectly
  ```

- [ ] **Inspect image metadata**
  ```bash
  docker inspect sc-generator:latest
  # Check:
  # - "Entrypoint": ["/app/docker-entrypoint.sh"]
  # - "Cmd": ["python3", "app.py"]
  # - "User": "scgen"
  # - No suspicious environment variables
  ```

---

## Pre-Deployment Runtime Testing

### Local Docker Startup

- [ ] **Start container with test configuration**
  ```bash
  # Set a temporary test SECRET_KEY
  export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
  
  # Start container
  docker-compose up -d
  
  # Should see: "All validations passed! Starting application..."
  ```

- [ ] **Verify container started**
  ```bash
  docker-compose ps
  # Should show: sc-generator is "Up"
  ```

- [ ] **Check container logs for errors**
  ```bash
  docker-compose logs -f sc-generator
  
  # Should see:
  # - Entrypoint validation messages
  # - Application startup messages
  # - No ERROR or CRITICAL messages
  
  # Watch for 30 seconds, then Ctrl+C
  ```

- [ ] **Verify running as non-root**
  ```bash
  docker-compose exec sc-generator id
  # Should output: uid=1000(scgen) gid=1000(scgen) groups=1000(scgen)
  # NOT: uid=0(root)
  ```

### Security Verification at Runtime

- [ ] **Check file permissions inside container**
  ```bash
  docker-compose exec sc-generator ls -la /app
  # All files should be owned by scgen:scgen
  
  docker-compose exec sc-generator ls -la /tmp/sc-uploads
  # Permission should be drwx------ (700)
  ```

- [ ] **Verify process privileges**
  ```bash
  docker-compose exec sc-generator ps aux
  # Python process should be running as scgen, not root
  ```

- [ ] **Check network capabilities**
  ```bash
  docker-compose exec sc-generator ip addr
  # Should show container network interface
  
  docker-compose exec sc-generator ip route
  # Should be limited to container network
  ```

### Application Functionality Testing

- [ ] **Test health endpoint**
  ```bash
  curl -v http://localhost:5000/api/health
  # Expected: HTTP 200 OK
  ```

- [ ] **Test file upload** (if applicable)
  ```bash
  # Create a test file
  echo "test data" > test.txt
  
  # Upload
  curl -X POST -F "file=@test.txt" http://localhost:5000/api/upload
  # Should succeed or return appropriate error
  
  # Clean up
  rm test.txt
  ```

- [ ] **Test rate limiting** (if implemented)
  ```bash
  # Make multiple rapid requests
  for i in {1..150}; do curl http://localhost:5000/api/health; done
  
  # After RATE_LIMIT_PER_IP requests, should see 429 (Too Many Requests)
  ```

- [ ] **Check log file creation**
  ```bash
  ls -la /var/log/sc-generator/
  # Should contain app.log with appropriate permissions
  
  tail -f /var/log/sc-generator/app.log
  # Should show application logs
  ```

### Shutdown Testing

- [ ] **Graceful shutdown**
  ```bash
  docker-compose down
  # Should complete without errors
  ```

- [ ] **Data persistence verification** (if using volumes)
  ```bash
  # Start again
  docker-compose up -d
  
  # Check if previous data still exists
  docker-compose exec sc-generator ls -la /tmp/sc-outputs
  ```

---

## Production Deployment

### Final Pre-Deploy Verification

- [ ] **Database/Backup prepared** (if applicable)
  - [ ] Backups configured
  - [ ] Backup tested and verified
  - [ ] Backup location secured

- [ ] **Monitoring configured**
  - [ ] Log aggregation set up
  - [ ] Alerts configured for errors
  - [ ] Health check monitoring active
  - [ ] Resource monitoring active

- [ ] **Reverse proxy configured** (if applicable)
  - [ ] TLS/HTTPS termination configured
  - [ ] Rate limiting rules configured
  - [ ] Security headers added (CSP, X-Frame-Options, etc.)

- [ ] **Firewall rules verified**
  - [ ] Only required ports open
  - [ ] IP allowlists configured if applicable
  - [ ] Egress rules configured (if applicable)

### Deployment Execution

- [ ] **Production environment prepared**
  ```bash
  # SSH to production server
  ssh user@prod.example.com
  
  # Navigate to deployment directory
  cd /opt/sc-generator
  
  # Verify no existing container
  docker-compose ps
  ```

- [ ] **Production .env configured**
  ```bash
  # Create .env with production values
  # CRITICAL: Different SECRET_KEY, CORS_ORIGINS, etc.
  
  # Verify permissions
  ls -la .env  # Should be -rw------- (600)
  ```

- [ ] **Pull latest code** (if using git)
  ```bash
  git pull origin main
  # Verify no uncommitted changes
  git status
  ```

- [ ] **Build production image**
  ```bash
  docker-compose build --no-cache
  # Verify build succeeds
  ```

- [ ] **Start production container**
  ```bash
  docker-compose up -d
  
  # Verify startup
  docker-compose ps
  
  # Check logs
  docker-compose logs --tail=50 sc-generator
  ```

- [ ] **Verify application is responding**
  ```bash
  curl -v http://localhost:5000/api/health
  # Expected: HTTP 200
  ```

### Post-Deployment Monitoring

- [ ] **Monitor logs for first 5 minutes**
  ```bash
  docker-compose logs -f sc-generator
  # Watch for errors, warnings
  # Look for: "All validations passed"
  # Look for: Application startup messages
  ```

- [ ] **Verify no validation warnings**
  ```bash
  docker-compose logs sc-generator | grep -i "warning\|error"
  # Should see nothing or only expected messages
  ```

- [ ] **Test API endpoints**
  ```bash
  # Health check
  curl http://localhost:5000/api/health
  
  # Smoke tests for critical endpoints
  # (Add your specific endpoints here)
  ```

- [ ] **Verify resource usage**
  ```bash
  docker stats sc-generator
  # Monitor for 1-2 minutes
  # CPU should be < 50% idle
  # Memory should be < 500MB (under load)
  ```

- [ ] **Check disk usage**
  ```bash
  docker-compose exec sc-generator df -h /
  # Should have adequate free space
  
  # Check log directory
  du -sh /var/log/sc-generator
  # Should be growing, not too large
  ```

---

## Rollback Procedures

If deployment fails or issues are discovered:

### Quick Rollback

```bash
# Stop current container
docker-compose down

# Return to previous version (if using git)
git checkout previous-commit

# Rebuild with previous code
docker-compose build --no-cache

# Start with previous .env
docker-compose up -d

# Verify
docker-compose logs -f sc-generator
```

### Data Preservation

```bash
# If using named volumes, data persists
docker volume ls

# If you need to backup current state
docker-compose exec sc-generator tar -czf /backup/state-backup.tar.gz /tmp/sc-* /var/log/sc-generator
```

---

## Post-Deployment Operations

### Regular Maintenance

- [ ] **Weekly tasks**
  - [ ] Review application logs
  - [ ] Check disk usage
  - [ ] Verify backups completed successfully

- [ ] **Monthly tasks**
  - [ ] Security updates: `docker pull python:3.11-slim`
  - [ ] Dependency updates: Update requirements.txt
  - [ ] Review and rotate secrets if needed
  - [ ] Audit log file for suspicious activity

- [ ] **Quarterly tasks**
  - [ ] Full security audit
  - [ ] Penetration testing (if applicable)
  - [ ] Review and update security policies
  - [ ] Disaster recovery drill

### Security Monitoring

- [ ] **Set up alerts for**
  - [ ] Error logs (ERROR, CRITICAL)
  - [ ] Rate limit violations
  - [ ] Failed authentication (if implemented)
  - [ ] Disk space < 10%
  - [ ] Container restart/crash
  - [ ] Health check failures

- [ ] **Regular log review**
  ```bash
  # Check for suspicious activity
  docker-compose logs sc-generator | grep -i "error\|security\|warning"
  
  # Monitor rate limiting
  docker-compose logs sc-generator | grep "rate_limit"
  ```

---

## Troubleshooting

### Issue: Container fails to start with "SECRET_KEY is not set"

**Solution:**
```bash
# Generate new SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(48))"

# Update .env
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')" >> .env

# Restart
docker-compose down && docker-compose up -d
```

### Issue: Container crashes with "Permission denied" errors

**Solution:**
```bash
# Check file ownership
docker-compose exec sc-generator ls -la /tmp/sc-uploads

# Fix if needed (run from host)
sudo chown -R 1000:1000 /tmp/sc-*

# Restart container
docker-compose restart sc-generator
```

### Issue: Health check failing

**Solution:**
```bash
# Test endpoint manually
curl -v http://localhost:5000/api/health

# Check application logs
docker-compose logs -f sc-generator

# Verify application started successfully
docker-compose exec sc-generator ps aux
```

### Issue: High CPU or memory usage

**Solution:**
```bash
# Check resource usage
docker stats sc-generator

# Review application logs for errors
docker-compose logs sc-generator | grep -i "error"

# Restart container
docker-compose restart sc-generator

# Monitor again
docker stats sc-generator
```

---

## Quick Reference Commands

```bash
# View logs
docker-compose logs -f sc-generator

# Execute command in container
docker-compose exec sc-generator <command>

# Rebuild image
docker-compose build --no-cache

# Start/stop container
docker-compose up -d          # Start
docker-compose down           # Stop

# Check container status
docker-compose ps
docker stats sc-generator

# View configuration
docker inspect sc-generator:latest

# Clean up resources
docker-compose down -v        # Remove containers and volumes
docker system prune           # Remove unused Docker resources

# Generate new SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## References

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [SC-Generator DOCKER_SECURITY.md](DOCKER_SECURITY.md)
- [SC-Generator .env.secure](.env.secure)
