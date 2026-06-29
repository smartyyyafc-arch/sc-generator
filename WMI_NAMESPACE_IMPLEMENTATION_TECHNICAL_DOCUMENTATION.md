# WMI Implementation - Technical Documentation with Namespace Examples

## Executive Summary

This document provides comprehensive technical documentation of the WMI (Windows Management Instrumentation) implementation within the sc-generator codebase. It includes detailed namespace specifications, connection patterns, execution methods, and practical implementation examples.

**Key Focus Areas:**
- WbemScripting.SWbemLocator implementation
- WMI namespace architecture and usage
- Multiple execution methods and patterns
- Registry access through StdRegProv
- Event subscription mechanisms
- Advanced obfuscation and stealth techniques

---

## Part 1: WMI Architecture Overview

### 1.1 Core Components

The WMI implementation consists of four primary components:

#### 1. WMI Executor (`wmi_executor.py`)
- Handles process execution through WMI
- Manages multiple execution methods
- Implements command obfuscation
- Provides configuration-driven behavior

#### 2. WMI Locator Variants (`wmi_locator_variants.py`)
- Generates connection variants for different scenarios
- Manages namespace specifications
- Handles authentication and security levels
- Supports remote and local connections

#### 3. WMI Registry Access (`wmi_registry_access.py`)
- Provides registry read/write operations
- Uses StdRegProv class for operations
- Supports multiple registry hives
- Implements proper error handling

#### 4. WMI Event Subscription (`wmi_event_subscription.py`)
- Creates asynchronous event handlers
- Manages WMI event sinks
- Implements persistence mechanisms
- Handles event filtering and triggers

### 1.2 Execution Flow

```
User Request (Command)
    |
    v
ExecutionConfig
    |
    v
WMIExecutor/WMILocatorVariantGenerator
    |
    +---> SWbemLocator Creation
    |
    +---> ConnectServer() call
    |
    +---> Namespace Selection
    |
    +---> Class/Method Invocation
    |
    v
VBS Payload Generation
    |
    v
Win32_Process.Create() or StdRegProv Method
    |
    v
Command Execution
```

---

## Part 2: WMI Namespace Specification

### 2.1 Standard WMI Namespaces

WMI organizes classes and functionality into namespaces. Each namespace contains specific management objects and methods.

#### 2.1.1 root\cimv2 - Common Information Model v2

**Purpose:** Primary namespace for system management and process execution

**Most Common Namespace - Default for process execution**

```vbs
' Basic connection to root\cimv2
Dim objLoc, objConn, objSvc, objProc
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\cimv2")
Set objSvc = objConn.Get("Win32_Process")
objSvc.Create "calc.exe"
```

**Key Classes:**
- `Win32_Process` - Process management
- `Win32_Service` - Service operations
- `Win32_OperatingSystem` - OS information
- `Win32_LogicalDisk` - Disk information
- `Win32_NetworkAdapter` - Network interfaces
- `Win32_ComputerSystem` - Computer information
- `Win32_Environment` - Environment variables
- `Win32_Registry` - Registry entries

**Use Cases:**
- Process execution (primary method)
- System query and monitoring
- Service management
- Disk and network operations
- Environment configuration

**Full Path Variations:**
```vbs
' Standard
ConnectServer(".", "root\cimv2")

' UNC path format
ConnectServer(".", "\\.\root\cimv2")

' Localhost
ConnectServer("localhost", "root\cimv2")

' Remote host
ConnectServer("192.168.1.100", "root\cimv2")
```

#### 2.1.2 root\default - Default Registry Provider

**Purpose:** Registry access and manipulation through StdRegProv

**WMI Registry Access Namespace**

```vbs
' Registry access via StdRegProv
Dim objLoc, objConn, objSvc, objMethod, objInParams, objOutParams
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\default")
Set objSvc = objConn.Get("StdRegProv")
Set objMethod = objSvc.Methods_("GetStringValue")
' ... method invocation
```

**Key Classes:**
- `StdRegProv` - Registry provider
  - Methods: GetStringValue, SetStringValue, DeleteValue, CreateKey, DeleteKey, EnumKey, EnumValues, etc.

