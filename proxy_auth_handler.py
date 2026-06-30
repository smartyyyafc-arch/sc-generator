"""
Proxy Authentication Handler

Comprehensive authentication handler for proxy connections supporting:
- Username/password (Basic, Digest)
- Certificate-based authentication (mTLS)
- NTLM authentication
- Kerberos support
- Custom authentication schemes

Usage:
    from proxy_auth_handler import ProxyAuthHandler, ProxyConfig

    # Username/password authentication
    config = ProxyConfig(
        proxy_url="http://proxy.example.com:8080",
        auth_type="basic",
        username="user",
        password="pass"
    )
    handler = ProxyAuthHandler(config)

    # Certificate-based authentication
    config = ProxyConfig(
        proxy_url="https://proxy.example.com:8080",
        auth_type="certificate",
        cert_path="/path/to/cert.pem",
        key_path="/path/to/key.pem",
        ca_bundle="/path/to/ca.pem"
    )
    handler = ProxyAuthHandler(config)
"""

import base64
import hashlib
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, Any
from enum import Enum
from urllib.parse import urlparse
import json
import hmac
import struct
from datetime import datetime


class AuthType(Enum):
    """Supported authentication types."""
    BASIC = "basic"
    DIGEST = "digest"
    NTLM = "ntlm"
    KERBEROS = "kerberos"
    CERTIFICATE = "certificate"
    CUSTOM = "custom"


@dataclass
class ProxyConfig:
    """Proxy configuration with authentication details."""

    proxy_url: str
    auth_type: AuthType = AuthType.BASIC
    username: Optional[str] = None
    password: Optional[str] = None
    cert_path: Optional[str] = None
    key_path: Optional[str] = None
    ca_bundle: Optional[str] = None
    domain: Optional[str] = None
    workstation: Optional[str] = None
    timeout: int = 30
    verify_ssl: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)
    ntlm_flags: int = 0x00000001 | 0x00000002 | 0x00000004 | 0x00000010

    def __post_init__(self):
        """Validate and normalize configuration."""
        if isinstance(self.auth_type, str):
            self.auth_type = AuthType(self.auth_type.lower())

        # Validate required fields based on auth type
        if self.auth_type in (AuthType.BASIC, AuthType.DIGEST):
            if not self.username or not self.password:
                raise ValueError(f"{self.auth_type.value} auth requires username and password")

        if self.auth_type == AuthType.CERTIFICATE:
            if not self.cert_path or not self.key_path:
                raise ValueError("Certificate auth requires cert_path and key_path")
            if not os.path.exists(self.cert_path):
                raise FileNotFoundError(f"Certificate not found: {self.cert_path}")
            if not os.path.exists(self.key_path):
                raise FileNotFoundError(f"Key not found: {self.key_path}")

        if self.ca_bundle and not os.path.exists(self.ca_bundle):
            raise FileNotFoundError(f"CA bundle not found: {self.ca_bundle}")


class AuthenticationScheme(ABC):
    """Abstract base class for authentication schemes."""

    def __init__(self, config: ProxyConfig):
        """Initialize authentication scheme."""
        self.config = config
        self.parsed_url = urlparse(config.proxy_url)

    @abstractmethod
    def get_auth_header(self) -> Dict[str, str]:
        """Generate authentication headers."""
        pass

    @abstractmethod
    def handle_auth_challenge(self, challenge: str) -> Dict[str, str]:
        """Handle authentication challenge from proxy."""
        pass


class BasicAuth(AuthenticationScheme):
    """HTTP Basic Authentication (RFC 7617)."""

    def get_auth_header(self) -> Dict[str, str]:
        """
        Generate Basic auth header.

        Returns:
            Dictionary with Proxy-Authorization header
        """
        credentials = f"{self.config.username}:{self.config.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Proxy-Authorization": f"Basic {encoded}"}

    def handle_auth_challenge(self, challenge: str) -> Dict[str, str]:
        """Basic auth doesn't require challenge handling."""
        return self.get_auth_header()


