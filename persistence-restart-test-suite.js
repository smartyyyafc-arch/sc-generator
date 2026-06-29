/**
 * Persistence Test Suite - Multiple Restart Scenarios
 * Comprehensive test coverage for system persistence with various restart conditions
 * Tests data retention, state recovery, and payload survival across system reboots
 */

const fs = require('fs');
const path = require('path');
const { EventEmitter } = require('events');

/**
 * Mock storage for testing persistence
 */
class PersistenceStorage {
  constructor(storageDir) {
    this.storageDir = storageDir;
    this.data = new Map();
    this.initializeStorage();
  }

  initializeStorage() {
    if (!fs.existsSync(this.storageDir)) {
      fs.mkdirSync(this.storageDir, { recursive: true });
    }
  }

  async write(key, value) {
    this.data.set(key, value);
    const filePath = path.join(this.storageDir, `${key}.json`);
    fs.writeFileSync(filePath, JSON.stringify({ key, value, timestamp: Date.now() }));
    return true;
  }

  async read(key) {
    const filePath = path.join(this.storageDir, `${key}.json`);
    if (fs.existsSync(filePath)) {
      const content = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      return content.value;
    }
    return null;
  }

  async delete(key) {
    this.data.delete(key);
    const filePath = path.join(this.storageDir, `${key}.json`);
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
    return true;
  }

  async exists(key) {
    const filePath = path.join(this.storageDir, `${key}.json`);
    return fs.existsSync(filePath);
  }

  async listKeys() {
    if (!fs.existsSync(this.storageDir)) {
      return [];
    }
    return fs.readdirSync(this.storageDir)
      .filter(f => f.endsWith('.json'))
      .map(f => f.replace('.json', ''));
  }

  async clear() {
    this.data.clear();
    if (fs.existsSync(this.storageDir)) {
      fs.rmSync(this.storageDir, { recursive: true, force: true });
    }
  }
}

/**
 * System state manager for simulating restarts
 */
class SystemStateManager extends EventEmitter {
  constructor(storageDir) {
    super();
    this.storage = new PersistenceStorage(storageDir);
    this.isRunning = true;
    this.executionCount = 0;
    this.lastBootTime = Date.now();
    this.uptime = 0;
  }

  async initialize() {
    await this.storage.write('boot_count', await this.getBootCount() + 1);
    await this.storage.write('last_boot_time', this.lastBootTime);
    this.emit('initialized');
  }

  async getBootCount() {
    const count = await this.storage.read('boot_count');
    return count ? parseInt(count) : 0;
  }

  async simulateRestart() {
    this.isRunning = false;
    this.emit('shutdown', { reason: 'restart', timestamp: Date.now() });

    // Simulate restart delay
    await new Promise(resolve => setTimeout(resolve, 100));

    this.isRunning = true;
    this.lastBootTime = Date.now();
    this.uptime = 0;

    await this.initialize();
    this.emit('restarted', { bootCount: await this.getBootCount(), timestamp: Date.now() });
  }

  async simulateGracefulShutdown() {
    this.isRunning = false;
    await this.storage.write('shutdown_state', JSON.stringify({
      timestamp: Date.now(),
      graceful: true
    }));
    this.emit('shutdown', { reason: 'graceful', timestamp: Date.now() });
  }

  async simulateCrash() {
    this.isRunning = false;
    this.emit('shutdown', { reason: 'crash', timestamp: Date.now() });
  }

  async getUptime() {
    return Date.now() - this.lastBootTime;
  }
}

/**
 * Payload persistence manager
 */
class PayloadPersistenceManager {
  constructor(storageDir) {
    this.storage = new PersistenceStorage(storageDir);
    this.payloads = new Map();
  }

  async storePayload(payloadId, payloadData) {
    const payload = {
      id: payloadId,
      data: payloadData,
      stored_at: Date.now(),
      executed: false,
      execution_count: 0,
      last_execution: null
    };

    this.payloads.set(payloadId, payload);
    await this.storage.write(`payload_${payloadId}`, JSON.stringify(payload));
    return payload;
  }

  async retrievePayload(payloadId) {
    const stored = await this.storage.read(`payload_${payloadId}`);
    if (stored) {
      return typeof stored === 'string' ? JSON.parse(stored) : stored;
    }
    return null;
  }

