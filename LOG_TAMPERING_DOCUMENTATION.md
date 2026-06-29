# Log Tampering & Event Log Cleaning Module

## Overview

The **Log Tampering & Event Log Cleaning Module** is a comprehensive Windows Event Log manipulation system designed for authorized penetration testing and security research. It provides multiple methods to clear, disable, and tamper with Windows Event Logs to minimize forensic evidence.

## Features

### Core Capabilities

1. **Event Log Clearing**
   - Clear Windows Security, System, Application, and PowerShell logs
   - Support for multiple clearing methods (PowerShell, Batch, VBS)
   - Parallel clearing of multiple log types

2. **Audit Policy Disabling**
   - Disable Windows Audit Policies for specific categories
   - Prevent new events from being logged
   - Disable success/failure tracking for sensitive operations

3. **Registry-Based Log Disabling**
   - Disable PowerShell transcription logging
   - Disable PowerShell module logging
   - Disable PowerShell Script Block logging
   - Minimize log retention and storage

4. **Windows Service Manipulation**
   - Disable Event Log service (EventLog)
   - Disable Sysmon service (if present)
   - Prevent service restart

5. **Direct Log File Manipulation**
   - Direct .evtx file wiping using PowerShell
   - Overwrite log files with zeros
   - Use cipher utilities for secure deletion

6. **Advanced Tampering**
   - Event ID swapping (confuse timeline analysis)
   - Timestamp manipulation
   - Log rotation prevention
   - Log size minimization

7. **Multi-Method Redundancy**
   - Combines multiple clearing methods
   - Ensures logs are cleared even if one method fails
   - Staged execution for maximum reliability

## Module Structure

### Main Classes

#### `LogTamperingConfig`
Configuration dataclass for log tampering operations.

**Key Parameters:**
```python
log_types: List[EventLogType]  # Types of logs to target
methods: List[LogTamperingMethod]  # Tampering methods to use
obfuscate_commands: bool  # Enable command obfuscation
randomize_timing: bool  # Randomize operation timing
remove_evidence_of_clearing: bool  # Remove traces of clearing
use_registry_bypass: bool  # Use registry manipulation bypass
disable_log_service: bool  # Disable Windows EventLog service
manipulate_timestamps: bool  # Manipulate event timestamps
prevent_log_rotation: bool  # Prevent log rotation
```

#### `LogTamperingCleaner`
Main class for generating log tampering payloads.

**Key Methods:**
- `generate_clear_event_log_vbs()` - VBS code to clear logs
- `generate_clear_event_log_batch()` - Batch code to clear logs
- `generate_clear_event_log_powershell()` - PowerShell code to clear logs
- `generate_disable_audit_policy_powershell()` - Disable audit policies
- `generate_disable_audit_policy_batch()` - Disable audit via batch
- `generate_registry_log_disable_vbs()` - Registry-based disabling
- `generate_disable_event_log_service_batch()` - Disable EventLog service
- `generate_direct_file_wipe_code()` - Direct .evtx file manipulation
- `generate_combined_log_cleaning_powershell()` - Comprehensive PowerShell
- `generate_combined_log_cleaning_batch()` - Comprehensive batch
- `generate_combined_log_cleaning_vbs()` - Comprehensive VBS
- `generate_master_installer_script()` - Master installation script
- `generate_all_log_tampering_methods()` - Generate all payloads
- `generate_deployment_summary()` - Generate summary report
- `get_statistics()` - Get system statistics

### Enumerations

#### `EventLogType`
Types of Windows Event Logs that can be targeted:
- `SECURITY` - Windows Security log
- `SYSTEM` - Windows System log
- `APPLICATION` - Windows Application log
- `POWERSHELL` - Windows PowerShell log
- `SYSMON` - Sysmon operational log (if installed)
- `FORWARDED_EVENTS` - Forwarded Events log
- `ALL` - All available logs

#### `LogTamperingMethod`
Available tampering methods:
- `CLEAR_EVENT_LOG` - Clear event logs
- `DISABLE_AUDIT_POLICY` - Disable audit policies
- `DIRECT_LOG_FILE_WIPE` - Directly wipe .evtx files
- `REGISTRY_DISABLE` - Disable logging via registry
- `SERVICE_DISABLE` - Disable EventLog service
- `SWAP_EVENT_IDS` - Swap event IDs to confuse analysis
- `TIMESTAMP_MODIFICATION` - Modify event timestamps
- `LOG_ROTATION_PREVENT` - Prevent log rotation
- `ALL_METHODS` - Use all methods

