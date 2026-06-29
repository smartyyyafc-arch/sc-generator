#!/usr/bin/env python3
"""
Test suite for COM CLSID Runtime Resolver
Tests all resolution methods and obfuscation techniques
"""

import unittest
import json
import re
from com_clsid_resolver import (
    CLSIDResolutionMethod,
    CLSIDObfuscationType,
    ResolutionContext,
    RegistryProgIDResolver,
    WMIRegistryResolver,
    EncodedLiteralResolver,
    HashBasedResolver,
    HybridCLSIDResolver,
    CLSIDResolverFactory,
    CLSIDDatabase,
    RuntimeCLSIDResolver,
    generate_clsid_resolver_package,
)


class TestRegistryProgIDResolver(unittest.TestCase):
    """Tests for registry-based ProgID to CLSID resolution"""

    def setUp(self):
        self.resolver = RegistryProgIDResolver()
        self.context = ResolutionContext(
            target_progid="WScript.Shell",
            target_clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"
        )

    def test_resolver_instantiation(self):
        """Test resolver can be instantiated"""
        self.assertIsNotNone(self.resolver)

    def test_resolver_method(self):
        """Test resolver returns correct method"""
        method = self.resolver.get_resolution_method()
        self.assertEqual(method, CLSIDResolutionMethod.REGISTRY_PROGID)

    def test_generates_vbscript_code(self):
        """Test generates valid VBScript code"""
        code = self.resolver.generate_resolution_code(self.context)
        self.assertIsInstance(code, str)
        self.assertIn("WScript.Shell", code)
        self.assertIn("RegRead", code)
        self.assertIn("HKCR", code)
        self.assertIn("CLSID", code)

    def test_code_contains_error_handling(self):
        """Test generated code has error handling"""
        code = self.resolver.generate_resolution_code(self.context)
        self.assertIn("On Error Resume Next", code)
        self.assertIn("On Error GoTo 0", code)

    def test_code_uses_random_variables(self):
        """Test generated code uses random variable names"""
        code1 = self.resolver.generate_resolution_code(self.context)
        code2 = self.resolver.generate_resolution_code(self.context)
        # Variables should be different between calls
        self.assertNotEqual(code1, code2)


class TestWMIRegistryResolver(unittest.TestCase):
    """Tests for WMI-based CLSID resolution"""

    def setUp(self):
        self.resolver = WMIRegistryResolver()
        self.context = ResolutionContext(
            target_progid="WbemScripting.SWbemLocator",
            target_clsid="{76A64158-CB41-11D1-8B02-00600806D9B6}"
        )

    def test_resolver_instantiation(self):
        """Test WMI resolver can be instantiated"""
        self.assertIsNotNone(self.resolver)

    def test_resolver_method(self):
        """Test resolver returns correct method"""
        method = self.resolver.get_resolution_method()
        self.assertEqual(method, CLSIDResolutionMethod.WMI_CLASS)

    def test_generates_wmi_code(self):
        """Test generates WMI StdRegProv code"""
        code = self.resolver.generate_resolution_code(self.context)
        self.assertIsInstance(code, str)
        self.assertIn("SWbemLocator", code)
        self.assertIn("StdRegProv", code)
        self.assertIn("GetStringValue", code)

    def test_code_has_registry_constants(self):
        """Test code uses WMI registry constants"""
        code = self.resolver.generate_resolution_code(self.context)
        # HKEY_LOCAL_MACHINE = 2147483648
        self.assertIn("2147483648", code)

    def test_code_connects_to_registry(self):
        """Test code connects to registry service"""
        code = self.resolver.generate_resolution_code(self.context)
        self.assertIn("ConnectToRegistry", code)
        self.assertIn("root", code)


