# Environment Variable Retrieval Handler

## Overview

The `EnvVarRetrievalHandler` provides robust, multi-strategy retrieval of obfuscated environment variables with automatic encoding detection, fallback paths for compatibility, and comprehensive error handling.

## Features

### 1. **Multi-Strategy Fallback Support**
Retrieves variables using multiple naming conventions:
- Standard: `PREFIX_0`, `PREFIX_1`, etc.
- Double underscore: `PREFIX__0`, `PREFIX__1`, etc.
- Chunk naming: `PREFIX_CHUNK_0`, `PREFIX_CHUNK_1`, etc.
- Data prefixed: `PREFIX_DATA_0`, `PREFIX_DATA_1`, etc.
- No separator: `PREFIX0`, `PREFIX1`, etc.
- Hex index: `PREFIX_0x0`, `PREFIX_0x1`, etc.
- Legacy format: `XPREFIX_DATA_CHUNK_0`
- Abbreviated: `P_0`, `P_1` (first letter of prefix)
- Windows format: `PREFIX_VAR_0`
- Packed format: `PREFIXDATA_0`

### 2. **Automatic Encoding Detection**
- Detects hex-encoded data
- Detects base64-encoded data
- Handles automatic conversion between encoding formats

### 3. **Intelligent Reconstruction**
- Concatenates chunks in correct order
- Handles multi-layer encoding (Hex → Base64 → UTF-8)
- Graceful fallback for edge cases

### 4. **Performance Optimization**
- Built-in caching system
- Configurable cache behavior
- Cache statistics and management

### 5. **Robust Error Handling**
- Graceful failure modes
- Optional exceptions for strict validation
- Detailed error messages

### 6. **Compatibility & Debugging**
- Generates compatibility reports
- Shows which strategies found variables
- Encoding type analysis

## Installation

The handler is available in two versions:

```javascript
// Node.js/CommonJS
const EnvVarRetrievalHandler = require('./env-var-retrieval-handler');

// TypeScript
import EnvVarRetrievalHandler from './env-var-retrieval-handler';
```

## Basic Usage

### Simple Retrieval

```javascript
const handler = new EnvVarRetrievalHandler();

// Retrieve and decode obfuscated payload
const result = handler.retrieve('APP');

if (result.success) {
  console.log('Payload:', result.payload);
} else {
  console.log('Error:', result.error);
}
```

### With Fallback Support

```javascript
const handler = new EnvVarRetrievalHandler();

// Use all fallback strategies for maximum compatibility
const result = handler.retrieve('APP', {
  useFallback: true,
  maxChunks: 20
});
```

### With Caching

```javascript
// Create handler with caching enabled (default)
const handler = new EnvVarRetrievalHandler({
  cache: true,
  debug: false
});

// First call retrieves from environment
const result1 = handler.retrieve('APP');

// Second call uses cache (much faster)
const result2 = handler.retrieve('APP');

// Check cache stats
console.log(handler.getCacheStats());
```

## Advanced Options

### Constructor Options

```javascript
const handler = new EnvVarRetrievalHandler({
  cache: true,              // Enable result caching (default: true)
  validateEncoding: true,   // Validate encoding before decode (default: true)
  throwOnNotFound: false,   // Throw error if no vars found (default: false)
  debug: false              // Enable debug logging (default: false)
});
```

### Retrieval Options

```javascript
const result = handler.retrieve('PREFIX', {
  useFallback: true,        // Use all fallback strategies (default: true)
  maxChunks: 20,            // Max chunks to search for (default: 20)
  allowRaw: false,          // Return raw concatenated data (default: false)
  validateEncoding: true,   // Validate encoding (default: true)
  timeout: null             // Timeout in ms (default: none)
});
```

## Return Value

### Successful Retrieval

```javascript
{
  success: true,
  payload: 'decoded payload string',
  chunks: [
    {
      index: 0,
      value: '48656c6c6f',
      varName: 'APP_0',
      strategy: 'standard'
    },
    // ... more chunks
  ],
  numChunks: 2,
  prefix: 'APP',
  metadata: {
    concatenatedLength: 10,
    payloadLength: 5,
    strategies: ['standard']
  }
}
```

### Failed Retrieval

```javascript
{
  success: false,
  payload: null,
  chunks: [],
  error: 'No environment variables found',
  prefix: 'APP'
}
```

