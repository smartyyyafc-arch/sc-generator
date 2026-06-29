#!/usr/bin/env python3
"""
Forensic Registry Storage Tester
Analyzes registry storage mechanisms against forensic detection tools
Tests payload detection difficulty and evasion effectiveness
"""

import re
import base64
import binascii
import json
import hashlib
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import unittest
from vbs_encoder import VBSEncoder, ObfuscationConfig


class DetectionMethod(Enum):
    """Registry forensic detection methods"""
    PATTERN_SIGNATURE = "pattern_signature"
    ENTROPY_ANALYSIS = "entropy_analysis"
    BASE64_DETECTION = "base64_detection"
    HEX_SEQUENCE_DETECTION = "hex_sequence_detection"
    REGISTRY_PATH_ANALYSIS = "registry_path_analysis"
    VALUE_SIZE_ANOMALY = "value_size_anomaly"
    STRING_EXTRACTION = "string_extraction"
    ENCODING_FINGERPRINT = "encoding_fingerprint"


@dataclass
class ForensicFinding:
    """A single forensic detection finding"""
    method: DetectionMethod
    detected: bool
    confidence: float  # 0.0 to 1.0
    evidence: str
    payload_fragment: str = ""
    difficulty_score: float = 0.0  # 0.0=easy to detect, 1.0=hard to detect


@dataclass
class ForensicReport:
    """Complete forensic analysis report"""
    payload: str
    payload_hash: str
    encoding_method: str
    registry_path: str
    registry_hive: str
    vbs_code: str
    findings: List[ForensicFinding]
    overall_detection_difficulty: float
    detectable_methods: List[str]
    evasion_techniques_used: List[str]
    size_analysis: Dict[str, int]


class PatternSignatureAnalyzer:
    """Detects payloads using signature patterns"""

    # Common IOCs and malicious patterns
    MALICIOUS_PATTERNS = {
        'powershell': r'powershell\.exe|powershell\s+-',
        'cmd_exec': r'cmd\.exe|cmd\s+/c',
        'vbscript_exec': r'CreateObject\s*\(\s*"WScript\.Shell"',
        'url_download': r'https?://|URLDownloadToFile|WinHttpRequest',
        'registry_run': r'HKEY_LOCAL_MACHINE.*?Run|HKEY_CURRENT_USER.*?Run',
        'encoded_payload': r'base64|hex\s+encoding',
        'execution_methods': r'\.Run\s*\(|Execute\s*\(|Eval\s*\(',
        'system_commands': r'WScript\.Shell|Shell\.Application|WSH\.Network',
    }

    @staticmethod
    def analyze(payload: str, vbs_code: str) -> ForensicFinding:
        """Detect malicious patterns in payload and VBS code"""
        combined = f"{payload} {vbs_code}".lower()
        matched_patterns = []

        for pattern_name, pattern in PatternSignatureAnalyzer.MALICIOUS_PATTERNS.items():
            if re.search(pattern, combined, re.IGNORECASE):
                matched_patterns.append(pattern_name)

        detected = len(matched_patterns) > 0
        confidence = min(len(matched_patterns) / len(PatternSignatureAnalyzer.MALICIOUS_PATTERNS), 1.0)

        evidence = f"Matched {len(matched_patterns)} suspicious patterns: {', '.join(matched_patterns)}"
        difficulty = 1.0 - confidence  # Hard to detect if few patterns match

        return ForensicFinding(
            method=DetectionMethod.PATTERN_SIGNATURE,
            detected=detected,
            confidence=confidence,
            evidence=evidence,
            difficulty_score=difficulty
        )


