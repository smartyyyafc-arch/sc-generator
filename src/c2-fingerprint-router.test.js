/**
 * C2 Fingerprint Router - Test Suite
 * Comprehensive tests for beacon fingerprint routing
 */

const {
  C2FingerprintRouter,
  BeaconFingerprint,
  FingerprintComponent,
  C2Server,
  RoutingRule,
  FingerprintType,
  MatchingAlgorithm,
  RoutingStrategy
} = require('./c2-fingerprint-router');

/**
 * Test Suite Runner
 */
class TestRunner {
  constructor() {
    this.passed = 0;
    this.failed = 0;
    this.tests = [];
  }

  assert(condition, message) {
    if (!condition) {
      throw new Error(`Assertion failed: ${message}`);
    }
  }

  assertEqual(actual, expected, message) {
    if (actual !== expected) {
      throw new Error(`Assertion failed: ${message} (expected ${expected}, got ${actual})`);
    }
  }

  test(name, fn) {
    try {
      fn.call(this);
      this.passed++;
      console.log(`✓ ${name}`);
    } catch (error) {
      this.failed++;
      console.error(`✗ ${name}`);
      console.error(`  ${error.message}`);
    }
  }

  report() {
    const total = this.passed + this.failed;
    const percentage = total > 0 ? ((this.passed / total) * 100).toFixed(2) : 0;
    console.log('\n' + '='.repeat(80));
    console.log('TEST REPORT');
    console.log('='.repeat(80));
    console.log(`Passed: ${this.passed}/${total} (${percentage}%)`);
    console.log(`Failed: ${this.failed}/${total}`);
    console.log('='.repeat(80) + '\n');
    return this.failed === 0;
  }
}

// Initialize test runner
const runner = new TestRunner();

// ============================================================================
// FINGERPRINT COMPONENT TESTS
// ============================================================================

console.log('\n' + '='.repeat(80));
console.log('FINGERPRINT COMPONENT TESTS');
console.log('='.repeat(80));

runner.test('Create fingerprint component', function() {
  const component = new FingerprintComponent(
    FingerprintType.SYSTEM_CONFIG,
    'Windows-10-x64',
    2.0
  );
  this.assert(component.componentType === FingerprintType.SYSTEM_CONFIG, 'Type mismatch');
  this.assert(component.value === 'Windows-10-x64', 'Value mismatch');
  this.assert(component.weight === 2.0, 'Weight mismatch');
});

runner.test('Fingerprint component has timestamp', function() {
  const component = new FingerprintComponent(FingerprintType.BEACON_ID, 'beacon-001');
  this.assert(component.timestamp, 'Timestamp missing');
  this.assert(component.timestamp.length > 0, 'Timestamp empty');
});

// ============================================================================
// BEACON FINGERPRINT TESTS
// ============================================================================

console.log('\n' + '='.repeat(80));
console.log('BEACON FINGERPRINT TESTS');
console.log('='.repeat(80));

runner.test('Create beacon fingerprint', function() {
  const components = [
    new FingerprintComponent(FingerprintType.SYSTEM_CONFIG, 'Windows-10-x64', 2.0),
    new FingerprintComponent(FingerprintType.PROCESS_INFO, 'explorer.exe', 1.5),
    new FingerprintComponent(FingerprintType.NETWORK_CONFIG, '192.168.1.100', 1.0)
  ];

  const fingerprint = new BeaconFingerprint('beacon-001', components);
  this.assert(fingerprint.beaconId === 'beacon-001', 'Beacon ID mismatch');
  this.assert(fingerprint.components.length === 3, 'Component count mismatch');
});

runner.test('Fingerprint generates hashes', function() {
  const components = [
    new FingerprintComponent(FingerprintType.SYSTEM_CONFIG, 'Linux-5.10-x64', 2.0)
  ];
  const fingerprint = new BeaconFingerprint('beacon-002', components);

  this.assert(fingerprint.fingerprintHash.length === 64, 'SHA256 hash length incorrect');
  this.assert(fingerprint.checksum.length === 32, 'MD5 checksum length incorrect');
});

runner.test('Fingerprint hash consistency', function() {
  const components = [
    new FingerprintComponent(FingerprintType.SYSTEM_CONFIG, 'Windows-10-x64', 2.0)
  ];
  const fp1 = new BeaconFingerprint('beacon-003', components);

  components[0].weight = 2.0; // No change
  const fp2 = new BeaconFingerprint('beacon-003', components);

  this.assert(fp1.fingerprintHash === fp2.fingerprintHash, 'Hash inconsistency');
});

