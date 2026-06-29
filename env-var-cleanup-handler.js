/**
 * Environment Variable Cleanup Handler
 *
 * Provides cleanup functions to remove and restore environment variables after execution.
 * Supports tracking of original values with restoration or deletion on cleanup.
 * Features:
 * 1. Automatic tracking of env var modifications
 * 2. Original value storage and restoration
 * 3. Transaction-like behavior with dry-run support
 * 4. Retry logic with exponential backoff
 * 5. Per-variable and global cleanup
 * 6. Statistics and reporting
 *
 * Usage:
 *   const handler = new EnvVarCleanupHandler({ verbose: true });
 *   handler.startTracking();
 *   process.env.MY_VAR = 'temporary_value';
 *   handler.trackSet('MY_VAR', 'temporary_value');
 *   // ... do work ...
 *   const result = await handler.executeCleanup();
 */

/**
 * Environment Variable Cleanup Handler Class
 * Tracks env var modifications and provides cleanup functionality
 */
class EnvVarCleanupHandler {
  constructor(options = {}) {
    this.options = {
      verbose: options.verbose ?? false,
      dryRun: options.dryRun ?? false,
      trackOriginalValues: options.trackOriginalValues ?? true,
      maxRetries: options.maxRetries ?? 3,
      retryDelayMs: options.retryDelayMs ?? 100,
      autoRestoreOnDelete: options.autoRestoreOnDelete ?? true,
    };
    this.cleanupLog = [];
    this.isActive = false;
  }

  /**
   * Start cleanup tracking
   */
  startTracking() {
    this.isActive = true;
    this.cleanupLog = [];
    if (this.options.verbose) {
      console.log('[EnvVarCleanup] Tracking started');
    }
  }

  /**
   * Stop cleanup tracking
   */
  stopTracking() {
    this.isActive = false;
    if (this.options.verbose) {
      console.log('[EnvVarCleanup] Tracking stopped');
    }
  }

  /**
   * Track a set operation (new env var or modification)
   */
  trackSet(name, value) {
    if (!this.isActive) return;

    const originalValue = this.options.trackOriginalValues
      ? process.env[name]
      : undefined;

    // Check if already tracked
    const existingIndex = this.cleanupLog.findIndex(e => e.name === name);
    if (existingIndex >= 0) {
      // Update existing entry with new current value
      this.cleanupLog[existingIndex].currentValue = value;
      if (this.options.verbose) {
        const preview = value.substring(0, 30) + (value.length > 30 ? '...' : '');
        console.log(
          `[EnvVarCleanup] Updated tracking for: ${name} = ${preview}`
        );
      }
      return;
    }

    const entry = {
      name,
      currentValue: value,
      originalValue,
      wasSet: originalValue !== undefined,
      timestamp: new Date(),
    };

    this.cleanupLog.push(entry);

    if (this.options.verbose) {
      const preview = value.substring(0, 30) + (value.length > 30 ? '...' : '');
      console.log(`[EnvVarCleanup] Tracked set: ${name} = ${preview}`);
    }
  }

  /**
   * Track a delete operation
   */
  trackDelete(name) {
    if (!this.isActive) return;

    const originalValue = this.options.trackOriginalValues
      ? process.env[name]
      : undefined;

    // Check if already tracked
    const existingIndex = this.cleanupLog.findIndex(e => e.name === name);
    if (existingIndex >= 0) {
      this.cleanupLog[existingIndex].currentValue = undefined;
      if (this.options.verbose) {
        console.log(`[EnvVarCleanup] Updated tracking (delete): ${name}`);
      }
      return;
    }

    const entry = {
      name,
      currentValue: undefined,
      originalValue,
      wasSet: originalValue !== undefined,
      timestamp: new Date(),
    };

    this.cleanupLog.push(entry);

    if (this.options.verbose) {
      console.log(`[EnvVarCleanup] Tracked delete: ${name}`);
    }
  }

