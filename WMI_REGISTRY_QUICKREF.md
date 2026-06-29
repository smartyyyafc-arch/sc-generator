# WMI Registry Access - Quick Reference Card

## Quick Start

```python
from wmi_registry_access import create_registry_accessor

accessor = create_registry_accessor()

# Read
code = accessor.read_registry_value("HKLM", "SOFTWARE", "Value")

# Write
code = accessor.write_registry_value("HKCU", "SOFTWARE\\MyApp", "Key", "Value")

# Execute the generated VBS code
# Save to .vbs file and run or execute directly
```

## Common Operations

### Read String Value
```python
code = accessor.read_registry_value("HKLM", "SOFTWARE", "TestValue")
```

### Read DWORD Value
```python
code = accessor.read_registry_dword("HKCU", "SOFTWARE", "TestDWORD")
```

### Read Binary Value
```python
code = accessor.read_registry_binary("HKCU", "SOFTWARE", "BinaryData")
```

### Write String Value
```python
code = accessor.write_registry_value("HKCU", "SOFTWARE\\MyApp", "Name", "Value")
```

### Write DWORD Value
```python
code = accessor.write_registry_dword("HKCU", "SOFTWARE\\MyApp", "Count", 1000)
```

### Write Binary Value
```python
code = accessor.write_registry_binary("HKCU", "SOFTWARE", "Data", "DEADBEEF")
```

### Delete Value
```python
code = accessor.delete_registry_value("HKCU", "SOFTWARE\\MyApp", "OldKey")
```

### Delete Key
```python
code = accessor.delete_registry_key("HKCU", "SOFTWARE\\MyApp")
```

### Create Key
```python
code = accessor.create_registry_key("HKCU", "SOFTWARE\\MyApp")
```

### Enumerate Keys
```python
code = accessor.enum_registry_keys("HKLM", "SOFTWARE")
```

### Enumerate Values
```python
code = accessor.enum_registry_values("HKLM", "SOFTWARE\\Microsoft")
```

### Check Key Exists
```python
code = accessor.check_registry_key_exists("HKLM", "SOFTWARE\\Microsoft")
```

## High-Level Functions

```python
from wmi_registry_access import read_registry, write_registry

# Read with type
code = read_registry("HKLM", "SOFTWARE", "Value", "string")
code = read_registry("HKCU", "SOFTWARE", "Counter", "dword")
code = read_registry("HKCU", "SOFTWARE", "Data", "binary")

# Write with type
code = write_registry("HKCU", "SOFTWARE", "Value", "data", "string")
code = write_registry("HKCU", "SOFTWARE", "Counter", "100", "dword")
code = write_registry("HKCU", "SOFTWARE", "Data", "DEADBEEF", "binary")
```

## Registry Hives

| Abbreviation | Full Name |
|--------------|-----------|
| HKLM | HKEY_LOCAL_MACHINE |
| HKCU | HKEY_CURRENT_USER |
| HKCR | HKEY_CLASSES_ROOT |
| HKU | HKEY_USERS |
| HKCC | HKEY_CURRENT_CONFIG |

## Configuration

```python
from wmi_registry_access import RegistryConfig, create_registry_accessor

# Obfuscated (stealth)
config = RegistryConfig(obfuscate_names=True, hide_errors=True)
accessor = create_registry_accessor(config)

# Clean (debugging)
config = RegistryConfig(obfuscate_names=False, hide_errors=False)
accessor = create_registry_accessor(config)
```

## Return Values

All methods return **VBScript code as strings**:

```python
code = accessor.read_registry_value("HKLM", "SOFTWARE", "Value")
# code is now a string containing VBS code

# Save to file
with open("script.vbs", "w") as f:
    f.write(code)

# Or execute directly via cmd or PowerShell
import subprocess
subprocess.run(["cscript.exe", "script.vbs"])
```

## Typical VBS Output

```vbs
On Error Resume Next
Dim regLoc_AbCd, regSvc_EfGh, ...
Set regLoc_AbCd = CreateObject("WbemScripting.SWbemLocator")
Set regSvc_EfGh = regLoc_AbCd.ConnectServer(".", "root\default")
' ... rest of code ...
On Error GoTo 0
```

## Error Handling

### Silent Mode (Default)
```python
config = RegistryConfig(hide_errors=True)
# Errors are suppressed, empty/0 values returned
```

### Explicit Mode
```python
config = RegistryConfig(hide_errors=False)
# Errors are captured, can check ReturnValue
```

## Complete Workflow Example

```python
from wmi_registry_access import create_registry_accessor

accessor = create_registry_accessor()

# 1. Create key
code1 = accessor.create_registry_key("HKCU", "SOFTWARE\\MyApp")

# 2. Write values
code2 = accessor.write_registry_value("HKCU", "SOFTWARE\\MyApp", "Version", "1.0.0")
code3 = accessor.write_registry_dword("HKCU", "SOFTWARE\\MyApp", "Build", 1001)

# 3. Read values
code4 = accessor.read_registry_value("HKCU", "SOFTWARE\\MyApp", "Version")

# 4. Enumerate
code5 = accessor.enum_registry_values("HKCU", "SOFTWARE\\MyApp")

# 5. Delete key
code6 = accessor.delete_registry_key("HKCU", "SOFTWARE\\MyApp")

# Combine all
combined = "\n\n".join([code1, code2, code3, code4, code5, code6])
```

## Methods Summary

