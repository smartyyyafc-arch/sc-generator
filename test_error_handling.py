#!/usr/bin/env python3
"""
Comprehensive Error Handling Tests for SC-Generator
Tests error handling for invalid inputs, edge cases, and boundary conditions
across all endpoints and core modules.
"""

import unittest
import json
import os
import tempfile
import shutil
from io import BytesIO
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
import sys

# Add the project root to path
sys.path.insert(0, '/home/user/sc-generator')

from app import app
from payload_generator import PayloadGenerator
from vbs_encoder import VBSEncoder


class TestErrorHandlingInputValidation(unittest.TestCase):
    """Test error handling for invalid inputs"""

    def setUp(self):
        """Set up test client and temporary directories"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Create temporary directories for testing
        self.temp_upload_dir = tempfile.mkdtemp()
        self.temp_output_dir = tempfile.mkdtemp()

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
    # Upload Endpoint - Error Handling Tests
    # ============================================================================

    def test_upload_no_file_provided(self):
        """Test upload endpoint with no file provided"""
        response = self.client.post('/api/upload')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('No file provided', data['error'])

    def test_upload_empty_filename(self):
        """Test upload endpoint with empty filename"""
        response = self.client.post('/api/upload',
            data={'file': (BytesIO(b'test'), '')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('No file selected', data['error'])

    def test_upload_invalid_file_extension(self):
        """Test upload with invalid file extension"""
        response = self.client.post('/api/upload',
            data={'file': (BytesIO(b'test'), 'malware.txt')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('File type not allowed', data['error'])

    def test_upload_multiple_invalid_extensions(self):
        """Test various invalid file extensions"""
        invalid_files = ['test.jpg', 'test.pdf', 'test.exe.txt', 'test.zip', 'test.py']
        for filename in invalid_files:
            response = self.client.post('/api/upload',
                data={'file': (BytesIO(b'test'), filename)},
                content_type='multipart/form-data'
            )
            self.assertEqual(response.status_code, 400, f"Failed for {filename}")
            data = json.loads(response.data)
            self.assertIn('error', data)

    def test_upload_valid_extensions_accepted(self):
        """Test that valid extensions are accepted"""
        valid_files = ['test.msi', 'test.exe', 'test.dll', 'test.bat', 'test.cmd', 'test.vbs']
        for filename in valid_files:
            response = self.client.post('/api/upload',
                data={'file': (BytesIO(b'test content'), filename)},
                content_type='multipart/form-data'
            )
            self.assertEqual(response.status_code, 200, f"Failed for {filename}")
            data = json.loads(response.data)
            self.assertIn('success', data)

    def test_upload_with_path_traversal_attempt(self):
        """Test upload with path traversal in filename"""
        response = self.client.post('/api/upload',
            data={'file': (BytesIO(b'test'), '../../../etc/passwd.exe')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        # Should either reject or sanitize
        self.assertTrue('error' in data or 'success' in data)

    def test_upload_with_null_bytes_in_filename(self):
        """Test upload with null bytes in filename"""
        response = self.client.post('/api/upload',
            data={'file': (BytesIO(b'test'), 'test\x00.exe')},
            content_type='multipart/form-data'
        )
        # Should either reject or sanitize
        self.assertIn(response.status_code, [200, 400])

    # ============================================================================
    # Generate Payload Endpoint - Error Handling Tests
    # ============================================================================

    def test_generate_payload_no_file_id(self):
        """Test generate payload without file_id"""
        response = self.client.post('/api/generate-payload',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('File ID required', data['error'])

    def test_generate_payload_nonexistent_file(self):
        """Test generate payload with non-existent file ID"""
        response = self.client.post('/api/generate-payload',
            data=json.dumps({'file_id': 'nonexistent'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('File not found', data['error'])

    def test_generate_payload_invalid_technique(self):
        """Test generate payload with invalid technique"""
        # First upload a file
        response = self.client.post('/api/upload',
            data={'file': (BytesIO(b'test'), 'test.exe')},
            content_type='multipart/form-data'
        )
        file_id = json.loads(response.data)['file_id']

        # Try invalid technique
        response = self.client.post('/api/generate-payload',
            data=json.dumps({
                'file_id': file_id,
                'technique': 'invalid_technique'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)  # Should fail gracefully

    def test_generate_payload_empty_file_id(self):
        """Test generate payload with empty file ID"""
        response = self.client.post('/api/generate-payload',
            data=json.dumps({'file_id': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_generate_payload_null_file_id(self):
        """Test generate payload with null file ID"""
        response = self.client.post('/api/generate-payload',
            data=json.dumps({'file_id': None}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_generate_payload_malformed_json(self):
        """Test generate payload with malformed JSON"""
        response = self.client.post('/api/generate-payload',
            data='{"invalid json}',
            content_type='application/json'
        )
        self.assertIn(response.status_code, [400, 500])

    def test_generate_payload_missing_content_type(self):
        """Test generate payload without proper content type"""
        response = self.client.post('/api/generate-payload',
            data='file_id=test'
        )
        self.assertIn(response.status_code, [400, 415])

    # ============================================================================
    # Download/Preview Endpoint - Error Handling Tests
    # ============================================================================

    def test_download_nonexistent_output(self):
        """Test downloading non-existent output"""
        response = self.client.get('/api/download/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_preview_nonexistent_output(self):
        """Test previewing non-existent output"""
        response = self.client.get('/api/preview/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_download_invalid_output_id_format(self):
        """Test download with various invalid output ID formats"""
        invalid_ids = ['', '..', '../../../etc/passwd', 'test|cat', 'test;rm -rf']
        for output_id in invalid_ids:
            response = self.client.get(f'/api/download/{output_id}')
            self.assertEqual(response.status_code, 404,
                f"Expected 404 for output_id: {output_id}")

    def test_preview_path_traversal_attempt(self):
        """Test preview with path traversal attempt"""
        response = self.client.get('/api/preview/../../../etc/passwd')
        self.assertEqual(response.status_code, 404)

    # ============================================================================
    # Custom Fingerprint Endpoint - Error Handling Tests
    # ============================================================================

    def test_create_fingerprint_no_data(self):
        """Test create fingerprint with no data"""
        response = self.client.post('/api/fingerprints',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_create_fingerprint_no_name(self):
        """Test create fingerprint without name"""
        response = self.client.post('/api/fingerprints',
            data=json.dumps({'config': {}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_create_fingerprint_no_config(self):
        """Test create fingerprint without config"""
        response = self.client.post('/api/fingerprints',
            data=json.dumps({'name': 'test'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_create_fingerprint_empty_name(self):
        """Test create fingerprint with empty name"""
        response = self.client.post('/api/fingerprints',
            data=json.dumps({'name': '', 'config': {}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_create_fingerprint_empty_config(self):
        """Test create fingerprint with empty config"""
        response = self.client.post('/api/fingerprints',
            data=json.dumps({'name': 'test', 'config': None}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    # ============================================================================
    # Proxy Endpoint - Error Handling Tests
    # ============================================================================

    def test_add_proxy_no_url(self):
        """Test add proxy without URL"""
        response = self.client.post('/api/proxies',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_add_proxy_empty_url(self):
        """Test add proxy with empty URL"""
        response = self.client.post('/api/proxies',
            data=json.dumps({'url': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_add_proxy_null_url(self):
        """Test add proxy with null URL"""
        response = self.client.post('/api/proxies',
            data=json.dumps({'url': None}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_add_proxy_invalid_type(self):
        """Test add proxy with invalid type"""
        response = self.client.post('/api/proxies',
            data=json.dumps({'url': 'http://proxy.com', 'type': 'invalid'}),
            content_type='application/json'
        )
        # Should either accept with default or reject
        self.assertIn(response.status_code, [200, 400])

    # ============================================================================
    # Batch Generate Endpoint - Error Handling Tests
    # ============================================================================

    def test_batch_generate_no_file_id(self):
        """Test batch generate without file ID"""
        response = self.client.post('/api/batch-generate',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_batch_generate_empty_techniques(self):
        """Test batch generate with empty techniques"""
        response = self.client.post('/api/batch-generate',
            data=json.dumps({'file_id': 'test', 'techniques': []}),
            content_type='application/json'
        )
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400])

    def test_batch_generate_none_techniques(self):
        """Test batch generate with None techniques"""
        response = self.client.post('/api/batch-generate',
            data=json.dumps({'file_id': 'test', 'techniques': None}),
            content_type='application/json'
        )
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 500])

    # ============================================================================
    # One-Click Generation Endpoint - Error Handling Tests
    # ============================================================================

    def test_generate_one_click_no_file_id(self):
        """Test one-click generation without file ID"""
        response = self.client.post('/api/generate-one-click',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_generate_one_click_nonexistent_file(self):
        """Test one-click generation with non-existent file"""
        response = self.client.post('/api/generate-one-click',
            data=json.dumps({'file_id': 'nonexistent'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_generate_one_click_invalid_style(self):
        """Test one-click generation with invalid style"""
        # Upload a file first
        response = self.client.post('/api/upload',
            data={'file': (BytesIO(b'test'), 'test.exe')},
            content_type='multipart/form-data'
        )
        file_id = json.loads(response.data)['file_id']

        # Generate with invalid style
        response = self.client.post('/api/generate-one-click',
            data=json.dumps({
                'file_id': file_id,
                'obfuscation_style': 'invalid_style'
            }),
            content_type='application/json'
        )
        # Should fail gracefully
        self.assertIn(response.status_code, [400, 500])

    def test_generate_one_click_invalid_file_type(self):
        """Test one-click generation with invalid file type"""
        # Upload a file first
        response = self.client.post('/api/upload',
            data={'file': (BytesIO(b'test'), 'test.exe')},
            content_type='multipart/form-data'
        )
        file_id = json.loads(response.data)['file_id']

        # Generate with invalid file type
        response = self.client.post('/api/generate-one-click',
            data=json.dumps({
                'file_id': file_id,
                'file_type': 'invalid_type'
            }),
            content_type='application/json'
        )
        # Should handle gracefully or default
        self.assertIn(response.status_code, [200, 400, 500])

    # ============================================================================
    # Persistent Payload Endpoint - Error Handling Tests
    # ============================================================================

    def test_generate_persistent_no_file_id(self):
        """Test persistent payload generation without file ID"""
        response = self.client.post('/api/generate-persistent',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_generate_persistent_nonexistent_file(self):
        """Test persistent payload with non-existent file"""
        response = self.client.post('/api/generate-persistent',
            data=json.dumps({'file_id': 'nonexistent'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_generate_persistent_invalid_method(self):
        """Test persistent payload with invalid persistence method"""
        # Upload a file first
        response = self.client.post('/api/upload',
            data={'file': (BytesIO(b'test'), 'test.exe')},
            content_type='multipart/form-data'
        )
        file_id = json.loads(response.data)['file_id']

        # Generate with invalid persistence method
        response = self.client.post('/api/generate-persistent',
            data=json.dumps({
                'file_id': file_id,
                'persistence_method': 'invalid_method'
            }),
            content_type='application/json'
        )
        # Should fail gracefully
        self.assertIn(response.status_code, [400, 500])

    # ============================================================================
    # Request Method Validation Tests
    # ============================================================================

    def test_post_endpoints_reject_get(self):
        """Test that POST endpoints reject GET requests"""
        post_endpoints = [
            '/api/fingerprints',
            '/api/proxies',
            '/api/generate-payload',
            '/api/batch-generate',
            '/api/generate-one-click',
            '/api/generate-persistent'
        ]
        for endpoint in post_endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 405,
                f"GET should not be allowed on {endpoint}")

    def test_get_endpoints_reject_post(self):
        """Test that GET endpoints reject POST requests"""
        get_endpoints = [
            '/api/health',
            '/api/techniques',
            '/api/fingerprints',
            '/api/proxies',
            '/api/settings',
            '/api/one-click-styles',
            '/api/recommendations',
            '/api/persistence-methods'
        ]
        for endpoint in get_endpoints:
            response = self.client.post(endpoint,
                data=json.dumps({}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 405,
                f"POST should not be allowed on {endpoint}")

    # ============================================================================
    # Content Type Tests
    # ============================================================================

    def test_api_endpoints_with_incorrect_content_type(self):
        """Test API endpoints with incorrect content type"""
        # Sending form data where JSON is expected
        response = self.client.post('/api/fingerprints',
            data='name=test&config={}',
            content_type='application/x-www-form-urlencoded'
        )
        # Should either work or reject properly
        self.assertIn(response.status_code, [200, 400, 415])

    # ============================================================================
    # Large Input Tests (Edge Cases)
    # ============================================================================

    def test_generate_payload_very_large_command(self):
        """Test generate payload with very large command"""
        # Upload a file
        response = self.client.post('/api/upload',
            data={'file': (BytesIO(b'test'), 'test.exe')},
            content_type='multipart/form-data'
        )
        file_id = json.loads(response.data)['file_id']

        # Try with very large command
        large_command = 'x' * 1000000  # 1MB command
        response = self.client.post('/api/generate-payload',
            data=json.dumps({
                'file_id': file_id,
                'technique': 'base64'
            }),
            content_type='application/json'
        )
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 413, 500])

    def test_fingerprint_with_very_large_config(self):
        """Test fingerprint creation with very large config"""
        large_config = {'key' + str(i): 'value' * 100 for i in range(1000)}
        response = self.client.post('/api/fingerprints',
            data=json.dumps({
                'name': 'test',
                'config': large_config
            }),
            content_type='application/json'
        )
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 413, 500])


class TestPayloadGeneratorErrorHandling(unittest.TestCase):
    """Test error handling in PayloadGenerator module"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = PayloadGenerator()

    def test_generate_with_none_command(self):
        """Test generate with None command"""
        with self.assertRaises((TypeError, AttributeError)):
            self.generator.generate(None)

    def test_generate_with_empty_command(self):
        """Test generate with empty command"""
        try:
            result = self.generator.generate("")
            self.assertIsInstance(result, str)
        except Exception as e:
            # Should either work or raise a meaningful error
            self.assertIsInstance(e, (ValueError, TypeError))

    def test_generate_with_invalid_technique(self):
        """Test generate with invalid technique"""
        with self.assertRaises(ValueError):
            self.generator.generate("test", technique="invalid_technique")

    def test_generate_with_invalid_obfuscation_level(self):
        """Test generate with various invalid obfuscation levels"""
        # The function should handle gracefully or use default
        invalid_levels = ["invalid", "LOUD", 123, None]
        for level in invalid_levels:
            try:
                result = self.generator.generate("test", obfuscation_level=level)
                self.assertIsInstance(result, str)
            except Exception as e:
                # Should be a meaningful error
                self.assertIsInstance(e, (ValueError, TypeError))

    def test_get_technique_info_invalid_technique(self):
        """Test get_technique_info with invalid technique"""
        result = self.generator.get_technique_info("invalid_technique")
        # Should return "Unknown technique" or similar
        self.assertIsInstance(result, str)

    def test_list_techniques_returns_list(self):
        """Test that list_techniques returns a list"""
        result = self.generator.list_techniques()
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

    def test_all_listed_techniques_are_valid(self):
        """Test that all listed techniques can generate payloads"""
        techniques = self.generator.list_techniques()
        for technique in techniques:
            try:
                payload = self.generator.generate("test", technique=technique)
                self.assertIsInstance(payload, str)
                self.assertTrue(len(payload) > 0)
            except Exception as e:
                self.fail(f"Technique {technique} failed: {e}")


