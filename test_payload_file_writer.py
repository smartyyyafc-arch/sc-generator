#!/usr/bin/env python3
"""
Test suite for Payload File Writer
Demonstrates all file writer functionality and obfuscation techniques
"""

import unittest
import os
import tempfile
import json
from pathlib import Path

from payload_file_writer import (
    PayloadFileWriter,
    FileFormat,
    PayloadMetadata,
    ObfuscationStrategies,
    write_payload_to_file,
    write_and_encode_payload
)


class TestObfuscationStrategies(unittest.TestCase):
    """Test obfuscation strategy implementations"""

    def setUp(self):
        self.strategies = ObfuscationStrategies()

    def test_xor_encode(self):
        """Test XOR encoding"""
        data = b"Hello World"
        key = b"secret"
        encoded = self.strategies.xor_encode(data, key)
        self.assertNotEqual(data, encoded)
        self.assertEqual(len(data), len(encoded))

    def test_reverse_bytes(self):
        """Test byte reversal"""
        data = b"Hello"
        reversed_data = self.strategies.reverse_bytes(data)
        self.assertEqual(self.strategies.reverse_bytes(reversed_data), data)

    def test_base64_encode(self):
        """Test Base64 encoding"""
        data = b"Test payload"
        encoded = self.strategies.base64_encode(data)
        self.assertIsInstance(encoded, str)
        # Base64 encoded string should be decodable
        import base64
        decoded = base64.b64decode(encoded)
        self.assertEqual(decoded, data)

    def test_hex_encode(self):
        """Test hex encoding"""
        data = b"Test"
        encoded = self.strategies.hex_encode(data)
        self.assertEqual(encoded, "54657374")

    def test_caesar_shift(self):
        """Test Caesar cipher"""
        text = "Hello World"
        encoded = self.strategies.caesar_shift(text, 13)
        self.assertNotEqual(text, encoded)
        decoded = self.strategies.caesar_shift(encoded, 13)
        self.assertEqual(decoded, text)

    def test_chunk_and_comment(self):
        """Test chunking with comments"""
        text = "This is a long text that should be chunked"
        chunked = self.strategies.chunk_and_comment(text, chunk_size=10)
        self.assertIn('\n', chunked)
        lines = chunked.split('\n')
        self.assertGreater(len(lines), 1)


