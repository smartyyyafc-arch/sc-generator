#!/usr/bin/env python3
"""
Comprehensive hex decoder test: encode → decode → execute verification
"""

import sys
sys.path.insert(0, '/home/user/sc-generator')

from vbs_encoder import VBSEncoder, ObfuscationConfig
import re


def test_hex_encoding_decoding():
    """Test hex encoding and decoding cycle"""
    print("=" * 70)
    print("TEST: HEX ENCODING/DECODING CYCLE")
    print("=" * 70)

    test_commands = [
        "notepad.exe",
        "cmd.exe /c whoami",
        "powershell.exe -Command \"Write-Host 'Test'\"",
        "C:\\Windows\\System32\\calc.exe",
    ]

    for cmd in test_commands:
        print(f"\n1. Original Command: {cmd}")

        # Step 1: Encode to hex
        hex_encoded = cmd.encode().hex()
        print(f"2. Hex Encoded: {hex_encoded}")
        print(f"   Length: {len(hex_encoded)} chars")

        # Step 2: Simulate VBS decoding
        decoded = ""
        for i in range(0, len(hex_encoded), 2):
            hex_pair = hex_encoded[i:i+2]
            char_code = int(hex_pair, 16)
            decoded += chr(char_code)

        print(f"3. Decoded back: {decoded}")

        # Step 3: Verify
        if decoded == cmd:
            print("   ✓ PASS: Encoding/Decoding cycle successful")
        else:
            print(f"   ✗ FAIL: Mismatch!")
            print(f"     Expected: {cmd}")
            print(f"     Got:      {decoded}")
            return False

    return True


def test_vbs_decoder_generation():
    """Test VBS decoder generation with variable consistency"""
    print("\n" + "=" * 70)
    print("TEST: VBS DECODER GENERATION & VARIABLE CONSISTENCY")
    print("=" * 70)

    config = ObfuscationConfig(use_hex_encoding=True)
    encoder = VBSEncoder(config)

    test_cmd = "cmd.exe /c echo Decoded"
    print(f"\nTest Command: {test_cmd}")

    # Generate decoder with execution
    vbs_code = encoder.create_hex_decoder_vbs(test_cmd, execute=True)

    print("\nGenerated VBS Code:")
    print("-" * 70)
    print(vbs_code)
    print("-" * 70)

    # Extract hex variable
    hex_var_match = re.search(r'Dim (h_\w+)', vbs_code)
    if not hex_var_match:
        print("✗ FAIL: Hex variable not declared with Dim")
        return False
    hex_var = hex_var_match.group(1)
    print(f"\n1. Hex variable declared: {hex_var}")

    # Extract decoded variable
    decoded_var_match = re.search(r'Dim (decoded_\w+)', vbs_code)
    if not decoded_var_match:
        print("✗ FAIL: Decoded variable not declared with Dim")
        return False
    decoded_var = decoded_var_match.group(1)
    print(f"2. Decoded variable declared: {decoded_var}")

    # Extract shell variable
    shell_var_match = re.search(r'Set (shell_\w+)\s*=', vbs_code)
    if not shell_var_match:
        print("✗ FAIL: Shell variable not properly assigned")
        return False
    shell_var = shell_var_match.group(1)
    print(f"3. Shell variable assigned: {shell_var}")

    # Check variable usage consistency
    hex_uses = vbs_code.count(hex_var)
    decoded_uses = vbs_code.count(decoded_var)
    shell_uses = vbs_code.count(shell_var)

    print(f"\n4. Variable Usage Count:")
    print(f"   - {hex_var}: {hex_uses} times")
    print(f"   - {decoded_var}: {decoded_uses} times")
    print(f"   - {shell_var}: {shell_uses} times")

    # Verify critical usage points
    checks = [
        (f"{hex_var} = ", f"Hex variable assignment"),
        (f"= DecodeHex", f"Function assignment to decoded var"),
        (f".Run {decoded_var}", f"Execution with decoded command"),
        (f"Set {shell_var} =", f"Shell creation"),
        (f"{shell_var}.Run", f"Shell.Run invocation"),
        (f"Set {shell_var} = Nothing", f"Shell cleanup"),
    ]

    print(f"\n5. Critical Usage Verification:")
    all_checks_passed = True
    for check_str, description in checks:
        if check_str in vbs_code:
            print(f"   ✓ {description}")
        else:
            print(f"   ✗ MISSING: {description}")
            all_checks_passed = False

    if all_checks_passed:
        print("\n✓ PASS: All variable consistency checks passed")
        return True
    else:
        print("\n✗ FAIL: Some variable checks failed")
        return False