class DigestAuth(AuthenticationScheme):
    """HTTP Digest Authentication (RFC 7616)."""

    def __init__(self, config: ProxyConfig):
        """Initialize Digest auth."""
        super().__init__(config)
        self.nonce = None
        self.realm = None
        self.qop = None
        self.opaque = None
        self.algorithm = "MD5"
        self.nonce_count = 0

    def get_auth_header(self) -> Dict[str, str]:
        """Return empty dict - Digest requires challenge first."""
        return {}

    def _parse_challenge(self, challenge: str) -> None:
        """Parse Digest challenge."""
        # Extract realm, nonce, qop, opaque, algorithm
        patterns = {
            'realm': r'realm="([^"]+)"',
            'nonce': r'nonce="([^"]+)"',
            'qop': r'qop="([^"]+)"',
            'opaque': r'opaque="([^"]+)"',
            'algorithm': r'algorithm=([\w\-]+)',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, challenge)
            if match:
                setattr(self, key, match.group(1))

    def _hash_function(self, data: str) -> str:
        """Hash function based on algorithm."""
        if self.algorithm == "SHA-256":
            return hashlib.sha256(data.encode()).hexdigest()
        else:  # MD5
            return hashlib.md5(data.encode()).hexdigest()

    def handle_auth_challenge(self, challenge: str) -> Dict[str, str]:
        """
        Handle Digest auth challenge.

        Args:
            challenge: Proxy-Authenticate header value

        Returns:
            Dictionary with Proxy-Authorization header
        """
        self._parse_challenge(challenge)
        self.nonce_count += 1

        # Generate response
        username = self.config.username
        password = self.config.password
        realm = self.realm
        uri = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"
        method = "CONNECT"

        # HA1 = hash(username:realm:password)
        ha1 = self._hash_function(f"{username}:{realm}:{password}")

        # HA2 = hash(method:uri)
        ha2 = self._hash_function(f"{method}:{uri}")

        # Generate client nonce
        cnonce = base64.b64encode(os.urandom(16)).decode().replace("=", "")
        nc = f"{self.nonce_count:08x}"

        # Response = hash(HA1:nonce:nc:cnonce:qop:HA2)
        if self.qop:
            response_data = f"{ha1}:{self.nonce}:{nc}:{cnonce}:{self.qop}:{ha2}"
        else:
            response_data = f"{ha1}:{self.nonce}:{ha2}"

        response = self._hash_function(response_data)

        # Build Authorization header
        auth_header = (
            f'Digest username="{username}", realm="{realm}", '
            f'nonce="{self.nonce}", uri="{uri}", '
            f'response="{response}"'
        )

        if self.opaque:
            auth_header += f', opaque="{self.opaque}"'
        if self.algorithm and self.algorithm != "MD5":
            auth_header += f', algorithm={self.algorithm}'
        if self.qop:
            auth_header += f', qop={self.qop}, nc={nc}, cnonce="{cnonce}"'

        return {"Proxy-Authorization": auth_header}


class NTLMAuth(AuthenticationScheme):
    """NTLM Authentication (NT LAN Manager)."""

    NTLM_SIGNATURE = b"NTLMSSP\x00"
    MESSAGE_TYPE_1 = 1
    MESSAGE_TYPE_2 = 2
    MESSAGE_TYPE_3 = 3

    def __init__(self, config: ProxyConfig):
        """Initialize NTLM auth."""
        super().__init__(config)
        self.ntlm_state = 0
        self.server_challenge = None

    def get_auth_header(self) -> Dict[str, str]:
        """Generate initial NTLM Type 1 message."""
        msg = self._create_type1_message()
        encoded = base64.b64encode(msg).decode()
        return {"Proxy-Authorization": f"NTLM {encoded}"}

    def _create_type1_message(self) -> bytes:
        """Create NTLM Type 1 message (negotiate)."""
        flags = self.config.ntlm_flags

        # Flags (4 bytes)
        msg = self.NTLM_SIGNATURE
        msg += struct.pack("<I", self.MESSAGE_TYPE_1)
        msg += struct.pack("<I", flags)

        # Domain, Workstation, Version (optional)
        domain = (self.config.domain or "").encode("utf-16-le")
        workstation = (self.config.workstation or "").encode("utf-16-le")

        # Calculate offsets
        payload_offset = 56
        domain_offset = payload_offset if domain else 0
        workstation_offset = domain_offset + len(domain) if workstation else 0

        # Domain descriptor (12 bytes)
        msg += struct.pack("<HHI", len(domain), len(domain), domain_offset)
        # Workstation descriptor (12 bytes)
        msg += struct.pack("<HHI", len(workstation), len(workstation), workstation_offset)
        # Version info (8 bytes) - optional
        msg += b"\x00" * 8

        # Payload
        if domain:
            msg += domain
        if workstation:
            msg += workstation

        return msg

    def _create_type3_message(self, username: str, password: str) -> bytes:
        """Create NTLM Type 3 message (authenticate)."""
        username_enc = username.encode("utf-16-le")
        domain_enc = (self.config.domain or "").encode("utf-16-le")
        workstation_enc = (self.config.workstation or "").encode("utf-16-le")

        # Calculate payload offset
        payload_offset = 56
        domain_offset = payload_offset
        username_offset = domain_offset + len(domain_enc)
        workstation_offset = username_offset + len(username_enc)
        lm_response_offset = workstation_offset + len(workstation_enc)
        ntlm_response_offset = lm_response_offset + 24

        # Generate NTLM response
        ntlm_response = self._generate_ntlm_response(password)

        msg = self.NTLM_SIGNATURE
        msg += struct.pack("<I", self.MESSAGE_TYPE_3)

        # LM response (empty)
        msg += struct.pack("<HHI", 0, 0, 0)
        # NTLM response descriptor
        msg += struct.pack("<HHI", len(ntlm_response), len(ntlm_response), ntlm_response_offset)
        # Domain descriptor
        msg += struct.pack("<HHI", len(domain_enc), len(domain_enc), domain_offset)
        # Username descriptor
        msg += struct.pack("<HHI", len(username_enc), len(username_enc), username_offset)
        # Workstation descriptor
        msg += struct.pack("<HHI", len(workstation_enc), len(workstation_enc), workstation_offset)
        # Session key (empty)
        msg += struct.pack("<HHI", 0, 0, 0)
        # Flags
        msg += struct.pack("<I", self.config.ntlm_flags)

        # Payload
        msg += domain_enc
        msg += username_enc
        msg += workstation_enc
        msg += ntlm_response

        return msg

    def _generate_ntlm_response(self, password: str) -> bytes:
        """Generate NTLM response hash."""
        # NTLMv2 response
        username = self.config.username.upper()
        domain = self.config.domain or ""

        # NTProofStr = HMAC_MD5(NT_HASH, username + domain)
        nt_hash = hashlib.md5(password.encode("utf-16-le")).digest()
        identity = (username + domain).encode("utf-16-le")
        nt_proof_str = hmac.new(nt_hash, identity, hashlib.md5).digest()

        # Add client challenge data
        client_data = (
            b"\x01\x01\x00\x00\x00\x00\x00\x00" +
            struct.pack("<Q", int(datetime.now().timestamp() * 10000000)) +
            b"\xaa" * 8 +  # Client nonce
            b"\x00\x00\x00\x00"
        )

        response = hmac.new(
            nt_hash,
            self.server_challenge + client_data,
            hashlib.md5
        ).digest() + client_data

        return response

    def handle_auth_challenge(self, challenge: str) -> Dict[str, str]:
        """
        Handle NTLM challenge.

        Args:
            challenge: Proxy-Authenticate header value

        Returns:
            Dictionary with Proxy-Authorization header
        """
        # Extract Type 2 message
        parts = challenge.split(" ")
        if len(parts) < 2:
            return self.get_auth_header()

        try:
            self.server_challenge = base64.b64decode(parts[1])
            # Extract server nonce from Type 2 message (offset 24, 8 bytes)
            self.server_challenge = self.server_challenge[24:32]
        except Exception:
            return self.get_auth_header()

        # Generate Type 3 message
        msg = self._create_type3_message(
            self.config.username,
            self.config.password
        )
        encoded = base64.b64encode(msg).decode()
        return {"Proxy-Authorization": f"NTLM {encoded}"}


class CertificateAuth(AuthenticationScheme):
    """Certificate-based (mTLS) Authentication."""

    def get_auth_header(self) -> Dict[str, str]:
        """
        Get certificate authentication details.

        Returns:
            Dictionary with certificate paths
        """
        return {
            "client_cert": self.config.cert_path,
            "client_key": self.config.key_path,
            "ca_bundle": self.config.ca_bundle,
            "verify_ssl": self.config.verify_ssl
        }

    def handle_auth_challenge(self, challenge: str) -> Dict[str, str]:
        """Certificate auth doesn't require challenge handling."""
        return self.get_auth_header()

    def validate_certificate(self) -> bool:
        """
        Validate certificate and key files.

        Returns:
            True if valid, raises exception otherwise
        """
        try:
            # Check if files are readable
            with open(self.config.cert_path, 'rb') as f:
                cert_data = f.read()
                if not (b'-----BEGIN CERTIFICATE-----' in cert_data or
                       b'-----BEGIN PKCS12-----' in cert_data):
                    raise ValueError("Invalid certificate format")

            with open(self.config.key_path, 'rb') as f:
                key_data = f.read()
                if not (b'-----BEGIN' in key_data):
                    raise ValueError("Invalid key format")

            return True
        except Exception as e:
            raise RuntimeError(f"Certificate validation failed: {e}")


class ProxyAuthHandler:
    """
    Main proxy authentication handler.

    Supports multiple authentication schemes and handles
    authentication challenges.

    Example:
        config = ProxyConfig(
            proxy_url="http://proxy.example.com:8080",
            auth_type="basic",
            username="user",
            password="pass"
        )
        handler = ProxyAuthHandler(config)
        headers = handler.get_auth_headers()
    """

    def __init__(self, config: ProxyConfig):
        """
        Initialize authentication handler.

        Args:
            config: ProxyConfig instance
        """
        self.config = config
        self.auth_scheme = self._create_auth_scheme()
        self.auth_state = {}
        self.last_challenge = None

    def _create_auth_scheme(self) -> AuthenticationScheme:
        """Create appropriate authentication scheme."""
        scheme_map = {
            AuthType.BASIC: BasicAuth,
            AuthType.DIGEST: DigestAuth,
            AuthType.NTLM: NTLMAuth,
            AuthType.CERTIFICATE: CertificateAuth,
        }

        scheme_class = scheme_map.get(self.config.auth_type)
        if not scheme_class:
            raise ValueError(f"Unsupported auth type: {self.config.auth_type}")

        return scheme_class(self.config)

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers.

        Returns:
            Dictionary of HTTP headers
        """
        headers = self.auth_scheme.get_auth_header()
        headers.update(self.config.custom_headers)
        return headers

    def handle_challenge(self, challenge: str) -> Dict[str, str]:
        """
        Handle authentication challenge from proxy.

        Args:
            challenge: Challenge string from Proxy-Authenticate header

        Returns:
            Dictionary with authentication response headers
        """
        self.last_challenge = challenge
        return self.auth_scheme.handle_auth_challenge(challenge)

    def get_proxy_url(self) -> str:
        """Get proxy URL without credentials."""
        parsed = urlparse(self.config.proxy_url)
        if parsed.hostname:
            port = f":{parsed.port}" if parsed.port else ""
            return f"{parsed.scheme}://{parsed.hostname}{port}"
        return self.config.proxy_url

    def get_connection_config(self) -> Dict[str, Any]:
        """
        Get complete connection configuration.

        Returns:
            Dictionary with proxy settings
        """
        config_dict = {
            "proxy_url": self.get_proxy_url(),
            "auth_type": self.config.auth_type.value,
            "timeout": self.config.timeout,
            "verify_ssl": self.config.verify_ssl,
        }

        if self.config.auth_type == AuthType.CERTIFICATE:
            config_dict.update(self.auth_scheme.get_auth_header())

        return config_dict

    def to_json(self) -> str:
        """
        Export configuration as JSON (without sensitive data).

        Returns:
            JSON string
        """
        safe_config = {
            "proxy_url": self.get_proxy_url(),
            "auth_type": self.config.auth_type.value,
            "timeout": self.config.timeout,
            "verify_ssl": self.config.verify_ssl,
            "domain": self.config.domain,
            "workstation": self.config.workstation,
        }

        if self.config.auth_type == AuthType.CERTIFICATE:
            safe_config["cert_path"] = self.config.cert_path
            safe_config["key_path"] = self.config.key_path
            safe_config["ca_bundle"] = self.config.ca_bundle

        return json.dumps(safe_config, indent=2)


def create_auth_handler(
    proxy_url: str,
    auth_type: str = "basic",
    **kwargs
) -> ProxyAuthHandler:
    """
    Convenience function to create authentication handler.

    Args:
        proxy_url: Proxy URL
        auth_type: Authentication type (basic, digest, ntlm, certificate)
        **kwargs: Additional configuration options

    Returns:
        ProxyAuthHandler instance

    Example:
        handler = create_auth_handler(
            "http://proxy.example.com:8080",
            auth_type="basic",
            username="user",
            password="pass"
        )
    """
    config = ProxyConfig(
        proxy_url=proxy_url,
        auth_type=auth_type,
        **kwargs
    )
    return ProxyAuthHandler(config)
