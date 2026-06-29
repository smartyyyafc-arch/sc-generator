/**
 * Registry Storage Variants using Different Hives (JavaScript)
 * Creates multiple storage implementations for Windows Registry access
 * Supports: HKLM (Software), HKEY_CURRENT_USER (System), and CurrentVersion hives
 */

const Registry = require('winreg');

/**
 * Registry Hive Enumeration
 */
const RegistryHive = {
  HKLM_SOFTWARE: 'HKEY_LOCAL_MACHINE\\Software',
  HKEY_CURRENT_USER: 'HKEY_CURRENT_USER',
  CURRENT_VERSION: 'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion',
  HKLM_SYSTEM: 'HKEY_LOCAL_MACHINE\\System',
  HKEY_CLASSES_ROOT: 'HKEY_CLASSES_ROOT',
  HKEY_CURRENT_CONFIG: 'HKEY_CURRENT_CONFIG',
};

/**
 * Base Registry Storage Interface
 * Defines contract for all registry storage variants
 */
class BaseRegistryStorage {
  constructor(hive, basePath) {
    this.hive = hive;
    this.basePath = basePath;
  }

  async read(key) {
    throw new Error('read() not implemented');
  }

  async write(key, value) {
    throw new Error('write() not implemented');
  }

  async delete(key) {
    throw new Error('delete() not implemented');
  }

  async exists(key) {
    throw new Error('exists() not implemented');
  }

  async listKeys() {
    throw new Error('listKeys() not implemented');
  }
}

/**
 * HKLM Software Hive Storage Variant
 * Suitable for application-wide settings and software configurations
 * Path: HKEY_LOCAL_MACHINE\Software\[AppName]
 */
class SoftwareHiveStorage extends BaseRegistryStorage {
  constructor(baseSubPath = 'CustomApp') {
    const hive = RegistryHive.HKLM_SOFTWARE;
    const basePath = `${hive}\\${baseSubPath}`;
    super(hive, basePath);
    this.registryKey = new Registry({
      hive: Registry.HKLM,
      key: basePath,
    });
  }

  async read(key) {
    try {
      const value = await this.registryKey.get(key);
      return value?.value ?? null;
    } catch (error) {
      console.error(`Failed to read ${key} from Software hive:`, error.message);
      return null;
    }
  }

  async write(key, value) {
    try {
      await this.registryKey.set(key, Registry.REG_SZ, value);
    } catch (error) {
      console.error(`Failed to write ${key} to Software hive:`, error.message);
      throw error;
    }
  }

  async delete(key) {
    try {
      await this.registryKey.remove(key);
    } catch (error) {
      console.error(`Failed to delete ${key} from Software hive:`, error.message);
      throw error;
    }
  }

  async exists(key) {
    try {
      await this.registryKey.get(key);
      return true;
    } catch {
      return false;
    }
  }

  async listKeys() {
    try {
      const items = await this.registryKey.values();
      return items.map((item) => item.name);
    } catch (error) {
      console.error('Failed to list keys from Software hive:', error.message);
      return [];
    }
  }
}

/**
 * HKEY_CURRENT_USER Hive Storage Variant
 * Suitable for user-specific settings and preferences
 * Path: HKEY_CURRENT_USER\[SubPath]
 */
class CurrentUserHiveStorage extends BaseRegistryStorage {
  constructor(baseSubPath = 'Software\\CustomApp') {
    const hive = RegistryHive.HKEY_CURRENT_USER;
    const basePath = `${hive}\\${baseSubPath}`;
    super(hive, basePath);
    this.registryKey = new Registry({
      hive: Registry.HKCU,
      key: basePath,
    });
  }

  async read(key) {
    try {
      const value = await this.registryKey.get(key);
      return value?.value ?? null;
    } catch (error) {
      console.error(`Failed to read ${key} from CurrentUser hive:`, error.message);
      return null;
    }
  }

  async write(key, value) {
    try {
      await this.registryKey.set(key, Registry.REG_SZ, value);
    } catch (error) {
      console.error(`Failed to write ${key} to CurrentUser hive:`, error.message);
      throw error;
    }
  }

  async delete(key) {
    try {
      await this.registryKey.remove(key);
    } catch (error) {
      console.error(`Failed to delete ${key} from CurrentUser hive:`, error.message);
      throw error;
    }
  }

