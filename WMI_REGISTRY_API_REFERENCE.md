# WMI Registry Access - Complete API Reference

## Module Overview

**File**: `wmi_registry_access.py`
**Classes**: `WMIRegistryAccess`, `RegistryConfig`
**Functions**: `create_registry_accessor()`, `read_registry()`, `write_registry()`
**Dependencies**: Python 3.6+ (no external packages)

---

## Class: `RegistryConfig`

Configuration dataclass for registry access operations.

### Properties

```python
@dataclass
class RegistryConfig:
    obfuscate_names: bool = True      # Randomize variable names
    hide_errors: bool = True          # Suppress error messages
    use_locator: bool = True          # Use SWbemLocator
    encode_values: bool = False       # Encode values (future)
```

### Example

```python
config = RegistryConfig(
    obfuscate_names=True,
    hide_errors=True,
    use_locator=True
)
```

---

## Class: `WMIRegistryAccess`

Main class providing all registry operations through WMI StdRegProv.

### Constructor

```python
def __init__(self, config: Optional[RegistryConfig] = None)
```

### Registry Hive Constants

```python
HKEY_LOCAL_MACHINE = 0x80000002     # HKLM
HKEY_CURRENT_USER = 0x80000001     # HKCU
HKEY_CLASSES_ROOT = 0x80000000     # HKCR
HKEY_USERS = 0x80000003            # HKU
HKEY_CURRENT_CONFIG = 0x80000005   # HKCC
```

### Registry Value Type Constants

```python
REG_SZ = 1                  # String
REG_EXPAND_SZ = 2          # Expandable string
REG_BINARY = 3             # Binary
REG_DWORD = 4              # DWORD (32-bit)
REG_DWORD_BIG_ENDIAN = 5   # Big-endian DWORD
REG_LINK = 6               # Symbolic link
REG_MULTI_SZ = 7           # Multi-string
REG_QWORD = 11             # QWORD (64-bit)
```

---

## Public Methods

### Read Operations

#### `read_registry_value(hive, key_path, value_name)`

Reads string value from registry via WMI StdRegProv.GetStringValue.

**Parameters**:
- `hive` (str): Registry hive ("HKLM", "HKCU", "HKCR", "HKU", "HKCC")
- `key_path` (str): Full registry path (e.g., "SOFTWARE\\Microsoft\\Windows")
- `value_name` (str): Name of the value to read

**Returns**: (str) VBS code string

**Example**:
```python
accessor = create_registry_accessor()
code = accessor.read_registry_value(
    "HKLM",
    "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
    "CurrentVersion"
)
```

**VBS Method Used**: `StdRegProv.GetStringValue`
- **Input Parameters**: `hDefKey`, `sSubKeyName`, `sValueName`
- **Output Parameters**: `sValue` (on success), `ReturnValue`

---

#### `read_registry_dword(hive, key_path, value_name)`

Reads DWORD (32-bit integer) value from registry via WMI StdRegProv.GetDWORDValue.

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path
- `value_name` (str): Name of the DWORD value

**Returns**: (str) VBS code string

**Example**:
```python
code = accessor.read_registry_dword(
    "HKCU",
    "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer",
    "NoViewOnDrive"
)
```

**VBS Method Used**: `StdRegProv.GetDWORDValue`
- **Input Parameters**: `hDefKey`, `sSubKeyName`, `sValueName`
- **Output Parameters**: `uValue` (on success), `ReturnValue`

---

#### `read_registry_binary(hive, key_path, value_name)`

Reads binary value from registry via WMI StdRegProv.GetBinaryValue and converts to hex string.

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path
- `value_name` (str): Name of the binary value

**Returns**: (str) VBS code string (result in hex format)

**Example**:
```python
code = accessor.read_registry_binary(
    "HKCU",
    "Software\\Settings",
    "BinaryData"
)
```

**VBS Method Used**: `StdRegProv.GetBinaryValue`
- **Input Parameters**: `hDefKey`, `sSubKeyName`, `sValueName`
- **Output Parameters**: `uValue` (byte array, converted to hex), `ReturnValue`

---

### Write Operations

#### `write_registry_value(hive, key_path, value_name, value_data, value_type="REG_SZ")`

Writes string value to registry via WMI StdRegProv.SetStringValue.

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path
- `value_name` (str): Name of the value to write
- `value_data` (str): String data to write (quotes are escaped)
- `value_type` (str): Type (default: "REG_SZ")

**Returns**: (str) VBS code string

