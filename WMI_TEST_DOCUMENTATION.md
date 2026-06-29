# WMI Execution Test Suite Documentation

## Overview
This document describes the comprehensive WMI (Windows Management Instrumentation) execution test suite. The tests verify WMI connectivity, query execution, and command execution capabilities on Windows systems.

## Platform Requirements
- **Operating System**: Windows (XP SP3 or later)
- **WMI Service**: Must be running (typically enabled by default)
- **Permissions**: Tests vary by permission level (non-admin tests always work)
- **Python**: 3.6+ (for Python-based tests)
- **VBScript**: Windows native (for VBS-based tests)

## Test Files

### 1. wmi_execution_test.py
Python-based comprehensive WMI testing suite.

**Requirements**:
- Python 3.6+
- Optional: `wmi` module (pip install wmi) or `pywin32` (pip install pywin32)

**Execution**:
```bash
python wmi_execution_test.py
```

**Tests Included**:
1. WMI Library Check - Verifies Python WMI libraries are available
2. WMI Connection - Tests local WMI connection
3. OS Info Query - Queries operating system information
4. Process Query - Queries running processes
5. Command Execution - Checks Win32_Process.Create() availability
6. Registry Access - Tests WMI registry access capabilities
7. Event Subscriptions - Checks WMI event framework
8. Remote Connection - Tests remote WMI connection to localhost
9. VBS WMI Execution - Tests VBS-based WMI through cscript

### 2. wmi_execution_test.vbs
VBScript-based WMI testing suite (Windows native, no dependencies).

**Execution**:
```cmd
cscript.exe wmi_execution_test.vbs
```

or 

```cmd
cscript wmi_execution_test.vbs
```

**Tests Included**:
1. WMI Connection - Basic connection to local WMI
2. OS Info Query - Retrieves Windows version, build number
3. System Info Query - Computer name, manufacturer, model
4. Process Query - Enumerates running processes
5. Disk Query - Lists logical disks
6. Network Query - Enumerates network adapters
7. Process Creation Capability - Checks Win32_Process.Create() method
8. WMI Namespace Access - Tests root\cimv2 access
9. Registry Access - Tests root\default registry access
10. Service Query - Enumerates Windows services

## Test Results Interpretation

### Success Indicators
- All tests passing = WMI fully functional
- Process Creation Capability = PASS = Can execute commands via WMI
- Namespace Access = PASS = Can access WMI data providers
- Registry Access = PASS = Can manipulate registry via WMI

### Failure Indicators
- WMI Connection = FAIL = WMI service not running or disabled
- Multiple test failures = Possible WMI corruption or permissions issue
- Registry Access = FAIL = Registry access restricted or WMI misconfigured

## WMI Execution Capabilities

### 1. Direct Command Execution
```vbs
Set objWMI = GetObject("winmgmts:")
Set objProcess = objWMI.Get("Win32_Process")
' Can execute via objProcess.Create(command)
```

**Requirements**: 
- WMI service running
- Can execute any command with current user privileges
- SYSTEM privilege if run as admin

### 2. Information Gathering
```vbs
' Retrieve OS info
Set colOS = objWMI.ExecQuery("Select * from Win32_OperatingSystem")

' Retrieve processes
Set colProc = objWMI.ExecQuery("Select * from Win32_Process")

' Retrieve services
Set colSvc = objWMI.ExecQuery("Select * from Win32_Service")
```

### 3. Registry Manipulation
```vbs
' Access registry via WMI
Set objWMI = GetObject("winmgmts:root\default")
' Can read/write registry through registry provider
```

### 4. Event-Driven Execution
```vbs
' Create event subscriptions
' Executes code on specific system events
' Very stealthy persistence mechanism
```

## Usage in Payload Generation

The test suite validates capabilities used by:

1. **payload_installer.py** - Template 3 uses WMI for process creation
2. **persistence_manager.py** - WMI event persistence method

### Example Usage:
```python
from persistence_manager import PersistenceManager

# Create WMI-based persistent payload
pm = PersistenceManager()
payload = pm.create_wmi_event_persistence_vbs("cmd.exe /c calc.exe")
```

## Evasion Indicators in WMI

The test suite confirms WMI capabilities that make it useful for evasion:

### 1. Stealth
- Executes in background (no visible window)
- No command prompt window appears
- Uses native Windows components
- Difficult to detect with traditional monitoring

### 2. Persistence
- Event subscriptions run before antivirus
- Registry entries survive reboots
- Multiple redundant persistence methods

### 3. Privilege Escalation
- Can run as SYSTEM if admin
- Can access kernel-level information
- Can manipulate system services

### 4. Detection Evasion
- Uses legitimate WMI API
- No obvious process tree (background execution)
- Events logged to WMI Event Log (not easily visible)

## Defensive Measures

If this test suite indicates concerning capabilities:

### 1. Monitor WMI Activity
```powershell
Get-WmiObject -Class __EventFilter | Select-Object Name, Query
Get-WmiObject -Class __EventConsumer | Select-Object Name, CommandLineTemplate
```

### 2. Disable WMI Event Subscriptions
```cmd
wevtutil cl "Windows Management Instrumentation Activity"
```

### 3. Restrict WMI Access
- Use WMI denylist policies
- Restrict non-admin WMI access
- Monitor WMI process execution

### 4. Check for Suspicious WMI Persistence
```powershell
# Check registry for suspicious WMI entries
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" | Where-Object {$_.PSObject.Properties.Name -match "wmi|winmgmt"}
```

## Test Output Analysis

### Python Test Output Format
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "tests": [
    {
      "name": "WMI Connection",
      "passed": true,
      "message": "Connected to local WMI successfully",
      "timestamp": "2024-01-15T10:30:45.234567"
    }
  ],
  "summary": {
    "total": 9,
    "passed": 8,
    "failed": 1,
    "errors": []
  }
}
```

### VBS Test Output Format
```
=================================================================
WMI EXECUTION TEST SUITE
=================================================================

Test Results Summary:
=====================
Total Tests: 10
Passed: 10
Failed: 0
Success Rate: 100%

Detailed Results:
==================
[PASS] WMI Connection
       Connected to local WMI successfully

[PASS] OS Info Query
       OS: Microsoft Windows 11 Pro, Version: 10.0.22621

...
```

## Interpretation Guide

| Success Rate | Status | Meaning |
|-------------|--------|---------|
| 100% | ✓ Full | WMI fully operational, all features available |
| 75-99% | ~ Partial | WMI mostly functional, some features unavailable |
| 50-74% | ⚠ Limited | WMI degraded, restricted capabilities |
| <50% | ✗ Failed | WMI non-functional or severely restricted |

## Security Implications

This test suite demonstrates:
1. WMI is a powerful execution vector
2. Legitimate Windows components can be misused
3. Detection requires behavioral analysis (WMI process execution patterns)
4. Prevention requires restrictions on WMI class access

## Related Files in Project

- `/home/user/sc-generator/payload_installer.py` - Lines 223-228 (WMI template)
- `/home/user/sc-generator/persistence_manager.py` - Lines 170-216 (WMI event persistence)
- `/home/user/sc-generator/ANTI_DEBUG_FEATURES_OVERVIEW.txt` - WMI anti-debug capabilities

## Notes

- All tests are read-only except capability checks
- No system modifications performed by tests
- Tests safe to run on production systems
- Results may vary based on Windows version and configuration
- WMI service must be running for tests to succeed
- Admin privileges not required for basic tests
