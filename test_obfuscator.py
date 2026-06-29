#!/usr/bin/env python3

"""
Test suite for command obfuscation utility
"""

import unittest
import sys
from obfuscator import CommandObfuscator


class TestHexEncoding(unittest.TestCase):
    """Test hex encoding/decoding"""

    def setUp(self):
        self.obf = CommandObfuscator()

    def test_hex_encode_simple(self):
        """Test simple hex encoding"""
        result = self.obf.hex_encode("hello")
        self.assertEqual(result, "68656c6c6f")

    def test_hex_decode_simple(self):
        """Test simple hex decoding"""
        result = self.obf.hex_decode("68656c6c6f")
        self.assertEqual(result, "hello")

    def test_hex_roundtrip(self):
        """Test hex encode/decode roundtrip"""
        original = "ls -la /tmp"
        encoded = self.obf.hex_encode(original)
        decoded = self.obf.hex_decode(encoded)
        self.assertEqual(original, decoded)

    def test_hex_with_spaces(self):
        """Test hex with spaces"""
        original = "echo hello world"
        encoded = self.obf.hex_encode(original)
        decoded = self.obf.hex_decode(encoded)
        self.assertEqual(original, decoded)

    def test_hex_with_special_chars(self):
        """Test hex with special characters"""
        original = "grep -i 'pattern' /etc/passwd"
        encoded = self.obf.hex_encode(original)
        decoded = self.obf.hex_decode(encoded)
        self.assertEqual(original, decoded)


class TestBase64Encoding(unittest.TestCase):
    """Test base64 encoding/decoding"""

    def setUp(self):
        self.obf = CommandObfuscator()

    def test_b64_encode_simple(self):
        """Test simple base64 encoding"""
        result = self.obf.b64_encode("hello")
        self.assertEqual(result, "aGVsbG8=")

    def test_b64_decode_simple(self):
        """Test simple base64 decoding"""
        result = self.obf.b64_decode("aGVsbG8=")
        self.assertEqual(result, "hello")

    def test_b64_roundtrip(self):
        """Test base64 encode/decode roundtrip"""
        original = "whoami"
        encoded = self.obf.b64_encode(original)
        decoded = self.obf.b64_decode(encoded)
        self.assertEqual(original, decoded)

    def test_b64_with_spaces(self):
        """Test base64 with spaces"""
        original = "cat /etc/passwd"
        encoded = self.obf.b64_encode(original)
        decoded = self.obf.b64_decode(encoded)
        self.assertEqual(original, decoded)


class TestROT13(unittest.TestCase):
    """Test ROT13 encoding"""

    def setUp(self):
        self.obf = CommandObfuscator()

    def test_rot13_simple(self):
        """Test simple ROT13"""
        original = "hello"
        encoded = self.obf.rot13(original)
        decoded = self.obf.rot13(encoded)
        self.assertEqual(original, decoded)

    def test_rot13_uppercase(self):
        """Test ROT13 with uppercase"""
        original = "HELLO"
        encoded = self.obf.rot13(original)
        decoded = self.obf.rot13(encoded)
        self.assertEqual(original, decoded)

    def test_rot13_mixed(self):
        """Test ROT13 with mixed case"""
        original = "Hello World"
        encoded = self.obf.rot13(original)
        decoded = self.obf.rot13(encoded)
        self.assertEqual(original, decoded)

    def test_rot13_preserves_numbers(self):
        """Test that ROT13 preserves numbers"""
        original = "hello123"
        encoded = self.obf.rot13(original)
        self.assertIn("123", encoded)


class TestReverseEncoding(unittest.TestCase):
    """Test reverse string encoding"""

    def setUp(self):
        self.obf = CommandObfuscator()

    def test_reverse_simple(self):
        """Test simple reverse"""
        original = "hello"
        reversed_str = self.obf.reverse(original)
        self.assertEqual(reversed_str, "olleh")

    def test_reverse_roundtrip(self):
        """Test reverse roundtrip"""
        original = "ls -la /tmp"
        reversed_str = self.obf.reverse(original)
        restored = self.obf.reverse(reversed_str)
        self.assertEqual(original, restored)


class TestCaesarCipher(unittest.TestCase):
    """Test Caesar cipher"""

    def setUp(self):
        self.obf = CommandObfuscator()

    def test_caesar_encode_simple(self):
        """Test simple Caesar cipher"""
        original = "hello"
        encoded = self.obf.caesar_cipher(original, 3)
        self.assertEqual(encoded, "khoor")

    def test_caesar_roundtrip(self):
        """Test Caesar cipher roundtrip"""
        original = "secret message"
        shift = 5
        encoded = self.obf.caesar_cipher(original, shift)
        decoded = self.obf.caesar_decipher(encoded, shift)
        self.assertEqual(original, decoded)

    def test_caesar_preserves_non_alpha(self):
        """Test that Caesar preserves non-alphabetic characters"""
        original = "hello-123"
        encoded = self.obf.caesar_cipher(original, 3)
        self.assertIn("-123", encoded)


class TestMultiLayer(unittest.TestCase):
    """Test multi-layer encoding"""

    def setUp(self):
        self.obf = CommandObfuscator()

    def test_multi_layer_2(self):
        """Test 2-layer encoding"""
        original = "secret"
        encoded = self.obf.multi_layer_encode(original, layers=2)
        decoded = self.obf.multi_layer_decode(encoded, layers=2)
        self.assertEqual(original, decoded)

    def test_multi_layer_3(self):
        """Test 3-layer encoding"""
        original = "sensitive data"
        encoded = self.obf.multi_layer_encode(original, layers=3)
        decoded = self.obf.multi_layer_decode(encoded, layers=3)
        self.assertEqual(original, decoded)

    def test_multi_layer_command(self):
        """Test multi-layer with complex command"""
        original = "grep -r 'password' /etc/"
        encoded = self.obf.multi_layer_encode(original, layers=3)
        decoded = self.obf.multi_layer_decode(encoded, layers=3)
        self.assertEqual(original, decoded)


