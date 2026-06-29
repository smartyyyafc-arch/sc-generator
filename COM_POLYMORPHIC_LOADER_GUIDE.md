# COM Polymorphic Loader - Quick Start Guide

## Installation

```bash
# Ensure Python 3.7+ is installed
python3 --version

# Import the module
from com_polymorphic_loader import (
    COMPolymorphicLoader,
    COMPolymorphicCodeGenerator,
    COMObjectType
)
```

## Quick Start (5 Minutes)

### 1. Create a Basic Loader

```python
from com_polymorphic_loader import COMPolymorphicLoader, COMObjectType

# Initialize loader
loader = COMPolymorphicLoader()

# Generate shell command execution code
code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "powershell.exe -Command 'Write-Host Hello'"
)

print(code)
```

### 2. Use High-Level Generator

```python
from com_polymorphic_loader import COMPolymorphicCodeGenerator

gen = COMPolymorphicCodeGenerator()

# Execute command
exec_code = gen.generate_command_executor("notepad.exe")

# Read registry
reg_code = gen.generate_registry_reader("HKCU\\Software")

# Execute WMI query
wmi_code = gen.generate_wmi_query_executor("SELECT * FROM Win32_Process")

print(exec_code)
```

### 3. Load Individual COM Objects

```python
loader = COMPolymorphicLoader()

# Load different objects
shell = loader.load_object(COMObjectType.SHELL)
wmi = loader.load_object(COMObjectType.WMI_LOCATOR)
excel = loader.load_object(COMObjectType.EXCEL)

# All have same interface
print(shell.get_progid())      # WScript.Shell
print(wmi.get_progid())        # WbemScripting.SWbemLocator
print(excel.get_progid())      # Excel.Application
```

---

## Common Tasks

### Task 1: Execute System Command

**Problem**: Execute a command and capture output

**Solution**:
```python
from com_polymorphic_loader import COMPolymorphicCodeGenerator

gen = COMPolymorphicCodeGenerator()
code = gen.generate_command_executor("cmd.exe /c dir C:\\Users")
print(code)
```

**Output**: Ready-to-use VBScript code

### Task 2: Execute WMI Query

**Problem**: Query running processes using WMI

**Solution**:
```python
loader = COMPolymorphicLoader()

code = loader.generate_polymorphic_code(
    COMObjectType.WMI_LOCATOR,
    "ExecQuery",
    "SELECT Name, ProcessId FROM Win32_Process WHERE Name='explorer.exe'"
)
print(code)
```

### Task 3: Read Registry Value

**Problem**: Read Windows registry value safely

**Solution**:
```python
gen = COMPolymorphicCodeGenerator()

code = gen.generate_registry_reader(
    "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders\\Desktop"
)
print(code)
```

### Task 4: Remote Command Execution (DCOM)

**Problem**: Execute command on remote machine

**Solution**:
```python
loader = COMPolymorphicLoader()

# Load shell with remote configuration
shell = loader.load_object(
    COMObjectType.SHELL,
    use_remote=True,
    remote_machine="192.168.1.100"
)

code = shell.get_instantiation_code()
print(code)
```

### Task 5: Open Excel File

**Problem**: Open and interact with Excel workbook

**Solution**:
```python
loader = COMPolymorphicLoader()

excel = loader.load_object(COMObjectType.EXCEL)
code = excel.get_execution_code("Open", "C:\\Data\\Report.xlsx")
print(code)
```

### Task 6: Fallback Chain for Robustness

**Problem**: Ensure execution even if primary method fails

**Solution**:
```python
loader = COMPolymorphicLoader()

code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "powershell.exe",
    fallback=True,        # Enable automatic fallback
    use_error_handling=True
)
print(code)  # Includes fallback to WMI_LOCATOR
```

### Task 7: XML Operations

**Problem**: Parse and manipulate XML

**Solution**:
```python
loader = COMPolymorphicLoader()

msxml = loader.load_object(COMObjectType.MSXML, version=6)
code = msxml.get_execution_code("LoadXML", "<root><item>data</item></root>")
print(code)
```

### Task 8: Export Configuration

**Problem**: Document all available COM objects and configurations

**Solution**:
```python
import json

loader = COMPolymorphicLoader()
config_json = loader.export_to_json()

# Save to file
with open("com_config.json", "w") as f:
    f.write(config_json)

# Parse and use
config = json.loads(config_json)
print("Available objects:", config["available_objects"])
print("Fallback chains:", config["fallback_chains"])
```

---

## Practical Examples

### Example 1: List Running Processes

