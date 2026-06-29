# Windows Version-Specific COM Object Variants Guide

## Overview

The `com_windows_version_variants.py` module provides comprehensive COM object instantiation variants optimized for different Windows versions. It handles version-specific differences in:

- **Security Models**: UAC, ASLR, DEP/NX, Integrity Levels
- **Registry Paths**: Different AppData locations across versions
- **COM Object Availability**: Version-dependent COM objects
- **API Compatibility**: APIs available in each version
- **Performance Characteristics**: Version-specific optimizations

## Supported Windows Versions

| Version | Number | Release Year | Status |
|---------|--------|--------------|--------|
| Windows XP | 5.1 | 2001 | Legacy (No UAC) |
| Windows Vista | 6.0 | 2006 | Legacy (UAC Introduction) |
| Windows 7 | 6.1 | 2009 | Legacy (Stable) |
| Windows 8 | 6.2 | 2012 | Legacy (Metro Era) |
| Windows 10 | 10.0 | 2015 | Active (LTS) |
| Windows 11 | 10.0.22000+ | 2021 | Current (Latest) |

## Key Features

### 1. Version Detection
Automatically detects target Windows version and generates appropriate code:

```python
gen = WindowsVersionSpecificCOMVariants()
version_check = gen.generate_version_check_code(WindowsVersion.WIN10)
```

**Output**: VBScript code that detects Windows version at runtime

### 2. UAC-Aware Variants
Handles User Account Control differences:

- **Windows XP**: No UAC, direct access
- **Windows Vista-11**: UAC-aware instantiation with integrity level checking

```python
uac_code = gen.generate_uac_aware_variant(WindowsVersion.WIN7, "Excel.Application")
```

### 3. Registry Path Variants
Version-specific registry paths for:

- COM object registration (HKCR\CLSID)
- AppData location registry entries
- Windows Run keys (HKCU, HKLM)

```python
registry_code = gen.generate_registry_path_variant(WindowsVersion.WIN10, "com_objects")
```

### 4. AppData Folder Handling
Automatic handling of version-specific AppData paths:

| Version | AppData Path |
|---------|--------------|
| XP | `C:\Documents and Settings\%USERNAME%\Application Data` |
| Vista+ | `C:\Users\%USERNAME%\AppData\Roaming` |

```python
appdata_code = gen.generate_appdata_folder_variant(WindowsVersion.WIN7, "user")
```

### 5. COM Object Availability Checking
Validates COM object availability on specific versions:

```python
availability_check = gen.generate_com_availability_check(WindowsVersion.WIN11, "Excel.Application")
```

### 6. Security Features Awareness
Documents security features enforced on each version:

```python
security_code = gen.generate_security_features_aware_code(WindowsVersion.WIN11, "WScript.Shell")
```

### 7. Fallback Cascades
Creates fallback chains across multiple Windows versions:

```python
versions = [WindowsVersion.WIN7, WindowsVersion.WIN10, WindowsVersion.WIN11]
cascade = gen.generate_fallback_cascade(versions, "Excel.Application")
```

### 8. Version-Optimized Variants
Three optimization strategies:

- **Performance**: Minimal overhead (XP optimized)
- **Stealth**: Minimize detection signatures
- **Compatibility**: Maximum cross-version support

```python
perf_code = gen.generate_version_optimized_variant(
    WindowsVersion.WIN10, 
    "Excel.Application", 
    "performance"
)
```

## Version Information Database

Each Windows version includes:

```python
@dataclass
class WindowsVersionInfo:
    name: str                              # Display name
    version_number: str                    # OS version (e.g., "6.1")
    build_number: int                      # Build number (e.g., 7600)
    kernel_version: str                    # Kernel version
    uac_supported: bool                    # UAC availability
    appdata_folders: Dict[str, str]        # Folder paths
    registry_paths: Dict[str, str]         # Registry paths
    available_com_objects: List[str]       # Available COM objects
    security_features: List[str]           # Security features
    deprecation_warnings: List[str]        # Deprecated APIs
```

## Detailed Version Characteristics

### Windows XP (5.1)
- **No UAC** - Direct access to system resources
- **No ASLR** - Predictable memory layout
- **Limited Security** - Basic DEP support only
- **AppData**: `Documents and Settings\%USERNAME%\Application Data`
- **Common COM Objects**: Excel, Word, WScript.Shell, MSXML2
- **Deprecation**: Legacy, many modern APIs unavailable

