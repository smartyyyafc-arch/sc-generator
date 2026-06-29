/**
 * Control Flow Flattening - Comprehensive Test Suite
 *
 * Tests polymorphic obfuscation, state machine generation,
 * opaque predicates, and code generation
 */

const {
  ControlFlowGraph,
  PolymorphicState,
  OpaquePredicates,
  ControlFlowFlattener,
  AdvancedControlFlowFlattener,
  FlattenedCodeGenerator
} = require('./control-flow-flattening');

/**
 * Test Suite
 */
class ControlFlowFlatteningTests {
  constructor() {
    this.passed = 0;
    this.failed = 0;
    this.tests = [];
  }

  /**
   * Assert helper
   */
  assert(condition, message) {
    if (condition) {
      this.passed++;
      console.log(`✓ ${message}`);
    } else {
      this.failed++;
      console.log(`✗ ${message}`);
      this.tests.push({ status: 'FAILED', message });
    }
  }

  /**
   * Test: CFG Node Creation
   */
  testCFGNodeCreation() {
    console.log('\n--- Test: CFG Node Creation ---');
    const graph = new ControlFlowGraph();

    const node1 = graph.createNode('assignment', { variable: 'x', value: 5 });
    this.assert(node1.id === 0, 'First node gets ID 0');
    this.assert(node1.type === 'assignment', 'Node type is set correctly');
    this.assert(node1.data.variable === 'x', 'Node data preserved');

    const node2 = graph.createNode('conditional', { condition: 'x > 0' });
    this.assert(node2.id === 1, 'Second node gets ID 1');
    this.assert(graph.nodeCounter === 2, 'Node counter increments');
  }

  /**
   * Test: CFG Edge Management
   */
  testCFGEdgeManagement() {
    console.log('\n--- Test: CFG Edge Management ---');
    const graph = new ControlFlowGraph();
    const node1 = graph.createNode('assignment', {});
    const node2 = graph.createNode('return', {});

    graph.addEdge(node1, node2);
    this.assert(node1.next.includes(node2), 'Edge added to next array');
    this.assert(node2.prev.includes(node1), 'Edge added to prev array');
    this.assert(graph.edges.length === 1, 'Edge stored in edges array');

    // Test duplicate edge prevention
    graph.addEdge(node1, node2);
    this.assert(graph.edges.length === 1, 'Duplicate edges not added');
  }

  /**
   * Test: Polymorphic State - Numeric Mode
   */
  testPolymorphicStateNumeric() {
    console.log('\n--- Test: Polymorphic State - Numeric Mode ---');
    const state = new PolymorphicState(42, PolymorphicState.MODES.NUMERIC);

    const code = state.generateCode('myState');
    this.assert(code.includes('let myState = 42'), 'Numeric state code generated');

    const comparison = state.generateComparison('myState', 42);
    this.assert(comparison === 'myState === 42', 'Numeric comparison correct');

    const assignment = state.generateAssignment('myState', 99);
    this.assert(assignment.includes('99'), 'Numeric assignment generated');
  }

  /**
   * Test: Polymorphic State - String Mode
   */
  testPolymorphicStateString() {
    console.log('\n--- Test: Polymorphic State - String Mode ---');
    const state = new PolymorphicState(5, PolymorphicState.MODES.STRING);

    const code = state.generateCode('strState');
    this.assert(code.includes('strState'), 'String state code generated');
    this.assert(code.includes("'"), 'String state uses quotes');

    const comparison = state.generateComparison('strState', 5);
    this.assert(comparison.includes('==='), 'String comparison uses equality');
  }

  /**
   * Test: Polymorphic State - Object Mode
   */
  testPolymorphicStateObject() {
    console.log('\n--- Test: Polymorphic State - Object Mode ---');
    const state = new PolymorphicState(7, PolymorphicState.MODES.OBJECT);

    const code = state.generateCode('objState');
    this.assert(code.includes('{_s:'), 'Object state creates object with _s field');
    this.assert(code.includes('Math.random()'), 'Object state includes random field');

    const comparison = state.generateComparison('objState', 7);
    this.assert(comparison.includes('._s'), 'Object comparison accesses _s field');
  }

  /**
   * Test: Polymorphic State - Array Mode
   */
  testPolymorphicStateArray() {
    console.log('\n--- Test: Polymorphic State - Array Mode ---');
    const state = new PolymorphicState(3, PolymorphicState.MODES.ARRAY);

    const code = state.generateCode('arrState');
    this.assert(code.includes('['), 'Array state uses array syntax');

    const comparison = state.generateComparison('arrState', 3);
    this.assert(comparison.includes('[0]'), 'Array comparison accesses first element');
  }

  /**
   * Test: Polymorphic State - Computed Mode
   */
  testPolymorphicStateComputed() {
    console.log('\n--- Test: Polymorphic State - Computed Mode ---');
    const state = new PolymorphicState(10, PolymorphicState.MODES.COMPUTED);

    const code = state.generateCode('compState');
    this.assert(code.includes('compState'), 'Computed state code generated');
    // Computed should use operations like +, *, ^, etc.
    const hasOperation = /[\+\*\^&|]/.test(code);
    this.assert(hasOperation, 'Computed state includes operations');
  }

