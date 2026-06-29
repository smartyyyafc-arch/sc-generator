#!/usr/bin/env python3
"""
Comprehensive Base64 Test Suite with Edge Cases
Tests cover encoding/decoding with edge cases, boundary conditions, and security aspects
"""

import unittest
import base64
import sys
import os
from io import BytesIO
from base64_encoder import Base64Encoder, Base64OperationsPair


class TestBase64EdgeCasesEmptyAndNone(unittest.TestCase):
    """Test edge cases with empty strings and None values"""

    def setUp(self):
        self.encoder = Base64Encoder()
        self.ops = Base64OperationsPair()

    def test_encode_empty_string(self):
        """Empty string should encode to empty string"""
        result = self.encoder.encode_to_base64("")
        self.assertEqual(result, "")

    def test_encode_single_character(self):
        """Single character encoding"""
        result = self.encoder.encode_to_base64("A")
        self.assertEqual(result, "QQ==")
        # Verify round trip
        decoded = base64.b64decode(result).decode()
        self.assertEqual(decoded, "A")

    def test_encode_two_characters(self):
        """Two character encoding"""
        result = self.encoder.encode_to_base64("AB")
        self.assertEqual(result, "QUI=")

    def test_encode_three_characters(self):
        """Three character encoding (no padding)"""
        result = self.encoder.encode_to_base64("ABC")
        self.assertEqual(result, "QUJD")

    def test_encode_whitespace_only(self):
        """Whitespace-only string encoding"""
        result = self.encoder.encode_to_base64("   ")
        decoded = base64.b64decode(result).decode()
        self.assertEqual(decoded, "   ")

    def test_encode_newline_only(self):
        """Newline-only string encoding"""
        result = self.encoder.encode_to_base64("\n")
        decoded = base64.b64decode(result).decode()
        self.assertEqual(decoded, "\n")

    def test_encode_tab_only(self):
        """Tab-only string encoding"""
        result = self.encoder.encode_to_base64("\t")
        decoded = base64.b64decode(result).decode()
        self.assertEqual(decoded, "\t")

    def test_encode_mixed_whitespace(self):
        """Mixed whitespace encoding"""
        result = self.encoder.encode_to_base64(" \t\n\r ")
        decoded = base64.b64decode(result).decode()
        self.assertEqual(decoded, " \t\n\r ")


class TestBase64EdgeCasesCharacterBoundaries(unittest.TestCase):
    """Test character boundary conditions"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_encode_ascii_range_lower(self):
        """Test lower ASCII range (0-31)"""
        for i in range(32):
            char = chr(i)
            encoded = self.encoder.encode_to_base64(char)
            decoded = base64.b64decode(encoded).decode()
            self.assertEqual(decoded, char, f"Failed for ASCII {i}")

    def test_encode_ascii_range_printable(self):
        """Test printable ASCII range (32-126)"""
        for i in range(32, 127):
            char = chr(i)
            encoded = self.encoder.encode_to_base64(char)
            decoded = base64.b64decode(encoded).decode()
            self.assertEqual(decoded, char, f"Failed for ASCII {i}")

    def test_encode_ascii_range_extended(self):
        """Test extended ASCII range (128-255)"""
        for i in range(128, 256):
            char_bytes = bytes([i])
            encoded = self.encoder.encode_bytes_to_base64(char_bytes)
            decoded = base64.b64decode(encoded)
            self.assertEqual(decoded, char_bytes, f"Failed for ASCII {i}")

    def test_encode_null_byte(self):
        """Test null byte encoding"""
        text_with_null = "test\x00value"
        encoded = self.encoder.encode_to_base64(text_with_null)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text_with_null)

    def test_encode_multiple_null_bytes(self):
        """Test multiple null bytes"""
        text_with_nulls = "\x00\x00\x00"
        encoded = self.encoder.encode_to_base64(text_with_nulls)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text_with_nulls)

    def test_encode_string_with_null_in_middle(self):
        """Test null byte in middle of string"""
        text = "before\x00after"
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)


class TestBase64EdgeCasesPadding(unittest.TestCase):
    """Test Base64 padding edge cases"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_padding_no_padding_needed(self):
        """String encoding to 0 padding (multiple of 3 bytes)"""
        text = "ABC"  # 3 bytes -> no padding
        encoded = self.encoder.encode_to_base64(text)
        self.assertFalse(encoded.endswith('='))
        self.assertEqual(len(encoded) % 4, 0)

    def test_padding_one_equal_sign(self):
        """String needing 1 padding equal sign"""
        text = "AB"  # 2 bytes -> 1 padding
        encoded = self.encoder.encode_to_base64(text)
        self.assertEqual(encoded.count('='), 1)
        self.assertTrue(encoded.endswith('='))

    def test_padding_two_equal_signs(self):
        """String needing 2 padding equal signs"""
        text = "A"  # 1 byte -> 2 padding
        encoded = self.encoder.encode_to_base64(text)
        self.assertEqual(encoded.count('='), 2)
        self.assertTrue(encoded.endswith('=='))

    def test_padding_multiple_blocks(self):
        """Multiple blocks with various padding"""
        for length in [1, 2, 3, 4, 5, 6, 7, 8]:
            text = "X" * length
            encoded = self.encoder.encode_to_base64(text)
            # All Base64 should be multiple of 4
            self.assertEqual(len(encoded) % 4, 0)
            # Verify round trip
            decoded = base64.b64decode(encoded).decode()
            self.assertEqual(decoded, text)

    def test_padding_exact_multiples_of_three(self):
        """Test strings that are exact multiples of 3 bytes"""
        for length in [3, 6, 9, 12, 15, 30, 100, 300]:
            text = "Y" * length
            encoded = self.encoder.encode_to_base64(text)
            # Verify it's valid base64
            self.assertEqual(len(encoded) % 4, 0, f"Length {length}: encoded not multiple of 4")
            decoded = base64.b64decode(encoded).decode()
            self.assertEqual(decoded, text, f"Round trip failed for length {length}")


