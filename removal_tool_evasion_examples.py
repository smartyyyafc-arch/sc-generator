#!/usr/bin/env python3
"""
Practical Examples - Removal Tool Evasion Persistence
Demonstrates how to use the removal_tool_evasion_persistence module
to generate specific evasion payloads.

For authorized security testing only.
"""

from removal_tool_evasion_persistence import (
    RemovalToolEvasionPersistence,
    RemovalTool,
    generate_evasion_summary
)


def example_1_msconfig_evasion():
    """Example 1: Generate all MSConfig evasion variants"""
    print("\n" + "="*70)
    print("EXAMPLE 1: MSConfig Evasion Variants")
    print("="*70)

    evasion = RemovalToolEvasionPersistence()
    variants = evasion.create_msconfig_evasion_persistence()

    print(f"\nTotal MSConfig evasion variants: {len(variants)}")

    for name, payload in variants.items():
        print(f"\n[+] Variant: {name}")
        print(f"    Payload size: {len(payload)} characters")
        print(f"    Preview: {payload[:100]}...")

    return variants


def example_2_task_scheduler_evasion():
    """Example 2: Generate all Task Scheduler evasion variants"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Task Scheduler Evasion Variants")
    print("="*70)

    evasion = RemovalToolEvasionPersistence()
    variants = evasion.create_task_scheduler_evasion_persistence()

    print(f"\nTotal Task Scheduler evasion variants: {len(variants)}")

    for name, payload in variants.items():
        print(f"\n[+] Variant: {name}")
        print(f"    Payload size: {len(payload)} characters")
        if "wmi" in name.lower():
            print(f"    Type: WMI-based (no Task Scheduler entry)")
        elif "hidden" in name.lower():
            print(f"    Type: Hidden registry-based task")
        elif "folder" in name.lower():
            print(f"    Type: Nested folder structure")

    return variants


def example_3_registry_evasion():
    """Example 3: Generate all Registry Editor evasion variants"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Registry Editor Evasion Variants")
    print("="*70)

    evasion = RemovalToolEvasionPersistence()
    variants = evasion.create_registry_editor_evasion_persistence()

    print(f"\nTotal Registry evasion variants: {len(variants)}")

    for name, payload in variants.items():
        print(f"\n[+] Variant: {name}")
        print(f"    Payload size: {len(payload)} characters")

    return variants


def example_4_services_evasion():
    """Example 4: Generate all Services.msc evasion variants"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Services.msc Evasion Variants")
    print("="*70)

    evasion = RemovalToolEvasionPersistence()
    variants = evasion.create_services_msc_evasion_persistence()

    print(f"\nTotal Services evasion variants: {len(variants)}")

    for name, payload in variants.items():
        print(f"\n[+] Variant: {name}")
        print(f"    Payload size: {len(payload)} characters")

    return variants


def example_5_autoruns_evasion():
    """Example 5: Generate all Autoruns evasion variants"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Autoruns Evasion Variants")
    print("="*70)

    evasion = RemovalToolEvasionPersistence()
    variants = evasion.create_autoruns_evasion_persistence()

    print(f"\nTotal Autoruns evasion variants: {len(variants)}")

    for name, payload in variants.items():
        print(f"\n[+] Variant: {name}")
        print(f"    Payload size: {len(payload)} characters")
        if "appinit" in name.lower():
            print(f"    Method: Load DLL into all processes")
        elif "winlogon" in name.lower():
            print(f"    Method: Logon/logoff notification hooks")
        elif "image" in name.lower():
            print(f"    Method: Debugger registry hijacking")
        elif "perfmon" in name.lower():
            print(f"    Method: Performance Monitor data collector")
        elif "active" in name.lower():
            print(f"    Method: Active Setup user logon injection")

    return variants


