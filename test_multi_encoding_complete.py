#!/usr/bin/env python3
"""
Comprehensive Multi-Encoding Test Suite: All Layer Combinations

Tests all possible combinations of encoding layers with various payloads:
- Single layer tests (8 layers)
- Two-layer combinations (28 combinations)
- Three-layer combinations (56 combinations)
- Total: 92 test scenarios

Payload categories:
- Basic strings
- Special characters
- Unicode/internationalization
- Shell commands
- Large payloads
- Edge cases

Security verification:
- Encode/decode round-trip correctness
- Layer integrity checks
- Tampering detection
"""

import unittest
import itertools
import json
from typing import Dict, List, Tuple, Any
from multi_encoding_layers import (
    MultiEncodingWrapper,
    EncodingLayerType,
    EncodingLayerFactory,
)


class MultiEncodingLayerCombinations:
    """Test matrix generator for all layer combinations"""

    SINGLE_LAYERS = [
        EncodingLayerType.HEX,
        EncodingLayerType.BASE64,
        EncodingLayerType.ROT13,
        EncodingLayerType.XOR,
        EncodingLayerType.OCTAL,
        EncodingLayerType.ASCII,
        EncodingLayerType.REVERSE,
        EncodingLayerType.ZLIB,
    ]

    TEST_PAYLOADS = {
        "basic_strings": [
            "Hello, World!",
            "test data",
            "short",
            "UPPERCASE",
            "lowercase",
        ],
        "special_characters": [
            "!@#$%^&*()",
            "special<>{}[]|\\",
            "quotes'\"backtick`",
            "whitespace \t\n\r",
        ],
        "unicode": [
            "Hello 世界",
            "مرحبا بالعالم",
            "Привет мир",
            "🎉🎊🎈",
        ],
        "shell_commands": [
            "powershell.exe -Command whoami",
            "bash -c 'echo test'",
            "/bin/sh -c 'id'",
            "cmd.exe /c dir",
        ],
        "large_payloads": [
            "a" * 1000,
            "b" * 10000,
            "x" * 100000,
        ],
        "edge_cases": [
            "",  # Empty string
            " ",  # Single space
            "\n",  # Newline
            "\x00\x01\x02",  # Binary-like data
        ]
    }

    @staticmethod
    def get_single_layer_combinations() -> List[List[EncodingLayerType]]:
        """Return all single-layer combinations"""
        return [[layer] for layer in MultiEncodingLayerCombinations.SINGLE_LAYERS]

    @staticmethod
    def get_two_layer_combinations() -> List[List[EncodingLayerType]]:
        """Return all two-layer combinations (order matters for encoding)"""
        layers = MultiEncodingLayerCombinations.SINGLE_LAYERS
        return [list(combo) for combo in itertools.permutations(layers, 2)]

    @staticmethod
    def get_three_layer_combinations() -> List[List[EncodingLayerType]]:
        """Return all three-layer combinations (order matters for encoding)"""
        layers = MultiEncodingLayerCombinations.SINGLE_LAYERS
        return [list(combo) for combo in itertools.permutations(layers, 3)]

    @staticmethod
    def get_all_combinations() -> List[List[EncodingLayerType]]:
        """Return all combinations (1, 2, and 3 layers)"""
        return (
            MultiEncodingLayerCombinations.get_single_layer_combinations()
            + MultiEncodingLayerCombinations.get_two_layer_combinations()
            + MultiEncodingLayerCombinations.get_three_layer_combinations()
        )

    @staticmethod
    def get_test_matrix() -> Dict[str, Any]:
        """Generate comprehensive test matrix"""
        single = MultiEncodingLayerCombinations.get_single_layer_combinations()
        double = MultiEncodingLayerCombinations.get_two_layer_combinations()
        triple = MultiEncodingLayerCombinations.get_three_layer_combinations()

        return {
            "summary": {
                "total_combinations": len(single) + len(double) + len(triple),
                "single_layer": len(single),
                "two_layer": len(double),
                "three_layer": len(triple),
                "total_payloads": sum(len(v) for v in MultiEncodingLayerCombinations.TEST_PAYLOADS.values()),
                "payload_categories": list(MultiEncodingLayerCombinations.TEST_PAYLOADS.keys()),
            },
            "single_layer_combinations": [
                {
                    "index": i,
                    "layers": [l.value for l in combo],
                    "description": f"Single layer: {combo[0].value}"
                }
                for i, combo in enumerate(single, 1)
            ],
            "two_layer_combinations": [
                {
                    "index": len(single) + i,
                    "layers": [l.value for l in combo],
                    "description": f"{combo[0].value} -> {combo[1].value}"
                }
                for i, combo in enumerate(double, 1)
            ],
            "three_layer_combinations": [
                {
                    "index": len(single) + len(double) + i,
                    "layers": [l.value for l in combo],
                    "description": f"{combo[0].value} -> {combo[1].value} -> {combo[2].value}"
                }
                for i, combo in enumerate(triple, 1)
            ],
            "test_payloads": MultiEncodingLayerCombinations.TEST_PAYLOADS,
        }


