# Test File Writer - API Reference

## Overview

`TestFileWriter` is a comprehensive testing framework that automates the full test lifecycle:
1. **Write** payload to test file
2. **Verify** file integrity
3. **Execute** the test file
4. **Cleanup** created resources
5. **Report** detailed results

## Installation

No external dependencies required. Uses only Python standard library.

```bash
python3 test_file_writer.py  # Run demo
python3 test_file_writer_examples.py  # View examples
```

## Quick Start

### Single Test

```python
from test_file_writer import TestFileWriter

writer = TestFileWriter()
result = writer.run_test("print('Hello')", "test.py")

print(f"Status: {result.execution_status}")
print(f"Output: {result.execution_output}")
```

### Multiple Tests

```python
writer = TestFileWriter()
tests = [
    ("print('Test 1')", "test1.py"),
    ("echo 'Test 2'", "test2.sh"),
]

results = writer.run_multiple_tests(tests)

for result in results:
    print(f"{result.test_name}: {result.execution_status}")
```

## API Reference

### TestFileWriter Class

#### Constructor

```python
TestFileWriter(temp_dir: Optional[str] = None, verbose: bool = True)
```

**Parameters:**
- `temp_dir`: Custom temporary directory (defaults to system temp)
- `verbose`: Enable status logging (default: True)

**Example:**
```python
writer = TestFileWriter(temp_dir="/tmp/my_tests", verbose=True)
```

#### Methods

##### write_payload

Write payload to a test file.

```python
def write_payload(self, payload: str, filename: str) -> Tuple[bool, str]
```

**Parameters:**
- `payload` (str): Content to write to file
- `filename` (str): Name of file to create

**Returns:**
- `(success: bool, file_path: str)` - Success status and file path or error message

**Example:**
```python
success, file_path = writer.write_payload("print('test')", "my_test.py")
if success:
    print(f"File created: {file_path}")
```

##### verify_file

Verify file integrity by comparing with expected content.

```python
def verify_file(self, file_path: str, expected_content: str) -> Tuple[bool, str]
```

**Parameters:**
- `file_path` (str): Path to file to verify
- `expected_content` (str): Expected file content

**Returns:**
- `(is_valid: bool, error_message: str)` - Validation status and error details

**Example:**
```python
valid, error = writer.verify_file(file_path, "print('test')")
if not valid:
    print(f"Verification failed: {error}")
```

##### execute_test

Execute a test file.

```python
def execute_test(self, file_path: str, timeout: int = 30) -> Dict[str, Any]
```

**Parameters:**
- `file_path` (str): Path to test file
- `timeout` (int): Timeout in seconds (default: 30)

**Returns:**
```python
{
    'status': 'SUCCESS|FAILED|ERROR|TIMEOUT',
    'exit_code': int,
    'stdout': str,
    'stderr': str,
    'duration_seconds': float,
    'error': Optional[str]
}
```

**Example:**
```python
result = writer.execute_test("test.py", timeout=10)
print(f"Exit code: {result['exit_code']}")
print(f"Output: {result['stdout']}")
print(f"Duration: {result['duration_seconds']:.3f}s")
```

##### cleanup

Clean up all created test files.

```python
def cleanup(self) -> bool
```

**Returns:**
- `bool` - True if all files cleaned up successfully

**Example:**
```python
if writer.cleanup():
    print("All temporary files cleaned up")
```

##### run_test

Run complete test cycle (write → verify → execute → cleanup).

```python
def run_test(self, payload: str, filename: str, timeout: int = 30) -> TestResult
```

**Parameters:**
- `payload` (str): Test file content
- `filename` (str): Filename to create
- `timeout` (int): Execution timeout in seconds (default: 30)

**Returns:**
- `TestResult` object with complete test information

**Example:**
```python
result = writer.run_test(
    payload="print('test')",
    filename="test.py",
    timeout=5
)

print(f"Test: {result.test_name}")
print(f"Written: {result.payload_written}")
print(f"Verified: {result.file_verified}")
print(f"Status: {result.execution_status}")
print(f"Output: {result.execution_output}")
print(f"Cleaned up: {result.cleanup_successful}")
```

