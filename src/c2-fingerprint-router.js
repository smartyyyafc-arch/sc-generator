/**
 * C2 Fingerprint-Based Router - Server-Side Implementation
 * Intelligent beacon routing and verification using cryptographic fingerprints
 * For authorized pentesting and security research
 */

const crypto = require('crypto');
const EventEmitter = require('events');

/**
 * Routing Strategy Enumeration
 */
const RoutingStrategy = {
  DIRECT: 'direct',
  LOAD_BALANCED: 'load_balanced',
  FAILOVER: 'failover',
  ROUND_ROBIN: 'round_robin',
  GEOLOCATION: 'geolocation',
  LATENCY_OPTIMIZED: 'latency',
  RANDOMIZED: 'randomized'
};

/**
 * Fingerprint Type Enumeration
 */
const FingerprintType = {
  BEACON_ID: 'beacon_id',
  SYSTEM_CONFIG: 'system_config',
  NETWORK_CONFIG: 'network_config',
  PROCESS_INFO: 'process_info',
  BEHAVIORAL: 'behavioral',
  CRYPTO: 'crypto'
};

/**
 * Matching Algorithm Enumeration
 */
const MatchingAlgorithm = {
  EXACT: 'exact',
  FUZZY: 'fuzzy',
  HIERARCHICAL: 'hierarchical',
  PROBABILISTIC: 'probabilistic'
};

/**
 * Fingerprint Component Class
 */
class FingerprintComponent {
  constructor(type, value, weight = 1.0, varianceTolerance = 0.0) {
    this.componentType = type;
    this.value = value;
    this.weight = weight;
    this.varianceTolerance = varianceTolerance;
    this.timestamp = new Date().toISOString();
  }
}

/**
 * Beacon Fingerprint Class
 */
class BeaconFingerprint {
  constructor(beaconId, components = []) {
    this.beaconId = beaconId;
    this.components = components;
    this.fingerprintHash = '';
    this.checksum = '';
    this.createdAt = new Date().toISOString();
    this.lastSeen = new Date().toISOString();
    this.metadata = {};
    this.generateHashes();
  }

  /**
   * Generate fingerprint and checksum hashes
   */
  generateHashes() {
    // Create composite fingerprint string
    const componentStrs = this.components
      .map(c => `${c.componentType}:${c.value}:${c.weight}`)
      .sort()
      .join('|');

    // Generate SHA-256 fingerprint hash
    this.fingerprintHash = crypto
      .createHash('sha256')
      .update(componentStrs)
      .digest('hex');

    // Generate MD5 checksum
    this.checksum = crypto
      .createHash('md5')
      .update(componentStrs)
      .digest('hex');
  }

  /**
   * Add or update component
   */
  addComponent(component) {
    const existingIndex = this.components.findIndex(
      c => c.componentType === component.componentType
    );
    if (existingIndex >= 0) {
      this.components[existingIndex] = component;
    } else {
      this.components.push(component);
    }
    this.generateHashes();
  }

  /**
   * Get component by type
   */
  getComponent(type) {
    return this.components.find(c => c.componentType === type);
  }

  /**
   * Update last seen timestamp
   */
  updateLastSeen() {
    this.lastSeen = new Date().toISOString();
  }
}

/**
 * C2 Server Class
 */
class C2Server {
  constructor(name, address, port, protocol = 'https', region = '') {
    this.serverId = crypto.randomBytes(8).toString('hex');
    this.name = name;
    this.address = address;
    this.port = port;
    this.protocol = protocol;
    this.region = region;
    this.fallbackServers = [];
    this.acceptedFingerprints = new Set();
    this.beaconLimit = 100;
    this.activeBeacons = new Set();
    this.isActive = true;
    this.latencyMs = 0;
    this.capacityPercent = 0;
    this.metadata = {};
    this.statsLastUpdated = new Date().toISOString();
  }

  /**
   * Get server URI
   */
  getUri() {
    return `${this.protocol}://${this.address}:${this.port}`;
  }

  /**
   * Check if server has capacity
   */
  hasCapacity() {
    return this.activeBeacons.size < this.beaconLimit && this.isActive;
  }

  /**
   * Get current load percentage
   */
  getLoadPercent() {
    return (this.activeBeacons.size / this.beaconLimit) * 100;
  }

  /**
   * Register beacon with server
   */
  registerBeacon(beaconId) {
    this.activeBeacons.add(beaconId);
    this.capacityPercent = this.getLoadPercent();
  }

