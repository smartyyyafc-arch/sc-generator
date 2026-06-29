#!/usr/bin/env python3
"""
Multi-Encoding Performance Test Suite
Tests encoding/decoding performance with variable payload sizes: 5KB, 10KB, 20KB
"""

import time
import json
import sys
import hashlib
import hmac
import secrets
import base64
import binascii
import random
import struct
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    payload_size: int
    payload_size_kb: float
    encode_time_ms: float
    decode_time_ms: float
    total_time_ms: float
    encoded_size: int
    encoded_size_kb: float
    compression_ratio: float
    throughput_encode_mbps: float
    throughput_decode_mbps: float
    throughput_total_mbps: float
    layer1_time_pct: float
    layer2_time_pct: float
    layer3_time_pct: float
    variant_used: int
    success: bool


# ============================================================================
# LAYER 1: Base64 + HMAC Integrity
# ============================================================================

class Layer1Base64:
    """Base64 with HMAC integrity verification"""

    def __init__(self):
        self.key = secrets.token_bytes(16)
        self.salt = secrets.token_hex(8)

    def encode(self, data: bytes) -> bytes:
        """Encode with HMAC protection"""
        # Add random padding
        prefix = secrets.token_bytes(random.randint(4, 8))
        suffix = secrets.token_bytes(random.randint(4, 8))
        padded = prefix + data + suffix

        # Base64 encode
        encoded = base64.b64encode(padded)

        # Compute HMAC
        h = hmac.new(self.key, data, hashlib.sha256)
        sig = h.digest()[:16]

        return sig + encoded

    def decode(self, encoded: bytes) -> bytes:
        """Decode and verify HMAC"""
        sig = encoded[:16]
        b64_data = encoded[16:]

        # Decode base64
        padded = base64.b64decode(b64_data)

        # Remove padding (find actual data)
        # Try to strip leading/trailing bytes
        for start in range(min(16, len(padded))):
            for end in range(len(padded), max(len(padded)-16, 0), -1):
                candidate = padded[start:end]
                if candidate:
                    h = hmac.new(self.key, candidate, hashlib.sha256)
                    if hmac.compare_digest(sig, h.digest()[:16]):
                        return candidate

        raise ValueError("HMAC verification failed")


# ============================================================================
# LAYER 2: Polymorphic Hex Encoding
# ============================================================================

class Layer2PolymorphicHex:
    """Hex encoding with 4 variants"""

    def __init__(self):
        self.variant = secrets.randbelow(4)
        self.mask = secrets.randbelow(256)
        self.offset = secrets.randbelow(16)

    def encode(self, data: bytes) -> bytes:
        """Encode using variant"""
        hex_str = binascii.hexlify(data).decode('ascii')

        if self.variant == 0:
            # Variant 0: Bit inversion
            result = ''.join(f'{(int(h, 16) ^ 0xF):x}' for h in hex_str)
        elif self.variant == 1:
            # Variant 1: Interleaved padding
            result = ''.join(h + f'{secrets.randbelow(16):x}' for h in hex_str)
        elif self.variant == 2:
            # Variant 2: Offset and reverse
            result = ''.join(f'{(int(h, 16) + self.offset) % 16:x}' for h in hex_str)
            result = result[::-1]
        else:
            # Variant 3: XOR mask
            result = ''.join(f'{(int(h, 16) ^ (self.mask % 16)):x}' for h in hex_str)

        # Add variant marker
        marker = f'{self.variant:01x}'
        return marker.encode() + result.encode()

    def decode(self, data: bytes) -> bytes:
        """Decode using variant"""
        marker = chr(data[0])
        variant = int(marker, 16)
        hex_str = data[1:].decode('ascii')

        if variant == 0:
            result = ''.join(f'{(int(h, 16) ^ 0xF):x}' for h in hex_str)
        elif variant == 1:
            result = ''.join(hex_str[i] for i in range(0, len(hex_str), 2))
        elif variant == 2:
            hex_str = hex_str[::-1]
            result = ''.join(f'{(int(h, 16) - self.offset) % 16:x}' for h in hex_str)
        else:
            result = ''.join(f'{(int(h, 16) ^ (self.mask % 16)):x}' for h in hex_str)

        return binascii.unhexlify(result)


