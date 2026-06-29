/**
 * Post-Installation Cleanup Handler - Usage Examples
 *
 * Comprehensive examples demonstrating:
 * 1. Basic installer removal
 * 2. History clearing workflows
 * 3. Complete post-install cleanup
 * 4. Different cleanup profiles
 * 5. Error handling
 * 6. Advanced cleanup patterns
 * 7. Reporting and statistics
 */

const PostInstallCleanupHandler = require('./post-install-cleanup-handler');
const {
  executePostInstallCleanup,
  withCleanupContext,
  initializeCleanupHandler,
} = require('./post-install-cleanup-handler');
const path = require('path');
const os = require('os');

/**
 * Example 1: Basic Installer Removal
 * Remove installer with minimal options
 */
async function example1_BasicInstallerRemoval() {
  console.log('\n=== Example 1: Basic Installer Removal ===\n');

  const handler = new PostInstallCleanupHandler({
    verbose: true,
    dryRun: false, // Actual deletion
    secureDelete: true,
  });

  handler.startTracking();

  // Remove installer file
  const installerPath = '/path/to/installer/setup.exe';
  const removed = await handler.removeInstaller(installerPath);
  console.log(`Installer removed: ${removed}`);

  // Get statistics
  const stats = handler.getStatistics();
  console.log(`Files deleted: ${stats.totalFilesDeleted}`);
  console.log(`Operation successful: ${removed}`);

  handler.stopTracking();
}

/**
 * Example 2: Shell History Clearing
 * Clear various shell history files and command history
 */
async function example2_ShellHistoryClearing() {
  console.log('\n=== Example 2: Shell History Clearing ===\n');

  const handler = new PostInstallCleanupHandler({
    verbose: true,
    dryRun: false,
    clearHistory: true,
    secureDelete: true,
  });

  handler.startTracking();

  // Clear shell history files
  console.log('Clearing shell history files...');
  await handler.clearShellHistory();

  // Clear in-memory command history
  console.log('Clearing in-memory command history...');
  await handler.clearCommandHistory();

  // Get cleared histories
  const clearedHistories = handler.getClearedHistories();
  console.log(`\nCleared history files:`);
  clearedHistories.forEach((file) => {
    console.log(`  - ${file}`);
  });

  const stats = handler.getStatistics();
  console.log(`\nTotal histories cleared: ${stats.totalHistoriesCleared}`);

  handler.stopTracking();
}

/**
 * Example 3: Complete Post-Install Cleanup (Minimal Profile)
 * Remove only installer and logs (minimal cleanup)
 */
async function example3_MinimalCleanup() {
  console.log('\n=== Example 3: Minimal Post-Install Cleanup ===\n');

  const handler = new PostInstallCleanupHandler({
    verbose: true,
    dryRun: false,
    profile: 'minimal', // Only installer and logs
  });

  handler.startTracking();

  // Remove installer
  const installerPath = '/opt/application/installer.sh';
  await handler.removeInstaller(installerPath);

  // Execute cleanup (logs only in minimal profile)
  const result = await handler.executeCleanup();

  // Get summary
  const summary = handler.getSummary();
  console.log(`\nCleanup Summary:`);
  console.log(`  Profile: ${summary.profile}`);
  console.log(`  Description: ${summary.profileDescription}`);
  console.log(`  Files deleted: ${summary.filesDeleted}`);
  console.log(`  Success: ${result.success}`);
  console.log(`  Time elapsed: ${result.totalTime}ms`);

  handler.stopTracking();
}

/**
 * Example 4: Standard Post-Install Cleanup
 * Remove installer, history, logs, and cache
 */
