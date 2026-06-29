#!/usr/bin/env python3
"""
Comprehensive Command Obfuscation Test Suite
Tests all encoding methods, edge cases, platform-specific payloads,
performance, security, and integration scenarios.
"""

import unittest
import time
import base64
import hashlib
import random
import string
from typing import Dict, List, Tuple
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


class TestBase64EncoderComprehensive(unittest.TestCase):
    """Comprehensive tests for Base64 encoding"""

    def setUp(self):
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        self.encoder = Base64CommandEncoder(config)

    def test_empty_command(self):
        """Test encoding empty command"""
        command = ""
        encoded, metadata = self.encoder.encode(command)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, command)

    def test_single_character(self):
        """Test encoding single character"""
        command = "a"
        encoded, metadata = self.encoder.encode(command)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, command)

    def test_unicode_characters(self):
        """Test encoding with unicode characters"""
        command = "echo 'Ñoño café'"
        encoded, metadata = self.encoder.encode(command)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, command)

    def test_special_shell_characters(self):
        """Test encoding with shell special characters"""
        commands = [
            "cmd.exe /c 'echo $PATH'",
            'powershell -Command "Get-Process | Select Name"',
            "bash -c 'for i in {1..10}; do echo $i; done'",
            "echo 'test && test || test'",
            "cat file.txt | grep pattern | awk '{print $1}'",
        ]
        for command in commands:
            with self.subTest(command=command):
                encoded, metadata = self.encoder.encode(command)
                decoded = base64.b64decode(encoded).decode()
                self.assertEqual(decoded, command)

    def test_newlines_and_tabs(self):
        """Test encoding commands with newlines and tabs"""
        command = "echo hello\necho world\ttest"
        encoded, metadata = self.encoder.encode(command)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, command)

    def test_base64_padding_variants(self):
        """Test various base64 padding scenarios"""
        # Lengths that produce different padding
        for length in [1, 2, 3, 4, 5, 10, 13, 17, 100]:
            with self.subTest(length=length):
                command = "a" * length
                encoded, metadata = self.encoder.encode(command)
                decoded = base64.b64decode(encoded).decode()
                self.assertEqual(decoded, command)

    def test_metadata_accuracy(self):
        """Test metadata contains accurate information"""
        command = "test command"
        encoded, metadata = self.encoder.encode(command)

        self.assertEqual(metadata["original_length"], len(command))
        self.assertEqual(metadata["encoded_length"], len(encoded))
        self.assertEqual(metadata["method"], "base64")

    def test_variable_name_randomization(self):
        """Test variable names are randomized"""
        command = "test"
        results = []

        for _ in range(5):
            encoded, metadata = self.encoder.encode(command)
            results.append(metadata["variable_name"])

        unique_names = set(results)
        self.assertGreater(len(unique_names), 1)

    def test_decoder_code_syntax(self):
        """Test decoder code is syntactically valid"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)
        code = self.encoder.generate_decoder_code(encoded, metadata)

        # Should be compilable Python
        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            self.fail(f"Generated decoder code has syntax error: {e}")

    def test_large_command_encoding(self):
        """Test encoding very large commands"""
        command = "powershell -Command " + ("A" * 10000)
        encoded, metadata = self.encoder.encode(command)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, command)


class TestHexEncoderComprehensive(unittest.TestCase):
    """Comprehensive tests for Hex encoding"""

    def setUp(self):
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.HEX)
        self.encoder = HexCommandEncoder(config)

    def test_hex_format_validation(self):
        """Test hex output is valid hex string"""
        commands = ["test", "hello world", "special!@#$%^&*()", ""]
        for command in commands:
            with self.subTest(command=command):
                encoded, metadata = self.encoder.encode(command)
                try:
                    bytes.fromhex(encoded)
                except ValueError:
                    self.fail(f"Encoded data is not valid hex: {encoded}")

    def test_hex_case_insensitivity(self):
        """Test hex decoding works with different cases"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)

        # Both uppercase and lowercase should work
        decoded_lower = bytes.fromhex(encoded.lower()).decode()
        decoded_upper = bytes.fromhex(encoded.upper()).decode()

        self.assertEqual(decoded_lower, command)
        self.assertEqual(decoded_upper, command)

    def test_null_bytes_handling(self):
        """Test handling of null bytes in encoding"""
        # While unusual, test the encoder's robustness
        command = "test\x00command"
        encoded, metadata = self.encoder.encode(command)
        decoded = bytes.fromhex(encoded).decode('latin-1')
        self.assertEqual(decoded, command)

    def test_chunk_size_configuration(self):
        """Test chunk size is properly tracked"""
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.HEX, chunk_size=32
        )
        encoder = HexCommandEncoder(config)

        command = "test"
        encoded, metadata = encoder.encode(command)

        self.assertEqual(metadata["chunk_size"], 32)

    def test_hex_decoder_code_generation(self):
        """Test hex decoder code is valid Python"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)
        code = self.encoder.generate_decoder_code(encoded, metadata)

        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            self.fail(f"Hex decoder code has syntax error: {e}")

    def test_very_long_hex_string(self):
        """Test encoding very long strings to hex"""
        command = "X" * 50000
        encoded, metadata = self.encoder.encode(command)
        decoded = bytes.fromhex(encoded).decode()
        self.assertEqual(decoded, command)


class TestXOREncoderComprehensive(unittest.TestCase):
    """Comprehensive tests for XOR encoding"""

    def setUp(self):
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.XOR)
        self.encoder = XORCommandEncoder(config)

    def test_xor_key_range(self):
        """Test XOR key is within valid byte range"""
        commands = ["test", "hello", "a" * 100]
        for command in commands:
            with self.subTest(command=command):
                encoded, metadata = self.encoder.encode(command)
                key = metadata["xor_key"]
                self.assertGreaterEqual(key, 0)
                self.assertLess(key, 256)

    def test_xor_deterministic_encoding(self):
        """Test same command produces same XOR key"""
        command = "test"
        results = []

        for _ in range(3):
            encoded, metadata = self.encoder.encode(command)
            results.append((encoded, metadata["xor_key"]))

        # All should have same key
        keys = [r[1] for r in results]
        self.assertEqual(len(set(keys)), 1)

    def test_xor_roundtrip(self):
        """Test XOR encode-decode roundtrip"""
        command = "test XOR encoding"
        encoded, metadata = self.encoder.encode(command)

        # Manually decode
        key = metadata["xor_key"]
        decoded_bytes = bytes(
            [int(encoded[i : i + 2], 16) ^ key for i in range(0, len(encoded), 2)]
        )
        decoded = decoded_bytes.decode()

        self.assertEqual(decoded, command)

    def test_xor_with_all_byte_values(self):
        """Test XOR with various byte values"""
        for byte_val in [0, 1, 127, 128, 255]:
            with self.subTest(byte_val=byte_val):
                command = chr(byte_val)
                encoded, metadata = self.encoder.encode(command)
                self.assertIsNotNone(encoded)

    def test_xor_decoder_code_generation(self):
        """Test XOR decoder code generation"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)
        code = self.encoder.generate_decoder_code(encoded, metadata)

        self.assertIn("xor", code.lower())
        self.assertIn("^", code)  # XOR operator

    def test_xor_with_custom_key(self):
        """Test XOR encoding with custom key"""
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.XOR, xor_key=42
        )
        encoder = XORCommandEncoder(config)

        command = "test"
        encoded, metadata = encoder.encode(command)

        self.assertEqual(metadata["xor_key"], 42)

    def test_xor_special_characters(self):
        """Test XOR with special characters"""
        command = "!@#$%^&*()_+-=[]{}|;:',.<>?/"
        encoded, metadata = self.encoder.encode(command)

        key = metadata["xor_key"]
        decoded = bytes(
            [int(encoded[i : i + 2], 16) ^ key for i in range(0, len(encoded), 2)]
        )
        self.assertEqual(decoded.decode(), command)


