# COM Object Instantiation Variants Guide

## Overview

This guide documents the COM (Component Object Model) object instantiation variants implementation. It provides multiple methods to create and interact with COM objects, including various obfuscation and evasion techniques.

## Implementation Files

- **com_object_variants.py**: Core COM object variant generator
- **com_object_examples.py**: Comprehensive examples and demonstrations
- **COM_VARIANTS_GUIDE.md**: This documentation

## Core Instantiation Methods

### 1. CreateObject (ProgID)
Direct instantiation using the Programmatic Identifier (ProgID).

**Syntax:**
```vbscript
Set objExcel = CreateObject("Excel.Application")
```

**Characteristics:**
- Most common method
- Requires COM registration
- Works with or without type library reference
- Late binding (dynamic method resolution)

**When to use:**
- Standard application automation
- Excel, Word, PowerPoint instantiation
- WScript.Shell access

---

### 2. CreateObject (CLSID)
Direct instantiation using the Class Identifier (CLSID) GUID.

**Syntax:**
```vbscript
Set objExcel = CreateObject("CLSID:{00024500-0000-0000-C000-000000000046}")
```

**Characteristics:**
- Bypasses ProgID registry lookup
- Requires exact CLSID knowledge
- Slightly faster than ProgID
- More evasive (direct GUID reference)

**When to use:**
- Bypassing ProgID-based detection
- Obfuscation scenarios
- Hardcoded CLSID deployment

---

### 3. GetObject (Running Instance)
Retrieves an existing running COM object instance.

**Syntax:**
```vbscript
Set objExcel = GetObject(, "Excel.Application")
```

**Characteristics:**
- Only works if object already running
- Fails silently if not found
- Reuses existing process (efficiency)
- Less suspicious than CreateObject

**When to use:**
- Interacting with already-running applications
- Avoiding spawning new processes
- Stealth scenarios

---

### 4. GetObject (Moniker Path)
Retrieves COM object from file path using moniker binding.

**Syntax:**
```vbscript
Set objDoc = GetObject("C:\sample.doc")
```

**Characteristics:**
- Binds to file-based COM objects
- Automatically creates appropriate object type
- File must exist
- Useful for document automation

**When to use:**
- Word document access
- Excel spreadsheet access
- Compound document interaction

---

### 5. GetObject (WMI Moniker)
Retrieves WMI namespace using moniker binding.

**Syntax:**
```vbscript
Set objWMI = GetObject("winmgmts://./root/cimv2")
```

**Characteristics:**
- Direct WMI namespace access
- Bypasses SWbemLocator instantiation
- Moniker format: `winmgmts://[machine]/[namespace]`
- More direct than CreateObject method

**When to use:**
- Direct WMI access without locator
- Namespace switching
- Remote WMI connections

---

### 6. New Keyword
Direct instantiation using VBScript New keyword.

**Syntax:**
```vbscript
Set objExcel = New Excel.Application
```

**Characteristics:**
- Requires library reference
- Early binding (compile-time type checking)
- VB.NET/VBScript with imported type library
- Type-safe but less flexible

**When to use:**
- Script with library references
- Type-safe applications
- IDE with IntelliSense support

---

### 7. CreateObject (Remote DCOM)
Remote instantiation via DCOM (Distributed COM).

**Syntax:**
```vbscript
Set objExcel = CreateObject("Excel.Application", "192.168.1.100")
```

**Characteristics:**
- Requires DCOM-enabled remote machine
- Authentication required
- Slower due to network latency
- Cross-machine automation

**When to use:**
- Remote system automation
- Lateral movement
- Distributed task execution

---

### 8. WMI Class Instantiation
Instantiation via SWbemServices.Get() method.

**Syntax:**
```vbscript
Set objLocator = CreateObject("WbemScripting.SWbemLocator")
Set objServices = objLocator.ConnectServer(".", "root\cimv2")
Set objClass = objServices.Get("Win32_Process")
```

**Characteristics:**
- Retrieves WMI class definition
- Enables method invocation on WMI classes
- Supports namespace variation
- Complex but powerful

**When to use:**
- WMI method execution
- System information retrieval
- Process and service management

---

### 9. Registry Lookup
Dynamic CLSID resolution through registry queries.

**Syntax:**
```vbscript
Dim shell, clsid
Set shell = CreateObject("WScript.Shell")
clsid = shell.RegRead("HKCR\Excel.Application\CLSID\")
Set objExcel = CreateObject("CLSID:" & clsid)
```

