# COM Polymorphic Loader - Reference Card

## Quick Reference

### Import Statement
```python
from com_polymorphic_loader import (
    COMPolymorphicLoader,
    COMPolymorphicCodeGenerator,
    COMObjectType,
    ICOMObject
)
```

---

## Core Classes

### COMPolymorphicLoader

**Initialization**:
```python
loader = COMPolymorphicLoader()
```

**Key Methods**:

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `load_object()` | `object_type`, `**kwargs` | `ICOMObject` | Load and cache COM object |
| `generate_polymorphic_code()` | `object_type`, `method`, `*args`, `fallback=True`, `use_error_handling=True` | `str` | Generate VBScript code |
| `get_object_metadata()` | `object_type` | `COMObjectMetadata` | Get object metadata |
| `get_fallback_chain()` | `object_type` | `List[COMObjectType]` | Get fallback objects |
| `list_available_objects()` | | `List[str]` | List all available objects |
| `generate_all_variants()` | | `Dict` | Get all variants as dict |
| `export_to_json()` | | `str` | Export configuration as JSON |

### COMPolymorphicCodeGenerator

**Initialization**:
```python
gen = COMPolymorphicCodeGenerator()
```

**Key Methods**:

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `generate_command_executor()` | `command` | `str` | Generate command execution code |
| `generate_wmi_query_executor()` | `query`, `namespace="root\\cimv2"` | `str` | Generate WMI query code |
| `generate_registry_reader()` | `reg_path` | `str` | Generate registry read code |
| `generate_file_operations()` | `operation`, `filepath` | `str` | Generate file operation code |
| `export_library()` | `output_format="json"` | `str` | Export library configuration |

### ICOMObject (Abstract Interface)

All COM objects implement:

```python
class ICOMObject(ABC):
    def get_progid(self) -> str                                    # ProgID
    def get_clsid(self) -> Optional[str]                          # CLSID
    def get_instantiation_code(self) -> str                        # Creation code
    def get_execution_code(self, method: str, *args) -> str       # Execution code
    def get_object_type(self) -> COMObjectType                     # Type
    def get_method_signature(self) -> Dict[str, List[str]]         # Methods
```

---

## Concrete Implementations

### ShellCOMObject (WScript.Shell)

**Creation**:
```python
shell = ShellCOMObject(use_remote=False, remote_machine=".")
shell = loader.load_object(COMObjectType.SHELL)
```

**Properties**:
- ProgID: `WScript.Shell`
- CLSID: `{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}`
- Supports Remote: Yes

**Methods**:
- `Run(command, windowStyle, waitOnReturn)`
- `Exec(command)`
- `RegRead(path)`
- `RegWrite(path, value)`
- `RegDelete(path)`
- `CreateShortcut(path)`
- `ExpandEnvironmentStrings(string)`
- `Popup(text, seconds, title, type)`

**Example**:
```python
code = shell.get_execution_code("Run", "calc.exe")
# or via loader
code = loader.generate_polymorphic_code(COMObjectType.SHELL, "Run", "calc.exe")
```

### WMILocatorCOMObject (WbemScripting.SWbemLocator)

**Creation**:
```python
wmi = WMILocatorCOMObject(namespace="root\\cimv2", use_remote=False)
wmi = loader.load_object(COMObjectType.WMI_LOCATOR)
```

**Properties**:
- ProgID: `WbemScripting.SWbemLocator`
- CLSID: `{76A64158-CB41-11D1-8B02-00600806D9B6}`
- Supports Remote: Yes

**Methods**:
- `ConnectServer(server, namespace)`
- `Get(className)`
- `ExecQuery(query)`
- `Create(className)`
- `InstancesOf(className)`
- `SubclassesOf(className)`

**Example**:
```python
code = wmi.get_execution_code("ExecQuery", "SELECT * FROM Win32_Process")
```

### ExcelCOMObject (Excel.Application)

**Creation**:
```python
excel = ExcelCOMObject(version=0)  # 0 for latest
excel = loader.load_object(COMObjectType.EXCEL, version=16)
```

**Properties**:
- ProgID: `Excel.Application` or `Excel.Application.16`
- CLSID: `{00024500-0000-0000-C000-000000000046}`
- Supports Remote: No

**Methods**:
- `Workbooks.Open(filename, updateLinks)`
- `Run(macroName)`
- `Quit()`
- `ActiveWorkbook`
- `ActiveSheet`

**Example**:
```python
code = excel.get_execution_code("Open", "C:\\file.xlsx")
```

### MSXMLCOMObject (MSXML2.DOMDocument)

**Creation**:
```python
msxml = MSXMLCOMObject(version=6)
msxml = loader.load_object(COMObjectType.MSXML, version=6)
```

**Properties**:
- ProgID: `MSXML2.DOMDocument.6.0`
- CLSID: `{F5078F32-C551-11D3-89B9-0000F81FE221}`
- Supports Remote: No