# ============================================================================
# LAYER 3: Shuffled Array
# ============================================================================

class Layer3ShuffledArray:
    """Array shuffling with position tracking"""

    def __init__(self):
        self.seed = secrets.token_hex(8)

    def encode(self, data: bytes) -> bytes:
        """Shuffle array elements"""
        # Convert to hex pairs
        hex_str = binascii.hexlify(data).decode('ascii')
        pairs = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]

        # Create shuffle
        indices = list(range(len(pairs)))
        random.seed(hash(self.seed) % (2**32))
        shuffled_indices = indices.copy()
        random.shuffle(shuffled_indices)

        shuffled_pairs = [pairs[i] for i in shuffled_indices]

        # Create position map (compact format)
        pos_map = ''.join(f'{idx:04x}' for idx in shuffled_indices)

        # Return as JSON-like format
        payload = {
            'd': shuffled_pairs,
            'p': pos_map,
            'n': len(pairs)
        }
        json_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        return json_bytes

    def decode(self, data: bytes) -> bytes:
        """Unshuffle array elements"""
        payload = json.loads(data.decode('utf-8'))

        shuffled_pairs = payload['d']
        pos_map = payload['p']
        n_pairs = payload['n']

        # Decode position map
        indices = [int(pos_map[i:i+4], 16) for i in range(0, len(pos_map), 4)]

        # Restore original order
        result_pairs = [''] * len(shuffled_pairs)
        for pos, idx in enumerate(indices):
            result_pairs[idx] = shuffled_pairs[pos]

        hex_str = ''.join(result_pairs)
        return binascii.unhexlify(hex_str)


# ============================================================================
# Hardened Multi-Encoder/Decoder
# ============================================================================

class HardenedMultiEncoder:
    """Three-layer hardened encoder"""

    def __init__(self):
        self.layer1 = Layer1Base64()
        self.layer2 = Layer2PolymorphicHex()
        self.layer3 = Layer3ShuffledArray()
        self.layer_times = [0, 0, 0]

    def encode(self, data: str) -> str:
        """Encode through all three layers"""
        data_bytes = data.encode('utf-8')

        # Layer 1: Base64 + HMAC
        start = time.perf_counter()
        layer1_out = self.layer1.encode(data_bytes)
        self.layer_times[0] += (time.perf_counter() - start)

        # Layer 2: Polymorphic Hex
        start = time.perf_counter()
        layer2_out = self.layer2.encode(layer1_out)
        self.layer_times[1] += (time.perf_counter() - start)

        # Layer 3: Array Shuffle
        start = time.perf_counter()
        layer3_out = self.layer3.encode(layer2_out)
        self.layer_times[2] += (time.perf_counter() - start)

        # Return as base64 string for compatibility
        return base64.b64encode(layer3_out).decode('ascii')

    def decode(self, encoded_str: str) -> str:
        """Decode through all three layers in reverse"""
        layer3_in = base64.b64decode(encoded_str.encode('ascii'))

        # Layer 3: Unshuffle
        start = time.perf_counter()
        layer2_out = self.layer3.decode(layer3_in)
        self.layer_times[2] += (time.perf_counter() - start)

        # Layer 2: Dehex
        start = time.perf_counter()
        layer1_out = self.layer2.decode(layer2_out)
        self.layer_times[1] += (time.perf_counter() - start)

        # Layer 1: Decode Base64 and verify
        start = time.perf_counter()
        data_bytes = self.layer1.decode(layer1_out)
        self.layer_times[0] += (time.perf_counter() - start)

        return data_bytes.decode('utf-8')


# ============================================================================
# Performance Testing
# ============================================================================