```python
from com_polymorphic_loader import COMPolymorphicCodeGenerator

gen = COMPolymorphicCodeGenerator()

# Method 1: Using Shell + cmd
shell_code = gen.generate_command_executor("tasklist.exe")

# Method 2: Using WMI
wmi_code = gen.generate_wmi_query_executor(
    "SELECT Name, ProcessId FROM Win32_Process"
)

print("Method 1 (Shell):\n", shell_code)
print("\nMethod 2 (WMI):\n", wmi_code)
```

### Example 2: Check System Uptime

```python
loader = COMPolymorphicLoader()

code = loader.generate_polymorphic_code(
    COMObjectType.WMI_LOCATOR,
    "ExecQuery",
    "SELECT SystemUpTime FROM Win32_OperatingSystem"
)

print(code)
```

### Example 3: Read Environment Variables

```python
gen = COMPolymorphicCodeGenerator()

code = gen.generate_registry_reader("HKCU\\Environment")
print(code)
```

### Example 4: Multi-Object Script

```python
from com_polymorphic_loader import COMPolymorphicLoader, COMObjectType

loader = COMPolymorphicLoader()

# Create script using multiple COM objects
script = """
' Using multiple COM objects polymorphically

"""

# Execute command
cmd_code = loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "cmd.exe /c systeminfo"
)
script += cmd_code + "\n\n"

# Query WMI
wmi_code = loader.generate_polymorphic_code(
    COMObjectType.WMI_LOCATOR,
    "ExecQuery",
    "SELECT * FROM Win32_OperatingSystem"
)
script += wmi_code + "\n"

print(script)
```

### Example 5: Error Handling Pattern

```python
loader = COMPolymorphicLoader()

# Generate code with comprehensive error handling
code = """
On Error Resume Next

"""

# Primary method
code += loader.generate_polymorphic_code(
    COMObjectType.SHELL,
    "Run",
    "powershell.exe -NoProfile -Command Get-Process",
    fallback=False,
    use_error_handling=False  # We'll handle it ourselves
)

code += """

If Err.Number <> 0 Then
    ' Fallback to alternative method
"""

# Fallback method
code += loader.generate_polymorphic_code(
    COMObjectType.WMI_LOCATOR,
    "ExecQuery",
    "SELECT * FROM Win32_Process",
    fallback=False,
    use_error_handling=False
)

code += """
End If

On Error GoTo 0
"""

print(code)
```

---

## Advanced Patterns

### Pattern 1: Object Pool

```python
class COMObjectPool:
    def __init__(self):
        self.loader = COMPolymorphicLoader()
        self.pool = {}
    
    def get_object(self, object_type):
        if object_type not in self.pool:
            self.pool[object_type] = self.loader.load_object(object_type)
        return self.pool[object_type]
    
    def get_code(self, object_type, method, *args):
        obj = self.get_object(object_type)
        return obj.get_execution_code(method, *args)

pool = COMObjectPool()
code = pool.get_code(COMObjectType.SHELL, "Run", "calc.exe")
```

### Pattern 2: Dynamic Method Dispatcher

```python
from com_polymorphic_loader import COMObjectType

class COMDispatcher:
    def __init__(self):
        self.loader = COMPolymorphicLoader()
    
    def execute(self, object_type, method, *args, **kwargs):
        return self.loader.generate_polymorphic_code(
            object_type,
            method,
            *args,
            fallback=kwargs.get("fallback", True),
            use_error_handling=kwargs.get("error_handling", True)
        )

dispatcher = COMDispatcher()

# Execute various operations
code1 = dispatcher.execute(COMObjectType.SHELL, "Run", "cmd.exe")
code2 = dispatcher.execute(COMObjectType.WMI_LOCATOR, "ExecQuery", "SELECT *...")
code3 = dispatcher.execute(COMObjectType.EXCEL, "Open", "file.xlsx")
```

### Pattern 3: Pipeline Architecture

```python
class COMPipeline:
    def __init__(self):
        self.loader = COMPolymorphicLoader()
        self.steps = []
    
    def add_step(self, object_type, method, *args):
        code = self.loader.generate_polymorphic_code(
            object_type, method, *args
        )
        self.steps.append(code)
        return self
    
    def build(self):
        return "\n\n".join(self.steps)

pipeline = COMPipeline()
pipeline.add_step(COMObjectType.SHELL, "Run", "cmd.exe /c ipconfig")
pipeline.add_step(COMObjectType.WMI_LOCATOR, "ExecQuery", "SELECT * FROM Win32_NetworkAdapterConfiguration")
pipeline.add_step(COMObjectType.SHELL, "RegRead", "HKCU\\Software")

final_code = pipeline.build()
print(final_code)
```

---

## Testing Your Code

### Unit Testing

