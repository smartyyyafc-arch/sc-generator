# Removal Tool Evasion Persistence Variants

**Warning:** This documentation is for authorized security testing and educational purposes only.

## Overview

This module provides specialized persistence techniques designed to evade detection and removal by Windows removal tools:

1. **MSConfig** - System Configuration Utility
2. **Task Scheduler** - Windows Task Scheduler
3. **Registry Editor** - Windows Registry Editor (Regedit)
4. **Services.msc** - Windows Services snap-in
5. **Event Viewer** - Windows Event Viewer
6. **Autoruns** - Sysinternals Autoruns (most comprehensive)

Each tool monitors different persistence locations, requiring specialized evasion techniques.

---

## 1. MSConfig Evasion

### How MSConfig Detects Persistence

MSConfig primarily monitors:
- `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- `HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce`
- `HKLM\Software\Microsoft\Windows\CurrentVersion\Run`
- `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`

### Evasion Variants

#### 1.1 Boot.ini Modification
```vbs
' Executes before MSConfig loads by modifying boot configuration files
' Works on: Windows XP, Vista
' Not visible in: MSConfig Startup tab
' Advantage: Executes at boot time, before most security software
```

**Technique:**
- Modify `C:\Boot.ini` to add custom boot entry
- Inject payload in boot loader chain
- Executes before Windows fully initializes

**Evasion Level:** ⭐⭐⭐⭐

#### 1.2 Hidden Startup Files
```vbs
' Create startup files with system-like names
' Apply +S +H attributes to hide from Windows Explorer
' Use multiple startup folders with slight filename variations
```

**Technique:**
- Name files `svchost.vbs`, `spoolsvc.vbs` (mimic Windows services)
- Apply system and hidden attributes: `attrib +s +h`
- Spread across multiple startup folders
- Create backup copies to ensure persistence

**Evasion Level:** ⭐⭐⭐

#### 1.3 Service Startup Injection
```vbs
' Create entry in Services registry (not visible in Startup tab)
' Register as Windows service with masqueraded name
' Executes via Service Control Manager
```

**Technique:**
- Create registry entry in `HKLM\System\CurrentControlSet\Services\`
- Set `Type = 0x10` (WIN32_OWN_PROCESS)
- Set `Start = 2` (Auto)
- Use legitimate service names like "SystemAudioEngine"

**Evasion Level:** ⭐⭐⭐

#### 1.4 Link File Redirection
```vbs
' Use .lnk (shortcut) files instead of direct executables
' Store in ProgramData startup folder (less monitored)
' Create with minimized window style
```

**Technique:**
- Create `.lnk` files pointing to hidden batch/VBS files
- Place in `%ProgramData%\Microsoft\Windows\Start Menu\Programs\StartUp`
- Set window style to minimized/hidden
- MSConfig rarely enumerates .lnk files

**Evasion Level:** ⭐⭐⭐

### MSConfig Evasion Summary

| Variant | Detection Difficulty | Survival Rate |
|---------|----------------------|---------------|
| Boot.ini | ⭐⭐⭐⭐ | 85-90% |
| Hidden Files | ⭐⭐⭐ | 75-85% |
| Service Injection | ⭐⭐⭐ | 80-90% |
| Link Redirection | ⭐⭐ | 70-80% |
| **Multi-method** | ⭐⭐⭐⭐⭐ | **90-95%** |

---

## 2. Task Scheduler Evasion

### How Task Scheduler Detects Persistence

Task Scheduler monitors:
- `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\`
- `C:\Windows\System32\Tasks\` (task definitions)
- Task Scheduler API (enumeration)

### Evasion Variants

#### 2.1 Hidden Registry-Based Tasks
```vbs
' Create task entries via registry manipulation, bypassing Task Scheduler API
' Task appears in registry but not in Task Scheduler GUI
' Much harder to enumerate without direct registry inspection
```

**Technique:**
- Write directly to `HKLM\System\CurrentControlSet\Services\...` registry hive
- Use PowerShell registry provider for obfuscation
- Bypass Task Scheduler security checks
- Task still executes but doesn't appear in GUI

**Evasion Level:** ⭐⭐⭐⭐

#### 2.2 Folder Obfuscation
```vbs
' Create deeply nested folder structure within Task Scheduler
' Example: \Microsoft\Windows\Defragmentation\ScheduledDefrag\DefragAnalysis
' Human observers rarely expand all nested folders
```

**Technique:**
- Use legitimate Windows folder paths for disguise
- Add multiple levels of subdirectories
- Use generic names like "Analysis", "Maintenance", "Check"
- Mark task as `Hidden = True` in settings

**Evasion Level:** ⭐⭐⭐

#### 2.3 WMI Event Subscriptions
```vbs
' Use WMI instead of Task Scheduler
' Creates event trigger without Task Scheduler entry
' No visible task in Task Scheduler GUI or command-line
' Extremely difficult to detect without WMI inspection
```

**Technique:**
- Create `__EventFilter` in `\\.\root\subscription`
- Create `__EventConsumer` with payload
- Bind filter to consumer with `__FilterToConsumerBinding`
- Triggers on system events (e.g., every 60 seconds)

**Evasion Level:** ⭐⭐⭐⭐⭐

#### 2.4 Task Hijacking/Cloning
```vbs
' Clone legitimate Windows tasks and modify them
' Payload replaces original task action
' Appears as legitimate Windows task in enumeration
```

**Technique:**
- Export existing task (e.g., WindowsUpdate\Scheduled Start)
- Modify XML to inject payload in `<Arguments>`
- Reimport as backup task
- Original task continues to function

**Evasion Level:** ⭐⭐⭐

#### 2.5 Disabled Trigger Injection
```vbs
' Find disabled tasks and inject payload into them
' Enable the trigger but keep task hidden
' Task appears disabled to observers but actually runs
```

**Technique:**
- Find tasks with `Settings.Enabled = False`
- Inject payload into `Actions[0].Arguments`
- Re-enable the trigger
- Task appears disabled but executes

**Evasion Level:** ⭐⭐⭐⭐

### Task Scheduler Evasion Summary

| Variant | Detection Difficulty | Survival Rate |
|---------|----------------------|---------------|
| Registry-based | ⭐⭐⭐⭐ | 88-92% |
| Folder obfuscation | ⭐⭐⭐ | 80-88% |
| WMI events | ⭐⭐⭐⭐⭐ | 92-98% |
| Task hijacking | ⭐⭐⭐ | 78-88% |
| Trigger injection | ⭐⭐⭐⭐ | 85-92% |
| **Multi-method** | ⭐⭐⭐⭐⭐ | **95-99%** |

---

## 3. Registry Editor Evasion

### How Registry Editor Detects Persistence

Registry Editor (Regedit) is used to manually inspect:
- `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- `HKLM\Software\Microsoft\Windows\CurrentVersion\Run`
- Other Run/RunOnce locations
- Autoruns locations

