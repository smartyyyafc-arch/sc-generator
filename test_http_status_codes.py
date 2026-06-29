#!/usr/bin/env python3
"""
HTTP Status Code Verification Test Suite

Comprehensive testing of all API endpoints to verify:
- Correct status codes for successful requests
- Correct status codes for error conditions
- Correct status codes for invalid methods (405)
- Correct status codes for missing resources (404)
- Correct status codes for invalid input (400, 422)
- Correct status codes for server errors (500)
- Correct status codes for timeouts (408)

Follows HTTP standards:
- 2xx: Success (200, 201, 204)
- 3xx: Redirection (301, 302, 304)
- 4xx: Client Error (400, 401, 403, 404, 405, 408, 422)
- 5xx: Server Error (500, 502, 503)
"""

import unittest
import json
import os
import tempfile
import io
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys

# Add the project root to path
sys.path.insert(0, '/home/user/sc-generator')

from app import app


class TestHTTPStatusCodes(unittest.TestCase):
    """Test HTTP status codes for all API endpoints"""

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
    # 2xx SUCCESS STATUS CODES
    # ============================================================================

    def test_health_endpoint_returns_200(self):
        """GET /api/health should return 200 OK"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200, "Health check should return 200 OK")
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')

    def test_techniques_endpoint_returns_200(self):
        """GET /api/techniques should return 200 OK"""
        response = self.client.get('/api/techniques')
        self.assertEqual(response.status_code, 200, "Techniques endpoint should return 200 OK")

    def test_fingerprints_get_returns_200(self):
        """GET /api/fingerprints should return 200 OK"""
        response = self.client.get('/api/fingerprints')
        self.assertEqual(response.status_code, 200, "Get fingerprints should return 200 OK")

    def test_proxies_get_returns_200(self):
        """GET /api/proxies should return 200 OK"""
        response = self.client.get('/api/proxies')
        self.assertEqual(response.status_code, 200, "Get proxies should return 200 OK")

    def test_settings_get_returns_200(self):
        """GET /api/settings should return 200 OK"""
        response = self.client.get('/api/settings')
        self.assertEqual(response.status_code, 200, "Get settings should return 200 OK")

    def test_one_click_styles_returns_200(self):
        """GET /api/one-click-styles should return 200 OK"""
        response = self.client.get('/api/one-click-styles')
        self.assertEqual(response.status_code, 200, "One-click styles should return 200 OK")

    def test_recommendations_returns_200(self):
        """GET /api/recommendations should return 200 OK"""
        response = self.client.get('/api/recommendations')
        self.assertEqual(response.status_code, 200, "Recommendations should return 200 OK")

    def test_persistence_methods_returns_200(self):
        """GET /api/persistence-methods should return 200 OK"""
        response = self.client.get('/api/persistence-methods')
        self.assertEqual(response.status_code, 200, "Persistence methods should return 200 OK")

    def test_proxy_info_returns_200(self):
        """GET /api/proxy-info should return 200 OK"""
        response = self.client.get('/api/proxy-info')
        self.assertEqual(response.status_code, 200, "Proxy info should return 200 OK")

    def test_cleanup_stats_returns_200(self):
        """GET /api/cleanup/stats should return 200 OK"""
        response = self.client.get('/api/cleanup/stats')
        self.assertEqual(response.status_code, 200, "Cleanup stats should return 200 OK")

    # ============================================================================
    # 400 BAD REQUEST STATUS CODES
    # ============================================================================

    def test_upload_missing_file_returns_400(self):
        """POST /api/upload without file should return 400 Bad Request"""
        response = self.client.post('/api/upload', data={})
        self.assertEqual(response.status_code, 400, "Upload without file should return 400 Bad Request")
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_upload_empty_filename_returns_400(self):
        """POST /api/upload with empty filename should return 400 Bad Request"""
        response = self.client.post('/api/upload', data={
            'file': (io.BytesIO(b'test'), '')
        })
        self.assertEqual(response.status_code, 400, "Upload with empty filename should return 400 Bad Request")

    def test_upload_unsupported_file_type_returns_400(self):
        """POST /api/upload with unsupported file type should return 400 Bad Request"""
        response = self.client.post('/api/upload', data={
            'file': (io.BytesIO(b'test'), 'test.txt')
        })
        self.assertEqual(response.status_code, 400, "Upload with unsupported type should return 400 Bad Request")
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_upload_empty_file_returns_400(self):
        """POST /api/upload with empty file should return 400 Bad Request"""
        response = self.client.post('/api/upload', data={
            'file': (io.BytesIO(b''), 'test.msi')
        })
        self.assertEqual(response.status_code, 400, "Upload with empty file should return 400 Bad Request")

    def test_generate_payload_missing_technique_returns_400(self):
        """POST /api/generate-payload without technique should return 400 Bad Request"""
        response = self.client.post('/api/generate-payload',
            json={'command': 'whoami'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400, "Generate payload without technique should return 400")
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_generate_payload_missing_command_returns_400(self):
        """POST /api/generate-payload without command should return 400 Bad Request"""
        response = self.client.post('/api/generate-payload',
            json={'technique': 'base64'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400, "Generate payload without command should return 400")
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_generate_payload_invalid_technique_returns_400(self):
        """POST /api/generate-payload with invalid technique should return 400 Bad Request"""
        response = self.client.post('/api/generate-payload',
            json={'technique': 'invalid_technique', 'command': 'whoami'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400, "Generate payload with invalid technique should return 400")

    def test_add_proxy_missing_host_returns_400(self):
        """POST /api/proxies without host should return 400 Bad Request"""
        response = self.client.post('/api/proxies',
            json={'port': 8080},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400, "Add proxy without host should return 400")

    def test_add_proxy_invalid_port_returns_400(self):
        """POST /api/proxies with invalid port should return 400 Bad Request"""
        response = self.client.post('/api/proxies',
            json={'host': 'proxy.example.com', 'port': 'not_a_number'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400, "Add proxy with invalid port should return 400")

    def test_batch_generate_missing_payloads_returns_400(self):
        """POST /api/batch-generate without payloads should return 400 Bad Request"""
        response = self.client.post('/api/batch-generate',
            json={},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400, "Batch generate without payloads should return 400")

    def test_generate_one_click_missing_command_returns_400(self):
        """POST /api/generate-one-click without command should return 400 Bad Request"""
        response = self.client.post('/api/generate-one-click',
            json={'style': 'default'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400, "Generate one-click without command should return 400")

    def test_generate_persistent_missing_command_returns_400(self):
        """POST /api/generate-persistent without command should return 400 Bad Request"""
        response = self.client.post('/api/generate-persistent',
            json={'method': 'registry'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400, "Generate persistent without command should return 400")

    # ============================================================================
    # 404 NOT FOUND STATUS CODES
    # ============================================================================

    def test_nonexistent_endpoint_returns_404(self):
        """GET /api/nonexistent should return 404 Not Found"""
        response = self.client.get('/api/nonexistent')
        self.assertEqual(response.status_code, 404, "Nonexistent endpoint should return 404 Not Found")

    def test_download_nonexistent_file_returns_404(self):
        """GET /api/download/nonexistent-id should return 404 Not Found"""
        response = self.client.get('/api/download/nonexistent-id-12345')
        self.assertEqual(response.status_code, 404, "Download nonexistent file should return 404")

    def test_preview_nonexistent_file_returns_404(self):
        """GET /api/preview/nonexistent-id should return 404 Not Found"""
        response = self.client.get('/api/preview/nonexistent-id-12345')
        self.assertEqual(response.status_code, 404, "Preview nonexistent file should return 404")

    def test_test_proxy_nonexistent_returns_404(self):
        """POST /api/proxies/nonexistent/test should return 404 Not Found"""
        response = self.client.post('/api/proxies/nonexistent-proxy-id/test')
        self.assertEqual(response.status_code, 404, "Test nonexistent proxy should return 404")

    # ============================================================================
    # 405 METHOD NOT ALLOWED STATUS CODES
    # ============================================================================

    def test_health_post_returns_405(self):
        """POST /api/health should return 405 Method Not Allowed"""
        response = self.client.post('/api/health')
        self.assertEqual(response.status_code, 405, "POST to health should return 405 Method Not Allowed")

    def test_health_put_returns_405(self):
        """PUT /api/health should return 405 Method Not Allowed"""
        response = self.client.put('/api/health')
        self.assertEqual(response.status_code, 405, "PUT to health should return 405 Method Not Allowed")

    def test_health_delete_returns_405(self):
        """DELETE /api/health should return 405 Method Not Allowed"""
        response = self.client.delete('/api/health')
        self.assertEqual(response.status_code, 405, "DELETE to health should return 405 Method Not Allowed")

    def test_techniques_post_returns_405(self):
        """POST /api/techniques should return 405 Method Not Allowed"""
        response = self.client.post('/api/techniques')
        self.assertEqual(response.status_code, 405, "POST to techniques should return 405")

    def test_techniques_put_returns_405(self):
        """PUT /api/techniques should return 405 Method Not Allowed"""
        response = self.client.put('/api/techniques')
        self.assertEqual(response.status_code, 405, "PUT to techniques should return 405")

    def test_techniques_delete_returns_405(self):
        """DELETE /api/techniques should return 405 Method Not Allowed"""
        response = self.client.delete('/api/techniques')
        self.assertEqual(response.status_code, 405, "DELETE to techniques should return 405")

    def test_fingerprints_put_returns_405(self):
        """PUT /api/fingerprints should return 405 Method Not Allowed"""
        response = self.client.put('/api/fingerprints')
        self.assertEqual(response.status_code, 405, "PUT to fingerprints should return 405")

    def test_fingerprints_delete_returns_405(self):
        """DELETE /api/fingerprints should return 405 Method Not Allowed"""
        response = self.client.delete('/api/fingerprints')
        self.assertEqual(response.status_code, 405, "DELETE to fingerprints should return 405")

    def test_proxies_get_put_returns_405(self):
        """PUT /api/proxies should return 405 Method Not Allowed"""
        response = self.client.put('/api/proxies')
        self.assertEqual(response.status_code, 405, "PUT to proxies should return 405")

    def test_proxies_get_delete_returns_405(self):
        """DELETE /api/proxies should return 405 Method Not Allowed"""
        response = self.client.delete('/api/proxies')
        self.assertEqual(response.status_code, 405, "DELETE to proxies should return 405")

    def test_settings_post_returns_405(self):
        """POST /api/settings should return 405 Method Not Allowed"""
        response = self.client.post('/api/settings')
        self.assertEqual(response.status_code, 405, "POST to settings should return 405")

    def test_settings_put_returns_405(self):
        """PUT /api/settings should return 405 Method Not Allowed"""
        response = self.client.put('/api/settings')
        self.assertEqual(response.status_code, 405, "PUT to settings should return 405")

    def test_settings_delete_returns_405(self):
        """DELETE /api/settings should return 405 Method Not Allowed"""
        response = self.client.delete('/api/settings')
        self.assertEqual(response.status_code, 405, "DELETE to settings should return 405")

    def test_one_click_styles_post_returns_405(self):
        """POST /api/one-click-styles should return 405 Method Not Allowed"""
        response = self.client.post('/api/one-click-styles')
        self.assertEqual(response.status_code, 405, "POST to one-click-styles should return 405")

    def test_recommendations_post_returns_405(self):
        """POST /api/recommendations should return 405 Method Not Allowed"""
        response = self.client.post('/api/recommendations')
        self.assertEqual(response.status_code, 405, "POST to recommendations should return 405")

    def test_persistence_methods_post_returns_405(self):
        """POST /api/persistence-methods should return 405 Method Not Allowed"""
        response = self.client.post('/api/persistence-methods')
        self.assertEqual(response.status_code, 405, "POST to persistence-methods should return 405")

    def test_proxy_info_post_returns_405(self):
        """POST /api/proxy-info should return 405 Method Not Allowed"""
        response = self.client.post('/api/proxy-info')
        self.assertEqual(response.status_code, 405, "POST to proxy-info should return 405")

    def test_cleanup_stats_post_returns_405(self):
        """POST /api/cleanup/stats should return 405 Method Not Allowed"""
        response = self.client.post('/api/cleanup/stats')
        self.assertEqual(response.status_code, 405, "POST to cleanup/stats should return 405")

    def test_download_put_returns_405(self):
        """PUT /api/download/<id> should return 405 Method Not Allowed"""
        response = self.client.put('/api/download/test-id')
        self.assertEqual(response.status_code, 405, "PUT to download should return 405")

    def test_download_post_returns_405(self):
        """POST /api/download/<id> should return 405 Method Not Allowed"""
        response = self.client.post('/api/download/test-id')
        self.assertEqual(response.status_code, 405, "POST to download should return 405")

    def test_preview_put_returns_405(self):
        """PUT /api/preview/<id> should return 405 Method Not Allowed"""
        response = self.client.put('/api/preview/test-id')
        self.assertEqual(response.status_code, 405, "PUT to preview should return 405")

    def test_preview_post_returns_405(self):
        """POST /api/preview/<id> should return 405 Method Not Allowed"""
        response = self.client.post('/api/preview/test-id')
        self.assertEqual(response.status_code, 405, "POST to preview should return 405")

    # ============================================================================
    # 200/201 SUCCESS WITH PROPER RESPONSE CONTENT
    # ============================================================================

    def test_upload_file_success_returns_200_with_file_id(self):
        """POST /api/upload with valid file should return 200 OK with file_id"""
        response = self.client.post('/api/upload', data={
            'file': (io.BytesIO(b'test content'), 'test.msi')
        })
        self.assertEqual(response.status_code, 200, "Valid upload should return 200 OK")
        data = json.loads(response.data)
        self.assertIn('file_id', data)
        self.assertIn('filename', data)
        self.assertEqual(data['filename'], 'test.msi')

    def test_add_proxy_success_returns_200(self):
        """POST /api/proxies with valid proxy should return 200 OK"""
        response = self.client.post('/api/proxies',
            json={
                'host': 'proxy.example.com',
                'port': 8080,
                'protocol': 'http'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200, "Valid proxy add should return 200 OK")
        data = json.loads(response.data)
        self.assertIn('proxy_id', data)

    def test_create_fingerprint_success_returns_200(self):
        """POST /api/fingerprints with valid data should return 200 OK"""
        response = self.client.post('/api/fingerprints',
            json={
                'name': 'TestFingerprint',
                'properties': {'property1': 'value1'}
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200, "Valid fingerprint creation should return 200 OK")

    # ============================================================================
    # 408 REQUEST TIMEOUT STATUS CODES
    # ============================================================================

    @patch('app.check_request_timeout')
    def test_upload_timeout_returns_408(self, mock_timeout):
        """POST /api/upload that times out should return 408 Request Timeout"""
        mock_timeout.return_value = True
        response = self.client.post('/api/upload', data={
            'file': (io.BytesIO(b'test'), 'test.msi')
        })
        self.assertEqual(response.status_code, 408, "Timed out upload should return 408")
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch('app.check_request_timeout')
    def test_generate_payload_timeout_returns_408(self, mock_timeout):
        """POST /api/generate-payload that times out should return 408 Request Timeout"""
        mock_timeout.return_value = True
        response = self.client.post('/api/generate-payload',
            json={'technique': 'base64', 'command': 'whoami'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 408, "Timed out generate should return 408")
        data = json.loads(response.data)
        self.assertIn('error', data)

    # ============================================================================
    # 500 INTERNAL SERVER ERROR STATUS CODES
    # ============================================================================

    @patch('app.PayloadGenerator')
    def test_generate_payload_server_error_returns_500(self, mock_payload_gen):
        """POST /api/generate-payload with server error should return 500 Internal Server Error"""
        mock_payload_gen.side_effect = Exception("Server error")
        response = self.client.post('/api/generate-payload',
            json={'technique': 'base64', 'command': 'whoami'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500, "Server error should return 500")

    # ============================================================================
    # CONSISTENCY: VERIFY ALL GET ENDPOINTS RETURN JSON
    # ============================================================================

    def test_all_get_endpoints_return_json_content_type(self):
        """All GET endpoints should return Content-Type: application/json"""
        get_endpoints = [
            '/api/health',
            '/api/techniques',
            '/api/fingerprints',
            '/api/proxies',
            '/api/settings',
            '/api/one-click-styles',
            '/api/recommendations',
            '/api/persistence-methods',
            '/api/proxy-info',
            '/api/cleanup/stats'
        ]

        for endpoint in get_endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                # Check if JSON can be parsed
                try:
                    json.loads(response.data)
                except json.JSONDecodeError:
                    self.fail(f"{endpoint} should return valid JSON")

    # ============================================================================
    # CONSISTENCY: VERIFY ERROR RESPONSES HAVE MESSAGE
    # ============================================================================

    def test_error_responses_contain_error_field(self):
        """All error responses should contain 'error' field"""
        error_test_cases = [
            ('POST', '/api/upload', {}, 400),  # Missing file
            ('POST', '/api/proxies', {'port': 8080}, 400),  # Missing host
            ('POST', '/api/generate-payload', {'technique': 'base64'}, 400),  # Missing command
        ]

        for method, endpoint, data, expected_status in error_test_cases:
            with self.subTest(method=method, endpoint=endpoint):
                if method == 'POST':
                    response = self.client.post(endpoint,
                        json=data,
                        content_type='application/json'
                    )
                else:
                    response = self.client.get(endpoint)

                if response.status_code >= 400:
                    data = json.loads(response.data)
                    self.assertIn('error', data,
                        f"{endpoint} error response should contain 'error' field")

    # ============================================================================
    # REDIRECT TESTS (3xx)
    # ============================================================================

    def test_trailing_slash_redirect(self):
        """Test handling of endpoints with trailing slash"""
        # Note: Flask typically handles this, but verify behavior
        response = self.client.get('/api/health/')
        # Should either return 200 or 308 (permanent redirect)
        self.assertIn(response.status_code, [200, 308, 404])

    # ============================================================================
    # CONTENT-LENGTH HEADERS
    # ============================================================================

    def test_response_has_content_length_for_json(self):
        """Successful responses should have Content-Length header"""
        response = self.client.get('/api/health')
        # Either Content-Length or Transfer-Encoding should be present
        self.assertTrue(
            'Content-Length' in response.headers or 'Transfer-Encoding' in response.headers,
            "Response should have Content-Length or Transfer-Encoding header"
        )

    # ============================================================================
    # STATUS CODE CONSISTENCY FOR UPLOAD FILE TYPES
    # ============================================================================

    def test_upload_various_invalid_extensions_returns_400(self):
        """Upload with various invalid extensions should return 400"""
        invalid_extensions = ['.txt', '.pdf', '.jpg', '.png', '.zip', '.py', '.js', '.html']

        for ext in invalid_extensions:
            with self.subTest(extension=ext):
                response = self.client.post('/api/upload', data={
                    'file': (io.BytesIO(b'test'), f'test{ext}')
                })
                self.assertEqual(response.status_code, 400,
                    f"Upload with {ext} should return 400 Bad Request")

    def test_upload_valid_extensions_returns_200(self):
        """Upload with valid extensions should return 200"""
        valid_extensions = ['.msi', '.exe', '.dll', '.bat', '.cmd', '.vbs']

        for ext in valid_extensions:
            with self.subTest(extension=ext):
                response = self.client.post('/api/upload', data={
                    'file': (io.BytesIO(b'test content'), f'test{ext}')
                })
                self.assertEqual(response.status_code, 200,
                    f"Upload with {ext} should return 200 OK")

    # ============================================================================
    # VERIFY CLEANUP ENDPOINT STATUS CODES
    # ============================================================================

    def test_cleanup_trigger_returns_200(self):
        """POST /api/cleanup/trigger should return 200 OK"""
        response = self.client.post('/api/cleanup/trigger')
        self.assertEqual(response.status_code, 200, "Cleanup trigger should return 200 OK")

    def test_cleanup_trigger_returns_json(self):
        """POST /api/cleanup/trigger should return JSON response"""
        response = self.client.post('/api/cleanup/trigger')
        try:
            data = json.loads(response.data)
            self.assertIn('status', data)
        except json.JSONDecodeError:
            self.fail("Cleanup trigger should return valid JSON")


class TestHTTPStatusCodesSummary(unittest.TestCase):
    """Summary test case documenting all expected status codes"""

    def test_status_code_documentation(self):
        """Document all expected HTTP status codes by endpoint"""
        expected_codes = {
            'GET /api/health': [200, 405],  # 200 OK, 405 for non-GET methods
            'GET /api/techniques': [200, 405],
            'GET /api/fingerprints': [200, 405],
            'POST /api/fingerprints': [200, 400, 405],
            'POST /api/proxies/<id>/test': [200, 404, 405],
            'GET /api/proxies': [200, 405],
            'POST /api/proxies': [200, 400, 405],
            'POST /api/upload': [200, 400, 408, 405, 500],
            'POST /api/generate-payload': [200, 400, 408, 405, 500],
            'GET /api/download/<id>': [200, 404, 405],
            'GET /api/preview/<id>': [200, 404, 405],
            'GET /api/settings': [200, 405],
            'POST /api/batch-generate': [200, 400, 408, 405],
            'POST /api/generate-one-click': [200, 400, 408, 405],
            'GET /api/one-click-styles': [200, 405],
            'GET /api/recommendations': [200, 405],
            'GET /api/persistence-methods': [200, 405],
            'POST /api/generate-persistent': [200, 400, 408, 405],
            'GET /api/proxy-info': [200, 405],
            'GET /api/cleanup/stats': [200, 405],
            'POST /api/cleanup/trigger': [200, 405],
            'ANY /api/nonexistent': [404],
        }

        # This test documents the expected status codes
        # It serves as reference documentation
        self.assertTrue(True)  # Documentation test always passes
        print("\n" + "=" * 80)
        print("HTTP STATUS CODE REFERENCE BY ENDPOINT")
        print("=" * 80)
        for endpoint, codes in sorted(expected_codes.items()):
            print(f"{endpoint}: {codes}")
        print("=" * 80)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
