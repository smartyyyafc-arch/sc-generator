# Base64 Encoder - Reverse Operations Guide

## Overview

The Base64 Encoder provides a comprehensive suite for encoding text and binary data to Base64 format, specifically designed to pair with the existing VBS decoder implementations in the project.

## Core Classes

### 1. Base64Encoder

The main encoder class providing core Base64 encoding functionality.

**Key Methods:**

- **`encode_to_base64(text: str) -> str`**: Encode plain text to Base64 string
- **`encode_to_base64_with_cache(text: str) -> Tuple[str, str]`**: Encode with caching support
- **`encode_command_payload(command: str) -> str`**: Encode command for VBS payload
- **`encode_file_content(file_content: str) -> str`**: Encode file content
- **`encode_bytes_to_base64(data: bytes) -> str`**: Encode binary bytes to Base64
- **`create_vbs_encoded_variable(text: str, var_name: Optional[str]) -> str`**: Create VBS code with encoded variable
- **`create_vbs_decoder_pair(text: str) -> Tuple[str, str]`**: Create paired encoder-decoder VBS code
- **`create_powershell_encoded_command(command: str) -> str`**: Create PowerShell UTF-16LE encoded command
- **`batch_encode_multiple(texts: list) -> dict`**: Encode multiple texts at once
- **`verify_encoding(original: str, encoded: str) -> bool`**: Verify encoding correctness
- **`create_reverse_lookup_table(texts: list) -> dict`**: Create bidirectional lookup tables

### 2. Base64OperationsPair

Symmetric encoder-decoder class providing matched operations.

**Key Methods:**

- **`encode(text: str) -> str`**: Encode text to Base64
- **`decode(encoded: str) -> str`**: Decode Base64 to text
- **`encode_with_validation(text: str) -> str`**: Encode with validation
- **`round_trip_transform(text: str) -> bool`**: Test encode-decode round trip

## Usage Examples

### Example 1: Simple Encoding

```python
from base64_encoder import Base64Encoder

encoder = Base64Encoder()
text = "powershell.exe -NoProfile -Command \"Get-Process\""
encoded = encoder.encode_to_base64(text)
print(encoded)  # cG93ZXJzaGVsbC5leGUgLU5vUHJvZmlsZSAtQ29tbWFuZCAiR2V0LVByb2Nlc3Mi
```

### Example 2: VBS Encoded Variable

```python
from base64_encoder import Base64Encoder

encoder = Base64Encoder()
payload = "net user Administrator /active:yes"
vbs_code = encoder.create_vbs_encoded_variable(payload, "encPayload")
print(vbs_code)
# Output:
# Dim encPayload
# encPayload = "bmV0IHVzZXIgQWRtaW5pc3RyYXRvciAvYWN0aXZlOnllcw=="
```

### Example 3: Paired Encoder-Decoder

```python
from base64_encoder import Base64Encoder

encoder = Base64Encoder()
text = "Test Command"
encoder_code, decoder_code = encoder.create_vbs_decoder_pair(text)
print("Encoder:\n", encoder_code)
print("\nDecoder:\n", decoder_code)
```

### Example 4: PowerShell Encoding

```python
from base64_encoder import Base64Encoder

encoder = Base64Encoder()
command = "Write-Host 'Hello World'"
ps_encoded = encoder.create_powershell_encoded_command(command)
print(ps_encoded)  # UTF-16LE encoded for -EncodedCommand
```

### Example 5: Batch Encoding

```python
from base64_encoder import Base64Encoder

encoder = Base64Encoder()
commands = ["whoami", "ipconfig /all", "tasklist", "systeminfo"]
encoded_commands = encoder.batch_encode_multiple(commands)

for cmd, encoded in encoded_commands.items():
    print(f"{cmd} -> {encoded}")
```

### Example 6: Round-Trip Verification

```python
from base64_encoder import Base64OperationsPair

ops = Base64OperationsPair()
text = "Round trip test"
success = ops.round_trip_transform(text)
print(f"Round trip successful: {success}")
```

### Example 7: Reverse Lookup Table

```python
from base64_encoder import Base64Encoder

encoder = Base64Encoder()
commands = ["net user", "ipconfig", "tasklist"]
lookup = encoder.create_reverse_lookup_table(commands)

# Forward: plain text -> encoded
print(lookup['forward']['net user'])  # bmV0IHVzZXI=

# Reverse: encoded -> plain text
print(lookup['reverse']['bmV0IHVzZXI='])  # net user
```