def test_variable_name_patterns():
    """Test that variable naming follows consistent patterns"""
    print("\n" + "=" * 70)
    print("TEST: VARIABLE NAMING PATTERNS")
    print("=" * 70)

    config = ObfuscationConfig(use_hex_encoding=True)
    encoder = VBSEncoder(config)

    print("\nGenerating 5 variants to check naming consistency:\n")

    for variant in range(1, 6):
        vbs_code = encoder.create_hex_decoder_vbs(f"test_{variant}.exe", execute=True)

        # Extract variables
        hex_vars = re.findall(r'\b(h_\w+)\b', vbs_code)
        decoded_vars = re.findall(r'\b(decoded_\w+)\b', vbs_code)
        shell_vars = re.findall(r'\b(shell_\w+)\b', vbs_code)

        print(f"Variant {variant}:")
        print(f"  Hex var:     {hex_vars[0] if hex_vars else 'NOT FOUND'}")
        print(f"  Decoded var: {decoded_vars[0] if decoded_vars else 'NOT FOUND'}")
        print(f"  Shell var:   {shell_vars[0] if shell_vars else 'NOT FOUND'}")

        # Verify all are present
        if not (hex_vars and decoded_vars and shell_vars):
            print("  ✗ FAIL: Missing variable type")
            return False

    print("\n✓ PASS: All variants have correct variable naming patterns")
    return True


def test_function_naming():
    """Test DecodeHex function naming and usage"""
    print("\n" + "=" * 70)
    print("TEST: DECODEHEX FUNCTION NAMING AND USAGE")
    print("=" * 70)

    config = ObfuscationConfig(use_hex_encoding=True)
    encoder = VBSEncoder(config)

    vbs_code = encoder.create_hex_decoder_vbs("test.exe", execute=False)

    # Extract function name
    func_match = re.search(r'Function (DecodeHex\w+)\(h\)', vbs_code)
    if not func_match:
        print("✗ FAIL: DecodeHex function not found")
        return False

    func_name = func_match.group(1)
    print(f"\n1. Function declared: {func_name}")

    # Count function usage
    func_usage_count = vbs_code.count(func_name)
    print(f"2. Function used {func_usage_count} times")

    # Verify function structure
    checks = [
        ("Function DecodeHex", "Function declaration"),
        ("Dim i, r", "Local variables (i, r)"),
        ("For i = 1 To Len(h) Step 2", "Loop structure"),
        ("Chr(CLng(\"&H\"", "Hex conversion"),
        ("Mid(h, i, 2)", "Character extraction"),
        ("End Function", "Function termination"),
        (f"{func_name} =", "Return value assignment"),
    ]

    print(f"\n3. Function Structure Verification:")
    all_checks_passed = True
    for check_str, description in checks:
        if check_str in vbs_code:
            print(f"   ✓ {description}")
        else:
            print(f"   ✗ MISSING: {description}")
            all_checks_passed = False

    if all_checks_passed:
        print("\n✓ PASS: Function structure is correct")
        return True
    else:
        print("\n✗ FAIL: Function structure has issues")
        return False


def test_execution_flow():
    """Test the complete execution flow"""
    print("\n" + "=" * 70)
    print("TEST: COMPLETE EXECUTION FLOW")
    print("=" * 70)

    config = ObfuscationConfig(use_hex_encoding=True)
    encoder = VBSEncoder(config)

    test_cmd = "notepad.exe"
    vbs_code = encoder.create_hex_decoder_vbs(test_cmd, execute=True)

    print(f"\nTest Command: {test_cmd}")
    print(f"Hex Encoding: {test_cmd.encode().hex()}")

    # Expected execution flow
    print("\nExpected Execution Flow:")
    print("1. Define DecodeHex function")
    print("2. Declare hex variable (h_*)")
    print("3. Store hex-encoded command in hex variable")
    print("4. Declare decoded variable (decoded_*)")
    print("5. Call DecodeHex function → store result in decoded variable")
    print("6. Declare shell variable (shell_*)")
    print("7. Create WScript.Shell object → store in shell variable")
    print("8. Call shell.Run with decoded command")
    print("9. Set shell variable to Nothing (cleanup)")

    print("\nActual Code Sections:")
    lines = vbs_code.split('\n')

    # Extract hex variable assignment
    hex_assign = [l for l in lines if ' = "' in l and 'h_' in l]
    if hex_assign:
        print(f"\n✓ Hex assignment found: {hex_assign[0].strip()}")

    # Extract decoded variable assignment
    decoded_assign = [l for l in lines if 'DecodeHex' in l and 'decoded_' in l]
    if decoded_assign:
        print(f"✓ Decoded assignment found: {decoded_assign[0].strip()}")

    # Extract shell creation
    shell_create = [l for l in lines if 'CreateObject' in l and 'WScript.Shell' in l]
    if shell_create:
        print(f"✓ Shell creation found: {shell_create[0].strip()}")

    # Extract execution
    shell_run = [l for l in lines if '.Run' in l]
    if shell_run:
        print(f"✓ Shell.Run found: {shell_run[0].strip()}")

    # Extract cleanup
    cleanup = [l for l in lines if 'Nothing' in l]
    if cleanup:
        print(f"✓ Cleanup found: {cleanup[0].strip()}")

    if all([hex_assign, decoded_assign, shell_create, shell_run, cleanup]):
        print("\n✓ PASS: Complete execution flow is present")
        return True
    else:
        print("\n✗ FAIL: Missing execution flow components")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("HEX DECODER COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    tests = [
        ("Hex Encoding/Decoding Cycle", test_hex_encoding_decoding),
        ("VBS Decoder Generation & Consistency", test_vbs_decoder_generation),
        ("Variable Naming Patterns", test_variable_name_patterns),
        ("Function Naming & Structure", test_function_naming),
        ("Execution Flow", test_execution_flow),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
