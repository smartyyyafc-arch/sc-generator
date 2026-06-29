# True Polymorphic Code Generation Engine

## Overview

The **True Polymorphic Code Generation Engine** (`polymorphic_engine.py`) is an advanced code generation system that creates **completely different code structures with each invocation** - not just variable name changes, but fundamentally different algorithms, control flows, and encoding strategies.

## What Makes It "True Polymorphic"

Unlike simple polymorphism that just randomizes variable names, this engine:

✓ **Different algorithms every run**: Randomly selects from 10 completely different encoding techniques  
✓ **Different control flows**: Wraps code in sequential, conditional, loop, or state machine patterns  
✓ **Different data representations**: Uses hex strings, byte arrays, or other formats  
✓ **Different variable names**: Generates random identifiers with unique counters  
✓ **Different code lengths**: Varies from ~500 to 1600+ bytes per generation  
✓ **Multi-stage encoding**: Chains multiple algorithms for deeper obfuscation  

## Files Included

| File | Purpose |
|------|---------|
| `polymorphic_engine.py` | Core engine implementation |
| `polymorphic_examples.py` | 9 practical usage examples |
| `test_polymorphic_engine.py` | 36-test comprehensive test suite |
| `POLYMORPHIC_ENGINE_GUIDE.md` | Detailed technical guide |
| `POLYMORPHIC_ENGINE_README.md` | This file |

## Quick Start

### Basic Usage

```python
from polymorphic_engine import PolymorphicCodeGenerator, PolymorphicConfig

# Create engine
config = PolymorphicConfig(complexity_level=4)
engine = PolymorphicCodeGenerator(config)

# Generate polymorphic script
command = "whoami"
script = engine.generate_complete_polymorphic_script(command)
print(script)
```

### Generate Multiple Variants

```python
# Generate 5 completely different versions of the same command
for i in range(5):
    engine = PolymorphicCodeGenerator()  # Fresh engine each time
    script = engine.generate_complete_polymorphic_script(command)
    with open(f"variant_{i+1}.py", "w") as f:
        f.write(script)
```

### Multi-Stage Polymorphic Payloads

```python
# 3-stage encoding: each stage uses different algorithm
engine = PolymorphicCodeGenerator()
script = engine.generate_multi_stage_polymorphic(
    payload="malware.exe",
    stages=3
)
print(script)
```

## Supported Encoding Algorithms

The engine randomly selects from these 10 algorithms:

### 1. **Linear XOR** (linear_xor)
- Random key (1-255) + random offset (0-255)
- Fast, simple XOR decoding
- ~530 bytes

### 2. **Bitwise Rotation** (bitwise_rot)
- Rotates each byte left by 1-7 positions
- Rotates back in decoder
- ~540 bytes

### 3. **Mathematical Offset** (math_offset)
- Multiplies bytes by random odd number
- Uses modular inverse for decoding
- ~550 bytes

### 4. **Interleave Reverse** (interleave_reverse)
- Splits data by even/odd indices
- Reverses and re-interleaves
- ~590 bytes

### 5. **Lookup Table** (lookup_table)
- Random 256-byte permutation table
- Each byte mapped through table
- ~1650 bytes (includes full table)

### 6. **Chaotic Shuffle** (chaotic_shuffle)
- Random byte position permutation
- Stores shuffle indices for decoding
- ~670 bytes

### 7. **Wave Pattern** (wave_pattern)
- Adds pseudo-random wave amplitude
- Different amplitude each run
- ~550 bytes

### 8. **Prime Modulo** (prime_modulo)
- Encodes using random prime (2-71)
- Modulo arithmetic decoding
- ~520 bytes

### 9. **Fibonacci Sequence** (fibonacci_sequence)
- Encodes using Fibonacci numbers
- Different length sequences each run
- ~600 bytes

### 10. **Recursive Split** (recursive_split)
- Recursively splits and reorders data
- Up to 3 levels deep
- ~500 bytes

## Configuration Options

