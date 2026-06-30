/**
 * Fingerprint Hash Generator
 *
 * Generates cryptographic hashes of system fingerprints for:
 * - Anonymized device tracking
 * - Privacy-preserving identification
 * - Deterministic user identification without PII
 * - Cross-session fingerprint correlation
 *
 * The generator creates multiple hash variants:
 * - Session hashes (temporary, single-use)
 * - Persistent hashes (device-level, stable)
 * - Partial hashes (selective attribute matching)
 * - Salted hashes (enhanced entropy with custom salts)
 *
 * Security Context: Analytics and user tracking for authorized applications
 */

const crypto = require('crypto');

class FingerprintHashGenerator {
  /**
   * Constructor
   * @param {Object} options Configuration options
   * @param {string} options.defaultHashAlgorithm Hash algorithm ('sha256', 'sha512', 'blake2b512')
   * @param {string} options.saltSource Default salt source
   * @param {boolean} options.includeUserAgent Include user agent in hash
   * @param {boolean} options.includeTimezone Include timezone in hash
   * @param {number} options.hashRounds PBKDF2 iteration count
   */
  constructor(options = {}) {
    this.defaultHashAlgorithm = options.defaultHashAlgorithm || 'sha256';
    this.saltSource = options.saltSource || 'fingerprint-salt';
    this.includeUserAgent = options.includeUserAgent !== false;
    this.includeTimezone = options.includeTimezone !== false;
    this.hashRounds = options.hashRounds || 100000;

    // Store generated hashes and metadata
    this.hashes = new Map();
    this.fingerprintCache = new Map();
    this.sessionHashes = new Map();

    // Default fingerprint components
    this.defaultComponents = [
      'userAgent',
      'language',
      'platform',
      'hardwareConcurrency',
      'deviceMemory',
      'timezone',
      'screen',
      'plugins',
      'canvas',
      'webgl',
      'fonts',
      'localStorage',
      'indexedDb',
      'openDatabase',
      'sessionStorage',
      'doNotTrack'
    ];
  }

  /**
   * Generate fingerprint hash from fingerprint data
   *
   * @param {Object} fingerprintData Fingerprint data object
   * @param {Object} options Hash options
   * @returns {string} Generated hash (hex string)
   */
  generateHash(fingerprintData, options = {}) {
    const {
      algorithm = this.defaultHashAlgorithm,
      salt = null,
      rounds = this.hashRounds,
      encoding = 'hex'
    } = options;

    // Serialize fingerprint data
    const dataString = this._serializeFingerprint(fingerprintData);

    // Generate or use provided salt
    let hashSalt = salt;
    if (!hashSalt) {
      hashSalt = this._generateSalt(fingerprintData);
    }

    // Generate hash based on algorithm
    let hash;
    switch (algorithm) {
      case 'sha512':
        hash = this._generateSHA512Hash(dataString, hashSalt);
        break;
      case 'blake2b512':
        hash = this._generateBLAKE2bHash(dataString, hashSalt);
        break;
      case 'pbkdf2':
        hash = this._generatePBKDF2Hash(dataString, hashSalt, rounds);
        break;
      case 'sha256':
      default:
        hash = this._generateSHA256Hash(dataString, hashSalt);
        break;
    }

    // Cache the hash
    const hashId = crypto.randomBytes(16).toString('hex');
    this.hashes.set(hashId, {
      hash,
      algorithm,
      salt: hashSalt,
      fingerprintData,
      timestamp: Date.now()
    });

    return hash;
  }

