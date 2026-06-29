/**
 * File Cleanup Handler Test Suite
 * Tests secure file deletion with trace removal
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const FileCleanupHandler = require('./file-cleanup-handler');

/**
 * Test suite for FileCleanupHandler
 */
class FileCleanupHandlerTests {
  constructor() {
    this.testDir = path.join(os.tmpdir(), 'file-cleanup-tests');
    this.testResults = [];
  }

  /**
   * Setup test environment
   */
  setup() {
    if (!fs.existsSync(this.testDir)) {
      fs.mkdirSync(this.testDir, { recursive: true });
    }
    console.log(`Test directory created: ${this.testDir}\n`);
  }

  /**
   * Cleanup test environment
   */
  teardown() {
    try {
      if (fs.existsSync(this.testDir)) {
        fs.rmSync(this.testDir, { recursive: true, force: true });
      }
      console.log(`\nTest directory cleaned up\n`);
    } catch (error) {
      console.warn(`Warning: Could not clean test directory: ${error.message}`);
    }
  }

  /**
   * Assert test condition
   */
  assert(condition, message) {
    if (!condition) {
      throw new Error(`Assertion failed: ${message}`);
    }
  }

  /**
   * Test 1: Basic file deletion
   */
  async testBasicFileDeletion() {
    console.log('Test 1: Basic File Deletion (Dry Run)\n');

    const testFile = path.join(this.testDir, 'test_basic.txt');
    fs.writeFileSync(testFile, 'Test content for basic deletion');

    const handler = new FileCleanupHandler({
      verbose: true,
      dryRun: true,
    });

    handler.startTracking();
    const result = await handler.deleteFile(testFile);

    this.assert(result === true, 'File deletion should succeed in dry-run');
    this.assert(
      fs.existsSync(testFile),
      'File should still exist in dry-run mode'
    );

    console.log('✓ Test passed\n');
    this.testResults.push({ test: 'Basic File Deletion', status: 'PASSED' });
  }

  /**
   * Test 2: Secure overwrite
   */
  async testSecureOverwrite() {
    console.log('Test 2: Secure Overwrite (Dry Run)\n');

    const testFile = path.join(this.testDir, 'test_overwrite.txt');
    const originalContent = 'Sensitive data that will be overwritten';
    fs.writeFileSync(testFile, originalContent);

    const handler = new FileCleanupHandler({
      verbose: true,
      dryRun: true,
      overwritePasses: 3,
    });

    handler.startTracking();

    // Test overwrite without deletion
    const overwritten = await handler.overwriteFileContents(testFile, 3);
    this.assert(overwritten === true, 'Overwrite should succeed');
    this.assert(
      fs.existsSync(testFile),
      'File should still exist in dry-run mode'
    );

    console.log('✓ Test passed\n');
    this.testResults.push({ test: 'Secure Overwrite', status: 'PASSED' });
  }

  /**
   * Test 3: Batch deletion
   */
  async testBatchDeletion() {
    console.log('Test 3: Batch File Deletion (Dry Run)\n');

    const files = [
      path.join(this.testDir, 'batch_file_1.txt'),
      path.join(this.testDir, 'batch_file_2.txt'),
      path.join(this.testDir, 'batch_file_3.txt'),
    ];

    files.forEach(file => {
      fs.writeFileSync(file, 'Batch test content');
    });

    const handler = new FileCleanupHandler({
      verbose: true,
      dryRun: true,
    });

    handler.startTracking();
    const result = await handler.secureDeleteBatch(files);

    this.assert(result.total === 3, 'Should process all 3 files');
    this.assert(result.success === 3, 'All files should be marked for deletion');

    files.forEach(file => {
      this.assert(
        fs.existsSync(file),
        `File ${file} should still exist in dry-run`
      );
    });

    console.log('✓ Test passed\n');
    this.testResults.push({ test: 'Batch File Deletion', status: 'PASSED' });
  }

