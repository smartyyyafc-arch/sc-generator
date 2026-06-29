# Registry Cleanup Handler - Quick Start Guide

## Overview

The Registry Cleanup Handler provides automatic cleanup of Windows Registry modifications with support for:
- Multi-hive tracking (HKLM, HKCU, CurrentVersion, System)
- Automatic value restoration
- Dry run testing
- Context manager pattern
- Error retry logic

## Files

### Core Implementation
- **registry-cleanup-handler.ts** (13KB)
  - Main `RegistryCleanupHandler` class
  - Global handler management
  - Context manager utilities
  - Cleanup tracking and execution

### Examples & Integration
- **registry-cleanup-examples.ts** (11KB)
  - 10 comprehensive usage examples
  - Covers basic to advanced patterns
  - Demonstrates all major features

- **registry-cleanup-integration.ts** (12KB)
  - 7 real-world integration patterns
  - Service initialization with cleanup
  - Application installer with rollback
  - Transaction-like operations
  - Configuration management
  - Feature toggles
  - Audit trail management
  - Batch operations

### Testing & Documentation
- **registry-cleanup-handler.test.ts** (12KB)
  - Comprehensive unit test suite
  - Integration tests
  - 30+ test cases covering all features

- **REGISTRY_CLEANUP_README.md**
  - Complete API reference
  - Detailed usage guide
  - Performance considerations
  - Best practices

## Quick Examples

### Example 1: Basic Cleanup (5 lines)
```typescript
const handler = new RegistryCleanupHandler({ verbose: true });
handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'MyKey', 'OldValue');
const result = await handler.executeCleanup();
console.log(`Cleaned ${result.entriesCleaned} entries`);
```

### Example 2: Context Manager (Recommended)
```typescript
const { result, cleanup } = await withCleanupContext(
  async (handler) => {
    handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TempKey');
    return 'done';
  },
  { verbose: true }
);
```

### Example 3: Dry Run (Test Only)
```typescript
const handler = new RegistryCleanupHandler({ dryRun: true });
handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TestKey');
await handler.executeCleanup(); // No actual changes
```

### Example 4: Multi-Hive Tracking
```typescript
const handler = new RegistryCleanupHandler();
handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'GlobalKey');
handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'UserKey');
handler.addEntry(RegistryHive.CURRENT_VERSION, 'VersionKey');
const result = await handler.executeCleanup();
```

### Example 5: Value Restoration
```typescript
const handler = new RegistryCleanupHandler({
  trackOriginalValues: true
});
// Original values will be restored automatically
handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key', 'OriginalValue');
await handler.executeCleanup();
```

## Key Classes

### RegistryCleanupHandler
Main cleanup manager with tracking and execution capabilities.

**Constructor Options:**
```typescript
new RegistryCleanupHandler({
  verbose: false,           // Enable logging
  dryRun: false,           // Test without changes
  trackOriginalValues: true, // Restore original values
  maxRetries: 3            // Retry attempts
})
```

**Key Methods:**
- `startTracking()` - Begin tracking modifications
- `stopTracking()` - Stop tracking
- `addEntry(hive, key, originalValue?)` - Add to cleanup log
- `executeCleanup()` - Perform cleanup
- `getTrackedEntries()` - Get all tracked entries
- `exportLog()` / `importLog()` - Save/restore logs

### Utility Functions

**withCleanupContext** (Recommended)
```typescript
const { result, cleanup } = await withCleanupContext(
  async (handler) => { /* your code */ },
  { verbose: true }
);
```

**Global Handler**
```typescript
const handler = initializeCleanupHandler();
const same = getCleanupHandler(); // Same instance
```

## Integration Patterns

### Pattern 1: Service with Auto-Cleanup
```typescript
class MyService {
  private handler = new RegistryCleanupHandler();
  
  async start() {
    this.handler.startTracking();
    process.on('SIGINT', () => this.stop());
  }
  
  async stop() {
    await this.handler.executeCleanup();
  }
}
```

### Pattern 2: Installer with Rollback
```typescript
async function install() {
  const { result, cleanup } = await withCleanupContext(
    async (handler) => {
      await registerApp(handler);
      await installSettings(handler);
      return 'installed';
    }
  );
}
```

### Pattern 3: Transaction-like Operations
```typescript
const tx = new RegistryTransaction();
tx.begin();
tx.addOperation(hive, key, value);
const committed = await tx.commit() || await tx.rollback();
```

### Pattern 4: Feature Toggles
```typescript
const features = new FeatureToggleManager('MyApp');
await features.enableFeature('BetaMode');
if (features.isFeatureEnabled('BetaMode')) { /* ... */ }
```

