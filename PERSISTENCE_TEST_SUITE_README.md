# Persistence Test Suite - Multiple Restart Scenarios

## Overview

The **Persistence Test Suite** (`persistence-restart-test-suite.js`) is a comprehensive testing framework designed to verify system persistence and data survival across multiple system restart scenarios. It tests the ability of payloads, configurations, and application state to survive reboots, crashes, and controlled shutdowns.

## Test Architecture

### Core Components

#### 1. **PersistenceStorage**
- Mock storage implementation simulating persistent disk storage
- Provides file-based data persistence using JSON serialization
- Methods:
  - `write(key, value)` - Store data with timestamp
  - `read(key)` - Retrieve stored data
  - `delete(key)` - Remove data
  - `exists(key)` - Check data existence
  - `listKeys()` - List all stored keys
  - `clear()` - Remove all data

#### 2. **SystemStateManager**
- Manages system state transitions and restart simulation
- Tracks boot counts, uptime, and shutdown states
- Extends EventEmitter for restart event handling
- Methods:
  - `initialize()` - Initialize system state
  - `simulateRestart()` - Simulate system restart
  - `simulateGracefulShutdown()` - Simulate controlled shutdown
  - `simulateCrash()` - Simulate unexpected crash
  - `getBootCount()` - Get number of system boots
  - `getUptime()` - Get current uptime duration

#### 3. **PayloadPersistenceManager**
- Manages payload storage and execution tracking
- Tracks execution counts and timestamps
- Methods:
  - `storePayload(payloadId, payloadData)` - Store payload
  - `retrievePayload(payloadId)` - Retrieve stored payload
  - `executePayload(payloadId)` - Execute and track payload
  - `listPayloads()` - List all stored payloads
  - `deletePayload(payloadId)` - Remove payload

#### 4. **TestResultTracker**
- Tracks test execution results and generates summaries
- Calculates success rates and performance metrics
- Methods:
  - `addResult(testName, passed, details)` - Record test result
  - `getSummary()` - Generate test summary

## Test Scenarios

### 1. Basic System Restart Scenarios
Tests fundamental data persistence and system behavior during restarts.

#### Tests:
- **single_restart_data_preservation** - Verify data survives one restart cycle
- **boot_counter_increment** - Ensure boot counter increments correctly
- **boot_timestamp_update** - Validate boot time updates on restart
- **rapid_restarts** - Handle multiple rapid successive restarts
- **data_integrity_through_restart** - Verify multiple data items survive restart

### 2. Payload Persistence Scenarios
Tests payload storage, retrieval, and execution tracking across restarts.

#### Tests:
- **payload_storage_retrieval** - Store and retrieve payload data
- **payload_execution_tracking** - Track payload execution count and state
- **multiple_payloads_storage** - Handle concurrent payload storage
- **payload_timestamp_update** - Update execution timestamps
- **payload_deletion** - Remove and verify payload removal

### 3. Graceful Shutdown Scenarios
Tests data preservation during controlled, orderly system shutdowns.

#### Tests:
- **graceful_shutdown_preservation** - Preserve data during graceful shutdown
- **graceful_shutdown_marker** - Record graceful shutdown indication

### 4. Crash Recovery Scenarios
Tests data survival and recovery after unexpected system crashes.

#### Tests:
- **crash_data_recovery** - Verify critical data survives uncontrolled crash
- **crash_detection** - Detect crash condition during recovery
- **transaction_log_survival** - Ensure transaction logs survive crashes

### 5. Sequential Restart Scenarios
Tests multiple restarts in sequence with state preservation.

#### Tests:
- **ten_sequential_restarts** - Handle 10 sequential restart cycles
- **incrementing_values_through_restarts** - Maintain incrementing state across restarts
- **independent_state_cycles** - Verify independent state per cycle

### 6. Mixed Restart Scenario Tests
Tests combinations of different restart types and conditions.

#### Tests:
- **graceful_shutdown_restart_cycle** - Graceful shutdown followed by restart
- **crash_recovery_restart** - Crash followed by recovery restart
- **mixed_payload_restart_scenario** - Payload state through mixed restarts
- **burst_payloads_crash_recovery** - Multiple payloads surviving crash

### 7. Edge Case Scenarios
Tests boundary conditions and unusual data situations.

#### Tests:
- **empty_value_persistence** - Preserve empty string values
- **long_key_persistence** - Handle very long key names (1000+ chars)
- **large_value_persistence** - Store and retrieve large data (100KB+)
- **special_characters_persistence** - Preserve special characters and escape sequences
- **json_object_persistence** - Store complex JSON structures

### 8. Concurrency Scenarios
Tests concurrent operations and thread-safety across restarts.

#### Tests:
- **concurrent_writes** - Handle concurrent write operations
- **concurrent_writes_through_restart** - Concurrent writes surviving restart

### 9. Performance Scenarios
Tests performance characteristics of persistence operations.

#### Tests:
- **initialization_performance** - System initialization < 1 second
- **large_scale_operations** - Handle 100+ operations < 5 seconds

