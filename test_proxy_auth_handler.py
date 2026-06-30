"""
Proxy Authentication Handler - Unit Tests

Comprehensive test suite for all authentication methods.
"""

import unittest
import base64
import json
from unittest.mock import patch, MagicMock
from proxy_auth_handler import (
    ProxyAuthHandler,
    ProxyConfig,
    AuthType,
    BasicAuth,
    DigestAuth,
    NTLMAuth,
    CertificateAuth,
    create_auth_handler,
)


class TestProxyConfig(unittest.TestCase):
    """Test ProxyConfig dataclass."""

    def test_basic_config_valid(self):
        """Test valid basic auth configuration."""
        config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type=AuthType.BASIC,
            username="user",
            password="pass"
        )
        self.assertEqual(config.auth_type, AuthType.BASIC)
        self.assertEqual(config.username, "user")

    def test_basic_config_missing_password(self):
        """Test basic auth missing password raises error."""
        with self.assertRaises(ValueError):
            ProxyConfig(
                proxy_url="http://proxy.example.com:8080",
                auth_type=AuthType.BASIC,
                username="user"
            )

    def test_digest_config_missing_credentials(self):
        """Test digest auth missing credentials raises error."""
        with self.assertRaises(ValueError):
            ProxyConfig(
                proxy_url="http://proxy.example.com:8080",
                auth_type=AuthType.DIGEST,
                username="user"
            )

    def test_certificate_config_missing_files(self):
        """Test certificate auth missing files raises error."""
        with self.assertRaises(FileNotFoundError):
            ProxyConfig(
                proxy_url="https://proxy.example.com:8443",
                auth_type=AuthType.CERTIFICATE,
                cert_path="/nonexistent/cert.pem",
                key_path="/nonexistent/key.pem"
            )

    def test_auth_type_string_conversion(self):
        """Test auth type string is converted to enum."""
        config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type="basic",
            username="user",
            password="pass"
        )
        self.assertEqual(config.auth_type, AuthType.BASIC)


class TestBasicAuth(unittest.TestCase):
    """Test Basic authentication."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type=AuthType.BASIC,
            username="testuser",
            password="testpass"
        )
        self.auth = BasicAuth(self.config)

    def test_auth_header_format(self):
        """Test Basic auth header format."""
        headers = self.auth.get_auth_header()
        self.assertIn("Proxy-Authorization", headers)
        self.assertTrue(headers["Proxy-Authorization"].startswith("Basic "))

    def test_auth_header_encoding(self):
        """Test Basic auth header encoding."""
        headers = self.auth.get_auth_header()
        auth_header = headers["Proxy-Authorization"]
        encoded = auth_header.split(" ")[1]

        # Decode and verify
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, "testuser:testpass")

    def test_special_characters_in_password(self):
        """Test password with special characters."""
        config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type=AuthType.BASIC,
            username="user",
            password="p@ssw0rd!#$%"
        )
        auth = BasicAuth(config)
        headers = auth.get_auth_header()

        encoded = headers["Proxy-Authorization"].split(" ")[1]
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(decoded, "user:p@ssw0rd!#$%")

    def test_handle_challenge_returns_same_header(self):
        """Test challenge handling returns same header."""
        headers1 = self.auth.get_auth_header()
        headers2 = self.auth.handle_auth_challenge("Basic realm=\"Proxy\"")
        self.assertEqual(headers1, headers2)


class TestDigestAuth(unittest.TestCase):
    """Test Digest authentication."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type=AuthType.DIGEST,
            username="digestuser",
            password="digestpass"
        )
        self.auth = DigestAuth(self.config)

    def test_parse_challenge(self):
        """Test parsing digest challenge."""
        challenge = (
            'Digest realm="Test Realm", '
            'nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093", '
            'qop="auth", '
            'opaque="5ccc069c403ebaf9f0171986f2c632e5", '
            'algorithm=MD5'
        )
        self.auth._parse_challenge(challenge)

        self.assertEqual(self.auth.realm, "Test Realm")
        self.assertEqual(self.auth.nonce, "dcd98b7102dd2f0e8b11d0f600bfb0c093")
        self.assertEqual(self.auth.qop, "auth")
        self.assertEqual(self.auth.algorithm, "MD5")

    def test_handle_challenge_creates_response(self):
        """Test handling digest challenge creates response."""
        challenge = (
            'Digest realm="Test Realm", '
            'nonce="test_nonce_123", '
            'qop="auth"'
        )
        headers = self.auth.handle_auth_challenge(challenge)

        self.assertIn("Proxy-Authorization", headers)
        self.assertTrue(headers["Proxy-Authorization"].startswith("Digest "))
        self.assertIn("response=", headers["Proxy-Authorization"])

    def test_sha256_algorithm(self):
        """Test SHA-256 algorithm support."""
        challenge = (
            'Digest realm="Test", '
            'nonce="test_nonce", '
            'algorithm=SHA-256'
        )
        self.auth._parse_challenge(challenge)
        self.assertEqual(self.auth.algorithm, "SHA-256")

        headers = self.auth.handle_auth_challenge(challenge)
        self.assertIn("algorithm=SHA-256", headers["Proxy-Authorization"])

    def test_nonce_count_increments(self):
        """Test nonce count increments with each challenge."""
        challenge = 'Digest realm="Test", nonce="test", qop="auth"'

        headers1 = self.auth.handle_auth_challenge(challenge)
        headers2 = self.auth.handle_auth_challenge(challenge)

        # Extract nc values
        nc1 = self._extract_nc(headers1["Proxy-Authorization"])
        nc2 = self._extract_nc(headers2["Proxy-Authorization"])

        self.assertNotEqual(nc1, nc2)

    @staticmethod
    def _extract_nc(auth_header):
        """Extract nc value from Digest header."""
        import re
        match = re.search(r'nc=(\w+)', auth_header)
        return match.group(1) if match else None


