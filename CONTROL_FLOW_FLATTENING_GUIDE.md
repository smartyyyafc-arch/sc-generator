# Control Flow Flattening with Polymorphic Obfuscation

## Overview

Control Flow Flattening is an advanced code obfuscation technique that transforms complex control structures (conditionals, loops, function calls) into a state machine with opaque state transitions. This implementation adds polymorphic layers where state representations can vary across execution, making static analysis and decompilation significantly more difficult.

## Key Concepts

### 1. Control Flow Graph (CFG)

A CFG represents a program as a directed graph where:
- **Nodes** represent code statements (assignments, conditionals, returns)
- **Edges** represent control flow transitions
- **Flattening** converts this into a dispatch-based state machine

### 2. Polymorphic State Representation

States can be encoded in multiple formats to evade detection:

| Mode | Format | Example | Use Case |
|------|--------|---------|----------|
| **NUMERIC** | Integer | `state = 42` | Default, minimal overhead |
| **STRING** | Character encoding | `state = 'ABCD'` | Confuses string analysis |
| **OBJECT** | Object with fields | `state = {_s: 42, _v: 0.5}` | Defeats simple property access |
| **ARRAY** | Array indices | `state = [42, 43]` | Multi-valued state transitions |
| **COMPUTED** | Opaque expressions | `state = ~42 & -1` | Most resistant to simplification |

### 3. Opaque Predicates

Meaningless conditions that always evaluate to true/false but are hard to simplify:

```javascript
// Always true
!(1 === 0)                          // Logical negation
(3735928559 >>> 0) > 0             // Bitwise operations
((1n << 30n) !== 0n)              // BigInt operations

// Always false
(1 === 0)
(Math.random() === -1)
(NaN === NaN)
```

### 4. State Machine Dispatch

Original code:
```javascript
if (x > 0) {
  result = x * 2;
} else {
  result = x * 3;
}
return result;
```

Flattened to:
```javascript
let state = 0;
while (true) {
  switch (state) {
    case 0:
      if (x > 0 && !(1 === 0)) {
        state = 1;
      } else {
        state = 2;
      }
      break;
    case 1:
      result = x * 2;
      state = 3;
      break;
    case 2:
      result = x * 3;
      state = 3;
      break;
    case 3:
      return result;
  }
}
```

## Architecture

### Core Classes

#### **ControlFlowGraph**
Represents and manages the control flow structure.

```javascript
const graph = new ControlFlowGraph();
const node1 = graph.createNode('assignment', { variable: 'x', value: 5 });
const node2 = graph.createNode('return', { value: 'x' });
graph.addEdge(node1, node2);
```

#### **PolymorphicState**
Generates code for state representation in different modes.

```javascript
const state = new PolymorphicState(42, PolymorphicState.MODES.OBJECT);
console.log(state.generateCode('myState'));        // let myState = {_s: 42, _v: ...}
console.log(state.generateComparison('myState', 42)); // myState._s === 42
console.log(state.generateAssignment('myState', 99)); // myState = {_s: 99, ...}
```

#### **OpaquePredicates**
Creates hard-to-analyze conditions.

```javascript
const truePredicate = OpaquePredicates.generateAlwaysTrue();
const falsePredicate = OpaquePredicates.generateAlwaysFalse();
const ambiguous = OpaquePredicates.generateAmbiguous();
```

#### **ControlFlowFlattener**
Converts functions into flattened state machines.

```javascript
const flattener = new ControlFlowFlattener();

function originalFunc(x) {
  if (x > 0) return x * 2;
  return x * 3;
}

flattener.parseFunctionToGraph(originalFunc);
flattener.setPolymorphicMode(PolymorphicState.MODES.COMPUTED);
const flattened = flattener.getFlattenedCode();
```

#### **FlattenedCodeGenerator**
High-level interface for code generation with multiple options.

```javascript
const generator = new FlattenedCodeGenerator();

const flatCode = generator.generateFromFunction(func, {
  polymorphicMode: 'object',
  opaquePredicates: true,
  variableEncoding: true,
  deadCode: true,
  junkStates: true,
  stateReordering: true
});

const analysis = generator.getAnalysis();
// {
//   stateCount: 5,
//   transitions: [...],
//   polymorphicMode: 'object',
//   features: { ... }
// }
```

