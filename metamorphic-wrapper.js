/**
 * Metamorphic Wrapper for Multi-Encoding System
 *
 * Provides dynamic payload structure transformation where:
 * - Encoding layer order varies between runs
 * - Serialization format changes (nested, flat, mixed)
 * - Intermediate states are selectively exposed or hidden
 * - Metadata structure morphs between runs
 *
 * This enables evasion of static analysis by preventing observers from
 * predicting the payload structure or encoding strategy in advance.
 */

const {
  encodeBase64,
  decodeBase64,
  encodeHex,
  decodeHex,
  encodeArray,
  decodeArray
} = require('./multi-encoding');

/**
 * Strategy Registry: Different encoding approaches
 */
const ENCODING_STRATEGIES = {
  // Strategy 1: Classic linear ordering (Base64 → Hex → Array)
  LINEAR: {
    name: 'LINEAR',
    id: 1,
    encode: (input) => {
      const base64 = encodeBase64(input);
      const hex = encodeHex(base64);
      const array = encodeArray(hex);
      return { base64, hex, array };
    },
    decode: (payload) => {
      const hex = decodeArray(payload.array);
      const base64 = decodeHex(hex);
      return decodeBase64(base64);
    }
  },

  // Strategy 2: Reverse linear ordering (Array → Hex → Base64)
  REVERSE_LINEAR: {
    name: 'REVERSE_LINEAR',
    id: 2,
    encode: (input) => {
      const array = encodeArray(encodeHex(encodeBase64(input)));
      return { array };
    },
    decode: (payload) => {
      return decodeBase64(decodeHex(decodeArray(payload.array)));
    }
  },

  // Strategy 3: Nested structure with hiding intermediate states
  NESTED_HIDDEN: {
    name: 'NESTED_HIDDEN',
    id: 3,
    encode: (input) => {
      const base64 = encodeBase64(input);
      const hex = encodeHex(base64);
      const array = encodeArray(hex);
      // Only expose the outermost encoding
      return { data: { nested: { payload: array } } };
    },
    decode: (payload) => {
      const array = payload.data.nested.payload;
      const hex = decodeArray(array);
      const base64 = decodeHex(hex);
      return decodeBase64(base64);
    }
  },

  // Strategy 4: Interleaved metadata and payload
  METADATA_INTERLEAVED: {
    name: 'METADATA_INTERLEAVED',
    id: 4,
    encode: (input) => {
      const base64 = encodeBase64(input);
      const hex = encodeHex(base64);
      const array = encodeArray(hex);
      return {
        meta: { version: 1, type: 'encoded' },
        payload: array,
        meta2: { checksum: Math.random().toString(36).substring(7) }
      };
    },
    decode: (payload) => {
      const hex = decodeArray(payload.payload);
      const base64 = decodeHex(hex);
      return decodeBase64(base64);
    }
  },

  // Strategy 5: Flat with encoding indicators
  FLAT_INDEXED: {
    name: 'FLAT_INDEXED',
    id: 5,
    encode: (input) => {
      const base64 = encodeBase64(input);
      const hex = encodeHex(base64);
      const array = encodeArray(hex);
      // Flatten with numbered indices
      const flat = {};
      array.forEach((elem, idx) => {
        flat[`_${idx}`] = elem;
      });
      return {
        __type: 'FLAT_INDEXED',
        __len: array.length,
        ...flat
      };
    },
    decode: (payload) => {
      const len = payload.__len;
      const array = [];
      for (let i = 0; i < len; i++) {
        array.push(payload[`_${i}`]);
      }
      const hex = decodeArray(array);
      const base64 = decodeHex(hex);
      return decodeBase64(base64);
    }
  },

  // Strategy 6: Base64 directly without intermediate exposures
  BASE64_ONLY: {
    name: 'BASE64_ONLY',
    id: 6,
    encode: (input) => {
      return { direct: encodeBase64(input) };
    },
    decode: (payload) => {
      return decodeBase64(payload.direct);
    }
  },

  // Strategy 7: Hex-only with special formatting
  HEX_ONLY: {
    name: 'HEX_ONLY',
    id: 7,
    encode: (input) => {
      const base64 = encodeBase64(input);
      const hex = encodeHex(base64);
      // Chunk hex by random sizes
      const chunks = [];
      let pos = 0;
      while (pos < hex.length) {
        const chunkSize = Math.floor(Math.random() * 10) + 2;
        chunks.push(hex.substr(pos, chunkSize));
        pos += chunkSize;
      }
      return { chunks };
    },
    decode: (payload) => {
      const hex = payload.chunks.join('');
      const base64 = decodeHex(hex);
      return decodeBase64(base64);
    }
  },

  // Strategy 8: Deep nesting with red herrings
  DEEP_NESTED_DECOYS: {
    name: 'DEEP_NESTED_DECOYS',
    id: 8,
    encode: (input) => {
      const base64 = encodeBase64(input);
      const hex = encodeHex(base64);
      const array = encodeArray(hex);
      return {
        decoy1: { fake: 'data1' },
        real: {
          decoy2: { fake: 'data2' },
          actual: {
            decoy3: { fake: 'data3' },
            value: array
          }
        },
        decoy4: { fake: 'data4' }
      };
    },
    decode: (payload) => {
      const array = payload.real.actual.value;
      const hex = decodeArray(array);
      const base64 = decodeHex(hex);
      return decodeBase64(base64);
    }
  },

  // Strategy 9: Array split across multiple fields
  SPLIT_ARRAY: {
    name: 'SPLIT_ARRAY',
    id: 9,
    encode: (input) => {
      const base64 = encodeBase64(input);
      const hex = encodeHex(base64);
      const array = encodeArray(hex);
      // Split array into chunks
      const midpoint = Math.floor(array.length / 2);
      return {
        part1: array.slice(0, midpoint),
        part2: array.slice(midpoint)
      };
    },
    decode: (payload) => {
      const array = [...payload.part1, ...payload.part2];
      const hex = decodeArray(array);
      const base64 = decodeHex(hex);
      return decodeBase64(base64);
    }
  },

  // Strategy 10: Object-based array with property names as encoding hints
  OBJECT_ARRAY: {
    name: 'OBJECT_ARRAY',
    id: 10,
    encode: (input) => {
      const base64 = encodeBase64(input);
      const hex = encodeHex(base64);
      const array = encodeArray(hex);
      // Convert array to object with hex-based keys
      const obj = {};
      array.forEach((val, idx) => {
        const key = `x${idx.toString(16).padStart(4, '0')}`;
        obj[key] = val;
      });
      return { data: obj, len: array.length };
    },
    decode: (payload) => {
      const array = [];
      for (let i = 0; i < payload.len; i++) {
        const key = `x${i.toString(16).padStart(4, '0')}`;
        array.push(payload.data[key]);
      }
      const hex = decodeArray(array);
      const base64 = decodeHex(hex);
      return decodeBase64(base64);
    }
  }
};

