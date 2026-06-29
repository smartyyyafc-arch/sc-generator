# WMI Implementation Documentation Index

## Overview

Complete technical documentation for the WMI (Windows Management Instrumentation) implementation in sc-generator, including namespace specifications, connection patterns, execution methods, and code examples.

---

## Primary Documentation Files

### 1. WMI_NAMESPACE_IMPLEMENTATION_TECHNICAL_DOCUMENTATION.md (37 KB)
**Comprehensive technical reference with namespace examples**

**Contents:**
- WMI Architecture Overview
- Core Components (WMI Executor, Locator Variants, Registry Access, Event Subscription)
- Execution Flow Diagrams
- Complete WMI Namespace Specification
  - root\cimv2 (Process Execution - Most Common)
  - root\default (Registry Access)
  - root\WDM (Windows Driver Model)
  - root\dcim (Data Center Infrastructure Management)
  - root\hardware (Hardware Information)
  - root\cimv1 (Legacy Support)
- Connection Methods and Patterns
  - Local connections (dot notation, localhost, 127.0.0.1)
  - Remote connections (IP, hostname)
  - Authenticated connections
  - Impersonation levels (0-3)
  - Authentication levels (4-8)
  - Security flags
- Process Execution Methods
  - SWbemLocator Direct Method (Most Common)
  - SWbemObject Query Method
  - WMI Event Sink Method
  - Timeout Method
- Registry Access via WMI
  - Read operations (String, DWORD, Binary)
  - Write operations (String, DWORD, Binary)
  - Key management (Create, Delete, Enumerate)
  - StdRegProv method invocation patterns
- Obfuscation Techniques
  - Base64 encoding/decoding
  - Hex encoding/decoding
  - Variable name randomization
- Complete Implementation Examples
  - Basic process execution
  - Remote execution with credentials
  - Registry workflows
  - Obfuscated command execution
- Namespace Compatibility Matrix
- Error Handling and Return Values
- Python Implementation Reference
- Security Considerations
- Performance Characteristics
- Troubleshooting Guide

**Audience:** Developers, Security Researchers, System Administrators
**Difficulty:** Intermediate to Advanced
**Use Case:** Deep understanding of WMI capabilities and namespace selection

---

### 2. WMI_QUICK_REFERENCE_AND_PATTERNS.md (19 KB)
**Quick lookup tables and advanced patterns for rapid implementation**

**Contents:**
- Quick Lookup Tables
  - Namespace Quick Reference
  - Connection Host Options
  - Security Level Settings
  - Registry Hive Constants (Decimal/Hex)
  - Win32_Process.Create Return Codes
  - StdRegProv Methods Table
- Connection String Templates (7 templates)
  - Basic Local Connection
  - Remote Connection (No Auth)
  - Remote Connection (With Auth)
  - With Impersonation Level
  - With Authentication Level
  - With Security Flags
  - Registry Access (root\default)
- Advanced Patterns
  - Asynchronous Execution with Event Sink
  - Batch Registry Operations
  - Error-Resilient Remote Execution
  - Command Encoding with Polymorphic Variants
  - WMI Registry Hybrid Approach
- Namespace Decision Tree (Flowchart)
- Code Snippets Library (8 ready-to-use snippets)
  - Minimal Process Execution
  - Compact with Error Handling
  - Full Parameter Control
  - Remote Execution
  - Registry Read
  - Registry Write
  - Base64 Encoded Command
  - Hex Encoded Command
- Performance Optimization (Connection Reuse)
- Namespace Compatibility Notes
- Summary

**Audience:** System Administrators, Automation Engineers, Security Testers
**Difficulty:** Beginner to Intermediate
**Use Case:** Quick copy-paste implementations, decision-making guidance

---

## Supporting Documentation

### Existing WMI Documentation Files

#### Process Execution
- **README_WMI_EXECUTOR.md** - WMI Executor overview and features
- **WMI_EXECUTOR_GUIDE.md** - Complete WMI Executor implementation guide
- **WMI_EXECUTOR_DELIVERABLES.txt** - Execution methods deliverables
- **WMI_EXECUTOR_INDEX.md** - Executor method index

