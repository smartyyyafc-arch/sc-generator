# Array Encoder - Complete Documentation

## Overview

The **Array Encoder** converts commands and data into chunked hex arrays for use with array decoder patterns. It is the reverse operation of the Array Decoder, chunking data into manageable pieces while supporting multiple encoding schemes and output formats.

## Features

### Encoding Types
- **HEX**: Convert data to hexadecimal representation
- **BASE64**: Encode data using base64
- **OCTAL**: Encode data as octal representation
- **MIXED**: Randomly alternate between encoding types

### Output Formats
- **Python**: Native Python list syntax
- **VBScript**: VBS array declaration
- **JavaScript**: ES6 const array syntax
- **PowerShell**: PowerShell array syntax
- **Bash**: Bash array syntax
- **JSON**: Structured JSON format
- **C/C++**: C-style array declaration

### Chunking Strategies
- **SEQUENTIAL**: Standard sequential chunks
- **RANDOM_ORDER**: Randomize chunk order with mapping
- **VARIABLE_SIZE**: Random-sized chunks (min/max configurable)
- **INTERLEAVED**: Interleave even and odd indices
- **NESTED**: Group chunks into nested arrays

## Installation & Usage

### Basic Usage

```python
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat

# Create configuration
config = EncoderConfig(
    chunk_size=16,
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.PYTHON,
    variable_name="payload"
)

# Create encoder and generate
encoder = ArrayEncoder(config)
result = encoder.generate("calc.exe")
print(result)
```

### Convenience Function

For quick encoding, use the convenience function:

```python
from array_encoder import encode_command_to_array

code = encode_command_to_array(
    "powershell.exe",
    chunk_size=16,
    encoding="hex",
    output_format="vbs",
    variable_name="cmd"
)
print(code)
```

## Configuration Options

### EncoderConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `chunk_size` | int | 16 | Size of each chunk in bytes |
| `encoding_type` | EncodingType | HEX | Type of encoding to use |
| `output_format` | OutputFormat | PYTHON | Output format |
| `chunking_strategy` | ChunkingStrategy | SEQUENTIAL | Chunking strategy |
| `variable_name` | str | "payload" | Name of output variable |
| `randomize_names` | bool | False | Randomize variable names |
| `add_comments` | bool | True | Add encoder comments |
| `preserve_order` | bool | True | Preserve chunk order |
| `min_chunk_size` | int | 8 | Min size for VARIABLE_SIZE |
| `max_chunk_size` | int | 32 | Max size for VARIABLE_SIZE |

## Examples

### Example 1: Basic Hex Encoding to VBS

```python
from array_encoder import encode_command_to_array

code = encode_command_to_array(
    "calc.exe",
    chunk_size=8,
    encoding="hex",
    output_format="vbs"
)
```

Output:
```vbs
' Array encoder: 1 chunks of hex
Dim payload(0)
payload(0) = "63616c632e657865"
```

### Example 2: Base64 to Python

```python
from array_encoder import encode_command_to_array

code = encode_command_to_array(
    "notepad.exe",
    chunk_size=8,
    encoding="base64",
    output_format="python"
)
```

Output:
```python
# Array encoder: 2 chunks of base64
payload = [
    "bm90ZXBh",
    "ZC5leGU="
]
```

### Example 3: Variable-Sized Chunks to JSON

```python
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat, ChunkingStrategy

config = EncoderConfig(
    chunk_size=16,
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.JSON,
    chunking_strategy=ChunkingStrategy.VARIABLE_SIZE,
    min_chunk_size=4,
    max_chunk_size=12
)

encoder = ArrayEncoder(config)
result = encoder.generate("cmd.exe /c ipconfig")
```

Output:
```json
{
  "payload": [
    "636d642e657865202f6320",
    "697066636f6e666967"
  ],
  "count": 2,
  "encoding": "hex",
  "chunk_size": 16
}
```

### Example 4: Randomized Variable Names

