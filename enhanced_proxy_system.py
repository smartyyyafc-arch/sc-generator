#!/usr/bin/env python3
"""
Enhanced Proxy System - Support for HTTP, HTTPS, SOCKS4, SOCKS5
Advanced proxy configuration, validation, and management
For authorized pentesting and security research
"""

import socket
import struct
import hashlib
import json
import os
import uuid
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
import urllib.parse


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProxyType(Enum):
    """Supported proxy types"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class ProxyAuthType(Enum):
    """Proxy authentication types"""
    NONE = "none"
    BASIC = "basic"
    DIGEST = "digest"


@dataclass
class ProxyCredentials:
    """Proxy authentication credentials"""
    username: str
    password: str
    auth_type: ProxyAuthType = ProxyAuthType.BASIC

    def encode_basic_auth(self) -> str:
        """Encode credentials for Basic authentication"""
        credentials = f"{self.username}:{self.password}"
        import base64
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        auth_type_value = self.auth_type.value if hasattr(self.auth_type, 'value') else self.auth_type
        return {
            'username': self.username,
            'password': self.password,
            'auth_type': auth_type_value
        }

    @staticmethod
    def from_dict(data: Dict) -> 'ProxyCredentials':
        """Create from dictionary"""
        auth_type = ProxyAuthType(data.get('auth_type', 'basic'))
        return ProxyCredentials(
            username=data['username'],
            password=data['password'],
            auth_type=auth_type
        )


@dataclass
class EnhancedProxyConfig:
    """Enhanced proxy configuration"""
    id: str
    url: str
    proxy_type: ProxyType
    host: str
    port: int
    credentials: Optional[ProxyCredentials] = None
    headers: Optional[Dict[str, str]] = None
    timeout: int = 10
    retry_count: int = 3
    tags: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_tested: Optional[str] = None
    test_status: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'url': self.url,
            'proxy_type': self.proxy_type.value,
            'host': self.host,
            'port': self.port,
            'credentials': self.credentials.to_dict() if self.credentials else None,
            'headers': self.headers,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'tags': self.tags,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'last_tested': self.last_tested,
            'test_status': self.test_status,
            'notes': self.notes
        }
        return data

    @staticmethod
    def from_dict(data: Dict) -> 'EnhancedProxyConfig':
        """Create from dictionary"""
        creds = None
        if data.get('credentials'):
            creds = ProxyCredentials.from_dict(data['credentials'])

        return EnhancedProxyConfig(
            id=data['id'],
            url=data['url'],
            proxy_type=ProxyType(data['proxy_type']),
            host=data['host'],
            port=data['port'],
            credentials=creds,
            headers=data.get('headers'),
            timeout=data.get('timeout', 10),
            retry_count=data.get('retry_count', 3),
            tags=data.get('tags', []),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at', datetime.now().isoformat()),
            last_tested=data.get('last_tested'),
            test_status=data.get('test_status'),
            notes=data.get('notes', '')
        )


class ProxyValidator(ABC):
    """Abstract base class for proxy validators"""

    @abstractmethod
    def validate(self, host: str, port: int, timeout: int = 10) -> Tuple[bool, str]:
        """Validate proxy connectivity"""
        pass

    @abstractmethod
    def get_connection_string(self, target_url: str, credentials: Optional[ProxyCredentials] = None) -> str:
        """Get connection string for the proxy type"""
        pass


class HTTPProxyValidator(ProxyValidator):
    """HTTP/HTTPS proxy validator"""

    def validate(self, host: str, port: int, timeout: int = 10) -> Tuple[bool, str]:
        """Test HTTP proxy connectivity"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            return True, "HTTP proxy is reachable"
        except socket.timeout:
            return False, "HTTP proxy connection timed out"
        except socket.error as e:
            return False, f"HTTP proxy connection failed: {str(e)}"
        except Exception as e:
            return False, f"HTTP proxy validation error: {str(e)}"

    def get_connection_string(self, target_url: str, credentials: Optional[ProxyCredentials] = None) -> str:
        """Get HTTP connection string"""
        if credentials:
            auth = credentials.encode_basic_auth()
            return f"http://{auth}@{{host}}:{{port}}"
        return "http://{host}:{port}"


