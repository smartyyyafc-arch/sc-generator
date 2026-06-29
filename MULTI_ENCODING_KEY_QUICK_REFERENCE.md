# Multi-Encoding Key Derivation - Quick Reference

## Installation & Setup

```python
from multi_encoding_key_derivation import (
    MultiEncodingKeySystem,
    KeyDerivationMethod,
    EncodingStrategy
)

# Initialize system
system = MultiEncodingKeySystem()
```

## Creating Target Profiles

### Basic Profile
```python
profile = system.create_target_profile(
    name='My Target',
    fingerprint_data={
        'hostname': 'server-01',
        'os': 'Linux',
        'version': '5.10'
    }
)
```

### With Custom Configuration
```python
profile = system.create_target_profile(
    name='Secure Target',
    fingerprint_data={...},
    encoding_strategy=EncodingStrategy.HEX,
    key_derivation_method=KeyDerivationMethod.ARGON2,
    salt='custom_salt',
    iterations=200000,
    key_length=32
)
```

## Key Derivation Methods

### PBKDF2 (Recommended Default)
```python
key_derivation_method=KeyDerivationMethod.PBKDF2
# Standard, industry-tested, configurable iterations
```

### HKDF (Fast & Secure)
```python
key_derivation_method=KeyDerivationMethod.HKDF
# RFC 5869, excellent entropy extraction
```

### Argon2 (Modern, Memory-Hard)
```python
key_derivation_method=KeyDerivationMethod.ARGON2
# Resistant to GPU/ASIC attacks, memory-hard
```

### Scrypt (Very Secure)
```python
key_derivation_method=KeyDerivationMethod.SCRYPT
# Sequential memory-hard, high security margin
```

### Bcrypt (Battle-Tested)
```python
key_derivation_method=KeyDerivationMethod.BCRYPT
# Password hashing standard, adaptive cost
```

### SHA256-Chain (Fast)
```python
key_derivation_method=KeyDerivationMethod.SHA256_CHAIN
# Quick derivation, lightweight
```

### HMAC-Chain (Balanced)
```python
key_derivation_method=KeyDerivationMethod.HMAC_CHAIN
# Security + performance balance
```

## Encoding Strategies

### HEX
```python
encoding_strategy=EncodingStrategy.HEX
# "Hello" -> "48656c6c6f"
```

### BASE64
```python
encoding_strategy=EncodingStrategy.BASE64
# "Hello" -> "SGVsbG8="
```

### ROT13
```python
encoding_strategy=EncodingStrategy.ROT13
# "Hello" -> "Uryyb"
```

### XOR (Key-Based)
```python
encoding_strategy=EncodingStrategy.XOR
# Uses key material for cipher (0-255)
```

### OCTAL
```python
encoding_strategy=EncodingStrategy.OCTAL
# "A" (65) -> "101"
```

### ASCII
```python
encoding_strategy=EncodingStrategy.ASCII
# "ABC" -> "65,66,67"
```

### REVERSE
```python
encoding_strategy=EncodingStrategy.REVERSE
# "Hello" -> "olleH"
```

### CUSTOM_SUBSTITUTION
```python
encoding_strategy=EncodingStrategy.CUSTOM_SUBSTITUTION
# Per-target substitution table from key
```

## Deriving Keys

### Basic Key Derivation
```python
derived_key = system.derive_key_for_target(profile.target_id)
print(derived_key.hex_key)  # 64-char hex string
```

### With Custom Salt
```python
derived_key = system.derive_key_for_target(
    profile.target_id,
    custom_salt='unique_salt'
)
```

## Getting Encoding Parameters

```python
params = system.get_encoding_parameters(profile.target_id)
# Returns dict with strategy-specific parameters

# For XOR: {'key': 42}
# For ROT13: {'rotation': 5}
# For Custom: {'substitution_table': {...}}
```

## Exporting Configuration

```python
config = system.export_key_config(profile.target_id)

# Returns:
# {
#   'target': {...},
#   'key': {...},
#   'encoding': {...},
#   'metadata': {...}
# }

# Save to JSON
import json
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)
```

## Fingerprint Integration

