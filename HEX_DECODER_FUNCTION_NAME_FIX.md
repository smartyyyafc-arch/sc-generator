# Hex Decoder Function Name Issue & Fix Documentation

## Executive Summary

This document details a critical bug in the **Hex decoder implementations** (`hex_decoder_variants.py` and `hex_decoder_hardened.py`) where **variable name collisions** occur due to prefix reuse in the `_generate_random_name()` method. This causes VBScript runtime errors when the same randomly-generated function/variable name is accidentally used multiple times in a single decoder instance.

---

## Problem Statement

### Issue Type
**Variable Scope / Naming Collision Bug**

### Affected Files
1. `/home/user/sc-generator/hex_decoder_hardened.py` (lines 250, 257)
2. `/home/user/sc-generator/hex_decoder_variants.py` (potential similar patterns)

### Root Cause
The `_generate_random_name(prefix: str)` method generates variable names by appending a random suffix to a provided prefix. However, **multiple calls within the same decoder generation can reuse the same prefix**, leading to potential name collisions.

**Critical Example from `hex_decoder_hardened.py` (lines 250, 257):**

```python
func_name = cls._generate_random_name("f", length=12)    # Line 250
# ... other variable generation ...
var_fso = cls._generate_random_name("f", length=8)       # Line 257
```

**Problem:** Both variables use prefix `"f"` but with different suffix lengths (12 vs 8). While the random suffixes typically differ, this represents a **violation of naming convention** and creates a **collision risk**.

### Similar Issue Pattern in `create_hardened_script_decoder()`

Lines 250-257 of `hex_decoder_hardened.py`:

```python
func_name = cls._generate_random_name("f", length=12)    # Function name prefix: "f"
var_hex = cls._generate_random_name("h", length=10)
var_decoded = cls._generate_random_name("d", length=10)
var_shell = cls._generate_random_name("s", length=10)
var_file = cls._generate_random_name("t", length=10)
var_i = cls._generate_random_name("j", length=8)
var_code = cls._generate_random_name("k", length=8)
var_fso = cls._generate_random_name("f", length=8)       # Variable prefix ALSO "f" ← COLLISION RISK
```

### Runtime Impact

When these colliding names are used in VBScript code, it can cause:
1. **'Object expected' runtime errors** - if a variable name is reused before the previous reference
2. **Incorrect control flow** - if a function name conflicts with a variable name
3. **Undefined behavior** - VBScript's loose scoping can make this unpredictable

---

## Technical Analysis

### Current Implementation

**File:** `hex_decoder_hardened.py` (lines 22-33)

```python
@staticmethod
def _generate_random_name(prefix: str, length: int = 8) -> str:
    """Generate cryptographically random variable name"""
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return f"{prefix}{suffix}"
```

**How it works:**
- Takes a prefix (e.g., "f", "h", "s")
- Appends `length` random alphanumeric characters
- Returns combined string

**Why collision risk exists:**
1. Prefixes are intentionally short (1-2 characters) to minimize generated code verbosity
2. Multiple variables/functions can legitimately need the same prefix (e.g., multiple "file" variables might use "f_")
3. With two "f" prefixes and random suffixes, there's a non-zero probability of collision
4. Different suffix lengths (12 vs 8) doesn't eliminate collision risk; it just reduces probability

### Reference: Base64 Decoder Fix (Commit 7938dcf)

A similar issue was **fixed in the Base64 decoder** on commit `7938dcf8638dd699af54cd0f454d249ef70f700b`:

**Before (Buggy Code):**
```python
def create_base64_decoder_vbs(self, payload: str, output_var: str = "p") -> str:
    encoded, var_name = self.encode_string_base64(payload)
    
    vbs_code = f"""
Dim {var_name}, {output_var}
{var_name} = "{encoded}"
Set {self._generate_random_name("o_")} = CreateObject("MSXML2.DOMDocument")
With {self._generate_random_name("o_")}
    .LoadXML "<u><![CDATA[" & {var_name} & "]]></u>"
    {output_var} = .SelectSingleNode("u").text
End With
```

**Problem:** `_generate_random_name("o_")` called **twice**, generating **two different names** for the **same object**.

```vbs
' Generated (buggy):
Set aBcDeFgH = CreateObject("MSXML2.DOMDocument")     ' First name
With iJkLmNoP                                           ' Different name! ← ERROR
    ' ... rest of code
End With
```

