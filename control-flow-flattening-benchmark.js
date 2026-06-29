/**
 * Control Flow Flattening - Performance & Analysis Benchmarks
 *
 * Measures code size, generation time, execution overhead,
 * and obfuscation effectiveness
 */

const {
  PolymorphicState,
  FlattenedCodeGenerator
} = require('./control-flow-flattening');

/**
 * Test Functions
 */
const testFunctions = {
  simple: function simple(x) {
    if (x > 0) {
      return x * 2;
    } else {
      return x * 3;
    }
  },

  multiPath: function multiPath(a, b, c) {
    if (a > b) {
      if (b > c) {
        return a + b + c;
      } else {
        return a - b + c;
      }
    } else {
      return a * b * c;
    }
  },

  complex: function complex(x, y) {
    let result = 0;

    if (x > 0) {
      result = x + y;
    } else {
      result = x - y;
    }

    if (result > 100) {
      return result * 2;
    } else if (result < -100) {
      return result / 2;
    } else {
      return result;
    }
  },

  arithmetic: function arithmetic(a, b) {
    const sum = a + b;
    const product = a * b;

    if (sum > product) {
      return sum - product;
    } else {
      return product - sum;
    }
  },

  nested: function nested(x) {
    if (x > 0) {
      if (x > 10) {
        if (x > 100) {
          return 'huge';
        }
        return 'large';
      }
      return 'positive';
    } else if (x < 0) {
      if (x < -10) {
        return 'negative_large';
      }
      return 'negative';
    } else {
      return 'zero';
    }
  }
};

/**
 * Benchmark Configuration Sets
 */
const configurations = {
  minimal: {
    name: 'Minimal',
    options: {
      polymorphicMode: PolymorphicState.MODES.NUMERIC,
      opaquePredicates: false,
      variableEncoding: false,
      deadCode: false,
      junkStates: false,
      stateReordering: false
    }
  },

  standard: {
    name: 'Standard',
    options: {
      polymorphicMode: PolymorphicState.MODES.NUMERIC,
      opaquePredicates: true,
      variableEncoding: true,
      deadCode: true,
      junkStates: false,
      stateReordering: false
    }
  },

  advanced: {
    name: 'Advanced',
    options: {
      polymorphicMode: PolymorphicState.MODES.OBJECT,
      opaquePredicates: true,
      variableEncoding: true,
      deadCode: true,
      junkStates: true,
      stateReordering: false
    }
  },

  maximum: {
    name: 'Maximum',
    options: {
      polymorphicMode: PolymorphicState.MODES.COMPUTED,
      opaquePredicates: true,
      variableEncoding: true,
      deadCode: true,
      junkStates: true,
      stateReordering: true
    }
  },

  polymorphic_numeric: {
    name: 'Polymorphic (Numeric)',
    options: {
      polymorphicMode: PolymorphicState.MODES.NUMERIC,
      opaquePredicates: true,
      variableEncoding: true,
      deadCode: true,
      junkStates: true
    }
  },

  polymorphic_object: {
    name: 'Polymorphic (Object)',
    options: {
      polymorphicMode: PolymorphicState.MODES.OBJECT,
      opaquePredicates: true,
      variableEncoding: true,
      deadCode: true,
      junkStates: true
    }
  },

  polymorphic_computed: {
    name: 'Polymorphic (Computed)',
    options: {
      polymorphicMode: PolymorphicState.MODES.COMPUTED,
      opaquePredicates: true,
      variableEncoding: true,
      deadCode: true,
      junkStates: true
    }
  }
};

/**
 * Benchmark Suite
 */
class ControlFlowBenchmark {
  constructor() {
    this.results = {
      sizeMeasurements: [],
      generationTime: [],
      analysis: {}
    };
  }

  /**
   * Measure code size
   */
  measureCodeSize(name, func, config) {
    const originalSize = func.toString().length;

    const generator = new FlattenedCodeGenerator();
    const flattened = generator.generateCompleteFunction(func, 'flat', config.options);
    const flatSize = flattened.length;
    const analysis = generator.getAnalysis();

    return {
      function: name,
      config: config.name,
      originalSize,
      flatSize,
      expansion: (flatSize / originalSize).toFixed(2),
      states: analysis.stateCount,
      transitions: analysis.transitions.length,
      compressionRatio: (flatSize / originalSize).toFixed(2) + 'x'
    };
  }

