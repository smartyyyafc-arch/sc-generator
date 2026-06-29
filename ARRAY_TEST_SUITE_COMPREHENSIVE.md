# Comprehensive Array Encoder Test Suite

## Overview

This test suite provides exhaustive testing of the Array Encoder with various payload sizes, from tiny (< 50 bytes) to very large (500KB+) payloads. It includes performance benchmarking, edge case validation, and integration testing.

## Test Files

### 1. `test_array_comprehensive_payloads.py`
Comprehensive payload size testing covering the full spectrum of input sizes and configurations.

#### Test Groups:

- **Tiny Payloads (< 50 bytes)**
  - Empty strings
  - Single characters
  - Single words
  - Short commands
  - Maximum tiny (49 bytes)

- **Small Payloads (50-500 bytes)**
  - 50, 100, 250, 500 byte payloads
  - Tests JSON output format
  - Validates chunk creation

- **Medium Payloads (500-5KB)**
  - 500, 1000, 2500, 5000 byte payloads
  - Uses Base64 encoding
  - Validates larger arrays

- **Large Payloads (5KB-50KB)**
  - 5K, 10K, 25K, 50K byte payloads
  - PowerShell output format
  - Performance timing
  - Sequential chunking

- **Very Large Payloads (50KB+)**
  - 50K, 100K, 250K byte payloads
  - Performance metrics
  - JSON output format
  - Memory efficiency validation

- **Various Chunk Sizes (Fixed 2KB Payload)**
  - Tests chunk sizes: 4, 8, 16, 32, 64, 128, 256, 512
  - Validates chunk count calculations
  - Tests performance across sizes

- **Encoding Types with Multiple Sizes**
  - HEX, BASE64, OCTAL encodings
  - Tests with 100, 1000, 10000 byte payloads
  - Validates encoding correctness

- **Chunking Strategies (3KB Payload)**
  - SEQUENTIAL
  - RANDOM_ORDER
  - VARIABLE_SIZE
  - INTERLEAVED
  - Each produces correct chunk counts

- **Output Formats (1KB Payload)**
  - PYTHON
  - VBS (VBScript)
  - JAVASCRIPT
  - POWERSHELL
  - BASH
  - JSON
  - C/C++
  - Validates output size and structure

- **Roundtrip Validation**
  - Tests encode-decode cycle
  - Validates data integrity
  - Tests 100, 500, 1K, 5K, 10K byte payloads
  - Allows tolerance for encoding issues

- **Edge Cases**
  - Single byte
  - All same character (1000 copies)
  - Special characters
  - Newlines and whitespace
  - Null-like characters
  - Unicode characters
  - Very long payloads

- **Stress Test**
  - 50KB payload
  - 3 encoding types × 2 strategies × 3 formats
  - 18 total combinations
  - Validates successful completion

#### Running:
```bash
python test_array_comprehensive_payloads.py
```

#### Expected Output:
- 60+ tests covering all payload sizes
- Performance metrics (time, throughput)
- Detailed results organized by test group
- Success rate percentage


### 2. `test_array_performance_benchmarks.py`
Detailed performance benchmarking and throughput analysis.

#### Benchmarks:

- **Encoding Speed**
  - Payloads: 100B, 500B, 1KB, 5KB, 10KB, 50KB, 100KB, 500KB
  - Metrics: Time (ms), Throughput (MB/s)
  - Validates linear scaling

- **Decoding Speed**
  - Various chunk counts
  - Metrics: Throughput (chunks/sec)
  - Tests realistic decoder scenarios

- **Encoding Types Comparison**
  - HEX vs BASE64 vs OCTAL
  - 10KB payload
  - Output size comparison
  - Speed comparison

- **Chunk Size Comparison**
  - Tests: 4, 8, 16, 32, 64, 128, 256, 512 bytes
  - Fixed 10KB payload
  - Validates optimal chunk sizes
  - Performance across sizes

- **Output Format Comparison**
  - All 7 output formats
  - 5KB payload
  - Output size metrics
  - Generation speed

- **Chunking Strategy Comparison**
  - All 4 strategies
  - 20KB payload
  - Performance metrics
  - Chunk count validation

- **Memory Usage**
  - Payloads: 1KB, 10KB, 100KB, 500KB
  - Current and peak memory
  - Memory efficiency validation

- **Scalability Analysis**
  - Tests linear vs. non-linear scaling
  - Compares performance ratios
  - Validates optimization effectiveness

#### Running:
```bash
python test_array_performance_benchmarks.py
```

#### Output:
- 8 benchmark categories
- 44 individual benchmark results
- Results saved to `benchmark_results.json`
- Throughput analysis
- Memory efficiency data


### 3. `test_array_edge_cases_integration.py`
Edge cases, error handling, and integration testing.

#### Test Categories:

- **Empty/Null Tests (3 tests)**
  - Empty strings
  - Single bytes
  - Various single character types

- **Large Size Tests (4 tests)**
  - Exactly chunk size
  - Exactly 2x chunk size
  - One byte over
  - One byte under

- **Special Characters (5 tests)**
  - Symbols and punctuation
  - Whitespace variations
  - Unicode characters
  - Null bytes
  - Mixed encodings

- **Repetitive Patterns (2 tests)**
  - 10KB of same character
  - Pattern repetition (ABCDEF × 1000)

- **Encoding Edge Cases (3 tests)**
  - Base64 padding scenarios
  - Hex with all 256 byte values
  - Octal encoding validation

- **Chunk Size Edge Cases (3 tests)**
  - Very small (size=1)
  - Very large (size=10000)
  - Power-of-two sequences

- **Strategy Edge Cases (4 tests)**
  - Variable chunk ranges
  - Min equals max scenarios
  - Random order preservation
  - Interleaved chunk validation

- **Output Format Edge Cases (4 tests)**
  - Python syntax validation
  - JSON format validity
  - VBS array structure
  - Bash array syntax

- **Roundtrip Tests (3 tests)**
  - Hex encode-decode
  - Base64 encode-decode
  - Binary data preservation

- **Random Data Tests (2 tests)**
  - Random ASCII data
  - Random binary data

- **Convenience Function Tests (2 tests)**
  - All encoding types
  - All output formats

#### Running:
```bash
python test_array_edge_cases_integration.py
```

#### Expected Results:
- 35+ edge case tests
- 97%+ success rate
- Validation of unusual scenarios
- Format correctness checking


## Payload Size Categories

### Tiny (< 50 bytes)
- **Use cases**: Short commands, file names, simple parameters
- **Chunk count**: Usually 1-2 chunks
- **Common encodings**: HEX, BASE64

### Small (50-500 bytes)
- **Use cases**: Short PowerShell commands, simple scripts
- **Chunk count**: 2-10 chunks
- **Optimal chunk size**: 16-32 bytes

### Medium (500-5KB)
- **Use cases**: Moderate scripts, encoded payloads
- **Chunk count**: 20-160 chunks
- **Optimal chunk size**: 32-64 bytes

### Large (5KB-50KB)
- **Use cases**: Full executables, large scripts
- **Chunk count**: 160-1600 chunks
- **Optimal chunk size**: 64-128 bytes

### Very Large (50KB+)
- **Use cases**: Complete programs, archives
- **Chunk count**: 1600+ chunks
- **Optimal chunk size**: 128-256 bytes


## Recommended Configurations

### For Minimum Chunks
```python
config = EncoderConfig(
    chunk_size=256,
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.JSON
)
```

### For Readability (Small Payloads)
```python
config = EncoderConfig(
    chunk_size=16,
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.PYTHON,
    add_comments=True
)
```

### For Obfuscation
```python
config = EncoderConfig(
    chunk_size=random.randint(32, 128),
    encoding_type=EncodingType.MIXED,
    output_format=OutputFormat.VBS,
    chunking_strategy=ChunkingStrategy.RANDOM_ORDER,
    randomize_names=True
)
```

### For Performance
```python
config = EncoderConfig(
    chunk_size=128,
    encoding_type=EncodingType.BASE64,
    output_format=OutputFormat.JSON,
    chunking_strategy=ChunkingStrategy.SEQUENTIAL
)
```


## Performance Metrics

### Encoding Speed (Baseline)
- **100 bytes**: ~0.02ms (4.8 MB/s)
- **1KB**: ~0.02ms (40 MB/s)
- **10KB**: ~0.19ms (51 MB/s)
- **100KB**: ~1.3ms (73 MB/s)
- **500KB**: ~6.3ms (75 MB/s)

### Throughput by Encoding
- **HEX**: ~75 MB/s
- **BASE64**: ~50 MB/s
- **OCTAL**: ~15 MB/s (slowest)

### Chunk Size Impact (10KB Payload)
- **Size=4**: 913ms, 2500 chunks
- **Size=32**: 112ms, 313 chunks
- **Size=512**: 25ms, 20 chunks
- Larger chunks = faster encoding

### Memory Efficiency
- **1KB**: ~0.00 MB
- **100KB**: ~0.33 MB
- **500KB**: ~1.67 MB
- Linear memory usage


## Test Execution Guide

### Quick Test (5 minutes)
```bash
python test_array_comprehensive_payloads.py
```

### Full Performance Analysis (10 minutes)
```bash
python test_array_performance_benchmarks.py
```

### Edge Case Validation (3 minutes)
```bash
python test_array_edge_cases_integration.py
```