/**
 * Metamorphic Wrapper: Core class for runtime payload transformation
 */
class MetamorphicWrapper {
  constructor(seed = null) {
    this.seed = seed || Math.random();
    this.strategy = null;
    this.executionCount = 0;
    this.lastPayload = null;
    this.selectionHistory = [];
  }

  /**
   * Select encoding strategy based on seed/execution count
   */
  selectStrategy(input) {
    const strategies = Object.values(ENCODING_STRATEGIES);

    // Deterministic selection based on seed and execution count
    const hashValue = this._hash(this.seed + this.executionCount + input);
    const strategyIndex = hashValue % strategies.length;

    this.strategy = strategies[strategyIndex];
    this.selectionHistory.push({
      execution: this.executionCount,
      strategyId: this.strategy.id,
      strategyName: this.strategy.name
    });

    return this.strategy;
  }

  /**
   * Simple hash function for deterministic strategy selection
   */
  _hash(input) {
    let hash = 0;
    const str = String(input);
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }

  /**
   * Encode with metamorphic transformation
   */
  encode(input) {
    const strategy = this.selectStrategy(input);

    const encodedPayload = strategy.encode(input);

    // Wrap with metamorphic metadata
    const wrapper = {
      __metamorphic: {
        version: 1,
        execution: this.executionCount,
        strategy: strategy.id,
        strategyName: strategy.name,
        timestamp: Date.now(),
        seed: this.seed
      },
      payload: encodedPayload
    };

    this.executionCount++;
    this.lastPayload = wrapper;

    return wrapper;
  }

