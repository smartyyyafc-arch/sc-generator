/**
 * Control Flow Flattening with Polymorphic Obfuscation
 *
 * Transforms complex control structures (if/else, loops, switch) into
 * a state machine with a dispatcher and opaque state transitions.
 *
 * Features:
 * - Converts conditionals to state-based dispatch
 * - Flattens nested structures into linear sequences
 * - Polymorphic state representations (numeric, string, object)
 * - Opaque predicates to mask true control flow
 * - State transition obfuscation
 * - Variable name encoding
 */

/**
 * Abstract Syntax representation for control flow
 */
class CFGNode {
  constructor(id, type, data = {}) {
    this.id = id;
    this.type = type; // 'assignment', 'conditional', 'loop', 'call', 'return'
    this.data = data;
    this.next = [];
    this.prev = [];
    this.label = null;
  }
}

/**
 * Control Flow Graph builder
 */
class ControlFlowGraph {
  constructor() {
    this.nodes = new Map();
    this.edges = [];
    this.nodeCounter = 0;
  }

  createNode(type, data = {}) {
    const id = this.nodeCounter++;
    const node = new CFGNode(id, type, data);
    this.nodes.set(id, node);
    return node;
  }

  addEdge(from, to) {
    if (!from.next.includes(to)) {
      from.next.push(to);
    }
    if (!to.prev.includes(from)) {
      to.prev.push(from);
    }
    this.edges.push({ from: from.id, to: to.id });
  }

  getNodes() {
    return Array.from(this.nodes.values());
  }

  getEdges() {
    return this.edges;
  }

  toJSON() {
    return {
      nodes: this.getNodes().map(n => ({
        id: n.id,
        type: n.type,
        data: n.data,
        label: n.label,
        nextIds: n.next.map(x => x.id),
        prevIds: n.prev.map(x => x.id)
      })),
      edges: this.edges
    };
  }
}

/**
 * Polymorphic State Representation
 * Encodes state in different formats to evade static analysis
 */
class PolymorphicState {
  static MODES = {
    NUMERIC: 'numeric',
    STRING: 'string',
    OBJECT: 'object',
    ARRAY: 'array',
    COMPUTED: 'computed'
  };

  constructor(stateValue, mode = PolymorphicState.MODES.NUMERIC) {
    this.stateValue = stateValue;
    this.mode = mode;
    this.transforms = [];
  }

  /**
   * Generate state transition code in chosen mode
   */
  generateCode(variableName = 'state') {
    switch (this.mode) {
      case PolymorphicState.MODES.NUMERIC:
        return `let ${variableName} = ${this.stateValue};`;

      case PolymorphicState.MODES.STRING:
        return `let ${variableName} = '${this._numToString(this.stateValue)}';`;

      case PolymorphicState.MODES.OBJECT:
        return `let ${variableName} = {_s: ${this.stateValue}, _v: Math.random()};`;

      case PolymorphicState.MODES.ARRAY:
        return `let ${variableName} = [${this.stateValue}, ${this.stateValue + 1}];`;

      case PolymorphicState.MODES.COMPUTED:
        const computation = this._generateOpaqueComputation(this.stateValue);
        return `let ${variableName} = ${computation};`;

      default:
        return `let ${variableName} = ${this.stateValue};`;
    }
  }

  /**
   * Generate comparison code for state checking
   */
  generateComparison(variableName, compareValue) {
    switch (this.mode) {
      case PolymorphicState.MODES.NUMERIC:
        return `${variableName} === ${compareValue}`;

      case PolymorphicState.MODES.STRING:
        return `${variableName} === '${this._numToString(compareValue)}'`;

      case PolymorphicState.MODES.OBJECT:
        return `${variableName}._s === ${compareValue}`;

      case PolymorphicState.MODES.ARRAY:
        return `${variableName}[0] === ${compareValue}`;

      case PolymorphicState.MODES.COMPUTED:
        return `(${variableName}) === ${compareValue}`;

      default:
        return `${variableName} === ${compareValue}`;
    }
  }

