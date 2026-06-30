# Fingerprint Hash Generator - Documentation

## Overview

The **Fingerprint Hash Generator** is a comprehensive cryptographic hashing system for anonymized user tracking and device identification. It provides multiple hashing algorithms, session management, privacy-preserving features, and cross-device identity linking capabilities.

### Key Features

- **Multiple Hash Algorithms**: SHA256, SHA512, PBKDF2, BLAKE2b
- **Session Management**: Temporary session-based hashes with expiration
- **Persistent Identification**: Stable device-level hashes for long-term tracking
- **Anonymous Tracking**: Privacy-preserving hashes with PII removal
- **Fingerprint Comparison**: Similarity analysis between fingerprints
- **Cross-Device Linking**: Link multiple devices under single identity
- **Comprehensive Reporting**: Detailed fingerprint analysis and variants

---

## Installation and Setup

### Import

```javascript
const FingerprintHashGenerator = require('./fingerprint-hash-generator');

// Initialize generator
const generator = new FingerprintHashGenerator({
  defaultHashAlgorithm: 'sha256',
  saltSource: 'fingerprint-salt',
  hashRounds: 100000,
  includeUserAgent: true,
  includeTimezone: true
});
```

### Configuration Options

```javascript
{
  // Hash algorithm: 'sha256' | 'sha512' | 'pbkdf2' | 'blake2b512'
  defaultHashAlgorithm: 'sha256',
  
  // Salt source for deterministic generation
  saltSource: 'fingerprint-salt',
  
  // PBKDF2 iteration rounds (higher = more secure, slower)
  hashRounds: 100000,
  
  // Include user agent in fingerprint
  includeUserAgent: true,
  
  // Include timezone in fingerprint
  includeTimezone: true
}
```

---

## Core Methods

### 1. Basic Hash Generation

Generate a hash from fingerprint data.

```javascript
const fingerprint = {
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
  language: 'en-US',
  platform: 'Win32',
  screen: { width: 1920, height: 1080 }
};

const hash = generator.generateHash(fingerprint, {
  algorithm: 'sha256',
  salt: 'optional-custom-salt',
  encoding: 'hex'
});

// Output: 64-character hex string (for SHA256)
// "d3a633e64438d698ee9fcbfd13d0350f4d0f94558e0928d3f4be5cae5a7bba59"
```

### 2. Hash Variants

Generate multiple hash variants with different algorithms.

```javascript
const variants = generator.generateHashVariants(fingerprint, {
  algorithms: ['sha256', 'sha512', 'pbkdf2'],
  salts: null, // Optional custom salts
  includePartial: true,
  partialDepth: 2
});

// Output structure:
// {
//   full: {
//     sha256: "...",
//     sha512: "...",
//     pbkdf2: "..."
//   },
//   partial: {
//     level_0: "...",
//     level_1: "..."
//   },
//   metadata: {
//     fingerprintedAt: 1656453743920,
//     componentCount: 4
//   }
// }
```

### 3. Session-Based Tracking

Create temporary session hashes that expire.

```javascript
const sessionHash = generator.generateSessionHash(fingerprint, 3600000);

// Output:
// {
//   sessionId: "a29621a957bf8d136b528729d7494dbe",
//   hash: "8973c1ea8507eb6799357c0713832e03...",
//   createdAt: 1656453743920,
//   expiresAt: 1656457343920,
//   fingerprintHash: "...",
//   isActive: true
// }
```

**Use Cases:**
- Tracking users during browser sessions (30 min - 24 hours)
- Shopping carts and temporary state
- API rate limiting per session
- Temporary device verification

### 4. Persistent Device Identification

Create stable hashes for long-term device tracking.

```javascript
const persistentHash = generator.generatePersistentHash(fingerprint);

// Output:
// {
//   deviceId: "device-3a84532521fde7da",
//   hash: "e1adb8bbd3c7c9a93f82c27b10baea95...",
//   createdAt: 1656453743920,
//   fingerprintHash: "...",
//   stable: true,
//   algorithm: 'pbkdf2'
// }
```

**Key Features:**
- Uses PBKDF2 with 100,000 iterations for enhanced security
- Stable device ID that survives browser cache clears
- Can recreate same hash with stored device ID
- Suitable for return visitor identification

### 5. Anonymous Tracking

Generate hashes with privacy protections.