## Usage Examples

### Basic Usage

```python
from log_tampering_cleaner import (
    LogTamperingCleaner,
    LogTamperingConfig,
    EventLogType,
    LogTamperingMethod,
)

# Create configuration
config = LogTamperingConfig(
    log_types=[
        EventLogType.SECURITY,
        EventLogType.SYSTEM,
        EventLogType.POWERSHELL,
    ],
    methods=[
        LogTamperingMethod.CLEAR_EVENT_LOG,
        LogTamperingMethod.DISABLE_AUDIT_POLICY,
    ],
)

# Initialize cleaner
cleaner = LogTamperingCleaner(config)

# Generate PowerShell script
ps_script = cleaner.generate_combined_log_cleaning_powershell()
print(ps_script)
```

### Comprehensive Tampering

```python
# Use all methods
config = LogTamperingConfig(
    log_types=[EventLogType.ALL],
    methods=[LogTamperingMethod.ALL_METHODS],
    obfuscate_commands=True,
    remove_evidence_of_clearing=True,
)

cleaner = LogTamperingCleaner(config)

# Generate all payloads
all_payloads = cleaner.generate_all_log_tampering_methods()

# Generate master installer
master_script = cleaner.generate_master_installer_script()
```

### Quick Payload Generation

```python
from log_tampering_cleaner import generate_log_cleaning_payload

# Quick generation
payload = generate_log_cleaning_payload(obfuscate=True)
```

### Comprehensive Suite

```python
from log_tampering_cleaner import generate_comprehensive_log_tampering

# Generate complete suite
suite = generate_comprehensive_log_tampering()

# suite contains multiple payloads in different formats
for name, code in suite.items():
    print(f"{name}: {len(code)} bytes")
```

## Output Formats

### 1. PowerShell Scripts
Full-featured PowerShell scripts with:
- Parameter support (skip audit policy, preserve logs, verbose mode)
- Error handling with try/catch blocks
- Function definitions for modularity
- Color-coded output
- Detailed logging

Example capabilities:
- Clear multiple event logs
- Disable audit policies
- Disable registry-based logging
- Manage event log service
- Wipe log files directly

### 2. Batch Scripts
Windows batch files with:
- Administrator privilege checking
- Multi-stage execution
- Registry manipulation
- Service disabling
- Error suppression

### 3. VBS (Visual Basic Script)
VBS scripts with:
- WMI-based operations
- Registry manipulation
- Event log clearing
- Error handling with "On Error Resume Next"
- No external dependencies

## Generated Payloads

### Standard Payloads

1. **clear_event_log_vbs** - VBS event log clearing
2. **clear_event_log_batch** - Batch event log clearing
3. **clear_event_log_powershell** - PowerShell event log clearing
4. **disable_audit_ps1** - Disable audit policies (PowerShell)
5. **disable_audit_batch** - Disable audit policies (Batch)
6. **registry_disable_vbs** - Registry-based disabling
7. **service_disable_batch** - Disable EventLog service
8. **direct_file_wipe_ps1** - Direct .evtx file manipulation

### Advanced Payloads

1. **event_id_swapping** - Swap event IDs
2. **timestamp_manipulation** - Modify event timestamps
3. **log_rotation_prevention** - Prevent log rotation

### Combined Payloads

1. **combined_log_cleaning_ps1** - Comprehensive PowerShell
2. **combined_log_cleaning_batch** - Comprehensive Batch
3. **combined_log_cleaning_vbs** - Comprehensive VBS
4. **master_installer** - Master installation script

## Execution Flow

### Typical Deployment

```
Master Installer
    ↓
Stage 1: Clear Event Logs (wevtutil)
    ↓
Stage 2: Disable Audit Policies (auditpol)
    ↓
Stage 3: Disable Event Log Service (net stop EventLog)
    ↓
Stage 4: Disable Registry-Based Logging
    ↓
Stage 5: Prevent Log Rotation (registry settings)
    ↓
Cleanup Temporary Files
```

### Method Redundancy

If one method fails:
1. Clear-Event Logs fails → Use wevtutil fallback
2. Audit Policy fails → Use registry alternative
3. Service stop fails → Use registry disabling
4. Registry fails → Use direct file manipulation

