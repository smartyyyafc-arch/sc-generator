# Unicode/UTF-8 Encoder - Quick Reference Card

## Import
```python
from unicode_utf8_encoder import UnicodeUTF8Encoder, UTF8Encoder
```

## Main Encoder
```python
encoder = UnicodeUTF8Encoder()
```

## UTF-8 Operations
```python
# Encode to UTF-8 bytes
bytes_data = encoder.utf8.encode_utf8("Hello 世界")

# Decode from UTF-8
text = encoder.utf8.decode_utf8(b'Hello \xe4\xb8\x96')

# Get byte sequence
bytes_list = encoder.utf8.get_byte_sequence('é')  # [195, 169]

# Get/create from codepoint
codepoint = encoder.utf8.get_codepoint('世')  # 0x4E16
char = encoder.utf8.char_from_codepoint(0x4E16)  # '世'
```

## Normalization
```python
# NFC (Canonical Composition - compact)
nfc = encoder.normalizer.normalize_nfc("café")

# NFD (Canonical Decomposition - expanded)
nfd = encoder.normalizer.normalize_nfd("café")

# NFKC (Compatibility Composition)
nfkc = encoder.normalizer.normalize_nfkc("ﬁle")  # "file"

# NFKD (Compatibility Decomposition)
nfkd = encoder.normalizer.normalize_nfkd("ﬁle")  # "file"
```

## Percent Encoding
```python
# Percent-encode (URL-safe)
encoded = encoder.percent_encoder.percent_encode("Hello World")
# "Hello%20World"

# Percent-decode
decoded = encoder.percent_encoder.percent_decode("Hello%20World")
# "Hello World"

# With safe characters
encoded = encoder.percent_encoder.percent_encode(
    "user@domain.com", 
    safe_chars='@.'
)

# URL encode (RFC 3986)
url_safe = encoder.percent_encoder.url_encode("search=café")
```

## Safe Commands
```python
# Escape for shell
bash_safe = encoder.command_builder.escape_for_shell("'Hello'", 'bash')
# 'sh: '\'Hello\'\"'

cmd_safe = encoder.command_builder.escape_for_shell("test&<>", 'cmd')
# test^&^<^>

ps_safe = encoder.command_builder.escape_for_shell("$var", 'powershell')

# Build commands
cmd = encoder.command_builder.build_command("echo", "arg1", "arg2")
```

## Character Analysis
```python
# Get Unicode category
cat = encoder.analyzer.get_category('A')  # 'Lu' (uppercase)
cat = encoder.analyzer.get_category('5')  # 'Nd' (digit)

# Get character name
name = encoder.analyzer.get_name('é')
# 'LATIN SMALL LETTER E WITH ACUTE'

# Detect scripts
scripts = encoder.analyzer.detect_scripts("Hello 世界")
# {'Latin', 'Han'}

# East Asian Width
width = encoder.analyzer.get_width('中')  # 2 (fullwidth)

# Check properties
printable = encoder.analyzer.is_printable("Hello")  # True
bidi = encoder.analyzer.is_bidi_text("Hello עברית")  # False/True
```

## Emoji Operations
```python
handler = encoder.emoji_handler

# Extract emoji
emoji_list = handler.extract_emoji("Hello 👋 🌍")  # ['👋', '🌍']

# Check for emoji
has = handler.has_emoji("Hello 🌍")  # True

# Count emoji
count = handler.count_emoji("😀😃😄")  # 3

# Remove emoji
text = handler.remove_emoji("Hello 👋")  # "Hello "
```

## Punycode
```python
punycode = encoder.punycode

# Encode to Punycode
encoded = punycode.encode_punycode("münchen.de")
# "xn--mnchen-3ya.de"

# Decode from Punycode
decoded = punycode.decode_punycode("xn--mnchen-3ya.de")
# "münchen.de"
```

## BOM Handling
```python
# Detect BOM
bom_type = encoder.utf8.detect_bom(b'\xef\xbb\xbftext')
# 'UTF-8', 'UTF-16-BE', 'UTF-16-LE', 'UTF-32-BE', 'UTF-32-LE', or None

# Add UTF-8 BOM
with_bom = encoder.utf8.add_utf8_bom("text")

# Remove BOM
clean = encoder.utf8.remove_bom(b'\xef\xbb\xbftext')
```

