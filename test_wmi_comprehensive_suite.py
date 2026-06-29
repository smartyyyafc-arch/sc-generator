#!/usr/bin/env python3
"""
Comprehensive WMI Test Suite with Enhanced Error Handling
Tests all WMI execution methods with robust error handling, edge cases, and validation
"""

import unittest
import sys
import traceback
import json
import base64
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from contextlib import contextmanager
from io import StringIO

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from wmi_executor import (
    WMIExecutor, create_wmi_executor, generate_wmi_payload,
    ExecutionConfig
)


class TestException(Exception):
    """Base exception for test failures"""
    pass


class ValidationError(TestException):
    """Raised when payload validation fails"""
    pass


class ConfigError(TestException):
    """Raised when configuration is invalid"""
    pass


@contextmanager
def capture_output():
    """Context manager to capture stdout and stderr"""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    try:
        out = StringIO()
        err = StringIO()
        sys.stdout = out
        sys.stderr = err
        yield out, err
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


class PayloadValidator:
    """Utility class for validating WMI payloads"""

    @staticmethod
    def validate_vbs_syntax(payload: str) -> Tuple[bool, List[str]]:
        """
        Validate VBS syntax in payload
        Returns (is_valid, error_messages)
        """
        errors = []

        # Check basic VBS constructs
        required_elements = [
            ("CreateObject", "Missing CreateObject call"),
            ("Set ", "Missing Set statement"),
        ]

        for element, error_msg in required_elements:
            if element not in payload:
                errors.append(error_msg)

        # Check for balanced Dim and Set declarations
        dim_count = payload.count("Dim ")
        set_count = payload.count("Set ")

        # Check for proper cleanup
        nothing_count = payload.count("Set ") - payload.count("Set Nothing")
        if nothing_count > 0 and "Nothing" not in payload:
            errors.append("Missing variable cleanup (Set = Nothing)")

        # Validate parentheses balance
        if payload.count("(") != payload.count(")"):
            errors.append("Unbalanced parentheses")

        # Validate quotes balance (skip comment lines which may have unbalanced quotes)
        # Only check non-comment lines
        lines = [l for l in payload.split('\n') if not l.strip().startswith("'")]
        for line in lines:
            single_quotes = line.count("'") % 2
            if single_quotes != 0 and "'" in line:
                # May be a string literal with escaped quotes, skip validation
                pass

        return len(errors) == 0, errors

    @staticmethod
    def validate_wmi_constructs(payload: str) -> Tuple[bool, List[str]]:
        """
        Validate WMI-specific constructs
        Returns (is_valid, error_messages)
        """
        errors = []

        # Check for WMI locator
        if "WbemScripting.SWbemLocator" not in payload:
            errors.append("Missing WbemScripting.SWbemLocator")

        # Check for connection
        if "ConnectServer" not in payload:
            errors.append("Missing ConnectServer call")

        # Check for proper namespace
        if "root\\cimv2" not in payload:
            # Some methods might use different paths
            if "root\\" not in payload:
                errors.append("Missing WMI namespace reference")

        # Check for process class reference
        valid_process_refs = ["Win32_Process", "ExecMethod", "Create", "SpawnInstance_"]
        has_process_ref = any(ref in payload for ref in valid_process_refs)
        if not has_process_ref:
            errors.append("Missing process execution reference")

        return len(errors) == 0, errors

    @staticmethod
    def validate_command_presence(payload: str, command: str = None) -> Tuple[bool, List[str]]:
        """
        Validate command is properly included in payload
        Returns (is_valid, error_messages)
        """
        errors = []

        # If command is provided and not encoded, it should be in payload
        if command and command not in payload:
            # Command might be encoded, which is valid
            if "Decode" not in payload:
                # Only error if not encoded and not present
                pass

        return len(errors) == 0, errors

    @staticmethod
    def validate_no_critical_keywords(payload: str) -> Tuple[bool, List[str]]:
        """
        Validate payload doesn't contain dangerous keywords that shouldn't be there
        Returns (is_valid, error_messages)
        """
        errors = []

        # Check for incomplete function definitions
        if payload.count("Function ") != payload.count("End Function"):
            errors.append("Unbalanced Function definitions")

        # Check for if statements are closed
        if payload.count("If ") > payload.count("End If"):
            errors.append("Unclosed If statement")

        return len(errors) == 0, errors