  /**
   * Unregister beacon from server
   */
  unregisterBeacon(beaconId) {
    this.activeBeacons.delete(beaconId);
    this.capacityPercent = this.getLoadPercent();
  }

  /**
   * Accept fingerprint for this server
   */
  acceptFingerprint(fingerprintHash) {
    this.acceptedFingerprints.add(fingerprintHash);
  }

  /**
   * Check if fingerprint is accepted
   */
  isFingerprintAccepted(fingerprintHash) {
    if (this.acceptedFingerprints.size === 0) return true; // Accept all if empty
    return this.acceptedFingerprints.has(fingerprintHash);
  }

  /**
   * Export server configuration
   */
  export() {
    return {
      serverId: this.serverId,
      name: this.name,
      address: this.address,
      port: this.port,
      protocol: this.protocol,
      region: this.region,
      uri: this.getUri(),
      activeBeacons: this.activeBeacons.size,
      beaconLimit: this.beaconLimit,
      capacityPercent: this.capacityPercent,
      isActive: this.isActive,
      latencyMs: this.latencyMs
    };
  }
}

/**
 * Routing Rule Class
 */
class RoutingRule {
  constructor(
    name,
    description,
    fingerprintPattern = {},
    targetServers = [],
    options = {}
  ) {
    this.ruleId = crypto.randomBytes(8).toString('hex');
    this.name = name;
    this.description = description;
    this.fingerprintPattern = fingerprintPattern;
    this.targetServers = targetServers;
    this.routingStrategy = options.routingStrategy || RoutingStrategy.DIRECT;
    this.matchingAlgorithm = options.matchingAlgorithm || MatchingAlgorithm.EXACT;
    this.matchThreshold = options.matchThreshold || 1.0;
    this.priority = options.priority || 0;
    this.isEnabled = options.isEnabled !== false;
    this.metadata = options.metadata || {};
  }

  /**
   * Check if rule is applicable
   */
  isApplicable() {
    return this.isEnabled && this.targetServers.length > 0;
  }

  /**
   * Export rule configuration
   */
  export() {
    return {
      ruleId: this.ruleId,
      name: this.name,
      description: this.description,
      routingStrategy: this.routingStrategy,
      matchingAlgorithm: this.matchingAlgorithm,
      matchThreshold: this.matchThreshold,
      priority: this.priority,
      targetServerCount: this.targetServers.length,
      isEnabled: this.isEnabled
    };
  }
}

/**
 * Routing Decision Class
 */
class RoutingDecision {
  constructor(beaconId, selectedServer) {
    this.beaconId = beaconId;
    this.selectedServer = selectedServer;
    this.decisionTimestamp = new Date().toISOString();
    this.confidenceScore = 1.0;
    this.matchingRuleId = '';
    this.alternativeServers = [];
    this.routingPath = [];
  }
}

/**
 * Fingerprint Validator Class
 */
class FingerprintValidator {
  constructor(hmacKey = null) {
    this.hmacKey = hmacKey || crypto
      .createHash('sha256')
      .update('c2_fingerprint_validator')
      .digest();
  }

  /**
   * Create HMAC signature for fingerprint
   */
  createSignature(fingerprint) {
    const message = `${fingerprint.beaconId}:${fingerprint.fingerprintHash}`;
    return crypto
      .createHmac('sha256', this.hmacKey)
      .update(message)
      .digest('hex');
  }

  /**
   * Verify fingerprint signature
   */
  verifySignature(fingerprint, signature) {
    const expectedSig = this.createSignature(fingerprint);
    return crypto.timingSafeEqual(
      Buffer.from(expectedSig),
      Buffer.from(signature)
    );
  }

  /**
   * Validate component consistency
   */
  validateComponentConsistency(components) {
    if (!components || components.length === 0) return false;

    // At least one system_config component required
    const typesPresent = new Set(components.map(c => c.componentType));
    if (!typesPresent.has(FingerprintType.SYSTEM_CONFIG)) return false;

    // Verify weights sum reasonably
    const totalWeight = components.reduce((sum, c) => sum + c.weight, 0);
    return totalWeight > 0 && totalWeight <= 100;
  }

  /**
   * Detect fingerprint tampering
   */
  detectTampering(fingerprint, originalHash) {
    const currentHash = fingerprint.fingerprintHash;
    return currentHash !== originalHash;
  }
}