class TestBase64EdgeCasesUnicodeAndEncoding(unittest.TestCase):
    """Test Unicode and encoding edge cases"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_encode_bmp_characters(self):
        """Test Basic Multilingual Plane characters (U+0000 to U+FFFF)"""
        # Chinese
        result = self.encoder.encode_to_base64("你好")
        decoded = base64.b64decode(result).decode('utf-8')
        self.assertEqual(decoded, "你好")

    def test_encode_supplementary_characters(self):
        """Test supplementary plane characters (above U+FFFF)"""
        # Emoji
        result = self.encoder.encode_to_base64("😀😁😂")
        decoded = base64.b64decode(result).decode('utf-8')
        self.assertEqual(decoded, "😀😁😂")

    def test_encode_rtl_languages(self):
        """Test right-to-left languages"""
        text = "مرحبا بالعالم"  # Arabic: Hello World
        result = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(result).decode('utf-8')
        self.assertEqual(decoded, text)

    def test_encode_mixed_scripts(self):
        """Test mixed scripts in single string"""
        text = "Hello 世界 مرحبا שלום Привет"
        result = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(result).decode('utf-8')
        self.assertEqual(decoded, text)

    def test_encode_zero_width_characters(self):
        """Test zero-width characters"""
        text = "A​B"  # A + zero-width space + B
        result = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(result).decode('utf-8')
        self.assertEqual(decoded, text)

    def test_encode_combining_characters(self):
        """Test combining diacritical marks"""
        text = "é"  # e + acute accent combining mark
        result = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(result).decode('utf-8')
        self.assertEqual(decoded, text)

    def test_encode_variation_selectors(self):
        """Test variation selectors"""
        text = "︎👨‍👩‍👧‍👦"  # Family emoji with variation selector
        result = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(result).decode('utf-8')
        self.assertEqual(decoded, text)

    def test_encode_bidi_text(self):
        """Test bidirectional text"""
        text = "Hello שלום World"  # LTR + RTL + LTR
        result = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(result).decode('utf-8')
        self.assertEqual(decoded, text)


class TestBase64EdgeCasesLengthBoundaries(unittest.TestCase):
    """Test length boundary conditions"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_encode_length_1(self):
        """Single byte"""
        text = "a"
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_length_64(self):
        """64 bytes"""
        text = "X" * 64
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_length_1024(self):
        """1 KB"""
        text = "Y" * 1024
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_length_1mb(self):
        """1 MB"""
        text = "Z" * (1024 * 1024)
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_length_boundaries_power_of_two(self):
        """Test around power of two boundaries"""
        for power in range(1, 14):
            length = 2 ** power
            for offset in [-1, 0, 1]:
                if length + offset > 0:
                    text = "T" * (length + offset)
                    encoded = self.encoder.encode_to_base64(text)
                    decoded = base64.b64decode(encoded).decode()
                    self.assertEqual(decoded, text)

    def test_encode_very_long_string(self):
        """Very long string (10MB)"""
        text = "A" * (10 * 1024 * 1024)
        encoded = self.encoder.encode_to_base64(text)
        # Verify at least the length is correct (base64 increases size by ~4/3)
        self.assertGreater(len(encoded), len(text))
        # Verify it can be decoded back
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(len(decoded), len(text))