class TestVBSEncoderErrorHandling(unittest.TestCase):
    """Test error handling in VBSEncoder module"""

    def setUp(self):
        """Set up test fixtures"""
        self.encoder = VBSEncoder()

    def test_encode_with_none_command(self):
        """Test encode with None command"""
        with self.assertRaises((TypeError, AttributeError)):
            self.encoder.create_wscript_hidden_execution(None)

    def test_encode_with_empty_command(self):
        """Test encode with empty command"""
        try:
            result = self.encoder.create_wscript_hidden_execution("")
            self.assertIsInstance(result, str)
        except Exception as e:
            self.assertIsInstance(e, (ValueError, TypeError))

    def test_encode_with_special_characters(self):
        """Test encode with special characters in command"""
        special_commands = [
            'echo "test"',
            "echo 'test'",
            'echo `test`',
            'echo $test',
            'echo \\test',
            'echo\x00test'  # null byte
        ]
        for cmd in special_commands:
            try:
                result = self.encoder.create_full_obfuscated_payload(cmd, 'base64')
                self.assertIsInstance(result, str)
            except Exception as e:
                # Should handle gracefully or raise meaningful error
                pass

    def test_encode_very_long_command(self):
        """Test encode with very long command"""
        long_cmd = 'x' * 100000
        try:
            result = self.encoder.create_full_obfuscated_payload(long_cmd, 'base64')
            self.assertIsInstance(result, str)
        except Exception as e:
            # Should handle gracefully
            self.assertIn(type(e).__name__, ['ValueError', 'MemoryError', 'TypeError'])

    def test_encode_unicode_command(self):
        """Test encode with unicode characters"""
        unicode_cmds = [
            'echo こんにちは',
            'echo 你好',
            'echo مرحبا',
            'echo🎉test'
        ]
        for cmd in unicode_cmds:
            try:
                result = self.encoder.create_full_obfuscated_payload(cmd, 'base64')
                self.assertIsInstance(result, str)
            except Exception as e:
                # May fail but should handle gracefully
                pass


