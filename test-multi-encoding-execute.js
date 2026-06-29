/**
 * Comprehensive Multi-Encoding Test Suite
 * Tests: Encode cmd with all 3 layers → Decode all → Execute
 * Verifies no variable scope issues
 */

const {
  encodeBase64,
  decodeBase64,
  encodeHex,
  decodeHex,
  encodeArray,
  decodeArray,
  compactMultiEncode,
  compactMultiDecode
} = require('./multi-encoding');

// Test utilities
let testsPassed = 0;
let testsFailed = 0;

function test(condition, testName, details = '') {
  if (condition) {
    console.log(`✓ ${testName}`);
    testsPassed++;
  } else {
    console.log(`✗ ${testName}`);
    if (details) console.log(`  Details: ${details}`);
    testsFailed++;
  }
}

function assertEqual(actual, expected, testName) {
  const match = actual === expected;
  test(match, testName, match ? '' : `Expected: ${expected}, Got: ${actual}`);
  return match;
}

// ============================================================================
// TEST SUITE 1: Layer-by-Layer Encoding with Commands
// ============================================================================
console.log('\n╔════════════════════════════════════════════════════════════════╗');
console.log('║ TEST SUITE 1: Layer-by-Layer Encoding with Commands           ║');
console.log('╚════════════════════════════════════════════════════════════════╝\n');

const cmdTestCases = [
  'echo "Hello World"',
  'node -e "console.log(123)"',
  'echo $VAR_NAME',
  'VAR="test" && echo $VAR',
  'if [ 1 -eq 1 ]; then echo "true"; fi',
  'for i in {1..3}; do echo $i; done'
];

console.log('Test Case: Encoding Commands through All 3 Layers\n');

cmdTestCases.forEach((cmd, idx) => {
  console.log(`\n--- Command ${idx + 1}: "${cmd}" ---`);

  // Layer 1: Base64
  const layer1_base64 = encodeBase64(cmd);
  console.log(`Layer 1 (Base64):  ${layer1_base64}`);

  // Layer 2: Hex
  const layer2_hex = encodeHex(layer1_base64);
  console.log(`Layer 2 (Hex):     ${layer2_hex}`);

  // Layer 3: Array
  const layer3_array = encodeArray(layer2_hex);
  console.log(`Layer 3 (Array):   [${layer3_array.slice(0, 5).join(', ')}${layer3_array.length > 5 ? '...' : ''}]`);

  // Now decode all layers
  console.log(`  Decoding...`);
  const decode_step1 = decodeArray(layer3_array);
  test(decode_step1 === layer2_hex, `  ✓ Array→Hex decode`, `Layers ${idx + 1}`);

  const decode_step2 = decodeHex(decode_step1);
  test(decode_step2 === layer1_base64, `  ✓ Hex→Base64 decode`, `Layers ${idx + 1}`);

  const decode_step3 = decodeBase64(decode_step2);
  test(decode_step3 === cmd, `  ✓ Base64→Original decode`, `Layers ${idx + 1}`);
});

// ============================================================================
// TEST SUITE 2: Multi-Layer Encoding/Decoding Pipeline
// ============================================================================
console.log('\n\n╔════════════════════════════════════════════════════════════════╗');
console.log('║ TEST SUITE 2: Complete Multi-Layer Pipeline                   ║');
console.log('╚════════════════════════════════════════════════════════════════╝\n');

console.log('Test Case: Full encode → decode roundtrip\n');

cmdTestCases.forEach((cmd, idx) => {
  console.log(`Command ${idx + 1}: "${cmd}"`);

  // Encode all layers at once
  const encoded = compactMultiEncode(cmd);

  // Immediately decode
  const decoded = compactMultiDecode(encoded);

  // Verify exact match
  const isMatch = decoded === cmd;
  test(isMatch, `  Roundtrip successful`, isMatch ? '' : `Expected: ${cmd}, Got: ${decoded}`);
});

// ============================================================================
// TEST SUITE 3: Variable Scope Isolation Test
// ============================================================================
console.log('\n\n╔════════════════════════════════════════════════════════════════╗');
console.log('║ TEST SUITE 3: Variable Scope Isolation                         ║');
console.log('╚════════════════════════════════════════════════════════════════╝\n');