  /**
   * Decode metamorphic payload
   */
  decode(wrapper) {
    const strategyId = wrapper.__metamorphic.strategy;
    const strategyName = wrapper.__metamorphic.strategyName;

    // Reconstruct strategy by ID or name
    let strategy = null;
    for (const [key, strat] of Object.entries(ENCODING_STRATEGIES)) {
      if (strat.id === strategyId || strat.name === strategyName) {
        strategy = strat;
        break;
      }
    }

    if (!strategy) {
      throw new Error(`Unknown strategy: ${strategyId} (${strategyName})`);
    }

    return strategy.decode(wrapper.payload);
  }

  /**
   * Get selection history for analysis
   */
  getSelectionHistory() {
    return [...this.selectionHistory];
  }

  /**
   * Get execution statistics
   */
  getStatistics() {
    return {
      executionCount: this.executionCount,
      seed: this.seed,
      strategiesUsed: new Set(this.selectionHistory.map(h => h.strategyName)).size,
      lastStrategy: this.strategy ? this.strategy.name : null
    };
  }
}

/**
 * Advanced Metamorphic Wrapper with additional morphing capabilities
 */
class AdvancedMetamorphicWrapper extends MetamorphicWrapper {
  constructor(seed = null) {
    super(seed);
    this.morphSettings = {
      randomizeMetadata: true,
      addDecoys: true,
      varyNesting: true
    };
  }

  /**
   * Encode with advanced morphing features
   */
  encode(input) {
    const strategy = this.selectStrategy(input);
    let payload = strategy.encode(input);

    // Apply morphing transformations
    if (this.morphSettings.addDecoys) {
      payload = this._addDecoys(payload);
    }

    if (this.morphSettings.varyNesting) {
      payload = this._varyNesting(payload);
    }

    const metadata = {
      version: 1,
      execution: this.executionCount,
      strategy: strategy.id,
      strategyName: strategy.name,
      timestamp: Date.now(),
      seed: this.seed
    };

    if (this.morphSettings.randomizeMetadata) {
      metadata.nonce = Math.random().toString(36).substring(7);
      metadata.decoyField = Math.random().toString(36).substring(7);
    }

    const wrapper = {
      __metamorphic: metadata,
      payload: payload
    };

    this.executionCount++;
    this.lastPayload = wrapper;

    return wrapper;
  }

  /**
   * Add random decoy fields to obfuscate payload structure
   */
  _addDecoys(payload) {
    // Only add decoys if payload is an object with a predictable structure
    if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
      return payload;
    }

    const decoys = {
      _decoy1: Math.random().toString(36),
      _decoy2: { nested: Math.random().toString(36) },
      _decoy3: [Math.random(), Math.random(), Math.random()]
    };

    // Insert decoys randomly within payload
    const result = { ...decoys };
    result.data = payload;
    return result;
  }

  /**
   * Vary nesting depth of payload
   */
  _varyNesting(payload) {
    const depth = Math.floor(Math.random() * 3) + 1;
    let result = payload;

    for (let i = 0; i < depth; i++) {
      result = { [`_nest${i}`]: result };
    }

    return result;
  }

  /**
   * Recursively unwrap nested payloads
   */
  _unwrapNesting(payload) {
    let result = payload;
    while (result && typeof result === 'object') {
      const keys = Object.keys(result);
      if (keys.length === 1 && keys[0].startsWith('_nest')) {
        result = result[keys[0]];
      } else if (keys.length > 0) {
        // Stop unwrapping if we hit a non-nesting structure
        break;
      } else {
        break;
      }
    }
    return result;
  }

  /**
   * Decode advanced metamorphic payload
   */
  decode(wrapper) {
    let payload = wrapper.payload;

    const strategyId = wrapper.__metamorphic.strategy;
    const strategyName = wrapper.__metamorphic.strategyName;

    let strategy = null;
    for (const [key, strat] of Object.entries(ENCODING_STRATEGIES)) {
      if (strat.id === strategyId || strat.name === strategyName) {
        strategy = strat;
        break;
      }
    }

    if (!strategy) {
      throw new Error(`Unknown strategy: ${strategyId} (${strategyName})`);
    }

    // First unwrap variable nesting added by _varyNesting
    payload = this._unwrapNesting(payload);

    // For DEEP_NESTED_DECOYS strategy, pass the unwrapped payload
    if (strategyId === 8) {
      return strategy.decode(payload);
    }

    // Then unwrap decoys if present (check all expected decoy fields)
    if (payload && typeof payload === 'object' && payload.data &&
        (payload._decoy1 !== undefined || payload._decoy2 !== undefined || payload._decoy3 !== undefined)) {
      payload = payload.data;
    }

    return strategy.decode(payload);
  }

  /**
   * Configure morphing behavior
   */
  configureMorphing(settings) {
    Object.assign(this.morphSettings, settings);
  }
}