/**
 * C2 Fingerprint Router Class
 */
class C2FingerprintRouter extends EventEmitter {
  constructor() {
    super();
    this.servers = new Map();
    this.routingRules = new Map();
    this.beaconFingerprints = new Map();
    this.routingHistory = [];
    this.validator = new FingerprintValidator();
    this.fingerprintCache = new Map(); // hash -> beaconId
    this.maxHistorySize = 10000;
  }

  /**
   * Register C2 server
   */
  registerServer(name, address, port, protocol = 'https', region = '') {
    const server = new C2Server(name, address, port, protocol, region);
    this.servers.set(server.serverId, server);
    this.emit('server:registered', { server });
    return server.serverId;
  }

  /**
   * Register beacon fingerprint
   */
  registerBeaconFingerprint(beaconId, components, targetServerId = null) {
    // Validate components
    if (!this.validator.validateComponentConsistency(components)) {
      throw new Error('Invalid fingerprint components');
    }

    // Create fingerprint
    const fingerprint = new BeaconFingerprint(beaconId, components);

    // Store fingerprint
    this.beaconFingerprints.set(beaconId, fingerprint);
    this.fingerprintCache.set(fingerprint.fingerprintHash, beaconId);

    // Register with target server
    if (targetServerId && this.servers.has(targetServerId)) {
      const server = this.servers.get(targetServerId);
      server.acceptFingerprint(fingerprint.fingerprintHash);
      fingerprint.metadata.targetServer = targetServerId;
    }

    this.emit('beacon:registered', { fingerprint });
    return fingerprint;
  }

  /**
   * Create routing rule
   */
  createRoutingRule(
    name,
    description,
    fingerprintPattern,
    targetServers,
    options = {}
  ) {
    const rule = new RoutingRule(
      name,
      description,
      fingerprintPattern,
      targetServers,
      options
    );
    this.routingRules.set(rule.ruleId, rule);
    this.emit('rule:created', { rule });
    return rule.ruleId;
  }

  /**
   * Match fingerprint component against pattern
   */
  matchFingerprintComponent(component, patternValue, algorithm) {
    switch (algorithm) {
      case MatchingAlgorithm.EXACT:
        const exactMatch = component.value === patternValue;
        return {
          matches: exactMatch,
          confidence: exactMatch ? 1.0 : 0.0
        };

      case MatchingAlgorithm.FUZZY:
        const fuzzyScore = this.fuzzyMatchRatio(component.value, patternValue);
        const tolerance = component.varianceTolerance;
        return {
          matches: fuzzyScore >= (1.0 - tolerance),
          confidence: fuzzyScore
        };

      case MatchingAlgorithm.PROBABILISTIC:
        const probScore = this.probabilisticMatch(component.value, patternValue);
        return {
          matches: probScore > 0.5,
          confidence: probScore
        };

      default:
        return { matches: false, confidence: 0.0 };
    }
  }

  /**
   * Calculate fuzzy match ratio
   */
  fuzzyMatchRatio(s1, s2) {
    if (s1 === s2) return 1.0;
    if (!s1 || !s2) return 0.0;

    const set1 = new Set(s1.split(''));
    const set2 = new Set(s2.split(''));
    const common = new Set([...set1].filter(x => set2.has(x)));
    const union = new Set([...set1, ...set2]);

    return union.size > 0 ? common.size / union.size : 0.0;
  }

  /**
   * Calculate probabilistic match score (Jaccard similarity)
   */
  probabilisticMatch(value, pattern) {
    if (value === pattern) return 1.0;

    const set1 = new Set(value.split('_'));
    const set2 = new Set(pattern.split('_'));
    const intersection = new Set([...set1].filter(x => set2.has(x)));
    const union = new Set([...set1, ...set2]);

    return union.size > 0 ? intersection.size / union.size : 0.0;
  }

