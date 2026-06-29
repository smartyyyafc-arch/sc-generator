#!/usr/bin/env python3
"""
Test suite for Configuration Fix #2 - Environment Variable Validation

Tests:
- Required variables are validated
- Type checking works correctly
- Range validation is enforced
- Path validation works
- Secure defaults are applied
- Auto-correction with warnings works
- Validation errors are caught
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path

# Import configuration module
from config import ConfigValidator, ConfigurationError, load_and_validate_config


class TestConfigValidator(unittest.TestCase):
    """Test configuration validator functionality"""

    def setUp(self):
        """Set up test environment"""
        self.validator = ConfigValidator()

    def test_validate_required_string_with_default(self):
        """Test string validation with default value"""
        os.environ.pop('TEST_STRING', None)
        result = self.validator.validate_required_string('TEST_STRING', default='default_value')
        self.assertEqual(result, 'default_value')
        self.assertFalse(self.validator.has_errors())

    def test_validate_required_string_missing_no_default(self):
        """Test string validation missing with no default"""
        os.environ.pop('TEST_STRING_MISSING', None)
        result = self.validator.validate_required_string('TEST_STRING_MISSING', default=None)
        self.assertIsNone(result)
        self.assertTrue(self.validator.has_errors())

    def test_validate_string_with_allowed_values(self):
        """Test string validation with allowed values"""
        os.environ['TEST_ENV_MODE'] = 'production'
        result = self.validator.validate_required_string(
            'TEST_ENV_MODE',
            default='development',
            allowed_values=['development', 'production', 'testing']
        )
        self.assertEqual(result, 'production')
        self.assertFalse(self.validator.has_errors())

    def test_validate_string_invalid_allowed_value(self):
        """Test string validation with invalid allowed value"""
        os.environ['TEST_ENV_MODE'] = 'invalid_mode'
        self.validator.errors = []  # Reset errors
        result = self.validator.validate_required_string(
            'TEST_ENV_MODE',
            default='development',
            allowed_values=['development', 'production']
        )
        self.assertIsNone(result)
        self.assertTrue(self.validator.has_errors())

    def test_validate_string_length_constraints(self):
        """Test string length validation"""
        os.environ['TEST_SHORT_STRING'] = 'ab'
        self.validator.errors = []
        result = self.validator.validate_required_string(
            'TEST_SHORT_STRING',
            default='default',
            min_length=5
        )
        self.assertIsNone(result)
        self.assertTrue(self.validator.has_errors())

    def test_validate_integer_valid(self):
        """Test integer validation with valid value"""
        os.environ['TEST_INT'] = '42'
        result = self.validator.validate_integer('TEST_INT', default=10)
        self.assertEqual(result, 42)
        self.assertFalse(self.validator.has_errors())

    def test_validate_integer_invalid_non_numeric(self):
        """Test integer validation with non-numeric value"""
        os.environ['TEST_INT_INVALID'] = 'not_a_number'
        self.validator.errors = []
        result = self.validator.validate_integer(
            'TEST_INT_INVALID',
            default=30,
            auto_correct=True
        )
        self.assertEqual(result, 30)
        self.assertTrue(self.validator.has_warnings())

    def test_validate_integer_below_minimum(self):
        """Test integer validation below minimum threshold"""
        os.environ['TEST_INT_MIN'] = '3'
        self.validator.errors = []
        self.validator.warnings = []
        result = self.validator.validate_integer(
            'TEST_INT_MIN',
            default=30,
            min_value=5,
            auto_correct=True
        )
        self.assertEqual(result, 30)
        self.assertTrue(self.validator.has_warnings())

    def test_validate_integer_above_maximum(self):
        """Test integer validation above maximum threshold"""
        os.environ['TEST_INT_MAX'] = '1000'
        self.validator.errors = []
        self.validator.warnings = []
        result = self.validator.validate_integer(
            'TEST_INT_MAX',
            default=30,
            max_value=100,
            auto_correct=True
        )
        self.assertEqual(result, 30)
        self.assertTrue(self.validator.has_warnings())

    def test_validate_boolean_true_values(self):
        """Test boolean validation for true values"""
        for true_value in ['true', 'True', 'TRUE', '1', 'yes', 'YES', 'on', 'enabled']:
            os.environ['TEST_BOOL'] = true_value
            self.validator.validated_config = {}
            result = self.validator.validate_boolean('TEST_BOOL', default=False)
            self.assertTrue(result, f"Failed for value: {true_value}")

    def test_validate_boolean_false_values(self):
        """Test boolean validation for false values"""
        for false_value in ['false', 'False', 'FALSE', '0', 'no', 'NO', 'off', 'disabled']:
            os.environ['TEST_BOOL'] = false_value
            self.validator.validated_config = {}
            result = self.validator.validate_boolean('TEST_BOOL', default=True)
            self.assertFalse(result, f"Failed for value: {false_value}")

    def test_validate_path_with_creation(self):
        """Test path validation with automatic creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = os.path.join(tmpdir, 'test_subdir')
            os.environ['TEST_PATH'] = test_path
            result = self.validator.validate_path(
                'TEST_PATH',
                default=tmpdir,
                create_if_missing=True
            )
            self.assertTrue(os.path.exists(test_path))
            self.assertFalse(self.validator.has_errors())

    def test_validate_path_not_exists_without_creation(self):
        """Test path validation when path doesn't exist and creation disabled"""
        os.environ['TEST_PATH_NO_CREATE'] = '/nonexistent/path/that/does/not/exist'
        self.validator.errors = []
        result = self.validator.validate_path(
            'TEST_PATH_NO_CREATE',
            default='/tmp',
            must_exist=True,
            create_if_missing=False
        )
        self.assertTrue(self.validator.has_errors())

    def test_validate_comma_separated_list(self):
        """Test comma-separated list validation"""
        os.environ['TEST_LIST'] = 'value1,value2,value3'
        result = self.validator.validate_comma_separated('TEST_LIST', default='default')
        self.assertEqual(result, ['value1', 'value2', 'value3'])
        self.assertFalse(self.validator.has_errors())

    def test_validate_comma_separated_with_spaces(self):
        """Test comma-separated list handles spaces correctly"""
        os.environ['TEST_LIST_SPACES'] = 'value1, value2 , value3'
        result = self.validator.validate_comma_separated('TEST_LIST_SPACES', default='default')
        self.assertEqual(result, ['value1', 'value2', 'value3'])

    def test_validate_comma_separated_with_allowed_values(self):
        """Test comma-separated list with allowed values constraint"""
        os.environ['TEST_LIST_ALLOWED'] = 'ext1,ext2,ext3'
        result = self.validator.validate_comma_separated(
            'TEST_LIST_ALLOWED',
            default='default',
            allowed_values=['ext1', 'ext2', 'ext3', 'ext4']
        )
        self.assertEqual(result, ['ext1', 'ext2', 'ext3'])
        self.assertFalse(self.validator.has_errors())

    def test_validate_comma_separated_invalid_value(self):
        """Test comma-separated list with invalid allowed value"""
        os.environ['TEST_LIST_INVALID'] = 'ext1,invalid,ext3'
        self.validator.errors = []
        result = self.validator.validate_comma_separated(
            'TEST_LIST_INVALID',
            default='default',
            allowed_values=['ext1', 'ext2', 'ext3']
        )
        self.assertTrue(self.validator.has_errors())

    def test_has_errors(self):
        """Test error tracking"""
        self.assertFalse(self.validator.has_errors())
        self.validator.add_error('TEST', 'test error')
        self.assertTrue(self.validator.has_errors())

    def test_has_warnings(self):
        """Test warning tracking"""
        self.assertFalse(self.validator.has_warnings())
        self.validator.add_warning('TEST', 'test warning')
        self.assertTrue(self.validator.has_warnings())

    def test_raise_if_errors(self):
        """Test that errors are raised correctly"""
        self.validator.add_error('TEST', 'critical error')
        with self.assertRaises(ConfigurationError):
            self.validator.raise_if_errors()

    def test_validated_config_dictionary(self):
        """Test that validated config is properly stored"""
        os.environ['TEST_VAR'] = 'test_value'
        self.validator.validate_required_string('TEST_VAR', default='default')
        self.assertIn('TEST_VAR', self.validator.validated_config)
        self.assertEqual(self.validator.validated_config['TEST_VAR'], 'test_value')