**Methods**:
- `Load(filename)`
- `LoadXML(xmlString)`
- `Save(filename)`
- `GetElementsByTagName(tagName)`
- `SelectNodes(xpath)`
- `SelectSingleNode(xpath)`

**Example**:
```python
code = msxml.get_execution_code("LoadXML", "<root></root>")
```

---

## Enumerations

### COMObjectType

```python
COMObjectType.SHELL              # WScript.Shell
COMObjectType.WMI_LOCATOR        # WbemScripting.SWbemLocator
COMObjectType.EXCEL              # Excel.Application
COMObjectType.WORD               # Word.Application
COMObjectType.MSXML              # MSXML2.DOMDocument
COMObjectType.ADODB              # ADODB.Connection
COMObjectType.INTERNET_EXPLORER  # InternetExplorer.Application
COMObjectType.OUTLOOK            # Outlook.Application
COMObjectType.WSCRIPT            # WScript.Shell/WScript.Network
COMObjectType.UNKNOWN            # (Invalid)
```

### COMInstantiationMethod

```python
COMInstantiationMethod.CREATE_OBJECT_PROGID    # CreateObject("ProgID")
COMInstantiationMethod.CREATE_OBJECT_CLSID     # CreateObject("CLSID:...")
COMInstantiationMethod.GET_OBJECT_RUNNING      # GetObject(, "ProgID")
COMInstantiationMethod.GET_OBJECT_MONIKER      # GetObject("path")
COMInstantiationMethod.GET_OBJECT_WMI          # GetObject("winmgmts://")
COMInstantiationMethod.NEW_KEYWORD             # New ClassName
COMInstantiationMethod.REMOTE_DCOM             # CreateObject("ProgID", machine)
COMInstantiationMethod.REGISTRY_LOOKUP         # Registry resolution
COMInstantiationMethod.ENCODED_PROGID          # Encoded creation
COMInstantiationMethod.INLINE_CLASS            # Inline VBScript class
COMInstantiationMethod.CLSID_MONIKER           # CLSID moniker binding
```

---

## Code Generation Patterns

### Pattern 1: Basic Command Execution

```python
loader = COMPolymorphicLoader()
code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "cmd.exe /c dir"
)
```

**Output**:
```vbscript
On Error Resume Next
Dim shell_ABC123
Set shell_ABC123 = CreateObject("WScript.Shell")
If Not IsEmpty(shell_ABC123) Then
    shell_ABC123.Run "cmd.exe /c dir"
End If
On Error GoTo 0
```

### Pattern 2: With Fallback Chain

```python
code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "cmd.exe",
    fallback=True
)
```

**Effect**: If shell fails, WMI_LOCATOR is tried as fallback

### Pattern 3: WMI Query

```python
code = loader.generate_polymorphic_code(
    COMObjectType.WMI_LOCATOR,
    "ExecQuery",
    "SELECT * FROM Win32_Process"
)
```

### Pattern 4: Registry Operation

```python
code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "RegRead",
    "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion"
)
```

### Pattern 5: Excel Operations

```python
code = loader.generate_polymorphic_code(
    COMObjectType.EXCEL,
    "Open",
    "C:\\report.xlsx"
)
```

### Pattern 6: XML Processing

```python
code = loader.generate_polymorphic_code(
    COMObjectType.MSXML,
    "LoadXML",
    "<data><item>test</item></data>"
)
```

---

## Metadata Properties

### COMObjectMetadata

```python
metadata = loader.get_object_metadata(COMObjectType.SHELL)

# Access properties
metadata.object_type              # COMObjectType.SHELL
metadata.progid                   # "WScript.Shell"
metadata.clsid                    # "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"
metadata.instantiation_method     # COMInstantiationMethod enum
metadata.fallback_methods         # List of fallback methods
metadata.requires_library_reference  # bool
metadata.supports_remote          # bool (DCOM)
metadata.supports_encoding        # bool
metadata.encoding_types           # ["base64", "hex", ...]
metadata.version_range            # (min, max) tuple
metadata.description              # string
metadata.category                 # "system", "wmi", "office", "xml", etc.
```

---

## Common Queries

### Get Metadata

```python
# Single object
metadata = loader.get_object_metadata(COMObjectType.SHELL)

# All variants
variants = loader.generate_all_variants()
for obj_type, variant in variants.items():
    print(variant["description"])
    print(variant["methods"])
```

### Check Capabilities

```python
obj = loader.load_object(COMObjectType.SHELL)

# Check if remote supported
metadata = loader.get_object_metadata(COMObjectType.SHELL)
if metadata.supports_remote:
    # Use DCOM
    ...

# Get fallback options
fallbacks = loader.get_fallback_chain(COMObjectType.SHELL)
for fallback_type in fallbacks:
    # Try fallback
    ...

# List methods
methods = obj.get_method_signature()
for method, params in methods.items():
    print(f"{method}: {params}")
```

### Export/Import Configuration

```python
# Export
config_json = loader.export_to_json()
with open("config.json", "w") as f:
    f.write(config_json)

# Import and parse
import json
with open("config.json", "r") as f:
    config = json.load(f)

available = config["available_objects"]
fallbacks = config["fallback_chains"]
variants = config["variants"]
```

