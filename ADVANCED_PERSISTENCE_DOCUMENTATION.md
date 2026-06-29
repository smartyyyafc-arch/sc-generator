# Advanced Multi-Method Persistence System

## Overview

The Advanced Multi-Method Persistence System provides a comprehensive, redundant approach to system persistence by combining three primary methods:

1. **Registry Persistence** - Multiple hives and registry paths
2. **Startup Folder Persistence** - Multiple file formats and locations
3. **Scheduled Task Persistence** - Multiple triggers and execution methods
4. **Fallback Chain** - Automatic recovery and re-deployment

This system is designed for authorized security testing and penetration testing scenarios.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         ADVANCED PERSISTENCE ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PRIMARY: Registry Persistence (HKCU + HKLM)                │
│ - Multiple registry paths (Run, RunOnce, Explorer, IE)     │
│ - Executes on user logon or system startup                 │
│ - Requires obfuscation of payload and value names          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ SECONDARY: Startup Folder Persistence                      │
│ - Multiple file formats (VBS, Batch, PowerShell)           │
│ - Multiple startup locations                               │
│ - Executes when user logs on or session starts             │
│ - Provides persistence even if registry is cleaned         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ TERTIARY: Scheduled Task Persistence                       │
│ - Multiple trigger types (Logon, Startup, Idle, Network)  │
│ - System-level execution with elevated privileges          │
│ - Independent of user logon (runs with SYSTEM account)     │
│ - Survives user account deletion                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ FALLBACK CHAIN: Recovery Mechanism                         │
│ - Detects persistence failure                              │
│ - Automatically re-deploys all methods                      │
│ - Ensures continuity across detection/removal attempts     │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

### Core Classes

#### `PersistenceConfig`
Configuration dataclass containing all persistence parameters.

**Key Parameters:**
- `payload` - The command or executable to run
- `obfuscation_enabled` - Enable/disable payload obfuscation
- `obfuscation_level` - Level of obfuscation (low/medium/high/extreme)
- `registry_hives` - List of registry hives to use
- `registry_paths` - List of registry paths for persistence
- `use_startup_folder` - Enable startup folder persistence
- `startup_extensions` - File formats for startup (.vbs/.bat/.ps1)
- `use_scheduled_task` - Enable scheduled task persistence
- `task_triggers` - Types of scheduled task triggers
- `enable_fallback_chain` - Enable automatic recovery mechanism
- `randomize_names` - Randomize registry/file/task names

#### `MultiMethodPersistence`
Main persistence implementation class.

**Key Methods:**
- `generate_registry_persistence()` - Generate registry payloads
- `generate_startup_persistence()` - Generate startup folder payloads
- `generate_scheduled_task_persistence()` - Generate scheduled task payloads
- `generate_fallback_chain()` - Generate fallback recovery mechanism
- `generate_all_persistence_methods()` - Generate all methods
- `generate_combined_installer()` - Generate master installer
- `get_deployment_summary()` - Display deployment information

### Enumerations

#### `RegistryHive`
```python
HKCU = "HKCU"  # Current user
HKLM = "HKLM"  # Local machine
HKCC = "HKCC"  # Current configuration
HKU = "HKU"    # Users
HKCR = "HKCR"  # Classes root
```

#### `ScheduledTaskTrigger`
```python
LOGON = "logon"        # Trigger at user logon
STARTUP = "startup"    # Trigger at system startup
IDLE = "idle"          # Trigger when system is idle
INTERVAL = "interval"  # Trigger at specific interval
DAILY = "daily"        # Trigger daily at specific time
WEEKLY = "weekly"      # Trigger weekly
ONCONNECT = "onconnect"  # Trigger on network connect
```

## Persistence Methods

### 1. Registry Persistence

**Mechanism:** Stores payload reference in Windows Registry Run keys

**Advantages:**
- No file creation needed (harder to detect)
- Executes automatically on user logon
- Survives system restart

**Supported Hives:**
- HKCU (User-level, no admin required)
- HKLM (System-level, admin required)
- HKU (All users)

**Supported Paths:**
- `Software\Microsoft\Windows\CurrentVersion\Run`
- `Software\Microsoft\Windows\CurrentVersion\RunOnce`
- `Software\Policies\Microsoft\Windows\Explorer`
- `Software\Microsoft\Internet Explorer\Desktop\Components`

**Evasion Techniques:**
- Randomized value names (appear as legitimate services)
- Payload encoding (base64/hex)
- Multiple redundant entries
- Error suppression in VBS wrapper

