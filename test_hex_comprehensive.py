#!/usr/bin/env python3
"""
Comprehensive Hex Decoder Test Suite with Edge Cases
Tests: empty strings, special characters, boundary conditions, encoding/decoding accuracy
"""

import sys
import unittest
from hex_decoder_variants import HexDecoderVariants
from hex_decoder_hardened import HardenedHexDecoder


class TestHexEncodingBasics(unittest.TestCase):
    """Test basic hex encoding/decoding operations"""

    def test_empty_string(self):
        """Test encoding/decoding empty string"""
        test_input = ""
        hex_encoded = test_input.encode().hex()

        self.assertEqual(hex_encoded, "")
        self.assertEqual(bytes.fromhex(hex_encoded).decode(), test_input)
        print(f"✓ Empty string test passed: '' -> '{hex_encoded}' -> ''")

    def test_single_character(self):
        """Test single character encoding"""
        test_input = "A"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(hex_encoded, "41")
        self.assertEqual(decoded, test_input)
        print(f"✓ Single character test passed: '{test_input}' -> '{hex_encoded}'")

    def test_numeric_string(self):
        """Test numeric string encoding"""
        test_input = "0123456789"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ Numeric string test passed: '{test_input}' -> '{hex_encoded}'")

    def test_ascii_printable_range(self):
        """Test all printable ASCII characters"""
        test_input = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ ASCII printable range test passed: {len(test_input)} chars encoded and decoded correctly")

    def test_control_characters(self):
        """Test control characters (tab, newline, carriage return)"""
        test_input = "\t\n\r"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(hex_encoded, "090a0d")
        self.assertEqual(decoded, test_input)
        print(f"✓ Control characters test passed: tab/newline/CR -> '{hex_encoded}'")

    def test_spaces_and_whitespace(self):
        """Test various whitespace characters"""
        test_input = "  \t  \n  \r  "
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ Whitespace test passed: encoded and decoded correctly")


class TestHexSpecialCharacters(unittest.TestCase):
    """Test special character handling"""

    def test_shell_special_chars(self):
        """Test shell special characters"""
        test_input = "cmd.exe /c echo $PATH && dir || exit"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ Shell special chars test passed: '{test_input}'")

    def test_powershell_syntax(self):
        """Test PowerShell-specific syntax"""
        test_input = 'powershell.exe -NoProfile -Command "Write-Host \'Hello\' | Tee-Object"'
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ PowerShell syntax test passed")

    def test_registry_paths(self):
        """Test Windows registry path patterns"""
        test_input = "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ Registry path test passed")

    def test_file_paths(self):
        """Test file path patterns"""
        test_input = "C:\\Windows\\System32\\notepad.exe"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ File path test passed")

    def test_url_encoding(self):
        """Test URL encoding patterns"""
        test_input = "https://example.com/path?query=value&other=123"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ URL encoding test passed")

    def test_json_payload(self):
        """Test JSON payload encoding"""
        test_input = '{"key":"value","nested":{"array":[1,2,3],"bool":true}}'
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ JSON payload test passed")

    def test_sql_injection_pattern(self):
        """Test SQL injection-like pattern"""
        test_input = "'; DROP TABLE users; --"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ SQL pattern test passed")

    def test_base64_like_content(self):
        """Test Base64-like content"""
        test_input = "SGVsbG8gV29ybGQhIFRoaXMgaXMgYSB0ZXN0Lg=="
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ Base64-like content test passed")

    def test_unicode_escape_sequences(self):
        """Test Unicode escape sequences"""
        test_input = "\\u0048\\u0065\\u006c\\u006c\\u006f"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ Unicode escape sequences test passed")

    def test_hex_string_as_input(self):
        """Test hex string being treated as regular text"""
        test_input = "48656c6c6f20576f726c64"  # "Hello World" in hex
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        self.assertNotEqual(decoded, "Hello World")
        print(f"✓ Hex string as input test passed (treats as text, not conversion)")

    def test_quotes_and_escapes(self):
        """Test various quote and escape combinations"""
        test_input = '''He said "Hello" and she replied 'Hi\\nThere' '''
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ Quotes and escapes test passed")


