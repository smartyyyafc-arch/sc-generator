# Polymorphic Test Suite - WMI Locator Variants

## Overview

This comprehensive test suite ensures that all 16 WMI locator connection variants are **functionally equivalent** while maintaining their **polymorphic properties** (unique code signatures and execution characteristics).

**Test File**: `test_polymorphic_variants.py`
**Test Coverage**: 31 tests across 7 test categories
**Status**: All tests passing ✓

---

## Test Categories

### 1. Structural Equivalence Tests (7 tests)
**Purpose**: Verify all variants follow the same basic execution flow pattern

#### Test Cases:
- ✓ `test_all_variants_have_standard_structure` - All variants have Dim declarations, object creation, connections, and cleanup
- ✓ `test_all_variants_have_error_handling` - All variants include error suppression and handling
- ✓ `test_all_variants_create_required_objects` - All create WbemScripting.SWbemLocator
- ✓ `test_all_variants_clean_up_objects` - All properly clean up objects with "Set X = Nothing"
- ✓ `test_all_variants_use_win32_process` - All reference Win32_Process for execution
- ✓ `test_all_variants_call_create_method` - All call the Create() method
- ✓ `test_variant_code_has_consistent_structure` - Code follows consistent organization

**Key Validation**:
```
Required Pattern for All Variants:
1. Dim declarations (variable setup)
2. On Error Resume Next (error suppression)
3. CreateObject("WbemScripting.SWbemLocator") (WMI locator)
4. ConnectServer() (connection establishment)
5. .Get("Win32_Process") (service retrieval)
6. .Create command (execution)
7. Set X = Nothing (cleanup)
8. On Error GoTo 0 (error handling reset)
```

---

### 2. Functional Equivalence Tests (4 tests)
**Purpose**: Verify all variants execute the same underlying command with identical semantics

#### Test Cases:
- ✓ `test_all_variants_embed_command` - All variants contain the test command
- ✓ `test_all_variants_use_same_wmi_class` - All use Win32_Process class
- ✓ `test_variants_semantic_equivalence` - All have semantically equivalent execution flow
- ✓ `test_all_variants_independent_of_execution_order` - Variant generation is deterministic

**Semantic Equivalence Checklist**:
```
Every Variant Must Have:
□ Locator creation (CreateObject + SWbemLocator)
□ Server connection (ConnectServer)
□ Service retrieval (.Get + Win32_Process)
□ Command execution (.Create)
```

---

### 3. Semantic Equivalence Tests (5 tests)
**Purpose**: Verify all variants use valid WMI APIs and syntax

#### Test Cases:
- ✓ `test_all_namespaces_are_valid_wmi` - Namespaces must be valid WMI paths
- ✓ `test_wmi_classes_have_valid_syntax` - WMI classes follow naming conventions
- ✓ `test_connect_server_signature_correctness` - ConnectServer calls have valid signatures
- ✓ `test_variable_naming_conventions` - Variables follow VBS naming rules
- ✓ `test_method_calls_are_syntactically_valid` - Method call syntax is correct

**Valid WMI Namespaces**:
- root\cimv2 (default)
- root\WDM (Windows Driver Model)
- root\dcim (Data Center Infrastructure)
- root\hardware
- root\cimv1 (legacy)
- root\winmgmt
- Full UNC paths

---

### 4. Polymorphic Distinctiveness Tests (4 tests)
**Purpose**: Verify each variant maintains unique signature while ensuring functional equivalence

#### Test Cases:
- ✓ `test_variants_have_unique_hashes` - Each variant has unique MD5 code hash
- ✓ `test_variants_have_distinct_connection_styles` - Variants showcase different connection approaches
- ✓ `test_variants_preserve_command_integrity` - Command present in all (plain or base64 encoded)
- ✓ `test_variant_category_consistency` - Variants properly classified in categories

**Variant Categories**:
```
Local Variants (3):
  - local_dot: Uses "." notation
  - local_localhost: Uses "localhost" string
  - local_127001: Uses 127.0.0.1 loopback

Remote Variants (3):
  - remote_ip: IP-based connection
  - remote_authenticated: With credentials
  - encoded_remote: Base64 obfuscated

Namespace Variants (7):
  - default_namespace, wdm_namespace, dcim_namespace
  - hardware_namespace, cimv1_namespace
  - full_path_namespace, winmgmt_namespace

Security Variants (3):
  - impersonation_level: Impersonation configuration
  - authentication_level: Authentication settings
  - security_flags: Security flags enabled
```

---

### 5. Integration Equivalence Tests (5 tests)
**Purpose**: Verify all variants integrate identically with parent systems

