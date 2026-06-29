# Environment Variable Cleanup Handler

A robust TypeScript/JavaScript library for tracking, managing, and cleaning up environment variables with automatic restoration of original values.

## Overview

The `EnvVarCleanupHandler` provides comprehensive functionality for:
- **Automatic tracking** of environment variable modifications
- **Original value preservation** with optional restoration
- **Transaction-like behavior** with rollback capabilities
- **Retry logic** with exponential backoff for reliability
- **Dry-run mode** for previewing cleanup operations
- **Statistics and reporting** for audit trails
- **Export/import** of cleanup logs for persistence

## Features

### Core Capabilities
- ✅ Track new environment variables (to be deleted on cleanup)
- ✅ Track modified environment variables (to be restored on cleanup)
- ✅ Automatic strategy determination (restore vs delete)
- ✅ Dry-run mode without actual modifications
- ✅ Retry logic with configurable backoff
- ✅ Global handler instance for convenience
- ✅ Context manager pattern for automatic cleanup
- ✅ Comprehensive statistics and reporting
- ✅ Export/import of cleanup logs

### Configuration Options

```typescript
interface CleanupOptions {
  verbose?: boolean;              // Enable verbose logging (default: false)
  dryRun?: boolean;               // Simulate cleanup without changes (default: false)
  trackOriginalValues?: boolean;  // Store original values (default: true)
  maxRetries?: number;            // Max retry attempts (default: 3)
  retryDelayMs?: number;          // Base retry delay in ms (default: 100)
  autoRestoreOnDelete?: boolean;  // Auto-restore on error (default: true)
}
```

## Installation

### TypeScript
```typescript
import { EnvVarCleanupHandler, initializeCleanupHandler } from './env-var-cleanup-handler';
```

### JavaScript
```javascript
const EnvVarCleanupHandler = require('./env-var-cleanup-handler');
const { initializeCleanupHandler, getCleanupHandler } = require('./env-var-cleanup-handler');
```

## Usage Examples

### Basic Cleanup

Track and cleanup a single environment variable:

```javascript
const handler = new EnvVarCleanupHandler({ verbose: true });
handler.startTracking();

// Track BEFORE setting the variable
handler.trackSet('TEMP_API_KEY', 'secret-key');
process.env.TEMP_API_KEY = 'secret-key';

// Do work with the variable...

// Cleanup
const result = await handler.executeCleanup();
console.log(result);
// Output: Variable is deleted
```

### Restore Original Values

Modify an existing variable and restore it on cleanup:

```javascript
// Set original value
process.env.CONFIG_ENV = 'production';

const handler = new EnvVarCleanupHandler();
handler.startTracking();

// Track BEFORE modifying
handler.trackSet('CONFIG_ENV', 'test');
process.env.CONFIG_ENV = 'test';

// Do work with modified variable...

// Cleanup - restores original value
const result = await handler.executeCleanup();
console.log(process.env.CONFIG_ENV);
// Output: 'production'
```

### Dry Run Mode

Preview cleanup without actual modifications:

```javascript
const handler = new EnvVarCleanupHandler({
  verbose: true,
  dryRun: true  // Preview only
});
handler.startTracking();

handler.trackSet('TEMP_VAR_1', 'value1');
handler.trackSet('TEMP_VAR_2', 'value2');
process.env.TEMP_VAR_1 = 'value1';
process.env.TEMP_VAR_2 = 'value2';

const result = await handler.executeCleanup();
console.log(process.env.TEMP_VAR_1);
// Output: 'value1' (still set, not deleted)
```

### Context Manager Pattern

Automatic cleanup with context manager:

```javascript
const { result, cleanup } = await withCleanupContext(
  async (handler) => {
    // Setup
    handler.trackSet('DB_URL', 'postgres://test@localhost/testdb');
    process.env.DB_URL = 'postgres://test@localhost/testdb';

    // Do work
    const data = await queryDatabase();

    return data;
  },
  { verbose: true }
);

console.log(process.env.DB_URL);
// Output: undefined (automatically cleaned up)
```

### Multiple Variables

Track and cleanup multiple variables:

```javascript
const handler = new EnvVarCleanupHandler();
handler.startTracking();

// Track multiple variables
handler.trackSet('API_KEY', 'temp-key');
handler.trackSet('LOG_LEVEL', 'debug');
handler.trackSet('DEBUG_MODE', 'true');

// Set variables
process.env.API_KEY = 'temp-key';
process.env.LOG_LEVEL = 'debug';
process.env.DEBUG_MODE = 'true';

// Get statistics before cleanup
const stats = handler.getStatistics();
console.log(`Total entries: ${stats.totalEntries}`);
console.log(`To delete: ${stats.deletedEntries}`);
console.log(`To restore: ${stats.restoredEntries}`);

// Cleanup
const result = await handler.executeCleanup();
console.log(`Cleaned: ${result.entriesCleaned}`);
```

### Global Handler

Use the global handler instance:

```javascript
const handler = getCleanupHandler();
handler.startTracking();

handler.trackSet('GLOBAL_VAR', 'value');
process.env.GLOBAL_VAR = 'value';

// Later in code
const globalHandler = getCleanupHandler();
// Same instance!

await globalHandler.executeCleanup();
```

### Export and Import

Persist cleanup logs:

```javascript
const handler1 = new EnvVarCleanupHandler();
handler1.startTracking();

handler1.trackSet('VAR1', 'value1');
handler1.trackSet('VAR2', 'value2');

// Export
const log = handler1.exportLog();
fs.writeFileSync('cleanup.json', log);

// Later, import
const handler2 = new EnvVarCleanupHandler();
const savedLog = fs.readFileSync('cleanup.json', 'utf8');
handler2.importLog(savedLog);

// Use imported entries
await handler2.executeCleanup();
```

## API Reference

### Class: EnvVarCleanupHandler

#### Constructor

```typescript
constructor(options?: CleanupOptions)
```

#### Methods

##### Tracking

```typescript
// Start tracking modifications
startTracking(): void

// Stop tracking modifications
stopTracking(): void

// Track a variable set operation
trackSet(name: string, value: string): void

// Track a variable delete operation
trackDelete(name: string): void

// Manually add entry
addEntry(name: string, currentValue?: string, originalValue?: string): void

// Clear all tracked entries
clearLog(): void
```

##### Retrieval

```typescript
// Get all tracked entries
getTrackedEntries(): CleanupEntry[]

// Get entry by variable name
getEntryByName(name: string): CleanupEntry | undefined
```

##### Cleanup Execution

```typescript
// Execute cleanup (restore/delete as needed)
async executeCleanup(): Promise<CleanupResult>

// Restore all to original values
async restoreAll(): Promise<CleanupResult>
```

##### Statistics and Reporting

```typescript
// Get cleanup statistics
getStatistics(): {
  totalEntries: number;
  restoredEntries: number;
  deletedEntries: number;
  skippedEntries: number;
  oldestEntry: Date | null;
  newestEntry: Date | null;
}

// Determine cleanup strategy for entry
determineStrategy(entry: CleanupEntry): 'restore' | 'delete' | 'skip'

// Export log as JSON
exportLog(): string

// Import log from JSON
importLog(jsonData: string): void
```

### Global Functions

```typescript
// Initialize and return global handler
initializeCleanupHandler(options?: CleanupOptions): EnvVarCleanupHandler

// Get global handler instance
getCleanupHandler(): EnvVarCleanupHandler

// Decorator for automatic cleanup
withAutoCleanup(options?: CleanupOptions)

// Context manager for automatic cleanup
async withCleanupContext<T>(
  callback: (handler: EnvVarCleanupHandler) => Promise<T>,
  options?: CleanupOptions
): Promise<{ result: T; cleanup: CleanupResult }>
```

### Interfaces

#### CleanupEntry

```typescript
interface CleanupEntry {
  name: string;                    // Variable name
  currentValue: string | undefined; // Current value
  originalValue: string | undefined; // Value before modification
  wasSet: boolean;                 // Whether var existed before
  timestamp: Date;                 // When tracked
  strategy?: 'restore' | 'delete' | 'skip'; // Cleanup strategy
}
```

#### CleanupResult

```typescript
interface CleanupResult {
  success: boolean;                // Overall success
  entriesCleaned: number;         // Count of cleaned entries
  failedEntries: CleanupEntry[];  // Entries that failed
  restoredEntries: string[];      // Restored variable names
  deletedEntries: string[];       // Deleted variable names
  totalTime: number;              // Execution time in ms
  errors: string[];               // Error messages
}
```

## Cleanup Strategy

The handler automatically determines the cleanup strategy for each tracked variable:

### Delete Strategy
- Applied when: Variable didn't exist before (newly created)
- Action: Variable is deleted from environment
- Use case: Temporary variables added during execution

### Restore Strategy
- Applied when: Variable existed before and was modified
- Action: Variable is restored to original value
- Use case: Configuration variables temporarily changed for testing