```javascript
const fingerprint = {
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
  email: 'user@example.com',      // PII
  ipAddress: '192.168.1.1',        // Identifier
  location: 'New York'              // Sensitive
};

const anonHash = generator.generateAnonymousHash(fingerprint, {
  removeDirectIdentifiers: true,    // Remove email, IP, etc
  removeSensitiveData: true,        // Remove location, medical, etc
  truncateHash: true,               // Limit hash length
  truncateLength: 16
});

// Output:
// {
//   hash: "8cb50396c7023bee",
//   anonymizedAt: 1656453743920,
//   anonFingerprintHash: "...",
//   componentCount: 3,
//   directIdentifiersRemoved: true,
//   sensitiveDataRemoved: true,
//   truncated: true,
//   truncateLength: 16
// }
```

**Privacy Features:**
- Removes direct identifiers (email, phone, IP, etc)
- Removes sensitive data (location, medical, financial)
- Optional hash truncation
- GDPR and privacy regulation compliant

### 6. Fingerprint Comparison

Compare two fingerprints to determine similarity.

```javascript
const fp1 = {
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
  platform: 'Win32',
  language: 'en-US'
};

const fp2 = {
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
  platform: 'Win32',
  language: 'en-US'
};

const comparison = generator.compareFingerprints(fp1, fp2, {
  algorithm: 'sha256',
  sensitivity: 'strict'  // 'strict', 'moderate', 'loose'
});

// Output:
// {
//   exactMatch: true,
//   similarity: 1.0,
//   hashDistance: 0,
//   consideredEqual: true,
//   sensitivity: 'strict',
//   hash1: "d0ed45b3e611578b5ef5d4b8...",
//   hash2: "d0ed45b3e611578b5ef5d4b8..."
// }
```

**Sensitivity Levels:**
- `strict`: Exact hash match required
- `moderate`: >85% similarity and hash distance < 5
- `loose`: >70% component similarity

### 7. Cross-Device Linking

Link multiple fingerprints under a single identity.

```javascript
const fingerprints = [
  { userAgent: 'Chrome', platform: 'Windows' },
  { userAgent: 'Safari', platform: 'iPhone' },
  { userAgent: 'Firefox', platform: 'Linux' }
];

const crossover = generator.generateCrossoverHash(fingerprints);

// Output:
// {
//   linkId: "2d4e9d397c0e98f1ed769229950efcfe",
//   hash: "0720f91be47c638bc52717a52a0a0685...",
//   linkedFingerprintCount: 3,
//   linkedAt: 1656453743920,
//   componentHashes: ["...", "...", "..."],
//   algorithm: 'sha256'
// }
```

**Use Cases:**
- Cross-device user tracking
- Linking desktop, mobile, tablet
- Account recovery verification
- Multi-device authentication

### 8. Fingerprint Verification

Verify if current fingerprint matches stored hash.

```javascript
const storedHash = "d3a633e64438d698ee9fcbfd13d0350f4d0f94558e0928d3f4be5cae5a7bba59";

const verification = generator.verifyFingerprint(fingerprint, storedHash, {
  algorithm: 'sha256',
  tolerance: 0
});

// Output:
// {
//   isValid: true,
//   exactMatch: true,
//   similarity: 1.0,
//   withinTolerance: true,
//   verifiedAt: 1656453743920,
//   algorithm: 'sha256'
// }
```

### 9. Comprehensive Reports

Generate detailed fingerprint analysis.

```javascript
const report = generator.generateFingerprintReport(fingerprint, {
  includeVariants: true,
  includeComponents: true,
  includeAnonymous: true
});

// Output includes:
// - Primary hash
// - Component count
// - Integrity checksum
// - Hash variants (SHA256, SHA512, PBKDF2)
// - Anonymous version
// - Timestamp metadata
```

### 10. Session Management

Clean up expired sessions for privacy/performance.

```javascript
const clearedCount = generator.clearExpiredSessions();
console.log(`Cleaned ${clearedCount} expired sessions`);
```

### 11. Export and Analytics

Export all hashes and sessions.

```javascript
const exported = generator.exportHashes();

// Output:
// {
//   exportedAt: 1656453743920,
//   hashes: {
//     "hash-id-1": { algorithm: 'sha256', timestamp: ..., hashPreview: '...' },
//     "hash-id-2": { algorithm: 'sha512', timestamp: ..., hashPreview: '...' }
//   },
//   sessions: {
//     "session-1": { createdAt: ..., expiresAt: ..., sessionHash: '...' }
//   },
//   statistics: {
//     totalHashes: 2,
//     activeSessions: 1,
//     cachedFingerprints: 0
//   }
// }
```

---

## Fingerprint Data Structure

### Standard Fingerprint Components

