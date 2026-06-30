/**
 * Fingerprint Hash Generator - Examples
 *
 * Comprehensive examples demonstrating:
 * - Basic hash generation
 * - Session management
 * - Fingerprint comparison
 * - Anonymous tracking
 * - Identity linking
 * - Persistence strategies
 */

const FingerprintHashGenerator = require('./fingerprint-hash-generator');

class FingerprintHashGeneratorExamples {
  constructor() {
    this.generator = new FingerprintHashGenerator();
  }

  /**
   * Example 1: Basic fingerprint hashing
   * Creates hashes from browser fingerprint data
   */
  example1_BasicHashing() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 1: Basic Fingerprint Hashing');
    console.log('='.repeat(70));

    // Browser fingerprint data
    const fingerprint = {
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      language: 'en-US',
      platform: 'Win32',
      hardwareConcurrency: 8,
      deviceMemory: 16,
      timezone: 'America/New_York',
      screen: {
        width: 1920,
        height: 1080,
        colorDepth: 24,
        pixelDepth: 24
      }
    };

    console.log('Fingerprint Data:');
    console.log(JSON.stringify(fingerprint, null, 2));

    // Generate hash
    const hash = this.generator.generateHash(fingerprint);
    console.log('\nGenerated Hash (SHA256):');
    console.log(hash);
    console.log(`Hash Length: ${hash.length} characters`);
  }

  /**
   * Example 2: Multiple hash algorithms
   * Compare different hashing algorithms
   */
  example2_MultipleAlgorithms() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 2: Multiple Hash Algorithms');
    console.log('='.repeat(70));

    const fingerprint = {
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      platform: 'Win32',
      language: 'en-US'
    };

    const algorithms = ['sha256', 'sha512', 'pbkdf2'];

    console.log('Fingerprint:');
    console.log(JSON.stringify(fingerprint, null, 2));

    console.log('\nHash Results:');
    algorithms.forEach(algo => {
      const hash = this.generator.generateHash(fingerprint, { algorithm: algo });
      console.log(`\n${algo.toUpperCase()}:`);
      console.log(`  Value: ${hash.substring(0, 64)}${hash.length > 64 ? '...' : ''}`);
      console.log(`  Length: ${hash.length}`);
    });
  }

  /**
   * Example 3: Session-based tracking
   * Create temporary session hashes for current session
   */
  example3_SessionTracking() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 3: Session-Based Tracking');
    console.log('='.repeat(70));

    const fingerprint = {
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)',
      platform: 'iPhone',
      language: 'en-US'
    };

    // Create 1-hour session
    const sessionHash = this.generator.generateSessionHash(fingerprint, 3600000);

    console.log('Session Information:');
    console.log(`  Session ID: ${sessionHash.sessionId}`);
    console.log(`  Session Hash: ${sessionHash.hash.substring(0, 32)}...`);
    console.log(`  Created: ${new Date(sessionHash.createdAt).toISOString()}`);
    console.log(`  Expires: ${new Date(sessionHash.expiresAt).toISOString()}`);
    console.log(`  Active: ${sessionHash.isActive}`);
    console.log(`  Duration: 1 hour`);

    // Multiple sessions in same service
    const fp1 = { userAgent: 'Chrome', device: 'Desktop' };
    const fp2 = { userAgent: 'Safari', device: 'iPad' };

    const session1 = this.generator.generateSessionHash(fp1, 3600000);
    const session2 = this.generator.generateSessionHash(fp2, 3600000);

    console.log('\nMultiple Sessions Example:');
    console.log(`Session 1 (Desktop): ${session1.sessionId.substring(0, 16)}...`);
    console.log(`Session 2 (iPad):    ${session2.sessionId.substring(0, 16)}...`);
  }

  /**
   * Example 4: Persistent device identification
   * Create stable device hashes for long-term tracking
   */
  example4_PersistentIdentification() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 4: Persistent Device Identification');
    console.log('='.repeat(70));

    const fingerprint = {
      userAgent: 'Mozilla/5.0 (X11; Linux x86_64)',
      platform: 'Linux',
      hardwareConcurrency: 4,
      deviceMemory: 8,
      timezone: 'Europe/London',
      screen: { width: 2560, height: 1440 }
    };

    // Create persistent device hash
    const persistentHash = this.generator.generatePersistentHash(fingerprint);

    console.log('Persistent Device Hash:');
    console.log(`  Device ID: ${persistentHash.deviceId}`);
    console.log(`  Hash: ${persistentHash.hash.substring(0, 32)}...`);
    console.log(`  Algorithm: ${persistentHash.algorithm}`);
    console.log(`  Created: ${new Date(persistentHash.createdAt).toISOString()}`);
    console.log(`  Stable: ${persistentHash.stable}`);

    // Recreate with same device ID
    const persistentHash2 = this.generator.generatePersistentHash(
      fingerprint,
      persistentHash.deviceId
    );

    console.log('\nRecreated Hash with Same Device ID:');
    console.log(`  Same Device ID: ${persistentHash2.deviceId === persistentHash.deviceId}`);
    console.log(`  Same Hash: ${persistentHash2.hash === persistentHash.hash}`);
  }

  /**
   * Example 5: Anonymous tracking
   * Generate hashes with identifiers removed for privacy
   */
  example5_AnonymousTracking() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 5: Anonymous Tracking');
    console.log('='.repeat(70));

    const originalFingerprint = {
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      language: 'en-US',
      platform: 'Win32',
      timezone: 'America/New_York',
      email: 'user@example.com',     // PII
      ipAddress: '192.168.1.100',    // Identifier
      location: 'New York, USA',     // Sensitive
      userId: '12345'                 // Direct identifier
    };

    console.log('Original Fingerprint (with PII):');
    console.log(`  Components: ${Object.keys(originalFingerprint).join(', ')}`);
    console.log(`  Total: ${Object.keys(originalFingerprint).length} properties`);

    // Generate anonymous hash
    const anonHash = this.generator.generateAnonymousHash(originalFingerprint, {
      removeDirectIdentifiers: true,
      removeSensitiveData: true,
      truncateHash: false
    });

    console.log('\nAnonymized Hash Result:');
    console.log(`  Hash: ${anonHash.hash.substring(0, 32)}...`);
    console.log(`  Components: ${anonHash.componentCount}`);
    console.log(`  Direct IDs Removed: ${anonHash.directIdentifiersRemoved}`);
    console.log(`  Sensitive Data Removed: ${anonHash.sensitiveDataRemoved}`);

    // Generate truncated anonymous hash
    const truncatedHash = this.generator.generateAnonymousHash(originalFingerprint, {
      removeDirectIdentifiers: true,
      removeSensitiveData: true,
      truncateHash: true,
      truncateLength: 16
    });

    console.log('\nTruncated Anonymous Hash (16 chars):');
    console.log(`  Hash: ${truncatedHash.hash}`);
    console.log(`  Truncated: ${truncatedHash.truncated}`);
  }

  /**
   * Example 6: Fingerprint comparison
   * Compare two fingerprints to determine similarity
   */
  example6_FingerprintComparison() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 6: Fingerprint Comparison');
    console.log('='.repeat(70));

    const fp_desktop_session1 = {
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      platform: 'Win32',
      language: 'en-US',
      screen: { width: 1920, height: 1080 },
      timezone: 'America/New_York'
    };

    const fp_desktop_session2 = {
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      platform: 'Win32',
      language: 'en-US',
      screen: { width: 1920, height: 1080 },
      timezone: 'America/New_York'
    };

    const fp_different_device = {
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6)',
      platform: 'iPhone',
      language: 'en-US',
      screen: { width: 390, height: 844 },
      timezone: 'America/Los_Angeles'
    };

    // Compare same device across sessions
    console.log('Comparison 1: Same Device Across Sessions');
    const result1 = this.generator.compareFingerprints(
      fp_desktop_session1,
      fp_desktop_session2
    );
    console.log(`  Exact Match: ${result1.exactMatch}`);
    console.log(`  Similarity: ${(result1.similarity * 100).toFixed(2)}%`);
    console.log(`  Considered Equal: ${result1.consideredEqual}`);

    // Compare different devices
    console.log('\nComparison 2: Desktop vs Mobile');
    const result2 = this.generator.compareFingerprints(
      fp_desktop_session1,
      fp_different_device,
      { sensitivity: 'moderate' }
    );
    console.log(`  Exact Match: ${result2.exactMatch}`);
    console.log(`  Similarity: ${(result2.similarity * 100).toFixed(2)}%`);
    console.log(`  Considered Equal: ${result2.consideredEqual}`);
  }

  /**
   * Example 7: Cross-device identity linking
   * Link multiple fingerprints under single identity
   */
  example7_CrossDeviceLinking() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 7: Cross-Device Identity Linking');
    console.log('='.repeat(70));

    const fingerprints = [
      {
        name: 'Desktop Chrome',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        platform: 'Win32',
        screen: { width: 1920, height: 1080 }
      },
      {
        name: 'Mobile Safari',
        userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6)',
        platform: 'iPhone',
        screen: { width: 390, height: 844 }
      },
      {
        name: 'Tablet Chrome',
        userAgent: 'Mozilla/5.0 (Linux; Android 11)',
        platform: 'Android',
        screen: { width: 768, height: 1024 }
      }
    ];

    // Create crossover hash linking all devices
    const fpData = fingerprints.map(({ name, ...fp }) => fp);
    const crossover = this.generator.generateCrossoverHash(fpData);

    console.log('Linked Devices:');
    fingerprints.forEach((fp, idx) => {
      console.log(`  ${idx + 1}. ${fp.name}`);
    });

    console.log('\nCrossover Hash:');
    console.log(`  Link ID: ${crossover.linkId}`);
    console.log(`  Hash: ${crossover.hash.substring(0, 32)}...`);
    console.log(`  Linked Fingerprints: ${crossover.linkedFingerprintCount}`);
    console.log(`  Created: ${new Date(crossover.linkedAt).toISOString()}`);
    console.log(`  Algorithm: ${crossover.algorithm}`);
  }

  /**
   * Example 8: Fingerprint verification
   * Verify if current fingerprint matches stored hash
   */
  example8_FingerprintVerification() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 8: Fingerprint Verification');
    console.log('='.repeat(70));

    // Initial fingerprint at login
    const initialFingerprint = {
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      platform: 'Win32',
      language: 'en-US',
      screen: { width: 1920, height: 1080 }
    };

    // Generate and store hash
    const storedHash = this.generator.generateHash(initialFingerprint);
    console.log('Initial Fingerprint Hash Generated:');
    console.log(`  Hash: ${storedHash.substring(0, 32)}...`);

    // Same user, same session
    const currentFingerprint1 = {
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      platform: 'Win32',
      language: 'en-US',
      screen: { width: 1920, height: 1080 }
    };

    const verify1 = this.generator.verifyFingerprint(currentFingerprint1, storedHash);
    console.log('\nVerification 1: Same Fingerprint');
    console.log(`  Valid: ${verify1.isValid}`);
    console.log(`  Similarity: ${(verify1.similarity * 100).toFixed(2)}%`);

    // Different fingerprint (upgraded browser)
    const currentFingerprint2 = {
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/92',
      platform: 'Win32',
      language: 'en-US',
      screen: { width: 1920, height: 1080 }
    };

    const verify2 = this.generator.verifyFingerprint(currentFingerprint2, storedHash);
    console.log('\nVerification 2: Different Fingerprint');
    console.log(`  Valid: ${verify2.isValid}`);
    console.log(`  Similarity: ${(verify2.similarity * 100).toFixed(2)}%`);
  }

  /**
   * Example 9: Comprehensive fingerprint report
   * Generate detailed fingerprint analysis report
   */
  example9_FingerprintReport() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 9: Comprehensive Fingerprint Report');
    console.log('='.repeat(70));

    const fingerprint = {
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      language: 'en-US',
      platform: 'Win32',
      timezone: 'America/New_York',
      hardwareConcurrency: 8,
      deviceMemory: 16,
      screen: { width: 1920, height: 1080, colorDepth: 24 }
    };

    const report = this.generator.generateFingerprintReport(fingerprint, {
      includeVariants: true,
      includeComponents: true,
      includeAnonymous: true
    });

    console.log('Fingerprint Report:');
    console.log(`  Generated: ${new Date(report.generatedAt).toISOString()}`);
    console.log(`  Primary Hash: ${report.primaryHash.substring(0, 32)}...`);
    console.log(`  Components: ${report.componentCount}`);
    console.log(`  Checksum: ${report.integrity.checksum.substring(0, 16)}...`);
    console.log(`  Data Size: ${report.integrity.dataSize} bytes`);

    console.log('\nHash Variants:');
    console.log(`  SHA256: ${report.variants.full.sha256.substring(0, 16)}...`);
    console.log(`  SHA512: ${report.variants.full.sha512.substring(0, 16)}...`);

    console.log('\nAnonymous Hash:');
    console.log(`  Hash: ${report.anonymous.hash.substring(0, 16)}...`);
    console.log(`  Components: ${report.anonymous.componentCount}`);
  }

  /**
   * Example 10: Privacy-aware analytics implementation
   * Complete example of privacy-preserving user tracking
   */
  example10_PrivacyAwareAnalytics() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 10: Privacy-Aware Analytics Implementation');
    console.log('='.repeat(70));

    class PrivacyAwareAnalytics {
      constructor() {
        this.generator = new FingerprintHashGenerator();
        this.sessions = new Map();
        this.events = [];
      }

      // Collect user fingerprint with PII
      collectFingerprint(userData) {
        const fingerprint = {
          userAgent: userData.userAgent,
          platform: userData.platform,
          language: userData.language,
          timezone: userData.timezone,
          screen: userData.screen
        };

        // Create anonymous hash
        const anonHash = this.generator.generateAnonymousHash(fingerprint, {
          removeDirectIdentifiers: true,
          truncateHash: true,
          truncateLength: 12
        });

        // Create session
        const session = this.generator.generateSessionHash(fingerprint, 1800000); // 30 min

        return {
          sessionId: session.sessionId,
          anonymousHash: anonHash.hash,
          timestamp: Date.now()
        };
      }

      // Track event
      trackEvent(sessionId, eventName, properties = {}) {
        this.events.push({
          sessionId,
          eventName,
          properties,
          timestamp: Date.now()
        });
      }

      // Generate analytics report
      generateReport() {
        return {
          totalEvents: this.events.length,
          uniqueSessions: new Set(this.events.map(e => e.sessionId)).size,
          events: this.events
        };
      }
    }

    // Usage
    const analytics = new PrivacyAwareAnalytics();

    const userData = {
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      platform: 'Win32',
      language: 'en-US',
      timezone: 'America/New_York',
      screen: { width: 1920, height: 1080 }
    };

    const tracking = analytics.collectFingerprint(userData);

    console.log('Session Created:');
    console.log(`  Session ID: ${tracking.sessionId}`);
    console.log(`  Anonymous Hash: ${tracking.anonymousHash}`);

    // Track events
    analytics.trackEvent(tracking.sessionId, 'page_view', { page: '/home' });
    analytics.trackEvent(tracking.sessionId, 'button_click', { button: 'signup' });
    analytics.trackEvent(tracking.sessionId, 'page_view', { page: '/about' });

    const report = analytics.generateReport();
    console.log('\nAnalytics Report:');
    console.log(`  Total Events: ${report.totalEvents}`);
    console.log(`  Unique Sessions: ${report.uniqueSessions}`);
  }

  /**
   * Run all examples
   */
  runAll() {
    console.log('\n' + '█'.repeat(70));
    console.log('█ Fingerprint Hash Generator - Complete Examples');
    console.log('█'.repeat(70));

    this.example1_BasicHashing();
    this.example2_MultipleAlgorithms();
    this.example3_SessionTracking();
    this.example4_PersistentIdentification();
    this.example5_AnonymousTracking();
    this.example6_FingerprintComparison();
    this.example7_CrossDeviceLinking();
    this.example8_FingerprintVerification();
    this.example9_FingerprintReport();
    this.example10_PrivacyAwareAnalytics();

    console.log('\n' + '█'.repeat(70));
    console.log('█ Examples Complete');
    console.log('█'.repeat(70) + '\n');
  }
}

/**
 * Run examples
 */
if (require.main === module) {
  const examples = new FingerprintHashGeneratorExamples();
  examples.runAll();
}

module.exports = FingerprintHashGeneratorExamples;
