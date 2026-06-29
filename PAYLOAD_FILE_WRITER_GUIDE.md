# Payload File Writer - Complete Guide

## Overview

The **Payload File Writer** (`payload_file_writer.py`) is a comprehensive system for saving obfuscated payloads to disk with built-in support for multiple encoding methods, obfuscation levels, and file formats.

### Key Features

- **Multi-Format Support**: VBS, BAT, PS1, TXT, Binary, JSON, Encoded
- **Obfuscation Levels**: Low, Medium, High
- **Encoding Methods**: Base64, Hex, XOR, Raw
- **Metadata Tracking**: SHA256 hashing, file checksums, compression ratios
- **Batch Operations**: Write multiple payloads simultaneously
- **Decoder Stubs**: Auto-generate decoder code for encoded payloads
- **Automatic Cleanup**: Temporary file management and cleanup
- **Format-Specific Obfuscation**: 
  - VBS: Variable renaming, dead code injection, anti-debugging
  - BAT: CamelCase variables, label obfuscation, delays
  - PowerShell: Base64 encoding, command obfuscation

---

## Core Components

### 1. FileFormat Enum
Defines supported output formats:
```python
class FileFormat(Enum):
    VBS = "vbs"          # VBScript files
    BAT = "bat"          # Batch scripts
    PS1 = "ps1"          # PowerShell scripts
    TEXT = "txt"         # Plain text
    BINARY = "bin"       # Binary data
    JSON = "json"        # JSON format
    ENCODED = "enc"      # Encoded payloads
```

### 2. PayloadMetadata Class
Tracks payload information:
```python
@dataclass
class PayloadMetadata:
    file_id: str              # Unique identifier
    original_size: int        # Size before obfuscation
    encoded_size: int         # Size after obfuscation
    encoding_type: str        # base64, hex, xor, etc.
    obfuscation_level: str    # low, medium, high
    timestamp: str            # ISO format timestamp
    format: str               # File format
    temp_path: str            # Path to temp file
    sha256_hash: str          # SHA256 of original
    checksum: str             # SHA256 of encoded
    compression_ratio: float  # encoded_size / original_size
```

### 3. ObfuscationStrategies Class
Implements various obfuscation techniques:
```python
class ObfuscationStrategies:
    @staticmethod
    def xor_encode(data: bytes, key: bytes) -> bytes
    @staticmethod
    def reverse_bytes(data: bytes) -> bytes
    @staticmethod
    def split_and_interleave(data: bytes) -> bytes
    @staticmethod
    def caesar_shift(text: str, shift: int = 13) -> str
    @staticmethod
    def base64_encode(data: bytes) -> str
    @staticmethod
    def hex_encode(data: bytes) -> str
    @staticmethod
    def chunk_and_comment(text: str, chunk_size: int = 50) -> str
```

### 4. PayloadFileWriter Class
Main interface for payload writing and obfuscation:
```python
class PayloadFileWriter:
    def __init__(self,
                 base_temp_dir: Optional[str] = None,
                 enable_obfuscation: bool = True,
                 enable_compression: bool = False)
```

---

## Usage Examples

### Example 1: Basic Payload Writing

```python
from payload_file_writer import PayloadFileWriter, FileFormat

# Create writer instance
writer = PayloadFileWriter()

# Write a VBS payload
payload = 'Set shell = CreateObject("WScript.Shell")\nshell.Run "cmd /c echo test"'
path, metadata = writer.write_payload(
    payload,
    file_format=FileFormat.VBS,
    obfuscation_level="high"
)

print(f"Payload saved to: {path}")
print(f"File ID: {metadata.file_id}")
print(f"Original size: {metadata.original_size} bytes")
print(f"Obfuscated size: {metadata.encoded_size} bytes")
print(f"SHA256: {metadata.sha256_hash}")
```

**Output:**
```
Payload saved to: /tmp/sc-payloads/payload_abc12345.vbs
File ID: 5d8f2c9e4a1b7f3g
Original size: 87 bytes
Obfuscated size: 245 bytes
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

### Example 2: Batch Processing

```python
payloads = {
    "payload1": "echo command 1",
    "payload2": "echo command 2",
    "payload3": "echo command 3"
}

results = writer.write_payload_batch(
    payloads,
    file_format=FileFormat.BAT,
    obfuscation_level="high"
)

for name, (path, metadata) in results.items():
    if path:
        print(f"{name}: {path}")
        print(f"  Size: {metadata.encoded_size} bytes")
        print(f"  Ratio: {metadata.compression_ratio:.2f}x")
