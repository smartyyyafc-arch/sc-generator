# True Polymorphic Code Generation Engine

## Overview

The **Polymorphic Engine** is a true code polymorphism system that generates **completely different code structures each time** it runs - not just variable name changes, but fundamentally different algorithms, control flows, and encoding strategies.

### Key Features

- **10 Different Encoding Algorithms**: Each invocation randomly selects from completely different encoding techniques
  - Linear XOR with random keys and offsets
  - Bitwise rotation with varying rotation amounts
  - Mathematical offset encoding with modular arithmetic
  - Interleave and reverse patterns
  - Lookup table based encoding (shuffled each time)
  - Chaotic shuffling/permutations
  - Wave pattern encoding
  - Prime modulo encoding
  - Fibonacci sequence encoding
  - Recursive split encoding

- **Multiple Control Flow Patterns**: Code structure varies each generation
  - Sequential execution
  - Conditional branches with opaque predicates
  - Loop wrapping
  - State machine patterns

- **True Polymorphism**: 
  - Different algorithms every run
  - Different variable names (randomized)
  - Different control flow structures
  - Different data representations (hex vs array literals)
  - Multi-stage polymorphic payloads

## Usage Examples

### Basic Polymorphic Generation

```python
from polymorphic_engine import PolymorphicCodeGenerator, PolymorphicConfig

# Create engine with configuration
config = PolymorphicConfig(
    algorithm_variants=3,
    control_flow_patterns=2,
    obfuscation_techniques=3,
    complexity_level=4
)

engine = PolymorphicCodeGenerator(config)

# Generate polymorphic script
command = "echo 'Hello from polymorphic code'"
script = engine.generate_complete_polymorphic_script(command)
print(script)
```

### Multi-Stage Polymorphic Payload

```python
# Generate 3-stage polymorphic payload
# (each stage encodes the previous stage's output)
multi_stage = engine.generate_multi_stage_polymorphic(
    payload="whoami", 
    stages=3
)
print(multi_stage)
```

### Direct Data Encoding

```python
# Encode data with polymorphic engine
data = b"sensitive payload"
encoded, metadata, algorithm_name = engine.encode_data(data)

# Generate decoder for specific encoding
decoder_code = engine.generate_polymorphic_decoder(encoded, metadata)
```

### Custom Configuration

```python
config = PolymorphicConfig(
    seed=None,  # None = truly random each run
    algorithm_variants=4,  # Use up to 4 different algorithms
    control_flow_patterns=3,
    obfuscation_techniques=4,
    target_language="python",
    complexity_level=5,  # Maximum complexity
    include_comments=False
)

engine = PolymorphicCodeGenerator(config)
```

## Algorithm Details

### 1. Linear XOR (linear_xor)
Applies XOR with random key and offset to each byte:
```
encoded = ((byte ^ key) + offset) & 0xFF
decoded = ((byte - offset) ^ key) & 0xFF
```

### 2. Bitwise Rotation (bitwise_rot)
Rotates each byte left by random amount:
```
encoded = ((byte << rotations) | (byte >> (8 - rotations))) & 0xFF
decoded = ((byte >> rotations) | (byte << (8 - rotations))) & 0xFF
```

### 3. Mathematical Offset (math_offset)
Uses multiplication and modulo for encoding:
```
encoded = (byte * multiplier + shift) % 256
decoded = (byte - shift) * inverse_multiplier & 0xFF
```

### 4. Interleave Reverse (interleave_reverse)
Splits data into even/odd indices, reverses each part, then reinterleaves:
```
even = [data[0], data[2], data[4], ...]
odd = [data[1], data[3], data[5], ...]
encoded = interleave(reverse(even), reverse(odd))
```

### 5. Lookup Table (lookup_table)
Creates random 256-byte permutation table:
```
table = [shuffled 0-255]
encoded = [table[byte] for byte in data]
decoded = [reverse_table[byte] for byte in encoded]
```

### 6. Chaotic Shuffle (chaotic_shuffle)
Randomly permutes byte positions:
```
shuffle_indices = random permutation
encoded = data reordered by shuffle_indices
decoded = inverse permutation applied
```

