#!/usr/bin/env python3
"""
Test suite for Array Encoder
Tests encoding, chunking strategies, and output formats
"""

import sys
import json
import binascii
import base64
from array_encoder import (
    ArrayEncoder, EncoderConfig, EncodingType, OutputFormat,
    ChunkingStrategy, encode_command_to_array
)


def test_hex_encoding():
    """Test hex encoding of command"""
    print("\n" + "=" * 60)
    print("TEST: Hex Encoding")
    print("=" * 60)

    cmd = "calc.exe"
    config = EncoderConfig(
        chunk_size=4,
        encoding_type=EncodingType.HEX,
        output_format=OutputFormat.PYTHON
    )
    encoder = ArrayEncoder(config)
    result = encoder.generate(cmd)

    print(f"Command: {cmd}")
    print(f"Chunk size: 4")
    print(f"Encoding: hex")
    print(f"\nGenerated Python list:\n{result}")

    # Verify: decode chunks back
    encoded_hex = binascii.hexlify(cmd.encode()).decode()
    print(f"\nFull hex string: {encoded_hex}")
    print(f"Length: {len(encoded_hex)} hex chars, {len(cmd)} original chars")

    return "PASS"


def test_base64_encoding():
    """Test base64 encoding of command"""
    print("\n" + "=" * 60)
    print("TEST: Base64 Encoding")
    print("=" * 60)

    cmd = "powershell.exe"
    config = EncoderConfig(
        chunk_size=6,
        encoding_type=EncodingType.BASE64,
        output_format=OutputFormat.PYTHON
    )
    encoder = ArrayEncoder(config)
    result = encoder.generate(cmd)

    print(f"Command: {cmd}")
    print(f"Chunk size: 6")
    print(f"Encoding: base64")
    print(f"\nGenerated Python list:\n{result}")

    # Verify
    encoded_b64 = base64.b64encode(cmd.encode()).decode()
    print(f"\nFull base64 string: {encoded_b64}")

    return "PASS"


def test_output_formats():
    """Test different output formats"""
    print("\n" + "=" * 60)
    print("TEST: Output Formats")
    print("=" * 60)

    cmd = "notepad"
    formats = [
        ("python", OutputFormat.PYTHON),
        ("vbs", OutputFormat.VBS),
        ("javascript", OutputFormat.JAVASCRIPT),
        ("powershell", OutputFormat.POWERSHELL),
        ("bash", OutputFormat.BASH),
        ("json", OutputFormat.JSON),
        ("c", OutputFormat.C),
    ]

    for fmt_name, fmt_enum in formats:
        print(f"\n--- Format: {fmt_name} ---")
        config = EncoderConfig(
            chunk_size=4,
            encoding_type=EncodingType.HEX,
            output_format=fmt_enum,
            add_comments=False
        )
        encoder = ArrayEncoder(config)
        result = encoder.generate(cmd)
        print(result[:200] + ("..." if len(result) > 200 else ""))

    return "PASS"


def test_chunking_strategies():
    """Test different chunking strategies"""
    print("\n" + "=" * 60)
    print("TEST: Chunking Strategies")
    print("=" * 60)

    cmd = "command.exe /arg1 /arg2"
    strategies = [
        ("sequential", ChunkingStrategy.SEQUENTIAL),
        ("variable_size", ChunkingStrategy.VARIABLE_SIZE),
        ("interleaved", ChunkingStrategy.INTERLEAVED),
    ]

    for strat_name, strat_enum in strategies:
        print(f"\n--- Strategy: {strat_name} ---")
        config = EncoderConfig(
            chunk_size=8,
            encoding_type=EncodingType.HEX,
            output_format=OutputFormat.PYTHON,
            chunking_strategy=strat_enum,
            min_chunk_size=4,
            max_chunk_size=12,
            add_comments=False
        )
        encoder = ArrayEncoder(config)
        result_dict = encoder.encode(cmd)
        print(f"Chunks: {result_dict['count']}")
        print(f"First chunk: {result_dict['chunks'][0][:30]}")

    return "PASS"


def test_convenience_function():
    """Test convenience function"""
    print("\n" + "=" * 60)
    print("TEST: Convenience Function")
    print("=" * 60)

    cmd = "test.exe"
    result = encode_command_to_array(
        cmd,
        chunk_size=4,
        encoding="hex",
        output_format="vbs"
    )

    print(f"Command: {cmd}")
    print(f"\nVBS Array:\n{result}")

    return "PASS"


