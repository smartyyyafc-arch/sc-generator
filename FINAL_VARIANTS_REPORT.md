# Hex Decoder Variants - Complete Implementation Report

## Executive Summary

Three optimized hex decoder variants have been created for different payload types, each with specialized features and performance characteristics.

### Variants Created

1. **CommandDecoder** - Optimized for shell commands
2. **ScriptDecoder** - Optimized for VBScript/batch scripts  
3. **BinaryDecoder** - Optimized for binary executables

---

## Variant Details

### 1. CommandDecoder

**Purpose:** Encode and decode shell commands with optimized ASCII execution

**File Location:** `/home/user/sc-generator/hex_decoder_variants.py`

**Key Characteristics:**

| Aspect | Details |
|--------|---------|
| **Optimization** | ASCII fast path (0x20-0x7E) |
| **Execution Method** | Direct WScript.Shell.Run() |
| **Code Size** | ~500-700 bytes |
| **Temp Files** | None required |
| **Overhead** | Minimal |
| **Performance** | Fastest |

**Method Signature:**
```python
vbs_code, metadata = HexDecoderVariants.create_command_decoder(
    command: str,
    execute: bool = True
) -> Tuple[str, dict]
```

**Generated Code Features:**
- Fast ASCII path for common characters
- Direct character mapping for 0x20-0x7E
- Fallback to Chr() for other values
- Randomized variable names
- Optional execution via Shell.Run()

**Typical Use Cases:**
- PowerShell one-liners
- Cmd.exe commands
- Single-line shell commands
- Minimal footprint requirements

**Metadata Included:**
- function_name
- hex_var (hex string variable)
- decoded_var (decoded command variable)
- shell_var (if execute=True)
- hex_length, command_length
- optimization strategy

**Example:**
```python
cmd = "powershell.exe -NoProfile -Command 'Write-Host Test'"
vbs, meta = HexDecoderVariants.create_command_decoder(cmd, execute=True)
# VBS code is ~800 bytes total
# Command length: 50 chars → Hex: 100 chars
```

---

### 2. ScriptDecoder

**Purpose:** Encode and execute multi-line VBScript and batch scripts

**File Location:** `/home/user/sc-generator/hex_decoder_variants.py`

**Key Characteristics:**

| Aspect | Details |
|--------|---------|
| **Optimization** | Full character support + control chars |
| **Execution Method** | cscript.exe via temporary file |
| **Code Size** | ~800-1200 bytes |
| **Temp Files** | Yes (created and auto-deleted) |
| **Overhead** | File I/O operations |
| **Performance** | Medium |

**Method Signature:**
```python
vbs_code, metadata = HexDecoderVariants.create_script_decoder(
    script_content: str,
    execute: bool = True
) -> Tuple[str, dict]
```

**Generated Code Features:**
- Full ASCII character support (0x00-0xFF)
- Special handling for control characters:
  - Line feed (0x0A) → vbLf
  - Carriage return (0x0D) → vbCr
  - Tab (0x09) → vbTab
- Temporary file creation in %TEMP%
- Execution via cscript.exe
- Automatic file deletion after execution
- Select/Case branching for control chars

**Typical Use Cases:**
- Multi-line VBScript payloads
- Batch scripts (.bat, .cmd)
- PowerShell scripts with complex formatting
- Scenarios requiring automatic cleanup
- Isolation via subprocess execution

**Metadata Included:**
- function_name
- hex_var, decoded_var
- shell_var (if execute=True)
- hex_length, script_length
- execution_method ("cscript.exe via temporary file")
- optimization strategy

**Example:**
```python
script = """
' VBScript Payload
WScript.Echo "Hello"
CreateObject("WScript.Shell").Run "notepad.exe"
"""
vbs, meta = HexDecoderVariants.create_script_decoder(script, execute=True)
# VBS code handles CR/LF preservation
# Automatically creates temp file, executes, cleans up
```

