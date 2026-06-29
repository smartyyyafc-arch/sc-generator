/**
 * Environment Variable Cleanup Handler (TypeScript)
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
 * Cleanup entry for tracking modifications
 */
export interface CleanupEntry {
  name: string;
  currentValue: string | undefined;
  originalValue: string | undefined;
  wasSet: boolean;
  timestamp: Date;
  strategy?: 'restore' | 'delete' | 'skip';
}

/**
 * Cleanup handler options
 */
export interface CleanupOptions {
  verbose?: boolean;
  dryRun?: boolean;
  trackOriginalValues?: boolean;
  maxRetries?: number;
  retryDelayMs?: number;
  autoRestoreOnDelete?: boolean;
}

/**
 * Cleanup handler result
 */
export interface CleanupResult {
  success: boolean;
  entriesCleaned: number;
  failedEntries: CleanupEntry[];
  restoredEntries: string[];
  deletedEntries: string[];
  totalTime: number;
  errors: string[];
}

/**
 * Environment Variable Cleanup Handler Class
 * Tracks env var modifications and provides cleanup functionality
 */
export class EnvVarCleanupHandler {
  private cleanupLog: CleanupEntry[] = [];
  private options: Required<CleanupOptions>;
  private isActive: boolean = false;

  constructor(options: CleanupOptions = {}) {
    this.options = {
      verbose: options.verbose ?? false,
      dryRun: options.dryRun ?? false,
      trackOriginalValues: options.trackOriginalValues ?? true,
      maxRetries: options.maxRetries ?? 3,
      retryDelayMs: options.retryDelayMs ?? 100,
      autoRestoreOnDelete: options.autoRestoreOnDelete ?? true,
    };
  }

  /**
   * Start cleanup tracking
   */
  startTracking(): void {
    this.isActive = true;
    this.cleanupLog = [];
    if (this.options.verbose) {
      console.log('[EnvVarCleanup] Tracking started');
    }
  }

  /**
   * Stop cleanup tracking
   */
  stopTracking(): void {
    this.isActive = false;
    if (this.options.verbose) {
      console.log('[EnvVarCleanup] Tracking stopped');
    }
  }

