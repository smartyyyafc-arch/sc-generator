# Enhanced Polymorphic Wrapper - Complete Documentation

## Overview

The **Enhanced Polymorphic Wrapper** (`polymorphic_wrapper_enhanced.py`) extends the original polymorphic obfuscation system with advanced evasion techniques including dead code injection, junk code generation, and variable swapping. This creates significantly more complex and harder-to-analyze command execution wrappers.

## Key Features

### 1. Advanced Obfuscation Techniques

#### Dead Code Injection
- **Purpose**: Insert unreachable code blocks that never execute
- **Types**:
  - `if False:` blocks with loop iterations
  - `try/except` blocks with `NotImplementedError()`
  - Unreachable function definitions
- **Impact**: +20-30% code size increase, confuses static analysis

#### Junk Code Injection
- **Purpose**: Add meaningless operations between actual code
- **Types**:
  - Random variable assignments
  - Hash operations on constants
  - Variable flag assignments
- **Impact**: +30% code size increase, dilutes code intent

#### Variable Swapping
- **Purpose**: Rename variables to obscure meaning
- **Implementation**:
  - Generate random names: `_[letter][number][letter]`
  - Maintain functionality while obscuring intent
  - Track swap mappings for consistent replacement
- **Example**: `cmd` → `_Q0m`, `data` → `_w1v`, `key` → `_g2p`

#### Misleading Comments
- **Purpose**: Add comments that describe non-existent operations
- **Examples**:
  - `# Validating integrity check...`
  - `# Synchronizing with remote service`
  - `# Authenticating with key server`
  - `# Compiling bytecode`
- **Impact**: Misdirects analysts and YARA/Sigma rules

#### Decoy Functions
- **Purpose**: Generate unused functions that serve no purpose
- **Characteristics**:
  - Random parameter counts (1-3 parameters)
  - Meaningless operations
  - Always return `None`
  - Have realistic-looking names like `_process_XXXX`

### 2. Polymorphic Encoding Strategies

The enhanced wrapper maintains all 8 encoding strategies from the original:

1. **BASE64** - Standard Base64 encoding with import statements
2. **HEX** - Hexadecimal string encoding
3. **XOR** - XOR cipher with random keys (1-255)
4. **ARRAY** - Chunked hex arrays with joins
5. **REVERSED** - Reversed hex encoding
6. **CHUNK_ROT** - Chunk rotation with configurable factor
7. **BITSHIFT** - Bit rotation with reversible operations
8. **NESTED_HYBRID** - Multi-layer (Base64 → Hex → Reversed)

Each strategy is randomly selected per invocation.

### 3. Multi-Format Output

Generates obfuscated wrappers in:
- **Python** - Full-featured with all obfuscation techniques
- **VBS** - VBScript for Windows compatibility
- **PowerShell** - Native Windows scripting
- **Bash** - Unix/Linux shell scripts

## Configuration

### EnhancedObfuscationConfig

```python
@dataclass
class EnhancedObfuscationConfig:
    strategies: List[PolymorphicStrategy] = None
    randomize_order: bool = True
    add_junk_code: bool = True
    add_dead_code: bool = True
    add_variable_swapping: bool = True
    junk_code_percentage: int = 30  # 30% of code
    dead_code_percentage: int = 20  # 20% dead code blocks
    variable_swap_percentage: int = 40  # 40% variable swapping
    chunk_size: int = 16
    rotation_factor: int = 3
    obfuscation_iterations: int = 1
    add_anti_analysis: bool = True
    output_format: str = "python"
    track_invocations: bool = True
    add_misleading_comments: bool = True
    add_decoy_functions: bool = True
```

## Usage Examples

### Basic Usage

```python
from polymorphic_wrapper_enhanced import create_enhanced_polymorphic_wrapper

command = "whoami"
result = create_enhanced_polymorphic_wrapper(
    command=command,
    output_format="python",
    iterations=3
)

print(result["wrapper"])
print(f"Hash: {result['command_hash']}")
print(f"Techniques: {result['techniques']}")
```

### Advanced Usage with Custom Config