### Windows Vista (6.0)
- **UAC Introduction** - User Account Control enforced
- **ASLR Support** - Address Space Layout Randomization
- **Enhanced Security** - Mandatory Integrity Control
- **AppData**: `Users\%USERNAME%\AppData\Roaming`
- **COM Objects**: Vista-era applications
- **Deprecation**: Some legacy COM objects limited

### Windows 7 (6.1)
- **UAC Refined** - Improved from Vista
- **ASLR/DEP** - Full support
- **Code Integrity** - Kernel integrity checking
- **AppData**: Standard Users folder structure
- **COM Objects**: Most Office applications fully supported
- **Stability**: Most stable pre-Windows 10 version

### Windows 8 (6.2)
- **Modern/Desktop Boundary** - App model split
- **AppContainer** - Isolation for Metro apps
- **COM Objects**: Some restrictions for Store apps
- **Security**: Enhanced, AppContainer sandboxing
- **Legacy**: Desktop COM largely unchanged

### Windows 10 (10.0)
- **Virtualization-Based Security** - Available (not default)
- **Credential Guard** - Enterprise credential protection
- **Windows Defender** - Integrated security
- **COM Objects**: Comprehensive support, IE phased out
- **VBScript**: Still supported but deprecated
- **Security**: Enhanced over Vista/7

### Windows 11 (10.0.22000+)
- **VBS Default** - Virtualization-based security default
- **Signed Drivers** - Strict driver signing
- **Secure Boot** - UEFI firmware requirement
- **COM Objects**: Limited legacy support
- **VBScript Removal**: Removed from Group Policy
- **Security**: Highest security posture, most restrictions
- **Deprecation**: Flash, IE fully removed

## Common COM Objects by Version

### Universal Across All Versions
- `WScript.Shell` - Script host shell interface
- `WScript.Network` - Network operations
- `MSXML2.DOMDocument` - XML processing
- `WbemScripting.SWbemLocator` - WMI access
- `Shell.Application` - Shell operations

### Office Applications (If Installed)
- `Excel.Application` - Excel automation
- `Word.Application` - Word automation
- `PowerPoint.Application` - PowerPoint automation
- `Access.Application` - Access automation (Win7+)
- `Outlook.Application` - Outlook automation

### Database Access
- `ADODB.Connection` - Database connections
- `ADODB.Recordset` - Database recordsets

### Platform-Specific
- `InternetExplorer.Application` - IE automation (Win7, Win10)
- `Windows.System.Launcher` - Win11 modern app launching

## Security Features Progression

| Feature | XP | Vista | 7 | 8 | 10 | 11 |
|---------|----|----|---|----|----|----|
| DEP/NX | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| ASLR | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| UAC | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Code Integrity | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ |
| AppContainer | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| VBS (Default) | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |

## Usage Patterns

### Pattern 1: Version-Specific Code Generation
```python
gen = WindowsVersionSpecificCOMVariants()

# Generate code for specific version
win10_code = gen.generate_uac_aware_variant(WindowsVersion.WIN10, "Excel.Application")
print(win10_code)
```

### Pattern 2: Get All Variants for Version
```python
variants = gen.generate_all_variants_for_version(WindowsVersion.WIN7)

for variant_id, variant_info in variants.items():
    print(f"[{variant_id}] - {variant_info['description']}")
    print(variant_info['code'])
```

### Pattern 3: Multi-Version Fallback
```python
# Try newer versions first, fallback to older
versions = [WindowsVersion.WIN11, WindowsVersion.WIN10, WindowsVersion.WIN7]
cascade_code = gen.generate_fallback_cascade(versions, "Excel.Application")
```

### Pattern 4: Registry Access with Version Awareness
```python
# Get version-specific registry path
code = gen.generate_registry_path_variant(WindowsVersion.WIN10, "appdata")
```

### Pattern 5: Security-Aware Instantiation
```python
# Generate code aware of version security features
code = gen.generate_security_features_aware_code(WindowsVersion.WIN11, "WScript.Shell")
```

### Pattern 6: Version Detection + Conditional Execution
```python
version_check = gen.generate_version_check_code(WindowsVersion.WIN10)
# Wrap COM instantiation based on version check
```

## Generated Code Characteristics

### Standard Structure
All generated VBScript code includes:

1. **Error Handling**: `On Error Resume Next` / `On Error GoTo 0`
2. **Null Checks**: `If Not IsEmpty(obj) Then`
3. **Variable Declaration**: `Dim var_name`
4. **Comments**: Version and feature notes

