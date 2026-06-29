# WMI Locator Connection Variants Summary

## Overview

This document describes 16 distinct WMI locator connection variants that use different connection strategies, WMI namespaces, and security configurations. These variants enable comprehensive WMI-based payload generation for various scenarios.

## Variant Categories

### 1. Local Connection Variants (3)

Local connections target the current machine using different address representations.

#### 1.1 Local Dot Connection
- **ID**: `local_dot`
- **Connection Host**: `"."` (dot notation)
- **Namespace**: `root\cimv2`
- **Use Case**: Most common local WMI execution
- **Characteristics**: Fastest, most compatible
- **Code Pattern**:
  ```vbs
  Set objLoc = CreateObject("WbemScripting.SWbemLocator")
  Set objConn = objLoc.ConnectServer(".", "root\cimv2")
  ```

#### 1.2 Local Localhost Connection
- **ID**: `local_localhost`
- **Connection Host**: `"localhost"` (DNS name)
- **Namespace**: `root\cimv2`
- **Use Case**: Named connection to local machine
- **Characteristics**: Requires DNS resolution, alternative to dot notation
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer("localhost", "root\cimv2")
  ```

#### 1.3 Local 127.0.0.1 Connection
- **ID**: `local_127001`
- **Connection Host**: `"127.0.0.1"` (loopback IP)
- **Namespace**: `root\cimv2`
- **Use Case**: IP-based local connection
- **Characteristics**: Explicit loopback address, avoids DNS
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer("127.0.0.1", "root\cimv2")
  ```

### 2. Remote Connection Variants (3)

Remote connections target different machines on the network.

#### 2.1 Remote IP Connection
- **ID**: `remote_ip`
- **Connection Host**: IP address (e.g., `"192.168.1.100"`)
- **Namespace**: `root\cimv2`
- **Use Case**: Cross-machine WMI execution
- **Characteristics**: Requires network access, WMI enabled on target
- **Authentication**: None (may require DCOM credentials)
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer("192.168.1.100", "root\cimv2")
  ```

#### 2.2 Remote Authenticated Connection
- **ID**: `remote_authenticated`
- **Connection Host**: IP address (e.g., `"192.168.1.100"`)
- **Authentication**: Username and password
- **Namespace**: `root\cimv2`
- **Use Case**: Cross-machine execution with explicit credentials
- **Characteristics**: Most reliable for remote execution
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer("192.168.1.100", "root\cimv2", "admin", "password")
  ```

#### 2.3 Remote Obfuscated Connection
- **ID**: `encoded_remote`
- **Connection Host**: IP address (e.g., `"192.168.1.100"`)
- **Namespace**: `root\cimv2`
- **Command Encoding**: Base64
- **Use Case**: Remote execution with command obfuscation
- **Characteristics**: Hides plaintext command in payload
- **Decoder**: Inline Base64 decoder (MSXML2.DOMDocument)
- **Code Pattern**:
  ```vbs
  Function DecodeBase64(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64 = node.NodeTypedValue
  End Function
  ```

### 3. Namespace Variants (7)

Different WMI namespaces provide access to different system information and management capabilities.

#### 3.1 Default Namespace Connection
- **ID**: `default_namespace`
- **Namespace**: Empty/default (defaults to `root\cimv2`)
- **Connection Host**: `"."`
- **Use Case**: Minimal connection parameters
- **Characteristics**: Simplest variant, uses WMI defaults
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer(".")
  ```

#### 3.2 Standard CIMV2 Namespace
- **ID**: `local_dot` (uses standard)
- **Namespace**: `root\cimv2`
- **Use Case**: Default and most common namespace
- **Classes**: Win32_Process, Win32_Service, Win32_LogicalDisk, etc.
- **Characteristics**: Broadest coverage of system classes

#### 3.3 WDM Namespace Connection
- **ID**: `wdm_namespace`
- **Namespace**: `root\WDM`
- **Use Case**: Windows Driver Model, system devices
- **Characteristics**: Hardware and driver information
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer(".", "root\WDM")
  ```

#### 3.4 DCIM Namespace Connection
- **ID**: `dcim_namespace`
- **Namespace**: `root\dcim`
- **Use Case**: Data Center Infrastructure Management
- **Characteristics**: Hardware inventory and system management
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer(".", "root\dcim")
  ```

#### 3.5 Hardware Namespace Connection
- **ID**: `hardware_namespace`
- **Namespace**: `root\hardware`
- **Use Case**: Hardware and device information
- **Characteristics**: System hardware inventory
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer(".", "root\hardware")
  ```