  /**
   * Generate multiple hash variants for a single fingerprint
   * Useful for matching against different hash versions
   *
   * @param {Object} fingerprintData Fingerprint data
   * @param {Object} options Generation options
   * @returns {Object} Multiple hash variants
   */
  generateHashVariants(fingerprintData, options = {}) {
    const {
      algorithms = ['sha256', 'sha512', 'pbkdf2'],
      salts = null,
      includePartial = true,
      partialDepth = 2
    } = options;

    const variants = {
      full: {},
      partial: {},
      metadata: {
        fingerprintedAt: Date.now(),
        componentCount: Object.keys(fingerprintData).length
      }
    };

    // Generate full hashes with different algorithms
    for (const algo of algorithms) {
      variants.full[algo] = this.generateHash(fingerprintData, {
        algorithm: algo,
        salt: salts ? salts[algo] : null
      });
    }

    // Generate partial hashes for flexible matching
    if (includePartial) {
      variants.partial = this._generatePartialHashes(
        fingerprintData,
        partialDepth
      );
    }

    return variants;
  }

  /**
   * Generate session-specific hash
   * Creates temporary hash valid for current session
   *
   * @param {Object} fingerprintData Fingerprint data
   * @param {number} sessionDuration Session duration in milliseconds
   * @returns {Object} Session hash object
   */
  generateSessionHash(fingerprintData, sessionDuration = 3600000) { // 1 hour default
    const sessionId = crypto.randomBytes(16).toString('hex');
    const sessionSalt = `session-${sessionId}-${Date.now()}`;

    const hash = this.generateHash(fingerprintData, {
      algorithm: 'sha256',
      salt: sessionSalt
    });

    const sessionHash = {
      sessionId,
      hash,
      createdAt: Date.now(),
      expiresAt: Date.now() + sessionDuration,
      fingerprintHash: this._hashString(JSON.stringify(fingerprintData)),
      isActive: true
    };

    this.sessionHashes.set(sessionId, sessionHash);

    return sessionHash;
  }

  /**
   * Generate persistent device hash
   * Creates stable hash for device-level tracking
   *
   * @param {Object} fingerprintData Fingerprint data
   * @param {string} deviceId Custom device identifier
   * @returns {Object} Persistent hash object
   */
  generatePersistentHash(fingerprintData, deviceId = null) {
    const persistentId = deviceId || this._generateDeviceId(fingerprintData);
    const persistentSalt = `persistent-${persistentId}`;

    // Use PBKDF2 for persistent hashes for stronger security
    const hash = this.generateHash(fingerprintData, {
      algorithm: 'pbkdf2',
      salt: persistentSalt,
      rounds: this.hashRounds
    });

    return {
      deviceId: persistentId,
      hash,
      createdAt: Date.now(),
      fingerprintHash: this._hashString(JSON.stringify(fingerprintData)),
      stable: true,
      algorithm: 'pbkdf2'
    };
  }

  /**
   * Generate anonymized tracking hash
   * Creates hash optimized for privacy-preserving tracking
   *
   * @param {Object} fingerprintData Fingerprint data
   * @param {Object} options Anonymization options
   * @returns {Object} Anonymized hash object
   */
  generateAnonymousHash(fingerprintData, options = {}) {
    const {
      removeDirectIdentifiers = true,
      removeSensitiveData = true,
      truncateHash = false,
      truncateLength = 16,
      includeTimestampComponent = true
    } = options;

    // Create anonymized copy
    let anonData = { ...fingerprintData };

    // Remove direct identifiers if requested
    if (removeDirectIdentifiers) {
      anonData = this._removeIdentifiers(anonData);
    }

    // Remove sensitive data if requested
    if (removeSensitiveData) {
      anonData = this._removeSensitiveData(anonData);
    }

    // Generate anonymous hash
    const anonSalt = `anon-${crypto.randomBytes(8).toString('hex')}`;
    let hash = this.generateHash(anonData, {
      algorithm: 'sha256',
      salt: anonSalt
    });

    // Truncate if requested
    if (truncateHash) {
      hash = hash.substring(0, truncateLength);
    }

    return {
      hash,
      anonymizedAt: Date.now(),
      anonFingerprintHash: this._hashString(JSON.stringify(anonData)),
      componentCount: Object.keys(anonData).length,
      directIdentifiersRemoved: removeDirectIdentifiers,
      sensitiveDataRemoved: removeSensitiveData,
      truncated: truncateHash,
      truncateLength: truncateHash ? truncateLength : null
    };
  }