runner.test('Add component to fingerprint', function() {
  const fingerprint = new BeaconFingerprint('beacon-004', [
    new FingerprintComponent(FingerprintType.SYSTEM_CONFIG, 'Windows-10-x64', 2.0)
  ]);

  const oldHash = fingerprint.fingerprintHash;
  fingerprint.addComponent(
    new FingerprintComponent(FingerprintType.PROCESS_INFO, 'explorer.exe', 1.5)
  );

  this.assert(fingerprint.components.length === 2, 'Component not added');
  this.assert(fingerprint.fingerprintHash !== oldHash, 'Hash should change after adding component');
});

runner.test('Get component by type', function() {
  const fingerprint = new BeaconFingerprint('beacon-005', [
    new FingerprintComponent(FingerprintType.SYSTEM_CONFIG, 'Linux-5.10', 2.0),
    new FingerprintComponent(FingerprintType.PROCESS_INFO, 'systemd', 1.5)
  ]);

  const sysComponent = fingerprint.getComponent(FingerprintType.SYSTEM_CONFIG);
  this.assert(sysComponent !== undefined, 'Component not found');
  this.assert(sysComponent.value === 'Linux-5.10', 'Wrong component retrieved');
});

// ============================================================================
// C2 SERVER TESTS
// ============================================================================

console.log('\n' + '='.repeat(80));
console.log('C2 SERVER TESTS');
console.log('='.repeat(80));

runner.test('Create C2 server', function() {
  const server = new C2Server('Primary', 'c2.example.com', 443, 'https', 'US-EAST');
  this.assert(server.name === 'Primary', 'Name mismatch');
  this.assert(server.port === 443, 'Port mismatch');
  this.assert(server.region === 'US-EAST', 'Region mismatch');
});

runner.test('Server generates URI', function() {
  const server = new C2Server('Test', 'test.com', 8443, 'https');
  const uri = server.getUri();
  this.assert(uri === 'https://test.com:8443', 'URI mismatch');
});

runner.test('Server capacity tracking', function() {
  const server = new C2Server('Test', 'test.com', 443);
  server.beaconLimit = 10;

  this.assert(server.hasCapacity(), 'Should have capacity initially');
  this.assertEqual(server.getLoadPercent(), 0, 'Initial load should be 0%');

  for (let i = 0; i < 10; i++) {
    server.registerBeacon(`beacon-${i}`);
  }

  this.assert(!server.hasCapacity(), 'Should be at capacity');
  this.assertEqual(server.getLoadPercent(), 100, 'Load should be 100%');
});

runner.test('Server beacon registration', function() {
  const server = new C2Server('Test', 'test.com', 443);
  server.registerBeacon('beacon-001');
  server.registerBeacon('beacon-002');

  this.assert(server.activeBeacons.has('beacon-001'), 'Beacon not registered');
  this.assert(server.activeBeacons.has('beacon-002'), 'Beacon not registered');
  this.assert(server.activeBeacons.size === 2, 'Beacon count mismatch');
});

runner.test('Server fingerprint acceptance', function() {
  const server = new C2Server('Test', 'test.com', 443);
  const fpHash = 'abc123def456';

  server.acceptFingerprint(fpHash);
  this.assert(server.isFingerprintAccepted(fpHash), 'Fingerprint not accepted');
  this.assert(server.isFingerprintAccepted('unknown'), 'Accept all when set is empty after adding');
});

// ============================================================================
// ROUTER INITIALIZATION TESTS
// ============================================================================

console.log('\n' + '='.repeat(80));
console.log('ROUTER INITIALIZATION TESTS');
console.log('='.repeat(80));

runner.test('Create router instance', function() {
  const router = new C2FingerprintRouter();
  this.assert(router instanceof C2FingerprintRouter, 'Router instance failed');
  this.assert(router.servers.size === 0, 'Initial server count should be 0');
});

runner.test('Register server with router', function() {
  const router = new C2FingerprintRouter();
  const serverId = router.registerServer('Primary', 'c2.example.com', 443);

  this.assert(serverId, 'Server ID not returned');
  this.assert(router.servers.has(serverId), 'Server not registered');
});

runner.test('Register multiple servers', function() {
  const router = new C2FingerprintRouter();
  const ids = [];

  for (let i = 0; i < 3; i++) {
    ids.push(router.registerServer(`Server${i}`, `c2-${i}.example.com`, 443));
  }

  this.assert(router.servers.size === 3, 'Server count mismatch');
  ids.forEach(id => {
    this.assert(router.servers.has(id), `Server ${id} not found`);
  });
});

// ============================================================================
// FINGERPRINT MATCHING TESTS
// ============================================================================

console.log('\n' + '='.repeat(80));
console.log('FINGERPRINT MATCHING TESTS');
console.log('='.repeat(80));

