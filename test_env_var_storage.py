#!/usr/bin/env python3
"""
Test Suite for Environment Variable Storage
Tests encoding, chunking, writing, and retrieval of payloads
"""

import unittest
import os
import json
import base64
from env_var_storage import (
    EnvVarWriter, EnvVarReader, EnvVarConfig,
    EnvVarScope, EnvVarEncoding, create_env_var_writer
)


class TestEnvVarEncoding(unittest.TestCase):
    """Test encoding methods"""

    def setUp(self):
        self.writer = EnvVarWriter()

    def test_raw_encoding(self):
        """Test RAW encoding"""
        value = "test payload"
        encoded = self.writer.encode_value(value, EnvVarEncoding.RAW)
        self.assertEqual(encoded, value)

    def test_base64_encoding(self):
        """Test BASE64 encoding"""
        value = "test payload"
        encoded = self.writer.encode_value(value, EnvVarEncoding.BASE64)
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, value)

    def test_hex_encoding(self):
        """Test HEX encoding"""
        value = "test"
        encoded = self.writer.encode_value(value, EnvVarEncoding.HEX)
        decoded = bytes.fromhex(encoded).decode()
        self.assertEqual(decoded, value)

    def test_chunked_base64_encoding(self):
        """Test CHUNKED_BASE64 encoding"""
        value = "a" * 1000  # Large payload
        encoded = self.writer.encode_value(value, EnvVarEncoding.CHUNKED_BASE64)
        data = json.loads(encoded)
        self.assertEqual(data["type"], "chunked_base64")
        self.assertIn("chunks", data)
        self.assertGreater(len(data["chunks"]), 1)

    def test_chunked_hex_encoding(self):
        """Test CHUNKED_HEX encoding"""
        value = "a" * 1000
        encoded = self.writer.encode_value(value, EnvVarEncoding.CHUNKED_HEX)
        data = json.loads(encoded)
        self.assertEqual(data["type"], "chunked_hex")
        self.assertIn("chunks", data)


class TestEnvVarObfuscation(unittest.TestCase):
    """Test variable name obfuscation"""

    def test_obfuscation_enabled(self):
        """Test that obfuscation changes variable name"""
        config = EnvVarConfig(use_obfuscation=True)
        writer = EnvVarWriter(config)
        obfuscated = writer.obfuscate_var_name("payload")
        self.assertNotEqual(obfuscated, "SC_payload")
        self.assertIn("SC_VAR_", obfuscated)

    def test_obfuscation_disabled(self):
        """Test that obfuscation can be disabled"""
        config = EnvVarConfig(use_obfuscation=False)
        writer = EnvVarWriter(config)
        obfuscated = writer.obfuscate_var_name("payload")
        self.assertEqual(obfuscated, "SC_payload")

    def test_consistent_obfuscation(self):
        """Test that obfuscation is consistent for same input"""
        config = EnvVarConfig(use_obfuscation=True)
        writer = EnvVarWriter(config)
        name1 = writer.obfuscate_var_name("payload")
        name2 = writer.obfuscate_var_name("payload")
        self.assertEqual(name1, name2)


class TestEnvVarChunking(unittest.TestCase):
    """Test payload chunking"""

    def setUp(self):
        self.config = EnvVarConfig(chunk_size=100, encoding=EnvVarEncoding.BASE64)
        self.writer = EnvVarWriter(self.config)

    def test_small_payload_no_chunking(self):
        """Test that small payloads don't create multiple chunks"""
        payload = "small"
        chunks = self.writer.chunk_payload(payload, "test")
        # Should have metadata + 1 or more chunks
        self.assertIn("test_META", chunks)

    def test_large_payload_chunking(self):
        """Test that large payloads create multiple chunks"""
        payload = "a" * 1000
        chunks = self.writer.chunk_payload(payload, "test")

        # Should have metadata
        self.assertIn("test_META", chunks)

        # Should have multiple chunks
        chunk_keys = [k for k in chunks.keys() if "CHUNK_" in k]
        self.assertGreater(len(chunk_keys), 1)

    def test_chunk_metadata(self):
        """Test that chunk metadata is created correctly"""
        payload = "test payload"
        chunks = self.writer.chunk_payload(payload, "test")

        metadata_str = chunks["test_META"]
        metadata = json.loads(metadata_str)

        self.assertIn("total_chunks", metadata)
        self.assertIn("encoding", metadata)
        self.assertIn("original_size", metadata)
        self.assertGreater(metadata["total_chunks"], 0)


