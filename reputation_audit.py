#!/usr/bin/env python3
"""
Reputation-Based Detection Evasion Audit
=========================================

Comprehensive reputation audit to verify payloads against reputation services:
- Hash-based reputation verification
- Payload signature analysis
- Behavioral pattern detection
- Evasion rate against reputation databases
- Polymorphic variant uniqueness verification
"""

import hashlib
import json
import statistics
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import random
import string


class ReputationLevel(Enum):
    """Reputation scoring levels"""
    TRUSTED = "trusted"
    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    UNKNOWN = "unknown"


@dataclass
class PayloadSignature:
    """Payload signature data"""
    hash_md5: str
    hash_sha1: str
    hash_sha256: str
    payload_content: str
    size_bytes: int
    entropy: float
    suspicious_patterns: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "md5": self.hash_md5,
            "sha1": self.hash_sha1,
            "sha256": self.hash_sha256,
            "size": self.size_bytes,
            "entropy": self.entropy,
            "suspicious_patterns": self.suspicious_patterns
        }


@dataclass
class ReputationRecord:
    """Reputation database record"""
    hash_sha256: str
    reputation_level: ReputationLevel
    detection_count: int
    first_seen: str
    last_seen: str
    vendors_detected: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


class ReputationDatabase:
    """Simulated reputation database (would be VirusTotal, AlienVault OTX, etc)"""

    def __init__(self):
        self.known_hashes: Dict[str, ReputationRecord] = {}
        self.payload_patterns: Dict[str, ReputationLevel] = {}
        self._initialize_database()

    def _initialize_database(self):
        """Initialize with known malicious patterns/hashes"""
        # Common malicious indicators
        malicious_patterns = [
            "exec(",
            "eval(",
            "subprocess.Popen",
            "__import__('os').system",
            "powershell -enc",
            "cmd /c",
            "CreateObject('WScript.Shell')",
            "WScript.CreateObject",
            "GetObject('winmgmts')",
            "SelectSingleNode",
            "System.Diagnostics.Process",
            "System.Net.ServicePointManager",
            "System.Reflection.Assembly",
        ]

        for pattern in malicious_patterns:
            self.payload_patterns[pattern] = ReputationLevel.SUSPICIOUS

    def add_known_hash(self, sha256: str, reputation: ReputationLevel,
                       detection_count: int = 0, vendors: List[str] = None):
        """Add hash to reputation database"""
        self.known_hashes[sha256] = ReputationRecord(
            hash_sha256=sha256,
            reputation_level=reputation,
            detection_count=detection_count,
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat(),
            vendors_detected=vendors or []
        )

    def lookup_hash(self, sha256: str) -> Optional[ReputationRecord]:
        """Look up hash in reputation database"""
        return self.known_hashes.get(sha256)

    def check_patterns(self, payload: str) -> List[str]:
        """Check payload for suspicious patterns"""
        detected_patterns = []
        for pattern, reputation in self.payload_patterns.items():
            if pattern in payload:
                detected_patterns.append(pattern)
        return detected_patterns


class PayloadAnalyzer:
    """Analyze payload characteristics"""

    @staticmethod
    def calculate_hashes(payload: str) -> Tuple[str, str, str]:
        """Calculate MD5, SHA1, SHA256 hashes"""
        payload_bytes = payload.encode('utf-8')
        md5 = hashlib.md5(payload_bytes).hexdigest()
        sha1 = hashlib.sha1(payload_bytes).hexdigest()
        sha256 = hashlib.sha256(payload_bytes).hexdigest()
        return md5, sha1, sha256

    @staticmethod
    def calculate_entropy(data: str) -> float:
        """Calculate Shannon entropy of payload"""
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
    def analyze_payload(payload: str, reputation_db: ReputationDatabase) -> PayloadSignature:
        """Full payload analysis"""
        md5, sha1, sha256 = PayloadAnalyzer.calculate_hashes(payload)
        entropy = PayloadAnalyzer.calculate_entropy(payload)
        suspicious_patterns = reputation_db.check_patterns(payload)

        return PayloadSignature(
            hash_md5=md5,
            hash_sha1=sha1,
            hash_sha256=sha256,
            payload_content=payload,
            size_bytes=len(payload.encode('utf-8')),
            entropy=entropy,
            suspicious_patterns=suspicious_patterns
        )


