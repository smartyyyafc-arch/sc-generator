# Registry Storage Implementation - Code Examples & Recipes

Complete working examples for common registry storage patterns and use cases.

## Table of Contents

1. [Basic Operations](#basic-operations)
2. [Multi-Hive Patterns](#multi-hive-patterns)
3. [Configuration Management](#configuration-management)
4. [Feature Flags](#feature-flags)
5. [Cleanup & Tracking](#cleanup--tracking)
6. [Advanced Patterns](#advanced-patterns)

---

## Basic Operations

### Example 1: Simple Read/Write Operations

```typescript
import { SoftwareHiveStorage } from './registry-storage-variants';

async function basicReadWrite() {
  const storage = new SoftwareHiveStorage('MyCompany\\MyApp');
  
  // Write a value
  await storage.write('LastLoggedInUser', 'john.doe');
  await storage.write('WindowState', 'Maximized');
  
  // Read a value
  const username = await storage.read('LastLoggedInUser');
  const windowState = await storage.read('WindowState');
  
  console.log(`User: ${username}, State: ${windowState}`);
}

basicReadWrite().catch(console.error);
```

### Example 2: Checking Key Existence

```typescript
import { CurrentUserHiveStorage } from './registry-storage-variants';

async function checkKeyExistence() {
  const storage = new CurrentUserHiveStorage('Software\\MyApp');
  
  // Check if key exists
  const hasLicenseKey = await storage.exists('LicenseKey');
  
  if (!hasLicenseKey) {
    console.log('License key not found, generating...');
    await storage.write('LicenseKey', generateNewLicenseKey());
  } else {
    const license = await storage.read('LicenseKey');
    console.log(`Using existing license: ${license}`);
  }
}

function generateNewLicenseKey(): string {
  return `KEY-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

checkKeyExistence().catch(console.error);
```

### Example 3: Deleting Registry Keys

```typescript
import { SoftwareHiveStorage } from './registry-storage-variants';

async function deleteObsoleteSettings() {
  const storage = new SoftwareHiveStorage('MyCompany\\MyApp');
  
  const obsoleteKeys = [
    'OldSettingV1',
    'DeprecatedFeature',
    'LegacyConfiguration',
  ];
  
  for (const key of obsoleteKeys) {
    if (await storage.exists(key)) {
      await storage.delete(key);
      console.log(`Deleted: ${key}`);
    }
  }
}

deleteObsoleteSettings().catch(console.error);
```

### Example 4: Listing All Keys in a Hive

```typescript
import { CurrentUserHiveStorage } from './registry-storage-variants';

async function listAndDisplayAllKeys() {
  const storage = new CurrentUserHiveStorage('Software\\MyApp\\Settings');
  
  const keys = await storage.listKeys();
  console.log(`Found ${keys.length} settings:`);
  
  for (const key of keys) {
    const value = await storage.read(key);
    console.log(`  ${key}: ${value}`);
  }
}

listAndDisplayAllKeys().catch(console.error);
```

---

## Multi-Hive Patterns

### Example 5: Global Defaults with User Overrides

```typescript
import {
  SoftwareHiveStorage,
  CurrentUserHiveStorage,
  RegistryHive,
} from './registry-storage-variants';

class SettingsManager {
  private globalStorage: SoftwareHiveStorage;
  private userStorage: CurrentUserHiveStorage;
  
  constructor(appName: string) {
    this.globalStorage = new SoftwareHiveStorage(appName);
    this.userStorage = new CurrentUserHiveStorage(`Software\\${appName}`);
  }
  
  async getSetting(key: string): Promise<string | null> {
    // Try user override first (HKEY_CURRENT_USER)
    let value = await this.userStorage.read(key);
    if (value !== null) {
      return value;
    }
    
    // Fall back to global default (HKEY_LOCAL_MACHINE)
    value = await this.globalStorage.read(key);
    return value;
  }
  
  async setSetting(key: string, value: string, global: boolean = false) {
    const storage = global ? this.globalStorage : this.userStorage;
    await storage.write(key, value);
  }
  
  async restoreDefault(key: string) {
    // Remove user override, falls back to global
    await this.userStorage.delete(key);
  }
}

// Usage
async function example5() {
  const settings = new SettingsManager('MyApp');
  
  // Get theme (will use user preference if set, otherwise global default)
  const theme = await settings.getSetting('Theme');
  console.log(`Current theme: ${theme}`);
  
  // Set global default
  await settings.setSetting('Theme', 'Light', true);
  
  // Set user preference
  await settings.setSetting('Theme', 'Dark', false);
  
  // Restore to global default
  await settings.restoreDefault('Theme');
}

example5().catch(console.error);
```

### Example 6: Reading from All Hives with Priority

```typescript
import { MultiHiveRegistryManager } from './registry-storage-variants';

async function findSettingInAllHives() {
  const manager = new MultiHiveRegistryManager('MyApp');
  const settingKey = 'DatabaseConnection';
  
  // Read from first available hive (priority order: software, currentUser, currentVersion, system)
  const result = await manager.readFromFirstAvailable(settingKey);
  
  if (result) {
    console.log(`Found "${settingKey}" in ${result.hive} hive: ${result.value}`);
  } else {
    console.log(`Setting not found in any hive`);
  }
}

findSettingInAllHives().catch(console.error);
```

### Example 7: Writing to All Hives for Redundancy

```typescript
import { MultiHiveRegistryManager } from './registry-storage-variants';

async function storeRedundantly() {
  const manager = new MultiHiveRegistryManager('MyApp');
  
  // Critical data to be stored in all hives
  const criticalSettings = {
    LicenseKey: 'ABC123-XYZ789',
    ActivationCode: 'PROD-2026',
    ExpirDate: '2027-12-31',
  };
  
  console.log('Storing critical settings in all hives...');
  
  for (const [key, value] of Object.entries(criticalSettings)) {
    await manager.writeToAllHives(key, value);
    console.log(`✓ Stored ${key}`);
  }
  
  // Verify by reading from first available
  for (const key of Object.keys(criticalSettings)) {
    const result = await manager.readFromFirstAvailable(key);
    if (result) {
      console.log(`✓ Verified ${key} from ${result.hive}`);
    }
  }
}

storeRedundantly().catch(console.error);
```

---

## Configuration Management

### Example 8: Application Configuration Class

```typescript
import {
  SoftwareHiveStorage,
  CurrentUserHiveStorage,
  RegistryHive,
} from './registry-storage-variants';

interface AppConfig {
  version: string;
  installPath: string;
  theme: string;
  autoUpdate: boolean;
  lastRunTime: string;
}

class ApplicationConfiguration {
  private globalStorage: SoftwareHiveStorage;
  private userStorage: CurrentUserHiveStorage;
  private cache: Map<string, string> = new Map();
  private defaultConfig: Partial<AppConfig>;
  
  constructor(appName: string, defaults?: Partial<AppConfig>) {
    this.globalStorage = new SoftwareHiveStorage(appName);
    this.userStorage = new CurrentUserHiveStorage(`Software\\${appName}`);
    this.defaultConfig = defaults || {};
  }
  
  async initialize(): Promise<void> {
    // Set up defaults if not already configured
    if (!await this.globalStorage.exists('Version')) {
      await this.globalStorage.write('Version', this.defaultConfig.version || '1.0.0');
      await this.globalStorage.write('InstallPath', this.defaultConfig.installPath || 'C:\\Program Files\\App');
    }
    
    if (!await this.userStorage.exists('Theme')) {
      await this.userStorage.write('Theme', this.defaultConfig.theme || 'Light');
      await this.userStorage.write('AutoUpdate', String(this.defaultConfig.autoUpdate ?? true));
    }
  }
  
  async getConfig(): Promise<AppConfig> {
    return {
      version: await this.getSetting('Version') || '1.0.0',
      installPath: await this.getSetting('InstallPath') || 'C:\\Program Files\\App',
      theme: await this.getSetting('Theme') || 'Light',
      autoUpdate: (await this.getSetting('AutoUpdate') || 'true') === 'true',
      lastRunTime: await this.getSetting('LastRunTime') || new Date().toISOString(),
    };
  }
  
  private async getSetting(key: string): Promise<string | null> {
    // Check cache first
    if (this.cache.has(key)) {
      return this.cache.get(key) || null;
    }
    
    // Try user setting first
    let value = await this.userStorage.read(key);
    
    // Fall back to global setting
    if (value === null) {
      value = await this.globalStorage.read(key);
    }
    
    // Cache the result
    if (value !== null) {
      this.cache.set(key, value);
    }
    
    return value;
  }
  
  async updateSetting(key: string, value: string, isGlobal: boolean = false) {
    const storage = isGlobal ? this.globalStorage : this.userStorage;
    await storage.write(key, value);
    this.cache.set(key, value); // Update cache
  }
  
  clearCache() {
    this.cache.clear();
  }
}

// Usage
async function example8() {
  const config = new ApplicationConfiguration('MyApp', {
    version: '2.0.0',
    installPath: 'C:\\Program Files\\MyApp',
    theme: 'Dark',
    autoUpdate: true,
  });
  
  await config.initialize();
  const appConfig = await config.getConfig();
  
  console.log('Application Configuration:');
  console.log(JSON.stringify(appConfig, null, 2));
  
  // Update a setting
  await config.updateSetting('Theme', 'Dark');
  
  // Clear cache when settings might have changed externally
  config.clearCache();
}

example8().catch(console.error);
```

### Example 9: Configuration Backup and Restore

```typescript
import { MultiHiveRegistryManager } from './registry-storage-variants';
import * as fs from 'fs';

class ConfigurationBackup {
  private manager: MultiHiveRegistryManager;
  
  constructor(appName: string) {
    this.manager = new MultiHiveRegistryManager(appName);
  }
  
  async backup(filename: string): Promise<void> {
    const storages = this.manager.getStorages();
    const backup: Record<string, Record<string, string>> = {};
    
    for (const [hiveName, storage] of Object.entries(storages)) {
      backup[hiveName] = {};
      
      const keys = await storage.listKeys();
      for (const key of keys) {
        const value = await storage.read(key);
        if (value !== null) {
          backup[hiveName][key] = value;
        }
      }
    }
    
    fs.writeFileSync(filename, JSON.stringify(backup, null, 2));
    console.log(`Configuration backed up to ${filename}`);
  }
  
  async restore(filename: string): Promise<void> {
    if (!fs.existsSync(filename)) {
      throw new Error(`Backup file not found: ${filename}`);
    }
    
    const backup = JSON.parse(fs.readFileSync(filename, 'utf-8'));
    const storages = this.manager.getStorages();
    
    for (const [hiveName, settings] of Object.entries(backup)) {
      const storage = storages[hiveName];
      if (!storage) continue;
      
      for (const [key, value] of Object.entries(settings as Record<string, string>)) {
        await storage.write(key, value);
      }
    }
    
    console.log(`Configuration restored from ${filename}`);
  }
}

// Usage
async function example9() {
  const backup = new ConfigurationBackup('MyApp');
  
  // Create backup
  await backup.backup('config-backup.json');
  
  // Later, restore from backup
  await backup.restore('config-backup.json');
}

example9().catch(console.error);
```

---

## Feature Flags

### Example 10: Feature Flag Manager

```typescript
import {
  SoftwareHiveStorage,
  CurrentUserHiveStorage,
} from './registry-storage-variants';

class FeatureFlagManager {
  private globalStorage: SoftwareHiveStorage;
  private userStorage: CurrentUserHiveStorage;
  private cache: Map<string, boolean> = new Map();
  
  constructor(appName: string) {
    this.globalStorage = new SoftwareHiveStorage(`${appName}\\Features`);
    this.userStorage = new CurrentUserHiveStorage(`Software\\${appName}\\Features`);
  }
  
  async isEnabled(featureName: string, userId?: string): Promise<boolean> {
    const cacheKey = `${featureName}:${userId || 'global'}`;
    
    // Check cache
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }
    
    let enabled = false;
    
    // User-specific override (highest priority)
    if (userId) {
      const userFeatureKey = `${featureName}_${userId}`;
      const value = await this.userStorage.read(userFeatureKey);
      if (value !== null) {
        enabled = value === 'true';
        this.cache.set(cacheKey, enabled);
        return enabled;
      }
    }
    
    // User global override
    let value = await this.userStorage.read(featureName);
    if (value !== null) {
      enabled = value === 'true';
      this.cache.set(cacheKey, enabled);
      return enabled;
    }
    
    // Global default
    value = await this.globalStorage.read(featureName);
    if (value !== null) {
      enabled = value === 'true';
    }
    
    this.cache.set(cacheKey, enabled);
    return enabled;
  }
  
  async setGlobalFlag(featureName: string, enabled: boolean): Promise<void> {
    await this.globalStorage.write(featureName, String(enabled));
    this.cache.clear(); // Invalidate cache
  }
  
  async setUserFlag(featureName: string, enabled: boolean, userId?: string): Promise<void> {
    const key = userId ? `${featureName}_${userId}` : featureName;
    await this.userStorage.write(key, String(enabled));
    this.cache.clear(); // Invalidate cache
  }
  
  async removeUserFlag(featureName: string, userId?: string): Promise<void> {
    const key = userId ? `${featureName}_${userId}` : featureName;
    await this.userStorage.delete(key);
    this.cache.clear(); // Invalidate cache
  }
}

// Usage
async function example10() {
  const flags = new FeatureFlagManager('MyApp');
  
  // Set global defaults
  await flags.setGlobalFlag('BetaFeatures', false);
  await flags.setGlobalFlag('AnalyticsEnabled', true);
  await flags.setGlobalFlag('DarkModeSupport', true);
  
  // Override for specific user
  await flags.setUserFlag('BetaFeatures', true, 'user123');
  
  // Check feature status
  const isBetaEnabled = await flags.isEnabled('BetaFeatures', 'user123');
  console.log(`Beta features for user123: ${isBetaEnabled}`); // true
  
  const isAnalyticsEnabled = await flags.isEnabled('AnalyticsEnabled', 'user456');
  console.log(`Analytics for user456: ${isAnalyticsEnabled}`); // true (global default)
}

example10().catch(console.error);
```

### Example 11: A/B Testing with Feature Flags

```typescript
import { SoftwareHiveStorage } from './registry-storage-variants';

class ABTestingManager {
  private storage: SoftwareHiveStorage;
  
  constructor(appName: string) {
    this.storage = new SoftwareHiveStorage(`${appName}\\ABTests`);
  }
  
  async enrollUser(userId: string, testName: string, variant: 'A' | 'B'): Promise<void> {
    const enrollmentKey = `${testName}_${userId}`;
    await this.storage.write(enrollmentKey, variant);
    console.log(`Enrolled ${userId} in ${testName} (variant ${variant})`);
  }
  
  async getVariant(userId: string, testName: string): Promise<'A' | 'B' | null> {
    const enrollmentKey = `${testName}_${userId}`;
    const value = await this.storage.read(enrollmentKey);
    return (value === 'A' || value === 'B') ? value : null;
  }
  
  async randomlyAssign(userId: string, testName: string): Promise<'A' | 'B'> {
    const existing = await this.getVariant(userId, testName);
    if (existing) return existing;
    
    // Randomly assign to A or B
    const variant: 'A' | 'B' = Math.random() < 0.5 ? 'A' : 'B';
    await this.enrollUser(userId, testName, variant);
    return variant;
  }
  
  async getTestMetadata(testName: string) {
    const startKey = `${testName}_Start`;
    const endKey = `${testName}_End`;
    
    return {
      start: await this.storage.read(startKey),
      end: await this.storage.read(endKey),
    };
  }
}

// Usage
async function example11() {
  const testing = new ABTestingManager('MyApp');
  
  // Start test
  await testing.enrollUser('user123', 'UIRevamp', 'A');
  await testing.enrollUser('user456', 'UIRevamp', 'B');
  
  // Get variant for user
  const variant = await testing.getVariant('user123', 'UIRevamp');
  console.log(`User123 is in variant ${variant}`);
  
  // Random assignment
  const assigned = await testing.randomlyAssign('user789', 'UIRevamp');
  console.log(`User789 randomly assigned to variant ${assigned}`);
}

example11().catch(console.error);
```

---

## Cleanup & Tracking

### Example 12: Temporary Configuration with Automatic Cleanup

```typescript
import {
  RegistryCleanupHandler,
  RegistryHive,
} from './registry-cleanup-handler';
import { SoftwareHiveStorage } from './registry-storage-variants';

async function temporaryConfiguration() {
  const handler = new RegistryCleanupHandler({
    verbose: true,
    trackOriginalValues: true,
  });
  
  handler.startTracking();
  
  try {
    const storage = new SoftwareHiveStorage('MyApp\\Temp');
    
    // Make temporary changes
    await storage.write('DebugMode', 'true');
    await storage.write('VerboseLogging', 'true');
    
    // Track these changes
    handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'DebugMode');
    handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'VerboseLogging');
    
    console.log('Running with temporary settings...');
    // Do work here
    
  } finally {
    // Automatic cleanup
    const result = await handler.executeCleanup();
    console.log(`Cleaned up ${result.entriesCleaned} entries`);
    handler.stopTracking();
  }
}

temporaryConfiguration().catch(console.error);
```

### Example 13: Cleanup with Context Manager

```typescript
import { withCleanupContext } from './registry-cleanup-handler';
import { CurrentUserHiveStorage } from './registry-storage-variants';

async function runTestWithCleanup() {
  const { result, cleanup } = await withCleanupContext(
    async (handler) => {
      const storage = new CurrentUserHiveStorage('Software\\MyApp\\Testing');
      
      // Write test configuration
      await storage.write('TestMode', 'true');
      await storage.write('MockData', 'enabled');
      
      handler.addEntry(
        'HKEY_CURRENT_USER',
        'TestMode',
        null // Indicating new key
      );
      
      // Run test
      console.log('Test running with temporary configuration...');
      
      return {
        testsPassed: 10,
        testsFailed: 0,
      };
    },
    { verbose: true, trackOriginalValues: true }
  );
  
  console.log('Test Results:', result);
  console.log('Cleanup Info:', cleanup);
}

runTestWithCleanup().catch(console.error);
```

### Example 14: Cleanup Statistics and Export

```typescript
import { RegistryCleanupHandler, RegistryHive } from './registry-cleanup-handler';
import * as fs from 'fs';

async function trackAndReport() {
  const handler = new RegistryCleanupHandler({
    verbose: true,
  });
  
  handler.startTracking();
  
  try {
    // Simulate various operations
    handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'AppVersion');
    handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'UserPreference1');
    handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'UserPreference2');
    handler.addEntry(RegistryHive.CURRENT_VERSION, 'CompatFlag');
    
    // Get statistics
    const stats = handler.getStatistics();
    console.log('Cleanup Statistics:');
    console.log(`  Total entries tracked: ${stats.totalEntries}`);
    console.log(`  Entries by hive:`, stats.entriesByHive);
    console.log(`  Oldest entry: ${stats.oldestEntry}`);
    console.log(`  Newest entry: ${stats.newestEntry}`);
    
    // Export log
    const logJson = handler.exportLog();
    fs.writeFileSync('registry-changes.json', logJson);
    console.log('Cleanup log exported to registry-changes.json');
    
    // Execute cleanup
    const result = await handler.executeCleanup();
    console.log(`Cleanup Result:
      Success: ${result.success}
      Cleaned: ${result.entriesCleaned}/${stats.totalEntries}
      Time: ${result.totalTime}ms
      Errors: ${result.errors.length}`);
    
  } finally {
    handler.stopTracking();
  }
}

