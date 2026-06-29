#!/usr/bin/env python3
"""
WMI Registry Access Module
Provides VBS functions for reading and writing Windows registry via WMI
Supports both HKLM (HKEY_LOCAL_MACHINE) and HKCU (HKEY_CURRENT_USER)
Uses WbemScripting.SWbemLocator for registry operations
"""

import base64
import random
import string
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class RegistryConfig:
    """Configuration for WMI registry access"""
    obfuscate_names: bool = True
    hide_errors: bool = True
    use_locator: bool = True
    encode_values: bool = False


class WMIRegistryAccess:
    """
    WMI Registry Access using WbemScripting.SWbemLocator
    Provides read and write operations for Windows registry
    Supports HKLM and HKCU hives
    """

    # Registry hive constants
    HKEY_LOCAL_MACHINE = 0x80000002
    HKEY_CURRENT_USER = 0x80000001
    HKEY_CLASSES_ROOT = 0x80000000
    HKEY_USERS = 0x80000003
    HKEY_CURRENT_CONFIG = 0x80000005

    # Registry value types
    REG_SZ = 1  # String
    REG_EXPAND_SZ = 2  # Expandable string
    REG_BINARY = 3  # Binary
    REG_DWORD = 4  # DWORD (32-bit integer)
    REG_DWORD_BIG_ENDIAN = 5  # Big-endian DWORD
    REG_LINK = 6  # Symbolic link
    REG_MULTI_SZ = 7  # Multi-string
    REG_QWORD = 11  # QWORD (64-bit integer)

    def __init__(self, config: Optional[RegistryConfig] = None):
        self.config = config or RegistryConfig()
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

    def _get_hive_constant(self, hive: str) -> int:
        """Get registry hive constant"""
        hive_map = {
            "HKLM": self.HKEY_LOCAL_MACHINE,
            "HKCU": self.HKEY_CURRENT_USER,
            "HKCR": self.HKEY_CLASSES_ROOT,
            "HKU": self.HKEY_USERS,
            "HKCC": self.HKEY_CURRENT_CONFIG,
        }
        return hive_map.get(hive.upper(), self.HKEY_LOCAL_MACHINE)

    def read_registry_value(self, hive: str, key_path: str, value_name: str) -> str:
        """
        Generate VBS code to read registry value via WMI
        Returns value as string

        Args:
            hive: Registry hive (HKLM, HKCU, etc.)
            key_path: Full registry path (e.g., "SOFTWARE\\Microsoft\\Windows")
            value_name: Name of the value to read

        Returns:
            VBS code for reading registry value
        """
        var_locator = self._get_or_create_var("locator", "regLoc")
        var_svc = self._get_or_create_var("service", "regSvc")
        var_method = self._get_or_create_var("method", "regMeth")
        var_inparams = self._get_or_create_var("inparams", "regIn")
        var_outparams = self._get_or_create_var("outparams", "regOut")
        var_result = self._get_or_create_var("result", "regRes")
        var_value = self._get_or_create_var("value", "regVal")

        hive_const = self._get_hive_constant(hive)

        error_handling = ""
        if self.config.hide_errors:
            error_handling = "On Error Resume Next\n"

        vbs_code = f'''
{error_handling}
Dim {var_locator}, {var_svc}, {var_method}, {var_inparams}, {var_outparams}, {var_result}, {var_value}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\default")
Set {var_method} = {var_svc}.Get("StdRegProv").Methods_("GetStringValue")
Set {var_inparams} = {var_method}.InParameters.SpawnInstance_()

{var_inparams}.hDefKey = {hive_const}
{var_inparams}.sSubKeyName = "{key_path}"
{var_inparams}.sValueName = "{value_name}"

Set {var_outparams} = {var_svc}.ExecMethod("StdRegProv", "GetStringValue", {var_inparams})

If {var_outparams}.ReturnValue = 0 Then
    {var_value} = {var_outparams}.sValue
Else
    {var_value} = ""
End If

Set {var_method} = Nothing
Set {var_inparams} = Nothing
Set {var_outparams} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
'''
        if self.config.hide_errors:
            vbs_code += "On Error GoTo 0\n"

        return vbs_code.strip()

    def read_registry_dword(self, hive: str, key_path: str, value_name: str) -> str:
        """
        Generate VBS code to read DWORD registry value via WMI

        Args:
            hive: Registry hive (HKLM, HKCU, etc.)
            key_path: Full registry path
            value_name: Name of the DWORD value

        Returns:
            VBS code for reading DWORD value
        """
        var_locator = self._get_or_create_var("locator", "dregLoc")
        var_svc = self._get_or_create_var("service", "dregSvc")
        var_method = self._get_or_create_var("method", "dregMeth")
        var_inparams = self._get_or_create_var("inparams", "dregIn")
        var_outparams = self._get_or_create_var("outparams", "dregOut")
        var_result = self._get_or_create_var("result", "dregRes")
        var_value = self._get_or_create_var("value", "dregVal")

        hive_const = self._get_hive_constant(hive)

        error_handling = ""
        if self.config.hide_errors:
            error_handling = "On Error Resume Next\n"

        vbs_code = f'''
{error_handling}
Dim {var_locator}, {var_svc}, {var_method}, {var_inparams}, {var_outparams}, {var_result}, {var_value}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\default")
Set {var_method} = {var_svc}.Get("StdRegProv").Methods_("GetDWORDValue")
Set {var_inparams} = {var_method}.InParameters.SpawnInstance_()

{var_inparams}.hDefKey = {hive_const}
{var_inparams}.sSubKeyName = "{key_path}"
{var_inparams}.sValueName = "{value_name}"

Set {var_outparams} = {var_svc}.ExecMethod("StdRegProv", "GetDWORDValue", {var_inparams})

If {var_outparams}.ReturnValue = 0 Then
    {var_value} = {var_outparams}.uValue
Else
    {var_value} = 0
End If

Set {var_method} = Nothing
Set {var_inparams} = Nothing
Set {var_outparams} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
'''
        if self.config.hide_errors:
            vbs_code += "On Error GoTo 0\n"

        return vbs_code.strip()

    def read_registry_binary(self, hive: str, key_path: str, value_name: str) -> str:
        """
        Generate VBS code to read binary registry value via WMI

        Args:
            hive: Registry hive
            key_path: Full registry path
            value_name: Name of the binary value

        Returns:
            VBS code for reading binary value
        """
        var_locator = self._get_or_create_var("locator", "bregLoc")
        var_svc = self._get_or_create_var("service", "bregSvc")
        var_method = self._get_or_create_var("method", "bregMeth")
        var_inparams = self._get_or_create_var("inparams", "bregIn")
        var_outparams = self._get_or_create_var("outparams", "bregOut")
        var_result = self._get_or_create_var("result", "bregRes")
        var_value = self._get_or_create_var("value", "bregVal")

        hive_const = self._get_hive_constant(hive)

        error_handling = ""
        if self.config.hide_errors:
            error_handling = "On Error Resume Next\n"

        vbs_code = f'''
{error_handling}
Dim {var_locator}, {var_svc}, {var_method}, {var_inparams}, {var_outparams}, {var_result}, {var_value}
Dim i, {self._get_or_create_var("hex_str", "hStr")}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\default")
Set {var_method} = {var_svc}.Get("StdRegProv").Methods_("GetBinaryValue")
Set {var_inparams} = {var_method}.InParameters.SpawnInstance_()

{var_inparams}.hDefKey = {hive_const}
{var_inparams}.sSubKeyName = "{key_path}"
{var_inparams}.sValueName = "{value_name}"

Set {var_outparams} = {var_svc}.ExecMethod("StdRegProv", "GetBinaryValue", {var_inparams})

If {var_outparams}.ReturnValue = 0 Then
    {self._get_or_create_var("hex_str")} = ""
    For i = LBound({var_outparams}.uValue) To UBound({var_outparams}.uValue)
        {self._get_or_create_var("hex_str")} = {self._get_or_create_var("hex_str")} & Right("0" & Hex({var_outparams}.uValue(i)), 2)
    Next
    {var_value} = {self._get_or_create_var("hex_str")}
Else
    {var_value} = ""
End If

Set {var_method} = Nothing
Set {var_inparams} = Nothing
Set {var_outparams} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
'''
        if self.config.hide_errors:
            vbs_code += "On Error GoTo 0\n"

        return vbs_code.strip()

    def write_registry_value(self, hive: str, key_path: str, value_name: str,
                            value_data: str, value_type: str = "REG_SZ") -> str:
        """
        Generate VBS code to write string registry value via WMI

        Args:
            hive: Registry hive
            key_path: Full registry path
            value_name: Name of the value to write
            value_data: Value data to write
            value_type: Type of value (REG_SZ, REG_EXPAND_SZ, etc.)

        Returns:
            VBS code for writing registry value
        """
        var_locator = self._get_or_create_var("locator", "wrLoc")
        var_svc = self._get_or_create_var("service", "wrSvc")
        var_method = self._get_or_create_var("method", "wrMeth")
        var_inparams = self._get_or_create_var("inparams", "wrIn")
        var_outparams = self._get_or_create_var("outparams", "wrOut")
        var_result = self._get_or_create_var("result", "wrRes")

        hive_const = self._get_hive_constant(hive)
        # Escape quotes in value data
        escaped_value = value_data.replace('"', '\\"')

        error_handling = ""
        if self.config.hide_errors:
            error_handling = "On Error Resume Next\n"

        vbs_code = f'''
{error_handling}
Dim {var_locator}, {var_svc}, {var_method}, {var_inparams}, {var_outparams}, {var_result}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\default")
Set {var_method} = {var_svc}.Get("StdRegProv").Methods_("SetStringValue")
Set {var_inparams} = {var_method}.InParameters.SpawnInstance_()

{var_inparams}.hDefKey = {hive_const}
{var_inparams}.sSubKeyName = "{key_path}"
{var_inparams}.sValueName = "{value_name}"
{var_inparams}.sValue = "{escaped_value}"

Set {var_outparams} = {var_svc}.ExecMethod("StdRegProv", "SetStringValue", {var_inparams})
{var_result} = {var_outparams}.ReturnValue

Set {var_method} = Nothing
Set {var_inparams} = Nothing
Set {var_outparams} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
'''
        if self.config.hide_errors:
            vbs_code += "On Error GoTo 0\n"

        return vbs_code.strip()

    def write_registry_dword(self, hive: str, key_path: str, value_name: str,
                            value_data: int) -> str:
        """
        Generate VBS code to write DWORD registry value via WMI

        Args:
            hive: Registry hive
            key_path: Full registry path
            value_name: Name of the DWORD value
            value_data: DWORD value to write (integer)

        Returns:
            VBS code for writing DWORD value
        """
        var_locator = self._get_or_create_var("locator", "dwrLoc")
        var_svc = self._get_or_create_var("service", "dwrSvc")
        var_method = self._get_or_create_var("method", "dwrMeth")
        var_inparams = self._get_or_create_var("inparams", "dwrIn")
        var_outparams = self._get_or_create_var("outparams", "dwrOut")
        var_result = self._get_or_create_var("result", "dwrRes")

        hive_const = self._get_hive_constant(hive)

        error_handling = ""
        if self.config.hide_errors:
            error_handling = "On Error Resume Next\n"

        vbs_code = f'''
{error_handling}
Dim {var_locator}, {var_svc}, {var_method}, {var_inparams}, {var_outparams}, {var_result}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\default")
Set {var_method} = {var_svc}.Get("StdRegProv").Methods_("SetDWORDValue")
Set {var_inparams} = {var_method}.InParameters.SpawnInstance_()

{var_inparams}.hDefKey = {hive_const}
{var_inparams}.sSubKeyName = "{key_path}"
{var_inparams}.sValueName = "{value_name}"
{var_inparams}.uValue = {value_data}

Set {var_outparams} = {var_svc}.ExecMethod("StdRegProv", "SetDWORDValue", {var_inparams})
{var_result} = {var_outparams}.ReturnValue

Set {var_method} = Nothing
Set {var_inparams} = Nothing
Set {var_outparams} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
'''
        if self.config.hide_errors:
            vbs_code += "On Error GoTo 0\n"

        return vbs_code.strip()

    def write_registry_binary(self, hive: str, key_path: str, value_name: str,
                             hex_data: str) -> str:
        """
        Generate VBS code to write binary registry value via WMI

        Args:
            hive: Registry hive
            key_path: Full registry path
            value_name: Name of the binary value
            hex_data: Hex string of binary data (e.g., "48656C6C6F")

        Returns:
            VBS code for writing binary value
        """
        var_locator = self._get_or_create_var("locator", "bwrLoc")
        var_svc = self._get_or_create_var("service", "bwrSvc")
        var_method = self._get_or_create_var("method", "bwrMeth")
        var_inparams = self._get_or_create_var("inparams", "bwrIn")
        var_outparams = self._get_or_create_var("outparams", "bwrOut")
        var_result = self._get_or_create_var("result", "bwrRes")
        var_array = self._get_or_create_var("array", "binArray")
        var_i = self._get_or_create_var("i", "idx")

        hive_const = self._get_hive_constant(hive)

        error_handling = ""
        if self.config.hide_errors:
            error_handling = "On Error Resume Next\n"

        vbs_code = f'''
{error_handling}
Dim {var_locator}, {var_svc}, {var_method}, {var_inparams}, {var_outparams}, {var_result}
Dim {var_array}(), {var_i}, {self._get_or_create_var("hex_len", "hLen")}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\default")

' Convert hex string to byte array
Dim {self._get_or_create_var("hex_data", "hData")}
{self._get_or_create_var("hex_data")} = "{hex_data}"
{self._get_or_create_var("hex_len")} = Len({self._get_or_create_var("hex_data")}) / 2 - 1
ReDim {var_array}({self._get_or_create_var("hex_len")})

For {var_i} = 0 To {self._get_or_create_var("hex_len")}
    {var_array}({var_i}) = CLng("&H" & Mid({self._get_or_create_var("hex_data")}, {var_i} * 2 + 1, 2))
Next

Set {var_method} = {var_svc}.Get("StdRegProv").Methods_("SetBinaryValue")
Set {var_inparams} = {var_method}.InParameters.SpawnInstance_()

{var_inparams}.hDefKey = {hive_const}
{var_inparams}.sSubKeyName = "{key_path}"
{var_inparams}.sValueName = "{value_name}"
{var_inparams}.uValue = {var_array}

Set {var_outparams} = {var_svc}.ExecMethod("StdRegProv", "SetBinaryValue", {var_inparams})
{var_result} = {var_outparams}.ReturnValue

Set {var_method} = Nothing
Set {var_inparams} = Nothing
Set {var_outparams} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
'''
        if self.config.hide_errors:
            vbs_code += "On Error GoTo 0\n"

        return vbs_code.strip()

    def delete_registry_value(self, hive: str, key_path: str, value_name: str) -> str:
        """
        Generate VBS code to delete registry value via WMI

        Args:
            hive: Registry hive
            key_path: Full registry path
            value_name: Name of the value to delete

        Returns:
            VBS code for deleting registry value
        """
        var_locator = self._get_or_create_var("locator", "delLoc")
        var_svc = self._get_or_create_var("service", "delSvc")
        var_method = self._get_or_create_var("method", "delMeth")
        var_inparams = self._get_or_create_var("inparams", "delIn")
        var_outparams = self._get_or_create_var("outparams", "delOut")
        var_result = self._get_or_create_var("result", "delRes")

        hive_const = self._get_hive_constant(hive)

        error_handling = ""
        if self.config.hide_errors:
            error_handling = "On Error Resume Next\n"

        vbs_code = f'''
{error_handling}
Dim {var_locator}, {var_svc}, {var_method}, {var_inparams}, {var_outparams}, {var_result}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\default")
Set {var_method} = {var_svc}.Get("StdRegProv").Methods_("DeleteValue")
Set {var_inparams} = {var_method}.InParameters.SpawnInstance_()

{var_inparams}.hDefKey = {hive_const}
{var_inparams}.sSubKeyName = "{key_path}"
{var_inparams}.sValueName = "{value_name}"

Set {var_outparams} = {var_svc}.ExecMethod("StdRegProv", "DeleteValue", {var_inparams})
{var_result} = {var_outparams}.ReturnValue

Set {var_method} = Nothing
Set {var_inparams} = Nothing
Set {var_outparams} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
'''
        if self.config.hide_errors:
            vbs_code += "On Error GoTo 0\n"

        return vbs_code.strip()

    def enum_registry_keys(self, hive: str, key_path: str) -> str:
        """
        Generate VBS code to enumerate registry keys via WMI

        Args:
            hive: Registry hive
            key_path: Full registry path

        Returns:
            VBS code for enumerating registry keys
        """
        var_locator = self._get_or_create_var("locator", "enumLoc")
        var_svc = self._get_or_create_var("service", "enumSvc")
        var_method = self._get_or_create_var("method", "enumMeth")
        var_inparams = self._get_or_create_var("inparams", "enumIn")
        var_outparams = self._get_or_create_var("outparams", "enumOut")
        var_result = self._get_or_create_var("result", "enumRes")
        var_i = self._get_or_create_var("i", "idx")
        var_subkeys = self._get_or_create_var("subkeys", "sKeys")

        hive_const = self._get_hive_constant(hive)

        error_handling = ""
        if self.config.hide_errors:
            error_handling = "On Error Resume Next\n"

        vbs_code = f'''
{error_handling}
Dim {var_locator}, {var_svc}, {var_method}, {var_inparams}, {var_outparams}, {var_result}
Dim {var_i}, {var_subkeys}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\default")
Set {var_method} = {var_svc}.Get("StdRegProv").Methods_("EnumKey")
Set {var_inparams} = {var_method}.InParameters.SpawnInstance_()

{var_inparams}.hDefKey = {hive_const}
{var_inparams}.sSubKeyName = "{key_path}"

Set {var_outparams} = {var_svc}.ExecMethod("StdRegProv", "EnumKey", {var_inparams})

If {var_outparams}.ReturnValue = 0 Then
    {var_subkeys} = {var_outparams}.sNames
    If Not IsNull({var_subkeys}) Then
        For {var_i} = LBound({var_subkeys}) To UBound({var_subkeys})
            ' Process subkey: {var_subkeys}({var_i})
        Next
    End If
End If

Set {var_method} = Nothing
Set {var_inparams} = Nothing
Set {var_outparams} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
'''
        if self.config.hide_errors:
            vbs_code += "On Error GoTo 0\n"

        return vbs_code.strip()

    def enum_registry_values(self, hive: str, key_path: str) -> str:
        """
        Generate VBS code to enumerate registry values via WMI

        Args:
            hive: Registry hive
            key_path: Full registry path

        Returns:
            VBS code for enumerating registry values
        """
        var_locator = self._get_or_create_var("locator", "enumVLoc")
        var_svc = self._get_or_create_var("service", "enumVSvc")
        var_method = self._get_or_create_var("method", "enumVMeth")
        var_inparams = self._get_or_create_var("inparams", "enumVIn")
        var_outparams = self._get_or_create_var("outparams", "enumVOut")
        var_result = self._get_or_create_var("result", "enumVRes")
        var_i = self._get_or_create_var("i", "vidx")
        var_names = self._get_or_create_var("names", "vNames")
        var_types = self._get_or_create_var("types", "vTypes")

        hive_const = self._get_hive_constant(hive)

        error_handling = ""
        if self.config.hide_errors:
            error_handling = "On Error Resume Next\n"

        vbs_code = f'''
{error_handling}
Dim {var_locator}, {var_svc}, {var_method}, {var_inparams}, {var_outparams}, {var_result}
Dim {var_i}, {var_names}, {var_types}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\default")
Set {var_method} = {var_svc}.Get("StdRegProv").Methods_("EnumValues")
Set {var_inparams} = {var_method}.InParameters.SpawnInstance_()

{var_inparams}.hDefKey = {hive_const}
{var_inparams}.sSubKeyName = "{key_path}"

Set {var_outparams} = {var_svc}.ExecMethod("StdRegProv", "EnumValues", {var_inparams})

If {var_outparams}.ReturnValue = 0 Then
    {var_names} = {var_outparams}.sNames
    {var_types} = {var_outparams}.Types
    If Not IsNull({var_names}) Then
        For {var_i} = LBound({var_names}) To UBound({var_names})
            ' Process value: {var_names}({var_i}) with type {var_types}({var_i})
        Next
    End If
End If

Set {var_method} = Nothing
Set {var_inparams} = Nothing
Set {var_outparams} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
'''
        if self.config.hide_errors:
            vbs_code += "On Error GoTo 0\n"

        return vbs_code.strip()

    def create_registry_key(self, hive: str, key_path: str) -> str:
        """
        Generate VBS code to create registry key via WMI

        Args:
            hive: Registry hive
            key_path: Full registry path to create

        Returns:
            VBS code for creating registry key
        """
        var_locator = self._get_or_create_var("locator", "creLoc")
        var_svc = self._get_or_create_var("service", "creSvc")
        var_method = self._get_or_create_var("method", "creMeth")
        var_inparams = self._get_or_create_var("inparams", "creIn")
        var_outparams = self._get_or_create_var("outparams", "creOut")
        var_result = self._get_or_create_var("result", "creRes")

        hive_const = self._get_hive_constant(hive)

        error_handling = ""
        if self.config.hide_errors:
            error_handling = "On Error Resume Next\n"

        vbs_code = f'''
{error_handling}
Dim {var_locator}, {var_svc}, {var_method}, {var_inparams}, {var_outparams}, {var_result}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\default")
Set {var_method} = {var_svc}.Get("StdRegProv").Methods_("CreateKey")
Set {var_inparams} = {var_method}.InParameters.SpawnInstance_()

{var_inparams}.hDefKey = {hive_const}
{var_inparams}.sSubKeyName = "{key_path}"

Set {var_outparams} = {var_svc}.ExecMethod("StdRegProv", "CreateKey", {var_inparams})
{var_result} = {var_outparams}.ReturnValue

Set {var_method} = Nothing
Set {var_inparams} = Nothing
Set {var_outparams} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
'''
        if self.config.hide_errors:
            vbs_code += "On Error GoTo 0\n"

        return vbs_code.strip()

    def delete_registry_key(self, hive: str, key_path: str) -> str:
        """
        Generate VBS code to delete registry key via WMI

        Args:
            hive: Registry hive
            key_path: Full registry path to delete

        Returns:
            VBS code for deleting registry key
        """
        var_locator = self._get_or_create_var("locator", "delKeyLoc")
        var_svc = self._get_or_create_var("service", "delKeySvc")
        var_method = self._get_or_create_var("method", "delKeyMeth")
        var_inparams = self._get_or_create_var("inparams", "delKeyIn")
        var_outparams = self._get_or_create_var("outparams", "delKeyOut")
        var_result = self._get_or_create_var("result", "delKeyRes")

        hive_const = self._get_hive_constant(hive)

        error_handling = ""
        if self.config.hide_errors:
            error_handling = "On Error Resume Next\n"

        vbs_code = f'''
{error_handling}
Dim {var_locator}, {var_svc}, {var_method}, {var_inparams}, {var_outparams}, {var_result}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\default")
Set {var_method} = {var_svc}.Get("StdRegProv").Methods_("DeleteKey")
Set {var_inparams} = {var_method}.InParameters.SpawnInstance_()

{var_inparams}.hDefKey = {hive_const}
{var_inparams}.sSubKeyName = "{key_path}"

Set {var_outparams} = {var_svc}.ExecMethod("StdRegProv", "DeleteKey", {var_inparams})
{var_result} = {var_outparams}.ReturnValue

Set {var_method} = Nothing
Set {var_inparams} = Nothing
Set {var_outparams} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
'''
        if self.config.hide_errors:
            vbs_code += "On Error GoTo 0\n"

        return vbs_code.strip()

    def check_registry_key_exists(self, hive: str, key_path: str) -> str:
        """
        Generate VBS code to check if registry key exists via WMI

        Args:
            hive: Registry hive
            key_path: Full registry path

        Returns:
            VBS code for checking registry key existence
        """
        var_locator = self._get_or_create_var("locator", "exLoc")
        var_svc = self._get_or_create_var("service", "exSvc")
        var_exists = self._get_or_create_var("exists", "keyExists")
        var_query = self._get_or_create_var("query", "qry")

        hive_const = self._get_hive_constant(hive)

        error_handling = ""
        if self.config.hide_errors:
            error_handling = "On Error Resume Next\n"

        vbs_code = f'''
{error_handling}
Dim {var_locator}, {var_svc}, {var_exists}

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\default")

On Error Resume Next
{var_svc}.Get("StdRegProv").GetStringValue {hive_const}, "{key_path}", ""
If Err.Number = 0 Then
    {var_exists} = True
Else
    {var_exists} = False
End If
On Error GoTo 0

Set {var_svc} = Nothing
Set {var_locator} = Nothing
'''
        if self.config.hide_errors:
            vbs_code = error_handling + vbs_code[len(error_handling):]

        return vbs_code.strip()

    def get_registry_methods_report(self) -> Dict[str, Dict[str, str]]:
        """Generate report of all available registry access methods"""
        methods = {
            "read_value": {
                "name": "Read String Value",
                "description": "Read string value from registry",
                "code": self.read_registry_value("HKLM", "SOFTWARE", "TestValue")
            },
            "read_dword": {
                "name": "Read DWORD Value",
                "description": "Read DWORD value from registry",
                "code": self.read_registry_dword("HKLM", "SOFTWARE", "TestDWORD")
            },
            "read_binary": {
                "name": "Read Binary Value",
                "description": "Read binary value from registry",
                "code": self.read_registry_binary("HKLM", "SOFTWARE", "TestBinary")
            },
            "write_value": {
                "name": "Write String Value",
                "description": "Write string value to registry",
                "code": self.write_registry_value("HKCU", "SOFTWARE", "TestValue", "TestData")
            },
            "write_dword": {
                "name": "Write DWORD Value",
                "description": "Write DWORD value to registry",
                "code": self.write_registry_dword("HKCU", "SOFTWARE", "TestDWORD", 1)
            },
            "write_binary": {
                "name": "Write Binary Value",
                "description": "Write binary value to registry",
                "code": self.write_registry_binary("HKCU", "SOFTWARE", "TestBinary", "48656C6C6F")
            },
            "delete_value": {
                "name": "Delete Value",
                "description": "Delete registry value",
                "code": self.delete_registry_value("HKCU", "SOFTWARE", "TestValue")
            },
            "enum_keys": {
                "name": "Enumerate Keys",
                "description": "Enumerate registry keys",
                "code": self.enum_registry_keys("HKLM", "SOFTWARE")
            },
            "enum_values": {
                "name": "Enumerate Values",
                "description": "Enumerate registry values in a key",
                "code": self.enum_registry_values("HKLM", "SOFTWARE")
            },
            "create_key": {
                "name": "Create Key",
                "description": "Create registry key",
                "code": self.create_registry_key("HKCU", "SOFTWARE\\TestKey")
            },
            "delete_key": {
                "name": "Delete Key",
                "description": "Delete registry key",
                "code": self.delete_registry_key("HKCU", "SOFTWARE\\TestKey")
            },
            "check_exists": {
                "name": "Check Key Exists",
                "description": "Check if registry key exists",
                "code": self.check_registry_key_exists("HKLM", "SOFTWARE")
            }
        }
        return methods