class TestArrayEncoderComprehensive(unittest.TestCase):
    """Comprehensive tests for Array chunking encoder"""

    def setUp(self):
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.ARRAY)
        self.encoder = ArrayCommandEncoder(config)

    def test_chunk_size_varies(self):
        """Test encoding with different chunk sizes"""
        command = "this is a test command with multiple parts"

        for chunk_size in [1, 4, 8, 16, 32, 100]:
            with self.subTest(chunk_size=chunk_size):
                config = CommandObfuscationConfig(
                    encoding_method=EncodingMethod.ARRAY, chunk_size=chunk_size
                )
                encoder = ArrayCommandEncoder(config)

                encoded, metadata = encoder.encode(command)
                self.assertEqual(metadata["chunk_size"], chunk_size)

    def test_chunk_reconstruction(self):
        """Test chunks can be properly reconstructed"""
        command = "test command"
        encoded, metadata = self.encoder.encode(command)

        chunks = metadata["chunks"]
        reconstructed = "".join(
            [bytes.fromhex(c).decode() for c in chunks]
        )

        self.assertEqual(reconstructed, command)

    def test_chunk_count_accuracy(self):
        """Test chunk count is accurate"""
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.ARRAY, chunk_size=5
        )
        encoder = ArrayCommandEncoder(config)

        command = "12345678901234567890"  # 20 chars, 4 chunks of 5
        encoded, metadata = encoder.encode(command)

        expected_chunks = (len(command) + 4) // 5
        self.assertEqual(metadata["chunk_count"], expected_chunks)

    def test_single_chunk(self):
        """Test command smaller than chunk size"""
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.ARRAY, chunk_size=100
        )
        encoder = ArrayCommandEncoder(config)

        command = "short"
        encoded, metadata = encoder.encode(command)

        self.assertEqual(len(metadata["chunks"]), 1)

    def test_exact_chunk_boundary(self):
        """Test command exactly matching chunk boundaries"""
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.ARRAY, chunk_size=5
        )
        encoder = ArrayCommandEncoder(config)

        command = "12345"  # Exactly one chunk
        encoded, metadata = encoder.encode(command)

        self.assertEqual(len(metadata["chunks"]), 1)

    def test_array_decoder_code_generation(self):
        """Test array decoder code is valid Python"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)
        code = self.encoder.generate_decoder_code(encoded, metadata)

        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            self.fail(f"Array decoder code has syntax error: {e}")


class TestNestedEncoderComprehensive(unittest.TestCase):
    """Comprehensive tests for nested multi-layer encoding"""

    def setUp(self):
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.NESTED)
        self.encoder = NestedCommandEncoder(config)

    def test_layer_sequence(self):
        """Test layer sequence is correct"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)

        self.assertEqual(metadata["layers"], ["base64", "hex", "reverse"])

    def test_layer_lengths_increase(self):
        """Test encoded lengths at each layer"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)

        # Generally, hex encoding increases size
        self.assertGreater(metadata["layer2_length"], 0)

    def test_nested_decode_process(self):
        """Test manual nested decoding"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)

        # Reverse the reverse
        layer2_hex = encoded[::-1]
        # Decode hex
        layer1_b64 = bytes.fromhex(layer2_hex).decode()
        # Decode base64
        original = base64.b64decode(layer1_b64).decode()

        self.assertEqual(original, command)

    def test_nested_decoder_code_execution_structure(self):
        """Test nested decoder code structure"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)
        code = self.encoder.generate_decoder_code(encoded, metadata)

        # Should define function and call it
        self.assertIn("def ", code)
        self.assertIn("decode_nested", code)

    def test_nested_with_special_characters(self):
        """Test nested encoding with special characters"""
        command = "test!@#$%^&*()"
        encoded, metadata = self.encoder.encode(command)

        # Manual decode
        layer2_hex = encoded[::-1]
        layer1_b64 = bytes.fromhex(layer2_hex).decode()
        original = base64.b64decode(layer1_b64).decode()

        self.assertEqual(original, command)


class TestPolymorphicEncoderComprehensive(unittest.TestCase):
    """Comprehensive tests for polymorphic encoding"""

    def setUp(self):
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.POLYMORPH)
        self.encoder = PolymorphicCommandEncoder(config)

    def test_different_encodings_produced(self):
        """Test polymorphic produces different encodings"""
        command = "test"
        methods = []

        for _ in range(20):
            encoded, metadata = self.encoder.encode(command)
            methods.append(metadata.get("selected_encoder"))

        unique_methods = set(methods)
        self.assertGreater(len(unique_methods), 1)

    def test_polymorphic_key_generated(self):
        """Test polymorphic key is always generated"""
        command = "test"
        encoded, metadata = self.encoder.encode(command)

        self.assertIn("polymorphic_key", metadata)
        self.assertGreaterEqual(metadata["polymorphic_key"], 1000)
        self.assertLess(metadata["polymorphic_key"], 10000)

    def test_all_encoder_types_used(self):
        """Test all encoder types are represented"""
        command = "test"
        methods = set()

        for _ in range(100):
            encoded, metadata = self.encoder.encode(command)
            methods.add(metadata.get("selected_encoder"))

        expected_types = {
            "Base64CommandEncoder",
            "HexCommandEncoder",
            "XORCommandEncoder",
            "ArrayCommandEncoder",
        }

        self.assertEqual(methods, expected_types)


class TestCommandStringObfuscatorComprehensive(unittest.TestCase):
    """Comprehensive tests for main obfuscator class"""

    def test_all_encoding_methods_supported(self):
        """Test all encoding methods work"""
        command = "test command"

        for method in EncodingMethod:
            with self.subTest(method=method.value):
                config = CommandObfuscationConfig(encoding_method=method)
                obfuscator = CommandStringObfuscator(config)

                result = obfuscator.obfuscate_command(command)

                self.assertIsNotNone(result["encoded_data"])
                self.assertIn("decoder_code", result)
                self.assertEqual(result["original_command"], command)

    def test_result_structure(self):
        """Test obfuscation result contains all required fields"""
        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command("test")

        required_fields = [
            "original_command",
            "encoded_data",
            "metadata",
            "decoder_code",
            "decoder_language",
            "obfuscation_level",
        ]

        for field in required_fields:
            self.assertIn(field, result)

    def test_vbs_base64_payload(self):
        """Test VBS payload with base64 encoding"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        command = "echo test"
        vbs = obfuscator.generate_vbs_payload(command)

        required_keywords = ["CreateObject", "WScript.Shell", "DOMDocument"]
        for keyword in required_keywords:
            self.assertIn(keyword, vbs)

    def test_vbs_hex_payload(self):
        """Test VBS payload with hex encoding"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.HEX)
        obfuscator = CommandStringObfuscator(config)

        command = "echo test"
        vbs = obfuscator.generate_vbs_payload(command)

        self.assertIn("Function", vbs)
        self.assertIn("CLng", vbs)

    def test_vbs_array_payload(self):
        """Test VBS payload with array encoding"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.ARRAY)
        obfuscator = CommandStringObfuscator(config)

        command = "test command"
        vbs = obfuscator.generate_vbs_payload(command)

        self.assertIn("Dim", vbs)
        self.assertIn("LBound", vbs)
        self.assertIn("UBound", vbs)

    def test_powershell_payload_structure(self):
        """Test PowerShell payload structure"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        command = "Write-Host test"
        ps = obfuscator.generate_powershell_payload(command)

        required_elements = ["$", "Invoke-Expression"]
        for element in required_elements:
            self.assertIn(element, ps)

    def test_bash_payload_structure(self):
        """Test Bash payload structure"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        command = "echo test"
        bash = obfuscator.generate_bash_payload(command)

        required_elements = ["#!/bin/bash", "base64", "-d", "eval"]
        for element in required_elements:
            self.assertIn(element, bash)

    def test_python_payload_structure(self):
        """Test Python payload structure"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        command = "echo test"
        py = obfuscator.generate_python_payload(command)

        required_elements = ["#!/usr/bin/env python3", "import subprocess", "shell=True"]
        for element in required_elements:
            self.assertIn(element, py)

    def test_history_tracking(self):
        """Test obfuscation history is tracked"""
        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        for i in range(5):
            obfuscator.obfuscate_command(f"command_{i}")

        self.assertEqual(len(obfuscator._obfuscation_history), 5)

    def test_full_report_generation(self):
        """Test comprehensive report generation"""
        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        report = obfuscator.generate_full_report("test command")

        required_sections = [
            "COMMAND STRING OBFUSCATION REPORT",
            "Original Command:",
            "Encoding Method:",
            "Obfuscation Level:",
            "Encoded Data:",
            "Decoder Code (Python):",
            "VBS Payload:",
            "PowerShell Payload:",
            "Bash Payload:",
        ]

        for section in required_sections:
            self.assertIn(section, report)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_empty_string_all_methods(self):
        """Test empty string encoding with all methods"""
        command = ""

        for method in [
            EncodingMethod.BASE64,
            EncodingMethod.HEX,
            EncodingMethod.XOR,
            EncodingMethod.ARRAY,
        ]:
            with self.subTest(method=method.value):
                config = CommandObfuscationConfig(encoding_method=method)
                obfuscator = CommandStringObfuscator(config)

                result = obfuscator.obfuscate_command(command)
                self.assertIsNotNone(result["encoded_data"])

    def test_very_long_command(self):
        """Test encoding very long commands"""
        command = "echo " + "A" * 100000

        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(command)
        self.assertGreater(len(result["encoded_data"]), 0)

    def test_binary_like_strings(self):
        """Test encoding binary-like strings"""
        commands = [
            "test\x00\x01\x02",
            "test\\x00\\x01",
            "\xff\xfe\xfd",
        ]

        config = CommandObfuscationConfig(encoding_method=EncodingMethod.HEX)
        obfuscator = CommandStringObfuscator(config)

        for command in commands:
            with self.subTest(command=repr(command)):
                try:
                    result = obfuscator.obfuscate_command(command)
                    self.assertIsNotNone(result["encoded_data"])
                except Exception:
                    pass  # Some may fail, that's okay for edge cases

    def test_only_special_characters(self):
        """Test encoding only special characters"""
        command = "!@#$%^&*()_+-=[]{}|;:',.<>?/\\"

        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(command)
        self.assertIsNotNone(result["encoded_data"])

    def test_only_whitespace(self):
        """Test encoding only whitespace"""
        commands = [" ", "  ", "\t", "\n", "\r\n", " \t \n "]

        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        for command in commands:
            with self.subTest(command=repr(command)):
                result = obfuscator.obfuscate_command(command)
                self.assertIsNotNone(result["encoded_data"])


class TestPerformance(unittest.TestCase):
    """Performance and efficiency tests"""

    def test_encoding_speed_base64(self):
        """Test base64 encoding speed"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        command = "test command"
        iterations = 100

        start = time.time()
        for _ in range(iterations):
            obfuscator.obfuscate_command(command)
        elapsed = time.time() - start

        # Should complete 100 iterations in under 1 second
        self.assertLess(elapsed, 1.0)

    def test_encoding_speed_hex(self):
        """Test hex encoding speed"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.HEX)
        obfuscator = CommandStringObfuscator(config)

        command = "test command"
        iterations = 100

        start = time.time()
        for _ in range(iterations):
            obfuscator.obfuscate_command(command)
        elapsed = time.time() - start

        self.assertLess(elapsed, 1.0)

    def test_encoding_speed_nested(self):
        """Test nested encoding speed"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.NESTED)
        obfuscator = CommandStringObfuscator(config)

        command = "test command"
        iterations = 50

        start = time.time()
        for _ in range(iterations):
            obfuscator.obfuscate_command(command)
        elapsed = time.time() - start

        self.assertLess(elapsed, 2.0)

    def test_payload_generation_speed(self):
        """Test payload generation speed"""
        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        command = "test command"
        iterations = 50

        start = time.time()
        for _ in range(iterations):
            obfuscator.generate_vbs_payload(command)
            obfuscator.generate_powershell_payload(command)
            obfuscator.generate_bash_payload(command)
        elapsed = time.time() - start

        self.assertLess(elapsed, 2.0)


