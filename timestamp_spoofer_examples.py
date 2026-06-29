#!/usr/bin/env python3
"""
Timestamp Spoofer - Usage Examples
Practical examples demonstrating file timestamp spoofing techniques
"""

import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from timestamp_spoofer import (
    TimestampSpoofer,
    SystemFileTimestampMatcher,
    spoof_to_reference,
    spoof_to_date,
    spoof_batch_files
)


def example_1_basic_spoofing():
    """Example 1: Basic timestamp spoofing to match system file"""
    print("=" * 60)
    print("Example 1: Basic Timestamp Spoofing")
    print("=" * 60)

    # Create test file
    test_file = "/tmp/payload.vbs"
    with open(test_file, 'w') as f:
        f.write("MsgBox \"Test\"")

    spoofer = TimestampSpoofer()

    # Get original timestamps
    orig_mtime, orig_atime, _ = spoofer.get_file_timestamps(test_file)
    print(f"Original mtime: {datetime.fromtimestamp(orig_mtime)}")
    print(f"Original atime: {datetime.fromtimestamp(orig_atime)}\n")

    # Spoof to match system file
    system_file = "/bin/ls"
    if os.path.exists(system_file):
        info = spoofer.spoof_to_match_file(test_file, system_file)
        print(f"Spoofed to match: {system_file}")
        print(f"New mtime: {info.mtime_dt}")
        print(f"New atime: {info.atime_dt}")
        print(f"Success: {info.spoof_success}\n")
    else:
        print(f"System file not found: {system_file}\n")

    # Cleanup
    os.remove(test_file)


def example_2_spoof_to_specific_date():
    """Example 2: Spoof to specific date and time"""
    print("=" * 60)
    print("Example 2: Spoof to Specific Date/Time")
    print("=" * 60)

    test_file = "/tmp/old_script.bat"
    with open(test_file, 'w') as f:
        f.write("@echo off\necho Hello")

    spoofer = TimestampSpoofer()

    # Set to old date
    target_date = datetime(2019, 6, 15, 14, 30, 0)
    info = spoofer.spoof_to_datetime(test_file, target_date)

    print(f"Target date: {target_date}")
    print(f"Actual mtime: {info.mtime_dt}")
    print(f"Success: {info.spoof_success}\n")

    # Cleanup
    os.remove(test_file)


def example_3_timestamp_delta():
    """Example 3: Spoof with time delta from reference file"""
    print("=" * 60)
    print("Example 3: Spoof With Time Delta")
    print("=" * 60)

    # Create files
    reference_file = "/tmp/ref_file.txt"
    target_file = "/tmp/target_file.txt"

    with open(reference_file, 'w') as f:
        f.write("Reference")
    with open(target_file, 'w') as f:
        f.write("Target")

    # Set reference to specific date
    ref_date = datetime(2023, 6, 1)
    os.utime(reference_file, (ref_date.timestamp(), ref_date.timestamp()))

    spoofer = TimestampSpoofer()

    # Spoof target to 2 weeks after reference
    info = spoofer.spoof_with_delta(target_file, reference_file, days_delta=14)

    print(f"Reference date: {ref_date}")
    print(f"Target date (ref + 14 days): {info.mtime_dt}")
    print(f"Success: {info.spoof_success}\n")

    # Cleanup
    os.remove(reference_file)
    os.remove(target_file)


def example_4_batch_spoofing():
    """Example 4: Spoof multiple files at once"""
    print("=" * 60)
    print("Example 4: Batch Timestamp Spoofing")
    print("=" * 60)

    # Create reference and target files
    reference_file = "/tmp/reference.txt"
    with open(reference_file, 'w') as f:
        f.write("Reference")

    target_files = [
        "/tmp/payload1.ps1",
        "/tmp/payload2.vbs",
        "/tmp/payload3.bat"
    ]

    for target in target_files:
        with open(target, 'w') as f:
            f.write("Payload")

    spoofer = TimestampSpoofer()

    # Batch spoof all targets to match reference
    results = spoofer.spoof_batch(target_files, reference_file=reference_file)

    print(f"Spoofed {len(results)} files to match reference:\n")
    for target, info in results.items():
        if info:
            print(f"  {os.path.basename(target)}: {info.mtime_dt}")
    print()

    # Cleanup
    os.remove(reference_file)
    for target in target_files:
        if os.path.exists(target):
            os.remove(target)


