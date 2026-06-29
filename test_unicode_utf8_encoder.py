#!/usr/bin/env python3
"""
Comprehensive test suite for Unicode/UTF-8 Command Encoder
Tests all encoding features, normalization, and international character support.
"""

import unittest
import json
from unicode_utf8_encoder import (
    UnicodeUTF8Encoder,
    UTF8Encoder,
    UnicodeNormalizer,
    PercentEncoder,
    UnicodeAnalyzer,
    SafeCommandBuilder,
    EmojiHandler,
    PunycodeHandler,
    UnicodeNormalizationForm,
    encode_utf8,
    decode_utf8,
    percent_encode,
    percent_decode,
    normalize,
    analyze_text,
)


class TestUTF8Encoder(unittest.TestCase):
    """Test UTF-8 encoding/decoding"""

    def setUp(self):
        self.encoder = UTF8Encoder()

    def test_encode_ascii(self):
        """Test encoding ASCII text"""
        text = "Hello World"
        encoded = self.encoder.encode_utf8(text)
        self.assertEqual(encoded, b'Hello World')

    def test_encode_unicode(self):
        """Test encoding Unicode text with multi-byte characters"""
        text = "Hello, 世界"
        encoded = self.encoder.encode_utf8(text)
        # UTF-8 encoding of 世 (U+4E16) = E4 B8 96
        # UTF-8 encoding of 界 (U+754C) = E7 95 8C
        self.assertIn(b'\xe4\xb8\x96', encoded)
        self.assertIn(b'\xe7\x95\x8c', encoded)

    def test_encode_emoji(self):
        """Test encoding emoji"""
        text = "Hello 🌍"
        encoded = self.encoder.encode_utf8(text)
        # 🌍 (U+1F30D) is encoded as F0 9F 8C 8D
        self.assertIn(b'\xf0\x9f\x8c\x8d', encoded)

    def test_decode_utf8(self):
        """Test decoding UTF-8 bytes"""
        encoded = b'Hello, \xe4\xb8\x96\xe7\x95\x8c'
        decoded = self.encoder.decode_utf8(encoded)
        self.assertEqual(decoded, "Hello, 世界")

    def test_get_byte_sequence(self):
        """Test getting byte sequence for character"""
        # 'A' should be [65]
        self.assertEqual(self.encoder.get_byte_sequence('A'), [65])
        # '€' (U+20AC) should be [226, 130, 172]
        self.assertEqual(self.encoder.get_byte_sequence('€'), [226, 130, 172])

    def test_get_codepoint(self):
        """Test getting Unicode codepoint"""
        self.assertEqual(self.encoder.get_codepoint('A'), 0x41)
        self.assertEqual(self.encoder.get_codepoint('é'), 0xE9)
        self.assertEqual(self.encoder.get_codepoint('世'), 0x4E16)

    def test_char_from_codepoint(self):
        """Test creating character from codepoint"""
        self.assertEqual(self.encoder.char_from_codepoint(0x41), 'A')
        self.assertEqual(self.encoder.char_from_codepoint(0x4E16), '世')
        self.assertEqual(self.encoder.char_from_codepoint(0x1F30D), '🌍')

    def test_bom_detection(self):
        """Test BOM detection"""
        utf8_bom = b'\xef\xbb\xbf' + b'hello'
        self.assertEqual(self.encoder.detect_bom(utf8_bom), 'UTF-8')

        utf16_be_bom = b'\xfe\xff' + b'hello'
        self.assertEqual(self.encoder.detect_bom(utf16_be_bom), 'UTF-16-BE')

        utf16_le_bom = b'\xff\xfe' + b'hello'
        self.assertEqual(self.encoder.detect_bom(utf16_le_bom), 'UTF-16-LE')

    def test_add_utf8_bom(self):
        """Test adding UTF-8 BOM"""
        text = "Hello"
        with_bom = self.encoder.add_utf8_bom(text)
        self.assertTrue(with_bom.startswith(b'\xef\xbb\xbf'))
        self.assertEqual(self.encoder.detect_bom(with_bom), 'UTF-8')

    def test_remove_bom(self):
        """Test BOM removal"""
        text = b'\xef\xbb\xbfHello'
        without_bom = self.encoder.remove_bom(text)
        self.assertEqual(without_bom, b'Hello')