## Integration with VBS Decoder

The encoder is designed to pair seamlessly with the existing VBS decoder:

### VBS Decoder Example (from vbs_encoder.py)

```vbs
Dim encodedPayload
encodedPayload = "Y21kIC9jIGVjaG8gdGVzdA=="
Set xmlDoc = CreateObject("MSXML2.DOMDocument")
With xmlDoc
    .LoadXML "<u><![CDATA[" & encodedPayload & "]]></u>"
    decodedPayload = .SelectSingleNode("u").text
End With
```

### Python Encoder Usage

```python
from base64_encoder import Base64Encoder

encoder = Base64Encoder()
command = "cmd /c echo test"
encoded = encoder.encode_to_base64(command)
# encoded = "Y21kIC9jIGVjaG8gdGVzdA=="
# This matches what the VBS decoder expects
```

## Features

### Caching

The encoder supports optional caching for performance optimization:

```python
encoder = Base64Encoder()
# First call - performs encoding
encoded1, key1 = encoder.encode_to_base64_with_cache("test")
# Second call - returns cached result
encoded2, key2 = encoder.encode_to_base64_with_cache("test")
# encoded1 == encoded2, key1 == key2
```

### Verification

Built-in verification ensures encoding correctness:

```python
encoder = Base64Encoder()
original = "Test String"
encoded = encoder.encode_to_base64(original)
is_valid = encoder.verify_encoding(original, encoded)  # True
```

### Error Handling

The encoder includes comprehensive error handling:

```python
from base64_encoder import Base64Encoder

encoder = Base64Encoder()

# Type checking
try:
    encoder.encode_to_base64(12345)  # Raises TypeError
except TypeError as e:
    print(f"Type error: {e}")

# Invalid bytes
try:
    encoder.encode_bytes_to_base64("not bytes")  # Raises TypeError
except TypeError as e:
    print(f"Type error: {e}")
```

## Command-Line Usage

The encoder can be run directly for quick encoding:

```bash
python3 base64_encoder.py
```

This runs built-in examples showing all major features.

## Test Suite

A comprehensive test suite is included:

```bash
python3 test_base64_encoder.py
```

Tests cover:
- Basic encoding operations
- Caching functionality
- Round-trip transformations
- Verification operations
- Batch operations
- Lookup tables
- PowerShell encoding
- VBS integration
- Bytes handling
- Error conditions

All 32 tests pass successfully.

## Integration Points

### With VBSEncoder

```python
from vbs_encoder import VBSEncoder
from base64_encoder import Base64Encoder

vbs_encoder = VBSEncoder()
b64_encoder = Base64Encoder()

# Encode command
command = "powershell.exe -NoProfile -Command \"Get-Process\""
encoded = b64_encoder.encode_to_base64(command)

# Create VBS decoder for this payload
vbs_decoder = vbs_encoder.create_base64_decoder_vbs(command)
```

### With Payload Generation

```python
from base64_encoder import Base64Encoder
from payload_generator import PayloadGenerator

encoder = Base64Encoder()
payload_gen = PayloadGenerator()

# Encode then generate
encoded_payload = encoder.encode_to_base64("malicious command")
generated_code = payload_gen.generate(encoded_payload)
```

## Performance Considerations

- **Caching**: Enables reuse of encodings for repeated texts
- **Batch Operations**: Process multiple texts efficiently
- **Lookup Tables**: Fast reverse lookups with O(1) access
- **Memory**: Efficient handling of large payloads (tested with 50KB+)

## Security Notes

This encoder is designed for authorized security testing and penetration testing purposes. Always ensure:

1. Proper authorization for use
2. Clear documentation of testing scope
3. Compliance with applicable laws and regulations
4. Ethical use in authorized environments only

## File Structure

```
/home/user/sc-generator/
├── base64_encoder.py              # Main encoder implementation
├── encoder_decoder_example.py      # 10 comprehensive examples
├── test_base64_encoder.py         # 32-test unit suite
└── BASE64_ENCODER_GUIDE.md        # This documentation
```

## API Reference

See `base64_encoder.py` for complete API documentation and method signatures.
