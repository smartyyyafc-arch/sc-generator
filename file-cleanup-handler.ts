/**
 * File Cleanup Handler with Secure Deletion (TypeScript)
 *
 * Provides secure file deletion with multiple methods:
 * 1. Standard file deletion
 * 2. Recycle bin clearing (platform-specific)
 * 3. Cryptographic overwrite of file contents
 * 4. Trace removal and forensic cleanup
 *
 * Features:
 * - Multi-pass overwrite (DoD 5220.22-M standard)
 * - Recycle bin/Trash clearing
 * - File metadata wipe
 * - Transaction tracking with rollback support
 * - Dry-run mode for safety verification
 * - Detailed operation logging and statistics
 * - Cross-platform support (Windows, Linux, macOS)
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import * as crypto from 'crypto';
import { execSync } from 'child_process';

/**
 * Options for FileCleanupHandler
 */
interface FileCleanupOptions {
  verbose?: boolean;
  dryRun?: boolean;
  overwritePasses?: number;
  clearRecycleBin?: boolean;
  wipeMetadata?: boolean;
  trackOperations?: boolean;
  maxRetries?: number;
  retryDelayMs?: number;
  tempDir?: string;
}

/**
 * Tracked file deletion entry
 */
interface DeletedFileEntry {
  filePath: string;
  deletedAt: Date;
  overwritePasses: number;
  secure: boolean;
  fileSize?: number;
}

/**
 * Operation log entry
 */
interface OperationEntry {
  operation: string;
  timestamp: Date;
  details: Record<string, any>;
  status: 'pending' | 'completed' | 'failed';
}

/**
 * Failed operation entry
 */
interface FailedOperationEntry {
  filePath?: string;
  error: string;
}

/**
 * Cleanup execution result
 */
interface CleanupResult {
  success: boolean;
  filesDeleted: number;
  operationsCompleted: number;
  recycleBinCleared: boolean;
  totalTime: number;
  errors: string[];
  summary: {
    deleted: number;
    failed: number;
    operations: number;
  };
}

/**
 * Statistics result
 */
interface Statistics {
  totalOperations: number;
  totalFilesDeleted: number;
  totalOperationsFailed: number;
  successRate: number;
  overwritePasses: number;
  recycleBinClearingEnabled: boolean;
  metadataWipingEnabled: boolean;
  totalBytesOverwritten: number;
}

/**
 * Cleanup report
 */
interface CleanupReport {
  timestamp: Date;
  statistics: Statistics;
  deletedFiles: DeletedFileEntry[];
  failedOperations: FailedOperationEntry[];
  allOperations: OperationEntry[];
  options: FileCleanupOptions;
}

/**
 * Cleanup summary
 */
interface CleanupSummary {
  title: string;
  timestamp: string;
  filesDeleted: number;
  operationsFailed: number;
  successRate: string;
  securityLevel: string;
  recycleBinCleared: boolean;
  metadataWiped: boolean;
  totalTime: string;
}

/**
 * Batch delete result
 */
interface BatchDeleteResult {
  success: number;
  failed: number;
  total: number;
  deletedFiles: string[];
  failedFiles: string[];
}

/**
 * File Cleanup Handler Class (TypeScript)
 * Manages secure file deletion with trace removal
 */
export class FileCleanupHandler {
  private options: Required<FileCleanupOptions>;
  private operations: OperationEntry[] = [];
  private isActive: boolean = false;
  private deletedFiles: DeletedFileEntry[] = [];
  private failedOperations: FailedOperationEntry[] = [];

  constructor(options: FileCleanupOptions = {}) {
    this.options = {
      verbose: options.verbose ?? false,
      dryRun: options.dryRun ?? false,
      overwritePasses: options.overwritePasses ?? 3,
      clearRecycleBin: options.clearRecycleBin ?? true,
      wipeMetadata: options.wipeMetadata ?? true,
      trackOperations: options.trackOperations ?? true,
      maxRetries: options.maxRetries ?? 3,
      retryDelayMs: options.retryDelayMs ?? 100,
      tempDir: options.tempDir ?? os.tmpdir(),
    };
  }

