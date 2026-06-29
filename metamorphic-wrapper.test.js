/**
 * Metamorphic Wrapper Test Suite
 *
 * Tests:
 * 1. Basic encode/decode with all strategies
 * 2. Payload structure variation between runs
 * 3. Advanced morphing features (decoys, nesting)
 * 4. Seed-based determinism
 * 5. Strategy selection consistency
 * 6. Payload analysis and metadata
 */

const {
  ENCODING_STRATEGIES,
  MetamorphicWrapper,
  AdvancedMetamorphicWrapper,
  analyzeMetamorphism,
  calculateDepth,
  detectNestingPattern
} = require('./metamorphic-wrapper');

// Test utilities
const assert = (condition, message) => {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
};

const assertEqual = (actual, expected, message) => {
  if (actual !== expected) {
    throw new Error(`Assertion failed: ${message}\nExpected: ${expected}\nActual: ${actual}`);
  }
};

const test = (name, fn) => {
  try {
    fn();
    console.log(`✓ ${name}`);
    return true;
  } catch (error) {
    console.error(`✗ ${name}`);
    console.error(`  Error: ${error.message}`);
    return false;
  }
};

// Test Suite
const results = [];

console.log('=== Metamorphic Wrapper Test Suite ===\n');

// Test 1: All strategies encode and decode correctly
console.log('Test Group 1: Strategy Functionality');
for (const [strategyName, strategy] of Object.entries(ENCODING_STRATEGIES)) {
  results.push(test(`Strategy ${strategyName} - encode/decode roundtrip`, () => {
    const input = 'Test String 123';
    const encoded = strategy.encode(input);
    const decoded = strategy.decode(encoded);
    assertEqual(decoded, input, `${strategyName} roundtrip failed`);
  }));
}

// Test 2: MetamorphicWrapper basic functionality
console.log('\nTest Group 2: Basic MetamorphicWrapper');
results.push(test('MetamorphicWrapper - single encode/decode', () => {
  const wrapper = new MetamorphicWrapper();
  const input = 'Hello World';
  const encoded = wrapper.encode(input);
  assert(encoded.__metamorphic !== undefined, 'Metadata missing');
  assert(encoded.payload !== undefined, 'Payload missing');
  const decoded = wrapper.decode(encoded);
  assertEqual(decoded, input, 'Decode mismatch');
}));

results.push(test('MetamorphicWrapper - multiple runs with same seed', () => {
  const seed = 12345;
  const wrapper = new MetamorphicWrapper(seed);
  const input = 'Test';

  const encoded1 = wrapper.encode(input);
  const strategy1 = encoded1.__metamorphic.strategyName;

  const encoded2 = wrapper.encode(input);
  const strategy2 = encoded2.__metamorphic.strategyName;

  // Different executions should use different strategies (likely, not guaranteed)
  const history = wrapper.getSelectionHistory();
  assert(history.length === 2, 'Should have 2 history entries');
}));

results.push(test('MetamorphicWrapper - metadata correctness', () => {
  const wrapper = new MetamorphicWrapper(42);
  const encoded = wrapper.encode('Test');
  const meta = encoded.__metamorphic;

  assert(meta.version !== undefined, 'Version missing');
  assert(meta.execution !== undefined, 'Execution count missing');
  assert(meta.strategy !== undefined, 'Strategy ID missing');
  assert(meta.strategyName !== undefined, 'Strategy name missing');
  assert(meta.timestamp !== undefined, 'Timestamp missing');
  assert(meta.seed !== undefined, 'Seed missing');
}));

// Test 3: Payload structure variation
console.log('\nTest Group 3: Payload Variation');
results.push(test('Different runs produce different structures', () => {
  const wrapper = new MetamorphicWrapper(999);
  const input = 'Variation Test';

  const payloads = [];
  for (let i = 0; i < 5; i++) {
    const encoded = wrapper.encode(input);
    payloads.push(analyzeMetamorphism(encoded));
  }

  // Check that at least some have different strategies
  const strategies = new Set(payloads.map(p => p.strategy));
  assert(strategies.size > 1, 'All runs used same strategy (low probability)');
}));

results.push(test('Analyze payload structures', () => {
  const wrapper = new MetamorphicWrapper();
  const encoded = wrapper.encode('Analysis Test');
  const analysis = analyzeMetamorphism(encoded);

  assert(analysis.strategy !== undefined, 'Strategy missing');
  assert(analysis.strategyId !== undefined, 'Strategy ID missing');
  assert(analysis.payloadShape !== undefined, 'Payload shape missing');
  assert(analysis.depth !== undefined, 'Depth missing');
  assert(analysis.size > 0, 'Size should be positive');
}));

// Test 4: Advanced MetamorphicWrapper
console.log('\nTest Group 4: Advanced Metamorphic Wrapper');
results.push(test('AdvancedMetamorphicWrapper - basic encode/decode', () => {
  const wrapper = new AdvancedMetamorphicWrapper();
  const input = 'Advanced Test';
  const encoded = wrapper.encode(input);
  const decoded = wrapper.decode(encoded);
  assertEqual(decoded, input, 'Advanced wrapper roundtrip failed');
}));

results.push(test('AdvancedMetamorphicWrapper - with decoys', () => {
  const wrapper = new AdvancedMetamorphicWrapper();
  wrapper.configureMorphing({ addDecoys: true, varyNesting: false });
  const encoded = wrapper.encode('Decoy Test');
  const decoded = wrapper.decode(encoded);
  assertEqual(decoded, 'Decoy Test', 'Decoy handling failed');
}));

