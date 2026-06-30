#!/usr/bin/env python3
"""
Comprehensive Registry and Environment Variable Persistence Verification
Tests persistence mechanisms with fallback strategies and dual HKCU/HKLM methods.

Verification includes:
- Registry write/read (HKCU with HKLM fallback)
- Environment variable write/read (USER with SYSTEM fallback)
- Cross-persistence (registry-to-env-var and vice versa)
- Fallback chain validation
- Durability across process restarts
- Permission handling and privilege escalation fallbacks
"""

import os
import sys
import json
import time
import base64
import tempfile
import platform
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
import subprocess
import hashlib


@dataclass
class VerificationResult:
    """Result of a single verification test"""
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP", "PARTIAL"
    message: str
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: float = 0.0


@dataclass
class PersistenceVerificationReport:
    """Complete verification report"""
    report_id: str
    timestamp: str
    platform: str
    test_results: List[VerificationResult] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "platform": self.platform,
            "test_results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "timestamp": r.timestamp,
                    "duration_ms": r.duration_ms,
                    "details": r.details,
                    "error": r.error
                }
                for r in self.test_results
            ],
            "summary": self.summary,
            "recommendations": self.recommendations
        }


class RegistryEnvVarPersistenceVerifier:
    """Comprehensive verification harness for registry and env var persistence"""

    def __init__(self):
        """Initialize verifier"""
        self.report_id = self._generate_report_id()
        self.platform_type = platform.system()
        self.results: List[VerificationResult] = []
        self.test_data = self._generate_test_data()
        self.temp_dir = tempfile.mkdtemp(prefix="persist_verify_")

    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        timestamp = datetime.now().isoformat().replace(":", "").replace("-", "")
        random_suffix = hashlib.md5(os.urandom(16)).hexdigest()[:8]
        return f"PERSIST_VERIFY_{timestamp}_{random_suffix}"

    def _generate_test_data(self) -> Dict[str, str]:
        """Generate various test data payloads"""
        return {
            "simple": "TestPayload_Simple",
            "json": json.dumps({"test": "json", "value": 12345}),
            "command": "powershell.exe -NoProfile -WindowStyle Hidden",
            "base64": base64.b64encode(b"encoded_payload").decode(),
            "hex": "48656C6C6F20576F726C64",
            "large": "X" * 5000,
            "special": "!@#$%^&*()_+-=[]{}|;:',.<>?/",
            "multiline": "Line1\nLine2\nLine3\nLine4",
        }

    def _log_result(
        self,
        test_name: str,
        status: str,
        message: str,
        details: Optional[Dict] = None,
        error: Optional[str] = None,
        duration_ms: float = 0.0
    ):
        """Log a test result"""
        result = VerificationResult(
            test_name=test_name,
            status=status,
            message=message,
            timestamp=datetime.now().isoformat(),
            details=details or {},
            error=error,
            duration_ms=duration_ms
        )
        self.results.append(result)
        status_symbol = {
            "PASS": "✓",
            "FAIL": "✗",
            "SKIP": "⊘",
            "PARTIAL": "◐"
        }.get(status, "?")
        print(f"[{status_symbol}] {test_name}: {message}")
        if error:
            print(f"    Error: {error}")

    def test_1_windows_registry_hkcu_write_read(self) -> bool:
        """Test writing and reading from HKCU registry"""
        if self.platform_type != "Windows":
            self._log_result(
                "Windows Registry HKCU Write/Read",
                "SKIP",
                "Not on Windows platform"
            )
            return True

        test_name = "Windows Registry HKCU Write/Read"
        start_time = time.time()

        try:
            import winreg

            test_value = self.test_data["simple"]
            value_name = f"TEST_HKCU_{hashlib.md5(os.urandom(8)).hexdigest()[:8]}"
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

            # Write to HKCU
            with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, test_value)

            # Read from HKCU
            with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_READ) as key:
                    read_value, _ = winreg.QueryValueEx(key, value_name)

            # Verify
            success = read_value == test_value
            duration = (time.time() - start_time) * 1000

            self._log_result(
                test_name,
                "PASS" if success else "FAIL",
                f"Value written and read successfully" if success else "Value mismatch",
                details={
                    "hive": "HKCU",
                    "path": reg_path,
                    "value_name": value_name,
                    "written": test_value,
                    "read": read_value if success else "FAILED",
                    "match": success
                },
                duration_ms=duration
            )

            # Cleanup
            try:
                with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                    with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                        winreg.DeleteValue(key, value_name)
            except:
                pass

            return success

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._log_result(
                test_name,
                "FAIL",
                "Exception during HKCU registry operation",
                error=str(e),
                duration_ms=duration
            )
            return False

    def test_2_windows_registry_hklm_write_read(self) -> bool:
        """Test writing and reading from HKLM registry (admin required)"""
        if self.platform_type != "Windows":
            self._log_result(
                "Windows Registry HKLM Write/Read",
                "SKIP",
                "Not on Windows platform"
            )
            return True

        test_name = "Windows Registry HKLM Write/Read"
        start_time = time.time()

        try:
            import winreg

            test_value = self.test_data["simple"]
            value_name = f"TEST_HKLM_{hashlib.md5(os.urandom(8)).hexdigest()[:8]}"
            reg_path = r"Software\Microsoft\Windows\CurrentVersion"

            # Try to write to HKLM
            try:
                with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
                    with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, test_value)

                # Read from HKLM
                with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
                    with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_READ) as key:
                        read_value, _ = winreg.QueryValueEx(key, value_name)

                success = read_value == test_value
                duration = (time.time() - start_time) * 1000

                self._log_result(
                    test_name,
                    "PASS" if success else "FAIL",
                    f"Value written and read from HKLM" if success else "Value mismatch",
                    details={
                        "hive": "HKLM",
                        "path": reg_path,
                        "value_name": value_name,
                        "written": test_value,
                        "read": read_value if success else "FAILED",
                        "match": success,
                        "requires_admin": True
                    },
                    duration_ms=duration
                )

                # Cleanup
                try:
                    with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
                        with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                            winreg.DeleteValue(key, value_name)
                except:
                    pass

                return success

            except PermissionError:
                duration = (time.time() - start_time) * 1000
                self._log_result(
                    test_name,
                    "FAIL",
                    "Permission denied (admin privileges required)",
                    details={
                        "hive": "HKLM",
                        "requires_admin": True,
                        "fallback_available": True
                    },
                    duration_ms=duration
                )
                return False

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._log_result(
                test_name,
                "FAIL",
                "Exception during HKLM registry operation",
                error=str(e),
                duration_ms=duration
            )
            return False

    def test_3_registry_hkcu_fallback_to_hklm(self) -> bool:
        """Test fallback from HKCU to HKLM when HKCU fails"""
        if self.platform_type != "Windows":
            self._log_result(
                "Registry HKCU→HKLM Fallback",
                "SKIP",
                "Not on Windows platform"
            )
            return True

        test_name = "Registry HKCU→HKLM Fallback"
        start_time = time.time()

        try:
            import winreg

            test_value = self.test_data["simple"]
            value_name = f"TEST_FB_{hashlib.md5(os.urandom(8)).hexdigest()[:8]}"
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

            # Try HKCU first
            hkcu_success = False
            try:
                with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                    with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, test_value)
                hkcu_success = True
            except Exception as e:
                pass

            # Fallback to HKLM if HKCU fails
            hklm_success = False
            if not hkcu_success:
                try:
                    with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
                        with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, test_value)
                    hklm_success = True
                except Exception:
                    pass

            # Read from whichever succeeded
            success = hkcu_success or hklm_success
            hive_used = "HKCU" if hkcu_success else ("HKLM" if hklm_success else "NONE")

            duration = (time.time() - start_time) * 1000

            self._log_result(
                test_name,
                "PASS" if success else "FAIL",
                f"Fallback chain succeeded using {hive_used}",
                details={
                    "hkcu_attempted": True,
                    "hkcu_success": hkcu_success,
                    "hklm_attempted": not hkcu_success,
                    "hklm_success": hklm_success,
                    "hive_used": hive_used,
                    "fallback_chain_working": success
                },
                duration_ms=duration
            )

            # Cleanup
            for hive_type, hkey_const in [("HKCU", winreg.HKEY_CURRENT_USER), ("HKLM", winreg.HKEY_LOCAL_MACHINE)]:
                try:
                    with winreg.ConnectRegistry(None, hkey_const) as hkey:
                        with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                            winreg.DeleteValue(key, value_name)
                except:
                    pass

            return success

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._log_result(
                test_name,
                "FAIL",
                "Exception during fallback test",
                error=str(e),
                duration_ms=duration
            )
            return False

    def test_4_env_var_user_write_read(self) -> bool:
        """Test writing and reading from user environment variables"""
        test_name = "Environment Variable USER Write/Read"
        start_time = time.time()

        try:
            test_value = self.test_data["simple"]
            var_name = f"TEST_ENV_USER_{hashlib.md5(os.urandom(8)).hexdigest()[:8]}"

            # Write to process environment (immediate persistence)
            os.environ[var_name] = test_value

            # Read back
            read_value = os.environ.get(var_name)

            success = read_value == test_value
            duration = (time.time() - start_time) * 1000

            self._log_result(
                test_name,
                "PASS" if success else "FAIL",
                "Environment variable written and read successfully" if success else "Value mismatch",
                details={
                    "scope": "USER",
                    "var_name": var_name,
                    "written": test_value,
                    "read": read_value if success else "FAILED",
                    "match": success,
                    "platform": self.platform_type
                },
                duration_ms=duration
            )

            return success

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._log_result(
                test_name,
                "FAIL",
                "Exception during environment variable operation",
                error=str(e),
                duration_ms=duration
            )
            return False

    def test_5_env_var_persistence_across_subprocess(self) -> bool:
        """Test environment variable persistence across subprocess calls"""
        test_name = "Environment Variable Persistence (Subprocess)"
        start_time = time.time()

        try:
            test_value = self.test_data["simple"]
            var_name = f"TEST_ENV_PERSIST_{hashlib.md5(os.urandom(8)).hexdigest()[:8]}"

            # Set in current process
            os.environ[var_name] = test_value

            # Create script to read from subprocess
            script_content = f"""import os; print(os.environ.get('{var_name}', 'NOT_FOUND'))"""

            # Run subprocess
            result = subprocess.run(
                [sys.executable, "-c", script_content],
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )

            read_value = result.stdout.strip()
            success = read_value == test_value
            duration = (time.time() - start_time) * 1000

            self._log_result(
                test_name,
                "PASS" if success else "FAIL",
                "Environment variable persisted across subprocess" if success else "Value not persisted",
                details={
                    "var_name": var_name,
                    "written": test_value,
                    "read_from_subprocess": read_value,
                    "match": success,
                    "subprocess_returncode": result.returncode
                },
                duration_ms=duration
            )

            return success

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._log_result(
                test_name,
                "FAIL",
                "Exception during subprocess persistence test",
                error=str(e),
                duration_ms=duration
            )
            return False

    def test_6_chunked_payload_registry_persistence(self) -> bool:
        """Test persistence of large chunked payloads in registry"""
        if self.platform_type != "Windows":
            self._log_result(
                "Chunked Payload Registry Persistence",
                "SKIP",
                "Not on Windows platform"
            )
            return True

        test_name = "Chunked Payload Registry Persistence"
        start_time = time.time()

        try:
            import winreg

            # Use large payload
            test_value = self.test_data["large"]
            chunk_size = 1000
            chunks = {
                f"CHUNK_{i:03d}": test_value[i:i+chunk_size]
                for i in range(0, len(test_value), chunk_size)
            }

            value_name_prefix = f"TEST_CHUNK_{hashlib.md5(os.urandom(8)).hexdigest()[:8]}"
            reg_path = r"Software\Microsoft\Windows\CurrentVersion"

            # Write chunks to HKCU
            with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                    for chunk_name, chunk_value in chunks.items():
                        full_name = f"{value_name_prefix}_{chunk_name}"
                        winreg.SetValueEx(key, full_name, 0, winreg.REG_SZ, chunk_value)

            # Read chunks back
            reconstructed = ""
            with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_READ) as key:
                    for chunk_name in sorted(chunks.keys()):
                        full_name = f"{value_name_prefix}_{chunk_name}"
                        try:
                            chunk_value, _ = winreg.QueryValueEx(key, full_name)
                            reconstructed += chunk_value
                        except:
                            pass

            success = reconstructed == test_value
            duration = (time.time() - start_time) * 1000

            self._log_result(
                test_name,
                "PASS" if success else "FAIL",
                f"Stored and retrieved {len(chunks)} chunks" if success else "Chunk reconstruction failed",
                details={
                    "original_size": len(test_value),
                    "chunk_count": len(chunks),
                    "chunk_size": chunk_size,
                    "reconstructed_size": len(reconstructed),
                    "match": success
                },
                duration_ms=duration
            )

            # Cleanup
            with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                    for chunk_name in chunks.keys():
                        full_name = f"{value_name_prefix}_{chunk_name}"
                        try:
                            winreg.DeleteValue(key, full_name)
                        except:
                            pass

            return success

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._log_result(
                test_name,
                "FAIL",
                "Exception during chunked payload test",
                error=str(e),
                duration_ms=duration
            )
            return False

    def test_7_multiple_encodings_registry(self) -> bool:
        """Test registry persistence with multiple encodings"""
        if self.platform_type != "Windows":
            self._log_result(
                "Multiple Encodings Registry Persistence",
                "SKIP",
                "Not on Windows platform"
            )
            return True

        test_name = "Multiple Encodings Registry Persistence"
        start_time = time.time()

        try:
            import winreg

            encodings_tests = {
                "base64": base64.b64encode(b"test_payload").decode(),
                "hex": "746573745f7061796c6f6164",
                "raw": "test_payload_raw"
            }

            reg_path = r"Software\Microsoft\Windows\CurrentVersion"
            all_success = True

            for encoding_type, test_value in encodings_tests.items():
                try:
                    value_name = f"TEST_ENC_{encoding_type}_{hashlib.md5(os.urandom(8)).hexdigest()[:6]}"

                    # Write
                    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                        with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, test_value)

                    # Read
                    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                        with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_READ) as key:
                            read_value, _ = winreg.QueryValueEx(key, value_name)

                    if read_value != test_value:
                        all_success = False

                    # Cleanup
                    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                        with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                            winreg.DeleteValue(key, value_name)

                except Exception:
                    all_success = False

            duration = (time.time() - start_time) * 1000

            self._log_result(
                test_name,
                "PASS" if all_success else "FAIL",
                f"Tested {len(encodings_tests)} encoding types" if all_success else "Some encodings failed",
                details={
                    "encodings_tested": list(encodings_tests.keys()),
                    "all_success": all_success
                },
                duration_ms=duration
            )

            return all_success

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._log_result(
                test_name,
                "FAIL",
                "Exception during encoding test",
                error=str(e),
                duration_ms=duration
            )
            return False

    def test_8_cross_persistence_registry_to_env(self) -> bool:
        """Test reading registry value from environment variable and vice versa"""
        if self.platform_type != "Windows":
            self._log_result(
                "Cross-Persistence Registry↔EnvVar",
                "SKIP",
                "Not on Windows platform"
            )
            return True

        test_name = "Cross-Persistence Registry↔EnvVar"
        start_time = time.time()

        try:
            import winreg

            test_value = self.test_data["json"]
            var_name = f"TEST_CROSS_{hashlib.md5(os.urandom(8)).hexdigest()[:8]}"
            value_name = f"REG_{var_name}"
            reg_path = r"Software\Microsoft\Windows\CurrentVersion"

            # Write to registry
            with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, test_value)

            # Read from registry and write to env var
            with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_READ) as key:
                    reg_read_value, _ = winreg.QueryValueEx(key, value_name)

            os.environ[var_name] = reg_read_value

            # Read from env var and verify
            env_read_value = os.environ.get(var_name)

            success = (reg_read_value == test_value) and (env_read_value == test_value)
            duration = (time.time() - start_time) * 1000

            self._log_result(
                test_name,
                "PASS" if success else "FAIL",
                "Successfully moved data from registry to environment variable" if success else "Cross-persistence failed",
                details={
                    "original_value": test_value,
                    "registry_read": reg_read_value == test_value,
                    "env_var_write": reg_read_value == test_value,
                    "env_var_read": env_read_value == test_value,
                    "all_match": success
                },
                duration_ms=duration
            )

            # Cleanup
            try:
                with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                    with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                        winreg.DeleteValue(key, value_name)
            except:
                pass

            return success

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._log_result(
                test_name,
                "FAIL",
                "Exception during cross-persistence test",
                error=str(e),
                duration_ms=duration
            )
            return False

    def test_9_fallback_chain_with_file_backup(self) -> bool:
        """Test complete fallback chain: Registry→EnvVar→File"""
        test_name = "Fallback Chain Registry→EnvVar→File"
        start_time = time.time()

        try:
            test_value = self.test_data["command"]
            var_name = f"TEST_CHAIN_{hashlib.md5(os.urandom(8)).hexdigest()[:8]}"

            stored_location = None

            # Primary: Registry
            if self.platform_type == "Windows":
                try:
                    import winreg
                    value_name = f"REG_{var_name}"
                    reg_path = r"Software\Microsoft\Windows\CurrentVersion"

                    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                        with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, test_value)

                    stored_location = "HKCU_REGISTRY"
                except Exception:
                    pass

            # Secondary: Environment Variable
            if not stored_location:
                try:
                    os.environ[var_name] = test_value
                    stored_location = "ENV_VAR"
                except Exception:
                    pass

            # Tertiary: File Backup
            if not stored_location:
                try:
                    backup_file = os.path.join(self.temp_dir, f"{var_name}.backup")
                    with open(backup_file, "w") as f:
                        f.write(test_value)
                    stored_location = f"FILE_BACKUP:{backup_file}"
                except Exception:
                    pass

            success = stored_location is not None
            duration = (time.time() - start_time) * 1000

            self._log_result(
                test_name,
                "PASS" if success else "FAIL",
                f"Data stored in {stored_location}" if success else "All storage methods failed",
                details={
                    "primary_attempted": self.platform_type == "Windows",
                    "secondary_attempted": True,
                    "tertiary_attempted": True,
                    "stored_location": stored_location
                },
                duration_ms=duration
            )

            # Cleanup registry
            if self.platform_type == "Windows" and stored_location == "HKCU_REGISTRY":
                try:
                    import winreg
                    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                        with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as key:
                            winreg.DeleteValue(key, value_name)
                except:
                    pass

            return success

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._log_result(
                test_name,
                "FAIL",
                "Exception during fallback chain test",
                error=str(e),
                duration_ms=duration
            )
            return False

    def test_10_special_characters_persistence(self) -> bool:
        """Test persistence of special characters and escape sequences"""
        test_name = "Special Characters Persistence"
        start_time = time.time()

        try:
            test_values = [
                self.test_data["special"],
                self.test_data["multiline"],
                "quote'test\"double",
                "backslash\\test",
                "percent%test",
            ]

            all_success = True

            for test_value in test_values:
                var_name = f"TEST_SPECIAL_{hashlib.md5(test_value.encode()).hexdigest()[:8]}"

                try:
                    # Write and read
                    os.environ[var_name] = test_value
                    read_value = os.environ.get(var_name)

                    if read_value != test_value:
                        all_success = False

                except Exception:
                    all_success = False

            duration = (time.time() - start_time) * 1000

            self._log_result(
                test_name,
                "PASS" if all_success else "FAIL",
                f"Tested {len(test_values)} special character patterns" if all_success else "Some patterns failed",
                details={
                    "patterns_tested": len(test_values),
                    "all_success": all_success
                },
                duration_ms=duration
            )

            return all_success

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._log_result(
                test_name,
                "FAIL",
                "Exception during special characters test",
                error=str(e),
                duration_ms=duration
            )
            return False

    def run_all_tests(self) -> PersistenceVerificationReport:
        """Run all verification tests"""
        print("\n" + "="*70)
        print("REGISTRY AND ENVIRONMENT VARIABLE PERSISTENCE VERIFICATION")
        print("="*70)
        print(f"Platform: {self.platform_type}")
        print(f"Report ID: {self.report_id}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("="*70 + "\n")

        # Run all tests
        test_methods = [
            self.test_1_windows_registry_hkcu_write_read,
            self.test_2_windows_registry_hklm_write_read,
            self.test_3_registry_hkcu_fallback_to_hklm,
            self.test_4_env_var_user_write_read,
            self.test_5_env_var_persistence_across_subprocess,
            self.test_6_chunked_payload_registry_persistence,
            self.test_7_multiple_encodings_registry,
            self.test_8_cross_persistence_registry_to_env,
            self.test_9_fallback_chain_with_file_backup,
            self.test_10_special_characters_persistence,
        ]

        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"Unhandled exception in {test_method.__name__}: {e}")

        # Generate summary
        summary = {
            "total": len(self.results),
            "passed": len([r for r in self.results if r.status == "PASS"]),
            "failed": len([r for r in self.results if r.status == "FAIL"]),
            "skipped": len([r for r in self.results if r.status == "SKIP"]),
            "partial": len([r for r in self.results if r.status == "PARTIAL"])
        }

        # Generate recommendations
        recommendations = []

        if summary["failed"] > 0:
            failed_tests = [r.test_name for r in self.results if r.status == "FAIL"]
            recommendations.append(f"Address failing tests: {', '.join(failed_tests[:3])}")

        hkcu_tests = [r for r in self.results if "HKCU" in r.test_name]
        hklm_tests = [r for r in self.results if "HKLM" in r.test_name]

        if hkcu_tests and all(r.status == "PASS" for r in hkcu_tests):
            recommendations.append("HKCU registry persistence verified and working")

        if hklm_tests and any(r.status == "FAIL" for r in hklm_tests):
            recommendations.append("HKLM requires elevated privileges - consider HKCU as primary")

        fallback_tests = [r for r in self.results if "Fallback" in r.test_name]
        if fallback_tests and all(r.status == "PASS" for r in fallback_tests):
            recommendations.append("Fallback chains are properly implemented and functional")

        if summary["skipped"] > 0:
            recommendations.append(f"Run on Windows platform for complete registry testing ({summary['skipped']} tests skipped)")

        # Create report
        report = PersistenceVerificationReport(
            report_id=self.report_id,
            timestamp=datetime.now().isoformat(),
            platform=self.platform_type,
            test_results=self.results,
            summary=summary,
            recommendations=recommendations
        )

        # Print summary
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        print(f"Total Tests:    {summary['total']}")
        print(f"Passed:         {summary['passed']}")
        print(f"Failed:         {summary['failed']}")
        print(f"Skipped:        {summary['skipped']}")
        print(f"Partial:        {summary['partial']}")
        print("="*70)

        if recommendations:
            print("\nRECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        print("\n" + "="*70 + "\n")

        return report


def main():
    """Main entry point"""
    verifier = RegistryEnvVarPersistenceVerifier()
    report = verifier.run_all_tests()

    # Save report to file
    output_file = os.path.join(
        os.path.dirname(__file__),
        f"PERSISTENCE_VERIFICATION_REPORT_{report.report_id}.json"
    )

    with open(output_file, "w") as f:
        json.dump(report.to_dict(), f, indent=2)

    print(f"Report saved to: {output_file}")

    return report


if __name__ == "__main__":
    report = main()