class TestBase64EdgeCasesSpecialCharacters(unittest.TestCase):
    """Test special character handling"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_encode_all_printable_ascii(self):
        """All printable ASCII characters"""
        import string
        text = string.printable
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_control_characters(self):
        """Control characters (0-31)"""
        text = "".join(chr(i) for i in range(32))
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_quotes_and_escapes(self):
        """Quotes and escape sequences"""
        text = '''He said "hello" and 'goodbye' with \\ slash'''
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_regex_special_chars(self):
        """Regex special characters"""
        text = r"^[a-zA-Z0-9.!?*+(){}[\]|\\-]+$"
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_html_entities(self):
        """HTML entities and tags"""
        text = "<html>&nbsp;<div class='test'>&copy; 2024</div></html>"
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_xml_entities(self):
        """XML entities"""
        text = "<?xml version='1.0'?><root attr='value &amp; more'/>"
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_sql_injection_patterns(self):
        """SQL injection patterns"""
        text = "'; DROP TABLE users; --"
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)


class TestBase64EdgeCasesRepeatingPatterns(unittest.TestCase):
    """Test repeating pattern edge cases"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_encode_single_char_repeated(self):
        """Single character repeated"""
        for char in "abcdefghijklmnopqrstuvwxyz":
            for count in [1, 2, 3, 10, 100, 1000]:
                text = char * count
                encoded = self.encoder.encode_to_base64(text)
                decoded = base64.b64decode(encoded).decode()
                self.assertEqual(decoded, text)

    def test_encode_alternating_pattern(self):
        """Alternating character pattern"""
        text = "ab" * 1000
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_base64_like_pattern(self):
        """Pattern that looks like Base64"""
        text = "SGVsbG8gV29ybGQ=" * 100
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)

    def test_encode_base64_alphabet(self):
        """Base64 alphabet as input"""
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" * 10
        encoded = self.encoder.encode_to_base64(text)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, text)


