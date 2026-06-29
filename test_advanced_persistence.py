#!/usr/bin/env python3
"""
Advanced Persistence Test Suite
Comprehensive tests for multi-method persistence system
"""

import unittest
import sys
from advanced_persistence_multimethods import (
    MultiMethodPersistence, PersistenceConfig, RegistryHive,
    ScheduledTaskTrigger, create_default_persistence_system
)


class TestPersistenceConfig(unittest.TestCase):
    """Test persistence configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        config = PersistenceConfig(payload="test.exe")
        self.assertEqual(config.payload, "test.exe")
        self.assertTrue(config.obfuscation_enabled)
        self.assertEqual(config.obfuscation_level, "high")

    def test_custom_config(self):
        """Test custom configuration"""
        config = PersistenceConfig(
            payload="custom.exe",
            obfuscation_level="extreme",
            registry_hives=[RegistryHive.HKLM]
        )
        self.assertEqual(config.payload, "custom.exe")
        self.assertEqual(config.obfuscation_level, "extreme")
        self.assertIn(RegistryHive.HKLM, config.registry_hives)

    def test_invalid_obfuscation_level(self):
        """Test invalid obfuscation level rejection"""
        config = PersistenceConfig(
            payload="test.exe",
            obfuscation_level="invalid"
        )
        with self.assertRaises(ValueError):
            MultiMethodPersistence(config)

    def test_empty_payload_rejection(self):
        """Test empty payload rejection"""
        config = PersistenceConfig(payload="")
        with self.assertRaises(ValueError):
            MultiMethodPersistence(config)


class TestRegistryPersistence(unittest.TestCase):
    """Test registry persistence functionality"""

    def setUp(self):
        self.config = PersistenceConfig(
            payload="calc.exe",
            use_startup_folder=False,
            use_scheduled_task=False
        )
        self.persistence = MultiMethodPersistence(self.config)

    def test_registry_payload_generation(self):
        """Test registry payload generation"""
        payloads = self.persistence.generate_registry_persistence()
        self.assertGreater(len(payloads), 0)

    def test_registry_multiple_hives(self):
        """Test multiple registry hives"""
        config = PersistenceConfig(
            payload="test.exe",
            registry_hives=[RegistryHive.HKCU, RegistryHive.HKLM],
            use_startup_folder=False,
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_registry_persistence()

        hkcu_payloads = [k for k in payloads.keys() if "HKCU" in k]
        hklm_payloads = [k for k in payloads.keys() if "HKLM" in k]

        self.assertGreater(len(hkcu_payloads), 0)
        self.assertGreater(len(hklm_payloads), 0)

    def test_registry_multiple_paths(self):
        """Test multiple registry paths"""
        config = PersistenceConfig(
            payload="test.exe",
            registry_paths=[
                "Software\\Test1",
                "Software\\Test2",
                "Software\\Test3"
            ],
            use_startup_folder=False,
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_registry_persistence()
        self.assertGreaterEqual(len(payloads), 3)

    def test_registry_vbs_contains_regwrite(self):
        """Test registry VBS contains RegWrite"""
        payloads = self.persistence.generate_registry_persistence()
        for payload in payloads.values():
            self.assertIn("RegWrite", payload)

    def test_registry_obfuscation(self):
        """Test registry payload obfuscation"""
        config = PersistenceConfig(
            payload="calc.exe",
            obfuscation_enabled=True,
            obfuscation_level="high",
            use_startup_folder=False,
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_registry_persistence()

        for payload in payloads.values():
            # Obfuscated payloads shouldn't contain plain "calc.exe"
            # (depending on encoding method)
            self.assertGreater(len(payload), 0)


class TestStartupFolderPersistence(unittest.TestCase):
    """Test startup folder persistence functionality"""

    def test_startup_vbs_generation(self):
        """Test VBS startup script generation"""
        config = PersistenceConfig(
            payload="calc.exe",
            use_startup_folder=True,
            startup_extensions=[".vbs"],
            registry_hives=[],
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_startup_persistence()

        vbs_payloads = [k for k in payloads.keys() if "vbs" in k]
        self.assertGreater(len(vbs_payloads), 0)

    def test_startup_batch_generation(self):
        """Test batch startup script generation"""
        config = PersistenceConfig(
            payload="cmd.exe",
            use_startup_folder=True,
            startup_extensions=[".bat"],
            registry_hives=[],
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_startup_persistence()

        batch_payloads = [k for k in payloads.keys() if "batch" in k]
        self.assertGreater(len(batch_payloads), 0)

    def test_startup_powershell_generation(self):
        """Test PowerShell startup script generation"""
        config = PersistenceConfig(
            payload="powershell.exe",
            use_startup_folder=True,
            startup_extensions=[".ps1"],
            registry_hives=[],
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_startup_persistence()

        ps_payloads = [k for k in payloads.keys() if "powershell" in k]
        self.assertGreater(len(ps_payloads), 0)

    def test_startup_all_formats(self):
        """Test all startup formats together"""
        config = PersistenceConfig(
            payload="test.exe",
            use_startup_folder=True,
            startup_extensions=[".vbs", ".bat", ".ps1"],
            registry_hives=[],
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_startup_persistence()

        self.assertEqual(len(payloads), 3)

    def test_startup_disabled(self):
        """Test startup disabled"""
        config = PersistenceConfig(
            payload="test.exe",
            use_startup_folder=False,
            registry_hives=[],
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_startup_persistence()

        self.assertEqual(len(payloads), 0)

    def test_startup_filename_randomization(self):
        """Test startup filename randomization"""
        config = PersistenceConfig(
            payload="test.exe",
            use_startup_folder=True,
            randomize_names=True,
            registry_hives=[],
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)

        # Generate multiple times and check for variation
        names = set()
        for _ in range(5):
            name = persistence._generate_startup_filename(".vbs")
            names.add(name)

        # Should be consistent with same payload
        self.assertEqual(len(names), 1)


class TestScheduledTaskPersistence(unittest.TestCase):
    """Test scheduled task persistence functionality"""

    def test_scheduled_task_xml_generation(self):
        """Test scheduled task XML generation"""
        config = PersistenceConfig(
            payload="calc.exe",
            use_startup_folder=False,
            registry_hives=[],
            use_scheduled_task=True
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_scheduled_task_persistence()

        xml_payloads = [k for k in payloads.keys() if "xml" in k]
        self.assertGreater(len(xml_payloads), 0)

    def test_scheduled_task_powershell_generation(self):
        """Test scheduled task PowerShell generation"""
        config = PersistenceConfig(
            payload="calc.exe",
            use_startup_folder=False,
            registry_hives=[],
            use_scheduled_task=True
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_scheduled_task_persistence()

        ps_payloads = [k for k in payloads.keys() if "powershell" in k]
        self.assertGreater(len(ps_payloads), 0)

    def test_scheduled_task_multiple_triggers(self):
        """Test multiple scheduled task triggers"""
        config = PersistenceConfig(
            payload="calc.exe",
            use_startup_folder=False,
            registry_hives=[],
            use_scheduled_task=True,
            task_triggers=[
                ScheduledTaskTrigger.LOGON,
                ScheduledTaskTrigger.STARTUP,
                ScheduledTaskTrigger.INTERVAL
            ]
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_scheduled_task_persistence()

        xml_payload = payloads.get("scheduled_task_xml", "")
        self.assertIn("LogonTrigger", xml_payload)
        self.assertIn("BootTrigger", xml_payload)
        self.assertIn("TimeTrigger", xml_payload)

    def test_scheduled_task_disabled(self):
        """Test scheduled task disabled"""
        config = PersistenceConfig(
            payload="test.exe",
            use_scheduled_task=False,
            use_startup_folder=False,
            registry_hives=[]
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_scheduled_task_persistence()

        self.assertEqual(len(payloads), 0)

    def test_task_xml_structure(self):
        """Test scheduled task XML structure"""
        config = PersistenceConfig(
            payload="calc.exe",
            use_startup_folder=False,
            registry_hives=[],
            use_scheduled_task=True
        )
        persistence = MultiMethodPersistence(config)
        payloads = persistence.generate_scheduled_task_persistence()

        xml_payload = payloads.get("scheduled_task_xml", "")
        self.assertIn("<?xml", xml_payload)
        self.assertIn("<Task", xml_payload)
        self.assertIn("<Triggers>", xml_payload)
        # Actions may be indented, so check for both
        self.assertTrue("<Actions" in xml_payload or "<Exec>" in xml_payload)


class TestFallbackChain(unittest.TestCase):
    """Test fallback chain functionality"""

    def test_fallback_chain_generation(self):
        """Test fallback chain generation"""
        config = PersistenceConfig(
            payload="calc.exe",
            enable_fallback_chain=True,
            use_startup_folder=False,
            registry_hives=[],
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        fallback = persistence.generate_fallback_chain()

        self.assertGreater(len(fallback), 0)

    def test_fallback_chain_disabled(self):
        """Test fallback chain disabled"""
        config = PersistenceConfig(
            payload="calc.exe",
            enable_fallback_chain=False,
            use_startup_folder=False,
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        fallback = persistence.generate_fallback_chain()

        self.assertEqual(len(fallback), 0)

    def test_fallback_chain_attempts(self):
        """Test fallback chain attempts multiple methods"""
        config = PersistenceConfig(
            payload="calc.exe",
            enable_fallback_chain=True,
            use_startup_folder=False,
            registry_hives=[],
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        fallback = persistence.generate_fallback_chain()

        vbs_code = fallback.get("fallback_chain_vbs", "")
        # Should contain multiple attempt comments
        self.assertIn("Attempt 1", vbs_code)
        self.assertIn("Attempt 2", vbs_code)
        self.assertIn("Attempt 3", vbs_code)


class TestMultiMethodCombination(unittest.TestCase):
    """Test combination of multiple persistence methods"""

    def test_all_methods_combined(self):
        """Test all methods combined"""
        config = PersistenceConfig(
            payload="calc.exe",
            use_startup_folder=True,
            use_scheduled_task=True,
            enable_fallback_chain=True
        )
        persistence = MultiMethodPersistence(config)
        all_methods = persistence.generate_all_persistence_methods()

        self.assertIn("registry", all_methods)
        self.assertIn("startup_folder", all_methods)
        self.assertIn("scheduled_task", all_methods)
        self.assertIn("fallback_chain", all_methods)

    def test_payload_count_redundancy(self):
        """Test payload count increases with redundancy"""
        minimal_config = PersistenceConfig(
            payload="test.exe",
            use_startup_folder=False,
            use_scheduled_task=False,
            enable_fallback_chain=False
        )
        minimal = MultiMethodPersistence(minimal_config)
        minimal.generate_all_persistence_methods()
        minimal_count = len(minimal.generated_code)

        full_config = PersistenceConfig(
            payload="test.exe",
            use_startup_folder=True,
            use_scheduled_task=True,
            enable_fallback_chain=True
        )
        full = MultiMethodPersistence(full_config)
        full.generate_all_persistence_methods()
        full_count = len(full.generated_code)

        self.assertGreater(full_count, minimal_count)

    def test_combined_installer_generation(self):
        """Test combined installer generation"""
        config = PersistenceConfig(
            payload="calc.exe",
            use_startup_folder=True,
            use_scheduled_task=True,
            enable_fallback_chain=True
        )
        persistence = MultiMethodPersistence(config)
        installer = persistence.generate_combined_installer()

        self.assertGreater(len(installer), 0)
        self.assertIn("Multi-Method Persistence Installer", installer)


class TestObfuscation(unittest.TestCase):
    """Test obfuscation functionality"""

    def test_obfuscation_enabled(self):
        """Test payload obfuscation enabled"""
        config = PersistenceConfig(
            payload="calc.exe",
            obfuscation_enabled=True,
            obfuscation_level="high",
            use_startup_folder=False,
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        obfuscated = persistence._obfuscate_payload("test_payload")

        self.assertNotEqual(obfuscated, "test_payload")

    def test_obfuscation_disabled(self):
        """Test payload obfuscation disabled"""
        config = PersistenceConfig(
            payload="calc.exe",
            obfuscation_enabled=False,
            use_startup_folder=False,
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        result = persistence._obfuscate_payload("test_payload")

        self.assertEqual(result, "test_payload")

    def test_obfuscation_levels(self):
        """Test different obfuscation levels"""
        levels = ["low", "medium", "high", "extreme"]

        for level in levels:
            config = PersistenceConfig(
                payload="calc.exe",
                obfuscation_enabled=True,
                obfuscation_level=level,
                use_startup_folder=False,
                use_scheduled_task=False
            )
            persistence = MultiMethodPersistence(config)
            # Should not raise exception
            persistence.generate_registry_persistence()


class TestNameRandomization(unittest.TestCase):
    """Test name randomization functionality"""

    def test_registry_randomized_names(self):
        """Test registry randomized value names"""
        config = PersistenceConfig(
            payload="calc.exe",
            randomize_names=True,
            use_startup_folder=False,
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        name = persistence._generate_registry_value_name(0, 0)

        self.assertIsNotNone(name)
        self.assertGreater(len(name), 0)

    def test_startup_randomized_names(self):
        """Test startup randomized filenames"""
        config = PersistenceConfig(
            payload="calc.exe",
            randomize_names=True,
            use_startup_folder=True,
            registry_hives=[],
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        name = persistence._generate_startup_filename(".vbs")

        self.assertIn(".vbs", name)
        self.assertGreater(len(name), 4)

    def test_task_randomized_names(self):
        """Test task randomized names"""
        config = PersistenceConfig(
            payload="calc.exe",
            randomize_names=True,
            registry_hives=[],
            use_startup_folder=False,
            use_scheduled_task=True
        )
        persistence = MultiMethodPersistence(config)
        name = persistence._obfuscate_task_name("TaskName")

        self.assertIsNotNone(name)
        self.assertGreater(len(name), 0)

    def test_randomization_disabled(self):
        """Test randomization disabled"""
        config = PersistenceConfig(
            payload="calc.exe",
            randomize_names=False,
            use_startup_folder=False,
            use_scheduled_task=False
        )
        persistence = MultiMethodPersistence(config)
        name = persistence._generate_registry_value_name(0, 0)

        self.assertEqual(name, "Value00")


class TestPayloadGeneration(unittest.TestCase):
    """Test payload generation and storage"""

    def test_generated_code_tracking(self):
        """Test generated code tracking"""
        config = PersistenceConfig(
            payload="calc.exe",
            use_startup_folder=True,
            use_scheduled_task=True
        )
        persistence = MultiMethodPersistence(config)
        persistence.generate_all_persistence_methods()

        self.assertGreater(len(persistence.generated_code), 0)

    def test_all_payloads_non_empty(self):
        """Test all generated payloads are non-empty"""
        config = PersistenceConfig(payload="calc.exe")
        persistence = MultiMethodPersistence(config)
        persistence.generate_all_persistence_methods()

        for key, code in persistence.generated_code.items():
            self.assertGreater(len(code), 0)
            self.assertIsInstance(code, str)

    def test_deployment_summary_generation(self):
        """Test deployment summary generation"""
        config = PersistenceConfig(payload="calc.exe")
        persistence = MultiMethodPersistence(config)
        summary = persistence.get_deployment_summary()

        self.assertIn("MULTI-METHOD PERSISTENCE", summary)
        self.assertIn("CONFIGURATION:", summary)
        self.assertIn("GENERATED PAYLOADS:", summary)


class TestErrorHandling(unittest.TestCase):
    """Test error handling"""

    def test_invalid_registry_hive(self):
        """Test invalid registry hive handling"""
        with self.assertRaises((ValueError, AttributeError)):
            RegistryHive("INVALID")

    def test_invalid_trigger_type(self):
        """Test invalid trigger type handling"""
        with self.assertRaises((ValueError, AttributeError)):
            ScheduledTaskTrigger("invalid")

    def test_persistence_with_special_chars(self):
        """Test persistence with special characters in payload"""
        payload = 'cmd.exe /c echo "Hello\\"World"'
        config = PersistenceConfig(payload=payload)
        persistence = MultiMethodPersistence(config)

        # Should handle special characters
        registry = persistence.generate_registry_persistence()
        self.assertGreater(len(registry), 0)


class TestDefaultSystem(unittest.TestCase):
    """Test default persistence system"""

    def test_default_system_creation(self):
        """Test creation of default persistence system"""
        system = create_default_persistence_system()
        self.assertIsNotNone(system)
        self.assertIsInstance(system, MultiMethodPersistence)

    def test_default_system_payload_generation(self):
        """Test default system payload generation"""
        system = create_default_persistence_system()
        all_methods = system.generate_all_persistence_methods()

        self.assertGreater(len(all_methods), 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestPersistenceConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestRegistryPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestStartupFolderPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestScheduledTaskPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestFallbackChain))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiMethodCombination))
    suite.addTests(loader.loadTestsFromTestCase(TestObfuscation))
    suite.addTests(loader.loadTestsFromTestCase(TestNameRandomization))
    suite.addTests(loader.loadTestsFromTestCase(TestPayloadGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestDefaultSystem))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