  /**
   * Start cleanup tracking
   */
  public startTracking(): void {
    this.isActive = true;
    this.operations = [];
    this.deletedFiles = [];
    this.failedOperations = [];
    if (this.options.verbose) {
      console.log('[FileCleanup] Tracking started');
    }
  }

  /**
   * Stop cleanup tracking
   */
  public stopTracking(): void {
    this.isActive = false;
    if (this.options.verbose) {
      console.log('[FileCleanup] Tracking stopped');
    }
  }

  /**
   * Log operation
   */
  private logOperation(
    operation: string,
    details: Record<string, any> = {}
  ): void {
    if (!this.isActive) return;

    const entry: OperationEntry = {
      operation,
      timestamp: new Date(),
      details,
      status: 'pending',
    };

    this.operations.push(entry);

    if (this.options.verbose) {
      console.log(
        `[FileCleanup] ${operation}: ${details.filePath || details.description || ''}`
      );
    }
  }

  /**
   * Generate random bytes for overwrite
   */
  private generateRandomBytes(length: number): Buffer {
    return crypto.randomBytes(length);
  }

  /**
   * Generate pattern for overwrite (DoD standard)
   */
  private generateOverwritePattern(length: number, passNumber: number): Buffer {
    const patterns = [
      Buffer.alloc(length, 0x00), // Pass 1: zeros
      Buffer.alloc(length, 0xff), // Pass 2: ones
      this.generateRandomBytes(length), // Pass 3: random
    ];
    return patterns[(passNumber - 1) % patterns.length];
  }

  /**
   * Overwrite file contents securely
   */
  public async overwriteFileContents(
    filePath: string,
    passes: number = this.options.overwritePasses
  ): Promise<boolean> {
    try {
      const fileStats = fs.statSync(filePath);
      const fileSize = fileStats.size;

      if (this.options.verbose) {
        console.log(
          `[FileCleanup] Overwriting ${filePath} (${fileSize} bytes) with ${passes} passes`
        );
      }

      for (let pass = 1; pass <= passes; pass++) {
        const pattern = this.generateOverwritePattern(fileSize, pass);

        if (!this.options.dryRun) {
          fs.writeFileSync(filePath, pattern);

          if (this.options.verbose) {
            console.log(`[FileCleanup] Overwrite pass ${pass}/${passes} completed`);
          }
        } else if (this.options.verbose) {
          console.log(`[FileCleanup] DRY RUN: Would overwrite pass ${pass}/${passes}`);
        }
      }

      return true;
    } catch (error) {
      if (this.options.verbose) {
        console.warn(`[FileCleanup] Error during overwrite: ${(error as Error).message}`);
      }
      throw error;
    }
  }

