# Fingerprint Payload Customizer - Quick Start Guide

## Installation

```javascript
const FingerprintPayloadCustomizer = require('./src/fingerprint-payload-customizer');
```

## 30-Second Example

```javascript
// 1. Create customizer
const customizer = new FingerprintPayloadCustomizer({
  fingerprintHash: 'my-target-system-hash'
});

// 2. Create payload
const payload = Buffer.from('Sensitive data');

// 3. Customize for target
const customized = customizer.customizeForTarget(
  payload,
  {
    platform: 'linux',
    architecture: 'x64',
    osVersion: '5.10.0'
  },
  'my-target-system-hash'
);

console.log('Customized Payload ID:', customized.id);
```

## Common Tasks

### Task 1: Lock Payload to Fingerprint

```javascript
const lock = customizer.createFingerprintLock(
  payload,
  targetFingerprint,
  {
    lockType: 'strict',
    expirationTime: 86400000  // 24 hours
  }
);
```

### Task 2: Generate Decoder

```javascript
const decoder = customizer.createStealthDecoder(
  payload,
  targetFingerprint,
  'js'  // or 'py', 'cpp', 'go'
);

// Use in target:
// decodePayload(targetFingerprint)
```

### Task 3: Create Multiple Variants

```javascript
const variants = customizer.createPolymorphicVariants(
  payload,
  [fingerprint1, fingerprint2, fingerprint3],
  {
    variantCount: 3,
    includeDecoys: true
  }
);
```

### Task 4: Verify Payload

```javascript
const isValid = customizer.verifyPayloadFingerprint(
  customizedPayloadId,
  targetFingerprint
);
```

### Task 5: Generate Report

```javascript
const report = customizer.generateFingerprintReport(
  customizedPayloadId
);

console.log(report);
// {
//   platform: 'linux',
//   architecture: 'x64',
//   profile: {...},
//   obfuscations: [...],
//   checksum: '...'
// }
```

## Platform-Specific Examples

### Windows Target
```javascript
const customized = customizer.customizeForTarget(
  payload,
  {
    platform: 'windows',
    architecture: 'x64',
    osVersion: '10.0.19044'
  },
  fingerprintHash
);
// Uses: PE format, DLL injection, API obfuscation
```

### Linux Target
```javascript
const customized = customizer.customizeForTarget(
  payload,
  {
    platform: 'linux',
    architecture: 'x64',
    osVersion: '5.10.0'
  },
  fingerprintHash
);
// Uses: ELF format, LD_PRELOAD evasion, symbol stripping
```

### macOS Target
```javascript
const customized = customizer.customizeForTarget(
  payload,
  {
    platform: 'macos',
    architecture: 'arm64',
    osVersion: '12.6'
  },
  fingerprintHash
);
// Uses: Mach-O format, code-signing bypass
```

## Key Features at a Glance

| Feature | Method | Output |
|---------|--------|--------|
| Encryption Key | `generateFingerprintKey()` | 32-byte key |
| IV Generation | `generateFingerprintIV()` | 16-byte IV |
| Payload Lock | `createFingerprintLock()` | Lock record |
| Customization | `customizeForTarget()` | Custom payload |
| Variants | `createPolymorphicVariants()` | Multiple variants |
| Wrapper | `createEnvironmentAwareWrapper()` | Wrapped payload |
| Decoder | `createStealthDecoder()` | Language code |
| Verification | `verifyPayloadFingerprint()` | Boolean |
| Report | `generateFingerprintReport()` | Metadata |
| Export | `exportCustomizations()` | JSON data |

## Fingerprint Format

A fingerprint should include:

```javascript
{
  os: 'Linux',           // OS name
  version: '5.10.0',     // OS version
  arch: 'x86_64',        // Architecture
  cpu: 'Intel Core i7',  // CPU model
  cores: 8,              // CPU core count
  ram: 16,               // RAM in GB
  interfaces: 2          // Network interfaces
}
```

## Encryption Details

