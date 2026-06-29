# Registry Cleanup Handler

A comprehensive TypeScript solution for tracking and cleaning up Windows Registry modifications. This module provides automatic cleanup functionality to remove traces after execution, with support for multiple registry hives and flexible cleanup patterns.

## Features

- **Multi-Hive Support**: Track and cleanup modifications across all Windows registry hives (HKLM, HKCU, CurrentVersion, System)
- **Automatic Tracking**: Track registry write and delete operations automatically
- **Value Restoration**: Restore original values after execution
- **Dry Run Mode**: Test cleanup operations without actual modification
- **Context Manager**: Automatic cleanup with context manager pattern
- **Export/Import**: Save and restore cleanup logs in JSON format
- **Retry Logic**: Automatic retry with exponential backoff for failed operations
- **Statistics**: Get detailed statistics about tracked entries
- **Global Handler**: Singleton pattern for global cleanup handler

## Installation

```typescript
import {
  RegistryCleanupHandler,
  initializeCleanupHandler,
  getCleanupHandler,
  withCleanupContext,
  withAutoCleanup,
} from './registry-cleanup-handler';
```

## Quick Start

### Basic Usage

```typescript
// Create a cleanup handler
const handler = new RegistryCleanupHandler({ verbose: true });

// Start tracking registry modifications
handler.startTracking();

// Add entries to cleanup log
handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'MyApp\\Setting1', 'OriginalValue');
handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'MyApp\\UserPref');

// Execute cleanup
const result = await handler.executeCleanup();
console.log(`Cleaned ${result.entriesCleaned} entries`);
```

### Context Manager Pattern (Recommended)

```typescript
const { result, cleanup } = await withCleanupContext(
  async (handler) => {
    // Your operation here
    handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TempKey');
    
    return 'operation result';
  },
  { verbose: true }
);

// Cleanup automatically executed
console.log(`Cleaned ${cleanup.entriesCleaned} entries`);
```

### Dry Run Mode

Test cleanup operations without making actual changes:

```typescript
const handler = new RegistryCleanupHandler({
  dryRun: true,  // No actual modifications
  verbose: true
});

handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TestKey');
const result = await handler.executeCleanup();
// No actual deletion occurs
```

## API Reference

### RegistryCleanupHandler

Main cleanup handler class for tracking and managing registry cleanup operations.

#### Constructor

```typescript
new RegistryCleanupHandler(options?: CleanupOptions)
```

**Options:**
- `verbose?: boolean` - Enable verbose logging (default: false)
- `dryRun?: boolean` - Test cleanup without actual modifications (default: false)
- `trackOriginalValues?: boolean` - Track and restore original values (default: true)
- `maxRetries?: number` - Maximum retry attempts per entry (default: 3)

#### Methods

##### `startTracking(): void`
Start tracking registry modifications.

```typescript
handler.startTracking();
```

##### `stopTracking(): void`
Stop tracking registry modifications.

```typescript
handler.stopTracking();
```

##### `addEntry(hive, key, originalValue?): void`
Manually add an entry to the cleanup log.

```typescript
handler.addEntry(
  RegistryHive.HKLM_SOFTWARE,
  'MyApp\\Setting',
  'OriginalValue'
);
```

##### `trackWrite(hive, key, storage): Promise<void>`
Track a registry write operation.

```typescript
await handler.trackWrite(
  RegistryHive.HKLM_SOFTWARE,
  'MyApp\\Setting',
  storage
);
```

##### `trackDelete(hive, key): void`
Track a registry delete operation.

```typescript
handler.trackDelete(RegistryHive.HKLM_SOFTWARE, 'MyApp\\Setting');
```

##### `getTrackedEntries(): CleanupEntry[]`
Get all tracked entries.

```typescript
const entries = handler.getTrackedEntries();
```

##### `getEntriesByHive(hive): CleanupEntry[]`
Get entries by specific hive.

```typescript
const softwareEntries = handler.getEntriesByHive(RegistryHive.HKLM_SOFTWARE);
```

##### `executeCleanup(): Promise<CleanupResult>`
Execute cleanup operation.

```typescript
const result = await handler.executeCleanup();
// Returns: { success, entriesCleaned, failedEntries, totalTime, errors }
```