def create_registry_accessor(config: Optional[RegistryConfig] = None) -> WMIRegistryAccess:
    """Factory function to create registry accessor with config"""
    return WMIRegistryAccess(config or RegistryConfig())


# High-level convenience functions
def read_registry(hive: str, key_path: str, value_name: str, value_type: str = "string") -> str:
    """
    High-level function to read registry value

    Args:
        hive: Registry hive (HKLM, HKCU, etc.)
        key_path: Full registry path
        value_name: Name of the value
        value_type: Type of value (string, dword, binary)

    Returns:
        VBS code for reading registry value
    """
    accessor = create_registry_accessor()

    if value_type.lower() == "dword":
        return accessor.read_registry_dword(hive, key_path, value_name)
    elif value_type.lower() == "binary":
        return accessor.read_registry_binary(hive, key_path, value_name)
    else:  # string
        return accessor.read_registry_value(hive, key_path, value_name)


def write_registry(hive: str, key_path: str, value_name: str, value_data: str,
                   value_type: str = "string") -> str:
    """
    High-level function to write registry value

    Args:
        hive: Registry hive
        key_path: Full registry path
        value_name: Name of the value
        value_data: Data to write
        value_type: Type of value (string, dword, binary)

    Returns:
        VBS code for writing registry value
    """
    accessor = create_registry_accessor()

    if value_type.lower() == "dword":
        return accessor.write_registry_dword(hive, key_path, value_name, int(value_data))
    elif value_type.lower() == "binary":
        return accessor.write_registry_binary(hive, key_path, value_name, value_data)
    else:  # string
        return accessor.write_registry_value(hive, key_path, value_name, value_data)


