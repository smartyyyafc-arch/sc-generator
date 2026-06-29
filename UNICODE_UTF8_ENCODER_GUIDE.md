# Unicode/UTF-8 Command Encoder - Comprehensive Guide

## Overview

The **Unicode/UTF-8 Command Encoder** provides robust international character support for shell commands and system operations. It handles multi-byte UTF-8 encoding, character normalization, safe escaping, and encoding transformations for international text.

## Features

### Core Features
- **UTF-8 Encoding/Decoding**: Multi-byte character support for all Unicode characters
- **Unicode Normalization**: NFC, NFD, NFKC, NFKD forms for canonical text representation
- **Percent Encoding**: URL-safe %XX encoding with UTF-8 support
- **Safe Command Construction**: Shell-safe escaping for bash, sh, cmd, PowerShell
- **Character Analysis**: Unicode category detection, script identification
- **BOM Handling**: Byte Order Mark detection and removal

### Advanced Features
- **Emoji Support**: Extraction, detection, counting, removal of emoji characters
- **Punycode**: International domain name (IDN) encoding/decoding
- **Bidirectional Text**: RTL/LTR text detection
- **East Asian Width**: Proper width calculation for CJK characters
- **Character Metadata**: Unicode names, categories, codepoint values

## Installation

```bash
# Copy the encoder to your project
cp unicode_utf8_encoder.py /your/project/path/

# No external dependencies required (uses Python stdlib)
```

## Quick Start

### Basic UTF-8 Encoding

```python
from unicode_utf8_encoder import UnicodeUTF8Encoder

encoder = UnicodeUTF8Encoder()

# Encode text to UTF-8
text = "Hello, 世界"
utf8_bytes = encoder.utf8.encode_utf8(text)
print(utf8_bytes)  # b'Hello, \xe4\xb8\x96\xe7\x95\x8c'

# Decode back
decoded = encoder.utf8.decode_utf8(utf8_bytes)
print(decoded)  # "Hello, 世界"
```

### Percent Encoding (URL-Safe)

```python
# Percent-encode text
text = "Hello World & Special"
encoded = encoder.percent_encoder.percent_encode(text)
print(encoded)  # "Hello%20World%20%26%20Special"

# Decode back
decoded = encoder.percent_encoder.percent_decode(encoded)
print(decoded)  # "Hello World & Special"
```

### Unicode Normalization

```python
# Normalize to NFC (Canonical Composition)
accented = "café"
normalized = encoder.normalizer.normalize_nfc(accented)

# Handle combining characters consistently
nfd = encoder.normalizer.normalize_nfd(accented)  # Decomposed
nfkc = encoder.normalizer.normalize_nfkc(accented)  # Compatibility composition
```

### Safe Command Building

```python
# Escape for shell safety
arg = "Hello 'World' & special"
bash_safe = encoder.command_builder.escape_for_shell(arg, 'bash')
print(bash_safe)  # 'Hello '\''World'\'' & special'

# Build complete command
cmd = encoder.command_builder.build_command(
    "echo", "Hello", "World & More"
)
```

### Text Analysis

```python
# Get complete encoding information
info = encoder.get_encoding_info("Hello 日本語 🌍")

print(info['utf8_bytes'])       # Hex representation
print(info['char_count'])       # Character count
print(info['scripts'])          # ['Latin', 'Han']
print(info['has_emoji'])        # True
print(info['emoji_count'])      # 1
```

## API Reference

### UTF8Encoder

Core UTF-8 encoding and decoding operations.

```python
encoder = UTF8Encoder()

# Encode to UTF-8
bytes_data = encoder.encode_utf8("text")

# Decode from UTF-8
text = encoder.decode_utf8(b'text')

# Get byte sequence for character
bytes_list = encoder.get_byte_sequence('é')  # [195, 169]

# Get Unicode codepoint
codepoint = encoder.get_codepoint('é')  # 0xE9 (233)

# Create character from codepoint
char = encoder.char_from_codepoint(0x4E16)  # '世'

# BOM operations
bom_type = encoder.detect_bom(b'\xef\xbb\xbftext')  # 'UTF-8'
with_bom = encoder.add_utf8_bom("text")
without_bom = encoder.remove_bom(b'\xef\xbb\xbftext')
```