##### `cleanupHive(hive): Promise<CleanupResult>`
Cleanup specific hive only.

```typescript
const result = await handler.cleanupHive(RegistryHive.HKLM_SOFTWARE);
```

##### `restoreAll(): Promise<CleanupResult>`
Restore all entries to their original values.

```typescript
const result = await handler.restoreAll();
```

##### `getStatistics(): Statistics`
Get detailed statistics about tracked entries.

```typescript
const stats = handler.getStatistics();
// Returns: { totalEntries, entriesByHive, oldestEntry, newestEntry }
```

##### `exportLog(): string`
Export cleanup log as JSON string.

```typescript
const json = handler.exportLog();
```

##### `importLog(jsonData): void`
Import cleanup log from JSON string.

```typescript
handler.importLog(jsonData);
```

##### `clearLog(): void`
Clear cleanup log without executing cleanup.

```typescript
handler.clearLog();
```

### Global Handler Functions

#### `initializeCleanupHandler(options?): RegistryCleanupHandler`
Initialize and return global cleanup handler singleton.

```typescript
const handler = initializeCleanupHandler({ verbose: true });
```

#### `getCleanupHandler(): RegistryCleanupHandler`
Get existing global cleanup handler instance.

```typescript
const handler = getCleanupHandler();
```

### Utility Functions

#### `withCleanupContext<T>(callback, options?): Promise<{result, cleanup}>`
Context manager for automatic cleanup.

```typescript
const { result, cleanup } = await withCleanupContext(
  async (handler) => {
    // Your code here
    return 'result';
  },
  { verbose: true, dryRun: false }
);
```

#### `withAutoCleanup(options?)`
Decorator for automatic cleanup (experimental).

```typescript
@withAutoCleanup({ verbose: true })
async function myOperation() {
  // Cleanup automatically runs after function
}
```

## Data Types

### CleanupEntry

```typescript
interface CleanupEntry {
  hive: RegistryHive;
  key: string;
  originalValue?: string | null;
  wasDeleted?: boolean;
  timestamp: Date;
}
```

### CleanupResult

```typescript
interface CleanupResult {
  success: boolean;
  entriesCleaned: number;
  failedEntries: CleanupEntry[];
  totalTime: number;
  errors: string[];
}
```

### CleanupOptions

```typescript
interface CleanupOptions {
  verbose?: boolean;
  dryRun?: boolean;
  trackOriginalValues?: boolean;
  maxRetries?: number;
}
```

## Usage Examples

### Example 1: Multi-Hive Application Settings

```typescript
async function configureApplicationWithCleanup() {
  const { result, cleanup } = await withCleanupContext(
    async (handler) => {
      const manager = new MultiHiveRegistryManager('MyApp');

      // Modify settings across hives
      await manager.writeToAllHives('Version', '2.1.0');
      await manager.writeToAllHives('LastRun', new Date().toISOString());

      // Track modifications for cleanup
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'MyApp\\Version');
      handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'Software\\MyApp\\LastRun');

      return 'Configuration complete';
    },
    { verbose: true }
  );

  console.log(`Cleaned ${cleanup.entriesCleaned} entries`);
}
```

### Example 2: Temporary Test Configuration

```typescript
async function testWithTemporaryRegistry() {
  const handler = new RegistryCleanupHandler({ 
    verbose: true,
    trackOriginalValues: true
  });

  handler.startTracking();

  try {
    // Create temporary settings
    const storage = new SoftwareHiveStorage('TestApp');
    await handler.trackWrite(
      RegistryHive.HKLM_SOFTWARE,
      'TestKey',
      storage
    );

    // Run tests...
    
  } finally {
    // Automatic cleanup
    const result = await handler.executeCleanup();
    console.log(`Cleaned up ${result.entriesCleaned} test entries`);
  }
}
```

### Example 3: Selective Hive Cleanup

```typescript
async function cleanupSpecificHives() {
  const handler = new RegistryCleanupHandler();

  // Add entries from multiple hives
  handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1', 'Value1');
  handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'Key2', 'Value2');
  handler.addEntry(RegistryHive.CURRENT_VERSION, 'Key3', 'Value3');

  // Cleanup only Software hive
  const result = await handler.cleanupHive(RegistryHive.HKLM_SOFTWARE);
  console.log(`Cleaned Software hive: ${result.entriesCleaned} entries`);

  // Cleanup remaining hives
  const finalResult = await handler.executeCleanup();
  console.log(`Cleaned all hives: ${finalResult.entriesCleaned} entries`);
}
```