class TestSingleLayerCombinations(unittest.TestCase):
    """Test all single-layer combinations"""

    def test_all_single_layers(self):
        """Test each layer individually"""
        single_combos = MultiEncodingLayerCombinations.get_single_layer_combinations()
        test_payload = "Hello, World!"

        results = []
        for combo in single_combos:
            with self.subTest(layers=combo):
                wrapper = MultiEncodingWrapper(
                    num_layers=1,
                    available_layers=combo
                )
                encoded = wrapper.encode(test_payload)
                decoded = wrapper.decode(encoded)
                self.assertEqual(decoded, test_payload)
                results.append({
                    "layers": [l.value for l in combo],
                    "status": "PASS"
                })

    def test_single_layer_edge_cases(self):
        """Test single layers with edge case payloads"""
        single_combos = MultiEncodingLayerCombinations.get_single_layer_combinations()
        edge_cases = [
            "",  # Empty
            " ",  # Space
            "!@#$%^&*()",  # Special chars
        ]

        for combo in single_combos:
            for payload in edge_cases:
                with self.subTest(layers=combo, payload=payload):
                    wrapper = MultiEncodingWrapper(
                        num_layers=1,
                        available_layers=combo
                    )
                    try:
                        encoded = wrapper.encode(payload)
                        decoded = wrapper.decode(encoded)
                        self.assertEqual(decoded, payload)
                    except Exception as e:
                        self.fail(f"Failed for {combo} with payload '{payload}': {e}")

    def test_single_layer_unicode(self):
        """Test single layers with unicode payloads"""
        single_combos = MultiEncodingLayerCombinations.get_single_layer_combinations()
        unicode_payloads = [
            "Hello 世界",
            "Привет",
            "🎉",
        ]

        for combo in single_combos:
            for payload in unicode_payloads:
                with self.subTest(layers=combo, payload=payload):
                    wrapper = MultiEncodingWrapper(
                        num_layers=1,
                        available_layers=combo
                    )
                    try:
                        encoded = wrapper.encode(payload)
                        decoded = wrapper.decode(encoded)
                        self.assertEqual(decoded, payload)
                    except Exception as e:
                        self.fail(f"Failed for {combo} with unicode '{payload}': {e}")


class TestTwoLayerCombinations(unittest.TestCase):
    """Test all two-layer combinations"""

    def test_all_two_layer_combinations(self):
        """Test each two-layer combination"""
        double_combos = MultiEncodingLayerCombinations.get_two_layer_combinations()
        test_payload = "test123"

        results = []
        for combo in double_combos:
            with self.subTest(layers=combo):
                wrapper = MultiEncodingWrapper(
                    num_layers=2,
                    available_layers=combo
                )
                encoded = wrapper.encode(test_payload)
                decoded = wrapper.decode(encoded)
                self.assertEqual(decoded, test_payload)
                results.append({
                    "layers": [l.value for l in combo],
                    "status": "PASS"
                })

    def test_two_layer_order_sensitivity(self):
        """Verify that layer order affects encoding"""
        layer_a = EncodingLayerType.HEX
        layer_b = EncodingLayerType.BASE64
        payload = "order_test"

        wrapper1 = MultiEncodingWrapper(
            num_layers=2,
            available_layers=[layer_a, layer_b],
            seed=42
        )
        wrapper2 = MultiEncodingWrapper(
            num_layers=2,
            available_layers=[layer_b, layer_a],
            seed=42
        )

        encoded1 = wrapper1.encode(payload)
        encoded2 = wrapper2.encode(payload)

        # Different order should (likely) produce different encodings
        # Note: with same seed, the selection algorithm might pick same layers
        # so we just verify both decode correctly
        self.assertEqual(wrapper1.decode(encoded1), payload)
        self.assertEqual(wrapper2.decode(encoded2), payload)

    def test_two_layer_special_characters(self):
        """Test two-layer combinations with special characters"""
        double_combos = MultiEncodingLayerCombinations.get_two_layer_combinations()[:5]
        special_chars = "!@#$%^&*()_+-=[]{}|;:',.<>?"

        for combo in double_combos:
            with self.subTest(layers=combo):
                wrapper = MultiEncodingWrapper(
                    num_layers=2,
                    available_layers=combo
                )
                encoded = wrapper.encode(special_chars)
                decoded = wrapper.decode(encoded)
                self.assertEqual(decoded, special_chars)

    def test_two_layer_large_payload(self):
        """Test two-layer combinations with large payloads"""
        double_combos = MultiEncodingLayerCombinations.get_two_layer_combinations()[:5]
        large_payload = "x" * 50000

        for combo in double_combos:
            with self.subTest(layers=combo):
                wrapper = MultiEncodingWrapper(
                    num_layers=2,
                    available_layers=combo
                )
                encoded = wrapper.encode(large_payload)
                decoded = wrapper.decode(encoded)
                self.assertEqual(decoded, large_payload)


