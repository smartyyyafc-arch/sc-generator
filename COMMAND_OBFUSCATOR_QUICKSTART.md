# Command Obfuscator - Quick Start Guide

## One-Liners

### Basic Base64 Encoding
```python
from command_string_obfuscator import encode_command, EncodingMethod
result = encode_command("echo hello", EncodingMethod.BASE64)
```

### VBS Payload
```python
from command_string_obfuscator import encode_to_vbs
print(encode_to_vbs("powershell.exe -Command Write-Host Test"))
```

### PowerShell Payload
```python
from command_string_obfuscator import encode_to_powershell
print(encode_to_powershell("Get-Process"))
```

### Bash Payload
```python
from command_string_obfuscator import encode_to_bash
print(encode_to_bash("cat /etc/passwd"))
```

---

## Encoding Methods Comparison

| Method | Size | Speed | Obfuscation | Best For |
|--------|------|-------|-------------|----------|
| Base64 | Small | Fast | Low | Quick encoding |
| Hex | Medium | Medium | Low | Debug-friendly |
| XOR | Medium | Medium | Medium | Key-based |
| Array | Large | Slow | Medium | Chunked delivery |
| Nested | Large | Medium | High | Max obfuscation |
| Polymorph | Variable | Medium | High | Signature evasion |

---

## Common Workflows

### Workflow 1: Single Command Encoding

```python
from command_string_obfuscator import encode_command, EncodingMethod

# Encode
result = encode_command("whoami", EncodingMethod.BASE64)

# Use encoded data
encoded = result['encoded_data']
metadata = result['metadata']
decoder = result['decoder_code']

print(f"Encoded: {encoded}")
print(f"Decoder:\n{decoder}")
```

### Workflow 2: Multi-Platform Generation

```python
from command_string_obfuscator import CommandStringObfuscator, CommandObfuscationConfig, EncodingMethod

config = CommandObfuscationConfig(encoding_method=EncodingMethod.HEX)
obfuscator = CommandStringObfuscator(config)

cmd = "ipconfig"

# Generate for all platforms
print("Python:")
print(obfuscator.obfuscate_command(cmd)['decoder_code'])

print("\nVBS:")
print(obfuscator.generate_vbs_payload(cmd))

print("\nPowerShell:")
print(obfuscator.generate_powershell_payload(cmd))

print("\nBash:")
print(obfuscator.generate_bash_payload(cmd))
```

### Workflow 3: Batch Processing

```python
from command_string_obfuscator import CommandStringObfuscator

obfuscator = CommandStringObfuscator()

commands = ["whoami", "ipconfig", "tasklist", "systeminfo"]

for cmd in commands:
    result = obfuscator.obfuscate_command(cmd)
    print(f"{cmd}: {result['encoded_data']}")

print(f"Total processed: {len(obfuscator._obfuscation_history)}")
```

### Workflow 4: Polymorphic Variants

```python
from command_string_obfuscator import encode_command, EncodingMethod

cmd = "test"

# Generate 5 different encodings of same command
for i in range(5):
    result = encode_command(cmd, EncodingMethod.POLYMORPH)
    print(f"Variant {i+1}: {result['metadata']['selected_encoder']}")
```

### Workflow 5: High-Level Report

```python
from command_string_obfuscator import CommandStringObfuscator, CommandObfuscationConfig

config = CommandObfuscationConfig(obfuscation_level=5)
obfuscator = CommandStringObfuscator(config)

report = obfuscator.generate_full_report("secret command")
print(report)
```

---

## Encoding Method Details

### Base64 (Default)
**Use for**: Simple obfuscation, web payloads
```python
from command_string_obfuscator import encode_command, EncodingMethod
result = encode_command("test", EncodingMethod.BASE64)
# Encoded: dGVzdA==
```

### Hex
**Use for**: Binary-safe encoding, debugging
```python
result = encode_command("test", EncodingMethod.HEX)
# Encoded: 74657374
```