#### Registry Operations
- **WMI_REGISTRY_GUIDE.md** - Complete registry access guide
- **WMI_REGISTRY_API_REFERENCE.md** - Detailed API reference
- **WMI_REGISTRY_QUICKREF.md** - Quick reference for registry operations
- **WMI_REGISTRY_SUMMARY.md** - Registry module summary
- **WMI_REGISTRY_INDEX.md** - Registry index and organization

#### Event Subscription
- **WMI_EVENT_SUBSCRIPTION_DOCUMENTATION.md** - Event subscription implementation
- **WMI_EVENT_SUBSCRIPTION_QUICKSTART.md** - Quick start guide
- **WMI_EVENT_SUBSCRIPTION_SUMMARY.txt** - Summary of event features

---

## Implementation Files

### Python Modules
- **wmi_executor.py** - Core WMI execution engine
  - WMIExecutor class
  - ExecutionConfig dataclass
  - Multiple execution methods
  - Command obfuscation
  - Factory functions

- **wmi_locator_variants.py** - WMI connection variants
  - WMILocatorVariantGenerator class
  - LocatorConnectionConfig dataclass
  - 14+ connection variant methods
  - Local and remote connection patterns

- **wmi_registry_access.py** - Registry access through WMI
  - WMIRegistryAccess class
  - RegistryConfig dataclass
  - Read/write/delete/enumerate operations
  - Multiple registry hive support

- **wmi_event_subscription.py** - WMI event subscription
  - Event sink creation
  - Event filtering
  - Async execution patterns

### Example Files
- **wmi_executor_examples.py** - 18 comprehensive examples
- **wmi_registry_examples.py** - Registry operation examples
- **wmi_event_subscription_examples.py** - Event subscription examples
- **example_hex_decoder_variants.py** - Encoding variants
- **integration_example.py** - Integration patterns

### Test Files
- **test_wmi_executor.py** - WMI executor tests
- **test_wmi_event_subscription.py** - Event subscription tests

---

## Quick Start Guide

### For Immediate Use:
1. Read **WMI_QUICK_REFERENCE_AND_PATTERNS.md**
   - Quick lookup tables
   - Connection templates (copy-paste ready)
   - Code snippets

### For Implementation:
1. Review **WMI_NAMESPACE_IMPLEMENTATION_TECHNICAL_DOCUMENTATION.md**
   - Select appropriate namespace (Section 2)
   - Choose connection method (Section 3)
   - Pick execution method (Section 4)
   - Review complete examples (Section 7)

### For Specific Tasks:

**Process Execution:**
- Read: Section 4 (Execution Methods)
- Example: Section 7.1 (Basic Execution)
- Code: wmi_executor_examples.py

**Registry Operations:**
- Read: Section 5 (Registry Access via WMI)
- Example: Section 7.3 (Registry Workflow)
- Code: wmi_registry_examples.py

**Remote Execution:**
- Read: Section 3.1.4 (Remote Connection - IP)
- Example: Section 7.2 (Remote with Credentials)
- Template: WMI_QUICK_REFERENCE_AND_PATTERNS.md (Template 3)

**Obfuscation:**
- Read: Section 6 (Obfuscation Techniques)
- Example: Section 7.4 (Obfuscated Execution)
- Snippets: WMI_QUICK_REFERENCE_AND_PATTERNS.md (Snippets 7-8)

**Advanced Patterns:**
- All patterns: WMI_QUICK_REFERENCE_AND_PATTERNS.md (Advanced Patterns section)

---

## Namespace Selection Guide

### root\cimv2 (Most Common - Process Execution)
**Use When:** You need to execute commands/manage processes
```
Key Classes: Win32_Process, Win32_Service, Win32_OperatingSystem
Methods: Create, Terminate, Pause, Resume
Example: objConn.Get("Win32_Process").Create "calc.exe"
```

### root\default (Registry Access)
**Use When:** You need to read/write registry values
```
Key Classes: StdRegProv
Methods: GetStringValue, SetStringValue, GetDWORDValue, DeleteValue, etc.
Example: objConn.Get("StdRegProv").Methods_("GetStringValue")
```

### root\WDM (Hardware/Drivers)
**Use When:** You need driver and hardware information
```
Key Classes: Win32_SoundDevice, Win32_NetworkAdapterConfiguration
Example: Query hardware devices and configurations
```

### root\dcim (Data Center Management)
**Use When:** You're on server hardware needing infrastructure info
```
Key Classes: PowerManagement, System Health classes
Example: Enterprise hardware monitoring
```