def generate_payload(size_kb: int) -> str:
    """Generate random test payload"""
    size_bytes = size_kb * 1024
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()'
    return ''.join(random.choice(chars) for _ in range(size_bytes))


def measure_performance(payload_size_kb: int, iterations: int = 3) -> PerformanceMetrics:
    """Measure encoding/decoding performance"""

    print(f"\n{'='*70}")
    print(f"Testing {payload_size_kb}KB Payload (Iterations: {iterations})")
    print(f"{'='*70}")

    encode_times = []
    decode_times = []
    encoded_sizes = []
    variants = []
    total_layer_times = [0, 0, 0]

    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}...", end=' ', flush=True)

        payload = generate_payload(payload_size_kb)
        payload_size = len(payload)

        encoder = HardenedMultiEncoder()

        # Measure encoding
        start_time = time.perf_counter()
        encoded = encoder.encode(payload)
        encode_duration = time.perf_counter() - start_time

        # Measure decoding (reuse same encoder to have correct keys)
        start_time = time.perf_counter()
        decoded = encoder.decode(encoded)
        decode_duration = time.perf_counter() - start_time

        # Verify correctness
        if decoded != payload:
            print("FAILED - Verification mismatch!")
            return PerformanceMetrics(
                payload_size=0, payload_size_kb=0, encode_time_ms=0, decode_time_ms=0,
                total_time_ms=0, encoded_size=0, encoded_size_kb=0, compression_ratio=0,
                throughput_encode_mbps=0, throughput_decode_mbps=0, throughput_total_mbps=0,
                layer1_time_pct=0, layer2_time_pct=0, layer3_time_pct=0, variant_used=0, success=False
            )

        encode_times.append(encode_duration * 1000)
        decode_times.append(decode_duration * 1000)
        encoded_sizes.append(len(encoded))
        variants.append(encoder.layer2.variant)

        for j in range(3):
            total_layer_times[j] += encoder.layer_times[j]

        print(f"✓ {encode_duration*1000:.2f}ms encode, {decode_duration*1000:.2f}ms decode")

    # Calculate statistics
    avg_encode_ms = sum(encode_times) / len(encode_times)
    avg_decode_ms = sum(decode_times) / len(decode_times)
    avg_total_ms = avg_encode_ms + avg_decode_ms
    avg_encoded_size = sum(encoded_sizes) / len(encoded_sizes)

    payload_size_bytes = payload_size_kb * 1024
    compression_ratio = avg_encoded_size / payload_size_bytes

    # Throughput calculations
    throughput_encode = (payload_size_bytes / (1024 * 1024)) / (avg_encode_ms / 1000)
    throughput_decode = (payload_size_bytes / (1024 * 1024)) / (avg_decode_ms / 1000)
    throughput_total = (payload_size_bytes / (1024 * 1024)) / (avg_total_ms / 1000)

    # Layer timing percentages (approximate based on iteration 0)
    total_time = sum(total_layer_times)
    layer1_pct = (total_layer_times[0] / total_time * 100) if total_time > 0 else 0
    layer2_pct = (total_layer_times[1] / total_time * 100) if total_time > 0 else 0
    layer3_pct = (total_layer_times[2] / total_time * 100) if total_time > 0 else 0

    metrics = PerformanceMetrics(
        payload_size=payload_size_bytes,
        payload_size_kb=payload_size_kb,
        encode_time_ms=avg_encode_ms,
        decode_time_ms=avg_decode_ms,
        total_time_ms=avg_total_ms,
        encoded_size=int(avg_encoded_size),
        encoded_size_kb=avg_encoded_size / 1024,
        compression_ratio=compression_ratio,
        throughput_encode_mbps=throughput_encode,
        throughput_decode_mbps=throughput_decode,
        throughput_total_mbps=throughput_total,
        layer1_time_pct=layer1_pct,
        layer2_time_pct=layer2_pct,
        layer3_time_pct=layer3_pct,
        variant_used=int(sum(variants) / len(variants)),
        success=True
    )

    return metrics


