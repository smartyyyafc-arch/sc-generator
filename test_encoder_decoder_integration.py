#!/usr/bin/env python3
"""
Integration tests for Base64Encoder with VBSEncoder decoder.
Verifies that encoder-generated payloads work correctly with VBS decoder.
"""

import unittest
import base64
from base64_encoder import Base64Encoder, Base64OperationsPair
from vbs_encoder import VBSEncoder, ObfuscationConfig


class TestEncoderDecoderIntegration(unittest.TestCase):
    """Test Base64Encoder integration with VBSEncoder decoder"""

    def setUp(self):
        self.encoder = Base64Encoder()
        self.vbs_encoder = VBSEncoder()

    def test_encoder_output_decodable_by_vbs(self):
        """Test that encoder output can be decoded by VBS decoder logic"""
        test_string = "Test Payload"
        encoded = self.encoder.encode_to_base64(test_string)

        # Simulate what VBS decoder does:
        # It uses MSXML2.DOMDocument to decode
        # The Python equivalent is base64.b64decode
        decoded = base64.b64decode(encoded).decode()

        self.assertEqual(decoded, test_string)

    def test_encoder_generates_valid_vbs_code(self):
        """Test that encoder generates valid VBS code"""
        payload = "cmd /c echo Hello"
        vbs_code = self.encoder.create_vbs_encoded_variable(payload)

        # VBS code should contain Dim statement
        self.assertIn("Dim", vbs_code)
        # Should contain the encoded payload
        self.assertIn(base64.b64encode(payload.encode()).decode(), vbs_code)

    def test_vbs_decoder_pair_generation(self):
        """Test paired encoder-decoder VBS generation"""
        text = "Test Payload"
        encoder_code, decoder_code = self.encoder.create_vbs_decoder_pair(text)

        # Both should contain Dim statements
        self.assertIn("Dim", encoder_code)
        self.assertIn("Dim", decoder_code)

        # Decoder should contain decoder logic
        self.assertIn("CreateObject", decoder_code)
        self.assertIn("MSXML2", decoder_code)

    def test_encoder_with_vbs_full_obfuscation(self):
        """Test encoder with full VBS obfuscation pipeline"""
        command = "powershell.exe -NoProfile -Command Get-Process"

        # Step 1: Encode with encoder
        encoded = self.encoder.encode_to_base64(command)

        # Step 2: Create VBS decoder
        vbs_code = self.vbs_encoder.create_base64_decoder_vbs(command)

        # Step 3: Verify VBS code is generated
        self.assertIsNotNone(vbs_code)
        self.assertIn("Dim", vbs_code)
        self.assertIn("CreateObject", vbs_code)

    def test_command_encoding_for_vbs_execution(self):
        """Test command encoding specifically for VBS execution"""
        commands = [
            "cmd /c echo Hello",
            "powershell.exe -Command \"Get-Process\"",
            "net user admin",
            "tasklist /v"
        ]

        for command in commands:
            # Encode with encoder
            encoded = self.encoder.encode_command_payload(command)

            # Verify it can be decoded
            decoded = base64.b64decode(encoded).decode()
            self.assertEqual(decoded, command)

            # Create VBS code for this command
            vbs_code = self.vbs_encoder.create_base64_decoder_vbs(command)
            self.assertIsNotNone(vbs_code)

    def test_batch_encode_for_vbs_multiple_payloads(self):
        """Test batch encoding for multiple VBS payloads"""
        commands = [
            "whoami",
            "ipconfig /all",
            "tasklist",
            "systeminfo",
            "net view"
        ]

        # Batch encode
        encoded_dict = self.encoder.batch_encode_multiple(commands)

        # Verify each can be used with VBS decoder
        for original_cmd, encoded_cmd in encoded_dict.items():
            # Can be decoded
            decoded = base64.b64decode(encoded_cmd).decode()
            self.assertEqual(decoded, original_cmd)

            # Can be used in VBS
            vbs_code = self.vbs_encoder.create_base64_decoder_vbs(original_cmd)
            self.assertIsNotNone(vbs_code)

    def test_powershell_encoding_not_vbs_base64(self):
        """Test that PowerShell encoding is different from VBS Base64"""
        command = "Write-Host 'Test'"

        # Standard Base64 (for VBS)
        vbs_encoded = self.encoder.encode_to_base64(command)

        # PowerShell UTF-16LE (for PowerShell -EncodedCommand)
        ps_encoded = self.encoder.create_powershell_encoded_command(command)

        # They should be different
        self.assertNotEqual(vbs_encoded, ps_encoded)

        # Both should decode to original
        vbs_decoded = base64.b64decode(vbs_encoded).decode()
        ps_decoded = base64.b64decode(ps_encoded).decode('utf-16-le')

        self.assertEqual(vbs_decoded, command)
        self.assertEqual(ps_decoded, command)

    def test_file_content_encoding_for_vbs(self):
        """Test file content encoding for use in VBS"""
        file_content = """@echo off
cls
echo System Information:
systeminfo
pause"""

        # Encode file content
        encoded = self.encoder.encode_file_content(file_content)

        # Can be used in VBS
        vbs_code = self.vbs_encoder.create_base64_decoder_vbs(file_content)
        self.assertIsNotNone(vbs_code)

        # Can be decoded back
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, file_content)

    def test_encoder_with_vbs_polymorphic_wrapper(self):
        """Test encoder payload works with polymorphic VBS wrapper"""
        payload = "cmd /c tasklist"
        encoded = self.encoder.encode_to_base64(payload)

        # Create full obfuscated payload
        full_payload = self.vbs_encoder.create_full_obfuscated_payload(payload, "base64")

        # Should be valid VBS code
        self.assertIsNotNone(full_payload)
        self.assertIn("Dim", full_payload)

        # Add polymorphic wrapper
        polymorphic = self.vbs_encoder.create_polymorphic_wrapper(full_payload)

        # Should still be valid VBS code
        self.assertIsNotNone(polymorphic)
        self.assertIn("Dim", polymorphic)

    def test_encoder_verification_with_vbs_decoding(self):
        """Test encoder verification works with VBS decoding scenario"""
        texts = [
            "Test",
            "Command /c",
            "PowerShell -NoProfile",
            "Special!@#$%^&*()"
        ]

        for text in texts:
            encoded = self.encoder.encode_to_base64(text)

            # Verification should pass
            is_valid = self.encoder.verify_encoding(text, encoded)
            self.assertTrue(is_valid)

            # VBS decoder should work
            vbs_code = self.vbs_encoder.create_base64_decoder_vbs(text)
            self.assertIsNotNone(vbs_code)

    def test_lookup_table_for_vbs_payload_selection(self):
        """Test lookup table for dynamic VBS payload selection"""
        payloads = [
            "cmd /c ipconfig",
            "powershell Get-Process",
            "net user",
            "tasklist /v"
        ]

        lookup = self.encoder.create_reverse_lookup_table(payloads)

        # Test forward lookup (pick encoding for payload)
        for payload in payloads:
            encoded = lookup['forward'][payload]
            self.assertIsNotNone(encoded)
            # Should be decodable
            decoded = base64.b64decode(encoded).decode()
            self.assertEqual(decoded, payload)

        # Test reverse lookup (find payload from encoding)
        for payload in payloads:
            encoded = lookup['forward'][payload]
            found_payload = lookup['reverse'][encoded]
            self.assertEqual(found_payload, payload)

    def test_encoder_bytes_for_binary_vbs_payload(self):
        """Test encoding binary data for VBS use"""
        binary_data = bytes([0x00, 0x01, 0x02, 0x03, 0xFF, 0xFE])

        # Encode bytes
        encoded = self.encoder.encode_bytes_to_base64(binary_data)

        # Create VBS variable with encoded bytes
        text = encoded
        vbs_var = self.encoder.create_vbs_encoded_variable(text, "binaryData")
        self.assertIn("Dim", vbs_var)
        # The VBS var contains the base64 of the already-encoded bytes
        self.assertIn("binaryData", vbs_var)

    def test_round_trip_with_vbs_simulation(self):
        """Test round-trip encode-decode simulating VBS decoder"""
        test_strings = [
            "Simple Test",
            "cmd /c echo %USERNAME%",
            "powershell.exe -NoProfile",
            "Complex String with !@#$%^&*()"
        ]

        ops = Base64OperationsPair()

        for test_str in test_strings:
            # Encode (like Python prepares)
            encoded = ops.encode(test_str)

            # Simulate VBS decode
            vbs_simulated_decoded = base64.b64decode(encoded).decode()

            # Full round trip
            round_trip_success = ops.round_trip_transform(test_str)

            self.assertEqual(vbs_simulated_decoded, test_str)
            self.assertTrue(round_trip_success)

    def test_caching_with_vbs_repeated_payloads(self):
        """Test caching efficiency with repeated VBS payloads"""
        payload = "cmd /c echo test"

        # First encoding (cache miss)
        encoded1, key1 = self.encoder.encode_to_base64_with_cache(payload)

        # Second encoding (cache hit)
        encoded2, key2 = self.encoder.encode_to_base64_with_cache(payload)

        # Should be identical
        self.assertEqual(encoded1, encoded2)
        self.assertEqual(key1, key2)

        # Both should work with VBS
        vbs_code1 = self.vbs_encoder.create_base64_decoder_vbs(payload)
        vbs_code2 = self.vbs_encoder.create_base64_decoder_vbs(payload)
        self.assertIsNotNone(vbs_code1)
        self.assertIsNotNone(vbs_code2)