class ReputationAuditor:
    """Audit payloads against reputation services"""

    def __init__(self):
        self.reputation_db = ReputationDatabase()
        self.analyzer = PayloadAnalyzer()
        self.audit_results = []
        self.seen_hashes: Set[str] = set()

    def audit_payload(self, payload: str, payload_name: str = "unknown") -> Dict:
        """Audit a single payload"""
        signature = self.analyzer.analyze_payload(payload, self.reputation_db)

        # Check reputation
        reputation_record = self.reputation_db.lookup_hash(signature.hash_sha256)

        if reputation_record:
            reputation = reputation_record.reputation_level
            detection_count = reputation_record.detection_count
            vendors = reputation_record.vendors_detected
            flagged = True
        else:
            reputation = ReputationLevel.UNKNOWN
            detection_count = 0
            vendors = []
            flagged = False

        # Check if hash is new/unique
        is_unique = signature.hash_sha256 not in self.seen_hashes
        self.seen_hashes.add(signature.hash_sha256)

        result = {
            "payload_name": payload_name,
            "hash_sha256": signature.hash_sha256,
            "hash_sha1": signature.hash_sha1,
            "hash_md5": signature.hash_md5,
            "size_bytes": signature.size_bytes,
            "entropy": round(signature.entropy, 4),
            "reputation_status": reputation.value,
            "flagged_by_reputation": flagged,
            "detection_count": detection_count,
            "vendors_detected": vendors,
            "suspicious_patterns_found": signature.suspicious_patterns,
            "is_unique_hash": is_unique,
            "polymorphic_evasion": is_unique and not flagged,
        }

        self.audit_results.append(result)
        return result

    def audit_polymorphic_variants(self, base_payload: str, variants: List[str],
                                   base_name: str = "payload") -> Dict:
        """Audit multiple polymorphic variants"""
        print(f"\n[*] Auditing {len(variants)} polymorphic variants...")

        variant_results = []
        for i, variant in enumerate(variants):
            result = self.audit_payload(variant, f"{base_name}_variant_{i+1}")
            variant_results.append(result)

        # Calculate statistics
        unique_hashes = len(set(r["hash_sha256"] for r in variant_results))
        evaded_reputation = sum(1 for r in variant_results if r["polymorphic_evasion"])
        avg_entropy = statistics.mean([r["entropy"] for r in variant_results])
        max_entropy = max([r["entropy"] for r in variant_results])
        min_entropy = min([r["entropy"] for r in variant_results])

        analysis = {
            "base_payload": base_payload,
            "total_variants": len(variants),
            "unique_hashes": unique_hashes,
            "evasion_rate": (unique_hashes / len(variants)) * 100,
            "polymorphic_evasion_count": evaded_reputation,
            "polymorphic_evasion_rate": (evaded_reputation / len(variants)) * 100,
            "average_entropy": round(avg_entropy, 4),
            "max_entropy": round(max_entropy, 4),
            "min_entropy": round(min_entropy, 4),
            "variants": variant_results,
        }

        return analysis

    def generate_reputation_report(self, analysis: Dict) -> Dict:
        """Generate comprehensive reputation audit report"""
        variants = analysis.get("variants", [])

        # Categorize by reputation
        trusted = [v for v in variants if v["reputation_status"] == "trusted"]
        benign = [v for v in variants if v["reputation_status"] == "benign"]
        suspicious = [v for v in variants if v["reputation_status"] == "suspicious"]
        malicious = [v for v in variants if v["reputation_status"] == "malicious"]
        unknown = [v for v in variants if v["reputation_status"] == "unknown"]

        # Evasion analysis
        evaded_reputation = [v for v in variants if v["polymorphic_evasion"]]
        flagged = [v for v in variants if v["flagged_by_reputation"]]

        # Pattern analysis
        all_patterns = []
        for v in variants:
            all_patterns.extend(v["suspicious_patterns_found"])
        pattern_frequency = {}
        for pattern in all_patterns:
            pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1

        report = {
            "audit_timestamp": datetime.now().isoformat(),
            "audit_type": "Reputation-Based Detection Evasion",
            "test_parameters": {
                "total_variants_audited": len(variants),
                "base_payload": analysis.get("base_payload", ""),
            },
            "reputation_classification": {
                "trusted_count": len(trusted),
                "benign_count": len(benign),
                "suspicious_count": len(suspicious),
                "malicious_count": len(malicious),
                "unknown_count": len(unknown),
            },
            "evasion_effectiveness": {
                "variants_evading_reputation": len(evaded_reputation),
                "evasion_rate_percent": round(analysis["polymorphic_evasion_rate"], 2),
                "flagged_variants": len(flagged),
                "unflagged_variants": len(variants) - len(flagged),
                "reputation_bypass_rate": round((len(variants) - len(flagged)) / len(variants) * 100, 2),
            },
            "uniqueness_analysis": {
                "total_unique_hashes": analysis["unique_hashes"],
                "hash_diversity_rate": round(analysis["evasion_rate"], 2),
                "collision_count": len(variants) - analysis["unique_hashes"],
            },
            "entropy_analysis": {
                "average_entropy": analysis["average_entropy"],
                "max_entropy": analysis["max_entropy"],
                "min_entropy": analysis["min_entropy"],
                "entropy_variance": round(statistics.variance([v["entropy"] for v in variants]), 4),
            },
            "suspicious_pattern_analysis": {
                "patterns_detected": len(set(all_patterns)),
                "total_pattern_instances": len(all_patterns),
                "pattern_frequency": dict(sorted(pattern_frequency.items(),
                                               key=lambda x: x[1], reverse=True)),
            },
            "variant_details": variants,
            "risk_assessment": self._assess_risk(analysis, evaded_reputation, flagged),
            "conclusions": self._generate_conclusions(analysis, evaded_reputation, flagged),
        }

        return report

    def _assess_risk(self, analysis: Dict, evaded: List[Dict], flagged: List[Dict]) -> Dict:
        """Assess risk level"""
        evasion_rate = analysis["polymorphic_evasion_rate"]

        if evasion_rate > 80:
            risk_level = "CRITICAL"
        elif evasion_rate > 60:
            risk_level = "HIGH"
        elif evasion_rate > 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "risk_level": risk_level,
            "detection_gap": f"{evasion_rate:.1f}% of variants bypass reputation detection",
            "primary_concern": "Polymorphic variants evading hash-based reputation lookups",
            "detection_resistance": len(evaded) > 0,
        }

    def _generate_conclusions(self, analysis: Dict, evaded: List[Dict], flagged: List[Dict]) -> List[str]:
        """Generate audit conclusions"""
        conclusions = []

        total = analysis["total_variants"]
        evasion_rate = analysis["polymorphic_evasion_rate"]

        if evasion_rate > 75:
            conclusions.append("CRITICAL: Polymorphic variants achieve high reputation evasion rates")
        if len(evaded) > 0:
            conclusions.append(f"Detected {len(evaded)} variants evading reputation detection through hash uniqueness")
        if analysis["unique_hashes"] == total:
            conclusions.append("All variants produce unique hashes - maximum hash-based evasion")
        if len(flagged) == 0:
            conclusions.append("None of the variants were flagged by reputation database")

        avg_entropy = analysis["average_entropy"]
        if avg_entropy > 6.0:
            conclusions.append(f"High payload entropy ({avg_entropy:.2f}) may confuse entropy-based detection")

        return conclusions


