# WMI Comprehensive Test Suite - Usage Guide

## Quick Start

### Installation
No additional dependencies required. The test suite uses Python's standard `unittest` library.

```bash
# Ensure you have Python 3.6+
python3 --version
```

### Running All Tests
```bash
cd /home/user/sc-generator
python3 test_wmi_comprehensive_suite.py
```

Expected output:
```
Ran 51 tests in 0.005s

OK

================================================================================
COMPREHENSIVE WMI TEST SUITE REPORT
================================================================================
Total Tests: 51
Successes: 51
Failures: 0
Errors: 0
Skipped: 0
Success Rate: 100.0%
================================================================================
```

## Test Suite Organization

### Test Classes by Category

#### Error Handling Tests (5 tests)
Focus on exception handling and error recovery.

```python
# Run only error handling tests
python3 -m unittest test_wmi_comprehensive_suite.TestWMIErrorHandling -v
```

Test coverage:
- Empty command handling
- Special character handling
- Configuration error handling
- Exception propagation

#### Payload Validation Tests (9 tests)
Validate generated VBS payloads for correctness.

```python
# Run validation tests
python3 -m unittest test_wmi_comprehensive_suite.TestWMIPayloadValidation -v
```

Test coverage:
- VBS syntax validation
- WMI construct verification
- Payload structure validation
- Encoding validation

#### Edge Case Tests (8 tests)
Test boundary conditions and unusual inputs.

```python
# Run edge case tests
python3 -m unittest test_wmi_comprehensive_suite.TestWMIEdgeCases -v
```

Test coverage:
- Unicode character handling
- Very long commands (10K+ chars)
- Path handling with backslashes
- Quote escaping
- Newline handling

#### Configuration Tests (5 tests)
Verify configuration management and isolation.

```python
# Run configuration tests
python3 -m unittest test_wmi_comprehensive_suite.TestWMIConfigurationHandling -v
```

Test coverage:
- Default configuration values
- Custom configuration values
- Configuration isolation
- Variable caching

#### Polymorphic Variant Tests (2 tests)
Test multiple execution method variants.

```python
# Run polymorphic tests
python3 -m unittest test_wmi_comprehensive_suite.TestWMIPolymorphicVariants -v
```

Test coverage:
- Variant 0: Locator method
- Variant 1: Object method
- Variant 2: Event sink
- Variant 3: Obfuscated payload

#### Encoding/Decoding Tests (3 tests)
Verify command encoding and decoding.

```python
# Run encoding tests
python3 -m unittest test_wmi_comprehensive_suite.TestWMIEncodingDecoding -v
```

Test coverage:
- Base64 encoding
- Hex encoding
- Decoder function syntax

#### Remote Execution Tests (4 tests)
Test remote WMI execution capabilities.

```python
# Run remote execution tests
python3 -m unittest test_wmi_comprehensive_suite.TestWMIRemoteExecution -v
```

Test coverage:
- Basic remote execution
- Execution with credentials
- Special characters in credentials
- Localhost execution

#### Launcher Script Tests (2 tests)
Test launcher script generation.

```python
# Run launcher tests
python3 -m unittest test_wmi_comprehensive_suite.TestWMILauncherScript -v
```

Test coverage:
- Launcher with wrapper
- Launcher without wrapper

#### High-Level API Tests (3 tests)
Test the public API functions.

```python
# Run API tests
python3 -m unittest test_wmi_comprehensive_suite.TestWMIHighLevelAPI -v
```

Test coverage:
- All method types
- Default method fallback
- Unknown method handling

#### Report Generation Tests (4 tests)
Test execution method report generation.

```python
# Run report tests
python3 -m unittest test_wmi_comprehensive_suite.TestWMIExecutionReport -v
```

Test coverage:
- Report generation
- Report structure
- Method count validation
- Payload validation in reports

#### Integration Tests (3 tests)
Test integration of multiple components.

```python
# Run integration tests
python3 -m unittest test_wmi_comprehensive_suite.TestWMIIntegration -v
```

Test coverage:
- Multiple methods with same command
- Executor instance isolation
- Configuration isolation

#### Error Message Tests (2 tests)
Test error reporting and messaging.

```python
# Run error message tests
python3 -m unittest test_wmi_comprehensive_suite.TestErrorMessages -v
```

Test coverage:
- Error message informativeness
- Validation coverage

## Using the PayloadValidator Class

The `PayloadValidator` class provides utility methods for validating payloads.

### Basic Usage

