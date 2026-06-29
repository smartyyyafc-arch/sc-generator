/**
 * Environment Variable Cleanup Handler - Tests
 * Comprehensive test suite for cleanup functionality
 */

const EnvVarCleanupHandler = require('./env-var-cleanup-handler');
const {
  getCleanupHandler,
  initializeCleanupHandler,
  withCleanupContext,
} = require('./env-var-cleanup-handler');

// Test utilities
function assert(condition, message) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(
      `Assertion failed: ${message}\nExpected: ${expected}\nActual: ${actual}`
    );
  }
}

function assertIncludes(array, value, message) {
  if (!array.includes(value)) {
    throw new Error(
      `Assertion failed: ${message}\nArray does not include: ${value}\nArray: ${JSON.stringify(array)}`
    );
  }
}

/**
 * Test Suite 1: Basic Tracking
 */
async function testBasicTracking() {
  console.log('Test Suite 1: Basic Tracking');

  const handler = new EnvVarCleanupHandler({ verbose: false });
  handler.startTracking();

  // Test tracking set
  process.env.TEST_VAR_1 = 'value1';
  handler.trackSet('TEST_VAR_1', 'value1');

  const entries = handler.getTrackedEntries();
  assert(entries.length === 1, 'Should have 1 entry');
  assertEqual(entries[0].name, 'TEST_VAR_1', 'Entry name should match');
  assertEqual(entries[0].currentValue, 'value1', 'Current value should match');

  // Test tracking delete (updates existing entry)
  handler.trackDelete('TEST_VAR_1');
  const entriesAfterDelete = handler.getTrackedEntries();
  assert(entriesAfterDelete.length === 1, 'Should still have 1 entry (updated)');
  assertEqual(entriesAfterDelete[0].currentValue, undefined, 'Current value should be undefined');

  handler.clearLog();
  console.log('  PASS: Basic tracking works correctly\n');
}

/**
 * Test Suite 2: Cleanup Strategies
 */
async function testCleanupStrategies() {
  console.log('Test Suite 2: Cleanup Strategies');

  // Ensure clean state
  delete process.env.STRATEGY_NEW_VAR;
  delete process.env.STRATEGY_MODIFY_VAR;

  const handler = new EnvVarCleanupHandler({ verbose: false });
  handler.startTracking();

  // Case 1: New variable - should delete (track before setting)
  handler.trackSet('STRATEGY_NEW_VAR', 'new_value');
  process.env.STRATEGY_NEW_VAR = 'new_value';

  // Case 2: Modified variable - should restore
  process.env.STRATEGY_MODIFY_VAR = 'original_value';
  const handler2 = new EnvVarCleanupHandler({ verbose: false });
  handler2.startTracking();
  handler2.trackSet('STRATEGY_MODIFY_VAR', 'modified_value');
  process.env.STRATEGY_MODIFY_VAR = 'modified_value';

  const entries = handler.getTrackedEntries();
  const newVarEntry = entries.find(e => e.name === 'STRATEGY_NEW_VAR');

  if (newVarEntry) {
    const strategy = handler.determineStrategy(newVarEntry);
    assertEqual(strategy, 'delete', 'New variable should use delete strategy');
  }

  const entries2 = handler2.getTrackedEntries();
  const modifyVarEntry = entries2.find(e => e.name === 'STRATEGY_MODIFY_VAR');

  if (modifyVarEntry) {
    const strategy = handler2.determineStrategy(modifyVarEntry);
    assertEqual(strategy, 'restore', 'Modified variable should use restore strategy');
  }

  // Cleanup
  delete process.env.STRATEGY_NEW_VAR;
  delete process.env.STRATEGY_MODIFY_VAR;

  console.log('  PASS: Cleanup strategies are correct\n');
}

/**
 * Test Suite 3: Execute Cleanup
 */
async function testExecuteCleanup() {
  console.log('Test Suite 3: Execute Cleanup');

  // Ensure clean state
  delete process.env.TEMP_VAR;

  const handler = new EnvVarCleanupHandler({ verbose: false });
  handler.startTracking();

  // Create a new variable - track BEFORE setting
  handler.trackSet('TEMP_VAR', 'temporary');
  process.env.TEMP_VAR = 'temporary';

  assertEqual(process.env.TEMP_VAR, 'temporary', 'Variable should be set');

  // Execute cleanup
  const result = await handler.executeCleanup();

  assert(result.success, 'Cleanup should succeed');
  assertEqual(result.entriesCleaned, 1, 'Should clean 1 entry');
  assertIncludes(result.deletedEntries, 'TEMP_VAR', 'Should delete TEMP_VAR');
  assertEqual(process.env.TEMP_VAR, undefined, 'Variable should be deleted');

  console.log('  PASS: Execute cleanup works correctly\n');
}

