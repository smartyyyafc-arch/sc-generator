# Command String Obfuscation Engine

## Overview

The **Command String Obfuscator** is a comprehensive Python-based tool for encoding command strings, storing them in obfuscated variables, and generating decoders for multiple target languages (Python, VBS, PowerShell, Bash).

### Key Features

- **Multiple Encoding Methods**: Base64, Hex, XOR, Array Chunking, Nested Multi-layer, Polymorphic
- **Multi-Platform Support**: Python, VBS, PowerShell, Bash, Windows Batch
- **Obfuscation Levels**: Configurable 1-5 levels of obfuscation
- **Polymorphic Generation**: Different encoding each execution
- **Roundtrip Verification**: Encode/decode with lossless reconstruction
- **Comprehensive Reports**: Full analysis with all platform payloads
- **Batch Processing**: Handle multiple commands efficiently

---

## Installation

```bash
# No external dependencies required - uses only Python stdlib
python3 command_string_obfuscator.py
```

---

## Quick Start

### Example 1: Basic Encoding

```python
from command_string_obfuscator import encode_command, EncodingMethod

# One-liner encoding
result = encode_command("echo hello", EncodingMethod.BASE64)

print("Encoded:", result['encoded_data'])
print("Decoder:\n", result['decoder_code'])
```

### Example 2: VBS Payload

```python
from command_string_obfuscator import encode_to_vbs

command = "powershell.exe -NoProfile -Command Write-Host Test"
vbs_payload = encode_to_vbs(command)
print(vbs_payload)
```

### Example 3: PowerShell Payload

```python
from command_string_obfuscator import encode_to_powershell

command = "Get-Process"
ps_payload = encode_to_powershell(command)
print(ps_payload)
```

### Example 4: Bash Payload

```python
from command_string_obfuscator import encode_to_bash

command = "cat /etc/passwd"
bash_payload = encode_to_bash(command)
print(bash_payload)
```

---

## Encoding Methods

### 1. Base64 (Default)

**Best for**: Simple encoding, basic obfuscation

```python
result = encode_command("whoami", EncodingMethod.BASE64)
# Encoded: d2hvYW1p
```

**Advantages**:
- Smallest overhead
- Fastest encoding/decoding
- Universal support
- Text-safe representation

**Use Cases**:
- Quick encoding
- Web payloads
- Log obfuscation

---

### 2. Hex

**Best for**: Binary-safe encoding, moderate obfuscation

```python
result = encode_command("ipconfig", EncodingMethod.HEX)
# Encoded: 6970636f6e666967
```

**Advantages**:
- Zero data loss
- Debuggable format
- Platform independent

**Use Cases**:
- Binary command payloads
- Detailed debugging
- Cross-platform deployment

---

### 3. XOR (Key-Based)

**Best for**: Key-based obfuscation, anti-signature

```python
result = encode_command("cmd.exe", EncodingMethod.XOR)
# Includes XOR key in metadata
```

**Advantages**:
- Key derivation from command hash
- Unique per command
- Consistent key for same command

**Use Cases**:
- Anti-malware evasion
- Per-command key management
- Signature breaking

---

### 4. Array Chunking

**Best for**: Large commands, chunk-based processing

```python
config = CommandObfuscationConfig(
    encoding_method=EncodingMethod.ARRAY,
    chunk_size=16
)
obfuscator = CommandStringObfuscator(config)
result = obfuscator.obfuscate_command("long command...")
```

**Advantages**:
- Splits command into chunks
- Independent chunk processing
- Distributable encoding

**Use Cases**:
- Large command payloads
- Distributed execution
- Staged delivery

---

### 5. Nested (Multi-Layer)

**Best for**: Maximum obfuscation, defense-in-depth

```python
result = encode_command("secret", EncodingMethod.NESTED)
# Base64 → Hex → Reverse
```

**Layers**:
1. Base64 encoding
2. Hex encoding (of base64)
3. String reversal

**Advantages**:
- Multiple layers of obfuscation
- Complex decoding chain
- Signature breaking

