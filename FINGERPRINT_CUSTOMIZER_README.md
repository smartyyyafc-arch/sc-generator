# Fingerprint-Based Payload Customizer

A sophisticated system for encoding payloads unique to target system fingerprints. This module provides fingerprint-locked execution, environment-specific delivery, and polymorphic payload generation.

**Security Context**: Authorized security research and penetration testing only.

## Overview

The Fingerprint Payload Customizer enables:

- **Fingerprint-Locked Execution**: Payloads execute only on matching target fingerprints
- **Environment-Specific Encoding**: Platform-aware payload encoding (PE, ELF, Mach-O)
- **Polymorphic Variants**: Generate multiple payload variants from single source
- **Stealth Decoders**: Multi-language payload decoders with built-in fingerprint verification
- **Anti-Analysis Wrapping**: Environment-aware wrappers that detect analysis
- **Metadata Tracking**: Comprehensive security audit trails

## Features

### 1. Fingerprint-Based Encryption

```javascript
const customizer = new FingerprintPayloadCustomizer({
  fingerprintHash: 'target-system-hash'
});

// Generate encryption key unique to target fingerprint
const key = customizer.generateFingerprintKey(targetFingerprint);

// Generate IV unique to target fingerprint
const iv = customizer.generateFingerprintIV(targetFingerprint);
```

**Key Derivation**:
- PBKDF2 with 100,000 iterations
- SHA256 hashing
- 32-byte keys (256-bit AES)
- 16-byte initialization vectors

### 2. Fingerprint Lock Creation

Lock payloads to specific system fingerprints with expiration:

```javascript
const lock = customizer.createFingerprintLock(payload, targetFingerprint, {
  lockType: 'strict',                    // strict, flexible, hardware-only
  requireExactMatch: true,               // exact fingerprint match required
  expirationTime: 86400000,              // 24 hours
  metadata: {
    targetId: 'target-123',
    campaignId: 'op-2024',
    operator: 'security-team'
  }
});
```

**Lock Types**:
- `strict`: Exact fingerprint match required
- `flexible`: Allow minor deviations
- `hardware-only`: Match only hardware components

### 3. Payload Customization

Customize payloads for specific target environments:

```javascript
const customized = customizer.customizeForTarget(
  payload,
  {
    platform: 'linux',
    architecture: 'x64',
    osVersion: '5.10.0',
    processorInfo: { model: 'Intel i7', cores: 8 },
    memoryInfo: { total: 16384 },
    networkInfo: { interfaces: 2 }
  },
  fingerprintHash
);
```

**Supported Platforms**:
- Windows (PE format, x86/x64)
- Linux (ELF format, x86_64/arm64)
- macOS (Mach-O format, x86_64/arm64)
- Generic (Base64 wrapper)

### 4. Polymorphic Variants

Generate multiple fingerprint-aware variants from single payload:

```javascript
const variants = customizer.createPolymorphicVariants(
  payload,
  fingerprintHashes,
  {
    variantCount: 5,              // variants per fingerprint
    minVariation: 0.3,            // 30% minimum variation
    includeDecoys: true,          // add dummy payloads
    decoyCount: 2                 // decoy payloads
  }
);
```

**Variant Features**:
- Unique encryption per variant
- Randomized byte injection
- Decoy payload generation
- Configurable variation level

### 5. Stealth Decoders

Generate platform-specific decoders with built-in fingerprint verification:

```javascript
// JavaScript decoder
const jsDecoder = customizer.createStealthDecoder(
  payload,
  targetFingerprint,
  'js'
);

// Python decoder
const pyDecoder = customizer.createStealthDecoder(
  payload,
  targetFingerprint,
  'py'
);

// C++ decoder
const cppDecoder = customizer.createStealthDecoder(
  payload,
  targetFingerprint,
  'cpp'
);

// Go decoder
const goDecoder = customizer.createStealthDecoder(
  payload,
  targetFingerprint,
  'go'
);
```

**Decoder Features**:
- Fingerprint validation before execution
- AES-256-CBC decryption
- Base64 payload encoding
- Multi-language support

### 6. Environment-Aware Wrapping

Create wrappers that detect environment and validate execution:

```javascript
const wrapped = customizer.createEnvironmentAwareWrapper(
  payload,
  targetFingerprint
);
```

**Anti-Analysis Features**:
- Anti-debugger checks
- Anti-VM detection
- Fingerprint validation
- Runtime environment checks

### 7. Delivery Profiles

Platform-specific delivery configurations:

```javascript
// Windows Profile
{
  name: 'Windows Target',
  encoding: 'pe-native',
  evasion: ['dll-injection', 'process-hollowing', 'code-cave'],
  arch: ['x86', 'x64'],
  obfuscation: ['string-encryption', 'api-obfuscation', 'control-flow']
}

// Linux Profile
{
  name: 'Linux Target',
  encoding: 'elf-native',
  evasion: ['ld-preload', 'ptrace-evasion', 'seccomp-bypass'],
  arch: ['x86_64', 'arm64'],
  obfuscation: ['symbol-stripping', 'binary-packing']
}

// macOS Profile
{
  name: 'macOS Target',
  encoding: 'mach-o-native',
  evasion: ['code-signing-bypass', 'gatekeeper-bypass'],
  arch: ['x86_64', 'arm64'],
  obfuscation: ['entitlement-modification']
}
```

## Usage Examples

### Example 1: Basic Linux Customization

```javascript
const customizer = new FingerprintPayloadCustomizer({
  fingerprintHash: 'linux-target-hash-123'
});

const customized = customizer.customizeForTarget(
  payload,
  {
    platform: 'linux',
    architecture: 'x64',
    osVersion: '5.10.0-8-generic'
  },
  'linux-target-hash-123'
);

console.log(`Customization ID: ${customized.id}`);
console.log(`Profile: ${customized.profile.name}`);
console.log(`Encoding: ${customized.profile.encoding}`);
```

### Example 2: Windows Fingerprint Lock

```javascript
const lock = customizer.createFingerprintLock(
  payload,
  'windows-10-target',
  {
    lockType: 'strict',
    expirationTime: 86400000,
    metadata: {
      targetName: 'WORKSTATION-007',
      targetDomain: 'example.com'
    }
  }
);

console.log(`Lock ID: ${lock.id}`);
console.log(`Expires: ${new Date(lock.metadata.expirationTime)}`);
```

### Example 3: Multi-Stage Payload

```javascript
// Stage 1: Stager
const stager = customizer.customizeForTarget(stagerPayload, profile, fp);

// Stage 2: Main
const main = customizer.customizeForTarget(mainPayload, profile, fp);

// Stage 3: PostEx
const postex = customizer.customizeForTarget(postexPayload, profile, fp);

// Create execution chain
const chain = {
  stages: [stager, main, postex],
  sequenceId: 'multistage-' + Date.now(),
  targetEnvironment: profile
};
```

### Example 4: Generate Stealth Decoder

```javascript
const jsDecoder = customizer.createStealthDecoder(
  payload,
  targetFingerprint,
  'js'
);

// Save decoder to file
fs.writeFileSync('decoder.js', jsDecoder);

// Usage in target:
// const crypto = require('crypto');
// const payload = decodePayload(targetFingerprint);
// payload.execute();
```

### Example 5: Export Customizations

```javascript
const exported = customizer.exportCustomizations();

// Contains:
// - Customization IDs and metadata
// - Lock information
// - Available delivery profiles
// - Platform-specific configurations

fs.writeFileSync(
  'customizations.json',
  JSON.stringify(exported, null, 2)
);
```

## API Reference

### Constructor Options

```javascript
new FingerprintPayloadCustomizer({
  fingerprintHash: string,           // System fingerprint hash
  fingerprintData: Object,           // Detailed fingerprint info
  encryptionAlgorithm: string,       // Default: 'aes-256-cbc'
  compressionLevel: number           // 1-9, default: 6
})
```

### Core Methods

#### `generateFingerprintKey(fingerprint, salt)`
Generate 32-byte encryption key from fingerprint.

#### `generateFingerprintIV(fingerprint, index)`
Generate 16-byte IV from fingerprint.

#### `createFingerprintLock(payload, fingerprint, options)`
Create fingerprint-locked payload.

#### `customizeForTarget(payload, profile, fingerprint)`
Customize payload for target environment.