## Integration with EnvVarObfuscator

### Complete Pipeline

```javascript
const Obfuscator = require('./env-var-obfuscator');
const Handler = require('./env-var-retrieval-handler');

// Step 1: Obfuscate payload
const obfuscator = new Obfuscator();
const obfResult = obfuscator.obfuscate('secret command', {
  chunks: 4,
  addDecoys: true,
  numDecoys: 3,
  prefix: 'SECURE'
});

// Step 2: Set environment variables
Object.entries(obfResult.variables).forEach(([name, value]) => {
  process.env[name] = value;
});

// Step 3: Retrieve and decode
const handler = new Handler();
const retrieved = handler.retrieve('SECURE');

console.log('Original:', 'secret command');
console.log('Retrieved:', retrieved.payload);
console.log('Match:', retrieved.payload === 'secret command');
```

## Fallback Strategy Resolution

### How It Works

1. For each chunk index (0, 1, 2, ...):
   - Try standard naming: `PREFIX_0`
   - Try double underscore: `PREFIX__0`
   - Try chunk naming: `PREFIX_CHUNK_0`
   - Continue through all 10 strategies
   - Use first found value
2. Stop searching when encountering a gap (missing index)
3. Return all found chunks in order

### Example

```javascript
// Standard naming not available
delete process.env.APP_0;
delete process.env.APP_1;

// But alternative naming is available
process.env.APP_CHUNK_0 = '48656c6c6f';
process.env.APP_CHUNK_1 = '';

const handler = new Handler();
const result = handler.retrieve('APP', { useFallback: true });

// Successfully retrieves using CHUNK naming strategy
console.log(result.chunks[0].strategy); // 'chunkNaming'
```

## Error Handling

### Graceful Failure Mode

```javascript
const handler = new Handler({ throwOnNotFound: false });

const result = handler.retrieve('NONEXISTENT');
// Returns: { success: false, error: 'No environment variables found', ... }
```

### Strict Mode

```javascript
const handler = new Handler({ throwOnNotFound: true });

try {
  handler.retrieve('NONEXISTENT');
} catch (error) {
  console.error('Retrieval failed:', error.message);
}
```

## Debugging

### Enable Debug Logging

```javascript
const handler = new Handler({ debug: true });
handler.retrieve('APP');

// Output:
// [EnvVarRetrievalHandler] Starting retrieval for prefix: APP
// [EnvVarRetrievalHandler] Retrieving all chunks for prefix: APP
// [EnvVarRetrievalHandler] Found chunk 0 using standard strategy: APP_0
// ...
```

### Generate Compatibility Report

```javascript
const handler = new Handler();
const report = handler.generateCompatibilityReport('APP');

console.log(JSON.stringify(report, null, 2));

// Output:
// {
//   "prefix": "APP",
//   "timestamp": "2024-06-29T...",
//   "strategies": {
//     "index_0": {
//       "standard": {
//         "varName": "APP_0",
//         "found": true,
//         "encoding": "hex"
//       },
//       "doubleUnderscore": {
//         "varName": "APP__0",
//         "found": false,
//         "encoding": "unknown"
//       },
//       // ... more strategies
//     }
//   }
// }
```

## Payload Validation

### Using Checksums

```javascript
const crypto = require('crypto');
const handler = new Handler();

// Retrieve payload
const result = handler.retrieve('APP');

// Calculate checksum
const checksum = crypto
  .createHash('sha256')
  .update(result.payload)
  .digest('hex');

// Validate later
const isValid = handler.validatePayload(result.payload, checksum);
console.log('Valid:', isValid);
```

## Caching

### Cache Management

```javascript
const handler = new Handler({ cache: true });

// Retrieve and cache
handler.retrieve('APP1');
handler.retrieve('APP2');
handler.retrieve('APP3');

// Check cache stats
const stats = handler.getCacheStats();
console.log('Cached entries:', stats.size);
console.log('Cache keys:', stats.keys);

// Clear cache
handler.clearCache();
console.log('Cache cleared:', handler.getCacheStats().size === 0);
```

## Raw Mode

For cases where you need the raw concatenated data without decoding:

```javascript
const handler = new Handler();

// Normal mode (with decoding)
const decoded = handler.retrieve('APP', { allowRaw: false });
// Result: { payload: 'Hello World', ... }

// Raw mode (concatenated hex)
const raw = handler.retrieve('APP', { allowRaw: true });
// Result: { payload: '48656c6c6f20576f726c64', raw: true, ... }
```