**Use Cases**:
- High-security scenarios
- Advanced threat modeling
- Multi-layer defense

---

### 6. Polymorphic

**Best for**: Evasion, unique signatures each time

```python
result1 = encode_command("test", EncodingMethod.POLYMORPH)
result2 = encode_command("test", EncodingMethod.POLYMORPH)
# Different encodings, same command!
```

**Advantages**:
- Randomly selects encoding method
- Different output each generation
- Polymorphic key tracking

**Use Cases**:
- Malware research
- Evasion testing
- Signature breaking

---

## Configuration

### ObfuscationConfig Parameters

```python
from command_string_obfuscator import CommandObfuscationConfig, EncodingMethod

config = CommandObfuscationConfig(
    encoding_method=EncodingMethod.BASE64,  # Which method to use
    variable_obfuscation=True,               # Randomize var names
    use_function_wrappers=True,              # Wrap in functions
    add_dead_code=True,                      # Add decoy code
    randomize_names=True,                    # Randomize identifiers
    obfuscation_level=3,                     # 1-5, higher = more obfuscation
    xor_key=None,                            # Optional XOR key
    chunk_size=16,                           # For array encoding
    add_anti_debug=False,                    # Anti-debugging features
    use_environment_vars=True                # Use env vars
)
```

---

## API Reference

### Main Classes

#### CommandStringObfuscator

```python
obfuscator = CommandStringObfuscator(config)

# Obfuscate command
result = obfuscator.obfuscate_command("command")

# Generate language-specific payloads
vbs = obfuscator.generate_vbs_payload("command")
ps = obfuscator.generate_powershell_payload("command")
bash = obfuscator.generate_bash_payload("command")
python_code = obfuscator.generate_python_payload("command")

# Generate comprehensive report
report = obfuscator.generate_full_report("command")
```

#### Individual Encoders

```python
encoder = Base64CommandEncoder(config)
encoded, metadata = encoder.encode("command")
decoder_code = encoder.generate_decoder_code(encoded, metadata)
```

Available encoders:
- `Base64CommandEncoder`
- `HexCommandEncoder`
- `XORCommandEncoder`
- `ArrayCommandEncoder`
- `NestedCommandEncoder`
- `PolymorphicCommandEncoder`

### Convenience Functions

```python
# Quick encoding
result = encode_command("cmd", EncodingMethod.BASE64)

# Quick payload generation
vbs = encode_to_vbs("cmd")
ps = encode_to_powershell("cmd")
bash = encode_to_bash("cmd")
```

---

## Result Format

All encoding functions return a `Dict` with:

```python
{
    "original_command": str,          # Original command
    "encoded_data": str,              # Encoded representation
    "metadata": {
        "method": str,                # Encoding method used
        "original_length": int,       # Command byte size
        "encoded_length": int,        # Encoded byte size
        "variable_name": str,         # Obfuscated var name
        "decoder_name": str,          # Decoder function name
        # ... method-specific fields
    },
    "decoder_code": str,              # Python decoder code
    "decoder_language": str,          # "python"
    "obfuscation_level": int,         # 1-5
}
```

---

## Platform Payloads

### VBS (Windows)

```python
payload = obfuscator.generate_vbs_payload(command)
# Creates:
# - MSXML2.DOMDocument-based base64 decoder
# - Or hex decoder function
# - WScript.Shell execution wrapper
```

**Output Format**:
```vbs
Dim variable_name, ...
' Decoder implementation
Set shell = CreateObject("WScript.Shell")
shell.Run decoded_cmd, 0, False
```

### PowerShell

```python
payload = obfuscator.generate_powershell_payload(command)
# Creates:
# - .NET UTF8/Base64 decoding
# - Invoke-Expression execution
```

**Output Format**:
```powershell
$cmd = "..."
$decoded = [System.Text.Encoding]::UTF8.GetString(...)
Invoke-Expression $decoded
```

### Bash

```python
payload = obfuscator.generate_bash_payload(command)
# Creates:
# - Base64/Hex decoding via base64 or xxd
# - eval execution
```

