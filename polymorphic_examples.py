#!/usr/bin/env python3
"""
Practical examples using the Polymorphic Engine
Demonstrates real-world usage patterns
"""

from polymorphic_engine import PolymorphicCodeGenerator, PolymorphicConfig
import json


def example_1_basic_generation():
    """Example 1: Basic polymorphic code generation"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Polymorphic Generation")
    print("=" * 70 + "\n")

    config = PolymorphicConfig(
        algorithm_variants=2,
        complexity_level=2
    )

    engine = PolymorphicCodeGenerator(config)

    # Generate code that executes a command
    command = "powershell -c 'Write-Host Test'"
    script = engine.generate_complete_polymorphic_script(command)

    print("Generated Script:")
    print(script)
    print(f"\nGeneration Info: {engine.get_generation_info()}")


def example_2_data_encoding():
    """Example 2: Encode arbitrary data"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Polymorphic Data Encoding")
    print("=" * 70 + "\n")

    engine = PolymorphicCodeGenerator()

    # Encode sensitive data
    sensitive_data = b"API_KEY=12345678secret"

    encoded, metadata, algo = engine.encode_data(sensitive_data)

    print(f"Original Data: {sensitive_data}")
    print(f"Algorithm Used: {algo}")
    print(f"Encoded Data: {encoded.hex()}")
    print(f"Encoded Length: {len(encoded)} bytes")
    print(f"\nAlgorithm Metadata: {metadata}")

    # Generate decoder code
    decoder = engine.generate_polymorphic_decoder(encoded, metadata)
    print(f"\nGenerated Decoder:\n{decoder}")


def example_3_multi_stage():
    """Example 3: Multi-stage polymorphic encoding"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Multi-Stage Polymorphic Encoding (3 stages)")
    print("=" * 70 + "\n")

    config = PolymorphicConfig(complexity_level=5)
    engine = PolymorphicCodeGenerator(config)

    payload = "calc.exe"
    script = engine.generate_multi_stage_polymorphic(payload, stages=3)

    print("Generated Multi-Stage Script:")
    print(script)
    print("\nNote: Each stage uses a different algorithm")


def example_4_multiple_generations():
    """Example 4: Show how same command produces different code"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Same Command, Different Generations")
    print("=" * 70 + "\n")

    command = "echo polymorphic"

    print("Generating 3 different scripts for the same command:\n")

    for i in range(3):
        print(f"--- Generation {i + 1} ---")

        engine = PolymorphicCodeGenerator()
        script = engine.generate_complete_polymorphic_script(command)

        # Extract algorithm name from generated script
        lines = script.split('\n')
        algo_line = [l for l in lines if 'Algorithm=' in l][0]
        print(algo_line.strip())

        # Show just the encoding logic (first 10 lines of actual code)
        code_lines = [l for l in lines if l.strip() and not l.startswith('#')]
        for line in code_lines[:3]:
            print(f"  {line}")

        print()


def example_5_configuration_variations():
    """Example 5: Different configuration levels"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Configuration Complexity Levels")
    print("=" * 70 + "\n")

    command = "test"

    configs = [
        ("Level 1 (Minimal)", PolymorphicConfig(complexity_level=1, algorithm_variants=1)),
        ("Level 3 (Medium)", PolymorphicConfig(complexity_level=3, algorithm_variants=2)),
        ("Level 5 (Maximum)", PolymorphicConfig(complexity_level=5, algorithm_variants=3)),
    ]

    for name, config in configs:
        print(f"\n{name}:")
        engine = PolymorphicCodeGenerator(config)
        info = engine.get_generation_info()
        print(f"  Algorithm Variants: {info['algorithm_variants']}")
        print(f"  Complexity: {info['complexity_level']}")


def example_6_batch_generation():
    """Example 6: Generate multiple polymorphic variants for distribution"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Batch Generation for Distribution")
    print("=" * 70 + "\n")

    command = "whoami"
    num_variants = 5

    print(f"Generating {num_variants} polymorphic variants of the same command:\n")

    variants = []
    for i in range(num_variants):
        engine = PolymorphicCodeGenerator()
        script = engine.generate_complete_polymorphic_script(command)

        # Extract algorithm used
        algo_line = [l for l in script.split('\n') if 'Algorithm=' in l][0]
        algo = algo_line.split('Algorithm=')[1].split()[0]

        variants.append({
            "variant": i + 1,
            "algorithm": algo,
            "script_length": len(script),
            "variables_generated": engine.get_generation_info()["variables_generated"]
        })

        print(f"Variant {i + 1}: {algo} ({len(script)} bytes, "
              f"{engine.get_generation_info()['variables_generated']} variables)")

    print("\n" + json.dumps(variants, indent=2))


