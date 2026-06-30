#!/usr/bin/env python3
"""
C2 Proxy Integration with TLS Certificate Pinning

Integrates TLS pinning with existing C2 proxy systems for secure connections.
Provides fallback mechanisms and audit logging for pentesting environments.

For authorized pentesting and security research only.
"""

import logging
import threading
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

from tls_pinning_c2_proxy import (
    TLSPinningManager,
    PinningStrategy,
    HashAlgorithm,
    PinningValidationResult,
    CertificateExtractor
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FailoverMode(Enum):
    """Failover behavior on pin validation failure"""
    STRICT = "strict"          # Reject connection if pin validation fails
    GRACEFUL = "graceful"      # Log warning but allow connection
    FALLBACK = "fallback"      # Try fallback servers
    ALERT = "alert"            # Alert operator but allow (operator decision)


@dataclass
class C2ProxyConfig:
    """C2 proxy configuration with pinning"""
    proxy_host: str
    proxy_port: int
    proxy_protocol: str = "https"

    # TLS Pinning configuration
    enable_pinning: bool = True
    pinning_strategy: PinningStrategy = PinningStrategy.PUBLIC_KEY
    hash_algorithm: HashAlgorithm = HashAlgorithm.SHA256
    pin_expiration_days: int = 365

    # Fallover configuration
    failover_mode: FailoverMode = FailoverMode.STRICT
    fallback_proxies: List[str] = field(default_factory=list)

    # Connection configuration
    connection_timeout: float = 10.0
    read_timeout: float = 30.0
    verify_ssl: bool = True

    # Audit configuration
    enable_audit: bool = True
    audit_on_failure: bool = True

    metadata: Dict = field(default_factory=dict)


@dataclass
class PinnedConnectionResult:
    """Result of pinned connection attempt"""
    success: bool
    proxy_host: str
    proxy_port: int
    pin_validation_passed: bool
    validation_result: Optional[PinningValidationResult] = None
    error_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    fallback_used: bool = False
    fallback_proxy: Optional[str] = None


class C2ProxyPinningConnector:
    """C2 Proxy connector with TLS pinning validation"""

    def __init__(
        self,
        pinning_manager: TLSPinningManager,
        config: C2ProxyConfig
    ):
        """
        Initialize C2 proxy connector with pinning

        Args:
            pinning_manager: TLSPinningManager instance
            config: C2ProxyConfig instance
        """
        self.pinning_manager = pinning_manager
        self.config = config
        self.lock = threading.Lock()
        self.connection_history: List[PinnedConnectionResult] = []

    def validate_and_connect(
        self,
        target_url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[bytes] = None,
        use_fallback: bool = True
    ) -> PinnedConnectionResult:
        """
        Validate proxy certificate and connect

        Args:
            target_url: Target URL to access through proxy
            method: HTTP method
            headers: Request headers
            data: Request body
            use_fallback: Whether to use fallback proxies on validation failure

        Returns:
            PinnedConnectionResult
        """
        logger.info(f"Attempting pinned connection to {self.config.proxy_host}:{self.config.proxy_port}")

        # Step 1: Validate proxy certificate
        if self.config.enable_pinning:
            validation_result = self.pinning_manager.validate_connection(
                host=self.config.proxy_host,
                port=self.config.proxy_port,
                timeout=self.config.connection_timeout
            )

            if not validation_result.is_valid:
                result = self._handle_validation_failure(
                    validation_result,
                    target_url,
                    use_fallback
                )
                with self.lock:
                    self.connection_history.append(result)
                return result
        else:
            validation_result = None

        # Step 2: Connect through proxy
        try:
            logger.info(f"Pin validation passed for {self.config.proxy_host}")
            # In real implementation, would make actual proxy connection
            # This is a demonstration of the validation workflow

            result = PinnedConnectionResult(
                success=True,
                proxy_host=self.config.proxy_host,
                proxy_port=self.config.proxy_port,
                pin_validation_passed=True,
                validation_result=validation_result
            )

            with self.lock:
                self.connection_history.append(result)

            logger.info(f"Successfully connected through pinned proxy")
            return result

        except Exception as e:
            result = PinnedConnectionResult(
                success=False,
                proxy_host=self.config.proxy_host,
                proxy_port=self.config.proxy_port,
                pin_validation_passed=True,
                validation_result=validation_result,
                error_message=f"Connection error: {str(e)}"
            )

            with self.lock:
                self.connection_history.append(result)

            logger.error(f"Connection error: {e}")
            return result

    def _handle_validation_failure(
        self,
        validation_result: PinningValidationResult,
        target_url: str,
        use_fallback: bool
    ) -> PinnedConnectionResult:
        """
        Handle certificate validation failure

        Args:
            validation_result: Validation result
            target_url: Target URL
            use_fallback: Whether to try fallback proxies

        Returns:
            PinnedConnectionResult
        """
        logger.warning(
            f"Pin validation failed for {self.config.proxy_host}: "
            f"{validation_result.error_message}"
        )

        if self.config.enable_audit and self.config.audit_on_failure:
            self._audit_validation_failure(validation_result)

        # Handle based on failover mode
        if self.config.failover_mode == FailoverMode.STRICT:
            return PinnedConnectionResult(
                success=False,
                proxy_host=self.config.proxy_host,
                proxy_port=self.config.proxy_port,
                pin_validation_passed=False,
                validation_result=validation_result,
                error_message=f"Pin validation failed (STRICT mode): {validation_result.error_message}"
            )

        elif self.config.failover_mode == FailoverMode.GRACEFUL:
            logger.warning("Allowing connection despite validation failure (GRACEFUL mode)")
            return PinnedConnectionResult(
                success=True,
                proxy_host=self.config.proxy_host,
                proxy_port=self.config.proxy_port,
                pin_validation_passed=False,
                validation_result=validation_result,
                error_message="Pin validation failed but connection allowed (GRACEFUL mode)"
            )

        elif self.config.failover_mode == FailoverMode.FALLBACK and use_fallback:
            return self._try_fallback_proxies(validation_result)

        elif self.config.failover_mode == FailoverMode.ALERT:
            logger.critical(f"Pin validation failed - operator intervention required")
            return PinnedConnectionResult(
                success=False,
                proxy_host=self.config.proxy_host,
                proxy_port=self.config.proxy_port,
                pin_validation_passed=False,
                validation_result=validation_result,
                error_message="Pin validation failed - ALERT mode: operator intervention required"
            )

        return PinnedConnectionResult(
            success=False,
            proxy_host=self.config.proxy_host,
            proxy_port=self.config.proxy_port,
            pin_validation_passed=False,
            validation_result=validation_result,
            error_message=f"Pin validation failed: {validation_result.error_message}"
        )

    def _try_fallback_proxies(
        self,
        original_validation_result: PinningValidationResult
    ) -> PinnedConnectionResult:
        """
        Try connecting through fallback proxies

        Args:
            original_validation_result: Original validation result

        Returns:
            PinnedConnectionResult
        """
        if not self.config.fallback_proxies:
            logger.error("No fallback proxies configured")
            return PinnedConnectionResult(
                success=False,
                proxy_host=self.config.proxy_host,
                proxy_port=self.config.proxy_port,
                pin_validation_passed=False,
                validation_result=original_validation_result,
                error_message="Pin validation failed and no fallback proxies available"
            )

        for fallback_proxy in self.config.fallback_proxies:
            logger.info(f"Trying fallback proxy: {fallback_proxy}")

            try:
                fallback_host, fallback_port = fallback_proxy.split(':')
                fallback_port = int(fallback_port)

                validation_result = self.pinning_manager.validate_connection(
                    host=fallback_host,
                    port=fallback_port,
                    timeout=self.config.connection_timeout
                )

                if validation_result.is_valid:
                    logger.info(f"Fallback proxy validation passed: {fallback_proxy}")
                    return PinnedConnectionResult(
                        success=True,
                        proxy_host=fallback_host,
                        proxy_port=fallback_port,
                        pin_validation_passed=True,
                        validation_result=validation_result,
                        fallback_used=True,
                        fallback_proxy=fallback_proxy
                    )
                else:
                    logger.warning(
                        f"Fallback proxy validation failed: {fallback_proxy} - "
                        f"{validation_result.error_message}"
                    )

            except Exception as e:
                logger.error(f"Error connecting to fallback proxy {fallback_proxy}: {e}")

        return PinnedConnectionResult(
            success=False,
            proxy_host=self.config.proxy_host,
            proxy_port=self.config.proxy_port,
            pin_validation_passed=False,
            validation_result=original_validation_result,
            error_message=f"All fallback proxies failed or unavailable"
        )

    def _audit_validation_failure(self, validation_result: PinningValidationResult):
        """Audit certificate validation failure"""
        logger.critical(
            f"SECURITY ALERT: Pin validation failed for {self.config.proxy_host} - "
            f"Possible MITM attack or certificate change"
        )

    def rotate_proxy_pins(self) -> Tuple[bool, str]:
        """
        Rotate pins for proxy certificate

        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Rotating pins for {self.config.proxy_host}")

        success, message = self.pinning_manager.rotate_pins(
            host=self.config.proxy_host,
            port=self.config.proxy_port,
            strategy=self.config.pinning_strategy,
            hash_algorithm=self.config.hash_algorithm,
            expiration_days=self.config.pin_expiration_days
        )

        if success:
            logger.info(f"Successfully rotated pins for {self.config.proxy_host}")
        else:
            logger.error(f"Failed to rotate pins: {message}")

        return success, message

    def get_connection_history(self) -> List[Dict]:
        """Get connection history"""
        with self.lock:
            return [
                {
                    'success': r.success,
                    'proxy_host': r.proxy_host,
                    'proxy_port': r.proxy_port,
                    'pin_validation_passed': r.pin_validation_passed,
                    'error_message': r.error_message,
                    'timestamp': r.timestamp,
                    'fallback_used': r.fallback_used,
                    'fallback_proxy': r.fallback_proxy
                }
                for r in self.connection_history
            ]

    def export_connection_log(self, output_file: Optional[str] = None) -> List[Dict]:
        """Export connection log"""
        log_data = self.get_connection_history()

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            logger.info(f"Exported connection log to {output_file}")

        return log_data

    def get_statistics(self) -> Dict:
        """Get connection statistics"""
        with self.lock:
            total = len(self.connection_history)
            successful = sum(1 for r in self.connection_history if r.success)
            pin_validated = sum(1 for r in self.connection_history if r.pin_validation_passed)
            fallback_used = sum(1 for r in self.connection_history if r.fallback_used)

        return {
            'total_attempts': total,
            'successful_attempts': successful,
            'failed_attempts': total - successful,
            'pin_validated_attempts': pin_validated,
            'fallback_used_attempts': fallback_used,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }


class C2ProxyFleet:
    """Manage multiple C2 proxies with pinning"""

    def __init__(self, pinning_manager: TLSPinningManager):
        """
        Initialize proxy fleet

        Args:
            pinning_manager: TLSPinningManager instance
        """
        self.pinning_manager = pinning_manager
        self.connectors: Dict[str, C2ProxyPinningConnector] = {}
        self.lock = threading.Lock()

    def add_proxy(
        self,
        proxy_id: str,
        config: C2ProxyConfig
    ) -> Tuple[bool, str]:
        """
        Add proxy to fleet with pinning

        Args:
            proxy_id: Unique proxy identifier
            config: C2ProxyConfig

        Returns:
            Tuple of (success, message)
        """
        with self.lock:
            if proxy_id in self.connectors:
                return False, f"Proxy {proxy_id} already exists"

            connector = C2ProxyPinningConnector(self.pinning_manager, config)
            self.connectors[proxy_id] = connector

        logger.info(f"Added proxy to fleet: {proxy_id} ({config.proxy_host}:{config.proxy_port})")
        return True, f"Proxy added: {proxy_id}"

    def initialize_proxy_pins(
        self,
        proxy_id: str,
        force: bool = False
    ) -> Tuple[bool, str]:
        """
        Initialize pins for a proxy

        Args:
            proxy_id: Proxy identifier
            force: Force re-pinning

        Returns:
            Tuple of (success, message)
        """
        with self.lock:
            if proxy_id not in self.connectors:
                return False, f"Proxy {proxy_id} not found"

            connector = self.connectors[proxy_id]
            config = connector.config

        # Check if pins already exist
        existing_pins = self.pinning_manager.get_pins(config.proxy_host)
        if existing_pins and not force:
            return True, f"Pins already exist for {config.proxy_host}"

        # Add pins from server
        success, message, pin_id = self.pinning_manager.add_pin_from_server(
            host=config.proxy_host,
            port=config.proxy_port,
            strategy=config.pinning_strategy,
            hash_algorithm=config.hash_algorithm,
            expiration_days=config.pin_expiration_days,
            timeout=config.connection_timeout,
            notes=f"C2 proxy: {proxy_id}"
        )

        return success, message

    def validate_fleet(self) -> Dict[str, bool]:
        """
        Validate all proxies in fleet

        Returns:
            Dictionary mapping proxy IDs to validation status
        """
        results = {}
        with self.lock:
            for proxy_id, connector in self.connectors.items():
                config = connector.config
                result = self.pinning_manager.validate_connection(
                    host=config.proxy_host,
                    port=config.proxy_port,
                    timeout=config.connection_timeout
                )
                results[proxy_id] = result.is_valid

        return results

    def get_proxy_status(self, proxy_id: str) -> Optional[Dict]:
        """Get status of specific proxy"""
        with self.lock:
            if proxy_id not in self.connectors:
                return None

            connector = self.connectors[proxy_id]
            config = connector.config

        stats = connector.get_statistics()
        pins = self.pinning_manager.get_pins(config.proxy_host)

        return {
            'proxy_id': proxy_id,
            'host': config.proxy_host,
            'port': config.proxy_port,
            'pinning_enabled': config.enable_pinning,
            'failover_mode': config.failover_mode.value,
            'statistics': stats,
            'pins_count': len(pins),
            'pins': pins
        }

    def get_fleet_status(self) -> Dict:
        """Get status of all proxies"""
        fleet_status = {}
        with self.lock:
            for proxy_id in self.connectors.keys():
                status = self.get_proxy_status(proxy_id)
                if status:
                    fleet_status[proxy_id] = status

        return fleet_status

    def rotate_all_pins(self) -> Dict[str, Tuple[bool, str]]:
        """Rotate pins for all proxies"""
        results = {}
        with self.lock:
            proxy_ids = list(self.connectors.keys())

        for proxy_id in proxy_ids:
            connector = self.connectors[proxy_id]
            success, message = connector.rotate_proxy_pins()
            results[proxy_id] = (success, message)

        return results

    def export_fleet_report(self, output_file: Optional[str] = None) -> Dict:
        """Export comprehensive fleet report"""
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'fleet_status': self.get_fleet_status(),
            'pinning_statistics': self.pinning_manager.get_statistics(),
            'audit_events': self.pinning_manager.audit_log[-100:]  # Last 100
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Exported fleet report to {output_file}")

        return report


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("C2 PROXY INTEGRATION WITH TLS PINNING")
    print("=" * 80)

    # Initialize pinning manager
    pinning_manager = TLSPinningManager()

    # Create proxy configuration
    proxy_config = C2ProxyConfig(
        proxy_host="c2.example.com",
        proxy_port=443,
        proxy_protocol="https",
        enable_pinning=True,
        pinning_strategy=PinningStrategy.PUBLIC_KEY,
        hash_algorithm=HashAlgorithm.SHA256,
        pin_expiration_days=365,
        failover_mode=FailoverMode.FALLBACK,
        fallback_proxies=["c2-backup.example.com:443"],
        enable_audit=True
    )

    # Initialize connector
    connector = C2ProxyPinningConnector(pinning_manager, proxy_config)

    print("\n1. C2 Proxy Configuration")
    print("-" * 80)
    print(f"  Primary Proxy: {proxy_config.proxy_host}:{proxy_config.proxy_port}")
    print(f"  Pinning Strategy: {proxy_config.pinning_strategy.value}")
    print(f"  Failover Mode: {proxy_config.failover_mode.value}")
    print(f"  Fallback Proxies: {len(proxy_config.fallback_proxies)}")

    print("\n2. Example Usage")
    print("-" * 80)
    print("""
    # Rotate proxy pins
    success, msg = connector.rotate_proxy_pins()

    # Validate and connect through proxy
    result = connector.validate_and_connect(
        target_url="https://api.example.com/data",
        method="GET"
    )

    # Get connection statistics
    stats = connector.get_statistics()

    # Export connection log
    connector.export_connection_log('/tmp/connection_log.json')
    """)

    print("\n3. Fleet Management Example")
    print("-" * 80)
    print("""
    # Create fleet manager
    fleet = C2ProxyFleet(pinning_manager)

    # Add proxies to fleet
    fleet.add_proxy("proxy_1", config1)
    fleet.add_proxy("proxy_2", config2)

    # Initialize pins for all proxies
    fleet.initialize_proxy_pins("proxy_1")

    # Validate entire fleet
    validation = fleet.validate_fleet()

    # Export fleet report
    fleet.export_fleet_report('/tmp/fleet_report.json')
    """)

    print("\n" + "=" * 80)
    print("C2 PROXY PINNING INTEGRATION READY")
    print("=" * 80)