  async executePayload(payloadId) {
    const payload = await this.retrievePayload(payloadId);
    if (!payload) {
      throw new Error(`Payload not found: ${payloadId}`);
    }

    payload.executed = true;
    payload.execution_count += 1;
    payload.last_execution = Date.now();

    await this.storage.write(`payload_${payloadId}`, JSON.stringify(payload));
    return payload;
  }

  async listPayloads() {
    const keys = await this.storage.listKeys();
    const payloadKeys = keys.filter(k => k.startsWith('payload_'));
    const payloads = [];

    for (const key of payloadKeys) {
      const payload = await this.storage.read(key);
      if (payload) {
        payloads.push(typeof payload === 'string' ? JSON.parse(payload) : payload);
      }
    }

    return payloads;
  }

  async deletePayload(payloadId) {
    this.payloads.delete(payloadId);
    await this.storage.delete(`payload_${payloadId}`);
  }
}

/**
 * Test result tracker
 */
class TestResultTracker {
  constructor() {
    this.results = [];
    this.startTime = Date.now();
  }

  addResult(testName, passed, details = {}) {
    this.results.push({
      test: testName,
      passed,
      timestamp: Date.now(),
      details
    });
  }

  getSummary() {
    const total = this.results.length;
    const passed = this.results.filter(r => r.passed).length;
    const failed = total - passed;

    return {
      total,
      passed,
      failed,
      success_rate: total > 0 ? (passed / total * 100).toFixed(2) + '%' : '0%',
      duration_ms: Date.now() - this.startTime,
      results: this.results
    };
  }
}

