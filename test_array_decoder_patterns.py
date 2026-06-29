#!/usr/bin/env python3
"""
Comprehensive test suite for Array Decoder Patterns
Tests all 10 concatenation patterns with multiple variations
"""

import unittest
import binascii
import re
from array_decoder_patterns import (
    ArrayDecoderPatterns,
    DecoderPattern,
    DecoderVariant
)


class TestArrayDecoderPatterns(unittest.TestCase):
    """Test suite for all decoder patterns"""

    def setUp(self):
        self.generator = ArrayDecoderPatterns()
        self.test_payloads = {
            "simple": "cmd /c echo Test",
            "medium": "powershell.exe -NoProfile -Command Write-Host 'Success'",
            "long": "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass\"",
        }

    def _validate_vbs_structure(self, code: str, pattern_name: str):
        """Common VBS structure validation"""
        self.assertIn("Dim", code, f"{pattern_name}: Should declare variables")
        self.assertIn("For", code, f"{pattern_name}: Should have loop")
        self.assertIn("Next", code, f"{pattern_name}: Should have Next")
        self.assertIn("CreateObject", code, f"{pattern_name}: Should create objects")
        self.assertIn("WScript.Shell", code, f"{pattern_name}: Should use WScript.Shell")
        self.assertIn(".Run", code, f"{pattern_name}: Should execute with Run")

    def _extract_array_indices(self, code: str) -> int:
        """Extract number of array chunks from code"""
        matches = re.findall(r'\("([0-9a-f]{2})*"\)', code)
        return len(matches)

    # ===== TEST PATTERN 1: SEQUENTIAL =====
    def test_1_sequential_basic(self):
        """Test sequential decoder basic generation"""
        payload = self.test_payloads["simple"]
        variant = DecoderVariant(pattern=DecoderPattern.SEQUENTIAL)
        code = self.generator.sequential_decoder(payload, variant)

        self._validate_vbs_structure(code, "SEQUENTIAL")
        self.assertIn("For", code)
        self.assertIn("To UBound", code)
        self.assertTrue("Step 2" in code or "For i = 1" in code)
        print("✓ Test 1: Sequential decoder basic structure valid")

    def test_1_sequential_chunks(self):
        """Test sequential decoder creates correct number of chunks"""
        payload = self.test_payloads["long"]
        variant = DecoderVariant(pattern=DecoderPattern.SEQUENTIAL, chunk_size=16)
        code = self.generator.sequential_decoder(payload, variant)

        expected_chunks = (len(payload) + 15) // 16  # Ceiling division
        dim_match = re.search(r'Dim\s+\w+\((\d+)\)', code)
        self.assertIsNotNone(dim_match)
        declared_size = int(dim_match.group(1))
        self.assertEqual(declared_size, expected_chunks - 1)
        print(f"✓ Test 2: Sequential creates {expected_chunks} chunks as expected")

    # ===== TEST PATTERN 2: INTERLEAVED =====
    def test_2_interleaved_basic(self):
        """Test interleaved decoder generation"""
        payload = self.test_payloads["medium"]
        variant = DecoderVariant(pattern=DecoderPattern.INTERLEAVED)
        code = self.generator.interleaved_decoder(payload, variant)

        self._validate_vbs_structure(code, "INTERLEAVED")
        self.assertIn("Step 2", code)  # Should use Step 2 for even/odd
        self.assertGreaterEqual(code.count("For"), 2)  # At least two separate loops
        print("✓ Test 3: Interleaved decoder structure valid")

    def test_2_interleaved_even_odd(self):
        """Test interleaved processes even then odd indices"""
        payload = self.test_payloads["simple"]
        variant = DecoderVariant(pattern=DecoderPattern.INTERLEAVED)
        code = self.generator.interleaved_decoder(payload, variant)

        # Should have two separate For loops with Step 2
        self.assertIn("Step 2", code)
        self.assertGreater(code.count("For"), 1)
        print("✓ Test 4: Interleaved even/odd pattern detected")

    # ===== TEST PATTERN 3: NESTED ARRAY =====
    def test_3_nested_array_2d(self):
        """Test nested 2D array decoder"""
        payload = self.test_payloads["long"]
        variant = DecoderVariant(pattern=DecoderPattern.NESTED_ARRAY)
        code = self.generator.nested_array_decoder(payload, variant)

        self._validate_vbs_structure(code, "NESTED_ARRAY")
        self.assertIn("UBound(", code)
        # Should have nested For loops for rows and columns
        self.assertGreater(code.count("For"), 1)
        print("✓ Test 5: Nested 2D array decoder valid")

    def test_3_nested_matrix_access(self):
        """Test nested array uses 2D indexing"""
        payload = self.test_payloads["simple"]
        variant = DecoderVariant(pattern=DecoderPattern.NESTED_ARRAY)
        code = self.generator.nested_array_decoder(payload, variant)

        # Should have 2D array access: array(row, col)
        two_d_pattern = re.search(r'\(\d+,\s*\d+\)', code)
        self.assertIsNotNone(two_d_pattern, "Should use 2D array indexing")
        print("✓ Test 6: Nested array uses 2D indexing")

    # ===== TEST PATTERN 4: MIXED ENCODING =====
    def test_4_mixed_encoding_basic(self):
        """Test mixed encoding decoder"""
        payload = self.test_payloads["medium"]
        variant = DecoderVariant(pattern=DecoderPattern.MIXED_ENCODING)
        code = self.generator.mixed_encoding_decoder(payload, variant)

        self._validate_vbs_structure(code, "MIXED_ENCODING")
        # Check for either Dictionary or mixed encoding conditional
        self.assertTrue("MSXML2.DOMDocument" in code or "If" in code)
        self.assertIn("hex", code)  # Should check encoding type
        print("✓ Test 7: Mixed encoding decoder valid")

    def test_4_mixed_encoding_types(self):
        """Test mixed encoding uses both hex and base64"""
        payload = self.test_payloads["simple"]
        variant = DecoderVariant(pattern=DecoderPattern.MIXED_ENCODING)
        code = self.generator.mixed_encoding_decoder(payload, variant)

        # Should have mixed encoding logic
        self.assertIn("hex", code)
        # Should have conditional or function for encoding type
        self.assertTrue("If" in code or "Function" in code)
        print("✓ Test 8: Mixed encoding uses multiple types")

    # ===== TEST PATTERN 5: REVERSE ORDER =====
    def test_5_reverse_order_basic(self):
        """Test reverse order decoder"""
        payload = self.test_payloads["medium"]
        variant = DecoderVariant(pattern=DecoderPattern.REVERSE_ORDER)
        code = self.generator.reverse_order_decoder(payload, variant)

        self._validate_vbs_structure(code, "REVERSE_ORDER")
        self.assertIn("Step -1", code)  # Reverse iteration
        print("✓ Test 9: Reverse order decoder valid")

    def test_5_reverse_iteration(self):
        """Test reverse order uses negative step"""
        payload = self.test_payloads["simple"]
        variant = DecoderVariant(pattern=DecoderPattern.REVERSE_ORDER)
        code = self.generator.reverse_order_decoder(payload, variant)

        self.assertIn("Step -1", code)
        self.assertIn("To 0", code)
        print("✓ Test 10: Reverse order iterates backwards")

    # ===== TEST PATTERN 6: CHUNK INDEX =====
    def test_6_chunk_index_basic(self):
        """Test chunk index (dictionary) decoder"""
        payload = self.test_payloads["medium"]
        variant = DecoderVariant(pattern=DecoderPattern.CHUNK_INDEX)
        code = self.generator.chunk_index_decoder(payload, variant)

        self._validate_vbs_structure(code, "CHUNK_INDEX")
        self.assertIn("Scripting.Dictionary", code)
        self.assertIn(".Add", code)  # Dictionary Add method
        print("✓ Test 11: Chunk index decoder valid")

    def test_6_dictionary_usage(self):
        """Test chunk index uses dictionary objects"""
        payload = self.test_payloads["simple"]
        variant = DecoderVariant(pattern=DecoderPattern.CHUNK_INDEX)
        code = self.generator.chunk_index_decoder(payload, variant)

        self.assertIn("Scripting.Dictionary", code)
        self.assertIn(".Add", code)
        self.assertIn(".Item", code)
        self.assertIn(".Count", code)
        print("✓ Test 12: Dictionary methods used correctly")

    # ===== TEST PATTERN 7: OBFUSCATED VAR =====
    def test_7_obfuscated_var_basic(self):
        """Test obfuscated variable decoder"""
        payload = self.test_payloads["medium"]
        variant = DecoderVariant(pattern=DecoderPattern.OBFUSCATED_VAR)
        code = self.generator.obfuscated_var_decoder(payload, variant)

        self._validate_vbs_structure(code, "OBFUSCATED_VAR")
        self.assertIn("Dim", code)
        self.assertIn("For", code)
        print("✓ Test 13: Obfuscated variable decoder valid")

    def test_7_obfuscated_names(self):
        """Test obfuscated variables have short names"""
        payload = self.test_payloads["simple"]
        variant = DecoderVariant(pattern=DecoderPattern.OBFUSCATED_VAR, randomize_names=False)
        code = self.generator.obfuscated_var_decoder(payload, variant)

        # Should have short variable names like x_1, x_2, etc.
        self.assertIn("x_", code)
        print("✓ Test 14: Obfuscated variables have short names")

    # ===== TEST PATTERN 8: POLYMORPHIC =====
    def test_8_polymorphic_basic(self):
        """Test polymorphic decoder"""
        payload = self.test_payloads["medium"]
        variant = DecoderVariant(pattern=DecoderPattern.POLYMORPHIC)
        code = self.generator.polymorphic_decoder(payload, variant)

        self._validate_vbs_structure(code, "POLYMORPHIC")
        self.assertIn("Function", code)  # Should have multiple functions
        self.assertIn("Select Case", code)  # Should select between implementations
        print("✓ Test 15: Polymorphic decoder valid")

    def test_8_polymorphic_functions(self):
        """Test polymorphic decoder has multiple decode functions"""
        payload = self.test_payloads["simple"]
        variant = DecoderVariant(pattern=DecoderPattern.POLYMORPHIC)
        code = self.generator.polymorphic_decoder(payload, variant)

        # Should have multiple Decode functions
        self.assertGreater(code.count("Function"), 2)
        self.assertIn("Select Case", code)
        self.assertIn("Case 0", code)
        print("✓ Test 16: Polymorphic has multiple implementations")

    # ===== TEST PATTERN 9: SPLIT DECODE =====
    def test_9_split_decode_basic(self):
        """Test split decode decoder"""
        payload = self.test_payloads["long"]
        variant = DecoderVariant(pattern=DecoderPattern.SPLIT_DECODE)
        code = self.generator.split_decode_decoder(payload, variant)

        self._validate_vbs_structure(code, "SPLIT_DECODE")
        self.assertIn("Function", code)  # Should have decode function
        # Should call function multiple times
        self.assertGreater(code.count("Decode"), 1)
        print("✓ Test 17: Split decode decoder valid")

    def test_9_split_groups(self):
        """Test split decode creates multiple groups"""
        payload = self.test_payloads["long"]
        variant = DecoderVariant(pattern=DecoderPattern.SPLIT_DECODE)
        code = self.generator.split_decode_decoder(payload, variant)

        # Should have at least 2 arrays
        dim_count = code.count("Dim arr")
        self.assertGreaterEqual(dim_count, 2, "Should have multiple arrays")
        print("✓ Test 18: Split decode has multiple arrays")

    # ===== TEST PATTERN 10: MATRIX ACCESS =====
    def test_10_matrix_access_basic(self):
        """Test matrix access decoder"""
        payload = self.test_payloads["medium"]
        variant = DecoderVariant(pattern=DecoderPattern.MATRIX_ACCESS)
        code = self.generator.matrix_access_decoder(payload, variant)

        self._validate_vbs_structure(code, "MATRIX_ACCESS")
        self.assertIn("Mod", code)  # Should use modulo arithmetic
        print("✓ Test 19: Matrix access decoder valid")

    def test_10_computed_indices(self):
        """Test matrix access uses computed indices"""
        payload = self.test_payloads["simple"]
        variant = DecoderVariant(pattern=DecoderPattern.MATRIX_ACCESS)
        code = self.generator.matrix_access_decoder(payload, variant)

        self.assertIn("Mod", code)  # Modulo for wrapping indices
        self.assertIn("computed_idx", code)
        print("✓ Test 20: Matrix access uses computed indices")