```python
from test_wmi_comprehensive_suite import PayloadValidator
from wmi_executor import create_wmi_executor

# Generate a payload
executor = create_wmi_executor()
payload = executor.generate_locator_method("cmd.exe")

# Create validator
validator = PayloadValidator()

# Validate VBS syntax
is_valid, errors = validator.validate_vbs_syntax(payload)
if is_valid:
    print("✓ VBS Syntax is valid")
else:
    print("✗ VBS Syntax errors:")
    for error in errors:
        print(f"  - {error}")

# Validate WMI constructs
is_valid, errors = validator.validate_wmi_constructs(payload)
if is_valid:
    print("✓ WMI Constructs are valid")
else:
    print("✗ WMI errors:")
    for error in errors:
        print(f"  - {error}")
```

### Validation Methods

#### 1. VBS Syntax Validation
```python
is_valid, errors = PayloadValidator.validate_vbs_syntax(payload)
# Checks: CreateObject, Set, Dim, balanced parentheses, quotes
```

#### 2. WMI Construct Validation
```python
is_valid, errors = PayloadValidator.validate_wmi_constructs(payload)
# Checks: SWbemLocator, ConnectServer, namespace, process refs
```

#### 3. Command Presence Validation
```python
is_valid, errors = PayloadValidator.validate_command_presence(payload, "cmd.exe")
# Checks: Command in payload or properly encoded
```

#### 4. Critical Keywords Validation
```python
is_valid, errors = PayloadValidator.validate_no_critical_keywords(payload)
# Checks: Balanced function definitions, If statements
```

## Test Report Generation

### Automatic Report
Reports are generated automatically at test completion:

```python
def generate_test_report(result) -> Dict:
    """Generate detailed test report"""
    report = {
        "total_tests": result.testsRun,
        "successes": result.testsRun - len(result.failures) - len(result.errors),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "success_rate": ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100),
    }
    return report
```

### Programmatic Report Access

```python
import unittest
from test_wmi_comprehensive_suite import run_comprehensive_tests, generate_test_report

result = run_comprehensive_tests(verbosity=2)
report = generate_test_report(result)

print(f"Success Rate: {report['success_rate']:.1f}%")
print(f"Total Tests: {report['total_tests']}")
print(f"Failures: {report['failures']}")
print(f"Errors: {report['errors']}")
```

## Common Test Scenarios

### Scenario 1: Validate All Execution Methods

```python
from test_wmi_comprehensive_suite import PayloadValidator
from wmi_executor import create_wmi_executor

executor = create_wmi_executor()
validator = PayloadValidator()

methods = {
    'locator': executor.generate_locator_method("cmd.exe"),
    'query': executor.generate_swbem_query("cmd.exe"),
    'object': executor.generate_swbem_object_method("cmd.exe"),
    'timeout': executor.generate_swbem_timeout_method("cmd.exe", 30),
    'event': executor.generate_wmi_event_sink("cmd.exe"),
    'hybrid': executor.generate_wmi_registry_hybrid("cmd.exe"),
}

for name, payload in methods.items():
    vbs_valid, vbs_errors = validator.validate_vbs_syntax(payload)
    if vbs_valid:
        print(f"✓ {name}: Valid")
    else:
        print(f"✗ {name}: {vbs_errors}")
```

### Scenario 2: Test Custom Configuration

```python
from wmi_executor import WMIExecutor, ExecutionConfig
from test_wmi_comprehensive_suite import PayloadValidator

# Create custom config
config = ExecutionConfig(
    obfuscate_names=True,
    use_locator=True,
    encode_command=True
)

# Create executor with custom config
executor = WMIExecutor(config)

# Generate and validate
payload = executor.generate_locator_method("powershell.exe")
validator = PayloadValidator()

is_valid, errors = validator.validate_vbs_syntax(payload)
print(f"Custom config payload valid: {is_valid}")
```

### Scenario 3: Test Edge Cases

```python
from wmi_executor import create_wmi_executor
from test_wmi_comprehensive_suite import PayloadValidator

executor = create_wmi_executor()
validator = PayloadValidator()

edge_cases = [
    "",  # Empty command
    "cmd.exe " + ("test " * 1000),  # Very long
    "cmd.exe /c 日本語",  # Unicode
    r"C:\Windows\System32\calc.exe",  # Windows path
]

for command in edge_cases:
    try:
        payload = executor.generate_locator_method(command)
        is_valid, _ = validator.validate_vbs_syntax(payload)
        print(f"✓ Edge case handled: {command[:30]}...")
    except Exception as e:
        print(f"✗ Edge case failed: {str(e)[:50]}...")
```

### Scenario 4: Comprehensive Payload Validation

