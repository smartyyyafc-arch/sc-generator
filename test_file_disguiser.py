#!/usr/bin/env python3
"""
Test suite for the File Disguiser tool.
"""

import unittest
import tempfile
import os
from pathlib import Path
from file_disguiser import FileDisguiser, DisguiseType, create_disguised_payload, extract_disguised_file


class TestFileDisguiser(unittest.TestCase):
    """Test cases for FileDisguiser functionality."""

    def setUp(self):
        """Create a temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.disguiser = FileDisguiser(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_write_disguised_text(self):
        """Test writing text content with disguise."""
        content = "This is secret content"
        path = self.disguiser.write_disguised_text("secret", content, DisguiseType.TXT)

        self.assertTrue(path.exists())
        self.assertTrue(str(path).endswith(".txt"))
        self.assertEqual(self.disguiser.read_disguised(path), content.encode())

    def test_write_disguised_binary(self):
        """Test writing binary content with disguise."""
        binary = b"\x89PNG\r\n\x1a\n" + b"binary data"
        path = self.disguiser.write_disguised_binary("image", binary, DisguiseType.PDF)

        self.assertTrue(path.exists())
        self.assertTrue(str(path).endswith(".pdf"))
        self.assertEqual(self.disguiser.read_disguised(path), binary)

    def test_multiple_disguise_types(self):
        """Test various disguise types."""
        types_to_test = [
            DisguiseType.TXT,
            DisguiseType.DOC,
            DisguiseType.PDF,
            DisguiseType.LOG,
            DisguiseType.JSON,
        ]

        for disguise_type in types_to_test:
            with self.subTest(disguise_type=disguise_type):
                path = self.disguiser.write_disguised_text(
                    f"test_{disguise_type.value}",
                    f"Content for {disguise_type.value}",
                    disguise_type
                )
                self.assertTrue(str(path).endswith(f".{disguise_type.value}"))

    def test_undisguise(self):
        """Test extracting content from disguised file."""
        original_content = "Hidden message"
        disguised_path = self.disguiser.write_disguised_text("hidden", original_content, DisguiseType.PDF)

        extracted_path = self.disguiser.undisguise(disguised_path)
        with open(extracted_path, "rb") as f:
            extracted_content = f.read().decode()

        self.assertEqual(extracted_content, original_content)

    def test_get_file_info(self):
        """Test retrieving file metadata."""
        path = self.disguiser.write_disguised_text("test", "content", DisguiseType.DOC)
        info = self.disguiser.get_file_info(path)

        self.assertEqual(info["original_name"], "test")
        self.assertEqual(info["disguise_ext"], "doc")
        self.assertEqual(info["size"], 7)

    def test_list_disguised_files(self):
        """Test listing all disguised files."""
        self.disguiser.write_disguised_text("file1", "content1", DisguiseType.TXT)
        self.disguiser.write_disguised_text("file2", "content2", DisguiseType.PDF)

        files = self.disguiser.list_disguised_files()
        self.assertEqual(len(files), 2)

    def test_string_disguise_type(self):
        """Test using string instead of enum for disguise type."""
        path = self.disguiser.write_disguised_text("test", "content", "xlsx")
        self.assertTrue(str(path).endswith(".xlsx"))

    def test_create_disguised_payload_helper(self):
        """Test convenience function for creating disguised files."""
        path = create_disguised_payload("secret data", "payload", "log", self.temp_dir)
        self.assertTrue(path.exists())
        self.assertTrue(str(path).endswith(".log"))

    def test_extract_disguised_file_helper(self):
        """Test convenience function for extracting files."""
        original = "hidden content"
        disguised_path = self.disguiser.write_disguised_text("test", original, DisguiseType.PDF)

        extracted = extract_disguised_file(disguised_path, os.path.join(self.temp_dir, "extracted"))
        with open(extracted, "rb") as f:
            content = f.read().decode()

        self.assertEqual(content, original)

    def test_unicode_content(self):
        """Test handling unicode content."""
        unicode_content = "Hello 世界 🔒 مرحبا мир"
        path = self.disguiser.write_disguised_text("unicode", unicode_content, DisguiseType.TXT)
        retrieved = self.disguiser.read_disguised(path).decode("utf-8")

        self.assertEqual(retrieved, unicode_content)

    def test_large_content(self):
        """Test handling large content."""
        large_content = "x" * (1024 * 1024)  # 1 MB
        path = self.disguiser.write_disguised_text("large", large_content, DisguiseType.BIN)

        self.assertTrue(path.exists())
        retrieved = self.disguiser.read_disguised(path)
        self.assertEqual(len(retrieved), 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
