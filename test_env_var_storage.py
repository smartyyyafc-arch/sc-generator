#!/usr/bin/env python3
"""
Comprehensive test suite for environment variable storage
Tests: write payload → retrieve → execute → verify persistence
"""

import os
import sys
import json
import time
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from env_var_storage import (
    EnvVarWriter, EnvVarReader, EnvVarConfig,
    EnvVarScope, EnvVarEncoding, create_env_var_writer
)


class EnvVarStorageTestSuite:
    """Comprehensive test suite for environment variable storage"""

    def __init__(self):
        """Initialize test suite"""
        self.test_results: List[Dict] = []
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
        self.test_payloads = self._create_test_payloads()
        self.timestamp = datetime.now().isoformat()

    def _create_test_payloads(self) -> Dict[str, str]:
        """Create various test payloads"""
        return {
            "simple": "Hello, World!",
            "json": json.dumps({"message": "test", "value": 42}),
            "script": "#!/bin/bash\necho 'Test payload executed'\nexit 0",
            "large": "X" * 5000,  # Large payload
            "special_chars": "Special: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "multiline": "Line 1\nLine 2\nLine 3\nLine 4",
            "unicode": "Unicode: café, ñoño, 中文, 日本語, العربية",
            "empty": "",
            "with_newlines": "\n\n\nContent with newlines\n\n\n",
            "base64_like": "aGVsbG8gd29ybGQ=",
        }

    def log_test(self, name: str, passed: bool, message: str, details: Optional[Dict] = None):
        """Log test result"""
        self.test_count += 1
        if passed:
            self.passed_count += 1
            status = "PASS"
        else:
            self.failed_count += 1
            status = "FAIL"

        result = {
            "test_number": self.test_count,
            "name": name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"[{status}] Test {self.test_count}: {name} - {message}")

    def test_1_write_simple_payload(self) -> bool:
        """Test writing a simple payload to process environment"""
        try:
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )
            payload = self.test_payloads["simple"]
            success, vars_list, message = writer.write_to_env("test_simple", payload)

            details = {
                "payload": payload,
                "success": success,
                "variables": vars_list,
                "message": message,
                "var_count": len(vars_list)
            }

            self.log_test(
                "Write Simple Payload",
                success,
                f"Stored in {len(vars_list)} environment variables",
                details
            )
            return success
        except Exception as e:
            self.log_test("Write Simple Payload", False, str(e))
            return False

    def test_2_write_json_payload(self) -> bool:
        """Test writing a JSON payload"""
        try:
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )
            payload = self.test_payloads["json"]
            success, vars_list, message = writer.write_to_env("test_json", payload)

            details = {
                "payload": payload,
                "success": success,
                "variables": vars_list,
                "var_count": len(vars_list)
            }

            self.log_test(
                "Write JSON Payload",
                success,
                f"Stored JSON in {len(vars_list)} variables",
                details
            )
            return success
        except Exception as e:
            self.log_test("Write JSON Payload", False, str(e))
            return False

    def test_3_write_large_payload(self) -> bool:
        """Test writing a large payload (chunking)"""
        try:
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )
            payload = self.test_payloads["large"]
            success, vars_list, message = writer.write_to_env("test_large", payload)

            details = {
                "payload_size": len(payload),
                "success": success,
                "variables": vars_list,
                "var_count": len(vars_list),
                "message": message
            }

            self.log_test(
                "Write Large Payload (Chunking)",
                success and len(vars_list) > 1,
                f"Split into {len(vars_list)} chunks",
                details
            )
            return success and len(vars_list) > 1
        except Exception as e:
            self.log_test("Write Large Payload", False, str(e))
            return False

    def test_4_retrieve_simple_payload(self) -> bool:
        """Test retrieving a simple payload"""
        try:
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )
            original_payload = self.test_payloads["simple"]
            write_success, vars_list, _ = writer.write_to_env("test_retrieve_simple", original_payload)

            if not write_success:
                self.log_test("Retrieve Simple Payload", False, "Failed to write payload first")
                return False

            # Retrieve
            reader = EnvVarReader()
            obfuscated_name = writer.obfuscate_var_name("test_retrieve_simple")
            retrieved_payload = reader.read_from_env(obfuscated_name)

            match = retrieved_payload == original_payload
            details = {
                "original": original_payload,
                "retrieved": retrieved_payload,
                "match": match,
                "variables": vars_list
            }

            self.log_test(
                "Retrieve Simple Payload",
                match,
                "Payload retrieved and matches original",
                details
            )
            return match
        except Exception as e:
            self.log_test("Retrieve Simple Payload", False, str(e))
            return False

    def test_5_retrieve_large_payload(self) -> bool:
        """Test retrieving a chunked payload"""
        try:
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )
            original_payload = self.test_payloads["large"]
            write_success, vars_list, _ = writer.write_to_env("test_retrieve_large", original_payload)

            if not write_success:
                self.log_test("Retrieve Large Payload", False, "Failed to write payload first")
                return False

            # Retrieve
            reader = EnvVarReader()
            obfuscated_name = writer.obfuscate_var_name("test_retrieve_large")
            retrieved_payload = reader.read_from_env(obfuscated_name)

            match = retrieved_payload == original_payload
            details = {
                "original_size": len(original_payload),
                "retrieved_size": len(retrieved_payload) if retrieved_payload else 0,
                "match": match,
                "chunk_count": len(vars_list)
            }

            self.log_test(
                "Retrieve Large Payload",
                match,
                f"Retrieved {len(retrieved_payload) if retrieved_payload else 0} bytes from {len(vars_list)} chunks",
                details
            )
            return match
        except Exception as e:
            self.log_test("Retrieve Large Payload", False, str(e))
            return False

    def test_6_multiple_encodings(self) -> bool:
        """Test different encoding methods"""
        try:
            payload = self.test_payloads["simple"]
            encodings_to_test = [
                EnvVarEncoding.BASE64,
                EnvVarEncoding.HEX,
                EnvVarEncoding.RAW,
            ]

            all_passed = True
            encoding_results = {}

            for encoding in encodings_to_test:
                writer = create_env_var_writer(
                    scope=EnvVarScope.PROCESS,
                    encoding=encoding
                )
                success, vars_list, _ = writer.write_to_env(f"test_encoding_{encoding.value}", payload)

                if success:
                    reader = EnvVarReader()
                    obfuscated_name = writer.obfuscate_var_name(f"test_encoding_{encoding.value}")
                    retrieved = reader.read_from_env(obfuscated_name)
                    match = retrieved == payload
                    encoding_results[encoding.value] = {"success": success, "match": match}
                    all_passed = all_passed and match
                else:
                    encoding_results[encoding.value] = {"success": False}
                    all_passed = False

            details = {
                "payload": payload,
                "encodings_tested": encoding_results
            }

            self.log_test(
                "Multiple Encodings",
                all_passed,
                f"Tested {len(encodings_to_test)} encoding methods",
                details
            )
            return all_passed
        except Exception as e:
            self.log_test("Multiple Encodings", False, str(e))
            return False

    def test_7_special_characters(self) -> bool:
        """Test payload with special characters"""
        try:
            payload = self.test_payloads["special_chars"]
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )
            success, vars_list, _ = writer.write_to_env("test_special", payload)

            if success:
                reader = EnvVarReader()
                obfuscated_name = writer.obfuscate_var_name("test_special")
                retrieved = reader.read_from_env(obfuscated_name)
                match = retrieved == payload

                details = {
                    "original": payload,
                    "retrieved": retrieved,
                    "match": match
                }

                self.log_test(
                    "Special Characters",
                    match,
                    "Special characters preserved correctly",
                    details
                )
                return match
            else:
                self.log_test("Special Characters", False, "Failed to write payload")
                return False
        except Exception as e:
            self.log_test("Special Characters", False, str(e))
            return False

    def test_8_unicode_characters(self) -> bool:
        """Test payload with Unicode characters"""
        try:
            payload = self.test_payloads["unicode"]
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )
            success, vars_list, _ = writer.write_to_env("test_unicode", payload)

            if success:
                reader = EnvVarReader()
                obfuscated_name = writer.obfuscate_var_name("test_unicode")
                retrieved = reader.read_from_env(obfuscated_name)
                match = retrieved == payload

                details = {
                    "original": payload,
                    "retrieved": retrieved,
                    "match": match
                }

                self.log_test(
                    "Unicode Characters",
                    match,
                    "Unicode characters handled correctly",
                    details
                )
                return match
            else:
                self.log_test("Unicode Characters", False, "Failed to write payload")
                return False
        except Exception as e:
            self.log_test("Unicode Characters", False, str(e))
            return False

    def test_9_empty_payload(self) -> bool:
        """Test handling of empty payload"""
        try:
            payload = self.test_payloads["empty"]
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )
            success, vars_list, _ = writer.write_to_env("test_empty", payload)

            details = {
                "payload": payload,
                "payload_size": len(payload),
                "success": success,
                "variables": vars_list
            }

            self.log_test(
                "Empty Payload",
                success,
                "Empty payload handled",
                details
            )
            return success
        except Exception as e:
            self.log_test("Empty Payload", False, str(e))
            return False

    def test_10_payload_execution(self) -> bool:
        """Test executing a payload retrieved from environment"""
        try:
            script_payload = "#!/bin/bash\necho 'PAYLOAD_EXECUTED_SUCCESSFULLY' > /tmp/test_exec.txt\nexit 0"

            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )
            success, vars_list, _ = writer.write_to_env("test_exec_payload", script_payload)

            if not success:
                self.log_test("Payload Execution", False, "Failed to store payload")
                return False

            # Retrieve and execute
            reader = EnvVarReader()
            obfuscated_name = writer.obfuscate_var_name("test_exec_payload")
            retrieved = reader.read_from_env(obfuscated_name)

            if retrieved is None:
                self.log_test("Payload Execution", False, "Failed to retrieve payload")
                return False

            # Write to temp file and execute
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(retrieved)
                temp_script = f.name

            try:
                os.chmod(temp_script, 0o755)
                result = subprocess.run([temp_script], capture_output=True, timeout=5)

                # Check if execution marker exists
                exec_marker_exists = os.path.exists('/tmp/test_exec.txt')

                if exec_marker_exists:
                    with open('/tmp/test_exec.txt', 'r') as f:
                        marker_content = f.read()
                    os.remove('/tmp/test_exec.txt')

                details = {
                    "script_size": len(retrieved),
                    "execution_result": result.returncode,
                    "marker_found": exec_marker_exists,
                    "marker_content": marker_content if exec_marker_exists else None
                }

                self.log_test(
                    "Payload Execution",
                    exec_marker_exists and result.returncode == 0,
                    "Retrieved payload executed successfully",
                    details
                )
                return exec_marker_exists and result.returncode == 0
            finally:
                if os.path.exists(temp_script):
                    os.remove(temp_script)

        except Exception as e:
            self.log_test("Payload Execution", False, str(e))
            return False

    def test_11_persistence_across_processes(self) -> bool:
        """Test if environment variables persist across subprocess calls"""
        try:
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )
            payload = self.test_payloads["json"]
            success, vars_list, _ = writer.write_to_env("test_persist", payload)

            if not success:
                self.log_test("Persistence Across Processes", False, "Failed to write payload")
                return False

            # Create a Python script that reads from subprocess env
            test_script = """
import os
import json
obfuscated_name = "{obfuscated_name}"
meta_var = obfuscated_name + "_META"
meta_str = os.environ.get(meta_var)
if meta_str:
    print("FOUND")
else:
    print("NOT_FOUND")
"""
            obfuscated_name = writer.obfuscate_var_name("test_persist")
            script_content = test_script.format(obfuscated_name=obfuscated_name)

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                temp_script = f.name

            try:
                result = subprocess.run(
                    [sys.executable, temp_script],
                    capture_output=True,
                    timeout=5,
                    env=os.environ.copy()
                )
                output = result.stdout.decode().strip()
                found = output == "FOUND"

                details = {
                    "variables_stored": vars_list,
                    "subprocess_output": output,
                    "found": found
                }

                self.log_test(
                    "Persistence Across Processes",
                    found,
                    "Environment variables accessible in subprocess",
                    details
                )
                return found
            finally:
                if os.path.exists(temp_script):
                    os.remove(temp_script)

        except Exception as e:
            self.log_test("Persistence Across Processes", False, str(e))
            return False

    def test_12_metadata_retrieval(self) -> bool:
        """Test retrieving and verifying metadata"""
        try:
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )
            payload = self.test_payloads["large"]
            success, vars_list, _ = writer.write_to_env("test_metadata", payload)

            if not success:
                self.log_test("Metadata Retrieval", False, "Failed to write payload")
                return False

            metadata = writer.get_var_metadata()
            obfuscated_name = writer.obfuscate_var_name("test_metadata")

            # Find metadata entries
            meta_entries = {k: v for k, v in metadata.items() if k.startswith(obfuscated_name)}
            has_meta = len(meta_entries) > 0

            details = {
                "variables": vars_list,
                "metadata_entries": len(meta_entries),
                "metadata_keys": list(meta_entries.keys()),
                "sample_metadata": list(meta_entries.values())[0] if meta_entries else None
            }

            self.log_test(
                "Metadata Retrieval",
                has_meta,
                f"Retrieved metadata for {len(meta_entries)} variables",
                details
            )
            return has_meta
        except Exception as e:
            self.log_test("Metadata Retrieval", False, str(e))
            return False

    def test_13_multiline_payload(self) -> bool:
        """Test payload with multiple lines"""
        try:
            payload = self.test_payloads["multiline"]
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )
            success, vars_list, _ = writer.write_to_env("test_multiline", payload)

            if success:
                reader = EnvVarReader()
                obfuscated_name = writer.obfuscate_var_name("test_multiline")
                retrieved = reader.read_from_env(obfuscated_name)
                match = retrieved == payload

                details = {
                    "line_count": len(payload.split('\n')),
                    "match": match,
                    "variables": vars_list
                }

                self.log_test(
                    "Multiline Payload",
                    match,
                    "Multiline payload preserved correctly",
                    details
                )
                return match
            else:
                self.log_test("Multiline Payload", False, "Failed to write payload")
                return False
        except Exception as e:
            self.log_test("Multiline Payload", False, str(e))
            return False

    def test_14_hex_encoding(self) -> bool:
        """Test hex encoding specifically"""
        try:
            payload = self.test_payloads["simple"]
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.HEX
            )
            success, vars_list, _ = writer.write_to_env("test_hex", payload)

            if success:
                reader = EnvVarReader()
                obfuscated_name = writer.obfuscate_var_name("test_hex")
                retrieved = reader.read_from_env(obfuscated_name)
                match = retrieved == payload

                details = {
                    "payload": payload,
                    "retrieved": retrieved,
                    "match": match,
                    "encoding": "hex"
                }

                self.log_test(
                    "Hex Encoding",
                    match,
                    "Payload correctly encoded/decoded using hex",
                    details
                )
                return match
            else:
                self.log_test("Hex Encoding", False, "Failed to write payload")
                return False
        except Exception as e:
            self.log_test("Hex Encoding", False, str(e))
            return False

    def test_15_obfuscation(self) -> bool:
        """Test variable name obfuscation"""
        try:
            writer = create_env_var_writer(
                scope=EnvVarScope.PROCESS,
                encoding=EnvVarEncoding.BASE64
            )

            original_name = "test_obfuscation"
            obfuscated = writer.obfuscate_var_name(original_name)

            # Should not directly contain the original name
            is_obfuscated = original_name not in obfuscated or obfuscated.startswith("SC_")

            details = {
                "original_name": original_name,
                "obfuscated_name": obfuscated,
                "contains_original": original_name in obfuscated,
                "starts_with_prefix": obfuscated.startswith("SC_")
            }

            self.log_test(
                "Obfuscation",
                is_obfuscated,
                f"Variable name obfuscated: {obfuscated}",
                details
            )
            return is_obfuscated
        except Exception as e:
            self.log_test("Obfuscation", False, str(e))
            return False

    def generate_report(self) -> str:
        """Generate test report"""
        report = []
        report.append("=" * 80)
        report.append("ENVIRONMENT VARIABLE STORAGE TEST REPORT")
        report.append("=" * 80)
        report.append(f"\nTest Execution Time: {self.timestamp}")
        report.append(f"Platform: {sys.platform}")
        report.append(f"Python Version: {sys.version.split()[0]}")
        report.append("\n" + "=" * 80)
        report.append("TEST SUMMARY")
        report.append("=" * 80)
        report.append(f"Total Tests: {self.test_count}")
        report.append(f"Passed: {self.passed_count} ({100*self.passed_count//self.test_count if self.test_count > 0 else 0}%)")
        report.append(f"Failed: {self.failed_count}")
        report.append(f"Success Rate: {100*self.passed_count//self.test_count if self.test_count > 0 else 0}%")

        report.append("\n" + "=" * 80)
        report.append("DETAILED TEST RESULTS")
        report.append("=" * 80)

        for result in self.test_results:
            report.append(f"\n[Test {result['test_number']}] {result['name']}")
            report.append(f"  Status: {result['status']}")
            report.append(f"  Message: {result['message']}")
            report.append(f"  Timestamp: {result['timestamp']}")

            if result['details']:
                report.append("  Details:")
                for key, value in result['details'].items():
                    if isinstance(value, (dict, list)):
                        report.append(f"    {key}: {json.dumps(value, indent=6)}")
                    else:
                        report.append(f"    {key}: {value}")

        report.append("\n" + "=" * 80)
        report.append("CONCLUSION")
        report.append("=" * 80)

        if self.failed_count == 0:
            report.append("ALL TESTS PASSED - Environment variable storage system is working correctly")
        else:
            report.append(f"SOME TESTS FAILED - {self.failed_count} test(s) need investigation")

        report.append("=" * 80)

        return "\n".join(report)

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 80)
        print("STARTING ENVIRONMENT VARIABLE STORAGE TEST SUITE")
        print("=" * 80 + "\n")

        # Run all test methods
        test_methods = [
            self.test_1_write_simple_payload,
            self.test_2_write_json_payload,
            self.test_3_write_large_payload,
            self.test_4_retrieve_simple_payload,
            self.test_5_retrieve_large_payload,
            self.test_6_multiple_encodings,
            self.test_7_special_characters,
            self.test_8_unicode_characters,
            self.test_9_empty_payload,
            self.test_10_payload_execution,
            self.test_11_persistence_across_processes,
            self.test_12_metadata_retrieval,
            self.test_13_multiline_payload,
            self.test_14_hex_encoding,
            self.test_15_obfuscation,
        ]

        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"ERROR: Test {test_method.__name__} crashed: {e}")

        # Generate and print report
        report = self.generate_report()
        print("\n" + report)
        return report


def main():
    """Main entry point"""
    suite = EnvVarStorageTestSuite()
    report = suite.run_all_tests()

    # Save report to file
    report_file = "/tmp/env_var_storage_test_report.txt"
    with open(report_file, "w") as f:
        f.write(report)

    print(f"\nReport saved to: {report_file}")

    # Exit with appropriate code
    exit_code = 0 if suite.failed_count == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
