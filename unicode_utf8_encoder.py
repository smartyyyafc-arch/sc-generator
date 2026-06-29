#!/usr/bin/env python3
"""
Unicode/UTF-8 Command Encoder
Provides comprehensive international character support for shell commands.
Handles multi-byte UTF-8 encoding, character normalization, and safe command construction.

Features:
- UTF-8 encoding/decoding with multi-byte character support
- Unicode normalization (NFC, NFD, NFKC, NFKD)
- Safe command construction with escaping
- Percent encoding (%XX format)
- URL encoding (RFC 3986)
- Punycode for international domain names
- Emoji and special character handling
- Unicode category detection
- Bidirectional text handling
- Surrogate pair conversion
- BOM (Byte Order Mark) detection and handling

For authorized security research and international tool localization.
"""

import unicodedata
import re
import struct
import binascii
from typing import Tuple, List, Dict, Optional, Set
from enum import Enum
import string


class UnicodeNormalizationForm(Enum):
    """Unicode normalization forms"""
    NFC = 'NFC'    # Canonical Composition
    NFD = 'NFD'    # Canonical Decomposition
    NFKC = 'NFKC'  # Compatibility Composition
    NFKD = 'NFKD'  # Compatibility Decomposition


class UnicodeCategory(Enum):
    """Unicode character categories"""
    LETTER_UPPERCASE = 'Lu'      # Uppercase Letter
    LETTER_LOWERCASE = 'Ll'      # Lowercase Letter
    LETTER_TITLECASE = 'Lt'      # Titlecase Letter
    LETTER_MODIFIER = 'Lm'       # Modifier Letter
    LETTER_OTHER = 'Lo'          # Other Letter
    MARK_NONSPACING = 'Mn'       # Nonspacing Mark
    MARK_SPACING = 'Mc'          # Spacing Mark
    MARK_ENCLOSING = 'Me'        # Enclosing Mark
    NUMBER_DECIMAL = 'Nd'        # Decimal Digit Number
    NUMBER_LETTER = 'Nl'         # Letter Number
    NUMBER_OTHER = 'No'          # Other Number
    PUNCTUATION_CONNECTOR = 'Pc' # Connector Punctuation
    PUNCTUATION_DASH = 'Pd'      # Dash Punctuation
    PUNCTUATION_OPEN = 'Ps'      # Open Punctuation
    PUNCTUATION_CLOSE = 'Pe'     # Close Punctuation
    PUNCTUATION_INITIAL = 'Pi'   # Initial Quote Punctuation
    PUNCTUATION_FINAL = 'Pf'     # Final Quote Punctuation
    PUNCTUATION_OTHER = 'Po'     # Other Punctuation
    SYMBOL_MATH = 'Sm'           # Math Symbol
    SYMBOL_CURRENCY = 'Sc'       # Currency Symbol
    SYMBOL_MODIFIER = 'Sk'       # Modifier Symbol
    SYMBOL_OTHER = 'So'          # Other Symbol
    SEPARATOR_SPACE = 'Zs'       # Space Separator
    SEPARATOR_LINE = 'Zl'        # Line Separator
    SEPARATOR_PARAGRAPH = 'Zp'   # Paragraph Separator
    OTHER_CONTROL = 'Cc'         # Control
    OTHER_FORMAT = 'Cf'          # Format
    OTHER_SURROGATE = 'Cs'       # Surrogate
    OTHER_PRIVATE = 'Co'         # Private Use
    OTHER_NOT_ASSIGNED = 'Cn'    # Not Assigned