```javascript
{
  // Browser/Device Info
  userAgent: string,
  platform: string,
  language: string,
  timezone: string,
  
  // Hardware Info
  hardwareConcurrency: number,
  deviceMemory: number,
  
  // Display Info
  screen: {
    width: number,
    height: number,
    colorDepth: number,
    pixelDepth: number
  },
  
  // Optional Components
  plugins: Array,
  fonts: Array,
  canvas: string,
  webgl: string,
  localStorage: boolean,
  indexedDb: boolean,
  sessionStorage: boolean,
  doNotTrack: string
}
```

---

## Hash Algorithms Comparison

| Algorithm | Length | Speed | Security | Use Case |
|-----------|--------|-------|----------|----------|
| SHA256 | 64 chars | Fast | Good | General purpose, sessions |
| SHA512 | 128 chars | Fast | Excellent | Security-critical |
| PBKDF2 | 128 chars | Slow | Excellent | Persistent device tracking |
| BLAKE2b | 128 chars | Fast | Excellent | Modern systems |

---

## Privacy and Compliance

### GDPR Compliance

✓ Anonymous hash generation removes PII
✓ Session-based tracking with expiration
✓ Configurable data retention
✓ Export functionality for user data portability

### Privacy Best Practices

```javascript
// 1. Use anonymous hashes for non-essential tracking
const anonHash = generator.generateAnonymousHash(fingerprint, {
  removeDirectIdentifiers: true,
  removeSensitiveData: true,
  truncateHash: true
});

// 2. Implement session expiration
const session = generator.generateSessionHash(fingerprint, 1800000); // 30 min

// 3. Clear expired sessions regularly
const interval = setInterval(() => {
  const cleared = generator.clearExpiredSessions();
}, 3600000); // Every hour

// 4. Communicate to users
// "We use device fingerprinting to prevent fraud and improve security"
```

---

## Use Cases and Examples

### 1. E-Commerce Fraud Detection

```javascript
class FraudDetector {
  constructor() {
    this.generator = new FingerprintHashGenerator();
    this.knownDevices = new Map();
  }

  registerDevice(fingerprint) {
    const persistent = this.generator.generatePersistentHash(fingerprint);
    this.knownDevices.set(persistent.deviceId, persistent);
    return persistent.deviceId;
  }

  verifyTransaction(fingerprint, userId) {
    const persistent = this.generator.generatePersistentHash(fingerprint);
    const stored = this.knownDevices.get(persistent.deviceId);
    
    if (!stored) {
      return { trusted: false, reason: 'Unknown device' };
    }
    
    const verified = this.generator.verifyFingerprint(fingerprint, stored.hash);
    return {
      trusted: verified.isValid,
      deviceId: persistent.deviceId,
      userId: userId
    };
  }
}
```

### 2. Analytics with Privacy

```javascript
class PrivacyAwareAnalytics {
  constructor() {
    this.generator = new FingerprintHashGenerator();
    this.events = [];
  }

  trackEvent(fingerprint, eventName, eventData) {
    const anonHash = this.generator.generateAnonymousHash(fingerprint, {
      removeDirectIdentifiers: true,
      truncateHash: true,
      truncateLength: 12
    });

    this.events.push({
      fingerprint: anonHash.hash,
      event: eventName,
      data: eventData,
      timestamp: Date.now()
    });
  }

  getAnonymousStats() {
    const uniqueUsers = new Set(this.events.map(e => e.fingerprint)).size;
    const eventCounts = {};
    
    this.events.forEach(e => {
      eventCounts[e.event] = (eventCounts[e.event] || 0) + 1;
    });

    return { uniqueUsers, eventCounts };
  }
}
```

### 3. Device Verification on Login

```javascript
class DeviceVerification {
  constructor() {
    this.generator = new FingerprintHashGenerator();
    this.trustedDevices = new Map();
  }

  storeTrustedDevice(userId, fingerprint) {
    const persistent = this.generator.generatePersistentHash(fingerprint);
    const key = `${userId}:${persistent.deviceId}`;
    this.trustedDevices.set(key, persistent.hash);
  }

  isTrustedDevice(userId, fingerprint) {
    const persistent = this.generator.generatePersistentHash(fingerprint);
    const key = `${userId}:${persistent.deviceId}`;
    
    if (!this.trustedDevices.has(key)) {
      return { trusted: false, requiresMFA: true };
    }

    const stored = this.trustedDevices.get(key);
    const verified = this.generator.verifyFingerprint(fingerprint, stored);
    
    return {
      trusted: verified.isValid,
      requiresMFA: !verified.isValid
    };
  }
}
```

