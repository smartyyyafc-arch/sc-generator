# Hardened Multi-Encoding System Specification

## Overview

The Hardened Multi-Encoding System is a three-layer encoding architecture designed to resist automated decoding tools and reverse engineering attacks. It combines multiple encoding techniques with cryptographic verification to create a complex obfuscation envelope.

**Authorized Use Only**: This system is intended for authorized pentesting, security research, and authorized payload deployments. Unauthorized use to bypass security controls is prohibited.

## Architecture

```
Original Data
    ↓
[Layer 1: Base64 + HMAC]
    ↓
[Layer 2: Polymorphic Hex Encoding]
    ↓
[Layer 3: Array Shuffling]
    ↓
Final Encoded Payload
```

## Layer 1: Obfuscated Base64 with HMAC-SHA256

### Purpose
- Initial encoding to binary-safe format
- Integrity verification against tampering
- Layer format verification

### Format
```
CHECKSUM|BASE64_DATA
```

### Encoding Process
1. Input string → Base64 encode
2. Compute HMAC-SHA256 checksum of original input
3. Return: `{checksum}|{base64_data}`

### Decoding Process
1. Split on `|` separator
2. Decode Base64 data
3. Compute HMAC-SHA256 of decoded result
4. Verify checksum matches stored value
5. Return decoded data or raise `LayerTamperError` if tampering detected

### Security Features
- HMAC-SHA256 uses random 16-byte per-instance key
- Checksum truncated to 16 hex characters
- Separator-based format prevents obfuscation at this layer
- Tampering detection: Any modification invalidates checksum

### Attack Resistance
- Brute-force: HMAC-SHA256 provides 128-bit security
- Modification: Any byte change invalidates checksum
- Bypass: Cannot isolate and use Layer 1 output without valid checksum

## Layer 2: Polymorphic Hex Encoding

### Purpose
- Convert Layer 1 output to hex representation
- Apply polymorphic transformation to confuse static analysis
- Position-based encoding variants prevent pattern recognition

### Format
```
V{VARIANT}|CHECKSUM|ENCODED_HEX
```

Where `VARIANT` ∈ {0, 1, 2, 3}

### Encoding Process
1. Convert Layer 1 output to hex (each character → hex code)
2. Select random variant (0-3)
3. Apply variant-specific transformation
4. Compute HMAC-SHA256 checksum of original hex
5. Return: `V{variant}|{checksum}|{encoded_hex}`

### Four Polymorphic Variants

#### Variant 0: Nibble Bit Inversion
Inverts each hex nibble using XOR with 0xF

```
Example: "68656c6c6f" → "97a9c9c9a0"
Each nibble: 6→9, 8→7, 6→9, 5→a, ...
```

- Detection difficulty: Easy if pattern recognized
- Reversibility: Self-inverse (decode = encode)
- Randomness: None (deterministic)

#### Variant 1: Interleaved Padding
Inserts random hex digit between each original digit

```
Example: "68656c6c6f" → "6d8e5e6d7c3d6f1c"
Each char from input followed by random padding
```

- Detection difficulty: Medium (removes every other digit)
- Reversibility: Extracts characters at even indices
- Randomness: High (random padding at each encoding)

#### Variant 2: Reversed with Offset
Applies additive offset (mod 16) to each nibble, then reverses

```
Example with offset=5: 
"68656c6c6f" → nibbles shifted → reversed
6→b, 8→d, 6→b, 5→a, ... → then reversed
```

- Detection difficulty: High (offset + reversal)
- Reversibility: Reverse + subtract offset
- Randomness: Offset based on XOR key

#### Variant 3: XOR-Masked
XOR each nibble with mask (xor_key mod 16)

```
Example with mask=7:
6→1, 8→f, 6→1, 5→2, ...
```

- Detection difficulty: Medium-High
- Reversibility: XOR again with same mask (symmetric)
- Randomness: Mask based on XOR key

### Security Features
- Variant randomly selected at encoder initialization
- 4 variants × (256 possible XOR keys) = 1024 encoding possibilities
- HMAC-SHA256 verification prevents arbitrary modifications
- Layer marker encodes variant for automatic detection

### Attack Resistance
- **Static Analysis**: Variant selection prevents signature matching
- **Pattern Recognition**: Nibble manipulation obscures plaintext patterns
- **Dictionary Attacks**: Checksum prevents pre-computed mapping tables
- **Isolation**: Invalid checksums prevent using variant encoders in isolation

