#!/usr/bin/env python3
"""
Proxy Chain Configuration Builder for Multi-Hop Routing

Supports building complex proxy chains with multiple sequential hops,
authentication per hop, protocol selection, and intelligent routing.

Features:
- Multi-hop proxy chaining (sequential routing through multiple proxies)
- Per-hop authentication configuration
- Protocol routing (HTTP/HTTPS/SOCKS4/SOCKS5)
- Chain validation and circular dependency detection
- Dynamic proxy selection and load balancing
- Chain state tracking and failure handling
- Metrics collection per hop
- Export/import chain configurations

Usage:
    from proxy_chain_builder import ProxyChainBuilder, ProxyChainConfig

    # Build a simple chain
    builder = ProxyChainBuilder()
    builder.add_hop("proxy1.example.com", 8080, "basic",
                   username="user1", password="pass1")
    builder.add_hop("proxy2.example.com", 8080, "basic",
                   username="user2", password="pass2")

    chain = builder.build()

    # Build from configuration file
    config = ProxyChainConfig.from_file("chain_config.json")
    chain = ProxyChainBuilder.from_config(config).build()
"""

import json
import hashlib
import threading
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlunparse
import copy
import base64


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProxyProtocol(Enum):
    """Supported proxy protocols"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"
    SOCKS5H = "socks5h"


class AuthType(Enum):
    """Proxy authentication types"""
    NONE = "none"
    BASIC = "basic"
    DIGEST = "digest"
    NTLM = "ntlm"
    CERTIFICATE = "certificate"
    CUSTOM = "custom"


class ChainState(Enum):
    """Proxy chain state"""
    INITIALIZED = "initialized"
    VALIDATED = "validated"
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"


class HopState(Enum):
    """Individual proxy hop state"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    SUSPENDED = "suspended"
    RECOVERING = "recovering"


@dataclass
class HopMetrics:
    """Metrics for individual proxy hop"""
    hop_index: int
    proxy_address: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    last_update: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_average_response_time(self) -> float:
        """Calculate average response time"""
        if self.total_requests == 0:
            return 0.0
        return self.total_response_time / self.total_requests

    def get_success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100


@dataclass
class ProxyHopConfig:
    """Configuration for a single proxy hop"""

    # Proxy connection details
    hostname: str
    port: int
    protocol: ProxyProtocol = ProxyProtocol.HTTP

    # Authentication
    auth_type: AuthType = AuthType.NONE
    username: Optional[str] = None
    password: Optional[str] = None

    # Certificate authentication
    cert_path: Optional[str] = None
    key_path: Optional[str] = None
    ca_bundle: Optional[str] = None

    # Connection settings
    timeout: int = 30
    verify_ssl: bool = True

    # Custom settings
    custom_headers: Dict[str, str] = field(default_factory=dict)
    proxy_headers: Dict[str, str] = field(default_factory=dict)

    # Metadata
    label: Optional[str] = None
    priority: int = 0
    enabled: bool = True

    def __post_init__(self):
        """Validate configuration"""
        if not self.hostname:
            raise ValueError("Hostname is required")
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port: {self.port}")

        if isinstance(self.protocol, str):
            self.protocol = ProxyProtocol(self.protocol.lower())

        if isinstance(self.auth_type, str):
            self.auth_type = AuthType(self.auth_type.lower())

        # Validate authentication
        if self.auth_type in (AuthType.BASIC, AuthType.DIGEST, AuthType.NTLM):
            if not self.username or not self.password:
                raise ValueError(f"{self.auth_type.value} auth requires username and password")

        if self.auth_type == AuthType.CERTIFICATE:
            if not self.cert_path or not self.key_path:
                raise ValueError("Certificate auth requires cert_path and key_path")

    def get_proxy_url(self) -> str:
        """Get proxy URL without authentication"""
        return f"{self.protocol.value}://{self.hostname}:{self.port}"

    def get_proxy_url_with_auth(self) -> str:
        """Get proxy URL with authentication (if applicable)"""
        if self.auth_type == AuthType.BASIC and self.username and self.password:
            encoded_auth = base64.b64encode(
                f"{self.username}:{self.password}".encode()
            ).decode()
            return (
                f"{self.protocol.value}://{self.username}:***@"
                f"{self.hostname}:{self.port}"
            )
        return self.get_proxy_url()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "hostname": self.hostname,
            "port": self.port,
            "protocol": self.protocol.value,
            "auth_type": self.auth_type.value,
            "timeout": self.timeout,
            "verify_ssl": self.verify_ssl,
            "label": self.label,
            "priority": self.priority,
            "enabled": self.enabled
        }


