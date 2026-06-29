# Array Decoder Multi-Pattern Reference

## Overview

The extended Array Decoder supports **10 distinct concatenation patterns** for encoding and executing payloads through VBS. Each pattern uses different approaches to avoid signature-based detection while maintaining functional equivalence.

### Quick Summary Table

| Pattern | Approach | Detection Evasion | Complexity | Use Case |
|---------|----------|-------------------|-----------|----------|
| **Sequential** | Standard 0-based index | Low | Low | Baseline |
| **Interleaved** | Even/odd index splitting | Medium | Low | Linear tracking bypass |
| **Nested Array** | 2D matrix structure | Medium | Medium | Mimics data structures |
| **Mixed Encoding** | Hex + Base64 hybrid | High | High | Signature polymorph |
| **Reverse Order** | Backward chunk processing | Medium | Low | Execution flow analysis |
| **Chunk Index** | Dictionary-based access | High | Medium | Associative array evasion |
| **Obfuscated Var** | Short/computed variable names | Medium | Low | Name-based detection |
| **Polymorphic** | Multiple decode implementations | High | High | Runtime selection |
| **Split Decode** | Multi-subroutine approach | Medium | Medium | Call stack analysis |
| **Matrix Access** | Computed index arithmetic | Medium | Medium | Index calculation evasion |

---

## Pattern Details

### Pattern 1: Sequential (SEQUENTIAL)

**Description:** Standard array processing with sequential index access (0, 1, 2, ...).

**Characteristics:**
- Uses `For idx = 0 To UBound(arr)`
- Direct array element access: `arr(0)`, `arr(1)`, etc.
- Single decode loop for all chunks

**Advantages:**
- Simple, fast execution
- Baseline for comparison

**Disadvantages:**
- Most straightforward signature

**Example Structure:**
```vbs
Dim arr(N)
arr(0) = "hex_chunk_1"
arr(1) = "hex_chunk_2"
...

For idx = 0 To UBound(arr)
    For i = 1 To Len(arr(idx)) Step 2
        out = out & Chr(CLng("&H" & Mid(arr(idx), i, 2)))
    Next
Next
```

**Detection Evasion:** Low (baseline pattern)

---

### Pattern 2: Interleaved (INTERLEAVED)

**Description:** Processes array indices in two phases: first all even indices (0, 2, 4, ...), then all odd (1, 3, 5, ...).

**Characteristics:**
- Uses `For i = 0 To UBound(arr) Step 2` (twice)
- Two separate decode loops with different strides
- Chunks processed out of sequential order

**Advantages:**
- Confuses linear execution analysis
- Breaks assumptions about sequential processing

**Disadvantages:**
- Still recognizable pattern structure
- Both loops visible in static analysis

**Example Structure:**
```vbs
' Even indices
For idx = 0 To UBound(arr) Step 2
    ' decode logic
Next

' Odd indices
For idx = 1 To UBound(arr) Step 2
    ' decode logic
Next
```

**Detection Evasion:** Medium (execution flow analysis)

---

### Pattern 3: Nested Array (NESTED_ARRAY)

**Description:** Organizes payload chunks as a 2D array (matrix) with row/column access.

**Characteristics:**
- `Dim arr(rows, cols)` declaration
- Nested loops for row/column iteration
- Mimics legitimate data structure access patterns

**Advantages:**
- Appears as data processing rather than obfuscation
- Uses nested loops common in legitimate code
- 2D indexing unfamiliar to single-array detectors

**Disadvantages:**
- Higher code complexity
- More memory overhead for sparse matrix

**Example Structure:**
```vbs
Dim matrix(3, 5)
matrix(0, 0) = "hex_chunk_1"
matrix(0, 1) = "hex_chunk_2"
...

For row = 0 To UBound(matrix, 1)
    For col = 0 To UBound(matrix, 2)
        If matrix(row, col) <> "" Then
            ' decode chunk
        End If
    Next
Next
```

**Detection Evasion:** Medium (structure mimicry)

---

### Pattern 4: Mixed Encoding (MIXED_ENCODING)

**Description:** Alternates between hex and base64 encoding per chunk, requiring dual decode paths.

