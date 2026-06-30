#!/usr/bin/env python3
"""
C2 Fingerprint-Based Router
Implements intelligent server routing based on beacon fingerprints
Ensures correct C2 server identification and correlation with beacons
For authorized pentesting and security research
"""

import hashlib
import json
import uuid
import hmac
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime
import ipaddress


class RoutingStrategy(Enum):
    """C2 routing strategies"""
    DIRECT = "direct"              # Direct connection to assigned server
    LOAD_BALANCED = "load_balanced"  # Distribute across multiple servers
    FAILOVER = "failover"          # Primary with fallback servers
    ROUND_ROBIN = "round_robin"    # Sequential server rotation
    GEOLOCATION = "geolocation"    # Route based on geo-location
    LATENCY_OPTIMIZED = "latency"  # Choose server with lowest latency
    RANDOMIZED = "randomized"      # Random server selection


class FingerprintType(Enum):
    """Types of fingerprint components"""
    BEACON_ID = "beacon_id"           # Unique beacon identifier
    SYSTEM_CONFIG = "system_config"   # OS/hardware fingerprint
    NETWORK_CONFIG = "network_config" # Network interface fingerprint
    PROCESS_INFO = "process_info"     # Process-level fingerprint
    BEHAVIORAL = "behavioral"         # Behavioral fingerprint (timing, patterns)
    CRYPTO = "crypto"                 # Cryptographic key material


class MatchingAlgorithm(Enum):
    """Fingerprint matching algorithms"""
    EXACT = "exact"                    # Exact match required
    FUZZY = "fuzzy"                    # Fuzzy matching with tolerance
    HIERARCHICAL = "hierarchical"      # Multi-level hierarchical matching
    PROBABILISTIC = "probabilistic"    # Probability-based matching


@dataclass
class FingerprintComponent:
    """Individual fingerprint component"""
    component_type: FingerprintType
    value: str
    weight: float = 1.0  # Importance weight (0-1)
    variance_tolerance: float = 0.0  # Allowed variance for fuzzy matching
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class BeaconFingerprint:
    """Complete beacon fingerprint"""
    beacon_id: str
    components: List[FingerprintComponent]
    fingerprint_hash: str = ""
    checksum: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict = field(default_factory=dict)

    def generate_hashes(self):
        """Generate fingerprint and checksum hashes"""
        # Create composite fingerprint string
        component_strs = [
            f"{c.component_type.value}:{c.value}:{c.weight}"
            for c in sorted(self.components, key=lambda x: x.component_type.value)
        ]
        composite = "|".join(component_strs)

        # Generate hashes
        self.fingerprint_hash = hashlib.sha256(composite.encode()).hexdigest()
        self.checksum = hashlib.md5(composite.encode()).hexdigest()


@dataclass
class C2Server:
    """C2 server configuration"""
    server_id: str
    name: str
    address: str
    port: int
    protocol: str  # http, https, dns, tls
    fallback_servers: List[str] = field(default_factory=list)
    accepted_fingerprints: Set[str] = field(default_factory=set)  # beacon fingerprint hashes
    beacon_limit: int = 100  # Max concurrent beacons
    active_beacons: Set[str] = field(default_factory=set)
    is_active: bool = True
    region: str = ""  # Geographic region
    latency_ms: float = 0.0
    capacity_percent: float = 0.0
    metadata: Dict = field(default_factory=dict)


@dataclass
class RoutingRule:
    """Fingerprint-based routing rule"""
    rule_id: str
    name: str
    description: str
    priority: int = 0  # Higher = higher priority
    fingerprint_pattern: Dict = field(default_factory=dict)  # Pattern to match
    target_servers: List[str] = field(default_factory=list)  # Server IDs
    routing_strategy: RoutingStrategy = RoutingStrategy.DIRECT
    matching_algorithm: MatchingAlgorithm = MatchingAlgorithm.EXACT
    match_threshold: float = 1.0  # For fuzzy/probabilistic matching
    is_enabled: bool = True
    metadata: Dict = field(default_factory=dict)


@dataclass
class RoutingDecision:
    """Routing decision result"""
    beacon_id: str
    selected_server: C2Server
    decision_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence_score: float = 1.0
    matching_rule_id: str = ""
    alternative_servers: List[C2Server] = field(default_factory=list)
    routing_path: List[str] = field(default_factory=list)  # Trace of routing decisions