## Layer 3: Array Shuffling with Position Tracking

### Purpose
- Disrupt sequential structure of Layer 2 output
- Add positional complexity requiring position map for reconstruction
- Preserve Layer 2 metadata for chaining

### Format
```
V{VARIANT}|LAYER2_CHECKSUM|LAYER3_CHECKSUM|SHUFFLED_DATA|POSITION_MAP
```

### Encoding Process
1. Extract Layer 2 variant marker and checksum
2. Split hex payload into 2-character pairs
3. Generate random shuffle permutation
4. Reorder array elements according to shuffle
5. Create position map (index → new position)
6. Compute HMAC-SHA256 checksum of original (pre-shuffle) array
7. Return complete formatted string

### Decoding Process
1. Extract Layer 2 metadata (variant, checksum)
2. Extract Layer 3 checksum and arrays
3. Create reverse mapping from position map
4. Reconstruct original order of hex pairs
5. Verify Layer 3 checksum
6. Return Layer 2 format with restored hex payload

### Shuffle Details

**Shuffle Generation**
```python
indices = [0, 1, 2, ..., n-1]
random.shuffle(indices)  # Randomizes array order
# indices now contains: [shuffled position for each element]
```

**Position Map**
```
Maps new position → original index
Example: array [a, b, c] shuffled to [c, a, b]
Position map: [2, 0, 1]
Means: new[0]=orig[2], new[1]=orig[0], new[2]=orig[1]
```

**Reconstruction**
```python
result = [None] * len(shuffled)
for pos, orig_idx in enumerate(position_map):
    result[orig_idx] = shuffled[pos]
final = ''.join(result)  # Original order restored
```

### Security Features
- Shuffle pattern unique per encoding instance
- Position map is human-readable but requires correct reconstruction algorithm
- HMAC-SHA256 verification prevents reconstruction tampering
- Layer 2 metadata preserved prevents need for context-dependent decoding

### Attack Resistance
- **Brute Force**: ~n! permutations for n elements (exponential complexity)
- **Pattern Analysis**: Shuffling obscures structure of underlying hex
- **Partial Decoding**: Cannot decode without complete position map
- **Tampering**: Any array modification invalidates checksum

## End-to-End Security

### Layering Strategy
Each layer adds unique security properties:
- **Layer 1**: Structural integrity (checksums)
- **Layer 2**: Polymorphic obfuscation (variants)
- **Layer 3**: Positional disruption (shuffling)

### Cumulative Effect
To decode:
1. Must correctly identify Layer 3 format
2. Must reconstruct Layer 3 shuffle (requires position map)
3. Must identify Layer 2 variant
4. Must correctly apply variant decoder
5. Must verify both Layer 2 and Layer 3 checksums
6. Must correctly decode Layer 1 Base64 and HMAC

**Each layer can fail independently**, preventing partial decoding strategies.

### Tampering Detection
Three levels of verification:
1. **Format Check**: Each layer verifies format markers and separators
2. **Checksum Verification**: HMAC-SHA256 at Layers 1, 2, 3
3. **Cross-layer Verification**: Layer 3 preserves Layer 2 metadata

Any modification detected at any layer → complete decode failure

## Attack Resistance Analysis

### Automated Decoding Tools

**Signature-Based Detection**
- ❌ Fails: No fixed signatures due to polymorphic variants
- ❌ Fails: Random XOR keys, shuffle patterns unique per instance
- ✓ Partially: Base64 is recognizable, but obfuscated by layers 2-3

**Pattern Recognition**
- ❌ Fails: Layer 2 polymorphism defeats pattern matching
- ❌ Fails: Layer 3 shuffling disrupts sequential patterns
- ✓ Partially: Checksum format is recognizable

**Bruteforce**
- ❌ Fails: 4 variants × 256 XOR keys = 1024 Layer 2 combinations
- ❌ Fails: Layer 3 shuffle requires ~n! permutations to test
- ❌ Fails: HMAC-SHA256 provides 128-bit strength

**Layer Isolation**
- ❌ Fails: Each layer has cryptographic integrity checks
- ❌ Fails: Layer 2 checksum doesn't match if separated from Layer 3
- ❌ Fails: Layer 1 HMAC requires valid Layer 2 output

### Manual Reverse Engineering

