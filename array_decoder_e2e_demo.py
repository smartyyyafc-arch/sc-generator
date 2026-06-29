#!/usr/bin/env python3
"""
Array Decoder End-to-End Demonstration
Shows the complete pipeline: payload split → encode → decode → execute
"""

import binascii
import re
from vbs_encoder import VBSEncoder


def demonstrate_payload_split():
    """Demonstrate Step 1: Splitting payload into chunks"""
    print("\n" + "="*70)
    print("STEP 1: PAYLOAD SPLITTING")
    print("="*70)

    payload = "powershell.exe -NoProfile -Command Write-Host 'Success'"
    chunk_size = 16

    print(f"Original Payload: {payload}")
    print(f"Payload Length: {len(payload)} bytes")
    print(f"Chunk Size: {chunk_size} bytes")

    chunks = [payload[i:i + chunk_size] for i in range(0, len(payload), chunk_size)]

    print(f"\nNumber of Chunks: {len(chunks)}")
    print("\nChunk Breakdown:")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}: [{len(chunk):2d} bytes] {repr(chunk)}")

    return chunks


def demonstrate_hex_encoding(chunks):
    """Demonstrate Step 2: Hex encoding of each chunk"""
    print("\n" + "="*70)
    print("STEP 2: HEX ENCODING")
    print("="*70)

    encoded_chunks = []
    print("Hex Encoding Each Chunk:")
    for i, chunk in enumerate(chunks):
        hex_encoded = binascii.hexlify(chunk.encode()).decode()
        encoded_chunks.append(hex_encoded)
        print(f"  Chunk {i}: {chunk!r:40s} → {hex_encoded}")

    return encoded_chunks


def demonstrate_hex_to_chr(hex_chunk):
    """Demonstrate Step 3: Hex to Character conversion (VBS simulation)"""
    print("\n" + "="*70)
    print("STEP 3: HEX-TO-CHARACTER CONVERSION (VBS Simulation)")
    print("="*70)

    print(f"Input Hex: {hex_chunk}")
    print(f"VBS Logic: For i = 1 To Len(h) Step 2: r = r & Chr(CLng(\"&H\" & Mid(h, i, 2)))")

    result = ""
    conversions = []
    for i in range(0, len(hex_chunk), 2):
        hex_pair = hex_chunk[i:i+2]
        char_code = int(hex_pair, 16)
        char = chr(char_code)
        result += char
        conversions.append(f"&H{hex_pair} ({int(hex_pair, 16):3d}) → '{char}'")

    print("\nHex Pair Conversions:")
    for i, conv in enumerate(conversions[:5]):
        print(f"  {conv}")
    if len(conversions) > 5:
        print(f"  ... ({len(conversions) - 5} more)")

    print(f"\nDecoded Result: {result!r}")
    return result


def demonstrate_full_pipeline(chunks, encoded_chunks):
    """Demonstrate Step 4: Full decode pipeline"""
    print("\n" + "="*70)
    print("STEP 4: FULL DECODE PIPELINE (All Chunks)")
    print("="*70)

    reconstructed = ""
    print("Processing all chunks:")
    for chunk_idx, hex_chunk in enumerate(encoded_chunks):
        chunk_result = ""
        for i in range(0, len(hex_chunk), 2):
            hex_pair = hex_chunk[i:i+2]
            char_code = int(hex_pair, 16)
            chunk_result += chr(char_code)
        reconstructed += chunk_result
        print(f"  Chunk {chunk_idx}: Decoded {len(hex_chunk)//2} chars → {chunk_result!r}")

    print(f"\nFull Reconstructed: {reconstructed!r}")
    print(f"Original Payload:   {chunks[0][0:len(chunks[0])]!r}...")

    # Verify integrity
    original_payload = "".join(chunks)
    match = reconstructed == original_payload
    print(f"\n✓ Integrity Check: {'PASS' if match else 'FAIL'}")

    return reconstructed