class FingerprintValidator:
    """Validates and verifies beacon fingerprints"""

    def __init__(self):
        self.hmac_key = hashlib.sha256(b"c2_fingerprint_validator").digest()

    def create_signature(self, fingerprint: BeaconFingerprint) -> str:
        """Create HMAC signature for fingerprint integrity"""
        message = f"{fingerprint.beacon_id}:{fingerprint.fingerprint_hash}"
        return hmac.new(self.hmac_key, message.encode(), hashlib.sha256).hexdigest()

    def verify_signature(self, fingerprint: BeaconFingerprint, signature: str) -> bool:
        """Verify fingerprint HMAC signature"""
        expected_sig = self.create_signature(fingerprint)
        return hmac.compare_digest(expected_sig, signature)

    def validate_component_consistency(self, components: List[FingerprintComponent]) -> bool:
        """Validate internal consistency of fingerprint components"""
        if not components:
            return False

        # At least one component of each major type
        types_present = {c.component_type for c in components}

        # Require system config
        if FingerprintType.SYSTEM_CONFIG not in types_present:
            return False

        # Verify weights sum reasonably
        total_weight = sum(c.weight for c in components)
        if total_weight <= 0 or total_weight > 100:
            return False

        return True

    def detect_tampering(self, fingerprint: BeaconFingerprint, original_hash: str) -> bool:
        """Detect if fingerprint has been tampered with"""
        fingerprint.generate_hashes()
        return fingerprint.fingerprint_hash != original_hash