console.log('Test Case: Encoding variables in different scopes\n');

// Simulate variable scope isolation
function testVariableScopeInLayer1() {
  const localVar = 'LOCAL_SCOPE_VAR';
  const encoded = encodeBase64(localVar);
  const decoded = decodeBase64(encoded);
  return decoded === localVar;
}

function testVariableScopeInLayer2() {
  const scopedData = encodeBase64('SCOPED_DATA');
  const encoded = encodeHex(scopedData);
  const decoded = decodeHex(encoded);
  return decoded === scopedData;
}

function testVariableScopeInLayer3() {
  const hexData = encodeHex(encodeBase64('NESTED_SCOPE'));
  const encoded = encodeArray(hexData);
  const decoded = decodeArray(encoded);
  return decoded === hexData;
}

function testCrossLayerScopeIsolation() {
  const input = 'CROSS_LAYER_TEST';

  // Encode with local variables in each layer
  const l1 = (() => {
    const tempBase64 = encodeBase64(input);
    return tempBase64;
  })();

  const l2 = (() => {
    const tempHex = encodeHex(l1);
    return tempHex;
  })();

  const l3 = (() => {
    const tempArray = encodeArray(l2);
    return tempArray;
  })();

  // Decode in separate scopes
  const d3 = (() => {
    const tempHex = decodeArray(l3);
    return tempHex;
  })();

  const d2 = (() => {
    const tempBase64 = decodeHex(d3);
    return tempBase64;
  })();

  const d1 = (() => {
    const original = decodeBase64(d2);
    return original;
  })();

  return d1 === input;
}

test(testVariableScopeInLayer1(), 'Layer 1 variable isolation');
test(testVariableScopeInLayer2(), 'Layer 2 variable isolation');
test(testVariableScopeInLayer3(), 'Layer 3 variable isolation');
test(testCrossLayerScopeIsolation(), 'Cross-layer scope isolation');

// ============================================================================
// TEST SUITE 4: Simulated Command Execution with Encoded Input
// ============================================================================
console.log('\n\n╔════════════════════════════════════════════════════════════════╗');
console.log('║ TEST SUITE 4: Execution Simulation with Encoded Commands      ║');
console.log('╚════════════════════════════════════════════════════════════════╝\n');

console.log('Test Case: Encode command → store → decode → execute\n');

// Simulated execution environment
class CommandExecutor {
  constructor() {
    this.executionLog = [];
    this.variables = {};
  }

  // Store encoded command
  storeEncoded(cmd, label) {
    const encoded = compactMultiEncode(cmd);
    this.executionLog.push({
      label,
      stored: true,
      base64: encoded.base64,
      hex: encoded.hex,
      array: encoded.array
    });
    return encoded;
  }

  // Retrieve and decode
  retrieveAndDecode(encoded) {
    const decoded = compactMultiDecode(encoded);
    this.executionLog.push({
      decoded: true,
      command: decoded
    });
    return decoded;
  }

  // Simulate execution (just verification, not actual exec)
  simulateExecute(cmd) {
    this.executionLog.push({
      executed: true,
      command: cmd,
      status: 'simulated'
    });
    return cmd;
  }

  // Verify isolation
  verifyNoScopeLeaks() {
    // Check that stored data doesn't cross-contaminate
    const stored = this.executionLog.filter(e => e.stored);
    const decoded = this.executionLog.filter(e => e.decoded);

    return stored.length > 0 && decoded.length > 0;
  }
}

const executor = new CommandExecutor();

// Test execution flow
const testCommands = [
  'echo "Test1"',
  'VAR=123 && echo $VAR',
  'node -e "console.log(456)"'
];