class TestEncoderVBSRuntimeExecution(unittest.TestCase):
    """Test encoder output in VBS runtime execution scenario"""

    def setUp(self):
        self.encoder = Base64Encoder()
        self.vbs_encoder = VBSEncoder()

    def test_runtime_decoded_payload_generation(self):
        """Test creating runtime-decoded payload"""
        payload = "powershell.exe -Command Get-Process"

        # Create runtime decoded payload
        runtime_payload = self.vbs_encoder.create_runtime_decoded_payload(
            payload, encoding="base64"
        )

        # Should contain encoded payload
        self.assertIsNotNone(runtime_payload)
        self.assertIn("Dim", runtime_payload)

    def test_wscript_execution_with_encoded_payload(self):
        """Test WScript hidden execution with encoded payload"""
        command = "calc.exe"

        # Create hidden execution
        exec_code = self.vbs_encoder.create_wscript_hidden_execution(command)

        # Should contain CreateObject
        self.assertIn("CreateObject", exec_code)
        self.assertIn("WScript.Shell", exec_code)

    def test_hex_decoder_alternative(self):
        """Test that hex encoding is alternative to Base64"""
        text = "test payload"

        # Base64 encoding
        b64_encoded = self.encoder.encode_to_base64(text)

        # Hex encoding via VBS
        hex_code = self.vbs_encoder.create_hex_decoder_vbs(text)

        # Both should be valid
        self.assertIsNotNone(b64_encoded)
        self.assertIsNotNone(hex_code)


if __name__ == "__main__":
    unittest.main(verbosity=2)
