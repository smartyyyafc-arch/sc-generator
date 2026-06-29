# Advanced Code Protection Features

This guide covers advanced techniques for maximum protection:
- Anti-tampering detection
- License verification
- Runtime protection
- Secure deployment

---

## ANTI-TAMPERING PROTECTION

### What is Anti-Tampering?
Anti-tampering detection prevents unauthorized modifications to your code after distribution.

### Implementation

Create a file: `anti_tampering.py`

```python
"""
Anti-Tampering Module

This module provides code integrity verification.
After obfuscation, these checks are protected.
"""

import hashlib
import sys
import os


class IntegrityChecker:
    """
    Verifies that the executable hasn't been modified.

    How it works:
    1. Calculate hash of critical files
    2. On startup, recalculate hash
    3. If hash differs, code has been tampered with
    4. Exit immediately to prevent unauthorized use
    """

    # This checksum is calculated at build time
    # Replace with actual checksum of your executable
    EXPECTED_CHECKSUM = "your-checksum-here"

    @classmethod
    def verify_integrity(cls, file_path):
        """
        Verify that a file hasn't been modified.

        Args:
            file_path: Path to file to verify

        Returns:
            True if file is intact, False if tampered
        """
        try:
            # Calculate SHA256 hash of the file
            sha256_hash = hashlib.sha256()

            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)

            calculated_checksum = sha256_hash.hexdigest()

            # Compare with expected checksum
            if calculated_checksum != cls.EXPECTED_CHECKSUM:
                return False

            return True

        except Exception as e:
            # If we can't verify, assume tampering
            print(f"ERROR: Cannot verify integrity: {e}")
            return False

    @classmethod
    def verify_or_exit(cls, file_path):
        """
        Verify integrity and exit if tampering detected.

        Args:
            file_path: Path to file to verify
        """
        if not cls.verify_integrity(file_path):
            print("ERROR: Code integrity check failed!")
            print("This application may have been modified.")
            print("For security, the application will exit immediately.")
            sys.exit(1)


class EnvironmentChecker:
    """
    Detects if code is running in a debugger or analysis environment.

    After obfuscation, these checks are protected.
    """

    @staticmethod
    def is_debugger_attached():
        """
        Check if debugger is attached.

        Returns:
            True if debugger is detected, False otherwise
        """
        # Check for common debugger environment variables
        debugger_vars = [
            'DEBUG',
            'DEBUGGING',
            'DEBUGGER',
            'PYDEVD_DISABLE_FILE_VALIDATION',
        ]

        for var in debugger_vars:
            if os.environ.get(var):
                return True

        # Check for debugger modules
        try:
            import pdb
            if hasattr(pdb, 'set_trace'):
                # Don't actually call it, just check if module loaded
                pass

            import debugpy
            return True
        except ImportError:
            pass

        return False

    @staticmethod
    def is_analysis_tool_running():
        """
        Check if code analysis tools are running.

        Returns:
            True if analysis tools detected, False otherwise
        """
        analysis_tools = [
            'pyinstaller',
            'py2exe',
            'cx_Freeze',
            'pyarmor',
            'frida',
            'objection',
        ]

        for tool in analysis_tools:
            try:
                __import__(tool)
                return True
            except ImportError:
                pass

        return False

    @staticmethod
    def check_environment():
        """
        Check if code is running in a safe environment.

        Exits if suspicious environment detected.
        """
        if EnvironmentChecker.is_debugger_attached():
            print("ERROR: Debugger detected!")
            print("This application does not run under debuggers.")
            sys.exit(1)

        if EnvironmentChecker.is_analysis_tool_running():
            print("ERROR: Analysis tools detected!")
            print("This application cannot be analyzed.")
            sys.exit(1)


def verify_at_startup():
    """
    Perform all integrity checks at application startup.

    Call this as the first thing in your main() function.
    """
    print("Verifying code integrity...")

    # Check environment
    EnvironmentChecker.check_environment()

    # Check file integrity
    current_file = sys.argv[0]
    IntegrityChecker.verify_or_exit(current_file)

    print("✓ Integrity check passed")
```