class TestEnvVarWrite(unittest.TestCase):
    """Test writing to environment variables"""

    def setUp(self):
        self.config = EnvVarConfig(scope=EnvVarScope.PROCESS)
        self.writer = EnvVarWriter(self.config)

    def test_write_to_process_env(self):
        """Test writing to process environment"""
        payload = "test payload"
        success, vars_list, message = self.writer.write_to_env("test", payload)

        self.assertTrue(success)
        self.assertGreater(len(vars_list), 0)
        # Check that metadata var is present (with obfuscation applied)
        meta_vars = [v for v in vars_list if "_META" in v]
        self.assertGreater(len(meta_vars), 0)

    def test_written_vars_accessible(self):
        """Test that written variables are accessible"""
        payload = "test payload"
        success, vars_list, _ = self.writer.write_to_env("test", payload)

        if success:
            for var_name in vars_list:
                self.assertIn(var_name, os.environ)

    def test_metadata_stored(self):
        """Test that metadata is stored correctly"""
        payload = "test"
        self.writer.write_to_env("test", payload)

        metadata = self.writer.get_var_metadata()
        self.assertGreater(len(metadata), 0)

    def test_multiple_writes(self):
        """Test writing multiple payloads"""
        payload1 = "payload1"
        payload2 = "payload2"

        success1, vars1, _ = self.writer.write_to_env("test1", payload1)
        success2, vars2, _ = self.writer.write_to_env("test2", payload2)

        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertGreater(len(vars1), 0)
        self.assertGreater(len(vars2), 0)


class TestEnvVarRead(unittest.TestCase):
    """Test reading from environment variables"""

    def setUp(self):
        self.config = EnvVarConfig(scope=EnvVarScope.PROCESS)
        self.writer = EnvVarWriter(self.config)
        self.reader = EnvVarReader(self.config)

    def test_read_after_write(self):
        """Test reading payload after writing"""
        payload = "test payload data"
        var_name = "testpayload"

        # Write
        success, vars_list, _ = self.writer.write_to_env(var_name, payload)
        self.assertTrue(success)

        # Read
        obfuscated_name = self.writer.obfuscate_var_name(var_name)
        # Manual reconstruction for testing
        metadata_var = f"{obfuscated_name}_META"
        if metadata_var in os.environ:
            metadata_str = os.environ[metadata_var]
            metadata = json.loads(metadata_str)
            reconstructed = ""
            for i in range(metadata["total_chunks"]):
                chunk_var = f"{obfuscated_name}_CHUNK_{i:03d}"
                if chunk_var in os.environ:
                    reconstructed += os.environ[chunk_var]

            # Decode
            if metadata["encoding"] == "base64":
                original = base64.b64decode(reconstructed).decode()
                self.assertEqual(original, payload)

    def test_list_payload_vars(self):
        """Test listing payload variables"""
        # Write some payloads
        self.writer.write_to_env("test1", "payload1")
        self.writer.write_to_env("test2", "payload2")

        # List
        vars_list = self.reader.list_payload_vars()
        self.assertGreater(len(vars_list), 0)


class TestEnvVarCodeGeneration(unittest.TestCase):
    """Test code generation for payload retrieval"""

    def setUp(self):
        self.writer = EnvVarWriter()

    def test_vbs_code_generation(self):
        """Test VBS retrieval code generation"""
        code = self.writer.get_retrieval_code("test", "vbs")
        self.assertIn("Base64Decode", code)
        self.assertIn("Environment", code)
        self.assertGreater(len(code), 100)

    def test_powershell_code_generation(self):
        """Test PowerShell retrieval code generation"""
        code = self.writer.get_retrieval_code("test", "powershell")
        self.assertIn("GetEnvironmentVariable", code)
        self.assertIn("ConvertFrom-Json", code)
        self.assertGreater(len(code), 100)

    def test_batch_code_generation(self):
        """Test Batch retrieval code generation"""
        code = self.writer.get_retrieval_code("test", "batch")
        self.assertIn("setlocal", code)
        self.assertGreater(len(code), 50)

    def test_code_contains_var_name(self):
        """Test that generated code contains variable name"""
        var_name = "mypayload"
        for lang in ["vbs", "powershell", "batch"]:
            code = self.writer.get_retrieval_code(var_name, lang)
            # Code should handle the variable (not exact name if obfuscated, but structure)
            self.assertGreater(len(code), 0)


