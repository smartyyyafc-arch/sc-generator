#!/usr/bin/env python3
"""
Test suite for payload file writer variants
Tests all location variants and their functionality
"""

import unittest
import os
import tempfile
from pathlib import Path
from payload_file_writer_variants import (
    BaseFileWriter,
    TempFileWriter,
    AppDataFileWriter,
    ProgramDataFileWriter,
    LocalAppDataFileWriter,
    UserProfileFileWriter,
    WindowsSystemFileWriter,
    RecycleBinFileWriter,
    PublicFileWriter,
    DownloadsFileWriter,
    CustomPathFileWriter,
    FileFormat,
    FileWriterFactory,
    MultiLocationPayloadWriter,
    PayloadMetadata
)


class TestTempFileWriter(unittest.TestCase):
    """Test TEMP directory writer"""

    def setUp(self):
        self.writer = TempFileWriter()
        self.test_payload = 'Set objShell = CreateObject("WScript.Shell")'

    def tearDown(self):
        self.writer.cleanup_all()

    def test_location_type(self):
        """Test location type identifier"""
        self.assertEqual(self.writer.get_location_type(), "%TEMP%")

    def test_write_payload(self):
        """Test writing payload"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.VBS,
            "high"
        )
        self.assertTrue(os.path.exists(path))
        self.assertIn("%TEMP%", metadata.location_type)
        self.assertEqual(metadata.format, "vbs")

    def test_payload_metadata(self):
        """Test metadata generation"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.VBS,
            "high"
        )
        self.assertIsNotNone(metadata.file_id)
        self.assertGreater(metadata.original_size, 0)
        self.assertEqual(metadata.location_type, "%TEMP%")
        self.assertIsNotNone(metadata.sha256_hash)

    def test_cleanup(self):
        """Test file cleanup"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.VBS,
            "high"
        )
        self.assertTrue(os.path.exists(path))
        self.writer.cleanup_temp_file(metadata.file_id)
        self.assertFalse(os.path.exists(path))


class TestAppDataFileWriter(unittest.TestCase):
    """Test APPDATA directory writer"""

    def setUp(self):
        self.writer = AppDataFileWriter(app_name="TestApp")
        self.test_payload = 'Set objShell = CreateObject("WScript.Shell")'

    def tearDown(self):
        self.writer.cleanup_all()

    def test_location_type(self):
        """Test location type identifier"""
        self.assertIn("%APPDATA%", self.writer.get_location_type())
        self.assertIn("TestApp", self.writer.get_location_type())

    def test_write_payload(self):
        """Test writing payload to APPDATA"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.VBS,
            "high"
        )
        self.assertTrue(os.path.exists(path))
        self.assertIn("%APPDATA%", metadata.location_type)

    def test_custom_app_name(self):
        """Test custom app name"""
        writer = AppDataFileWriter(app_name="CustomApp")
        self.assertIn("CustomApp", writer.get_location_type())


class TestProgramDataFileWriter(unittest.TestCase):
    """Test ProgramData directory writer"""

    def setUp(self):
        self.writer = ProgramDataFileWriter(vendor_name="TestVendor")
        self.test_payload = "@echo test"

    def tearDown(self):
        self.writer.cleanup_all()

    def test_location_type(self):
        """Test location type identifier"""
        location = self.writer.get_location_type()
        self.assertIn("ProgramData", location)
        self.assertIn("TestVendor", location)

    def test_write_payload(self):
        """Test writing payload to ProgramData"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.BAT,
            "high"
        )
        self.assertTrue(os.path.exists(path))
        self.assertIn("ProgramData", metadata.location_type)


class TestLocalAppDataFileWriter(unittest.TestCase):
    """Test LOCALAPPDATA directory writer"""

    def setUp(self):
        self.writer = LocalAppDataFileWriter(app_name="LocalTestApp")
        self.test_payload = "Get-Process"

    def tearDown(self):
        self.writer.cleanup_all()

    def test_location_type(self):
        """Test location type identifier"""
        location = self.writer.get_location_type()
        self.assertIn("%LOCALAPPDATA%", location)
        self.assertIn("LocalTestApp", location)

    def test_write_payload(self):
        """Test writing payload to LOCALAPPDATA"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.PS1,
            "high"
        )
        self.assertTrue(os.path.exists(path))


