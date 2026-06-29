#!/usr/bin/env python3
"""
File Disguiser - Real-World Usage Examples
"""

from file_disguiser import FileDisguiser, DisguiseType


def example_1_hide_config():
    """Hide configuration files as innocuous types."""
    print("=== Example 1: Hide Configuration Files ===\n")

    disguiser = FileDisguiser("./examples/configs")

    # Hide API config as log file
    api_config = """
[api]
endpoint=https://api.example.com
key=sk_live_abc123def456
secret=sk_secret_xyz789
timeout=30
retry_count=3
"""

    path = disguiser.write_disguised_text("app_config", api_config, DisguiseType.LOG)
    print(f"✓ Hidden API config as: {path}")

    # Hide database credentials as JSON (ironic)
    db_creds = """
{
  "host": "db.internal.example.com",
  "port": 5432,
  "user": "admin",
  "password": "SuperSecretPassword123!",
  "database": "production"
}
"""

    db_path = disguiser.write_disguised_text("database", db_creds, DisguiseType.JSON)
    print(f"✓ Hidden DB credentials as: {db_path}\n")


def example_2_hide_scripts():
    """Hide executable scripts as document types."""
    print("=== Example 2: Hide Scripts as Documents ===\n")

    disguiser = FileDisguiser("./examples/scripts")

    # Hide Python script as PDF
    python_script = """#!/usr/bin/env python3
import sys
import os

def main():
    print("Hidden Python script running...")
    data = sys.argv[1] if len(sys.argv) > 1 else "default"
    process(data)

def process(data):
    # Do something with data
    pass

if __name__ == "__main__":
    main()
"""

    path = disguiser.write_disguised_text("automation", python_script, DisguiseType.PDF)
    print(f"✓ Hidden Python script as PDF: {path}")

    # Hide Bash script as Word document
    bash_script = """#!/bin/bash

# System monitoring script
LOGFILE="/var/log/monitor.log"
THRESHOLD=80

check_disk_usage() {
    usage=$(df / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    if [ "$usage" -gt "$THRESHOLD" ]; then
        echo "WARNING: Disk usage at $usage%" >> "$LOGFILE"
    fi
}

check_memory() {
    # Check system memory
    free -h | grep Mem
}

main() {
    check_disk_usage
    check_memory
}

main "$@"
"""

    bash_path = disguiser.write_disguised_text("monitor", bash_script, DisguiseType.DOCX)
    print(f"✓ Hidden Bash script as Word document: {bash_path}\n")


def example_3_hide_payloads():
    """Hide binary payloads as common file types."""
    print("=== Example 3: Hide Binary Payloads ===\n")

    disguiser = FileDisguiser("./examples/payloads")

    # Simulate binary payload (real executables would be used in practice)
    fake_payload = b"\x4d\x5a\x90\x00\x03\x00\x00\x00" + b"PAYLOAD_DATA" * 50

    # Hide as Office document
    exe_path = disguiser.write_disguised_binary("document", fake_payload, DisguiseType.DOCX)
    print(f"✓ Hidden binary payload as DOCX: {exe_path}")

    # Hide as PDF
    pdf_path = disguiser.write_disguised_binary("report", fake_payload, DisguiseType.PDF)
    print(f"✓ Hidden binary payload as PDF: {pdf_path}")

    # Hide as Excel spreadsheet
    xls_path = disguiser.write_disguised_binary("data", fake_payload, DisguiseType.XLSX)
    print(f"✓ Hidden binary payload as XLSX: {xls_path}\n")


def example_4_track_and_manage():
    """Track disguised files and manage them."""
    print("=== Example 4: Track and Manage Files ===\n")

    disguiser = FileDisguiser("./examples/managed")

    # Create multiple disguised files
    files_to_create = [
        ("secret1", "This is secret data 1", DisguiseType.TXT),
        ("secret2", "This is secret data 2", DisguiseType.LOG),
        ("secret3", b"Binary secret data 3", DisguiseType.PDF),
    ]

    for name, content, disguise in files_to_create:
        if isinstance(content, bytes):
            disguiser.write_disguised_binary(name, content, disguise)
        else:
            disguiser.write_disguised_text(name, content, disguise)

    # List all tracked files
    print("Tracked disguised files:")
    for info in disguiser.list_disguised_files():
        print(f"  - {info['original_name']}.{info['disguise_ext']} "
              f"({info['size']} bytes, type: {info['content_type']})")

    print()


def example_5_extract_recover():
    """Create and recover disguised files."""
    print("=== Example 5: Extract and Recover Files ===\n")

    disguiser = FileDisguiser("./examples/recovery")

    # Hide some data
    original_content = "CONFIDENTIAL: Project Apollo Status Report\n\nPhase 1: Complete\nPhase 2: In Progress\nPhase 3: Pending"
    hidden_path = disguiser.write_disguised_text("report", original_content, DisguiseType.PDF)
    print(f"✓ Hidden file as: {hidden_path}")

    # Later, recover it
    recovered_path = disguiser.undisguise(hidden_path)
    print(f"✓ Recovered to: {recovered_path}")

    # Verify content
    with open(recovered_path, 'r') as f:
        recovered_content = f.read()
    print(f"✓ Content verified: {recovered_content[:50]}...\n")


def example_6_batch_operations():
    """Batch hide and organize multiple files."""
    print("=== Example 6: Batch Operations ===\n")

    disguiser = FileDisguiser("./examples/batch")

    # Simulate multiple file sources
    file_sources = {
        "application": ("app.py", "def main(): pass", DisguiseType.TXT),
        "configuration": ("config.ini", "[settings]\nkey=value", DisguiseType.LOG),
        "credentials": ("auth.json", '{"token": "xyz123"}', DisguiseType.JSON),
    }

    print("Processing batch operation...")
    for category, (filename, content, disguise) in file_sources.items():
        disguiser.write_disguised_text(filename.replace(".py", "").replace(".ini", "").replace(".json", ""),
                                       content, disguise)
        print(f"  ✓ {filename} -> .{disguise.value}")

    print(f"\n✓ Total files hidden: {len(disguiser.list_disguised_files())}\n")


def example_7_custom_extensions():
    """Use custom or non-standard extensions."""
    print("=== Example 7: Custom Extensions ===\n")

    disguiser = FileDisguiser("./examples/custom")

    # Use any custom extension
    content = "Custom extension content"
    
    custom_ext_1 = disguiser.write_disguised_text("file", content, "custom")
    print(f"✓ Custom extension: {custom_ext_1}")

    custom_ext_2 = disguiser.write_disguised_text("data", content, "xyz123")
    print(f"✓ Custom extension: {custom_ext_2}")

    # Even unusual combinations
    custom_ext_3 = disguiser.write_disguised_text("obscure", content, "backup_old")
    print(f"✓ Unusual extension: {custom_ext_3}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("FILE DISGUISER - USAGE EXAMPLES")
    print("="*60 + "\n")

    try:
        example_1_hide_config()
        example_2_hide_scripts()
        example_3_hide_payloads()
        example_4_track_and_manage()
        example_5_extract_recover()
        example_6_batch_operations()
        example_7_custom_extensions()

        print("="*60)
        print("All examples completed successfully!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()
