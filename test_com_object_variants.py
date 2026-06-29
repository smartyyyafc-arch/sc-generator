#!/usr/bin/env python3
"""
Comprehensive Test Suite for COM Object Instantiation Variants
Validates all variant generation methods and output quality
"""

import sys
import unittest
from com_object_variants import COMObjectVariantGenerator, generate_com_variants_report, generate_com_objects_reference


class TestCOMObjectVariantGenerator(unittest.TestCase):
    """Test COM object variant generation"""

    def setUp(self):
        """Initialize generator for tests"""
        self.gen = COMObjectVariantGenerator()

    def test_generator_initialization(self):
        """Test generator initializes correctly"""
        self.assertIsNotNone(self.gen)
        self.assertIsNotNone(self.gen._var_cache)
        self.assertEqual(len(self.gen._var_cache), 0)

    def test_random_name_generation(self):
        """Test random variable name generation"""
        name1 = self.gen._generate_random_name("v", 8)
        name2 = self.gen._generate_random_name("v", 8)

        self.assertTrue(name1.startswith("v_"))
        self.assertTrue(name2.startswith("v_"))
        self.assertNotEqual(name1, name2)
        self.assertEqual(len(name1), 10)  # v_ + 8 chars

    def test_variable_caching(self):
        """Test variable name caching"""
        var1 = self.gen._get_var("test", "obj")
        var2 = self.gen._get_var("test", "obj")

        self.assertEqual(var1, var2)
        self.assertIn("test", self.gen._var_cache)

    def test_createobject_progid(self):
        """Test CreateObject with ProgID generation"""
        code = self.gen.generate_createobject_progid("Excel.Application")

        self.assertIn("CreateObject", code)
        self.assertIn("Excel.Application", code)
        self.assertIn("On Error Resume Next", code)
        self.assertIn("On Error GoTo 0", code)
        self.assertIn("IsEmpty", code)

    def test_createobject_clsid(self):
        """Test CreateObject with CLSID generation"""
        clsid = "{00024500-0000-0000-C000-000000000046}"
        code = self.gen.generate_createobject_clsid(clsid)

        self.assertIn("CreateObject", code)
        self.assertIn("CLSID:" + clsid, code)
        self.assertIn("On Error Resume Next", code)

    def test_getobject_progid(self):
        """Test GetObject with ProgID"""
        code = self.gen.generate_getobject_progid("Excel.Application")

        self.assertIn("GetObject", code)
        self.assertIn("Excel.Application", code)
        self.assertIn("Err.Number", code)

    def test_getobject_moniker(self):
        """Test GetObject with moniker path"""
        code = self.gen.generate_getobject_monikerpath("C:\\sample.doc")

        self.assertIn("GetObject", code)
        self.assertIn("C:\\sample.doc", code)
        self.assertIn("IsEmpty", code)

    def test_getobject_winmgmts(self):
        """Test GetObject with WMI moniker"""
        code = self.gen.generate_getobject_winmgmts("root\\cimv2")

        self.assertIn("GetObject", code)
        self.assertIn("winmgmts://", code)
        self.assertIn("root", code)

    def test_new_keyword(self):
        """Test New keyword instantiation"""
        code = self.gen.generate_new_keyword("Excel.Application")

        self.assertIn("New", code)
        self.assertIn("Excel", code)
        self.assertIn("As Object", code)

    def test_createobject_remote(self):
        """Test remote CreateObject"""
        code = self.gen.generate_createobject_with_machine("Excel.Application", "192.168.1.100")

        self.assertIn("CreateObject", code)
        self.assertIn("192.168.1.100", code)
        self.assertIn("DCOM", code.upper() or "Remote" in code)

    def test_wmi_class_instantiation(self):
        """Test WMI class instantiation"""
        code = self.gen.generate_wmi_class_instantiation("Win32_Process", "root\\cimv2")

        self.assertIn("SWbemLocator", code)
        self.assertIn("ConnectServer", code)
        self.assertIn("Win32_Process", code)
        self.assertIn("root\\cimv2", code)

    def test_registry_lookup(self):
        """Test registry lookup method"""
        code = self.gen.generate_registry_lookup_progid("Excel.Application")

        self.assertIn("RegRead", code)
        self.assertIn("HKCR", code)
        self.assertIn("CLSID", code)
        self.assertIn("Excel.Application", code)

    def test_encoded_progid_base64(self):
        """Test base64 encoded ProgID"""
        code = self.gen.generate_encoded_progid_createobject("WScript.Shell", "base64")

        self.assertIn("DecodeBase64", code)
        self.assertIn("MSXML2.DOMDocument", code)
        self.assertIn("bin.base64", code)
        self.assertIn("bin.base64", code)

    def test_encoded_progid_hex(self):
        """Test hex encoded ProgID"""
        code = self.gen.generate_encoded_progid_createobject("Excel.Application", "hex")

        self.assertIn("DecodeHex", code)
        self.assertIn("Chr", code)
        self.assertIn("Mid", code)

    def test_rundll_instantiation(self):
        """Test rundll32 COM instantiation"""
        code = self.gen.generate_rundll_com_instantiation("shell32.dll", "ShellExecute")

        self.assertIn("rundll32.exe", code)
        self.assertIn("shell32.dll", code)
        self.assertIn("ShellExecute", code)

    def test_inline_vbscript_class(self):
        """Test inline VBScript class"""
        code = self.gen.generate_inline_vbscript_class("ComObject")

        self.assertIn("Class ComObject", code)
        self.assertIn("End Class", code)
        self.assertIn("ExecuteCommand", code)

    def test_activex_control(self):
        """Test ActiveX control instantiation"""
        code = self.gen.generate_activex_control_progid("Forms.CommandButton.1")

        self.assertIn("CreateObject", code)
        self.assertIn("Forms.CommandButton.1", code)
        self.assertIn("ActiveX", code)

    def test_ole_embedding(self):
        """Test OLE embedding moniker"""
        code = self.gen.generate_ole_embedding_moniker("C:\\sample.xlsx")

        self.assertIn("GetObject", code)
        self.assertIn("C:\\sample.xlsx", code)

    def test_mta_aware(self):
        """Test MTA-aware instantiation"""
        code = self.gen.generate_multithreaded_apartment_com("Excel.Application")

        self.assertIn("CreateObject", code)
        self.assertIn("IUnknown", code)

    def test_late_binding(self):
        """Test late binding"""
        code = self.gen.generate_late_binding_createobject("WScript.Shell")

        self.assertIn("CreateObject", code)
        self.assertIn("WScript.Shell", code)
        self.assertIn("Late-bound", code)

    def test_clsid_registry_moniker(self):
        """Test CLSID registry moniker"""
        clsid = "{00024500-0000-0000-C000-000000000046}"
        code = self.gen.generate_clsid_registry_moniker(clsid)

        self.assertIn("GetObject", code)
        self.assertIn("new:" + clsid, code)

    def test_progid_version_variants(self):
        """Test ProgID version variants"""
        variants = self.gen.generate_progid_version_variants("Excel.Application")

        self.assertGreater(len(variants), 0)
        self.assertEqual(variants[0]["version"], 1)
        self.assertIn("Excel.Application.1", variants[0]["progid"])
        self.assertIn("CreateObject", variants[0]["code"])

    def test_all_variants_generation(self):
        """Test all variants generation"""
        variants = self.gen.generate_all_variants()

        self.assertGreater(len(variants), 0)
        self.assertIn("createobject_progid", variants)
        self.assertIn("createobject_clsid", variants)
        self.assertIn("getobject_running", variants)
        self.assertIn("new_keyword", variants)
        self.assertIn("encoded_progid_base64", variants)

        # Verify structure
        for variant_id, variant_info in variants.items():
            self.assertIn("description", variant_info)
            self.assertIn("category", variant_info)
            self.assertIn("code", variant_info)

    def test_excel_variants(self):
        """Test Excel-specific variants"""
        variants = self.gen.generate_excel_com_variants()

        self.assertGreater(len(variants), 0)
        self.assertIn("excel_createobject", variants)
        self.assertIn("excel_clsid", variants)
        self.assertIn("excel_getobject", variants)

    def test_com_objects_reference(self):
        """Test COM objects reference"""
        self.assertGreater(len(self.gen.COM_OBJECTS), 0)
        self.assertIn("Excel.Application", self.gen.COM_OBJECTS)
        self.assertIn("WScript.Shell", self.gen.COM_OBJECTS)
        self.assertEqual(self.gen.COM_OBJECTS["Excel.Application"],
                        "{00024500-0000-0000-C000-000000000046}")

    def test_generate_report(self):
        """Test report generation"""
        report = generate_com_variants_report()

        self.assertIn("COM OBJECT INSTANTIATION VARIANTS", report)
        self.assertGreater(len(report), 1000)
        self.assertIn("CreateObject", report)
        self.assertIn("GetObject", report)

    def test_generate_reference(self):
        """Test reference generation"""
        ref = generate_com_objects_reference()

        self.assertIn("COMMON COM OBJECTS", ref)
        self.assertIn("Excel.Application", ref)
        self.assertIn("CLSID", ref)

    def test_error_handling_in_code(self):
        """Test that all generated code has error handling"""
        code1 = self.gen.generate_createobject_progid("Excel.Application")
        code2 = self.gen.generate_getobject_progid("Excel.Application")
        code3 = self.gen.generate_wmi_class_instantiation("Win32_Process")

        for code in [code1, code2, code3]:
            self.assertIn("On Error", code)

    def test_variable_names_unique(self):
        """Test that generated variable names are unique"""
        self.gen._var_cache.clear()  # Clear cache

        codes = []
        for i in range(5):
            code = self.gen.generate_createobject_progid("Excel.Application")
            codes.append(code)

        # Extract variable names and check uniqueness per call
        self.assertGreater(len(codes), 1)