@dataclass
class ProxyChainConfig:
    """Configuration for entire proxy chain"""

    chain_name: str
    description: str = ""
    hops: List[ProxyHopConfig] = field(default_factory=list)

    # Chain settings
    allow_direct_fallback: bool = False
    enable_load_balancing: bool = False
    max_chain_hops: int = 10
    total_timeout: int = 120

    # Retry configuration
    max_retries_per_hop: int = 2
    retry_backoff_factor: float = 2.0

    # Metrics
    enable_metrics: bool = True
    metrics_retention_days: int = 30

    # Validation
    validate_chain_on_init: bool = True
    circular_hop_detection: bool = True

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate chain configuration

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not self.chain_name:
            errors.append("Chain name is required")

        if len(self.hops) == 0:
            errors.append("At least one proxy hop is required")

        if len(self.hops) > self.max_chain_hops:
            errors.append(
                f"Number of hops ({len(self.hops)}) exceeds maximum ({self.max_chain_hops})"
            )

        # Check for duplicate hostnames (circular dependency)
        if self.circular_hop_detection:
            hostnames = set()
            for i, hop in enumerate(self.hops):
                if (hop.hostname, hop.port) in hostnames:
                    errors.append(
                        f"Duplicate hop detected at index {i}: "
                        f"{hop.hostname}:{hop.port}"
                    )
                hostnames.add((hop.hostname, hop.port))

        # Validate each hop
        for i, hop in enumerate(self.hops):
            try:
                hop_dict = hop.to_dict()  # This will raise if invalid
            except ValueError as e:
                errors.append(f"Hop {i} validation error: {str(e)}")

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "chain_name": self.chain_name,
            "description": self.description,
            "hops": [hop.to_dict() for hop in self.hops],
            "allow_direct_fallback": self.allow_direct_fallback,
            "enable_load_balancing": self.enable_load_balancing,
            "max_chain_hops": self.max_chain_hops,
            "total_timeout": self.total_timeout,
            "max_retries_per_hop": self.max_retries_per_hop,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def to_json(self) -> str:
        """Export to JSON (excludes sensitive data)"""
        return json.dumps(self.to_dict(), indent=2)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ProxyChainConfig':
        """Create from dictionary"""
        hops = [
            ProxyHopConfig(
                hostname=hop['hostname'],
                port=hop['port'],
                protocol=ProxyProtocol(hop.get('protocol', 'http')),
                auth_type=AuthType(hop.get('auth_type', 'none')),
                timeout=hop.get('timeout', 30),
                verify_ssl=hop.get('verify_ssl', True),
                label=hop.get('label')
            )
            for hop in data.get('hops', [])
        ]

        return ProxyChainConfig(
            chain_name=data['chain_name'],
            description=data.get('description', ''),
            hops=hops,
            allow_direct_fallback=data.get('allow_direct_fallback', False),
            enable_load_balancing=data.get('enable_load_balancing', False),
            max_chain_hops=data.get('max_chain_hops', 10),
            total_timeout=data.get('total_timeout', 120)
        )

    @staticmethod
    def from_json(json_str: str) -> 'ProxyChainConfig':
        """Create from JSON string"""
        data = json.loads(json_str)
        return ProxyChainConfig.from_dict(data)

    @staticmethod
    def from_file(file_path: str) -> 'ProxyChainConfig':
        """Load from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return ProxyChainConfig.from_dict(data)


class ProxyChain:
    """Represents an active proxy chain"""

    def __init__(self, config: ProxyChainConfig):
        """Initialize proxy chain"""
        self.config = config
        self.state = ChainState.INITIALIZED
        self.hop_states: Dict[int, HopState] = {}
        self.hop_metrics: Dict[int, HopMetrics] = {}
        self.lock = threading.Lock()
        self.chain_id = self._generate_chain_id()

        # Initialize hop states and metrics
        for i, hop in enumerate(config.hops):
            self.hop_states[i] = HopState.HEALTHY
            self.hop_metrics[i] = HopMetrics(
                hop_index=i,
                proxy_address=hop.get_proxy_url()
            )

        logger.info(f"Proxy chain '{config.chain_name}' initialized with {len(config.hops)} hops")

    def _generate_chain_id(self) -> str:
        """Generate unique chain ID"""
        chain_str = (
            f"{self.config.chain_name}:"
            f"{':'.join(f'{h.hostname}:{h.port}' for h in self.config.hops)}"
        )
        return hashlib.sha256(chain_str.encode()).hexdigest()[:16]

    def get_chain_id(self) -> str:
        """Get chain ID"""
        return self.chain_id

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate chain configuration"""
        is_valid, errors = self.config.validate()

        if is_valid and self.config.validate_chain_on_init:
            with self.lock:
                self.state = ChainState.VALIDATED
                logger.info(f"Chain '{self.config.chain_name}' validated successfully")

        return is_valid, errors

    def get_hop_config(self, hop_index: int) -> Optional[ProxyHopConfig]:
        """Get configuration for specific hop"""
        if 0 <= hop_index < len(self.config.hops):
            return self.config.hops[hop_index]
        return None

    def get_all_hops(self) -> List[ProxyHopConfig]:
        """Get all hop configurations"""
        return copy.deepcopy(self.config.hops)

    def get_enabled_hops(self) -> List[Tuple[int, ProxyHopConfig]]:
        """Get all enabled hops with indices"""
        return [(i, hop) for i, hop in enumerate(self.config.hops) if hop.enabled]

    def record_hop_success(self, hop_index: int, response_time: float = 0.0) -> None:
        """Record successful connection through hop"""
        if hop_index not in self.hop_metrics:
            return

        with self.lock:
            metrics = self.hop_metrics[hop_index]
            metrics.total_requests += 1
            metrics.successful_requests += 1
            metrics.total_response_time += response_time
            metrics.last_update = datetime.now().isoformat()

            # Update hop state
            if self.hop_states[hop_index] != HopState.SUSPENDED:
                self.hop_states[hop_index] = HopState.HEALTHY

    def record_hop_failure(self, hop_index: int) -> None:
        """Record failed connection through hop"""
        if hop_index not in self.hop_metrics:
            return

        with self.lock:
            metrics = self.hop_metrics[hop_index]
            metrics.total_requests += 1
            metrics.failed_requests += 1
            metrics.last_update = datetime.now().isoformat()

            # Update hop state
            if metrics.failed_requests > 3:
                self.hop_states[hop_index] = HopState.UNHEALTHY

    def get_hop_metrics(self, hop_index: int) -> Optional[HopMetrics]:
        """Get metrics for specific hop"""
        with self.lock:
            return copy.deepcopy(self.hop_metrics.get(hop_index))

    def get_all_metrics(self) -> Dict[int, HopMetrics]:
        """Get all hop metrics"""
        with self.lock:
            return {
                idx: copy.deepcopy(metrics)
                for idx, metrics in self.hop_metrics.items()
            }

    def get_hop_state(self, hop_index: int) -> Optional[HopState]:
        """Get state of specific hop"""
        with self.lock:
            return self.hop_states.get(hop_index)

    def get_all_hop_states(self) -> Dict[int, HopState]:
        """Get all hop states"""
        with self.lock:
            return copy.deepcopy(self.hop_states)

    def get_chain_state(self) -> ChainState:
        """Get overall chain state"""
        with self.lock:
            return self.state

    def update_chain_state(self, new_state: ChainState) -> None:
        """Update overall chain state"""
        with self.lock:
            self.state = new_state
            logger.debug(f"Chain state updated to {new_state.value}")

    def get_chain_health(self) -> Dict[str, Any]:
        """Get comprehensive chain health information"""
        with self.lock:
            hop_health = {}
            for idx, hop in enumerate(self.config.hops):
                metrics = self.hop_metrics.get(idx)
                hop_health[idx] = {
                    "proxy": hop.get_proxy_url(),
                    "state": self.hop_states[idx].value if idx in self.hop_states else "unknown",
                    "metrics": asdict(metrics) if metrics else None
                }

            return {
                "chain_id": self.chain_id,
                "chain_name": self.config.chain_name,
                "chain_state": self.state.value,
                "total_hops": len(self.config.hops),
                "enabled_hops": sum(1 for h in self.config.hops if h.enabled),
                "hops": hop_health,
                "timestamp": datetime.now().isoformat()
            }