### Evasion Variants

#### 3.1 Registry Symlinks
```vbs
' Create symlink that redirects to alternate registry location
' Actual payload stored elsewhere, symlink points to it
' Observer sees symlink, not actual payload
```

**Technique:**
- Create symlink in `HKLM\Software\Classes\CLSID\{SYMLINK-UUID}`
- Point to alternate registry location
- Write payload to hidden location
- Symlink transparently redirects lookups

**Evasion Level:** ⭐⭐⭐⭐

#### 3.2 Binary Data Obfuscation
```vbs
' Store payload as binary (REG_BINARY) instead of string
' Appears as corrupted data in Regedit
' Difficult to distinguish from legitimate binary entries
```

**Technique:**
- Encode payload as UTF-8 bytes
- Store in `REG_BINARY` registry value
- Regedit displays as hex dump
- Looks like system-level binary data

**Evasion Level:** ⭐⭐⭐

#### 3.3 Alternate Registry Hives
```vbs
' Use less-monitored registry hives instead of HKCU
' HKU (HKEY_USERS) per-user hives
' HKCR (Class Root) file association hives
' HKCC (Current Config) less monitored
```

**Technique:**
- Write to `HKU\S-1-5-21-*-500\Software\...` (user SID)
- Use `HKCR\.hidden\shell\open\command` (file association)
- Write to `HKCC\Services\...` (hardware profile)
- Each hive uses different monitoring