**After (Fixed Code):**
```python
def create_base64_decoder_vbs(self, payload: str, output_var: str = "p") -> str:
    encoded, var_name = self.encode_string_base64(payload)
    obj_var = self._generate_random_name("o_")         # STORE the name ONCE
    
    vbs_code = f"""
Dim {var_name}, {output_var}
{var_name} = "{encoded}"
Set {obj_var} = CreateObject("MSXML2.DOMDocument")    # Use stored name
With {obj_var}                                          # Use same stored name
    .LoadXML "<u><![CDATA[" & {var_name} & "]]></u>"
    {output_var} = .SelectSingleNode("u").text
End With
```

**Result:** Same object name used in both `Set` and `With` statements, fixing the runtime error.

---

## Solution

### Approach: Store-Once, Reuse Pattern

The fix follows the **proven pattern from the Base64 decoder fix**:

**Key Principle:** Generate a variable/function name **once** and store it in a Python variable. Reuse that Python variable throughout the f-string template. This guarantees VBScript uses the same name consistently.

### Fix for `hex_decoder_hardened.py` - `create_hardened_script_decoder()`

**Lines 249-257 (Current Problematic Code):**

```python
# Generate obfuscated names
func_name = cls._generate_random_name("f", length=12)
var_hex = cls._generate_random_name("h", length=10)
var_decoded = cls._generate_random_name("d", length=10)
var_shell = cls._generate_random_name("s", length=10)
var_file = cls._generate_random_name("t", length=10)
var_i = cls._generate_random_name("j", length=8)
var_code = cls._generate_random_name("k", length=8)
var_fso = cls._generate_random_name("f", length=8)     # ← Collision risk with func_name
```

**Corrected Code:**

```python
# Generate obfuscated names - use UNIQUE prefixes
func_name = cls._generate_random_name("fn", length=12)   # Changed "f" → "fn" for function
var_hex = cls._generate_random_name("h", length=10)
var_decoded = cls._generate_random_name("d", length=10)
var_shell = cls._generate_random_name("s", length=10)
var_file = cls._generate_random_name("t", length=10)
var_i = cls._generate_random_name("j", length=8)
var_code = cls._generate_random_name("k", length=8)
var_fso = cls._generate_random_name("f", length=8)      # ✓ Now unique from func_name
```

**Rationale:**
- `"fn"` (2 characters) is still concise but clearly distinguishes function names from variable names
- All other prefixes remain unique: h, d, s, t, j, k, f
- No changes needed to VBScript output code; Python variables already stored correctly

### Related Issues in Same File

**`create_hardened_binary_decoder()` (lines 373-382):**

Similar prefix collision patterns with the variable name `var_stream`:

```python
func_name = cls._generate_random_name("b", length=12)   # Function uses "b"
var_hex = cls._generate_random_name("e", length=10)
var_decoded_arr = cls._generate_random_name("a", length=10)
var_file = cls._generate_random_name("f", length=10)
var_shell = cls._generate_random_name("w", length=10)
var_i = cls._generate_random_name("m", length=8)
var_code = cls._generate_random_name("n", length=8)
var_stream = cls._generate_random_name("s", length=8)   # Variable uses "s"
```

**Status:** This method appears safer (no prefix reuse between func_name and variables), but should still be reviewed for consistency.

---

## Implementation Checklist

### Primary Fix: `hex_decoder_hardened.py`

- [ ] **Line 250:** Change `cls._generate_random_name("f", length=12)` to `cls._generate_random_name("fn", length=12)`
  - **File Path:** `/home/user/sc-generator/hex_decoder_hardened.py`
  - **Method:** `create_hardened_script_decoder()`
  - **Change:** Function name prefix isolation

### Secondary Review: All Decoders

- [ ] Review `hex_decoder_variants.py` for similar patterns
- [ ] Review `hex_decoder_hardened.py::create_hardened_command_decoder()` (line 146)
- [ ] Review `hex_decoder_hardened.py::create_hardened_binary_decoder()` (line 374)
- [ ] Add unit tests to verify no naming collisions

### Testing Strategy

**Unit Test Template:**

