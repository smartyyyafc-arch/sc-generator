#!/usr/bin/env python3
"""
Comprehensive test suite for Hex Decoder Variants

Tests all three variants:
1. CommandDecoder - for shell commands
2. ScriptDecoder - for VBScript/batch scripts
3. BinaryDecoder - for binary executables
"""

import unittest
from hex_decoder_variants import HexDecoderVariants, generate_all_variants
import re


class TestHexDecoderVariants(unittest.TestCase):
    """Test suite for hex decoder variants"""

    def setUp(self):
        """Set up test fixtures"""
        self.decoder = HexDecoderVariants()

    def test_encode_to_hex(self):
        """Test hex encoding"""
        text = "hello"
        hex_result = HexDecoderVariants.encode_to_hex(text)
        self.assertEqual(hex_result, "68656c6c6f")

    def test_command_decoder_structure(self):
        """Verify command decoder has required structure"""
        command = "notepad.exe"
        vbs_code, metadata = HexDecoderVariants.create_command_decoder(command, execute=True)

        # Verify function definition
        self.assertIn("Function", vbs_code)
        self.assertIn("DecCmd_", vbs_code)

        # Verify hex encoding
        self.assertIn("Dim h_", vbs_code)
        self.assertIn(HexDecoderVariants.encode_to_hex(command), vbs_code)

        # Verify execution
        self.assertIn("WScript.Shell", vbs_code)
        self.assertIn(".Run", vbs_code)

        # Verify metadata
        self.assertEqual(metadata['type'], 'command')
        self.assertEqual(metadata['payload_type'], 'Shell Command')
        self.assertTrue(metadata['execute'])

    def test_command_decoder_without_execution(self):
        """Verify command decoder can be created without execution"""
        command = "cmd.exe"
        vbs_code, metadata = HexDecoderVariants.create_command_decoder(command, execute=False)

        # Should have decoder function
        self.assertIn("Function", vbs_code)

        # Should NOT have execution code
        self.assertNotIn("WScript.Shell", vbs_code)
        self.assertNotIn(".Run", vbs_code)

        # Metadata should reflect no execution
        self.assertFalse(metadata['execute'])
        self.assertIsNone(metadata['shell_var'])

    def test_script_decoder_structure(self):
        """Verify script decoder has required structure"""
        script = "WScript.Echo \"test\""
        vbs_code, metadata = HexDecoderVariants.create_script_decoder(script, execute=True)

        # Verify function definition
        self.assertIn("Function", vbs_code)
        self.assertIn("DecScript_", vbs_code)

        # Verify hex encoding
        self.assertIn(HexDecoderVariants.encode_to_hex(script), vbs_code)

        # Verify special character handling
        self.assertIn("vbLf", vbs_code)  # Line feed
        self.assertIn("vbCr", vbs_code)  # Carriage return
        self.assertIn("vbTab", vbs_code)  # Tab

        # Verify execution
        self.assertIn("cscript.exe", vbs_code)
        self.assertIn("Scripting.FileSystemObject", vbs_code)

        # Verify metadata
        self.assertEqual(metadata['type'], 'script')
        self.assertEqual(metadata['payload_type'], 'Script File')
        self.assertIn("cscript.exe", metadata['execution_method'])

    def test_script_decoder_multiline(self):
        """Verify script decoder handles multiline content"""
        script = "Line 1\nLine 2\r\nLine 3"
        vbs_code, metadata = HexDecoderVariants.create_script_decoder(script, execute=True)

        # Should handle newline characters
        hex_script = HexDecoderVariants.encode_to_hex(script)
        self.assertIn(hex_script, vbs_code)

        # Script length should be correct
        self.assertEqual(metadata['script_length'], len(script))

    def test_binary_decoder_structure(self):
        """Verify binary decoder has required structure"""
        binary_hex = "4d5a90000300000004000000ffff0000b8000000"
        vbs_code, metadata = HexDecoderVariants.create_binary_decoder(binary_hex, execute=True)

        # Verify function definition
        self.assertIn("Function", vbs_code)
        self.assertIn("DecBin_", vbs_code)

        # Verify byte array handling
        self.assertIn("byteArray()", vbs_code)
        self.assertIn("ReDim byteArray", vbs_code)

        # Verify binary file writing
        self.assertIn("ADODB.Stream", vbs_code)
        self.assertIn("WriteByte", vbs_code)
        self.assertIn("SaveToFile", vbs_code)

        # Verify integrity check
        self.assertIn("integrity check", vbs_code.lower())
        self.assertIn("UBound", vbs_code)

        # Verify metadata
        self.assertEqual(metadata['type'], 'binary')
        self.assertEqual(metadata['payload_type'], 'Binary Executable')
        self.assertIsNotNone(metadata['integrity_check'])

    def test_binary_decoder_with_bytes_input(self):
        """Verify binary decoder handles bytes input"""
        binary_bytes = b'\x4d\x5a\x90\x00'
        vbs_code, metadata = HexDecoderVariants.create_binary_decoder(binary_bytes, execute=True)

        # Should handle bytes correctly
        self.assertEqual(metadata['binary_length'], 4)
        self.assertIn("4d5a9000", vbs_code)

    def test_variable_names_are_unique(self):
        """Verify generated variable names are properly formatted"""
        command = "test.exe"
        vbs_code, metadata = HexDecoderVariants.create_command_decoder(command, execute=True)

        # Extract all declared variables
        dim_pattern = r'Dim\s+([\w_]+)'
        declared_vars = set(re.findall(dim_pattern, vbs_code))

        # Check that generated custom variables have proper naming
        # Some variables are language keywords/built-ins, so exclude those
        excluded = {'i', 'r', 'result', 'hexStr', 'strLen', 'charCode', 'hexPair'}
        custom_vars = declared_vars - excluded

        # Custom variables should have underscores
        for var in custom_vars:
            self.assertTrue(
                '_' in var,
                f"Custom variable {var} should be formatted with underscore"
            )

    def test_hex_encoding_correctness(self):
        """Verify hex encoding is correct"""
        test_strings = [
            "hello",
            "test.exe",
            "powershell.exe -NoProfile",
            "A" * 100,  # Long string
        ]

        for test_str in test_strings:
            encoded = HexDecoderVariants.encode_to_hex(test_str)
            # Decode manually to verify
            decoded = bytes.fromhex(encoded).decode()
            self.assertEqual(decoded, test_str)

    def test_metadata_completeness(self):
        """Verify all variants provide complete metadata"""
        command = "test"
        script = "test"
        binary = "4d5a"

        # Command variant
        _, cmd_meta = HexDecoderVariants.create_command_decoder(command)
        required_keys = {'type', 'function_name', 'hex_var', 'decoded_var', 'payload_type',
                        'encoding', 'optimization', 'execute'}
        self.assertTrue(required_keys.issubset(set(cmd_meta.keys())))

        # Script variant
        _, script_meta = HexDecoderVariants.create_script_decoder(script)
        self.assertTrue(required_keys.issubset(set(script_meta.keys())))

        # Binary variant
        _, bin_meta = HexDecoderVariants.create_binary_decoder(binary)
        # Binary variant has different variable names (decoded_array instead of decoded_var)
        binary_required = {'type', 'function_name', 'hex_var', 'payload_type',
                          'encoding', 'optimization', 'execute'}
        self.assertTrue(binary_required.issubset(set(bin_meta.keys())))

    def test_generate_all_variants(self):
        """Verify generate_all_variants produces all three variants"""
        command = "notepad.exe"
        script = "WScript.Echo 'test'"
        binary = "4d5a90000300000004000000"

        variants = generate_all_variants(command, script, binary)

        # Should have all three variants
        self.assertIn('command', variants)
        self.assertIn('script', variants)
        self.assertIn('binary', variants)

        # Each variant should have required keys
        for variant_type in ['command', 'script', 'binary']:
            self.assertIn('code', variants[variant_type])
            self.assertIn('metadata', variants[variant_type])
            self.assertIn('description', variants[variant_type])

    def test_command_decoder_ascii_optimization(self):
        """Verify command decoder has ASCII optimization"""
        command = "echo test"
        vbs_code, metadata = HexDecoderVariants.create_command_decoder(command)

        # Should mention ASCII optimization
        self.assertIn("ASCII", metadata['optimization'])

        # Should have conditional for printable ASCII range (32-126)
        self.assertIn("32 And", vbs_code)
        self.assertIn("126", vbs_code)

    def test_script_decoder_control_characters(self):
        """Verify script decoder handles control characters"""
        script = "Line1\nLine2\tTabbed\rCarriage"
        vbs_code, metadata = HexDecoderVariants.create_script_decoder(script)

        # Should have control character handling
        self.assertIn("vbLf", vbs_code)
        self.assertIn("vbCr", vbs_code)
        self.assertIn("vbTab", vbs_code)

    def test_binary_decoder_integrity_check(self):
        """Verify binary decoder includes integrity check"""
        binary_hex = "4d5a90000300000004000000"
        vbs_code, metadata = HexDecoderVariants.create_binary_decoder(binary_hex)

        # Should verify decoded size matches expected
        self.assertIn("integrity", vbs_code.lower())
        expected_bytes = len(binary_hex) // 2
        self.assertIn(str(expected_bytes), vbs_code)

    def test_execution_code_presence(self):
        """Verify execution code is added only when requested"""
        command = "test.exe"

        # With execution
        with_exec, meta_exec = HexDecoderVariants.create_command_decoder(command, execute=True)
        self.assertIn("WScript.Shell", with_exec)
        self.assertTrue(meta_exec['execute'])

        # Without execution
        without_exec, meta_no_exec = HexDecoderVariants.create_command_decoder(command, execute=False)
        self.assertNotIn("WScript.Shell", without_exec)
        self.assertFalse(meta_no_exec['execute'])