**Registry Hive Constants:**
```vbs
' Registry hive constants (first parameter to registry methods)
HKEY_CLASSES_ROOT = &H80000000  ' 2147483648
HKEY_CURRENT_USER = &H80000001  ' 2147483649
HKEY_LOCAL_MACHINE = &H80000002 ' 2147483650
HKEY_USERS = &H80000003         ' 2147483651
HKEY_CURRENT_CONFIG = &H80000005 ' 2147483653
```

**Use Cases:**
- Read/write registry values
- Create/delete registry keys
- Enumerate registry structure
- Modify system configuration

**Implementation Example:**
```vbs
' Read registry value
Function ReadRegValue(hive, keyPath, valueName)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("GetStringValue")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    objInParams.sValueName = valueName
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "GetStringValue", objInParams)
    
    If objOutParams.ReturnValue = 0 Then
        ReadRegValue = objOutParams.sValue
    Else
        ReadRegValue = ""
    End If
End Function
```

#### 2.1.3 root\WDM - Windows Driver Model

**Purpose:** Hardware and driver information

**Driver and Hardware Management**

```vbs
Dim objLoc, objConn
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\WDM")
```

**Key Classes:**
- `Win32_SoundDevice` - Audio devices
- `Win32_NetworkAdapterConfiguration` - Network configuration
- `Win32_PnPDevice` - Plug and Play devices
- `Win32_SerialPort` - Serial ports

**Use Cases:**
- Hardware enumeration
- Driver information retrieval
- Device management
- Hardware monitoring

#### 2.1.4 root\dcim - Data Center Infrastructure Management

**Purpose:** System management and infrastructure monitoring

**Enterprise Hardware Management**

```vbs
Dim objLoc, objConn
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\dcim")
```

**Key Classes:**
- PowerManagement classes
- System health information
- Chassis and component data
- Firmware details

**Use Cases:**
- Data center monitoring
- Hardware inventory
- Power management
- System health checks

#### 2.1.5 root\hardware - Hardware Information

**Purpose:** Physical hardware information

**System Hardware Details**

```vbs
Dim objLoc, objConn
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\hardware")
```

**Key Classes:**
- CPU, Memory, Storage information
- Physical component details
- Hardware relationships

#### 2.1.6 root\cimv1 - Legacy CIM v1 Namespace

**Purpose:** Backward compatibility with older WMI implementations

**Legacy WMI Classes**

```vbs
Dim objLoc, objConn
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\cimv1")
```

**Use Cases:**
- Legacy system compatibility
- Older Windows version support
- Historical data access

---

## Part 3: Connection Methods and Patterns

### 3.1 Basic Connection Patterns

#### 3.1.1 Local Connection - Dot Notation (Most Common)

**Pattern:** `ConnectServer(".", namespace)`

```vbs
Dim objLoc, objConn
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\cimv2")
' objConn now connected to local WMI
```

**Characteristics:**
- Connects to local system
- Fastest connection
- Default authentication
- Most common pattern

**When to Use:**
- Local command execution
- Local system queries
- Standard automation scripts

#### 3.1.2 Local Connection - Localhost String

**Pattern:** `ConnectServer("localhost", namespace)`

```vbs
Dim objLoc, objConn
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer("localhost", "root\cimv2")
```

**Characteristics:**
- Alternative to dot notation
- Resolves to local system
- Slightly slower than dot notation
- Network-resolvable name

#### 3.1.3 Loopback IP Connection

**Pattern:** `ConnectServer("127.0.0.1", namespace)`

```vbs
Dim objLoc, objConn
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer("127.0.0.1", "root\cimv2")
```

**Characteristics:**
- IP-based local connection
- Works on all systems
- TCP/IP based
- Useful for network-based automation

#### 3.1.4 Remote Connection - IP Address

**Pattern:** `ConnectServer("192.168.x.x", namespace)`

```vbs
Dim objLoc, objConn, objCmd
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer("192.168.1.100", "root\cimv2")
Set objCmd = objConn.Get("Win32_Process")
objCmd.Create "cmd.exe /c whoami"
```