**Characteristics:**
- Resolves ProgID to CLSID at runtime
- Flexible and dynamic
- Requires WScript.Shell access
- Adds complexity but improves evasion

**When to use:**
- Dynamic COM resolution
- Detection evasion
- Obfuscated payload generation

---

## Obfuscation Techniques

### Base64 Encoded ProgID
Encodes ProgID string in base64 with MSXML2 decoder.

**Method:**
```vbscript
Function DecodeBase64(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64 = node.NodeTypedValue
End Function

Set objShell = CreateObject(DecodeBase64("V1NjcmlwdC5TaGVsbA=="))
```

**Encoding Example:**
- Input: `WScript.Shell`
- Output: `V1NjcmlwdC5TaGVsbA==`

---

### Hex Encoded ProgID
Encodes ProgID string in hexadecimal.

**Method:**
```vbscript
Function DecodeHex(hexStr)
    Dim i, result
    For i = 1 To Len(hexStr) Step 2
        result = result & Chr("&H" & Mid(hexStr, i, 2))
    Next
    DecodeHex = result
End Function

Set objShell = CreateObject(DecodeHex("57536372697074..."))
```

---

### CLSID Registry Moniker
Uses moniker syntax with "new:" prefix for CLSID binding.

**Syntax:**
```vbscript
Set objShell = GetObject("new:{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}")
```

**Characteristics:**
- Registry-based CLSID lookup
- Moniker-based instantiation
- Evasive CLSID usage pattern

---

### Inline VBScript Class
Creates pseudo-COM object without external registration.

**Method:**
```vbscript
Class FakeComObject
    Public Sub Execute(cmd)
        ' Custom implementation
    End Sub
End Class

Set objFake = New FakeComObject
```

**Advantages:**
- No registry dependency
- Completely custom behavior
- Non-detectable as real COM object

---

## COM Objects Reference

### Office Applications
| ProgID | CLSID |
|--------|-------|
| Excel.Application | {00024500-0000-0000-C000-000000000046} |
| Word.Application | {000209FF-0000-0000-C000-000000000046} |
| PowerPoint.Application | {91493441-5A91-11CF-8700-00AA0060263B} |
| Access.Application | {73A4C9C1-D68D-11D0-98BF-00A0746B9C1B} |
| Outlook.Application | {0006F03A-0000-0000-C000-000000000046} |

### System Objects
| ProgID | CLSID |
|--------|-------|
| WScript.Shell | {F935DC22-1CF0-11D0-ADB9-00C04FD58A0B} |
| WScript.Network | {093FF999-1EA0-4F46-9A21-ECC5D57F0C6F} |
| Shell.Application | {13709620-C279-11CE-A49E-444553540000} |
| WbemScripting.SWbemLocator | {76A64158-CB41-11D1-8B02-00600806D9B6} |

### Data Access Objects
| ProgID | CLSID |
|--------|-------|
| ADODB.Connection | {00000514-0000-0010-8000-00AA006D2EA4} |
| ADODB.Recordset | {00000555-0000-0010-8000-00AA006D2EA4} |

### XML Objects
| ProgID | CLSID |
|--------|-------|
| MSXML2.DOMDocument | {F5078F32-C551-11D3-89B9-0000F81FE221} |

---

## WMI Namespaces

### Common WMI Namespaces
- `root\cimv2` - Core Management Information (standard)
- `root\WDM` - Windows Driver Model
- `root\dcim` - Data Center Infrastructure Management
- `root\hardware` - Hardware information
- `root\cimv1` - Legacy CIMv1 classes
- `root\default` - Default namespace

### Namespace Examples
```vbscript
' Local connection with namespace
Set objServices = objLocator.ConnectServer(".", "root\cimv2")

' Remote connection with namespace
Set objServices = objLocator.ConnectServer("192.168.1.100", "root\dcim")

' WMI moniker with namespace
Set objWMI = GetObject("winmgmts://./root/WDM")
```

---

## Error Handling Patterns

### Silent Error Suppression
```vbscript
On Error Resume Next
Set objExcel = CreateObject("Excel.Application")
If Err.Number = 0 And Not IsEmpty(objExcel) Then
    ' Success path
End If
On Error GoTo 0
```

### Cascading Fallback
```vbscript
Dim objExcel
On Error Resume Next
Set objExcel = CreateObject("Excel.Application")
If IsEmpty(objExcel) Then
    Set objExcel = CreateObject("Excel.Application.16")
End If
If IsEmpty(objExcel) Then
    Set objExcel = GetObject(, "Excel.Application")
End If
On Error GoTo 0
```

