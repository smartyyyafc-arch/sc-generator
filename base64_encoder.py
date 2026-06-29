#!/usr/bin/env python3
"""
Base64 Encoder - Pair with existing VBS Base64 decoder
Provides reverse operations for the VBSEncoder decoder functions
For authorized pentesting and security research
"""

import base64
import string
import random
from typing import Tuple, Optional
from functools import lru_cache


class Base64Encoder:
    """Encode strings to Base64 for use with VBS decoder"""

    def __init__(self):
        self._encoding_cache = {}

    def encode_to_base64(self, text: str) -> str:
        """
        Encode plain text to Base64 string.

        Args:
            text: Plain text string to encode

        Returns:
            Base64-encoded string
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        return base64.b64encode(text.encode()).decode()

    def encode_to_base64_with_cache(self, text: str) -> Tuple[str, str]:
        """
        Encode plain text to Base64 with caching support.
        Useful for repeated encoding operations.

        Args:
            text: Plain text string to encode

        Returns:
            Tuple of (encoded_string, cache_key)
        """
        # Check cache first
        if text in self._encoding_cache:
            return self._encoding_cache[text]

        # Perform encoding
        encoded = self.encode_to_base64(text)
        cache_key = f"b64_{hash(text) % 1000000}"

        # Store in cache
        self._encoding_cache[text] = (encoded, cache_key)
        return encoded, cache_key

    def encode_command_payload(self, command: str) -> str:
        """
        Encode a command for use as a VBS payload.

        Args:
            command: Command string to encode

        Returns:
            Base64-encoded command payload
        """
        return self.encode_to_base64(command)

    def encode_file_content(self, file_content: str) -> str:
        """
        Encode file content to Base64.

        Args:
            file_content: Content of file to encode

        Returns:
            Base64-encoded content
        """
        return self.encode_to_base64(file_content)

    def encode_bytes_to_base64(self, data: bytes) -> str:
        """
        Encode bytes to Base64 string.

        Args:
            data: Bytes to encode

        Returns:
            Base64-encoded string
        """
        if not isinstance(data, bytes):
            raise TypeError(f"Expected bytes, got {type(data).__name__}")

        return base64.b64encode(data).decode()

    def create_vbs_encoded_variable(self, text: str, var_name: Optional[str] = None) -> str:
        """
        Create VBS code with Base64-encoded variable.
        Pairs with VBSEncoder's create_base64_decoder_vbs function.

        Args:
            text: Text to encode
            var_name: Optional variable name (generated if not provided)

        Returns:
            VBS code snippet with encoded variable declaration
        """
        encoded = self.encode_to_base64(text)

        if not var_name:
            var_name = self._generate_random_vbs_name("v_")

        vbs_code = f'Dim {var_name}\n{var_name} = "{encoded}"'
        return vbs_code

    def create_vbs_decoder_pair(self, text: str) -> Tuple[str, str]:
        """
        Create paired encoder-decoder VBS code.

        Args:
            text: Text to encode

        Returns:
            Tuple of (encoder_code, decoder_code)
        """
        encoded = self.encode_to_base64(text)
        var_name = self._generate_random_vbs_name("v_")
        obj_var = self._generate_random_vbs_name("o_")

        encoder_code = f"""
Dim {var_name}
{var_name} = "{encoded}"
"""

        decoder_code = f"""
Dim {var_name}, {self._generate_random_vbs_name("decoded_")}
{var_name} = "{encoded}"
Set {obj_var} = CreateObject("MSXML2.DOMDocument")
With {obj_var}
    .LoadXML "<u><![CDATA[" & {var_name} & "]]></u>"
    {self._generate_random_vbs_name("decoded_")} = .SelectSingleNode("u").text
