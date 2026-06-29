# Command Obfuscation Utility

A comprehensive command obfuscation system using environment variables and string concatenation techniques. Includes both Bash and Python implementations with multiple encoding strategies.

## Overview

This utility provides several obfuscation methods to encode and decode commands:

1. **Hex Encoding** - Convert to hexadecimal representation
2. **Base64 Encoding** - Standard base64 encoding
3. **ROT13 Encoding** - Rotation cipher (ROT13)
4. **Reverse String** - Simple string reversal
5. **Caesar Cipher** - Shift-based cipher (configurable shift)
6. **Character Substitution** - Replace characters (a→4, e→3, etc.)
7. **XOR Encoding** - XOR cipher with key
8. **Multi-layer Encoding** - Combine multiple methods
9. **Hash Verification** - Sign obfuscated commands with SHA256
10. **Environment Variable Concatenation** - Build commands from env vars

## Files

- `obfuscator.sh` - Bash implementation
- `obfuscator.py` - Python implementation with extended features

## Installation

```bash
# Make executable
chmod +x obfuscator.sh obfuscator.py

# Add to PATH (optional)
export PATH="$PATH:$(pwd)"
```

## Python Usage

### Run Demonstrations

```bash
python3 obfuscator.py demo
```

### Command-Line Interface

```bash
# Hex encoding
python3 obfuscator.py hex_encode "ls -la /tmp"
# Output: 6c73202d6c61202f746d70

# Hex decoding
python3 obfuscator.py hex_decode "6c73202d6c61202f746d70"
# Output: ls -la /tmp

# Base64 encoding
python3 obfuscator.py b64_encode "whoami"
# Output: d2hvYW1p

# Base64 decoding
python3 obfuscator.py b64_decode "d2hvYW1p"
# Output: whoami

# ROT13 encoding/decoding
python3 obfuscator.py rot13 "ls -la /tmp"
# Output: yf -yn /gzc

# Reverse string
python3 obfuscator.py reverse "ls -la /tmp"
# Output: pmt/ al- sl

# Caesar cipher (shift=3)
python3 obfuscator.py caesar "ls -la /tmp"
# Output: ov -od /wps

# Multi-layer encoding
python3 obfuscator.py multi "ls -la /tmp"
# Output: AzZ3ZmVjZzD2LmLkZwNlMwp0AzD3ZN==
```

### Python API

```python
from obfuscator import CommandObfuscator

obf = CommandObfuscator()

# Hex encoding
encoded = obf.hex_encode("ls -la")
decoded = obf.hex_decode(encoded)

# Base64 encoding
encoded = obf.b64_encode("whoami")
decoded = obf.b64_decode(encoded)

# ROT13
encoded = obf.rot13("secret command")

# Multi-layer obfuscation
encoded = obf.multi_layer_encode("sensitive command", layers=3)
decoded = obf.multi_layer_decode(encoded, layers=3)

# Hash verification
encoded, cmd_hash = obf.obfuscate_with_hash("cat /etc/passwd")
verified = obf.verify_obfuscated(encoded, cmd_hash)

# Environment variable concatenation
cmd = obf.dynamic_command_builder("$CMD_LS", "$FLAG_A", "/tmp")
```

## Bash Usage

### Setup Environment

```bash
source obfuscator.sh
setup_obfuscation_env
```

### Hex Encoding Examples

```bash
# Encode a command
source obfuscator.sh
hex_encode_cmd "echo 'secret'"
# Output: 6563686f202773656372657427

# Decode command
hex_decode_exec "6563686f202773656372657427"
# Output: echo 'secret'
```

### Base64 Examples

```bash
source obfuscator.sh

# Encode
b64_encode_cmd "whoami"
# Output: d2hvYW1p

# Decode and execute
b64_decode_exec "d2hvYW1p"
```

### Environment Variable Method

```bash
source obfuscator.sh
setup_obfuscation_env

# Build command from environment variables
build_obfuscated_cmd "OBF_CMD_LS" "OBF_FLAG_LA" "/tmp"
# Output: ls la /tmp
```

### Run Examples

```bash
bash obfuscator.sh examples
```

## Advanced Techniques

### Multi-Layer Obfuscation

```python
from obfuscator import CommandObfuscator

obf = CommandObfuscator()

# Apply 3 layers: Hex → Base64 → ROT13
sensitive_cmd = "cat /etc/shadow"
encoded = obf.multi_layer_encode(sensitive_cmd, layers=3)
print(f"Obfuscated: {encoded}")

# Reverse the process
decoded = obf.multi_layer_decode(encoded, layers=3)
print(f"Decoded: {decoded}")
```

### Hash Verification

```python
# Sign and verify commands
encoded, cmd_hash = obf.obfuscate_with_hash("sudo rm -rf /")
print(f"Encoded: {encoded}")
print(f"Hash: {cmd_hash}")

# Later, verify integrity
if obf.verify_obfuscated(encoded, cmd_hash):
    print("Command verified!")
else:
    print("Warning: Command has been tampered with!")
```

### XOR Encoding with Key

```python
# XOR encode with custom key
command = "secret message"
key = "mykey123"
encoded = obf.xor_encode(command, key)

# Decode
decoded = obf.xor_decode(encoded, key)
```

