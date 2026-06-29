/**
 * Environment Variable Retrieval Handler (TypeScript)
 *
 * Provides robust retrieval of obfuscated environment variables with:
 * 1. Primary source (direct env var access)
 * 2. Fallback paths for compatibility (alternative locations/naming schemes)
 * 3. Multiple decoding strategies (handles various obfuscation levels)
 * 4. Error handling and validation
 * 5. Caching for performance
 *
 * Usage:
 *   const handler = new EnvVarRetrievalHandler();
 *   const payload = handler.retrieve('APP', { useFallback: true });
 *   // Returns decoded payload with fallback support
 */

import * as crypto from 'crypto';

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

interface CompatibilityStrategyFunction {
  (prefix: string, index: number): string;
}

interface CompatibilityStrategies {
  [key: string]: CompatibilityStrategyFunction;
}

interface EnvVarRetrievalOptions {
  cache?: boolean;
  validateEncoding?: boolean;
  throwOnNotFound?: boolean;
  debug?: boolean;
}

class EnvVarRetrievalHandler {
  private options: EnvVarRetrievalOptions;
  private cache: Map<string, RetrievalResult>;
  private fallbackPaths: CompatibilityStrategies;

  constructor(options: EnvVarRetrievalOptions = {}) {
    this.options = {
      cache: options.cache !== false,
      validateEncoding: options.validateEncoding !== false,
      throwOnNotFound: options.throwOnNotFound !== false,
      debug: options.debug || false,
    };
    this.cache = new Map();
    this.fallbackPaths = this.initializeFallbackPaths();
  }

  /**
   * Initialize fallback path strategies for compatibility
   */
  private initializeFallbackPaths(): CompatibilityStrategies {
    return {
      // Standard naming convention: PREFIX_0, PREFIX_1, etc.
      standard: (prefix: string, index: number) => `${prefix}_${index}`,

      // Alternative with underscores: PREFIX__0, PREFIX__1, etc.
      doubleUnderscore: (prefix: string, index: number) => `${prefix}__${index}`,

      // Capitalized variation: PREFIX_CHUNK_0, PREFIX_CHUNK_1, etc.
      chunkNaming: (prefix: string, index: number) => `${prefix}_CHUNK_${index}`,

      // Prefixed with DATA: PREFIX_DATA_0, PREFIX_DATA_1, etc.
      dataPrefixed: (prefix: string, index: number) => `${prefix}_DATA_${index}`,

      // Numbered variation: PREFIX0, PREFIX1, PREFIX2, etc. (no separator)
      noSeparator: (prefix: string, index: number) => `${prefix}${index}`,

      // Hexadecimal index: PREFIX_0x0, PREFIX_0x1, etc.
      hexIndex: (prefix: string, index: number) => `${prefix}_0x${index.toString(16)}`,

      // Legacy format: XPREFIX_DATA_CHUNK_0
      legacyFormat: (prefix: string, index: number) => `X${prefix}_DATA_CHUNK_${index}`,

      // Abbreviated: P_0, P_1, P_2 (first letter of prefix)
      abbreviated: (prefix: string, index: number) => {
        const abbr = prefix.charAt(0).toUpperCase();
        return `${abbr}_${index}`;
      },

      // Environment specific Windows: PREFIX_VAR_0
      windowsFormat: (prefix: string, index: number) => `${prefix}_VAR_${index}`,

      // Packed format: PREFIXDATA_0, PREFIXDATA_1
      packedFormat: (prefix: string, index: number) => `${prefix}DATA_${index}`,
    };
  }

  /**
   * Log debug messages if debug mode is enabled
   */
  private debug(message: string, data?: any): void {
    if (this.options.debug) {
      if (data) {
        console.log(`[EnvVarRetrievalHandler] ${message}`, data);
      } else {
        console.log(`[EnvVarRetrievalHandler] ${message}`);
      }
    }
  }

