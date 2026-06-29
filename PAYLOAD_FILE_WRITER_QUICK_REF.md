# Payload File Writer - Quick Reference

## Installation
```python
from payload_file_writer import PayloadFileWriter, FileFormat
```

## Basic Usage

### Single Payload
```python
writer = PayloadFileWriter()
path, metadata = writer.write_payload(
    payload="cmd.exe /c echo test",
    file_format=FileFormat.VBS,
    obfuscation_level="high"
)
print(f"Saved to: {path}")
writer.cleanup_all()
```

### Multiple Payloads
```python
payloads = {"p1": "cmd1", "p2": "cmd2"}
results = writer.write_payload_batch(payloads, FileFormat.BAT, "high")
writer.cleanup_all()
```

### With Encoding
```python
payload_path, decoder_path, meta = writer.write_payload_with_decoder(
    payload="encrypted command",
    encoding_type="base64",
    obfuscation_level="high"
)
writer.cleanup_all()
```

## File Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| VBS | .vbs | Windows script, full obfuscation support |
| BAT | .bat | Batch files, Windows commands |
| PS1 | .ps1 | PowerShell scripts |
| TEXT | .txt | Plain text output |
| BINARY | .bin | Binary data |
| JSON | .json | JSON formatted |
| ENCODED | .enc | Encoded/encrypted payloads |

## Obfuscation Levels

| Level | Speed | Stealth | Size | Use |
|-------|-------|--------|------|-----|
| low | Fast | Basic | +0% | Testing |
| medium | Normal | Good | +130% | Production |
| high | Slow | Excellent | +170% | Maximum stealth |

## Encoding Methods

| Method | Overhead | Speed | Note |
|--------|----------|-------|------|
| base64 | 1.33x | Fast | Standard, widely supported |
| hex | 2.0x | Fast | ASCII-safe |
| xor | 1.0x | Fast | Encrypted with embedded key |
| raw | 0x | - | No encoding, obfuscation only |

## API Cheat Sheet

### Write Methods
```python
# Single write
path, meta = writer.write_payload(payload, FileFormat.VBS, "high")

# Batch write
results = writer.write_payload_batch(dict_payloads, FileFormat.BAT, "high")

# With encoding
paths = writer.write_payload_with_decoder(payload, "base64", "high")
```

### Obfuscation Methods
```python
# VBS-specific
obfuscated = writer.obfuscate_vbs_payload(vbs_code, "high")

# BAT-specific
obfuscated = writer.obfuscate_bat_payload(bat_code, "high")

# PowerShell-specific
obfuscated = writer.obfuscate_powershell(ps_code, "high")
```

### Metadata Methods
```python
# Export as JSON
json_str = writer.export_metadata_json(file_id)

# Get metadata object
metadata = writer.get_payload_info(file_id)

# List all stored metadata
for file_id, meta in writer.metadata_store.items():
    print(meta)
```

### Cleanup Methods
```python
# Clean single file
success = writer.cleanup_temp_file(file_id)

# Clean all files
count = writer.cleanup_all()
```

## Common Patterns

### Pattern 1: Write and Return Path
```python
def get_obfuscated_payload(command, fmt=FileFormat.VBS):
    writer = PayloadFileWriter()
    path, _ = writer.write_payload(command, fmt, "high")
    return path
```

### Pattern 2: Try-Finally Cleanup
```python
writer = PayloadFileWriter()
try:
    path, meta = writer.write_payload(payload)
    # Use payload
finally:
    writer.cleanup_all()
```

### Pattern 3: Batch with Progress
```python
writer = PayloadFileWriter()
for i, payload in enumerate(payloads):
    path, meta = writer.write_payload(payload)
    print(f"Progress: {i+1}/{len(payloads)}")
writer.cleanup_all()
```

### Pattern 4: Memory Efficient
```python
writer = PayloadFileWriter()
BATCH_SIZE = 100

for i in range(0, total, BATCH_SIZE):
    batch = payloads[i:i+BATCH_SIZE]
    results = writer.write_payload_batch(batch)
    writer.cleanup_all()  # Free memory
```

### Pattern 5: Format Chain
```python
writer = PayloadFileWriter()
for fmt in [FileFormat.VBS, FileFormat.BAT, FileFormat.PS1]:
    path, meta = writer.write_payload(payload, fmt)
writer.cleanup_all()
```

## Property Reference

### FileFormat Enum
```python
FileFormat.VBS       # VBScript
FileFormat.BAT       # Batch
FileFormat.PS1       # PowerShell
FileFormat.TEXT      # Text
FileFormat.BINARY    # Binary
FileFormat.JSON      # JSON
FileFormat.ENCODED   # Encoded
```