describe('Persistence Test Suite - Multiple Restart Scenarios', () => {
  let tracker;

  beforeEach(() => {
    tracker = new TestResultTracker();
  });

  /**
   * BASIC RESTART SCENARIOS
   * Tests for single system restart and data survival
   */
  describe('Basic System Restart Scenarios', () => {
    let stateManager;
    let storageDir;

    beforeEach(async () => {
      storageDir = `/tmp/persistence_test_${Date.now()}`;
      stateManager = new SystemStateManager(storageDir);
      await stateManager.initialize();
    });

    it('should preserve data across single restart', async () => {
      const testKey = 'test_data';
      const testValue = 'persistence_value_123';

      // Before restart: write data
      await stateManager.storage.write(testKey, testValue);
      const beforeRestart = await stateManager.storage.read(testKey);

      // Simulate restart
      await stateManager.simulateRestart();

      // After restart: read data
      const afterRestart = await stateManager.storage.read(testKey);

      expect(beforeRestart).toBe(testValue);
      expect(afterRestart).toBe(testValue);
      tracker.addResult('single_restart_data_preservation', beforeRestart === afterRestart);
    });

    it('should increment boot counter on each restart', async () => {
      const initialBootCount = await stateManager.getBootCount();

      await stateManager.simulateRestart();
      const afterFirstRestart = await stateManager.getBootCount();

      await stateManager.simulateRestart();
      const afterSecondRestart = await stateManager.getBootCount();

      expect(afterFirstRestart).toBe(initialBootCount + 1);
      expect(afterSecondRestart).toBe(initialBootCount + 2);
      tracker.addResult('boot_counter_increment',
        afterFirstRestart === initialBootCount + 1 && afterSecondRestart === initialBootCount + 2
      );
    });

    it('should update boot timestamp on restart', async () => {
      const firstBootTime = await stateManager.storage.read('last_boot_time');

      await new Promise(resolve => setTimeout(resolve, 50));
      await stateManager.simulateRestart();
      const secondBootTime = await stateManager.storage.read('last_boot_time');

      expect(firstBootTime).toBeDefined();
      expect(secondBootTime).toBeDefined();
      expect(parseInt(secondBootTime)).toBeGreaterThan(parseInt(firstBootTime));
      tracker.addResult('boot_timestamp_update', parseInt(secondBootTime) > parseInt(firstBootTime));
    });

    it('should handle multiple rapid restarts', async () => {
      const restartCount = 5;
      const bootCounts = [];

      for (let i = 0; i < restartCount; i++) {
        const count = await stateManager.getBootCount();
        bootCounts.push(count);
        await stateManager.simulateRestart();
      }

      expect(bootCounts.length).toBe(restartCount);
      const isSequential = bootCounts.every((count, i) => i === 0 || count < bootCounts[i - 1] || count === bootCounts[i - 1] + 1);
      tracker.addResult('rapid_restarts', isSequential);
    });

    it('should maintain data integrity through restart cycle', async () => {
      const testData = {
        key1: 'value1',
        key2: 'value2',
        key3: 'value3'
      };

      // Write test data
      for (const [key, value] of Object.entries(testData)) {
        await stateManager.storage.write(key, value);
      }

      // Restart
      await stateManager.simulateRestart();

      // Verify all data
      let allPreserved = true;
      for (const [key, value] of Object.entries(testData)) {
        const retrieved = await stateManager.storage.read(key);
        if (retrieved !== value) {
          allPreserved = false;
        }
      }

      expect(allPreserved).toBe(true);
      tracker.addResult('data_integrity_through_restart', allPreserved);
    });

    afterEach(async () => {
      await stateManager.storage.clear();
    });
  });

  /**
   * PAYLOAD PERSISTENCE SCENARIOS
   * Tests for payload survival and execution across restarts
   */
  describe('Payload Persistence Scenarios', () => {
    let payloadManager;
    let storageDir;

    beforeEach(() => {
      storageDir = `/tmp/payload_test_${Date.now()}`;
      payloadManager = new PayloadPersistenceManager(storageDir);
    });

    it('should store and retrieve payload across restart', async () => {
      const payloadId = 'test_payload_1';
      const payloadData = {
        command: 'echo "Test payload"',
        args: ['arg1', 'arg2'],
        priority: 'high'
      };

      // Store payload
      await payloadManager.storePayload(payloadId, payloadData);

      // Simulate retrieval (after restart)
      const retrieved = await payloadManager.retrievePayload(payloadId);

      expect(retrieved).toBeDefined();
      expect(retrieved.id).toBe(payloadId);
      expect(retrieved.data).toEqual(payloadData);
      tracker.addResult('payload_storage_retrieval',
        retrieved && retrieved.id === payloadId
      );
    });

    it('should track payload execution count', async () => {
      const payloadId = 'exec_counter_payload';
      const payloadData = { command: 'test' };

      // Store and execute multiple times
      await payloadManager.storePayload(payloadId, payloadData);

      let payload = await payloadManager.executePayload(payloadId);
      expect(payload.execution_count).toBe(1);

      // Simulate restart - payload should persist
      const retrieved = await payloadManager.retrievePayload(payloadId);
      expect(retrieved.execution_count).toBe(1);

      // Execute again after restart
      payload = await payloadManager.executePayload(payloadId);
      expect(payload.execution_count).toBe(2);

      tracker.addResult('payload_execution_tracking', payload.execution_count === 2);
    });

    it('should handle multiple concurrent payloads', async () => {
      const payloadCount = 10;
      const payloadIds = [];

      // Store multiple payloads
      for (let i = 0; i < payloadCount; i++) {
        const id = `payload_${i}`;
        payloadIds.push(id);
        await payloadManager.storePayload(id, { index: i });
      }

      // List all payloads
      const stored = await payloadManager.listPayloads();

      expect(stored.length).toBe(payloadCount);
      tracker.addResult('multiple_payloads_storage', stored.length === payloadCount);
    });

    it('should update payload execution timestamp', async () => {
      const payloadId = 'timestamp_payload';
      const payloadData = { command: 'test' };

      await payloadManager.storePayload(payloadId, payloadData);
      const beforeExecution = await payloadManager.retrievePayload(payloadId);
      expect(beforeExecution.last_execution).toBeNull();

      await new Promise(resolve => setTimeout(resolve, 10));
      await payloadManager.executePayload(payloadId);

      const afterExecution = await payloadManager.retrievePayload(payloadId);
      expect(afterExecution.last_execution).not.toBeNull();
      expect(afterExecution.last_execution).toBeGreaterThan(beforeExecution.stored_at);

      tracker.addResult('payload_timestamp_update',
        afterExecution.last_execution > beforeExecution.stored_at
      );
    });

    it('should remove deleted payloads', async () => {
      const payloadId = 'delete_test_payload';
      await payloadManager.storePayload(payloadId, { command: 'test' });

      let exists = await payloadManager.retrievePayload(payloadId);
      expect(exists).not.toBeNull();

      await payloadManager.deletePayload(payloadId);

      exists = await payloadManager.retrievePayload(payloadId);
      expect(exists).toBeNull();

      tracker.addResult('payload_deletion', exists === null);
    });

    afterEach(async () => {
      await payloadManager.storage.clear();
    });
  });

  /**
   * GRACEFUL SHUTDOWN SCENARIOS
   * Tests for data preservation during controlled shutdowns
   */
  describe('Graceful Shutdown Scenarios', () => {
    let stateManager;
    let storageDir;

    beforeEach(async () => {
      storageDir = `/tmp/shutdown_test_${Date.now()}`;
      stateManager = new SystemStateManager(storageDir);
      await stateManager.initialize();
    });

    it('should preserve state during graceful shutdown', async () => {
      const stateKey = 'application_state';
      const stateValue = JSON.stringify({
        session: 'active',
        user: 'testuser',
        data: [1, 2, 3, 4, 5]
      });

      await stateManager.storage.write(stateKey, stateValue);
      await stateManager.simulateGracefulShutdown();

      // Simulate restart after graceful shutdown
      stateManager.isRunning = true;
      await stateManager.initialize();

      const recovered = await stateManager.storage.read(stateKey);
      expect(recovered).toBe(stateValue);

      tracker.addResult('graceful_shutdown_preservation', recovered === stateValue);
    });

    it('should record graceful shutdown marker', async () => {
      await stateManager.simulateGracefulShutdown();

      // Check shutdown state was recorded
      const shutdownState = await stateManager.storage.read('shutdown_state');
      expect(shutdownState).not.toBeNull();

      const parsed = JSON.parse(shutdownState);
      expect(parsed.graceful).toBe(true);

      tracker.addResult('graceful_shutdown_marker',
        parsed && parsed.graceful === true
      );
    });

    afterEach(async () => {
      await stateManager.storage.clear();
    });
  });

  /**
   * CRASH RECOVERY SCENARIOS
   * Tests for data survival and recovery after unexpected crashes
   */
  describe('Crash Recovery Scenarios', () => {
    let stateManager;
    let storageDir;

    beforeEach(async () => {
      storageDir = `/tmp/crash_test_${Date.now()}`;
      stateManager = new SystemStateManager(storageDir);
      await stateManager.initialize();
    });

    it('should preserve committed data after crash', async () => {
      const criticalData = 'critical_information_123';

      // Write critical data (simulate fsync/commit)
      await stateManager.storage.write('critical', criticalData);

      // Simulate crash without proper shutdown
      await stateManager.simulateCrash();

      // Simulate restart
      stateManager.isRunning = true;
      await stateManager.initialize();

      // Verify data survived crash
      const recovered = await stateManager.storage.read('critical');
      expect(recovered).toBe(criticalData);

      tracker.addResult('crash_data_recovery', recovered === criticalData);
    });

    it('should detect crash condition on recovery', async () => {
      // Write normal data
      await stateManager.storage.write('normal_key', 'normal_value');

      // Simulate crash
      await stateManager.simulateCrash();
      expect(stateManager.isRunning).toBe(false);

      // Detect crash during recovery
      const wasCrash = !await stateManager.storage.read('shutdown_state');

      // Restart system
      stateManager.isRunning = true;
      await stateManager.initialize();

      expect(wasCrash).toBe(true);
      tracker.addResult('crash_detection', wasCrash);
    });

    it('should maintain transaction log across crash', async () => {
      const transactions = [];

      // Log transactions
      for (let i = 0; i < 5; i++) {
        const tx = {
          id: i,
          timestamp: Date.now(),
          data: `transaction_${i}`
        };
        transactions.push(tx);
        await stateManager.storage.write(`tx_${i}`, JSON.stringify(tx));
      }

      // Crash
      await stateManager.simulateCrash();

      // Recovery
      stateManager.isRunning = true;
      await stateManager.initialize();

      // Verify all transactions survived
      let allRecovered = true;
      for (let i = 0; i < 5; i++) {
        const recovered = await stateManager.storage.read(`tx_${i}`);
        if (!recovered) allRecovered = false;
      }

      expect(allRecovered).toBe(true);
      tracker.addResult('transaction_log_survival', allRecovered);
    });

    afterEach(async () => {
      await stateManager.storage.clear();
    });
  });

  /**
   * SEQUENTIAL RESTART SCENARIOS
   * Tests for multiple restarts in sequence
   */
  describe('Sequential Restart Scenarios', () => {
    let stateManager;
    let storageDir;

    beforeEach(async () => {
      storageDir = `/tmp/sequential_test_${Date.now()}`;
      stateManager = new SystemStateManager(storageDir);
      await stateManager.initialize();
    });

    it('should handle 10 sequential restarts', async () => {
      const restartCount = 10;
      const bootCounts = [];

      for (let i = 0; i < restartCount; i++) {
        const bootCount = await stateManager.getBootCount();
        bootCounts.push(bootCount);
        await stateManager.simulateRestart();
      }

      // Verify monotonic increase (allowing for ties)
      let isValid = true;
      for (let i = 1; i < bootCounts.length; i++) {
        if (bootCounts[i] < bootCounts[i - 1]) {
          isValid = false;
          break;
        }
      }

      expect(isValid).toBe(true);
      tracker.addResult('ten_sequential_restarts', isValid);
    });

    it('should preserve increasing data values through restarts', async () => {
      const valueKey = 'incrementing_value';
      let currentValue = 0;

      // Perform 5 restart cycles with increasing values
      for (let cycle = 0; cycle < 5; cycle++) {
        currentValue += 100;
        await stateManager.storage.write(valueKey, currentValue.toString());

        const retrieved = await stateManager.storage.read(valueKey);
        expect(parseInt(retrieved)).toBe(currentValue);

        await stateManager.simulateRestart();
      }

      // Final verification after last restart
      const final = await stateManager.storage.read(valueKey);
      expect(parseInt(final)).toBe(currentValue);

      tracker.addResult('incrementing_values_through_restarts', parseInt(final) === currentValue);
    });

    it('should maintain independent state across restarts', async () => {
      const stateSnapshots = [];

      for (let i = 0; i < 3; i++) {
        await stateManager.storage.write(`state_${i}`, JSON.stringify({
          cycle: i,
          timestamp: Date.now()
        }));

        const snapshot = {};
        for (let j = 0; j <= i; j++) {
          snapshot[`state_${j}`] = await stateManager.storage.read(`state_${j}`);
        }
        stateSnapshots.push(snapshot);

        await stateManager.simulateRestart();
      }

      // Verify each state is independent
      expect(stateSnapshots.length).toBe(3);
      expect(Object.keys(stateSnapshots[0]).length).toBe(1);
      expect(Object.keys(stateSnapshots[1]).length).toBe(2);
      expect(Object.keys(stateSnapshots[2]).length).toBe(3);

      tracker.addResult('independent_state_cycles',
        Object.keys(stateSnapshots[0]).length === 1 &&
        Object.keys(stateSnapshots[1]).length === 2 &&
        Object.keys(stateSnapshots[2]).length === 3
      );
    });

    afterEach(async () => {
      await stateManager.storage.clear();
    });
  });

  /**
   * MIXED SCENARIO TESTS
   * Tests combining different restart types and conditions
   */
  describe('Mixed Restart Scenario Tests', () => {
    let payloadManager;
    let stateManager;
    let storageDir;

    beforeEach(async () => {
      storageDir = `/tmp/mixed_test_${Date.now()}`;
      stateManager = new SystemStateManager(storageDir);
      payloadManager = new PayloadPersistenceManager(storageDir);
      await stateManager.initialize();
    });

    it('should handle graceful shutdown followed by restart', async () => {
      const dataKey = 'graceful_restart_data';
      const dataValue = 'test_data_123';

      await stateManager.storage.write(dataKey, dataValue);

      // Graceful shutdown
      await stateManager.simulateGracefulShutdown();

      // Restart
      stateManager.isRunning = true;
      await stateManager.initialize();

      const recovered = await stateManager.storage.read(dataKey);
      expect(recovered).toBe(dataValue);

      tracker.addResult('graceful_shutdown_restart_cycle', recovered === dataValue);
    });

    it('should handle crash followed by recovery restart', async () => {
      const recoveryKey = 'crash_recovery_key';
      await stateManager.storage.write(recoveryKey, 'recovery_value');

      // Simulate crash
      await stateManager.simulateCrash();

      // Simulate recovery restart
      stateManager.isRunning = true;
      await stateManager.initialize();

      const recovered = await stateManager.storage.read(recoveryKey);
      expect(recovered).toBe('recovery_value');

      tracker.addResult('crash_recovery_restart', recovered === 'recovery_value');
    });

    it('should maintain payload state through mixed restart scenarios', async () => {
      const payloadId = 'mixed_scenario_payload';

      // Store payload
      await payloadManager.storePayload(payloadId, { command: 'test' });

      // Execute and graceful shutdown
      await payloadManager.executePayload(payloadId);
      await stateManager.simulateGracefulShutdown();

      // Restart
      stateManager.isRunning = true;
      await stateManager.initialize();

      // Execute again after restart
      const retrieved = await payloadManager.retrievePayload(payloadId);
      expect(retrieved.execution_count).toBe(1);

      await payloadManager.executePayload(payloadId);
      const final = await payloadManager.retrievePayload(payloadId);
      expect(final.execution_count).toBe(2);

      tracker.addResult('mixed_payload_restart_scenario', final.execution_count === 2);
    });

    it('should handle burst of payloads and crash', async () => {
      const payloadCount = 5;

      // Store multiple payloads
      for (let i = 0; i < payloadCount; i++) {
        await payloadManager.storePayload(`burst_${i}`, { index: i });
      }

      // Execute some
      for (let i = 0; i < 3; i++) {
        await payloadManager.executePayload(`burst_${i}`);
      }

      // Crash
      await stateManager.simulateCrash();

      // Recovery
      stateManager.isRunning = true;
      await stateManager.initialize();

      // Verify all payloads survived
      const survivors = await payloadManager.listPayloads();
      expect(survivors.length).toBe(payloadCount);

      // Verify execution counts
      const executed = survivors.filter(p => p.executed).length;
      expect(executed).toBe(3);

      tracker.addResult('burst_payloads_crash_recovery',
        survivors.length === payloadCount && executed === 3
      );
    });

    afterEach(async () => {
      await stateManager.storage.clear();
    });
  });

  /**
   * EDGE CASE SCENARIOS
   * Tests for boundary conditions and unusual situations
   */
  describe('Edge Case Scenarios', () => {
    let stateManager;
    let storageDir;

    beforeEach(async () => {
      storageDir = `/tmp/edge_test_${Date.now()}`;
      stateManager = new SystemStateManager(storageDir);
      await stateManager.initialize();
    });

    it('should handle empty key-value pairs', async () => {
      await stateManager.storage.write('empty_key', '');
      const retrieved = await stateManager.storage.read('empty_key');

      expect(retrieved).toBe('');
      tracker.addResult('empty_value_persistence', retrieved === '');
    });

    it('should handle very long keys', async () => {
      const longKey = 'k'.repeat(1000);
      const value = 'test_value';

      await stateManager.storage.write(longKey, value);
      const retrieved = await stateManager.storage.read(longKey);

      expect(retrieved).toBe(value);
      tracker.addResult('long_key_persistence', retrieved === value);
    });

    it('should handle large data values', async () => {
      const largeData = JSON.stringify({
        data: 'x'.repeat(100000),
        size: 100000
      });

      await stateManager.storage.write('large_data', largeData);
      const retrieved = await stateManager.storage.read('large_data');

      expect(retrieved).toBe(largeData);
      tracker.addResult('large_value_persistence', retrieved === largeData);
    });

    it('should handle special characters in values', async () => {
      const specialValue = '!@#$%^&*()_+-=[]{}|;:"\'<>,.?/\n\t\r';

      await stateManager.storage.write('special', specialValue);
      const retrieved = await stateManager.storage.read('special');

      expect(retrieved).toBe(specialValue);
      tracker.addResult('special_characters_persistence', retrieved === specialValue);
    });

    it('should handle JSON object persistence', async () => {
      const complexObject = {
        nested: {
          deep: {
            value: [1, 2, 3],
            metadata: {
              created: Date.now(),
              tags: ['test', 'edge-case']
            }
          }
        }
      };

      const jsonString = JSON.stringify(complexObject);
      await stateManager.storage.write('complex', jsonString);
      const retrieved = await stateManager.storage.read('complex');

      expect(retrieved).toBe(jsonString);
      tracker.addResult('json_object_persistence', retrieved === jsonString);
    });

    afterEach(async () => {
      await stateManager.storage.clear();
    });
  });

  /**
   * CONCURRENCY SCENARIOS
   * Tests for handling concurrent operations across restarts
   */
  describe('Concurrency Scenarios', () => {
    let stateManager;
    let storageDir;

    beforeEach(async () => {
      storageDir = `/tmp/concurrent_test_${Date.now()}`;
      stateManager = new SystemStateManager(storageDir);
      await stateManager.initialize();
    });

    it('should handle concurrent writes before restart', async () => {
      const writePromises = [];

      for (let i = 0; i < 20; i++) {
        writePromises.push(
          stateManager.storage.write(`concurrent_${i}`, `value_${i}`)
        );
      }

      await Promise.all(writePromises);

      const keys = await stateManager.storage.listKeys();
      expect(keys.length).toBeGreaterThanOrEqual(20);

      tracker.addResult('concurrent_writes', keys.length >= 20);
    });

    it('should preserve concurrent writes through restart', async () => {
      // Concurrent writes
      const writePromises = [];
      for (let i = 0; i < 10; i++) {
        writePromises.push(
          stateManager.storage.write(`concurrent_persist_${i}`, `value_${i}`)
        );
      }
      await Promise.all(writePromises);

      // Restart
      await stateManager.simulateRestart();

      // Verify all survived
      let allSurvived = true;
      for (let i = 0; i < 10; i++) {
        const value = await stateManager.storage.read(`concurrent_persist_${i}`);
        if (value !== `value_${i}`) {
          allSurvived = false;
        }
      }

      expect(allSurvived).toBe(true);
      tracker.addResult('concurrent_writes_through_restart', allSurvived);
    });

    afterEach(async () => {
      await stateManager.storage.clear();
    });
  });

  /**
   * PERFORMANCE SCENARIOS
   * Tests for performance characteristics across restarts
   */
  describe('Performance Scenarios', () => {
    let stateManager;
    let storageDir;

    beforeEach(async () => {
      storageDir = `/tmp/perf_test_${Date.now()}`;
      stateManager = new SystemStateManager(storageDir);
    });

    it('should handle initialization within acceptable time', async () => {
      const startTime = Date.now();
      await stateManager.initialize();
      const duration = Date.now() - startTime;

      expect(duration).toBeLessThan(1000); // Should initialize in < 1 second
      tracker.addResult('initialization_performance', duration < 1000, { duration });
    });

    it('should handle large-scale persistence operations', async () => {
      const operationCount = 100;
      const startTime = Date.now();

      for (let i = 0; i < operationCount; i++) {
        await stateManager.storage.write(`perf_${i}`, `value_${i}`);
      }

      const duration = Date.now() - startTime;
      const opsPerSecond = (operationCount / (duration / 1000)).toFixed(2);

      expect(duration).toBeLessThan(5000); // Should complete in < 5 seconds
      tracker.addResult('large_scale_operations', duration < 5000, { opsPerSecond });
    });

    afterEach(async () => {
      await stateManager.storage.clear();
    });
  });

  /**
   * TEST SUMMARY
   * Final summary of all test results
   */
  afterAll(() => {
    console.log('\n' + '='.repeat(70));
    console.log('PERSISTENCE TEST SUITE - FINAL SUMMARY');
    console.log('='.repeat(70));

    const summary = tracker.getSummary();
    console.log(`\nTotal Tests: ${summary.total}`);
    console.log(`Passed: ${summary.passed}`);
    console.log(`Failed: ${summary.failed}`);
    console.log(`Success Rate: ${summary.success_rate}`);
    console.log(`Duration: ${summary.duration_ms}ms`);
    console.log('\n' + '='.repeat(70));
  });
});

module.exports = {
  PersistenceStorage,
  SystemStateManager,
  PayloadPersistenceManager,
  TestResultTracker,
  describe,
  it,
  expect
};
