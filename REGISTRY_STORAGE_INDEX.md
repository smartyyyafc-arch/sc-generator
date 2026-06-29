# Registry Storage Variants - Complete Index

## Project Overview

This project provides production-ready Windows Registry storage implementations supporting multiple hives with consistent interfaces.

## Files Included

### Source Code
1. **registry-storage-variants.ts** - TypeScript implementation
   - Type-safe interfaces
   - Full TypeScript support
   - 300+ lines

2. **registry-storage-variants.js** - JavaScript implementation
   - Node.js compatible
   - ES6 async/await
   - Drop-in replacement for TypeScript version

### Tests
3. **registry-storage-variants.test.js** - Comprehensive test suite
   - 30+ test cases
   - All hive variants covered
   - Error scenarios tested
   - Jest compatible

### Examples
4. **registry-storage-examples.js** - 10 practical examples
   - Application settings management
   - User preferences with defaults
   - Multi-hive redundancy
   - Feature flags
   - Configuration migration
   - System service configuration
   - OS version detection
   - Settings backup/restore
   - Conditional storage selection
   - Hive comparison

### Documentation
5. **REGISTRY_STORAGE_VARIANTS.md** - Main documentation
   - API reference
   - Usage examples
   - Best practices
   - Error handling

6. **REGISTRY_HIVES_COMPARISON.md** - Comprehensive comparison
   - Hive characteristics
   - Detailed use cases
   - Performance analysis
   - Migration paths

7. **REGISTRY_STORAGE_INDEX.md** - This file
   - Project index
   - Quick start guide
   - API summary

## Quick Start

### Installation
```bash
npm install winreg
```

### Basic Usage
```javascript
const { SoftwareHiveStorage, MultiHiveRegistryManager } = 
  require('./registry-storage-variants');

// Single hive
const storage = new SoftwareHiveStorage('MyApp');
await storage.write('Version', '1.0.0');
const version = await storage.read('Version');

// Multiple hives
const manager = new MultiHiveRegistryManager('MyApp');
await manager.writeToAllHives('ConfigKey', 'value');
const result = await manager.readFromFirstAvailable('ConfigKey');
```

## Available Storage Variants

### 1. SoftwareHiveStorage
```javascript
// Path: HKEY_LOCAL_MACHINE\Software\[AppName]
const storage = new SoftwareHiveStorage('MyApp');

// Use for: Global application settings
// Requires: Admin to write
// Scope: All users
```

### 2. CurrentUserHiveStorage
```javascript
// Path: HKEY_CURRENT_USER\Software\[AppName]
const storage = new CurrentUserHiveStorage('Software\\MyApp');

// Use for: User-specific preferences
// Requires: No elevation
// Scope: Current user only
```

### 3. CurrentVersionHiveStorage
```javascript
// Path: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\[AppName]
const storage = new CurrentVersionHiveStorage('MyApp');

// Use for: OS version-related settings
// Requires: Admin to write
// Scope: System-wide
```

### 4. SystemHiveStorage
```javascript
// Path: HKEY_LOCAL_MACHINE\System\[Path]
const storage = new SystemHiveStorage('ControlSet001\\Services\\MyApp');

// Use for: System services and hardware
// Requires: Admin/System
// Scope: System-critical
```

## Common Patterns

### Pattern 1: Global Settings
```javascript
const storage = new SoftwareHiveStorage('MyApp');
await storage.write('Version', '2.1.0');
await storage.write('InstallPath', 'C:\\Program Files\\MyApp');
```

### Pattern 2: User Preferences
```javascript
const userStorage = new CurrentUserHiveStorage('Software\\MyApp');
await userStorage.write('Theme', 'Dark');
await userStorage.write('AutoUpdate', 'true');
```

### Pattern 3: Multi-Hive Redundancy
```javascript
const manager = new MultiHiveRegistryManager('MyApp');
await manager.writeToAllHives('CriticalKey', 'value');
```