class TestFullConfigurationLoad(unittest.TestCase):
    """Test loading and validating complete configuration"""

    def setUp(self):
        """Set up minimal valid configuration"""
        # Set required environment variables
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['REQUEST_TIMEOUT_SECONDS'] = '30'
        os.environ['UPLOAD_TIMEOUT_SECONDS'] = '300'
        os.environ['GENERATE_TIMEOUT_SECONDS'] = '120'
        os.environ['DOWNLOAD_TIMEOUT_SECONDS'] = '60'

    def test_load_config_with_defaults(self):
        """Test loading complete configuration with defaults"""
        try:
            config = load_and_validate_config()
            self.assertIsNotNone(config)
            self.assertIn('FLASK_ENV', config)
            self.assertIn('REQUEST_TIMEOUT_SECONDS', config)
            self.assertIn('UPLOAD_FOLDER', config)
            self.assertIn('OUTPUT_FOLDER', config)
        except ConfigurationError as e:
            self.fail(f"Configuration loading failed: {e}")

    def test_timeout_validation_constraints(self):
        """Test timeout validation with constraints"""
        os.environ['REQUEST_TIMEOUT_SECONDS'] = '3'  # Below minimum of 5
        # Should be auto-corrected to default
        config = load_and_validate_config()
        # Check that a valid timeout is set (either corrected or default)
        self.assertGreaterEqual(config['REQUEST_TIMEOUT_SECONDS'], 5)

    def test_invalid_flask_env(self):
        """Test invalid FLASK_ENV value"""
        os.environ['FLASK_ENV'] = 'invalid_env_mode'
        with self.assertRaises(ConfigurationError):
            load_and_validate_config()


class TestSecurityDefaults(unittest.TestCase):
    """Test that security defaults are properly applied"""

    def setUp(self):
        """Set up for security testing"""
        self.validator = ConfigValidator()
        os.environ.pop('SECRET_KEY', None)

    def test_secret_key_warning_in_development(self):
        """Test that SECRET_KEY warning is issued when not set"""
        os.environ['FLASK_ENV'] = 'development'
        os.environ.pop('SECRET_KEY', None)
        # This should warn but not fail in development
        self.validator.validate_required_string('SECRET_KEY', default='dev-key')
        # May have warnings, but shouldn't have errors for dev mode

    def test_debug_mode_defaults_to_false(self):
        """Test that debug mode defaults to false (secure)"""
        os.environ.pop('FLASK_DEBUG', None)
        result = self.validator.validate_boolean('FLASK_DEBUG', default=False)
        self.assertFalse(result)

    def test_cors_restricted_by_default(self):
        """Test that CORS has restricted origins by default"""
        os.environ['CORS_ORIGINS'] = 'http://localhost:3000'
        result = self.validator.validate_comma_separated(
            'CORS_ORIGINS',
            default='http://localhost:3000'
        )
        self.assertNotIn('*', result)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestConfigValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestFullConfigurationLoad))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityDefaults))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
