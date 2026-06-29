# Environment Variable Cleanup Handler - Quick Reference

## Quick Start

### Basic Usage
```javascript
const EnvVarCleanupHandler = require('./env-var-cleanup-handler');

// Create handler
const handler = new EnvVarCleanupHandler({ verbose: true });
handler.startTracking();

// Track BEFORE setting
handler.trackSet('MY_VAR', 'temp_value');
process.env.MY_VAR = 'temp_value';

// Do work...

// Cleanup (restores/deletes as needed)
const result = await handler.executeCleanup();
console.log(result.success);  // true/false
```

### Context Manager (Recommended)
```javascript
const { result, cleanup } = await withCleanupContext(
  async (handler) => {
    handler.trackSet('VAR', 'value');
    process.env.VAR = 'value';
    return doWork();
  }
);
```

## Common Patterns

### New Variable (Will be deleted)
```javascript
handler.trackSet('NEW_VAR', 'value');
process.env.NEW_VAR = 'value';
// After cleanup: deleted
```

### Existing Variable (Will be restored)
```javascript
process.env.EXISTING = 'original';
handler.trackSet('EXISTING', 'modified');
process.env.EXISTING = 'modified';
// After cleanup: 'original'
```

### Dry Run
```javascript
const handler = new EnvVarCleanupHandler({ dryRun: true });
// ... add entries ...
await handler.executeCleanup();
// Variables not actually changed
```

### Multiple Variables
```javascript
handler.trackSet('VAR1', 'value1');
handler.trackSet('VAR2', 'value2');
process.env.VAR1 = 'value1';
process.env.VAR2 = 'value2';

const result = await handler.executeCleanup();
console.log(result.entriesCleaned);      // 2
console.log(result.deletedEntries);      // ['VAR1', 'VAR2']
```

## Configuration Options

```javascript
const handler = new EnvVarCleanupHandler({
  verbose: true,              // Enable logging
  dryRun: false,              // Preview without changes
  trackOriginalValues: true,  // Store originals
  maxRetries: 3,              // Retry attempts
  retryDelayMs: 100,          // Base retry delay
});
```

## API Summary

### Tracking
- `startTracking()` - Start tracking
- `stopTracking()` - Stop tracking
- `trackSet(name, value)` - Track variable set
- `trackDelete(name)` - Track variable delete
- `addEntry(name, current, original)` - Manual entry

### Execution
- `executeCleanup()` - Run cleanup
- `restoreAll()` - Restore all

### Info
- `getTrackedEntries()` - Get all entries
- `getEntryByName(name)` - Get specific entry
- `getStatistics()` - Get stats
- `determineStrategy(entry)` - Get strategy

### Storage
- `exportLog()` - Export as JSON
- `importLog(json)` - Import from JSON
- `clearLog()` - Clear all entries

### Global
- `getCleanupHandler()` - Get global instance
- `initializeCleanupHandler()` - Init global

### Context
- `withCleanupContext(callback)` - Auto cleanup

## Return Value

```javascript
CleanupResult {
  success: boolean,              // Success flag
  entriesCleaned: number,        // Count cleaned
  failedEntries: CleanupEntry[], // Failed entries
  restoredEntries: string[],     // Restored names
  deletedEntries: string[],      // Deleted names
  totalTime: number,             // Time in ms
  errors: string[],              // Error messages
}
```

## Strategy Determination

| Scenario | Strategy | Action |
|----------|----------|--------|
| New variable | Delete | Remove from env |
| Modified existing | Restore | Restore original |
| Unchanged | Skip | No action |

## Best Practices

1. **Track before setting**
   ```javascript
   ✅ handler.trackSet(...);  process.env.VAR = ...;
   ❌ process.env.VAR = ...;  handler.trackSet(...);
   ```

2. **Use context managers**
   ```javascript
   ✅ const { result, cleanup } = await withCleanupContext(...)
   ❌ handler.startTracking(); ... await handler.executeCleanup();
   ```

3. **Check results**
   ```javascript
   const result = await handler.executeCleanup();
   if (!result.success) { console.error(result.errors); }
   ```

4. **Test with dry run**
   ```javascript
   const test = new EnvVarCleanupHandler({ dryRun: true });
   const real = new EnvVarCleanupHandler({ dryRun: false });
   ```

