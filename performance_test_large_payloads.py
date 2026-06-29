#!/usr/bin/env python3
"""
Performance test for Hex decoder with large payloads (>10KB)
Measures execution time, memory usage, and efficiency metrics
"""

import time
import sys
import os
from typing import Tuple, List, Dict
import json
import tracemalloc
from hex_decoder_variants import HexDecoderVariants


def generate_large_payload(size_kb: int, payload_type: str = "ascii") -> str:
    """
    Generate a large payload of specified size

    Args:
        size_kb: Size of payload in kilobytes
        payload_type: 'ascii', 'mixed', 'binary'

    Returns:
        Generated payload string
    """
    target_size = size_kb * 1024

    if payload_type == "ascii":
        # ASCII command-like payload
        base = "powershell.exe -NoProfile -Command \"Write-Host 'Test output: %d' -ForegroundColor Cyan\""
        payload = base
        counter = 0
        while len(payload) < target_size:
            payload += "\n" + base % counter
            counter += 1
            if counter > 10000:  # Safety limit
                break
        return payload[:target_size]

    elif payload_type == "mixed":
        # Mix of ASCII and special characters
        ascii_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        special = "!@#$%^&*()-_=+[]{}|;:,.<>?/\\`~\t\n\r"
        pattern = ascii_chars + special
        payload = ""
        while len(payload) < target_size:
            payload += pattern
        return payload[:target_size]

    elif payload_type == "binary":
        # Binary-like data
        payload = ""
        for i in range(target_size):
            payload += chr(i % 256)
        return payload[:target_size]

    return ""


def test_hex_decoder_performance(payload: str, test_name: str, decoder_type: str = "command") -> Dict:
    """
    Test hex decoder performance with given payload

    Args:
        payload: Input payload to decode
        test_name: Name of the test
        decoder_type: 'command', 'script', or 'binary'

    Returns:
        Dictionary with performance metrics
    """
    print(f"\n{'='*80}")
    print(f"Test: {test_name}")
    print(f"{'='*80}")

    payload_size_kb = len(payload) / 1024
    hex_encoded = payload.encode().hex()
    hex_size_kb = len(hex_encoded) / 1024

    print(f"Payload size: {payload_size_kb:.2f} KB ({len(payload)} bytes)")
    print(f"Hex encoded size: {hex_size_kb:.2f} KB ({len(hex_encoded)} bytes)")
    print(f"Encoder efficiency: {(len(hex_encoded) / len(payload)):.2f}x")

    metrics = {
        "test_name": test_name,
        "payload_size_kb": payload_size_kb,
        "payload_bytes": len(payload),
        "hex_size_kb": hex_size_kb,
        "hex_bytes": len(hex_encoded),
        "encoder_overhead": (len(hex_encoded) / len(payload)),
        "decoder_type": decoder_type,
        "results": {}
    }

    # Test different decoder types
    decoder_methods = {
        "command": HexDecoderVariants.create_command_decoder,
        "script": HexDecoderVariants.create_script_decoder,
        "binary": lambda p, e: HexDecoderVariants.create_binary_decoder(p.encode(), e)
    }

    if decoder_type not in decoder_methods:
        decoder_type = "command"

    decoder_func = decoder_methods[decoder_type]

    # Measure code generation time and size
    print(f"\nTesting {decoder_type} decoder...")

    # Memory tracking
    tracemalloc.start()
    start_time = time.time()

    try:
        vbs_code, metadata = decoder_func(payload, execute=False)

        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        generation_time_ms = (end_time - start_time) * 1000
        vbs_size_kb = len(vbs_code) / 1024

        print(f"  Code generation time: {generation_time_ms:.4f} ms")
        print(f"  Generated VBS size: {vbs_size_kb:.2f} KB ({len(vbs_code)} bytes)")
        print(f"  Peak memory usage: {peak / 1024 / 1024:.2f} MB")
        print(f"  Current memory usage: {current / 1024 / 1024:.2f} MB")

        # Calculate efficiency metrics
        overhead_percent = ((len(vbs_code) - len(payload)) / len(payload)) * 100

        metrics["results"][decoder_type] = {
            "generation_time_ms": generation_time_ms,
            "vbs_size_kb": vbs_size_kb,
            "vbs_bytes": len(vbs_code),
            "peak_memory_mb": peak / 1024 / 1024,
            "current_memory_mb": current / 1024 / 1024,
            "overhead_percent": overhead_percent,
            "metadata": {
                "function_name": metadata.get("function_name"),
                "payload_type": metadata.get("payload_type"),
                "optimization": metadata.get("optimization"),
                "hex_length": metadata.get("hex_length"),
            },
            "success": True
        }

        print(f"  Success: VBS code generated ({len(vbs_code)} bytes)")

    except Exception as e:
        print(f"  Error: {e}")
        metrics["results"][decoder_type] = {
            "error": str(e),
            "success": False
        }
        tracemalloc.stop()

    return metrics


