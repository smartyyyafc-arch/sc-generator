#!/usr/bin/env python3
"""
COM Object Instantiation Variants Generator
Creates COM execution payloads using different object instantiation methods:
- CreateObject: Direct instantiation from ProgID or CLSID
- GetObject: Retrieval of existing COM objects or files
- New: Direct class instantiation (VB.NET/VBScript)
- Alternative methods: moniker bindings, registry lookups, etc.
- Obfuscation techniques: encoded CLSIDs, registry paths, WMI class instantiation
"""

import base64
import random
import string
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class COMObjectConfig:
    """Configuration for COM object instantiation variants"""
    progid: str  # ProgID (e.g., "Excel.Application")
    clsid: Optional[str] = None  # CLSID (e.g., "{00024500-0000-0000-C000-000000000046}")
    method: str = "CreateObject"  # CreateObject, GetObject, New, Moniker, Registry
    use_error_handling: bool = True
    add_registry_bypass: bool = False
    use_encoding: bool = False
    encoding_type: str = "base64"  # base64, hex, xor
    use_delayed_execution: bool = False
    add_memory_tricks: bool = False


class COMObjectVariantGenerator:
    """Generates COM object instantiation variants"""

    # Common COM objects with ProgID and CLSID mappings
    COM_OBJECTS = {
        "Excel.Application": "{00024500-0000-0000-C000-000000000046}",
        "Word.Application": "{000209FF-0000-0000-C000-000000000046}",
        "PowerPoint.Application": "{91493441-5A91-11CF-8700-00AA0060263B}",
        "Access.Application": "{73A4C9C1-D68D-11D0-98BF-00A0746B9C1B}",
        "Outlook.Application": "{0006F03A-0000-0000-C000-000000000046}",
        "WbemScripting.SWbemLocator": "{76A64158-CB41-11D1-8B02-00600806D9B6}",
        "Shell.Application": "{13709620-C279-11CE-A49E-444553540000}",
        "InternetExplorer.Application": "{0002DF01-0000-0000-C000-000000000046}",
        "MSXML2.DOMDocument": "{F5078F32-C551-11D3-89B9-0000F81FE221}",
        "ADODB.Connection": "{00000514-0000-0010-8000-00AA006D2EA4}",
        "ADODB.Recordset": "{00000555-0000-0010-8000-00AA006D2EA4}",
        "WScript.Shell": "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}",
        "WScript.Network": "{093FF999-1EA0-4F46-9A21-ECC5D57F0C6F}",
    }

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

    def _encode_base64(self, text: str) -> str:
        """Encode text to base64"""
        return base64.b64encode(text.encode()).decode()

    def _encode_hex(self, text: str) -> str:
        """Encode text to hex"""
        return text.encode().hex()

    def generate_createobject_progid(self, progid: str, command: str = "calc.exe") -> str:
        """
        Direct CreateObject with ProgID
        Most common method for COM instantiation
        Example: CreateObject("Excel.Application")
        """
        var_obj = self._get_var("obj", "comObj")

        code = f'''Dim {var_obj}
On Error Resume Next
Set {var_obj} = CreateObject("{progid}")
If Not IsEmpty({var_obj}) Then
    ' Object created successfully
    ' Execute payload here
End If
On Error GoTo 0'''
        return code

    def generate_createobject_clsid(self, clsid: str, command: str = "calc.exe") -> str:
        """
        CreateObject with CLSID string
        Alternative to ProgID for direct class instantiation
        Format: CreateObject("CLSID", CLSID_STRING)
        """
        var_obj = self._get_var("obj", "clsidObj")

        code = f'''Dim {var_obj}
On Error Resume Next
Set {var_obj} = CreateObject("CLSID:{clsid}")
If Not IsEmpty({var_obj}) Then
    ' Object created from CLSID
End If
On Error GoTo 0'''
        return code

    def generate_getobject_progid(self, progid: str = "Excel.Application") -> str:
        """
        GetObject with ProgID
        Retrieves existing running COM object instance
        Fails silently if not already running
        """
        var_obj = self._get_var("obj", "getObj")

        code = f'''Dim {var_obj}
On Error Resume Next
Set {var_obj} = GetObject(, "{progid}")
If Err.Number = 0 And Not IsEmpty({var_obj}) Then
    ' Successfully retrieved running object
End If
On Error GoTo 0'''
        return code

    def generate_getobject_monikerpath(self, moniker_path: str) -> str:
        """
        GetObject with moniker path binding
        Creates COM object from file path or moniker URL
        Example: GetObject("C:\\file.doc", "Word.Document")
        """
        var_obj = self._get_var("obj", "monikerObj")

        code = f'''Dim {var_obj}
On Error Resume Next
Set {var_obj} = GetObject("{moniker_path}")
If Not IsEmpty({var_obj}) Then
    ' Object retrieved from path
End If
On Error GoTo 0'''
        return code

    def generate_getobject_winmgmts(self, namespace: str = "root\\cimv2") -> str:
        """
        GetObject with WMI moniker binding
        Binds to WMI namespace directly using moniker
        Format: winmgmts://./root/cimv2
        """
        var_obj = self._get_var("obj", "wmiObj")
        moniker = f"winmgmts://./{ namespace.replace(chr(92), '/')}"

        code = f'''Dim {var_obj}
On Error Resume Next
Set {var_obj} = GetObject("{moniker}")
If Not IsEmpty({var_obj}) Then
    ' WMI namespace retrieved
End If
On Error GoTo 0'''
        return code

    def generate_new_keyword(self, progid: str) -> str:
        """
        New keyword for direct instantiation
        Only works with referenced libraries or early-bound objects
        VB.NET/VBScript with library reference
        """
        var_obj = self._get_var("obj", "newObj")

        code = f'''Dim {var_obj} As Object
' Requires library reference to "{progid}"
On Error Resume Next
Set {var_obj} = New {progid.split('.')[0]}
If Not IsEmpty({var_obj}) Then
    ' Object created with New keyword
End If
On Error GoTo 0'''
        return code

    def generate_createobject_with_machine(self, progid: str, machine: str = ".") -> str:
        """
        CreateObject with machine name (DCOM)
        Enables remote COM object instantiation
        """
        var_obj = self._get_var("obj", "remoteObj")

        code = f'''Dim {var_obj}
On Error Resume Next
Set {var_obj} = CreateObject("{progid}", "{machine}")
If Not IsEmpty({var_obj}) Then
    ' Remote object created via DCOM
End If
On Error GoTo 0'''
        return code

    def generate_wmi_class_instantiation(self, wmi_class: str = "Win32_Process", namespace: str = "root\\cimv2") -> str:
        """
        WMI class instantiation through SWbemServices.Get
        Retrieves WMI class definition for manipulation
        """
        var_loc = self._get_var("loc", "wmiLoc")
        var_svc = self._get_var("svc", "wmiSvc")
        var_cls = self._get_var("cls", "wmiCls")

        code = f'''Dim {var_loc}, {var_svc}, {var_cls}
On Error Resume Next
Set {var_loc} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_loc}.ConnectServer(".", "{namespace}")
Set {var_cls} = {var_svc}.Get("{wmi_class}")
If Not IsEmpty({var_cls}) Then
    ' WMI class retrieved
End If
On Error GoTo 0'''
        return code

    def generate_registry_lookup_progid(self, progid: str = "Excel.Application") -> str:
        """
        Registry lookup to resolve ProgID to CLSID
        Bypasses normal COM registration checks
        """
        var_shell = self._get_var("shell", "regShell")
        var_key = self._get_var("key", "regKey")
        var_obj = self._get_var("obj", "regObj")

        code = f'''Dim {var_shell}, {var_key}, {var_obj}
On Error Resume Next
Set {var_shell} = CreateObject("WScript.Shell")
{var_key} = {var_shell}.RegRead("HKCR\\\\{progid}\\\\CLSID\\\\")
Set {var_obj} = CreateObject("CLSID:" & {var_key})
If Not IsEmpty({var_obj}) Then
    ' Object created from registry-resolved CLSID
End If
On Error GoTo 0'''
        return code

    def generate_encoded_progid_createobject(self, progid: str, encoding_type: str = "base64") -> str:
        """
        CreateObject with encoded ProgID
        Obfuscates the ProgID string through encoding
        """
        if encoding_type == "base64":
            encoded = self._encode_base64(progid)
            decoder_func = "DecodeBase64"
            decode_code = f'''Function {decoder_func}(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    {decoder_func} = node.NodeTypedValue
End Function'''
        else:  # hex
            encoded = self._encode_hex(progid)
            decoder_func = "DecodeHex"
            decode_code = f'''Function {decoder_func}(hexStr)
    Dim i, result
    For i = 1 To Len(hexStr) Step 2
        result = result & Chr("&H" & Mid(hexStr, i, 2))
    Next
    {decoder_func} = result
End Function'''

        var_obj = self._get_var("obj", "encObj")
        var_progid = self._get_var("progid", "decProgID")

        code = f'''{decode_code}

Dim {var_obj}, {var_progid}
On Error Resume Next
{var_progid} = {decoder_func}("{encoded}")
Set {var_obj} = CreateObject({var_progid})
If Not IsEmpty({var_obj}) Then
    ' Object created from encoded ProgID
End If
On Error GoTo 0'''
        return code

    def generate_rundll_com_instantiation(self, dll_path: str = "shell32.dll", entry: str = "ShellExecute") -> str:
        """
        COM object instantiation through rundll32
        Indirect method using DLL exports
        """
        var_shell = self._get_var("shell", "dllShell")
        var_cmd = self._get_var("cmd", "dllCmd")

        code = f'''Dim {var_shell}, {var_cmd}
On Error Resume Next
Set {var_shell} = CreateObject("WScript.Shell")
{var_cmd} = "rundll32.exe {dll_path} {entry}"
{var_shell}.Run {var_cmd}
On Error GoTo 0'''
        return code

    def generate_inline_vbscript_class(self, class_name: str = "ComObject") -> str:
        """
        Inline VBScript class definition mimicking COM object
        Creates pseudo-COM object without registration
        """
        var_obj = self._get_var("obj", "inlineObj")

        code = f'''Class {class_name}
    Public Property Get Version
        Version = "1.0"
    End Property

    Public Sub ExecuteCommand(cmd)
        Dim shell
        Set shell = CreateObject("WScript.Shell")
        shell.Run cmd
        Set shell = Nothing
    End Sub
End Class

Dim {var_obj}
Set {var_obj} = New {class_name}
If Not IsEmpty({var_obj}) Then
    ' Inline class object created
End If'''
        return code

    def generate_activex_control_progid(self, progid: str = "Forms.CommandButton.1") -> str:
        """
        ActiveX control instantiation through ProgID
        Creates windowed or windowless ActiveX controls
        """
        var_obj = self._get_var("obj", "axCtrl")

        code = f'''Dim {var_obj}
On Error Resume Next
Set {var_obj} = CreateObject("{progid}")
If Not IsEmpty({var_obj}) Then
    ' ActiveX control created
    ' Can access control properties and methods
End If
On Error GoTo 0'''
        return code

    def generate_ole_embedding_moniker(self, file_path: str = "C:\\sample.xlsx") -> str:
        """
        OLE embedding moniker for compound document access
        Retrieves embedded objects from documents
        """
        var_obj = self._get_var("obj", "oleObj")

        code = f'''Dim {var_obj}
On Error Resume Next
Set {var_obj} = GetObject("{file_path}")
If Not IsEmpty({var_obj}) Then
    ' OLE embedded object retrieved
End If
On Error GoTo 0'''
        return code

    def generate_multithreaded_apartment_com(self, progid: str) -> str:
        """
        COM object instantiation with MTA consideration
        Uses CreateObject with apartment model awareness
        """
        var_obj = self._get_var("obj", "mtaObj")
        var_unknown = self._get_var("unk", "comUnknown")

        code = f'''Dim {var_obj}, {var_unknown}
On Error Resume Next
Set {var_obj} = CreateObject("{progid}")
If Not IsEmpty({var_obj}) Then
    ' Get IUnknown interface
    Set {var_unknown} = {var_obj}
    ' Object can be used across apartments
End If
On Error GoTo 0'''
        return code

    def generate_late_binding_createobject(self, progid: str) -> str:
        """
        Late binding COM object creation
        No type library reference required
        Most flexible and evasive method
        """
        var_obj = self._get_var("obj", "lateObj")

        code = f'''Dim {var_obj}
On Error Resume Next
Set {var_obj} = CreateObject("{progid}")
If Not IsEmpty({var_obj}) Then
    ' Late-bound object - no type checking
    ' Can dynamically call any method/property
End If
On Error GoTo 0'''
        return code

    def generate_clsid_registry_moniker(self, clsid: str) -> str:
        """
        CLSID-based registry moniker binding
        Resolves CLSID through registry bindings
        """
        var_obj = self._get_var("obj", "clsidReg")

        code = f'''Dim {var_obj}
On Error Resume Next
Set {var_obj} = GetObject("new:{clsid}")
If Not IsEmpty({var_obj}) Then
    ' Object created from CLSID registry lookup
End If
On Error GoTo 0'''
        return code

    def generate_progid_version_variants(self, base_progid: str) -> List[str]:
        """
        Generate multiple versions of ProgID
        Handles version-specific object instantiation
        """
        variants = []
        for version in range(1, 20):  # Common versions 1-20
            progid_variant = f"{base_progid}.{version}"
            var_obj = self._get_var("obj", f"v{version}")
            code = f'''Dim {var_obj}
On Error Resume Next
Set {var_obj} = CreateObject("{progid_variant}")
If Not IsEmpty({var_obj}) Then
    ' Version {version} object created
End If
On Error GoTo 0'''
            variants.append({
                "version": version,
                "progid": progid_variant,
                "code": code
            })
        return variants

    def generate_all_variants(self) -> Dict[str, Dict]:
        """Generate all available COM object instantiation variants"""
        variants = {
            "createobject_progid": {
                "description": "Direct CreateObject with ProgID",
                "category": "basic",
                "code": self.generate_createobject_progid("Excel.Application")
            },
            "createobject_clsid": {
                "description": "CreateObject with explicit CLSID",
                "category": "basic",
                "code": self.generate_createobject_clsid("{00024500-0000-0000-C000-000000000046}")
            },
            "getobject_running": {
                "description": "GetObject to retrieve running instance",
                "category": "retrieval",
                "code": self.generate_getobject_progid("Excel.Application")
            },
            "getobject_moniker": {
                "description": "GetObject with moniker path binding",
                "category": "retrieval",
                "code": self.generate_getobject_monikerpath("C:\\sample.doc")
            },
            "getobject_winmgmts": {
                "description": "GetObject with WMI moniker binding",
                "category": "wmi",
                "code": self.generate_getobject_winmgmts("root\\cimv2")
            },
            "new_keyword": {
                "description": "New keyword for direct instantiation",
                "category": "basic",
                "code": self.generate_new_keyword("Excel.Application")
            },
            "createobject_remote": {
                "description": "CreateObject with remote machine (DCOM)",
                "category": "remote",
                "code": self.generate_createobject_with_machine("Excel.Application", "192.168.1.100")
            },
            "wmi_class_instantiation": {
                "description": "WMI class instantiation via SWbemServices",
                "category": "wmi",
                "code": self.generate_wmi_class_instantiation("Win32_Process")
            },
            "registry_lookup": {
                "description": "Registry lookup to resolve ProgID",
                "category": "registry",
                "code": self.generate_registry_lookup_progid("Excel.Application")
            },
            "encoded_progid_base64": {
                "description": "CreateObject with base64 encoded ProgID",
                "category": "obfuscation",
                "code": self.generate_encoded_progid_createobject("Excel.Application", "base64")
            },
            "encoded_progid_hex": {
                "description": "CreateObject with hex encoded ProgID",
                "category": "obfuscation",
                "code": self.generate_encoded_progid_createobject("WScript.Shell", "hex")
            },
            "rundll_com": {
                "description": "COM instantiation through rundll32",
                "category": "indirect",
                "code": self.generate_rundll_com_instantiation("shell32.dll", "ShellExecute")
            },
            "inline_vbscript_class": {
                "description": "Inline VBScript class mimicking COM",
                "category": "evasion",
                "code": self.generate_inline_vbscript_class("ComObject")
            },
            "activex_control": {
                "description": "ActiveX control instantiation",
                "category": "activex",
                "code": self.generate_activex_control_progid("Forms.CommandButton.1")
            },
            "ole_embedding": {
                "description": "OLE embedding moniker for documents",
                "category": "ole",
                "code": self.generate_ole_embedding_moniker("C:\\sample.xlsx")
            },
            "mta_aware": {
                "description": "COM object with MTA awareness",
                "category": "threading",
                "code": self.generate_multithreaded_apartment_com("Excel.Application")
            },
            "late_binding": {
                "description": "Late binding COM object creation",
                "category": "basic",
                "code": self.generate_late_binding_createobject("WScript.Shell")
            },
            "clsid_registry_moniker": {
                "description": "CLSID registry moniker binding",
                "category": "registry",
                "code": self.generate_clsid_registry_moniker("{00024500-0000-0000-C000-000000000046}")
            }
        }
        return variants

    def generate_excel_com_variants(self) -> Dict[str, Dict]:
        """Generate Excel-specific COM object variants"""
        excel_clsid = self.COM_OBJECTS["Excel.Application"]

        variants = {
            "excel_createobject": {
                "description": "Excel via CreateObject ProgID",
                "application": "Excel",
                "code": self.generate_createobject_progid("Excel.Application")
            },
            "excel_clsid": {
                "description": "Excel via direct CLSID",
                "application": "Excel",
                "code": self.generate_createobject_clsid(excel_clsid)
            },
            "excel_getobject": {
                "description": "Excel via GetObject running instance",
                "application": "Excel",
                "code": self.generate_getobject_progid("Excel.Application")
            },
            "excel_version_variants": {
                "description": "Excel version-specific instantiation",
                "application": "Excel",
                "code": "# Multiple versions available through progid versions"
            }
        }
        return variants


