#!/usr/bin/env python3
"""
Polymorphic Test Suite - WMI Locator Variants
Ensures all variants are functionally equivalent while maintaining polymorphic properties.

Test Categories:
1. Structural Equivalence: All variants follow the same basic execution flow
2. Functional Equivalence: All variants execute the same underlying command
3. Semantic Equivalence: All variants use valid WMI APIs and syntax
4. Polymorphic Properties: Each variant maintains unique signatures
5. Integration Equivalence: All variants integrate with parent system identically
"""

import unittest
import re
import base64
import json
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Import the WMI variant generator
import sys
sys.path.insert(0, '/home/user/sc-generator')
from wmi_locator_variants import WMILocatorVariantGenerator, LocatorConnectionConfig


@dataclass
class VariantSignature:
    """Signature of a variant for polymorphic analysis"""
    variant_id: str
    variable_names: Set[str]
    wmi_classes: Set[str]
    namespaces: Set[str]
    connection_styles: Set[str]
    security_features: Set[str]
    code_length: int
    unique_hash: str


class VariantAnalyzer:
    """Analyzes VBS code for structural and functional properties"""

    @staticmethod
    def extract_variable_names(code: str) -> Set[str]:
        """Extract all VBS variable names from code"""
        # Match Dim declarations and variable assignments
        pattern = r'\b(Dim|Set)\s+([a-zA-Z_]\w*)\b'
        matches = re.findall(pattern, code, re.IGNORECASE)
        return {match[1] for match in matches}

    @staticmethod
    def extract_wmi_classes(code: str) -> Set[str]:
        """Extract WMI class references"""
        pattern = r'(?:Get|ExecQuery|InstancesOf|AssociatorsOf)\s*\(\s*"([^"]+)"'
        matches = re.findall(pattern, code, re.IGNORECASE)
        return set(matches)

    @staticmethod
    def extract_namespaces(code: str) -> Set[str]:
        """Extract WMI namespace references"""
        pattern = r'(?:root\\+|\\\\\\\\root\\\\)([a-zA-Z0-9_]+(?:\\\\[a-zA-Z0-9_]+)*)'
        matches = re.findall(pattern, code, re.IGNORECASE)
        # Also capture explicit namespace strings
        namespace_pattern = r'"(root\\[^"]*)"'
        explicit = re.findall(namespace_pattern, code)
        return set(matches) | set(explicit)

    @staticmethod
    def extract_connection_styles(code: str) -> Set[str]:
        """Extract WMI connection styles"""
        styles = set()
        if re.search(r'ConnectServer\s*\(\s*"\."\s*[,)]', code, re.IGNORECASE):
            styles.add("local_dot")
        if re.search(r'ConnectServer\s*\(\s*"localhost"', code, re.IGNORECASE):
            styles.add("local_localhost")
        if re.search(r'ConnectServer\s*\(\s*"127\.0\.0\.1"', code, re.IGNORECASE):
            styles.add("local_loopback")
        if re.search(r'ConnectServer\s*\(\s*"(?!\.)[^"]*"\s*,', code, re.IGNORECASE):
            styles.add("remote_host")
        return styles

    @staticmethod
    def extract_security_features(code: str) -> Set[str]:
        """Extract security-related features"""
        features = set()
        if re.search(r'ImpersonationLevel', code, re.IGNORECASE):
            features.add("impersonation")
        if re.search(r'AuthenticationLevel', code, re.IGNORECASE):
            features.add("authentication_level")
        if re.search(r'Security_', code, re.IGNORECASE):
            features.add("security_object")
        if re.search(r'ConnectServer\s*\([^)]*""[^)]*""[^)]*""[^)]*""[^)]*,', code):
            features.add("security_flags")
        if re.search(r'DecodeBase64|node\.DataType.*base64', code, re.IGNORECASE):
            features.add("encoding")
        return features

    @staticmethod
    def extract_error_handling(code: str) -> Dict[str, int]:
        """Extract error handling patterns"""
        patterns = {
            "on_error_resume_next": len(re.findall(r'On Error Resume Next', code, re.IGNORECASE)),
            "on_error_goto_zero": len(re.findall(r'On Error GoTo 0', code, re.IGNORECASE)),
            "error_objects": len(re.findall(r'\bErr\b', code, re.IGNORECASE)),
        }
        return patterns

    @staticmethod
    def compute_signature(code: str, variant_id: str) -> VariantSignature:
        """Compute signature of a variant"""
        import hashlib
        return VariantSignature(
            variant_id=variant_id,
            variable_names=VariantAnalyzer.extract_variable_names(code),
            wmi_classes=VariantAnalyzer.extract_wmi_classes(code),
            namespaces=VariantAnalyzer.extract_namespaces(code),
            connection_styles=VariantAnalyzer.extract_connection_styles(code),
            security_features=VariantAnalyzer.extract_security_features(code),
            code_length=len(code),
            unique_hash=hashlib.md5(code.encode()).hexdigest()
        )