results.push(test('AdvancedMetamorphicWrapper - with variable nesting', () => {
  const wrapper = new AdvancedMetamorphicWrapper();
  wrapper.configureMorphing({ addDecoys: false, varyNesting: true });

  const depths = [];
  for (let i = 0; i < 5; i++) {
    const encoded = wrapper.encode('Nesting Test');
    const depth = calculateDepth(encoded.payload);
    depths.push(depth);
    const decoded = wrapper.decode(encoded);
    assertEqual(decoded, 'Nesting Test', `Nesting decode failed at iteration ${i}`);
  }

  // Should have variable depths
  const uniqueDepths = new Set(depths);
  assert(uniqueDepths.size > 1, 'Nesting should vary, but all have same depth');
}));

results.push(test('AdvancedMetamorphicWrapper - all morphing enabled', () => {
  const wrapper = new AdvancedMetamorphicWrapper();
  wrapper.configureMorphing({
    randomizeMetadata: true,
    addDecoys: true,
    varyNesting: true
  });

  for (let i = 0; i < 5; i++) {
    const encoded = wrapper.encode('Full Morph Test');
    const decoded = wrapper.decode(encoded);
    assertEqual(decoded, 'Full Morph Test', `Full morph decode failed at iteration ${i}`);
  }
}));

// Test 5: Seed-based determinism
console.log('\nTest Group 5: Deterministic Selection');
results.push(test('Same seed produces same strategy sequence', () => {
  const input = 'Determinism Test';
  const seed = 55555;

  const wrapper1 = new MetamorphicWrapper(seed);
  const strategies1 = [];
  for (let i = 0; i < 5; i++) {
    const encoded = wrapper1.encode(input);
    strategies1.push(encoded.__metamorphic.strategy);
  }

  const wrapper2 = new MetamorphicWrapper(seed);
  const strategies2 = [];
  for (let i = 0; i < 5; i++) {
    const encoded = wrapper2.encode(input);
    strategies2.push(encoded.__metamorphic.strategy);
  }

  for (let i = 0; i < 5; i++) {
    assertEqual(strategies1[i], strategies2[i], `Strategy mismatch at position ${i}`);
  }
}));

// Test 6: Edge cases
console.log('\nTest Group 6: Edge Cases');
results.push(test('Empty string encoding/decoding', () => {
  const wrapper = new MetamorphicWrapper();
  const encoded = wrapper.encode('');
  const decoded = wrapper.decode(encoded);
  assertEqual(decoded, '', 'Empty string handling failed');
}));

results.push(test('Special characters encoding/decoding', () => {
  const wrapper = new MetamorphicWrapper();
  const input = 'Special: @#$%^&*()_+-=[]{}|;:,.<>?/';
  const encoded = wrapper.encode(input);
  const decoded = wrapper.decode(encoded);
  assertEqual(decoded, input, 'Special characters handling failed');
}));

results.push(test('Unicode/Emoji encoding/decoding', () => {
  const wrapper = new MetamorphicWrapper();
  const input = 'Unicode: 你好世界 🚀 مرحبا العالم';
  const encoded = wrapper.encode(input);
  const decoded = wrapper.decode(encoded);
  assertEqual(decoded, input, 'Unicode handling failed');
}));

results.push(test('Large string encoding/decoding', () => {
  const wrapper = new MetamorphicWrapper();
  const input = 'A'.repeat(10000);
  const encoded = wrapper.encode(input);
  const decoded = wrapper.decode(encoded);
  assertEqual(decoded, input, 'Large string handling failed');
}));

// Test 7: Statistics and history
console.log('\nTest Group 7: Statistics & History');
results.push(test('Execution count increments', () => {
  const wrapper = new MetamorphicWrapper();
  assert(wrapper.executionCount === 0, 'Initial count should be 0');

  wrapper.encode('Test');
  assert(wrapper.executionCount === 1, 'Count should be 1 after first encode');

  wrapper.encode('Test');
  assert(wrapper.executionCount === 2, 'Count should be 2 after second encode');
}));

results.push(test('Selection history tracks all selections', () => {
  const wrapper = new MetamorphicWrapper();
  wrapper.encode('Test 1');
  wrapper.encode('Test 2');
  wrapper.encode('Test 3');

  const history = wrapper.getSelectionHistory();
  assert(history.length === 3, 'History should have 3 entries');
  for (let i = 0; i < 3; i++) {
    assert(history[i].execution === i, `Execution number mismatch at ${i}`);
    assert(history[i].strategyId !== undefined, `Strategy ID missing at ${i}`);
    assert(history[i].strategyName !== undefined, `Strategy name missing at ${i}`);
  }
}));

results.push(test('Get statistics', () => {
  const wrapper = new MetamorphicWrapper(123);
  wrapper.encode('Test 1');
  wrapper.encode('Test 2');

  const stats = wrapper.getStatistics();
  assert(stats.executionCount === 2, 'Execution count mismatch');
  assert(stats.seed === 123, 'Seed mismatch');
  assert(stats.strategiesUsed > 0, 'Should have used strategies');
  assert(stats.lastStrategy !== null, 'Last strategy should be set');
}));

// Print results summary
console.log('\n' + '='.repeat(50));
const passed = results.filter(r => r).length;
const failed = results.filter(r => !r).length;
const total = results.length;

console.log(`\nTest Results: ${passed}/${total} passed, ${failed} failed`);
console.log(`Success Rate: ${((passed / total) * 100).toFixed(2)}%`);

if (failed > 0) {
  process.exit(1);
} else {
  console.log('\nAll tests passed! ✓');
}