- **Algorithm**: AES-256-CBC
- **Key Derivation**: PBKDF2 with 100,000 iterations
- **Key Size**: 32 bytes (256-bit)
- **IV Size**: 16 bytes (128-bit)
- **Hash Function**: SHA256

## Testing

```bash
# Run all tests (20 tests, all passing)
node src/fingerprint-payload-customizer.test.js

# Run examples (10 scenarios)
node src/fingerprint-payload-customizer-examples.js
```

## Best Practices

1. **Always set expiration times** for locks
2. **Include metadata** for tracking and auditing
3. **Use platform-specific profiles** for evasion
4. **Generate multiple variants** for different targets
5. **Verify fingerprints** before execution
6. **Keep fingerprints stable** (don't change rapidly)
7. **Hash fingerprints** before transport
8. **Update profiles** regularly for new evasion techniques

## Common Errors

### Error: "Fingerprint not found"
```javascript
// Solution: Initialize customizer with correct fingerprint
new FingerprintPayloadCustomizer({
  fingerprintHash: 'correct-hash-value'
});
```

### Error: "Buffer required"
```javascript
// Solution: Ensure payload is a Buffer
const payload = Buffer.from('string data');  // Correct
const payload = 'string data';               // Wrong
```

### Error: "Invalid platform"
```javascript
// Solution: Use supported platforms
const supported = ['windows', 'linux', 'macos', 'generic'];
```

## Advanced Configuration

```javascript
const customizer = new FingerprintPayloadCustomizer({
  fingerprintHash: 'my-hash',
  fingerprintData: {
    os: 'Linux',
    version: '5.10.0',
    arch: 'x86_64',
    cpu: 'Intel',
    cores: 8,
    ram: 16,
    interfaces: 2
  },
  encryptionAlgorithm: 'aes-256-cbc',  // Only option currently
  compressionLevel: 9                  // 1-9, higher = better compression
});
```

## Multi-Stage Payload Example

```javascript
// Stage 1: Stager (small, initial loader)
const stager = customizer.customizeForTarget(
  stagerPayload, profile, fp
);

// Stage 2: Main payload (large, core functionality)
const main = customizer.customizeForTarget(
  mainPayload, profile, fp
);

// Stage 3: PostEx (cleanup, persistence)
const postex = customizer.customizeForTarget(
  postexPayload, profile, fp
);

// Chain them
const chain = {
  stage1: stager.id,
  stage2: main.id,
  stage3: postex.id
};
```

## Export for Deployment

```javascript
const exported = customizer.exportCustomizations();

// Contains:
// - Customizations (IDs, platforms, hashes)
// - Locks (metadata, checksums)
// - Profiles (evasion, encoding, obfuscation)

fs.writeFileSync('deployment.json', JSON.stringify(exported, null, 2));
```

## Integration with Other Tools

```javascript
const FileObfuscator = require('./file-obfuscator');

// Step 1: Obfuscate file
const obfuscator = new FileObfuscator();
const obfuscated = obfuscator.obfuscate(filePath);

// Step 2: Customize with fingerprint
const customizer = new FingerprintPayloadCustomizer();
const customized = customizer.customizeForTarget(
  obfuscated.metadata.payload,
  targetProfile,
  targetFingerprint
);

// Step 3: Generate decoder
const decoder = customizer.createStealthDecoder(
  customized.encrypted.data,
  targetFingerprint,
  'js'
);
```

## Performance Tips

1. Cache customizer instances for multiple payloads
2. Pre-compute fingerprints for batch operations
3. Use compression for large payloads
4. Generate variants in parallel for speed
5. Export customizations in batches

## Security Reminders

- This tool is for **authorized security testing only**
- Always obtain proper permissions before use
- Include comprehensive audit trails
- Use secure key management
- Rotate fingerprints regularly
- Update evasion techniques frequently
- Monitor payload execution
- Maintain operational security

---

For detailed documentation, see: `FINGERPRINT_CUSTOMIZER_README.md`