End With
"""

        return encoder_code.strip(), decoder_code.strip()

    def create_powershell_encoded_command(self, command: str) -> str:
        """
        Create Base64-encoded command for PowerShell.

        Args:
            command: PowerShell command to encode

        Returns:
            Base64-encoded command for -EncodedCommand parameter
        """
        # PowerShell uses UTF-16LE encoding
        return base64.b64encode(command.encode('utf-16-le')).decode()

    def batch_encode_multiple(self, texts: list) -> dict:
        """
        Encode multiple texts at once.

        Args:
            texts: List of strings to encode

        Returns:
            Dictionary mapping original text to encoded value
        """
        result = {}
        for text in texts:
            result[text] = self.encode_to_base64(text)
        return result

    def _generate_random_vbs_name(self, prefix: str = "", length: int = 8) -> str:
        """Generate random VBS variable/function name."""
        chars = string.ascii_letters + string.digits + "_"
        name = prefix + "".join(random.choices(chars, k=length))
        return name

    def verify_encoding(self, original: str, encoded: str) -> bool:
        """
        Verify that encoding was done correctly.

        Args:
            original: Original text
            encoded: Encoded text

        Returns:
            True if encoding is correct, False otherwise
        """
        try:
            decoded = base64.b64decode(encoded).decode()
            return decoded == original
        except Exception:
            return False

    def create_reverse_lookup_table(self, texts: list) -> dict:
        """
        Create a lookup table for encoding/decoding.
        Useful for quickly finding encoded equivalents.

        Args:
            texts: List of texts to create lookup for

        Returns:
            Dictionary with forward and reverse mappings
        """
        lookup = {
            'forward': {},  # plain -> encoded
            'reverse': {}   # encoded -> plain
        }

        for text in texts:
            encoded = self.encode_to_base64(text)
            lookup['forward'][text] = encoded
            lookup['reverse'][encoded] = text

        return lookup


class Base64OperationsPair:
    """
    Paired encoder-decoder operations for Base64 transformations.
    Provides symmetric encode/decode operations.
    """

    def __init__(self):
        self.encoder = Base64Encoder()

    def encode(self, text: str) -> str:
        """Encode plain text to Base64."""
        return self.encoder.encode_to_base64(text)

    def decode(self, encoded: str) -> str:
        """Decode Base64 string to plain text."""
        try:
            return base64.b64decode(encoded).decode()
        except Exception as e:
            raise ValueError(f"Failed to decode Base64: {e}")

    def encode_with_validation(self, text: str) -> str:
        """
        Encode and validate the operation.

        Args:
            text: Text to encode

        Returns:
            Base64-encoded string

        Raises:
            ValueError: If encoding cannot be validated
        """
        encoded = self.encode(text)
        if not self.encoder.verify_encoding(text, encoded):
            raise ValueError("Encoding validation failed")
        return encoded

    def round_trip_transform(self, text: str) -> bool:
        """
        Test encode-decode round trip to verify correctness.

        Args:
            text: Text to test

        Returns:
            True if round trip is successful
        """
        encoded = self.encode(text)
        decoded = self.decode(encoded)
        return decoded == text


def encode_payload(text: str) -> str:
    """
    Convenience function to encode a payload string.

    Args:
        text: Text to encode

    Returns:
        Base64-encoded string
    """
    encoder = Base64Encoder()
    return encoder.encode_to_base64(text)


def create_encoder_decoder_pair(text: str) -> Tuple[str, str]:
    """
    Convenience function to create paired VBS encoder-decoder.

    Args:
        text: Text to encode

    Returns:
        Tuple of (encoder_vbs_code, decoder_vbs_code)
    """
    encoder = Base64Encoder()
    return encoder.create_vbs_decoder_pair(text)


def verify_reverse_operation(original: str, encoded: str) -> bool:
    """
    Verify that the reverse operation (decode) will work correctly.

    Args:
        original: Original plain text
        encoded: Base64-encoded text

    Returns:
        True if reverse operation is valid
    """
    encoder = Base64Encoder()
    return encoder.verify_encoding(original, encoded)


if __name__ == "__main__":
    # Example usage demonstrating encoder functionality

    print("=== Base64 Encoder Examples ===\n")

    encoder = Base64Encoder()

    # Example 1: Simple string encoding
    test_string = "powershell.exe -NoProfile -WindowStyle Hidden"
    encoded = encoder.encode_to_base64(test_string)
    print(f"Original: {test_string}")
    print(f"Encoded: {encoded}\n")

    # Example 2: Encode with cache
    command = "cmd /c echo test"
    encoded, cache_key = encoder.encode_to_base64_with_cache(command)
    print(f"Command: {command}")
    print(f"Encoded: {encoded}")
    print(f"Cache Key: {cache_key}\n")

    # Example 3: Create VBS variable with encoded value
    vbs_var = encoder.create_vbs_encoded_variable("Test Command")
    print(f"VBS Variable:\n{vbs_var}\n")

    # Example 4: PowerShell encoded command
    ps_command = "Write-Host 'Hello World'"
    ps_encoded = encoder.create_powershell_encoded_command(ps_command)
    print(f"PowerShell Command: {ps_command}")
    print(f"PowerShell Encoded: {ps_encoded}\n")

    # Example 5: Verify encoding
    test = "verification test"
    test_encoded = encoder.encode_to_base64(test)
    is_valid = encoder.verify_encoding(test, test_encoded)
    print(f"Verification Test: {test}")
    print(f"Is Valid: {is_valid}\n")

    # Example 6: Round-trip test
    ops = Base64OperationsPair()
    round_trip_text = "Round trip test string"
    success = ops.round_trip_transform(round_trip_text)
    print(f"Round Trip Test: {round_trip_text}")
    print(f"Success: {success}\n")

    # Example 7: Batch encoding
    texts = ["command1", "command2", "command3"]
    batch_result = encoder.batch_encode_multiple(texts)
    print(f"Batch Encoded Results:")
    for text, encoded_text in batch_result.items():
        print(f"  {text} -> {encoded_text}\n")
