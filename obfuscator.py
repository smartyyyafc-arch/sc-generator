#!/usr/bin/env python3

"""
Command Obfuscation Utility
Uses environment variables and string concatenation to obfuscate commands
"""

import os
import sys
import base64
import hashlib
import struct
from typing import List, Tuple, Dict
from pathlib import Path


class CommandObfuscator:
    """Main obfuscation engine"""

    def __init__(self):
        self.env_vars: Dict[str, str] = {}
        self.setup_environment()

    def setup_environment(self):
        """Initialize obfuscation environment variables"""
        self.env_vars = {
            # Character building blocks
            'CHAR_E': 'e',
            'CHAR_C': 'c',
            'CHAR_H': 'h',
            'CHAR_O': 'o',
            'CHAR_L': 'l',
            'CHAR_S': 's',
            'CHAR_SPACE': ' ',
            'CHAR_DASH': '-',
            'CHAR_SLASH': '/',

            # Command fragments
            'CMD_ECHO': 'echo',
            'CMD_LS': 'ls',
            'CMD_CAT': 'cat',
            'CMD_GREP': 'grep',
            'CMD_BASH': 'bash',
            'CMD_SH': 'sh',

            # Flags
            'FLAG_A': 'a',
            'FLAG_L': 'l',
            'FLAG_R': 'r',
            'FLAG_I': 'i',
            'FLAG_N': 'n',
            'FLAG_V': 'v',
        }

        # Store in actual environment
        for key, value in self.env_vars.items():
            os.environ[key] = value

    def hex_encode(self, command: str) -> str:
        """Encode command as hex string"""
        return command.encode('utf-8').hex()

    def hex_decode(self, hex_string: str) -> str:
        """Decode hex string to command"""
        return bytes.fromhex(hex_string).decode('utf-8')

    def b64_encode(self, command: str) -> str:
        """Encode command as base64"""
        return base64.b64encode(command.encode('utf-8')).decode('utf-8')

    def b64_decode(self, b64_string: str) -> str:
        """Decode base64 string to command"""
        return base64.b64decode(b64_string.encode('utf-8')).decode('utf-8')

    def rot13(self, text: str) -> str:
        """ROT13 encoding/decoding"""
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)

    def reverse(self, command: str) -> str:
        """Reverse string obfuscation"""
        return command[::-1]

    def caesar_cipher(self, command: str, shift: int = 3) -> str:
        """Caesar cipher encoding"""
        result = []
        for char in command:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)

    def caesar_decipher(self, command: str, shift: int = 3) -> str:
        """Caesar cipher decoding"""
        return self.caesar_cipher(command, -shift)

    def xor_encode(self, command: str, key: str = "obfuscate") -> bytes:
        """XOR encoding with key"""
        key_bytes = key.encode('utf-8')
        cmd_bytes = command.encode('utf-8')
        result = bytes(a ^ b for a, b in zip(cmd_bytes, (key_bytes * (len(cmd_bytes) // len(key_bytes) + 1))))
        return result

    def xor_decode(self, encoded: bytes, key: str = "obfuscate") -> str:
        """XOR decoding with key"""
        key_bytes = key.encode('utf-8')
        result = bytes(a ^ b for a, b in zip(encoded, (key_bytes * (len(encoded) // len(key_bytes) + 1))))
        return result.decode('utf-8')

    def env_var_concat(self, *parts: str) -> str:
        """Build command using environment variable concatenation"""
        result = []
        for part in parts:
            if part.startswith('$'):
                # Replace environment variable reference
                var_name = part[1:]
                result.append(os.environ.get(var_name, part))
            else:
                result.append(part)
        return ' '.join(result)

    def multi_layer_encode(self, command: str, layers: int = 3) -> str:
        """Apply multiple encoding layers"""
        current = command
        encoders = [self.hex_encode, self.b64_encode, self.rot13]

        for i in range(layers):
            encoder = encoders[i % len(encoders)]
            current = encoder(current)

        return current

    def multi_layer_decode(self, encoded: str, layers: int = 3) -> str:
        """Reverse multiple encoding layers"""
        current = encoded
        # Reverse order of decoders to match encoding order
        decoders = [self.hex_decode, self.b64_decode, self.rot13]

        for i in range(layers - 1, -1, -1):
            decoder = decoders[i % len(decoders)]
            try:
                current = decoder(current)
            except Exception as e:
                print(f"Error decoding layer {i}: {e}", file=sys.stderr)
                return None

        return current

    def obfuscate_with_hash(self, command: str) -> Tuple[str, str]:
        """Obfuscate with hash signature"""
        cmd_hash = hashlib.sha256(command.encode()).hexdigest()
        encoded = self.b64_encode(command)
        return encoded, cmd_hash

    def verify_obfuscated(self, encoded: str, expected_hash: str) -> bool:
        """Verify obfuscated command hash"""
        try:
            decoded = self.b64_decode(encoded)
            cmd_hash = hashlib.sha256(decoded.encode()).hexdigest()
            return cmd_hash == expected_hash
        except:
            return False

    def character_substitution(self, command: str) -> str:
        """Simple character substitution cipher"""
        mapping = {
            'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5',
            't': '7', 'l': '1', 'g': '9', 'z': '2'
        }
        result = []
        for char in command:
            if char.lower() in mapping and char.islower():
                result.append(mapping[char])
            elif char.lower() in mapping and char.isupper():
                result.append(mapping[char.lower()].upper())
            else:
                result.append(char)
        return ''.join(result)

    def polyalphabetic_cipher(self, command: str, key: str = "secret") -> str:
        """Polyalphabetic cipher (Vigenère-like)"""
        result = []
        key_bytes = key.encode('utf-8')
        key_index = 0

        for char in command:
            if char.isalpha():
                shift = key_bytes[key_index % len(key_bytes)]
                if char.islower():
                    result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
                else:
                    result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
                key_index += 1
            else:
                result.append(char)

        return ''.join(result)

    def dynamic_command_builder(self, *command_parts: str) -> str:
        """Build command dynamically from parts"""
        # Reconstruct with env vars
        result = []
        for part in command_parts:
            if part.startswith('$'):
                var_name = part[1:]
                result.append(self.env_vars.get(var_name, part))
            else:
                result.append(part)
        return ' '.join(result)


class ObfuscationDemo:
    """Demonstration and testing utilities"""

    def __init__(self):
        self.obfuscator = CommandObfuscator()

    def demo_all(self):
        """Run all demonstrations"""
        test_cmd = "ls -la /tmp"

        print("=" * 60)
        print("COMMAND OBFUSCATION DEMONSTRATIONS")
        print("=" * 60)
        print(f"\nOriginal Command: {test_cmd}\n")

        self.demo_hex(test_cmd)
        self.demo_base64(test_cmd)
        self.demo_rot13(test_cmd)
        self.demo_reverse(test_cmd)
        self.demo_caesar(test_cmd)
        self.demo_character_sub(test_cmd)
        self.demo_multi_layer(test_cmd)
        self.demo_hash_verification(test_cmd)
        self.demo_env_vars()

    def demo_hex(self, command: str):
        """Demonstrate hex encoding"""
        print("\n[HEX ENCODING]")
        encoded = self.obfuscator.hex_encode(command)
        print(f"Encoded:  {encoded}")
        decoded = self.obfuscator.hex_decode(encoded)
        print(f"Decoded:  {decoded}")

    def demo_base64(self, command: str):
        """Demonstrate base64 encoding"""
        print("\n[BASE64 ENCODING]")
        encoded = self.obfuscator.b64_encode(command)
        print(f"Encoded:  {encoded}")
        decoded = self.obfuscator.b64_decode(encoded)
        print(f"Decoded:  {decoded}")

    def demo_rot13(self, command: str):
        """Demonstrate ROT13"""
        print("\n[ROT13 ENCODING]")
        encoded = self.obfuscator.rot13(command)
        print(f"Encoded:  {encoded}")
        decoded = self.obfuscator.rot13(encoded)
        print(f"Decoded:  {decoded}")

    def demo_reverse(self, command: str):
        """Demonstrate reverse encoding"""
        print("\n[REVERSE STRING]")
        encoded = self.obfuscator.reverse(command)
        print(f"Encoded:  {encoded}")
        decoded = self.obfuscator.reverse(encoded)
        print(f"Decoded:  {decoded}")

    def demo_caesar(self, command: str):
        """Demonstrate Caesar cipher"""
        print("\n[CAESAR CIPHER (shift=3)]")
        encoded = self.obfuscator.caesar_cipher(command, 3)
        print(f"Encoded:  {encoded}")
        decoded = self.obfuscator.caesar_decipher(encoded, 3)
        print(f"Decoded:  {decoded}")

    def demo_character_sub(self, command: str):
        """Demonstrate character substitution"""
        print("\n[CHARACTER SUBSTITUTION]")
        encoded = self.obfuscator.character_substitution(command)
        print(f"Encoded:  {encoded}")

    def demo_multi_layer(self, command: str):
        """Demonstrate multi-layer obfuscation"""
        print("\n[MULTI-LAYER OBFUSCATION (Hex → Base64 → ROT13)]")
        encoded = self.obfuscator.multi_layer_encode(command, 3)
        print(f"Encoded:  {encoded}")
        decoded = self.obfuscator.multi_layer_decode(encoded, 3)
        print(f"Decoded:  {decoded}")

    def demo_hash_verification(self, command: str):
        """Demonstrate hash verification"""
        print("\n[HASH VERIFICATION]")
        encoded, cmd_hash = self.obfuscator.obfuscate_with_hash(command)
        print(f"Encoded:  {encoded}")
        print(f"Hash:     {cmd_hash}")
        verified = self.obfuscator.verify_obfuscated(encoded, cmd_hash)
        print(f"Verified: {verified}")

    def demo_env_vars(self):
        """Demonstrate environment variable usage"""
        print("\n[ENVIRONMENT VARIABLE CONCATENATION]")
        cmd = self.obfuscator.env_var_concat("$CMD_LS", "$FLAG_L", "$FLAG_A", "/tmp")
        print(f"Built Command: {cmd}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: obfuscator.py <command> [args...]")
        print("\nCommands:")
        print("  demo              - Run all demonstrations")
        print("  hex_encode <cmd>  - Hex encode a command")
        print("  hex_decode <hex>  - Hex decode")
        print("  b64_encode <cmd>  - Base64 encode")
        print("  b64_decode <b64>  - Base64 decode")
        print("  rot13 <cmd>       - ROT13 encode/decode")
        print("  reverse <cmd>     - Reverse string")
        print("  caesar <cmd>      - Caesar cipher (shift=3)")
        print("  multi <cmd>       - Multi-layer encode")
        sys.exit(1)

    command = sys.argv[1]
    obfuscator = CommandObfuscator()

    if command == "demo":
        demo = ObfuscationDemo()
        demo.demo_all()

    elif command == "hex_encode" and len(sys.argv) > 2:
        cmd_text = ' '.join(sys.argv[2:])
        print(obfuscator.hex_encode(cmd_text))

    elif command == "hex_decode" and len(sys.argv) > 2:
        hex_text = sys.argv[2]
        print(obfuscator.hex_decode(hex_text))

    elif command == "b64_encode" and len(sys.argv) > 2:
        cmd_text = ' '.join(sys.argv[2:])
        print(obfuscator.b64_encode(cmd_text))

    elif command == "b64_decode" and len(sys.argv) > 2:
        b64_text = sys.argv[2]
        print(obfuscator.b64_decode(b64_text))

    elif command == "rot13" and len(sys.argv) > 2:
        cmd_text = ' '.join(sys.argv[2:])
        print(obfuscator.rot13(cmd_text))

    elif command == "reverse" and len(sys.argv) > 2:
        cmd_text = ' '.join(sys.argv[2:])
        print(obfuscator.reverse(cmd_text))

    elif command == "caesar" and len(sys.argv) > 2:
        cmd_text = ' '.join(sys.argv[2:])
        print(obfuscator.caesar_cipher(cmd_text, 3))

    elif command == "multi" and len(sys.argv) > 2:
        cmd_text = ' '.join(sys.argv[2:])
        print(obfuscator.multi_layer_encode(cmd_text, 3))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