  async exists(key) {
    try {
      await this.registryKey.get(key);
      return true;
    } catch {
      return false;
    }
  }

  async listKeys() {
    try {
      const items = await this.registryKey.values();
      return items.map((item) => item.name);
    } catch (error) {
      console.error('Failed to list keys from CurrentUser hive:', error.message);
      return [];
    }
  }
}

/**
 * CurrentVersion Hive Storage Variant
 * Suitable for system version-related settings and OS configurations
 * Path: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\[SubPath]
 */
class CurrentVersionHiveStorage extends BaseRegistryStorage {
  constructor(baseSubPath = 'CustomApp') {
    const hive = RegistryHive.CURRENT_VERSION;
    const basePath = `${hive}\\${baseSubPath}`;
    super(hive, basePath);
    this.baseSubPath = baseSubPath;
    this.registryKey = new Registry({
      hive: Registry.HKLM,
      key: basePath,
    });
  }

  async read(key) {
    try {
      const value = await this.registryKey.get(key);
      return value?.value ?? null;
    } catch (error) {
      console.error(`Failed to read ${key} from CurrentVersion hive:`, error.message);
      return null;
    }
  }

  async write(key, value) {
    try {
      await this.registryKey.set(key, Registry.REG_SZ, value);
    } catch (error) {
      console.error(`Failed to write ${key} to CurrentVersion hive:`, error.message);
      throw error;
    }
  }

  async delete(key) {
    try {
      await this.registryKey.remove(key);
    } catch (error) {
      console.error(`Failed to delete ${key} from CurrentVersion hive:`, error.message);
      throw error;
    }
  }

  async exists(key) {
    try {
      await this.registryKey.get(key);
      return true;
    } catch {
      return false;
    }
  }

  async listKeys() {
    try {
      const items = await this.registryKey.values();
      return items.map((item) => item.name);
    } catch (error) {
      console.error('Failed to list keys from CurrentVersion hive:', error.message);
      return [];
    }
  }
}

/**
 * System Hive Storage Variant
 * Suitable for system hardware profiles and device configurations
 * Path: HKEY_LOCAL_MACHINE\System\[ControlSet]\Services\[SubPath]
 */
class SystemHiveStorage extends BaseRegistryStorage {
  constructor(baseSubPath = 'ControlSet001\\Services\\CustomApp') {
    const hive = RegistryHive.HKLM_SYSTEM;
    const basePath = `${hive}\\${baseSubPath}`;
    super(hive, basePath);
    this.registryKey = new Registry({
      hive: Registry.HKLM,
      key: basePath,
    });
  }

  async read(key) {
    try {
      const value = await this.registryKey.get(key);
      return value?.value ?? null;
    } catch (error) {
      console.error(`Failed to read ${key} from System hive:`, error.message);
      return null;
    }
  }

  async write(key, value) {
    try {
      await this.registryKey.set(key, Registry.REG_SZ, value);
    } catch (error) {
      console.error(`Failed to write ${key} to System hive:`, error.message);
      throw error;
    }
  }

  async delete(key) {
    try {
      await this.registryKey.remove(key);
    } catch (error) {
      console.error(`Failed to delete ${key} from System hive:`, error.message);
      throw error;
    }
  }

  async exists(key) {
    try {
      await this.registryKey.get(key);
      return true;
    } catch {
      return false;
    }
  }

  async listKeys() {
    try {
      const items = await this.registryKey.values();
      return items.map((item) => item.name);
    } catch (error) {
      console.error('Failed to list keys from System hive:', error.message);
      return [];
    }
  }
}

/**
 * Multi-Hive Registry Storage Manager
 * Coordinates operations across multiple registry hives
 */
class MultiHiveRegistryManager {
  constructor(
    appName = 'CustomApp',
    userSubPath = 'Software\\CustomApp',
    versionSubPath = 'CustomApp',
    systemSubPath = 'ControlSet001\\Services\\CustomApp'
  ) {
    this.softwareStorage = new SoftwareHiveStorage(appName);
    this.currentUserStorage = new CurrentUserHiveStorage(userSubPath);
    this.currentVersionStorage = new CurrentVersionHiveStorage(versionSubPath);
    this.systemStorage = new SystemHiveStorage(systemSubPath);
  }