class TestEncodedLiteralResolver(unittest.TestCase):
    """Tests for encoded CLSID literal resolution"""

    def setUp(self):
        self.context = ResolutionContext(
            target_progid="WScript.Shell",
            target_clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"
        )

    def test_xor_encoding(self):
        """Test XOR encoding and decoding"""
        resolver = EncodedLiteralResolver(CLSIDObfuscationType.XOR)
        encoded, decoder = resolver.generate_encoded_clsid(
            self.context.target_clsid,
            CLSIDObfuscationType.XOR
        )
        self.assertIsInstance(encoded, str)
        self.assertIsInstance(decoder, str)
        self.assertIn("DecodeXOR", decoder)
        self.assertIn("Xor", decoder)

    def test_base64_encoding(self):
        """Test Base64 encoding"""
        resolver = EncodedLiteralResolver(CLSIDObfuscationType.BASE64)
        encoded, decoder = resolver.generate_encoded_clsid(
            self.context.target_clsid,
            CLSIDObfuscationType.BASE64
        )
        self.assertIsInstance(encoded, str)
        self.assertIn("DecodeBase64", decoder)
        self.assertIn("MSXML2.DOMDocument", decoder)

    def test_hex_encoding(self):
        """Test Hex encoding"""
        resolver = EncodedLiteralResolver(CLSIDObfuscationType.HEX)
        encoded, decoder = resolver.generate_encoded_clsid(
            self.context.target_clsid,
            CLSIDObfuscationType.HEX
        )
        self.assertIsInstance(encoded, str)
        self.assertIn("DecodeHex", decoder)

    def test_rot13_encoding(self):
        """Test ROT13 encoding"""
        resolver = EncodedLiteralResolver(CLSIDObfuscationType.ROT13)
        encoded, decoder = resolver.generate_encoded_clsid(
            self.context.target_clsid,
            CLSIDObfuscationType.ROT13
        )
        self.assertIsInstance(encoded, str)
        self.assertIn("DecodeRot13", decoder)

    def test_hybrid_encoding(self):
        """Test hybrid encoding combines multiple techniques"""
        resolver = EncodedLiteralResolver(CLSIDObfuscationType.HYBRID)
        encoded, decoder = resolver.generate_encoded_clsid(
            self.context.target_clsid,
            CLSIDObfuscationType.HYBRID
        )
        self.assertIsInstance(encoded, str)
        self.assertIn("Function", decoder)

    def test_encoded_resolution_code(self):
        """Test generated resolution code with encoding"""
        resolver = EncodedLiteralResolver(CLSIDObfuscationType.XOR)
        # Need to provide target CLSID for encoding
        context = ResolutionContext(
            target_progid="WScript.Shell",
            target_clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}",
            obfuscation=CLSIDObfuscationType.XOR
        )
        code = resolver.generate_resolution_code(context)
        self.assertIsInstance(code, str)
        self.assertIn("Function", code)
        self.assertIn("Decode", code)

    def test_all_encodings_produce_different_output(self):
        """Test different encodings produce different results"""
        clsid = "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"
        resolver = EncodedLiteralResolver()

        xor_encoded, _ = resolver.generate_encoded_clsid(clsid, CLSIDObfuscationType.XOR)
        b64_encoded, _ = resolver.generate_encoded_clsid(clsid, CLSIDObfuscationType.BASE64)
        hex_encoded, _ = resolver.generate_encoded_clsid(clsid, CLSIDObfuscationType.HEX)

        # All should be different
        self.assertNotEqual(xor_encoded, b64_encoded)
        self.assertNotEqual(xor_encoded, hex_encoded)
        self.assertNotEqual(b64_encoded, hex_encoded)


class TestHashBasedResolver(unittest.TestCase):
    """Tests for hash-based CLSID lookup"""

    def setUp(self):
        self.resolver = HashBasedResolver()
        self.resolver.add_mapping("WScript.Shell", "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}")
        self.context = ResolutionContext(
            target_progid="WScript.Shell"
        )

    def test_resolver_instantiation(self):
        """Test hash resolver can be instantiated"""
        self.assertIsNotNone(self.resolver)

    def test_add_mapping(self):
        """Test mappings can be added"""
        self.assertEqual(len(self.resolver.hash_table), 1)

    def test_resolver_method(self):
        """Test resolver returns correct method"""
        method = self.resolver.get_resolution_method()
        self.assertEqual(method, CLSIDResolutionMethod.HASH_LOOKUP)

    def test_generates_hash_table_code(self):
        """Test generates code with hash table"""
        code = self.resolver.generate_resolution_code(self.context)
        self.assertIsInstance(code, str)
        self.assertIn("hashTable", code)
        self.assertIn("CreateObject", code)
        self.assertIn("Scripting.Dictionary", code)

    def test_hash_table_lookup_logic(self):
        """Test generated code includes lookup logic"""
        code = self.resolver.generate_resolution_code(self.context)
        self.assertIn("Exists", code)
        self.assertIn("Add", code)