  /**
   * Compare two fingerprints by hash
   * Determines similarity between fingerprints
   *
   * @param {Object} fingerprint1 First fingerprint
   * @param {Object} fingerprint2 Second fingerprint
   * @param {Object} options Comparison options
   * @returns {Object} Comparison results
   */
  compareFingerprints(fingerprint1, fingerprint2, options = {}) {
    const {
      algorithm = this.defaultHashAlgorithm,
      sensitivity = 'strict' // 'strict', 'moderate', 'loose'
    } = options;

    const hash1 = this.generateHash(fingerprint1, { algorithm });
    const hash2 = this.generateHash(fingerprint2, { algorithm });

    // Direct match
    const exactMatch = hash1 === hash2;

    // Similarity score based on components
    const similarity = this._calculateSimilarity(fingerprint1, fingerprint2);

    // Distance between hashes (Levenshtein-like)
    const hashDistance = this._calculateHashDistance(hash1, hash2);

    // Determine if fingerprints are considered equal based on sensitivity
    let considered_equal = false;
    switch (sensitivity) {
      case 'strict':
        considered_equal = exactMatch;
        break;
      case 'moderate':
        considered_equal = exactMatch || (similarity > 0.85 && hashDistance < 5);
        break;
      case 'loose':
        considered_equal = exactMatch || (similarity > 0.7);
        break;
    }

    return {
      exactMatch,
      similarity: Math.round(similarity * 100) / 100,
      hashDistance,
      consideredEqual: considered_equal,
      sensitivity,
      hash1: hash1.substring(0, 16),
      hash2: hash2.substring(0, 16)
    };
  }

  /**
   * Generate crossover hash for linked identities
   * Creates hash linking multiple fingerprints
   *
   * @param {Array<Object>} fingerprints Array of fingerprints to link
   * @param {string} linkId Custom link identifier
   * @returns {Object} Crossover hash object
   */
  generateCrossoverHash(fingerprints, linkId = null) {
    if (!Array.isArray(fingerprints) || fingerprints.length === 0) {
      throw new Error('Fingerprints must be a non-empty array');
    }

    const id = linkId || crypto.randomBytes(16).toString('hex');

    // Create combined fingerprint from all inputs
    const combined = fingerprints.reduce((acc, fp) => {
      return acc + JSON.stringify(fp);
    }, '');

    const crossoverSalt = `crossover-${id}`;
    const hash = this.generateHash(
      { combined, linkId: id },
      { salt: crossoverSalt }
    );

    return {
      linkId: id,
      hash,
      linkedFingerprintCount: fingerprints.length,
      linkedAt: Date.now(),
      componentHashes: fingerprints.map(fp =>
        this._hashString(JSON.stringify(fp))
      ),
      algorithm: 'sha256'
    };
  }

  /**
   * Verify fingerprint matches stored hash
   *
   * @param {Object} fingerprintData Current fingerprint data
   * @param {string} storedHash Hash to compare against
   * @param {Object} options Verification options
   * @returns {Object} Verification result
   */
  verifyFingerprint(fingerprintData, storedHash, options = {}) {
    const {
      algorithm = this.defaultHashAlgorithm,
      tolerance = 0 // Allow minor variations
    } = options;

    const currentHash = this.generateHash(fingerprintData, { algorithm });

    // Exact match
    const isValid = currentHash === storedHash;

    // Similarity check if exact match fails
    let similarity = 0;
    if (!isValid) {
      similarity = this._calculateHashSimilarity(currentHash, storedHash);
    }

    // Check if within tolerance
    const withinTolerance = similarity >= (1 - tolerance);

    return {
      isValid,
      exactMatch: isValid,
      similarity: Math.round(similarity * 10000) / 10000,
      withinTolerance,
      verifiedAt: Date.now(),
      algorithm
    };
  }