---

## Testing

Run the comprehensive test suite:

```bash
node src/fingerprint-hash-generator.test.js
```

Test coverage includes:
- Basic hash generation
- Algorithm consistency
- Session management
- Persistent identification
- Anonymous tracking
- Fingerprint comparison
- Cross-device linking
- Verification
- Report generation
- Session expiration
- Export functionality
- Large fingerprint handling

---

## Performance Considerations

### Hash Generation Speed

- **SHA256**: ~0.1ms per hash
- **SHA512**: ~0.1ms per hash
- **PBKDF2**: ~50-100ms per hash (100,000 iterations)
- **BLAKE2b**: ~0.1ms per hash

### Memory Usage

- Generator instance: ~1-2 MB
- 1,000 stored hashes: ~500 KB - 1 MB
- Export data: ~10-50 KB for typical dataset

### Optimization Tips

```javascript
// Batch hash generation
const hashes = fingerprints.map(fp => 
  generator.generateHash(fp)
);

// Clear old sessions periodically
setInterval(() => {
  generator.clearExpiredSessions();
}, 3600000);

// Use salt caching for repeated fingerprints
const cachedFingerprints = new Map();
```

---

## Security Considerations

### Hash Collisions

- SHA256: Cryptographically secure (2^128 resistance)
- SHA512: Even stronger (2^256 resistance)
- PBKDF2: Additional protection through key derivation

### Salt Handling

- Automatic salt generation from fingerprint data
- Supports custom salts for additional entropy
- Salt stored with hash for verification

### Timing Attacks

- All hash operations use constant-time algorithms
- Comparison functions are timing-safe

---

## Examples

Run comprehensive examples:

```bash
node src/fingerprint-hash-generator-examples.js
```

Includes 10 detailed examples:
1. Basic fingerprint hashing
2. Multiple hash algorithms
3. Session-based tracking
4. Persistent device identification
5. Anonymous tracking
6. Fingerprint comparison
7. Cross-device linking
8. Fingerprint verification
9. Comprehensive reports
10. Privacy-aware analytics implementation

---

## API Reference

### Constructor

```javascript
new FingerprintHashGenerator(options)
```

### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `generateHash()` | (fingerprint, options) | string | Basic hash generation |
| `generateHashVariants()` | (fingerprint, options) | Object | Multiple algorithm variants |
| `generateSessionHash()` | (fingerprint, duration) | Object | Temporary session hash |
| `generatePersistentHash()` | (fingerprint, deviceId) | Object | Stable device hash |
| `generateAnonymousHash()` | (fingerprint, options) | Object | Privacy-preserving hash |
| `compareFingerprints()` | (fp1, fp2, options) | Object | Similarity comparison |
| `generateCrossoverHash()` | (fingerprints, linkId) | Object | Multi-device linking |
| `verifyFingerprint()` | (fingerprint, storedHash, options) | Object | Hash verification |
| `generateFingerprintReport()` | (fingerprint, options) | Object | Detailed analysis |
| `exportHashes()` | () | Object | Export all data |
| `clearExpiredSessions()` | () | number | Clean expired sessions |

---

## License and Usage

**Security Context**: Analytics and user tracking for authorized applications

Suitable for:
- E-commerce fraud detection
- User analytics and statistics
- Device verification and trust scoring
- Cross-device tracking
- Session management
- Return visitor identification

Must be used in compliance with:
- GDPR and privacy regulations
- User consent requirements
- Data retention policies
- Local laws and regulations

---

## Troubleshooting

### Q: Hash values differ each time
**A**: This is normal if using automatically generated salts. Store the salt with the hash for reproducibility.

### Q: PBKDF2 is too slow
**A**: Reduce `hashRounds` option (trade security for speed), or use SHA256 for less critical uses.

### Q: Sessions not expiring
**A**: Call `clearExpiredSessions()` periodically or implement background cleanup.

### Q: Anonymous hash still too identifying
**A**: Use truncation and remove more components. Consider random noise injection.

---

## Version History

- **1.0.0** (2024-06): Initial release
  - Basic hash generation (SHA256, SHA512, PBKDF2)
  - Session and persistent hashing
  - Anonymous tracking with PII removal
  - Fingerprint comparison and verification
  - Cross-device linking
  - Comprehensive reporting

---

## Support and Feedback

For issues, feature requests, or questions:
- Review examples and documentation
- Check test suite for expected behavior
- Consult privacy regulations for compliance