  /**
   * Match fingerprint to routing rule
   */
  matchFingerprintToRule(fingerprint, rule) {
    const pattern = rule.fingerprintPattern;

    // Empty pattern matches all
    if (Object.keys(pattern).length === 0) {
      return { matches: true, confidence: 1.0 };
    }

    let matches = [];
    let weights = [];

    for (const component of fingerprint.components) {
      const typeStr = component.componentType;

      if (typeStr in pattern) {
        const patternValue = pattern[typeStr];
        const result = this.matchFingerprintComponent(
          component,
          patternValue,
          rule.matchingAlgorithm
        );
        matches.push(result.matches);
        weights.push(component.weight);
      } else {
        matches.push(true);
        weights.push(0.1);
      }
    }

    if (matches.length === 0) {
      return { matches: false, confidence: 0.0 };
    }

    // Calculate weighted confidence
    let matchedWeight = 0;
    for (let i = 0; i < matches.length; i++) {
      if (matches[i]) matchedWeight += weights[i];
    }

    const totalWeight = weights.reduce((sum, w) => sum + w, 0);
    const overallConfidence = totalWeight > 0 ? matchedWeight / totalWeight : 0.0;
    const ruleMatches = overallConfidence >= rule.matchThreshold;

    return { matches: ruleMatches, confidence: overallConfidence };
  }

  /**
   * Route beacon to correct C2 server
   */
  routeBeacon(beaconId, fingerprint = null, forceServerId = null) {
    // Get or lookup fingerprint
    if (!fingerprint) {
      if (!this.beaconFingerprints.has(beaconId)) {
        throw new Error(`Beacon ${beaconId} fingerprint not found`);
      }
      fingerprint = this.beaconFingerprints.get(beaconId);
    }

    // Verify fingerprint
    if (!this.validator.validateComponentConsistency(fingerprint.components)) {
      throw new Error(`Invalid fingerprint for beacon ${beaconId}`);
    }

    const decision = new RoutingDecision(beaconId, null);
    decision.routingPath.push('route_beacon_entry');

    // Force routing if specified
    if (forceServerId) {
      if (!this.servers.has(forceServerId)) {
        throw new Error(`Server ${forceServerId} not found`);
      }
      const server = this.servers.get(forceServerId);
      decision.selectedServer = server;
      decision.confidenceScore = 1.0;
      decision.routingPath.push(`forced_to_${forceServerId}`);
      this.finalizeRouting(decision);
      return decision;
    }

    // Match against routing rules (sorted by priority)
    const sortedRules = Array.from(this.routingRules.values())
      .sort((a, b) => b.priority - a.priority);

    let bestServer = null;
    let bestConfidence = 0.0;

    for (const rule of sortedRules) {
      if (!rule.isApplicable()) continue;

      const result = this.matchFingerprintToRule(fingerprint, rule);

      if (result.matches && result.confidence > bestConfidence) {
        decision.routingPath.push(`matched_rule_${rule.ruleId}`);
        bestConfidence = result.confidence;
        decision.matchingRuleId = rule.ruleId;

        // Select server based on strategy
        const selectedServerId = this.selectServerByStrategy(
          rule.targetServers,
          rule.routingStrategy,
          beaconId
        );

        if (this.servers.has(selectedServerId)) {
          bestServer = this.servers.get(selectedServerId);
          decision.alternativeServers = rule.targetServers
            .filter(sid => sid !== selectedServerId && this.servers.has(sid))
            .map(sid => this.servers.get(sid));
        }
      }
    }

    // Fallback to default routing
    if (!bestServer) {
      decision.routingPath.push('no_rule_match_fallback');
      bestServer = this.getDefaultServer(beaconId);

      if (!bestServer) {
        throw new Error('No available C2 servers');
      }
    }

    decision.selectedServer = bestServer;
    decision.confidenceScore = bestConfidence;
    this.finalizeRouting(decision);
    return decision;
  }

  /**
   * Select server by routing strategy
   */
  selectServerByStrategy(serverIds, strategy, beaconId) {
    if (serverIds.length === 0) return null;

    switch (strategy) {
      case RoutingStrategy.DIRECT:
        return serverIds[0];

      case RoutingStrategy.ROUND_ROBIN: {
        const hash = crypto
          .createHash('md5')
          .update(beaconId)
          .digest('hex');
        const idx = parseInt(hash, 16) % serverIds.length;
        return serverIds[idx];
      }

      case RoutingStrategy.LOAD_BALANCED: {
        const available = serverIds.filter(sid => this.servers.has(sid));
        if (available.length === 0) return serverIds[0];
        return available.reduce((best, sid) => {
          const bestServer = this.servers.get(best);
          const currentServer = this.servers.get(sid);
          return currentServer.getLoadPercent() < bestServer.getLoadPercent() ? sid : best;
        });
      }

      case RoutingStrategy.LATENCY_OPTIMIZED: {
        const available = serverIds.filter(sid => this.servers.has(sid));
        if (available.length === 0) return serverIds[0];
        return available.reduce((best, sid) => {
          const bestLatency = this.servers.get(best).latencyMs;
          const currentLatency = this.servers.get(sid).latencyMs;
          return currentLatency < bestLatency ? sid : best;
        });
      }

      case RoutingStrategy.RANDOMIZED: {
        const idx = Math.floor(Math.random() * serverIds.length);
        return serverIds[idx];
      }

      default:
        return serverIds[0];
    }
  }

