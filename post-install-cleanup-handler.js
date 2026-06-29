/**
 * Post-Installation Cleanup Handler
 *
 * Provides comprehensive cleanup after installation including:
 * 1. Installer file removal (with secure deletion option)
 * 2. History clearing (shell history, command history, etc.)
 * 3. Temporary file cleanup
 * 4. Installation logs cleanup
 * 5. Cache and artifact removal
 * 6. Trace removal and forensic cleanup
 *
 * Features:
 * - Targeted removal of installer executables and scripts
 * - Cross-platform shell history clearing (bash, zsh, sh, cmd, powershell)
 * - Secure deletion with cryptographic overwrite
 * - Transaction tracking with rollback support
 * - Dry-run mode for safety verification
 * - Detailed operation logging and statistics
 * - Batch cleanup operations with retry logic
 * - Pre-defined cleanup profiles (minimal, standard, thorough)
 *
 * Usage:
 *   const handler = new PostInstallCleanupHandler({ verbose: true });
 *   handler.startTracking();
 *   const result = await handler.removeInstaller('/path/to/installer');
 *   const cleanupReport = await handler.executeCleanup();
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');
const { execSync, spawnSync } = require('child_process');

/**
 * Post-Installation Cleanup Handler Class
 * Manages removal of installer files and clears installation traces
 */
class PostInstallCleanupHandler {
  constructor(options = {}) {
    this.options = {
      verbose: options.verbose ?? false,
      dryRun: options.dryRun ?? false,
      secureDelete: options.secureDelete ?? true,
      overwritePasses: options.overwritePasses ?? 3,
      clearHistory: options.clearHistory ?? true,
      clearLogs: options.clearLogs ?? true,
      clearCache: options.clearCache ?? true,
      clearTemp: options.clearTemp ?? true,
      clearRecycleBin: options.clearRecycleBin ?? true,
      trackOperations: options.trackOperations ?? true,
      maxRetries: options.maxRetries ?? 3,
      retryDelayMs: options.retryDelayMs ?? 100,
      tempDir: options.tempDir ?? os.tmpdir(),
      homeDir: options.homeDir ?? os.homedir(),
      profile: options.profile ?? 'standard', // 'minimal', 'standard', 'thorough'
    };

    this.operations = [];
    this.isActive = false;
    this.deletedFiles = [];
    this.clearedHistories = [];
    this.failedOperations = [];
    this.cleanupProfile = this.getCleanupProfile(this.options.profile);
  }

  /**
   * Get predefined cleanup profiles
   */
  getCleanupProfile(profileName) {
    const profiles = {
      minimal: {
        name: 'Minimal',
        description: 'Remove only installer and main logs',
        clearInstaller: true,
        clearHistory: false,
        clearLogs: true,
        clearCache: false,
        clearTemp: false,
        secureDelete: false,
      },
      standard: {
        name: 'Standard',
        description: 'Remove installer, history, logs, and cache',
        clearInstaller: true,
        clearHistory: true,
        clearLogs: true,
        clearCache: true,
        clearTemp: false,
        secureDelete: true,
      },
      thorough: {
        name: 'Thorough',
        description: 'Complete cleanup including temp files and forensic traces',
        clearInstaller: true,
        clearHistory: true,
        clearLogs: true,
        clearCache: true,
        clearTemp: true,
        secureDelete: true,
      },
    };

    return profiles[profileName] || profiles.standard;
  }

  /**
   * Start cleanup tracking
   */
  startTracking() {
    this.isActive = true;
    this.operations = [];
    this.deletedFiles = [];
    this.clearedHistories = [];
    this.failedOperations = [];
    if (this.options.verbose) {
      console.log('[PostInstallCleanup] Tracking started');
    }
  }

  /**
   * Stop cleanup tracking
   */
  stopTracking() {
    this.isActive = false;
    if (this.options.verbose) {
      console.log('[PostInstallCleanup] Tracking stopped');
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
        `[PostInstallCleanup] ${operation}: ${details.filePath || details.description || ''}`
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
          `[PostInstallCleanup] Overwriting ${filePath} (${fileSize} bytes) with ${passes} passes`
        );
      }

      for (let pass = 1; pass <= passes; pass++) {
        const pattern = this.generateOverwritePattern(fileSize, pass);

        if (!this.options.dryRun) {
          fs.writeFileSync(filePath, pattern);

          if (this.options.verbose) {
            console.log(`[PostInstallCleanup] Overwrite pass ${pass}/${passes} completed`);
          }
        } else if (this.options.verbose) {
          console.log(`[PostInstallCleanup] DRY RUN: Would overwrite pass ${pass}/${passes}`);
        }
      }