### Example Generated Code (Windows 7)
```vbscript
Dim vObj_AbCdEf
On Error Resume Next
' Windows 7 - UAC context detected
Set vObj_AbCdEf = CreateObject("Excel.Application")
If Not IsEmpty(vObj_AbCdEf) Then
    ' Object created successfully
    ' Running in Medium integrity level
End If
On Error GoTo 0
```

## Best Practices

### 1. Always Check Availability
```python
availability = gen.generate_com_availability_check(version, com_object)
```

### 2. Use Fallback Cascades
```python
versions = [WindowsVersion.WIN11, WindowsVersion.WIN10, WindowsVersion.WIN7]
code = gen.generate_fallback_cascade(versions, "Excel.Application")
```

### 3. Handle Registry Virtualization (Vista+)
```python
# Non-elevated processes get virtualized registry access
registry_code = gen.generate_registry_path_variant(version, "com_objects")
```

### 4. Respect UAC on Vista and Later
```python
uac_code = gen.generate_uac_aware_variant(version, "Excel.Application")
```

### 5. Use Version-Optimized Variants
```python
# Choose optimization based on context
code = gen.generate_version_optimized_variant(
    version, 
    com_object, 
    optimization_type  # "performance", "stealth", "compatibility"
)
```

## Comparison Matrix

Use the comparison matrix to understand feature availability:

```python
matrix = generate_version_comparison_matrix()
print(matrix)
```

This shows:
- UAC Support
- Security Features Count
- Available COM Objects
- ASLR Support
- DEP/NX Support
- Code Integrity
- VBScript Support

## Testing

Comprehensive test suite validates:

- Version information completeness
- Version progression
- Variant generation
- Error handling
- Code quality
- Feature matrices

Run tests:
```bash
python test_com_windows_version_variants.py
```

## Example Usage Scripts

See `com_windows_version_examples.py` for 14 detailed examples:

1. Simple version detection
2. UAC-aware instantiation
3. Registry paths by version
4. AppData folder handling
5. COM object availability
6. Security features awareness
7. Fallback cascades
8. Version-optimized variants
9. Complete variant sets
10. Feature comparison matrix
11. XP-specific handling
12. Win11 advanced security
13. Multi-version strategy
14. Programmatic version selection

## Performance Considerations

- **XP/Vista**: Minimal overhead, direct access
- **Win7**: Balanced security and performance
- **Win8**: Additional isolation overhead
- **Win10/11**: Enhanced security at performance cost

## Security Considerations

- **Elevation Requirements**: Some COM objects require admin/high integrity
- **Whitelisting**: Win11 has more restrictive whitelists
- **Registry Virtualization**: Non-elevated access redirected on Vista+
- **AppContainer**: Metro/Modern apps have restricted COM access
- **Credential Guard**: Win10+ enterprise feature affects COM operations

## Deprecation Timeline

### Windows XP (End of Life)
- No longer actively developed
- Used only for legacy system support
- Full support in this module

### Windows Vista-7 (Extended Support Ending)
- Legacy but still widely used
- Partial deprecation for newer features
- Full compatibility support

### Windows 8 (Mainstream Support Ended)
- Limited support recommended
- App model complexity
- Basic COM support maintained

### Windows 10 (LTS Until 2025)
- Active support continues
- Comprehensive COM support
- Modern security features

### Windows 11 (Current)
- Latest features and security
- VBScript limited/removed
- Most restrictive COM access

## Integration with Other Modules

- `com_object_variants.py`: General COM variants (complements version variants)
- `com_polymorphic_loader.py`: Polymorphic COM loading
- `wmi_locator_variants.py`: WMI-specific implementations

## References

- [Windows OS Version History](https://docs.microsoft.com/en-us/windows/release-health/release-information)
- [COM and DCOM](https://docs.microsoft.com/en-us/windows/win32/com/component-object-model--com-)
- [User Account Control](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/)
- [Windows Security Features](https://docs.microsoft.com/en-us/windows/security/threat-protection/)

## Troubleshooting

### COM Object Not Available
- Check `available_com_objects` list for version
- Try fallback cascade to older versions
- Verify application installation

### Registry Access Denied
- Non-elevated process on Vista+ has virtualized registry
- Use fallback registry paths
- Check UAC integrity level

### VBScript Execution Issues
- Win11 removed VBScript Group Policy support
- Use fallback execution methods
- Consider PowerShell alternatives

### Integrity Level Problems
- Check `security_features` for UAC/Integrity Control
- Medium integrity may limit COM objects
- Use elevation if required

## License

Part of sc-generator project. See project LICENSE for details.