  /**
   * Generate state assignment code
   */
  generateAssignment(variableName, newValue) {
    switch (this.mode) {
      case PolymorphicState.MODES.NUMERIC:
        return `${variableName} = ${newValue};`;

      case PolymorphicState.MODES.STRING:
        return `${variableName} = '${this._numToString(newValue)}';`;

      case PolymorphicState.MODES.OBJECT:
        return `${variableName} = {_s: ${newValue}, _v: Math.random()};`;

      case PolymorphicState.MODES.ARRAY:
        return `${variableName} = [${newValue}, ${newValue + 1}];`;

      case PolymorphicState.MODES.COMPUTED:
        const computation = this._generateOpaqueComputation(newValue);
        return `${variableName} = ${computation};`;

      default:
        return `${variableName} = ${newValue};`;
    }
  }

  _numToString(num) {
    return String.fromCharCode(...num.toString().split('').map(d => parseInt(d) + 65));
  }

  _generateOpaqueComputation(value) {
    const techniques = [
      () => `(${value} + 0)`,
      () => `(${value} * 1)`,
      () => `(~${value} & -1)`,
      () => `(${value} | 0)`,
      () => `(${value} ^ 0)`,
      () => `(Math.ceil(${value}.toFixed(0)))`,
      () => `Math.imul(1, ${value})`
    ];
    const choice = techniques[Math.floor(Math.random() * techniques.length)];
    return choice();
  }
}

/**
 * Opaque Predicate Generator
 * Creates meaningless conditions that always evaluate to true/false
 * but are hard to simplify through static analysis
 */
class OpaquePredicates {
  static generateAlwaysTrue() {
    const techniques = [
      '!(1 === 0)',
      '(3735928559 >>> 0) > 0',
      '(Math.abs(-1) === Math.abs(1))',
      '((1n << 30n) !== 0n)',
      '(parseInt("1e2") === 100)',
      '((x) => x === x)(Math.random() || true)',
      '(!!(1 & 1))',
      '((a, b) => a ^ b)(0, 0) === 0'
    ];
    return techniques[Math.floor(Math.random() * techniques.length)];
  }

  static generateAlwaysFalse() {
    const techniques = [
      '(1 === 0)',
      '(Math.random() === -1)',
      '((0 & 1) === 1)',
      '(NaN === NaN)',
      '((x) => x !== x)(undefined)',
      '(parseInt("9999999999999999999999999") === 0)',
      '((a) => !a && a)(true)',
      '(!!(1 ^ 1))'
    ];
    return techniques[Math.floor(Math.random() * techniques.length)];
  }

  static generateAmbiguous() {
    const a = Math.floor(Math.random() * 256);
    const b = Math.floor(Math.random() * 256);
    return `((${a} & ${b}) === ${a & b})`;
  }
}

/**
 * Control Flow Flattening Engine
 * Transforms code structure into state machine
 */
class ControlFlowFlattener {
  constructor() {
    this.cfg = new ControlFlowGraph();
    this.stateMap = new Map();
    this.stateCounter = 0;
    this.polymorphicMode = PolymorphicState.MODES.NUMERIC;
    this.enableOpaquePredicates = true;
    this.enableVariableEncoding = true;
    this.variableEncoding = new Map();
  }

  /**
   * Parse simple JavaScript function into CFG
   */
  parseFunctionToGraph(func) {
    const funcStr = func.toString();
    const astNodes = this._extractControlFlowStructures(funcStr);

    let currentNode = null;
    const startNode = this.cfg.createNode('start', {});
    currentNode = startNode;

    for (const astNode of astNodes) {
      const cfgNode = this._convertASTToCFG(astNode);
      if (currentNode) {
        this.cfg.addEdge(currentNode, cfgNode);
      }
      currentNode = cfgNode;
    }

    const endNode = this.cfg.createNode('end', {});
    if (currentNode) {
      this.cfg.addEdge(currentNode, endNode);
    }

    return this.cfg;
  }

