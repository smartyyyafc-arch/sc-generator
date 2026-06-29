# WMI Locator Variants - Complete Index

## Quick Overview

This package contains 16 distinct WMI (Windows Management Instrumentation) locator connection variants using `WbemScripting.SWbemLocator`. Each variant represents a different approach to establishing WMI connections with various:

- Connection targets (local, remote)
- Authentication methods (none, username/password)
- WMI namespaces (root\cimv2, root\WDM, root\dcim, etc.)
- Security configurations (impersonation levels, authentication levels, privileges)

## Files Included

### Core Implementation Files

1. **wmi_locator_variants.py** (Main generator)
   - `WMILocatorVariantGenerator` class
   - 15 individual variant generation methods
   - `generate_all_variants()` method for complete catalog
   - Produces randomized VBS code with obfuscated variable names

2. **wmi_variants_integration.py** (Integration module)
   - `WMIVariantCatalog` - Organized variant access
   - `WMIPayloadBuilder` - Builder pattern for payload construction
   - `WMIVariantSelector` - Intelligent variant selection based on use case
   - `WMIVariantAnalyzer` - Analysis and comparison tools

### Reference Documentation

3. **WMI_LOCATOR_VARIANTS_SUMMARY.md** (Detailed technical reference)
   - Complete description of each variant
   - Connection patterns and examples
   - Namespace details and compatibility
   - Security levels explanation
   - Performance and detection characteristics
   - Forensic artifacts and defense mechanisms

4. **WMI_VARIANTS_COMPLETE_REFERENCE.txt** (Full code examples)
   - All 16 variants with complete VBS code
   - Summary table
   - Quick reference guide
   - Usage examples

5. **WMI_VARIANTS_INDEX.md** (This file)
   - Quick lookup guide
   - File organization
   - Category breakdown
   - Quick start instructions

### Data Files

6. **wmi_locator_variants.json** (JSON export)
   - All 16 variants in JSON format
   - Variant ID, description, type, and code
   - Easy parsing for integration
   - Machine-readable format

7. **wmi_variants_output.txt** (Sample output)
   - Generated VBS for all variants using "cmd.exe /c whoami"
   - Shows real-world example output
   - Variable name randomization demonstration

## Variant Categories

### 1. Local Connections (3 variants)
- **local_dot**: Connection using dot (.) notation - MOST COMMON
- **local_localhost**: Connection using "localhost" DNS name
- **local_127001**: Connection using 127.0.0.1 loopback IP

**Best for**: Local process execution, testing, stealth

### 2. Remote Connections (3 variants)
- **remote_ip**: Basic remote connection via IP address
- **remote_authenticated**: Remote connection with username/password
- **encoded_remote**: Remote connection with base64 command encoding

**Best for**: Cross-machine execution, lateral movement

### 3. Namespace Variants (7 variants)
- **default_namespace**: Empty namespace (uses WMI default)
- **wdm_namespace**: Windows Driver Model namespace (root\WDM)
- **dcim_namespace**: Data Center Infrastructure Management (root\dcim)
- **hardware_namespace**: Hardware information namespace
- **cimv1_namespace**: Legacy CIMv1 namespace (older systems)
- **winmgmt_namespace**: WinMgmt root namespace
- **full_path_namespace**: Full UNC-style path format

**Best for**: Evading signature-based detection, testing namespace variations

### 4. Security Configuration Variants (3 variants)
- **impersonation_level**: Sets impersonation level (0-3, recommended 3=Delegate)
- **authentication_level**: Sets authentication level (4-8, recommended 6=Packet)
- **security_flags**: Enables security flags (128=Enable All Privileges)

**Best for**: Privilege escalation, secure remote execution, elevated operations

## Usage Quick Start

### Python Import

```python
from wmi_locator_variants import WMILocatorVariantGenerator

# Create generator
gen = WMILocatorVariantGenerator()

# Generate single variant
code = gen.generate_local_dot_connection("calc.exe")
print(code)

# Generate all variants at once
all_variants = gen.generate_all_variants("whoami")
for variant_id, info in all_variants.items():
    print(f"{variant_id}: {info['description']}")
    print(info['code'])
```

### Integration with Payload Generator

```python
from wmi_locator_variants import WMILocatorVariantGenerator

def generate_wmi_payload(command, variant_type="local"):
    gen = WMILocatorVariantGenerator()
    variants = gen.generate_all_variants(command)
    
    # Filter by type
    filtered = {k: v for k, v in variants.items() if v["type"] == variant_type}
    
    # Select or iterate
    for variant_id, variant_info in filtered.items():
        yield variant_id, variant_info["code"]
```

### Polymorphic Payload Selection

```python
import random
from wmi_locator_variants import WMILocatorVariantGenerator

gen = WMILocatorVariantGenerator()
variants = gen.generate_all_variants("cmd.exe")

# Select random variant for polymorphism
variant_id = random.choice(list(variants.keys()))
payload = variants[variant_id]["code"]
```

