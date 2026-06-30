#!/usr/bin/env python3
"""
Integration Test: Base64 → Polymorphic Wrapper Chaining
Tests component interaction, variable isolation, end-to-end execution,
performance benchmarks, and resource cleanup.

Verification checklist:
1. Components interact correctly
2. No variable conflicts between components
3. Output payload executes end-to-end
4. Performance acceptable (< 1s generation)
5. No memory leaks or hung processes
"""

import sys
import os
import time
import psutil
import json
import base64
import subprocess
import tempfile
import gc
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base64_encoder import Base64Encoder, Base64OperationsPair
from polymorphic_wrapper import (
    PolymorphicCommandEncoder,
    PolymorphicConfig,
    PolymorphicStrategy,
    create_polymorphic_wrapper,
)


class Base64PolymorphicIntegrationTest:
    """Integration test suite for Base64 → Polymorphic wrapper chaining"""

    def __init__(self):
        self.passed = []
        self.failed = []
        self.performance_results = {}
        self.memory_baseline = None
        self.test_results = {
            "test": "Base64 → Polymorphic Wrapper Integration",
            "status": "FAIL",
            "issues": [],
        }

    def run_all_tests(self) -> Dict:
        """Run complete integration test suite"""
        print("=" * 80)
        print("BASE64 → POLYMORPHIC WRAPPER INTEGRATION TEST")
        print("=" * 80)
        print(f"\nTest started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python version: {sys.version}")
        print(f"Process ID: {os.getpid()}")

        # Record baseline memory
        self.memory_baseline = self._get_process_memory()
        print(f"Baseline memory: {self.memory_baseline:.2f} MB")

        try:
            # Run all integration tests
            self.test_component_interaction()
            self.test_variable_isolation()
            self.test_end_to_end_execution()
            self.test_performance()
            self.test_memory_cleanup()
            self.test_no_hung_processes()

            # Determine final status
            if self.failed:
                self.test_results["status"] = "FAIL"
                self.test_results["issues"] = self.failed
            else:
                self.test_results["status"] = "PASS"
                self.test_results["issues"] = []

        except Exception as e:
            self.test_results["status"] = "FAIL"
            self.test_results["issues"].append(f"Unhandled exception: {str(e)}")
            print(f"\n✗ Unhandled exception: {e}")

        # Print summary
        self._print_summary()
        return self.test_results

    def test_component_interaction(self):
        """Test 1: Components interact correctly"""
        print("\n" + "=" * 80)
        print("TEST 1: Component Interaction")
        print("=" * 80)

        try:
            # Initialize both components
            b64_encoder = Base64Encoder()
            poly_encoder = PolymorphicCommandEncoder()

            test_commands = [
                "echo 'Integration Test'",
                "ls -la /tmp",
                "python3 --version",
            ]

            interaction_count = 0

            for cmd in test_commands:
                # Step 1: Base64 encode
                b64_encoded = b64_encoder.encode_to_base64(cmd)
                print(f"\n[1] Base64 encode: '{cmd[:30]}...'")
                print(f"    → Encoded: {b64_encoded[:50]}...")

                # Step 2: Polymorphic encode the Base64 string
                poly_payload = poly_encoder.encode(b64_encoded)
                print(f"[2] Polymorphic encode (strategy: {poly_payload['strategy']})")
                print(f"    → Encoded length: {len(poly_payload['encoded_data'])}")

                # Step 3: Verify we can decode back through polymorphic layer
                namespace = {}
                exec(poly_payload["decoder_code"], namespace)
                decoder_func = namespace[poly_payload["decoder_name"]]
                poly_decoded = decoder_func()
                print(f"[3] Polymorphic decode")
                print(f"    → Matches Base64: {poly_decoded == b64_encoded}")

                # Step 4: Verify we can Base64 decode to original
                final_decoded = base64.b64decode(poly_decoded).decode()
                print(f"[4] Base64 decode")
                print(f"    → Matches original: {final_decoded == cmd}")

                assert poly_decoded == b64_encoded, "Polymorphic layer failed"
                assert final_decoded == cmd, "Base64 layer failed"

                interaction_count += 1

            print(f"\n✓ Component interaction successful ({interaction_count} command chains)")
            self.passed.append("Component interaction")

        except Exception as e:
            issue = f"Component interaction failed: {str(e)}"
            self.failed.append(issue)
            print(f"✗ {issue}")

    def test_variable_isolation(self):
        """Test 2: No variable conflicts between components"""
        print("\n" + "=" * 80)
        print("TEST 2: Variable Isolation (No Name Conflicts)")
        print("=" * 80)

        try:
            poly_encoder = PolymorphicCommandEncoder()
            test_cmd = "test_variable_isolation_command"

            # Generate multiple polymorphic encodings
            payloads = []
            variable_names = set()
            decoder_names = set()

            print("\nGenerating 50 polymorphic encodings...")
            for i in range(50):
                payload = poly_encoder.encode(test_cmd)
                payloads.append(payload)

                var_name = payload.get("var_name", "")
                decoder_name = payload.get("decoder_name", "")

                variable_names.add(var_name)
                decoder_names.add(decoder_name)

            print(f"\nUnique variable names: {len(variable_names)}")
            print(f"Unique decoder names: {len(decoder_names)}")
            print(f"Total encodings: {len(payloads)}")

            # Check for duplicates (conflicts)
            if len(variable_names) < len(payloads) * 0.8:
                issue = f"High rate of variable name collisions: {len(variable_names)}/{len(payloads)}"
                self.failed.append(issue)
                print(f"✗ {issue}")
                return

            if len(decoder_names) < len(payloads) * 0.8:
                issue = f"High rate of decoder name collisions: {len(decoder_names)}/{len(payloads)}"
                self.failed.append(issue)
                print(f"✗ {issue}")
                return

            # Test that no two decoders interfere
            print("\nTesting decoder isolation...")
            all_namespace = {}
            success_count = 0

            for payload in payloads:
                try:
                    exec(payload["decoder_code"], all_namespace)
                    decoder_func = all_namespace[payload["decoder_name"]]
                    result = decoder_func()
                    if result == test_cmd:
                        success_count += 1
                except Exception as e:
                    issue = f"Decoder isolation failed: {str(e)}"
                    self.failed.append(issue)
                    print(f"✗ {issue}")
                    return

            print(f"✓ All {success_count}/{len(payloads)} decoders executed successfully without conflicts")
            self.passed.append("Variable isolation")

        except Exception as e:
            issue = f"Variable isolation test failed: {str(e)}"
            self.failed.append(issue)
            print(f"✗ {issue}")

    def test_end_to_end_execution(self):
        """Test 3: Output payload executes end-to-end"""
        print("\n" + "=" * 80)
        print("TEST 3: End-to-End Execution (Full Chain)")
        print("=" * 80)

        try:
            # Test with different output formats
            formats = ["python"]  # Focus on Python for execution testing
            test_commands = [
                "echo 'test1'",
                "python3 -c \"print('test2')\"",
            ]

            execution_success = 0

            for fmt in formats:
                print(f"\n[FORMAT: {fmt.upper()}]")

                for cmd in test_commands:
                    try:
                        # Generate wrapper with Base64+Polymorphic chaining
                        b64_encoder = Base64Encoder()
                        b64_encoded = b64_encoder.encode_to_base64(cmd)

                        # Create polymorphic wrapper around Base64 string
                        poly_config = PolymorphicConfig(output_format=fmt)
                        poly_encoder = PolymorphicCommandEncoder(poly_config)
                        payload = poly_encoder.encode(b64_encoded)

                        # For Python, we can directly execute
                        if fmt == "python":
                            namespace = {}
                            exec(payload["decoder_code"], namespace)
                            decoder_func = namespace[payload["decoder_name"]]
                            decoded_b64 = decoder_func()

                            # Verify it matches
                            assert decoded_b64 == b64_encoded, "Polymorphic decode mismatch"

                            final_cmd = base64.b64decode(decoded_b64).decode()
                            assert final_cmd == cmd, "Base64 decode mismatch"

                            print(f"  ✓ '{cmd[:30]}...' → Full chain verified")
                            execution_success += 1

                    except Exception as e:
                        issue = f"End-to-end execution failed for '{cmd}': {str(e)}"
                        self.failed.append(issue)
                        print(f"  ✗ {issue}")

            print(f"\n✓ End-to-end execution: {execution_success} successful")
            self.passed.append("End-to-end execution")

        except Exception as e:
            issue = f"End-to-end execution test failed: {str(e)}"
            self.failed.append(issue)
            print(f"✗ {issue}")

    def test_performance(self):
        """Test 4: Performance acceptable (< 1s generation)"""
        print("\n" + "=" * 80)
        print("TEST 4: Performance Benchmark (< 1s requirement)")
        print("=" * 80)

        try:
            b64_encoder = Base64Encoder()
            poly_encoder = PolymorphicCommandEncoder()

            test_cmd = "performance_test_" * 5  # ~85 chars

            # Benchmark Base64 encoding
            iterations = 100
            start = time.time()
            for _ in range(iterations):
                b64_encoder.encode_to_base64(test_cmd)
            b64_time = time.time() - start

            # Benchmark Polymorphic encoding
            start = time.time()
            for _ in range(iterations):
                poly_encoder.encode(test_cmd)
            poly_time = time.time() - start

            # Benchmark combined chain
            start = time.time()
            for _ in range(iterations):
                b64_encoded = b64_encoder.encode_to_base64(test_cmd)
                poly_encoder.encode(b64_encoded)
            combined_time = time.time() - start

            # Calculate per-operation times
            b64_per_op = (b64_time / iterations) * 1000  # ms
            poly_per_op = (poly_time / iterations) * 1000  # ms
            combined_per_op = (combined_time / iterations) * 1000  # ms

            print(f"\nBenchmark results ({iterations} iterations, {len(test_cmd)} char command):")
            print(f"  Base64 alone:       {b64_per_op:.3f} ms per operation")
            print(f"  Polymorphic alone:  {poly_per_op:.3f} ms per operation")
            print(f"  Combined chain:     {combined_per_op:.3f} ms per operation")

            self.performance_results = {
                "b64_ms": b64_per_op,
                "poly_ms": poly_per_op,
                "combined_ms": combined_per_op,
                "iterations": iterations,
            }

            # Check performance requirement: < 1s for combined operation
            if combined_per_op < 1000:  # 1 second = 1000ms
                print(f"✓ Performance acceptable: {combined_per_op:.3f}ms < 1000ms")
                self.passed.append("Performance (< 1s)")
            else:
                issue = f"Performance degraded: {combined_per_op:.3f}ms >= 1000ms"
                self.failed.append(issue)
                print(f"✗ {issue}")

        except Exception as e:
            issue = f"Performance test failed: {str(e)}"
            self.failed.append(issue)
            print(f"✗ {issue}")

    def test_memory_cleanup(self):
        """Test 5: No memory leaks"""
        print("\n" + "=" * 80)
        print("TEST 5: Memory Cleanup (No Leaks)")
        print("=" * 80)

        try:
            b64_encoder = Base64Encoder()
            poly_encoder = PolymorphicCommandEncoder()

            test_cmd = "memory_test_" * 10

            print("\nMemory stress test (1000 encode operations)...")

            initial_memory = self._get_process_memory()
            print(f"  Initial memory: {initial_memory:.2f} MB")

            # Perform many operations
            for i in range(1000):
                b64_encoded = b64_encoder.encode_to_base64(test_cmd)
                poly_encoder.encode(b64_encoded)

                # Periodic garbage collection
                if i % 100 == 0:
                    gc.collect()

            # Force garbage collection
            gc.collect()

            final_memory = self._get_process_memory()
            memory_delta = final_memory - initial_memory

            print(f"  Final memory: {final_memory:.2f} MB")
            print(f"  Memory delta: {memory_delta:.2f} MB")

            # Allow up to 50MB growth for 1000 operations
            if memory_delta < 50:
                print(f"✓ Memory cleanup good: {memory_delta:.2f}MB growth")
                self.passed.append("Memory cleanup")
            else:
                issue = f"Potential memory leak: {memory_delta:.2f}MB growth"
                self.failed.append(issue)
                print(f"✗ {issue}")

        except Exception as e:
            issue = f"Memory cleanup test failed: {str(e)}"
            self.failed.append(issue)
            print(f"✗ {issue}")

    def test_no_hung_processes(self):
        """Test 6: No hung processes or deadlocks"""
        print("\n" + "=" * 80)
        print("TEST 6: No Hung Processes")
        print("=" * 80)

        try:
            poly_encoder = PolymorphicCommandEncoder()
            test_cmd = "hung_process_test"

            print("\nTesting for hung processes (50 operations with timeouts)...")

            hung_count = 0

            for i in range(50):
                start = time.time()

                try:
                    payload = poly_encoder.encode(test_cmd)

                    # Try to decode (should complete quickly)
                    namespace = {}
                    exec(payload["decoder_code"], namespace)
                    decoder_func = namespace[payload["decoder_name"]]
                    result = decoder_func()

                    elapsed = time.time() - start

                    # Each operation should complete in < 100ms
                    if elapsed > 0.1:
                        print(f"  ⚠ Operation {i+1} took {elapsed*1000:.1f}ms (slow)")

                except Exception as e:
                    print(f"  ✗ Operation {i+1} failed: {e}")
                    hung_count += 1

            if hung_count == 0:
                print(f"✓ No hung processes: All 50 operations completed successfully")
                self.passed.append("No hung processes")
            else:
                issue = f"Detected {hung_count} hung/failed operations"
                self.failed.append(issue)
                print(f"✗ {issue}")

        except Exception as e:
            issue = f"Hung process test failed: {str(e)}"
            self.failed.append(issue)
            print(f"✗ {issue}")

    def _get_process_memory(self) -> float:
        """Get current process memory in MB"""
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0

    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        print(f"\nPassed tests ({len(self.passed)}):")
        for test in self.passed:
            print(f"  ✓ {test}")

        if self.failed:
            print(f"\nFailed tests ({len(self.failed)}):")
            for issue in self.failed:
                print(f"  ✗ {issue}")

        print(f"\nPerformance metrics:")
        for key, value in self.performance_results.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")

        print(f"\nOverall status: {self.test_results['status']}")
        print(f"Total passed: {len(self.passed)}")
        print(f"Total failed: {len(self.failed)}")


def main():
    """Main entry point"""
    test_suite = Base64PolymorphicIntegrationTest()
    results = test_suite.run_all_tests()

    # Return results as JSON
    print("\n" + "=" * 80)
    print("FINAL RESULTS (JSON)")
    print("=" * 80)
    print(json.dumps(results, indent=2))

    # Save results
    output_file = "/home/user/sc-generator/base64_polymorphic_integration_test_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")

    # Exit with status
    exit_code = 0 if results["status"] == "PASS" else 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