```python
from polymorphic_wrapper_enhanced import (
    EnhancedObfuscationConfig,
    EnhancedPolymorphicEncoder
)

config = EnhancedObfuscationConfig(
    add_junk_code=True,
    add_dead_code=True,
    add_variable_swapping=True,
    add_decoy_functions=True,
    junk_code_percentage=40,  # More junk
    dead_code_percentage=30,  # More dead code
)

encoder = EnhancedPolymorphicEncoder(config)
payload = encoder.encode("calc.exe")

print(payload["decoder_code"])
```

### Generating Multiple Formats

```python
command = "ipconfig /all"

for fmt in ["python", "vbs", "powershell", "bash"]:
    result = create_enhanced_polymorphic_wrapper(
        command=command,
        output_format=fmt,
        iterations=2
    )
    
    with open(f"wrapper.{fmt}", "w") as f:
        f.write(result["wrapper"])
```

## Output Analysis

### Obfuscation Impact Metrics

Based on test results for command `dir /s`:

| Metric | Minimal | Maximum | Increase |
|--------|---------|---------|----------|
| Lines | 6 | 15 | +150% |
| Bytes | 167 | 379 | +127% |
| Functions | 1 | 3-4 | +300% |
| Dead Code Blocks | 0 | 2-3 | - |
| Comments | 1 | 8-10 | +900% |

### Strategy Distribution

Over 50 invocations with maximum randomization:

```
hex         12%
reversed    12%
xor         10%
chunk_rot   18%
bitshift    18%
base64      12%
array       10%
nested_hybrid 8%
```

## Component Details

### JunkCodeGenerator

```python
class JunkCodeGenerator:
    @staticmethod
    def generate_junk_variable_assignments() -> str
    @staticmethod
    def generate_junk_comments() -> List[str]
    @staticmethod
    def generate_dead_code_block() -> str
    @staticmethod
    def generate_decoy_function(func_count: int = 3) -> str
```

### VariableSwapper

```python
class VariableSwapper:
    def generate_swap_name(original_name: str) -> str
    def swap_in_code(code: str, variables: List[str]) -> Tuple[str, Dict]
```

### EnhancedPolymorphicEncoder

```python
class EnhancedPolymorphicEncoder:
    def encode(command: str) -> Dict  # Main encoding
    def generate_enhanced_wrapper_script(command: str, iterations: int) -> str
    def generate_enhanced_vbs_wrapper(command: str, iterations: int) -> str
    def generate_enhanced_powershell_wrapper(command: str, iterations: int) -> str
    def generate_enhanced_bash_wrapper(command: str, iterations: int) -> str
    def get_statistics() -> Dict
```

## Sample Generated Output

### Python Wrapper Structure

```python
#!/usr/bin/env python3
# Advanced Polymorphic Obfuscation Engine v2.0
# Generating 3 encoding variants with multi-layer evasion
import base64
import sys

# Decoy functions (unused)
def _process_9634(p0, p1):
    _y = ''.join([str(j) for j in range(5)])
    return None

# Junk variable assignments
_var_1234 = "debug"
_var_5678 = [156, 254]

# Variant 1: base64
import base64
_cmd_b64_49424 = "cG93ZXJzaGVsbC5leGUgLU5vUHJvZmlsZSAuLi4="
def _decode_b64_83559():
    _x = hash('temp_value')  # Junk code
    # Verifying digital signature (misleading comment)
    return base64.b64decode(_cmd_b64_49424).decode()
    # Dead code below
    if False:
        TiaqIgHLQ = 3
        for _ in range(76):
            TiaqIgHLQ += 76

# Variant 2: array
_cmd_arr_41881 = ["706f7765...", "72736865...", "6c6c2e65..."]
def _decode_arr_40931():
    return ''.join([bytes.fromhex(c).decode() for c in _cmd_arr_41881])

def execute_polymorphic():
    cmd = _decode_b64_83559()
    import subprocess
    subprocess.run(cmd, shell=True)

if __name__ == '__main__':
    execute_polymorphic()
```

## Evasion Capabilities

### What Gets Evaded

1. **Static Analysis**
   - Dead code confuses flow analysis
   - Variable swapping obscures intent
   - Multiple strategies prevent pattern matching

2. **YARA/Sigma Rules**
   - Misleading comments trigger false negatives
   - Junk code increases noise
   - Decoy functions dilute signature detection

