#!/usr/bin/env python3
"""
Test Suite for WMI Executor
Validates all WMI execution methods and payload generation
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from wmi_executor import (
    WMIExecutor, create_wmi_executor, generate_wmi_payload,
    ExecutionConfig
)


class TestWMIExecutorBasics(unittest.TestCase):
    """Test basic WMI executor functionality"""

    def setUp(self):
        """Initialize executor for each test"""
        self.executor = create_wmi_executor()
        self.test_command = "powershell -NoProfile -Command Write-Host Test"

    def test_executor_creation(self):
        """Test executor can be created"""
        self.assertIsNotNone(self.executor)
        self.assertIsInstance(self.executor, WMIExecutor)

    def test_config_creation(self):
        """Test ExecutionConfig can be created with defaults"""
        config = ExecutionConfig()
        self.assertTrue(config.use_locator)
        self.assertTrue(config.obfuscate_names)
        self.assertTrue(config.use_polymorphism)

    def test_custom_config(self):
        """Test executor with custom configuration"""
        config = ExecutionConfig(obfuscate_names=False, use_locator=True)
        executor = WMIExecutor(config)
        self.assertFalse(executor.config.obfuscate_names)
        self.assertTrue(executor.config.use_locator)


class TestWMILocatorMethod(unittest.TestCase):
    """Test SWbemLocator direct method"""

    def setUp(self):
        self.executor = create_wmi_executor()
        self.test_command = "calc.exe"

    def test_locator_method_generation(self):
        """Test locator method payload generation"""
        payload = self.executor.generate_locator_method(self.test_command)
        self.assertIsNotNone(payload)
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("ConnectServer", payload)
        self.assertIn("Create", payload)
        self.assertIn(self.test_command, payload)

    def test_locator_method_vbs_syntax(self):
        """Test generated VBS has valid syntax"""
        payload = self.executor.generate_locator_method(self.test_command)
        # Check for required VBS constructs
        self.assertIn("Dim ", payload)
        self.assertIn("Set ", payload)
        self.assertIn("CreateObject", payload)

    def test_locator_method_has_cleanup(self):
        """Test proper variable cleanup"""
        payload = self.executor.generate_locator_method(self.test_command)
        # Should have Set = Nothing for cleanup
        self.assertIn("Nothing", payload)

    def test_locator_method_with_special_chars(self):
        """Test command with special characters"""
        special_cmd = 'cmd.exe /c "echo test"'
        payload = self.executor.generate_locator_method(special_cmd)
        self.assertIsNotNone(payload)
        self.assertIn("cmd.exe", payload)


class TestWMISWbemMethods(unittest.TestCase):
    """Test various SWbem method implementations"""

    def setUp(self):
        self.executor = create_wmi_executor()
        self.test_command = "powershell.exe"

    def test_swbem_query_method(self):
        """Test SWbem query interface"""
        payload = self.executor.generate_swbem_query(self.test_command)
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("localhost", payload)
        self.assertIn("root\\cimv2", payload)

    def test_swbem_object_method(self):
        """Test SWbemObject method invocation"""
        payload = self.executor.generate_swbem_object_method(self.test_command)
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("Methods_", payload)
        self.assertIn("InParameters", payload)

    def test_swbem_timeout_method(self):
        """Test WMI execution with timeout"""
        payload = self.executor.generate_swbem_timeout_method(self.test_command, timeout_seconds=60)
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("ShowWindow", payload)
        self.assertIn("WScript.Sleep", payload)
        self.assertIn("60000", payload)  # 60 seconds in milliseconds

    def test_swbem_event_sink(self):
        """Test WMI event sink execution"""
        payload = self.executor.generate_wmi_event_sink(self.test_command)
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("SpawnInstance_", payload)
        self.assertIn("On Error Resume Next", payload)


class TestWMIObfuscation(unittest.TestCase):
    """Test obfuscation features"""

    def setUp(self):
        self.executor = create_wmi_executor()

    def test_variable_name_randomization(self):
        """Test variable names are randomized"""
        payload1 = self.executor.generate_locator_method("cmd.exe")
        # Reset cache and executor for second generation
        executor2 = create_wmi_executor()
        payload2 = executor2.generate_locator_method("cmd.exe")

        # Payloads should be different due to randomization
        # Extract variable names and check they're different
        self.assertNotEqual(payload1, payload2)

    def test_base64_obfuscation(self):
        """Test Base64 payload obfuscation"""
        command = "calc.exe"
        payload = self.executor.generate_obfuscated_wmi_payload(command, "base64")
        self.assertIn("DecodeBase64Cmd", payload)
        self.assertNotIn("calc.exe", payload)  # Command should be encoded
        self.assertIn("WbemScripting.SWbemLocator", payload)

    def test_hex_obfuscation(self):
        """Test Hex payload obfuscation"""
        command = "cmd.exe"
        payload = self.executor.generate_obfuscated_wmi_payload(command, "hex")
        self.assertIn("DecodeHexCmd", payload)
        self.assertNotIn("cmd.exe", payload)  # Command should be encoded
        self.assertIn("WbemScripting.SWbemLocator", payload)


class TestWMIAdvancedFeatures(unittest.TestCase):
    """Test advanced WMI features"""

    def setUp(self):
        self.executor = create_wmi_executor()

    def test_registry_hybrid_execution(self):
        """Test WMI registry hybrid method"""
        payload = self.executor.generate_wmi_registry_hybrid("cmd.exe")
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("Win32_OSRecoveryConfiguration", payload)
        self.assertIn("DecodeBase64", payload)

    def test_remote_wmi_execution(self):
        """Test remote WMI execution"""
        payload = self.executor.generate_remote_wmi_execution(
            "cmd.exe",
            remote_host="192.168.1.100",
            username="admin",
            password="password"
        )
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("192.168.1.100", payload)
        self.assertIn("admin", payload)

    def test_launcher_script_generation(self):
        """Test complete launcher script"""
        payload = self.executor.generate_wmi_launcher_script("cmd.exe", add_wrapper=True)
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("WScript.Arguments.Count", payload)
        self.assertIn("WScript.ScriptFullName", payload)

    def test_launcher_without_wrapper(self):
        """Test launcher script without wrapper"""
        payload = self.executor.generate_wmi_launcher_script("cmd.exe", add_wrapper=False)
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertNotIn("WScript.Arguments.Count", payload)


class TestPolymorphicExecution(unittest.TestCase):
    """Test polymorphic execution variants"""

    def setUp(self):
        self.executor = create_wmi_executor()

    def test_polymorphic_variant_0(self):
        """Test polymorphic variant 0"""
        payload = self.executor.generate_polymorphic_wmi_executor("cmd.exe", variant=0)
        self.assertIn("WbemScripting.SWbemLocator", payload)

    def test_polymorphic_variant_1(self):
        """Test polymorphic variant 1"""
        payload = self.executor.generate_polymorphic_wmi_executor("cmd.exe", variant=1)
        self.assertIn("WbemScripting.SWbemLocator", payload)

    def test_polymorphic_variant_2(self):
        """Test polymorphic variant 2"""
        payload = self.executor.generate_polymorphic_wmi_executor("cmd.exe", variant=2)
        self.assertIn("WbemScripting.SWbemLocator", payload)

    def test_polymorphic_variant_cycling(self):
        """Test polymorphic variants cycle through 4 options"""
        payloads = []
        for i in range(4):
            payload = self.executor.generate_polymorphic_wmi_executor("cmd.exe", variant=i)
            payloads.append(payload)
        # All should contain WMI locator
        for payload in payloads:
            self.assertIn("WbemScripting.SWbemLocator", payload)


class TestHighLevelAPI(unittest.TestCase):
    """Test high-level payload generation API"""

    def test_generate_locator_payload(self):
        """Test generate_wmi_payload with locator method"""
        payload = generate_wmi_payload("calc.exe", method="locator")
        self.assertIn("WbemScripting.SWbemLocator", payload)

    def test_generate_query_payload(self):
        """Test generate_wmi_payload with query method"""
        payload = generate_wmi_payload("cmd.exe", method="query")
        self.assertIn("WbemScripting.SWbemLocator", payload)

    def test_generate_obfuscated_payload(self):
        """Test generate_wmi_payload with obfuscation"""
        payload = generate_wmi_payload("calc.exe", method="obfuscated", encoding="base64")
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("DecodeBase64Cmd", payload)

    def test_generate_with_timeout(self):
        """Test generate_wmi_payload with timeout"""
        payload = generate_wmi_payload("cmd.exe", method="timeout", timeout=45)
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("45000", payload)


class TestExecutionReport(unittest.TestCase):
    """Test execution method report generation"""

    def setUp(self):
        self.executor = create_wmi_executor()

    def test_report_generation(self):
        """Test report of all execution methods"""
        report = self.executor.generate_execution_report()
        self.assertIsNotNone(report)
        self.assertGreater(len(report), 0)

    def test_report_structure(self):
        """Test report has correct structure"""
        report = self.executor.generate_execution_report()
        for key, method in report.items():
            self.assertIn("name", method)
            self.assertIn("description", method)
            self.assertIn("stealth_level", method)
            self.assertIn("code", method)

    def test_report_contains_all_methods(self):
        """Test report includes all execution methods"""
        report = self.executor.generate_execution_report()
        expected_methods = [
            "locator_method",
            "swbem_query",
            "object_method",
            "timeout_method",
            "event_sink",
            "registry_hybrid",
            "obfuscated_payload"
        ]
        for method_key in expected_methods:
            self.assertIn(method_key, report)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and resilience"""

    def setUp(self):
        self.executor = create_wmi_executor()

    def test_error_handling_in_payload(self):
        """Test error handling is included"""
        payload = self.executor.generate_swbem_object_method("cmd.exe")
        self.assertIn("On Error Resume Next", payload)
        self.assertIn("On Error GoTo 0", payload)

    def test_event_sink_error_handling(self):
        """Test event sink includes error handling"""
        payload = self.executor.generate_wmi_event_sink("cmd.exe")
        self.assertIn("On Error Resume Next", payload)

    def test_empty_command_handling(self):
        """Test handling of empty command"""
        payload = self.executor.generate_locator_method("")
        self.assertIsNotNone(payload)
        self.assertIn("WbemScripting.SWbemLocator", payload)

    def test_long_command_handling(self):
        """Test handling of very long command"""
        long_cmd = "cmd.exe " + (" /c echo test" * 100)
        payload = self.executor.generate_locator_method(long_cmd)
        self.assertIsNotNone(payload)
        self.assertIn("WbemScripting.SWbemLocator", payload)


