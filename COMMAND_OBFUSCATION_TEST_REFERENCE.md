# Command Obfuscation Test Suite - Detailed Reference

## Quick Start

```bash
# Run all tests
python3 -m unittest test_command_obfuscation_comprehensive -v

# Expected output: Ran 81 tests in ~0.01s, OK
```

---

## Test Classes

### 1. TestBase64EncoderComprehensive

**Purpose**: Validate base64 encoding robustness

#### Tests
| Test Name | Input | Validates |
|-----------|-------|-----------|
| test_empty_command | "" | Empty string handling |
| test_single_character | "a" | Single byte encoding |
| test_unicode_characters | "echo 'Ñoño café'" | Unicode support |
| test_special_shell_characters | Various shell commands | Shell metacharacter preservation |
| test_newlines_and_tabs | "echo hello\necho world\ttest" | Whitespace preservation |
| test_base64_padding_variants | Strings of length 1-100 | Padding correctness |
| test_metadata_accuracy | "test command" | Length tracking |
| test_variable_name_randomization | "test" (5x) | Name uniqueness |
| test_decoder_code_syntax | "test" | Python compilability |
| test_large_command_encoding | 10KB+ command | Large data handling |

**Key Assertions**:
```python
# Round-trip accuracy
decoded = base64.b64decode(encoded).decode()
assert decoded == original

# Metadata validation
assert metadata['original_length'] == len(command)
assert metadata['encoded_length'] == len(encoded)

# Code syntax
compile(decoder_code, '<string>', 'exec')
```

---

### 2. TestHexEncoderComprehensive

**Purpose**: Validate hex encoding correctness

#### Tests
| Test Name | Focus |
|-----------|-------|
| test_hex_format_validation | Valid hex string output |
| test_hex_case_insensitivity | Case-independent decoding |
| test_null_bytes_handling | Binary data robustness |
| test_chunk_size_configuration | Configuration tracking |
| test_hex_decoder_code_generation | Code generation |
| test_very_long_hex_string | 50KB+ hex strings |

**Example**:
```python
encoded = "7465737420636f6d6d616e64"  # "test command" in hex
decoded = bytes.fromhex(encoded).decode()
assert decoded == "test command"
```

---

### 3. TestXOREncoderComprehensive

**Purpose**: Validate XOR key derivation and encoding

#### Tests
| Test Name | Validates |
|-----------|-----------|
| test_xor_key_range | Key is 0-255 |
| test_xor_deterministic_encoding | Same input → same key |
| test_xor_roundtrip | Full encode-decode cycle |
| test_xor_with_all_byte_values | All byte values (0-255) |
| test_xor_decoder_code_generation | Code syntax |
| test_xor_with_custom_key | Custom key support |
| test_xor_special_characters | Special char handling |

**XOR Example**:
```python
# Encode: each byte XORed with key
# Decode: XOR same bytes with same key again
encoded_byte = original_byte ^ key
decoded_byte = encoded_byte ^ key  # Returns original
```

---

### 4. TestArrayEncoderComprehensive

**Purpose**: Validate chunking and array-based encoding

#### Tests
| Test Name | Tests |
|-----------|-------|
| test_chunk_size_varies | Chunk sizes: 1, 4, 8, 16, 32, 100 |
| test_chunk_reconstruction | Reassembly accuracy |
| test_chunk_count_accuracy | Correct count calculation |
| test_single_chunk | cmd < chunk_size |
| test_exact_chunk_boundary | cmd == chunk_size |
| test_array_decoder_code_generation | Code validity |

**Chunk Example**:
```python
# With chunk_size=5, "12345678901234567890" produces:
# ['12345', '67890', '12345', '67890']
# Each chunk hex-encoded separately
```

---

### 5. TestNestedEncoderComprehensive

**Purpose**: Validate multi-layer encoding (base64 → hex → reverse)

#### Tests
| Test Name | Validates |
|-----------|-----------|
| test_layer_sequence | Order: base64, hex, reverse |
| test_layer_lengths_increase | Size progression |
| test_nested_decode_process | Layer unwrapping |
| test_nested_decoder_code_execution_structure | Code structure |
| test_nested_with_special_characters | Special chars |

**Layer Example**:
```
Original:       "test"
Layer 1 (b64):  "dGVzdA=="
Layer 2 (hex):  "6447567a4141"  (length doubled by hex encoding)
Layer 3 (rev):  "1141a7z76d64"  (reversed)
```

---

### 6. TestPolymorphicEncoderComprehensive

**Purpose**: Validate random encoder selection

#### Tests
| Test Name | Expected Behavior |
|-----------|------------------|
| test_different_encodings_produced | Multiple encoder types selected over 20 iterations |
| test_polymorphic_key_generated | Key always 1000-9999 range |
| test_all_encoder_types_used | All 4 types used over 100 iterations |