def generate_sample_polymorphic_variants(base_payload: str, count: int = 10) -> List[str]:
    """Generate sample polymorphic variants for testing"""
    variants = []

    for i in range(count):
        # Variant strategy: shuffle keywords and add junk code
        variant = base_payload

        # Add random variable assignments
        junk_vars = [f"_v{j} = {random.randint(1, 1000)}" for j in range(random.randint(1, 3))]
        variant = variant + "\n" + "\n".join(junk_vars)

        # Vary the payload slightly
        if i % 2 == 0:
            variant = variant.replace("exec", "eval") if "exec" in variant else variant
        if i % 3 == 0:
            variant = "# Comment\n" + variant
        if i % 4 == 0:
            variant = variant + f"\n# ID: {random.randint(10000, 99999)}"

        variants.append(variant)

    return variants


def run_reputation_audit(output_file: str = None) -> Dict:
    """Run comprehensive reputation audit"""
    print("\n" + "="*80)
    print("REPUTATION-BASED DETECTION EVASION AUDIT")
    print("="*80)

    # Initialize auditor
    auditor = ReputationAuditor()

    # Test payloads
    test_cases = [
        {
            "name": "Basic_Command_Execution",
            "payload": "import subprocess; subprocess.run(['cmd', '/c', 'dir'], shell=True)",
            "variants_count": 5
        },
        {
            "name": "Obfuscated_Exec",
            "payload": "__import__('os').system('dir')",
            "variants_count": 5
        },
        {
            "name": "PowerShell_Execution",
            "payload": "powershell -enc VwByAGkAdABlAC0ASABvAHMAdAAoACcAaABlAGwAbABvACcA",
            "variants_count": 5
        },
    ]

    all_reports = []

    for test_case in test_cases:
        print(f"\n[*] Testing: {test_case['name']}")
        print(f"    Base Payload: {test_case['payload'][:60]}...")

        # Generate variants
        variants = generate_sample_polymorphic_variants(
            test_case['payload'],
            test_case['variants_count']
        )

        # Audit variants
        analysis = auditor.audit_polymorphic_variants(
            test_case['payload'],
            variants,
            test_case['name']
        )

        # Generate report
        report = auditor.generate_reputation_report(analysis)
        all_reports.append(report)

        # Print summary
        print(f"    Unique Hashes: {analysis['unique_hashes']}/{len(variants)}")
        print(f"    Evasion Rate: {analysis['polymorphic_evasion_rate']:.1f}%")
        print(f"    Avg Entropy: {analysis['average_entropy']:.2f}")
        print(f"    Flagged by Reputation: {len([v for v in analysis['variants'] if v['flagged_by_reputation']])}")

    # Aggregate results
    master_report = {
        "audit_summary": {
            "timestamp": datetime.now().isoformat(),
            "audit_type": "Multi-Case Reputation Audit",
            "test_cases_count": len(test_cases),
            "total_variants_audited": sum(len(r["variant_details"]) for r in all_reports),
        },
        "case_reports": all_reports,
        "aggregate_statistics": {
            "total_unique_hashes": sum(len(set(r["hash_sha256"] for r in report["variant_details"]))
                                       for report in all_reports),
            "average_evasion_rate": round(statistics.mean([
                r["evasion_effectiveness"]["evasion_rate_percent"]
                for r in all_reports
            ]), 2),
            "average_reputation_bypass_rate": round(statistics.mean([
                r["evasion_effectiveness"]["reputation_bypass_rate"]
                for r in all_reports
            ]), 2),
            "average_entropy": round(statistics.mean([
                r["entropy_analysis"]["average_entropy"]
                for r in all_reports
            ]), 4),
        },
        "risk_summary": {
            "critical_cases": len([r for r in all_reports if r["risk_assessment"]["risk_level"] == "CRITICAL"]),
            "high_risk_cases": len([r for r in all_reports if r["risk_assessment"]["risk_level"] == "HIGH"]),
            "overall_risk": "CRITICAL" if any(r["risk_assessment"]["risk_level"] == "CRITICAL" for r in all_reports) else "HIGH",
        },
    }

    # Save report
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(master_report, f, indent=2, default=str)
        print(f"\n[+] Report saved to: {output_file}")

    return master_report


