# Registry Storage Implementation - Technical Documentation

## Overview

This document provides comprehensive technical documentation for the Windows Registry storage implementation, including key hierarchy patterns, architecture, usage examples, and best practices.

## Table of Contents

1. [Architecture & Design](#architecture--design)
2. [Key Hierarchy Structure](#key-hierarchy-structure)
3. [Storage Variants](#storage-variants)
4. [Core Interfaces](#core-interfaces)
5. [Implementation Details](#implementation-details)
6. [Key Hierarchy Examples](#key-hierarchy-examples)
7. [Cleanup & Tracking](#cleanup--tracking)
8. [Best Practices](#best-practices)
9. [Integration Patterns](#integration-patterns)

---

## Architecture & Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 Application Layer                               │
├─────────────────────────────────────────────────────────────────┤
│              MultiHiveRegistryManager                           │
│  (Coordinates operations across multiple hives)                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┬─────────────────┬───────────────┬─────────┐   │
│  │ Software     │ CurrentUser     │ CurrentVersion│ System  │   │
│  │ Hive         │ Hive            │ Hive          │ Hive    │   │
│  │ Storage      │ Storage         │ Storage       │ Storage │   │
│  └──────────────┴─────────────────┴───────────────┴─────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                  IRegistryStorage Interface                     │
├─────────────────────────────────────────────────────────────────┤
│              Windows Registry (via winreg library)              │
│  ┌──────────────┬─────────────────┬───────────────┬─────────┐   │
│  │ HKLM         │ HKCU            │ HKLM          │ HKLM    │   │
│  │ Software     │                 │ CurrentVer    │ System  │   │
│  └──────────────┴─────────────────┴───────────────┴─────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Design Patterns Used

1. **Factory Pattern**: `RegistryStorageFactory` creates appropriate storage variants
2. **Strategy Pattern**: Each hive storage is a strategy implementation
3. **Decorator Pattern**: `withAutoCleanup` decorator for automatic cleanup
4. **Context Manager Pattern**: `withCleanupContext` for scoped cleanup
5. **Observer Pattern**: Cleanup tracking system logs modifications

---

## Key Hierarchy Structure

### Registry Hive Enumeration

```typescript
enum RegistryHive {
  HKLM_SOFTWARE = 'HKEY_LOCAL_MACHINE\\Software',
  HKEY_CURRENT_USER = 'HKEY_CURRENT_USER',
  CURRENT_VERSION = 'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion',
  HKLM_SYSTEM = 'HKEY_LOCAL_MACHINE\\System',
  HKEY_CLASSES_ROOT = 'HKEY_CLASSES_ROOT',
  HKEY_CURRENT_CONFIG = 'HKEY_CURRENT_CONFIG',
}
```

### Key Hierarchy Levels

The registry uses a hierarchical key structure with the following levels:

```
Hive Root
  └── Subkey Level 1 (Vendor/Company)
        └── Subkey Level 2 (Application Name)
              └── Subkey Level 3 (Component/Feature)
                    └── Value Name (Registry Key)
```

---

## Key Hierarchy Examples

### Example 1: Application Settings Hierarchy

**Hive**: HKEY_LOCAL_MACHINE\Software

**Full Path**: HKEY_LOCAL_MACHINE\Software\MyCompany\MyApplication\Settings

```
HKEY_LOCAL_MACHINE
  └── Software
        └── MyCompany                           [Organization]
              └── MyApplication                 [Application]
                    └── Settings                [Component]
                          ├── Version: "2.1.0"
                          ├── Publisher: "MyCompany"
                          ├── InstallDate: "2026-06-29T10:30:00Z"
                          └── InstallPath: "C:\\Program Files\\MyApplication"
```

**TypeScript Implementation**:

```typescript
const softwareStorage = new SoftwareHiveStorage('MyCompany\\MyApplication\\Settings');

// Write application settings
await softwareStorage.write('Version', '2.1.0');
await softwareStorage.write('Publisher', 'MyCompany');
await softwareStorage.write('InstallDate', new Date().toISOString());
await softwareStorage.write('InstallPath', 'C:\\Program Files\\MyApplication');

// Read application settings
const version = await softwareStorage.read('Version');
```

### Example 2: User Preferences Hierarchy

**Hive**: HKEY_CURRENT_USER

**Full Path**: HKEY_CURRENT_USER\Software\MyCompany\MyApplication\Preferences

```
HKEY_CURRENT_USER
  └── Software
        └── MyCompany                           [Organization]
              └── MyApplication                 [Application]
                    └── Preferences             [Component]
                          ├── Theme: "Dark"
                          ├── Language: "en-US"
                          ├── TimeFormat: "24h"
                          ├── DateFormat: "YYYY-MM-DD"
                          └── AutoUpdate: "true"
```

**TypeScript Implementation**:

```typescript
const userStorage = new CurrentUserHiveStorage('Software\\MyCompany\\MyApplication\\Preferences');

// Set default preferences
const defaults = {
  Theme: 'Light',
  Language: 'en-US',
  TimeFormat: '24h',
  DateFormat: 'YYYY-MM-DD',
  FontSize: '12',
};

for (const [key, value] of Object.entries(defaults)) {
  const existing = await userStorage.read(key);
  if (existing === null) {
    await userStorage.write(key, value);
  }
}
```

### Example 3: Feature Flags Hierarchy

**Hive**: Multiple hives (global defaults in Software, user overrides in CurrentUser)

```
HKEY_LOCAL_MACHINE\Software
  └── MyCompany
        └── MyApplication
              └── Features                      [Global Features]
                    ├── Feature_BetaFeatures: "false"
                    ├── Feature_AnalyticsEnabled: "true"
                    ├── Feature_CloudSync: "false"
                    └── Feature_DarkModeSupport: "true"

HKEY_CURRENT_USER\Software
  └── MyCompany
        └── MyApplication
              └── Features                      [User Overrides]
                    ├── Feature_DarkModeSupport: "true"
                    └── Feature_BetaFeatures: "true"
```

**TypeScript Implementation**:

```typescript
const manager = new MultiHiveRegistryManager('MyCompany\\MyApplication');
const softwareStorage = manager.getStorageByHive('software');
const userStorage = manager.getStorageByHive('currentUser');

// Set global feature flags
const globalFeatures = {
  BetaFeatures: 'false',
  AnalyticsEnabled: 'true',
  CloudSync: 'false',
  DarkModeSupport: 'true',
};

for (const [key, value] of Object.entries(globalFeatures)) {
  await softwareStorage.write(`Feature_${key}`, value);
}

// Override with user preferences
async function getFeatureFlag(featureName: string): Promise<boolean> {
  // Try user override first
  let value = await userStorage.read(`Feature_${featureName}`);
  if (value !== null) return value === 'true';
  
  // Fall back to global setting
  value = await softwareStorage.read(`Feature_${featureName}`);
  return value === 'true';
}

// Usage
const isDarkModeEnabled = await getFeatureFlag('DarkModeSupport');
```

### Example 4: Windows Service Configuration Hierarchy

**Hive**: HKEY_LOCAL_MACHINE\System

**Full Path**: HKEY_LOCAL_MACHINE\System\ControlSet001\Services\MyService\Parameters

```
HKEY_LOCAL_MACHINE
  └── System
        └── ControlSet001                       [Active Control Set]
              └── Services                      [All Services]
                    └── MyService               [Service Name]
                          ├── DisplayName: "My Custom Service"
                          ├── Description: "Handles background tasks"
                          ├── ImagePath: "%SystemRoot%\\System32\\MyService.exe"
                          ├── Start: "2"        [Automatic]
                          ├── Type: "20"        [Win32_ShareProcess]
                          ├── ErrorControl: "1" [Normal]
                          └── Parameters
                                ├── ServiceDll: "%SystemRoot%\\System32\\MyService.dll"
                                └── ConfigValue: "configuration data"
```

**TypeScript Implementation**:

```typescript
const serviceStorage = new SystemHiveStorage('ControlSet001\\Services\\MyService');

const serviceConfig = {
  DisplayName: 'My Custom Service',
  Description: 'Handles important background tasks',
  Start: '2',        // 2 = Automatic, 3 = Manual, 4 = Disabled
  Type: '20',        // 20 = Win32_ShareProcess
  ErrorControl: '1', // 1 = Normal
  ServiceDll: '%SystemRoot%\\System32\\MyService.dll',
};

for (const [key, value] of Object.entries(serviceConfig)) {
  await serviceStorage.write(key, value);
}
```

### Example 5: Nested Component Configuration Hierarchy

**Hive**: HKEY_LOCAL_MACHINE\Software

**Full Path**: HKEY_LOCAL_MACHINE\Software\MyCompany\MyApplication\Components\Database

```
HKEY_LOCAL_MACHINE
  └── Software
        └── MyCompany
              └── MyApplication
                    ├── Settings                [Application Settings]
                    │     ├── Version: "2.1.0"
                    │     └── InstallPath: "..."
                    │
                    ├── Components              [Component Registry]
                    │     └── Database          [Database Component]
                    │           ├── Host: "localhost"
                    │           ├── Port: "5432"
                    │           ├── Username: "dbuser"
                    │           ├── PoolSize: "10"
                    │           └── Timeout: "30000"
                    │
                    ├── Logging                 [Logging Configuration]
                    │     ├── Level: "INFO"
                    │     ├── Format: "JSON"
                    │     └── Path: "C:\\Logs\\MyApp"
                    │
                    └── Security                [Security Settings]
                          ├── SSLEnabled: "true"
                          ├── TLSVersion: "1.3"
                          └── CertPath: "C:\\Certs\\server.pfx"
```

**TypeScript Implementation**:

```typescript
// Create storage for each component
const databaseStorage = new SoftwareHiveStorage(
  'MyCompany\\MyApplication\\Components\\Database'
);
const loggingStorage = new SoftwareHiveStorage(
  'MyCompany\\MyApplication\\Logging'
);
const securityStorage = new SoftwareHiveStorage(
  'MyCompany\\MyApplication\\Security'
);

// Database configuration
const dbConfig = {
  Host: 'localhost',
  Port: '5432',
  Username: 'dbuser',
  PoolSize: '10',
  Timeout: '30000',
};

for (const [key, value] of Object.entries(dbConfig)) {
  await databaseStorage.write(key, value);
}

// Logging configuration
const logConfig = {
  Level: 'INFO',
  Format: 'JSON',
  Path: 'C:\\Logs\\MyApp',
};

for (const [key, value] of Object.entries(logConfig)) {
  await loggingStorage.write(key, value);
}

// Security configuration
const secConfig = {
  SSLEnabled: 'true',
  TLSVersion: '1.3',
  CertPath: 'C:\\Certs\\server.pfx',
};

for (const [key, value] of Object.entries(secConfig)) {
  await securityStorage.write(key, value);
}
```

### Example 6: Version and Compatibility Registry

**Hive**: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion

**Full Path**: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\MyApplication

```
HKEY_LOCAL_MACHINE
  └── Software
        └── Microsoft
              └── Windows
                    └── CurrentVersion          [Windows Version Info]
                          ├── CurrentVersion: "10.0"
                          ├── CurrentBuildNumber: "26100"
                          ├── CurrentMajorVersionNumber: "10"
                          ├── CurrentMinorVersionNumber: "0"
                          │
                          └── MyApplication     [Application Compatibility]
                                ├── CompatibilityMode: "Windows10Plus"
                                ├── LegacyMode: "false"
                                ├── ModernFeatures: "true"
                                ├── MinimumOSVersion: "10.0"
                                └── SupportedArch: "x64"
```

**TypeScript Implementation**:

```typescript
const versionStorage = new CurrentVersionHiveStorage('MyApplication');

// Detect OS version
const osVersionBase = new CurrentVersionHiveStorage('');
const version = await osVersionBase.read('CurrentVersion');
const buildNumber = await osVersionBase.read('CurrentBuildNumber');

// Set compatibility flags based on OS version
const parsedVersion = parseFloat(version || '0');
let compatMode = 'Modern';
let legacyMode = 'false';
let modernFeatures = 'false';

if (parsedVersion < 6.1) {
  compatMode = 'Legacy';
  legacyMode = 'true';
  modernFeatures = 'false';
} else if (parsedVersion >= 10.0) {
  compatMode = 'Windows10Plus';
  legacyMode = 'false';
  modernFeatures = 'true';
}

await versionStorage.write('CompatibilityMode', compatMode);
await versionStorage.write('LegacyMode', legacyMode);
await versionStorage.write('ModernFeatures', modernFeatures);
await versionStorage.write('MinimumOSVersion', '10.0');
await versionStorage.write('SupportedArch', 'x64');
```

---

## Storage Variants

### 1. SoftwareHiveStorage

**Purpose**: Store application-wide settings and software configurations

**Hive**: HKEY_LOCAL_MACHINE\Software

**Permissions Required**: Administrator privileges

**Use Cases**:
- Global application configuration
- Installation information
- Publisher and version details
- License information
- System-wide feature flags (defaults)

```typescript
const storage = new SoftwareHiveStorage('MyCompany\\MyApplication');
await storage.write('Version', '2.1.0');
await storage.write('License', 'ABC123-XYZ789');
```

### 2. CurrentUserHiveStorage

**Purpose**: Store user-specific preferences and settings

**Hive**: HKEY_CURRENT_USER

**Permissions Required**: Current user permissions only

**Use Cases**:
- User preferences and themes
- Personal settings
- User-specific feature flag overrides
- Last used values
- User session information

```typescript
const storage = new CurrentUserHiveStorage('Software\\MyCompany\\MyApplication\\Preferences');
await storage.write('Theme', 'Dark');
await storage.write('Language', 'en-US');
await storage.write('AutoUpdate', 'true');
```

### 3. CurrentVersionHiveStorage

**Purpose**: Store OS version-related and compatibility settings

**Hive**: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion

**Permissions Required**: Administrator privileges

**Use Cases**:
- OS version detection
- Compatibility mode settings
- Windows version-specific configuration
- Application compatibility information

```typescript
const storage = new CurrentVersionHiveStorage('MyApplication');
await storage.write('CompatibilityMode', 'Windows10Plus');
await storage.write('MinimumOSVersion', '10.0');
```

### 4. SystemHiveStorage

**Purpose**: Store system-level hardware profiles and service configurations

**Hive**: HKEY_LOCAL_MACHINE\System

**Permissions Required**: Administrator privileges (SYSTEM or equivalent)

**Use Cases**:
- Windows service configurations
- Hardware profile settings
- System-level device drivers
- Boot configurations
- Control sets (ControlSet001, ControlSet002)

```typescript
const storage = new SystemHiveStorage('ControlSet001\\Services\\MyService');
await storage.write('DisplayName', 'My Custom Service');
await storage.write('Start', '2'); // Automatic
```

---

## Core Interfaces

### IRegistryStorage Interface

```typescript
interface IRegistryStorage {
  hive: RegistryHive;
  
  // Read a registry value
  read(key: string): Promise<string | null>;
  
  // Write a registry value
  write(key: string, value: string): Promise<void>;
  
  // Delete a registry key
  delete(key: string): Promise<void>;
  
  // Check if a key exists
  exists(key: string): Promise<boolean>;
  
  // List all keys in this hive
  listKeys(): Promise<string[]>;
}
```

### CleanupEntry Interface

```typescript
interface CleanupEntry {
  hive: RegistryHive;           // Which hive was modified
  key: string;                  // Registry key name
  originalValue?: string | null;// Original value (for restoration)
  wasDeleted?: boolean;         // Whether key was deleted
  timestamp: Date;              // When modification occurred
}
```

### CleanupOptions Interface

```typescript
interface CleanupOptions {
  verbose?: boolean;            // Enable detailed logging
  dryRun?: boolean;             // Simulate cleanup without actual deletion
  trackOriginalValues?: boolean;// Store original values for restoration
  maxRetries?: number;          // Max attempts for cleanup operations
}
```

### CleanupResult Interface

```typescript
interface CleanupResult {
  success: boolean;             // Overall cleanup success
  entriesCleaned: number;       // Number of entries cleaned
  failedEntries: CleanupEntry[];// Entries that failed cleanup
  totalTime: number;            // Time taken in milliseconds
  errors: string[];             // Error messages
}
```

---

## Implementation Details

### MultiHiveRegistryManager

Coordinates operations across multiple registry hives:

```typescript
const manager = new MultiHiveRegistryManager(
  'MyCompany\\MyApplication',           // Software hive subpath
  'Software\\MyCompany\\MyApplication', // CurrentUser hive subpath
  'MyCompany\\MyApplication',           // CurrentVersion hive subpath
  'ControlSet001\\Services\\MyService'  // System hive subpath
);

// Write to all hives
await manager.writeToAllHives('ConfigValue', 'value123');

// Read from specific hive
const value = await manager.readFromHive('software', 'Version');

// Read from first available hive
const result = await manager.readFromFirstAvailable('ConfigValue');
if (result) {
  console.log(`Found in ${result.hive}: ${result.value}`);
}

// Delete from all hives
await manager.deleteFromAllHives('OldConfigValue');
```

### RegistryStorageFactory

Factory pattern for creating storage instances:

```typescript
// Create single storage for specific hive
const storage = RegistryStorageFactory.createStorage(
  RegistryHive.HKLM_SOFTWARE,
  'MyCompany\\MyApplication'
);

// Create all variants at once
const storages = RegistryStorageFactory.createAllVariants('MyApplication');
for (const [name, storage] of storages) {
  console.log(`${name}: ${storage.hive}`);
}
```

---

## Cleanup & Tracking

### RegistryCleanupHandler

Tracks and manages cleanup of registry modifications:

```typescript
// Create cleanup handler
const handler = new RegistryCleanupHandler({
  verbose: true,
  trackOriginalValues: true,
  maxRetries: 3,
});

// Start tracking
handler.startTracking();

// Manually add entries to track
handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TestKey', 'OriginalValue');

// Get statistics
const stats = handler.getStatistics();
console.log(`Total entries: ${stats.totalEntries}`);
console.log(`By hive:`, stats.entriesByHive);

// Execute cleanup
const result = await handler.executeCleanup();
console.log(`Cleaned: ${result.entriesCleaned}/${stats.totalEntries}`);

// Cleanup specific hive
const hiveResult = await handler.cleanupHive(RegistryHive.HKLM_SOFTWARE);

// Export/import cleanup log
const logJSON = handler.exportLog();
handler.importLog(logJSON);
```

### Automatic Cleanup with Context Manager

```typescript
const { result, cleanup } = await withCleanupContext(
  async (handler) => {
    // Code that modifies registry
    const storage = new SoftwareHiveStorage('MyApp');
    await storage.write('TestKey', 'TestValue');
    
    return 'Operation completed';
  },
  { verbose: true }
);

console.log('Result:', result);
console.log('Cleanup Info:', cleanup);
```

### Automatic Cleanup Decorator

```typescript
@withAutoCleanup({ verbose: true })
async function configureApplication() {
  const storage = new CurrentUserHiveStorage('Software\\MyApp');
  await storage.write('Setting1', 'Value1');
  await storage.write('Setting2', 'Value2');
  // Cleanup happens automatically after function execution
}
```

---

## Best Practices

### 1. Key Naming Conventions

```
// Use PascalCase for key names
Correct:   Version, InstallDate, DisplayName
Incorrect: version, install_date, displayName

// Use semantic hierarchy
Good:   CompanyName\ApplicationName\ComponentName\SettingName
Bad:    MySettings, Data, Config

// Use prefixes for feature flags
Feature_BetaMode, Feature_AnalyticsEnabled

// Use suffixes for metadata
LastUpdated, CreatedBy, UpdatedOn
```

### 2. Multi-Hive Strategy

```typescript
// Tier 1: System defaults (Software hive)
const defaults = new SoftwareHiveStorage('MyApp\\Defaults');

// Tier 2: User overrides (CurrentUser hive)
const userPrefs = new CurrentUserHiveStorage('Software\\MyApp');

// Tier 3: Fallback chain
async function getSetting(key: string): Promise<string | null> {
  // Try user preference first
  let value = await userPrefs.read(key);
  if (value !== null) return value;
  
  // Fall back to system default
  value = await defaults.read(key);
  return value;
}
```

### 3. Error Handling

```typescript
try {
  await storage.write('CriticalSetting', value);
} catch (error) {
  console.error('Failed to write setting:', error);
  // Implement fallback or user notification
}

// For reads, null indicates key doesn't exist
const value = await storage.read('OptionalSetting');
if (value === null) {
  // Use default value
  console.log('Setting not found, using default');
}
```

### 4. Performance Optimization

```typescript
// Batch operations when possible
const batchWrite = async (settings: Record<string, string>) => {
  for (const [key, value] of Object.entries(settings)) {
    await storage.write(key, value);
  }
};

// Use listKeys() to enumerate before iteration
const keys = await storage.listKeys();
const values = await Promise.all(
  keys.map(key => storage.read(key))
);

// Cache frequently accessed values
const cache = new Map<string, string>();
```

### 5. Security Considerations

```typescript
// Don't store passwords in registry (use DPAPI)
// Don't store sensitive tokens directly
// Use restricted permissions on service-related hives

// Audit critical modifications
const handler = new RegistryCleanupHandler({ trackOriginalValues: true });
handler.startTracking();
// ... operations ...
const log = handler.exportLog();
auditLogger.log('Registry modifications:', log);
```

### 6. Backward Compatibility

```typescript
// Maintain version information for schema changes
const VERSION = '1.0';
await storage.write('SchemaVersion', VERSION);

// Support migration paths
const oldValue = await legacyStorage.read('OldSettingName');
if (oldValue !== null) {
  // Migrate to new location/format
  await newStorage.write('NewSettingName', migrateValue(oldValue));
}
```

---

## Integration Patterns

### Pattern 1: Initialization with Defaults

```typescript
async function initializeApplicationSettings() {
  const storage = new SoftwareHiveStorage('MyCompany\\MyApplication');
  const userStorage = new CurrentUserHiveStorage(
    'Software\\MyCompany\\MyApplication'
  );
  
  const defaults = {
    Version: '1.0.0',
    InstallDate: new Date().toISOString(),
    UpdateCheckInterval: '86400',
  };
  
  for (const [key, value] of Object.entries(defaults)) {
    const existing = await storage.read(key);
    if (existing === null) {
      await storage.write(key, value);
    }
  }
}
```

### Pattern 2: Configuration Migration

```typescript
async function migrateConfiguration(
  source: IRegistryStorage,
  target: IRegistryStorage,
  keys: string[]
) {
  const failed: string[] = [];
  
  for (const key of keys) {
    try {
      const value = await source.read(key);
      if (value !== null) {
        await target.write(key, value);
        console.log(`Migrated: ${key}`);
      }
    } catch (error) {
      failed.push(key);
      console.error(`Failed to migrate ${key}:`, error);
    }
  }
  
  return failed;
}
```

### Pattern 3: Feature Flag Rollout

```typescript
async function isFeatureEnabled(
  featureName: string,
  userId?: string
): Promise<boolean> {
  const userStorage = new CurrentUserHiveStorage(
    `Software\\MyApp\\UserFeatures`
  );
  const globalStorage = new SoftwareHiveStorage('MyApp\\Features');
  
  // User-specific override
  if (userId) {
    const userFlag = await userStorage.read(`${featureName}_${userId}`);
    if (userFlag !== null) return userFlag === 'true';
  }
  
  // User-global override
  const userFlag = await userStorage.read(featureName);
  if (userFlag !== null) return userFlag === 'true';
  
  // System-wide default
  const globalFlag = await globalStorage.read(featureName);
  return globalFlag === 'true';
}
```

### Pattern 4: Atomic Configuration Updates

```typescript
async function updateConfigurationAtomic(
  updates: Record<string, string>,
  handler: RegistryCleanupHandler
): Promise<boolean> {
  handler.startTracking();
  
  try {
    const storage = new SoftwareHiveStorage('MyApp\\Config');
    
    for (const [key, value] of Object.entries(updates)) {
      const original = await storage.read(key);
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, key, original);
      await storage.write(key, value);
    }
    
    return true;
  } catch (error) {
    console.error('Update failed, rolling back...');
    await handler.executeCleanup();
    return false;
  }
}
```

---

## Common Patterns Summary

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Tiered Settings** | Default + Override | Global setting in Software hive, user override in CurrentUser |
| **Feature Flags** | Gradual rollout | Feature_FeatureName with boolean value |
| **Cleanup Tracking** | Temporary changes | Use handler for cleanup after operation |
| **Migration** | Configuration updates | Migrate from old keys to new location |
| **Atomic Updates** | Multiple keys | Use cleanup handler for rollback on failure |
| **Version Tracking** | Schema evolution | Store SchemaVersion for compatibility |
| **Multi-Component** | Complex apps | Separate hive paths for each component |
| **Service Config** | Windows services | System hive with ControlSet path |

---

## Summary

This registry storage implementation provides:

✓ **Multi-hive support** with four specialized variants
✓ **Flexible key hierarchy** for organized configuration
✓ **Automatic cleanup** and tracking mechanisms
✓ **Error handling** with retry logic
✓ **Factory pattern** for easy storage creation
✓ **Backup/restore** capabilities
✓ **Audit trail** via cleanup logging
✓ **Atomic operations** support with rollback

Use this documentation as a reference for implementing registry-based configuration management in Windows applications.