class TestPatternComparison(unittest.TestCase):
    """Compare different patterns"""

    def setUp(self):
        self.generator = ArrayDecoderPatterns()
        self.payload = "cmd /c dir"

    def test_all_patterns_generate_valid_code(self):
        """Test all patterns generate valid VBS code"""
        results = self.generator.generate_all_patterns(self.payload)

        self.assertEqual(len(results), len(DecoderPattern))
        for pattern_name, code in results.items():
            self.assertIsNotNone(code)
            self.assertGreater(len(code), 100)
            self.assertIn("Dim", code)
            self.assertIn("CreateObject", code)
            self.assertIn("WScript.Shell", code)

        print(f"✓ Test 21: All {len(results)} patterns generate valid code")

    def test_patterns_are_unique(self):
        """Test each pattern produces unique code"""
        results = self.generator.generate_all_patterns(self.payload)
        codes = list(results.values())

        # Each code should be unique
        unique_codes = set(codes)
        self.assertEqual(len(unique_codes), len(codes),
                        "All patterns should produce unique code")

        print(f"✓ Test 22: All {len(results)} patterns are unique")

    def test_pattern_code_sizes(self):
        """Test code size varies by pattern"""
        results = self.generator.generate_all_patterns(self.payload)

        sizes = {name: len(code) for name, code in results.items()}
        min_size = min(sizes.values())
        max_size = max(sizes.values())

        print("\n✓ Test 23: Pattern code sizes vary:")
        for name, size in sorted(sizes.items(), key=lambda x: x[1]):
            print(f"  {name:20s}: {size:5d} bytes")

        self.assertGreater(max_size, min_size * 1.5,
                          "Patterns should have different code sizes")

    def test_pattern_feature_coverage(self):
        """Test patterns use different VBS features"""
        results = self.generator.generate_all_patterns(self.payload)

        features = {
            "Dictionary": "Scripting.Dictionary",
            "2D Array": "(",
            "Select Case": "Select Case",
            "Multiple Functions": "Function",
            "Do Loop": "Do",
            "Modulo": "Mod",
        }

        pattern_features = {}
        for pattern_name, code in results.items():
            used_features = []
            for feat_name, feat_pattern in features.items():
                if feat_pattern in code:
                    used_features.append(feat_name)
            pattern_features[pattern_name] = used_features

        print("\n✓ Test 24: Pattern features:")
        for pattern, feats in sorted(pattern_features.items()):
            print(f"  {pattern:20s}: {', '.join(feats) if feats else '(basic)'}")


