#!/usr/bin/env python3
"""
WMI Registry Access Examples
Comprehensive examples demonstrating registry read/write operations via WMI
"""

from wmi_registry_access import (
    create_registry_accessor, RegistryConfig,
    read_registry, write_registry
)


def example_1_read_hklm_string():
    """Example 1: Read string value from HKLM"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Read String Value from HKLM")
    print("="*80)

    accessor = create_registry_accessor()
    code = accessor.read_registry_value(
        "HKLM",
        "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
        "CurrentVersion"
    )

    print("\nRegistry Path: HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion")
    print("Value Name: CurrentVersion")
    print("\nGenerated VBS Code:")
    print(code)


def example_2_read_hkcu_string():
    """Example 2: Read string value from HKCU"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Read String Value from HKCU")
    print("="*80)

    accessor = create_registry_accessor()
    code = accessor.read_registry_value(
        "HKCU",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer",
        "Shell Folders"
    )

    print("\nRegistry Path: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer")
    print("Value Name: Shell Folders")
    print("\nGenerated VBS Code:")
    print(code)


def example_3_read_dword():
    """Example 3: Read DWORD value"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Read DWORD Value from HKCU")
    print("="*80)

    accessor = create_registry_accessor()
    code = accessor.read_registry_dword(
        "HKCU",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer",
        "NoViewOnDrive"
    )

    print("\nRegistry Path: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer")
    print("Value Name: NoViewOnDrive")
    print("Type: DWORD")
    print("\nGenerated VBS Code:")
    print(code)


def example_4_read_binary():
    """Example 4: Read binary value"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Read Binary Value from HKCU")
    print("="*80)

    accessor = create_registry_accessor()
    code = accessor.read_registry_binary(
        "HKCU",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "DisplayName"
    )

    print("\nRegistry Path: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run")
    print("Value Name: DisplayName")
    print("Type: Binary")
    print("\nGenerated VBS Code:")
    print(code)


def example_5_write_string_hkcu():
    """Example 5: Write string value to HKCU"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Write String Value to HKCU")
    print("="*80)

    accessor = create_registry_accessor()
    code = accessor.write_registry_value(
        "HKCU",
        "Software\\MyApp",
        "AppName",
        "My Application"
    )

    print("\nRegistry Path: HKCU\\Software\\MyApp")
    print("Value Name: AppName")
    print("Value Data: My Application")
    print("\nGenerated VBS Code:")
    print(code)


def example_6_write_dword_hkcu():
    """Example 6: Write DWORD value to HKCU"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Write DWORD Value to HKCU")
    print("="*80)

    accessor = create_registry_accessor()
    code = accessor.write_registry_dword(
        "HKCU",
        "Software\\MyApp\\Settings",
        "Timeout",
        30000
    )

    print("\nRegistry Path: HKCU\\Software\\MyApp\\Settings")
    print("Value Name: Timeout")
    print("Value Data: 30000 (DWORD)")
    print("\nGenerated VBS Code:")
    print(code)


def example_7_write_binary():
    """Example 7: Write binary value"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Write Binary Value to HKCU")
    print("="*80)

    accessor = create_registry_accessor()
    # Hex string for "Hello"
    hex_data = "48656C6C6F"
    code = accessor.write_registry_binary(
        "HKCU",
        "Software\\MyApp",
        "BinaryData",
        hex_data
    )

    print("\nRegistry Path: HKCU\\Software\\MyApp")
    print("Value Name: BinaryData")
    print("Value Data (Hex): 48656C6C6F")
    print("\nGenerated VBS Code:")
    print(code)


def example_8_delete_value():
    """Example 8: Delete registry value"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Delete Registry Value")
    print("="*80)

    accessor = create_registry_accessor()
    code = accessor.delete_registry_value(
        "HKCU",
        "Software\\MyApp",
        "AppName"
    )

    print("\nRegistry Path: HKCU\\Software\\MyApp")
    print("Value Name: AppName (to be deleted)")
    print("\nGenerated VBS Code:")
    print(code)


def example_9_enum_keys():
    """Example 9: Enumerate registry keys"""
    print("\n" + "="*80)
    print("EXAMPLE 9: Enumerate Registry Keys")
    print("="*80)

    accessor = create_registry_accessor()
    code = accessor.enum_registry_keys(
        "HKLM",
        "SOFTWARE\\Microsoft"
    )

    print("\nRegistry Path: HKLM\\SOFTWARE\\Microsoft")
    print("Operation: Enumerate subkeys")
    print("\nGenerated VBS Code:")
    print(code)