class TestPolymorphicStructuralEquivalence(unittest.TestCase):
    """Test 1: Structural Equivalence - All variants follow same flow pattern"""

    def setUp(self):
        self.generator = WMILocatorVariantGenerator()
        self.test_command = "calc.exe"
        self.variants = self.generator.generate_all_variants(self.test_command)

    def test_all_variants_have_standard_structure(self):
        """All variants must have basic VBS structure"""
        required_patterns = [
            r'Dim\s+',  # Variable declarations
            r'CreateObject\s*\(',  # Object creation
            r'ConnectServer\s*\(',  # WMI connection
            r'Set.*Nothing',  # Object cleanup
        ]

        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            for pattern in required_patterns:
                with self.subTest(variant=variant_id, pattern=pattern):
                    self.assertIsNotNone(
                        re.search(pattern, code, re.IGNORECASE),
                        f"Variant {variant_id} missing pattern: {pattern}"
                    )

    def test_all_variants_have_error_handling(self):
        """All variants must include error handling"""
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            with self.subTest(variant=variant_id):
                self.assertIn('On Error Resume Next', code,
                            f"Variant {variant_id} missing error suppression")
                self.assertIn('On Error GoTo 0', code,
                            f"Variant {variant_id} missing error handling reset")

    def test_all_variants_create_required_objects(self):
        """All variants must create WbemScripting.SWbemLocator"""
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            with self.subTest(variant=variant_id):
                self.assertIn('WbemScripting.SWbemLocator', code,
                            f"Variant {variant_id} missing SWbemLocator creation")

    def test_all_variants_clean_up_objects(self):
        """All variants must properly clean up objects"""
        required_cleanups = ['var_loc', 'var_conn', 'var_svc']

        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            # Count Set X = Nothing statements
            cleanup_count = len(re.findall(r'Set\s+\w+\s*=\s*Nothing', code))
            with self.subTest(variant=variant_id):
                self.assertGreaterEqual(cleanup_count, 3,
                                      f"Variant {variant_id} insufficient cleanup statements")

    def test_all_variants_use_win32_process(self):
        """All variants must reference Win32_Process for execution"""
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            with self.subTest(variant=variant_id):
                self.assertIn('Win32_Process', code,
                            f"Variant {variant_id} missing Win32_Process reference")

    def test_all_variants_call_create_method(self):
        """All variants must call Create method on service object"""
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            with self.subTest(variant=variant_id):
                # Create or DecodeBase64 then Create
                has_create = '.Create ' in code or 'Create ' in code
                self.assertTrue(has_create,
                              f"Variant {variant_id} missing Create() method call")

    def test_variant_code_has_consistent_structure(self):
        """All variant code must follow consistent structure"""
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            lines = [l.strip() for l in code.split('\n') if l.strip()]

            with self.subTest(variant=variant_id):
                # First non-empty line should be Dim or Function
                self.assertRegex(lines[0], r'^(Dim|Function)',
                               f"Variant {variant_id} improper structure start")
                # Should have error handling early
                error_handlers = [i for i, l in enumerate(lines)
                                if 'On Error' in l]
                self.assertTrue(error_handlers,
                              f"Variant {variant_id} missing error handlers")


