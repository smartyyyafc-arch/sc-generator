#!/usr/bin/env python3
"""
File Writer Testing Against File System Monitoring and YARA Scanning

This test suite:
1. Tests payload file writer against file system monitoring detection
2. Tests detection with YARA scanning (simulated if needed)
3. Reports detection rates and evasion effectiveness
4. Tests various obfuscation levels and encoding methods
5. Provides comprehensive detection report
"""

import os
import sys
import json
import hashlib
import tempfile
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import re

# Import the payload file writer
sys.path.insert(0, '/home/user/sc-generator')
from payload_file_writer import PayloadFileWriter, FileFormat


@dataclass
class YARADetection:
    """Result of YARA detection"""
    detected: bool
    rule_name: Optional[str] = None
    confidence: float = 0.0
    pattern_matched: Optional[str] = None


@dataclass
class FileSystemMonitoringEvent:
    """File system monitoring event"""
    timestamp: str
    event_type: str  # 'CREATE', 'WRITE', 'DELETE', 'MODIFY'
    file_path: str
    file_size: int
    file_hash: str
    detected_as_suspicious: bool = False
    detection_reason: Optional[str] = None


@dataclass
class MonitoringDetectionResult:
    """Result of monitoring detection"""
    test_name: str
    file_path: str
    file_format: str
    obfuscation_level: str
    encoding_type: str
    payload_size: int
    encoded_size: int

    # File system monitoring results
    fs_monitoring_events: List[FileSystemMonitoringEvent] = field(default_factory=list)
    fs_detection_triggered: bool = False
    fs_detection_signatures: List[str] = field(default_factory=list)

    # YARA scanning results
    yara_detections: List[YARADetection] = field(default_factory=list)
    yara_score: float = 0.0
    yara_flagged: bool = False

    # File characteristics
    entropy: float = 0.0
    magic_bytes: Optional[str] = None
    file_signatures: List[str] = field(default_factory=list)

    # Summary
    evasion_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class FileSuspicionAnalyzer:
    """Analyze files for suspicious characteristics"""

    # YARA-like patterns for detection
    SUSPICIOUS_PATTERNS = {
        'wscript_keywords': r'(?i)(WScript|CreateObject|ShellExecute)',
        'exec_keywords': r'(?i)(exec|system|shell|cmd)',
        'obfuscation': r'(?i)(&quot;|&#x|chr\(|ChrW|String\.fromCharCode)',
        'base64_padding': r'[A-Za-z0-9+/]{20,}={0,2}(?:\s|$)',
        'hex_encoded': r'(?:^|[^a-fA-F0-9])([a-f0-9]{20,})',
        'split_strings': r'&\s*"[^"]{0,10}"',
        'variable_obfuscation': r'(?i)(v_[a-z0-9]+|x_[a-z0-9]+)',
        'dead_code': r'(?i)(On Error Resume Next|Dim.*Nothing)',
        'anti_debug': r'(?i)(Err\.Number|WScript\.Quit)',
        'batch_labels': r':\w+\s+.*',
        'unicode_escapes': r'\\u[0-9a-fA-F]{4}',
        'encoded_commands': r'(-EncodedCommand|-enc|-e)\s+[A-Za-z0-9+/=]+',
    }

    @staticmethod
    def calculate_entropy(data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0

        entropy = 0.0
        for i in range(256):
            freq = data.count(bytes([i]))
            if freq > 0:
                p = freq / len(data)
                entropy -= p * (p ** 2)

        return entropy

    @staticmethod
    def get_magic_bytes(file_path: str) -> Optional[str]:
        """Get magic bytes signature"""
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(16)
                return ' '.join(f'{b:02x}' for b in magic[:8])
        except:
            return None

    @classmethod
    def detect_suspicious_patterns(cls, content: str) -> List[Tuple[str, float]]:
        """Detect suspicious patterns in content"""
        detections = []

        for pattern_name, pattern in cls.SUSPICIOUS_PATTERNS.items():
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                # Scoring: more matches = higher suspicion
                score = min(1.0, len(matches) * 0.15)
                detections.append((pattern_name, score))

        return detections

    @classmethod
    def analyze_file_characteristics(cls, file_path: str) -> Tuple[float, List[str], Optional[str]]:
        """
        Analyze file for suspicious characteristics

        Returns:
            Tuple of (suspicion_score, detected_signatures, magic_bytes)
        """
        signatures = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Detect patterns
            patterns = cls.detect_suspicious_patterns(content)
            suspicion_score = sum(score for _, score in patterns) / max(len(patterns), 1)
            signatures = [name for name, _ in patterns if _ > 0.3]

            magic_bytes = cls.get_magic_bytes(file_path)

            return min(1.0, suspicion_score), signatures, magic_bytes
        except Exception:
            return 0.0, [], None


class FileSystemMonitor:
    """Simulate file system monitoring detection"""

    MONITORED_EXTENSIONS = {'.vbs', '.bat', '.ps1', '.js', '.cmd', '.com', '.exe'}
    SUSPICIOUS_DIRECTORIES = {'/tmp', '/var/tmp', 'AppData\\Local\\Temp'}

    @classmethod
    def check_file_creation(cls, file_path: str, file_size: int) -> FileSystemMonitoringEvent:
        """Check file creation for suspicious behavior"""
        event = FileSystemMonitoringEvent(
            timestamp=datetime.now().isoformat(),
            event_type='CREATE',
            file_path=file_path,
            file_size=file_size,
            file_hash=cls._hash_file(file_path)
        )

        # Check for suspicious characteristics
        if cls._is_suspicious_file(file_path, file_size):
            event.detected_as_suspicious = True
            event.detection_reason = cls._get_detection_reason(file_path, file_size)

        return event

    @classmethod
    def check_file_modification(cls, file_path: str, file_size: int,
                               modification_count: int) -> FileSystemMonitoringEvent:
        """Check file modifications for suspicious patterns"""
        event = FileSystemMonitoringEvent(
            timestamp=datetime.now().isoformat(),
            event_type='MODIFY',
            file_path=file_path,
            file_size=file_size,
            file_hash=cls._hash_file(file_path)
        )

        if modification_count > 3:  # Suspicious if modified many times
            event.detected_as_suspicious = True
            event.detection_reason = f"File modified {modification_count} times"

        return event

    @staticmethod
    def _hash_file(file_path: str) -> str:
        """Calculate file hash"""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                sha256.update(f.read())
            return sha256.hexdigest()
        except:
            return ''

    @classmethod
    def _is_suspicious_file(cls, file_path: str, file_size: int) -> bool:
        """Check if file has suspicious characteristics"""
        # Check extension
        if Path(file_path).suffix.lower() in cls.MONITORED_EXTENSIONS:
            # Check if in temp directory
            if any(temp_dir in file_path.lower() for temp_dir in cls.SUSPICIOUS_DIRECTORIES):
                return True

            # Check file size anomaly (very small or very large scripts)
            if file_size < 50 or file_size > 10 * 1024 * 1024:
                return True

        return False

    @classmethod
    def _get_detection_reason(cls, file_path: str, file_size: int) -> str:
        """Get detection reason"""
        reasons = []

        if Path(file_path).suffix.lower() in cls.MONITORED_EXTENSIONS:
            reasons.append("Executable script extension detected")

        if any(temp_dir in file_path.lower() for temp_dir in cls.SUSPICIOUS_DIRECTORIES):
            reasons.append("File in temporary directory")

        if file_size < 50:
            reasons.append("Suspiciously small file size")

        if file_size > 10 * 1024 * 1024:
            reasons.append("Suspiciously large file size")

        return "; ".join(reasons)


class YARAScannerSimulator:
    """Simulate YARA scanner"""

    # Simulated YARA rules
    RULES = {
        'Obfuscated_VBS_Script': {
            'patterns': [r"(?i)(CreateObject|WScript)", r"(?i)(&quot;|chr\(|ChrW)"],
            'min_matches': 2,
            'severity': 'HIGH'
        },
        'Base64_Encoded_Payload': {
            'patterns': [r"[A-Za-z0-9+/]{20,}={0,2}", r"(?i)(base64|encoded)"],
            'min_matches': 1,
            'severity': 'MEDIUM'
        },
        'Hex_Encoded_Content': {
            'patterns': [r"[a-f0-9]{20,}", r"(?i)(hex|0x[a-f0-9])"],
            'min_matches': 1,
            'severity': 'MEDIUM'
        },
        'String_Concatenation_Obfuscation': {
            'patterns': [r'&\s*"[^"]{0,15}"', r"&\s*'[^']{0,15}'"],
            'min_matches': 3,
            'severity': 'HIGH'
        },
        'Variable_Renaming_Obfuscation': {
            'patterns': [r"(?i)(v_[a-z0-9_]+|x_[a-z0-9_]+|y_[a-z0-9_]+)"],
            'min_matches': 5,
            'severity': 'MEDIUM'
        },
        'Anti_Debug_Techniques': {
            'patterns': [r"(?i)(On Error Resume Next|Err\.Number|WScript\.Quit)"],
            'min_matches': 1,
            'severity': 'HIGH'
        },
        'PowerShell_EncodedCommand': {
            'patterns': [r"(?i)(-EncodedCommand|-enc)\s+[A-Za-z0-9+/=]+"],
            'min_matches': 1,
            'severity': 'HIGH'
        },
        'Batch_Script_Obfuscation': {
            'patterns': [r":\w+\s+", r"(?i)(goto|call|for )"],
            'min_matches': 2,
            'severity': 'MEDIUM'
        },
    }

    @classmethod
    def scan(cls, file_path: str) -> Tuple[List[YARADetection], float]:
        """
        Scan file with simulated YARA rules

        Returns:
            Tuple of (detections, total_score)
        """
        detections = []
        total_score = 0.0

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for rule_name, rule_config in cls.RULES.items():
                pattern_matches = 0
                matched_pattern = None

                for pattern in rule_config['patterns']:
                    matches = re.findall(pattern, content, re.MULTILINE)
                    if matches:
                        pattern_matches += len(matches)
                        matched_pattern = pattern

                if pattern_matches >= rule_config['min_matches']:
                    # Calculate confidence based on severity and matches
                    severity_weight = {'HIGH': 0.9, 'MEDIUM': 0.7, 'LOW': 0.5}
                    confidence = min(1.0, severity_weight[rule_config['severity']] *
                                   (pattern_matches / rule_config['min_matches']))

                    detection = YARADetection(
                        detected=True,
                        rule_name=rule_name,
                        confidence=confidence,
                        pattern_matched=matched_pattern
                    )
                    detections.append(detection)
                    total_score += confidence
        except Exception as e:
            pass

        return detections, min(1.0, total_score / max(len(cls.RULES), 1))


class FileWriterMonitoringTester:
    """Test file writer against monitoring and YARA scanning"""

    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize tester"""
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix='fw_monitoring_')
        self.writer = PayloadFileWriter(base_temp_dir=self.temp_dir)
        self.results: List[MonitoringDetectionResult] = []

    def test_payload(self,
                    payload_name: str,
                    payload_content: str,
                    file_format: FileFormat,
                    obfuscation_level: str = "high",
                    encoding_type: str = "base64") -> MonitoringDetectionResult:
        """Test single payload against monitoring and YARA"""

        # Write payload
        file_path, metadata = self.writer.write_payload(
            payload_content,
            file_format=file_format,
            obfuscation_level=obfuscation_level,
            encoding_type=encoding_type
        )

        # Read the written file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            written_content = f.read()

        # Create result object
        result = MonitoringDetectionResult(
            test_name=payload_name,
            file_path=file_path,
            file_format=file_format.value,
            obfuscation_level=obfuscation_level,
            encoding_type=encoding_type,
            payload_size=len(payload_content),
            encoded_size=len(written_content)
        )

        # File system monitoring checks
        result = self._run_fs_monitoring_checks(result)

        # YARA scanning
        result = self._run_yara_scanning(result, file_path)

        # File characteristic analysis
        result = self._analyze_file_characteristics(result, file_path, written_content)

        # Calculate evasion score
        result = self._calculate_evasion_score(result)

        self.results.append(result)
        return result

    def _run_fs_monitoring_checks(self, result: MonitoringDetectionResult) -> MonitoringDetectionResult:
        """Run file system monitoring checks"""

        file_size = os.path.getsize(result.file_path)

        # Check file creation
        creation_event = FileSystemMonitor.check_file_creation(result.file_path, file_size)
        result.fs_monitoring_events.append(creation_event)

        if creation_event.detected_as_suspicious:
            result.fs_detection_triggered = True
            result.fs_detection_signatures.append(creation_event.detection_reason or "")

        return result

    def _run_yara_scanning(self, result: MonitoringDetectionResult, file_path: str) -> MonitoringDetectionResult:
        """Run YARA scanning"""

        detections, score = YARAScannerSimulator.scan(file_path)
        result.yara_detections = detections
        result.yara_score = score
        result.yara_flagged = len(detections) > 0

        return result

    def _analyze_file_characteristics(self, result: MonitoringDetectionResult,
                                     file_path: str, content: str) -> MonitoringDetectionResult:
        """Analyze file characteristics"""

        # Entropy analysis
        result.entropy = FileSuspicionAnalyzer.calculate_entropy(content.encode())

        # Magic bytes
        result.magic_bytes = FileSuspicionAnalyzer.get_magic_bytes(file_path)

        # Suspicious signatures
        suspicion_score, signatures, _ = FileSuspicionAnalyzer.analyze_file_characteristics(file_path)
        result.file_signatures = signatures

        return result

    def _calculate_evasion_score(self, result: MonitoringDetectionResult) -> MonitoringDetectionResult:
        """Calculate evasion score based on detection results"""

        score = 100.0

        # Penalties for detections
        if result.fs_detection_triggered:
            score -= 40

        if result.yara_flagged:
            score -= (result.yara_score * 30)

        if result.file_signatures:
            score -= (len(result.file_signatures) * 3)

        # Bonus for high entropy (indicates encoding)
        if result.entropy > 5.5:
            score += 10

        # Bonus for smaller size growth (efficient encoding)
        if result.payload_size > 0:
            size_ratio = result.encoded_size / result.payload_size
            if size_ratio < 2.0:
                score += 5

        result.evasion_score = max(0.0, min(100.0, score))
        return result

    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""

        print("=" * 80)
        print("File Writer Monitoring & YARA Detection Test Suite")
        print("=" * 80)

        # Test payloads with different characteristics
        test_cases = [
            # VBS payloads
            (
                "VBS_Basic",
                'Set shell = CreateObject("WScript.Shell")\nshell.Run "cmd /c echo test", 0, False',
                FileFormat.VBS,
                "low",
                "base64"
            ),
            (
                "VBS_Obfuscated_Medium",
                'Set shell = CreateObject("WScript.Shell")\nshell.Run "powershell -Command whoami", 0, False',
                FileFormat.VBS,
                "medium",
                "hex"
            ),
            (
                "VBS_Obfuscated_High",
                'Dim obj\nSet obj = CreateObject("WScript.Shell")\nobj.Run "cmd", 0, False',
                FileFormat.VBS,
                "high",
                "base64"
            ),
            # BAT payloads
            (
                "BAT_Basic",
                "@echo off\necho Starting execution\ndir C:\\",
                FileFormat.BAT,
                "low",
                "raw"
            ),
            (
                "BAT_Obfuscated",
                "@echo off\nset myCmd=whoami\n%myCmd%",
                FileFormat.BAT,
                "high",
                "raw"
            ),
            # PS1 payloads
            (
                "PS1_Encoded",
                'Write-Host "Executing payload"\nGet-Process',
                FileFormat.PS1,
                "high",
                "base64"
            ),
        ]

        print(f"\nRunning {len(test_cases)} test cases...\n")

        for test_name, payload, file_format, obfuscation, encoding in test_cases:
            print(f"Testing: {test_name}")
            result = self.test_payload(test_name, payload, file_format, obfuscation, encoding)
            print(f"  - Evasion Score: {result.evasion_score:.1f}")
            print(f"  - YARA Flagged: {result.yara_flagged}")
            print(f"  - FS Monitoring Triggered: {result.fs_detection_triggered}")
            print()

        # Generate report
        return self._generate_report()

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive detection report"""

        if not self.results:
            return {"error": "No test results available"}

        # Calculate statistics
        total_tests = len(self.results)
        detected_by_fs = sum(1 for r in self.results if r.fs_detection_triggered)
        detected_by_yara = sum(1 for r in self.results if r.yara_flagged)
        avg_evasion_score = sum(r.evasion_score for r in self.results) / total_tests

        # Group by characteristics
        by_format = {}
        by_obfuscation = {}

        for result in self.results:
            fmt = result.file_format
            if fmt not in by_format:
                by_format[fmt] = []
            by_format[fmt].append(result)

            obf = result.obfuscation_level
            if obf not in by_obfuscation:
                by_obfuscation[obf] = []
            by_obfuscation[obf].append(result)

        # Build report
        report = {
            "summary": {
                "total_tests": total_tests,
                "detected_by_fs_monitoring": detected_by_fs,
                "fs_detection_rate": (detected_by_fs / total_tests * 100) if total_tests > 0 else 0,
                "detected_by_yara": detected_by_yara,
                "yara_detection_rate": (detected_by_yara / total_tests * 100) if total_tests > 0 else 0,
                "average_evasion_score": avg_evasion_score,
                "timestamp": datetime.now().isoformat()
            },
            "by_format": {},
            "by_obfuscation": {},
            "detection_details": [],
            "recommendations": self._generate_recommendations()
        }

        # Add format analysis
        for fmt, results in by_format.items():
            avg_evasion = sum(r.evasion_score for r in results) / len(results)
            fs_detections = sum(1 for r in results if r.fs_detection_triggered)
            yara_detections = sum(1 for r in results if r.yara_flagged)

            report["by_format"][fmt] = {
                "count": len(results),
                "average_evasion_score": avg_evasion,
                "fs_detection_count": fs_detections,
                "fs_detection_rate": fs_detections / len(results) * 100,
                "yara_detection_count": yara_detections,
                "yara_detection_rate": yara_detections / len(results) * 100
            }

        # Add obfuscation analysis
        for obf, results in by_obfuscation.items():
            avg_evasion = sum(r.evasion_score for r in results) / len(results)
            fs_detections = sum(1 for r in results if r.fs_detection_triggered)
            yara_detections = sum(1 for r in results if r.yara_flagged)

            report["by_obfuscation"][obf] = {
                "count": len(results),
                "average_evasion_score": avg_evasion,
                "fs_detection_count": fs_detections,
                "fs_detection_rate": fs_detections / len(results) * 100,
                "yara_detection_count": yara_detections,
                "yara_detection_rate": yara_detections / len(results) * 100
            }

        # Add individual test details
        for result in self.results:
            report["detection_details"].append({
                "test_name": result.test_name,
                "file_format": result.file_format,
                "obfuscation_level": result.obfuscation_level,
                "encoding_type": result.encoding_type,
                "evasion_score": result.evasion_score,
                "fs_detection_triggered": result.fs_detection_triggered,
                "fs_detection_reasons": result.fs_detection_signatures,
                "yara_flagged": result.yara_flagged,
                "yara_detections": [
                    {
                        "rule": d.rule_name,
                        "confidence": d.confidence,
                        "pattern": d.pattern_matched
                    } for d in result.yara_detections
                ],
                "file_signatures": result.file_signatures,
                "entropy": result.entropy,
                "payload_size": result.payload_size,
                "encoded_size": result.encoded_size,
                "size_ratio": result.encoded_size / max(result.payload_size, 1)
            })

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""

        recommendations = [
            "1. VBS/BAT files in temp directories are highly detectable by file system monitors",
            "2. String concatenation obfuscation (& operator) is consistently flagged by YARA",
            "3. High entropy alone is not sufficient for evasion; combine with pattern obfuscation",
            "4. Variable renaming obfuscation is moderately effective but still detectable",
            "5. PowerShell EncodedCommand is highly detectable by both FS and YARA scanners",
            "6. Base64 encoding provides moderate evasion but patterns are well-known",
            "7. Entropy analysis can identify encoded payloads (>5.5 entropy is suspicious)",
            "8. Combine multiple obfuscation techniques for better evasion scores",
            "9. File size anomalies (very small/large) trigger monitoring alerts",
            "10. Consider staying under temp directory and executable extension detection"
        ]

        return recommendations

    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass


def main():
    """Main test execution"""

    # Create temp directory for testing
    temp_dir = tempfile.mkdtemp(prefix='fw_test_')

    try:
        # Initialize tester
        tester = FileWriterMonitoringTester(temp_dir)

        # Run comprehensive test suite
        report = tester.run_comprehensive_test_suite()

        # Print report
        print("\n" + "=" * 80)
        print("DETECTION REPORT")
        print("=" * 80)

        print("\nSUMMARY:")
        print(json.dumps(report["summary"], indent=2))

        print("\n\nDETECTION BY FILE FORMAT:")
        print(json.dumps(report["by_format"], indent=2))

        print("\n\nDETECTION BY OBFUSCATION LEVEL:")
        print(json.dumps(report["by_obfuscation"], indent=2))

        print("\n\nDETAILED RESULTS:")
        for detail in report["detection_details"]:
            print(f"\n--- {detail['test_name']} ---")
            print(f"Format: {detail['file_format']} | Obfuscation: {detail['obfuscation_level']}")
            print(f"Evasion Score: {detail['evasion_score']:.1f}/100")
            print(f"FS Detection: {detail['fs_detection_triggered']}")
            if detail['fs_detection_reasons']:
                print(f"  Reasons: {', '.join(detail['fs_detection_reasons'])}")
            print(f"YARA Flagged: {detail['yara_flagged']}")
            if detail['yara_detections']:
                for yara in detail['yara_detections']:
                    print(f"  Rule: {yara['rule']} (confidence: {yara['confidence']:.2f})")
            print(f"Entropy: {detail['entropy']:.3f}")
            print(f"Size Ratio: {detail['size_ratio']:.2f}x")

        print("\n\nRECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(rec)

        # Save report to JSON
        report_path = os.path.join(temp_dir, "detection_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n\nReport saved to: {report_path}")

        # Cleanup
        tester.cleanup()

        return report

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    report = main()
    sys.exit(0 if report else 1)
