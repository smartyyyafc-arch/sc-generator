/**
 * Control Flow Flattening - Practical Examples
 *
 * Demonstrates real-world usage patterns and integration scenarios
 */

const {
  PolymorphicState,
  OpaquePredicates,
  ControlFlowFlattener,
  FlattenedCodeGenerator
} = require('./control-flow-flattening');

/**
 * Example 1: Simple Conditional Flattening
 *
 * Original code:
 * if (x > 0) return x * 2;
 * else return x * 3;
 */
function example1_SimpleConditional() {
  console.log('\n=== Example 1: Simple Conditional Flattening ===\n');

  function original(x) {
    if (x > 0) {
      return x * 2;
    } else {
      return x * 3;
    }
  }

  const generator = new FlattenedCodeGenerator();
  const flattened = generator.generateCompleteFunction(
    original,
    'flattenedConditional',
    {
      polymorphicMode: PolymorphicState.MODES.NUMERIC,
      opaquePredicates: true
    }
  );

  console.log('FLATTENED CODE:');
  console.log(flattened);
  console.log('\nANALYSIS:');
  console.log(JSON.stringify(generator.getAnalysis(), null, 2));
}

/**
 * Example 2: Polymorphic Mode Comparison
 *
 * Same function in different state representation modes
 */
function example2_PolymorphicModes() {
  console.log('\n=== Example 2: Polymorphic Mode Comparison ===\n');

  function logic(a, b) {
    if (a > b) {
      return a - b;
    } else {
      return b - a;
    }
  }

  const modes = [
    { name: 'NUMERIC', mode: PolymorphicState.MODES.NUMERIC },
    { name: 'STRING', mode: PolymorphicState.MODES.STRING },
    { name: 'OBJECT', mode: PolymorphicState.MODES.OBJECT },
    { name: 'ARRAY', mode: PolymorphicState.MODES.ARRAY },
    { name: 'COMPUTED', mode: PolymorphicState.MODES.COMPUTED }
  ];

  modes.forEach(({ name, mode }) => {
    console.log(`\n--- Mode: ${name} ---`);
    const generator = new FlattenedCodeGenerator();
    const code = generator.generateFromFunction(logic, {
      polymorphicMode: mode,
      opaquePredicates: false // Disable for clarity
    });

    // Show first 500 chars
    console.log(code.substring(0, 500));
    console.log('...');

    const analysis = generator.getAnalysis();
    console.log(`States: ${analysis.stateCount}, Transitions: ${analysis.transitions.length}`);
  });
}

/**
 * Example 3: Feature Comparison
 *
 * Same code with different obfuscation features enabled/disabled
 */
function example3_FeatureComparison() {
  console.log('\n=== Example 3: Feature Comparison ===\n');

  function compute(x, y) {
    const sum = x + y;
    if (sum > 0) {
      return sum * 2;
    }
    return sum;
  }

  const featureSets = [
    {
      name: 'Minimal',
      options: {
        polymorphicMode: PolymorphicState.MODES.NUMERIC,
        opaquePredicates: false,
        variableEncoding: false,
        deadCode: false,
        junkStates: false
      }
    },
    {
      name: 'Standard',
      options: {
        polymorphicMode: PolymorphicState.MODES.NUMERIC,
        opaquePredicates: true,
        variableEncoding: true,
        deadCode: true,
        junkStates: false
      }
    },
    {
      name: 'Maximum',
      options: {
        polymorphicMode: PolymorphicState.MODES.COMPUTED,
        opaquePredicates: true,
        variableEncoding: true,
        deadCode: true,
        junkStates: true,
        stateReordering: true
      }
    }
  ];

  featureSets.forEach(({ name, options }) => {
    console.log(`\n--- Configuration: ${name} ---`);
    const generator = new FlattenedCodeGenerator();
    const code = generator.generateFromFunction(compute, options);

    const analysis = generator.getAnalysis();
    console.log(`Code size: ${code.length} characters`);
    console.log(`States: ${analysis.stateCount}`);
    console.log(`Features: ${JSON.stringify(analysis.features)}`);
  });
}

