#!/usr/bin/env python3
"""
Edge Cases and Integration Tests for Array Encoder
Tests unusual payload scenarios, integration with decoders, and error handling
"""

import sys
import json
import binascii
import base64
import random
import string
from array_encoder import (
    ArrayEncoder, EncoderConfig, EncodingType, OutputFormat,
    ChunkingStrategy, encode_command_to_array
)


class EdgeCaseTests:
    """Edge case and integration tests"""

    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def test(self, name, test_func):
        """Execute a test"""
        try:
            result = test_func()
            status = "PASS" if result else "FAIL"
            if result:
                self.passed += 1
            else:
                self.failed += 1
            self.results.append((name, status, ""))
            print(f"{'✓' if result else '✗'} {name}")
            return result
        except Exception as e:
            self.failed += 1
            self.results.append((name, "FAIL", str(e)))
            print(f"✗ {name}: {e}")
            return False

    # ========================= Empty/Null Tests =========================
    def test_empty_string(self):
        """Test encoding empty string"""
        def run():
            config = EncoderConfig(chunk_size=16, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.generate("")
            return len(result) > 0
        return self.test("Empty String", run)

    def test_single_byte(self):
        """Test single byte encoding"""
        def run():
            config = EncoderConfig(chunk_size=8, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.encode("A")
            return result["count"] >= 1
        return self.test("Single Byte", run)

    def test_single_char_types(self):
        """Test various single character types"""
        def run():
            chars = ["\n", "\t", " ", "\\", '"', "'", "\x00"]
            for char in chars:
                try:
                    config = EncoderConfig(chunk_size=8, encoding_type=EncodingType.HEX)
                    encoder = ArrayEncoder(config)
                    result = encoder.generate(char)
                    if len(result) == 0:
                        return False
                except Exception:
                    return False
            return True
        return self.test("Single Char Types", run)

    # ========================= Large Size Tests =========================
    def test_exactly_chunk_size(self):
        """Test payload exactly matching chunk size"""
        def run():
            payload = "A" * 32
            config = EncoderConfig(chunk_size=32, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] == 1
        return self.test("Payload Exactly Chunk Size", run)

    def test_exactly_2x_chunk_size(self):
        """Test payload exactly 2x chunk size"""
        def run():
            payload = "A" * 64
            config = EncoderConfig(chunk_size=32, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] == 2
        return self.test("Payload Exactly 2x Chunk Size", run)

    def test_one_byte_over_chunk_size(self):
        """Test payload one byte over chunk size"""
        def run():
            payload = "A" * 33
            config = EncoderConfig(chunk_size=32, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] == 2
        return self.test("Payload One Byte Over Chunk Size", run)

    def test_one_byte_under_chunk_size(self):
        """Test payload one byte under chunk size"""
        def run():
            payload = "A" * 31
            config = EncoderConfig(chunk_size=32, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] == 1
        return self.test("Payload One Byte Under Chunk Size", run)

    # ========================= Special Characters Tests =========================
    def test_special_characters(self):
        """Test special characters in payload"""
        def run():
            payload = "!@#$%^&*()[]{}|;:',<>?/~`"
            config = EncoderConfig(chunk_size=16, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.generate(payload)
            return len(result) > 0
        return self.test("Special Characters", run)

    def test_whitespace_characters(self):
        """Test various whitespace characters"""
        def run():
            payload = " \t\n\r\v\f"
            config = EncoderConfig(chunk_size=8, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] >= 1
        return self.test("Whitespace Characters", run)

    def test_unicode_characters(self):
        """Test Unicode characters"""
        def run():
            payload = "你好世界🚀✓"
            config = EncoderConfig(chunk_size=16, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.generate(payload)
            return len(result) > 0
        return self.test("Unicode Characters", run)

    def test_null_bytes(self):
        """Test null bytes in payload"""
        def run():
            payload = "hello\x00world"
            config = EncoderConfig(chunk_size=8, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] >= 1
        return self.test("Null Bytes", run)

    def test_mixed_encoding_characters(self):
        """Test mix of ASCII and non-ASCII"""
        def run():
            payload = "abc123!@#你好"
            config = EncoderConfig(chunk_size=12, encoding_type=EncodingType.BASE64)
            encoder = ArrayEncoder(config)
            result = encoder.generate(payload)
            return len(result) > 0
        return self.test("Mixed Encoding Characters", run)

    # ========================= Repetitive Pattern Tests =========================
    def test_repetitive_characters(self):
        """Test highly repetitive content"""
        def run():
            payload = "A" * 10000
            config = EncoderConfig(chunk_size=64, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] > 0 and all(isinstance(c, str) for c in result["chunks"])
        return self.test("Repetitive Characters (10KB)", run)

    def test_pattern_repetition(self):
        """Test pattern repetition"""
        def run():
            payload = "ABCDEF" * 1000
            config = EncoderConfig(chunk_size=32, encoding_type=EncodingType.BASE64)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] > 0
        return self.test("Pattern Repetition", run)

    # ========================= Encoding Edge Cases =========================
    def test_base64_padding(self):
        """Test base64 encoding with various padding scenarios"""
        def run():
            payloads = ["A", "AB", "ABC", "ABCD"]
            for payload in payloads:
                config = EncoderConfig(chunk_size=8, encoding_type=EncodingType.BASE64)
                encoder = ArrayEncoder(config)
                result = encoder.generate(payload)
                if len(result) == 0:
                    return False
            return True
        return self.test("Base64 Padding Scenarios", run)

    def test_hex_encoding_all_bytes(self):
        """Test hex encoding with all possible byte values"""
        def run():
            # Create payload with all byte values 0-255
            payload = ''.join(chr(i % 256) for i in range(256))
            config = EncoderConfig(chunk_size=16, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] == 16  # 256 bytes / 16 = 16 chunks
        return self.test("Hex All Byte Values", run)

    def test_octal_encoding(self):
        """Test octal encoding"""
        def run():
            payload = "Hello World"
            config = EncoderConfig(chunk_size=8, encoding_type=EncodingType.OCTAL)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] > 0 and all(isinstance(c, str) for c in result["chunks"])
        return self.test("Octal Encoding", run)

    # ========================= Chunk Size Edge Cases =========================
    def test_very_small_chunk_size(self):
        """Test very small chunk size"""
        def run():
            payload = "Test Payload"
            config = EncoderConfig(chunk_size=1, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] == len(payload)
        return self.test("Very Small Chunk Size (1)", run)

    def test_very_large_chunk_size(self):
        """Test very large chunk size"""
        def run():
            payload = "A" * 1000
            config = EncoderConfig(chunk_size=10000, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] == 1
        return self.test("Very Large Chunk Size", run)

    def test_power_of_two_chunk_sizes(self):
        """Test power-of-two chunk sizes"""
        def run():
            payload = "A" * 1000
            for chunk_size in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]:
                config = EncoderConfig(chunk_size=chunk_size, encoding_type=EncodingType.HEX)
                encoder = ArrayEncoder(config)
                result = encoder.encode(payload)
                if result["count"] != (1000 + chunk_size - 1) // chunk_size:
                    return False
            return True
        return self.test("Power-of-Two Chunk Sizes", run)

    # ========================= Strategy Edge Cases =========================
    def test_variable_chunk_range(self):
        """Test variable chunk size ranges"""
        def run():
            payload = "A" * 1000
            config = EncoderConfig(
                chunk_size=32,
                encoding_type=EncodingType.HEX,
                chunking_strategy=ChunkingStrategy.VARIABLE_SIZE,
                min_chunk_size=1,
                max_chunk_size=1000
            )
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] > 0 and result["count"] <= len(payload)
        return self.test("Variable Chunk Range", run)

    def test_variable_chunk_min_equals_max(self):
        """Test variable chunk when min equals max"""
        def run():
            payload = "A" * 100
            config = EncoderConfig(
                chunk_size=32,
                encoding_type=EncodingType.HEX,
                chunking_strategy=ChunkingStrategy.VARIABLE_SIZE,
                min_chunk_size=10,
                max_chunk_size=10
            )
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] > 0
        return self.test("Variable Chunk Min=Max", run)

    def test_random_order_preservation(self):
        """Test random order strategy preserves all chunks"""
        def run():
            payload = "A" * 500
            config = EncoderConfig(
                chunk_size=32,
                encoding_type=EncodingType.HEX,
                chunking_strategy=ChunkingStrategy.RANDOM_ORDER
            )
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return "order" in result and len(result["order"]) == result["count"]
        return self.test("Random Order Preservation", run)

    def test_interleaved_chunk_count(self):
        """Test interleaved strategy produces correct chunks"""
        def run():
            payload = "A" * 1000
            config = EncoderConfig(
                chunk_size=32,
                encoding_type=EncodingType.HEX,
                chunking_strategy=ChunkingStrategy.INTERLEAVED
            )
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            expected = (1000 + 32 - 1) // 32
            return result["count"] == expected
        return self.test("Interleaved Chunk Count", run)

    # ========================= Output Format Edge Cases =========================
    def test_python_array_syntax(self):
        """Test Python array output is valid syntax"""
        def run():
            payload = "test"
            config = EncoderConfig(
                chunk_size=8,
                encoding_type=EncodingType.HEX,
                output_format=OutputFormat.PYTHON
            )
            encoder = ArrayEncoder(config)
            result = encoder.generate(payload)
            # Try to compile as Python code
            try:
                compile(result, '<string>', 'exec')
                return True
            except SyntaxError:
                return False
        return self.test("Python Array Syntax", run)

    def test_json_format_validity(self):
        """Test JSON output is valid JSON"""
        def run():
            payload = "test"
            config = EncoderConfig(
                chunk_size=8,
                encoding_type=EncodingType.HEX,
                output_format=OutputFormat.JSON
            )
            encoder = ArrayEncoder(config)
            result = encoder.generate(payload)
            try:
                json.loads(result)
                return True
            except json.JSONDecodeError:
                return False
        return self.test("JSON Format Validity", run)

    def test_vbs_array_syntax(self):
        """Test VBS array output structure"""
        def run():
            payload = "test"
            config = EncoderConfig(
                chunk_size=8,
                encoding_type=EncodingType.HEX,
                output_format=OutputFormat.VBS
            )
            encoder = ArrayEncoder(config)
            result = encoder.generate(payload)
            # Check for VBScript array declarations
            return "Dim " in result and "(" in result and ")" in result
        return self.test("VBS Array Syntax", run)

    def test_bash_array_syntax(self):
        """Test Bash array output structure"""
        def run():
            payload = "test"
            config = EncoderConfig(
                chunk_size=8,
                encoding_type=EncodingType.HEX,
                output_format=OutputFormat.BASH
            )
            encoder = ArrayEncoder(config)
            result = encoder.generate(payload)
            # Check for bash array syntax
            return "=(" in result and ")" in result
        return self.test("Bash Array Syntax", run)

    # ========================= Roundtrip Tests =========================
    def test_hex_roundtrip(self):
        """Test hex encode-decode roundtrip"""
        def run():
            payload = "Hello World 123!@#"
            config = EncoderConfig(chunk_size=8, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            encoded = encoder.encode(payload)

            # Decode
            decoded = ""
            for chunk in encoded["chunks"]:
                decoded += bytes.fromhex(chunk).decode('utf-8')

            return decoded == payload
        return self.test("Hex Roundtrip", run)

    def test_base64_roundtrip(self):
        """Test base64 encode-decode roundtrip"""
        def run():
            payload = "Hello World 123!@#"
            config = EncoderConfig(chunk_size=12, encoding_type=EncodingType.BASE64)
            encoder = ArrayEncoder(config)
            encoded = encoder.encode(payload)

            # Decode
            decoded = ""
            for chunk in encoded["chunks"]:
                decoded += base64.b64decode(chunk).decode('utf-8')

            return decoded == payload
        return self.test("Base64 Roundtrip", run)

    def test_binary_data_roundtrip(self):
        """Test binary data roundtrip"""
        def run():
            # Binary data with all byte values
            payload = bytes(range(256)).decode('latin-1')
            config = EncoderConfig(chunk_size=32, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            encoded = encoder.encode(payload)

            # Decode
            decoded = ""
            for chunk in encoded["chunks"]:
                decoded += bytes.fromhex(chunk).decode('latin-1')

            return decoded == payload
        return self.test("Binary Data Roundtrip", run)

    # ========================= Random Data Tests =========================
    def test_random_ascii(self):
        """Test with random ASCII data"""
        def run():
            payload = ''.join(random.choices(string.printable, k=1000))
            config = EncoderConfig(chunk_size=32, encoding_type=EncodingType.HEX)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] > 0
        return self.test("Random ASCII Data", run)

    def test_random_binary(self):
        """Test with random binary data"""
        def run():
            payload = ''.join(chr(random.randint(0, 255)) for _ in range(1000))
            config = EncoderConfig(chunk_size=32, encoding_type=EncodingType.BASE64)
            encoder = ArrayEncoder(config)
            result = encoder.encode(payload)
            return result["count"] > 0
        return self.test("Random Binary Data", run)

    # ========================= Convenience Function Tests =========================
    def test_convenience_all_encodings(self):
        """Test convenience function with all encodings"""
        def run():
            payload = "test.exe"
            for encoding in ["hex", "base64", "octal"]:
                result = encode_command_to_array(payload, encoding=encoding)
                if len(result) == 0:
                    return False
            return True
        return self.test("Convenience Function All Encodings", run)

    def test_convenience_all_formats(self):
        """Test convenience function with all output formats"""
        def run():
            payload = "test.exe"
            formats = ["python", "vbs", "js", "ps", "bash", "json", "c"]
            for fmt in formats:
                result = encode_command_to_array(payload, output_format=fmt)
                if len(result) == 0:
                    return False
            return True
        return self.test("Convenience Function All Formats", run)

    def run_all_tests(self):
        """Run all edge case and integration tests"""
        print("\n" + "=" * 80)
        print("ARRAY ENCODER: EDGE CASES & INTEGRATION TESTS")
        print("=" * 80)

        print("\n--- Empty/Null Tests ---")
        self.test_empty_string()
        self.test_single_byte()
        self.test_single_char_types()

        print("\n--- Large Size Tests ---")
        self.test_exactly_chunk_size()
        self.test_exactly_2x_chunk_size()
        self.test_one_byte_over_chunk_size()
        self.test_one_byte_under_chunk_size()

        print("\n--- Special Characters Tests ---")
        self.test_special_characters()
        self.test_whitespace_characters()
        self.test_unicode_characters()
        self.test_null_bytes()
        self.test_mixed_encoding_characters()

        print("\n--- Repetitive Pattern Tests ---")
        self.test_repetitive_characters()
        self.test_pattern_repetition()

        print("\n--- Encoding Edge Cases ---")
        self.test_base64_padding()
        self.test_hex_encoding_all_bytes()
        self.test_octal_encoding()

        print("\n--- Chunk Size Edge Cases ---")
        self.test_very_small_chunk_size()
        self.test_very_large_chunk_size()
        self.test_power_of_two_chunk_sizes()

        print("\n--- Strategy Edge Cases ---")
        self.test_variable_chunk_range()
        self.test_variable_chunk_min_equals_max()
        self.test_random_order_preservation()
        self.test_interleaved_chunk_count()

        print("\n--- Output Format Edge Cases ---")
        self.test_python_array_syntax()
        self.test_json_format_validity()
        self.test_vbs_array_syntax()
        self.test_bash_array_syntax()

        print("\n--- Roundtrip Tests ---")
        self.test_hex_roundtrip()
        self.test_base64_roundtrip()
        self.test_binary_data_roundtrip()

        print("\n--- Random Data Tests ---")
        self.test_random_ascii()
        self.test_random_binary()

        print("\n--- Convenience Function Tests ---")
        self.test_convenience_all_encodings()
        self.test_convenience_all_formats()

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        total = self.passed + self.failed
        print(f"Passed: {self.passed}/{total}")
        print(f"Failed: {self.failed}/{total}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%")
        print("=" * 80)

        return self.failed == 0


def main():
    """Main entry point"""
    tests = EdgeCaseTests()
    success = tests.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
