#!/usr/bin/env python3
"""
Base64 Fix Verification Test Suite
Tests the VBS Base64 decoder implementation with various payloads
"""

import sys
import base64
import binascii
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, '/home/user/sc-generator')

from vbs_encoder import VBSEncoder, ObfuscationConfig

class Base64VerificationTest:
    """Comprehensive test suite for Base64 encoding/decoding fix"""

    def __init__(self):
        self.encoder = VBSEncoder()
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def test_case(self, name, test_func):
        """Execute a test case and record results"""
        try:
            result = test_func()
            if result:
                self.test_results.append(f"✓ PASSED: {name}")
                self.passed += 1
            else:
                self.test_results.append(f"✗ FAILED: {name}")
                self.failed += 1
            return result
        except Exception as e:
            self.test_results.append(f"✗ ERROR: {name} - {str(e)}")
            self.failed += 1
            return False

    def verify_base64_encoding(self):
        """Test 1: Verify base64 encoding produces valid output"""
        payload = "test command"
        encoded, var_name = self.encoder.encode_string_base64(payload)

        # Expected Base64 encoding of "test command"
        expected = base64.b64encode(payload.encode()).decode()

        if encoded == expected:
            print(f"  Input: {payload}")
            print(f"  Encoded: {encoded}")
            print(f"  Expected: {expected}")
            print(f"  Variable: {var_name}")
            return True
        else:
            print(f"  MISMATCH: {encoded} != {expected}")
            return False

    def verify_vbs_decoder_generation(self):
        """Test 2: Verify VBS decoder code generation"""
        payload = "test command"
        vbs_code = self.encoder.create_base64_decoder_vbs(payload)

        required_elements = [
            "MSXML2.DOMDocument",
            "CreateObject",
            "LoadXML",
            "CDATA",
            "SelectSingleNode"
        ]

        all_present = all(elem in vbs_code for elem in required_elements)

        if all_present:
            print("  Generated VBS contains all required elements:")
            for elem in required_elements:
                print(f"    - {elem}")
            return True
        else:
            missing = [e for e in required_elements if e not in vbs_code]
            print(f"  Missing elements: {missing}")
            return False

    def verify_payload_structure(self):
        """Test 3: Verify complete payload structure"""
        payload = "test command"
        vbs_code = self.encoder.create_full_obfuscated_payload(payload, "base64")

        required_sections = [
            "Option Explicit",
            "CreateObject",
            "Run",
            "MSXML2.DOMDocument"
        ]

        all_present = all(section in vbs_code for section in required_sections)

        if all_present:
            print("  Complete payload structure verified:")
            for section in required_sections:
                print(f"    - Found: {section}")
            print(f"  Total payload length: {len(vbs_code)} characters")
            return True
        else:
            missing = [s for s in required_sections if s not in vbs_code]
            print(f"  Missing sections: {missing}")
            return False

    def verify_hex_fallback(self):
        """Test 4: Verify hex encoding fallback"""
        payload = "test command"
        hex_encoded, var_name = self.encoder.encode_string_hex(payload)

        # Verify hex encoding
        expected_hex = payload.encode().hex()

        if hex_encoded == expected_hex:
            print(f"  Input: {payload}")
            print(f"  Hex Encoded: {hex_encoded}")
            print(f"  Variable: {var_name}")
            return True
        else:
            print(f"  Hex encoding mismatch")
            return False

    def verify_hex_decoder_generation(self):
        """Test 5: Verify hex decoder VBS generation"""
        payload = "test command"
        vbs_code = self.encoder.create_hex_decoder_vbs(payload)

        required_elements = [
            "Function",
            "Chr(CLng",
            "Mid",
            "Len"
        ]

        all_present = all(elem in vbs_code for elem in required_elements)

        if all_present:
            print("  Hex decoder VBS contains all required elements:")
            for elem in required_elements:
                print(f"    - {elem}")
            return True
        else:
            missing = [e for e in required_elements if e not in vbs_code]
            print(f"  Missing elements: {missing}")
            return False

    def verify_array_concatenation(self):
        """Test 6: Verify array concatenation decoder"""
        payload = "test command"
        vbs_code = self.encoder.create_array_concatenation_decoder(payload)

        required_elements = [
            "Dim",
            "For Each",
            "Chr(CLng"
        ]

        all_present = all(elem in vbs_code for elem in required_elements)

        if all_present:
            print("  Array concatenation decoder contains required elements:")
            for elem in required_elements:
                print(f"    - {elem}")
            return True
        else:
            missing = [e for e in required_elements if e not in vbs_code]
            print(f"  Missing elements: {missing}")
            return False

    def verify_polymorphic_wrapper(self):
        """Test 7: Verify polymorphic wrapper generation"""
        payload = "test command"
        vbs_code = self.encoder.create_full_obfuscated_payload(payload, "base64")
        wrapped = self.encoder.create_polymorphic_wrapper(vbs_code)

        # Wrapped version should be longer or equal
        if len(wrapped) >= len(vbs_code) and "Dim" in wrapped:
            print(f"  Original payload length: {len(vbs_code)}")
            print(f"  Wrapped payload length: {len(wrapped)}")
            print(f"  Obfuscation level: Increased")
            return True
        else:
            print(f"  Wrapper not properly applied")
            return False

    def verify_cache_mechanism(self):
        """Test 8: Verify encoding cache works correctly"""
        payload = "test command"

        # First encoding
        encoded1, var1 = self.encoder.encode_string_base64(payload)

        # Second encoding of same payload (should use cache)
        encoded2, var2 = self.encoder.encode_string_base64(payload)

        if encoded1 == encoded2:
            print(f"  Cache hit verified")
            print(f"  Encoding 1: {encoded1}")
            print(f"  Encoding 2: {encoded2}")
            return True
        else:
            print(f"  Cache inconsistency detected")
            return False

    def verify_special_characters(self):
        """Test 9: Verify handling of special characters"""
        test_payloads = [
            "test command",
            "cmd /c echo hello",
            'powershell -Command "Write-Host test"',
            "test\nwith\nnewlines",
            "test@special$chars%"
        ]

        all_valid = True
        for payload in test_payloads:
            try:
                encoded, _ = self.encoder.encode_string_base64(payload)
                decoded = base64.b64decode(encoded).decode()

                if decoded == payload:
                    print(f"  ✓ {payload[:40]}...")
                else:
                    print(f"  ✗ Mismatch: {payload[:40]}...")
                    all_valid = False
            except Exception as e:
                print(f"  ✗ Error encoding: {payload[:40]}... - {str(e)}")
                all_valid = False

        return all_valid

    def verify_runtime_decoded_payload(self):
        """Test 10: Verify runtime-decoded payload generation"""
        payload = "test command"
        vbs_code = self.encoder.create_runtime_decoded_payload(payload, "base64")

        required_elements = [
            "Function",
            "MSXML2.DOMDocument",
            "CDATA"
        ]

        all_present = all(elem in vbs_code for elem in required_elements)

        if all_present:
            print("  Runtime decoded payload contains required elements:")
            for elem in required_elements:
                print(f"    - {elem}")
            return True
        else:
            missing = [e for e in required_elements if e not in vbs_code]
            print(f"  Missing elements: {missing}")
            return False

    def run_all_tests(self):
        """Execute all test cases"""
        print("=" * 60)
        print("Base64 Fix Verification Test Suite")
        print("=" * 60)
        print()

        print("Test 1: Base64 Encoding Verification")
        print("-" * 60)
        self.test_case("Base64 encoding produces valid output",
                      self.verify_base64_encoding)
        print()

        print("Test 2: VBS Decoder Code Generation")
        print("-" * 60)
        self.test_case("VBS decoder code generation",
                      self.verify_vbs_decoder_generation)
        print()

        print("Test 3: Complete Payload Structure")
        print("-" * 60)
        self.test_case("Complete payload structure verification",
                      self.verify_payload_structure)
        print()

        print("Test 4: Hex Encoding Fallback")
        print("-" * 60)
        self.test_case("Hex encoding fallback mechanism",
                      self.verify_hex_fallback)
        print()

        print("Test 5: Hex Decoder VBS Generation")
        print("-" * 60)
        self.test_case("Hex decoder VBS code generation",
                      self.verify_hex_decoder_generation)
        print()

        print("Test 6: Array Concatenation Decoder")
        print("-" * 60)
        self.test_case("Array concatenation decoder generation",
                      self.verify_array_concatenation)
        print()

        print("Test 7: Polymorphic Wrapper")
        print("-" * 60)
        self.test_case("Polymorphic wrapper obfuscation",
                      self.verify_polymorphic_wrapper)
        print()

        print("Test 8: Cache Mechanism")
        print("-" * 60)
        self.test_case("Encoding cache mechanism",
                      self.verify_cache_mechanism)
        print()

        print("Test 9: Special Characters Handling")
        print("-" * 60)
        self.test_case("Special characters encoding/decoding",
                      self.verify_special_characters)
        print()

        print("Test 10: Runtime Decoded Payload")
        print("-" * 60)
        self.test_case("Runtime-decoded payload generation",
                      self.verify_runtime_decoded_payload)
        print()

        # Print summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        for result in self.test_results:
            print(result)
        print()
        print(f"Total Passed: {self.passed}")
        print(f"Total Failed: {self.failed}")
        print(f"Total Tests: {self.passed + self.failed}")
        print()

        if self.failed == 0:
            print("✓ ALL TESTS PASSED")
            return True
        else:
            print(f"✗ {self.failed} TEST(S) FAILED")
            return False


def main():
    """Main test execution"""
    tester = Base64VerificationTest()
    success = tester.run_all_tests()

    # Write results to file
    output_file = Path("/tmp/claude-0/-home-user-sc-generator/cea520eb-2877-52b0-bbd4-c38bff01b8ad/scratchpad/base64_verification_results.txt")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("Base64 Fix Verification - Test Results\n")
        f.write("=" * 60 + "\n\n")

        for result in tester.test_results:
            f.write(result + "\n")

        f.write(f"\nTotal Passed: {tester.passed}\n")
        f.write(f"Total Failed: {tester.failed}\n")
        f.write(f"Total Tests: {tester.passed + tester.failed}\n")

        if tester.failed == 0:
            f.write("\n✓ ALL TESTS PASSED - Base64 Fix Verified\n")
        else:
            f.write(f"\n✗ {tester.failed} TEST(S) FAILED\n")

    print(f"\nResults written to: {output_file}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
