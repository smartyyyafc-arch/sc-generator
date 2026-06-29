#!/usr/bin/env node

/**
 * Environment Variable Retrieval Handler - Test Suite
 *
 * Comprehensive tests for env var retrieval with fallback paths
 */

const EnvVarRetrievalHandler = require('./env-var-retrieval-handler');

// Test utilities
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
};

function print(text, color = 'reset') {
  console.log(`${colors[color] || ''}${text}${colors.reset}`);
}

function section(title) {
  print('\n' + '='.repeat(70), 'bright');
  print(title, 'cyan');
  print('='.repeat(70), 'bright');
}

function test(name, fn) {
  try {
    fn();
    print(`  ✓ ${name}`, 'green');
    return true;
  } catch (error) {
    print(`  ✗ ${name}`, 'red');
    print(`    Error: ${error.message}`, 'dim');
    return false;
  }
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

// ============================================================================
// TEST SUITE
// ============================================================================

section('TEST 1: Encoding Detection');

const handler1 = new EnvVarRetrievalHandler({ debug: false });

test('Detects hex encoding', () => {
  const hexValue = '48656c6c6f';
  const encoding = handler1.detectEncoding(hexValue);
  assert(encoding === 'hex', `Expected 'hex', got '${encoding}'`);
});

test('Detects base64 encoding', () => {
  const base64Value = 'SGVsbG8gV29ybGQ=';
  const encoding = handler1.detectEncoding(base64Value);
  assert(encoding === 'base64', `Expected 'base64', got '${encoding}'`);
});

test('Returns unknown for unrecognized encoding', () => {
  const unknownValue = 'not-encoded';
  const encoding = handler1.detectEncoding(unknownValue);
  assert(encoding === 'unknown', `Expected 'unknown', got '${encoding}'`);
});

// ============================================================================

section('TEST 2: Chunk Retrieval with Fallback Strategies');

// Set up test environment variables using standard naming
process.env.TESTPREFIX_0 = '48656c6c';
process.env.TESTPREFIX_1 = '6f2c';

const handler2 = new EnvVarRetrievalHandler({ debug: false });

test('Retrieves chunks with standard naming', () => {
  const chunks = handler2.getAllChunks('TESTPREFIX', 10);
  assert(chunks.length === 2, `Expected 2 chunks, got ${chunks.length}`);
  assert(chunks[0].value === '48656c6c', 'First chunk mismatch');
  assert(chunks[1].value === '6f2c', 'Second chunk mismatch');
});

test('Stops at first gap in chunk indices', () => {
  // Don't set TESTPREFIX_2, so it should stop at gap
  const chunks = handler2.getAllChunks('TESTPREFIX', 10);
  assert(chunks.length === 2, `Expected 2 chunks before gap, got ${chunks.length}`);
});

// ============================================================================

section('TEST 3: Payload Reconstruction');

const handler3 = new EnvVarRetrievalHandler({ debug: false });

test('Reconstructs hex to UTF-8 payload', () => {
  // "Hello" in hex: 48656c6c6f
  const chunks = ['48656c6c6f'];
  const payload = handler3.reconstructPayload(chunks);
  assert(payload === 'Hello', `Expected 'Hello', got '${payload}'`);
});

test('Reconstructs multi-chunk hex payload', () => {
  // "Hello, World" split into chunks
  const chunks = ['48656c6c6f', '2c20576f72', '6c64'];
  const payload = handler3.reconstructPayload(chunks);
  assert(payload === 'Hello, World', `Expected 'Hello, World', got '${payload}'`);
});

test('Reconstructs base64 payload', () => {
  // "Test" in base64: VGVzdA==
  const chunks = ['VGVzdA=='];
  const payload = handler3.reconstructPayload(chunks);
  assert(payload === 'Test', `Expected 'Test', got '${payload}'`);
});

// ============================================================================

section('TEST 4: Full Retrieval Workflow');

// Set up test environment
process.env.FULLTEST_0 = '48656c6c';  // "Hell"
process.env.FULLTEST_1 = '6f';        // "o"

const handler4 = new EnvVarRetrievalHandler({ debug: false });

test('Full retrieval with fallback', () => {
  const result = handler4.retrieve('FULLTEST', { useFallback: true });
  assert(result.success === true, `Expected success, got ${result.success}`);
  assert(result.payload === 'Hello', `Expected 'Hello', got '${result.payload}'`);
  assert(result.numChunks === 2, `Expected 2 chunks, got ${result.numChunks}`);
});

test('Returns metadata with retrieval result', () => {
  const result = handler4.retrieve('FULLTEST', { useFallback: true });
  assert(result.metadata !== undefined, 'Metadata missing');
  assert(result.metadata.payloadLength > 0, 'Payload length should be > 0');
  assert(result.metadata.strategies.length > 0, 'Strategies should be identified');
});

// ============================================================================

section('TEST 5: Caching');

process.env.CACHE_TEST_0 = '63616368';  // "cach"
process.env.CACHE_TEST_1 = '65';        // "e"

const handler5 = new EnvVarRetrievalHandler({ cache: true, debug: false });

test('Caches retrieval results', () => {
  const result1 = handler5.retrieve('CACHE_TEST');
  const result2 = handler5.retrieve('CACHE_TEST');
  const stats = handler5.getCacheStats();
  assert(stats.size === 1, `Expected 1 cache entry, got ${stats.size}`);
});

test('Cache can be cleared', () => {
  handler5.retrieve('CACHE_TEST');
  assert(handler5.getCacheStats().size > 0, 'Cache should have entries');
  handler5.clearCache();
  assert(handler5.getCacheStats().size === 0, 'Cache should be empty after clear');
});

// ============================================================================

section('TEST 6: Fallback Strategies');

const handler6 = new EnvVarRetrievalHandler({ debug: false });

test('Supports standard naming: PREFIX_0, PREFIX_1', () => {
  process.env.STRAT1_0 = '61';
  const chunks = handler6.getAllChunks('STRAT1', 5);
  assert(chunks.length > 0, 'Should find standard naming');
  assert(chunks[0].strategy === 'standard', `Expected 'standard', got '${chunks[0].strategy}'`);
});

test('Supports double underscore: PREFIX__0, PREFIX__1', () => {
  process.env.STRAT2__0 = '62';
  const chunks = handler6.getAllChunks('STRAT2', 5);
  assert(chunks.length > 0, 'Should find double underscore naming');
});

test('Supports chunk naming: PREFIX_CHUNK_0, PREFIX_CHUNK_1', () => {
  process.env.STRAT3_CHUNK_0 = '63';
  const chunks = handler6.getAllChunks('STRAT3', 5);
  assert(chunks.length > 0, 'Should find chunk naming');
});

test('Supports data prefixed: PREFIX_DATA_0, PREFIX_DATA_1', () => {
  process.env.STRAT4_DATA_0 = '64';
  const chunks = handler6.getAllChunks('STRAT4', 5);
  assert(chunks.length > 0, 'Should find data prefixed naming');
});

test('Supports no separator: PREFIX0, PREFIX1, PREFIX2', () => {
  process.env.STRAT50 = '65';
  const chunks = handler6.getAllChunks('STRAT5', 5);
  assert(chunks.length > 0, 'Should find no separator naming');
});

test('Supports hex index: PREFIX_0x0, PREFIX_0x1', () => {
  process.env.STRAT6_0x0 = '66';
  const chunks = handler6.getAllChunks('STRAT6', 5);
  assert(chunks.length > 0, 'Should find hex index naming');
});

test('Supports legacy format: XPREFIX_DATA_CHUNK_0', () => {
  process.env.XSTRAT7_DATA_CHUNK_0 = '67';
  const chunks = handler6.getAllChunks('STRAT7', 5);
  assert(chunks.length > 0, 'Should find legacy naming');
});

test('Supports abbreviated: P_0, P_1 (first letter)', () => {
  // Single letter prefix
  process.env.A_0 = '68';
  const chunks = handler6.getAllChunks('ANYTHING', 5);
  assert(chunks.length > 0, 'Should find abbreviated naming');
});

test('Supports Windows format: PREFIX_VAR_0', () => {
  process.env.STRAT9_VAR_0 = '69';
  const chunks = handler6.getAllChunks('STRAT9', 5);
  assert(chunks.length > 0, 'Should find Windows format naming');
});

test('Supports packed format: PREFIXDATA_0', () => {
  process.env.STRAT10DATA_0 = '6a';
  const chunks = handler6.getAllChunks('STRAT10', 5);
  assert(chunks.length > 0, 'Should find packed format naming');
});

// ============================================================================

section('TEST 7: Error Handling');

const handler7 = new EnvVarRetrievalHandler({ throwOnNotFound: false, debug: false });

test('Returns error when no variables found', () => {
  const result = handler7.retrieve('NONEXISTENT_PREFIX_12345', { useFallback: true });
  assert(result.success === false, 'Should return false for non-existent prefix');
  assert(result.error !== undefined, 'Should include error message');
});

const handler7b = new EnvVarRetrievalHandler({ throwOnNotFound: true, debug: false });

test('Throws error when throwOnNotFound is enabled', () => {
  try {
    handler7b.retrieve('NONEXISTENT_PREFIX_THROW_12345', { useFallback: true });
    assert(false, 'Should have thrown error');
  } catch (error) {
    assert(error.message.includes('No variables found'), 'Error message should mention no variables');
  }
});

// ============================================================================

section('TEST 8: Compatibility Report');

process.env.COMPAT_0 = '63';
const handler8 = new EnvVarRetrievalHandler({ debug: false });

test('Generates compatibility report', () => {
  const report = handler8.generateCompatibilityReport('COMPAT');
  assert(report.prefix === 'COMPAT', 'Report should include prefix');
  assert(report.timestamp !== undefined, 'Report should include timestamp');
  assert(report.strategies !== undefined, 'Report should include strategies');
});

test('Report shows all fallback strategies', () => {
  const report = handler8.generateCompatibilityReport('COMPAT');
  const firstIndex = report.strategies['index_0'];
  assert(firstIndex !== undefined, 'Report should have index entries');
  const strategyCount = Object.keys(firstIndex).length;
  assert(strategyCount > 5, `Expected multiple strategies, got ${strategyCount}`);
});

// ============================================================================

section('TEST 9: Raw Mode');

process.env.RAW_0 = '48656c6c';
process.env.RAW_1 = '6f';

const handler9 = new EnvVarRetrievalHandler({ debug: false });

test('Returns raw concatenated data when allowRaw is true', () => {
  const result = handler9.retrieve('RAW', { allowRaw: true });
  assert(result.success === true, 'Should succeed in raw mode');
  assert(result.payload === '48656c6c6f', 'Should concatenate without decoding');
  assert(result.raw === true, 'Should set raw flag');
});

// ============================================================================

section('TEST 10: Payload Validation');

process.env.VALIDATE_0 = '54657374';  // "Test" in hex

const handler10 = new EnvVarRetrievalHandler({ debug: false });

test('Validates payload against checksum', () => {
  const result = handler10.retrieve('VALIDATE');
  const payload = result.payload;

  // Create a valid checksum
  const crypto = require('crypto');
  const validChecksum = crypto.createHash('sha256').update(payload).digest('hex');

  const isValid = handler10.validatePayload(payload, validChecksum);
  assert(isValid === true, 'Valid checksum should validate');
});

test('Invalidates payload with wrong checksum', () => {
  const result = handler10.retrieve('VALIDATE');
  const payload = result.payload;

  // Use wrong checksum
  const wrongChecksum = 'invalid0000000000000000000000000000000000000000000000000000000000';

  const isValid = handler10.validatePayload(payload, wrongChecksum);
  assert(isValid === false, 'Wrong checksum should not validate');
});

// ============================================================================
// SUMMARY
// ============================================================================

section('SUMMARY');

print(`
Integration with env-var-obfuscator:
  1. Use env-var-obfuscator to create obfuscated variables
  2. Use EnvVarRetrievalHandler to retrieve and decode them
  3. Multiple fallback strategies ensure compatibility
  4. Automatic encoding detection (hex, base64)
  5. Caching for performance
  6. Comprehensive error handling

Next Steps:
  - See env-var-retrieval-handler.js for source code
  - See env-var-retrieval-handler.ts for TypeScript version
  - Use with env-var-obfuscator for complete pipeline
`, 'blue');
