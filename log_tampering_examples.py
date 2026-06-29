#!/usr/bin/env python3
"""
Log Tampering Examples - Demonstrates usage of log cleaning module

Examples of:
1. Basic event log clearing
2. Audit policy disabling
3. Registry-based log disabling
4. Multi-method comprehensive cleaning
5. Custom configurations
"""

from log_tampering_cleaner import (
    LogTamperingCleaner,
    LogTamperingConfig,
    EventLogType,
    LogTamperingMethod,
    generate_log_cleaning_payload,
    generate_comprehensive_log_tampering,
)
import json


def example_1_basic_event_log_clearing():
    """Example 1: Basic event log clearing"""
    print("\n" + "="*70)
    print("Example 1: Basic Event Log Clearing")
    print("="*70)

    config = LogTamperingConfig(
        log_types=[
            EventLogType.SECURITY,
            EventLogType.SYSTEM,
            EventLogType.APPLICATION,
        ],
        methods=[LogTamperingMethod.CLEAR_EVENT_LOG],
        verbose=True,
    )

    cleaner = LogTamperingCleaner(config)

    print("\n[*] Generating VBS code for event log clearing...")
    vbs_code = cleaner.generate_clear_event_log_vbs()
    print(f"\n{vbs_code[:500]}...\n")

    print("\n[*] Generating Batch code for event log clearing...")
    batch_code = cleaner.generate_clear_event_log_batch()
    print(f"\n{batch_code[:500]}...\n")


def example_2_audit_policy_disabling():
    """Example 2: Disabling Windows audit policies"""
    print("\n" + "="*70)
    print("Example 2: Audit Policy Disabling")
    print("="*70)

    config = LogTamperingConfig(
        log_types=[EventLogType.SECURITY],
        methods=[LogTamperingMethod.DISABLE_AUDIT_POLICY],
        verbose=True,
    )

    cleaner = LogTamperingCleaner(config)

    print("\n[*] Generating PowerShell code to disable audit policies...")
    ps_code = cleaner.generate_disable_audit_policy_powershell()
    print(f"\n{ps_code[:600]}...\n")

    print("\n[*] Generating Batch code to disable audit policies...")
    batch_code = cleaner.generate_disable_audit_policy_batch()
    print(f"\n{batch_code[:600]}...\n")


def example_3_registry_based_logging_disable():
    """Example 3: Disable logging via registry"""
    print("\n" + "="*70)
    print("Example 3: Registry-Based Logging Disable")
    print("="*70)

    config = LogTamperingConfig(
        log_types=[EventLogType.POWERSHELL],
        methods=[LogTamperingMethod.REGISTRY_DISABLE],
        verbose=True,
    )

    cleaner = LogTamperingCleaner(config)

    print("\n[*] Generating VBS code to disable logging via registry...")
    vbs_code = cleaner.generate_registry_log_disable_vbs()
    print(f"\n{vbs_code[:600]}...\n")


def example_4_comprehensive_log_cleaning():
    """Example 4: Comprehensive multi-method log cleaning"""
    print("\n" + "="*70)
    print("Example 4: Comprehensive Log Cleaning (All Methods)")
    print("="*70)

    config = LogTamperingConfig(
        log_types=[
            EventLogType.SECURITY,
            EventLogType.SYSTEM,
            EventLogType.APPLICATION,
            EventLogType.POWERSHELL,
        ],
        methods=[
            LogTamperingMethod.CLEAR_EVENT_LOG,
            LogTamperingMethod.DISABLE_AUDIT_POLICY,
            LogTamperingMethod.REGISTRY_DISABLE,
            LogTamperingMethod.SERVICE_DISABLE,
            LogTamperingMethod.DIRECT_LOG_FILE_WIPE,
        ],
        obfuscate_commands=True,
        verbose=True,
    )

    cleaner = LogTamperingCleaner(config)

    print("\n[*] Generating comprehensive PowerShell script...")
    ps_script = cleaner.generate_combined_log_cleaning_powershell()
    print(f"\n[Generated] Comprehensive PowerShell script ({len(ps_script)} bytes)")
    print(f"\n{ps_script[:800]}...\n")

    print("\n[*] Generating comprehensive Batch script...")
    batch_script = cleaner.generate_combined_log_cleaning_batch()
    print(f"\n[Generated] Comprehensive Batch script ({len(batch_script)} bytes)")
    print(f"\n{batch_script[:800]}...\n")

    print("\n[*] Generating comprehensive VBS script...")
    vbs_script = cleaner.generate_combined_log_cleaning_vbs()
    print(f"\n[Generated] Comprehensive VBS script ({len(vbs_script)} bytes)")
    print(f"\n{vbs_script[:800]}...\n")


def example_5_custom_configuration():
    """Example 5: Custom configuration with specific options"""
    print("\n" + "="*70)
    print("Example 5: Custom Configuration")
    print("="*70)

    config = LogTamperingConfig(
        log_types=[EventLogType.SECURITY, EventLogType.POWERSHELL],
        methods=[
            LogTamperingMethod.CLEAR_EVENT_LOG,
            LogTamperingMethod.REGISTRY_DISABLE,
            LogTamperingMethod.LOG_ROTATION_PREVENT,
        ],
        obfuscate_commands=True,
        remove_evidence_of_clearing=True,
        disable_log_service=True,
        manipulate_timestamps=True,
        prevent_log_rotation=True,
        verbose=True,
    )

    cleaner = LogTamperingCleaner(config)

    print("\n[*] Deployment Configuration:")
    summary = cleaner.generate_deployment_summary()
    print(json.dumps(summary, indent=2))

    print("\n[*] Statistics:")
    stats = cleaner.get_statistics()
    print(json.dumps(stats, indent=2))


