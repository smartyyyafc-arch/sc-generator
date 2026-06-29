/**
 * Fingerprint Payload Customizer - Test Suite
 */

const FingerprintPayloadCustomizer = require('./fingerprint-payload-customizer');
const crypto = require('crypto');
const assert = require('assert');

// Test configuration
const TEST_PAYLOAD = Buffer.from('This is a test payload for fingerprint customization');
const TEST_FINGERPRINT = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';
const TEST_FINGERPRINT_DATA = {
  os: 'Linux',
  version: '5.10.0',
  arch: 'x86_64',
  cpu: 'Intel Core i7',
  cores: 8,
  ram: 16,
  interfaces: 3
};

/**
 * Test 1: Instantiation
 */
function test_instantiation() {
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: TEST_FINGERPRINT,
    fingerprintData: TEST_FINGERPRINT_DATA
  });

  assert(customizer instanceof FingerprintPayloadCustomizer);
  assert(customizer.fingerprintHash === TEST_FINGERPRINT);
  assert(customizer.deliveryProfiles.size > 0);
  assert(customizer.deliveryProfiles.has('windows'));
  assert(customizer.deliveryProfiles.has('linux'));
  assert(customizer.deliveryProfiles.has('macos'));

  console.log('✓ Test 1: Instantiation passed');
}

/**
 * Test 2: Fingerprint key generation
 */
function test_fingerprintKeyGeneration() {
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: TEST_FINGERPRINT
  });

  const key = customizer.generateFingerprintKey(TEST_FINGERPRINT);
  assert(Buffer.isBuffer(key));
  assert(key.length === 32);

  // Same fingerprint should generate same key
  const key2 = customizer.generateFingerprintKey(TEST_FINGERPRINT);
  assert(key.equals(key2));

  // Different fingerprint should generate different key
  const key3 = customizer.generateFingerprintKey('different-fingerprint');
  assert(!key.equals(key3));

  console.log('✓ Test 2: Fingerprint key generation passed');
}

/**
 * Test 3: Fingerprint IV generation
 */
function test_fingerprintIVGeneration() {
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: TEST_FINGERPRINT
  });

  const iv = customizer.generateFingerprintIV(TEST_FINGERPRINT);
  assert(Buffer.isBuffer(iv));
  assert(iv.length === 16);

  // Same fingerprint and index should generate same IV
  const iv2 = customizer.generateFingerprintIV(TEST_FINGERPRINT);
  assert(iv.equals(iv2));

  // Different index should generate different IV
  const iv3 = customizer.generateFingerprintIV(TEST_FINGERPRINT, 1);
  assert(!iv.equals(iv3));

  console.log('✓ Test 3: Fingerprint IV generation passed');
}

/**
 * Test 4: Fingerprint lock creation
 */
function test_fingerprintLockCreation() {
  const customizer = new FingerprintPayloadCustomizer();

  const lock = customizer.createFingerprintLock(TEST_PAYLOAD, TEST_FINGERPRINT, {
    lockType: 'strict',
    requireExactMatch: true,
    expirationTime: 3600000 // 1 hour
  });

  assert(lock.id);
  assert(lock.encrypted);
  assert(lock.metadata);
  assert(lock.metadata.lockType === 'strict');
  assert(lock.metadata.requireExactMatch === true);
  assert(lock.metadata.expirationTime !== null);
  assert(lock.metadata.timestamp);

  // Lock should be stored
  assert(customizer.payloadLocks.has(lock.id));

  console.log('✓ Test 4: Fingerprint lock creation passed');
}

/**
 * Test 5: Payload customization for target
 */