def print_audit_summary(report: Dict):
    """Print audit summary"""
    print("\n" + "="*80)
    print("REPUTATION AUDIT SUMMARY")
    print("="*80)

    summary = report["audit_summary"]
    agg_stats = report["aggregate_statistics"]
    risk = report["risk_summary"]

    print(f"\n[AUDIT OVERVIEW]")
    print(f"  Timestamp: {summary['timestamp']}")
    print(f"  Test Cases: {summary['test_cases_count']}")
    print(f"  Total Variants Audited: {summary['total_variants_audited']}")

    print(f"\n[AGGREGATE STATISTICS]")
    print(f"  Total Unique Hashes: {agg_stats['total_unique_hashes']}")
    print(f"  Average Evasion Rate: {agg_stats['average_evasion_rate']:.1f}%")
    print(f"  Average Reputation Bypass Rate: {agg_stats['average_reputation_bypass_rate']:.1f}%")
    print(f"  Average Entropy: {agg_stats['average_entropy']:.4f}")

    print(f"\n[RISK ASSESSMENT]")
    print(f"  Critical Cases: {risk['critical_cases']}")
    print(f"  High Risk Cases: {risk['high_risk_cases']}")
    print(f"  Overall Risk Level: {risk['overall_risk']}")

    print(f"\n[INDIVIDUAL CASE RESULTS]")
    for i, case_report in enumerate(report["case_reports"], 1):
        print(f"\n  Case {i}: {case_report['test_parameters'].get('base_payload', 'Unknown')[:40]}...")
        evasion = case_report["evasion_effectiveness"]
        print(f"    Evasion Rate: {evasion['evasion_rate_percent']:.1f}%")
        print(f"    Reputation Bypass: {evasion['reputation_bypass_rate']:.1f}%")
        print(f"    Flagged Variants: {evasion['flagged_variants']}")
        print(f"    Risk Level: {case_report['risk_assessment']['risk_level']}")

    print("\n" + "="*80)


if __name__ == "__main__":
    import sys

    output_file = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/-home-user-sc-generator/cea520eb-2877-52b0-bbd4-c38bff01b8ad/scratchpad/reputation_audit_report.json"

    report = run_reputation_audit(output_file)
    print_audit_summary(report)

    print(f"\n[+] Full report saved to: {output_file}")