##### run_multiple_tests

Run multiple test cases in sequence.

```python
def run_multiple_tests(
    self, 
    test_cases: List[Tuple[str, str]], 
    timeout: int = 30
) -> List[TestResult]
```

**Parameters:**
- `test_cases` (List): List of (payload, filename) tuples
- `timeout` (int): Timeout per test in seconds (default: 30)

**Returns:**
- `List[TestResult]` - List of test results

**Example:**
```python
tests = [
    ("print('test1')", "test1.py"),
    ("echo 'test2'", "test2.sh"),
    ("node -e \"console.log('test3')\"", "test3.js"),
]

results = writer.run_multiple_tests(tests)

for result in results:
    print(f"{result.test_name}: {result.execution_status}")
```

##### calculate_hash

Calculate SHA256 hash of content.

```python
def calculate_hash(self, content: str) -> str
```

**Parameters:**
- `content` (str): Content to hash

**Returns:**
- `str` - SHA256 hash in hexadecimal format

**Example:**
```python
hash_val = writer.calculate_hash("test content")
print(f"Hash: {hash_val}")
```

### TestResult Class

Data class containing complete test information.

**Attributes:**
```python
@dataclass
class TestResult:
    test_name: str              # Test name (filename without extension)
    payload_written: bool       # Whether file was written successfully
    payload_hash: str           # SHA256 hash of payload
    file_verified: bool         # Whether file verification passed
    file_path: str              # Path to created test file
    execution_status: str       # 'SUCCESS', 'FAILED', 'ERROR', 'TIMEOUT', 'SKIPPED'
    execution_output: str       # Standard output
    execution_error: str        # Standard error output
    exit_code: int              # Process exit code
    duration_seconds: float     # Execution time
    cleanup_successful: bool    # Whether cleanup was successful
    timestamp: str              # ISO timestamp
```

**Methods:**
```python
def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary for JSON serialization"""
```

**Example:**
```python
result = writer.run_test("print('test')", "test.py")

# Access attributes
print(result.test_name)
print(result.execution_status)
print(result.exit_code)

# Convert to dict
data = result.to_dict()
json_str = json.dumps(data)
```

### Helper Functions

#### generate_summary

Generate test summary statistics.

```python
def generate_summary(results: List[TestResult]) -> Dict[str, Any]
```

**Parameters:**
- `results` (List[TestResult]): List of test results

**Returns:**
```python
{
    'total_tests': int,
    'passed': int,
    'failed': int,
    'errors': int,
    'timeouts': int,
    'skipped': int,
    'pass_rate': float,  # 0-100
    'total_duration_seconds': float,
    'average_duration_seconds': float,
    'all_cleanup_successful': bool,
    'timestamp': str  # ISO timestamp
}
```

**Example:**
```python
from test_file_writer import generate_summary

results = writer.run_multiple_tests(tests)
summary = generate_summary(results)

print(f"Pass Rate: {summary['pass_rate']:.1f}%")
print(f"Total Time: {summary['total_duration_seconds']:.2f}s")
```

## Supported File Types

The framework auto-detects file type and executes accordingly:

| Extension | Executor | Auto-detect |
|-----------|----------|------------|
| `.py` | Python 3 | Yes |
| `.sh` | Bash | Yes |
| `.js` | Node.js | Yes |
| Other | Direct execution | Yes |

## Features

### 1. Automatic File Type Detection

```python
writer.run_test("print('py')", "test.py")      # Uses Python
writer.run_test("echo 'bash'", "test.sh")      # Uses Bash
writer.run_test("console.log('js')", "test.js")  # Uses Node.js
```

### 2. Content Verification

Files are verified before execution to ensure payload integrity:

```python
payload = "print('test')"
result = writer.run_test(payload, "test.py")

print(f"File verified: {result.file_verified}")
print(f"Payload hash: {result.payload_hash}")
```

