#!/usr/bin/env python3
"""
Comprehensive test suite for command string obfuscator
"""

import unittest
import base64
import binascii
from command_string_obfuscator import (
    CommandStringObfuscator,
    CommandObfuscationConfig,
    EncodingMethod,
    Base64CommandEncoder,
    HexCommandEncoder,
    XORCommandEncoder,
    ArrayCommandEncoder,
    NestedCommandEncoder,
    PolymorphicCommandEncoder,
    encode_command,
    encode_to_vbs,
    encode_to_powershell,
    encode_to_bash,
)


class TestBase64Encoder(unittest.TestCase):
    """Test Base64 encoding"""

    def setUp(self):
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        self.encoder = Base64CommandEncoder(config)

    def test_encode_simple_command(self):
        """Test encoding a simple command"""
        command = "echo hello"
        encoded, metadata = self.encoder.encode(command)

        # Verify it's valid base64
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, command)

    def test_encode_complex_command(self):
        """Test encoding a complex command"""
        command = 'powershell.exe -NoProfile -WindowStyle Hidden -Command "Write-Host \'Test\'"'
        encoded, metadata = self.encoder.encode(command)

        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, command)

    def test_metadata_contains_required_fields(self):
        """Test metadata structure"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)

        self.assertIn("method", metadata)
        self.assertIn("variable_name", metadata)
        self.assertIn("decoder_name", metadata)
        self.assertEqual(metadata["method"], "base64")

    def test_decoder_code_generation(self):
        """Test decoder code generation"""
        command = "echo test"
        encoded, metadata = self.encoder.encode(command)
        code = self.encoder.generate_decoder_code(encoded, metadata)

        # Code should contain imports and variable names
        self.assertIn("import base64", code)
        self.assertIn("decode", code)
        self.assertIn("command", code)


class TestHexEncoder(unittest.TestCase):
    """Test Hex encoding"""

    def setUp(self):
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.HEX)
        self.encoder = HexCommandEncoder(config)

    def test_encode_simple_command(self):
        """Test hex encoding"""
        command = "echo hello"
        encoded, metadata = self.encoder.encode(command)

        # Verify hex decoding
        decoded = bytes.fromhex(encoded).decode()
        self.assertEqual(decoded, command)

    def test_hex_format_validation(self):
        """Test encoded data is valid hex"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)

        # Should be valid hex
        try:
            bytes.fromhex(encoded)
        except ValueError:
            self.fail("Encoded data is not valid hex")


class TestXOREncoder(unittest.TestCase):
    """Test XOR encoding"""

    def setUp(self):
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.XOR)
        self.encoder = XORCommandEncoder(config)

    def test_encode_with_key(self):
        """Test XOR encoding with specific key"""
        command = "test command"
        encoded, metadata = self.encoder.encode(command)

        # Verify decoding
        key = metadata["xor_key"]
        decoded = bytes([int(encoded[i : i + 2], 16) ^ key for i in range(0, len(encoded), 2)])
        self.assertEqual(decoded.decode(), command)

    def test_xor_key_derivation(self):
        """Test XOR key is derived consistently"""
        command = "test"
        encoded1, meta1 = self.encoder.encode(command)
        encoded2, meta2 = self.encoder.encode(command)

        # Same command should produce same key
        self.assertEqual(meta1["xor_key"], meta2["xor_key"])


