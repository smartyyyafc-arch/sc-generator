/**
 * Environment Variable Cleanup Handler - Usage Examples
 * Demonstrates various usage patterns for the cleanup handler
 */

const EnvVarCleanupHandler = require('./env-var-cleanup-handler');
const {
  getCleanupHandler,
  initializeCleanupHandler,
  withCleanupContext,
} = require('./env-var-cleanup-handler');

/**
 * Example 1: Basic Variable Cleanup
 * Shows how to track and clean up a single environment variable
 */
async function example1_basicCleanup() {
  console.log('\n=== Example 1: Basic Variable Cleanup ===\n');

  const handler = new EnvVarCleanupHandler({ verbose: true });
  handler.startTracking();

  console.log('Setting temporary environment variable...');
  process.env.TEMP_API_KEY = 'secret-key-12345';
  handler.trackSet('TEMP_API_KEY', 'secret-key-12345');

  console.log(`Current value: ${process.env.TEMP_API_KEY}`);

  console.log('\nCleaning up environment variables...');
  const result = await handler.executeCleanup();
  handler.stopTracking();

  console.log(`After cleanup: ${process.env.TEMP_API_KEY}`);
  console.log(`Cleanup result:`, {
    success: result.success,
    entriesCleaned: result.entriesCleaned,
    deletedEntries: result.deletedEntries,
  });
}

/**
 * Example 2: Restoring Original Values
 * Shows how to modify an existing variable and restore it
 */
async function example2_restoreOriginal() {
  console.log('\n=== Example 2: Restoring Original Values ===\n');

  // Start with a known original value
  process.env.CONFIG_ENV = 'production';
  console.log(`Original CONFIG_ENV: ${process.env.CONFIG_ENV}`);

  const handler = new EnvVarCleanupHandler({
    verbose: true,
    trackOriginalValues: true,
  });
  handler.startTracking();

  console.log('\nChanging environment for testing...');
  process.env.CONFIG_ENV = 'test';
  handler.trackSet('CONFIG_ENV', 'test');
  console.log(`Modified CONFIG_ENV: ${process.env.CONFIG_ENV}`);

  console.log('\nCleaning up - restoring original value...');
  const result = await handler.executeCleanup();
  handler.stopTracking();

  console.log(`Restored CONFIG_ENV: ${process.env.CONFIG_ENV}`);
  console.log(`Cleanup result:`, {
    success: result.success,
    restoredEntries: result.restoredEntries,
  });

  // Cleanup
  delete process.env.CONFIG_ENV;
}

/**
 * Example 3: Dry Run Mode
 * Shows how to preview cleanup without actually modifying environment
 */
async function example3_dryRun() {
  console.log('\n=== Example 3: Dry Run Mode ===\n');

  const handler = new EnvVarCleanupHandler({
    verbose: true,
    dryRun: true, // Enable dry run
  });
  handler.startTracking();

  console.log('Setting multiple temporary variables...');
  process.env.TEMP_VAR_1 = 'value1';
  process.env.TEMP_VAR_2 = 'value2';
  process.env.TEMP_VAR_3 = 'value3';

  handler.trackSet('TEMP_VAR_1', 'value1');
  handler.trackSet('TEMP_VAR_2', 'value2');
  handler.trackSet('TEMP_VAR_3', 'value3');

  console.log('\nRunning cleanup in DRY RUN mode...');
  const result = await handler.executeCleanup();

  console.log('\nVariables after dry run cleanup:');
  console.log(`  TEMP_VAR_1: ${process.env.TEMP_VAR_1}`);
  console.log(`  TEMP_VAR_2: ${process.env.TEMP_VAR_2}`);
  console.log(`  TEMP_VAR_3: ${process.env.TEMP_VAR_3}`);
  console.log('(Variables are still set because of dry run mode)');

  // Cleanup
  delete process.env.TEMP_VAR_1;
  delete process.env.TEMP_VAR_2;
  delete process.env.TEMP_VAR_3;
}

/**
 * Example 4: Context Manager Pattern
 * Shows how to use the context manager for automatic cleanup
 */
async function example4_contextManager() {
  console.log('\n=== Example 4: Context Manager Pattern ===\n');

  console.log('Before context:');
  console.log(`  CONTEXT_DB_URL: ${process.env.CONTEXT_DB_URL}`);

  const { result, cleanup } = await withCleanupContext(
    async (handler) => {
      console.log('\nInside context:');
      process.env.CONTEXT_DB_URL = 'postgresql://test:test@localhost/testdb';
      handler.trackSet('CONTEXT_DB_URL', 'postgresql://test:test@localhost/testdb');
      console.log(`  CONTEXT_DB_URL: ${process.env.CONTEXT_DB_URL}`);

      // Simulate some async work
      console.log('\nPerforming database operations...');
      await new Promise(resolve => setTimeout(resolve, 100));

      return 'db_operation_complete';
    },
    { verbose: false }
  );

  console.log('\nAfter context:');
  console.log(`  CONTEXT_DB_URL: ${process.env.CONTEXT_DB_URL}`);
  console.log(`  Operation result: ${result}`);
  console.log(`  Cleanup successful: ${cleanup.success}`);
}