def demonstrate_vbs_code_generation():
    """Demonstrate Step 5: VBS Code Generation"""
    print("\n" + "="*70)
    print("STEP 5: VBS CODE GENERATION")
    print("="*70)

    encoder = VBSEncoder()
    payload = "cmd /c echo Success"

    vbs_code = encoder.create_array_concatenation_decoder(payload)

    print("Generated VBS Code:")
    print("-" * 70)
    print(vbs_code)
    print("-" * 70)

    # Parse and analyze
    print("\nCode Structure Analysis:")
    lines = vbs_code.split('\n')

    # Find array declaration
    dim_match = re.search(r'Dim\s+(\w+)\((\d+)\)', vbs_code)
    if dim_match:
        print(f"  Array Name: {dim_match.group(1)}")
        print(f"  Array Size: {dim_match.group(2)} (0-indexed)")

    # Count chunks
    assignments = len([l for l in lines if '(' in l and '=' in l and 'Dim' not in l])
    print(f"  Array Assignments: {assignments} chunks")

    # Find loop variable
    for_each = re.search(r'For Each\s+(\w+)\s+In', vbs_code)
    if for_each:
        print(f"  Loop Variable: {for_each.group(1)}")

    # Find execution
    if "WScript.Shell" in vbs_code:
        print(f"  Execution Method: WScript.Shell.Run")

    return vbs_code


def demonstrate_array_structure_details():
    """Show detailed array structure"""
    print("\n" + "="*70)
    print("ARRAY STRUCTURE DETAILS")
    print("="*70)

    encoder = VBSEncoder()
    payload = "test command"

    vbs_code = encoder.create_array_concatenation_decoder(payload)
    lines = vbs_code.split('\n')

    print("VBS Code Line-by-Line Breakdown:")
    print()

    for i, line in enumerate(lines, 1):
        if line.strip():
            # Categorize line
            if 'Dim' in line:
                category = "[DECLARATION]"
            elif 'For' in line or 'Next' in line:
                category = "[LOOP]"
            elif 'Set' in line or 'CreateObject' in line:
                category = "[OBJECT]"
            elif '.Run' in line:
                category = "[EXECUTION]"
            elif '=' in line and '(' in line:
                category = "[ASSIGNMENT]"
            else:
                category = "[OTHER]"

            print(f"{i:2d}. {category:15s} {line.strip()}")


def main():
    """Run complete demonstration"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "ARRAY DECODER END-TO-END DEMONSTRATION".center(68) + "║")
    print("║" + "(Payload Split → Encode → Decode → Execute)".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    # Step 1: Split payload
    chunks = demonstrate_payload_split()

    # Step 2: Hex encoding
    encoded_chunks = demonstrate_hex_encoding(chunks)

    # Step 3: Hex-to-Char conversion (first chunk example)
    if encoded_chunks:
        demonstrate_hex_to_chr(encoded_chunks[0])

    # Step 4: Full pipeline reconstruction
    reconstructed = demonstrate_full_pipeline(chunks, encoded_chunks)

    # Step 5: VBS code generation
    vbs_code = demonstrate_vbs_code_generation()

    # Step 6: Array structure details
    demonstrate_array_structure_details()

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Original Payload: {len(''.join(chunks))} bytes")
    print(f"Split into: {len(chunks)} chunks (16 bytes each)")
    print(f"Hex Encoded: {sum(len(c) for c in encoded_chunks)//2} bytes → {sum(len(c) for c in encoded_chunks)} hex chars")
    print(f"VBS Code Generated: {len(vbs_code)} bytes")
    print(f"Obfuscation Level: High (hex encoding + array concatenation + random names)")
    print(f"Execution Method: WScript.Shell.Run (hidden window)")
    print()
    print("✓ All steps completed successfully!")
    print("="*70)


if __name__ == "__main__":
    main()