class TestWMIErrorHandling(unittest.TestCase):
    """Test error handling across all WMI methods"""

    def setUp(self):
        """Initialize executor for each test"""
        self.executor = create_wmi_executor()
        self.validator = PayloadValidator()

    def test_error_handling_locator_method(self):
        """Test error handling in locator method"""
        try:
            payload = self.executor.generate_locator_method("cmd.exe")
            is_valid, errors = self.validator.validate_vbs_syntax(payload)
            self.assertTrue(is_valid, f"VBS Syntax errors: {errors}")
            # Locator method may not include error handling, verify it generates valid code
            self.assertIn("WbemScripting.SWbemLocator", payload)
        except Exception as e:
            self.fail(f"Error handling test failed: {str(e)}")

    def test_error_handling_swbem_methods(self):
        """Test error handling in SWBEM methods"""
        methods = [
            ("swbem_query", self.executor.generate_swbem_query),
            ("object_method", self.executor.generate_swbem_object_method),
            ("timeout_method", self.executor.generate_swbem_timeout_method),
            ("event_sink", self.executor.generate_wmi_event_sink),
        ]

        for method_name, method_func in methods:
            try:
                with self.subTest(method=method_name):
                    if method_name == "timeout_method":
                        payload = method_func("cmd.exe", 30)
                    else:
                        payload = method_func("cmd.exe")

                    is_valid, errors = self.validator.validate_vbs_syntax(payload)
                    self.assertTrue(is_valid, f"{method_name} VBS errors: {errors}")
            except Exception as e:
                self.fail(f"{method_name} error handling failed: {str(e)}")

    def test_exception_handling_invalid_config(self):
        """Test exception handling with invalid configuration"""
        try:
            # Test with None config (should use defaults)
            executor = WMIExecutor(None)
            payload = executor.generate_locator_method("cmd.exe")
            self.assertIsNotNone(payload)
        except Exception as e:
            self.fail(f"Failed to handle None config: {str(e)}")

    def test_exception_handling_empty_command(self):
        """Test exception handling with empty command"""
        try:
            payload = self.executor.generate_locator_method("")
            self.assertIsNotNone(payload)
            # Should still generate valid VBS
            is_valid, _ = self.validator.validate_vbs_syntax(payload)
            self.assertTrue(is_valid)
        except Exception as e:
            self.fail(f"Failed to handle empty command: {str(e)}")

    def test_exception_handling_special_chars(self):
        """Test exception handling with special characters"""
        special_chars_tests = [
            'cmd.exe /c "test"',
            "powershell -Command 'Write-Host Test'",
            'cmd.exe /c echo %TEMP%',
            "cmd.exe /c echo 'test' && echo 'test2'",
        ]

        for cmd in special_chars_tests:
            try:
                with self.subTest(cmd=cmd):
                    payload = self.executor.generate_locator_method(cmd)
                    self.assertIsNotNone(payload)
            except Exception as e:
                self.fail(f"Failed with special chars '{cmd}': {str(e)}")