class TestHybridCLSIDResolver(unittest.TestCase):
    """Tests for hybrid CLSID resolution with fallback chains"""

    def setUp(self):
        self.resolver = HybridCLSIDResolver()
        self.resolver.add_resolver(RegistryProgIDResolver())
        self.resolver.add_resolver(WMIRegistryResolver())
        self.context = ResolutionContext(
            target_progid="WScript.Shell",
            target_clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"
        )

    def test_hybrid_instantiation(self):
        """Test hybrid resolver can be instantiated"""
        self.assertIsNotNone(self.resolver)

    def test_add_resolver(self):
        """Test resolvers can be added"""
        self.assertEqual(len(self.resolver.resolvers), 2)

    def test_resolver_method(self):
        """Test resolver returns correct method"""
        method = self.resolver.get_resolution_method()
        self.assertEqual(method, CLSIDResolutionMethod.HYBRID_RESOLUTION)

    def test_generates_fallback_chain(self):
        """Test generates code with multiple resolution methods"""
        code = self.resolver.generate_resolution_code(self.context)
        self.assertIsInstance(code, str)
        self.assertIn("RegRead", code)  # From registry resolver
        self.assertIn("StdRegProv", code)  # From WMI resolver
        self.assertIn("If Len", code)  # Fallback logic

    def test_fallback_order(self):
        """Test fallback chain tries resolvers in order"""
        code = self.resolver.generate_resolution_code(self.context)
        reg_pos = code.find("RegRead")
        wmi_pos = code.find("StdRegProv")
        # Registry resolver should come before WMI in code
        self.assertLess(reg_pos, wmi_pos)


class TestCLSIDResolverFactory(unittest.TestCase):
    """Tests for CLSID resolver factory"""

    def test_create_registry_resolver(self):
        """Test factory creates registry resolver"""
        resolver = CLSIDResolverFactory.create_resolver(
            CLSIDResolutionMethod.REGISTRY_PROGID
        )
        self.assertIsInstance(resolver, RegistryProgIDResolver)

    def test_create_wmi_resolver(self):
        """Test factory creates WMI resolver"""
        resolver = CLSIDResolverFactory.create_resolver(
            CLSIDResolutionMethod.WMI_CLASS
        )
        self.assertIsInstance(resolver, WMIRegistryResolver)

    def test_create_encoded_resolver(self):
        """Test factory creates encoded resolver"""
        resolver = CLSIDResolverFactory.create_resolver(
            CLSIDResolutionMethod.ENCODED_LITERAL
        )
        self.assertIsInstance(resolver, EncodedLiteralResolver)

    def test_create_hash_resolver(self):
        """Test factory creates hash resolver"""
        resolver = CLSIDResolverFactory.create_resolver(
            CLSIDResolutionMethod.HASH_LOOKUP
        )
        self.assertIsInstance(resolver, HashBasedResolver)

    def test_create_hybrid_resolver(self):
        """Test factory creates hybrid resolver"""
        methods = [
            CLSIDResolutionMethod.REGISTRY_PROGID,
            CLSIDResolutionMethod.WMI_CLASS,
        ]
        resolver = CLSIDResolverFactory.create_hybrid_resolver(methods)
        self.assertIsInstance(resolver, HybridCLSIDResolver)
        self.assertEqual(len(resolver.resolvers), 2)

    def test_invalid_method_raises_error(self):
        """Test factory raises error for unknown method"""
        with self.assertRaises(ValueError):
            CLSIDResolverFactory.create_resolver("invalid_method")


