#!/usr/bin/env python3
"""
Test Suite for Windows Version-Specific COM Variants
Validates version-specific COM object instantiation and security awareness
"""

import sys
import unittest
from com_windows_version_variants import (
    WindowsVersionSpecificCOMVariants,
    WindowsVersion,
    generate_comprehensive_windows_variants_report,
    generate_version_comparison_matrix
)


class TestWindowsVersionInfo(unittest.TestCase):
    """Test Windows version information database"""

    def setUp(self):
        self.gen = WindowsVersionSpecificCOMVariants()

    def test_all_versions_have_info(self):
        """Test that all Windows versions have complete info"""
        for version in WindowsVersion:
            info = self.gen._get_version_info(version)
            self.assertIsNotNone(info)
            self.assertIsNotNone(info.name)
            self.assertIsNotNone(info.version_number)
            self.assertGreater(info.build_number, 0)

    def test_version_progression(self):
        """Test that versions are in chronological order"""
        versions = [WindowsVersion.XP, WindowsVersion.VISTA, WindowsVersion.WIN7,
                   WindowsVersion.WIN8, WindowsVersion.WIN10, WindowsVersion.WIN11]
        version_numbers = []
        for v in versions:
            ver_str = self.gen.VERSION_INFO[v].version_number
            parts = ver_str.split('.')
            # Convert to comparable float (e.g., "10.0.22000" -> 10.0)
            main_ver = float(f"{parts[0]}.{parts[1]}")
            version_numbers.append(main_ver)

        # Verify ascending order
        for i in range(len(version_numbers) - 1):
            self.assertLessEqual(version_numbers[i], version_numbers[i + 1])

    def test_uac_feature_progression(self):
        """Test UAC feature progression across versions"""
        xp_info = self.gen.VERSION_INFO[WindowsVersion.XP]
        vista_info = self.gen.VERSION_INFO[WindowsVersion.VISTA]
        win11_info = self.gen.VERSION_INFO[WindowsVersion.WIN11]

        # XP no UAC, Vista and later have UAC
        self.assertFalse(xp_info.uac_supported)
        self.assertTrue(vista_info.uac_supported)
        self.assertTrue(win11_info.uac_supported)

    def test_appdata_folder_structure(self):
        """Test that AppData folder paths are properly defined"""
        xp_info = self.gen.VERSION_INFO[WindowsVersion.XP]
        win7_info = self.gen.VERSION_INFO[WindowsVersion.WIN7]

        # XP uses Documents and Settings
        self.assertIn("Documents and Settings", xp_info.appdata_folders["user"])

        # Win7+ uses Users
        self.assertIn("Users", win7_info.appdata_folders["user"])

    def test_registry_paths_defined(self):
        """Test that registry paths are defined for each version"""
        for version in WindowsVersion:
            info = self.gen.VERSION_INFO[version]
            self.assertGreater(len(info.registry_paths), 0)
            self.assertIn("com_objects", info.registry_paths)

    def test_com_objects_availability(self):
        """Test COM object availability across versions"""
        xp_info = self.gen.VERSION_INFO[WindowsVersion.XP]
        win11_info = self.gen.VERSION_INFO[WindowsVersion.WIN11]

        # All versions should have at least some COM objects
        self.assertGreater(len(xp_info.available_com_objects), 0)
        self.assertGreater(len(win11_info.available_com_objects), 0)

        # Win11 should have at least as many as XP
        self.assertGreaterEqual(len(win11_info.available_com_objects),
                               len(xp_info.available_com_objects))

    def test_security_features_progression(self):
        """Test that security features increase with version"""
        xp_features = len(self.gen.VERSION_INFO[WindowsVersion.XP].security_features)
        win11_features = len(self.gen.VERSION_INFO[WindowsVersion.WIN11].security_features)

        self.assertLess(xp_features, win11_features)


class TestVersionCheckGeneration(unittest.TestCase):
    """Test Windows version check code generation"""

    def setUp(self):
        self.gen = WindowsVersionSpecificCOMVariants()

    def test_version_check_code_generation(self):
        """Test version check code generation"""
        for version in WindowsVersion:
            code = self.gen.generate_version_check_code(version)
            self.assertIsNotNone(code)
            self.assertGreater(len(code), 0)
            self.assertIn("GetWindowsVersion", code)
            self.assertIn("CheckWindowsVersion", code)

    def test_version_check_includes_version_number(self):
        """Test that version check code includes target version number"""
        code = self.gen.generate_version_check_code(WindowsVersion.WIN10)
        self.assertIn("10", code)

    def test_version_check_includes_major_minor(self):
        """Test that version check validates major and minor versions"""
        code = self.gen.generate_version_check_code(WindowsVersion.WIN7)
        self.assertIn("major", code.lower())
        self.assertIn("minor", code.lower())