async function example4_StandardCleanup() {
  console.log('\n=== Example 4: Standard Post-Install Cleanup ===\n');

  const handler = new PostInstallCleanupHandler({
    verbose: true,
    dryRun: false,
    profile: 'standard', // Default profile
  });

  handler.startTracking();

  // Remove installer
  const installerPath = '/tmp/app-setup-1.0.exe';
  console.log(`Removing installer: ${installerPath}`);
  await handler.removeInstaller(installerPath);

  // Execute full cleanup
  console.log('\nExecuting standard cleanup...');
  const result = await handler.executeCleanup();

  // Export detailed report
  const report = handler.exportReport();
  console.log(`\nCleanup Report:`);
  console.log(`  Timestamp: ${report.timestamp.toISOString()}`);
  console.log(`  Profile: ${report.profile}`);
  console.log(`  Files deleted: ${report.statistics.totalFilesDeleted}`);
  console.log(`  Histories cleared: ${report.statistics.totalHistoriesCleared}`);
  console.log(`  Operations completed: ${report.statistics.totalOperations}`);
  console.log(`  Success rate: ${(report.statistics.successRate * 100).toFixed(2)}%`);

  handler.stopTracking();
}

/**
 * Example 5: Thorough Post-Install Cleanup
 * Complete cleanup including temp files and forensic traces
 */
async function example5_ThoroughCleanup() {
  console.log('\n=== Example 5: Thorough Post-Install Cleanup ===\n');

  const handler = new PostInstallCleanupHandler({
    verbose: true,
    dryRun: false,
    profile: 'thorough', // Maximum cleanup
    overwritePasses: 3, // DoD standard overwrite
  });

  handler.startTracking();

  // Remove installer directory
  const installerDir = '/opt/installers/app-v2.0';
  console.log(`Removing installer directory: ${installerDir}`);
  await handler.removeInstaller(installerDir);

  // Execute thorough cleanup
  console.log('\nExecuting thorough cleanup...');
  const result = await handler.executeCleanup();

  // Get comprehensive statistics
  const stats = handler.getStatistics();
  console.log(`\nCleanup Statistics:`);
  console.log(`  Security level: ${stats.secureDeleteEnabled ? '3-pass overwrite' : 'Standard deletion'}`);
  console.log(`  Total files deleted: ${stats.totalFilesDeleted}`);
  console.log(`  Total histories cleared: ${stats.totalHistoriesCleared}`);
  console.log(`  Operations failed: ${stats.totalOperationsFailed}`);
  console.log(`  Overall success rate: ${(stats.successRate * 100).toFixed(2)}%`);

  handler.stopTracking();
}

/**
 * Example 6: Dry-Run Mode for Safe Testing
 * Preview cleanup operations without actually deleting
 */
async function example6_DryRunMode() {
  console.log('\n=== Example 6: Dry-Run Mode (Safety Test) ===\n');

  const handler = new PostInstallCleanupHandler({
    verbose: true,
    dryRun: true, // No actual deletion
    profile: 'thorough',
  });

  handler.startTracking();

  // Preview installer removal
  const installerPath = '/tmp/installer.msi';
  console.log(`[DRY RUN] Would remove: ${installerPath}`);
  await handler.removeInstaller(installerPath);

  // Preview full cleanup
  console.log('\n[DRY RUN] Executing cleanup preview...');
  const result = await handler.executeCleanup();

  // Show what would be done
  const summary = handler.getSummary();
  console.log(`\n[DRY RUN] Cleanup Preview:`);
  console.log(`  Profile: ${summary.profile}`);
  console.log(`  Files would be deleted: ${summary.filesDeleted}`);
  console.log(`  Histories would be cleared: ${summary.historiesCleared}`);
  console.log(`  Security level: ${summary.securityLevel}`);
  console.log(`\n[DRY RUN] No actual files were deleted.`);

  handler.stopTracking();
}

/**
 * Example 7: Custom Cleanup Configuration
 * Advanced cleanup with custom options
 */