### Pattern 4: Fallback Resolution
```javascript
const result = await manager.readFromFirstAvailable('ConfigKey');
if (result) {
  console.log(`Found in ${result.hive}: ${result.value}`);
}
```

### Pattern 5: Factory Creation
```javascript
const variants = RegistryStorageFactory.createAllVariants('MyApp');
for (const [name, storage] of variants) {
  console.log(`${name}: ${storage.hive}`);
}
```

## API Reference

### IRegistryStorage Interface
```typescript
interface IRegistryStorage {
  hive: RegistryHive;
  read(key: string): Promise<string | null>;
  write(key: string, value: string): Promise<void>;
  delete(key: string): Promise<void>;
  exists(key: string): Promise<boolean>;
  listKeys(): Promise<string[]>;
}
```

### MultiHiveRegistryManager Methods
- `writeToAllHives(key, value)` - Write to all hives
- `readFromHive(hive, key)` - Read from specific hive
- `readFromFirstAvailable(key)` - Read from first match
- `deleteFromAllHives(key)` - Delete from all hives
- `getStorageByHive(hive)` - Get storage instance
- `getStorages()` - Get all storage instances

### Factory Methods
- `RegistryStorageFactory.createStorage(hive, subPath)` - Create single variant
- `RegistryStorageFactory.createAllVariants(appName)` - Create all variants

## Enum: RegistryHive

```javascript
{
  HKLM_SOFTWARE,           // Application software
  HKEY_CURRENT_USER,       // User preferences
  CURRENT_VERSION,         // OS version info
  HKLM_SYSTEM,             // System configuration
  HKEY_CLASSES_ROOT,       // File associations
  HKEY_CURRENT_CONFIG      // Current hardware profile
}
```

## Use Case Selection Guide

| Use Case | Recommended | Reason |
|----------|------------|--------|
| Global app settings | Software | Visible to all users |
| User preferences | CurrentUser | User-specific |
| License info | Software | Shared access |
| User theme | CurrentUser | Per-user customization |
| OS compatibility | CurrentVersion | Standard OS location |
| Service config | System | Service management |
| Version detection | CurrentVersion | OS version info |
| Feature flags (global) | Software | All users see same flags |
| Feature flags (user) | CurrentUser | User can override |

## Error Handling

### Graceful Null Returns
```javascript
const value = await storage.read('NonExistent');
// Returns: null (not exception)
```

### Exception Handling
```javascript
try {
  await storage.write('Key', 'value');
} catch (error) {
  console.error('Write failed:', error.message);
}
```

### Multi-Hive Tolerance
```javascript
await manager.writeToAllHives('Key', 'value');
// Uses Promise.allSettled() - tolerates partial failures
```

## Performance Tips

1. **Use CurrentUser for Speed**: No elevation check
2. **Batch Reads**: Use listKeys() once
3. **Cache Values**: Store frequently accessed values
4. **Parallel Multi-Hive**: writeToAllHives() uses Promise.all()
5. **Conditional Selection**: Choose hive based on scope

## Permission Requirements

| Operation | Software | CurrentUser | CurrentVersion | System |
|-----------|----------|-------------|-----------------|--------|
| Read | User | User | User | Admin |
| Write | Admin | User | Admin | Admin |
| Delete | Admin | User | Admin | Admin |

## Testing

```bash
# Run all tests
npm test registry-storage-variants.test.js

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- --testNamePattern="SoftwareHiveStorage"
```

## Examples

### 1. Configuration Management
See: `exampleApplicationSettings()` in registry-storage-examples.js

### 2. User Settings
See: `exampleUserPreferencesWithDefaults()` in registry-storage-examples.js

### 3. Feature Flags
See: `exampleFeatureFlags()` in registry-storage-examples.js

### 4. Service Configuration
See: `exampleSystemServiceConfiguration()` in registry-storage-examples.js

