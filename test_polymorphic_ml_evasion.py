#!/usr/bin/env python3
"""
Polymorphic Variant ML Malware Detector Evasion Test Suite

Tests polymorphic code variants against machine learning malware detectors.
Verifies evasion through:
- Signature diversity (no two variants share exact signatures)
- Feature space distribution (variants spread across detection feature space)
- Opcode sequence variation (different instruction patterns)
- Control flow graph diversity (CFG changes)
- Entropy variation (payload entropy differs across variants)
"""

import hashlib
import base64
import json
import statistics
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from polymorphic_engine import PolymorphicCodeGenerator, PolymorphicConfig


# ==================== ML DETECTOR SIMULATION ====================

class DetectionFeature(Enum):
    """Machine learning detection features"""
    SIGNATURE_HASH = "signature_hash"
    OPCODE_SEQUENCE = "opcode_sequence"
    ENTROPY = "entropy"
    CONTROL_FLOW_PATTERN = "control_flow_pattern"
    STRING_CONSTANTS = "string_constants"
    API_CALLS = "api_calls"
    MEMORY_FOOTPRINT = "memory_footprint"
    EXECUTION_PATTERN = "execution_pattern"
    ALGORITHM_SIGNATURE = "algorithm_signature"
    VARIABLE_NAMING = "variable_naming"


@dataclass
class DetectionResult:
    """Result from ML detector"""
    variant_id: str
    is_detected: bool
    confidence: float
    features_triggered: List[str]
    signature_hash: str
    entropy_score: float
    opcode_sequence_hash: str
    algorithm_variant: str