  /**
   * Manual add entry to cleanup log
   */
  addEntry(name, currentValue, originalValue = undefined) {
    const entry = {
      name,
      currentValue,
      originalValue: originalValue ?? process.env[name],
      wasSet:
        originalValue !== undefined || process.env[name] !== undefined,
      timestamp: new Date(),
    };

    this.cleanupLog.push(entry);

    if (this.options.verbose) {
      console.log(`[EnvVarCleanup] Added entry: ${name}`);
    }
  }

  /**
   * Get all tracked entries
   */
  getTrackedEntries() {
    return [...this.cleanupLog];
  }

  /**
   * Get tracked entry by name
   */
  getEntryByName(name) {
    return this.cleanupLog.find(e => e.name === name);
  }

  /**
   * Clear cleanup log without cleanup
   */
  clearLog() {
    this.cleanupLog = [];
    if (this.options.verbose) {
      console.log('[EnvVarCleanup] Log cleared');
    }
  }

  /**
   * Determine cleanup strategy for an entry
   */
  determineStrategy(entry) {
    if (entry.wasSet && entry.originalValue !== undefined) {
      // Variable existed before, restore it
      return 'restore';
    } else if (!entry.wasSet) {
      // Variable was created, delete it
      return 'delete';
    }
    // No cleanup needed
    return 'skip';
  }

  /**
   * Execute cleanup with retries
   */
  async executeCleanup() {
    const startTime = Date.now();
    const result = {
      success: true,
      entriesCleaned: 0,
      failedEntries: [],
      restoredEntries: [],
      deletedEntries: [],
      totalTime: 0,
      errors: [],
    };

    if (this.cleanupLog.length === 0) {
      if (this.options.verbose) {
        console.log('[EnvVarCleanup] No entries to clean');
      }
      result.totalTime = Date.now() - startTime;
      return result;
    }

    if (this.options.verbose) {
      console.log(
        `[EnvVarCleanup] Starting cleanup of ${this.cleanupLog.length} entries`
      );
    }

    if (this.options.dryRun) {
      console.log('[EnvVarCleanup] DRY RUN - No actual cleanup performed');
      for (const entry of this.cleanupLog) {
        const strategy = this.determineStrategy(entry);
        console.log(
          `[EnvVarCleanup] Would ${strategy}: ${entry.name}${strategy === 'restore' ? ` = ${entry.originalValue}` : ''}`
        );
        if (strategy !== 'skip') {
          result.entriesCleaned++;
        }
      }
      result.totalTime = Date.now() - startTime;
      return result;
    }

    // Process cleanup for each entry
    for (const entry of this.cleanupLog) {
      const cleaned = await this.cleanupEntry(entry, result);
      if (cleaned) {
        result.entriesCleaned++;
      } else {
        result.failedEntries.push(entry);
        result.success = false;
      }
    }

    result.totalTime = Date.now() - startTime;

    if (this.options.verbose) {
      console.log(
        `[EnvVarCleanup] Cleanup complete: ${result.entriesCleaned}/${this.cleanupLog.length} entries cleaned in ${result.totalTime}ms`
      );
      if (result.restoredEntries.length > 0) {
        console.log(
          `[EnvVarCleanup] Restored: ${result.restoredEntries.join(', ')}`
        );
      }
      if (result.deletedEntries.length > 0) {
        console.log(
          `[EnvVarCleanup] Deleted: ${result.deletedEntries.join(', ')}`
        );
      }
    }

    return result;
  }