def example_10_enum_values():
    """Example 10: Enumerate registry values"""
    print("\n" + "="*80)
    print("EXAMPLE 10: Enumerate Registry Values")
    print("="*80)

    accessor = create_registry_accessor()
    code = accessor.enum_registry_values(
        "HKLM",
        "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion"
    )

    print("\nRegistry Path: HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion")
    print("Operation: Enumerate values in key")
    print("\nGenerated VBS Code:")
    print(code)


def example_11_create_key():
    """Example 11: Create registry key"""
    print("\n" + "="*80)
    print("EXAMPLE 11: Create Registry Key")
    print("="*80)

    accessor = create_registry_accessor()
    code = accessor.create_registry_key(
        "HKCU",
        "Software\\MyApp\\SubKey"
    )

    print("\nRegistry Path: HKCU\\Software\\MyApp\\SubKey")
    print("Operation: Create key")
    print("\nGenerated VBS Code:")
    print(code)


def example_12_delete_key():
    """Example 12: Delete registry key"""
    print("\n" + "="*80)
    print("EXAMPLE 12: Delete Registry Key")
    print("="*80)

    accessor = create_registry_accessor()
    code = accessor.delete_registry_key(
        "HKCU",
        "Software\\MyApp\\SubKey"
    )

    print("\nRegistry Path: HKCU\\Software\\MyApp\\SubKey")
    print("Operation: Delete key")
    print("\nGenerated VBS Code:")
    print(code)


def example_13_check_key_exists():
    """Example 13: Check if key exists"""
    print("\n" + "="*80)
    print("EXAMPLE 13: Check Registry Key Exists")
    print("="*80)

    accessor = create_registry_accessor()
    code = accessor.check_registry_key_exists(
        "HKLM",
        "SOFTWARE\\Microsoft\\Windows"
    )

    print("\nRegistry Path: HKLM\\SOFTWARE\\Microsoft\\Windows")
    print("Operation: Check if key exists")
    print("\nGenerated VBS Code:")
    print(code)


def example_14_high_level_read():
    """Example 14: High-level read function"""
    print("\n" + "="*80)
    print("EXAMPLE 14: High-Level Read Function")
    print("="*80)

    # Read string
    code1 = read_registry("HKLM", "SOFTWARE", "TestValue", "string")
    print("\n[1] Read String:")
    print(code1[:200] + "...")

    # Read DWORD
    code2 = read_registry("HKCU", "SOFTWARE", "TestDWORD", "dword")
    print("\n[2] Read DWORD:")
    print(code2[:200] + "...")

    # Read Binary
    code3 = read_registry("HKCU", "SOFTWARE", "TestBinary", "binary")
    print("\n[3] Read Binary:")
    print(code3[:200] + "...")


def example_15_high_level_write():
    """Example 15: High-level write function"""
    print("\n" + "="*80)
    print("EXAMPLE 15: High-Level Write Function")
    print("="*80)

    # Write string
    code1 = write_registry("HKCU", "SOFTWARE\\MyApp", "AppData", "data", "string")
    print("\n[1] Write String:")
    print(code1[:200] + "...")

    # Write DWORD
    code2 = write_registry("HKCU", "SOFTWARE\\MyApp", "Counter", "1000", "dword")
    print("\n[2] Write DWORD:")
    print(code2[:200] + "...")

    # Write Binary
    code3 = write_registry("HKCU", "SOFTWARE\\MyApp", "BinData", "DEADBEEF", "binary")
    print("\n[3] Write Binary:")
    print(code3[:200] + "...")


def example_16_obfuscated_config():
    """Example 16: Use obfuscated variable names"""
    print("\n" + "="*80)
    print("EXAMPLE 16: Obfuscated Configuration")
    print("="*80)

    config = RegistryConfig(obfuscate_names=True, hide_errors=True)
    accessor = create_registry_accessor(config)

    code = accessor.read_registry_value(
        "HKLM",
        "SOFTWARE",
        "TestValue"
    )

    print("\nConfiguration:")
    print("  Obfuscate Names: True")
    print("  Hide Errors: True")
    print("\nGenerated VBS Code (with obfuscated variable names):")
    print(code)


def example_17_no_obfuscation():
    """Example 17: Use clean variable names (no obfuscation)"""
    print("\n" + "="*80)
    print("EXAMPLE 17: Clean Configuration (No Obfuscation)")
    print("="*80)

    config = RegistryConfig(obfuscate_names=False, hide_errors=False)
    accessor = create_registry_accessor(config)

    code = accessor.write_registry_value(
        "HKCU",
        "SOFTWARE\\Test",
        "Value",
        "Data"
    )

    print("\nConfiguration:")
    print("  Obfuscate Names: False")
    print("  Hide Errors: False")
    print("\nGenerated VBS Code (with clean variable names):")
    print(code)