  /**
   * Measure generation time
   */
  measureGenerationTime(name, func, config, iterations = 100) {
    const generator = new FlattenedCodeGenerator();

    const start = process.hrtime.bigint();

    for (let i = 0; i < iterations; i++) {
      generator.generateFromFunction(func, config.options);
    }

    const end = process.hrtime.bigint();
    const totalNs = Number(end - start);
    const totalMs = totalNs / 1000000;
    const avgMs = totalMs / iterations;

    return {
      function: name,
      config: config.name,
      iterations,
      totalMs: totalMs.toFixed(3),
      avgMs: avgMs.toFixed(3),
      opsPerSec: (1000 / avgMs).toFixed(0)
    };
  }

  /**
   * Run comprehensive benchmarks
   */
  runBenchmarks() {
    console.log('╔════════════════════════════════════════════════════════════════════╗');
    console.log('║  Control Flow Flattening - Performance Benchmarks                   ║');
    console.log('╚════════════════════════════════════════════════════════════════════╝\n');

    // Code Size Benchmarks
    console.log('=== Code Size Analysis ===\n');
    console.log('Function        Configuration    Original  Flattened  Expansion  States\n' +
                '─────────────────────────────────────────────────────────────────────────');

    const sizeResults = [];
    for (const [funcName, func] of Object.entries(testFunctions)) {
      for (const [configKey, config] of Object.entries(configurations)) {
        const result = this.measureCodeSize(funcName, func, config);
        sizeResults.push(result);

        console.log(
          result.function.padEnd(16) +
          result.config.padEnd(18) +
          result.originalSize.toString().padEnd(10) +
          result.flatSize.toString().padEnd(11) +
          result.expansion.padEnd(11) +
          result.states
        );
      }
    }

    // Generation Time Benchmarks
    console.log('\n\n=== Generation Time Analysis ===\n');
    console.log('Function        Configuration    Iterations  Total (ms)  Avg (ms)  Ops/Sec\n' +
                '───────────────────────────────────────────────────────────────────────────');

    const timeResults = [];
    for (const [funcName, func] of Object.entries(testFunctions)) {
      for (const [configKey, config] of Object.entries(configurations)) {
        const result = this.measureGenerationTime(funcName, func, config, 50);
        timeResults.push(result);

        console.log(
          result.function.padEnd(16) +
          result.config.padEnd(18) +
          result.iterations.toString().padEnd(12) +
          result.totalMs.padEnd(11) +
          result.avgMs.padEnd(9) +
          result.opsPerSec
        );
      }
    }

    // Summary Statistics
    this.printSummaryStatistics(sizeResults, timeResults);
  }

  /**
   * Print summary statistics
   */
  printSummaryStatistics(sizeResults, timeResults) {
    console.log('\n\n=== Summary Statistics ===\n');

    // Size statistics by configuration
    console.log('Code Size by Configuration:\n');
    const configGroups = {};

    for (const result of sizeResults) {
      if (!configGroups[result.config]) {
        configGroups[result.config] = [];
      }
      configGroups[result.config].push(parseFloat(result.expansion));
    }

    for (const [config, expansions] of Object.entries(configGroups)) {
      const avg = (expansions.reduce((a, b) => a + b, 0) / expansions.length).toFixed(2);
      const min = Math.min(...expansions).toFixed(2);
      const max = Math.max(...expansions).toFixed(2);

      console.log(`  ${config.padEnd(20)} - Avg: ${avg}x  Min: ${min}x  Max: ${max}x`);
    }

    // Time statistics by configuration
    console.log('\nGeneration Speed by Configuration:\n');
    const timeGroups = {};

    for (const result of timeResults) {
      if (!timeGroups[result.config]) {
        timeGroups[result.config] = [];
      }
      timeGroups[result.config].push(parseFloat(result.opsPerSec));
    }

    for (const [config, opsPerSecArray] of Object.entries(timeGroups)) {
      const avg = (opsPerSecArray.reduce((a, b) => a + b, 0) / opsPerSecArray.length).toFixed(0);
      const min = Math.min(...opsPerSecArray).toFixed(0);
      const max = Math.max(...opsPerSecArray).toFixed(0);

      console.log(`  ${config.padEnd(20)} - Avg: ${avg} ops/s  Range: ${min}-${max} ops/s`);
    }

    // Function complexity ranking
    console.log('\nFunction Complexity (by original size):\n');
    const funcSizes = [];
    for (const [name, func] of Object.entries(testFunctions)) {
      funcSizes.push({ name, size: func.toString().length });
    }
    funcSizes.sort((a, b) => b.size - a.size);

    for (const { name, size } of funcSizes) {
      console.log(`  ${name.padEnd(20)} - ${size} bytes`);
    }

    // Obfuscation effectiveness
    console.log('\nObfuscation Effectiveness Ranking:\n');
    console.log('  Level 1 (Minimal):      Basic flattening only');
    console.log('  Level 2 (Standard):     + Opaque predicates + Variable encoding');
    console.log('  Level 3 (Advanced):     + Dead code + Junk states');
    console.log('  Level 4 (Maximum):      + Computed mode + State reordering\n');
  }