  /**
   * Generate comprehensive fingerprint report
   *
   * @param {Object} fingerprintData Fingerprint data
   * @param {Object} options Report options
   * @returns {Object} Comprehensive report
   */
  generateFingerprintReport(fingerprintData, options = {}) {
    const {
      includeVariants = true,
      includeComponents = true,
      includeAnonymous = true
    } = options;

    const report = {
      generatedAt: Date.now(),
      primaryHash: this.generateHash(fingerprintData),
      componentCount: Object.keys(fingerprintData).length,
      components: includeComponents ? fingerprintData : null,
      integrity: {
        checksum: this._hashString(JSON.stringify(fingerprintData)),
        dataSize: JSON.stringify(fingerprintData).length
      }
    };

    if (includeVariants) {
      report.variants = this.generateHashVariants(fingerprintData);
    }

    if (includeAnonymous) {
      report.anonymous = this.generateAnonymousHash(fingerprintData);
    }

    return report;
  }

  /**
   * Export all tracked hashes
   *
   * @returns {Object} Exported hashes and metadata
   */
  exportHashes() {
    const data = {
      exportedAt: Date.now(),
      hashes: {},
      sessions: {},
      statistics: {
        totalHashes: this.hashes.size,
        activeSessions: this.sessionHashes.size,
        cachedFingerprints: this.fingerprintCache.size
      }
    };

    // Export hash metadata (without sensitive data)
    for (const [id, hashData] of this.hashes) {
      data.hashes[id] = {
        algorithm: hashData.algorithm,
        timestamp: hashData.timestamp,
        hashPreview: hashData.hash.substring(0, 16)
      };
    }

    // Export active sessions
    for (const [id, session] of this.sessionHashes) {
      if (session.isActive && session.expiresAt > Date.now()) {
        data.sessions[id] = {
          createdAt: session.createdAt,
          expiresAt: session.expiresAt,
          sessionHash: session.hash.substring(0, 16)
        };
      }
    }

    return data;
  }

  /**
   * Clear expired session hashes
   * Useful for privacy/memory management
   *
   * @returns {number} Number of cleared sessions
   */
  clearExpiredSessions() {
    const now = Date.now();
    let cleared = 0;

    for (const [id, session] of this.sessionHashes) {
      if (session.expiresAt < now) {
        this.sessionHashes.delete(id);
        cleared++;
      }
    }

    return cleared;
  }

  /**
   * Private method: Serialize fingerprint for hashing
   * @private
   */
  _serializeFingerprint(fingerprintData) {
    // Sort keys for consistent serialization
    const sorted = {};
    Object.keys(fingerprintData)
      .sort()
      .forEach(key => {
        sorted[key] = fingerprintData[key];
      });

    return JSON.stringify(sorted);
  }

  /**
   * Private method: Generate salt from fingerprint
   * @private
   */
  _generateSalt(fingerprintData) {
    const dataHash = this._hashString(JSON.stringify(fingerprintData));
    return `${this.saltSource}-${dataHash.substring(0, 16)}`;
  }

  /**
   * Private method: Generate SHA256 hash
   * @private
   */
  _generateSHA256Hash(data, salt) {
    const combined = data + salt;
    return crypto.createHash('sha256')
      .update(combined)
      .digest('hex');
  }

  /**
   * Private method: Generate SHA512 hash
   * @private
   */
  _generateSHA512Hash(data, salt) {
    const combined = data + salt;
    return crypto.createHash('sha512')
      .update(combined)
      .digest('hex');
  }

  /**
   * Private method: Generate BLAKE2b hash
   * @private
   */
  _generateBLAKE2bHash(data, salt) {
    const combined = data + salt;
    // blake2b is available via crypto in newer Node versions
    try {
      return crypto.createHash('blake2b512')
        .update(combined)
        .digest('hex');
    } catch (e) {
      // Fallback to SHA512 if blake2b not available
      return this._generateSHA512Hash(data, salt);
    }
  }