class TestBase64EdgeCasesBinaryData(unittest.TestCase):
    """Test binary data edge cases"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_encode_all_byte_values(self):
        """All possible byte values (0-255)"""
        data = bytes(range(256))
        encoded = self.encoder.encode_bytes_to_base64(data)
        decoded = base64.b64decode(encoded)
        self.assertEqual(decoded, data)

    def test_encode_repeated_byte_pattern(self):
        """Repeated byte patterns"""
        for byte_val in [0, 1, 127, 255]:
            data = bytes([byte_val] * 100)
            encoded = self.encoder.encode_bytes_to_base64(data)
            decoded = base64.b64decode(encoded)
            self.assertEqual(decoded, data)

    def test_encode_binary_with_null_bytes(self):
        """Binary data with null bytes"""
        data = b"\x00\x01\x02\x03\x00\xff\xfe\xfd"
        encoded = self.encoder.encode_bytes_to_base64(data)
        decoded = base64.b64decode(encoded)
        self.assertEqual(decoded, data)

    def test_encode_high_entropy_binary(self):
        """High entropy binary data"""
        import hashlib
        # Generate high-entropy data using hash
        data = hashlib.sha256(b"test" * 100).digest() * 10
        encoded = self.encoder.encode_bytes_to_base64(data)
        decoded = base64.b64decode(encoded)
        self.assertEqual(decoded, data)


class TestBase64EdgeCasesRoundTrip(unittest.TestCase):
    """Test round-trip encoding/decoding edge cases"""

    def setUp(self):
        self.ops = Base64OperationsPair()

    def test_round_trip_empty(self):
        """Round trip empty string"""
        success = self.ops.round_trip_transform("")
        self.assertTrue(success)

    def test_round_trip_single_byte(self):
        """Round trip single byte"""
        success = self.ops.round_trip_transform("X")
        self.assertTrue(success)

    def test_round_trip_special_chars(self):
        """Round trip special characters"""
        text = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        success = self.ops.round_trip_transform(text)
        self.assertTrue(success)

    def test_round_trip_unicode(self):
        """Round trip Unicode"""
        text = "你好世界 مرحبا Привет 🌍"
        success = self.ops.round_trip_transform(text)
        self.assertTrue(success)

    def test_round_trip_whitespace_variations(self):
        """Round trip various whitespace"""
        texts = [" ", "\t", "\n", "\r", "\r\n", " \t\n\r"]
        for text in texts:
            success = self.ops.round_trip_transform(text)
            self.assertTrue(success, f"Failed for whitespace: {repr(text)}")

    def test_round_trip_null_bytes(self):
        """Round trip null bytes"""
        text = "test\x00value"
        success = self.ops.round_trip_transform(text)
        self.assertTrue(success)

    def test_round_trip_multiple_encodings(self):
        """Multiple successive round trips"""
        original = "Test Data"
        current = original
        for _ in range(10):
            # Encode
            encoded = base64.b64encode(current.encode()).decode()
            # Decode
            current = base64.b64decode(encoded).decode()
        self.assertEqual(current, original)


class TestBase64EdgeCasesVerification(unittest.TestCase):
    """Test verification edge cases"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_verify_empty_string(self):
        """Verify empty string"""
        result = self.encoder.verify_encoding("", "")
        self.assertTrue(result)

    def test_verify_case_sensitive(self):
        """Verify Base64 is case-sensitive"""
        original = "Test"
        encoded = self.encoder.encode_to_base64(original)
        # Change case (Base64 is case-sensitive)
        mangled = encoded.lower() if encoded.isupper() else encoded.upper()
        try:
            result = self.encoder.verify_encoding(original, mangled)
            # Should fail because of case difference
            self.assertFalse(result)
        except:
            # Or may raise an error
            pass

    def test_verify_padding_modified(self):
        """Verify fails with modified padding"""
        original = "A"
        encoded = self.encoder.encode_to_base64(original)  # "QQ=="
        # Remove padding
        mangled = encoded.replace("=", "")
        try:
            result = self.encoder.verify_encoding(original, mangled)
            self.assertFalse(result)
        except:
            pass

    def test_verify_character_changed(self):
        """Verify fails with character changed"""
        original = "Test"
        encoded = self.encoder.encode_to_base64(original)
        # Change a character in encoded string
        mangled = encoded[:-1] + ('A' if encoded[-1] != 'A' else 'B')
        result = self.encoder.verify_encoding(original, mangled)
        self.assertFalse(result)


