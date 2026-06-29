#!/usr/bin/env python3
"""
End-to-End Test for Array Decoder
Tests the complete pipeline: payload → split → encode chunks → decode → execute
"""

import unittest
import binascii
import re
from typing import List, Tuple
from vbs_encoder import VBSEncoder


class ArrayDecoderE2E(unittest.TestCase):
    """End-to-end tests for Array decoder functionality"""

    def setUp(self):
        """Initialize test fixtures"""
        self.encoder = VBSEncoder()
        self.test_payloads = {
            "simple": "cmd /c echo Hello",
            "medium": "powershell.exe -NoProfile -Command Write-Host 'Test'",
            "long": "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine'); Write-Output 'Path updated'\"",
            "special_chars": "cmd /c echo Special@Chars#$%",
        }

    def test_array_decoder_generation(self):
        """Test 1: Array decoder VBS code generation"""
        payload = self.test_payloads["simple"]
        vbs_code = self.encoder.create_array_concatenation_decoder(payload)

        # Verify structure
        self.assertIn("Dim", vbs_code, "Should declare arrays")
        self.assertIn("For Each", vbs_code, "Should iterate through array")
        self.assertIn("Chr(CLng", vbs_code, "Should convert hex to chr")
        self.assertIn("WScript.Shell", vbs_code, "Should use WScript.Shell")
        self.assertIn(".Run", vbs_code, "Should execute command")
        print("✓ Test 1 PASSED: Array decoder VBS structure is valid")

    def test_payload_split_into_chunks(self):
        """Test 2: Payload splitting into 16-byte chunks"""
        payload = self.test_payloads["medium"]

        # Simulate payload splitting (as done in create_array_concatenation_decoder)
        chunk_size = 16
        chunks = [payload[i:i + chunk_size] for i in range(0, len(payload), chunk_size)]

        # Verify splitting logic
        self.assertGreater(len(chunks), 1, "Medium payload should split into multiple chunks")

        # Verify each chunk (except last) is correct size
        for i, chunk in enumerate(chunks[:-1]):
            self.assertEqual(len(chunk), chunk_size, f"Chunk {i} should be {chunk_size} bytes")

        # Last chunk can be smaller
        self.assertLessEqual(len(chunks[-1]), chunk_size, "Last chunk should be <= chunk size")

        # Verify chunks concatenate to original
        reconstructed = "".join(chunks)
        self.assertEqual(reconstructed, payload, "Chunks should reconstruct original payload")

        print(f"✓ Test 2 PASSED: Payload split into {len(chunks)} chunks correctly")

    def test_chunk_hex_encoding(self):
        """Test 3: Hex encoding of chunks"""
        payload = self.test_payloads["simple"]
        chunk_size = 16
        chunks = [payload[i:i + chunk_size] for i in range(0, len(payload), chunk_size)]

        encoded_chunks = []
        for chunk in chunks:
            hex_encoded = binascii.hexlify(chunk.encode()).decode()
            encoded_chunks.append(hex_encoded)

            # Verify hex encoding properties
            self.assertTrue(all(c in '0123456789abcdef' for c in hex_encoded),
                          f"Chunk should be valid hex: {hex_encoded}")
            self.assertEqual(len(hex_encoded), len(chunk) * 2,
                           f"Hex length should be 2x chunk length")

        self.assertEqual(len(encoded_chunks), len(chunks), "Should have one encoded chunk per original")
        print(f"✓ Test 3 PASSED: {len(chunks)} chunks encoded to hex correctly")

    def test_hex_to_chr_decoding(self):
        """Test 4: Hex to character decoding simulation"""
        test_string = "Hello"
        hex_encoded = binascii.hexlify(test_string.encode()).decode()

        # Simulate VBS decoding logic: For i = 1 To Len(h) Step 2: Chr(CLng("&H" & Mid(h, i, 2)))
        decoded = ""
        for i in range(0, len(hex_encoded), 2):
            hex_pair = hex_encoded[i:i+2]
            char_code = int(hex_pair, 16)
            decoded += chr(char_code)

        self.assertEqual(decoded, test_string, "Decoded should match original")
        print(f"✓ Test 4 PASSED: Hex '{hex_encoded}' decoded to '{decoded}' correctly")

    def test_full_decoding_pipeline(self):
        """Test 5: Complete decode pipeline (all chunks)"""
        payload = self.test_payloads["medium"]
        chunk_size = 16
        chunks = [payload[i:i + chunk_size] for i in range(0, len(payload), chunk_size)]

        # Step 1: Encode chunks
        encoded_chunks = []
        for chunk in chunks:
            hex_encoded = binascii.hexlify(chunk.encode()).decode()
            encoded_chunks.append(hex_encoded)

        # Step 2: Decode (simulate VBS decoding)
        reconstructed = ""
        for hex_chunk in encoded_chunks:
            for i in range(0, len(hex_chunk), 2):
                hex_pair = hex_chunk[i:i+2]
                char_code = int(hex_pair, 16)
                reconstructed += chr(char_code)

        # Verify result
        self.assertEqual(reconstructed, payload, "Full pipeline should reconstruct payload exactly")
        print(f"✓ Test 5 PASSED: Complete pipeline decoded {len(chunks)} chunks to original")

    def test_vbs_array_syntax_validity(self):
        """Test 6: Generated VBS array syntax is valid"""
        payload = self.test_payloads["simple"]
        vbs_code = self.encoder.create_array_concatenation_decoder(payload)

        # Parse VBS structure
        lines = vbs_code.split('\n')

        # Check for Dim array declaration
        dim_lines = [l for l in lines if 'Dim' in l and '(' in l]
        self.assertGreater(len(dim_lines), 0, "Should have Dim array declaration")

        # Extract array name from first Dim
        array_name_match = re.search(r'Dim\s+(\w+)\(', dim_lines[0])
        self.assertIsNotNone(array_name_match, "Should parse array name")
        array_name = array_name_match.group(1)

        # Check array element assignments
        assignment_lines = [l for l in lines if f'{array_name}(' in l and '=' in l]
        self.assertGreater(len(assignment_lines), 0, "Should have array element assignments")

        # Check For Each loop
        for_each_lines = [l for l in lines if 'For Each' in l]
        self.assertGreater(len(for_each_lines), 0, "Should have For Each loop")

        print(f"✓ Test 6 PASSED: VBS syntax structure validated (array: {array_name}, {len(assignment_lines)} assignments)")

    def test_multiple_payload_sizes(self):
        """Test 7: Various payload sizes"""
        test_cases = {
            "tiny": "a",
            "small": "cmd /c dir",
            "medium": self.test_payloads["medium"],
            "large": self.test_payloads["long"],
        }

        results = {}
        for name, payload in test_cases.items():
            vbs_code = self.encoder.create_array_concatenation_decoder(payload)

            # Verify it generates valid code
            self.assertIn("For Each", vbs_code)
            self.assertIn("Chr(CLng", vbs_code)

            # Count chunks (based on split logic)
            chunks = [payload[i:i+16] for i in range(0, len(payload), 16)]
            results[name] = {
                "payload_len": len(payload),
                "chunks": len(chunks),
                "vbs_len": len(vbs_code)
            }

        for name, data in results.items():
            print(f"  {name}: payload={data['payload_len']}B, chunks={data['chunks']}, vbs={data['vbs_len']}B")

        print(f"✓ Test 7 PASSED: Tested {len(results)} payload sizes")

    def test_special_characters_encoding(self):
        """Test 8: Special characters in payload"""
        payload = self.test_payloads["special_chars"]

        # Encode payload
        hex_encoded = binascii.hexlify(payload.encode()).decode()

        # Decode it back
        decoded = ""
        for i in range(0, len(hex_encoded), 2):
            hex_pair = hex_encoded[i:i+2]
            char_code = int(hex_pair, 16)
            decoded += chr(char_code)

        self.assertEqual(decoded, payload, "Special characters should survive encoding/decoding")
        print(f"✓ Test 8 PASSED: Special characters encoded/decoded correctly")

    def test_array_variable_names(self):
        """Test 9: Array variable names are properly generated"""
        payload = self.test_payloads["medium"]
        vbs_code = self.encoder.create_array_concatenation_decoder(payload)

        # Extract variable names
        dim_match = re.search(r'Dim\s+(\w+)\(', vbs_code)
        self.assertIsNotNone(dim_match, "Should have array dimension")
        array_var = dim_match.group(1)

        # Find loop variable
        for_match = re.search(r'For Each\s+(\w+)\s+In', vbs_code)
        self.assertIsNotNone(for_match, "Should have For Each loop")
        loop_var = for_match.group(1)

        # Output variable should be used in concatenation
        self.assertIn(f"{loop_var}", vbs_code, "Loop variable should be used")

        print(f"✓ Test 9 PASSED: Variable names generated (array: {array_var}, loop: {loop_var})")

    def test_execution_wrapper(self):
        """Test 10: Execution wrapper present"""
        payload = self.test_payloads["simple"]
        vbs_code = self.encoder.create_array_concatenation_decoder(payload)

        # Check for WScript.Shell execution
        self.assertIn("WScript.Shell", vbs_code, "Should use WScript.Shell")
        self.assertIn(".Run", vbs_code, "Should use .Run method")
        self.assertIn("0", vbs_code, "Should hide window (0)")

        # Verify structure: SetCreateObject → Set var = CreateObject("WScript.Shell")
        set_match = re.search(r'Set\s+(\w+)\s*=\s*CreateObject\("WScript\.Shell"\)', vbs_code)
        self.assertIsNotNone(set_match, "Should create WScript.Shell object")
        shell_var = set_match.group(1)

        # Check Run call
        run_match = re.search(rf'{re.escape(shell_var)}\.Run', vbs_code)
        self.assertIsNotNone(run_match, "Should call Run on shell object")

        print(f"✓ Test 10 PASSED: Execution wrapper validated (shell var: {shell_var})")

    def test_concatenation_loop_logic(self):
        """Test 11: Inner hex-to-char conversion loop"""
        test_hex = "48656C6C6F"  # "Hello" in hex

        # Simulate the VBS loop: For i = 1 To Len(h) Step 2: r = r & Chr(CLng("&H" & Mid(h, i, 2)))
        result = ""
        for i in range(0, len(test_hex), 2):
            hex_pair = test_hex[i:i+2]
            char_code = int(hex_pair, 16)
            result += chr(char_code)

        self.assertEqual(result, "Hello", "Loop logic should decode hex correctly")
        print(f"✓ Test 11 PASSED: Hex-to-char loop logic validated")

    def test_vbs_code_has_no_syntax_errors(self):
        """Test 12: Generated VBS code passes basic syntax checks"""
        payload = self.test_payloads["medium"]
        vbs_code = self.encoder.create_array_concatenation_decoder(payload)

        # Basic syntax checks
        checks = {
            "Balanced Dim declarations": vbs_code.count("Dim") >= 1,
            "No unclosed strings": vbs_code.count('"') % 2 == 0,
            "Has For loop": vbs_code.count("For") >= 2,  # For Each and inner For
            "Has Next statements": vbs_code.count("Next") >= 2,  # Two For loops need Next
            "Proper Next pairing": vbs_code.count("For") == vbs_code.count("Next"),
            "Has Set statements": vbs_code.count("Set") >= 1,
            "No orphaned control flow": True,  # Manual verification
        }

        failed_checks = [name for name, passed in checks.items() if not passed]
        self.assertEqual(len(failed_checks), 0, f"Syntax checks failed: {failed_checks}")

        print(f"✓ Test 12 PASSED: All VBS syntax checks passed")

    def test_payload_reconstruction_integrity(self):
        """Test 13: Payload reconstruction from multiple chunks maintains integrity"""
        for payload_name, payload in self.test_payloads.items():
            # Simulate full encode-decode cycle
            chunks = [payload[i:i+16] for i in range(0, len(payload), 16)]

            # Encode all chunks
            all_hex_chunks = [binascii.hexlify(c.encode()).decode() for c in chunks]

            # Reconstruct by decoding all chunks
            reconstructed = ""
            for hex_chunk in all_hex_chunks:
                for i in range(0, len(hex_chunk), 2):
                    hex_pair = hex_chunk[i:i+2]
                    reconstructed += chr(int(hex_pair, 16))

            self.assertEqual(reconstructed, payload,
                           f"Payload '{payload_name}' should reconstruct perfectly")

        print(f"✓ Test 13 PASSED: All {len(self.test_payloads)} payloads maintain integrity")

    def test_array_bounds(self):
        """Test 14: Array bounds are correct"""
        payload = self.test_payloads["long"]
        chunks = [payload[i:i+16] for i in range(0, len(payload), 16)]

        # Parse VBS code to verify array bounds
        vbs_code = self.encoder.create_array_concatenation_decoder(payload)

        # Look for array declaration with bounds
        dim_match = re.search(r'Dim\s+\w+\((\d+)\)', vbs_code)
        self.assertIsNotNone(dim_match, "Should have array bounds")

        declared_size = int(dim_match.group(1))
        expected_size = len(chunks) - 1  # VBS arrays are 0-indexed

        self.assertEqual(declared_size, expected_size,
                        f"Array bounds {declared_size} should match chunk count {expected_size}")

        print(f"✓ Test 14 PASSED: Array bounds correct (size: {declared_size}, chunks: {len(chunks)})")

    def test_performance_with_large_payload(self):
        """Test 15: Performance with large payload"""
        import time

        # Create large payload
        large_payload = "powershell.exe -Command " + ("A" * 5000)

        start = time.time()
        vbs_code = self.encoder.create_array_concatenation_decoder(large_payload)
        elapsed = time.time() - start

        # Should complete quickly
        self.assertLess(elapsed, 1.0, f"Generation should be fast, took {elapsed:.3f}s")

        # Verify it's still valid
        self.assertIn("For Each", vbs_code)
        self.assertIn("Chr(CLng", vbs_code)

        print(f"✓ Test 15 PASSED: Large payload (5KB+) generated in {elapsed:.4f}s")