class TestUnicodeNormalizer(unittest.TestCase):
    """Test Unicode normalization"""

    def setUp(self):
        self.normalizer = UnicodeNormalizer()

    def test_nfc_normalization(self):
        """Test NFC (Canonical Composition) normalization"""
        # é can be represented as U+00E9 or U+0065 U+0301
        decomposed = 'é'  # e + combining acute
        composed = 'é'  # precomposed é

        nfc_decomposed = self.normalizer.normalize_nfc(decomposed)
        nfc_composed = self.normalizer.normalize_nfc(composed)

        self.assertEqual(nfc_decomposed, nfc_composed)

    def test_nfd_normalization(self):
        """Test NFD (Canonical Decomposition) normalization"""
        composed = 'é'
        nfd = self.normalizer.normalize_nfd(composed)
        self.assertIn('́', nfd)  # Should contain combining acute

    def test_nfkc_normalization(self):
        """Test NFKC (Compatibility Composition) normalization"""
        # ﬁ (fi ligature, U+FB01) should normalize to 'fi'
        text = 'ﬁ'
        nfkc = self.normalizer.normalize_nfkc(text)
        self.assertEqual(nfkc, 'fi')

    def test_normalization_caching(self):
        """Test that normalization results are cached"""
        text = "café"
        result1 = self.normalizer.normalize_nfc(text)
        result2 = self.normalizer.normalize_nfc(text)
        self.assertIs(result1, result2)  # Same object due to caching


class TestPercentEncoder(unittest.TestCase):
    """Test percent encoding/decoding"""

    def setUp(self):
        self.encoder = PercentEncoder()

    def test_percent_encode_ascii(self):
        """Test percent encoding ASCII"""
        encoded = self.encoder.percent_encode("Hello World")
        self.assertEqual(encoded, "Hello%20World")

    def test_percent_encode_unicode(self):
        """Test percent encoding Unicode"""
        encoded = self.encoder.percent_encode("café")
        # é is U+00E9, UTF-8 bytes: C3 A9
        self.assertIn("%C3%A9", encoded)

    def test_percent_encode_with_safe_chars(self):
        """Test percent encoding with safe characters"""
        encoded = self.encoder.percent_encode("user@example.com", safe_chars='@.')
        self.assertEqual(encoded, "user@example.com")

    def test_percent_decode(self):
        """Test percent decoding"""
        decoded = self.encoder.percent_decode("Hello%20World")
        self.assertEqual(decoded, "Hello World")

    def test_percent_decode_unicode(self):
        """Test percent decoding Unicode"""
        decoded = self.encoder.percent_decode("caf%C3%A9")
        self.assertEqual(decoded, "café")

    def test_url_encode(self):
        """Test URL encoding (RFC 3986)"""
        encoded = self.encoder.url_encode("user@example.com:8080/path?query=value")
        # Should preserve unreserved characters
        self.assertIn("example.com", encoded)
        self.assertIn("user", encoded)


class TestUnicodeAnalyzer(unittest.TestCase):
    """Test Unicode character analysis"""

    def setUp(self):
        self.analyzer = UnicodeAnalyzer()

    def test_get_category(self):
        """Test Unicode category detection"""
        self.assertEqual(self.analyzer.get_category('A'), 'Lu')  # Uppercase Letter
        self.assertEqual(self.analyzer.get_category('a'), 'Ll')  # Lowercase Letter
        self.assertEqual(self.analyzer.get_category('5'), 'Nd')  # Decimal Digit
        self.assertEqual(self.analyzer.get_category(' '), 'Zs')  # Space Separator

    def test_get_name(self):
        """Test Unicode character names"""
        name_a = self.analyzer.get_name('A')
        self.assertIn('LATIN', name_a)

        name_emoji = self.analyzer.get_name('🌍')
        self.assertIsNotNone(name_emoji)

    def test_is_printable(self):
        """Test printability detection"""
        self.assertTrue(self.analyzer.is_printable("Hello"))
        self.assertFalse(self.analyzer.is_printable("Hello\x00World"))  # Contains null

    def test_detect_scripts(self):
        """Test script detection"""
        scripts = self.analyzer.detect_scripts("Hello 世界")
        self.assertIn('Latin', scripts)
        self.assertIn('Han', scripts)

        scripts = self.analyzer.detect_scripts("Привет")
        self.assertIn('Cyrillic', scripts)

        scripts = self.analyzer.detect_scripts("مرحبا")
        self.assertIn('Arabic', scripts)

    def test_get_width(self):
        """Test East Asian Width detection"""
        # ASCII character should be width 1
        self.assertEqual(self.analyzer.get_width('A'), 1)
        # CJK characters are typically width 2
        self.assertEqual(self.analyzer.get_width('あ'), 2)  # Hiragana
        self.assertEqual(self.analyzer.get_width('中'), 2)  # Han