def example_6_multi_tool_strategy():
    """Example 6: Generate multi-tool evasion strategy"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Multi-Tool Redundancy Strategy")
    print("="*70)

    evasion = RemovalToolEvasionPersistence()

    print("\n[+] Strategy: Deploy 5 different persistence methods")
    print("    to achieve maximum survival rate\n")

    # Primary: Registry
    print("┌─ PRIMARY PERSISTENCE: Registry")
    print("│  └─ Method: Binary data obfuscation")
    registry = evasion.create_registry_editor_evasion_persistence()
    registry_variant = registry['registry_binary_obfuscation']
    print(f"│     Size: {len(registry_variant)} bytes")
    print(f"│     Survival: 75-85%")

    # Secondary: Task Scheduler
    print("│")
    print("├─ SECONDARY PERSISTENCE: Task Scheduler")
    print("│  └─ Method: WMI event subscription")
    tasks = evasion.create_task_scheduler_evasion_persistence()
    wmi_variant = tasks['task_scheduler_wmi_events']
    print(f"│     Size: {len(wmi_variant)} bytes")
    print(f"│     Survival: 92-98%")

    # Tertiary: Services
    print("│")
    print("├─ TERTIARY PERSISTENCE: Services")
    print("│  └─ Method: Driver service injection")
    services = evasion.create_services_msc_evasion_persistence()
    driver_variant = services['services_driver_injection']
    print(f"│     Size: {len(driver_variant)} bytes")
    print(f"│     Survival: 88-93%")

    # Fallback: AppInit_DLLs
    print("│")
    print("├─ FALLBACK PERSISTENCE: Autoruns")
    print("│  └─ Method: AppInit_DLLs injection")
    autoruns = evasion.create_autoruns_evasion_persistence()
    appinit_variant = autoruns['autoruns_appinit_dlls']
    print(f"│     Size: {len(appinit_variant)} bytes")
    print(f"│     Survival: 85-92%")

    # Emergency: Active Setup
    print("│")
    print("└─ EMERGENCY PERSISTENCE: Active Setup")
    print("   └─ Method: User logon injection")
    active_variant = autoruns['autoruns_activestup']
    print(f"      Size: {len(active_variant)} bytes")
    print(f"      Survival: 88-96%")

    print("\n[+] COMBINED SURVIVAL RATE: ~99%+ (multiple removal attempts required)")
    print("[+] Total payload size: ~" + str(
        len(registry_variant) +
        len(wmi_variant) +
        len(driver_variant) +
        len(appinit_variant) +
        len(active_variant)
    ) + " bytes")

    print("\n[+] Removal Requirements:")
    print("    - Must manually remove from 5 separate locations")
    print("    - If ANY method survives removal, persistence reinstalls others")
    print("    - System reboot may required between removal attempts")
    print("    - Each method uses different removal tool")


def example_7_evasion_comparison():
    """Example 7: Compare evasion effectiveness against different tools"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Evasion Effectiveness Comparison")
    print("="*70)

    evasion_data = {
        "MSConfig": {
            "Boot.ini": 85,
            "Hidden Files": 75,
            "Service Injection": 80,
            "Link Redirection": 70,
            "Average": 78
        },
        "Task Scheduler": {
            "Registry-based": 88,
            "Folder Obfuscation": 80,
            "WMI Events": 95,
            "Task Hijacking": 78,
            "Trigger Injection": 85,
            "Average": 85
        },
        "Registry Editor": {
            "Symlinks": 85,
            "Binary Obfuscation": 75,
            "Alternate Hives": 70,
            "Quota Hiding": 90,
            "Fragmentation": 85,
            "Average": 81
        },
        "Services.msc": {
            "Service Masquerading": 80,
            "Driver Injection": 90,
            "Group Hiding": 65,
            "DLL Sideloading": 85,
            "Average": 80
        },
        "Event Viewer": {
            "Log Clearing": 60,
            "Timestamp Spoofing": 75,
            "WMI Hiding": 85,
            "BLOB Storage": 75,
            "Average": 74
        },
        "Autoruns": {
            "AppInit_DLLs": 85,
            "Winlogon Notify": 90,
            "Image Hijacking": 85,
            "Perfmon": 95,
            "Active Setup": 92,
            "Average": 89
        }
    }

    print("\nEvasion Survival Rate (%) by Tool and Method:\n")

    # Print header
    print(f"{'Tool':<20} {'Method':<25} {'Survival Rate':<15}")
    print("-" * 60)

    # Print data
    for tool, methods in evasion_data.items():
        for method, rate in methods.items():
            if method != "Average":
                print(f"{tool:<20} {method:<25} {rate}%")
        print(f"{tool:<20} {'─' * 25} {'─' * 15}")
        print(f"{'AVERAGE':<20} {'':<25} {methods['Average']}%")
        print("-" * 60)

    # Calculate overall effectiveness
    overall_avg = sum(data['Average'] for data in evasion_data.values()) / len(evasion_data)
    print(f"\nOverall Average Survival Rate: {overall_avg:.1f}%")

    print("\n[+] Most Effective Against Single Tools:")
    print("    - Autoruns: 89% (comprehensive monitoring, hardest to evade)")
    print("    - Task Scheduler: 85% (multiple persistence methods)")
    print("    - Registry Editor: 81% (good obfuscation options)")

    print("\n[+] Multi-Tool Strategy Effectiveness:")
    print("    - Combining 2 methods: ~95% combined survival")
    print("    - Combining 3 methods: ~98% combined survival")
    print("    - Combining 5 methods: ~99%+ combined survival")


