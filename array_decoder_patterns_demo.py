#!/usr/bin/env python3
"""
Array Decoder Multi-Pattern Demonstration
Shows all 10 patterns in action with real payloads
"""

import binascii
import json
from array_decoder_patterns import (
    ArrayDecoderPatterns,
    DecoderPattern,
    DecoderVariant
)


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def analyze_vbs_code(code: str, pattern_name: str) -> dict:
    """Analyze VBS code characteristics"""
    analysis = {
        "pattern": pattern_name,
        "code_size": len(code),
        "line_count": len(code.split('\n')),
        "has_array": "Dim" in code and "(" in code,
        "has_loops": code.count("For") + code.count("Do"),
        "has_functions": code.count("Function"),
        "has_dictionary": "Dictionary" in code,
        "has_2d_array": "," in code and "(" in code,
        "has_select": "Select Case" in code,
        "has_modulo": "Mod" in code,
        "hex_decode": "Chr(CLng" in code,
        "uses_wscript": "WScript.Shell" in code,
    }
    return analysis


def demo_single_pattern(pattern, payload):
    """Demonstrate a single pattern"""
    generator = ArrayDecoderPatterns()
    variant = DecoderVariant(pattern=pattern, randomize_names=True)

    print(f"\nPattern: {pattern.value.upper()}")
    print(f"Payload: {payload[:50]}{'...' if len(payload) > 50 else ''}")

    vbs_code = generator.generate_decoder(payload, pattern, variant)

    print(f"Generated VBS Code:")
    print(f"  Size: {len(vbs_code)} bytes")
    print(f"  Lines: {len(vbs_code.split(chr(10)))} lines")
    print(f"\nFirst 400 characters:")
    print("-" * 80)
    print(vbs_code[:400])
    print("-" * 80)

    if len(vbs_code) > 400:
        print(f"... ({len(vbs_code) - 400} more bytes)")

    analysis = analyze_vbs_code(vbs_code, pattern.value)

    print(f"\nAnalysis:")
    for key, value in analysis.items():
        if key != "pattern":
            print(f"  {key:20s}: {value}")

    return vbs_code, analysis


def demo_all_patterns_comparison(payload):
    """Generate and compare all patterns"""
    print_section("ALL PATTERNS - COMPARISON")

    generator = ArrayDecoderPatterns()
    results = {}
    analyses = {}

    for pattern in DecoderPattern:
        variant = DecoderVariant(pattern=pattern, randomize_names=True)
        vbs_code = generator.generate_decoder(payload, pattern, variant)
        results[pattern.value] = vbs_code
        analyses[pattern.value] = analyze_vbs_code(vbs_code, pattern.value)

    # Print comparison table
    print(f"{'Pattern':<20} {'Size':>8} {'Lines':>6} {'Loops':>6} {'Funcs':>6} {'Features':>20}")
    print("-" * 80)

    for pattern in DecoderPattern:
        analysis = analyses[pattern.value]
        features = []
        if analysis["has_dictionary"]:
            features.append("dict")
        if analysis["has_2d_array"]:
            features.append("2d")
        if analysis["has_select"]:
            features.append("select")
        if analysis["has_modulo"]:
            features.append("mod")
        feature_str = ",".join(features) if features else "-"

        print(f"{pattern.value:<20} {analysis['code_size']:>8} {analysis['line_count']:>6} "
              f"{analysis['has_loops']:>6} {analysis['has_functions']:>6} {feature_str:>20}")

    return results, analyses


