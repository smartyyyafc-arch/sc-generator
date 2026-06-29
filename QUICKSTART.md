# File Disguiser - Quick Start Guide

## Installation

```bash
cp file_disguiser.py /your/project/
```

## 5-Minute Start

### 1. Hide a Text File

```python
from file_disguiser import FileDisguiser, DisguiseType

# Create disguiser
d = FileDisguiser("./hidden")

# Hide Python code as .txt
path = d.write_disguised_text("mycode", "print('secret')", DisguiseType.TXT)
# Result: ./hidden/mycode.txt (contains Python code)
```

### 2. Hide Binary Data

```python
# Hide binary as .pdf
with open("image.png", "rb") as f:
    data = f.read()

path = d.write_disguised_binary("document", data, DisguiseType.PDF)
# Result: ./hidden/document.pdf (contains PNG data)
```

### 3. Read Disguised File

```python
# Read what's inside
content = d.read_disguised(path)
print(content)  # Raw bytes
```

### 4. Extract Original

```python
# Get original file back
original = d.undisguise(path)
# Result: ./hidden/mycode (no extension)
```

### 5. Track Files

```python
# See what you've hidden
for file_info in d.list_disguised_files():
    print(f"{file_info['original_name']}.{file_info['disguise_ext']}")
```

## Common Patterns

### Hide Configuration as Log File

```python
from file_disguiser import FileDisguiser, DisguiseType

d = FileDisguiser(".")
config = "secret_key=abc123\napi_url=https://..."
d.write_disguised_text("config", config, DisguiseType.LOG)
# Creates: config.log (hides .env-like content)
```

### Hide Payload as Word Document

```python
payload = b"\x4d\x5a\x90\x00..."  # Binary executable
d.write_disguised_binary("resume", payload, DisguiseType.DOCX)
# Creates: resume.docx (contains executable)
```

### Hide JSON as Text

```python
json_data = '{"api_key": "secret"}'
d.write_disguised_text("data", json_data, "txt")
# Creates: data.txt (contains JSON)
```

## Supported Extensions

```
.txt, .doc, .docx, .pdf, .xls, .xlsx, 
.ppt, .pptx, .csv, .json, .log, .dat, .bin
```

## Quick Functions

```python
# One-liner to hide a file
from file_disguiser import create_disguised_payload
create_disguised_payload("secret", "file", "pdf", ".")

# One-liner to extract
from file_disguiser import extract_disguised_file
extract_disguised_file("file.pdf", "output")
```

## File Tracking

The disguiser maintains a `file_map` with metadata:

```python
info = d.get_file_info("mycode.txt")
print(info)
# {
#     'original_name': 'mycode',
#     'disguise_ext': 'txt',
#     'size': 16,
#     'content_type': 'str'
# }
```

## Advanced: Custom Extension

```python
# Use any extension string
d.write_disguised_text("file", "content", "xyz")
# Creates: file.xyz
```

## Testing

```bash
python -m unittest test_file_disguiser.py -v
```

**All 11 tests pass** - covers text, binary, unicode, large files, extraction, tracking.

## Key Methods

| Method | Purpose |
|--------|---------|
| `write_disguised_text()` | Hide text content |
| `write_disguised_binary()` | Hide binary content |
| `read_disguised()` | Read from disguised file |
| `undisguise()` | Extract and save original |
| `get_file_info()` | Get file metadata |
| `list_disguised_files()` | List all tracked files |

## Real-World Example

```python
from file_disguiser import FileDisguiser, DisguiseType

# Initialize
disguiser = FileDisguiser("./secure_storage")

# Hide multiple files
with open("script.py") as f:
    disguiser.write_disguised_text("script", f.read(), DisguiseType.TXT)

with open("config.json") as f:
    disguiser.write_disguised_text("config", f.read(), DisguiseType.LOG)

with open("data.bin", "rb") as f:
    disguiser.write_disguised_binary("data", f.read(), DisguiseType.PDF)

# List what's hidden
for info in disguiser.list_disguised_files():
    print(f"Hidden: {info['original_name']}.{info['disguise_ext']}")

# Later: recover specific file
recovered = disguiser.undisguise("./secure_storage/script.txt")
```

## Important Notes

- **Obfuscation only** - Not encryption. Use for hiding, not security.
- **No compression** - Files stored as-is
- **Tracks metadata** - Remembers original names and types
- **Supports all sizes** - Limited only by available disk/RAM
- **Unicode ready** - Handles international characters

## Troubleshooting

**Q: File not found when undisguising**
```python
# Specify full path
disguiser.undisguise("./hidden/myfile.txt", "./output/myfile")
```

**Q: How to hide without tracking?**
```python
# Just write the file directly
with open("file.pdf", "wb") as f:
    f.write(content)
```

**Q: Can I change the disguise after creation?**
```python
# Extract and re-hide with new disguise
content = disguiser.read_disguised("old.pdf")
disguiser.write_disguised_binary("file", content, "docx")
```

---

**Ready to use!** Copy `file_disguiser.py` and start hiding files.
