#!/usr/bin/env python3
"""
Test Suite for COM Object Polymorphic Loader
Tests polymorphic instantiation, fallback chains, and code generation
"""

import unittest
import json
from com_polymorphic_loader import (
    COMPolymorphicLoader,
    COMPolymorphicCodeGenerator,
    COMObjectType,
    COMInstantiationMethod,
    ShellCOMObject,
    WMILocatorCOMObject,
    ExcelCOMObject,
    MSXMLCOMObject
)


class TestCOMObjectImplementations(unittest.TestCase):
    """Test individual COM object implementations"""

    def test_shell_object_creation(self):
        """Test WScript.Shell COM object creation"""
        shell = ShellCOMObject()
        self.assertEqual(shell.get_progid(), "WScript.Shell")
        self.assertEqual(
            shell.get_clsid(),
            "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"
        )
        self.assertEqual(shell.get_object_type(), COMObjectType.SHELL)

    def test_shell_object_instantiation_code(self):
        """Test WScript.Shell instantiation code generation"""
        shell = ShellCOMObject()
        code = shell.get_instantiation_code()
        self.assertIn("CreateObject", code)
        self.assertIn("WScript.Shell", code)
        self.assertIn("On Error Resume Next", code)

    def test_shell_object_run_execution(self):
        """Test WScript.Shell Run method execution"""
        shell = ShellCOMObject()
        code = shell.get_execution_code("Run", "calc.exe")
        self.assertIn("Run", code)
        self.assertIn("calc.exe", code)

    def test_shell_object_remote_instantiation(self):
        """Test remote DCOM instantiation"""
        shell = ShellCOMObject(use_remote=True, remote_machine="192.168.1.100")
        code = shell.get_instantiation_code()
        self.assertIn("192.168.1.100", code)

    def test_wmi_locator_object_creation(self):
        """Test WbemScripting.SWbemLocator creation"""
        wmi = WMILocatorCOMObject()
        self.assertEqual(
            wmi.get_progid(),
            "WbemScripting.SWbemLocator"
        )
        self.assertEqual(
            wmi.get_clsid(),
            "{76A64158-CB41-11D1-8B02-00600806D9B6}"
        )
        self.assertEqual(wmi.get_object_type(), COMObjectType.WMI_LOCATOR)

    def test_wmi_locator_instantiation_code(self):
        """Test WMI Locator instantiation code"""
        wmi = WMILocatorCOMObject()
        code = wmi.get_instantiation_code()
        self.assertIn("ConnectServer", code)
        self.assertIn("root\\cimv2", code)

    def test_wmi_locator_custom_namespace(self):
        """Test WMI Locator with custom namespace"""
        wmi = WMILocatorCOMObject(namespace="root\\wmi")
        code = wmi.get_instantiation_code()
        self.assertIn("root\\wmi", code)

    def test_excel_object_creation(self):
        """Test Excel.Application object creation"""
        excel = ExcelCOMObject()
        self.assertEqual(excel.get_progid(), "Excel.Application")
        self.assertEqual(
            excel.get_clsid(),
            "{00024500-0000-0000-C000-000000000046}"
        )
        self.assertEqual(excel.get_object_type(), COMObjectType.EXCEL)

    def test_excel_versioned_progid(self):
        """Test version-specific Excel ProgID"""
        excel = ExcelCOMObject(version=16)
        self.assertEqual(excel.get_progid(), "Excel.Application.16")

    def test_msxml_object_creation(self):
        """Test MSXML2.DOMDocument object creation"""
        msxml = MSXMLCOMObject()
        self.assertIn("MSXML2.DOMDocument", msxml.get_progid())
        self.assertEqual(
            msxml.get_clsid(),
            "{F5078F32-C551-11D3-89B9-0000F81FE221}"
        )
        self.assertEqual(msxml.get_object_type(), COMObjectType.MSXML)

    def test_method_signatures(self):
        """Test method signature retrieval"""
        shell = ShellCOMObject()
        methods = shell.get_method_signature()
        self.assertIn("Run", methods)
        self.assertIn("Exec", methods)
        self.assertIn("RegRead", methods)


