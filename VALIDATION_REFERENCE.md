# Configuration Validation Reference

## Environment Variable Validation Rules

This document provides the exact validation rules applied by `docker-entrypoint.sh` for all environment variables.

---

## Required Variables (Startup Failure if Invalid)

### SECRET_KEY

| Property | Value |
|----------|-------|
| **Required** | YES (startup failure if missing) |
| **Type** | String |
| **Minimum Length** | 32 characters |
| **Recommended Length** | 48+ characters |
| **Format** | URL-safe base64 or random hex |
| **Change Frequency** | Per environment (never reuse across envs) |

**Validation:**
```python
# Fails if:
- Not set
- Using default value: "your-super-secret-key-change-this-in-production"
- Using template value: "CHANGEME-USE_RANDOM_SECRET_key_value_here_min_32_chars"
- Length < 32 characters

# Startup will exit with: ERROR
# Error message: "SECRET_KEY is not set or using default value!"
```

**Generation:**
```bash
# Recommended method
python3 -c "import secrets; print(secrets.token_urlsafe(48))"

# Output example:
# aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX4yZ5aB6cD7eF8gH9iJ0k
```

---

## Timeout Variables (Validation with Auto-Reset to Defaults)

### REQUEST_TIMEOUT_SECONDS

| Property | Value |
|----------|-------|
| **Type** | Integer (seconds) |
| **Minimum** | 5 seconds |
| **Default** | 30 seconds |
| **Typical Range** | 5-300 seconds |
| **Description** | Default timeout for API requests |

**Validation Rule:**
```
IF REQUEST_TIMEOUT_SECONDS < 5:
    REQUEST_TIMEOUT_SECONDS = 30  (reset to default)
    LOG WARNING: "REQUEST_TIMEOUT_SECONDS too small, using default 30 seconds"
```

**Severity:** WARNING (continues startup)

---

### UPLOAD_TIMEOUT_SECONDS

| Property | Value |
|----------|-------|
| **Type** | Integer (seconds) |
| **Minimum** | 60 seconds |
| **Default** | 300 seconds (5 minutes) |
| **Typical Range** | 60-900 seconds |
| **Description** | Timeout for file upload operations |

**Validation Rule:**
```
IF UPLOAD_TIMEOUT_SECONDS < 60:
    UPLOAD_TIMEOUT_SECONDS = 300  (reset to default)
    LOG WARNING: "UPLOAD_TIMEOUT_SECONDS too small, using default 300 seconds"
```

**Severity:** WARNING (continues startup)

---

### GENERATE_TIMEOUT_SECONDS

| Property | Value |
|----------|-------|
| **Type** | Integer (seconds) |
| **Minimum** | 10 seconds |
| **Default** | 120 seconds (2 minutes) |
| **Typical Range** | 10-600 seconds |
| **Description** | Timeout for payload generation operations |

**Validation Rule:**
```
IF GENERATE_TIMEOUT_SECONDS < 10:
    GENERATE_TIMEOUT_SECONDS = 120  (reset to default)
    LOG WARNING: "GENERATE_TIMEOUT_SECONDS too small, using default 120 seconds"
```

**Severity:** WARNING (continues startup)

---

### DOWNLOAD_TIMEOUT_SECONDS

| Property | Value |
|----------|-------|
| **Type** | Integer (seconds) |
| **Minimum** | 5 seconds |
| **Default** | 60 seconds (1 minute) |
| **Typical Range** | 5-300 seconds |
| **Description** | Timeout for file download operations |

**Validation Rule:**
```
IF DOWNLOAD_TIMEOUT_SECONDS < 5:
    DOWNLOAD_TIMEOUT_SECONDS = 60  (reset to default)
    LOG WARNING: "DOWNLOAD_TIMEOUT_SECONDS too small, using default 60 seconds"
```

**Severity:** WARNING (continues startup)

---

## Security Variables (Validation with Restrictions)

### FLASK_ENV

| Property | Value |
|----------|-------|
| **Type** | String |
| **Allowed Values** | `production`, `development`, `testing` |
| **Default** | `production` |
| **Recommended (Prod)** | `production` |
| **Recommended (Dev)** | `development` |

**Validation Rule:**
```
IF FLASK_ENV NOT IN ['production', 'development', 'testing']:
    FLASK_ENV = production  (reset to default)
    LOG WARNING: "FLASK_ENV has invalid value, using production"
```

**Severity:** WARNING (continues startup)

---

### FLASK_DEBUG

| Property | Value |
|----------|-------|
| **Type** | Boolean |
| **Allowed Values** | `true`, `false` |
| **Default** | `false` |
| **Critical in Prod** | MUST be `false` |

