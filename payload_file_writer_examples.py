#!/usr/bin/env python3
"""
Real-world examples for Payload File Writer
Demonstrates practical use cases and patterns
"""

import os
import json
from pathlib import Path
from payload_file_writer import (
    PayloadFileWriter,
    FileFormat,
    PayloadMetadata,
    write_payload_to_file,
    write_and_encode_payload
)


# ============================================================================
# EXAMPLE 1: Simple Payload Writing with Cleanup
# ============================================================================

def example_1_simple_write():
    """Basic write-and-cleanup pattern"""
    print("=" * 70)
    print("EXAMPLE 1: Simple Payload Writing")
    print("=" * 70)

    writer = PayloadFileWriter()

    # Define payload
    vbs_payload = """
Dim objWMIService
Set objWMIService = GetObject("winmgmts:")
Dim colItems
Set colItems = objWMIService.ExecQuery("Select * from Win32_Process")
"""

    try:
        # Write payload with high obfuscation
        path, metadata = writer.write_payload(
            vbs_payload,
            file_format=FileFormat.VBS,
            obfuscation_level="high"
        )

        print(f"\n✓ Payload written successfully")
        print(f"  Location: {path}")
        print(f"  File ID: {metadata.file_id}")
        print(f"  Original size: {metadata.original_size} bytes")
        print(f"  Obfuscated size: {metadata.encoded_size} bytes")
        print(f"  Compression ratio: {metadata.compression_ratio:.2f}x")
        print(f"  SHA256 hash: {metadata.sha256_hash[:16]}...")

        # Display first 200 chars of obfuscated code
        with open(path, 'r') as f:
            content = f.read()
        print(f"\n  Obfuscated code (first 200 chars):")
        print(f"  {content[:200]}...")

    finally:
        # Always cleanup
        writer.cleanup_all()
        print(f"\n✓ Cleanup complete")


# ============================================================================
# EXAMPLE 2: Multi-Format Batch Generation
# ============================================================================

def example_2_multi_format_batch():
    """Generate same payload in multiple formats"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multi-Format Batch Generation")
    print("=" * 70)

    base_payload = "powershell.exe -NoProfile -Command Get-Process"

    writers = {
        'vbs': PayloadFileWriter(),
        'bat': PayloadFileWriter(),
        'ps1': PayloadFileWriter()
    }

    formats = {
        'vbs': FileFormat.VBS,
        'bat': FileFormat.BAT,
        'ps1': FileFormat.PS1
    }

    results = {}

    try:
        for format_name, writer in writers.items():
            path, metadata = writer.write_payload(
                base_payload,
                file_format=formats[format_name],
                obfuscation_level="high"
            )

            results[format_name] = {
                'path': path,
                'metadata': metadata
            }

            print(f"\n✓ {format_name.upper()} payload generated")
            print(f"  Path: {path}")
            print(f"  Size: {metadata.encoded_size} bytes")

    finally:
        # Cleanup all
        for writer in writers.values():
            writer.cleanup_all()


# ============================================================================
# EXAMPLE 3: Payload with Encoding and Decoder
# ============================================================================

def example_3_encoded_payload():
    """Generate payload with automatic decoder stub"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Payload with Encoder/Decoder")
    print("=" * 70)

    writer = PayloadFileWriter()

    # Original payload
    payload = 'cmd.exe /c "powershell.exe -NoProfile -Command Write-Host Executed"'

    try:
        # Generate with Base64 encoding
        payload_path, decoder_path, metadata = writer.write_payload_with_decoder(
            payload,
            encoding_type="base64",
            obfuscation_level="high"
        )

        print(f"\n✓ Encoded payload generated")
        print(f"  Payload file: {payload_path}")
        print(f"  Decoder stub: {decoder_path}")
        print(f"  Encoding: {metadata.encoding_type}")
        print(f"  Original size: {metadata.original_size} bytes")
        print(f"  Encoded size: {metadata.encoded_size} bytes")

        # Read and display decoder
        with open(decoder_path, 'r') as f:
            decoder = f.read()

        print(f"\n  Generated decoder VBS code:")
        print(f"  {decoder[:300]}...")

        # Try XOR encoding
        payload_path_xor, decoder_path_xor, meta_xor = writer.write_payload_with_decoder(
            payload,
            encoding_type="xor",
            obfuscation_level="high"
        )

        print(f"\n✓ XOR-encoded payload generated")
        print(f"  Payload file: {payload_path_xor}")
        print(f"  Encoding: XOR with embedded key")
        print(f"  Size overhead: {meta_xor.compression_ratio:.2f}x")

    finally:
        writer.cleanup_all()


# ============================================================================
# EXAMPLE 4: Batch Processing with Error Handling
# ============================================================================

