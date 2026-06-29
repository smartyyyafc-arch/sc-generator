#!/usr/bin/env python3
"""
Test Suite for WMI Event Subscription Implementation
Tests event subscription generation and handler creation
"""

import unittest
import base64
from wmi_event_subscription import (
    WMIEventSubscription, EventSubscriptionConfig, EventTriggerType,
    create_event_subscription, generate_event_subscription_payload
)


class TestEventSubscriptionConfig(unittest.TestCase):
    """Test event subscription configuration"""

    def test_default_config(self):
        """Test default configuration"""
        config = EventSubscriptionConfig()
        self.assertEqual(config.event_trigger, EventTriggerType.PROCESS_START)
        self.assertEqual(config.namespace, "root\\subscription")
        self.assertTrue(config.obfuscate_names)

    def test_custom_config(self):
        """Test custom configuration"""
        config = EventSubscriptionConfig(
            event_trigger=EventTriggerType.SERVICE_START,
            event_filter_name="CustomFilter",
            consumer_name="CustomConsumer"
        )
        self.assertEqual(config.event_trigger, EventTriggerType.SERVICE_START)
        self.assertEqual(config.event_filter_name, "CustomFilter")
        self.assertEqual(config.consumer_name, "CustomConsumer")


class TestEventSubscriptionGeneration(unittest.TestCase):
    """Test event subscription payload generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.subscription = create_event_subscription()
        self.test_command = "cmd.exe /c whoami"

    def test_event_subscription_vbs(self):
        """Test basic event subscription VBS generation"""
        payload = self.subscription.generate_event_subscription_vbs(self.test_command)
        self.assertIsInstance(payload, str)
        self.assertIn("WbemScripting.SWbemLocator", payload)
        self.assertIn("__EventFilter", payload)
        self.assertIn("CommandLineEventConsumer", payload)
        self.assertIn(self.test_command, payload)

    def test_async_event_handler(self):
        """Test async event handler generation"""
        payload = self.subscription.generate_async_event_handler(self.test_command)
        self.assertIsInstance(payload, str)
        self.assertIn("Class", payload)
        self.assertIn("OnObjectReady", payload)
        self.assertIn(self.test_command, payload)

    def test_timer_event_consumer(self):
        """Test timer event consumer generation"""
        interval = 120000
        payload = self.subscription.generate_timer_event_consumer(
            self.test_command, interval
        )
        self.assertIsInstance(payload, str)
        self.assertIn("__TimerEvent", payload)
        self.assertIn(str(interval), payload)
        self.assertIn(self.test_command, payload)

    def test_service_startup_consumer(self):
        """Test service startup consumer generation"""
        service_name = "WinRM"
        payload = self.subscription.generate_service_startup_consumer(
            self.test_command, service_name
        )
        self.assertIsInstance(payload, str)
        self.assertIn("Win32_Service", payload)
        self.assertIn(service_name, payload)
        self.assertIn(self.test_command, payload)

    def test_process_trigger_subscription(self):
        """Test process-specific trigger subscription"""
        process_name = "notepad.exe"
        payload = self.subscription.generate_event_trigger_subscription(
            self.test_command, process_name
        )
        self.assertIsInstance(payload, str)
        self.assertIn("__InstanceCreationEvent", payload)
        self.assertIn("Win32_Process", payload)
        self.assertIn(process_name, payload)
        self.assertIn(self.test_command, payload)

    def test_encoded_subscription_base64(self):
        """Test Base64-encoded event subscription"""
        payload = self.subscription.generate_encoded_event_subscription(
            self.test_command, encoding="base64"
        )
        self.assertIsInstance(payload, str)
        self.assertIn("DecodeBase64Cmd", payload)
        # Command should be Base64 encoded
        encoded_cmd = base64.b64encode(self.test_command.encode()).decode()
        self.assertIn(encoded_cmd, payload)

    def test_encoded_subscription_hex(self):
        """Test Hex-encoded event subscription"""
        payload = self.subscription.generate_encoded_event_subscription(
            self.test_command, encoding="hex"
        )
        self.assertIsInstance(payload, str)
        self.assertIn("DecodeHexCmd", payload)
        # Command should be Hex encoded
        encoded_cmd = self.test_command.encode().hex()
        self.assertIn(encoded_cmd, payload)

    def test_powershell_event_subscription(self):
        """Test PowerShell-based event subscription"""
        payload = self.subscription.generate_powershell_event_subscription(
            self.test_command
        )
        self.assertIsInstance(payload, str)
        self.assertIn("New-Object", payload)
        self.assertIn("CommandLineEventConsumer", payload)
        self.assertIn(self.test_command, payload)

    def test_event_subscription_removal(self):
        """Test event subscription removal code generation"""
        payload = self.subscription.generate_event_subscription_removal()
        self.assertIsInstance(payload, str)
        self.assertIn("__FilterToConsumerBinding", payload)
        self.assertIn("__EventFilter", payload)
        self.assertIn("CommandLineEventConsumer", payload)


class TestEventFilterWQL(unittest.TestCase):
    """Test WQL filter generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.subscription = create_event_subscription()

    def test_process_start_wql(self):
        """Test process start WQL generation"""
        wql = self.subscription.generate_event_filter_wql(EventTriggerType.PROCESS_START)
        self.assertIn("__InstanceCreationEvent", wql)
        self.assertIn("Win32_Process", wql)

    def test_process_stop_wql(self):
        """Test process stop WQL generation"""
        wql = self.subscription.generate_event_filter_wql(EventTriggerType.PROCESS_STOP)
        self.assertIn("__InstanceDeletionEvent", wql)
        self.assertIn("Win32_Process", wql)

    def test_service_start_wql(self):
        """Test service start WQL generation"""
        wql = self.subscription.generate_event_filter_wql(EventTriggerType.SERVICE_START)
        self.assertIn("__InstanceModificationEvent", wql)
        self.assertIn("Win32_Service", wql)

    def test_service_stop_wql(self):
        """Test service stop WQL generation"""
        wql = self.subscription.generate_event_filter_wql(EventTriggerType.SERVICE_STOP)
        self.assertIn("__InstanceModificationEvent", wql)
        self.assertIn("Win32_Service", wql)

    def test_timer_event_wql(self):
        """Test timer event WQL generation"""
        wql = self.subscription.generate_event_filter_wql(EventTriggerType.WMI_CONSUMER_TIMER)
        self.assertIn("__TimerEvent", wql)

    def test_network_config_wql(self):
        """Test network adapter config WQL generation"""
        wql = self.subscription.generate_event_filter_wql(
            EventTriggerType.NETWORK_ADAPTER_CONFIG
        )
        self.assertIn("Win32_NetworkAdapterConfiguration", wql)

    def test_user_login_wql(self):
        """Test user login WQL generation"""
        wql = self.subscription.generate_event_filter_wql(EventTriggerType.USER_LOGIN)
        self.assertIn("Win32_LogonSession", wql)

    def test_registry_change_wql(self):
        """Test registry change WQL generation"""
        wql = self.subscription.generate_event_filter_wql(EventTriggerType.REGISTRY_CHANGE)
        self.assertIn("RegistryKeyChangeEvent", wql)


