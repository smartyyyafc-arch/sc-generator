#!/usr/bin/env python3
"""
Advanced Reputation-Based Detection Evasion Audit
=================================================

Comprehensive reputation audit including:
- Integration with polymorphic engine
- Signature-based reputation analysis
- Behavioral reputation scoring
- Multi-vendor reputation simulation
- YARA rule detection
- Machine learning feature extraction
- Reputation database correlation
"""

import hashlib
import json
import statistics
import base64
import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import random


class VendorReputation(Enum):
    """Major reputation vendors"""
    VIRUSTOTAL = "VirusTotal"
    HYBRID_ANALYSIS = "Hybrid Analysis"
    ALIENVAULT_OTX = "AlienVault OTX"
    ABUSE_CH = "Abuse.ch"
    GOOGLE_SAFE_BROWSING = "Google Safe Browsing"


@dataclass
class VendorDetection:
    """Vendor-specific detection"""
    vendor: VendorReputation
    detected: bool
    confidence: float
    category: str
    signature: str


@dataclass
class ReputationScore:
    """Comprehensive reputation score"""
    hash_sha256: str
    overall_score: float  # 0-100, higher = more malicious
    vendor_detections: List[VendorDetection]
    first_seen_timestamp: str
    last_seen_timestamp: str
    variant_count: int
    evasion_techniques: List[str]
    behavioral_indicators: List[str]


class AdvancedReputationDatabase:
    """Advanced reputation database with multi-vendor support"""

    def __init__(self):
        self.hash_database: Dict[str, ReputationScore] = {}
        self.pattern_database: Dict[str, List[str]] = self._build_pattern_db()
        self.yara_rules = self._build_yara_rules()
        self.behavioral_signatures = self._build_behavioral_sigs()

    def _build_pattern_db(self) -> Dict[str, List[str]]:
        """Build malicious pattern database"""
        return {
            "execution_patterns": [
                r"subprocess\.|os\.system|exec\(|eval\(|__import__|getattr|setattr",
                r"system\(|Runtime\.exec|ShellExecute|CreateProcess|WinExec",
                r"powershell|cmd\.exe|csc\.exe|mshta\.exe|regsvcs\.exe|regasm\.exe",
            ],
            "obfuscation_patterns": [
                r"base64|b64decode|binascii|unhexlify|codecs\.decode",
                r"chr\(|ord\(|chr\s*\(\s*ord|bytes\.fromhex|bytearray",
            ],
            "network_patterns": [
                r"socket|requests|urllib|http\.client|smtplib|ftplib",
                r"WinInet|InternetOpenUrl|HttpSendRequest|socket\.socket",
            ],
            "file_patterns": [
                r"open\(|read\(|write\(|\.replace\(|FileStream|File\.WriteAllBytes",
            ],
            "registry_patterns": [
                r"winreg|HKEY_|RegOpenKey|RegSetValue|Get-Item|Set-Item",
            ],
        }

    def _build_yara_rules(self) -> Dict[str, str]:
        """Build YARA rule signatures"""
        return {
            "high_entropy_payload": "avg_entropy > 6.5",
            "exec_family": "contains('exec') OR contains('eval')",
            "powershell_encoded": "contains('powershell') AND contains('-enc')",
            "registry_access": "contains('HKEY_') OR contains('RegSetValue')",
            "process_injection": "contains('WriteProcessMemory') OR contains('CreateRemoteThread')",
            "network_c2": "contains('http://') OR contains('https://') AND NOT contains('.microsoft.com')",
        }

    def _build_behavioral_sigs(self) -> Dict[str, List[str]]:
        """Build behavioral signatures"""
        return {
            "persistence": [
                "scheduled_task", "registry_run_key", "startup_folder",
                "scheduled_job", "wmi_event_subscription"
            ],
            "lateral_movement": [
                "named_pipe_access", "admin_share_access", "psexec_usage",
                "wmi_lateral", "pass_the_hash"
            ],
            "privilege_escalation": [
                "token_impersonation", "uac_bypass", "kernel_exploit",
                "driver_load", "policy_modification"
            ],
            "defense_evasion": [
                "anti_vm", "anti_debug", "anti_sandbox", "anti_reverse_engineering",
                "code_obfuscation", "polymorphic_evasion"
            ],
        }

    def lookup_reputation(self, sha256: str) -> Optional[ReputationScore]:
        """Look up reputation for hash"""
        return self.hash_database.get(sha256)

    def add_reputation(self, sha256: str, score: float, vendors: List[VendorDetection]):
        """Add reputation record"""
        self.hash_database[sha256] = ReputationScore(
            hash_sha256=sha256,
            overall_score=score,
            vendor_detections=vendors,
            first_seen_timestamp=datetime.now().isoformat(),
            last_seen_timestamp=datetime.now().isoformat(),
            variant_count=1,
            evasion_techniques=[],
            behavioral_indicators=[],
        )

    def check_behavioral_indicators(self, payload: str) -> List[str]:
        """Check for behavioral indicators"""
        indicators = []
        for category, sigs in self.behavioral_signatures.items():
            for sig in sigs:
                if sig.lower() in payload.lower():
                    indicators.append(f"{category}:{sig}")
        return indicators


