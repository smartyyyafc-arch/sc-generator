/**
 * Metamorphic Wrapper: Practical Integration Examples
 *
 * Real-world use cases and integration patterns
 */

const {
  MetamorphicWrapper,
  AdvancedMetamorphicWrapper,
  analyzeMetamorphism
} = require('./metamorphic-wrapper');

// ============================================================================
// Example 1: Simple Payload Serialization
// ============================================================================

console.log('\n' + '='.repeat(70));
console.log('EXAMPLE 1: Simple Payload Serialization');
console.log('='.repeat(70));

class SimplePayloadEncoder {
  constructor(seed) {
    this.wrapper = new MetamorphicWrapper(seed);
  }

  encode(data) {
    const json = JSON.stringify(data);
    return this.wrapper.encode(json);
  }

  decode(wrapped) {
    const json = this.wrapper.decode(wrapped);
    return JSON.parse(json);
  }
}

// Usage
const encoder = new SimplePayloadEncoder(111);
const payload = {
  user: 'alice@example.com',
  action: 'login',
  timestamp: Date.now(),
  ip: '192.168.1.100'
};

const encoded = encoder.encode(payload);
console.log('Original:', payload);
console.log('Encoded Strategy:', encoded.__metamorphic.strategyName);
console.log('Payload Size:', JSON.stringify(encoded).length, 'bytes');

// Store or transmit encoded payload...

const decoded = encoder.decode(encoded);
console.log('Decoded:', decoded);
console.log('Match:', JSON.stringify(payload) === JSON.stringify(decoded) ? 'YES' : 'NO');

// ============================================================================
// Example 2: Dynamic Obfuscation Based on Sensitivity
// ============================================================================

console.log('\n' + '='.repeat(70));
console.log('EXAMPLE 2: Sensitivity-Based Morphing');
console.log('='.repeat(70));

class SensitivityAwareEncoder {
  constructor() {
    this.publicWrapper = new MetamorphicWrapper();
    this.privateWrapper = new AdvancedMetamorphicWrapper();

    // Configure for maximum security
    this.privateWrapper.configureMorphing({
      randomizeMetadata: true,
      addDecoys: true,
      varyNesting: true
    });
  }

  encode(data, sensitivity = 'public') {
    const json = JSON.stringify(data);

    if (sensitivity === 'public') {
      return this.publicWrapper.encode(json);
    } else if (sensitivity === 'private') {
      return this.privateWrapper.encode(json);
    } else if (sensitivity === 'confidential') {
      // Double encode for maximum obfuscation
      const firstPass = this.privateWrapper.encode(json);
      const secondPass = this.privateWrapper.encode(JSON.stringify(firstPass));
      return secondPass;
    }
  }

  decode(wrapped, sensitivity = 'public') {
    if (sensitivity === 'confidential') {
      const firstDecode = this.privateWrapper.decode(wrapped);
      const parsed = JSON.parse(firstDecode);
      return JSON.parse(this.privateWrapper.decode(parsed));
    } else if (sensitivity === 'private') {
      return JSON.parse(this.privateWrapper.decode(wrapped));
    } else {
      return JSON.parse(this.publicWrapper.decode(wrapped));
    }
  }
}

// Usage
const sensitivityEncoder = new SensitivityAwareEncoder();

const publicData = { message: 'Hello World' };
const privateData = { password: 'secret123' };
const confidentialData = { apiKey: 'sk_live_abc123xyz' };

const pubEncoded = sensitivityEncoder.encode(publicData, 'public');
const privEncoded = sensitivityEncoder.encode(privateData, 'private');
const confEncoded = sensitivityEncoder.encode(confidentialData, 'confidential');

console.log('Public Data Size:', JSON.stringify(pubEncoded).length);
console.log('Private Data Size:', JSON.stringify(privEncoded).length);
console.log('Confidential Data Size:', JSON.stringify(confEncoded).length);

console.log('\nPublic Decoded:', sensitivityEncoder.decode(pubEncoded, 'public'));
console.log('Private Decoded:', sensitivityEncoder.decode(privEncoded, 'private'));
console.log('Confidential Decoded:', sensitivityEncoder.decode(confEncoded, 'confidential'));

// ============================================================================
// Example 3: Payload Versioning with Strategy Tracking
// ============================================================================

console.log('\n' + '='.repeat(70));
console.log('EXAMPLE 3: Payload Versioning & Strategy History');
console.log('='.repeat(70));

class VersionedPayloadStore {
  constructor(seed) {
    this.wrapper = new AdvancedMetamorphicWrapper(seed);
    this.store = [];
  }

  addPayload(data, version = 1) {
    const json = JSON.stringify({ version, data });
    const encoded = this.wrapper.encode(json);

    this.store.push({
      id: this.store.length,
      strategy: encoded.__metamorphic.strategyName,
      execution: encoded.__metamorphic.execution,
      timestamp: encoded.__metamorphic.timestamp,
      encoded
    });

    return this.store[this.store.length - 1].id;
  }

