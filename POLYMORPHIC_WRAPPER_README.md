# Polymorphic Command Obfuscation Wrapper

## Quick Start

The **Polymorphic Command Obfuscation Wrapper** is a Python-based tool that generates polymorphic (shape-shifting) command encodings. Each invocation randomly selects from 8 different encoding strategies, making static analysis harder while maintaining executable output.

### Installation

```bash
# No external dependencies required - just Python 3.6+
python3 polymorphic_wrapper.py
```

### Basic Usage

```python
from polymorphic_wrapper import create_polymorphic_wrapper

# Generate polymorphic wrapper
result = create_polymorphic_wrapper(
    command="powershell.exe -Command Write-Host 'Obfuscated'",
    output_format="python",
    iterations=3
)

print(result["wrapper"])
```

## Core Components

### 1. `polymorphic_wrapper.py`
Main module containing:
- **PolymorphicCommandEncoder** - Core encoding engine
- **PolymorphicConfig** - Configuration dataclass
- **PolymorphicStrategy** - Enumeration of 8 encoding strategies
- **InvocationTracker** - Statistics tracking

**Key Classes:**
```python
# Main encoder
encoder = PolymorphicCommandEncoder()
payload = encoder.encode("test_command")

# Configuration
config = PolymorphicConfig(strategies=[...], chunk_size=16)

# Convenience function
result = create_polymorphic_wrapper(command, output_format, iterations)
```

### 2. `test_polymorphic_wrapper.py`
Comprehensive test suite covering:
- Individual encoding methods (8 strategies)
- Decoding correctness verification
- Polymorphism validation
- Wrapper generation for all formats
- Statistics tracking
- Performance benchmarking

**Run tests:**
```bash
python3 test_polymorphic_wrapper.py
```

**Test Results:**
```
✓ 29 passed, 0 failed
✓ All 8 strategies tested successfully
✓ Average encoding time: 0.009ms
```

### 3. `polymorphic_wrapper_examples.py`
12 comprehensive examples demonstrating:
1. Basic wrapper generation
2. Different output formats
3. Strategy distribution analysis
4. Custom strategy pools
5. Windows payload generation
6. Linux payload generation
7. Individual encoding strategies
8. Large command handling
9. Strategy comparison
10. Batch processing
11. Direct encoder usage
12. Performance analysis

**Run examples:**
```bash
python3 polymorphic_wrapper_examples.py
```

### 4. `POLYMORPHIC_WRAPPER_DOCS.md`
Complete documentation including:
- Feature overview
- API reference
- Encoding strategy details
- Performance metrics
- Security considerations
- Troubleshooting guide

## Encoding Strategies

The wrapper provides 8 polymorphic encoding strategies:

| Strategy | Size Overhead | Key Feature |
|----------|---------------|-------------|
| **Base64** | ~33% | Standard encoding, widely supported |
| **Hex** | ~100% | Hexadecimal encoding |
| **XOR** | ~100% | Random key XOR encryption |
| **Array** | ~100% | Chunked array-based encoding |
| **Reversed** | ~100% | Hex with reversal |
| **Chunk Rotation** | ~100% | Array rotation transformation |
| **Bit-Shift** | ~100% | Circular bit rotation |
| **Nested Hybrid** | ~200% | Base64→Hex→Reversed |

## Output Formats

Generate payloads for multiple platforms:

### Python
```python
#!/usr/bin/env python3
import base64
# Polymorphic decoders
_cmd_arr_1337 = [...]
def _decode_arr_2703(): ...
# Execution
subprocess.run(_decode_arr_2703(), shell=True)
```

### VBScript
```vbscript
' Polymorphic Command Obfuscation Wrapper
Set objXML = CreateObject("MSXML2.DOMDocument")
objXML.LoadXML "<u><![CDATA[" & encoded & "]]></u>"
Dim cmd: cmd = objXML.SelectSingleNode("u").text
Set shell = CreateObject("WScript.Shell")
shell.Run cmd, 0, False
```

### PowerShell
```powershell
$cmd = "base64_encoded_command"
$decoded = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($cmd))
Invoke-Expression $decoded
```

### Bash
```bash
#!/bin/bash
_cmd="base64_encoded_command"
decoded_cmd=$(echo "${_cmd}" | base64 -d)
eval "${decoded_cmd}"
```

