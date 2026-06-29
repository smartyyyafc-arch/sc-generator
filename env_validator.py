#!/usr/bin/env python3
"""
Environment Configuration Validator
Validates all required environment variables and ensures secure defaults
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, List

logger = logging.getLogger(__name__)

# ============================================================================
# Environment Variable Schema Definition
# ============================================================================
ENV_SCHEMA = {
    # Flask Settings
    'FLASK_ENV': {
        'type': str,
        'default': 'production',
        'choices': ['development', 'testing', 'production'],
        'description': 'Flask environment mode',
        'required': False,
    },
    'FLASK_DEBUG': {
        'type': bool,
        'default': False,
        'description': 'Debug mode (NEVER enable in production)',
        'required': False,
    },
    'SECRET_KEY': {
        'type': str,
        'default': None,
        'min_length': 32,
        'description': 'Session secret key (must be 32+ characters)',
        'required': True,
        'is_sensitive': True,
    },
    'SERVER_HOST': {
        'type': str,
        'default': '0.0.0.0',
        'description': 'Server bind address',
        'required': False,
    },
    'SERVER_PORT': {
        'type': int,
        'default': 5000,
        'min': 1024,
        'max': 65535,
        'description': 'Server port number',
        'required': False,
    },

    # File Upload & Storage
    'UPLOAD_FOLDER': {
        'type': str,
        'default': '/tmp/sc-uploads',
        'description': 'Directory for uploaded files',
        'required': False,
        'is_path': True,
    },
    'OUTPUT_FOLDER': {
        'type': str,
        'default': '/tmp/sc-outputs',
        'description': 'Directory for generated payloads',
        'required': False,
        'is_path': True,
    },
    'MAX_FILE_SIZE_MB': {
        'type': int,
        'default': 100,
        'min': 1,
        'max': 5000,
        'description': 'Maximum file size in MB',
        'required': False,
    },
    'ALLOWED_EXTENSIONS': {
        'type': str,
        'default': 'msi,exe,dll,bat,cmd,vbs',
        'description': 'Allowed file extensions (comma-separated)',
        'required': False,
    },

    # Request Timeouts
    'REQUEST_TIMEOUT_SECONDS': {
        'type': int,
        'default': 30,
        'min': 5,
        'description': 'Standard request timeout (minimum: 5 seconds)',
        'required': False,
    },
    'UPLOAD_TIMEOUT_SECONDS': {
        'type': int,
        'default': 300,
        'min': 60,
        'description': 'File upload timeout (minimum: 60 seconds)',
        'required': False,
    },
    'GENERATE_TIMEOUT_SECONDS': {
        'type': int,
        'default': 120,
        'min': 10,
        'description': 'Payload generation timeout (minimum: 10 seconds)',
        'required': False,
    },
    'DOWNLOAD_TIMEOUT_SECONDS': {
        'type': int,
        'default': 60,
        'min': 5,
        'description': 'File download timeout (minimum: 5 seconds)',
        'required': False,
    },

    # Rate Limiting
    'RATE_LIMIT_ENABLED': {
        'type': bool,
        'default': True,
        'description': 'Enable rate limiting',
        'required': False,
    },
    'RATE_LIMIT_PER_IP': {
        'type': int,
        'default': 100,
        'min': 1,
        'description': 'Requests per minute per IP',
        'required': False,
    },
    'RATE_LIMIT_GLOBAL': {
        'type': int,
        'default': 1000,
        'min': 1,
        'description': 'Global requests per minute limit',
        'required': False,
    },
    'RATE_LIMIT_CLEANUP_INTERVAL': {
        'type': int,
        'default': 300,
        'min': 60,
        'description': 'Rate limit cleanup interval (seconds)',
        'required': False,
    },
    'RATE_LIMIT_UPLOAD': {
        'type': int,
        'default': 10,
        'min': 1,
        'description': 'Upload endpoint rate limit per minute',
        'required': False,
    },
    'RATE_LIMIT_GENERATE': {
        'type': int,
        'default': 20,
        'min': 1,
        'description': 'Generate payload rate limit per minute',
        'required': False,
    },
    'RATE_LIMIT_ONE_CLICK': {
        'type': int,
        'default': 15,
        'min': 1,
        'description': 'One-click installer rate limit per minute',
        'required': False,
    },
    'RATE_LIMIT_PERSISTENT': {
        'type': int,
        'default': 10,
        'min': 1,
        'description': 'Persistent payload rate limit per minute',
        'required': False,
    },
    'RATE_LIMIT_BATCH': {
        'type': int,
        'default': 5,
        'min': 1,
        'description': 'Batch generation rate limit per minute',
        'required': False,
    },
    'RATE_LIMIT_DOWNLOAD': {
        'type': int,
        'default': 50,
        'min': 1,
        'description': 'Download rate limit per minute',
        'required': False,
    },
    'RATE_LIMIT_PREVIEW': {
        'type': int,
        'default': 50,
        'min': 1,
        'description': 'Preview rate limit per minute',
        'required': False,
    },
    'RATE_LIMIT_WHITELIST': {
        'type': str,
        'default': '127.0.0.1',
        'description': 'IP addresses to whitelist from rate limiting',
        'required': False,
    },

    # Security
    'CORS_ENABLED': {
        'type': bool,
        'default': True,
        'description': 'Enable CORS',
        'required': False,
    },
    'CORS_ORIGINS': {
        'type': str,
        'default': 'http://localhost:3000,http://localhost:8080',
        'description': 'CORS allowed origins (comma-separated)',
        'required': False,
    },
    'MAX_JSON_SIZE': {
        'type': int,
        'default': 16777216,
        'min': 1024,
        'description': 'Maximum JSON request body size (bytes)',
        'required': False,
    },

    # Logging
    'LOG_LEVEL': {
        'type': str,
        'default': 'INFO',
        'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        'description': 'Logging level',
        'required': False,
    },
    'LOG_FILE': {
        'type': str,
        'default': '/var/log/sc-generator/app.log',
        'description': 'Log file path',
        'required': False,
        'is_path': True,
    },
    'LOG_MAX_SIZE': {
        'type': int,
        'default': 10485760,
        'min': 1048576,
        'description': 'Maximum log file size (bytes)',
        'required': False,
    },
    'LOG_BACKUP_COUNT': {
        'type': int,
        'default': 5,
        'min': 1,
        'max': 50,
        'description': 'Number of backup log files to keep',
        'required': False,
    },

    # Cleanup
    'CLEANUP_INTERVAL_HOURS': {
        'type': int,
        'default': 24,
        'min': 1,
        'description': 'Auto-cleanup interval (hours)',
        'required': False,
    },
    'FILE_RETENTION_HOURS': {
        'type': int,
        'default': 72,
        'min': 1,
        'description': 'File retention period (hours)',
        'required': False,
    },

    # Fingerprint & Proxy
    'FINGERPRINT_DB_PATH': {
        'type': str,
        'default': '/tmp/sc-fingerprints.db',
        'description': 'Fingerprint database path',
        'required': False,
        'is_path': True,
    },
    'PROXY_TIMEOUT_SECONDS': {
        'type': int,
        'default': 30,
        'min': 5,
        'description': 'Proxy connection timeout (seconds)',
        'required': False,
    },

    # Obfuscation
    'OBFUSCATION_DEFAULT_LEVEL': {
        'type': str,
        'default': 'high',
        'choices': ['low', 'medium', 'high'],
        'description': 'Default obfuscation level',
        'required': False,
    },
    'POLYMORPHIC_VARIANTS': {
        'type': int,
        'default': 5,
        'min': 1,
        'max': 50,
        'description': 'Number of polymorphic variants',
        'required': False,
    },
    'NOISE_RATIO': {
        'type': float,
        'default': 0.3,
        'min': 0.0,
        'max': 1.0,
        'description': 'Noise injection ratio',
        'required': False,
    },
}


class EnvironmentValidator:
    """Validates and loads environment configuration"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.config: Dict[str, Any] = {}

    def validate(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate all environment variables against schema

        Returns:
            Tuple of (success, config_dict)
        """
        for var_name, schema in ENV_SCHEMA.items():
            self._validate_variable(var_name, schema)

        if self.errors:
            self._print_errors()
            return False, {}

        if self.warnings:
            self._print_warnings()

        return True, self.config

    def _validate_variable(self, var_name: str, schema: Dict[str, Any]) -> None:
        """Validate a single environment variable"""
        env_value = os.environ.get(var_name)

        # Check if required
        if schema.get('required', False) and env_value is None:
            self.errors.append(
                f"REQUIRED: {var_name} not set. {schema.get('description', '')}"
            )
            return

        # Use default if not provided
        if env_value is None:
            default = schema.get('default')
            if default is not None:
                self.config[var_name] = default
            return

        # Parse value to correct type
        try:
            parsed_value = self._parse_value(env_value, schema)
        except ValueError as e:
            self.errors.append(f"{var_name}: {str(e)}")
            return

        # Validate constraints
        validation_error = self._validate_constraints(var_name, parsed_value, schema)
        if validation_error:
            self.errors.append(validation_error)
            return

        # Path validation
        if schema.get('is_path'):
            path_error = self._validate_path(var_name, parsed_value)
            if path_error:
                self.warnings.append(path_error)

        # Sensitivity warning
        if schema.get('is_sensitive') and env_value == 'your-super-secret-key-change-this-in-production':
            self.errors.append(
                f"SECURITY: {var_name} contains default value. "
                "Change to a secure random value before production deployment."
            )

        self.config[var_name] = parsed_value

    def _parse_value(self, value: str, schema: Dict[str, Any]) -> Any:
        """Parse string value to correct type"""
        var_type = schema.get('type', str)

        if var_type == bool:
            if value.lower() in ('true', '1', 'yes', 'on'):
                return True
            elif value.lower() in ('false', '0', 'no', 'off'):
                return False
            else:
                raise ValueError(f"Invalid boolean value: {value}")

        elif var_type == int:
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Expected integer, got: {value}")

        elif var_type == float:
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"Expected float, got: {value}")

        return value

    def _validate_constraints(self, var_name: str, value: Any, schema: Dict[str, Any]) -> str:
        """Validate value against schema constraints"""
        # Check choices
        if 'choices' in schema and value not in schema['choices']:
            return (
                f"{var_name}: '{value}' not in allowed values: "
                f"{', '.join(map(str, schema['choices']))}"
            )

        # Check min/max for integers
        if isinstance(value, int):
            if 'min' in schema and value < schema['min']:
                return f"{var_name}: {value} is below minimum {schema['min']}"
            if 'max' in schema and value > schema['max']:
                return f"{var_name}: {value} exceeds maximum {schema['max']}"

        # Check min/max for floats
        if isinstance(value, float):
            if 'min' in schema and value < schema['min']:
                return f"{var_name}: {value} is below minimum {schema['min']}"
            if 'max' in schema and value > schema['max']:
                return f"{var_name}: {value} exceeds maximum {schema['max']}"

        # Check string length
        if isinstance(value, str) and 'min_length' in schema:
            if len(value) < schema['min_length']:
                return (
                    f"{var_name}: value too short "
                    f"(minimum {schema['min_length']} characters)"
                )

        return ""

    def _validate_path(self, var_name: str, path_str: str) -> str:
        """Validate directory path exists and is writable"""
        path = Path(path_str)

        # Try to create directory if it doesn't exist
        try:
            path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            return (
                f"WARNING: Cannot create directory {var_name}={path_str}. "
                "Ensure the directory exists and is writable."
            )
        except Exception as e:
            return (
                f"WARNING: Error validating path {var_name}={path_str}: {str(e)}"
            )

        # Check if writable
        if not os.access(path, os.W_OK):
            return (
                f"WARNING: Directory {var_name}={path_str} is not writable. "
                "Ensure proper permissions are set."
            )

        return ""

    def _print_errors(self) -> None:
        """Print validation errors"""
        print("\n" + "="*80, file=sys.stderr)
        print("ENVIRONMENT CONFIGURATION ERRORS", file=sys.stderr)
        print("="*80, file=sys.stderr)
        for error in self.errors:
            print(f"  ✗ {error}", file=sys.stderr)
        print("="*80, file=sys.stderr)

    def _print_warnings(self) -> None:
        """Print validation warnings"""
        if not self.warnings:
            return
        print("\n" + "="*80)
        print("ENVIRONMENT CONFIGURATION WARNINGS")
        print("="*80)
        for warning in self.warnings:
            print(f"  ⚠ {warning}")
        print("="*80 + "\n")


def validate_environment() -> Tuple[bool, Dict[str, Any]]:
    """
    Load and validate environment configuration

    Returns:
        Tuple of (success, config_dict)

    Example:
        success, config = validate_environment()
        if success:
            DEBUG = config['FLASK_DEBUG']
        else:
            sys.exit(1)
    """
    validator = EnvironmentValidator()
    return validator.validate()


if __name__ == '__main__':
    # Test validation
    success, config = validate_environment()

    if success:
        print("\n✓ All environment variables validated successfully!\n")
        print("Loaded configuration:")
        for key, value in sorted(config.items()):
            # Don't print sensitive values
            if any(sensitive in key for sensitive in ['SECRET', 'PASSWORD', 'KEY', 'TOKEN']):
                print(f"  {key} = ****hidden****")
            else:
                print(f"  {key} = {value}")
    else:
        print("\n✗ Environment validation failed!", file=sys.stderr)
        sys.exit(1)