```python
from fingerprint_key_integration import FingerprintKeyIntegration

integration = FingerprintKeyIntegration()

# Register fingerprint with encoding
fp_id, target_id = integration.register_fingerprint_with_encoding(
    fingerprint_id='fp_existing',
    target_name='Encoded Target'
)

# Encode payload
encoded = integration.encode_payload_for_target(
    target_id=target_id,
    payload='secret_data'
)

# Decode payload
decoded = integration.decode_payload_for_target(
    target_id=target_id,
    encoded_payload=encoded.encoded
)
```

## Listing & Managing Profiles

```python
# List all profiles
profiles = system.list_target_profiles()

# Get profile details
details = system.get_fingerprint_details(fingerprint_id)

# Generate system report
report = system.generate_system_report()
print(report)
```

## Common Patterns

### Create Multiple Targets
```python
targets = []
systems = [
    {'name': 'Web', 'os': 'Linux', 'version': '5.10'},
    {'name': 'DB', 'os': 'Linux', 'version': '5.15'},
    {'name': 'Cache', 'os': 'Linux', 'version': '5.12'}
]

for sys_data in systems:
    profile = system.create_target_profile(
        name=sys_data['name'],
        fingerprint_data=sys_data
    )
    targets.append(profile)
```

### Compare Key Derivation Methods
```python
fingerprint = {'system': 'test', 'id': '001'}

for method in [KeyDerivationMethod.PBKDF2, 
               KeyDerivationMethod.ARGON2,
               KeyDerivationMethod.SCRYPT]:
    profile = system.create_target_profile(
        name=f"Method: {method.value}",
        fingerprint_data=fingerprint,
        key_derivation_method=method
    )
    key = system.derive_key_for_target(profile.target_id)
    print(f"{method.value}: {key.hex_key[:16]}...")
```

### Batch Encoding
```python
def encode_batch(target_id, payloads):
    results = []
    for payload in payloads:
        encoded = integration.encode_payload_for_target(
            target_id=target_id,
            payload=payload
        )
        results.append({
            'original': payload,
            'encoded': encoded.encoded,
            'strategy': encoded.encoding_strategy
        })
    return results

payloads = ['cmd1', 'cmd2', 'cmd3']
results = encode_batch(target_id, payloads)
```

## Configuration Files

```
~/.sc-generator/encoding-keys/
├── target_profiles.json          # Target definitions
├── fingerprint_mappings.json    # Fingerprint links
└── derived_keys/                 # Cached derived keys (optional)
```

## Troubleshooting

### "Target not found"
```python
# Ensure target exists
if target_id not in system.target_profiles:
    # Create it first
    profile = system.create_target_profile(...)
```

### Import errors
```bash
# Ensure dependencies installed
pip3 install cryptography argon2-cffi bcrypt
```

### JSON serialization issues
```python
# Keys automatically converted to hex in export
config = system.export_key_config(target_id)
json_str = json.dumps(config)  # Works automatically
```

## Performance Tips

- Use HKDF for fast key derivation
- Use PBKDF2 for balanced security/speed
- Use Argon2 for high-security scenarios
- Cache derived keys with `system.derived_keys`
- Reuse profiles for multiple payloads

## Security Checklist

- ✓ Use unique salt per target (or auto-generated)
- ✓ Configure iterations appropriately (100k minimum)
- ✓ Store configurations securely
- ✓ Validate fingerprint data integrity
- ✓ Use memory-hard methods when possible
- ✓ Audit key derivation parameters
- ✓ Backup target profiles safely

## API Summary

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| MultiEncodingKeySystem | Main system | create_target_profile(), derive_key_for_target(), export_key_config() |
| FingerprintHasher | Fingerprint hashing | hash_fingerprint(), hash_with_weights() |
| KeyDerivationFactory | Key generation | derive_pbkdf2(), derive_hkdf(), derive_key() |
| EncodingStrategySelector | Strategy selection | select_strategy_from_fingerprint() |
| FingerprintKeyIntegration | Integration | register_fingerprint_with_encoding() |

## Examples Repository

See these files for complete examples:
- `multi_encoding_key_derivation.py` - Demonstrations at end of file
- `fingerprint_key_integration.py` - Integration examples
- `test_multi_encoding_key_derivation.py` - Test cases
- `MULTI_ENCODING_KEY_DERIVATION_GUIDE.md` - Detailed guide

## For More Information

Read: `MULTI_ENCODING_KEY_DERIVATION_GUIDE.md`
Tests: `test_multi_encoding_key_derivation.py`
Summary: `MULTI_ENCODING_KEY_SYSTEM_SUMMARY.txt`