### Polyalphabetic Cipher

```python
# Vigenère-like cipher
command = "sensitive data"
key = "secretkey"
encoded = obf.polyalphabetic_cipher(command, key)
# Decoding uses the same function with reversed logic
```

## Real-World Examples

### Obfuscating Shell Scripts

```bash
#!/bin/bash
source obfuscator.sh
setup_obfuscation_env

# Obfuscate sensitive operations
SECRET_CMD=$(b64_encode_cmd "cat /etc/shadow")

# Store obfuscated
echo "Executing: $SECRET_CMD"

# Execute when needed
eval "$(b64_decode_exec "$SECRET_CMD")"
```

### API Key Protection

```python
from obfuscator import CommandObfuscator

obf = CommandObfuscator()

# Protect API credentials
api_key = "sk-1234567890abcdef"
protected = obf.multi_layer_encode(api_key, layers=2)

# Store in config
config = {
    "api_key_obf": protected,
    "method": "multi_layer_2"
}

# Decode when needed
if config["method"] == "multi_layer_2":
    api_key = obf.multi_layer_decode(protected, layers=2)
```

### Command Audit Trail

```python
from obfuscator import CommandObfuscator
import json

obf = CommandObfuscator()

# Log commands with hash verification
commands = [
    "ls -la /home",
    "cat /etc/passwd",
    "whoami"
]

audit_log = []
for cmd in commands:
    encoded, cmd_hash = obf.obfuscate_with_hash(cmd)
    audit_log.append({
        "command": encoded,
        "hash": cmd_hash,
        "timestamp": "2026-06-29T00:00:00Z"
    })

# Save audit log
with open("audit.json", "w") as f:
    json.dump(audit_log, f, indent=2)
```

## Encoding Comparison

| Method | Speed | Reversibility | Security | Use Case |
|--------|-------|---------------|----------|----------|
| Hex | Fast | Trivial | Low | Obfuscation only |
| Base64 | Fast | Trivial | Low | Obfuscation + encoding |
| ROT13 | Fast | Trivial | Low | Educational |
| Reverse | Very Fast | Trivial | Very Low | Simple masking |
| Caesar | Fast | Easy | Very Low | Basic cipher |
| XOR | Fast | Depends on key | Medium | Simple encryption |
| Multi-layer | Slow | Very Hard | High | Strong obfuscation |
| Hash Verification | Medium | N/A | High | Integrity checking |

## Security Considerations

**⚠️ WARNING: Obfuscation ≠ Encryption**

This utility provides obfuscation only. For sensitive data protection:

1. Use proper encryption (AES, RSA) for sensitive commands
2. Never rely on obfuscation for security
3. Combine with access controls and authentication
4. Use multi-layer encoding for basic obscurity
5. Implement proper key management for XOR/Caesar variants
6. Always verify command integrity with hash verification

## Performance Notes

- **Fastest**: Reverse, Caesar, Hex
- **Medium**: Base64, ROT13
- **Slowest**: Multi-layer encoding

For performance-critical applications, prefer single-layer encoding.

## Troubleshooting

### Python Decoding Fails

```python
# Ensure correct layer count
try:
    decoded = obf.multi_layer_decode(encoded, layers=3)
except Exception as e:
    print(f"Decoding failed: {e}")
    # Try with different layer count
    decoded = obf.multi_layer_decode(encoded, layers=2)
```

### Bash Commands Not Executing

```bash
# Ensure proper quoting
CMD=$(hex_encode_cmd "ls -la")
eval "$(hex_decode_exec "$CMD")"

# Check for special characters
# May need additional escaping with complex commands
```

## Examples in Action

```bash
# Simple obfuscation chain
echo "whoami" | while read cmd; do
    python3 obfuscator.py hex_encode "$cmd"
done

# Multiple encoding methods
for method in hex b64 rot13 reverse; do
    echo "Method: $method"
    python3 obfuscator.py $method "ls -la /tmp"
done

# Decode from hex file
hex_content=$(cat encoded.hex)
python3 obfuscator.py hex_decode "$hex_content" | bash
```

## API Reference

### CommandObfuscator Methods

- `hex_encode(command: str) -> str`
- `hex_decode(hex_string: str) -> str`
- `b64_encode(command: str) -> str`
- `b64_decode(b64_string: str) -> str`
- `rot13(text: str) -> str`
- `reverse(command: str) -> str`
- `caesar_cipher(command: str, shift=3) -> str`
- `caesar_decipher(command: str, shift=3) -> str`
- `xor_encode(command: str, key="obfuscate") -> bytes`
- `xor_decode(encoded: bytes, key="obfuscate") -> str`
- `multi_layer_encode(command: str, layers=3) -> str`
- `multi_layer_decode(encoded: str, layers=3) -> str`
- `obfuscate_with_hash(command: str) -> Tuple[str, str]`
- `verify_obfuscated(encoded: str, expected_hash: str) -> bool`
- `character_substitution(command: str) -> str`
- `polyalphabetic_cipher(command: str, key="secret") -> str`

## License

Available for educational and authorized security testing purposes.

## Disclaimer

This tool is for authorized use only. Obfuscating commands to hide malicious activity is illegal.
Always ensure you have proper authorization before using command obfuscation in any environment.