---

## Error Handling

### Try-Catch Pattern

```python
code = """
On Error Resume Next

' Primary method
Set shell = CreateObject("WScript.Shell")
shell.Run "cmd.exe"

If Err.Number <> 0 Then
    ' Fallback method
    Set wmi = CreateObject("WbemScripting.SWbemLocator")
End If

On Error GoTo 0
"""
```

### Polymorphic Error Handling

```python
code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "cmd.exe",
    use_error_handling=True    # Enables On Error Resume Next/GoTo 0
)
```

### Check for Empty Object

```python
code = """
If IsEmpty(shell_object) Then
    ' Object creation failed
    ' Use fallback
Else
    ' Object is valid, execute
    shell_object.Run "cmd.exe"
End If
"""
```

---

## Performance Considerations

### Object Caching

```python
# Automatic caching - same reference returned
obj1 = loader.load_object(COMObjectType.SHELL)
obj2 = loader.load_object(COMObjectType.SHELL)
assert obj1 is obj2  # True - cached
```

### Code Generation Overhead

```python
# Generation is fast - string concatenation
start = time.time()
code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "cmd.exe"
)
elapsed = time.time() - start
# Typically < 1ms
```

### Fallback Chain Cost

```python
# No fallback - minimal code
code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "cmd.exe",
    fallback=False
)

# With fallback - more code but more resilient
code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "cmd.exe",
    fallback=True
)
# Extra cost only when primary fails
```

---

## Testing Checklist

- [ ] Object instantiation succeeds
- [ ] Generated code contains correct ProgID
- [ ] Generated code contains correct method calls
- [ ] Error handling is present
- [ ] Fallback chain is correct
- [ ] Arguments are properly escaped
- [ ] Metadata is accurate
- [ ] JSON export parses correctly
- [ ] Remote configuration is applied
- [ ] Version-specific settings work

---

## Common Mistakes to Avoid

❌ **Mistake**: Directly accessing internal objects
```python
# Wrong
loader._objects[COMObjectType.SHELL] = ...

# Right
loader.load_object(COMObjectType.SHELL)
```

❌ **Mistake**: Assuming all objects support remote
```python
# Wrong - Excel doesn't support DCOM
excel = loader.load_object(COMObjectType.EXCEL, use_remote=True)

# Right - Check metadata first
metadata = loader.get_object_metadata(COMObjectType.EXCEL)
if metadata.supports_remote:
    # Use remote
    ...
```

❌ **Mistake**: Not handling None returns
```python
# Wrong
code = obj.get_clsid()  # May be None
use_clsid(code)

# Right
if obj.get_clsid() is not None:
    use_clsid(obj.get_clsid())
```

❌ **Mistake**: Disabling error handling in production
```python
# Wrong
code = loader.generate_polymorphic_code(
    object_type,
    method,
    *args,
    use_error_handling=False
)

# Right
code = loader.generate_polymorphic_code(
    object_type,
    method,
    *args,
    use_error_handling=True
)
```

---

## API Quick Lookup

### By Task

| Task | Code |
|------|------|
| Execute command | `gen.generate_command_executor("cmd")` |
| Query WMI | `gen.generate_wmi_query_executor("SELECT...")` |
| Read registry | `gen.generate_registry_reader("HKCU...")` |
| Open Excel | `loader.generate_polymorphic_code(COMObjectType.EXCEL, "Open", "file.xlsx")` |
| Process XML | `loader.generate_polymorphic_code(COMObjectType.MSXML, "LoadXML", "<xml>...")` |
| List objects | `loader.list_available_objects()` |
| Export config | `loader.export_to_json()` |
| Get methods | `obj.get_method_signature()` |
| Get metadata | `loader.get_object_metadata(type)` |

### By Object

| Object | PROGID | Type | Remote |
|--------|--------|------|--------|
| WScript.Shell | `WScript.Shell` | `SHELL` | Yes |
| WMI Locator | `WbemScripting.SWbemLocator` | `WMI_LOCATOR` | Yes |
| Excel | `Excel.Application` | `EXCEL` | No |
| MSXML | `MSXML2.DOMDocument.6.0` | `MSXML` | No |

---

## Resource Links

- Full Documentation: `COM_POLYMORPHIC_LOADER_DOCUMENTATION.md`
- Quick Start Guide: `COM_POLYMORPHIC_LOADER_GUIDE.md`
- Implementation: `com_polymorphic_loader.py`
- Tests: `test_com_polymorphic_loader.py`
- Examples: `com_polymorphic_loader.py` (demonstrates_polymorphism function)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial release with 4 COM objects, polymorphic loader, fallback chains |

---

## Support

For issues or questions:
1. Check the documentation
2. Review test cases in `test_com_polymorphic_loader.py`
3. Run demonstrations in `com_polymorphic_loader.py`
4. Enable error handling and check generated VBScript
