/**
 * Comprehensive test suite for multi-encoding system
 */

const {
  encodeBase64,
  decodeBase64,
  encodeHex,
  decodeHex,
  encodeArray,
  decodeArray,
  multiEncode,
  multiDecode,
  compactMultiEncode,
  compactMultiDecode
} = require('./multi-encoding');

// Test counter
let testsPassed = 0;
let testsFailed = 0;

function assert(condition, testName) {
  if (condition) {
    console.log(`✓ ${testName}`);
    testsPassed++;
  } else {
    console.log(`✗ ${testName}`);
    testsFailed++;
  }
}

function assertEqual(actual, expected, testName) {
  assert(actual === expected, testName);
  if (actual !== expected) {
    console.log(`  Expected: ${expected}`);
    console.log(`  Got: ${actual}`);
  }
}

function assertArrayEqual(actual, expected, testName) {
  const arrEqual = JSON.stringify(actual) === JSON.stringify(expected);
  assert(arrEqual, testName);
  if (!arrEqual) {
    console.log(`  Expected: ${JSON.stringify(expected)}`);
    console.log(`  Got: ${JSON.stringify(actual)}`);
  }
}

console.log('=== Layer 1: Base64 Encoding/Decoding ===\n');

// Base64 tests
const base64TestCases = [
  'Hello, World!',
  'Test123',
  '',
  'Special chars: @#$%^&*()',
  'Numbers: 0123456789',
  'Multi\nline\ntext'
];

base64TestCases.forEach(testCase => {
  const encoded = encodeBase64(testCase);
  const decoded = decodeBase64(encoded);
  assertEqual(decoded, testCase, `Base64: "${testCase}"`);
});

console.log('\n=== Layer 2: Hex Encoding/Decoding ===\n');

// Hex tests
const hexTestCases = [
  'SGVsbG8sIFdvcmxkIQ==',
  'VGVzdDEyMw==',
  'QQ==',
  ''
];

hexTestCases.forEach(testCase => {
  const encoded = encodeHex(testCase);
  const decoded = decodeHex(encoded);
  assertEqual(decoded, testCase, `Hex: "${testCase}"`);
});

console.log('\n=== Layer 3: Array Encoding/Decoding ===\n');

// Array tests
const arrayTestCases = [
  '534756736247387349466476636d786b49513d3d',
  '56465a48594141',
  '51'
];

arrayTestCases.forEach(testCase => {
  const encoded = encodeArray(testCase);
  const decoded = decodeArray(encoded);
  assertEqual(decoded, testCase, `Array: "${testCase}"`);
});

console.log('\n=== Full Multi-Encoding Pipeline ===\n');

// Full pipeline tests
const fullPipelineTests = [
  'Hello, World!',
  'Quick brown fox',
  '12345',
  'Special: !@#$%^&*()',
  'Empty',
  'a',
  '🚀 Rocket emoji test',
  'Multi\nLine\nString'
];

fullPipelineTests.forEach(testCase => {
  const encoded = multiEncode(testCase);
  const decoded = multiDecode(encoded);
  assertEqual(decoded, testCase, `Full pipeline: "${testCase}"`);
});

console.log('\n=== Compact Encoding/Decoding ===\n');

// Compact version tests
fullPipelineTests.forEach(testCase => {
  const encoded = compactMultiEncode(testCase);
  const decoded = compactMultiDecode(encoded);
  assertEqual(decoded, testCase, `Compact: "${testCase}"`);
});

console.log('\n=== Layer Consistency Tests ===\n');

// Verify encoding chain order
const testInput = 'Chain Test';
const step1 = encodeBase64(testInput);
const step2 = encodeHex(step1);
const step3 = encodeArray(step2);

assertEqual(step1, 'Q2hhaW4gVGVzdA==', 'Base64 step correct');
const hexCheck = encodeHex(step1) === step2;
assert(hexCheck, 'Hex step chains from Base64');
const arrayCheck = JSON.stringify(encodeArray(step2)) === JSON.stringify(step3);
assert(arrayCheck, 'Array step chains from Hex');

// Verify decoding chain order
const reverse3 = decodeArray(step3);
assertEqual(reverse3, step2, 'Array decode produces Hex');
const reverse2 = decodeHex(reverse3);
assertEqual(reverse2, step1, 'Hex decode produces Base64');
const reverse1 = decodeBase64(reverse2);
assertEqual(reverse1, testInput, 'Base64 decode produces original');

console.log('\n=== Edge Cases ===\n');

// Edge cases
const emptyEncoded = encodeBase64('');
const emptyDecoded = decodeBase64(emptyEncoded);
assertEqual(emptyDecoded, '', 'Empty string encoding/decoding');

const singleChar = encodeBase64('A');
const singleDecoded = decodeBase64(singleChar);
assertEqual(singleDecoded, 'A', 'Single character encoding/decoding');

// Very long string
const longString = 'A'.repeat(1000);
const longEncoded = compactMultiEncode(longString);
const longDecoded = compactMultiDecode(longEncoded);
assertEqual(longDecoded, longString, 'Long string (1000 chars) encoding/decoding');

console.log('\n=== Structure Validation ===\n');

// Validate output structures
const sample = compactMultiEncode('Test');
assert(typeof sample.base64 === 'string', 'base64 is string');
assert(typeof sample.hex === 'string', 'hex is string');
assert(Array.isArray(sample.array), 'array is Array');
assert(sample.array.every(x => typeof x === 'string'), 'array elements are strings');

console.log('\n=== Test Summary ===\n');
console.log(`Total tests: ${testsPassed + testsFailed}`);
console.log(`Passed: ${testsPassed}`);
console.log(`Failed: ${testsFailed}`);
console.log(`Status: ${testsFailed === 0 ? '✓ ALL TESTS PASSED' : '✗ SOME TESTS FAILED'}`);

process.exit(testsFailed > 0 ? 1 : 0);