```python
config = EncoderConfig(
    chunk_size=16,
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.PYTHON,
    randomize_names=True  # Enable random variable names
)

encoder = ArrayEncoder(config)
result = encoder.generate("test.exe")
```

Output (variable names randomized):
```python
payloadKxNpQr = [
    "7465737420636f6d6d616e6420726574756e2e657865"
]
```

## Encoding Details

### Hex Encoding
- Converts each character to its hexadecimal byte representation
- Example: "AB" → "4142"
- Uses UTF-8 encoding for non-ASCII characters
- Efficient for binary data representation

### Base64 Encoding
- Standard base64 encoding per RFC 4648
- Example: "AB" → "QUI="
- Larger output than hex (4 chars per 3 input bytes)
- Better for printable character distribution

### Octal Encoding
- Converts to octal representation
- Example: "A" → "101"
- Useful for shell command obfuscation
- Commonly used in VBS hex-to-octal conversion

### Mixed Encoding
- Randomly alternates between encoding types per chunk
- Useful for polymorphic encoders
- Evades signature-based detection

## Chunking Strategies

### Sequential
- Divides data into fixed-size chunks in order
- Simplest and most direct approach
- Good for basic array generation

### Random Order
- Randomizes chunk order for obfuscation
- Returns mapping for decoder to use
- Requires decoder to implement index mapping

### Variable Size
- Creates random-sized chunks within min/max range
- Evades pattern detection
- Adds complexity to decoders

### Interleaved
- Processes even-indexed chunks, then odd
- Requires decoder to de-interleave
- Good for code obfuscation

### Nested
- Groups chunks into sub-arrays
- Creates 2D array structure
- Useful for multi-level obfuscation

## Output Format Details

### Python
```python
payload = [
    "chunk1",
    "chunk2"
]
```

### VBScript
```vbs
Dim payload(1)
payload(0) = "chunk1"
payload(1) = "chunk2"
```

### JavaScript
```javascript
const payload = [
    "chunk1",
    "chunk2"
];
```

### PowerShell
```powershell
$payload = @(
    "chunk1",
    "chunk2"
)
```

### Bash
```bash
payload=(
    "chunk1"
    "chunk2"
)
```

### JSON
```json
{
  "payload": ["chunk1", "chunk2"],
  "count": 2,
  "encoding": "hex",
  "chunk_size": 16
}
```

### C/C++
```c
const char* payload[] = {
    "chunk1",
    "chunk2"
};
int payload_len = 2;
```

## API Reference

### ArrayEncoder Class

#### Methods

##### `encode(data: str) -> Dict`
Encodes data into chunks according to configuration.

**Parameters:**
- `data`: Input command/data string

**Returns:**
- Dictionary with keys:
  - `chunks`: List of encoded chunks
  - `count`: Number of chunks
  - `strategy`: Chunking strategy used
  - `order`: Chunk order indices

**Example:**
```python
encoder = ArrayEncoder(config)
result = encoder.encode("test.exe")
print(result['chunks'])  # List of chunks
```

##### `generate(data: str) -> str`
Encodes data and generates output in specified format.

**Parameters:**
- `data`: Input command/data string

**Returns:**
- Formatted string ready for use in target language

**Example:**
```python
encoder = ArrayEncoder(config)
code = encoder.generate("test.exe")
```

##### `to_python_list(chunks: List[str]) -> str`
Converts chunk list to Python list format.

##### `to_vbs_array(chunks: List[str]) -> str`
Converts chunk list to VBScript array format.

##### `to_javascript_array(chunks: List[str]) -> str`
Converts chunk list to JavaScript array format.

##### `to_powershell_array(chunks: List[str]) -> str`
Converts chunk list to PowerShell array format.

##### `to_bash_array(chunks: List[str]) -> str`
Converts chunk list to Bash array format.

##### `to_json(chunks: List[str]) -> str`
Converts chunk list to JSON format.

##### `to_c_array(chunks: List[str]) -> str`
Converts chunk list to C/C++ array format.

### Convenience Functions

#### `encode_command_to_array(...)`
Quick encoding function for simple use cases.