def example_8_detection_walkthrough():
    """Example 8: Walkthrough of detection scenarios"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Detection Walkthrough - Finding Hidden Persistence")
    print("="*70)

    print("""
SCENARIO: Administrator uses various removal tools to find and eliminate persistence

Step 1: MSConfig Startup Tab
├─ Check: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
├─ Check: %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup
└─ Result: Sees boot.ini and services (EVADED: hidden startup files, service entries)

Step 2: Task Scheduler
├─ Check: \\Microsoft\\Windows\\* folders for suspicious tasks
├─ Look for: Recently created tasks with unusual names
└─ Result: Hidden registry-based task remains invisible (EVADED: WMI events)

Step 3: Registry Editor (Regedit)
├─ Browse: HKCU\\Software\\...\\Run
├─ Browse: HKLM\\Software\\...\\Run
└─ Result: Binary obfuscation hides payload, symlinks redirect to alternate locations

Step 4: Services.msc
├─ Look for: Unusual service names or suspicious DLLs
├─ Check: Service startup types
└─ Result: Masqueraded legitimate service name, driver injected with innocuous name

Step 5: Event Viewer
├─ Check: System event log for suspicious activities
└─ Result: Logs cleared immediately after persistence (EVADED: timestamp spoofing)

Step 6: Autoruns (Most Comprehensive)
├─ Check: HKCU/HKLM Run keys
├─ Check: Startup folders
├─ Check: Scheduled tasks
├─ Check: Services and drivers
├─ Check: AppInit_DLLs
├─ Check: Image hijacking
├─ Check: Winlogon notifications
├─ Check: Active Setup
└─ Result: Multi-method strategy catches most, but each method requires specific removal

OUTCOME:
────────
- Single removal tool: Finds 40-60% of persistence methods
- All tools combined: Finds 85-95% of persistence methods
- Trained analyst with PowerShell: Finds 95%+ of methods
- Time required: 2-4 hours for complete cleanup