class EntropyAnalyzer:
    """Analyzes entropy to detect encoded/encrypted data"""

    @staticmethod
    def calculate_entropy(data: str) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0

        freq = {}
        for char in data:
            freq[char] = freq.get(char, 0) + 1

        entropy = 0.0
        length = len(data)
        for count in freq.values():
            p = count / length
            entropy -= p * (p**0.5) if p > 0 else 0

        return entropy

    @staticmethod
    def analyze(payload: str, encoded_payload: str) -> ForensicFinding:
        """Detect encoded payloads using entropy analysis"""
        payload_entropy = EntropyAnalyzer.calculate_entropy(payload)
        encoded_entropy = EntropyAnalyzer.calculate_entropy(encoded_payload)

        # Encoded data typically has high entropy (4.0-5.8 bits/char for base64/hex)
        entropy_threshold = 3.5
        high_entropy = encoded_entropy > entropy_threshold

        confidence = min((encoded_entropy / 6.0), 1.0) if high_entropy else 0.0
        detected = high_entropy

        evidence = f"Payload entropy: {payload_entropy:.2f}, Encoded entropy: {encoded_entropy:.2f}"
        difficulty = 0.2 if high_entropy else 0.8  # High entropy is easy to spot

        return ForensicFinding(
            method=DetectionMethod.ENTROPY_ANALYSIS,
            detected=detected,
            confidence=confidence,
            evidence=evidence,
            payload_fragment=f"Entropy ratio: {encoded_entropy/max(payload_entropy, 0.1):.2f}x",
            difficulty_score=difficulty
        )


class Base64DetectionAnalyzer:
    """Detects base64-encoded payloads"""

    # Base64 alphabet patterns
    BASE64_PATTERN = r'^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'
    BASE64_LONG_SEQUENCE = r'[A-Za-z0-9+/]{20,}'

    @staticmethod
    def analyze(encoded_payload: str, encoding_method: str) -> ForensicFinding:
        """Detect base64 encoding"""
        if encoding_method != "base64":
            return ForensicFinding(
                method=DetectionMethod.BASE64_DETECTION,
                detected=False,
                confidence=0.0,
                evidence="Encoding method is not base64",
                difficulty_score=1.0
            )

        # Check for base64 patterns
        is_valid_base64 = bool(re.match(Base64DetectionAnalyzer.BASE64_PATTERN, encoded_payload))
        has_padding = encoded_payload.endswith(('==', '='))
        has_long_sequence = bool(re.search(Base64DetectionAnalyzer.BASE64_LONG_SEQUENCE, encoded_payload))

        detected = is_valid_base64 or has_long_sequence
        confidence = 0.9 if (is_valid_base64 and has_padding) else 0.6 if detected else 0.0

        # Try to decode to verify
        try:
            decoded = base64.b64decode(encoded_payload).decode('utf-8', errors='ignore')
            can_decode = len(decoded) > 0
            confidence = min(confidence + 0.2, 1.0) if can_decode else confidence
        except:
            can_decode = False

        evidence = f"Valid base64: {is_valid_base64}, Has padding: {has_padding}, Decodable: {can_decode}"
        difficulty = 0.1 if detected else 0.9  # Base64 is very easy to detect

        return ForensicFinding(
            method=DetectionMethod.BASE64_DETECTION,
            detected=detected,
            confidence=confidence,
            evidence=evidence,
            payload_fragment=encoded_payload[:50],
            difficulty_score=difficulty
        )


class HexSequenceAnalyzer:
    """Detects hex-encoded sequences"""

    HEX_PATTERN = r'^[0-9a-fA-F]+$'
    HEX_LONG_SEQUENCE = r'[0-9a-fA-F]{20,}'

    @staticmethod
    def analyze(encoded_payload: str, encoding_method: str) -> ForensicFinding:
        """Detect hex encoding"""
        if encoding_method != "hex":
            return ForensicFinding(
                method=DetectionMethod.HEX_SEQUENCE_DETECTION,
                detected=False,
                confidence=0.0,
                evidence="Encoding method is not hex",
                difficulty_score=1.0
            )

        is_valid_hex = bool(re.match(HexSequenceAnalyzer.HEX_PATTERN, encoded_payload))
        has_long_hex = bool(re.search(HexSequenceAnalyzer.HEX_LONG_SEQUENCE, encoded_payload))

        detected = is_valid_hex or has_long_hex
        confidence = 0.95 if is_valid_hex else 0.5 if detected else 0.0

        # Try to decode
        try:
            decoded = binascii.unhexlify(encoded_payload).decode('utf-8', errors='ignore')
            can_decode = len(decoded) > 0
            confidence = min(confidence + 0.15, 1.0) if can_decode else confidence
        except:
            can_decode = False

        evidence = f"Valid hex: {is_valid_hex}, Decodable: {can_decode}"
        difficulty = 0.2 if detected else 0.9  # Hex is fairly easy to detect

        return ForensicFinding(
            method=DetectionMethod.HEX_SEQUENCE_DETECTION,
            detected=detected,
            confidence=confidence,
            evidence=evidence,
            payload_fragment=encoded_payload[:50],
            difficulty_score=difficulty
        )