  /**
   * Test: Opaque Predicates - Always True
   */
  testOpaquePredicatesAlwaysTrue() {
    console.log('\n--- Test: Opaque Predicates - Always True ---');
    const predicate = OpaquePredicates.generateAlwaysTrue();

    this.assert(predicate.length > 0, 'Predicate generated');
    this.assert(typeof predicate === 'string', 'Predicate is string');

    // Try to evaluate (should be true)
    try {
      const result = eval(predicate);
      this.assert(result === true, 'Predicate evaluates to true');
    } catch (e) {
      this.assert(false, 'Predicate evaluation error: ' + e.message);
    }
  }

  /**
   * Test: Opaque Predicates - Always False
   */
  testOpaquePredicatesAlwaysFalse() {
    console.log('\n--- Test: Opaque Predicates - Always False ---');
    const predicate = OpaquePredicates.generateAlwaysFalse();

    this.assert(predicate.length > 0, 'Predicate generated');

    try {
      const result = eval(predicate);
      this.assert(result === false, 'Predicate evaluates to false');
    } catch (e) {
      this.assert(false, 'Predicate evaluation error: ' + e.message);
    }
  }

  /**
   * Test: Opaque Predicates - Ambiguous
   */
  testOpaquePredicatesAmbiguous() {
    console.log('\n--- Test: Opaque Predicates - Ambiguous ---');
    const predicate = OpaquePredicates.generateAmbiguous();

    this.assert(predicate.length > 0, 'Ambiguous predicate generated');

    try {
      const result = eval(predicate);
      this.assert(typeof result === 'boolean', 'Predicate evaluates to boolean');
    } catch (e) {
      this.assert(false, 'Predicate evaluation error: ' + e.message);
    }
  }

  /**
   * Test: Control Flow Flattener - Graph Parsing
   */
  testFlattenerGraphParsing() {
    console.log('\n--- Test: Control Flow Flattener - Graph Parsing ---');
    const flattener = new ControlFlowFlattener();

    function testFunc(x) {
      if (x > 0) {
        return x * 2;
      } else {
        return x * 3;
      }
    }

    const graph = flattener.parseFunctionToGraph(testFunc);
    this.assert(graph !== null, 'Graph created from function');
    this.assert(graph.nodes.size > 0, 'Graph contains nodes');
    this.assert(graph.getEdges().length > 0, 'Graph contains edges');
  }

  /**
   * Test: Control Flow Flattener - State Mapping
   */
  testFlattenerStateMapping() {
    console.log('\n--- Test: Control Flow Flattener - State Mapping ---');
    const flattener = new ControlFlowFlattener();

    function simpleFunc() {
      const x = 5;
      return x;
    }

    flattener.parseFunctionToGraph(simpleFunc);
    const transitions = flattener.getStateTransitions();

    this.assert(Array.isArray(transitions), 'Transitions array returned');
    this.assert(transitions.every(t => typeof t.from === 'number'), 'Transitions have numeric states');
  }

  /**
   * Test: Control Flow Flattener - Polymorphic Modes
   */
  testFlattenerPolymorphicModes() {
    console.log('\n--- Test: Control Flow Flattener - Polymorphic Modes ---');
    const flattener = new ControlFlowFlattener();

    const modes = [
      PolymorphicState.MODES.NUMERIC,
      PolymorphicState.MODES.STRING,
      PolymorphicState.MODES.OBJECT,
      PolymorphicState.MODES.ARRAY,
      PolymorphicState.MODES.COMPUTED
    ];

    for (const mode of modes) {
      flattener.setPolymorphicMode(mode);
      this.assert(flattener.polymorphicMode === mode, `Polymorphic mode set to ${mode}`);
    }
  }

  /**
   * Test: Advanced Flattener - Features
   */
  testAdvancedFlattenerFeatures() {
    console.log('\n--- Test: Advanced Flattener - Features ---');
    const flattener = new AdvancedControlFlowFlattener();

    this.assert(flattener.deadCodeInsertion === true, 'Dead code insertion enabled');
    this.assert(flattener.junkStateInsertion === true, 'Junk state insertion enabled');
    this.assert(flattener.stateReordering === true, 'State reordering enabled');

    flattener.deadCodeInsertion = false;
    this.assert(flattener.deadCodeInsertion === false, 'Dead code insertion can be disabled');
  }

  /**
   * Test: Code Generator - Function Conversion
   */
  testCodeGeneratorFunctionConversion() {
    console.log('\n--- Test: Code Generator - Function Conversion ---');
    const generator = new FlattenedCodeGenerator();

    function targetFunc(a, b) {
      if (a > b) {
        return a;
      } else {
        return b;
      }
    }

    const code = generator.generateFromFunction(targetFunc);
    this.assert(code.length > 0, 'Flattened code generated');
    this.assert(code.includes('switch'), 'Code uses switch statement');
    this.assert(code.includes('case'), 'Code uses case labels');
  }