/**
 * Example 5: Multiple Variable Tracking
 * Shows how to track multiple variables with different strategies
 */
async function example5_multipleVariables() {
  console.log('\n=== Example 5: Multiple Variable Tracking ===\n');

  // Set original values for some variables
  process.env.EXISTING_VAR = 'original_value';

  const handler = new EnvVarCleanupHandler({
    verbose: true,
    trackOriginalValues: true,
  });
  handler.startTracking();

  console.log('Setting up variables...');
  process.env.NEW_VAR = 'new_value';
  process.env.EXISTING_VAR = 'modified_value';
  process.env.ANOTHER_NEW = 'another_value';

  handler.trackSet('NEW_VAR', 'new_value');
  handler.trackSet('EXISTING_VAR', 'modified_value');
  handler.trackSet('ANOTHER_NEW', 'another_value');

  const stats = handler.getStatistics();
  console.log('\nTracking statistics:');
  console.log(`  Total entries: ${stats.totalEntries}`);
  console.log(`  To be restored: ${stats.restoredEntries}`);
  console.log(`  To be deleted: ${stats.deletedEntries}`);

  console.log('\nExecuting cleanup...');
  const result = await handler.executeCleanup();
  handler.stopTracking();

  console.log('\nAfter cleanup:');
  console.log(`  NEW_VAR: ${process.env.NEW_VAR}`);
  console.log(`  EXISTING_VAR: ${process.env.EXISTING_VAR}`);
  console.log(`  ANOTHER_NEW: ${process.env.ANOTHER_NEW}`);

  // Cleanup
  delete process.env.EXISTING_VAR;
}

/**
 * Example 6: Global Handler
 * Shows how to use the global handler instance
 */
async function example6_globalHandler() {
  console.log('\n=== Example 6: Global Handler ===\n');

  console.log('Getting global cleanup handler...');
  const handler = getCleanupHandler();

  handler.startTracking();
  console.log('Tracking started on global handler');

  process.env.GLOBAL_VAR_1 = 'value1';
  process.env.GLOBAL_VAR_2 = 'value2';

  handler.trackSet('GLOBAL_VAR_1', 'value1');
  handler.trackSet('GLOBAL_VAR_2', 'value2');

  console.log(`\nGlobal handler has ${handler.getTrackedEntries().length} entries`);

  console.log('\nExecuting cleanup...');
  const result = await handler.executeCleanup();

  console.log(`Cleanup successful: ${result.success}`);
  console.log(`Entries cleaned: ${result.entriesCleaned}`);

  handler.stopTracking();
}

/**
 * Example 7: Export and Import
 * Shows how to export and import cleanup logs
 */
async function example7_exportImport() {
  console.log('\n=== Example 7: Export and Import ===\n');

  // Create first handler and log some entries
  const handler1 = new EnvVarCleanupHandler({ verbose: false });
  handler1.startTracking();

  process.env.EXPORT_VAR_1 = 'value1';
  process.env.EXPORT_VAR_2 = 'value2';
  handler1.trackSet('EXPORT_VAR_1', 'value1');
  handler1.trackSet('EXPORT_VAR_2', 'value2');

  console.log('Handler 1 - Exporting cleanup log...');
  const exportedLog = handler1.exportLog();
  console.log(`Exported log size: ${exportedLog.length} characters`);
  console.log(`Exported log (first 200 chars): ${exportedLog.substring(0, 200)}...`);

  // Create second handler and import the log
  const handler2 = new EnvVarCleanupHandler({ verbose: false });
  console.log('\nHandler 2 - Importing cleanup log...');
  handler2.importLog(exportedLog);

  const entries = handler2.getTrackedEntries();
  console.log(`Imported ${entries.length} entries:`);
  entries.forEach(entry => {
    console.log(`  - ${entry.name}: ${entry.currentValue}`);
  });

  // Cleanup
  delete process.env.EXPORT_VAR_1;
  delete process.env.EXPORT_VAR_2;
}

/**
 * Example 8: Statistics and Reporting
 * Shows how to generate statistics about cleanup operations
 */