def generate_com_variants_report() -> str:
    """Generate comprehensive report of all COM object instantiation variants"""
    gen = COMObjectVariantGenerator()
    variants = gen.generate_all_variants()

    report = "=" * 90 + "\n"
    report += "COM OBJECT INSTANTIATION VARIANTS\n"
    report += "=" * 90 + "\n\n"

    # Group by category
    categories = {}
    for variant_id, variant_info in variants.items():
        category = variant_info.get("category", "other")
        if category not in categories:
            categories[category] = []
        categories[category].append((variant_id, variant_info))

    for category in sorted(categories.keys()):
        report += f"\n{'=' * 90}\n"
        report += f"CATEGORY: {category.upper()}\n"
        report += f"{'=' * 90}\n\n"

        for variant_id, variant_info in categories[category]:
            report += f"[{variant_id.upper()}]\n"
            report += f"Description: {variant_info['description']}\n"
            report += f"{'-' * 90}\n"
            report += f"{variant_info['code']}\n"
            report += f"\n{'-' * 90}\n\n"

    return report


def generate_com_objects_reference() -> str:
    """Generate reference of common COM objects with ProgID and CLSID"""
    gen = COMObjectVariantGenerator()

    ref = "=" * 100 + "\n"
    ref += "COMMON COM OBJECTS REFERENCE\n"
    ref += "=" * 100 + "\n\n"

    ref += f"{'ProgID':<40} {'CLSID':<50}\n"
    ref += "-" * 100 + "\n"

    for progid, clsid in sorted(gen.COM_OBJECTS.items()):
        ref += f"{progid:<40} {clsid:<50}\n"

    ref += "\n" + "=" * 100 + "\n"
    return ref


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--reference":
        print(generate_com_objects_reference())
    else:
        report = generate_com_variants_report()
        print(report)