  getPayload(id) {
    const entry = this.store[id];
    if (!entry) return null;

    const decoded = this.wrapper.decode(entry.encoded);
    return JSON.parse(decoded);
  }

  getHistory() {
    return this.store.map(entry => ({
      id: entry.id,
      strategy: entry.strategy,
      execution: entry.execution,
      timestamp: new Date(entry.timestamp).toISOString()
    }));
  }

  getStatistics() {
    const strategies = new Map();
    this.store.forEach(entry => {
      strategies.set(
        entry.strategy,
        (strategies.get(entry.strategy) || 0) + 1
      );
    });

    return {
      totalPayloads: this.store.length,
      strategyDistribution: Object.fromEntries(strategies),
      averageSize: this.store.reduce(
        (sum, entry) => sum + JSON.stringify(entry.encoded).length,
        0
      ) / this.store.length
    };
  }
}

// Usage
const versionedStore = new VersionedPayloadStore(222);

// Add multiple payloads
const ids = [];
ids.push(versionedStore.addPayload({ user: 'alice', role: 'admin' }));
ids.push(versionedStore.addPayload({ user: 'bob', role: 'user' }));
ids.push(versionedStore.addPayload({ user: 'charlie', role: 'viewer' }));

console.log('Added 3 payloads');
console.log('Strategy History:');
versionedStore.getHistory().forEach(entry => {
  console.log(`  ID ${entry.id}: ${entry.strategy} (exec=${entry.execution})`);
});

console.log('\nStatistics:', versionedStore.getStatistics());

console.log('\nRetrieving payload ID 1:', versionedStore.getPayload(1));

// ============================================================================
// Example 4: Payload Comparison & Anomaly Detection
// ============================================================================

console.log('\n' + '='.repeat(70));
console.log('EXAMPLE 4: Payload Analysis & Anomaly Detection');
console.log('='.repeat(70));

class PayloadAnalyzer {
  constructor() {
    this.baseline = null;
    this.samples = [];
  }

  recordSample(encoded) {
    const analysis = analyzeMetamorphism(encoded);
    this.samples.push(analysis);

    if (!this.baseline) {
      this.baseline = analysis;
    }

    return analysis;
  }

  detectAnomalies() {
    if (!this.baseline) return [];

    const anomalies = [];
    this.samples.forEach((sample, idx) => {
      const issues = [];

      // Check strategy consistency
      if (sample.strategyId !== this.baseline.strategyId && idx === 0) {
        issues.push(`Different strategy: ${sample.strategy}`);
      }

      // Check payload shape
      if (sample.payloadShape.length !== this.baseline.payloadShape.length) {
        issues.push(`Different payload shape: ${sample.payloadShape.length} vs ${this.baseline.payloadShape.length}`);
      }

      // Check depth
      if (Math.abs(sample.depth - this.baseline.depth) > 2) {
        issues.push(`Unusual depth: ${sample.depth} (baseline ${this.baseline.depth})`);
      }

      // Check size variation
      if (Math.abs(sample.size - this.baseline.size) / this.baseline.size > 0.3) {
        issues.push(`Large size variation: ${sample.size} bytes`);
      }

      if (issues.length > 0) {
        anomalies.push({ sample: idx, issues });
      }
    });

    return anomalies;
  }

  getSummary() {
    if (this.samples.length === 0) return null;

    return {
      totalSamples: this.samples.length,
      strategies: new Set(this.samples.map(s => s.strategy)).size,
      avgDepth: this.samples.reduce((s, a) => s + a.depth, 0) / this.samples.length,
      avgSize: this.samples.reduce((s, a) => s + a.size, 0) / this.samples.length,
      anomalies: this.detectAnomalies().length
    };
  }
}

// Usage
const analyzer = new PayloadAnalyzer();
const wrapper = new AdvancedMetamorphicWrapper(333);

console.log('Analyzing 5 encoded payloads...');
for (let i = 0; i < 5; i++) {
  const encoded = wrapper.encode('Test Data');
  const analysis = analyzer.recordSample(encoded);
  console.log(`Sample ${i}: ${analysis.strategy} (size=${analysis.size}, depth=${analysis.depth})`);
}

console.log('\nPayload Analysis Summary:');
console.log(analyzer.getSummary());

const anomalies = analyzer.detectAnomalies();
if (anomalies.length > 0) {
  console.log('\nAnomalies Detected:');
  anomalies.forEach(anom => {
    console.log(`  Sample ${anom.sample}:`, anom.issues.join(', '));
  });
} else {
  console.log('\nNo anomalies detected - payload structure consistent');
}

// ============================================================================
// Example 5: Batch Processing with Progress Tracking
// ============================================================================

console.log('\n' + '='.repeat(70));
console.log('EXAMPLE 5: Batch Processing with Progress Tracking');
console.log('='.repeat(70));

class BatchProcessor {
  constructor(seed, batchSize = 10) {
    this.wrapper = new MetamorphicWrapper(seed);
    this.batchSize = batchSize;
    this.results = [];
  }