## Complete Text Analysis
```python
info = encoder.get_encoding_info("Hello 世界 🌍")

# Dictionary contains:
# - original: str
# - utf8_bytes: hex string
# - utf8_length: int
# - char_count: int
# - percent_encoded: str
# - normalized_nfc: str
# - normalized_nfd: str
# - scripts: list
# - has_emoji: bool
# - emoji_count: int
# - is_bidi: bool
# - characters: list of dicts with:
#   - char, codepoint, codepoint_hex
#   - name, category, utf8_bytes, width
```

## Convenience Functions
```python
from unicode_utf8_encoder import (
    encode_utf8,          # Quick UTF-8 encode
    decode_utf8,          # Quick UTF-8 decode
    percent_encode,       # Quick percent encode
    percent_decode,       # Quick percent decode
    normalize,            # Quick normalize (param: 'NFC'/'NFD'/'NFKC'/'NFKD')
    analyze_text,         # Quick full analysis
)

bytes_data = encode_utf8("Hello")
text = decode_utf8(b'Hello')
encoded = percent_encode("text")
decoded = percent_decode(encoded)
normalized = normalize("café", 'NFC')
info = analyze_text("text")
```

## Common Unicode Categories
| Code | Name | Example |
|------|------|---------|
| Lu | Uppercase Letter | A, Ñ |
| Ll | Lowercase Letter | a, ñ |
| Nd | Decimal Digit | 0-9 |
| Zs | Space Separator | (space) |
| Po | Other Punctuation | ! , ? |
| Sm | Math Symbol | + , = |
| Sc | Currency Symbol | $ , € |
| So | Other Symbol | © , ® |

## Unicode Normalization Forms
| Form | Purpose | Example |
|------|---------|---------|
| NFC | Canonical Composition | café (compact) |
| NFD | Canonical Decomposition | café (e + accent) |
| NFKC | Compatibility Composition | ﬁ → fi |
| NFKD | Compatibility Decomposition | ﬁ → f + i |

## Script Names
```
'Latin'           # Latin alphabet
'Cyrillic'        # Russian, Serbian, etc.
'Arabic'          # Arabic script
'Hebrew'          # Hebrew script
'Han'             # Chinese/Japanese/Korean
'Hiragana'        # Japanese hiragana
'Katakana'        # Japanese katakana
'Hangul'          # Korean hangul
'Devanagari'      # Hindi, Sanskrit
'Emoji'           # Emoji characters
```

## Common Patterns

### Safe File Path
```python
# Create safe filename
filename = encoder.percent_encoder.percent_encode(
    encoder.normalizer.normalize_nfc(filename)
)
```

### Database Storage
```python
# Normalize for consistency
db_value = encoder.normalizer.normalize_nfc(user_input)
```

### URL Parameter
```python
# Safe URL encoding
param = encoder.percent_encoder.url_encode("key=value with spaces")
```

### Shell Command
```python
# Safe command with arguments
cmd = encoder.command_builder.build_command(
    "process",
    "arg1",
    "arg 2 with spaces"
)
```

### Domain Name
```python
# Convert international domain
dns_safe = encoder.punycode.encode_punycode(domain)
```

## Encoding Comparison

| Method | Use Case | Example |
|--------|----------|---------|
| UTF-8 | Binary/storage | `b'\xc3\xa9'` for é |
| Percent | URLs/URLs | `caf%C3%A9` |
| Normalized | Database/comparison | canonical form |
| Hex | Debug/display | `c3a9` |

## Performance Tips
1. Use UTF-8Encoder for bulk encoding
2. Normalization results are cached
3. Reuse encoder instance
4. Avoid repeated full analysis
5. Use convenience functions for single operations

## Security Notes
- Always escape shell arguments properly
- Normalize user input for database queries
- Validate UTF-8 before processing
- Be aware of homograph attacks (Punycode)
- Use appropriate normalization form for comparison

## Testing
```bash
python3 test_unicode_utf8_encoder.py
# Runs 55 comprehensive tests
```

## Error Handling
```python
try:
    result = encoder.utf8.encode_utf8(text)
except TypeError:
    # Handle invalid input type
    pass
```

## References
- [Unicode Standard](https://unicode.org/)
- [UTF-8 Encoding (RFC 3629)](https://tools.ietf.org/html/rfc3629)
- [Python unicodedata](https://docs.python.org/3/library/unicodedata.html)