  /**
   * Extract control flow structures from function body
   */
  _extractControlFlowStructures(funcStr) {
    // Simplified extraction - in production use proper AST parser
    const structures = [];

    // Match if statements
    const ifRegex = /if\s*\((.*?)\)\s*\{([\s\S]*?)\}(?:\s*else\s*\{([\s\S]*?)\})?/g;
    let match;
    while ((match = ifRegex.exec(funcStr)) !== null) {
      structures.push({
        type: 'if',
        condition: match[1],
        trueBranch: match[2],
        falseBranch: match[3]
      });
    }

    // Match assignments
    const assignRegex = /(\w+)\s*=\s*([^;]+);/g;
    while ((match = assignRegex.exec(funcStr)) !== null) {
      structures.push({
        type: 'assignment',
        variable: match[1],
        value: match[2]
      });
    }

    // Match returns
    const returnRegex = /return\s+([^;]+);/g;
    while ((match = returnRegex.exec(funcStr)) !== null) {
      structures.push({
        type: 'return',
        value: match[1]
      });
    }

    return structures;
  }

  /**
   * Convert AST node to CFG node
   */
  _convertASTToCFG(astNode) {
    switch (astNode.type) {
      case 'if':
        return this.cfg.createNode('conditional', {
          condition: astNode.condition,
          trueBranch: astNode.trueBranch,
          falseBranch: astNode.falseBranch
        });

      case 'assignment':
        return this.cfg.createNode('assignment', {
          variable: astNode.variable,
          value: astNode.value
        });

      case 'return':
        return this.cfg.createNode('return', {
          value: astNode.value
        });

      default:
        return this.cfg.createNode('unknown', astNode);
    }
  }

  /**
   * Flatten CFG into dispatch-based structure
   */
  flattenGraph() {
    const nodes = this.cfg.getNodes();
    const flatCode = [];

    // Initialize state variable
    const stateVar = this._encodeVariable('state');
    const polymorphic = new PolymorphicState(0, this.polymorphicMode);
    flatCode.push(polymorphic.generateCode(stateVar));

    // Create state to node mapping
    const stateNodeMap = new Map();
    for (const node of nodes) {
      const state = this.stateCounter++;
      stateNodeMap.set(node.id, state);
      this.stateMap.set(state, node);
    }

    // Generate dispatch structure
    flatCode.push(`\nwhile(true) {`);
    flatCode.push(`  switch(${stateVar}) {`);

    for (const [nodeId, state] of stateNodeMap.entries()) {
      const node = this.cfg.nodes.get(nodeId);
      flatCode.push(`    case ${state}:`);
      flatCode.push(`      ${this._generateNodeCode(node, stateVar, stateNodeMap)}`);
    }

    flatCode.push(`    default:`);
    flatCode.push(`      break;`);
    flatCode.push(`  }`);
    flatCode.push(`}`);

    return flatCode.join('\n');
  }

  /**
   * Generate code for individual CFG node
   */
  _generateNodeCode(node, stateVar, stateNodeMap) {
    const code = [];

    switch (node.type) {
      case 'assignment':
        code.push(node.data.variable + ' = ' + node.data.value + ';');
        break;

      case 'conditional':
        const condition = this._obfuscateCondition(node.data.condition);
        code.push(`if (${condition}) {`);
        const trueState = this._getNextState(node, 0, stateNodeMap);
        code.push(`  ${new PolymorphicState(trueState, this.polymorphicMode).generateAssignment(stateVar, trueState)}`);
        code.push(`} else {`);
        const falseState = this._getNextState(node, 1, stateNodeMap);
        code.push(`  ${new PolymorphicState(falseState, this.polymorphicMode).generateAssignment(stateVar, falseState)}`);
        code.push(`}`);
        break;

      case 'return':
        code.push(`return ${node.data.value};`);
        break;

      case 'start':
      case 'end':
        if (node.type === 'end') {
          code.push('return;');
        }
        break;
    }

    if (this.enableOpaquePredicates && Math.random() > 0.5) {
      code.push(`if (${OpaquePredicates.generateAlwaysTrue()}) {}`);
    }

    return code.join('\n      ');
  }