class TestCommandEncoding(unittest.TestCase):
    """Test command encoding and decoding"""

    def setUp(self):
        self.executor = create_wmi_executor()

    def test_base64_decoder_included(self):
        """Test Base64 decoder function is included"""
        payload = self.executor.generate_obfuscated_wmi_payload("cmd.exe", "base64")
        self.assertIn("Function DecodeBase64Cmd", payload)

    def test_hex_decoder_included(self):
        """Test Hex decoder function is included"""
        payload = self.executor.generate_obfuscated_wmi_payload("cmd.exe", "hex")
        self.assertIn("Function DecodeHexCmd", payload)

    def test_decoder_function_calls(self):
        """Test decoder functions are called"""
        payload = self.executor.generate_obfuscated_wmi_payload("calc.exe", "base64")
        self.assertIn("DecodeBase64Cmd", payload)


def run_tests(verbosity=2):
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWMIExecutorBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestWMILocatorMethod))
    suite.addTests(loader.loadTestsFromTestCase(TestWMISWbemMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestWMIObfuscation))
    suite.addTests(loader.loadTestsFromTestCase(TestWMIAdvancedFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestPolymorphicExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestHighLevelAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestExecutionReport))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandEncoding))

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests(verbosity=2)
    sys.exit(0 if result.wasSuccessful() else 1)