function test_payloadCustomization() {
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: TEST_FINGERPRINT
  });

  const targetProfile = {
    platform: 'linux',
    architecture: 'x64',
    osVersion: '5.10.0',
    processorInfo: { model: 'Intel Core i7', cores: 8 },
    memoryInfo: { total: 16384 },
    networkInfo: { interfaces: 3 }
  };

  const customized = customizer.customizeForTarget(
    TEST_PAYLOAD,
    targetProfile,
    TEST_FINGERPRINT
  );

  assert(customized.id);
  assert(customized.platform === 'linux');
  assert(customized.architecture === 'x64');
  assert(customized.encrypted);
  assert(customized.profile);
  assert(customized.obfuscations);
  assert(customized.timestamp);

  // Customization should be stored
  assert(customizer.customizations.has(customized.id));

  console.log('✓ Test 5: Payload customization passed');
}

/**
 * Test 6: Polymorphic variants creation
 */
function test_polymorphicVariants() {
  const customizer = new FingerprintPayloadCustomizer();

  const fingerprints = [
    TEST_FINGERPRINT,
    'abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890'
  ];

  const variants = customizer.createPolymorphicVariants(
    TEST_PAYLOAD,
    fingerprints,
    {
      variantCount: 2,
      includeDecoys: true,
      decoyCount: 1
    }
  );

  assert(variants.length > 0);
  assert(variants.length >= 4); // 2 fingerprints * 2 variants + 1 decoy = 5

  // Check variant structure
  const variant = variants[0];
  assert(variant.encrypted);

  // Check decoy is present
  const decoy = variants.find(v => v.isDecoy);
  assert(decoy !== undefined);

  console.log('✓ Test 6: Polymorphic variants creation passed');
}

/**
 * Test 7: Environment-aware wrapper creation
 */
function test_environmentAwareWrapper() {
  const customizer = new FingerprintPayloadCustomizer();

  const wrapped = customizer.createEnvironmentAwareWrapper(
    TEST_PAYLOAD,
    TEST_FINGERPRINT
  );

  assert(Buffer.isBuffer(wrapped));
  assert(wrapped.length > TEST_PAYLOAD.length);

  console.log('✓ Test 7: Environment-aware wrapper creation passed');
}

/**
 * Test 8: Stealth decoder generation - JavaScript
 */
function test_stealthDecoderJS() {
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: TEST_FINGERPRINT
  });

  const decoder = customizer.createStealthDecoder(
    TEST_PAYLOAD,
    TEST_FINGERPRINT,
    'js'
  );

  assert(typeof decoder === 'string');
  assert(decoder.includes('decodePayload'));
  assert(decoder.includes('verifyFingerprint'));
  assert(decoder.includes('crypto'));

  console.log('✓ Test 8: Stealth decoder (JS) generation passed');
}

/**
 * Test 9: Stealth decoder generation - Python
 */
function test_stealthDecoderPython() {
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: TEST_FINGERPRINT
  });

  const decoder = customizer.createStealthDecoder(
    TEST_PAYLOAD,
    TEST_FINGERPRINT,
    'py'
  );

  assert(typeof decoder === 'string');
  assert(decoder.includes('def decode_payload'));
  assert(decoder.includes('def verify_fingerprint'));
  assert(decoder.includes('hashlib'));

  console.log('✓ Test 9: Stealth decoder (Python) generation passed');
}

/**
 * Test 10: Stealth decoder generation - C++
 */
function test_stealthDecoderCpp() {
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: TEST_FINGERPRINT
  });

  const decoder = customizer.createStealthDecoder(
    TEST_PAYLOAD,
    TEST_FINGERPRINT,
    'cpp'
  );

  assert(typeof decoder === 'string');
  assert(decoder.includes('decodePayload'));
  assert(decoder.includes('verifyFingerprint'));
  assert(decoder.includes('openssl'));

  console.log('✓ Test 10: Stealth decoder (C++) generation passed');
}

/**
 * Test 11: Stealth decoder generation - Go
 */
function test_stealthDecoderGo() {
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: TEST_FINGERPRINT
  });

  const decoder = customizer.createStealthDecoder(
    TEST_PAYLOAD,
    TEST_FINGERPRINT,
    'go'
  );

  assert(typeof decoder === 'string');
  assert(decoder.includes('func DecodePayload'));
  assert(decoder.includes('func VerifyFingerprint'));
  assert(decoder.includes('crypto/sha256'));

  console.log('✓ Test 11: Stealth decoder (Go) generation passed');
}

