# Registry Storage API Reference

## VBSEncoder Class Methods

### `create_registry_storage_vbs()`

Write encoded payload to Windows Registry.

**Signature:**
```python
def create_registry_storage_vbs(
    self,
    payload: str,
    registry_hive: str = "HKCU",
    registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name: str = "SystemUpdate",
    encoding: str = "base64"
) -> str
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `payload` | str | Required | Command/payload to store |
| `registry_hive` | str | "HKCU" | "HKCU" or "HKLM" |
| `registry_path` | str | "Software\..." | Path within hive |
| `value_name` | str | "SystemUpdate" | Registry value name |
| `encoding` | str | "base64" | "base64" or "hex" |

**Returns:** VBS code string for registry write operation

**Raises:** None (errors handled in generated VBS)

**Example:**
```python
encoder = VBSEncoder()
vbs = encoder.create_registry_storage_vbs(
    payload="cmd.exe /c echo test",
    registry_hive="HKCU",
    registry_path="Software\\MyApp",
    value_name="Config"
)
```

**Generated Code Features:**
- Uses WScript.Shell COM object
- Encodes payload using specified method
- Supports REG_SZ registry type
- Includes error handling
- Returns None on error (silent failure)

---

### `create_registry_retrieval_and_execute_vbs()`

Read encoded payload from Registry and optionally execute it.

**Signature:**
```python
def create_registry_retrieval_and_execute_vbs(
    self,
    registry_hive: str = "HKCU",
    registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name: str = "SystemUpdate",
    encoding: str = "base64",
    auto_execute: bool = True
) -> str
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `registry_hive` | str | "HKCU" | "HKCU" or "HKLM" |
| `registry_path` | str | "Software\..." | Path within hive |
| `value_name` | str | "SystemUpdate" | Registry value name |
| `encoding` | str | "base64" | "base64" or "hex" |
| `auto_execute` | bool | True | Execute payload after retrieval |

**Returns:** VBS code string for registry read and optional execution

**Example:**
```python
vbs = encoder.create_registry_retrieval_and_execute_vbs(
    registry_hive="HKCU",
    registry_path="Software\\MyApp",
    value_name="Config",
    encoding="base64",
    auto_execute=True
)
```

**Generated Code Features:**
- Decodes payload based on encoding method
- Validates payload retrieval
- Optional WScript.Shell.Run execution
- Error handling with On Error Resume Next
- Cleans up COM objects

---

### `create_registry_persistence_payload()`

Create complete persistence payload with storage and retrieval.

**Signature:**
```python
def create_registry_persistence_payload(
    self,
    payload: str,
    registry_hive: str = "HKCU",
    registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name: str = "SystemUpdate",
    encoding: str = "base64"
) -> str
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `payload` | str | Required | Command to store and execute |
| `registry_hive` | str | "HKCU" | "HKCU" or "HKLM" |
| `registry_path` | str | "Software\..." | Path within hive |
| `value_name` | str | "SystemUpdate" | Registry value name |
| `encoding` | str | "base64" | "base64" or "hex" |

**Returns:** Combined VBS code for storage and retrieval

**Example:**
```python
vbs = encoder.create_registry_persistence_payload(
    payload="powershell.exe -Command 'Get-Process'",
    registry_hive="HKCU",
    registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name="WindowsUpdate"
)
```

**Generated Code Includes:**
1. Storage section - writes payload to registry
2. Retrieval section - reads and executes payload
3. System Maintenance Script header
4. Error handling throughout

---

## Module-Level Functions

### `write_payload_to_registry()`

Wrapper function for quick registry payload storage.

**Signature:**
```python
def write_payload_to_registry(
    payload: str,
    registry_hive: str = "HKCU",
    registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name: str = "SystemUpdate",
    encoding: str = "base64",
    retrieve_and_execute: bool = False
) -> str
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `payload` | str | Required | Payload to store |
| `registry_hive` | str | "HKCU" | "HKCU" or "HKLM" |
| `registry_path` | str | "Software\..." | Registry path |
| `value_name` | str | "SystemUpdate" | Value name |
| `encoding` | str | "base64" | "base64" or "hex" |
| `retrieve_and_execute` | bool | False | Include retrieval code |

**Returns:** VBS code for registry storage

**Example:**
```python
from vbs_encoder import write_payload_to_registry

# Storage only
vbs = write_payload_to_registry(
    payload="test.exe",
    registry_hive="HKCU"
)

# Storage with retrieval
vbs = write_payload_to_registry(
    payload="test.exe",
    registry_hive="HKCU",
    retrieve_and_execute=True
)
```

---

### `create_registry_retriever()`

Wrapper function for quick registry payload retrieval.

**Signature:**
```python
def create_registry_retriever(
    registry_hive: str = "HKCU",
    registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name: str = "SystemUpdate",
    encoding: str = "base64",
    auto_execute: bool = True
) -> str
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `registry_hive` | str | "HKCU" | "HKCU" or "HKLM" |
| `registry_path` | str | "Software\..." | Registry path |
| `value_name` | str | "SystemUpdate" | Value name |
| `encoding` | str | "base64" | "base64" or "hex" |
| `auto_execute` | bool | True | Execute retrieved payload |

**Returns:** VBS code for registry retrieval

**Example:**
```python
from vbs_encoder import create_registry_retriever

# Read and execute
vbs = create_registry_retriever(
    registry_hive="HKCU",
    value_name="MyPayload",
    auto_execute=True
)

# Read only
vbs = create_registry_retriever(
    registry_hive="HKCU",
    value_name="MyPayload",
    auto_execute=False
)
```

---

### `validate_registry_path()`

Validate registry path format.

**Signature:**
```python
def validate_registry_path(registry_path: str) -> bool
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `registry_path` | str | Path to validate |