**Example**:
```python
code = accessor.write_registry_value(
    "HKCU",
    "Software\\MyApp",
    "AppName",
    "My Application"
)
```

**VBS Method Used**: `StdRegProv.SetStringValue`
- **Input Parameters**: `hDefKey`, `sSubKeyName`, `sValueName`, `sValue`
- **Output Parameters**: `ReturnValue`

**Note**: Automatically escapes quotes in value data.

---

#### `write_registry_dword(hive, key_path, value_name, value_data)`

Writes DWORD (32-bit integer) value to registry via WMI StdRegProv.SetDWORDValue.

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path
- `value_name` (str): Name of the DWORD value
- `value_data` (int): DWORD value (0-4294967295)

**Returns**: (str) VBS code string

**Example**:
```python
code = accessor.write_registry_dword(
    "HKCU",
    "Software\\MyApp\\Settings",
    "Timeout",
    30000
)
```

**VBS Method Used**: `StdRegProv.SetDWORDValue`
- **Input Parameters**: `hDefKey`, `sSubKeyName`, `sValueName`, `uValue`
- **Output Parameters**: `ReturnValue`

---

#### `write_registry_binary(hive, key_path, value_name, hex_data)`

Writes binary value to registry via WMI StdRegProv.SetBinaryValue. Converts hex string to byte array.

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path
- `value_name` (str): Name of the binary value
- `hex_data` (str): Hex string (e.g., "48656C6C6F" for "Hello")

**Returns**: (str) VBS code string

**Example**:
```python
code = accessor.write_registry_binary(
    "HKCU",
    "Software\\MyApp",
    "BinaryData",
    "48656C6C6F"  # "Hello" in hex
)
```

**VBS Method Used**: `StdRegProv.SetBinaryValue`
- **Input Parameters**: `hDefKey`, `sSubKeyName`, `sValueName`, `uValue` (byte array)
- **Output Parameters**: `ReturnValue`

**Note**: Automatically converts hex string to byte array. Each pair of hex characters becomes one byte.

---

### Deletion Operations

#### `delete_registry_value(hive, key_path, value_name)`

Deletes registry value via WMI StdRegProv.DeleteValue.

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path
- `value_name` (str): Name of the value to delete

**Returns**: (str) VBS code string

**Example**:
```python
code = accessor.delete_registry_value(
    "HKCU",
    "Software\\MyApp",
    "TestValue"
)
```

**VBS Method Used**: `StdRegProv.DeleteValue`
- **Input Parameters**: `hDefKey`, `sSubKeyName`, `sValueName`
- **Output Parameters**: `ReturnValue`

---

#### `delete_registry_key(hive, key_path)`

Deletes registry key via WMI StdRegProv.DeleteKey.

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path to delete

**Returns**: (str) VBS code string

**Example**:
```python
code = accessor.delete_registry_key(
    "HKCU",
    "Software\\MyApp\\SubKey"
)
```

**VBS Method Used**: `StdRegProv.DeleteKey`
- **Input Parameters**: `hDefKey`, `sSubKeyName`
- **Output Parameters**: `ReturnValue`

---

### Enumeration Operations

#### `enum_registry_keys(hive, key_path)`

Enumerates subkeys in a registry key via WMI StdRegProv.EnumKey.

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path

**Returns**: (str) VBS code string

**Example**:
```python
code = accessor.enum_registry_keys(
    "HKLM",
    "SOFTWARE\\Microsoft"
)
```

**VBS Method Used**: `StdRegProv.EnumKey`
- **Input Parameters**: `hDefKey`, `sSubKeyName`
- **Output Parameters**: `sNames` (array of subkey names), `ReturnValue`

**Output Format**: Returns array of subkey names in `sNames` variable.

---

#### `enum_registry_values(hive, key_path)`

Enumerates values in a registry key via WMI StdRegProv.EnumValues.

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path

**Returns**: (str) VBS code string

**Example**:
```python
code = accessor.enum_registry_values(
    "HKLM",
    "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion"
)
```

**VBS Method Used**: `StdRegProv.EnumValues`
- **Input Parameters**: `hDefKey`, `sSubKeyName`
- **Output Parameters**: `sNames` (value names array), `Types` (value types array), `ReturnValue`

**Output Format**: Returns:
- `sNames`: Array of value names
- `Types`: Array of value types (REG_SZ, REG_DWORD, etc.)

---

### Management Operations

#### `create_registry_key(hive, key_path)`

Creates registry key via WMI StdRegProv.CreateKey.

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path to create

**Returns**: (str) VBS code string

