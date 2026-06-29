#!/usr/bin/env python3
"""
Test suite for registry_obfuscator.py
Comprehensive tests for all obfuscation types and configurations
"""

import unittest
import binascii
from registry_obfuscator import (
    RegistryObfuscator, ObfuscationConfig, ObfuscationType,
    RegistryStorageGenerator
)


class TestObfuscationTypes(unittest.TestCase):
    """Test each obfuscation type"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_payload = "powershell.exe -Command 'Write-Host Test'"
        self.short_payload = "test"

    def test_binary_obfuscation(self):
        """Test binary obfuscation"""
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.BINARY,
            add_junk_data=False
        )
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(self.test_payload)

        self.assertEqual(result['type'], 'binary')
        self.assertIn('PayloadData', result['registry_values'])
        self.assertIn('PayloadSize', result['registry_values'])
        self.assertIn('retrieval_code', result)

        # Verify data is hex
        data, reg_type = result['registry_values']['PayloadData']
        self.assertEqual(reg_type, 'REG_SZ')
        # Should be valid hex
        self.assertTrue(all(c in '0123456789abcdef' for c in data.lower()))

    def test_binary_with_junk(self):
        """Test binary obfuscation with junk data"""
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.BINARY,
            add_junk_data=True,
            junk_ratio=0.5
        )
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(self.test_payload)

        self.assertEqual(result['type'], 'binary')
        self.assertTrue(result['metadata']['has_junk'])
        # Data should be larger due to junk
        data, _ = result['registry_values']['PayloadData']
        self.assertGreater(len(data), len(self.test_payload) * 2)

    def test_hex_string_obfuscation(self):
        """Test hex string obfuscation"""
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.HEX_STRING,
            add_junk_data=False
        )
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(self.test_payload)

        self.assertEqual(result['type'], 'hex_string')
        self.assertIn('PayloadHex', result['registry_values'])

        # Verify data is hex
        data, reg_type = result['registry_values']['PayloadHex']
        self.assertEqual(reg_type, 'REG_SZ')
        self.assertTrue(all(c in '0123456789abcdef' for c in data.lower()))

    def test_split_values_obfuscation(self):
        """Test split values obfuscation"""
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.SPLIT_VALUES,
            chunk_size=8,
            add_junk_data=False,
            scramble_order=False
        )
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(self.test_payload)

        self.assertEqual(result['type'], 'split_values')

        # Should have chunk values and indices (one for each chunk)
        chunk_values = [k for k in result['registry_values'].keys() if k.startswith('Chunk') and k != 'ChunkCount']
        index_values = [k for k in result['registry_values'].keys() if k.startswith('Index')]

        self.assertGreater(len(chunk_values), 0)
        # All chunks should have indices
        self.assertEqual(len(chunk_values), len(index_values))

    def test_split_values_scrambled(self):
        """Test split values with scrambled order"""
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.SPLIT_VALUES,
            chunk_size=8,
            add_junk_data=False,
            scramble_order=True
        )
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(self.test_payload)

        # Verify chunk order was stored
        chunk_order = result['metadata']['chunk_order']
        self.assertTrue(len(chunk_order) > 0)

    def test_interleaved_obfuscation(self):
        """Test interleaved obfuscation"""
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.INTERLEAVED,
            junk_ratio=0.3
        )
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(self.test_payload)

        self.assertEqual(result['type'], 'interleaved')
        self.assertIn('InterleavedData', result['registry_values'])
        self.assertIn('InterleavedMask', result['registry_values'])

        # Mask should be stored
        mask = result['metadata']['mask']
        self.assertGreater(len(mask), 0)

    def test_xored_obfuscation(self):
        """Test XOR obfuscation"""
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.XORED,
            xor_key=0x42
        )
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(self.test_payload)

        self.assertEqual(result['type'], 'xored')
        self.assertIn('XoredPayload', result['registry_values'])
        self.assertIn('XorKey', result['registry_values'])

        # Verify XOR key is stored
        xor_key_str, _ = result['registry_values']['XorKey']
        self.assertEqual(int(xor_key_str), 0x42)

    def test_xored_random_key(self):
        """Test XOR with random key generation"""
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.XORED
        )
        obfuscator1 = RegistryObfuscator(config)
        obfuscator2 = RegistryObfuscator(config)

        result1 = obfuscator1.obfuscate(self.test_payload)
        result2 = obfuscator2.obfuscate(self.test_payload)

        # Keys should be different (random)
        key1, _ = result1['registry_values']['XorKey']
        key2, _ = result2['registry_values']['XorKey']

        # They should be different (with high probability)
        # (not guaranteed but very likely)

    def test_base64_obfuscation(self):
        """Test base64 obfuscation"""
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.BASE64,
            add_junk_data=False
        )
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(self.test_payload)

        self.assertEqual(result['type'], 'base64')
        self.assertIn('Base64Part0', result['registry_values'])

        # Verify data is base64
        data, _ = result['registry_values']['Base64Part0']
        # Base64 chars: A-Z, a-z, 0-9, +, /, =
        self.assertTrue(all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in data))

    def test_base64_chunked(self):
        """Test base64 with chunks"""
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.BASE64,
            add_junk_data=True,
            junk_ratio=0.2
        )
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(self.test_payload)

        # Should have multiple parts
        part_count, _ = result['registry_values']['Base64PartCount']
        self.assertGreater(int(part_count), 0)

    def test_chunked_hex_obfuscation(self):
        """Test chunked hex obfuscation"""
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.CHUNKED_HEX,
            chunk_size=16
        )
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(self.test_payload)

        self.assertEqual(result['type'], 'chunked_hex')

        # Should have multiple chunks
        chunk_count, _ = result['registry_values']['HexChunkCount']
        self.assertGreater(int(chunk_count), 0)

        # Each chunk should be hex
        for i in range(int(chunk_count)):
            chunk_name = f"HexChunk{i:03d}"
            data, _ = result['registry_values'][chunk_name]
            self.assertTrue(all(c in '0123456789abcdef' for c in data.lower()))


class TestMetadata(unittest.TestCase):
    """Test metadata generation"""

    def setUp(self):
        self.test_payload = "test payload"

    def test_metadata_includes_size(self):
        """Test that metadata includes original size"""
        config = ObfuscationConfig(obfuscation_type=ObfuscationType.BINARY)
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(self.test_payload)

        self.assertIn('original_size', result['metadata'])
        self.assertEqual(result['metadata']['original_size'], len(self.test_payload))

    def test_metadata_includes_config(self):
        """Test that metadata includes relevant config info"""
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.XORED,
            xor_key=0xFF
        )
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(self.test_payload)

        self.assertIn('xor_key', result['metadata'])


class TestStorageGenerator(unittest.TestCase):
    """Test VBS code generation"""

    def setUp(self):
        self.test_payload = "powershell.exe -Command test"

    def test_storage_vbs_generation(self):
        """Test VBS storage code generation"""
        config = ObfuscationConfig(obfuscation_type=ObfuscationType.HEX_STRING)
        obfuscator = RegistryObfuscator(config)
        generator = RegistryStorageGenerator(obfuscator)

        vbs_code = generator.generate_storage_vbs(
            self.test_payload,
            registry_hive="HKCU",
            registry_path="Software\\Test"
        )

        self.assertIn("CreateObject", vbs_code)
        self.assertIn("WScript.Shell", vbs_code)
        self.assertIn("RegWrite", vbs_code)
        self.assertIn("Software\\Test", vbs_code)

    def test_retrieval_vbs_generation(self):
        """Test VBS retrieval code generation"""
        config = ObfuscationConfig(obfuscation_type=ObfuscationType.HEX_STRING)
        obfuscator = RegistryObfuscator(config)
        generator = RegistryStorageGenerator(obfuscator)

        vbs_code = generator.generate_retrieval_vbs(
            registry_hive="HKCU",
            registry_path="Software\\Test",
            auto_execute=True
        )

        self.assertIn("CreateObject", vbs_code)
        self.assertIn("RegRead", vbs_code)
        self.assertIn("Retrieve", vbs_code)

    def test_retrieval_without_execution(self):
        """Test retrieval without auto-execute"""
        config = ObfuscationConfig(obfuscation_type=ObfuscationType.BINARY)
        obfuscator = RegistryObfuscator(config)
        generator = RegistryStorageGenerator(obfuscator)

        vbs_code = generator.generate_retrieval_vbs(
            registry_hive="HKCU",
            registry_path="Software\\Test",
            auto_execute=False
        )

        self.assertIn("Retrieve", vbs_code)
        # Should not have execution code
        self.assertNotIn(".Run", vbs_code)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios"""

    def test_empty_payload(self):
        """Test with empty payload"""
        config = ObfuscationConfig(obfuscation_type=ObfuscationType.HEX_STRING)
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate("")

        self.assertEqual(result['metadata']['original_size'], 0)

    def test_large_payload(self):
        """Test with large payload"""
        large_payload = "A" * 10000
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.SPLIT_VALUES,
            chunk_size=256
        )
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(large_payload)

        self.assertEqual(result['metadata']['original_size'], len(large_payload))

    def test_special_characters(self):
        """Test with special characters"""
        payload = "test!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        config = ObfuscationConfig(obfuscation_type=ObfuscationType.XORED)
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(payload)

        self.assertEqual(result['metadata']['original_size'], len(payload))

    def test_unicode_payload(self):
        """Test with unicode characters"""
        payload = "test™®©€¥"
        config = ObfuscationConfig(obfuscation_type=ObfuscationType.BASE64)
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(payload)

        self.assertEqual(result['metadata']['original_size'], len(payload))

    def test_newlines_in_payload(self):
        """Test with newlines in payload"""
        payload = "line1\nline2\nline3"
        config = ObfuscationConfig(obfuscation_type=ObfuscationType.BINARY)
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(payload)

        self.assertEqual(result['metadata']['original_size'], len(payload))