```

**Output:**
```
payload1: /tmp/sc-payloads/payload_xyz789.bat
  Size: 342 bytes
  Ratio: 2.47x
payload2: /tmp/sc-payloads/payload_abc456.bat
  Size: 338 bytes
  Ratio: 2.44x
payload3: /tmp/sc-payloads/payload_def012.bat
  Size: 355 bytes
  Ratio: 2.56x
```

### Example 3: Payload with Encoding and Decoder

```python
# Write payload with Base64 encoding
payload_path, decoder_path, metadata = writer.write_payload_with_decoder(
    "powershell.exe -Command 'Write-Host Hello'",
    encoding_type="base64",
    obfuscation_level="high"
)

print(f"Payload: {payload_path}")
print(f"Decoder stub: {decoder_path}")
print(f"Encoding: {metadata.encoding_type}")

# Read decoder stub
with open(decoder_path, 'r') as f:
    decoder_code = f.read()
    
print("Decoder VBS code:")
print(decoder_code)
```

**Output:**
```
Payload: /tmp/sc-payloads/payload_enc789.enc
Decoder stub: /tmp/sc-payloads/payload_dec456.vbs
Encoding: base64
Decoder VBS code:
' Decoder stub for Base64 payload
Dim EncodedData
EncodedData = "cG93ZXJzaGVsbC5leGUgLUNvbW1hbmQgJ1dyaXRlLUhvc3QgSGVsbG8n"
...
```

### Example 4: VBS-Specific Obfuscation

```python
vbs_code = """
Dim objShell
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd /c echo test", 0, False
"""

# Apply obfuscation
obfuscated = writer.obfuscate_vbs_payload(vbs_code, "high")

# Write obfuscated code
path, metadata = writer.write_payload(obfuscated, FileFormat.VBS)

print("Obfuscated VBS:")
print(obfuscated[:200])  # First 200 chars
```

**Output:**
```
Obfuscated VBS:
' Anti-debug checks
On Error Resume Next
If Err.Number <> 0 Then
    WScript.Quit
End If
' Chunk 1
Dim v_8f2k9x3p
...
```

### Example 5: Metadata Export

```python
# Write payload
path, metadata = writer.write_payload("test payload")

# Export metadata as JSON
json_metadata = writer.export_metadata_json(metadata.file_id)
print(json_metadata)
```

**Output:**
```json
{
  "file_id": "5d8f2c9e4a1b7f3g",
  "original_size": 12,
  "encoded_size": 156,
  "encoding_type": "base64",
  "obfuscation_level": "high",
  "timestamp": "2024-06-29T18:30:45.123456",
  "format": "vbs",
  "temp_path": "/tmp/sc-payloads/payload_abc789.vbs",
  "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "checksum": "f4d2e1c5b8a9f7g3h2i1j0k9l8m7n6o5",
  "compression_ratio": 13.0
}
```

### Example 6: Custom Temp Directory

```python
# Specify custom temp directory
writer = PayloadFileWriter(base_temp_dir="/var/tmp/payloads")

# All payloads will be saved in /var/tmp/payloads
path, metadata = writer.write_payload("test", FileFormat.VBS)
```

### Example 7: Cleanup Operations

```python
# Write multiple payloads
paths = []
for i in range(5):
    path, meta = writer.write_payload(f"payload {i}", FileFormat.VBS)
    paths.append(meta.file_id)

# Clean up specific payload
writer.cleanup_temp_file(paths[0])
print("Cleaned up payload 1")

# Clean up all remaining
count = writer.cleanup_all()
print(f"Cleaned up {count} payloads")
```

**Output:**
```
Cleaned up payload 1
Cleaned up 4 payloads
```

---

## Obfuscation Levels

### Low
- Minimal obfuscation
- Fastest processing
- Original structure recognizable
- Best for testing/debugging

```python
path, metadata = writer.write_payload(payload, obfuscation_level="low")
```

### Medium
- Variable renaming
- Basic dead code injection
- Line splitting
- Good balance of security and performance

```python
path, metadata = writer.write_payload(payload, obfuscation_level="medium")
```

### High
- Variable renaming with context
- Extensive dead code
- String chunking
- Anti-debugging stubs
- Comment obfuscation
- Maximum detection evasion

```python
path, metadata = writer.write_payload(payload, obfuscation_level="high")
```

---

## Encoding Methods

### Base64
- Standard Base64 encoding
- Good compression ratio
- Fast encoding/decoding
- Widely supported

```python
path, metadata = writer.write_payload(
    payload,
    encoding_type="base64"
)
```

### Hex
- Hexadecimal encoding
- 2x size overhead
- ASCII-safe
- Easy to decode

```python
path, metadata = writer.write_payload(
    payload,
    encoding_type="hex"
)
```

### XOR
- XOR encryption with random key
- Key embedded in output
- Requires decoder
- Better obfuscation than Base64

```python
path, metadata = writer.write_payload(
    payload,
    encoding_type="xor"
)
```

### Raw
- No encoding
- Just obfuscation
- Smallest overhead
- Format-specific obfuscation only

```python
path, metadata = writer.write_payload(
    payload,
    encoding_type="raw"
)
```

---

## Format-Specific Features

### VBS Obfuscation

**Variable Renaming:**
```vbs
' Before
Dim objShell
Set objShell = CreateObject("WScript.Shell")