def example_4_batch_with_error_handling():
    """Robust batch processing with error handling"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Batch Processing with Error Handling")
    print("=" * 70)

    writer = PayloadFileWriter()

    # Multiple payloads to process
    payloads = {
        'registry_add': '@echo off\nreg add HKCU\\Software\\Test /v Value /d Data',
        'process_spawn': '@echo off\nstart cmd.exe /c echo launched',
        'network_test': '@echo off\nipconfig /all',
        'task_create': '@echo off\ntasksched /create /tn TestTask /tr cmd.exe',
        'cleanup': '@echo off\ndel %TEMP%\\test.tmp'
    }

    try:
        print(f"\n  Processing {len(payloads)} payloads...")

        # Write all payloads
        results = writer.write_payload_batch(
            payloads,
            file_format=FileFormat.BAT,
            obfuscation_level="high"
        )

        # Summarize results
        successful = []
        failed = []

        for name, (path, metadata) in results.items():
            if path and os.path.exists(path):
                successful.append(name)
                print(f"\n✓ {name}")
                print(f"  Path: {path}")
                print(f"  Size: {metadata.encoded_size} bytes")
            else:
                failed.append(name)
                print(f"\n✗ {name} - Failed to write")

        print(f"\n\nSummary:")
        print(f"  Successful: {len(successful)}/{len(payloads)}")
        print(f"  Failed: {len(failed)}/{len(payloads)}")

    finally:
        writer.cleanup_all()


# ============================================================================
# EXAMPLE 5: Obfuscation Level Comparison
# ============================================================================

def example_5_obfuscation_comparison():
    """Compare different obfuscation levels"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Obfuscation Level Comparison")
    print("=" * 70)

    vbs_code = """
Dim objShell
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd.exe /c powershell.exe -NoProfile", 0, False
Set objShell = Nothing
"""

    writer = PayloadFileWriter()

    results = {}

    try:
        for level in ["low", "medium", "high"]:
            path, metadata = writer.write_payload(
                vbs_code,
                file_format=FileFormat.VBS,
                obfuscation_level=level
            )

            with open(path, 'r') as f:
                content = f.read()

            results[level] = {
                'size': metadata.encoded_size,
                'ratio': metadata.compression_ratio,
                'content_sample': content[:100]
            }

        print("\n  Obfuscation Level Comparison:")
        print(f"  {'Level':<10} {'Size':<10} {'Ratio':<10} {'Sample':<30}")
        print(f"  {'-'*60}")

        for level, data in results.items():
            print(f"  {level:<10} {data['size']:<10} {data['ratio']:<10.2f} {data['content_sample'][:25]:<30}...")

    finally:
        writer.cleanup_all()


# ============================================================================
# EXAMPLE 6: Metadata Export and Archiving
# ============================================================================

def example_6_metadata_export():
    """Export payload metadata for logging and archiving"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Metadata Export and Archiving")
    print("=" * 70)

    writer = PayloadFileWriter()

    # Create sample payloads
    payloads = {
        'payload_1': 'Set shell = CreateObject("WScript.Shell")\nshell.Run "cmd"',
        'payload_2': 'echo batch command',
        'payload_3': 'Write-Host PowerShell'
    }

    formats = [FileFormat.VBS, FileFormat.BAT, FileFormat.PS1]
    metadata_log = []

    try:
        for (name, payload), fmt in zip(payloads.items(), formats):
            path, metadata = writer.write_payload(
                payload,
                file_format=fmt,
                obfuscation_level="high"
            )

            # Export metadata
            json_meta = writer.export_metadata_json(metadata.file_id)
            metadata_log.append(json.loads(json_meta))

            print(f"\n✓ {name} - {fmt.value.upper()}")
            print(f"  ID: {metadata.file_id}")
            print(f"  Size: {metadata.original_size} → {metadata.encoded_size} bytes")

        # Display combined metadata
        print(f"\n\nCombined Metadata Log (JSON):")
        combined = {
            'timestamp': metadata_log[0]['timestamp'],
            'payloads': metadata_log,
            'summary': {
                'total': len(metadata_log),
                'total_original_size': sum(m['original_size'] for m in metadata_log),
                'total_encoded_size': sum(m['encoded_size'] for m in metadata_log)
            }
        }
        print(json.dumps(combined, indent=2))

    finally:
        writer.cleanup_all()


# ============================================================================
# EXAMPLE 7: Format-Specific Obfuscation Demo
# ============================================================================

def example_7_format_obfuscation():
    """Demonstrate format-specific obfuscation techniques"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Format-Specific Obfuscation")
    print("=" * 70)

    writer = PayloadFileWriter()

    # VBS-specific obfuscation
    print("\n1. VBS Obfuscation:")
    vbs_code = "Dim x\nSet x = CreateObject(\"WScript.Shell\")\nx.Run \"cmd\""
    obfuscated_vbs = writer.obfuscate_vbs_payload(vbs_code, "high")
    print(f"   Original: {len(vbs_code)} bytes")
    print(f"   Obfuscated: {len(obfuscated_vbs)} bytes")
    print(f"   Sample: {obfuscated_vbs[:80]}...")

    # BAT-specific obfuscation
    print("\n2. BAT Obfuscation:")
    bat_code = "@echo off\nset myVar=value\necho %myVar%"
    obfuscated_bat = writer.obfuscate_bat_payload(bat_code, "high")
    print(f"   Original: {len(bat_code)} bytes")
    print(f"   Obfuscated: {len(obfuscated_bat)} bytes")
    print(f"   Sample: {obfuscated_bat[:80]}...")

    # PowerShell-specific obfuscation
    print("\n3. PowerShell Obfuscation:")
    ps_code = "Write-Host 'Hello World'"
    obfuscated_ps = writer.obfuscate_powershell(ps_code, "high")
    print(f"   Original: {len(ps_code)} bytes")
    print(f"   Obfuscated: {len(obfuscated_ps)} bytes")
    print(f"   Uses Base64 encoding: {'EncodedCommand' in obfuscated_ps}")
    print(f"   Sample: {obfuscated_ps[:80]}...")