class UTF8Encoder:
    """Core UTF-8 encoder with multi-byte character support"""

    def __init__(self):
        self._cache = {}
        self._bom_cache = {}

    def encode_utf8(self, text: str) -> bytes:
        """
        Encode text to UTF-8 bytes.

        Args:
            text: String to encode

        Returns:
            UTF-8 encoded bytes
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")
        return text.encode('utf-8')

    def decode_utf8(self, data: bytes) -> str:
        """
        Decode UTF-8 bytes to text.

        Args:
            data: UTF-8 encoded bytes

        Returns:
            Decoded string
        """
        if not isinstance(data, bytes):
            raise TypeError(f"Expected bytes, got {type(data).__name__}")
        return data.decode('utf-8', errors='replace')

    def get_byte_sequence(self, char: str) -> List[int]:
        """
        Get UTF-8 byte sequence for a character.

        Args:
            char: Single character

        Returns:
            List of byte values (0-255)
        """
        if len(char) != 1:
            raise ValueError("Expected single character")
        encoded = char.encode('utf-8')
        return list(encoded)

    def get_codepoint(self, char: str) -> int:
        """
        Get Unicode codepoint for a character.

        Args:
            char: Single character

        Returns:
            Unicode codepoint (0-0x10FFFF)
        """
        if len(char) != 1:
            raise ValueError("Expected single character")
        return ord(char)

    def char_from_codepoint(self, codepoint: int) -> str:
        """
        Get character from Unicode codepoint.

        Args:
            codepoint: Unicode codepoint (0-0x10FFFF)

        Returns:
            Character string
        """
        if not 0 <= codepoint <= 0x10FFFF:
            raise ValueError(f"Invalid codepoint: {codepoint:#x}")
        return chr(codepoint)

    def detect_bom(self, data: bytes) -> Optional[str]:
        """
        Detect Byte Order Mark (BOM) in data.

        Args:
            data: Byte sequence to check

        Returns:
            BOM type: 'UTF-8', 'UTF-16-BE', 'UTF-16-LE', 'UTF-32-BE', 'UTF-32-LE', or None
        """
        if len(data) >= 4:
            if data[:4] == b'\x00\x00\xfe\xff':
                return 'UTF-32-BE'
            if data[:4] == b'\xff\xfe\x00\x00':
                return 'UTF-32-LE'
        if len(data) >= 3:
            if data[:3] == b'\xef\xbb\xbf':
                return 'UTF-8'
        if len(data) >= 2:
            if data[:2] == b'\xfe\xff':
                return 'UTF-16-BE'
            if data[:2] == b'\xff\xfe':
                return 'UTF-16-LE'
        return None

    def add_utf8_bom(self, text: str) -> bytes:
        """
        Add UTF-8 BOM to text and encode.

        Args:
            text: String to encode

        Returns:
            UTF-8 BOM + encoded text
        """
        return b'\xef\xbb\xbf' + text.encode('utf-8')

    def remove_bom(self, data: bytes) -> bytes:
        """
        Remove BOM from byte sequence if present.

        Args:
            data: Byte sequence possibly with BOM

        Returns:
            Bytes without BOM
        """
        bom_type = self.detect_bom(data)
        if bom_type == 'UTF-8':
            return data[3:]
        elif bom_type in ('UTF-16-BE', 'UTF-16-LE'):
            return data[2:]
        elif bom_type in ('UTF-32-BE', 'UTF-32-LE'):
            return data[4:]
        return data


class UnicodeNormalizer:
    """Unicode normalization and canonicalization"""

    def __init__(self):
        self._normalization_cache = {}

    def normalize(self, text: str, form: UnicodeNormalizationForm = UnicodeNormalizationForm.NFC) -> str:
        """
        Normalize Unicode text to specified form.

        Args:
            text: Text to normalize
            form: Normalization form (NFC, NFD, NFKC, NFKD)

        Returns:
            Normalized text
        """
        cache_key = (text, form.value)
        if cache_key in self._normalization_cache:
            return self._normalization_cache[cache_key]

        normalized = unicodedata.normalize(form.value, text)
        self._normalization_cache[cache_key] = normalized
        return normalized

    def normalize_nfc(self, text: str) -> str:
        """Canonical composition normalization"""
        return self.normalize(text, UnicodeNormalizationForm.NFC)

    def normalize_nfd(self, text: str) -> str:
        """Canonical decomposition normalization"""
        return self.normalize(text, UnicodeNormalizationForm.NFD)

    def normalize_nfkc(self, text: str) -> str:
        """Compatibility composition normalization"""
        return self.normalize(text, UnicodeNormalizationForm.NFKC)

    def normalize_nfkd(self, text: str) -> str:
        """Compatibility decomposition normalization"""
        return self.normalize(text, UnicodeNormalizationForm.NFKD)

    def get_character_decomposition(self, char: str) -> Optional[List[str]]:
        """
        Get decomposition of a character.

        Args:
            char: Single character

        Returns:
            List of decomposed characters or None
        """
        if len(char) != 1:
            return None
        decomp = unicodedata.decomposition(char)
        if decomp:
            return decomp.split()
        return None


class PercentEncoder:
    """Percent-encoding (URL encoding) with UTF-8 support"""

    def __init__(self):
        self._unreserved = set(string.ascii_letters + string.digits + '-._~')

    def percent_encode(self, text: str, safe_chars: Optional[str] = None) -> str:
        """
        Percent-encode text (UTF-8 based).

        Args:
            text: Text to encode
            safe_chars: Additional characters not to encode

        Returns:
            Percent-encoded string
        """
        safe = self._unreserved.copy()
        if safe_chars:
            safe.update(safe_chars)

        result = []
        for byte in text.encode('utf-8'):
            char = chr(byte)
            if char in safe:
                result.append(char)
            else:
                result.append(f'%{byte:02X}')
        return ''.join(result)

    def percent_decode(self, encoded: str) -> str:
        """
        Decode percent-encoded string.

        Args:
            encoded: Percent-encoded string

        Returns:
            Decoded text
        """
        # Replace %XX sequences with bytes
        def replacer(match):
            hex_str = match.group(1)
            return bytes([int(hex_str, 16)])

        # Decode UTF-8 sequences
        pattern = rb'%([0-9A-Fa-f]{2})'
        encoded_bytes = encoded.encode('ascii')
        decoded_bytes = re.sub(pattern, lambda m: bytes([int(m.group(1), 16)]), encoded_bytes)
        return decoded_bytes.decode('utf-8', errors='replace')

    def url_encode(self, text: str, safe_chars: str = '') -> str:
        """
        URL-encode text (RFC 3986 compliant).

        Args:
            text: Text to encode
            safe_chars: Characters not to encode

        Returns:
            URL-encoded string
        """
        safe = self._unreserved.copy()
        safe.update(safe_chars)
        return self.percent_encode(text, ''.join(safe))


class UnicodeAnalyzer:
    """Analyze Unicode text properties"""

    def __init__(self):
        self._category_cache = {}

    def get_category(self, char: str) -> str:
        """
        Get Unicode category of character.

        Args:
            char: Single character

        Returns:
            Category code (e.g., 'Lu', 'Ll', 'Nd')
        """
        if len(char) != 1:
            raise ValueError("Expected single character")
        return unicodedata.category(char)

    def get_name(self, char: str) -> Optional[str]:
        """
        Get Unicode name of character.

        Args:
            char: Single character

        Returns:
            Unicode name or None
        """
        if len(char) != 1:
            raise ValueError("Expected single character")
        try:
            return unicodedata.name(char)
        except ValueError:
            return None

    def is_printable(self, text: str) -> bool:
        """Check if text contains only printable characters"""
        return all(unicodedata.category(c) != 'Cc' for c in text)

    def is_bidi_text(self, text: str) -> bool:
        """Check if text contains bidirectional characters"""
        bidi_categories = {'R', 'AL', 'RLE', 'RLO', 'PDF', 'LRE', 'LRO'}
        for char in text:
            # Simple check for RTL marks
            if ord(char) in (0x202A, 0x202B, 0x202C, 0x202D, 0x202E,  # BiDi override
                            0x200E, 0x200F):  # BiDi marks
                return True
        return False

    def detect_scripts(self, text: str) -> Set[str]:
        """
        Detect Unicode scripts in text.

        Args:
            text: Text to analyze

        Returns:
            Set of script names (Latin, Greek, Cyrillic, Arabic, Han, etc.)
        """
        scripts = set()
        script_ranges = {
            'Latin': (0x0000, 0x024F),
            'Greek': (0x0370, 0x03FF),
            'Cyrillic': (0x0400, 0x04FF),
            'Arabic': (0x0600, 0x06FF),
            'Hebrew': (0x0590, 0x05FF),
            'Devanagari': (0x0900, 0x097F),
            'Han': (0x4E00, 0x9FFF),
            'Hiragana': (0x3040, 0x309F),
            'Katakana': (0x30A0, 0x30FF),
            'Hangul': (0xAC00, 0xD7AF),
            'Emoji': (0x1F300, 0x1F9FF),
        }

        for char in text:
            codepoint = ord(char)
            for script, (start, end) in script_ranges.items():
                if start <= codepoint <= end:
                    scripts.add(script)
                    break

        return scripts

    def get_width(self, char: str) -> int:
        """
        Get display width of character (East Asian Width).

        Args:
            char: Single character

        Returns:
            Width: 1 (narrow/neutral) or 2 (wide/fullwidth)
        """
        if len(char) != 1:
            raise ValueError("Expected single character")
        ea_width = unicodedata.east_asian_width(char)
        return 2 if ea_width in ('W', 'F') else 1


class SafeCommandBuilder:
    """Build safe commands with Unicode text"""

    def __init__(self):
        self.encoder = UTF8Encoder()
        self.analyzer = UnicodeAnalyzer()
        self.percent_encoder = PercentEncoder()

    def escape_for_shell(self, text: str, shell: str = 'bash') -> str:
        """
        Escape text for safe shell usage.

        Args:
            text: Text to escape
            shell: Shell type ('bash', 'sh', 'cmd', 'powershell')

        Returns:
            Escaped text
        """
        if shell in ('bash', 'sh'):
            # Single-quote everything, escape embedded single quotes
            return "'" + text.replace("'", "'\\''") + "'"
        elif shell == 'cmd':
            # Escape special CMD characters
            special = '^<>|&'
            escaped = text
            for char in special:
                escaped = escaped.replace(char, '^' + char)
            return escaped
        elif shell == 'powershell':
            # PowerShell escaping
            special = '`$"\'@'
            escaped = text
            for char in special:
                escaped = escaped.replace(char, '`' + char)
            return "'" + escaped + "'"
        else:
            return text

    def build_command(self, command: str, *args: str, shell: str = 'bash') -> str:
        """
        Build a safe command with Unicode arguments.

        Args:
            command: Command name
            args: Command arguments
            shell: Target shell

        Returns:
            Complete command string
        """
        escaped_args = [self.escape_for_shell(arg, shell) for arg in args]
        return ' '.join([command] + escaped_args)

    def build_command_with_encoding(self, command: str, *args: str,
                                   encoding: str = 'percent') -> str:
        """
        Build command with encoded arguments.

        Args:
            command: Command name
            args: Command arguments
            encoding: Encoding type ('percent', 'utf8', 'hex')

        Returns:
            Command with encoded arguments
        """
        if encoding == 'percent':
            encoded_args = [self.percent_encoder.percent_encode(arg) for arg in args]
        elif encoding == 'utf8':
            encoded_args = [self.encoder.encode_utf8(arg).hex() for arg in args]
        elif encoding == 'hex':
            encoded_args = [''.join(f'{b:02x}' for b in self.encoder.encode_utf8(arg)) for arg in args]
        else:
            raise ValueError(f"Unknown encoding: {encoding}")

        return ' '.join([command] + encoded_args)


class EmojiHandler:
    """Handle emoji and special Unicode characters"""

    def __init__(self):
        self.analyzer = UnicodeAnalyzer()

    def extract_emoji(self, text: str) -> List[str]:
        """
        Extract emoji from text.

        Args:
            text: Text to search

        Returns:
            List of emoji characters found
        """
        emoji = []
        for char in text:
            if ord(char) in range(0x1F300, 0x1F9FF):
                emoji.append(char)
        return emoji

    def has_emoji(self, text: str) -> bool:
        """Check if text contains emoji"""
        return len(self.extract_emoji(text)) > 0

    def remove_emoji(self, text: str) -> str:
        """Remove all emoji from text"""
        return ''.join(char for char in text if ord(char) not in range(0x1F300, 0x1F9FF))

    def count_emoji(self, text: str) -> int:
        """Count emoji in text"""
        return len(self.extract_emoji(text))


class PunycodeHandler:
    """Handle Punycode for internationalized domain names"""

    def encode_punycode(self, domain: str) -> str:
        """
        Encode international domain name to Punycode.

        Args:
            domain: International domain name

        Returns:
            Punycode ASCII domain
        """
        try:
            # Python's built-in idna encoding
            return domain.encode('idna').decode('ascii')
        except Exception:
            return domain

    def decode_punycode(self, encoded: str) -> str:
        """
        Decode Punycode to international domain name.

        Args:
            encoded: Punycode ASCII domain

        Returns:
            International domain name
        """
        try:
            return encoded.encode('ascii').decode('idna')
        except Exception:
            return encoded


class UnicodeUTF8Encoder:
    """Main encoder combining all Unicode/UTF-8 functionality"""

    def __init__(self):
        self.utf8 = UTF8Encoder()
        self.normalizer = UnicodeNormalizer()
        self.percent_encoder = PercentEncoder()
        self.analyzer = UnicodeAnalyzer()
        self.command_builder = SafeCommandBuilder()
        self.emoji_handler = EmojiHandler()
        self.punycode = PunycodeHandler()

    def encode_command(self, text: str, method: str = 'percent') -> str:
        """
        Encode text for safe command usage.

        Args:
            text: Text to encode
            method: Encoding method ('percent', 'utf8-hex', 'normalized')

        Returns:
            Encoded text
        """
        if method == 'percent':
            return self.percent_encoder.percent_encode(text)
        elif method == 'utf8-hex':
            utf8_bytes = self.utf8.encode_utf8(text)
            return ''.join(f'\\x{b:02x}' for b in utf8_bytes)
        elif method == 'normalized':
            return self.normalizer.normalize_nfc(text)
        else:
            raise ValueError(f"Unknown encoding method: {method}")

    def decode_command(self, encoded: str, method: str = 'percent') -> str:
        """
        Decode text from safe command encoding.

        Args:
            encoded: Encoded text
            method: Encoding method ('percent', 'utf8-hex')

        Returns:
            Decoded text
        """
        if method == 'percent':
            return self.percent_encoder.percent_decode(encoded)
        elif method == 'utf8-hex':
            # Simple hex string decoder
            hex_str = encoded.replace('\\x', '')
            byte_array = bytes.fromhex(hex_str)
            return self.utf8.decode_utf8(byte_array)
        else:
            raise ValueError(f"Unknown decoding method: {method}")

    def get_encoding_info(self, text: str) -> Dict:
        """
        Get comprehensive encoding information for text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with encoding information
        """
        utf8_bytes = self.utf8.encode_utf8(text)
        return {
            'original': text,
            'utf8_bytes': utf8_bytes.hex(),
            'utf8_length': len(utf8_bytes),
            'char_count': len(text),
            'percent_encoded': self.percent_encoder.percent_encode(text),
            'normalized_nfc': self.normalizer.normalize_nfc(text),
            'normalized_nfd': self.normalizer.normalize_nfd(text),
            'scripts': list(self.analyzer.detect_scripts(text)),
            'has_emoji': self.emoji_handler.has_emoji(text),
            'emoji_count': self.emoji_handler.count_emoji(text),
            'is_bidi': self.analyzer.is_bidi_text(text),
            'characters': [
                {
                    'char': char,
                    'codepoint': ord(char),
                    'codepoint_hex': f'U+{ord(char):04X}',
                    'name': self.analyzer.get_name(char),
                    'category': self.analyzer.get_category(char),
                    'utf8_bytes': char.encode('utf-8').hex(),
                    'width': self.analyzer.get_width(char)
                }
                for char in text
            ]
        }


# Convenience functions for direct usage
def encode_utf8(text: str) -> bytes:
    """Quickly encode text to UTF-8"""
    encoder = UnicodeUTF8Encoder()
    return encoder.utf8.encode_utf8(text)


def decode_utf8(data: bytes) -> str:
    """Quickly decode UTF-8 bytes"""
    encoder = UnicodeUTF8Encoder()
    return encoder.utf8.decode_utf8(data)


def percent_encode(text: str) -> str:
    """Quickly percent-encode text"""
    encoder = UnicodeUTF8Encoder()
    return encoder.percent_encoder.percent_encode(text)


def percent_decode(encoded: str) -> str:
    """Quickly percent-decode text"""
    encoder = UnicodeUTF8Encoder()
    return encoder.percent_encoder.percent_decode(encoded)


def normalize(text: str, form: str = 'NFC') -> str:
    """Quickly normalize text"""
    encoder = UnicodeUTF8Encoder()
    form_map = {
        'NFC': UnicodeNormalizationForm.NFC,
        'NFD': UnicodeNormalizationForm.NFD,
        'NFKC': UnicodeNormalizationForm.NFKC,
        'NFKD': UnicodeNormalizationForm.NFKD,
    }
    return encoder.normalizer.normalize(text, form_map.get(form, UnicodeNormalizationForm.NFC))


def analyze_text(text: str) -> Dict:
    """Quickly get complete text analysis"""
    encoder = UnicodeUTF8Encoder()
    return encoder.get_encoding_info(text)


if __name__ == '__main__':
    # Example usage
    encoder = UnicodeUTF8Encoder()

    # Example 1: Basic UTF-8 encoding
    print("=== Basic UTF-8 Encoding ===")
    text = "Hello, 世界! 🌍"
    print(f"Original: {text}")
    print(f"UTF-8 bytes: {encoder.utf8.encode_utf8(text).hex()}")

    # Example 2: Percent encoding
    print("\n=== Percent Encoding ===")
    print(f"Percent encoded: {encoder.percent_encoder.percent_encode(text)}")

    # Example 3: Unicode normalization
    print("\n=== Unicode Normalization ===")
    accented = "café"
    print(f"Original: {accented}")
    print(f"NFC: {encoder.normalizer.normalize_nfc(accented)}")
    print(f"NFD: {encoder.normalizer.normalize_nfd(accented)}")

    # Example 4: Text analysis
    print("\n=== Text Analysis ===")
    info = encoder.get_encoding_info("Hello 日本語")
    print(f"Character count: {info['char_count']}")
    print(f"UTF-8 byte length: {info['utf8_length']}")
    print(f"Detected scripts: {', '.join(info['scripts'])}")

    # Example 5: Safe command building
    print("\n=== Safe Command Building ===")
    cmd = encoder.command_builder.escape_for_shell("echo 'Hello & goodbye'", 'bash')
    print(f"Bash-safe: {cmd}")

    # Example 6: Emoji handling
    print("\n=== Emoji Handling ===")
    emoji_text = "Hello 👋 World 🌍"
    print(f"Original: {emoji_text}")
    print(f"Has emoji: {encoder.emoji_handler.has_emoji(emoji_text)}")
    print(f"Emoji count: {encoder.emoji_handler.count_emoji(emoji_text)}")
    print(f"Without emoji: {encoder.emoji_handler.remove_emoji(emoji_text)}")

    # Example 7: Punycode for domains
    print("\n=== Punycode Domain Names ===")
    domain = "münchen.de"
    print(f"International: {domain}")
    print(f"Punycode: {encoder.punycode.encode_punycode(domain)}")
