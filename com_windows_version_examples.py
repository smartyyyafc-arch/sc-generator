#!/usr/bin/env python3
"""
Windows Version-Specific COM Variants - Usage Examples
Demonstrates how to use the WindowsVersionSpecificCOMVariants generator
for different Windows versions and scenarios
"""

from com_windows_version_variants import (
    WindowsVersionSpecificCOMVariants,
    WindowsVersion,
    generate_comprehensive_windows_variants_report,
    generate_version_comparison_matrix
)


def example_1_simple_version_detection():
    """
    Example 1: Simple Windows version detection
    Useful when you need to identify target system version
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Windows Version Detection")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()

    # Generate version detection code for Windows 10
    version_check_code = gen.generate_version_check_code(WindowsVersion.WIN10)
    print("Version detection code for Windows 10:")
    print(version_check_code)
    print("\n" + "-" * 80 + "\n")


def example_2_uac_aware_instantiation():
    """
    Example 2: UAC-Aware COM Object Instantiation
    Handles different security contexts across Windows versions
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: UAC-Aware COM Object Instantiation")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()

    versions = [WindowsVersion.XP, WindowsVersion.WIN7, WindowsVersion.WIN10, WindowsVersion.WIN11]

    for version in versions:
        version_info = gen.VERSION_INFO[version]
        print(f"\n{version_info.name}:")
        print("-" * 40)
        uac_code = gen.generate_uac_aware_variant(version, "Excel.Application")
        print(uac_code)
        print()


def example_3_registry_paths_by_version():
    """
    Example 3: Version-Specific Registry Path Access
    Shows how registry paths differ across Windows versions
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Version-Specific Registry Path Access")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()

    versions = [WindowsVersion.XP, WindowsVersion.VISTA, WindowsVersion.WIN7, WindowsVersion.WIN11]

    for version in versions:
        version_info = gen.VERSION_INFO[version]
        print(f"\n{version_info.name}:")
        print(f"  COM Objects Registry Path: {version_info.registry_paths.get('com_objects')}")
        print(f"  AppData Registry Path: {version_info.registry_paths.get('appdata', 'N/A')}")

        registry_code = gen.generate_registry_path_variant(version, "com_objects")
        print(f"\nRegistry access code:")
        print(registry_code[:200] + "...\n")


def example_4_appdata_folder_handling():
    """
    Example 4: AppData Folder Handling Across Versions
    Shows how AppData folder structure changes across Windows versions
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: AppData Folder Handling Across Versions")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()

    versions = [WindowsVersion.XP, WindowsVersion.VISTA, WindowsVersion.WIN7, WindowsVersion.WIN10]

    for version in versions:
        version_info = gen.VERSION_INFO[version]
        print(f"\n{version_info.name} AppData Paths:")
        print("-" * 40)
        for folder_type, path in version_info.appdata_folders.items():
            print(f"  {folder_type:<12}: {path}")


def example_5_com_object_availability():
    """
    Example 5: COM Object Availability Checks
    Demonstrates version-specific COM object availability
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: COM Object Availability Checks")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()

    com_objects = ["Excel.Application", "Word.Application", "Shell.Application", "WScript.Shell"]
    versions = [WindowsVersion.XP, WindowsVersion.WIN7, WindowsVersion.WIN10, WindowsVersion.WIN11]

    print("COM Object Availability Matrix:")
    print(f"{'Object':<30} ", end="")
    for version in versions:
        print(f"{gen.VERSION_INFO[version].name:<15} ", end="")
    print("\n" + "-" * 100)

    for obj in com_objects:
        print(f"{obj:<30} ", end="")
        for version in versions:
            available = obj in gen.VERSION_INFO[version].available_com_objects
            status = "Available" if available else "Limited   "
            print(f"{status:<15} ", end="")
        print()


def example_6_security_features_awareness():
    """
    Example 6: Security Features Awareness
    Shows how security features differ across versions
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Security Features Awareness")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()

    versions = [WindowsVersion.XP, WindowsVersion.VISTA, WindowsVersion.WIN7,
               WindowsVersion.WIN10, WindowsVersion.WIN11]

    for version in versions:
        version_info = gen.VERSION_INFO[version]
        print(f"\n{version_info.name}:")
        print("-" * 60)
        print(f"  UAC Supported: {'Yes' if version_info.uac_supported else 'No'}")
        print(f"  Security Features ({len(version_info.security_features)}):")
        for feature in version_info.security_features:
            print(f"    + {feature}")
        if version_info.deprecation_warnings:
            print(f"  Deprecation Warnings:")
            for warning in version_info.deprecation_warnings:
                print(f"    ! {warning}")