class C2FingerprintRouter:
    """
    Intelligent C2 server router based on beacon fingerprints
    Routes beacons to correct servers using fingerprint matching
    """

    def __init__(self):
        self.servers: Dict[str, C2Server] = {}
        self.routing_rules: Dict[str, RoutingRule] = {}
        self.beacon_fingerprints: Dict[str, BeaconFingerprint] = {}
        self.routing_history: List[RoutingDecision] = []
        self.validator = FingerprintValidator()

        # Fingerprint cache for quick lookups
        self.fingerprint_cache: Dict[str, str] = {}  # hash -> server_id

    def register_server(
        self,
        name: str,
        address: str,
        port: int,
        protocol: str = "https",
        region: str = "",
        fallback_servers: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Register a C2 server"""
        server_id = str(uuid.uuid4())[:16]
        server = C2Server(
            server_id=server_id,
            name=name,
            address=address,
            port=port,
            protocol=protocol,
            region=region,
            fallback_servers=fallback_servers or [],
            metadata=metadata or {}
        )
        self.servers[server_id] = server
        return server_id

    def register_beacon_fingerprint(
        self,
        beacon_id: str,
        components: List[FingerprintComponent],
        target_server_id: Optional[str] = None
    ) -> BeaconFingerprint:
        """
        Register a beacon with its fingerprint

        Args:
            beacon_id: Unique beacon identifier
            components: List of fingerprint components
            target_server_id: Server this beacon should route to

        Returns:
            BeaconFingerprint object
        """
        # Validate components
        if not self.validator.validate_component_consistency(components):
            raise ValueError("Invalid fingerprint components")

        # Create fingerprint
        fingerprint = BeaconFingerprint(
            beacon_id=beacon_id,
            components=components,
            metadata={'target_server': target_server_id} if target_server_id else {}
        )

        # Generate hashes
        fingerprint.generate_hashes()

        # Store fingerprint
        self.beacon_fingerprints[beacon_id] = fingerprint
        self.fingerprint_cache[fingerprint.fingerprint_hash] = beacon_id

        # Register with target server
        if target_server_id and target_server_id in self.servers:
            self.servers[target_server_id].accepted_fingerprints.add(fingerprint.fingerprint_hash)

        return fingerprint

    def create_routing_rule(
        self,
        name: str,
        description: str,
        fingerprint_pattern: Dict,
        target_servers: List[str],
        routing_strategy: RoutingStrategy = RoutingStrategy.DIRECT,
        matching_algorithm: MatchingAlgorithm = MatchingAlgorithm.EXACT,
        match_threshold: float = 1.0,
        priority: int = 0
    ) -> str:
        """Create a fingerprint-based routing rule"""
        rule_id = str(uuid.uuid4())[:16]
        rule = RoutingRule(
            rule_id=rule_id,
            name=name,
            description=description,
            fingerprint_pattern=fingerprint_pattern,
            target_servers=target_servers,
            routing_strategy=routing_strategy,
            matching_algorithm=matching_algorithm,
            match_threshold=match_threshold,
            priority=priority
        )
        self.routing_rules[rule_id] = rule
        return rule_id

    def match_fingerprint_component(
        self,
        component: FingerprintComponent,
        pattern_value: str,
        algorithm: MatchingAlgorithm
    ) -> Tuple[bool, float]:
        """
        Match a fingerprint component against a pattern

        Returns:
            (match: bool, confidence: float)
        """
        if algorithm == MatchingAlgorithm.EXACT:
            return (component.value == pattern_value, 1.0 if component.value == pattern_value else 0.0)

        elif algorithm == MatchingAlgorithm.FUZZY:
            # Simple Levenshtein-based fuzzy matching
            match_ratio = self._fuzzy_match_ratio(component.value, pattern_value)
            tolerance = component.variance_tolerance
            return (match_ratio >= (1.0 - tolerance), match_ratio)

        elif algorithm == MatchingAlgorithm.PROBABILISTIC:
            # Probabilistic matching with confidence scoring
            confidence = self._probabilistic_match(component.value, pattern_value)
            return (confidence > 0.5, confidence)

        else:
            return (False, 0.0)

    def _fuzzy_match_ratio(self, s1: str, s2: str) -> float:
        """Calculate fuzzy match ratio (0-1)"""
        if s1 == s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        # Simple character overlap ratio
        common = len(set(s1) & set(s2))
        total = len(set(s1) | set(s2))
        return common / total if total > 0 else 0.0

    def _probabilistic_match(self, value: str, pattern: str) -> float:
        """Calculate probabilistic match score"""
        # Implement Jaccard similarity for probabilistic matching
        if value == pattern:
            return 1.0

        set1 = set(value.split('_'))
        set2 = set(pattern.split('_'))

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def match_fingerprint_to_rule(
        self,
        fingerprint: BeaconFingerprint,
        rule: RoutingRule
    ) -> Tuple[bool, float]:
        """
        Match fingerprint against a routing rule

        Returns:
            (matches: bool, overall_confidence: float)
        """
        if not rule.is_enabled:
            return (False, 0.0)

        pattern = rule.fingerprint_pattern
        if not pattern:
            return (True, 1.0)  # Empty pattern matches all

        matches = []
        weights = []

        for component in fingerprint.components:
            component_type_str = component.component_type.value

            if component_type_str in pattern:
                pattern_value = pattern[component_type_str]
                match, confidence = self.match_fingerprint_component(
                    component,
                    pattern_value,
                    rule.matching_algorithm
                )
                matches.append(match)
                weights.append(component.weight)
            else:
                # Component not in pattern - assume match with low weight
                matches.append(True)
                weights.append(0.1)

        if not matches:
            return (False, 0.0)

        # Calculate weighted confidence
        matched_weight = sum(w for m, w in zip(matches, weights) if m)
        total_weight = sum(weights)
        overall_confidence = matched_weight / total_weight if total_weight > 0 else 0.0

        # Check against threshold
        rule_matches = overall_confidence >= rule.match_threshold
        return (rule_matches, overall_confidence)

    def route_beacon(
        self,
        beacon_id: str,
        fingerprint: Optional[BeaconFingerprint] = None,
        force_server_id: Optional[str] = None
    ) -> RoutingDecision:
        """
        Route a beacon to the correct C2 server based on its fingerprint

        Args:
            beacon_id: Beacon identifier
            fingerprint: BeaconFingerprint (lookup if not provided)
            force_server_id: Force routing to specific server

        Returns:
            RoutingDecision with selected server and alternatives
        """
        # Get or lookup fingerprint
        if not fingerprint:
            if beacon_id not in self.beacon_fingerprints:
                raise ValueError(f"Beacon {beacon_id} fingerprint not found")
            fingerprint = self.beacon_fingerprints[beacon_id]

        # Verify fingerprint validity
        if not self.validator.validate_component_consistency(fingerprint.components):
            raise ValueError(f"Invalid fingerprint for beacon {beacon_id}")

        routing_path = ["route_beacon_entry"]

        # Force routing if specified
        if force_server_id:
            if force_server_id not in self.servers:
                raise ValueError(f"Server {force_server_id} not found")
            server = self.servers[force_server_id]
            routing_path.append(f"forced_to_{force_server_id}")
            return RoutingDecision(
                beacon_id=beacon_id,
                selected_server=server,
                confidence_score=1.0,
                routing_path=routing_path
            )

        # Match against routing rules (sorted by priority)
        sorted_rules = sorted(
            self.routing_rules.values(),
            key=lambda r: r.priority,
            reverse=True
        )

        best_server = None
        best_confidence = 0.0
        matching_rule_id = ""
        alternative_servers = []

        for rule in sorted_rules:
            rule_matches, confidence = self.match_fingerprint_to_rule(fingerprint, rule)

            if rule_matches and confidence > best_confidence:
                routing_path.append(f"matched_rule_{rule.rule_id}")
                best_confidence = confidence
                matching_rule_id = rule.rule_id

                # Select server based on routing strategy
                selected_server_id = self._select_server_by_strategy(
                    rule.target_servers,
                    rule.routing_strategy,
                    beacon_id
                )

                if selected_server_id in self.servers:
                    best_server = self.servers[selected_server_id]
                    alternative_servers = [
                        self.servers[sid]
                        for sid in rule.target_servers
                        if sid != selected_server_id and sid in self.servers
                    ]

        # Fallback to default routing if no rule matched
        if not best_server:
            routing_path.append("no_rule_match_fallback")
            best_server = self._get_default_server(beacon_id)
            if not best_server:
                raise RuntimeError("No available C2 servers")

        # Register beacon with server
        best_server.active_beacons.add(beacon_id)

        decision = RoutingDecision(
            beacon_id=beacon_id,
            selected_server=best_server,
            confidence_score=best_confidence,
            matching_rule_id=matching_rule_id,
            alternative_servers=alternative_servers,
            routing_path=routing_path
        )

        self.routing_history.append(decision)
        return decision

    def _select_server_by_strategy(
        self,
        server_ids: List[str],
        strategy: RoutingStrategy,
        beacon_id: str
    ) -> str:
        """Select specific server from list based on routing strategy"""
        if not server_ids:
            return ""

        if strategy == RoutingStrategy.DIRECT:
            return server_ids[0]

        elif strategy == RoutingStrategy.ROUND_ROBIN:
            # Simple round-robin based on beacon ID hash
            idx = int(hashlib.md5(beacon_id.encode()).hexdigest(), 16) % len(server_ids)
            return server_ids[idx]

        elif strategy == RoutingStrategy.LOAD_BALANCED:
            # Select server with lowest capacity
            available = [sid for sid in server_ids if sid in self.servers]
            if not available:
                return server_ids[0]
            return min(available, key=lambda sid: self.servers[sid].capacity_percent)

        elif strategy == RoutingStrategy.LATENCY_OPTIMIZED:
            # Select server with lowest latency
            available = [sid for sid in server_ids if sid in self.servers]
            if not available:
                return server_ids[0]
            return min(available, key=lambda sid: self.servers[sid].latency_ms)

        elif strategy == RoutingStrategy.GEOLOCATION:
            # Return first available (would need beacon location data)
            return server_ids[0]

        elif strategy == RoutingStrategy.RANDOMIZED:
            import random
            return random.choice(server_ids)

        else:
            return server_ids[0]

    def _get_default_server(self, beacon_id: str) -> Optional[C2Server]:
        """Get default C2 server with capacity"""
        active_servers = [
            s for s in self.servers.values()
            if s.is_active and len(s.active_beacons) < s.beacon_limit
        ]

        if not active_servers:
            return None

        # Return server with lowest current load
        return min(active_servers, key=lambda s: len(s.active_beacons))

    def update_fingerprint(
        self,
        beacon_id: str,
        new_components: List[FingerprintComponent]
    ) -> BeaconFingerprint:
        """Update beacon fingerprint"""
        if beacon_id not in self.beacon_fingerprints:
            raise ValueError(f"Beacon {beacon_id} not found")

        old_fingerprint = self.beacon_fingerprints[beacon_id]

        # Create updated fingerprint
        updated_fp = BeaconFingerprint(
            beacon_id=beacon_id,
            components=new_components,
            metadata=old_fingerprint.metadata
        )
        updated_fp.generate_hashes()

        self.beacon_fingerprints[beacon_id] = updated_fp
        return updated_fp

    def get_routing_stats(self) -> Dict:
        """Get routing statistics"""
        return {
            'total_beacons': len(self.beacon_fingerprints),
            'total_servers': len(self.servers),
            'total_routing_rules': len(self.routing_rules),
            'routing_decisions': len(self.routing_history),
            'beacons_per_server': {
                server_id: len(server.active_beacons)
                for server_id, server in self.servers.items()
            },
            'average_confidence': (
                sum(d.confidence_score for d in self.routing_history) / len(self.routing_history)
                if self.routing_history else 0.0
            )
        }

    def export_routing_config(self, include_secrets: bool = False) -> Dict:
        """Export complete routing configuration"""
        config = {
            'servers': {
                sid: {
                    'name': s.name,
                    'address': s.address,
                    'port': s.port,
                    'protocol': s.protocol,
                    'region': s.region,
                    'active_beacons': len(s.active_beacons),
                    'accepted_fingerprints': len(s.accepted_fingerprints) if include_secrets else 0
                }
                for sid, s in self.servers.items()
            },
            'routing_rules': {
                rid: {
                    'name': r.name,
                    'description': r.description,
                    'strategy': r.routing_strategy.value,
                    'algorithm': r.matching_algorithm.value,
                    'enabled': r.is_enabled
                }
                for rid, r in self.routing_rules.items()
            },
            'fingerprints': len(self.beacon_fingerprints),
            'routing_decisions': len(self.routing_history)
        }
        return config

    def clear_beacon(self, beacon_id: str) -> bool:
        """Remove beacon from active tracking"""
        if beacon_id not in self.beacon_fingerprints:
            return False

        fingerprint = self.beacon_fingerprints[beacon_id]

        # Remove from all servers
        for server in self.servers.values():
            server.active_beacons.discard(beacon_id)
            server.accepted_fingerprints.discard(fingerprint.fingerprint_hash)

        # Remove fingerprint
        del self.beacon_fingerprints[beacon_id]
        if fingerprint.fingerprint_hash in self.fingerprint_cache:
            del self.fingerprint_cache[fingerprint.fingerprint_hash]

        return True


def demonstrate_routing():
    """Demonstrate C2 fingerprint-based routing"""
    print("=" * 80)
    print("C2 FINGERPRINT-BASED ROUTING DEMONSTRATION")
    print("=" * 80 + "\n")

    # Initialize router
    router = C2FingerprintRouter()

    # Register C2 servers
    print("REGISTERING C2 SERVERS:")
    print("-" * 80)

    server_ids = []
    servers_config = [
        ("Primary Handler", "c2-primary.example.com", 443, "https", "US-EAST"),
        ("Secondary Handler", "c2-secondary.example.com", 443, "https", "US-WEST"),
        ("Backup Handler", "c2-backup.example.com", 8443, "https", "EU-WEST"),
    ]

    for name, address, port, protocol, region in servers_config:
        sid = router.register_server(
            name=name,
            address=address,
            port=port,
            protocol=protocol,
            region=region
        )
        server_ids.append(sid)
        print(f"  Registered: {name} -> {sid}")

    print()

    # Create routing rules
    print("CREATING ROUTING RULES:")
    print("-" * 80)

    # Rule 1: Windows systems to primary
    rule1_id = router.create_routing_rule(
        name="Windows Systems",
        description="Route Windows systems to primary handler",
        fingerprint_pattern={
            'system_config': 'Windows.*'
        },
        target_servers=[server_ids[0]],
        routing_strategy=RoutingStrategy.DIRECT,
        matching_algorithm=MatchingAlgorithm.FUZZY,
        match_threshold=0.8,
        priority=10
    )
    print(f"  Rule 1 (Windows): {rule1_id}")

    # Rule 2: Linux systems to secondary
    rule2_id = router.create_routing_rule(
        name="Linux Systems",
        description="Route Linux systems to secondary handler",
        fingerprint_pattern={
            'system_config': 'Linux.*'
        },
        target_servers=[server_ids[1]],
        routing_strategy=RoutingStrategy.DIRECT,
        matching_algorithm=MatchingAlgorithm.FUZZY,
        match_threshold=0.8,
        priority=10
    )
    print(f"  Rule 2 (Linux): {rule2_id}")

    # Rule 3: High-memory systems with load balancing
    rule3_id = router.create_routing_rule(
        name="High-Memory Systems",
        description="Route systems with 8GB+ RAM with load balancing",
        fingerprint_pattern={
            'system_config': '.*RAM.*8GB.*'
        },
        target_servers=server_ids,
        routing_strategy=RoutingStrategy.LOAD_BALANCED,
        matching_algorithm=MatchingAlgorithm.FUZZY,
        match_threshold=0.7,
        priority=5
    )
    print(f"  Rule 3 (High-Memory): {rule3_id}\n")

    # Register beacon fingerprints
    print("REGISTERING BEACON FINGERPRINTS:")
    print("-" * 80)

    beacon_fps = []

    # Beacon 1: Windows system
    beacon1_components = [
        FingerprintComponent(
            component_type=FingerprintType.SYSTEM_CONFIG,
            value="Windows-10-x64",
            weight=2.0
        ),
        FingerprintComponent(
            component_type=FingerprintType.PROCESS_INFO,
            value="explorer.exe",
            weight=1.5
        ),
        FingerprintComponent(
            component_type=FingerprintType.NETWORK_CONFIG,
            value="192.168.1.100",
            weight=1.0
        ),
    ]
    fp1 = router.register_beacon_fingerprint(
        beacon_id="beacon_001",
        components=beacon1_components,
        target_server_id=server_ids[0]
    )
    beacon_fps.append(("beacon_001", fp1))
    print(f"  Beacon 001 (Windows): {fp1.beacon_id} -> Hash: {fp1.fingerprint_hash[:16]}...")

    # Beacon 2: Linux system
    beacon2_components = [
        FingerprintComponent(
            component_type=FingerprintType.SYSTEM_CONFIG,
            value="Linux-5.10-x64",
            weight=2.0
        ),
        FingerprintComponent(
            component_type=FingerprintType.PROCESS_INFO,
            value="systemd",
            weight=1.5
        ),
        FingerprintComponent(
            component_type=FingerprintType.NETWORK_CONFIG,
            value="10.0.0.50",
            weight=1.0
        ),
    ]
    fp2 = router.register_beacon_fingerprint(
        beacon_id="beacon_002",
        components=beacon2_components,
        target_server_id=server_ids[1]
    )
    beacon_fps.append(("beacon_002", fp2))
    print(f"  Beacon 002 (Linux): {fp2.beacon_id} -> Hash: {fp2.fingerprint_hash[:16]}...\n")

    # Perform routing decisions
    print("ROUTING DECISIONS:")
    print("-" * 80)

    for beacon_id, fingerprint in beacon_fps:
        try:
            decision = router.route_beacon(beacon_id, fingerprint)
            print(f"\nBeacon: {beacon_id}")
            print(f"  Selected Server: {decision.selected_server.name} ({decision.selected_server.server_id})")
            print(f"  Address: {decision.selected_server.address}:{decision.selected_server.port}")
            print(f"  Confidence: {decision.confidence_score:.2%}")
            print(f"  Matching Rule: {decision.matching_rule_id}")
            print(f"  Routing Path: {' -> '.join(decision.routing_path)}")

            if decision.alternative_servers:
                print(f"  Fallback Servers:")
                for alt_server in decision.alternative_servers:
                    print(f"    - {alt_server.name} ({alt_server.address}:{alt_server.port})")
        except Exception as e:
            print(f"  Error routing {beacon_id}: {e}")

    # Display statistics
    print("\n" + "=" * 80)
    print("ROUTING STATISTICS:")
    print("-" * 80)
    stats = router.get_routing_stats()
    for key, value in stats.items():
        if key == 'beacons_per_server':
            print(f"\n{key}:")
            for sid, count in value.items():
                server_name = router.servers[sid].name if sid in router.servers else "Unknown"
                print(f"  {server_name}: {count}")
        else:
            print(f"{key}: {value}")

    # Export configuration
    print("\n" + "=" * 80)
    print("ROUTING CONFIGURATION EXPORT:")
    print("-" * 80)
    config = router.export_routing_config()
    print(json.dumps(config, indent=2))


if __name__ == "__main__":
    demonstrate_routing()
