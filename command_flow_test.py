#!/usr/bin/env python3
"""
Command flow test: Verify encode → decode → execute flow with detailed tracing
"""

import sys
sys.path.insert(0, '/home/user/sc-generator')

from vbs_encoder import VBSEncoder, ObfuscationConfig
import re


def trace_command_flow():
    """Trace the complete command flow from encode to execute"""
    print("=" * 80)
    print("COMMAND FLOW TEST: encode → decode → execute")
    print("=" * 80)

    # Test command
    test_command = "cmd.exe /c whoami"
    print(f"\nStep 1: Original Command")
    print(f"  Command: {test_command}")
    print(f"  Length: {len(test_command)} characters")

    # Hex encoding
    hex_encoded = test_command.encode().hex()
    print(f"\nStep 2: Hex Encoding")
    print(f"  Hex: {hex_encoded}")
    print(f"  Length: {len(hex_encoded)} characters (hex pairs)")

    # Show hex breakdown
    print(f"\nStep 2a: Hex Breakdown")
    hex_pairs = [hex_encoded[i:i+2] for i in range(0, len(hex_encoded), 2)]
    print(f"  Hex pairs: {' '.join(hex_pairs[:8])}... ({len(hex_pairs)} pairs total)")

    for i, pair in enumerate(hex_pairs[:5]):
        char_code = int(pair, 16)
        char = chr(char_code)
        print(f"    {pair} → {char_code:3d} → '{char}'")
    if len(hex_pairs) > 5:
        print(f"    ... ({len(hex_pairs) - 5} more pairs)")

    # Generate VBS code
    print(f"\nStep 3: VBS Code Generation")
    config = ObfuscationConfig(use_hex_encoding=True)
    encoder = VBSEncoder(config)
    vbs_code = encoder.create_hex_decoder_vbs(test_command, execute=True)

    # Parse variable names
    hex_var_match = re.search(r'Dim (h_\w+)', vbs_code)
    decoded_var_match = re.search(r'Dim (decoded_\w+)', vbs_code)
    shell_var_match = re.search(r'Set (shell_\w+)', vbs_code)
    func_match = re.search(r'Function (DecodeHex\w+)', vbs_code)

    hex_var = hex_var_match.group(1) if hex_var_match else "UNKNOWN"
    decoded_var = decoded_var_match.group(1) if decoded_var_match else "UNKNOWN"
    shell_var = shell_var_match.group(1) if shell_var_match else "UNKNOWN"
    func_name = func_match.group(1) if func_match else "UNKNOWN"

    print(f"  Variable names:")
    print(f"    Hex variable:     {hex_var}")
    print(f"    Decoded variable: {decoded_var}")
    print(f"    Shell variable:   {shell_var}")
    print(f"    Function name:    {func_name}")

    # Show VBS code structure
    print(f"\nStep 4: Generated VBS Code Structure")
    print("-" * 80)
    print(vbs_code)
    print("-" * 80)

    # Trace execution steps
    print(f"\nStep 5: Execution Trace (simulated)")
    print(f"\n5.1 Function Definition Phase")
    print(f"    Define function: {func_name}(h)")
    print(f"    - Parameters: h (hex string)")
    print(f"    - Local vars: i (loop counter), r (result)")
    print(f"    - Logic: Loop through hex string pairs, decode each to character")

    print(f"\n5.2 Hex Variable Setup Phase")
    print(f"    Declare: {hex_var}")
    print(f"    Assign: {hex_var} = \"{hex_encoded}\"")
    print(f"    Value: {len(hex_encoded)} character hex string")

    print(f"\n5.3 Decoding Phase")
    print(f"    Declare: {decoded_var}")
    print(f"    Call: {decoded_var} = {func_name}({hex_var})")
    print(f"    Function executes:")
    print(f"      - Loop i from 1 to {len(hex_encoded)} by step 2")
    print(f"      - Extract Mid({hex_var}, i, 2) → hex pair")
    print(f"      - Convert to character: Chr(CLng(\"&H\" & pair))")
    print(f"      - Build result: r = r & character")
    print(f"    Result: {decoded_var} = \"{test_command}\"")

    print(f"\n5.4 Shell Creation Phase")
    print(f"    Declare: {shell_var}")
    print(f"    Create: Set {shell_var} = CreateObject(\"WScript.Shell\")")
    print(f"    Status: WScript.Shell object ready for execution")

    print(f"\n5.5 Execution Phase")
    print(f"    Execute: {shell_var}.Run {decoded_var}, 0, False")
    print(f"    - Command: {test_command}")
    print(f"    - Window: 0 (hidden)")
    print(f"    - WaitOnReturn: False (non-blocking)")
    print(f"    Result: Command executed")

    print(f"\n5.6 Cleanup Phase")
    print(f"    Release: Set {shell_var} = Nothing")
    print(f"    Status: Shell object cleaned up, resources freed")

    # Verify consistency
    print(f"\nStep 6: Variable Consistency Verification")
    print(f"\n  Variable Usage Summary:")

    hex_uses = vbs_code.count(hex_var)
    decoded_uses = vbs_code.count(decoded_var)
    shell_uses = vbs_code.count(shell_var)
    func_uses = vbs_code.count(f"{func_name}(")

    print(f"    {hex_var}:")
    print(f"      - Declared: 1 time (Dim {hex_var})")
    print(f"      - Assigned: 1 time ({hex_var} = \"...\")")
    print(f"      - Used: 1 time in function call")
    print(f"      - Total occurrences: {hex_uses} ✓")

    print(f"    {decoded_var}:")
    print(f"      - Declared: 1 time (Dim {decoded_var})")
    print(f"      - Assigned: 1 time ({decoded_var} = {func_name}(...))")
    print(f"      - Used: 1 time in .Run call")
    print(f"      - Total occurrences: {decoded_uses} ✓")

    print(f"    {shell_var}:")
    print(f"      - Declared: 1 time (Dim {shell_var})")
    print(f"      - Assigned: 1 time (Set {shell_var} = CreateObject(...))")
    print(f"      - Used: 1 time for .Run method")
    print(f"      - Cleaned: 1 time (Set ... = Nothing)")
    print(f"      - Total occurrences: {shell_uses} ✓")

    print(f"    {func_name}:")
    print(f"      - Defined: 1 time (Function declaration)")
    print(f"      - Called: {func_uses} time(s)")

    # Verify key elements
    print(f"\nStep 7: Critical Element Verification")
    checks = {
        "Function definition": f"Function {func_name}(h)",
        "Loop structure": "For i = 1 To Len(h) Step 2",
        "Hex conversion": 'Chr(CLng("&H" & Mid(h, i, 2)))',
        "Hex assignment": f'{hex_var} = "{hex_encoded}"',
        "Decode call": f"{decoded_var} = {func_name}({hex_var})",
        "Shell creation": 'CreateObject("WScript.Shell")',
        "Shell.Run call": f".Run {decoded_var}",
        "Shell cleanup": "= Nothing",
    }

    all_pass = True
    for check_name, check_pattern in checks.items():
        if check_pattern in vbs_code:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name} - MISSING!")
            all_pass = False

    # Final status
    print(f"\nStep 8: Test Result")
    if all_pass and hex_uses >= 2 and decoded_uses >= 2 and shell_uses >= 3:
        print(f"  Status: ✓ PASS - All checks passed")
        print(f"\n  Summary:")
        print(f"    - Command properly encoded to hex")
        print(f"    - VBS decoder generated with unique variable names")
        print(f"    - Hex variable properly declared and used")
        print(f"    - Decoded variable properly declared and used")
        print(f"    - Shell variable properly declared, used, and cleaned")
        print(f"    - Execution flow complete and consistent")
        return True
    else:
        print(f"  Status: ✗ FAIL - Some checks failed")
        return False


