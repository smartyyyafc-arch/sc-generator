# File Disguiser - File Writer with Deceptive Extensions

A Python utility for creating files with disguised extensions that hide actual file content behind legitimate-looking file types (txt, doc, pdf, etc.).

## Features

- **Multiple Disguise Types**: Hide content as TXT, DOC, DOCX, PDF, XLS, XLSX, PPT, PPTX, CSV, JSON, LOG, DAT, BIN, and more
- **Flexible Content**: Support for both text and binary content
- **File Tracking**: Maintains metadata about disguised files for later extraction
- **Easy Extraction**: Recover original content from disguised files
- **Unicode Support**: Handle international characters and special encodings
- **Large File Support**: Process files of any size

## Installation

```bash
# Copy the file_disguiser.py to your project
cp file_disguiser.py /path/to/your/project/
```

No external dependencies required - uses only Python standard library.

## Usage

### Basic Text Disguise

```python
from file_disguiser import FileDisguiser, DisguiseType

# Initialize disguiser
disguiser = FileDisguiser("./hidden_files")

# Hide Python code as a text file
code = "print('Hello, World!')"
path = disguiser.write_disguised_text("script", code, DisguiseType.TXT)
# Creates: ./hidden_files/script.txt (contains Python code)
```

### Binary Content Disguise

```python
# Hide binary data as PDF
binary_data = b"\x89PNG\r\n\x1a\n" + b"image data"
path = disguiser.write_disguised_binary("image", binary_data, DisguiseType.PDF)
# Creates: ./hidden_files/image.pdf (contains binary data)
```

### Reading Disguised Files

```python
# Read content from disguised file
content = disguiser.read_disguised(path)
print(content)  # Raw bytes
```

### Extracting Original Content

```python
# Recover original file from disguise
extracted_path = disguiser.undisguise(path)
# Creates: ./hidden_files/script (original filename)
```

### File Information

```python
# Get metadata about a disguised file
info = disguiser.get_file_info(path)
print(info)
# Output:
# {
#     'original_name': 'script',
#     'disguise_ext': 'txt',
#     'size': 24,
#     'content_type': 'str'
# }
```

### List All Disguised Files

```python
# View all tracked disguised files
files = disguiser.list_disguised_files()
for f in files:
    print(f"{f['original_name']}.{f['disguise_ext']} ({f['size']} bytes)")
```

## API Reference

### FileDisguiser Class

#### Constructor
```python
FileDisguiser(base_dir: Optional[str] = None)
```
- `base_dir`: Directory to store disguised files (default: current directory)

#### Methods

**write_disguised(filename, content, disguise_as=DisguiseType.TXT, encoding='utf-8')**
- Write content to disguised file
- `filename`: Original filename without extension
- `content`: String or bytes to write
- `disguise_as`: DisguiseType enum or string extension
- Returns: Path to created file

**write_disguised_text(filename, text_content, disguise_as=DisguiseType.TXT, encoding='utf-8')**
- Write text content to disguised file
- Returns: Path to created file

**write_disguised_binary(filename, binary_content, disguise_as=DisguiseType.BIN)**
- Write binary content to disguised file
- Returns: Path to created file

**read_disguised(disguised_path)**
- Read raw bytes from disguised file
- Returns: File content as bytes

**get_file_info(disguised_path)**
- Get metadata about a disguised file
- Returns: Dictionary with file information

**undisguise(disguised_path, output_path=None)**
- Extract content and save with original filename
- Returns: Path to extracted file

**list_disguised_files()**
- List all tracked disguised files
- Returns: List of metadata dictionaries

### Convenience Functions

**create_disguised_payload(data, filename='payload', disguise_as='txt', output_dir='.')**
- Quick function to create a disguised file
- Returns: Path to created file

**extract_disguised_file(disguised_path, output_path=None)**
- Quick function to extract a disguised file
- Returns: Path to extracted file

## Supported Disguise Types

```
TXT   - Plain text files (.txt)
DOC   - Legacy Word documents (.doc)
DOCX  - Modern Word documents (.docx)
PDF   - PDF documents (.pdf)
XLS   - Legacy Excel spreadsheets (.xls)
XLSX  - Modern Excel spreadsheets (.xlsx)
PPT   - Legacy PowerPoint presentations (.ppt)
PPTX  - Modern PowerPoint presentations (.pptx)
CSV   - Comma-separated values (.csv)
JSON  - JSON data files (.json)
LOG   - Log files (.log)
DAT   - Generic data files (.dat)
BIN   - Binary files (.bin)
```

## Examples

### Example 1: Hide Configuration Data

```python
from file_disguiser import FileDisguiser, DisguiseType

disguiser = FileDisguiser("./configs")

# Hide API configuration as a log file
config = """
api_key=sk_test_123456789
endpoint=https://api.example.com
timeout=30
"""

config_file = disguiser.write_disguised_text("app_config", config, DisguiseType.LOG)
print(f"Config hidden as: {config_file}")
```

### Example 2: Hide Binary Executable

```python
# Read an actual binary file
with open("malware_sample", "rb") as f:
    executable = f.read()

# Disguise as PDF
hidden_exe = disguiser.write_disguised_binary(
    "document",
    executable,
    DisguiseType.PDF
)

# Later, extract it
disguiser.undisguise(hidden_exe, "extracted_executable")
```

### Example 3: Batch Disguise Multiple Files

```python
files_to_hide = {
    "script.py": (open("script.py").read(), DisguiseType.TXT),
    "data.json": (open("data.json").read(), DisguiseType.LOG),
    "image.png": (open("image.png", "rb").read(), DisguiseType.PDF),
}

for original_name, (content, disguise_type) in files_to_hide.items():
    base_name = original_name.rsplit(".", 1)[0]
    disguiser.write_disguised(base_name, content, disguise_type)
```

## Testing

Run the test suite:

```bash
python -m pytest test_file_disguiser.py -v
```

Or with unittest:

```bash
python -m unittest test_file_disguiser.py
```

## Use Cases

- **Security**: Hide sensitive files with inconspicuous extensions
- **Obfuscation**: Disguise malicious payloads as benign file types
- **Data Protection**: Store confidential data behind legitimate-looking extensions
- **Steganography**: Embed content in files with misleading types
- **Testing**: Simulate file type mismatches and error handling
- **Development**: Test file processing without revealing actual content

## Performance Notes

- Supports files of any size (memory-limited only by available RAM)
- File metadata tracking uses minimal memory
- No compression or encryption applied (content stored as-is)
- Fast read/write operations using standard file I/O

## Security Disclaimer

This tool provides **obfuscation only**, not encryption or true security. Files are stored as plain content with misleading extensions. For actual security:
- Use encryption (AES, etc.)
- Implement proper access controls
- Use file integrity verification
- Consider digital signatures

## License

Open source utility for file management and testing.

## Author

Claude Code - File Disguiser Tool