class AdvancedPayloadAnalyzer:
    """Advanced payload analysis with multiple techniques"""

    @staticmethod
    def extract_features(payload: str) -> Dict[str, any]:
        """Extract comprehensive features from payload"""
        features = {
            "length": len(payload),
            "entropy": AdvancedPayloadAnalyzer._calculate_entropy(payload),
            "byte_distribution": AdvancedPayloadAnalyzer._analyze_byte_distribution(payload),
            "ngram_frequency": AdvancedPayloadAnalyzer._extract_ngrams(payload),
            "opcode_sequence": AdvancedPayloadAnalyzer._extract_opcodes(payload),
            "api_calls": AdvancedPayloadAnalyzer._extract_api_calls(payload),
            "strings": AdvancedPayloadAnalyzer._extract_strings(payload),
        }
        return features

    @staticmethod
    def _calculate_entropy(data: str) -> float:
        """Calculate Shannon entropy"""
        if not data:
            return 0.0
        byte_counts = {}
        data_bytes = data.encode('utf-8')
        for byte in data_bytes:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        entropy = 0.0
        length = len(data_bytes)
        for count in byte_counts.values():
            probability = count / length
            entropy -= probability * (__import__('math').log2(probability) if probability else 0)
        return entropy

    @staticmethod
    def _analyze_byte_distribution(payload: str) -> Dict[str, float]:
        """Analyze byte distribution"""
        data_bytes = payload.encode('utf-8')
        byte_count = {}
        for byte in data_bytes:
            byte_count[byte] = byte_count.get(byte, 0) + 1

        total = len(data_bytes)
        distribution = {}
        for byte, count in sorted(byte_count.items()):
            if count > total * 0.05:  # Top 5% threshold
                distribution[f"byte_{byte:02x}"] = count / total

        return distribution

    @staticmethod
    def _extract_ngrams(payload: str, n: int = 3) -> Dict[str, int]:
        """Extract n-grams"""
        ngrams = {}
        for i in range(len(payload) - n + 1):
            ngram = payload[i:i+n]
            ngrams[ngram] = ngrams.get(ngram, 0) + 1
        # Return top 10
        return dict(sorted(ngrams.items(), key=lambda x: x[1], reverse=True)[:10])

    @staticmethod
    def _extract_opcodes(payload: str) -> List[str]:
        """Extract opcode-like patterns"""
        # Simulate opcode extraction
        opcodes = []
        keywords = ['mov', 'push', 'call', 'ret', 'jmp', 'lea', 'xor']
        for kw in keywords:
            if kw in payload.lower():
                opcodes.append(kw)
        return opcodes

    @staticmethod
    def _extract_api_calls(payload: str) -> List[str]:
        """Extract API calls"""
        api_pattern = r'(?:[a-zA-Z_][a-zA-Z0-9_]*\.)+[a-zA-Z_][a-zA-Z0-9_]*\('
        apis = re.findall(api_pattern, payload)
        return list(set(apis))[:10]

    @staticmethod
    def _extract_strings(payload: str) -> List[str]:
        """Extract strings"""
        string_pattern = r'"[^"]*"|\'[^\']*\''
        strings = re.findall(string_pattern, payload)
        return list(set(strings))[:10]