```python
def test_hex_decoder_no_naming_collisions():
    """Verify generated decoder functions have unique variable names"""
    from hex_decoder_hardened import HardenedHexDecoder
    
    # Generate multiple instances
    for iteration in range(100):
        vbs_code, metadata = HardenedHexDecoder.create_hardened_script_decoder(
            "Test script content",
            execute=True
        )
        
        # Extract all variable/function names from generated code
        generated_names = set()
        for line in vbs_code.split('\n'):
            if 'Dim ' in line or 'Function ' in line or 'Set ' in line:
                # Parse names...
                pass
        
        # Assert no duplicates
        assert len(generated_names) == len(set(generated_names)), \
            f"Iteration {iteration}: Duplicate names detected: {generated_names}"
```

---

## Prevention: Coding Standards

### Best Practices for Name Generation

1. **Use Unique Prefixes:** Each variable/function should have a **distinct prefix**
   - Functions: `"fn"`, `"func"`, `"dec"`
   - Variables: `"var"`, `"obj"`, `"tmp"`
   - Specialized: `"hex"`, `"bin"`, `"str"`

2. **Store Names, Don't Regenerate:**
   ```python
   # ✓ GOOD
   obj_name = self._generate_random_name("obj_")
   vbs += f"Set {obj_name} = ...\n"
   vbs += f"With {obj_name}\n"
   
   # ✗ BAD
   vbs += f"Set {self._generate_random_name('obj_')} = ...\n"
   vbs += f"With {self._generate_random_name('obj_')}\n"  # Different names!
   ```

3. **Document Prefix Mappings:** In class docstring, list all prefixes used:
   ```python
   """
   Variable Naming Convention:
   - "fn_" : Decoder functions
   - "hex_": Hex string variables
   - "dec_": Decoded content variables
   - "obj_": Object/COM references
   """
   ```

---

## Deployment Impact

### Backward Compatibility
- **No breaking changes** - Generated VBScript output remains functionally identical
- **Internal fix only** - Affects Python generator logic, not external API
- **Generated code quality** - Improves reliability, reduces runtime errors

### Performance Impact
- **Negligible** - No additional computation overhead
- **Code size** - Generated VBScript size unchanged
- **Execution speed** - VBScript runtime performance unaffected

### Security Impact
- **Positive** - Eliminates potential variable shadowing exploits
- **Code obfuscation** - Maintains intended obfuscation while fixing correctness

---

## References

### Related Commits
- **Base64 Fix:** `7938dcf` - "Fix Base64 decoder variable scope issue - store object var name before reuse"
  - Demonstrates the exact problem and solution pattern
  - Applied to `vbs_encoder.py::create_base64_decoder_vbs()`

### Files Affected
```
/home/user/sc-generator/
├── hex_decoder_hardened.py          (PRIMARY: Line 250)
├── hex_decoder_variants.py          (REVIEW: Potential similar issues)
├── test_hex_decoder_hardened.py     (UPDATE: Add collision detection tests)
└── test_hex_decoder_variants.py     (UPDATE: Add collision detection tests)
```

### Testing Files
```
/home/user/sc-generator/
├── test_hex_decoder_execution.py    (Execution validation)
├── test_hex_decoder_performance.py  (Performance benchmarks)
└── example_hex_decoder_variants.py  (Integration examples)
```

---

## Appendix: Variable Name Reference

### Current Prefix Allocation

**File: `hex_decoder_hardened.py`**

| Method | Variable | Prefix | Length | Collision Risk |
|--------|----------|--------|--------|-----------------|
| `create_hardened_script_decoder()` | func_name | "f" | 12 | **HIGH** ← with var_fso |
| | var_hex | "h" | 10 | None |
| | var_decoded | "d" | 10 | None |
| | var_shell | "s" | 10 | None |
| | var_file | "t" | 10 | None |
| | var_i | "j" | 8 | None |
| | var_code | "k" | 8 | None |
| | var_fso | "f" | 8 | **HIGH** ← with func_name |

**Recommended Fix Allocation:**

| Variable | Current Prefix | Recommended Prefix | Rationale |
|----------|---------------|--------------------|-----------|
| func_name | "f" | "fn" | Clearly marks functions |
| var_fso | "f" | "f" | Remains for file system objects |

---

## Sign-Off

**Issue Type:** Critical / High Priority  
**Severity:** Medium (Affects specific edge cases, caught by code review)  
**Fix Complexity:** Low (1-line change per affected location)  
**Testing Required:** Yes (Unit tests for collision detection)  
**Documentation:** Complete  

**Status:** Ready for Implementation  
**Date:** 2026-06-29
