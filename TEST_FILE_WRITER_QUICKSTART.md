# Test File Writer - Quick Start Guide

## Installation

The utility is ready to use - no installation needed:

```bash
cd /home/user/sc-generator
python3 test_file_writer.py          # Run demo
python3 test_file_writer_examples.py # View examples
```

## 30-Second Start

```python
from test_file_writer import TestFileWriter

# Create writer
writer = TestFileWriter()

# Run a single test
result = writer.run_test("print('Hello!')", "test.py")

print(f"Status: {result.execution_status}")
print(f"Output: {result.execution_output}")
```

## Common Tasks

### Task 1: Run Multiple Tests

```python
from test_file_writer import TestFileWriter, generate_summary

writer = TestFileWriter()

tests = [
    ("print('Test 1')", "test1.py"),
    ("print('Test 2')", "test2.py"),
    ("echo 'Test 3'", "test3.sh"),
]

results = writer.run_multiple_tests(tests)
summary = generate_summary(results)

print(f"Passed: {summary['passed']}/{summary['total_tests']}")
print(f"Pass Rate: {summary['pass_rate']:.1f}%")
```

### Task 2: Export Results as JSON

```python
import json
from test_file_writer import TestFileWriter, generate_summary

writer = TestFileWriter()
results = writer.run_multiple_tests(tests)
summary = generate_summary(results)

output = {
    'summary': summary,
    'results': [r.to_dict() for r in results]
}

with open('results.json', 'w') as f:
    json.dump(output, f, indent=2)
```

### Task 3: Test with Timeout

```python
result = writer.run_test(
    "import time; time.sleep(10); print('Done')",
    "test.py",
    timeout=2  # 2 second limit
)

if result.execution_status == 'TIMEOUT':
    print("Test timed out!")
```

### Task 4: Test with Assertions

```python
payload = """
def add(a, b):
    return a + b

result = add(2, 3)
assert result == 5, f"Expected 5, got {result}"
print("Assertion passed!")
"""

result = writer.run_test(payload, "test.py")
print(result.execution_output)
```

### Task 5: Verify File Integrity

```python
payload = "print('Hello')"

# Write
success, path = writer.write_payload(payload, "test.py")

# Verify
verified, error = writer.verify_file(path, payload)
print(f"File verified: {verified}")

# Hash
hash_val = writer.calculate_hash(payload)
print(f"SHA256: {hash_val}")
```

### Task 6: Custom Temp Directory

```python
import tempfile

temp_dir = tempfile.mkdtemp(prefix="my_tests_")
writer = TestFileWriter(temp_dir=temp_dir)

result = writer.run_test("print('test')", "test.py")
print(result.file_path)
```

## Supported File Types

| Type | Extension | Example |
|------|-----------|---------|
| Python | `.py` | `test_script.py` |
| Bash | `.sh` | `test_script.sh` |
| Node.js | `.js` | `test_script.js` |

## Result Attributes

```python
result = writer.run_test(payload, "test.py")

# Check success
print(result.payload_written)        # bool
print(result.file_verified)          # bool
print(result.cleanup_successful)     # bool

# Get execution info
print(result.execution_status)       # 'SUCCESS' | 'FAILED' | 'ERROR' | 'TIMEOUT' | 'SKIPPED'
print(result.exit_code)              # int
print(result.execution_output)       # str (stdout)
print(result.execution_error)        # str (stderr)

# Performance
print(result.duration_seconds)       # float
print(result.timestamp)              # ISO string

# Security
print(result.payload_hash)           # SHA256 hex
```

## Exit Status Summary

```python
from test_file_writer import generate_summary

summary = generate_summary(results)

print(summary['total_tests'])        # Total test count
print(summary['passed'])             # Passed tests
print(summary['failed'])             # Failed tests
print(summary['errors'])             # Error tests
print(summary['timeouts'])           # Timeout tests
print(summary['pass_rate'])          # 0-100
print(summary['total_duration_seconds'])  # Total time
print(summary['all_cleanup_successful'])  # Cleanup status
```

## Logging Output

Enable verbose mode to see all operations:

```python
writer = TestFileWriter(verbose=True)

# Output:
# [2026-06-29T18:30:00.123456] Payload written to /tmp/test.py
# [2026-06-29T18:30:00.123500] File verified: /tmp/test.py
# [2026-06-29T18:30:00.123600] Executing: /usr/bin/python3 /tmp/test.py
# [2026-06-29T18:30:00.125000] Cleaned up: /tmp/test.py
```

## Error Handling

```python
result = writer.run_test(payload, "test.py")

if not result.payload_written:
    print(f"Write failed: {result.file_path}")

if not result.file_verified:
    print(f"Verify failed: {result.execution_error}")

if result.execution_status == 'TIMEOUT':
    print(f"Test timed out after {result.duration_seconds}s")

if result.execution_status == 'FAILED':
    print(f"Test failed with exit code {result.exit_code}")
    print(f"Error: {result.execution_error}")

if not result.cleanup_successful:
    print(f"Cleanup failed for {result.file_path}")
```

## CI/CD Integration

```python
import json
import sys
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

# Report
print(f"Tests: {summary['total_tests']}")
print(f"Passed: {summary['passed']}")
print(f"Failed: {summary['failed']}")

# Exit appropriately
sys.exit(0 if summary['failed'] == 0 else 1)
```

## Performance Tips

1. **Batch Tests**: Use `run_multiple_tests()` for efficiency
2. **Set Timeouts**: Prevent hanging on long-running tests
3. **Disable Verbose**: Turn off logging in production
4. **Cleanup**: Automatic cleanup happens after each test

## Troubleshooting

### "File not found" Error
```python
if result.payload_written:
    print(f"Created at: {result.file_path}")
else:
    print("Failed to write payload")
```

### Verification Failed
```python
if not result.file_verified:
    print(f"Issue: {result.execution_error}")
```

### Test Timed Out
```python
result = writer.run_test(payload, "test.py", timeout=60)
```

### Interpreter Not Found
```bash
# Ensure interpreters are installed
python3 --version
node --version
bash --version
```

## Files

- **test_file_writer.py** - Main utility
- **test_file_writer_examples.py** - Usage examples
- **TEST_FILE_WRITER_API.md** - Full API reference
- **TEST_FILE_WRITER_QUICKSTART.md** - This file

## Next Steps

1. Read full API: `TEST_FILE_WRITER_API.md`
2. See examples: `python3 test_file_writer_examples.py`
3. Run demo: `python3 test_file_writer.py`
4. Integrate into your project

## Support

For more details, see:
- `TEST_FILE_WRITER_API.md` - Complete API documentation
- `test_file_writer_examples.py` - Practical examples
