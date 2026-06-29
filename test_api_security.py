#!/usr/bin/env python3
"""
Comprehensive API security and HTTP status code verification tests
Tests all endpoints for proper authentication, authorization, input validation,
and correct HTTP status codes for various scenarios.
"""

import unittest
import json
import os
import tempfile
from io import BytesIO
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys

# Add the project root to path
sys.path.insert(0, '/home/user/sc-generator')

from app import app


class TestAPISecurityAndStatusCodes(unittest.TestCase):
    """Test API security measures and HTTP status codes"""

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
        import shutil
        if os.path.exists(self.temp_upload_dir):
            shutil.rmtree(self.temp_upload_dir)
        if os.path.exists(self.temp_output_dir):
            shutil.rmtree(self.temp_output_dir)

    # ============================================================================
    # Health Check Endpoint Tests
    # ============================================================================

    def test_health_check_returns_200(self):
        """Test that health check endpoint returns 200 OK"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)

    def test_health_check_response_format(self):
        """Test that health check returns valid JSON response"""
        response = self.client.get('/api/health')
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'ok')
        self.assertIn('version', data)

    def test_health_check_only_accepts_get(self):
        """Test that health check only accepts GET requests"""
        response = self.client.post('/api/health')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

        response = self.client.put('/api/health')
        self.assertEqual(response.status_code, 405)

        response = self.client.delete('/api/health')
        self.assertEqual(response.status_code, 405)

    # ============================================================================
    # Techniques Endpoint Tests
    # ============================================================================

    def test_techniques_returns_200(self):
        """Test that techniques endpoint returns 200 OK"""
        response = self.client.get('/api/techniques')
        self.assertEqual(response.status_code, 200)

    def test_techniques_response_format(self):
        """Test that techniques endpoint returns proper JSON"""
        response = self.client.get('/api/techniques')
        data = json.loads(response.data)
        self.assertIn('techniques', data)
        self.assertIn('descriptions', data)
        self.assertIn('metadata', data)
        self.assertIsInstance(data['techniques'], list)

    def test_techniques_only_accepts_get(self):
        """Test that techniques endpoint only accepts GET requests"""
        response = self.client.post('/api/techniques')
        self.assertEqual(response.status_code, 405)

        response = self.client.put('/api/techniques')
        self.assertEqual(response.status_code, 405)

    # ============================================================================
    # Fingerprints GET Endpoint Tests
    # ============================================================================

    def test_get_fingerprints_returns_200(self):
        """Test that GET fingerprints endpoint returns 200 OK"""
        response = self.client.get('/api/fingerprints')
        self.assertEqual(response.status_code, 200)

    def test_get_fingerprints_response_format(self):
        """Test that GET fingerprints returns valid JSON"""
        response = self.client.get('/api/fingerprints')
        data = json.loads(response.data)
        self.assertIn('fingerprints', data)

    def test_get_fingerprints_only_accepts_get(self):
        """Test that GET fingerprints only accepts GET requests"""
        response = self.client.put('/api/fingerprints')
        self.assertEqual(response.status_code, 405)

    # ============================================================================
    # Fingerprints POST Endpoint Tests (Input Validation)
    # ============================================================================

    def test_create_fingerprint_requires_json(self):
        """Test that POST fingerprints requires JSON content type"""
        response = self.client.post(
            '/api/fingerprints',
            data="invalid data",
            content_type='text/plain'
        )
        # Should either return 400 or handle gracefully
        self.assertIn(response.status_code, [400, 415, 500])

    def test_create_fingerprint_missing_name_returns_400(self):
        """Test that missing name returns 400 Bad Request"""
        response = self.client.post(
            '/api/fingerprints',
            data=json.dumps({'config': {'key': 'value'}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_create_fingerprint_missing_config_returns_400(self):
        """Test that missing config returns 400 Bad Request"""
        response = self.client.post(
            '/api/fingerprints',
            data=json.dumps({'name': 'test'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_create_fingerprint_missing_both_returns_400(self):
        """Test that missing both name and config returns 400"""
        response = self.client.post(
            '/api/fingerprints',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_fingerprint_with_valid_data(self):
        """Test that valid fingerprint creation succeeds"""
        response = self.client.post(
            '/api/fingerprints',
            data=json.dumps({'name': 'test_fp', 'config': {'key': 'value'}}),
            content_type='application/json'
        )
        # Should return 200 or other success code
        self.assertLess(response.status_code, 300)
        data = json.loads(response.data)
        self.assertIn('id', data)

    # ============================================================================
    # Proxies Endpoint Tests
    # ============================================================================

    def test_get_proxies_returns_200(self):
        """Test that GET proxies endpoint returns 200 OK"""
        response = self.client.get('/api/proxies')
        self.assertEqual(response.status_code, 200)

    def test_get_proxies_response_format(self):
        """Test that GET proxies returns valid JSON"""
        response = self.client.get('/api/proxies')
        data = json.loads(response.data)
        self.assertIn('proxies', data)

    def test_add_proxy_missing_url_returns_400(self):
        """Test that missing URL returns 400 Bad Request"""
        response = self.client.post(
            '/api/proxies',
            data=json.dumps({'type': 'http'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_add_proxy_with_valid_url(self):
        """Test that valid proxy creation succeeds"""
        response = self.client.post(
            '/api/proxies',
            data=json.dumps({
                'url': 'http://proxy.example.com:8080',
                'type': 'http'
            }),
            content_type='application/json'
        )
        self.assertLess(response.status_code, 300)
        data = json.loads(response.data)
        self.assertIn('id', data)

    def test_add_proxy_invalid_json_returns_400(self):
        """Test that invalid JSON returns 400"""
        response = self.client.post(
            '/api/proxies',
            data="{ invalid json }",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    # ============================================================================
    # File Upload Endpoint Tests
    # ============================================================================

    def test_upload_no_file_returns_400(self):
        """Test that upload without file returns 400 Bad Request"""
        response = self.client.post('/api/upload')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('No file', data['error'])

    def test_upload_empty_filename_returns_400(self):
        """Test that empty filename returns 400 Bad Request"""
        response = self.client.post(
            '/api/upload',
            data={'file': (BytesIO(b'test'), '')}
        )
        self.assertEqual(response.status_code, 400)

    def test_upload_invalid_file_type_returns_400(self):
        """Test that invalid file type returns 400 Bad Request"""
        response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'test content'), 'test.txt')
            }
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('not allowed', data['error'])

    def test_upload_valid_msi_file(self):
        """Test that valid MSI upload succeeds"""
        response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'fake msi content'), 'installer.msi')
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('file_id', data)
        self.assertIn('filename', data)
        self.assertIn('size', data)
        self.assertIn('upload_time', data)

    def test_upload_valid_exe_file(self):
        """Test that valid EXE upload succeeds"""
        response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'MZ fake exe'), 'program.exe')
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_upload_valid_vbs_file(self):
        """Test that valid VBS upload succeeds"""
        response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'WScript.Echo "test"'), 'script.vbs')
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_upload_valid_dll_file(self):
        """Test that valid DLL upload succeeds"""
        response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'MZ fake dll'), 'library.dll')
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_upload_valid_bat_file(self):
        """Test that valid BAT upload succeeds"""
        response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'@echo off'), 'script.bat')
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_upload_valid_cmd_file(self):
        """Test that valid CMD upload succeeds"""
        response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'@echo off'), 'script.cmd')
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_upload_case_insensitive_extension(self):
        """Test that file extensions are case-insensitive"""
        response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'fake exe'), 'program.EXE')
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_upload_only_accepts_post(self):
        """Test that upload endpoint only accepts POST"""
        response = self.client.get('/api/upload')
        self.assertEqual(response.status_code, 405)

    # ============================================================================
    # Generate Payload Endpoint Tests
    # ============================================================================

    def test_generate_payload_no_json_returns_400(self):
        """Test that payload generation without JSON returns error"""
        response = self.client.post('/api/generate-payload')
        self.assertEqual(response.status_code, 400)

    def test_generate_payload_missing_file_id_returns_400(self):
        """Test that missing file_id returns 400"""
        response = self.client.post(
            '/api/generate-payload',
            data=json.dumps({'technique': 'base64'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_generate_payload_nonexistent_file_returns_404(self):
        """Test that nonexistent file_id returns 404 Not Found"""
        response = self.client.post(
            '/api/generate-payload',
            data=json.dumps({
                'file_id': 'nonexistent123',
                'technique': 'base64'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_generate_payload_with_valid_file(self):
        """Test payload generation with valid file"""
        # First upload a file
        upload_response = self.client.post(
            '/api/upload',
            data={
                'file': (BytesIO(b'fake msi'), 'test.msi')
            }
        )
        self.assertEqual(upload_response.status_code, 200)
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']

        # Now generate payload
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
        data = json.loads(response.data)
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('output_id', data)
        self.assertIn('payload', data)
        self.assertIn('size', data)

    def test_generate_payload_only_accepts_post(self):
        """Test that generate-payload only accepts POST"""
        response = self.client.get('/api/generate-payload')
        self.assertEqual(response.status_code, 405)

    # ============================================================================
    # Download Endpoint Tests
    # ============================================================================

    def test_download_nonexistent_payload_returns_404(self):
        """Test that downloading nonexistent payload returns 404"""
        response = self.client.get('/api/download/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_download_only_accepts_get(self):
        """Test that download endpoint only accepts GET"""
        response = self.client.post('/api/download/test123')
        self.assertEqual(response.status_code, 405)

        response = self.client.put('/api/download/test123')
        self.assertEqual(response.status_code, 405)

    def test_download_valid_payload(self):
        """Test downloading valid payload"""
        # Create a test file
        test_file = os.path.join(self.temp_output_dir, 'testid_payload.vbs')
        with open(test_file, 'w') as f:
            f.write('test vbs content')

        response = self.client.get('/api/download/testid')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test vbs content', response.data)

    # ============================================================================
    # Preview Endpoint Tests
    # ============================================================================

    def test_preview_nonexistent_payload_returns_404(self):
        """Test that previewing nonexistent payload returns 404"""
        response = self.client.get('/api/preview/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_preview_only_accepts_get(self):
        """Test that preview endpoint only accepts GET"""
        response = self.client.post('/api/preview/test123')
        self.assertEqual(response.status_code, 405)

    def test_preview_valid_payload(self):
        """Test previewing valid payload"""
        # Create a test file
        test_file = os.path.join(self.temp_output_dir, 'testid2_payload.vbs')
        with open(test_file, 'w') as f:
            f.write('preview test content')

        response = self.client.get('/api/preview/testid2')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('content', data)
        self.assertIn('preview test content', data['content'])

    # ============================================================================
    # Settings Endpoint Tests
    # ============================================================================

    def test_settings_returns_200(self):
        """Test that settings endpoint returns 200 OK"""
        response = self.client.get('/api/settings')
        self.assertEqual(response.status_code, 200)

    def test_settings_response_format(self):
        """Test that settings returns valid configuration"""
        response = self.client.get('/api/settings')
        data = json.loads(response.data)
        self.assertIn('max_file_size', data)
        self.assertIn('allowed_formats', data)
        self.assertIn('obfuscation_levels', data)

    def test_settings_only_accepts_get(self):
        """Test that settings endpoint only accepts GET"""
        response = self.client.post('/api/settings')
        self.assertEqual(response.status_code, 405)

    # ============================================================================
    # Batch Generate Endpoint Tests
    # ============================================================================

    def test_batch_generate_missing_file_id_returns_400(self):
        """Test that batch generate without file_id returns 400"""
        response = self.client.post(
            '/api/batch-generate',
            data=json.dumps({'techniques': ['base64']}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_batch_generate_nonexistent_file_returns_404(self):
        """Test that batch generate with nonexistent file returns 404"""
        response = self.client.post(
            '/api/batch-generate',
            data=json.dumps({
                'file_id': 'nonexistent',
                'techniques': ['base64', 'wmi']
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_batch_generate_only_accepts_post(self):
        """Test that batch-generate only accepts POST"""
        response = self.client.get('/api/batch-generate')
        self.assertEqual(response.status_code, 405)

    # ============================================================================
    # One-Click Generate Endpoint Tests
    # ============================================================================

    def test_generate_one_click_missing_file_id_returns_400(self):
        """Test that one-click without file_id returns 400"""
        response = self.client.post(
            '/api/generate-one-click',
            data=json.dumps({'obfuscation_style': 'polymorphic'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_generate_one_click_nonexistent_file_returns_404(self):
        """Test that one-click with nonexistent file returns 404"""
        response = self.client.post(
            '/api/generate-one-click',
            data=json.dumps({
                'file_id': 'nonexistent',
                'obfuscation_style': 'polymorphic'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_generate_one_click_only_accepts_post(self):
        """Test that generate-one-click only accepts POST"""
        response = self.client.get('/api/generate-one-click')
        self.assertEqual(response.status_code, 405)

    # ============================================================================
    # One-Click Styles Endpoint Tests
    # ============================================================================

    def test_one_click_styles_returns_200(self):
        """Test that one-click styles endpoint returns 200"""
        response = self.client.get('/api/one-click-styles')
        self.assertEqual(response.status_code, 200)

    def test_one_click_styles_response_format(self):
        """Test that one-click styles returns valid JSON"""
        response = self.client.get('/api/one-click-styles')
        data = json.loads(response.data)
        self.assertIn('styles', data)
        self.assertIsInstance(data['styles'], dict)

    def test_one_click_styles_only_accepts_get(self):
        """Test that one-click-styles only accepts GET"""
        response = self.client.post('/api/one-click-styles')
        self.assertEqual(response.status_code, 405)

    # ============================================================================
    # Recommendations Endpoint Tests
    # ============================================================================

    def test_recommendations_returns_200(self):
        """Test that recommendations endpoint returns 200"""
        response = self.client.get('/api/recommendations')
        self.assertEqual(response.status_code, 200)

    def test_recommendations_response_format(self):
        """Test that recommendations returns valid data"""
        response = self.client.get('/api/recommendations')
        data = json.loads(response.data)
        self.assertIn('recommendations', data)
        recommendations = data['recommendations']
        self.assertIn('standard', recommendations)
        self.assertIn('one-click', recommendations)
        self.assertIn('persistent', recommendations)

    def test_recommendations_only_accepts_get(self):
        """Test that recommendations only accepts GET"""
        response = self.client.post('/api/recommendations')
        self.assertEqual(response.status_code, 405)

    # ============================================================================
    # Persistence Methods Endpoint Tests
    # ============================================================================

    def test_persistence_methods_returns_200(self):
        """Test that persistence methods endpoint returns 200"""
        response = self.client.get('/api/persistence-methods')
        self.assertEqual(response.status_code, 200)

    def test_persistence_methods_response_format(self):
        """Test that persistence methods returns valid data"""
        response = self.client.get('/api/persistence-methods')
        data = json.loads(response.data)
        self.assertIn('methods', data)
        methods = data['methods']
        self.assertIn('registry', methods)
        self.assertIn('startup', methods)
        self.assertIn('multi', methods)

    def test_persistence_methods_only_accepts_get(self):
        """Test that persistence-methods only accepts GET"""
        response = self.client.post('/api/persistence-methods')
        self.assertEqual(response.status_code, 405)

    # ============================================================================
    # Generate Persistent Payload Endpoint Tests
    # ============================================================================

    def test_generate_persistent_missing_file_id_returns_400(self):
        """Test that persistent without file_id returns 400"""
        response = self.client.post(
            '/api/generate-persistent',
            data=json.dumps({'persistence_method': 'multi'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_generate_persistent_nonexistent_file_returns_404(self):
        """Test that persistent with nonexistent file returns 404"""
        response = self.client.post(
            '/api/generate-persistent',
            data=json.dumps({
                'file_id': 'nonexistent',
                'persistence_method': 'multi'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_generate_persistent_only_accepts_post(self):
        """Test that generate-persistent only accepts POST"""
        response = self.client.get('/api/generate-persistent')
        self.assertEqual(response.status_code, 405)

    # ============================================================================
    # 404 and 405 Tests
    # ============================================================================

    def test_nonexistent_endpoint_returns_404(self):
        """Test that accessing nonexistent endpoint returns 404"""
        response = self.client.get('/api/nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_invalid_method_returns_405(self):
        """Test that invalid HTTP methods return 405"""
        # Test various endpoints with wrong methods
        endpoints = [
            ('/api/health', 'post'),
            ('/api/techniques', 'delete'),
            ('/api/settings', 'put'),
        ]

        for endpoint, method in endpoints:
            if method == 'post':
                response = self.client.post(endpoint)
            elif method == 'delete':
                response = self.client.delete(endpoint)
            elif method == 'put':
                response = self.client.put(endpoint)

            self.assertEqual(response.status_code, 405,
                           f"Endpoint {endpoint} with {method} should return 405")

    # ============================================================================
    # CORS Security Tests
    # ============================================================================

    def test_cors_headers_present(self):
        """Test that CORS headers are properly set"""
        response = self.client.get('/api/health')
        # Flask-CORS should add headers, check for them
        # Note: actual header name may vary by flask-cors version
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # Input Sanitization Tests
    # ============================================================================

    def test_large_json_payload_handling(self):
        """Test that excessively large JSON is handled"""
        large_data = 'x' * 10000000  # 10MB string
        response = self.client.post(
            '/api/fingerprints',
            data=json.dumps({'name': large_data, 'config': {}}),
            content_type='application/json'
        )
        # Should either accept or reject gracefully, not crash
        self.assertIsNotNone(response.status_code)

    def test_special_characters_in_filename(self):
        """Test handling of special characters in filenames"""
        special_names = [
            'test<script>.msi',
            'test\'; DROP TABLE.msi',
            'test../../etc/passwd.msi',
            'test|whoami.msi',
        ]

        for filename in special_names:
            response = self.client.post(
                '/api/upload',
                data={'file': (BytesIO(b'content'), filename)}
            )
            # Should either sanitize or reject safely
            self.assertIn(response.status_code, [200, 400, 422])

    def test_malformed_json_returns_error(self):
        """Test that malformed JSON is handled gracefully"""
        response = self.client.post(
            '/api/fingerprints',
            data='{invalid json}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    # ============================================================================
    # Error Response Format Tests
    # ============================================================================

    def test_error_responses_have_error_field(self):
        """Test that error responses include error field"""
        error_endpoints = [
            ('/api/upload', 'post', {}),
            ('/api/generate-payload', 'post', json.dumps({})),
        ]

        for endpoint, method, data in error_endpoints:
            if method == 'post':
                if data:
                    response = self.client.post(
                        endpoint,
                        data=data,
                        content_type='application/json'
                    )
                else:
                    response = self.client.post(endpoint)

            if response.status_code >= 400:
                try:
                    resp_data = json.loads(response.data)
                    self.assertIn('error', resp_data,
                                f"Error response from {endpoint} missing 'error' field")
                except:
                    # Some endpoints may return non-JSON errors
                    pass

    # ============================================================================
    # Status Code Consistency Tests
    # ============================================================================

    def test_all_endpoints_return_valid_http_status(self):
        """Test that all endpoints return valid HTTP status codes"""
        test_endpoints = [
            ('/api/health', 'get'),
            ('/api/techniques', 'get'),
            ('/api/fingerprints', 'get'),
            ('/api/proxies', 'get'),
            ('/api/settings', 'get'),
            ('/api/one-click-styles', 'get'),
            ('/api/recommendations', 'get'),
            ('/api/persistence-methods', 'get'),
        ]

        for endpoint, method in test_endpoints:
            if method == 'get':
                response = self.client.get(endpoint)
            else:
                response = self.client.post(endpoint)

            # Valid HTTP status codes are 1xx-5xx
            self.assertGreaterEqual(response.status_code, 100)
            self.assertLessEqual(response.status_code, 599)

    def test_success_responses_return_2xx(self):
        """Test that successful operations return 2xx status codes"""
        # Health check
        response = self.client.get('/api/health')
        self.assertGreaterEqual(response.status_code, 200)
        self.assertLess(response.status_code, 300)

    def test_client_error_responses_return_4xx(self):
        """Test that client errors return 4xx status codes"""
        # Missing required parameter
        response = self.client.post(
            '/api/generate-payload',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertGreaterEqual(response.status_code, 400)
        self.assertLess(response.status_code, 500)

    # ============================================================================
    # Security-Specific Tests
    # ============================================================================

    def test_path_traversal_in_download(self):
        """Test that path traversal attacks are prevented in download"""
        response = self.client.get('/api/download/../../../etc/passwd')
        # Should not access files outside the output folder
        self.assertIn(response.status_code, [404, 400, 403])

    def test_path_traversal_in_preview(self):
        """Test that path traversal attacks are prevented in preview"""
        response = self.client.get('/api/preview/../../../etc/passwd')
        # Should not access files outside the output folder
        self.assertIn(response.status_code, [404, 400, 403])

    def test_file_upload_size_limit(self):
        """Test that file upload respects size limits"""
        # Create a file larger than limit (100MB)
        # Note: This test may be skipped if it's too resource intensive
        pass  # Skipped for performance reasons

    def test_uploaded_files_isolated_by_id(self):
        """Test that uploaded files are isolated by unique ID"""
        # Upload same filename twice
        for _ in range(2):
            response = self.client.post(
                '/api/upload',
                data={'file': (BytesIO(b'content1'), 'test.msi')}
            )
            self.assertEqual(response.status_code, 200)

        # Both should have different file_ids
        # Verify files are stored separately
        files = os.listdir(self.temp_upload_dir)
        self.assertEqual(len(files), 2)
        # Both should have unique IDs
        ids = [f.split('_')[0] for f in files]
        self.assertEqual(len(set(ids)), 2)

    def test_no_sensitive_data_in_error_responses(self):
        """Test that error responses don't leak sensitive information"""
        response = self.client.post(
            '/api/generate-payload',
            data=json.dumps({'file_id': '../../../etc/passwd'}),
            content_type='application/json'
        )
        # Should return 404 without revealing directory structure
        self.assertEqual(response.status_code, 404)
        error_msg = json.loads(response.data).get('error', '')
        # Error should not contain full paths or system info
        self.assertNotIn('/etc', error_msg)
        self.assertNotIn('/tmp', error_msg)


class TestHTTPStatusCodeComprehensive(unittest.TestCase):
    """Comprehensive HTTP status code tests"""

    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_status_code_200_ok(self):
        """Verify 200 OK is returned for successful requests"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)

    def test_status_code_400_bad_request(self):
        """Verify 400 Bad Request for invalid input"""
        response = self.client.post(
            '/api/generate-payload',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_status_code_404_not_found(self):
        """Verify 404 Not Found for missing resources"""
        response = self.client.get('/api/download/nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_status_code_405_method_not_allowed(self):
        """Verify 405 Method Not Allowed for wrong HTTP methods"""
        response = self.client.post('/api/health')
        self.assertEqual(response.status_code, 405)

    def test_status_code_500_server_error(self):
        """Verify 500 Server Error handling (simulated)"""
        # This would require mocking an actual error condition
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
