#!/usr/bin/env python3
"""
Complete example demonstrating Base64 Encoder paired with VBS Decoder.
Shows how the encoder and decoder work together in reverse operations.
"""

from base64_encoder import Base64Encoder, Base64OperationsPair
from vbs_encoder import VBSEncoder, ObfuscationConfig


def example_1_simple_encode_decode():
    """Example 1: Simple encode-decode cycle"""
    print("=" * 70)
    print("EXAMPLE 1: Simple Encode-Decode Cycle")
    print("=" * 70)

    encoder = Base64Encoder()
    original_text = "Reverse Operation Test"

    # Encode with the encoder
    encoded = encoder.encode_to_base64(original_text)
    print(f"Original Text: {original_text}")
    print(f"Encoded (by Base64Encoder): {encoded}")

    # Verify it matches what VBS decoder would receive
    ops = Base64OperationsPair()
    decoded = ops.decode(encoded)
    print(f"Decoded (back to original): {decoded}")
    print(f"Match: {decoded == original_text}\n")


def example_2_command_encoding():
    """Example 2: Encode PowerShell commands"""
    print("=" * 70)
    print("EXAMPLE 2: PowerShell Command Encoding")
    print("=" * 70)

    encoder = Base64Encoder()

    # Standard Base64 encoding for VBS
    command = "powershell.exe -NoProfile -Command \"Get-Process\""
    vbs_encoded = encoder.encode_to_base64(command)
    print(f"Command: {command}")
    print(f"VBS Base64: {vbs_encoded}")

    # PowerShell UTF-16LE encoding
    ps_encoded = encoder.create_powershell_encoded_command(command)
    print(f"PowerShell Encoded: {ps_encoded}\n")


def example_3_vbs_integrated():
    """Example 3: Full VBS integration - Encoder creating payload for decoder"""
    print("=" * 70)
    print("EXAMPLE 3: VBS Encoder-Decoder Integration")
    print("=" * 70)

    # Step 1: Encode the command using Base64Encoder
    encoder = Base64Encoder()
    command = "cmd /c echo Hello from reverse operation"
    encoded_command = encoder.encode_to_base64(command)

    print(f"Step 1 - Encode command:")
    print(f"  Original: {command}")
    print(f"  Encoded: {encoded_command}\n")

    # Step 2: Create VBS decoder that will handle this encoded command
    vbs_encoder = VBSEncoder()
    vbs_decoder_code = vbs_encoder.create_base64_decoder_vbs(
        command, "decoded_payload"
    )

    print(f"Step 2 - VBS Decoder code generated:")
    print(vbs_decoder_code)
    print()


def example_4_vbs_encoded_variable():
    """Example 4: Create VBS variable with encoded value"""
    print("=" * 70)
    print("EXAMPLE 4: VBS Encoded Variable")
    print("=" * 70)

    encoder = Base64Encoder()
    payload = "net user Administrator /active:yes"

    # Create VBS code with encoded variable
    vbs_code = encoder.create_vbs_encoded_variable(payload, "encPayload")
    print(f"Original Payload: {payload}\n")
    print(f"VBS Code (with encoded variable):")
    print(vbs_code)
    print()


def example_5_batch_encoding():
    """Example 5: Batch encode multiple commands"""
    print("=" * 70)
    print("EXAMPLE 5: Batch Encoding Multiple Commands")
    print("=" * 70)

    encoder = Base64Encoder()
    commands = [
        "whoami",
        "ipconfig /all",
        "tasklist",
        "systeminfo"
    ]

    encoded_commands = encoder.batch_encode_multiple(commands)

    print("Batch Encoding Results:")
    print("-" * 70)
    for cmd, encoded in encoded_commands.items():
        print(f"Command: {cmd}")
        print(f"Encoded: {encoded}")
        print()


def example_6_verification():
    """Example 6: Verify encoding correctness"""
    print("=" * 70)
    print("EXAMPLE 6: Encoding Verification")
    print("=" * 70)

    encoder = Base64Encoder()
    ops = Base64OperationsPair()

    test_strings = [
        "Test 1",
        "powershell.exe",
        "cmd /c calc.exe",
        "Complex!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
    ]

    print("Verification Results:")
    print("-" * 70)
    for test in test_strings:
        encoded = encoder.encode_to_base64(test)
        is_valid = encoder.verify_encoding(test, encoded)
        round_trip = ops.round_trip_transform(test)

        print(f"String: {test}")
        print(f"  Verification: {is_valid}")
        print(f"  Round Trip: {round_trip}")
        print()


def example_7_reverse_lookup():
    """Example 7: Create reverse lookup tables"""
    print("=" * 70)
    print("EXAMPLE 7: Reverse Lookup Tables")
    print("=" * 70)

    encoder = Base64Encoder()
    commands = [
        "net user",
        "ipconfig",
        "tasklist",
        "systeminfo"
    ]

    lookup = encoder.create_reverse_lookup_table(commands)

    print("Forward Mapping (Plain -> Encoded):")
    print("-" * 70)
    for plain, encoded in lookup['forward'].items():
        print(f"{plain:20} -> {encoded}")

    print("\nReverse Mapping (Encoded -> Plain):")
    print("-" * 70)
    for encoded, plain in lookup['reverse'].items():
        print(f"{encoded:30} -> {plain}")
    print()


def example_8_bytes_encoding():
    """Example 8: Encode bytes data"""
    print("=" * 70)
    print("EXAMPLE 8: Bytes Encoding")
    print("=" * 70)

    encoder = Base64Encoder()

    # Binary data
    binary_data = b"\x00\x01\x02\x03\x04\x05"
    encoded = encoder.encode_bytes_to_base64(binary_data)

    print(f"Binary Data: {binary_data}")
    print(f"Encoded: {encoded}")
    print()


def example_9_paired_vbs():
    """Example 9: Create paired encoder-decoder VBS code"""
    print("=" * 70)
    print("EXAMPLE 9: Paired Encoder-Decoder VBS Code")
    print("=" * 70)

    encoder = Base64Encoder()
    text = "Test Payload for VBS"

    encoder_code, decoder_code = encoder.create_vbs_decoder_pair(text)

    print(f"Original Text: {text}\n")
    print("Encoder Code (VBS):")
    print("-" * 70)
    print(encoder_code)
    print("\nDecoder Code (VBS):")
    print("-" * 70)
    print(decoder_code)
    print()


def example_10_file_content():
    """Example 10: Encode file content"""
    print("=" * 70)
    print("EXAMPLE 10: File Content Encoding")
    print("=" * 70)

    encoder = Base64Encoder()
    file_content = """@echo off
REM This is a batch script
echo Starting...
pause"""

    encoded = encoder.encode_file_content(file_content)

    print("Original File Content:")
    print("-" * 70)
    print(file_content)
    print("\nEncoded File Content:")
    print("-" * 70)
    print(encoded)
    print()


def main():
    """Run all examples"""
    examples = [
        example_1_simple_encode_decode,
        example_2_command_encoding,
        example_3_vbs_integrated,
        example_4_vbs_encoded_variable,
        example_5_batch_encoding,
        example_6_verification,
        example_7_reverse_lookup,
        example_8_bytes_encoding,
        example_9_paired_vbs,
        example_10_file_content,
    ]

    for example in examples:
        example()


if __name__ == "__main__":
    main()