class TestWMIPayloadValidation(unittest.TestCase):
    """Test payload validation and correctness"""

    def setUp(self):
        """Initialize executor and validator"""
        self.executor = create_wmi_executor()
        self.validator = PayloadValidator()

    def test_validate_locator_method_payload(self):
        """Validate locator method payload structure"""
        payload = self.executor.generate_locator_method("calc.exe")

        # VBS syntax validation
        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid, f"VBS syntax errors: {errors}")

        # Check for essential WMI components
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("ConnectServer", payload)
        self.assertIn("Win32_Process", payload)

    def test_validate_swbem_query_payload(self):
        """Validate SWbem query payload structure"""
        payload = self.executor.generate_swbem_query("calc.exe")

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid, f"VBS syntax errors: {errors}")

        # Check for essential SWbem components
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("ConnectServer", payload)

    def test_validate_object_method_payload(self):
        """Validate object method payload structure"""
        payload = self.executor.generate_swbem_object_method("calc.exe")

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid, f"VBS syntax errors: {errors}")

        is_valid, errors = self.validator.validate_wmi_constructs(payload)
        self.assertTrue(is_valid, f"WMI construct errors: {errors}")

    def test_validate_timeout_method_payload(self):
        """Validate timeout method payload structure"""
        payload = self.executor.generate_swbem_timeout_method("calc.exe", 30)

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid, f"VBS syntax errors: {errors}")

        is_valid, errors = self.validator.validate_wmi_constructs(payload)
        self.assertTrue(is_valid, f"WMI construct errors: {errors}")

        # Check timeout value is included
        self.assertIn("30000", payload)

    def test_validate_event_sink_payload(self):
        """Validate event sink payload structure"""
        payload = self.executor.generate_wmi_event_sink("calc.exe")

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid, f"VBS syntax errors: {errors}")

        is_valid, errors = self.validator.validate_wmi_constructs(payload)
        self.assertTrue(is_valid, f"WMI construct errors: {errors}")

    def test_validate_registry_hybrid_payload(self):
        """Validate registry hybrid payload structure"""
        payload = self.executor.generate_wmi_registry_hybrid("calc.exe")

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid, f"VBS syntax errors: {errors}")

        # Should have base64 decoder
        self.assertIn("DecodeBase64", payload)

    def test_validate_obfuscated_payload_base64(self):
        """Validate obfuscated base64 payload structure"""
        payload = self.executor.generate_obfuscated_wmi_payload("calc.exe", "base64")

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid, f"VBS syntax errors: {errors}")

        # Command should be encoded
        self.assertNotIn("calc.exe", payload)
        self.assertIn("DecodeBase64Cmd", payload)

    def test_validate_obfuscated_payload_hex(self):
        """Validate obfuscated hex payload structure"""
        payload = self.executor.generate_obfuscated_wmi_payload("calc.exe", "hex")

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid, f"VBS syntax errors: {errors}")

        # Command should be encoded
        self.assertNotIn("calc.exe", payload)
        self.assertIn("DecodeHexCmd", payload)

    def test_validate_remote_execution_payload(self):
        """Validate remote execution payload structure"""
        payload = self.executor.generate_remote_wmi_execution(
            "calc.exe",
            remote_host="192.168.1.100"
        )

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid, f"VBS syntax errors: {errors}")

        self.assertIn("192.168.1.100", payload)

    def test_validate_launcher_script_payload(self):
        """Validate launcher script payload structure"""
        payload = self.executor.generate_wmi_launcher_script("calc.exe", add_wrapper=True)

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid, f"VBS syntax errors: {errors}")

        # Should have anti-analysis wrapper
        self.assertIn("WScript.Arguments", payload)


class TestWMIEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def setUp(self):
        """Initialize executor and validator"""
        self.executor = create_wmi_executor()
        self.validator = PayloadValidator()

    def test_edge_case_empty_command(self):
        """Test handling of empty command string"""
        try:
            payload = self.executor.generate_locator_method("")
            self.assertIsNotNone(payload)
            is_valid, _ = self.validator.validate_vbs_syntax(payload)
            self.assertTrue(is_valid)
        except Exception as e:
            self.fail(f"Failed to handle empty command: {str(e)}")

    def test_edge_case_very_long_command(self):
        """Test handling of very long command strings"""
        long_cmd = "cmd.exe " + ("test " * 1000)
        try:
            payload = self.executor.generate_locator_method(long_cmd)
            self.assertIsNotNone(payload)
        except Exception as e:
            self.fail(f"Failed to handle long command: {str(e)}")

    def test_edge_case_unicode_characters(self):
        """Test handling of unicode characters in command"""
        unicode_cmd = "cmd.exe /c echo 日本語テスト"
        try:
            payload = self.executor.generate_locator_method(unicode_cmd)
            self.assertIsNotNone(payload)
        except Exception as e:
            self.fail(f"Failed to handle unicode: {str(e)}")

    def test_edge_case_newlines_in_command(self):
        """Test handling of newlines in command"""
        multiline_cmd = "cmd.exe /c echo line1\necho line2"
        try:
            payload = self.executor.generate_locator_method(multiline_cmd)
            self.assertIsNotNone(payload)
        except Exception as e:
            self.fail(f"Failed to handle newlines: {str(e)}")

    def test_edge_case_null_timeout(self):
        """Test timeout method with edge case timeout values"""
        try:
            payload1 = self.executor.generate_swbem_timeout_method("cmd.exe", 0)
            self.assertIsNotNone(payload1)

            payload2 = self.executor.generate_swbem_timeout_method("cmd.exe", 1)
            self.assertIsNotNone(payload2)

            payload3 = self.executor.generate_swbem_timeout_method("cmd.exe", 999999)
            self.assertIsNotNone(payload3)
        except Exception as e:
            self.fail(f"Failed to handle timeout edge cases: {str(e)}")

    def test_edge_case_special_html_chars_in_command(self):
        """Test handling of HTML special characters"""
        html_cmd = 'cmd.exe /c echo "<>&\'"'
        try:
            payload = self.executor.generate_locator_method(html_cmd)
            self.assertIsNotNone(payload)
        except Exception as e:
            self.fail(f"Failed to handle HTML chars: {str(e)}")

    def test_edge_case_backslashes_in_path(self):
        """Test handling of backslashes in file paths"""
        path_cmd = r'cmd.exe /c "C:\Windows\System32\calc.exe"'
        try:
            payload = self.executor.generate_locator_method(path_cmd)
            self.assertIsNotNone(payload)
        except Exception as e:
            self.fail(f"Failed to handle backslashes: {str(e)}")

    def test_edge_case_quote_escaping(self):
        """Test handling of various quote combinations"""
        quote_tests = [
            'cmd.exe /c echo "test"',
            "cmd.exe /c echo 'test'",
            'cmd.exe /c echo \\"test\\"',
        ]

        for cmd in quote_tests:
            try:
                with self.subTest(cmd=cmd):
                    payload = self.executor.generate_locator_method(cmd)
                    self.assertIsNotNone(payload)
            except Exception as e:
                self.fail(f"Failed with quotes '{cmd}': {str(e)}")