### Using Anti-Tampering in Your Application

```python
# In your main application file (before obfuscation)

from anti_tampering import verify_at_startup

def main():
    """Main application entry point."""
    # FIRST: Verify code integrity
    verify_at_startup()

    # THEN: Run your application
    print("Application running...")
    # Your application code here


if __name__ == "__main__":
    main()
```

### Calculating and Setting the Checksum

```bash
# After creating your executable with PyInstaller:

# On Linux/Mac:
sha256sum ./dist/YourApp > checksum.txt

# On Windows (PowerShell):
certutil -hashfile dist\YourApp.exe SHA256

# Copy the checksum and update EXPECTED_CHECKSUM in anti_tampering.py
# Then re-obfuscate and re-package
```

---

## LICENSE VERIFICATION

### Create License Module

Create a file: `license_manager.py`

```python
"""
License Verification Module

Implements license key validation for protected applications.
After obfuscation, license verification is encrypted.
"""

import os
import datetime
import hashlib
import sys


class LicenseManager:
    """
    Manages license verification and enforcement.

    Supports:
    - License key validation
    - Expiration date checking
    - Device fingerprinting
    - Usage tracking
    """

    # Valid license keys (in production, verify against licensing server)
    VALID_LICENSES = {
        'KEY-2024-ENTERPRISE-001': {
            'tier': 'enterprise',
            'expires': datetime.datetime(2025, 12, 31),
            'features': ['all'],
            'max_uses': None,  # Unlimited
        },
        'KEY-2024-PROFESSIONAL-001': {
            'tier': 'professional',
            'expires': datetime.datetime(2025, 6, 30),
            'features': ['basic', 'advanced'],
            'max_uses': 1000,
        },
        'KEY-2024-TRIAL-001': {
            'tier': 'trial',
            'expires': datetime.datetime(2024, 7, 31),
            'features': ['basic'],
            'max_uses': 100,
        },
    }

    def __init__(self):
        """Initialize the license manager."""
        self.license_key = None
        self.license_info = None
        self.use_count = 0

    def load_license_from_environment(self):
        """
        Load license key from environment variable.

        Returns:
            License key string, or None if not found
        """
        license_key = os.environ.get('LICENSE_KEY')

        if not license_key:
            return None

        self.license_key = license_key
        return license_key

    def load_license_from_file(self, file_path):
        """
        Load license key from file.

        Args:
            file_path: Path to license file

        Returns:
            License key string, or None if file not found
        """
        try:
            with open(file_path, 'r') as f:
                license_key = f.read().strip()

            self.license_key = license_key
            return license_key

        except FileNotFoundError:
            return None

        except Exception as e:
            print(f"ERROR: Could not read license file: {e}")
            return None

    def validate_license(self, license_key):
        """
        Validate a license key.

        Args:
            license_key: License key to validate

        Returns:
            License info dict if valid, None if invalid
        """
        # Check if key exists in valid licenses
        if license_key not in self.VALID_LICENSES:
            return None

        license_info = self.VALID_LICENSES[license_key]

        # Check expiration
        if datetime.datetime.now() > license_info['expires']:
            return None

        # License is valid
        self.license_key = license_key
        self.license_info = license_info
        return license_info

    def check_license_or_exit(self):
        """
        Check license and exit if invalid.

        Tries:
        1. Environment variable LICENSE_KEY
        2. File ~/license.key
        3. File /etc/license.key (Linux)

        Exits if no valid license found.
        """
        # Try to load license from environment
        license_key = self.load_license_from_environment()

        # Try to load from file if environment variable not set
        if not license_key:
            license_key = self.load_license_from_file(
                os.path.expanduser("~/license.key")
            )

        # Try system location (Linux)
        if not license_key:
            license_key = self.load_license_from_file("/etc/license.key")

        # Validate the license
        if not license_key or not self.validate_license(license_key):
            print("ERROR: Invalid or missing license key!")
            print()
            print("To use this application, you need a valid license.")
            print()
            print("Provide license key by:")
            print("  1. Set environment variable: export LICENSE_KEY='your-key'")
            print("  2. Create file ~/.license.key with your license key")
            print("  3. Contact support for a license key")
            print()
            sys.exit(1)

        print(f"✓ License verified: {self.license_info['tier']}")

    def check_feature_access(self, feature_name):
        """
        Check if a feature is available under current license.

        Args:
            feature_name: Name of feature to check

        Returns:
            True if feature is available, False otherwise
        """
        if not self.license_info:
            return False

        if 'all' in self.license_info['features']:
            return True

        return feature_name in self.license_info['features']

    def track_usage(self):
        """
        Track usage for licensing compliance.

        Some licenses have usage limits.
        """
        self.use_count += 1

        # Check usage limit
        if self.license_info and self.license_info['max_uses']:
            if self.use_count > self.license_info['max_uses']:
                print("ERROR: Usage limit exceeded for this license!")
                print(f"Limit: {self.license_info['max_uses']} uses")
                print(f"Current: {self.use_count} uses")
                sys.exit(1)

    def get_expiration_date(self):
        """
        Get license expiration date.

        Returns:
            datetime object, or None if not set
        """
        if self.license_info:
            return self.license_info['expires']

        return None

    def get_days_until_expiration(self):
        """
        Get days until license expires.

        Returns:
            Number of days, or -1 if already expired
        """
        expiration = self.get_expiration_date()

        if not expiration:
            return None

        delta = expiration - datetime.datetime.now()
        return delta.days


# Global license manager instance
_license_manager = None


def initialize_license_manager():
    """Initialize global license manager."""
    global _license_manager

    if _license_manager is None:
        _license_manager = LicenseManager()

    return _license_manager


def verify_license():
    """
    Verify license at application startup.

    Call this as the first thing in your main() function.
    """
    manager = initialize_license_manager()
    manager.check_license_or_exit()
    return manager


def get_license_manager():
    """Get the global license manager instance."""
    global _license_manager

    if _license_manager is None:
        _license_manager = LicenseManager()

    return _license_manager
```

