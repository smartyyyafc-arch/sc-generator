#!/usr/bin/env python3
"""
Test suite for proxy chain configuration and execution

Tests:
- Chain building
- Configuration validation
- Hop management
- Metrics tracking
- Configuration import/export
"""

import json
import sys
from pathlib import Path

from proxy_chain_builder import (
    ProxyChainBuilder, ProxyChainConfig, ProxyHopConfig,
    ProxyChain, ProxyProtocol, AuthType, ChainState, HopState
)
from proxy_chain_executor import (
    ProxyChainExecutor, ExecutionMode, HopExecutionStatus
)


class TestProxyChain:
    """Test proxy chain functionality"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def test(self, name: str):
        """Decorator for test methods"""
        def decorator(func):
            self.tests.append((name, func))
            return func
        return decorator

    def run_all(self):
        """Run all tests"""
        print("=" * 80)
        print("PROXY CHAIN TEST SUITE")
        print("=" * 80)

        for test_name, test_func in self.tests:
            try:
                print(f"\n▶ {test_name}")
                print("-" * 80)
                test_func(self)
                self.passed += 1
                print(f"✓ PASSED")
            except AssertionError as e:
                self.failed += 1
                print(f"✗ FAILED: {e}")
            except Exception as e:
                self.failed += 1
                print(f"✗ ERROR: {e}")

        print("\n" + "=" * 80)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("=" * 80)

        return self.failed == 0

    def assert_equal(self, actual, expected, message=""):
        """Assert equality"""
        if actual != expected:
            raise AssertionError(
                f"{message}\nExpected: {expected}\nActual: {actual}"
            )

    def assert_true(self, condition, message=""):
        """Assert true"""
        if not condition:
            raise AssertionError(f"Expected True: {message}")

    def assert_false(self, condition, message=""):
        """Assert false"""
        if condition:
            raise AssertionError(f"Expected False: {message}")

    def assert_greater_than(self, actual, expected, message=""):
        """Assert greater than"""
        if actual <= expected:
            raise AssertionError(f"{message}\n{actual} <= {expected}")

    def assert_in(self, item, container, message=""):
        """Assert item in container"""
        if item not in container:
            raise AssertionError(f"{message}\n{item} not in {container}")


# Initialize test suite
tests = TestProxyChain()


@tests.test("1. Create Simple 2-Hop Chain")
def test_simple_chain(self):
    """Test creating a simple 2-hop chain"""
    builder = ProxyChainBuilder("simple-chain")
    builder.add_hop("proxy1.example.com", 8080)
    builder.add_hop("proxy2.example.com", 3128)

    chain = builder.build()

    self.assert_equal(len(chain.get_all_hops()), 2, "Should have 2 hops")
    self.assert_equal(chain.config.chain_name, "simple-chain", "Chain name mismatch")
    self.assert_true(chain.config.validate()[0], "Chain should be valid")


@tests.test("2. Chain with Authentication")
def test_chain_with_auth(self):
    """Test chain with different authentication types"""
    builder = ProxyChainBuilder("auth-chain")

    # Basic auth
    builder.add_hop(
        "proxy1.example.com", 8080,
        auth_type="basic",
        username="user1",
        password="pass1"
    )

    # No auth
    builder.add_hop("proxy2.example.com", 3128)

    chain = builder.build()

    hops = chain.get_all_hops()
    self.assert_equal(hops[0].auth_type, AuthType.BASIC, "First hop should be BASIC auth")
    self.assert_equal(hops[1].auth_type, AuthType.NONE, "Second hop should have no auth")


@tests.test("3. Protocol Specification")
def test_protocol_specification(self):
    """Test different protocol specifications"""
    builder = ProxyChainBuilder("protocol-chain")
    builder.add_hop("proxy1.example.com", 8080, protocol="http")
    builder.add_hop("proxy2.example.com", 1080, protocol="socks5")
    builder.add_hop("proxy3.example.com", 8443, protocol="https")

    chain = builder.build()
    hops = chain.get_all_hops()

    protocols = [hop.protocol for hop in hops]
    self.assert_in(ProxyProtocol.HTTP, protocols, "Should have HTTP protocol")
    self.assert_in(ProxyProtocol.SOCKS5, protocols, "Should have SOCKS5 protocol")
    self.assert_in(ProxyProtocol.HTTPS, protocols, "Should have HTTPS protocol")


@tests.test("4. Configuration Validation")
def test_configuration_validation(self):
    """Test configuration validation"""
    # Valid configuration
    builder = ProxyChainBuilder("valid-chain")
    builder.add_hop("proxy.example.com", 8080)
    chain = builder.build()

    is_valid, errors = chain.validate()
    self.assert_true(is_valid, "Valid chain should pass validation")
    self.assert_equal(len(errors), 0, "Valid chain should have no errors")

    # Invalid configuration (no hops)
    try:
        empty_builder = ProxyChainBuilder("empty-chain")
        empty_chain = empty_builder.build()
        self.assert_false(True, "Empty chain should raise error")
    except ValueError:
        pass  # Expected


@tests.test("5. Circular Dependency Detection")
def test_circular_dependency(self):
    """Test detection of circular dependencies"""
    config = ProxyChainConfig(
        chain_name="circular-chain",
        hops=[
            ProxyHopConfig(hostname="proxy1.example.com", port=8080),
            ProxyHopConfig(hostname="proxy2.example.com", port=3128),
            ProxyHopConfig(hostname="proxy1.example.com", port=8080),  # Duplicate
        ],
        circular_hop_detection=True
    )

    is_valid, errors = config.validate()
    self.assert_false(is_valid, "Chain with duplicate hops should be invalid")
    self.assert_greater_than(len(errors), 0, "Should have error message for duplicates")


@tests.test("6. Proxy URL Generation")
def test_proxy_url_generation(self):
    """Test proxy URL generation"""
    hop = ProxyHopConfig(
        hostname="proxy.example.com",
        port=8080,
        protocol=ProxyProtocol.HTTP,
        auth_type=AuthType.BASIC,
        username="user",
        password="pass"
    )

    url = hop.get_proxy_url()
    self.assert_equal(url, "http://proxy.example.com:8080", "URL generation mismatch")

    # URL with auth (should mask password)
    url_with_auth = hop.get_proxy_url_with_auth()
    self.assert_true("***" in url_with_auth, "Password should be masked")


@tests.test("7. Hop Configuration Export/Import")
def test_hop_config_export(self):
    """Test exporting and importing hop configuration"""
    original = ProxyHopConfig(
        hostname="proxy.example.com",
        port=8080,
        auth_type=AuthType.BASIC,
        username="user",
        password="pass",
        label="Test Hop"
    )

    config_dict = original.to_dict()
    self.assert_equal(config_dict["hostname"], "proxy.example.com", "Hostname mismatch")
    self.assert_equal(config_dict["port"], 8080, "Port mismatch")
    self.assert_equal(config_dict["auth_type"], "basic", "Auth type mismatch")


@tests.test("8. Chain Configuration Export/Import")
def test_chain_config_export(self):
    """Test exporting and importing chain configuration"""
    builder = ProxyChainBuilder("export-test")
    builder.add_hop("proxy1.example.com", 8080, label="Hop 1")
    builder.add_hop("proxy2.example.com", 3128, label="Hop 2")
    builder.set_total_timeout(60)

    chain = builder.build()
    config = chain.config

    # Export to JSON
    json_str = config.to_json()
    config_dict = json.loads(json_str)

    self.assert_equal(config_dict["chain_name"], "export-test", "Chain name mismatch")
    self.assert_equal(len(config_dict["hops"]), 2, "Should have 2 hops")
    self.assert_equal(config_dict["total_timeout"], 60, "Timeout mismatch")

    # Import from JSON
    reimported = ProxyChainConfig.from_json(json_str)
    self.assert_equal(reimported.chain_name, "export-test", "Reimport chain name mismatch")
    self.assert_equal(len(reimported.hops), 2, "Reimport should have 2 hops")


@tests.test("9. Chain Health Tracking")
def test_chain_health(self):
    """Test chain health status tracking"""
    builder = ProxyChainBuilder("health-chain")
    builder.add_hop("proxy1.example.com", 8080)
    builder.add_hop("proxy2.example.com", 3128)

    chain = builder.build()

    # Record some activity
    chain.record_hop_success(0, response_time=0.5)
    chain.record_hop_success(1, response_time=0.3)
    chain.record_hop_success(0, response_time=0.45)
    chain.record_hop_failure(1)

    # Check metrics
    metrics_0 = chain.get_hop_metrics(0)
    self.assert_equal(metrics_0.total_requests, 2, "Hop 0 should have 2 requests")
    self.assert_equal(metrics_0.successful_requests, 2, "Hop 0 should have 2 successes")

    metrics_1 = chain.get_hop_metrics(1)
    self.assert_equal(metrics_1.total_requests, 2, "Hop 1 should have 2 requests")
    self.assert_equal(metrics_1.failed_requests, 1, "Hop 1 should have 1 failure")

    # Check health status
    health = chain.get_chain_health()
    self.assert_equal(health["total_hops"], 2, "Should report 2 hops")
    self.assert_equal(health["enabled_hops"], 2, "Should report 2 enabled hops")


@tests.test("10. Hop Metrics Calculation")
def test_hop_metrics(self):
    """Test hop metrics calculations"""
    from proxy_chain_builder import HopMetrics

    metrics = HopMetrics(
        hop_index=0,
        proxy_address="proxy.example.com:8080",
        total_requests=10,
        successful_requests=8,
        total_response_time=2.5
    )

    success_rate = metrics.get_success_rate()
    self.assert_equal(success_rate, 80.0, "Success rate should be 80%")

    avg_time = metrics.get_average_response_time()
    self.assert_equal(avg_time, 0.25, "Avg response time should be 0.25s")


@tests.test("11. Enabled/Disabled Hops")
def test_enabled_hops(self):
    """Test filtering of enabled/disabled hops"""
    builder = ProxyChainBuilder("enabled-test")
    builder.add_hop("proxy1.example.com", 8080)
    builder.add_hop("proxy2.example.com", 3128)
    builder.add_hop("proxy3.example.com", 8443)

    chain = builder.build()

    # Disable middle hop
    chain.config.hops[1].enabled = False

    enabled = chain.get_enabled_hops()
    self.assert_equal(len(enabled), 2, "Should have 2 enabled hops")

    # Check indices
    indices = [idx for idx, hop in enabled]
    self.assert_in(0, indices, "Should include hop 0")
    self.assert_in(2, indices, "Should include hop 2")


@tests.test("12. Chain ID Generation")
def test_chain_id(self):
    """Test unique chain ID generation"""
    builder1 = ProxyChainBuilder("chain-1")
    builder1.add_hop("proxy.example.com", 8080)
    chain1 = builder1.build()

    builder2 = ProxyChainBuilder("chain-2")
    builder2.add_hop("proxy.example.com", 8080)
    chain2 = builder2.build()

    id1 = chain1.get_chain_id()
    id2 = chain2.get_chain_id()

    self.assert_equal(len(id1), 16, "Chain ID should be 16 chars")
    self.assert_true(id1 != id2, "Different chains should have different IDs")


@tests.test("13. Builder Method Chaining")
def test_builder_chaining(self):
    """Test fluent builder API"""
    chain = (ProxyChainBuilder("chained")
             .add_hop("proxy1.example.com", 8080)
             .add_hop("proxy2.example.com", 3128)
             .set_total_timeout(60)
             .enable_metrics(True)
             .set_description("Chained configuration")
             .build())

    self.assert_equal(chain.config.chain_name, "chained", "Chain name mismatch")
    self.assert_equal(len(chain.get_all_hops()), 2, "Should have 2 hops")
    self.assert_equal(chain.config.total_timeout, 60, "Timeout not set")
    self.assert_true(chain.config.enable_metrics, "Metrics not enabled")


@tests.test("14. Executor Creation")
def test_executor_creation(self):
    """Test creating executor for chain"""
    builder = ProxyChainBuilder("exec-chain")
    builder.add_hop("proxy1.example.com", 8080)
    builder.add_hop("proxy2.example.com", 3128)

    chain = builder.build()
    executor = ProxyChainExecutor(chain, ExecutionMode.SEQUENTIAL)

    self.assert_equal(executor.execution_mode, ExecutionMode.SEQUENTIAL, "Mode mismatch")

    stats = executor.get_executor_stats()
    self.assert_equal(stats["total_requests"], 0, "Should have no requests yet")
    self.assert_equal(stats["success_rate"], 0, "Success rate should be 0")


@tests.test("15. Chain State Management")
def test_chain_state(self):
    """Test chain state management"""
    builder = ProxyChainBuilder("state-chain")
    builder.add_hop("proxy1.example.com", 8080)

    chain = builder.build()

    # State should be validated after build (if validate_chain_on_init is True)
    state = chain.get_chain_state()
    self.assert_equal(state, ChainState.VALIDATED, "State should be VALIDATED after build")

    # Update state
    chain.update_chain_state(ChainState.ACTIVE)
    state = chain.get_chain_state()
    self.assert_equal(state, ChainState.ACTIVE, "State not updated")


@tests.test("16. Hop State Tracking")
def test_hop_states(self):
    """Test individual hop state tracking"""
    builder = ProxyChainBuilder("hop-state-chain")
    builder.add_hop("proxy1.example.com", 8080)
    builder.add_hop("proxy2.example.com", 3128)

    chain = builder.build()

    # Check initial states
    state_0 = chain.get_hop_state(0)
    self.assert_equal(state_0, HopState.HEALTHY, "Initial hop state should be HEALTHY")

    # Record failures to change state
    for _ in range(5):
        chain.record_hop_failure(1)

    state_1 = chain.get_hop_state(1)
    self.assert_equal(state_1, HopState.UNHEALTHY, "Hop should be UNHEALTHY after failures")


@tests.test("17. Invalid Port Number")
def test_invalid_port(self):
    """Test validation of invalid port numbers"""
    try:
        hop = ProxyHopConfig(hostname="proxy.example.com", port=99999)
        self.assert_false(True, "Should reject invalid port")
    except ValueError:
        pass  # Expected


@tests.test("18. Missing Required Fields")
def test_missing_fields(self):
    """Test validation of missing required fields"""
    try:
        hop = ProxyHopConfig(hostname="", port=8080)
        self.assert_false(True, "Should reject missing hostname")
    except ValueError:
        pass  # Expected


@tests.test("19. Chain Max Hop Limit")
def test_max_hop_limit(self):
    """Test enforcement of maximum hop limit"""
    config = ProxyChainConfig(
        chain_name="too-many-hops",
        max_chain_hops=2,
        hops=[
            ProxyHopConfig(hostname="proxy1.example.com", port=8080),
            ProxyHopConfig(hostname="proxy2.example.com", port=3128),
            ProxyHopConfig(hostname="proxy3.example.com", port=8443),
        ]
    )

    is_valid, errors = config.validate()
    self.assert_false(is_valid, "Should reject chain exceeding max hops")


@tests.test("20. Configuration File Operations")
def test_config_file_operations(self):
    """Test saving and loading configuration files"""
    builder = ProxyChainBuilder("file-test")
    builder.add_hop("proxy1.example.com", 8080, label="Hop 1")
    builder.add_hop("proxy2.example.com", 3128, label="Hop 2")

    chain = builder.build()

    # Export to JSON
    json_str = chain.config.to_json()
    config_dict = json.loads(json_str)

    # Verify structure
    self.assert_in("chain_name", config_dict, "Should have chain_name")
    self.assert_in("hops", config_dict, "Should have hops")
    self.assert_greater_than(len(config_dict["hops"]), 0, "Should have hops")


if __name__ == "__main__":
    success = tests.run_all()
    sys.exit(0 if success else 1)