**Requirements:**
- Network connectivity to remote system
- WMI enabled on remote system
- Appropriate firewall rules
- User privileges on remote system

**Characteristics:**
- Cross-system execution
- Network latency factors
- Requires proper network setup
- Suitable for remote management

#### 3.1.5 Remote Connection with Hostname

**Pattern:** `ConnectServer("hostname", namespace)`

```vbs
Dim objLoc, objConn
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer("SERVER01", "root\cimv2")
```

**Requirements:**
- Hostname resolvable via DNS/hosts file
- Network connectivity
- WMI enabled on remote system

### 3.2 Advanced Connection Parameters

#### 3.2.1 Authenticated Connection

**Pattern:** `ConnectServer(host, namespace, username, password)`

```vbs
Dim objLoc, objConn
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(
    "192.168.1.100",      ' Remote host
    "root\cimv2",         ' Namespace
    "DOMAIN\username",    ' Username
    "password"            ' Password
)
```

**Use Cases:**
- Cross-domain remote execution
- Alternative credentials
- Service account operations
- Privilege escalation scenarios

**Full Signature:**
```
ConnectServer(
    strServer As String,
    strNamespace As String,
    strUser As String,
    strPassword As String,
    strLocale As String = "",
    strAuthority As String = "",
    iSecurityFlags As Long = 0
) As SWbemServices
```

#### 3.2.2 Connection with Impersonation Level

**Pattern:** Setting impersonation after connection

```vbs
Dim objLoc, objConn
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\cimv2")

' Set impersonation level
' 0=Anonymous, 1=Identify, 2=Impersonate, 3=Delegate
objConn.Security_.ImpersonationLevel = 3
```

**Impersonation Levels:**
| Level | Value | Name | Description |
|-------|-------|------|-------------|
| Anonymous | 0 | wbemImpersonationLevelAnonymous | No impersonation |
| Identify | 1 | wbemImpersonationLevelIdentify | Server knows client identity |
| Impersonate | 2 | wbemImpersonationLevelImpersonate | Server can use client identity |
| Delegate | 3 | wbemImpersonationLevelDelegate | Client identity for remote ops |

#### 3.2.3 Connection with Authentication Level

**Pattern:** Setting authentication level

```vbs
Dim objLoc, objConn
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\cimv2")

' Set authentication level
' 4=Connect, 5=Call, 6=Packet, 7=PacketPrivacy, 8=PacketIntegrity
objConn.Security_.AuthenticationLevel = 6
```

**Authentication Levels:**
| Level | Value | Name | Description |
|-------|-------|------|-------------|
| Connect | 4 | wbemAuthenticationLevelDefault | Default/Connect level |
| Call | 5 | wbemAuthenticationLevelCall | Call-level authentication |
| Packet | 6 | wbemAuthenticationLevelPkt | Packet-level authentication |
| Packet Integrity | 8 | wbemAuthenticationLevelPktIntegrity | Packet integrity |
| Packet Privacy | 7 | wbemAuthenticationLevelPktPrivacy | Packet encryption |

#### 3.2.4 Connection with Security Flags

**Pattern:** `ConnectServer(..., iSecurityFlags)`

```vbs
Dim objLoc, objConn
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(
    ".",
    "root\cimv2",
    "",
    "",
    "",
    "",
    128  ' wbemPrivilegeEnableAllPrivilege
)
```

**Common Security Flags:**
| Flag | Value | Purpose |
|------|-------|---------|
| wbemPrivilegeEnableAllPrivilege | 128 | Enable all privileges |
| No flags | 0 | Standard security |

---

## Part 4: Execution Methods

### 4.1 SWbemLocator Direct Method

**Most Common and Most Stealthy**

```vbs
Dim objLoc, objConn, objSvc, objMethod, objInParams, objOutParams
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\cimv2")
Set objSvc = objConn.Get("Win32_Process")
Set objMethod = objSvc.Methods_("Create")
Set objInParams = objMethod.InParameters.SpawnInstance_()
objInParams.CommandLine = "calc.exe"
Set objOutParams = objConn.ExecMethod("Win32_Process", "Create", objInParams)
```

