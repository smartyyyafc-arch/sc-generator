#!/usr/bin/env python3
"""
Comprehensive examples of polymorphic array wrapper usage
Demonstrates various configurations and customizations
"""

from array_polymorphic_random_chunks import (
    ArrayPolymorphicRandomChunks,
    PolymorphicConfig,
    PolymorphicStrategy
)


def example_basic_usage():
    """Basic usage example"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Polymorphic Wrapper")
    print("="*80 + "\n")

    generator = ArrayPolymorphicRandomChunks()
    payload = "powershell.exe -NoProfile -Command Write-Host Success"

    # Basic configuration
    config = PolymorphicConfig()
    code = generator.generate_polymorphic_wrapper(payload, config)

    print("Configuration:")
    print(f"  - Payload: {payload}")
    print(f"  - Chunk Size: {config.chunk_size}")
    print(f"  - Randomize Order: {config.randomize_order}")
    print(f"  - Multiple Strategies: {config.use_multiple_strategies}")
    print(f"  - Add Junk Code: {config.add_junk_code}")

    print(f"\nGenerated Code ({len(code)} bytes):")
    print("-"*80)
    lines = code.split("\n")
    for line in lines[:30]:
        print(line)
    if len(lines) > 30:
        print(f"\n... ({len(lines) - 30} more lines) ...\n")

    print(f"\nChunk Order (Shuffled): {generator.chunk_order}")
    print(f"Index Mapping: {generator.index_mapping}")


def example_aggressive_obfuscation():
    """Example with aggressive obfuscation"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Aggressive Obfuscation")
    print("="*80 + "\n")

    generator = ArrayPolymorphicRandomChunks()
    payload = "cmd.exe /c whoami"

    # Aggressive configuration
    config = PolymorphicConfig(
        randomize_order=True,
        use_multiple_strategies=True,
        num_strategies=4,
        add_junk_code=True,
        obfuscate_variable_names=True,
        chunk_size=8,
        encoding_type="hex"
    )

    code = generator.generate_polymorphic_wrapper(payload, config)

    print("Configuration:")
    print(f"  - Payload: {payload}")
    print(f"  - Chunk Size: {config.chunk_size}")
    print(f"  - Num Strategies: {config.num_strategies}")
    print(f"  - Junk Code: {config.add_junk_code}")
    print(f"  - Obfuscate Names: {config.obfuscate_variable_names}")

    print(f"\nGenerated Code Statistics:")
    print(f"  - Total Length: {len(code)} bytes")
    print(f"  - Total Lines: {len(code.split(chr(10)))}")
    print(f"  - Functions: {code.count('Function')}")
    print(f"  - For Loops: {code.count('For')}")

    print(f"\nFirst 500 characters:")
    print("-"*80)
    print(code[:500])
    print("...")


def example_mixed_encoding():
    """Example with mixed encoding"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Mixed Encoding (Hex + Base64)")
    print("="*80 + "\n")

    generator = ArrayPolymorphicRandomChunks()
    payload = "powershell.exe -EncodedCommand"

    # Mixed encoding
    config = PolymorphicConfig(
        encoding_type="mixed",
        chunk_size=12,
        randomize_order=True,
        add_junk_code=True
    )

    code = generator.generate_polymorphic_wrapper(payload, config)

    print("Configuration:")
    print(f"  - Payload: {payload}")
    print(f"  - Encoding Type: {config.encoding_type}")
    print(f"  - Chunk Size: {config.chunk_size}")

    print(f"\nGenerated Code (first 400 chars):")
    print("-"*80)
    print(code[:400])
    print("...")


def example_large_payload():
    """Example with large payload"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Large Payload Handling")
    print("="*80 + "\n")

    generator = ArrayPolymorphicRandomChunks()
    # Large payload
    payload = "powershell.exe -NoProfile -ExecutionPolicy Bypass " + \
              "-Command \"$x = 'test'; " * 10 + \
              "Write-Host $x\""

    config = PolymorphicConfig(
        chunk_size=32,
        randomize_order=True,
        use_multiple_strategies=True,
        num_strategies=3,
        add_junk_code=True
    )

    code = generator.generate_polymorphic_wrapper(payload, config)

    print("Configuration:")
    print(f"  - Payload Length: {len(payload)} characters")
    print(f"  - Chunk Size: {config.chunk_size}")
    print(f"  - Total Chunks: {len(payload) // config.chunk_size + (1 if len(payload) % config.chunk_size else 0)}")

    print(f"\nGenerated Code Statistics:")
    print(f"  - Total Length: {len(code)} bytes")
    print(f"  - Total Lines: {len(code.split(chr(10)))}")
    print(f"  - Obfuscation Factor: {len(code) / len(payload):.2f}x")

    print(f"\nChunk Shuffling:")
    print(f"  - Original Order: {list(range(len(generator.chunk_order)))}")
    print(f"  - Shuffled Order: {generator.chunk_order}")