async function example8_statistics() {
  console.log('\n=== Example 8: Statistics and Reporting ===\n');

  // Set original values
  process.env.STAT_EXISTING = 'original';

  const handler = new EnvVarCleanupHandler({
    verbose: false,
    trackOriginalValues: true,
  });
  handler.startTracking();

  // Create scenario
  process.env.STAT_NEW_1 = 'new_value_1';
  process.env.STAT_NEW_2 = 'new_value_2';
  process.env.STAT_EXISTING = 'modified';

  handler.trackSet('STAT_NEW_1', 'new_value_1');
  handler.trackSet('STAT_NEW_2', 'new_value_2');
  handler.trackSet('STAT_EXISTING', 'modified');

  // Get statistics before cleanup
  console.log('Statistics before cleanup:');
  const statsBefore = handler.getStatistics();
  console.log(JSON.stringify(statsBefore, null, 2));

  // Execute cleanup
  const result = await handler.executeCleanup();

  // Get statistics after cleanup
  console.log('\nCleanup result:');
  console.log(JSON.stringify(result, null, 2));

  // Cleanup
  delete process.env.STAT_EXISTING;
}

/**
 * Example 9: Error Recovery
 * Shows how the handler handles and reports errors
 */
async function example9_errorRecovery() {
  console.log('\n=== Example 9: Error Recovery ===\n');

  const handler = new EnvVarCleanupHandler({
    verbose: true,
    maxRetries: 2,
    retryDelayMs: 50,
  });
  handler.startTracking();

  process.env.NORMAL_VAR = 'value';
  handler.trackSet('NORMAL_VAR', 'value');

  console.log('\nExecuting cleanup with normal variable...');
  const result = await handler.executeCleanup();

  console.log('\nCleanup result:');
  console.log(`  Success: ${result.success}`);
  console.log(`  Entries cleaned: ${result.entriesCleaned}`);
  console.log(`  Failed entries: ${result.failedEntries.length}`);
  console.log(`  Errors: ${result.errors.length}`);

  if (result.errors.length > 0) {
    console.log('\nErrors encountered:');
    result.errors.forEach(error => console.log(`  - ${error}`));
  }
}

/**
 * Example 10: Advanced Workflow
 * Shows a complete workflow combining multiple features
 */
async function example10_advancedWorkflow() {
  console.log('\n=== Example 10: Advanced Workflow ===\n');

  console.log('Step 1: Initialize handler with options');
  const handler = new EnvVarCleanupHandler({
    verbose: true,
    trackOriginalValues: true,
    dryRun: false,
  });
  handler.startTracking();

  console.log('\nStep 2: Setup original environment');
  process.env.APP_ENV = 'production';
  process.env.LOG_LEVEL = 'error';

  console.log('\nStep 3: Simulate application startup (modify environment)');
  const { result, cleanup } = await withCleanupContext(
    async (ctx) => {
      process.env.APP_ENV = 'development';
      process.env.LOG_LEVEL = 'debug';
      process.env.DEBUG_MODE = 'true';

      ctx.trackSet('APP_ENV', 'development');
      ctx.trackSet('LOG_LEVEL', 'debug');
      ctx.trackSet('DEBUG_MODE', 'true');

      console.log('  APP_ENV:', process.env.APP_ENV);
      console.log('  LOG_LEVEL:', process.env.LOG_LEVEL);
      console.log('  DEBUG_MODE:', process.env.DEBUG_MODE);

      console.log('\nStep 4: Perform operations');
      await new Promise(resolve => setTimeout(resolve, 100));

      return 'application_execution_complete';
    },
    { verbose: false }
  );

  console.log('\nStep 5: Environment after cleanup');
  console.log('  APP_ENV:', process.env.APP_ENV);
  console.log('  LOG_LEVEL:', process.env.LOG_LEVEL);
  console.log('  DEBUG_MODE:', process.env.DEBUG_MODE);

  console.log('\nStep 6: Summary');
  console.log(`  Operation result: ${result}`);
  console.log(`  Cleanup successful: ${cleanup.success}`);
  console.log(`  Restored: ${cleanup.restoredEntries.join(', ')}`);
  console.log(`  Deleted: ${cleanup.deletedEntries.join(', ')}`);

  // Cleanup
  delete process.env.APP_ENV;
  delete process.env.LOG_LEVEL;
}

/**
 * Run all examples
 */
async function runAllExamples() {
  console.log('========================================');
  console.log('Environment Variable Cleanup Handler');
  console.log('Usage Examples');
  console.log('========================================');

  try {
    await example1_basicCleanup();
    await example2_restoreOriginal();
    await example3_dryRun();
    await example4_contextManager();
    await example5_multipleVariables();
    await example6_globalHandler();
    await example7_exportImport();
    await example8_statistics();
    await example9_errorRecovery();
    await example10_advancedWorkflow();

    console.log('\n========================================');
    console.log('All examples completed!');
    console.log('========================================');
  } catch (error) {
    console.error('Error running examples:', error);
    process.exit(1);
  }
}

// Run examples if this is the main module
if (require.main === module) {
  runAllExamples().catch(console.error);
}

module.exports = {
  example1_basicCleanup,
  example2_restoreOriginal,
  example3_dryRun,
  example4_contextManager,
  example5_multipleVariables,
  example6_globalHandler,
  example7_exportImport,
  example8_statistics,
  example9_errorRecovery,
  example10_advancedWorkflow,
  runAllExamples,
};