class TestNTLMAuth(unittest.TestCase):
    """Test NTLM authentication."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type=AuthType.NTLM,
            username="testuser",
            password="testpass",
            domain="TESTDOMAIN",
            workstation="TESTWS"
        )
        self.auth = NTLMAuth(self.config)

    def test_type1_message_structure(self):
        """Test Type 1 message structure."""
        msg = self.auth._create_type1_message()

        # Check signature
        self.assertTrue(msg.startswith(b"NTLMSSP\x00"))

        # Check message type (should be 1)
        import struct
        msg_type = struct.unpack("<I", msg[8:12])[0]
        self.assertEqual(msg_type, 1)

    def test_type1_message_encoding(self):
        """Test Type 1 message is base64 encoded."""
        headers = self.auth.get_auth_header()
        auth_header = headers["Proxy-Authorization"]

        self.assertTrue(auth_header.startswith("NTLM "))
        encoded = auth_header.split(" ")[1]

        # Should be valid base64
        decoded = base64.b64decode(encoded)
        self.assertTrue(decoded.startswith(b"NTLMSSP\x00"))

    def test_type3_message_includes_credentials(self):
        """Test Type 3 message generation."""
        self.auth.server_challenge = b"\x00" * 8
        msg = self.auth._create_type3_message("testuser", "testpass")

        # Check signature and type
        self.assertTrue(msg.startswith(b"NTLMSSP\x00"))
        import struct
        msg_type = struct.unpack("<I", msg[8:12])[0]
        self.assertEqual(msg_type, 3)

    def test_handle_challenge_response(self):
        """Test handling Type 2 challenge."""
        # Create mock Type 2 message
        type2_msg = b"NTLMSSP\x00" + b"\x02\x00\x00\x00" + b"\x00" * 40
        type2_b64 = base64.b64encode(type2_msg).decode()
        challenge = f"NTLM {type2_b64}"

        headers = self.auth.handle_auth_challenge(challenge)
        self.assertIn("Proxy-Authorization", headers)
        self.assertTrue(headers["Proxy-Authorization"].startswith("NTLM "))


class TestCertificateAuth(unittest.TestCase):
    """Test Certificate-based authentication."""

    @patch('os.path.exists')
    def setUp(self, mock_exists):
        """Set up test fixtures."""
        mock_exists.return_value = True

        self.config = ProxyConfig(
            proxy_url="https://secure-proxy.example.com:8443",
            auth_type=AuthType.CERTIFICATE,
            cert_path="/path/to/cert.pem",
            key_path="/path/to/key.pem",
            ca_bundle="/path/to/ca.pem"
        )
        self.auth = CertificateAuth(self.config)

    def test_get_auth_header_returns_paths(self):
        """Test get_auth_header returns certificate paths."""
        headers = self.auth.get_auth_header()

        self.assertEqual(headers["client_cert"], "/path/to/cert.pem")
        self.assertEqual(headers["client_key"], "/path/to/key.pem")
        self.assertEqual(headers["ca_bundle"], "/path/to/ca.pem")
        self.assertTrue(headers["verify_ssl"])

    def test_handle_challenge_returns_same_config(self):
        """Test challenge handling returns same configuration."""
        headers1 = self.auth.get_auth_header()
        headers2 = self.auth.handle_auth_challenge("some challenge")
        self.assertEqual(headers1, headers2)


class TestProxyAuthHandler(unittest.TestCase):
    """Test main ProxyAuthHandler class."""

    def test_create_handler_basic_auth(self):
        """Test creating handler with basic auth."""
        config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type=AuthType.BASIC,
            username="user",
            password="pass"
        )
        handler = ProxyAuthHandler(config)

        self.assertIsNotNone(handler.auth_scheme)
        self.assertIsInstance(handler.auth_scheme, BasicAuth)

    def test_create_handler_digest_auth(self):
        """Test creating handler with digest auth."""
        config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type=AuthType.DIGEST,
            username="user",
            password="pass"
        )
        handler = ProxyAuthHandler(config)

        self.assertIsInstance(handler.auth_scheme, DigestAuth)

    def test_create_handler_ntlm_auth(self):
        """Test creating handler with NTLM auth."""
        config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type=AuthType.NTLM,
            username="user",
            password="pass"
        )
        handler = ProxyAuthHandler(config)

        self.assertIsInstance(handler.auth_scheme, NTLMAuth)

    def test_get_proxy_url_removes_credentials(self):
        """Test get_proxy_url removes credentials if present."""
        config = ProxyConfig(
            proxy_url="http://user:pass@proxy.example.com:8080",
            auth_type=AuthType.BASIC,
            username="testuser",
            password="testpass"
        )
        handler = ProxyAuthHandler(config)
        url = handler.get_proxy_url()

        self.assertNotIn("user:pass@", url)
        self.assertIn("proxy.example.com", url)

    def test_get_connection_config(self):
        """Test getting connection configuration."""
        config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type=AuthType.BASIC,
            username="user",
            password="pass",
            timeout=45
        )
        handler = ProxyAuthHandler(config)
        conn_config = handler.get_connection_config()

        self.assertEqual(conn_config["auth_type"], "basic")
        self.assertEqual(conn_config["timeout"], 45)
        self.assertIn("proxy_url", conn_config)

    def test_to_json_excludes_credentials(self):
        """Test JSON export excludes sensitive credentials."""
        config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type=AuthType.BASIC,
            username="user",
            password="secret_password"
        )
        handler = ProxyAuthHandler(config)
        json_str = handler.to_json()
        json_obj = json.loads(json_str)

        self.assertNotIn("password", json_obj)
        self.assertNotIn("username", json_obj)
        self.assertIn("proxy_url", json_obj)

    def test_custom_headers_included(self):
        """Test custom headers are included in auth headers."""
        custom_headers = {
            "X-Custom-Header": "custom_value",
            "User-Agent": "CustomAgent/1.0"
        }
        config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type=AuthType.BASIC,
            username="user",
            password="pass",
            custom_headers=custom_headers
        )
        handler = ProxyAuthHandler(config)
        headers = handler.get_auth_headers()

        self.assertIn("X-Custom-Header", headers)
        self.assertEqual(headers["X-Custom-Header"], "custom_value")


class TestConvenienceFunction(unittest.TestCase):
    """Test create_auth_handler convenience function."""

    def test_create_handler_basic(self):
        """Test creating handler with convenience function."""
        handler = create_auth_handler(
            proxy_url="http://proxy.example.com:8080",
            auth_type="basic",
            username="user",
            password="pass"
        )

        self.assertIsInstance(handler, ProxyAuthHandler)
        self.assertEqual(handler.config.auth_type, AuthType.BASIC)

    def test_create_handler_with_kwargs(self):
        """Test convenience function with additional kwargs."""
        handler = create_auth_handler(
            proxy_url="http://proxy.example.com:8080",
            auth_type="ntlm",
            username="user",
            password="pass",
            domain="TESTDOMAIN",
            timeout=60
        )

        self.assertEqual(handler.config.domain, "TESTDOMAIN")
        self.assertEqual(handler.config.timeout, 60)

    def test_create_handler_invalid_auth_type(self):
        """Test convenience function with invalid auth type."""
        with self.assertRaises(ValueError):
            create_auth_handler(
                proxy_url="http://proxy.example.com:8080",
                auth_type="invalid_type",
                username="user",
                password="pass"
            )


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    def test_basic_auth_workflow(self):
        """Test complete basic auth workflow."""
        handler = create_auth_handler(
            proxy_url="http://proxy.example.com:8080",
            auth_type="basic",
            username="integtest",
            password="integpass"
        )

        # Get initial headers
        headers = handler.get_auth_headers()
        self.assertIn("Proxy-Authorization", headers)

        # Verify header structure
        auth_header = headers["Proxy-Authorization"]
        self.assertTrue(auth_header.startswith("Basic "))

    def test_proxy_url_normalization(self):
        """Test proxy URL normalization."""
        test_cases = [
            ("http://proxy.example.com", "http://proxy.example.com"),
            ("http://proxy.example.com:8080", "http://proxy.example.com:8080"),
            ("https://proxy.example.com:8443", "https://proxy.example.com:8443"),
        ]

        for input_url, expected_output in test_cases:
            handler = create_auth_handler(
                proxy_url=input_url,
                auth_type="basic",
                username="user",
                password="pass"
            )
            self.assertEqual(handler.get_proxy_url(), expected_output)

    def test_timeout_configuration(self):
        """Test timeout configuration."""
        handler = create_auth_handler(
            proxy_url="http://proxy.example.com:8080",
            auth_type="basic",
            username="user",
            password="pass",
            timeout=120
        )

        config = handler.get_connection_config()
        self.assertEqual(config["timeout"], 120)


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