class RegistryPathAnalyzer:
    """Analyzes registry paths for suspicious locations"""

    # Known suspicious registry paths
    SUSPICIOUS_PATHS = {
        'Run': r'.*\\Run$',
        'RunOnce': r'.*\\RunOnce$',
        'Shell Folders': r'.*\\Shell Folders',
        'Services': r'.*\\Services\\',
        'Winlogon': r'.*\\Winlogon',
        'AppInit_DLLs': r'.*\\AppInit_DLLs',
    }

    @staticmethod
    def analyze(registry_path: str, registry_hive: str) -> ForensicFinding:
        """Analyze registry path for suspicious patterns"""
        matched_suspicious = []

        for suspicious_type, pattern in RegistryPathAnalyzer.SUSPICIOUS_PATHS.items():
            if re.search(pattern, registry_path, re.IGNORECASE):
                matched_suspicious.append(suspicious_type)

        detected = len(matched_suspicious) > 0
        confidence = min(len(matched_suspicious) / len(RegistryPathAnalyzer.SUSPICIOUS_PATHS), 1.0) if detected else 0.0

        # HKLM is more suspicious than HKCU
        if registry_hive.upper() == "HKLM":
            confidence = min(confidence + 0.2, 1.0)

        evidence = f"Registry path: {registry_path} (Hive: {registry_hive})"
        if matched_suspicious:
            evidence += f". Suspicious types matched: {', '.join(matched_suspicious)}"

        difficulty = 1.0 - confidence  # Easy to detect known malicious paths

        return ForensicFinding(
            method=DetectionMethod.REGISTRY_PATH_ANALYSIS,
            detected=detected,
            confidence=confidence,
            evidence=evidence,
            difficulty_score=difficulty
        )


class ValueSizeAnomalyAnalyzer:
    """Detects anomalies in registry value sizes"""

    # Typical registry value sizes
    NORMAL_SIZE_RANGE = (10, 1000)  # Bytes

    @staticmethod
    def analyze(payload: str, encoded_payload: str) -> ForensicFinding:
        """Detect anomalous value sizes"""
        payload_size = len(payload)
        encoded_size = len(encoded_payload)

        # Base64 adds ~33% overhead
        size_ratio = encoded_size / max(payload_size, 1)

        # Very large registry values are unusual
        is_abnormal_size = encoded_size > ValueSizeAnomalyAnalyzer.NORMAL_SIZE_RANGE[1]

        confidence = 0.3 if is_abnormal_size else 0.1
        detected = is_abnormal_size

        evidence = f"Payload size: {payload_size} bytes, Encoded size: {encoded_size} bytes (ratio: {size_ratio:.2f})"
        difficulty = 0.7 if is_abnormal_size else 0.95  # Normal-sized values are harder to detect

        return ForensicFinding(
            method=DetectionMethod.VALUE_SIZE_ANOMALY,
            detected=detected,
            confidence=confidence,
            evidence=evidence,
            payload_fragment=f"{encoded_size} bytes",
            difficulty_score=difficulty
        )