trackAndReport().catch(console.error);
```

---

## Advanced Patterns

### Example 15: Configuration Versioning and Migration

```typescript
import { SoftwareHiveStorage } from './registry-storage-variants';

const CURRENT_SCHEMA_VERSION = 2;

class VersionedConfiguration {
  private storage: SoftwareHiveStorage;
  
  constructor(appName: string) {
    this.storage = new SoftwareHiveStorage(appName);
  }
  
  async initialize(): Promise<void> {
    const version = await this.storage.read('SchemaVersion');
    
    if (version === null) {
      // First run, initialize with current version
      await this.storage.write('SchemaVersion', String(CURRENT_SCHEMA_VERSION));
      await this.initializeDefaults();
    } else {
      const numVersion = parseInt(version, 10);
      if (numVersion < CURRENT_SCHEMA_VERSION) {
        await this.migrate(numVersion, CURRENT_SCHEMA_VERSION);
      }
    }
  }
  
  private async initializeDefaults(): Promise<void> {
    await this.storage.write('DatabaseHost', 'localhost');
    await this.storage.write('DatabasePort', '5432');
    await this.storage.write('MaxConnections', '10');
  }
  
  private async migrate(from: number, to: number): Promise<void> {
    console.log(`Migrating configuration from v${from} to v${to}`);
    
    if (from < 2) {
      // Migration from v1 to v2
      const oldDb = await this.storage.read('OldDatabasePath');
      if (oldDb) {
        // Rename to new format
        await this.storage.write('DatabasePath', oldDb);
        await this.storage.delete('OldDatabasePath');
      }
    }
    
    // Update schema version
    await this.storage.write('SchemaVersion', String(CURRENT_SCHEMA_VERSION));
    console.log('Migration complete');
  }
}

