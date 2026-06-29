/**
 * Registry Storage Variants Tests
 * Comprehensive test suite for all registry hive storage implementations
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

describe('Registry Storage Variants', () => {
  describe('RegistryHive Enumeration', () => {
    it('should define all required hives', () => {
      expect(RegistryHive.HKLM_SOFTWARE).toBe('HKEY_LOCAL_MACHINE\\Software');
      expect(RegistryHive.HKEY_CURRENT_USER).toBe('HKEY_CURRENT_USER');
      expect(RegistryHive.CURRENT_VERSION).toContain('CurrentVersion');
      expect(RegistryHive.HKLM_SYSTEM).toBe('HKEY_LOCAL_MACHINE\\System');
    });

    it('should have all standard hives', () => {
      const hives = Object.values(RegistryHive);
      expect(hives.length).toBeGreaterThanOrEqual(4);
      expect(hives).toContain(RegistryHive.HKLM_SOFTWARE);
      expect(hives).toContain(RegistryHive.HKEY_CURRENT_USER);
    });
  });

  describe('SoftwareHiveStorage', () => {
    let storage;

    beforeEach(() => {
      storage = new SoftwareHiveStorage('TestApp');
    });

    it('should have correct hive property', () => {
      expect(storage.hive).toBe(RegistryHive.HKLM_SOFTWARE);
    });

    it('should have basePath set correctly', () => {
      expect(storage.basePath).toContain('TestApp');
      expect(storage.basePath).toContain('Software');
    });

    it('should implement IRegistryStorage interface', async () => {
      expect(typeof storage.read).toBe('function');
      expect(typeof storage.write).toBe('function');
      expect(typeof storage.delete).toBe('function');
      expect(typeof storage.exists).toBe('function');
      expect(typeof storage.listKeys).toBe('function');
    });

    it('should return null on read error', async () => {
      const result = await storage.read('NonExistentKey');
      expect(result).toBeNull();
    });

    it('should list keys', async () => {
      const keys = await storage.listKeys();
      expect(Array.isArray(keys)).toBe(true);
    });
  });

  describe('CurrentUserHiveStorage', () => {
    let storage;

    beforeEach(() => {
      storage = new CurrentUserHiveStorage('Software\\TestApp');
    });

    it('should have correct hive property', () => {
      expect(storage.hive).toBe(RegistryHive.HKEY_CURRENT_USER);
    });

    it('should have basePath set correctly', () => {
      expect(storage.basePath).toContain('TestApp');
      expect(storage.basePath).toContain('HKEY_CURRENT_USER');
    });

    it('should implement IRegistryStorage interface', async () => {
      expect(typeof storage.read).toBe('function');
      expect(typeof storage.write).toBe('function');
      expect(typeof storage.delete).toBe('function');
      expect(typeof storage.exists).toBe('function');
      expect(typeof storage.listKeys).toBe('function');
    });

    it('should handle read/write operations', async () => {
      const keys = await storage.listKeys();
      expect(Array.isArray(keys)).toBe(true);
    });
  });

  describe('CurrentVersionHiveStorage', () => {
    let storage;

    beforeEach(() => {
      storage = new CurrentVersionHiveStorage('TestApp');
    });

    it('should have correct hive property', () => {
      expect(storage.hive).toBe(RegistryHive.CURRENT_VERSION);
    });

    it('should have basePath set correctly', () => {
      expect(storage.basePath).toContain('TestApp');
      expect(storage.basePath).toContain('CurrentVersion');
    });

    it('should store baseSubPath', () => {
      expect(storage.baseSubPath).toBe('TestApp');
    });

    it('should implement IRegistryStorage interface', async () => {
      expect(typeof storage.read).toBe('function');
      expect(typeof storage.write).toBe('function');
      expect(typeof storage.delete).toBe('function');
      expect(typeof storage.exists).toBe('function');
      expect(typeof storage.listKeys).toBe('function');
    });
  });

  describe('SystemHiveStorage', () => {
    let storage;

    beforeEach(() => {
      storage = new SystemHiveStorage('ControlSet001\\Services\\TestApp');
    });

    it('should have correct hive property', () => {
      expect(storage.hive).toBe(RegistryHive.HKLM_SYSTEM);
    });

    it('should have basePath set correctly', () => {
      expect(storage.basePath).toContain('System');
      expect(storage.basePath).toContain('TestApp');
    });

    it('should implement IRegistryStorage interface', async () => {
      expect(typeof storage.read).toBe('function');
      expect(typeof storage.write).toBe('function');
      expect(typeof storage.delete).toBe('function');
      expect(typeof storage.exists).toBe('function');
      expect(typeof storage.listKeys).toBe('function');
    });

    it('should list keys', async () => {
      const keys = await storage.listKeys();
      expect(Array.isArray(keys)).toBe(true);
    });
  });

  describe('MultiHiveRegistryManager', () => {
    let manager;

    beforeEach(() => {
      manager = new MultiHiveRegistryManager('TestApp');
    });

    it('should initialize all storage variants', () => {
      expect(manager.softwareStorage).toBeDefined();
      expect(manager.currentUserStorage).toBeDefined();
      expect(manager.currentVersionStorage).toBeDefined();
      expect(manager.systemStorage).toBeDefined();
    });

    it('should return all storages', () => {
      const storages = manager.getStorages();
      expect(storages.software).toBeDefined();
      expect(storages.currentUser).toBeDefined();
      expect(storages.currentVersion).toBeDefined();
      expect(storages.system).toBeDefined();
    });

    it('should get storage by hive name', () => {
      const software = manager.getStorageByHive('software');
      expect(software).toBe(manager.softwareStorage);

      const currentUser = manager.getStorageByHive('currentUser');
      expect(currentUser).toBe(manager.currentUserStorage);

      const currentVersion = manager.getStorageByHive('currentVersion');
      expect(currentVersion).toBe(manager.currentVersionStorage);

      const system = manager.getStorageByHive('system');
      expect(system).toBe(manager.systemStorage);
    });

    it('should throw error for unknown hive', () => {
      expect(() => {
        manager.getStorageByHive('unknown');
      }).toThrow();
    });

    it('should read from specific hive', async () => {
      const result = await manager.readFromHive('software', 'TestKey');
      expect(result === null || typeof result === 'string').toBe(true);
    });

    it('should handle readFromFirstAvailable', async () => {
      const result = await manager.readFromFirstAvailable('TestKey');
      expect(result === null || (result.value !== undefined && result.hive !== undefined)).toBe(true);
    });

    it('should handle writeToAllHives', async () => {
      await expect(manager.writeToAllHives('TestKey', 'TestValue')).resolves.toBeUndefined();
    });

    it('should handle deleteFromAllHives', async () => {
      await expect(manager.deleteFromAllHives('TestKey')).resolves.toBeUndefined();
    });
  });

  describe('RegistryStorageFactory', () => {
    it('should create software storage', () => {
      const storage = RegistryStorageFactory.createStorage(RegistryHive.HKLM_SOFTWARE, 'TestApp');
      expect(storage).toBeInstanceOf(SoftwareHiveStorage);
      expect(storage.hive).toBe(RegistryHive.HKLM_SOFTWARE);
    });

    it('should create current user storage', () => {
      const storage = RegistryStorageFactory.createStorage(RegistryHive.HKEY_CURRENT_USER);
      expect(storage).toBeInstanceOf(CurrentUserHiveStorage);
      expect(storage.hive).toBe(RegistryHive.HKEY_CURRENT_USER);
    });

    it('should create current version storage', () => {
      const storage = RegistryStorageFactory.createStorage(RegistryHive.CURRENT_VERSION);
      expect(storage).toBeInstanceOf(CurrentVersionHiveStorage);
      expect(storage.hive).toBe(RegistryHive.CURRENT_VERSION);
    });

    it('should create system storage', () => {
      const storage = RegistryStorageFactory.createStorage(RegistryHive.HKLM_SYSTEM);
      expect(storage).toBeInstanceOf(SystemHiveStorage);
      expect(storage.hive).toBe(RegistryHive.HKLM_SYSTEM);
    });

    it('should throw error for unsupported hive', () => {
      expect(() => {
        RegistryStorageFactory.createStorage('UNSUPPORTED_HIVE');
      }).toThrow();
    });

    it('should create all variants', () => {
      const variants = RegistryStorageFactory.createAllVariants('TestApp');
      expect(variants.size).toBe(4);
      expect(variants.has('software')).toBe(true);
      expect(variants.has('currentUser')).toBe(true);
      expect(variants.has('currentVersion')).toBe(true);
      expect(variants.has('system')).toBe(true);
    });

    it('should create variants with correct hives', () => {
      const variants = RegistryStorageFactory.createAllVariants('TestApp');
      expect(variants.get('software').hive).toBe(RegistryHive.HKLM_SOFTWARE);
      expect(variants.get('currentUser').hive).toBe(RegistryHive.HKEY_CURRENT_USER);
      expect(variants.get('currentVersion').hive).toBe(RegistryHive.CURRENT_VERSION);
      expect(variants.get('system').hive).toBe(RegistryHive.HKLM_SYSTEM);
    });
  });

  describe('Storage Variants Comparison', () => {
    it('should have distinct hive paths', () => {
      const softwareStorage = new SoftwareHiveStorage('Test');
      const currentUserStorage = new CurrentUserHiveStorage('Software\\Test');
      const currentVersionStorage = new CurrentVersionHiveStorage('Test');
      const systemStorage = new SystemHiveStorage('ControlSet001\\Services\\Test');

      const hives = [
        softwareStorage.hive,
        currentUserStorage.hive,
        currentVersionStorage.hive,
        systemStorage.hive,
      ];

      const uniqueHives = new Set(hives);
      expect(uniqueHives.size).toBe(4);
    });

    it('should support different sub-paths', () => {
      const storage1 = new SoftwareHiveStorage('App1');
      const storage2 = new SoftwareHiveStorage('App2');
      const storage3 = new SoftwareHiveStorage('Company\\App3');

      expect(storage1.basePath).toContain('App1');
      expect(storage2.basePath).toContain('App2');
      expect(storage3.basePath).toContain('App3');
    });
  });

  describe('Error Handling', () => {
    let manager;

    beforeEach(() => {
      manager = new MultiHiveRegistryManager('TestApp');
    });

    it('should handle write errors gracefully', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      await expect(manager.softwareStorage.write('', '')).rejects.toBeDefined();
      consoleSpy.mockRestore();
    });

    it('should handle read errors gracefully', async () => {
      const result = await manager.softwareStorage.read('InvalidKey@@##');
      expect(result).toBeNull();
    });

    it('should handle multiple hive failures', async () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      await manager.writeToAllHives('InvalidKey@@##', 'value');
      consoleSpy.mockRestore();
    });

    it('should handle delete errors gracefully', async () => {
      await expect(manager.softwareStorage.delete('NonExistentKey')).resolves.toBeUndefined();
    });
  });
});
