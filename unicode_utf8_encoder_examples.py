#!/usr/bin/env python3
"""
Unicode/UTF-8 Encoder - Practical Examples and Demonstrations
Shows real-world usage patterns and integration scenarios.
"""

from unicode_utf8_encoder import (
    UnicodeUTF8Encoder,
    UTF8Encoder,
    UnicodeNormalizer,
    PercentEncoder,
    UnicodeAnalyzer,
    SafeCommandBuilder,
    EmojiHandler,
    PunycodeHandler,
)
import json


def example_1_basic_encoding():
    """Example 1: Basic UTF-8 encoding and decoding"""
    print("=" * 70)
    print("EXAMPLE 1: Basic UTF-8 Encoding/Decoding")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()

    texts = [
        "Hello World",
        "Привет мир",
        "你好世界",
        "مرحبا بالعالم",
        "🌍🌎🌏",
    ]

    for text in texts:
        utf8_bytes = encoder.utf8.encode_utf8(text)
        decoded = encoder.utf8.decode_utf8(utf8_bytes)

        print(f"\nOriginal:      {text}")
        print(f"UTF-8 bytes:   {utf8_bytes.hex()}")
        print(f"Byte count:    {len(utf8_bytes)}")
        print(f"Char count:    {len(text)}")
        print(f"Decoded:       {decoded}")


def example_2_percent_encoding():
    """Example 2: Percent encoding for URLs and safe transmission"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Percent Encoding (URL-Safe Transmission)")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()

    # Real-world scenario: passing parameters safely
    test_cases = [
        ("user@example.com", None),
        ("search term with spaces", None),
        ("special&chars<>|", None),
        ("café français", None),
        ("北京天气", None),
        ("hello world", ""),  # with empty safe chars
    ]

    for text, safe in test_cases:
        if safe is None:
            encoded = encoder.percent_encoder.percent_encode(text)
        else:
            encoded = encoder.percent_encoder.percent_encode(text, safe_chars=safe)
        decoded = encoder.percent_encoder.percent_decode(encoded)

        print(f"\nOriginal:  {text}")
        print(f"Encoded:   {encoded}")
        print(f"Decoded:   {decoded}")
        print(f"Valid:     {decoded == text}")


def example_3_unicode_normalization():
    """Example 3: Unicode normalization for consistent data handling"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Unicode Normalization")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()

    # Text that can be represented in multiple ways
    test_cases = [
        ("café", "Composed vs Decomposed"),
        ("ﬁle", "Ligature vs Separate"),
        ("㍻", "Compatibility Character"),
        ("Å", "Angstrom Sign vs A with ring"),
    ]

    for text, description in test_cases:
        nfc = encoder.normalizer.normalize_nfc(text)
        nfd = encoder.normalizer.normalize_nfd(text)
        nfkc = encoder.normalizer.normalize_nfkc(text)
        nfkd = encoder.normalizer.normalize_nfkd(text)

        print(f"\n{description}: {text}")
        print(f"  NFC:  {nfc!r} (len={len(nfc)})")
        print(f"  NFD:  {nfd!r} (len={len(nfd)})")
        print(f"  NFKC: {nfkc!r} (len={len(nfkc)})")
        print(f"  NFKD: {nfkd!r} (len={len(nfkd)})")


def example_4_text_analysis():
    """Example 4: Comprehensive text analysis"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Text Analysis & Encoding Information")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()

    test_texts = [
        "Hello World",
        "Hello 世界",
        "Привет 🌍",
        "مرحبا بالعالم",
    ]

    for text in test_texts:
        info = encoder.get_encoding_info(text)

        print(f"\nText: {text}")
        print(f"  Character count: {info['char_count']}")
        print(f"  UTF-8 byte count: {info['utf8_length']}")
        print(f"  Scripts: {', '.join(info['scripts'])}")
        print(f"  Has emoji: {info['has_emoji']}")
        print(f"  Is bidirectional: {info['is_bidi']}")
        print(f"  Percent encoded: {info['percent_encoded'][:50]}...")


def example_5_safe_commands():
    """Example 5: Building safe shell commands"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Safe Command Building")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()
    builder = encoder.command_builder

    # Arguments that need escaping
    arguments = [
        "simple",
        "with spaces",
        "special'quotes'here",
        "shell&redirect<>|",
        "café française",
        "path/to/file",
    ]

    shells = ["bash", "cmd", "powershell"]

    for arg in arguments:
        print(f"\nArgument: {arg}")
        for shell in shells:
            escaped = builder.escape_for_shell(arg, shell)
            print(f"  {shell:12} {escaped}")