### 7. Wave Pattern (wave_pattern)
Adds pseudo-random wave amplitude to each byte:
```
encoded = (byte + wave_amplitude) & 0xFF
decoded = (byte - wave_amplitude) & 0xFF
```

### 8. Prime Modulo (prime_modulo)
Uses prime number modulo arithmetic:
```
prime = random prime from [2, 3, 5, 7, ..., 71]
encoded = (byte + offset) % prime
decoded = (byte - offset) % prime
```

### 9. Fibonacci Sequence (fibonacci_sequence)
Encodes using Fibonacci numbers:
```
fib = [0, 1, 1, 2, 3, 5, 8, 13, ...]
encoded = (byte + fib[i]) & 0xFF
decoded = (byte - fib[i]) & 0xFF
```

### 10. Recursive Split (recursive_split)
Recursively splits and reorders data:
```
split each half recursively
swap left/right at each level
maximum recursion depth = 3
```

## Control Flow Patterns

Each generated script can wrap its code in different control flow structures:

### Sequential
Direct, simple execution with no extra wrappers.

### Conditional
```python
if condition_var:
    # actual decoding code
else:
    # dummy code
```

### Loop
```python
for i in range(1):
    # actual decoding code
```

### State Machine
```python
state = 0
while state == 0:
    # actual decoding code
    state = 1
```

## Polymorphic Variations

Each generation creates **completely different code**:

```
Generation 1:
- Algorithm: linear_xor with key=108, offset=93
- Control Flow: state_machine
- Variables: v_dqgPKXEd_4, result_cSMsUrodGDGA_3, ...
- Data repr: bytes([...])

Generation 2:
- Algorithm: prime_modulo with prime=13, offset=30
- Control Flow: sequential
- Variables: v_avoBJNiTZ_1, result_TPdcvJMHBgJf_3, ...
- Data repr: bytes.fromhex(...)

Generation 3:
- Algorithm: fibonacci_sequence
- Control Flow: loop
- Variables: v_D_Xf_ZQQeU_1, fib_pycgufvfcEdV_4, ...
- Data repr: bytes([...])
```

## Advanced Features

### Multi-Stage Encoding

Create payloads with multiple encoding stages. Each stage encodes the output of the previous stage using a completely different algorithm:

```python
# Stage 1: interleave_reverse
# → output becomes input for Stage 2

# Stage 2: lookup_table
# → output becomes input for Stage 3

# Stage 3: linear_xor
# → final encoded payload
```

### Generation Information

Get metadata about generated code:

```python
info = engine.get_generation_info()
# Returns:
# {
#     'algorithm_variants': 3,
#     'control_flow_patterns': 2,
#     'obfuscation_techniques': 3,
#     'target_language': 'python',
#     'complexity_level': 4,
#     'variables_generated': 7
# }
```

## Security Considerations

- **Randomization**: Use `seed=None` for true randomness
- **Fixed Seed**: Use `seed=12345` for reproducible testing
- **Complexity Levels**: Higher levels = more obfuscation but slower execution
- **Multi-Stage**: Increases detection resistance significantly

## Performance

- Single stage encoding: Very fast (microseconds)
- Multi-stage encoding: Slower but stronger obfuscation
- Decoding overhead: Minimal, comparable to original data size

## Integration

The polymorphic engine integrates with the broader SC Generator ecosystem:

```python
from polymorphic_engine import PolymorphicCodeGenerator
from command_string_obfuscator import CommandObfuscationConfig

# Generate polymorphic decoder for obfuscated commands
engine = PolymorphicCodeGenerator()
script = engine.generate_complete_polymorphic_script(command)

# Can be combined with other encoding methods
# for layered protection
```

## Testing

Run comprehensive tests:

```bash
python3 polymorphic_engine.py
```

This demonstrates:
1. Three complete generations with different algorithms
2. Multi-stage polymorphic payload
3. Generation information for each variant

## File Location

- **Engine**: `/home/user/sc-generator/polymorphic_engine.py`
- **Guide**: `/home/user/sc-generator/POLYMORPHIC_ENGINE_GUIDE.md`
