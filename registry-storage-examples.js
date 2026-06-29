/**
 * Registry Storage Variants - Practical Examples
 * Real-world usage scenarios and patterns
 */

const {
  RegistryHive,
  SoftwareHiveStorage,
  CurrentUserHiveStorage,
  CurrentVersionHiveStorage,
  SystemHiveStorage,
  MultiHiveRegistryManager,
  RegistryStorageFactory,
} = require('./registry-storage-variants');

/**
 * Example 1: Application Settings Management
 * Store application configuration across multiple hives
 */
async function exampleApplicationSettings() {
  console.log('\n=== Example 1: Application Settings ===');

  const manager = new MultiHiveRegistryManager('MyApplication');

  // Global app settings in Software hive
  const softwareStorage = manager.getStorageByHive('software');
  await softwareStorage.write('Version', '2.1.0');
  await softwareStorage.write('Publisher', 'MyCompany');
  await softwareStorage.write('InstallDate', new Date().toISOString());

  // User-specific preferences in CurrentUser hive
  const userStorage = manager.getStorageByHive('currentUser');
  await userStorage.write('Theme', 'Dark');
  await userStorage.write('AutoUpdate', 'true');
  await userStorage.write('LastLoginTime', new Date().toISOString());

  // OS-related settings in CurrentVersion
  const versionStorage = manager.getStorageByHive('currentVersion');
  await versionStorage.write('MinimumOSVersion', '10.0');
  await versionStorage.write('SupportedArch', 'x64');

  console.log('Application settings stored in all hives');

  // Retrieve values
  const appVersion = await softwareStorage.read('Version');
  const userTheme = await userStorage.read('Theme');
  const minOS = await versionStorage.read('MinimumOSVersion');

  console.log(`App Version: ${appVersion}`);
  console.log(`User Theme: ${userTheme}`);
  console.log(`Min OS: ${minOS}`);
}

/**
 * Example 2: User Preferences with Defaults
 * Fallback chain for user preferences with defaults
 */
async function exampleUserPreferencesWithDefaults() {
  console.log('\n=== Example 2: User Preferences with Defaults ===');

  const userStorage = new CurrentUserHiveStorage('Software\\MyApp\\Settings');
  const defaultPreferences = {
    Theme: 'Light',
    Language: 'en-US',
    TimeFormat: '24h',
    DateFormat: 'YYYY-MM-DD',
    FontSize: '12',
  };

  // Set defaults if not already set
  for (const [key, defaultValue] of Object.entries(defaultPreferences)) {
    const existing = await userStorage.read(key);
    if (existing === null) {
      await userStorage.write(key, defaultValue);
      console.log(`Set default ${key}: ${defaultValue}`);
    }
  }

  // Read all preferences
  const preferences = {};
  for (const key of Object.keys(defaultPreferences)) {
    preferences[key] = await userStorage.read(key);
  }

  console.log('User Preferences:', preferences);
}

/**
 * Example 3: Multi-Hive Redundancy
 * Store critical data in multiple hives for redundancy
 */
async function exampleMultiHiveRedundancy() {
  console.log('\n=== Example 3: Multi-Hive Redundancy ===');

  const manager = new MultiHiveRegistryManager('CriticalApp');
  const criticalData = {
    LicenseKey: 'ABC123-DEF456-GHI789',
    ActivationDate: new Date().toISOString(),
    ExpiryDate: '2027-12-31',
  };

  // Write critical data to all hives
  for (const [key, value] of Object.entries(criticalData)) {
    await manager.writeToAllHives(key, value);
    console.log(`Stored ${key} in all hives`);
  }

  // Read from first available hive
  for (const key of Object.keys(criticalData)) {
    const result = await manager.readFromFirstAvailable(key);
    if (result) {
      console.log(`Retrieved ${key} from ${result.hive}: ${result.value}`);
    }
  }
}

/**
 * Example 4: Feature Flags across Hives
 * Manage feature flags with hive-specific overrides
 */