class TestCLSIDDatabase(unittest.TestCase):
    """Tests for CLSID database"""

    def test_database_contains_known_clsids(self):
        """Test database has known CLSID entries"""
        metadata = CLSIDDatabase.get_metadata("WScript.Shell")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.progid, "WScript.Shell")
        self.assertIn("F935DC22", metadata.clsid)

    def test_get_clsid_by_progid(self):
        """Test retrieving CLSID by ProgID"""
        clsid = CLSIDDatabase.get_clsid("Shell.Application")
        self.assertIsNotNone(clsid)
        self.assertIn("13709620", clsid)

    def test_get_nonexistent_progid(self):
        """Test retrieving nonexistent ProgID returns None"""
        result = CLSIDDatabase.get_metadata("Nonexistent.Object")
        self.assertIsNone(result)

    def test_list_all_clsids(self):
        """Test listing all CLSIDs"""
        clsids = CLSIDDatabase.list_all()
        self.assertGreater(len(clsids), 0)
        self.assertGreater(len(clsids), 5)  # Should have many entries

    def test_metadata_contains_required_fields(self):
        """Test metadata has all required fields"""
        metadata = CLSIDDatabase.get_metadata("Excel.Application")
        self.assertIsNotNone(metadata.progid)
        self.assertIsNotNone(metadata.clsid)
        self.assertIsNotNone(metadata.description)
        self.assertIsNotNone(metadata.category)

    def test_category_classification(self):
        """Test objects are properly categorized"""
        office_objects = [m for m in CLSIDDatabase.list_all() if m.category == "office"]
        self.assertGreater(len(office_objects), 0)


class TestRuntimeCLSIDResolver(unittest.TestCase):
    """Tests for main runtime CLSID resolver"""

    def setUp(self):
        self.resolver = RuntimeCLSIDResolver()

    def test_resolver_instantiation(self):
        """Test runtime resolver can be instantiated"""
        self.assertIsNotNone(self.resolver)

    def test_resolve_from_database(self):
        """Test resolving from database"""
        clsid = self.resolver.resolve("WScript.Shell")
        self.assertIsNotNone(clsid)
        self.assertIn("F935DC22", clsid)

    def test_caching(self):
        """Test results are cached"""
        progid = "Shell.Application"
        clsid1 = self.resolver.resolve(progid)
        clsid2 = self.resolver.resolve(progid)
        self.assertEqual(clsid1, clsid2)
        self.assertIn(progid, self.resolver.cache)

    def test_cache_bypass(self):
        """Test cache can be bypassed"""
        progid = "Excel.Application"
        self.resolver.resolve(progid)
        # Clear cache manually to force re-resolution
        self.resolver.cache.clear()
        self.assertEqual(len(self.resolver.cache), 0)

    def test_set_resolution_strategy(self):
        """Test resolution strategy can be set"""
        strategy = RegistryProgIDResolver()
        self.resolver.set_resolution_strategy(strategy)
        self.assertEqual(self.resolver.resolution_strategy, strategy)

    def test_set_obfuscation(self):
        """Test obfuscation type can be set"""
        self.resolver.set_obfuscation(CLSIDObfuscationType.XOR)
        self.assertEqual(self.resolver.obfuscation, CLSIDObfuscationType.XOR)

    def test_generate_resolution_script(self):
        """Test generating resolution script"""
        script = self.resolver.generate_resolution_script("WScript.Shell")
        self.assertIsInstance(script, str)
        self.assertGreater(len(script), 0)

    def test_generate_com_instantiation_with_resolution(self):
        """Test generating COM instantiation with runtime resolution"""
        script = self.resolver.generate_com_instantiation_script(
            "WScript.Shell",
            use_runtime_resolution=True
        )
        self.assertIsInstance(script, str)
        self.assertIn("CreateObject", script)
        self.assertIn("CLSID", script)

    def test_generate_com_instantiation_without_resolution(self):
        """Test generating COM instantiation without runtime resolution"""
        script = self.resolver.generate_com_instantiation_script(
            "WScript.Shell",
            use_runtime_resolution=False
        )
        self.assertIsInstance(script, str)
        self.assertIn("CreateObject", script)

    def test_script_contains_error_handling(self):
        """Test generated scripts have error handling"""
        script = self.resolver.generate_com_instantiation_script("Shell.Application")
        self.assertIn("On Error", script)