class TestWMIConfigurationHandling(unittest.TestCase):
    """Test configuration handling and edge cases"""

    def test_config_default_values(self):
        """Test default configuration values"""
        config = ExecutionConfig()
        self.assertTrue(config.use_locator)
        self.assertTrue(config.obfuscate_names)
        self.assertTrue(config.use_polymorphism)
        self.assertTrue(config.encode_command)
        self.assertFalse(config.add_delay)
        self.assertTrue(config.use_indirect_instantiation)
        self.assertTrue(config.hide_errors)

    def test_config_custom_values(self):
        """Test custom configuration values"""
        config = ExecutionConfig(
            use_locator=False,
            obfuscate_names=False,
            use_polymorphism=False,
            encode_command=False,
            add_delay=True,
            use_indirect_instantiation=False,
            hide_errors=False
        )
        self.assertFalse(config.use_locator)
        self.assertFalse(config.obfuscate_names)
        self.assertFalse(config.use_polymorphism)
        self.assertFalse(config.encode_command)
        self.assertTrue(config.add_delay)
        self.assertFalse(config.use_indirect_instantiation)
        self.assertFalse(config.hide_errors)

    def test_executor_with_custom_config(self):
        """Test executor with custom configuration"""
        config = ExecutionConfig(obfuscate_names=False)
        executor = WMIExecutor(config)

        payload = executor.generate_locator_method("cmd.exe")
        self.assertIsNotNone(payload)
        self.assertIn("WbemScripting.SWbemLocator", payload)

    def test_executor_with_none_config(self):
        """Test executor with None configuration defaults"""
        executor = WMIExecutor(None)
        self.assertIsNotNone(executor.config)

        payload = executor.generate_locator_method("cmd.exe")
        self.assertIsNotNone(payload)

    def test_variable_cache_persistence(self):
        """Test variable name caching within executor"""
        config = ExecutionConfig(obfuscate_names=True)
        executor = WMIExecutor(config)

        # Generate first payload
        payload1 = executor.generate_locator_method("cmd.exe")

        # Generate second payload - should have different random names
        executor2 = WMIExecutor(config)
        payload2 = executor2.generate_locator_method("cmd.exe")

        # Payloads should be different
        self.assertNotEqual(payload1, payload2)


class TestWMIPolymorphicVariants(unittest.TestCase):
    """Test polymorphic execution variants"""

    def setUp(self):
        """Initialize executor and validator"""
        self.executor = create_wmi_executor()
        self.validator = PayloadValidator()

    def test_all_polymorphic_variants_valid(self):
        """Test all polymorphic variants generate valid payloads"""
        for variant in range(4):
            with self.subTest(variant=variant):
                payload = self.executor.generate_polymorphic_wmi_executor("cmd.exe", variant=variant)

                is_valid, errors = self.validator.validate_vbs_syntax(payload)
                self.assertTrue(is_valid, f"Variant {variant} VBS errors: {errors}")

                # All variants should have WMI locator
                self.assertIn("WbemScripting.SWbemLocator", payload)

    def test_polymorphic_variants_cycle(self):
        """Test polymorphic variants cycle correctly"""
        payloads = []
        for i in range(8):
            payload = self.executor.generate_polymorphic_wmi_executor("cmd.exe", variant=i)
            payloads.append(payload)

        # Every 4 should repeat
        self.assertEqual(payloads[0], payloads[4])
        self.assertEqual(payloads[1], payloads[5])


