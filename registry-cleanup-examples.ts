/**
 * Registry Cleanup Handler - Usage Examples
 * Demonstrates cleanup functionality with various patterns
 */

import {
  RegistryCleanupHandler,
  initializeCleanupHandler,
  getCleanupHandler,
  withCleanupContext,
  withAutoCleanup,
  CleanupResult,
} from './registry-cleanup-handler';
import {
  MultiHiveRegistryManager,
  SoftwareHiveStorage,
  RegistryHive,
} from './registry-storage-variants';

/**
 * Example 1: Basic cleanup tracking
 */
async function exampleBasicCleanup() {
  console.log('\n=== Example 1: Basic Cleanup Tracking ===');

  const handler = new RegistryCleanupHandler({ verbose: true });
  handler.startTracking();

  const storage = new SoftwareHiveStorage('MyApp');

  // Simulate writes
  handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TestKey1', null);
  handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TestKey2', 'OldValue');
  handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TestKey3', 'ConfigData');

  console.log('Tracked entries:', handler.getTrackedEntries().length);

  // Execute cleanup
  const result = await handler.executeCleanup();
  console.log('Cleanup result:', {
    success: result.success,
    cleaned: result.entriesCleaned,
    time: result.totalTime,
  });
}

/**
 * Example 2: Cleanup with dry run
 */
async function exampleDryRunCleanup() {
  console.log('\n=== Example 2: Dry Run Cleanup ===');

  const handler = new RegistryCleanupHandler({
    verbose: true,
    dryRun: true, // No actual cleanup
  });

  handler.startTracking();
  handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TestKey1');
  handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'UserPref');
  handler.addEntry(RegistryHive.CURRENT_VERSION, 'VersionInfo');

  console.log('Total entries to clean:', handler.getTrackedEntries().length);

  const result = await handler.executeCleanup();
  console.log('Dry run completed:', {
    entriesWouldbeCleaned: result.entriesCleaned,
    success: result.success,
  });
}

/**
 * Example 3: Multi-hive cleanup
 */
async function exampleMultiHiveCleanup() {
  console.log('\n=== Example 3: Multi-Hive Cleanup ===');

  const handler = new RegistryCleanupHandler({ verbose: true });
  handler.startTracking();

  // Add entries from different hives
  handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'GlobalSetting', 'GlobalValue');
  handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'UserSetting', 'UserValue');
  handler.addEntry(RegistryHive.CURRENT_VERSION, 'VersionSetting', 'VersionValue');
  handler.addEntry(RegistryHive.HKLM_SYSTEM, 'SystemSetting', 'SystemValue');

  // Get statistics
  const stats = handler.getStatistics();
  console.log('Cleanup statistics:', {
    total: stats.totalEntries,
    byHive: stats.entriesByHive,
  });

  // Cleanup specific hive
  const result = await handler.cleanupHive(RegistryHive.HKLM_SOFTWARE);
  console.log('Software hive cleanup:', {
    cleaned: result.entriesCleaned,
    success: result.success,
  });

  // Cleanup remaining hives
  const finalResult = await handler.executeCleanup();
  console.log('Final cleanup:', {
    totalCleaned: finalResult.entriesCleaned,
    success: finalResult.success,
  });
}

/**
 * Example 4: Context manager pattern
 */
async function exampleContextManager() {
  console.log('\n=== Example 4: Context Manager Pattern ===');

  const { result, cleanup } = await withCleanupContext(
    async (handler) => {
      console.log('Executing operation with auto-cleanup...');

      // Add some entries
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TempKey1', null);
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TempKey2', 'OriginalValue');

      // Simulate operation
      const operationResult = 'Operation successful';

      return operationResult;
    },
    { verbose: true }
  );

  console.log('Operation result:', result);
  console.log('Cleanup result:', {
    cleaned: cleanup.entriesCleaned,
    success: cleanup.success,
    time: cleanup.totalTime,
  });
}

/**
 * Example 5: Tracking with original value restoration
 */
async function exampleValueRestoration() {
  console.log('\n=== Example 5: Value Restoration ===');

  const handler = new RegistryCleanupHandler({
    verbose: true,
    trackOriginalValues: true,
    dryRun: true, // Using dry run for safety
  });

  handler.startTracking();

  // These entries have original values that will be restored
  handler.addEntry(
    RegistryHive.HKLM_SOFTWARE,
    'AppVersion',
    '1.0.0'
  );
  handler.addEntry(
    RegistryHive.HKLM_SOFTWARE,
    'LastRunTime',
    '2024-01-01T00:00:00Z'
  );
  handler.addEntry(
    RegistryHive.HKLM_SOFTWARE,
    'UserCount',
    '42'
  );

  // These entries have no original values and will be deleted
  handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'NewTempKey');
  handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'SessionData');

  const entries = handler.getTrackedEntries();
  console.log('Entries to restore:');
  for (const entry of entries) {
    if (entry.originalValue !== undefined) {
      console.log(`  - Restore ${entry.key} to: ${entry.originalValue}`);
    } else {
      console.log(`  - Delete ${entry.key} (newly created)`);
    }
  }

  const result = await handler.restoreAll();
  console.log('Restoration complete:', {
    restored: result.entriesCleaned,
    time: result.totalTime,
  });
}

/**
 * Example 6: Cleanup log export/import
 */
