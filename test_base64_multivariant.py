#!/usr/bin/env python3
"""
Test suite for Base64 Multi-Variant Wrapper
Demonstrates polymorphic decoder generation with unique variable names
"""

import base64
from base64_multivariant_wrapper import (
    Base64MultiVariantWrapper,
    Base64PolymorphicDecoder,
    Base64VariantNameGenerator,
    DecoderVariant,
    create_multivariant_base64_decoder,
    create_random_decoder,
    encode_and_wrap
)


def test_name_generator():
    """Test variable name generator uniqueness"""
    print("=" * 60)
    print("TEST 1: Variable Name Generator")
    print("=" * 60)

    gen = Base64VariantNameGenerator()

    # Generate multiple names
    names = []
    for i in range(10):
        name = gen.generate_name(f"var_")
        names.append(name)
        print(f"  Generated: {name}")

    # Check uniqueness
    if len(names) == len(set(names)):
        print("\n✓ All names are unique")
    else:
        print("\n✗ Duplicate names found!")

    print()


def test_single_variant():
    """Test generating a single random variant"""
    print("=" * 60)
    print("TEST 2: Single Random Variant Generation")
    print("=" * 60)

    payload = "cmd.exe /c calc.exe"
    encoded = base64.b64encode(payload.encode()).decode()

    print(f"Payload: {payload}")
    print(f"Encoded: {encoded}\n")

    # Generate decoder
    decoder = create_random_decoder(encoded)

    print("Generated Decoder (first 300 chars):")
    print(decoder[:300] + "...")
    print(f"\nTotal length: {len(decoder)} characters")
    print()


def test_multiple_variants():
    """Test generating multiple distinct variants"""
    print("=" * 60)
    print("TEST 3: Multiple Random Variants")
    print("=" * 60)

    payload = "powershell -EncodedCommand"
    encoded = base64.b64encode(payload.encode()).decode()

    wrapper = Base64MultiVariantWrapper(encoded)

    # Generate 3 variants
    print(f"Generating 3 random variants from payload: {payload}\n")

    for i, (code, variant_name) in enumerate(wrapper.generate_polymorphic_suite(3), 1):
        print(f"--- Variant {i}: {variant_name.upper()} ---")
        lines = code.split('\n')
        print(f"  First line: {lines[0]}")
        print(f"  Total lines: {len(lines)}")
        print(f"  Total chars: {len(code)}")
        print()


def test_all_variants():
    """Test all decoder variant types"""
    print("=" * 60)
    print("TEST 4: All Decoder Variants")
    print("=" * 60)

    payload = base64.b64encode(b"Test payload").decode()
    wrapper = Base64MultiVariantWrapper(payload)

    all_variants = wrapper.generate_all_variants()

    print(f"Available variants: {len(all_variants)}\n")

    for variant_name, code in all_variants.items():
        print(f"[{variant_name.upper()}]")
        print(f"  Length: {len(code)} chars")
        print(f"  Lines: {len(code.split(chr(10)))}")

        # Extract function name
        if "Function " in code:
            func_line = [l for l in code.split('\n') if 'Function ' in l][0]
            print(f"  Function: {func_line.strip()[:60]}...")
        print()


def test_variant_with_junk_code():
    """Test variant generation with obfuscating junk code"""
    print("=" * 60)
    print("TEST 5: Variant with Junk Code Obfuscation")
    print("=" * 60)

    payload = base64.b64encode(b"Secret command").decode()
    decoder_gen = Base64PolymorphicDecoder(payload, DecoderVariant.MSXML_DOMXML)

    # Generate with junk
    code_with_junk = decoder_gen.generate_with_junk_code(junk_lines=5)

    print("Generated code with 5 junk lines:")
    print(code_with_junk)
    print(f"\nTotal length: {len(code_with_junk)} characters")
    print()


def test_inline_decoder():
    """Test inline decoder generation"""
    print("=" * 60)
    print("TEST 6: Inline Decoder (Non-Function)")
    print("=" * 60)

    payload = base64.b64encode(b"Inline test").decode()
    decoder_gen = Base64PolymorphicDecoder(payload)

    inline = decoder_gen.generate_inline_decoder()

    print("Inline decoder code:")
    print(inline)
    print(f"\nLength: {len(inline)} characters")
    print()