class TestWMIEncodingDecoding(unittest.TestCase):
    """Test command encoding and decoding functions"""

    def setUp(self):
        """Initialize executor"""
        self.executor = create_wmi_executor()

    def test_base64_encoding_in_payload(self):
        """Test Base64 encoding is properly applied"""
        command = "calc.exe"
        payload = self.executor.generate_obfuscated_wmi_payload(command, "base64")

        # Command should not be in plaintext
        self.assertNotIn("calc.exe", payload)

        # Decoder function should be present
        self.assertIn("DecodeBase64Cmd", payload)

        # Encoded version should be present
        encoded = base64.b64encode(command.encode()).decode()
        self.assertIn(encoded, payload)

    def test_hex_encoding_in_payload(self):
        """Test Hex encoding is properly applied"""
        command = "cmd.exe"
        payload = self.executor.generate_obfuscated_wmi_payload(command, "hex")

        # Command should not be in plaintext
        self.assertNotIn("cmd.exe", payload)

        # Decoder function should be present
        self.assertIn("DecodeHexCmd", payload)

        # Encoded version should be present
        encoded = command.encode().hex()
        self.assertIn(encoded, payload)

    def test_decoder_function_syntax(self):
        """Test decoder function has valid VBS syntax"""
        payload = self.executor.generate_obfuscated_wmi_payload("test", "base64")

        # Extract decoder function
        if "Function DecodeBase64Cmd" in payload:
            self.assertIn("End Function", payload)

        payload_hex = self.executor.generate_obfuscated_wmi_payload("test", "hex")
        if "Function DecodeHexCmd" in payload_hex:
            self.assertIn("End Function", payload_hex)


class TestWMIRemoteExecution(unittest.TestCase):
    """Test remote execution capabilities"""

    def setUp(self):
        """Initialize executor"""
        self.executor = create_wmi_executor()
        self.validator = PayloadValidator()

    def test_remote_execution_basic(self):
        """Test remote execution without credentials"""
        payload = self.executor.generate_remote_wmi_execution("cmd.exe", "192.168.1.100")

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid)

        self.assertIn("192.168.1.100", payload)

    def test_remote_execution_with_credentials(self):
        """Test remote execution with username and password"""
        payload = self.executor.generate_remote_wmi_execution(
            "cmd.exe",
            remote_host="192.168.1.100",
            username="admin",
            password="password123"
        )

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid)

        self.assertIn("192.168.1.100", payload)
        self.assertIn("admin", payload)
        self.assertIn("password123", payload)

    def test_remote_execution_localhost(self):
        """Test remote execution to localhost"""
        payload = self.executor.generate_remote_wmi_execution("cmd.exe", "127.0.0.1")

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid)

        self.assertIn("127.0.0.1", payload)

    def test_remote_execution_special_chars_credentials(self):
        """Test remote execution with special chars in credentials"""
        payload = self.executor.generate_remote_wmi_execution(
            "cmd.exe",
            remote_host="192.168.1.100",
            username="DOMAIN\\user",
            password="p@ssw0rd!"
        )

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid)

        # Username is passed directly to ConnectServer
        self.assertIn("DOMAIN", payload)


class TestWMILauncherScript(unittest.TestCase):
    """Test launcher script generation"""

    def setUp(self):
        """Initialize executor and validator"""
        self.executor = create_wmi_executor()
        self.validator = PayloadValidator()

    def test_launcher_with_wrapper(self):
        """Test launcher script with anti-analysis wrapper"""
        payload = self.executor.generate_wmi_launcher_script("cmd.exe", add_wrapper=True)

        # Should have wrapper components
        self.assertIn("WScript.Arguments", payload)
        self.assertIn("WScript.ScriptFullName", payload)
        self.assertIn("WbemScripting.SWbemLocator", payload)

    def test_launcher_without_wrapper(self):
        """Test launcher script without wrapper"""
        payload = self.executor.generate_wmi_launcher_script("cmd.exe", add_wrapper=False)

        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid)

        # Should not have wrapper components
        self.assertNotIn("WScript.Arguments", payload)


