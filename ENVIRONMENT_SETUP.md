# Environment Configuration Guide

This guide explains how to properly configure the SC-Generator application using environment variables.

## Quick Start

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Update critical values:**
   - `SECRET_KEY`: Change to a random secure string
   - `CORS_ORIGINS`: Update for your deployment environment
   - `RATE_LIMIT_*`: Adjust based on your expected traffic

3. **Validate configuration:**
   ```bash
   python3 env_validator.py
   ```

4. **Start the application:**
   ```bash
   python3 app.py
   ```

## Critical Security Configuration

### 1. SECRET_KEY

**Purpose:** Used for session management and CSRF token generation

**Security Requirements:**
- Must be at least 32 characters long
- Must be random and unpredictable
- Must NOT be stored in version control
- Must be different per environment

**Generate a secure key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example:**
```env
SECRET_KEY=rZ8-Dj_K4L9pQw2XyVbN6MhJ3FgE5TuI7AsCbD1_W0
```

### 2. FLASK_DEBUG

**CRITICAL WARNING:** NEVER set to `true` in production

```env
FLASK_DEBUG=false  # Always false in production
```

### 3. CORS_ORIGINS

**Purpose:** Specifies which domains can make requests to the API

**Secure Configuration:**
- Development: `http://localhost:3000,http://localhost:8080`
- Production: Specify exact domain only, no wildcards
  ```env
  CORS_ORIGINS=https://app.example.com
  ```

**Never use wildcards in production:**
```env
# WRONG - NEVER DO THIS
CORS_ORIGINS=*

# WRONG - NEVER DO THIS
CORS_ORIGINS=http://*
```

## Request Timeout Configuration

### Purpose
Prevents slowloris attacks and resource exhaustion by enforcing maximum request duration.

### Timeout Values

| Variable | Minimum | Default | Use Case |
|----------|---------|---------|----------|
| `REQUEST_TIMEOUT_SECONDS` | 5s | 30s | Standard API requests |
| `UPLOAD_TIMEOUT_SECONDS` | 60s | 300s | Large file uploads |
| `GENERATE_TIMEOUT_SECONDS` | 10s | 120s | Payload generation |
| `DOWNLOAD_TIMEOUT_SECONDS` | 5s | 60s | File downloads |

### Configuration Rules

1. **Minimum thresholds are enforced** - values below minimum are reset to defaults with a warning
2. **All values must be realistic** - too low causes failures, too high risks resource exhaustion
3. **Adjust based on infrastructure** - faster servers can use lower timeouts

### Example: Production Configuration

```env
# Fast servers, stable network
REQUEST_TIMEOUT_SECONDS=30
UPLOAD_TIMEOUT_SECONDS=300
GENERATE_TIMEOUT_SECONDS=120
DOWNLOAD_TIMEOUT_SECONDS=60
```

### Example: Slow/Distant Infrastructure

```env
# Slower connections, high latency
REQUEST_TIMEOUT_SECONDS=45
UPLOAD_TIMEOUT_SECONDS=600
GENERATE_TIMEOUT_SECONDS=180
DOWNLOAD_TIMEOUT_SECONDS=90
```

## Rate Limiting Configuration

### Purpose
Protects against abuse and DoS attacks by limiting request frequency.

### Global Settings

```env
# Enable/disable rate limiting globally
RATE_LIMIT_ENABLED=true

# Max requests per minute per IP address
RATE_LIMIT_PER_IP=100

# Max requests per minute globally (all IPs combined)
RATE_LIMIT_GLOBAL=1000

# Cleanup interval for rate limit state (seconds)
RATE_LIMIT_CLEANUP_INTERVAL=300
```

### Endpoint-Specific Limits

```env
# Requests per minute per IP for each endpoint
RATE_LIMIT_UPLOAD=10           # File uploads
RATE_LIMIT_GENERATE=20         # Payload generation
RATE_LIMIT_ONE_CLICK=15        # One-click installer
RATE_LIMIT_PERSISTENT=10       # Persistent payloads
RATE_LIMIT_BATCH=5             # Batch operations
RATE_LIMIT_DOWNLOAD=50         # Downloads
RATE_LIMIT_PREVIEW=50          # Previews
```

### IP Whitelist