**Validation Rules:**
```
# Rule 1: Invalid value
IF FLASK_DEBUG NOT IN ['true', 'false']:
    FLASK_DEBUG = false  (reset to default)
    LOG WARNING: "FLASK_DEBUG has invalid value, using false"

# Rule 2: Debug in production (CRITICAL)
IF FLASK_ENV == 'production' AND FLASK_DEBUG == 'true':
    EXIT WITH ERROR: "FLASK_DEBUG must be false in production!"
```

**Severity for Rule 1:** WARNING (continues startup)
**Severity for Rule 2:** CRITICAL ERROR (startup failure)

---

### LOG_LEVEL

| Property | Value |
|----------|-------|
| **Type** | String |
| **Allowed Values** | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| **Default** | `INFO` |
| **Recommended (Prod)** | `INFO` or `WARNING` |
| **Recommended (Dev)** | `DEBUG` |

**Validation Rule:**
```
IF FLASK_ENV == 'production' AND LOG_LEVEL == 'DEBUG':
    LOG WARNING: "LOG_LEVEL is DEBUG in production"
    LOG WARNING: "Debug mode exposes sensitive data"
    LOG WARNING: "Recommend changing to INFO or WARNING"
```

**Severity:** WARNING (continues startup, but alerts operator)

---

### RATE_LIMIT_ENABLED

| Property | Value |
|----------|-------|
| **Type** | Boolean |
| **Allowed Values** | `true`, `false` |
| **Default** | `true` |
| **Critical in Prod** | MUST be `true` |

**Validation Rule:**
```
IF RATE_LIMIT_ENABLED NOT IN ['true', 'false']:
    RATE_LIMIT_ENABLED = true  (reset to default)
    LOG WARNING: "RATE_LIMIT_ENABLED has invalid value, using true"
```

**Severity:** WARNING (continues startup)

---

### CORS_ORIGINS

| Property | Value |
|----------|-------|
| **Type** | String (comma-separated) |
| **Format** | Exact origins (no wildcards in production) |
| **Default** | `http://localhost:3000,http://localhost:8080` |
| **Critical in Prod** | MUST NOT contain `*` |

**Validation Rule:**
```
IF FLASK_ENV == 'production' AND '*' in CORS_ORIGINS:
    EXIT WITH ERROR: "CORS_ORIGINS contains wildcards in production!"
    ERROR MESSAGE: "Set specific allowed origins instead"
```

**Severity:** CRITICAL ERROR (startup failure in production)

**Examples:**

Valid for development:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,*
```

Valid for production:
```
CORS_ORIGINS=https://app.example.com,https://www.example.com
```

Invalid for production:
```
CORS_ORIGINS=*
CORS_ORIGINS=https://*.example.com
```

---

## File and Directory Variables (Validation with Checks)

### UPLOAD_FOLDER

| Property | Value |
|----------|-------|
| **Type** | File path |
| **Default** | `/tmp/sc-uploads` |
| **Validation** | Directory must exist and be writable |

**Validation Rule:**
```
IF directory does not exist:
    CREATE directory
    SET ownership to scgen:scgen
    SET permissions to 700

IF directory not writable by scgen:
    EXIT WITH ERROR: "Directory is not writable: {path}"
    SHOW actual permissions: ls -ld {path}
```

**Severity:** ERROR if not writable (startup failure)

---

### OUTPUT_FOLDER

| Property | Value |
|----------|-------|
| **Type** | File path |
| **Default** | `/tmp/sc-outputs` |
| **Validation** | Directory must exist and be writable |

**Validation Rule:**
```
IF directory does not exist:
    CREATE directory
    SET ownership to scgen:scgen
    SET permissions to 700

IF directory not writable by scgen:
    EXIT WITH ERROR: "Directory is not writable: {path}"
    SHOW actual permissions: ls -ld {path}
```

**Severity:** ERROR if not writable (startup failure)

---

### LOG_FILE

| Property | Value |
|----------|-------|
| **Type** | File path |
| **Default** | `/var/log/sc-generator/app.log` |
| **Validation** | Parent directory must exist and be writable |

**Validation Rule:**
```
parent_dir = dirname(LOG_FILE)

IF parent directory does not exist:
    CREATE parent directory
    SET ownership to scgen:scgen
    SET permissions to 755

IF parent directory not writable by scgen:
    EXIT WITH ERROR: "Directory is not writable: {parent_dir}"
```

**Severity:** ERROR if not writable (startup failure)

---

## Size and Count Variables (Validation with Ranges)

### MAX_FILE_SIZE_MB

| Property | Value |
|----------|-------|
| **Type** | Integer (megabytes) |
| **Minimum** | 1 MB |
| **Maximum** | 500 MB |
| **Default** | 100 MB |
| **Typical Range** | 50-200 MB |

**Validation Rule:**
```
IF MAX_FILE_SIZE_MB < 1 OR MAX_FILE_SIZE_MB > 500:
    MAX_FILE_SIZE_MB = 100  (reset to default)
    LOG WARNING: "MAX_FILE_SIZE_MB out of range, using default 100MB"
