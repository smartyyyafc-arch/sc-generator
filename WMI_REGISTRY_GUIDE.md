# WMI Registry Access Module - Complete Guide

## Overview

The WMI Registry Access module provides comprehensive functions for reading and writing Windows registry values through WbemScripting.SWbemLocator. This enables secure, WMI-based registry operations on HKLM and HKCU without direct registry file access.

## Key Features

- **Multiple Registry Types**: Supports REG_SZ (string), REG_DWORD (32-bit), REG_BINARY (binary), and more
- **Dual Hive Support**: Works with HKEY_LOCAL_MACHINE (HKLM) and HKEY_CURRENT_USER (HKCU)
- **Obfuscation Support**: Optional variable name obfuscation for stealth
- **Error Handling**: Configurable error suppression for covert operations
- **Key Operations**: Create, delete, enumerate, and check registry keys
- **Value Operations**: Read, write, delete, and enumerate registry values
- **StdRegProv Integration**: Uses Windows Management Instrumentation's StdRegProv class

## Architecture

### Core Components

#### `WMIRegistryAccess` Class
Main class providing all registry operations through WMI.

```python
from wmi_registry_access import create_registry_accessor

accessor = create_registry_accessor()
code = accessor.read_registry_value("HKLM", "SOFTWARE", "TestValue")
```

#### `RegistryConfig` Dataclass
Configuration options for registry access behavior:

```python
from wmi_registry_access import RegistryConfig, create_registry_accessor

config = RegistryConfig(
    obfuscate_names=True,      # Randomize variable names
    hide_errors=True,          # Suppress error messages
    use_locator=True,          # Use SWbemLocator
    encode_values=False        # Encode values (future)
)

accessor = create_registry_accessor(config)
```

## API Reference

### Registry Hives

Supported registry hives:
- `HKLM` - HKEY_LOCAL_MACHINE (0x80000002)
- `HKCU` - HKEY_CURRENT_USER (0x80000001)
- `HKCR` - HKEY_CLASSES_ROOT (0x80000000)
- `HKU` - HKEY_USERS (0x80000003)
- `HKCC` - HKEY_CURRENT_CONFIG (0x80000005)

### Read Operations

#### `read_registry_value(hive, key_path, value_name)`
Read string value from registry.

```python
code = accessor.read_registry_value(
    "HKLM",
    "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
    "CurrentVersion"
)
```

**Returns**: VBS code string that:
- Reads string value via StdRegProv.GetStringValue
- Returns value or empty string on error
- Includes error handling

#### `read_registry_dword(hive, key_path, value_name)`
Read DWORD (32-bit integer) value.

```python
code = accessor.read_registry_dword(
    "HKCU",
    "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer",
    "NoViewOnDrive"
)
```

**Returns**: VBS code that reads DWORD via StdRegProv.GetDWORDValue

#### `read_registry_binary(hive, key_path, value_name)`
Read binary value.

```python
code = accessor.read_registry_binary(
    "HKCU",
    "Software\\Settings",
    "BinaryData"
)
```

**Returns**: VBS code that reads binary via StdRegProv.GetBinaryValue and converts to hex string

### Write Operations

#### `write_registry_value(hive, key_path, value_name, value_data, value_type="REG_SZ")`
Write string value to registry.

```python
code = accessor.write_registry_value(
    "HKCU",
    "Software\\MyApp",
    "AppName",
    "My Application"
)
```

**Parameters**:
- `hive`: Registry hive
- `key_path`: Full registry path
- `value_name`: Name of value to write
- `value_data`: String data to write
- `value_type`: Type of value (default: REG_SZ)

**Returns**: VBS code that writes string via StdRegProv.SetStringValue

#### `write_registry_dword(hive, key_path, value_name, value_data)`
Write DWORD value.

```python
code = accessor.write_registry_dword(
    "HKCU",
    "Software\\MyApp\\Settings",
    "Timeout",
    30000
)
```

**Parameters**:
- `value_data`: Integer value to write (0-4294967295)

**Returns**: VBS code that writes DWORD via StdRegProv.SetDWORDValue

#### `write_registry_binary(hive, key_path, value_name, hex_data)`
Write binary value.

```python
code = accessor.write_registry_binary(
    "HKCU",
    "Software\\MyApp",
    "BinaryData",
    "48656C6C6F"  # "Hello" in hex
)
```

**Parameters**:
- `hex_data`: Hex string of binary data (e.g., "DEADBEEF")

**Returns**: VBS code that converts hex to byte array and writes via StdRegProv.SetBinaryValue

### Deletion Operations

#### `delete_registry_value(hive, key_path, value_name)`
Delete registry value.

```python
code = accessor.delete_registry_value(
    "HKCU",
    "Software\\MyApp",
    "TestValue"
)
```

**Returns**: VBS code that deletes value via StdRegProv.DeleteValue

#### `delete_registry_key(hive, key_path)`
Delete registry key.

```python
code = accessor.delete_registry_key(
    "HKCU",
    "Software\\MyApp\\SubKey"
)
```

**Returns**: VBS code that deletes key via StdRegProv.DeleteKey

### Enumeration Operations