class TestHashVerification(unittest.TestCase):
    """Test hash verification"""

    def setUp(self):
        self.obf = CommandObfuscator()

    def test_hash_verification_valid(self):
        """Test valid hash verification"""
        command = "secret command"
        encoded, cmd_hash = self.obf.obfuscate_with_hash(command)
        verified = self.obf.verify_obfuscated(encoded, cmd_hash)
        self.assertTrue(verified)

    def test_hash_verification_invalid(self):
        """Test invalid hash verification"""
        command = "secret command"
        encoded, cmd_hash = self.obf.obfuscate_with_hash(command)
        wrong_hash = "0" * 64
        verified = self.obf.verify_obfuscated(encoded, wrong_hash)
        self.assertFalse(verified)

    def test_hash_different_for_different_commands(self):
        """Test different commands produce different hashes"""
        _, hash1 = self.obf.obfuscate_with_hash("command1")
        _, hash2 = self.obf.obfuscate_with_hash("command2")
        self.assertNotEqual(hash1, hash2)


class TestCharacterSubstitution(unittest.TestCase):
    """Test character substitution"""

    def setUp(self):
        self.obf = CommandObfuscator()

    def test_character_sub_simple(self):
        """Test simple character substitution"""
        original = "hello"
        encoded = self.obf.character_substitution(original)
        # e->3, l->1, o->0
        self.assertIn("3", encoded)  # e->3
        self.assertIn("1", encoded)  # l->1
        self.assertIn("0", encoded)  # o->0

    def test_character_sub_preserves_unknown_chars(self):
        """Test substitution preserves unknown characters"""
        original = "test-123"
        encoded = self.obf.character_substitution(original)
        self.assertIn("-", encoded)
        self.assertIn("123", encoded)


class TestXOREncoding(unittest.TestCase):
    """Test XOR encoding"""

    def setUp(self):
        self.obf = CommandObfuscator()

    def test_xor_roundtrip(self):
        """Test XOR encode/decode roundtrip"""
        original = "secret message"
        key = "mykey"
        encoded = self.obf.xor_encode(original, key)
        decoded = self.obf.xor_decode(encoded, key)
        self.assertEqual(original, decoded)

    def test_xor_different_keys(self):
        """Test XOR with different keys produces different output"""
        original = "test"
        encoded1 = self.obf.xor_encode(original, "key1")
        encoded2 = self.obf.xor_encode(original, "key2")
        self.assertNotEqual(encoded1, encoded2)

    def test_xor_wrong_key_fails(self):
        """Test XOR with wrong key produces wrong output"""
        original = "test"
        encoded = self.obf.xor_encode(original, "key1")
        decoded = self.obf.xor_decode(encoded, "wrongkey")
        self.assertNotEqual(original, decoded)


class TestEnvironmentVariables(unittest.TestCase):
    """Test environment variable concatenation"""

    def setUp(self):
        self.obf = CommandObfuscator()

    def test_env_var_basic(self):
        """Test basic environment variable"""
        import os
        os.environ['TEST_VAR'] = 'testvalue'
        result = self.obf.env_var_concat("$TEST_VAR", "other")
        self.assertIn("testvalue", result)

    def test_env_var_nonexistent(self):
        """Test nonexistent environment variable"""
        result = self.obf.env_var_concat("$NONEXISTENT_VAR_12345", "other")
        self.assertIn("$NONEXISTENT_VAR_12345", result)

    def test_dynamic_command_builder(self):
        """Test dynamic command builder"""
        result = self.obf.dynamic_command_builder("$CMD_ECHO", "hello")
        self.assertIn("echo", result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases"""

    def setUp(self):
        self.obf = CommandObfuscator()

    def test_empty_string(self):
        """Test empty string"""
        original = ""
        encoded = self.obf.hex_encode(original)
        decoded = self.obf.hex_decode(encoded)
        self.assertEqual(original, decoded)

    def test_unicode_characters(self):
        """Test unicode characters"""
        original = "hello 你好 мир"
        encoded = self.obf.hex_encode(original)
        decoded = self.obf.hex_decode(encoded)
        self.assertEqual(original, decoded)

    def test_very_long_command(self):
        """Test very long command"""
        original = "ls " + "-la " * 100 + "/tmp"
        encoded = self.obf.b64_encode(original)
        decoded = self.obf.b64_decode(encoded)
        self.assertEqual(original, decoded)

    def test_special_bash_characters(self):
        """Test special bash characters"""
        original = "echo $VAR | grep 'pattern' && echo done"
        encoded = self.obf.hex_encode(original)
        decoded = self.obf.hex_decode(encoded)
        self.assertEqual(original, decoded)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHexEncoding))
    suite.addTests(loader.loadTestsFromTestCase(TestBase64Encoding))
    suite.addTests(loader.loadTestsFromTestCase(TestROT13))
    suite.addTests(loader.loadTestsFromTestCase(TestReverseEncoding))
    suite.addTests(loader.loadTestsFromTestCase(TestCaesarCipher))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestHashVerification))
    suite.addTests(loader.loadTestsFromTestCase(TestCharacterSubstitution))
    suite.addTests(loader.loadTestsFromTestCase(TestXOREncoding))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvironmentVariables))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
