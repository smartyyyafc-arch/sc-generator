#!/usr/bin/env python3
"""
Multi-Encoding Layers: Randomly selects 1-3 encoding layers for enhanced obfuscation
Supports multiple encoding strategies that can be chained together
For authorized pentesting and security research
"""

import random
import binascii
import base64
import string
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class EncodingLayerType(Enum):
    """Individual encoding layer types"""
    HEX = "hex"
    BASE64 = "base64"
    ROT13 = "rot13"
    XOR = "xor"
    OCTAL = "octal"
    ASCII = "ascii"
    REVERSE = "reverse"
    ZLIB = "zlib"


@dataclass
class EncodingLayer:
    """Represents a single encoding layer"""
    layer_type: EncodingLayerType
    encode_func: Callable
    decode_func: Callable
    config: Dict = None


class EncodingLayerFactory:
    """Factory for creating individual encoding layers"""

    @staticmethod
    def hex_encode(data: str) -> str:
        """Encode to hex"""
        return binascii.hexlify(data.encode()).decode()

    @staticmethod
    def hex_decode(data: str) -> str:
        """Decode from hex"""
        return binascii.unhexlify(data).decode()

    @staticmethod
    def base64_encode(data: str) -> str:
        """Encode to base64"""
        return base64.b64encode(data.encode()).decode()

    @staticmethod
    def base64_decode(data: str) -> str:
        """Decode from base64"""
        return base64.b64decode(data).decode()

    @staticmethod
    def rot13_encode(data: str) -> str:
        """Encode with ROT13"""
        result = []
        for char in data:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)

    @staticmethod
    def rot13_decode(data: str) -> str:
        """Decode from ROT13 (ROT13 is symmetric)"""
        return EncodingLayerFactory.rot13_encode(data)

    @staticmethod
    def xor_encode(data: str, key: int = 42) -> str:
        """Encode with XOR"""
        result = []
        for char in data:
            xored = ord(char) ^ key
            result.append(format(xored, '02x'))
        return ''.join(result)

    @staticmethod
    def xor_decode(data: str, key: int = 42) -> str:
        """Decode from XOR"""
        result = []
        for i in range(0, len(data), 2):
            byte_val = int(data[i:i+2], 16)
            result.append(chr(byte_val ^ key))
        return ''.join(result)

    @staticmethod
    def octal_encode(data: str) -> str:
        """Encode to octal"""
        hex_str = binascii.hexlify(data.encode()).decode()
        octal_parts = []
        for i in range(0, len(hex_str), 2):
            byte_val = int(hex_str[i:i+2], 16)
            octal_parts.append(oct(byte_val)[2:].zfill(3))
        return "".join(octal_parts)

    @staticmethod
    def octal_decode(data: str) -> str:
        """Decode from octal"""
        result = []
        for i in range(0, len(data), 3):
            octal_val = data[i:i+3]
            byte_val = int(octal_val, 8)
            result.append(chr(byte_val))
        return ''.join(result)

    @staticmethod
    def ascii_encode(data: str) -> str:
        """Encode as ASCII codes"""
        return ','.join(str(ord(char)) for char in data)

    @staticmethod
    def ascii_decode(data: str) -> str:
        """Decode from ASCII codes"""
        return ''.join(chr(int(val)) for val in data.split(','))

    @staticmethod
    def reverse_encode(data: str) -> str:
        """Reverse the string"""
        return data[::-1]

    @staticmethod
    def reverse_decode(data: str) -> str:
        """Reverse the string (reverse is symmetric)"""
        return data[::-1]

    @staticmethod
    def zlib_encode(data: str) -> str:
        """Encode with zlib compression and base64"""
        import zlib
        compressed = zlib.compress(data.encode())
        return base64.b64encode(compressed).decode()

    @staticmethod
    def zlib_decode(data: str) -> str:
        """Decode from zlib"""
        import zlib
        compressed = base64.b64decode(data)
        return zlib.decompress(compressed).decode()

    @staticmethod
    def create_layer(layer_type: EncodingLayerType, config: Dict = None) -> EncodingLayer:
        """Create an encoding layer of specified type"""
        config = config or {}

        layers_map = {
            EncodingLayerType.HEX: (
                EncodingLayerFactory.hex_encode,
                EncodingLayerFactory.hex_decode
            ),
            EncodingLayerType.BASE64: (
                EncodingLayerFactory.base64_encode,
                EncodingLayerFactory.base64_decode
            ),
            EncodingLayerType.ROT13: (
                EncodingLayerFactory.rot13_encode,
                EncodingLayerFactory.rot13_decode
            ),
            EncodingLayerType.XOR: (
                lambda d: EncodingLayerFactory.xor_encode(d, config.get('key', 42)),
                lambda d: EncodingLayerFactory.xor_decode(d, config.get('key', 42))
            ),
            EncodingLayerType.OCTAL: (
                EncodingLayerFactory.octal_encode,
                EncodingLayerFactory.octal_decode
            ),
            EncodingLayerType.ASCII: (
                EncodingLayerFactory.ascii_encode,
                EncodingLayerFactory.ascii_decode
            ),
            EncodingLayerType.REVERSE: (
                EncodingLayerFactory.reverse_encode,
                EncodingLayerFactory.reverse_decode
            ),
            EncodingLayerType.ZLIB: (
                EncodingLayerFactory.zlib_encode,
                EncodingLayerFactory.zlib_decode
            ),
        }

        encode_func, decode_func = layers_map[layer_type]
        return EncodingLayer(
            layer_type=layer_type,
            encode_func=encode_func,
            decode_func=decode_func,
            config=config
        )