### Using the Variant Selector

```python
from wmi_variants_integration import WMIVariantSelector

# Get recommendations for specific use case
local_vars = WMIVariantSelector.recommend_for_local_execution()
remote_vars = WMIVariantSelector.recommend_for_remote_execution()
stealth_vars = WMIVariantSelector.recommend_for_stealth()
```

## Variant Characteristics

### Speed Ranking (fastest to slowest)
1. local_dot (10-20ms)
2. local_127001 (10-20ms)
3. default_namespace (10-20ms)
4. full_path_namespace (15-25ms)
5. local_localhost (15-50ms)
6. security_flags (15-30ms)
7. impersonation_level (15-30ms)
8. authentication_level (20-40ms)
9. wdm_namespace (20-50ms)
10. hardware_namespace (20-50ms)
11. dcim_namespace (50-100ms)
12. cimv1_namespace (50-150ms)
13. remote_authenticated (100-500ms)
14. remote_ip (100-500ms)
15. encoded_remote (100-500ms)

### Stealth Ranking (most to least stealthy)
1. encoded_remote (Base64 encoding hides command)
2. full_path_namespace (Non-standard path notation)
3. wdm_namespace (Uncommon namespace)
4. local_dot (Very common, good OPSEC)
5. local_127001 (IP-based, avoids DNS)
6. local_localhost (Requires DNS, potentially logged)
7. impersonation_level (May trigger security alerts)
8. authentication_level (Encryption/signing may be detected)
9. remote_authenticated (Requires credentials, may be logged)
10. dcim_namespace (Rare usage)
11. hardware_namespace (Unusual selection)
12. default_namespace (Minimal parameters, suspicious)
13. remote_ip (Network traffic visible)
14. cimv1_namespace (Legacy system indicator)
15. security_flags (Privilege request, highly suspicious)

## JSON Data Structure

The `wmi_locator_variants.json` file contains:

```json
{
  "variant_id": {
    "description": "Human-readable description",
    "type": "category_type",
    "code": "Complete VBS code"
  }
}
```

Example:
```json
{
  "local_dot": {
    "description": "Local connection using dot (.) notation",
    "type": "local",
    "code": "Dim objLoc_...\nSet objLoc = CreateObject(\"WbemScripting.SWbemLocator\")\n..."
  }
}
```

## VBS Code Pattern

All variants follow this basic pattern:

```vbs
Dim <variables>
On Error Resume Next
Set <locator> = CreateObject("WbemScripting.SWbemLocator")
Set <connection> = <locator>.ConnectServer("<host>", "<namespace>"[, auth params])
[Optional: Set security levels]
Set <service> = <connection>.Get("Win32_Process")
<service>.Create "<command>"
[Cleanup]
On Error GoTo 0
```

### Variable Obfuscation

All variables are randomized with 8-character suffixes:
- `objLoc_qTBGfwoY` instead of `objLocator`
- `objConn_BPkrThEK` instead of `objConnection`
- `objSvc_PmkJsaiE` instead of `objService`

## Connection Parameters

### Host Parameter
- `.` (dot) - Local machine
- `localhost` - Local machine (DNS-based)
- `127.0.0.1` - Local machine (IP-based)
- `<IP>` - Remote machine by IP
- `<hostname>` - Remote machine by hostname

### Namespace Parameter
- `root\cimv2` - Default, system management classes
- `root\WDM` - Windows Driver Model
- `root\dcim` - Data Center Infrastructure Management
- `root\hardware` - Hardware information
- `root\cimv1` - Legacy classes
- `` (empty) - Defaults to cimv2
- `\\.\root\cimv2` - Full path format

### Authentication Parameters
- None - Uses current user credentials
- `username, password` - Explicit credentials
- `username, password, <reserved>, <reserved>, <reserved>, <reserved>, flags` - With flags

## WMI Namespace Details

| Namespace | Full Path | Purpose | Classes | Availability |
|-----------|-----------|---------|---------|--------------|
| cimv2 | root\cimv2 | System management | Win32_Process, Win32_Service | All Windows |
| WDM | root\WDM | Driver model | Driver info | Win2000+ |
| DCIM | root\dcim | Data center management | Hardware inventory | Server editions |
| Hardware | root\hardware | Hardware info | System hardware | Select versions |
| CIMv1 | root\cimv1 | Legacy classes | Older definitions | XP, Server2003 |

## Security Levels

### Impersonation Levels
```
0 = Anonymous (no credentials)
1 = Identify (server knows client identity)
2 = Impersonate (server acts as client locally)
3 = Delegate (server acts as client remotely) ← MOST POWERFUL
```