**Distribution**:
```
Over 100 iterations, expects ~25 of each:
- Base64CommandEncoder
- HexCommandEncoder
- XORCommandEncoder
- ArrayCommandEncoder
```

---

### 7. TestCommandStringObfuscatorComprehensive

**Purpose**: Main obfuscator integration tests

#### Payload Generation Tests

**VBS Base64**:
```vbscript
Set obj = CreateObject("MSXML2.DOMDocument")
With obj
    .LoadXML "<u><![CDATA[" & encoded_data & "]]></u>"
    decoded_cmd = .SelectSingleNode("u").text
End With
```

**VBS Hex**:
```vbscript
Function DecodeHex(h)
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
End Function
```

**VBS Array**:
```vbscript
Dim arr(n)
arr(0) = "first_chunk_hex"
arr(1) = "second_chunk_hex"
' ... decoded with DecodeArray function
```

**PowerShell**:
```powershell
$decoded = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($cmd))
Invoke-Expression $decoded
```

**Bash**:
```bash
#!/bin/bash
decoded_cmd=$(echo "$encoded" | base64 -d)
eval "$decoded_cmd"
```

**Python**:
```python
#!/usr/bin/env python3
# decoder code here
subprocess.run(command, shell=True)
```

---

### 8. TestEdgeCases

**Purpose**: Boundary condition testing

#### Test Scenarios

| Test | Input | Expected |
|------|-------|----------|
| test_empty_string_all_methods | "" | Encodes successfully |
| test_very_long_command | 100KB+ | Encodes without error |
| test_binary_like_strings | "\x00\x01\x02" | Handled gracefully |
| test_only_special_characters | "!@#$%^&*()" | Encoded intact |
| test_only_whitespace | " \t\n\r" | Preserved |

---

### 9. TestPerformance

**Purpose**: Performance regression detection

#### Benchmarks

| Test | Iterations | Limit | Typical |
|------|------------|-------|---------|
| test_encoding_speed_base64 | 100 | < 1.0s | ~0.01s |
| test_encoding_speed_hex | 100 | < 1.0s | ~0.01s |
| test_encoding_speed_nested | 50 | < 2.0s | ~0.02s |
| test_payload_generation_speed | 50 × 3 | < 2.0s | ~0.05s |

**Sample Timing**:
```
test_encoding_speed_base64 ... ok (0.001s)
test_encoding_speed_hex ... ok (0.001s)
test_encoding_speed_nested ... ok (0.005s)
test_payload_generation_speed ... ok (0.020s)
```

---

### 10. TestSecurityProperties

**Purpose**: Verify obfuscation effectiveness

#### Tests

| Test | Validates |
|------|-----------|
| test_encoded_data_differs_from_original | encoded ≠ original |
| test_variable_names_are_randomized | 5 different var names |
| test_polymorphic_prevents_detection | 20 unique encoded variants |

---

### 11. TestComplexCommands

**Purpose**: Real-world command robustness

#### Commands Tested

**PowerShell**:
```powershell
powershell.exe -NoProfile -WindowStyle Hidden -Command "Get-Process | ForEach-Object { $_.Kill() }"
```

**CMD**:
```cmd
cmd.exe /c "for /L %i in (1,1,10) do @echo %i"
```

**Bash**:
```bash
bash -c "for i in {1..100}; do curl -s http://target.com/api?id=$i | jq . ; done"
```

**With Nested Quotes**:
```cmd
cmd.exe /c 'echo "test" && powershell -Command "'Get-ChildItem'\"'
```

**With Environment Variables**:
```bash
echo $PATH && echo %SYSTEMROOT% && echo ${HOME}
```

**With Pipe Operators**:
```bash
cat /etc/passwd | grep root | awk -F: '{print $1}'
```

---

### 12. TestConfigurationOptions

**Purpose**: Configuration variation testing

#### Obfuscation Levels

| Level | Purpose | Use Case |
|-------|---------|----------|
| 1 | Minimal | Speed priority |
| 2 | Light | Basic obfuscation |
| 3 | Medium | Balanced (default) |
| 4 | Heavy | Strong obfuscation |
| 5 | Maximum | Nested encoding |

#### Randomization Options

```python
# Randomized names (default)
b64_aB3Xk8 = "..."  # Different each time
decode_b64_Lm9pQ = lambda x: ...

# Deterministic names
b64_1 = "..."       # Same each time
decode_b64_2 = lambda x: ...
```

---

### 13. TestIntegration

**Purpose**: Cross-component functionality

#### Round-Trip Tests

All 4 methods verified:

```python
# Base64
assert base64.b64decode(encoded).decode() == original

# Hex
assert bytes.fromhex(encoded).decode() == original

# XOR
key = metadata['xor_key']
assert bytes([int(encoded[i:i+2], 16) ^ key for i in range(0, len(encoded), 2)]).decode() == original

# Array
assert ''.join([bytes.fromhex(c).decode() for c in chunks]) == original
```