**Output Format**:
```bash
#!/bin/bash
cmd="..."
decoded_cmd=$(echo "$cmd" | base64 -d)
eval "$decoded_cmd"
```

### Python (Standalone)

```python
payload = obfuscator.generate_python_payload(command)
# Creates complete standalone Python script
# - Imports and functions
# - Decoding logic
# - subprocess execution
```

---

## Usage Examples

### Example 1: Basic Encoding

```python
from command_string_obfuscator import encode_command, EncodingMethod

result = encode_command("echo test", EncodingMethod.BASE64)
print(result['encoded_data'])      # ZWNobyB0ZXN0
print(result['decoder_code'])      # Python code
```

### Example 2: Multi-Platform Deployment

```python
from command_string_obfuscator import CommandStringObfuscator, CommandObfuscationConfig, EncodingMethod

config = CommandObfuscationConfig(encoding_method=EncodingMethod.HEX)
obfuscator = CommandStringObfuscator(config)

cmd = "whoami"

# Generate for all platforms
python_decoder = obfuscator.obfuscate_command(cmd)['decoder_code']
vbs_payload = obfuscator.generate_vbs_payload(cmd)
ps_payload = obfuscator.generate_powershell_payload(cmd)
bash_payload = obfuscator.generate_bash_payload(cmd)

# Use each as needed
```

### Example 3: Batch Processing

```python
commands = [
    "ipconfig",
    "tasklist",
    "systeminfo",
    "whoami",
]

obfuscator = CommandStringObfuscator()

for cmd in commands:
    result = obfuscator.obfuscate_command(cmd)
    print(f"{cmd}: {result['encoded_data'][:50]}...")

print(f"Total: {len(obfuscator._obfuscation_history)} obfuscations")
```

### Example 4: Polymorphic Variant Generation

```python
from command_string_obfuscator import EncodingMethod

# Generate 5 different encodings of same command
for i in range(5):
    result = encode_command("test", EncodingMethod.POLYMORPH)
    method = result['metadata']['selected_encoder']
    key = result['metadata']['polymorphic_key']
    print(f"Variant {i+1}: {method} (Key: {key})")
```

### Example 5: High-Obfuscation Report

```python
from command_string_obfuscator import CommandStringObfuscator, CommandObfuscationConfig

config = CommandObfuscationConfig(obfuscation_level=5)
obfuscator = CommandStringObfuscator(config)

report = obfuscator.generate_full_report("secret command")
print(report)
# Outputs comprehensive analysis with all platform payloads
```

---

## Testing

### Run All Tests

```bash
python3 test_command_string_obfuscator.py
```

### Test Coverage

- ✓ Base64 encoding/decoding
- ✓ Hex encoding/decoding
- ✓ XOR key derivation
- ✓ Array chunking
- ✓ Nested multi-layer encoding
- ✓ Polymorphic generation
- ✓ VBS payload generation
- ✓ PowerShell payload generation
- ✓ Bash payload generation
- ✓ Python payload generation
- ✓ Roundtrip verification
- ✓ Complex command handling
- ✓ Large command support
- ✓ Batch processing
- ✓ Performance benchmarks

### Run Examples

```bash
# Run all examples
python3 command_obfuscation_examples.py

# Run specific example (1-16)
python3 command_obfuscation_examples.py 1
python3 command_obfuscation_examples.py 7
python3 command_obfuscation_examples.py 15
```

---

## Performance

### Benchmarks

| Method | Time/100 ops | Output Size | Compression |
|--------|--------------|-------------|------------|
| Base64 | ~0.5ms | ~133% | 33% overhead |
| Hex | ~0.3ms | ~200% | 100% overhead |
| XOR | ~1.0ms | ~200% | 100% overhead |
| Array | ~2.0ms | ~200% | 100% overhead |
| Nested | ~1.5ms | ~250% | 150% overhead |
| Polymorph | ~1.0ms | Variable | Variable |

**Throughput**: ~200,000 commands/second (Base64)

---

## Security Considerations

### Strengths

✓ Prevents casual command inspection
✓ Breaks string-based signatures
✓ Multiple encoding layers available
✓ Polymorphic generation for uniqueness
✓ Key-based XOR variant