### Example 4: Persistent Cleanup Log

```typescript
async function saveCleanupState() {
  const handler = new RegistryCleanupHandler();

  // Add entries
  handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1', 'Value1');
  handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'Key2', 'Value2');

  // Export for persistent storage
  const json = handler.exportLog();
  fs.writeFileSync('cleanup-log.json', json);

  // Later, restore and execute
  const restored = fs.readFileSync('cleanup-log.json', 'utf-8');
  handler.importLog(restored);
  const result = await handler.executeCleanup();
}
```

### Example 5: Error Handling

```typescript
async function robustCleanup() {
  const handler = new RegistryCleanupHandler({
    verbose: true,
    maxRetries: 5,  // Retry up to 5 times
  });

  try {
    handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1');
    handler.addEntry(RegistryHive.HKLM_SYSTEM, 'ProtectedKey');

    const result = await handler.executeCleanup();

    if (!result.success) {
      console.error(`Cleanup partially failed:`);
      result.failedEntries.forEach(entry => {
        console.error(`  - ${entry.hive}\\${entry.key}`);
      });
      console.error('Errors:', result.errors);
    }
  } catch (error) {
    console.error('Cleanup execution error:', error);
  }
}
```

## Advanced Usage

### Custom Retry Logic

```typescript
const handler = new RegistryCleanupHandler({
  maxRetries: 3,  // Retry 3 times with exponential backoff
  verbose: true
});
```

### Statistics and Monitoring

```typescript
const handler = new RegistryCleanupHandler();

// Add entries...
handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1');

// Get statistics
const stats = handler.getStatistics();
console.log(`Total entries: ${stats.totalEntries}`);
console.log(`By hive:`, stats.entriesByHive);
console.log(`Oldest: ${stats.oldestEntry}`);
console.log(`Newest: ${stats.newestEntry}`);
```

### Batch Operations

```typescript
const handler = new RegistryCleanupHandler({ dryRun: true });

// Add many entries
const keys = ['Key1', 'Key2', 'Key3', 'Key4', 'Key5'];
for (const key of keys) {
  handler.addEntry(RegistryHive.HKLM_SOFTWARE, key);
}

// Cleanup in batch
const result = await handler.executeCleanup();
console.log(`Processed ${result.entriesCleaned} entries`);
```

## Testing

Run the test suite:

```bash
npm test registry-cleanup-handler.test.ts
```

Example tests cover:
- Initialization with various options
- Tracking and log management
- Query and filtering operations
- Cleanup execution and dry runs
- Export/import functionality
- Global handler singleton pattern
- Context manager integration
- Error handling and recovery

## Performance Considerations

1. **Dry Run Mode**: Use dry run for testing without actual registry modifications
2. **Tracking Original Values**: Disable if not needed to reduce memory usage
3. **Batch Cleanup**: Group operations by hive for efficient cleanup
4. **Retry Logic**: Configure max retries based on environment
5. **Verbose Logging**: Disable in production for better performance

## Best Practices

1. **Always Use Context Manager**: Ensures cleanup runs even on errors
2. **Enable Verbose in Development**: Track operations during development
3. **Use Dry Run for Testing**: Test cleanup logic before production
4. **Export Logs for Debugging**: Save cleanup logs for audit trails
5. **Handle Errors Gracefully**: Check CleanupResult for failures

## Supported Registry Hives

- `HKEY_LOCAL_MACHINE\Software` (HKLM_SOFTWARE)
- `HKEY_CURRENT_USER` (HKEY_CURRENT_USER)
- `HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion` (CURRENT_VERSION)
- `HKEY_LOCAL_MACHINE\System` (HKLM_SYSTEM)

## Limitations

- Requires Windows registry access permissions
- Some registry keys may be protected by Windows
- Maximum retry attempts limited to configured value
- Timestamps have millisecond precision

## License

Part of the sc-generator project.