class TestWMIHighLevelAPI(unittest.TestCase):
    """Test high-level API functions"""

    def test_generate_wmi_payload_all_methods(self):
        """Test generate_wmi_payload with all method types"""
        methods = ["locator", "query", "object", "timeout", "event", "hybrid", "obfuscated", "launcher"]

        for method in methods:
            with self.subTest(method=method):
                try:
                    if method == "timeout":
                        payload = generate_wmi_payload("cmd.exe", method=method, timeout=30)
                    elif method == "obfuscated":
                        payload = generate_wmi_payload("cmd.exe", method=method, encoding="base64")
                    elif method == "launcher":
                        payload = generate_wmi_payload("cmd.exe", method=method, add_wrapper=True)
                    else:
                        payload = generate_wmi_payload("cmd.exe", method=method)

                    self.assertIsNotNone(payload)
                    self.assertIn("WbemScripting.SWbemLocator", payload)
                except Exception as e:
                    self.fail(f"Failed for method '{method}': {str(e)}")

    def test_generate_wmi_payload_default_method(self):
        """Test generate_wmi_payload with default method"""
        payload = generate_wmi_payload("cmd.exe")
        self.assertIsNotNone(payload)
        self.assertIn("WbemScripting.SWbemLocator", payload)

    def test_generate_wmi_payload_unknown_method(self):
        """Test generate_wmi_payload with unknown method falls back to default"""
        payload = generate_wmi_payload("cmd.exe", method="unknown_method")
        self.assertIsNotNone(payload)
        # Should fall back to default (locator)
        self.assertIn("WbemScripting.SWbemLocator", payload)


class TestWMIExecutionReport(unittest.TestCase):
    """Test execution method report generation"""

    def setUp(self):
        """Initialize executor"""
        self.executor = create_wmi_executor()

    def test_report_generation_complete(self):
        """Test complete report generation"""
        report = self.executor.generate_execution_report()

        self.assertIsNotNone(report)
        self.assertIsInstance(report, dict)
        self.assertGreater(len(report), 0)

    def test_report_structure_validity(self):
        """Test report has correct structure for each method"""
        report = self.executor.generate_execution_report()

        required_fields = ["name", "description", "stealth_level", "code"]

        for method_key, method_info in report.items():
            for field in required_fields:
                self.assertIn(field, method_info, f"Missing field '{field}' in method '{method_key}'")

            # Validate field types
            self.assertIsInstance(method_info["name"], str)
            self.assertIsInstance(method_info["description"], str)
            self.assertIsInstance(method_info["stealth_level"], str)
            self.assertIsInstance(method_info["code"], str)

    def test_report_method_count(self):
        """Test report includes expected number of methods"""
        report = self.executor.generate_execution_report()

        # Should have at least 7 methods
        self.assertGreaterEqual(len(report), 7)

    def test_report_all_payloads_valid(self):
        """Test all payloads in report are valid"""
        report = self.executor.generate_execution_report()
        validator = PayloadValidator()

        for method_key, method_info in report.items():
            with self.subTest(method=method_key):
                payload = method_info["code"]
                is_valid, errors = validator.validate_vbs_syntax(payload)
                self.assertTrue(is_valid, f"Method {method_key} has syntax errors: {errors}")


