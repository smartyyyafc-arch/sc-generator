/**
 * Registry Storage Variants using Different Hives
 * Creates multiple storage implementations for Windows Registry access
 * Supports: HKLM (Software), HKEY_CURRENT_USER (System), and CurrentVersion hives
 */

import * as Registry from 'winreg';

/**
 * Registry Hive Enumeration
 */
export enum RegistryHive {
  HKLM_SOFTWARE = 'HKEY_LOCAL_MACHINE\\Software',
  HKEY_CURRENT_USER = 'HKEY_CURRENT_USER',
  CURRENT_VERSION = 'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion',
  HKLM_SYSTEM = 'HKEY_LOCAL_MACHINE\\System',
  HKEY_CLASSES_ROOT = 'HKEY_CLASSES_ROOT',
  HKEY_CURRENT_CONFIG = 'HKEY_CURRENT_CONFIG',
}

/**
 * Base Registry Storage Interface
 */
export interface IRegistryStorage {
  hive: RegistryHive;
  read(key: string): Promise<string | null>;
  write(key: string, value: string): Promise<void>;
  delete(key: string): Promise<void>;
  exists(key: string): Promise<boolean>;
  listKeys(): Promise<string[]>;
}

/**
 * HKLM Software Hive Storage Variant
 * Suitable for application-wide settings and software configurations
 */
export class SoftwareHiveStorage implements IRegistryStorage {
  readonly hive = RegistryHive.HKLM_SOFTWARE;
  private registryKey: Registry.Registry;
  private basePath: string;

  constructor(baseSubPath: string = 'CustomApp') {
    this.basePath = `${this.hive}\\${baseSubPath}`;
    this.registryKey = new Registry({
      hive: Registry.HKLM,
      key: this.basePath,
    });
  }

  async read(key: string): Promise<string | null> {
    try {
      const value = await this.registryKey.get(key);
      return value?.value ?? null;
    } catch (error) {
      console.error(`Failed to read ${key} from Software hive:`, error);
      return null;
    }
  }

  async write(key: string, value: string): Promise<void> {
    try {
      await this.registryKey.set(key, Registry.REG_SZ, value);
    } catch (error) {
      console.error(`Failed to write ${key} to Software hive:`, error);
      throw error;
    }
  }

  async delete(key: string): Promise<void> {
    try {
      await this.registryKey.remove(key);
    } catch (error) {
      console.error(`Failed to delete ${key} from Software hive:`, error);
      throw error;
    }
  }

  async exists(key: string): Promise<boolean> {
    try {
      const value = await this.registryKey.get(key);
      return value !== undefined;
    } catch {
      return false;
    }
  }

  async listKeys(): Promise<string[]> {
    try {
      const items = await this.registryKey.values();
      return items.map((item) => item.name);
    } catch (error) {
      console.error('Failed to list keys from Software hive:', error);
      return [];
    }
  }
}

/**
 * HKEY_CURRENT_USER Hive Storage Variant
 * Suitable for user-specific settings and preferences
 */
export class CurrentUserHiveStorage implements IRegistryStorage {
  readonly hive = RegistryHive.HKEY_CURRENT_USER;
  private registryKey: Registry.Registry;
  private basePath: string;

  constructor(baseSubPath: string = 'Software\\CustomApp') {
    this.basePath = `${this.hive}\\${baseSubPath}`;
    this.registryKey = new Registry({
      hive: Registry.HKCU,
      key: this.basePath,
    });
  }

  async read(key: string): Promise<string | null> {
    try {
      const value = await this.registryKey.get(key);
      return value?.value ?? null;
    } catch (error) {
      console.error(`Failed to read ${key} from CurrentUser hive:`, error);
      return null;
    }
  }

  async write(key: string, value: string): Promise<void> {
    try {
      await this.registryKey.set(key, Registry.REG_SZ, value);
    } catch (error) {
      console.error(`Failed to write ${key} to CurrentUser hive:`, error);
      throw error;
    }
  }

  async delete(key: string): Promise<void> {
    try {
      await this.registryKey.remove(key);
    } catch (error) {
      console.error(`Failed to delete ${key} from CurrentUser hive:`, error);
      throw error;
    }
  }

  async exists(key: string): Promise<boolean> {
    try {
      const value = await this.registryKey.get(key);
      return value !== undefined;
    } catch {
      return false;
    }
  }

  async listKeys(): Promise<string[]> {
    try {
      const items = await this.registryKey.values();
      return items.map((item) => item.name);
    } catch (error) {
      console.error('Failed to list keys from CurrentUser hive:', error);
      return [];
    }
  }
}

/**
 * CurrentVersion Hive Storage Variant
 * Suitable for system version-related settings and OS configurations
 */
export class CurrentVersionHiveStorage implements IRegistryStorage {
  readonly hive = RegistryHive.CURRENT_VERSION;
  private registryKey: Registry.Registry;
  private baseSubPath: string;

  constructor(baseSubPath: string = 'CustomApp') {
    this.baseSubPath = baseSubPath;
    this.registryKey = new Registry({
      hive: Registry.HKLM,
      key: `${this.hive}\\${baseSubPath}`,
    });
  }

  async read(key: string): Promise<string | null> {
    try {
      const value = await this.registryKey.get(key);
      return value?.value ?? null;
    } catch (error) {
      console.error(`Failed to read ${key} from CurrentVersion hive:`, error);
      return null;
    }
  }

  async write(key: string, value: string): Promise<void> {
    try {
      await this.registryKey.set(key, Registry.REG_SZ, value);
    } catch (error) {
      console.error(`Failed to write ${key} to CurrentVersion hive:`, error);
      throw error;
    }
  }

