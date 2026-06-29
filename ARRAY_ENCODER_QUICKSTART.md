# Array Encoder - Quick Start Guide

## Installation

```bash
# No external dependencies required (uses stdlib only)
# Just use array_encoder.py
```

## 5-Minute Quick Start

### 1. Basic Hex to VBScript

```python
from array_encoder import encode_command_to_array

# Encode a command to VBScript array
vbs_code = encode_command_to_array(
    "calc.exe",
    chunk_size=8,
    encoding="hex",
    output_format="vbs"
)

print(vbs_code)
```

Output:
```vbs
' Array encoder: 1 chunks of hex
Dim payload(0)
payload(0) = "63616c632e657865"
```

### 2. Base64 to Python

```python
from array_encoder import encode_command_to_array

code = encode_command_to_array(
    "powershell.exe",
    chunk_size=10,
    encoding="base64",
    output_format="python"
)

print(code)
```

### 3. Longer Command to JavaScript

```python
from array_encoder import encode_command_to_array

cmd = 'powershell.exe -Command "Get-Process"'

js_code = encode_command_to_array(
    cmd,
    chunk_size=16,
    encoding="hex",
    output_format="javascript"
)

print(js_code)
```

## Common Patterns

### Pattern 1: Multiple Encoding Types

```python
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat

# HEX
config_hex = EncoderConfig(encoding_type=EncodingType.HEX, output_format=OutputFormat.PYTHON)
result_hex = ArrayEncoder(config_hex).generate("test")

# BASE64
config_b64 = EncoderConfig(encoding_type=EncodingType.BASE64, output_format=OutputFormat.PYTHON)
result_b64 = ArrayEncoder(config_b64).generate("test")

# OCTAL
config_oct = EncoderConfig(encoding_type=EncodingType.OCTAL, output_format=OutputFormat.PYTHON)
result_oct = ArrayEncoder(config_oct).generate("test")
```

### Pattern 2: All Output Formats

```python
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat

cmd = "notepad.exe"

formats = [
    OutputFormat.PYTHON,
    OutputFormat.VBS,
    OutputFormat.JAVASCRIPT,
    OutputFormat.POWERSHELL,
    OutputFormat.BASH,
    OutputFormat.JSON,
    OutputFormat.C
]

for fmt in formats:
    config = EncoderConfig(encoding_type=EncodingType.HEX, output_format=fmt)
    encoder = ArrayEncoder(config)
    result = encoder.generate(cmd)
    print(f"\n--- {fmt.value} ---\n{result}")
```

### Pattern 3: Variable Chunk Sizes

```python
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat, ChunkingStrategy

config = EncoderConfig(
    chunk_size=16,
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.PYTHON,
    chunking_strategy=ChunkingStrategy.VARIABLE_SIZE,
    min_chunk_size=4,
    max_chunk_size=20
)

encoder = ArrayEncoder(config)
result = encoder.generate("long command string here")
```

### Pattern 4: Randomized Variable Names

```python
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat

config = EncoderConfig(
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.PYTHON,
    randomize_names=True  # Generate random variable names
)

encoder = ArrayEncoder(config)
result = encoder.generate("cmd.exe")
```

### Pattern 5: JSON Output for Integration

```python
from array_encoder import encode_command_to_array
import json

code_str = encode_command_to_array(
    "test.exe /arg",
    chunk_size=8,
    encoding="hex",
    output_format="json"
)

# Parse JSON for integration with other tools
data = json.loads(code_str)
print(f"Chunks: {data['payload']}")
print(f"Count: {data['count']}")
print(f"Encoding: {data['encoding']}")
```

## Encoding Comparison

| Encoding | Size | Use Case |
|----------|------|----------|
| HEX | 2x input | Binary data, reliable |
| BASE64 | 1.33x input | Printable, compact |
| OCTAL | 3x input | Shell obfuscation |
| MIXED | Variable | Polymorphic |

## Chunk Size Recommendations

| Platform | Recommended | Notes |
|----------|-------------|-------|
| VBScript | 16-32 bytes | String length limits |
| PowerShell | 32-64 bytes | Performance |
| Python | 16-32 bytes | Readability |
| JavaScript | 16-32 bytes | Variable size |
| Bash | 16-32 bytes | Line length |
| C/C++ | 32-64 bytes | Compiler limits |

## Real-World Examples

### Example 1: Encoded PowerShell Command

```python
from array_encoder import encode_command_to_array

cmd = 'powershell.exe -NoProfile -WindowStyle Hidden -Command "Get-Process | Stop-Process"'

result = encode_command_to_array(
    cmd,
    chunk_size=20,
    encoding="hex",
    output_format="powershell",
    variable_name="encoded_cmd"
)

print(result)
```

### Example 2: VBS Payload Generation