class TestSafeCommandBuilder(unittest.TestCase):
    """Test safe command building"""

    def setUp(self):
        self.builder = SafeCommandBuilder()

    def test_escape_for_bash(self):
        """Test bash escaping"""
        escaped = self.builder.escape_for_shell("Hello 'World'", 'bash')
        self.assertEqual(escaped, "'Hello '\\''World'\\'''")

    def test_escape_for_cmd(self):
        """Test CMD escaping"""
        escaped = self.builder.escape_for_shell("test<>|&", 'cmd')
        self.assertIn('^<', escaped)
        self.assertIn('^>', escaped)
        self.assertIn('^|', escaped)
        self.assertIn('^&', escaped)

    def test_build_command(self):
        """Test building safe commands"""
        cmd = self.builder.build_command("echo", "Hello", "World")
        self.assertIn("echo", cmd)

    def test_build_command_with_encoding(self):
        """Test building commands with encoding"""
        cmd = self.builder.build_command_with_encoding("echo", "Hello", encoding='percent')
        self.assertIn("echo", cmd)


class TestEmojiHandler(unittest.TestCase):
    """Test emoji handling"""

    def setUp(self):
        self.handler = EmojiHandler()

    def test_extract_emoji(self):
        """Test emoji extraction"""
        text = "Hello 👋 World 🌍"
        emojis = self.handler.extract_emoji(text)
        self.assertEqual(len(emojis), 2)
        self.assertIn('👋', emojis)
        self.assertIn('🌍', emojis)

    def test_has_emoji(self):
        """Test emoji detection"""
        self.assertTrue(self.handler.has_emoji("Hello 🌍"))
        self.assertFalse(self.handler.has_emoji("Hello World"))

    def test_remove_emoji(self):
        """Test emoji removal"""
        text = "Hello 👋 World 🌍"
        without_emoji = self.handler.remove_emoji(text)
        self.assertEqual(without_emoji, "Hello  World ")

    def test_count_emoji(self):
        """Test emoji counting"""
        text = "Hello 👋 World 🌍"
        count = self.handler.count_emoji(text)
        self.assertEqual(count, 2)


class TestPunycodeHandler(unittest.TestCase):
    """Test Punycode handling for international domains"""

    def setUp(self):
        self.handler = PunycodeHandler()

    def test_encode_punycode(self):
        """Test Punycode encoding"""
        domain = "münchen.de"
        encoded = self.handler.encode_punycode(domain)
        self.assertIn("xn--", encoded)  # Punycode prefix

    def test_decode_punycode(self):
        """Test Punycode decoding"""
        encoded = "xn--mnchen-3ya.de"
        decoded = self.handler.decode_punycode(encoded)
        self.assertIn("münchen", decoded.lower())