def example_5_clone_timestamps():
    """Example 5: Clone timestamps to simulate file family"""
    print("=" * 60)
    print("Example 5: Clone Timestamps to Multiple Files")
    print("=" * 60)

    # Create source file with specific timestamp
    source_file = "/tmp/windows_system.dll"
    with open(source_file, 'w') as f:
        f.write("System library")

    # Set to Windows 10 release date
    win10_date = datetime(2015, 7, 29, 0, 0, 0)
    os.utime(source_file, (win10_date.timestamp(), win10_date.timestamp()))

    # Create target files
    target_files = [
        "/tmp/dll_copy1.dll",
        "/tmp/dll_copy2.dll",
        "/tmp/dll_copy3.dll"
    ]

    for target in target_files:
        with open(target, 'w') as f:
            f.write("DLL copy")

    spoofer = TimestampSpoofer()

    # Clone timestamps
    results = spoofer.clone_timestamps(source_file, target_files)

    print(f"Source file timestamp: {win10_date}")
    print(f"Cloned to {len(results)} files:\n")
    for target, info in results.items():
        if info:
            print(f"  {os.path.basename(target)}: {info.mtime_dt}")
    print()

    # Cleanup
    os.remove(source_file)
    for target in target_files:
        if os.path.exists(target):
            os.remove(target)


def example_6_restore_timestamps():
    """Example 6: Restore original timestamps"""
    print("=" * 60)
    print("Example 6: Restore Original Timestamps")
    print("=" * 60)

    test_file = "/tmp/modifiable.txt"
    with open(test_file, 'w') as f:
        f.write("Test content")

    spoofer = TimestampSpoofer()

    # Get original
    orig_mtime, _, _ = spoofer.get_file_timestamps(test_file)
    print(f"Original mtime: {datetime.fromtimestamp(orig_mtime)}")

    # Spoof to old date
    old_date = datetime(2000, 1, 1, 0, 0, 0)
    spoofer.spoof_to_datetime(test_file, old_date)
    spoofed_mtime, _, _ = spoofer.get_file_timestamps(test_file)
    print(f"Spoofed mtime: {datetime.fromtimestamp(spoofed_mtime)}")

    # Restore
    spoofer.restore_timestamps(test_file)
    restored_mtime, _, _ = spoofer.get_file_timestamps(test_file)
    print(f"Restored mtime: {datetime.fromtimestamp(restored_mtime)}")
    print(f"Successfully restored: {abs(restored_mtime - orig_mtime) < 1}\n")

    # Cleanup
    os.remove(test_file)


def example_7_system_file_matching():
    """Example 7: Match file to system file types"""
    print("=" * 60)
    print("Example 7: Match File to System File Types")
    print("=" * 60)

    test_file = "/tmp/disguised.exe"
    with open(test_file, 'w') as f:
        f.write("Executable")

    matcher = SystemFileTimestampMatcher()

    try:
        # Match to system binary
        print("Matching to system binary...")
        info = matcher.match_to_system_binary(test_file)
        print(f"Matched timestamp: {info.mtime_dt}")
        print(f"Success: {info.spoof_success}\n")
    except FileNotFoundError as e:
        print(f"Could not match: {e}\n")

    # Cleanup
    os.remove(test_file)


def example_8_random_timestamps():
    """Example 8: Randomize timestamps within date range"""
    print("=" * 60)
    print("Example 8: Randomize Timestamps in Date Range")
    print("=" * 60)

    test_file = "/tmp/random_date.txt"
    with open(test_file, 'w') as f:
        f.write("Content")

    spoofer = TimestampSpoofer()

    # Define date range (all of 2022)
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 31)
    start_ts = start_date.timestamp()
    end_ts = end_date.timestamp()

    # Randomize
    info = spoofer.randomize_within_range(test_file, start_ts, end_ts)

    print(f"Range: {start_date} to {end_date}")
    print(f"Random timestamp: {info.mtime_dt}")
    print(f"Success: {info.spoof_success}\n")

    # Cleanup
    os.remove(test_file)


def example_9_timestamp_comparison():
    """Example 9: Compare timestamps between files"""
    print("=" * 60)
    print("Example 9: Compare File Timestamps")
    print("=" * 60)

    # Create files with different timestamps
    file1 = "/tmp/file1.txt"
    file2 = "/tmp/file2.txt"

    with open(file1, 'w') as f:
        f.write("File 1")
    with open(file2, 'w') as f:
        f.write("File 2")

    spoofer = TimestampSpoofer()

    # Set file1 to specific date
    date1 = datetime(2023, 1, 1)
    os.utime(file1, (date1.timestamp(), date1.timestamp()))

    # Set file2 to 5 days later
    date2 = date1 + timedelta(days=5)
    os.utime(file2, (date2.timestamp(), date2.timestamp()))

    # Get delta
    delta = spoofer.get_timestamp_delta(file1, file2)

    print(f"File 1 timestamp: {date1}")
    print(f"File 2 timestamp: {date2}")
    print(f"Delta (file1 - file2): {delta} seconds ({delta / 86400} days)\n")

    # Cleanup
    os.remove(file1)
    os.remove(file2)


