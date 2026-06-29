/**
 * File Cleanup Handler - Integration Examples
 *
 * Real-world usage examples for secure file deletion with trace removal
 */

const FileCleanupHandler = require('./file-cleanup-handler');
const fs = require('fs');
const path = require('path');
const os = require('os');

/**
 * Example 1: Clean temporary files after processing
 */
async function example1_CleanTempFiles() {
  console.log('=== Example 1: Clean Temporary Files After Processing ===\n');

  const handler = new FileCleanupHandler({
    verbose: true,
    overwritePasses: 3,
  });

  handler.startTracking();

  try {
    // Simulate creating temporary files during processing
    const tempFiles = [
      path.join(os.tmpdir(), 'temp_data_001.tmp'),
      path.join(os.tmpdir(), 'temp_data_002.tmp'),
      path.join(os.tmpdir(), 'cache_001.tmp'),
    ];

    // Create test files (in real scenario, these would be created by your app)
    tempFiles.forEach(file => {
      if (!fs.existsSync(file)) {
        fs.writeFileSync(file, 'Temporary sensitive data...');
      }
    });

    console.log('Temp files created, now cleaning...\n');

    // Securely delete all temporary files
    const results = await handler.secureDeleteBatch(tempFiles, {
      secure: true,
      overwritePasses: 3,
    });

    // Execute cleanup
    const cleanup = await handler.executeCleanup();

    console.log('Cleanup Results:');
    console.log(JSON.stringify(cleanup, null, 2));

    handler.stopTracking();
  } catch (error) {
    console.error('Error:', error.message);
  }
}

/**
 * Example 2: Secure deletion with detailed reporting
 */
async function example2_DetailedReporting() {
  console.log('\n=== Example 2: Secure Deletion with Reporting ===\n');

  const handler = new FileCleanupHandler({
    verbose: true,
    overwritePasses: 5, // Higher security
    trackOperations: true,
  });

  handler.startTracking();

  try {
    // Create sensitive test file
    const sensitiveFile = path.join(os.tmpdir(), 'sensitive_data.txt');
    if (!fs.existsSync(sensitiveFile)) {
      fs.writeFileSync(sensitiveFile, 'HIGHLY SENSITIVE DATA - Customer PII and credentials');
    }

    console.log('Deleting sensitive file...\n');
    await handler.secureDelete(sensitiveFile);

    // Execute cleanup
    await handler.executeCleanup();

    // Generate and display report
    const report = handler.exportReport();
    console.log('\nCleanup Report:');
    console.log(JSON.stringify(report, null, 2));

    // Display summary
    const summary = handler.getSummary();
    console.log('\nCleanup Summary:');
    console.log(JSON.stringify(summary, null, 2));

    handler.stopTracking();
  } catch (error) {
    console.error('Error:', error.message);
  }
}

/**
 * Example 3: Batch cleanup of cache files
 */
async function example3_CacheCleanup() {
  console.log('\n=== Example 3: Cache and Cookie Files Cleanup ===\n');

  const handler = new FileCleanupHandler({
    verbose: true,
    clearRecycleBin: true,
    wipeMetadata: true,
  });

  handler.startTracking();

  try {
    // Simulate cache files
    const cacheDir = path.join(os.tmpdir(), 'cache');
    if (!fs.existsSync(cacheDir)) {
      fs.mkdirSync(cacheDir, { recursive: true });
    }

    const cacheFiles = [
      path.join(cacheDir, 'cache_001.db'),
      path.join(cacheDir, 'cookies.dat'),
      path.join(cacheDir, 'session_tokens.json'),
    ];

    // Create cache files
    cacheFiles.forEach(file => {
      if (!fs.existsSync(file)) {
        fs.writeFileSync(file, 'Cache data with tracking info...');
      }
    });

    console.log(`Cleaning ${cacheFiles.length} cache files...\n`);

    // Delete cache files
    const results = await handler.secureDeleteBatch(cacheFiles);

    // Cleanup
    const cleanup = await handler.executeCleanup();

    console.log('\nCache Cleanup Complete:');
    console.log(`Deleted: ${results.success}/${results.total} files`);
    console.log(`Recycle bin cleared: ${cleanup.recycleBinCleared}`);

    // Cleanup test directory
    try {
      fs.rmSync(cacheDir, { recursive: true, force: true });
    } catch (e) {
      // Ignore cleanup errors
    }

    handler.stopTracking();
  } catch (error) {
    console.error('Error:', error.message);
  }
}