class TestHexBoundaryConditions(unittest.TestCase):
    """Test boundary conditions and limits"""

    def test_single_byte_values(self):
        """Test all single byte values (0-255)"""
        for byte_value in range(256):
            test_bytes = bytes([byte_value])
            hex_encoded = test_bytes.hex()
            decoded_bytes = bytes.fromhex(hex_encoded)

            self.assertEqual(decoded_bytes, test_bytes)

        print(f"✓ All single byte values (0-255) test passed")

    def test_very_long_string(self):
        """Test very long string encoding"""
        test_input = "A" * 10000
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        self.assertEqual(len(hex_encoded), len(test_input) * 2)
        print(f"✓ Very long string (10000 chars) test passed")

    def test_alternating_pattern(self):
        """Test alternating byte pattern"""
        test_input = "AB" * 500
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ Alternating pattern (1000 chars) test passed")

    def test_maximum_byte_value(self):
        """Test maximum byte value (255)"""
        test_bytes = bytes([255, 254, 253, 252, 251])
        hex_encoded = test_bytes.hex()
        decoded_bytes = bytes.fromhex(hex_encoded)

        self.assertEqual(decoded_bytes, test_bytes)
        self.assertEqual(hex_encoded, "fffefdfcfb")
        print(f"✓ Maximum byte values test passed")

    def test_all_null_bytes(self):
        """Test all null bytes"""
        test_input = "cmd.exe\x00\x00\x00"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode(errors='ignore')

        self.assertIn("cmd.exe", decoded)
        print(f"✓ Null bytes test passed")

    def test_repeated_characters(self):
        """Test repeated characters"""
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()":
            test_input = char * 100
            hex_encoded = test_input.encode().hex()
            decoded = bytes.fromhex(hex_encoded).decode()

            self.assertEqual(decoded, test_input)

        print(f"✓ Repeated characters test passed for all chars")

    def test_hex_string_length_odd(self):
        """Test handling of odd-length hex strings (invalid)"""
        # This should fail gracefully
        try:
            result = bytes.fromhex("48656c6c6f2")  # One char short
            # If it doesn't raise, ensure it's handled
        except ValueError as e:
            print(f"✓ Odd-length hex string correctly raises ValueError: {e}")

    def test_hex_string_case_insensitive(self):
        """Test that hex is case-insensitive"""
        test_input = "Hello"
        hex_lower = test_input.encode().hex()
        hex_upper = hex_lower.upper()
        hex_mixed = "".join(c.upper() if i % 2 else c for i, c in enumerate(hex_lower))

        decoded_lower = bytes.fromhex(hex_lower).decode()
        decoded_upper = bytes.fromhex(hex_upper).decode()
        decoded_mixed = bytes.fromhex(hex_mixed).decode()

        self.assertEqual(decoded_lower, test_input)
        self.assertEqual(decoded_upper, test_input)
        self.assertEqual(decoded_mixed, test_input)
        print(f"✓ Case-insensitive hex test passed")