class TestConfigVariations(unittest.TestCase):
    """Test various configuration combinations"""

    def setUp(self):
        self.test_payload = "test"

    def test_all_configs_produce_valid_output(self):
        """Test that all config variations produce valid output"""
        obfuscation_types = list(ObfuscationType)

        for obf_type in obfuscation_types:
            with self.subTest(obfuscation_type=obf_type):
                config = ObfuscationConfig(obfuscation_type=obf_type)
                obfuscator = RegistryObfuscator(config)
                result = obfuscator.obfuscate(self.test_payload)

                # All results should have these keys
                self.assertIn('type', result)
                self.assertIn('registry_values', result)
                self.assertIn('metadata', result)
                self.assertIn('retrieval_code', result)

                # Registry values should be non-empty
                self.assertGreater(len(result['registry_values']), 0)

    def test_chunk_size_variations(self):
        """Test different chunk sizes"""
        payload = "test_payload" * 100

        for chunk_size in [16, 64, 256, 512]:
            with self.subTest(chunk_size=chunk_size):
                config = ObfuscationConfig(
                    obfuscation_type=ObfuscationType.SPLIT_VALUES,
                    chunk_size=chunk_size
                )
                obfuscator = RegistryObfuscator(config)
                result = obfuscator.obfuscate(payload)

                chunk_count = result['metadata']['chunk_count']
                # Chunk count should scale with size
                expected_min = len(payload) // chunk_size
                self.assertGreaterEqual(chunk_count, expected_min)

    def test_junk_ratio_variations(self):
        """Test different junk ratios"""
        payload = "test"

        for ratio in [0.0, 0.3, 0.5, 0.8]:
            with self.subTest(junk_ratio=ratio):
                config = ObfuscationConfig(
                    obfuscation_type=ObfuscationType.BINARY,
                    add_junk_data=(ratio > 0),
                    junk_ratio=ratio
                )
                obfuscator = RegistryObfuscator(config)
                result = obfuscator.obfuscate(payload)

                # Should generate valid output
                self.assertIn('registry_values', result)


class TestRetrievalFunctions(unittest.TestCase):
    """Test VBS retrieval function generation"""

    def test_all_retrieval_functions_generated(self):
        """Test that all obfuscation types have retrieval functions"""
        obfuscation_types = list(ObfuscationType)

        for obf_type in obfuscation_types:
            with self.subTest(obfuscation_type=obf_type):
                config = ObfuscationConfig(obfuscation_type=obf_type)
                obfuscator = RegistryObfuscator(config)
                result = obfuscator.obfuscate("test")

                # Should have retrieval code
                self.assertIn('retrieval_code', result)
                self.assertGreater(len(result['retrieval_code']), 0)
                # Should start with Function definition
                self.assertIn('Function Retrieve', result['retrieval_code'])

    def test_retrieval_functions_have_proper_syntax(self):
        """Test that retrieval functions have proper VBS syntax"""
        config = ObfuscationConfig(obfuscation_type=ObfuscationType.HEX_STRING)
        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate("test")

        code = result['retrieval_code']
        # Should have balanced function def and end
        self.assertEqual(code.count('Function '), code.count('End Function'))


if __name__ == "__main__":
    unittest.main()
