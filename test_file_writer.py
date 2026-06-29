#!/usr/bin/env python3
"""
Test File Writer Utility

Comprehensive testing framework that:
1. Writes payload to test file
2. Verifies file integrity
3. Executes the test file
4. Cleans up resources
5. Returns test results
"""

import os
import sys
import tempfile
import hashlib
import subprocess
import json
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TestResult:
    """Result of a single test execution"""
    test_name: str
    payload_written: bool
    payload_hash: str
    file_verified: bool
    file_path: str
    execution_status: str
    execution_output: str
    execution_error: str
    exit_code: int
    duration_seconds: float
    cleanup_successful: bool
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class TestFileWriter:
    """Manages test file writing, verification, execution, and cleanup"""

    def __init__(self, temp_dir: Optional[str] = None, verbose: bool = True):
        """
        Initialize TestFileWriter

        Args:
            temp_dir: Custom temp directory (defaults to system temp)
            verbose: Print status messages
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.verbose = verbose
        self.created_files: List[str] = []

    def log(self, message: str):
        """Print log message if verbose"""
        if self.verbose:
            print(f"[{datetime.now().isoformat()}] {message}")

    def calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()

    def write_payload(self, payload: str, filename: str) -> Tuple[bool, str]:
        """
        Write payload to file

        Args:
            payload: Content to write
            filename: Name of file to create

        Returns:
            Tuple of (success, file_path)
        """
        try:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(payload)

            self.created_files.append(file_path)
            self.log(f"Payload written to {file_path}")
            return True, file_path
        except Exception as e:
            self.log(f"Error writing payload: {e}")
            return False, str(e)

    def verify_file(self, file_path: str, expected_content: str) -> Tuple[bool, str]:
        """
        Verify file integrity

        Args:
            file_path: Path to file to verify
            expected_content: Expected file content

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            with open(file_path, 'r') as f:
                actual_content = f.read()

            if actual_content != expected_content:
                return False, "File content mismatch"

            # Additional checks
            if os.path.getsize(file_path) == 0:
                return False, "File is empty"

            self.log(f"File verified: {file_path}")
            return True, ""
        except Exception as e:
            return False, str(e)

    def execute_test(self, file_path: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute test file

        Args:
            file_path: Path to test file
            timeout: Execution timeout in seconds

        Returns:
            Dictionary with execution results
        """
        import time
        start_time = time.time()

        try:
            # Determine how to execute based on file extension
            extension = Path(file_path).suffix.lower()

            if extension == '.py':
                cmd = [sys.executable, file_path]
            elif extension == '.js':
                cmd = ['node', file_path]
            elif extension == '.sh':
                cmd = ['bash', file_path]
            else:
                # Try to execute directly
                cmd = [file_path]

            self.log(f"Executing: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            duration = time.time() - start_time

            return {
                'status': 'SUCCESS' if result.returncode == 0 else 'FAILED',
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration_seconds': duration,
                'error': None
            }
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return {
                'status': 'TIMEOUT',
                'exit_code': -1,
                'stdout': '',
                'stderr': f'Execution timed out after {timeout} seconds',
                'duration_seconds': duration,
                'error': 'TIMEOUT'
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                'status': 'ERROR',
                'exit_code': -1,
                'stdout': '',
                'stderr': str(e),
                'duration_seconds': duration,
                'error': type(e).__name__
            }

    def cleanup(self) -> bool:
        """
        Clean up created test files

        Returns:
            True if all files cleaned up successfully
        """
        all_success = True

        for file_path in self.created_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.log(f"Cleaned up: {file_path}")
            except Exception as e:
                self.log(f"Error cleaning up {file_path}: {e}")
                all_success = False

        self.created_files.clear()
        return all_success

    def run_test(self, payload: str, filename: str, timeout: int = 30) -> TestResult:
        """
        Run complete test cycle

        Args:
            payload: Test file content
            filename: Filename to create
            timeout: Execution timeout

        Returns:
            TestResult with all details
        """
        import time
        test_start = time.time()

        test_name = Path(filename).stem

        # Write payload
        write_success, file_path = self.write_payload(payload, filename)
        payload_hash = self.calculate_hash(payload)

        if not write_success:
            return TestResult(
                test_name=test_name,
                payload_written=False,
                payload_hash=payload_hash,
                file_verified=False,
                file_path=file_path,
                execution_status='SKIPPED',
                execution_output='',
                execution_error=f"Failed to write payload: {file_path}",
                exit_code=-1,
                duration_seconds=time.time() - test_start,
                cleanup_successful=False,
                timestamp=datetime.now().isoformat()
            )

        # Verify file
        file_verified, verify_error = self.verify_file(file_path, payload)

        if not file_verified:
            self.cleanup()
            return TestResult(
                test_name=test_name,
                payload_written=True,
                payload_hash=payload_hash,
                file_verified=False,
                file_path=file_path,
                execution_status='SKIPPED',
                execution_output='',
                execution_error=f"File verification failed: {verify_error}",
                exit_code=-1,
                duration_seconds=time.time() - test_start,
                cleanup_successful=False,
                timestamp=datetime.now().isoformat()
            )

        # Execute test
        exec_result = self.execute_test(file_path, timeout)

        # Cleanup
        cleanup_success = self.cleanup()

        return TestResult(
            test_name=test_name,
            payload_written=True,
            payload_hash=payload_hash,
            file_verified=True,
            file_path=file_path,
            execution_status=exec_result['status'],
            execution_output=exec_result['stdout'],
            execution_error=exec_result['stderr'],
            exit_code=exec_result['exit_code'],
            duration_seconds=time.time() - test_start,
            cleanup_successful=cleanup_success,
            timestamp=datetime.now().isoformat()
        )

    def run_multiple_tests(self, test_cases: List[Tuple[str, str]], timeout: int = 30) -> List[TestResult]:
        """
        Run multiple test cases

        Args:
            test_cases: List of (payload, filename) tuples
            timeout: Execution timeout per test

        Returns:
            List of TestResult objects
        """
        results = []
        for payload, filename in test_cases:
            result = self.run_test(payload, filename, timeout)
            results.append(result)

        return results


def generate_summary(results: List[TestResult]) -> Dict[str, Any]:
    """Generate test summary statistics"""
    total = len(results)
    passed = sum(1 for r in results if r.execution_status == 'SUCCESS')
    failed = sum(1 for r in results if r.execution_status == 'FAILED')
    errors = sum(1 for r in results if r.execution_status == 'ERROR')
    timeouts = sum(1 for r in results if r.execution_status == 'TIMEOUT')
    skipped = sum(1 for r in results if r.execution_status == 'SKIPPED')

    total_duration = sum(r.duration_seconds for r in results)
    avg_duration = total_duration / total if total > 0 else 0

    return {
        'total_tests': total,
        'passed': passed,
        'failed': failed,
        'errors': errors,
        'timeouts': timeouts,
        'skipped': skipped,
        'pass_rate': (passed / total * 100) if total > 0 else 0,
        'total_duration_seconds': total_duration,
        'average_duration_seconds': avg_duration,
        'all_cleanup_successful': all(r.cleanup_successful for r in results),
        'timestamp': datetime.now().isoformat()
    }


# Example usage and tests
if __name__ == '__main__':
    print("=" * 70)
    print("Test File Writer - Demonstration")
    print("=" * 70)

    writer = TestFileWriter(verbose=True)

    # Create test cases
    test_cases = [
        # Python test
        (
            "#!/usr/bin/env python3\nprint('Python test passed')\nexit(0)",
            "test_python_1.py"
        ),
        # Bash test
        (
            "#!/bin/bash\necho 'Bash test passed'\nexit 0",
            "test_bash_1.sh"
        ),
        # Failing Python test
        (
            "#!/usr/bin/env python3\nprint('Test failed')\nexit(1)",
            "test_python_fail.py"
        ),
        # Node.js test (if available)
        (
            "console.log('Node.js test passed');\nprocess.exit(0);",
            "test_node_1.js"
        ),
    ]

    print("\nRunning test suite...")
    print("-" * 70)

    results = writer.run_multiple_tests(test_cases, timeout=10)

    # Print results
    print("\n" + "=" * 70)
    print("Test Results")
    print("=" * 70)

    for result in results:
        print(f"\nTest: {result.test_name}")
        print(f"  Payload Written: {result.payload_written}")
        print(f"  File Verified: {result.file_verified}")
        print(f"  Execution Status: {result.execution_status}")
        print(f"  Exit Code: {result.exit_code}")
        print(f"  Duration: {result.duration_seconds:.3f}s")
        print(f"  Cleanup Successful: {result.cleanup_successful}")

        if result.execution_output:
            print(f"  Output: {result.execution_output[:100]}")
        if result.execution_error:
            print(f"  Error: {result.execution_error[:100]}")

    # Print summary
    summary = generate_summary(results)

    print("\n" + "=" * 70)
    print("Summary Statistics")
    print("=" * 70)
    print(json.dumps(summary, indent=2))

    # Exit with appropriate code
    sys.exit(0 if summary['failed'] == 0 and summary['errors'] == 0 else 1)