def example_7_payload_detection_evasion():
    """Example 7: Evade static payload detection"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Payload Detection Evasion")
    print("=" * 70 + "\n")

    # Original payload that might be detected
    payload = "rundll32.exe shell32.dll"

    print(f"Original Payload: {payload}\n")
    print("Static signature of original: " + payload)
    print("(Easy for detection systems to find)\n")

    print("Polymorphic Encoding (10 variants):\n")

    algorithms_used = {}

    for i in range(10):
        engine = PolymorphicCodeGenerator()
        encoded, metadata, algo = engine.encode_data(payload.encode())

        if algo not in algorithms_used:
            algorithms_used[algo] = 0
        algorithms_used[algo] += 1

        # Show encoded representation
        hex_repr = encoded.hex()[:40]  # First 40 chars
        print(f"  Variant {i + 1}: {algo:20s} → {hex_repr}...")

    print(f"\nAlgorithm Distribution:")
    for algo, count in sorted(algorithms_used.items()):
        print(f"  {algo}: {count} times")

    print("\nEach variant is completely different, defeating static signatures")


def example_8_controlled_seed():
    """Example 8: Reproducible generation with seed"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Reproducible Generation with Seed")
    print("=" * 70 + "\n")

    command = "test"

    # Generate with fixed seed - should be identical
    print("Generating twice with seed=42:\n")

    for run in range(2):
        config = PolymorphicConfig(seed=42)
        engine = PolymorphicCodeGenerator(config)
        script = engine.generate_complete_polymorphic_script(command)

        algo_line = [l for l in script.split('\n') if 'Algorithm=' in l][0]
        print(f"Run {run + 1}: {algo_line.strip()}")

    print("\n(Both runs use same algorithm due to fixed seed)")

    # Now without seed - should be different
    print("\nGenerating twice without seed (truly random):\n")

    for run in range(2):
        config = PolymorphicConfig()  # seed=None by default
        engine = PolymorphicCodeGenerator(config)
        script = engine.generate_complete_polymorphic_script(command)

        algo_line = [l for l in script.split('\n') if 'Algorithm=' in l][0]
        print(f"Run {run + 1}: {algo_line.strip()}")

    print("\n(Different algorithms due to true randomization)")


def example_9_custom_algorithms():
    """Example 9: Analyzing algorithm selection"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Algorithm Distribution Analysis")
    print("=" * 70 + "\n")

    print("Running 50 random generations to see algorithm distribution:\n")

    algorithm_stats = {}

    for _ in range(50):
        engine = PolymorphicCodeGenerator()
        data = b"test payload"
        _, _, algo = engine.encode_data(data)

        if algo not in algorithm_stats:
            algorithm_stats[algo] = 0
        algorithm_stats[algo] += 1

    # Sort by frequency
    sorted_stats = sorted(algorithm_stats.items(), key=lambda x: x[1], reverse=True)

    print("Algorithm Distribution:")
    print("-" * 40)
    for algo, count in sorted_stats:
        percentage = (count / 50) * 100
        bar = "█" * (count // 2)
        print(f"{algo:25s}: {count:2d} ({percentage:5.1f}%) {bar}")

    print("\nNote: Distribution should be approximately uniform")


def run_all_examples():
    """Run all examples"""
    examples = [
        ("Basic Generation", example_1_basic_generation),
        ("Data Encoding", example_2_data_encoding),
        ("Multi-Stage", example_3_multi_stage),
        ("Multiple Generations", example_4_multiple_generations),
        ("Configuration Variations", example_5_configuration_variations),
        ("Batch Generation", example_6_batch_generation),
        ("Detection Evasion", example_7_payload_detection_evasion),
        ("Controlled Seed", example_8_controlled_seed),
        ("Algorithm Analysis", example_9_custom_algorithms),
    ]

    print("\n" + "=" * 70)
    print("POLYMORPHIC ENGINE - PRACTICAL EXAMPLES")
    print("=" * 70)

    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {name}: {e}")

    print("\n" + "=" * 70)
    print("END OF EXAMPLES")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    # Uncomment to run all examples
    run_all_examples()

    # Or run individual examples
    # example_1_basic_generation()
    # example_2_data_encoding()
    # example_3_multi_stage()
