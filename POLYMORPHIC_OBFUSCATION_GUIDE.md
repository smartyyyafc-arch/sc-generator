# Polymorphic Obfuscation Techniques: Technical Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Polymorphic Engine Architecture](#polymorphic-engine-architecture)
4. [Obfuscation Techniques](#obfuscation-techniques)
5. [Implementation Examples](#implementation-examples)
6. [Advanced Patterns](#advanced-patterns)
7. [Detection & Anti-Detection](#detection--anti-detection)
8. [Performance Considerations](#performance-considerations)

---

## Overview

Polymorphic obfuscation is a dynamic code transformation technique where the same functionality is encoded differently each time it's generated. Unlike static obfuscation, polymorphic code changes its structure, encoding, and execution patterns while maintaining identical behavioral semantics.

### Key Characteristics
- **Self-modifying code**: Code mutates during execution
- **Varied encodings**: Same operation encoded multiple ways
- **Dynamic decryption**: Uses runtime decryption engines
- **Randomization**: Each instance differs from others
- **Evasion capability**: Defeats signature-based detection

---

## Core Concepts

### 1. Metamorphic vs. Polymorphic

| Aspect | Metamorphic | Polymorphic |
|--------|------------|------------|
| Structure | Changes during replication | Varies between instances |
| Engine | External transformer | Embedded decoder |
| Encoding | Source-level mutations | Instruction/data encoding |
| Detection | Harder (changes between generations) | Medium (engine is constant) |

### 2. Mutation Vectors

**Instruction-level mutations:**
- Register swapping: `mov eax, ebx` → `lea eax, [ebx + 0]`
- Instruction expansion: `inc eax` → `add eax, 1`
- Junk insertion: Random NOP sequences, unused variable assignments
- Branch reversal: `jz target` → `jnz skip; jmp target; skip:`

**Data encoding:**
- Byte substitution
- Arithmetic transformation
- XOR encryption with dynamic keys
- Bit reversal and rotation

---

## Polymorphic Engine Architecture

### Generic Polymorphic Decoder Model

```
┌─────────────────────────────────────────┐
│     Polymorphic Encrypted Payload       │
│  ┌──────────────────────────────────┐   │
│  │  Decoder Stub (Variable)         │   │
│  │  - Unique each generation        │   │
│  │  - Decryption logic              │   │
│  ├──────────────────────────────────┤   │
│  │  Encrypted Code Payload          │   │
│  │  - Variable encryption scheme    │   │
│  │  - Randomized key                │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
         ↓ (Execution)
┌─────────────────────────────────────────┐
│  Decoder Executes:                      │
│  1. Locates encrypted payload           │
│  2. Decrypts using embedded key         │
│  3. Transfers control to plaintext      │
│  4. Payload executes (functional code)  │
└─────────────────────────────────────────┘
```

### Engine Components

**Decoder Stub**
- Self-locating (position-independent)
- Key generation logic
- Decryption algorithm
- Jump/call to plaintext payload

**Encryption Scheme**
- Dynamic key derivation
- Various cipher modes (XOR, ADD, SUB, ROR)
- Randomized block size

**Key Repository**
- Embedded in decoder
- Derived from entropy source
- Time/counter-dependent generation

---

## Obfuscation Techniques

### 1. Instruction-Level Mutations

#### Technique: Register Swapping
Original code uses specific registers; polymorphic version randomizes:

```javascript
// Original
function add(a, b) {
    let result = a + b;
    return result;
}

// Generation 1 (using r1, r2, r3)
// r1 ← a
// r2 ← b
// r3 ← r1 + r2
// return r3

// Generation 2 (using r5, r7, r4)
// r5 ← a
// r7 ← b
// r4 ← r5 + r7
// return r4
```

#### Assembly-level example:
```asm
; Generation 1
mov eax, [ebp + 8]      ; eax = a
mov ebx, [ebp + 12]     ; ebx = b
add eax, ebx            ; eax = a + b
ret

; Generation 2 (same logic, different registers)
mov ecx, [ebp + 8]      ; ecx = a
mov edx, [ebp + 12]     ; edx = b
add ecx, edx            ; ecx = a + b
mov eax, ecx            ; move result to eax for return
ret
```

### 2. Arithmetic Substitution

Replace one operation with equivalent sequences:

```javascript
// Original
x = y + 5;

// Polymorphic Variant 1 (addition chain)
x = y + 2;
x = x + 3;

// Polymorphic Variant 2 (multiplication + subtraction)
x = y * 2;
x = x - y;
x = x + 5;

// Polymorphic Variant 3 (bitwise operations - for specific values)
x = (y | 4) + 1;  // If y is small and positive

// Polymorphic Variant 4 (using lookups)
const addTable = [0,1,2,3,4,5,6,7,8,9,10];
x = addTable[y % 11] + y - (y % 11) + 5;
```

### 3. Code Expansion via Junk Instructions

```javascript
// Original
function process(data) {
    return data * 2;
}

// Polymorphic variant with junk
function process(data) {
    let temp1 = Math.random();           // junk
    let unused = data ^ 0xDEADBEEF;      // junk assignment
    let result = data * 2;
    
    if (Math.PI > 3.0) {                 // always true junk condition
        let meaningless = temp1 + unused; // unused junk
    }
    
    return result;
}
```

### 4. Control Flow Flattening

Original branching converted to state machine:

```javascript
// Original
function authenticateUser(password) {
    if (password.length < 8) {
        return false;
    }
    if (!password.match(/[0-9]/)) {
        return false;
    }
    return true;
}

// Polymorphic (flattened state machine)
function authenticateUser(password) {
    let state = 0;
    let result = false;
    
    while (true) {
        switch(state) {
            case 0:
                state = (password.length < 8) ? 1 : 2;
                break;
            case 1:
                result = false;
                state = 99;
                break;
            case 2:
                state = (!password.match(/[0-9]/)) ? 3 : 4;
                break;
            case 3:
                result = false;
                state = 99;
                break;
            case 4:
                result = true;
                state = 99;
                break;
            case 99:
                return result;
        }
    }
}
```

### 5. Data Encoding via XOR Encryption

```javascript
// Original string data
const secret = "ADMIN_PASSWORD";

// Polymorphic encoded version
class PolymorphicString {
    constructor(plaintext, keyVariant) {
        this.keyVariant = keyVariant;
        this.encrypted = this.encryptVariant(plaintext);
    }
    
    encryptVariant(text) {
        const keys = [
            0x7F, 0xAB, 0xCD, 0xEF,  // Variant 1 key
            0x12, 0x34, 0x56, 0x78,  // Variant 2 key
            0xFE, 0xDC, 0xBA, 0x98,  // Variant 3 key
        ];
        
        const keySet = keys.slice(
            this.keyVariant * 4, 
            (this.keyVariant + 1) * 4
        );
        
        return text.split('').map((char, idx) => 
            String.fromCharCode(
                char.charCodeAt(0) ^ keySet[idx % keySet.length]
            )
        );
    }
    
    decrypt() {
        // Same as encrypt (XOR is symmetric)
        return this.encryptVariant(this.encrypted.join('')).join('');
    }
}

// Usage
const polymorphicSecret = new PolymorphicString("PASSWORD", 
    Math.floor(Math.random() * 3));
```

### 6. Dynamic Decoder Stub Generation

```python
# Python example for generating varied decoder stubs

import random
import os

class PolymorphicDecoderGenerator:
    def __init__(self, payload):
        self.payload = payload
        self.key = os.urandom(4)
        
    def generate_decoder_variant(self, variant_id):
        """Generate unique decoder for each instance"""
        
        if variant_id % 3 == 0:
            return self._decoder_xor_variant()
        elif variant_id % 3 == 1:
            return self._decoder_add_variant()
        else:
            return self._decoder_rol_variant()
    
    def _decoder_xor_variant(self):
        """XOR-based decoder"""
        key = int.from_bytes(self.key, 'little')
        encrypted = bytes([b ^ (key >> (8 * (i % 4))) & 0xFF 
                          for i, b in enumerate(self.payload)])
        
        return f"""
        def decode():
            key = {key}
            encrypted = {encrypted}
            decrypted = bytearray()
            for i, byte in enumerate(encrypted):
                decrypted.append(byte ^ ((key >> (8 * (i % 4))) & 0xFF))
            return bytes(decrypted)
        """
    
    def _decoder_add_variant(self):
        """Addition-based decoder"""
        key = int.from_bytes(self.key, 'little')
        encrypted = bytes([(b + key) & 0xFF for b in self.payload])
        
        return f"""
        def decode():
            key = {key}
            encrypted = {encrypted}
            decrypted = bytearray()
            for byte in encrypted:
                decrypted.append((byte - key) & 0xFF)
            return bytes(decrypted)
        """
    
    def _decoder_rol_variant(self):
        """Rotate-left based decoder"""
        key = int.from_bytes(self.key, 'little') & 0x7
        encrypted = bytes([((b << key) | (b >> (8 - key))) & 0xFF 
                          for b in self.payload])
        
        return f"""
        def decode():
            key = {key}
            encrypted = {encrypted}
            decrypted = bytearray()
            for byte in encrypted:
                decrypted.append(((byte >> key) | (byte << (8 - key))) & 0xFF)
            return bytes(decrypted)
        """
```

---

## Implementation Examples

### Example 1: JavaScript Polymorphic Payload Encoder

```javascript
class PolymorphicPayloadEncoder {
    constructor(sourceCode) {
        this.source = sourceCode;
        this.generationCount = 0;
    }
    
    // Main entry point
    encode() {
        const variant = this.generationCount++ % 5;
        
        switch(variant) {
            case 0: return this.encodeWithStringXor();
            case 1: return this.encodeWithArrayShuffling();
            case 2: return this.encodeWithFunctionChaining();
            case 3: return this.encodeWithRegexSubstitution();
            case 4: return this.encodeWithArrayDecoding();
        }
    }
    
    // Variant 1: String XOR with random key
    encodeWithStringXor() {
        const key = Math.floor(Math.random() * 256);
        const encoded = Array.from(this.source)
            .map(char => String.fromCharCode(char.charCodeAt(0) ^ key))
            .join('');
        
        return `
(function() {
    const key = ${key};
    const encoded = ${JSON.stringify(encoded)};
    const decoded = Array.from(encoded)
        .map(char => String.fromCharCode(char.charCodeAt(0) ^ key))
        .join('');
    eval(decoded);
})();`;
    }
    
    // Variant 2: Array shuffling with index mapping
    encodeWithArrayShuffling() {
        const chars = this.source.split('');
        const indices = chars.map((_, i) => i);
        
        // Fisher-Yates shuffle
        for (let i = indices.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [indices[i], indices[j]] = [indices[j], indices[i]];
        }
        
        const shuffled = indices.map(i => chars[i]);
        const mapping = indices.map((_, i) => indices.indexOf(i));
        
        return `
(function() {
    const shuffled = ${JSON.stringify(shuffled)};
    const mapping = ${JSON.stringify(mapping)};
    const decoded = new Array(shuffled.length);
    for (let i = 0; i < shuffled.length; i++) {
        decoded[mapping[i]] = shuffled[i];
    }
    eval(decoded.join(''));
})();`;
    }
    
    // Variant 3: Function chaining with intermediate transformations
    encodeWithFunctionChaining() {
        const step1 = this.source.split('')
            .map((c, i) => String.fromCharCode(c.charCodeAt(0) + i))
            .join('');
        
        return `
(function() {
    const step1 = ${JSON.stringify(step1)};
    const decoded = Array.from(step1)
        .map((c, i) => String.fromCharCode(c.charCodeAt(0) - i))
        .join('');
    (function(code) { eval(code); })(decoded);
})();`;
    }
    
    // Variant 4: Regex-based substitution obfuscation
    encodeWithRegexSubstitution() {
        let obfuscated = this.source;
        const substitutions = {
            'function': 'Function',
            'return': 'return ',
            'var': 'var ',
        };
        
        Object.entries(substitutions).forEach(([key, replacement]) => {
            obfuscated = obfuscated.replace(
                new RegExp(key, 'g'),
                replacement + String.fromCharCode(Math.random() * 256)
            );
        });
        
        return `
(function() {
    const obfuscated = ${JSON.stringify(obfuscated)};
    const cleaned = obfuscated
        .replace(/Function/g, 'function')
        .replace(/return\\s/g, 'return')
        .replace(/var\\s/g, 'var');
    eval(cleaned);
})();`;
    }
    
    // Variant 5: Array-based character encoding
    encodeWithArrayDecoding() {
        const charCodes = this.source.split('').map(c => c.charCodeAt(0));
        const step = Math.floor(Math.random() * 256) + 1;
        const encoded = charCodes.map(code => code ^ step);
        
        return `
(function() {
    const step = ${step};
    const encoded = ${JSON.stringify(encoded)};
    const decoded = String.fromCharCode(
        ...encoded.map(code => code ^ step)
    );
    eval(decoded);
})();`;
    }
}

// Usage
const encoder = new PolymorphicPayloadEncoder('alert("Hello")');
console.log(encoder.encode());  // Variant 1
console.log(encoder.encode());  // Variant 2
console.log(encoder.encode());  // Variant 3
```

### Example 2: Binary-level Polymorphic Engine (Pseudo-code)

```c
// Pseudo-code for binary polymorphic engine

typedef struct {
    uint8_t *encrypted_payload;
    size_t payload_size;
    uint32_t encryption_key;
    uint8_t cipher_variant;
} PolymorphicPackage;

typedef struct {
    uint8_t *code;
    size_t size;
} DecodedPayload;

// Polymorphic decryption engine
DecodedPayload* polymorphic_decrypt(PolymorphicPackage *pkg) {
    DecodedPayload *result = malloc(sizeof(DecodedPayload));
    result->code = malloc(pkg->payload_size);
    result->size = pkg->payload_size;
    
    // Variant selection
    switch(pkg->cipher_variant) {
        case CIPHER_XOR:
            decrypt_xor(result->code, pkg->encrypted_payload, 
                       pkg->payload_size, pkg->encryption_key);
            break;
            
        case CIPHER_ADD:
            decrypt_add(result->code, pkg->encrypted_payload, 
                       pkg->payload_size, pkg->encryption_key);
            break;
            
        case CIPHER_SUB:
            decrypt_sub(result->code, pkg->encrypted_payload, 
                       pkg->payload_size, pkg->encryption_key);
            break;
            
        case CIPHER_ROR:
            decrypt_ror(result->code, pkg->encrypted_payload, 
                       pkg->payload_size, pkg->encryption_key & 0x7);
            break;
            
        default:
            return NULL;
    }
    
    return result;
}

// Individual decryption algorithms
void decrypt_xor(uint8_t *dst, uint8_t *src, size_t len, uint32_t key) {
    for (size_t i = 0; i < len; i++) {
        dst[i] = src[i] ^ ((key >> (8 * (i % 4))) & 0xFF);
    }
}

void decrypt_add(uint8_t *dst, uint8_t *src, size_t len, uint32_t key) {
    for (size_t i = 0; i < len; i++) {
        dst[i] = (src[i] - ((key >> (8 * (i % 4))) & 0xFF)) & 0xFF;
    }
}

void decrypt_ror(uint8_t *dst, uint8_t *src, size_t len, uint8_t shift) {
    for (size_t i = 0; i < len; i++) {
        dst[i] = ((src[i] >> shift) | (src[i] << (8 - shift))) & 0xFF;
    }
}

// Execute decoded payload
int execute_payload(DecodedPayload *payload) {
    // Cast to function pointer and execute
    int (*func)(void) = (int (*)(void))payload->code;
    return func();
}
```

### Example 3: Multi-layered Polymorphic Obfuscation

```javascript
class MultiLayerPolymorphicObfuscator {
    constructor(sourceCode) {
        this.source = sourceCode;
    }
    
    obfuscate() {
        // Layer 1: Control flow flattening
        let layer1 = this.flattenControlFlow(this.source);
        
        // Layer 2: Variable renaming with polymorphic mapping
        let layer2 = this.polymorphicVariableRename(layer1);
        
        // Layer 3: String encryption
        let layer3 = this.encryptStrings(layer2);
        
        // Layer 4: Add junk code
        let layer4 = this.injectJunkCode(layer3);
        
        // Layer 5: Wrap in decoder
        let layer5 = this.wrapInDecoder(layer4);
        
        return layer5;
    }
    
    flattenControlFlow(code) {
        // Convert if/else/loops into state machine
        return code.replace(
            /if\s*\((.*?)\)\s*\{(.*?)\}/g,
            (match, condition, body) => {
                const stateId = Math.random().toString(36).substr(2, 9);
                return `
if (${condition}) {
    __state_${stateId}__ = true;
    ${body}
}`;
            }
        );
    }
    
    polymorphicVariableRename(code) {
        const varMap = {};
        const varPattern = /\b(var|let|const)\s+(\w+)/g;
        
        let match;
        while ((match = varPattern.exec(code)) !== null) {
            const originalName = match[2];
            if (!varMap[originalName]) {
                // Generate random name that changes per execution
                varMap[originalName] = `_${Math.random().toString(36).substr(2)}_`;
            }
        }
        
        let result = code;
        Object.entries(varMap).forEach(([original, renamed]) => {
            result = result.replace(new RegExp(`\\b${original}\\b`, 'g'), renamed);
        });
        
        return result;
    }
    
    encryptStrings(code) {
        const stringPattern = /"(.*?)"|'(.*?)'/g;
        const encryptedStrings = {};
        let counter = 0;
        
        let result = code.replace(stringPattern, (match, dq, sq) => {
            const original = dq || sq;
            const encrypted = this.encryptString(original);
            const varName = `__str_${counter++}__`;
            encryptedStrings[varName] = encrypted;
            return `(function(){
                const key = ${Math.random() * 256 | 0};
                const enc = ${JSON.stringify(encrypted)};
                return String.fromCharCode(
                    ...enc.map((c, i) => c ^ key)
                );
            })()`;
        });
        
        return result;
    }
    
    encryptString(str) {
        const key = Math.floor(Math.random() * 256);
        return str.split('').map(c => c.charCodeAt(0) ^ key);
    }
    
    injectJunkCode(code) {
        const junkSnippets = [
            'let _j = Math.random();',
            'void (_j ^ 0xDEADBEEF);',
            'if (Math.PI > 0) { let _unused = _j; }',
            'const _temp = [].concat(0, 1, 2);',
        ];
        
        // Insert random junk at random positions
        let result = code;
        const junkCount = Math.floor(Math.random() * 3) + 1;
        
        for (let i = 0; i < junkCount; i++) {
            const junk = junkSnippets[Math.floor(Math.random() * junkSnippets.length)];
            const pos = Math.floor(Math.random() * result.length);
            result = result.slice(0, pos) + junk + result.slice(pos);
        }
        
        return result;
    }
    
    wrapInDecoder(code) {
        const decoderId = Math.random().toString(36).substr(2, 9);
        return `
(function() {
    const decoder_${decoderId} = function() {
        ${code}
    };
    decoder_${decoderId}();
})();`;
    }
}

// Usage
const obfuscator = new MultiLayerPolymorphicObfuscator(`
function login(user, pass) {
    if (user === "admin" && pass === "secret") {
        return true;
    }
    return false;
}
login("admin", "secret");
`);

console.log(obfuscator.obfuscate());
```

---

## Advanced Patterns

### 1. Metamorphic Instruction Substitution Table

```javascript
const instructionSubstitutionTable = {
    // Original -> [Alternative 1, Alternative 2, Alternative 3]
    'add': [
        'function(a, b) { return a + b; }',
        'function(a, b) { let r = 0; for(let i = 0; i < b; i++) r = a + 1; return r; }',
        'function(a, b) { return a ^ b ^ (a & b) << 1; }', // XOR-based addition
    ],
    'multiply': [
        'function(a, b) { return a * b; }',
        'function(a, b) { let r = 0; for(let i = 0; i < b; i++) r += a; return r; }',
        'function(a, b) { return (a * b); }', // Direct (will be obfuscated)
    ],
    'compare': [
        'function(a, b) { return a < b ? -1 : (a > b ? 1 : 0); }',
        'function(a, b) { return a - b; }',
        'function(a, b) { return (a ^ ((a ^ b) | ((a - b) >> 31))) - (b ^ ((a ^ b) | ((a - b) >> 31))); }',
    ]
};
```

### 2. Anti-Debugging Polymorphic Detector

```javascript
class PolymorphicAntiDebugger {
    static createDebuggingDetector() {
        // Each variant checks for different debugging indicators
        const variants = [
            this.variantCheckDevtools,
            this.variantCheckBreakpoints,
            this.variantCheckTimingAnomaly,
            this.variantCheckConsoleAPI,
        ];
        
        const variant = variants[Math.floor(Math.random() * variants.length)];
        return variant.call(this);
    }
    
    static variantCheckDevtools() {
        return `
(function() {
    const isOpen = () => {
        const start = performance.now();
        debugger;
        return (performance.now() - start) > 100;
    };
    if (isOpen()) { throw new Error('Debugging detected'); }
})();`;
    }
    
    static variantCheckBreakpoints() {
        return `
(function() {
    const func = () => { };
    const start = performance.now();
    func.toString(); // May pause if breakpoint set
    const elapsed = performance.now() - start;
    if (elapsed > 50) { throw new Error('Breakpoint detected'); }
})();`;
    }
    
    static variantCheckTimingAnomaly() {
        return `
(function() {
    const iterations = 1000000;
    const start = performance.now();
    for (let i = 0; i < iterations; i++) { }
    const elapsed = performance.now() - start;
    if (elapsed > 1000) { throw new Error('Debugging or heavy load detected'); }
})();`;
    }
    
    static variantCheckConsoleAPI() {
        return `
(function() {
    const originalLog = console.log;
    let called = false;
    console.log = function() {
        called = true;
        originalLog.apply(console, arguments);
    };
    const test = console.log === originalLog;
    if (!test) { throw new Error('Console hooked'); }
})();`;
    }
}
```

### 3. Self-Modifying Payload Executor

```python
class SelfModifyingPolymorph:
    def __init__(self, original_code):
        self.original = original_code
        self.mutations = []
    
    def execute_with_self_modification(self):
        """Execute code that modifies itself"""
        
        # Phase 1: Encrypt and store original
        encrypted = self._encrypt_phase(self.original)
        
        # Phase 2: Execute encrypted code
        decryption_key = self._generate_key()
        self.mutations.append(encrypted)
        
        # Phase 3: Self-modify during execution
        return self._execute_with_mutations(encrypted, decryption_key)
    
    def _encrypt_phase(self, code):
        """Encrypt code with polymorphic key"""
        import os
        key = os.urandom(16)
        from cryptography.fernet import Fernet
        
        cipher = Fernet(Fernet.generate_key())
        encrypted = cipher.encrypt(code.encode())
        return encrypted
    
    def _generate_key(self):
        """Generate polymorphic decryption key"""
        import time
        import hashlib
        
        # Key derived from current time + entropy
        timestamp = str(time.time()).encode()
        entropy = os.urandom(8)
        return hashlib.sha256(timestamp + entropy).digest()
    
    def _execute_with_mutations(self, encrypted_code, key):
        """Execute and mutate code on each cycle"""
        
        mutation_count = 0
        max_mutations = 5
        
        while mutation_count < max_mutations:
            # Decrypt current iteration
            current_code = self._decrypt_code(encrypted_code, key)
            
            # Mutate the code for next iteration
            mutated_code = self._mutate_code(current_code)
            
            # Execute current version
            exec(current_code)
            
            # Prepare for next cycle
            encrypted_code = self._encrypt_phase(mutated_code)
            key = self._generate_key()
            mutation_count += 1
    
    def _mutate_code(self, code):
        """Apply random mutations to code"""
        import random
        
        mutations = [
            lambda c: self._rename_variables(c),
            lambda c: self._reorder_statements(c),
            lambda c: self._insert_dead_code(c),
            lambda c: self._transform_literals(c),
        ]
        
        mutation_func = random.choice(mutations)
        return mutation_func(code)
    
    def _rename_variables(self, code):
        """Rename all variables randomly"""
        import re
        import random
        import string
        
        var_pattern = r'\b([a-zA-Z_]\w*)\b'
        seen = {}
        
        def replacer(match):
            var = match.group(1)
            if var not in seen:
                seen[var] = '_' + ''.join(random.choices(string.ascii_lowercase, k=8))
            return seen[var]
        
        return re.sub(var_pattern, replacer, code)
    
    def _reorder_statements(self, code):
        """Reorder independent statements"""
        lines = code.split('\n')
        # Simple reordering (in production, need dependency analysis)
        import random
        random.shuffle(lines)
        return '\n'.join(lines)
    
    def _insert_dead_code(self, code):
        """Insert non-functional code snippets"""
        dead_snippets = [
            'x = 0xDEADBEEF',
            'y = [1, 2, 3]',
            'unused_var = None',
        ]
        
        import random
        for _ in range(random.randint(1, 3)):
            code += '\n' + random.choice(dead_snippets)
        
        return code
    
    def _transform_literals(self, code):
        """Transform literal values"""
        import re
        
        def transform_number(match):
            num = int(match.group(0))
            # Encode as operation
            return f'({num} + 0)'
        
        return re.sub(r'\b\d+\b', transform_number, code)
    
    def _decrypt_code(self, encrypted, key):
        """Decrypt code (placeholder)"""
        return encrypted.decode() if isinstance(encrypted, bytes) else encrypted
```

---

## Detection & Anti-Detection

### Detection Signatures

```regex
# Polymorphic decoder patterns
eval\s*\(\s*["\'].*?["\']
Function\s*\(\s*["\'].*?["\']
String\.fromCharCode\s*\(\s*\.\.\.
atob\s*\(\s*["\'].*?["\']

# Self-modifying code patterns
(decrypted|decoded|decompressed)\.(call|apply|replace)
\[\s*Math\.random\(\)\s*\]
undefined\s*(while|for)\s*\(
__[a-zA-Z0-9_]+__\s*=
```

### Anti-Detection Techniques

```javascript
// Technique 1: Decoder obfuscation
const obfuscatedDecoder = (() => {
    const code = (function(){/*actual decoder*/}).toString();
    const lines = code.split('\n').reverse(); // Reverse lines
    return lines.join('\n');
})();

// Technique 2: Hiding eval usage
const executeCode = (() => {
    const evalFunc = [].constructor.constructor('return this')().eval;
    return (code) => evalFunc(code);
})();

// Technique 3: Breaking signature patterns
const polymorphicEval = (code) => {
    const marker = Symbol('exec');
    const executor = {
        [marker]: eval
    };
    return executor[marker](code);
};

// Technique 4: Timing-dependent execution
const timedExecution = (code) => {
    const delay = Math.random() * 1000;
    setTimeout(() => eval(code), delay);
};
```

---

## Performance Considerations

### Optimization Strategies

```javascript
class OptimizedPolymorphicEngine {
    constructor() {
        this.cache = new Map();
        this.compiledCache = new WeakMap();
    }
    
    // Cache decoded payloads to avoid recomputation
    executeWithCache(encryptedPayload, key) {
        const cacheKey = `${encryptedPayload.toString()}_${key}`;
        
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }
        
        const decrypted = this.decrypt(encryptedPayload, key);
        this.cache.set(cacheKey, decrypted);
        
        return decrypted;
    }
    
    // Lazy decryption only when needed
    lazyDecode(encryptedPayload) {
        return new Proxy({}, {
            get: (target, prop) => {
                if (!(prop in target)) {
                    target[prop] = this.decrypt(encryptedPayload)[prop];
                }
                return target[prop];
            }
        });
    }
    
    // Batch encryption to reduce overhead
    batchEncrypt(payloads, key) {
        return payloads.map(payload => this.encryptEfficient(payload, key));
    }
    
    encryptEfficient(payload, key) {
        // Use native crypto when available
        if (typeof crypto !== 'undefined') {
            return crypto.subtle.encrypt('AES-GCM', key, payload);
        }
        // Fallback to JavaScript implementation
        return this.encryptFallback(payload, key);
    }
    
    decrypt(payload, key) {
        // Efficient decryption
        const buffer = new Uint8Array(payload);
        const keyBuffer = new Uint8Array(key);
        
        return buffer.map((byte, i) => 
            byte ^ keyBuffer[i % keyBuffer.length]
        );
    }
}
```

### Polymorphic Overhead Analysis

| Technique | Encoding Time | Decoding Time | Size Overhead | Detection Risk |
|-----------|--------------|--------------|---------------|----------------|
| XOR Single | <1ms | <1ms | 0% | High |
| XOR Layered | 5ms | 5ms | 10% | Low |
| Arithmetic | 10ms | 10ms | 25% | Medium |
| Control Flow Flattening | 50ms | Inline | 150% | Very Low |
| Multi-layer | 100ms | 20ms | 200% | Very Low |

---

## Countermeasures & Hardening

### Runtime Integrity Checking

```javascript
class IntegrityMonitor {
    static monitorCodeExecution() {
        const originalEval = eval;
        const executedPayloads = new Set();
        
        window.eval = function(code) {
            // Log all eval executions
            executedPayloads.add(code);
            
            // Verify code signature
            if (!IntegrityMonitor.verifySignature(code)) {
                throw new Error('Code integrity check failed');
            }
            
            return originalEval.call(this, code);
        };
    }
    
    static verifySignature(code) {
        // Implement code signing/verification
        const hash = IntegrityMonitor.hashCode(code);
        return IntegrityMonitor.knownHashes.has(hash);
    }
    
    static hashCode(code) {
        let hash = 0;
        for (let i = 0; i < code.length; i++) {
            hash = ((hash << 5) - hash) + code.charCodeAt(i);
            hash = hash & hash;
        }
        return hash;
    }
}
```

---

## Conclusion

Polymorphic obfuscation represents one of the most sophisticated code protection and evasion techniques. Its strength lies in:

1. **Variability**: Each instance is unique, defeating static analysis
2. **Embedding**: Decoder is built into the protected code
3. **Multi-layering**: Combining multiple techniques increases security
4. **Adaptability**: Can mutate based on runtime detection

However, effective defenses include:

- Behavioral analysis (not just static)
- Runtime monitoring and integrity checking
- Sandboxed execution environments
- Advanced decompilation tools

Understanding both attack and defense mechanisms is essential for security professionals working in reverse engineering, malware analysis, and code protection domains.

---

## References

- "Polymorphic Code and Computer Viruses" - Academic research
- "Metamorphic Engines in Malware Analysis" - Security conferences
- "Advanced Code Obfuscation Techniques" - OWASP guidelines
- "Binary Instrumentation and Self-Modification" - Low-level systems research