class MultiEncodingWrapper:
    """
    Randomized multi-encoding wrapper that selects 1-3 layers
    Each instance generates a random combination of encoding layers
    """

    def __init__(
        self,
        num_layers: Optional[int] = None,
        available_layers: Optional[List[EncodingLayerType]] = None,
        seed: Optional[int] = None
    ):
        """
        Initialize multi-encoding wrapper with randomized layer selection

        Args:
            num_layers: Number of layers to use (1-3). If None, randomly selected.
            available_layers: List of encoding layers to choose from.
                            If None, uses all available layers.
            seed: Random seed for reproducibility (optional)
        """
        if seed is not None:
            random.seed(seed)

        # Set default available layers
        if available_layers is None:
            self.available_layers = [
                EncodingLayerType.HEX,
                EncodingLayerType.BASE64,
                EncodingLayerType.ROT13,
                EncodingLayerType.XOR,
                EncodingLayerType.OCTAL,
                EncodingLayerType.REVERSE,
                EncodingLayerType.ZLIB,
            ]
        else:
            self.available_layers = available_layers

        # Randomly select number of layers (1-3)
        if num_layers is None:
            self.num_layers = random.randint(1, 3)
        else:
            self.num_layers = max(1, min(3, num_layers))

        # Randomly select which layers to use (without replacement)
        selected = random.sample(
            self.available_layers,
            k=min(self.num_layers, len(self.available_layers))
        )
        self.layers_sequence = selected

        # Create the encoding layers
        self.encoding_layers = []
        for layer_type in self.layers_sequence:
            config = {}
            if layer_type == EncodingLayerType.XOR:
                config['key'] = random.randint(1, 255)
            layer = EncodingLayerFactory.create_layer(layer_type, config)
            self.encoding_layers.append(layer)

    def encode(self, data: str) -> str:
        """
        Apply all encoding layers in sequence

        Args:
            data: Input data to encode

        Returns:
            Encoded data after applying all layers
        """
        result = data
        for layer in self.encoding_layers:
            result = layer.encode_func(result)
        return result

    def decode(self, data: str) -> str:
        """
        Apply all decoding layers in reverse sequence

        Args:
            data: Encoded data to decode

        Returns:
            Decoded data after reversing all layers
        """
        result = data
        # Apply layers in reverse order
        for layer in reversed(self.encoding_layers):
            result = layer.decode_func(result)
        return result

    def get_layer_info(self) -> Dict:
        """Get information about the layers used"""
        layers_info = []
        for i, layer in enumerate(self.encoding_layers):
            layer_dict = {
                'index': i + 1,
                'type': layer.layer_type.value,
            }
            if layer.config:
                layer_dict['config'] = layer.config
            layers_info.append(layer_dict)

        return {
            'total_layers': self.num_layers,
            'layers': layers_info,
            'sequence': [l.layer_type.value for l in self.encoding_layers]
        }

    def generate_decoder_python(self, encoded_payload: str, var_name: str = "payload") -> str:
        """
        Generate Python decoder code for the encoded payload

        Args:
            encoded_payload: The encoded data
            var_name: Variable name for the payload

        Returns:
            Python code to decode the payload
        """
        code = f"# Multi-Encoding Wrapper: {self.num_layers} layers\n"
        code += f"# Layers: {' -> '.join(l.layer_type.value for l in self.encoding_layers)}\n"
        code += f"import base64\nimport binascii\n"

        if any(l.layer_type == EncodingLayerType.ZLIB for l in self.encoding_layers):
            code += "import zlib\n"

        code += f"\n{var_name} = \"{encoded_payload}\"\n\n"

        # Generate decoder functions
        for i, layer in enumerate(self.encoding_layers):
            code += f"# Decode layer {i+1}: {layer.layer_type.value}\n"

            if layer.layer_type == EncodingLayerType.HEX:
                code += f"{var_name} = binascii.unhexlify({var_name}).decode()\n"
            elif layer.layer_type == EncodingLayerType.BASE64:
                code += f"{var_name} = base64.b64decode({var_name}).decode()\n"
            elif layer.layer_type == EncodingLayerType.ROT13:
                code += self._rot13_decoder(var_name)
            elif layer.layer_type == EncodingLayerType.XOR:
                key = layer.config.get('key', 42)
                code += self._xor_decoder(var_name, key)
            elif layer.layer_type == EncodingLayerType.OCTAL:
                code += self._octal_decoder(var_name)
            elif layer.layer_type == EncodingLayerType.ASCII:
                code += self._ascii_decoder(var_name)
            elif layer.layer_type == EncodingLayerType.REVERSE:
                code += f"{var_name} = {var_name}[::-1]\n"
            elif layer.layer_type == EncodingLayerType.ZLIB:
                code += f"{var_name} = zlib.decompress(base64.b64decode({var_name})).decode()\n"

            code += "\n"

        code += f"print({var_name})\n"
        return code

    @staticmethod
    def _rot13_decoder(var_name: str) -> str:
        """Generate ROT13 decoder code"""
        return f"""def rot13_decode(s):
    return ''.join(chr((ord(c) - ord('a' if c.islower() else 'A') + 13) % 26 + ord('a' if c.islower() else 'A')) if c.isalpha() else c for c in s)
{var_name} = rot13_decode({var_name})
"""

    @staticmethod
    def _xor_decoder(var_name: str, key: int) -> str:
        """Generate XOR decoder code"""
        return f"""def xor_decode(s, key={key}):
    return ''.join(chr(int(s[i:i+2], 16) ^ key) for i in range(0, len(s), 2))
{var_name} = xor_decode({var_name})
"""

    @staticmethod
    def _octal_decoder(var_name: str) -> str:
        """Generate octal decoder code"""
        return f"""def octal_decode(s):
    return ''.join(chr(int(s[i:i+3], 8)) for i in range(0, len(s), 3))
{var_name} = octal_decode({var_name})
"""

    @staticmethod
    def _ascii_decoder(var_name: str) -> str:
        """Generate ASCII decoder code"""
        return f"""{var_name} = ''.join(chr(int(v)) for v in {var_name}.split(','))
"""

    def generate_decoder_powershell(self, encoded_payload: str, var_name: str = "payload") -> str:
        """
        Generate PowerShell decoder code for the encoded payload

        Args:
            encoded_payload: The encoded data
            var_name: Variable name for the payload

        Returns:
            PowerShell code to decode the payload
        """
        code = f"# Multi-Encoding Wrapper: {self.num_layers} layers\n"
        code += f"# Layers: {' -> '.join(l.layer_type.value for l in self.encoding_layers)}\n\n"
        code += f"${var_name} = \"{encoded_payload}\"\n\n"

        for i, layer in enumerate(self.encoding_layers):
            code += f"# Decode layer {i+1}: {layer.layer_type.value}\n"

            if layer.layer_type == EncodingLayerType.HEX:
                code += f"${var_name} = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromHexString(${var_name}))\n"
            elif layer.layer_type == EncodingLayerType.BASE64:
                code += f"${var_name} = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(${var_name}))\n"
            elif layer.layer_type == EncodingLayerType.ROT13:
                code += self._rot13_decoder_ps(var_name)
            elif layer.layer_type == EncodingLayerType.REVERSE:
                code += f"${var_name} = $({var_name}.ToCharArray() | ForEach-Object {{[string]$_}} | sort -Descending | join '')\n"
            elif layer.layer_type == EncodingLayerType.OCTAL:
                code += self._octal_decoder_ps(var_name)
            elif layer.layer_type == EncodingLayerType.ASCII:
                code += self._ascii_decoder_ps(var_name)
            elif layer.layer_type == EncodingLayerType.ZLIB:
                code += self._zlib_decoder_ps(var_name)

            code += "\n"

        code += f"Write-Host ${var_name}\n"
        return code

    @staticmethod
    def _rot13_decoder_ps(var_name: str) -> str:
        """Generate PowerShell ROT13 decoder code"""
        return f"""${var_name} = $({var_name}.ToCharArray() | ForEach-Object {{
    $c = [int]$_
    if (($c -ge 97 -and $c -le 122) -or ($c -ge 65 -and $c -le 90)) {{
        [char](([int]$_ - (if ([char]$_ -match '[a-z]') {{ 97 }} else {{ 65 }})) + 13 % 26 + (if ([char]$_ -match '[a-z]') {{ 97 }} else {{ 65 }}))
    }} else {{
        [char]$_
    }}
}} | join '')
"""

    @staticmethod
    def _octal_decoder_ps(var_name: str) -> str:
        """Generate PowerShell octal decoder code"""
        return f"""${var_name} = $([regex]::Matches(${var_name}, '.{{1,3}}') | ForEach-Object {{
    [char][convert]::ToInt32($_.Value, 8)
}} | join '')
"""

    @staticmethod
    def _ascii_decoder_ps(var_name: str) -> str:
        """Generate PowerShell ASCII decoder code"""
        return f"""${var_name} = $({var_name}.Split(',') | ForEach-Object {{
    [char][int]$_
}} | join '')
"""

    @staticmethod
    def _zlib_decoder_ps(var_name: str) -> str:
        """Generate PowerShell zlib decoder code"""
        return f"""${var_name} = [System.Text.Encoding]::UTF8.GetString((New-Object System.IO.Compression.GZipStream([System.IO.MemoryStream][System.Convert]::FromBase64String(${var_name}), 'Decompress')).ReadToEnd())
"""

    def generate_wrapper_report(self) -> str:
        """Generate a detailed report about the encoding configuration"""
        report = "=" * 70 + "\n"
        report += "MULTI-ENCODING WRAPPER CONFIGURATION REPORT\n"
        report += "=" * 70 + "\n\n"

        report += f"Total Encoding Layers: {self.num_layers}\n"
        report += f"Layer Sequence: {' -> '.join(l.layer_type.value for l in self.encoding_layers)}\n\n"

        report += "Detailed Layer Configuration:\n"
        report += "-" * 70 + "\n"

        for i, layer in enumerate(self.encoding_layers):
            report += f"\nLayer {i+1}: {layer.layer_type.value.upper()}\n"
            if layer.config:
                report += f"  Config: {layer.config}\n"
            else:
                report += "  Config: Default\n"

        report += "\n" + "=" * 70 + "\n"
        return report