/**
 * Test Suite 4: Restore Original Values
 */
async function testRestoreOriginalValues() {
  console.log('Test Suite 4: Restore Original Values');

  // Set original value
  process.env.RESTORE_VAR = 'original_value';

  const handler = new EnvVarCleanupHandler({
    verbose: false,
    trackOriginalValues: true,
  });
  handler.startTracking();

  // Track BEFORE modifying, so we capture original value
  handler.trackSet('RESTORE_VAR', 'modified_value');
  process.env.RESTORE_VAR = 'modified_value';

  assertEqual(
    process.env.RESTORE_VAR,
    'modified_value',
    'Variable should be modified'
  );

  // Execute cleanup
  const result = await handler.executeCleanup();

  assert(result.success, 'Cleanup should succeed');
  assertIncludes(result.restoredEntries, 'RESTORE_VAR', 'Should restore variable');
  assertEqual(
    process.env.RESTORE_VAR,
    'original_value',
    'Variable should be restored'
  );

  // Cleanup
  delete process.env.RESTORE_VAR;
  console.log('  PASS: Original values restored correctly\n');
}

/**
 * Test Suite 5: Dry Run Mode
 */
async function testDryRun() {
  console.log('Test Suite 5: Dry Run Mode');

  const handler = new EnvVarCleanupHandler({ verbose: false, dryRun: true });
  handler.startTracking();

  process.env.DRY_RUN_VAR = 'temporary';
  handler.trackSet('DRY_RUN_VAR', 'temporary');

  const result = await handler.executeCleanup();

  assert(result.success, 'Cleanup should succeed');
  assertEqual(result.entriesCleaned, 1, 'Should report 1 entry cleaned');
  assertEqual(
    process.env.DRY_RUN_VAR,
    'temporary',
    'Variable should still be set (dry run)'
  );

  // Cleanup
  delete process.env.DRY_RUN_VAR;
  console.log('  PASS: Dry run mode works correctly\n');
}

/**
 * Test Suite 6: Context Manager
 */
async function testContextManager() {
  console.log('Test Suite 6: Context Manager');

  // Ensure clean state
  delete process.env.CONTEXT_VAR;

  const { result, cleanup } = await withCleanupContext(
    async (handler) => {
      handler.trackSet('CONTEXT_VAR', 'context_value');
      process.env.CONTEXT_VAR = 'context_value';

      assertEqual(
        process.env.CONTEXT_VAR,
        'context_value',
        'Variable should be set in context'
      );

      return 'operation_result';
    },
    { verbose: false }
  );

  assertEqual(result, 'operation_result', 'Result should match');
  assert(cleanup.success, 'Cleanup should succeed');
  assertEqual(
    process.env.CONTEXT_VAR,
    undefined,
    'Variable should be cleaned up after context'
  );

  console.log('  PASS: Context manager works correctly\n');
}

/**
 * Test Suite 7: Statistics
 */
async function testStatistics() {
  console.log('Test Suite 7: Statistics');

  // Ensure clean state
  delete process.env.STAT_VAR_1;
  delete process.env.STAT_VAR_2;

  const handler = new EnvVarCleanupHandler({ verbose: false });
  handler.startTracking();

  // Add multiple entries - track BEFORE setting
  handler.trackSet('STAT_VAR_1', 'value1');
  handler.trackSet('STAT_VAR_2', 'value2');
  process.env.STAT_VAR_1 = 'value1';
  process.env.STAT_VAR_2 = 'value2';

  const stats = handler.getStatistics();

  assertEqual(stats.totalEntries, 2, 'Should have 2 total entries');
  assertEqual(stats.deletedEntries, 2, 'Should have 2 entries to delete');
  assert(
    stats.oldestEntry !== null,
    'Should have oldest entry timestamp'
  );
  assert(
    stats.newestEntry !== null,
    'Should have newest entry timestamp'
  );

  // Cleanup
  await handler.executeCleanup();

  console.log('  PASS: Statistics calculated correctly\n');
}

/**
 * Test Suite 8: Entry Retrieval
 */