def example_6_emoji_handling():
    """Example 6: Working with emoji"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Emoji Handling")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()
    handler = encoder.emoji_handler

    test_cases = [
        "Task completed ✓",
        "Success! 🎉🎊",
        "Hello 👋 World 🌍",
        "No emoji here",
        "😀😃😄😁😆😅",
    ]

    for text in test_cases:
        emojis = handler.extract_emoji(text)
        count = handler.count_emoji(text)
        without_emoji = handler.remove_emoji(text)
        has_emoji = handler.has_emoji(text)

        print(f"\nText: {text}")
        print(f"  Has emoji: {has_emoji}")
        print(f"  Emoji count: {count}")
        if emojis:
            print(f"  Emoji: {', '.join(emojis)}")
        print(f"  Without emoji: {without_emoji!r}")


def example_7_punycode():
    """Example 7: Internationalized domain names (Punycode)"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Punycode for International Domain Names")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()
    punycode = encoder.punycode

    # Real international domains
    domains = [
        "münchen.de",
        "москва.рф",
        "中国.cn",
        "مصر.eg",
        "ελλάδα.gr",
    ]

    for domain in domains:
        encoded = punycode.encode_punycode(domain)
        decoded = punycode.decode_punycode(encoded)

        print(f"\nInternational: {domain}")
        print(f"Punycode:      {encoded}")
        print(f"Decoded:       {decoded}")


def example_8_character_metadata():
    """Example 8: Unicode character metadata"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Character Metadata & Unicode Properties")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()
    analyzer = encoder.analyzer

    # Diverse character set
    chars = [
        'A',      # ASCII
        'é',      # Accented
        '5',      # Digit
        '中',     # CJK
        'א',      # Hebrew
        'ь',      # Cyrillic
        '€',      # Symbol
        '👋',     # Emoji
    ]

    for char in chars:
        category = analyzer.get_category(char)
        name = analyzer.get_name(char)
        codepoint = encoder.utf8.get_codepoint(char)
        bytes_seq = encoder.utf8.get_byte_sequence(char)
        width = analyzer.get_width(char)

        print(f"\nCharacter: {char}")
        print(f"  Codepoint: U+{codepoint:04X} ({codepoint})")
        print(f"  Category: {category}")
        print(f"  Name: {name}")
        print(f"  UTF-8 bytes: {' '.join(f'{b:02X}' for b in bytes_seq)}")
        print(f"  Display width: {width}")


def example_9_script_detection():
    """Example 9: Script and language detection"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Script Detection")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()
    analyzer = encoder.analyzer

    # Mixed-script texts
    texts = [
        "Hello",
        "Hello 世界",
        "Привет мир",
        "مرحبا بالعالم",
        "שלום עולם",
        "你好 مرحبا こんにちは",
        "Hello Привет 中文 اللغة العربية 日本語",
    ]

    for text in texts:
        scripts = analyzer.detect_scripts(text)
        is_bidi = analyzer.is_bidi_text(text)

        print(f"\nText: {text}")
        print(f"  Scripts: {', '.join(sorted(scripts))}")
        print(f"  Bidirectional: {is_bidi}")


def example_10_practical_integration():
    """Example 10: Practical integration scenario"""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: Practical Integration - Log Processing")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()

    # Simulate log entries with international content
    log_entries = [
        {"timestamp": "2024-06-29 10:00:00", "level": "INFO", "msg": "Application started"},
        {"timestamp": "2024-06-29 10:01:00", "level": "SUCCESS", "msg": "Task completed ✓"},
        {"timestamp": "2024-06-29 10:02:00", "level": "INFO", "msg": "Processing: café français"},
        {"timestamp": "2024-06-29 10:03:00", "level": "WARNING", "msg": "Data: 你好世界"},
        {"timestamp": "2024-06-29 10:04:00", "level": "ERROR", "msg": "Error in مرحبا"},
    ]

    print("\nLog Processing:")
    for entry in log_entries:
        msg = entry["msg"]
        info = encoder.get_encoding_info(msg)

        print(f"\n[{entry['timestamp']}] {entry['level']}")
        print(f"  Message: {msg}")
        print(f"  Characters: {info['char_count']}")
        print(f"  Bytes: {info['utf8_length']}")
        print(f"  Scripts: {', '.join(info['scripts']) if info['scripts'] else 'ASCII'}")
        print(f"  Emoji: {info['emoji_count']}")

        # Safe percent encoding for storage/transmission
        safe_msg = encoder.percent_encoder.percent_encode(msg)
        print(f"  Safe encoding: {safe_msg[:60]}...")


