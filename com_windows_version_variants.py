#!/usr/bin/env python3
"""
Windows Version-Specific COM Object Variants Generator
Creates COM execution payloads optimized for different Windows versions:
- Windows XP (5.1) - Legacy COM support
- Windows Vista (6.0) - Enhanced security model
- Windows 7 (6.1) - Improved COM stability
- Windows 8 (6.2) - Metro/Modern app integration
- Windows 10 (10.0) - Universal Windows Platform
- Windows 11 (10.0.22000+) - Latest security features

Handles version-specific:
- API availability and compatibility
- Security context (UAC, integrity levels)
- Registry paths and locations
- COM object availability
- Performance optimizations
"""

import base64
import random
import string
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class WindowsVersion(Enum):
    """Windows version identifiers"""
    XP = "5.1"
    VISTA = "6.0"
    WIN7 = "6.1"
    WIN8 = "6.2"
    WIN10 = "10.0"
    WIN11 = "10.0.22000"


@dataclass
class WindowsVersionInfo:
    """Detailed Windows version information"""
    name: str
    version_number: str
    build_number: int
    kernel_version: str
    uac_supported: bool
    appdata_folders: Dict[str, str]
    registry_paths: Dict[str, str]
    available_com_objects: List[str]
    security_features: List[str]
    deprecation_warnings: List[str]