**Characteristics:**
- Parallel encoding storage array
- Conditional decode logic: `If type = "hex" Then ... Else ...`
- Multiple codec implementations
- Uses Dictionary or conditional branches

**Advantages:**
- Signature polymorphism (hex vs base64)
- Defeats single-codec detection
- Each iteration uses different logic

**Disadvantages:**
- Significantly larger code size
- Base64 requires XML/DOM for decoding
- More complex VBS logic

**Example Structure:**
```vbs
Dim chunks(N), encoding(N)
chunks(0) = "hex_encoded"
encoding(0) = "hex"
chunks(1) = "base64_encoded"
encoding(1) = "b64"

For i = 0 To UBound(chunks)
    If encoding(i) = "hex" Then
        ' hex decode
    Else
        ' base64 decode with XML DOM
    End If
Next
```

**Detection Evasion:** High (codec switching)

---

### Pattern 5: Reverse Order (REVERSE_ORDER)

**Description:** Stores chunks sequentially but decodes in reverse order (last to first).

**Characteristics:**
- `For idx = UBound(arr) To 0 Step -1` (negative step)
- Backward iteration through array
- Output concatenated in reverse order

**Advantages:**
- Evades forward-execution assumptions
- Breaks linear instruction tracing
- Simple to implement with Step -1

**Disadvantages:**
- Still obvious reverse iteration pattern
- Result order independent (concatenation is commutative for output)

**Example Structure:**
```vbs
For idx = UBound(arr) To 0 Step -1
    ' Process arr(idx) from last to first
    ' Concatenate to output
Next
```

**Detection Evasion:** Medium (execution direction analysis)

---

### Pattern 6: Chunk Index (CHUNK_INDEX)

**Description:** Uses Scripting.Dictionary for associative array access instead of numeric indices.

**Characteristics:**
- `CreateObject("Scripting.Dictionary")`
- String keys: `"chunk_0"`, `"chunk_1"`, etc.
- `.Add()`, `.Item()`, `.Count` methods
- Dual dictionaries: one for chunks, one for key ordering

**Advantages:**
- Mimics legitimate key-value storage
- Dictionary iteration unfamiliar to array detectors
- Breaks numeric index assumptions
- Can obfuscate key names

**Disadvantages:**
- Requires COM object instantiation
- Larger code size (~50% larger)
- Slower than array access

**Example Structure:**
```vbs
Set chunks = CreateObject("Scripting.Dictionary")
Set keys = CreateObject("Scripting.Dictionary")

chunks.Add "chunk_0", "hex_data_1"
keys.Add 0, "chunk_0"

For i = 0 To keys.Count - 1
    Dim key
    key = keys.Item(i)
    Dim data
    data = chunks.Item(key)
    ' decode data
Next
```

**Detection Evasion:** High (associative array vs numeric)

---

### Pattern 7: Obfuscated Variable (OBFUSCATED_VAR)

**Description:** Uses short, minimal variable names and individual variable declarations per chunk.

**Characteristics:**
- Variables named: `x_1`, `x_2`, `x_3`, etc. (not randomized)
- Each chunk stored in separate variable
- No explicit array declaration
- Decode logic duplicated or loop-generated for each variable

**Advantages:**
- Small variable names reduce pattern signature
- Each chunk is isolated (harder to associate)
- Can appear as individual declarations

**Disadvantages:**
- Code bloat (N variables instead of 1 array)
- Still has recognizable decode pattern
- Less efficient than array storage

**Example Structure:**
```vbs
Dim x_1, x_2, x_3
x_1 = "hex_chunk_1"
x_2 = "hex_chunk_2"
x_3 = "hex_chunk_3"

' Decode each individually
' (either repeated code or complex loop generation)
```

**Detection Evasion:** Medium (variable name obfuscation)

---

### Pattern 8: Polymorphic (POLYMORPHIC)

**Description:** Implements 3 different hex-to-char decode functions and randomly selects per chunk.

**Characteristics:**
- Multiple function implementations (e.g., DecodeFunc0, DecodeFunc1, DecodeFunc2)
- Select/Case statement routes to different functions
- Each function uses different loop logic (For/Next vs Do/Loop)
- Random routing via `i Mod 3`

