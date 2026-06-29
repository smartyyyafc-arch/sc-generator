#!/usr/bin/env python3
"""
Unit tests for Base64Encoder - Verify reverse operations with VBS decoder
"""

import unittest
import base64
from base64_encoder import Base64Encoder, Base64OperationsPair


class TestBase64EncoderBasics(unittest.TestCase):
    """Test basic encoding operations"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_encode_simple_string(self):
        """Test encoding a simple string"""
        text = "Hello World"
        encoded = self.encoder.encode_to_base64(text)
        self.assertEqual(encoded, "SGVsbG8gV29ybGQ=")

    def test_encode_empty_string(self):
        """Test encoding an empty string"""
        text = ""
        encoded = self.encoder.encode_to_base64(text)
        self.assertEqual(encoded, "")

    def test_encode_special_characters(self):
        """Test encoding special characters"""
        text = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        encoded = self.encoder.encode_to_base64(text)
        # Verify by decoding back
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_unicode(self):
        """Test encoding unicode characters"""
        text = "Hello 世界 مرحبا"
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_long_string(self):
        """Test encoding a long string"""
        text = "A" * 10000
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)


class TestBase64EncoderCaching(unittest.TestCase):
    """Test caching functionality"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_caching_same_input(self):
        """Test that caching returns same result for same input"""
        text = "Test String"
        encoded1, key1 = self.encoder.encode_to_base64_with_cache(text)
        encoded2, key2 = self.encoder.encode_to_base64_with_cache(text)

        self.assertEqual(encoded1, encoded2)
        self.assertEqual(key1, key2)

    def test_cache_different_inputs(self):
        """Test that different inputs get different keys"""
        text1 = "String 1"
        text2 = "String 2"

        encoded1, key1 = self.encoder.encode_to_base64_with_cache(text1)
        encoded2, key2 = self.encoder.encode_to_base64_with_cache(text2)

        self.assertNotEqual(encoded1, encoded2)
        self.assertNotEqual(key1, key2)


class TestBase64EncoderRoundTrip(unittest.TestCase):
    """Test encode-decode round trip operations"""

    def setUp(self):
        self.ops = Base64OperationsPair()

    def test_round_trip_simple(self):
        """Test round trip for simple string"""
        original = "Round Trip Test"
        success = self.ops.round_trip_transform(original)
        self.assertTrue(success)

    def test_round_trip_empty(self):
        """Test round trip for empty string"""
        original = ""
        success = self.ops.round_trip_transform(original)
        self.assertTrue(success)

    def test_round_trip_special_chars(self):
        """Test round trip with special characters"""
        original = "Test!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        success = self.ops.round_trip_transform(original)
        self.assertTrue(success)

    def test_round_trip_large_text(self):
        """Test round trip with large text"""
        original = "X" * 50000
        success = self.ops.round_trip_transform(original)
        self.assertTrue(success)


class TestBase64EncoderVerification(unittest.TestCase):
    """Test verification functionality"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_verify_valid_encoding(self):
        """Test verification of valid encoding"""
        original = "Test"
        encoded = self.encoder.encode_to_base64(original)
        result = self.encoder.verify_encoding(original, encoded)
        self.assertTrue(result)

    def test_verify_invalid_encoding(self):
        """Test verification of invalid encoding"""
        original = "Test"
        invalid_encoded = "InvalidBase64!!!"
        result = self.encoder.verify_encoding(original, invalid_encoded)
        self.assertFalse(result)

    def test_verify_mismatched_content(self):
        """Test verification with mismatched content"""
        original = "Test"
        other_text = "Different"
        encoded = self.encoder.encode_to_base64(other_text)
        result = self.encoder.verify_encoding(original, encoded)
        self.assertFalse(result)


class TestBase64EncoderBatchOperations(unittest.TestCase):
    """Test batch encoding operations"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_batch_encode_multiple(self):
        """Test encoding multiple strings at once"""
        texts = ["Command1", "Command2", "Command3"]
        results = self.encoder.batch_encode_multiple(texts)

        self.assertEqual(len(results), 3)
        for text in texts:
            self.assertIn(text, results)
            # Verify each can be decoded back
            decoded = base64.b64decode(results[text]).decode()
            self.assertEqual(decoded, text)

    def test_batch_encode_empty_list(self):
        """Test batch encoding with empty list"""
        results = self.encoder.batch_encode_multiple([])
        self.assertEqual(len(results), 0)