class WindowsVersionSpecificCOMVariants:
    """Generates Windows version-specific COM variants"""

    # Windows version information database
    VERSION_INFO = {
        WindowsVersion.XP: WindowsVersionInfo(
            name="Windows XP",
            version_number="5.1",
            build_number=2600,
            kernel_version="5.1",
            uac_supported=False,
            appdata_folders={
                "user": "C:\\Documents and Settings\\%USERNAME%\\Application Data",
                "all_users": "C:\\Documents and Settings\\All Users\\Application Data",
                "temp": "C:\\Documents and Settings\\%USERNAME%\\Local Settings\\Temp",
            },
            registry_paths={
                "com_objects": "HKCR\\CLSID",
                "file_associations": "HKCR\\",
                "windows_run": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            },
            available_com_objects=[
                "Excel.Application",
                "Word.Application",
                "PowerPoint.Application",
                "WScript.Shell",
                "WScript.Network",
                "MSXML2.DOMDocument",
                "ADODB.Connection",
                "WbemScripting.SWbemLocator",
            ],
            security_features=[
                "DEP (Data Execution Prevention)",
                "Windows Firewall (Limited)",
            ],
            deprecation_warnings=[
                "No ASLR support",
                "Limited UAC protections",
                "Older WMI security model",
            ]
        ),
        WindowsVersion.VISTA: WindowsVersionInfo(
            name="Windows Vista",
            version_number="6.0",
            build_number=6000,
            kernel_version="6.0",
            uac_supported=True,
            appdata_folders={
                "user": "C:\\Users\\%USERNAME%\\AppData\\Roaming",
                "local": "C:\\Users\\%USERNAME%\\AppData\\Local",
                "temp": "C:\\Users\\%USERNAME%\\AppData\\Local\\Temp",
                "all_users": "C:\\ProgramData",
            },
            registry_paths={
                "com_objects": "HKCR\\CLSID",
                "appdata": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders",
                "windows_run": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                "machine_run": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            },
            available_com_objects=[
                "Excel.Application",
                "Word.Application",
                "PowerPoint.Application",
                "WScript.Shell",
                "WScript.Network",
                "MSXML2.DOMDocument",
                "ADODB.Connection",
                "WbemScripting.SWbemLocator",
                "Shell.Application",
            ],
            security_features=[
                "UAC (User Account Control)",
                "ASLR (Address Space Layout Randomization)",
                "DEP/NX",
                "Mandatory Integrity Control",
                "Enhanced WMI security",
            ],
            deprecation_warnings=[
                "Some legacy COM objects may require elevation",
                "Registry virtualization active for non-elevated processes",
            ]
        ),
        WindowsVersion.WIN7: WindowsVersionInfo(
            name="Windows 7",
            version_number="6.1",
            build_number=7600,
            kernel_version="6.1",
            uac_supported=True,
            appdata_folders={
                "user": "C:\\Users\\%USERNAME%\\AppData\\Roaming",
                "local": "C:\\Users\\%USERNAME%\\AppData\\Local",
                "temp": "C:\\Users\\%USERNAME%\\AppData\\Local\\Temp",
                "all_users": "C:\\ProgramData",
            },
            registry_paths={
                "com_objects": "HKCR\\CLSID",
                "appdata": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders",
                "windows_run": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                "machine_run": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            },
            available_com_objects=[
                "Excel.Application",
                "Word.Application",
                "PowerPoint.Application",
                "Access.Application",
                "Outlook.Application",
                "WScript.Shell",
                "WScript.Network",
                "MSXML2.DOMDocument",
                "ADODB.Connection",
                "WbemScripting.SWbemLocator",
                "Shell.Application",
                "InternetExplorer.Application",
            ],
            security_features=[
                "UAC",
                "ASLR",
                "DEP/NX",
                "Mandatory Integrity Control",
                "Enhanced WMI security",
                "Code Integrity (CI)",
            ],
            deprecation_warnings=[
                "Internet Explorer 8/9 legacy",
                "Older .NET Framework versions",
            ]
        ),
        WindowsVersion.WIN8: WindowsVersionInfo(
            name="Windows 8",
            version_number="6.2",
            build_number=9200,
            kernel_version="6.2",
            uac_supported=True,
            appdata_folders={
                "user": "C:\\Users\\%USERNAME%\\AppData\\Roaming",
                "local": "C:\\Users\\%USERNAME%\\AppData\\Local",
                "temp": "C:\\Users\\%USERNAME%\\AppData\\Local\\Temp",
                "all_users": "C:\\ProgramData",
            },
            registry_paths={
                "com_objects": "HKCR\\CLSID",
                "appdata": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders",
                "windows_run": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                "machine_run": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            },
            available_com_objects=[
                "Excel.Application",
                "Word.Application",
                "PowerPoint.Application",
                "Access.Application",
                "Outlook.Application",
                "WScript.Shell",
                "WScript.Network",
                "MSXML2.DOMDocument",
                "ADODB.Connection",
                "WbemScripting.SWbemLocator",
                "Shell.Application",
                "InternetExplorer.Application",
            ],
            security_features=[
                "UAC",
                "ASLR",
                "DEP/NX",
                "Mandatory Integrity Control",
                "Enhanced WMI security",
                "Code Integrity (CI)",
                "AppContainer isolation",
                "Metro app sandboxing",
            ],
            deprecation_warnings=[
                "Desktop/Modern app boundary",
                "WinRT COM interop complexity",
                "Legacy DirectX COM reduced support",
            ]
        ),
        WindowsVersion.WIN10: WindowsVersionInfo(
            name="Windows 10",
            version_number="10.0",
            build_number=19045,
            kernel_version="10.0",
            uac_supported=True,
            appdata_folders={
                "user": "C:\\Users\\%USERNAME%\\AppData\\Roaming",
                "local": "C:\\Users\\%USERNAME%\\AppData\\Local",
                "temp": "C:\\Users\\%USERNAME%\\AppData\\Local\\Temp",
                "all_users": "C:\\ProgramData",
            },
            registry_paths={
                "com_objects": "HKCR\\CLSID",
                "appdata": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders",
                "windows_run": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                "machine_run": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            },
            available_com_objects=[
                "Excel.Application",
                "Word.Application",
                "PowerPoint.Application",
                "Access.Application",
                "Outlook.Application",
                "WScript.Shell",
                "WScript.Network",
                "MSXML2.DOMDocument",
                "ADODB.Connection",
                "WbemScripting.SWbemLocator",
                "Shell.Application",
                "InternetExplorer.Application",
                "Microsoft.Update.AutoUpdate",
            ],
            security_features=[
                "UAC",
                "ASLR",
                "DEP/NX",
                "Mandatory Integrity Control",
                "Enhanced WMI security",
                "Code Integrity (CI)",
                "AppContainer isolation",
                "Virtualization-based security (VBS)",
                "Credential Guard (Enterprise)",
                "Windows Defender integration",
            ],
            deprecation_warnings=[
                "Internet Explorer phased out",
                "Flash removed",
                "Legacy .NET Framework versions",
                "WMI v1 reduced support",
            ]
        ),
        WindowsVersion.WIN11: WindowsVersionInfo(
            name="Windows 11",
            version_number="10.0.22000",
            build_number=22000,
            kernel_version="10.0",
            uac_supported=True,
            appdata_folders={
                "user": "C:\\Users\\%USERNAME%\\AppData\\Roaming",
                "local": "C:\\Users\\%USERNAME%\\AppData\\Local",
                "temp": "C:\\Users\\%USERNAME%\\AppData\\Local\\Temp",
                "all_users": "C:\\ProgramData",
            },
            registry_paths={
                "com_objects": "HKCR\\CLSID",
                "appdata": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders",
                "windows_run": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                "machine_run": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            },
            available_com_objects=[
                "Excel.Application",
                "Word.Application",
                "PowerPoint.Application",
                "Access.Application",
                "Outlook.Application",
                "WScript.Shell",
                "WScript.Network",
                "MSXML2.DOMDocument",
                "ADODB.Connection",
                "WbemScripting.SWbemLocator",
                "Shell.Application",
                "Microsoft.Update.AutoUpdate",
                "Windows.System.Launcher",
            ],
            security_features=[
                "UAC",
                "ASLR",
                "DEP/NX",
                "Mandatory Integrity Control",
                "Enhanced WMI security",
                "Code Integrity (CI)",
                "AppContainer isolation",
                "Virtualization-based security (VBS) - Default",
                "Credential Guard - Default",
                "Windows Defender - Integrated",
                "Signed drivers requirement",
                "Kernel-mode code signing",
                "Secure Boot requirement",
                "UEFI firmware",
            ],
            deprecation_warnings=[
                "Flash removed",
                "WMI v1 legacy functions deprecated",
                "32-bit app support limited",
                "Internet Explorer fully removed",
                "Legacy DirectX COM reduced support",
                "VBScript in Group Policy removed",
            ]
        ),
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

    def _get_version_info(self, version: WindowsVersion) -> WindowsVersionInfo:
        """Get version information"""
        return self.VERSION_INFO.get(version)

    def generate_version_check_code(self, target_version: WindowsVersion) -> str:
        """Generate VBScript code to check Windows version at runtime"""
        var_os = self._get_var("os", "osObj")
        var_version = self._get_var("version", "osVer")
        var_major = self._get_var("major", "osMajor")
        var_minor = self._get_var("minor", "osMinor")

        version_info = self._get_version_info(target_version)
        version_parts = version_info.version_number.split('.')
        target_major = version_parts[0]
        target_minor = version_parts[1] if len(version_parts) > 1 else "0"

        code = f'''Function GetWindowsVersion()
    Dim {var_os}, {var_version}
    On Error Resume Next
    Set {var_os} = GetObject("winmgmts:").ExecQuery("select * from Win32_OperatingSystem")
    Dim item
    For Each item In {var_os}
        {var_version} = item.Version
    Next
    GetWindowsVersion = {var_version}
End Function

Function CheckWindowsVersion()
    Dim {var_version}, {var_major}, {var_minor}
    {var_version} = GetWindowsVersion()
    If InStr({var_version}, ".") > 0 Then
        {var_major} = CLng(Left({var_version}, InStr({var_version}, ".") - 1))
        {var_minor} = CLng(Mid({var_version}, InStr({var_version}, ".") + 1))

        ' Check for {version_info.name} (v{version_info.version_number})
        If {var_major} = {target_major} And {var_minor} >= {target_minor} Then
            CheckWindowsVersion = True
        Else
            CheckWindowsVersion = False
        End If
    End If
End Function

If CheckWindowsVersion() Then
    ' Version check passed - {version_info.name} detected
Else
    ' Version mismatch - consider fallback
End If'''
        return code

    def generate_uac_aware_variant(self, version: WindowsVersion, com_object: str) -> str:
        """Generate UAC-aware COM object instantiation"""
        version_info = self._get_version_info(version)
        var_obj = self._get_var("obj", "uacObj")
        var_shell = self._get_var("shell", "shellObj")

        if not version_info.uac_supported:
            # XP doesn't have UAC
            code = f'''Dim {var_obj}
On Error Resume Next
Set {var_obj} = CreateObject("{com_object}")
If Not IsEmpty({var_obj}) Then
    ' {version_info.name} - No UAC security context
End If
On Error GoTo 0'''
        else:
            # Vista and later with UAC
            code = f'''Dim {var_obj}, {var_shell}
On Error Resume Next
Set {var_shell} = CreateObject("WScript.Shell")
Dim isAdmin, isMedium
isMedium = True ' Default assumption

On Error Resume Next
Set {var_obj} = CreateObject("{com_object}")

If Not IsEmpty({var_obj}) Then
    ' {version_info.name} - UAC context detected
    ' Running in {"Medium" if version != WindowsVersion.XP else "No UAC"} integrity level
    ' Some COM objects require elevation to High integrity
End If

On Error GoTo 0'''

        return code

    def generate_registry_path_variant(self, version: WindowsVersion, registry_location: str) -> str:
        """Generate version-specific registry path access"""
        version_info = self._get_version_info(version)
        var_shell = self._get_var("shell", "regShell")
        var_path = self._get_var("path", "regPath")
        var_value = self._get_var("value", "regValue")

        # Map registry location names to actual paths
        reg_paths = version_info.registry_paths.get(registry_location, "HKCR\\CLSID")

        code = f'''Dim {var_shell}, {var_path}, {var_value}
On Error Resume Next

Set {var_shell} = CreateObject("WScript.Shell")
{var_path} = "{reg_paths}"

' {version_info.name} registry access
' AppData path: {version_info.appdata_folders.get("user", "N/A")}

On Error Resume Next
{var_value} = {var_shell}.RegRead({var_path})

If Err.Number = 0 Then
    ' Registry value found - {version_info.name} registry accessible
Else
    ' Registry access denied - May require elevation
End If

On Error GoTo 0'''
        return code

    def generate_appdata_folder_variant(self, version: WindowsVersion, folder_type: str = "user") -> str:
        """Generate version-specific AppData folder paths"""
        version_info = self._get_version_info(version)
        var_shell = self._get_var("shell", "folderShell")
        var_path = self._get_var("path", "folderPath")
        var_fso = self._get_var("fso", "fileSystem")

        folder_path = version_info.appdata_folders.get(folder_type, "C:\\ProgramData")

        code = f'''Dim {var_shell}, {var_fso}, {var_path}
On Error Resume Next

Set {var_shell} = CreateObject("WScript.Shell")
Set {var_fso} = CreateObject("Scripting.FileSystemObject")

' {version_info.name} - {folder_type} AppData path
{var_path} = "{folder_path}"

' Expand environment variables
If InStr({var_path}, "%") > 0 Then
    {var_path} = {var_shell}.ExpandEnvironmentStrings({var_path})
End If

' Check if folder exists
If {var_fso}.FolderExists({var_path}) Then
    ' AppData folder accessible: {folder_path}
Else
    ' AppData folder not found - May need creation
End If

On Error GoTo 0'''
        return code

    def generate_com_availability_check(self, version: WindowsVersion, com_object: str) -> str:
        """Generate version-specific COM object availability check"""
        version_info = self._get_version_info(version)
        var_obj = self._get_var("obj", "checkObj")
        available = com_object in version_info.available_com_objects

        code = f'''Function IsCOMObjectAvailable(progid)
    Dim {var_obj}
    On Error Resume Next
    Set {var_obj} = CreateObject(progid)
    If Err.Number = 0 And Not IsEmpty({var_obj}) Then
        IsCOMObjectAvailable = True
    Else
        IsCOMObjectAvailable = False
    End If
    On Error GoTo 0
End Function

' {version_info.name} COM availability
' {com_object}: {"Available" if available else "May not be available - requires installation"}

If IsCOMObjectAvailable("{com_object}") Then
    ' {com_object} is available on {version_info.name}
Else
    ' {com_object} not available - fallback required
End If'''
        return code

    def generate_security_features_aware_code(self, version: WindowsVersion, com_object: str) -> str:
        """Generate code aware of version-specific security features"""
        version_info = self._get_version_info(version)
        var_obj = self._get_var("obj", "secObj")

        security_notes = "\n    ' ".join(version_info.security_features)

        code = f'''Dim {var_obj}
On Error Resume Next

' {version_info.name} Security Features:
' {security_notes}

Set {var_obj} = CreateObject("{com_object}")

If Err.Number = 0 Then
    ' COM object created successfully
    ' Security context: {", ".join(version_info.security_features[:2]) if version_info.security_features else "Minimal"}
Else
    ' COM instantiation failed - likely due to:
    ' {"UAC denial" if version_info.uac_supported else "Permission denied"}
    ' Security policy restrictions
End If

On Error GoTo 0'''
        return code

    def generate_fallback_cascade(self, versions: List[WindowsVersion], com_object: str) -> str:
        """Generate COM instantiation with fallback cascade across Windows versions"""
        var_obj = self._get_var("obj", "cascadeObj")
        var_success = self._get_var("success", "created")

        code = f'''Dim {var_obj}, {var_success}
{var_success} = False

' Fallback cascade for {com_object} across Windows versions
'''

        for i, version in enumerate(versions):
            version_info = self._get_version_info(version)
            if i > 0:
                code += f"\nIf Not {var_success} Then\n"
            code += f'''    On Error Resume Next
    Set {var_obj} = CreateObject("{com_object}")
    If Err.Number = 0 And Not IsEmpty({var_obj}) Then
        {var_success} = True
        ' {version_info.name} - Object instantiated successfully
    End If
    On Error GoTo 0
'''

        code += f'''
If {var_success} Then
    ' COM object instantiated on compatible version
Else
    ' COM object instantiation failed on all versions
End If'''
        return code

    def generate_version_optimized_variant(self, version: WindowsVersion, com_object: str,
                                          optimization_type: str = "performance") -> str:
        """Generate version-optimized COM instantiation"""
        version_info = self._get_version_info(version)
        var_obj = self._get_var("obj", "optObj")

        if optimization_type == "performance":
            # XP and 7 can be more direct, 8+ needs more careful handling
            if version == WindowsVersion.XP:
                code = f'''Dim {var_obj}
On Error Resume Next
' {version_info.name} - Optimized for performance (minimal security overhead)
Set {var_obj} = CreateObject("{com_object}")
If Not IsEmpty({var_obj}) Then
    ' Object ready for use
End If
On Error GoTo 0'''
            elif version in [WindowsVersion.WIN10, WindowsVersion.WIN11]:
                code = f'''Dim {var_obj}
On Error Resume Next
' {version_info.name} - Optimized for security-first performance
Set {var_obj} = CreateObject("{com_object}")
If Err.Number = 0 And Not IsEmpty({var_obj}) Then
    ' Object created with security contexts enforced
End If
On Error GoTo 0'''
            else:
                code = f'''Dim {var_obj}
On Error Resume Next
' {version_info.name} - Balanced performance and security
Set {var_obj} = CreateObject("{com_object}")
If Not IsEmpty({var_obj}) Then
    ' Object ready
End If
On Error GoTo 0'''

        elif optimization_type == "stealth":
            security_features_str = ', '.join(version_info.security_features[:2])
            code = f'''Dim {var_obj}
On Error Resume Next
' {version_info.name} - Stealth mode
' Minimize detection across {security_features_str}
Set {var_obj} = CreateObject("{com_object}")
If Not IsEmpty({var_obj}) Then
    ' Silent execution
End If
On Error GoTo 0'''

        else:  # compatibility
            code = f'''Dim {var_obj}
On Error Resume Next
' {version_info.name} - Maximum compatibility
' Handles: {", ".join(version_info.available_com_objects[:3])}...
Set {var_obj} = CreateObject("{com_object}")
If Not IsEmpty({var_obj}) Then
    ' Compatible mode
End If
On Error GoTo 0'''

        return code

    def generate_version_summary_report(self) -> str:
        """Generate summary report of all Windows versions and COM support"""
        report = "=" * 120 + "\n"
        report += "WINDOWS VERSION-SPECIFIC COM OBJECT VARIANTS REPORT\n"
        report += "=" * 120 + "\n\n"

        for version in [WindowsVersion.XP, WindowsVersion.VISTA, WindowsVersion.WIN7,
                       WindowsVersion.WIN8, WindowsVersion.WIN10, WindowsVersion.WIN11]:
            info = self.VERSION_INFO[version]
            report += f"\n[{info.name.upper()} - v{info.version_number}]\n"
            report += "-" * 120 + "\n"
            report += f"Build: {info.build_number}\n"
            report += f"Kernel: {info.kernel_version}\n"
            report += f"UAC Supported: {'Yes' if info.uac_supported else 'No'}\n"
            report += f"\nAppData Paths:\n"
            for key, path in info.appdata_folders.items():
                report += f"  {key}: {path}\n"
            report += f"\nSecurity Features:\n"
            for feature in info.security_features:
                report += f"  + {feature}\n"
            report += f"\nAvailable COM Objects ({len(info.available_com_objects)}):\n"
            for obj in info.available_com_objects[:5]:
                report += f"  - {obj}\n"
            if len(info.available_com_objects) > 5:
                report += f"  ... and {len(info.available_com_objects) - 5} more\n"
            if info.deprecation_warnings:
                report += f"\nDeprecation Warnings:\n"
                for warning in info.deprecation_warnings:
                    report += f"  ! {warning}\n"
            report += "\n"

        return report

    def generate_all_variants_for_version(self, version: WindowsVersion) -> Dict[str, Dict]:
        """Generate all COM variants optimized for a specific Windows version"""
        version_info = self._get_version_info(version)

        variants = {
            "version_check": {
                "description": f"Version detection for {version_info.name}",
                "code": self.generate_version_check_code(version)
            },
            "uac_aware": {
                "description": f"UAC-aware COM instantiation for {version_info.name}",
                "code": self.generate_uac_aware_variant(version, "WScript.Shell")
            },
            "registry_access": {
                "description": f"Registry path access for {version_info.name}",
                "code": self.generate_registry_path_variant(version, "com_objects")
            },
            "appdata_access": {
                "description": f"AppData folder access for {version_info.name}",
                "code": self.generate_appdata_folder_variant(version, "user")
            },
            "com_availability": {
                "description": f"COM object availability check for {version_info.name}",
                "code": self.generate_com_availability_check(version, "Excel.Application")
            },
            "security_aware": {
                "description": f"Security-aware COM instantiation for {version_info.name}",
                "code": self.generate_security_features_aware_code(version, "WScript.Shell")
            },
            "performance_optimized": {
                "description": f"Performance-optimized variant for {version_info.name}",
                "code": self.generate_version_optimized_variant(version, "Excel.Application", "performance")
            },
            "stealth_mode": {
                "description": f"Stealth execution variant for {version_info.name}",
                "code": self.generate_version_optimized_variant(version, "WScript.Shell", "stealth")
            },
            "compatibility_mode": {
                "description": f"Maximum compatibility variant for {version_info.name}",
                "code": self.generate_version_optimized_variant(version, "Shell.Application", "compatibility")
            }
        }

        return variants


def generate_comprehensive_windows_variants_report() -> str:
    """Generate comprehensive report with all Windows version variants"""
    gen = WindowsVersionSpecificCOMVariants()

    report = gen.generate_version_summary_report()
    report += "\n\n" + "=" * 120 + "\n"
    report += "DETAILED VARIANT EXAMPLES BY VERSION\n"
    report += "=" * 120 + "\n"

    for version in [WindowsVersion.XP, WindowsVersion.VISTA, WindowsVersion.WIN7,
                   WindowsVersion.WIN8, WindowsVersion.WIN10, WindowsVersion.WIN11]:
        info = gen.VERSION_INFO[version]
        report += f"\n{'=' * 120}\n"
        report += f"{info.name.upper()}\n"
        report += f"{'=' * 120}\n\n"

        variants = gen.generate_all_variants_for_version(version)
        for variant_id, variant_info in variants.items():
            report += f"[{variant_id.upper()}]\n"
            report += f"Description: {variant_info['description']}\n"
            report += "-" * 120 + "\n"
            report += variant_info['code'] + "\n"
            report += "-" * 120 + "\n\n"

    return report


def generate_version_comparison_matrix() -> str:
    """Generate feature comparison matrix across Windows versions"""
    gen = WindowsVersionSpecificCOMVariants()

    matrix = "=" * 150 + "\n"
    matrix += "WINDOWS VERSION FEATURE COMPARISON MATRIX\n"
    matrix += "=" * 150 + "\n\n"

    # Header
    versions = [WindowsVersion.XP, WindowsVersion.VISTA, WindowsVersion.WIN7,
               WindowsVersion.WIN8, WindowsVersion.WIN10, WindowsVersion.WIN11]
    version_names = [gen.VERSION_INFO[v].name for v in versions]

    matrix += f"{'Feature':<30} " + "".join([f"{name:^18}" for name in version_names]) + "\n"
    matrix += "-" * 150 + "\n"

    # UAC Support
    matrix += f"{'UAC Support':<30} "
    for v in versions:
        matrix += f"{'Yes' if gen.VERSION_INFO[v].uac_supported else 'No':<18} "
    matrix += "\n"

    # Security Features Count
    matrix += f"{'Security Features':<30} "
    for v in versions:
        matrix += f"{len(gen.VERSION_INFO[v].security_features):<18} "
    matrix += "\n"

    # COM Objects Count
    matrix += f"{'Available COM Objects':<30} "
    for v in versions:
        matrix += f"{len(gen.VERSION_INFO[v].available_com_objects):<18} "
    matrix += "\n"

    # ASLR Support
    matrix += f"{'ASLR Support':<30} "
    aslr_support = [False, True, True, True, True, True]
    for support in aslr_support:
        matrix += f"{'Yes' if support else 'No':<18} "
    matrix += "\n"

    # DEP/NX Support
    matrix += f"{'DEP/NX Support':<30} "
    dep_support = [True, True, True, True, True, True]
    for support in dep_support:
        matrix += f"{'Yes' if support else 'No':<18} "
    matrix += "\n"

    # Code Integrity
    matrix += f"{'Code Integrity':<30} "
    ci_support = [False, False, True, True, True, True]
    for support in ci_support:
        matrix += f"{'Yes' if support else 'No':<18} "
    matrix += "\n"

    # VBS Support
    matrix += f"{'VBScript Support':<30} "
    vbs_support = [True, True, True, True, True, False]
    for support in vbs_support:
        matrix += f"{'Full' if support else 'Limited':<18} "
    matrix += "\n"

    matrix += "\n" + "=" * 150 + "\n"
    return matrix


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--matrix":
            print(generate_version_comparison_matrix())
        elif sys.argv[1] == "--full":
            print(generate_comprehensive_windows_variants_report())
        elif sys.argv[1].startswith("--version="):
            version_name = sys.argv[1].split("=")[1].upper()
            try:
                version = WindowsVersion[version_name]
                gen = WindowsVersionSpecificCOMVariants()
                variants = gen.generate_all_variants_for_version(version)
                print(f"Variants for {gen.VERSION_INFO[version].name}:\n")
                for variant_id, variant_info in variants.items():
                    print(f"\n[{variant_id.upper()}]")
                    print(f"Description: {variant_info['description']}\n")
                    print(variant_info['code'])
                    print("-" * 80 + "\n")
            except KeyError:
                print(f"Unknown version: {version_name}")
                print(f"Available versions: {', '.join([v.name for v in WindowsVersion])}")
        else:
            print("Usage:")
            print("  python com_windows_version_variants.py              # Summary report")
            print("  python com_windows_version_variants.py --full      # Full detailed report")
            print("  python com_windows_version_variants.py --matrix    # Feature matrix")
            print("  python com_windows_version_variants.py --version=WIN10  # Specific version")
    else:
        print(generate_comprehensive_windows_variants_report()[:5000])  # Print first 5000 chars