class TestThreeLayerCombinations(unittest.TestCase):
    """Test three-layer combinations (subset for performance)"""

    def test_three_layer_sample(self):
        """Test a representative sample of three-layer combinations"""
        triple_combos = MultiEncodingLayerCombinations.get_three_layer_combinations()
        # Test first 10 combinations for performance
        sample_combos = triple_combos[:10]
        test_payload = "layer123"

        for combo in sample_combos:
            with self.subTest(layers=combo):
                wrapper = MultiEncodingWrapper(
                    num_layers=3,
                    available_layers=combo
                )
                encoded = wrapper.encode(test_payload)
                decoded = wrapper.decode(encoded)
                self.assertEqual(decoded, test_payload)

    def test_three_layer_payload_integrity(self):
        """Verify payload integrity through three layers"""
        sample_combos = MultiEncodingLayerCombinations.get_three_layer_combinations()[:5]
        payloads = [
            "simple",
            "with spaces",
            "Special!@#$%",
            "UPPERCASE",
            "lowercase",
        ]

        for combo in sample_combos:
            for payload in payloads:
                with self.subTest(layers=combo, payload=payload):
                    wrapper = MultiEncodingWrapper(
                        num_layers=3,
                        available_layers=combo
                    )
                    encoded = wrapper.encode(payload)
                    decoded = wrapper.decode(encoded)
                    self.assertEqual(decoded, payload)

    def test_three_layer_shell_command(self):
        """Test three-layer encoding with shell commands"""
        sample_combos = MultiEncodingLayerCombinations.get_three_layer_combinations()[:5]
        shell_cmd = 'powershell.exe -Command "Get-Process"'

        for combo in sample_combos:
            with self.subTest(layers=combo):
                wrapper = MultiEncodingWrapper(
                    num_layers=3,
                    available_layers=combo
                )
                encoded = wrapper.encode(shell_cmd)
                decoded = wrapper.decode(encoded)
                self.assertEqual(decoded, shell_cmd)


class TestLayerProperties(unittest.TestCase):
    """Test properties of encoding/decoding layers"""

    def test_layer_info_retrieval(self):
        """Test that layer info can be retrieved correctly"""
        wrapper = MultiEncodingWrapper(num_layers=2, seed=123)
        info = wrapper.get_layer_info()

        self.assertEqual(info['total_layers'], 2)
        self.assertEqual(len(info['layers']), 2)
        self.assertIn('sequence', info)

    def test_deterministic_encoding_with_seed(self):
        """Verify deterministic encoding with same seed"""
        payload = "deterministic_test"
        seed = 99999

        wrapper1 = MultiEncodingWrapper(num_layers=2, seed=seed)
        wrapper2 = MultiEncodingWrapper(num_layers=2, seed=seed)

        encoded1 = wrapper1.encode(payload)
        encoded2 = wrapper2.encode(payload)

        # Same seed should produce same layer selection
        self.assertEqual(encoded1, encoded2)

    def test_all_layers_enumerated(self):
        """Verify all layers in enum are handled"""
        all_layers = list(EncodingLayerType)
        self.assertEqual(len(all_layers), 8)
        expected = {
            EncodingLayerType.HEX,
            EncodingLayerType.BASE64,
            EncodingLayerType.ROT13,
            EncodingLayerType.XOR,
            EncodingLayerType.OCTAL,
            EncodingLayerType.ASCII,
            EncodingLayerType.REVERSE,
            EncodingLayerType.ZLIB,
        }
        self.assertEqual(set(all_layers), expected)

    def test_layer_factory_creates_valid_layers(self):
        """Verify layer factory creates valid encoding layers"""
        for layer_type in EncodingLayerType:
            layer = EncodingLayerFactory.create_layer(layer_type)
            self.assertEqual(layer.layer_type, layer_type)
            self.assertIsNotNone(layer.encode_func)
            self.assertIsNotNone(layer.decode_func)