  /**
   * Track a set operation (new env var or modification)
   */
  trackSet(name: string, value: string): void {
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
        console.log(
          `[EnvVarCleanup] Updated tracking for: ${name} = ${value.substring(0, 30)}${value.length > 30 ? '...' : ''}`
        );
      }
      return;
    }

    const entry: CleanupEntry = {
      name,
      currentValue: value,
      originalValue,
      wasSet: originalValue !== undefined,
      timestamp: new Date(),
    };

    this.cleanupLog.push(entry);

    if (this.options.verbose) {
      console.log(
        `[EnvVarCleanup] Tracked set: ${name} = ${value.substring(0, 30)}${value.length > 30 ? '...' : ''}`
      );
    }
  }

  /**
   * Track a delete operation
   */
  trackDelete(name: string): void {
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

    const entry: CleanupEntry = {
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
  addEntry(
    name: string,
    currentValue: string | undefined,
    originalValue?: string | undefined
  ): void {
    const entry: CleanupEntry = {
      name,
      currentValue,
      originalValue: originalValue ?? process.env[name],
      wasSet: originalValue !== undefined || process.env[name] !== undefined,
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
  getTrackedEntries(): CleanupEntry[] {
    return [...this.cleanupLog];
  }

  /**
   * Get tracked entry by name
   */
  getEntryByName(name: string): CleanupEntry | undefined {
    return this.cleanupLog.find(e => e.name === name);
  }

  /**
   * Clear cleanup log without cleanup
   */
  clearLog(): void {
    this.cleanupLog = [];
    if (this.options.verbose) {
      console.log('[EnvVarCleanup] Log cleared');
    }
  }

  /**
   * Determine cleanup strategy for an entry
   */
  private determineStrategy(entry: CleanupEntry): 'restore' | 'delete' | 'skip' {
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
  async executeCleanup(): Promise<CleanupResult> {
    const startTime = Date.now();
    const result: CleanupResult = {
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
        console.log(`[EnvVarCleanup] Restored: ${result.restoredEntries.join(', ')}`);
      }
      if (result.deletedEntries.length > 0) {
        console.log(`[EnvVarCleanup] Deleted: ${result.deletedEntries.join(', ')}`);
      }
    }

    return result;
  }

  /**
   * Cleanup a single entry with retries
   */
  private async cleanupEntry(
    entry: CleanupEntry,
    result: CleanupResult
  ): Promise<boolean> {
    const strategy = this.determineStrategy(entry);
    entry.strategy = strategy;

    if (strategy === 'skip') {
      if (this.options.verbose) {
        console.log(`[EnvVarCleanup] Skipping: ${entry.name}`);
      }
      return true;
    }

    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.options.maxRetries; attempt++) {
      try {
        if (strategy === 'restore') {
          // Restore original value
          if (entry.originalValue !== undefined) {
            process.env[entry.name] = entry.originalValue;
            result.restoredEntries.push(entry.name);
            if (this.options.verbose) {
              console.log(
                `[EnvVarCleanup] Restored: ${entry.name} = ${entry.originalValue.substring(0, 30)}${entry.originalValue.length > 30 ? '...' : ''}`
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
        lastError = error as Error;
        if (this.options.verbose) {
          console.warn(
            `[EnvVarCleanup] Attempt ${attempt}/${this.options.maxRetries} failed for ${entry.name}:`,
            lastError.message
          );
        }

        if (attempt < this.options.maxRetries) {
          // Wait before retry with exponential backoff
          await this.sleep(Math.pow(2, attempt - 1) * this.options.retryDelayMs);
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
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Restore all entries to their original values
   */
  async restoreAll(): Promise<CleanupResult> {
    return this.executeCleanup();
  }

  /**
   * Get cleanup statistics
   */
  getStatistics(): {
    totalEntries: number;
    restoredEntries: number;
    deletedEntries: number;
    skippedEntries: number;
    oldestEntry: Date | null;
    newestEntry: Date | null;
  } {
    const stats = {
      totalEntries: this.cleanupLog.length,
      restoredEntries: 0,
      deletedEntries: 0,
      skippedEntries: 0,
      oldestEntry: null as Date | null,
      newestEntry: null as Date | null,
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
  exportLog(): string {
    return JSON.stringify(this.cleanupLog, null, 2);
  }

  /**
   * Import cleanup log from JSON
   */
  importLog(jsonData: string): void {
    try {
      const imported = JSON.parse(jsonData) as CleanupEntry[];
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
let globalCleanupHandler: EnvVarCleanupHandler | null = null;

/**
 * Initialize and return global cleanup handler
 */
export function initializeCleanupHandler(
  options?: CleanupOptions
): EnvVarCleanupHandler {
  globalCleanupHandler = new EnvVarCleanupHandler(options);
  globalCleanupHandler.startTracking();
  return globalCleanupHandler;
}

/**
 * Get global cleanup handler
 */
export function getCleanupHandler(): EnvVarCleanupHandler {
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
export function withAutoCleanup(options?: CleanupOptions) {
  return function <T extends (...args: any[]) => Promise<any>>(
    target: T
  ): T {
    return (async (...args: any[]) => {
      const handler = getCleanupHandler();
      const wasActive = handler['isActive'];
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
        if (options?.verbose) {
          console.log('[AutoCleanup] Cleanup completed:', result);
        }
      }
    }) as T;
  };
}

/**
 * Context manager for automatic cleanup
 */
export async function withCleanupContext<T>(
  callback: (handler: EnvVarCleanupHandler) => Promise<T>,
  options?: CleanupOptions
): Promise<{ result: T; cleanup: CleanupResult }> {
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

/**
 * Export cleanup handler for use
 */
export default EnvVarCleanupHandler;