/**
 * Test 12: Payload fingerprint verification
 */
function test_payloadVerification() {
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: TEST_FINGERPRINT
  });

  const customized = customizer.customizeForTarget(
    TEST_PAYLOAD,
    {
      platform: 'linux',
      architecture: 'x64'
    },
    TEST_FINGERPRINT
  );

  // Verify by ID and fingerprint
  const isValid = customizer.verifyPayloadFingerprint(
    customized.id,
    TEST_FINGERPRINT
  );
  assert(isValid === true);

  console.log('✓ Test 12: Payload fingerprint verification passed');
}

/**
 * Test 13: Fingerprint report generation
 */
function test_fingerprintReport() {
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: TEST_FINGERPRINT
  });

  const customized = customizer.customizeForTarget(
    TEST_PAYLOAD,
    {
      platform: 'windows',
      architecture: 'x64',
      osVersion: '10.0.19041'
    },
    TEST_FINGERPRINT
  );

  const report = customizer.generateFingerprintReport(customized.id);

  assert(report !== null);
  assert(report.id === customized.id);
  assert(report.platform === 'windows');
  assert(report.architecture === 'x64');
  assert(report.profile);
  assert(report.obfuscations);
  assert(report.checksum);

  console.log('✓ Test 13: Fingerprint report generation passed');
}

/**
 * Test 14: Export customizations
 */
function test_exportCustomizations() {
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: TEST_FINGERPRINT
  });

  // Add some customizations
  customizer.customizeForTarget(
    TEST_PAYLOAD,
    { platform: 'linux', architecture: 'x64' },
    TEST_FINGERPRINT
  );

  customizer.customizeForTarget(
    TEST_PAYLOAD,
    { platform: 'windows', architecture: 'x64' },
    TEST_FINGERPRINT
  );

  const exported = customizer.exportCustomizations();

  assert(exported.customizations);
  assert(exported.locks);
  assert(exported.profiles);
  assert(Object.keys(exported.customizations).length >= 2);
  assert(exported.profiles.windows);
  assert(exported.profiles.linux);
  assert(exported.profiles.macos);

  console.log('✓ Test 14: Export customizations passed');
}

/**
 * Test 15: Delivery profile selection
 */
function test_deliveryProfiles() {
  const customizer = new FingerprintPayloadCustomizer();

  // Test each platform profile
  const platforms = ['windows', 'linux', 'macos', 'generic'];

  for (const platform of platforms) {
    const profile = customizer.deliveryProfiles.get(platform);
    assert(profile !== undefined);
    assert(profile.name);
    assert(profile.encoding);
    assert(Array.isArray(profile.evasion));
    assert(Array.isArray(profile.arch));
    assert(profile.obfuscation);
  }

  console.log('✓ Test 15: Delivery profiles validation passed');
}

/**
 * Test 16: Multiple fingerprint locks
 */
function test_multipleFingerprints() {
  const customizer = new FingerprintPayloadCustomizer();

  const fingerprints = [
    TEST_FINGERPRINT,
    'abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
    'fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210'
  ];

  const locks = [];
  for (const fp of fingerprints) {
    const lock = customizer.createFingerprintLock(TEST_PAYLOAD, fp);
    locks.push(lock);
  }

  assert(locks.length === 3);
  assert(customizer.payloadLocks.size === 3);

  // Each lock should be unique
  const ids = locks.map(l => l.id);
  const uniqueIds = new Set(ids);
  assert(uniqueIds.size === 3);

  console.log('✓ Test 16: Multiple fingerprint locks passed');
}

/**
 * Test 17: Fingerprint data hashing
 */
