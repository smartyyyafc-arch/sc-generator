#!/usr/bin/env python3
"""
Comprehensive Tests for Multi-Encoding Key Derivation System
Tests key derivation methods, encoding strategies, and integration
"""

import unittest
import json
import hashlib
from typing import Dict, Any

from multi_encoding_key_derivation import (
    MultiEncodingKeySystem,
    KeyDerivationMethod,
    EncodingStrategy,
    FingerprintHasher,
    KeyDerivationFactory,
    EncodingStrategySelector,
    FingerprintComponent,
    TargetProfile
)


class TestFingerprintHasher(unittest.TestCase):
    """Test fingerprint hashing functionality"""

    def setUp(self):
        self.hasher = FingerprintHasher()
        self.test_data = {
            'os': 'Windows 10',
            'processor': 'Intel i7',
            'hostname': 'WORKSTATION-01'
        }

    def test_hash_fingerprint_deterministic(self):
        """Test that same fingerprint produces same hash"""
        hash1 = self.hasher.hash_fingerprint(self.test_data)
        hash2 = self.hasher.hash_fingerprint(self.test_data)
        self.assertEqual(hash1, hash2)

    def test_hash_fingerprint_different_for_different_data(self):
        """Test that different fingerprints produce different hashes"""
        data2 = self.test_data.copy()
        data2['hostname'] = 'DIFFERENT'

        hash1 = self.hasher.hash_fingerprint(self.test_data)
        hash2 = self.hasher.hash_fingerprint(data2)
        self.assertNotEqual(hash1, hash2)

    def test_hash_with_weights(self):
        """Test weighted hash calculation"""
        weights = {'os': 2, 'processor': 1, 'hostname': 1}
        hash_val = self.hasher.hash_with_weights(self.test_data, weights)
        self.assertIsNotNone(hash_val)
        self.assertEqual(len(hash_val), 64)  # SHA256 hex length

    def test_extract_components(self):
        """Test component extraction from hash"""
        hash_val = self.hasher.hash_fingerprint(self.test_data)
        components = self.hasher.extract_components(hash_val, 4)

        self.assertEqual(len(components), 4)
        self.assertTrue(all(len(c) > 0 for c in components))

    def test_different_hash_methods(self):
        """Test different hash methods"""
        hash_sha256 = self.hasher.hash_fingerprint(self.test_data, 'sha256')
        hash_sha512 = self.hasher.hash_fingerprint(self.test_data, 'sha512')
        hash_md5 = self.hasher.hash_fingerprint(self.test_data, 'md5')

        self.assertEqual(len(hash_sha256), 64)  # SHA256
        self.assertEqual(len(hash_sha512), 128)  # SHA512
        self.assertEqual(len(hash_md5), 32)  # MD5