def example_7_fallback_cascade():
    """
    Example 7: Fallback Cascade Across Versions
    Shows how to create fallback chains for maximum compatibility
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Fallback Cascade Across Windows Versions")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()

    # Create a cascade from older to newer versions
    versions = [WindowsVersion.WIN7, WindowsVersion.WIN10, WindowsVersion.WIN11]
    fallback_code = gen.generate_fallback_cascade(versions, "Excel.Application")

    print("Fallback cascade code:")
    print(fallback_code)


def example_8_version_optimized_variants():
    """
    Example 8: Version-Optimized Variants
    Shows performance-optimized vs. stealth-optimized vs. compatibility-optimized code
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Version-Optimized Variants")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()

    optimization_types = ["performance", "stealth", "compatibility"]
    version = WindowsVersion.WIN10

    for opt_type in optimization_types:
        print(f"\n{opt_type.upper()} Optimized for Windows 10:")
        print("-" * 60)
        code = gen.generate_version_optimized_variant(version, "Excel.Application", opt_type)
        print(code)
        print()


def example_9_complete_variant_set_per_version():
    """
    Example 9: Complete Variant Set for a Specific Version
    Shows all available variants for a single Windows version
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Complete Variant Set for Windows 7")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()
    version = WindowsVersion.WIN7
    variants = gen.generate_all_variants_for_version(version)

    version_info = gen.VERSION_INFO[version]
    print(f"All variants available for {version_info.name}:\n")

    for variant_id, variant_info in variants.items():
        print(f"\n[{variant_id.upper()}]")
        print(f"Description: {variant_info['description']}")
        print("Code:")
        print("-" * 60)
        print(variant_info['code'][:300] + "..." if len(variant_info['code']) > 300 else variant_info['code'])


def example_10_feature_comparison_matrix():
    """
    Example 10: Feature Comparison Matrix
    Displays features across all Windows versions
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 10: Windows Version Feature Comparison Matrix")
    print("=" * 80 + "\n")

    matrix = generate_version_comparison_matrix()
    print(matrix)


def example_11_xp_specific_handling():
    """
    Example 11: Windows XP Specific Handling
    Demonstrates special handling for legacy XP systems
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 11: Windows XP Specific Handling")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()
    xp_info = gen.VERSION_INFO[WindowsVersion.XP]

    print(f"Windows XP ({xp_info.version_number}) Details:")
    print(f"  Build: {xp_info.build_number}")
    print(f"  Kernel: {xp_info.kernel_version}")
    print(f"  UAC: {'Supported' if xp_info.uac_supported else 'Not supported'}")
    print(f"\nAvailable COM Objects:")
    for obj in xp_info.available_com_objects:
        print(f"  - {obj}")

    print(f"\nAppData Paths:")
    for folder_type, path in xp_info.appdata_folders.items():
        print(f"  {folder_type}: {path}")

    print(f"\nSecurity Features:")
    for feature in xp_info.security_features:
        print(f"  + {feature}")

    print(f"\nDeprecation Warnings:")
    for warning in xp_info.deprecation_warnings:
        print(f"  ! {warning}")

    # Generate XP-specific code
    print("\nXP-Specific COM Instantiation:")
    xp_code = gen.generate_uac_aware_variant(WindowsVersion.XP, "Excel.Application")
    print(xp_code)


def example_12_win11_advanced_security():
    """
    Example 12: Windows 11 Advanced Security Features
    Demonstrates handling of latest Win11 security features
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 12: Windows 11 Advanced Security Features")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()
    win11_info = gen.VERSION_INFO[WindowsVersion.WIN11]

    print(f"Windows 11 ({win11_info.version_number}) Security Features:")
    for i, feature in enumerate(win11_info.security_features, 1):
        print(f"  {i}. {feature}")

    print(f"\nDeprecation Warnings (Legacy Support Removed):")
    for warning in win11_info.deprecation_warnings:
        print(f"  ! {warning}")

    # Generate Win11-specific security-aware code
    print("\nWin11 Security-Aware COM Instantiation:")
    win11_code = gen.generate_security_features_aware_code(WindowsVersion.WIN11, "WScript.Shell")
    print(win11_code)