#### `enum_registry_keys(hive, key_path)`
Enumerate subkeys in a registry key.

```python
code = accessor.enum_registry_keys(
    "HKLM",
    "SOFTWARE\\Microsoft"
)
```

**Returns**: VBS code that enumerates keys via StdRegProv.EnumKey

**Output Format**: Returns array of subkey names in `sNames`

#### `enum_registry_values(hive, key_path)`
Enumerate values in a registry key.

```python
code = accessor.enum_registry_values(
    "HKLM",
    "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion"
)
```

**Returns**: VBS code that enumerates values via StdRegProv.EnumValues

**Output Format**: Returns two arrays:
- `sNames`: Array of value names
- `Types`: Array of value types

### Management Operations

#### `create_registry_key(hive, key_path)`
Create registry key.

```python
code = accessor.create_registry_key(
    "HKCU",
    "Software\\MyApp\\SubKey"
)
```

**Returns**: VBS code that creates key via StdRegProv.CreateKey

#### `check_registry_key_exists(hive, key_path)`
Check if registry key exists.

```python
code = accessor.check_registry_key_exists(
    "HKLM",
    "SOFTWARE\\Microsoft\\Windows"
)
```

**Returns**: VBS code that checks existence (returns True/False in `keyExists` variable)

### High-Level Convenience Functions

#### `read_registry(hive, key_path, value_name, value_type="string")`
Simplified read function.

```python
from wmi_registry_access import read_registry

# Read string
code = read_registry("HKLM", "SOFTWARE", "TestValue", "string")

# Read DWORD
code = read_registry("HKCU", "SOFTWARE", "TestDWORD", "dword")

# Read binary
code = read_registry("HKCU", "SOFTWARE", "TestBinary", "binary")
```

**Parameters**:
- `value_type`: "string", "dword", or "binary"

#### `write_registry(hive, key_path, value_name, value_data, value_type="string")`
Simplified write function.

```python
from wmi_registry_access import write_registry

# Write string
code = write_registry("HKCU", "SOFTWARE\\MyApp", "AppName", "MyApp")

# Write DWORD
code = write_registry("HKCU", "SOFTWARE\\MyApp", "Counter", "1000", "dword")

# Write binary
code = write_registry("HKCU", "SOFTWARE\\MyApp", "BinData", "DEADBEEF", "binary")
```

## Usage Examples

### Example 1: Read Windows Version

```python
from wmi_registry_access import create_registry_accessor

accessor = create_registry_accessor()
code = accessor.read_registry_value(
    "HKLM",
    "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
    "CurrentVersion"
)
# Save code to .vbs file and execute
```

### Example 2: Write Application Settings

```python
accessor = create_registry_accessor()

# Create key
create_code = accessor.create_registry_key("HKCU", "Software\\MyApp")

# Write version
version_code = accessor.write_registry_value(
    "HKCU", "Software\\MyApp", "Version", "1.0.0"
)

# Write build number
build_code = accessor.write_registry_dword(
    "HKCU", "Software\\MyApp", "Build", 1001
)
```

### Example 3: Complete Workflow

```python
from wmi_registry_access import create_registry_accessor

accessor = create_registry_accessor()

# 1. Create key
create_code = accessor.create_registry_key("HKCU", "Software\\TestApp")

# 2. Write values
write_str = accessor.write_registry_value("HKCU", "Software\\TestApp", "Name", "TestApp")
write_dw = accessor.write_registry_dword("HKCU", "Software\\TestApp", "Count", 100)

# 3. Read values
read_str = accessor.read_registry_value("HKCU", "Software\\TestApp", "Name")
read_dw = accessor.read_registry_dword("HKCU", "Software\\TestApp", "Count")

# 4. Enumerate values
enum_code = accessor.enum_registry_values("HKCU", "Software\\TestApp")

# 5. Delete key
delete_code = accessor.delete_registry_key("HKCU", "Software\\TestApp")
```

### Example 4: Obfuscated Operations

```python
from wmi_registry_access import RegistryConfig, create_registry_accessor

# Create with obfuscation
config = RegistryConfig(
    obfuscate_names=True,
    hide_errors=True
)
accessor = create_registry_accessor(config)

# Generate obfuscated VBS code
code = accessor.read_registry_value(
    "HKCU",
    "Software\\Settings",
    "Value"
)
# Variable names will be randomized
```

## VBS Output Format

All methods return VBS (VBScript) code as strings. Example output:

```vbs
On Error Resume Next
Dim objLoc_aBcDeFg, objSvc_XyZaBc, objMeth_qWeRtY, objIn_PoIuYt, objOut_LkJhGf, objRes_TyUiOp, objVal_MnBvCx

Set objLoc_aBcDeFg = CreateObject("WbemScripting.SWbemLocator")
Set objSvc_XyZaBc = objLoc_aBcDeFg.ConnectServer(".", "root\default")
Set objMeth_qWeRtY = objSvc_XyZaBc.Get("StdRegProv").Methods_("GetStringValue")
Set objIn_PoIuYt = objMeth_qWeRtY.InParameters.SpawnInstance_()

objIn_PoIuYt.hDefKey = 2147483650
objIn_PoIuYt.sSubKeyName = "SOFTWARE"
objIn_PoIuYt.sValueName = "TestValue"

Set objOut_LkJhGf = objSvc_XyZaBc.ExecMethod("StdRegProv", "GetStringValue", objIn_PoIuYt)

If objOut_LkJhGf.ReturnValue = 0 Then
    objVal_MnBvCx = objOut_LkJhGf.sValue
Else
    objVal_MnBvCx = ""
End If

Set objMeth_qWeRtY = Nothing
Set objIn_PoIuYt = Nothing
Set objOut_LkJhGf = Nothing
Set objSvc_XyZaBc = Nothing
Set objLoc_aBcDeFg = Nothing
On Error GoTo 0
```

## Configuration Options

### RegistryConfig

- **obfuscate_names** (bool, default=True): Randomize variable names for stealth
- **hide_errors** (bool, default=True): Add "On Error Resume Next" for silent operation
- **use_locator** (bool, default=True): Use SWbemLocator (always used currently)
- **encode_values** (bool, default=False): Encode values (future feature)

## Windows Management Instrumentation (WMI) Details

### StdRegProv Class

The module uses the `StdRegProv` class in `root\default` namespace:

```
WbemScripting.SWbemLocator
  |
  +-- ConnectServer(".", "root\default")
       |
       +-- StdRegProv Methods
            - GetStringValue
            - GetDWORDValue
            - GetBinaryValue
            - SetStringValue
            - SetDWORDValue
            - SetBinaryValue
            - DeleteValue
            - DeleteKey
            - CreateKey
            - EnumKey
            - EnumValues
```

### Return Value Codes

- 0: Success
- 1: Instance not found
- 2: Method call failed
- Other: System error codes

## Security and Stealth

### Features

1. **WbemScripting.SWbemLocator**: Executes through WMI COM interface
2. **StdRegProv**: Native Windows Management instrumentation provider
3. **Variable Obfuscation**: Random variable names make analysis harder
4. **Error Suppression**: Silent operation when configured
5. **No Direct Registry Access**: Works through WMI abstraction layer

### Advantages

- Avoids direct registry file modifications
- Uses legitimate Windows APIs
- Harder to detect than direct Registry modifications
- No admin rights required for HKCU operations
- Works on modern Windows with security restrictions

## Requirements

### System Requirements

- Windows XP or later
- Windows Management Instrumentation (WMI) enabled
- Administrative privileges (for HKLM operations)
- Standard user privileges (for HKCU operations)

### Python Requirements

- Python 3.6+
- No external dependencies

## Error Handling

### Default Behavior (hide_errors=True)

Operations fail silently with empty/zero returns:
- String values return ""
- DWORD values return 0
- Boolean operations return False

### Explicit Error Handling (hide_errors=False)

VBS code includes structured error handling:
- Errors are captured
- Return codes can be checked
- Debugging is easier

## Performance Considerations

- Each operation creates new WMI connection (standard practice)
- Connection overhead ~10-50ms per operation
- Suitable for batch operations
- For repeated operations, consider batching code

## Limitations

- Cannot read/write REG_QWORD (64-bit) directly
- Cannot read/write REG_MULTI_SZ (multi-string) directly
- Enumeration returns arrays (limited to available array size)
- Requires appropriate registry permissions

## Examples Directory

See `wmi_registry_examples.py` for 20 complete examples:

```bash
python wmi_registry_examples.py          # Run all examples
python wmi_registry_examples.py 1        # Run specific example
```

## Troubleshooting

### Issue: "Invalid registry key"
**Solution**: Check key path spelling, use full path like "SOFTWARE\\Microsoft"

### Issue: "Access denied"
**Solution**: Ensure appropriate user/admin permissions for the registry hive

### Issue: "Method not found"
**Solution**: Verify WMI is enabled and StdRegProv is accessible

### Issue: "Value not found"
**Solution**: Check value name spelling; empty string is returned on error

## Best Practices

1. Always specify full registry paths
2. Use appropriate hives (HKLM for system, HKCU for user)
3. Backup registry before automated modifications
4. Test code in safe environment first
5. Use proper escaping for special characters
6. Handle return codes in production code
7. Keep VBS files secure if sensitive operations

## References

- Windows Registry Structure: https://docs.microsoft.com/en-us/windows/win32/sysinfo/registry
- WMI StdRegProv: https://docs.microsoft.com/en-us/previous-versions/windows/desktop/regprov/stdregprov
- VBScript Documentation: https://docs.microsoft.com/en-us/previous-versions/t0aew7h6(v=vs.85)
- WbemScripting.SWbemLocator: https://docs.microsoft.com/en-us/windows/win32/wmisdk/swbemlocator

## File Locations

- **Module**: `/home/user/sc-generator/wmi_registry_access.py`
- **Examples**: `/home/user/sc-generator/wmi_registry_examples.py`
- **Guide**: `/home/user/sc-generator/WMI_REGISTRY_GUIDE.md`

## License & Usage

This module is provided as part of the sc-generator toolkit for authorized security research and testing purposes only.
