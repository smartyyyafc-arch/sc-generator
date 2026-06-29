# Registry Storage Variants Documentation

## Overview

This module provides multiple Windows Registry storage implementations using different hives. Each variant is optimized for specific use cases and follows a consistent interface.

## Supported Registry Hives

### 1. HKLM Software (HKEY_LOCAL_MACHINE\Software)
- **Purpose**: Application-wide settings and software configurations
- **Scope**: All users on the system
- **Use Cases**: Global application settings, version information, feature flags
- **Access Level**: Requires administrator privileges to write

### 2. HKEY_CURRENT_USER
- **Purpose**: User-specific settings and preferences
- **Scope**: Current logged-in user only
- **Use Cases**: User preferences, theme settings, personal configurations
- **Access Level**: User can read/write own hive

### 3. CurrentVersion (HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion)
- **Purpose**: System version-related settings and OS configurations
- **Scope**: System-wide OS information
- **Use Cases**: Windows version detection, OS compatibility settings
- **Access Level**: Requires administrator privileges to write

### 4. System Hive (HKEY_LOCAL_MACHINE\System)
- **Purpose**: System hardware profiles and device configurations
- **Scope**: System device settings
- **Use Cases**: Hardware configuration, boot settings, service configuration
- **Access Level**: Requires administrator privileges

## Architecture

```
BaseRegistryStorage
├── SoftwareHiveStorage
├── CurrentUserHiveStorage
├── CurrentVersionHiveStorage
└── SystemHiveStorage

MultiHiveRegistryManager (coordinates all variants)
RegistryStorageFactory (creates storage instances)
```

## Interface Definition

All storage implementations implement the `IRegistryStorage` interface:

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

## Usage Examples

### Single Hive Storage

```javascript
const { SoftwareHiveStorage } = require('./registry-storage-variants');

// Create storage for Software hive
const storage = new SoftwareHiveStorage('MyApp');

// Read value
const value = await storage.read('Version');

// Write value
await storage.write('Version', '1.0.0');

// Check existence
const exists = await storage.exists('Version');

// Delete value
await storage.delete('Version');

// List all keys
const keys = await storage.listKeys();
```

### User-Specific Storage

```javascript
const { CurrentUserHiveStorage } = require('./registry-storage-variants');

// Create storage for current user
const userStorage = new CurrentUserHiveStorage('Software\\MyApp');

// User preferences are isolated per user
await userStorage.write('Theme', 'Dark');
await userStorage.write('Language', 'en-US');
```

### CurrentVersion Storage

```javascript
const { CurrentVersionHiveStorage } = require('./registry-storage-variants');

// Create storage for Windows CurrentVersion
const versionStorage = new CurrentVersionHiveStorage('MyApp');

// Store OS-specific settings
await versionStorage.write('MinOSVersion', '10.0');
```

### System Storage

```javascript
const { SystemHiveStorage } = require('./registry-storage-variants');

// Create storage for system configuration
const systemStorage = new SystemHiveStorage('ControlSet001\\Services\\MyService');

// Configure system services
await systemStorage.write('Start', '2'); // Auto-start
await systemStorage.write('Type', '20');
```

### Multi-Hive Manager

```javascript
const { MultiHiveRegistryManager } = require('./registry-storage-variants');

// Create manager for all hives
const manager = new MultiHiveRegistryManager('MyApp');

// Write to specific hive
await manager.readFromHive('software', 'Version');

// Write to all hives simultaneously
await manager.writeToAllHives('SyncKey', 'value');

// Read from first available hive
const result = await manager.readFromFirstAvailable('ConfigKey');
// Returns: { value: 'config_value', hive: 'software' }

// Delete from all hives
await manager.deleteFromAllHives('OldKey');

// Get all storage instances
const storages = manager.getStorages();
```

### Using Factory Pattern

```javascript
const { RegistryStorageFactory, RegistryHive } = require('./registry-storage-variants');

// Create single variant
const storage = RegistryStorageFactory.createStorage(
  RegistryHive.HKLM_SOFTWARE,
  'MyApp'
);

// Create all variants at once
const variants = RegistryStorageFactory.createAllVariants('MyApp');

// variants is a Map with keys: 'software', 'currentUser', 'currentVersion', 'system'
for (const [name, storage] of variants) {
  console.log(`${name}: ${storage.hive}`);
}
```

## Hive Selection Guide

| Use Case | Recommended Hive | Reason |
|----------|-----------------|--------|
| Global app settings | HKLM Software | Visible to all users |
| User preferences | HKEY_CURRENT_USER | Per-user isolation |
| OS compatibility | CurrentVersion | Standard OS settings location |
| System services | System | Service configuration |
| License info | HKLM Software | Shared across users |
| User theme | HKEY_CURRENT_USER | User-specific |
| Minimum OS version | CurrentVersion | OS detection |
| Device drivers | System | Hardware configuration |

## Key Features

### 1. Consistent Interface
All storage variants implement the same interface, making them interchangeable.

```javascript
const storages = [
  new SoftwareHiveStorage('MyApp'),
  new CurrentUserHiveStorage('Software\\MyApp'),
  new CurrentVersionHiveStorage('MyApp'),
  new SystemHiveStorage('ControlSet001\\Services\\MyApp'),
];

// All support the same operations
for (const storage of storages) {
  const value = await storage.read('Key');
  await storage.write('Key', 'value');
  const exists = await storage.exists('Key');
  await storage.delete('Key');
  const keys = await storage.listKeys();
}
```