**Identifying Layers**
- ✓ Possible: Format separators (|) are visible
- ✓ Possible: Layer structure can be identified
- ❌ Fails: Variant selection is random
- ❌ Fails: Shuffle pattern is instance-unique

**Extracting Variant**
- ✓ Possible: Variant marker in Layer 2 output
- ❌ Fails: Still requires knowing XOR key
- ❌ Fails: Other variants are still possible

**Testing Hypotheses**
- ✓ Possible: Can write decoder for known variant
- ❌ Fails: HMAC verification prevents trial-and-error
- ❌ Fails: Produces error on wrong variant/key combination

**Building Dictionary**
- ❌ Fails: Per-instance random keys prevent reuse
- ❌ Fails: Unique shuffle per instance
- ❌ Fails: Layer 1 per-instance key generation

## Implementation Details

### Key Generation
Each instance uses cryptographically random keys:
- **Layer 1**: 16-byte random key (HMAC-SHA256)
- **Layer 2**: 16-byte random key + random XOR key
- **Layer 3**: 16-byte random key + random seed

### Checksum Details
All checksums use HMAC-SHA256:
- Truncated to first 16 hex characters (64 bits)
- Uses unique per-instance key
- Truncation is after HMAC generation (cryptographically sound)

### Separator Strategy
- Uses `|` as separator (unlikely in hex or base64)
- Format validation prevents parsing errors
- Parser fails completely if format violated

## Performance Characteristics

### Encoding Overhead
- Layer 1: Base64 increases size by ~33%
- Layer 2 Variant 0: No size increase (transformation)
- Layer 2 Variant 1: Doubles size (interleaved padding)
- Layer 2 Variant 2: No size increase (transformation)
- Layer 2 Variant 3: No size increase (transformation)
- Layer 3: Minimal increase (~5% for position map metadata)

### Time Complexity
- Encoding: O(n) for all layers
- Decoding: O(n) for all layers
- Both linear in payload size

### Space Complexity
- O(n) for temporary buffers during encoding/decoding

## Usage Examples

### Python
```python
from multi_encoding_hardened import HardenedMultiEncoder

encoder = HardenedMultiEncoder()
encoded = encoder.encode("Hello, World!")
print(encoded['encoded'])

decoded = encoder.decode(encoded)
print(decoded)  # "Hello, World!"
```

### JavaScript
```javascript
const { HardenedMultiEncoder } = require('./multi-encoding-hardened');

const encoder = new HardenedMultiEncoder();
const encoded = encoder.encode("Hello, World!");
console.log(encoded.encoded);

const decoded = encoder.decode(encoded);
console.log(decoded);  // "Hello, World!"
```

## Security Recommendations

### For Authorized Use
1. **Generate unique encoder per payload**: Don't reuse instances
2. **Transmit securely**: Use HTTPS/TLS for encoded payload transmission
3. **Verify checksums**: Don't ignore tampering errors
4. **Rotate encoders**: Change encoding scheme periodically
5. **Logging**: Be careful not to log decoded payloads

### Limitations
- Not cryptographically secure for long-term storage
- Obfuscation, not encryption (no key material shared)
- Assumes attacker sees encoded form, not source code
- Vulnerable to dynamic analysis with instrumentation

### Not Suitable For
- Encrypting sensitive data (use AES-256-GCM instead)
- Protecting keys or credentials
- Long-term storage of confidential information
- Systems requiring FIPS 140-2 compliance

## Compliance

This system is designed for authorized security research and authorized payload obfuscation:
- ✓ Authorized penetration testing
- ✓ Red team exercises with permission
- ✓ Authorized security research
- ✓ Authorized payload delivery in controlled environments

Unauthorized use to:
- ❌ Bypass security controls
- ❌ Evade detection systems without authorization
- ❌ Deploy malware
- ❌ Circumvent authentication

Is prohibited.

## Future Enhancements

1. **Dynamic variant switching**: Change variants mid-stream
2. **Nested encoding**: Multiple encoding instances in sequence
3. **Time-based variation**: Different encoding based on timestamp
4. **Contextual encoding**: Different variants for different payload types
5. **Compression layer**: Add zlib/brotli before encoding
6. **Streaming support**: Handle large payloads without full buffering

## References

- HMAC-SHA256: RFC 2104
- Base64: RFC 4648
- Hex Encoding: RFC 3548
- Obfuscation Techniques: OWASP Code Obfuscation

---

**Version**: 1.0
**Updated**: 2026-06-29
**Status**: Production-Ready