```

**Severity:** WARNING (continues startup)

---

### RATE_LIMIT_PER_IP

| Property | Value |
|----------|-------|
| **Type** | Integer (requests per minute) |
| **Minimum** | 10 requests/min |
| **Default** | 100 requests/min |
| **Typical Range** | 10-1000 requests/min |

**Validation Rule:**
```
IF RATE_LIMIT_PER_IP < 10:
    RATE_LIMIT_PER_IP = 100  (reset to default)
    LOG WARNING: "RATE_LIMIT_PER_IP too low, using default 100"
```

**Severity:** WARNING (continues startup)

---

### RATE_LIMIT_GLOBAL

| Property | Value |
|----------|-------|
| **Type** | Integer (requests per minute) |
| **Minimum** | 100 requests/min |
| **Default** | 1000 requests/min |
| **Typical Range** | 100-10000 requests/min |

**Validation Rule:**
```
IF RATE_LIMIT_GLOBAL < 100:
    RATE_LIMIT_GLOBAL = 1000  (reset to default)
    LOG WARNING: "RATE_LIMIT_GLOBAL too low, using default 1000"
```

**Severity:** WARNING (continues startup)

---

### LOG_MAX_SIZE

| Property | Value |
|----------|-------|
| **Type** | Integer (bytes) |
| **Minimum** | 1,048,576 bytes (1 MB) |
| **Default** | 10,485,760 bytes (10 MB) |
| **Typical Range** | 1-100 MB |

**Validation Rule:**
```
IF LOG_MAX_SIZE < 1048576:  # 1 MB
    LOG_MAX_SIZE = 10485760  (reset to default 10 MB)
    LOG WARNING: "LOG_MAX_SIZE too small, using default 10MB"
```

**Severity:** WARNING (continues startup)

---

## Validation Execution Flow

```
┌─────────────────────────────────────┐
│   Docker Container Startup          │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 1. Validate Required Variables      │
│    - SECRET_KEY check               │
│                                     │
│    FAIL → EXIT with ERROR           │
│    PASS → Continue                  │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 2. Validate Directories             │
│    - Check existence                │
│    - Check writable                 │
│                                     │
│    FAIL → EXIT with ERROR           │
│    PASS → Continue                  │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 3. Validate Timeout Values          │
│    - Check minimums                 │
│    - Reset if invalid               │
│                                     │
│    FAIL → LOG WARNING + reset       │
│    PASS → Continue                  │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 4. Validate Security Settings       │
│    - FLASK_ENV/DEBUG check          │
│    - CORS_ORIGINS check             │
│    - LOG_LEVEL check                │
│    - RATE_LIMIT check               │
│                                     │
│    CRITICAL FAIL → EXIT with ERROR  │
│    WARNING FAIL → LOG WARNING       │
│    PASS → Continue                  │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 5. Verify User Permissions          │
│    - Check not running as root      │
│                                     │
│    FAIL → EXIT with ERROR           │
│    PASS → Continue                  │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ All Validations Passed!             │
│ Starting Application...             │
└─────────────────────────────────────┘
```

---

## Log Output Reference

### Successful Validation Example

```
[INFO] ==========================================
[INFO] SC-Generator Docker Entrypoint
[INFO] ==========================================
[INFO] Validating required environment variables...
[INFO] ✓ SECRET_KEY is valid (length: 60)
[INFO] Validating directory permissions...
[INFO] ✓ Directory writable: /tmp/sc-uploads
[INFO] ✓ Directory writable: /tmp/sc-outputs
[INFO] ✓ Directory writable: /var/log/sc-generator
[INFO] Validating timeout configuration...
[INFO] ✓ REQUEST_TIMEOUT_SECONDS: 30s
[INFO] ✓ UPLOAD_TIMEOUT_SECONDS: 300s
[INFO] ✓ GENERATE_TIMEOUT_SECONDS: 120s
[INFO] ✓ DOWNLOAD_TIMEOUT_SECONDS: 60s
[INFO] Validating security settings...
[INFO] ✓ FLASK_ENV: production
[INFO] ✓ FLASK_DEBUG: false
[INFO] ✓ LOG_LEVEL: INFO
[INFO] ✓ CORS_ORIGINS: http://localhost:3000
[INFO] ✓ RATE_LIMIT_ENABLED: true
[INFO] Verifying container user...
[INFO] ✓ Running as: scgen (UID: 1000, GID: 1000)
[INFO] ==========================================
[INFO] All validations passed!
[INFO] Starting application...
[INFO] ==========================================
 * Running on http://0.0.0.0:5000