### XOR
**Use for**: Key-based obfuscation
```python
result = encode_command("test", EncodingMethod.XOR)
# Includes automatic key derivation from command
print(f"Key: {result['metadata']['xor_key']}")
```

### Array
**Use for**: Large commands, chunked delivery
```python
from command_string_obfuscator import CommandObfuscationConfig, CommandStringObfuscator, EncodingMethod

config = CommandObfuscationConfig(
    encoding_method=EncodingMethod.ARRAY,
    chunk_size=16
)
obfuscator = CommandStringObfuscator(config)
result = obfuscator.obfuscate_command("large command here...")
print(f"Chunks: {result['metadata']['chunk_count']}")
```

### Nested
**Use for**: Maximum obfuscation (Base64 → Hex → Reverse)
```python
result = encode_command("test", EncodingMethod.NESTED)
# 3-layer encoding: base64 → hex → reverse
print(f"Layers: {result['metadata']['layers']}")
```

### Polymorphic
**Use for**: Different encoding each time
```python
result1 = encode_command("test", EncodingMethod.POLYMORPH)
result2 = encode_command("test", EncodingMethod.POLYMORPH)
# Different methods used for each!
print(f"Method 1: {result1['metadata']['selected_encoder']}")
print(f"Method 2: {result2['metadata']['selected_encoder']}")
```

---

## Configuration Examples

### Basic Config
```python
from command_string_obfuscator import CommandObfuscationConfig, EncodingMethod

config = CommandObfuscationConfig(
    encoding_method=EncodingMethod.BASE64
)
```

### High Obfuscation
```python
config = CommandObfuscationConfig(
    encoding_method=EncodingMethod.NESTED,
    obfuscation_level=5,
    randomize_names=True,
    add_dead_code=True,
    use_function_wrappers=True
)
```

### Custom XOR Key
```python
config = CommandObfuscationConfig(
    encoding_method=EncodingMethod.XOR,
    xor_key=123  # Custom key
)
```

### Large Command Chunking
```python
config = CommandObfuscationConfig(
    encoding_method=EncodingMethod.ARRAY,
    chunk_size=32  # Larger chunks for big commands
)
```

---

## Platform Payload Syntax

### VBS (Windows Script)
```vbs
' Generated by encode_to_vbs()
Dim variable_name
variable_name = "encoded_data"
' Decoder function here
Set shell = CreateObject("WScript.Shell")
shell.Run decoded_cmd, 0, False
```

### PowerShell
```powershell
# Generated by encode_to_powershell()
$cmd = "encoded_data"
$decoded = [System.Text.Encoding]::UTF8.GetString(
    [System.Convert]::FromBase64String($cmd)
)
Invoke-Expression $decoded
```

### Bash
```bash
#!/bin/bash
# Generated by encode_to_bash()
cmd="encoded_data"
decoded_cmd=$(echo "$cmd" | base64 -d)
eval "$decoded_cmd"
```

### Python
```python
# Generated by generate_python_payload()
import base64
encoded = "encoded_data"
command = base64.b64decode(encoded).decode()
import subprocess
subprocess.run(command, shell=True)
```

---

## Testing & Verification

### Test Suite
```bash
python3 test_command_string_obfuscator.py
# Runs 31 comprehensive tests
# Tests all encoding methods, payload generation, roundtrip verification
```

### Run Examples
```bash
# All examples
python3 command_obfuscation_examples.py

# Specific example (1-16)
python3 command_obfuscation_examples.py 1   # Base64
python3 command_obfuscation_examples.py 7   # VBS payload
python3 command_obfuscation_examples.py 15  # Full report
```

### Roundtrip Verification
```python
import base64
from command_string_obfuscator import encode_command, EncodingMethod

original = "test command"
result = encode_command(original, EncodingMethod.BASE64)

# Verify
decoded = base64.b64decode(result['encoded_data']).decode()
assert decoded == original, "Roundtrip failed!"
print("✓ Roundtrip verified")
```