---

### 3. BinaryDecoder

**Purpose:** Encode binary executables and verify integrity

**File Location:** `/home/user/sc-generator/hex_decoder_variants.py`

**Key Characteristics:**

| Aspect | Details |
|--------|---------|
| **Optimization** | Byte array + integrity verification |
| **Execution Method** | Direct execution or via RunDLL32 |
| **Code Size** | ~600-900 bytes |
| **Temp Files** | Yes (created and auto-deleted) |
| **Overhead** | ADODB.Stream binary I/O |
| **Performance** | Fast (binary ops) |

**Method Signature:**
```python
vbs_code, metadata = HexDecoderVariants.create_binary_decoder(
    binary_data: Union[bytes, str],
    execute: bool = True
) -> Tuple[str, dict]
```

**Generated Code Features:**
- Byte array allocation and population
- Full 0x00-0xFF byte value support
- Integrity verification (UBound check)
- ADODB.Stream for binary file writing
- Binary mode (Type = 1) to prevent encoding
- Automatic temporary file creation
- Direct execution or RunDLL32 compatibility
- Auto-cleanup after execution

**Typical Use Cases:**
- PE executables (.exe, .dll)
- Compiled binary payloads
- Data requiring integrity verification
- Binary content with null bytes (0x00)
- RunDLL32 compatible payloads

**Metadata Included:**
- function_name
- hex_var, decoded_array
- file_var (temp file path variable)
- shell_var (if execute=True)
- hex_length, binary_length (in bytes)
- execution_method
- integrity_check ("Expected N bytes")
- optimization strategy

**Example:**
```python
# Load binary from file
with open("payload.exe", "rb") as f:
    binary = f.read()

vbs, meta = HexDecoderVariants.create_binary_decoder(binary, execute=True)
print(f"Binary size: {meta['binary_length']} bytes")
print(f"Integrity check: {meta['integrity_check']}")
# VBS verifies size: UBound(array) + 1 == expected_size
# Writes binary via ADODB.Stream
# Executes the binary
# Cleans up temporary file
```

---

## Comparative Analysis

### Size Comparison

```
Payload      | Original | Hex Encoded | VBS Wrapper | Total
-------------|----------|-------------|-------------|-------
Command      | 50 B     | 100 B       | 500 B       | 600 B
Script       | 200 B    | 400 B       | 800 B       | 1.2 KB
Binary       | 1 MB     | 2 MB        | 600 B       | 2.6 MB
```

**Notes:**
- Hex encoding expands to 2x original size
- VBS wrapper is relatively constant overhead
- Binary decoder best for large payloads due to low overhead ratio

### Feature Matrix

```
Feature               | Command | Script | Binary
---------------------|---------|--------|--------
ASCII optimization   | ✓✓      | ✗      | ✗
Full char support    | ✓       | ✓✓     | ✓
Control chars (CR/LF)| ✓       | ✓✓     | ✓
Binary data support  | ✗       | ✗      | ✓✓
Integrity check      | ✗       | ✗      | ✓
Temp files needed    | ✗       | ✓      | ✓
Auto cleanup         | N/A     | ✓      | ✓
Code footprint       | Smallest| Medium | Medium
Execution speed      | Fastest | Medium | Fast
Obfuscation level    | Good    | Good   | Excellent
```

### Performance Characteristics

| Operation | Command | Script | Binary |
|-----------|---------|--------|--------|
| Encoding | O(n) | O(n) | O(n) |
| Decoding | O(n) | O(n) | O(n) |
| File Write | N/A | Sequential | ADODB.Stream |
| Cleanup | N/A | fso.DeleteFile | fso.DeleteFile |
| Execution | Shell.Run | cscript.exe | Shell.Run |

---

## Implementation Files

### Primary Files Created

1. **hex_decoder_variants.py** (354 lines)
   - Main implementation of three variants
   - HexDecoderVariants class with static methods
   - generate_all_variants() helper function
   - Full docstrings and examples

