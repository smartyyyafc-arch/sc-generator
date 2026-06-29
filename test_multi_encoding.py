#!/usr/bin/env python3
"""
Unit tests for Multi-Encoding Wrapper
Verifies encoding/decoding correctness and layer functionality
"""

import unittest
from multi_encoding_layers import (
    MultiEncodingWrapper,
    EncodingLayerType,
    EncodingLayerFactory,
    create_multi_encoding_wrapper
)


class TestEncodingLayers(unittest.TestCase):
    """Test individual encoding layers"""

    def test_hex_encode_decode(self):
        """Test hex encoding and decoding"""
        test_data = "hello world"
        encoded = EncodingLayerFactory.hex_encode(test_data)
        decoded = EncodingLayerFactory.hex_decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_base64_encode_decode(self):
        """Test base64 encoding and decoding"""
        test_data = "secret message"
        encoded = EncodingLayerFactory.base64_encode(test_data)
        decoded = EncodingLayerFactory.base64_decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_rot13_encode_decode(self):
        """Test ROT13 encoding and decoding"""
        test_data = "test data"
        encoded = EncodingLayerFactory.rot13_encode(test_data)
        decoded = EncodingLayerFactory.rot13_decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_xor_encode_decode(self):
        """Test XOR encoding and decoding"""
        test_data = "xor test"
        key = 42
        encoded = EncodingLayerFactory.xor_encode(test_data, key)
        decoded = EncodingLayerFactory.xor_decode(encoded, key)
        self.assertEqual(decoded, test_data)

    def test_octal_encode_decode(self):
        """Test octal encoding and decoding"""
        test_data = "octal"
        encoded = EncodingLayerFactory.octal_encode(test_data)
        decoded = EncodingLayerFactory.octal_decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_ascii_encode_decode(self):
        """Test ASCII encoding and decoding"""
        test_data = "ascii"
        encoded = EncodingLayerFactory.ascii_encode(test_data)
        decoded = EncodingLayerFactory.ascii_decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_reverse_encode_decode(self):
        """Test reverse encoding and decoding"""
        test_data = "reverse"
        encoded = EncodingLayerFactory.reverse_encode(test_data)
        decoded = EncodingLayerFactory.reverse_decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_zlib_encode_decode(self):
        """Test zlib encoding and decoding"""
        test_data = "zlib compression test"
        encoded = EncodingLayerFactory.zlib_encode(test_data)
        decoded = EncodingLayerFactory.zlib_decode(encoded)
        self.assertEqual(decoded, test_data)


