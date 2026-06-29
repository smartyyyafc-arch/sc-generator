#!/usr/bin/env python3
"""
VBS Payload Verification Script
Verifies all VBS payload generators produce valid syntax with no undefined functions
"""

import sys
from vbs_syntax_validator import VBSSyntaxValidator, validate_vbs_payload
from vbs_encoder import VBSEncoder, generate_clean_vbs_payload
from vbs_advanced_obfuscation import AdvancedVBSObfuscation, create_stealthy_payload
from payload_generator import PayloadGenerator


class PayloadVerificationReport:
    """Generate comprehensive verification report for all VBS payloads"""

    def __init__(self):
        self.validator = VBSSyntaxValidator()
        self.generator = PayloadGenerator()
        self.encoder = VBSEncoder()
        self.obf = AdvancedVBSObfuscation()
        self.test_command = "cmd /c echo test"
        self.results = {
            "passed": [],
            "failed": [],
            "total": 0
        }

    def test_payload(self, name: str, payload: str) -> bool:
        """Test a single payload"""
        self.results["total"] += 1
        is_valid, errors = self.validator.validate(payload)

        if is_valid:
            self.results["passed"].append(name)
            print(f"✓ PASS: {name}")
            return True
        else:
            self.results["failed"].append({
                "name": name,
                "errors": errors,
                "error_count": len(errors)
            })
            print(f"✗ FAIL: {name}")
            for error in errors:
                print(f"    Line {error.line_number} [{error.error_type}]: {error.message}")
            return False

    def verify_all_techniques(self):
        """Verify all payload generation techniques"""
        print("\n" + "="*70)
        print("VBS PAYLOAD GENERATOR VERIFICATION REPORT")
        print("="*70)

        print("\n[1] Testing Basic VBS Encoder Functions")
        print("-" * 70)
        self.test_payload(
            "Base64 Decoder VBS",
            self.encoder.create_base64_decoder_vbs("test payload")
        )
        self.test_payload(
            "Hex Decoder VBS",
            self.encoder.create_hex_decoder_vbs("test payload")[0]
        )
        self.test_payload(
            "Array Concatenation Decoder",
            self.encoder.create_array_concatenation_decoder("test payload")[0]
        )
        self.test_payload(
            "WScript Hidden Execution",
            self.encoder.create_wscript_hidden_execution("cmd /c test")
        )
        self.test_payload(
            "Polymorphic Wrapper",
            self.encoder.create_polymorphic_wrapper("Dim x\nx = 1")
        )
        self.test_payload(
            "Runtime Decoded Base64",
            self.encoder.create_runtime_decoded_payload("cmd /c test", "base64")
        )
        self.test_payload(
            "Runtime Decoded Hex",
            self.encoder.create_runtime_decoded_payload("cmd /c test", "hex")
        )

        print("\n[2] Testing Full Obfuscated Payloads")
        print("-" * 70)
        self.test_payload(
            "Full Obfuscated Base64",
            self.encoder.create_full_obfuscated_payload("cmd /c test", "base64")
        )
        self.test_payload(
            "Full Obfuscated Hex",
            self.encoder.create_full_obfuscated_payload("cmd /c test", "hex")
        )
        self.test_payload(
            "Full Obfuscated Array",
            self.encoder.create_full_obfuscated_payload("cmd /c test", "array")
        )

        print("\n[3] Testing Clean VBS Payload Generation")
        print("-" * 70)
        self.test_payload(
            "Clean Payload - Low Obfuscation",
            generate_clean_vbs_payload("cmd /c test", "low")
        )
        self.test_payload(
            "Clean Payload - Medium Obfuscation",
            generate_clean_vbs_payload("cmd /c test", "medium")
        )
        self.test_payload(
            "Clean Payload - High Obfuscation",
            generate_clean_vbs_payload("cmd /c test", "high")
        )

        print("\n[4] Testing Advanced Obfuscation Techniques")
        print("-" * 70)
        self.test_payload(
            "Environment Variable Decoder",
            self.obf.create_environment_variable_decoder("test payload")
        )
        self.test_payload(
            "WMI Execution Wrapper",
            self.obf.create_wmi_execution_wrapper("cmd /c test")
        )
        self.test_payload(
            "Registry Stored Payload",
            self.obf.create_registry_stored_payload("cmd /c test")
        )
        self.test_payload(
            "Scheduled Task Injection",
            self.obf.create_scheduled_task_injection("cmd /c test")
        )
        self.test_payload(
            "COM Object Obfuscation",
            self.obf.create_com_object_obfuscation("cmd /c test")
        )
        self.test_payload(
            "Obfuscated Function Calls",
            self.obf.create_obfuscated_function_calls("cmd /c test")
        )
        self.test_payload(
            "File Writer Injection",
            self.obf.create_filewriter_injection("cmd /c test")
        )
        self.test_payload(
            "Multi-Encoding Chain",
            self.obf.create_multi_encoding_chain("test payload")
        )

        print("\n[5] Testing Stealthy Payload Creation")
        print("-" * 70)
        techniques = ["wmi", "registry", "env", "com", "multi", "obfuscated_calls", "filewriter"]
        for technique in techniques:
            self.test_payload(
                f"Stealthy Payload - {technique.upper()}",
                create_stealthy_payload("cmd /c test", technique)
            )

        print("\n[6] Testing Unified Payload Generator Techniques")
        print("-" * 70)
        for technique in self.generator.list_techniques():
            try:
                payload = self.generator.generate(self.test_command, technique=technique)
                self.test_payload(
                    f"PayloadGenerator - {technique.upper()}",
                    payload
                )
            except Exception as e:
                self.results["failed"].append({
                    "name": f"PayloadGenerator - {technique.upper()}",
                    "errors": [str(e)],
                    "error_count": 1
                })
                print(f"✗ FAIL: PayloadGenerator - {technique.upper()}")
                print(f"    Exception: {str(e)[:100]}")

        print("\n[7] Testing All Obfuscation Levels")
        print("-" * 70)
        for level in ["low", "medium", "high"]:
            for technique in ["base64", "hex"]:
                try:
                    payload = self.generator.generate(
                        self.test_command,
                        technique=technique,
                        obfuscation_level=level
                    )
                    self.test_payload(
                        f"Generator - {technique} ({level} obfuscation)",
                        payload
                    )
                except Exception as e:
                    self.results["failed"].append({
                        "name": f"Generator - {technique} ({level} obfuscation)",
                        "errors": [str(e)],
                        "error_count": 1
                    })

    def print_summary(self):
        """Print summary of verification results"""
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.results['total']}")
        print(f"Passed: {len(self.results['passed'])} ({100*len(self.results['passed'])//self.results['total']}%)")
        print(f"Failed: {len(self.results['failed'])} ({100*len(self.results['failed'])//self.results['total']}%)")

        if self.results["failed"]:
            print("\n" + "="*70)
            print("FAILED TESTS DETAILS")
            print("="*70)
            for failed_test in self.results["failed"]:
                print(f"\n{failed_test['name']}")
                print(f"  Error Count: {failed_test['error_count']}")
                if isinstance(failed_test['errors'], list) and len(failed_test['errors']) > 0:
                    first_error = failed_test['errors'][0]
                    if hasattr(first_error, 'message'):
                        print(f"  First Error: {first_error.message}")
                    else:
                        print(f"  First Error: {str(first_error)[:200]}")

        print("\n" + "="*70)
        if self.results["failed"]:
            print("RESULT: FAILED - Some payloads have syntax errors")
            return False
        else:
            print("RESULT: SUCCESS - All payloads have valid VBS syntax with no undefined functions")
            return True

    def print_detailed_results(self):
        """Print detailed results for debugging"""
        print("\n" + "="*70)
        print("DETAILED VALIDATION RESULTS")
        print("="*70)

        print("\nPassed Tests:")
        for name in sorted(self.results["passed"]):
            print(f"  ✓ {name}")

        if self.results["failed"]:
            print("\nFailed Tests:")
            for failed_test in self.results["failed"]:
                print(f"\n  ✗ {failed_test['name']}")
                if isinstance(failed_test['errors'], list):
                    for error in failed_test['errors'][:3]:  # Show first 3 errors
                        if hasattr(error, 'line_number'):
                            print(f"      Line {error.line_number}: {error.message}")
                        else:
                            print(f"      {str(error)[:100]}")
                    if len(failed_test['errors']) > 3:
                        print(f"      ... and {len(failed_test['errors']) - 3} more errors")


def main():
    """Main entry point"""
    report = PayloadVerificationReport()

    try:
        report.verify_all_techniques()
        report.print_summary()
        report.print_detailed_results()

        # Return appropriate exit code
        if report.results["failed"]:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"\n[!] FATAL ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