def create_multi_encoding_wrapper(
    num_layers: Optional[int] = None,
    available_layers: Optional[List[EncodingLayerType]] = None,
    seed: Optional[int] = None
) -> MultiEncodingWrapper:
    """
    Convenience function to create a multi-encoding wrapper

    Args:
        num_layers: Number of layers (1-3). If None, randomly selected.
        available_layers: Available encoding types. If None, uses all.
        seed: Random seed for reproducibility

    Returns:
        Configured MultiEncodingWrapper instance
    """
    return MultiEncodingWrapper(
        num_layers=num_layers,
        available_layers=available_layers,
        seed=seed
    )


if __name__ == "__main__":
    # Example 1: Basic usage with random layer selection
    print("=" * 70)
    print("Example 1: Random Multi-Encoding Wrapper")
    print("=" * 70)
    wrapper1 = MultiEncodingWrapper()
    print(wrapper1.generate_wrapper_report())

    # Encode a simple message
    test_message = "Hello, World!"
    encoded = wrapper1.encode(test_message)
    print(f"\nOriginal message: {test_message}")
    print(f"Encoded message: {encoded}\n")

    # Verify decoding works
    decoded = wrapper1.decode(encoded)
    print(f"Decoded message: {decoded}")
    print(f"Verification: {decoded == test_message}\n")

    # Example 2: Specific number of layers
    print("=" * 70)
    print("Example 2: 3-Layer Encoding")
    print("=" * 70)
    wrapper2 = MultiEncodingWrapper(num_layers=3)
    print(wrapper2.generate_wrapper_report())

    test_payload = "powershell.exe -Command Write-Host test"
    encoded2 = wrapper2.encode(test_payload)
    print(f"\nOriginal payload: {test_payload}")
    print(f"Encoded payload: {encoded2}\n")

    decoded2 = wrapper2.decode(encoded2)
    print(f"Decoded payload: {decoded2}")
    print(f"Verification: {decoded2 == test_payload}\n")

    # Example 3: Generate Python decoder
    print("=" * 70)
    print("Example 3: Python Decoder Code")
    print("=" * 70)
    wrapper3 = MultiEncodingWrapper(num_layers=2, seed=42)
    test_cmd = "calc.exe"
    encoded3 = wrapper3.encode(test_cmd)

    print("\nGenerated Python decoder:\n")
    print(wrapper3.generate_decoder_python(encoded3, "cmd_payload"))

    # Example 4: Generate PowerShell decoder
    print("\n" + "=" * 70)
    print("Example 4: PowerShell Decoder Code")
    print("=" * 70)
    wrapper4 = MultiEncodingWrapper(num_layers=2, seed=42)
    test_cmd2 = "whoami"
    encoded4 = wrapper4.encode(test_cmd2)

    print("\nGenerated PowerShell decoder:\n")
    print(wrapper4.generate_decoder_powershell(encoded4, "cmd"))