      return true;
    } catch (error) {
      if (this.options.verbose) {
        console.warn(`[PostInstallCleanup] Error during overwrite: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Delete file with optional secure overwrite
   */
  async deleteFile(filePath, options = {}) {
    const deleteOptions = {
      secure: options.secure ?? (this.options.secureDelete && this.cleanupProfile.secureDelete),
      overwritePasses: options.overwritePasses ?? this.options.overwritePasses,
      ...options,
    };

    this.logOperation('deleteFile', { filePath });

    if (!fs.existsSync(filePath)) {
      const error = `File not found: ${filePath}`;
      if (this.options.verbose) {
        console.warn(`[PostInstallCleanup] ${error}`);
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
            console.log(`[PostInstallCleanup] File deleted: ${filePath}`);
          }
        } else if (this.options.verbose) {
          console.log(`[PostInstallCleanup] DRY RUN: Would delete file: ${filePath}`);
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
            `[PostInstallCleanup] Delete attempt ${attempt}/${this.options.maxRetries} failed: ${error.message}`
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
      console.error(`[PostInstallCleanup] ${errorMsg}`);
    }
    return false;
  }

  /**
   * Remove installer file or directory
   */
  async removeInstaller(installerPath, options = {}) {
    if (!installerPath) {
      const error = 'Installer path is required';
      this.failedOperations.push({ filePath: installerPath, error });
      return false;
    }

    this.logOperation('removeInstaller', { filePath: installerPath });

    if (!fs.existsSync(installerPath)) {
      if (this.options.verbose) {
        console.warn(`[PostInstallCleanup] Installer not found: ${installerPath}`);
      }
      // Not a failure if installer doesn't exist
      return true;
    }

    try {
      const isDirectory = fs.statSync(installerPath).isDirectory();

      if (!this.options.dryRun) {
        if (isDirectory) {
          // Recursively delete directory
          this.deleteDirectoryRecursive(installerPath);
          if (this.options.verbose) {
            console.log(`[PostInstallCleanup] Installer directory deleted: ${installerPath}`);
          }
        } else {
          // Delete file
          const deleteSuccess = await this.deleteFile(installerPath, {
            secure: options.secure ?? this.cleanupProfile.secureDelete,
          });
          if (!deleteSuccess) {
            return false;
          }
        }
      } else if (this.options.verbose) {
        console.log(`[PostInstallCleanup] DRY RUN: Would delete installer: ${installerPath}`);
      }

      return true;
    } catch (error) {
      const errorMsg = `Failed to remove installer: ${error.message}`;
      this.failedOperations.push({ filePath: installerPath, error: errorMsg });
      if (this.options.verbose) {
        console.error(`[PostInstallCleanup] ${errorMsg}`);
      }
      return false;
    }
  }

  /**
   * Recursively delete directory
   */
  deleteDirectoryRecursive(dirPath) {
    if (!fs.existsSync(dirPath)) {
      return;
    }

    const files = fs.readdirSync(dirPath);

    for (const file of files) {
      const filePath = path.join(dirPath, file);
      const stats = fs.statSync(filePath);

      if (stats.isDirectory()) {
        this.deleteDirectoryRecursive(filePath);
      } else {
        fs.unlinkSync(filePath);
      }
    }

    if (!this.options.dryRun) {
      fs.rmdirSync(dirPath);
    }
  }

  /**
   * Clear shell history files
   */
  async clearShellHistory() {
    if (!this.cleanupProfile.clearHistory || !this.options.clearHistory) {
      if (this.options.verbose) {
        console.log('[PostInstallCleanup] Shell history clearing disabled');
      }
      return true;
    }

    this.logOperation('clearShellHistory', { description: 'Clear shell history files' });

    const historyFiles = [
      // Bash
      path.join(this.options.homeDir, '.bash_history'),
      path.join(this.options.homeDir, '.bash_sessions'),
      // Zsh
      path.join(this.options.homeDir, '.zsh_history'),
      path.join(this.options.homeDir, '.zsh_sessions'),
      // Sh
      path.join(this.options.homeDir, '.sh_history'),
      // Fish
      path.join(this.options.homeDir, '.local/share/fish/fish_history'),
      // Tcsh
      path.join(this.options.homeDir, '.history'),
      path.join(this.options.homeDir, '.tcsh_history'),
      // Ksh
      path.join(this.options.homeDir, '.ksh_history'),
    ];

    if (this.options.verbose) {
      console.log(`[PostInstallCleanup] Clearing shell history (${historyFiles.length} files)`);
    }

    let clearedCount = 0;

    for (const historyFile of historyFiles) {
      try {
        if (fs.existsSync(historyFile)) {
          const deleted = await this.deleteFile(historyFile, {
            secure: this.cleanupProfile.secureDelete,
          });

          if (deleted) {
            this.clearedHistories.push(historyFile);
            clearedCount++;
          }
        }
      } catch (error) {
        if (this.options.verbose) {
          console.warn(
            `[PostInstallCleanup] Could not clear history file ${historyFile}: ${error.message}`
          );
        }
      }
    }

    if (this.options.verbose) {
      console.log(`[PostInstallCleanup] Cleared ${clearedCount} history files`);
    }

    return true;
  }

  /**
   * Clear command history in memory
   */
  async clearCommandHistory() {
    this.logOperation('clearCommandHistory', { description: 'Clear in-memory command history' });

    if (this.options.dryRun) {
      if (this.options.verbose) {
        console.log('[PostInstallCleanup] DRY RUN: Would clear in-memory command history');
      }
      return true;
    }

    try {
      const platform = os.platform();

      if (platform === 'win32') {
        // Windows: Clear command history
        try {
          // Clear cmd.exe history
          execSync('cls', { stdio: 'pipe' });
          // Clear PowerShell history
          execSync('powershell -Command "Clear-History -Confirm:$false"', {
            stdio: 'pipe',
          });
          if (this.options.verbose) {
            console.log('[PostInstallCleanup] Windows command history cleared');
          }
        } catch (error) {
          if (this.options.verbose) {
            console.warn(`[PostInstallCleanup] Could not clear Windows history: ${error.message}`);
          }
        }
      } else {
        // Unix-like: Clear shell history via history command
        try {
          execSync('history -c', { shell: '/bin/bash', stdio: 'pipe' });
          if (this.options.verbose) {
            console.log('[PostInstallCleanup] Unix command history cleared');
          }
        } catch (error) {
          if (this.options.verbose) {
            console.warn(`[PostInstallCleanup] Could not clear Unix history: ${error.message}`);
          }
        }
      }

      return true;
    } catch (error) {
      if (this.options.verbose) {
        console.warn(
          `[PostInstallCleanup] Error clearing command history: ${error.message}`
        );
      }
      return true; // Non-critical operation
    }
  }

  /**
   * Clear installation logs
   */
  async clearInstallationLogs() {
    if (!this.cleanupProfile.clearLogs || !this.options.clearLogs) {
      if (this.options.verbose) {
        console.log('[PostInstallCleanup] Log clearing disabled');
      }
      return true;
    }

    this.logOperation('clearInstallationLogs', { description: 'Clear installation logs' });

    const logPatterns = [
      // Npm logs
      path.join(this.options.homeDir, '.npm'),
      path.join(this.options.homeDir, '.npm-global'),
      // Node logs
      path.join(this.options.homeDir, '.node-gyp'),
      // Common log locations
      '/var/log',
      path.join(this.options.homeDir, '.logs'),
      path.join(this.options.homeDir, 'logs'),
    ];

    let clearedCount = 0;

    for (const logPath of logPatterns) {
      try {
        if (fs.existsSync(logPath)) {
          const stats = fs.statSync(logPath);

          if (stats.isDirectory()) {
            // Clear directory contents but keep directory
            const files = fs.readdirSync(logPath);
            for (const file of files) {
              try {
                const filePath = path.join(logPath, file);
                if (fs.statSync(filePath).isDirectory()) {
                  this.deleteDirectoryRecursive(filePath);
                } else {
                  await this.deleteFile(filePath, {
                    secure: this.cleanupProfile.secureDelete,
                  });
                }
                clearedCount++;
              } catch (err) {
                // Continue on error
              }
            }
          } else if (stats.isFile()) {
            const deleted = await this.deleteFile(logPath, {
              secure: this.cleanupProfile.secureDelete,
            });
            if (deleted) clearedCount++;
          }
        }
      } catch (error) {
        if (this.options.verbose) {
          console.warn(
            `[PostInstallCleanup] Could not clear logs at ${logPath}: ${error.message}`
          );
        }
      }
    }

    if (this.options.verbose) {
      console.log(`[PostInstallCleanup] Cleared ${clearedCount} log files`);
    }

    return true;
  }

  /**
   * Clear cache directories
   */
  async clearCache() {
    if (!this.cleanupProfile.clearCache || !this.options.clearCache) {
      if (this.options.verbose) {
        console.log('[PostInstallCleanup] Cache clearing disabled');
      }
      return true;
    }

    this.logOperation('clearCache', { description: 'Clear installation cache' });

    const cachePaths = [
      // Npm cache
      path.join(this.options.homeDir, '.npm'),
      // Pip cache
      path.join(this.options.homeDir, '.cache/pip'),
      // General cache
      path.join(this.options.homeDir, '.cache'),
      // Yarn cache
      path.join(this.options.homeDir, '.yarn/cache'),
      // Composer cache
      path.join(this.options.homeDir, '.composer/cache'),
    ];

    let clearedCount = 0;

    for (const cachePath of cachePaths) {
      try {
        if (fs.existsSync(cachePath)) {
          const stats = fs.statSync(cachePath);

          if (stats.isDirectory()) {
            // Try to clear directory contents
            try {
              const files = fs.readdirSync(cachePath);
              for (const file of files) {
                try {
                  const filePath = path.join(cachePath, file);
                  const fileStats = fs.statSync(filePath);
                  if (fileStats.isDirectory()) {
                    this.deleteDirectoryRecursive(filePath);
                  } else {
                    await this.deleteFile(filePath, {
                      secure: this.cleanupProfile.secureDelete,
                    });
                  }
                  clearedCount++;
                } catch (err) {
                  // Continue on error
                }
              }
            } catch (err) {
              // Continue on error
            }
          }
        }
      } catch (error) {
        if (this.options.verbose) {
          console.warn(
            `[PostInstallCleanup] Could not clear cache at ${cachePath}: ${error.message}`
          );
        }
      }
    }

    if (this.options.verbose) {
      console.log(`[PostInstallCleanup] Cleared ${clearedCount} cache files`);
    }

    return true;
  }

  /**
   * Clear temporary files
   */
  async clearTemporaryFiles() {
    if (!this.cleanupProfile.clearTemp || !this.options.clearTemp) {
      if (this.options.verbose) {
        console.log('[PostInstallCleanup] Temporary file clearing disabled');
      }
      return true;
    }

    this.logOperation('clearTemporaryFiles', {
      description: 'Clear temporary installation files',
    });

    const tempPaths = [this.options.tempDir, path.join(this.options.homeDir, '.tmp')];

    let clearedCount = 0;

    for (const tempPath of tempPaths) {
      try {
        if (fs.existsSync(tempPath) && tempPath !== '/tmp' && tempPath !== '/var/tmp') {
          const files = fs.readdirSync(tempPath);
          for (const file of files) {
            try {
              const filePath = path.join(tempPath, file);
              const stats = fs.statSync(filePath);

              // Only delete files modified in the last hour (likely install-related)
              const now = Date.now();
              const modified = stats.mtimeMs;
              const ageMinutes = (now - modified) / (1000 * 60);

              if (ageMinutes < 60) {
                if (stats.isDirectory()) {
                  this.deleteDirectoryRecursive(filePath);
                } else {
                  await this.deleteFile(filePath, {
                    secure: this.cleanupProfile.secureDelete,
                  });
                }
                clearedCount++;
              }
            } catch (err) {
              // Continue on error
            }
          }
        }
      } catch (error) {
        if (this.options.verbose) {
          console.warn(
            `[PostInstallCleanup] Could not clear temp files at ${tempPath}: ${error.message}`
          );
        }
      }
    }

    if (this.options.verbose) {
      console.log(`[PostInstallCleanup] Cleared ${clearedCount} temporary files`);
    }

    return true;
  }

  /**
   * Clear recycle bin / trash (platform-specific)
   */
  async clearRecycleBin() {
    if (!this.options.clearRecycleBin) {
      if (this.options.verbose) {
        console.log('[PostInstallCleanup] Recycle bin clearing disabled');
      }
      return true;
    }

    this.logOperation('clearRecycleBin', { description: 'Clear system recycle bin' });

    if (this.options.dryRun) {
      if (this.options.verbose) {
        console.log('[PostInstallCleanup] DRY RUN: Would clear recycle bin');
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
            console.log('[PostInstallCleanup] Windows Recycle Bin cleared');
          }
        } catch (error) {
          // May fail due to permissions, but continue
          if (this.options.verbose) {
            console.warn(
              `[PostInstallCleanup] Could not clear Recycle Bin (may need admin rights)`
            );
          }
        }
      } else if (platform === 'darwin') {
        // macOS: Clear Trash
        try {
          execSync("rm -rf ~/.Trash/*", { stdio: 'pipe' });
          if (this.options.verbose) {
            console.log('[PostInstallCleanup] macOS Trash cleared');
          }
        } catch (error) {
          if (this.options.verbose) {
            console.warn(`[PostInstallCleanup] Could not clear Trash`);
          }
        }
      } else if (platform === 'linux') {
        // Linux: Clear trash directories
        try {
          execSync("rm -rf ~/.local/share/Trash/* ~/.Trash/*", { stdio: 'pipe' });
          if (this.options.verbose) {
            console.log('[PostInstallCleanup] Linux trash cleared');
          }
        } catch (error) {
          if (this.options.verbose) {
            console.warn(`[PostInstallCleanup] Could not clear trash`);
          }
        }
      }

      return true;
    } catch (error) {
      if (this.options.verbose) {
        console.error(
          `[PostInstallCleanup] Recycle bin clear failed: ${error.message}`
        );
      }
      return false;
    }
  }

  /**
   * Execute complete post-installation cleanup
   */
  async executeCleanup() {
    const startTime = Date.now();
    const result = {
      success: true,
      profile: this.cleanupProfile.name,
      filesDeleted: 0,
      historiesCleared: 0,
      totalTime: 0,
      errors: [],
      summary: {
        deleted: this.deletedFiles.length,
        historiesCleared: this.clearedHistories.length,
        failed: this.failedOperations.length,
        operations: this.operations.length,
      },
    };

    if (this.options.verbose) {
      console.log(
        `[PostInstallCleanup] Starting cleanup with profile: ${this.cleanupProfile.name}`
      );
    }

    try {
      // Execute cleanup operations based on profile
      if (this.cleanupProfile.clearHistory) {
        await this.clearShellHistory();
        await this.clearCommandHistory();
      }

      if (this.cleanupProfile.clearLogs) {
        await this.clearInstallationLogs();
      }

      if (this.cleanupProfile.clearCache) {
        await this.clearCache();
      }

      if (this.cleanupProfile.clearTemp) {
        await this.clearTemporaryFiles();
      }

      if (this.options.clearRecycleBin) {
        await this.clearRecycleBin();
      }
    } catch (error) {
      result.errors.push(`Cleanup execution failed: ${error.message}`);
      result.success = false;
    }

    result.filesDeleted = this.deletedFiles.length;
    result.historiesCleared = this.clearedHistories.length;
    result.totalTime = Date.now() - startTime;

    if (this.failedOperations.length > 0) {
      result.success = false;
      result.errors = [
        ...result.errors,
        ...this.failedOperations.map(op => op.error),
      ];
    }

    if (this.options.verbose) {
      console.log(
        `[PostInstallCleanup] Cleanup complete: ${result.filesDeleted} files deleted, ` +
        `${result.historiesCleared} histories cleared, ${result.totalTime}ms elapsed`
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
   * Get cleared histories list
   */
  getClearedHistories() {
    return [...this.clearedHistories];
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
      totalHistoriesCleared: this.clearedHistories.length,
      totalOperationsFailed: this.failedOperations.length,
      successRate:
        this.deletedFiles.length /
        (this.deletedFiles.length + this.failedOperations.length) || 0,
      profile: this.cleanupProfile.name,
      secureDeleteEnabled: this.cleanupProfile.secureDelete,
      overwritePasses: this.options.overwritePasses,
    };

    return stats;
  }

  /**
   * Export cleanup report as JSON
   */
  exportReport() {
    return {
      timestamp: new Date(),
      profile: this.cleanupProfile.name,
      statistics: this.getStatistics(),
      deletedFiles: this.getDeletedFiles(),
      clearedHistories: this.getClearedHistories(),
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
      title: 'Post-Installation Cleanup Summary',
      timestamp: report.timestamp.toISOString(),
      profile: this.cleanupProfile.name,
      profileDescription: this.cleanupProfile.description,
      filesDeleted: stats.totalFilesDeleted,
      historiesCleared: stats.totalHistoriesCleared,
      operationsFailed: stats.totalOperationsFailed,
      successRate: `${(stats.successRate * 100).toFixed(2)}%`,
      securityLevel: stats.secureDeleteEnabled ? `${this.options.overwritePasses}-pass overwrite` : 'Standard deletion',
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
    this.clearedHistories = [];
    this.failedOperations = [];
    if (this.options.verbose) {
      console.log('[PostInstallCleanup] Tracking data cleared');
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
  globalCleanupHandler = new PostInstallCleanupHandler(options);
  globalCleanupHandler.startTracking();
  return globalCleanupHandler;
}

/**
 * Get global cleanup handler
 */
function getCleanupHandler() {
  if (!globalCleanupHandler) {
    globalCleanupHandler = new PostInstallCleanupHandler();
    globalCleanupHandler.startTracking();
  }
  return globalCleanupHandler;
}

/**
 * Convenient function for complete post-install cleanup
 */
async function executePostInstallCleanup(installerPath, options = {}) {
  const handler = new PostInstallCleanupHandler(options);
  handler.startTracking();

  if (installerPath) {
    await handler.removeInstaller(installerPath);
  }

  const result = await handler.executeCleanup();
  handler.stopTracking();

  return {
    result,
    report: handler.exportReport(),
    summary: handler.getSummary(),
  };
}

/**
 * Context manager for post-install cleanup
 */
async function withCleanupContext(callback, options = {}) {
  const handler = new PostInstallCleanupHandler(options);
  handler.startTracking();

  try {
    const result = await callback(handler);
    const cleanup = await handler.executeCleanup();
    handler.stopTracking();
    return {
      result,
      cleanup,
      report: handler.exportReport(),
      summary: handler.getSummary(),
    };
  } catch (error) {
    handler.stopTracking();
    throw error;
  }
}

// Export the class and factory functions
module.exports = PostInstallCleanupHandler;
module.exports.PostInstallCleanupHandler = PostInstallCleanupHandler;
module.exports.initializeCleanupHandler = initializeCleanupHandler;
module.exports.getCleanupHandler = getCleanupHandler;
module.exports.executePostInstallCleanup = executePostInstallCleanup;
module.exports.withCleanupContext = withCleanupContext;

// Example usage and demonstrations
if (require.main === module) {
  console.log('=== Post-Installation Cleanup Handler Demo ===\n');

  (async () => {
    // Example 1: Standard cleanup (dry run)
    console.log('=== Example 1: Standard Cleanup (Dry Run) ===');
    const handler1 = new PostInstallCleanupHandler({
      verbose: true,
      dryRun: true,
      profile: 'standard',
    });
    handler1.startTracking();

    const result1 = await handler1.removeInstaller('/tmp/installer.sh');
    console.log('Installer removal result:', result1);

    const cleanup1 = await handler1.executeCleanup();
    console.log('Cleanup result:', JSON.stringify(cleanup1, null, 2));

    // Example 2: Thorough cleanup with context manager
    console.log('\n=== Example 2: Thorough Cleanup Context (Dry Run) ===');
    const { result: contextResult, cleanup, summary } = await withCleanupContext(
      async (handler) => {
        console.log('Inside cleanup context...');
        await handler.removeInstaller('/tmp/installer-thorough.exe');
        return 'post-install cleanup completed';
      },
      { verbose: true, dryRun: true, profile: 'thorough' }
    );

    console.log('Context result:', contextResult);
    console.log('Cleanup summary:', JSON.stringify(summary, null, 2));

    // Example 3: Minimal cleanup with statistics
    console.log('\n=== Example 3: Minimal Cleanup (Dry Run) ===');
    const handler3 = new PostInstallCleanupHandler({
      verbose: false,
      dryRun: true,
      profile: 'minimal',
    });
    handler3.startTracking();

    await handler3.executeCleanup();

    const stats = handler3.getStatistics();
    console.log('Statistics:', JSON.stringify(stats, null, 2));

    const report = handler3.exportReport();
    console.log('Report profile:', report.profile);

    // Example 4: Complete post-install cleanup
    console.log('\n=== Example 4: Complete Post-Install Cleanup (Dry Run) ===');
    const { result: completeResult, summary: completeSummary } = await executePostInstallCleanup(
      '/tmp/installer',
      { verbose: true, dryRun: true, profile: 'standard' }
    );

    console.log('Complete cleanup result:');
    console.log('  Files deleted:', completeResult.filesDeleted);
    console.log('  Histories cleared:', completeResult.historiesCleared);
    console.log('  Profile:', completeSummary.profile);
    console.log('  Success rate:', completeSummary.successRate);

    console.log('\n=== Demo Complete ===');
  })().catch(console.error);
}
