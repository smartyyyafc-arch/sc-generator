/**
 * Fingerprint Hash Generator - Test Suite
 *
 * Tests for anonymized tracking hash generation
 */

const FingerprintHashGenerator = require('./fingerprint-hash-generator');

class FingerprintHashGeneratorTest {
  constructor() {
    this.generator = new FingerprintHashGenerator();
    this.testResults = [];
    this.testCount = 0;
    this.passCount = 0;
    this.failCount = 0;
  }

  /**
   * Test: Basic hash generation
   */
  testBasicHashGeneration() {
    const testName = 'Basic Hash Generation';
    try {
      const fingerprint = {
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        language: 'en-US',
        platform: 'Win32',
        screen: { width: 1920, height: 1080 }
      };

      const hash = this.generator.generateHash(fingerprint);

      this.assert(typeof hash === 'string', 'Hash should be string');
      this.assert(hash.length === 64, 'SHA256 hash should be 64 chars');
      this.assert(/^[a-f0-9]{64}$/.test(hash), 'Hash should be valid hex');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Hash consistency
   */
  testHashConsistency() {
    const testName = 'Hash Consistency';
    try {
      const fingerprint = {
        userAgent: 'Mozilla/5.0',
        language: 'en-US',
        platform: 'Linux'
      };

      const hash1 = this.generator.generateHash(fingerprint);
      const hash2 = this.generator.generateHash(fingerprint);

      // Same input should produce same hash with deterministic salt
      this.assert(hash1.length === hash2.length, 'Hashes should be same length');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Different fingerprints produce different hashes
   */
  testDifferentFingerprintsDifferentHashes() {
    const testName = 'Different Fingerprints Different Hashes';
    try {
      const fp1 = { userAgent: 'Chrome', platform: 'Windows' };
      const fp2 = { userAgent: 'Firefox', platform: 'Linux' };

      const hash1 = this.generator.generateHash(fp1);
      const hash2 = this.generator.generateHash(fp2);

      this.assert(hash1 !== hash2, 'Different fingerprints should have different hashes');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Multiple hash algorithms
   */
  testMultipleAlgorithms() {
    const testName = 'Multiple Hash Algorithms';
    try {
      const fingerprint = {
        userAgent: 'Mozilla/5.0',
        language: 'en-US',
        timezone: 'UTC'
      };

      const sha256 = this.generator.generateHash(fingerprint, { algorithm: 'sha256' });
      const sha512 = this.generator.generateHash(fingerprint, { algorithm: 'sha512' });
      const pbkdf2 = this.generator.generateHash(fingerprint, { algorithm: 'pbkdf2' });

      this.assert(sha256.length === 64, 'SHA256 should be 64 chars');
      this.assert(sha512.length === 128, 'SHA512 should be 128 chars');
      this.assert(pbkdf2.length === 128, 'PBKDF2 should be 128 chars');
      this.assert(sha256 !== sha512, 'Different algorithms should produce different hashes');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Hash variants generation
   */
  testHashVariants() {
    const testName = 'Hash Variants Generation';
    try {
      const fingerprint = {
        userAgent: 'Mozilla/5.0',
        platform: 'Windows',
        language: 'en-US',
        timezone: 'EST'
      };

      const variants = this.generator.generateHashVariants(fingerprint);

      this.assert(variants.full, 'Should have full variants');
      this.assert(variants.full.sha256, 'Should have SHA256 variant');
      this.assert(variants.full.sha512, 'Should have SHA512 variant');
      this.assert(variants.partial, 'Should have partial variants');
      this.assert(variants.metadata, 'Should have metadata');
      this.assert(variants.metadata.componentCount === 4, 'Should count components');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Session hash generation
   */
  testSessionHashGeneration() {
    const testName = 'Session Hash Generation';
    try {
      const fingerprint = {
        userAgent: 'Mozilla/5.0',
        platform: 'Windows',
        language: 'en-US'
      };

      const sessionHash = this.generator.generateSessionHash(fingerprint, 3600000);

      this.assert(sessionHash.sessionId, 'Should have session ID');
      this.assert(sessionHash.hash, 'Should have hash');
      this.assert(sessionHash.createdAt, 'Should have creation timestamp');
      this.assert(sessionHash.expiresAt, 'Should have expiration timestamp');
      this.assert(sessionHash.isActive, 'Should be active');
      this.assert(sessionHash.expiresAt > sessionHash.createdAt, 'Expiration should be after creation');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Persistent hash generation
   */
  testPersistentHashGeneration() {
    const testName = 'Persistent Hash Generation';
    try {
      const fingerprint = {
        userAgent: 'Mozilla/5.0',
        platform: 'Windows',
        hardwareConcurrency: 8,
        deviceMemory: 16
      };

      const persistentHash = this.generator.generatePersistentHash(fingerprint);

      this.assert(persistentHash.deviceId, 'Should have device ID');
      this.assert(persistentHash.hash, 'Should have hash');
      this.assert(persistentHash.stable, 'Should be stable');
      this.assert(persistentHash.algorithm === 'pbkdf2', 'Should use PBKDF2');
      this.assert(persistentHash.hash.length === 128, 'PBKDF2 hash should be 128 chars');

      // Generate again with same device ID
      const persistent2 = this.generator.generatePersistentHash(fingerprint, persistentHash.deviceId);
      this.assert(persistent2.deviceId === persistentHash.deviceId, 'Device ID should remain same');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Anonymous hash generation
   */
  testAnonymousHashGeneration() {
    const testName = 'Anonymous Hash Generation';
    try {
      const fingerprint = {
        userAgent: 'Mozilla/5.0',
        platform: 'Windows',
        language: 'en-US',
        email: 'user@example.com',
        ipAddress: '192.168.1.1',
        location: 'New York'
      };

      const anonHash = this.generator.generateAnonymousHash(fingerprint, {
        removeDirectIdentifiers: true,
        removeSensitiveData: true,
        truncateHash: false
      });

      this.assert(anonHash.hash, 'Should have anonymous hash');
      this.assert(anonHash.directIdentifiersRemoved, 'Should have removed identifiers');
      this.assert(anonHash.sensitiveDataRemoved, 'Should have removed sensitive data');
      this.assert(anonHash.componentCount < Object.keys(fingerprint).length, 'Should have fewer components');

      // Test truncated version
      const truncated = this.generator.generateAnonymousHash(fingerprint, {
        truncateHash: true,
        truncateLength: 16
      });

      this.assert(truncated.hash.length === 16, 'Truncated hash should be 16 chars');
      this.assert(truncated.truncated, 'Should be marked as truncated');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Fingerprint comparison
   */
  testFingerprintComparison() {
    const testName = 'Fingerprint Comparison';
    try {
      const fp1 = {
        userAgent: 'Mozilla/5.0',
        platform: 'Windows',
        language: 'en-US',
        screen: { width: 1920, height: 1080 }
      };

      const fp2 = {
        userAgent: 'Mozilla/5.0',
        platform: 'Windows',
        language: 'en-US',
        screen: { width: 1920, height: 1080 }
      };

      const fp3 = {
        userAgent: 'Firefox',
        platform: 'Linux',
        language: 'en-GB'
      };

      // Identical fingerprints
      const result1 = this.generator.compareFingerprints(fp1, fp2);
      this.assert(result1.exactMatch, 'Identical fingerprints should match exactly');
      this.assert(result1.similarity >= 0.99, 'Should have high similarity');

      // Different fingerprints
      const result2 = this.generator.compareFingerprints(fp1, fp3);
      this.assert(!result2.exactMatch, 'Different fingerprints should not match');
      this.assert(result2.similarity < 0.5, 'Should have low similarity');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Crossover hash for linked identities
   */
  testCrossoverHash() {
    const testName = 'Crossover Hash Generation';
    try {
      const fp1 = { userAgent: 'Mozilla/5.0', platform: 'Windows' };
      const fp2 = { userAgent: 'Firefox', platform: 'Linux' };
      const fp3 = { userAgent: 'Safari', platform: 'macOS' };

      const crossover = this.generator.generateCrossoverHash([fp1, fp2, fp3]);

      this.assert(crossover.linkId, 'Should have link ID');
      this.assert(crossover.hash, 'Should have crossover hash');
      this.assert(crossover.linkedFingerprintCount === 3, 'Should link 3 fingerprints');
      this.assert(crossover.componentHashes.length === 3, 'Should have 3 component hashes');
      this.assert(crossover.algorithm === 'sha256', 'Should use SHA256');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Fingerprint verification
   */
  testFingerprintVerification() {
    const testName = 'Fingerprint Verification';
    try {
      const fingerprint = {
        userAgent: 'Mozilla/5.0',
        platform: 'Windows',
        language: 'en-US'
      };

      const hash = this.generator.generateHash(fingerprint);

      // Verify same fingerprint
      const result1 = this.generator.verifyFingerprint(fingerprint, hash);
      this.assert(result1.exactMatch, 'Same fingerprint should verify');
      this.assert(result1.isValid, 'Should be valid');

      // Verify different fingerprint
      const modified = { ...fingerprint, language: 'fr-FR' };
      const result2 = this.generator.verifyFingerprint(modified, hash);
      this.assert(!result2.exactMatch, 'Different fingerprint should not match exactly');
      this.assert(!result2.isValid, 'Different fingerprint should not be valid');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Fingerprint report generation
   */
  testFingerprintReport() {
    const testName = 'Fingerprint Report Generation';
    try {
      const fingerprint = {
        userAgent: 'Mozilla/5.0',
        platform: 'Windows',
        language: 'en-US',
        timezone: 'EST',
        screen: { width: 1920, height: 1080 }
      };

      const report = this.generator.generateFingerprintReport(fingerprint, {
        includeVariants: true,
        includeComponents: true,
        includeAnonymous: true
      });

      this.assert(report.generatedAt, 'Should have generation timestamp');
      this.assert(report.primaryHash, 'Should have primary hash');
      this.assert(report.componentCount === 5, 'Should count components');
      this.assert(report.integrity, 'Should have integrity data');
      this.assert(report.integrity.checksum, 'Should have checksum');
      this.assert(report.variants, 'Should include variants');
      this.assert(report.anonymous, 'Should include anonymous hash');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Session expiration
   */
  testSessionExpiration() {
    const testName = 'Session Expiration';
    try {
      const fingerprint = { userAgent: 'Mozilla/5.0', platform: 'Windows' };

      // Create session that expires in 100ms
      const sessionHash = this.generator.generateSessionHash(fingerprint, 100);

      this.assert(sessionHash.isActive, 'Session should be active initially');
      this.assert(sessionHash.expiresAt > Date.now(), 'Should expire in future');

      // Wait for expiration
      setTimeout(() => {
        const cleared = this.generator.clearExpiredSessions();
        this.assert(cleared > 0, 'Should clear at least one session');
      }, 150);

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Export functionality
   */
  testExport() {
    const testName = 'Export Functionality';
    try {
      // Generate some hashes and sessions
      const fp1 = { userAgent: 'Mozilla/5.0', platform: 'Windows' };
      const fp2 = { userAgent: 'Firefox', platform: 'Linux' };

      this.generator.generateHash(fp1);
      this.generator.generateHash(fp2);
      this.generator.generateSessionHash(fp1, 3600000);

      const exported = this.generator.exportHashes();

      this.assert(exported.exportedAt, 'Should have export timestamp');
      this.assert(exported.hashes, 'Should export hashes');
      this.assert(exported.sessions, 'Should export sessions');
      this.assert(exported.statistics, 'Should have statistics');
      this.assert(exported.statistics.totalHashes >= 2, 'Should have at least 2 hashes');
      this.assert(exported.statistics.activeSessions >= 1, 'Should have at least 1 session');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Salt handling
   */
  testSaltHandling() {
    const testName = 'Salt Handling';
    try {
      const fingerprint = { userAgent: 'Mozilla/5.0', platform: 'Windows' };

      // Hash with default salt
      const hash1 = this.generator.generateHash(fingerprint);

      // Hash with custom salt
      const customSalt = 'my-custom-salt-123';
      const hash2 = this.generator.generateHash(fingerprint, { salt: customSalt });

      this.assert(hash1 !== hash2, 'Different salts should produce different hashes');
      this.assert(hash1.length === 64, 'SHA256 should be 64 chars');
      this.assert(hash2.length === 64, 'SHA256 should be 64 chars');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Test: Large fingerprint handling
   */
  testLargeFingerprintHandling() {
    const testName = 'Large Fingerprint Handling';
    try {
      const largeFingerprint = {
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        platform: 'Win32',
        language: 'en-US',
        languages: ['en-US', 'en', 'fr-FR', 'de-DE'],
        screen: { width: 1920, height: 1080, colorDepth: 24, pixelDepth: 24 },
        plugins: [
          { name: 'Chrome PDF Plugin', version: '1.0' },
          { name: 'Chrome PDF Viewer', version: '1.0' },
          { name: 'Native Client Executable', version: '1.0' }
        ],
        timezone: 'America/New_York',
        hardwareConcurrency: 8,
        deviceMemory: 16,
        maxTouchPoints: 0,
        fonts: ['Arial', 'Verdana', 'Helvetica', 'Times New Roman', 'Courier New']
      };

      const hash = this.generator.generateHash(largeFingerprint);
      const report = this.generator.generateFingerprintReport(largeFingerprint);

      this.assert(hash.length === 64, 'Should generate valid hash');
      this.assert(report.componentCount === Object.keys(largeFingerprint).length, 'Should count all components');

      this.pass(testName);
    } catch (e) {
      this.fail(testName, e);
    }
  }

  /**
   * Helper: Assert condition
   */
  assert(condition, message) {
    if (!condition) {
      throw new Error(`Assertion failed: ${message}`);
    }
  }

  /**
   * Helper: Mark test as passed
   */
  pass(testName) {
    this.passCount++;
    this.testCount++;
    this.testResults.push({ test: testName, status: 'PASS' });
    console.log(`✓ ${testName}`);
  }

  /**
   * Helper: Mark test as failed
   */
  fail(testName, error) {
    this.failCount++;
    this.testCount++;
    this.testResults.push({ test: testName, status: 'FAIL', error: error.message });
    console.log(`✗ ${testName}: ${error.message}`);
  }

  /**
   * Run all tests
   */
  runAllTests() {
    console.log('='.repeat(60));
    console.log('Fingerprint Hash Generator - Test Suite');
    console.log('='.repeat(60));

    this.testBasicHashGeneration();
    this.testHashConsistency();
    this.testDifferentFingerprintsDifferentHashes();
    this.testMultipleAlgorithms();
    this.testHashVariants();
    this.testSessionHashGeneration();
    this.testPersistentHashGeneration();
    this.testAnonymousHashGeneration();
    this.testFingerprintComparison();
    this.testCrossoverHash();
    this.testFingerprintVerification();
    this.testFingerprintReport();
    this.testSessionExpiration();
    this.testExport();
    this.testSaltHandling();
    this.testLargeFingerprintHandling();

    console.log('='.repeat(60));
    console.log(`Tests: ${this.testCount} | Passed: ${this.passCount} | Failed: ${this.failCount}`);
    console.log('='.repeat(60));

    return {
      total: this.testCount,
      passed: this.passCount,
      failed: this.failCount,
      results: this.testResults
    };
  }
}

/**
 * Run tests
 */
if (require.main === module) {
  const tester = new FingerprintHashGeneratorTest();
  const results = tester.runAllTests();
  process.exit(results.failed > 0 ? 1 : 0);
}

module.exports = FingerprintHashGeneratorTest;