3. **String-Based Detection**
   - Command encoding prevents direct string matching
   - Variable swapping obscures command references
   - Multiple layers prevent simple grep detection

4. **Behavioral Analysis**
   - Polymorphic nature defeats replay detection
   - Each invocation generates different encodings
   - Decoy operations confuse intent analysis

### Limitations

- Not suitable for environments with bytecode analysis
- Behavioral endpoints may still detect execution
- Very old or basic static analyzers may be overwhelmed
- Does not encrypt network traffic

## Performance Characteristics

### Size Overhead
- **Minimal obfuscation**: 20-30% increase
- **Maximum obfuscation**: 80-150% increase

### Execution Speed
- **Minimal impact** on command execution
- Decoding overhead: <10ms for typical commands
- Dead code and junk has no runtime impact

### Memory Usage
- Minimal additional memory consumption
- All encoding happens during wrapper generation, not execution

## Comparison with Original Polymorphic Wrapper

| Feature | Original | Enhanced |
|---------|----------|----------|
| Encoding Strategies | 8 | 8 (same) |
| Dead Code Injection | No | Yes |
| Junk Code | Limited | Extensive |
| Variable Swapping | No | Yes |
| Misleading Comments | No | Yes |
| Decoy Functions | No | Yes |
| Code Size Increase | 10-20% | 80-150% |
| Obfuscation Level | Medium | Maximum |

## Testing

Run the comprehensive test suite:

```bash
python3 test_enhanced_polymorphic.py
```

Tests include:
1. Junk code generation
2. Variable swapping verification
3. Single encoding test
4. Obfuscation level comparison
5. Multi-format wrapper generation
6. Strategy distribution analysis
7. Code complexity metrics
8. Syntax validation (all decoders)
9. Evasion feature verification

## Best Practices

### When to Use

✓ Red team operations
✓ Penetration testing (authorized)
✓ Research and analysis
✓ Training and education

### When NOT to Use

✗ Production systems
✗ Unauthorized access
✗ Any illegal activity
✗ Systems without proper authorization

### Recommended Settings

**For Quick Evasion:**
```python
config = EnhancedObfuscationConfig(
    add_junk_code=True,
    add_dead_code=False,
    add_variable_swapping=True,
)
```

**For Maximum Evasion:**
```python
config = EnhancedObfuscationConfig(
    add_junk_code=True,
    add_dead_code=True,
    add_variable_swapping=True,
    add_decoy_functions=True,
    junk_code_percentage=50,
    dead_code_percentage=30,
)
```

**For Stealth:**
```python
config = EnhancedObfuscationConfig(
    add_junk_code=True,
    add_dead_code=True,
    add_variable_swapping=True,
    add_decoy_functions=True,
    add_misleading_comments=True,
)
```

## Files

- **polymorphic_wrapper_enhanced.py** - Main implementation
- **test_enhanced_polymorphic.py** - Comprehensive test suite
- **polymorphic_wrapper.py** - Original wrapper (for reference)

## Return Value Structure

```python
{
    "wrapper": str,           # Generated wrapper code
    "format": str,            # Output format (python/vbs/powershell/bash)
    "iterations": int,        # Number of encoding variants
    "statistics": {
        "total_invocations": int,
        "strategy_distribution": dict,
        "unique_strategies_used": int,
    },
    "command_hash": str,      # MD5 hash of original command
    "obfuscation_level": str, # "MAXIMUM"
    "techniques": List[str],  # Applied obfuscation techniques
}
```

## Troubleshooting

### Syntax Errors in Generated Code
- Ensure all strategies are properly initialized
- Check that comment injection is properly escaped
- Verify dead code injection targets are correct

### Variable Swapping Not Working
- Ensure `add_variable_swapping=True` in config
- Check that variable names are in the swap list
- Verify swapper instance is properly initialized

### Wrapper Won't Execute
- Validate command syntax before encoding
- Check output format matches target environment
- Ensure all dependencies (base64, subprocess, etc.) are available

## Version

**Version**: 2.0 (Enhanced)  
**Based On**: Polymorphic Command Obfuscation Wrapper v1.0  
**Last Updated**: 2024  
**Compatibility**: Python 3.7+