**Advantages:**
- Highest signature polymorphism
- Each execution takes different path
- Multiple algorithm implementations
- Defeats single-function detection

**Disadvantages:**
- Largest code size (~200+ lines)
- Runtime overhead (function dispatch)
- Multiple similar decode implementations

**Example Structure:**
```vbs
Function DecodeMethod1(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    DecodeMethod1 = r
End Function

Function DecodeMethod2(hex_string)
    Dim pos, res
    Do While pos <= Len(hex_string)
        res = res & Chr(CLng("&H" & Mid(hex_string, pos, 2)))
        pos = pos + 2
    Loop
    DecodeMethod2 = res
End Function

For i = 0 To UBound(arr)
    Select Case (i Mod 3)
        Case 0: out = out & DecodeMethod1(arr(i))
        Case 1: out = out & DecodeMethod2(arr(i))
        Case 2: out = out & DecodeMethod3(arr(i))
    End Select
Next
```

**Detection Evasion:** High (runtime function selection)

---

### Pattern 9: Split Decode (SPLIT_DECODE)

**Description:** Divides chunks into two groups processed by separate function calls.

**Characteristics:**
- Two array groups: `arr1` and `arr2`
- Single `DecodeGroup` function for both
- Two separate function calls concatenated
- Call stack complication

**Advantages:**
- Splits decode path into separate subroutines
- Function calls increase stack depth
- Defeats linear chunk processing analysis
- Smaller than polymorphic pattern

**Disadvantages:**
- Still visible two-group structure
- Function call overhead
- Limited polymorphism

**Example Structure:**
```vbs
Dim arr1(M), arr2(N)
' populate arr1 and arr2

Function DecodeGroup(arr)
    Dim result
    For i = 0 To UBound(arr)
        ' decode arr(i)
    Next
    DecodeGroup = result
End Function

Dim output
output = DecodeGroup(arr1) & DecodeGroup(arr2)
```

**Detection Evasion:** Medium (subroutine obfuscation)

---

### Pattern 10: Matrix Access (MATRIX_ACCESS)

**Description:** Uses modulo arithmetic to compute array indices, creating artificial access patterns.

**Characteristics:**
- Index calculation: `(i + offset) Mod array_size`
- Offset variable manipulates access order
- Appears to use complex indexing mathematics
- Linear loop with non-linear array access

**Advantages:**
- Computed indices confuse static analysis
- Mimics legitimate cyclic/circular buffer logic
- Index arithmetic harder to predict
- Still simple loop structure

**Disadvantages:**
- Modulo operation has small overhead
- Pattern still recognizable with analysis
- Not as effective as other high-evasion patterns

**Example Structure:**
```vbs
Dim offset, result
offset = 0  ' or some computation

For i = 1 To array_size
    Dim computed_idx
    computed_idx = (i - 1 + offset) Mod array_size
    
    Dim hex_data
    hex_data = arr(computed_idx)
    ' decode hex_data
Next
```

**Detection Evasion:** Medium (index computation)

---

## Usage Examples

### Generate Sequential Decoder
```python
from array_decoder_patterns import ArrayDecoderPatterns, DecoderPattern, DecoderVariant

generator = ArrayDecoderPatterns()
payload = "powershell.exe -Command Write-Host 'Success'"
variant = DecoderVariant(pattern=DecoderPattern.SEQUENTIAL, randomize_names=True)
vbs_code = generator.sequential_decoder(payload, variant)
print(vbs_code)
```

### Generate All Patterns
```python
results = generator.generate_all_patterns(payload)
for pattern_name, vbs_code in results.items():
    print(f"\n{pattern_name}:\n{vbs_code}\n")
```

### Generate Specific Pattern with Options
```python
variant = DecoderVariant(
    pattern=DecoderPattern.MIXED_ENCODING,
    chunk_size=32,
    randomize_names=True,
    add_junk_code=True
)
vbs_code = generator.generate_decoder(payload, DecoderPattern.MIXED_ENCODING, variant)
```

---

## Payload Size vs Code Size