class TestUnicodeUTF8EncoderIntegration(unittest.TestCase):
    """Integration tests for complete encoder"""

    def setUp(self):
        self.encoder = UnicodeUTF8Encoder()

    def test_encode_command_percent(self):
        """Test encoding command with percent encoding"""
        encoded = self.encoder.encode_command("Hello 世界", method='percent')
        self.assertIsInstance(encoded, str)
        self.assertIn('%', encoded)

    def test_encode_command_utf8_hex(self):
        """Test encoding command with UTF-8 hex"""
        encoded = self.encoder.encode_command("Hello", method='utf8-hex')
        self.assertIn('\\x', encoded)

    def test_encode_decode_roundtrip(self):
        """Test encoding/decoding roundtrip"""
        original = "Hello, 世界! 🌍"
        encoded = self.encoder.encode_command(original, method='percent')
        decoded = self.encoder.decode_command(encoded, method='percent')
        self.assertEqual(decoded, original)

    def test_get_encoding_info(self):
        """Test comprehensive encoding information"""
        text = "Hello 日本語 🌍"
        info = self.encoder.get_encoding_info(text)

        self.assertIn('original', info)
        self.assertIn('utf8_bytes', info)
        self.assertIn('utf8_length', info)
        self.assertIn('char_count', info)
        self.assertIn('percent_encoded', info)
        self.assertIn('scripts', info)
        self.assertIn('has_emoji', info)
        self.assertIn('characters', info)

        self.assertEqual(info['original'], text)
        self.assertTrue(info['has_emoji'])
        self.assertIn('Han', info['scripts'])
        self.assertGreater(info['utf8_length'], len(text))


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    def test_encode_utf8_function(self):
        """Test encode_utf8 convenience function"""
        result = encode_utf8("Hello")
        self.assertEqual(result, b'Hello')

    def test_decode_utf8_function(self):
        """Test decode_utf8 convenience function"""
        result = decode_utf8(b'Hello')
        self.assertEqual(result, "Hello")

    def test_percent_encode_function(self):
        """Test percent_encode convenience function"""
        result = percent_encode("Hello World")
        self.assertEqual(result, "Hello%20World")

    def test_percent_decode_function(self):
        """Test percent_decode convenience function"""
        result = percent_decode("Hello%20World")
        self.assertEqual(result, "Hello World")

    def test_normalize_function(self):
        """Test normalize convenience function"""
        result = normalize("café", 'NFC')
        self.assertIsInstance(result, str)

    def test_analyze_text_function(self):
        """Test analyze_text convenience function"""
        info = analyze_text("Hello 世界")
        self.assertIsInstance(info, dict)
        self.assertIsNotNone(info.get('char_count'))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios"""

    def setUp(self):
        self.encoder = UnicodeUTF8Encoder()

    def test_empty_string(self):
        """Test handling empty strings"""
        utf8 = self.encoder.utf8.encode_utf8("")
        self.assertEqual(utf8, b'')

        percent = self.encoder.percent_encoder.percent_encode("")
        self.assertEqual(percent, "")

    def test_very_long_string(self):
        """Test handling very long strings"""
        long_text = "Hello " * 10000
        utf8 = self.encoder.utf8.encode_utf8(long_text)
        decoded = self.encoder.utf8.decode_utf8(utf8)
        self.assertEqual(decoded, long_text)

    def test_mixed_bidi_text(self):
        """Test bidirectional text mixing"""
        bidi_text = "Hello שלום مرحبا"
        is_bidi = self.encoder.analyzer.is_bidi_text(bidi_text)
        # May or may not detect depending on RTL marks

    def test_invalid_utf8_recovery(self):
        """Test handling invalid UTF-8"""
        # Invalid UTF-8 byte sequence
        invalid = b'\xff\xfe'
        decoded = self.encoder.utf8.decode_utf8(invalid)
        # Should not raise, should use replacement character
        self.assertIsInstance(decoded, str)

    def test_surrogate_pair_handling(self):
        """Test emoji (surrogate pairs in UTF-16)"""
        emoji = "🌍"  # U+1F30D
        codepoint = self.encoder.utf8.get_codepoint(emoji)
        self.assertEqual(codepoint, 0x1F30D)

    def test_combining_characters(self):
        """Test combining characters"""
        # Base character + combining accent
        combining = 'é'  # e + combining acute
        count = len(combining)
        self.assertEqual(count, 2)  # Two characters
        self.assertFalse(combining[1].isalpha())  # Second is combining mark


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios"""

    def setUp(self):
        self.encoder = UnicodeUTF8Encoder()

    def test_international_filenames(self):
        """Test handling international filenames"""
        filename = "文档_2024.txt"
        encoded = self.encoder.percent_encoder.percent_encode(filename)
        decoded = self.encoder.percent_encoder.percent_decode(encoded)
        self.assertEqual(decoded, filename)

    def test_command_line_arguments(self):
        """Test safe command-line argument passing"""
        arg = "Hello 'World' & special chars"
        safe_bash = self.encoder.command_builder.escape_for_shell(arg, 'bash')
        # Should be wrapped in single quotes with escaped embedded quotes
        self.assertTrue(safe_bash.startswith("'"))
        self.assertTrue(safe_bash.endswith("'"))

    def test_log_message_encoding(self):
        """Test encoding log messages with emoji"""
        log_msg = "Task completed ✓ Success 🎉"
        info = self.encoder.get_encoding_info(log_msg)
        # ✓ is U+2713 (not emoji), 🎉 is emoji
        self.assertGreater(info['emoji_count'], 0)

    def test_url_parameter_encoding(self):
        """Test URL parameter encoding"""
        param = "search=café français"
        encoded = self.encoder.percent_encoder.url_encode(param)
        decoded = self.encoder.percent_encoder.percent_decode(encoded)
        self.assertEqual(decoded, param)


def run_tests():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUTF8Encoder))
    suite.addTests(loader.loadTestsFromTestCase(TestUnicodeNormalizer))
    suite.addTests(loader.loadTestsFromTestCase(TestPercentEncoder))
    suite.addTests(loader.loadTestsFromTestCase(TestUnicodeAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestSafeCommandBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestEmojiHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestPunycodeHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestUnicodeUTF8EncoderIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestRealWorldScenarios))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("UNICODE/UTF-8 ENCODER TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