def test_multiple_commands():
    """Test with various command types"""
    print("\n\n" + "=" * 80)
    print("MULTI-COMMAND TEST: Various command types")
    print("=" * 80)

    commands = [
        ("Simple executable", "notepad.exe"),
        ("With parameters", "cmd.exe /c dir C:\\"),
        ("PowerShell", "powershell.exe -NoProfile -Command \"[System.Environment]::OSVersion\""),
        ("With quotes", 'cmd.exe /c echo "test"'),
        ("Network command", "net.exe user"),
    ]

    results = []
    for desc, cmd in commands:
        print(f"\nCommand: {desc}")
        print(f"  {cmd}")

        hex_enc = cmd.encode().hex()
        print(f"  Hex: {hex_enc[:50]}{'...' if len(hex_enc) > 50 else ''}")
        print(f"  Hex length: {len(hex_enc)} chars")

        # Generate decoder
        config = ObfuscationConfig(use_hex_encoding=True)
        encoder = VBSEncoder(config)
        vbs = encoder.create_hex_decoder_vbs(cmd, execute=True)

        # Verify
        passed = "Function DecodeHex" in vbs and "WScript.Shell" in vbs and ".Run" in vbs
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  Status: {status}")
        results.append((desc, passed))

    print(f"\n" + "=" * 80)
    print(f"Multi-command Results: {sum(1 for _, p in results if p)}/{len(results)} passed")
    for desc, passed in results:
        print(f"  {'✓' if passed else '✗'} {desc}")

    return all(p for _, p in results)


if __name__ == "__main__":
    result1 = trace_command_flow()
    result2 = test_multiple_commands()

    print(f"\n" + "=" * 80)
    print(f"FINAL RESULT: {'✓ ALL TESTS PASSED' if (result1 and result2) else '✗ SOME TESTS FAILED'}")
    print("=" * 80)

    exit(0 if (result1 and result2) else 1)