class TestPackageGeneration(unittest.TestCase):
    """Tests for complete resolver package generation"""

    def test_generate_package(self):
        """Test generating complete resolver package"""
        package = generate_clsid_resolver_package()
        self.assertIsInstance(package, dict)
        self.assertGreater(len(package), 0)

    def test_package_contains_expected_components(self):
        """Test package contains all expected components"""
        package = generate_clsid_resolver_package()
        expected = [
            "registry_resolver.vbs",
            "wmi_resolver.vbs",
            "encoded_resolver.vbs",
            "hybrid_resolver.vbs",
            "runtime_resolver.vbs",
            "clsid_database.json",
        ]
        for component in expected:
            self.assertIn(component, package)

    def test_vbs_components_are_valid_code(self):
        """Test VBS components contain valid code"""
        package = generate_clsid_resolver_package()
        vbs_files = [f for f in package.keys() if f.endswith(".vbs")]
        for vbs_file in vbs_files:
            code = package[vbs_file]
            self.assertIsInstance(code, str)
            self.assertGreater(len(code), 50)  # Non-trivial code
            self.assertIn("Dim", code)  # Contains variable declaration

    def test_json_database_is_valid(self):
        """Test JSON database is valid and parseable"""
        package = generate_clsid_resolver_package()
        db_json = package["clsid_database.json"]
        data = json.loads(db_json)
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 0)
        # Check structure
        for progid, entry in data.items():
            self.assertIn("clsid", entry)
            self.assertIn("description", entry)
            self.assertIn("category", entry)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components"""

    def test_complete_workflow_registry_resolution(self):
        """Test complete workflow with registry resolution"""
        resolver = CLSIDResolverFactory.create_resolver(
            CLSIDResolutionMethod.REGISTRY_PROGID
        )
        context = ResolutionContext(
            target_progid="WScript.Shell",
            target_clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"
        )
        code = resolver.generate_resolution_code(context)
        self.assertIsInstance(code, str)
        self.assertIn("RegRead", code)

    def test_complete_workflow_with_obfuscation(self):
        """Test complete workflow with obfuscation"""
        runtime = RuntimeCLSIDResolver()
        runtime.set_obfuscation(CLSIDObfuscationType.XOR)
        # Set encoded resolution strategy
        encoded_resolver = EncodedLiteralResolver(CLSIDObfuscationType.XOR)
        runtime.set_resolution_strategy(encoded_resolver)
        script = runtime.generate_com_instantiation_script("Excel.Application")
        self.assertIsInstance(script, str)
        self.assertIn("CreateObject", script)  # Should contain COM instantiation

    def test_hybrid_resolution_with_all_methods(self):
        """Test hybrid resolution with all available methods"""
        methods = [
            CLSIDResolutionMethod.REGISTRY_PROGID,
            CLSIDResolutionMethod.WMI_CLASS,
        ]
        hybrid = CLSIDResolverFactory.create_hybrid_resolver(methods)
        context = ResolutionContext(
            target_progid="WbemScripting.SWbemLocator"
        )
        code = hybrid.generate_resolution_code(context)
        self.assertIn("RegRead", code)
        self.assertIn("StdRegProv", code)

    def test_multiple_clsid_resolutions(self):
        """Test resolving multiple CLSIDs"""
        resolver = RuntimeCLSIDResolver()
        progids = [
            "WScript.Shell",
            "Shell.Application",
            "Excel.Application",
            "MSXML2.DOMDocument",
        ]
        results = {}
        for progid in progids:
            clsid = resolver.resolve(progid)
            self.assertIsNotNone(clsid)
            results[progid] = clsid

        # All should be different
        clsids = list(results.values())
        self.assertEqual(len(clsids), len(set(clsids)))

    def test_encoding_variations(self):
        """Test different encoding strategies"""
        clsid = "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"
        encodings = [
            CLSIDObfuscationType.XOR,
            CLSIDObfuscationType.BASE64,
            CLSIDObfuscationType.HEX,
            CLSIDObfuscationType.ROT13,
        ]
        encoded_results = {}
        for encoding in encodings:
            resolver = EncodedLiteralResolver(encoding)
            encoded, _ = resolver.generate_encoded_clsid(clsid, encoding)
            encoded_results[encoding.value] = encoded

        # All encodings should produce different outputs
        encoded_values = list(encoded_results.values())
        self.assertEqual(len(encoded_values), len(set(encoded_values)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
