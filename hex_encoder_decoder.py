"""
Hex Encoder and Decoder with support for non-ASCII characters.
Handles UTF-8 encoded strings properly.
"""

def hex_encoder(data: str) -> str:
    """
    Encodes a string (including non-ASCII characters) to hexadecimal representation.

    Args:
        data (str): Input string, can contain non-ASCII characters (Unicode)

    Returns:
        str: Hexadecimal encoded string (lowercase hex digits)

    Example:
        >>> hex_encoder("Hello")
        '48656c6c6f'
        >>> hex_encoder("Hello, 世界")
        '48656c6c6f2c20e4b896e7958c'
    """
    # Encode string to UTF-8 bytes, then convert each byte to hex
    return data.encode('utf-8').hex()


def hex_decoder(hex_string: str) -> str:
    """
    Decodes a hexadecimal string back to its original string form.
    Handles non-ASCII characters that were UTF-8 encoded.

    Args:
        hex_string (str): Hexadecimal encoded string

    Returns:
        str: Decoded original string with non-ASCII characters preserved

    Raises:
        ValueError: If the input is not a valid hex string or has odd length

    Example:
        >>> hex_decoder('48656c6c6f')
        'Hello'
        >>> hex_decoder('48656c6c6f2c20e4b896e7958c')
        'Hello, 世界'
    """
    try:
        # Convert hex string to bytes, then decode from UTF-8
        return bytes.fromhex(hex_string).decode('utf-8')
    except ValueError as e:
        raise ValueError(f"Invalid hex string: {e}")


# Test cases
if __name__ == "__main__":
    # Test 1: ASCII only
    test1 = "Hello"
    encoded1 = hex_encoder(test1)
    decoded1 = hex_decoder(encoded1)
    print(f"Test 1 (ASCII):")
    print(f"  Original: {test1}")
    print(f"  Encoded:  {encoded1}")
    print(f"  Decoded:  {decoded1}")
    print(f"  Match: {test1 == decoded1}\n")

    # Test 2: Mixed ASCII and Unicode
    test2 = "Hello, 世界"
    encoded2 = hex_encoder(test2)
    decoded2 = hex_decoder(encoded2)
    print(f"Test 2 (Mixed ASCII + Chinese):")
    print(f"  Original: {test2}")
    print(f"  Encoded:  {encoded2}")
    print(f"  Decoded:  {decoded2}")
    print(f"  Match: {test2 == decoded2}\n")

    # Test 3: Emoji
    test3 = "Hello 😀 World"
    encoded3 = hex_encoder(test3)
    decoded3 = hex_decoder(encoded3)
    print(f"Test 3 (ASCII + Emoji):")
    print(f"  Original: {test3}")
    print(f"  Encoded:  {encoded3}")
    print(f"  Decoded:  {decoded3}")
    print(f"  Match: {test3 == decoded3}\n")

    # Test 4: Multiple scripts
    test4 = "Привет мир 🌍 한글"
    encoded4 = hex_encoder(test4)
    decoded4 = hex_decoder(encoded4)
    print(f"Test 4 (Russian + Emoji + Korean):")
    print(f"  Original: {test4}")
    print(f"  Encoded:  {encoded4}")
    print(f"  Decoded:  {decoded4}")
    print(f"  Match: {test4 == decoded4}\n")

    # Test 5: Special characters
    test5 = "Café\t\n©"
    encoded5 = hex_encoder(test5)
    decoded5 = hex_decoder(encoded5)
    print(f"Test 5 (Special chars):")
    print(f"  Original: {repr(test5)}")
    print(f"  Encoded:  {encoded5}")
    print(f"  Decoded:  {repr(decoded5)}")
    print(f"  Match: {test5 == decoded5}")