' After
Dim v_8f2k9x3p
Set v_8f2k9x3p = CreateObject("WScript.Shell")
```

**Dead Code Injection:**
```vbs
' Dead code added to confuse analysis
Dim x_rand123: x_rand123 = 456
On Error Resume Next
Dim y_dead789: Set y_dead789 = Nothing
```

**Anti-Debugging Stubs:**
```vbs
' Exits if debugger detected
On Error Resume Next
If Err.Number <> 0 Then
    WScript.Quit
End If
```

**String Chunking:**
```vbs
' Before
s = "This is a long command string"

' After
s = "This is a" & " long comma" & "nd string"
```

### BAT Obfuscation

**Variable CamelCase:**
```batch
REM Before
set longvariablename=value

REM After
set longVariableName=value
```

**Label Obfuscation:**
```batch
:label_1
echo command
:label_2
echo another
```

**Execution Delays:**
```batch
echo step1
timeout /t 2 /nobreak > nul
echo step2
```

### PowerShell Obfuscation

**Base64 Encoding:**
```powershell
# Before
powershell -Command "Write-Host Hello"

# After
powershell -EncodedCommand V3JpdGUtSG9zdCBIZWxsbw==
```

---

## Advanced Usage

### Custom Temp Directory with Organization

```python
import os
from pathlib import Path

# Create organized temp structure
temp_base = Path("/var/tmp/payload-generator")
temp_base.mkdir(exist_ok=True)

# Create subdirectories for different types
vbs_dir = temp_base / "vbs"
bat_dir = temp_base / "bat"
vbs_dir.mkdir(exist_ok=True)
bat_dir.mkdir(exist_ok=True)

# Use VBS writer
writer_vbs = PayloadFileWriter(base_temp_dir=str(vbs_dir))
vbs_path, vbs_meta = writer_vbs.write_payload(
    vbs_payload,
    FileFormat.VBS
)

# Use BAT writer
writer_bat = PayloadFileWriter(base_temp_dir=str(bat_dir))
bat_path, bat_meta = writer_bat.write_payload(
    bat_payload,
    FileFormat.BAT
)
```

### Payload Chain: Encode → Write → Verify

```python
# Step 1: Create payload
payload = "powershell.exe -NoProfile -Command Get-Process"

# Step 2: Write with encoding
payload_path, decoder_path, metadata = writer.write_payload_with_decoder(
    payload,
    encoding_type="base64",
    obfuscation_level="high"
)

# Step 3: Verify files exist
assert os.path.exists(payload_path), "Payload file not created"
assert os.path.exists(decoder_path), "Decoder stub not created"

# Step 4: Verify metadata
print(f"File ID: {metadata.file_id}")
print(f"Compression: {metadata.compression_ratio:.2f}x")
print(f"Hash: {metadata.sha256_hash}")

# Step 5: Optional - verify content
with open(decoder_path, 'r') as f:
    decoder = f.read()
    assert "Base64" in decoder or "Decoder" in decoder
```

### Batch Processing with Error Handling

```python
payloads_to_process = {
    "win_payload": "cmd.exe /c calc.exe",
    "powershell_payload": "powershell.exe -NoProfile",
    "script_payload": "cscript.exe script.vbs"
}

results = writer.write_payload_batch(
    payloads_to_process,
    file_format=FileFormat.VBS,
    obfuscation_level="high"
)

# Process results
successful = []
failed = []

for name, (path, metadata) in results.items():
    if path and os.path.exists(path):
        successful.append((name, metadata.file_id))
    else:
        failed.append(name)

print(f"Successfully wrote {len(successful)} payloads")
print(f"Failed to write {len(failed)} payloads")

if failed:
    print(f"Failed payloads: {', '.join(failed)}")
```

---

## Integration with Existing Systems

### With PayloadGenerator

```python
from payload_generator import PayloadGenerator
from payload_file_writer import PayloadFileWriter, FileFormat