```python
config = PolymorphicConfig(
    seed=None,                          # None = truly random
    algorithm_variants=3,               # Mix up to N algorithms
    control_flow_patterns=2,            # Wrap in 1-2 control flow patterns
    obfuscation_techniques=3,           # Apply N obfuscation methods
    target_language="python",           # Target language (python, csharp, vb)
    complexity_level=3,                 # 1-5 (higher = more complex)
    include_comments=False              # Add code comments
)
```

## Control Flow Patterns

Code can be wrapped in different control structures:

### Sequential
Direct execution, no extra wrappers:
```python
encoded_X = bytes([...])
decoded = decode(encoded_X)
```

### Conditional
Wrapped in if/else with opaque predicate:
```python
if condition_var:
    encoded_X = bytes([...])
    decoded = decode(encoded_X)
else:
    dummy = None
```

### Loop
Wrapped in loop (runs once):
```python
for i in range(1):
    encoded_X = bytes([...])
    decoded = decode(encoded_X)
```

### State Machine
Wrapped in state machine pattern:
```python
state = 0
while state == 0:
    encoded_X = bytes([...])
    decoded = decode(encoded_X)
    state = 1
```

## API Reference

### PolymorphicCodeGenerator

#### Methods

**`encode_data(data: bytes) -> Tuple[bytes, Dict, str]`**
- Encodes data with random algorithm
- Returns: (encoded_bytes, metadata, algorithm_name)

**`generate_polymorphic_decoder(encoded_data: bytes, metadata: Dict) -> str`**
- Generates Python decoder code
- Returns: decoder code string

**`generate_complete_polymorphic_script(command: str) -> str`**
- Generates complete executable script
- Returns: full Python script

**`generate_multi_stage_polymorphic(payload: str, stages: int) -> str`**
- Generates N-stage polymorphic payload
- Each stage uses different algorithm
- Returns: multi-stage Python script

**`get_generation_info() -> Dict[str, Any]`**
- Returns metadata about generated code
- Includes variables_generated, complexity_level, etc.

## Examples

### Example 1: Batch Generation for Distribution

```python
# Generate 10 different variants for distribution
for i in range(10):
    engine = PolymorphicCodeGenerator()
    script = engine.generate_complete_polymorphic_script("whoami")
    with open(f"payload_{i:02d}.py", "w") as f:
        f.write(script)
```

### Example 2: Payload Detection Evasion

```python
# Same payload, completely different encodings each run
payload = "rundll32.exe shell32.dll"

for i in range(10):
    engine = PolymorphicCodeGenerator()
    encoded, metadata, algo = engine.encode_data(payload.encode())
    print(f"Variant {i+1}: {algo} → {encoded.hex()[:40]}...")
    # Each output is unique, defeating static signatures
```

### Example 3: Multi-Stage Encoding

```python
# 5-stage polymorphic encoding
engine = PolymorphicCodeGenerator()
script = engine.generate_multi_stage_polymorphic(
    payload="calc.exe",
    stages=5  # More stages = stronger obfuscation
)
print(script)
```

### Example 4: Custom Configuration

```python
# Minimum complexity
config_light = PolymorphicConfig(complexity_level=1)
engine_light = PolymorphicCodeGenerator(config_light)

# Maximum complexity
config_heavy = PolymorphicConfig(complexity_level=5)
engine_heavy = PolymorphicCodeGenerator(config_heavy)
```

## Running Examples

```bash
# Run all 9 examples with detailed output
python3 polymorphic_examples.py

# Examples included:
# 1. Basic Polymorphic Generation
# 2. Polymorphic Data Encoding
# 3. Multi-Stage Polymorphic Encoding
# 4. Same Command, Different Generations
# 5. Configuration Complexity Levels
# 6. Batch Generation for Distribution
# 7. Payload Detection Evasion
# 8. Reproducible Generation with Seed
# 9. Algorithm Distribution Analysis
```

## Running Tests

```bash
# Run full test suite
python3 test_polymorphic_engine.py

# Test Summary:
# ✓ 36 tests
# ✓ 10 encoding algorithms
# ✓ 4 control flow patterns
# ✓ Multiple data length ranges
# ✓ Configuration variations
# ✓ Decoder generation
# ✓ Variable tracking
# ✓ Polymorphic uniqueness
```

## Key Features