**Example:**
```python
config = PersistenceConfig(
    payload="calc.exe",
    registry_hives=[RegistryHive.HKCU, RegistryHive.HKLM],
    use_startup_folder=False,
    use_scheduled_task=False
)
persistence = MultiMethodPersistence(config)
registry_payloads = persistence.generate_registry_persistence()
```

### 2. Startup Folder Persistence

**Mechanism:** Places executable scripts in startup folders

**Advantages:**
- User-level persistence (no admin required)
- Multiple startup locations increase redundancy
- Different file formats for flexibility

**Supported Formats:**
- `.vbs` - VBScript (executed by cscript.exe)
- `.bat` - Batch script (executed by cmd.exe)
- `.ps1` - PowerShell script (executed by powershell.exe)

**Startup Locations:**
- User Startup folder
- AppData Startup
- ProgramData Startup
- Public startup folder

**Evasion Techniques:**
- Obfuscated script names (appear as system services)
- Hidden script content (encoded payload)
- Multiple file formats
- Redundant copies in multiple locations

**Example:**
```python
config = PersistenceConfig(
    payload="cmd.exe /c ipconfig",
    use_startup_folder=True,
    startup_extensions=[".vbs", ".bat", ".ps1"],
    registry_hives=[],
    use_scheduled_task=False
)
persistence = MultiMethodPersistence(config)
startup_payloads = persistence.generate_startup_persistence()
```

### 3. Scheduled Task Persistence

**Mechanism:** Creates Windows Scheduled Task with multiple triggers

**Advantages:**
- System-level execution (higher privileges)
- Independent of user logon
- Multiple trigger options
- Survives user account changes

**Supported Triggers:**
- **Logon** - Executes when user logs on
- **Startup** - Executes at system boot
- **Idle** - Executes when system is idle
- **Interval** - Executes at regular intervals
- **Daily** - Executes daily at specific time
- **Weekly** - Executes weekly
- **OnConnect** - Executes when network connects

**Task Properties:**
- Hidden from normal view
- Auto-start on system availability
- High priority execution
- Survives anti-malware removal

**Evasion Techniques:**
- Legitimate-looking task names
- Spoofed author (Microsoft Corporation)
- Task scheduler XML encoding
- Multiple trigger types for redundancy

**Example:**
```python
config = PersistenceConfig(
    payload="powershell.exe -NoProfile -Command 'Get-Process'",
    registry_hives=[],
    use_startup_folder=False,
    use_scheduled_task=True,
    task_triggers=[
        ScheduledTaskTrigger.LOGON,
        ScheduledTaskTrigger.STARTUP,
        ScheduledTaskTrigger.INTERVAL
    ]
)
persistence = MultiMethodPersistence(config)
task_payloads = persistence.generate_scheduled_task_persistence()
```

### 4. Fallback Chain

**Mechanism:** Automatic recovery and re-deployment

**Features:**
- Detects if any persistence method fails
- Automatically re-deploys failed methods
- Attempts multiple fallback strategies
- Ensures continuity across cleanup attempts

**Fallback Strategy:**
1. Attempt Registry persistence
2. If registry fails, attempt Startup folder
3. If startup fails, attempt direct execution
4. If any fails, fallback chain restores all methods

**Example:**
```python
config = PersistenceConfig(
    payload="calc.exe",
    enable_fallback_chain=True,
    use_startup_folder=True,
    use_scheduled_task=True
)
persistence = MultiMethodPersistence(config)
fallback = persistence.generate_fallback_chain()
```

## Usage Examples

### Example 1: Minimal Configuration (Registry Only)

```python
from advanced_persistence_multimethods import (
    MultiMethodPersistence, PersistenceConfig, RegistryHive
)

config = PersistenceConfig(
    payload="notepad.exe",
    obfuscation_enabled=True,
    obfuscation_level="medium",
    registry_hives=[RegistryHive.HKCU],
    use_startup_folder=False,
    use_scheduled_task=False
)

persistence = MultiMethodPersistence(config)
registry_payloads = persistence.generate_registry_persistence()
```

### Example 2: Lightweight Configuration

```python
config = PersistenceConfig(
    payload="calc.exe",
    use_scheduled_task=False
)

persistence = MultiMethodPersistence(config)
all_payloads = persistence.generate_all_persistence_methods()
```

### Example 3: Maximum Redundancy