/**
 * Example 4: Opaque Predicates in Action
 *
 * Demonstrates how opaque predicates are generated and used
 */
function example4_OpaquePredicates() {
  console.log('\n=== Example 4: Opaque Predicates ===\n');

  console.log('Sample Always-True Predicates:');
  for (let i = 0; i < 5; i++) {
    const predicate = OpaquePredicates.generateAlwaysTrue();
    try {
      const result = eval(predicate);
      console.log(`  ${predicate} => ${result}`);
    } catch (e) {
      console.log(`  ${predicate} => ERROR: ${e.message}`);
    }
  }

  console.log('\nSample Always-False Predicates:');
  for (let i = 0; i < 5; i++) {
    const predicate = OpaquePredicates.generateAlwaysFalse();
    try {
      const result = eval(predicate);
      console.log(`  ${predicate} => ${result}`);
    } catch (e) {
      console.log(`  ${predicate} => ERROR: ${e.message}`);
    }
  }

  console.log('\nSample Ambiguous Predicates:');
  for (let i = 0; i < 5; i++) {
    const predicate = OpaquePredicates.generateAmbiguous();
    try {
      const result = eval(predicate);
      console.log(`  ${predicate} => ${result}`);
    } catch (e) {
      console.log(`  ${predicate} => ERROR: ${e.message}`);
    }
  }
}

/**
 * Example 5: State Machine Analysis
 *
 * Analyze the state transitions in flattened code
 */
function example5_StateAnalysis() {
  console.log('\n=== Example 5: State Machine Analysis ===\n');

  function flowLogic(n) {
    if (n < 0) {
      return 'negative';
    } else if (n === 0) {
      return 'zero';
    } else {
      return 'positive';
    }
  }

  const generator = new FlattenedCodeGenerator();
  generator.generateFromFunction(flowLogic);

  const analysis = generator.getAnalysis();

  console.log('State Transition Map:');
  console.log(`Total States: ${analysis.stateCount}`);
  console.log(`Total Transitions: ${analysis.transitions.length}`);

  console.log('\nTransition Details:');
  analysis.transitions.forEach((t, idx) => {
    console.log(`  Transition ${idx + 1}: State ${t.from} → State ${t.to}`);
    if (t.condition) {
      console.log(`    Condition: ${t.condition}`);
    }
  });

  console.log('\nPolymorphic Mode:', analysis.polymorphicMode);
  console.log('Enabled Features:');
  Object.entries(analysis.features).forEach(([feature, enabled]) => {
    console.log(`  ${feature}: ${enabled}`);
  });
}

/**
 * Example 6: Polymorphic State Deep Dive
 *
 * Explore how states are generated in each mode
 */
function example6_PolymorphicStates() {
  console.log('\n=== Example 6: Polymorphic State Generation ===\n');

  const modes = [
    PolymorphicState.MODES.NUMERIC,
    PolymorphicState.MODES.STRING,
    PolymorphicState.MODES.OBJECT,
    PolymorphicState.MODES.ARRAY,
    PolymorphicState.MODES.COMPUTED
  ];

  const testValue = 42;
  const compareValue = 42;

  modes.forEach(mode => {
    console.log(`\n--- Mode: ${mode} ---`);

    const state = new PolymorphicState(testValue, mode);

    console.log('Initialization:');
    console.log(`  ${state.generateCode('state')}`);

    console.log('Comparison (state === 42):');
    console.log(`  if (${state.generateComparison('state', compareValue)}) { ... }`);

    console.log('Assignment (state = 99):');
    console.log(`  ${state.generateAssignment('state', 99)}`);
  });
}

/**
 * Example 7: Function with Multiple Paths
 *
 * More complex function with nested conditionals
 */