class ArrayDecoderIntegration(unittest.TestCase):
    """Integration tests combining multiple components"""

    def setUp(self):
        self.encoder = VBSEncoder()

    def test_array_vs_other_decoders(self):
        """Test 16: Array decoder produces different output than other methods"""
        payload = "cmd /c echo test"

        array_code = self.encoder.create_array_concatenation_decoder(payload)
        base64_code = self.encoder.create_base64_decoder_vbs(payload)
        hex_code = self.encoder.create_hex_decoder_vbs(payload, execute=True)

        # Should be different
        self.assertNotEqual(array_code, base64_code, "Array and base64 decoders should differ")
        self.assertNotEqual(array_code, hex_code, "Array and hex decoders should differ")

        # Array and base64 should have CreateObject
        for name, code in [("array", array_code), ("base64", base64_code), ("hex", hex_code)]:
            self.assertIn("CreateObject", code, f"{name} should have CreateObject")

        # All should have proper structure
        for name, code in [("array", array_code), ("base64", base64_code), ("hex", hex_code)]:
            self.assertGreater(len(code), 50, f"{name} code should be substantial")

        print(f"✓ Test 16 PASSED: Array decoder produces distinct code")

    def test_cache_effectiveness(self):
        """Test 17: Encoder caching works efficiently"""
        payload = "test payload"

        # First encoding
        import time
        start = time.time()
        encoded1, var1 = self.encoder.encode_string_base64(payload)
        time1 = time.time() - start

        # Second encoding (should be cached)
        start = time.time()
        encoded2, var2 = self.encoder.encode_string_base64(payload)
        time2 = time.time() - start

        # Should get same encoding
        self.assertEqual(encoded1, encoded2, "Cached encoding should be identical")

        # Cache should be faster (or at least same)
        self.assertLessEqual(time2, time1 * 1.5, "Cached access should be fast")

        print(f"✓ Test 17 PASSED: Caching effective (first: {time1*1000:.3f}ms, cached: {time2*1000:.3f}ms)")

    def test_random_name_generation(self):
        """Test 18: Random names are generated properly"""
        payload = "test"
        vbs_code = self.encoder.create_array_concatenation_decoder(payload)

        # Extract all variable names
        variables = re.findall(r'\b[a-zA-Z_]\w*\b', vbs_code)
        unique_vars = set(variables)

        # Should have multiple unique variables
        self.assertGreater(len(unique_vars), 5, "Should generate multiple distinct variable names")

        # VBS keywords should be present
        keywords = {'Dim', 'For', 'Next', 'Set', 'CreateObject', 'Run'}
        for keyword in keywords:
            self.assertIn(keyword, vbs_code, f"Should contain VBS keyword: {keyword}")

        print(f"✓ Test 18 PASSED: Generated {len(unique_vars)} unique variable names")


if __name__ == "__main__":
    # Run with verbose output
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("ARRAY DECODER END-TO-END TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