// Usage
async function example15() {
  const config = new VersionedConfiguration('MyApp');
  await config.initialize(); // Handles migration if needed
}

example15().catch(console.error);
```

### Example 16: Secure Settings Wrapper

```typescript
import { CurrentUserHiveStorage } from './registry-storage-variants';

class SecureSettingsManager {
  private storage: CurrentUserHiveStorage;
  private sensitiveKeys = new Set(['Password', 'Token', 'Secret', 'Key']);
  
  constructor(appName: string) {
    this.storage = new CurrentUserHiveStorage(`Software\\${appName}\\Secure`);
  }
  
  async setSensitive(key: string, value: string): Promise<void> {
    if (!this.isSensitive(key)) {
      throw new Error(`Key ${key} is not marked as sensitive`);
    }
    
    // In production, use DPAPI (Data Protection API) for encryption
    const encrypted = this.encryptValue(value);
    await this.storage.write(key, encrypted);
    console.log(`Stored secure setting: ${key}`);
  }
  
  async getSensitive(key: string): Promise<string | null> {
    if (!this.isSensitive(key)) {
      throw new Error(`Key ${key} is not marked as sensitive`);
    }
    
    const encrypted = await this.storage.read(key);
    if (encrypted === null) return null;
    
    return this.decryptValue(encrypted);
  }
  