```python
config = PersistenceConfig(
    payload="powershell.exe -NoProfile -WindowStyle Hidden -Command 'Get-Process'",
    obfuscation_enabled=True,
    obfuscation_level="extreme",
    registry_hives=[RegistryHive.HKCU, RegistryHive.HKLM],
    registry_paths=[
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
        "Software\\Policies\\Microsoft\\Windows\\Explorer",
        "Software\\Microsoft\\Internet Explorer\\Desktop\\Components"
    ],
    use_startup_folder=True,
    startup_extensions=[".vbs", ".bat", ".ps1"],
    use_scheduled_task=True,
    task_triggers=[
        ScheduledTaskTrigger.LOGON,
        ScheduledTaskTrigger.STARTUP,
        ScheduledTaskTrigger.INTERVAL,
        ScheduledTaskTrigger.DAILY
    ],
    enable_fallback_chain=True,
    randomize_names=True
)

persistence = MultiMethodPersistence(config)
persistence.generate_all_persistence_methods()
print(persistence.get_deployment_summary())
```

### Example 4: Combined Installer

```python
config = PersistenceConfig(payload="calc.exe")
persistence = MultiMethodPersistence(config)
installer = persistence.generate_combined_installer()

# Save to file
with open("installer.vbs", "w") as f:
    f.write(installer)
```

## Obfuscation Techniques

### Encoding Methods

1. **Base64 Encoding**
   - Standard encoding used by VBScript MSXML2
   - Avoids detection of plain-text payloads
   - Supports strings up to 32KB

2. **Hex Encoding**
   - Alternative encoding method
   - Harder to decode manually
   - Character-by-character conversion

### Name Randomization

When `randomize_names=True`:

**Registry Values:**
- WindowsUpdate
- SystemRestore
- SpeechRuntime
- NtfsVolume
- ScheduledDefrag
- DiskOptimizer
- SecurityCheck
- MaintenanceTask
- CryptoService

**File Names:**
- WindowsDefender
- SystemService
- HostService
- NetworkAdapter
- AudioDriver
- GraphicsEngine
- SecurityUpdate
- MaintenanceTask
- BackupService

**Task Names:**
- SystemMaintenance
- WindowsUpdate
- ScheduledDefrag
- DiskOptimizer
- SystemRestore
- ServiceRestarter
- CacheManager
- NetworkMonitor
- DriverUpdate

### Error Suppression

All generated code includes:
- `On Error Resume Next` in VBS
- `-ErrorAction SilentlyContinue` in PowerShell
- Try/catch blocks where applicable

This prevents error messages and maintains stealth.

## Redundancy Analysis

### Removal Scenarios

**Scenario 1: Registry Cleanup**
```
Removed: Registry keys
Surviving: Startup folder scripts, Scheduled tasks
Result: Persistence maintained ✓
```

**Scenario 2: Startup Folder Cleanup**
```
Removed: Startup folder files
Surviving: Registry keys, Scheduled tasks
Result: Persistence maintained ✓
```

**Scenario 3: Task Scheduler Cleanup**
```
Removed: Scheduled tasks
Surviving: Registry keys, Startup folder files
Result: Persistence maintained ✓
```

**Scenario 4: Multi-Method Cleanup (>1 method removed)**
```
Removed: 2 of 3 methods
Surviving: 1 method
Action: Fallback chain re-deploys all 3 methods
Result: Full persistence restored ✓
```

**Scenario 5: Complete Cleanup Attempt**
```
Removed: All 3 methods + fallback chain
Surviving: None
Result: Persistence lost (requires 100% cleanup)
Cleanup Difficulty: EXTREME
```

## Deployment Strategies

### Phase 1: Initial Payload (First Contact)
- Deliver via PowerShell one-liner, batch script, or exploit
- Execute multi-method persistence installer
- Deploy all three methods simultaneously

### Phase 2: Registry Persistence (Quick Fallback)
- Executes next user logon
- No admin required (HKCU)
- Invisible to most tools

### Phase 3: Startup Folder (User-Level)
- Executes on session start
- Hard to detect without inspection
- Survives registry cleanup

### Phase 4: Scheduled Tasks (System-Level)
- Multiple triggers provide redundancy
- System-level privileges
- Independent of user logon

### Phase 5: Fallback Chain (Recovery)
- Monitors persistence status
- Re-deploys on detection of failure
- Ensures automatic recovery

## Detection Evasion

### Techniques Implemented

1. **Payload Encoding**
   - Base64/Hex encoding avoids content-based detection
   - Dynamic decoding on execution
   - Supports obfuscation levels: low/medium/high/extreme

2. **Name Obfuscation**
   - Randomized registry values (appear as system services)
   - Spoofed file names (Windows system names)
   - Legitimate task names (Microsoft services)

3. **Location Variation**
   - Multiple registry hives (HKCU + HKLM)
   - Multiple registry paths (Run + RunOnce + Explorer + IE)
   - Multiple startup locations (AppData + ProgramData + Public)
   - Multiple task triggers (Logon + Startup + Idle + etc)