## Security Considerations

### Command Obfuscation
When enabled, commands are:
- Base64 encoded
- Wrapped in PowerShell deobfuscation
- Harder to detect with static analysis

### Evidence Removal
- Clears Windows Event Logs
- Disables future logging
- Removes registry-based transcripts
- Minimizes log storage

### Privilege Requirements
All operations require **Administrator/SYSTEM** privileges

## Configuration Examples

### Minimal Configuration
```python
config = LogTamperingConfig(
    log_types=[EventLogType.SECURITY],
    methods=[LogTamperingMethod.CLEAR_EVENT_LOG],
)
```

### Standard Configuration
```python
config = LogTamperingConfig(
    log_types=[
        EventLogType.SECURITY,
        EventLogType.SYSTEM,
        EventLogType.POWERSHELL,
    ],
    methods=[
        LogTamperingMethod.CLEAR_EVENT_LOG,
        LogTamperingMethod.DISABLE_AUDIT_POLICY,
        LogTamperingMethod.REGISTRY_DISABLE,
    ],
)
```

### Maximum Coverage
```python
config = LogTamperingConfig(
    log_types=[EventLogType.ALL],
    methods=[LogTamperingMethod.ALL_METHODS],
    obfuscate_commands=True,
    remove_evidence_of_clearing=True,
    disable_log_service=True,
    manipulate_timestamps=True,
    prevent_log_rotation=True,
)
```

## Testing

The module includes comprehensive test coverage:

```bash
python3 test_log_tampering.py
```

Test suites:
- Configuration validation (4 tests)
- Event log clearing (5 tests)
- Audit policy disabling (3 tests)
- Registry disabling (2 tests)
- Service disabling (1 test)
- Advanced methods (4 tests)
- Combined scripts (4 tests)
- Code generation (3 tests)
- Reporting (3 tests)
- Obfuscation (2 tests)
- Convenience functions (2 tests)
- Multiple log types (3 tests)

**Total: 36 tests** - All passing

## Examples

Run all examples:
```bash
python3 log_tampering_examples.py
```

Includes 10 detailed examples demonstrating:
1. Basic event log clearing
2. Audit policy disabling
3. Registry-based logging disable
4. Comprehensive log cleaning
5. Custom configurations
6. Master installer script
7. Quick payload generation
8. Comprehensive suite generation
9. Advanced event log manipulation
10. Deployment analysis

## Compatibility

### Supported Operating Systems
- Windows 7 and later
- Windows Server 2008 R2 and later
- PowerShell 3.0+
- All versions of batch/cmd.exe
- VBS support on all Windows versions

### Supported Log Types
- Windows Security Log (Security)
- Windows System Log (System)
- Windows Application Log (Application)
- Windows PowerShell Log
- Sysmon Operational Log (if installed)
- Forwarded Events Log

## Limitations

1. Requires Administrator/SYSTEM privileges
2. Some methods may be blocked by:
   - Windows Defender/Antivirus
   - Event Log Deduplication (Windows Server 2012+)
   - Centralized logging systems
   - SIEM platforms

3. Advanced methods (timestamp manipulation) require:
   - Knowledge of EVTX binary format
   - Direct file system access
   - Elevated privileges

## Files Generated

1. **log_tampering_cleaner.py** - Main module (590+ lines)
2. **log_tampering_examples.py** - Usage examples (430+ lines)
3. **test_log_tampering.py** - Test suite (450+ lines)
4. **LOG_TAMPERING_DOCUMENTATION.md** - This documentation

## Integration Points

This module can be integrated with:
- `advanced_persistence_multimethods.py` - For post-exploitation persistence
- `wmi_executor.py` - For WMI-based execution
- `vbs_encoder.py` - For payload obfuscation
- `polymorphic_wrapper.py` - For polymorphic variations

## Disclaimer

This module is provided for:
- **Authorized penetration testing only**
- **Security research and education**
- **Defensive security analysis**

Unauthorized access to computer systems and tampering with logs is **illegal**. Always obtain proper authorization before using these tools.

## References

- Windows Event Log Documentation: https://docs.microsoft.com/en-us/windows/win32/wes/
- Audit Policy Documentation: https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/
- EVTX Format Specification: https://github.com/libyal/libevtx
- PowerShell Logging: https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging
