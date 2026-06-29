#!/usr/bin/env python3
"""
Test Suite for Log Tampering & Event Log Cleaning Module

Tests:
1. Configuration validation
2. Code generation
3. Script formatting
4. Method coverage
5. Output validation
6. Error handling
"""

import unittest
import json
from log_tampering_cleaner import (
    LogTamperingCleaner,
    LogTamperingConfig,
    EventLogType,
    LogTamperingMethod,
    generate_log_cleaning_payload,
    generate_comprehensive_log_tampering,
)


class TestLogTamperingConfig(unittest.TestCase):
    """Test configuration validation"""

    def test_valid_config(self):
        """Test valid configuration"""
        config = LogTamperingConfig(
            log_types=[EventLogType.SECURITY],
            methods=[LogTamperingMethod.CLEAR_EVENT_LOG],
        )
        self.assertIsNotNone(config)

    def test_empty_log_types_fails(self):
        """Test that empty log types raises error"""
        with self.assertRaises(ValueError):
            config = LogTamperingConfig(
                log_types=[],
                methods=[LogTamperingMethod.CLEAR_EVENT_LOG],
            )
            LogTamperingCleaner(config)

    def test_empty_methods_fails(self):
        """Test that empty methods raises error"""
        with self.assertRaises(ValueError):
            config = LogTamperingConfig(
                log_types=[EventLogType.SECURITY],
                methods=[],
            )
            LogTamperingCleaner(config)

    def test_default_config(self):
        """Test default configuration"""
        config = LogTamperingConfig()
        cleaner = LogTamperingCleaner(config)
        self.assertIsNotNone(cleaner)


class TestEventLogClearing(unittest.TestCase):
    """Test event log clearing functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = LogTamperingConfig(
            log_types=[EventLogType.SECURITY, EventLogType.SYSTEM],
            methods=[LogTamperingMethod.CLEAR_EVENT_LOG],
        )
        self.cleaner = LogTamperingCleaner(self.config)

    def test_clear_event_log_vbs(self):
        """Test VBS code generation for event log clearing"""
        vbs_code = self.cleaner.generate_clear_event_log_vbs()
        self.assertIsNotNone(vbs_code)
        self.assertIn("ClearEventLog", vbs_code)
        self.assertIn("Security", vbs_code)
        self.assertIn("System", vbs_code)

    def test_clear_event_log_batch(self):
        """Test batch code generation for event log clearing"""
        batch_code = self.cleaner.generate_clear_event_log_batch()
        self.assertIsNotNone(batch_code)
        self.assertIn("wevtutil", batch_code)
        self.assertIn("Security", batch_code)

    def test_clear_event_log_powershell(self):
        """Test PowerShell code generation for event log clearing"""
        ps_code = self.cleaner.generate_clear_event_log_powershell()
        self.assertIsNotNone(ps_code)
        # Should have some PowerShell-like content
        self.assertTrue(len(ps_code) > 0)

    def test_vbs_syntax_validation(self):
        """Test that VBS code has valid structure"""
        vbs_code = self.cleaner.generate_clear_event_log_vbs()
        # Check for required VBS elements
        self.assertIn("On Error Resume Next", vbs_code)
        self.assertIn("Dim", vbs_code)

    def test_batch_syntax_validation(self):
        """Test that batch code has valid structure"""
        batch_code = self.cleaner.generate_clear_event_log_batch()
        self.assertIn("@echo", batch_code.lower())


class TestAuditPolicyDisabling(unittest.TestCase):
    """Test audit policy disabling functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = LogTamperingConfig(
            log_types=[EventLogType.SECURITY],
            methods=[LogTamperingMethod.DISABLE_AUDIT_POLICY],
        )
        self.cleaner = LogTamperingCleaner(self.config)

    def test_disable_audit_policy_powershell(self):
        """Test PowerShell code for audit policy disabling"""
        ps_code = self.cleaner.generate_disable_audit_policy_powershell()
        self.assertIsNotNone(ps_code)
        self.assertIn("auditpol", ps_code)
        self.assertIn("disable", ps_code.lower())

    def test_disable_audit_policy_batch(self):
        """Test batch code for audit policy disabling"""
        batch_code = self.cleaner.generate_disable_audit_policy_batch()
        self.assertIsNotNone(batch_code)
        self.assertIn("auditpol", batch_code)
        self.assertIn("disable", batch_code.lower())

    def test_audit_categories_included(self):
        """Test that all audit categories are included"""
        batch_code = self.cleaner.generate_disable_audit_policy_batch()
        categories = [
            "Account Logon",
            "Account Management",
            "Logon/Logoff",
        ]
        for category in categories:
            self.assertIn(category, batch_code)