async function exampleLogExportImport() {
  console.log('\n=== Example 6: Log Export/Import ===');

  const handler1 = new RegistryCleanupHandler({ verbose: true });

  handler1.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1', 'Value1');
  handler1.addEntry(RegistryHive.HKEY_CURRENT_USER, 'Key2', 'Value2');

  // Export log
  const exported = handler1.exportLog();
  console.log('Exported log:');
  console.log(exported);

  // Create new handler and import
  const handler2 = new RegistryCleanupHandler({ verbose: true });
  handler2.importLog(exported);

  const importedEntries = handler2.getTrackedEntries();
  console.log('Imported entries:', importedEntries.length);
}

/**
 * Example 7: Multi-hive operation with cleanup
 */
async function exampleMultiHiveOperation() {
  console.log('\n=== Example 7: Multi-Hive Operation with Cleanup ===');

  const { result, cleanup } = await withCleanupContext(
    async (handler) => {
      const manager = new MultiHiveRegistryManager('TestApp');
      const storages = manager.getStorages();

      // Simulate writing to all hives
      for (const [hiveName, storage] of Object.entries(storages)) {
        try {
          // Track the write
          const hiveKey = Object.entries(RegistryHive).find(
            ([, value]) =>
              value.includes(storage.hive)
          )?.[1] as RegistryHive;

          if (hiveKey) {
            handler.addEntry(hiveKey, `WriteKey_${hiveName}`, null);
          }
        } catch (error) {
          console.error(`Error in ${hiveName}:`, error);
        }
      }

      return { hivesModified: Object.keys(storages).length };
    },
    { verbose: true, dryRun: true }
  );

  console.log('Operation result:', result);
  console.log('Cleanup stats:', {
    entriesCleaned: cleanup.entriesCleaned,
    success: cleanup.success,
  });
}

/**
 * Example 8: Global cleanup handler
 */
async function exampleGlobalHandler() {
  console.log('\n=== Example 8: Global Cleanup Handler ===');

  // Initialize global handler
  const handler = initializeCleanupHandler({ verbose: true });

  handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'GlobalKey1');
  handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'GlobalKey2', 'OriginalValue');

  console.log('Global handler entries:', handler.getTrackedEntries().length);

  // Later, get the same global instance
  const sameHandler = getCleanupHandler();
  console.log('Same handler instance:', handler === sameHandler);

  const result = await sameHandler.executeCleanup();
  console.log('Cleanup result:', {
    cleaned: result.entriesCleaned,
    success: result.success,
  });
}

/**
 * Example 9: Error handling and failed entries
 */
async function exampleErrorHandling() {
  console.log('\n=== Example 9: Error Handling ===');

  const handler = new RegistryCleanupHandler({
    verbose: true,
    maxRetries: 2, // Limited retries for demo
  });

  handler.startTracking();

  // Add entries that might fail
  handler.addEntry(
    RegistryHive.HKLM_SOFTWARE,
    'NormalKey',
    'NormalValue'
  );
  handler.addEntry(
    RegistryHive.HKLM_SYSTEM,
    'ProtectedSystemKey',
    null
  );

  const result = await handler.executeCleanup();

  console.log('Cleanup result:', {
    success: result.success,
    cleaned: result.entriesCleaned,
    failed: result.failedEntries.length,
    errors: result.errors,
  });

  if (result.failedEntries.length > 0) {
    console.log('Failed entries:');
    for (const entry of result.failedEntries) {
      console.log(`  - ${entry.hive}\\${entry.key}`);
    }
  }
}

/**
 * Example 10: Cleanup by hive
 */
async function exampleCleanupByHive() {
  console.log('\n=== Example 10: Cleanup by Hive ===');

  const handler = new RegistryCleanupHandler({ verbose: true, dryRun: true });

  // Add entries from multiple hives
  handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'SoftKey1');
  handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'SoftKey2');
  handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'UserKey1');
  handler.addEntry(RegistryHive.CURRENT_VERSION, 'VersionKey1');

  console.log('Initial entries:', handler.getTrackedEntries().length);

  // Cleanup specific hive
  const softwareResult = await handler.cleanupHive(RegistryHive.HKLM_SOFTWARE);
  console.log('Software hive cleanup:', {
    cleaned: softwareResult.entriesCleaned,
  });

  console.log('Remaining entries:', handler.getTrackedEntries().length);

  // Cleanup remaining
  const finalResult = await handler.executeCleanup();
  console.log('Final cleanup:', {
    cleaned: finalResult.entriesCleaned,
  });
}

/**
 * Run all examples
 */
async function runAllExamples() {
  try {
    await exampleBasicCleanup();
    await exampleDryRunCleanup();
    await exampleMultiHiveCleanup();
    await exampleContextManager();
    await exampleValueRestoration();
    await exampleLogExportImport();
    await exampleMultiHiveOperation();
    await exampleGlobalHandler();
    await exampleErrorHandling();
    await exampleCleanupByHive();

    console.log('\n=== All Examples Complete ===');
  } catch (error) {
    console.error('Example execution error:', error);
  }
}

/**
 * Export examples
 */
export {
  exampleBasicCleanup,
  exampleDryRunCleanup,
  exampleMultiHiveCleanup,
  exampleContextManager,
  exampleValueRestoration,
  exampleLogExportImport,
  exampleMultiHiveOperation,
  exampleGlobalHandler,
  exampleErrorHandling,
  exampleCleanupByHive,
  runAllExamples,
};

// Run examples if this file is executed directly
if (require.main === module) {
  runAllExamples();
}