  /**
   * Test 4: Statistics tracking
   */
  async testStatisticsTracking() {
    console.log('Test 4: Statistics and Reporting\n');

    const handler = new FileCleanupHandler({
      verbose: true,
      dryRun: true,
      overwritePasses: 3,
    });

    handler.startTracking();

    const testFiles = [
      path.join(this.testDir, 'stat_file_1.txt'),
      path.join(this.testDir, 'stat_file_2.txt'),
    ];

    testFiles.forEach(file => {
      fs.writeFileSync(file, 'Statistics test content');
    });

    await handler.secureDeleteBatch(testFiles);

    const stats = handler.getStatistics();
    console.log('Statistics:', JSON.stringify(stats, null, 2));

    this.assert(stats.totalFilesDeleted === 2, 'Should track 2 deleted files');
    this.assert(
      stats.successRate === 1,
      'Should have 100% success rate'
    );

    const summary = handler.getSummary();
    console.log('\nSummary:', JSON.stringify(summary, null, 2));

    this.assert(
      summary.filesDeleted === 2,
      'Summary should show 2 deleted files'
    );

    console.log('✓ Test passed\n');
    this.testResults.push({ test: 'Statistics Tracking', status: 'PASSED' });
  }

  /**
   * Test 5: Operation logging
   */
  async testOperationLogging() {
    console.log('Test 5: Operation Logging\n');

    const handler = new FileCleanupHandler({
      verbose: true,
      trackOperations: true,
    });

    handler.startTracking();
    handler.logOperation('testDelete', {
      filePath: '/test/path/file.txt',
    });
    handler.logOperation('testOverwrite', {
      filePath: '/test/path/file2.txt',
    });

    const operations = handler.getOperations();
    console.log('Logged operations:', JSON.stringify(operations, null, 2));

    this.assert(operations.length === 2, 'Should have 2 operations logged');
    this.assert(
      operations[0].operation === 'testDelete',
      'First operation should be testDelete'
    );

    console.log('✓ Test passed\n');
    this.testResults.push({ test: 'Operation Logging', status: 'PASSED' });
  }

  /**
   * Test 6: File not found handling
   */
  async testFileNotFoundHandling() {
    console.log('Test 6: File Not Found Handling\n');

    const handler = new FileCleanupHandler({
      verbose: true,
    });

    handler.startTracking();

    const nonExistentFile = path.join(
      this.testDir,
      'non_existent_file.txt'
    );
    const result = await handler.deleteFile(nonExistentFile);

    this.assert(result === false, 'Should fail for non-existent file');

    const failedOps = handler.getFailedOperations();
    this.assert(
      failedOps.length > 0,
      'Should track failed operations'
    );

    console.log('✓ Test passed\n');
    this.testResults.push({
      test: 'File Not Found Handling',
      status: 'PASSED',
    });
  }

  /**
   * Test 7: Context manager
   */
  async testContextManager() {
    console.log('Test 7: Context Manager (Dry Run)\n');

    const { result, cleanup, report } = await FileCleanupHandler.withCleanupContext(
      async (handler) => {
        const testFile = path.join(this.testDir, 'context_file.txt');
        fs.writeFileSync(testFile, 'Context test content');
        await handler.secureDelete(testFile);
        return 'operation completed';
      },
      { verbose: true, dryRun: true }
    );

    console.log('Context result:', result);
    console.log('Cleanup:', JSON.stringify(cleanup, null, 2));

    this.assert(result === 'operation completed', 'Should return operation result');
    this.assert(cleanup.success !== undefined, 'Should have cleanup result');

    console.log('✓ Test passed\n');
    this.testResults.push({ test: 'Context Manager', status: 'PASSED' });
  }

  /**
   * Test 8: Recycle bin clearing flag
   */
  async testRecycleBinClearing() {
    console.log('Test 8: Recycle Bin Clearing (Dry Run)\n');

    const handler = new FileCleanupHandler({
      verbose: true,
      dryRun: true,
      clearRecycleBin: true,
    });

    handler.startTracking();
    const result = await handler.clearRecycleBin();

    this.assert(result === true, 'Recycle bin clearing should succeed');

    console.log('✓ Test passed\n');
    this.testResults.push({ test: 'Recycle Bin Clearing', status: 'PASSED' });
  }