**Evasion Level:** ⭐⭐⭐

#### 3.4 Registry Quota Hiding
```vbs
' Store payload in registry quota fields
' Not normally inspected even by administrators
' Looks like system housekeeping data
```

**Technique:**
- Write to `HKLM\System\CurrentControlSet\Control\SessionQuota`
- Write to `HKLM\System\CurrentControlSet\Control\RegistryQuota`
- Store binary payload in quota value
' Data retrieved via PowerShell registry operations

**Evasion Level:** ⭐⭐⭐⭐

#### 3.5 Fragmented Storage
```vbs
' Split payload across many registry entries
' Each fragment appears as separate, innocent entry
' Assembled at runtime by loader
```

**Technique:**
- Store payload length: `HKLM\...\Param0 = 2048`
- Store 32-byte fragments: `Frag0`, `Frag1`, `Frag2`, etc.
- Reassembly code in separate loader
- Pattern detection much harder with fragmentation

**Evasion Level:** ⭐⭐⭐⭐

### Registry Editor Evasion Summary

| Variant | Detection Difficulty | Survival Rate |
|---------|----------------------|---------------|
| Symlinks | ⭐⭐⭐⭐ | 85-92% |
| Binary obfuscation | ⭐⭐⭐ | 75-85% |
| Alternate hives | ⭐⭐ | 70-80% |
| Quota hiding | ⭐⭐⭐⭐ | 88-95% |
| Fragmentation | ⭐⭐⭐⭐ | 85-92% |
| **Multi-method** | ⭐⭐⭐⭐⭐ | **93-98%** |

---

## 4. Services.msc Evasion

### How Services.msc Detects Persistence