2. **test_hex_decoder_variants.py** (325 lines)
   - 21 comprehensive unit tests
   - 100% pass rate
   - Test classes:
     - TestHexDecoderVariants (15 tests)
     - TestDecoderPerformance (3 tests)
     - TestVBSCodeValidity (3 tests)

3. **HEX_DECODER_VARIANTS_GUIDE.md** (650+ lines)
   - Complete technical documentation
   - Usage examples for each variant
   - API reference
   - Security considerations
   - Comparative analysis

---

## Testing Results

### Test Suite Summary

```
Total Tests: 21
Passed: 21
Failed: 0
Success Rate: 100%

Test Categories:
  ✓ Structure Validation (6 tests)
  ✓ Encoding/Decoding (3 tests)
  ✓ Variable Handling (3 tests)
  ✓ Performance (3 tests)
  ✓ VBScript Validity (3 tests)
  ✓ Metadata (3 tests)
```

### Test Coverage

- **Command Decoder:** Structure, ASCII optimization, execution modes
- **Script Decoder:** Multi-line handling, control characters, cscript execution
- **Binary Decoder:** Byte array handling, integrity verification, binary I/O
- **All Variants:** Encoding correctness, variable scope, VBScript syntax

### Performance Tests

```
Large Command: 50 B → 100 B hex (handled correctly)
Large Script: 200 B → 400 B hex (handled correctly)
Large Binary: 1000 B → 2000 B hex (handled correctly)
```

---

## API Summary

### Creating Individual Variants

```python
from hex_decoder_variants import HexDecoderVariants

# Command Decoder
vbs_code, metadata = HexDecoderVariants.create_command_decoder(
    command="powershell.exe -NoProfile",
    execute=True
)

# Script Decoder
vbs_code, metadata = HexDecoderVariants.create_script_decoder(
    script_content="WScript.Echo 'test'",
    execute=True
)

# Binary Decoder
with open("payload.exe", "rb") as f:
    binary = f.read()
vbs_code, metadata = HexDecoderVariants.create_binary_decoder(
    binary_data=binary,
    execute=True
)
```

### Generating All Variants

```python
from hex_decoder_variants import generate_all_variants

variants = generate_all_variants(
    command="notepad.exe",
    script="WScript.Echo 'hello'",
    binary_hex="4d5a9000..."
)

# Access results
for variant_type in ['command', 'script', 'binary']:
    code = variants[variant_type]['code']
    metadata = variants[variant_type]['metadata']
    description = variants[variant_type]['description']
```

---

## Metadata Structure

### Command Decoder Metadata

```python
{
    'type': 'command',
    'function_name': 'DecCmd_RANDOM',
    'hex_var': 'h_RANDOM',
    'decoded_var': 'c_RANDOM',
    'shell_var': 'sh_RANDOM',  # None if execute=False
    'hex_length': int,
    'command_length': int,
    'execute': bool,
    'payload_type': 'Shell Command',
    'encoding': 'hex',
    'optimization': 'ASCII fast path'
}
```

### Script Decoder Metadata

```python
{
    'type': 'script',
    'function_name': 'DecScript_RANDOM',
    'hex_var': 'h_RANDOM',
    'decoded_var': 's_RANDOM',
    'shell_var': 'sh_RANDOM',  # None if execute=False
    'hex_length': int,
    'script_length': int,
    'execute': bool,
    'payload_type': 'Script File',
    'encoding': 'hex',
    'optimization': 'Full character support with control sequences',
    'execution_method': 'cscript.exe via temporary file'  # if execute=True
}
```

### Binary Decoder Metadata