class TestArrayEncoder(unittest.TestCase):
    """Test Array chunking encoder"""

    def setUp(self):
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.ARRAY)
        self.encoder = ArrayCommandEncoder(config)

    def test_encode_chunks(self):
        """Test command chunking"""
        command = "this is a test command"
        encoded, metadata = self.encoder.encode(command)

        chunks = metadata["chunks"]
        # Verify chunks can be reconstructed
        decoded_parts = [bytes.fromhex(c).decode() for c in chunks]
        decoded = "".join(decoded_parts)
        self.assertEqual(decoded, command)

    def test_chunk_size_respected(self):
        """Test chunk size configuration"""
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.ARRAY, chunk_size=8
        )
        encoder = ArrayCommandEncoder(config)

        command = "this is a longer test command with multiple chunks"
        encoded, metadata = encoder.encode(command)

        # Verify chunk count
        self.assertGreater(len(metadata["chunks"]), 1)

    def test_decode_chunks(self):
        """Test decoding from chunks"""
        command = "test command"
        encoded, metadata = self.encoder.encode(command)

        code = self.encoder.generate_decoder_code(encoded, metadata)
        self.assertIn("fromhex", code)
        self.assertIn("join", code)


class TestNestedEncoder(unittest.TestCase):
    """Test nested multi-layer encoding"""

    def setUp(self):
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.NESTED)
        self.encoder = NestedCommandEncoder(config)

    def test_nested_encoding_layers(self):
        """Test multi-layer encoding and decoding"""
        command = "test command"
        encoded, metadata = self.encoder.encode(command)

        # Verify layers are applied
        self.assertEqual(len(metadata["layers"]), 3)
        self.assertIn("base64", metadata["layers"])
        self.assertIn("hex", metadata["layers"])
        self.assertIn("reverse", metadata["layers"])

    def test_nested_decoder_code(self):
        """Test nested decoder code generation"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)
        code = self.encoder.generate_decoder_code(encoded, metadata)

        # Should reference multiple layers (case-insensitive)
        self.assertIn("Reverse", code)
        self.assertIn("fromhex", code)
        self.assertIn("base64", code)


class TestPolymorphicEncoder(unittest.TestCase):
    """Test polymorphic encoding"""

    def setUp(self):
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.POLYMORPH)
        self.encoder = PolymorphicCommandEncoder(config)

    def test_polymorph_produces_different_encodings(self):
        """Test that polymorphic encoder selects different methods"""
        command = "test"
        results = []

        for _ in range(5):
            encoded, metadata = self.encoder.encode(command)
            results.append(metadata.get("selected_encoder"))

        # At least some should be different (statistically likely with 5 attempts)
        unique_encoders = set(results)
        self.assertGreater(len(unique_encoders), 1)

    def test_polymorphic_metadata_tracking(self):
        """Test metadata includes polymorphic information"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)

        self.assertIn("selected_encoder", metadata)
        self.assertIn("polymorphic_key", metadata)


