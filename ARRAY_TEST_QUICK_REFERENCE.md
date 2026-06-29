# Array Test Suite Quick Reference

## Running Tests

### Single Test File
```bash
python test_array_comprehensive_payloads.py
python test_array_performance_benchmarks.py
python test_array_edge_cases_integration.py
```

### All Tests
```bash
python test_array_comprehensive_payloads.py && \
python test_array_performance_benchmarks.py && \
python test_array_edge_cases_integration.py
```

### With Output Capture
```bash
python test_array_comprehensive_payloads.py > payloads_results.txt 2>&1
python test_array_performance_benchmarks.py > benchmarks_results.txt 2>&1
python test_array_edge_cases_integration.py > edge_cases_results.txt 2>&1
```

---

## Test Summary

### test_array_comprehensive_payloads.py (60+ tests)
Tests encoding with various payload sizes from bytes to megabytes.

**Test Groups:**
- Tiny Payloads: < 50 bytes (5 tests)
- Small Payloads: 50-500 bytes (4 tests)
- Medium Payloads: 500-5KB (4 tests)
- Large Payloads: 5KB-50KB (4 tests)
- Very Large Payloads: 50KB+ (3 tests)
- Chunk Sizes: 1-512 bytes (8 tests)
- Encoding Types: HEX/BASE64/OCTAL (9 tests)
- Chunking Strategies: All 4 strategies (4 tests)
- Output Formats: 7 different formats (7 tests)
- Roundtrip: Encode/decode validation (5 tests)
- Edge Cases: Unusual scenarios (6 tests)
- Stress Test: 18 combinations (1 test)

**Expected Results:**
- 60+ tests, 100% pass rate
- Performance timing included
- Organized by test group

---

### test_array_performance_benchmarks.py (44 benchmarks)
Measures encoding speed, throughput, and resource usage.

**Benchmark Categories:**
- Encoding Speed: 100B to 500KB (8 tests)
- Decoding Speed: Various chunk counts (5 tests)
- Encoding Types: HEX/BASE64/OCTAL (3 tests)
- Chunk Sizes: 4-512 bytes (8 tests)
- Output Formats: All 7 formats (7 tests)
- Chunking Strategies: All 4 strategies (4 tests)
- Memory Usage: Various sizes (4 tests)
- Scalability: Performance scaling (5 tests)

**Output:**
- `benchmark_results.json` - Machine-readable results
- Console output with timing and throughput
- Memory usage metrics
- Scaling analysis

**Key Metrics:**
- Time (milliseconds)
- Throughput (MB/s or chunks/sec)
- Memory usage (current and peak)
- Scaling factors

---

### test_array_edge_cases_integration.py (35+ tests)
Tests unusual scenarios, error handling, and format validation.

**Test Categories:**
- Empty/Null: 3 tests
- Size Boundaries: 4 tests
- Special Characters: 5 tests
- Repetitive Patterns: 2 tests
- Encoding Edge Cases: 3 tests
- Chunk Size Extremes: 3 tests
- Strategy Edge Cases: 4 tests
- Format Validation: 4 tests
- Roundtrip Testing: 3 tests
- Random Data: 2 tests
- Convenience Functions: 2 tests

**Expected Results:**
- 35+ tests, 97%+ pass rate
- Format validation (Python, JSON, VBS, Bash syntax)
- Roundtrip encode-decode verification
- Edge case handling

---

## Quick Configuration Examples

### Minimal Encoding (Small Payload)
```python
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat

config = EncoderConfig(
    chunk_size=16,
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.PYTHON
)
encoder = ArrayEncoder(config)
result = encoder.generate("calc.exe")
```

### Performance Optimized (Large Payload)
```python
config = EncoderConfig(
    chunk_size=256,
    encoding_type=EncodingType.BASE64,
    output_format=OutputFormat.JSON,
    chunking_strategy=ChunkingStrategy.SEQUENTIAL
)
encoder = ArrayEncoder(config)
result = encoder.generate(large_payload)
```

### Obfuscated (Stealth)
```python
from array_encoder import ChunkingStrategy

config = EncoderConfig(
    chunk_size=random.randint(32, 128),
    encoding_type=EncodingType.MIXED,
    output_format=OutputFormat.VBS,
    chunking_strategy=ChunkingStrategy.RANDOM_ORDER,
    randomize_names=True,
    variable_name="data"
)
encoder = ArrayEncoder(config)
result = encoder.generate(payload)
```

---

## Expected Performance

### Throughput by Encoding (Baseline)
| Encoding | Speed | Quality |
|----------|-------|---------|
| HEX | 75 MB/s | Good |
| BASE64 | 50 MB/s | Better compression |
| OCTAL | 15 MB/s | Slow but compact |

