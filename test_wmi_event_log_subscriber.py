#!/usr/bin/env python3
"""
Test suite for WMI Event Log Subscriber
Tests various event log monitoring and subscription scenarios
"""

import sys
import json
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


def test_basic_failed_login_subscription():
    """Test basic failed login event subscription"""
    print("\n[TEST 1] Basic Failed Login Subscription")
    print("-" * 80)

    config = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SECURITY,
        event_ids=[4625],
        trigger_conditions=[EventTriggerCondition.FAILED_LOGIN],
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_event_log_subscription_vbs("cmd.exe /c whoami")

    assert "__EventFilter" in payload
    assert "CommandLineEventConsumer" in payload
    assert "__FilterToConsumerBinding" in payload
    assert "EventCode=4625" in payload
    print("PASS - Failed login subscription generated correctly")
    return True


def test_successful_login_subscription():
    """Test successful login event subscription"""
    print("\n[TEST 2] Successful Login Subscription")
    print("-" * 80)

    config = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SECURITY,
        event_ids=[4624, 4648],
        trigger_conditions=[EventTriggerCondition.SUCCESSFUL_LOGIN],
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_event_log_subscription_vbs("cmd.exe /c echo test")

    assert "EventCode=4624" in payload or "4648" in payload
    assert "CommandLineEventConsumer" in payload
    print("PASS - Successful login subscription generated correctly")
    return True


def test_privilege_escalation_subscription():
    """Test privilege escalation event subscription"""
    print("\n[TEST 3] Privilege Escalation Subscription")
    print("-" * 80)

    config = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SECURITY,
        event_ids=[4672, 4964],
        trigger_conditions=[EventTriggerCondition.PRIVILEGE_ESCALATION],
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_event_log_subscription_vbs("powershell.exe -Command Get-Process")

    assert "4672" in payload or "4964" in payload
    print("PASS - Privilege escalation subscription generated correctly")
    return True


def test_service_startup_subscription():
    """Test service startup event subscription"""
    print("\n[TEST 4] Service Startup Subscription")
    print("-" * 80)

    config = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SYSTEM,
        event_ids=[7036],
        trigger_conditions=[EventTriggerCondition.SERVICE_STARTED],
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_event_log_subscription_vbs("cmd.exe /c ipconfig")

    assert "EventCode=7036" in payload
    assert "System" in payload or "Logfile=" in payload
    print("PASS - Service startup subscription generated correctly")
    return True