4. **Execution Concealment**
   - Hidden window mode (`-WindowStyle Hidden`)
   - Background process creation (WMI exec)
   - No command line visibility (encoded in registry)
   - Error suppression prevents notifications

5. **Privilege Handling**
   - User-level methods (no admin required)
   - System-level methods (admin persistence)
   - Automatic fallback for privilege failures
   - Support for both HKCU and HKLM

## Testing

### Unit Tests

Comprehensive test suite with 41 test cases covering:
- Configuration validation
- Registry persistence generation
- Startup folder persistence
- Scheduled task creation
- Fallback chain mechanisms
- Multi-method combinations
- Obfuscation functionality
- Name randomization
- Payload generation
- Error handling

**Run tests:**
```bash
python3 test_advanced_persistence.py
```

**Expected output:**
```
Ran 41 tests in 0.004s
OK
```

### Examples

Comprehensive examples demonstrating:
1. Basic registry persistence
2. Startup folder with all formats
3. Scheduled task with multiple triggers
4. Full redundancy configuration
5. Fallback chain mechanisms
6. Master installer generation
7. Anti-removal techniques
8. Stealth and evasion techniques
9. Configuration showcase
10. Deployment strategies

**Run examples:**
```bash
python3 advanced_persistence_examples.py
```

## Output Formats

### Generated Payloads

1. **VBScript** (.vbs)
   - Windows native language
   - Maximum compatibility
   - Supports registry, startup, scheduled tasks
   - Size: 800-8000 characters

2. **Batch Script** (.bat)
   - Simple command execution
   - Used for startup folder
   - Size: 500-1500 characters

3. **PowerShell** (.ps1)
   - Modern execution environment
   - Better obfuscation support
   - System task registration
   - Size: 900-8000 characters

4. **XML Task Definition**
   - Windows Task Scheduler format
   - Machine-readable task definition
   - Supports complex trigger configurations
   - Size: 2000-3000 characters

## Performance Characteristics

### Payload Generation Time
- Basic configuration: < 1ms
- Full configuration: < 5ms
- All methods with obfuscation: < 10ms

### Payload Size
- Registry payload (single): 780 bytes
- Startup payload (single): 500-1700 bytes
- Scheduled task payload: 1600-8200 bytes
- Combined installer: 5000+ bytes

### Redundancy Metrics
- Minimum persistence points: 3 (1 registry + 1 startup + 1 task)
- Maximum persistence points: 13+ (6 registry + 3 startup + 3 task + 1 fallback)
- Average redundancy: 7-10 persistence points

## Security Considerations

### For Authorized Testing Only

This system is designed for authorized security testing, penetration testing, and red team exercises. Use only:
- With proper authorization
- In controlled environments
- For legitimate security research
- In compliance with applicable laws

### Cleanup

To remove persistence:
1. Delete registry entries from all hives and paths
2. Remove startup folder files from all locations
3. Delete scheduled tasks via Task Scheduler
4. Disable fallback chain if still active

**Note:** Complete cleanup requires removing all persistence points simultaneously to prevent fallback chain re-deployment.

## Advanced Features

### Custom Configuration

Create specialized configurations for specific scenarios:

```python
config = PersistenceConfig(
    payload="your_payload_here",
    obfuscation_enabled=True,
    obfuscation_level="extreme",
    registry_hives=[RegistryHive.HKCU, RegistryHive.HKLM],
    registry_paths=["your_custom_paths"],
    use_startup_folder=True,
    use_scheduled_task=True,
    enable_fallback_chain=True,
    randomize_names=True
)
```

### Deployment Summary

Get detailed information about generated payloads:

```python
persistence = MultiMethodPersistence(config)
print(persistence.get_deployment_summary())
```

Output includes:
- Configuration details
- Number of variants per method
- Total payload count
- Redundancy levels
- Evasion techniques applied

### Payload Tracking

Track all generated payloads:

```python
persistence = MultiMethodPersistence(config)
persistence.generate_all_persistence_methods()

for key, code in persistence.generated_code.items():
    print(f"{key}: {len(code)} characters")
```

## References

### Related Components
- `vbs_encoder.py` - VBScript encoding and obfuscation
- `registry_storage_examples.py` - Registry persistence examples
- `payload_file_writer_variants.py` - File writing techniques

### Windows APIs Used
- `WScript.Shell.RegWrite` - Registry writing
- `WScript.Shell.RegRead` - Registry reading
- `FileSystemObject` - File operations
- `Win32_Process` - Process creation
- `Schedule.Service` - Task scheduler

## License

For authorized security testing and research only.
Not intended for malicious purposes.
Use responsibly and legally.

---

**Version:** 1.0
**Last Updated:** June 29, 2026
**Status:** Production Ready