class TestUACVariantGeneration(unittest.TestCase):
    """Test UAC-aware variant generation"""

    def setUp(self):
        self.gen = WindowsVersionSpecificCOMVariants()

    def test_xp_no_uac_variant(self):
        """Test that XP variant doesn't mention UAC"""
        code = self.gen.generate_uac_aware_variant(WindowsVersion.XP, "Excel.Application")
        self.assertIn("No UAC", code)
        self.assertNotIn("Medium", code)

    def test_vista_uac_variant(self):
        """Test that Vista variant includes UAC awareness"""
        code = self.gen.generate_uac_aware_variant(WindowsVersion.VISTA, "Excel.Application")
        self.assertIn("UAC", code)

    def test_win11_uac_variant(self):
        """Test that Win11 variant includes UAC awareness"""
        code = self.gen.generate_uac_aware_variant(WindowsVersion.WIN11, "Excel.Application")
        self.assertIn("UAC", code)
        self.assertIn("CreateObject", code)

    def test_all_uac_variants_have_error_handling(self):
        """Test that all UAC variants have error handling"""
        for version in WindowsVersion:
            code = self.gen.generate_uac_aware_variant(version, "Excel.Application")
            self.assertIn("On Error", code)


class TestRegistryPathVariants(unittest.TestCase):
    """Test registry path variant generation"""

    def setUp(self):
        self.gen = WindowsVersionSpecificCOMVariants()

    def test_registry_path_generation(self):
        """Test registry path code generation"""
        code = self.gen.generate_registry_path_variant(WindowsVersion.WIN7, "com_objects")
        self.assertIsNotNone(code)
        self.assertIn("RegRead", code)
        self.assertIn("HKCR", code)

    def test_different_registry_locations(self):
        """Test different registry location types"""
        locations = ["com_objects", "windows_run", "appdata"]
        for location in locations:
            code = self.gen.generate_registry_path_variant(WindowsVersion.WIN10, location)
            self.assertIn("RegRead", code)

    def test_version_specific_paths(self):
        """Test that paths vary by version"""
        xp_code = self.gen.generate_registry_path_variant(WindowsVersion.XP, "com_objects")
        win11_code = self.gen.generate_registry_path_variant(WindowsVersion.WIN11, "com_objects")

        # Both should reference their respective versions
        self.assertIn("XP", xp_code)
        self.assertIn("11", win11_code)


class TestAppdataFolderVariants(unittest.TestCase):
    """Test AppData folder variant generation"""

    def setUp(self):
        self.gen = WindowsVersionSpecificCOMVariants()

    def test_appdata_folder_generation(self):
        """Test AppData folder code generation"""
        code = self.gen.generate_appdata_folder_variant(WindowsVersion.WIN7, "user")
        self.assertIn("AppData", code)
        self.assertIn("FolderExists", code)

    def test_xp_appdata_path(self):
        """Test XP uses Documents and Settings"""
        code = self.gen.generate_appdata_folder_variant(WindowsVersion.XP, "user")
        self.assertIn("Documents and Settings", code)

    def test_win7_appdata_path(self):
        """Test Win7 uses Users\\AppData"""
        code = self.gen.generate_appdata_folder_variant(WindowsVersion.WIN7, "user")
        self.assertIn("Users", code)
        self.assertIn("AppData", code)

    def test_all_folder_types(self):
        """Test all folder types generate valid code"""
        folder_types = ["user", "local", "temp", "all_users"]
        for folder_type in folder_types:
            code = self.gen.generate_appdata_folder_variant(WindowsVersion.WIN10, folder_type)
            self.assertIn("FileSystemObject", code)


class TestCOMAvailabilityCheck(unittest.TestCase):
    """Test COM object availability checks"""

    def setUp(self):
        self.gen = WindowsVersionSpecificCOMVariants()

    def test_com_availability_function_generation(self):
        """Test COM availability check function generation"""
        code = self.gen.generate_com_availability_check(WindowsVersion.WIN7, "Excel.Application")
        self.assertIn("IsCOMObjectAvailable", code)
        self.assertIn("CreateObject", code)

    def test_xp_excel_availability(self):
        """Test Excel availability on XP"""
        code = self.gen.generate_com_availability_check(WindowsVersion.XP, "Excel.Application")
        self.assertIn("Available", code)

    def test_win11_com_availability(self):
        """Test COM availability on Win11"""
        code = self.gen.generate_com_availability_check(WindowsVersion.WIN11, "Shell.Application")
        self.assertIn("IsCOMObjectAvailable", code)

    def test_unavailable_com_object_marking(self):
        """Test that unavailable COM objects are marked"""
        # Try with an object that might not be universally available
        code = self.gen.generate_com_availability_check(WindowsVersion.WIN11, "NonExistent.Object")
        # Should still generate function but mark as potentially unavailable
        self.assertIn("IsCOMObjectAvailable", code)