#### 3.6 CIMv1 Legacy Namespace Connection
- **ID**: `cimv1_namespace`
- **Namespace**: `root\cimv1`
- **Use Case**: Legacy WMI classes (older Windows versions)
- **Characteristics**: Backward compatibility, older systems
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer(".", "root\cimv1")
  ```

#### 3.7 Full Path Namespace Connection
- **ID**: `full_path_namespace`
- **Namespace**: `\\.\root\cimv2` (UNC-style path)
- **Connection Host**: `"."`
- **Use Case**: Explicit full-path namespace specification
- **Characteristics**: Extended path format variant
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer(".", "\\\\\root\cimv2")
  ```

### 4. Security Configuration Variants (3)

Security-focused connection variants control authentication and impersonation behavior.

#### 4.1 Impersonation Level Connection
- **ID**: `impersonation_level`
- **Impersonation Level**: 3 (Delegate)
- **Levels**:
  - 0 = Anonymous (no credentials)
  - 1 = Identify (server knows client identity)
  - 2 = Impersonate (server acts as client locally)
  - 3 = Delegate (server acts as client remotely)
- **Use Case**: Remote operations requiring client impersonation
- **Characteristics**: Allows remote resource access as client
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer(".", "root\cimv2")
  objConn.Security_.ImpersonationLevel = 3
  ```

#### 4.2 Authentication Level Connection
- **ID**: `authentication_level`
- **Authentication Level**: 6 (Packet)
- **Levels**:
  - 4 = Connect (authenticate once)
  - 5 = Call (authenticate each call)
  - 6 = Packet (authenticate and sign packets)
  - 7 = PacketPrivacy (authenticate, sign, and encrypt)
  - 8 = PacketIntegrity (authenticate and sign only)
- **Use Case**: Secure remote communication
- **Characteristics**: Message-level security enforcement
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer(".", "root\cimv2")
  objConn.Security_.AuthenticationLevel = 6
  ```

#### 4.3 Security Flags Connection
- **ID**: `security_flags`
- **Security Flags**: 128 (Enable All Privileges)
- **Flags**:
  - 0 = Default behavior
  - 128 = Enable all privileges for the call
- **Use Case**: Privilege elevation for sensitive operations
- **Characteristics**: Grants all available privileges
- **Code Pattern**:
  ```vbs
  Set objConn = objLoc.ConnectServer(".", "root\cimv2", "", "", "", "", 128)
  ```

## Connection Pattern Comparison

| Variant | Type | Host | Namespace | Auth | Security | Speed | Stealth |
|---------|------|------|-----------|------|----------|-------|---------|
| local_dot | Local | `.` | cimv2 | None | Standard | Fast | High |
| local_localhost | Local | `localhost` | cimv2 | None | Standard | Medium | High |
| local_127001 | Local | `127.0.0.1` | cimv2 | None | Standard | Fast | High |
| remote_ip | Remote | IP | cimv2 | None | Standard | Medium | High |
| remote_authenticated | Remote | IP | cimv2 | Yes | Standard | Medium | High |
| encoded_remote | Remote | IP | cimv2 | None | Standard | Medium | Very High |
| default_namespace | Local | `.` | Default | None | Standard | Fast | High |
| wdm_namespace | Local | `.` | WDM | None | Standard | Medium | Medium |
| dcim_namespace | Local | `.` | DCIM | None | Standard | Medium | Medium |
| hardware_namespace | Local | `.` | Hardware | None | Standard | Medium | Medium |
| cimv1_namespace | Local | `.` | CIMv1 | None | Standard | Medium | Low |
| full_path_namespace | Local | `.` | Full Path | None | Standard | Fast | Medium |
| impersonation_level | Security | `.` | cimv2 | None | Delegate | Medium | High |
| authentication_level | Security | `.` | cimv2 | None | Packet | Medium | High |
| security_flags | Security | `.` | cimv2 | None | Privilege | Medium | High |

## WMI Namespace Details

### root\cimv2 (Default)
- **Purpose**: Common Information Model v2 - system management
- **Classes**: Win32_Process, Win32_Service, Win32_LogicalDisk, Win32_NetworkAdapterConfiguration
- **Availability**: All Windows versions with WMI

### root\WDM
- **Purpose**: Windows Driver Model
- **Classes**: Driver and device information
- **Availability**: Windows 2000+

### root\dcim
- **Purpose**: Data Center Infrastructure Management
- **Classes**: Hardware inventory, system info
- **Availability**: Windows Server (limited availability)

### root\hardware
- **Purpose**: Hardware information
- **Classes**: System hardware inventory
- **Availability**: Select Windows versions

### root\cimv1
- **Purpose**: Legacy CIM v1 classes
- **Classes**: Older WMI class definitions
- **Availability**: Windows XP, Server 2003

## Security Levels Explained