function test_fingerprintHashing() {
  const customizer = new FingerprintPayloadCustomizer();

  const fp1 = 'test-fingerprint-1';
  const fp2 = 'test-fingerprint-2';

  const hash1 = customizer._hashFingerprint(fp1);
  const hash2 = customizer._hashFingerprint(fp2);

  assert(typeof hash1 === 'string');
  assert(typeof hash2 === 'string');
  assert(hash1 !== hash2);

  // Same input should produce same hash
  const hash1Again = customizer._hashFingerprint(fp1);
  assert(hash1 === hash1Again);

  console.log('✓ Test 17: Fingerprint hashing passed');
}

/**
 * Test 18: Customization metadata preservation
 */
function test_customizationMetadata() {
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: TEST_FINGERPRINT
  });

  const customMetadata = {
    targetId: 'target-12345',
    campaignId: 'campaign-abc',
    stage: 'delivery'
  };

  const lock = customizer.createFingerprintLock(
    TEST_PAYLOAD,
    TEST_FINGERPRINT,
    {
      metadata: customMetadata
    }
  );

  assert(lock.metadata.customMetadata);
  assert(lock.metadata.customMetadata.targetId === 'target-12345');
  assert(lock.metadata.customMetadata.campaignId === 'campaign-abc');

  console.log('✓ Test 18: Customization metadata preservation passed');
}

/**
 * Test 19: Encryption algorithm validation
 */
function test_encryptionAlgorithm() {
  const customizer = new FingerprintPayloadCustomizer({
    encryptionAlgorithm: 'aes-256-cbc'
  });

  const key = customizer.generateFingerprintKey(TEST_FINGERPRINT);
  const iv = customizer.generateFingerprintIV(TEST_FINGERPRINT);

  const encrypted = customizer._encryptPayload(TEST_PAYLOAD, key, iv);

  assert(encrypted.data);
  assert(encrypted.iv);
  assert(encrypted.algorithm === 'aes-256-cbc');

  console.log('✓ Test 19: Encryption algorithm validation passed');
}

/**
 * Test 20: Compression level configuration
 */
function test_compressionLevel() {
  const customizer1 = new FingerprintPayloadCustomizer({
    compressionLevel: 1 // Low compression
  });

  const customizer9 = new FingerprintPayloadCustomizer({
    compressionLevel: 9 // High compression
  });

  assert(customizer1.compressionLevel === 1);
  assert(customizer9.compressionLevel === 9);

  console.log('✓ Test 20: Compression level configuration passed');
}

/**
 * Run all tests
 */
function runAllTests() {
  console.log('\n' + '='.repeat(70));
  console.log('FINGERPRINT PAYLOAD CUSTOMIZER - TEST SUITE');
  console.log('='.repeat(70) + '\n');

  const tests = [
    test_instantiation,
    test_fingerprintKeyGeneration,
    test_fingerprintIVGeneration,
    test_fingerprintLockCreation,
    test_payloadCustomization,
    test_polymorphicVariants,
    test_environmentAwareWrapper,
    test_stealthDecoderJS,
    test_stealthDecoderPython,
    test_stealthDecoderCpp,
    test_stealthDecoderGo,
    test_payloadVerification,
    test_fingerprintReport,
    test_exportCustomizations,
    test_deliveryProfiles,
    test_multipleFingerprints,
    test_fingerprintHashing,
    test_customizationMetadata,
    test_encryptionAlgorithm,
    test_compressionLevel
  ];

  let passed = 0;
  let failed = 0;

  for (const test of tests) {
    try {
      test();
      passed++;
    } catch (error) {
      console.error(`✗ ${test.name} failed:`, error.message);
      failed++;
    }
  }

  console.log('\n' + '='.repeat(70));
  console.log(`RESULTS: ${passed} passed, ${failed} failed out of ${tests.length} tests`);
  console.log('='.repeat(70) + '\n');

  return failed === 0;
}

// Run tests
if (require.main === module) {
  const success = runAllTests();
  process.exit(success ? 0 : 1);
}

module.exports = { runAllTests };
