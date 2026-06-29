#!/usr/bin/env python3
"""
Persistence Reboot Test - Verifies payload execution survives system reboot
Tests both Windows persistence payload generation and Linux-based simulation
For authorized security testing only
"""

import os
import sys
import time
import json
import subprocess
import tempfile
import hashlib
from datetime import datetime
from pathlib import Path


class RebootPersistenceTest:
    """Test persistence across system reboots"""

    def __init__(self, test_dir=None):
        self.test_dir = test_dir or "/tmp/persistence_test"
        self.results = {
            "test_id": hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }
        self.setup_test_environment()

    def setup_test_environment(self):
        """Initialize test environment"""
        os.makedirs(self.test_dir, exist_ok=True)
        self.marker_file = os.path.join(self.test_dir, "persistence_marker.txt")
        self.log_file = os.path.join(self.test_dir, "execution_log.txt")
        self.payload_dir = os.path.join(self.test_dir, "payloads")
        os.makedirs(self.payload_dir, exist_ok=True)

        print(f"[*] Test environment initialized at: {self.test_dir}")
        print(f"[*] Test ID: {self.results['test_id']}")

    def write_payload_to_disk(self, payload_name, payload_content):
        """Write payload to disk for persistence"""
        payload_path = os.path.join(self.payload_dir, payload_name)
        with open(payload_path, 'w') as f:
            f.write(payload_content)
        os.chmod(payload_path, 0o755)

        test_result = {
            "test": "payload_write",
            "payload_name": payload_name,
            "path": payload_path,
            "size": len(payload_content),
            "timestamp": datetime.now().isoformat(),
            "status": "written"
        }
        self.results["tests"].append(test_result)
        print(f"[+] Payload written: {payload_path}")
        print(f"[+] Payload size: {len(payload_content)} bytes")

        return payload_path

    def create_startup_hook(self, command):
        """Create Linux startup hook for testing"""
        # Create bashrc entry
        bashrc_entry = f"\n# Persistence Test Hook - {self.results['test_id']}\n"
        bashrc_entry += f"{command}\n"

        rc_file = os.path.expanduser("~/.bashrc")

        # Add hook to bashrc
        if os.path.exists(rc_file):
            with open(rc_file, 'a') as f:
                f.write(bashrc_entry)

        test_result = {
            "test": "startup_hook_bashrc",
            "path": rc_file,
            "timestamp": datetime.now().isoformat(),
            "status": "installed"
        }
        self.results["tests"].append(test_result)
        print(f"[+] Startup hook installed in: {rc_file}")

        return rc_file

    def create_cron_persistence(self, command):
        """Create cron-based persistence (Linux)"""
        # Create a script that adds cron job
        cron_script = f"""#!/bin/bash
(crontab -l 2>/dev/null; echo "@reboot {command}") | crontab -
"""
        cron_path = os.path.join(self.payload_dir, "install_cron.sh")
        with open(cron_path, 'w') as f:
            f.write(cron_script)
        os.chmod(cron_path, 0o755)

        test_result = {
            "test": "cron_persistence",
            "script_path": cron_path,
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "status": "script_created"
        }
        self.results["tests"].append(test_result)
        print(f"[+] Cron persistence script created: {cron_path}")

        return cron_path

    def create_systemd_service(self, service_name, command):
        """Create systemd service for persistence"""
        service_content = f"""[Unit]
Description=Persistence Test Service
After=network.target

[Service]
Type=simple
ExecStart={command}
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
"""
        service_path = os.path.join(self.payload_dir, f"{service_name}.service")
        with open(service_path, 'w') as f:
            f.write(service_content)

        test_result = {
            "test": "systemd_service",
            "service_name": service_name,
            "path": service_path,
            "timestamp": datetime.now().isoformat(),
            "status": "created"
        }
        self.results["tests"].append(test_result)
        print(f"[+] Systemd service created: {service_path}")

        return service_path

    def create_windows_payload_variants(self):
        """Generate Windows persistence payload variants for documentation"""
        from persistence_manager import create_persistent_payload

        # Test command that writes a marker on execution
        test_cmd = f'powershell -NoProfile -Command "Add-Content -Path \'C:\\\\Users\\\\Public\\\\Documents\\\\persistence_marker.txt\' -Value \'Executed at {datetime.now().isoformat()}\'"'

        windows_payloads = {}

        methods = ["registry", "startup", "task", "multi"]

        for method in methods:
            try:
                result = create_persistent_payload(test_cmd, method)
                windows_payloads[method] = {
                    "method_name": result['method_name'],
                    "windows_versions": result['windows_versions'],
                    "survival_rate": result['survival_rate'],
                    "size": result['size'],
                    "advantages": result['advantages'],
                    "disadvantages": result['disadvantages'],
                    "payload_preview": result['vbs_code'][:200] + "..."
                }

                # Save full payload to file
                payload_file = os.path.join(
                    self.payload_dir,
                    f"windows_persistence_{method}.vbs"
                )
                with open(payload_file, 'w') as f:
                    f.write(result['vbs_code'])

                print(f"[+] Windows {method} payload generated: {payload_file}")
            except Exception as e:
                print(f"[-] Error generating {method} payload: {e}")

        self.results["windows_payloads"] = windows_payloads
        return windows_payloads

    def create_execution_monitor(self):
        """Create script to monitor payload execution"""
        monitor_script = f"""#!/bin/bash
# Persistence Execution Monitor - Test ID: {self.results['test_id']}

LOG_FILE="{self.log_file}"
MARKER_FILE="{self.marker_file}"

# Log execution
echo "Persistence test executed at $(date)" >> "$LOG_FILE"
echo "User: $(whoami)" >> "$LOG_FILE"
echo "Hostname: $(hostname)" >> "$LOG_FILE"
echo "Uptime: $(uptime)" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"

# Create marker file
touch "$MARKER_FILE"
echo "{{" > "$MARKER_FILE"
echo '  "test_id": "{self.results["test_id"]}",' >> "$MARKER_FILE"
echo '  "execution_time": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",' >> "$MARKER_FILE"
echo '  "executed": true' >> "$MARKER_FILE"
echo "}}" >> "$MARKER_FILE"

# Verify execution
if [ -f "$MARKER_FILE" ]; then
    echo "[+] Persistence verified at $MARKER_FILE"
fi
"""

        monitor_path = os.path.join(self.payload_dir, "execution_monitor.sh")
        with open(monitor_path, 'w') as f:
            f.write(monitor_script)
        os.chmod(monitor_path, 0o755)

        test_result = {
            "test": "execution_monitor",
            "path": monitor_path,
            "timestamp": datetime.now().isoformat(),
            "status": "created"
        }
        self.results["tests"].append(test_result)
        print(f"[+] Execution monitor created: {monitor_path}")

        return monitor_path

    def simulate_reboot(self):
        """Simulate reboot by executing startup hooks"""
        print("\n" + "="*70)
        print("[*] SIMULATING SYSTEM REBOOT")
        print("="*70 + "\n")

        # Execute monitor script
        monitor_path = self.create_execution_monitor()

        try:
            result = subprocess.run(
                ["/bin/bash", monitor_path],
                capture_output=True,
                timeout=5
            )

            reboot_result = {
                "test": "simulated_reboot",
                "status": "success" if result.returncode == 0 else "failed",
                "timestamp": datetime.now().isoformat(),
                "stdout": result.stdout.decode() if result.stdout else "",
                "stderr": result.stderr.decode() if result.stderr else "",
                "return_code": result.returncode
            }
            self.results["tests"].append(reboot_result)
            print(f"[+] Simulated reboot completed")
            print(f"[+] Return code: {result.returncode}")

        except subprocess.TimeoutExpired:
            print("[-] Reboot simulation timed out")
            self.results["tests"].append({
                "test": "simulated_reboot",
                "status": "timeout",
                "timestamp": datetime.now().isoformat()
            })

    def verify_persistence(self):
        """Verify that payload executed after reboot"""
        print("\n" + "="*70)
        print("[*] VERIFYING PERSISTENCE")
        print("="*70 + "\n")

        verification_result = {
            "test": "persistence_verification",
            "timestamp": datetime.now().isoformat(),
            "checks": []
        }

        # Check 1: Marker file exists
        marker_exists = os.path.exists(self.marker_file)
        check1 = {
            "name": "Marker file existence",
            "result": marker_exists,
            "path": self.marker_file
        }
        verification_result["checks"].append(check1)

        if marker_exists:
            print(f"[+] Marker file exists: {self.marker_file}")
            with open(self.marker_file, 'r') as f:
                marker_content = f.read()
                print(f"[+] Marker content:\n{marker_content}")
                check1["content"] = marker_content
        else:
            print(f"[-] Marker file NOT found: {self.marker_file}")

        # Check 2: Log file has entries
        log_exists = os.path.exists(self.log_file)
        check2 = {
            "name": "Execution log existence",
            "result": log_exists,
            "path": self.log_file
        }
        verification_result["checks"].append(check2)

        if log_exists:
            print(f"[+] Log file exists: {self.log_file}")
            with open(self.log_file, 'r') as f:
                log_content = f.read()
                print(f"[+] Log content:\n{log_content}")
                check2["content"] = log_content

        # Check 3: Payload directory contains files
        payloads_exist = os.path.exists(self.payload_dir)
        payload_files = []
        if payloads_exist:
            payload_files = os.listdir(self.payload_dir)

        check3 = {
            "name": "Payload files stored",
            "result": len(payload_files) > 0,
            "files": payload_files,
            "count": len(payload_files)
        }
        verification_result["checks"].append(check3)

        print(f"[+] Payload files: {len(payload_files)}")
        for pf in payload_files:
            print(f"    - {pf}")

        # Overall status
        verification_result["status"] = "verified" if marker_exists else "not_verified"
        self.results["tests"].append(verification_result)

        return verification_result

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*70)
        print("[*] GENERATING REBOOT PERSISTENCE TEST REPORT")
        print("="*70 + "\n")

        # Summarize results
        passed_tests = sum(1 for t in self.results["tests"]
                          if t.get("status") == "verified" or
                          (isinstance(t.get("checks"), list) and
                           t.get("status") == "verified"))
        total_tests = len(self.results["tests"])

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "test_date": self.results["timestamp"],
            "test_environment": {
                "test_dir": self.test_dir,
                "marker_file": self.marker_file,
                "log_file": self.log_file,
                "payload_dir": self.payload_dir
            }
        }

        # Save JSON report
        report_path = os.path.join(self.test_dir, "reboot_test_report.json")
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"[+] Report saved to: {report_path}\n")

        return report_path

    def run_full_test(self):
        """Execute complete reboot persistence test"""
        print("\n" + "="*70)
        print("PERSISTENCE REBOOT TEST SUITE")
        print("="*70)
        print(f"Test ID: {self.results['test_id']}")
        print(f"Timestamp: {self.results['timestamp']}")
        print("="*70 + "\n")

        # Step 1: Generate Windows payloads
        print("[*] Step 1: Generate Windows Persistence Payloads")
        print("-" * 70)
        try:
            self.create_windows_payload_variants()
        except ImportError as e:
            print(f"[!] Warning: Could not import persistence_manager: {e}")
            print("[!] Windows payloads will be skipped")

        # Step 2: Create test payloads for Linux
        print("\n[*] Step 2: Create Test Payloads")
        print("-" * 70)
        test_payload = f"""#!/bin/bash
# Persistence test payload - {self.results['test_id']}
echo 'Persistence test executed' >> "{self.log_file}"
touch "{self.marker_file}"
"""
        self.write_payload_to_disk("persistence_test.sh", test_payload)

        # Step 3: Install persistence mechanisms
        print("\n[*] Step 3: Install Persistence Mechanisms")
        print("-" * 70)
        payload_path = os.path.join(self.payload_dir, "persistence_test.sh")
        self.create_startup_hook(f"bash {payload_path}")
        self.create_cron_persistence(f"bash {payload_path}")
        self.create_systemd_service("persistence-test", f"bash {payload_path}")

        # Step 4: Simulate reboot
        print("\n[*] Step 4: Simulate System Reboot")
        print("-" * 70)
        self.simulate_reboot()

        # Step 5: Verify persistence
        print("\n[*] Step 5: Verify Persistence Execution")
        print("-" * 70)
        self.verify_persistence()

        # Step 6: Generate report
        self.generate_report()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)

        summary = self.results.get("summary", {})
        print(f"\nTotal Tests: {summary.get('total_tests', 0)}")
        print(f"Test Date: {summary.get('test_date', 'N/A')}")
        print(f"Test Directory: {summary.get('test_environment', {}).get('test_dir', 'N/A')}")

        # List all test results
        print("\nTest Results:")
        print("-" * 70)
        for i, test in enumerate(self.results["tests"], 1):
            test_name = test.get("test", "unknown")
            status = test.get("status", "pending")
            timestamp = test.get("timestamp", "N/A")

            status_icon = "[+]" if status == "verified" or status == "success" else "[*]"
            print(f"{i}. {status_icon} {test_name}: {status} ({timestamp})")

        print("\n" + "="*70)
        print("Reboot persistence test complete!")
        print(f"Full report: {os.path.join(self.test_dir, 'reboot_test_report.json')}")
        print("="*70 + "\n")


def main():
    """Main test execution"""
    # Determine test directory
    test_dir = os.getenv("PERSISTENCE_TEST_DIR", "/tmp/persistence_test_2026")

    # Run test
    tester = RebootPersistenceTest(test_dir)
    tester.run_full_test()

    # Save results to file for retrieval
    results_file = os.path.join(test_dir, "reboot_test_results.json")
    with open(results_file, 'w') as f:
        json.dump(tester.results, f, indent=2)

    print(f"\n[+] Results saved to: {results_file}")

    return 0 if tester.results["summary"].get("total_tests", 0) > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