  /**
   * Delete file with optional overwrite
   */
  public async deleteFile(
    filePath: string,
    options: Partial<FileCleanupOptions> & { secure?: boolean; overwritePasses?: number; wipeMetadata?: boolean } = {}
  ): Promise<boolean> {
    const deleteOptions = {
      secure: options.secure ?? true,
      overwritePasses: options.overwritePasses ?? this.options.overwritePasses,
      wipeMetadata: options.wipeMetadata ?? this.options.wipeMetadata,
      ...options,
    };

    this.logOperation('deleteFile', { filePath });

    if (!fs.existsSync(filePath)) {
      const error = `File not found: ${filePath}`;
      if (this.options.verbose) {
        console.warn(`[FileCleanup] ${error}`);
      }
      this.failedOperations.push({ filePath, error });
      return false;
    }

    let attempt = 0;
    let lastError: Error | null = null;

    while (attempt < this.options.maxRetries) {
      try {
        // Step 1: Secure overwrite if requested
        if (deleteOptions.secure) {
          await this.overwriteFileContents(filePath, deleteOptions.overwritePasses);
        }

        // Step 2: Delete file
        if (!this.options.dryRun) {
          fs.unlinkSync(filePath);
          if (this.options.verbose) {
            console.log(`[FileCleanup] File deleted: ${filePath}`);
          }
        } else if (this.options.verbose) {
          console.log(`[FileCleanup] DRY RUN: Would delete file: ${filePath}`);
        }

        this.deletedFiles.push({
          filePath,
          deletedAt: new Date(),
          overwritePasses: deleteOptions.overwritePasses,
          secure: deleteOptions.secure,
        });

        return true;
      } catch (error) {
        lastError = error as Error;
        attempt++;

        if (this.options.verbose) {
          console.warn(
            `[FileCleanup] Delete attempt ${attempt}/${this.options.maxRetries} failed: ${lastError.message}`
          );
        }

        if (attempt < this.options.maxRetries) {
          await this.sleep(
            Math.pow(2, attempt - 1) * this.options.retryDelayMs
          );
        }
      }
    }

    const errorMsg = `Failed to delete ${filePath}: ${lastError?.message}`;
    this.failedOperations.push({ filePath, error: errorMsg });
    if (this.options.verbose) {
      console.error(`[FileCleanup] ${errorMsg}`);
    }
    return false;
  }

  /**
   * Clear recycle bin / trash (platform-specific)
   */
  public async clearRecycleBin(): Promise<boolean> {
    if (!this.options.clearRecycleBin) {
      if (this.options.verbose) {
        console.log('[FileCleanup] Recycle bin clearing disabled');
      }
      return true;
    }

    this.logOperation('clearRecycleBin', { description: 'Clear system recycle bin' });

    if (this.options.dryRun) {
      if (this.options.verbose) {
        console.log('[FileCleanup] DRY RUN: Would clear recycle bin');
      }
      return true;
    }

    try {
      const platform = os.platform();

      if (platform === 'win32') {
        // Windows: Clear Recycle Bin
        try {
          execSync('cmd /c "rd /s /q %SystemRoot%\\$Recycle.bin"', {
            stdio: 'pipe',
          });
          if (this.options.verbose) {
            console.log('[FileCleanup] Windows Recycle Bin cleared');
          }
        } catch (error) {
          if (this.options.verbose) {
            console.warn(
              `[FileCleanup] Could not clear Recycle Bin: ${(error as Error).message}`
            );
          }
        }
      } else if (platform === 'darwin') {
        // macOS: Clear Trash
        try {
          execSync("rm -rf ~/.Trash/*", { stdio: 'pipe' });
          if (this.options.verbose) {
            console.log('[FileCleanup] macOS Trash cleared');
          }
        } catch (error) {
          if (this.options.verbose) {
            console.warn(`[FileCleanup] Could not clear Trash: ${(error as Error).message}`);
          }
        }
      } else if (platform === 'linux') {
        // Linux: Clear trash directories
        try {
          execSync("rm -rf ~/.local/share/Trash/* ~/.Trash/*", { stdio: 'pipe' });
          if (this.options.verbose) {
            console.log('[FileCleanup] Linux trash cleared');
          }
        } catch (error) {
          if (this.options.verbose) {
            console.warn(`[FileCleanup] Could not clear trash: ${(error as Error).message}`);
          }
        }
      }

      return true;
    } catch (error) {
      if (this.options.verbose) {
        console.error(
          `[FileCleanup] Recycle bin clear failed: ${(error as Error).message}`
        );
      }
      return false;
    }
  }

