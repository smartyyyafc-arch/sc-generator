#!/usr/bin/env python3
"""
Test suite for enhanced polymorphic wrapper
Demonstrates all obfuscation techniques: dead code, junk comments, variable swapping
"""

import sys
import json
from polymorphic_wrapper_enhanced import (
    create_enhanced_polymorphic_wrapper,
    EnhancedPolymorphicEncoder,
    EnhancedObfuscationConfig,
    JunkCodeGenerator,
    VariableSwapper,
)


def test_junk_code_generation():
    """Test junk code generation"""
    print("\n" + "="*80)
    print("TEST 1: JUNK CODE GENERATION")
    print("="*80)

    junk_gen = JunkCodeGenerator()

    # Test variable assignments
    print("\n[*] Generated Junk Variable Assignments:")
    junk_vars = junk_gen.generate_junk_variable_assignments()
    print(junk_vars)

    # Test junk comments
    print("\n[*] Generated Junk Comments:")
    junk_comments = junk_gen.generate_junk_comments()
    for comment in junk_comments:
        print(f"  {comment}")

    # Test dead code blocks
    print("\n[*] Generated Dead Code Blocks:")
    for i in range(3):
        dead_code = junk_gen.generate_dead_code_block()
        print(f"\nDead Code Block {i+1}:")
        print(dead_code)

    # Test decoy functions
    print("\n[*] Generated Decoy Functions:")
    decoy_funcs = junk_gen.generate_decoy_function(2)
    print(decoy_funcs)


def test_variable_swapping():
    """Test variable name swapping"""
    print("\n" + "="*80)
    print("TEST 2: VARIABLE NAME SWAPPING")
    print("="*80)

    swapper = VariableSwapper()

    # Generate swapped names
    original_vars = ["cmd", "data", "key", "payload", "decoded"]
    print("\n[*] Variable Swap Mapping:")
    print(f"{'Original':<15} {'Swapped To':<15}")
    print("-" * 30)

    for var in original_vars:
        swapped = swapper.generate_swap_name(var)
        print(f"{var:<15} {swapped:<15}")


def test_enhanced_encoding_single():
    """Test single enhanced encoding with obfuscation"""
    print("\n" + "="*80)
    print("TEST 3: SINGLE ENHANCED ENCODING")
    print("="*80)

    config = EnhancedObfuscationConfig(
        add_junk_code=True,
        add_dead_code=True,
        add_variable_swapping=True,
        add_decoy_functions=True,
    )
    encoder = EnhancedPolymorphicEncoder(config)

    test_command = "whoami"
    print(f"\n[*] Command: {test_command}")

    payload = encoder.encode(test_command)

    print(f"\n[*] Strategy: {payload['strategy']}")
    print(f"[*] Variable Name: {payload['var_name']}")
    print(f"[*] Decoder Name: {payload['decoder_name']}")
    print(f"[*] Encoded Data: {payload['encoded_data'][:50]}...")
    print(f"\n[*] Generated Decoder Code:")
    print(payload['decoder_code'])


def test_obfuscation_levels():
    """Test different obfuscation levels"""
    print("\n" + "="*80)
    print("TEST 4: OBFUSCATION LEVELS COMPARISON")
    print("="*80)

    test_command = "dir /s"

    # Minimal obfuscation
    config_min = EnhancedObfuscationConfig(
        add_junk_code=False,
        add_dead_code=False,
        add_variable_swapping=False,
        add_decoy_functions=False,
    )
    encoder_min = EnhancedPolymorphicEncoder(config_min)

    # Maximum obfuscation
    config_max = EnhancedObfuscationConfig(
        add_junk_code=True,
        add_dead_code=True,
        add_variable_swapping=True,
        add_decoy_functions=True,
    )
    encoder_max = EnhancedPolymorphicEncoder(config_max)

    payload_min = encoder_min.encode(test_command)
    payload_max = encoder_max.encode(test_command)

    decoder_min_lines = len(payload_min['decoder_code'].split('\n'))
    decoder_max_lines = len(payload_max['decoder_code'].split('\n'))

    print(f"\n[*] Command: {test_command}")
    print(f"\n[*] Minimal Obfuscation Decoder:")
    print(f"    Lines: {decoder_min_lines}")
    print(f"    Size: {len(payload_min['decoder_code'])} bytes")

    print(f"\n[*] Maximum Obfuscation Decoder:")
    print(f"    Lines: {decoder_max_lines}")
    print(f"    Size: {len(payload_max['decoder_code'])} bytes")

    print(f"\n[*] Obfuscation Increase: {((decoder_max_lines - decoder_min_lines) / decoder_min_lines * 100):.1f}% more lines")
    print(f"[*] Size Increase: {((len(payload_max['decoder_code']) - len(payload_min['decoder_code'])) / len(payload_min['decoder_code']) * 100):.1f}% larger")