class TestCOMPolymorphicLoader(unittest.TestCase):
    """Test polymorphic loader functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.loader = COMPolymorphicLoader()

    def test_loader_initialization(self):
        """Test loader initialization"""
        self.assertIsNotNone(self.loader._metadata)
        self.assertIsNotNone(self.loader._fallback_chains)
        self.assertGreater(len(self.loader.list_available_objects()), 0)

    def test_load_shell_object(self):
        """Test loading shell COM object"""
        obj = self.loader.load_object(COMObjectType.SHELL)
        self.assertIsNotNone(obj)
        self.assertEqual(obj.get_progid(), "WScript.Shell")

    def test_load_wmi_object(self):
        """Test loading WMI COM object"""
        obj = self.loader.load_object(COMObjectType.WMI_LOCATOR)
        self.assertIsNotNone(obj)
        self.assertEqual(obj.get_progid(), "WbemScripting.SWbemLocator")

    def test_load_excel_object(self):
        """Test loading Excel COM object"""
        obj = self.loader.load_object(COMObjectType.EXCEL)
        self.assertIsNotNone(obj)
        self.assertEqual(obj.get_progid(), "Excel.Application")

    def test_load_msxml_object(self):
        """Test loading MSXML COM object"""
        obj = self.loader.load_object(COMObjectType.MSXML)
        self.assertIsNotNone(obj)
        self.assertIn("MSXML2.DOMDocument", obj.get_progid())

    def test_object_caching(self):
        """Test object caching in loader"""
        obj1 = self.loader.load_object(COMObjectType.SHELL)
        obj2 = self.loader.load_object(COMObjectType.SHELL)
        self.assertIs(obj1, obj2)  # Same object reference

    def test_get_object_metadata(self):
        """Test metadata retrieval"""
        metadata = self.loader.get_object_metadata(COMObjectType.SHELL)
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.object_type, COMObjectType.SHELL)
        self.assertEqual(metadata.progid, "WScript.Shell")

    def test_fallback_chain_exists(self):
        """Test fallback chain retrieval"""
        fallbacks = self.loader.get_fallback_chain(COMObjectType.SHELL)
        self.assertGreater(len(fallbacks), 0)

    def test_generate_polymorphic_code_no_fallback(self):
        """Test polymorphic code generation without fallback"""
        code = self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "Run",
            "calc.exe",
            fallback=False
        )
        self.assertIn("CreateObject", code)
        self.assertIn("WScript.Shell", code)
        self.assertIn("Run", code)
        self.assertIn("calc.exe", code)

    def test_generate_polymorphic_code_with_fallback(self):
        """Test polymorphic code generation with fallback"""
        code = self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "Run",
            "calc.exe",
            fallback=True
        )
        self.assertIn("CreateObject", code)
        self.assertIn("On Error Resume Next", code)

    def test_generate_wmi_code(self):
        """Test WMI code generation"""
        code = self.loader.generate_polymorphic_code(
            COMObjectType.WMI_LOCATOR,
            "ExecQuery",
            "SELECT * FROM Win32_Process"
        )
        self.assertIn("WbemScripting.SWbemLocator", code)
        self.assertIn("ExecQuery", code)
        self.assertIn("Win32_Process", code)

    def test_list_available_objects(self):
        """Test listing available objects"""
        available = self.loader.list_available_objects()
        self.assertIn("shell", available)
        self.assertIn("wmi_locator", available)
        self.assertIn("excel", available)
        self.assertIn("msxml", available)
        self.assertNotIn("unknown", available)

    def test_generate_all_variants(self):
        """Test generating all variants"""
        variants = self.loader.generate_all_variants()
        self.assertGreater(len(variants), 0)
        self.assertIn("shell", variants)
        self.assertIn("progid", variants["shell"])
        self.assertIn("clsid", variants["shell"])

    def test_export_to_json(self):
        """Test JSON export"""
        json_str = self.loader.export_to_json()
        data = json.loads(json_str)
        self.assertIn("available_objects", data)
        self.assertIn("variants", data)
        self.assertIn("fallback_chains", data)

    def test_polymorphic_shell_registry_operation(self):
        """Test polymorphic registry operation"""
        code = self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "RegRead",
            "HKCU\\Software\\Test"
        )
        self.assertIn("RegRead", code)
        self.assertIn("HKCU", code)


class TestCOMPolymorphicCodeGenerator(unittest.TestCase):
    """Test high-level code generator"""

    def setUp(self):
        """Set up test fixtures"""
        self.gen = COMPolymorphicCodeGenerator()

    def test_generate_command_executor(self):
        """Test command executor generation"""
        code = self.gen.generate_command_executor("powershell.exe")
        self.assertIn("powershell.exe", code)
        self.assertIn("WScript.Shell", code)

    def test_generate_wmi_query_executor(self):
        """Test WMI query executor generation"""
        code = self.gen.generate_wmi_query_executor("SELECT * FROM Win32_Process")
        self.assertIn("Win32_Process", code)
        self.assertIn("WbemScripting.SWbemLocator", code)

    def test_generate_registry_reader(self):
        """Test registry reader generation"""
        code = self.gen.generate_registry_reader("HKCU\\Software\\Test")
        self.assertIn("RegRead", code)
        self.assertIn("HKCU", code)

    def test_generate_file_operations_open(self):
        """Test file operations for opening"""
        code = self.gen.generate_file_operations("open", "C:\\test.xlsx")
        self.assertIn("Excel", code)

    def test_generate_file_operations_read(self):
        """Test file operations for reading"""
        code = self.gen.generate_file_operations("read", "C:\\test.txt")
        self.assertIn("WScript.Shell", code)

    def test_export_library_json(self):
        """Test library export as JSON"""
        json_str = self.gen.export_library("json")
        data = json.loads(json_str)
        self.assertIn("available_objects", data)


class TestPolymorphicUsagePatterns(unittest.TestCase):
    """Test real-world usage patterns"""

    def setUp(self):
        """Set up test fixtures"""
        self.loader = COMPolymorphicLoader()

    def test_multiple_object_instantiation(self):
        """Test instantiating multiple different COM objects"""
        shell = self.loader.load_object(COMObjectType.SHELL)
        wmi = self.loader.load_object(COMObjectType.WMI_LOCATOR)
        excel = self.loader.load_object(COMObjectType.EXCEL)
        msxml = self.loader.load_object(COMObjectType.MSXML)

        self.assertNotEqual(shell.get_progid(), wmi.get_progid())
        self.assertNotEqual(wmi.get_progid(), excel.get_progid())
        self.assertNotEqual(excel.get_progid(), msxml.get_progid())

    def test_same_interface_different_implementations(self):
        """Test that all objects implement same interface"""
        objects = [
            self.loader.load_object(COMObjectType.SHELL),
            self.loader.load_object(COMObjectType.WMI_LOCATOR),
            self.loader.load_object(COMObjectType.EXCEL),
            self.loader.load_object(COMObjectType.MSXML)
        ]

        for obj in objects:
            self.assertTrue(hasattr(obj, "get_progid"))
            self.assertTrue(hasattr(obj, "get_clsid"))
            self.assertTrue(hasattr(obj, "get_instantiation_code"))
            self.assertTrue(hasattr(obj, "get_execution_code"))
            self.assertTrue(hasattr(obj, "get_object_type"))
            self.assertTrue(hasattr(obj, "get_method_signature"))

    def test_method_polymorphism(self):
        """Test polymorphic method invocation"""
        shell = self.loader.load_object(COMObjectType.SHELL)
        wmi = self.loader.load_object(COMObjectType.WMI_LOCATOR)

        # Same interface, different implementations
        shell_code = shell.get_execution_code("Run", "test.exe")
        wmi_code = wmi.get_execution_code("ExecQuery", "SELECT * FROM Win32_Process")

        self.assertIn("Run", shell_code)
        self.assertIn("ExecQuery", wmi_code)
        self.assertNotIn("Run", wmi_code)
        self.assertNotIn("ExecQuery", shell_code)

    def test_fallback_chain_usage(self):
        """Test using fallback chains"""
        # Primary object fails, fallback should work
        code = self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "Run",
            "cmd.exe",
            fallback=True,
            use_error_handling=True
        )

        # Should have error handling for fallback
        self.assertIn("On Error Resume Next", code)
        self.assertIn("If IsEmpty", code)

    def test_polymorphic_code_quality(self):
        """Test generated code quality"""
        code = self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "Run",
            "test.exe"
        )

        # Check for valid VBScript structure
        self.assertIn("Dim", code)
        self.assertIn("Set", code)
        self.assertIn("CreateObject", code)
        self.assertIn("On Error", code)


class TestPolymorphicRobustness(unittest.TestCase):
    """Test robustness and edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.loader = COMPolymorphicLoader()
        self.gen = COMPolymorphicCodeGenerator()

    def test_empty_method_arguments(self):
        """Test with empty method arguments"""
        code = self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "Run"
        )
        self.assertIn("Run", code)

    def test_special_characters_in_arguments(self):
        """Test handling special characters"""
        code = self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "Run",
            "cmd.exe /c echo \"test & test\""
        )
        self.assertIn("cmd.exe", code)

    def test_multiple_method_invocations(self):
        """Test multiple different method calls"""
        code1 = self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "Run",
            "calc.exe"
        )
        code2 = self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "RegRead",
            "HKCU\\Test"
        )

        self.assertNotEqual(code1, code2)
        self.assertIn("Run", code1)
        self.assertIn("RegRead", code2)

    def test_remote_dcom_configuration(self):
        """Test remote DCOM configuration"""
        obj = self.loader.load_object(
            COMObjectType.SHELL,
            use_remote=True,
            remote_machine="192.168.1.100"
        )
        code = obj.get_instantiation_code()
        self.assertIn("192.168.1.100", code)

    def test_excel_version_specificity(self):
        """Test Excel version-specific instantiation"""
        obj = self.loader.load_object(
            COMObjectType.EXCEL,
            version=16
        )
        self.assertEqual(obj.get_progid(), "Excel.Application.16")


def run_test_suite():
    """Run complete test suite"""
    loader = unittest.TestLoader()

    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestCOMObjectImplementations))
    suite.addTests(loader.loadTestsFromTestCase(TestCOMPolymorphicLoader))
    suite.addTests(loader.loadTestsFromTestCase(TestCOMPolymorphicCodeGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestPolymorphicUsagePatterns))
    suite.addTests(loader.loadTestsFromTestCase(TestPolymorphicRobustness))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_test_suite()
    exit(0 if result.wasSuccessful() else 1)