def example_13_multi_version_com_strategy():
    """
    Example 13: Multi-Version COM Strategy
    Shows how to handle COM instantiation across multiple Windows versions
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 13: Multi-Version COM Strategy")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()

    # Strategy: Try modern versions first, then fallback to older ones
    all_versions = [WindowsVersion.WIN11, WindowsVersion.WIN10, WindowsVersion.WIN7, WindowsVersion.VISTA]

    print("Multi-version strategy (newest to oldest):\n")

    for i, version in enumerate(all_versions, 1):
        info = gen.VERSION_INFO[version]
        print(f"{i}. {info.name} (v{info.version_number})")
        print(f"   UAC: {'Supported' if info.uac_supported else 'Not supported'}")
        print(f"   COM Objects: {len(info.available_com_objects)}")
        print(f"   Security Features: {len(info.security_features)}")
        print()

    # Generate cascade code
    print("Cascade code for best compatibility:")
    cascade = gen.generate_fallback_cascade(all_versions, "Excel.Application")
    print(cascade)


def example_14_programmatic_version_selection():
    """
    Example 14: Programmatic Version Selection
    Shows how to programmatically select appropriate variant
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 14: Programmatic Version Selection")
    print("=" * 80 + "\n")

    gen = WindowsVersionSpecificCOMVariants()

    def select_best_variant(target_com_object: str, current_version: WindowsVersion) -> str:
        """Select best variant for target COM object on specific version"""
        version_info = gen.VERSION_INFO[current_version]

        # Check if COM object is available
        if target_com_object in version_info.available_com_objects:
            print(f"✓ {target_com_object} is available on {version_info.name}")
            if version_info.uac_supported:
                print(f"  Using UAC-aware variant")
                return gen.generate_uac_aware_variant(current_version, target_com_object)
            else:
                print(f"  Using simple variant (no UAC)")
                return gen.generate_version_optimized_variant(current_version, target_com_object, "compatibility")
        else:
            print(f"✗ {target_com_object} may not be available on {version_info.name}")
            print(f"  Consider fallback strategy")
            return None

    # Test programmatic selection
    test_cases = [
        (WindowsVersion.WIN10, "Excel.Application"),
        (WindowsVersion.WIN11, "WScript.Shell"),
        (WindowsVersion.XP, "Excel.Application"),
    ]

    for version, com_obj in test_cases:
        print(f"\nTest: {com_obj} on {gen.VERSION_INFO[version].name}")
        print("-" * 60)
        code = select_best_variant(com_obj, version)
        if code:
            print("Generated code (first 150 chars):")
            print(code[:150] + "...")


def run_all_examples():
    """Run all examples"""
    examples = [
        example_1_simple_version_detection,
        example_2_uac_aware_instantiation,
        example_3_registry_paths_by_version,
        example_4_appdata_folder_handling,
        example_5_com_object_availability,
        example_6_security_features_awareness,
        example_7_fallback_cascade,
        example_8_version_optimized_variants,
        example_9_complete_variant_set_per_version,
        example_10_feature_comparison_matrix,
        example_11_xp_specific_handling,
        example_12_win11_advanced_security,
        example_13_multi_version_com_strategy,
        example_14_programmatic_version_selection,
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}")
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        try:
            example_func = globals()[f"example_{example_num}"]
            example_func()
        except KeyError:
            print(f"Example not found: {example_num}")
            print("Available examples: 1-14")
    else:
        # Run specific example or all
        print("Windows Version-Specific COM Variants - Examples")
        print("Usage: python com_windows_version_examples.py [example_number]")
        print("Examples: 1-14")
        print("\nRunning a subset of important examples...\n")

        # Run key examples
        example_1_simple_version_detection()
        example_2_uac_aware_instantiation()
        example_5_com_object_availability()
        example_6_security_features_awareness()
        example_10_feature_comparison_matrix()