## Usage Examples

### Example 1: Basic Flattening

```javascript
const { FlattenedCodeGenerator, PolymorphicState } = require('./control-flow-flattening');

function calculate(a, b) {
  if (a > b) {
    return a - b;
  } else {
    return b - a;
  }
}

const generator = new FlattenedCodeGenerator();
const flatCode = generator.generateCompleteFunction(
  calculate,
  'obfuscatedCalc',
  { polymorphicMode: PolymorphicState.MODES.NUMERIC }
);

console.log(flatCode);
// Output: Complete function with flattened state machine
```

### Example 2: Polymorphic Code Generation

```javascript
const generator = new FlattenedCodeGenerator();

// Generate multiple versions of same logic with different state encodings
const modes = [
  PolymorphicState.MODES.NUMERIC,
  PolymorphicState.MODES.OBJECT,
  PolymorphicState.MODES.COMPUTED
];

modes.forEach(mode => {
  const code = generator.generateFromFunction(myFunc, {
    polymorphicMode: mode,
    opaquePredicates: true,
    variableEncoding: true
  });
  console.log(`Mode: ${mode}`);
  console.log(code);
  console.log('---');
});
```

### Example 3: Analysis and Inspection

```javascript
const generator = new FlattenedCodeGenerator();
generator.generateFromFunction(targetFunc, {
  polymorphicMode: PolymorphicState.MODES.OBJECT,
  deadCode: true,
  junkStates: true
});

const analysis = generator.getAnalysis();
console.log('State count:', analysis.stateCount);
console.log('Transitions:', analysis.transitions.length);
console.log('Features enabled:', analysis.features);
```

## Anti-Analysis Features

### 1. Dead Code Insertion
Unreachable code paths mixed with real logic:
```javascript
if (Math.random() > 2) {
  var x = "unreachable";
}
switch (99999) { case 0: break; }
```

### 2. Junk States
Unreachable states in the state machine that create false control flow paths during analysis.

### 3. State Reordering
States are not sequential (0, 1, 2, 3) but randomly ordered, breaking linear analysis assumptions.

### 4. Variable Encoding
Variable names are replaced with randomized identifiers:
- `state` → `_a7k3m`
- `result` → `_f2p9q`

### 5. Opaque Predicate Wrapping
All conditions are wrapped with meaningless but hard-to-simplify expressions:
```javascript
// Original: if (x > 0)
// Obfuscated: if ((x > 0) && !(1 === 0))
// Or:        if ((x > 0) || (NaN === NaN))
```

## Performance Characteristics

| Aspect | Impact | Mitigation |
|--------|--------|-----------|
| **Code Size** | 3-5x increase | Use selective flattening |
| **Execution Speed** | 1-2x slower | Use numeric mode for performance |
| **Analysis Resistance** | Very High | Multiple layers of obfuscation |
| **Reversibility** | Difficult | State machine more complex than original |

## Security Considerations

### Strengths
- Highly resistant to static analysis
- Opaque predicates difficult to simplify
- Polymorphic representations evade pattern matching
- State machine harder to trace manually

### Limitations
- Dynamic analysis can still reveal control flow
- Semantic information may be preserved in operations
- Very large increase in code size
- Not suitable for real-time applications

## Integration with Metamorphic Systems

Control flow flattening complements metamorphic code generation:

```javascript
const { MetamorphicWrapper } = require('./metamorphic-wrapper');
const { FlattenedCodeGenerator } = require('./control-flow-flattening');

// Create morphing wrapper
const wrapper = new MetamorphicWrapper();

// Get original payload
const payload = wrapper.encode(sensitiveData);

// Apply control flow flattening to extraction logic
const generator = new FlattenedCodeGenerator();
const extractionLogic = generator.generateCompleteFunction(
  () => extractFromPayload(payload),
  'extract',
  { polymorphicMode: 'computed' }
);
```

