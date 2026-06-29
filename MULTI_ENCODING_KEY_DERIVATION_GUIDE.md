# Multi-Encoding Key Derivation System

## Overview

The Multi-Encoding Key Derivation System provides cryptographic key generation from system fingerprints with unique encoding strategies per target. This system enables:

- **Deterministic key derivation** from system characteristics
- **Multiple key derivation methods** (PBKDF2, HKDF, SHA256-Chain, HMAC-Chain, Argon2, Bcrypt, Scrypt)
- **Per-target encoding strategies** (HEX, Base64, ROT13, XOR, Octal, ASCII, Reverse, Custom Substitution)
- **Integration with fingerprint management** system
- **Secure, reproducible key generation** for authorized pentesting

## Architecture

### Core Components

#### 1. FingerprintHasher
Generates deterministic hashes from fingerprint data with multiple methods:
- SHA256 (default)
- SHA512
- MD5
- Weighted hashing based on component importance

```python
from multi_encoding_key_derivation import FingerprintHasher

hasher = FingerprintHasher()

fingerprint = {
    'hostname': 'SERVER-001',
    'os': 'Windows Server 2019',
    'processor': 'Intel i7'
}

# Generate deterministic hash
hash_val = hasher.hash_fingerprint(fingerprint)
# Output: "08ea27467dffd8525c840ce603a87a2c408a025577736b9e15e60ec17234d515"

# Generate weighted hash
weights = {'hostname': 3, 'os': 2, 'processor': 1}
weighted_hash = hasher.hash_with_weights(fingerprint, weights)

# Extract components from hash
components = hasher.extract_components(hash_val, 4)
```

#### 2. KeyDerivationFactory
Implements multiple key derivation methods:

**PBKDF2** (Password-Based Key Derivation Function 2)
- Industry standard
- Configurable iterations (default: 100,000)
- HMAC-SHA256 based

```python
key = KeyDerivationFactory.derive_pbkdf2(
    fingerprint_data,
    salt='unique_salt',
    iterations=100000,
    key_length=32
)
```

**HKDF** (HMAC-based Key Derivation Function)
- RFC 5869 standard
- Extract-expand model
- Better for key material with high entropy

```python
key = KeyDerivationFactory.derive_hkdf(
    fingerprint_data,
    salt='unique_salt',
    info='multi-encoding-key',
    key_length=32
)
```

**SHA256-Chain**
- Chained SHA256 operations
- Deterministic
- Fast, suitable for high-performance scenarios

```python
key = KeyDerivationFactory.derive_sha256_chain(
    fingerprint_data,
    salt='unique_salt',
    iterations=100000,
    key_length=32
)
```

**HMAC-Chain**
- Chained HMAC-SHA256 operations
- Combines HMAC with iteration
- Resistant to rainbow tables

```python
key = KeyDerivationFactory.derive_hmac_chain(
    fingerprint_data,
    salt='unique_salt',
    iterations=100000,
    key_length=32
)
```

**Argon2** (Modern password hashing)
- Memory-hard algorithm
- Resistant to GPU/ASIC attacks
- Recommended for sensitive applications

```python
key = KeyDerivationFactory.derive_argon2(
    fingerprint_data,
    salt='unique_salt',
    time_cost=2,
    memory_cost=65536,
    parallelism=1,
    key_length=32
)
```

**Bcrypt** (Battle-tested algorithm)
- Adaptive, designed for passwords
- Resistant to brute-force attacks
- Tunable cost parameter

```python
key = KeyDerivationFactory.derive_bcrypt(
    fingerprint_data,
    salt='unique_salt',
    rounds=12
)
```

**Scrypt** (Cryptographically strong)
- Memory-hard KDF
- Sequential memory hard function
- High security margin

```python
key = KeyDerivationFactory.derive_scrypt(
    fingerprint_data,
    salt='unique_salt',
    n=16384,
    r=8,
    p=1,
    key_length=32
)
```

#### 3. EncodingStrategySelector
Automatically selects and parameterizes encoding strategies:

```python
from multi_encoding_key_derivation import EncodingStrategySelector, EncodingStrategy

selector = EncodingStrategySelector()

# Deterministically select strategy based on fingerprint
strategy = selector.select_strategy_from_fingerprint(fingerprint)
# Returns: EncodingStrategy.HEX (or other based on fingerprint hash)

# Get encoding parameters for strategy
params = selector.get_strategy_parameters(strategy, key)
# Returns: {'key': 42, 'multi_byte': True}
```

#### 4. MultiEncodingKeySystem
Main orchestration system:

```python
from multi_encoding_key_derivation import MultiEncodingKeySystem, KeyDerivationMethod, EncodingStrategy

system = MultiEncodingKeySystem()

# Create target profile
profile = system.create_target_profile(
    name='Production Server',
    fingerprint_data={
        'hostname': 'prod-01',
        'os': 'Ubuntu 20.04',
        'kernel': '5.10.0'
    },
    encoding_strategy=EncodingStrategy.HEX,
    key_derivation_method=KeyDerivationMethod.PBKDF2,
    salt='production_salt',
    iterations=100000,
    key_length=32
)

# Derive key for target
derived_key = system.derive_key_for_target(profile.target_id)

# Get encoding parameters
params = system.get_encoding_parameters(profile.target_id)

# Export complete configuration
config = system.export_key_config(profile.target_id)
```

### TargetProfile Structure

```python
@dataclass
class TargetProfile:
    target_id: str                    # Unique identifier
    name: str                         # Human-readable name
    fingerprint_data: Dict[str, str]  # System fingerprint
    encoding_strategy: EncodingStrategy
    key_derivation_method: KeyDerivationMethod
    salt: str = ""                    # Derivation salt
    iterations: int = 100000          # KDF iterations
    key_length: int = 32              # Key size in bytes
    metadata: Dict[str, Any]          # Additional data
    created_at: str                   # Timestamp
```

### DerivedKey Structure

```python
@dataclass
class DerivedKey:
    key: bytes                        # Raw key material
    hex_key: str                      # Hex representation
    strategy: EncodingStrategy
    derivation_method: KeyDerivationMethod
    target_id: str
    fingerprint_hash: str             # Hash of fingerprint
    salt_used: str                    # Salt used in derivation
    iterations: int                   # Iterations performed
    metadata: Dict[str, Any]          # Additional metadata
```

## Encoding Strategies

### HEX Encoding
Binary-safe hexadecimal representation:
```python
# Encoding: "Hello" -> "48656c6c6f"
# Decoding: "48656c6c6f" -> "Hello"
```

### BASE64 Encoding
Standard Base64 with padding:
```python
# Encoding: "Hello" -> "SGVsbG8="
# Decoding: "SGVsbG8=" -> "Hello"
```

### ROT13 Substitution
Caesar cipher with rotation 13:
```python
# Encoding: "Hello" -> "Uryyb"
# Rotation configurable per target
```

### XOR Cipher
XOR with key-derived byte:
```python
# Encoding: "Hello" XOR 0x42 -> "26172f2f2c"
# Key: derived from fingerprint (0-255)
```

### OCTAL Encoding
Octal byte representation:
```python
# Encoding: "A" (0x41) -> "101"
# Deterministic, reversible
```

### ASCII Encoding
Comma-separated ASCII values:
```python
# Encoding: "ABC" -> "65,66,67"
# Decoding: "65,66,67" -> "ABC"
```

### REVERSE
Simple string reversal:
```python
# Encoding: "Hello" -> "olleH"
# Symmetric operation
```

### Custom Substitution
Per-target substitution table:
```python
# Generated from key material
# Each character mapped to unique character
# Deterministic for same key
```

## Integration with Fingerprint Manager

The `FingerprintKeyIntegration` class provides unified fingerprint + encoding management:

```python
from fingerprint_key_integration import FingerprintKeyIntegration, TargetEncodingMode

integration = FingerprintKeyIntegration()

# Register existing fingerprint with encoding
fingerprint_id, target_id = integration.register_fingerprint_with_encoding(
    fingerprint_id='fp_12345',
    target_name='Windows Server Target',
    encoding_strategy=EncodingStrategy.HEX
)

# Encode payload for target
encoded = integration.encode_payload_for_target(
    target_id=target_id,
    payload="powershell.exe -Command",
    mode=TargetEncodingMode.DETERMINISTIC
)

# Decode payload
decoded = integration.decode_payload_for_target(
    target_id=target_id,
    encoded_payload=encoded.encoded
)

# Get integrated profile
profile = integration.get_integrated_profile(target_id)
```

## Usage Examples

### Example 1: Basic Key Derivation

```python
from multi_encoding_key_derivation import MultiEncodingKeySystem

system = MultiEncodingKeySystem()

# Create profile for target system
profile = system.create_target_profile(
    name='Web Server',
    fingerprint_data={
        'hostname': 'web-01.prod.local',
        'os': 'CentOS 7',
        'apache_version': '2.4.6'
    }
)

# Derive cryptographic key
derived_key = system.derive_key_for_target(profile.target_id)

print(f"Target: {profile.name}")
print(f"Strategy: {derived_key.strategy.value}")
print(f"Key: {derived_key.hex_key}")
print(f"Fingerprint Hash: {derived_key.fingerprint_hash}")
```

### Example 2: Multi-Method Comparison