**Components:**
1. **SWbemLocator Creation** - WMI interface object
2. **ConnectServer** - Establish namespace connection
3. **Get** - Retrieve WMI class
4. **Methods_** - Get method definition
5. **InParameters.SpawnInstance_** - Create parameter instance
6. **ExecMethod** - Execute method with parameters

**Return Values:**
- **0** - Process created successfully
- **2** - Permission denied
- **3** - Insufficient memory
- **8** - Unknown error
- **9** - Invalid parameter

### 4.2 SWbemObject Query Method

**Query-Based Execution**

```vbs
Dim objLoc, objServices, objClass, objInstance
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objServices = objLoc.ConnectServer(".", "root\cimv2")
Set objClass = objServices.Get("Win32_ProcessStartup")
Set objInstance = objClass.SpawnInstance_()
objInstance.ShowWindow = 0
objServices.Get("Win32_Process").Create "cmd.exe", Null, objInstance
```

**Key Differences:**
- Uses SpawnInstance_ for object creation
- Supports startup configuration
- Shows window control available
- Cleaner syntax for complex scenarios

### 4.3 WMI Event Sink Method

**Asynchronous Event-Driven Execution**

```vbs
Dim objLoc, objServices, objEvent, objSink, objClass
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objServices = objLoc.ConnectServer(".", "root\cimv2")
Set objSink = CreateObject("WbemScripting.SWbemSink")
Set objClass = objServices.Get("Win32_Process")
objClass.ExecMethodAsync objSink, "Create", CreateObject("WbemScripting.SWbemNamedValueSet")
WScript.Sleep 1000
```

**Characteristics:**
- Asynchronous execution
- Non-blocking call
- Event handler pattern
- Harder to trace

### 4.4 Timeout Method

**Process Execution with Timeout**

```vbs
Dim objLoc, objServices, objStartup, objProcess, dblTimeout
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objServices = objLoc.ConnectServer(".", "root\cimv2")
Set objStartup = objServices.Get("Win32_ProcessStartup").SpawnInstance_()
objStartup.ShowWindow = 0
Dim objInParams, objOutParams
Set objInParams = objServices.Get("Win32_Process").Methods_("Create").InParameters.SpawnInstance_()
objInParams.CommandLine = "cmd.exe"
Set objOutParams = objServices.ExecMethod("Win32_Process", "Create", objInParams)
WScript.Sleep 30000  ' 30 second timeout
```

---

## Part 5: Registry Access via WMI

### 5.1 Registry Method Invocation Pattern

**General Pattern for All Registry Operations:**

```vbs
Function PerformRegistryOperation(operation, hive, keyPath, valueName, valueData)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams, returnValue
    
    ' 1. Create locator and connect to root\default
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    
    ' 2. Get StdRegProv class
    Dim objStdRegProv
    Set objStdRegProv = objConn.Get("StdRegProv")
    
    ' 3. Get method definition (e.g., "GetStringValue", "SetStringValue")
    Set objMethod = objStdRegProv.Methods_(operation)
    
    ' 4. Create and populate input parameters
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    If operation <> "CreateKey" And operation <> "DeleteKey" Then
        objInParams.sValueName = valueName
    End If
    
    ' 5. Execute method
    Set objOutParams = objConn.ExecMethod("StdRegProv", operation, objInParams)
    
    ' 6. Check return value and process output
    PerformRegistryOperation = objOutParams.ReturnValue
End Function
```

### 5.2 Registry Value Read Operations

#### Read String Value

```vbs
Function ReadStringValue(hive, keyPath, valueName)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("GetStringValue")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    objInParams.hDefKey = hive  ' e.g., 2147483650 for HKLM
    objInParams.sSubKeyName = keyPath
    objInParams.sValueName = valueName
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "GetStringValue", objInParams)
    
    If objOutParams.ReturnValue = 0 Then
        ReadStringValue = objOutParams.sValue
    Else
        ReadStringValue = ""
    End If
End Function

' Usage
Dim value
value = ReadStringValue(2147483650, "SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductName")
WScript.Echo value
```

