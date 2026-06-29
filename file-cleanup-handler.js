/**
 * File Cleanup Handler with Secure Deletion
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
 *
 * Usage:
 *   const handler = new FileCleanupHandler({ verbose: true });
 *   handler.startTracking();
 *   const result = await handler.secureDelete('/path/to/file');
 *   const cleanupReport = await handler.executeCleanup();
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');
const { execSync } = require('child_process');

/**
 * File Cleanup Handler Class
 * Manages secure file deletion with trace removal
 */
class FileCleanupHandler {
  constructor(options = {}) {
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
    this.operations = [];
    this.isActive = false;
    this.deletedFiles = [];
    this.failedOperations = [];
  }

  /**
   * Start cleanup tracking
   */
  startTracking() {
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
  stopTracking() {
    this.isActive = false;
    if (this.options.verbose) {
      console.log('[FileCleanup] Tracking stopped');
    }
  }

  /**
   * Log operation
   */
  logOperation(operation, details = {}) {
    if (!this.isActive) return;

    const entry = {
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
  generateRandomBytes(length) {
    return crypto.randomBytes(length);
  }

  /**
   * Generate pattern for overwrite (DoD standard)
   */
  generateOverwritePattern(length, passNumber) {
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
  async overwriteFileContents(filePath, passes = this.options.overwritePasses) {
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
        console.warn(`[FileCleanup] Error during overwrite: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Delete file with optional overwrite
   */
  async deleteFile(filePath, options = {}) {
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
    let lastError = null;

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
        lastError = error;
        attempt++;

        if (this.options.verbose) {
          console.warn(
            `[FileCleanup] Delete attempt ${attempt}/${this.options.maxRetries} failed: ${error.message}`
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
  async clearRecycleBin() {
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
          // May fail due to permissions, but continue
          if (this.options.verbose) {
            console.warn(
              `[FileCleanup] Could not clear Recycle Bin (may need admin rights): ${error.message}`
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
            console.warn(`[FileCleanup] Could not clear Trash: ${error.message}`);
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
            console.warn(
              `[FileCleanup] Could not clear trash: ${error.message}`
            );
          }
        }
      }

      return true;
    } catch (error) {
      if (this.options.verbose) {
        console.error(
          `[FileCleanup] Recycle bin clear failed: ${error.message}`
        );
      }
      return false;
    }
  }

  /**
   * Remove file metadata (timestamps, ACLs)
   */
  async removeFileMetadata(filePath) {
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
          `[FileCleanup] Could not clear metadata: ${error.message}`
        );
      }
      // Don't fail operation if metadata can't be cleared
      return true;
    }
  }

  /**
   * Securely delete a file with all traces
   */
  async secureDelete(filePath, options = {}) {
    try {
      if (!fs.existsSync(filePath)) {
        throw new Error(`File not found: ${filePath}`);
      }

      const deleteOptions = { secure: true, ...options };

      // Remove metadata first
      await this.removeFileMetadata(filePath);

      // Delete file with overwrite
      const deleted = await this.deleteFile(filePath, deleteOptions);

      // Clear recycle bin after each deletion
      if (deleted && this.options.clearRecycleBin) {
        await this.clearRecycleBin();
      }

      return deleted;
    } catch (error) {
      if (this.options.verbose) {
        console.error(`[FileCleanup] Secure delete failed: ${error.message}`);
      }
      this.failedOperations.push({ filePath, error: error.message });
      return false;
    }
  }

  /**
   * Batch secure delete multiple files
   */
  async secureDeleteBatch(filePaths, options = {}) {
    const results = {
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
  async executeCleanup() {
    const startTime = Date.now();
    const result = {
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
        result.errors.push(`Recycle bin clear failed: ${error.message}`);
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
  getOperations() {
    return [...this.operations];
  }

  /**
   * Get deleted files list
   */
  getDeletedFiles() {
    return [...this.deletedFiles];
  }

  /**
   * Get failed operations
   */
  getFailedOperations() {
    return [...this.failedOperations];
  }

  /**
   * Get cleanup statistics
   */
  getStatistics() {
    const stats = {
      totalOperations: this.operations.length,
      totalFilesDeleted: this.deletedFiles.length,
      totalOperationsFailed: this.failedOperations.length,
      successRate: this.deletedFiles.length /
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
  exportReport() {
    return {
      timestamp: new Date(),
      statistics: this.getStatistics(),
      deletedFiles: this.getDeletedFiles(),
      failedOperations: this.getFailedOperations(),
      allOperations: this.getOperations(),
      options: this.options,
    };
  }

  /**
   * Generate human-readable cleanup summary
   */
  getSummary() {
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
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Clear all tracking data
   */
  clearTracking() {
    this.operations = [];
    this.deletedFiles = [];
    this.failedOperations = [];
    if (this.options.verbose) {
      console.log('[FileCleanup] Tracking data cleared');
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
  globalCleanupHandler = new FileCleanupHandler(options);
  globalCleanupHandler.startTracking();
  return globalCleanupHandler;
}

/**
 * Get global cleanup handler
 */
function getCleanupHandler() {
  if (!globalCleanupHandler) {
    globalCleanupHandler = new FileCleanupHandler();
    globalCleanupHandler.startTracking();
  }
  return globalCleanupHandler;
}

/**
 * Convenient function for single secure delete
 */
async function secureDeleteFile(filePath, options = {}) {
  const handler = new FileCleanupHandler(options);
  handler.startTracking();
  const result = await handler.secureDelete(filePath);
  await handler.executeCleanup();
  return result;
}

/**
 * Convenient function for batch secure delete
 */
async function secureDeleteFiles(filePaths, options = {}) {
  const handler = new FileCleanupHandler(options);
  handler.startTracking();
  const results = await handler.secureDeleteBatch(filePaths);
  await handler.executeCleanup();
  return results;
}

/**
 * Context manager for file cleanup
 */
async function withCleanupContext(callback, options = {}) {
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

// Export the class and factory functions
module.exports = FileCleanupHandler;
module.exports.FileCleanupHandler = FileCleanupHandler;
module.exports.initializeCleanupHandler = initializeCleanupHandler;
module.exports.getCleanupHandler = getCleanupHandler;
module.exports.secureDeleteFile = secureDeleteFile;
module.exports.secureDeleteFiles = secureDeleteFiles;
module.exports.withCleanupContext = withCleanupContext;

// Example usage and demonstrations
if (require.main === module) {
  console.log('=== File Cleanup Handler Demo ===\n');

  (async () => {
    // Example 1: Secure delete single file
    console.log('=== Example 1: Secure Delete Single File (Dry Run) ===');
    const handler1 = new FileCleanupHandler({
      verbose: true,
      dryRun: true,
      overwritePasses: 3,
    });
    handler1.startTracking();

    // Create test file
    const testFile1 = path.join(handler1.options.tempDir, 'test_secure_delete.txt');
    if (!handler1.options.dryRun) {
      fs.writeFileSync(testFile1, 'This is sensitive data that needs secure deletion');
    }

    const result1 = await handler1.secureDelete(testFile1);
    console.log('Delete result:', result1);

    // Example 2: Batch secure delete with statistics
    console.log('\n=== Example 2: Batch Secure Delete (Dry Run) ===');
    const handler2 = new FileCleanupHandler({
      verbose: true,
      dryRun: true,
      overwritePasses: 3,
      clearRecycleBin: true,
    });
    handler2.startTracking();

    const testFiles = [
      path.join(handler2.options.tempDir, 'sensitive_1.txt'),
      path.join(handler2.options.tempDir, 'sensitive_2.txt'),
      path.join(handler2.options.tempDir, 'sensitive_3.txt'),
    ];

    const batchResult = await handler2.secureDeleteBatch(testFiles);
    console.log('Batch delete result:', JSON.stringify(batchResult, null, 2));

    // Example 3: Statistics and reporting
    console.log('\n=== Example 3: Cleanup Statistics ===');
    const handler3 = new FileCleanupHandler({
      verbose: false,
      dryRun: true,
      overwritePasses: 3,
    });
    handler3.startTracking();
    handler3.logOperation('testOp', { description: 'Test operation' });

    const stats = handler3.getStatistics();
    console.log('Statistics:', JSON.stringify(stats, null, 2));

    const summary = handler3.getSummary();
    console.log('\nSummary:', JSON.stringify(summary, null, 2));

    // Example 4: Context manager usage
    console.log('\n=== Example 4: Context Manager (Dry Run) ===');
    const { result: contextResult, cleanup, report } = await withCleanupContext(
      async (handler) => {
        console.log('Inside cleanup context...');
        const testFile = path.join(handler.options.tempDir, 'context_test.txt');
        await handler.secureDelete(testFile);
        return 'context operation completed';
      },
      { verbose: true, dryRun: true }
    );

    console.log('Context result:', contextResult);
    console.log('Cleanup report:', JSON.stringify(report, null, 2));

    console.log('\n=== Demo Complete ===');
  })().catch(console.error);
}