def example_10_history_and_tracking():
    """Example 10: Track spoofing history"""
    print("=" * 60)
    print("Example 10: Track Spoofing History")
    print("=" * 60)

    files = [
        "/tmp/tracked1.txt",
        "/tmp/tracked2.txt",
        "/tmp/tracked3.txt"
    ]

    for f in files:
        with open(f, 'w') as fp:
            fp.write("Tracked")

    spoofer = TimestampSpoofer()

    # Spoof multiple files
    ref_file = "/tmp/reference.txt"
    with open(ref_file, 'w') as f:
        f.write("Reference")

    results = spoofer.spoof_batch(files, reference_file=ref_file)

    # Get history
    history = spoofer.get_history()
    print(f"Spoofing history for {len(history)} files:\n")

    for file_path, info in history.items():
        print(f"  {os.path.basename(file_path)}:")
        print(f"    Original: {datetime.fromtimestamp(info.original_mtime)}")
        print(f"    Spoofed:  {info.mtime_dt}")

    print(f"\nTotal history entries: {len(history)}\n")

    # Clear history
    cleared = spoofer.clear_history()
    print(f"Cleared {cleared} history entries\n")

    # Cleanup
    os.remove(ref_file)
    for f in files:
        if os.path.exists(f):
            os.remove(f)


def example_11_convenience_functions():
    """Example 11: Using convenience functions"""
    print("=" * 60)
    print("Example 11: Convenience Functions")
    print("=" * 60)

    # Create test files
    target = "/tmp/convenience_target.txt"
    reference = "/tmp/convenience_ref.txt"

    with open(target, 'w') as f:
        f.write("Target")
    with open(reference, 'w') as f:
        f.write("Reference")

    # Use convenience function - spoof to reference
    print("Using spoof_to_reference()...")
    info1 = spoof_to_reference(target, reference)
    print(f"  Result: {info1.mtime_dt}\n")

    # Use convenience function - spoof to date
    print("Using spoof_to_date()...")
    target_date = datetime(2021, 3, 15, 9, 30, 0)
    info2 = spoof_to_date(target, target_date)
    print(f"  Target: {target_date}")
    print(f"  Result: {info2.mtime_dt}\n")

    # Cleanup
    os.remove(target)
    os.remove(reference)


def example_12_advanced_payload_concealment():
    """Example 12: Advanced payload concealment scenario"""
    print("=" * 60)
    print("Example 12: Advanced Payload Concealment")
    print("=" * 60)

    spoofer = TimestampSpoofer()

    # Create simulated payload files
    payload_files = [
        ("/tmp/system32_fake.dll", "C:\\Windows\\System32\\kernel32.dll"),
        ("/tmp/driver_fake.sys", "C:\\Windows\\System32\\drivers\\disk.sys"),
    ]

    print("Payload concealment simulation:\n")

    for payload_path, system_path_desc in payload_files:
        with open(payload_path, 'w') as f:
            f.write("Obfuscated payload")

        # Get approximate Windows 10 system file dates
        win10_base = datetime(2015, 7, 29)
        os.utime(payload_path, (win10_base.timestamp(), win10_base.timestamp()))

        print(f"Payload: {os.path.basename(payload_path)}")
        print(f"  Spoofed timestamp: {win10_base}")
        print(f"  Simulates: {system_path_desc}\n")

        # Cleanup
        os.remove(payload_path)


if __name__ == "__main__":
    examples = [
        example_1_basic_spoofing,
        example_2_spoof_to_specific_date,
        example_3_timestamp_delta,
        example_4_batch_spoofing,
        example_5_clone_timestamps,
        example_6_restore_timestamps,
        example_7_system_file_matching,
        example_8_random_timestamps,
        example_9_timestamp_comparison,
        example_10_history_and_tracking,
        example_11_convenience_functions,
        example_12_advanced_payload_concealment,
    ]

    print("\n" + "=" * 60)
    print("TIMESTAMP SPOOFER - USAGE EXAMPLES")
    print("=" * 60 + "\n")

    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"Error in example {i}: {e}\n")

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
