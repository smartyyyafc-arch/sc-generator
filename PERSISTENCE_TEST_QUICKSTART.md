# Persistence Test Suite - Quick Start Guide

## Overview

The Persistence Test Suite provides **42 comprehensive tests** covering 9 distinct restart and crash scenarios to verify data survival across system boundaries.

## Quick Start

### 1. File Location
```
/home/user/sc-generator/persistence-restart-test-suite.js
```

### 2. Run All Tests
```bash
# Using npm test (if configured)
npm test -- persistence-restart-test-suite.js

# Using Jest directly
npx jest persistence-restart-test-suite.js

# Using Node with Jest globals
node -r jest-globals persistence-restart-test-suite.js
```

### 3. Run Specific Test Suite
```bash
# Basic restart scenarios only
npx jest -t "Basic System Restart Scenarios"

# Payload persistence only
npx jest -t "Payload Persistence Scenarios"

# Crash recovery only
npx jest -t "Crash Recovery Scenarios"
```

### 4. Run Single Test
```bash
npx jest -t "should preserve data across single restart"
```

## Test Categories (42 Total)

### Category 1: Basic Restart (5 tests)
- Data preservation across restart
- Boot counter increment
- Boot timestamp updates
- Multiple rapid restarts
- Data integrity verification

### Category 2: Payload Persistence (5 tests)
- Payload storage and retrieval
- Execution count tracking
- Multiple concurrent payloads
- Timestamp updates
- Payload deletion

### Category 3: Graceful Shutdown (2 tests)
- State preservation on shutdown
- Graceful shutdown marker recording

### Category 4: Crash Recovery (3 tests)
- Data recovery after crash
- Crash detection on restart
- Transaction log survival

### Category 5: Sequential Restarts (3 tests)
- 10 sequential restart handling
- Incrementing value preservation
- Independent state cycles

### Category 6: Mixed Scenarios (4 tests)
- Graceful shutdown + restart
- Crash + recovery restart
- Mixed payload scenarios
- Burst payloads with crash

### Category 7: Edge Cases (5 tests)
- Empty value persistence
- Very long keys (1000+ chars)
- Large data (100KB+)
- Special characters
- Complex JSON structures

### Category 8: Concurrency (2 tests)
- Concurrent writes before restart
- Concurrent writes through restart

### Category 9: Performance (2 tests)
- Initialization performance (< 1s)
- Large-scale operations (100 ops < 5s)

## Key Test Examples

### Example 1: Basic Restart Test
```javascript
it('should preserve data across single restart', async () => {
  // Write data before restart
  await stateManager.storage.write('test_data', 'value_123');
  
  // Simulate restart
  await stateManager.simulateRestart();
  
  // Verify data survived
  const recovered = await stateManager.storage.read('test_data');
  expect(recovered).toBe('value_123');
});
```

### Example 2: Payload Execution Tracking
```javascript
it('should track payload execution count', async () => {
  // Store payload
  await payloadManager.storePayload('payload_1', { command: 'test' });
  
  // Execute 
  let payload = await payloadManager.executePayload('payload_1');
  expect(payload.execution_count).toBe(1);
  
  // Restart - payload persists
  await stateManager.simulateRestart();
  
  // Execute again after restart
  payload = await payloadManager.executePayload('payload_1');
  expect(payload.execution_count).toBe(2);
});
```

### Example 3: Crash Recovery
```javascript
it('should preserve committed data after crash', async () => {
  // Write critical data
  await stateManager.storage.write('critical', 'important_value');
  
  // Crash without graceful shutdown
  await stateManager.simulateCrash();
  
  // Recovery restart
  stateManager.isRunning = true;
  await stateManager.initialize();
  
  // Verify data survived
  const recovered = await stateManager.storage.read('critical');
  expect(recovered).toBe('important_value');
});
```

## Interpreting Results

### Sample Output:
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