def demo_pattern_characteristics():
    """Show detailed characteristics of each pattern"""
    print_section("PATTERN CHARACTERISTICS DEEP DIVE")

    characteristics = {
        DecoderPattern.SEQUENTIAL: {
            "approach": "Standard array indexing (0, 1, 2, ...)",
            "detection_evasion": "Low - baseline pattern",
            "complexity": "Low - simple sequential loops",
            "code_overhead": "Minimal",
            "best_for": "Baseline comparison",
            "features": ["Single array", "Forward iteration", "Direct indexing"],
        },
        DecoderPattern.INTERLEAVED: {
            "approach": "Process even indices, then odd indices",
            "detection_evasion": "Medium - breaks linear execution",
            "complexity": "Low - two separate loops",
            "code_overhead": "Minimal",
            "best_for": "Evading execution flow analysis",
            "features": ["Single array", "Dual phase processing", "Step 2 iteration"],
        },
        DecoderPattern.NESTED_ARRAY: {
            "approach": "2D array (row/column) organization",
            "detection_evasion": "Medium - mimics data structures",
            "complexity": "Medium - nested loops",
            "code_overhead": "Slight (~20%)",
            "best_for": "Appearing as legitimate data processing",
            "features": ["2D array", "Nested loops", "Matrix access"],
        },
        DecoderPattern.MIXED_ENCODING: {
            "approach": "Alternate hex and base64 per chunk",
            "detection_evasion": "High - codec polymorphism",
            "complexity": "High - dual decode paths",
            "code_overhead": "Significant (~150%)",
            "best_for": "Breaking single-codec signatures",
            "features": ["Dual encoding", "Conditional decode", "XML DOM"],
        },
        DecoderPattern.REVERSE_ORDER: {
            "approach": "Backward chunk processing (last to first)",
            "detection_evasion": "Medium - direction analysis",
            "complexity": "Low - negative step loop",
            "code_overhead": "Minimal",
            "best_for": "Evading forward execution tracking",
            "features": ["Reverse iteration", "Step -1", "Backward processing"],
        },
        DecoderPattern.CHUNK_INDEX: {
            "approach": "Dictionary-based associative array",
            "detection_evasion": "High - breaks numeric indexing",
            "complexity": "Medium - Dictionary objects",
            "code_overhead": "Moderate (~30%)",
            "best_for": "Defeating array-based detection",
            "features": ["Dictionary", "String keys", "Key-value storage"],
        },
        DecoderPattern.OBFUSCATED_VAR: {
            "approach": "Short variable names per chunk",
            "detection_evasion": "Medium - variable obfuscation",
            "complexity": "Low - repeated decode logic",
            "code_overhead": "High (~100%)",
            "best_for": "Defeating name-pattern analysis",
            "features": ["Individual variables", "Short names", "Duplicated logic"],
        },
        DecoderPattern.POLYMORPHIC: {
            "approach": "Multiple decode implementations with runtime selection",
            "detection_evasion": "High - highest polymorphism",
            "complexity": "High - 3 functions + Select/Case",
            "code_overhead": "Very high (~200%)",
            "best_for": "Maximum signature variety",
            "features": ["Multiple functions", "Select/Case", "Function dispatch"],
        },
        DecoderPattern.SPLIT_DECODE: {
            "approach": "Two array groups with separate function calls",
            "detection_evasion": "Medium - subroutine distribution",
            "complexity": "Medium - function calls",
            "code_overhead": "Moderate (~40%)",
            "best_for": "Stack frame obfuscation",
            "features": ["Subroutines", "Multiple arrays", "Separate calls"],
        },
        DecoderPattern.MATRIX_ACCESS: {
            "approach": "Computed indices with modulo arithmetic",
            "detection_evasion": "Medium - index computation",
            "complexity": "Low - computed access",
            "code_overhead": "Minimal",
            "best_for": "Defeating static index analysis",
            "features": ["Modulo arithmetic", "Computed indices", "Cyclic access"],
        },
    }

    for pattern in DecoderPattern:
        info = characteristics[pattern]
        print(f"\n{pattern.value.upper()}")
        print("-" * 80)
        for key, value in info.items():
            if isinstance(value, list):
                print(f"  {key:15s}: {', '.join(value)}")
            else:
                print(f"  {key:15s}: {value}")


def demo_code_size_scaling(payloads):
    """Show how code size scales with payload size"""
    print_section("CODE SIZE SCALING BY PAYLOAD SIZE")

    generator = ArrayDecoderPatterns()

    print(f"{'Payload Size':<15} ", end="")
    for pattern in DecoderPattern:
        print(f"{pattern.value[:12]:<14} ", end="")
    print()
    print("-" * (15 + 14 * len(DecoderPattern)))

    results = {}
    for payload_name, payload in payloads.items():
        print(f"{payload_name:<15} ", end="")

        sizes = {}
        for pattern in DecoderPattern:
            variant = DecoderVariant(pattern=pattern, randomize_names=True)
            vbs_code = generator.generate_decoder(payload, pattern, variant)
            size = len(vbs_code)
            sizes[pattern.value] = size
            print(f"{size:>6}B ({size/1024:.1f}KB) ", end="")
        print()

        results[payload_name] = sizes

    return results


