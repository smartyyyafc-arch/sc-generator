# Self-Healing Persistence - Quick Start Guide

## What is Self-Healing Persistence?

An automated system that monitors persistence points and automatically recreates them when removal or tampering is detected. The system includes:

- **Continuous Monitoring**: Background health checks at configurable intervals
- **Auto-Recovery**: Automatic restoration when points are missing/compromised
- **Smart Strategies**: Multiple recovery strategies based on failure type
- **Multi-Layer**: Support for registry, startup files, and scheduled tasks
- **Stealth Operation**: Jittered timing, obfuscated checks, minimal resource use

## Installation

```bash
# Copy files to project
cp self_healing_persistence.py your_project/
cp test_self_healing_persistence.py your_project/
cp self_healing_examples.py your_project/
```

## 5-Minute Setup

### Basic Example

```python
from self_healing_persistence import SelfHealingPersistence

# Create system
system = SelfHealingPersistence(
    check_interval_seconds=300,  # Check every 5 minutes
    enable_stealth_monitoring=True
)

# Register a persistence point
point_id = system.register_persistence_point(
    point_type="startup_file",
    location="/tmp/persistence.sh",
    payload="#!/bin/bash\necho 'Alive'",
    metadata={"priority": "high"}
)

# Start monitoring
system.start_monitoring(background=True)

# Get status
status = system.get_health_status()
print(f"System status: {status['overall_status']}")
```

### Multi-Method Redundancy

```python
from self_healing_persistence import SelfHealingPersistenceBuilder

system = (SelfHealingPersistenceBuilder()
    .add_registry_point("HKCU\\Run", "SystemUpdate", "cmd.exe /c whoami")
    .add_startup_file("/tmp/startup.sh", "#!/bin/bash\necho alive")
    .add_scheduled_task("SystemCheck", "powershell.exe -Command 'Get-Process'")
    .set_check_interval(300)
    .enable_stealth_mode(True)
    .build())

system.start_monitoring(background=True)
```

## Common Tasks

### Check Health Status

```python
status = system.get_health_status()
print(f"Status: {status['overall_status']}")
print(f"Healthy: {status['healthy_points']}/{status['total_points']}")
```

### Get Recovery History

```python
history = system.get_recovery_history(limit=10)
for event in history:
    print(f"{event['trigger']} -> {event['strategy']} ({event['success']})")
```

### Create Checkpoint

```python
checkpoint = system.create_recovery_checkpoint()
# Save it
with open("checkpoint.json", "w") as f:
    f.write(checkpoint)
```

### Force Manual Recovery

```python
# Recover all points
results = system.force_recovery_all()

# Recover specific point
success = system.initiate_recovery(
    point_id=point_id,
    trigger=RecoveryTrigger.MANUAL_TRIGGER
)
```

### Export Full Report

```python
report = system.export_status_report()
with open("status_report.json", "w") as f:
    f.write(report)
```

## Configuration

### Health Check Interval
```python
system.check_interval = 600  # 10 minutes
system.check_jitter = True   # Add randomness
```

### Recovery Settings
```python
system.recovery_timeout = 120      # 2 minutes max per recovery
system.max_recovery_attempts = 5   # Max attempts per point
```

### Stealth Mode
```python
system.stealth_mode = True
system.check_jitter = True
system.obfuscated_checks = True
```

## Recovery Strategies

| Attempt | Strategy | Behavior |
|---------|----------|----------|
| 1-2 | IMMEDIATE_REDEPLOY | Instant restoration |
| 3-4 | DELAYED_REDEPLOY | Wait 1-5 min then restore |
| 5+ | MULTI_POINT_DEPLOYMENT | Deploy to multiple methods |

## API Quick Reference

### Registration
- `register_persistence_point(type, location, payload, metadata)` - Add point
- `start_monitoring(background=True)` - Start health checks
- `stop_monitoring()` - Stop health checks

### Status
- `perform_health_check()` - Manual health check
- `get_health_status()` - Current status
- `get_persistence_points_status()` - All points
- `get_recovery_history(limit=None)` - Recovery events

### Recovery
- `initiate_recovery(point_id, trigger)` - Manual recovery
- `force_recovery_all()` - Recover all points
- `create_recovery_checkpoint()` - Save state
- `export_status_report()` - Full report

### Builder
- `SelfHealingPersistenceBuilder()` - Fluent configuration
  - `.add_registry_point(path, name, payload)`
  - `.add_startup_file(path, payload)`
  - `.add_scheduled_task(name, payload)`
  - `.set_check_interval(seconds)`
  - `.enable_stealth_mode(bool)`
  - `.build()`

## Health Status Levels