class TestUserProfileFileWriter(unittest.TestCase):
    """Test USERPROFILE directory writer"""

    def setUp(self):
        self.writer = UserProfileFileWriter(subdir=".config")
        self.test_payload = 'echo "user profile test"'

    def tearDown(self):
        self.writer.cleanup_all()

    def test_location_type(self):
        """Test location type identifier"""
        location = self.writer.get_location_type()
        self.assertIn("%USERPROFILE%", location)
        self.assertIn(".config", location)

    def test_write_payload(self):
        """Test writing payload to USERPROFILE"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.BAT,
            "high"
        )
        self.assertTrue(os.path.exists(path))


class TestWindowsSystemFileWriter(unittest.TestCase):
    """Test Windows System directory writer"""

    def setUp(self):
        self.writer = WindowsSystemFileWriter(target_dir="Temp")
        self.test_payload = "@echo system test"

    def tearDown(self):
        self.writer.cleanup_all()

    def test_location_type(self):
        """Test location type identifier"""
        location = self.writer.get_location_type()
        self.assertIn("Windows", location)
        self.assertIn("Temp", location)

    def test_write_payload(self):
        """Test writing payload to Windows Temp"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.BAT,
            "high"
        )
        self.assertTrue(os.path.exists(path))


class TestRecycleBinFileWriter(unittest.TestCase):
    """Test Recycle Bin directory writer"""

    def setUp(self):
        self.writer = RecycleBinFileWriter()
        self.test_payload = "Set objShell = CreateObject"

    def tearDown(self):
        self.writer.cleanup_all()

    def test_location_type(self):
        """Test location type identifier"""
        location = self.writer.get_location_type()
        self.assertIn("Recycle.Bin", location)

    def test_write_payload(self):
        """Test writing payload to Recycle Bin"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.VBS,
            "high"
        )
        self.assertTrue(os.path.exists(path))


class TestPublicFileWriter(unittest.TestCase):
    """Test Public directory writer"""

    def setUp(self):
        self.writer = PublicFileWriter(subdir="Shared")
        self.test_payload = "Public payload"

    def tearDown(self):
        self.writer.cleanup_all()

    def test_location_type(self):
        """Test location type identifier"""
        location = self.writer.get_location_type()
        self.assertIn("Public", location)

    def test_write_payload(self):
        """Test writing payload to Public"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.TEXT,
            "high"
        )
        self.assertTrue(os.path.exists(path))


