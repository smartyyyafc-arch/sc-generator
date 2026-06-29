#!/usr/bin/env python3
"""
Test Suite for Polymorphic Command Obfuscation Wrapper
Validates functionality, encoding correctness, and polymorphism
"""

import sys
import base64
import subprocess
import tempfile
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from polymorphic_wrapper import (
    PolymorphicCommandEncoder,
    PolymorphicConfig,
    PolymorphicStrategy,
    create_polymorphic_wrapper,
)


class PolymorphicWrapperTestSuite:
    """Comprehensive test suite for polymorphic obfuscation"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_commands = [
            "echo 'Hello World'",
            "ls -la /tmp",
            "python3 --version",
            "powershell.exe -NoProfile -Command Write-Host 'Test'",
            "calc.exe",
        ]

    def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 80)
        print("POLYMORPHIC WRAPPER TEST SUITE")
        print("=" * 80)

        self.test_encoding_methods()
        self.test_decoding_correctness()
        self.test_polymorphism()
        self.test_wrapper_generation()
        self.test_statistics()
        self.test_multiple_iterations()
        self.test_all_strategies()

        print("\n" + "=" * 80)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("=" * 80)

        return self.failed == 0

    def test_encoding_methods(self):
        """Test individual encoding methods"""
        print("\n[TEST] Individual Encoding Methods")
        print("-" * 80)

        encoder = PolymorphicCommandEncoder()
        command = "test_command"

        for strategy in PolymorphicStrategy:
            try:
                config = PolymorphicConfig(strategies=[strategy])
                test_encoder = PolymorphicCommandEncoder(config)
                payload = test_encoder.encode(command)

                assert payload["strategy"] == strategy.value, f"Strategy mismatch: {strategy.value}"
                assert "encoded_data" in payload, "Missing encoded_data"
                assert "decoder_code" in payload, "Missing decoder_code"

                print(f"✓ {strategy.value}: OK")
                self.passed += 1

            except Exception as e:
                print(f"✗ {strategy.value}: {e}")
                self.failed += 1

    def test_decoding_correctness(self):
        """Test that encoded commands can be decoded correctly"""
        print("\n[TEST] Decoding Correctness")
        print("-" * 80)

        encoder = PolymorphicCommandEncoder()

        for command in self.test_commands[:3]:  # Test first 3 commands
            try:
                payload = encoder.encode(command)
                strategy = payload["strategy"]

                # Create decoder function
                decoder_code = payload["decoder_code"]
                decoder_name = payload["decoder_name"]

                # Execute decoder in isolated namespace
                namespace = {}
                exec(decoder_code, namespace)
                decoded_command = namespace[decoder_name]()

                assert decoded_command == command, f"Mismatch: {command} != {decoded_command}"
                print(f"✓ {strategy}: '{command[:30]}...' -> Decoded correctly")
                self.passed += 1

            except Exception as e:
                print(f"✗ Decoding failed for '{command}': {e}")
                self.failed += 1

    def test_polymorphism(self):
        """Test that polymorphism generates different encodings"""
        print("\n[TEST] Polymorphism (Different Encodings Per Invocation)")
        print("-" * 80)

        encoder = PolymorphicCommandEncoder()
        command = "polymorphic_test"

        strategies_used = set()

        for i in range(20):
            payload = encoder.encode(command)
            strategies_used.add(payload["strategy"])

        # Should use multiple different strategies
        unique_count = len(strategies_used)
        print(f"✓ Generated {unique_count} different strategies in 20 invocations")
        print(f"  Strategies used: {strategies_used}")

        if unique_count >= 3:  # Expect at least 3 different strategies
            print("✓ Polymorphism working correctly")
            self.passed += 1
        else:
            print("✗ Insufficient polymorphism")
            self.failed += 1

    def test_wrapper_generation(self):
        """Test wrapper generation for all output formats"""
        print("\n[TEST] Wrapper Generation")
        print("-" * 80)

        formats = ["python", "vbs", "powershell", "bash"]
        command = "test_wrapper_generation"

        for fmt in formats:
            try:
                result = create_polymorphic_wrapper(command, output_format=fmt, iterations=2)

                assert "wrapper" in result, f"Missing wrapper for {fmt}"
                assert "statistics" in result, f"Missing statistics for {fmt}"
                assert len(result["wrapper"]) > 0, f"Empty wrapper for {fmt}"
                assert result["iterations"] == 2, f"Iteration mismatch for {fmt}"

                print(f"✓ {fmt.upper()}: Generated wrapper ({len(result['wrapper'])} bytes)")
                self.passed += 1

            except Exception as e:
                print(f"✗ {fmt.upper()}: {e}")
                self.failed += 1

    def test_statistics(self):
        """Test statistics tracking"""
        print("\n[TEST] Statistics Tracking")
        print("-" * 80)

        try:
            encoder = PolymorphicCommandEncoder()
            command = "statistics_test"

            # Generate 15 encodings
            for _ in range(15):
                encoder.encode(command)

            stats = encoder.get_statistics()

            assert "total_invocations" in stats, "Missing total_invocations"
            assert "strategy_distribution" in stats, "Missing strategy_distribution"
            assert "unique_strategies_used" in stats, "Missing unique_strategies_used"
            assert stats["total_invocations"] == 15, f"Invocation count mismatch: {stats['total_invocations']}"

            print(f"✓ Total invocations: {stats['total_invocations']}")
            print(f"✓ Unique strategies: {stats['unique_strategies_used']}")
            print(f"✓ Distribution: {stats['strategy_distribution']}")
            self.passed += 1

        except Exception as e:
            print(f"✗ Statistics tracking failed: {e}")
            self.failed += 1

    def test_multiple_iterations(self):
        """Test wrapper generation with multiple iterations"""
        print("\n[TEST] Multiple Iterations")
        print("-" * 80)

        command = "multi_iteration_test"
        iterations_list = [1, 3, 5, 10]

        for iterations in iterations_list:
            try:
                result = create_polymorphic_wrapper(command, output_format="python", iterations=iterations)

                # Count number of decoders in wrapper
                wrapper = result["wrapper"]
                decoder_count = wrapper.count("def _decode_")

                assert decoder_count >= iterations, f"Expected {iterations} decoders, got {decoder_count}"
                print(f"✓ {iterations} iterations: Generated {decoder_count} decoders")
                self.passed += 1

            except Exception as e:
                print(f"✗ {iterations} iterations failed: {e}")
                self.failed += 1

    def test_all_strategies(self):
        """Test all encoding strategies work end-to-end"""
        print("\n[TEST] All Strategies (End-to-End)")
        print("-" * 80)

        command = "strategy_test_command"
        strategies_tested = 0

        for strategy in PolymorphicStrategy:
            try:
                config = PolymorphicConfig(strategies=[strategy])
                encoder = PolymorphicCommandEncoder(config)
                payload = encoder.encode(command)

                # Decode
                namespace = {}
                exec(payload["decoder_code"], namespace)
                decoder_func = namespace[payload["decoder_name"]]
                decoded = decoder_func()

                assert decoded == command, f"Decode mismatch for {strategy.value}"

                print(f"✓ {strategy.value:20s}: Encoded -> Decoded successfully")
                strategies_tested += 1
                self.passed += 1

            except Exception as e:
                print(f"✗ {strategy.value:20s}: {e}")
                self.failed += 1

        print(f"\n✓ All {strategies_tested} strategies tested successfully")


def benchmark_polymorphic_encoder():
    """Benchmark polymorphic encoder performance"""
    print("\n" + "=" * 80)
    print("PERFORMANCE BENCHMARK")
    print("=" * 80)

    import time

    encoder = PolymorphicCommandEncoder()
    command = "benchmark_" * 10  # ~100 chars

    iterations = 100
    start = time.time()

    for _ in range(iterations):
        encoder.encode(command)

    elapsed = time.time() - start
    avg_time = (elapsed / iterations) * 1000  # Convert to ms

    print(f"\nEncoding performance (command length: {len(command)} chars)")
    print(f"Total iterations: {iterations}")
    print(f"Total time: {elapsed:.3f}s")
    print(f"Average time per encoding: {avg_time:.3f}ms")


def demonstrate_polymorphic_behavior():
    """Demonstrate polymorphic behavior with same command"""
    print("\n" + "=" * 80)
    print("POLYMORPHIC BEHAVIOR DEMONSTRATION")
    print("=" * 80)

    command = "echo 'Polymorphic Demo'"
    encoder = PolymorphicCommandEncoder()

    print(f"\nEncoding the same command 10 times with different strategies:\n")

    strategies_found = {}
    for i in range(10):
        payload = encoder.encode(command)
        strategy = payload["strategy"]
        strategies_found[strategy] = strategies_found.get(strategy, 0) + 1

        print(f"{i+1:2d}. Strategy: {strategy:15s} | "
              f"Encoded length: {len(payload['encoded_data']):4d} | "
              f"First 30 chars: {payload['encoded_data'][:30]}")

    print(f"\nStrategy Distribution (10 invocations):")
    for strategy, count in sorted(strategies_found.items()):
        print(f"  {strategy:15s}: {count} times")


if __name__ == "__main__":
    # Run test suite
    test_suite = PolymorphicWrapperTestSuite()
    success = test_suite.run_all_tests()

    # Run benchmarks
    benchmark_polymorphic_encoder()

    # Demonstrate polymorphic behavior
    demonstrate_polymorphic_behavior()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