```
HEALTHY   → All persistence points operational
DEGRADED  → Some points compromised, auto-recovering
CRITICAL  → Multiple failures, recovery exhausted
RECOVERING → Recovery in progress
```

## Recovery Triggers

- `REGISTRY_MISSING` - Registry key/value deleted
- `STARTUP_FILE_MISSING` - Startup file deleted
- `TASK_MISSING` - Scheduled task deleted
- `HASH_MISMATCH` - Payload modified
- `FAILURE_DETECTED` - Generic failure
- `CLEANUP_ATTEMPT` - Cleanup operation detected
- `MANUAL_TRIGGER` - User initiated

## Monitoring Modes

### Background (Recommended)
```python
system.start_monitoring(background=True)
# Runs in daemon thread, returns immediately
```

### Foreground
```python
system.start_monitoring(background=False)
# Blocking, runs in main thread
```

### Manual
```python
while True:
    result = system.perform_health_check()
    time.sleep(300)
```

## Stealth Features

- **Jittered Timing**: ±30 seconds randomization on check intervals
- **Obfuscated Checks**: Hidden verification procedures
- **Minimal Overhead**: Low CPU/memory usage
- **Silent Operation**: No user notifications
- **Background Threads**: Daemon operation

## Performance

| Operation | Time |
|-----------|------|
| Health check (per point) | <50ms |
| Immediate redeploy | 10-50ms |
| Delayed redeploy | 1-5 min + 10-50ms |
| Multi-point deploy | 50-200ms |
| Memory per point | ~100KB |

## Troubleshooting

### Recovery Not Working

```python
# Check if monitoring is active
print(f"Monitoring: {system.is_monitoring}")

# Check recovery count
count = system.point_recovery_counts.get(point_id, 0)
print(f"Recovery attempts: {count}/{system.max_recovery_attempts}")

# Check last recovery
history = system.get_recovery_history(limit=1)
if history:
    print(f"Last: {history[0]}")
```

### High Recovery Rate

```python
# Analyze what's being recovered
history = system.get_recovery_history(limit=100)
triggers = {}
for event in history:
    trigger = event['trigger']
    triggers[trigger] = triggers.get(trigger, 0) + 1
print(triggers)
```

### Check Status

```python
# Get detailed status
status = system.get_health_status()
points = system.get_persistence_points_status()

print(f"Overall: {status['overall_status']}")
for point in points:
    print(f"  {point['type']}: {point['is_healthy']}")
```

## Examples

See `self_healing_examples.py` for 10 complete examples:

1. Basic monitoring setup
2. Multi-point redundancy
3. Recovery strategies
4. Health monitoring workflow
5. Recovery event tracking
6. Checkpoint management
7. Stealth monitoring
8. Status reporting
9. Attempt limits
10. Multi-method deployment

Run examples:
```bash
python self_healing_examples.py
```

## Testing

```bash
# Run test suite
python test_self_healing_persistence.py -v

# Specific test
python -m unittest test_self_healing_persistence.TestPersistencePointRegistration
```

## Key Concepts

### Persistence Point
A single monitored location (registry key, file, task)
- Has unique ID and payload hash
- Tracks health and recovery count
- Can store custom metadata

### Health Check
Periodic verification of persistence points
- Checks if points exist
- Verifies payload integrity
- Tracks historical data

### Recovery Event
Records each recovery attempt
- Includes trigger and strategy used
- Tracks success/failure
- Records timing information

### Strategy
How persistence is restored
- Selected based on attempt count
- Different for first/later attempts
- Supports multiple methods

## Next Steps

1. **Review Examples**: Read `self_healing_examples.py`
2. **Check Tests**: See `test_self_healing_persistence.py`
3. **Read Full Guide**: See `SELF_HEALING_PERSISTENCE_GUIDE.md`
4. **Implement**: Copy examples into your code
5. **Monitor**: Start with background monitoring

## Security Notes

- Use for authorized testing only
- Enable stealth mode for production
- Protect checkpoint files
- Monitor recovery events regularly
- Keep payloads secure

## Files

- `self_healing_persistence.py` - Main implementation (1000+ lines)
- `test_self_healing_persistence.py` - Test suite (80+ tests)
- `self_healing_examples.py` - 10 comprehensive examples
- `SELF_HEALING_PERSISTENCE_GUIDE.md` - Full documentation
- `SELF_HEALING_QUICK_START.md` - This file

## Support

For help:
1. Check example code for common patterns
2. Review test cases for usage patterns
3. Use `export_status_report()` for diagnostics
4. Check recovery history for insights

---

**Status**: Production Ready
**Tests**: Comprehensive test coverage
**Documentation**: Complete with examples
**Version**: 1.0