  processBatch(items, operation) {
    console.log(`Processing ${items.length} items in batches of ${this.batchSize}...`);

    for (let i = 0; i < items.length; i += this.batchSize) {
      const batch = items.slice(i, Math.min(i + this.batchSize, items.length));
      const progress = Math.floor((i / items.length) * 100);

      const batchResults = batch.map(item => {
        const processed = operation(item);
        const encoded = this.wrapper.encode(JSON.stringify(processed));
        return {
          original: item,
          processed,
          strategy: encoded.__metamorphic.strategyName,
          encoded
        };
      });

      this.results.push(...batchResults);

      console.log(`  [${progress}%] Processed items ${i}-${Math.min(i + this.batchSize, items.length)}`);
    }

    return this.results;
  }

  getStats() {
    return {
      totalProcessed: this.results.length,
      strategiesUsed: new Set(this.results.map(r => r.strategy)).size,
      totalSize: this.results.reduce(
        (sum, r) => sum + JSON.stringify(r.encoded).length,
        0
      ),
      averageSize: this.results.reduce(
        (sum, r) => sum + JSON.stringify(r.encoded).length,
        0
      ) / this.results.length
    };
  }
}

// Usage
const processor = new BatchProcessor(444, 3);
const itemsToProcess = [
  { id: 1, name: 'Item 1', value: 100 },
  { id: 2, name: 'Item 2', value: 200 },
  { id: 3, name: 'Item 3', value: 300 },
  { id: 4, name: 'Item 4', value: 400 },
  { id: 5, name: 'Item 5', value: 500 },
  { id: 6, name: 'Item 6', value: 600 }
];

// Process with transformation
processor.processBatch(itemsToProcess, item => ({
  ...item,
  processed: true,
  processedAt: Date.now(),
  hash: Math.random().toString(36).substring(7)
}));

console.log('\nBatch Processing Statistics:');
console.log(processor.getStats());

// ============================================================================
// Example 6: Request/Response Wrapping for HTTP APIs
// ============================================================================

console.log('\n' + '='.repeat(70));
console.log('EXAMPLE 6: HTTP API Request/Response Wrapping');
console.log('='.repeat(70));

class APIPayloadWrapper {
  constructor(seed) {
    this.wrapper = new AdvancedMetamorphicWrapper(seed);
    this.wrapper.configureMorphing({
      randomizeMetadata: true,
      addDecoys: false,
      varyNesting: true
    });
  }

  wrapRequest(method, path, data) {
    const request = { method, path, data, timestamp: Date.now() };
    const encoded = this.wrapper.encode(JSON.stringify(request));

    return {
      __wrapped: true,
      __version: 1,
      __strategy: encoded.__metamorphic.strategyName,
      payload: encoded
    };
  }

  unwrapRequest(wrapped) {
    const decoded = this.wrapper.decode(wrapped.payload);
    return JSON.parse(decoded);
  }

  wrapResponse(statusCode, data, headers = {}) {
    const response = { statusCode, data, headers, timestamp: Date.now() };
    const encoded = this.wrapper.encode(JSON.stringify(response));

    return {
      __wrapped: true,
      __version: 1,
      __strategy: encoded.__metamorphic.strategyName,
      payload: encoded
    };
  }

  unwrapResponse(wrapped) {
    const decoded = this.wrapper.decode(wrapped.payload);
    return JSON.parse(decoded);
  }
}

// Usage
const apiWrapper = new APIPayloadWrapper(555);

// Wrap a request
const request = apiWrapper.wrapRequest('POST', '/api/users', {
  email: 'user@example.com',
  name: 'John Doe'
});

console.log('Wrapped Request:');
console.log(`  Strategy: ${request.__strategy}`);
console.log(`  Size: ${JSON.stringify(request).length} bytes`);

// Unwrap for processing
const unwrappedRequest = apiWrapper.unwrapRequest(request);
console.log('Unwrapped Request:');
console.log(unwrappedRequest);

// Wrap a response
const response = apiWrapper.wrapResponse(201, {
  id: 'user_123',
  email: 'user@example.com',
  created: Date.now()
}, { 'Content-Type': 'application/json' });

console.log('\nWrapped Response:');
console.log(`  Strategy: ${response.__strategy}`);
console.log(`  Size: ${JSON.stringify(response).length} bytes`);

// Unwrap response
const unwrappedResponse = apiWrapper.unwrapResponse(response);
console.log('Unwrapped Response:');
console.log(unwrappedResponse);

// ============================================================================
// Summary
// ============================================================================

console.log('\n' + '='.repeat(70));
console.log('METAMORPHIC WRAPPER - INTEGRATION EXAMPLES COMPLETE');
console.log('='.repeat(70));
console.log(`
Key Takeaways:

1. Simple Serialization: Wrap JSON data with minimal overhead
2. Sensitivity-Based: Apply different morphing based on data sensitivity
3. Versioning: Track payload versions and strategies over time
4. Analysis: Detect anomalies and unexpected payload structures
5. Batch Processing: Efficiently process multiple items with progress
6. API Integration: Wrap HTTP requests and responses transparently

Each approach demonstrates how the metamorphic wrapper adapts to different
use cases while maintaining full encode/decode integrity.
`);