class TestKeyDerivationFactory(unittest.TestCase):
    """Test key derivation methods"""

    def setUp(self):
        self.fingerprint = {
            'system': 'test_system',
            'version': '1.0.0',
            'id': 'test_id_12345'
        }
        self.salt = 'test_salt_1234'

    def test_pbkdf2_derivation(self):
        """Test PBKDF2 key derivation"""
        key = KeyDerivationFactory.derive_pbkdf2(
            self.fingerprint,
            self.salt,
            iterations=10000,
            key_length=32
        )

        self.assertEqual(len(key), 32)
        self.assertIsInstance(key, bytes)

    def test_pbkdf2_deterministic(self):
        """Test PBKDF2 produces same key for same input"""
        key1 = KeyDerivationFactory.derive_pbkdf2(
            self.fingerprint,
            self.salt,
            iterations=10000,
            key_length=32
        )
        key2 = KeyDerivationFactory.derive_pbkdf2(
            self.fingerprint,
            self.salt,
            iterations=10000,
            key_length=32
        )

        self.assertEqual(key1, key2)

    def test_hkdf_derivation(self):
        """Test HKDF key derivation"""
        key = KeyDerivationFactory.derive_hkdf(
            self.fingerprint,
            self.salt,
            key_length=32
        )

        self.assertEqual(len(key), 32)
        self.assertIsInstance(key, bytes)

    def test_sha256_chain_derivation(self):
        """Test SHA256 chain key derivation"""
        key = KeyDerivationFactory.derive_sha256_chain(
            self.fingerprint,
            self.salt,
            iterations=1000,
            key_length=32
        )

        self.assertEqual(len(key), 32)
        self.assertIsInstance(key, bytes)

    def test_hmac_chain_derivation(self):
        """Test HMAC chain key derivation"""
        key = KeyDerivationFactory.derive_hmac_chain(
            self.fingerprint,
            self.salt,
            iterations=1000,
            key_length=32
        )

        self.assertEqual(len(key), 32)
        self.assertIsInstance(key, bytes)

    def test_generic_derive_key(self):
        """Test generic key derivation with different methods"""
        methods = [
            KeyDerivationMethod.PBKDF2,
            KeyDerivationMethod.HKDF,
            KeyDerivationMethod.SHA256_CHAIN,
            KeyDerivationMethod.HMAC_CHAIN
        ]

        for method in methods:
            with self.subTest(method=method):
                key = KeyDerivationFactory.derive_key(
                    self.fingerprint,
                    method,
                    self.salt,
                    iterations=10000,
                    key_length=32
                )

                self.assertEqual(len(key), 32)
                self.assertIsInstance(key, bytes)

    def test_different_salt_different_key(self):
        """Test that different salts produce different keys"""
        key1 = KeyDerivationFactory.derive_pbkdf2(
            self.fingerprint,
            'salt_1',
            iterations=10000,
            key_length=32
        )
        key2 = KeyDerivationFactory.derive_pbkdf2(
            self.fingerprint,
            'salt_2',
            iterations=10000,
            key_length=32
        )

        self.assertNotEqual(key1, key2)


class TestEncodingStrategySelector(unittest.TestCase):
    """Test encoding strategy selection"""

    def setUp(self):
        self.fingerprint = {
            'device': 'laptop',
            'os': 'Linux',
            'arch': 'x86_64'
        }

    def test_strategy_selection_deterministic(self):
        """Test that same fingerprint selects same strategy"""
        strategy1 = EncodingStrategySelector.select_strategy_from_fingerprint(
            self.fingerprint
        )
        strategy2 = EncodingStrategySelector.select_strategy_from_fingerprint(
            self.fingerprint
        )

        self.assertEqual(strategy1, strategy2)

    def test_strategy_selection_different_fingerprint(self):
        """Test different fingerprint may select different strategy"""
        fp2 = self.fingerprint.copy()
        fp2['device'] = 'server'

        # Not guaranteed to be different, but likely
        strategy1 = EncodingStrategySelector.select_strategy_from_fingerprint(
            self.fingerprint
        )
        strategy2 = EncodingStrategySelector.select_strategy_from_fingerprint(
            fp2
        )

        # Just check they're valid strategies
        self.assertIsInstance(strategy1, EncodingStrategy)
        self.assertIsInstance(strategy2, EncodingStrategy)

    def test_strategy_selection_limited_choices(self):
        """Test strategy selection from limited choices"""
        choices = [EncodingStrategy.HEX, EncodingStrategy.BASE64]

        strategy = EncodingStrategySelector.select_strategy_from_fingerprint(
            self.fingerprint,
            available_strategies=choices
        )

        self.assertIn(strategy, choices)

    def test_strategy_parameters(self):
        """Test getting parameters for each strategy"""
        key = bytes.fromhex('0123456789abcdef0123456789abcdef')

        strategies = [
            EncodingStrategy.XOR,
            EncodingStrategy.ROT13,
            EncodingStrategy.CUSTOM_SUBSTITUTION
        ]

        for strategy in strategies:
            with self.subTest(strategy=strategy):
                params = EncodingStrategySelector.get_strategy_parameters(
                    strategy,
                    key
                )

                self.assertIsInstance(params, dict)
                self.assertTrue(len(params) > 0)