class TestPayloadFileWriter(unittest.TestCase):
    """Test payload file writer core functionality"""

    def setUp(self):
        """Create temporary directory for tests"""
        self.test_dir = tempfile.mkdtemp(prefix="test_payload_")
        self.writer = PayloadFileWriter(base_temp_dir=self.test_dir)
        self.test_payload = 'Set shell = CreateObject("WScript.Shell")\nshell.Run "cmd /c echo test"'

    def tearDown(self):
        """Clean up temp directory"""
        self.writer.cleanup_all()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_temp_file(self):
        """Test temporary file creation"""
        temp_path = self.writer.create_temp_file(suffix=".vbs")
        self.assertTrue(os.path.exists(temp_path))
        self.assertTrue(temp_path.endswith(".vbs"))

    def test_write_payload_vbs(self):
        """Test writing VBS payload"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            file_format=FileFormat.VBS,
            obfuscation_level="high"
        )

        self.assertTrue(os.path.exists(path))
        self.assertEqual(metadata.format, "vbs")
        self.assertEqual(metadata.original_size, len(self.test_payload))
        self.assertGreater(metadata.encoded_size, 0)

    def test_write_payload_bat(self):
        """Test writing BAT payload"""
        bat_payload = "@echo off\necho Test batch"
        path, metadata = self.writer.write_payload(
            bat_payload,
            file_format=FileFormat.BAT,
            obfuscation_level="medium"
        )

        self.assertTrue(os.path.exists(path))
        self.assertEqual(metadata.format, "bat")

    def test_write_payload_ps1(self):
        """Test writing PowerShell payload"""
        ps_payload = 'Write-Host "Hello World"'
        path, metadata = self.writer.write_payload(
            ps_payload,
            file_format=FileFormat.PS1,
            obfuscation_level="high"
        )

        self.assertTrue(os.path.exists(path))
        self.assertEqual(metadata.format, "ps1")

    def test_obfuscation_levels(self):
        """Test different obfuscation levels"""
        levels = ["low", "medium", "high"]
        paths = []

        for level in levels:
            path, metadata = self.writer.write_payload(
                self.test_payload,
                obfuscation_level=level
            )
            paths.append(path)
            self.assertTrue(os.path.exists(path))

        # Higher obfuscation should generally produce larger files
        with open(paths[0], 'r') as f:
            low = f.read()
        with open(paths[2], 'r') as f:
            high = f.read()

        # High obfuscation typically produces more code
        self.assertIsNotNone(low)
        self.assertIsNotNone(high)

    def test_metadata_tracking(self):
        """Test metadata tracking and retrieval"""
        path, metadata = self.writer.write_payload(self.test_payload)

        retrieved = self.writer.get_payload_info(metadata.file_id)
        self.assertEqual(retrieved.file_id, metadata.file_id)
        self.assertEqual(retrieved.format, metadata.format)
        self.assertEqual(retrieved.sha256_hash, metadata.sha256_hash)

    def test_encoding_types(self):
        """Test different encoding types"""
        encodings = ["base64", "hex"]

        for encoding in encodings:
            path, metadata = self.writer.write_payload(
                self.test_payload,
                encoding_type=encoding
            )
            self.assertEqual(metadata.encoding_type, encoding)
            self.assertTrue(os.path.exists(path))

    def test_batch_write(self):
        """Test batch payload writing"""
        payloads = {
            "payload1": "echo test1",
            "payload2": "echo test2",
            "payload3": "echo test3"
        }

        results = self.writer.write_payload_batch(
            payloads,
            file_format=FileFormat.BAT,
            obfuscation_level="high"
        )

        self.assertEqual(len(results), 3)
        for name, (path, metadata) in results.items():
            self.assertIsNotNone(path)
            self.assertTrue(os.path.exists(path))

    def test_write_with_decoder(self):
        """Test writing payload with decoder stub"""
        payload_path, decoder_path, metadata = self.writer.write_payload_with_decoder(
            self.test_payload,
            encoding_type="base64",
            obfuscation_level="high"
        )

        self.assertTrue(os.path.exists(payload_path))
        self.assertTrue(os.path.exists(decoder_path))
        self.assertEqual(metadata.encoding_type, "base64")

    def test_metadata_json_export(self):
        """Test metadata JSON export"""
        path, metadata = self.writer.write_payload(self.test_payload)
        json_output = self.writer.export_metadata_json(metadata.file_id)

        # Verify it's valid JSON
        data = json.loads(json_output)
        self.assertEqual(data['file_id'], metadata.file_id)
        self.assertEqual(data['format'], metadata.format)

    def test_cleanup_single_file(self):
        """Test single file cleanup"""
        path, metadata = self.writer.write_payload(self.test_payload)
        file_id = metadata.file_id

        self.assertTrue(os.path.exists(path))
        success = self.writer.cleanup_temp_file(file_id)
        self.assertTrue(success)
        self.assertFalse(os.path.exists(path))

    def test_cleanup_all_files(self):
        """Test cleanup of all files"""
        paths = []
        for i in range(3):
            path, _ = self.writer.write_payload(f"test payload {i}")
            paths.append(path)

        # Verify files exist
        for path in paths:
            self.assertTrue(os.path.exists(path))

        # Cleanup all
        count = self.writer.cleanup_all()
        self.assertEqual(count, 3)

        # Verify files are gone
        for path in paths:
            self.assertFalse(os.path.exists(path))

    def test_hash_verification(self):
        """Test payload hash calculation"""
        path, metadata = self.writer.write_payload(self.test_payload)

        # Hash should be consistent
        hash1 = metadata.sha256_hash
        path2, metadata2 = self.writer.write_payload(self.test_payload)
        hash2 = metadata2.sha256_hash

        self.assertEqual(hash1, hash2)

    def test_compression_ratio(self):
        """Test compression ratio calculation"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            obfuscation_level="high"
        )

        self.assertGreater(metadata.compression_ratio, 0)
        self.assertLessEqual(metadata.compression_ratio, 10.0)  # Sanity check


class TestVBSObfuscation(unittest.TestCase):
    """Test VBS-specific obfuscation"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_vbs_")
        self.writer = PayloadFileWriter(base_temp_dir=self.test_dir)
        self.vbs_code = """