  private isSensitive(key: string): boolean {
    return this.sensitiveKeys.has(key) || key.toLowerCase().includes('secret');
  }
  
  private encryptValue(value: string): string {
    // TODO: Use DPAPI or other encryption
    // This is just a placeholder
    return Buffer.from(value).toString('base64');
  }
  
  private decryptValue(encrypted: string): string {
    // TODO: Use DPAPI or other decryption
    // This is just a placeholder
    return Buffer.from(encrypted, 'base64').toString();
  }
}

// Usage
async function example16() {
  const secure = new SecureSettingsManager('MyApp');
  
  // Store sensitive data
  await secure.setSensitive('APIToken', 'secret-token-12345');
  
  // Retrieve sensitive data
  const token = await secure.getSensitive('APIToken');
  console.log(`Retrieved token: ${token?.substring(0, 6)}...`);
}

example16().catch(console.error);
```

### Example 17: Registry Watcher with Polling

```typescript
import { SoftwareHiveStorage } from './registry-storage-variants';

class RegistryWatcher {
  private storage: SoftwareHiveStorage;
  private cache: Map<string, string> = new Map();
  private watchers: Map<string, (newValue: string | null) => void> = new Map();
  private isWatching: boolean = false;
  
  constructor(appName: string) {
    this.storage = new SoftwareHiveStorage(appName);
  }
  