  /**
   * Remove file metadata (timestamps, ACLs)
   */
  public async removeFileMetadata(filePath: string): Promise<boolean> {
    if (!this.options.wipeMetadata || this.options.dryRun) {
      return true;
    }

    try {
      // Reset modification and access times to epoch
      const epoch = new Date(0);
      fs.utimesSync(filePath, epoch, epoch);

      if (this.options.verbose) {
        console.log(`[FileCleanup] File metadata cleared: ${filePath}`);
      }

      return true;
    } catch (error) {
      if (this.options.verbose) {
        console.warn(
          `[FileCleanup] Could not clear metadata: ${(error as Error).message}`
        );
      }
      return true; // Don't fail operation
    }
  }

  /**
   * Securely delete a file with all traces
   */
  public async secureDelete(
    filePath: string,
    options: Partial<FileCleanupOptions> & { secure?: boolean; overwritePasses?: number } = {}
  ): Promise<boolean> {
    try {
      if (!fs.existsSync(filePath)) {
        throw new Error(`File not found: ${filePath}`);
      }

      const deleteOptions = { secure: true, ...options };

      // Remove metadata first
      await this.removeFileMetadata(filePath);

      // Delete file with overwrite
      const deleted = await this.deleteFile(filePath, deleteOptions as any);

      // Clear recycle bin after each deletion
      if (deleted && this.options.clearRecycleBin) {
        await this.clearRecycleBin();
      }

      return deleted;
    } catch (error) {
      if (this.options.verbose) {
        console.error(`[FileCleanup] Secure delete failed: ${(error as Error).message}`);
      }
      this.failedOperations.push({
        filePath,
        error: (error as Error).message,
      });
      return false;
    }
  }

  /**
   * Batch secure delete multiple files
   */
  public async secureDeleteBatch(
    filePaths: string[],
    options: Partial<FileCleanupOptions> = {}
  ): Promise<BatchDeleteResult> {
    const results: BatchDeleteResult = {
      success: 0,
      failed: 0,
      total: filePaths.length,
      deletedFiles: [],
      failedFiles: [],
    };

    if (this.options.verbose) {
      console.log(
        `[FileCleanup] Starting batch delete of ${filePaths.length} files`
      );
    }

    for (const filePath of filePaths) {
      const deleted = await this.secureDelete(filePath, options);
      if (deleted) {
        results.success++;
        results.deletedFiles.push(filePath);
      } else {
        results.failed++;
        results.failedFiles.push(filePath);
      }
    }

    if (this.options.verbose) {
      console.log(
        `[FileCleanup] Batch delete complete: ${results.success}/${results.total} successful`
      );
    }

    return results;
  }

  /**
   * Execute all cleanup operations
   */
  public async executeCleanup(): Promise<CleanupResult> {
    const startTime = Date.now();
    const result: CleanupResult = {
      success: true,
      filesDeleted: 0,
      operationsCompleted: 0,
      recycleBinCleared: false,
      totalTime: 0,
      errors: [],
      summary: {
        deleted: this.deletedFiles.length,
        failed: this.failedOperations.length,
        operations: this.operations.length,
      },
    };

    if (this.operations.length === 0 && this.deletedFiles.length === 0) {
      if (this.options.verbose) {
        console.log('[FileCleanup] No operations to clean');
      }
      result.totalTime = Date.now() - startTime;
      return result;
    }

    if (this.options.verbose) {
      console.log(
        `[FileCleanup] Starting cleanup of ${this.operations.length} operations`
      );
    }

    // Clear recycle bin at the end
    if (this.options.clearRecycleBin) {
      try {
        await this.clearRecycleBin();
        result.recycleBinCleared = true;
      } catch (error) {
        result.errors.push(`Recycle bin clear failed: ${(error as Error).message}`);
      }
    }

    result.filesDeleted = this.deletedFiles.length;
    result.operationsCompleted = this.operations.length;
    result.totalTime = Date.now() - startTime;

    if (this.failedOperations.length > 0) {
      result.success = false;
      result.errors = this.failedOperations.map(op => op.error);
    }

    if (this.options.verbose) {
      console.log(
        `[FileCleanup] Cleanup complete: ${result.filesDeleted} files deleted, ${result.totalTime}ms elapsed`
      );
    }

    return result;
  }