### UnicodeNormalizer

Unicode normalization to different canonical forms.

```python
normalizer = UnicodeNormalizer()

# Normalize to specific form
nfc = normalizer.normalize_nfc("café")   # Composed
nfd = normalizer.normalize_nfd("café")   # Decomposed
nfkc = normalizer.normalize_nfkc("ﬁ")    # "fi"
nfkd = normalizer.normalize_nfkd("ﬁ")    # "fi" (decomposed)

# Get character decomposition
decomp = normalizer.get_character_decomposition('é')
```

### PercentEncoder

URL and percent encoding with UTF-8 support.

```python
encoder = PercentEncoder()

# Percent encode
encoded = encoder.percent_encode("Hello World")  # "Hello%20World"

# With safe characters (not encoded)
encoded = encoder.percent_encode("user@example.com", safe_chars='@.')

# Percent decode
decoded = encoder.percent_decode("Hello%20World")

# URL encode (RFC 3986)
url_encoded = encoder.url_encode("search=café")
```

### UnicodeAnalyzer

Analyze Unicode character properties and text composition.

```python
analyzer = UnicodeAnalyzer()

# Get Unicode category
cat = analyzer.get_category('A')     # 'Lu' (Uppercase Letter)
cat = analyzer.get_category('5')     # 'Nd' (Decimal Digit)

# Get Unicode name
name = analyzer.get_name('é')        # 'LATIN SMALL LETTER E WITH ACUTE'

# Check text properties
is_printable = analyzer.is_printable("Hello")
is_bidi = analyzer.is_bidi_text("Hello עברית")

# Detect scripts
scripts = analyzer.detect_scripts("Hello 日本語 مرحبا")
# Returns: {'Latin', 'Han', 'Arabic'}

# Get East Asian Width
width = analyzer.get_width('中')  # 2 (fullwidth)
```

### SafeCommandBuilder

Build safe commands with proper escaping.

```python
builder = SafeCommandBuilder()

# Escape for specific shell
bash_escaped = builder.escape_for_shell("Hello 'World'", 'bash')
cmd_escaped = builder.escape_for_shell("test<>|&", 'cmd')
ps_escaped = builder.escape_for_shell("Hello $var", 'powershell')

# Build complete command
cmd = builder.build_command("echo", "arg1", "arg2")

# Build with encoding
cmd = builder.build_command_with_encoding(
    "echo", "Hello", encoding='percent'
)
```

### EmojiHandler

Work with emoji and special Unicode characters.

```python
handler = EmojiHandler()

# Extract emoji
emoji_list = handler.extract_emoji("Hello 👋 World 🌍")
# Returns: ['👋', '🌍']

# Check for emoji
has_emoji = handler.has_emoji("Hello 🌍")  # True

# Remove emoji
text = handler.remove_emoji("Hello 👋 World")  # "Hello  World"

# Count emoji
count = handler.count_emoji("😀😃😄")  # 3
```

### PunycodeHandler

Handle internationalized domain names.

```python
handler = PunycodeHandler()

# Encode to Punycode
encoded = handler.encode_punycode("münchen.de")
# Returns: "xn--mnchen-3ya.de"

# Decode from Punycode
decoded = handler.decode_punycode("xn--mnchen-3ya.de")
# Returns: "münchen.de"
```

### UnicodeUTF8Encoder (Main)

Complete encoder combining all functionality.

```python
encoder = UnicodeUTF8Encoder()

# Encode command
encoded = encoder.encode_command("Hello 世界", method='percent')
encoded = encoder.encode_command("Hello", method='utf8-hex')

# Decode command
decoded = encoder.decode_command(encoded, method='percent')

# Get full encoding info
info = encoder.get_encoding_info("Text")
# Returns dict with:
# - utf8_bytes, utf8_length
# - char_count
# - percent_encoded
# - normalized (NFC, NFD)
# - scripts detected
# - emoji info
# - character-by-character details
```