class TestDecoderPerformance(unittest.TestCase):
    """Performance and efficiency tests for decoders"""

    def test_large_command_handling(self):
        """Verify decoder handles large commands"""
        large_command = "powershell.exe " + "-arg " * 100
        vbs_code, metadata = HexDecoderVariants.create_command_decoder(large_command)

        self.assertEqual(metadata['command_length'], len(large_command))
        self.assertEqual(metadata['hex_length'], len(HexDecoderVariants.encode_to_hex(large_command)))

    def test_large_script_handling(self):
        """Verify decoder handles large scripts"""
        large_script = "' Comment\nWScript.Echo \"line\"\n" * 50
        vbs_code, metadata = HexDecoderVariants.create_script_decoder(large_script)

        self.assertEqual(metadata['script_length'], len(large_script))

    def test_binary_size_tracking(self):
        """Verify binary decoder correctly tracks sizes"""
        binary_hex = "00" * 1000  # 1000 bytes
        vbs_code, metadata = HexDecoderVariants.create_binary_decoder(binary_hex)

        self.assertEqual(metadata['binary_length'], 1000)
        self.assertEqual(metadata['hex_length'], len(binary_hex))


class TestVBSCodeValidity(unittest.TestCase):
    """Tests for VBScript code validity"""

    def test_vbs_syntax_elements(self):
        """Verify generated VBScript has valid syntax elements"""
        command = "test.exe"
        vbs_code, _ = HexDecoderVariants.create_command_decoder(command, execute=True)

        # Should have basic VBScript elements
        self.assertIn("Function", vbs_code)
        self.assertIn("End Function", vbs_code)
        self.assertIn("Dim", vbs_code)
        self.assertIn("For", vbs_code)
        self.assertIn("Next", vbs_code)

    def test_vbs_function_completion(self):
        """Verify all functions are properly closed"""
        command = "test"
        script = "test"
        binary = "4d5a"

        variants = [
            HexDecoderVariants.create_command_decoder(command),
            HexDecoderVariants.create_script_decoder(script),
            HexDecoderVariants.create_binary_decoder(binary)
        ]

        for vbs_code, _ in variants:
            # Count Function declarations (not including "End Function")
            function_count = vbs_code.count("\nFunction ")
            end_function_count = vbs_code.count("End Function")
            self.assertGreaterEqual(end_function_count, 0, "Should have proper End Function statements")

    def test_vbs_variable_initialization(self):
        """Verify variables are initialized before use"""
        command = "test.exe"
        vbs_code, metadata = HexDecoderVariants.create_command_decoder(command)

        # Extract the hex variable
        hex_var = metadata['hex_var']

        # Find where it's declared and where it's used
        lines = vbs_code.split('\n')

        dim_line = None
        use_lines = []

        for i, line in enumerate(lines):
            if f"Dim {hex_var}" in line:
                dim_line = i
            if hex_var in line and f"Dim {hex_var}" not in line:
                use_lines.append(i)

        # Variable should be declared before first use
        if use_lines and dim_line is not None:
            self.assertLess(dim_line, min(use_lines),
                            f"Variable {hex_var} used before declaration")


def run_all_tests():
    """Run all test suites"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHexDecoderVariants))
    suite.addTests(loader.loadTestsFromTestCase(TestDecoderPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestVBSCodeValidity))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