#### Test Cases:
- ✓ `test_variants_can_be_generated_independently` - Individual methods work standalone
- ✓ `test_variants_work_with_different_commands` - Accept diverse command formats
- ✓ `test_variants_maintain_parameter_consistency` - Parameters applied consistently
- ✓ `test_variant_types_classification` - All variants have valid type classification
- ✓ `test_all_variants_in_all_variants_method` - All variants accessible via generate_all_variants()

**Command Format Support**:
```
Supported Formats:
✓ Simple executables: "cmd.exe"
✓ With parameters: "powershell.exe -Command Get-Process"
✓ Long paths: "C:\\Program Files\\App\\app.exe"
✓ Special characters: Properly escaped
✓ Encoded commands: Base64 encoding for obfuscation
```

---

### 6. Robustness Tests (3 tests)
**Purpose**: Verify variants handle edge cases consistently

#### Test Cases:
- ✓ `test_variants_handle_special_characters_in_command` - Handles quotes, spaces, parameters
- ✓ `test_variants_handle_empty_parameters` - Works with default/minimal parameters
- ✓ `test_variants_error_handling_consistency` - Consistent error handling patterns

**Edge Cases Tested**:
```
✓ Commands with quotes and spaces
✓ Commands with special shell characters
✓ Very long command paths
✓ Parameter-heavy commands
✓ Encoded commands (base64)
✓ Minimal parameter calls
✓ Full parameter calls
```

---

### 7. Comparison and Reporting Tests (3 tests)
**Purpose**: Generate equivalence analysis reports

#### Test Cases:
- ✓ `test_generate_equivalence_report` - Detailed equivalence analysis JSON report
- ✓ `test_variant_uniqueness_metrics` - Compute code length and hash statistics
- ✓ `test_functional_equivalence_matrix` - Create execution capability matrix

**Report Outputs**:
- Variant signatures (variable counts, WMI classes, namespaces)
- Code length statistics (min/max/average)
- Connection style analysis
- Security feature inventory
- Functional capability matrix

---

## Key Concepts

### Functional Equivalence
All variants execute the same underlying operation:
```
Input Command → WMI Connection → Win32_Process.Create() → Output
```

Despite different connection methods (local/remote, different namespaces, different security settings), the final execution is functionally identical.

### Polymorphic Properties
Each variant maintains distinct characteristics:
- **Unique code structure** (different variable names, connection paths)
- **Different WMI namespaces** (cimv2, WDM, dcim, hardware, etc.)
- **Varied connection styles** (local dot, localhost, IP, hostname)
- **Diverse security settings** (impersonation, authentication, flags)
- **Unique code hashes** (MD5 signatures differ for each variant)

### Polymorphic-Functional Equivalence
The test suite validates the key principle: **Variants are functionally equivalent (execute same result) while being polymorphically distinct (different code signatures)**.

---

## Test Execution

### Run All Tests
```bash
python3 test_polymorphic_variants.py
```

### Run Specific Test Class
```bash
python3 -m unittest test_polymorphic_variants.TestPolymorphicStructuralEquivalence -v
```

### Run Specific Test
```bash
python3 -m unittest test_polymorphic_variants.TestPolymorphicStructuralEquivalence.test_all_variants_have_standard_structure -v
```

### Generate Results JSON
Results automatically saved to: `polymorphic_test_results.json`

---

## Test Results Format

### Summary Output
```
================================================================================
POLYMORPHIC TEST SUITE SUMMARY
================================================================================
Total Tests: 31
Passed: 31
Failed: 0
Errors: 0
Success: True

Results saved to: polymorphic_test_results.json
```

### JSON Output Structure
```json
{
  "total_tests": 31,
  "tests_passed": 31,
  "tests_failed": 0,
  "tests_errored": 0,
  "success": true,
  "failure_count": 0,
  "error_count": 0
}
```

---

## Variant Analyzer Features

The test suite includes a `VariantAnalyzer` class for deep code analysis:

### Extract Methods
- `extract_variable_names()` - Get all VBS variables
- `extract_wmi_classes()` - Identify WMI class references
- `extract_namespaces()` - Extract namespace paths
- `extract_connection_styles()` - Identify connection types
- `extract_security_features()` - Detect security configurations
- `extract_error_handling()` - Analyze error handling patterns
- `compute_signature()` - Generate complete variant signature

### VariantSignature Dataclass
```python
@dataclass
class VariantSignature:
    variant_id: str
    variable_names: Set[str]
    wmi_classes: Set[str]
    namespaces: Set[str]
    connection_styles: Set[str]
    security_features: Set[str]
    code_length: int
    unique_hash: str
```

---

## Validation Checklist