## Convenience Functions

Quick-access functions for common operations:

```python
from unicode_utf8_encoder import (
    encode_utf8,
    decode_utf8,
    percent_encode,
    percent_decode,
    normalize,
    analyze_text
)

# UTF-8
utf8_bytes = encode_utf8("text")
text = decode_utf8(b'text')

# Percent encoding
encoded = percent_encode("text")
decoded = percent_decode(encoded)

# Normalization
normalized = normalize("café", 'NFC')

# Analysis
info = analyze_text("text")
```

## Unicode Normalization Forms

### NFC (Canonical Composition)
- Combines characters with their combining marks
- Smallest representation
- Default for most modern systems
- Example: é = U+00E9 (precomposed)

### NFD (Canonical Decomposition)
- Decomposes characters into base + combining marks
- Useful for character-by-character processing
- Example: é = e (U+0065) + ◌́ (U+0301)

### NFKC (Compatibility Composition)
- Includes compatibility decompositions
- Converts compatibility characters to their equivalents
- Example: ﬁ (ligature) → fi

### NFKD (Compatibility Decomposition)
- Combines compatibility and canonical decomposition
- Most expanded form

## Unicode Categories

| Category | Description | Examples |
|----------|-------------|----------|
| Lu | Uppercase Letter | A, Ñ |
| Ll | Lowercase Letter | a, ñ |
| Lt | Titlecase Letter | ª |
| Lm | Modifier Letter | ʰ |
| Lo | Other Letter | ა, ◌ٰ |
| Mn | Nonspacing Mark | ◌́ |
| Mc | Spacing Mark | ◌ु |
| Me | Enclosing Mark | ◌⃣ |
| Nd | Decimal Digit Number | 0-9, ٠-٩ |
| Nl | Letter Number | Ⅰ, Ⅱ |
| No | Other Number | ½, ¼ |
| Pc | Connector Punctuation | _ |
| Pd | Dash Punctuation | -, – |
| Ps | Open Punctuation | ( , [ |
| Pe | Close Punctuation | ) , ] |
| Pi | Initial Quote | « |
| Pf | Final Quote | » |
| Po | Other Punctuation | ! , ? |
| Sm | Math Symbol | + , = |
| Sc | Currency Symbol | $ , € |
| Sk | Modifier Symbol | ˆ |
| So | Other Symbol | © , ® |
| Zs | Space Separator | (space) |
| Zl | Line Separator | (line sep) |
| Zp | Paragraph Separator | (para sep) |
| Cc | Control | (control chars) |
| Cf | Format | (zero-width, etc) |
| Cs | Surrogate | (UTF-16) |
| Co | Private Use | (user-defined) |
| Cn | Not Assigned | (unassigned) |

## Real-World Examples

### Example 1: Internationalized Filenames

```python
from unicode_utf8_encoder import UnicodeUTF8Encoder

encoder = UnicodeUTF8Encoder()

# Create safe filename from international text
filename = "文档_报告_2024.txt"
safe = encoder.percent_encoder.percent_encode(filename)
print(safe)  # Can be used in URLs or file paths
```

### Example 2: Database Query with Unicode

```python
from unicode_utf8_encoder import UnicodeUTF8Encoder

encoder = UnicodeUTF8Encoder()

# Normalize database input for consistency
user_input = "café"
normalized = encoder.normalizer.normalize_nfc(user_input)
# Use normalized for database queries to ensure matching
```

### Example 3: Log Messages with Emoji

```python
from unicode_utf8_encoder import UnicodeUTF8Encoder

encoder = UnicodeUTF8Encoder()

log_msg = "Task completed ✓ Success 🎉"
info = encoder.get_encoding_info(log_msg)

print(f"Characters: {info['char_count']}")
print(f"UTF-8 bytes: {info['utf8_length']}")
print(f"Emoji: {info['emoji_count']}")
```

### Example 4: Command Line Arguments

