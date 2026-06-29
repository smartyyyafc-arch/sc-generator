#!/usr/bin/env python3
"""
Test script for verifying hex decoder execution handler
"""

from vbs_encoder import VBSEncoder, ObfuscationConfig
import re


def extract_variables_from_vbs(vbs_code):
    """Extract all variable names used in VBS code"""
    # Find Dim statements
    dim_pattern = r'Dim\s+([\w_]+(?:\s*,\s*[\w_]+)*)'
    dims = re.findall(dim_pattern, vbs_code)

    dim_vars = set()
    for dim_group in dims:
        # Split by comma and clean up
        vars_in_group = [v.strip() for v in dim_group.split(',')]
        dim_vars.update(vars_in_group)

    # Find Set statements
    set_pattern = r'Set\s+([\w_]+)\s*='
    set_vars = set(re.findall(set_pattern, vbs_code))

    # Find all variable assignments
    assign_pattern = r'([\w_]+)\s*=\s*(?!(?:Now|Chr|CreateObject|CLng|Mid|Len))'
    assign_vars = set(re.findall(assign_pattern, vbs_code))

    # Find function calls/references
    func_call_pattern = r'\b([\w_]+)\s*\('
    func_calls = set(re.findall(func_call_pattern, vbs_code))

    return {
        'declared': dim_vars,
        'set': set_vars,
        'assigned': assign_vars - func_calls,
        'functions': func_calls,
        'all': dim_vars | set_vars | assign_vars | func_calls
    }


def verify_hex_decoder_without_execution():
    """Test hex decoder without execution"""
    print("=" * 60)
    print("TEST 1: Hex Decoder WITHOUT Execution")
    print("=" * 60)

    config = ObfuscationConfig(use_hex_encoding=True)
    encoder = VBSEncoder(config)

    test_command = "notepad.exe"
    vbs_code = encoder.create_hex_decoder_vbs(test_command, execute=False)

    print("\nGenerated VBS Code:")
    print("-" * 60)
    print(vbs_code)
    print("-" * 60)

    # Verify structure
    assert "Function" in vbs_code, "Missing DecodeHex function"
    assert "For i = 1 To Len" in vbs_code, "Missing hex decoding loop"
    assert "Chr(CLng" in vbs_code, "Missing hex character conversion"
    assert "CreateObject" not in vbs_code, "Should not create shell without execute=True"
    assert "WScript.Shell" not in vbs_code, "Should not reference WScript.Shell without execute=True"

    vars_info = extract_variables_from_vbs(vbs_code)
    print("\nVariables Analysis:")
    print(f"  Declared: {vars_info['declared']}")
    print(f"  Set: {vars_info['set']}")
    print(f"  Assigned: {vars_info['assigned']}")
    print(f"  Functions: {vars_info['functions']}")

    print("\n✓ Test PASSED: Hex decoder without execution works correctly")


def verify_hex_decoder_with_execution():
    """Test hex decoder with execution"""
    print("\n" + "=" * 60)
    print("TEST 2: Hex Decoder WITH Execution")
    print("=" * 60)

    config = ObfuscationConfig(use_hex_encoding=True)
    encoder = VBSEncoder(config)

    test_command = "notepad.exe"
    vbs_code = encoder.create_hex_decoder_vbs(test_command, execute=True)

    print("\nGenerated VBS Code:")
    print("-" * 60)
    print(vbs_code)
    print("-" * 60)

    # Verify structure
    assert "Function" in vbs_code, "Missing DecodeHex function"
    assert "For i = 1 To Len" in vbs_code, "Missing hex decoding loop"
    assert "Chr(CLng" in vbs_code, "Missing hex character conversion"
    assert "CreateObject" in vbs_code, "Missing CreateObject for WScript.Shell"
    assert "WScript.Shell" in vbs_code, "Missing WScript.Shell reference"
    assert ".Run" in vbs_code, "Missing .Run method call"
    assert "Set" in vbs_code and "= Nothing" in vbs_code, "Missing object cleanup"

    vars_info = extract_variables_from_vbs(vbs_code)
    print("\nVariables Analysis:")
    print(f"  Declared: {vars_info['declared']}")
    print(f"  Set: {vars_info['set']}")
    print(f"  Assigned: {vars_info['assigned']}")
    print(f"  Functions: {vars_info['functions']}")

    # Verify variable usage consistency
    print("\nVariable Consistency Check:")

    # Extract shell variable
    shell_match = re.search(r'Dim ([\w_]+).*?shell_', vbs_code)
    if shell_match or 'shell_' in vbs_code:
        shell_var_pattern = r'(shell_\w+)'
        shell_vars = re.findall(shell_var_pattern, vbs_code)
        if shell_vars:
            shell_var = shell_vars[0]
            shell_uses = vbs_code.count(f"{shell_var}")
            print(f"  Shell variable '{shell_var}' declared and used {shell_uses} times")
            assert shell_uses >= 3, f"Shell variable should be used at least 3 times (declared, assigned, .Run, set=Nothing)"

    # Extract decoded variable
    decoded_pattern = r'(decoded_\w+)'
    decoded_vars = re.findall(decoded_pattern, vbs_code)
    if decoded_vars:
        decoded_var = decoded_vars[0]
        decoded_uses = vbs_code.count(decoded_var)
        print(f"  Decoded variable '{decoded_var}' declared and used {decoded_uses} times")
        assert decoded_uses >= 2, "Decoded variable should be assigned and used in .Run"

    # Extract hex variable
    hex_pattern = r'(h_\w+)'
    hex_vars = re.findall(hex_pattern, vbs_code)
    if hex_vars:
        hex_var = hex_vars[0]
        hex_uses = vbs_code.count(hex_var)
        print(f"  Hex variable '{hex_var}' declared and used {hex_uses} times")
        assert hex_uses >= 2, "Hex variable should be assigned and used in decode function"

    print("\n✓ Test PASSED: Hex decoder with execution works correctly")


