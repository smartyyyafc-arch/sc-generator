#!/usr/bin/env python3
"""
Integration Example: Multi-Encoding + Array Encoder
Demonstrates combining multi-encoding layers with array encoding for enhanced obfuscation
For authorized pentesting and security research
"""

from multi_encoding_layers import MultiEncodingWrapper, EncodingLayerType
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat, ChunkingStrategy


def example_multiencoding_then_array():
    """
    Example 1: First apply multi-encoding, then chunk into array
    This provides strong obfuscation with array-based delivery
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Multi-Encoding -> Array Chunking")
    print("=" * 70)

    # Step 1: Create multi-encoding wrapper
    wrapper = MultiEncodingWrapper(num_layers=2)
    print(f"\nEncoding layers: {' -> '.join(l.layer_type.value for l in wrapper.encoding_layers)}")

    # Step 2: Encode the command
    command = "powershell.exe -Command Get-Process"
    encoded = wrapper.encode(command)
    print(f"\nOriginal command: {command}")
    print(f"Encoded command: {encoded}")

    # Step 3: Chunk the encoded command into array
    config = EncoderConfig(
        chunk_size=16,
        encoding_type=EncodingType.HEX,
        output_format=OutputFormat.POWERSHELL,
        variable_name="encoded_payload",
        chunking_strategy=ChunkingStrategy.SEQUENTIAL
    )

    array_encoder = ArrayEncoder(config)
    array_result = array_encoder.generate(encoded)

    print(f"\nArray-chunked payload (PowerShell):\n")
    print(array_result)

    # Step 4: Generate Python decoder for the multi-encoding
    decoder = wrapper.generate_decoder_python(encoded, "payload")
    print(f"\nDecoder code to rebuild original command:\n")
    print(decoder)


def example_custom_python_decoder():
    """
    Example 2: Generate custom Python decoder that reconstructs array and decodes
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Custom Python Decoder with Array Reconstruction")
    print("=" * 70)

    # Create multi-encoding wrapper
    wrapper = MultiEncodingWrapper(num_layers=2, seed=42)

    # Encode command
    command = "calc.exe"
    encoded = wrapper.encode(command)

    print(f"\nOriginal command: {command}")
    print(f"Multi-encoded: {encoded}")
    print(f"Layers: {' -> '.join(l.layer_type.value for l in wrapper.encoding_layers)}\n")

    # Create array encoder config
    array_config = EncoderConfig(
        chunk_size=8,
        encoding_type=EncodingType.BASE64,
        output_format=OutputFormat.PYTHON,
        variable_name="chunks"
    )

    # Generate array chunks
    array_encoder = ArrayEncoder(array_config)
    encoded_result = array_encoder.encode(encoded)
    chunks = encoded_result["chunks"]

    print("Generated array chunks (Python):\n")
    print(array_encoder.to_python_list(chunks))

    # Create custom decoder that reconstructs from array and decodes
    # Generate the multi-encoding decoder first
    multi_decoder = wrapper.generate_decoder_python(encoded, 'result')
    decoder_lines = multi_decoder.split('\n')

    decoder_code = f'''#!/usr/bin/env python3
# Custom decoder: Array reconstruction + Multi-encoding decoding

# Array chunks (reconstructed from encoding)
chunks = [
{chr(10).join(f'    "{chunk}"' for chunk in chunks)}
]

# Step 1: Reconstruct from array
reconstructed = ''.join(chunks)

# Step 2: Multi-encoding decode ({wrapper.num_layers} layers)
{chr(10).join(decoder_lines[:-1])}
print(reconstructed)
'''

    print("\nFull decoder script:\n")
    print(decoder_code)


def example_powershell_integration():
    """
    Example 3: PowerShell integration with array and multi-encoding
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: PowerShell Full Integration")
    print("=" * 70)

    # Multi-encoding
    wrapper = MultiEncodingWrapper(num_layers=2)
    command = "ipconfig"
    encoded = wrapper.encode(command)

    print(f"\nCommand: {command}")
    print(f"Encoded: {encoded}")
    print(f"Layers: {' -> '.join(l.layer_type.value for l in wrapper.encoding_layers)}\n")

    # Array encoding
    config = EncoderConfig(
        chunk_size=12,
        encoding_type=EncodingType.HEX,
        output_format=OutputFormat.POWERSHELL,
        variable_name="payloadChunks"
    )

    array_encoder = ArrayEncoder(config)
    array_code = array_encoder.generate(encoded)

    # Combined PowerShell decoder
    ps_decoder = wrapper.generate_decoder_powershell(encoded, 'command')
    combined_ps = f'''# Multi-Encoding + Array Integration
{array_code}

# Reconstruct from array
$reconstructed = $payloadChunks -join ''

# Multi-encoding decoder ({wrapper.num_layers} layers)
$command = $reconstructed

{chr(10).join(line for line in ps_decoder.split(chr(10))[2:] if 'Write-Host' not in line)}

Write-Host "Decoded: $command"
'''

    print("Combined PowerShell decoder:\n")
    print(combined_ps)


def example_batch_encoding_arrays():
    """
    Example 4: Batch process multiple payloads through both wrappers
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Batch Encoding Multiple Payloads")
    print("=" * 70)

    payloads = [
        "cmd.exe /c dir",
        "powershell.exe -NoProfile",
        "notepad.exe",
        "tasklist.exe"
    ]

    print(f"\nBatch processing {len(payloads)} payloads:\n")

    results = []

    for payload in payloads:
        # Multi-encode
        wrapper = MultiEncodingWrapper()
        encoded = wrapper.encode(payload)

        # Array encode
        array_config = EncoderConfig(
            chunk_size=16,
            encoding_type=EncodingType.BASE64,
            output_format=OutputFormat.PYTHON
        )
        array_encoder = ArrayEncoder(array_config)
        array_result = array_encoder.encode(encoded)

        layers = ' -> '.join(l.layer_type.value for l in wrapper.encoding_layers)

        results.append({
            'payload': payload,
            'multi_encoded': encoded,
            'array_chunks': len(array_result['chunks']),
            'layers': layers,
            'final_size': sum(len(c) for c in array_result['chunks'])
        })

    # Display results
    print(f"{'Payload':<25} {'Multi-Layers':<20} {'Chunks':<8} {'Size':<8}")
    print("-" * 70)
    for result in results:
        print(f"{result['payload']:<25} {result['layers']:<20} {result['array_chunks']:<8} {result['final_size']:<8}")