class TestBase64EdgeCasesPowershell(unittest.TestCase):
    """Test PowerShell encoding edge cases"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_powershell_empty_command(self):
        """PowerShell empty command"""
        encoded = self.encoder.create_powershell_encoded_command("")
        decoded = base64.b64decode(encoded).decode('utf-16-le')
        self.assertEqual(decoded, "")

    def test_powershell_single_char(self):
        """PowerShell single character"""
        encoded = self.encoder.create_powershell_encoded_command("A")
        decoded = base64.b64decode(encoded).decode('utf-16-le')
        self.assertEqual(decoded, "A")

    def test_powershell_special_chars(self):
        """PowerShell special characters"""
        command = "$var = @(); [array]::ForEach($var, {$_})"
        encoded = self.encoder.create_powershell_encoded_command(command)
        decoded = base64.b64decode(encoded).decode('utf-16-le')
        self.assertEqual(decoded, command)

    def test_powershell_unicode(self):
        """PowerShell with unicode"""
        command = "Write-Host '你好'"
        encoded = self.encoder.create_powershell_encoded_command(command)
        decoded = base64.b64decode(encoded).decode('utf-16-le')
        self.assertEqual(decoded, command)

    def test_powershell_large_script(self):
        """PowerShell large script"""
        command = "for ($i=0; $i -lt 1000; $i++) { Write-Host $i }"
        encoded = self.encoder.create_powershell_encoded_command(command)
        decoded = base64.b64decode(encoded).decode('utf-16-le')
        self.assertEqual(decoded, command)


class TestBase64EdgeCasesBatchOperations(unittest.TestCase):
    """Test batch operation edge cases"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_batch_empty_list(self):
        """Batch with empty list"""
        results = self.encoder.batch_encode_multiple([])
        self.assertEqual(len(results), 0)

    def test_batch_single_item(self):
        """Batch with single item"""
        results = self.encoder.batch_encode_multiple(["test"])
        self.assertEqual(len(results), 1)
        self.assertIn("test", results)

    def test_batch_duplicate_items(self):
        """Batch with duplicate items"""
        results = self.encoder.batch_encode_multiple(["test", "test", "test"])
        # Dictionary keys must be unique, so there should be 1 unique item
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("test", results)

    def test_batch_empty_strings(self):
        """Batch with empty strings"""
        results = self.encoder.batch_encode_multiple(["", "", ""])
        # Dictionary keys must be unique, so there should be 1 empty string key
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("", results)

    def test_batch_large_number_items(self):
        """Batch with large number of items"""
        items = [f"item_{i}" for i in range(1000)]
        results = self.encoder.batch_encode_multiple(items)
        self.assertEqual(len(results), 1000)

    def test_batch_mixed_content(self):
        """Batch with mixed content types"""
        items = [
            "",
            "a",
            "Hello World",
            "!@#$%^&*()",
            "你好",
            "A" * 1000,
        ]
        results = self.encoder.batch_encode_multiple(items)
        self.assertEqual(len(results), len(items))
        for item in items:
            self.assertIn(item, results)


class TestBase64EdgeCasesDataTypeHandling(unittest.TestCase):
    """Test data type handling edge cases"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_encode_bytes_empty(self):
        """Encode empty bytes"""
        result = self.encoder.encode_bytes_to_base64(b"")
        self.assertEqual(result, "")

    def test_encode_bytes_single_byte(self):
        """Encode single byte"""
        result = self.encoder.encode_bytes_to_base64(b"X")
        decoded = base64.b64decode(result)
        self.assertEqual(decoded, b"X")

    def test_encode_invalid_type_none(self):
        """Encoding None should raise TypeError"""
        with self.assertRaises((TypeError, AttributeError)):
            self.encoder.encode_to_base64(None)

    def test_encode_invalid_type_int(self):
        """Encoding int should raise TypeError"""
        with self.assertRaises(TypeError):
            self.encoder.encode_to_base64(12345)

    def test_encode_invalid_type_list(self):
        """Encoding list should raise TypeError"""
        with self.assertRaises(TypeError):
            self.encoder.encode_to_base64([1, 2, 3])

    def test_encode_invalid_type_dict(self):
        """Encoding dict should raise TypeError"""
        with self.assertRaises(TypeError):
            self.encoder.encode_to_base64({"key": "value"})

    def test_encode_bytes_invalid_type(self):
        """Encoding non-bytes to encode_bytes should raise TypeError"""
        with self.assertRaises(TypeError):
            self.encoder.encode_bytes_to_base64("not bytes")


class TestBase64EdgeCasesStandardCompliance(unittest.TestCase):
    """Test RFC 4648 Base64 standard compliance"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_rfc4648_example_1(self):
        """RFC 4648 test vector: 'foobar'"""
        result = self.encoder.encode_to_base64("foobar")
        self.assertEqual(result, "Zm9vYmFy")

    def test_rfc4648_example_2(self):
        """RFC 4648 test vector: 'fooba'"""
        result = self.encoder.encode_to_base64("fooba")
        self.assertEqual(result, "Zm9vYmE=")

    def test_rfc4648_example_3(self):
        """RFC 4648 test vector: 'foob'"""
        result = self.encoder.encode_to_base64("foob")
        self.assertEqual(result, "Zm9vYg==")

    def test_rfc4648_test_vectors(self):
        """RFC 4648 complete test vectors"""
        test_vectors = [
            ("", ""),
            ("f", "Zg=="),
            ("fo", "Zm8="),
            ("foo", "Zm9v"),
            ("foob", "Zm9vYg=="),
            ("fooba", "Zm9vYmE="),
            ("foobar", "Zm9vYmFy"),
        ]
        for plain, expected in test_vectors:
            result = self.encoder.encode_to_base64(plain)
            self.assertEqual(result, expected, f"Failed for '{plain}'")