class ProxyChainBuilder:
    """Builder class for constructing proxy chains"""

    def __init__(self, chain_name: str = "default-chain", description: str = ""):
        """Initialize chain builder"""
        self.chain_name = chain_name
        self.description = description
        self.hops: List[ProxyHopConfig] = []
        self.config_overrides: Dict[str, Any] = {}

    def add_hop(
        self,
        hostname: str,
        port: int,
        auth_type: str = "none",
        protocol: str = "http",
        label: Optional[str] = None,
        **kwargs
    ) -> 'ProxyChainBuilder':
        """
        Add a proxy hop to the chain

        Args:
            hostname: Proxy hostname or IP
            port: Proxy port
            auth_type: Authentication type (none, basic, digest, ntlm, certificate)
            protocol: Protocol (http, https, socks4, socks5)
            label: Optional label for this hop
            **kwargs: Additional configuration (username, password, etc.)

        Returns:
            Self for method chaining
        """
        hop = ProxyHopConfig(
            hostname=hostname,
            port=port,
            protocol=ProxyProtocol(protocol.lower()),
            auth_type=AuthType(auth_type.lower()),
            label=label or f"hop_{len(self.hops)}",
            **kwargs
        )

        self.hops.append(hop)
        logger.debug(f"Added hop: {hop.get_proxy_url()}")

        return self

    def add_hop_from_url(
        self,
        proxy_url: str,
        auth_type: str = "none",
        label: Optional[str] = None,
        **kwargs
    ) -> 'ProxyChainBuilder':
        """
        Add a proxy hop from URL string

        Args:
            proxy_url: Proxy URL (e.g., "http://proxy.example.com:8080")
            auth_type: Authentication type
            label: Optional label
            **kwargs: Additional configuration

        Returns:
            Self for method chaining
        """
        parsed = urlparse(proxy_url)

        hostname = parsed.hostname or "127.0.0.1"
        port = parsed.port or 80
        protocol = parsed.scheme or "http"

        return self.add_hop(
            hostname=hostname,
            port=port,
            protocol=protocol,
            auth_type=auth_type,
            label=label,
            **kwargs
        )

    def set_chain_name(self, name: str) -> 'ProxyChainBuilder':
        """Set chain name"""
        self.chain_name = name
        return self

    def set_description(self, description: str) -> 'ProxyChainBuilder':
        """Set chain description"""
        self.description = description
        return self

    def set_allow_direct_fallback(self, allow: bool = True) -> 'ProxyChainBuilder':
        """Allow direct connection fallback"""
        self.config_overrides['allow_direct_fallback'] = allow
        return self

    def set_max_hops(self, max_hops: int) -> 'ProxyChainBuilder':
        """Set maximum chain hops"""
        self.config_overrides['max_chain_hops'] = max_hops
        return self

    def set_total_timeout(self, timeout: int) -> 'ProxyChainBuilder':
        """Set total chain timeout in seconds"""
        self.config_overrides['total_timeout'] = timeout
        return self

    def enable_load_balancing(self, enable: bool = True) -> 'ProxyChainBuilder':
        """Enable load balancing across hops"""
        self.config_overrides['enable_load_balancing'] = enable
        return self

    def enable_metrics(self, enable: bool = True) -> 'ProxyChainBuilder':
        """Enable metrics collection"""
        self.config_overrides['enable_metrics'] = enable
        return self

    def build(self) -> ProxyChain:
        """
        Build the proxy chain

        Returns:
            ProxyChain instance

        Raises:
            ValueError: If chain configuration is invalid
        """
        # Create configuration
        config = ProxyChainConfig(
            chain_name=self.chain_name,
            description=self.description,
            hops=copy.deepcopy(self.hops)
        )

        # Apply overrides
        for key, value in self.config_overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)

        # Validate configuration
        is_valid, errors = config.validate()
        if not is_valid:
            error_msg = "; ".join(errors)
            raise ValueError(f"Invalid proxy chain configuration: {error_msg}")

        # Create and return chain
        chain = ProxyChain(config)
        is_valid, errors = chain.validate()

        if not is_valid:
            logger.warning(f"Chain validation warnings: {'; '.join(errors)}")

        return chain

    @staticmethod
    def from_config(config: ProxyChainConfig) -> 'ProxyChainBuilder':
        """Create builder from configuration"""
        builder = ProxyChainBuilder(
            chain_name=config.chain_name,
            description=config.description
        )

        for hop in config.hops:
            builder.add_hop(
                hostname=hop.hostname,
                port=hop.port,
                auth_type=hop.auth_type.value,
                protocol=hop.protocol.value,
                label=hop.label,
                username=hop.username,
                password=hop.password,
                cert_path=hop.cert_path,
                key_path=hop.key_path,
                ca_bundle=hop.ca_bundle,
                timeout=hop.timeout,
                verify_ssl=hop.verify_ssl
            )

        # Apply configuration options
        builder.config_overrides = {
            'allow_direct_fallback': config.allow_direct_fallback,
            'enable_load_balancing': config.enable_load_balancing,
            'max_chain_hops': config.max_chain_hops,
            'total_timeout': config.total_timeout,
            'enable_metrics': config.enable_metrics
        }

        return builder

    @staticmethod
    def from_file(file_path: str) -> 'ProxyChainBuilder':
        """Create builder from JSON file"""
        config = ProxyChainConfig.from_file(file_path)
        return ProxyChainBuilder.from_config(config)