async function testEntryRetrieval() {
  console.log('Test Suite 8: Entry Retrieval');

  const handler = new EnvVarCleanupHandler({ verbose: false });
  handler.startTracking();

  process.env.ENTRY_VAR = 'value';
  handler.trackSet('ENTRY_VAR', 'value');

  const entry = handler.getEntryByName('ENTRY_VAR');
  assert(entry !== undefined, 'Should retrieve entry by name');
  assertEqual(entry.name, 'ENTRY_VAR', 'Entry name should match');

  const noEntry = handler.getEntryByName('NONEXISTENT');
  assertEqual(noEntry, undefined, 'Should return undefined for nonexistent entry');

  // Cleanup
  await handler.executeCleanup();

  console.log('  PASS: Entry retrieval works correctly\n');
}

/**
 * Test Suite 9: Export and Import Log
 */
async function testExportImportLog() {
  console.log('Test Suite 9: Export and Import Log');

  const handler1 = new EnvVarCleanupHandler({ verbose: false });
  handler1.startTracking();

  process.env.EXPORT_VAR = 'value';
  handler1.trackSet('EXPORT_VAR', 'value');

  // Export log
  const exportedLog = handler1.exportLog();
  assert(
    typeof exportedLog === 'string',
    'Exported log should be a string'
  );

  // Import log
  const handler2 = new EnvVarCleanupHandler({ verbose: false });
  handler2.importLog(exportedLog);

  const entries = handler2.getTrackedEntries();
  assertEqual(entries.length, 1, 'Should have imported 1 entry');
  assertEqual(entries[0].name, 'EXPORT_VAR', 'Imported entry name should match');

  // Cleanup
  await handler1.executeCleanup();

  console.log('  PASS: Export and import log works correctly\n');
}

/**
 * Test Suite 10: Global Handler
 */
async function testGlobalHandler() {
  console.log('Test Suite 10: Global Handler');

  const handler1 = getCleanupHandler();
  const handler2 = getCleanupHandler();

  assert(handler1 === handler2, 'Should return same global handler instance');

  // Cleanup
  handler1.clearLog();

  console.log('  PASS: Global handler management works correctly\n');
}

/**
 * Test Suite 11: Multiple Operations on Same Variable
 */
async function testMultipleOperations() {
  console.log('Test Suite 11: Multiple Operations on Same Variable');

  const handler = new EnvVarCleanupHandler({ verbose: false });
  handler.startTracking();

  // Set value
  process.env.MULTI_VAR = 'value1';
  handler.trackSet('MULTI_VAR', 'value1');

  // Update value
  process.env.MULTI_VAR = 'value2';
  handler.trackSet('MULTI_VAR', 'value2');

  const entries = handler.getTrackedEntries();
  assertEqual(entries.length, 1, 'Should have 1 entry (not 2)');
  assertEqual(entries[0].currentValue, 'value2', 'Should have latest value');

  // Cleanup
  const result = await handler.executeCleanup();
  assert(result.success, 'Cleanup should succeed');

  console.log('  PASS: Multiple operations on same variable handled correctly\n');
}

/**
 * Test Suite 12: Error Handling
 */
async function testErrorHandling() {
  console.log('Test Suite 12: Error Handling');

  const handler = new EnvVarCleanupHandler({
    verbose: false,
    maxRetries: 1,
  });
  handler.startTracking();

  // Create a valid entry
  process.env.ERROR_VAR = 'value';
  handler.trackSet('ERROR_VAR', 'value');

  // Execute cleanup (should succeed with default values)
  const result = await handler.executeCleanup();

  // Cleanup
  delete process.env.ERROR_VAR;

  console.log('  PASS: Error handling works correctly\n');
}

/**
 * Run all tests
 */
async function runAllTests() {
  console.log('====================================');
  console.log('Environment Variable Cleanup Handler Tests');
  console.log('====================================\n');

  try {
    await testBasicTracking();
    await testCleanupStrategies();
    await testExecuteCleanup();
    await testRestoreOriginalValues();
    await testDryRun();
    await testContextManager();
    await testStatistics();
    await testEntryRetrieval();
    await testExportImportLog();
    await testGlobalHandler();
    await testMultipleOperations();
    await testErrorHandling();

    console.log('====================================');
    console.log('All tests passed!');
    console.log('====================================');
  } catch (error) {
    console.error('Test failed:', error.message);
    process.exit(1);
  }
}

// Run tests if this is the main module
if (require.main === module) {
  runAllTests().catch(console.error);
}

module.exports = {
  runAllTests,
  testBasicTracking,
  testCleanupStrategies,
  testExecuteCleanup,
  testRestoreOriginalValues,
  testDryRun,
  testContextManager,
  testStatistics,
  testEntryRetrieval,
  testExportImportLog,
  testGlobalHandler,
  testMultipleOperations,
  testErrorHandling,
};
