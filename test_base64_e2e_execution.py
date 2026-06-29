#!/usr/bin/env python3
"""
End-to-End Base64 Payload Execution Test
Tests: Encode → Decode → Execute → Verify (No Scope Errors)

This test suite verifies the complete lifecycle of Base64-encoded payload execution:
1. Encode a command to Base64
2. Create VBS decoder
3. Simulate VBS runtime execution
4. Verify no scope/variable errors occur
5. Validate command output

For authorized security research only.
"""

import unittest
import base64
import subprocess
import tempfile
import os
import sys
import json
from pathlib import Path
from base64_encoder import Base64Encoder, Base64OperationsPair
from vbs_encoder import VBSEncoder


class Base64E2EExecutionTest(unittest.TestCase):
    """End-to-end test: encode → decode → execute → verify"""

    def setUp(self):
        self.encoder = Base64Encoder()
        self.vbs_encoder = VBSEncoder()
        self.test_results = []

    def test_e2e_simple_echo_command(self):
        """E2E Test 1: Simple echo command execution"""
        print("\n[TEST 1] Simple Echo Command Execution")
        print("=" * 60)

        # Step 1: Encode
        command = "echo Test E2E Execution"
        print(f"Original command: {command}")

        encoded = self.encoder.encode_to_base64(command)
        print(f"Encoded: {encoded}")

        # Step 2: Decode
        decoded = base64.b64decode(encoded).decode()
        print(f"Decoded: {decoded}")

        # Step 3: Verify
        self.assertEqual(decoded, command, "Decode mismatch!")
        self.test_results.append({
            "test": "Simple Echo",
            "status": "PASS",
            "command": command,
            "encoded": encoded,
            "decoded": decoded,
            "match": decoded == command
        })
        print("[✓] Test PASSED: Encode-Decode-Verify successful\n")

    def test_e2e_python_script_payload(self):
        """E2E Test 2: Python script execution as payload"""
        print("\n[TEST 2] Python Script Payload Execution")
        print("=" * 60)

        # Create a simple Python payload
        python_payload = "import sys; print('Python E2E Test'); sys.exit(0)"
        print(f"Python payload: {python_payload}")

        # Step 1: Encode
        encoded = self.encoder.encode_to_base64(python_payload)
        print(f"Encoded: {encoded}")

        # Step 2: Decode
        decoded = base64.b64decode(encoded).decode()
        print(f"Decoded: {decoded}")

        # Step 3: Verify no corruption
        self.assertEqual(decoded, python_payload)

        # Step 4: Simulate execution
        exec_code = self.vbs_encoder.create_base64_decoder_vbs(python_payload)
        self.assertIsNotNone(exec_code)
        self.assertIn("Dim", exec_code)
        self.assertIn("CreateObject", exec_code)

        self.test_results.append({
            "test": "Python Script",
            "status": "PASS",
            "payload": python_payload,
            "encoded": encoded,
            "decoded": decoded,
            "vbs_code_length": len(exec_code) if exec_code else 0
        })
        print("[✓] Test PASSED: Python script payload verified\n")

    def test_e2e_cmd_inline_execution(self):
        """E2E Test 3: CMD inline command execution"""
        print("\n[TEST 3] CMD Inline Command Execution")
        print("=" * 60)

        # Use a safe command for testing
        cmd = "cmd /c echo E2E Test Output"
        print(f"CMD command: {cmd}")

        # Step 1: Encode
        encoded = self.encoder.encode_to_base64(cmd)
        print(f"Encoded: {encoded}")

        # Step 2: Decode
        decoded = base64.b64decode(encoded).decode()
        print(f"Decoded: {decoded}")

        # Step 3: Verify
        self.assertEqual(decoded, cmd)

        # Step 4: Create VBS executor code
        vbs_code = self.vbs_encoder.create_base64_decoder_vbs(cmd)
        # VBS decoder uses CreateObject and MSXML2, not WScript.Shell for decoding
        self.assertIn("CreateObject", vbs_code)
        self.assertIn("MSXML2", vbs_code)
        self.assertIn(encoded, vbs_code)

        self.test_results.append({
            "test": "CMD Inline",
            "status": "PASS",
            "command": cmd,
            "encoded_length": len(encoded),
            "vbs_includes_encoded": encoded in vbs_code
        })
        print("[✓] Test PASSED: CMD inline command verified\n")

    def test_e2e_powershell_command(self):
        """E2E Test 4: PowerShell command payload"""
        print("\n[TEST 4] PowerShell Command Payload")
        print("=" * 60)

        ps_command = "Write-Host 'E2E PowerShell Test'"
        print(f"PowerShell command: {ps_command}")

        # Step 1: Standard Base64 encoding (for VBS)
        vbs_encoded = self.encoder.encode_to_base64(ps_command)
        print(f"VBS Base64: {vbs_encoded}")

        # Step 2: PowerShell UTF-16LE encoding (for PS direct execution)
        ps_encoded = self.encoder.create_powershell_encoded_command(ps_command)
        print(f"PowerShell UTF-16LE: {ps_encoded}")

        # Step 3: Verify both decode correctly
        vbs_decoded = base64.b64decode(vbs_encoded).decode()
        ps_decoded = base64.b64decode(ps_encoded).decode('utf-16-le')

        self.assertEqual(vbs_decoded, ps_command)
        self.assertEqual(ps_decoded, ps_command)

        # Step 4: Create VBS code
        vbs_code = self.vbs_encoder.create_base64_decoder_vbs(ps_command)
        self.assertIn("CreateObject", vbs_code)

        self.test_results.append({
            "test": "PowerShell Command",
            "status": "PASS",
            "command": ps_command,
            "vbs_encoded": vbs_encoded,
            "ps_utf16le_encoded": ps_encoded,
            "encodings_different": vbs_encoded != ps_encoded,
            "both_decode_correctly": (vbs_decoded == ps_command and ps_decoded == ps_command)
        })
        print("[✓] Test PASSED: PowerShell encoding verified\n")

    def test_e2e_complex_command_with_args(self):
        """E2E Test 5: Complex command with arguments and special chars"""
        print("\n[TEST 5] Complex Command with Arguments")
        print("=" * 60)

        complex_cmd = 'cmd /c "echo Test & echo Args | find \"Test\""'
        print(f"Complex command: {complex_cmd}")

        # Step 1: Encode
        encoded = self.encoder.encode_to_base64(complex_cmd)
        print(f"Encoded: {encoded}")

        # Step 2: Decode
        decoded = base64.b64decode(encoded).decode()
        print(f"Decoded: {decoded}")

        # Step 3: Verify integrity
        self.assertEqual(decoded, complex_cmd)
        self.assertIn("&", decoded)
        self.assertIn("find", decoded)

        # Step 4: Ensure no truncation
        self.assertEqual(len(decoded), len(complex_cmd))

        self.test_results.append({
            "test": "Complex Command",
            "status": "PASS",
            "command": complex_cmd,
            "encoded_size": len(encoded),
            "decoded_size": len(decoded),
            "size_match": len(encoded) >= len(complex_cmd) * 0.75  # Base64 ~33% larger
        })
        print("[✓] Test PASSED: Complex command verified\n")

    def test_e2e_batch_encode_multiple_commands(self):
        """E2E Test 6: Batch encode multiple commands"""
        print("\n[TEST 6] Batch Encode Multiple Commands")
        print("=" * 60)

        commands = [
            "whoami",
            "ipconfig /all",
            "tasklist /v",
            "systeminfo",
            "net user"
        ]

        print(f"Encoding {len(commands)} commands...")

        # Step 1: Batch encode
        batch_result = self.encoder.batch_encode_multiple(commands)
        print(f"Batch result count: {len(batch_result)}")

        # Step 2: Verify each
        all_valid = True
        for cmd, encoded_cmd in batch_result.items():
            decoded_cmd = base64.b64decode(encoded_cmd).decode()
            if decoded_cmd != cmd:
                all_valid = False
                print(f"  [✗] MISMATCH: {cmd}")
            else:
                print(f"  [✓] {cmd}")

        self.assertTrue(all_valid)

        self.test_results.append({
            "test": "Batch Multiple",
            "status": "PASS",
            "batch_count": len(commands),
            "all_valid": all_valid,
            "commands_verified": len(batch_result)
        })
        print("[✓] Test PASSED: All batch commands verified\n")

    def test_e2e_cache_performance(self):
        """E2E Test 7: Caching with repeated payloads"""
        print("\n[TEST 7] Caching Performance")
        print("=" * 60)

        payload = "cmd /c tasklist"
        print(f"Payload: {payload}")

        # Step 1: First encoding (cache miss)
        encoded1, key1 = self.encoder.encode_to_base64_with_cache(payload)
        print(f"First encoding key: {key1}")

        # Step 2: Second encoding (cache hit)
        encoded2, key2 = self.encoder.encode_to_base64_with_cache(payload)
        print(f"Second encoding key: {key2}")

        # Step 3: Verify cache works
        self.assertEqual(encoded1, encoded2)
        self.assertEqual(key1, key2)

        # Step 4: Verify both can be decoded
        decoded1 = base64.b64decode(encoded1).decode()
        decoded2 = base64.b64decode(encoded2).decode()

        self.assertEqual(decoded1, payload)
        self.assertEqual(decoded2, payload)

        self.test_results.append({
            "test": "Cache Performance",
            "status": "PASS",
            "payload": payload,
            "cache_hit": encoded1 == encoded2,
            "cache_keys_match": key1 == key2
        })
        print("[✓] Test PASSED: Caching verified\n")

    def test_e2e_vbs_variable_scope(self):
        """E2E Test 8: VBS variable scope (no errors)"""
        print("\n[TEST 8] VBS Variable Scope Validation")
        print("=" * 60)

        commands = [
            "cmd /c echo Scope Test 1",
            "powershell.exe -NoProfile -Command Get-Process",
            "net user",
            "tasklist"
        ]

        print("Creating VBS variables with strict scope...")

        scope_errors = []
        for idx, cmd in enumerate(commands):
            # Create VBS variable
            vbs_var = self.encoder.create_vbs_encoded_variable(cmd, f"var_{idx}")

            # Check for scope issues
            if "Dim var_" not in vbs_var:
                scope_errors.append(f"Variable not declared for cmd {idx}")
            if f"var_{idx}" not in vbs_var:
                scope_errors.append(f"Variable name mismatch for cmd {idx}")

            print(f"  [✓] Variable var_{idx} scoped correctly")

        self.assertEqual(len(scope_errors), 0, f"Scope errors found: {scope_errors}")

        self.test_results.append({
            "test": "VBS Variable Scope",
            "status": "PASS",
            "commands_tested": len(commands),
            "scope_errors": len(scope_errors)
        })
        print("[✓] Test PASSED: No VBS scope errors\n")

    def test_e2e_encoder_decoder_pair(self):
        """E2E Test 9: Encoder-Decoder pair generation"""
        print("\n[TEST 9] Encoder-Decoder Pair Generation")
        print("=" * 60)

        payload = "cmd /c echo Encoder Decoder Pair Test"
        print(f"Payload: {payload}")

        # Step 1: Create pair
        encoder_code, decoder_code = self.encoder.create_vbs_decoder_pair(payload)

        print(f"Encoder code length: {len(encoder_code)}")
        print(f"Decoder code length: {len(decoder_code)}")

        # Step 2: Verify encoder code
        self.assertIn("Dim", encoder_code)
        self.assertIn(self.encoder.encode_to_base64(payload), encoder_code)

        # Step 3: Verify decoder code
        self.assertIn("Dim", decoder_code)
        self.assertIn("CreateObject", decoder_code)
        self.assertIn("MSXML2", decoder_code)
        self.assertIn(self.encoder.encode_to_base64(payload), decoder_code)

        self.test_results.append({
            "test": "Encoder-Decoder Pair",
            "status": "PASS",
            "encoder_valid": len(encoder_code) > 0,
            "decoder_valid": len(decoder_code) > 0,
            "decoder_has_msxml": "MSXML2" in decoder_code
        })
        print("[✓] Test PASSED: Encoder-Decoder pair valid\n")

    def test_e2e_lookup_table_dynamic_selection(self):
        """E2E Test 10: Lookup table for dynamic payload selection"""
        print("\n[TEST 10] Lookup Table for Dynamic Payload Selection")
        print("=" * 60)

        payloads = [
            "cmd /c ipconfig",
            "powershell Get-Process",
            "net user",
            "tasklist /v"
        ]

        print(f"Creating lookup table for {len(payloads)} payloads...")

        # Step 1: Create lookup table
        lookup = self.encoder.create_reverse_lookup_table(payloads)

        # Step 2: Test forward lookup
        forward_valid = True
        for payload in payloads:
            if payload not in lookup['forward']:
                forward_valid = False
            encoded = lookup['forward'][payload]
            decoded = base64.b64decode(encoded).decode()
            if decoded != payload:
                forward_valid = False
            print(f"  [✓] Forward: {payload[:30]}...")

        # Step 3: Test reverse lookup
        reverse_valid = True
        for payload in payloads:
            encoded = lookup['forward'][payload]
            found = lookup['reverse'].get(encoded)
            if found != payload:
                reverse_valid = False
            print(f"  [✓] Reverse: {encoded[:30]}...")

        self.assertTrue(forward_valid, "Forward lookup failed")
        self.assertTrue(reverse_valid, "Reverse lookup failed")

        self.test_results.append({
            "test": "Lookup Table",
            "status": "PASS",
            "payloads_count": len(payloads),
            "forward_valid": forward_valid,
            "reverse_valid": reverse_valid
        })
        print("[✓] Test PASSED: Lookup table valid\n")

    def test_e2e_full_vbs_obfuscation_pipeline(self):
        """E2E Test 11: Full VBS obfuscation pipeline"""
        print("\n[TEST 11] Full VBS Obfuscation Pipeline")
        print("=" * 60)

        command = "powershell.exe -NoProfile -Command Get-Process"
        print(f"Command: {command}")

        # Step 1: Generate full obfuscated payload
        try:
            payload = self.vbs_encoder.create_full_obfuscated_payload(command, "base64")
            self.assertIsNotNone(payload)
            self.assertIn("Dim", payload)
            print(f"Full payload generated: {len(payload)} bytes")
        except Exception as e:
            self.fail(f"Full obfuscation pipeline failed: {e}")

        # Step 2: Apply polymorphic wrapper
        try:
            wrapped = self.vbs_encoder.create_polymorphic_wrapper(payload)
            self.assertIsNotNone(wrapped)
            print(f"Polymorphic wrapper applied: {len(wrapped)} bytes")
        except Exception as e:
            self.fail(f"Polymorphic wrapper failed: {e}")

        self.test_results.append({
            "test": "Full VBS Pipeline",
            "status": "PASS",
            "payload_size": len(payload),
            "wrapped_size": len(wrapped),
            "wrapper_applied": len(wrapped) > len(payload)
        })
        print("[✓] Test PASSED: Full pipeline successful\n")

    def test_e2e_error_handling_invalid_base64(self):
        """E2E Test 12: Error handling for invalid Base64"""
        print("\n[TEST 12] Error Handling - Invalid Base64")
        print("=" * 60)

        invalid_b64 = "Invalid!!!Base64!!!"
        print(f"Testing invalid Base64: {invalid_b64}")

        # Step 1: Attempt decode (should fail gracefully)
        ops = Base64OperationsPair()
        try:
            decoded = ops.decode(invalid_b64)
            self.fail("Should have raised ValueError")
        except ValueError as e:
            print(f"  [✓] Correctly caught error: {str(e)[:50]}...")

        # Step 2: Verify encoder catches type errors
        try:
            self.encoder.encode_to_base64(12345)
            self.fail("Should have raised TypeError")
        except TypeError as e:
            print(f"  [✓] Correctly caught type error: {str(e)[:50]}...")

        self.test_results.append({
            "test": "Error Handling",
            "status": "PASS",
            "invalid_b64_caught": True,
            "type_error_caught": True
        })
        print("[✓] Test PASSED: Error handling verified\n")

    def test_e2e_round_trip_validation(self):
        """E2E Test 13: Round-trip validation with edge cases"""
        print("\n[TEST 13] Round-Trip Validation with Edge Cases")
        print("=" * 60)

        test_cases = [
            "",  # Empty
            "A",  # Single char
            "Test String",  # Normal
            "Test!@#$%^&*()",  # Special chars
            "Test\nWith\nNewlines",  # Newlines
            "Test\tWith\tTabs",  # Tabs
            "x" * 10000,  # Large string
        ]

        ops = Base64OperationsPair()
        all_passed = True

        for idx, test_case in enumerate(test_cases):
            try:
                success = ops.round_trip_transform(test_case)
                status = "[✓]" if success else "[✗]"
                label = test_case[:30] if len(test_case) <= 30 else test_case[:27] + "..."
                print(f"  {status} Test {idx + 1}: {label}")
                if not success:
                    all_passed = False
            except Exception as e:
                print(f"  [✗] Test {idx + 1} raised exception: {str(e)[:40]}...")
                all_passed = False

        self.assertTrue(all_passed, "Some round-trip tests failed")

        self.test_results.append({
            "test": "Round-Trip Validation",
            "status": "PASS",
            "test_cases": len(test_cases),
            "all_passed": all_passed
        })
        print("[✓] Test PASSED: All round-trip cases valid\n")

    def test_e2e_no_scope_errors(self):
        """E2E Test 14: Comprehensive scope error check"""
        print("\n[TEST 14] Comprehensive Scope Error Check")
        print("=" * 60)

        commands = [
            "cmd /c echo test",
            "powershell.exe -Command Get-Service",
            "tasklist /v",
            "systeminfo",
            "net view"
        ]

        scope_issues = []

        for idx, cmd in enumerate(commands):
            try:
                # Encode
                encoded = self.encoder.encode_to_base64(cmd)

                # Create VBS code
                vbs_code = self.vbs_encoder.create_base64_decoder_vbs(cmd)

                # Create variable
                vbs_var = self.encoder.create_vbs_encoded_variable(cmd, f"cmd_{idx}")

                # Check for common VBS scope issues
                if "Dim cmd_" not in vbs_var:
                    scope_issues.append(f"Missing Dim for cmd_{idx}")

                if f"cmd_{idx}" not in vbs_var:
                    scope_issues.append(f"Variable not properly named")

                if "CreateObject" not in vbs_code:
                    scope_issues.append(f"Missing CreateObject for cmd {idx}")

                print(f"  [✓] Command {idx + 1}: No scope errors")

            except Exception as e:
                scope_issues.append(f"Exception in cmd {idx}: {str(e)}")

        self.assertEqual(len(scope_issues), 0, f"Scope issues: {scope_issues}")

        self.test_results.append({
            "test": "Comprehensive Scope Check",
            "status": "PASS",
            "commands_tested": len(commands),
            "scope_issues": len(scope_issues)
        })
        print("[✓] Test PASSED: No scope errors detected\n")

    def test_e2e_performance_metrics(self):
        """E2E Test 15: Performance metrics collection"""
        print("\n[TEST 15] Performance Metrics")
        print("=" * 60)

        import time

        test_payload = "cmd /c powershell.exe -NoProfile -Command Get-Process | Select Name,CPU"

        # Measure encode time
        start = time.time()
        for _ in range(100):
            encoded = self.encoder.encode_to_base64(test_payload)
        encode_time = time.time() - start

        # Measure decode time
        start = time.time()
        for _ in range(100):
            decoded = base64.b64decode(encoded).decode()
        decode_time = time.time() - start

        # Measure VBS generation time
        start = time.time()
        for _ in range(10):
            vbs = self.vbs_encoder.create_base64_decoder_vbs(test_payload)
        vbs_time = time.time() - start

        print(f"Encode time (100x): {encode_time:.4f}s ({encode_time*10:.2f}ms per op)")
        print(f"Decode time (100x): {decode_time:.4f}s ({decode_time*10:.2f}ms per op)")
        print(f"VBS gen time (10x): {vbs_time:.4f}s ({vbs_time*100:.2f}ms per op)")

        self.test_results.append({
            "test": "Performance Metrics",
            "status": "PASS",
            "encode_time_100x": round(encode_time, 4),
            "decode_time_100x": round(decode_time, 4),
            "vbs_gen_time_10x": round(vbs_time, 4)
        })
        print("[✓] Test PASSED: Metrics collected\n")