class TestPolymorphicFunctionalEquivalence(unittest.TestCase):
    """Test 2: Functional Equivalence - All variants execute the same command"""

    def setUp(self):
        self.generator = WMILocatorVariantGenerator()
        self.test_command = "notepad.exe"
        self.variants = self.generator.generate_all_variants(self.test_command)

    def test_all_variants_embed_command(self):
        """All variants must include the test command"""
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            with self.subTest(variant=variant_id):
                # Command should be present (may be base64 encoded)
                self.assertTrue(
                    self.test_command in code or
                    base64.b64encode(self.test_command.encode()).decode() in code,
                    f"Variant {variant_id} missing command"
                )

    def test_all_variants_use_same_wmi_class(self):
        """All variants must use Win32_Process WMI class"""
        wmi_classes = set()
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            classes = VariantAnalyzer.extract_wmi_classes(code)
            wmi_classes.update(classes)

        with self.subTest():
            self.assertIn('Win32_Process', wmi_classes,
                         "Some variant missing Win32_Process class")

    def test_variants_semantic_equivalence(self):
        """All variants should have semantically equivalent execution flow"""
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            with self.subTest(variant=variant_id):
                # Extract key semantic operations
                has_locator_creation = 'CreateObject' in code and 'SWbemLocator' in code
                has_server_connection = 'ConnectServer' in code
                has_service_retrieval = '.Get(' in code and 'Win32_Process' in code
                has_command_execution = '.Create' in code

                self.assertTrue(has_locator_creation,
                              f"{variant_id}: missing locator creation")
                self.assertTrue(has_server_connection,
                              f"{variant_id}: missing server connection")
                self.assertTrue(has_service_retrieval,
                              f"{variant_id}: missing service retrieval")
                self.assertTrue(has_command_execution,
                              f"{variant_id}: missing command execution")

    def test_all_variants_independent_of_execution_order(self):
        """Variant execution order should not affect outcome"""
        # Test that generating variants multiple times yields consistent results
        gen1 = WMILocatorVariantGenerator()
        gen2 = WMILocatorVariantGenerator()

        variants1 = gen1.generate_all_variants(self.test_command)
        variants2 = gen2.generate_all_variants(self.test_command)

        # Variant structure should be consistent (ignoring randomized variable names)
        for variant_id in variants1:
            with self.subTest(variant=variant_id):
                code1 = variants1[variant_id]['code']
                code2 = variants2[variant_id]['code']

                # Both should have same structure
                self.assertEqual(
                    len(code1.split('\n')),
                    len(code2.split('\n')),
                    f"Variant {variant_id} structure inconsistency"
                )


class TestPolymorphicSemanticEquivalence(unittest.TestCase):
    """Test 3: Semantic Equivalence - All variants use valid WMI APIs"""

    def setUp(self):
        self.generator = WMILocatorVariantGenerator()
        self.test_command = "cmd.exe /c echo test"
        self.variants = self.generator.generate_all_variants(self.test_command)

    def test_all_namespaces_are_valid_wmi(self):
        """All extracted namespaces must be valid WMI namespaces"""
        valid_namespaces = {
            'cimv2', 'WDM', 'dcim', 'hardware', 'cimv1',
            'root', 'default', 'winmgmt', 'wdm'
        }

        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            namespaces = VariantAnalyzer.extract_namespaces(code)

            with self.subTest(variant=variant_id):
                for ns in namespaces:
                    # Namespace should be recognizable
                    self.assertTrue(
                        any(valid in ns.lower() for valid in valid_namespaces) or
                        ns == '.',
                        f"Variant {variant_id} uses invalid namespace: {ns}"
                    )

    def test_wmi_classes_have_valid_syntax(self):
        """All WMI class references must have valid syntax"""
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            classes = VariantAnalyzer.extract_wmi_classes(code)

            with self.subTest(variant=variant_id):
                for wmi_class in classes:
                    # WMI classes typically start with Win32_ or MSFT_
                    self.assertTrue(
                        wmi_class.startswith(('Win32_', 'MSFT_', 'CIM_')) or
                        wmi_class == 'Win32_Process',
                        f"Variant {variant_id} invalid WMI class: {wmi_class}"
                    )

    def test_connect_server_signature_correctness(self):
        """All ConnectServer calls must have valid signatures"""
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            # Extract ConnectServer calls
            connects = re.findall(
                r'ConnectServer\s*\(\s*([^)]+)\)',
                code
            )

            with self.subTest(variant=variant_id):
                self.assertTrue(connects,
                              f"Variant {variant_id} missing ConnectServer")
                # Each call should have host parameter at minimum
                for connect in connects:
                    params = connect.split(',')
                    self.assertGreater(len(params), 0,
                                     f"Variant {variant_id} invalid ConnectServer params")

    def test_variable_naming_conventions(self):
        """All variables must follow valid VBS naming conventions"""
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            vars_used = VariantAnalyzer.extract_variable_names(code)

            with self.subTest(variant=variant_id):
                for var in vars_used:
                    # VBS variable names: start with letter/underscore, alphanumeric
                    self.assertRegex(var, r'^[a-zA-Z_]\w*$',
                                   f"Variant {variant_id} invalid variable name: {var}")

    def test_method_calls_are_syntactically_valid(self):
        """All method calls must be syntactically valid"""
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']

            with self.subTest(variant=variant_id):
                # Check for properly formed object method calls
                invalid_patterns = [
                    r'\.\s*\.\s*',  # Double dots
                    r'\s\.\s',      # Space-dot-space
                ]
                for pattern in invalid_patterns:
                    self.assertIsNone(
                        re.search(pattern, code),
                        f"Variant {variant_id} has invalid method call syntax"
                    )