  /**
   * Get default server
   */
  getDefaultServer(beaconId) {
    const activeServers = Array.from(this.servers.values())
      .filter(s => s.hasCapacity());

    if (activeServers.length === 0) return null;

    // Return server with lowest load
    return activeServers.reduce((best, current) =>
      current.getLoadPercent() < best.getLoadPercent() ? current : best
    );
  }

  /**
   * Finalize routing and register beacon
   */
  finalizeRouting(decision) {
    if (decision.selectedServer) {
      decision.selectedServer.registerBeacon(decision.beaconId);
      this.routingHistory.push(decision);

      // Maintain history size limit
      if (this.routingHistory.length > this.maxHistorySize) {
        this.routingHistory.shift();
      }

      this.emit('beacon:routed', decision);
    }
  }

  /**
   * Update beacon fingerprint
   */
  updateBeaconFingerprint(beaconId, newComponents) {
    if (!this.beaconFingerprints.has(beaconId)) {
      throw new Error(`Beacon ${beaconId} not found`);
    }

    const oldFp = this.beaconFingerprints.get(beaconId);
    const updatedFp = new BeaconFingerprint(beaconId, newComponents);
    updatedFp.metadata = oldFp.metadata;

    this.beaconFingerprints.set(beaconId, updatedFp);
    this.fingerprintCache.delete(oldFp.fingerprintHash);
    this.fingerprintCache.set(updatedFp.fingerprintHash, beaconId);

    this.emit('beacon:updated', { updatedFp });
    return updatedFp;
  }

  /**
   * Get routing statistics
   */
  getRoutingStats() {
    const stats = {
      totalBeacons: this.beaconFingerprints.size,
      totalServers: this.servers.size,
      totalRoutingRules: this.routingRules.size,
      routingDecisions: this.routingHistory.length,
      beaconsPerServer: {},
      averageConfidence: 0
    };

    for (const [sid, server] of this.servers) {
      stats.beaconsPerServer[sid] = {
        name: server.name,
        count: server.activeBeacons.size,
        capacity: server.getLoadPercent().toFixed(2) + '%'
      };
    }

    if (this.routingHistory.length > 0) {
      const avgConfidence = this.routingHistory.reduce(
        (sum, d) => sum + d.confidenceScore,
        0
      ) / this.routingHistory.length;
      stats.averageConfidence = avgConfidence.toFixed(4);
    }

    return stats;
  }

  /**
   * Export routing configuration
   */
  exportRoutingConfig(includeSecrets = false) {
    const config = {
      servers: {},
      routingRules: {},
      fingerprints: this.beaconFingerprints.size,
      routingDecisions: this.routingHistory.length
    };

    for (const [sid, server] of this.servers) {
      config.servers[sid] = server.export();
    }

    for (const [rid, rule] of this.routingRules) {
      config.routingRules[rid] = rule.export();
    }

    return config;
  }

  /**
   * Clear beacon from tracking
   */
  clearBeacon(beaconId) {
    if (!this.beaconFingerprints.has(beaconId)) {
      return false;
    }

    const fingerprint = this.beaconFingerprints.get(beaconId);

    // Remove from all servers
    for (const server of this.servers.values()) {
      server.unregisterBeacon(beaconId);
      server.acceptedFingerprints.delete(fingerprint.fingerprintHash);
    }

    // Remove fingerprint
    this.beaconFingerprints.delete(beaconId);
    this.fingerprintCache.delete(fingerprint.fingerprintHash);

    this.emit('beacon:cleared', { beaconId });
    return true;
  }
}

// Export classes and constants
module.exports = {
  C2FingerprintRouter,
  BeaconFingerprint,
  FingerprintComponent,
  C2Server,
  RoutingRule,
  RoutingDecision,
  FingerprintValidator,
  RoutingStrategy,
  FingerprintType,
  MatchingAlgorithm
};