**Returns:** True if valid, False otherwise

**Validation Rules:**
- Must not be empty
- Must be string type
- Must use backslash (\) as separator (not forward slash)
- Maximum length: reasonable for registry path

**Example:**
```python
from vbs_encoder import validate_registry_path

# Valid paths
validate_registry_path("Software\\Test")  # True
validate_registry_path("Software\\Microsoft\\Windows\\CurrentVersion\\Run")  # True

# Invalid paths
validate_registry_path("Software/Test")  # False - forward slash
validate_registry_path("")  # False - empty
validate_registry_path(None)  # False - not string
```

---

### `validate_registry_hive()`

Validate registry hive name.

**Signature:**
```python
def validate_registry_hive(registry_hive: str) -> bool
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `registry_hive` | str | Hive name to validate |

**Returns:** True if valid, False otherwise

**Supported Values:**
- "HKCU" (case-insensitive)
- "HKLM" (case-insensitive)
- "HKEY_CURRENT_USER"
- "HKEY_LOCAL_MACHINE"

**Example:**
```python
from vbs_encoder import validate_registry_hive

# Valid hives
validate_registry_hive("HKCU")  # True
validate_registry_hive("HKLM")  # True
validate_registry_hive("hkcu")  # True - case insensitive
validate_registry_hive("HKEY_CURRENT_USER")  # True

# Invalid hives
validate_registry_hive("HKCC")  # False
validate_registry_hive("HKEY_USERS")  # False
validate_registry_hive("")  # False
```

---

## Data Types

### Registry Hives
```python
type RegistryHive = Literal["HKCU", "HKLM", "HKEY_CURRENT_USER", "HKEY_LOCAL_MACHINE"]
```

### Encoding Methods
```python
type EncodingMethod = Literal["base64", "hex"]
```

### Registry Value Types (Supported)
```python
type RegistryValueType = Literal["REG_SZ"]  # Currently supported
```

---

## Error Handling

All functions gracefully handle errors through generated VBS code:

```vbs
On Error Resume Next
[operation]
On Error GoTo 0
```

### Common Errors (Handled Silently)
- Registry path doesn't exist
- Insufficient permissions
- Invalid registry format
- Corrupted registry data

### Validation Errors (Raised by Python Functions)
- None raised (validation functions return boolean)
- Errors in generation caught during encoding

---

## Encoding Specifications

### Base64 Encoding
**Uses:** MSXML2.DOMDocument
**Overhead:** ~33% size increase
**Decoder:**
```vbs
Function Decode(encoded)
    Dim xmlDoc
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    xmlDoc.LoadXML "<root><![CDATA[" & encoded & "]]></root>"
    Decode = xmlDoc.DocumentElement.text
    Set xmlDoc = Nothing
End Function
```

### Hex Encoding
**Uses:** Chr(CLng("&H...")) conversion
**Overhead:** ~100% size increase
**Decoder:**
```vbs
Function DecodeHex(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    DecodeHex = r
End Function
```

---

## Registry Operations

### RegWrite (Storage)
**Syntax:**
```vbs
WScript.Shell.RegWrite path, value, type
```

**Parameters:**
- path: "HKEY_CURRENT_USER\Software\Test\Value"
- value: Encoded payload string
- type: "REG_SZ" (always)

### RegRead (Retrieval)
**Syntax:**
```vbs
value = WScript.Shell.RegRead(path)
```

**Parameters:**
- path: Registry path with value name

**Returns:**
- Encoded payload string if found
- Empty string if not found

---

## Example Workflow

```python
from vbs_encoder import VBSEncoder, write_payload_to_registry

# Initialize encoder
encoder = VBSEncoder()

# Step 1: Create storage code
storage_code = write_payload_to_registry(
    payload="calc.exe",
    registry_hive="HKCU",
    registry_path="Software\\Test",
    value_name="MyKey",
    encoding="base64"
)

# Step 2: Save to file
with open("store.vbs", "w") as f:
    f.write(storage_code)

# Step 3: Create retrieval code
retrieval_code = encoder.create_registry_retrieval_and_execute_vbs(
    registry_hive="HKCU",
    registry_path="Software\\Test",
    value_name="MyKey",
    auto_execute=True
)

# Step 4: Save retrieval to file
with open("retrieve.vbs", "w") as f:
    f.write(retrieval_code)
```

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| `create_registry_storage_vbs()` | < 1ms | Fast encoding/generation |
| `create_registry_retrieval_and_execute_vbs()` | < 1ms | Includes decoding logic |
| `create_registry_persistence_payload()` | < 2ms | Combined operations |
| `validate_registry_path()` | < 0.1ms | Simple string validation |
| `validate_registry_hive()` | < 0.1ms | List lookup |

---

## Compatibility

### Operating Systems
- Windows XP and later
- Windows Server 2003 and later
- Windows 7, 8, 10, 11
- Windows Server 2008 and later

### Requirements
- WScript.Shell COM object
- MSXML2.DOMDocument (for base64 decoding)
- Windows Registry access

### Not Required
- Administrator privileges (for HKCU)
- Additional software or libraries
- Network connectivity

---

## Caching Behavior

The VBSEncoder class caches encoded values:

```python
encoder = VBSEncoder()
# First call: encodes and caches
vbs1 = encoder.encode_string_base64("test")
# Second call: uses cached value
vbs2 = encoder.encode_string_base64("test")
```

This improves performance for repeated encodings of the same payload.

---

## References

- [WScript.Shell Documentation](https://learn.microsoft.com/en-us/previous-versions/t8b6bz5t(v=vs.85))
- [Windows Registry](https://learn.microsoft.com/en-us/windows/win32/sysinfo/structure-of-the-registry)
- [MSXML2.DOMDocument](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ms763742(v=vs.85))