def verify_variable_matching():
    """Verify that all variables are properly declared and used"""
    print("\n" + "=" * 60)
    print("TEST 3: Variable Declaration and Usage Matching")
    print("=" * 60)

    config = ObfuscationConfig(use_hex_encoding=True)
    encoder = VBSEncoder(config)

    test_command = "cmd.exe /c whoami"
    vbs_code = encoder.create_hex_decoder_vbs(test_command, execute=True)

    print("\nGenerated VBS Code:")
    print("-" * 60)
    print(vbs_code)
    print("-" * 60)

    # Extract declared variables
    dim_pattern = r'Dim\s+([\w_]+(?:\s*,\s*[\w_]+)*)'
    dims = re.findall(dim_pattern, vbs_code)
    declared_vars = set()
    for dim_group in dims:
        vars_in_group = [v.strip() for v in dim_group.split(',')]
        declared_vars.update(vars_in_group)

    # Extract used variables (excluding built-in functions and VBS keywords)
    builtin_funcs = {
        'Len', 'Chr', 'CLng', 'Mid', 'CreateObject', 'Now', 'Set', 'End',
        'Function', 'For', 'Next', 'To', 'Step', 'Dim', 'Nothing',
        'WScript', 'Shell', 'Run', 'False', 'H', 'i', 'r', 'h'
    }

    # Look for actual variable references (underscores and randomized names)
    custom_var_pattern = r'\b([a-z]+_[a-zA-Z0-9]+)\b'
    custom_vars = set(re.findall(custom_var_pattern, vbs_code, re.IGNORECASE))

    print("\nVariable Matching Analysis:")
    print(f"  Declared variables: {sorted(declared_vars)}")
    print(f"  Custom variables used: {sorted(custom_vars)}")

    # Check that custom variables are declared
    undeclared = custom_vars - declared_vars
    print(f"  Undeclared but used: {undeclared if undeclared else 'None (✓)'}")

    assert len(undeclared) == 0, f"Found undeclared variables: {undeclared}"

    print("\n✓ Test PASSED: All variables properly matched")


def show_complete_decoder_example():
    """Show a complete hex decoder example with all features"""
    print("\n" + "=" * 60)
    print("COMPLETE HEX DECODER EXAMPLE")
    print("=" * 60)

    config = ObfuscationConfig(
        use_hex_encoding=True,
        use_variable_obfuscation=True,
        use_wscript_objects=True
    )
    encoder = VBSEncoder(config)

    # Example command
    command = "powershell.exe -NoProfile -Command \"Write-Host 'Decoded'\""

    print(f"\nOriginal Command: {command}")
    print("\nGenerated Hex Decoder with Execution:")
    print("-" * 60)

    vbs_code = encoder.create_hex_decoder_vbs(command, execute=True)
    print(vbs_code)
    print("-" * 60)

    # Show hex encoding
    hex_encoded = command.encode().hex()
    print(f"\nHex Encoding Details:")
    print(f"  Command: {command}")
    print(f"  Hex: {hex_encoded}")
    print(f"  Length: {len(hex_encoded)} characters")


if __name__ == "__main__":
    try:
        verify_hex_decoder_without_execution()
        verify_hex_decoder_with_execution()
        verify_variable_matching()
        show_complete_decoder_example()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ Test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