async function example7_CustomConfiguration() {
  console.log('\n=== Example 7: Custom Cleanup Configuration ===\n');

  const handler = new PostInstallCleanupHandler({
    verbose: true,
    dryRun: false,
    secureDelete: true,
    overwritePasses: 7, // High-security overwrite
    clearHistory: true,
    clearLogs: true,
    clearCache: true,
    clearTemp: true,
    clearRecycleBin: true,
    maxRetries: 5, // More resilient
    retryDelayMs: 200, // Longer delay between retries
    homeDir: os.homedir(), // Use actual home directory
    tempDir: os.tmpdir(), // Use actual temp directory
  });

  handler.startTracking();

  // Remove installer with custom options
  const installerPath = '/home/user/app-installer.bin';
  console.log(`Removing installer with custom security settings...`);
  await handler.removeInstaller(installerPath);

  // Execute cleanup with custom configuration
  console.log(`\nExecuting cleanup with custom configuration...`);
  const result = await handler.executeCleanup();

  // Show detailed configuration in report
  const report = handler.exportReport();
  console.log(`\nCustom Configuration Applied:`);
  console.log(`  Secure delete: ${report.options.secureDelete}`);
  console.log(`  Overwrite passes: ${report.options.overwritePasses}`);
  console.log(`  Max retries: ${report.options.maxRetries}`);
  console.log(`  Retry delay: ${report.options.retryDelayMs}ms`);

  console.log(`\nCleanup Result:`);
  console.log(`  Success: ${result.success}`);
  console.log(`  Files deleted: ${result.filesDeleted}`);
  console.log(`  Time elapsed: ${result.totalTime}ms`);

  handler.stopTracking();
}

/**
 * Example 8: Error Handling and Recovery
 * Graceful handling of cleanup errors
 */
async function example8_ErrorHandling() {
  console.log('\n=== Example 8: Error Handling and Recovery ===\n');

  const handler = new PostInstallCleanupHandler({
    verbose: true,
    dryRun: false,
    maxRetries: 3,
  });

  handler.startTracking();

  // Try to remove non-existent installer (handled gracefully)
  console.log('Attempting to remove non-existent installer...');
  const nonExistentPath = '/non/existent/installer.exe';
  const result1 = await handler.removeInstaller(nonExistentPath);
  console.log(`Result: ${result1} (non-existent file handled gracefully)`);

  // Execute cleanup even with potential errors
  console.log('\nExecuting cleanup despite potential errors...');
  const result = await handler.executeCleanup();

  // Show any errors that occurred
  if (result.errors.length > 0) {
    console.log(`\nErrors encountered:`);
    result.errors.forEach((error) => {
      console.log(`  - ${error}`);
    });
  } else {
    console.log(`\nNo errors encountered during cleanup.`);
  }

  // Show which operations failed
  const failed = handler.getFailedOperations();
  if (failed.length > 0) {
    console.log(`\nFailed operations: ${failed.length}`);
  }

  handler.stopTracking();
}

/**
 * Example 9: Context Manager Pattern
 * Automatic cleanup with context manager
 */
async function example9_ContextManager() {
  console.log('\n=== Example 9: Context Manager Pattern ===\n');

  const { result, cleanup, summary } = await withCleanupContext(
    async (handler) => {
      console.log('Inside cleanup context...');

      // Perform cleanup operations
      const installerPath = '/tmp/contextual-installer.sh';
      await handler.removeInstaller(installerPath);

      // Do other work
      console.log('Performing post-install operations...');

      return 'post-install operations completed';
    },
    {
      verbose: true,
      dryRun: false,
      profile: 'standard',
    }
  );

  console.log(`\nContext result: ${result}`);
  console.log(`Cleanup executed: ${cleanup.success}`);
  console.log(`Profile used: ${summary.profile}`);
  console.log(`Files deleted: ${summary.filesDeleted}`);
}

/**
 * Example 10: Complete Post-Install Cleanup Helper
 * Convenience function for full post-install cleanup
 */
async function example10_CompletePostInstall() {
  console.log('\n=== Example 10: Complete Post-Install Cleanup Helper ===\n');

  const installerPath = '/tmp/app-installer-v1.0.tar.gz';

  const { result, summary, report } = await executePostInstallCleanup(installerPath, {
    verbose: true,
    dryRun: false,
    profile: 'standard',
  });

  console.log(`\nPost-Install Cleanup Complete:`);
  console.log(`  Profile: ${summary.profile}`);
  console.log(`  Description: ${summary.profileDescription}`);
  console.log(`  Files deleted: ${summary.filesDeleted}`);
  console.log(`  Histories cleared: ${summary.historiesCleared}`);
  console.log(`  Success rate: ${summary.successRate}`);
  console.log(`  Time elapsed: ${result.totalTime}ms`);

  console.log(`\nDetailed Report:`);
  console.log(`  Total operations: ${report.statistics.totalOperations}`);
  console.log(`  Total failures: ${report.statistics.totalOperationsFailed}`);
  console.log(`  Security level: ${report.statistics.secureDeleteEnabled ? 'High' : 'Standard'}`);
}