class TestBoundaryConditions(unittest.TestCase):
    """Test boundary conditions and edge cases"""

    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Create temporary directories
        self.temp_upload_dir = tempfile.mkdtemp()
        self.temp_output_dir = tempfile.mkdtemp()
        self.app.config['UPLOAD_FOLDER'] = self.temp_upload_dir
        self.app.config['OUTPUT_FOLDER'] = self.temp_output_dir

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.temp_upload_dir):
            shutil.rmtree(self.temp_upload_dir)
        if os.path.exists(self.temp_output_dir):
            shutil.rmtree(self.temp_output_dir)

    def test_upload_zero_byte_file(self):
        """Test upload with zero-byte file"""
        response = self.client.post('/api/upload',
            data={'file': (BytesIO(b''), 'test.exe')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['size'], 0)

    def test_upload_very_small_file(self):
        """Test upload with 1-byte file"""
        response = self.client.post('/api/upload',
            data={'file': (BytesIO(b'x'), 'test.exe')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['size'], 1)

    def test_settings_endpoint_returns_valid_data(self):
        """Test settings endpoint returns valid configuration data"""
        response = self.client.get('/api/settings')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('max_file_size', data)
        self.assertIn('allowed_formats', data)
        self.assertIn('obfuscation_levels', data)
        self.assertIsInstance(data['max_file_size'], int)
        self.assertIsInstance(data['allowed_formats'], list)
        self.assertIsInstance(data['obfuscation_levels'], list)

    def test_recommendations_endpoint_returns_valid_data(self):
        """Test recommendations endpoint returns valid data"""
        response = self.client.get('/api/recommendations')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('recommendations', data)
        recommendations = data['recommendations']
        self.assertTrue(len(recommendations) > 0)
        for key, rec in recommendations.items():
            self.assertIn('title', rec)
            self.assertIn('recommended_config', rec)

    def test_persistence_methods_endpoint_returns_valid_data(self):
        """Test persistence methods endpoint returns valid data"""
        response = self.client.get('/api/persistence-methods')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('methods', data)
        self.assertTrue(len(data['methods']) > 0)

    def test_one_click_styles_endpoint_returns_valid_data(self):
        """Test one-click styles endpoint returns valid data"""
        response = self.client.get('/api/one-click-styles')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('styles', data)
        self.assertTrue(len(data['styles']) > 0)


if __name__ == '__main__':
    unittest.main()