function example7_ComplexFlow() {
  console.log('\n=== Example 7: Complex Control Flow ===\n');

  function complexLogic(x, y, z) {
    let result = 0;

    if (x > 0) {
      result = x + y;
    } else {
      result = x - y;
    }

    if (result > z) {
      return result * 2;
    } else {
      return result / 2;
    }
  }

  const generator = new FlattenedCodeGenerator();
  const code = generator.generateCompleteFunction(complexLogic, 'complex_flat', {
    polymorphicMode: PolymorphicState.MODES.OBJECT,
    opaquePredicates: true,
    variableEncoding: true,
    deadCode: true
  });

  console.log('Generated function preview (first 800 chars):');
  console.log(code.substring(0, 800));
  console.log('...\n');

  const analysis = generator.getAnalysis();
  console.log('Complexity metrics:');
  console.log(`  Code size: ${code.length} bytes`);
  console.log(`  States: ${analysis.stateCount}`);
  console.log(`  Transitions: ${analysis.transitions.length}`);
  console.log(`  Compression ratio: ${(code.length / complexLogic.toString().length).toFixed(2)}x`);
}

/**
 * Example 8: Security Analysis
 *
 * Compare security characteristics of different configurations
 */
function example8_SecurityAnalysis() {
  console.log('\n=== Example 8: Security Analysis ===\n');

  function target(a, b) {
    return a > b ? a : b;
  }

  const configurations = [
    {
      name: 'Unobfuscated',
      options: {}
    },
    {
      name: 'Basic Flattening',
      options: {
        polymorphicMode: PolymorphicState.MODES.NUMERIC,
        opaquePredicates: false,
        variableEncoding: false,
        deadCode: false
      }
    },
    {
      name: 'Intermediate',
      options: {
        polymorphicMode: PolymorphicState.MODES.OBJECT,
        opaquePredicates: true,
        variableEncoding: true,
        deadCode: true
      }
    },
    {
      name: 'Maximum Security',
      options: {
        polymorphicMode: PolymorphicState.MODES.COMPUTED,
        opaquePredicates: true,
        variableEncoding: true,
        deadCode: true,
        junkStates: true,
        stateReordering: true
      }
    }
  ];

  console.log('Security vs Size Tradeoff:\n');
  console.log('Configuration'.padEnd(20) + 'Size (bytes)'.padEnd(15) + 'States'.padEnd(10) + 'Features');
  console.log('-'.repeat(70));

  const unobfuscated = target.toString().length;

  configurations.forEach(({ name, options }) => {
    const generator = new FlattenedCodeGenerator();
    const code = generator.generateFromFunction(target, options);
    const analysis = generator.getAnalysis();

    const features = Object.values(analysis.features).filter(Boolean).length;
    const sizeRatio = code.length / unobfuscated;

    console.log(
      name.padEnd(20) +
      code.length.toString().padEnd(15) +
      analysis.stateCount.toString().padEnd(10) +
      `${features} enabled`
    );
  });

  console.log(`\nNote: Unobfuscated size: ${unobfuscated} bytes`);
}

/**
 * Example 9: Recursive Function Handling
 *
 * Demonstrate limitations with recursive functions
 */
function example9_Recursion() {
  console.log('\n=== Example 9: Recursion Considerations ===\n');

  function factorial(n) {
    if (n <= 1) {
      return 1;
    }
    return n * factorial(n - 1);
  }

  console.log('Original function:');
  console.log(factorial.toString());

  console.log('\nNote: Direct flattening of recursion requires special handling.');
  console.log('Recommended approaches:');
  console.log('1. Convert to iterative equivalent before flattening');
  console.log('2. Use separate flattening for each call level');
  console.log('3. Replace recursion with trampolining + state machine');

  // Iterative equivalent
  function factorialIterative(n) {
    let result = 1;
    for (let i = 2; i <= n; i++) {
      result *= i;
    }
    return result;
  }

  console.log('\nIterative equivalent (suitable for flattening):');
  console.log(factorialIterative.toString());

  const generator = new FlattenedCodeGenerator();
  const flattened = generator.generateCompleteFunction(factorialIterative, 'flat_factorial');

  console.log('\nFlattened version (first 600 chars):');
  console.log(flattened.substring(0, 600));
  console.log('...');
}