```

### Failed Validation Example (CRITICAL)

```
[INFO] ==========================================
[INFO] SC-Generator Docker Entrypoint
[INFO] ==========================================
[INFO] Validating required environment variables...
[ERROR] SECRET_KEY is not set or using default value!
[ERROR] Generate a new key: python3 -c "import secrets; print(secrets.token_urlsafe(48))"
ERROR EXITING
```

### Warning Validation Example (WARNING)

```
[INFO] Validating timeout configuration...
[WARN] REQUEST_TIMEOUT_SECONDS (3) is less than minimum (5s), using default 30s
[INFO] ✓ REQUEST_TIMEOUT_SECONDS: 30s (reset from invalid 3)
[INFO] ✓ UPLOAD_TIMEOUT_SECONDS: 300s
```

---

## Troubleshooting Validation Issues

### Problem: "SECRET_KEY is not set"

**Check .env file:**
```bash
grep SECRET_KEY .env
# Should output: SECRET_KEY=<long-random-string>
```

**Fix:**
```bash
# Generate new SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(48))"

# Update .env
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')" >> .env

# Restart
docker-compose restart sc-generator
```

### Problem: "Directory is not writable"

**Check permissions:**
```bash
ls -la /tmp/sc-uploads
# Should show: drwx------ 

# Check ownership
id
# Container should run as UID 1000
```

**Fix:**
```bash
# Fix from host (if using mounted volumes)
sudo chown 1000:1000 /tmp/sc-*
sudo chmod 700 /tmp/sc-*

# Or from Docker
docker-compose exec sc-generator ls -la /tmp/sc-uploads

# Restart
docker-compose restart sc-generator
```

### Problem: Timeout validation warnings

**Example warning:**
```
[WARN] REQUEST_TIMEOUT_SECONDS (2) is less than minimum (5s), using default 30s
```

**Check .env:**
```bash
grep REQUEST_TIMEOUT_SECONDS .env
# Should be >= 5
```

**Fix:**
```bash
# Edit .env
nano .env
# Change: REQUEST_TIMEOUT_SECONDS=2
# To:     REQUEST_TIMEOUT_SECONDS=30

# Restart
docker-compose restart sc-generator
```

### Problem: "FLASK_DEBUG must be false in production"

**Check .env:**
```bash
grep -E "FLASK_ENV|FLASK_DEBUG" .env
```

**Fix:**
```bash
# Update .env
sed -i 's/FLASK_DEBUG=.*/FLASK_DEBUG=false/' .env

# Verify
grep FLASK_DEBUG .env

# Restart
docker-compose restart sc-generator
```

---

## Production Verification Checklist

Use this checklist before deploying to production:

- [ ] `SECRET_KEY` is changed from default (min 32 chars)
- [ ] `FLASK_ENV=production`
- [ ] `FLASK_DEBUG=false`
- [ ] `LOG_LEVEL=INFO` or `WARNING` (never DEBUG)
- [ ] `RATE_LIMIT_ENABLED=true`
- [ ] `CORS_ORIGINS` does not contain `*`
- [ ] All timeout values are >= minimums
- [ ] `MAX_FILE_SIZE_MB` is appropriate
- [ ] Directory permissions are correct
- [ ] Log files can be written
- [ ] No validation warnings in startup logs
- [ ] Application starts successfully: `curl http://localhost:5000/api/health`

---

## Reference Tables

### Validation Severity Levels

| Level | Description | Action | Startup |
|-------|-------------|--------|---------|
| **PASS** | All checks pass | Log success | Continue |
| **WARNING** | Minor issue, auto-fixed | Log warning, apply fix | Continue |
| **ERROR** | Major issue | Log error, stop | Fail |
| **CRITICAL ERROR** | Security violation | Log error, stop | Fail |

### Configuration Defaults Summary

| Variable | Default Value | Min | Unit |
|----------|---------------|-----|------|
| REQUEST_TIMEOUT_SECONDS | 30 | 5 | seconds |
| UPLOAD_TIMEOUT_SECONDS | 300 | 60 | seconds |
| GENERATE_TIMEOUT_SECONDS | 120 | 10 | seconds |
| DOWNLOAD_TIMEOUT_SECONDS | 60 | 5 | seconds |
| MAX_FILE_SIZE_MB | 100 | 1 | MB |
| RATE_LIMIT_PER_IP | 100 | 10 | req/min |
| RATE_LIMIT_GLOBAL | 1000 | 100 | req/min |
| LOG_MAX_SIZE | 10485760 | 1048576 | bytes |
| FLASK_ENV | production | - | enum |
| FLASK_DEBUG | false | - | bool |
| LOG_LEVEL | INFO | - | enum |

---

## Additional Resources

- [DOCKER_SECURITY.md](DOCKER_SECURITY.md) - Security hardening details
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Deployment guide
- [.env.secure](.env.secure) - Configuration template