### True Randomization
```python
# Each engine instance is independent
engine1 = PolymorphicCodeGenerator()  # Uses random algorithm
engine2 = PolymorphicCodeGenerator()  # Uses different random algorithm
engine3 = PolymorphicCodeGenerator()  # Uses different random algorithm
```

### Reproducible Generation
```python
# Same seed = same algorithm sequence
engine1 = PolymorphicCodeGenerator(PolymorphicConfig(seed=42))
engine2 = PolymorphicCodeGenerator(PolymorphicConfig(seed=42))
# Both use same algorithm selections
```

### Variable Tracking
```python
engine = PolymorphicCodeGenerator()
# ... generate code ...
info = engine.get_generation_info()
print(f"Variables generated: {info['variables_generated']}")
```

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Single encoding | <1ms | Very fast |
| Decoder generation | <2ms | Includes control flow wrapping |
| Complete script | <5ms | With subprocess execution code |
| Multi-stage (3 stages) | ~15ms | 3 different algorithms |
| Multi-stage (5 stages) | ~25ms | 5 different algorithms |

## Security Considerations

### Advantages
- **Signature Evasion**: Each variant has different structure
- **Behavior Consistency**: Decoding produces correct output
- **Complexity Scalability**: Configure complexity levels 1-5
- **Multi-Stage Support**: Layer multiple encodings

### Best Practices
1. Use `complexity_level=5` for maximum obfuscation
2. Generate multiple variants for distribution
3. Use multi-stage encoding (3+ stages) for critical payloads
4. Avoid using fixed seeds in production (enables reproducibility)

## Integration

The polymorphic engine integrates with the SC Generator ecosystem:

```python
# Combine with command obfuscation
from command_string_obfuscator import CommandObfuscationConfig
from polymorphic_engine import PolymorphicCodeGenerator

# Obfuscate command
config = CommandObfuscationConfig(encoding_method="base64")
obfuscated = obfuscate_command(command, config)

# Apply polymorphic encoding
poly_engine = PolymorphicCodeGenerator()
polymorphic_script = poly_engine.generate_complete_polymorphic_script(obfuscated)
```

## Troubleshooting

### Generated script doesn't execute
- Check that `subprocess` module is available
- Verify target system has Python 3.6+
- Ensure no typos in generated variable names

### Decoder produces wrong output
- Verify metadata passed to decoder matches encoding
- Check that encoded data wasn't corrupted
- Test with small payloads first

### Algorithm not selected
- Confirm engine is using latest version
- Check configuration limits aren't too restrictive
- Try without seed to enable full randomization

## Advanced Usage

### Streaming Encoding

```python
# Encode large data in chunks
engine = PolymorphicCodeGenerator()
chunk_size = 1024
data = open("large_file.bin", "rb").read()

for i in range(0, len(data), chunk_size):
    chunk = data[i:i+chunk_size]
    encoded, metadata, algo = engine.encode_data(chunk)
    print(f"Chunk {i//chunk_size}: {algo}")
```

### Custom Decoder Format

```python
# Generate decoder and customize wrapper
engine = PolymorphicCodeGenerator()
encoded, metadata, _ = engine.encode_data(b"data")
decoder = engine.generate_polymorphic_decoder(encoded, metadata)

# Wrap in custom function
custom_script = f"""
def extract_payload():
    {chr(10).join('    ' + line for line in decoder.split(chr(10)))}
    return decoded_var

payload = extract_payload()
"""
```

## Architecture

```
PolymorphicCodeGenerator
├── AlgorithmVariant (enum - 10 algorithms)
├── ControlFlowPattern (enum - 4 patterns)
├── ObfuscationTechnique (enum - 8 techniques)
└── Methods:
    ├── encode_data()
    ├── generate_polymorphic_decoder()
    ├── generate_complete_polymorphic_script()
    └── generate_multi_stage_polymorphic()
```

## License

Part of SC Generator suite

## Support

For issues or questions:
1. Check `POLYMORPHIC_ENGINE_GUIDE.md` for detailed technical info
2. Review `polymorphic_examples.py` for usage patterns
3. Run `test_polymorphic_engine.py` to verify installation
4. Check algorithm metadata for specific encoding details

---

**True Polymorphic Engine v1.0** - Complete code generation polymorphism at each execution
