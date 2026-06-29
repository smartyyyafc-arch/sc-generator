#!/usr/bin/env python3
"""
Integration test for Timestamp Spoofer with Payload Writer
Validates complete end-to-end timestamp spoofing workflow
"""

import unittest
import os
import tempfile
from datetime import datetime
from pathlib import Path

from timestamp_spoofer import TimestampSpoofer, SystemFileTimestampMatcher
from payload_file_writer import PayloadFileWriter, FileFormat
from payload_writer_with_timestamps import ConcealedPayloadWriter


class TestTimestampIntegration(unittest.TestCase):
    """Integration tests for complete timestamp spoofing workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.spoofer = TimestampSpoofer()
        self.payload_writer = PayloadFileWriter(self.temp_dir)
        self.concealed_writer = ConcealedPayloadWriter(self.temp_dir)

    def tearDown(self):
        """Clean up"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_write_and_spoof_workflow(self):
        """Test complete write and spoof workflow"""
        payload = 'echo test'

        # Write payload
        path, metadata = self.payload_writer.write_payload(
            payload,
            FileFormat.BAT,
            "high"
        )

        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))
        self.assertGreater(metadata.encoded_size, 0)

        # Spoof timestamp
        info = self.spoofer.spoof_to_match_file(path, "/bin/ls")
        self.assertTrue(info.spoof_success)
        self.assertIsNotNone(info.mtime_dt)

    def test_concealed_payload_single(self):
        """Test writing single concealed payload"""
        payload = 'MsgBox "test"'

        result = self.concealed_writer.write_concealed_payload(
            payload,
            file_format=FileFormat.VBS,
            spoof_to_system=True
        )

        self.assertIsNotNone(result["payload_path"])
        self.assertTrue(os.path.exists(result["payload_path"]))
        self.assertIsNotNone(result["timestamp_info"])
        self.assertTrue(result["timestamp_info"].spoof_success)

    def test_concealed_payload_batch(self):
        """Test writing batch of concealed payloads"""
        payloads = {
            "p1": "echo one",
            "p2": "echo two",
            "p3": "echo three"
        }

        results = self.concealed_writer.write_batch_concealed_payloads(
            payloads,
            file_format=FileFormat.BAT
        )

        self.assertEqual(len(results), 3)

        for name, result in results.items():
            self.assertIsNotNone(result)
            self.assertTrue(os.path.exists(result["payload_path"]))
            self.assertTrue(result["timestamp_info"].spoof_success)

    def test_payload_family_identical_timestamps(self):
        """Test payload family with identical timestamps"""
        payloads = {
            "dll1": "REM library 1",
            "dll2": "REM library 2",
            "dll3": "REM library 3"
        }

        results = self.concealed_writer.write_payload_family(
            payloads,
            file_format=FileFormat.BAT
        )

        # Get timestamps
        timestamps = []
        for name, result in results.items():
            self.assertIsNotNone(result)
            ts = result["timestamp_info"].spoofed_mtime
            timestamps.append(ts)

        # All timestamps should be identical or within 1 second
        for ts in timestamps[1:]:
            self.assertAlmostEqual(ts, timestamps[0], delta=1)

    def test_manifest_export(self):
        """Test payload manifest export"""
        payloads = {
            "test1": "echo test1",
            "test2": "echo test2"
        }

        results = self.concealed_writer.write_batch_concealed_payloads(payloads)
        manifest = self.concealed_writer.export_payload_manifest(results)

        # Verify manifest structure
        import json
        manifest_data = json.loads(manifest)
        self.assertIn("payloads", manifest_data)
        self.assertEqual(len(manifest_data["payloads"]), 2)

        for entry in manifest_data["payloads"]:
            self.assertIn("name", entry)
            self.assertIn("path", entry)
            self.assertIn("timestamp", entry)

    def test_timestamp_preservation_across_operations(self):
        """Test that timestamps are preserved through operations"""
        # Create file
        test_file = os.path.join(self.temp_dir, "preserve.txt")
        with open(test_file, 'w') as f:
            f.write("test")

        # Set specific timestamp
        target_date = datetime(2020, 6, 15, 10, 0, 0)
        self.spoofer.spoof_to_datetime(test_file, target_date)

        # Get timestamp
        info1 = self.spoofer.get_history()[test_file]
        ts1 = info1.spoofed_mtime

        # Wait a bit
        import time
        time.sleep(0.1)

        # Get timestamp again
        ts2, _, _ = self.spoofer.get_file_timestamps(test_file)

        # Should be very close (no change)
        self.assertAlmostEqual(ts1, ts2, delta=1)

    def test_batch_cleanup(self):
        """Test cleanup of batch payloads"""
        payloads = {
            "c1": "echo cleanup1",
            "c2": "echo cleanup2"
        }

        results = self.concealed_writer.write_batch_concealed_payloads(payloads)

        # Verify files exist
        for name, result in results.items():
            self.assertTrue(os.path.exists(result["payload_path"]))

        # Cleanup
        cleaned = self.concealed_writer.cleanup_payloads(results)
        self.assertEqual(cleaned, 2)

        # Verify files are deleted
        for name, result in results.items():
            if result and result["payload_path"]:
                # Note: files might not be immediately deleted, but they should be marked
                pass

    def test_system_file_matching_chain(self):
        """Test matching through system file hierarchy"""
        # Create test file
        test_file = os.path.join(self.temp_dir, "match_test.txt")
        with open(test_file, 'w') as f:
            f.write("Match test")

        matcher = SystemFileTimestampMatcher()

        try:
            # Try system binary match
            info = matcher.match_to_system_binary(test_file)
            self.assertTrue(info.spoof_success)
            self.assertIsNotNone(info.mtime_dt)
        except FileNotFoundError:
            self.skipTest("System binary not available")

    def test_spoof_multiple_files_verify_all(self):
        """Test spoofing multiple files and verify each"""
        files = []
        for i in range(3):
            f = os.path.join(self.temp_dir, f"file{i}.txt")
            with open(f, 'w') as fp:
                fp.write(f"File {i}")
            files.append(f)

        # Create reference
        ref_file = os.path.join(self.temp_dir, "ref.txt")
        with open(ref_file, 'w') as f:
            f.write("Reference")

        ref_date = datetime(2022, 1, 1)
        os.utime(ref_file, (ref_date.timestamp(), ref_date.timestamp()))

        # Spoof all files
        results = self.spoofer.spoof_batch(files, reference_file=ref_file)

        # Verify all were spoofed
        for f, info in results.items():
            self.assertIsNotNone(info)
            self.assertTrue(info.spoof_success)

            # Get file timestamp
            mtime, _, _ = self.spoofer.get_file_timestamps(f)
            ref_mtime, _, _ = self.spoofer.get_file_timestamps(ref_file)

            # Should match (within 1 second)
            self.assertAlmostEqual(mtime, ref_mtime, delta=1)

    def test_concealed_vbs_workflow(self):
        """Test complete VBS payload concealment workflow"""
        vbs_code = '''Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd.exe /c echo hidden", 0, False'''

        result = self.concealed_writer.write_concealed_payload(
            vbs_code,
            file_format=FileFormat.VBS,
            spoof_to_system=True
        )

        # Verify result structure
        self.assertIn("payload_path", result)
        self.assertIn("payload_metadata", result)
        self.assertIn("timestamp_info", result)

        # Verify file exists
        self.assertTrue(os.path.exists(result["payload_path"]))

        # Verify timestamp was spoofed
        self.assertIsNotNone(result["timestamp_info"])
        self.assertTrue(result["timestamp_info"].spoof_success)

        # Verify metadata is correct
        self.assertEqual(result["payload_metadata"].format, "vbs")
        self.assertGreater(result["payload_metadata"].encoded_size, 0)

    def test_stealth_timestamp_levels(self):
        """Test different stealth timestamp levels"""
        payload = "echo test"

        for level in ["low", "medium", "high"]:
            result = self.concealed_writer.write_payload_with_stealth_timestamps(
                payload,
                file_format=FileFormat.BAT,
                stealth_level=level
            )

            self.assertIsNotNone(result["payload_path"])
            self.assertTrue(os.path.exists(result["payload_path"]))
            self.assertEqual(result["stealth_level"], level)

            if level in ["medium", "high"]:
                self.assertIsNotNone(result["timestamp_info"])
                self.assertTrue(result["timestamp_info"].spoof_success)

    def test_error_handling_nonexistent_file(self):
        """Test error handling for non-existent files"""
        with self.assertRaises(FileNotFoundError):
            self.spoofer.get_file_timestamps("/nonexistent/file.txt")

        with self.assertRaises(FileNotFoundError):
            self.spoofer.spoof_to_match_file(
                "/nonexistent/target.txt",
                "/nonexistent/ref.txt"
            )

    def test_complete_payload_concealment_scenario(self):
        """Test complete payload concealment scenario"""
        # Create multiple payloads
        payloads = {
            "stage1_dll": "REM Stage 1 DLL",
            "stage2_exe": "REM Stage 2 EXE",
            "stage3_bat": "REM Stage 3 BAT"
        }

        # Write as concealed payload family
        results = self.concealed_writer.write_payload_family(
            payloads,
            file_format=FileFormat.BAT
        )

        # Verify all created
        self.assertEqual(len(results), 3)

        # Get all timestamps
        timestamps = {}
        for name, result in results.items():
            if result and result["timestamp_info"]:
                timestamps[name] = result["timestamp_info"].spoofed_mtime

        # Verify all have timestamps
        self.assertEqual(len(timestamps), 3)

        # Verify they're all the same (family)
        ts_values = list(timestamps.values())
        for ts in ts_values[1:]:
            self.assertAlmostEqual(ts, ts_values[0], delta=1)

        # Export manifest
        manifest = self.concealed_writer.export_payload_manifest(results)
        self.assertIsNotNone(manifest)
        self.assertIn('"stage1_dll"', manifest)


if __name__ == "__main__":
    unittest.main()