### Speed by Chunk Size (10KB Payload)
| Chunk Size | Time | Chunks |
|-----------|------|--------|
| 4 | 913ms | 2500 |
| 32 | 112ms | 313 |
| 128 | 57ms | 79 |
| 512 | 25ms | 20 |

### Memory Usage
| Payload | Memory |
|---------|--------|
| 1 KB | < 1 MB |
| 100 KB | ~0.3 MB |
| 500 KB | ~1.7 MB |

---

## Test Execution Times

| Test Suite | Duration | Tests |
|-----------|----------|-------|
| Comprehensive Payloads | ~5 min | 60+ |
| Performance Benchmarks | ~10 min | 44 |
| Edge Cases | ~3 min | 35+ |
| **All Tests** | **~20 min** | **140+** |

---

## Success Criteria

### All Tests Pass ✓
```
Passed: 140/140
Success Rate: 100%
```

### Performance Acceptable ✓
```
Encoding < 10ms for 100KB
Decoding > 1M chunks/sec
Memory < 5MB for 500KB
```

### Roundtrip Successful ✓
```
Encoded data == Original data
100% match after decode
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Large payload fails | Increase chunk_size |
| Slow encoding | Use BASE64, increase chunk_size |
| High memory | Process smaller chunks |
| Roundtrip fails | Check encoding type matches |
| Invalid output format | Verify output_format parameter |
| Special chars fail | Use appropriate encoding |

---

## File Locations

```
/home/user/sc-generator/
├── test_array_comprehensive_payloads.py      # Comprehensive tests
├── test_array_performance_benchmarks.py      # Performance metrics
├── test_array_edge_cases_integration.py      # Edge cases
├── ARRAY_TEST_SUITE_COMPREHENSIVE.md         # Full documentation
├── ARRAY_TEST_QUICK_REFERENCE.md             # This file
└── benchmark_results.json                     # Generated results
```

---

## Common Test Commands

### Quick Validation (5 min)
```bash
python test_array_comprehensive_payloads.py 2>&1 | tail -20
```

### Full Performance Analysis
```bash
python test_array_performance_benchmarks.py
```

### Check Edge Cases
```bash
python test_array_edge_cases_integration.py 2>&1 | grep -E "✓|✗|Summary"
```

### All with Summary
```bash
python test_array_comprehensive_payloads.py 2>&1 | grep -E "TEST|Passed|Failed"
python test_array_performance_benchmarks.py 2>&1 | grep -E "Total|Results"
python test_array_edge_cases_integration.py 2>&1 | grep -E "Passed|Failed"
```

---

## Output Format Quick Guide

### PYTHON Format
```python
payload = [
    "48656c6c6f",
    "20576f726c64"
]
```

### JSON Format
```json
{
  "payload": ["48656c6c6f", "20576f726c64"],
  "count": 2,
  "encoding": "hex",
  "chunk_size": 16
}
```

### VBS Format
```vbs
Dim payload(1)
payload(0) = "48656c6c6f"
payload(1) = "20576f726c64"
```

### BASH Format
```bash
payload=(
    "48656c6c6f"
    "20576f726c64"
)
```

### POWERSHELL Format
```powershell
$payload = @(
    "48656c6c6f",
    "20576f726c64"
)
```

---

## Payload Size Guidelines

| Size | Typical Content | Recommended Chunk |
|------|-----------------|-------------------|
| < 50B | Short command | 8-16 |
| 50-500B | Command + args | 16-32 |
| 500B-5KB | Script | 32-64 |
| 5-50KB | Large script | 64-128 |
| > 50KB | Binary/archive | 128-256 |

---

## Reading Test Output

### Passed Test
```
✓ Test Name
  Details about test
```

### Failed Test
```
✗ Test Name
  Error message
```

### Summary Line
```
Passed: 60/60
Failed: 0/60
Success Rate: 100.0%
```

### Benchmark Output
```
Payload Size    Time (ms)  Throughput (MB/s)
         100        0.020               4.76 ✓
```

---

## Additional Resources

- **Full Documentation**: `ARRAY_TEST_SUITE_COMPREHENSIVE.md`
- **Encoder Module**: `array_encoder.py`
- **Decoder Module**: `array_decoder.py` (if available)
- **Benchmarks Data**: `benchmark_results.json` (generated)

---

## Contact & Support

For issues or questions about the test suite:
1. Check test output for specific error
2. Review edge cases test results
3. Verify configuration parameters
4. Check benchmark results for performance issues

---

Last Updated: 2026-06-29
Test Suite Version: 1.0
Python Version: 3.6+