**Parameters:**
- `command`: Command/data to encode
- `chunk_size`: Size of each chunk (default: 16)
- `encoding`: Encoding type (default: "hex")
- `output_format`: Output format (default: "python")
- `variable_name`: Output variable name (default: "payload")

**Returns:**
- Encoded array as string

**Example:**
```python
from array_encoder import encode_command_to_array

code = encode_command_to_array(
    "calc.exe",
    chunk_size=8,
    encoding="hex",
    output_format="vbs"
)
```

## Testing

Run the test suite to verify functionality:

```bash
python3 test_array_encoder.py
```

Test coverage includes:
- Hex encoding/decoding
- Base64 encoding
- Multiple output formats
- Chunking strategies
- Roundtrip encode-decode verification
- Large command handling
- JSON validation
- Randomized variable names

## Reverse Operation: Decoding

The encoded arrays are designed to work with Array Decoder patterns. The decoder reverses the process:

1. Takes encoded chunks from array
2. Decodes each chunk (hex → bytes, base64 → bytes, etc.)
3. Reconstructs original command
4. Executes or processes as needed

Example decoder (VBScript):
```vbs
Dim payload(1)
payload(0) = "74657374"
payload(1) = "2e657865"

Dim result
For i = 0 To UBound(payload)
    For j = 1 To Len(payload(i)) Step 2
        result = result & Chr(CLng("&H" & Mid(payload(i), j, 2)))
    Next
Next

WScript.Shell.Run result, 0, False
```

## Security Considerations

### Obfuscation Strength
- Hex/Base64 encoding provides obfuscation, not encryption
- Multiple encodings and chunking strategies increase detection evasion
- Randomized variable names improve obfuscation
- Should be combined with additional anti-analysis techniques

### Best Practices
1. Use appropriate chunk sizes for your target platform
2. Combine encoding with polymorphic decoder patterns
3. Use randomized variable names when possible
4. Add multiple encoding layers for sensitive payloads
5. Test thoroughly in your target environment

### Limitations
- Not cryptographically secure
- Detectable by static analysis of decoder patterns
- May trigger behavioral detection if suspicious execution follows
- Should be part of larger obfuscation strategy

## Performance Notes

- Sequential chunking: O(n) where n is data length
- Variable-size chunking: O(n) with random number generation overhead
- Memory usage: O(n) for chunks storage
- Suitable for payloads up to several megabytes

## Integration with Array Decoder

The Array Encoder output is specifically designed for use with Array Decoder patterns:

1. **Sequential Encoder → Sequential Decoder**: Direct correspondence
2. **Randomized Encoder → Index Mapping Decoder**: Use chunk order mapping
3. **Variable-Size Encoder → Adaptive Decoder**: Dynamically handle chunk sizes
4. **Interleaved Encoder → De-Interleave Decoder**: Restore original order

## Example Workflow

```python
# 1. Encode command
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat

config = EncoderConfig(
    chunk_size=16,
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.VBS
)

encoder = ArrayEncoder(config)
vbs_code = encoder.generate("calc.exe")

# 2. Save VBS code
with open("payload.vbs", "w") as f:
    f.write(vbs_code)

# 3. Use with Array Decoder in target script
# The generated array pairs with array decoder patterns
```

## Troubleshooting

### Issue: Encoding produces different output sizes
**Cause**: Different encoding types produce different length outputs (hex vs base64)
**Solution**: Calculate expected output size: hex is 2x input, base64 is 4/3x input

### Issue: Chunks don't align with decoder
**Cause**: Chunk size mismatch between encoder and decoder
**Solution**: Ensure both use same chunk size configuration

### Issue: Variable names conflict in generated code
**Cause**: Randomization disabled or collision with existing variables
**Solution**: Enable `randomize_names=True` or manually change `variable_name`

### Issue: Large payloads take too long to encode
**Cause**: Very small chunk sizes or variable-size strategy with large range
**Solution**: Increase chunk size or reduce randomization overhead

## License

For authorized pentesting and security research only.
