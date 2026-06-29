#!/usr/bin/env python3
"""
Unit tests for VBS encoder and payload generator
"""

import unittest
from vbs_encoder import VBSEncoder, ObfuscationConfig, generate_clean_vbs_payload
from vbs_advanced_obfuscation import (
    AdvancedVBSObfuscation,
    create_stealthy_payload,
)
from payload_generator import PayloadGenerator


class TestVBSEncoder(unittest.TestCase):
    """Test basic VBS encoder functionality"""

    def setUp(self):
        self.encoder = VBSEncoder()

    def test_base64_encoding(self):
        """Test base64 string encoding"""
        text = "Test String"
        encoded, var_name = self.encoder.encode_string_base64(text)
        self.assertIsNotNone(encoded)
        self.assertIsNotNone(var_name)
        self.assertTrue(var_name.startswith("v_"))

    def test_hex_encoding(self):
        """Test hex string encoding"""
        text = "Test String"
        encoded, var_name = self.encoder.encode_string_hex(text)
        self.assertIsNotNone(encoded)
        self.assertIsNotNone(var_name)
        self.assertTrue(var_name.startswith("h_"))

    def test_base64_decoder_vbs_generation(self):
        """Test VBS base64 decoder code generation"""
        payload = "Test payload command"
        vbs_code = self.encoder.create_base64_decoder_vbs(payload)
        self.assertIn("MSXML2.DOMDocument", vbs_code)
        self.assertIn("CreateObject", vbs_code)

    def test_hex_decoder_vbs_generation(self):
        """Test VBS hex decoder code generation"""
        text = "Test String"
        vbs_code = self.encoder.create_hex_decoder_vbs(text)
        self.assertIn("Function", vbs_code)
        self.assertIn("Chr(CLng", vbs_code)

    def test_array_concatenation_decoder(self):
        """Test array-based concatenation decoder"""
        text = "Test String for array encoding"
        vbs_code = self.encoder.create_array_concatenation_decoder(text)
        self.assertIn("Dim", vbs_code)
        self.assertIn("For Each", vbs_code)

    def test_wscript_hidden_execution(self):
        """Test WScript hidden execution wrapper"""
        command = "cmd /c echo test"
        vbs_code = self.encoder.create_wscript_hidden_execution(command)
        self.assertIn("WScript.Shell", vbs_code)
        self.assertIn("0", vbs_code)  # Hidden window

    def test_polymorphic_wrapper(self):
        """Test polymorphic wrapper generation"""
        code = "Dim x"
        wrapped = self.encoder.create_polymorphic_wrapper(code)
        self.assertIsNotNone(wrapped)
        self.assertIn("Dim", wrapped)
        self.assertIn("x", wrapped)

    def test_obfuscate_command(self):
        """Test command obfuscation"""
        command = "powershell.exe -Command test"
        vbs_code = self.encoder.obfuscate_command(command)
        self.assertIn("CreateObject", vbs_code)
        self.assertIn(".Run", vbs_code)


class TestAdvancedObfuscation(unittest.TestCase):
    """Test advanced obfuscation techniques"""

    def setUp(self):
        self.obf = AdvancedVBSObfuscation()

    def test_environment_variable_decoder(self):
        """Test environment variable decoding"""
        payload = "Test payload"
        vbs_code = self.obf.create_environment_variable_decoder(payload)
        self.assertIn("Environment", vbs_code)
        self.assertIn("reconstructed", vbs_code)

    def test_wmi_execution(self):
        """Test WMI execution wrapper"""
        command = "cmd /c echo test"
        vbs_code = self.obf.create_wmi_execution_wrapper(command)
        self.assertIn("winmgmts", vbs_code)
        self.assertIn("Win32_Process", vbs_code)

    def test_registry_storage(self):
        """Test registry-based payload storage"""
        payload = "Test payload"
        vbs_code = self.obf.create_registry_stored_payload(payload)
        self.assertIn("RegWrite", vbs_code)
        self.assertIn("RegRead", vbs_code)

    def test_obfuscated_calls(self):
        """Test obfuscated function calls"""
        command = "cmd /c test"
        vbs_code = self.obf.create_obfuscated_function_calls(command)
        self.assertIn("&", vbs_code)  # String concatenation
        self.assertIn("CreateObject", vbs_code)

    def test_filewriter_injection(self):
        """Test file writer injection"""
        command = "cmd /c test"
        vbs_code = self.obf.create_filewriter_injection(command)
        self.assertIn("CreateTextFile", vbs_code)
        self.assertIn("DeleteFile", vbs_code)

    def test_multi_encoding_chain(self):
        """Test multi-encoding chain"""
        payload = "Test String"
        vbs_code = self.obf.create_multi_encoding_chain(payload)
        self.assertIn("chunk", vbs_code)
        self.assertIn("hexDecode", vbs_code)