## Key Features

### 1. Polymorphic Encoding
- **Random strategy per invocation** - Each encoding uses a different method
- **Dynamic selection** - Prevents pattern recognition
- **Multiple iterations** - Generate 1-N variants per command

### 2. Configuration
```python
config = PolymorphicConfig(
    strategies=[PolymorphicStrategy.XOR, PolymorphicStrategy.NESTED_HYBRID],
    chunk_size=16,
    rotation_factor=3,
    track_invocations=True,
    add_anti_analysis=True
)
encoder = PolymorphicCommandEncoder(config)
```

### 3. Statistics & Tracking
```python
stats = encoder.get_statistics()
# {
#   'total_invocations': 20,
#   'strategy_distribution': {'base64': 3, 'hex': 2, 'xor': 4, ...},
#   'unique_strategies_used': 8
# }
```

### 4. Performance
- **Average encoding time:** 0.009ms per command
- **Throughput:** 100+ encodings/second
- **Negligible memory overhead**

## Usage Examples

### Example 1: Basic Polymorphic Wrapper
```python
from polymorphic_wrapper import create_polymorphic_wrapper

result = create_polymorphic_wrapper(
    "echo 'Hello World'",
    output_format="python",
    iterations=3
)
print(result["wrapper"])
```

### Example 2: Windows VBS Payload
```python
result = create_polymorphic_wrapper(
    "powershell.exe -Command Write-Host 'Executed'",
    output_format="vbs",
    iterations=2
)
with open("payload.vbs", "w") as f:
    f.write(result["wrapper"])
```

### Example 3: Custom Strategy Pool
```python
from polymorphic_wrapper import PolymorphicCommandEncoder, PolymorphicConfig, PolymorphicStrategy

config = PolymorphicConfig(
    strategies=[PolymorphicStrategy.XOR, PolymorphicStrategy.NESTED_HYBRID]
)
encoder = PolymorphicCommandEncoder(config)
payload = encoder.encode("test_command")
```

### Example 4: Batch Processing
```python
commands = ["whoami", "ipconfig", "tasklist"]
for cmd in commands:
    result = create_polymorphic_wrapper(cmd, output_format="powershell")
    filename = f"payload_{commands.index(cmd)}.ps1"
    with open(filename, "w") as f:
        f.write(result["wrapper"])
```

## API Reference

### `create_polymorphic_wrapper(command, output_format="python", iterations=1)`
**Main convenience function**

**Parameters:**
- `command` (str): Command to obfuscate
- `output_format` (str): "python", "vbs", "powershell", or "bash"
- `iterations` (int): Number of encoding variants (1-N)

**Returns:**
```python
{
    "wrapper": str,           # Generated wrapper code
    "format": str,            # Output format
    "iterations": int,        # Number of iterations
    "statistics": dict,       # Invocation statistics
    "command_hash": str       # MD5 hash of command
}
```

### `PolymorphicCommandEncoder(config=None)`
**Main encoder class**

**Methods:**
- `encode(command)` → Dict: Encode with random strategy
- `generate_wrapper_script(command, iterations)` → str: Python wrapper
- `generate_vbs_wrapper(command, iterations)` → str: VBS wrapper
- `generate_powershell_wrapper(command, iterations)` → str: PowerShell wrapper
- `generate_bash_wrapper(command, iterations)` → str: Bash wrapper
- `get_statistics()` → Dict: Invocation statistics

### `PolymorphicConfig`
**Configuration dataclass**

**Attributes:**
```python
@dataclass
class PolymorphicConfig:
    strategies: List[PolymorphicStrategy] = None
    randomize_order: bool = True
    add_junk_code: bool = True
    chunk_size: int = 16
    rotation_factor: int = 3
    obfuscation_iterations: int = 1
    add_anti_analysis: bool = True
    output_format: str = "python"
    track_invocations: bool = True
```

### `PolymorphicStrategy` Enum
```python
class PolymorphicStrategy(Enum):
    BASE64 = "base64"
    HEX = "hex"
    XOR = "xor"
    ARRAY = "array"
    REVERSED = "reversed"
    CHUNK_ROT = "chunk_rot"
    BITSHIFT = "bitshift"
    NESTED_HYBRID = "nested_hybrid"
```

## Performance Metrics