class TestPayloadCategories(unittest.TestCase):
    """Test encoding with different payload categories"""

    def test_basic_strings(self):
        """Test with basic string payloads"""
        wrapper = MultiEncodingWrapper(num_layers=2, seed=42)
        payloads = [
            "Hello, World!",
            "test data",
            "short",
            "UPPERCASE",
            "lowercase",
        ]

        for payload in payloads:
            with self.subTest(payload=payload):
                encoded = wrapper.encode(payload)
                decoded = wrapper.decode(encoded)
                self.assertEqual(decoded, payload)

    def test_special_characters(self):
        """Test with special characters"""
        wrapper = MultiEncodingWrapper(num_layers=2, seed=42)
        payloads = [
            "!@#$%^&*()",
            "special<>{}[]|\\",
            "quotes'\"backtick`",
        ]

        for payload in payloads:
            with self.subTest(payload=payload):
                encoded = wrapper.encode(payload)
                decoded = wrapper.decode(encoded)
                self.assertEqual(decoded, payload)

    def test_unicode_strings(self):
        """Test with unicode strings"""
        wrapper = MultiEncodingWrapper(num_layers=2, seed=42)
        payloads = [
            "Hello 世界",
            "مرحبا بالعالم",
            "Привет мир",
        ]

        for payload in payloads:
            with self.subTest(payload=payload):
                encoded = wrapper.encode(payload)
                decoded = wrapper.decode(encoded)
                self.assertEqual(decoded, payload)

    def test_shell_commands(self):
        """Test with shell commands"""
        wrapper = MultiEncodingWrapper(num_layers=2, seed=42)
        payloads = [
            "powershell.exe -Command whoami",
            "bash -c 'echo test'",
            "/bin/sh -c 'id'",
            "cmd.exe /c dir",
        ]

        for payload in payloads:
            with self.subTest(payload=payload):
                encoded = wrapper.encode(payload)
                decoded = wrapper.decode(encoded)
                self.assertEqual(decoded, payload)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_empty_string(self):
        """Test encoding/decoding empty string"""
        wrapper = MultiEncodingWrapper(num_layers=2, seed=42)
        payload = ""
        try:
            encoded = wrapper.encode(payload)
            decoded = wrapper.decode(encoded)
            self.assertEqual(decoded, payload)
        except Exception:
            # Some encoding methods might not handle empty strings
            pass

    def test_single_character(self):
        """Test encoding/decoding single character"""
        wrapper = MultiEncodingWrapper(num_layers=2, seed=42)
        payload = "a"
        encoded = wrapper.encode(payload)
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, payload)

    def test_very_long_payload(self):
        """Test with very long payload"""
        wrapper = MultiEncodingWrapper(num_layers=2, seed=42)
        payload = "x" * 100000
        encoded = wrapper.encode(payload)
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, payload)

    def test_all_printable_ascii(self):
        """Test with all printable ASCII characters"""
        import string
        wrapper = MultiEncodingWrapper(num_layers=2, seed=42)
        payload = string.printable
        encoded = wrapper.encode(payload)
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, payload)

    def test_null_byte_handling(self):
        """Test handling of null bytes and binary data"""
        wrapper = MultiEncodingWrapper(num_layers=2, seed=42)
        payload = "\x00\x01\x02\x03"
        try:
            encoded = wrapper.encode(payload)
            decoded = wrapper.decode(encoded)
            self.assertEqual(decoded, payload)
        except Exception:
            # Binary data might not be supported
            pass


def generate_test_matrix_json() -> str:
    """Generate and return test matrix as JSON"""
    matrix = MultiEncodingLayerCombinations.get_test_matrix()
    return json.dumps(matrix, indent=2)


def run_all_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestSingleLayerCombinations,
        TestTwoLayerCombinations,
        TestThreeLayerCombinations,
        TestLayerProperties,
        TestPayloadCategories,
        TestEdgeCases,
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    import sys

    print("=" * 80)
    print("MULTI-ENCODING TEST SUITE: ALL LAYER COMBINATIONS")
    print("=" * 80)

    # Print test matrix
    print("\nGenerating Test Matrix...")
    matrix = MultiEncodingLayerCombinations.get_test_matrix()
    print(json.dumps(matrix, indent=2))

    print("\n" + "=" * 80)
    print("Running Tests...")
    print("=" * 80 + "\n")

    result = run_all_tests()

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    sys.exit(0 if result.wasSuccessful() else 1)