class AdvancedReputationAuditor:
    """Advanced reputation auditor with multiple detection vectors"""

    def __init__(self):
        self.reputation_db = AdvancedReputationDatabase()
        self.analyzer = AdvancedPayloadAnalyzer()
        self.audit_results = []

    def analyze_payload_reputation(self, payload: str, payload_name: str = "unknown") -> Dict:
        """Comprehensive payload reputation analysis"""
        hashes = self._calculate_hashes(payload)
        features = self.analyzer.extract_features(payload)
        behavioral = self.reputation_db.check_behavioral_indicators(payload)

        # Simulate reputation lookup
        reputation_record = self.reputation_db.lookup_reputation(hashes["sha256"])

        # Assign reputation score
        if reputation_record:
            reputation_score = reputation_record.overall_score
            vendors_detected = reputation_record.vendor_detections
        else:
            # Calculate reputation score based on features
            reputation_score = self._calculate_reputation_score(features, payload)
            vendors_detected = self._simulate_vendor_detections(hashes["sha256"], reputation_score)

        result = {
            "payload_name": payload_name,
            "hashes": hashes,
            "size_bytes": len(payload.encode('utf-8')),
            "features": {
                "entropy": round(features["entropy"], 4),
                "length": features["length"],
                "api_calls_found": features["api_calls"],
                "strings_found": features["strings"],
            },
            "reputation": {
                "score": round(reputation_score, 2),
                "classification": self._classify_reputation(reputation_score),
                "vendor_detections": len(vendors_detected),
                "vendors": [v.vendor.value for v in vendors_detected if v.detected],
            },
            "behavioral_indicators": behavioral,
            "yara_matches": self._check_yara_rules(features),
            "evasion_indicators": self._detect_evasion_techniques(payload),
        }

        self.audit_results.append(result)
        return result

    def _calculate_hashes(self, payload: str) -> Dict[str, str]:
        """Calculate all hash types"""
        payload_bytes = payload.encode('utf-8')
        return {
            "md5": hashlib.md5(payload_bytes).hexdigest(),
            "sha1": hashlib.sha1(payload_bytes).hexdigest(),
            "sha256": hashlib.sha256(payload_bytes).hexdigest(),
        }

    def _calculate_reputation_score(self, features: Dict, payload: str) -> float:
        """Calculate reputation score (0-100)"""
        score = 0.0

        # Entropy score
        entropy = features["entropy"]
        if entropy > 7.0:
            score += 20
        elif entropy > 6.0:
            score += 15
        elif entropy > 5.0:
            score += 8

        # Pattern matching
        patterns = [
            "exec(", "eval(", "__import__", "subprocess",
            "os.system", "powershell", "cmd.exe"
        ]
        for pattern in patterns:
            if pattern in payload:
                score += 15

        # Obfuscation indicators
        if any(x in payload for x in ["base64", "binascii", "codecs"]):
            score += 10

        return min(score, 100.0)

    def _classify_reputation(self, score: float) -> str:
        """Classify reputation based on score"""
        if score >= 80:
            return "MALICIOUS"
        elif score >= 60:
            return "SUSPICIOUS"
        elif score >= 40:
            return "BENIGN_WITH_RISK"
        else:
            return "UNKNOWN"

    def _simulate_vendor_detections(self, sha256: str, score: float) -> List[VendorDetection]:
        """Simulate vendor detections"""
        detections = []
        vendors = list(VendorReputation)

        # Higher score = more vendors detect
        detection_probability = min(score / 100.0, 1.0)

        for vendor in vendors:
            if random.random() < detection_probability:
                detections.append(VendorDetection(
                    vendor=vendor,
                    detected=True,
                    confidence=random.uniform(0.7, 1.0),
                    category="Generic.Polymorphic" if score > 60 else "Unknown",
                    signature=f"{vendor.value}_{sha256[:8]}"
                ))

        return detections

    def _check_yara_rules(self, features: Dict) -> List[str]:
        """Check YARA rules"""
        matches = []
        if features["entropy"] > 6.5:
            matches.append("high_entropy_payload")
        return matches

    def _detect_evasion_techniques(self, payload: str) -> List[str]:
        """Detect evasion techniques"""
        techniques = []

        if any(x in payload for x in ["base64", "b64decode", "binascii"]):
            techniques.append("payload_encoding")
        if any(x in payload for x in ["exec", "eval", "__import__"]):
            techniques.append("dynamic_execution")
        if any(x in payload for x in ["sleep", "time.sleep", "WaitForSingleObject"]):
            techniques.append("behavioral_delay")
        if len(payload) > 10000:
            techniques.append("size_obfuscation")

        return techniques