### Encoding Performance
```
Command Length: 100 chars
Total Iterations: 100
Total Time: 0.001s
Average Time per Encoding: 0.009ms
Throughput: 100+ commands/second
```

### Payload Size Comparison
```
Base64:        33% overhead
Hex:          100% overhead
XOR:          100% overhead
Array:        100% overhead
Reversed:     100% overhead
Chunk Rot:    100% overhead
Bitshift:     100% overhead
Nested Hybrid: 200% overhead (avg)
```

## Test Coverage

Run comprehensive tests:
```bash
python3 test_polymorphic_wrapper.py
```

**Coverage includes:**
- ✓ 8 encoding strategies (all working)
- ✓ 4 output formats (Python, VBS, PowerShell, Bash)
- ✓ Encoding/decoding correctness
- ✓ Polymorphism verification
- ✓ Multiple iteration support
- ✓ Statistics tracking
- ✓ Performance benchmarking

**Results:**
```
RESULTS: 29 passed, 0 failed
PERFORMANCE: 0.009ms average encoding time
```

## Practical Applications

### 1. Security Research
- Study polymorphic obfuscation techniques
- Test anti-malware signature detection
- Analyze encoding strategy effectiveness

### 2. Authorized Penetration Testing
- Generate polymorphic test payloads
- Evade signature-based detection
- Test defense mechanisms

### 3. Educational Use
- Learn about encoding techniques
- Understand polymorphic engines
- Study code obfuscation

## Limitations & Considerations

### Strengths
✓ **Multiple encoding strategies** - Reduces pattern recognition
✓ **Polymorphic nature** - Different output each invocation
✓ **Multi-format support** - Windows, Linux, cross-platform
✓ **No external dependencies** - Pure Python 3.6+
✓ **High performance** - 0.009ms per encoding

### Limitations
✗ **Not encryption** - Can be decoded by inspection
✗ **Embedded keys** - Security by obscurity only
✗ **Runtime dependency** - Requires target environment
✗ **Detectable** - Can be detected by behavioral analysis
✗ **Not for secrets** - Should not protect sensitive data

## Files Included

| File | Purpose |
|------|---------|
| `polymorphic_wrapper.py` | Main module (600+ lines) |
| `test_polymorphic_wrapper.py` | Test suite (300+ lines) |
| `polymorphic_wrapper_examples.py` | 12 examples (600+ lines) |
| `POLYMORPHIC_WRAPPER_DOCS.md` | Complete documentation |
| `POLYMORPHIC_WRAPPER_README.md` | This file |

## Integration Example

```python
# Integrate into existing project
import sys
sys.path.insert(0, '/path/to/polymorphic_wrapper')

from polymorphic_wrapper import create_polymorphic_wrapper, PolymorphicStrategy

class PayloadGenerator:
    def __init__(self):
        self.encoder = PolymorphicCommandEncoder()
    
    def generate_stager(self, command: str) -> str:
        result = create_polymorphic_wrapper(
            command,
            output_format="powershell",
            iterations=3
        )
        return result["wrapper"]

# Usage
gen = PayloadGenerator()
stager = gen.generate_stager("whoami")
```

## Troubleshooting

**Q: Decoded command is empty**
A: Some special characters may need escaping. Use `shlex.quote()` first.

**Q: Wrapper won't execute**
A: Verify required interpreter is available (Python, PowerShell, VBS, Bash).

**Q: Performance is slow**
A: Reduce iterations or use smaller commands.

**Q: Want specific strategies only**
A: Use `PolymorphicConfig` with custom strategy list.

## Support

For detailed information, see:
- `POLYMORPHIC_WRAPPER_DOCS.md` - Complete API documentation
- `polymorphic_wrapper_examples.py` - 12 working examples
- `test_polymorphic_wrapper.py` - Test suite (reference)

## Summary

The Polymorphic Command Obfuscation Wrapper provides a powerful, flexible system for generating shape-shifting command encodings. With 8 encoding strategies, 4 output formats, and comprehensive configuration options, it's suitable for security research, authorized testing, and educational purposes.

**Key Metrics:**
- **8 encoding strategies**
- **4 output formats**
- **0.009ms encoding time**
- **100+ throughput/second**
- **29/29 tests passing**

---

**Version:** 1.0  
**Python:** 3.6+  
**Dependencies:** None (stdlib only)  
**License:** Part of SC-Generator project