### 2. Error Handling
All operations include comprehensive error handling with logging.

```javascript
try {
  await storage.write('Key', 'value');
} catch (error) {
  console.error('Write failed:', error.message);
}
```

### 3. Multi-Hive Coordination
The MultiHiveRegistryManager simplifies operations across multiple hives.

```javascript
// Write simultaneously to all hives (with failure tolerance)
await manager.writeToAllHives('ConfigKey', 'value');

// Read from first available hive
const result = await manager.readFromFirstAvailable('ConfigKey');
```

### 4. Factory Pattern
Easy creation of storage instances with factory methods.

```javascript
const storage = RegistryStorageFactory.createStorage(hive, subPath);
```

## Registry Paths Reference

### Software Hive
```
HKEY_LOCAL_MACHINE\Software\MyApp
HKEY_LOCAL_MACHINE\Software\MyCompany\MyApp
```

### Current User Hive
```
HKEY_CURRENT_USER\Software\MyApp
HKEY_CURRENT_USER\Software\MyCompany\MyApp
```

### CurrentVersion Hive
```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\MyApp
```

### System Hive
```
HKEY_LOCAL_MACHINE\System\ControlSet001\Services\MyService
HKEY_LOCAL_MACHINE\System\ControlSet002\Services\MyService
```

## Permission Requirements

| Hive | Read | Write | Delete |
|------|------|-------|--------|
| HKLM Software | User | Admin | Admin |
| HKEY_CURRENT_USER | User | User | User |
| CurrentVersion | User | Admin | Admin |
| System | Admin | Admin | Admin |

## Error Scenarios

### Read Non-Existent Key
Returns `null` instead of throwing error.

```javascript
const value = await storage.read('NonExistent');
// Returns: null
```

### Write Without Permissions
Throws error with descriptive message.

```javascript
try {
  await storage.write('Key', 'value');
} catch (error) {
  // Error: Access denied (insufficient permissions)
}
```

### Multiple Hive Failures
writeToAllHives() tolerates partial failures and logs warnings.

```javascript
await manager.writeToAllHives('Key', 'value');
// May log: "Failed to write to 2 hives"
// But won't throw - uses Promise.allSettled()
```

## Performance Considerations

1. **Batch Operations**: Use listKeys() to retrieve all keys at once rather than individual reads
2. **Hive Selection**: CurrentUser is faster than HKLM (no elevation needed)
3. **Multi-Hive Writes**: writeToAllHives() uses parallel operations (Promise.all)
4. **Error Recovery**: Null returns faster than exceptions for non-existent keys

## Testing

Run the comprehensive test suite:

```bash
npm test registry-storage-variants.test.js
```

Test coverage includes:
- Individual hive storage operations
- Multi-hive manager functionality
- Factory pattern creation
- Error handling and edge cases
- Interface compliance

## Examples

### Configuration Management
```javascript
const manager = new MultiHiveRegistryManager('ConfigApp');

// Store app configuration
await manager.writeToAllHives('LastUpdate', new Date().toISOString());
await manager.writeToAllHives('Version', '2.1.0');
await manager.writeToAllHives('Enabled', 'true');
```

### User Settings
```javascript
const userStorage = new CurrentUserHiveStorage('Software\\MyApp');

// Store user preferences
await userStorage.write('ColorScheme', 'Dark');
await userStorage.write('FontSize', '14');
await userStorage.write('Language', 'en-US');
```

### System Configuration
```javascript
const systemStorage = new SystemHiveStorage('ControlSet001\\Services\\MyService');

// Configure service startup
await systemStorage.write('Start', '2'); // Automatic
await systemStorage.write('Type', '20');  // Win32_ShareProcess
await systemStorage.write('DisplayName', 'My Service');
```

### Conditional Reading
```javascript
// Try multiple hives in priority order
const result = await manager.readFromFirstAvailable('ImportantSetting');

if (result) {
  console.log(`Found "${result.value}" in ${result.hive} hive`);
} else {
  console.log('Setting not found in any hive');
}
```

## Migration Between Hives

```javascript
async function migrateKey(sourceHive, targetHive, key) {
  const value = await sourceHive.read(key);
  if (value !== null) {
    await targetHive.write(key, value);
    await sourceHive.delete(key);
  }
}

const sourceSoftware = new SoftwareHiveStorage('OldApp');
const targetSoftware = new SoftwareHiveStorage('NewApp');

await migrateKey(sourceSoftware, targetSoftware, 'Version');
```

## Best Practices

1. **Use Appropriate Hive**: Select hive based on scope (user vs. system)
2. **Handle Errors Gracefully**: Always expect null returns and potential exceptions
3. **Elevate When Needed**: Request admin privileges before writing to HKLM
4. **Use Factory Pattern**: Simplifies hive selection and creation
5. **Batch Operations**: Use multiHive manager for related values
6. **Document Paths**: Comment registry paths in code for maintenance
7. **Test Permissions**: Verify expected hive access in your environment

## Compatibility

- **Node.js**: 12.0.0+
- **Platform**: Windows only (requires winreg module)
- **OS**: Windows 7+, Windows Server 2008+

## Dependencies

- `winreg`: Windows Registry access module