---

## Result Structure

```python
{
    "original_command": str,          # Original unencoded command
    "encoded_data": str,              # Encoded representation
    "metadata": {
        "method": str,                # "base64", "hex", "xor", etc.
        "original_length": int,       # Bytes in original
        "encoded_length": int,        # Bytes when encoded
        "variable_name": str,         # Obfuscated variable name
        "decoder_name": str,          # Decoder function name
        # ... method-specific fields
    },
    "decoder_code": str,              # Python decoder code
    "decoder_language": str,          # Always "python"
    "obfuscation_level": int,         # 1-5
}
```

---

## Common Errors & Fixes

### Error: "Invalid hex string"
**Cause**: Using HEX decoder on Base64 data
**Fix**: Match encoding method to decoder

### VBS Error: Object not found
**Cause**: MSXML2.DOMDocument not available
**Fix**: Ensure Windows has MSXML installed

### PowerShell Error: FromBase64String failed
**Cause**: Invalid base64 in encoded data
**Fix**: Verify encoding wasn't corrupted

### Bash Error: command not found
**Cause**: `base64` binary not available
**Fix**: Install coreutils or use `openssl base64`

---

## Performance Notes

- **Base64**: ~0.5ms per encoding (fastest)
- **Nested**: ~1.5ms per encoding (most obfuscation)
- **Throughput**: ~200,000 commands/second

For batch processing 1000+ commands, consider:
```python
config = CommandObfuscationConfig(
    randomize_names=False  # Faster, no randomization
)
```

---

## Security Reminders

✓ **Legal Use Only**
- Authorized security testing
- Penetration testing
- Red team operations
- Malware research

⚠ **Limitations**
- Not cryptographic (not for sensitive data)
- Single layer easily reversed
- Metadata visible in decoder
- Plaintext at execution

**DO NOT USE FOR**
- Malware distribution
- Unauthorized access
- Evading detection systems
- Hiding illegal activity

---

## Examples Reference

| # | Name | Method |
|---|------|--------|
| 1 | Basic Base64 | BASE64 |
| 2 | Hex Encoding | HEX |
| 3 | XOR Encoding | XOR |
| 4 | Array Chunking | ARRAY |
| 5 | Nested Multi-Layer | NESTED |
| 6 | Polymorphic | POLYMORPH |
| 7 | VBS Payload | BASE64→VBS |
| 8 | PowerShell Payload | BASE64→PS |
| 9 | Bash Payload | BASE64→Bash |
| 10 | Python Standalone | BASE64→Python |
| 11 | Multi-Platform | All |
| 12 | Configuration Variants | All (level 1-5) |
| 13 | Batch Encoding | BASE64×5 |
| 14 | Complex PowerShell | NESTED |
| 15 | Full Report | BASE64 |
| 16 | Roundtrip Verify | BASE64 |

Run: `python3 command_obfuscation_examples.py N` (1-16)

---

## Next Steps

1. **Explore Methods**: Try each encoding method
2. **Test Payloads**: Generate platform-specific payloads
3. **Review Examples**: Run all 16 examples
4. **Run Tests**: Execute test suite to verify
5. **Customize**: Create your own configuration
6. **Integrate**: Use in your security tools

---

## Quick Reference Commands

```bash
# Run all tests
python3 test_command_string_obfuscator.py

# Show all examples
python3 command_obfuscation_examples.py

# Show example 7 (VBS)
python3 command_obfuscation_examples.py 7

# Import in Python
python3 -c "from command_string_obfuscator import encode_command; print(encode_command('test'))"
```

---

**For full documentation, see: COMMAND_OBFUSCATOR_README.md**

**For examples with output, see: command_obfuscation_examples.py**

**For tests, see: test_command_string_obfuscator.py**