  async watch(key: string, callback: (newValue: string | null) => void): Promise<void> {
    this.watchers.set(key, callback);
    
    if (!this.isWatching) {
      this.startWatching();
    }
  }
  
  private startWatching(): void {
    if (this.isWatching) return;
    
    this.isWatching = true;
    this.pollRegistry();
  }
  
  private async pollRegistry(): Promise<void> {
    while (this.isWatching) {
      for (const [key, callback] of this.watchers) {
        const newValue = await this.storage.read(key);
        const oldValue = this.cache.get(key);
        
        if (newValue !== oldValue) {
          this.cache.set(key, newValue || '');
          callback(newValue);
        }
      }
      
      // Poll every 5 seconds
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
  
  stopWatching(): void {
    this.isWatching = false;
  }
}

// Usage
async function example17() {
  const watcher = new RegistryWatcher('MyApp');
  
  // Watch for configuration changes
  await watcher.watch('ConfigurationVersion', (newValue) => {
    console.log(`Configuration changed to version: ${newValue}`);
  });
  
  // Watch for feature flag changes
  await watcher.watch('FeatureFlag_DarkMode', (enabled) => {
    console.log(`Dark mode is now: ${enabled}`);
  });
  
  // Stop watching after 60 seconds (for example)
  setTimeout(() => {
    watcher.stopWatching();
    console.log('Stopped watching registry');
  }, 60000);
}

example17().catch(console.error);
```

---

## Summary

This document provides practical, copy-paste-ready examples for:

- **Basic operations**: Read, write, delete, exists, list
- **Multi-hive patterns**: Defaults, overrides, redundancy
- **Configuration management**: Classes, backup/restore
- **Feature flags**: Manager, A/B testing
- **Cleanup**: Tracking, context managers, statistics
- **Advanced patterns**: Versioning, security, watching

Each example is self-contained and demonstrates best practices for registry storage operations in Windows applications.
