#!/usr/bin/env python3
"""
SC-Generator Configuration Management

CONFIGURATION FIX #2: Environment Variable Validation at Startup
- Validates all required environment variables exist and are valid
- Provides secure defaults
- Ensures configuration is properly initialized before app starts
- Comprehensive documentation and error messages
"""

import os
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging for configuration validation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
config_logger = logging.getLogger('CONFIG')


class ConfigurationError(Exception):
    """Raised when configuration validation fails"""
    pass


class ConfigValidator:
    """
    Validates environment variables and configuration at startup.

    Features:
    - Type validation (int, bool, string, path)
    - Range/constraint checking
    - Security validation (secure defaults, no weak values)
    - Comprehensive error messages
    - Auto-correction with warnings where safe
    """

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.validated_config: Dict[str, Any] = {}

    def add_error(self, key: str, message: str):
        """Record a validation error"""
        error_msg = f"[{key}] {message}"
        self.errors.append(error_msg)
        config_logger.error(error_msg)

    def add_warning(self, key: str, message: str):
        """Record a validation warning"""
        warning_msg = f"[{key}] {message}"
        self.warnings.append(warning_msg)
        config_logger.warning(warning_msg)

    def validate_required_string(
        self,
        key: str,
        default: Optional[str] = None,
        allowed_values: Optional[List[str]] = None,
        min_length: int = 1,
        max_length: Optional[int] = None
    ) -> Optional[str]:
        """
        Validate a required string environment variable.

        Args:
            key: Environment variable name
            default: Default value if not set
            allowed_values: List of allowed values (if restricted)
            min_length: Minimum string length
            max_length: Maximum string length

        Returns:
            Validated string value or None if validation failed
        """
        value = os.environ.get(key, default)

        if value is None:
            self.add_error(key, f"Required environment variable not set and no default provided")
            return None

        value = str(value).strip()

        # Check length constraints
        if len(value) < min_length:
            self.add_error(key, f"Value too short (min {min_length} chars, got {len(value)})")
            return None

        if max_length and len(value) > max_length:
            self.add_error(key, f"Value too long (max {max_length} chars, got {len(value)})")
            return None

        # Check allowed values
        if allowed_values and value not in allowed_values:
            self.add_error(
                key,
                f"Invalid value '{value}'. Allowed: {', '.join(allowed_values)}"
            )
            return None

        self.validated_config[key] = value
        return value

    def validate_integer(
        self,
        key: str,
        default: int,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        auto_correct: bool = True
    ) -> int:
        """
        Validate an integer environment variable.

        Args:
            key: Environment variable name
            default: Default value
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            auto_correct: Auto-correct to default if invalid (with warning)

        Returns:
            Validated integer value
        """
        value_str = os.environ.get(key)

        if value_str is None:
            self.validated_config[key] = default
            return default

        try:
            value = int(value_str)
        except ValueError:
            if auto_correct:
                self.add_warning(
                    key,
                    f"Invalid integer '{value_str}', using default {default}"
                )
                self.validated_config[key] = default
                return default
            else:
                self.add_error(key, f"Invalid integer value: {value_str}")
                return default

        # Check constraints
        if min_value is not None and value < min_value:
            if auto_correct:
                self.add_warning(
                    key,
                    f"Value {value} below minimum {min_value}, using default {default}"
                )
                self.validated_config[key] = default
                return default
            else:
                self.add_error(key, f"Value {value} below minimum {min_value}")
                return default

        if max_value is not None and value > max_value:
            if auto_correct:
                self.add_warning(
                    key,
                    f"Value {value} above maximum {max_value}, using default {default}"
                )
                self.validated_config[key] = default
                return default
            else:
                self.add_error(key, f"Value {value} above maximum {max_value}")
                return default

        self.validated_config[key] = value
        return value

    def validate_boolean(
        self,
        key: str,
        default: bool = False
    ) -> bool:
        """
        Validate a boolean environment variable.

        Args:
            key: Environment variable name
            default: Default value

        Returns:
            Validated boolean value
        """
        value_str = os.environ.get(key, str(default)).lower().strip()

        truthy_values = {'true', '1', 'yes', 'on', 'enabled'}
        falsy_values = {'false', '0', 'no', 'off', 'disabled'}

        if value_str in truthy_values:
            self.validated_config[key] = True
            return True
        elif value_str in falsy_values:
            self.validated_config[key] = False
            return False
        else:
            self.add_warning(
                key,
                f"Invalid boolean '{value_str}', using default {default}"
            )
            self.validated_config[key] = default
            return default

    def validate_path(
        self,
        key: str,
        default: str,
        must_exist: bool = False,
        must_be_writable: bool = False,
        create_if_missing: bool = True
    ) -> Optional[str]:
        """
        Validate a file path environment variable.

        Args:
            key: Environment variable name
            default: Default path
            must_exist: Path must already exist
            must_be_writable: Path must be writable
            create_if_missing: Create directory if it doesn't exist

        Returns:
            Validated path or None if validation failed
        """
        path_str = os.environ.get(key, default)
        path = Path(path_str)

        if must_exist and not path.exists():
            if create_if_missing:
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    self.add_warning(
                        key,
                        f"Path did not exist, created: {path}"
                    )
                except Exception as e:
                    self.add_error(
                        key,
                        f"Cannot create path: {path} - {str(e)}"
                    )
                    return None
            else:
                self.add_error(key, f"Path does not exist: {path}")
                return None

        if must_be_writable:
            try:
                test_file = path / '.write_test'
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                self.add_error(
                    key,
                    f"Path is not writable: {path} - {str(e)}"
                )
                return None

        self.validated_config[key] = str(path)
        return str(path)

    def validate_comma_separated(
        self,
        key: str,
        default: str,
        allowed_values: Optional[List[str]] = None
    ) -> List[str]:
        """
        Validate a comma-separated list environment variable.

        Args:
            key: Environment variable name
            default: Default comma-separated values
            allowed_values: List of allowed individual values

        Returns:
            List of validated values
        """
        value_str = os.environ.get(key, default)
        items = [item.strip() for item in value_str.split(',') if item.strip()]

        if not items:
            self.add_error(key, "No valid items in comma-separated list")
            return []

        if allowed_values:
            invalid_items = [item for item in items if item not in allowed_values]
            if invalid_items:
                self.add_error(
                    key,
                    f"Invalid items: {', '.join(invalid_items)}. "
                    f"Allowed: {', '.join(allowed_values)}"
                )
                return []

        self.validated_config[key] = items
        return items

    def has_errors(self) -> bool:
        """Check if any validation errors occurred"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if any validation warnings occurred"""
        return len(self.warnings) > 0

    def raise_if_errors(self):
        """Raise ConfigurationError if any validation errors occurred"""
        if self.has_errors():
            error_summary = "\n".join(self.errors)
            raise ConfigurationError(
                f"Configuration validation failed with {len(self.errors)} error(s):\n{error_summary}"
            )

    def report(self):
        """Print a summary report of validation results"""
        config_logger.info("=" * 80)
        config_logger.info("CONFIGURATION VALIDATION REPORT")
        config_logger.info("=" * 80)

        if self.has_errors():
            config_logger.error(f"ERRORS ({len(self.errors)}):")
            for error in self.errors:
                config_logger.error(f"  {error}")

        if self.has_warnings():
            config_logger.warning(f"WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                config_logger.warning(f"  {warning}")

        if not self.has_errors() and not self.has_warnings():
            config_logger.info("All configuration validated successfully!")

        config_logger.info("=" * 80)


def load_and_validate_config() -> Dict[str, Any]:
    """
    Load and validate all configuration from environment variables.

    Returns:
        Dictionary of validated configuration values

    Raises:
        ConfigurationError: If critical validation errors occur
    """
    validator = ConfigValidator()

    config_logger.info("Starting configuration validation...")

    # ========================================================================
    # FLASK APPLICATION SETTINGS
    # ========================================================================
    flask_env = validator.validate_required_string(
        'FLASK_ENV',
        default='production',
        allowed_values=['development', 'production', 'testing']
    )

    flask_debug = validator.validate_boolean('FLASK_DEBUG', default=False)

    # Validate SECRET_KEY for production
    secret_key = os.environ.get('SECRET_KEY', None)
    if flask_env == 'production' and (not secret_key or len(secret_key) < 32):
        validator.add_error(
            'SECRET_KEY',
            'Production mode requires SECRET_KEY env var with minimum 32 characters'
        )
    elif not secret_key:
        secret_key = 'dev-key-change-in-production'
        validator.add_warning('SECRET_KEY', 'Using insecure default key (development only)')

    validator.validated_config['SECRET_KEY'] = secret_key

    server_host = validator.validate_required_string(
        'SERVER_HOST',
        default='0.0.0.0',
        allowed_values=['0.0.0.0', '127.0.0.1', 'localhost']
    )

    server_port = validator.validate_integer(
        'SERVER_PORT',
        default=5000,
        min_value=1024,
        max_value=65535
    )

    # ========================================================================
    # FILE UPLOAD & STORAGE
    # ========================================================================
    upload_folder = validator.validate_path(
        'UPLOAD_FOLDER',
        default='/tmp/sc-uploads',
        must_be_writable=True,
        create_if_missing=True
    )

    output_folder = validator.validate_path(
        'OUTPUT_FOLDER',
        default='/tmp/sc-outputs',
        must_be_writable=True,
        create_if_missing=True
    )

    max_file_size_mb = validator.validate_integer(
        'MAX_FILE_SIZE_MB',
        default=100,
        min_value=1,
        max_value=10000
    )

    allowed_extensions = validator.validate_comma_separated(
        'ALLOWED_EXTENSIONS',
        default='msi,exe,dll,bat,cmd,vbs',
        allowed_values=['msi', 'exe', 'dll', 'bat', 'cmd', 'vbs', 'ps1']
    )

    # ========================================================================
    # REQUEST TIMEOUT CONFIGURATION
    # ========================================================================
    request_timeout = validator.validate_integer(
        'REQUEST_TIMEOUT_SECONDS',
        default=30,
        min_value=5,
        max_value=600
    )

    upload_timeout = validator.validate_integer(
        'UPLOAD_TIMEOUT_SECONDS',
        default=300,
        min_value=60,
        max_value=3600
    )

    generate_timeout = validator.validate_integer(
        'GENERATE_TIMEOUT_SECONDS',
        default=120,
        min_value=10,
        max_value=1800
    )

    download_timeout = validator.validate_integer(
        'DOWNLOAD_TIMEOUT_SECONDS',
        default=60,
        min_value=5,
        max_value=600
    )

    # ========================================================================
    # SECURITY SETTINGS
    # ========================================================================
    cors_enabled = validator.validate_boolean('CORS_ENABLED', default=True)

    cors_origins = validator.validate_comma_separated(
        'CORS_ORIGINS',
        default='http://localhost:3000,http://localhost:8080'
    )

    max_json_size = validator.validate_integer(
        'MAX_JSON_SIZE',
        default=16777216,  # 16MB
        min_value=1048576,  # 1MB
        max_value=104857600  # 100MB
    )

    # ========================================================================
    # LOGGING CONFIGURATION
    # ========================================================================
    log_level = validator.validate_required_string(
        'LOG_LEVEL',
        default='INFO',
        allowed_values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    )

    log_file = validator.validate_path(
        'LOG_FILE',
        default='/tmp/sc-generator.log',
        create_if_missing=False
    )

    log_max_size = validator.validate_integer(
        'LOG_MAX_SIZE',
        default=10485760,  # 10MB
        min_value=1048576,  # 1MB
        max_value=104857600  # 100MB
    )

    log_backup_count = validator.validate_integer(
        'LOG_BACKUP_COUNT',
        default=5,
        min_value=1,
        max_value=100
    )

    # ========================================================================
    # CLEANUP CONFIGURATION
    # ========================================================================
    cleanup_interval = validator.validate_integer(
        'CLEANUP_INTERVAL_HOURS',
        default=24,
        min_value=1,
        max_value=720
    )

    file_retention = validator.validate_integer(
        'FILE_RETENTION_HOURS',
        default=72,
        min_value=1,
        max_value=2160
    )

    # ========================================================================
    # FINGERPRINT & PROXY CONFIGURATION
    # ========================================================================
    fingerprint_db = validator.validate_path(
        'FINGERPRINT_DB_PATH',
        default='/tmp/sc-fingerprints.db',
        create_if_missing=False
    )

    proxy_timeout = validator.validate_integer(
        'PROXY_TIMEOUT_SECONDS',
        default=30,
        min_value=1,
        max_value=300
    )

    # ========================================================================
    # OBFUSCATION SETTINGS
    # ========================================================================
    obfuscation_level = validator.validate_required_string(
        'OBFUSCATION_DEFAULT_LEVEL',
        default='high',
        allowed_values=['low', 'medium', 'high']
    )

    polymorphic_variants = validator.validate_integer(
        'POLYMORPHIC_VARIANTS',
        default=5,
        min_value=1,
        max_value=20
    )

    # Build final configuration dictionary
    config = {
        # Flask settings
        'FLASK_ENV': flask_env,
        'FLASK_DEBUG': flask_debug,
        'SECRET_KEY': secret_key,
        'SERVER_HOST': server_host,
        'SERVER_PORT': server_port,

        # File settings
        'UPLOAD_FOLDER': upload_folder,
        'OUTPUT_FOLDER': output_folder,
        'MAX_FILE_SIZE_MB': max_file_size_mb,
        'MAX_FILE_SIZE': max_file_size_mb * 1024 * 1024,
        'ALLOWED_EXTENSIONS': allowed_extensions,

        # Request timeouts
        'REQUEST_TIMEOUT_SECONDS': request_timeout,
        'UPLOAD_TIMEOUT_SECONDS': upload_timeout,
        'GENERATE_TIMEOUT_SECONDS': generate_timeout,
        'DOWNLOAD_TIMEOUT_SECONDS': download_timeout,

        # Security
        'CORS_ENABLED': cors_enabled,
        'CORS_ORIGINS': cors_origins,
        'MAX_JSON_SIZE': max_json_size,

        # Logging
        'LOG_LEVEL': log_level,
        'LOG_FILE': log_file,
        'LOG_MAX_SIZE': log_max_size,
        'LOG_BACKUP_COUNT': log_backup_count,

        # Cleanup
        'CLEANUP_INTERVAL_HOURS': cleanup_interval,
        'FILE_RETENTION_HOURS': file_retention,

        # Fingerprint & Proxy
        'FINGERPRINT_DB_PATH': fingerprint_db,
        'PROXY_TIMEOUT_SECONDS': proxy_timeout,

        # Obfuscation
        'OBFUSCATION_DEFAULT_LEVEL': obfuscation_level,
        'POLYMORPHIC_VARIANTS': polymorphic_variants,
    }

    # Print validation report
    validator.report()

    # Raise exception if critical errors
    validator.raise_if_errors()

    return config


def get_config() -> Dict[str, Any]:
    """
    Get validated configuration singleton.

    Returns:
        Validated configuration dictionary

    Raises:
        ConfigurationError: If validation fails
    """
    if not hasattr(get_config, '_config'):
        get_config._config = load_and_validate_config()
    return get_config._config


if __name__ == '__main__':
    try:
        config = get_config()
        print("\nConfiguration loaded successfully!")
        print(f"Server: {config['SERVER_HOST']}:{config['SERVER_PORT']}")
        print(f"Upload folder: {config['UPLOAD_FOLDER']}")
        print(f"Output folder: {config['OUTPUT_FOLDER']}")
        print(f"Max file size: {config['MAX_FILE_SIZE_MB']} MB")
        sys.exit(0)
    except ConfigurationError as e:
        print(f"\nConfiguration Error: {e}", file=sys.stderr)
        sys.exit(1)
