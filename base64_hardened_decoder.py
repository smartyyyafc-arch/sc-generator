#!/usr/bin/env python3
"""
Hardened Base64 Decoder with Anti-Debugger and Anti-Analysis Checks
Provides Base64 decoding with resistance against static/dynamic analysis, debuggers, and sandboxes
For authorized security research and pentesting only
"""

import base64
import sys
import os
import hashlib
import time
import ctypes
import struct
from typing import Optional, Tuple
from functools import wraps


class AntiAnalysisEnvironment:
    """Detect and resist analysis/debugging environments"""

    @staticmethod
    def detect_debugger() -> bool:
        """Detect common debuggers (gdb, lldb, windbg, x64dbg, etc.)"""
        # Check for debugger environment variables
        debugger_vars = [
            'GDB_HOOK_OUTPUT',
            'LLDB_DEBUGSERVER_VERSION',
            'DEBUGGER_ACTIVE',
            '_JAVA_DEBUG',
            'DEBUG',
            'PYTHONDEVMODE'
        ]

        for var in debugger_vars:
            if os.environ.get(var):
                return True

        # Unix-specific: check if parent process is debugger
        try:
            with open('/proc/self/status', 'r') as f:
                status = f.read()
                if 'TracerPid:' in status:
                    tracer_pid = int(status.split('TracerPid:')[1].strip().split('\n')[0])
                    if tracer_pid != 0:
                        return True
        except (FileNotFoundError, PermissionError):
            pass

        # Check ptrace availability (Unix systems)
        if hasattr(ctypes, 'CDLL'):
            try:
                libc = ctypes.CDLL("libc.so.6")
                result = libc.ptrace(0, os.getpid(), 1, 0)  # PTRACE_TRACEME
                if result == -1:
                    return True
            except (OSError, AttributeError):
                pass

        return False

    @staticmethod
    def detect_virtual_machine() -> bool:
        """Detect running in VM/hypervisor (QEMU, VirtualBox, VMware, Hyper-V)"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read().lower()
                vm_signatures = ['qemu', 'kvm', 'virtualbox', 'vmware', 'xen', 'hyperv']
                if any(sig in cpuinfo for sig in vm_signatures):
                    return True
        except FileNotFoundError:
            pass

        try:
            with open('/sys/class/dmi/id/sys_vendor', 'r') as f:
                vendor = f.read().lower()
                vm_vendors = ['vmware', 'virtualbox', 'qemu', 'xen', 'microsoft', 'innotek']
                if any(vendor_sig in vendor for vendor_sig in vm_vendors):
                    return True
        except FileNotFoundError:
            pass

        return False

    @staticmethod
    def detect_sandbox() -> bool:
        """Detect common sandbox/analysis environments"""
        sandbox_indicators = [
            '/opt/cuckoo',
            '/opt/sandboxie',
            '/proc/vz',  # OpenVZ
            '/.dockerenv',
            '/.singularity',
            '/sys/fs/cgroup/docker',
        ]

        for indicator in sandbox_indicators:
            if os.path.exists(indicator):
                return True

        # Check for common sandbox environment variables
        sandbox_vars = [
            'SANDBOX_RUNTIME_MODE',
            'CUCKOO',
            'WINAPIOVERRIDE',
            'STRACE_ATTACHED',
        ]

        for var in sandbox_vars:
            if os.environ.get(var):
                return True

        return False

    @staticmethod
    def detect_instrumentation() -> bool:
        """Detect code instrumentation/monitoring tools"""
        instrumentation_indicators = [
            '/proc/sys/kernel/perf_event_paranoid',
            '/sys/kernel/debug/tracing',
        ]

        for indicator in instrumentation_indicators:
            try:
                if os.path.exists(indicator):
                    return True
            except (OSError, PermissionError):
                pass

        # Check for strace/ltrace via process name
        try:
            with open('/proc/self/cmdline', 'r') as f:
                cmdline = f.read().lower()
                if any(x in cmdline for x in ['strace', 'ltrace', 'valgrind']):
                    return True
        except FileNotFoundError:
            pass

        return False


class AntiTamperingProtection:
    """Protect against code tampering and modification"""

    def __init__(self):
        self._integrity_hash = None
        self._init_time = time.time()

    def calculate_integrity_hash(self, data: bytes) -> str:
        """Calculate SHA-256 hash for integrity verification"""
        return hashlib.sha256(data).hexdigest()

    def verify_integrity(self, data: bytes, expected_hash: str) -> bool:
        """Verify data integrity against expected hash"""
        calculated = self.calculate_integrity_hash(data)
        # Use constant-time comparison to resist timing attacks
        return self._constant_time_compare(calculated, expected_hash)

    @staticmethod
    def _constant_time_compare(a: str, b: str) -> bool:
        """Constant-time string comparison to prevent timing attacks"""
        if len(a) != len(b):
            return False
        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
        return result == 0

    def detect_runtime_modification(self, original_code: str) -> bool:
        """Detect if code has been modified at runtime"""
        current_hash = self.calculate_integrity_hash(original_code.encode())
        if self._integrity_hash is None:
            self._integrity_hash = current_hash
            return False
        return current_hash != self._integrity_hash


class AntiReversEngineering:
    """Resist reverse engineering and static analysis"""

    @staticmethod
    def obfuscate_decode_path(encoded_data: str) -> bytes:
        """Use indirect decoding path to complicate analysis"""
        # Split decoding into multiple stages
        stage1 = base64.b64decode(encoded_data)
        # Add noise operations
        stage2 = bytes([b ^ 0x00 for b in stage1])  # XOR with 0 (no-op but looks suspicious)
        return stage2

    @staticmethod
    def add_junk_code_execution():
        """Execute junk operations to complicate static analysis"""
        # These operations serve no functional purpose but add complexity
        junk_values = [
            int.from_bytes(os.urandom(4), 'big') % 1000,
            hashlib.md5(str(time.time()).encode()).hexdigest(),
            sum([x for x in range(0, 100, 2)]),
        ]
        # Use values so optimizer doesn't eliminate
        return sum([len(str(v)) for v in junk_values]) > 0

    @staticmethod
    def polymorphic_decode_engine(encoded: str) -> bytes:
        """Use polymorphic decoding to resist signature detection"""
        variants = [
            lambda x: base64.b64decode(x),
            lambda x: base64.b64decode(x.replace('\n', '').replace('\r', '')),
            lambda x: base64.b64decode(x.strip()),
        ]

        # Select variant based on input characteristics
        variant_selector = (len(encoded) ^ ord(encoded[0])) % len(variants)
        return variants[variant_selector](encoded)


class RateLimitingObfuscation:
    """Add delays to frustrate automated analysis"""

    def __init__(self, min_delay: float = 0.01, max_delay: float = 0.1):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._call_times = []

    def add_stochastic_delay(self):
        """Add probabilistic delays between operations"""
        if os.urandom(1)[0] % 3 == 0:  # 1 in 3 calls
            delay = self.min_delay + (os.urandom(1)[0] / 255.0) * (self.max_delay - self.min_delay)
            time.sleep(delay)

    def detect_analysis_speed(self) -> bool:
        """Detect if decoding is happening too fast (indicates analysis)"""
        if not self._call_times:
            self._call_times.append(time.time())
            return False

        recent_time = time.time()
        time_diff = recent_time - self._call_times[-1]

        # If operations happening faster than 1ms apart, likely being analyzed
        if time_diff < 0.001:
            return True

        self._call_times.append(recent_time)
        return False


class EnvironmentAwarenessProtection:
    """Context-aware security based on execution environment"""

    @staticmethod
    def get_execution_context() -> dict:
        """Determine execution context"""
        return {
            'is_interactive': sys.stdin.isatty() if hasattr(sys.stdin, 'isatty') else False,
            'has_argv': len(sys.argv) > 1,
            'is_main_module': __name__ == '__main__',
            'python_optimization': sys.flags.optimize,
            'has_debugger': sys.gettrace() is not None,
        }

    @staticmethod
    def enforce_production_mode():
        """Enforce production-mode constraints"""
        # Raise exception if running with optimization disabled (dev mode)
        if sys.flags.optimize == 0:
            # Could be analysis - exit gracefully or raise
            pass  # Depends on security policy


class HardenedBase64Decoder:
    """Hardened Base64 decoder with comprehensive anti-analysis protection"""

    def __init__(self, enable_anti_analysis: bool = True, strict_mode: bool = False):
        """
        Initialize hardened decoder.

        Args:
            enable_anti_analysis: Enable all anti-analysis checks
            strict_mode: Exit on any suspicious activity (dangerous in test environments)
        """
        self.enable_anti_analysis = enable_anti_analysis
        self.strict_mode = strict_mode

        self.anti_analysis = AntiAnalysisEnvironment()
        self.anti_tampering = AntiTamperingProtection()
        self.anti_reverse = AntiReversEngineering()
        self.rate_limiter = RateLimitingObfuscation()
        self.env_awareness = EnvironmentAwarenessProtection()

        self._initialized = False
        self._call_count = 0
        self._suspicious_activity_count = 0

    def _run_security_checks(self) -> Tuple[bool, list]:
        """
        Run comprehensive security checks.

        Returns:
            Tuple of (passed, threats_detected)
        """
        threats = []

        if not self.enable_anti_analysis:
            return True, threats

        # Check for debuggers
        if self.anti_analysis.detect_debugger():
            threats.append("debugger_detected")
            self._suspicious_activity_count += 1

        # Check for VMs
        if self.anti_analysis.detect_virtual_machine():
            threats.append("vm_detected")
            self._suspicious_activity_count += 1

        # Check for sandboxes
        if self.anti_analysis.detect_sandbox():
            threats.append("sandbox_detected")
            self._suspicious_activity_count += 1

        # Check for instrumentation
        if self.anti_analysis.detect_instrumentation():
            threats.append("instrumentation_detected")
            self._suspicious_activity_count += 1

        # Check for rapid analysis
        if self.rate_limiter.detect_analysis_speed():
            threats.append("rapid_analysis_detected")
            self._suspicious_activity_count += 1

        # Check execution context
        context = self.env_awareness.get_execution_context()
        if context.get('has_debugger'):
            threats.append("python_debugger_active")
            self._suspicious_activity_count += 1

        # Threshold for too much suspicion
        if self._suspicious_activity_count > 3:
            threats.append("excessive_suspicion")

        return len(threats) == 0, threats

    def _handle_threat_detection(self, threats: list):
        """
        Handle detected threats based on configuration.

        Args:
            threats: List of detected threats
        """
        if not threats:
            return

        if self.strict_mode:
            raise RuntimeError(f"Security threats detected: {threats}")

        # Log threats (in production, would log securely)
        # In non-strict mode, continue but track suspicious activity

    def decode(self, encoded_data: str, integrity_check: Optional[str] = None) -> str:
        """
        Decode Base64-encoded data with comprehensive protection.

        Args:
            encoded_data: Base64-encoded string
            integrity_check: Optional SHA-256 hash for integrity verification

        Returns:
            Decoded plaintext string

        Raises:
            ValueError: If decoding fails or tampering detected
            RuntimeError: If in strict mode and threats detected
        """
        self._call_count += 1

        # Run security checks
        passed, threats = self._run_security_checks()
        self._handle_threat_detection(threats)

        # Add stochastic delays
        self.rate_limiter.add_stochastic_delay()

        # Input validation
        if not isinstance(encoded_data, str):
            raise ValueError("Encoded data must be string")

        if len(encoded_data) == 0:
            raise ValueError("Encoded data cannot be empty")

        # Verify integrity if provided
        if integrity_check:
            if not self.anti_tampering.verify_integrity(
                encoded_data.encode(),
                integrity_check
            ):
                raise ValueError("Data integrity check failed - possible tampering")

        try:
            # Use polymorphic decoding for anti-RE
            decoded_bytes = self.anti_reverse.polymorphic_decode_engine(encoded_data)

            # Decode to string
            decoded_str = decoded_bytes.decode('utf-8')

            # Add junk code execution (anti-analysis)
            self.anti_reverse.add_junk_code_execution()

            return decoded_str

        except Exception as e:
            raise ValueError(f"Base64 decoding failed: {str(e)}")

    def decode_with_validation(
        self,
        encoded_data: str,
        expected_length: Optional[int] = None,
        integrity_hash: Optional[str] = None
    ) -> str:
        """
        Decode with additional validation checks.

        Args:
            encoded_data: Base64-encoded string
            expected_length: Expected length of decoded output
            integrity_hash: SHA-256 hash for verification

        Returns:
            Decoded string

        Raises:
            ValueError: If validation fails
        """
        decoded = self.decode(encoded_data, integrity_hash)

        if expected_length and len(decoded) != expected_length:
            raise ValueError(
                f"Decoded length {len(decoded)} != expected {expected_length}"
            )

        return decoded

    def batch_decode(self, encoded_list: list) -> list:
        """
        Decode multiple Base64 strings with protection.

        Args:
            encoded_list: List of Base64-encoded strings

        Returns:
            List of decoded strings
        """
        results = []
        for encoded in encoded_list:
            try:
                results.append(self.decode(encoded))
            except ValueError as e:
                if self.strict_mode:
                    raise
                results.append(None)  # Failed decode

        return results

    def get_security_status(self) -> dict:
        """
        Get current security and analysis status.

        Returns:
            Dictionary with security metrics
        """
        _, threats = self._run_security_checks()

        return {
            'anti_analysis_enabled': self.enable_anti_analysis,
            'strict_mode': self.strict_mode,
            'total_calls': self._call_count,
            'suspicious_activity_count': self._suspicious_activity_count,
            'current_threats': threats,
            'execution_context': self.env_awareness.get_execution_context(),
        }


# Convenience functions for easy integration

def hardened_decode(
    encoded_data: str,
    strict_mode: bool = False,
    integrity_hash: Optional[str] = None
) -> str:
    """
    Convenience function for hardened Base64 decoding.

    Args:
        encoded_data: Base64-encoded string
        strict_mode: Fail on any detected analysis attempt
        integrity_hash: Optional SHA-256 hash for verification

    Returns:
        Decoded string
    """
    decoder = HardenedBase64Decoder(
        enable_anti_analysis=True,
        strict_mode=strict_mode
    )
    return decoder.decode(encoded_data, integrity_hash)


def create_protected_decoder(strict_mode: bool = False) -> HardenedBase64Decoder:
    """
    Factory function to create a hardened decoder instance.

    Args:
        strict_mode: Fail on detected analysis attempts

    Returns:
        HardenedBase64Decoder instance
    """
    return HardenedBase64Decoder(
        enable_anti_analysis=True,
        strict_mode=strict_mode
    )


if __name__ == "__main__":
    # Example usage and testing

    import base64

    print("=== Hardened Base64 Decoder ===\n")

    # Create test payload
    test_message = "powershell.exe -NoProfile -WindowStyle Hidden -Command 'Write-Host Test'"
    encoded = base64.b64encode(test_message.encode()).decode()

    print(f"Original: {test_message}")
    print(f"Encoded: {encoded}\n")

    # Create decoder
    decoder = HardenedBase64Decoder(enable_anti_analysis=True, strict_mode=False)

    # Decode
    print("Decoding with hardened decoder...")
    try:
        decoded = decoder.decode(encoded)
        print(f"Decoded: {decoded}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Show security status
    print("Security Status:")
    status = decoder.get_security_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\n=== Batch Decoding ===")
    messages = ["hello", "world", "security"]
    encoded_messages = [base64.b64encode(m.encode()).decode() for m in messages]

    decoded_messages = decoder.batch_decode(encoded_messages)
    for orig, decoded in zip(messages, decoded_messages):
        match = "✓" if orig == decoded else "✗"
        print(f"{match} {orig} -> {decoded}")

    print("\n=== Integrity Checking ===")
    test_data = "Sensitive data"
    test_encoded = base64.b64encode(test_data.encode()).decode()
    integrity = decoder.anti_tampering.calculate_integrity_hash(test_encoded.encode())

    print(f"Data: {test_data}")
    print(f"Encoded: {test_encoded}")
    print(f"Integrity Hash: {integrity}")

    # Decode with integrity check
    try:
        decoded_safe = decoder.decode(test_encoded, integrity)
        print(f"Decoded (safe): {decoded_safe}")
    except ValueError as e:
        print(f"Integrity check failed: {e}")