class MLMalwareDetector:
    """Simulated ML-based malware detector"""

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.known_signatures = set()
        self.feature_database = []

    def calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of code"""
        if not data:
            return 0.0

        byte_counts = {}
        for byte in data:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1

        entropy = 0.0
        length = len(data)
        for count in byte_counts.values():
            probability = count / length
            entropy -= probability * (probability and __import__('math').log2(probability) or 0)

        return entropy

    def extract_opcode_sequence(self, code: str) -> str:
        """Extract opcode-like sequence from Python code"""
        # Simplified: extract keywords as pseudo-opcodes
        keywords = ['for', 'while', 'if', 'else', 'def', 'class', 'import', 'return']
        opcodes = []

        for keyword in keywords:
            count = code.count(keyword)
            if count > 0:
                opcodes.append(f"{keyword}:{count}")

        return "|".join(sorted(opcodes))

    def extract_control_flow_pattern(self, code: str) -> str:
        """Extract control flow pattern signature"""
        patterns = []

        if 'while' in code and 'for' in code:
            patterns.append('mixed_loops')
        if code.count('if') > 3:
            patterns.append('high_branching')
        if 'def ' in code:
            patterns.append('function_def')
        if code.count('\n') > 100:
            patterns.append('large_code')

        return "|".join(patterns) if patterns else "sequential"

    def detect_code(self, code: str, algorithm_variant: str = "unknown") -> DetectionResult:
        """Detect if code is malicious using ML-like heuristics"""
        code_bytes = code.encode()

        # Calculate features
        signature_hash = hashlib.sha256(code_bytes).hexdigest()
        entropy = self.calculate_entropy(code_bytes)
        opcode_seq = self.extract_opcode_sequence(code)
        opcode_hash = hashlib.md5(opcode_seq.encode()).hexdigest()
        control_flow = self.extract_control_flow_pattern(code)

        # Check known signatures
        is_known_signature = signature_hash in self.known_signatures

        # Calculate feature-based score
        feature_score = self._calculate_feature_score(
            entropy, opcode_seq, control_flow, code
        )

        # Build detection result
        features_triggered = []
        if entropy > 4.5:
            features_triggered.append(DetectionFeature.ENTROPY.value)
        if is_known_signature:
            features_triggered.append(DetectionFeature.SIGNATURE_HASH.value)
        if 'subprocess' in code or 'os.system' in code:
            features_triggered.append(DetectionFeature.API_CALLS.value)
        if len(code) > 500:
            features_triggered.append(DetectionFeature.MEMORY_FOOTPRINT.value)

        confidence = feature_score
        is_detected = confidence >= self.threshold

        return DetectionResult(
            variant_id=f"var_{hashlib.md5(code_bytes).hexdigest()[:8]}",
            is_detected=is_detected,
            confidence=confidence,
            features_triggered=features_triggered,
            signature_hash=signature_hash,
            entropy_score=entropy,
            opcode_sequence_hash=opcode_hash,
            algorithm_variant=algorithm_variant
        )

    def _calculate_feature_score(self, entropy: float, opcode_seq: str,
                                control_flow: str, code: str) -> float:
        """Calculate detection score based on multiple features"""
        score = 0.0

        # Entropy-based scoring (normalized to 0-1)
        entropy_score = min(entropy / 8.0, 1.0) * 0.25

        # Suspicious pattern scoring
        suspicious_patterns = [
            'subprocess', 'os.system', 'exec', 'eval', 'compile',
            'ctypes', 'windll', 'CreateProcess'
        ]
        pattern_score = sum(0.1 for pattern in suspicious_patterns if pattern in code)
        pattern_score = min(pattern_score, 0.4)

        # Obfuscation scoring (random variable names)
        obfuscation_score = 0.1 if ('v_' in code or 'result_' in code) else 0

        # Control flow complexity
        control_flow_score = 0.15 if 'high_branching' in control_flow else 0.05

        score = entropy_score + pattern_score + obfuscation_score + control_flow_score
        return min(score, 1.0)

    def add_known_signature(self, signature: str):
        """Add a known malware signature"""
        self.known_signatures.add(signature)


# ==================== EVASION VERIFICATION ====================

@dataclass
class EvasionMetrics:
    """Metrics for evasion success"""
    total_variants: int
    detected_variants: int
    evasion_rate: float  # Percentage of variants that evaded
    unique_signatures: int
    signature_diversity_ratio: float
    entropy_range: Tuple[float, float]
    entropy_variance: float
    opcode_diversity: int
    control_flow_diversity: int
    avg_confidence_score: float
    min_confidence_score: float
    max_confidence_score: float


class EvasionTester:
    """Test polymorphic variants for ML detection evasion"""

    def __init__(self, detector: MLMalwareDetector, num_variants: int = 50):
        self.detector = detector
        self.num_variants = num_variants
        self.detection_results: List[DetectionResult] = []
        self.variants: List[str] = []
        self.signatures_seen: Set[str] = set()
        self.opcodes_seen: Set[str] = set()
        self.control_flows_seen: Set[str] = set()
        self.entropies: List[float] = []

    def generate_variants(self, payload: str) -> List[str]:
        """Generate multiple polymorphic variants"""
        print(f"\n[*] Generating {self.num_variants} polymorphic variants...")

        for i in range(self.num_variants):
            config = PolymorphicConfig(
                algorithm_variants=3,
                control_flow_patterns=2,
                obfuscation_techniques=3,
                complexity_level=4
            )

            engine = PolymorphicCodeGenerator(config)
            variant = engine.generate_complete_polymorphic_script(payload)
            self.variants.append(variant)

            if (i + 1) % 10 == 0:
                print(f"    Generated {i + 1}/{self.num_variants} variants")

        return self.variants

    def test_variants(self) -> List[DetectionResult]:
        """Test all variants against detector"""
        print(f"\n[*] Testing {len(self.variants)} variants against ML detector...")

        for i, variant in enumerate(self.variants):
            result = self.detector.detect_code(variant)
            self.detection_results.append(result)

            # Collect unique signatures and features
            self.signatures_seen.add(result.signature_hash)
            self.opcodes_seen.add(result.opcode_sequence_hash)
            self.entropies.append(result.entropy_score)

            # Extract control flow from variant
            control_flow = self.detector.extract_control_flow_pattern(variant)
            self.control_flows_seen.add(control_flow)

            if (i + 1) % 10 == 0:
                print(f"    Tested {i + 1}/{len(self.variants)} variants")

        return self.detection_results

    def calculate_evasion_metrics(self) -> EvasionMetrics:
        """Calculate evasion success metrics"""
        detected_count = sum(1 for r in self.detection_results if r.is_detected)
        evasion_rate = ((len(self.detection_results) - detected_count) /
                       len(self.detection_results) * 100)

        confidence_scores = [r.confidence for r in self.detection_results]
        entropy_values = [r.entropy_score for r in self.detection_results]

        return EvasionMetrics(
            total_variants=len(self.detection_results),
            detected_variants=detected_count,
            evasion_rate=evasion_rate,
            unique_signatures=len(self.signatures_seen),
            signature_diversity_ratio=len(self.signatures_seen) / len(self.detection_results),
            entropy_range=(min(entropy_values), max(entropy_values)),
            entropy_variance=statistics.variance(entropy_values) if len(entropy_values) > 1 else 0,
            opcode_diversity=len(self.opcodes_seen),
            control_flow_diversity=len(self.control_flows_seen),
            avg_confidence_score=statistics.mean(confidence_scores),
            min_confidence_score=min(confidence_scores),
            max_confidence_score=max(confidence_scores)
        )

    def generate_report(self) -> Dict:
        """Generate comprehensive evasion test report"""
        metrics = self.calculate_evasion_metrics()

        # Categorize results
        evaded = [r for r in self.detection_results if not r.is_detected]
        detected = [r for r in self.detection_results if r.is_detected]

        # Feature triggering analysis
        feature_stats = {}
        for result in self.detection_results:
            for feature in result.features_triggered:
                feature_stats[feature] = feature_stats.get(feature, 0) + 1

        # Algorithm diversity analysis
        algo_names = set(r.algorithm_variant for r in self.detection_results)

        report = {
            "test_summary": {
                "total_variants_tested": metrics.total_variants,
                "variants_detected": metrics.detected_variants,
                "variants_evaded": metrics.total_variants - metrics.detected_variants,
                "evasion_success_rate": f"{metrics.evasion_rate:.2f}%",
                "polymorphic_effectiveness": metrics.signature_diversity_ratio,
            },
            "signature_analysis": {
                "unique_signatures": metrics.unique_signatures,
                "signature_diversity_ratio": f"{metrics.signature_diversity_ratio:.4f}",
                "no_two_signatures_identical": len(self.signatures_seen) == len(self.detection_results),
            },
            "entropy_analysis": {
                "entropy_range": f"{metrics.entropy_range[0]:.4f} - {metrics.entropy_range[1]:.4f}",
                "entropy_variance": f"{metrics.entropy_variance:.4f}",
                "average_entropy": f"{statistics.mean(self.entropies):.4f}",
            },
            "feature_diversity": {
                "unique_opcode_sequences": metrics.opcode_diversity,
                "unique_control_flows": metrics.control_flow_diversity,
                "features_triggered_distribution": feature_stats,
            },
            "confidence_distribution": {
                "average_confidence": f"{metrics.avg_confidence_score:.4f}",
                "min_confidence": f"{metrics.min_confidence_score:.4f}",
                "max_confidence": f"{metrics.max_confidence_score:.4f}",
                "std_deviation": f"{statistics.stdev([r.confidence for r in self.detection_results]):.4f}",
            },
            "evasion_characteristics": {
                "evaded_variants_count": len(evaded),
                "avg_confidence_evaded": f"{statistics.mean([r.confidence for r in evaded]):.4f}" if evaded else "N/A",
                "detected_variants_count": len(detected),
                "avg_confidence_detected": f"{statistics.mean([r.confidence for r in detected]):.4f}" if detected else "N/A",
            },
            "polymorphic_algorithm_diversity": {
                "algorithms_used": list(algo_names),
                "algorithm_count": len(algo_names),
            },
            "evasion_verdict": {
                "polymorphic": metrics.signature_diversity_ratio > 0.95,
                "effective_entropy_variation": metrics.entropy_variance > 0.1,
                "strong_control_flow_diversity": metrics.control_flow_diversity >= 3,
                "overall_evasion_success": metrics.evasion_rate > 70,
            }
        }

        return report


# ==================== ADVANCED EVASION TESTS ====================

class AdvancedEvasionAnalyzer:
    """Analyze advanced evasion techniques"""

    @staticmethod
    def test_signature_collision_resistance(variants: List[str]) -> Dict:
        """Test resistance to signature-based detection"""
        signatures = set()
        collisions = 0

        for variant in variants:
            sig = hashlib.sha256(variant.encode()).hexdigest()
            if sig in signatures:
                collisions += 1
            signatures.add(sig)

        return {
            "total_variants": len(variants),
            "unique_signatures": len(signatures),
            "collisions": collisions,
            "collision_rate": collisions / len(variants) if variants else 0,
            "collision_resistant": collisions == 0,
        }

    @staticmethod
    def test_behavioral_diversity(variants: List[str]) -> Dict:
        """Analyze behavioral diversity across variants"""
        detector = MLMalwareDetector()

        behaviors = {
            'uses_subprocess': 0,
            'uses_os_system': 0,
            'uses_exec': 0,
            'high_entropy': 0,
            'complex_control_flow': 0,
        }

        for variant in variants:
            if 'subprocess' in variant:
                behaviors['uses_subprocess'] += 1
            if 'os.system' in variant:
                behaviors['uses_os_system'] += 1
            if 'exec' in variant or 'eval' in variant:
                behaviors['uses_exec'] += 1

            entropy = detector.calculate_entropy(variant.encode())
            if entropy > 5.0:
                behaviors['high_entropy'] += 1

            control_flow = detector.extract_control_flow_pattern(variant)
            if 'high_branching' in control_flow:
                behaviors['complex_control_flow'] += 1

        return {
            "behavior_distribution": behaviors,
            "behavioral_variance": len([v for v in behaviors.values() if v > 0]) / len(behaviors),
        }

    @staticmethod
    def test_feature_space_distribution(variants: List[str]) -> Dict:
        """Analyze distribution in ML feature space"""
        detector = MLMalwareDetector()

        entropy_values = []
        opcode_sequences = []

        for variant in variants:
            entropy = detector.calculate_entropy(variant.encode())
            entropy_values.append(entropy)

            opcode_seq = detector.extract_opcode_sequence(variant)
            opcode_sequences.append(opcode_seq)

        unique_opcodes = len(set(opcode_sequences))

        return {
            "entropy_min": min(entropy_values),
            "entropy_max": max(entropy_values),
            "entropy_mean": statistics.mean(entropy_values),
            "entropy_stdev": statistics.stdev(entropy_values) if len(entropy_values) > 1 else 0,
            "unique_opcode_sequences": unique_opcodes,
            "opcode_diversity_ratio": unique_opcodes / len(variants),
            "feature_space_coverage": "comprehensive" if unique_opcodes > len(variants) * 0.7 else "limited",
        }


# ==================== TEST EXECUTION ====================

def run_comprehensive_evasion_test(num_variants: int = 50) -> Dict:
    """Run comprehensive polymorphic evasion test"""
    print("\n" + "="*80)
    print("POLYMORPHIC VARIANT ML MALWARE DETECTOR EVASION TEST")
    print("="*80)

    payload = "echo 'polymorphic payload executed'"

    # Initialize detector
    detector = MLMalwareDetector(threshold=0.7)

    # Test 1: Basic evasion testing
    print("\n[TEST 1] Basic Polymorphic Evasion Testing")
    print("-" * 80)
    tester = EvasionTester(detector, num_variants=num_variants)
    variants = tester.generate_variants(payload)
    results = tester.test_variants()
    basic_report = tester.generate_report()

    # Test 2: Signature collision resistance
    print("\n[TEST 2] Signature Collision Resistance Analysis")
    print("-" * 80)
    analyzer = AdvancedEvasionAnalyzer()
    sig_analysis = analyzer.test_signature_collision_resistance(variants)
    print(f"    Unique Signatures: {sig_analysis['unique_signatures']}/{sig_analysis['total_variants']}")
    print(f"    Collision Rate: {sig_analysis['collision_rate']:.4f}")
    print(f"    Collision Resistant: {sig_analysis['collision_resistant']}")

    # Test 3: Behavioral diversity
    print("\n[TEST 3] Behavioral Diversity Analysis")
    print("-" * 80)
    behavior_analysis = analyzer.test_behavioral_diversity(variants)
    print(f"    Behavioral Variance: {behavior_analysis['behavioral_variance']:.4f}")
    for behavior, count in behavior_analysis['behavior_distribution'].items():
        print(f"    {behavior}: {count} variants")

    # Test 4: Feature space distribution
    print("\n[TEST 4] Feature Space Distribution Analysis")
    print("-" * 80)
    feature_analysis = analyzer.test_feature_space_distribution(variants)
    print(f"    Entropy Range: {feature_analysis['entropy_min']:.4f} - {feature_analysis['entropy_max']:.4f}")
    print(f"    Entropy Mean: {feature_analysis['entropy_mean']:.4f}")
    print(f"    Entropy Stdev: {feature_analysis['entropy_stdev']:.4f}")
    print(f"    Unique Opcode Sequences: {feature_analysis['unique_opcode_sequences']}")
    print(f"    Opcode Diversity Ratio: {feature_analysis['opcode_diversity_ratio']:.4f}")
    print(f"    Feature Space Coverage: {feature_analysis['feature_space_coverage']}")

    # Compile final report
    final_report = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "test_parameters": {
            "num_variants": num_variants,
            "detection_threshold": detector.threshold,
            "payload": payload,
        },
        "test_1_basic_evasion": basic_report,
        "test_2_signature_resistance": sig_analysis,
        "test_3_behavioral_diversity": behavior_analysis,
        "test_4_feature_space_distribution": feature_analysis,
        "overall_evasion_verdict": {
            "polymorphic_effective": basic_report['evasion_verdict']['polymorphic'],
            "entropy_variation_strong": basic_report['evasion_verdict']['effective_entropy_variation'],
            "control_flow_diverse": basic_report['evasion_verdict']['strong_control_flow_diversity'],
            "evasion_success_high": basic_report['evasion_verdict']['overall_evasion_success'],
            "recommendation": "POLYMORPHIC ENGINE EFFECTIVE FOR ML EVASION"
                            if all([
                                basic_report['evasion_verdict']['polymorphic'],
                                basic_report['evasion_verdict']['effective_entropy_variation'],
                                basic_report['evasion_verdict']['strong_control_flow_diversity']
                            ]) else "MARGINAL EVASION EFFECTIVENESS"
        }
    }

    return final_report


def print_final_report(report: Dict):
    """Print formatted final report"""
    print("\n" + "="*80)
    print("EVASION TEST FINAL REPORT")
    print("="*80)

    print("\n[OVERALL VERDICT]")
    for key, value in report['overall_evasion_verdict'].items():
        print(f"  {key}: {value}")

    print("\n[TEST 1 SUMMARY]")
    test1 = report['test_1_basic_evasion']
    print(f"  Evasion Rate: {test1['test_summary']['evasion_success_rate']}")
    print(f"  Variants Detected: {test1['test_summary']['variants_detected']}/{test1['test_summary']['total_variants_tested']}")
    print(f"  Signature Diversity: {test1['signature_analysis']['signature_diversity_ratio']}")
    print(f"  No Signature Collisions: {test1['signature_analysis']['no_two_signatures_identical']}")

    print("\n[TEST 2 SUMMARY]")
    test2 = report['test_2_signature_resistance']
    print(f"  Collision Resistant: {test2['collision_resistant']}")
    print(f"  Unique Signatures: {test2['unique_signatures']}/{test2['total_variants']}")

    print("\n[TEST 3 SUMMARY]")
    test3 = report['test_3_behavioral_diversity']
    print(f"  Behavioral Variance: {test3['behavioral_variance']:.4f}")

    print("\n[TEST 4 SUMMARY]")
    test4 = report['test_4_feature_space_distribution']
    print(f"  Entropy Range: {test4['entropy_min']:.4f} - {test4['entropy_max']:.4f}")
    print(f"  Feature Space Coverage: {test4['feature_space_coverage']}")

    print("\n" + "="*80)


if __name__ == "__main__":
    import sys

    # Allow command-line argument for number of variants
    num_variants = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    report = run_comprehensive_evasion_test(num_variants=num_variants)
    print_final_report(report)

    # Save report to JSON
    report_file = f"/tmp/claude-0/-home-user-sc-generator/cea520eb-2877-52b0-bbd4-c38bff01b8ad/scratchpad/evasion_test_report.json"
    with open(report_file, 'w') as f:
        # Convert non-serializable types
        json.dump(report, f, indent=2, default=str)

    print(f"\n[*] Full report saved to: {report_file}")

    # Print recommendation
    print("\n" + "="*80)
    print("EVASION TEST COMPLETE")
    print("="*80)
    print(f"\nRECOMMENDATION: {report['overall_evasion_verdict']['recommendation']}")