  /**
   * Get next state for given node
   */
  _getNextState(node, branchIndex, stateNodeMap) {
    if (node.next.length > branchIndex) {
      return stateNodeMap.get(node.next[branchIndex].id);
    }
    return stateNodeMap.get(node.id) + 1;
  }

  /**
   * Obfuscate condition by adding opaque predicates
   */
  _obfuscateCondition(condition) {
    if (!this.enableOpaquePredicates) {
      return condition;
    }

    const techniques = [
      () => `(${condition}) && ${OpaquePredicates.generateAlwaysTrue()}`,
      () => `(${condition}) || ${OpaquePredicates.generateAlwaysFalse()}`,
      () => `!(!(${condition}))`,
      () => `((${condition}) ? true : false)`,
      () => `(${OpaquePredicates.generateAmbiguous()} ? (${condition}) : (${condition}))`
    ];

    const choice = techniques[Math.floor(Math.random() * techniques.length)];
    return choice();
  }

  /**
   * Encode variable name
   */
  _encodeVariable(name) {
    if (!this.enableVariableEncoding) {
      return name;
    }

    if (!this.variableEncoding.has(name)) {
      const encoded = '_' + Math.random().toString(36).substring(2, 15);
      this.variableEncoding.set(name, encoded);
    }

    return this.variableEncoding.get(name);
  }

  /**
   * Set polymorphic state mode
   */
  setPolymorphicMode(mode) {
    if (Object.values(PolymorphicState.MODES).includes(mode)) {
      this.polymorphicMode = mode;
    }
  }

  /**
   * Get flattened code as string
   */
  getFlattenedCode() {
    return this.flattenGraph();
  }

  /**
   * Get state transition map for analysis
   */
  getStateTransitions() {
    const transitions = [];
    for (const [state, node] of this.stateMap.entries()) {
      for (const nextNode of node.next) {
        const nextState = Array.from(this.stateMap.entries())
          .find(([s, n]) => n.id === nextNode.id)?.[0];
        if (nextState !== undefined) {
          transitions.push({
            from: state,
            to: nextState,
            nodeType: node.type,
            condition: node.data.condition || null
          });
        }
      }
    }
    return transitions;
  }
}

/**
 * Advanced Flattening with Anti-Analysis Features
 */
class AdvancedControlFlowFlattener extends ControlFlowFlattener {
  constructor() {
    super();
    this.deadCodeInsertion = true;
    this.junkStateInsertion = true;
    this.stateReordering = true;
  }

  /**
   * Insert dead code paths to confuse analysis
   */
  _insertDeadCode(codeArray) {
    if (!this.deadCodeInsertion) return codeArray;

    const deadPatterns = [
      'if(Math.random() > 2) { var x = "unreachable"; }',
      'try { throw new Error("never"); } catch(e) { }',
      'switch(99999) { case 0: break; }',
      '/*jshint dead_code:false*/ if(false) { var y = 42; }'
    ];

    for (let i = 0; i < codeArray.length; i += 3) {
      const pattern = deadPatterns[Math.floor(Math.random() * deadPatterns.length)];
      codeArray.splice(i, 0, '      // ' + pattern);
    }

    return codeArray;
  }

  /**
   * Insert junk states that are unreachable
   */
  _insertJunkStates(stateNodeMap) {
    if (!this.junkStateInsertion) return;

    for (let i = 0; i < 5; i++) {
      const junkState = this.stateCounter++;
      this.stateMap.set(junkState, {
        type: 'junk',
        data: { value: Math.random().toString(36) }
      });
    }
  }