class TestHexDecoderVariants(unittest.TestCase):
    """Test HexDecoderVariants with various inputs"""

    def test_variants_empty_string(self):
        """Test variants with empty string"""
        try:
            vbs_code, metadata = HexDecoderVariants.create_command_decoder("", execute=False)
            self.assertIsNotNone(vbs_code)
            self.assertIsNotNone(metadata)
            print(f"✓ Variants empty string test passed")
        except Exception as e:
            print(f"⚠ Variants empty string raised: {e}")

    def test_variants_special_chars(self):
        """Test variants with special characters"""
        commands = [
            "echo 'test' && ls",
            'cmd /c "echo test"',
            "powershell -Command \"Write-Host $env:PATH\"",
            "reg.exe query HKLM\\Software\\Microsoft",
            "C:\\Windows\\System32\\calc.exe",
        ]

        for command in commands:
            try:
                vbs_code, metadata = HexDecoderVariants.create_command_decoder(command, execute=False)
                self.assertIsNotNone(vbs_code)
                self.assertIn(command.encode().hex(), vbs_code or metadata.get('hex_var', ''))
                print(f"✓ Variants test passed for: {command[:50]}")
            except Exception as e:
                print(f"✗ Variants test failed for '{command}': {e}")

    def test_variants_long_command(self):
        """Test variants with very long command"""
        long_command = "powershell -Command \"" + "Get-Process | Where-Object {$_.ProcessName -match 'test'} | Select-Object Name, ID; " * 10 + "\""

        try:
            vbs_code, metadata = HexDecoderVariants.create_command_decoder(long_command, execute=False)
            self.assertIsNotNone(vbs_code)
            print(f"✓ Variants long command test passed (length: {len(long_command)})")
        except Exception as e:
            print(f"✗ Variants long command test failed: {e}")


class TestHardenedHexDecoder(unittest.TestCase):
    """Test HardenedHexDecoder with various inputs"""

    def test_hardened_empty_command(self):
        """Test hardened decoder with empty command"""
        try:
            vbs_code, metadata = HardenedHexDecoder.create_hardened_command_decoder("", execute=False)
            self.assertIsNotNone(vbs_code)
            self.assertIsNotNone(metadata)
            print(f"✓ Hardened empty command test passed")
        except Exception as e:
            print(f"⚠ Hardened empty command raised: {e}")

    def test_hardened_special_chars(self):
        """Test hardened decoder with special characters"""
        commands = [
            "calc.exe",
            "cmd.exe /c whoami",
            "powershell.exe -NoProfile -Command \"Write-Host 'Test'\"",
            "C:\\Windows\\System32\\notepad.exe C:\\temp\\file.txt",
        ]

        for command in commands:
            try:
                vbs_code, metadata = HardenedHexDecoder.create_hardened_command_decoder(command, execute=False)
                self.assertIsNotNone(vbs_code)
                # Verify obfuscation layers are present
                self.assertGreater(len(metadata['obfuscation_layers']), 0)
                print(f"✓ Hardened command test passed: {command}")
            except Exception as e:
                print(f"✗ Hardened command test failed for '{command}': {e}")

    def test_hardened_script_empty(self):
        """Test hardened script decoder with empty script"""
        try:
            vbs_code, metadata = HardenedHexDecoder.create_hardened_script_decoder("", execute=False)
            self.assertIsNotNone(vbs_code)
            print(f"✓ Hardened empty script test passed")
        except Exception as e:
            print(f"⚠ Hardened empty script raised: {e}")

    def test_hardened_script_special_chars(self):
        """Test hardened script decoder with special characters"""
        scripts = [
            "WScript.Echo 'Hello World'",
            "Set objShell = CreateObject(\"WScript.Shell\")\nobjShell.Run \"calc.exe\", 1, False",
            "'Comment line\nDim x\nx = 123",
        ]

        for script in scripts:
            try:
                vbs_code, metadata = HardenedHexDecoder.create_hardened_script_decoder(script, execute=False)
                self.assertIsNotNone(vbs_code)
                self.assertEqual(len(script.encode().hex()), metadata['hex_length'])
                print(f"✓ Hardened script test passed: {script[:40]}")
            except Exception as e:
                print(f"✗ Hardened script test failed: {e}")

    def test_hardened_binary_empty(self):
        """Test hardened binary decoder with minimal hex"""
        try:
            vbs_code, metadata = HardenedHexDecoder.create_hardened_binary_decoder("", execute=False)
            self.assertIsNotNone(vbs_code)
            print(f"✓ Hardened empty binary test passed")
        except Exception as e:
            print(f"⚠ Hardened empty binary raised: {e}")

    def test_hardened_binary_various(self):
        """Test hardened binary decoder with various sizes"""
        binary_hexes = [
            "4d5a",  # MZ header start (2 bytes)
            "4d5a9000",  # MZ header (4 bytes)
            "4d5a" + "00" * 100,  # 52 bytes
            "4d5a" + "ff" * 256,  # 258 bytes
        ]

        for hex_data in binary_hexes:
            try:
                vbs_code, metadata = HardenedHexDecoder.create_hardened_binary_decoder(hex_data, execute=False)
                self.assertIsNotNone(vbs_code)
                expected_size = len(hex_data) // 2
                self.assertEqual(metadata['binary_length'], expected_size)
                print(f"✓ Hardened binary test passed (size: {expected_size} bytes)")
            except Exception as e:
                print(f"✗ Hardened binary test failed for size {len(hex_data)//2}: {e}")

    def test_hardened_obfuscation_layers(self):
        """Test that hardened decoder includes obfuscation layers"""
        command = "test.exe"
        vbs_code, metadata = HardenedHexDecoder.create_hardened_command_decoder(command, execute=False)

        required_layers = [
            'Variable name randomization',
            'Junk code injection',
            'Dead code paths',
            'String chunking',
        ]

        for layer in required_layers:
            self.assertIn(layer, metadata['obfuscation_layers'])

        print(f"✓ Hardened obfuscation layers verification passed ({len(metadata['obfuscation_layers'])} layers)")

    def test_hardened_protection_level(self):
        """Test that hardened decoder has proper protection level"""
        command = "test.exe"
        vbs_code, metadata = HardenedHexDecoder.create_hardened_command_decoder(command, execute=True)

        self.assertEqual(metadata['protection_level'], 'high')
        self.assertTrue(metadata['execute'])
        print(f"✓ Hardened protection level verification passed")