class TestPayloadGenerator(unittest.TestCase):
    """Test payload generator interface"""

    def setUp(self):
        self.gen = PayloadGenerator()

    def test_generator_initialization(self):
        """Test generator initializes correctly"""
        self.assertIsNotNone(self.gen)
        self.assertTrue(len(self.gen.techniques) > 0)

    def test_list_techniques(self):
        """Test technique listing"""
        techniques = self.gen.list_techniques()
        self.assertIn("base64", techniques)
        self.assertIn("wmi", techniques)
        self.assertIn("registry", techniques)

    def test_technique_info(self):
        """Test technique info retrieval"""
        info = self.gen.get_technique_info("base64")
        self.assertIsNotNone(info)
        self.assertTrue(len(info) > 0)

    def test_generate_base64(self):
        """Test base64 payload generation"""
        command = "cmd /c echo test"
        payload = self.gen.generate(command, technique="base64")
        self.assertIsNotNone(payload)
        self.assertIn("CreateObject", payload)

    def test_generate_wmi(self):
        """Test WMI payload generation"""
        command = "cmd /c test"
        payload = self.gen.generate(command, technique="wmi")
        self.assertIsNotNone(payload)
        self.assertIn("Win32_Process", payload)

    def test_generate_registry(self):
        """Test registry payload generation"""
        command = "cmd /c test"
        payload = self.gen.generate(command, technique="registry")
        self.assertIsNotNone(payload)
        self.assertIn("RegWrite", payload)

    def test_generate_multi_encoding(self):
        """Test multi-encoding payload"""
        command = "powershell.exe -Command test"
        payload = self.gen.generate(command, technique="multi_encoding")
        self.assertIsNotNone(payload)
        self.assertTrue(len(payload) > 100)

    def test_generate_with_high_obfuscation(self):
        """Test high obfuscation level"""
        command = "cmd /c test"
        payload = self.gen.generate(
            command, technique="base64", obfuscation_level="high"
        )
        self.assertIsNotNone(payload)
        self.assertIn("Dim", payload)


class TestCleanVBSPayload(unittest.TestCase):
    """Test clean VBS payload generation"""

    def test_low_obfuscation(self):
        """Test low obfuscation level"""
        payload = generate_clean_vbs_payload("cmd /c test", "low")
        self.assertIsNotNone(payload)
        self.assertIn("Run", payload)

    def test_medium_obfuscation(self):
        """Test medium obfuscation level"""
        payload = generate_clean_vbs_payload("cmd /c test", "medium")
        self.assertIsNotNone(payload)
        self.assertIn("DecodeHex", payload)

    def test_high_obfuscation(self):
        """Test high obfuscation level"""
        payload = generate_clean_vbs_payload("cmd /c test", "high")
        self.assertIsNotNone(payload)
        self.assertTrue(len(payload) > 100)


class TestStealthyPayload(unittest.TestCase):
    """Test stealthy payload creation"""

    def test_all_techniques(self):
        """Test all stealthy techniques"""
        command = "cmd /c test"
        techniques = [
            "wmi",
            "registry",
            "env",
            "com",
            "multi",
            "obfuscated_calls",
            "filewriter",
        ]

        for technique in techniques:
            with self.subTest(technique=technique):
                payload = create_stealthy_payload(command, technique)
                self.assertIsNotNone(payload)
                self.assertTrue(len(payload) > 0)


class TestPayloadQuality(unittest.TestCase):
    """Test payload quality and characteristics"""

    def setUp(self):
        self.gen = PayloadGenerator()

    def test_payload_is_valid_vbs_syntax(self):
        """Test that generated payloads contain valid VBS syntax"""
        command = "cmd /c test"
        payload = self.gen.generate(command, technique="base64")

        # Check for required VBS elements
        self.assertIn("Dim", payload)
        self.assertIn("CreateObject", payload)

    def test_payload_contains_error_handling(self):
        """Test that payloads include error handling"""
        command = "cmd /c test"
        payload = self.gen.generate(command, technique="wmi")
        self.assertIn("Error", payload)

    def test_payload_executes_hidden(self):
        """Test that payloads execute without visible window"""
        command = "cmd /c test"
        payload = self.gen.generate(command, technique="base64")
        # Look for window hiding (usually 0 in Run parameters)
        self.assertIn("0", payload)

    def test_payload_size_reasonable(self):
        """Test that payload sizes are reasonable"""
        command = "cmd /c echo test"

        payloads = {
            "basic": self.gen.generate(command, technique="basic"),
            "base64": self.gen.generate(command, technique="base64"),
            "wmi": self.gen.generate(command, technique="wmi"),
        }

        for technique, payload in payloads.items():
            with self.subTest(technique=technique):
                # Payload should be at least 100 bytes but not unreasonably large
                self.assertGreater(len(payload), 50)
                self.assertLess(len(payload), 50000)


if __name__ == "__main__":
    unittest.main()