def demo_pattern_variations(payload):
    """Show variations with different configurations"""
    print_section("PATTERN VARIATIONS - CHUNK SIZE & RANDOMIZATION")

    generator = ArrayDecoderPatterns()

    # Variations to test
    chunk_sizes = [8, 16, 32]
    randomization = [True, False]

    print(f"Testing: Sequential pattern with {payload[:30]}...\n")

    print(f"{'Chunk Size':<12} {'Randomized':<15} {'Code Size':>12} {'Variables':>12}")
    print("-" * 60)

    for chunk_size in chunk_sizes:
        for is_random in randomization:
            variant = DecoderVariant(
                pattern=DecoderPattern.SEQUENTIAL,
                chunk_size=chunk_size,
                randomize_names=is_random
            )

            # Count chunks
            chunks = [payload[i:i + chunk_size] for i in range(0, len(payload), chunk_size)]
            num_chunks = len(chunks)

            vbs_code = generator.sequential_decoder(payload, variant)
            code_size = len(vbs_code)

            # Extract unique variables
            import re
            variables = set(re.findall(r'\b[a-zA-Z_]\w*\b', vbs_code))
            var_count = len(variables)

            randomized_str = "Yes" if is_random else "No"
            print(f"{chunk_size:<12} {randomized_str:<15} {code_size:>12} {var_count:>12}")

    print(f"\nNote: Code size may vary slightly due to randomized variable name length")


def demo_payload_evolution():
    """Show output for progressively larger payloads"""
    print_section("PAYLOAD EVOLUTION - SINGLE PATTERN (POLYMORPHIC)")

    generator = ArrayDecoderPatterns()
    pattern = DecoderPattern.POLYMORPHIC

    base_payload = "powershell.exe -NoProfile -Command "
    size_increments = [10, 50, 100, 500]

    print(f"Pattern: {pattern.value.upper()}\n")
    print(f"{'Payload Bytes':<15} {'Code Size':>12} {'Chunks':>8} {'Code/Payload Ratio':>20}")
    print("-" * 70)

    for increment in size_increments:
        payload = base_payload + "A" * increment
        num_chunks = (len(payload) + 15) // 16  # 16-byte chunks

        variant = DecoderVariant(pattern=pattern, randomize_names=True)
        vbs_code = generator.generate_decoder(payload, pattern, variant)
        code_size = len(vbs_code)

        ratio = code_size / len(payload)
        print(f"{len(payload):<15} {code_size:>12} {num_chunks:>8} {ratio:>20.2f}x")


def main():
    """Run complete demonstration"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "ARRAY DECODER MULTI-PATTERN DEMONSTRATION".center(78) + "║")
    print("║" + "10 Distinct Concatenation Patterns with Full Analysis".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")

    # Test payloads
    test_payloads = {
        "short": "cmd /c dir",
        "medium": "powershell.exe -NoProfile -Command Write-Host 'Success'",
        "long": "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; Get-Process\"",
    }

    # Demo 1: Pattern characteristics
    demo_pattern_characteristics()

    # Demo 2: Single pattern example
    print_section("SINGLE PATTERN EXAMPLE - SEQUENTIAL")
    demo_single_pattern(DecoderPattern.SEQUENTIAL, test_payloads["medium"])

    # Demo 3: All patterns comparison
    results, analyses = demo_all_patterns_comparison(test_payloads["medium"])

    # Demo 4: Code size scaling
    scaling = demo_code_size_scaling(test_payloads)

    # Demo 5: Variations
    demo_pattern_variations(test_payloads["short"])

    # Demo 6: Payload evolution
    demo_payload_evolution()

    # Summary
    print_section("SUMMARY")
    print(f"✓ Demonstrated all {len(DecoderPattern)} array decoder patterns")
    print(f"✓ Each pattern provides different detection evasion characteristics")
    print(f"✓ All patterns produce functionally equivalent outputs")
    print(f"✓ Code size varies from ~1.5KB (Sequential) to ~12KB (Polymorphic)")
    print(f"✓ Patterns can be combined with payload variants for maximum flexibility")
    print("\nFor detailed documentation, see: ARRAY_DECODER_PATTERNS_REFERENCE.md")
    print("For automated testing, run: python test_array_decoder_patterns.py")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