  /**
   * Run polymorphic mode comparison
   */
  comparePolymorphicModes() {
    console.log('\n╔════════════════════════════════════════════════════════════════════╗');
    console.log('║  Polymorphic Mode Comparison                                       ║');
    console.log('╚════════════════════════════════════════════════════════════════════╝\n');

    const func = testFunctions.complex;
    const modes = [
      { name: 'NUMERIC', mode: PolymorphicState.MODES.NUMERIC },
      { name: 'STRING', mode: PolymorphicState.MODES.STRING },
      { name: 'OBJECT', mode: PolymorphicState.MODES.OBJECT },
      { name: 'ARRAY', mode: PolymorphicState.MODES.ARRAY },
      { name: 'COMPUTED', mode: PolymorphicState.MODES.COMPUTED }
    ];

    console.log('Mode         Original  Flattened  Overhead  Complexity\n' +
                '───────────────────────────────────────────────────────');

    for (const { name, mode } of modes) {
      const generator = new FlattenedCodeGenerator();
      const code = generator.generateFromFunction(func, {
        polymorphicMode: mode,
        opaquePredicates: true
      });

      const originalSize = func.toString().length;
      const flatSize = code.length;
      const overhead = ((flatSize / originalSize - 1) * 100).toFixed(0);

      // Simple complexity measure (more operators = more complex)
      const complexity = (code.match(/[+*^&|~%]/g) || []).length;

      console.log(
        name.padEnd(13) +
        originalSize.toString().padEnd(10) +
        flatSize.toString().padEnd(11) +
        overhead.padEnd(10) +
        complexity
      );
    }
  }

  /**
   * Analyze state machine characteristics
   */
  analyzeStateMachines() {
    console.log('\n╔════════════════════════════════════════════════════════════════════╗');
    console.log('║  State Machine Characteristics                                     ║');
    console.log('╚════════════════════════════════════════════════════════════════════╝\n');

    console.log('Function        States  Transitions  Ratio   Dead States  Transition Density\n' +
                '──────────────────────────────────────────────────────────────────────────────');

    for (const [funcName, func] of Object.entries(testFunctions)) {
      const generator = new FlattenedCodeGenerator();
      generator.generateFromFunction(func, configurations.maximum.options);
      const analysis = generator.getAnalysis();

      const states = analysis.stateCount;
      const transitions = analysis.transitions.length;
      const ratio = (transitions / states).toFixed(2);
      const deadStates = Math.max(0, states - transitions); // Approximate
      const density = ((transitions / (states * states)) * 100).toFixed(1);

      console.log(
        funcName.padEnd(16) +
        states.toString().padEnd(8) +
        transitions.toString().padEnd(13) +
        ratio.padEnd(8) +
        deadStates.toString().padEnd(12) +
        density + '%'
      );
    }
  }
}

/**
 * Main execution
 */
function main() {
  const benchmark = new ControlFlowBenchmark();

  // Run all benchmarks
  benchmark.runBenchmarks();

  // Run polymorphic mode comparison
  benchmark.comparePolymorphicModes();

  // Analyze state machines
  benchmark.analyzeStateMachines();

  console.log('\n╔════════════════════════════════════════════════════════════════════╗');
  console.log('║  Benchmark Complete                                                ║');
  console.log('╚════════════════════════════════════════════════════════════════════╝\n');
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = ControlFlowBenchmark;