#### `createPolymorphicVariants(payload, fingerprints, options)`
Generate multiple fingerprint-aware variants.

#### `createEnvironmentAwareWrapper(payload, fingerprint)`
Wrap payload with anti-analysis code.

#### `createStealthDecoder(payload, fingerprint, language)`
Generate language-specific decoder.

#### `verifyPayloadFingerprint(payload, fingerprint)`
Verify payload matches fingerprint.

#### `generateFingerprintReport(payloadId)`
Generate detailed fingerprint report.

#### `exportCustomizations()`
Export all customizations for transport.

## Security Considerations

### 1. Fingerprint Stability

Fingerprints should include stable system characteristics:
- CPU model and core count
- OS version
- System architecture
- Network interface count
- RAM capacity

Avoid volatile characteristics that change frequently.

### 2. Key Management

- Fingerprint keys are derived using PBKDF2
- 100,000 iterations recommended
- Never transmit raw fingerprint data
- Use hashed fingerprints in transport

### 3. Expiration Times

Always set appropriate expiration times:
- Short-term operations: 1-24 hours
- Medium-term campaigns: 1-7 days
- Long-term persistence: 30-90 days

### 4. Metadata Tracking

Include audit metadata:
- Campaign ID
- Operator ID
- Target identification
- Execution timestamps
- Callback information

### 5. Polymorphic Variants

Generate multiple variants for evasion:
- Different variants per fingerprint
- Minimum 30% variation recommended
- Include decoy payloads
- Randomize delivery timing

## Testing

Run comprehensive test suite:

```bash
node src/fingerprint-payload-customizer.test.js
```

**Test Coverage** (20 tests):
- Instantiation and configuration
- Key and IV generation
- Fingerprint lock creation
- Payload customization
- Polymorphic variants
- Environment-aware wrapping
- Stealth decoders (JS, Python, C++, Go)
- Fingerprint verification
- Report generation
- Export functionality
- Delivery profiles
- Multiple fingerprints
- Metadata preservation
- Encryption algorithms
- Compression levels

## Examples

Run comprehensive examples:

```bash
node src/fingerprint-payload-customizer-examples.js
```

**10 Example Scenarios**:
1. Basic Linux customization
2. Windows fingerprint lock
3. Multi-fingerprint polymorphic variants
4. Environment-aware wrapper
5. Stealthy decoders (multi-language)
6. Fingerprint report generation
7. Export customizations for deployment
8. Multi-stage payload customization
9. Fingerprint-based delivery selection
10. Security metadata tracking

## Integration with File Obfuscator

Works seamlessly with FileObfuscator:

```javascript
const FileObfuscator = require('./file-obfuscator');
const FingerprintPayloadCustomizer = require('./fingerprint-payload-customizer');

// Obfuscate file
const obfuscator = new FileObfuscator();
const obfuscated = obfuscator.obfuscate(filePath, outputDir);

// Customize with fingerprint
const customizer = new FingerprintPayloadCustomizer();
const customized = customizer.customizeForTarget(
  obfuscated.metadata.payload,
  targetProfile,
  targetFingerprint
);
```

## Performance Characteristics

- Key generation: ~50ms (PBKDF2 100k iterations)
- IV generation: ~1ms
- Payload encryption: ~5-10ms for 1MB payload
- Compression: ~20-50ms for 1MB payload
- Variant generation: ~100ms for 5 variants
- Decoder generation: ~5ms

## File Structure

```
src/
├── fingerprint-payload-customizer.js          # Main class (500+ lines)
├── fingerprint-payload-customizer.test.js     # 20 comprehensive tests
└── fingerprint-payload-customizer-examples.js # 10 usage examples
```

## License

For authorized security research and penetration testing only.

## Support

For issues or questions:
- Review test cases for API usage
- Check examples for implementation patterns
- Verify fingerprint format and hashing
- Validate target profile configuration

## Version

Version 1.0 - Released 2024

## Related Components

- **FileObfuscator**: File obfuscation techniques
- **FingerprintManager** (Python): System fingerprint collection
- **PayloadEncoder**: Generic payload encoding

---

**Disclaimer**: This tool is provided for authorized security testing only. Unauthorized use may be illegal. Always obtain proper authorization before conducting security research or penetration testing.