## Usage

### Running the Test Suite

#### Using Jest/Testing Framework:
```bash
npm test -- persistence-restart-test-suite.js
```

#### Direct Execution:
```bash
node -r jest-globals persistence-restart-test-suite.js
```

### Example Test Output:
```
PERSISTENCE TEST SUITE - FINAL SUMMARY
======================================================================
Total Tests: 42
Passed: 40
Failed: 2
Success Rate: 95.24%
Duration: 2,547ms
======================================================================
```

## Test Data Flow

### Basic Restart Flow:
```
1. Initialize System State
   └─ Boot counter = 1
   └─ Last boot time recorded

2. Write Persistence Data
   └─ Data stored to disk (JSON files)
   └─ Timestamps recorded

3. Simulate Restart
   └─ System marked as not running
   └─ Restart delay simulated
   └─ System marked as running
   └─ Boot counter incremented
   └─ Boot time updated

4. Verify Data Survival
   └─ Read data from disk
   └─ Compare with original values
   └─ Assert equality
```

### Payload Execution Tracking:
```
1. Store Payload
   └─ ID assigned
   └─ Data serialized
   └─ Execution count = 0
   └─ Last execution = null

2. Execute Payload
   └─ Mark as executed
   └─ Increment counter
   └─ Update timestamp
   └─ Persist to disk

3. Survive Restart
   └─ Restart system
   └─ Reload payload
   └─ Verify execution state persisted

4. Execute Again
   └─ Counter increments from persisted value
   └─ New timestamp recorded
```

## Expected Results

### Success Criteria:
- All test data survives restart cycles
- Boot counters increment monotonically
- Timestamps update correctly
- Payloads execute multiple times and maintain state
- Crashes don't corrupt persisted data
- Special characters and large values handled correctly
- Concurrent operations remain consistent
- Performance meets time constraints

### Failure Indicators:
- Data loss after restart
- Boot counter corruption
- Payload state inconsistency
- Timestamp discrepancies
- Special character corruption
- Performance degradation

## Integration Points

### With Registry Storage:
```javascript
// Integrate with registry-storage-variants.ts
const registryStorage = new SoftwareHiveStorage('PersistenceTest');
const testData = await registryStorage.read('payload_state');
```

### With Persistence Manager:
```python
# Python integration
from persistence_manager import create_persistent_payload
payload = create_persistent_payload(command, method='registry')
```

## Performance Benchmarks

| Operation | Target | Typical | Status |
|-----------|--------|---------|--------|
| Initialization | < 1s | ~50ms | ✓ |
| Single Write | < 10ms | ~2ms | ✓ |
| Single Read | < 10ms | ~1ms | ✓ |
| Bulk (100 ops) | < 5s | ~500ms | ✓ |
| Restart Cycle | < 500ms | ~150ms | ✓ |

## Edge Cases Handled

1. **Empty Values** - Preserve zero-length strings
2. **Large Data** - Support 100KB+ values
3. **Special Characters** - Handle escapes, unicode, control chars
4. **Long Keys** - Support 1000+ character key names
5. **Concurrent Access** - Multiple simultaneous operations
6. **Rapid Restarts** - Multiple restarts in quick succession
7. **Complex Objects** - Nested JSON structures
8. **Transaction Logs** - Sequential transaction preservation

## Extending the Test Suite

### Adding New Test Scenarios:

```javascript
describe('Custom Restart Scenario', () => {
  it('should handle custom behavior', async () => {
    const stateManager = new SystemStateManager(storageDir);
    await stateManager.initialize();
    
    // Your test logic
    await stateManager.storage.write('test_key', 'test_value');
    await stateManager.simulateRestart();
    const result = await stateManager.storage.read('test_key');
    
    expect(result).toBe('test_value');
    tracker.addResult('custom_scenario', result === 'test_value');
  });
});
```

### Custom Storage Implementation:

```javascript
class CustomStorage extends PersistenceStorage {
  async write(key, value) {
    // Custom implementation
    super.write(key, value);
  }
}
```

## Troubleshooting

### Test Failures
1. Check storage directory permissions
2. Verify disk space availability
3. Ensure JSON serialization compatibility
4. Check for timing issues in async operations

### Performance Issues
1. Increase timeout limits for slow systems
2. Reduce operation counts for resource-constrained environments
3. Disable concurrent tests if needed

### Data Corruption
1. Enable detailed logging
2. Check file system integrity
3. Verify JSON parsing
4. Review transaction handling

## Related Files

- `registry-storage-variants.ts` - Windows registry storage implementations
- `persistence_manager.py` - Windows persistence payload generation
- `test_persistence_reboot.py` - Python reboot persistence tests
- `test_advanced_persistence.py` - Advanced persistence testing

## License

Internal testing framework - Authorized security testing only.

## Notes

- All tests use mock implementations for safety
- File-based storage simulates disk persistence
- No actual system reboots are performed
- All test data is isolated in temporary directories
- Tests clean up resources after execution