  /**
   * Cleanup a single entry with retries
   */
  async cleanupEntry(entry, result) {
    const strategy = this.determineStrategy(entry);
    entry.strategy = strategy;

    if (strategy === 'skip') {
      if (this.options.verbose) {
        console.log(`[EnvVarCleanup] Skipping: ${entry.name}`);
      }
      return true;
    }

    let lastError = null;

    for (let attempt = 1; attempt <= this.options.maxRetries; attempt++) {
      try {
        if (strategy === 'restore') {
          // Restore original value
          if (entry.originalValue !== undefined) {
            process.env[entry.name] = entry.originalValue;
            result.restoredEntries.push(entry.name);
            if (this.options.verbose) {
              const preview = entry.originalValue.substring(0, 30) +
                (entry.originalValue.length > 30 ? '...' : '');
              console.log(
                `[EnvVarCleanup] Restored: ${entry.name} = ${preview}`
              );
            }
          }
        } else if (strategy === 'delete') {
          // Delete the env var (it was created during operation)
          delete process.env[entry.name];
          result.deletedEntries.push(entry.name);
          if (this.options.verbose) {
            console.log(`[EnvVarCleanup] Deleted: ${entry.name}`);
          }
        }

        return true;
      } catch (error) {
        lastError = error;
        if (this.options.verbose) {
          console.warn(
            `[EnvVarCleanup] Attempt ${attempt}/${this.options.maxRetries} failed for ${entry.name}:`,
            lastError.message
          );
        }

        if (attempt < this.options.maxRetries) {
          // Wait before retry with exponential backoff
          await this.sleep(
            Math.pow(2, attempt - 1) * this.options.retryDelayMs
          );
        }
      }
    }

    const errorMsg = `Failed to cleanup ${entry.name}: ${lastError?.message}`;
    result.errors.push(errorMsg);
    console.error(`[EnvVarCleanup] ${errorMsg}`);
    return false;
  }

  /**
   * Sleep utility
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Restore all entries to their original values
   */
  async restoreAll() {
    return this.executeCleanup();
  }

  /**
   * Get cleanup statistics
   */
  getStatistics() {
    const stats = {
      totalEntries: this.cleanupLog.length,
      restoredEntries: 0,
      deletedEntries: 0,
      skippedEntries: 0,
      oldestEntry: null,
      newestEntry: null,
    };

    for (const entry of this.cleanupLog) {
      const strategy = this.determineStrategy(entry);
      if (strategy === 'restore') stats.restoredEntries++;
      else if (strategy === 'delete') stats.deletedEntries++;
      else stats.skippedEntries++;

      if (!stats.oldestEntry || entry.timestamp < stats.oldestEntry) {
        stats.oldestEntry = entry.timestamp;
      }

      if (!stats.newestEntry || entry.timestamp > stats.newestEntry) {
        stats.newestEntry = entry.timestamp;
      }
    }

    return stats;
  }

  /**
   * Export cleanup log as JSON
   */
  exportLog() {
    return JSON.stringify(this.cleanupLog, null, 2);
  }

  /**
   * Import cleanup log from JSON
   */
  importLog(jsonData) {
    try {
      const imported = JSON.parse(jsonData);
      for (const entry of imported) {
        entry.timestamp = new Date(entry.timestamp);
        this.cleanupLog.push(entry);
      }
      if (this.options.verbose) {
        console.log(`[EnvVarCleanup] Imported ${imported.length} entries`);
      }
    } catch (error) {
      console.error('[EnvVarCleanup] Error importing log:', error);
      throw error;
    }
  }
}

/**
 * Global cleanup handler instance
 */
let globalCleanupHandler = null;

/**
 * Initialize and return global cleanup handler
 */
function initializeCleanupHandler(options = {}) {
  globalCleanupHandler = new EnvVarCleanupHandler(options);
  globalCleanupHandler.startTracking();
  return globalCleanupHandler;
}

/**
 * Get global cleanup handler
 */
function getCleanupHandler() {
  if (!globalCleanupHandler) {
    globalCleanupHandler = new EnvVarCleanupHandler();
    globalCleanupHandler.startTracking();
  }
  return globalCleanupHandler;
}

/**
 * Automatic cleanup decorator for async functions
 * Ensures cleanup runs after function execution
 */
function withAutoCleanup(options = {}) {
  return function (target) {
    return async (...args) => {
      const handler = getCleanupHandler();
      const wasActive = handler.isActive;
      if (!wasActive) {
        handler.startTracking();
      }

      try {
        return await target(...args);
      } finally {
        const result = await handler.executeCleanup();
        if (!wasActive) {
          handler.stopTracking();
        }
        if (options.verbose) {
          console.log('[AutoCleanup] Cleanup completed:', result);
        }
      }
    };
  };
}

/**
 * Context manager for automatic cleanup
 */
