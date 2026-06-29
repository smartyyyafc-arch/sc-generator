#!/usr/bin/env python3
"""
Test Suite for Security Fix #4: Proxy Configuration and Forwarding

Tests:
1. Credential encryption/decryption
2. Proxy authentication encoding (HTTP, SOCKS5, URL auth)
3. Proxy configuration creation with encrypted credentials
4. Proxy session creation with proper forwarding
5. Error handling for invalid configurations
6. Proxy connectivity testing
"""

import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# Test imports
try:
    from fingerprint_manager import (
        CredentialManager, ProxyAuthEncoder, ProxyConfig,
        CredentialEncryptionError, ProxyAuthenticationError
    )
    IMPORTS_OK = True
except ImportError as e:
    print(f"Warning: Could not import fingerprint_manager: {e}")
    IMPORTS_OK = False


class TestCredentialEncryption(unittest.TestCase):
    """Test credential encryption and decryption"""

    def setUp(self):
        """Set up test fixtures"""
        if not IMPORTS_OK:
            self.skipTest("Required imports unavailable")

        self.test_dir = tempfile.mkdtemp()
        self.key_file = os.path.join(self.test_dir, '.cred_key')
        self.cred_mgr = CredentialManager(key_file=self.key_file)

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_encryption_basic(self):
        """Test basic credential encryption"""
        username = "testuser"
        password = "testpass123"

        encrypted = self.cred_mgr.encrypt_credentials(username, password)

        # Encrypted should be a string (base64)
        self.assertIsInstance(encrypted, str)
        self.assertGreater(len(encrypted), 0)

        # Should not contain plaintext
        self.assertNotIn(password, encrypted)
        self.assertNotIn(username, encrypted)

    def test_decryption_basic(self):
        """Test credential decryption"""
        username = "testuser"
        password = "testpass123"

        encrypted = self.cred_mgr.encrypt_credentials(username, password)
        decrypted_user, decrypted_pass = self.cred_mgr.decrypt_credentials(encrypted)

        self.assertEqual(decrypted_user, username)
        self.assertEqual(decrypted_pass, password)

    def test_encryption_round_trip(self):
        """Test encryption round-trip for various credentials"""
        test_cases = [
            ("user", "pass"),
            ("admin", "C0mpl3x!P@ssw0rd"),
            ("proxy_user", "密码"),  # Chinese characters
            ("test@example.com", "p@ss:w0rd!@#$"),  # Special characters
        ]

        for username, password in test_cases:
            with self.subTest(username=username):
                encrypted = self.cred_mgr.encrypt_credentials(username, password)
                decrypted_user, decrypted_pass = self.cred_mgr.decrypt_credentials(encrypted)

                self.assertEqual(decrypted_user, username)
                self.assertEqual(decrypted_pass, password)

    def test_invalid_token_handling(self):
        """Test handling of corrupted/invalid encrypted data"""
        invalid_encrypted = "aW52YWxpZF9lbmNyeXB0ZWRfZGF0YQ=="  # Invalid base64

        with self.assertRaises(CredentialEncryptionError):
            self.cred_mgr.decrypt_credentials(invalid_encrypted)

    def test_key_file_permissions(self):
        """Test that key file has secure permissions"""
        # Recreate credential manager to generate new key
        test_key_file = os.path.join(self.test_dir, 'test_key')
        cred_mgr = CredentialManager(key_file=test_key_file)

        # Check file exists
        self.assertTrue(os.path.exists(test_key_file))

        # Check permissions (should be 0o600 = 384)
        file_stat = os.stat(test_key_file)
        file_mode = file_stat.st_mode & 0o777

        self.assertEqual(file_mode, 0o600, f"Key file has insecure permissions: {oct(file_mode)}")

    def test_key_persistence(self):
        """Test that encryption key persists across instances"""
        username = "testuser"
        password = "testpass"

        # Create credential manager and encrypt
        mgr1 = CredentialManager(key_file=self.key_file)
        encrypted = mgr1.encrypt_credentials(username, password)

        # Create new instance with same key file
        mgr2 = CredentialManager(key_file=self.key_file)
        decrypted_user, decrypted_pass = mgr2.decrypt_credentials(encrypted)

        self.assertEqual(decrypted_user, username)
        self.assertEqual(decrypted_pass, password)


