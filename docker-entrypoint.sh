#!/bin/bash
# ============================================================================
# SC-Generator Docker Entrypoint Script
# SECURITY FIX #3: Validates configuration and enforces secure defaults
# ============================================================================

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================================================
# Validation Functions
# ============================================================================

validate_required_vars() {
    log_info "Validating required environment variables..."

    # SECRET_KEY validation
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-super-secret-key-change-this-in-production" ] || [ "$SECRET_KEY" = "CHANGEME-USE_RANDOM_SECRET_key_value_here_min_32_chars" ]; then
        log_error "SECRET_KEY is not set or using default value!"
        log_error "Generate a new key: python3 -c \"import secrets; print(secrets.token_urlsafe(48))\""
        exit 1
    fi

    if [ ${#SECRET_KEY} -lt 32 ]; then
        log_error "SECRET_KEY must be at least 32 characters long (current: ${#SECRET_KEY})"
        exit 1
    fi

    log_info "✓ SECRET_KEY is valid (length: ${#SECRET_KEY})"
}

validate_directories() {
    log_info "Validating directory permissions..."

    local dirs=(
        "$UPLOAD_FOLDER:/tmp/sc-uploads"
        "$OUTPUT_FOLDER:/tmp/sc-outputs"
        "/var/log/sc-generator"
    )

    for dir_pair in "${dirs[@]}"; do
        IFS=':' read -r env_var dir <<< "$dir_pair"

        # Use environment variable if set, otherwise use dir
        [ -n "$env_var" ] && dir_check="${!env_var:-$dir}" || dir_check="$dir"

        if [ ! -d "$dir_check" ]; then
            log_warn "Directory does not exist: $dir_check (creating...)"
            mkdir -p "$dir_check" || { log_error "Failed to create directory: $dir_check"; exit 1; }
        fi

        if [ ! -w "$dir_check" ]; then
            log_error "Directory is not writable: $dir_check"
            log_error "Permissions: $(ls -ld $dir_check)"
            exit 1
        fi

        log_info "✓ Directory writable: $dir_check"
    done
}

validate_timeout_values() {
    log_info "Validating timeout configuration..."

    # Validate REQUEST_TIMEOUT_SECONDS (min: 5)
    if [ -n "$REQUEST_TIMEOUT_SECONDS" ] && [ "$REQUEST_TIMEOUT_SECONDS" -lt 5 ]; then
        log_warn "REQUEST_TIMEOUT_SECONDS ($REQUEST_TIMEOUT_SECONDS) is less than minimum (5s), using default 30s"
        export REQUEST_TIMEOUT_SECONDS=30
    fi
    log_info "✓ REQUEST_TIMEOUT_SECONDS: ${REQUEST_TIMEOUT_SECONDS:-30}s"

    # Validate UPLOAD_TIMEOUT_SECONDS (min: 60)
    if [ -n "$UPLOAD_TIMEOUT_SECONDS" ] && [ "$UPLOAD_TIMEOUT_SECONDS" -lt 60 ]; then
        log_warn "UPLOAD_TIMEOUT_SECONDS ($UPLOAD_TIMEOUT_SECONDS) is less than minimum (60s), using default 300s"
        export UPLOAD_TIMEOUT_SECONDS=300
    fi
    log_info "✓ UPLOAD_TIMEOUT_SECONDS: ${UPLOAD_TIMEOUT_SECONDS:-300}s"

    # Validate GENERATE_TIMEOUT_SECONDS (min: 10)
    if [ -n "$GENERATE_TIMEOUT_SECONDS" ] && [ "$GENERATE_TIMEOUT_SECONDS" -lt 10 ]; then
        log_warn "GENERATE_TIMEOUT_SECONDS ($GENERATE_TIMEOUT_SECONDS) is less than minimum (10s), using default 120s"
        export GENERATE_TIMEOUT_SECONDS=120
    fi
    log_info "✓ GENERATE_TIMEOUT_SECONDS: ${GENERATE_TIMEOUT_SECONDS:-120}s"

    # Validate DOWNLOAD_TIMEOUT_SECONDS (min: 5)
    if [ -n "$DOWNLOAD_TIMEOUT_SECONDS" ] && [ "$DOWNLOAD_TIMEOUT_SECONDS" -lt 5 ]; then
        log_warn "DOWNLOAD_TIMEOUT_SECONDS ($DOWNLOAD_TIMEOUT_SECONDS) is less than minimum (5s), using default 60s"
        export DOWNLOAD_TIMEOUT_SECONDS=60
    fi
    log_info "✓ DOWNLOAD_TIMEOUT_SECONDS: ${DOWNLOAD_TIMEOUT_SECONDS:-60}s"
}

validate_security_settings() {
    log_info "Validating security settings..."

    # Check FLASK_ENV
    if [ "$FLASK_ENV" != "production" ] && [ "$FLASK_ENV" != "development" ] && [ "$FLASK_ENV" != "testing" ]; then
        log_warn "FLASK_ENV has invalid value: $FLASK_ENV (must be: production, development, or testing)"
        export FLASK_ENV=production
    fi
    log_info "✓ FLASK_ENV: $FLASK_ENV"

    # Check FLASK_DEBUG
    if [ "$FLASK_DEBUG" != "false" ] && [ "$FLASK_DEBUG" != "true" ]; then
        log_warn "FLASK_DEBUG has invalid value: $FLASK_DEBUG (must be: true or false)"
        export FLASK_DEBUG=false
    fi

    if [ "$FLASK_ENV" = "production" ] && [ "$FLASK_DEBUG" = "true" ]; then
        log_error "FLASK_DEBUG must be false in production!"
        exit 1
    fi
    log_info "✓ FLASK_DEBUG: $FLASK_DEBUG"

    # Check LOG_LEVEL
    log_level="${LOG_LEVEL:-INFO}"
    if [ "$FLASK_ENV" = "production" ] && ([ "$log_level" = "DEBUG" ]); then
        log_warn "LOG_LEVEL is DEBUG in production (exposes sensitive data)"
        log_warn "Recommend changing to INFO or WARNING"
    fi
    log_info "✓ LOG_LEVEL: $log_level"

    # Check CORS_ORIGINS for wildcards in production
    if [ "$FLASK_ENV" = "production" ]; then
        if echo "$CORS_ORIGINS" | grep -q "\*"; then
            log_error "CORS_ORIGINS contains wildcards (*) in production - this is a security risk!"
            log_error "Set specific allowed origins instead"
            exit 1
        fi
    fi
    log_info "✓ CORS_ORIGINS: $CORS_ORIGINS"

    # Check RATE_LIMIT_ENABLED
    if [ "$RATE_LIMIT_ENABLED" != "true" ] && [ "$RATE_LIMIT_ENABLED" != "false" ]; then
        log_warn "RATE_LIMIT_ENABLED has invalid value: $RATE_LIMIT_ENABLED (must be: true or false)"
        export RATE_LIMIT_ENABLED=true
    fi
    log_info "✓ RATE_LIMIT_ENABLED: $RATE_LIMIT_ENABLED"
}

verify_user_permissions() {
    log_info "Verifying container user..."

    current_user=$(id -u)
    current_group=$(id -g)
    current_username=$(id -un)

    if [ "$current_user" = "0" ]; then
        log_error "Container is running as root (UID 0) - SECURITY RISK!"
        log_error "Application should run as non-root user"
        exit 1
    fi

    log_info "✓ Running as: $current_username (UID: $current_user, GID: $current_group)"
}

check_health_endpoint() {
    log_info "Waiting for application to start..."

    # Wait up to 30 seconds for the application to start
    max_attempts=30
    attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost:5000/api/health >/dev/null 2>&1; then
            log_info "✓ Application is healthy"
            return 0
        fi

        attempt=$((attempt + 1))
        sleep 1
    done

    log_warn "Health check did not pass after $max_attempts seconds (this may be normal)"
    return 0  # Don't fail, let app run
}

# ============================================================================
# Main Execution
# ============================================================================

log_info "=========================================="
log_info "SC-Generator Docker Entrypoint"
log_info "=========================================="

# Run validations
validate_required_vars
validate_directories
validate_timeout_values
validate_security_settings
verify_user_permissions

log_info "=========================================="
log_info "All validations passed!"
log_info "Starting application..."
log_info "=========================================="

# Execute the main application
exec "$@"