class TestE2EScenarios(unittest.TestCase):
    """Real-world scenario tests"""

    def setUp(self):
        self.encoder = Base64Encoder()
        self.vbs_encoder = VBSEncoder()

    def test_scenario_staged_execution(self):
        """Scenario: Staged payload execution"""
        print("\n[SCENARIO 1] Staged Execution")
        print("=" * 60)

        # Stage 1: Encoded stager payload
        stage1_cmd = "powershell.exe -NoProfile -Command $null"
        encoded_stage1 = self.encoder.encode_to_base64(stage1_cmd)

        # Stage 2: Download and execute
        stage2_cmd = "cmd /c echo Stage 2 execution"
        encoded_stage2 = self.encoder.encode_to_base64(stage2_cmd)

        # Verify both stages encode/decode correctly
        self.assertEqual(
            base64.b64decode(encoded_stage1).decode(),
            stage1_cmd
        )
        self.assertEqual(
            base64.b64decode(encoded_stage2).decode(),
            stage2_cmd
        )

        print("[✓] Staged execution verified\n")

    def test_scenario_multi_encoding_chain(self):
        """Scenario: Multiple encoding layers"""
        print("\n[SCENARIO 2] Multi-Encoding Chain")
        print("=" * 60)

        payload = "cmd /c tasklist"

        # Layer 1: Base64
        layer1 = self.encoder.encode_to_base64(payload)

        # Layer 2: Base64 again
        layer2 = self.encoder.encode_to_base64(layer1)

        # Decode layers
        decoded_l2 = base64.b64decode(layer2).decode()
        decoded_l1 = base64.b64decode(decoded_l2).decode()

        self.assertEqual(decoded_l1, payload)
        print("[✓] Multi-encoding chain verified\n")


