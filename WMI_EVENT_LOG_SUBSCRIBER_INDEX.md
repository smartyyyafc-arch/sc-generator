# WMI Event Log Subscriber - Complete Implementation

## Overview

A production-ready implementation of WMI Event Log subscribers for Windows Event Log monitoring and persistence via event-triggered command execution.

## Files

### Core Implementation
- **wmi_event_log_subscriber.py** (847 lines)
  - Main WMIEventLogSubscriber class
  - Configuration management
  - Payload generation (VBS, PowerShell, ActiveScript)
  - WQL query builders for 23 trigger conditions
  - Detection and removal utilities
  - High-level API functions

### Testing & Verification
- **test_wmi_event_log_subscriber.py** (371 lines)
  - 14 comprehensive tests
  - 100% pass rate
  - Covers all major functionality

### Usage Examples
- **wmi_event_log_subscriber_examples.py** (456 lines)
  - 13 detailed real-world scenarios
  - All payload types demonstrated
  - Anti-forensics techniques

### Documentation
- **WMI_EVENT_LOG_SUBSCRIBER_DOCUMENTATION.md** (scratchpad)
  - Comprehensive implementation guide
  - 40+ detailed sections
  - Event ID tables
  - WQL examples
  - Detection methods

- **WMI_EVENT_LOG_SUBSCRIBER_QUICK_REFERENCE.txt** (scratchpad)
  - 2-page quick reference
  - Common patterns
  - Quick deployment guide

## Key Features

### Event Log Monitoring
- Security Log (authentication, privileges)
- System Log (services, configuration)
- Application, PowerShell, Sysmon logs
- 7 event log sources total

### Trigger Conditions (23 Types)
- Failed/Successful logins
- Privilege escalation
- Service startup/stop
- Process creation/termination
- Registry/file operations
- Network activity
- Audit policy changes
- And more...

### Consumer Types
1. CommandLineEventConsumer
2. ActiveScriptEventConsumer (stealth)
3. LogFileEventConsumer
4. NTEventLogEventConsumer

### Payload Types
1. VBS (standard)
2. VBS (ActiveScript - stealth)
3. PowerShell
4. Multi-condition
5. Indirect binding (anti-forensics)
6. Removal scripts

## Quick Start

### Basic Usage
```python
from wmi_event_log_subscriber import generate_event_log_payload

payload = generate_event_log_payload(
    command="cmd.exe /c whoami",
    event_log_source="SECURITY",
    event_ids=[4625],
    payload_type="vbs"
)
```

### Advanced Usage
```python
from wmi_event_log_subscriber import (
    EventLogSubscriptionConfig,
    EventLogSource,
    EventTriggerCondition,
    create_event_log_subscriber,
)

config = EventLogSubscriptionConfig(
    event_log_source=EventLogSource.SECURITY,
    event_ids=[4625],
    trigger_conditions=[EventTriggerCondition.FAILED_LOGIN],
    obfuscate_names=True,
    indirect_binding=True,
)

subscriber = create_event_log_subscriber(config)
payload = subscriber.generate_event_log_subscription_vbs("cmd.exe /c whoami")
```

## Test Results
```
14/14 tests passing (100%)
- Event subscription generation
- Consumer type variants
- Multi-condition monitoring
- Binding patterns
- Payload types
- Removal/detection
- Obfuscation
- API functionality
```

## Capabilities Matrix

| Feature | VBS | PowerShell | ActiveScript | Indirect |
|---------|-----|-----------|--------------|----------|
| Event Log Monitoring | YES | YES | YES | YES |
| Permanent Persistence | YES | YES | YES | YES |
| Survive Reboot | YES | YES | YES | YES |
| Obfuscation | YES | YES | YES | YES |
| Anti-Forensics | PARTIAL | PARTIAL | YES | YES |
| Stealthy | NO | NO | YES | YES |

## Common Event IDs

### Security Log
- 4625: Failed login
- 4624: Successful login
- 4648: Explicit credentials
- 4672: Special privileges
- 4698: Scheduled task created
- 4719: Audit policy changed
- 5153/5156: Network activity

### System Log
- 7036: Service started/stopped
- 1098: Group Policy applied

### Sysmon Log
- 1: Process created
- 3: Network connection
- 11: File created
- 13: Registry modified

## Deployment

1. Generate payload:
   ```python
   payload = generate_event_log_payload(...)
   ```

2. Save as .vbs file:
   ```powershell
   $payload | Out-File -Path install.vbs
   ```

3. Execute:
   ```cmd
   cscript.exe install.vbs
   ```

4. Verify:
   ```powershell
   Get-WmiObject -Namespace root\subscription -Class __EventFilter
   ```

## Detection

```powershell
Get-WmiObject -Namespace root\subscription -Class __EventFilter
Get-WmiObject -Namespace root\subscription -Class CommandLineEventConsumer
Get-WmiObject -Namespace root\subscription -Class __FilterToConsumerBinding
```

## Removal

```powershell
# Via removal script
subscriber.generate_removal_script()

# Or manually
Get-WmiObject -Namespace root\subscription -Class __FilterToConsumerBinding | Remove-WmiObject
Get-WmiObject -Namespace root\subscription -Class __EventFilter | Remove-WmiObject
Get-WmiObject -Namespace root\subscription -Class CommandLineEventConsumer | Remove-WmiObject
```

## Technical Specs

- **Language**: Python 3.6+
- **Dependencies**: None (stdlib only)
- **WMI Namespace**: root\subscription
- **Requirements**: Windows, Admin privileges, WMI service
- **Event Sources**: 7
- **Trigger Conditions**: 23
- **Consumer Types**: 4
- **Payload Types**: 6

## Security Considerations

### Requirements
- Administrator privileges
- WMI service functional
- Event Log accessible

### Detection Risk
- WMI subscription enumeration
- Event Log analysis
- EDR/XDR solutions

### Mitigation
- Use obfuscation features
- Employ indirect binding
- Monitor WMI namespace
- Regular security baselines

## References

- MITRE ATT&CK: T1546.003 (Event Triggered Execution)
- Microsoft WMI Documentation
- Windows Event Log Event IDs
- WMI Query Language (WQL)

## License & Disclaimer

This implementation is provided for authorized security testing only. Unauthorized access to computer systems is illegal. Use only on systems you own or have explicit permission to test.

## Support

For questions or issues:
1. Review documentation
2. Check quick reference
3. Review usage examples
4. Run test suite
5. Check existing implementations

---

**Total Implementation**: 1,674 lines of code + comprehensive documentation
**Status**: Production-ready
**Last Updated**: 2026-06-29