```python
from test_wmi_comprehensive_suite import PayloadValidator
from wmi_executor import create_wmi_executor

executor = create_wmi_executor()
validator = PayloadValidator()
payload = executor.generate_locator_method("calc.exe")

# Comprehensive validation
validations = [
    ("VBS Syntax", validator.validate_vbs_syntax(payload)),
    ("WMI Constructs", validator.validate_wmi_constructs(payload)),
    ("Command Presence", validator.validate_command_presence(payload, "calc.exe")),
    ("Critical Keywords", validator.validate_no_critical_keywords(payload)),
]

print("Comprehensive Validation Results:")
print("=" * 50)
for name, (is_valid, errors) in validations:
    status = "✓ PASS" if is_valid else "✗ FAIL"
    print(f"{name}: {status}")
    if errors:
        for error in errors:
            print(f"  - {error}")
```

## Interpreting Test Results

### All Tests Pass
```
Ran 51 tests in 0.005s
OK
Success Rate: 100.0%
```
✓ No issues detected
✓ All payload generation methods working correctly
✓ Error handling functioning properly

### Some Tests Fail
```
Ran 51 tests
FAILED (failures=X, errors=Y)
Success Rate: X%
```

Check failure details:
```bash
python3 test_wmi_comprehensive_suite.py -v
```

### Common Failure Reasons

1. **VBS Syntax Errors**
   - Unbalanced parentheses
   - Missing Set statements
   - Unclosed function definitions

2. **WMI Construct Errors**
   - Missing SWbemLocator
   - Missing ConnectServer call
   - Invalid namespace reference

3. **Validation Errors**
   - Command encoding issues
   - Special character handling
   - Quote escaping problems

## Continuous Integration

### GitHub Actions Example

```yaml
name: WMI Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Run WMI Test Suite
      run: python test_wmi_comprehensive_suite.py -v
```

## Troubleshooting

### Issue: Tests not found
```bash
# Ensure you're in the correct directory
cd /home/user/sc-generator

# Verify file exists
ls -la test_wmi_comprehensive_suite.py
```

### Issue: Import errors
```bash
# Ensure wmi_executor.py is in the same directory
ls -la wmi_executor.py

# Check Python path
python3 -c "import sys; print(sys.path)"
```

### Issue: Test timeouts
The test suite is lightweight and should complete in <10ms. If tests hang:
1. Check for infinite loops in payloads
2. Verify no external network calls
3. Review custom test modifications

### Issue: Encoding errors
If you see encoding errors with Unicode tests:
```bash
# Ensure UTF-8 encoding
export PYTHONIOENCODING=utf-8
python3 test_wmi_comprehensive_suite.py
```

## Performance Benchmarking

### Measure Execution Time
```bash
time python3 test_wmi_comprehensive_suite.py
```

Expected: ~5-10ms on modern hardware

### Profile Memory Usage
```bash
python3 -m memory_profiler test_wmi_comprehensive_suite.py
```

Expected: <50MB peak memory

## Extending the Test Suite

### Adding New Tests

```python
class TestWMICustomFeature(unittest.TestCase):
    """Test custom WMI feature"""
    
    def setUp(self):
        self.executor = create_wmi_executor()
        self.validator = PayloadValidator()
    
    def test_custom_functionality(self):
        """Test description"""
        payload = self.executor.some_method("cmd.exe")
        is_valid, errors = self.validator.validate_vbs_syntax(payload)
        self.assertTrue(is_valid)
```

### Adding New Validators

```python
# Add to PayloadValidator class
@staticmethod
def validate_custom_aspect(payload: str) -> Tuple[bool, List[str]]:
    """Validate custom aspect of payload"""
    errors = []
    # Add validation logic
    return len(errors) == 0, errors
```

## Best Practices

1. **Run tests frequently**: Before committing changes
2. **Maintain test isolation**: Each test should be independent
3. **Use descriptive names**: Test names should indicate what's being tested
4. **Document edge cases**: Comment on why specific edge cases matter
5. **Keep tests fast**: <100ms total execution time
6. **Test error paths**: Not just success cases

## Additional Resources

- WMI Executor Documentation: `wmi_executor.py`
- VBS Reference: Windows Scripting Host Documentation
- WMI Reference: Microsoft WMI Documentation
- Test Framework: Python `unittest` module documentation

## Support

For issues or questions:
1. Check test output for specific error messages
2. Review PayloadValidator for validation details
3. Examine wmi_executor.py for implementation details
4. Check WMI_TEST_SUITE_SUMMARY.md for comprehensive overview
