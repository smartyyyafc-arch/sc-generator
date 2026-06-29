/**
 * Registry Cleanup Handler
 * Provides cleanup functions to remove registry traces after execution
 * Supports cleanup from multiple hives with transaction-like behavior
 */

import {
  IRegistryStorage,
  RegistryHive,
  SoftwareHiveStorage,
  CurrentUserHiveStorage,
  CurrentVersionHiveStorage,
  SystemHiveStorage,
  MultiHiveRegistryManager,
} from './registry-storage-variants';

/**
 * Cleanup entry for tracking modifications
 */
export interface CleanupEntry {
  hive: RegistryHive;
  key: string;
  originalValue?: string | null;
  wasDeleted?: boolean;
  timestamp: Date;
}

/**
 * Cleanup handler options
 */
export interface CleanupOptions {
  verbose?: boolean;
  dryRun?: boolean;
  trackOriginalValues?: boolean;
  maxRetries?: number;
}

/**
 * Cleanup handler result
 */
export interface CleanupResult {
  success: boolean;
  entriesCleaned: number;
  failedEntries: CleanupEntry[];
  totalTime: number;
  errors: string[];
}

/**
 * Registry Cleanup Handler Class
 * Tracks registry modifications and provides cleanup functionality
 */
export class RegistryCleanupHandler {
  private cleanupLog: CleanupEntry[] = [];
  private storageMap: Map<RegistryHive, IRegistryStorage> = new Map();
  private options: Required<CleanupOptions>;
  private isActive: boolean = false;

  constructor(options: CleanupOptions = {}) {
    this.options = {
      verbose: options.verbose ?? false,
      dryRun: options.dryRun ?? false,
      trackOriginalValues: options.trackOriginalValues ?? true,
      maxRetries: options.maxRetries ?? 3,
    };

    this.initializeStorageMap();
  }

  /**
   * Initialize storage map with all hive variants
   */
  private initializeStorageMap(): void {
    this.storageMap.set(
      RegistryHive.HKLM_SOFTWARE,
      new SoftwareHiveStorage()
    );
    this.storageMap.set(
      RegistryHive.HKEY_CURRENT_USER,
      new CurrentUserHiveStorage()
    );
    this.storageMap.set(
      RegistryHive.CURRENT_VERSION,
      new CurrentVersionHiveStorage()
    );
    this.storageMap.set(
      RegistryHive.HKLM_SYSTEM,
      new SystemHiveStorage()
    );
  }

  /**
   * Start cleanup tracking
   */
  startTracking(): void {
    this.isActive = true;
    this.cleanupLog = [];
    if (this.options.verbose) {
      console.log('[RegistryCleanup] Tracking started');
    }
  }

  /**
   * Stop cleanup tracking
   */
  stopTracking(): void {
    this.isActive = false;
    if (this.options.verbose) {
      console.log('[RegistryCleanup] Tracking stopped');
    }
  }

  /**
   * Track a registry write operation
   */
  async trackWrite(
    hive: RegistryHive,
    key: string,
    storage: IRegistryStorage
  ): Promise<void> {
    if (!this.isActive) return;

    try {
      const originalValue = this.options.trackOriginalValues
        ? await storage.read(key)
        : undefined;

      const entry: CleanupEntry = {
        hive,
        key,
        originalValue,
        timestamp: new Date(),
      };

      this.cleanupLog.push(entry);

      if (this.options.verbose) {
        console.log(`[RegistryCleanup] Tracked write: ${hive}\\${key}`);
      }
    } catch (error) {
      console.error(`[RegistryCleanup] Error tracking write for ${key}:`, error);
    }
  }

  /**
   * Track a registry delete operation
   */
  trackDelete(hive: RegistryHive, key: string): void {
    if (!this.isActive) return;

    const entry: CleanupEntry = {
      hive,
      key,
      wasDeleted: true,
      timestamp: new Date(),
    };

    this.cleanupLog.push(entry);

    if (this.options.verbose) {
      console.log(`[RegistryCleanup] Tracked delete: ${hive}\\${key}`);
    }
  }

  /**
   * Manual add entry to cleanup log
   */
  addEntry(hive: RegistryHive, key: string, originalValue?: string | null): void {
    const entry: CleanupEntry = {
      hive,
      key,
      originalValue,
      timestamp: new Date(),
    };

    this.cleanupLog.push(entry);

    if (this.options.verbose) {
      console.log(`[RegistryCleanup] Added entry: ${hive}\\${key}`);
    }
  }

  /**
   * Get all tracked entries
   */
  getTrackedEntries(): CleanupEntry[] {
    return [...this.cleanupLog];
  }

  /**
   * Get tracked entries by hive
   */
  getEntriesByHive(hive: RegistryHive): CleanupEntry[] {
    return this.cleanupLog.filter(entry => entry.hive === hive);
  }

  /**
   * Clear cleanup log without cleanup
   */
  clearLog(): void {
    this.cleanupLog = [];
    if (this.options.verbose) {
      console.log('[RegistryCleanup] Log cleared');
    }
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
      totalTime: 0,
      errors: [],
    };

    if (this.cleanupLog.length === 0) {
      if (this.options.verbose) {
        console.log('[RegistryCleanup] No entries to clean');
      }
      result.totalTime = Date.now() - startTime;
      return result;
    }

    if (this.options.verbose) {
      console.log(`[RegistryCleanup] Starting cleanup of ${this.cleanupLog.length} entries`);
    }