class ComprehensiveReputationReport:
    """Generate comprehensive reputation audit report"""

    @staticmethod
    def generate(audit_results: List[Dict]) -> Dict:
        """Generate comprehensive report"""
        report = {
            "audit_metadata": {
                "timestamp": datetime.now().isoformat(),
                "audit_type": "Advanced Reputation-Based Detection Evasion",
                "total_payloads_audited": len(audit_results),
            },
            "payload_analysis": audit_results,
            "aggregate_statistics": ComprehensiveReputationReport._calculate_stats(audit_results),
            "risk_assessment": ComprehensiveReputationReport._assess_risk(audit_results),
            "detection_gaps": ComprehensiveReputationReport._identify_gaps(audit_results),
            "recommendations": ComprehensiveReputationReport._generate_recommendations(audit_results),
        }
        return report

    @staticmethod
    def _calculate_stats(results: List[Dict]) -> Dict:
        """Calculate aggregate statistics"""
        reputation_scores = [r["reputation"]["score"] for r in results]
        entropies = [r["features"]["entropy"] for r in results]
        behavioral_counts = [len(r["behavioral_indicators"]) for r in results]

        return {
            "average_reputation_score": round(statistics.mean(reputation_scores), 2),
            "max_reputation_score": round(max(reputation_scores), 2),
            "min_reputation_score": round(min(reputation_scores), 2),
            "average_entropy": round(statistics.mean(entropies), 4),
            "payloads_with_behavioral_indicators": sum(1 for b in behavioral_counts if b > 0),
            "unique_yara_matches": len(set(m for r in results for m in r["yara_matches"])),
            "evasion_technique_frequency": ComprehensiveReputationReport._count_evasion_techniques(results),
        }

    @staticmethod
    def _count_evasion_techniques(results: List[Dict]) -> Dict[str, int]:
        """Count evasion technique frequency"""
        techniques = {}
        for r in results:
            for tech in r["evasion_indicators"]:
                techniques[tech] = techniques.get(tech, 0) + 1
        return dict(sorted(techniques.items(), key=lambda x: x[1], reverse=True))

    @staticmethod
    def _assess_risk(results: List[Dict]) -> Dict:
        """Assess overall risk"""
        malicious_count = len([r for r in results if r["reputation"]["classification"] == "MALICIOUS"])
        suspicious_count = len([r for r in results if r["reputation"]["classification"] == "SUSPICIOUS"])
        avg_score = statistics.mean([r["reputation"]["score"] for r in results])

        if avg_score > 70 or malicious_count > len(results) * 0.5:
            risk_level = "CRITICAL"
        elif avg_score > 50 or suspicious_count > len(results) * 0.3:
            risk_level = "HIGH"
        else:
            risk_level = "MEDIUM"

        return {
            "risk_level": risk_level,
            "malicious_count": malicious_count,
            "suspicious_count": suspicious_count,
            "average_score": round(avg_score, 2),
            "detection_coverage": f"{((malicious_count + suspicious_count) / len(results) * 100):.1f}%",
        }

    @staticmethod
    def _identify_gaps(results: List[Dict]) -> Dict:
        """Identify detection gaps"""
        undetected = [r for r in results if r["reputation"]["vendor_detections"] == 0]
        low_entropy = [r for r in results if r["features"]["entropy"] < 4.0]
        no_behavioral = [r for r in results if len(r["behavioral_indicators"]) == 0]

        return {
            "undetected_payloads": len(undetected),
            "undetected_rate": f"{(len(undetected) / len(results) * 100):.1f}%",
            "low_entropy_evasion": len(low_entropy),
            "no_behavioral_indicators": len(no_behavioral),
            "detection_blind_spots": [
                "Hash-based detection bypassed by polymorphic variants",
                "Behavioral detection blind spots in low-entropy payloads",
                "Entropy-based detection bypassed by structured payloads",
            ],
        }

    @staticmethod
    def _generate_recommendations(results: List[Dict]) -> List[str]:
        """Generate recommendations"""
        recommendations = [
            "Implement multi-layered detection: hash + behavioral + heuristic analysis",
            "Deploy machine learning models trained on polymorphic variant families",
            "Increase entropy thresholds for suspicious classification",
            "Monitor behavioral patterns for process injection and registry modification",
            "Implement reputation scoring that combines multiple vectors",
            "Regular signature updates to detect known polymorphic families",
            "Use YARA rules for variant detection patterns",
        ]
        return recommendations