  async delete(key: string): Promise<void> {
    try {
      await this.registryKey.remove(key);
    } catch (error) {
      console.error(`Failed to delete ${key} from CurrentVersion hive:`, error);
      throw error;
    }
  }

  async exists(key: string): Promise<boolean> {
    try {
      const value = await this.registryKey.get(key);
      return value !== undefined;
    } catch {
      return false;
    }
  }

  async listKeys(): Promise<string[]> {
    try {
      const items = await this.registryKey.values();
      return items.map((item) => item.name);
    } catch (error) {
      console.error('Failed to list keys from CurrentVersion hive:', error);
      return [];
    }
  }
}

/**
 * System Hive Storage Variant
 * Suitable for system hardware profiles and device configurations
 */
export class SystemHiveStorage implements IRegistryStorage {
  readonly hive = RegistryHive.HKLM_SYSTEM;
  private registryKey: Registry.Registry;
  private basePath: string;

  constructor(baseSubPath: string = 'ControlSet001\\Services\\CustomApp') {
    this.basePath = `${this.hive}\\${baseSubPath}`;
    this.registryKey = new Registry({
      hive: Registry.HKLM,
      key: this.basePath,
    });
  }

  async read(key: string): Promise<string | null> {
    try {
      const value = await this.registryKey.get(key);
      return value?.value ?? null;
    } catch (error) {
      console.error(`Failed to read ${key} from System hive:`, error);
      return null;
    }
  }

  async write(key: string, value: string): Promise<void> {
    try {
      await this.registryKey.set(key, Registry.REG_SZ, value);
    } catch (error) {
      console.error(`Failed to write ${key} to System hive:`, error);
      throw error;
    }
  }

  async delete(key: string): Promise<void> {
    try {
      await this.registryKey.remove(key);
    } catch (error) {
      console.error(`Failed to delete ${key} from System hive:`, error);
      throw error;
    }
  }

  async exists(key: string): Promise<boolean> {
    try {
      const value = await this.registryKey.get(key);
      return value !== undefined;
    } catch {
      return false;
    }
  }

  async listKeys(): Promise<string[]> {
    try {
      const items = await this.registryKey.values();
      return items.map((item) => item.name);
    } catch (error) {
      console.error('Failed to list keys from System hive:', error);
      return [];
    }
  }
}

/**
 * Multi-Hive Registry Storage Manager
 * Coordinates operations across multiple registry hives
 */
export class MultiHiveRegistryManager {
  private softwareStorage: SoftwareHiveStorage;
  private currentUserStorage: CurrentUserHiveStorage;
  private currentVersionStorage: CurrentVersionHiveStorage;
  private systemStorage: SystemHiveStorage;

  constructor(
    appName: string = 'CustomApp',
    userSubPath: string = 'Software\\CustomApp',
    versionSubPath: string = 'CustomApp',
    systemSubPath: string = 'ControlSet001\\Services\\CustomApp'
  ) {
    this.softwareStorage = new SoftwareHiveStorage(appName);
    this.currentUserStorage = new CurrentUserHiveStorage(userSubPath);
    this.currentVersionStorage = new CurrentVersionHiveStorage(versionSubPath);
    this.systemStorage = new SystemHiveStorage(systemSubPath);
  }

  /**
   * Write value to all hives
   */
  async writeToAllHives(key: string, value: string): Promise<void> {
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
  async readFromHive(hive: 'software' | 'currentUser' | 'currentVersion' | 'system', key: string): Promise<string | null> {
    const storage = this.getStorageByHive(hive);
    return storage.read(key);
  }

  /**
   * Read value from all hives and return first match
   */
  async readFromFirstAvailable(key: string): Promise<{ value: string | null; hive: string } | null> {
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
  async deleteFromAllHives(key: string): Promise<void> {
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
  private getStorageByHive(hive: 'software' | 'currentUser' | 'currentVersion' | 'system'): IRegistryStorage {
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
  getStorages(): Record<string, IRegistryStorage> {
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
export class RegistryStorageFactory {
  static createStorage(
    hive: RegistryHive,
    subPath?: string
  ): IRegistryStorage {
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

  static createAllVariants(appName: string = 'CustomApp'): Map<string, IRegistryStorage> {
    const variants = new Map<string, IRegistryStorage>();

    variants.set('software', new SoftwareHiveStorage(appName));
    variants.set('currentUser', new CurrentUserHiveStorage(`Software\\${appName}`));
    variants.set('currentVersion', new CurrentVersionHiveStorage(appName));
    variants.set('system', new SystemHiveStorage(`ControlSet001\\Services\\${appName}`));

    return variants;
  }
}

/**
 * Example usage and initialization
 */
export async function initializeRegistryStorage(): Promise<void> {
  // Create multi-hive manager
  const manager = new MultiHiveRegistryManager('MyApp');

  // Example: Write to specific hive
  await manager.readFromHive('software', 'Version');

  // Example: Write to all hives
  await manager.writeToAllHives('ConfigValue', 'test123');

  // Example: Read from first available hive
  const result = await manager.readFromFirstAvailable('ConfigValue');
  console.log('Found value:', result);

  // Example: Using factory
  const storages = RegistryStorageFactory.createAllVariants('MyApp');
  for (const [name, storage] of storages) {
    console.log(`${name}: ${storage.hive}`);
  }
}

export default {
  RegistryHive,
  SoftwareHiveStorage,
  CurrentUserHiveStorage,
  CurrentVersionHiveStorage,
  SystemHiveStorage,
  MultiHiveRegistryManager,
  RegistryStorageFactory,
};