class TestCommandStringObfuscator(unittest.TestCase):
    """Test main obfuscator class"""

    def test_base64_obfuscation(self):
        """Test base64 obfuscation workflow"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        command = "echo test"
        result = obfuscator.obfuscate_command(command)

        self.assertIn("encoded_data", result)
        self.assertIn("metadata", result)
        self.assertIn("decoder_code", result)
        self.assertEqual(result["original_command"], command)

    def test_all_encoding_methods(self):
        """Test all encoding methods work"""
        command = "test command"

        for method in EncodingMethod:
            with self.subTest(method=method):
                config = CommandObfuscationConfig(encoding_method=method)
                obfuscator = CommandStringObfuscator(config)

                result = obfuscator.obfuscate_command(command)

                self.assertIsNotNone(result["encoded_data"])
                self.assertIn("decoder_code", result)

    def test_vbs_payload_generation(self):
        """Test VBS payload generation"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        command = "echo test"
        vbs_payload = obfuscator.generate_vbs_payload(command)

        # Payload should contain VBS keywords
        self.assertIn("CreateObject", vbs_payload)
        self.assertIn("WScript.Shell", vbs_payload)

    def test_powershell_payload_generation(self):
        """Test PowerShell payload generation"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        command = "Write-Host test"
        ps_payload = obfuscator.generate_powershell_payload(command)

        # Payload should contain PowerShell keywords
        self.assertIn("FromBase64String", ps_payload)
        self.assertIn("Invoke-Expression", ps_payload)

    def test_bash_payload_generation(self):
        """Test Bash payload generation"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        command = "echo test"
        bash_payload = obfuscator.generate_bash_payload(command)

        # Payload should contain bash keywords
        self.assertIn("base64", bash_payload)
        self.assertIn("eval", bash_payload)

    def test_python_payload_generation(self):
        """Test Python payload generation"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        command = "echo test"
        python_payload = obfuscator.generate_python_payload(command)

        # Should be valid Python code
        self.assertIn("import", python_payload)
        self.assertIn("subprocess", python_payload)

    def test_obfuscation_history_tracking(self):
        """Test obfuscation history is tracked"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        obfuscator.obfuscate_command("command1")
        obfuscator.obfuscate_command("command2")

        self.assertEqual(len(obfuscator._obfuscation_history), 2)

    def test_full_report_generation(self):
        """Test comprehensive report generation"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        command = "test command"
        report = obfuscator.generate_full_report(command)

        # Report should contain all sections
        self.assertIn("Original Command:", report)
        self.assertIn("Encoding Method:", report)
        self.assertIn("Decoder Code (Python):", report)
        self.assertIn("VBS Payload:", report)
        self.assertIn("PowerShell Payload:", report)
        self.assertIn("Bash Payload:", report)


class TestConvenienceFunctions(unittest.TestCase):
    """Test module-level convenience functions"""

    def test_encode_command_function(self):
        """Test encode_command shortcut"""
        command = "test"
        result = encode_command(command, EncodingMethod.BASE64)

        self.assertIn("encoded_data", result)
        self.assertIn("decoder_code", result)

    def test_encode_to_vbs_function(self):
        """Test encode_to_vbs shortcut"""
        command = "test"
        vbs = encode_to_vbs(command)

        self.assertIn("CreateObject", vbs)

    def test_encode_to_powershell_function(self):
        """Test encode_to_powershell shortcut"""
        command = "test"
        ps = encode_to_powershell(command)

        self.assertIn("FromBase64String", ps)

    def test_encode_to_bash_function(self):
        """Test encode_to_bash shortcut"""
        command = "test"
        bash = encode_to_bash(command)

        self.assertIn("base64", bash)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_roundtrip_encoding_decoding(self):
        """Test full encode-decode cycle"""
        original_command = "powershell.exe -NoProfile -Command Write-Host Hello"

        # Encode
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)
        result = obfuscator.obfuscate_command(original_command)

        # Decode
        encoded_data = result["encoded_data"]
        decoded = base64.b64decode(encoded_data).decode()

        self.assertEqual(decoded, original_command)

    def test_complex_command_with_special_chars(self):
        """Test encoding complex commands with special characters"""
        command = 'cmd.exe /c "echo test > file.txt && type file.txt"'

        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(command)
        decoded = base64.b64decode(result["encoded_data"]).decode()

        self.assertEqual(decoded, command)

    def test_large_command_encoding(self):
        """Test encoding large commands"""
        # Create a large command
        command = "powershell.exe " + " ".join(
            ["-CommandParameter" for _ in range(100)]
        )

        config = CommandObfuscationConfig(encoding_method=EncodingMethod.ARRAY)
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(command)

        self.assertIsNotNone(result["encoded_data"])
        self.assertGreater(len(result["encoded_data"]), 0)


class TestPerformance(unittest.TestCase):
    """Performance-related tests"""

    def test_randomization_performance(self):
        """Test randomization doesn't severely impact performance"""
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.BASE64, randomize_names=True
        )
        obfuscator = CommandStringObfuscator(config)

        import time

        command = "test command"

        start = time.time()
        for _ in range(100):
            obfuscator.obfuscate_command(command)
        elapsed = time.time() - start

        # Should complete 100 obfuscations in reasonable time
        self.assertLess(elapsed, 5.0)


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