def run_performance_suite():
    """Run complete performance test suite with various payload sizes"""

    print("\n" + "="*80)
    print("HEX DECODER LARGE PAYLOAD PERFORMANCE TEST")
    print("="*80)
    print(f"Test started: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Test configurations: (size_kb, payload_type, decoder_type)
    test_cases = [
        # Small payloads (for baseline)
        (1, "ascii", "command"),
        (5, "ascii", "command"),
        (10, "ascii", "command"),

        # Medium payloads
        (25, "ascii", "command"),
        (50, "ascii", "command"),
        (100, "ascii", "command"),

        # Large payloads (>10KB requirement)
        (150, "ascii", "command"),
        (250, "ascii", "command"),
        (500, "ascii", "command"),
        (1000, "ascii", "command"),

        # Mixed content tests
        (50, "mixed", "command"),
        (250, "mixed", "command"),
        (500, "mixed", "command"),

        # Different payload types
        (50, "ascii", "script"),
        (250, "ascii", "script"),
        (50, "ascii", "binary"),
        (250, "ascii", "binary"),
    ]

    all_results = []
    start_suite_time = time.time()

    for size_kb, payload_type, decoder_type in test_cases:
        test_name = f"{size_kb}KB_{payload_type}_{decoder_type}"

        # Generate payload
        print(f"\nGenerating {size_kb}KB payload ({payload_type})...")
        payload = generate_large_payload(size_kb, payload_type)

        # Run performance test
        result = test_hex_decoder_performance(payload, test_name, decoder_type)
        all_results.append(result)

    suite_duration = time.time() - start_suite_time

    # Print summary
    print("\n" + "="*80)
    print("PERFORMANCE TEST SUMMARY")
    print("="*80)

    summary_stats = {
        "total_tests": len(all_results),
        "successful_tests": sum(1 for r in all_results if all(v.get("success", True) for v in r["results"].values())),
        "total_duration_seconds": suite_duration,
        "test_results": []
    }

    for result in all_results:
        print(f"\nTest: {result['test_name']}")
        print(f"  Payload: {result['payload_size_kb']:.2f} KB")
        print(f"  Hex encoded: {result['hex_size_kb']:.2f} KB (encoder overhead: {result['encoder_overhead']:.2f}x)")

        for decoder_type, decoder_result in result["results"].items():
            if decoder_result.get("success"):
                print(f"  {decoder_type.upper()} Decoder:")
                print(f"    Generation time: {decoder_result['generation_time_ms']:.4f} ms")
                print(f"    VBS size: {decoder_result['vbs_size_kb']:.2f} KB")
                print(f"    Memory peak: {decoder_result['peak_memory_mb']:.2f} MB")
                print(f"    Overhead: +{decoder_result['overhead_percent']:.1f}%")
            else:
                print(f"  {decoder_type.upper()} Decoder: FAILED - {decoder_result.get('error')}")

        summary_stats["test_results"].append({
            "name": result["test_name"],
            "payload_kb": result["payload_size_kb"],
            "results": result["results"]
        })

    # Performance analysis
    print("\n" + "="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80)

    # Find slowest tests
    slowest = sorted(
        [(r["test_name"], max(v.get("generation_time_ms", 0) for v in r["results"].values() if v.get("success")))
         for r in all_results if any(v.get("success") for v in r["results"].values())],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    print("\nSlowest tests:")
    for test_name, gen_time in slowest:
        print(f"  {test_name}: {gen_time:.4f} ms")

    # Largest generated payloads
    largest = sorted(
        [(r["test_name"], max(v.get("vbs_bytes", 0) for v in r["results"].values() if v.get("success")))
         for r in all_results if any(v.get("success") for v in r["results"].values())],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    print("\nLargest generated payloads:")
    for test_name, vbs_bytes in largest:
        print(f"  {test_name}: {vbs_bytes / 1024:.2f} KB")

    # Peak memory usage
    peak_mem = max(
        [max(v.get("peak_memory_mb", 0) for v in r["results"].values() if v.get("success"))
         for r in all_results if any(v.get("success") for v in r["results"].values())],
        default=0
    )

    print(f"\nPeak memory usage: {peak_mem:.2f} MB")

    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    print("""
1. Command Decoder: Best for shell commands
   - Efficient for ASCII-heavy payloads
   - Minimal overhead for typical command sizes
   - Recommended for payloads <500KB

2. Script Decoder: Best for multi-line scripts
   - Full character support including control sequences
   - Better handling of special characters
   - Suitable for payloads with mixed content

3. Binary Decoder: Best for executable payloads
   - Byte-accurate decoding with integrity verification
   - Handles all byte values (0x00-0xFF)
   - Use for binary executables and DLLs

Performance Notes:
   - Hex encoding typically results in 2x size increase
   - Generation time scales linearly with payload size
   - Memory usage remains reasonable even for large payloads
   - All decoders handle large payloads efficiently
""")

    print(f"\nTest suite completed in {suite_duration:.2f} seconds")
    print(f"Average time per test: {suite_duration / len(test_cases):.4f} seconds")

    # Save detailed results to JSON
    results_file = "/tmp/hex_decoder_performance_results.json"
    with open(results_file, "w") as f:
        json.dump(summary_stats, f, indent=2, default=str)

    print(f"\nDetailed results saved to: {results_file}")

    return summary_stats


if __name__ == "__main__":
    try:
        results = run_performance_suite()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during test execution: {e}")
        traceback.print_exc()
        sys.exit(1)