/**
 * Example 11: Sequential Profile Escalation
 * Start with minimal and escalate to thorough cleanup
 */
async function example11_ProfileEscalation() {
  console.log('\n=== Example 11: Profile Escalation ===\n');

  const profiles = ['minimal', 'standard', 'thorough'];
  const results = [];

  for (const profile of profiles) {
    console.log(`\nExecuting ${profile} cleanup profile...`);

    const handler = new PostInstallCleanupHandler({
      verbose: false,
      dryRun: true, // Dry run for demonstration
      profile,
    });

    handler.startTracking();

    const result = await handler.executeCleanup();
    const summary = handler.getSummary();

    results.push({
      profile: summary.profile,
      description: summary.profileDescription,
      filesDeleted: summary.filesDeleted,
      historiesCleared: summary.historiesCleared,
      success: result.success,
    });

    handler.stopTracking();
  }

  // Show escalation results
  console.log(`\nProfile Escalation Results:`);
  console.log('='.repeat(80));
  results.forEach((r) => {
    console.log(`\n${r.profile}:`);
    console.log(`  ${r.description}`);
    console.log(`  Files would be deleted: ${r.filesDeleted}`);
    console.log(`  Histories would be cleared: ${r.historiesCleared}`);
  });
}

/**
 * Example 12: Global Handler Management
 * Use global handler instance for application-wide cleanup
 */
async function example12_GlobalHandlerManagement() {
  console.log('\n=== Example 12: Global Handler Management ===\n');

  // Initialize global handler
  const handler = initializeCleanupHandler({
    verbose: true,
    dryRun: false,
    profile: 'standard',
  });

  console.log('Global handler initialized');

  // Use handler from anywhere in the application
  await handler.removeInstaller('/tmp/app-setup.exe');
  console.log('Installer removed via global handler');

  // Execute cleanup
  const result = await handler.executeCleanup();
  console.log(`Global cleanup executed: ${result.success}`);

  // Get statistics from global handler
  const stats = handler.getStatistics();
  console.log(`\nGlobal handler statistics:`);
  console.log(`  Total files deleted: ${stats.totalFilesDeleted}`);
  console.log(`  Total operations: ${stats.totalOperations}`);

  handler.stopTracking();
}

/**
 * Example 13: Batch Installer Removal
 * Remove multiple installers from different locations
 */
async function example13_BatchInstallerRemoval() {
  console.log('\n=== Example 13: Batch Installer Removal ===\n');

  const handler = new PostInstallCleanupHandler({
    verbose: true,
    dryRun: false,
    secureDelete: true,
  });

  handler.startTracking();

  const installers = [
    '/opt/app/installer.sh',
    '/tmp/setup.exe',
    '/home/user/Downloads/installer.msi',
    '/var/cache/app-installer',
  ];

  console.log(`Removing ${installers.length} installers...\n`);

  let successCount = 0;
  for (const installer of installers) {
    console.log(`Processing: ${installer}`);
    const removed = await handler.removeInstaller(installer);
    if (removed) successCount++;
    console.log(`  Status: ${removed ? 'Removed' : 'Not found or error'}`);
  }

  console.log(`\nBatch removal complete: ${successCount}/${installers.length} successful`);

  const result = await handler.executeCleanup();
  console.log(`Full cleanup executed: ${result.success}`);

  handler.stopTracking();
}

/**
 * Example 14: Reporting and Audit Trail
 * Generate detailed cleanup audit trail
 */