def example_18_complete_workflow():
    """Example 18: Complete workflow - create, write, read, delete"""
    print("\n" + "="*80)
    print("EXAMPLE 18: Complete Registry Workflow")
    print("="*80)

    accessor = create_registry_accessor()

    print("\n[STEP 1] Create Registry Key")
    print("-" * 80)
    create_code = accessor.create_registry_key("HKCU", "SOFTWARE\\MyApp")
    print(create_code[:150] + "...")

    print("\n[STEP 2] Write String Value")
    print("-" * 80)
    write_code = accessor.write_registry_value(
        "HKCU", "SOFTWARE\\MyApp", "AppVersion", "1.0.0"
    )
    print(write_code[:150] + "...")

    print("\n[STEP 3] Write DWORD Value")
    print("-" * 80)
    dword_code = accessor.write_registry_dword(
        "HKCU", "SOFTWARE\\MyApp", "BuildNumber", 1001
    )
    print(dword_code[:150] + "...")

    print("\n[STEP 4] Read String Value")
    print("-" * 80)
    read_code = accessor.read_registry_value(
        "HKCU", "SOFTWARE\\MyApp", "AppVersion"
    )
    print(read_code[:150] + "...")

    print("\n[STEP 5] Enumerate Keys")
    print("-" * 80)
    enum_code = accessor.enum_registry_keys("HKCU", "SOFTWARE")
    print(enum_code[:150] + "...")

    print("\n[STEP 6] Delete Key")
    print("-" * 80)
    delete_code = accessor.delete_registry_key("HKCU", "SOFTWARE\\MyApp")
    print(delete_code[:150] + "...")


def example_19_methods_report():
    """Example 19: Registry access methods report"""
    print("\n" + "="*80)
    print("EXAMPLE 19: Registry Access Methods Report")
    print("="*80)

    accessor = create_registry_accessor()
    report = accessor.get_registry_methods_report()

    for method_key, method_info in report.items():
        print(f"\n{method_info['name']}")
        print(f"  Description: {method_info['description']}")
        print(f"  Code Length: {len(method_info['code'])} chars")


def example_20_batch_operations():
    """Example 20: Batch registry operations"""
    print("\n" + "="*80)
    print("EXAMPLE 20: Batch Registry Operations")
    print("="*80)

    accessor = create_registry_accessor()

    operations = [
        ("Read Version", accessor.read_registry_value,
         ("HKLM", "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", "CurrentVersion")),
        ("Read ProductName", accessor.read_registry_value,
         ("HKLM", "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", "ProductName")),
        ("Write TestValue", accessor.write_registry_value,
         ("HKCU", "SOFTWARE\\Test", "TestKey", "TestValue")),
        ("Read TestValue", accessor.read_registry_value,
         ("HKCU", "SOFTWARE\\Test", "TestKey")),
    ]

    print("\nBatch Operations:\n")

    for i, (name, func, args) in enumerate(operations, 1):
        code = func(*args)
        print(f"[{i}] {name}")
        print(f"    Code Length: {len(code)} chars")
        print()


def run_all_examples():
    """Run all examples"""
    examples = [
        example_1_read_hklm_string,
        example_2_read_hkcu_string,
        example_3_read_dword,
        example_4_read_binary,
        example_5_write_string_hkcu,
        example_6_write_dword_hkcu,
        example_7_write_binary,
        example_8_delete_value,
        example_9_enum_keys,
        example_10_enum_values,
        example_11_create_key,
        example_12_delete_key,
        example_13_check_key_exists,
        example_14_high_level_read,
        example_15_high_level_write,
        example_16_obfuscated_config,
        example_17_no_obfuscation,
        example_18_complete_workflow,
        example_19_methods_report,
        example_20_batch_operations,
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {example_func.__name__}: {e}")

    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example_num = int(sys.argv[1])
        examples = [
            example_1_read_hklm_string,
            example_2_read_hkcu_string,
            example_3_read_dword,
            example_4_read_binary,
            example_5_write_string_hkcu,
            example_6_write_dword_hkcu,
            example_7_write_binary,
            example_8_delete_value,
            example_9_enum_keys,
            example_10_enum_values,
            example_11_create_key,
            example_12_delete_key,
            example_13_check_key_exists,
            example_14_high_level_read,
            example_15_high_level_write,
            example_16_obfuscated_config,
            example_17_no_obfuscation,
            example_18_complete_workflow,
            example_19_methods_report,
            example_20_batch_operations,
        ]
        if 1 <= example_num <= len(examples):
            examples[example_num - 1]()
        else:
            print(f"Example {example_num} not found. Choose 1-{len(examples)}")
    else:
        run_all_examples()