def example_6_master_installer():
    """Example 6: Master installer script"""
    print("\n" + "="*70)
    print("Example 6: Master Installer Script")
    print("="*70)

    config = LogTamperingConfig(
        log_types=[
            EventLogType.SECURITY,
            EventLogType.SYSTEM,
            EventLogType.APPLICATION,
            EventLogType.POWERSHELL,
        ],
        methods=[LogTamperingMethod.ALL_METHODS],
    )

    cleaner = LogTamperingCleaner(config)

    print("\n[*] Generating master installer script...")
    master_script = cleaner.generate_master_installer_script()
    print(f"\n[Generated] Master installer script ({len(master_script)} bytes)")
    print(f"\n{master_script[:1000]}...\n")


def example_7_quick_payload():
    """Example 7: Quick log cleaning payload"""
    print("\n" + "="*70)
    print("Example 7: Quick Log Cleaning Payload")
    print("="*70)

    print("\n[*] Generating quick log cleaning payload...")
    payload = generate_log_cleaning_payload(obfuscate=True)
    print(f"\n[Generated] Payload ({len(payload)} bytes)")
    print(f"\n{payload[:600]}...\n")


def example_8_comprehensive_suite():
    """Example 8: Generate complete log tampering suite"""
    print("\n" + "="*70)
    print("Example 8: Comprehensive Log Tampering Suite")
    print("="*70)

    print("\n[*] Generating complete log tampering suite...")
    suite = generate_comprehensive_log_tampering()

    print(f"\n[Generated] {len(suite)} different payloads:")
    for name, code in suite.items():
        print(f"  - {name}: {len(code)} bytes")

    print("\n[*] Sample payloads:")
    for idx, (name, code) in enumerate(list(suite.items())[:3]):
        print(f"\n--- {name} ---")
        print(code[:400])
        print("...")


def example_9_event_log_manipulation():
    """Example 9: Advanced event log manipulation techniques"""
    print("\n" + "="*70)
    print("Example 9: Advanced Event Log Manipulation")
    print("="*70)

    config = LogTamperingConfig(
        log_types=[EventLogType.SECURITY],
        methods=[
            LogTamperingMethod.SWAP_EVENT_IDS,
            LogTamperingMethod.TIMESTAMP_MODIFICATION,
            LogTamperingMethod.DIRECT_LOG_FILE_WIPE,
        ],
    )

    cleaner = LogTamperingCleaner(config)

    print("\n[*] Generating event ID swapping code...")
    swap_code = cleaner.generate_event_id_swapping_code()
    print(f"\n{swap_code[:400]}...\n")

    print("\n[*] Generating timestamp manipulation code...")
    ts_code = cleaner.generate_timestamp_manipulation_code()
    print(f"\n{ts_code[:400]}...\n")

    print("\n[*] Generating log rotation prevention code...")
    rotation_code = cleaner.generate_log_rotation_prevention_code()
    print(f"\n{rotation_code[:400]}...\n")


def example_10_deployment_analysis():
    """Example 10: Analyze deployment configuration"""
    print("\n" + "="*70)
    print("Example 10: Deployment Analysis")
    print("="*70)

    config = LogTamperingConfig(
        log_types=[
            EventLogType.SECURITY,
            EventLogType.SYSTEM,
            EventLogType.APPLICATION,
            EventLogType.POWERSHELL,
            EventLogType.SYSMON,
        ],
        methods=[LogTamperingMethod.ALL_METHODS],
    )

    cleaner = LogTamperingCleaner(config)

    print("\n[*] Generating all log tampering methods...")
    all_methods = cleaner.generate_all_log_tampering_methods()

    print(f"\n[Summary] Generated {len(all_methods)} payloads:")
    for name in sorted(all_methods.keys()):
        code_size = len(all_methods[name])
        print(f"  ✓ {name}: {code_size} bytes")

    print("\n[*] Deployment Summary:")
    summary = cleaner.generate_deployment_summary()
    print(json.dumps(summary, indent=2))

    print("\n[*] System Statistics:")
    stats = cleaner.get_statistics()
    print(json.dumps(stats, indent=2))


def run_all_examples():
    """Run all examples"""
    examples = [
        ("Basic Event Log Clearing", example_1_basic_event_log_clearing),
        ("Audit Policy Disabling", example_2_audit_policy_disabling),
        ("Registry-Based Logging Disable", example_3_registry_based_logging_disable),
        ("Comprehensive Log Cleaning", example_4_comprehensive_log_cleaning),
        ("Custom Configuration", example_5_custom_configuration),
        ("Master Installer Script", example_6_master_installer),
        ("Quick Payload", example_7_quick_payload),
        ("Comprehensive Suite", example_8_comprehensive_suite),
        ("Advanced Event Log Manipulation", example_9_event_log_manipulation),
        ("Deployment Analysis", example_10_deployment_analysis),
    ]

    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  Log Tampering & Event Log Cleaning - Examples".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)

    for idx, (name, example_func) in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n[!] Error in example {idx} ({name}): {e}")

    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  Examples Complete".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70 + "\n")


if __name__ == "__main__":
    run_all_examples()