### Result Interpretation:
- **Passed ≥ 40/42**: System persistence working correctly
- **Passed 35-39/42**: Minor issues detected, review failures
- **Passed < 35/42**: Significant persistence issues, investigate

## Common Test Scenarios

### Scenario A: Daily Restart Cycle
Tests simulating application surviving daily system restart:
- Write configuration
- Simulate restart (boot count = 2)
- Verify configuration intact
- Repeat 10 times

### Scenario B: Crash + Recovery
Tests simulating unexpected crash and recovery:
- Write critical payload
- Simulate crash (ungraceful shutdown)
- Simulate recovery restart
- Verify payload intact and execution count preserved

### Scenario C: Payload Lifecycle
Tests complete payload lifecycle:
1. Store payload (execution_count = 0)
2. Execute payload (execution_count = 1)
3. Restart system
4. Retrieve payload (execution_count = 1)
5. Execute again (execution_count = 2)

### Scenario D: Concurrent Writes
Tests handling concurrent persistence operations:
- 20 concurrent writes
- Verify all data survives
- No corruption or loss

## Performance Expectations

| Operation | Expected | Limit |
|-----------|----------|-------|
| Initialize System | 50ms | 1s |
| Single Write | 2ms | 10ms |
| Single Read | 1ms | 10ms |
| Restart Cycle | 150ms | 500ms |
| 100 Operations | 500ms | 5s |

## Troubleshooting

### Tests Fail to Run
```bash
# Install dependencies
npm install jest --save-dev

# Verify Jest is available
npx jest --version
```

### Performance Issues
- Tests may be slower on slow disks
- Reduce operation counts for resource-constrained systems
- Increase timeout values if needed

### File Permission Errors
```bash
# Ensure temp directory is writable
chmod 777 /tmp
```

### Cleanup Issues
```bash
# Manual cleanup of test directories
rm -rf /tmp/persistence_test_*
rm -rf /tmp/payload_test_*
rm -rf /tmp/shutdown_test_*
rm -rf /tmp/crash_test_*
rm -rf /tmp/sequential_test_*
rm -rf /tmp/mixed_test_*
rm -rf /tmp/edge_test_*
rm -rf /tmp/concurrent_test_*
rm -rf /tmp/perf_test_*
```

## Integration with CI/CD

### GitHub Actions Example:
```yaml
- name: Run Persistence Tests
  run: npx jest persistence-restart-test-suite.js
  
- name: Upload Results
  if: always()
  uses: actions/upload-artifact@v2
  with:
    name: test-results
    path: ./test-results.json
```

### Jenkins Pipeline:
```groovy
stage('Persistence Tests') {
  steps {
    sh 'npx jest persistence-restart-test-suite.js --json --outputFile=results.json'
    junit 'results.json'
  }
}
```

## Success Criteria Checklist

- [ ] All 42 tests pass
- [ ] Success rate ≥ 95%
- [ ] No data loss detected
- [ ] Boot counters monotonically increasing
- [ ] Payload execution counts accurate
- [ ] Special characters preserved
- [ ] Large values handled correctly
- [ ] Concurrent operations safe
- [ ] Performance within limits

## Next Steps

1. **Run Baseline**: Execute all tests to establish baseline
2. **Document Results**: Record initial performance metrics
3. **Monitor Changes**: Run before and after code changes
4. **Investigate Failures**: Debug any failing tests
5. **Extend Tests**: Add custom test scenarios as needed

## Related Documentation

- `PERSISTENCE_TEST_SUITE_README.md` - Detailed documentation
- `registry-storage-test-suite.js` - Registry storage tests
- `test_persistence_reboot.py` - Python-based reboot tests
- `persistence_manager.py` - Payload generation

## Support

For detailed information, see: `PERSISTENCE_TEST_SUITE_README.md`

---

**Last Updated**: 2026-06-29  
**Total Tests**: 42  
**Target Success Rate**: 95%+  
**Estimated Runtime**: 2-5 seconds