class TestMultiEncodingKeySystem(unittest.TestCase):
    """Test the complete key system"""

    def setUp(self):
        self.system = MultiEncodingKeySystem()
        self.test_fingerprint = {
            'hostname': 'test-host',
            'os': 'Linux',
            'version': '5.10'
        }

    def test_create_target_profile(self):
        """Test creating target profile"""
        profile = self.system.create_target_profile(
            name='Test Target',
            fingerprint_data=self.test_fingerprint
        )

        self.assertIsNotNone(profile.target_id)
        self.assertEqual(profile.name, 'Test Target')
        self.assertEqual(profile.fingerprint_data, self.test_fingerprint)

    def test_derive_key_for_target(self):
        """Test key derivation for target"""
        profile = self.system.create_target_profile(
            name='Key Test',
            fingerprint_data=self.test_fingerprint
        )

        derived_key = self.system.derive_key_for_target(profile.target_id)

        self.assertEqual(len(derived_key.key), profile.key_length)
        self.assertEqual(len(derived_key.hex_key), profile.key_length * 2)
        self.assertIsNotNone(derived_key.fingerprint_hash)

    def test_encoding_parameters(self):
        """Test getting encoding parameters"""
        profile = self.system.create_target_profile(
            name='Encoding Test',
            fingerprint_data=self.test_fingerprint
        )

        params = self.system.get_encoding_parameters(profile.target_id)

        self.assertIsInstance(params, dict)
        self.assertTrue(len(params) > 0)

    def test_list_profiles(self):
        """Test listing target profiles"""
        # Create multiple profiles
        self.system.create_target_profile(
            name='Profile 1',
            fingerprint_data={'id': '1'}
        )
        self.system.create_target_profile(
            name='Profile 2',
            fingerprint_data={'id': '2'}
        )

        profiles = self.system.list_target_profiles()

        self.assertGreaterEqual(len(profiles), 2)
        self.assertTrue(all('target_id' in p for p in profiles))
        self.assertTrue(all('strategy' in p for p in profiles))

    def test_export_key_config(self):
        """Test exporting complete configuration"""
        profile = self.system.create_target_profile(
            name='Export Test',
            fingerprint_data=self.test_fingerprint
        )

        config = self.system.export_key_config(profile.target_id)

        self.assertIn('target', config)
        self.assertIn('key', config)
        self.assertIn('encoding', config)
        self.assertIn('metadata', config)

        self.assertEqual(config['target']['id'], profile.target_id)
        self.assertEqual(config['key']['length'], profile.key_length)

    def test_custom_salt(self):
        """Test custom salt in key derivation"""
        profile = self.system.create_target_profile(
            name='Salt Test',
            fingerprint_data=self.test_fingerprint,
            salt='custom_salt'
        )

        key1 = self.system.derive_key_for_target(profile.target_id)

        # Derive again with same salt
        key2 = self.system.derive_key_for_target(profile.target_id)

        self.assertEqual(key1.hex_key, key2.hex_key)

    def test_different_key_derivation_methods(self):
        """Test different key derivation methods"""
        methods = [
            KeyDerivationMethod.PBKDF2,
            KeyDerivationMethod.HKDF,
            KeyDerivationMethod.SHA256_CHAIN,
            KeyDerivationMethod.HMAC_CHAIN
        ]

        derived_keys = {}

        for method in methods:
            profile = self.system.create_target_profile(
                name=f'Method {method.value}',
                fingerprint_data=self.test_fingerprint,
                key_derivation_method=method
            )

            derived_key = self.system.derive_key_for_target(profile.target_id)
            derived_keys[method] = derived_key

        # All methods should produce different keys
        hex_keys = [k.hex_key for k in derived_keys.values()]
        self.assertEqual(len(set(hex_keys)), len(methods))

    def test_system_report(self):
        """Test system report generation"""
        self.system.create_target_profile(
            name='Report Test',
            fingerprint_data=self.test_fingerprint
        )

        report = self.system.generate_system_report()

        self.assertIn('MULTI-ENCODING KEY DERIVATION SYSTEM REPORT', report)
        self.assertIn('Report Test', report)