async function exampleFeatureFlags() {
  console.log('\n=== Example 4: Feature Flags ===');

  const manager = new MultiHiveRegistryManager('FeatureApp');

  const features = {
    BetaFeatures: 'false',
    AnalyticsEnabled: 'true',
    CloudSync: 'false',
    DarkModeSupport: 'true',
  };

  // Set global defaults in Software hive
  const softwareStorage = manager.getStorageByHive('software');
  for (const [key, value] of Object.entries(features)) {
    await softwareStorage.write(`Feature_${key}`, value);
  }

  // Override with user-specific settings in CurrentUser
  const userStorage = manager.getStorageByHive('currentUser');
  await userStorage.write('Feature_DarkModeSupport', 'true');
  await userStorage.write('Feature_BetaFeatures', 'true');

  // Retrieve with fallback to defaults
  async function getFeatureFlag(featureName) {
    // Try user override first
    let value = await userStorage.read(`Feature_${featureName}`);
    if (value !== null) return value === 'true';

    // Fall back to global setting
    value = await softwareStorage.read(`Feature_${featureName}`);
    return value === 'true';
  }

  console.log('Feature Status:');
  for (const featureName of Object.keys(features)) {
    const enabled = await getFeatureFlag(featureName);
    console.log(`  ${featureName}: ${enabled ? 'ENABLED' : 'DISABLED'}`);
  }
}

/**
 * Example 5: Configuration Migration
 * Migrate configuration from one location to another
 */
async function exampleConfigurationMigration() {
  console.log('\n=== Example 5: Configuration Migration ===');

  const oldStorage = new SoftwareHiveStorage('OldAppName');
  const newStorage = new SoftwareHiveStorage('NewAppName');

  const keysToMigrate = ['Version', 'License', 'Settings', 'InstallPath'];

  console.log('Migrating configuration...');
  for (const key of keysToMigrate) {
    const value = await oldStorage.read(key);
    if (value !== null) {
      await newStorage.write(key, value);
      console.log(`Migrated ${key}: ${value}`);
    }
  }

  console.log('Migration complete');
}

/**
 * Example 6: System Service Configuration
 * Configure a Windows service with the System hive
 */
async function exampleSystemServiceConfiguration() {
  console.log('\n=== Example 6: System Service Configuration ===');

  const serviceStorage = new SystemHiveStorage('ControlSet001\\Services\\MyService');

  const serviceConfig = {
    DisplayName: 'My Custom Service',
    Description: 'Handles important background tasks',
    Start: '2', // 2 = Automatic, 3 = Manual, 4 = Disabled
    Type: '20', // 20 = Win32_ShareProcess
    ErrorControl: '1', // 1 = Normal
    ServiceDll: '%SystemRoot%\\System32\\MyService.dll',
  };

  console.log('Configuring service...');
  for (const [key, value] of Object.entries(serviceConfig)) {
    try {
      await serviceStorage.write(key, value);
      console.log(`Set ${key}: ${value}`);
    } catch (error) {
      console.error(`Failed to set ${key}: ${error.message}`);
    }
  }
}

/**
 * Example 7: OS Version Detection and Compatibility
 * Detect OS version and set compatibility flags
 */
async function exampleOSVersionDetection() {
  console.log('\n=== Example 7: OS Version Detection ===');

  const currentVersionStorage = new CurrentVersionHiveStorage('CompatibilityApp');

  // Read current Windows version info
  const currentVersionBase = new CurrentVersionHiveStorage('');
  const version = await currentVersionBase.read('CurrentVersion');
  const buildNumber = await currentVersionBase.read('CurrentBuildNumber');

  console.log(`Detected Windows Version: ${version}`);
  console.log(`Build Number: ${buildNumber}`);

  // Set compatibility flags based on OS version
  const parsedVersion = parseFloat(version);
  let compatMode = 'Modern';

  if (parsedVersion < 6.1) {
    compatMode = 'Legacy';
    await currentVersionStorage.write('LegacyMode', 'true');
  } else if (parsedVersion >= 10.0) {
    compatMode = 'Windows10Plus';
    await currentVersionStorage.write('ModernFeatures', 'true');
  }

  console.log(`Compatibility Mode: ${compatMode}`);
  await currentVersionStorage.write('CompatibilityMode', compatMode);
}