#### Read DWORD Value

```vbs
Function ReadDWORDValue(hive, keyPath, valueName)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("GetDWORDValue")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    objInParams.sValueName = valueName
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "GetDWORDValue", objInParams)
    
    If objOutParams.ReturnValue = 0 Then
        ReadDWORDValue = objOutParams.uValue
    Else
        ReadDWORDValue = 0
    End If
End Function
```

#### Read Binary Value

```vbs
Function ReadBinaryValue(hive, keyPath, valueName)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams, i, hexStr
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("GetBinaryValue")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    objInParams.sValueName = valueName
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "GetBinaryValue", objInParams)
    
    If objOutParams.ReturnValue = 0 Then
        hexStr = ""
        For i = 0 To UBound(objOutParams.uValue)
            hexStr = hexStr & Right("00" & Hex(objOutParams.uValue(i)), 2)
        Next
        ReadBinaryValue = hexStr
    Else
        ReadBinaryValue = ""
    End If
End Function
```

### 5.3 Registry Value Write Operations

#### Write String Value

```vbs
Function WriteStringValue(hive, keyPath, valueName, valueData)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("SetStringValue")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    objInParams.sValueName = valueName
    objInParams.sValue = valueData
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "SetStringValue", objInParams)
    WriteStringValue = objOutParams.ReturnValue
End Function
```

#### Write DWORD Value

```vbs
Function WriteDWORDValue(hive, keyPath, valueName, dwordValue)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("SetDWORDValue")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    objInParams.sValueName = valueName
    objInParams.uValue = dwordValue
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "SetDWORDValue", objInParams)
    WriteDWORDValue = objOutParams.ReturnValue
End Function
```

#### Write Binary Value

```vbs
Function WriteBinaryValue(hive, keyPath, valueName, hexString)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams, i, byteArray
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("SetBinaryValue")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    ' Convert hex string to byte array
    ReDim byteArray(Len(hexString) / 2 - 1)
    For i = 0 To UBound(byteArray)
        byteArray(i) = CLng("&H" & Mid(hexString, i * 2 + 1, 2))
    Next
    
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    objInParams.sValueName = valueName
    objInParams.uValue = byteArray
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "SetBinaryValue", objInParams)
    WriteBinaryValue = objOutParams.ReturnValue
End Function
```

### 5.4 Registry Key Management

#### Create Registry Key

```vbs
Function CreateRegistryKey(hive, keyPath)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("CreateKey")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "CreateKey", objInParams)
    CreateRegistryKey = objOutParams.ReturnValue
End Function
```

#### Delete Registry Key

```vbs
Function DeleteRegistryKey(hive, keyPath)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("DeleteKey")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "DeleteKey", objInParams)
    DeleteRegistryKey = objOutParams.ReturnValue
End Function
```

#### Enumerate Registry Keys

```vbs
Function EnumerateRegistryKeys(hive, keyPath)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams, i
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("EnumKey")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "EnumKey", objInParams)
    
    If objOutParams.ReturnValue = 0 Then
        For i = 0 To UBound(objOutParams.sNames)
            WScript.Echo objOutParams.sNames(i)
        Next
    End If
End Function
```

#### Enumerate Registry Values

```vbs
Function EnumerateRegistryValues(hive, keyPath)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams, i
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("EnumValues")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "EnumValues", objInParams)
    
    If objOutParams.ReturnValue = 0 Then
        For i = 0 To UBound(objOutParams.sNames)
            WScript.Echo "Name: " & objOutParams.sNames(i) & " Type: " & objOutParams.Types(i)
        Next
    End If
End Function
```

---

## Part 6: Obfuscation and Encoding Techniques

### 6.1 Base64 Encoding/Decoding

**In-Script Decoder Function:**

```vbs
Function DecodeBase64(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64 = node.NodeTypedValue
End Function

Function EncodeBase64(data)
    ' Binary data encoding (opposite of decode)
    ' Note: MSXML approach is primarily for decoding
    ' For encoding, use other methods or inline base64 strings
End Function
```