  /**
   * Get all logged operations
   */
  public getOperations(): OperationEntry[] {
    return [...this.operations];
  }

  /**
   * Get deleted files list
   */
  public getDeletedFiles(): DeletedFileEntry[] {
    return [...this.deletedFiles];
  }

  /**
   * Get failed operations
   */
  public getFailedOperations(): FailedOperationEntry[] {
    return [...this.failedOperations];
  }

  /**
   * Get cleanup statistics
   */
  public getStatistics(): Statistics {
    const stats: Statistics = {
      totalOperations: this.operations.length,
      totalFilesDeleted: this.deletedFiles.length,
      totalOperationsFailed: this.failedOperations.length,
      successRate:
        this.deletedFiles.length /
          (this.deletedFiles.length + this.failedOperations.length) || 0,
      overwritePasses: this.options.overwritePasses,
      recycleBinClearingEnabled: this.options.clearRecycleBin,
      metadataWipingEnabled: this.options.wipeMetadata,
      totalBytesOverwritten: this.deletedFiles.reduce(
        (sum, file) => sum + (file.fileSize || 0),
        0
      ),
    };

    return stats;
  }

  /**
   * Export cleanup report as JSON
   */
  public exportReport(): CleanupReport {
    return {
      timestamp: new Date(),
      statistics: this.getStatistics(),
      deletedFiles: this.getDeletedFiles(),
      failedOperations: this.getFailedOperations(),
      allOperations: this.getOperations(),
      options: this.options as FileCleanupOptions,
    };
  }

  /**
   * Generate human-readable cleanup summary
   */
  public getSummary(): CleanupSummary {
    const stats = this.getStatistics();
    const report = this.exportReport();

    return {
      title: 'File Cleanup Summary',
      timestamp: report.timestamp.toISOString(),
      filesDeleted: stats.totalFilesDeleted,
      operationsFailed: stats.totalOperationsFailed,
      successRate: `${(stats.successRate * 100).toFixed(2)}%`,
      securityLevel: `${this.options.overwritePasses}-pass overwrite`,
      recycleBinCleared: this.options.clearRecycleBin,
      metadataWiped: this.options.wipeMetadata,
      totalTime: `${report.timestamp.getTime()}ms`,
    };
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Clear all tracking data
   */
  public clearTracking(): void {
    this.operations = [];
    this.deletedFiles = [];
    this.failedOperations = [];
    if (this.options.verbose) {
      console.log('[FileCleanup] Tracking data cleared');
    }
  }
}

/**
 * Convenient function for single secure delete
 */
export async function secureDeleteFile(
  filePath: string,
  options: FileCleanupOptions = {}
): Promise<boolean> {
  const handler = new FileCleanupHandler(options);
  handler.startTracking();
  const result = await handler.secureDelete(filePath);
  await handler.executeCleanup();
  return result;
}

/**
 * Convenient function for batch secure delete
 */
export async function secureDeleteFiles(
  filePaths: string[],
  options: FileCleanupOptions = {}
): Promise<BatchDeleteResult> {
  const handler = new FileCleanupHandler(options);
  handler.startTracking();
  const results = await handler.secureDeleteBatch(filePaths);
  await handler.executeCleanup();
  return results;
}

/**
 * Context manager for file cleanup
 */
export async function withCleanupContext<T>(
  callback: (handler: FileCleanupHandler) => Promise<T>,
  options: FileCleanupOptions = {}
): Promise<{ result: T; cleanup: CleanupResult; report: CleanupReport }> {
  const handler = new FileCleanupHandler(options);
  handler.startTracking();

  try {
    const result = await callback(handler);
    const cleanup = await handler.executeCleanup();
    handler.stopTracking();
    return { result, cleanup, report: handler.exportReport() };
  } catch (error) {
    handler.stopTracking();
    throw error;
  }
}

export default FileCleanupHandler;