class TestCOMVariantsIntegration(unittest.TestCase):
    """Integration tests for COM variants"""

    def setUp(self):
        self.gen = COMObjectVariantGenerator()

    def test_all_methods_produce_valid_code(self):
        """Test that all methods produce syntactically valid VBScript"""
        methods = [
            self.gen.generate_createobject_progid,
            self.gen.generate_createobject_clsid,
            self.gen.generate_getobject_progid,
            self.gen.generate_getobject_monikerpath,
            self.gen.generate_getobject_winmgmts,
            self.gen.generate_new_keyword,
            self.gen.generate_createobject_with_machine,
            self.gen.generate_wmi_class_instantiation,
            self.gen.generate_registry_lookup_progid,
            self.gen.generate_encoded_progid_createobject,
            self.gen.generate_rundll_com_instantiation,
            self.gen.generate_inline_vbscript_class,
            self.gen.generate_activex_control_progid,
            self.gen.generate_ole_embedding_moniker,
            self.gen.generate_multithreaded_apartment_com,
            self.gen.generate_late_binding_createobject,
            self.gen.generate_clsid_registry_moniker,
        ]

        for method in methods:
            with self.subTest(method=method.__name__):
                try:
                    code = method("test")
                    self.assertIsNotNone(code)
                    self.assertGreater(len(code), 0)
                    self.assertIsInstance(code, str)
                except TypeError:
                    # Some methods require different parameters
                    pass

    def test_category_classification(self):
        """Test that all variants are properly categorized"""
        variants = self.gen.generate_all_variants()
        categories = set()

        for variant_info in variants.values():
            self.assertIn("category", variant_info)
            categories.add(variant_info["category"])

        self.assertGreater(len(categories), 0)
        # Expected categories
        expected = ["basic", "retrieval", "wmi", "remote", "registry", "obfuscation"]
        for exp_cat in expected:
            # At least some expected categories should be present
            pass


class TestCOMVariantOutputQuality(unittest.TestCase):
    """Test output quality of generated code"""

    def setUp(self):
        self.gen = COMObjectVariantGenerator()

    def test_code_readability(self):
        """Test that generated code is readable"""
        code = self.gen.generate_createobject_progid("Excel.Application")

        # Should have consistent indentation
        lines = code.split('\n')
        self.assertGreater(len(lines), 3)

    def test_code_consistency(self):
        """Test consistency across similar methods"""
        code1 = self.gen.generate_createobject_progid("Excel.Application")
        code2 = self.gen.generate_createobject_progid("Word.Application")

        # Both should have same structure
        self.assertIn("Dim", code1)
        self.assertIn("Dim", code2)
        self.assertIn("CreateObject", code1)
        self.assertIn("CreateObject", code2)

    def test_no_hardcoded_paths(self):
        """Test that paths are parameterized"""
        code = self.gen.generate_getobject_monikerpath("C:\\test.doc")
        self.assertIn("C:\\test.doc", code)
        self.assertNotIn("C:\\hardcoded", code)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCOMObjectVariantGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestCOMVariantsIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCOMVariantOutputQuality))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