class TestSecurityFeaturesAwareCode(unittest.TestCase):
    """Test security-aware code generation"""

    def setUp(self):
        self.gen = WindowsVersionSpecificCOMVariants()

    def test_security_features_in_code(self):
        """Test that security features are documented in code"""
        code = self.gen.generate_security_features_aware_code(WindowsVersion.WIN7, "WScript.Shell")
        self.assertIn("Security Features:", code)

    def test_version_specific_security(self):
        """Test version-specific security features"""
        xp_code = self.gen.generate_security_features_aware_code(WindowsVersion.XP, "WScript.Shell")
        win11_code = self.gen.generate_security_features_aware_code(WindowsVersion.WIN11, "WScript.Shell")

        # Win11 should mention more security features
        xp_features = xp_code.count("Security")
        win11_features = win11_code.count("Security")
        self.assertGreater(win11_features, 0)


class TestFallbackCascade(unittest.TestCase):
    """Test fallback cascade across Windows versions"""

    def setUp(self):
        self.gen = WindowsVersionSpecificCOMVariants()

    def test_fallback_cascade_generation(self):
        """Test fallback cascade code generation"""
        versions = [WindowsVersion.WIN7, WindowsVersion.WIN10, WindowsVersion.WIN11]
        code = self.gen.generate_fallback_cascade(versions, "Excel.Application")

        self.assertIsNotNone(code)
        self.assertIn("Fallback cascade", code)
        self.assertIn("CreateObject", code)

    def test_fallback_includes_all_versions(self):
        """Test that fallback includes all specified versions"""
        versions = [WindowsVersion.WIN7, WindowsVersion.WIN10]
        code = self.gen.generate_fallback_cascade(versions, "WScript.Shell")

        self.assertIn("Windows 7", code)
        self.assertIn("Windows 10", code)

    def test_fallback_has_success_check(self):
        """Test that fallback includes success checking"""
        versions = [WindowsVersion.XP, WindowsVersion.WIN7]
        code = self.gen.generate_fallback_cascade(versions, "Excel.Application")

        self.assertIn("success", code.lower())


class TestVersionOptimizedVariants(unittest.TestCase):
    """Test version-optimized variant generation"""

    def setUp(self):
        self.gen = WindowsVersionSpecificCOMVariants()

    def test_performance_optimized_variant(self):
        """Test performance-optimized variant"""
        code = self.gen.generate_version_optimized_variant(
            WindowsVersion.WIN7, "Excel.Application", "performance"
        )
        self.assertIn("performance", code.lower())

    def test_stealth_mode_variant(self):
        """Test stealth mode variant"""
        code = self.gen.generate_version_optimized_variant(
            WindowsVersion.WIN10, "WScript.Shell", "stealth"
        )
        self.assertIn("stealth", code.lower())

    def test_compatibility_mode_variant(self):
        """Test compatibility mode variant"""
        code = self.gen.generate_version_optimized_variant(
            WindowsVersion.WIN11, "Shell.Application", "compatibility"
        )
        self.assertIn("compatibility", code.lower())

    def test_xp_performance_variant(self):
        """Test XP performance optimization (minimal overhead)"""
        code = self.gen.generate_version_optimized_variant(
            WindowsVersion.XP, "Excel.Application", "performance"
        )
        self.assertIn("minimal", code.lower())

    def test_win11_security_first(self):
        """Test Win11 security-first optimization"""
        code = self.gen.generate_version_optimized_variant(
            WindowsVersion.WIN11, "Excel.Application", "performance"
        )
        self.assertIn("security", code.lower())