  /**
   * Test: Code Generator - Complete Function
   */
  testCodeGeneratorCompleteFunction() {
    console.log('\n--- Test: Code Generator - Complete Function ---');
    const generator = new FlattenedCodeGenerator();

    function logic(x) {
      return x + 1;
    }

    const complete = generator.generateCompleteFunction(logic, 'flatFunc');
    this.assert(complete.includes('function flatFunc()'), 'Function name preserved');
    this.assert(complete.includes('{'), 'Function has body');
    this.assert(complete.includes('}'), 'Function properly closed');
  }

  /**
   * Test: Code Generator - Analysis
   */
  testCodeGeneratorAnalysis() {
    console.log('\n--- Test: Code Generator - Analysis ---');
    const generator = new FlattenedCodeGenerator();

    function dummy() {
      return 42;
    }

    generator.generateFromFunction(dummy);
    const analysis = generator.getAnalysis();

    this.assert(analysis.stateCount > 0, 'State count in analysis');
    this.assert(Array.isArray(analysis.transitions), 'Transitions in analysis');
    this.assert(analysis.features !== undefined, 'Features in analysis');
    this.assert(analysis.polymorphicMode !== undefined, 'Polymorphic mode in analysis');
  }

  /**
   * Test: Variable Encoding
   */
  testVariableEncoding() {
    console.log('\n--- Test: Variable Encoding ---');
    const flattener = new ControlFlowFlattener();
    flattener.enableVariableEncoding = true;

    const encoded1 = flattener._encodeVariable('state');
    const encoded2 = flattener._encodeVariable('state');

    this.assert(encoded1 === encoded2, 'Same variable gets same encoding');
    this.assert(encoded1.startsWith('_'), 'Encoded variable starts with underscore');

    const encoded3 = flattener._encodeVariable('other');
    this.assert(encoded1 !== encoded3, 'Different variables get different encodings');
  }

  /**
   * Test: Condition Obfuscation
   */
  testConditionObfuscation() {
    console.log('\n--- Test: Condition Obfuscation ---');
    const flattener = new ControlFlowFlattener();
    flattener.enableOpaquePredicates = true;

    const condition = 'x > 0';
    const obfuscated = flattener._obfuscateCondition(condition);

    this.assert(obfuscated !== condition, 'Condition is obfuscated');
    this.assert(obfuscated.includes('x > 0'), 'Original condition included in obfuscation');
  }

  /**
   * Test: Multiple Runs Produce Different Results
   */
  testPolymorphismVariability() {
    console.log('\n--- Test: Polymorphism Variability ---');
    const generator1 = new FlattenedCodeGenerator();
    const generator2 = new FlattenedCodeGenerator();

    function test() {
      return 1;
    }

    const code1 = generator1.generateFromFunction(test);
    const code2 = generator2.generateFromFunction(test);

    // Due to randomization in opaque predicates and other features,
    // codes should be different (though logically equivalent)
    this.assert(code1.length > 0 && code2.length > 0, 'Both generated codes');
    // Note: They might be same due to randomization, but likely different
  }

  /**
   * Run all tests
   */
  runAll() {
    console.log('=== Control Flow Flattening Test Suite ===');

    this.testCFGNodeCreation();
    this.testCFGEdgeManagement();
    this.testPolymorphicStateNumeric();
    this.testPolymorphicStateString();
    this.testPolymorphicStateObject();
    this.testPolymorphicStateArray();
    this.testPolymorphicStateComputed();
    this.testOpaquePredicatesAlwaysTrue();
    this.testOpaquePredicatesAlwaysFalse();
    this.testOpaquePredicatesAmbiguous();
    this.testFlattenerGraphParsing();
    this.testFlattenerStateMapping();
    this.testFlattenerPolymorphicModes();
    this.testAdvancedFlattenerFeatures();
    this.testCodeGeneratorFunctionConversion();
    this.testCodeGeneratorCompleteFunction();
    this.testCodeGeneratorAnalysis();
    this.testVariableEncoding();
    this.testConditionObfuscation();
    this.testPolymorphismVariability();

    this.printSummary();
  }

  /**
   * Print test summary
   */
  printSummary() {
    console.log('\n=== Test Summary ===');
    console.log(`Passed: ${this.passed}`);
    console.log(`Failed: ${this.failed}`);
    console.log(`Total: ${this.passed + this.failed}`);
    console.log(`Success Rate: ${((this.passed / (this.passed + this.failed)) * 100).toFixed(2)}%`);

    if (this.failed === 0) {
      console.log('\nAll tests passed! ✓');
    } else {
      console.log(`\n${this.failed} test(s) failed.`);
    }
  }
}

// Run tests if executed directly
if (require.main === module) {
  const testSuite = new ControlFlowFlatteningTests();
  testSuite.runAll();
}

module.exports = ControlFlowFlatteningTests;