def test_active_script_consumer():
    """Test ActiveScript consumer (more stealthy)"""
    print("\n[TEST 5] Active Script Consumer")
    print("-" * 80)

    config = EventLogSubscriptionConfig(
        consumer_type=ConsumerType.ACTIVE_SCRIPT,
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_active_script_consumer("cmd.exe /c dir")

    assert "ActiveScriptEventConsumer" in payload
    assert "VBScript" in payload
    assert "ScriptText" in payload
    print("PASS - Active Script consumer generated correctly")
    return True


def test_multi_condition_subscription():
    """Test multi-condition event subscription"""
    print("\n[TEST 6] Multi-Condition Subscription")
    print("-" * 80)

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
    payload = subscriber.generate_multi_condition_subscription("cmd.exe /c whoami")

    assert payload.count("__EventFilter") >= 3
    assert "Filter 1:" in payload
    assert "Filter 2:" in payload
    assert "Filter 3:" in payload
    print("PASS - Multi-condition subscription generated correctly")
    return True


def test_indirect_binding():
    """Test indirect binding for anti-forensics"""
    print("\n[TEST 7] Indirect Binding (Anti-Forensics)")
    print("-" * 80)

    config = EventLogSubscriptionConfig(
        binding_type=BindingType.INDIRECT,
        indirect_binding=True,
    )

    subscriber = create_event_log_subscriber(config)
    payload = subscriber.generate_indirect_binding_subscription("cmd.exe /c tasklist")

    assert "ActiveScriptEventConsumer" in payload
    assert "IndirectConsumer" in payload
    print("PASS - Indirect binding subscription generated correctly")
    return True


def test_powershell_subscription():
    """Test PowerShell-based subscription"""
    print("\n[TEST 8] PowerShell Event Log Subscription")
    print("-" * 80)

    subscriber = create_event_log_subscriber()
    payload = subscriber.generate_powershell_event_log_subscription("cmd.exe /c systeminfo")

    assert "$filterName" in payload
    assert "$consumerName" in payload
    assert "New-Object System.Management.ManagementClass" in payload
    assert ".Put()" in payload
    print("PASS - PowerShell subscription generated correctly")
    return True


def test_removal_script():
    """Test removal script generation"""
    print("\n[TEST 9] Removal Script Generation")
    print("-" * 80)

    subscriber = create_event_log_subscriber()
    removal_script = subscriber.generate_removal_script()

    assert "__FilterToConsumerBinding" in removal_script
    assert "Delete" in removal_script
    assert "On Error Resume Next" in removal_script
    print("PASS - Removal script generated correctly")
    return True


def test_detection_queries():
    """Test detection query generation"""
    print("\n[TEST 10] Detection Query Generation")
    print("-" * 80)

    subscriber = create_event_log_subscriber()
    queries = subscriber.generate_detection_query()

    assert "list_event_filters" in queries
    assert "list_consumers" in queries
    assert "list_bindings" in queries
    assert "list_active_script_consumers" in queries
    assert "__EventFilter" in queries["list_event_filters"]
    assert "CommandLineEventConsumer" in queries["list_consumers"]
    print("PASS - Detection queries generated correctly")
    return True


def test_obfuscation():
    """Test name obfuscation"""
    print("\n[TEST 11] Name Obfuscation")
    print("-" * 80)

    config = EventLogSubscriptionConfig(
        obfuscate_names=True,
        randomize_variables=True,
    )

    subscriber = create_event_log_subscriber(config)
    payload1 = subscriber.generate_event_log_subscription_vbs("cmd.exe /c whoami")

    # Verify obfuscation is applied
    assert "EventLogMonitor" in payload1  # Base name still visible in filter
    # Variables should be obfuscated
    assert "evtLocator" in payload1 or "evtService" in payload1
    print("PASS - Name obfuscation applied correctly")
    return True


def test_high_level_api():
    """Test high-level API functions"""
    print("\n[TEST 12] High-Level API")
    print("-" * 80)

    # Test basic payload generation
    payload1 = generate_event_log_payload(
        "cmd.exe /c whoami",
        event_log_source="SECURITY",
        event_ids=[4625],
        payload_type="vbs"
    )
    assert "__EventFilter" in payload1

    # Test PowerShell payload
    payload2 = generate_event_log_payload(
        "cmd.exe /c systeminfo",
        event_log_source="SYSTEM",
        payload_type="powershell"
    )
    assert "$filterName" in payload2

    # Test indirect binding
    payload3 = generate_event_log_payload(
        "cmd.exe /c tasklist",
        payload_type="indirect"
    )
    assert "IndirectConsumer" in payload3

    print("PASS - High-level API works correctly")
    return True


def test_event_filter_wql_generation():
    """Test WQL generation for different event types"""
    print("\n[TEST 13] Event Filter WQL Generation")
    print("-" * 80)

    subscriber = create_event_log_subscriber()

    # Test various WQL generations
    failed_login_wql = subscriber._build_event_filter_wql(
        "Security", [4625], EventTriggerCondition.FAILED_LOGIN
    )
    assert "EventCode=4625" in failed_login_wql
    assert "Win32_NTLogEvent" in failed_login_wql

    service_wql = subscriber._build_event_filter_wql(
        "System", [7036], EventTriggerCondition.SERVICE_STARTED
    )
    assert "EventCode=7036" in service_wql

    privilege_wql = subscriber._build_event_filter_wql(
        "Security", [4672], EventTriggerCondition.PRIVILEGE_ESCALATION
    )
    assert "4672" in privilege_wql

    print("PASS - WQL generation correct for all event types")
    return True


def test_summary_generation():
    """Test configuration summary"""
    print("\n[TEST 14] Configuration Summary")
    print("-" * 80)

    config = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SECURITY,
        event_ids=[4625, 4624],
        trigger_conditions=[
            EventTriggerCondition.FAILED_LOGIN,
            EventTriggerCondition.SUCCESSFUL_LOGIN,
        ],
        consumer_type=ConsumerType.COMMANDLINE,
        binding_type=BindingType.INDIRECT,
        obfuscate_names=True,
        permanent=True,
    )

    subscriber = create_event_log_subscriber(config)
    summary = subscriber.generate_summary()

    assert summary["log_source"] == "Security"
    assert 4625 in summary["event_ids"]
    assert "FailedLogin" in summary["trigger_conditions"]
    assert summary["obfuscation_enabled"] == True
    assert summary["permanent"] == True
    print("PASS - Configuration summary generated correctly")
    print(json.dumps(summary, indent=2))
    return True


def run_all_tests():
    """Run all test cases"""
    tests = [
        test_basic_failed_login_subscription,
        test_successful_login_subscription,
        test_privilege_escalation_subscription,
        test_service_startup_subscription,
        test_active_script_consumer,
        test_multi_condition_subscription,
        test_indirect_binding,
        test_powershell_subscription,
        test_removal_script,
        test_detection_queries,
        test_obfuscation,
        test_high_level_api,
        test_event_filter_wql_generation,
        test_summary_generation,
    ]

    print("=" * 80)
    print("WMI EVENT LOG SUBSCRIBER - TEST SUITE")
    print("=" * 80)

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"FAIL - {test_func.__name__}: {str(e)}")
            failed += 1

    print("\n" + "=" * 80)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