### Impersonation Levels
- **Anonymous (0)**: No authentication, server doesn't know client identity
- **Identify (1)**: Client identity is known but not used for access checks
- **Impersonate (2)**: Server can act as client for local resources
- **Delegate (3)**: Server can act as client for remote resources (most powerful)

### Authentication Levels
- **Connect (4)**: Authenticate once at connection start
- **Call (5)**: Authenticate at each method call
- **Packet (6)**: Authenticate and sign all packets
- **PacketPrivacy (7)**: Authenticate, sign, and encrypt packets
- **PacketIntegrity (8)**: Authenticate and sign (no encryption)

## Usage Patterns

### Basic Local Execution
```python
from wmi_locator_variants import WMILocatorVariantGenerator

gen = WMILocatorVariantGenerator()
code = gen.generate_local_dot_connection("calc.exe")
print(code)
```

### Remote Execution with Credentials
```python
code = gen.generate_authenticated_connection(
    "cmd.exe /c ipconfig",
    "192.168.1.100",
    "admin",
    "password"
)
print(code)
```

### Get All Variants
```python
variants = gen.generate_all_variants("calc.exe")
for variant_id, info in variants.items():
    print(f"{variant_id}: {info['description']}")
    print(info['code'])
```

## Detection Evasion

### Obfuscation Techniques
1. **Namespace Variation**: Using non-standard namespaces may evade detection
2. **Command Encoding**: Base64 encoding hides plaintext commands
3. **Remote Execution**: Distributes execution across network
4. **Security Flags**: Privilege elevation requests may bypass UAC

### Variable Name Randomization
All variants include randomized 8-character variable name suffixes:
```vbs
Dim objLoc_qTBGfwoY, objConn_BPkrThEK
```

### Error Suppression
All variants include `On Error Resume Next` and `On Error GoTo 0` for silent failure.

## Network Considerations

### Local Execution
- Uses WMI locally via pipe communication
- No network traffic
- Requires local WMI service
- Fast execution

### Remote Execution
- Uses DCOM (RPC) for communication
- Requires network access to port 445
- May require firewall configuration
- Requires WMI service on remote system
- Slower than local execution

### Authentication
- Local execution: Uses current user credentials
- Remote execution without auth: Uses current credentials via DCOM
- Remote execution with auth: Uses provided credentials
- Kerberos required for delegation level

## Compatibility Matrix

| Variant | WinXP | Vista | Win7 | Win8 | Win10 | Win11 | Server2003 | Server2008 | Server2016 | Server2019 |
|---------|-------|-------|------|------|-------|-------|-----------|-----------|-----------|-----------|
| local_dot | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| remote_ip | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| wdm_namespace | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| dcim_namespace | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| cimv1_namespace | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |

## Performance Characteristics

### Speed Ranking (fastest to slowest)
1. local_dot (baseline: 10-20ms)
2. local_127001 (baseline: 10-20ms)
3. default_namespace (baseline: 10-20ms)
4. full_path_namespace (baseline: 15-25ms)
5. local_localhost (baseline: 15-50ms due to DNS)
6. security_flags (baseline: 15-30ms)
7. impersonation_level (baseline: 15-30ms)
8. authentication_level (baseline: 20-40ms)
9. wdm_namespace (baseline: 20-50ms)
10. hardware_namespace (baseline: 20-50ms)
11. encoded_remote (baseline: 100-500ms)
12. remote_authenticated (baseline: 100-500ms)
13. dcim_namespace (baseline: 50-100ms)
14. remote_ip (baseline: 100-500ms)
15. cimv1_namespace (baseline: 50-150ms)

## Forensic Artifacts

### Windows Event Logs
- Event ID 4688: Process creation (if auditing enabled)
- Event ID 5140: Network access (remote execution)
- WMI Event Tracing for Windows (ETW) logs
- Windows Defender logs

### Registry Artifacts
- HKLM\Software\Microsoft\Wbem: WMI configuration
- HKLM\Software\Microsoft\Windows NT\CurrentVersion: System info

### File Artifacts
- %SystemRoot%\System32\Wbem\Logs: WMI logs
- %SystemRoot%\Temp: Temporary WMI files
- Event log files: %SystemRoot%\System32\WinEvt\Logs

## Defense Mechanisms

### Detection
1. Monitor for SWbemLocator instantiation
2. Track ConnectServer calls with unusual parameters
3. Monitor WMI provider loading
4. Track Create method invocations

### Prevention
1. Disable WMI if not needed
2. Configure Windows Firewall to block DCOM
3. Use AppLocker/WDAC to restrict script execution
4. Enable WMI event logging
5. Monitor for suspicious namespace access

## References

- WbemScripting Type Library Documentation
- Win32_Process WMI Class
- MSDN: Connecting to WMI on a Remote Computer
- MSDN: Setting the Default Security Level for a Namespace
- MSDN: Impersonation in COM