# Convenience functions
def create_chain_builder(chain_name: str = "default-chain") -> ProxyChainBuilder:
    """Create a new chain builder"""
    return ProxyChainBuilder(chain_name)


def create_chain_from_config_file(file_path: str) -> ProxyChain:
    """Create chain directly from configuration file"""
    return ProxyChainBuilder.from_file(file_path).build()


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("PROXY CHAIN BUILDER - DEMONSTRATION")
    print("=" * 80)

    # Example 1: Build a simple 2-hop chain
    print("\n1. Building Simple 2-Hop Chain")
    print("-" * 80)

    builder = ProxyChainBuilder("two-hop-chain")
    builder.add_hop(
        "proxy1.example.com", 8080,
        auth_type="basic",
        username="user1",
        password="pass1",
        label="First Hop"
    )
    builder.add_hop(
        "proxy2.example.com", 3128,
        auth_type="basic",
        username="user2",
        password="pass2",
        label="Second Hop"
    )
    builder.set_description("Example 2-hop proxy chain")
    builder.set_total_timeout(60)

    try:
        chain = builder.build()
        print(f"✓ Chain built successfully")
        print(f"  Chain ID: {chain.get_chain_id()}")
        print(f"  Total hops: {len(chain.get_all_hops())}")

        # Show hop details
        for i, hop in enumerate(chain.get_all_hops()):
            print(f"  Hop {i}: {hop.get_proxy_url()}")

        # Show chain health
        health = chain.get_chain_health()
        print(f"\n  Chain Health:")
        print(f"    State: {health['chain_state']}")
        print(f"    Enabled hops: {health['enabled_hops']}/{health['total_hops']}")
    except ValueError as e:
        print(f"✗ Error: {e}")

    # Example 2: Build a 3-hop chain with different protocols
    print("\n2. Building 3-Hop Chain with Mixed Protocols")
    print("-" * 80)

    builder2 = ProxyChainBuilder("multi-protocol-chain")
    builder2.add_hop("proxy1.example.com", 8080, protocol="http")
    builder2.add_hop("proxy2.example.com", 1080, protocol="socks5")
    builder2.add_hop("proxy3.example.com", 8443, protocol="https")
    builder2.set_description("Chain with multiple protocols")
    builder2.enable_metrics(True)

    try:
        chain2 = builder2.build()
        print(f"✓ Chain built successfully")
        print(f"  Chain ID: {chain2.get_chain_id()}")

        for i, hop in enumerate(chain2.get_all_hops()):
            print(f"  Hop {i}: {hop.protocol.value.upper()} - {hop.get_proxy_url()}")
    except ValueError as e:
        print(f"✗ Error: {e}")

    # Example 3: Build from proxy URLs
    print("\n3. Building Chain from Proxy URLs")
    print("-" * 80)

    builder3 = ProxyChainBuilder("url-based-chain")
    builder3.add_hop_from_url("http://proxy1.example.com:8080")
    builder3.add_hop_from_url("http://proxy2.example.com:3128")

    try:
        chain3 = builder3.build()
        print(f"✓ Chain built successfully")
        print(f"  Total hops: {len(chain3.get_all_hops())}")
    except ValueError as e:
        print(f"✗ Error: {e}")

    # Example 4: Export and import configuration
    print("\n4. Configuration Export/Import")
    print("-" * 80)

    builder4 = ProxyChainBuilder("export-demo")
    builder4.add_hop("proxy1.example.com", 8080, label="Hop 1")
    builder4.add_hop("proxy2.example.com", 3128, label="Hop 2")

    chain4 = builder4.build()
    config = chain4.config

    # Export to JSON
    json_config = config.to_json()
    print(f"✓ Configuration exported to JSON ({len(json_config)} bytes)")

    # Show snippet
    print(f"\n  JSON snippet:")
    config_dict = json.loads(json_config)
    print(f"    Chain: {config_dict['chain_name']}")
    print(f"    Hops: {len(config_dict['hops'])}")

    # Import from JSON
    reimported = ProxyChainConfig.from_json(json_config)
    print(f"\n✓ Configuration reimported successfully")
    print(f"  Chain name: {reimported.chain_name}")
    print(f"  Hops: {len(reimported.hops)}")

    # Example 5: Metrics tracking
    print("\n5. Metrics Tracking Example")
    print("-" * 80)

    builder5 = ProxyChainBuilder("metrics-demo")
    builder5.add_hop("proxy1.example.com", 8080, label="Primary")
    builder5.add_hop("proxy2.example.com", 3128, label="Secondary")
    builder5.enable_metrics(True)

    chain5 = builder5.build()

    # Simulate some successful connections
    chain5.record_hop_success(0, response_time=0.5)
    chain5.record_hop_success(1, response_time=0.3)
    chain5.record_hop_success(0, response_time=0.45)

    # Simulate some failures
    chain5.record_hop_failure(1)

    # Get metrics
    health = chain5.get_chain_health()
    print(f"Chain Health Report:")
    print(f"  Chain State: {health['chain_state']}")
    print(f"  Total Hops: {health['total_hops']}")
    print(f"  Enabled Hops: {health['enabled_hops']}")

    print(f"\n  Hop Metrics:")
    for hop_idx, hop_info in health['hops'].items():
        print(f"    Hop {hop_idx}: {hop_info['proxy']}")
        print(f"      State: {hop_info['state']}")
        if hop_info['metrics']:
            print(f"      Requests: {hop_info['metrics']['total_requests']}")
            print(f"      Success: {hop_info['metrics']['successful_requests']}")

    print("\n" + "=" * 80)
    print("PROXY CHAIN BUILDER - DEMONSTRATION COMPLETE")
    print("=" * 80)