**Example**:
```python
code = accessor.create_registry_key(
    "HKCU",
    "Software\\MyApp\\SubKey"
)
```

**VBS Method Used**: `StdRegProv.CreateKey`
- **Input Parameters**: `hDefKey`, `sSubKeyName`
- **Output Parameters**: `ReturnValue`

---

#### `check_registry_key_exists(hive, key_path)`

Checks if registry key exists via WMI StdRegProv.GetStringValue (method exists check).

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path

**Returns**: (str) VBS code string

**Example**:
```python
code = accessor.check_registry_key_exists(
    "HKLM",
    "SOFTWARE\\Microsoft\\Windows"
)
```

**Output**: Returns boolean value in `keyExists` variable (True/False).

---

### Reporting

#### `get_registry_methods_report()`

Generates report of all available registry access methods with examples.

**Parameters**: None

**Returns**: (dict) Dictionary with method keys and info:
```python
{
    "read_value": {
        "name": "Read String Value",
        "description": "Read string value from registry",
        "code": "... VBS code ..."
    },
    "read_dword": {...},
    # ... etc ...
}
```

**Example**:
```python
report = accessor.get_registry_methods_report()
for key, info in report.items():
    print(f"{info['name']}: {info['description']}")
```

---

## Factory Function

### `create_registry_accessor(config: Optional[RegistryConfig] = None)`

Creates WMIRegistryAccess instance with optional configuration.

**Parameters**:
- `config` (RegistryConfig, optional): Configuration object. Defaults to standard config if None.

**Returns**: (WMIRegistryAccess) Configured accessor instance

**Example**:
```python
# Default config
accessor = create_registry_accessor()

# Custom config
config = RegistryConfig(obfuscate_names=False)
accessor = create_registry_accessor(config)
```

---

## High-Level Convenience Functions

### `read_registry(hive, key_path, value_name, value_type="string")`

High-level function to read registry value with type detection.

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path
- `value_name` (str): Name of value to read
- `value_type` (str): Type of value - "string", "dword", or "binary" (default: "string")

**Returns**: (str) VBS code string

**Example**:
```python
from wmi_registry_access import read_registry

# Read string
code = read_registry("HKLM", "SOFTWARE", "TestValue", "string")

# Read DWORD
code = read_registry("HKCU", "SOFTWARE", "TestDWORD", "dword")

# Read binary
code = read_registry("HKCU", "SOFTWARE", "TestBinary", "binary")
```

---

### `write_registry(hive, key_path, value_name, value_data, value_type="string")`

High-level function to write registry value with type conversion.

**Parameters**:
- `hive` (str): Registry hive
- `key_path` (str): Full registry path
- `value_name` (str): Name of value to write
- `value_data` (str): Data to write (type depends on value_type)
- `value_type` (str): Type of value - "string", "dword", or "binary" (default: "string")

**Returns**: (str) VBS code string

**Example**:
```python
from wmi_registry_access import write_registry

# Write string
code = write_registry("HKCU", "SOFTWARE\\MyApp", "AppName", "MyApp")

# Write DWORD (value_data is converted to int)
code = write_registry("HKCU", "SOFTWARE\\MyApp", "Counter", "1000", "dword")

# Write binary (value_data should be hex string)
code = write_registry("HKCU", "SOFTWARE\\MyApp", "BinData", "DEADBEEF", "binary")
```

---

## Return Values

### VBS Output Format

All methods return VBScript code as strings. Example:

```vbs
On Error Resume Next

Dim regLoc_AbCdEfGh, regSvc_IjKlMnOp, regMeth_QrStUvWx, regIn_YzAbCdEf, regOut_GhIjKlMn, regRes_OpQrStUv, regVal_WxYzAbCd

Set regLoc_AbCdEfGh = CreateObject("WbemScripting.SWbemLocator")
Set regSvc_IjKlMnOp = regLoc_AbCdEfGh.ConnectServer(".", "root\default")
Set regMeth_QrStUvWx = regSvc_IjKlMnOp.Get("StdRegProv").Methods_("GetStringValue")
Set regIn_YzAbCdEf = regMeth_QrStUvWx.InParameters.SpawnInstance_()

regIn_YzAbCdEf.hDefKey = 2147483650
regIn_YzAbCdEf.sSubKeyName = "SOFTWARE"
regIn_YzAbCdEf.sValueName = "TestValue"

Set regOut_GhIjKlMn = regSvc_IjKlMnOp.ExecMethod("StdRegProv", "GetStringValue", regIn_YzAbCdEf)

If regOut_GhIjKlMn.ReturnValue = 0 Then
    regVal_WxYzAbCd = regOut_GhIjKlMn.sValue
Else
    regVal_WxYzAbCd = ""
End If

Set regMeth_QrStUvWx = Nothing
Set regIn_YzAbCdEf = Nothing
Set regOut_GhIjKlMn = Nothing
Set regSvc_IjKlMnOp = Nothing
Set regLoc_AbCdEfGh = Nothing

On Error GoTo 0
```