```python
from unicode_utf8_encoder import UnicodeUTF8Encoder

encoder = UnicodeUTF8Encoder()

# Safe passing of arguments with special characters
args = [
    "Hello & goodbye",
    "path/to/file",
    "user@domain.com"
]

safe_args = [
    encoder.command_builder.escape_for_shell(arg, 'bash')
    for arg in args
]

cmd = "process " + " ".join(safe_args)
```

### Example 5: International Domain Names

```python
from unicode_utf8_encoder import UnicodeUTF8Encoder

encoder = UnicodeUTF8Encoder()

# Convert to Punycode for DNS
domain = "münchen.de"
punycode = encoder.punycode.encode_punycode(domain)
print(punycode)  # "xn--mnchen-3ya.de"

# Use in HTTP requests, DNS queries, etc.
```

### Example 6: Bidirectional Text Handling

```python
from unicode_utf8_encoder import UnicodeUTF8Encoder

encoder = UnicodeUTF8Encoder()

# Detect mixed LTR/RTL content
text = "Hello שלום World"
is_bidi = encoder.analyzer.is_bidi_text(text)
scripts = encoder.analyzer.detect_scripts(text)

print(f"Mixed direction: {is_bidi}")
print(f"Scripts: {scripts}")  # {'Latin', 'Hebrew'}
```

## Character Byte Sequences

### Common Multi-Byte Sequences

**2-byte characters (U+0080 to U+07FF)**
```
Example: é (U+00E9)
UTF-8: C3 A9 (0xC3 = 110xxxxx, 0xA9 = 10xxxxxx)
```

**3-byte characters (U+0800 to U+FFFF)**
```
Example: 世 (U+4E16)
UTF-8: E4 B8 96 (0xE4 = 1110xxxx, 0xB8 = 10xxxxxx, 0x96 = 10xxxxxx)
```

**4-byte characters (U+10000 to U+10FFFF)**
```
Example: 🌍 (U+1F30D)
UTF-8: F0 9F 8C 8D (0xF0 = 11110xxx, 0x9F = 10xxxxxx, etc)
```

## Performance Considerations

- **Caching**: Normalization results are cached to improve repeated operations
- **Memory**: Full analysis can be memory-intensive for very large texts
- **Speed**: Percent encoding/decoding is O(n) for text length
- **Unicode Database**: Category detection requires Unicode database access

## Testing

Run comprehensive test suite:

```bash
python3 test_unicode_utf8_encoder.py
```

Test coverage includes:
- UTF-8 encoding/decoding (ASCII, Unicode, emoji, invalid sequences)
- Unicode normalization (NFC, NFD, NFKC, NFKD)
- Percent encoding/decoding
- Character analysis and script detection
- Emoji handling
- Command escaping for multiple shells
- Punycode encoding/decoding
- Real-world scenarios
- Edge cases

## Limitations

1. **Codepoint Range**: Valid codepoints are U+0000 to U+10FFFF
2. **Surrogates**: UTF-16 surrogates (U+D800-U+DFFF) cannot be encoded
3. **Normalization**: Preserves semantic equivalence but not visual appearance
4. **Shell Support**: Limited to bash, sh, cmd, PowerShell (extensible for others)
5. **Emoji Detection**: Uses codepoint ranges, may not cover all emoji variations

## Security Considerations

- Always normalize user input for database operations
- Escape commands properly for the target shell
- Validate input character encoding before processing
- Be aware of homograph attacks in international domains (punycode squatting)
- Use percent encoding for URL components
- Handle BOM markers appropriately for file formats

## Future Enhancements

- Support for additional shell types (zsh, fish, tcsh)
- Grapheme cluster support (for complex scripts)
- Unicode regex support
- Transliteration support
- Additional encoding formats (URL encoding variants, etc.)

## References

- [Unicode Standard](https://unicode.org/)
- [RFC 3629 - UTF-8](https://tools.ietf.org/html/rfc3629)
- [RFC 3492 - Punycode](https://tools.ietf.org/html/rfc3492)
- [RFC 3986 - URI Generic Syntax](https://tools.ietf.org/html/rfc3986)
- [Python unicodedata Module](https://docs.python.org/3/library/unicodedata.html)