Bypass rate limiting for specific IPs (comma-separated, no spaces):

```env
RATE_LIMIT_WHITELIST=127.0.0.1,192.168.1.100,10.0.0.50
```

### Configuration Strategy

**Conservative (High Protection):**
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_IP=50
RATE_LIMIT_GLOBAL=500
RATE_LIMIT_UPLOAD=5
RATE_LIMIT_GENERATE=10
```

**Moderate (Balanced):**
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_IP=100
RATE_LIMIT_GLOBAL=1000
RATE_LIMIT_UPLOAD=10
RATE_LIMIT_GENERATE=20
```

**Permissive (High Throughput):**
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_IP=200
RATE_LIMIT_GLOBAL=2000
RATE_LIMIT_UPLOAD=20
RATE_LIMIT_GENERATE=50
```

## File Upload Configuration

### Maximum File Size

```env
# Maximum file size in MB
# Prevents DoS attacks via enormous files
MAX_FILE_SIZE_MB=100
```

### Allowed Extensions

```env
# Comma-separated list (no spaces)
ALLOWED_EXTENSIONS=msi,exe,dll,bat,cmd,vbs
```

### Upload Directories

```env
# Temporary file upload directory
UPLOAD_FOLDER=/tmp/sc-uploads

# Generated payload output directory
OUTPUT_FOLDER=/tmp/sc-outputs
```

**Important:** Ensure these directories:
1. Exist and are writable by the application user
2. Have sufficient disk space
3. Are on a partition with cleanup procedures

## Logging Configuration

### Log Level

```env
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

### Log File Settings

```env
# Path where logs are written
LOG_FILE=/var/log/sc-generator/app.log

# Maximum log file size before rotation (bytes)
LOG_MAX_SIZE=10485760  # 10MB

# Number of backup log files to keep
LOG_BACKUP_COUNT=5
```

### Configuration Examples

**Development:**
```env
LOG_LEVEL=DEBUG
LOG_FILE=/tmp/sc-generator.log
```

**Production:**
```env
LOG_LEVEL=INFO
LOG_FILE=/var/log/sc-generator/app.log
LOG_MAX_SIZE=52428800  # 50MB
LOG_BACKUP_COUNT=10
```

## Obfuscation Settings

### Obfuscation Level

```env
# Options: low, medium, high
OBFUSCATION_DEFAULT_LEVEL=high
```

### Polymorphic Variants

```env
# Number of different variants to generate
# Higher = more variants = better evasion but slower generation
POLYMORPHIC_VARIANTS=5
```

### Noise Ratio

```env
# Ratio of noise code to inject (0.0 to 1.0)
# 0.0 = no noise
# 0.3 = 30% noise
# 1.0 = 100% noise
NOISE_RATIO=0.3
```

## Proxy Configuration

```env
# Timeout for proxy connections (seconds)
PROXY_TIMEOUT_SECONDS=30
```

## File Retention & Cleanup

### Automatic Cleanup

```env
# How often to run cleanup (hours)
CLEANUP_INTERVAL_HOURS=24

# How long to keep generated files (hours)
FILE_RETENTION_HOURS=72
```

Files older than `FILE_RETENTION_HOURS` are automatically deleted.

**Example: 3-day retention with daily cleanup**
```env
CLEANUP_INTERVAL_HOURS=24
FILE_RETENTION_HOURS=72
```

## Validation & Startup

### Automatic Validation

The application automatically validates all environment variables on startup:

1. **Type checking** - Ensures correct data types
2. **Constraint validation** - Checks min/max values and allowed choices
3. **Path validation** - Verifies directories exist and are writable
4. **Requirement checking** - Ensures all required variables are set

### Manual Validation

```bash
python3 env_validator.py
```

**Output example:**
```
================================================================================
ENVIRONMENT CONFIGURATION WARNINGS
================================================================================
  ⚠ WARNING: Directory LOG_FILE=/var/log/sc-generator/app.log is not writable.
    Ensure proper permissions are set.
================================================================================

✓ All environment variables validated successfully!

Loaded configuration:
  CLEANUP_INTERVAL_HOURS = 24
  CORS_ENABLED = True
  CORS_ORIGINS = http://localhost:3000,http://localhost:8080
  ...
```

### Error Handling

If validation fails, the application will not start:

```
================================================================================
ENVIRONMENT CONFIGURATION ERRORS
================================================================================
  ✗ REQUIRED: SECRET_KEY not set. Session secret key (must be 32+ characters)
  ✗ SECRET_KEY: value too short (minimum 32 characters)
================================================================================
```

**Resolution:** Fix the listed errors and re-run the application.

## Environment-Specific Templates

### Development Environment

```env
FLASK_ENV=development
FLASK_DEBUG=false
SECRET_KEY=dev-only-change-this-before-production-usage-12345678
SERVER_HOST=127.0.0.1
SERVER_PORT=5000
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000
LOG_LEVEL=DEBUG
RATE_LIMIT_ENABLED=false
```

### Staging Environment

```env
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
CORS_ORIGINS=https://staging.example.com
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_IP=150
UPLOAD_FOLDER=/var/data/sc-generator/uploads
OUTPUT_FOLDER=/var/data/sc-generator/outputs
LOG_FILE=/var/log/sc-generator/app.log
```

### Production Environment

```env
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
SERVER_HOST=127.0.0.1
SERVER_PORT=5000
CORS_ORIGINS=https://app.example.com
LOG_LEVEL=WARNING
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_IP=100
RATE_LIMIT_GLOBAL=1000
REQUEST_TIMEOUT_SECONDS=30
UPLOAD_TIMEOUT_SECONDS=300
GENERATE_TIMEOUT_SECONDS=120
DOWNLOAD_TIMEOUT_SECONDS=60
UPLOAD_FOLDER=/var/data/sc-generator/uploads
OUTPUT_FOLDER=/var/data/sc-generator/outputs
LOG_FILE=/var/log/sc-generator/app.log
LOG_MAX_SIZE=52428800
LOG_BACKUP_COUNT=10
CLEANUP_INTERVAL_HOURS=24
FILE_RETENTION_HOURS=72
```

## Deployment Checklist

- [ ] Copy `.env.example` to `.env`
- [ ] Generate secure `SECRET_KEY`
- [ ] Set `FLASK_DEBUG=false`
- [ ] Configure `CORS_ORIGINS` for your domain
- [ ] Validate configuration: `python3 env_validator.py`
- [ ] Ensure all directory paths exist and are writable
- [ ] Verify log file directory has sufficient permissions
- [ ] Test with `python3 app.py`
- [ ] Configure rate limiting for your traffic profile
- [ ] Set up log rotation (systemd, logrotate, etc.)
- [ ] Never commit `.env` to version control
- [ ] Document any custom environment variable requirements

## Troubleshooting

### Application won't start

1. Run validation: `python3 env_validator.py`
2. Check error messages in startup output
3. Review required variables section
4. Verify all paths are accessible

### Rate limiting too aggressive

1. Increase `RATE_LIMIT_PER_IP` and `RATE_LIMIT_GLOBAL`
2. Increase endpoint-specific limits
3. Add trusted IPs to `RATE_LIMIT_WHITELIST`

### Requests timing out

1. Increase the corresponding timeout variable
2. Check server resource usage (CPU, memory, disk I/O)
3. Check network latency between client and server
4. Consider splitting large operations into smaller tasks

### Directory permission errors

```bash
# Ensure application user can write to directories
sudo chown app-user:app-user /path/to/directory
sudo chmod 755 /path/to/directory
```

## Best Practices

1. **Never commit .env to version control** - Use `.env.example` for documentation
2. **Use strong SECRET_KEY** - Generate with cryptographic randomness
3. **Disable debug in production** - Prevents information leakage
4. **Restrict CORS origins** - Never use wildcards in production
5. **Monitor rate limit metrics** - Adjust based on actual usage patterns
6. **Rotate logs regularly** - Prevent disk space exhaustion
7. **Review timeout values** - Adjust based on actual infrastructure
8. **Test configuration changes** - Validate with `env_validator.py` before deployment
9. **Document custom values** - Explain any non-default settings
10. **Use environment-specific files** - Maintain separate config for each environment

## Further Reading

- [Flask Configuration Documentation](https://flask.palletsprojects.com/config/)
- [OWASP: Secure Configuration Management](https://owasp.org/www-project-top-ten/)
- [12 Factor App: Store Config in Environment](https://12factor.net/config)