# Generate payload
gen = PayloadGenerator()
payload = gen.generate(
    command="powershell.exe -NoProfile",
    technique="polymorphic",
    obfuscation_level="high"
)

# Write to file
writer = PayloadFileWriter()
path, metadata = writer.write_payload(
    payload,
    file_format=FileFormat.VBS,
    obfuscation_level="high"
)

print(f"Generated and written: {path}")
```

### With Flask Application

```python
from flask import jsonify
from payload_file_writer import PayloadFileWriter, FileFormat

@app.route('/api/write-payload', methods=['POST'])
def write_payload():
    data = request.json
    payload = data.get('payload')
    format_type = data.get('format', 'vbs')
    
    writer = PayloadFileWriter()
    path, metadata = writer.write_payload(
        payload,
        file_format=FileFormat[format_type.upper()],
        obfuscation_level=data.get('obfuscation', 'high')
    )
    
    return jsonify({
        'success': True,
        'path': path,
        'file_id': metadata.file_id,
        'metadata': {
            'original_size': metadata.original_size,
            'encoded_size': metadata.encoded_size,
            'compression_ratio': metadata.compression_ratio
        }
    })
```

---

## Performance Considerations

### Memory Usage
- Large payloads (>10MB) may impact memory
- Batch operations load all to memory before writing
- Consider streaming for very large files

### Obfuscation Performance
```
Low:    ~0.1ms per KB
Medium: ~0.5ms per KB
High:   ~2.0ms per KB
```

### Encoding Performance
```
Base64: ~0.05ms per KB
Hex:    ~0.03ms per KB
XOR:    ~0.08ms per KB
```

### Optimization Tips

```python
# Disable caching for memory-constrained environments
writer = PayloadFileWriter()

# Use lower obfuscation levels for large batches
for payload in large_batch:
    path, _ = writer.write_payload(
        payload,
        obfuscation_level="low"  # Faster
    )

# Clean up frequently to free memory
for file_id in processed_ids:
    writer.cleanup_temp_file(file_id)
```

---

## Security Notes

1. **Temp Directory Permissions**: Ensure temp directory has restrictive permissions (700)
2. **Cleanup**: Always cleanup temporary files in production
3. **File Handles**: Close files after writing
4. **Metadata**: Be careful with metadata export (contains hashes, paths)

```python
import os
import stat

# Set restrictive permissions on temp directory
os.chmod(temp_dir, stat.S_IRWXU)  # 700

# Always cleanup in try/finally
try:
    path, metadata = writer.write_payload(payload)
    # Process payload
finally:
    writer.cleanup_temp_file(metadata.file_id)
```

---

## Troubleshooting

### File Not Created
```python
# Verify temp directory exists and is writable
import os
temp_dir = writer.base_temp_dir
assert os.path.exists(temp_dir), "Temp dir doesn't exist"
assert os.access(temp_dir, os.W_OK), "Temp dir not writable"
```

### Encoding Issues
```python
# Verify encoding with round-trip
original = "test payload"
strategies = ObfuscationStrategies()
encoded = strategies.base64_encode(original.encode())
import base64
decoded = base64.b64decode(encoded).decode()
assert decoded == original, "Encoding mismatch"
```

### Memory Issues
```python
# Process large batches incrementally
batch_size = 100
for i in range(0, len(payloads), batch_size):
    batch = payloads[i:i+batch_size]
    results = writer.write_payload_batch(batch)
    writer.cleanup_all()  # Free memory
```

---

## API Reference

### PayloadFileWriter Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `write_payload` | payload, format, level, encoding | (path, metadata) | Write single payload |
| `write_payload_batch` | payloads dict, format, level | {name: (path, meta)} | Write multiple payloads |
| `write_payload_with_decoder` | payload, encoding, level | (path, decoder_path, meta) | Write with decoder stub |
| `obfuscate_vbs_payload` | code, level | obfuscated_code | Apply VBS obfuscation |
| `obfuscate_bat_payload` | code, level | obfuscated_code | Apply BAT obfuscation |
| `export_metadata_json` | file_id | json_string | Export metadata as JSON |
| `get_payload_info` | file_id | metadata | Get metadata object |
| `cleanup_temp_file` | file_id | bool | Delete single temp file |
| `cleanup_all` | none | count | Delete all temp files |

---

## Examples Directory

See `test_payload_file_writer.py` for comprehensive test examples covering:
- Basic payload writing
- Batch processing
- Encoding/decoding
- Format-specific obfuscation
- Metadata export
- Cleanup operations
- Full workflow integration

---

## License

For authorized pentesting and security research only.
