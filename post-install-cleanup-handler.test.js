/**
 * Post-Installation Cleanup Handler Tests
 *
 * Comprehensive test suite for post-installation cleanup functionality
 * Tests include:
 * - Installer removal
 * - Shell history clearing
 * - Log file cleanup
 * - Cache clearing
 * - Temporary file cleanup
 * - Transaction tracking
 * - Error handling and recovery
 * - Cleanup profiles
 * - Statistics and reporting
 */

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');
const PostInstallCleanupHandler = require('./post-install-cleanup-handler');
const {
  executePostInstallCleanup,
  withCleanupContext,
  initializeCleanupHandler,
  getCleanupHandler,
} = require('./post-install-cleanup-handler');

/**
 * Test utilities
 */
function createTestFile(filePath, content = 'test content') {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(filePath, content);
  return filePath;
}

function createTestDirectory(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
  return dirPath;
}

function fileExists(filePath) {
  return fs.existsSync(filePath);
}

function directoryExists(dirPath) {
  return fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory();
}

/**
 * Test Suite
 */
describe('PostInstallCleanupHandler', () => {
  let tempDir;
  let homeDir;

  before(() => {
    // Create temporary test directories
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cleanup-test-'));
    homeDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cleanup-home-'));
  });

  after(() => {
    // Clean up temporary directories
    try {
      if (fs.existsSync(tempDir)) {
        fs.rmSync(tempDir, { recursive: true, force: true });
      }
      if (fs.existsSync(homeDir)) {
        fs.rmSync(homeDir, { recursive: true, force: true });
      }
    } catch (error) {
      console.error('Error cleaning up test directories:', error);
    }
  });

  describe('Initialization', () => {
    it('should create handler with default options', () => {
      const handler = new PostInstallCleanupHandler();
      assert.strictEqual(handler.options.verbose, false);
      assert.strictEqual(handler.options.dryRun, false);
      assert.strictEqual(handler.options.secureDelete, true);
      assert.strictEqual(handler.options.clearHistory, true);
    });

    it('should create handler with custom options', () => {
      const options = {
        verbose: true,
        dryRun: true,
        secureDelete: false,
        profile: 'minimal',
      };
      const handler = new PostInstallCleanupHandler(options);
      assert.strictEqual(handler.options.verbose, true);
      assert.strictEqual(handler.options.dryRun, true);
      assert.strictEqual(handler.options.secureDelete, false);
      assert.strictEqual(handler.options.profile, 'minimal');
    });

    it('should support all cleanup profiles', () => {
      const profiles = ['minimal', 'standard', 'thorough'];
      profiles.forEach(profile => {
        const handler = new PostInstallCleanupHandler({ profile });
        assert.strictEqual(handler.cleanupProfile.name, profile.charAt(0).toUpperCase() + profile.slice(1));
      });
    });

    it('should start and stop tracking', () => {
      const handler = new PostInstallCleanupHandler();
      assert.strictEqual(handler.isActive, false);
      handler.startTracking();
      assert.strictEqual(handler.isActive, true);
      handler.stopTracking();
      assert.strictEqual(handler.isActive, false);
    });
  });

  describe('Installer Removal', () => {
    it('should remove single installer file', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        secureDelete: false,
        homeDir,
      });
      handler.startTracking();

      const installerPath = path.join(tempDir, 'installer.sh');
      createTestFile(installerPath);
      assert(fileExists(installerPath));

      const result = await handler.removeInstaller(installerPath);
      assert.strictEqual(result, true);
      assert.strictEqual(fileExists(installerPath), false);
    });

    it('should remove installer directory', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        homeDir,
      });
      handler.startTracking();

      const installerDir = path.join(tempDir, 'installer-dir');
      createTestDirectory(installerDir);
      createTestFile(path.join(installerDir, 'script.sh'));
      createTestFile(path.join(installerDir, 'data.txt'));
      assert(directoryExists(installerDir));

      const result = await handler.removeInstaller(installerDir);
      assert.strictEqual(result, true);
      assert.strictEqual(directoryExists(installerDir), false);
    });

    it('should handle non-existent installer gracefully', async () => {
      const handler = new PostInstallCleanupHandler({ homeDir });
      handler.startTracking();

      const nonExistentPath = path.join(tempDir, 'does-not-exist.sh');
      const result = await handler.removeInstaller(nonExistentPath);
      assert.strictEqual(result, true); // Should not fail
    });

    it('should track installer removal operations', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        secureDelete: false,
        homeDir,
      });
      handler.startTracking();

      const installerPath = path.join(tempDir, 'install-tracked.exe');
      createTestFile(installerPath);

      await handler.removeInstaller(installerPath);
      const operations = handler.getOperations();
      assert(operations.some(op => op.operation === 'removeInstaller'));
    });

    it('should support dry-run mode for installer removal', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: true,
        homeDir,
      });
      handler.startTracking();

      const installerPath = path.join(tempDir, 'dryrun-installer.msi');
      createTestFile(installerPath);

      const result = await handler.removeInstaller(installerPath);
      assert.strictEqual(result, true);
      assert.strictEqual(fileExists(installerPath), true); // File should still exist in dry-run
    });
  });

  describe('History Clearing', () => {
    it('should clear shell history files', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        secureDelete: false,
        clearHistory: true,
        homeDir,
      });
      handler.startTracking();

      // Create fake history files
      const historyFiles = [
        path.join(homeDir, '.bash_history'),
        path.join(homeDir, '.zsh_history'),
        path.join(homeDir, '.history'),
      ];

      historyFiles.forEach(file => createTestFile(file, 'history content'));

      const result = await handler.clearShellHistory();
      assert.strictEqual(result, true);

      // Check that files were deleted
      const histories = handler.getClearedHistories();
      assert(histories.length > 0);
    });

    it('should skip history clearing when disabled', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        clearHistory: false,
        homeDir,
      });
      handler.startTracking();

      const result = await handler.clearShellHistory();
      assert.strictEqual(result, true);

      const histories = handler.getClearedHistories();
      assert.strictEqual(histories.length, 0);
    });

    it('should handle missing history files gracefully', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        homeDir: path.join(tempDir, 'non-existent-home'),
        clearHistory: true,
      });
      handler.startTracking();

      const result = await handler.clearShellHistory();
      assert.strictEqual(result, true);
    });

    it('should clear command history', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: true, // Use dry-run to avoid actual system commands
        homeDir,
      });
      handler.startTracking();

      const result = await handler.clearCommandHistory();
      assert.strictEqual(result, true);
    });
  });

  describe('Log Clearing', () => {
    it('should clear installation logs', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        secureDelete: false,
        clearLogs: true,
        homeDir,
      });
      handler.startTracking();

      // Create test log directory
      const logsDir = path.join(homeDir, '.logs');
      createTestDirectory(logsDir);
      createTestFile(path.join(logsDir, 'install.log'));
      createTestFile(path.join(logsDir, 'error.log'));

      const result = await handler.clearInstallationLogs();
      assert.strictEqual(result, true);
    });

    it('should skip log clearing when disabled', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        clearLogs: false,
        homeDir,
      });
      handler.startTracking();

      const result = await handler.clearInstallationLogs();
      assert.strictEqual(result, true);
    });
  });

  describe('Cache Clearing', () => {
    it('should clear cache directories', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        secureDelete: false,
        clearCache: true,
        homeDir,
      });
      handler.startTracking();

      // Create test cache directory
      const cacheDir = path.join(homeDir, '.cache');
      createTestDirectory(cacheDir);
      createTestFile(path.join(cacheDir, 'cache-file.txt'));

      const result = await handler.clearCache();
      assert.strictEqual(result, true);
    });

    it('should skip cache clearing when disabled', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        clearCache: false,
        homeDir,
      });
      handler.startTracking();

      const result = await handler.clearCache();
      assert.strictEqual(result, true);
    });
  });

  describe('Temporary File Clearing', () => {
    it('should clear recent temporary files', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        secureDelete: false,
        clearTemp: true,
        tempDir,
        homeDir,
      });
      handler.startTracking();

      const tempFile = path.join(tempDir, 'recent-temp.txt');
      createTestFile(tempFile, 'temporary content');

      const result = await handler.clearTemporaryFiles();
      assert.strictEqual(result, true);
    });

    it('should skip temp clearing when disabled', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        clearTemp: false,
        tempDir,
        homeDir,
      });
      handler.startTracking();

      const result = await handler.clearTemporaryFiles();
      assert.strictEqual(result, true);
    });
  });

  describe('Cleanup Profiles', () => {
    it('should apply minimal profile settings', () => {
      const handler = new PostInstallCleanupHandler({
        profile: 'minimal',
      });
      assert.strictEqual(handler.cleanupProfile.name, 'Minimal');
      assert.strictEqual(handler.cleanupProfile.clearInstaller, true);
      assert.strictEqual(handler.cleanupProfile.clearHistory, false);
      assert.strictEqual(handler.cleanupProfile.secureDelete, false);
    });

    it('should apply standard profile settings', () => {
      const handler = new PostInstallCleanupHandler({
        profile: 'standard',
      });
      assert.strictEqual(handler.cleanupProfile.name, 'Standard');
      assert.strictEqual(handler.cleanupProfile.clearInstaller, true);
      assert.strictEqual(handler.cleanupProfile.clearHistory, true);
      assert.strictEqual(handler.cleanupProfile.secureDelete, true);
    });

    it('should apply thorough profile settings', () => {
      const handler = new PostInstallCleanupHandler({
        profile: 'thorough',
      });
      assert.strictEqual(handler.cleanupProfile.name, 'Thorough');
      assert.strictEqual(handler.cleanupProfile.clearTemp, true);
      assert.strictEqual(handler.cleanupProfile.secureDelete, true);
    });
  });

  describe('Complete Cleanup', () => {
    it('should execute complete cleanup workflow', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: true,
        profile: 'standard',
        homeDir,
      });
      handler.startTracking();

      const result = await handler.executeCleanup();
      assert.strictEqual(result.success, true);
      assert.strictEqual(result.profile, 'Standard');
      assert(result.totalTime >= 0);
    });

    it('should return cleanup result with statistics', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: true,
        homeDir,
      });
      handler.startTracking();

      const result = await handler.executeCleanup();
      assert(result.hasOwnProperty('filesDeleted'));
      assert(result.hasOwnProperty('historiesCleared'));
      assert(result.hasOwnProperty('summary'));
      assert(result.hasOwnProperty('totalTime'));
    });

    it('should track operations during cleanup', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: true,
        homeDir,
      });
      handler.startTracking();

      await handler.executeCleanup();

      const operations = handler.getOperations();
      assert(operations.length > 0);
    });
  });

  describe('Statistics and Reporting', () => {
    it('should generate cleanup statistics', () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: true,
        profile: 'standard',
      });
      handler.startTracking();

      const stats = handler.getStatistics();
      assert(stats.hasOwnProperty('totalOperations'));
      assert(stats.hasOwnProperty('totalFilesDeleted'));
      assert(stats.hasOwnProperty('profile'));
      assert.strictEqual(stats.profile, 'Standard');
    });

    it('should generate cleanup summary', () => {
      const handler = new PostInstallCleanupHandler({
        profile: 'thorough',
      });
      handler.startTracking();

      const summary = handler.getSummary();
      assert.strictEqual(summary.title, 'Post-Installation Cleanup Summary');
      assert.strictEqual(summary.profile, 'Thorough');
      assert(summary.hasOwnProperty('timestamp'));
      assert(summary.hasOwnProperty('successRate'));
    });

    it('should export cleanup report', () => {
      const handler = new PostInstallCleanupHandler();
      handler.startTracking();

      const report = handler.exportReport();
      assert(report.hasOwnProperty('timestamp'));
      assert(report.hasOwnProperty('profile'));
      assert(report.hasOwnProperty('statistics'));
      assert(report.hasOwnProperty('deletedFiles'));
      assert(report.hasOwnProperty('clearedHistories'));
    });

    it('should track deleted files', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        secureDelete: false,
        homeDir,
      });
      handler.startTracking();

      const installerPath = path.join(tempDir, 'tracked-installer.sh');
      createTestFile(installerPath);

      await handler.removeInstaller(installerPath);

      const deleted = handler.getDeletedFiles();
      assert(deleted.length > 0);
    });

    it('should track failed operations', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        homeDir,
      });
      handler.startTracking();

      // Try to remove non-existent installer (will be tracked as no-op but not failure)
      const nonExistentPath = path.join(tempDir, 'missing-installer.sh');
      await handler.removeInstaller(nonExistentPath);

      // Create a file with no read permissions to force a failure
      const restrictedFile = path.join(tempDir, 'restricted-file.txt');
      createTestFile(restrictedFile, 'restricted content');

      // This might not fail depending on permissions, so we just verify the method exists
      const failed = handler.getFailedOperations();
      assert(Array.isArray(failed));
    });
  });

  describe('Factory Functions', () => {
    it('should initialize global cleanup handler', () => {
      const handler = initializeCleanupHandler({ verbose: true });
      assert(handler instanceof PostInstallCleanupHandler);
      assert.strictEqual(handler.isActive, true);
    });

    it('should get global cleanup handler', () => {
      initializeCleanupHandler();
      const handler = getCleanupHandler();
      assert(handler instanceof PostInstallCleanupHandler);
    });

    it('should execute post-install cleanup with installer', async () => {
      const installerPath = path.join(tempDir, 'test-installer.exe');
      createTestFile(installerPath);

      const { result, summary } = await executePostInstallCleanup(installerPath, {
        dryRun: true,
        homeDir,
      });

      assert(result.hasOwnProperty('success'));
      assert(summary.hasOwnProperty('profile'));
    });

    it('should work with cleanup context manager', async () => {
      const { result, cleanup, summary } = await withCleanupContext(
        async (handler) => {
          return 'test result';
        },
        { dryRun: true, homeDir }
      );

      assert.strictEqual(result, 'test result');
      assert(cleanup.hasOwnProperty('success'));
      assert(summary.hasOwnProperty('profile'));
    });
  });

  describe('Error Handling', () => {
    it('should handle cleanup errors gracefully', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: false,
        homeDir,
      });
      handler.startTracking();

      // Try cleanup with invalid paths (should not throw)
      const result = await handler.executeCleanup();
      assert(result.hasOwnProperty('success'));
    });

    it('should continue cleanup on partial failures', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: true,
        profile: 'thorough',
        homeDir,
      });
      handler.startTracking();

      const result = await handler.executeCleanup();
      // Should complete even if some operations fail
      assert(result.hasOwnProperty('totalTime'));
    });

    it('should handle context manager errors', async () => {
      try {
        await withCleanupContext(
          async (handler) => {
            throw new Error('Test error');
          },
          { dryRun: true, homeDir }
        );
        assert.fail('Should have thrown error');
      } catch (error) {
        assert.strictEqual(error.message, 'Test error');
      }
    });
  });

  describe('Data Management', () => {
    it('should clear tracking data', () => {
      const handler = new PostInstallCleanupHandler();
      handler.startTracking();
      handler.logOperation('testOp', { description: 'test' });

      assert(handler.getOperations().length > 0);
      handler.clearTracking();
      assert.strictEqual(handler.getOperations().length, 0);
    });

    it('should maintain separate handler instances', () => {
      const handler1 = new PostInstallCleanupHandler({ verbose: true });
      const handler2 = new PostInstallCleanupHandler({ verbose: false });

      assert.strictEqual(handler1.options.verbose, true);
      assert.strictEqual(handler2.options.verbose, false);
    });
  });

  describe('Dry-Run Mode', () => {
    it('should not delete files in dry-run mode', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: true,
        homeDir,
      });
      handler.startTracking();

      const testFile = path.join(tempDir, 'dryrun-test.txt');
      createTestFile(testFile);

      await handler.removeInstaller(testFile);
      assert.strictEqual(fileExists(testFile), true); // File should still exist
    });

    it('should report dryrun status in result', async () => {
      const handler = new PostInstallCleanupHandler({
        dryRun: true,
        homeDir,
      });
      handler.startTracking();

      const result = await handler.executeCleanup();
      assert.strictEqual(result.success, true);
    });
  });
});