#### Sequential Operations

```python
obfuscator.obfuscate_command("command1")
obfuscator.obfuscate_command("command2")
obfuscator.obfuscate_command("command3")
# History length should be 3
```

---

### 14. TestConvenienceFunctions

**Purpose**: Shortcut function validation

#### Functions Tested

```python
# Quick encoding
encode_command("test", EncodingMethod.BASE64)

# Platform payloads
encode_to_vbs("test")
encode_to_powershell("test")
encode_to_bash("test")
```

---

### 15. TestErrorHandling

**Purpose**: Robustness against edge config values

| Test | Config | Expected |
|------|--------|----------|
| test_invalid_config_values | obfuscation_level=10 | Handled gracefully |
| test_large_chunk_size | chunk_size=10000 | Works correctly |
| test_small_chunk_size | chunk_size=1 | Works correctly |

---

## Test Execution Examples

### Example 1: Basic Execution
```bash
$ python3 -m unittest test_command_obfuscation_comprehensive -v

test_all_encoding_methods_supported (test_command_obfuscation_comprehensive.TestCommandStringObfuscatorComprehensive) ... ok
test_base64_padding_variants (test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive) ... ok
test_bash_payload_structure (test_command_obfuscation_comprehensive.TestCommandStringObfuscatorComprehensive) ... ok
...
Ran 81 tests in 0.009s
OK
```

### Example 2: Single Test Class
```bash
$ python3 -m unittest test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive -v

test_base64_padding_variants (test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive) ... ok
test_decoder_code_syntax (test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive) ... ok
test_empty_command (test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive) ... ok
test_large_command_encoding (test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive) ... ok
test_metadata_accuracy (test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive) ... ok
test_newlines_and_tabs (test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive) ... ok
test_single_character (test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive) ... ok
test_special_shell_characters (test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive) ... ok
test_unicode_characters (test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive) ... ok
test_variable_name_randomization (test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive) ... ok
Ran 10 tests in 0.001s
OK
```

### Example 3: Single Test
```bash
$ python3 -m unittest test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive.test_unicode_characters -v

test_unicode_characters (test_command_obfuscation_comprehensive.TestBase64EncoderComprehensive) ... ok
Ran 1 test in 0.001s
OK
```

---

## Test Data

### Sample Commands Tested

```python
# Simple
"echo hello"
"test"

# Complex PowerShell
'powershell.exe -NoProfile -WindowStyle Hidden -Command "Write-Host \'Obfuscated\'"'

# CMD with operators
'cmd.exe /c "echo test > file.txt && type file.txt"'

# Bash with pipes
"cat /etc/passwd | grep root | awk -F: '{print $1}'"

# With environment variables
"echo $PATH && echo %SYSTEMROOT% && echo ${HOME}"

# Large (100+ repetitions)
"powershell.exe " + " ".join(["-CommandParameter" for _ in range(100)])
```

### Sample Encoded Outputs

**Base64 Example**:
```
Input:  "test"
Output: "dGVzdA=="
Metadata:
  method: "base64"
  original_length: 4
  encoded_length: 8
  variable_name: "b64_aB3Xk8"
  decoder_name: "decode_b64_Lm9pQ"
```

**Hex Example**:
```
Input:  "test"
Output: "74657374"
Metadata:
  method: "hex"
  original_length: 4
  encoded_length: 8
  chunk_size: 16
```

**XOR Example**:
```
Input:  "test"
Key:    246 (derived from MD5 hash)
Output: "82938582" (hex of XORed bytes)
Metadata:
  method: "xor"
  xor_key: 246
  original_length: 4
  encoded_length: 8
```

**Nested Example**:
```
Input:     "test"
Layer1:    "dGVzdA==" (base64)
Layer2:    "6447567a4141" (hex of base64)
Layer3:    "1141a7z76d64" (reversed hex)
```

---

## Maintenance Notes

### Adding New Tests

1. Choose appropriate test class or create new one
2. Follow naming: `test_<what_is_being_tested>`
3. Include docstring describing test purpose
4. Use `subTest()` for parameterized tests
5. Keep tests focused and independent

### Debugging Failed Tests

```bash
# Run with more details
python3 -m unittest test_command_obfuscation_comprehensive.TestName.test_name -v

# Run with traceback
python3 -m unittest test_command_obfuscation_comprehensive --debug
```

### Performance Regression

If tests start timing out:
```bash
# Time the tests
time python3 -m unittest test_command_obfuscation_comprehensive

# Profile specific encoder
python3 -m cProfile test_command_obfuscation_comprehensive
```

---

## Expected Test Duration

- **Total suite**: ~10ms on modern hardware
- **Base64 tests**: ~1ms
- **Performance tests**: ~50ms (dominated by timing loops)
- **All other tests**: ~50ms combined

---

Last Updated: 2026-06-29