/**
 * Example 4: Dry-run mode for safety verification
 */
async function example4_DryRunMode() {
  console.log('\n=== Example 4: Dry-Run Mode for Safety Verification ===\n');

  const handler = new FileCleanupHandler({
    verbose: true,
    dryRun: true, // Preview mode - no actual deletion
    overwritePasses: 3,
  });

  handler.startTracking();

  try {
    // Create test file
    const testFile = path.join(os.tmpdir(), 'test_dry_run.txt');
    if (!fs.existsSync(testFile)) {
      fs.writeFileSync(testFile, 'Test data for dry-run');
    }

    console.log('Running in DRY-RUN mode - no files will be deleted\n');

    // Delete in dry-run mode
    await handler.secureDelete(testFile);

    // Execute cleanup
    const cleanup = await handler.executeCleanup();

    console.log('\nDry-Run Result:');
    console.log(JSON.stringify(cleanup, null, 2));

    // Verify file still exists
    const fileExists = fs.existsSync(testFile);
    console.log(`\nFile still exists after dry-run: ${fileExists}`);

    // Now cleanup the test file
    if (fileExists) {
      fs.unlinkSync(testFile);
    }

    handler.stopTracking();
  } catch (error) {
    console.error('Error:', error.message);
  }
}

/**
 * Example 5: Context manager for automatic cleanup
 */
async function example5_ContextManager() {
  console.log('\n=== Example 5: Context Manager with Auto-Cleanup ===\n');

  try {
    const { result, cleanup, report } = await FileCleanupHandler.withCleanupContext(
      async (handler) => {
        console.log('Inside cleanup context...\n');

        // Create files to delete
        const file1 = path.join(os.tmpdir(), 'context_file_1.txt');
        const file2 = path.join(os.tmpdir(), 'context_file_2.txt');

        if (!fs.existsSync(file1)) {
          fs.writeFileSync(file1, 'Context file 1');
        }
        if (!fs.existsSync(file2)) {
          fs.writeFileSync(file2, 'Context file 2');
        }

        // Operations are automatically tracked
        await handler.secureDelete(file1);
        await handler.secureDelete(file2);

        return 'All files processed';
      },
      { verbose: true, dryRun: false }
    );

    console.log('\nContext Result:', result);
    console.log('Cleanup Success:', cleanup.success);
    console.log('Files Deleted:', cleanup.filesDeleted);

    handler.stopTracking();
  } catch (error) {
    console.error('Error:', error.message);
  }
}

/**
 * Example 6: Error handling and failed file recovery
 */
async function example6_ErrorHandling() {
  console.log('\n=== Example 6: Error Handling and Recovery ===\n');

  const handler = new FileCleanupHandler({
    verbose: true,
    maxRetries: 3,
    retryDelayMs: 100,
  });

  handler.startTracking();

  try {
    // Try to delete both existing and non-existing files
    const files = [
      path.join(os.tmpdir(), 'existing_file.txt'),
      path.join(os.tmpdir(), 'non_existing_file.txt'),
    ];

    // Create only the first file
    fs.writeFileSync(files[0], 'This file exists');

    console.log('Attempting to delete mix of existing and non-existing files...\n');

    const results = await handler.secureDeleteBatch(files);

    console.log('Batch Results:');
    console.log(`Success: ${results.success}/${results.total}`);
    console.log('Deleted:', results.deletedFiles);
    console.log('Failed:', results.failedFiles);

    // Get detailed failure info
    const failedOps = handler.getFailedOperations();
    console.log('\nDetailed Failures:');
    console.log(JSON.stringify(failedOps, null, 2));

    handler.stopTracking();
  } catch (error) {
    console.error('Error:', error.message);
  }
}