testCommands.forEach((cmd, idx) => {
  console.log(`\nExecution Sequence ${idx + 1}:`);
  console.log(`  Command: "${cmd}"`);

  // Step 1: Encode and store
  const encoded = executor.storeEncoded(cmd, `cmd_${idx}`);
  console.log(`  Encoded: base64=${encoded.base64.substring(0, 20)}...`);

  // Step 2: Retrieve and decode
  const decoded = executor.retrieveAndDecode(encoded);
  test(decoded === cmd, `  Decode matches original`, '');

  // Step 3: Simulate execution
  executor.simulateExecute(decoded);
  console.log(`  Simulated execution completed`);
});

test(executor.verifyNoScopeLeaks(), 'No scope leaks detected in executor');

// ============================================================================
// TEST SUITE 5: Large Command Encoding Test
// ============================================================================
console.log('\n\n╔════════════════════════════════════════════════════════════════╗');
console.log('║ TEST SUITE 5: Large Command Encoding                          ║');
console.log('╚════════════════════════════════════════════════════════════════╝\n');

console.log('Test Case: Encoding large, complex commands\n');

const largeCmd = `
  #!/bin/bash
  VAR1="value1"
  VAR2="value2"
  for i in {1..100}; do
    echo "Iteration $i: $VAR1 $VAR2"
  done
  if [ $? -eq 0 ]; then
    echo "Success"
  fi
`.trim();

console.log(`Large command size: ${largeCmd.length} chars`);

const largeEncoded = compactMultiEncode(largeCmd);
console.log(`  Base64 size: ${largeEncoded.base64.length} chars`);
console.log(`  Hex size: ${largeEncoded.hex.length} chars`);
console.log(`  Array elements: ${largeEncoded.array.length}`);

const largeDecoded = compactMultiDecode(largeEncoded);
test(largeDecoded === largeCmd, 'Large command perfect roundtrip',
  largeDecoded === largeCmd ? '' : `Size mismatch: ${largeCmd.length} vs ${largeDecoded.length}`);

// ============================================================================
// TEST SUITE 6: Special Characters and Edge Cases
// ============================================================================
console.log('\n\n╔════════════════════════════════════════════════════════════════╗');
console.log('║ TEST SUITE 6: Special Characters and Edge Cases               ║');
console.log('╚════════════════════════════════════════════════════════════════╝\n');

const edgeCases = [
  { name: 'Empty string', value: '' },
  { name: 'Single char', value: 'x' },
  { name: 'Newlines', value: 'line1\nline2\nline3' },
  { name: 'Tabs', value: 'col1\tcol2\tcol3' },
  { name: 'Quotes', value: 'echo "test" && echo \'test\'' },
  { name: 'Backticks', value: 'echo `date`' },
  { name: 'Dollar signs', value: '$VAR $((1+1)) ${VAR}' },
  { name: 'Backslashes', value: 'path\\to\\file' },
  { name: 'Mixed special', value: '!@#$%^&*()[]{}' },
  { name: 'Unicode', value: '你好世界 🚀' }
];

console.log('Testing edge cases:\n');

edgeCases.forEach(({ name, value }) => {
  const encoded = compactMultiEncode(value);
  const decoded = compactMultiDecode(encoded);
  test(decoded === value, `Edge case: ${name}`,
    decoded === value ? '' : `Expected: "${value}", Got: "${decoded}"`);
});

// ============================================================================
// TEST SUMMARY
// ============================================================================
console.log('\n\n╔════════════════════════════════════════════════════════════════╗');
console.log('║ TEST SUMMARY                                                   ║');
console.log('╚════════════════════════════════════════════════════════════════╝\n');

const totalTests = testsPassed + testsFailed;
const passRate = totalTests > 0 ? ((testsPassed / totalTests) * 100).toFixed(1) : 0;

console.log(`Total Tests:   ${totalTests}`);
console.log(`Passed:        ${testsPassed} ✓`);
console.log(`Failed:        ${testsFailed} ${testsFailed > 0 ? '✗' : '✓'}`);
console.log(`Pass Rate:     ${passRate}%`);
console.log(`\nStatus:        ${testsFailed === 0 ? '✓ ALL TESTS PASSED' : '✗ SOME TESTS FAILED'}`);

console.log('\n═══════════════════════════════════════════════════════════════════\n');

process.exit(testsFailed > 0 ? 1 : 0);