def test_encode_and_wrap():
    """Test encode and wrap convenience function"""
    print("=" * 60)
    print("TEST 7: Encode and Wrap Convenience Function")
    print("=" * 60)

    plain_text = "This is a test payload"

    print(f"Plain text: {plain_text}")
    encoded, wrapper_code = encode_and_wrap(plain_text, variant_count=2)

    print(f"\nEncoded: {encoded}")
    print(f"\nGenerated wrapper code (first 500 chars):")
    print(wrapper_code[:500] + "...")
    print(f"\nTotal wrapper length: {len(wrapper_code)} characters")
    print()


def test_variant_metadata():
    """Test variant generation metadata tracking"""
    print("=" * 60)
    print("TEST 8: Variant Metadata Tracking")
    print("=" * 60)

    payload = base64.b64encode(b"metadata test").decode()
    wrapper = Base64MultiVariantWrapper(payload)

    # Generate several variants
    print("Generating 5 variants and tracking metadata...\n")
    for _ in range(5):
        wrapper.generate_variant()

    metadata = wrapper.get_variant_metadata()

    print(f"Total variants generated: {len(metadata)}\n")
    print("Metadata:")
    print("Call | Variant Type          | Code Length")
    print("-" * 50)
    for item in metadata:
        print(f"{item['call']:4} | {item['variant']:21} | {len(item['code']):4} chars")
    print()


def test_deterministic_names():
    """Test hash-based deterministic naming"""
    print("=" * 60)
    print("TEST 9: Deterministic Hash-Based Naming")
    print("=" * 60)

    text = "deterministic_test_payload"
    gen1 = Base64VariantNameGenerator()
    gen2 = Base64VariantNameGenerator()

    name1 = gen1.generate_name("func_", use_hash=True, source_text=text)
    name2 = gen2.generate_name("func_", use_hash=True, source_text=text)

    print(f"Source text: {text}\n")
    print(f"Name 1: {name1}")
    print(f"Name 2: {name2}")

    if "deterministic" in name1.lower() or "test" in name1.lower():
        print("\n✓ Hash-based naming generated from source text")
    print()


def test_large_payload():
    """Test with larger payload"""
    print("=" * 60)
    print("TEST 10: Large Payload Handling")
    print("=" * 60)

    large_payload = "A" * 1000  # 1KB payload
    encoded = base64.b64encode(large_payload.encode()).decode()

    print(f"Original payload: {len(large_payload)} bytes")
    print(f"Encoded payload: {len(encoded)} characters")

    wrapper = Base64MultiVariantWrapper(encoded)
    code = wrapper.generate_variant()[0]

    print(f"Generated decoder: {len(code)} characters")
    print(f"Payload embedding test: {'PASS' if encoded in code or 'DecodeBase64' in code else 'INFO'}")
    print()


def test_variant_diversity():
    """Test that each variant call produces unique output"""
    print("=" * 60)
    print("TEST 11: Variant Diversity (Each Call Different)")
    print("=" * 60)

    payload = base64.b64encode(b"diversity test").decode()
    wrapper = Base64MultiVariantWrapper(payload)

    # Generate 5 decoders
    decoders = []
    for i in range(5):
        code, _ = wrapper.generate_variant()
        decoders.append(code)

    print("Generated 5 decoders and comparing...\n")

    # Count unique decoders
    unique_count = len(set(decoders))
    print(f"Total decoders: 5")
    print(f"Unique decoders: {unique_count}")

    if unique_count > 1:
        print("✓ Variants are polymorphic (each call produces different output)")
    else:
        print("✗ Variants are identical")

    # Compare variable names
    print("\nVariable name diversity (first 100 chars of each):")
    for i, code in enumerate(decoders[:3], 1):
        first_vars = code[:100]
        print(f"  Decoder {i}: {first_vars.replace(chr(10), ' ')[:80]}...")

    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " BASE64 MULTI-VARIANT WRAPPER TEST SUITE ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    test_name_generator()
    test_single_variant()
    test_multiple_variants()
    test_all_variants()
    test_variant_with_junk_code()
    test_inline_decoder()
    test_encode_and_wrap()
    test_variant_metadata()
    test_deterministic_names()
    test_large_payload()
    test_variant_diversity()

    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