### Using License Verification

```python
# In your main application file (before obfuscation)

from license_manager import verify_license, get_license_manager

def main():
    """Main application entry point."""
    # FIRST: Verify license
    license_mgr = verify_license()

    print(f"License tier: {license_mgr.license_info['tier']}")
    print(f"Expires: {license_mgr.get_expiration_date()}")
    print(f"Days left: {license_mgr.get_days_until_expiration()}")

    # Check if premium features are available
    if license_mgr.check_feature_access('advanced'):
        print("Advanced features available")

    # THEN: Run your application
    print("\nApplication running...")


if __name__ == "__main__":
    main()
```

### Distributing with License Keys

```bash
# For end users, provide license key via environment:

export LICENSE_KEY="KEY-2024-PROFESSIONAL-001"
./dist/ProtectedApp

# Or create a file:
echo "KEY-2024-PROFESSIONAL-001" > ~/.license.key
./dist/ProtectedApp
```

---

## SERVER-SIDE LICENSE VERIFICATION

For maximum security, verify licenses against a server:

```python
"""
Server-based license verification

For production systems, verify licenses against your backend service.
"""

import requests
import json


def verify_license_with_server(license_key, app_id):
    """
    Verify license key against licensing server.

    Args:
        license_key: License key to verify
        app_id: Application identifier

    Returns:
        License info dict if valid, None if invalid

    Note:
        - Requires HTTPS connection
        - Should cache results to handle server downtime
        - Include device fingerprint for device-specific licenses
    """
    try:
        # Connect to licensing server (use HTTPS)
        response = requests.post(
            "https://licensing.example.com/api/verify",
            json={
                "license_key": license_key,
                "app_id": app_id,
                "timestamp": datetime.datetime.now().isoformat(),
            },
            timeout=5
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except requests.RequestException:
        # If server is unreachable, use cached verification
        return verify_license_cached(license_key)


def verify_license_cached(license_key):
    """
    Use cached license verification if server is unavailable.

    This allows the application to work offline for a limited time.
    """
    # Cache file location
    cache_file = os.path.expanduser("~/.app_license_cache")

    try:
        with open(cache_file, 'r') as f:
            cache = json.load(f)

        if license_key in cache:
            cached_info = cache[license_key]

            # Check if cache is still valid (e.g., less than 30 days old)
            cached_time = datetime.datetime.fromisoformat(
                cached_info['timestamp']
            )
            age = datetime.datetime.now() - cached_time

            if age.days < 30:
                return cached_info

    except (FileNotFoundError, json.JSONDecodeError):
        pass

    return None
```