/**
 * Example 7: Statistics and analytics
 */
async function example7_Statistics() {
  console.log('\n=== Example 7: Cleanup Statistics and Analytics ===\n');

  const handler = new FileCleanupHandler({
    verbose: false,
    dryRun: true, // Use dry-run to simulate multiple operations
  });

  handler.startTracking();

  try {
    // Simulate cleanup operations
    const files = [];
    for (let i = 0; i < 5; i++) {
      const file = path.join(os.tmpdir(), `analytics_test_${i}.txt`);
      if (!fs.existsSync(file)) {
        fs.writeFileSync(file, `Test file ${i}`);
      }
      files.push(file);
    }

    console.log('Simulating cleanup of 5 files...\n');

    // Perform cleanup
    await handler.secureDeleteBatch(files);
    await handler.executeCleanup();

    // Get statistics
    const stats = handler.getStatistics();
    console.log('Cleanup Statistics:');
    console.log(JSON.stringify(stats, null, 2));

    // Get summary
    const summary = handler.getSummary();
    console.log('\nCleanup Summary:');
    console.log(JSON.stringify(summary, null, 2));

    // Cleanup test files
    files.forEach(file => {
      if (fs.existsSync(file)) {
        try {
          fs.unlinkSync(file);
        } catch (e) {
          // Ignore
        }
      }
    });

    handler.stopTracking();
  } catch (error) {
    console.error('Error:', error.message);
  }
}

/**
 * Example 8: Secure deletion with metadata removal
 */
async function example8_MetadataRemoval() {
  console.log('\n=== Example 8: File Metadata Removal ===\n');

  const handler = new FileCleanupHandler({
    verbose: true,
    wipeMetadata: true,
    dryRun: true,
  });

  handler.startTracking();

  try {
    const testFile = path.join(os.tmpdir(), 'metadata_test.txt');
    if (!fs.existsSync(testFile)) {
      fs.writeFileSync(testFile, 'File with metadata to remove');
    }

    console.log('Removing file metadata in dry-run mode...\n');

    // Get original metadata
    const stats = fs.statSync(testFile);
    console.log('Original file metadata:');
    console.log('  - Access time:', stats.atime);
    console.log('  - Modify time:', stats.mtime);
    console.log('  - Size:', stats.size);

    // Remove metadata
    await handler.removeFileMetadata(testFile);

    console.log('\nMetadata removal would reset times to epoch (1970-01-01)');

    // Cleanup
    if (fs.existsSync(testFile)) {
      fs.unlinkSync(testFile);
    }

    handler.stopTracking();
  } catch (error) {
    console.error('Error:', error.message);
  }
}

/**
 * Run all examples
 */
async function runAllExamples() {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║  File Cleanup Handler - Integration Examples               ║');
  console.log('║  Secure File Deletion with Trace Removal                   ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  const examples = [
    example1_CleanTempFiles,
    example2_DetailedReporting,
    example3_CacheCleanup,
    example4_DryRunMode,
    example5_ContextManager,
    example6_ErrorHandling,
    example7_Statistics,
    example8_MetadataRemoval,
  ];

  for (const example of examples) {
    try {
      await example();
    } catch (error) {
      console.error(`Example failed: ${error.message}`);
    }
    console.log('\n' + '═'.repeat(60) + '\n');
  }

  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║  All Examples Completed                                    ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
}

// Run if executed directly
if (require.main === module) {
  runAllExamples().catch(console.error);
}

module.exports = {
  example1_CleanTempFiles,
  example2_DetailedReporting,
  example3_CacheCleanup,
  example4_DryRunMode,
  example5_ContextManager,
  example6_ErrorHandling,
  example7_Statistics,
  example8_MetadataRemoval,
  runAllExamples,
};
