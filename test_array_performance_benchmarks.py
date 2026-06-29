#!/usr/bin/env python3
"""
Performance Benchmarks for Array Encoder with Various Payload Sizes
Comprehensive performance testing covering:
- Encoding/decoding speed
- Memory efficiency
- Throughput analysis
- Comparison across different configurations
"""

import sys
import time
import tracemalloc
import random
import string
import json
from array_encoder import (
    ArrayEncoder, EncoderConfig, EncodingType, OutputFormat,
    ChunkingStrategy
)


class PerformanceBenchmark:
    """Performance benchmark suite for array encoder"""

    def __init__(self):
        self.results = []

    def generate_payload(self, size):
        """Generate random payload of specified size"""
        return ''.join(random.choices(string.printable, k=size))

    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of function"""
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        return result, elapsed

    def measure_memory(self, func, *args, **kwargs):
        """Measure memory usage of function"""
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return result, current, peak

    def benchmark_encoding_speed(self):
        """Benchmark encoding speed for various payload sizes"""
        print("\n" + "=" * 80)
        print("BENCHMARK: Encoding Speed")
        print("=" * 80)
        print(f"{'Payload Size':>15} {'Time (ms)':>12} {'Throughput (MB/s)':>18} {'Result'}")
        print("-" * 60)

        payload_sizes = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000]

        for size in payload_sizes:
            try:
                payload = self.generate_payload(size)

                def encode_func():
                    config = EncoderConfig(
                        chunk_size=32,
                        encoding_type=EncodingType.HEX,
                        output_format=OutputFormat.JSON
                    )
                    encoder = ArrayEncoder(config)
                    return encoder.encode(payload)

                _, elapsed = self.measure_time(encode_func)

                throughput = size / (elapsed * 1024 * 1024) if elapsed > 0 else 0
                time_ms = elapsed * 1000

                print(f"{size:>15} {time_ms:>12.3f} {throughput:>18.2f} ✓")
                self.results.append({
                    "benchmark": "encoding_speed",
                    "payload_size": size,
                    "time_ms": time_ms,
                    "throughput_mbps": throughput
                })
            except Exception as e:
                print(f"{size:>15} {'ERROR':>12} {str(e)[:20]:>18} ✗")

    def benchmark_decoding_speed(self):
        """Benchmark decoding speed for various chunk counts"""
        print("\n" + "=" * 80)
        print("BENCHMARK: Decoding Speed")
        print("=" * 80)
        print(f"{'Chunk Count':>15} {'Time (ms)':>12} {'Throughput':>18} {'Result'}")
        print("-" * 60)

        payload_sizes = [1000, 5000, 10000, 50000, 100000]

        for size in payload_sizes:
            try:
                payload = self.generate_payload(size)

                config = EncoderConfig(
                    chunk_size=32,
                    encoding_type=EncodingType.HEX,
                    output_format=OutputFormat.JSON
                )
                encoder = ArrayEncoder(config)
                encoded = encoder.encode(payload)
                chunk_count = encoded["count"]
                chunks = encoded["chunks"]

                def decode_func():
                    result = ""
                    for chunk in chunks:
                        try:
                            result += bytes.fromhex(chunk).decode('utf-8', errors='ignore')
                        except ValueError:
                            pass
                    return result

                _, elapsed = self.measure_time(decode_func)

                throughput = chunk_count / elapsed if elapsed > 0 else 0
                time_ms = elapsed * 1000

                print(f"{chunk_count:>15} {time_ms:>12.3f} {throughput:>18.0f} chunks/s ✓")
                self.results.append({
                    "benchmark": "decoding_speed",
                    "chunk_count": chunk_count,
                    "time_ms": time_ms,
                    "throughput_chunks_per_sec": throughput
                })
            except Exception as e:
                print(f"{size:>15} {'ERROR':>12} {str(e)[:20]:>18} ✗")

    def benchmark_encoding_types(self):
        """Benchmark different encoding types"""
        print("\n" + "=" * 80)
        print("BENCHMARK: Encoding Types Comparison")
        print("=" * 80)
        print(f"{'Encoding Type':>15} {'Time (ms)':>12} {'Output Size':>15} {'Result'}")
        print("-" * 60)

        payload = self.generate_payload(10000)

        encoding_types = [
            ("HEX", EncodingType.HEX),
            ("BASE64", EncodingType.BASE64),
            ("OCTAL", EncodingType.OCTAL),
        ]

        for enc_name, enc_type in encoding_types:
            try:
                def encode_func():
                    config = EncoderConfig(
                        chunk_size=32,
                        encoding_type=enc_type,
                        output_format=OutputFormat.JSON
                    )
                    encoder = ArrayEncoder(config)
                    return encoder.generate(payload)

                result, elapsed = self.measure_time(encode_func)
                output_size = len(result)
                time_ms = elapsed * 1000

                print(f"{enc_name:>15} {time_ms:>12.3f} {output_size:>15} ✓")
                self.results.append({
                    "benchmark": "encoding_type_comparison",
                    "encoding_type": enc_name,
                    "time_ms": time_ms,
                    "output_size": output_size
                })
            except Exception as e:
                print(f"{enc_name:>15} {'ERROR':>12} {str(e)[:20]:>15} ✗")

    def benchmark_chunk_sizes(self):
        """Benchmark different chunk sizes"""
        print("\n" + "=" * 80)
        print("BENCHMARK: Chunk Size Comparison (10KB Payload)")
        print("=" * 80)
        print(f"{'Chunk Size':>15} {'Time (ms)':>12} {'Chunk Count':>15} {'Result'}")
        print("-" * 60)

        payload = self.generate_payload(10000)
        chunk_sizes = [4, 8, 16, 32, 64, 128, 256, 512]

        for chunk_size in chunk_sizes:
            try:
                def encode_func():
                    config = EncoderConfig(
                        chunk_size=chunk_size,
                        encoding_type=EncodingType.HEX,
                        output_format=OutputFormat.PYTHON
                    )
                    encoder = ArrayEncoder(config)
                    return encoder.encode(payload)

                result, elapsed = self.measure_time(encode_func)
                chunk_count = result["count"]
                time_ms = elapsed * 1000

                print(f"{chunk_size:>15} {time_ms:>12.3f} {chunk_count:>15} ✓")
                self.results.append({
                    "benchmark": "chunk_size_comparison",
                    "chunk_size": chunk_size,
                    "time_ms": time_ms,
                    "chunk_count": chunk_count
                })
            except Exception as e:
                print(f"{chunk_size:>15} {'ERROR':>12} {str(e)[:20]:>15} ✗")

    def benchmark_output_formats(self):
        """Benchmark different output formats"""
        print("\n" + "=" * 80)
        print("BENCHMARK: Output Format Comparison (5KB Payload)")
        print("=" * 80)
        print(f"{'Output Format':>15} {'Time (ms)':>12} {'Output Size':>15} {'Result'}")
        print("-" * 60)

        payload = self.generate_payload(5000)

        output_formats = [
            ("PYTHON", OutputFormat.PYTHON),
            ("VBS", OutputFormat.VBS),
            ("JAVASCRIPT", OutputFormat.JAVASCRIPT),
            ("POWERSHELL", OutputFormat.POWERSHELL),
            ("BASH", OutputFormat.BASH),
            ("JSON", OutputFormat.JSON),
            ("C", OutputFormat.C),
        ]

        for fmt_name, fmt_enum in output_formats:
            try:
                def encode_func():
                    config = EncoderConfig(
                        chunk_size=32,
                        encoding_type=EncodingType.HEX,
                        output_format=fmt_enum
                    )
                    encoder = ArrayEncoder(config)
                    return encoder.generate(payload)

                result, elapsed = self.measure_time(encode_func)
                output_size = len(result)
                time_ms = elapsed * 1000

                print(f"{fmt_name:>15} {time_ms:>12.3f} {output_size:>15} ✓")
                self.results.append({
                    "benchmark": "output_format_comparison",
                    "format": fmt_name,
                    "time_ms": time_ms,
                    "output_size": output_size
                })
            except Exception as e:
                print(f"{fmt_name:>15} {'ERROR':>12} {str(e)[:20]:>15} ✗")

    def benchmark_chunking_strategies(self):
        """Benchmark different chunking strategies"""
        print("\n" + "=" * 80)
        print("BENCHMARK: Chunking Strategy Comparison (20KB Payload)")
        print("=" * 80)
        print(f"{'Strategy':>20} {'Time (ms)':>12} {'Chunk Count':>15} {'Result'}")
        print("-" * 60)

        payload = self.generate_payload(20000)

        strategies = [
            ("SEQUENTIAL", ChunkingStrategy.SEQUENTIAL),
            ("RANDOM_ORDER", ChunkingStrategy.RANDOM_ORDER),
            ("VARIABLE_SIZE", ChunkingStrategy.VARIABLE_SIZE),
            ("INTERLEAVED", ChunkingStrategy.INTERLEAVED),
        ]

        for strat_name, strat_enum in strategies:
            try:
                def encode_func():
                    config = EncoderConfig(
                        chunk_size=64,
                        encoding_type=EncodingType.HEX,
                        output_format=OutputFormat.JSON,
                        chunking_strategy=strat_enum,
                        min_chunk_size=32,
                        max_chunk_size=128
                    )
                    encoder = ArrayEncoder(config)
                    return encoder.encode(payload)

                result, elapsed = self.measure_time(encode_func)
                chunk_count = result["count"]
                time_ms = elapsed * 1000

                print(f"{strat_name:>20} {time_ms:>12.3f} {chunk_count:>15} ✓")
                self.results.append({
                    "benchmark": "chunking_strategy_comparison",
                    "strategy": strat_name,
                    "time_ms": time_ms,
                    "chunk_count": chunk_count
                })
            except Exception as e:
                print(f"{strat_name:>20} {'ERROR':>12} {str(e)[:20]:>15} ✗")

    def benchmark_memory_usage(self):
        """Benchmark memory usage for various payload sizes"""
        print("\n" + "=" * 80)
        print("BENCHMARK: Memory Usage")
        print("=" * 80)
        print(f"{'Payload Size':>15} {'Current (MB)':>15} {'Peak (MB)':>15} {'Result'}")
        print("-" * 60)

        payload_sizes = [1000, 10000, 100000, 500000]

        for size in payload_sizes:
            try:
                payload = self.generate_payload(size)

                def encode_func():
                    config = EncoderConfig(
                        chunk_size=64,
                        encoding_type=EncodingType.HEX,
                        output_format=OutputFormat.JSON
                    )
                    encoder = ArrayEncoder(config)
                    return encoder.encode(payload)

                _, current, peak = self.measure_memory(encode_func)
                current_mb = current / (1024 * 1024)
                peak_mb = peak / (1024 * 1024)

                print(f"{size:>15} {current_mb:>15.2f} {peak_mb:>15.2f} ✓")
                self.results.append({
                    "benchmark": "memory_usage",
                    "payload_size": size,
                    "current_memory_mb": current_mb,
                    "peak_memory_mb": peak_mb
                })
            except Exception as e:
                print(f"{size:>15} {'ERROR':>15} {str(e)[:20]:>15} ✗")

    def benchmark_scalability(self):
        """Benchmark scalability across payload sizes"""
        print("\n" + "=" * 80)
        print("BENCHMARK: Scalability Analysis")
        print("=" * 80)
        print(f"{'Payload Size':>15} {'Time/KB (ms)':>15} {'Scaling Factor':>15} {'Result'}")
        print("-" * 60)

        payload_sizes = [1000, 5000, 10000, 50000, 100000]
        baseline_time = None
        baseline_size = None

        for size in payload_sizes:
            try:
                payload = self.generate_payload(size)

                def encode_func():
                    config = EncoderConfig(
                        chunk_size=32,
                        encoding_type=EncodingType.HEX,
                        output_format=OutputFormat.JSON
                    )
                    encoder = ArrayEncoder(config)
                    return encoder.encode(payload)

                _, elapsed = self.measure_time(encode_func)
                time_per_kb = (elapsed * 1000) / (size / 1024)

                if baseline_time is None:
                    baseline_time = elapsed
                    baseline_size = size
                    scaling_factor = 1.0
                else:
                    scaling_factor = (elapsed / baseline_time) / (size / baseline_size)

                print(f"{size:>15} {time_per_kb:>15.3f} {scaling_factor:>15.2f}x ✓")
                self.results.append({
                    "benchmark": "scalability",
                    "payload_size": size,
                    "time_per_kb_ms": time_per_kb,
                    "scaling_factor": scaling_factor
                })
            except Exception as e:
                print(f"{size:>15} {'ERROR':>15} {str(e)[:20]:>15} ✗")

    def save_results(self, filename="benchmark_results.json"):
        """Save benchmark results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\nResults saved to {filename}")
        except Exception as e:
            print(f"Error saving results: {e}")

    def run_all_benchmarks(self):
        """Run all benchmarks"""
        print("\n" + "=" * 80)
        print("ARRAY ENCODER PERFORMANCE BENCHMARKS")
        print("=" * 80)

        self.benchmark_encoding_speed()
        self.benchmark_decoding_speed()
        self.benchmark_encoding_types()
        self.benchmark_chunk_sizes()
        self.benchmark_output_formats()
        self.benchmark_chunking_strategies()
        self.benchmark_memory_usage()
        self.benchmark_scalability()

        # Summary
        print("\n" + "=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)
        print(f"Total benchmarks executed: {len(self.results)}")

        # Save results
        self.save_results()

        return True


def main():
    """Main entry point"""
    benchmark = PerformanceBenchmark()
    success = benchmark.run_all_benchmarks()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