class TestBase64EncoderLookupTable(unittest.TestCase):
    """Test reverse lookup table functionality"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_lookup_table_forward(self):
        """Test forward lookup mapping"""
        texts = ["Text1", "Text2", "Text3"]
        lookup = self.encoder.create_reverse_lookup_table(texts)

        for text in texts:
            self.assertIn(text, lookup['forward'])
            # Verify encoded value
            encoded = lookup['forward'][text]
            decoded = base64.b64decode(encoded).decode()
            self.assertEqual(decoded, text)

    def test_lookup_table_reverse(self):
        """Test reverse lookup mapping"""
        texts = ["Text1", "Text2", "Text3"]
        lookup = self.encoder.create_reverse_lookup_table(texts)

        for text in texts:
            encoded = lookup['forward'][text]
            self.assertIn(encoded, lookup['reverse'])
            self.assertEqual(lookup['reverse'][encoded], text)


class TestBase64EncoderPowershell(unittest.TestCase):
    """Test PowerShell-specific encoding"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_powershell_encoding(self):
        """Test PowerShell UTF-16LE encoding"""
        command = "Write-Host 'Test'"
        encoded = self.encoder.create_powershell_encoded_command(command)

        # Decode and verify
        decoded = base64.b64decode(encoded).decode('utf-16-le')
        self.assertEqual(decoded, command)

    def test_powershell_encoding_with_special_chars(self):
        """Test PowerShell encoding with special characters"""
        command = "Get-Process | Where-Object {$_.CPU -gt 100}"
        encoded = self.encoder.create_powershell_encoded_command(command)

        # Decode and verify
        decoded = base64.b64decode(encoded).decode('utf-16-le')
        self.assertEqual(decoded, command)


class TestBase64EncoderVBSIntegration(unittest.TestCase):
    """Test VBS-specific encoding functionality"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_vbs_encoded_variable(self):
        """Test creating VBS encoded variable"""
        text = "Test Command"
        vbs_code = self.encoder.create_vbs_encoded_variable(text)

        self.assertIn("Dim", vbs_code)
        # Should contain the base64 encoded version
        expected_encoding = base64.b64encode(text.encode()).decode()
        self.assertIn(expected_encoding, vbs_code)

    def test_vbs_encoded_variable_custom_name(self):
        """Test creating VBS encoded variable with custom name"""
        text = "Test"
        var_name = "myVar"
        vbs_code = self.encoder.create_vbs_encoded_variable(text, var_name)

        self.assertIn(f"Dim {var_name}", vbs_code)
        self.assertIn(var_name, vbs_code)

    def test_vbs_decoder_pair(self):
        """Test creating paired VBS encoder-decoder"""
        text = "Test Payload"
        encoder_code, decoder_code = self.encoder.create_vbs_decoder_pair(text)

        # Both should contain VBS Dim statements
        self.assertIn("Dim", encoder_code)
        self.assertIn("Dim", decoder_code)

        # Decoder should contain the decoder logic
        self.assertIn("CreateObject", decoder_code)


class TestBase64EncoderBytesHandling(unittest.TestCase):
    """Test binary data handling"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_encode_bytes(self):
        """Test encoding bytes"""
        data = b"Test Binary Data"
        encoded = self.encoder.encode_bytes_to_base64(data)
        decoded = base64.b64decode(encoded)
        self.assertEqual(decoded, data)

    def test_encode_bytes_binary(self):
        """Test encoding binary bytes"""
        data = bytes(range(256))
        encoded = self.encoder.encode_bytes_to_base64(data)
        decoded = base64.b64decode(encoded)
        self.assertEqual(decoded, data)

    def test_encode_bytes_invalid_type(self):
        """Test encoding non-bytes raises error"""
        with self.assertRaises(TypeError):
            self.encoder.encode_bytes_to_base64("Not bytes")


class TestBase64EncoderPayloadTypes(unittest.TestCase):
    """Test different payload types"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_encode_command_payload(self):
        """Test encoding command payload"""
        command = "cmd /c echo test"
        encoded = self.encoder.encode_command_payload(command)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, command)

    def test_encode_file_content(self):
        """Test encoding file content"""
        content = """@echo off
echo Test Script
pause"""
        encoded = self.encoder.encode_file_content(content)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, content)


class TestBase64OperationsPairValidation(unittest.TestCase):
    """Test Base64OperationsPair validation"""

    def setUp(self):
        self.ops = Base64OperationsPair()

    def test_encode_with_validation_valid(self):
        """Test encode with validation succeeds for valid input"""
        text = "Valid Input"
        encoded = self.ops.encode_with_validation(text)
        decoded = self.ops.decode(encoded)
        self.assertEqual(decoded, text)

    def test_decode_invalid_base64(self):
        """Test decode raises error for invalid Base64"""
        with self.assertRaises(ValueError):
            self.ops.decode("Invalid!!!Base64")


class TestBase64EncoderErrorHandling(unittest.TestCase):
    """Test error handling"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_encode_invalid_type(self):
        """Test encoding non-string raises error"""
        with self.assertRaises(TypeError):
            self.encoder.encode_to_base64(12345)

    def test_encode_non_string_list(self):
        """Test encoding list raises error"""
        with self.assertRaises(TypeError):
            self.encoder.encode_to_base64([1, 2, 3])


if __name__ == "__main__":
    unittest.main(verbosity=2)