**Usage in WMI Execution:**

```vbs
Function DecodeBase64(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64 = node.NodeTypedValue
End Function

Dim objLoc, objConn, objCmd, decodedCmd
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\cimv2")
Set objCmd = objConn.Get("Win32_Process")

' "Y2FsYy5leGU=" is base64 for "calc.exe"
decodedCmd = DecodeBase64("Y2FsYy5leGU=")
objCmd.Create decodedCmd
```

### 6.2 Hex Encoding/Decoding

**Hex Decoder Function:**

```vbs
Function DecodeHex(hexString)
    Dim i, result
    result = ""
    For i = 1 To Len(hexString) Step 2
        result = result & Chr(CLng("&H" & Mid(hexString, i, 2)))
    Next
    DecodeHex = result
End Function

Function EncodeHex(text)
    Dim i, hexStr
    hexStr = ""
    For i = 1 To Len(text)
        hexStr = hexStr & Right("00" & Hex(Asc(Mid(text, i, 1))), 2)
    Next
    EncodeHex = hexStr
End Function
```

**Usage in WMI Execution:**

```vbs
Function DecodeHex(hexString)
    Dim i, result
    result = ""
    For i = 1 To Len(hexString) Step 2
        result = result & Chr(CLng("&H" & Mid(hexString, i, 2)))
    Next
    DecodeHex = result
End Function

Dim objLoc, objConn, objCmd, decodedCmd
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\cimv2")
Set objCmd = objConn.Get("Win32_Process")

' "63616C632E657865" is hex for "calc.exe"
decodedCmd = DecodeHex("63616C632E657865")
objCmd.Create decodedCmd
```

### 6.3 Variable Name Obfuscation

**Pattern for Randomized Names:**

```python
import random
import string

def generate_random_var_name(prefix="v", length=8):
    """Generate random variable name for obfuscation"""
    suffix = ''.join(random.choices(string.ascii_letters, k=length))
    return f"{prefix}_{suffix}"

# Usage
var_loc = generate_random_var_name("objLoc")      # e.g., "objLoc_XyZaBcDe"
var_conn = generate_random_var_name("objConn")    # e.g., "objConn_AbCdEfGh"
var_cmd = generate_random_var_name("objCmd")      # e.g., "objCmd_MnOpQrSt"
```

**VBS Output with Obfuscation:**

```vbs
Dim objLoc_XyZaBcDe, objConn_AbCdEfGh, objCmd_MnOpQrSt
On Error Resume Next
Set objLoc_XyZaBcDe = CreateObject("WbemScripting.SWbemLocator")
Set objConn_AbCdEfGh = objLoc_XyZaBcDe.ConnectServer(".", "root\cimv2")
Set objCmd_MnOpQrSt = objConn_AbCdEfGh.Get("Win32_Process")
objCmd_MnOpQrSt.Create "calc.exe"
Set objCmd_MnOpQrSt = Nothing
Set objConn_AbCdEfGh = Nothing
Set objLoc_XyZaBcDe = Nothing
On Error GoTo 0
```

---

## Part 7: Complete Implementation Examples

### 7.1 Basic Local Process Execution

```vbs
' Simple process execution on local system
Dim objLoc, objConn, objSvc, objProc
On Error Resume Next

Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\cimv2")
Set objSvc = objConn.Get("Win32_Process")

' Execute command
objSvc.Create "cmd.exe /c ipconfig > C:\temp\ipconfig.txt"

' Cleanup
Set objSvc = Nothing
Set objConn = Nothing
Set objLoc = Nothing
On Error GoTo 0
```

### 7.2 Remote Process Execution with Credentials

```vbs
' Remote execution with authentication
Dim objLoc, objConn, objSvc
On Error Resume Next

Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(
    "192.168.1.100",
    "root\cimv2",
    "DOMAIN\Administrator",
    "Password123"
)

Set objSvc = objConn.Get("Win32_Process")
objSvc.Create "cmd.exe /c net user"

Set objSvc = Nothing
Set objConn = Nothing
Set objLoc = Nothing
On Error GoTo 0
```