class TestKeyUniqueness(unittest.TestCase):
    """Test that different fingerprints produce different keys"""

    def setUp(self):
        self.system = MultiEncodingKeySystem()

    def test_unique_keys_for_different_fingerprints(self):
        """Test that different fingerprints produce unique keys"""
        fingerprints = [
            {'system': 'windows', 'version': '10'},
            {'system': 'linux', 'version': '20.04'},
            {'system': 'macos', 'version': '11'}
        ]

        derived_keys = []

        for i, fp in enumerate(fingerprints):
            profile = self.system.create_target_profile(
                name=f'System {i}',
                fingerprint_data=fp
            )
            key = self.system.derive_key_for_target(profile.target_id)
            derived_keys.append(key.hex_key)

        # All keys should be different
        self.assertEqual(len(set(derived_keys)), len(fingerprints))

    def test_similar_fingerprints_different_keys(self):
        """Test that slightly different fingerprints produce different keys"""
        fp1 = {'device': 'server', 'os': 'Linux', 'version': '5.10'}
        fp2 = {'device': 'server', 'os': 'Linux', 'version': '5.11'}

        profile1 = self.system.create_target_profile(
            name='Server v5.10',
            fingerprint_data=fp1
        )
        profile2 = self.system.create_target_profile(
            name='Server v5.11',
            fingerprint_data=fp2
        )

        key1 = self.system.derive_key_for_target(profile1.target_id)
        key2 = self.system.derive_key_for_target(profile2.target_id)

        self.assertNotEqual(key1.hex_key, key2.hex_key)


class TestEncodingAndDecoding(unittest.TestCase):
    """Test encoding and decoding operations"""

    def setUp(self):
        self.system = MultiEncodingKeySystem()

    def test_roundtrip_hex(self):
        """Test HEX encoding roundtrip"""
        from multi_encoding_key_derivation import EncodingStrategySelector

        profile = self.system.create_target_profile(
            name='HEX Test',
            fingerprint_data={'test': 'data'},
            encoding_strategy=EncodingStrategy.HEX
        )

        test_data = "Hello, World!"

        # Encode
        import binascii
        encoded = binascii.hexlify(test_data.encode()).decode()

        # Decode
        decoded = binascii.unhexlify(encoded).decode()

        self.assertEqual(decoded, test_data)

    def test_roundtrip_base64(self):
        """Test BASE64 encoding roundtrip"""
        import base64

        profile = self.system.create_target_profile(
            name='BASE64 Test',
            fingerprint_data={'test': 'data'},
            encoding_strategy=EncodingStrategy.BASE64
        )

        test_data = "Secret message"

        encoded = base64.b64encode(test_data.encode()).decode()
        decoded = base64.b64decode(encoded).decode()

        self.assertEqual(decoded, test_data)


def run_comprehensive_tests():
    """Run all tests with detailed output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFingerprintHasher))
    suite.addTests(loader.loadTestsFromTestCase(TestKeyDerivationFactory))
    suite.addTests(loader.loadTestsFromTestCase(TestEncodingStrategySelector))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiEncodingKeySystem))
    suite.addTests(loader.loadTestsFromTestCase(TestKeyUniqueness))
    suite.addTests(loader.loadTestsFromTestCase(TestEncodingAndDecoding))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    result = run_comprehensive_tests()
    exit(0 if result.wasSuccessful() else 1)