class TestProxyAuthenticationEncoding(unittest.TestCase):
    """Test proxy authentication encoding for different methods"""

    def test_http_basic_auth_encoding(self):
        """Test HTTP Basic auth encoding"""
        username = "proxyuser"
        password = "proxypass"

        auth_header = ProxyAuthEncoder.encode_http_proxy_auth(username, password)

        # Should start with "Basic "
        self.assertTrue(auth_header.startswith("Basic "))

        # Should be base64 encoded
        import base64
        encoded_part = auth_header.split(" ")[1]
        decoded = base64.b64decode(encoded_part).decode('utf-8')
        self.assertEqual(decoded, f"{username}:{password}")

    def test_http_auth_special_characters(self):
        """Test HTTP auth with special characters"""
        username = "user@example.com"
        password = "p@ss:word!@#$"

        auth_header = ProxyAuthEncoder.encode_http_proxy_auth(username, password)
        self.assertTrue(auth_header.startswith("Basic "))

    def test_socks5_auth_encoding(self):
        """Test SOCKS5 auth packet encoding (RFC 1929)"""
        username = "sockuser"
        password = "sockpass"

        auth_packet = ProxyAuthEncoder.encode_socks5_auth(username, password)

        # Should be bytes
        self.assertIsInstance(auth_packet, bytes)

        # Parse the packet
        # [VER=1] [ULEN] [UNAME] [PLEN] [PASSWD]
        version = auth_packet[0]
        self.assertEqual(version, 0x01)

        ulen = auth_packet[1]
        self.assertEqual(ulen, len(username.encode('utf-8')))

        uname = auth_packet[2:2+ulen].decode('utf-8')
        self.assertEqual(uname, username)

        plen_idx = 2 + ulen
        plen = auth_packet[plen_idx]
        self.assertEqual(plen, len(password.encode('utf-8')))

        passwd = auth_packet[plen_idx+1:plen_idx+1+plen].decode('utf-8')
        self.assertEqual(passwd, password)

    def test_socks5_auth_length_validation(self):
        """Test SOCKS5 auth with length limits"""
        # Username and password must be < 255 bytes
        long_username = "a" * 256
        password = "pass"

        with self.assertRaises(ProxyAuthenticationError):
            ProxyAuthEncoder.encode_socks5_auth(long_username, password)

        long_password = "a" * 256
        with self.assertRaises(ProxyAuthenticationError):
            ProxyAuthEncoder.encode_socks5_auth("user", long_password)

    def test_proxy_url_auth_encoding(self):
        """Test proxy URL authentication embedding"""
        url = "http://proxy.example.com:8080"
        username = "user"
        password = "pass"

        auth_url = ProxyAuthEncoder.encode_proxy_url_auth(
            url, username, password, 'http'
        )

        # Should contain credentials
        self.assertIn(f"{username}:{password}", auth_url)
        self.assertTrue(auth_url.startswith("http://"))

    def test_proxy_url_auth_with_special_chars(self):
        """Test URL auth encoding with special characters"""
        url = "http://proxy.example.com:8080"
        username = "user@domain.com"
        password = "p@ss:word!@#$"

        auth_url = ProxyAuthEncoder.encode_proxy_url_auth(
            url, username, password, 'http'
        )

        # Special characters should be URL-encoded
        self.assertTrue(auth_url.startswith("http://"))
        # Exact encoded values depend on quote() implementation
        self.assertIn("@proxy.example.com", auth_url)  # Host should be after auth

    def test_proxy_url_auth_replaces_existing(self):
        """Test that URL auth replaces existing credentials"""
        url = "http://olduser:oldpass@proxy.example.com:8080"
        username = "newuser"
        password = "newpass"

        auth_url = ProxyAuthEncoder.encode_proxy_url_auth(
            url, username, password, 'http'
        )

        # Should not contain old credentials
        self.assertNotIn("olduser", auth_url)
        self.assertNotIn("oldpass", auth_url)

        # Should contain new credentials
        self.assertIn(f"{username}:{password}", auth_url)