class StringExtractionAnalyzer:
    """Attempts to extract readable strings from encoded payloads"""

    MIN_STRING_LENGTH = 4

    @staticmethod
    def extract_strings(data: str) -> List[str]:
        """Extract readable strings from data"""
        strings = re.findall(r'[\x20-\x7E]{' + str(StringExtractionAnalyzer.MIN_STRING_LENGTH) + ',}', data)
        return strings

    @staticmethod
    def analyze(payload: str, encoded_payload: str, vbs_code: str) -> ForensicFinding:
        """Detect if original payload can be extracted from code"""
        # Try to find the original payload in the VBS code
        payload_in_code = payload in vbs_code

        # Try to find common payload fragments
        fragments = payload.split()
        fragments_found = sum(1 for frag in fragments if len(frag) > 4 and frag.lower() in vbs_code.lower())
        fragment_ratio = fragments_found / max(len(fragments), 1) if fragments else 0

        detected = payload_in_code or fragment_ratio > 0.3
        confidence = 1.0 if payload_in_code else min(fragment_ratio, 1.0)

        evidence = f"Payload in code: {payload_in_code}, Fragment matches: {fragments_found}/{len(fragments)}"
        difficulty = 1.0 if not detected else 0.0  # Either fully hidden or fully visible

        return ForensicFinding(
            method=DetectionMethod.STRING_EXTRACTION,
            detected=detected,
            confidence=confidence,
            evidence=evidence,
            difficulty_score=difficulty
        )


class EncodingFingerprintAnalyzer:
    """Detects encoding fingerprints specific to base64/hex"""

    @staticmethod
    def analyze(encoded_payload: str, encoding_method: str) -> ForensicFinding:
        """Detect encoding-specific fingerprints"""
        if encoding_method == "base64":
            # Base64 has characteristic padding and alphabet
            has_b64_alphabet = bool(re.search(r'[A-Za-z0-9+/]{4,}', encoded_payload))
            has_padding = encoded_payload.endswith(('=', '=='))
            confidence = 0.8 if (has_b64_alphabet and has_padding) else 0.5 if has_b64_alphabet else 0.0
            evidence = f"Base64 alphabet present: {has_b64_alphabet}, Padding: {has_padding}"

        elif encoding_method == "hex":
            # Hex has only 0-9 and a-f
            has_hex_alphabet = bool(re.search(r'[0-9a-fA-F]{4,}', encoded_payload))
            no_base64_only = not bool(re.search(r'[G-Z]', encoded_payload))
            confidence = 0.85 if (has_hex_alphabet and no_base64_only) else 0.4 if has_hex_alphabet else 0.0
            evidence = f"Hex alphabet present: {has_hex_alphabet}, No B64-only chars: {no_base64_only}"
        else:
            confidence = 0.0
            evidence = "Unknown encoding method"

        detected = confidence > 0.4
        difficulty = 0.1 if detected else 0.9  # Easy to detect specific encodings

        return ForensicFinding(
            method=DetectionMethod.ENCODING_FINGERPRINT,
            detected=detected,
            confidence=confidence,
            evidence=evidence,
            difficulty_score=difficulty
        )


class ForensicRegistryTester:
    """Main forensic testing harness"""

    def __init__(self):
        self.encoder = VBSEncoder()
        self.findings: List[ForensicFinding] = []

    def run_analysis(
        self,
        payload: str,
        registry_hive: str = "HKCU",
        registry_path: str = "Software\\Microsoft\\Windows",
        value_name: str = "TestValue",
        encoding: str = "base64"
    ) -> ForensicReport:
        """Run complete forensic analysis"""
        self.findings = []

        # Generate VBS code
        vbs_code = self.encoder.create_registry_storage_vbs(
            payload,
            registry_hive=registry_hive,
            registry_path=registry_path,
            value_name=value_name,
            encoding=encoding
        )

        # Encode payload
        if encoding == "base64":
            encoded_payload, _ = self.encoder.encode_string_base64(payload)
        else:
            encoded_payload, _ = self.encoder.encode_string_hex(payload)

        # Run all analysis methods
        self.findings.append(PatternSignatureAnalyzer.analyze(payload, vbs_code))
        self.findings.append(EntropyAnalyzer.analyze(payload, encoded_payload))
        self.findings.append(Base64DetectionAnalyzer.analyze(encoded_payload, encoding))
        self.findings.append(HexSequenceAnalyzer.analyze(encoded_payload, encoding))
        self.findings.append(RegistryPathAnalyzer.analyze(registry_path, registry_hive))
        self.findings.append(ValueSizeAnomalyAnalyzer.analyze(payload, encoded_payload))
        self.findings.append(StringExtractionAnalyzer.analyze(payload, encoded_payload, vbs_code))
        self.findings.append(EncodingFingerprintAnalyzer.analyze(encoded_payload, encoding))

        # Calculate overall difficulty
        detection_difficulties = [f.difficulty_score for f in self.findings]
        overall_difficulty = sum(detection_difficulties) / len(detection_difficulties) if detection_difficulties else 0.5

        # Get detected methods
        detectable_methods = [f.method.value for f in self.findings if f.detected]

        # Determine evasion techniques
        evasion_techniques = []
        if encoding == "base64":
            evasion_techniques.append("base64_encoding")
        elif encoding == "hex":
            evasion_techniques.append("hex_encoding")
        evasion_techniques.append("registry_obfuscation")
        evasion_techniques.append("vbs_wrapper")

        # Size analysis
        size_analysis = {
            "original_payload": len(payload),
            "encoded_payload": len(encoded_payload),
            "vbs_code": len(vbs_code),
            "encoding_overhead": len(encoded_payload) - len(payload),
            "total_size": len(vbs_code) + len(encoded_payload)
        }

        return ForensicReport(
            payload=payload,
            payload_hash=hashlib.sha256(payload.encode()).hexdigest(),
            encoding_method=encoding,
            registry_path=registry_path,
            registry_hive=registry_hive,
            vbs_code=vbs_code,
            findings=self.findings,
            overall_detection_difficulty=overall_difficulty,
            detectable_methods=detectable_methods,
            evasion_techniques_used=evasion_techniques,
            size_analysis=size_analysis
        )