```python
from multi_encoding_key_derivation import MultiEncodingKeySystem, KeyDerivationMethod

system = MultiEncodingKeySystem()

fingerprint = {
    'system_id': 'target_001',
    'hash': 'abc123def456'
}

methods = [
    KeyDerivationMethod.PBKDF2,
    KeyDerivationMethod.HKDF,
    KeyDerivationMethod.ARGON2
]

for method in methods:
    profile = system.create_target_profile(
        name=f"Method: {method.value}",
        fingerprint_data=fingerprint,
        key_derivation_method=method
    )
    
    key = system.derive_key_for_target(profile.target_id)
    print(f"{method.value}: {key.hex_key}")
```

### Example 3: Encoding Payload for Target

```python
from fingerprint_key_integration import FingerprintKeyIntegration

integration = FingerprintKeyIntegration()

# Get available fingerprints
fps = integration.fingerprint_manager.get_available_fingerprints()

for fp in fps[:1]:
    # Register with encoding
    fp_id, target_id = integration.register_fingerprint_with_encoding(
        fingerprint_id=fp['id'],
        target_name=f"Encoded {fp['name']}"
    )
    
    # Encode payload
    payload = "secret_command_here"
    encoded = integration.encode_payload_for_target(
        target_id=target_id,
        payload=payload
    )
    
    print(f"Original: {encoded.original}")
    print(f"Encoded: {encoded.encoded}")
    print(f"Strategy: {encoded.encoding_strategy}")
    
    # Verify decoding
    decoded = integration.decode_payload_for_target(
        target_id=target_id,
        encoded_payload=encoded.encoded
    )
    
    print(f"Decoded matches: {decoded == payload}")
```

### Example 4: Export Configuration

```python
from multi_encoding_key_derivation import MultiEncodingKeySystem
import json

system = MultiEncodingKeySystem()

profile = system.create_target_profile(
    name='Export Test',
    fingerprint_data={'device': 'laptop', 'os': 'Linux'}
)

# Export complete configuration
config = system.export_key_config(profile.target_id)

# Can be serialized to JSON
config_json = json.dumps(config, indent=2)
print(config_json)

# Expected structure:
# {
#   "target": { ... },
#   "key": { ... },
#   "encoding": { ... },
#   "metadata": { ... }
# }
```

## Security Considerations

### Key Uniqueness
- Each unique fingerprint produces unique keys
- Same fingerprint always produces same key (deterministic)
- Different salts produce different keys

### Salt Management
- Should be unpredictable and unique per target
- Can be auto-generated from fingerprint hash
- Can be explicitly specified for consistency

### Iteration Counts
- Default: 100,000 (PBKDF2)
- Higher = more resistant to brute-force
- Trade-off with performance
- Recommended minimum: 10,000 for PBKDF2

### Key Length
- Default: 32 bytes (256 bits)
- Suitable for AES-256
- Can be increased for additional margin

### Method Selection
- PBKDF2: Best compatibility, industry standard
- HKDF: Better entropy extraction, RFC standard
- Argon2/Scrypt: Memory-hard, modern security
- SHA256-Chain: Fast, lightweight
- HMAC-Chain: Balanced security/performance

## Testing

Run comprehensive test suite:

```bash
python3 test_multi_encoding_key_derivation.py
```

Tests include:
- Fingerprint hashing consistency
- Key derivation determinism
- Strategy selection
- Encoding/decoding roundtrips
- Integration scenarios
- Key uniqueness verification

## Configuration Storage

Configurations are stored in JSON format:

```
~/.sc-generator/encoding-keys/
├── target_profiles.json      # Target definitions
├── fingerprint_mappings.json # Fingerprint-target mappings
```

## API Reference

See inline docstrings in:
- `multi_encoding_key_derivation.py` - Core system
- `fingerprint_key_integration.py` - Integration layer

## Performance Characteristics

| Method | Iterations | Memory | Speed | Security |
|--------|-----------|--------|-------|----------|
| PBKDF2 | 100k | Low | Fast | Good |
| HKDF | - | Low | Very Fast | Excellent |
| SHA256-Chain | 100k | Low | Fast | Good |
| HMAC-Chain | 100k | Low | Fast | Very Good |
| Argon2 | Variable | High | Slow | Excellent |
| Bcrypt | Variable | Low | Slow | Excellent |
| Scrypt | Variable | High | Slow | Excellent |

## Troubleshooting

### Import Errors
Ensure all dependencies are installed:
```bash
pip3 install cryptography pycryptodomex argon2-cffi bcrypt
```

### Missing Fingerprints
Ensure fingerprint manager is initialized:
```python
from fingerprint_manager import FingerprintManager
mgr = FingerprintManager()
mgr._initialize_default_fingerprints()
```

### JSON Serialization
Ensure bytes are converted to hex strings:
```python
config = system.export_key_config(target_id)
# Parameters with bytes are automatically converted to hex
json_str = json.dumps(config)
```

## Future Enhancements

- Hardware security module (HSM) integration
- PBKDF3 support when available
- Multi-factor key derivation
- Key rotation strategies
- Hardware fingerprinting extensions
- Real-time key update mechanisms
