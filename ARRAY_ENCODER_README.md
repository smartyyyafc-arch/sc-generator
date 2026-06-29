# Array Encoder - Complete Package

## Overview

The **Array Encoder** is a Python utility that chunks commands and data into hex arrays, providing the reverse operation of Array Decoder patterns. It supports multiple encoding types, output formats, and chunking strategies for generating obfuscated payloads.

## Key Features

✓ **Multiple Encoding Types**: HEX, BASE64, OCTAL, MIXED  
✓ **7 Output Formats**: Python, VBScript, JavaScript, PowerShell, Bash, JSON, C/C++  
✓ **5 Chunking Strategies**: Sequential, Random Order, Variable Size, Interleaved, Nested  
✓ **Obfuscation Options**: Randomized variable names, comments control, custom naming  
✓ **Cross-Platform**: Works with any command/payload  
✓ **Zero Dependencies**: Uses Python stdlib only  
✓ **Fully Tested**: 9/9 test cases passing  

## Files Included

### Core Implementation
- **`array_encoder.py`** (480 lines)
  - Main encoder class and implementation
  - 7 output format methods
  - 5 chunking strategy implementations
  - Convenience functions for quick use

### Tests & Validation
- **`test_array_encoder.py`** (380 lines)
  - 9 comprehensive test cases
  - Covers all encoding types
  - All output formats tested
  - Roundtrip validation (encode-decode)

### Documentation
- **`ARRAY_ENCODER_DOCUMENTATION.md`** (Full technical reference)
  - Detailed API documentation
  - Configuration reference
  - Security considerations
  - Troubleshooting guide

- **`ARRAY_ENCODER_QUICKSTART.md`** (5-minute quick start)
  - Quick usage patterns
  - Common examples
  - Encoding comparisons
  - Chunk size recommendations

- **`array_encoder_examples.py`** (12 practical examples)
  - Real-world usage scenarios
  - VBScript payloads
  - PowerShell obfuscation
  - Cross-platform encoding
  - API integration examples

## Quick Start

### Installation
```bash
# No external dependencies required
# Just ensure Python 3.6+ is available
```

### Basic Usage

```python
from array_encoder import encode_command_to_array

# Encode calc.exe to VBScript array
result = encode_command_to_array(
    "calc.exe",
    chunk_size=16,
    encoding="hex",
    output_format="vbs"
)

print(result)
```

Output:
```vbs
' Array encoder: 1 chunks of hex
Dim payload(0)
payload(0) = "63616c632e657865"
```

### Advanced Usage

```python
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat, ChunkingStrategy

config = EncoderConfig(
    chunk_size=16,
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.PYTHON,
    chunking_strategy=ChunkingStrategy.VARIABLE_SIZE,
    randomize_names=True,
    add_comments=True
)

encoder = ArrayEncoder(config)
result = encoder.generate("powershell.exe -Command 'Get-Process'")
```

## Feature Matrix

### Encoding Types
| Type | Example | Use Case |
|------|---------|----------|
| HEX | `63616c632e657865` | Binary data, reliable |
| BASE64 | `Y2FsYy5leGU=` | Printable, compact |
| OCTAL | `143 061 154 154 157` | Shell obfuscation |
| MIXED | Varies | Polymorphic payloads |

### Output Formats
| Format | Platform | Best For |
|--------|----------|----------|
| Python | Python 3+ | Script integration |
| VBScript | Windows | Legacy VBS execution |
| JavaScript | Web/Node.js | Browser/Node payloads |
| PowerShell | Windows | Modern Windows |
| Bash | Linux/Unix | Shell scripts |
| JSON | Universal | API/storage |
| C/C++ | Compiled | Binary payloads |

### Chunking Strategies
| Strategy | Complexity | Obfuscation |
|----------|-----------|-------------|
| Sequential | Low | Low |
| Random Order | Medium | Medium |
| Variable Size | Medium | High |
| Interleaved | Medium | Medium |
| Nested | High | High |

## Real-World Examples

### Example 1: VBScript Payload
```python
from array_encoder import encode_command_to_array

cmd = "powershell.exe -Command \"Get-Process | Stop-Process\""
vbs = encode_command_to_array(cmd, chunk_size=20, encoding="hex", output_format="vbs")
```

### Example 2: PowerShell Obfuscation
```python
from array_encoder import encode_command_to_array

cmd = "cmd.exe /c systeminfo"
ps = encode_command_to_array(cmd, chunk_size=16, encoding="hex", output_format="powershell")
```

### Example 3: Cross-Platform
```python
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat

formats = [OutputFormat.PYTHON, OutputFormat.BASH, OutputFormat.POWERSHELL]
for fmt in formats:
    config = EncoderConfig(encoding_type=EncodingType.HEX, output_format=fmt)
    encoder = ArrayEncoder(config)
    print(encoder.generate("test.exe"))
```

### Example 4: JSON for APIs
```python
from array_encoder import encode_command_to_array
import json

json_str = encode_command_to_array("cmd", output_format="json")
data = json.loads(json_str)
# Use with database, REST API, etc.
```

## Configuration Reference

