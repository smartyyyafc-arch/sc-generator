#!/usr/bin/env python3
"""
Hash Randomization Audit Tool
Verifies that each generated file has unique hash to evade hash-based detection
"""

import hashlib
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import json
from datetime import datetime
import tempfile

# Import project generators
from payload_generator import PayloadGenerator
from polymorphic_engine import PolymorphicCodeGenerator, PolymorphicConfig
from payload_file_writer import PayloadFileWriter, FileFormat


class HashRandomizationAuditor:
    """Audits file hash randomization across generated payloads"""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir()) / "hash_audit"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_cases": [],
            "hash_collisions": [],
            "uniqueness_stats": {},
            "findings": []
        }

        self.hash_cache: Dict[str, List[str]] = defaultdict(list)
        self.generated_files = []

    def calculate_hashes(self, content: bytes, file_id: str = "") -> Dict[str, str]:
        """Calculate multiple hash types for content"""
        return {
            "md5": hashlib.md5(content).hexdigest(),
            "sha1": hashlib.sha1(content).hexdigest(),
            "sha256": hashlib.sha256(content).hexdigest(),
            "sha512": hashlib.sha512(content).hexdigest(),
            "blake2b": hashlib.blake2b(content).hexdigest(),
            "file_id": file_id
        }

    def test_payload_generator_randomization(self, num_samples: int = 100) -> Dict:
        """Test PayloadGenerator for hash randomization"""
        print(f"\n[*] Testing PayloadGenerator with {num_samples} samples...")

        test_case = {
            "name": "PayloadGenerator Randomization",
            "num_samples": num_samples,
            "technique": "base64",
            "command": "calc.exe",
            "results": {}
        }

        generator = PayloadGenerator(enable_caching=False, enable_randomization=True)
        hashes_by_type = defaultdict(list)
        payloads = []

        for i in range(num_samples):
            payload = generator.generate(
                "calc.exe",
                technique="base64",
                obfuscation_level="high"
            )
            payloads.append(payload)

            hashes = self.calculate_hashes(payload.encode(), file_id=f"payload_{i}")
            for hash_type, hash_value in hashes.items():
                if hash_type != "file_id":
                    hashes_by_type[hash_type].append(hash_value)

            # Cache for collision detection
            for hash_type in ["sha256", "md5"]:
                self.hash_cache[f"payload_{hash_type}_{hashes[hash_type]}"].append(f"sample_{i}")

        # Analyze results
        results = {}
        for hash_type, hash_list in hashes_by_type.items():
            unique_count = len(set(hash_list))
            collision_count = num_samples - unique_count
            uniqueness_pct = (unique_count / num_samples) * 100

            results[hash_type] = {
                "total_samples": num_samples,
                "unique_hashes": unique_count,
                "collisions": collision_count,
                "uniqueness_percentage": uniqueness_pct,
                "sample_hashes": hash_list[:5]  # First 5 samples
            }

            print(f"  {hash_type:12} - Unique: {unique_count}/{num_samples} ({uniqueness_pct:.1f}%) - Collisions: {collision_count}")

            if collision_count > 0:
                self.results["findings"].append(
                    f"COLLISION RISK: {hash_type} has {collision_count} collision(s) in PayloadGenerator"
                )

        test_case["results"] = results
        test_case["payload_lengths"] = [len(p) for p in payloads[:10]]

        return test_case

    def test_polymorphic_engine_randomization(self, num_samples: int = 100) -> Dict:
        """Test PolymorphicCodeGenerator for hash randomization"""
        print(f"\n[*] Testing PolymorphicCodeGenerator with {num_samples} samples...")

        test_case = {
            "name": "PolymorphicCodeGenerator Randomization",
            "num_samples": num_samples,
            "results": {}
        }

        hashes_by_type = defaultdict(list)
        generated_codes = []

        for i in range(num_samples):
            # Generate with different seed each time
            config = PolymorphicConfig(seed=None)  # No fixed seed = randomization
            generator = PolymorphicCodeGenerator(config=config)

            # Generate random algorithm combination
            algorithms = generator.select_random_algorithms()
            control_flows = generator.select_random_control_flows()
            obfuscations = generator.select_random_obfuscations()

            # Create code signature from choices
            code_signature = f"alg:{len(algorithms)}_cf:{len(control_flows)}_obf:{len(obfuscations)}"
            generated_codes.append(code_signature)

            hashes = self.calculate_hashes(code_signature.encode(), file_id=f"poly_{i}")
            for hash_type, hash_value in hashes.items():
                if hash_type != "file_id":
                    hashes_by_type[hash_type].append(hash_value)

        # Analyze results
        results = {}
        for hash_type, hash_list in hashes_by_type.items():
            unique_count = len(set(hash_list))
            collision_count = num_samples - unique_count
            uniqueness_pct = (unique_count / num_samples) * 100

            results[hash_type] = {
                "total_samples": num_samples,
                "unique_hashes": unique_count,
                "collisions": collision_count,
                "uniqueness_percentage": uniqueness_pct,
                "sample_hashes": hash_list[:5]
            }

            print(f"  {hash_type:12} - Unique: {unique_count}/{num_samples} ({uniqueness_pct:.1f}%) - Collisions: {collision_count}")

            if collision_count > 0:
                self.results["findings"].append(
                    f"COLLISION RISK: {hash_type} has {collision_count} collision(s) in PolymorphicCodeGenerator"
                )

        test_case["results"] = results
        return test_case

    def test_file_writer_randomization(self, num_samples: int = 50) -> Dict:
        """Test PayloadFileWriter for hash randomization"""
        print(f"\n[*] Testing PayloadFileWriter with {num_samples} samples...")

        test_case = {
            "name": "PayloadFileWriter Randomization",
            "num_samples": num_samples,
            "results": {}
        }

        generator = PayloadGenerator(enable_caching=False, enable_randomization=True)
        writer = PayloadFileWriter(enable_obfuscation=True)

        hashes_by_type = defaultdict(list)
        file_paths = []

        for i in range(num_samples):
            payload = generator.generate("calc.exe", technique="base64", obfuscation_level="high")

            try:
                file_path, metadata = writer.write_payload(
                    payload,
                    file_format=FileFormat.VBS,
                    obfuscation_level="high",
                    encoding_type="base64"
                )

                file_paths.append(file_path)

                # Read file and calculate hashes
                with open(file_path, 'rb') as f:
                    file_content = f.read()

                hashes = self.calculate_hashes(file_content, file_id=f"file_{i}")
                for hash_type, hash_value in hashes.items():
                    if hash_type != "file_id":
                        hashes_by_type[hash_type].append(hash_value)

                # Verify metadata hash
                if metadata.sha256_hash:
                    if metadata.sha256_hash != hashlib.sha256(payload.encode()).hexdigest():
                        self.results["findings"].append(
                            f"HASH MISMATCH: File {i} metadata hash doesn't match payload"
                        )

            except Exception as e:
                self.results["findings"].append(f"ERROR writing file {i}: {str(e)}")

        # Analyze results
        results = {}
        for hash_type, hash_list in hashes_by_type.items():
            unique_count = len(set(hash_list))
            collision_count = num_samples - unique_count
            uniqueness_pct = (unique_count / num_samples) * 100 if num_samples > 0 else 0

            results[hash_type] = {
                "total_samples": len(file_paths),
                "unique_hashes": unique_count,
                "collisions": collision_count,
                "uniqueness_percentage": uniqueness_pct,
                "sample_hashes": hash_list[:3] if hash_list else []
            }

            print(f"  {hash_type:12} - Unique: {unique_count}/{len(file_paths)} ({uniqueness_pct:.1f}%) - Collisions: {collision_count}")

            if collision_count > 0:
                self.results["findings"].append(
                    f"COLLISION RISK: {hash_type} has {collision_count} collision(s) in written files"
                )

        test_case["results"] = results
        self.generated_files.extend(file_paths)

        return test_case

    def test_multi_technique_randomization(self, num_samples: int = 30) -> Dict:
        """Test randomization across different encoding techniques"""
        print(f"\n[*] Testing multi-technique randomization with {num_samples} samples...")

        test_case = {
            "name": "Multi-Technique Randomization",
            "num_samples": num_samples,
            "techniques": ["base64", "hex", "array"],
            "results": {}
        }

        generator = PayloadGenerator(enable_caching=False, enable_randomization=True)
        hashes_by_technique = defaultdict(lambda: defaultdict(list))

        for technique in test_case["techniques"]:
            for i in range(num_samples):
                payload = generator.generate("calc.exe", technique=technique, obfuscation_level="high")
                hashes = self.calculate_hashes(payload.encode(), file_id=f"{technique}_{i}")

                for hash_type in ["sha256", "md5"]:
                    hashes_by_technique[technique][hash_type].append(hashes[hash_type])

        # Analyze results per technique
        for technique, hash_data in hashes_by_technique.items():
            tech_results = {}
            for hash_type, hash_list in hash_data.items():
                unique_count = len(set(hash_list))
                collision_count = num_samples - unique_count
                uniqueness_pct = (unique_count / num_samples) * 100

                tech_results[hash_type] = {
                    "unique_hashes": unique_count,
                    "collisions": collision_count,
                    "uniqueness_percentage": uniqueness_pct
                }

                print(f"  {technique:12} {hash_type:12} - Unique: {unique_count}/{num_samples} ({uniqueness_pct:.1f}%)")

            test_case["results"][technique] = tech_results

        return test_case

    def test_cross_file_collision_detection(self, num_samples: int = 200) -> Dict:
        """Detect if any generated files have identical hashes"""
        print(f"\n[*] Performing cross-file collision detection with {num_samples} samples...")

        test_case = {
            "name": "Cross-File Collision Detection",
            "num_samples": num_samples,
            "results": {}
        }

        generator = PayloadGenerator(enable_caching=False, enable_randomization=True)
        sha256_hashes = {}
        md5_hashes = {}

        for i in range(num_samples):
            payload = generator.generate("powershell.exe -Command 'Get-Process'",
                                        technique="base64",
                                        obfuscation_level="high")

            sha256 = hashlib.sha256(payload.encode()).hexdigest()
            md5 = hashlib.md5(payload.encode()).hexdigest()

            if sha256 in sha256_hashes:
                collision_info = {
                    "type": "SHA256",
                    "hash": sha256,
                    "collisions": [sha256_hashes[sha256], i]
                }
                self.results["hash_collisions"].append(collision_info)
                self.results["findings"].append(
                    f"SHA256 COLLISION DETECTED: Samples {sha256_hashes[sha256]} and {i} have identical hash"
                )
            else:
                sha256_hashes[sha256] = i

            if md5 in md5_hashes:
                collision_info = {
                    "type": "MD5",
                    "hash": md5,
                    "collisions": [md5_hashes[md5], i]
                }
                self.results["hash_collisions"].append(collision_info)
                self.results["findings"].append(
                    f"MD5 COLLISION DETECTED: Samples {md5_hashes[md5]} and {i} have identical hash"
                )
            else:
                md5_hashes[md5] = i

        unique_sha256 = len(sha256_hashes)
        unique_md5 = len(md5_hashes)

        test_case["results"] = {
            "sha256": {
                "total_samples": num_samples,
                "unique_hashes": unique_sha256,
                "collision_count": num_samples - unique_sha256,
                "collision_free": (num_samples - unique_sha256) == 0
            },
            "md5": {
                "total_samples": num_samples,
                "unique_hashes": unique_md5,
                "collision_count": num_samples - unique_md5,
                "collision_free": (num_samples - unique_md5) == 0
            }
        }

        print(f"  SHA256: {unique_sha256} unique hashes, {num_samples - unique_sha256} collisions")
        print(f"  MD5:    {unique_md5} unique hashes, {num_samples - unique_md5} collisions")

        return test_case

    def run_all_audits(self) -> None:
        """Run all randomization audit tests"""
        print("=" * 70)
        print("FILE HASH RANDOMIZATION AUDIT REPORT")
        print("=" * 70)

        self.results["test_cases"].append(self.test_payload_generator_randomization(num_samples=100))
        self.results["test_cases"].append(self.test_polymorphic_engine_randomization(num_samples=100))
        self.results["test_cases"].append(self.test_file_writer_randomization(num_samples=50))
        self.results["test_cases"].append(self.test_multi_technique_randomization(num_samples=30))
        self.results["test_cases"].append(self.test_cross_file_collision_detection(num_samples=200))

        # Calculate overall statistics
        self._calculate_overall_stats()
        self._generate_security_assessment()

        # Save results
        self._save_results()

    def _calculate_overall_stats(self) -> None:
        """Calculate overall uniqueness statistics"""
        print("\n[*] Calculating overall statistics...")

        all_uniqueness_rates = []
        total_collisions = 0

        for test_case in self.results["test_cases"]:
            if "results" in test_case:
                if isinstance(test_case["results"], dict):
                    for key, value in test_case["results"].items():
                        if isinstance(value, dict) and "uniqueness_percentage" in value:
                            all_uniqueness_rates.append(value["uniqueness_percentage"])
                            if "collisions" in value:
                                total_collisions += value["collisions"]

        if all_uniqueness_rates:
            avg_uniqueness = sum(all_uniqueness_rates) / len(all_uniqueness_rates)
            min_uniqueness = min(all_uniqueness_rates)
            max_uniqueness = max(all_uniqueness_rates)

            self.results["uniqueness_stats"] = {
                "average_uniqueness_percentage": avg_uniqueness,
                "min_uniqueness_percentage": min_uniqueness,
                "max_uniqueness_percentage": max_uniqueness,
                "total_collisions_detected": total_collisions
            }

            print(f"  Average Uniqueness: {avg_uniqueness:.2f}%")
            print(f"  Min Uniqueness:     {min_uniqueness:.2f}%")
            print(f"  Max Uniqueness:     {max_uniqueness:.2f}%")
            print(f"  Total Collisions:   {total_collisions}")

    def _generate_security_assessment(self) -> None:
        """Generate security assessment based on results"""
        print("\n[*] Generating security assessment...")

        findings_count = len(self.results["findings"])
        collision_count = len(self.results["hash_collisions"])

        if findings_count == 0 and collision_count == 0:
            assessment = "EXCELLENT: No hash collisions detected. Strong randomization confirmed."
            severity = "PASS"
        elif collision_count <= 2 and findings_count <= 1:
            assessment = "GOOD: Minimal collision risk. Randomization is effective for most use cases."
            severity = "PASS"
        elif collision_count <= 5:
            assessment = "WARNING: Some collisions detected. Randomization may be insufficient for high-volume operations."
            severity = "WARNING"
        else:
            assessment = "CRITICAL: Multiple collisions detected. Randomization mechanism is inadequate."
            severity = "FAIL"

        self.results["security_assessment"] = {
            "status": severity,
            "assessment": assessment,
            "recommendations": self._generate_recommendations(severity)
        }

        print(f"  Status: {severity}")
        print(f"  Assessment: {assessment}")

    def _generate_recommendations(self, severity: str) -> List[str]:
        """Generate recommendations based on severity"""
        recommendations = []

        if severity == "PASS":
            recommendations.append("Current randomization implementation is effective.")
            recommendations.append("No immediate action required.")
        elif severity == "WARNING":
            recommendations.append("Review entropy sources in randomization functions.")
            recommendations.append("Consider adding entropy pooling for high-volume generation.")
            recommendations.append("Implement seed diversification across sessions.")
        else:  # FAIL
            recommendations.append("CRITICAL: Redesign randomization mechanism.")
            recommendations.append("Implement cryptographic PRNG (secrets module).")
            recommendations.append("Add per-file entropy injection.")
            recommendations.append("Verify random.seed() is not called with predictable values.")
            recommendations.append("Test against hash-based detection systems.")

        return recommendations

    def _save_results(self) -> None:
        """Save audit results to files"""
        # JSON report
        json_path = self.output_dir / "hash_randomization_audit.json"
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n[+] JSON report saved: {json_path}")

        # Text report
        text_path = self.output_dir / "hash_randomization_audit.txt"
        with open(text_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("FILE HASH RANDOMIZATION AUDIT REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Generated: {self.results['timestamp']}\n\n")

            # Security Assessment
            if "security_assessment" in self.results:
                assessment = self.results["security_assessment"]
                f.write("SECURITY ASSESSMENT\n")
                f.write("-" * 80 + "\n")
                f.write(f"Status: {assessment['status']}\n")
                f.write(f"Assessment: {assessment['assessment']}\n\n")
                f.write("Recommendations:\n")
                for rec in assessment['recommendations']:
                    f.write(f"  • {rec}\n")
                f.write("\n")

            # Overall Statistics
            if self.results["uniqueness_stats"]:
                stats = self.results["uniqueness_stats"]
                f.write("OVERALL STATISTICS\n")
                f.write("-" * 80 + "\n")
                f.write(f"Average Uniqueness: {stats.get('average_uniqueness_percentage', 0):.2f}%\n")
                f.write(f"Min Uniqueness:     {stats.get('min_uniqueness_percentage', 0):.2f}%\n")
                f.write(f"Max Uniqueness:     {stats.get('max_uniqueness_percentage', 0):.2f}%\n")
                f.write(f"Total Collisions:   {stats.get('total_collisions_detected', 0)}\n\n")

            # Test Case Results
            f.write("TEST CASE RESULTS\n")
            f.write("-" * 80 + "\n")
            for test_case in self.results["test_cases"]:
                f.write(f"\n{test_case['name']}\n")
                f.write(f"  Samples: {test_case.get('num_samples', 'N/A')}\n")

                if isinstance(test_case.get("results"), dict):
                    for key, value in test_case["results"].items():
                        if isinstance(value, dict):
                            if "uniqueness_percentage" in value:
                                f.write(f"  {key}: {value.get('uniqueness_percentage', 0):.1f}% unique, ")
                                f.write(f"{value.get('collisions', 0)} collision(s)\n")
                            elif "collision_free" in value:
                                status = "✓ PASS" if value["collision_free"] else "✗ FAIL"
                                f.write(f"  {key}: {status} - ")
                                f.write(f"{value.get('unique_hashes', 0)} unique, ")
                                f.write(f"{value.get('collision_count', 0)} collision(s)\n")

            # Findings
            if self.results["findings"]:
                f.write("\nFINDINGS\n")
                f.write("-" * 80 + "\n")
                for finding in self.results["findings"]:
                    f.write(f"• {finding}\n")

            if self.results["hash_collisions"]:
                f.write("\nHASH COLLISIONS DETECTED\n")
                f.write("-" * 80 + "\n")
                for collision in self.results["hash_collisions"]:
                    f.write(f"• {collision['type']}: {collision['hash'][:16]}...\n")
                    f.write(f"  Involved samples: {collision['collisions']}\n")

        print(f"[+] Text report saved: {text_path}")

        return json_path, text_path


def main():
    auditor = HashRandomizationAuditor()
    auditor.run_all_audits()

    # Print summary
    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print("=" * 70)

    if auditor.results["security_assessment"]["status"] == "PASS":
        print(f"✓ {auditor.results['security_assessment']['assessment']}")
    else:
        print(f"✗ {auditor.results['security_assessment']['assessment']}")

    print(f"\nReports generated in: {auditor.output_dir}")


if __name__ == "__main__":
    main()