```python
from array_encoder import encode_command_to_array

# Cmd execution payload
cmd = "cmd.exe /c systeminfo > C:\\temp\\info.txt"

vbs = encode_command_to_array(
    cmd,
    chunk_size=16,
    encoding="hex",
    output_format="vbs",
    variable_name="cmd_array"
)

# Can be injected into VBS decoder
print(vbs)
```

### Example 3: Cross-Platform Encoding

```python
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat

cmd = "ls -la /tmp"

platforms = {
    "bash": OutputFormat.BASH,
    "powershell": OutputFormat.POWERSHELL,
    "python": OutputFormat.PYTHON,
    "javascript": OutputFormat.JAVASCRIPT,
}

for platform, fmt in platforms.items():
    config = EncoderConfig(
        chunk_size=16,
        encoding_type=EncodingType.HEX,
        output_format=fmt,
        variable_name="payload"
    )
    result = ArrayEncoder(config).generate(cmd)
    print(f"\n=== {platform.upper()} ===\n{result}")
```

## Command-Line Usage

Save this as `encode_cmd.py`:

```python
#!/usr/bin/env python3
import sys
from array_encoder import encode_command_to_array

if len(sys.argv) < 3:
    print("Usage: python3 encode_cmd.py <command> <output_format> [chunk_size] [encoding]")
    print("  output_format: python, vbs, js, ps, bash, json, c")
    print("  chunk_size: default 16")
    print("  encoding: hex, base64, octal, mixed")
    sys.exit(1)

cmd = sys.argv[1]
fmt = sys.argv[2]
chunk_size = int(sys.argv[3]) if len(sys.argv) > 3 else 16
encoding = sys.argv[4] if len(sys.argv) > 4 else "hex"

result = encode_command_to_array(
    cmd,
    chunk_size=chunk_size,
    encoding=encoding,
    output_format=fmt
)

print(result)
```

Usage:
```bash
python3 encode_cmd.py "calc.exe" vbs
python3 encode_cmd.py "powershell.exe" python 20 hex
python3 encode_cmd.py "notepad" javascript 16 base64
```

## Key Functions

### For Simple Tasks
```python
from array_encoder import encode_command_to_array

result = encode_command_to_array("cmd", chunk_size=16, encoding="hex", output_format="vbs")
```

### For Advanced Tasks
```python
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat, ChunkingStrategy

config = EncoderConfig(
    chunk_size=16,
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.PYTHON,
    chunking_strategy=ChunkingStrategy.VARIABLE_SIZE,
    randomize_names=True
)

encoder = ArrayEncoder(config)
result = encoder.generate("command here")
```

## Integration with Array Decoder

```python
# 1. Encode command
from array_encoder import encode_command_to_array

vbs_array = encode_command_to_array(
    "calc.exe",
    chunk_size=16,
    encoding="hex",
    output_format="vbs"
)

# 2. Combine with Array Decoder
decoder_code = """
Function DecodeHex(hexStr)
    Dim result, i
    For i = 1 To Len(hexStr) Step 2
        result = result & Chr(CLng("&H" & Mid(hexStr, i, 2)))
    Next
    DecodeHex = result
End Function

Dim command
command = ""
"""

# Append encoder output
full_code = decoder_code + vbs_array + """
' Reconstruct and execute
For i = 0 To UBound(payload)
    command = command & DecodeHex(payload(i))
Next

CreateObject("WScript.Shell").Run command, 0, False
"""

print(full_code)
```

## Testing Your Encoding

```python
from array_encoder import encode_command_to_array
import binascii

cmd = "test.exe"

# Encode
result = encode_command_to_array(
    cmd,
    chunk_size=8,
    encoding="hex",
    output_format="python"
)

print(f"Original: {cmd}")
print(f"Encoded:\n{result}")

# Verify by manual decode
full_hex = binascii.hexlify(cmd.encode()).decode()
print(f"Full hex: {full_hex}")
print(f"Reconstructed: {bytes.fromhex(full_hex).decode()}")
```

## Troubleshooting

### Q: Why is my output larger than expected?
**A**: Hex encoding produces 2x size. Base64 produces 1.33x. This is normal.

### Q: Can I use special characters?
**A**: Yes, UTF-8 is supported. Non-ASCII characters are properly encoded.

### Q: How do I combine multiple commands?
**A**: Use command separators appropriate for your platform (`;` for Unix, `&` for Windows).

### Q: Can I make it more obfuscated?
**A**: Enable `randomize_names=True` and use `VARIABLE_SIZE` chunking strategy.

### Q: Is this reversible?
**A**: Yes, the decoder reverses the process. Use Array Decoder patterns.

## See Also

- `array_decoder_patterns.py` - Decoder patterns to reverse this encoding
- `test_array_encoder.py` - Full test suite
- `ARRAY_ENCODER_DOCUMENTATION.md` - Complete documentation