/**
 * Example 8: Settings Backup and Restore
 * Backup settings to a format, then restore them
 */
async function exampleSettingsBackupRestore() {
  console.log('\n=== Example 8: Settings Backup and Restore ===');

  const manager = new MultiHiveRegistryManager('BackupApp');
  const storages = manager.getStorages();

  // Backup all settings
  const backup = {};
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

  console.log('Backup created:');
  console.log(JSON.stringify(backup, null, 2));

  // Simulate modification
  console.log('\nModifying settings...');
  await manager.writeToAllHives('TestKey', 'Modified');

  // Restore settings
  console.log('Restoring from backup...');
  for (const [hiveName, storage] of Object.entries(storages)) {
    for (const [key, value] of Object.entries(backup[hiveName])) {
      await storage.write(key, value);
    }
  }

  console.log('Settings restored');
}

/**
 * Example 9: Conditional Storage Selection
 * Choose storage based on environment conditions
 */
async function exampleConditionalStorageSelection() {
  console.log('\n=== Example 9: Conditional Storage Selection ===');

  // Simulate environment detection
  const isSystemAdmin = true; // In real code, check actual permissions
  const requiresUserIsolation = true;

  let storage;

  if (isSystemAdmin && !requiresUserIsolation) {
    // Use Software hive for global settings
    storage = new SoftwareHiveStorage('AdminApp');
    console.log('Using HKLM Software hive (global)');
  } else if (requiresUserIsolation) {
    // Use CurrentUser hive for user-specific settings
    storage = new CurrentUserHiveStorage('Software\\IsolatedApp');
    console.log('Using HKEY_CURRENT_USER hive (user-isolated)');
  } else {
    // Fallback to CurrentVersion
    storage = new CurrentVersionHiveStorage('AppConfig');
    console.log('Using CurrentVersion hive');
  }

  // Use the selected storage
  await storage.write('Environment', isSystemAdmin ? 'Admin' : 'User');
  const env = await storage.read('Environment');
  console.log(`Stored environment: ${env}`);
}

/**
 * Example 10: All Hives Comparison
 * Compare same key across all available hives
 */
async function exampleCompareAcrossHives() {
  console.log('\n=== Example 10: Compare Across All Hives ===');

  const manager = new MultiHiveRegistryManager('ComparisonApp');
  const keyName = 'SharedSetting';

  // Write different values to each hive
  const values = {
    software: 'GlobalValue',
    currentUser: 'UserValue',
    currentVersion: 'OSValue',
    system: 'SystemValue',
  };

  console.log('Writing values to all hives...');
  for (const [hive, value] of Object.entries(values)) {
    try {
      await manager.readFromHive(hive, keyName);
    } catch (error) {
      // Key might not exist, just for demonstration
    }
  }

  // Compare values
  console.log('\nComparison across hives:');
  const storages = manager.getStorages();
  for (const [hiveName, storage] of Object.entries(storages)) {
    const value = await storage.read(keyName);
    console.log(`  ${hiveName}: ${value}`);
  }
}

/**
 * Run all examples
 */
async function runAllExamples() {
  try {
    await exampleApplicationSettings();
    await exampleUserPreferencesWithDefaults();
    await exampleMultiHiveRedundancy();
    await exampleFeatureFlags();
    await exampleConfigurationMigration();
    await exampleSystemServiceConfiguration();
    await exampleOSVersionDetection();
    await exampleSettingsBackupRestore();
    await exampleConditionalStorageSelection();
    await exampleCompareAcrossHives();

    console.log('\n=== All Examples Complete ===');
  } catch (error) {
    console.error('Example execution error:', error.message);
  }
}

module.exports = {
  exampleApplicationSettings,
  exampleUserPreferencesWithDefaults,
  exampleMultiHiveRedundancy,
  exampleFeatureFlags,
  exampleConfigurationMigration,
  exampleSystemServiceConfiguration,
  exampleOSVersionDetection,
  exampleSettingsBackupRestore,
  exampleConditionalStorageSelection,
  exampleCompareAcrossHives,
  runAllExamples,
};

// Run examples if this file is executed directly
if (require.main === module) {
  runAllExamples();
}