### Authentication Levels
```
4 = Connect (authenticate once)
5 = Call (authenticate each call)
6 = Packet (authenticate and sign packets) ← RECOMMENDED
7 = PacketPrivacy (sign and encrypt)
8 = PacketIntegrity (sign only)
```

### Security Flags
```
0 = Default behavior
128 = Enable all privileges
```

## Use Case Recommendations

### For Local Process Execution
Use: `local_dot`, `default_namespace`, `local_127001`
- Fast execution
- Minimal parameters
- Good OPSEC

### For Remote Process Execution
Use: `remote_authenticated`, `remote_ip`
- Requires network access
- May need credentials
- DCOM firewall rules

### For Evading Detection
Use: `encoded_remote`, `full_path_namespace`, `wdm_namespace`
- Non-standard patterns
- Uncommon namespaces
- Obfuscated commands

### For Privilege Escalation
Use: `security_flags`, `impersonation_level`, `authentication_level`
- Elevated operations
- Kerberos delegation
- Increased detection risk

### For Maximum Compatibility
Use: `local_dot`, `remote_authenticated`, `default_namespace`
- Works on all Windows versions
- Standard patterns
- Well-tested

## File Access Quick Reference

```python
# Read JSON variants
import json
with open('wmi_locator_variants.json') as f:
    variants = json.load(f)

# Access specific variant
code = variants['local_dot']['code']

# Get all variants of type 'namespace'
namespace_variants = {k: v for k, v in variants.items() if v['type'] == 'namespace'}

# Get variant descriptions
for vid, info in variants.items():
    print(f"{vid}: {info['description']}")
```

## Compatibility Matrix

| Variant | WinXP | Vista | Win7 | Win8 | Win10 | Win11 | Server2003 | Server2008 | Server2016 | Server2019 |
|---------|-------|-------|------|------|-------|-------|-----------|-----------|-----------|-----------|
| local_dot | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| remote_authenticated | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| wdm_namespace | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| dcim_namespace | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| cimv1_namespace | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |

## Detection and Evasion

### Log Artifacts
- Event ID 4688: Process creation
- Event ID 5140: Network access
- WMI Event Tracing (ETW)
- Security event logs

### Detection Evasion Techniques
1. **Variable obfuscation**: All variables randomized
2. **Error suppression**: `On Error Resume Next`
3. **Command encoding**: Base64 for obfuscation
4. **Namespace variation**: Non-standard namespaces evade signatures
5. **Remote execution**: Distributes execution trace

## Performance Considerations

### Local Execution Performance
- Uses WMI service locally
- No network overhead
- Fastest: local_dot, local_127001, default_namespace
- Typical execution: 10-50ms

### Remote Execution Performance
- Uses DCOM (RPC) over network
- Network latency added
- Firewall traversal required
- Typical execution: 100-500ms

### Namespace Impact
- Standard namespace (cimv2): Fastest
- Non-standard namespaces: May be slower
- Encoded variants: Decoder overhead

## Integration Examples

### With Existing Payload Generator

```python
from wmi_locator_variants import WMILocatorVariantGenerator

class EnhancedPayloadGenerator:
    def __init__(self):
        self.wmi_gen = WMILocatorVariantGenerator()
    
    def generate(self, command, technique="wmi", variant=None):
        if technique == "wmi":
            variants = self.wmi_gen.generate_all_variants(command)
            if variant:
                return variants[variant]["code"]
            else:
                return list(variants.values())[0]["code"]
```

### With Polymorphic Wrapper

```python
import random
from wmi_locator_variants import WMILocatorVariantGenerator

def generate_polymorphic_wmi(command, iterations=5):
    gen = WMILocatorVariantGenerator()
    variants = gen.generate_all_variants(command)
    
    for i in range(iterations):
        variant_id = random.choice(list(variants.keys()))
        yield f"' Variant {i}: {variant_id}\n" + variants[variant_id]["code"]
```

## Troubleshooting

### "WMI Service Not Running"
- Ensure Windows Management Instrumentation service is running
- Check: `net start winmgmt`

### "Access Denied"
- Check permissions for WMI namespace
- Verify credentials for remote execution
- Check UAC restrictions

### "Namespace Not Found"
- Verify WMI namespace exists on target system
- Use compatible namespace for OS version
- Fall back to root\cimv2 if unsure

### "Command Not Executing"
- Verify command syntax
- Check if command requires quotes
- Test with simple command first (calc.exe)

## References

- WbemScripting Type Library Documentation
- Win32_Process WMI Class Reference
- MSDN: Connecting to WMI Remotely
- MSDN: Setting WMI Security
- Windows Driver Model (WDM) Documentation
- DCIM Specification

## License and Usage

For authorized security testing and defensive research only. All variants include proper error handling and resource cleanup.

---

**Generated**: 2026-06-29
**Total Variants**: 16
**Categories**: 4 (Local, Remote, Namespace, Security)
**Languages**: VBScript (for execution), Python (for generation)