class TestHighLevelAPI(unittest.TestCase):
    """Test high-level API functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_command = "powershell.exe"

    def test_generate_process_subscription(self):
        """Test process subscription via high-level API"""
        payload = generate_event_subscription_payload(self.test_command, "process")
        self.assertIsInstance(payload, str)
        self.assertIn("__EventFilter", payload)

    def test_generate_service_subscription(self):
        """Test service subscription via high-level API"""
        payload = generate_event_subscription_payload(
            self.test_command, "service", service_name="WinRM"
        )
        self.assertIsInstance(payload, str)
        self.assertIn("Win32_Service", payload)

    def test_generate_timer_subscription(self):
        """Test timer subscription via high-level API"""
        payload = generate_event_subscription_payload(
            self.test_command, "timer", interval=60000
        )
        self.assertIsInstance(payload, str)
        self.assertIn("__TimerEvent", payload)

    def test_generate_trigger_subscription(self):
        """Test trigger subscription via high-level API"""
        payload = generate_event_subscription_payload(
            self.test_command, "trigger", process_name="explorer.exe"
        )
        self.assertIsInstance(payload, str)
        self.assertIn("Win32_Process", payload)

    def test_generate_encoded_subscription(self):
        """Test encoded subscription via high-level API"""
        payload = generate_event_subscription_payload(
            self.test_command, "encoded", encoding="base64"
        )
        self.assertIsInstance(payload, str)
        self.assertIn("DecodeBase64Cmd", payload)

    def test_generate_async_handler(self):
        """Test async handler via high-level API"""
        payload = generate_event_subscription_payload(self.test_command, "async")
        self.assertIsInstance(payload, str)
        self.assertIn("Class", payload)

    def test_generate_powershell_subscription(self):
        """Test PowerShell subscription via high-level API"""
        payload = generate_event_subscription_payload(self.test_command, "powershell")
        self.assertIsInstance(payload, str)
        self.assertIn("New-Object", payload)


class TestObfuscation(unittest.TestCase):
    """Test obfuscation features"""

    def test_variable_name_obfuscation(self):
        """Test that variable names are obfuscated"""
        config = EventSubscriptionConfig(obfuscate_names=True)
        subscription = WMIEventSubscription(config)
        payload = subscription.generate_event_subscription_vbs("cmd.exe")

        # Check that payload contains randomized variable names
        # They should contain underscores and letters
        self.assertIn("_", payload)

    def test_variable_name_no_obfuscation(self):
        """Test that variable names can be plain"""
        config = EventSubscriptionConfig(obfuscate_names=False)
        subscription = WMIEventSubscription(config)
        payload = subscription.generate_event_subscription_vbs("cmd.exe")

        # Should contain standard prefixes
        self.assertIn("Dim", payload)

    def test_encoded_command_obfuscation(self):
        """Test that commands can be encoded for obfuscation"""
        subscription = create_event_subscription()
        command = "calc.exe"

        # Base64 encoding
        payload_b64 = subscription.generate_encoded_event_subscription(
            command, EventTriggerType.PROCESS_START, "base64"
        )
        encoded_cmd = base64.b64encode(command.encode()).decode()
        self.assertIn(encoded_cmd, payload_b64)
        self.assertNotIn(command, payload_b64)  # Command not in plain text

        # Hex encoding
        payload_hex = subscription.generate_encoded_event_subscription(
            command, EventTriggerType.PROCESS_START, "hex"
        )
        # Hex version should have decoder function and not plain text command
        self.assertIn("DecodeHexCmd", payload_hex)
        self.assertNotIn(command, payload_hex)  # Command not in plain text


class TestEventHandlerSummary(unittest.TestCase):
    """Test event handler summary generation"""

    def test_handler_summary(self):
        """Test that handler summary contains all handler types"""
        subscription = create_event_subscription()
        summary = subscription.generate_event_handler_summary()

        self.assertIsInstance(summary, dict)
        self.assertIn("event_subscription", summary)
        self.assertIn("async_handler", summary)
        self.assertIn("timer_consumer", summary)
        self.assertIn("service_startup", summary)
        self.assertIn("encoded_subscription", summary)

    def test_handler_summary_structure(self):
        """Test that each handler has required fields"""
        subscription = create_event_subscription()
        summary = subscription.generate_event_handler_summary()

        required_fields = ["name", "description", "trigger", "persistence"]
        for handler_key, handler_info in summary.items():
            for field in required_fields:
                self.assertIn(field, handler_info)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios"""

    def test_command_with_special_characters(self):
        """Test command with special characters"""
        subscription = create_event_subscription()
        command = 'cmd.exe /c echo "test & special" > file.txt'
        payload = subscription.generate_event_subscription_vbs(command)
        self.assertIsInstance(payload, str)
        self.assertIn(command, payload)

    def test_very_long_command(self):
        """Test very long command"""
        subscription = create_event_subscription()
        command = "cmd.exe /c " + "a" * 500
        payload = subscription.generate_event_subscription_vbs(command)
        self.assertIsInstance(payload, str)
        self.assertIn(command, payload)

    def test_multiple_subscriptions(self):
        """Test creating multiple subscriptions"""
        subscription1 = create_event_subscription()
        subscription2 = create_event_subscription()

        payload1 = subscription1.generate_event_subscription_vbs("cmd.exe")
        payload2 = subscription2.generate_event_subscription_vbs("powershell.exe")

        self.assertNotEqual(payload1, payload2)
        self.assertIn("cmd.exe", payload1)
        self.assertIn("powershell.exe", payload2)

    def test_zero_interval_timer(self):
        """Test timer with very small interval"""
        subscription = create_event_subscription()
        payload = subscription.generate_timer_event_consumer("cmd.exe", 100)
        self.assertIsInstance(payload, str)
        self.assertIn("100", payload)

    def test_large_interval_timer(self):
        """Test timer with large interval"""
        subscription = create_event_subscription()
        payload = subscription.generate_timer_event_consumer("cmd.exe", 86400000)  # 24 hours
        self.assertIsInstance(payload, str)
        self.assertIn("86400000", payload)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