def example_advanced_variants():
    """Example with multiple random variants"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Advanced Polymorphic with Multiple Variants")
    print("="*80 + "\n")

    generator = ArrayPolymorphicRandomChunks()
    payload = "powershell -c Get-Process"

    code = generator.generate_advanced_polymorphic(payload, variant_count=3)

    print("Configuration:")
    print(f"  - Payload: {payload}")
    print(f"  - Number of Variants: 3")
    print(f"  - Random Selection at Runtime: Yes")

    print(f"\nGenerated Code Statistics:")
    print(f"  - Total Length: {len(code)} bytes")
    print(f"  - Total Lines: {len(code.split(chr(10)))}")
    print(f"  - Contains Rnd(): {'Rnd()' in code}")
    print(f"  - Contains If statements: {'If' in code}")

    print(f"\nFirst 600 characters:")
    print("-"*80)
    print(code[:600])
    print("...")


def example_minimal_overhead():
    """Example with minimal overhead"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Minimal Overhead Configuration")
    print("="*80 + "\n")

    generator = ArrayPolymorphicRandomChunks()
    payload = "test.exe"

    # Minimal configuration
    config = PolymorphicConfig(
        chunk_size=16,
        randomize_order=False,
        use_multiple_strategies=False,
        strategy=PolymorphicStrategy.LINEAR_DECODE,
        add_junk_code=False,
        obfuscate_variable_names=False
    )

    code = generator.generate_polymorphic_wrapper(payload, config)

    print("Configuration:")
    print(f"  - Payload: {payload}")
    print(f"  - Randomize Order: {config.randomize_order}")
    print(f"  - Multiple Strategies: {config.use_multiple_strategies}")
    print(f"  - Add Junk Code: {config.add_junk_code}")
    print(f"  - Obfuscate Names: {config.obfuscate_variable_names}")

    print(f"\nGenerated Code ({len(code)} bytes):")
    print("-"*80)
    print(code)


def example_specific_strategy():
    """Example using specific decode strategy"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Specific Decode Strategy - Lookup Table")
    print("="*80 + "\n")

    generator = ArrayPolymorphicRandomChunks()
    payload = "explorer.exe"

    config = PolymorphicConfig(
        strategy=PolymorphicStrategy.LOOKUP_TABLE,
        use_multiple_strategies=False,
        randomize_order=True
    )

    code = generator.generate_polymorphic_wrapper(payload, config)

    print("Configuration:")
    print(f"  - Payload: {payload}")
    print(f"  - Strategy: {config.strategy.value}")

    print(f"\nGenerated Code (showing strategy function):")
    print("-"*80)

    # Extract and show the decode function
    lines = code.split("\n")
    in_function = False
    for i, line in enumerate(lines):
        if "Function" in line and "Decode" in line:
            in_function = True
        if in_function:
            print(line)
            if "End Function" in line:
                break


def example_comparison():
    """Example showing configuration comparison"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Configuration Comparison")
    print("="*80 + "\n")

    payload = "powershell test" * 5

    configs = [
        ("Minimal", PolymorphicConfig(
            randomize_order=False,
            use_multiple_strategies=False,
            add_junk_code=False,
            obfuscate_variable_names=False
        )),
        ("Moderate", PolymorphicConfig(
            randomize_order=True,
            use_multiple_strategies=True,
            num_strategies=2,
            add_junk_code=True,
            obfuscate_variable_names=True
        )),
        ("Maximum", PolymorphicConfig(
            randomize_order=True,
            use_multiple_strategies=True,
            num_strategies=5,
            add_junk_code=True,
            obfuscate_variable_names=True,
            chunk_size=8
        )),
    ]

    results = []
    for name, config in configs:
        generator = ArrayPolymorphicRandomChunks()
        code = generator.generate_polymorphic_wrapper(payload, config)
        results.append({
            "name": name,
            "size": len(code),
            "lines": len(code.split("\n")),
            "functions": code.count("Function"),
            "obfuscation_ratio": len(code) / len(payload)
        })

    print("Configuration Comparison:")
    print(f"{'Config':<15} {'Size (bytes)':<15} {'Lines':<10} {'Functions':<12} {'Obfuscation Ratio':<20}")
    print("-"*80)
    for r in results:
        print(f"{r['name']:<15} {r['size']:<15} {r['lines']:<10} {r['functions']:<12} {r['obfuscation_ratio']:<20.2f}x")


def main():
    """Run all examples"""
    examples = [
        example_basic_usage,
        example_aggressive_obfuscation,
        example_mixed_encoding,
        example_large_payload,
        example_advanced_variants,
        example_minimal_overhead,
        example_specific_strategy,
        example_comparison
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n[ERROR] {example.__name__}: {e}")

    print("\n" + "="*80)
    print("✓ All examples completed")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