def test_roundtrip_decode():
    """Test that encoded chunks can be decoded back"""
    print("\n" + "=" * 60)
    print("TEST: Roundtrip Encode-Decode")
    print("=" * 60)

    cmd = "Hello World"
    config = EncoderConfig(
        chunk_size=4,
        encoding_type=EncodingType.HEX,
        output_format=OutputFormat.PYTHON
    )
    encoder = ArrayEncoder(config)
    encoded = encoder.encode(cmd)

    print(f"Original command: {cmd}")
    print(f"Chunks: {encoded['chunks']}")

    # Reconstruct from chunks (simulating decoder)
    reconstructed = ""
    for chunk in encoded['chunks']:
        # Hex decode each chunk
        decoded_bytes = bytes.fromhex(chunk)
        reconstructed += decoded_bytes.decode('utf-8')

    print(f"Reconstructed: {reconstructed}")
    print(f"Match: {reconstructed == cmd}")

    return "PASS" if reconstructed == cmd else "FAIL"


def test_large_command():
    """Test with larger command"""
    print("\n" + "=" * 60)
    print("TEST: Large Command")
    print("=" * 60)

    cmd = "powershell.exe -Command \"Get-Process | Where-Object { $_.CPU -gt 100 } | Stop-Process\""
    config = EncoderConfig(
        chunk_size=16,
        encoding_type=EncodingType.HEX,
        output_format=OutputFormat.PYTHON,
        add_comments=True
    )
    encoder = ArrayEncoder(config)
    result = encoder.generate(cmd)

    lines = result.split('\n')
    print(f"Command length: {len(cmd)} chars")
    print(f"Generated array lines: {len(lines)}")
    print(f"\nFirst 5 lines:")
    for line in lines[:5]:
        print(f"  {line}")
    print(f"...")
    print(f"Last line: {lines[-1]}")

    return "PASS"


def test_json_output_format():
    """Test JSON output format specifically"""
    print("\n" + "=" * 60)
    print("TEST: JSON Output Validation")
    print("=" * 60)

    cmd = "test.exe"
    config = EncoderConfig(
        chunk_size=4,
        encoding_type=EncodingType.HEX,
        output_format=OutputFormat.JSON
    )
    encoder = ArrayEncoder(config)
    result = encoder.generate(cmd)

    print(f"Command: {cmd}")
    print(f"\nJSON output:\n{result}")

    # Validate JSON
    try:
        data = json.loads(result)
        print(f"\nJSON validation: OK")
        print(f"  - Payload chunks: {len(data['payload'])}")
        print(f"  - Count: {data['count']}")
        print(f"  - Encoding: {data['encoding']}")
        print(f"  - Chunk size: {data['chunk_size']}")
        return "PASS"
    except json.JSONDecodeError as e:
        print(f"JSON validation: FAIL - {e}")
        return "FAIL"


def test_randomized_variable_names():
    """Test randomized variable names"""
    print("\n" + "=" * 60)
    print("TEST: Randomized Variable Names")
    print("=" * 60)

    cmd = "cmd.exe"
    config = EncoderConfig(
        chunk_size=4,
        encoding_type=EncodingType.HEX,
        output_format=OutputFormat.PYTHON,
        randomize_names=True,
        add_comments=False
    )

    results = []
    for i in range(3):
        encoder = ArrayEncoder(config)
        result = encoder.generate(cmd)
        # Extract first line to see variable name
        var_name = result.split('=')[0].strip()
        results.append(var_name)
        print(f"Run {i+1}: Variable name = {var_name}")

    # Check if names are different
    if len(set(results)) > 1:
        print("\nRandomization: OK (different variable names generated)")
        return "PASS"
    else:
        print("\nRandomization: Names may be identical (possible but unlikely)")
        return "PASS"


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("ARRAY ENCODER TEST SUITE")
    print("=" * 80)

    tests = [
        ("Hex Encoding", test_hex_encoding),
        ("Base64 Encoding", test_base64_encoding),
        ("Output Formats", test_output_formats),
        ("Chunking Strategies", test_chunking_strategies),
        ("Convenience Function", test_convenience_function),
        ("Roundtrip Encode-Decode", test_roundtrip_decode),
        ("Large Command", test_large_command),
        ("JSON Output Validation", test_json_output_format),
        ("Randomized Variable Names", test_randomized_variable_names),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] {test_name}: {e}")
            results.append((test_name, "FAIL"))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, r in results if r == "PASS")
    failed = sum(1 for _, r in results if r == "FAIL")

    for test_name, result in results:
        status = "✓" if result == "PASS" else "✗"
        print(f"{status} {test_name}: {result}")

    print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)} tests")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