5. **Use verbose in development**
   ```javascript
   const handler = new EnvVarCleanupHandler({ verbose: true });
   ```

## Cleanup Strategies Explained

### Delete Strategy (New Variables)
When you create a new environment variable during execution:
- Original value: `undefined`
- Current value: `your_value`
- Cleanup action: Delete the variable
- After cleanup: Variable removed from process.env

### Restore Strategy (Modified Variables)
When you modify an existing environment variable:
- Original value: `original_value`
- Current value: `modified_value`
- Cleanup action: Restore to original
- After cleanup: Variable set back to original value

### Skip Strategy (Unchanged)
When no changes were made:
- Original value: `value`
- Current value: `value`
- Cleanup action: No action needed
- After cleanup: Variable unchanged

## Error Handling

```javascript
const result = await handler.executeCleanup();

if (!result.success) {
  console.error('Cleanup had errors:');
  result.errors.forEach(err => console.error(`  - ${err}`));
  
  console.log('Failed entries:');
  result.failedEntries.forEach(entry => {
    console.log(`  - ${entry.name}: ${entry.originalValue || 'NEW'}`);
  });
}
```

## Statistics

```javascript
const stats = handler.getStatistics();
console.log(stats);
// {
//   totalEntries: 5,
//   restoredEntries: 2,
//   deletedEntries: 3,
//   skippedEntries: 0,
//   oldestEntry: Date,
//   newestEntry: Date
// }
```

## Persistence

```javascript
// Export cleanup log
const log = handler.exportLog();
fs.writeFileSync('cleanup.json', log);

// Import cleanup log
const handler2 = new EnvVarCleanupHandler();
const saved = fs.readFileSync('cleanup.json', 'utf8');
handler2.importLog(saved);
```

## Global Handler

```javascript
// Get global instance (singleton)
const handler = getCleanupHandler();

// Or initialize with options
const handler = initializeCleanupHandler({
  verbose: true,
  trackOriginalValues: true
});

// Same instance everywhere
const same = getCleanupHandler();
```

## File Locations

- **Implementation:** `env-var-cleanup-handler.ts` (TypeScript) or `.js`
- **Tests:** `env-var-cleanup-handler.test.js`
- **Examples:** `env-var-cleanup-examples.js`
- **Documentation:** `ENV_VAR_CLEANUP_HANDLER.md`

## Typical Workflow

```javascript
// 1. Create handler
const handler = new EnvVarCleanupHandler({ verbose: true });
handler.startTracking();

// 2. Track operations
handler.trackSet('API_KEY', 'test-key');
handler.trackSet('LOG_LEVEL', 'debug');
process.env.API_KEY = 'test-key';
process.env.LOG_LEVEL = 'debug';

// 3. Do work
await runTests();

// 4. Get statistics
const stats = handler.getStatistics();
console.log(`Tracked: ${stats.totalEntries} variables`);

// 5. Execute cleanup
const result = await handler.executeCleanup();
console.log(`Cleaned: ${result.entriesCleaned} entries`);

// 6. Stop tracking
handler.stopTracking();
```

## Advanced: Decorator Pattern

```javascript
const myFunc = withAutoCleanup({ verbose: true })(
  async () => {
    const handler = getCleanupHandler();
    handler.trackSet('VAR', 'value');
    process.env.VAR = 'value';
    return doWork();
  }
);

// Cleanup runs automatically after myFunc completes
await myFunc();
```

## Troubleshooting

### Variables Not Being Cleaned
- Check that you call `trackSet()` BEFORE `process.env.VAR = ...`
- Verify `startTracking()` was called
- Check `getTrackedEntries()` returns entries

### Cleanup Fails
- Check `result.errors` for specific errors
- Enable `verbose: true` to see operations
- Check `result.failedEntries` for problematic entries

### Wrong Strategy Applied
- Ensure variables exist before modifying if restore is needed
- Use `determineStrategy()` to check strategy before cleanup
- Check entry's `originalValue` field

### Global Handler Not Initialized
- Call `getCleanupHandler()` (creates if needed)
- Or call `initializeCleanupHandler()` explicitly
- Verify it's the same instance: `getCleanupHandler() === getCleanupHandler()`