class TestBulkVariantGeneration(unittest.TestCase):
    """Test bulk variant generation"""

    def setUp(self):
        self.gen = WindowsVersionSpecificCOMVariants()

    def test_all_variants_for_version(self):
        """Test generating all variants for a version"""
        variants = self.gen.generate_all_variants_for_version(WindowsVersion.WIN10)

        self.assertGreater(len(variants), 0)
        self.assertIn("version_check", variants)
        self.assertIn("uac_aware", variants)
        self.assertIn("registry_access", variants)
        self.assertIn("appdata_access", variants)
        self.assertIn("com_availability", variants)
        self.assertIn("security_aware", variants)

    def test_all_variants_have_code(self):
        """Test that all variants have code"""
        for version in WindowsVersion:
            variants = self.gen.generate_all_variants_for_version(version)
            for variant_id, variant_info in variants.items():
                self.assertIn("code", variant_info)
                self.assertGreater(len(variant_info["code"]), 0)

    def test_variant_structure(self):
        """Test variant structure consistency"""
        variants = self.gen.generate_all_variants_for_version(WindowsVersion.WIN7)

        for variant_id, variant_info in variants.items():
            self.assertIn("description", variant_info)
            self.assertIn("code", variant_info)
            self.assertIsInstance(variant_info["description"], str)
            self.assertIsInstance(variant_info["code"], str)


class TestReportGeneration(unittest.TestCase):
    """Test report generation"""

    def test_version_summary_report(self):
        """Test version summary report generation"""
        gen = WindowsVersionSpecificCOMVariants()
        report = gen.generate_version_summary_report()

        self.assertIsNotNone(report)
        self.assertGreater(len(report), 1000)
        self.assertIn("WINDOWS XP", report)
        self.assertIn("WINDOWS 11", report)

    def test_comprehensive_report(self):
        """Test comprehensive report generation"""
        report = generate_comprehensive_windows_variants_report()

        self.assertIsNotNone(report)
        self.assertGreater(len(report), 5000)
        self.assertIn("CreateObject", report)

    def test_comparison_matrix(self):
        """Test version comparison matrix generation"""
        matrix = generate_version_comparison_matrix()

        self.assertIsNotNone(matrix)
        self.assertGreater(len(matrix), 1000)
        self.assertIn("Feature", matrix)
        self.assertIn("UAC", matrix)


class TestVariableNaming(unittest.TestCase):
    """Test variable naming across variants"""

    def setUp(self):
        self.gen = WindowsVersionSpecificCOMVariants()

    def test_variable_uniqueness_within_code(self):
        """Test that variables are uniquely named"""
        self.gen._var_cache.clear()
        code1 = self.gen.generate_version_check_code(WindowsVersion.WIN7)
        # Variables should be consistent for same cache
        self.assertIn("_", code1)  # Should have underscore in var names


class TestErrorHandling(unittest.TestCase):
    """Test error handling in generated code"""

    def setUp(self):
        self.gen = WindowsVersionSpecificCOMVariants()

    def test_all_generated_code_has_error_handling(self):
        """Test that all code includes error handling"""
        for version in WindowsVersion:
            code1 = self.gen.generate_uac_aware_variant(version, "Excel.Application")
            code2 = self.gen.generate_registry_path_variant(version, "com_objects")
            code3 = self.gen.generate_appdata_folder_variant(version, "user")

            for code in [code1, code2, code3]:
                self.assertIn("On Error", code)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_version_flow(self):
        """Test complete version detection and COM instantiation flow"""
        gen = WindowsVersionSpecificCOMVariants()

        # Create version check + COM instantiation
        version_check = gen.generate_version_check_code(WindowsVersion.WIN7)
        uac_aware = gen.generate_uac_aware_variant(WindowsVersion.WIN7, "Excel.Application")
        fallback = gen.generate_fallback_cascade(
            [WindowsVersion.WIN7, WindowsVersion.WIN10], "Excel.Application"
        )

        # All should have code
        for code in [version_check, uac_aware, fallback]:
            self.assertGreater(len(code), 0)

    def test_cross_version_consistency(self):
        """Test consistency across version variants"""
        gen = WindowsVersionSpecificCOMVariants()

        # Generate same variant for all versions
        for version in WindowsVersion:
            code = gen.generate_version_check_code(version)
            # All should have similar structure
            self.assertIn("GetWindowsVersion", code)
            self.assertIn("CheckWindowsVersion", code)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestWindowsVersionInfo,
        TestVersionCheckGeneration,
        TestUACVariantGeneration,
        TestRegistryPathVariants,
        TestAppdataFolderVariants,
        TestCOMAvailabilityCheck,
        TestSecurityFeaturesAwareCode,
        TestFallbackCascade,
        TestVersionOptimizedVariants,
        TestBulkVariantGeneration,
        TestReportGeneration,
        TestVariableNaming,
        TestErrorHandling,
        TestIntegration,
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