  /**
   * Write value to all hives
   */
  async writeToAllHives(key, value) {
    const results = await Promise.allSettled([
      this.softwareStorage.write(key, value),
      this.currentUserStorage.write(key, value),
      this.currentVersionStorage.write(key, value),
      this.systemStorage.write(key, value),
    ]);

    const failures = results.filter((r) => r.status === 'rejected');
    if (failures.length > 0) {
      console.warn(`Failed to write to ${failures.length} hives`);
    }
  }

  /**
   * Read value from specific hive
   */
  async readFromHive(hive, key) {
    const storage = this.getStorageByHive(hive);
    return storage.read(key);
  }

  /**
   * Read value from all hives and return first match
   */
  async readFromFirstAvailable(key) {
    const hives = [
      { name: 'software', storage: this.softwareStorage },
      { name: 'currentUser', storage: this.currentUserStorage },
      { name: 'currentVersion', storage: this.currentVersionStorage },
      { name: 'system', storage: this.systemStorage },
    ];

    for (const { name, storage } of hives) {
      const value = await storage.read(key);
      if (value !== null) {
        return { value, hive: name };
      }
    }

    return null;
  }

  /**
   * Delete key from all hives
   */
  async deleteFromAllHives(key) {
    await Promise.allSettled([
      this.softwareStorage.delete(key),
      this.currentUserStorage.delete(key),
      this.currentVersionStorage.delete(key),
      this.systemStorage.delete(key),
    ]);
  }

  /**
   * Get storage instance by hive name
   */
  getStorageByHive(hive) {
    switch (hive) {
      case 'software':
        return this.softwareStorage;
      case 'currentUser':
        return this.currentUserStorage;
      case 'currentVersion':
        return this.currentVersionStorage;
      case 'system':
        return this.systemStorage;
      default:
        throw new Error(`Unknown hive: ${hive}`);
    }
  }

  /**
   * List all available storages
   */
  getStorages() {
    return {
      software: this.softwareStorage,
      currentUser: this.currentUserStorage,
      currentVersion: this.currentVersionStorage,
      system: this.systemStorage,
    };
  }
}

/**
 * Registry Storage Factory
 * Creates appropriate storage variant based on hive type
 */
class RegistryStorageFactory {
  static createStorage(hive, subPath) {
    switch (hive) {
      case RegistryHive.HKLM_SOFTWARE:
        return new SoftwareHiveStorage(subPath || 'CustomApp');
      case RegistryHive.HKEY_CURRENT_USER:
        return new CurrentUserHiveStorage(subPath || 'Software\\CustomApp');
      case RegistryHive.CURRENT_VERSION:
        return new CurrentVersionHiveStorage(subPath || 'CustomApp');
      case RegistryHive.HKLM_SYSTEM:
        return new SystemHiveStorage(subPath || 'ControlSet001\\Services\\CustomApp');
      default:
        throw new Error(`Unsupported hive: ${hive}`);
    }
  }

  static createAllVariants(appName = 'CustomApp') {
    const variants = new Map();

    variants.set('software', new SoftwareHiveStorage(appName));
    variants.set('currentUser', new CurrentUserHiveStorage(`Software\\${appName}`));
    variants.set('currentVersion', new CurrentVersionHiveStorage(appName));
    variants.set('system', new SystemHiveStorage(`ControlSet001\\Services\\${appName}`));

    return variants;
  }
}

/**
 * Example usage
 */
async function initializeRegistryStorage() {
  // Create multi-hive manager
  const manager = new MultiHiveRegistryManager('MyApp');

  // Example: Read from specific hive
  const softwareValue = await manager.readFromHive('software', 'Version');
  console.log('Software hive Version:', softwareValue);

  // Example: Write to all hives
  await manager.writeToAllHives('ConfigValue', 'test123');
  console.log('Written ConfigValue to all hives');

  // Example: Read from first available hive
  const result = await manager.readFromFirstAvailable('ConfigValue');
  console.log('Found value:', result);

  // Example: Using factory
  const storages = RegistryStorageFactory.createAllVariants('MyApp');
  console.log('Available storage variants:');
  for (const [name, storage] of storages) {
    console.log(`  ${name}: ${storage.hive}`);
  }
}

module.exports = {
  RegistryHive,
  SoftwareHiveStorage,
  CurrentUserHiveStorage,
  CurrentVersionHiveStorage,
  SystemHiveStorage,
  MultiHiveRegistryManager,
  RegistryStorageFactory,
  BaseRegistryStorage,
  initializeRegistryStorage,
};