if __name__ == "__main__":
    print("=" * 80)
    print("WMI REGISTRY ACCESS - WbemScripting.SWbemLocator Registry Operations")
    print("=" * 80)

    accessor = create_registry_accessor()

    print("\n[1] Read String Value from HKLM")
    print("-" * 80)
    print(accessor.read_registry_value("HKLM", "SOFTWARE\\Microsoft\\Windows", "CurrentVersion"))

    print("\n[2] Read DWORD Value from HKCU")
    print("-" * 80)
    print(accessor.read_registry_dword("HKCU", "Software\\Microsoft\\Windows\\CurrentVersion", "Run"))

    print("\n[3] Write String Value to HKCU")
    print("-" * 80)
    print(accessor.write_registry_value("HKCU", "SOFTWARE\\Test", "TestValue", "Hello World"))

    print("\n[4] Write DWORD Value to HKCU")
    print("-" * 80)
    print(accessor.write_registry_dword("HKCU", "SOFTWARE\\Test", "TestDWORD", 12345))

    print("\n[5] Delete Registry Value")
    print("-" * 80)
    print(accessor.delete_registry_value("HKCU", "SOFTWARE\\Test", "TestValue"))

    print("\n[6] Enumerate Registry Keys")
    print("-" * 80)
    print(accessor.enum_registry_keys("HKLM", "SOFTWARE\\Microsoft"))

    print("\n[7] Enumerate Registry Values")
    print("-" * 80)
    print(accessor.enum_registry_values("HKLM", "SOFTWARE\\Microsoft\\Windows"))

    print("\n[8] Create Registry Key")
    print("-" * 80)
    print(accessor.create_registry_key("HKCU", "SOFTWARE\\MyApp"))

    print("\n[9] Delete Registry Key")
    print("-" * 80)
    print(accessor.delete_registry_key("HKCU", "SOFTWARE\\MyApp"))

    print("\n" + "=" * 80)
    print("Registry Access Methods Summary")
    print("=" * 80)
    report = accessor.get_registry_methods_report()
    for key, method_info in report.items():
        print(f"\n{method_info['name']}")
        print(f"  Description: {method_info['description']}")