/**
 * Example 10: Integration with Encoding Systems
 *
 * Show how control flow flattening complements other obfuscation techniques
 */
function example10_Integration() {
  console.log('\n=== Example 10: Integration with Encoding Systems ===\n');

  // Simulated payload extraction
  function extractFromPayload(encodedData) {
    if (!encodedData || typeof encodedData !== 'object') {
      return null;
    }

    if (encodedData.type === 'array') {
      return encodedData.data.join('');
    } else if (encodedData.type === 'hex') {
      let result = '';
      for (let i = 0; i < encodedData.data.length; i += 2) {
        result += String.fromCharCode(parseInt(encodedData.data.substr(i, 2), 16));
      }
      return result;
    } else if (encodedData.type === 'base64') {
      return Buffer.from(encodedData.data, 'base64').toString('utf8');
    }

    return null;
  }

  console.log('Multi-layer protection strategy:');
  console.log('1. Data Encoding Layer (Base64, Hex, Array)');
  console.log('   - Encoding: Multi-Encoding system');
  console.log('   - Purpose: Hide data representation\n');

  console.log('2. Morphic Wrapper Layer');
  console.log('   - Framework: Metamorphic Wrapper');
  console.log('   - Purpose: Vary payload structure on each run\n');

  console.log('3. Control Flow Obfuscation Layer');
  console.log('   - Technique: Control Flow Flattening');
  console.log('   - Purpose: Obscure extraction logic\n');

  console.log('Integrated example:');
  const generator = new FlattenedCodeGenerator();
  const flatExtractor = generator.generateCompleteFunction(
    extractFromPayload,
    'secureExtractor',
    {
      polymorphicMode: PolymorphicState.MODES.COMPUTED,
      opaquePredicates: true,
      variableEncoding: true,
      deadCode: true,
      junkStates: true
    }
  );

  console.log('Generated secure extractor (first 700 chars):');
  console.log(flatExtractor.substring(0, 700));
  console.log('...\n');

  const analysis = generator.getAnalysis();
  console.log('Defense metrics:');
  console.log(`  States in extractor: ${analysis.stateCount}`);
  console.log(`  Obfuscation layers: 3 (Encoding + Morphic + Control Flow)`);
  console.log(`  Code expansion: ${(flatExtractor.length / extractFromPayload.toString().length).toFixed(2)}x`);
}

/**
 * Run all examples
 */
function runAllExamples() {
  console.log('╔════════════════════════════════════════════════════════════════════╗');
  console.log('║  Control Flow Flattening - Practical Examples                      ║');
  console.log('╚════════════════════════════════════════════════════════════════════╝');

  example1_SimpleConditional();
  example2_PolymorphicModes();
  example3_FeatureComparison();
  example4_OpaquePredicates();
  example5_StateAnalysis();
  example6_PolymorphicStates();
  example7_ComplexFlow();
  example8_SecurityAnalysis();
  example9_Recursion();
  example10_Integration();

  console.log('\n╔════════════════════════════════════════════════════════════════════╗');
  console.log('║  All Examples Completed                                            ║');
  console.log('╚════════════════════════════════════════════════════════════════════╝');
}

// Export functions
module.exports = {
  example1_SimpleConditional,
  example2_PolymorphicModes,
  example3_FeatureComparison,
  example4_OpaquePredicates,
  example5_StateAnalysis,
  example6_PolymorphicStates,
  example7_ComplexFlow,
  example8_SecurityAnalysis,
  example9_Recursion,
  example10_Integration,
  runAllExamples
};

// Run all examples if executed directly
if (require.main === module) {
  runAllExamples();
}