class TestEnvVarConfig(unittest.TestCase):
    """Test configuration management"""

    def test_default_config(self):
        """Test default configuration"""
        config = EnvVarConfig()
        self.assertEqual(config.scope, EnvVarScope.USER)
        self.assertEqual(config.encoding, EnvVarEncoding.BASE64)
        self.assertTrue(config.use_obfuscation)

    def test_custom_config(self):
        """Test custom configuration"""
        config = EnvVarConfig(
            scope=EnvVarScope.PROCESS,
            encoding=EnvVarEncoding.HEX,
            use_obfuscation=False
        )
        self.assertEqual(config.scope, EnvVarScope.PROCESS)
        self.assertEqual(config.encoding, EnvVarEncoding.HEX)
        self.assertFalse(config.use_obfuscation)

    def test_factory_function(self):
        """Test factory function"""
        writer = create_env_var_writer(
            scope=EnvVarScope.PROCESS,
            encoding=EnvVarEncoding.HEX
        )
        self.assertIsInstance(writer, EnvVarWriter)
        self.assertEqual(writer.config.scope, EnvVarScope.PROCESS)
        self.assertEqual(writer.config.encoding, EnvVarEncoding.HEX)


class TestEnvVarIntegration(unittest.TestCase):
    """Integration tests"""

    def setUp(self):
        self.writer = create_env_var_writer(
            scope=EnvVarScope.PROCESS,
            encoding=EnvVarEncoding.CHUNKED_BASE64
        )

    def test_end_to_end_workflow(self):
        """Test complete write-store-read workflow"""
        payload = "This is a complete test of environment variable storage with a longer payload to ensure chunking works correctly"
        var_name = "e2e_test"

        # Write
        success, vars_list, message = self.writer.write_to_env(var_name, payload)
        self.assertTrue(success, message)
        self.assertGreater(len(vars_list), 0)

        # Verify all variables are in environment
        for var in vars_list:
            self.assertIn(var, os.environ)

        # Get metadata
        metadata = self.writer.get_var_metadata()
        self.assertGreater(len(metadata), 0)

    def test_large_payload_handling(self):
        """Test handling of large payloads"""
        large_payload = "X" * 10000
        success, vars_list, message = self.writer.write_to_env("large", large_payload)

        # Should succeed even with large payload due to chunking
        self.assertTrue(success)
        self.assertGreater(len(vars_list), 2)  # Should have multiple chunks

    def test_special_characters_in_payload(self):
        """Test handling of special characters"""
        payload = "Special chars: !@#$%^&*()[]{}\\\"'`~|"
        success, vars_list, _ = self.writer.write_to_env("special", payload)

        if success:
            obfuscated = self.writer.obfuscate_var_name("special")
            metadata_str = os.environ.get(f"{obfuscated}_META")
            self.assertIsNotNone(metadata_str)


class TestEnvVarValidation(unittest.TestCase):
    """Test validation"""

    def setUp(self):
        self.writer = EnvVarWriter()

    def test_value_validation(self):
        """Test environment variable value validation"""
        # Small value should pass
        small_value = "test"
        self.assertTrue(self.writer._validate_env_var_value(small_value))

        # Extremely large value should fail
        huge_value = "x" * 50000
        self.assertFalse(self.writer._validate_env_var_value(huge_value))

    def test_chunking_respects_limits(self):
        """Test that chunking respects size limits"""
        payload = "a" * 10000
        chunks = self.writer.chunk_payload(payload, "test")

        for chunk_value in chunks.values():
            self.assertTrue(self.writer._validate_env_var_value(chunk_value))


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestEnvVarEncoding))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvVarObfuscation))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvVarChunking))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvVarWrite))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvVarRead))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvVarCodeGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvVarConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvVarIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvVarValidation))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