### root\hardware (Hardware Details)
**Use When:** You need CPU, Memory, Storage information
```
Example: Hardware inventory and specifications
```

### root\cimv1 (Legacy Support)
**Use When:** You're on very old Windows systems
```
Example: Backward compatibility with legacy systems
```

---

## Connection Type Quick Guide

| Scenario | Template | Speed | Auth | Scope |
|----------|----------|-------|------|-------|
| Local execution | `ConnectServer(".", "root\cimv2")` | Fast | None | Local |
| Remote same domain | `ConnectServer("IP", "root\cimv2")` | Medium | Domain | Remote |
| Remote other domain | `ConnectServer("IP", "root\cimv2", "usr", "pwd")` | Medium | Explicit | Remote |
| High privilege | Add security flags or impersonation | Medium | Elevated | Local/Remote |
| Registry access | `ConnectServer(".", "root\default")` | Fast | None | Local |
| Encrypted connection | Set AuthenticationLevel = 7 | Medium | Yes | Remote |

---

## Code Example Index

### VBScript Examples Location
| Example | File | Line | Section |
|---------|------|------|---------|
| Basic locator connection | WMI_NAMESPACE_IMPLEMENTATION_TECHNICAL_DOCUMENTATION.md | Part 3.1.1 | Local Connection |
| Remote connection | WMI_NAMESPACE_IMPLEMENTATION_TECHNICAL_DOCUMENTATION.md | Part 3.1.4 | Remote Connection |
| Authenticated remote | WMI_NAMESPACE_IMPLEMENTATION_TECHNICAL_DOCUMENTATION.md | Part 3.2.1 | Advanced Parameters |
| Process execution | WMI_NAMESPACE_IMPLEMENTATION_TECHNICAL_DOCUMENTATION.md | Part 4.1 | Execution Methods |
| Registry read | WMI_NAMESPACE_IMPLEMENTATION_TECHNICAL_DOCUMENTATION.md | Part 5.2 | Registry Read Operations |
| Registry write | WMI_NAMESPACE_IMPLEMENTATION_TECHNICAL_DOCUMENTATION.md | Part 5.3 | Registry Write Operations |
| Base64 decoding | WMI_NAMESPACE_IMPLEMENTATION_TECHNICAL_DOCUMENTATION.md | Part 6.1 | Base64 Encoding |
| Obfuscated execution | WMI_NAMESPACE_IMPLEMENTATION_TECHNICAL_DOCUMENTATION.md | Part 7.4 | Obfuscated Example |

### Python Examples Location
| Example | File | Number |
|---------|------|--------|
| Basic executor | wmi_executor_examples.py | Example 1-3 |
| Remote execution | wmi_executor_examples.py | Example 9 |
| Registry access | wmi_registry_examples.py | All 20 examples |
| Event subscription | wmi_event_subscription_examples.py | All examples |
| Locator variants | wmi_locator_variants.py | All 14+ methods |

---

## Windows Version Compatibility

| Namespace | WinXP | Vista | 7 | 8 | 10 | 11 | Server |
|-----------|-------|-------|---|---|----|----|--------|
| root\cimv2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| root\default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| root\WDM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| root\dcim | - | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| root\hardware | - | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| root\cimv1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## Key Concepts

### WbemScripting.SWbemLocator
The primary COM object for establishing WMI connections. Used in all patterns.

```vbs
Set objLoc = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLoc.ConnectServer(host, namespace, user, password)
```

### ConnectServer() Parameters
```vbs
ConnectServer(
    strServer,         ' Host: ".", "localhost", IP, hostname
    strNamespace,      ' Namespace: "root\cimv2", "root\default", etc.
    strUser,           ' Username: "" for current user, "DOMAIN\user" for other
    strPassword,       ' Password: "" for current user
    strLocale,         ' Locale: "" for default
    strAuthority,      ' Authority: "" for default
    iSecurityFlags     ' Flags: 0 for default, 128 for all privileges
)
```

### Methods_ and InParameters
Used to call WMI class methods with parameters.

```vbs
Set objMethod = objClass.Methods_("MethodName")
Set objInParams = objMethod.InParameters.SpawnInstance_()
objInParams.ParameterName = value
Set objOutParams = objConnection.ExecMethod("ClassName", "MethodName", objInParams)
```