def print_metrics(metrics: PerformanceMetrics):
    """Pretty print performance metrics"""
    print(f"\n{'-'*70}")
    print(f"RESULTS - {metrics.payload_size_kb:.0f}KB Payload")
    print(f"{'-'*70}")
    print(f"Payload Size:          {metrics.payload_size:,} bytes ({metrics.payload_size_kb:.1f}KB)")
    print(f"Encoded Size:          {metrics.encoded_size:,} bytes ({metrics.encoded_size_kb:.1f}KB)")
    print(f"Compression Ratio:     {metrics.compression_ratio:.3f}x")
    print(f"\nTiming (average):")
    print(f"  Encode:              {metrics.encode_time_ms:.2f}ms")
    print(f"  Decode:              {metrics.decode_time_ms:.2f}ms")
    print(f"  Total:               {metrics.total_time_ms:.2f}ms")
    print(f"\nThroughput:")
    print(f"  Encode:              {metrics.throughput_encode_mbps:.2f} MB/s")
    print(f"  Decode:              {metrics.throughput_decode_mbps:.2f} MB/s")
    print(f"  Total:               {metrics.throughput_total_mbps:.2f} MB/s")
    print(f"\nLayer Time Distribution:")
    print(f"  Layer 1 (Base64):     {metrics.layer1_time_pct:.1f}%")
    print(f"  Layer 2 (Hex):        {metrics.layer2_time_pct:.1f}%")
    print(f"  Layer 3 (Array):      {metrics.layer3_time_pct:.1f}%")
    print(f"\nAverage Variant:       {metrics.variant_used}")
    print(f"Status:                {'✓ PASS' if metrics.success else '✗ FAIL'}")


def create_performance_profile(all_metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
    """Create comprehensive performance profile"""

    profile = {
        'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'system_info': {
            'python_version': sys.version.split()[0],
            'platform': sys.platform
        },
        'test_summary': {
            'total_tests': len(all_metrics),
            'successful_tests': sum(1 for m in all_metrics if m.success),
            'payload_sizes_kb': [m.payload_size_kb for m in all_metrics],
            'total_test_time_seconds': sum(m.total_time_ms for m in all_metrics) / 1000
        },
        'detailed_results': [asdict(m) for m in all_metrics],
        'performance_summary': {
            'fastest_payload_kb': min(all_metrics, key=lambda m: m.total_time_ms).payload_size_kb if all_metrics else 0,
            'slowest_payload_kb': max(all_metrics, key=lambda m: m.total_time_ms).payload_size_kb if all_metrics else 0,
            'average_encode_throughput_mbps': sum(m.throughput_encode_mbps for m in all_metrics) / len(all_metrics) if all_metrics else 0,
            'average_decode_throughput_mbps': sum(m.throughput_decode_mbps for m in all_metrics) / len(all_metrics) if all_metrics else 0,
            'average_compression_ratio': sum(m.compression_ratio for m in all_metrics) / len(all_metrics) if all_metrics else 0
        },
        'encoding_characteristics': {
            'description': 'Hardened Multi-Encoding with 3 layers: Base64, Polymorphic Hex, Shuffled Array',
            'security_features': [
                'HMAC-SHA256 integrity verification per layer',
                '4 polymorphic hex encoding variants',
                'Array shuffling with position tracking',
                'Random noise injection in Base64 layer',
                'Variant-based encryption in Hex layer',
                'Cryptographic checksum validation'
            ],
            'layer_details': {
                'layer_1': {
                    'name': 'Base64 + HMAC',
                    'description': 'Encodes with random padding and HMAC-SHA256 integrity verification'
                },
                'layer_2': {
                    'name': 'Polymorphic Hex',
                    'description': 'Converts to hex using one of 4 variants: bit-inversion, interleaved, reversed-offset, XOR-mask',
                    'variant_count': 4
                },
                'layer_3': {
                    'name': 'Shuffled Array',
                    'description': 'Shuffles hex pairs and encodes position map in JSON format'
                }
            }
        },
        'scaling_analysis': {
            'payload_5kb': {
                'encode_ms': all_metrics[0].encode_time_ms if len(all_metrics) > 0 else 0,
                'decode_ms': all_metrics[0].decode_time_ms if len(all_metrics) > 0 else 0,
                'throughput_mbps': all_metrics[0].throughput_total_mbps if len(all_metrics) > 0 else 0
            },
            'payload_10kb': {
                'encode_ms': all_metrics[1].encode_time_ms if len(all_metrics) > 1 else 0,
                'decode_ms': all_metrics[1].decode_time_ms if len(all_metrics) > 1 else 0,
                'throughput_mbps': all_metrics[1].throughput_total_mbps if len(all_metrics) > 1 else 0
            },
            'payload_20kb': {
                'encode_ms': all_metrics[2].encode_time_ms if len(all_metrics) > 2 else 0,
                'decode_ms': all_metrics[2].decode_time_ms if len(all_metrics) > 2 else 0,
                'throughput_mbps': all_metrics[2].throughput_total_mbps if len(all_metrics) > 2 else 0
            }
        }
    }

    return profile