  /**
   * Test 9: Export report
   */
  async testExportReport() {
    console.log('Test 9: Export Report\n');

    const handler = new FileCleanupHandler({
      verbose: false,
      dryRun: true,
    });

    handler.startTracking();

    const testFile = path.join(this.testDir, 'report_file.txt');
    fs.writeFileSync(testFile, 'Report test content');

    await handler.secureDelete(testFile);

    const report = handler.exportReport();
    console.log('Exported report:', JSON.stringify(report, null, 2));

    this.assert(report.timestamp !== undefined, 'Report should have timestamp');
    this.assert(
      report.statistics !== undefined,
      'Report should have statistics'
    );
    this.assert(report.options !== undefined, 'Report should have options');

    console.log('✓ Test passed\n');
    this.testResults.push({ test: 'Export Report', status: 'PASSED' });
  }

  /**
   * Test 10: Convenience functions
   */
  async testConvenienceFunctions() {
    console.log('Test 10: Convenience Functions (Dry Run)\n');

    const testFile1 = path.join(this.testDir, 'convenience_1.txt');
    const testFile2 = path.join(this.testDir, 'convenience_2.txt');

    fs.writeFileSync(testFile1, 'Convenience test 1');
    fs.writeFileSync(testFile2, 'Convenience test 2');

    // Test single file convenience function
    const singleResult = await FileCleanupHandler.secureDeleteFile(testFile1, {
      dryRun: true,
      verbose: false,
    });
    this.assert(singleResult === true, 'Single file delete should succeed');

    // Test batch convenience function
    const batchResult = await FileCleanupHandler.secureDeleteFiles(
      [testFile2],
      { dryRun: true, verbose: false }
    );
    this.assert(batchResult.success === 1, 'Batch delete should succeed');

    console.log('✓ Test passed\n');
    this.testResults.push({
      test: 'Convenience Functions',
      status: 'PASSED',
    });
  }

  /**
   * Run all tests
   */
  async runAll() {
    this.setup();

    console.log('===================================');
    console.log('File Cleanup Handler Test Suite');
    console.log('===================================\n');

    const tests = [
      this.testBasicFileDeletion.bind(this),
      this.testSecureOverwrite.bind(this),
      this.testBatchDeletion.bind(this),
      this.testStatisticsTracking.bind(this),
      this.testOperationLogging.bind(this),
      this.testFileNotFoundHandling.bind(this),
      this.testContextManager.bind(this),
      this.testRecycleBinClearing.bind(this),
      this.testExportReport.bind(this),
      this.testConvenienceFunctions.bind(this),
    ];

    for (const test of tests) {
      try {
        await test();
      } catch (error) {
        console.error(`✗ Test failed: ${error.message}\n`);
        this.testResults.push({
          test: test.name,
          status: 'FAILED',
          error: error.message,
        });
      }
    }

    this.teardown();

    // Print summary
    this.printSummary();
  }

  /**
   * Print test summary
   */
  printSummary() {
    console.log('===================================');
    console.log('Test Summary');
    console.log('===================================\n');

    const passed = this.testResults.filter(r => r.status === 'PASSED').length;
    const failed = this.testResults.filter(r => r.status === 'FAILED').length;
    const total = this.testResults.length;

    console.log(`Total: ${total}`);
    console.log(`Passed: ${passed}`);
    console.log(`Failed: ${failed}`);
    console.log(`Success Rate: ${((passed / total) * 100).toFixed(2)}%\n`);

    console.log('Detailed Results:');
    console.log(JSON.stringify(this.testResults, null, 2));
  }
}

// Run tests if executed directly
if (require.main === module) {
  const tests = new FileCleanupHandlerTests();
  tests.runAll().catch(console.error);
}

module.exports = FileCleanupHandlerTests;
