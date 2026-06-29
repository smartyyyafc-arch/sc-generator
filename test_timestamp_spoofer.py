#!/usr/bin/env python3
"""
Test suite for Timestamp Spoofer module
Validates timestamp spoofing functionality
"""

import unittest
import os
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

from timestamp_spoofer import (
    TimestampSpoofer,
    SystemFileTimestampMatcher,
    TimestampInfo,
    spoof_to_reference,
    spoof_to_date,
    spoof_batch_files
)


class TestTimestampSpoofer(unittest.TestCase):
    """Test cases for TimestampSpoofer class"""

    def setUp(self):
        """Set up test fixtures"""
        self.spoofer = TimestampSpoofer()

        # Create temporary test files
        self.temp_dir = tempfile.mkdtemp()
        self.target_file = os.path.join(self.temp_dir, "target.txt")
        self.reference_file = os.path.join(self.temp_dir, "reference.txt")

        with open(self.target_file, 'w') as f:
            f.write("Target payload")

        with open(self.reference_file, 'w') as f:
            f.write("Reference file")

        # Set reference file to known timestamp
        self.reference_timestamp = time.time() - 86400 * 30  # 30 days ago
        os.utime(self.reference_file, (self.reference_timestamp, self.reference_timestamp))

    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_file_timestamps(self):
        """Test retrieving file timestamps"""
        mtime, atime, ctime = self.spoofer.get_file_timestamps(self.target_file)

        self.assertIsInstance(mtime, float)
        self.assertIsInstance(atime, float)
        self.assertIsInstance(ctime, float)
        self.assertGreater(mtime, 0)

    def test_get_file_timestamps_dt(self):
        """Test retrieving timestamps as datetime strings"""
        mtime_str, atime_str, ctime_str = self.spoofer.get_file_timestamps_dt(self.target_file)

        self.assertIsInstance(mtime_str, str)
        self.assertIsInstance(atime_str, str)
        self.assertIsInstance(ctime_str, str)
        # Should be ISO format
        datetime.fromisoformat(mtime_str)

    def test_spoof_to_match_file(self):
        """Test spoofing to match reference file"""
        info = self.spoofer.spoof_to_match_file(self.target_file, self.reference_file)

        self.assertIsInstance(info, TimestampInfo)
        self.assertTrue(info.spoof_success)
        self.assertEqual(info.file_path, self.target_file)

        # Verify timestamps are close (within 1 second due to precision)
        new_mtime, new_atime, _ = self.spoofer.get_file_timestamps(self.target_file)
        self.assertAlmostEqual(new_mtime, self.reference_timestamp, delta=1)

    def test_spoof_to_timestamp(self):
        """Test spoofing to specific Unix epoch timestamp"""
        target_ts = datetime(2020, 6, 15, 10, 30, 0).timestamp()

        info = self.spoofer.spoof_to_timestamp(self.target_file, target_ts)

        self.assertTrue(info.spoof_success)
        new_mtime, _, _ = self.spoofer.get_file_timestamps(self.target_file)
        self.assertAlmostEqual(new_mtime, target_ts, delta=1)

    def test_spoof_to_datetime(self):
        """Test spoofing to specific datetime"""
        target_dt = datetime(2021, 3, 20, 14, 45, 0)

        info = self.spoofer.spoof_to_datetime(self.target_file, target_dt)

        self.assertTrue(info.spoof_success)
        new_mtime, _, _ = self.spoofer.get_file_timestamps(self.target_file)
        self.assertAlmostEqual(new_mtime, target_dt.timestamp(), delta=1)

    def test_spoof_with_delta_days(self):
        """Test spoofing with day delta"""
        info = self.spoofer.spoof_with_delta(
            self.target_file,
            self.reference_file,
            days_delta=10
        )

        self.assertTrue(info.spoof_success)
        new_mtime, _, _ = self.spoofer.get_file_timestamps(self.target_file)
        expected_ts = self.reference_timestamp + (10 * 86400)
        self.assertAlmostEqual(new_mtime, expected_ts, delta=1)

    def test_spoof_with_delta_hours(self):
        """Test spoofing with hour delta"""
        info = self.spoofer.spoof_with_delta(
            self.target_file,
            self.reference_file,
            hours_delta=5
        )

        self.assertTrue(info.spoof_success)
        new_mtime, _, _ = self.spoofer.get_file_timestamps(self.target_file)
        expected_ts = self.reference_timestamp + (5 * 3600)
        self.assertAlmostEqual(new_mtime, expected_ts, delta=1)

    def test_spoof_with_negative_delta(self):
        """Test spoofing with negative time delta"""
        info = self.spoofer.spoof_with_delta(
            self.target_file,
            self.reference_file,
            days_delta=-5
        )

        self.assertTrue(info.spoof_success)
        new_mtime, _, _ = self.spoofer.get_file_timestamps(self.target_file)
        expected_ts = self.reference_timestamp - (5 * 86400)
        self.assertAlmostEqual(new_mtime, expected_ts, delta=1)

    def test_randomize_within_range(self):
        """Test randomizing timestamp within range"""
        start_ts = datetime(2020, 1, 1).timestamp()
        end_ts = datetime(2020, 12, 31).timestamp()

        info = self.spoofer.randomize_within_range(
            self.target_file,
            start_ts,
            end_ts
        )

        self.assertTrue(info.spoof_success)
        new_mtime, _, _ = self.spoofer.get_file_timestamps(self.target_file)
        self.assertGreater(new_mtime, start_ts)
        self.assertLess(new_mtime, end_ts)

    def test_restore_timestamps(self):
        """Test restoring original timestamps"""
        original_mtime, _, _ = self.spoofer.get_file_timestamps(self.target_file)

        # Spoof to different timestamp
        target_ts = datetime(2015, 1, 1).timestamp()
        self.spoofer.spoof_to_timestamp(self.target_file, target_ts)

        # Verify spoofing worked
        spoofed_mtime, _, _ = self.spoofer.get_file_timestamps(self.target_file)
        self.assertNotAlmostEqual(spoofed_mtime, original_mtime, delta=60)

        # Restore
        success = self.spoofer.restore_timestamps(self.target_file)
        self.assertTrue(success)

        # Verify restoration
        restored_mtime, _, _ = self.spoofer.get_file_timestamps(self.target_file)
        self.assertAlmostEqual(restored_mtime, original_mtime, delta=1)

    def test_clone_timestamps(self):
        """Test cloning timestamps to multiple files"""
        clone_files = [
            os.path.join(self.temp_dir, f"clone{i}.txt")
            for i in range(3)
        ]

        for clone_file in clone_files:
            with open(clone_file, 'w') as f:
                f.write("Clone test")

        results = self.spoofer.clone_timestamps(self.reference_file, clone_files)

        self.assertEqual(len(results), 3)
        for clone_file, info in results.items():
            self.assertIsNotNone(info)
            self.assertTrue(info.spoof_success)

            # Verify timestamps match reference
            clone_mtime, _, _ = self.spoofer.get_file_timestamps(clone_file)
            ref_mtime, _, _ = self.spoofer.get_file_timestamps(self.reference_file)
            self.assertAlmostEqual(clone_mtime, ref_mtime, delta=1)

    def test_get_timestamp_delta(self):
        """Test calculating timestamp delta between files"""
        # Create second file with different timestamp
        file2 = os.path.join(self.temp_dir, "file2.txt")
        with open(file2, 'w') as f:
            f.write("File 2")

        # Set file2 to 1 hour after reference_file
        file2_ts = self.reference_timestamp + 3600
        os.utime(file2, (file2_ts, file2_ts))

        delta = self.spoofer.get_timestamp_delta(file2, self.reference_file)
        self.assertAlmostEqual(delta, 3600, delta=1)

    def test_spoof_batch(self):
        """Test batch spoofing"""
        batch_files = [
            os.path.join(self.temp_dir, f"batch{i}.txt")
            for i in range(3)
        ]

        for batch_file in batch_files:
            with open(batch_file, 'w') as f:
                f.write("Batch test")

        results = self.spoofer.spoof_batch(batch_files, reference_file=self.reference_file)

        self.assertEqual(len(results), 3)
        for batch_file, info in results.items():
            self.assertIsNotNone(info)
            self.assertTrue(info.spoof_success)

    def test_timestamp_history(self):
        """Test timestamp history tracking"""
        self.spoofer.spoof_to_match_file(self.target_file, self.reference_file)

        history = self.spoofer.get_history()
        self.assertIn(self.target_file, history)
        self.assertIsInstance(history[self.target_file], TimestampInfo)

    def test_clear_history(self):
        """Test clearing timestamp history"""
        self.spoofer.spoof_to_match_file(self.target_file, self.reference_file)
        count = self.spoofer.clear_history()

        self.assertEqual(count, 1)
        history = self.spoofer.get_history()
        self.assertEqual(len(history), 0)

    def test_spoof_only_atime(self):
        """Test spoofing only access time"""
        original_mtime, original_atime, _ = self.spoofer.get_file_timestamps(self.target_file)

        self.spoofer.spoof_to_match_file(
            self.target_file,
            self.reference_file,
            spoof_mtime=False,
            spoof_atime=True
        )

        new_mtime, new_atime, _ = self.spoofer.get_file_timestamps(self.target_file)

        # mtime should not change (much)
        self.assertAlmostEqual(new_mtime, original_mtime, delta=1)

    def test_spoof_only_mtime(self):
        """Test spoofing only modification time"""
        original_mtime, original_atime, _ = self.spoofer.get_file_timestamps(self.target_file)

        self.spoofer.spoof_to_match_file(
            self.target_file,
            self.reference_file,
            spoof_mtime=True,
            spoof_atime=False
        )

        new_mtime, new_atime, _ = self.spoofer.get_file_timestamps(self.target_file)

        # mtime should change
        self.assertNotAlmostEqual(new_mtime, original_mtime, delta=60)

    def test_file_not_found_error(self):
        """Test FileNotFoundError handling"""
        with self.assertRaises(FileNotFoundError):
            self.spoofer.get_file_timestamps("/nonexistent/file.txt")

        with self.assertRaises(FileNotFoundError):
            self.spoofer.spoof_to_match_file(
                "/nonexistent/target.txt",
                self.reference_file
            )