async function withCleanupContext(callback, options = {}) {
  const handler = new EnvVarCleanupHandler(options);
  handler.startTracking();

  try {
    const result = await callback(handler);
    const cleanup = await handler.executeCleanup();
    handler.stopTracking();
    return { result, cleanup };
  } catch (error) {
    handler.stopTracking();
    throw error;
  }
}

// Export the class and factory functions
module.exports = EnvVarCleanupHandler;
module.exports.EnvVarCleanupHandler = EnvVarCleanupHandler;
module.exports.initializeCleanupHandler = initializeCleanupHandler;
module.exports.getCleanupHandler = getCleanupHandler;
module.exports.withAutoCleanup = withAutoCleanup;
module.exports.withCleanupContext = withCleanupContext;

// Example usage
if (require.main === module) {
  console.log('=== Environment Variable Cleanup Handler Demo ===\n');

  (async () => {
    // Example 1: Basic cleanup
    console.log('=== Example 1: Basic Cleanup ===');
    const handler1 = new EnvVarCleanupHandler({ verbose: true });
    handler1.startTracking();

    process.env.DEMO_VAR = 'temporary_value';
    handler1.trackSet('DEMO_VAR', 'temporary_value');

    console.log('\nBefore cleanup:', process.env.DEMO_VAR);
    const result1 = await handler1.executeCleanup();
    console.log('After cleanup:', process.env.DEMO_VAR);
    console.log('Result:', JSON.stringify(result1, null, 2));

    // Example 2: Restoring original values
    console.log('\n=== Example 2: Restoring Original Values ===');
    const originalValue = 'original_value';
    process.env.MODIFY_VAR = originalValue;

    const handler2 = new EnvVarCleanupHandler({ verbose: true });
    handler2.startTracking();

    process.env.MODIFY_VAR = 'modified_value';
    handler2.trackSet('MODIFY_VAR', 'modified_value');

    console.log('\nBefore cleanup:', process.env.MODIFY_VAR);
    const result2 = await handler2.executeCleanup();
    console.log('After cleanup:', process.env.MODIFY_VAR);
    console.log('Result:', JSON.stringify(result2, null, 2));

    // Example 3: Dry run
    console.log('\n=== Example 3: Dry Run ===');
    const handler3 = new EnvVarCleanupHandler({ verbose: true, dryRun: true });
    handler3.startTracking();

    process.env.DRY_RUN_VAR_1 = 'temp1';
    process.env.DRY_RUN_VAR_2 = 'temp2';
    handler3.trackSet('DRY_RUN_VAR_1', 'temp1');
    handler3.trackSet('DRY_RUN_VAR_2', 'temp2');

    const result3 = await handler3.executeCleanup();
    console.log('Result:', JSON.stringify(result3, null, 2));

    // Example 4: Context manager
    console.log('\n=== Example 4: Context Manager ===');
    const { result: contextResult, cleanup: contextCleanup } = await withCleanupContext(
      async (handler) => {
        process.env.CONTEXT_VAR = 'context_value';
        handler.trackSet('CONTEXT_VAR', 'context_value');
        console.log('Inside context:', process.env.CONTEXT_VAR);
        return 'context operation result';
      },
      { verbose: true }
    );
    console.log('After context:', process.env.CONTEXT_VAR);
    console.log('Result:', contextResult);
    console.log('Cleanup:', JSON.stringify(contextCleanup, null, 2));

    // Example 5: Statistics
    console.log('\n=== Example 5: Statistics ===');
    const handler5 = new EnvVarCleanupHandler({ verbose: false });
    handler5.startTracking();

    process.env.STAT_VAR_1 = 'value1';
    process.env.STAT_VAR_2 = 'value2';
    handler5.trackSet('STAT_VAR_1', 'modified1');
    handler5.trackSet('STAT_VAR_2', 'modified2');

    const stats = handler5.getStatistics();
    console.log('Statistics:', JSON.stringify(stats, null, 2));

    // Execute cleanup
    await handler5.executeCleanup();
    console.log('\nCleanup completed');
  })().catch(console.error);
}