def example_11_database_consistency():
    """Example 11: Database input normalization"""
    print("\n" + "=" * 70)
    print("EXAMPLE 11: Database Input Normalization")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()

    # User inputs that might have different representations
    user_inputs = [
        "Café",
        "CAFÉ",
        "Cäfe",  # Different decomposition
        "Dünemark",
        "Zürich",
    ]

    print("Database Insert Normalization:")
    print("User Input → Normalized (NFC) → Safe for DB\n")

    for user_input in user_inputs:
        normalized = encoder.normalizer.normalize_nfc(user_input)
        safe = encoder.percent_encoder.percent_encode(normalized)

        print(f"Input:      {user_input!r}")
        print(f"Normalized: {normalized!r}")
        print(f"Safe:       {safe!r}")
        print()


def example_12_file_operations():
    """Example 12: International filename handling"""
    print("\n" + "=" * 70)
    print("EXAMPLE 12: International Filename Handling")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()

    # International filenames
    filenames = [
        "报告_2024.txt",
        "café_menu.pdf",
        "résumé_français.docx",
        "тест_документ.doc",
        "اختبار_ملف.xlsx",
    ]

    print("Filename Processing for Cross-Platform Storage:\n")

    for filename in filenames:
        # Normalize for consistency
        normalized = encoder.normalizer.normalize_nfkc(filename)
        # Encode for safe storage in ASCII-only systems
        encoded = encoder.percent_encoder.percent_encode(normalized)
        # For URL compatibility
        url_safe = encoder.percent_encoder.url_encode(normalized)

        print(f"Original:  {filename}")
        print(f"Normalized: {normalized}")
        print(f"Percent:   {encoded}")
        print(f"URL-safe:  {url_safe}")
        print()


def example_13_command_injection_safety():
    """Example 13: Protection against command injection"""
    print("\n" + "=" * 70)
    print("EXAMPLE 13: Command Injection Prevention")
    print("=" * 70)

    encoder = UnicodeUTF8Encoder()
    builder = encoder.command_builder

    # Potentially malicious inputs
    suspicious_inputs = [
        "hello",
        "hello; rm -rf /",
        "hello && evil_command",
        "hello | grep secret",
        "hello 'world' && cat /etc/passwd",
    ]

    print("Command Safety Verification:\n")

    for malicious in suspicious_inputs:
        safe_bash = builder.escape_for_shell(malicious, 'bash')
        safe_cmd = builder.escape_for_shell(malicious, 'cmd')

        print(f"Input:      {malicious!r}")
        print(f"Bash safe:  {safe_bash}")
        print(f"CMD safe:   {safe_cmd}")
        print()


def example_14_bom_handling():
    """Example 14: BOM detection and handling"""
    print("\n" + "=" * 70)
    print("EXAMPLE 14: BOM (Byte Order Mark) Handling")
    print("=" * 70)

    utf8_encoder = UTF8Encoder()

    # Create data with different BOMs
    text = "Hello BOM"

    utf8_with_bom = utf8_encoder.add_utf8_bom(text)
    utf16_be = b'\xfe\xff' + "Hello".encode('utf-16-be')
    utf16_le = b'\xff\xfe' + "Hello".encode('utf-16-le')

    test_data = [
        (utf8_with_bom, "UTF-8 with BOM"),
        (utf16_be, "UTF-16 Big-Endian"),
        (utf16_le, "UTF-16 Little-Endian"),
        (text.encode('utf-8'), "UTF-8 no BOM"),
    ]

    print("BOM Detection:\n")

    for data, description in test_data:
        bom_type = utf8_encoder.detect_bom(data)
        clean = utf8_encoder.remove_bom(data)

        print(f"Data: {description}")
        print(f"  Bytes: {data[:10].hex()}...")
        print(f"  BOM type: {bom_type}")
        print(f"  After removal: {clean[:10].hex()}...")
        print()


def main():
    """Run all examples"""
    print("\n" * 2)
    print("╔" + "═" * 68 + "╗")
    print("║" + " UNICODE/UTF-8 ENCODER - COMPREHENSIVE EXAMPLES ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")

    examples = [
        example_1_basic_encoding,
        example_2_percent_encoding,
        example_3_unicode_normalization,
        example_4_text_analysis,
        example_5_safe_commands,
        example_6_emoji_handling,
        example_7_punycode,
        example_8_character_metadata,
        example_9_script_detection,
        example_10_practical_integration,
        example_11_database_consistency,
        example_12_file_operations,
        example_13_command_injection_safety,
        example_14_bom_handling,
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {example_func.__name__}: {e}")
        print("\n")

    print("\n" * 1)
    print("╔" + "═" * 68 + "╗")
    print("║" + " All examples completed successfully ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")


if __name__ == '__main__':
    main()