class TestRegistryDisabling(unittest.TestCase):
    """Test registry-based logging disabling"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = LogTamperingConfig(
            log_types=[EventLogType.POWERSHELL],
            methods=[LogTamperingMethod.REGISTRY_DISABLE],
        )
        self.cleaner = LogTamperingCleaner(self.config)

    def test_registry_disable_vbs(self):
        """Test VBS code for registry disabling"""
        vbs_code = self.cleaner.generate_registry_log_disable_vbs()
        self.assertIsNotNone(vbs_code)
        self.assertIn("SetDWordValue", vbs_code)
        self.assertIn("PowerShell", vbs_code)

    def test_registry_paths_included(self):
        """Test that required registry paths are included"""
        vbs_code = self.cleaner.generate_registry_log_disable_vbs()
        registry_paths = [
            "Transcription",
            "ModuleLogging",
            "ScriptBlockLogging",
        ]
        for path in registry_paths:
            self.assertIn(path, vbs_code)


class TestServiceDisabling(unittest.TestCase):
    """Test service disabling functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = LogTamperingConfig(
            log_types=[EventLogType.SECURITY],
            methods=[LogTamperingMethod.SERVICE_DISABLE],
        )
        self.cleaner = LogTamperingCleaner(self.config)

    def test_service_disable_batch(self):
        """Test batch code for service disabling"""
        batch_code = self.cleaner.generate_disable_event_log_service_batch()
        self.assertIsNotNone(batch_code)
        self.assertIn("EventLog", batch_code)
        self.assertIn("net stop", batch_code.lower())


class TestAdvancedMethods(unittest.TestCase):
    """Test advanced tampering methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = LogTamperingConfig(
            log_types=[EventLogType.SECURITY],
            methods=[
                LogTamperingMethod.SWAP_EVENT_IDS,
                LogTamperingMethod.TIMESTAMP_MODIFICATION,
                LogTamperingMethod.DIRECT_LOG_FILE_WIPE,
            ],
        )
        self.cleaner = LogTamperingCleaner(self.config)

    def test_event_id_swapping(self):
        """Test event ID swapping code generation"""
        code = self.cleaner.generate_event_id_swapping_code()
        self.assertIsNotNone(code)
        self.assertIn("EventID", code)

    def test_timestamp_manipulation(self):
        """Test timestamp manipulation code generation"""
        code = self.cleaner.generate_timestamp_manipulation_code()
        self.assertIsNotNone(code)
        self.assertTrue(len(code) > 0)

    def test_direct_file_wipe(self):
        """Test direct file wipe code generation"""
        code = self.cleaner.generate_direct_file_wipe_code()
        self.assertIsNotNone(code)
        self.assertIn(".evtx", code)

    def test_log_rotation_prevention(self):
        """Test log rotation prevention code"""
        code = self.cleaner.generate_log_rotation_prevention_code()
        self.assertIsNotNone(code)
        self.assertIn("MaxSize", code)


class TestCombinedScripts(unittest.TestCase):
    """Test combined/master scripts"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = LogTamperingConfig(
            log_types=[
                EventLogType.SECURITY,
                EventLogType.SYSTEM,
                EventLogType.APPLICATION,
            ],
            methods=[LogTamperingMethod.ALL_METHODS],
        )
        self.cleaner = LogTamperingCleaner(self.config)

    def test_combined_powershell(self):
        """Test combined PowerShell script"""
        ps_script = self.cleaner.generate_combined_log_cleaning_powershell()
        self.assertIsNotNone(ps_script)
        self.assertIn("param", ps_script)
        self.assertIn("function", ps_script)

    def test_combined_batch(self):
        """Test combined batch script"""
        batch_script = self.cleaner.generate_combined_log_cleaning_batch()
        self.assertIsNotNone(batch_script)
        self.assertIn("@echo", batch_script.lower())

    def test_combined_vbs(self):
        """Test combined VBS script"""
        vbs_script = self.cleaner.generate_combined_log_cleaning_vbs()
        self.assertIsNotNone(vbs_script)
        self.assertIn("On Error Resume Next", vbs_script)

    def test_master_installer(self):
        """Test master installer script"""
        master_script = self.cleaner.generate_master_installer_script()
        self.assertIsNotNone(master_script)
        self.assertIn("Stage", master_script)


