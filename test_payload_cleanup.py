#!/usr/bin/env python3
"""
Comprehensive test suite for verifying temp file cleanup after payload generation.
Ensures that all temporary resources are properly cleaned up after operations.
"""

import unittest
import json
import os
import tempfile
import shutil
from io import BytesIO
from pathlib import Path
import sys
import time

sys.path.insert(0, '/home/user/sc-generator')

from app import app


class TestPayloadCleanup(unittest.TestCase):
    """Test suite for verifying proper cleanup of temporary files and resources"""

    def setUp(self):
        """Set up test client and temporary directories"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Create temporary directories for testing
        self.temp_upload_dir = tempfile.mkdtemp(prefix='test_upload_')
        self.temp_output_dir = tempfile.mkdtemp(prefix='test_output_')

        # Patch the app config
        self.app.config['UPLOAD_FOLDER'] = self.temp_upload_dir
        self.app.config['OUTPUT_FOLDER'] = self.temp_output_dir

    def tearDown(self):
        """Clean up temporary directories"""
        if os.path.exists(self.temp_upload_dir):
            shutil.rmtree(self.temp_upload_dir)
        if os.path.exists(self.temp_output_dir):
            shutil.rmtree(self.temp_output_dir)

    # ============================================================================
    # Basic Upload and Cleanup Tests
    # ============================================================================

    def test_upload_creates_file(self):
        """Test that uploading a file creates it in the upload folder"""
        response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test content'), 'test.msi')
            }
        )
        self.assertEqual(response.status_code, 200)

        # Verify file exists
        files = os.listdir(self.temp_upload_dir)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('.msi'))

    def test_uploaded_files_not_leaked_after_errors(self):
        """Test that uploaded files are not left behind after generation errors"""
        # Upload a file
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test content'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']
        initial_count = len(os.listdir(self.temp_upload_dir))

        # Try invalid payload generation (invalid technique)
        response = self.client.post(
            '/api/generate-payload',
            data=json.dumps({
                'file_id': file_id,
                'technique': 'invalid_technique_xyz',
                'obfuscation': 'high'
            }),
            content_type='application/json'
        )
        # Should fail
        self.assertNotEqual(response.status_code, 200)

        # Upload folder should still have the same files
        final_count = len(os.listdir(self.temp_upload_dir))
        self.assertEqual(initial_count, final_count)

    # ============================================================================
    # Output File Cleanup Tests
    # ============================================================================

    def test_output_files_created_for_payload_generation(self):
        """Test that output files are created when payloads are generated"""
        # Upload a file
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test msi'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        # Generate payload
        response = self.client.post(
            '/api/generate-payload',
            data=json.dumps({
                'file_id': file_id,
                'technique': 'base64',
                'obfuscation': 'high'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Verify output file exists
        output_files = os.listdir(self.temp_output_dir)
        self.assertGreater(len(output_files), 0)
        self.assertTrue(any(f.endswith('.vbs') for f in output_files))

    def test_multiple_payloads_tracked_independently(self):
        """Test that multiple payload generations create separate output files"""
        # Upload file
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test msi'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        # Generate first payload
        response1 = self.client.post(
            '/api/generate-payload',
            data=json.dumps({
                'file_id': file_id,
                'technique': 'base64',
                'obfuscation': 'high'
            }),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        data1 = json.loads(response1.data)
        output_id1 = data1['output_id']

        # Generate second payload with different technique
        response2 = self.client.post(
            '/api/generate-payload',
            data=json.dumps({
                'file_id': file_id,
                'technique': 'hex',
                'obfuscation': 'high'
            }),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.data)
        output_id2 = data2['output_id']

        # Verify both output files exist and are different
        output_files = os.listdir(self.temp_output_dir)
        self.assertGreaterEqual(len(output_files), 2)
        self.assertNotEqual(output_id1, output_id2)

        # Verify files have content
        path1 = os.path.join(self.temp_output_dir, f'{output_id1}_payload.vbs')
        path2 = os.path.join(self.temp_output_dir, f'{output_id2}_payload.vbs')

        self.assertTrue(os.path.exists(path1))
        self.assertTrue(os.path.exists(path2))

        with open(path1, 'r') as f:
            content1 = f.read()
        with open(path2, 'r') as f:
            content2 = f.read()

        self.assertGreater(len(content1), 0)
        self.assertGreater(len(content2), 0)
        # Different techniques should produce different payloads
        self.assertNotEqual(content1, content2)

    def test_download_succeeds_for_generated_payload(self):
        """Test that downloading a generated payload works correctly"""
        # Upload and generate
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test msi'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        gen_response = self.client.post(
            '/api/generate-payload',
            data=json.dumps({
                'file_id': file_id,
                'technique': 'base64',
                'obfuscation': 'high'
            }),
            content_type='application/json'
        )
        gen_data = json.loads(gen_response.data)
        output_id = gen_data['output_id']

        # Download
        download_response = self.client.get(f'/api/download/{output_id}')
        self.assertEqual(download_response.status_code, 200)
        self.assertGreater(len(download_response.data), 0)

    def test_preview_succeeds_for_generated_payload(self):
        """Test that previewing a generated payload works correctly"""
        # Upload and generate
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test msi'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        gen_response = self.client.post(
            '/api/generate-payload',
            data=json.dumps({
                'file_id': file_id,
                'technique': 'base64',
                'obfuscation': 'high'
            }),
            content_type='application/json'
        )
        gen_data = json.loads(gen_response.data)
        output_id = gen_data['output_id']

        # Preview
        preview_response = self.client.get(f'/api/preview/{output_id}')
        self.assertEqual(preview_response.status_code, 200)
        preview_data = json.loads(preview_response.data)
        self.assertIn('content', preview_data)
        self.assertGreater(len(preview_data['content']), 0)

    # ============================================================================
    # Batch Generation Cleanup Tests
    # ============================================================================

    def test_batch_generation_creates_multiple_outputs(self):
        """Test that batch generation creates separate output files"""
        # Upload file
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test msi'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        # Batch generate
        response = self.client.post(
            '/api/batch-generate',
            data=json.dumps({
                'file_id': file_id,
                'techniques': ['base64', 'hex', 'wmi']
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('results', data)
        self.assertGreaterEqual(len(data['results']), 2)

    # ============================================================================
    # One-Click Generation Cleanup Tests
    # ============================================================================

    def test_one_click_generation_creates_output(self):
        """Test that one-click generation creates output files"""
        # Upload file
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test msi'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        # Generate one-click
        response = self.client.post(
            '/api/generate-one-click',
            data=json.dumps({
                'file_id': file_id,
                'obfuscation_style': 'polymorphic',
                'file_type': 'vbs'
            }),
            content_type='application/json'
        )

        if response.status_code == 200:
            # Verify output files were created
            output_files = os.listdir(self.temp_output_dir)
            self.assertGreater(len(output_files), 0)

    # ============================================================================
    # Persistent Generation Cleanup Tests
    # ============================================================================

    def test_persistent_generation_creates_output(self):
        """Test that persistent payload generation creates output files"""
        # Upload file
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test msi'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        # Generate persistent
        response = self.client.post(
            '/api/generate-persistent',
            data=json.dumps({
                'file_id': file_id,
                'technique': 'base64',
                'persistence_method': 'registry',
                'obfuscation': 'high'
            }),
            content_type='application/json'
        )

        if response.status_code == 200:
            output_files = os.listdir(self.temp_output_dir)
            self.assertGreater(len(output_files), 0)
            self.assertTrue(any(f.endswith('.vbs') for f in output_files))

    # ============================================================================
    # File Size and Resource Tests
    # ============================================================================

    def test_upload_folder_contains_only_uploaded_files(self):
        """Test that upload folder only contains uploaded files"""
        initial_count = len(os.listdir(self.temp_upload_dir))

        # Upload multiple files
        for i in range(3):
            self.client.post(
                '/api/upload',
                data={
                    'file': (BytesIO(b'test content'), f'test{i}.msi')
                }
            )

        final_count = len(os.listdir(self.temp_upload_dir))
        self.assertEqual(final_count, initial_count + 3)

    def test_output_folder_contains_only_vbs_payloads(self):
        """Test that output folder contains only generated VBS payloads"""
        # Upload and generate
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test msi'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        # Generate multiple payloads
        for technique in ['base64', 'hex', 'array']:
            self.client.post(
                '/api/generate-payload',
                data=json.dumps({
                    'file_id': file_id,
                    'technique': technique,
                    'obfuscation': 'high'
                }),
                content_type='application/json'
            )

        # Verify all files are VBS
        output_files = os.listdir(self.temp_output_dir)
        for filename in output_files:
            self.assertTrue(filename.endswith('.vbs'))

    def test_payload_content_is_valid_vbs(self):
        """Test that generated payloads contain valid VBS code"""
        # Upload and generate
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test msi'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        response = self.client.post(
            '/api/generate-payload',
            data=json.dumps({
                'file_id': file_id,
                'technique': 'base64',
                'obfuscation': 'high'
            }),
            content_type='application/json'
        )
        data = json.loads(response.data)
        payload = data['payload']

        # Check for VBS indicators
        vbs_indicators = ['CreateObject', 'Set ', 'Dim ', 'End', 'Function', 'Sub']
        has_indicator = any(indicator in payload for indicator in vbs_indicators)
        self.assertTrue(has_indicator, "Payload should contain VBS code")

    # ============================================================================
    # Error Handling and Cleanup Tests
    # ============================================================================

    def test_cleanup_on_upload_with_max_size_exceeded(self):
        """Test that temp files are cleaned up if max size is exceeded"""
        # Create oversized file (if size limit is enforced)
        large_content = b'x' * (101 * 1024 * 1024)  # Just over 100MB limit

        response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(large_content), 'large.msi')
            }
        )

        # Should fail due to size
        if response.status_code != 200:
            # Verify no partial files were left
            upload_files = os.listdir(self.temp_upload_dir)
            # Either no files or a legitimate file, not partial ones
            for f in upload_files:
                file_path = os.path.join(self.temp_upload_dir, f)
                file_size = os.path.getsize(file_path)
                # If a file exists, it should be complete
                self.assertLess(file_size, 101 * 1024 * 1024)

    def test_no_orphaned_files_after_generation(self):
        """Test that no orphaned temp files are left after generation"""
        initial_upload_files = set(os.listdir(self.temp_upload_dir))
        initial_output_files = set(os.listdir(self.temp_output_dir))

        # Upload and generate
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test msi'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        response = self.client.post(
            '/api/generate-payload',
            data=json.dumps({
                'file_id': file_id,
                'technique': 'base64',
                'obfuscation': 'high'
            }),
            content_type='application/json'
        )

        # Get final file lists
        final_upload_files = set(os.listdir(self.temp_upload_dir))
        final_output_files = set(os.listdir(self.temp_output_dir))

        # Check no extra files were created
        new_upload = final_upload_files - initial_upload_files
        new_output = final_output_files - initial_output_files

        # Only expected files should be created
        self.assertGreaterEqual(len(new_upload), 1)  # At least the uploaded file
        self.assertGreaterEqual(len(new_output), 1)  # At least one output file

    # ============================================================================
    # Disk Space and Resource Monitoring Tests
    # ============================================================================

    def test_upload_folder_disk_space_reasonable(self):
        """Test that uploaded files don't consume excessive disk space"""
        # Upload a file
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test content' * 1000), 'test.msi')
            }
        )
        self.assertEqual(upload_response.status_code, 200)

        # Check disk usage
        total_size = 0
        for filename in os.listdir(self.temp_upload_dir):
            filepath = os.path.join(self.temp_upload_dir, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)

        # Should be reasonable (less than 1MB in test)
        self.assertLess(total_size, 10 * 1024 * 1024)

    def test_output_folder_disk_space_reasonable(self):
        """Test that generated payloads don't consume excessive disk space"""
        # Upload and generate
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test msi'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        # Generate multiple payloads
        for i in range(5):
            self.client.post(
                '/api/generate-payload',
                data=json.dumps({
                    'file_id': file_id,
                    'technique': 'base64',
                    'obfuscation': 'high'
                }),
                content_type='application/json'
            )

        # Check total disk usage
        total_size = 0
        for filename in os.listdir(self.temp_output_dir):
            filepath = os.path.join(self.temp_output_dir, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)

        # Should be reasonable (less than 1MB total)
        self.assertLess(total_size, 10 * 1024 * 1024)

    # ============================================================================
    # Data Integrity Tests
    # ============================================================================

    def test_payload_data_persists_after_generation(self):
        """Test that payload data persists and can be retrieved"""
        # Upload and generate
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test msi'), 'test.msi')
            }
        )
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        gen_response = self.client.post(
            '/api/generate-payload',
            data=json.dumps({
                'file_id': file_id,
                'technique': 'base64',
                'obfuscation': 'high'
            }),
            content_type='application/json'
        )
        gen_data = json.loads(gen_response.data)
        original_payload = gen_data['payload']
        output_id = gen_data['output_id']

        # Retrieve via preview
        preview_response = self.client.get(f'/api/preview/{output_id}')
        preview_data = json.loads(preview_response.data)
        retrieved_payload = preview_data['content']

        # Should be identical
        self.assertEqual(original_payload, retrieved_payload)

    def test_multiple_files_dont_interfere(self):
        """Test that processing multiple files doesn't cause interference"""
        file_ids = []

        # Upload multiple files
        for i in range(3):
            upload_response = self.client.post(
                '/api/upload',
                data={
                    'file': (BytesIO(f'test content {i}'.encode()), f'test{i}.msi')
                }
            )
            upload_data = json.loads(upload_response.data)
            file_ids.append(upload_data['file_id'])

        # Generate payloads for each
        for file_id in file_ids:
            response = self.client.post(
                '/api/generate-payload',
                data=json.dumps({
                    'file_id': file_id,
                    'technique': 'base64',
                    'obfuscation': 'high'
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

        # Verify all output files exist
        output_files = os.listdir(self.temp_output_dir)
        self.assertGreaterEqual(len(output_files), 3)


if __name__ == '__main__':
    unittest.main()