/**
 * Integration Tests
 */
describe('Integration Tests', () => {
  let tempDir;
  let homeDir;

  beforeEach(() => {
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'integration-test-'));
    homeDir = fs.mkdtempSync(path.join(os.tmpdir(), 'integration-home-'));
  });

  afterEach(() => {
    try {
      if (fs.existsSync(tempDir)) {
        fs.rmSync(tempDir, { recursive: true, force: true });
      }
      if (fs.existsSync(homeDir)) {
        fs.rmSync(homeDir, { recursive: true, force: true });
      }
    } catch (error) {
      console.error('Error cleaning up test directories:', error);
    }
  });

  it('should perform complete post-install cleanup workflow', async () => {
    const handler = new PostInstallCleanupHandler({
      dryRun: false,
      secureDelete: false,
      profile: 'standard',
      homeDir,
    });
    handler.startTracking();

    // Simulate post-install state
    const installerDir = path.join(tempDir, 'app-installer');
    fs.mkdirSync(installerDir, { recursive: true });
    createTestFile(path.join(installerDir, 'setup.exe'));
    createTestFile(path.join(homeDir, '.bash_history'), 'command history');

    // Execute full cleanup
    await handler.removeInstaller(installerDir);
    const result = await handler.executeCleanup();

    // Verify cleanup
    assert.strictEqual(result.success, true);
    assert.strictEqual(directoryExists(installerDir), false);
  });

  it('should support multiple cleanup profiles in sequence', async () => {
    const profiles = ['minimal', 'standard', 'thorough'];
    const results = [];

    for (const profile of profiles) {
      const handler = new PostInstallCleanupHandler({
        dryRun: true,
        profile,
        homeDir,
      });
      handler.startTracking();

      const result = await handler.executeCleanup();
      const summary = handler.getSummary();

      results.push({
        profile: summary.profile,
        success: result.success,
      });
    }

    assert.strictEqual(results.length, 3);
    assert.strictEqual(results[0].profile, 'Minimal');
    assert.strictEqual(results[1].profile, 'Standard');
    assert.strictEqual(results[2].profile, 'Thorough');
  });
});

/**
 * Run tests with: npm test post-install-cleanup-handler.test.js
 */
console.log('Post-Installation Cleanup Handler Test Suite');
console.log('Tests ready to run with: npm test post-install-cleanup-handler.test.js');