  /**
   * Check if value looks like base64 encoded data
   */
  private isBase64Encoded(value: any): boolean {
    if (!value || typeof value !== 'string') return false;
    // Base64 pattern: alphanumeric, +, /, and = for padding
    const base64Regex = /^[A-Za-z0-9+/]*={0,2}$/;
    return base64Regex.test(value) && value.length % 4 === 0;
  }

  /**
   * Check if value looks like hex encoded data
   */
  private isHexEncoded(value: any): boolean {
    if (!value || typeof value !== 'string') return false;
    // Hex pattern: only 0-9a-fA-F characters
    const hexRegex = /^[0-9a-fA-F]+$/;
    return hexRegex.test(value) && value.length % 2 === 0;
  }

  /**
   * Detect encoding type of a value
   */
  private detectEncoding(value: string): string {
    if (!value || typeof value !== 'string') return 'unknown';
    if (this.isHexEncoded(value)) return 'hex';
    if (this.isBase64Encoded(value)) return 'base64';
    return 'unknown';
  }

  /**
   * Retrieve env var from standard location
   */
  private getFromStandard(varName: string): string | null {
    this.debug(`Attempting standard retrieval for: ${varName}`);
    return process.env[varName] || null;
  }

  /**
   * Retrieve env var from all possible locations (primary + fallbacks)
   */
  private getWithFallback(varName: string): any {
    this.debug(`Retrieving with fallback for: ${varName}`);

    // Try primary location
    const primary = this.getFromStandard(varName);
    if (primary !== null) {
      this.debug(`Found at primary location: ${varName}`, primary.substring(0, 20) + '...');
      return { value: primary, location: 'primary', varName };
    }

    // Try common alternative locations
    const alternatives = [
      varName.toUpperCase(),
      varName.toLowerCase(),
      varName.replace(/_/g, '-'),
      varName.replace(/-/g, '_'),
    ];

    for (const alt of alternatives) {
      if (alt !== varName) {
        const value = this.getFromStandard(alt);
        if (value !== null) {
          this.debug(`Found at alternative location: ${alt}`, value.substring(0, 20) + '...');
          return { value, location: 'alternative', varName: alt, originalVarName: varName };
        }
      }
    }

    this.debug(`Variable not found: ${varName}`);
    return { value: null, location: 'notfound', varName };
  }

  /**
   * Retrieve all chunks using fallback strategies
   */
  private getAllChunks(prefix: string, maxChunks: number = 20): ChunkInfo[] {
    this.debug(`Retrieving all chunks for prefix: ${prefix}`, { maxChunks });
    const chunks: ChunkInfo[] = [];
    const fallbackNames = Object.keys(this.fallbackPaths);

    // Try each naming convention
    for (let i = 0; i < maxChunks; i++) {
      let found = false;

      // Try each fallback strategy
      for (const strategyName of fallbackNames) {
        const strategy = this.fallbackPaths[strategyName];
        const varName = strategy(prefix, i);
        const value = process.env[varName];

        if (value !== null && value !== undefined) {
          chunks.push({
            index: i,
            value,
            varName,
            strategy: strategyName,
          });
          this.debug(`Found chunk ${i} using ${strategyName} strategy: ${varName}`);
          found = true;
          break; // Use first found for this index
        }
      }

      if (!found && i > 0) {
        // Stop searching if we find gaps (missing indices)
        this.debug(`No chunk found at index ${i}, stopping search`);
        break;
      }
    }

    this.debug(`Retrieved ${chunks.length} chunks for prefix: ${prefix}`);
    return chunks;
  }

  /**
   * Decode hex string to ASCII/characters
   */
  private decodeHexToAscii(hexString: string): string {
    let result = '';
    for (let i = 0; i < hexString.length; i += 2) {
      const hex = hexString.substr(i, 2);
      result += String.fromCharCode(parseInt(hex, 16));
    }
    return result;
  }

  /**
   * Decode hex string to Base64
   * (used when hex is encoding base64)
   */
  private decodeHexToBase64(hexString: string): string {
    return this.decodeHexToAscii(hexString);
  }