# ============================================================================
# EXAMPLE 8: Integration with Payload Generator
# ============================================================================

def example_8_integration():
    """Show integration with PayloadGenerator"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Integration Pattern")
    print("=" * 70)

    # Simulate payload generation
    def generate_payload(technique):
        """Mock payload generation"""
        return f"Generated payload using {technique} technique"

    writer = PayloadFileWriter()

    techniques = ["base64", "hex", "array", "wmi"]

    try:
        print(f"\n  Generating payloads for multiple techniques:")

        for technique in techniques:
            # Generate payload
            payload = generate_payload(technique)

            # Write to file
            path, metadata = writer.write_payload(
                payload,
                file_format=FileFormat.VBS,
                obfuscation_level="high"
            )

            print(f"\n✓ Technique: {technique}")
            print(f"  File ID: {metadata.file_id}")
            print(f"  Path: {path}")
            print(f"  Size: {metadata.encoded_size} bytes")

    finally:
        writer.cleanup_all()


# ============================================================================
# EXAMPLE 9: Streaming Cleanup for Memory Efficiency
# ============================================================================

def example_9_memory_efficient():
    """Memory-efficient batch processing with streaming cleanup"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Memory-Efficient Processing")
    print("=" * 70)

    writer = PayloadFileWriter()
    batch_size = 3
    total_payloads = 10

    print(f"\n  Processing {total_payloads} payloads in batches of {batch_size}...")

    try:
        for batch_num in range(0, total_payloads, batch_size):
            batch_end = min(batch_num + batch_size, total_payloads)
            batch = {
                f"payload_{i}": f"echo test {i}"
                for i in range(batch_num, batch_end)
            }

            # Write batch
            results = writer.write_payload_batch(batch, FileFormat.BAT, "high")

            print(f"\n  Batch {batch_num // batch_size + 1}:")
            for name, (path, metadata) in results.items():
                if path:
                    print(f"    ✓ {name} ({metadata.encoded_size} bytes)")

            # Cleanup immediately to free memory
            count = writer.cleanup_all()
            print(f"    Cleaned up {count} files")

    except Exception as e:
        print(f"  Error: {e}")
        writer.cleanup_all()


# ============================================================================
# EXAMPLE 10: Advanced Encoding Chain
# ============================================================================

def example_10_encoding_chain():
    """Demonstrate encoding method chaining"""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: Encoding Method Comparison")
    print("=" * 70)

    payload = "powershell.exe -NoProfile -Command [System.Diagnostics.Process]::Start('cmd.exe')"
    writer = PayloadFileWriter()

    encodings = ["base64", "hex", "xor"]

    try:
        print(f"\n  Original payload: {len(payload)} bytes")
        print(f"  Content: {payload[:50]}...")

        print(f"\n  {'Encoding':<15} {'Size':<10} {'Ratio':<10} {'Type':<20}")
        print(f"  {'-'*55}")

        for encoding in encodings:
            path, metadata = writer.write_payload(
                payload,
                encoding_type=encoding,
                obfuscation_level="high"
            )

            print(f"  {encoding:<15} {metadata.encoded_size:<10} {metadata.compression_ratio:<10.2f} VBS")

    finally:
        writer.cleanup_all()


# ============================================================================
# Main
# ============================================================================

def main():
    """Run all examples"""
    print("\n")
    print("*" * 70)
    print("* Payload File Writer - Real-World Examples")
    print("*" * 70)

    examples = [
        ("Simple Write", example_1_simple_write),
        ("Multi-Format Batch", example_2_multi_format_batch),
        ("Encoded Payload", example_3_encoded_payload),
        ("Batch with Error Handling", example_4_batch_with_error_handling),
        ("Obfuscation Comparison", example_5_obfuscation_comparison),
        ("Metadata Export", example_6_metadata_export),
        ("Format-Specific Obfuscation", example_7_format_obfuscation),
        ("Integration Pattern", example_8_integration),
        ("Memory Efficient", example_9_memory_efficient),
        ("Encoding Comparison", example_10_encoding_chain),
    ]

    for i, (name, example_func) in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n✗ Error in {name}: {e}")

    print("\n" + "*" * 70)
    print("* All examples completed!")
    print("*" * 70 + "\n")


if __name__ == "__main__":
    main()