```python
import unittest
from com_polymorphic_loader import COMPolymorphicLoader, COMObjectType

class TestMyPayload(unittest.TestCase):
    def setUp(self):
        self.loader = COMPolymorphicLoader()
    
    def test_shell_execution(self):
        code = self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "Run",
            "calc.exe"
        )
        self.assertIn("WScript.Shell", code)
        self.assertIn("Run", code)
        self.assertIn("calc.exe", code)
    
    def test_wmi_query(self):
        code = self.loader.generate_polymorphic_code(
            COMObjectType.WMI_LOCATOR,
            "ExecQuery",
            "SELECT * FROM Win32_Process"
        )
        self.assertIn("WbemScripting.SWbemLocator", code)
        self.assertIn("ExecQuery", code)

if __name__ == "__main__":
    unittest.main()
```

### Integration Testing

```python
def test_integration():
    gen = COMPolymorphicCodeGenerator()
    
    # Test command execution
    cmd_code = gen.generate_command_executor("cmd.exe /c echo test")
    assert "WScript.Shell" in cmd_code
    
    # Test WMI query
    wmi_code = gen.generate_wmi_query_executor("SELECT * FROM Win32_Process")
    assert "WbemScripting.SWbemLocator" in wmi_code
    
    # Test registry read
    reg_code = gen.generate_registry_reader("HKCU\\Software")
    assert "RegRead" in reg_code
    
    print("All integration tests passed!")

test_integration()
```

---

## Debugging Tips

### Tip 1: Print Generated Code

```python
loader = COMPolymorphicLoader()
code = loader.generate_polymorphic_code(COMObjectType.SHELL, "Run", "test.exe")
print("=" * 80)
print(code)
print("=" * 80)
```

### Tip 2: Check Object Metadata

```python
loader = COMPolymorphicLoader()
metadata = loader.get_object_metadata(COMObjectType.SHELL)
print(f"ProgID: {metadata.progid}")
print(f"CLSID: {metadata.clsid}")
print(f"Supports Remote: {metadata.supports_remote}")
print(f"Category: {metadata.category}")
```

### Tip 3: Verify Method Signatures

```python
shell = loader.load_object(COMObjectType.SHELL)
methods = shell.get_method_signature()
print("Available methods:")
for method, params in methods.items():
    print(f"  {method}: {params}")
```

### Tip 4: Export and Review Configuration

```python
loader = COMPolymorphicLoader()
config = loader.export_to_json()
# Review in text editor or parse with json.loads()
```

---

## Performance Tips

1. **Load objects once, reuse multiple times**
   ```python
   shell = loader.load_object(COMObjectType.SHELL)  # Load once
   code1 = shell.get_execution_code("Run", "cmd1.exe")
   code2 = shell.get_execution_code("Run", "cmd2.exe")  # Reuse
   ```

2. **Cache generated code**
   ```python
   cache = {}
   key = (object_type, method, args)
   if key not in cache:
       cache[key] = loader.generate_polymorphic_code(...)
   code = cache[key]
   ```

3. **Use fallback wisely**
   - Enable for critical operations
   - Disable if performance is critical
   - Profile your specific use case

---

## Troubleshooting

### Issue: "Object not found"

**Cause**: COM object not registered on system

**Solution**:
```python
# Check available objects
available = loader.list_available_objects()
print(available)

# Use different object
code = loader.generate_polymorphic_code(
    COMObjectType.WMI_LOCATOR,  # Try alternative
    "ExecQuery",
    "SELECT * FROM Win32_Process"
)
```

### Issue: "Permission denied"

**Cause**: Insufficient privileges

**Solution**:
```python
# Run with administrator privileges
# Use error handling
code = loader.generate_polymorphic_code(
    object_type,
    method,
    *args,
    use_error_handling=True  # Will catch errors gracefully
)
```

### Issue: "Method not found"

**Cause**: Incorrect method name or signature

**Solution**:
```python
# Check available methods
obj = loader.load_object(COMObjectType.SHELL)
methods = obj.get_method_signature()
print(methods)  # List all available methods
```

---

## Summary

**Key takeaways**:

1. Use `COMPolymorphicLoader` for low-level control
2. Use `COMPolymorphicCodeGenerator` for common tasks
3. Enable fallback chains for robustness
4. Always include error handling
5. Test generated code before deployment
6. Use object pool for performance
7. Export configuration for documentation

**Next steps**:

- Run `test_com_polymorphic_loader.py` to verify installation
- Explore example generation in `demonstrate_polymorphism()`
- Read `COM_POLYMORPHIC_LOADER_DOCUMENTATION.md` for detailed reference
- Implement custom COM objects for specialized use cases