class TestDownloadsFileWriter(unittest.TestCase):
    """Test Downloads directory writer"""

    def setUp(self):
        self.writer = DownloadsFileWriter()
        self.test_payload = "Downloads payload"

    def tearDown(self):
        self.writer.cleanup_all()

    def test_location_type(self):
        """Test location type identifier"""
        location = self.writer.get_location_type()
        self.assertIn("Downloads", location)

    def test_write_payload(self):
        """Test writing payload to Downloads"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.TEXT,
            "high"
        )
        self.assertTrue(os.path.exists(path))


class TestCustomPathFileWriter(unittest.TestCase):
    """Test custom path file writer"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.writer = CustomPathFileWriter(self.temp_dir)
        self.test_payload = "Custom path payload"

    def tearDown(self):
        self.writer.cleanup_all()
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def test_custom_path(self):
        """Test custom path location"""
        location = self.writer.get_location_type()
        self.assertEqual(location, self.temp_dir)

    def test_write_payload(self):
        """Test writing to custom path"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.TEXT,
            "high"
        )
        self.assertTrue(os.path.exists(path))
        self.assertIn(self.temp_dir, path)


class TestFileWriterFactory(unittest.TestCase):
    """Test file writer factory"""

    def test_create_temp_writer(self):
        """Test creating TEMP writer"""
        writer = FileWriterFactory.create("temp")
        self.assertIsNotNone(writer)
        self.assertEqual(writer.get_location_type(), "%TEMP%")

    def test_create_appdata_writer(self):
        """Test creating APPDATA writer"""
        writer = FileWriterFactory.create("appdata", app_name="TestApp")
        self.assertIsNotNone(writer)
        self.assertIn("%APPDATA%", writer.get_location_type())

    def test_create_programdata_writer(self):
        """Test creating ProgramData writer"""
        writer = FileWriterFactory.create("programdata", vendor_name="TestVendor")
        self.assertIsNotNone(writer)
        self.assertIn("ProgramData", writer.get_location_type())

    def test_create_invalid_variant(self):
        """Test creating invalid variant"""
        writer = FileWriterFactory.create("invalid_variant")
        self.assertIsNone(writer)

    def test_available_variants(self):
        """Test getting available variants"""
        variants = FileWriterFactory.get_available_variants()
        self.assertGreater(len(variants), 0)
        self.assertIn("temp", variants)
        self.assertIn("appdata", variants)
        self.assertIn("programdata", variants)

    def test_create_all_writers(self):
        """Test creating all writers at once"""
        writers = FileWriterFactory.create_all()
        self.assertGreater(len(writers), 0)
        self.assertIn("temp", writers)
        self.assertIn("appdata", writers)
        self.assertIn("programdata", writers)


class TestMultiLocationPayloadWriter(unittest.TestCase):
    """Test multi-location payload writer"""

    def setUp(self):
        self.multi_writer = MultiLocationPayloadWriter(
            variants=["temp", "appdata", "localappdata"]
        )
        self.test_payload = "Multi-location test payload"

    def tearDown(self):
        self.multi_writer.cleanup_all_locations()

    def test_write_to_all_locations(self):
        """Test writing to all locations"""
        results = self.multi_writer.write_to_all_locations(
            self.test_payload,
            FileFormat.VBS,
            "high"
        )
        self.assertEqual(len(results), 3)
        for variant, (path, metadata) in results.items():
            if path:
                self.assertTrue(os.path.exists(path))
                self.assertIsNotNone(metadata)

    def test_get_summary(self):
        """Test getting summary"""
        results = self.multi_writer.write_to_all_locations(
            self.test_payload,
            FileFormat.VBS,
            "high"
        )
        summary = self.multi_writer.get_summary(results)

        self.assertIn("total_locations", summary)
        self.assertIn("successful_writes", summary)
        self.assertGreater(summary["total_locations"], 0)
        self.assertGreater(summary["successful_writes"], 0)

    def test_cleanup_all_locations(self):
        """Test cleanup all locations"""
        self.multi_writer.write_to_all_locations(
            self.test_payload,
            FileFormat.VBS,
            "high"
        )
        cleanup_results = self.multi_writer.cleanup_all_locations()
        self.assertIsInstance(cleanup_results, dict)
        total_cleaned = sum(cleanup_results.values())
        self.assertGreater(total_cleaned, 0)

    def test_custom_variant_selection(self):
        """Test custom variant selection"""
        multi_writer = MultiLocationPayloadWriter(
            variants=["temp", "downloads"]
        )
        self.assertEqual(len(multi_writer.writers), 2)
        self.assertIn("temp", multi_writer.writers)
        self.assertIn("downloads", multi_writer.writers)
        multi_writer.cleanup_all_locations()


class TestFileFormats(unittest.TestCase):
    """Test different file formats"""

    def setUp(self):
        self.writer = TempFileWriter()

    def tearDown(self):
        self.writer.cleanup_all()

    def test_vbs_format(self):
        """Test VBS format"""
        payload = 'Set obj = CreateObject("WScript.Shell")'
        path, metadata = self.writer.write_payload(
            payload,
            FileFormat.VBS,
            "high"
        )
        self.assertEqual(metadata.format, "vbs")
        self.assertTrue(path.endswith(".vbs"))

    def test_bat_format(self):
        """Test BAT format"""
        payload = "@echo test"
        path, metadata = self.writer.write_payload(
            payload,
            FileFormat.BAT,
            "high"
        )
        self.assertEqual(metadata.format, "bat")
        self.assertTrue(path.endswith(".bat"))

    def test_ps1_format(self):
        """Test PowerShell format"""
        payload = "Get-Process"
        path, metadata = self.writer.write_payload(
            payload,
            FileFormat.PS1,
            "high"
        )
        self.assertEqual(metadata.format, "ps1")
        self.assertTrue(path.endswith(".ps1"))

    def test_text_format(self):
        """Test text format"""
        payload = "Plain text payload"
        path, metadata = self.writer.write_payload(
            payload,
            FileFormat.TEXT,
            "high"
        )
        self.assertEqual(metadata.format, "txt")
        self.assertTrue(path.endswith(".txt"))


class TestObfuscationLevels(unittest.TestCase):
    """Test different obfuscation levels"""

    def setUp(self):
        self.writer = TempFileWriter(enable_obfuscation=True)
        self.test_payload = 'Set objShell = CreateObject("WScript.Shell")'

    def tearDown(self):
        self.writer.cleanup_all()

    def test_low_obfuscation(self):
        """Test low obfuscation"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.VBS,
            "low"
        )
        self.assertEqual(metadata.obfuscation_level, "low")
        self.assertTrue(os.path.exists(path))

    def test_medium_obfuscation(self):
        """Test medium obfuscation"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.VBS,
            "medium"
        )
        self.assertEqual(metadata.obfuscation_level, "medium")
        self.assertTrue(os.path.exists(path))

    def test_high_obfuscation(self):
        """Test high obfuscation"""
        path, metadata = self.writer.write_payload(
            self.test_payload,
            FileFormat.VBS,
            "high"
        )
        self.assertEqual(metadata.obfuscation_level, "high")
        self.assertTrue(os.path.exists(path))


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTempFileWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestAppDataFileWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestProgramDataFileWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestLocalAppDataFileWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestUserProfileFileWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestWindowsSystemFileWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestRecycleBinFileWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestPublicFileWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestDownloadsFileWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestCustomPathFileWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestFileWriterFactory))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiLocationPayloadWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestFileFormats))
    suite.addTests(loader.loadTestsFromTestCase(TestObfuscationLevels))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