## Common Patterns

### Pattern: Automatic Cleanup
```typescript
try {
  handler.startTracking();
  // Do registry modifications
  handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1');
} finally {
  await handler.executeCleanup();
}
```

### Pattern: Error Recovery
```typescript
const result = await handler.executeCleanup();
if (!result.success) {
  console.error('Failed entries:', result.failedEntries);
  console.error('Errors:', result.errors);
}
```

### Pattern: Statistics
```typescript
const stats = handler.getStatistics();
console.log(`Total: ${stats.totalEntries}`);
console.log(`By hive:`, stats.entriesByHive);
```

### Pattern: Persistence
```typescript
const json = handler.exportLog();
// ... save to file ...
const handler2 = new RegistryCleanupHandler();
handler2.importLog(json);
```

## Performance Tips

1. **Use Dry Run for Testing**
   ```typescript
   new RegistryCleanupHandler({ dryRun: true })
   ```

2. **Disable Value Tracking if Not Needed**
   ```typescript
   new RegistryCleanupHandler({ trackOriginalValues: false })
   ```

3. **Group Operations by Hive**
   - More efficient cleanup execution

4. **Use Context Manager**
   - Automatic error handling
   - Guaranteed cleanup execution

5. **Limit Retries in Production**
   ```typescript
   new RegistryCleanupHandler({ maxRetries: 2 })
   ```

## Error Handling

```typescript
try {
  const result = await handler.executeCleanup();
  
  if (result.success) {
    console.log(`Success: ${result.entriesCleaned} cleaned`);
  } else {
    result.failedEntries.forEach(entry => {
      console.error(`Failed: ${entry.hive}\\${entry.key}`);
    });
  }
} catch (error) {
  console.error('Cleanup error:', error);
}
```

## Data Types

### CleanupEntry
```typescript
{
  hive: RegistryHive;
  key: string;
  originalValue?: string;
  wasDeleted?: boolean;
  timestamp: Date;
}
```

### CleanupResult
```typescript
{
  success: boolean;
  entriesCleaned: number;
  failedEntries: CleanupEntry[];
  totalTime: number;
  errors: string[];
}
```

## Supported Hives

- `RegistryHive.HKLM_SOFTWARE` - HKEY_LOCAL_MACHINE\\Software
- `RegistryHive.HKEY_CURRENT_USER` - HKEY_CURRENT_USER
- `RegistryHive.CURRENT_VERSION` - ...\\CurrentVersion
- `RegistryHive.HKLM_SYSTEM` - ...\\System

## Best Practices

1. ✅ **Use Context Manager** for automatic cleanup
2. ✅ **Enable Verbose** during development
3. ✅ **Use Dry Run** before production cleanup
4. ✅ **Track Original Values** for safe restoration
5. ✅ **Export Logs** for audit trails
6. ✅ **Handle Errors** gracefully
7. ✅ **Test Thoroughly** before deployment

## Common Issues

### Issue: Cleanup Not Executing
- Ensure `startTracking()` was called or use context manager
- Check if tracking was stopped with `stopTracking()`

### Issue: Permission Denied
- Some registry keys require admin privileges
- Failed entries appear in `CleanupResult.failedEntries`

### Issue: Retries Not Working
- Increase `maxRetries` option (default: 3)
- Check Windows event logs for permission issues

## Integration with Existing Code

```typescript
// Before: Manual cleanup
async function oldWay() {
  // Modify registry
  // Hope we remember to cleanup
}

// After: Automatic cleanup
async function newWay() {
  return withCleanupContext(
    async (handler) => {
      // Modify registry
      handler.addEntry(hive, key);
      // Automatic cleanup guaranteed
    }
  );
}
```

## Testing Your Implementation

```typescript
// Test with dry run
const handler = new RegistryCleanupHandler({ 
  dryRun: true,
  verbose: true 
});

handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TestKey');
const result = await handler.executeCleanup();

// Verify in dry run results
console.log(`Would clean: ${result.entriesCleaned} entries`);
```

## Resources

- **API Reference**: See REGISTRY_CLEANUP_README.md
- **Examples**: See registry-cleanup-examples.ts
- **Patterns**: See registry-cleanup-integration.ts
- **Tests**: See registry-cleanup-handler.test.ts

## Summary

The Registry Cleanup Handler provides:
- ✅ Automatic cleanup of registry modifications
- ✅ Multi-hive support with granular control
- ✅ Value restoration to original state
- ✅ Transaction-like behavior with rollback
- ✅ Flexible integration patterns
- ✅ Comprehensive error handling
- ✅ Production-ready with retry logic

Use it to safely manage temporary registry changes with guaranteed cleanup!