---

## DEPLOYMENT BEST PRACTICES

### 1. Code Signing

Sign your executable to prevent tampering and warnings:

```bash
# On Windows with signtool:
signtool sign /f certificate.pfx /p password /t http://timestamp.server.com \
    dist\YourApp.exe

# Verify signature:
signtool verify /pa dist\YourApp.exe
```

### 2. Distribution

```bash
# Create distribution package:
mkdir distribution
cp dist/YourApp dist/distribution/

# Add documentation and license:
cp LICENSE.txt distribution/
cp README.txt distribution/
cp SETUP_INSTRUCTIONS.txt distribution/

# Create archive:
zip -r distribution.zip distribution/
```

### 3. Version Control

Track protected releases separately:

```bash
# Keep releases in separate directory
mkdir releases
cp dist/YourApp releases/YourApp-v1.0.exe

# Sign with version info
echo "Version: 1.0.0" > releases/VERSION.txt
echo "Build date: $(date)" >> releases/VERSION.txt
echo "Checksum: $(sha256sum dist/YourApp)" >> releases/VERSION.txt
```

### 4. Update Mechanism

Implement automatic updates with verification:

```python
"""
Secure update mechanism
"""

import requests
import hashlib


def check_for_updates(current_version):
    """Check if update is available."""
    try:
        response = requests.get(
            "https://updates.example.com/latest-version",
            timeout=5
        )

        if response.status_code == 200:
            latest = response.json()
            return latest['version'] > current_version

    except requests.RequestException:
        # No internet, can't check
        pass

    return False


def download_and_verify_update(download_url, expected_sha256):
    """
    Download update and verify checksum.

    Args:
        download_url: URL to download update from
        expected_sha256: Expected SHA256 checksum

    Returns:
        Path to verified executable, or None if verification failed
    """
    try:
        # Download
        response = requests.get(download_url, timeout=30)
        update_data = response.content

        # Verify checksum
        calculated_sha256 = hashlib.sha256(update_data).hexdigest()

        if calculated_sha256 != expected_sha256:
            print("ERROR: Update verification failed!")
            return None

        # Save to file
        update_file = os.path.expanduser("~/.app_update")

        with open(update_file, 'wb') as f:
            f.write(update_data)

        return update_file

    except Exception as e:
        print(f"ERROR: Update download failed: {e}")
        return None
```

---

## SUMMARY

Advanced protection features:

1. **Anti-Tampering**
   - File integrity checking
   - Environment validation
   - Debugger detection

2. **License Verification**
   - License key validation
   - Expiration checking
   - Feature-based licensing
   - Usage tracking

3. **Server-Side Security**
   - Remote license verification
   - Cached validation for offline use
   - Update checking

4. **Deployment Security**
   - Code signing
   - Checksum verification
   - Secure distribution
   - Update mechanism

These features, combined with PyArmor obfuscation and PyInstaller packaging, provide enterprise-grade code protection.