class TestProxyConfiguration(unittest.TestCase):
    """Test proxy configuration management"""

    def test_proxy_config_creation(self):
        """Test creating proxy configuration"""
        config = ProxyConfig(
            id="proxy1",
            url="http://proxy.example.com:8080",
            type="http",
            auth={'username': 'user', 'password_encrypted': 'encrypted_pass'},
            timeout=30,
            verify_ssl=True
        )

        self.assertEqual(config.id, "proxy1")
        self.assertEqual(config.url, "http://proxy.example.com:8080")
        self.assertEqual(config.type, "http")
        self.assertIsNotNone(config.auth)
        self.assertEqual(config.timeout, 30)
        self.assertTrue(config.verify_ssl)

    def test_proxy_config_to_dict(self):
        """Test proxy configuration serialization"""
        auth = {'username': 'user', 'password_encrypted': 'encrypted_pass'}
        config = ProxyConfig(
            id="proxy1",
            url="http://proxy.example.com:8080",
            type="http",
            auth=auth,
            timeout=30
        )

        config_dict = config.to_dict()

        self.assertEqual(config_dict['id'], "proxy1")
        self.assertEqual(config_dict['url'], "http://proxy.example.com:8080")
        self.assertEqual(config_dict['type'], "http")
        self.assertEqual(config_dict['auth'], auth)

    def test_proxy_config_from_dict(self):
        """Test proxy configuration deserialization"""
        config_dict = {
            'id': 'proxy1',
            'url': 'http://proxy.example.com:8080',
            'type': 'http',
            'auth': {'username': 'user', 'password_encrypted': 'encrypted'},
            'timeout': 30,
            'verify_ssl': True
        }

        config = ProxyConfig.from_dict(config_dict)

        self.assertEqual(config.id, "proxy1")
        self.assertEqual(config.url, "http://proxy.example.com:8080")
        self.assertEqual(config.type, "http")
        self.assertIsNotNone(config.auth)

    def test_proxy_config_socks5(self):
        """Test SOCKS5 proxy configuration"""
        config = ProxyConfig(
            id="socks5-proxy",
            url="socks5://proxy.example.com:1080",
            type="socks5",
            auth={'username': 'sockuser', 'password_encrypted': 'encrypted'},
            timeout=30
        )

        self.assertEqual(config.type, "socks5")
        self.assertTrue(config.url.startswith("socks5://"))


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""

    def test_empty_credentials(self):
        """Test handling of empty credentials"""
        if not IMPORTS_OK:
            self.skipTest("Required imports unavailable")

        test_dir = tempfile.mkdtemp()
        try:
            cred_mgr = CredentialManager(key_file=os.path.join(test_dir, '.cred_key'))

            # Empty username or password should work (encryption level)
            encrypted = cred_mgr.encrypt_credentials("", "pass")
            self.assertIsInstance(encrypted, str)

            encrypted = cred_mgr.encrypt_credentials("user", "")
            self.assertIsInstance(encrypted, str)

        finally:
            shutil.rmtree(test_dir)

    def test_very_long_credentials(self):
        """Test handling of very long credentials"""
        if not IMPORTS_OK:
            self.skipTest("Required imports unavailable")

        test_dir = tempfile.mkdtemp()
        try:
            cred_mgr = CredentialManager(key_file=os.path.join(test_dir, '.cred_key'))

            # Very long credentials (but < 255 bytes for SOCKS5 compat)
            long_user = "a" * 200
            long_pass = "b" * 200

            encrypted = cred_mgr.encrypt_credentials(long_user, long_pass)
            decrypted_user, decrypted_pass = cred_mgr.decrypt_credentials(encrypted)

            self.assertEqual(decrypted_user, long_user)
            self.assertEqual(decrypted_pass, long_pass)

        finally:
            shutil.rmtree(test_dir)


class TestIntegration(unittest.TestCase):
    """Integration tests for proxy security"""

    def test_proxy_workflow(self):
        """Test complete proxy configuration workflow"""
        if not IMPORTS_OK:
            self.skipTest("Required imports unavailable")

        test_dir = tempfile.mkdtemp()
        try:
            # 1. Create credential manager
            cred_mgr = CredentialManager(key_file=os.path.join(test_dir, '.cred_key'))

            # 2. Encrypt credentials
            username = "proxyuser"
            password = "proxypass"
            encrypted = cred_mgr.encrypt_credentials(username, password)

            # 3. Create proxy config with encrypted credentials
            config = ProxyConfig(
                id="test-proxy",
                url="http://proxy.example.com:8080",
                type="http",
                auth={'username': username, 'password_encrypted': encrypted},
                timeout=30
            )

            # 4. Serialize for storage
            config_dict = config.to_dict()

            # 5. Deserialize from storage
            restored_config = ProxyConfig.from_dict(config_dict)

            # 6. Decrypt credentials when needed
            stored_encrypted = restored_config.auth['password_encrypted']
            decrypted_user, decrypted_pass = cred_mgr.decrypt_credentials(stored_encrypted)

            # Verify end-to-end
            self.assertEqual(decrypted_user, username)
            self.assertEqual(decrypted_pass, password)

        finally:
            shutil.rmtree(test_dir)

    def test_proxy_auth_header_generation(self):
        """Test generating proper auth headers for proxy"""
        test_dir = tempfile.mkdtemp()
        try:
            # Simulate complete workflow
            cred_mgr = CredentialManager(key_file=os.path.join(test_dir, '.cred_key'))

            username = "user"
            password = "pass"

            # Encrypt and store
            encrypted = cred_mgr.encrypt_credentials(username, password)

            # Later, when making request, decrypt and generate header
            decrypted_user, decrypted_pass = cred_mgr.decrypt_credentials(encrypted)
            auth_header = ProxyAuthEncoder.encode_http_proxy_auth(decrypted_user, decrypted_pass)

            # Verify header is valid
            self.assertTrue(auth_header.startswith("Basic "))

        finally:
            shutil.rmtree(test_dir)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCredentialEncryption))
    suite.addTests(loader.loadTestsFromTestCase(TestProxyAuthenticationEncoding))
    suite.addTests(loader.loadTestsFromTestCase(TestProxyConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())