---

## Advanced Techniques

### Version-Specific Instantiation
Some COM objects support version suffixes:
```vbscript
Set objExcel = CreateObject("Excel.Application.1")  ' Version 1
Set objExcel = CreateObject("Excel.Application.16")  ' Excel 2016
```

### Multithreaded Apartment (MTA) Considerations
```vbscript
' COM objects have apartment models
Set objUnknown = objExcel  ' Retrieve IUnknown interface
' Can be marshalled across apartments
```

### Late Binding
No type library reference required:
```vbscript
Dim objExcel
Set objExcel = CreateObject("Excel.Application")
objExcel.Visible = True  ' Property access without compile-time checking
```

---

## Use Cases

### 1. Document Automation
```vbscript
Set objDoc = GetObject("C:\sample.docx")
objDoc.Selection.Font.Name = "Arial"
objDoc.Save
```

### 2. Process Execution via WMI
```vbscript
Set objLocator = CreateObject("WbemScripting.SWbemLocator")
Set objServices = objLocator.ConnectServer(".", "root\cimv2")
Set objProcess = objServices.Get("Win32_Process")
objProcess.Create "powershell.exe"
```

### 3. Registry Access
```vbscript
Set objShell = CreateObject("WScript.Shell")
strValue = objShell.RegRead("HKLM\Software\Microsoft\Windows\CurrentVersion\")
```

### 4. Remote System Access
```vbscript
Set objExcel = CreateObject("Excel.Application", "remote.company.com")
' Requires DCOM configuration
```

### 5. Encoded Payload Execution
```vbscript
Set objShell = CreateObject(DecodeBase64("V1NjcmlwdC5TaGVsbA=="))
objShell.Run "calc.exe"
```

---

## Detection Evasion

### Key Evasion Strategies

1. **CLSID Usage**: Use CLSID instead of ProgID to bypass string-based detection
2. **Encoding**: Encode ProgID/command strings in base64 or hex
3. **Registry Lookup**: Dynamically resolve CLSIDs through registry
4. **Moniker Binding**: Use alternative binding methods (GetObject with monikers)
5. **Inline Classes**: Create fake COM objects without registration
6. **Delayed Execution**: Use WScript.CreateObject with delayed instantiation
7. **Namespace Variation**: Use alternative WMI namespaces
8. **Version Variants**: Try multiple ProgID versions

---

## Performance Considerations

| Method | Speed | Memory | Notes |
|--------|-------|--------|-------|
| CreateObject (ProgID) | Medium | Medium | Standard, well-optimized |
| CreateObject (CLSID) | Slightly Faster | Medium | Skips registry lookup |
| GetObject (Running) | Fast | Low | Reuses existing process |
| GetObject (Moniker) | Medium | Medium | File system access required |
| New Keyword | Fast | Medium | Early binding only |
| Remote DCOM | Slow | High | Network latency |
| Registry Lookup | Slow | Low | Additional registry query |

---

## Security Implications

### Attack Surface
- COM object instantiation requires execution context
- Privilege level determines accessible COM objects
- Some objects require admin/SYSTEM context

### Detection Points
- Process creation (rundll32, wscript, cscript)
- Registry queries (HKCR, HKLM)
- Network traffic (DCOM remote calls)
- WMI activity monitoring
- COM object instantiation logging

### Mitigation
- Restrict COM object registration
- Monitor WMI activity
- Block script execution (PowerShell constrained mode)
- Disable DCOM for remote access
- Audit registry queries

---

## Testing and Verification

### Python Testing
```python
from com_object_variants import COMObjectVariantGenerator

gen = COMObjectVariantGenerator()
variants = gen.generate_all_variants()
for variant_id, variant_info in variants.items():
    print(f"{variant_id}: {variant_info['description']}")
```

### Running Examples
```bash
python3 com_object_examples.py
```

### Generate Reference
```bash
python3 com_object_variants.py --reference
```

---

## Summary

COM object instantiation provides multiple pathways for system access and automation. The variations in instantiation methods offer flexibility for legitimate automation while also enabling sophisticated evasion techniques. Understanding these methods is critical for both development and security analysis.

### Key Takeaways:
1. **CreateObject** remains the standard method but is easily detectable
2. **GetObject** provides stealth through object reuse
3. **CLSID** usage bypasses ProgID-based detection
4. **Encoding** and **Obfuscation** complicate analysis
5. **Registry Lookup** adds dynamic resolution layer
6. **WMI Integration** enables powerful system interaction
7. **Multiple Variants** ensure robustness across environments