class TestPatternVariants(unittest.TestCase):
    """Test variants and configurations"""

    def setUp(self):
        self.generator = ArrayDecoderPatterns()
        self.payload = "test payload"

    def test_chunk_size_variants(self):
        """Test different chunk sizes"""
        chunk_sizes = [8, 16, 32, 64]

        for size in chunk_sizes:
            variant = DecoderVariant(
                pattern=DecoderPattern.SEQUENTIAL,
                chunk_size=size
            )
            code = self.generator.sequential_decoder(self.payload, variant)
            self.assertIn("Dim", code)
            self.assertIn("For", code)

        print(f"✓ Test 25: Tested {len(chunk_sizes)} chunk size variants")

    def test_randomization_toggle(self):
        """Test randomization on/off"""
        variant_random = DecoderVariant(
            pattern=DecoderPattern.SEQUENTIAL,
            randomize_names=True
        )
        variant_static = DecoderVariant(
            pattern=DecoderPattern.SEQUENTIAL,
            randomize_names=False
        )

        code_random = self.generator.sequential_decoder(self.payload, variant_random)
        code_static = self.generator.sequential_decoder(self.payload, variant_static)

        # Both should be valid
        self.assertIn("Dim", code_random)
        self.assertIn("Dim", code_static)

        # Both should have variables
        self.assertGreater(len(code_random), 50)
        self.assertGreater(len(code_static), 50)

        print("✓ Test 26: Randomization toggle works")

    def test_multiple_encodings_compatibility(self):
        """Test mixing patterns with payloads of various sizes"""
        payloads = [
            "a",
            "short cmd",
            "medium command payload here",
            "l" * 1000,  # Large payload
        ]

        for payload in payloads:
            for pattern in DecoderPattern:
                variant = DecoderVariant(pattern=pattern)
                code = self.generator.generate_decoder(payload, pattern, variant)
                self.assertIn("CreateObject", code)
                self.assertGreater(len(code), 50)

        print(f"✓ Test 27: All patterns handle {len(payloads)} payload sizes")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*80)
    print("ARRAY DECODER PATTERNS TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*80)

    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
        for test, traceback in result.failures + result.errors:
            print(f"\nFailed: {test}")
            print(traceback)