class ForensicTestSuite(unittest.TestCase):
    """Unit tests for forensic detection"""

    def setUp(self):
        self.tester = ForensicRegistryTester()

    def test_simple_payload_detection(self):
        """Test detection of simple payload"""
        report = self.tester.run_analysis(
            "powershell.exe -Command Write-Host",
            encoding="base64"
        )

        # Should detect patterns
        self.assertTrue(any(f.method == DetectionMethod.PATTERN_SIGNATURE and f.detected for f in report.findings))

    def test_base64_encoding_detection(self):
        """Test base64 encoding detection"""
        report = self.tester.run_analysis(
            "test payload",
            encoding="base64"
        )

        # Should detect base64
        base64_finding = next((f for f in report.findings if f.method == DetectionMethod.BASE64_DETECTION), None)
        self.assertIsNotNone(base64_finding)
        self.assertTrue(base64_finding.detected)

    def test_hex_encoding_detection(self):
        """Test hex encoding detection"""
        report = self.tester.run_analysis(
            "test payload",
            encoding="hex"
        )

        # Should detect hex
        hex_finding = next((f for f in report.findings if f.method == DetectionMethod.HEX_SEQUENCE_DETECTION), None)
        self.assertIsNotNone(hex_finding)
        self.assertTrue(hex_finding.detected)

    def test_registry_path_suspicion(self):
        """Test suspicious registry path detection"""
        report = self.tester.run_analysis(
            "test",
            registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        )

        # Run key should be detected as suspicious
        path_finding = next((f for f in report.findings if f.method == DetectionMethod.REGISTRY_PATH_ANALYSIS), None)
        self.assertIsNotNone(path_finding)
        self.assertTrue(path_finding.detected)

    def test_long_payload_size_anomaly(self):
        """Test detection of abnormally large payloads"""
        long_payload = "cmd /c " + ("A" * 2000)
        report = self.tester.run_analysis(long_payload)

        # Should detect size anomaly
        size_finding = next((f for f in report.findings if f.method == DetectionMethod.VALUE_SIZE_ANOMALY), None)
        self.assertIsNotNone(size_finding)

    def test_entropy_analysis(self):
        """Test entropy-based detection"""
        report = self.tester.run_analysis("test payload")

        # Should perform entropy analysis
        entropy_finding = next((f for f in report.findings if f.method == DetectionMethod.ENTROPY_ANALYSIS), None)
        self.assertIsNotNone(entropy_finding)

    def test_overall_difficulty_score(self):
        """Test that overall difficulty score is calculated"""
        report = self.tester.run_analysis("test")

        self.assertGreaterEqual(report.overall_detection_difficulty, 0.0)
        self.assertLessEqual(report.overall_detection_difficulty, 1.0)


if __name__ == "__main__":
    unittest.main()