class TestMultiEncodingWrapper(unittest.TestCase):
    """Test MultiEncodingWrapper functionality"""

    def test_single_layer_encoding(self):
        """Test encoding with single layer"""
        wrapper = MultiEncodingWrapper(num_layers=1)
        test_data = "single layer"
        encoded = wrapper.encode(test_data)
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_double_layer_encoding(self):
        """Test encoding with two layers"""
        wrapper = MultiEncodingWrapper(num_layers=2)
        test_data = "double layer"
        encoded = wrapper.encode(test_data)
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_triple_layer_encoding(self):
        """Test encoding with three layers"""
        wrapper = MultiEncodingWrapper(num_layers=3)
        test_data = "triple layer"
        encoded = wrapper.encode(test_data)
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_random_layer_selection(self):
        """Test random layer selection"""
        wrapper = MultiEncodingWrapper()
        # Should have 1-3 layers
        self.assertGreaterEqual(wrapper.num_layers, 1)
        self.assertLessEqual(wrapper.num_layers, 3)
        # Should have correct number of layers
        self.assertEqual(len(wrapper.encoding_layers), wrapper.num_layers)

    def test_specific_layers(self):
        """Test selecting specific layers"""
        available = [
            EncodingLayerType.HEX,
            EncodingLayerType.BASE64
        ]
        wrapper = MultiEncodingWrapper(
            num_layers=2,
            available_layers=available
        )
        layer_types = [l.layer_type for l in wrapper.encoding_layers]
        for layer_type in layer_types:
            self.assertIn(layer_type, available)

    def test_deterministic_encoding(self):
        """Test that same seed produces same encoding"""
        test_data = "deterministic test"

        wrapper1 = MultiEncodingWrapper(num_layers=2, seed=12345)
        wrapper2 = MultiEncodingWrapper(num_layers=2, seed=12345)

        encoded1 = wrapper1.encode(test_data)
        encoded2 = wrapper2.encode(test_data)

        self.assertEqual(encoded1, encoded2)

    def test_layer_order_matters(self):
        """Test that decoding in reverse order is necessary"""
        wrapper = MultiEncodingWrapper(num_layers=2)
        test_data = "order test"
        encoded = wrapper.encode(test_data)

        # Decoding should work in reverse order
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_complex_payload(self):
        """Test with complex real-world payload"""
        payload = 'powershell.exe -Command "Get-Process | Select-Object Name"'
        wrapper = MultiEncodingWrapper(num_layers=3)
        encoded = wrapper.encode(payload)
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, payload)

    def test_get_layer_info(self):
        """Test layer information retrieval"""
        wrapper = MultiEncodingWrapper(num_layers=2)
        info = wrapper.get_layer_info()

        self.assertEqual(info['total_layers'], 2)
        self.assertEqual(len(info['layers']), 2)
        self.assertEqual(len(info['sequence']), 2)

        for layer in info['layers']:
            self.assertIn('index', layer)
            self.assertIn('type', layer)

    def test_python_decoder_generation(self):
        """Test Python decoder code generation"""
        wrapper = MultiEncodingWrapper(num_layers=2, seed=999)
        test_data = "decoder test"
        encoded = wrapper.encode(test_data)

        decoder_code = wrapper.generate_decoder_python(encoded, "payload")

        # Check that decoder code contains expected elements
        self.assertIn("import", decoder_code)
        self.assertIn("payload = ", decoder_code)
        self.assertIn("print", decoder_code)

    def test_powershell_decoder_generation(self):
        """Test PowerShell decoder code generation"""
        wrapper = MultiEncodingWrapper(num_layers=2, seed=999)
        test_data = "decoder test"
        encoded = wrapper.encode(test_data)

        decoder_code = wrapper.generate_decoder_powershell(encoded, "payload")

        # Check that decoder code contains expected elements
        self.assertIn("$payload", decoder_code)
        self.assertIn("Write-Host", decoder_code)

    def test_generate_wrapper_report(self):
        """Test wrapper report generation"""
        wrapper = MultiEncodingWrapper(num_layers=2)
        report = wrapper.generate_wrapper_report()

        # Check report contains expected information
        self.assertIn("MULTI-ENCODING WRAPPER", report)
        self.assertIn("Total Encoding Layers", report)
        self.assertIn("Layer Sequence", report)

    def test_empty_string_encoding(self):
        """Test encoding empty string"""
        wrapper = MultiEncodingWrapper(num_layers=1)
        test_data = ""
        encoded = wrapper.encode(test_data)
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_special_characters(self):
        """Test encoding special characters"""
        wrapper = MultiEncodingWrapper(num_layers=2)
        test_data = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        encoded = wrapper.encode(test_data)
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_long_payload(self):
        """Test encoding long payload"""
        wrapper = MultiEncodingWrapper(num_layers=2)
        test_data = "a" * 10000
        encoded = wrapper.encode(test_data)
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_convenience_function(self):
        """Test convenience function"""
        wrapper = create_multi_encoding_wrapper(num_layers=2, seed=42)
        self.assertEqual(wrapper.num_layers, 2)

    def test_layer_types_validity(self):
        """Test that all layers in encoding are valid"""
        wrapper = MultiEncodingWrapper()
        for layer in wrapper.encoding_layers:
            self.assertIsInstance(layer.layer_type, EncodingLayerType)
            self.assertIsNotNone(layer.encode_func)
            self.assertIsNotNone(layer.decode_func)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_num_layers_boundary_low(self):
        """Test num_layers=0 defaults to 1"""
        wrapper = MultiEncodingWrapper(num_layers=0)
        self.assertEqual(wrapper.num_layers, 1)

    def test_num_layers_boundary_high(self):
        """Test num_layers>3 caps at 3"""
        wrapper = MultiEncodingWrapper(num_layers=10)
        self.assertEqual(wrapper.num_layers, 3)

    def test_unicode_characters(self):
        """Test encoding unicode characters"""
        wrapper = MultiEncodingWrapper(num_layers=2)
        test_data = "Hello 世界 مرحبا мир"
        encoded = wrapper.encode(test_data)
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_newlines_and_tabs(self):
        """Test encoding whitespace characters"""
        wrapper = MultiEncodingWrapper(num_layers=2)
        test_data = "line1\nline2\ttabbed"
        encoded = wrapper.encode(test_data)
        decoded = wrapper.decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_multiple_encodings_different(self):
        """Test that different random seeds produce different encodings"""
        test_data = "different test"
        wrapper1 = MultiEncodingWrapper(num_layers=2, seed=100)
        wrapper2 = MultiEncodingWrapper(num_layers=2, seed=200)

        encoded1 = wrapper1.encode(test_data)
        encoded2 = wrapper2.encode(test_data)

        # Encodings should typically be different with different seeds
        # (not guaranteed but highly probable)
        self.assertNotEqual(
            wrapper1.encoding_layers[0].layer_type,
            wrapper2.encoding_layers[0].layer_type
        )


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEncodingLayers))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiEncodingWrapper))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