### 7.3 Registry Operations Workflow

```vbs
' Complete registry workflow
Function ReadRegistry(hive, keyPath, valueName)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("GetStringValue")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    objInParams.sValueName = valueName
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "GetStringValue", objInParams)
    
    If objOutParams.ReturnValue = 0 Then
        ReadRegistry = objOutParams.sValue
    Else
        ReadRegistry = ""
    End If
End Function

Function WriteRegistry(hive, keyPath, valueName, valueData)
    Dim objLoc, objConn, objMethod, objInParams, objOutParams
    Set objLoc = CreateObject("WbemScripting.SWbemLocator")
    Set objConn = objLoc.ConnectServer(".", "root\default")
    Set objMethod = objConn.Get("StdRegProv").Methods_("SetStringValue")
    Set objInParams = objMethod.InParameters.SpawnInstance_()
    
    objInParams.hDefKey = hive
    objInParams.sSubKeyName = keyPath
    objInParams.sValueName = valueName
    objInParams.sValue = valueData
    
    Set objOutParams = objConn.ExecMethod("StdRegProv", "SetStringValue", objInParams)
    WriteRegistry = objOutParams.ReturnValue
End Function

' Usage
Dim value
value = ReadRegistry(2147483650, "SOFTWARE\Test", "MyValue")
WScript.Echo "Read value: " & value

WriteRegistry 2147483650, "SOFTWARE\Test", "MyValue", "NewValue"
WScript.Echo "Value written"
```

### 7.4 Obfuscated Command Execution

```vbs
Function DecodeBase64(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64 = node.NodeTypedValue
End Function

' Base64 encoded: "cmd.exe /c whoami > C:\temp\whoami.txt"
' Actual encoded value: "Y21kLmV4ZSAvYyB3aG9hbWkgPiBDOlx0ZW1wXHdob2FtaS50eHQ="

Dim objLoc, objConn, objCmd, decodedCmd
On Error Resume Next

Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(".", "root\cimv2")
Set objCmd = objConn.Get("Win32_Process")

decodedCmd = DecodeBase64("Y21kLmV4ZSAvYyB3aG9hbWkgPiBDOlx0ZW1wXHdob2FtaS50eHQ=")
objCmd.Create decodedCmd

Set objCmd = Nothing
Set objConn = Nothing
Set objLoc = Nothing
On Error GoTo 0
```

---

## Part 8: Namespace Compatibility Matrix

| Namespace | Min Windows | Primary Use | Key Classes |
|-----------|-------------|------------|------------|
| root\cimv2 | XP | Process execution, system management | Win32_Process, Win32_Service |
| root\default | XP | Registry operations | StdRegProv |
| root\WDM | XP | Hardware/drivers | Win32_SoundDevice, Win32_NetworkAdapter |
| root\dcim | Vista+ | Data center management | PowerManagement classes |
| root\hardware | Vista+ | Hardware info | CPU, Memory, Storage info |
| root\cimv1 | Legacy | Legacy WMI | Older CIM classes |

---

## Part 9: Error Handling and Return Values

### 9.1 Process Creation Return Codes (Win32_Process.Create)

| Code | Meaning | Resolution |
|------|---------|-----------|
| 0 | Success | Command executed |
| 2 | Access Denied | Insufficient privileges |
| 3 | Insufficient Memory | Not enough RAM |
| 8 | Unknown error | Retry or check system |
| 9 | Invalid parameter | Validate command syntax |

### 9.2 Registry Operation Return Codes (StdRegProv)

| Code | Meaning | Resolution |
|------|---------|-----------|
| 0 | Success | Operation completed |
| 1 | Instance not found | Key/value doesn't exist |
| 2 | Method call failed | WMI error |
| Other | System error code | Check Windows error codes |

### 9.3 Error Handling Patterns

**Pattern 1: Silent Error Handling**

```vbs
On Error Resume Next
' ... code that might fail
If Err.Number <> 0 Then
    ' Error occurred, but continue
End If
On Error GoTo 0
```

**Pattern 2: Explicit Error Checking**