## API Reference

### PolymorphicState

```javascript
class PolymorphicState {
  constructor(stateValue, mode)
  generateCode(variableName)              // Get initialization code
  generateComparison(varName, value)      // Get comparison code
  generateAssignment(varName, value)      // Get assignment code
  
  static MODES = {
    NUMERIC: 'numeric',
    STRING: 'string',
    OBJECT: 'object',
    ARRAY: 'array',
    COMPUTED: 'computed'
  }
}
```

### ControlFlowFlattener

```javascript
class ControlFlowFlattener {
  parseFunctionToGraph(func)              // Parse function into CFG
  flattenGraph()                          // Convert CFG to flattened code
  getFlattenedCode()                      // Get flattened code string
  setPolymorphicMode(mode)                // Set state representation mode
  getStateTransitions()                   // Get transition map
  
  enableOpaquePredicates: boolean
  enableVariableEncoding: boolean
}
```

### FlattenedCodeGenerator

```javascript
class FlattenedCodeGenerator {
  generateFromFunction(func, options)     // Generate flattened code
  generateCompleteFunction(func, name, options)  // Generate complete function
  getCode()                               // Get generated code
  getAnalysis()                           // Get analysis metrics
}
```

## Testing

Run the comprehensive test suite:

```bash
node control-flow-flattening.test.js
```

Test coverage includes:
- CFG node and edge creation
- All polymorphic state modes
- Opaque predicate generation and evaluation
- Code generation and parsing
- Variable encoding
- Feature combinations

## Output Examples

### Numeric Mode Output
```javascript
function obfuscated() {
  let _abc = 0;
  while(true) {
    switch(_abc) {
      case 0:
        if (x > 0 && !(1 === 0)) {
          _abc = 1;
        } else {
          _abc = 2;
        }
        break;
      // ...
    }
  }
}
```

### Object Mode Output
```javascript
function obfuscated() {
  let _xyz = {_s: 0, _v: 0.245};
  while(true) {
    switch(_xyz._s) {
      case 0:
        if (x > 0 || (NaN === NaN)) {
          _xyz = {_s: 1, _v: Math.random()};
        } else {
          _xyz = {_s: 2, _v: Math.random()};
        }
        break;
      // ...
    }
  }
}
```

### Computed Mode Output
```javascript
function obfuscated() {
  let _pqr = (~0 & -1);
  while(true) {
    switch(_pqr) {
      case 0:
        if ((x > 0) && ((3735928559 >>> 0) > 0)) {
          _pqr = (1 + 0);
        } else {
          _pqr = (~1 & -1);
        }
        break;
      // ...
    }
  }
}
```

## Advanced Customization

### Custom Opaque Predicates

```javascript
// Extend OpaquePredicates with domain-specific predicates
class CustomOpaquePredicates extends OpaquePredicates {
  static generateDomainSpecific() {
    return `(window.location.href.length > 0)`;
  }
}
```

### Custom State Modes

```javascript
// Create new polymorphic state mode
class CustomState extends PolymorphicState {
  generateCode(varName) {
    // Custom implementation
    return `let ${varName} = encode(${this.stateValue})`;
  }
}
```

## Performance Optimization Tips

1. **Use Numeric Mode** for speed-sensitive code
2. **Disable Dead Code** for size-sensitive applications
3. **Selective Flattening** - only flatten critical functions
4. **Pre-compute Opaque Predicates** to avoid runtime overhead
5. **Combine with Other Techniques** like string encoding and control flow guards

## Future Enhancements

- [ ] Loop flattening (for/while/do-while)
- [ ] Function call virtualization
- [ ] Semantic-preserving transformations
- [ ] Machine learning-resistant analysis
- [ ] Hardware-accelerated state machine execution
- [ ] Quantum-resistant encryption for state values

## References

1. Collberg et al. - "A Taxonomy of Obfuscating Transformations"
2. Drape & Fitch - "Control Flow Flattening as a Defensive Measure"
3. Wang et al. - "Software Obfuscation Schemes: A Survey"

## License

This implementation is part of the SC-Generator toolkit.