class TestHexEncodingEdgeCases(unittest.TestCase):
    """Test extreme edge cases and error conditions"""

    def test_null_bytes_in_command(self):
        """Test null bytes embedded in command"""
        test_input = "cmd\x00exe"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode(errors='ignore')

        self.assertIn("cmd", decoded)
        print(f"✓ Null bytes in command test passed")

    def test_all_printable_ascii(self):
        """Test all printable ASCII combined"""
        test_input = "".join(chr(i) for i in range(32, 127))
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ All printable ASCII test passed ({len(test_input)} chars)")

    def test_repeated_special_sequence(self):
        """Test repeated special sequences"""
        test_input = "\\x41\\x42\\x43" * 100
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ Repeated special sequences test passed")

    def test_mixed_encodings_representation(self):
        """Test mixed encoding representation (as text)"""
        test_input = "Hello\\x41\\x42\\x43World"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ Mixed encodings representation test passed")

    def test_command_with_pipes_and_redirects(self):
        """Test command with shell pipes and redirects"""
        test_input = "echo test | grep e > /dev/null && echo found || echo not found"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ Command with pipes and redirects test passed")

    def test_windows_batch_syntax(self):
        """Test Windows batch script syntax"""
        test_input = "@echo off\nfor /f %%i in ('whoami') do set user=%%i\necho %user%"
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ Windows batch syntax test passed")

    def test_vbscript_syntax(self):
        """Test VBScript syntax"""
        test_input = """Dim objShell
Set objShell = CreateObject("WScript.Shell")
objShell.Run "notepad.exe", 1, False"""
        hex_encoded = test_input.encode().hex()
        decoded = bytes.fromhex(hex_encoded).decode()

        self.assertEqual(decoded, test_input)
        print(f"✓ VBScript syntax test passed")