### 5. Settings Backup
See: `exampleSettingsBackupRestore()` in registry-storage-examples.js

## Advanced Topics

### Custom Hive Paths
```javascript
const storage = new SoftwareHiveStorage('Company\\Product\\Module');
// Path: HKEY_LOCAL_MACHINE\Software\Company\Product\Module
```

### Migration Between Hives
```javascript
async function migrateKey(source, target, key) {
  const value = await source.read(key);
  if (value !== null) {
    await target.write(key, value);
    await source.delete(key);
  }
}
```

### Conditional Hive Selection
```javascript
const storage = isAdmin 
  ? new SoftwareHiveStorage('MyApp')
  : new CurrentUserHiveStorage('Software\\MyApp');
```

### Multi-Key Backup
```javascript
const backup = {};
for (const key of await storage.listKeys()) {
  backup[key] = await storage.read(key);
}
```

## Troubleshooting

### "Access Denied" Errors
- Ensure running with appropriate permissions
- Software/System hives require admin
- CurrentUser hive requires user context

### "Key Not Found" (null returns)
- Normal behavior - use null checks
- No exceptions thrown for missing keys
- Use `exists()` to check before read

### Permission Denied on Delete
- Check DACL permissions on registry key
- May need to disable antivirus monitoring
- Ensure elevated privileges

## Dependencies

- **winreg**: `npm install winreg`
- **Node.js**: 12.0.0 or higher
- **Platform**: Windows only

## File Structure

```
registry-storage-variants/
├── registry-storage-variants.ts          # TypeScript source
├── registry-storage-variants.js          # JavaScript source
├── registry-storage-variants.test.js     # Jest tests
├── registry-storage-examples.js          # 10 examples
├── REGISTRY_STORAGE_VARIANTS.md          # Main docs
├── REGISTRY_HIVES_COMPARISON.md          # Comparison guide
└── REGISTRY_STORAGE_INDEX.md             # This file
```

## Key Concepts

### 1. Registry Hive
Root key in Windows Registry (e.g., HKLM, HKCU)

### 2. Registry Path
Full path to a registry key (e.g., `HKLM\Software\MyApp`)

### 3. Registry Key
Individual setting/value within a path

### 4. Value
Data associated with a registry key (string in this implementation)

### 5. Scope
Visibility range (user-specific vs. system-wide)

## Implementation Highlights

- **Interface Consistency**: All variants implement same interface
- **Error Tolerance**: Null returns instead of exceptions for missing keys
- **Async/Await**: Full async implementation
- **Factory Pattern**: Simplified variant creation
- **Type Safety**: TypeScript definitions available
- **Performance**: Optimized for Windows registry access
- **Testing**: Comprehensive test suite included

## Next Steps

1. **Install Dependencies**: `npm install winreg`
2. **Review Documentation**: Read REGISTRY_STORAGE_VARIANTS.md
3. **Study Examples**: Run registry-storage-examples.js
4. **Run Tests**: Execute registry-storage-variants.test.js
5. **Choose Hive**: Use REGISTRY_HIVES_COMPARISON.md to select
6. **Implement**: Use appropriate storage variant for your use case

## Support and Maintenance

- Check error messages in console output
- Review test cases for usage patterns
- Consult REGISTRY_HIVES_COMPARISON.md for hive selection
- Refer to examples for common patterns
- Verify Windows permissions for your scenario

## Version Information

- Current: 1.0.0
- Node.js: 12.0.0+
- Windows: 7+, Server 2008+
- Winreg: Latest

## Summary

This registry storage variants implementation provides:
- 4 production-ready hive storage classes
- Consistent interface across all variants
- Multi-hive coordination manager
- Factory pattern for easy creation
- Comprehensive error handling
- Full TypeScript and JavaScript support
- Extensive documentation and examples
- Complete test coverage

Choose the appropriate hive based on your requirements, use the factory pattern for easy instantiation, and leverage the multi-hive manager for coordinated operations.