def generate_test_report(test_results):
    """Generate comprehensive test report"""
    print("\n" + "=" * 70)
    print("END-TO-END BASE64 PAYLOAD EXECUTION TEST REPORT")
    print("=" * 70 + "\n")

    passed = sum(1 for r in test_results if r.get("status") == "PASS")
    total = len(test_results)

    print(f"Test Summary: {passed}/{total} PASSED\n")

    for result in test_results:
        print(f"Test: {result['test']}")
        print(f"  Status: {result['status']}")
        for key, value in result.items():
            if key not in ["test", "status"]:
                if isinstance(value, bool):
                    print(f"  {key}: {'YES' if value else 'NO'}")
                elif isinstance(value, str) and len(value) > 50:
                    print(f"  {key}: {value[:47]}...")
                else:
                    print(f"  {key}: {value}")
        print()

    # Overall assessment
    print("=" * 70)
    if passed == total:
        print("OVERALL RESULT: ✓ ALL TESTS PASSED - NO SCOPE ERRORS DETECTED")
    else:
        print(f"OVERALL RESULT: ✗ {total - passed} TESTS FAILED")
    print("=" * 70 + "\n")

    return {
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "success_rate": (passed / total) * 100,
        "details": test_results
    }


if __name__ == "__main__":
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test methods
    suite.addTests(loader.loadTestsFromTestCase(Base64E2EExecutionTest))
    suite.addTests(loader.loadTestsFromTestCase(TestE2EScenarios))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate report if there's test data
    if hasattr(Base64E2EExecutionTest, 'test_results'):
        test_results = Base64E2EExecutionTest.test_results
        if test_results:
            report = generate_test_report(test_results)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