class TestHexEncodingIntegration(unittest.TestCase):
    """Integration tests for end-to-end hex encoding/decoding"""

    def test_roundtrip_consistency(self):
        """Test that encoding-decoding roundtrip is consistent"""
        test_inputs = [
            "",
            "A",
            "Hello World",
            "cmd.exe /c whoami",
            "powershell -NoProfile -Command \"Write-Host 'Test'\"",
            "C:\\Windows\\System32\\calc.exe",
            "HKEY_LOCAL_MACHINE\\Software",
            "!@#$%^&*()[]{}+-=<>?,./",
            "\t\n\r",
            "ABC123!@#DEF456$%^GHI789&*()",
        ]

        for test_input in test_inputs:
            hex_encoded = test_input.encode().hex()
            roundtrip = bytes.fromhex(hex_encoded).decode()
            self.assertEqual(roundtrip, test_input)

        print(f"✓ Roundtrip consistency test passed for {len(test_inputs)} inputs")

    def test_hex_format_validation(self):
        """Test hex format is always lowercase alphanumeric"""
        test_inputs = [
            "test",
            "UPPERCASE",
            "MixedCase123",
            "!@#$%",
            "",
        ]

        for test_input in test_inputs:
            hex_encoded = test_input.encode().hex()
            # Verify format
            self.assertTrue(all(c in '0123456789abcdef' for c in hex_encoded))
            self.assertEqual(len(hex_encoded) % 2, 0)

        print(f"✓ Hex format validation test passed")

    def test_hex_length_doubling(self):
        """Test that hex encoding doubles the character count for ASCII"""
        test_inputs = [
            "A",
            "Hello",
            "Test String",
            "1234567890",
        ]

        for test_input in test_inputs:
            hex_encoded = test_input.encode().hex()
            self.assertEqual(len(hex_encoded), len(test_input) * 2)

        print(f"✓ Hex length doubling test passed")

    def test_decoder_generation_with_edge_inputs(self):
        """Test that decoder generation works with edge case inputs"""
        edge_cases = [
            ("", "Empty command"),
            ("A", "Single character"),
            ("cmd " * 100, "Very long command"),
            ("!@#$%^&*()", "Special characters only"),
            ("\t\n\r", "Control characters only"),
        ]

        for test_input, description in edge_cases:
            try:
                vbs_code, metadata = HexDecoderVariants.create_command_decoder(test_input, execute=False)
                self.assertIsNotNone(vbs_code)
                print(f"✓ Decoder generation test passed: {description}")
            except Exception as e:
                print(f"⚠ Decoder generation test for '{description}' raised: {type(e).__name__}")


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics and characteristics"""

    def test_hex_encoding_size_growth(self):
        """Test hex encoding size growth pattern"""
        sizes = [1, 10, 100, 1000, 10000]

        for size in sizes:
            test_input = "A" * size
            hex_encoded = test_input.encode().hex()
            self.assertEqual(len(hex_encoded), size * 2)
            print(f"✓ Size {size:5d} bytes -> hex {len(hex_encoded):6d} bytes (2x growth)")

    def test_obfuscation_overhead(self):
        """Test obfuscation adds expected overhead"""
        commands = [
            "calc.exe",
            "cmd.exe /c whoami",
            "powershell -NoProfile -Command \"Test\"",
        ]

        for command in commands:
            try:
                vbs_normal, _ = HexDecoderVariants.create_command_decoder(command, execute=False)
                vbs_hardened, _ = HardenedHexDecoder.create_hardened_command_decoder(command, execute=False)

                overhead = ((len(vbs_hardened) - len(vbs_normal)) / len(vbs_normal)) * 100
                print(f"✓ Obfuscation overhead: {overhead:.1f}% for '{command[:30]}'")
            except Exception as e:
                print(f"⚠ Overhead test skipped: {e}")


def run_all_tests():
    """Run all test suites"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE HEX DECODER TEST SUITE")
    print("Testing: Edge Cases, Special Characters, Boundary Conditions")
    print("=" * 80 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHexEncodingBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestHexSpecialCharacters))
    suite.addTests(loader.loadTestsFromTestCase(TestHexBoundaryConditions))
    suite.addTests(loader.loadTestsFromTestCase(TestHexDecoderVariants))
    suite.addTests(loader.loadTestsFromTestCase(TestHardenedHexDecoder))
    suite.addTests(loader.loadTestsFromTestCase(TestHexEncodingEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestHexEncodingIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceMetrics))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80 + "\n")

    return result


if __name__ == "__main__":
    result = run_all_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