runner.test('Exact match algorithm', function() {
  const router = new C2FingerprintRouter();
  const component = new FingerprintComponent(FingerprintType.SYSTEM_CONFIG, 'Windows-10', 1.0);

  const result = router.matchFingerprintComponent(
    component,
    'Windows-10',
    MatchingAlgorithm.EXACT
  );

  this.assert(result.matches === true, 'Exact match failed');
  this.assert(result.confidence === 1.0, 'Confidence should be 1.0');
});

runner.test('Exact match failure', function() {
  const router = new C2FingerprintRouter();
  const component = new FingerprintComponent(FingerprintType.SYSTEM_CONFIG, 'Windows-10', 1.0);

  const result = router.matchFingerprintComponent(
    component,
    'Windows-11',
    MatchingAlgorithm.EXACT
  );

  this.assert(result.matches === false, 'Should not match');
  this.assert(result.confidence === 0.0, 'Confidence should be 0.0');
});

runner.test('Fuzzy match algorithm', function() {
  const router = new C2FingerprintRouter();
  const component = new FingerprintComponent(
    FingerprintType.SYSTEM_CONFIG,
    'Windows-10-x64',
    1.0,
    0.2 // 20% tolerance
  );

  const result = router.matchFingerprintComponent(
    component,
    'Windows-10-x86',
    MatchingAlgorithm.FUZZY
  );

  this.assert(result.confidence > 0, 'Should have some confidence');
});

runner.test('Probabilistic match', function() {
  const router = new C2FingerprintRouter();
  const component = new FingerprintComponent(
    FingerprintType.SYSTEM_CONFIG,
    'Windows_10_Enterprise',
    1.0
  );

  const result = router.matchFingerprintComponent(
    component,
    'Windows_10_Professional',
    MatchingAlgorithm.PROBABILISTIC
  );

  this.assert(result.confidence >= 0, 'Confidence should be valid');
  this.assert(result.confidence <= 1.0, 'Confidence should not exceed 1.0');
});

// ============================================================================
// ROUTING RULE TESTS
// ============================================================================

console.log('\n' + '='.repeat(80));
console.log('ROUTING RULE TESTS');
console.log('='.repeat(80));

runner.test('Create routing rule', function() {
  const router = new C2FingerprintRouter();
  const ruleId = router.createRoutingRule(
    'Windows Systems',
    'Route Windows to primary',
    { system_config: 'Windows.*' },
    ['server-1'],
    { priority: 10 }
  );

  this.assert(ruleId, 'Rule ID not returned');
  this.assert(router.routingRules.has(ruleId), 'Rule not stored');
});

runner.test('Routing rule priorities', function() {
  const router = new C2FingerprintRouter();
  const serverId = router.registerServer('Test', 'test.com', 443);

  const rule1 = router.createRoutingRule(
    'Rule1',
    'Low priority',
    {},
    [serverId],
    { priority: 5 }
  );

  const rule2 = router.createRoutingRule(
    'Rule2',
    'High priority',
    {},
    [serverId],
    { priority: 10 }
  );

  const rules = Array.from(router.routingRules.values())
    .sort((a, b) => b.priority - a.priority);

  this.assert(rules[0].ruleId === rule2, 'Priority sorting failed');
});

// ============================================================================
// BEACON ROUTING TESTS
// ============================================================================

console.log('\n' + '='.repeat(80));
console.log('BEACON ROUTING TESTS');
console.log('='.repeat(80));

runner.test('Route beacon to server', function() {
  const router = new C2FingerprintRouter();
  const serverId = router.registerServer('Primary', 'c2.example.com', 443);

  const components = [
    new FingerprintComponent(FingerprintType.SYSTEM_CONFIG, 'Windows-10-x64', 2.0)
  ];

  const fingerprint = new BeaconFingerprint('beacon-001', components);
  router.registerBeaconFingerprint('beacon-001', components, serverId);

  // Create routing rule
  router.createRoutingRule(
    'Windows Route',
    'Route Windows systems',
    { system_config: 'Windows-10-x64' },
    [serverId],
    { priority: 10, matchingAlgorithm: MatchingAlgorithm.EXACT }
  );

  const decision = router.routeBeacon('beacon-001', fingerprint);

  this.assert(decision.selectedServer !== null, 'No server selected');
  this.assert(decision.selectedServer.serverId === serverId, 'Wrong server selected');
});