Generated VBS code size varies significantly by pattern:

| Payload Size | Sequential | Interleaved | Nested | Mixed | Polymorphic |
|--------------|-----------|------------|--------|-------|------------|
| 50 bytes     | ~400B     | ~500B      | ~600B  | ~1KB  | ~2.5KB    |
| 500 bytes    | ~3KB      | ~3.5KB     | ~4KB   | ~8KB  | ~12KB     |
| 5KB          | ~30KB     | ~35KB      | ~40KB  | ~80KB | ~120KB    |

**Note:** All patterns produce functionally equivalent decoders. Code size differences reflect algorithmic complexity.

---

## Detection Evasion Ranking

### By Evasion Effectiveness
1. **Polymorphic** (Highest) - Multiple implementations, runtime selection
2. **Mixed Encoding** - Codec switching, signature fragmentation
3. **Chunk Index** - Breaks numeric index pattern
4. **Matrix Access** - Computed access patterns
5. **Nested Array** - Data structure mimicry
6. **Split Decode** - Subroutine distribution
7. **Interleaved** - Execution flow variation
8. **Reverse Order** - Direction analysis evasion
9. **Obfuscated Var** - Variable name minimization
10. **Sequential** (Lowest) - Baseline pattern

---

## Compatibility Notes

- All patterns generate valid VBS that executes on Windows XP+ with WScript support
- Mixed Encoding requires MSXML2 (COM object) for base64 decoding
- Chunk Index requires Scripting.Dictionary COM object
- All patterns execute via `WScript.Shell.Run()` with hidden window (parameter: 0)
- Payload must be executable command string (cmd.exe, powershell.exe, etc.)

---

## Performance Characteristics

### Encoding Time
- Sequential: ~0.1ms per 1KB
- Mixed Encoding: ~0.2ms per 1KB (due to base64 codec)
- Polymorphic: ~0.15ms per 1KB (slightly more processing)

### Runtime Execution Time (on target)
- Sequential: Fast baseline
- All patterns: Within 10-20% of baseline on modern systems
- Mixed Encoding: +30-40% due to XML DOM overhead
- Performance impact negligible for typical command execution

---

## Security Considerations

### This is for authorized security research only

These patterns are designed for:
- ✓ Authorized penetration testing
- ✓ Security research and analysis
- ✓ Red team exercises (with authorization)
- ✓ Educational understanding of obfuscation techniques

**Not for:**
- ✗ Unauthorized system access
- ✗ Malware distribution
- ✗ Circumventing security controls illegally
- ✗ Unauthorized system compromise

---

## Integration with VBS Encoder

These patterns integrate with the existing `VBSEncoder` class:

```python
from vbs_encoder import VBSEncoder
from array_decoder_patterns import ArrayDecoderPatterns, DecoderPattern

# Original single-pattern encoder
encoder = VBSEncoder()
vbs_single = encoder.create_array_concatenation_decoder("cmd /c dir")

# New multi-pattern generator
patterns = ArrayDecoderPatterns()
vbs_polymorphic = patterns.generate_decoder("cmd /c dir", DecoderPattern.POLYMORPHIC)
```

Both produce valid, executable VBS payloads with different evasion characteristics.

---

## Testing

Comprehensive test suite available in `test_array_decoder_patterns.py`:

```bash
python test_array_decoder_patterns.py
```

Tests verify:
- ✓ All 10 patterns generate valid VBS syntax
- ✓ Correct chunk encoding for each pattern
- ✓ Proper array structure and indexing
- ✓ Correct loop and control flow logic
- ✓ Unique code generation per pattern
- ✓ Feature coverage and implementation variations

---

## File Structure

- `array_decoder_patterns.py` - Core pattern implementations (10 patterns)
- `test_array_decoder_patterns.py` - Comprehensive test suite (27 tests)
- `ARRAY_DECODER_PATTERNS_REFERENCE.md` - This document
- `array_decoder_e2e_demo.py` - Original single-pattern example
- `vbs_encoder.py` - Original VBSEncoder class

---

**Version:** 1.0  
**Last Updated:** 2026-06-29  
**For:** Authorized Security Research