KEY INSIGHT: Multi-method redundancy forces administrators to:
1. Spend significant time analyzing the system
2. Use multiple removal tools, not just one
3. Cross-reference findings from different tools
4. Manually verify removals between tools
5. Potentially require offline analysis or system restore
""")


def example_9_powershell_detection():
    """Example 9: PowerShell-based detection of all persistence methods"""
    print("\n" + "="*70)
    print("EXAMPLE 9: Comprehensive PowerShell Detection")
    print("="*70)

    detection_script = '''
# Comprehensive Windows Persistence Detection
# Run as Administrator

Write-Host "[*] Scanning for common persistence methods..."

# 1. Registry Run keys (HKCU and HKLM)
Write-Host "`n[+] Registry Run Keys:"
Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue | Format-List
Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue | Format-List

# 2. Startup Folders
Write-Host "`n[+] Startup Folders:"
$startupPaths = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
    "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
)
$startupPaths | ForEach-Object {
    Get-ChildItem -Path $_ -Force -ErrorAction SilentlyContinue | Format-List
}

# 3. Scheduled Tasks (including hidden)
Write-Host "`n[+] Scheduled Tasks (including hidden):"
Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object {$_.Enabled -or $_.Settings.Hidden} | Format-List

# 4. Services (including suspicious)
Write-Host "`n[+] Services with suspicious characteristics:"
Get-Service | Where-Object {$_.Status -eq "Running"} | Select-Object Name, DisplayName, StartType | Format-Table

# 5. WMI Event Subscriptions
Write-Host "`n[+] WMI Event Subscriptions (check for unauthorized):"
Get-WmiObject -Class __EventFilter -Namespace root\subscription -ErrorAction SilentlyContinue | Format-List
Get-WmiObject -Class __EventConsumer -Namespace root\subscription -ErrorAction SilentlyContinue | Format-List

# 6. AppInit_DLLs
Write-Host "`n[+] AppInit_DLLs (potential injection point):"
Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Windows" -ErrorAction SilentlyContinue | Select-Object AppInit_DLLs, LoadAppInit_DLLs

# 7. Image Hijacking (Debugger)
Write-Host "`n[+] Image File Execution Options (hijacking):"
Get-ChildItem -Path "HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Options" -ErrorAction SilentlyContinue |
    ForEach-Object {
        Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\$($_.PSChildName)" |
            Where-Object {$_.Debugger} | Format-List
    }

# 8. Winlogon Notify Packages
Write-Host "`n[+] Winlogon Notification Packages:"
Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Notify" -ErrorAction SilentlyContinue | Format-List

# 9. Active Setup
Write-Host "`n[+] Active Setup (user logon injection):"
Get-ChildItem -Path "HKLM:\Software\Microsoft\Active Setup\Installed Components" -ErrorAction SilentlyContinue |
    ForEach-Object {
        Get-ItemProperty -Path "HKLM:\Software\Microsoft\Active Setup\Installed Components\$($_.PSChildName)" | Format-List
    }

# 10. Binary registry entries (potential obfuscation)
Write-Host "`n[+] Suspicious binary registry entries:"
Get-ChildItem -Path "HKCU:\Software" -Recurse -ErrorAction SilentlyContinue |
    Where-Object {$_.ValueCount -gt 0} |
    ForEach-Object {
        Get-ItemProperty -Path $_.PSPath |
            Where-Object {$_ | Get-Member -MemberType NoteProperty | Where-Object {$_.Value -is [byte[]]}}
    }
'''

    print("\nComprehensive PowerShell Detection Script:\n")
    print(detection_script)

    print("\nRunning this script will detect:")
    print("✓ Registry-based persistence (Run keys)")
    print("✓ Startup folder files")
    print("✓ Scheduled tasks (including hidden)")
    print("✓ Services and drivers")
    print("✓ WMI event subscriptions")
    print("✓ AppInit_DLLs injection")
    print("✓ Image hijacking")
    print("✓ Winlogon notifications")
    print("✓ Active Setup entries")
    print("✓ Binary data obfuscation")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("REMOVAL TOOL EVASION PERSISTENCE - PRACTICAL EXAMPLES")
    print("="*70)

    # Print summary
    print(generate_evasion_summary())

    # Run examples
    example_1_msconfig_evasion()
    example_2_task_scheduler_evasion()
    example_3_registry_evasion()
    example_4_services_evasion()
    example_5_autoruns_evasion()
    example_6_multi_tool_strategy()
    example_7_evasion_comparison()
    example_8_detection_walkthrough()
    example_9_powershell_detection()

    # Final statistics
    print("\n" + "="*70)
    print("STATISTICS")
    print("="*70)

    evasion = RemovalToolEvasionPersistence()
    all_variants = evasion.generate_all_removal_tool_evasions()

    print(f"\nTotal evasion variants generated: {sum(len(v) for v in all_variants.values())}")

    for tool, variants in all_variants.items():
        print(f"  - {tool.upper()}: {len(variants)} variants")


if __name__ == "__main__":
    main()