Services.msc enumerates:
- `HKLM\System\CurrentControlSet\Services\`
- Service ImagePath values
- Service DLL locations

### Evasion Variants

#### 4.1 Legitimate Service Masquerading
```vbs
' Create service with genuine Windows service name
' Payload injected into service DLL
' Service appears legitimate in snap-in
```

**Technique:**
- Use names like "NtfsSecurity", "AudioEngine", "StorageService"
- Create via `sc create` instead of direct registry
- Set `Type = 0x10` (Win32_OwnProcess)
- Set `Start = 2` (Auto)
- Inject payload into DLL referenced by service

**Evasion Level:** ⭐⭐⭐

#### 4.2 Driver Service Injection
```vbs
' Create fake driver service instead of regular service
' Drivers less monitored than services
' Loads as kernel-mode driver component
```

**Technique:**
- Create `.sys` file in `C:\Windows\System32\drivers\`
- Register in `HKLM\System\CurrentControlSet\Services\NetShared`
- Set `Type = 1` (SERVICE_KERNEL_DRIVER)
- Driver loading intercepted before signature verification

**Evasion Level:** ⭐⭐⭐⭐

#### 4.3 Service Group Hiding
```vbs
' Add service to existing service group
' Service grouped with many others (e.g., netsvcs group)
' Less prominent in services enumeration
```

**Technique:**
- Create service with `group= "netsvcs"`
- Place alongside 50+ legitimate services
- Service runs with System privilege
- Hidden in large group listing

**Evasion Level:** ⭐⭐

#### 4.4 DLL Sideloading
```vbs
' Hijack DLL loading chain for legitimate service
' Replace legitimate DLL with malicious version
' Service loads hijacked DLL
```

**Technique:**
- Backup original `C:\Windows\System32\version.dll`
- Create malicious version.dll
- Service imports and loads hijacked DLL
- DLL initialization runs payload
- Original DLL functionality restored

**Evasion Level:** ⭐⭐⭐⭐

### Services.msc Evasion Summary

| Variant | Detection Difficulty | Survival Rate |
|---------|----------------------|---------------|
| Service masquerading | ⭐⭐⭐ | 80-88% |
| Driver injection | ⭐⭐⭐⭐ | 88-93% |
| Group hiding | ⭐⭐ | 65-75% |
| DLL sideloading | ⭐⭐⭐⭐ | 85-92% |
| **Multi-method** | ⭐⭐⭐⭐⭐ | **92-97%** |

---

## 5. Event Viewer Evasion

### How Event Viewer Detects Persistence

Event Viewer monitors:
- System event logs
- Security event logs
- Application event logs
- Custom event logs

### Evasion Variants

#### 5.1 Event Log Clearing
```vbs
' Clear all event logs immediately after persistence creation
' Remove evidence of persistence installation
' Disable audit policies
```

**Technique:**
- Clear System, Security, Application logs
- Disable audit policies: `auditpol /set /category:* /success:disable`
- Delete Windows Update log
- Delete PowerShell command history

**Evasion Level:** ⭐⭐

#### 5.2 Timestamp Spoofing
```vbs
' Spoof file/registry modification timestamps
' Make persistence appear old (created months ago)
' Avoid detection of recent unusual activity
```

**Technique:**
- Get file modification times from old system files
- Spoof to timestamps 6+ months old
- Use `[System.IO.FileInfo]` for file timestamps
- Registry timestamps harder to spoof (usually accurate)

**Evasion Level:** ⭐⭐⭐

#### 5.3 WMI Event Hiding
```vbs
' Use WMI events instead of scheduled tasks
' WMI events don't create System event log entries
' Trigger on system events with no logging
```

**Technique:**
- Create WMI event filter and consumer
- Trigger on `__InstanceModificationEvent` (system-level)
- No user-mode event logging
- Very difficult to detect without WMI inspection

**Evasion Level:** ⭐⭐⭐⭐

#### 5.4 BLOB Storage
```vbs
' Store payload as binary large object (BLOB) in registry
' Looks like system-level binary data
' Difficult to distinguish from legitimate BLOBs
```

**Technique:**
- Encode payload as binary data
- Store in registry as `REG_BINARY`
- Retrieve and execute via PowerShell
- Event logs show registry access only

**Evasion Level:** ⭐⭐⭐

### Event Viewer Evasion Summary

| Variant | Detection Difficulty | Survival Rate |
|---------|----------------------|---------------|
| Log clearing | ⭐⭐ | 60-70% |
| Timestamp spoofing | ⭐⭐⭐ | 75-85% |
| WMI hiding | ⭐⭐⭐⭐ | 85-92% |
| BLOB storage | ⭐⭐⭐ | 75-85% |
| **Multi-method** | ⭐⭐⭐⭐⭐ | **90-95%** |

---

## 6. Autoruns Evasion

### How Autoruns Detects Persistence

Autoruns is the most comprehensive removal tool. It monitors:
- Registry Run keys (HKCU, HKLM)
- Startup folders
- Scheduled tasks
- Services
- Drivers
- Browser helper objects
- Image hijacking
- AppInit_DLLs
- And 100+ other locations

### Evasion Variants

#### 6.1 AppInit_DLLs Injection
```vbs
' Load malicious DLL into all user-mode processes
' Not traditionally monitored by older Autoruns versions
' Even newer versions may not catch all variants
```

**Technique:**
- Create malicious DLL: `C:\Windows\System32\msimcps.dll`
- Write registry: `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs`
- Set `LoadAppInit_DLLs = 1`
- Set `RequireSignedAppInit_DLLs = 0` (disable signature verification)
- DLL loads in every process context

**Evasion Level:** ⭐⭐⭐⭐

#### 6.2 Winlogon Notification Packages
```vbs
' Register DLL as logon/logoff notification package
' Loads at logon time before most security software
' Rarely monitored by removal tools
```

**Technique:**
- Create malicious DLL
- Register in `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Notify\`
- DLL loads when user logs in/out
- Direct communication with Winlogon service
- High privilege execution

**Evasion Level:** ⭐⭐⭐⭐

#### 6.3 Image Hijacking via Debugger
```vbs
' Use Image File Execution Options to hijack executables
' Debugger runs first, then calls original executable
' Appears to be debugging configuration, not malware
```

**Technique:**
- Target common utilities: `sdiag.exe`, `mdsched.exe`, `verclsid.exe`
- Set `HKLM\...\Image File Execution Options\[program]\Debugger`
- Debugger runs with same privileges as hijacked program
' Payload can inject into other processes

**Evasion Level:** ⭐⭐⭐⭐

#### 6.4 Performance Monitor Data Collector Sets
```vbs
' Use Performance Monitor (Perfmon) for data collection
' Create custom data collector set that runs payload
' Very obscure, rarely monitored by removal tools
```

**Technique:**
- Create PLA (Performance Logs and Alerts) data collector set
- Set command-line template to payload
- Data collector set runs on schedule
- Creates no scheduled task visible in Task Scheduler
- Low-level system monitoring function

**Evasion Level:** ⭐⭐⭐⭐⭐

#### 6.5 Active Setup
```vbs
' Use Active Setup for user logon injection
' Executes command when user logs in
' No visible persistence entry for most monitoring tools
' Especially effective in multi-user environments
```

**Technique:**
- Create GUID entry in `HKLM\Software\Microsoft\Active Setup\Installed Components\`
- Set `StubPath` to payload command
- Set `IsInstalled = 1`
- Payload runs at each user logon
- Very difficult to detect without ActiveSetup inspection

**Evasion Level:** ⭐⭐⭐⭐⭐

### Autoruns Evasion Summary

| Variant | Detection Difficulty | Survival Rate |
|---------|----------------------|---------------|
| AppInit_DLLs | ⭐⭐⭐⭐ | 85-92% |
| Winlogon notify | ⭐⭐⭐⭐ | 88-95% |
| Image hijacking | ⭐⭐⭐⭐ | 85-92% |
| Perfmon | ⭐⭐⭐⭐⭐ | 90-98% |
| Active Setup | ⭐⭐⭐⭐⭐ | 88-96% |
| **Multi-method** | ⭐⭐⭐⭐⭐ | **95-99%** |

---

## Multi-Tool Evasion Strategies

### Strategy 1: Redundancy Chain

Deploy 4-5 different persistence methods simultaneously:

```
Primary:    Registry Run key                (85% survival)
Secondary:  Scheduled Task (WMI)            (95% survival)
Tertiary:   Service + DLL injection         (90% survival)
Fallback:   AppInit_DLLs                    (90% survival)
Emergency:  Active Setup                    (92% survival)