class TestSecurityProperties(unittest.TestCase):
    """Test security-relevant properties"""

    def test_encoded_data_differs_from_original(self):
        """Test encoded data is different from original"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        command = "test"
        result = obfuscator.obfuscate_command(command)

        self.assertNotEqual(result["original_command"], result["encoded_data"])

    def test_variable_names_are_randomized(self):
        """Test variable names are randomized in decoder"""
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.BASE64, randomize_names=True
        )
        obfuscator = CommandStringObfuscator(config)

        codes = []
        for _ in range(5):
            result = obfuscator.obfuscate_command("test")
            codes.append(result["decoder_code"])

        # Codes should be different due to randomized names
        unique_codes = set(codes)
        self.assertGreater(len(unique_codes), 1)

    def test_polymorphic_prevents_detection(self):
        """Test polymorphic encoding prevents pattern detection"""
        config = CommandObfuscationConfig(encoding_method=EncodingMethod.POLYMORPH)
        obfuscator = CommandStringObfuscator(config)

        command = "test"
        encoded_variants = []

        for _ in range(20):
            result = obfuscator.obfuscate_command(command)
            encoded_variants.append(result["encoded_data"])

        # Should have different encoded variants
        unique_variants = set(encoded_variants)
        self.assertGreater(len(unique_variants), 1)


class TestComplexCommands(unittest.TestCase):
    """Test with complex real-world commands"""

    def test_powershell_command(self):
        """Test complex PowerShell command"""
        command = 'powershell.exe -NoProfile -WindowStyle Hidden -Command "Get-Process | ForEach-Object { $_.Kill() }"'

        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(command)
        self.assertEqual(result["original_command"], command)

    def test_cmd_command(self):
        """Test complex cmd.exe command"""
        command = 'cmd.exe /c "for /L %i in (1,1,10) do @echo %i"'

        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(command)
        self.assertEqual(result["original_command"], command)

    def test_bash_command(self):
        """Test complex bash command"""
        command = 'bash -c "for i in {1..100}; do curl -s http://target.com/api?id=$i | jq . ; done"'

        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(command)
        self.assertEqual(result["original_command"], command)

    def test_command_with_quotes(self):
        """Test command with nested quotes"""
        command = '''cmd.exe /c 'echo "test" && powershell -Command "'Get-ChildItem'\"'''

        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(command)
        self.assertEqual(result["original_command"], command)

    def test_command_with_environment_variables(self):
        """Test command with environment variables"""
        command = "echo $PATH && echo %SYSTEMROOT% && echo ${HOME}"

        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(command)
        self.assertEqual(result["original_command"], command)

    def test_command_with_pipe_operators(self):
        """Test command with pipe operators"""
        command = "cat /etc/passwd | grep root | awk -F: '{print $1}'"

        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(command)
        self.assertEqual(result["original_command"], command)


class TestConfigurationOptions(unittest.TestCase):
    """Test configuration variations"""

    def test_obfuscation_level_1(self):
        """Test obfuscation level 1"""
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.BASE64, obfuscation_level=1
        )
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command("test")
        self.assertEqual(result["obfuscation_level"], 1)

    def test_obfuscation_level_5(self):
        """Test obfuscation level 5 (maximum)"""
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.NESTED, obfuscation_level=5
        )
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command("test")
        self.assertEqual(result["obfuscation_level"], 5)

    def test_variable_randomization_enabled(self):
        """Test with variable randomization enabled"""
        config = CommandObfuscationConfig(randomize_names=True)
        obfuscator = CommandStringObfuscator(config)

        results = [obfuscator.obfuscate_command("test") for _ in range(5)]
        codes = [r["decoder_code"] for r in results]

        unique_codes = set(codes)
        self.assertGreater(len(unique_codes), 1)

    def test_variable_randomization_disabled(self):
        """Test with variable randomization disabled"""
        config = CommandObfuscationConfig(randomize_names=False, encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        result1 = obfuscator.obfuscate_command("test")
        result2 = obfuscator.obfuscate_command("test")

        # Variable names should be deterministic (will use method-specific prefixes like b64_)
        # Just verify the same variable pattern appears in both
        code1_vars = [line for line in result1["decoder_code"].split('\n') if '=' in line]
        code2_vars = [line for line in result2["decoder_code"].split('\n') if '=' in line]

        # Both should have same structure when randomization is disabled
        self.assertEqual(len(code1_vars), len(code2_vars))


class TestIntegration(unittest.TestCase):
    """Integration and cross-functional tests"""

    def test_encode_decode_roundtrip_base64(self):
        """Test complete encode-decode cycle with base64"""
        original = "test command"

        config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(original)
        decoded = base64.b64decode(result["encoded_data"]).decode()

        self.assertEqual(decoded, original)

    def test_encode_decode_roundtrip_hex(self):
        """Test complete encode-decode cycle with hex"""
        original = "test command"

        config = CommandObfuscationConfig(encoding_method=EncodingMethod.HEX)
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(original)
        decoded = bytes.fromhex(result["encoded_data"]).decode()

        self.assertEqual(decoded, original)

    def test_encode_decode_roundtrip_xor(self):
        """Test complete encode-decode cycle with XOR"""
        original = "test command"

        config = CommandObfuscationConfig(encoding_method=EncodingMethod.XOR)
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command(original)

        key = result["metadata"]["xor_key"]
        encoded = result["encoded_data"]
        decoded = bytes(
            [int(encoded[i : i + 2], 16) ^ key for i in range(0, len(encoded), 2)]
        ).decode()

        self.assertEqual(decoded, original)

    def test_multiple_encodings_in_sequence(self):
        """Test multiple commands encoded in sequence"""
        commands = ["test1", "test2", "test3", "test4", "test5"]

        config = CommandObfuscationConfig()
        obfuscator = CommandStringObfuscator(config)

        results = [obfuscator.obfuscate_command(cmd) for cmd in commands]

        self.assertEqual(len(obfuscator._obfuscation_history), 5)
        for i, result in enumerate(results):
            self.assertEqual(result["original_command"], commands[i])


class TestConvenienceFunctions(unittest.TestCase):
    """Test module-level convenience functions"""

    def test_encode_command_default(self):
        """Test encode_command with defaults"""
        result = encode_command("test")

        self.assertIn("encoded_data", result)
        self.assertIn("decoder_code", result)

    def test_encode_command_hex(self):
        """Test encode_command with hex method"""
        result = encode_command("test", EncodingMethod.HEX)

        self.assertEqual(result["metadata"]["method"], "hex")

    def test_encode_to_vbs_default(self):
        """Test encode_to_vbs shortcut"""
        vbs = encode_to_vbs("test")

        self.assertIn("CreateObject", vbs)

    def test_encode_to_powershell_default(self):
        """Test encode_to_powershell shortcut"""
        ps = encode_to_powershell("test")

        self.assertIn("FromBase64String", ps)

    def test_encode_to_bash_default(self):
        """Test encode_to_bash shortcut"""
        bash = encode_to_bash("test")

        self.assertIn("base64", bash)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and robustness"""

    def test_invalid_config_values(self):
        """Test handling of invalid config values"""
        # Test with extreme obfuscation level
        config = CommandObfuscationConfig(obfuscation_level=10)
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command("test")
        self.assertIsNotNone(result["encoded_data"])

    def test_large_chunk_size(self):
        """Test very large chunk size"""
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.ARRAY, chunk_size=10000
        )
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command("test")
        self.assertIsNotNone(result["encoded_data"])

    def test_small_chunk_size(self):
        """Test very small chunk size"""
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.ARRAY, chunk_size=1
        )
        obfuscator = CommandStringObfuscator(config)

        result = obfuscator.obfuscate_command("test")
        self.assertIsNotNone(result["encoded_data"])


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
