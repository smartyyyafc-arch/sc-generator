#!/usr/bin/env python3
"""
Test File Writer - Usage Examples

Simple examples showing how to use TestFileWriter
"""

from test_file_writer import TestFileWriter, generate_summary
import json


def example_1_single_test():
    """Example 1: Run a single test"""
    print("\n" + "="*70)
    print("Example 1: Single Test Execution")
    print("="*70)

    writer = TestFileWriter(verbose=True)

    # Python test payload
    python_code = """
import math
result = math.sqrt(16)
print(f'Square root of 16 is: {result}')
assert result == 4.0, 'Incorrect result'
print('Test passed!')
"""

    result = writer.run_test(python_code, "example1_math.py")

    print(f"\nTest Result:")
    print(f"  Status: {result.execution_status}")
    print(f"  Exit Code: {result.exit_code}")
    print(f"  Output: {result.execution_output}")
    print(f"  Cleanup: {result.cleanup_successful}")

    return result


def example_2_batch_tests():
    """Example 2: Run multiple tests and get summary"""
    print("\n" + "="*70)
    print("Example 2: Batch Test Execution")
    print("="*70)

    writer = TestFileWriter(verbose=False)

    # Multiple test cases
    tests = [
        ("print('Hello World')", "batch_hello.py"),
        ("echo 'Test 1'\necho 'Test 2'", "batch_echo.sh"),
        ("x = 5 + 3\nprint(x)", "batch_math.py"),
    ]

    results = writer.run_multiple_tests(tests)
    summary = generate_summary(results)

    print(f"\nBatch Results:")
    print(f"  Total: {summary['total_tests']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Pass Rate: {summary['pass_rate']:.1f}%")
    print(f"  Total Time: {summary['total_duration_seconds']:.4f}s")

    return results, summary


def example_3_with_assertions():
    """Example 3: Tests with assertions"""
    print("\n" + "="*70)
    print("Example 3: Tests with Assertions")
    print("="*70)

    writer = TestFileWriter(verbose=False)

    # Test with assertions
    test_payload = """
# Unit test with assertions
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

# Run tests
assert add(2, 3) == 5, "Addition failed"
assert multiply(3, 4) == 12, "Multiplication failed"
assert add(0, 0) == 0, "Zero test failed"

print("All assertions passed!")
"""

    result = writer.run_test(test_payload, "assertion_test.py")

    print(f"\nAssertion Test:")
    print(f"  Status: {result.execution_status}")
    print(f"  Output: {result.execution_output}")
    if result.execution_error:
        print(f"  Error: {result.execution_error}")

    return result


def example_4_timeout():
    """Example 4: Test with timeout"""
    print("\n" + "="*70)
    print("Example 4: Test Timeout Handling")
    print("="*70)

    writer = TestFileWriter(verbose=False)

    # This will timeout
    slow_code = "import time\ntime.sleep(5)\nprint('Done')"

    result = writer.run_test(slow_code, "timeout_test.py", timeout=1)

    print(f"\nTimeout Test (1 second limit):")
    print(f"  Status: {result.execution_status}")
    print(f"  Duration: {result.duration_seconds:.4f}s")
    print(f"  Error: {result.execution_error}")

    return result


def example_5_json_export():
    """Example 5: Export results as JSON"""
    print("\n" + "="*70)
    print("Example 5: JSON Export")
    print("="*70)

    writer = TestFileWriter(verbose=False)

    tests = [
        ("print('Test 1')", "json_test1.py"),
        ("print('Test 2')", "json_test2.py"),
    ]

    results = writer.run_multiple_tests(tests)
    summary = generate_summary(results)

    # Create JSON output
    output = {
        'summary': summary,
        'test_results': [r.to_dict() for r in results]
    }

    print("\nJSON Output:")
    print(json.dumps(output, indent=2))

    return output


def example_6_verify_file_integrity():
    """Example 6: File verification"""
    print("\n" + "="*70)
    print("Example 6: File Integrity Verification")
    print("="*70)

    writer = TestFileWriter(verbose=False)

    payload = "x = 42\nprint(f'Answer: {x}')"

    # Write the file
    success, file_path = writer.write_payload(payload, "verify_test.py")
    print(f"File written: {file_path}")

    # Verify content
    verified, error = writer.verify_file(file_path, payload)
    print(f"Verification: {verified}")

    if verified:
        # Calculate hash
        hash_val = writer.calculate_hash(payload)
        print(f"Content Hash: {hash_val}")

    # Execute
    result = writer.execute_test(file_path)
    print(f"Execution: {result['status']}")
    print(f"Output: {result['stdout']}")

    # Cleanup
    cleanup_ok = writer.cleanup()
    print(f"Cleanup: {cleanup_ok}")

    return verified


def example_7_custom_temp_dir():
    """Example 7: Using custom temp directory"""
    print("\n" + "="*70)
    print("Example 7: Custom Temp Directory")
    print("="*70)

    import tempfile
    import os

    # Create custom temp directory
    custom_dir = tempfile.mkdtemp(prefix="test_fw_")
    print(f"Using custom directory: {custom_dir}")

    writer = TestFileWriter(temp_dir=custom_dir, verbose=False)

    payload = "print('Testing with custom directory')"
    result = writer.run_test(payload, "custom_dir_test.py")

    print(f"Test Status: {result.execution_status}")
    print(f"File Path: {result.file_path}")

    # Cleanup directory
    try:
        os.rmdir(custom_dir)
        print(f"Directory cleaned up: {custom_dir}")
    except:
        print(f"Note: Directory not empty, may need manual cleanup")

    return result


if __name__ == '__main__':
    print("\n" + "="*70)
    print("TEST FILE WRITER - USAGE EXAMPLES")
    print("="*70)

    # Run all examples
    example_1_single_test()
    example_2_batch_tests()
    example_3_with_assertions()
    example_4_timeout()
    example_5_json_export()
    example_6_verify_file_integrity()
    example_7_custom_temp_dir()

    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)