  /**
   * Reorder states to non-sequential arrangement
   */
  _reorderStates(stateNodeMap) {
    if (!this.stateReordering) return stateNodeMap;

    const entries = Array.from(stateNodeMap.entries());
    const shuffled = entries.sort(() => Math.random() - 0.5);
    return new Map(shuffled);
  }

  /**
   * Override flattening with advanced techniques
   */
  flattenGraph() {
    const baseCode = super.flattenGraph().split('\n');
    const enhanced = this._insertDeadCode([...baseCode]);
    return enhanced.join('\n');
  }
}

/**
 * Code Generator for flattened structures
 */
class FlattenedCodeGenerator {
  constructor() {
    this.flattener = new AdvancedControlFlowFlattener();
    this.generatedCode = '';
  }

  /**
   * Generate flattened code from function
   */
  generateFromFunction(func, options = {}) {
    this.flattener.enableOpaquePredicates = options.opaquePredicates !== false;
    this.flattener.enableVariableEncoding = options.variableEncoding !== false;
    this.flattener.deadCodeInsertion = options.deadCode !== false;
    this.flattener.junkStateInsertion = options.junkStates !== false;
    this.flattener.stateReordering = options.stateReordering !== false;

    if (options.polymorphicMode) {
      this.flattener.setPolymorphicMode(options.polymorphicMode);
    }

    this.flattener.parseFunctionToGraph(func);
    this.generatedCode = this.flattener.getFlattenedCode();
    return this.generatedCode;
  }

  /**
   * Generate complete wrapped function
   */
  generateCompleteFunction(func, functionName = 'flattened', options = {}) {
    const flattenedBody = this.generateFromFunction(func, options);

    return `function ${functionName}() {
  ${flattenedBody}
}`;
  }

  /**
   * Get analysis data
   */
  getAnalysis() {
    return {
      stateCount: this.flattener.stateCounter,
      transitions: this.flattener.getStateTransitions(),
      polymorphicMode: this.flattener.polymorphicMode,
      features: {
        opaquePredicates: this.flattener.enableOpaquePredicates,
        variableEncoding: this.flattener.enableVariableEncoding,
        deadCode: this.flattener.deadCodeInsertion,
        junkStates: this.flattener.junkStateInsertion,
        stateReordering: this.flattener.stateReordering
      }
    };
  }

  /**
   * Get generated code
   */
  getCode() {
    return this.generatedCode;
  }
}

// Export
module.exports = {
  CFGNode,
  ControlFlowGraph,
  PolymorphicState,
  OpaquePredicates,
  ControlFlowFlattener,
  AdvancedControlFlowFlattener,
  FlattenedCodeGenerator
};

// Example usage
if (require.main === module) {
  console.log('=== Control Flow Flattening Demonstration ===\n');

  // Example function to flatten
  function exampleLogic(x) {
    if (x > 0) {
      return x * 2;
    } else {
      return x * 3;
    }
  }

  const generator = new FlattenedCodeGenerator();

  console.log('--- Numeric State Mode ---');
  const code1 = generator.generateFromFunction(exampleLogic, {
    polymorphicMode: PolymorphicState.MODES.NUMERIC
  });
  console.log(code1);
  console.log('\nAnalysis:', JSON.stringify(generator.getAnalysis(), null, 2));

  console.log('\n--- Object State Mode ---');
  const code2 = generator.generateFromFunction(exampleLogic, {
    polymorphicMode: PolymorphicState.MODES.OBJECT
  });
  console.log(code2);

  console.log('\n--- Computed State Mode ---');
  const code3 = generator.generateFromFunction(exampleLogic, {
    polymorphicMode: PolymorphicState.MODES.COMPUTED
  });
  console.log(code3);
}