### Limitations

⚠ Not cryptographic - single layer is reversible
⚠ Metadata visible in decoder code
⚠ Variable names still extractable
⚠ Memory inspection possible
⚠ Plaintext at execution time

### Recommended Use

- **Authorized security testing**
- **Penetration testing research**
- **Malware analysis (controlled)**
- **Blue team defense testing**

### NOT for

- Hiding malicious code
- Evading antivirus (use cryptographic obfuscation)
- Protecting intellectual property (use encryption)
- Unauthorized access attempts

---

## Advanced Usage

### Custom Variable Names

```python
config = CommandObfuscationConfig(randomize_names=True)
# Names like: v_aB3xY9zQ, decode_Fn4mK8pL
```

### XOR with Custom Key

```python
config = CommandObfuscationConfig(
    encoding_method=EncodingMethod.XOR,
    xor_key=42  # Custom key
)
```

### Array Chunking

```python
config = CommandObfuscationConfig(
    encoding_method=EncodingMethod.ARRAY,
    chunk_size=32  # Larger chunks
)
```

### Batch with History

```python
obfuscator = CommandStringObfuscator()
for cmd in commands:
    obfuscator.obfuscate_command(cmd)

# Access history
for entry in obfuscator._obfuscation_history:
    print(entry['original_command'])
```

---

## Troubleshooting

### Command Not Decoding Correctly

- Verify encoding method matches decoder
- Check for character encoding issues
- Ensure variable names are correct
- Test roundtrip with same encoder

### VBS Errors

- Ensure MSXML2.DOMDocument is available
- Check WScript.Shell execution permissions
- Verify command syntax for target system

### PowerShell Issues

- Verify .NET Framework version
- Check execution policy allows Invoke-Expression
- Ensure UTF8 encoding compatibility

### Bash Compatibility

- Use `base64 -d` for decoding (not `-D`)
- For hex, use `xxd -r -p` or `od` fallback
- Ensure sh/bash availability

---

## File Structure

```
command_string_obfuscator.py          # Main module
├─ CommandObfuscationConfig          # Configuration dataclass
├─ EncodingMethod                    # Encoding enum
├─ CommandEncoder (ABC)              # Base encoder class
├─ Base64CommandEncoder              # Base64 implementation
├─ HexCommandEncoder                 # Hex implementation
├─ XORCommandEncoder                 # XOR implementation
├─ ArrayCommandEncoder               # Array chunking
├─ NestedCommandEncoder              # Multi-layer
├─ PolymorphicCommandEncoder         # Random selection
└─ CommandStringObfuscator           # Main class

test_command_string_obfuscator.py     # Test suite (31 tests)
command_obfuscation_examples.py       # 16 examples + demonstrations
COMMAND_OBFUSCATOR_README.md          # This documentation
```

---

## License & Disclaimer

**For authorized security research and penetration testing only.**

This tool is provided for:
- ✓ Educational purposes
- ✓ Authorized security testing
- ✓ Red team operations
- ✓ Malware analysis research

This tool is NOT for:
- ✗ Unauthorized system access
- ✗ Malware distribution
- ✗ Illegal activities
- ✗ Harm or exploitation

---

## Contributing

Improvements welcome:
- Additional encoding methods
- Platform-specific optimizations
- Better anti-debugging
- Performance enhancements

---

## Support

### Quick Reference

```python
# One-liner encoding
result = encode_command("cmd", EncodingMethod.BASE64)

# Multi-platform payloads
vbs = encode_to_vbs("cmd")
ps = encode_to_powershell("cmd")
bash = encode_to_bash("cmd")

# Full configuration
config = CommandObfuscationConfig(...)
obfuscator = CommandStringObfuscator(config)
result = obfuscator.obfuscate_command("cmd")
```

See `command_obfuscation_examples.py` for 16 complete examples.

---

## Changelog

### v1.0
- Initial release
- 6 encoding methods
- 4 platform targets
- Comprehensive test suite
- Full documentation
- 16 example programs