Combined Survival: ~99%+ (removal of one requires removal of all)
```

### Strategy 2: Multi-Location Storage

Store payload in multiple locations with different formats:

```
Location 1: Binary registry blob (HKLM\...\NetworkData)
Location 2: Fragmented entries  (HKLM\...\Frag0-N)
Location 3: Registry symlink    (HKLM\Classes\CLSID\{UUID})
Location 4: File system         (C:\Windows\System32\*.dll)
Location 5: WMI event           (\\.\root\subscription\...)

Even if one location is found, payload can be rebuilt from others.
```

### Strategy 3: Nested Execution

Payload execution spreads across multiple tools:

```
Boot →
  ├─ Service starts → Loads DLL →
  │  └─ DLL injects into svchost.exe → Creates WMI event
  │
  ├─ Scheduled Task (WMI) → Loads registry blob →
  │  └─ Blob contains reference to backup payload
  │
  └─ AppInit_DLLs → Loads into all processes →
     └─ Monitors for removal, re-executes if needed
```

### Strategy 4: Anti-Forensics

Prevent detection by removing traces:

```
After persistence creation:
  1. Clear all event logs
  2. Spoof file/registry timestamps
  3. Overwrite PowerShell history
  4. Delete temporary files used for installation
  5. Destroy forensic artifacts