### Skip Strategy
- Applied when: Variable wasn't changed (shouldn't happen normally)
- Action: No cleanup performed
- Use case: Edge case handling

## Best Practices

### 1. Track Before Setting

Always call `trackSet()` BEFORE modifying the environment variable:

```javascript
// ✅ Correct
handler.trackSet('MY_VAR', 'new_value');
process.env.MY_VAR = 'new_value';

// ❌ Wrong - captures modified value as "original"
process.env.MY_VAR = 'new_value';
handler.trackSet('MY_VAR', 'new_value');
```

### 2. Use Context Managers

Prefer context managers for automatic cleanup:

```javascript
// ✅ Recommended
const { result, cleanup } = await withCleanupContext(
  async (handler) => {
    handler.trackSet('VAR', 'value');
    process.env.VAR = 'value';
    return doWork();
  }
);

// ✗ Manual - easy to forget cleanup
handler.trackSet('VAR', 'value');
process.env.VAR = 'value';
// Might forget this:
await handler.executeCleanup();
```

### 3. Enable Verbose for Debugging

Use verbose mode during development:

```javascript
const handler = new EnvVarCleanupHandler({
  verbose: true  // Logs all operations
});
```

### 4. Use Dry Run for Safety

Test cleanup strategy before actual execution:

```javascript
const dryHandler = new EnvVarCleanupHandler({ dryRun: true });
// ... add entries ...
await dryHandler.executeCleanup(); // Preview only

// Once satisfied:
const realHandler = new EnvVarCleanupHandler({ dryRun: false });
// ... add entries ...
await realHandler.executeCleanup(); // Actually cleanup
```

### 5. Check Results

Always check cleanup results for errors:

```javascript
const result = await handler.executeCleanup();

if (!result.success) {
  console.error('Cleanup failed:', result.errors);
  console.log('Failed entries:', result.failedEntries);
}
```

## Error Handling

The handler provides comprehensive error handling:

### Retry Logic
- Automatically retries failed cleanup operations
- Configurable retry count and delay
- Exponential backoff strategy

### Error Reporting
- Errors collected in `CleanupResult.errors`
- Failed entries tracked in `failedEntries`
- Verbose logging for debugging

### Example

```javascript
const result = await handler.executeCleanup();

if (result.failedEntries.length > 0) {
  console.error('Failed to cleanup:');
  result.failedEntries.forEach(entry => {
    console.error(`  - ${entry.name}`);
  });
}

result.errors.forEach(error => {
  console.error(`Error: ${error}`);
});
```

## Performance Considerations

### Caching
- Variables are not cached (env vars can change anytime)
- Tracking is O(n) where n is number of tracked variables

### Memory
- Cleanup log stored in memory
- Export to file for long-running processes

### Retry Delays
- Default: 100ms base delay
- Exponential backoff: 100ms → 200ms → 400ms
- Configurable via `retryDelayMs` option

## Testing

Comprehensive test suite included:

```bash
node env-var-cleanup-handler.test.js
```

Tests cover:
- Basic tracking
- Cleanup strategies
- Execution
- Value restoration
- Dry run mode
- Context managers
- Statistics
- Export/import
- Global handlers
- Error handling

## Examples

Run the usage examples:

```bash
node env-var-cleanup-examples.js
```

Includes 10 detailed examples:
1. Basic variable cleanup
2. Restoring original values
3. Dry run mode
4. Context manager pattern
5. Multiple variable tracking
6. Global handler usage
7. Export and import
8. Statistics and reporting
9. Error recovery
10. Advanced workflow

## TypeScript Support

Full TypeScript support with type definitions:

```typescript
import {
  EnvVarCleanupHandler,
  CleanupEntry,
  CleanupOptions,
  CleanupResult,
  initializeCleanupHandler,
  withCleanupContext,
} from './env-var-cleanup-handler';

const handler = new EnvVarCleanupHandler({ verbose: true });
const result: CleanupResult = await handler.executeCleanup();
```

## License

Part of sc-generator project.

## Related Files

- `env-var-cleanup-handler.ts` - TypeScript implementation
- `env-var-cleanup-handler.js` - JavaScript implementation
- `env-var-cleanup-handler.test.js` - Test suite
- `env-var-cleanup-examples.js` - Usage examples
- `env-var-retrieval-handler.ts` - Environment variable retrieval
- `registry-cleanup-handler.ts` - Similar registry cleanup handler