    if (this.options.dryRun) {
      console.log('[RegistryCleanup] DRY RUN - No actual cleanup performed');
      result.entriesCleaned = this.cleanupLog.length;
      result.totalTime = Date.now() - startTime;
      return result;
    }

    // Group entries by hive for efficient cleanup
    const entriesByHive = new Map<RegistryHive, CleanupEntry[]>();
    for (const entry of this.cleanupLog) {
      if (!entriesByHive.has(entry.hive)) {
        entriesByHive.set(entry.hive, []);
      }
      entriesByHive.get(entry.hive)!.push(entry);
    }

    // Process cleanup per hive
    for (const [hive, entries] of entriesByHive) {
      const storage = this.storageMap.get(hive);
      if (!storage) {
        const error = `Unknown hive: ${hive}`;
        result.errors.push(error);
        result.success = false;
        continue;
      }

      for (const entry of entries) {
        const cleaned = await this.cleanupEntry(entry, storage);
        if (cleaned) {
          result.entriesCleaned++;
        } else {
          result.failedEntries.push(entry);
          result.success = false;
        }
      }
    }

    result.totalTime = Date.now() - startTime;

    if (this.options.verbose) {
      console.log(
        `[RegistryCleanup] Cleanup complete: ${result.entriesCleaned}/${this.cleanupLog.length} entries cleaned in ${result.totalTime}ms`
      );
    }

    return result;
  }

  /**
   * Cleanup a single entry with retries
   */
  private async cleanupEntry(
    entry: CleanupEntry,
    storage: IRegistryStorage
  ): Promise<boolean> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.options.maxRetries; attempt++) {
      try {
        if (entry.wasDeleted) {
          // Key was deleted during operation, nothing to restore
          if (this.options.verbose) {
            console.log(
              `[RegistryCleanup] Skipping deleted key: ${entry.hive}\\${entry.key}`
            );
          }
          return true;
        }

        if (entry.originalValue !== undefined) {
          // Restore original value
          await storage.write(entry.key, entry.originalValue);
          if (this.options.verbose) {
            console.log(
              `[RegistryCleanup] Restored: ${entry.hive}\\${entry.key} = ${entry.originalValue}`
            );
          }
        } else {
          // Delete the key (it was created during operation)
          const exists = await storage.exists(entry.key);
          if (exists) {
            await storage.delete(entry.key);
            if (this.options.verbose) {
              console.log(`[RegistryCleanup] Deleted: ${entry.hive}\\${entry.key}`);
            }
          }
        }

        return true;
      } catch (error) {
        lastError = error as Error;
        if (this.options.verbose) {
          console.warn(
            `[RegistryCleanup] Attempt ${attempt}/${this.options.maxRetries} failed for ${entry.key}:`,
            lastError.message
          );
        }

        if (attempt < this.options.maxRetries) {
          // Wait before retry with exponential backoff
          await this.sleep(Math.pow(2, attempt - 1) * 100);
        }
      }
    }

    const errorMsg = `Failed to cleanup ${entry.hive}\\${entry.key}: ${lastError?.message}`;
    result.errors.push(errorMsg);
    console.error(`[RegistryCleanup] ${errorMsg}`);
    return false;
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Cleanup all entries from a specific hive
   */
  async cleanupHive(hive: RegistryHive): Promise<CleanupResult> {
    const entries = this.getEntriesByHive(hive);
    const originalLog = this.cleanupLog;

    this.cleanupLog = entries;
    const result = await this.executeCleanup();
    this.cleanupLog = originalLog.filter(e => e.hive !== hive);

    return result;
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
    entriesByHive: Record<string, number>;
    oldestEntry: Date | null;
    newestEntry: Date | null;
  } {
    const stats = {
      totalEntries: this.cleanupLog.length,
      entriesByHive: {} as Record<string, number>,
      oldestEntry: null as Date | null,
      newestEntry: null as Date | null,
    };

    for (const entry of this.cleanupLog) {
      stats.entriesByHive[entry.hive] =
        (stats.entriesByHive[entry.hive] || 0) + 1;

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
        console.log(`[RegistryCleanup] Imported ${imported.length} entries`);
      }
    } catch (error) {
      console.error('[RegistryCleanup] Error importing log:', error);
      throw error;
    }
  }
}

/**
 * Global cleanup handler instance
 */
let globalCleanupHandler: RegistryCleanupHandler | null = null;

/**
 * Initialize and return global cleanup handler
 */
export function initializeCleanupHandler(
  options?: CleanupOptions
): RegistryCleanupHandler {
  globalCleanupHandler = new RegistryCleanupHandler(options);
  globalCleanupHandler.startTracking();
  return globalCleanupHandler;
}

/**
 * Get global cleanup handler
 */
export function getCleanupHandler(): RegistryCleanupHandler {
  if (!globalCleanupHandler) {
    globalCleanupHandler = new RegistryCleanupHandler();
  }
  return globalCleanupHandler;
}

/**
 * Automatic cleanup decorator for functions
 * Ensures cleanup runs after function execution
 */
export function withAutoCleanup(options?: CleanupOptions) {
  return function <T extends (...args: any[]) => Promise<any>>(
    target: T
  ): T {
    return (async (...args: any[]) => {
      const handler = getCleanupHandler();
      handler.startTracking();

      try {
        return await target(...args);
      } finally {
        const result = await handler.executeCleanup();
        handler.stopTracking();
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
  callback: (handler: RegistryCleanupHandler) => Promise<T>,
  options?: CleanupOptions
): Promise<{ result: T; cleanup: CleanupResult }> {
  const handler = new RegistryCleanupHandler(options);
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
export default RegistryCleanupHandler;