## Performance Characteristics

### Typical Timings

- **Small payloads (< 100 bytes)**
  - First retrieval: 0.1-0.5ms
  - Cached retrieval: 0.01-0.05ms

- **Medium payloads (100-10KB)**
  - First retrieval: 0.5-2ms
  - Cached retrieval: 0.05-0.1ms

- **Large payloads (> 10KB)**
  - First retrieval: 2-10ms
  - Cached retrieval: 0.1-0.5ms

### Optimization Tips

1. **Enable caching** for repeated retrievals
2. **Disable fallback** if naming scheme is known
3. **Set maxChunks** to reasonable value (default: 20)
4. **Use raw mode** if you don't need decoding

## Examples

See `env-var-retrieval-examples.js` for 10 real-world usage examples:

1. Basic retrieval
2. Fallback strategy resolution
3. Caching for performance
4. Error handling
5. Compatibility debugging
6. Full obfuscation pipeline
7. Raw mode usage
8. Payload validation
9. Multiple prefixes
10. Performance analysis

Run examples:
```bash
node env-var-retrieval-examples.js
```

## Testing

Comprehensive test suite available in `env-var-retrieval-handler-test.js`:

```bash
node env-var-retrieval-handler-test.js
```

Tests cover:
- Encoding detection (hex, base64, unknown)
- Chunk retrieval with fallback
- Payload reconstruction
- Full retrieval workflow
- Caching behavior
- All 10 fallback strategies
- Error handling
- Compatibility reports
- Raw mode
- Payload validation

## API Reference

### Main Methods

| Method | Purpose |
|--------|---------|
| `retrieve(prefix, options)` | Retrieve and decode obfuscated payload |
| `getAllChunks(prefix, maxChunks)` | Get all chunks for prefix using fallback |
| `reconstructPayload(chunks)` | Reconstruct payload from chunks |
| `validatePayload(payload, checksum)` | Validate payload against checksum |
| `generateCompatibilityReport(prefix)` | Generate debugging report |
| `clearCache()` | Clear result cache |
| `getCacheStats()` | Get cache statistics |

### Encoding Detection

| Method | Purpose |
|--------|---------|
| `isHexEncoded(value)` | Check if value is hex-encoded |
| `isBase64Encoded(value)` | Check if value is base64-encoded |
| `detectEncoding(value)` | Detect encoding type |

### Decoding

| Method | Purpose |
|--------|---------|
| `decodeHexToBase64(hexString)` | Convert hex to base64 |
| `decodeBase64ToUtf8(base64)` | Convert base64 to UTF-8 |

## Troubleshooting

### Problem: "No variables found"

**Solution:** Enable fallback strategies and debug logging:

```javascript
const handler = new Handler({ debug: true });
const result = handler.retrieve('APP', { useFallback: true, maxChunks: 50 });

if (!result.success) {
  const report = handler.generateCompatibilityReport('APP');
  console.log(JSON.stringify(report, null, 2));
}
```

### Problem: Reconstruction fails

**Solution:** Check encoding and try raw mode:

```javascript
const handler = new Handler();

// Try raw mode to see concatenated data
const raw = handler.retrieve('APP', { allowRaw: true });
console.log('Raw data:', raw.payload);

// Enable debug for detailed info
const handler2 = new Handler({ debug: true });
handler2.retrieve('APP');
```

### Problem: Slow performance

**Solution:** Enable caching and reduce search space:

```javascript
const handler = new Handler({ cache: true });

// Reduce search space if chunks are small
const result = handler.retrieve('APP', { maxChunks: 5 });
```

## Security Considerations

1. **Cache Sensitivity:** Cached results may contain sensitive data. Clear cache when done:
   ```javascript
   handler.clearCache();
   ```

2. **Debug Logging:** Disable debug mode in production:
   ```javascript
   const handler = new Handler({ debug: false });
   ```

3. **Error Messages:** In strict mode, error messages may leak variable names. Use graceful mode in sensitive environments.

4. **Checksum Validation:** Always validate payloads using checksums for mission-critical data.

## Contributing

To extend fallback strategies, modify the `initializeFallbackPaths()` method in the handler.

## License

Part of the sc-generator project.