/**
 * Utility: Compare payload structures between runs
 */
function analyzeMetamorphism(wrapper) {
  return {
    strategy: wrapper.__metamorphic.strategyName,
    strategyId: wrapper.__metamorphic.strategy,
    payloadShape: Object.keys(wrapper.payload),
    depth: calculateDepth(wrapper.payload),
    size: JSON.stringify(wrapper.payload).length,
    hasDecoys: 'data' in wrapper.payload,
    nesting: detectNestingPattern(wrapper.payload)
  };
}

function calculateDepth(obj, current = 0) {
  if (typeof obj !== 'object' || obj === null) {
    return current;
  }
  const depths = Object.values(obj).map(v => calculateDepth(v, current + 1));
  return Math.max(current, ...depths);
}

function detectNestingPattern(obj, pattern = []) {
  if (typeof obj !== 'object' || obj === null) {
    return pattern;
  }
  const keys = Object.keys(obj);
  if (keys.length === 1) {
    pattern.push(keys[0]);
    return detectNestingPattern(obj[keys[0]], pattern);
  }
  return pattern;
}

// Export for use as module
module.exports = {
  ENCODING_STRATEGIES,
  MetamorphicWrapper,
  AdvancedMetamorphicWrapper,
  analyzeMetamorphism,
  calculateDepth,
  detectNestingPattern
};

// Example usage
if (require.main === module) {
  console.log('=== Metamorphic Wrapper Demonstration ===\n');

  const testString = 'Metamorphic Test String';
  const wrapper = new AdvancedMetamorphicWrapper(42);

  console.log('--- Run 1 ---');
  const encoded1 = wrapper.encode(testString);
  console.log(`Strategy: ${encoded1.__metamorphic.strategyName}`);
  console.log(`Payload Analysis:`, analyzeMetamorphism(encoded1));
  const decoded1 = wrapper.decode(encoded1);
  console.log(`Decoded: ${decoded1}`);
  console.log(`Match: ${decoded1 === testString ? 'SUCCESS ✓' : 'FAILED ✗'}\n`);

  console.log('--- Run 2 (Same seed, different execution) ---');
  const encoded2 = wrapper.encode(testString);
  console.log(`Strategy: ${encoded2.__metamorphic.strategyName}`);
  console.log(`Payload Analysis:`, analyzeMetamorphism(encoded2));
  const decoded2 = wrapper.decode(encoded2);
  console.log(`Decoded: ${decoded2}`);
  console.log(`Match: ${decoded2 === testString ? 'SUCCESS ✓' : 'FAILED ✗'}\n`);

  console.log('--- Run 3 (Same seed, different execution) ---');
  const encoded3 = wrapper.encode(testString);
  console.log(`Strategy: ${encoded3.__metamorphic.strategyName}`);
  console.log(`Payload Analysis:`, analyzeMetamorphism(encoded3));
  const decoded3 = wrapper.decode(encoded3);
  console.log(`Decoded: ${decoded3}`);
  console.log(`Match: ${decoded3 === testString ? 'SUCCESS ✓' : 'FAILED ✗'}\n`);

  console.log('--- Selection History ---');
  console.log(wrapper.getSelectionHistory());
  console.log('\n--- Statistics ---');
  console.log(wrapper.getStatistics());

  console.log('\n--- Different Seed, More Runs ---');
  const wrapper2 = new AdvancedMetamorphicWrapper(999);
  for (let i = 0; i < 5; i++) {
    const encoded = wrapper2.encode(testString);
    console.log(`Run ${i + 1}: ${encoded.__metamorphic.strategyName}`);
  }
}
