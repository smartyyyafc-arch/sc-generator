# Environment Variable Retrieval Handler - API Reference

## Quick Reference

### Constructor

```javascript
new EnvVarRetrievalHandler(options?)
```

**Options:**
- `cache?: boolean` - Enable result caching (default: true)
- `validateEncoding?: boolean` - Validate encoding before decode (default: true)
- `throwOnNotFound?: boolean` - Throw error if no vars found (default: false)
- `debug?: boolean` - Enable debug logging (default: false)

### Main Method

```javascript
retrieve(prefix: string, options?): RetrievalResult
```

**Options:**
- `useFallback?: boolean` - Use all fallback strategies (default: true)
- `maxChunks?: number` - Max chunks to search for (default: 20)
- `allowRaw?: boolean` - Return raw concatenated data (default: false)
- `validateEncoding?: boolean` - Validate encoding (default: true)
- `timeout?: number | null` - Timeout in ms (default: none)

**Returns:**
```javascript
{
  success: boolean,           // Whether retrieval succeeded
  payload: string | null,     // Decoded payload or null
  chunks: ChunkInfo[],        // Found chunks with metadata
  numChunks?: number,         // Number of chunks found
  error?: string,             // Error message if failed
  prefix: string,             // The prefix used
  raw?: boolean,              // Whether result is raw data
  metadata?: {
    concatenatedLength: number,
    payloadLength: number,
    strategies: string[]
  }
}
```

---

## Core Methods

### `retrieve(prefix, options?)`
Main method for retrieving and decoding obfuscated payloads.

```javascript
const handler = new EnvVarRetrievalHandler();
const result = handler.retrieve('APP');
if (result.success) {
  console.log(result.payload);
}
```

### `getAllChunks(prefix, maxChunks?)`
Get all chunks for a prefix using fallback strategies.

```javascript
const handler = new EnvVarRetrievalHandler();
const chunks = handler.getAllChunks('APP', 20);
chunks.forEach(chunk => {
  console.log(`${chunk.varName}: ${chunk.value}`);
});
```

### `reconstructPayload(chunks)`
Reconstruct payload from chunk data.

```javascript
const handler = new EnvVarRetrievalHandler();
const chunks = [
  { index: 0, value: '48656c6c6f' },
  { index: 1, value: '20576f726c64' }
];
const payload = handler.reconstructPayload(chunks);
// Returns: "Hello World"
```

---

## Encoding Detection Methods

### `detectEncoding(value)`
Detect the encoding type of a value.

```javascript
const handler = new EnvVarRetrievalHandler();

handler.detectEncoding('48656c6c6f');      // 'hex'
handler.detectEncoding('SGVsbG8=');         // 'base64'
handler.detectEncoding('not-encoded');      // 'unknown'
```

### `isHexEncoded(value)`
Check if value is hex-encoded.

```javascript
const handler = new EnvVarRetrievalHandler();
handler.isHexEncoded('48656c6c6f');  // true
handler.isHexEncoded('invalid');      // false
```

### `isBase64Encoded(value)`
Check if value is base64-encoded.

```javascript
const handler = new EnvVarRetrievalHandler();
handler.isBase64Encoded('SGVsbG8=');  // true
handler.isBase64Encoded('invalid');   // false
```

---

## Decoding Methods

### `decodeHexToAscii(hexString)`
Convert hex string to ASCII characters.

```javascript
const handler = new EnvVarRetrievalHandler();
handler.decodeHexToAscii('48656c6c6f');
// Returns: "Hello"
```

### `decodeHexToBase64(hexString)`
Convert hex string to base64 (hex->ASCII->base64).

```javascript
const handler = new EnvVarRetrievalHandler();
const base64 = handler.decodeHexToBase64('...');
```

### `decodeBase64ToUtf8(base64String)`
Convert base64 to UTF-8 string.

```javascript
const handler = new EnvVarRetrievalHandler();
handler.decodeBase64ToUtf8('SGVsbG8=');
// Returns: "Hello"
```

---

## Cache Management Methods

### `clearCache()`
Clear all cached results.

```javascript
const handler = new EnvVarRetrievalHandler({ cache: true });
handler.retrieve('APP');
handler.clearCache();
```

### `getCacheStats()`
Get cache statistics.

```javascript
const handler = new EnvVarRetrievalHandler({ cache: true });
handler.retrieve('APP1');
handler.retrieve('APP2');

const stats = handler.getCacheStats();
// Returns: { size: 2, keys: [...] }
```

---

## Validation Methods

### `validatePayload(payload, checksum)`
Validate payload against SHA-256 checksum.

```javascript
const crypto = require('crypto');
const handler = new EnvVarRetrievalHandler();

const result = handler.retrieve('APP');
const checksum = crypto
  .createHash('sha256')
  .update(result.payload)
  .digest('hex');

const isValid = handler.validatePayload(result.payload, checksum);
// Returns: true/false
```

---

## Debugging Methods

### `generateCompatibilityReport(prefix)`
Generate a detailed compatibility report for debugging.

```javascript
const handler = new EnvVarRetrievalHandler();
const report = handler.generateCompatibilityReport('APP');

console.log(JSON.stringify(report, null, 2));
// Output:
// {
//   "prefix": "APP",
//   "timestamp": "2024-06-29T...",
//   "strategies": {
//     "index_0": {
//       "standard": { "varName": "APP_0", "found": true, ... },
//       "doubleUnderscore": { "varName": "APP__0", "found": false, ... },
//       ...
//     }
//   }
// }
```

---

## Fallback Strategies

The handler supports 10 different naming conventions:

| Strategy | Pattern | Example |
|----------|---------|---------|
| `standard` | `PREFIX_0` | `APP_0`, `APP_1` |
| `doubleUnderscore` | `PREFIX__0` | `APP__0`, `APP__1` |
| `chunkNaming` | `PREFIX_CHUNK_0` | `APP_CHUNK_0` |
| `dataPrefixed` | `PREFIX_DATA_0` | `APP_DATA_0` |
| `noSeparator` | `PREFIX0` | `APP0`, `APP1` |
| `hexIndex` | `PREFIX_0x0` | `APP_0x0`, `APP_0x1` |
| `legacyFormat` | `XPREFIX_DATA_CHUNK_0` | `XAPP_DATA_CHUNK_0` |
| `abbreviated` | `P_0` | `A_0` (first letter) |
| `windowsFormat` | `PREFIX_VAR_0` | `APP_VAR_0` |
| `packedFormat` | `PREFIXDATA_0` | `APPDATA_0` |

---

## Examples by Use Case

### Basic Usage
```javascript
const handler = new EnvVarRetrievalHandler();
const result = handler.retrieve('APP');
console.log(result.payload);
```

### With Fallback Support
```javascript
const handler = new EnvVarRetrievalHandler();
const result = handler.retrieve('APP', {
  useFallback: true,
  maxChunks: 50
});
```

### With Caching
```javascript
const handler = new EnvVarRetrievalHandler({
  cache: true
});

const result1 = handler.retrieve('APP');  // From env
const result2 = handler.retrieve('APP');  // From cache
```

### With Debug Logging
```javascript
const handler = new EnvVarRetrievalHandler({
  debug: true
});

const result = handler.retrieve('APP');
// Outputs detailed debug info to console
```

### Error Handling
```javascript
// Graceful mode (default)
const handler1 = new EnvVarRetrievalHandler({
  throwOnNotFound: false
});
const result = handler1.retrieve('NONEXISTENT');
if (!result.success) {
  console.log('Error:', result.error);
}

// Strict mode
const handler2 = new EnvVarRetrievalHandler({
  throwOnNotFound: true
});
try {
  handler2.retrieve('NONEXISTENT');
} catch (error) {
  console.error('Retrieval failed:', error.message);
}
```

### Raw Mode
```javascript
const handler = new EnvVarRetrievalHandler();

// Get decoded payload
const normal = handler.retrieve('APP');
console.log(normal.payload);  // Decoded string

// Get raw concatenated data
const raw = handler.retrieve('APP', { allowRaw: true });
console.log(raw.payload);     // Hex string (not decoded)
```

### With Validation
```javascript
const crypto = require('crypto');
const handler = new EnvVarRetrievalHandler();

const result = handler.retrieve('APP');
const checksum = crypto
  .createHash('sha256')
  .update(result.payload)
  .digest('hex');

const isValid = handler.validatePayload(result.payload, checksum);
```

### Debugging
```javascript
const handler = new EnvVarRetrievalHandler({ debug: true });

// Enable debug logging
const result = handler.retrieve('APP');

// Generate compatibility report
const report = handler.generateCompatibilityReport('APP');
console.log(JSON.stringify(report, null, 2));
```

---

## Type Definitions (TypeScript)

```typescript
interface RetrievalOptions {
  useFallback?: boolean;
  maxChunks?: number;
  allowRaw?: boolean;
  validateEncoding?: boolean;
  timeout?: number | null;
}

interface RetrievalResult {
  success: boolean;
  payload: string | null;
  chunks: ChunkInfo[];
  numChunks?: number;
  error?: string;
  prefix: string;
  raw?: boolean;
  metadata?: {
    concatenatedLength: number;
    payloadLength: number;
    strategies: string[];
  };
}

interface ChunkInfo {
  index: number;
  value: string;
  varName: string;
  strategy?: string;
}

interface EnvVarRetrievalOptions {
  cache?: boolean;
  validateEncoding?: boolean;
  throwOnNotFound?: boolean;
  debug?: boolean;
}
```

---

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `No variables found` | No environment variables with prefix found | Check variable names, enable fallback mode |
| `Reconstruction failed` | Could not decode chunks into payload | Verify encoding, try raw mode |
| `Direct hex decode failed` | Hex decoding produced invalid UTF-8 | Check hex data format |
| `Base64 decode error` | Invalid base64 data | Verify base64 encoding |

---

## Performance Tips

1. **Enable caching** for repeated retrievals of same prefix
2. **Disable fallback** if variable naming scheme is known
3. **Set realistic maxChunks** based on expected payload size
4. **Use raw mode** if you don't need automatic decoding
5. **Reduce search space** by using tighter maxChunks limits

---

## Integration Points

### With EnvVarObfuscator

```javascript
const Obfuscator = require('./env-var-obfuscator');
const Handler = require('./env-var-retrieval-handler');

// Create and obfuscate
const obfuscator = new Obfuscator();
const obfResult = obfuscator.obfuscate('secret', {
  chunks: 4,
  prefix: 'APP'
});

// Set environment
Object.entries(obfResult.variables).forEach(([name, value]) => {
  process.env[name] = value;
});

// Retrieve and decode
const handler = new Handler();
const result = handler.retrieve('APP');
console.log(result.payload);  // 'secret'
```

---

## Testing

Run the test suite:
```bash
node env-var-retrieval-handler-test.js
```

Run the examples:
```bash
node env-var-retrieval-examples.js
```

---

## Support

For issues, examples, or questions:
- See `ENV_VAR_RETRIEVAL_GUIDE.md` for detailed documentation
- See `env-var-retrieval-examples.js` for 10 real-world examples
- Run tests with `env-var-retrieval-handler-test.js`