```vbs
On Error Resume Next
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
If Err.Number <> 0 Then
    WScript.Echo "Error creating locator: " & Err.Description
    WScript.Quit
End If
On Error GoTo 0
```

---

## Part 10: Python Implementation Reference

### 10.1 WMIExecutor Class Structure

```python
from dataclasses import dataclass
from typing import Optional, Dict
import base64
import random
import string

@dataclass
class ExecutionConfig:
    """Configuration for WMI execution"""
    use_locator: bool = True
    obfuscate_names: bool = True
    use_polymorphism: bool = True
    encode_command: bool = True
    hide_errors: bool = True

class WMIExecutor:
    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()
        self._var_cache: Dict[str, str] = {}
    
    def _get_or_create_var(self, key: str, prefix: str = "v") -> str:
        """Get or create variable name"""
        if key not in self._var_cache:
            suffix = ''.join(random.choices(string.ascii_letters, k=8))
            self._var_cache[key] = f"{prefix}_{suffix}"
        return self._var_cache[key]
    
    def generate_locator_method(self, command: str) -> str:
        """Generate WMI locator execution payload"""
        # Implementation details...
        pass
```

### 10.2 WMILocatorVariantGenerator Class

```python
class WMILocatorVariantGenerator:
    """Generates WMI locator connection variants"""
    
    def generate_local_dot_connection(self, command: str, namespace: str = "root\\cimv2") -> str:
        """Local connection using dot notation"""
        # Returns VBS code for local execution
        pass
    
    def generate_remote_ip_connection(self, command: str, remote_host: str, 
                                     namespace: str = "root\\cimv2") -> str:
        """Remote connection with IP address"""
        # Returns VBS code for remote execution
        pass
    
    def generate_authenticated_connection(self, command: str, remote_host: str,
                                         username: str, password: str,
                                         namespace: str = "root\\cimv2") -> str:
        """Remote connection with credentials"""
        # Returns VBS code with authentication
        pass
```

---

## Part 11: Security Considerations

### 11.1 WMI Security Requirements

**Local Execution:**
- User must have access to WMI service
- Administrator privileges for Win32_Process.Create
- WMI service must be running

**Remote Execution:**
- Network connectivity to target system
- WMI enabled on target system
- Proper Windows Firewall rules
- Valid credentials on target system (if not same domain)

### 11.2 Detection Evasion

**Techniques Implemented:**
1. Variable name randomization (prevents static pattern matching)
2. Error suppression (hides execution indicators)
3. Command encoding (Base64/Hex for obfuscation)
4. Multiple execution methods (defeats method-specific signatures)
5. Namespace variation (uses different connection paths)

---

## Part 12: Performance Characteristics

| Operation | Typical Speed | Overhead | Notes |
|-----------|--------------|----------|-------|
| Local process creation | 50-200ms | Low | Fastest method |
| Remote process creation | 200-1000ms | Network latency | Depends on network |
| Registry read | 10-50ms | Low | Fast operation |
| Registry write | 10-50ms | Low | Fast operation |
| Event sink creation | 100-300ms | Medium | Async setup cost |

---

## Part 13: Troubleshooting Reference

### Common Issues

**Issue: "Object Required" error**
- Cause: CreateObject failure
- Solution: Ensure WbemScripting.SWbemLocator is available

**Issue: "Access Denied"**
- Cause: Insufficient privileges
- Solution: Run with admin rights or use different credentials

**Issue: "Invalid namespace"**
- Cause: Wrong namespace path
- Solution: Verify namespace exists on target system

**Issue: Remote connection fails**
- Cause: Network/firewall/credentials
- Solution: Test network connectivity and firewall rules

---

## Conclusion

This documentation provides comprehensive coverage of WMI implementation including:
- Namespace specifications and usage patterns
- Connection methods for local and remote systems
- Process execution techniques
- Registry access implementations
- Obfuscation and encoding strategies
- Complete code examples in both VBS and Python
- Error handling and troubleshooting

The WMI implementation within sc-generator supports multiple execution paths, authentication mechanisms, and stealth techniques, making it a comprehensive toolkit for WMI-based operations.

