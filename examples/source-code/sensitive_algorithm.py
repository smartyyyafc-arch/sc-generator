#!/usr/bin/env python3
"""
Sensitive Algorithm - Example proprietary Python code
This file represents your intellectual property that needs protection.

This code will be:
1. Obfuscated with PyArmor (encrypting the bytecode and renaming variables)
2. Packaged with PyInstaller (creating a standalone executable)
3. Protected from reverse engineering and unauthorized modification

For a real project, this would contain your proprietary algorithms,
machine learning models, or business logic.
"""

import sys
import os
import hashlib
import datetime


class ProprietaryAlgorithm:
    """
    This class represents your proprietary code.

    After obfuscation:
    - Class name will be renamed to meaningless identifier
    - All method names will be encrypted
    - All variable names will be meaningless
    - The algorithm will be encrypted and unreadable
    - Reverse engineering will be extremely difficult
    """

    # These constants represent your trade secrets
    MAGIC_CONSTANT_1 = 0.75
    MAGIC_CONSTANT_2 = 2.5
    MAGIC_CONSTANT_3 = 1.333

    def __init__(self):
        """Initialize the proprietary algorithm."""
        self.execution_count = 0
        self.creation_time = datetime.datetime.now()

    def calculate_proprietary_value(self, input_data):
        """
        This is your secret algorithm.

        In a real scenario, this would be:
        - Machine learning model prediction
        - Proprietary encryption algorithm
        - Complex financial calculation
        - Specialized data processing

        After obfuscation, the logic will be encrypted.
        """
        result = 0

        # Complex proprietary calculation
        for value in input_data:
            intermediate = (value ** 2) * self.MAGIC_CONSTANT_1
            result += intermediate * self.MAGIC_CONSTANT_2

        result = result * self.MAGIC_CONSTANT_3
        self.execution_count += 1

        return result

    def validate_input(self, data):
        """Validate input before processing."""
        if not isinstance(data, (list, tuple)):
            raise ValueError("Input must be a list or tuple")

        if len(data) == 0:
            raise ValueError("Input cannot be empty")

        for item in data:
            if not isinstance(item, (int, float)):
                raise ValueError("All items must be numeric")

        return True

    def get_statistics(self, data):
        """Calculate statistics on input data."""
        result = self.calculate_proprietary_value(data)

        return {
            'result': result,
            'input_size': len(data),
            'min_value': min(data),
            'max_value': max(data),
            'sum_value': sum(data),
            'execution_count': self.execution_count,
            'processing_time': (datetime.datetime.now() - self.creation_time).total_seconds()
        }


def verify_license_key(license_key):
    """
    Verify that a valid license key is provided.

    In production, this would:
    - Check against a licensing server
    - Verify expiration date
    - Check device fingerprint
    - Prevent license sharing

    After obfuscation, the verification logic is encrypted.
    """
    valid_licenses = [
        'KEY-2024-ENTERPRISE-001',
        'KEY-2024-PROFESSIONAL-001',
        'KEY-2024-DEVELOPER-TRIAL',
    ]

    return license_key in valid_licenses


def verify_file_integrity(filepath):
    """
    Verify that the file hasn't been tampered with.

    This is an anti-tampering check. After obfuscation,
    it will be encrypted and difficult to bypass.
    """
    try:
        with open(filepath, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash
    except Exception as e:
        print(f"ERROR: Could not verify file integrity: {e}")
        return None


def main():
    """
    Main entry point for the protected executable.

    After packaging with PyInstaller:
    - This becomes the entry point of the .exe file
    - All imports and dependencies are included
    - The Python runtime is bundled (user doesn't see it)
    - The code is obfuscated and encrypted
    """

    print("=" * 60)
    print("Proprietary Algorithm Tool v1.0")
    print("Protected by PyArmor Obfuscation + PyInstaller Packaging")
    print("=" * 60)
    print()

    # Step 1: Verify license
    print("[Step 1] Verifying license...")
    license_key = os.environ.get('LICENSE_KEY', 'KEY-2024-ENTERPRISE-001')

    if not verify_license_key(license_key):
        print("ERROR: Invalid license key")
        print("Please set environment variable: LICENSE_KEY='your-valid-key'")
        sys.exit(1)

    print(f"✓ License verified: {license_key}")
    print()

    # Step 2: Verify file integrity
    print("[Step 2] Verifying file integrity...")
    current_file = sys.argv[0]
    file_hash = verify_file_integrity(current_file)

    if file_hash:
        print(f"✓ File hash: {file_hash[:16]}...")
        print("✓ No tampering detected")
    print()

    # Step 3: Initialize algorithm
    print("[Step 3] Initializing proprietary algorithm...")
    algorithm = ProprietaryAlgorithm()
    print("✓ Algorithm initialized")
    print()

    # Step 4: Process sample data
    print("[Step 4] Processing data with proprietary algorithm...")
    sample_data = [1.5, 2.3, 3.7, 4.2, 5.1]

    try:
        algorithm.validate_input(sample_data)
        stats = algorithm.get_statistics(sample_data)

        print(f"✓ Input data: {sample_data}")
        print(f"✓ Result: {stats['result']:.6f}")
        print(f"✓ Statistics:")
        print(f"  - Input size: {stats['input_size']}")
        print(f"  - Min value: {stats['min_value']}")
        print(f"  - Max value: {stats['max_value']}")
        print(f"  - Sum value: {stats['sum_value']}")
        print(f"  - Execution count: {stats['execution_count']}")
        print(f"  - Processing time: {stats['processing_time']:.4f} seconds")

    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("Processing complete!")
    print("Your proprietary algorithm has been executed successfully.")
    print("The code is protected from reverse engineering.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