  /**
   * Decode Base64 to UTF-8
   */
  private decodeBase64ToUtf8(base64String: string): string | null {
    try {
      return Buffer.from(base64String, 'base64').toString('utf8');
    } catch (error) {
      this.debug(`Base64 decode error: ${(error as Error).message}`);
      return null;
    }
  }

  /**
   * Reconstruct payload from chunks with automatic encoding detection
   */
  private reconstructPayload(chunks: (ChunkInfo | string)[]): string | null {
    if (!chunks || chunks.length === 0) {
      this.debug('No chunks provided for reconstruction');
      return null;
    }

    this.debug(`Reconstructing payload from ${chunks.length} chunks`);

    // Concatenate all chunk values
    const hexString = chunks
      .map((c: any) => typeof c === 'string' ? c : c.value)
      .filter((v: any) => v && typeof v === 'string')
      .join('');

    if (hexString.length === 0) {
      this.debug('Empty hex string after concatenation');
      return null;
    }

    // Detect encoding type
    const encoding = this.detectEncoding(hexString);
    this.debug(`Detected encoding: ${encoding}`);

    try {
      if (encoding === 'hex') {
        // Hex can be:
        // 1. Hex representation of characters (hex -> ASCII -> check if valid base64)
        // 2. Direct hex of the original data

        // First try: hex -> base64 string -> UTF-8
        const asciiFromHex = this.decodeHexToAscii(hexString);
        if (this.isBase64Encoded(asciiFromHex)) {
          const payload = this.decodeBase64ToUtf8(asciiFromHex);
          if (payload) {
            this.debug('Successfully decoded via hex->base64->utf8 path');
            return payload;
          }
        }

        // Second try: direct hex -> UTF-8 (in case hex is direct encoding)
        // Assuming pairs of hex are UTF-8 bytes
        try {
          const payload = Buffer.from(hexString, 'hex').toString('utf8');
          if (payload && payload.length > 0) {
            this.debug('Successfully decoded via direct hex->utf8 path');
            return payload;
          }
        } catch (e) {
          this.debug(`Direct hex decode failed: ${(e as Error).message}`);
        }

        // Third try: hex -> ASCII representation
        this.debug('Returning hex->ascii conversion');
        return asciiFromHex;
      } else if (encoding === 'base64') {
        // Base64 -> UTF-8
        const payload = this.decodeBase64ToUtf8(hexString);
        return payload;
      } else {
        // Try both strategies for unknown encoding
        const base64 = this.decodeHexToBase64(hexString);
        const payload = this.decodeBase64ToUtf8(base64);
        if (payload && payload.length > 0) {
          return payload;
        }
        // Fallback: assume it's raw data
        return hexString;
      }
    } catch (error) {
      this.debug(`Reconstruction error: ${(error as Error).message}`);
      return null;
    }
  }

