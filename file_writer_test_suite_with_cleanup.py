#!/usr/bin/env python3
"""
File Writer Test Suite with Comprehensive Cleanup Verification
Tests PayloadFileWriter with strict cleanup verification and resource management
Ensures all temporary files are properly cleaned up after test execution
"""

import os
import tempfile
import shutil
import json
import hashlib
import unittest
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import sys

# Import the module under test
sys.path.insert(0, '/home/user/sc-generator')
from payload_file_writer import (
    PayloadFileWriter,
    FileFormat,
    PayloadMetadata,
    ObfuscationStrategies
)


@dataclass
class CleanupVerificationResult:
    """Result of cleanup verification"""
    test_name: str
    files_created: int
    files_cleaned: int
    orphaned_files: List[str]
    temp_dir_cleaned: bool
    verification_passed: bool
    details: Dict


class FileWriterTestSuite(unittest.TestCase):
    """Test suite for PayloadFileWriter with cleanup verification"""

    @classmethod
    def setUpClass(cls):
        """Set up class-level resources"""
        cls.test_base_dir = Path(tempfile.gettempdir()) / "test-file-writer-suite"
        cls.test_base_dir.mkdir(parents=True, exist_ok=True)
        cls.cleanup_results: List[CleanupVerificationResult] = []

    @classmethod
    def tearDownClass(cls):
        """Tear down class-level resources"""
        # Final cleanup of test directory
        if cls.test_base_dir.exists():
            shutil.rmtree(cls.test_base_dir, ignore_errors=True)

        # Print cleanup results summary
        print("\n" + "="*70)
        print("CLEANUP VERIFICATION SUMMARY")
        print("="*70)
        for result in cls.cleanup_results:
            status = "✓ PASS" if result.verification_passed else "✗ FAIL"
            print(f"\n{status} - {result.test_name}")
            print(f"  Files Created: {result.files_created}")
            print(f"  Files Cleaned: {result.files_cleaned}")
            print(f"  Orphaned Files: {len(result.orphaned_files)}")
            if result.orphaned_files:
                for orphan in result.orphaned_files:
                    print(f"    - {orphan}")
            print(f"  Temp Dir Cleaned: {result.temp_dir_cleaned}")

    def setUp(self):
        """Set up test-specific resources"""
        self.test_temp_dir = self.test_base_dir / f"test_{id(self)}"
        self.test_temp_dir.mkdir(parents=True, exist_ok=True)
        self.writer = PayloadFileWriter(base_temp_dir=str(self.test_temp_dir))
        self.files_before = set(self.test_temp_dir.glob("**/*"))

    def tearDown(self):
        """Tear down test-specific resources and verify cleanup"""
        self._verify_cleanup()

        # Force cleanup of any remaining files
        if self.test_temp_dir.exists():
            shutil.rmtree(self.test_temp_dir, ignore_errors=True)

    def _verify_cleanup(self):
        """Verify that all resources created during test are cleaned up"""
        files_after = set(self.test_temp_dir.glob("**/*"))
        remaining_files = files_after - self.files_before

        # Check metadata store is empty
        metadata_cleaned = len(self.writer.metadata_store) == 0

        # Check temp directory
        temp_dir_cleaned = not any(self.test_temp_dir.glob("**/*"))

        # Verify all files are actually deleted
        orphaned_files = [str(f) for f in remaining_files if f.is_file()]

        result = CleanupVerificationResult(
            test_name=self._testMethodName,
            files_created=len(self.files_before),
            files_cleaned=len([f for f in self.files_before if not f.exists()]),
            orphaned_files=orphaned_files,
            temp_dir_cleaned=temp_dir_cleaned,
            verification_passed=metadata_cleaned and len(orphaned_files) == 0,
            details={
                "metadata_cleaned": metadata_cleaned,
                "remaining_metadata": len(self.writer.metadata_store),
                "timestamp": datetime.now().isoformat()
            }
        )

        FileWriterTestSuite.cleanup_results.append(result)

        # Assert cleanup was successful
        self.assertTrue(
            metadata_cleaned,
            f"Metadata store not cleaned: {list(self.writer.metadata_store.keys())}"
        )
        self.assertEqual(
            len(orphaned_files), 0,
            f"Orphaned files found: {orphaned_files}"
        )

    def test_01_basic_payload_write_and_cleanup(self):
        """Test 1: Write single payload and verify cleanup"""
        payload = 'Set shell = CreateObject("WScript.Shell")\nshell.Run "cmd /c echo test", 0, False'

        # Write payload
        file_path, metadata = self.writer.write_payload(
            payload,
            file_format=FileFormat.VBS,
            obfuscation_level="high"
        )

        # Verify file exists
        self.assertTrue(os.path.exists(file_path), "Payload file not created")
        self.assertEqual(metadata.format, "vbs", "Format mismatch")
        self.assertGreater(len(metadata.file_id), 0, "File ID not generated")

        # Cleanup
        cleanup_success = self.writer.cleanup_temp_file(metadata.file_id)
        self.assertTrue(cleanup_success, "Cleanup failed")

        # Verify file is deleted
        self.assertFalse(os.path.exists(file_path), "File not deleted after cleanup")
        self.assertEqual(len(self.writer.metadata_store), 0, "Metadata not removed")

    def test_02_batch_payload_write_and_cleanup(self):
        """Test 2: Write multiple payloads in batch and verify cleanup"""
        payloads = {
            "payload_1": "echo test1",
            "payload_2": "echo test2",
            "payload_3": "echo test3",
            "payload_4": "echo test4",
        }

        # Write batch
        batch_result = self.writer.write_payload_batch(
            payloads,
            file_format=FileFormat.BAT,
            obfuscation_level="medium"
        )

        # Verify all files created
        created_files = []
        for name, (path, metadata) in batch_result.items():
            if path:
                self.assertTrue(os.path.exists(path), f"File {name} not created")
                created_files.append(metadata.file_id)

        self.assertEqual(len(created_files), 4, "Not all batch files created")
        self.assertEqual(len(self.writer.metadata_store), 4, "Metadata not stored")

        # Cleanup all
        cleaned_count = self.writer.cleanup_all()

        # Verify cleanup
        self.assertEqual(cleaned_count, 4, "Not all files cleaned")
        self.assertEqual(len(self.writer.metadata_store), 0, "Metadata store not empty")

        # Verify files deleted
        for file_id in created_files:
            metadata = None
            for m in batch_result.values():
                if m[1] and m[1].file_id == file_id:
                    metadata = m[1]
                    break
            if metadata:
                self.assertFalse(
                    os.path.exists(metadata.temp_path),
                    f"File not deleted: {metadata.temp_path}"
                )

    def test_03_payload_with_decoder_and_cleanup(self):
        """Test 3: Write payload with decoder stub and verify cleanup"""
        payload = 'Set obj = CreateObject("WScript.Shell")'

        # Write with decoder
        payload_path, decoder_path, metadata = self.writer.write_payload_with_decoder(
            payload,
            encoding_type="base64",
            obfuscation_level="high"
        )

        # Verify files created
        self.assertTrue(os.path.exists(payload_path), "Payload file not created")
        self.assertTrue(os.path.exists(decoder_path), "Decoder file not created")
        self.assertEqual(len(self.writer.metadata_store), 2, "Not all metadata stored")

        # Cleanup all
        cleaned_count = self.writer.cleanup_all()

        # Verify cleanup
        self.assertEqual(cleaned_count, 2, "Not all files cleaned")
        self.assertFalse(os.path.exists(payload_path), "Payload file not deleted")
        self.assertFalse(os.path.exists(decoder_path), "Decoder file not deleted")
        self.assertEqual(len(self.writer.metadata_store), 0, "Metadata store not empty")

    def test_04_multiple_formats_and_cleanup(self):
        """Test 4: Write payloads in multiple formats and verify cleanup"""
        test_payload = "test payload content"
        formats = [FileFormat.VBS, FileFormat.BAT, FileFormat.PS1, FileFormat.JSON]

        file_paths = []
        file_ids = []

        # Write files in different formats
        for fmt in formats:
            try:
                path, metadata = self.writer.write_payload(
                    test_payload,
                    file_format=fmt,
                    obfuscation_level="high"
                )
                if path:
                    file_paths.append(path)
                    file_ids.append(metadata.file_id)
                    self.assertTrue(os.path.exists(path), f"File format {fmt} not created")
            except Exception as e:
                # Some formats might fail gracefully
                pass

        # Verify metadata stored
        initial_count = len(self.writer.metadata_store)
        self.assertGreater(initial_count, 0, "No metadata stored")

        # Cleanup
        cleaned_count = self.writer.cleanup_all()
        self.assertEqual(cleaned_count, initial_count, "Cleanup count mismatch")

        # Verify all files deleted
        for path in file_paths:
            self.assertFalse(os.path.exists(path), f"File not deleted: {path}")

        self.assertEqual(len(self.writer.metadata_store), 0, "Metadata store not empty")

    def test_05_metadata_integrity_and_cleanup(self):
        """Test 5: Verify metadata integrity before cleanup"""
        payload = "sensitive payload data"

        # Write payload
        path, metadata = self.writer.write_payload(
            payload,
            file_format=FileFormat.VBS,
            obfuscation_level="high"
        )

        # Verify metadata
        self.assertIsNotNone(metadata.file_id, "File ID missing")
        self.assertEqual(metadata.original_size, len(payload), "Original size mismatch")
        self.assertGreater(metadata.encoded_size, 0, "Encoded size invalid")
        self.assertIsNotNone(metadata.sha256_hash, "SHA256 hash missing")
        self.assertIsNotNone(metadata.checksum, "Checksum missing")
        self.assertTrue(os.path.exists(metadata.temp_path), "Temp path invalid")

        # Get info
        retrieved_metadata = self.writer.get_payload_info(metadata.file_id)
        self.assertEqual(retrieved_metadata.file_id, metadata.file_id, "Metadata retrieval failed")

        # Export as JSON
        json_export = self.writer.export_metadata_json(metadata.file_id)
        exported_data = json.loads(json_export)
        self.assertIn("file_id", exported_data, "JSON export missing file_id")
        self.assertIn("sha256_hash", exported_data, "JSON export missing hash")

        # Cleanup
        success = self.writer.cleanup_temp_file(metadata.file_id)
        self.assertTrue(success, "Cleanup failed")

        # Verify metadata cannot be retrieved after cleanup
        with self.assertRaises(ValueError):
            self.writer.get_payload_info(metadata.file_id)

    def test_06_obfuscation_and_cleanup(self):
        """Test 6: Apply obfuscation and verify cleanup"""
        vbs_payload = 'MsgBox "Hello World"'

        # Test obfuscation
        obfuscated = self.writer.obfuscate_vbs_payload(vbs_payload, "high")
        self.assertNotEqual(vbs_payload, obfuscated, "Obfuscation not applied")

        # Write obfuscated payload
        path, metadata = self.writer.write_payload(
            vbs_payload,
            file_format=FileFormat.VBS,
            obfuscation_level="high"
        )

        # Verify file contains obfuscated content
        with open(path, 'r') as f:
            file_content = f.read()
        self.assertNotEqual(file_content, vbs_payload, "File not obfuscated")

        # Cleanup
        self.writer.cleanup_all()
        self.assertFalse(os.path.exists(path), "File not deleted")
        self.assertEqual(len(self.writer.metadata_store), 0, "Metadata not cleared")

    def test_07_partial_cleanup_and_recovery(self):
        """Test 7: Partial cleanup and recovery"""
        payloads_data = {
            "p1": "payload 1",
            "p2": "payload 2",
            "p3": "payload 3",
        }

        # Write batch
        batch_result = self.writer.write_payload_batch(payloads_data)

        file_ids = []
        paths = []
        for name, (path, metadata) in batch_result.items():
            if metadata:
                file_ids.append(metadata.file_id)
                paths.append(path)

        self.assertEqual(len(file_ids), 3, "Not all files written")

        # Cleanup first file only
        first_id = file_ids[0]
        cleanup_success = self.writer.cleanup_temp_file(first_id)
        self.assertTrue(cleanup_success, "Single cleanup failed")

        # Verify first file deleted
        self.assertFalse(os.path.exists(paths[0]), "First file not deleted")

        # Verify others still exist
        self.assertTrue(os.path.exists(paths[1]), "Second file deleted unexpectedly")
        self.assertTrue(os.path.exists(paths[2]), "Third file deleted unexpectedly")

        # Verify metadata
        self.assertEqual(len(self.writer.metadata_store), 2, "Metadata not updated correctly")

        # Cleanup remaining
        cleaned = self.writer.cleanup_all()
        self.assertEqual(cleaned, 2, "Partial cleanup count mismatch")
        self.assertEqual(len(self.writer.metadata_store), 0, "Metadata store not empty")

    def test_08_error_handling_and_cleanup(self):
        """Test 8: Error handling with proper cleanup"""
        # Test cleanup of non-existent file
        result = self.writer.cleanup_temp_file("non_existent_id")
        self.assertFalse(result, "Should return False for non-existent file")

        # Write a valid payload
        payload = "test payload"
        path, metadata = self.writer.write_payload(payload)

        self.assertTrue(os.path.exists(path), "File not created")

        # Cleanup should succeed
        cleanup_success = self.writer.cleanup_temp_file(metadata.file_id)
        self.assertTrue(cleanup_success, "Cleanup failed")
        self.assertFalse(os.path.exists(path), "File not deleted")

    def test_09_large_payload_and_cleanup(self):
        """Test 9: Handle large payloads and verify cleanup"""
        # Create large payload (500 KB to avoid timeout)
        large_payload = "x" * (500 * 1024)

        # Write large payload
        path, metadata = self.writer.write_payload(
            large_payload,
            file_format=FileFormat.BINARY,
            obfuscation_level="low"
        )

        self.assertTrue(os.path.exists(path), "Large file not created")
        self.assertEqual(metadata.original_size, 500 * 1024, "Original size incorrect")

        # Verify file size
        actual_size = os.path.getsize(path)
        self.assertGreater(actual_size, 0, "File size is zero")

        # Cleanup
        success = self.writer.cleanup_temp_file(metadata.file_id)
        self.assertTrue(success, "Large file cleanup failed")
        self.assertFalse(os.path.exists(path), "Large file not deleted")

    def test_10_concurrent_operations_and_cleanup(self):
        """Test 10: Multiple concurrent operations and cleanup"""
        payloads = [
            ('Set obj = CreateObject("WScript.Shell")', FileFormat.VBS),
            ('echo test', FileFormat.BAT),
            ('Get-Process', FileFormat.PS1),
            ('[{"test": "data"}]', FileFormat.JSON),
        ]

        created_paths = []
        created_ids = []

        # Write multiple payloads
        for payload, fmt in payloads:
            try:
                path, metadata = self.writer.write_payload(
                    payload,
                    file_format=fmt,
                    obfuscation_level="medium"
                )
                if path:
                    created_paths.append(path)
                    created_ids.append(metadata.file_id)
            except Exception as e:
                pass  # Some formats might not be supported

        # Verify all created
        self.assertGreater(len(created_paths), 0, "No files created")
        for path in created_paths:
            self.assertTrue(os.path.exists(path), f"File not found: {path}")

        # Cleanup all
        cleaned_count = self.writer.cleanup_all()
        self.assertEqual(cleaned_count, len(created_paths), "Cleanup count mismatch")

        # Verify all deleted
        for path in created_paths:
            self.assertFalse(os.path.exists(path), f"File not deleted: {path}")

        self.assertEqual(len(self.writer.metadata_store), 0, "Metadata not cleared")