class TestCodeGeneration(unittest.TestCase):
    """Test code generation methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = LogTamperingConfig(
            log_types=[EventLogType.SECURITY, EventLogType.POWERSHELL],
            methods=[LogTamperingMethod.ALL_METHODS],
        )
        self.cleaner = LogTamperingCleaner(self.config)

    def test_generate_all_methods(self):
        """Test generating all methods"""
        all_methods = self.cleaner.generate_all_log_tampering_methods()
        self.assertIsNotNone(all_methods)
        self.assertGreater(len(all_methods), 0)
        self.assertIsInstance(all_methods, dict)

    def test_generated_code_stored(self):
        """Test that generated code is stored"""
        self.cleaner.generate_all_log_tampering_methods()
        self.assertGreater(len(self.cleaner.generated_code), 0)

    def test_code_quality(self):
        """Test generated code quality"""
        self.cleaner.generate_all_log_tampering_methods()
        for name, code in self.cleaner.generated_code.items():
            self.assertIsNotNone(code)
            self.assertGreater(len(code), 0)
            self.assertIsInstance(code, str)


class TestReporting(unittest.TestCase):
    """Test reporting functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = LogTamperingConfig(
            log_types=[EventLogType.SECURITY],
            methods=[LogTamperingMethod.CLEAR_EVENT_LOG],
        )
        self.cleaner = LogTamperingCleaner(self.config)

    def test_deployment_summary(self):
        """Test deployment summary generation"""
        summary = self.cleaner.generate_deployment_summary()
        self.assertIsNotNone(summary)
        self.assertIn("title", summary)
        self.assertIn("configuration", summary)
        self.assertIn("capabilities", summary)

    def test_statistics(self):
        """Test statistics generation"""
        self.cleaner.generate_all_log_tampering_methods()
        stats = self.cleaner.get_statistics()
        self.assertIsNotNone(stats)
        self.assertIn("total_methods_generated", stats)
        self.assertGreater(stats["total_methods_generated"], 0)

    def test_summary_json_serializable(self):
        """Test that summary is JSON serializable"""
        summary = self.cleaner.generate_deployment_summary()
        try:
            json_str = json.dumps(summary)
            self.assertIsNotNone(json_str)
        except TypeError:
            self.fail("Summary is not JSON serializable")


class TestObfuscation(unittest.TestCase):
    """Test command obfuscation"""

    def setUp(self):
        """Set up test fixtures"""
        self.config_obfuscated = LogTamperingConfig(
            log_types=[EventLogType.SECURITY],
            methods=[LogTamperingMethod.CLEAR_EVENT_LOG],
            obfuscate_commands=True,
        )
        self.config_plain = LogTamperingConfig(
            log_types=[EventLogType.SECURITY],
            methods=[LogTamperingMethod.CLEAR_EVENT_LOG],
            obfuscate_commands=False,
        )

    def test_obfuscation_enabled(self):
        """Test code obfuscation when enabled"""
        cleaner = LogTamperingCleaner(self.config_obfuscated)
        original_cmd = "wevtutil cl Security"
        obfuscated = cleaner._obfuscate_command(original_cmd)
        self.assertNotEqual(original_cmd, obfuscated)

    def test_obfuscation_disabled(self):
        """Test that obfuscation is skipped when disabled"""
        cleaner = LogTamperingCleaner(self.config_plain)
        original_cmd = "wevtutil cl Security"
        result = cleaner._obfuscate_command(original_cmd)
        self.assertEqual(original_cmd, result)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    def test_generate_log_cleaning_payload(self):
        """Test quick log cleaning payload generation"""
        payload = generate_log_cleaning_payload()
        self.assertIsNotNone(payload)
        self.assertGreater(len(payload), 0)

    def test_generate_comprehensive_log_tampering(self):
        """Test comprehensive log tampering generation"""
        suite = generate_comprehensive_log_tampering()
        self.assertIsNotNone(suite)
        self.assertIsInstance(suite, dict)
        self.assertGreater(len(suite), 0)


class TestMultipleLogTypes(unittest.TestCase):
    """Test handling multiple log types"""

    def test_security_log(self):
        """Test security log handling"""
        config = LogTamperingConfig(
            log_types=[EventLogType.SECURITY],
            methods=[LogTamperingMethod.CLEAR_EVENT_LOG],
        )
        cleaner = LogTamperingCleaner(config)
        code = cleaner.generate_clear_event_log_vbs()
        self.assertIn("Security", code)

    def test_powershell_log(self):
        """Test PowerShell log handling"""
        config = LogTamperingConfig(
            log_types=[EventLogType.POWERSHELL],
            methods=[LogTamperingMethod.CLEAR_EVENT_LOG],
        )
        cleaner = LogTamperingCleaner(config)
        code = cleaner.generate_clear_event_log_vbs()
        self.assertIn("Windows PowerShell", code)

    def test_multiple_logs(self):
        """Test handling multiple log types"""
        config = LogTamperingConfig(
            log_types=[
                EventLogType.SECURITY,
                EventLogType.SYSTEM,
                EventLogType.APPLICATION,
                EventLogType.POWERSHELL,
                EventLogType.SYSMON,
            ],
            methods=[LogTamperingMethod.CLEAR_EVENT_LOG],
        )
        cleaner = LogTamperingCleaner(config)
        code = cleaner.generate_clear_event_log_vbs()
        self.assertIn("Security", code)
        self.assertIn("System", code)
        self.assertIn("Application", code)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLogTamperingConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestEventLogClearing))
    suite.addTests(loader.loadTestsFromTestCase(TestAuditPolicyDisabling))
    suite.addTests(loader.loadTestsFromTestCase(TestRegistryDisabling))
    suite.addTests(loader.loadTestsFromTestCase(TestServiceDisabling))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestCombinedScripts))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestReporting))
    suite.addTests(loader.loadTestsFromTestCase(TestObfuscation))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestMultipleLogTypes))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    run_tests()
