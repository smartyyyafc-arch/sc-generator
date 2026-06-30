#!/usr/bin/env python3
"""
Test Suite and Examples for TLS Certificate Pinning

Demonstrates usage patterns and validates pinning implementation.
For authorized pentesting and security research only.
"""

import sys
import json
import logging
from typing import List, Dict, Tuple

from tls_pinning_c2_proxy import (
    TLSPinningManager,
    PinningStrategy,
    HashAlgorithm,
    CertificateExtractor,
    PinHashGenerator,
    FingerprintComponent,
    PinData
)

from c2_proxy_pinning_integration import (
    C2ProxyConfig,
    C2ProxyPinningConnector,
    FailoverMode,
    C2ProxyFleet
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TLSPinningTestSuite:
    """Comprehensive test suite for TLS pinning"""

    def __init__(self, config_dir: str = '/tmp/sc-pins-test'):
        """Initialize test suite"""
        self.config_dir = config_dir
        self.manager = TLSPinningManager(config_dir=config_dir)
        self.test_results: List[Dict] = []

    def run_all_tests(self) -> Dict:
        """Run all tests and return results"""
        print("\n" + "=" * 80)
        print("TLS PINNING TEST SUITE")
        print("=" * 80)

        tests = [
            ("Manager Initialization", self.test_manager_initialization),
            ("Pin Data Structure", self.test_pin_data_structure),
            ("Pin Expiration", self.test_pin_expiration),
            ("Hash Generation", self.test_hash_generation),
            ("Pin Persistence", self.test_pin_persistence),
            ("Audit Logging", self.test_audit_logging),
            ("Statistics", self.test_statistics),
            ("C2 Proxy Config", self.test_c2_proxy_config),
            ("Failover Modes", self.test_failover_modes),
            ("Fleet Management", self.test_fleet_management),
        ]

        for test_name, test_func in tests:
            try:
                result = test_func()
                status = "PASS" if result else "FAIL"
                self.test_results.append({
                    'test_name': test_name,
                    'status': status,
                    'result': result
                })
                print(f"  [{status}] {test_name}")
            except Exception as e:
                self.test_results.append({
                    'test_name': test_name,
                    'status': 'ERROR',
                    'error': str(e)
                })
                print(f"  [ERROR] {test_name}: {e}")

        return self._summarize_results()

    def test_manager_initialization(self) -> bool:
        """Test manager initialization"""
        try:
            manager = TLSPinningManager(config_dir=self.config_dir)
            assert manager is not None
            assert manager.config_dir == self.config_dir
            assert isinstance(manager.pins, dict)
            assert isinstance(manager.audit_log, list)
            return True
        except Exception as e:
            logger.error(f"Manager initialization failed: {e}")
            return False

    def test_pin_data_structure(self) -> bool:
        """Test PinData structure and serialization"""
        try:
            pin = PinData(
                pin_id="test_pin_001",
                strategy=PinningStrategy.PUBLIC_KEY,
                pin_hash="abc123def456",
                hash_algorithm=HashAlgorithm.SHA256,
                subject_name="CN=test.example.com",
                issuer_name="CN=Test CA",
                backup_pins=["backup1", "backup2"]
            )

            # Test serialization
            pin_dict = pin.to_dict()
            assert pin_dict['pin_id'] == "test_pin_001"
            assert pin_dict['strategy'] == "public_key"
            assert pin_dict['hash_algorithm'] == "sha256"

            # Test deserialization
            restored_pin = PinData.from_dict(pin_dict)
            assert restored_pin.pin_id == pin.pin_id
            assert restored_pin.strategy == pin.strategy

            return True
        except Exception as e:
            logger.error(f"Pin data structure test failed: {e}")
            return False

    def test_pin_expiration(self) -> bool:
        """Test pin expiration logic"""
        try:
            from datetime import datetime, timedelta

            # Create non-expired pin
            pin1 = PinData(
                pin_id="pin_active",
                strategy=PinningStrategy.PUBLIC_KEY,
                pin_hash="hash1",
                hash_algorithm=HashAlgorithm.SHA256,
                expires_at=(datetime.utcnow() + timedelta(days=30)).isoformat()
            )
            assert not pin1.is_expired(), "Active pin should not be expired"

            # Create expired pin
            pin2 = PinData(
                pin_id="pin_expired",
                strategy=PinningStrategy.PUBLIC_KEY,
                pin_hash="hash2",
                hash_algorithm=HashAlgorithm.SHA256,
                expires_at=(datetime.utcnow() - timedelta(days=1)).isoformat()
            )
            assert pin2.is_expired(), "Expired pin should be detected"

            # Create indefinite pin
            pin3 = PinData(
                pin_id="pin_indefinite",
                strategy=PinningStrategy.PUBLIC_KEY,
                pin_hash="hash3",
                hash_algorithm=HashAlgorithm.SHA256,
                expires_at=None
            )
            assert not pin3.is_expired(), "Indefinite pin should not expire"

            return True
        except Exception as e:
            logger.error(f"Pin expiration test failed: {e}")
            return False

    def test_hash_generation(self) -> bool:
        """Test hash generation for pins"""
        try:
            test_data = b"test certificate data"

            # Test SHA-256
            hash_256 = PinHashGenerator.hash_data(test_data, HashAlgorithm.SHA256)
            assert len(hash_256) == 64, "SHA-256 should produce 64 hex chars"
            assert isinstance(hash_256, str), "Hash should be string"

            # Test SHA-384
            hash_384 = PinHashGenerator.hash_data(test_data, HashAlgorithm.SHA384)
            assert len(hash_384) == 96, "SHA-384 should produce 96 hex chars"

            # Test SHA-512
            hash_512 = PinHashGenerator.hash_data(test_data, HashAlgorithm.SHA512)
            assert len(hash_512) == 128, "SHA-512 should produce 128 hex chars"

            # Test consistency
            hash_256_again = PinHashGenerator.hash_data(test_data, HashAlgorithm.SHA256)
            assert hash_256 == hash_256_again, "Hashes should be consistent"

            return True
        except Exception as e:
            logger.error(f"Hash generation test failed: {e}")
            return False

    def test_pin_persistence(self) -> bool:
        """Test pin persistence to disk"""
        try:
            # Add test pin
            manager = TLSPinningManager(config_dir=self.config_dir)
            test_host = "test.example.com"

            pin = PinData(
                pin_id="persist_test",
                strategy=PinningStrategy.PUBLIC_KEY,
                pin_hash="persisthash123",
                hash_algorithm=HashAlgorithm.SHA256,
                subject_name="CN=test.example.com"
            )

            # Add to manager
            with manager.lock:
                manager.pins[test_host] = [pin]
            manager._save_pins()

            # Reload and verify
            manager2 = TLSPinningManager(config_dir=self.config_dir)
            assert test_host in manager2.pins, "Pin should persist"
            assert len(manager2.pins[test_host]) == 1, "Should have one pin"
            assert manager2.pins[test_host][0].pin_id == "persist_test", "Pin ID should match"

            return True
        except Exception as e:
            logger.error(f"Pin persistence test failed: {e}")
            return False

    def test_audit_logging(self) -> bool:
        """Test audit logging functionality"""
        try:
            manager = TLSPinningManager(config_dir=self.config_dir)
            initial_count = len(manager.audit_log)

            # Generate some audit events
            manager._audit_log('test_event', 'test.example.com', 'test_pin', 'Test details')

            assert len(manager.audit_log) > initial_count, "Audit log should grow"
            assert manager.audit_log[-1]['event_type'] == 'test_event', "Event type should match"

            # Test export
            audit_data = manager.export_audit_log()
            assert isinstance(audit_data, list), "Audit export should be list"

            return True
        except Exception as e:
            logger.error(f"Audit logging test failed: {e}")
            return False

    def test_statistics(self) -> bool:
        """Test statistics gathering"""
        try:
            manager = TLSPinningManager(config_dir=self.config_dir)

            # Add test pins
            for i in range(3):
                pin = PinData(
                    pin_id=f"stat_pin_{i}",
                    strategy=PinningStrategy.PUBLIC_KEY,
                    pin_hash=f"hash_{i}",
                    hash_algorithm=HashAlgorithm.SHA256
                )
                host = f"host{i}.example.com"
                with manager.lock:
                    manager.pins[host] = [pin]

            # Get statistics
            stats = manager.get_statistics()
            assert 'total_hosts' in stats, "Stats should have total_hosts"
            assert 'total_pins' in stats, "Stats should have total_pins"
            assert 'active_pins' in stats, "Stats should have active_pins"
            assert stats['total_hosts'] > 0, "Should have hosts"

            return True
        except Exception as e:
            logger.error(f"Statistics test failed: {e}")
            return False

    def test_c2_proxy_config(self) -> bool:
        """Test C2 proxy configuration"""
        try:
            config = C2ProxyConfig(
                proxy_host="c2.example.com",
                proxy_port=443,
                proxy_protocol="https",
                enable_pinning=True,
                pinning_strategy=PinningStrategy.PUBLIC_KEY,
                hash_algorithm=HashAlgorithm.SHA256,
                failover_mode=FailoverMode.FALLBACK,
                fallback_proxies=["backup.example.com:443"],
                connection_timeout=10.0
            )

            assert config.proxy_host == "c2.example.com"
            assert config.proxy_port == 443
            assert config.enable_pinning is True
            assert config.failover_mode == FailoverMode.FALLBACK
            assert len(config.fallback_proxies) == 1

            return True
        except Exception as e:
            logger.error(f"C2 proxy config test failed: {e}")
            return False

    def test_failover_modes(self) -> bool:
        """Test failover mode configurations"""
        try:
            modes = [
                FailoverMode.STRICT,
                FailoverMode.GRACEFUL,
                FailoverMode.FALLBACK,
                FailoverMode.ALERT
            ]

            for mode in modes:
                config = C2ProxyConfig(
                    proxy_host="test.example.com",
                    proxy_port=443,
                    failover_mode=mode
                )
                assert config.failover_mode == mode, f"Mode {mode} should be set"

            return True
        except Exception as e:
            logger.error(f"Failover modes test failed: {e}")
            return False

    def test_fleet_management(self) -> bool:
        """Test fleet management"""
        try:
            manager = TLSPinningManager(config_dir=self.config_dir)
            fleet = C2ProxyFleet(manager)

            # Add proxies
            config1 = C2ProxyConfig(
                proxy_host="proxy1.example.com",
                proxy_port=443
            )
            config2 = C2ProxyConfig(
                proxy_host="proxy2.example.com",
                proxy_port=443
            )

            success1, _ = fleet.add_proxy("proxy_1", config1)
            success2, _ = fleet.add_proxy("proxy_2", config2)

            assert success1 and success2, "Proxies should be added"
            assert len(fleet.connectors) == 2, "Should have 2 proxies"

            # Test duplicate prevention
            success3, msg = fleet.add_proxy("proxy_1", config1)
            assert not success3, "Duplicate should be rejected"

            return True
        except Exception as e:
            logger.error(f"Fleet management test failed: {e}")
            return False

    def _summarize_results(self) -> Dict:
        """Summarize test results"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        errors = sum(1 for r in self.test_results if r['status'] == 'ERROR')

        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print("=" * 80 + "\n")

        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'success_rate': (passed/total*100) if total > 0 else 0,
            'results': self.test_results
        }


class TLSPinningExamples:
    """Example usage patterns for TLS pinning"""

    @staticmethod
    def example_basic_pinning():
        """Example: Basic certificate pinning"""
        print("\n" + "=" * 80)
        print("EXAMPLE 1: Basic Certificate Pinning")
        print("=" * 80)

        print("""
from tls_pinning_c2_proxy import TLSPinningManager, PinningStrategy, HashAlgorithm

# Initialize manager
manager = TLSPinningManager()

# Add pin from remote server
success, msg, pin_id = manager.add_pin_from_server(
    host='c2.example.com',
    port=443,
    strategy=PinningStrategy.PUBLIC_KEY,
    hash_algorithm=HashAlgorithm.SHA256,
    expiration_days=365,
    notes='C2 primary handler'
)

if success:
    print(f'Pin created: {pin_id}')

    # Validate connection
    result = manager.validate_connection('c2.example.com', 443)
    print(f'Valid: {result.is_valid}')
else:
    print(f'Error: {msg}')
        """)

    @staticmethod
    def example_c2_proxy_integration():
        """Example: C2 proxy with pinning"""
        print("\n" + "=" * 80)
        print("EXAMPLE 2: C2 Proxy Integration with Pinning")
        print("=" * 80)

        print("""
from tls_pinning_c2_proxy import TLSPinningManager, PinningStrategy
from c2_proxy_pinning_integration import (
    C2ProxyConfig,
    C2ProxyPinningConnector,
    FailoverMode
)

# Setup
manager = TLSPinningManager()
config = C2ProxyConfig(
    proxy_host='c2.example.com',
    proxy_port=443,
    enable_pinning=True,
    pinning_strategy=PinningStrategy.PUBLIC_KEY,
    failover_mode=FailoverMode.FALLBACK,
    fallback_proxies=['backup.example.com:443']
)

# Create connector
connector = C2ProxyPinningConnector(manager, config)

# Initialize pins
success, msg = manager.add_pin_from_server('c2.example.com', 443)

# Connect through proxy
result = connector.validate_and_connect(
    target_url='https://command.example.com/beacon',
    method='POST',
    data=b'{...beacon data...}'
)

if result.success:
    print('Connected through pinned proxy')
else:
    print(f'Connection failed: {result.error_message}')
        """)

    @staticmethod
    def example_fleet_management():
        """Example: Multi-proxy fleet management"""
        print("\n" + "=" * 80)
        print("EXAMPLE 3: Multi-Proxy Fleet Management")
        print("=" * 80)

        print("""
from c2_proxy_pinning_integration import C2ProxyFleet, C2ProxyConfig
from tls_pinning_c2_proxy import TLSPinningManager

# Initialize
manager = TLSPinningManager()
fleet = C2ProxyFleet(manager)

# Define proxies
proxies = [
    ('primary', C2ProxyConfig(proxy_host='c2-1.example.com', proxy_port=443)),
    ('secondary', C2ProxyConfig(proxy_host='c2-2.example.com', proxy_port=443)),
    ('backup', C2ProxyConfig(proxy_host='c2-3.example.com', proxy_port=443)),
]

# Add to fleet
for proxy_id, config in proxies:
    fleet.add_proxy(proxy_id, config)
    fleet.initialize_proxy_pins(proxy_id)

# Validate entire fleet
validation = fleet.validate_fleet()
for proxy_id, is_valid in validation.items():
    print(f'{proxy_id}: {"Valid" if is_valid else "Invalid"}')

# Export report
fleet.export_fleet_report('/tmp/fleet_report.json')
        """)

    @staticmethod
    def example_pin_rotation():
        """Example: Pin rotation workflow"""
        print("\n" + "=" * 80)
        print("EXAMPLE 4: Pin Rotation Workflow")
        print("=" * 80)

        print("""
from tls_pinning_c2_proxy import TLSPinningManager

manager = TLSPinningManager()

# Initial pin
success, msg, pin_id = manager.add_pin_from_server(
    host='c2.example.com',
    port=443,
    expiration_days=365
)
print(f'Initial pin: {pin_id}')

# ... 360 days later, certificate still valid ...

# Rotate pins
success, msg = manager.rotate_pins(
    host='c2.example.com',
    port=443,
    expiration_days=365
)
print(f'Rotation: {msg}')

# Verify rotation
pins = manager.get_pins('c2.example.com')
print(f'Total pins after rotation: {len(pins)}')
        """)

    @staticmethod
    def example_error_handling():
        """Example: Error handling and fallback"""
        print("\n" + "=" * 80)
        print("EXAMPLE 5: Error Handling and Fallback")
        print("=" * 80)

        print("""
from c2_proxy_pinning_integration import (
    C2ProxyPinningConnector,
    C2ProxyConfig,
    FailoverMode
)
from tls_pinning_c2_proxy import TLSPinningManager

manager = TLSPinningManager()

# Config with fallback
config = C2ProxyConfig(
    proxy_host='primary.example.com',
    proxy_port=443,
    failover_mode=FailoverMode.FALLBACK,
    fallback_proxies=[
        'secondary.example.com:443',
        'tertiary.example.com:443'
    ]
)

connector = C2ProxyPinningConnector(manager, config)

try:
    result = connector.validate_and_connect(
        target_url='https://cmd.example.com/tasks',
        method='GET',
        use_fallback=True
    )

    if result.success:
        if result.fallback_used:
            print(f'Using fallback: {result.fallback_proxy}')
        else:
            print('Using primary proxy')
    else:
        print(f'All proxies failed: {result.error_message}')

except Exception as e:
    print(f'Critical error: {e}')
        """)

    @staticmethod
    def run_all_examples():
        """Run all examples"""
        print("\n" + "=" * 80)
        print("TLS PINNING IMPLEMENTATION EXAMPLES")
        print("=" * 80)

        TLSPinningExamples.example_basic_pinning()
        TLSPinningExamples.example_c2_proxy_integration()
        TLSPinningExamples.example_fleet_management()
        TLSPinningExamples.example_pin_rotation()
        TLSPinningExamples.example_error_handling()

        print("\n" + "=" * 80)
        print("END OF EXAMPLES")
        print("=" * 80 + "\n")


def main():
    """Main test execution"""
    print("\n" + "=" * 80)
    print("TLS CERTIFICATE PINNING - TEST AND EXAMPLES")
    print("=" * 80)

    # Run test suite
    test_suite = TLSPinningTestSuite()
    results = test_suite.run_all_tests()

    # Run examples
    TLSPinningExamples.run_all_examples()

    # Summary
    print("\n" + "=" * 80)
    print("TEST AND EXAMPLES COMPLETE")
    print("=" * 80)
    print(f"Test Success Rate: {results['success_rate']:.1f}%")
    print("=" * 80 + "\n")

    return 0 if results['success_rate'] == 100 else 1


if __name__ == "__main__":
    sys.exit(main())