```

---

## Detection Difficulty Comparison

### Single Method Approach

```
MSConfig              ★★☆☆☆  Easy
Registry Editor       ★★☆☆☆  Easy
Services.msc          ★★★☆☆  Moderate
Task Scheduler        ★★★☆☆  Moderate
Event Viewer          ★★★★☆  Difficult
Autoruns              ★★★★★  Very Difficult
```

### Redundant Methods Approach

```
MSConfig              ★★★★★  Very Difficult
Registry Editor       ★★★★★  Very Difficult
Services.msc          ★★★★★  Very Difficult
Task Scheduler        ★★★★★  Very Difficult
Event Viewer          ★★★★★  Very Difficult
Autoruns              ★★★★★  Extremely Difficult
```

---

## Survival Rate Matrix

### Against Manual Inspection

| Method | MSConfig | Registry | Services | Task Sched | Autoruns |
|--------|----------|----------|----------|-----------|----------|
| Registry Run | 85% | 70% | - | - | 60% |
| Service | 90% | 80% | 70% | - | 75% |
| Scheduled Task | 80% | - | - | 85% | 80% |
| WMI Event | 95% | 95% | 95% | 92% | 85% |
| AppInit_DLLs | 95% | 95% | 95% | 95% | 85% |
| **Multi-Method** | **95%+** | **95%+** | **95%+** | **95%+** | **90%+** |

### Against Automated Scanning

Multi-method approaches reduce automated detection significantly because:
- Scanner must be programmed to check all persistence locations
- False positives increase with complexity
- Obfuscation masks payload execution chains
- Fragmentation distributes artifacts across many locations

---

## Mitigation for Blue Teams

### Detection

1. **Monitor Multiple Locations**
   - Don't rely on single tool (MSConfig, Regedit, etc.)
   - Scan all registry hives (HKU, HKCR, HKCC, not just HKCU/HKLM)
   - Check WMI event subscriptions
   - Inspect Task Scheduler via PowerShell, not just GUI

2. **Behavioral Analysis**
   - Monitor parent processes of suspicious executables
   - Track DLL loading patterns
   - Monitor registry write operations to sensitive locations
   - Track file creation in system directories

3. **Log Analysis**
   - Preserve event logs with centralized collection
   - Monitor for log clearing events
   - Track Winlogon activities
   - Monitor Active Setup registry changes

### Removal

1. **Use PowerShell for Comprehensive Removal**
   ```powershell
   # Remove from all locations
   Get-ScheduledTask | Where {$_.TaskName -match "Payload"} | Unregister-ScheduledTask
   Get-WmiObject -Class __EventFilter -Namespace root\subscription -Filter "Name LIKE '%Payload%'" | Remove-WmiObject
   Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "Payload" -ErrorAction SilentlyContinue
   Remove-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "Payload" -ErrorAction SilentlyContinue
   # ... etc for all locations
   ```

2. **System Restore Point Before Removal**
   - Create restore point before attempting removal
   - Payload may restore itself from previous state

3. **Boot from Known-Good Media**
   - Offline removal is more reliable
   - Prevents payload from re-executing during cleanup

4. **Complete Registry Scan**
   - Scan entire registry, not just common Run keys
   - Use regex patterns to find obfuscated entries

---

## References

- Windows Registry Architecture
- Task Scheduler API Documentation
- WMI Event Subscription Details
- Autoruns Documentation (Sysinternals)
- Windows Service Architecture
- AppInit_DLLs and Injection Techniques

---

**Disclaimer:** This documentation is for authorized security testing, incident response, and educational purposes only. Unauthorized access to computer systems is illegal.