class SOCKS4ProxyValidator(ProxyValidator):
    """SOCKS4 proxy validator"""

    def validate(self, host: str, port: int, timeout: int = 10) -> Tuple[bool, str]:
        """Test SOCKS4 proxy connectivity"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))

            # SOCKS4 greeting
            # Send CONNECT request to localhost:80
            target_host = "127.0.0.1"
            target_port = 80

            request = struct.pack('>BBH', 4, 1, target_port)  # VER, CMD, PORT
            request += socket.inet_aton(target_host)  # IP
            request += b'\x00'  # User ID terminator

            sock.sendall(request)

            # Receive response
            response = sock.recv(8)
            sock.close()

            if len(response) >= 2:
                if response[1] == 90:  # Request granted
                    return True, "SOCKS4 proxy is functional"
                else:
                    return False, f"SOCKS4 request rejected (code: {response[1]})"
            else:
                return False, "Invalid SOCKS4 response"

        except socket.timeout:
            return False, "SOCKS4 proxy connection timed out"
        except socket.error as e:
            return False, f"SOCKS4 proxy connection failed: {str(e)}"
        except Exception as e:
            return False, f"SOCKS4 proxy validation error: {str(e)}"

    def get_connection_string(self, target_url: str, credentials: Optional[ProxyCredentials] = None) -> str:
        """Get SOCKS4 connection string"""
        return "socks4://{host}:{port}"


class SOCKS5ProxyValidator(ProxyValidator):
    """SOCKS5 proxy validator"""

    def validate(self, host: str, port: int, timeout: int = 10) -> Tuple[bool, str]:
        """Test SOCKS5 proxy connectivity"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))

            # SOCKS5 greeting
            # Send initial greeting
            greeting = b'\x05\x01\x00'  # VER 5, NMETHODS 1, NO AUTH
            sock.sendall(greeting)

            # Receive greeting response
            response = sock.recv(2)
            if len(response) < 2:
                sock.close()
                return False, "Invalid SOCKS5 greeting response"

            if response[0] != 5:
                sock.close()
                return False, "SOCKS5 version mismatch"

            # Authenticate if necessary
            auth_method = response[1]
            if auth_method == 0xFF:  # No acceptable method
                sock.close()
                return False, "No acceptable SOCKS5 authentication method"

            # Try simple connection to localhost:80
            target_host = "127.0.0.1"
            target_port = 80

            # Build CONNECT request
            connect_request = b'\x05\x01\x00\x01'  # VER, CMD CONNECT, RSV, ATYP IPv4
            connect_request += socket.inet_aton(target_host)
            connect_request += struct.pack('>H', target_port)

            sock.sendall(connect_request)

            # Receive response
            response = sock.recv(4)
            if len(response) >= 2 and response[0] == 5 and response[1] == 0:
                sock.close()
                return True, "SOCKS5 proxy is functional"
            else:
                sock.close()
                return False, f"SOCKS5 connection failed (response: {response.hex()})"

        except socket.timeout:
            return False, "SOCKS5 proxy connection timed out"
        except socket.error as e:
            return False, f"SOCKS5 proxy connection failed: {str(e)}"
        except Exception as e:
            return False, f"SOCKS5 proxy validation error: {str(e)}"

    def get_connection_string(self, target_url: str, credentials: Optional[ProxyCredentials] = None) -> str:
        """Get SOCKS5 connection string"""
        if credentials:
            return f"socks5://{credentials.username}:{credentials.password}@{{host}}:{{port}}"
        return "socks5://{host}:{port}"