def example_variable_layers():
    """
    Example 5: Demonstrate randomized layer selection across multiple encodings
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Variable Multi-Encoding Across Multiple Runs")
    print("=" * 70)

    payload = "secret_command"

    print(f"\nEncoding '{payload}' 5 times with random layers:\n")

    for i in range(5):
        wrapper = MultiEncodingWrapper()
        encoded = wrapper.encode(payload)
        layers = ' -> '.join(l.layer_type.value for l in wrapper.encoding_layers)

        print(f"  Run {i+1}: {layers:<30} | Output size: {len(encoded)}")


def example_xor_with_custom_key():
    """
    Example 6: Encoding with XOR layer (shows key in config)
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 6: XOR Encoding with Custom Key")
    print("=" * 70)

    payload = "test_payload"

    # Create wrapper that will use XOR
    wrapper = MultiEncodingWrapper(num_layers=1)

    # Find if XOR is in the layers
    has_xor = any(l.layer_type.value == 'xor' for l in wrapper.encoding_layers)

    if has_xor:
        xor_layer = [l for l in wrapper.encoding_layers if l.layer_type.value == 'xor'][0]
        xor_key = xor_layer.config.get('key', 42)

        print(f"\nXOR Layer Configuration:")
        print(f"  Key: {xor_key}")
        print(f"  Key (hex): {hex(xor_key)}")

        encoded = wrapper.encode(payload)
        decoded = wrapper.decode(encoded)

        print(f"\n  Original: {payload}")
        print(f"  Encoded:  {encoded}")
        print(f"  Decoded:  {decoded}")
        print(f"  Success:  {decoded == payload}")
    else:
        print(f"\nNo XOR layer in this run. Layers: {[l.layer_type.value for l in wrapper.encoding_layers]}")
        wrapper = MultiEncodingWrapper(
            num_layers=1,
            available_layers=[EncodingLayerType.XOR]
        )
        encoded = wrapper.encode(payload)
        print(f"Retrying with XOR-only wrapper...")
        print(f"Encoded: {encoded}")


def example_comprehensive_report():
    """
    Example 7: Generate comprehensive encoding/decoding report
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Comprehensive Encoding Report")
    print("=" * 70)

    # Multi-encoding
    wrapper = MultiEncodingWrapper(num_layers=3)
    payload = "complex_payload_for_testing"
    encoded = wrapper.encode(payload)

    # Array encoding
    config = EncoderConfig(
        chunk_size=12,
        encoding_type=EncodingType.HEX,
        chunking_strategy=ChunkingStrategy.VARIABLE_SIZE,
        min_chunk_size=6,
        max_chunk_size=20
    )
    array_encoder = ArrayEncoder(config)
    array_result = array_encoder.encode(encoded)

    # Generate reports
    print("\n" + wrapper.generate_wrapper_report())

    print("Array Encoding Summary:")
    print(f"  Strategy: {array_result['strategy']}")
    print(f"  Chunks: {array_result['count']}")
    print(f"  Chunk Sizes: {[len(c) for c in array_result['chunks'][:5]]}...")

    # Size analysis
    original_size = len(payload)
    multi_size = len(encoded)
    array_size = sum(len(c) for c in array_result['chunks'])

    print(f"\nSize Analysis:")
    print(f"  Original payload: {original_size} bytes")
    print(f"  After multi-encoding: {multi_size} bytes ({multi_size/original_size:.2f}x)")
    print(f"  After array encoding: {array_size} bytes ({array_size/original_size:.2f}x)")
    print(f"  Total expansion: {array_size/original_size:.2f}x")


def main():
    """Run all integration examples"""
    print("\n" + "=" * 70)
    print("MULTI-ENCODING + ARRAY ENCODER INTEGRATION EXAMPLES")
    print("=" * 70)

    example_multiencoding_then_array()
    example_custom_python_decoder()
    example_powershell_integration()
    example_batch_encoding_arrays()
    example_variable_layers()
    example_xor_with_custom_key()
    example_comprehensive_report()

    print("\n" + "=" * 70)
    print("All integration examples completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