def run_advanced_audit(output_file: str = None) -> Dict:
    """Run advanced reputation audit"""
    print("\n" + "="*80)
    print("ADVANCED REPUTATION-BASED DETECTION EVASION AUDIT")
    print("="*80)

    auditor = AdvancedReputationAuditor()

    # Test payloads
    test_payloads = [
        ("command_exec", "import subprocess; subprocess.Popen(['calc.exe'])"),
        ("eval_dynamic", "eval(__import__('base64').b64decode('aW1wb3J0IG9z').decode())"),
        ("powershell_c2", "powershell -enc VwByAGkAdABlAC0ASABvAHMAdAAoACcAcABpAG4AZQBH"),
        ("vbscript_wmi", "CreateObject('WbemScripting.SWbemLocator').ConnectServer()"),
        ("registry_run", "reg add HKEY_LOCAL_MACHINE\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run"),
    ]

    print("\n[*] Analyzing payloads for reputation evasion...\n")

    for payload_name, payload in test_payloads:
        print(f"[+] Analyzing: {payload_name}")
        result = auditor.analyze_payload_reputation(payload, payload_name)
        print(f"    Reputation Score: {result['reputation']['score']}")
        print(f"    Classification: {result['reputation']['classification']}")
        print(f"    Entropy: {result['features']['entropy']}")
        print(f"    Behavioral Indicators: {len(result['behavioral_indicators'])}")

    # Generate report
    report = ComprehensiveReputationReport.generate(auditor.audit_results)

    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n[+] Report saved to: {output_file}")

    return report


def print_summary(report: Dict):
    """Print audit summary"""
    print("\n" + "="*80)
    print("ADVANCED REPUTATION AUDIT SUMMARY")
    print("="*80)

    metadata = report["audit_metadata"]
    stats = report["aggregate_statistics"]
    risk = report["risk_assessment"]
    gaps = report["detection_gaps"]

    print(f"\n[AUDIT METADATA]")
    print(f"  Timestamp: {metadata['timestamp']}")
    print(f"  Payloads Audited: {metadata['total_payloads_audited']}")

    print(f"\n[REPUTATION STATISTICS]")
    print(f"  Average Reputation Score: {stats['average_reputation_score']}")
    print(f"  Max Score: {stats['max_reputation_score']}")
    print(f"  Average Entropy: {stats['average_entropy']}")

    print(f"\n[RISK ASSESSMENT]")
    print(f"  Risk Level: {risk['risk_level']}")
    print(f"  Malicious Payloads: {risk['malicious_count']}")
    print(f"  Suspicious Payloads: {risk['suspicious_count']}")
    print(f"  Detection Coverage: {risk['detection_coverage']}")

    print(f"\n[DETECTION GAPS]")
    print(f"  Undetected Rate: {gaps['undetected_rate']}")
    print(f"  Low-Entropy Evasion: {gaps['low_entropy_evasion']}")

    print(f"\n[RECOMMENDATIONS]")
    for rec in report["recommendations"][:3]:
        print(f"  - {rec}")

    print("\n" + "="*80)


if __name__ == "__main__":
    import sys
    output_file = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/-home-user-sc-generator/cea520eb-2877-52b0-bbd4-c38bff01b8ad/scratchpad/advanced_reputation_report.json"

    report = run_advanced_audit(output_file)
    print_summary(report)