class TestSystemFileTimestampMatcher(unittest.TestCase):
    """Test cases for SystemFileTimestampMatcher class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")

        with open(self.test_file, 'w') as f:
            f.write("Test file")

        self.matcher = SystemFileTimestampMatcher()

    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_spoofer(self):
        """Test getting underlying spoofer instance"""
        spoofer = self.matcher.get_spoofer()
        self.assertIsInstance(spoofer, TimestampSpoofer)

    def test_match_to_system_binary(self):
        """Test matching to system binary"""
        try:
            info = self.matcher.match_to_system_binary(self.test_file)
            self.assertIsNotNone(info)
            self.assertTrue(info.spoof_success)
        except FileNotFoundError:
            self.skipTest("System binary not found")

    def test_match_to_config_file(self):
        """Test matching to system config file"""
        try:
            info = self.matcher.match_to_config_file(self.test_file)
            self.assertIsNotNone(info)
            self.assertTrue(info.spoof_success)
        except FileNotFoundError:
            self.skipTest("System config file not found")


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.target_file = os.path.join(self.temp_dir, "target.txt")
        self.reference_file = os.path.join(self.temp_dir, "reference.txt")

        with open(self.target_file, 'w') as f:
            f.write("Target")

        with open(self.reference_file, 'w') as f:
            f.write("Reference")

    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_spoof_to_reference(self):
        """Test spoof_to_reference convenience function"""
        info = spoof_to_reference(self.target_file, self.reference_file)
        self.assertIsInstance(info, TimestampInfo)
        self.assertTrue(info.spoof_success)

    def test_spoof_to_date(self):
        """Test spoof_to_date convenience function"""
        target_dt = datetime(2022, 5, 10, 12, 0, 0)
        info = spoof_to_date(self.target_file, target_dt)
        self.assertIsInstance(info, TimestampInfo)
        self.assertTrue(info.spoof_success)

    def test_spoof_batch_files(self):
        """Test spoof_batch_files convenience function"""
        batch_files = [
            os.path.join(self.temp_dir, f"batch{i}.txt")
            for i in range(2)
        ]

        for bf in batch_files:
            with open(bf, 'w') as f:
                f.write("Batch")

        results = spoof_batch_files(batch_files, self.reference_file)
        self.assertEqual(len(results), 2)

        for batch_file, info in results.items():
            self.assertIsNotNone(info)
            self.assertTrue(info.spoof_success)


class TestTimestampInfo(unittest.TestCase):
    """Test TimestampInfo dataclass"""

    def test_timestamp_info_creation(self):
        """Test creating TimestampInfo object"""
        info = TimestampInfo(
            file_path="/tmp/test.txt",
            original_mtime=1000.0,
            original_atime=1000.0,
            original_ctime=1000.0,
            spoofed_mtime=2000.0,
            spoofed_atime=2000.0,
            spoofed_ctime=2000.0,
            mtime_dt="2023-01-01T00:00:00",
            atime_dt="2023-01-01T00:00:00",
            ctime_dt="2023-01-01T00:00:00",
            spoof_success=True
        )

        self.assertEqual(info.file_path, "/tmp/test.txt")
        self.assertEqual(info.original_mtime, 1000.0)
        self.assertEqual(info.spoofed_mtime, 2000.0)
        self.assertTrue(info.spoof_success)


if __name__ == "__main__":
    unittest.main()