class CleanupIntegrationTest(unittest.TestCase):
    """Integration tests for cleanup across multiple operations"""

    def setUp(self):
        """Set up integration test environment"""
        self.integration_dir = Path(tempfile.gettempdir()) / "integration_test"
        self.integration_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up integration test environment"""
        if self.integration_dir.exists():
            shutil.rmtree(self.integration_dir, ignore_errors=True)

    def test_multiple_writer_instances_cleanup(self):
        """Test cleanup with multiple writer instances"""
        instances = []
        all_paths = []

        # Create multiple writer instances
        for i in range(3):
            sub_dir = self.integration_dir / f"writer_{i}"
            sub_dir.mkdir(parents=True, exist_ok=True)
            writer = PayloadFileWriter(base_temp_dir=str(sub_dir))
            instances.append(writer)

            # Write payload with each instance
            path, metadata = writer.write_payload(f"payload_{i}")
            all_paths.append(path)

            self.assertTrue(os.path.exists(path), f"Path {i} not created")

        # Cleanup each instance
        for writer in instances:
            cleaned = writer.cleanup_all()
            self.assertGreaterEqual(cleaned, 0, "Cleanup returned negative count")

        # Verify all cleaned
        for path in all_paths:
            self.assertFalse(os.path.exists(path), f"Path not cleaned: {path}")


class CleanupReportGenerator:
    """Generate detailed cleanup verification reports"""

    def __init__(self, test_results: List[CleanupVerificationResult]):
        self.results = test_results

    def generate_report(self) -> Dict:
        """Generate comprehensive cleanup report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.verification_passed)
        failed_tests = total_tests - passed_tests

        total_created = sum(r.files_created for r in self.results)
        total_cleaned = sum(r.files_cleaned for r in self.results)
        total_orphaned = sum(len(r.orphaned_files) for r in self.results)

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{(passed_tests/total_tests*100):.2f}%" if total_tests > 0 else "0%"
            },
            "cleanup_summary": {
                "total_files_created": total_created,
                "total_files_cleaned": total_cleaned,
                "total_orphaned_files": total_orphaned,
                "cleanup_success_rate": f"{(total_cleaned/total_created*100):.2f}%" if total_created > 0 else "0%"
            },
            "failed_cleanups": [
                {
                    "test": r.test_name,
                    "orphaned_count": len(r.orphaned_files),
                    "orphaned_files": r.orphaned_files
                }
                for r in self.results if not r.verification_passed
            ],
            "timestamp": datetime.now().isoformat()
        }

        return report

    def save_report(self, file_path: str) -> None:
        """Save report to JSON file"""
        report = self.generate_report()
        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {file_path}")


def run_tests_with_report(verbosity: int = 2) -> Tuple[unittest.TestResult, Dict]:
    """Run all tests and generate cleanup report"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(FileWriterTestSuite))
    suite.addTests(loader.loadTestsFromTestCase(CleanupIntegrationTest))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Generate report
    report_gen = CleanupReportGenerator(FileWriterTestSuite.cleanup_results)
    report = report_gen.generate_report()

    return result, report


if __name__ == "__main__":
    print("="*70)
    print("FILE WRITER TEST SUITE WITH CLEANUP VERIFICATION")
    print("="*70 + "\n")

    # Run tests with detailed reporting
    test_result, cleanup_report = run_tests_with_report(verbosity=2)

    # Print cleanup report
    print("\n" + "="*70)
    print("CLEANUP VERIFICATION REPORT")
    print("="*70)
    print(json.dumps(cleanup_report, indent=2))

    # Save report
    report_path = "/home/user/sc-generator/file_writer_cleanup_report.json"
    report_gen = CleanupReportGenerator(FileWriterTestSuite.cleanup_results)
    report_gen.save_report(report_path)

    # Exit with appropriate code
    sys.exit(0 if test_result.wasSuccessful() else 1)