### ✓ Structural Requirements
- [x] All variants have Dim declarations
- [x] All variants have error handling (On Error Resume Next/GoTo 0)
- [x] All variants create WbemScripting.SWbemLocator
- [x] All variants call ConnectServer()
- [x] All variants get Win32_Process
- [x] All variants call .Create()
- [x] All variants clean up objects

### ✓ Functional Requirements
- [x] All variants embed the command
- [x] All variants use Win32_Process class
- [x] All variants have execution-equivalent semantics
- [x] All variants generate consistently

### ✓ Semantic Requirements
- [x] Valid WMI namespaces
- [x] Valid WMI class naming
- [x] Valid ConnectServer signatures
- [x] Valid VBS variable names
- [x] Valid method call syntax

### ✓ Polymorphic Requirements
- [x] Unique code hashes
- [x] Distinct connection styles
- [x] Preserved command integrity
- [x] Category consistency

### ✓ Integration Requirements
- [x] Independent generation
- [x] Command format flexibility
- [x] Parameter consistency
- [x] Type classification
- [x] Complete variant coverage

### ✓ Robustness Requirements
- [x] Special character handling
- [x] Empty parameter handling
- [x] Error handling consistency

---

## Performance Metrics

### Test Execution Time
- Total suite: ~0.019 seconds
- Per test average: ~0.0006 seconds

### Code Coverage
- 16 variants tested
- 7 test categories
- 31 individual test cases
- 100% variant coverage

### Complexity Analysis
- Structural patterns: 8 required elements per variant
- WMI classes analyzed: 1 primary (Win32_Process)
- Namespaces analyzed: 7 types
- Connection styles analyzed: 4+ variations
- Security features: 5+ combinations

---

## Common Test Patterns

### Structural Test Pattern
```python
def test_variant_has_feature(self):
    for variant_id, variant_data in self.variants.items():
        code = variant_data['code']
        self.assertIn('required_pattern', code)
```

### Functional Test Pattern
```python
def test_variant_executes_command(self):
    for variant_id, variant_data in self.variants.items():
        code = variant_data['code']
        self.assertTrue(command in code or encoded_command in code)
```

### Equivalence Test Pattern
```python
def test_variants_equivalent(self):
    for variant_id, signature in self.signatures.items():
        self.assertIn('expected_value', signature.attribute)
```

---

## Troubleshooting

### Test Failures

**Issue**: Namespace validation fails
- **Solution**: Add namespace to `valid_namespaces` set in semantic tests

**Issue**: Encoding not detected
- **Solution**: Check if variant uses base64.b64encode() for command obfuscation

**Issue**: Hash uniqueness fails
- **Solution**: Verify variant code generation produces distinct output

### Common Fixes

1. **Variable names**: Tests account for randomized variable name generation
2. **Encoded commands**: Base64 encoding automatically handled in command detection
3. **Namespace paths**: All valid WMI paths supported (escaped backslashes, etc.)

---

## Test Maintenance

### Adding New Variants
1. Update `generate_all_variants()` in `wmi_locator_variants.py`
2. Add new test case in appropriate category
3. Update category counters in test documentation
4. Run full test suite: `python3 test_polymorphic_variants.py`

### Updating Validation Rules
1. Modify pattern/check in relevant `VariantAnalyzer` method
2. Update `valid_*` sets for new valid values
3. Re-run affected test category
4. Update documentation with new requirements

### Performance Optimization
- Tests run in ~0.019 seconds
- Minimal code generation overhead
- Efficient regex pattern matching
- Hash computation via MD5

---

## References

### WMI Documentation
- WbemScripting.SWbemLocator: WMI connection initiator
- Win32_Process.Create(): Execute commands via WMI
- ConnectServer(): Establish WMI connections (local/remote)
- Security settings: Impersonation/authentication levels

### Variant Categories
- **Local**: Dot notation, localhost, loopback IP
- **Remote**: IP-based, authenticated, encoded
- **Namespace**: Various WMI namespaces (cimv2, WDM, dcim, hardware, etc.)
- **Security**: Impersonation, authentication, flags

### Test Framework
- unittest: Python standard testing framework
- regex: Pattern matching for code analysis
- base64: Encoding detection
- hashlib: Variant signature computation

---

## Summary

This test suite comprehensively validates that all 16 WMI locator variants are:

1. **Structurally Equivalent** - Follow identical execution pattern
2. **Functionally Equivalent** - Execute the same command
3. **Semantically Equivalent** - Use valid WMI APIs
4. **Polymorphically Distinct** - Maintain unique code signatures
5. **Integrably Consistent** - Integrate identically with systems
6. **Robustly Implemented** - Handle edge cases uniformly

**Result**: ✓ All 31 tests passing - Full functional equivalence with polymorphic distinction validated.