class ProxyParserValidator:
    """Parse and validate proxy URLs"""

    PROXY_PATTERN = re.compile(
        r'^(http|https|socks4|socks5)://'  # Protocol
        r'(?:([^:@]+)(?::([^@]+))?@)?'  # Optional credentials
        r'([^/:]+)'  # Host
        r'(?::(\d+))?'  # Optional port
        r'(?:/.*)?$',  # Optional path
        re.IGNORECASE
    )

    @classmethod
    def parse_proxy_url(cls, url: str) -> Tuple[bool, Optional[Dict], str]:
        """Parse proxy URL and extract components"""
        match = cls.PROXY_PATTERN.match(url)

        if not match:
            return False, None, "Invalid proxy URL format"

        protocol, username, password, host, port = match.groups()
        protocol = protocol.lower()

        # Get default port based on protocol
        default_ports = {
            'http': 80,
            'https': 443,
            'socks4': 1080,
            'socks5': 1080
        }

        if not port:
            port = default_ports.get(protocol, 1080)
        else:
            try:
                port = int(port)
                if not (1 <= port <= 65535):
                    return False, None, f"Port must be between 1 and 65535, got {port}"
            except ValueError:
                return False, None, f"Invalid port number: {port}"

        credentials = None
        if username and password:
            auth_type = ProxyAuthType.BASIC
            credentials = {
                'username': username,
                'password': password,
                'auth_type': auth_type.value
            }

        result = {
            'protocol': protocol,
            'host': host,
            'port': port,
            'credentials': credentials
        }

        return True, result, "Proxy URL parsed successfully"

    @classmethod
    def validate_proxy_url(cls, url: str) -> Tuple[bool, str]:
        """Validate proxy URL format"""
        success, parsed, message = cls.parse_proxy_url(url)
        return success, message


class EnhancedProxyManager:
    """Manage enhanced proxy configurations"""

    def __init__(self, config_dir: str = '/tmp/sc-proxies'):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

        self.proxies: Dict[str, EnhancedProxyConfig] = {}
        self.validators: Dict[ProxyType, ProxyValidator] = {
            ProxyType.HTTP: HTTPProxyValidator(),
            ProxyType.HTTPS: HTTPProxyValidator(),
            ProxyType.SOCKS4: SOCKS4ProxyValidator(),
            ProxyType.SOCKS5: SOCKS5ProxyValidator(),
        }

        self._load_proxies()

    def _load_proxies(self):
        """Load proxy configurations from disk"""
        proxy_file = os.path.join(self.config_dir, 'proxies.json')
        if os.path.exists(proxy_file):
            try:
                with open(proxy_file, 'r') as f:
                    data = json.load(f)
                    for proxy_data in data:
                        proxy = EnhancedProxyConfig.from_dict(proxy_data)
                        self.proxies[proxy.id] = proxy
                logger.info(f"Loaded {len(self.proxies)} proxies from disk")
            except Exception as e:
                logger.error(f"Error loading proxies: {e}")

    def _save_proxies(self):
        """Save proxy configurations to disk"""
        proxy_file = os.path.join(self.config_dir, 'proxies.json')
        data = [proxy.to_dict() for proxy in self.proxies.values()]
        with open(proxy_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(self.proxies)} proxies to disk")

    def add_proxy(self, url: str, tags: List[str] = None, notes: str = "") -> Tuple[bool, str, Optional[str]]:
        """Add a proxy configuration from URL"""
        # Parse URL
        success, parsed, message = ProxyParserValidator.parse_proxy_url(url)
        if not success:
            return False, message, None

        # Validate protocol
        try:
            proxy_type = ProxyType(parsed['protocol'])
        except ValueError:
            return False, f"Unsupported proxy type: {parsed['protocol']}", None

        # Create proxy config
        proxy_id = str(uuid.uuid4())[:12]

        credentials = None
        if parsed['credentials']:
            credentials = ProxyCredentials(**parsed['credentials'])

        proxy = EnhancedProxyConfig(
            id=proxy_id,
            url=url,
            proxy_type=proxy_type,
            host=parsed['host'],
            port=parsed['port'],
            credentials=credentials,
            tags=tags or [],
            notes=notes
        )

        self.proxies[proxy_id] = proxy
        self._save_proxies()

        logger.info(f"Added proxy: {proxy_id} ({proxy_type.value}://{parsed['host']}:{parsed['port']})")
        return True, "Proxy added successfully", proxy_id

    def remove_proxy(self, proxy_id: str) -> Tuple[bool, str]:
        """Remove proxy configuration"""
        if proxy_id not in self.proxies:
            return False, f"Proxy {proxy_id} not found"

        del self.proxies[proxy_id]
        self._save_proxies()
        logger.info(f"Removed proxy: {proxy_id}")
        return True, "Proxy removed successfully"

    def test_proxy(self, proxy_id: str, timeout: int = 10) -> Tuple[bool, str]:
        """Test proxy connectivity"""
        if proxy_id not in self.proxies:
            return False, f"Proxy {proxy_id} not found"

        proxy = self.proxies[proxy_id]

        if not proxy.is_active:
            return False, "Proxy is not active"

        validator = self.validators.get(proxy.proxy_type)
        if not validator:
            return False, f"No validator for proxy type: {proxy.proxy_type.value}"

        success, message = validator.validate(proxy.host, proxy.port, timeout)

        # Update test status
        proxy.last_tested = datetime.now().isoformat()
        proxy.test_status = "passed" if success else "failed"
        self._save_proxies()

        logger.info(f"Proxy test {'passed' if success else 'failed'}: {proxy_id} - {message}")
        return success, message

    def test_all_proxies(self, timeout: int = 10) -> Dict[str, Tuple[bool, str]]:
        """Test all active proxies"""
        results = {}
        for proxy_id in self.proxies:
            if self.proxies[proxy_id].is_active:
                success, message = self.test_proxy(proxy_id, timeout)
                results[proxy_id] = (success, message)
        return results

    def get_proxy(self, proxy_id: str) -> Optional[Dict]:
        """Get proxy configuration"""
        if proxy_id not in self.proxies:
            return None
        return self.proxies[proxy_id].to_dict()

    def get_all_proxies(self, active_only: bool = False) -> List[Dict]:
        """Get all proxy configurations"""
        proxies = []
        for proxy in self.proxies.values():
            if active_only and not proxy.is_active:
                continue
            proxies.append(proxy.to_dict())
        return proxies

    def get_proxies_by_type(self, proxy_type: ProxyType) -> List[Dict]:
        """Get proxies by type"""
        proxies = []
        for proxy in self.proxies.values():
            if proxy.proxy_type == proxy_type:
                proxies.append(proxy.to_dict())
        return proxies

    def get_proxies_by_tag(self, tag: str) -> List[Dict]:
        """Get proxies by tag"""
        proxies = []
        for proxy in self.proxies.values():
            if tag in proxy.tags:
                proxies.append(proxy.to_dict())
        return proxies

    def get_connection_string(self, proxy_id: str, target_url: str = "") -> Optional[str]:
        """Get connection string for proxy"""
        if proxy_id not in self.proxies:
            return None

        proxy = self.proxies[proxy_id]
        validator = self.validators.get(proxy.proxy_type)

        if not validator:
            return None

        connection_string = validator.get_connection_string(target_url, proxy.credentials)
        return connection_string.format(host=proxy.host, port=proxy.port)

    def update_proxy_status(self, proxy_id: str, is_active: bool) -> Tuple[bool, str]:
        """Update proxy active status"""
        if proxy_id not in self.proxies:
            return False, f"Proxy {proxy_id} not found"

        self.proxies[proxy_id].is_active = is_active
        self._save_proxies()
        status = "activated" if is_active else "deactivated"
        logger.info(f"Proxy {status}: {proxy_id}")
        return True, f"Proxy {status} successfully"

    def add_tag(self, proxy_id: str, tag: str) -> Tuple[bool, str]:
        """Add tag to proxy"""
        if proxy_id not in self.proxies:
            return False, f"Proxy {proxy_id} not found"

        proxy = self.proxies[proxy_id]
        if tag not in proxy.tags:
            proxy.tags.append(tag)
            self._save_proxies()
            logger.info(f"Added tag '{tag}' to proxy {proxy_id}")
            return True, f"Tag '{tag}' added"
        return True, f"Tag '{tag}' already exists"

    def get_statistics(self) -> Dict[str, Any]:
        """Get proxy statistics"""
        total = len(self.proxies)
        active = sum(1 for p in self.proxies.values() if p.is_active)
        tested = sum(1 for p in self.proxies.values() if p.last_tested)
        passed = sum(1 for p in self.proxies.values() if p.test_status == "passed")

        by_type = {}
        for proxy_type in ProxyType:
            count = sum(1 for p in self.proxies.values() if p.proxy_type == proxy_type)
            if count > 0:
                by_type[proxy_type.value] = count

        return {
            'total_proxies': total,
            'active_proxies': active,
            'tested_proxies': tested,
            'passed_tests': passed,
            'by_type': by_type
        }

    def export_report(self, output_file: str = None) -> Dict:
        """Export comprehensive proxy report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'proxies': self.get_all_proxies(),
            'summary': {
                'total': len(self.proxies),
                'active': sum(1 for p in self.proxies.values() if p.is_active),
                'success_rate': self._calculate_success_rate()
            }
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report exported to {output_file}")

        return report

    def _calculate_success_rate(self) -> float:
        """Calculate proxy test success rate"""
        tested = [p for p in self.proxies.values() if p.last_tested]
        if not tested:
            return 0.0

        passed = sum(1 for p in tested if p.test_status == "passed")
        return round((passed / len(tested)) * 100, 2)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("ENHANCED PROXY SYSTEM - COMPREHENSIVE TEST")
    print("=" * 80)

    # Initialize manager
    manager = EnhancedProxyManager()

    # Test proxy URL parsing
    print("\n1. Testing Proxy URL Parsing")
    print("-" * 80)

    test_urls = [
        "http://proxy.example.com:8080",
        "https://user:pass@secure-proxy.com:8443",
        "socks4://socks4.proxy.com:1080",
        "socks5://user:pass@socks5.proxy.com:1080",
        "invalid://proxy",
    ]

    for url in test_urls:
        success, parsed, message = ProxyParserValidator.parse_proxy_url(url)
        status = "OK" if success else "FAIL"
        print(f"  [{status}] {url}")
        if success:
            print(f"       -> Type: {parsed['protocol']}, Host: {parsed['host']}:{parsed['port']}")
            if parsed['credentials']:
                print(f"       -> Auth: {parsed['credentials']['username']}")
        else:
            print(f"       -> Error: {message}")

    # Add proxies
    print("\n2. Adding Proxies")
    print("-" * 80)

    proxy_configs = [
        ("http://proxy1.example.com:8080", ["http", "test"], "Corporate HTTP proxy"),
        ("https://secure-proxy.example.com:8443", ["https", "secure"], "HTTPS proxy"),
        ("socks4://socks4.example.com:1080", ["socks4", "legacy"], "Legacy SOCKS4"),
        ("socks5://user:pass@socks5.example.com:1080", ["socks5", "secure"], "SOCKS5 with auth"),
    ]

    added_ids = []
    for url, tags, notes in proxy_configs:
        success, message, proxy_id = manager.add_proxy(url, tags, notes)
        if success:
            print(f"  [OK] Added: {proxy_id}")
            added_ids.append(proxy_id)
        else:
            print(f"  [FAIL] {message}")

    # Display proxies
    print("\n3. Configured Proxies")
    print("-" * 80)

    for proxy in manager.get_all_proxies():
        print(f"  ID: {proxy['id']}")
        print(f"    URL: {proxy['url']}")
        print(f"    Type: {proxy['proxy_type']}")
        print(f"    Tags: {', '.join(proxy['tags'])}")
        print(f"    Active: {proxy['is_active']}")
        print()

    # Test proxy by type
    print("\n4. Proxies by Type")
    print("-" * 80)

    for proxy_type in ProxyType:
        proxies = manager.get_proxies_by_type(proxy_type)
        print(f"  {proxy_type.value.upper()}: {len(proxies)} proxy/proxies")
        for proxy in proxies:
            print(f"    - {proxy['host']}:{proxy['port']}")

    # Test by tag
    print("\n5. Proxies by Tag")
    print("-" * 80)

    tags_to_search = ["secure", "test", "socks5"]
    for tag in tags_to_search:
        proxies = manager.get_proxies_by_tag(tag)
        print(f"  Tag '{tag}': {len(proxies)} proxy/proxies")

    # Get statistics
    print("\n6. Proxy Statistics")
    print("-" * 80)

    stats = manager.get_statistics()
    print(f"  Total Proxies: {stats['total_proxies']}")
    print(f"  Active Proxies: {stats['active_proxies']}")
    print(f"  Tested Proxies: {stats['tested_proxies']}")
    print(f"  Passed Tests: {stats['passed_tests']}")
    print(f"  By Type:")
    for ptype, count in stats['by_type'].items():
        print(f"    - {ptype}: {count}")

    # Export report
    print("\n7. Exporting Report")
    print("-" * 80)

    report_file = os.path.join(manager.config_dir, 'proxy_report.json')
    report = manager.export_report(report_file)
    print(f"  Report exported to: {report_file}")
    print(f"  Success Rate: {report['summary']['success_rate']}%")

    print("\n" + "=" * 80)
    print("ENHANCED PROXY SYSTEM - TEST COMPLETE")
    print("=" * 80)