async function example14_ReportingAndAudit() {
  console.log('\n=== Example 14: Reporting and Audit Trail ===\n');

  const handler = new PostInstallCleanupHandler({
    verbose: false,
    dryRun: false,
    profile: 'standard',
  });

  handler.startTracking();

  // Perform cleanup
  await handler.removeInstaller('/tmp/installer.tar.gz');
  const result = await handler.executeCleanup();

  // Export comprehensive report
  const report = handler.exportReport();

  console.log(`Cleanup Audit Trail:`);
  console.log(`Timestamp: ${report.timestamp.toISOString()}`);
  console.log(`\nStatistics:`);
  console.log(`  Profile: ${report.statistics.profile}`);
  console.log(`  Total operations: ${report.statistics.totalOperations}`);
  console.log(`  Files deleted: ${report.statistics.totalFilesDeleted}`);
  console.log(`  Operations failed: ${report.statistics.totalOperationsFailed}`);
  console.log(`  Success rate: ${(report.statistics.successRate * 100).toFixed(2)}%`);

  console.log(`\nDeleted Files:`);
  report.deletedFiles.forEach((file) => {
    console.log(`  - ${file.filePath}`);
    console.log(`    Deleted at: ${file.deletedAt.toISOString()}`);
    console.log(`    Secure: ${file.secure}`);
  });

  console.log(`\nCleared Histories:`);
  report.clearedHistories.forEach((history) => {
    console.log(`  - ${history}`);
  });

  handler.stopTracking();
}

/**
 * Main execution
 */
async function main() {
  console.log('Post-Installation Cleanup Handler - Usage Examples');
  console.log('='.repeat(80));

  const examples = [
    {
      number: 1,
      name: 'Basic Installer Removal',
      fn: example1_BasicInstallerRemoval,
    },
    {
      number: 2,
      name: 'Shell History Clearing',
      fn: example2_ShellHistoryClearing,
    },
    {
      number: 3,
      name: 'Minimal Post-Install Cleanup',
      fn: example3_MinimalCleanup,
    },
    {
      number: 4,
      name: 'Standard Post-Install Cleanup',
      fn: example4_StandardCleanup,
    },
    {
      number: 5,
      name: 'Thorough Post-Install Cleanup',
      fn: example5_ThoroughCleanup,
    },
    {
      number: 6,
      name: 'Dry-Run Mode (Safety Test)',
      fn: example6_DryRunMode,
    },
    {
      number: 7,
      name: 'Custom Cleanup Configuration',
      fn: example7_CustomConfiguration,
    },
    {
      number: 8,
      name: 'Error Handling and Recovery',
      fn: example8_ErrorHandling,
    },
    {
      number: 9,
      name: 'Context Manager Pattern',
      fn: example9_ContextManager,
    },
    {
      number: 10,
      name: 'Complete Post-Install Cleanup Helper',
      fn: example10_CompletePostInstall,
    },
    {
      number: 11,
      name: 'Profile Escalation',
      fn: example11_ProfileEscalation,
    },
    {
      number: 12,
      name: 'Global Handler Management',
      fn: example12_GlobalHandlerManagement,
    },
    {
      number: 13,
      name: 'Batch Installer Removal',
      fn: example13_BatchInstallerRemoval,
    },
    {
      number: 14,
      name: 'Reporting and Audit Trail',
      fn: example14_ReportingAndAudit,
    },
  ];

  console.log('\nAvailable Examples:');
  examples.forEach((example) => {
    console.log(`  ${example.number}. ${example.name}`);
  });

  console.log('\n' + '='.repeat(80));
  console.log('Run individual examples by calling the corresponding function.');
  console.log('Example: await example1_BasicInstallerRemoval()');
  console.log('='.repeat(80));

  // Run all examples for demonstration
  console.log('\nRunning all examples...\n');

  for (const example of examples) {
    try {
      console.log(`\n${'#'.repeat(80)}`);
      console.log(`Running Example ${example.number}: ${example.name}`);
      console.log(`${'#'.repeat(80)}`);
      await example.fn();
    } catch (error) {
      console.error(`Error in example ${example.number}:`, error.message);
    }
  }

  console.log('\n' + '='.repeat(80));
  console.log('All examples completed!');
  console.log('='.repeat(80));
}

// Export examples for use in other modules
module.exports = {
  example1_BasicInstallerRemoval,
  example2_ShellHistoryClearing,
  example3_MinimalCleanup,
  example4_StandardCleanup,
  example5_ThoroughCleanup,
  example6_DryRunMode,
  example7_CustomConfiguration,
  example8_ErrorHandling,
  example9_ContextManager,
  example10_CompletePostInstall,
  example11_ProfileEscalation,
  example12_GlobalHandlerManagement,
  example13_BatchInstallerRemoval,
  example14_ReportingAndAudit,
};

// Run main if executed directly
if (require.main === module) {
  main().catch(console.error);
}