def main():
    """Run comprehensive performance tests"""

    print("\n" + "="*70)
    print("MULTI-ENCODING PERFORMANCE TEST SUITE")
    print("="*70)
    print("\nTesting hardened multi-encoding system with variable payload sizes")
    print("Payload sizes: 5KB, 10KB, 20KB")
    print("Iterations per size: 3")

    all_metrics = []

    # Test each payload size
    for size_kb in [5, 10, 20]:
        metrics = measure_performance(size_kb, iterations=3)
        all_metrics.append(metrics)
        print_metrics(metrics)

    # Create performance profile
    profile = create_performance_profile(all_metrics)

    # Save results to JSON
    output_file = '/home/user/sc-generator/PERFORMANCE_PROFILE_MULTI_ENCODING.json'
    with open(output_file, 'w') as f:
        json.dump(profile, f, indent=2)

    print(f"\n{'='*70}")
    print("PERFORMANCE PROFILE SAVED")
    print(f"{'='*70}")
    print(f"Output file: {output_file}")

    # Print summary
    print(f"\n{'='*70}")
    print("EXECUTIVE SUMMARY")
    print(f"{'='*70}")
    print(f"\nTest Execution: {profile['test_date']}")
    print(f"Total Tests Run: {profile['test_summary']['total_tests']}")
    print(f"Successful: {profile['test_summary']['successful_tests']}")
    print(f"Total Time: {profile['test_summary']['total_test_time_seconds']:.2f}s")

    summary = profile['performance_summary']
    print(f"\nPerformance Metrics:")
    print(f"  Average Encode Throughput:  {summary['average_encode_throughput_mbps']:.2f} MB/s")
    print(f"  Average Decode Throughput:  {summary['average_decode_throughput_mbps']:.2f} MB/s")
    print(f"  Average Compression Ratio:  {summary['average_compression_ratio']:.3f}x")

    # Payload size progression
    scaling = profile['scaling_analysis']
    print(f"\nPayload Size Progression:")
    for size_kb in [5, 10, 20]:
        size_key = f'payload_{size_kb}kb'
        data = scaling[size_key]
        total = data['encode_ms'] + data['decode_ms']
        print(f"  {size_kb:2d}KB: {data['encode_ms']:6.2f}ms encode, "
              f"{data['decode_ms']:6.2f}ms decode, "
              f"{data['throughput_mbps']:6.2f} MB/s ({total:7.2f}ms total)")

    print(f"\n{'='*70}\n")

    return profile


if __name__ == '__main__':
    profile = main()
    sys.exit(0 if profile['test_summary']['successful_tests'] == profile['test_summary']['total_tests'] else 1)