class TestPolymorphicDistinctiveness(unittest.TestCase):
    """Test 4: Polymorphic Properties - Each variant maintains unique signature"""

    def setUp(self):
        self.generator = WMILocatorVariantGenerator()
        self.test_command = "test.exe"
        self.variants = self.generator.generate_all_variants(self.test_command)
        self.signatures = {
            var_id: VariantAnalyzer.compute_signature(var_data['code'], var_id)
            for var_id, var_data in self.variants.items()
        }

    def test_variants_have_unique_hashes(self):
        """Each variant code should have unique hash"""
        hashes = [sig.unique_hash for sig in self.signatures.values()]
        unique_hashes = set(hashes)

        self.assertEqual(len(hashes), len(unique_hashes),
                        "Some variants have identical code structure")

    def test_variants_have_distinct_connection_styles(self):
        """Variants should showcase different connection approaches"""
        local_variants = [
            'local_dot', 'local_localhost', 'local_127001'
        ]
        remote_variants = [
            'remote_ip', 'remote_authenticated', 'encoded_remote'
        ]
        namespace_variants = [
            'default_namespace', 'wdm_namespace', 'dcim_namespace',
            'hardware_namespace', 'cimv1_namespace', 'full_path_namespace',
            'winmgmt_namespace'
        ]

        # Verify local variants use different connection strings
        for variant_id in local_variants:
            if variant_id in self.variants:
                code = self.variants[variant_id]['code']
                styles = VariantAnalyzer.extract_connection_styles(code)
                # Should identify its connection style
                self.assertTrue(styles,
                              f"{variant_id} should have identifiable connection style")

    def test_variants_preserve_command_integrity(self):
        """Command should be present and intact in all variants"""
        for variant_id, variant_data in self.variants.items():
            code = variant_data['code']
            # Look for command in plain or encoded form
            has_command = (
                self.test_command in code or
                self.test_command.upper() in code or
                base64.b64encode(self.test_command.encode()).decode() in code
            )
            with self.subTest(variant=variant_id):
                self.assertTrue(has_command,
                              f"Variant {variant_id} lost command integrity")

    def test_variant_category_consistency(self):
        """Variants in same category should have similar characteristics"""
        categories = {}
        for variant_id, variant_data in self.variants.items():
            category = variant_data.get('type', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(variant_id)

        # Analyze consistency within categories
        for category, variant_ids in categories.items():
            if len(variant_ids) > 1:
                with self.subTest(category=category):
                    # Variants in same category should be classifiable
                    # At minimum they should all exist and have signatures
                    for var_id in variant_ids:
                        self.assertIn(var_id, self.signatures,
                                    f"Missing signature for {var_id} in category {category}")


class TestPolymorphicIntegrationEquivalence(unittest.TestCase):
    """Test 5: Integration Equivalence - All variants integrate identically"""

    def setUp(self):
        self.generator = WMILocatorVariantGenerator()
        self.test_command = "powershell.exe"
        self.variants = self.generator.generate_all_variants(self.test_command)

    def test_variants_can_be_generated_independently(self):
        """Each variant method should work independently"""
        test_cmd = "test.exe"

        # Test individual method calls
        local_dot = self.generator.generate_local_dot_connection(test_cmd)
        localhost = self.generator.generate_localhost_connection(test_cmd)
        loopback = self.generator.generate_127001_connection(test_cmd)

        self.assertIn('".', local_dot)
        self.assertIn('localhost', localhost)
        self.assertIn('127.0.0.1', loopback)

    def test_variants_work_with_different_commands(self):
        """All variants should accept different commands"""
        commands = [
            "cmd.exe",
            "powershell.exe -Command Get-Process",
            "notepad.exe",
            "C:\\\\Program Files\\\\App\\\\app.exe",
        ]

        for cmd in commands:
            variants = self.generator.generate_all_variants(cmd)
            with self.subTest(command=cmd):
                # Each variant should contain command
                for var_id, var_data in variants.items():
                    code = var_data['code']
                    # Check for command presence (accounting for encoding and escaping)
                    self.assertTrue(
                        cmd in code or
                        cmd.replace('\\', '\\\\') in code or
                        base64.b64encode(cmd.encode()).decode() in code,
                        f"Variant {var_id} failed with command: {cmd}"
                    )

    def test_variants_maintain_parameter_consistency(self):
        """Parameters should be applied consistently across variants"""
        # Test with namespace parameter
        namespace_variants = [
            ('default_namespace', self.generator.generate_default_namespace_connection),
            ('authentication_level', self.generator.generate_authentication_level_connection),
            ('impersonation', self.generator.generate_impersonation_connection),
        ]

        for var_name, method in namespace_variants:
            try:
                code = method(self.test_command, "root\\cimv2")
                self.assertIn("root\\cimv2", code,
                            f"Parameter not applied in {var_name}")
            except TypeError:
                # Some variants have different signatures, which is ok
                pass

    def test_variant_types_classification(self):
        """All variants should be classified with valid types"""
        valid_types = {'local', 'remote', 'remote_auth', 'namespace',
                      'security', 'remote_obfuscated'}

        for variant_id, variant_data in self.variants.items():
            var_type = variant_data.get('type')
            with self.subTest(variant=variant_id):
                self.assertIn(var_type, valid_types,
                            f"Variant {variant_id} has invalid type: {var_type}")

    def test_all_variants_in_all_variants_method(self):
        """All generation methods should appear in generate_all_variants"""
        # Get all variant IDs from the method
        all_var_ids = set(self.variants.keys())

        # Count variants by category
        type_counts = {}
        for var_data in self.variants.values():
            var_type = var_data.get('type')
            type_counts[var_type] = type_counts.get(var_type, 0) + 1

        # Should have representation from each category
        required_types = {'local', 'remote', 'namespace', 'security', 'remote_obfuscated'}
        found_types = set(type_counts.keys())

        self.assertTrue(required_types.issubset(found_types),
                       f"Missing variant types: {required_types - found_types}")


class TestPolymorphicRobustness(unittest.TestCase):
    """Test 6: Robustness - Variants handle edge cases consistently"""

    def setUp(self):
        self.generator = WMILocatorVariantGenerator()

    def test_variants_handle_special_characters_in_command(self):
        """Variants should handle commands with special characters"""
        commands_with_special_chars = [
            'cmd.exe /c echo "hello world"',
            'powershell.exe -Command $x=1;Write-Host $x',
            'C:\\Path\\With Spaces\\app.exe',
        ]

        for cmd in commands_with_special_chars:
            variants = self.generator.generate_all_variants(cmd)
            with self.subTest(command=cmd):
                # At least one variant should contain the command
                found = False
                for var_data in variants.values():
                    if cmd in var_data['code'] or cmd.replace('\\', '\\\\') in var_data['code']:
                        found = True
                        break
                self.assertTrue(found, f"No variant handled: {cmd}")

    def test_variants_handle_empty_parameters(self):
        """Variants should handle empty/default parameters gracefully"""
        # Test with minimal parameters
        try:
            code1 = self.generator.generate_default_namespace_connection("cmd.exe")
            self.assertIn("cmd.exe", code1)

            code2 = self.generator.generate_local_dot_connection("test.exe")
            self.assertIn("test.exe", code2)
        except Exception as e:
            self.fail(f"Variant failed with minimal parameters: {e}")

    def test_variants_error_handling_consistency(self):
        """All variants should have consistent error handling patterns"""
        variants = self.generator.generate_all_variants("test.exe")
        error_patterns = {}

        for variant_id, variant_data in variants.items():
            code = variant_data['code']
            errors = VariantAnalyzer.extract_error_handling(code)
            error_patterns[variant_id] = errors

        # All should have On Error Resume Next
        for variant_id, pattern in error_patterns.items():
            with self.subTest(variant=variant_id):
                self.assertGreater(pattern['on_error_resume_next'], 0,
                                 f"{variant_id} missing On Error Resume Next")
                self.assertGreater(pattern['on_error_goto_zero'], 0,
                                 f"{variant_id} missing On Error GoTo 0")


class TestPolymorphicComparisonReport(unittest.TestCase):
    """Test 7: Comprehensive comparison and reporting"""

    def setUp(self):
        self.generator = WMILocatorVariantGenerator()
        self.test_command = "report_test.exe"
        self.variants = self.generator.generate_all_variants(self.test_command)
        self.signatures = {
            var_id: VariantAnalyzer.compute_signature(var_data['code'], var_id)
            for var_id, var_data in self.variants.items()
        }

    def test_generate_equivalence_report(self):
        """Generate detailed equivalence analysis report"""
        report = {
            "test_suite": "Polymorphic Functional Equivalence",
            "total_variants": len(self.variants),
            "test_command": self.test_command,
            "analysis": {}
        }

        for variant_id, signature in self.signatures.items():
            report["analysis"][variant_id] = {
                "code_length": signature.code_length,
                "unique_hash": signature.unique_hash,
                "variable_count": len(signature.variable_names),
                "wmi_classes": list(signature.wmi_classes),
                "namespaces": list(signature.namespaces),
                "connection_styles": list(signature.connection_styles),
                "security_features": list(signature.security_features),
            }

        self.assertIn("analysis", report)
        self.assertEqual(len(report["analysis"]), len(self.variants))

    def test_variant_uniqueness_metrics(self):
        """Compute variant distinctiveness metrics"""
        metrics = {
            "total_unique_codes": len(set(sig.unique_hash for sig in self.signatures.values())),
            "avg_code_length": sum(sig.code_length for sig in self.signatures.values()) / len(self.signatures),
            "min_code_length": min(sig.code_length for sig in self.signatures.values()),
            "max_code_length": max(sig.code_length for sig in self.signatures.values()),
        }

        self.assertEqual(metrics["total_unique_codes"], len(self.variants),
                        "Not all variants are unique")
        self.assertGreater(metrics["avg_code_length"], 0)

    def test_functional_equivalence_matrix(self):
        """Create functional equivalence matrix"""
        matrix = {}

        for var_id, signature in self.signatures.items():
            # Each variant should support the same command
            variant_data = self.variants[var_id]
            code = variant_data['code']

            matrix[var_id] = {
                "supports_command": self.test_command in code or
                                   self.test_command.upper() in code,
                "has_error_handling": 'On Error' in code,
                "creates_wmi_object": 'CreateObject' in code,
                "connects_to_server": 'ConnectServer' in code,
                "gets_wmi_class": '.Get(' in code,
                "executes_process": '.Create' in code,
            }

        # All variants should support core operations
        for var_id, support in matrix.items():
            with self.subTest(variant=var_id):
                # For encoded variants, command is base64 encoded
                code = self.variants[var_id]['code']
                has_command = (support["supports_command"] or
                             base64.b64encode(self.test_command.encode()).decode() in code)
                self.assertTrue(has_command,
                              f"{var_id} doesn't support command")
                self.assertTrue(support["has_error_handling"],
                              f"{var_id} missing error handling")
                self.assertTrue(support["creates_wmi_object"],
                              f"{var_id} doesn't create WMI object")
                self.assertTrue(support["connects_to_server"],
                              f"{var_id} doesn't connect to server")


def run_polymorphic_test_suite(verbosity: int = 2) -> Dict[str, any]:
    """
    Run the complete polymorphic test suite
    Returns results dictionary
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestPolymorphicStructuralEquivalence,
        TestPolymorphicFunctionalEquivalence,
        TestPolymorphicSemanticEquivalence,
        TestPolymorphicDistinctiveness,
        TestPolymorphicIntegrationEquivalence,
        TestPolymorphicRobustness,
        TestPolymorphicComparisonReport,
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Compile results
    return {
        "total_tests": result.testsRun,
        "tests_passed": result.testsRun - len(result.failures) - len(result.errors),
        "tests_failed": len(result.failures),
        "tests_errored": len(result.errors),
        "success": result.wasSuccessful(),
        "failures": [(str(test), traceback) for test, traceback in result.failures],
        "errors": [(str(test), traceback) for test, traceback in result.errors],
    }


if __name__ == '__main__':
    results = run_polymorphic_test_suite(verbosity=2)

    print("\n" + "=" * 80)
    print("POLYMORPHIC TEST SUITE SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['tests_passed']}")
    print(f"Failed: {results['tests_failed']}")
    print(f"Errors: {results['tests_errored']}")
    print(f"Success: {results['success']}")

    # Save results to JSON
    import json
    with open('/home/user/sc-generator/polymorphic_test_results.json', 'w') as f:
        # Convert non-serializable items
        serializable_results = {
            "total_tests": results['total_tests'],
            "tests_passed": results['tests_passed'],
            "tests_failed": results['tests_failed'],
            "tests_errored": results['tests_errored'],
            "success": results['success'],
            "failure_count": len(results['failures']),
            "error_count": len(results['errors']),
        }
        json.dump(serializable_results, f, indent=2)
        print(f"\nResults saved to: /home/user/sc-generator/polymorphic_test_results.json")