### 3. Timeout Handling

```python
# Test that times out
result = writer.run_test("import time; time.sleep(10)", "test.py", timeout=1)
print(result.execution_status)  # 'TIMEOUT'
```

### 4. Automatic Cleanup

All created files are automatically cleaned up after execution:

```python
result = writer.run_test("print('test')", "test.py")
print(result.cleanup_successful)  # True
```

### 5. Detailed Error Reporting

```python
result = writer.run_test("raise ValueError('error')", "test.py")
print(f"Status: {result.execution_status}")  # 'FAILED'
print(f"Error: {result.execution_error}")    # Full traceback
print(f"Exit Code: {result.exit_code}")      # 1
```

### 6. JSON Export

```python
results = writer.run_multiple_tests(tests)
summary = generate_summary(results)

output = {
    'summary': summary,
    'results': [r.to_dict() for r in results]
}

json_str = json.dumps(output, indent=2)
```

## Exit Codes

The framework returns different exit codes based on test results:

- `0` - All tests passed
- `1` - One or more tests failed

## Performance Characteristics

- **Write**: ~1ms per file
- **Verify**: ~1ms per file
- **Execute**: Depends on test payload
- **Cleanup**: ~1ms per file

Typical test cycle: 10-20ms for simple tests

## Error Handling

The framework handles various error scenarios:

1. **Write Errors**: File creation failures
2. **Verification Errors**: Content mismatch
3. **Execution Errors**: Program crashes, missing interpreters
4. **Timeout Errors**: Long-running tests
5. **Cleanup Errors**: Permission issues

All errors are captured and reported in the result.

## Best Practices

### 1. Use Descriptive Filenames

```python
# Good
writer.run_test(payload, "test_array_decoder.py")

# Poor
writer.run_test(payload, "t1.py")
```

### 2. Include Assertions

```python
payload = """
result = compute_something()
assert result == expected, f"Got {result}, expected {expected}"
print("Test passed!")
"""
```

### 3. Handle Timeouts

```python
# Set appropriate timeouts
result = writer.run_test(payload, "test.py", timeout=30)
```

### 4. Batch Related Tests

```python
tests = [
    (payload1, "test_feature_a_1.py"),
    (payload2, "test_feature_a_2.py"),
    (payload3, "test_feature_a_3.py"),
]

results = writer.run_multiple_tests(tests)
summary = generate_summary(results)
```

### 5. Use Verbose Mode for Debugging

```python
writer = TestFileWriter(verbose=True)  # See all operations
```

## Limitations

1. No parallel execution (sequential only)
2. File types must have recognized extensions
3. Interpreters must be available in PATH
4. No support for interactive tests
5. No built-in test discovery

## Troubleshooting

### Test Fails with "File not found"

```python
# Check file was written
if not result.payload_written:
    print("Payload write failed")
```

### Verification Fails

```python
# File content mismatch
if not result.file_verified:
    print(f"Error: {result.execution_error}")
```

### Timeout Errors

```python
# Increase timeout
result = writer.run_test(payload, "test.py", timeout=60)
```

### Missing Interpreter

```python
# Ensure interpreter is installed and in PATH
# Python 3: python3 --version
# Node.js: node --version
# Bash: bash --version
```

## Examples

See `test_file_writer_examples.py` for comprehensive examples:

1. Single test execution
2. Batch testing
3. Tests with assertions
4. Timeout handling
5. JSON export
6. File verification
7. Custom temp directories

## Integration with CI/CD

```python
import json
from test_file_writer import TestFileWriter, generate_summary

writer = TestFileWriter(verbose=False)
results = writer.run_multiple_tests(test_cases)
summary = generate_summary(results)

# Save results
with open('test_results.json', 'w') as f:
    json.dump({
        'summary': summary,
        'results': [r.to_dict() for r in results]
    }, f, indent=2)

# Exit with appropriate code
exit(0 if summary['failed'] == 0 else 1)
```

## License

Part of sc-generator project.