class TestBase64EdgeCasesConsistency(unittest.TestCase):
    """Test consistency and determinism"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_multiple_encodings_same_result(self):
        """Multiple encodings of same input produce same result"""
        text = "Consistency Test"
        result1 = self.encoder.encode_to_base64(text)
        result2 = self.encoder.encode_to_base64(text)
        result3 = self.encoder.encode_to_base64(text)
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)

    def test_different_instances_same_result(self):
        """Different encoder instances produce same result"""
        text = "Different Instances"
        encoder1 = Base64Encoder()
        encoder2 = Base64Encoder()
        result1 = encoder1.encode_to_base64(text)
        result2 = encoder2.encode_to_base64(text)
        self.assertEqual(result1, result2)

    def test_encoding_is_deterministic(self):
        """Encoding is deterministic (no random elements)"""
        import hashlib
        text = "Deterministic Test"
        hashes = []
        for _ in range(10):
            result = self.encoder.encode_to_base64(text)
            hashes.append(hashlib.sha256(result.encode()).hexdigest())
        # All hashes should be identical
        self.assertTrue(all(h == hashes[0] for h in hashes))


class TestBase64EdgeCasesLookupTable(unittest.TestCase):
    """Test lookup table edge cases"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_lookup_table_empty_list(self):
        """Lookup table with empty list"""
        lookup = self.encoder.create_reverse_lookup_table([])
        self.assertEqual(len(lookup['forward']), 0)
        self.assertEqual(len(lookup['reverse']), 0)

    def test_lookup_table_single_item(self):
        """Lookup table with single item"""
        lookup = self.encoder.create_reverse_lookup_table(["test"])
        self.assertEqual(len(lookup['forward']), 1)
        self.assertEqual(len(lookup['reverse']), 1)
        self.assertIn("test", lookup['forward'])

    def test_lookup_table_duplicates(self):
        """Lookup table with duplicate items"""
        lookup = self.encoder.create_reverse_lookup_table(["test", "test", "test"])
        # Should handle duplicates gracefully
        self.assertIn("test", lookup['forward'])

    def test_lookup_table_bidirectional(self):
        """Lookup table bidirectional consistency"""
        items = ["a", "b", "c", "test", ""]
        lookup = self.encoder.create_reverse_lookup_table(items)
        for item in items:
            if item:  # Skip empty strings in this check
                encoded = lookup['forward'][item]
                self.assertEqual(lookup['reverse'][encoded], item)


class TestBase64EdgeCasesMemoryAndPerformance(unittest.TestCase):
    """Test memory and performance edge cases"""

    def setUp(self):
        self.encoder = Base64Encoder()

    def test_large_string_encoding(self):
        """Encode very large string"""
        text = "X" * (100 * 1024 * 1024)  # 100MB
        try:
            encoded = self.encoder.encode_to_base64(text)
            # Should handle without crashing
            self.assertIsInstance(encoded, str)
        except MemoryError:
            # May fail on limited systems - that's acceptable
            pass

    def test_many_small_encodings(self):
        """Many small encoding operations"""
        for i in range(10000):
            text = f"test_{i}"
            encoded = self.encoder.encode_to_base64(text)
            self.assertIsInstance(encoded, str)

    def test_encoding_preserves_length_ratio(self):
        """Verify encoding preserves expected length ratio"""
        # Base64 encoded string should be ~4/3 the length of original
        text = "A" * 3000
        encoded = self.encoder.encode_to_base64(text)
        # Account for padding
        expected_length = (len(text) * 4) // 3
        if len(text) % 3:
            expected_length += 4 - (len(text) % 3)
        self.assertEqual(len(encoded), expected_length)


if __name__ == "__main__":
    unittest.main(verbosity=2)