### Error Handling Pattern
```vbs
On Error Resume Next
' ... operations ...
If Err.Number <> 0 Then
    ' Handle error
End If
On Error GoTo 0
```

---

## Registry Hive Reference

**Hexadecimal Constants Used in StdRegProv:**

- **HKEY_CLASSES_ROOT** = 0x80000000 (2147483648)
- **HKEY_CURRENT_USER** = 0x80000001 (2147483649)
- **HKEY_LOCAL_MACHINE** = 0x80000002 (2147483650) - Most Common
- **HKEY_USERS** = 0x80000003 (2147483651)
- **HKEY_CURRENT_CONFIG** = 0x80000005 (2147483653)

---

## Performance Notes

- **Connection Overhead:** 10-50ms per connection
- **Local Execution:** 50-200ms per command
- **Remote Execution:** 200-1000ms (varies by network)
- **Registry Operations:** 10-50ms per operation
- **Reusing Connections:** 5-10x faster than creating new connections

---

## Security and Stealth Features

Implemented throughout WMI module:
1. Variable name randomization
2. Error suppression (On Error Resume Next)
3. Command encoding (Base64/Hex)
4. Multiple execution methods
5. Registry-based obfuscation
6. Event sink asynchronous execution
7. No plaintext commands in payloads
8. Proper resource cleanup

---

## Troubleshooting Quick Reference

| Problem | Cause | Solution |
|---------|-------|----------|
| Object Required | CreateObject failed | Ensure WbemScripting.SWbemLocator available |
| Access Denied | Insufficient privileges | Run as admin or use different credentials |
| Invalid namespace | Wrong namespace path | Verify namespace exists on target system |
| Connection timeout | Network/firewall | Check connectivity and firewall rules |
| Method not found | WMI service issues | Restart WMI service, check service running |
| Registry key not found | Key doesn't exist | Verify key path, check permissions |

---

## Document Statistics

- **Total Documentation Size:** ~56 KB
- **Main Documents:** 2 comprehensive guides
- **Supporting Files:** 10+ guides and references
- **Code Examples:** 60+ examples (VBS and Python)
- **Namespace Coverage:** 6 primary namespaces + sub-namespaces
- **Methods Documented:** 30+ execution and registry methods
- **Connection Patterns:** 7+ documented patterns

---

## How to Use This Documentation

### For Quick Answers:
→ Use **WMI_QUICK_REFERENCE_AND_PATTERNS.md**
- Contains lookup tables
- Ready-to-use templates
- Code snippets

### For Complete Understanding:
→ Use **WMI_NAMESPACE_IMPLEMENTATION_TECHNICAL_DOCUMENTATION.md**
- Complete namespace specifications
- Detailed method descriptions
- Full implementation examples
- Error handling and troubleshooting

### For Specific Implementation:
1. Review the Quick Reference for your scenario
2. Find the appropriate namespace section
3. Copy template or snippet
4. Customize for your needs
5. Review complete examples for reference

### For Learning:
1. Start with Quick Reference overview
2. Read relevant namespace section in technical doc
3. Study complete examples
4. Test with provided code snippets
5. Review Python implementation for reference

---

## Additional Resources

### Python Implementation
- `wmi_executor.py` - Core execution engine
- `wmi_locator_variants.py` - Connection variants
- `wmi_registry_access.py` - Registry operations
- `wmi_event_subscription.py` - Event handling

### Test and Examples
- `test_wmi_executor.py` - Test suite
- `wmi_executor_examples.py` - 18 examples
- `wmi_registry_examples.py` - Registry examples
- `wmi_event_subscription_examples.py` - Event examples

### Reference Docs
- Windows Management Instrumentation (WMI) documentation
- VBScript reference
- Win32 API reference
- Registry structure documentation

---

## Summary

This documentation set provides:
- ✓ Complete WMI namespace specifications
- ✓ Connection methods and patterns
- ✓ Process execution techniques
- ✓ Registry access implementations
- ✓ Obfuscation and encoding strategies
- ✓ Complete code examples (VBS and Python)
- ✓ Error handling and troubleshooting
- ✓ Performance optimization
- ✓ Security considerations
- ✓ Quick reference tables

**Total Coverage:** Comprehensive implementation guide for all WMI-based operations in sc-generator