| Method | Purpose | Returns |
|--------|---------|---------|
| `read_registry_value` | Read string | VBS code |
| `read_registry_dword` | Read DWORD | VBS code |
| `read_registry_binary` | Read binary | VBS code (hex) |
| `write_registry_value` | Write string | VBS code |
| `write_registry_dword` | Write DWORD | VBS code |
| `write_registry_binary` | Write binary | VBS code |
| `delete_registry_value` | Delete value | VBS code |
| `delete_registry_key` | Delete key | VBS code |
| `create_registry_key` | Create key | VBS code |
| `enum_registry_keys` | List subkeys | VBS code |
| `enum_registry_values` | List values | VBS code |
| `check_registry_key_exists` | Check existence | VBS code |
| `get_registry_methods_report` | List all methods | Dict |

## Common Registry Paths

```python
# Windows Version
accessor.read_registry_value(
    "HKLM",
    "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
    "CurrentVersion"
)

# User Shell Folders
accessor.read_registry_value(
    "HKCU",
    "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders",
    "Desktop"
)

# Startup Programs
accessor.read_registry_value(
    "HKCU",
    "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    "SomeProgram"
)

# System Settings
accessor.read_registry_value(
    "HKLM",
    "SYSTEM\\CurrentControlSet\\Services",
    "ServiceName"
)
```

## Batch Operations

```python
# Multiple reads
reads = [
    accessor.read_registry_value("HKLM", "SOFTWARE", "Value1"),
    accessor.read_registry_value("HKLM", "SOFTWARE", "Value2"),
    accessor.read_registry_value("HKLM", "SOFTWARE", "Value3"),
]

# Multiple writes
writes = [
    accessor.write_registry_value("HKCU", "SOFTWARE\\App", "Key1", "Val1"),
    accessor.write_registry_value("HKCU", "SOFTWARE\\App", "Key2", "Val2"),
    accessor.write_registry_value("HKCU", "SOFTWARE\\App", "Key3", "Val3"),
]

# Combine
all_code = "\n\n".join(reads + writes)
```

## Tips & Tricks

### Escaping Quotes
Quotes in values are automatically escaped:
```python
accessor.write_registry_value(
    "HKCU", "SOFTWARE", "Note", 'He said "hello"'
)
# Automatically becomes: 'He said \"hello\"'
```

### Hex Data Format
Binary data should be provided as hex string:
```python
# "Hello" in hex
accessor.write_registry_binary("HKCU", "SOFTWARE", "Data", "48656C6C6F")

# Uppercase or lowercase both work
accessor.write_registry_binary("HKCU", "SOFTWARE", "Data", "DEADBEEF")
accessor.write_registry_binary("HKCU", "SOFTWARE", "Data", "deadbeef")
```

### Getting Random Variable Names
Each accessor instance generates unique variable names per operation:
```python
accessor = create_registry_accessor(RegistryConfig(obfuscate_names=True))
code1 = accessor.read_registry_value("HKLM", "SOFTWARE", "Value")
code2 = accessor.read_registry_value("HKLM", "SOFTWARE", "Value")
# code1 and code2 have different variable names
```

## Debugging

### See Generated Code
```python
accessor = create_registry_accessor()
code = accessor.read_registry_value("HKLM", "SOFTWARE", "Value")
print(code)  # Print the generated VBS code
```

### Clean Variable Names (No Obfuscation)
```python
config = RegistryConfig(obfuscate_names=False)
accessor = create_registry_accessor(config)
code = accessor.read_registry_value("HKLM", "SOFTWARE", "Value")
# Variable names will be: regLoc, regSvc, regMeth, etc.
```

### Explicit Error Handling
```python
config = RegistryConfig(hide_errors=False)
accessor = create_registry_accessor(config)
code = accessor.read_registry_value("HKLM", "SOFTWARE", "Value")
# VBS code will show "On Error GoTo 0" instead of silent mode
```

## Files

- **Module**: `wmi_registry_access.py`
- **Examples**: `wmi_registry_examples.py` (20 examples)
- **Full Guide**: `WMI_REGISTRY_GUIDE.md`
- **API Reference**: `WMI_REGISTRY_API_REFERENCE.md`
- **Summary**: `WMI_REGISTRY_SUMMARY.md`

## Related Modules

- `wmi_executor.py` - Process execution via WMI
- `wmi_executor_examples.py` - Execution examples

## Command Line Usage

```bash
# Run all examples
python wmi_registry_examples.py

# Run specific example
python wmi_registry_examples.py 1

# Run module tests
python wmi_registry_access.py
```

## Performance Notes

- **Code Generation**: <1ms per operation
- **VBS Execution**: 10-50ms per operation
- **Best Practice**: Batch operations together
- **Recommended Batch Size**: 1-1000 operations

## Supported Data Types

| Type | Method | Max Size | Notes |
|------|--------|----------|-------|
| String (REG_SZ) | get/set_registry_value | 256KB | Supports unicode |
| DWORD (REG_DWORD) | get/set_registry_dword | 4 bytes | 0-4294967295 |
| Binary (REG_BINARY) | get/set_registry_binary | 2GB | As hex string |

## Limitations

- No direct QWORD (64-bit) support
- No direct MULTI_SZ (multi-string) support
- Enumeration limited to array size
- Requires appropriate registry permissions
- No remote registry access built-in

## Quick Examples

### Example 1: Check Windows Version
```python
from wmi_registry_access import read_registry
code = read_registry("HKLM", "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", "CurrentVersion")
```

### Example 2: Write Custom Setting
```python
from wmi_registry_access import write_registry
code = write_registry("HKCU", "SOFTWARE\\MyApp", "Setting", "Value")
```

### Example 3: Delete Unwanted Entry
```python
from wmi_registry_access import create_registry_accessor
accessor = create_registry_accessor()
code = accessor.delete_registry_value("HKCU", "SOFTWARE\\Unwanted", "Key")
```

---

**For complete information, see WMI_REGISTRY_GUIDE.md**