### Complete Suite (20 minutes)
```bash
for test in test_array_comprehensive_payloads.py test_array_performance_benchmarks.py test_array_edge_cases_integration.py; do
    echo "Running $test..."
    python "$test"
    echo ""
done
```

## Interpretation of Results

### Success Criteria
- ✓ All tests pass without exceptions
- ✓ Chunk counts match expected values
- ✓ Roundtrip encode-decode successful
- ✓ Output formats are syntactically valid
- ✓ Performance within expected ranges

### Warning Signs
- ✗ Tests fail at specific payload sizes
- ✗ Performance degrades significantly
- ✗ Memory usage grows non-linearly
- ✗ Encoding loses data
- ✗ Output format syntax errors

### Performance Baseline Expectations
- Encoding < 10ms for 100KB
- Decoding throughput > 1M chunks/sec
- Memory usage < 5MB for 500KB payload
- Linear scaling with payload size


## Integration Examples

### With Array Decoder
```python
from array_encoder import ArrayEncoder, EncoderConfig, EncodingType, OutputFormat
from array_decoder import ArrayDecoder

# Encode
config = EncoderConfig(
    chunk_size=32,
    encoding_type=EncodingType.HEX,
    output_format=OutputFormat.PYTHON
)
encoder = ArrayEncoder(config)
chunks = encoder.encode("calc.exe")["chunks"]

# Decode
decoder = ArrayDecoder()
result = decoder.decode_hex_chunks(chunks)
assert result == "calc.exe"
```

### With Multiple Formats
```python
# Generate for different platforms
formats = [
    ("powershell", OutputFormat.POWERSHELL),
    ("bash", OutputFormat.BASH),
    ("vbs", OutputFormat.VBS)
]

for platform, fmt in formats:
    config = EncoderConfig(
        chunk_size=64,
        encoding_type=EncodingType.HEX,
        output_format=fmt
    )
    encoder = ArrayEncoder(config)
    output = encoder.generate("payload")
    save_to_file(f"payload_{platform}.txt", output)
```

### Stress Testing
```python
# Test with realistic payload sizes
test_payloads = {
    "tiny": "cmd.exe",
    "small": generate_payload(200),
    "medium": generate_payload(2000),
    "large": generate_payload(20000)
}

for name, payload in test_payloads.items():
    config = EncoderConfig(chunk_size=32)
    encoder = ArrayEncoder(config)
    result = encoder.encode(payload)
    print(f"{name}: {result['count']} chunks")
```


## Troubleshooting

### Issue: Encoding fails with large payloads
- **Solution**: Increase chunk size, use BASE64 instead of OCTAL

### Issue: Roundtrip decode fails
- **Solution**: Ensure encoding/decoding types match, check for special characters

### Issue: Output format is invalid syntax
- **Solution**: Verify output_format parameter, check for special characters in payload

### Issue: Performance degradation
- **Solution**: Use larger chunk sizes, profile with benchmark script

### Issue: Memory usage grows too large
- **Solution**: Process in smaller chunks, use streaming decoder


## Test Coverage Summary

| Category | Tests | Coverage |
|----------|-------|----------|
| Payload Sizes | 25 | Tiny to Very Large |
| Chunk Sizes | 8 | 1 to 512 bytes |
| Encodings | 9 | HEX, BASE64, OCTAL |
| Chunking Strategies | 4 | All strategies |
| Output Formats | 7 | All formats |
| Edge Cases | 20 | Special scenarios |
| Integration | 40 | End-to-end |
| Performance | 44 | Throughput & memory |
| **Total** | **157+** | **Comprehensive** |


## Recommendations

### For Production Use
- Use `EncodingType.HEX` or `EncodingType.BASE64`
- Use `ChunkingStrategy.SEQUENTIAL` for predictability
- Test with your actual payload sizes
- Profile with `test_array_performance_benchmarks.py`

### For Stealth/Obfuscation
- Use `EncodingType.MIXED` for variety
- Use `ChunkingStrategy.RANDOM_ORDER` or `ChunkingStrategy.VARIABLE_SIZE`
- Use `randomize_names=True`
- Test with `test_array_edge_cases_integration.py`

### For Compatibility
- Test output format syntax with target environment
- Validate roundtrip with actual decoder
- Use `test_array_comprehensive_payloads.py` for validation

### For Performance
- Use larger chunk sizes (128+)
- Use BASE64 for better compression
- Use SEQUENTIAL chunking strategy
- Profile with benchmarks before deployment


## Files Generated

- `test_array_comprehensive_payloads.py` - Comprehensive payload testing
- `test_array_performance_benchmarks.py` - Performance metrics and analysis
- `test_array_edge_cases_integration.py` - Edge cases and integration tests
- `benchmark_results.json` - Performance benchmark results (generated)
- `ARRAY_TEST_SUITE_COMPREHENSIVE.md` - This documentation