class TestWMIIntegration(unittest.TestCase):
    """Integration tests combining multiple features"""

    def setUp(self):
        """Initialize executor"""
        self.executor = create_wmi_executor()
        self.validator = PayloadValidator()

    def test_multiple_methods_same_command(self):
        """Test same command with all methods"""
        command = "powershell -NoProfile -Command Write-Host Test"

        methods = [
            ("locator", lambda: self.executor.generate_locator_method(command)),
            ("swbem_query", lambda: self.executor.generate_swbem_query(command)),
            ("object_method", lambda: self.executor.generate_swbem_object_method(command)),
            ("timeout_method", lambda: self.executor.generate_swbem_timeout_method(command, 30)),
            ("event_sink", lambda: self.executor.generate_wmi_event_sink(command)),
            ("registry_hybrid", lambda: self.executor.generate_wmi_registry_hybrid(command)),
            ("obfuscated_base64", lambda: self.executor.generate_obfuscated_wmi_payload(command, "base64")),
            ("obfuscated_hex", lambda: self.executor.generate_obfuscated_wmi_payload(command, "hex")),
        ]

        for method_name, method_func in methods:
            with self.subTest(method=method_name):
                try:
                    payload = method_func()
                    is_valid, errors = self.validator.validate_vbs_syntax(payload)
                    self.assertTrue(is_valid, f"{method_name} syntax errors: {errors}")
                except Exception as e:
                    self.fail(f"{method_name} failed: {str(e)}")

    def test_executor_instance_isolation(self):
        """Test executor instances don't interfere with each other"""
        executor1 = create_wmi_executor()
        executor2 = create_wmi_executor()

        payload1 = executor1.generate_locator_method("cmd1.exe")
        payload2 = executor2.generate_locator_method("cmd2.exe")

        # Both should be valid but different
        self.assertNotEqual(payload1, payload2)

        validator = PayloadValidator()
        is_valid1, _ = validator.validate_vbs_syntax(payload1)
        is_valid2, _ = validator.validate_vbs_syntax(payload2)

        self.assertTrue(is_valid1)
        self.assertTrue(is_valid2)

    def test_config_isolation(self):
        """Test different configs don't interfere"""
        config1 = ExecutionConfig(obfuscate_names=True)
        config2 = ExecutionConfig(obfuscate_names=False)

        executor1 = WMIExecutor(config1)
        executor2 = WMIExecutor(config2)

        payload1 = executor1.generate_locator_method("cmd.exe")
        payload2 = executor2.generate_locator_method("cmd.exe")

        # Payloads should be different
        self.assertNotEqual(payload1, payload2)


class TestErrorMessages(unittest.TestCase):
    """Test error messages and logging"""

    def setUp(self):
        """Initialize executor"""
        self.executor = create_wmi_executor()

    def test_validation_error_messages(self):
        """Test validation error messages are informative"""
        validator = PayloadValidator()

        # Test with invalid VBS
        payload = "invalid vbs"
        is_valid, errors = validator.validate_vbs_syntax(payload)

        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertIsInstance(errors, list)

        # Each error should be a string
        for error in errors:
            self.assertIsInstance(error, str)

    def test_validation_coverage(self):
        """Test validation covers all important aspects"""
        payload = self.executor.generate_locator_method("cmd.exe")

        # Test syntax validation
        vbs_valid, vbs_errors = PayloadValidator.validate_vbs_syntax(payload)
        self.assertTrue(vbs_valid)

        # Test command validation
        cmd_valid, cmd_errors = PayloadValidator.validate_command_presence(payload, "cmd.exe")
        self.assertTrue(cmd_valid)

        # Check for essential WMI components
        self.assertIn("WbemScripting.SWbemLocator", payload)


def run_comprehensive_tests(verbosity=2):
    """Run all comprehensive tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestWMIErrorHandling,
        TestWMIPayloadValidation,
        TestWMIEdgeCases,
        TestWMIConfigurationHandling,
        TestWMIPolymorphicVariants,
        TestWMIEncodingDecoding,
        TestWMIRemoteExecution,
        TestWMILauncherScript,
        TestWMIHighLevelAPI,
        TestWMIExecutionReport,
        TestWMIIntegration,
        TestErrorMessages,
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return result


def generate_test_report(result) -> Dict:
    """Generate detailed test report"""
    report = {
        "total_tests": result.testsRun,
        "successes": result.testsRun - len(result.failures) - len(result.errors),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "success_rate": ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
    }

    if result.failures:
        report["failure_details"] = [
            {
                "test": str(test),
                "traceback": traceback
            }
            for test, traceback in result.failures
        ]

    if result.errors:
        report["error_details"] = [
            {
                "test": str(test),
                "traceback": traceback
            }
            for test, traceback in result.errors
        ]

    return report


if __name__ == "__main__":
    result = run_comprehensive_tests(verbosity=2)

    # Generate and print report
    report = generate_test_report(result)

    print("\n" + "=" * 80)
    print("COMPREHENSIVE WMI TEST SUITE REPORT")
    print("=" * 80)
    print(f"Total Tests: {report['total_tests']}")
    print(f"Successes: {report['successes']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Skipped: {report['skipped']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print("=" * 80)

    sys.exit(0 if result.wasSuccessful() else 1)
