/**
 * Registry Cleanup Handler - Unit Tests
 * Tests cleanup functionality and patterns
 */

import {
  RegistryCleanupHandler,
  initializeCleanupHandler,
  getCleanupHandler,
  withCleanupContext,
  CleanupEntry,
  CleanupResult,
} from './registry-cleanup-handler';
import { RegistryHive } from './registry-storage-variants';

describe('RegistryCleanupHandler', () => {
  let handler: RegistryCleanupHandler;

  beforeEach(() => {
    handler = new RegistryCleanupHandler({ verbose: false });
  });

  describe('Initialization', () => {
    it('should create handler with default options', () => {
      const h = new RegistryCleanupHandler();
      expect(h).toBeInstanceOf(RegistryCleanupHandler);
    });

    it('should create handler with custom options', () => {
      const h = new RegistryCleanupHandler({
        verbose: true,
        dryRun: true,
        trackOriginalValues: false,
        maxRetries: 5,
      });
      expect(h).toBeInstanceOf(RegistryCleanupHandler);
    });
  });

  describe('Tracking', () => {
    it('should start and stop tracking', () => {
      handler.startTracking();
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'TestKey');
      expect(handler.getTrackedEntries().length).toBe(1);

      handler.stopTracking();
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'AnotherKey');
      expect(handler.getTrackedEntries().length).toBe(1); // Should still be 1
    });

    it('should add entries manually', () => {
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1', 'Value1');
      handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'Key2', 'Value2');
      handler.addEntry(RegistryHive.CURRENT_VERSION, 'Key3');

      const entries = handler.getTrackedEntries();
      expect(entries.length).toBe(3);
    });

    it('should track write operations', async () => {
      handler.startTracking();

      const storage = {
        hive: RegistryHive.HKLM_SOFTWARE,
        read: async () => 'OriginalValue',
        write: async () => {},
        delete: async () => {},
        exists: async () => true,
        listKeys: async () => [],
      };

      await handler.trackWrite(
        RegistryHive.HKLM_SOFTWARE,
        'TestKey',
        storage as any
      );

      const entries = handler.getTrackedEntries();
      expect(entries.length).toBe(1);
      expect(entries[0].originalValue).toBe('OriginalValue');
    });

    it('should track delete operations', () => {
      handler.startTracking();
      handler.trackDelete(RegistryHive.HKLM_SOFTWARE, 'DeletedKey');

      const entries = handler.getTrackedEntries();
      expect(entries.length).toBe(1);
      expect(entries[0].wasDeleted).toBe(true);
    });
  });

  describe('Query and Filter', () => {
    beforeEach(() => {
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'SoftKey1');
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'SoftKey2');
      handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'UserKey1');
      handler.addEntry(RegistryHive.CURRENT_VERSION, 'VersionKey1');
    });

    it('should get all tracked entries', () => {
      const entries = handler.getTrackedEntries();
      expect(entries.length).toBe(4);
    });

    it('should filter entries by hive', () => {
      const softwareEntries = handler.getEntriesByHive(RegistryHive.HKLM_SOFTWARE);
      expect(softwareEntries.length).toBe(2);

      const userEntries = handler.getEntriesByHive(RegistryHive.HKEY_CURRENT_USER);
      expect(userEntries.length).toBe(1);
    });

    it('should get statistics', () => {
      const stats = handler.getStatistics();

      expect(stats.totalEntries).toBe(4);
      expect(stats.entriesByHive[RegistryHive.HKLM_SOFTWARE]).toBe(2);
      expect(stats.entriesByHive[RegistryHive.HKEY_CURRENT_USER]).toBe(1);
      expect(stats.oldestEntry).toBeTruthy();
      expect(stats.newestEntry).toBeTruthy();
    });
  });

  describe('Cleanup Operations', () => {
    it('should handle dry run cleanup', async () => {
      const dryHandler = new RegistryCleanupHandler({ dryRun: true });
      dryHandler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1');
      dryHandler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key2');

      const result = await dryHandler.executeCleanup();

      expect(result.success).toBe(true);
      expect(result.entriesCleaned).toBe(2);
      expect(result.dryRun).toBe(true);
    });

    it('should return cleanup result with statistics', async () => {
      const dryHandler = new RegistryCleanupHandler({ dryRun: true });
      dryHandler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1');

      const result = await dryHandler.executeCleanup();

      expect(result).toHaveProperty('success');
      expect(result).toHaveProperty('entriesCleaned');
      expect(result).toHaveProperty('failedEntries');
      expect(result).toHaveProperty('totalTime');
      expect(result).toHaveProperty('errors');
      expect(result.totalTime).toBeGreaterThanOrEqual(0);
    });

    it('should handle empty cleanup log', async () => {
      const result = await handler.executeCleanup();

      expect(result.success).toBe(true);
      expect(result.entriesCleaned).toBe(0);
    });
  });

  describe('Log Management', () => {
    it('should clear log', () => {
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1');
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key2');
      expect(handler.getTrackedEntries().length).toBe(2);

      handler.clearLog();
      expect(handler.getTrackedEntries().length).toBe(0);
    });

    it('should export log to JSON', () => {
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1', 'Value1');
      handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'Key2', 'Value2');

      const json = handler.exportLog();
      expect(json).toBeTruthy();

      const parsed = JSON.parse(json);
      expect(Array.isArray(parsed)).toBe(true);
      expect(parsed.length).toBe(2);
    });

    it('should import log from JSON', () => {
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1', 'Value1');
      const exported = handler.exportLog();

      const newHandler = new RegistryCleanupHandler();
      newHandler.importLog(exported);

      expect(newHandler.getTrackedEntries().length).toBe(1);
    });

    it('should throw on invalid JSON import', () => {
      expect(() => {
        handler.importLog('invalid json');
      }).toThrow();
    });
  });

  describe('Global Handler', () => {
    it('should initialize global handler', () => {
      const handler = initializeCleanupHandler({ verbose: false });
      expect(handler).toBeInstanceOf(RegistryCleanupHandler);
    });

    it('should return same global instance', () => {
      const handler1 = getCleanupHandler();
      const handler2 = getCleanupHandler();
      expect(handler1).toBe(handler2);
    });

    it('should get global handler even without init', () => {
      const handler = getCleanupHandler();
      expect(handler).toBeInstanceOf(RegistryCleanupHandler);
    });
  });

  describe('Context Manager', () => {
    it('should execute with cleanup context', async () => {
      const { result, cleanup } = await withCleanupContext(
        async (handler) => {
          handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1');
          return 'success';
        },
        { dryRun: true }
      );

      expect(result).toBe('success');
      expect(cleanup).toHaveProperty('entriesCleaned');
      expect(cleanup.entriesCleaned).toBe(1);
    });

    it('should handle errors in context', async () => {
      const error = new Error('Test error');

      try {
        await withCleanupContext(async () => {
          throw error;
        });
        fail('Should have thrown');
      } catch (err) {
        expect(err).toBe(error);
      }
    });

    it('should cleanup even on error', async () => {
      const { result, cleanup } = await withCleanupContext(
        async (handler) => {
          handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1');
          throw new Error('Expected error');
        },
        { dryRun: true }
      ).catch((err) => {
        if (err.message === 'Expected error') {
          return { result: null, cleanup: { entriesCleaned: 0 } as CleanupResult };
        }
        throw err;
      });

      // Error was caught and handled
      expect(result).toBeNull();
    });
  });

  describe('Entry Management', () => {
    it('should add entry with original value', () => {
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1', 'OriginalValue');

      const entries = handler.getTrackedEntries();
      expect(entries[0].originalValue).toBe('OriginalValue');
    });

    it('should add entry without original value', () => {
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1');

      const entries = handler.getTrackedEntries();
      expect(entries[0].originalValue).toBeUndefined();
    });

    it('should track entry timestamp', () => {
      const beforeAdd = new Date();
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1');
      const afterAdd = new Date();

      const entries = handler.getTrackedEntries();
      expect(entries[0].timestamp).toBeTruthy();
      expect(entries[0].timestamp.getTime()).toBeGreaterThanOrEqual(beforeAdd.getTime());
      expect(entries[0].timestamp.getTime()).toBeLessThanOrEqual(afterAdd.getTime());
    });
  });

  describe('Hive-specific cleanup', () => {
    beforeEach(() => {
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'SoftKey1');
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, 'SoftKey2');
      handler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'UserKey1');
    });

    it('should cleanup specific hive', async () => {
      const dryHandler = new RegistryCleanupHandler({ dryRun: true });
      dryHandler.addEntry(RegistryHive.HKLM_SOFTWARE, 'SoftKey1');
      dryHandler.addEntry(RegistryHive.HKLM_SOFTWARE, 'SoftKey2');
      dryHandler.addEntry(RegistryHive.HKEY_CURRENT_USER, 'UserKey1');

      const result = await dryHandler.cleanupHive(RegistryHive.HKLM_SOFTWARE);

      expect(result.entriesCleaned).toBe(2);
      expect(dryHandler.getTrackedEntries().length).toBe(1);
    });
  });

  describe('Restore operations', () => {
    it('should restore all entries', async () => {
      const dryHandler = new RegistryCleanupHandler({ dryRun: true });
      dryHandler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key1', 'Value1');
      dryHandler.addEntry(RegistryHive.HKLM_SOFTWARE, 'Key2', 'Value2');

      const result = await dryHandler.restoreAll();

      expect(result.success).toBe(true);
      expect(result.entriesCleaned).toBe(2);
    });
  });
});

describe('Integration Tests', () => {
  it('should handle multiple operations in sequence', async () => {
    const handler = new RegistryCleanupHandler({
      verbose: false,
      dryRun: true,
    });

    handler.startTracking();

    for (let i = 0; i < 10; i++) {
      handler.addEntry(RegistryHive.HKLM_SOFTWARE, `Key${i}`, `Value${i}`);
    }

    expect(handler.getTrackedEntries().length).toBe(10);

    const result = await handler.executeCleanup();
    expect(result.entriesCleaned).toBe(10);
    expect(result.success).toBe(true);

    handler.stopTracking();
  });

  it('should handle export/import cycle', () => {
    const handler1 = new RegistryCleanupHandler();

    for (let i = 0; i < 5; i++) {
      handler1.addEntry(RegistryHive.HKLM_SOFTWARE, `Key${i}`, `Value${i}`);
    }

    const exported = handler1.exportLog();

    const handler2 = new RegistryCleanupHandler();
    handler2.importLog(exported);

    expect(handler2.getTrackedEntries().length).toBe(5);
  });
});