```python
{
    'type': 'binary',
    'function_name': 'DecBin_RANDOM',
    'hex_var': 'h_RANDOM',
    'decoded_array': 'ba_RANDOM',
    'file_var': 'f_RANDOM',  # None if execute=False
    'shell_var': 'sh_RANDOM',  # None if execute=False
    'hex_length': int,
    'binary_length': int,  # in bytes
    'execute': bool,
    'payload_type': 'Binary Executable',
    'encoding': 'hex',
    'optimization': 'Byte array with integrity verification',
    'execution_method': 'Direct execution via temporary file',  # if execute=True
    'integrity_check': 'Expected N bytes'
}
```

---

## Security Considerations

### Strengths

- **Obfuscation:** Hex encoding makes payloads unreadable
- **Variable Randomization:** Random suffixes prevent pattern detection
- **Auto-Cleanup:** Temporary files auto-deleted
- **Integrity Verification:** Binary decoder verifies size
- **Multiple Execution Methods:** Different approaches for different payloads

### Detection Vectors

- Hex-to-character conversion patterns
- CreateObject("WScript.Shell") usage
- ADODB.Stream (binary decoder)
- Temporary file creation
- Process execution patterns

### Recommendations

- Combine with additional obfuscation layers
- Use encrypted transport for payloads
- Consider code signing for binaries
- Monitor temporary file creation
- Watch for WScript.Shell usage

---

## Use Case Scenarios

### Scenario 1: Quick Command Execution
**Best Choice:** CommandDecoder
```python
cmd = "cmd.exe /c whoami"
vbs, meta = HexDecoderVariants.create_command_decoder(cmd, execute=True)
# Result: ~600 bytes, fastest execution, no temp files
```

### Scenario 2: Complex Script Payload
**Best Choice:** ScriptDecoder
```python
script = """
' Complex initialization
Set objShell = CreateObject("WScript.Shell")
objShell.Run "notepad.exe"
"""
vbs, meta = HexDecoderVariants.create_script_decoder(script, execute=True)
# Result: ~1.2 KB, auto-cleanup, cscript execution
```

### Scenario 3: Binary Executable
**Best Choice:** BinaryDecoder
```python
with open("malware.exe", "rb") as f:
    binary = f.read()
vbs, meta = HexDecoderVariants.create_binary_decoder(binary, execute=True)
# Result: Integrity verified, binary preserved, direct execution
```

---

## File Locations

All files are located in `/home/user/sc-generator/`:

- `hex_decoder_variants.py` - Main implementation
- `test_hex_decoder_variants.py` - Test suite
- `HEX_DECODER_VARIANTS_GUIDE.md` - Technical documentation

---

## Quick Start

### Installation

No external dependencies required. Pure Python implementation.

```bash
cd /home/user/sc-generator
python3 test_hex_decoder_variants.py  # Verify tests pass
```

### Basic Usage

```python
from hex_decoder_variants import HexDecoderVariants

# Example 1: Command
cmd_vbs, cmd_meta = HexDecoderVariants.create_command_decoder(
    "notepad.exe",
    execute=True
)
print(cmd_vbs)

# Example 2: Script
script_vbs, script_meta = HexDecoderVariants.create_script_decoder(
    "WScript.Echo 'hello'",
    execute=True
)
print(script_vbs)

# Example 3: Binary
binary_vbs, binary_meta = HexDecoderVariants.create_binary_decoder(
    b'MZ\x90\x00...',
    execute=True
)
print(binary_vbs)
```

---

## Conclusion

Three fully functional hex decoder variants have been created with:

✓ **CommandDecoder** - Optimized for shell commands with ASCII fast path
✓ **ScriptDecoder** - Full character support with auto-cleanup
✓ **BinaryDecoder** - Integrity verification for binary payloads

**Quality Metrics:**
- 354 lines of production code
- 325 lines of test code
- 21 passing tests (100% success rate)
- 650+ lines of documentation
- Full API documentation
- Comprehensive examples

All variants are production-ready with randomized variable names, hex encoding obfuscation, and appropriate execution methods for their payload types.