### PayloadMetadata Fields
```python
metadata.file_id             # Unique ID
metadata.original_size       # Original bytes
metadata.encoded_size        # Encoded bytes
metadata.encoding_type       # base64/hex/xor/raw
metadata.obfuscation_level   # low/medium/high
metadata.timestamp           # ISO timestamp
metadata.format              # File format
metadata.temp_path           # Full path
metadata.sha256_hash         # Original hash
metadata.checksum            # Encoded hash
metadata.compression_ratio   # encoded/original
```

## Obfuscation Techniques

### VBS (VBScript)
- Variable renaming
- Dead code injection
- Line splitting
- String chunking
- Anti-debugging stubs
- Comment insertion

### BAT (Batch)
- Variable CamelCase
- Label obfuscation
- Execution delays
- Character encoding

### PowerShell
- Base64 encoding
- -EncodedCommand
- Variable obfuscation
- Function renaming

## Performance Notes

### Encoding Speed
- Base64: ~0.05ms/KB
- Hex: ~0.03ms/KB
- XOR: ~0.08ms/KB

### Obfuscation Speed
- Low: ~0.1ms/KB
- Medium: ~0.5ms/KB
- High: ~2.0ms/KB

### Memory Tips
- Large files (>100MB) require streaming
- Batch cleanup frequently
- Use low obfuscation for memory-constrained systems

## Error Handling

### File Not Created
```python
try:
    path, _ = writer.write_payload(payload)
    assert os.path.exists(path), "File not created"
except Exception as e:
    print(f"Error: {e}")
    writer.cleanup_all()
```

### Encoding Failures
```python
try:
    path, _ = writer.write_payload(payload, encoding_type="xor")
except ValueError as e:
    print(f"Encoding error: {e}")
```

### Cleanup Errors
```python
count = writer.cleanup_all()
if count == 0:
    print("No files to clean up")
```

## File Size Estimates

For reference payloads:

```
Original        Low     Medium   High
10 KB    →     10 KB    23 KB    27 KB
100 KB   →    100 KB   230 KB   270 KB
1 MB     →      1 MB   2.3 MB   2.7 MB
```

## Security Checklist

- [ ] Set temp directory permissions to 700
- [ ] Always use try/finally for cleanup
- [ ] Don't store temp paths in logs
- [ ] Use high obfuscation for sensitive payloads
- [ ] Export metadata to secure location
- [ ] Verify checksums before delivery
- [ ] Clear metadata after export

## Troubleshooting

| Issue | Solution |
|-------|----------|
| File not created | Check temp dir permissions |
| Encoding fails | Use different encoding type |
| Memory issues | Use batch size 100-500 |
| Slow processing | Use low obfuscation |
| Hash mismatch | Verify original payload |

## Integration Examples

### With Flask
```python
@app.route('/generate', methods=['POST'])
def generate():
    writer = PayloadFileWriter()
    path, meta = writer.write_payload(request.json['payload'])
    return send_file(path)
```

### With Async
```python
async def generate_async(payloads):
    writer = PayloadFileWriter()
    tasks = [write_async(p) for p in payloads]
    results = await asyncio.gather(*tasks)
    writer.cleanup_all()
    return results
```

### With CLI
```bash
python3 -c "
from payload_file_writer import write_payload_to_file, FileFormat
path, meta = write_payload_to_file('cmd.exe /c calc', FileFormat.VBS)
print(path)
"
```

## Full Example

```python
#!/usr/bin/env python3
from payload_file_writer import PayloadFileWriter, FileFormat
import os

# Initialize
writer = PayloadFileWriter(base_temp_dir="/tmp/payloads")

# Define payloads
payloads = {
    "registry": "reg add HKCU\\Software\\Test",
    "process": "start calc.exe",
    "network": "ipconfig /all"
}

try:
    # Generate
    results = writer.write_payload_batch(
        payloads,
        file_format=FileFormat.BAT,
        obfuscation_level="high"
    )

    # Process
    for name, (path, meta) in results.items():
        if path:
            print(f"✓ {name}: {path}")
            print(f"  Size: {meta.encoded_size} bytes")
            
            # Export metadata
            json_meta = writer.export_metadata_json(meta.file_id)
            print(f"  Meta: {json_meta[:100]}...")

finally:
    # Cleanup
    count = writer.cleanup_all()
    print(f"Cleaned up {count} files")
```

---

For full documentation, see `PAYLOAD_FILE_WRITER_GUIDE.md`

For examples, run `python3 payload_file_writer_examples.py`

For tests, run `python3 test_payload_file_writer.py`