### StdRegProv Return Codes

- `0`: Success
- `1`: Instance not found
- `2`: Method call failed  
- `3`: Access denied
- Other: System error code

---

## Private Methods

### `_generate_random_name(prefix: str = "v")`

Generates random variable name for obfuscation.

**Parameters**:
- `prefix` (str): Variable name prefix (default: "v")

**Returns**: (str) Random variable name like "v_AbCdEfGh"

---

### `_get_or_create_var(key: str, prefix: str = "v")`

Gets cached variable name or creates new one for consistency.

**Parameters**:
- `key` (str): Cache key for variable
- `prefix` (str): Variable name prefix

**Returns**: (str) Variable name

---

### `_get_hive_constant(hive: str)`

Maps hive abbreviation to registry constant value.

**Parameters**:
- `hive` (str): Hive abbreviation ("HKLM", "HKCU", etc.)

**Returns**: (int) Registry hive constant

---

## Usage Patterns

### Pattern 1: Simple Read

```python
from wmi_registry_access import create_registry_accessor

accessor = create_registry_accessor()
code = accessor.read_registry_value("HKLM", "SOFTWARE", "Value")
# Save to .vbs file and execute
```

### Pattern 2: Simple Write

```python
code = accessor.write_registry_value("HKCU", "SOFTWARE\\MyApp", "Setting", "Value")
# Save to .vbs file and execute
```

### Pattern 3: Workflow

```python
steps = []
steps.append(accessor.create_registry_key("HKCU", "SOFTWARE\\MyApp"))
steps.append(accessor.write_registry_value("HKCU", "SOFTWARE\\MyApp", "Name", "MyApp"))
steps.append(accessor.write_registry_dword("HKCU", "SOFTWARE\\MyApp", "Count", 100))
steps.append(accessor.read_registry_value("HKCU", "SOFTWARE\\MyApp", "Name"))
steps.append(accessor.delete_registry_key("HKCU", "SOFTWARE\\MyApp"))

# Combine all steps
combined_code = "\n\n".join(steps)
```

### Pattern 4: Batch Operations

```python
config = RegistryConfig(obfuscate_names=True)
accessor = create_registry_accessor(config)

operations = [
    ("read_version", "HKLM", "SOFTWARE", "CurrentVersion"),
    ("read_build", "HKLM", "SOFTWARE", "BuildNumber"),
    ("write_setting", "HKCU", "SOFTWARE", "MySetting"),
]

for op_type, hive, path, *args in operations:
    if op_type == "read_version":
        code = accessor.read_registry_value(hive, path, args[0])
    elif op_type == "write_setting":
        code = accessor.write_registry_value(hive, path, args[0], args[1])
    # ... execute code
```

---

## Error Handling

### Configuration for Error Handling

```python
# Silent mode (no errors shown)
config = RegistryConfig(hide_errors=True)

# Explicit error mode
config = RegistryConfig(hide_errors=False)

accessor = create_registry_accessor(config)
```

### Checking for Errors in VBS

```vbs
' Code returns ReturnValue = 0 for success
If outParams.ReturnValue = 0 Then
    ' Success
Else
    ' Error occurred
    WScript.Echo "Error: " & outParams.ReturnValue
End If
```

---

## Performance Characteristics

- **Code Generation**: <1ms per operation
- **VBS Execution**: 10-50ms per operation (WMI overhead)
- **Recommended Usage**: Batch operations to reduce overhead
- **Scalability**: Suitable for 1-1000 operations per script

---

## Compatibility

### System Requirements
- Windows XP or later
- WMI enabled
- StdRegProv provider available

### Python Requirements
- Python 3.6+
- No external packages

---

## File Location

- **Module**: `wmi_registry_access.py`
- **Examples**: `wmi_registry_examples.py`
- **Full Guide**: `WMI_REGISTRY_GUIDE.md`

---

## See Also

- `wmi_executor.py` - Process execution via WMI
- `wmi_executor_examples.py` - Execution examples
- `wmi_registry_examples.py` - Registry access examples