  /**
   * Main retrieval method with full fallback support
   *
   * Options:
   *   - useFallback: boolean (default: true) - Use all fallback strategies
   *   - maxChunks: number (default: 20) - Maximum chunks to search for
   *   - allowRaw: boolean (default: false) - Return raw concatenated chunks
   *   - validateEncoding: boolean (default: true) - Validate encoding before decode
   *   - timeout: number (default: none) - Timeout for retrieval in ms
   */
  public retrieve(prefix: string, options: RetrievalOptions = {}): RetrievalResult {
    const opts: RetrievalOptions = {
      useFallback: options.useFallback !== false,
      maxChunks: options.maxChunks || 20,
      allowRaw: options.allowRaw === true,
      validateEncoding: options.validateEncoding !== false,
      timeout: options.timeout || null,
    };

    this.debug(`Starting retrieval for prefix: ${prefix}`, opts);

    // Check cache first
    const cacheKey = `${prefix}:${JSON.stringify(opts)}`;
    if (this.options.cache && this.cache.has(cacheKey)) {
      this.debug(`Cache hit for: ${prefix}`);
      return this.cache.get(cacheKey)!;
    }

    try {
      // Retrieve all chunks
      const chunks = opts.useFallback
        ? this.getAllChunks(prefix, opts.maxChunks)
        : this.getAllChunks(prefix, opts.maxChunks);

      if (chunks.length === 0) {
        this.debug(`No chunks found for prefix: ${prefix}`);
        const result: RetrievalResult = {
          success: false,
          payload: null,
          chunks: [],
          error: 'No environment variables found',
          prefix,
        };

        if (this.options.cache) {
          this.cache.set(cacheKey, result);
        }

        if (this.options.throwOnNotFound) {
          throw new Error(`No variables found for prefix: ${prefix}`);
        }

        return result;
      }

      // Return raw chunks if requested
      if (opts.allowRaw) {
        const rawPayload = chunks.map((c: ChunkInfo) => c.value).join('');
        const result: RetrievalResult = {
          success: true,
          payload: rawPayload,
          chunks,
          raw: true,
          prefix,
        };

        if (this.options.cache) {
          this.cache.set(cacheKey, result);
        }

        return result;
      }

      // Reconstruct and decode payload
      const payload = this.reconstructPayload(chunks);

      if (payload === null) {
        this.debug(`Failed to reconstruct payload from chunks`);
        const result: RetrievalResult = {
          success: false,
          payload: null,
          chunks,
          error: 'Reconstruction failed',
          prefix,
        };

        if (this.options.cache) {
          this.cache.set(cacheKey, result);
        }

        if (this.options.throwOnNotFound) {
          throw new Error(`Failed to reconstruct payload from ${chunks.length} chunks`);
        }

        return result;
      }

      const result: RetrievalResult = {
        success: true,
        payload,
        chunks,
        numChunks: chunks.length,
        prefix,
        metadata: {
          concatenatedLength: chunks.reduce((sum, c) => sum + c.value.length, 0),
          payloadLength: payload.length,
          strategies: [...new Set(chunks.map((c) => c.strategy || 'unknown'))],
        },
      };

      if (this.options.cache) {
        this.cache.set(cacheKey, result);
      }

      this.debug(`Successfully retrieved payload from ${chunks.length} chunks`);
      return result;
    } catch (error) {
      this.debug(`Retrieval error: ${(error as Error).message}`);
      const result: RetrievalResult = {
        success: false,
        payload: null,
        chunks: [],
        error: (error as Error).message,
        prefix,
      };

      if (!this.options.throwOnNotFound) {
        return result;
      }

      throw error;
    }
  }

  /**
   * Clear the cache
   */
  public clearCache(): void {
    this.cache.clear();
    this.debug('Cache cleared');
  }

  /**
   * Get cache statistics
   */
  public getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }

  /**
   * Validate retrieval against expected checksum (if available)
   */
  public validatePayload(payload: string, checksum: string): boolean {
    if (!checksum) return true;

    const hash = crypto.createHash('sha256').update(payload).digest('hex');
    const valid = hash === checksum;

    this.debug(`Payload validation: ${valid ? 'PASS' : 'FAIL'}`);
    return valid;
  }

  /**
   * Generate compatibility report for debugging
   */
  public generateCompatibilityReport(prefix: string): any {
    this.debug(`Generating compatibility report for: ${prefix}`);

    const report: any = {
      prefix,
      timestamp: new Date().toISOString(),
      strategies: {},
    };

    const fallbackNames = Object.keys(this.fallbackPaths);

    for (let i = 0; i < 5; i++) {
      report.strategies[`index_${i}`] = {};

      for (const strategyName of fallbackNames) {
        const strategy = this.fallbackPaths[strategyName];
        const varName = strategy(prefix, i);
        const value = process.env[varName];

        report.strategies[`index_${i}`][strategyName] = {
          varName,
          found: value !== undefined && value !== null,
          valueLength: value ? value.length : 0,
          encoding: value ? this.detectEncoding(value) : 'unknown',
        };
      }
    }

    return report;
  }
}

export default EnvVarRetrievalHandler;
export { EnvVarRetrievalHandler, RetrievalOptions, RetrievalResult, ChunkInfo };