def test_wrapper_generation():
    """Test wrapper generation across formats"""
    print("\n" + "="*80)
    print("TEST 5: WRAPPER GENERATION (All Formats)")
    print("="*80)

    test_command = "calc.exe"
    formats = ["python", "vbs", "powershell", "bash"]

    for fmt in formats:
        print(f"\n[*] Generating {fmt.upper()} wrapper...")
        result = create_enhanced_polymorphic_wrapper(test_command, output_format=fmt, iterations=2)

        wrapper_size = len(result['wrapper'])
        print(f"    Size: {wrapper_size} bytes")
        print(f"    Obfuscation Level: {result['obfuscation_level']}")
        print(f"    Techniques: {', '.join(result['techniques'][:3])}...")


def test_strategy_distribution():
    """Test strategy distribution over multiple invocations"""
    print("\n" + "="*80)
    print("TEST 6: STRATEGY DISTRIBUTION (50 Invocations)")
    print("="*80)

    encoder = EnhancedPolymorphicEncoder()
    test_command = "test_payload"

    for _ in range(50):
        encoder.encode(test_command)

    stats = encoder.get_statistics()

    print(f"\n[*] Total Invocations: {stats['total_invocations']}")
    print(f"[*] Unique Strategies Used: {stats['unique_strategies_used']}")

    print(f"\n[*] Strategy Distribution:")
    print(f"{'Strategy':<20} {'Count':<10} {'Percentage':<10}")
    print("-" * 40)

    for strategy, count in stats['strategy_distribution'].items():
        percentage = (count / stats['total_invocations'] * 100)
        print(f"{strategy:<20} {count:<10} {percentage:.1f}%")


def test_complexity_metrics():
    """Test complexity metrics of generated code"""
    print("\n" + "="*80)
    print("TEST 7: CODE COMPLEXITY METRICS")
    print("="*80)

    config = EnhancedObfuscationConfig(
        add_junk_code=True,
        add_dead_code=True,
        add_variable_swapping=True,
        add_decoy_functions=True,
    )
    encoder = EnhancedPolymorphicEncoder(config)

    test_command = "powershell.exe -NoProfile -Command Get-Process"
    wrapper = encoder.generate_enhanced_wrapper_script(test_command, iterations=3)

    lines = wrapper.split('\n')
    functions = wrapper.count('def ')
    junk_blocks = wrapper.count('if False:') + wrapper.count('try:')
    comments = wrapper.count('#')

    print(f"\n[*] Generated Wrapper Metrics:")
    print(f"    Total Lines: {len(lines)}")
    print(f"    Total Functions: {functions}")
    print(f"    Dead Code Blocks: {junk_blocks}")
    print(f"    Comment Lines: {comments}")
    print(f"    Average Line Length: {sum(len(line) for line in lines) / len(lines):.1f} chars")


def test_payload_execution():
    """Test that enhanced payloads are valid Python"""
    print("\n" + "="*80)
    print("TEST 8: PAYLOAD SYNTAX VALIDATION")
    print("="*80)

    config = EnhancedObfuscationConfig(
        add_junk_code=True,
        add_dead_code=True,
        add_variable_swapping=True,
    )
    encoder = EnhancedPolymorphicEncoder(config)

    test_command = "echo 'test'"

    for _ in range(5):
        payload = encoder.encode(test_command)
        decoder_code = payload['decoder_code']

        # Try to compile the decoder code (syntax check)
        try:
            compile(decoder_code, '<string>', 'exec')
            print(f"[+] Strategy {payload['strategy']}: Valid Python syntax")
        except SyntaxError as e:
            print(f"[-] Strategy {payload['strategy']}: SYNTAX ERROR - {e}")


def test_evasion_features():
    """Test evasion features"""
    print("\n" + "="*80)
    print("TEST 9: EVASION FEATURES VERIFICATION")
    print("="*80)

    config = EnhancedObfuscationConfig()
    encoder = EnhancedPolymorphicEncoder(config)

    test_command = "sensitive_command"
    wrapper = encoder.generate_enhanced_wrapper_script(test_command, iterations=3)

    # Check for evasion features
    features = {
        "Dead Code (if False:)": "if False:" in wrapper,
        "Dead Code (try/except)": "raise NotImplementedError()" in wrapper,
        "Junk Comments": "#" in wrapper and "Verifying" in wrapper,
        "Decoy Functions": "def _process_" in wrapper,
        "Variable Swapping": "_cmd_" in wrapper,
        "Multiple Strategies": wrapper.count("# Encoding variant") >= 2,
    }

    print("\n[*] Evasion Features Present:")
    for feature, present in features.items():
        status = "[+]" if present else "[-]"
        print(f"  {status} {feature}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("ENHANCED POLYMORPHIC WRAPPER TEST SUITE")
    print("="*80)

    test_junk_code_generation()
    test_variable_swapping()
    test_enhanced_encoding_single()
    test_obfuscation_levels()
    test_wrapper_generation()
    test_strategy_distribution()
    test_complexity_metrics()
    test_payload_execution()
    test_evasion_features()

    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80 + "\n")