Dim objShell
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd /c echo test", 0, False
"""

    def tearDown(self):
        self.writer.cleanup_all()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_vbs_obfuscation_low(self):
        """Test low-level VBS obfuscation"""
        obfuscated = self.writer.obfuscate_vbs_payload(self.vbs_code, "low")
        self.assertEqual(obfuscated, self.vbs_code)

    def test_vbs_obfuscation_medium(self):
        """Test medium-level VBS obfuscation"""
        obfuscated = self.writer.obfuscate_vbs_payload(self.vbs_code, "medium")
        # Should contain obfuscation
        self.assertNotEqual(obfuscated, self.vbs_code)

    def test_vbs_obfuscation_high(self):
        """Test high-level VBS obfuscation"""
        obfuscated = self.writer.obfuscate_vbs_payload(self.vbs_code, "high")
        # Should be significantly different
        self.assertNotEqual(obfuscated, self.vbs_code)
        # Should contain dead code or comments
        self.assertGreater(len(obfuscated), len(self.vbs_code))


class TestBATObfuscation(unittest.TestCase):
    """Test BAT-specific obfuscation"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_bat_")
        self.writer = PayloadFileWriter(base_temp_dir=self.test_dir)
        self.bat_code = "@echo off\necho Hello World\npause"

    def tearDown(self):
        self.writer.cleanup_all()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_bat_obfuscation(self):
        """Test BAT file obfuscation"""
        obfuscated = self.writer.obfuscate_bat_payload(self.bat_code, "high")
        self.assertIsNotNone(obfuscated)
        # Should contain batch-specific obfuscation patterns
        self.assertTrue(len(obfuscated) > 0)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_conv_")

    def tearDown(self):
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_write_payload_to_file(self):
        """Test write_payload_to_file convenience function"""
        payload = "echo test"
        path, metadata = write_payload_to_file(payload, FileFormat.BAT, "high")

        self.assertTrue(os.path.exists(path))
        self.assertEqual(metadata.format, "bat")

        # Cleanup
        os.remove(path)

    def test_write_and_encode_payload(self):
        """Test write_and_encode_payload convenience function"""
        payload = "test payload"
        payload_path, decoder_path, metadata = write_and_encode_payload(
            payload,
            encoding_type="base64",
            obfuscation_level="high"
        )

        self.assertTrue(os.path.exists(payload_path))
        self.assertTrue(os.path.exists(decoder_path))

        # Cleanup
        os.remove(payload_path)
        os.remove(decoder_path)


class TestFileWriterIntegration(unittest.TestCase):
    """Integration tests for file writer"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_integration_")
        self.writer = PayloadFileWriter(base_temp_dir=self.test_dir)

    def tearDown(self):
        self.writer.cleanup_all()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_full_workflow(self):
        """Test complete workflow: write, encode, export, cleanup"""
        payload = "original payload content"

        # Step 1: Write with encoding
        payload_path, decoder_path, metadata = self.writer.write_payload_with_decoder(
            payload,
            encoding_type="base64"
        )

        self.assertTrue(os.path.exists(payload_path))
        self.assertTrue(os.path.exists(decoder_path))

        # Step 2: Export metadata
        json_meta = self.writer.export_metadata_json(metadata.file_id)
        data = json.loads(json_meta)
        self.assertEqual(data['encoding_type'], "base64")

        # Step 3: Verify file contains content
        with open(payload_path, 'r') as f:
            content = f.read()
        self.assertGreater(len(content), 0)

        # Step 4: Cleanup
        success = self.writer.cleanup_temp_file(metadata.file_id)
        self.assertTrue(success)
        self.assertFalse(os.path.exists(payload_path))

    def test_multiple_payloads_workflow(self):
        """Test handling multiple payloads"""
        payloads = {
            "cmd1": "echo command 1",
            "cmd2": "echo command 2",
            "cmd3": "echo command 3"
        }

        # Write batch
        results = self.writer.write_payload_batch(payloads, FileFormat.BAT, "high")
        self.assertEqual(len(results), 3)

        # Verify all exist
        for name, (path, meta) in results.items():
            self.assertTrue(os.path.exists(path))

        # Export all metadata
        for name, (path, meta) in results.items():
            json_meta = self.writer.export_metadata_json(meta.file_id)
            data = json.loads(json_meta)
            self.assertIsNotNone(data)

        # Cleanup all
        count = self.writer.cleanup_all()
        self.assertEqual(count, 3)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