  /**
   * Private method: Generate PBKDF2 hash
   * @private
   */
  _generatePBKDF2Hash(data, salt, rounds) {
    const key = crypto.pbkdf2Sync(data, salt, rounds, 64, 'sha256');
    return key.toString('hex');
  }

  /**
   * Private method: Hash a string directly
   * @private
   */
  _hashString(str) {
    return crypto.createHash('sha256')
      .update(str)
      .digest('hex');
  }

  /**
   * Private method: Generate partial hashes
   * @private
   */
  _generatePartialHashes(fingerprintData, depth) {
    const partial = {};
    const keys = Object.keys(fingerprintData);

    // Generate hash for each subset of data
    for (let i = 0; i < Math.min(depth, keys.length); i++) {
      const subset = {};
      for (let j = 0; j <= i; j++) {
        subset[keys[j]] = fingerprintData[keys[j]];
      }
      partial[`level_${i}`] = this.generateHash(subset);
    }

    return partial;
  }

  /**
   * Private method: Calculate fingerprint similarity
   * @private
   */
  _calculateSimilarity(fp1, fp2) {
    const keys1 = new Set(Object.keys(fp1));
    const keys2 = new Set(Object.keys(fp2));

    const intersection = new Set([...keys1].filter(x => keys2.has(x)));
    const union = new Set([...keys1, ...keys2]);

    let matches = 0;
    for (const key of intersection) {
      if (JSON.stringify(fp1[key]) === JSON.stringify(fp2[key])) {
        matches++;
      }
    }

    return union.size > 0 ? matches / union.size : 0;
  }

  /**
   * Private method: Calculate hash distance (bit-level)
   * @private
   */
  _calculateHashDistance(hash1, hash2) {
    let distance = 0;
    const minLen = Math.min(hash1.length, hash2.length);

    for (let i = 0; i < minLen; i++) {
      if (hash1[i] !== hash2[i]) {
        distance++;
      }
    }

    return distance;
  }

  /**
   * Private method: Calculate hash similarity
   * @private
   */
  _calculateHashSimilarity(hash1, hash2) {
    const distance = this._calculateHashDistance(hash1, hash2);
    const maxLen = Math.max(hash1.length, hash2.length);
    return 1 - (distance / maxLen);
  }

  /**
   * Private method: Generate device ID from fingerprint
   * @private
   */
  _generateDeviceId(fingerprintData) {
    const id = this._hashString(JSON.stringify(fingerprintData));
    return `device-${id.substring(0, 16)}`;
  }

  /**
   * Private method: Remove direct identifiers
   * @private
   */
  _removeIdentifiers(data) {
    const identifierKeys = [
      'macAddress',
      'ipAddress',
      'serialNumber',
      'imei',
      'uuid',
      'userId',
      'email',
      'phone',
      'username'
    ];

    const cleaned = { ...data };
    identifierKeys.forEach(key => {
      delete cleaned[key];
    });

    return cleaned;
  }

  /**
   * Private method: Remove sensitive data
   * @private
   */
  _removeSensitiveData(data) {
    const sensitiveKeys = [
      'location',
      'gps',
      'latitude',
      'longitude',
      'homeAddress',
      'workAddress',
      'personalData',
      'medical',
      'financial',
      'paymentMethod'
    ];

    const cleaned = { ...data };
    sensitiveKeys.forEach(key => {
      delete cleaned[key];
    });

    return cleaned;
  }
}

/**
 * Export
 */
module.exports = FingerprintHashGenerator;

// CLI usage example
if (require.main === module) {
  console.log('Fingerprint Hash Generator');
  console.log('Usage: const FingerprintHashGenerator = require("./fingerprint-hash-generator");');
}