runner.test('Beacon registered with server', function() {
  const router = new C2FingerprintRouter();
  const serverId = router.registerServer('Primary', 'c2.example.com', 443);

  const components = [
    new FingerprintComponent(FingerprintType.SYSTEM_CONFIG, 'Windows-10-x64', 2.0)
  ];

  router.registerBeaconFingerprint('beacon-001', components, serverId);

  // Create rule to route to this server
  router.createRoutingRule(
    'Route',
    'Route beacon',
    { system_config: 'Windows-10-x64' },
    [serverId],
    { matchingAlgorithm: MatchingAlgorithm.EXACT }
  );

  const fingerprint = new BeaconFingerprint('beacon-001', components);
  router.routeBeacon('beacon-001', fingerprint);

  const server = router.servers.get(serverId);
  this.assert(server.activeBeacons.has('beacon-001'), 'Beacon not registered with server');
});

runner.test('Round-robin routing strategy', function() {
  const router = new C2FingerprintRouter();
  const server1 = router.registerServer('Server1', 'c2-1.com', 443);
  const server2 = router.registerServer('Server2', 'c2-2.com', 443);

  // Create rule with round-robin
  router.createRoutingRule(
    'RoundRobin',
    'Distribute load',
    {},
    [server1, server2],
    { routingStrategy: RoutingStrategy.ROUND_ROBIN }
  );

  const components = [
    new FingerprintComponent(FingerprintType.SYSTEM_CONFIG, 'Linux', 1.0)
  ];

  // Route multiple beacons
  const decision1 = router.routeBeacon('beacon-001', new BeaconFingerprint('beacon-001', components));
  const decision2 = router.routeBeacon('beacon-002', new BeaconFingerprint('beacon-002', components));

  // At least one should use each server (or same if odd distribution)
  this.assert(decision1.selectedServer !== null, 'Decision 1 failed');
  this.assert(decision2.selectedServer !== null, 'Decision 2 failed');
});

runner.test('Load-balanced routing strategy', function() {
  const router = new C2FingerprintRouter();
  const server1 = router.registerServer('Server1', 'c2-1.com', 443);
  const server2 = router.registerServer('Server2', 'c2-2.com', 443);

  // Set different capacities
  const s1 = router.servers.get(server1);
  const s2 = router.servers.get(server2);

  s1.beaconLimit = 10;
  s2.beaconLimit = 10;

  // Add beacons to server1
  for (let i = 0; i < 5; i++) {
    s1.registerBeacon(`old-beacon-${i}`);
  }

  // Create rule
  router.createRoutingRule(
    'LoadBalance',
    'Load balance',
    {},
    [server1, server2],
    { routingStrategy: RoutingStrategy.LOAD_BALANCED }
  );

  // Route new beacon - should go to server2 (less loaded)
  const components = [
    new FingerprintComponent(FingerprintType.SYSTEM_CONFIG, 'Windows', 1.0)
  ];

  const decision = router.routeBeacon('beacon-new', new BeaconFingerprint('beacon-new', components));
  this.assert(decision.selectedServer.serverId === server2, 'Should route to less loaded server');
});

// ============================================================================
// STATISTICS AND EXPORT TESTS
// ============================================================================

console.log('\n' + '='.repeat(80));
console.log('STATISTICS AND EXPORT TESTS');
console.log('='.repeat(80));

runner.test('Get routing statistics', function() {
  const router = new C2FingerprintRouter();
  router.registerServer('Server1', 'c2-1.com', 443);

  const stats = router.getRoutingStats();
  this.assert(stats.totalServers === 1, 'Server count mismatch');
  this.assert(stats.totalBeacons === 0, 'Initial beacon count should be 0');
});

runner.test('Export routing configuration', function() {
  const router = new C2FingerprintRouter();
  const serverId = router.registerServer('Primary', 'c2.example.com', 443);

  const config = router.exportRoutingConfig();
  this.assert(config.servers, 'Servers not in config');
  this.assert(config.routingRules, 'Rules not in config');
  this.assert(serverId in config.servers, 'Server not in exported config');
});

runner.test('Clear beacon from tracking', function() {
  const router = new C2FingerprintRouter();
  const serverId = router.registerServer('Server1', 'c2-1.com', 443);

  const components = [
    new FingerprintComponent(FingerprintType.SYSTEM_CONFIG, 'Windows-10', 1.0)
  ];

  router.registerBeaconFingerprint('beacon-001', components, serverId);
  this.assert(router.beaconFingerprints.has('beacon-001'), 'Beacon not registered');

  const cleared = router.clearBeacon('beacon-001');
  this.assert(cleared === true, 'Clear should return true');
  this.assert(!router.beaconFingerprints.has('beacon-001'), 'Beacon still in fingerprints');
});

// ============================================================================
// RUN TEST REPORT
// ============================================================================

const allPassed = runner.report();
process.exit(allPassed ? 0 : 1);