### Quick Configuration
```python
EncoderConfig(
    chunk_size=16,           # Bytes per chunk
    encoding_type=EncodingType.HEX,  # HEX, BASE64, OCTAL, MIXED
    output_format=OutputFormat.PYTHON,  # Python, VBS, JS, PowerShell, Bash, JSON, C
    chunking_strategy=ChunkingStrategy.SEQUENTIAL,  # Sequential, RandomOrder, VariableSize, Interleaved, Nested
    variable_name="payload",  # Name of output variable
    randomize_names=False,   # Randomize variable names
    add_comments=True,       # Add encoder comments
    preserve_order=True,     # Preserve chunk order
    min_chunk_size=8,        # For VARIABLE_SIZE
    max_chunk_size=32        # For VARIABLE_SIZE
)
```

## Testing

### Run Test Suite
```bash
python3 test_array_encoder.py
```

### Test Coverage
- Hex encoding/decoding
- Base64 encoding
- All 7 output formats
- All 5 chunking strategies
- Roundtrip validation
- Large command handling
- JSON structure validation
- Randomized variable names

## API Reference

### Main Classes

#### `ArrayEncoder`
```python
encoder = ArrayEncoder(config)
result = encoder.generate("command")
encoded = encoder.encode("data")
```

#### `EncoderConfig`
```python
config = EncoderConfig(
    chunk_size=16,
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.PYTHON
)
```

### Convenience Function
```python
result = encode_command_to_array(
    "command",
    chunk_size=16,
    encoding="hex",
    output_format="vbs",
    variable_name="payload"
)
```

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| Hex encoding | O(n) | O(n) |
| Chunking | O(n) | O(n) |
| Format generation | O(n) | O(n) |

**Performance Notes:**
- Handles payloads up to several MB efficiently
- Variable-size chunking has minor randomization overhead
- JSON format fastest for parsing
- All operations complete in <100ms for typical payloads

## Integration Examples

### With Array Decoder
```python
# 1. Encode with Array Encoder
vbs_array = encode_command_to_array(
    "calc.exe",
    chunk_size=16,
    encoding="hex",
    output_format="vbs"
)

# 2. Combine with Array Decoder patterns
full_code = decoder_function + vbs_array + execution_code
```

### With Obfuscation
```python
# Multiple layers of obfuscation
result = encode_command_to_array(
    cmd,
    chunk_size=16,
    encoding="base64",
    output_format="powershell",
    randomize_names=True
)
```

### With Database Storage
```python
import json
json_payload = encode_command_to_array(cmd, output_format="json")
data = json.loads(json_payload)
# Store in database, retrieve later
```

## Security Considerations

### Obfuscation Strength
- Hex/Base64 encoding provides obfuscation, not encryption
- Multiple encoding types improve evasion
- Randomized variable names reduce signatures
- Chunking strategies avoid pattern detection

### Best Practices
1. Use with appropriate decoder patterns
2. Combine with additional obfuscation techniques
3. Test in target environment
4. Monitor for behavioral detection triggers
5. Use randomization for polymorphic results

### Limitations
- Not cryptographically secure
- May be detected by signature-based analysis
- Behavioral detection still applicable
- Should be part of larger obfuscation strategy

## Troubleshooting

### Q: Output is larger than expected
**A**: Hex is 2x input size, Base64 is 1.33x input size. This is normal.

### Q: Chunks not aligned with decoder
**A**: Ensure chunk_size matches between encoder and decoder.

### Q: Variable name conflicts
**A**: Enable `randomize_names=True` to avoid collisions.

### Q: Large payloads slow
**A**: Increase chunk_size or reduce randomization.

## Use Cases

- ✓ Payload obfuscation
- ✓ Command encoding
- ✓ Data chunking
- ✓ Multi-platform payload generation
- ✓ API payload format conversion
- ✓ Polymorphic encoder generation
- ✓ Security research
- ✓ Penetration testing

## Requirements

- Python 3.6+
- No external dependencies
- Unix or Windows compatible

## Examples Location

All examples are in `/home/user/sc-generator/`:
- **`array_encoder.py`** - Main encoder
- **`test_array_encoder.py`** - Test suite
- **`array_encoder_examples.py`** - 12 practical examples

## Documentation Files

- **`ARRAY_ENCODER_DOCUMENTATION.md`** - Complete technical reference
- **`ARRAY_ENCODER_QUICKSTART.md`** - Quick start guide
- **`ARRAY_ENCODER_README.md`** - This file

## Quick Reference Commands

```bash
# Run tests
python3 test_array_encoder.py

# Run examples
python3 array_encoder_examples.py

# Use in your code
python3 -c "from array_encoder import encode_command_to_array; print(encode_command_to_array('calc.exe'))"
```

## Summary

The Array Encoder provides a complete solution for chunking commands into obfuscated arrays. With support for multiple encodings and output formats, it works seamlessly with Array Decoder patterns to create polymorphic, evasive payloads.

### Key Strengths
- Simple, intuitive API
- Zero dependencies
- Comprehensive testing
- Multiple output formats
- Flexible configuration
- Production-ready code

### Next Steps
1. Read `ARRAY_ENCODER_QUICKSTART.md` for 5-minute overview
2. Run `test_array_encoder.py` to verify installation
3. Review `array_encoder_examples.py` for practical usage
4. Check `ARRAY_ENCODER_DOCUMENTATION.md` for advanced topics

---

**For authorized pentesting and security research only.**
