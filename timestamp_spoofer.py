#!/usr/bin/env python3
"""
Timestamp Spoofer - Modify file timestamps to match system files
Handles modification time (mtime), access time (atime), and change time (ctime) spoofing
For authorized pentesting and security research
"""

import os
import stat
import time
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass
import platform
import subprocess


@dataclass
class TimestampInfo:
    """File timestamp information"""
    file_path: str
    original_mtime: float
    original_atime: float
    original_ctime: float
    spoofed_mtime: float
    spoofed_atime: float
    spoofed_ctime: float
    mtime_dt: str  # Human readable
    atime_dt: str  # Human readable
    ctime_dt: str  # Human readable
    spoof_success: bool


class TimestampSpoofer:
    """Spoof file timestamps to match system or reference files"""

    def __init__(self):
        """Initialize timestamp spoofer"""
        self.system = platform.system()
        self.timestamp_history: Dict[str, TimestampInfo] = {}

    def get_file_timestamps(self, file_path: str) -> Tuple[float, float, float]:
        """
        Get current file timestamps (mtime, atime, ctime)

        Args:
            file_path: Path to file

        Returns:
            Tuple of (mtime, atime, ctime) in Unix epoch
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_stat = os.stat(file_path)
        return (
            file_stat.st_mtime,
            file_stat.st_atime,
            file_stat.st_ctime
        )

    def get_file_timestamps_dt(self, file_path: str) -> Tuple[str, str, str]:
        """
        Get file timestamps as human-readable datetime strings

        Args:
            file_path: Path to file

        Returns:
            Tuple of (mtime_str, atime_str, ctime_str)
        """
        mtime, atime, ctime = self.get_file_timestamps(file_path)
        return (
            datetime.fromtimestamp(mtime).isoformat(),
            datetime.fromtimestamp(atime).isoformat(),
            datetime.fromtimestamp(ctime).isoformat()
        )

    def spoof_to_match_file(self,
                           target_file: str,
                           reference_file: str,
                           spoof_atime: bool = True,
                           spoof_mtime: bool = True) -> TimestampInfo:
        """
        Spoof target file timestamps to match reference file

        Args:
            target_file: File to modify timestamps on
            reference_file: File to copy timestamps from
            spoof_atime: Also spoof access time
            spoof_mtime: Also spoof modification time

        Returns:
            TimestampInfo object with before/after timestamps
        """
        if not os.path.exists(target_file):
            raise FileNotFoundError(f"Target file not found: {target_file}")

        if not os.path.exists(reference_file):
            raise FileNotFoundError(f"Reference file not found: {reference_file}")

        # Get original timestamps
        orig_mtime, orig_atime, orig_ctime = self.get_file_timestamps(target_file)

        # Get reference timestamps
        ref_mtime, ref_atime, _ = self.get_file_timestamps(reference_file)

        # Apply timestamps
        try:
            if spoof_mtime and spoof_atime:
                os.utime(target_file, (ref_atime, ref_mtime))
            elif spoof_mtime:
                os.utime(target_file, (ref_atime, ref_mtime))
            elif spoof_atime:
                os.utime(target_file, (ref_atime, orig_mtime))

            # Get new timestamps
            new_mtime, new_atime, new_ctime = self.get_file_timestamps(target_file)

            # Create info record
            mtime_dt, atime_dt, ctime_dt = self.get_file_timestamps_dt(target_file)
            info = TimestampInfo(
                file_path=target_file,
                original_mtime=orig_mtime,
                original_atime=orig_atime,
                original_ctime=orig_ctime,
                spoofed_mtime=new_mtime,
                spoofed_atime=new_atime,
                spoofed_ctime=new_ctime,
                mtime_dt=mtime_dt,
                atime_dt=atime_dt,
                ctime_dt=ctime_dt,
                spoof_success=True
            )

            self.timestamp_history[target_file] = info
            return info

        except Exception as e:
            raise IOError(f"Failed to spoof timestamps: {e}")

    def spoof_to_timestamp(self,
                          file_path: str,
                          target_timestamp: float,
                          spoof_atime: bool = True,
                          spoof_mtime: bool = True) -> TimestampInfo:
        """
        Spoof file timestamps to specific Unix epoch time

        Args:
            file_path: File to modify
            target_timestamp: Target Unix epoch timestamp
            spoof_atime: Also spoof access time
            spoof_mtime: Also spoof modification time

        Returns:
            TimestampInfo object
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get original timestamps
        orig_mtime, orig_atime, orig_ctime = self.get_file_timestamps(file_path)

        # Apply timestamps
        try:
            if spoof_mtime and spoof_atime:
                os.utime(file_path, (target_timestamp, target_timestamp))
            elif spoof_mtime:
                os.utime(file_path, (orig_atime, target_timestamp))
            elif spoof_atime:
                os.utime(file_path, (target_timestamp, orig_mtime))

            # Get new timestamps
            new_mtime, new_atime, new_ctime = self.get_file_timestamps(file_path)

            # Create info record
            mtime_dt, atime_dt, ctime_dt = self.get_file_timestamps_dt(file_path)
            info = TimestampInfo(
                file_path=file_path,
                original_mtime=orig_mtime,
                original_atime=orig_atime,
                original_ctime=orig_ctime,
                spoofed_mtime=new_mtime,
                spoofed_atime=new_atime,
                spoofed_ctime=new_ctime,
                mtime_dt=mtime_dt,
                atime_dt=atime_dt,
                ctime_dt=ctime_dt,
                spoof_success=True
            )

            self.timestamp_history[file_path] = info
            return info

        except Exception as e:
            raise IOError(f"Failed to spoof timestamps: {e}")

    def spoof_to_datetime(self,
                         file_path: str,
                         target_datetime: datetime,
                         spoof_atime: bool = True,
                         spoof_mtime: bool = True) -> TimestampInfo:
        """
        Spoof file timestamps to specific datetime

        Args:
            file_path: File to modify
            target_datetime: Target datetime object
            spoof_atime: Also spoof access time
            spoof_mtime: Also spoof modification time

        Returns:
            TimestampInfo object
        """
        target_timestamp = target_datetime.timestamp()
        return self.spoof_to_timestamp(
            file_path,
            target_timestamp,
            spoof_atime=spoof_atime,
            spoof_mtime=spoof_mtime
        )

    def spoof_to_system_file(self,
                            target_file: str,
                            system_file_path: str = None) -> TimestampInfo:
        """
        Spoof target file timestamps to match a standard system file

        Args:
            target_file: File to modify
            system_file_path: System file to match (or None for auto-detect)

        Returns:
            TimestampInfo object
        """
        if system_file_path is None:
            system_file_path = self._get_system_reference_file()

        return self.spoof_to_match_file(target_file, system_file_path)

    def spoof_batch(self,
                   file_paths: List[str],
                   reference_file: str = None,
                   target_timestamp: float = None) -> Dict[str, TimestampInfo]:
        """
        Spoof timestamps for multiple files

        Args:
            file_paths: List of files to modify
            reference_file: File to copy timestamps from (or use target_timestamp)
            target_timestamp: Unix epoch timestamp (used if reference_file is None)

        Returns:
            Dictionary mapping file paths to TimestampInfo
        """
        results = {}

        if reference_file and not os.path.exists(reference_file):
            raise FileNotFoundError(f"Reference file not found: {reference_file}")

        for file_path in file_paths:
            try:
                if reference_file:
                    info = self.spoof_to_match_file(file_path, reference_file)
                elif target_timestamp:
                    info = self.spoof_to_timestamp(file_path, target_timestamp)
                else:
                    raise ValueError("Either reference_file or target_timestamp required")

                results[file_path] = info
            except Exception as e:
                print(f"Error spoofing {file_path}: {e}")
                results[file_path] = None

        return results

    def spoof_with_delta(self,
                        target_file: str,
                        reference_file: str,
                        days_delta: int = 0,
                        hours_delta: int = 0,
                        minutes_delta: int = 0) -> TimestampInfo:
        """
        Spoof target file to match reference file plus/minus time delta

        Args:
            target_file: File to modify
            reference_file: File to copy timestamps from
            days_delta: Days to add/subtract
            hours_delta: Hours to add/subtract
            minutes_delta: Minutes to add/subtract

        Returns:
            TimestampInfo object
        """
        if not os.path.exists(reference_file):
            raise FileNotFoundError(f"Reference file not found: {reference_file}")

        # Get reference timestamp
        ref_mtime, ref_atime, _ = self.get_file_timestamps(reference_file)

        # Calculate delta
        delta = timedelta(
            days=days_delta,
            hours=hours_delta,
            minutes=minutes_delta
        )
        delta_seconds = delta.total_seconds()

        # Apply delta to reference timestamp
        adjusted_timestamp = ref_mtime + delta_seconds

        return self.spoof_to_timestamp(target_file, adjusted_timestamp)

    def randomize_within_range(self,
                              file_path: str,
                              start_timestamp: float,
                              end_timestamp: float) -> TimestampInfo:
        """
        Spoof file timestamp to random value within range

        Args:
            file_path: File to modify
            start_timestamp: Start of range (Unix epoch)
            end_timestamp: End of range (Unix epoch)

        Returns:
            TimestampInfo object
        """
        import random
        if start_timestamp > end_timestamp:
            start_timestamp, end_timestamp = end_timestamp, start_timestamp

        random_timestamp = random.uniform(start_timestamp, end_timestamp)
        return self.spoof_to_timestamp(file_path, random_timestamp)

    def restore_timestamps(self, file_path: str) -> bool:
        """
        Restore file to original timestamps from history

        Args:
            file_path: File to restore

        Returns:
            True if restoration successful
        """
        if file_path not in self.timestamp_history:
            return False

        try:
            info = self.timestamp_history[file_path]
            os.utime(
                file_path,
                (info.original_atime, info.original_mtime)
            )
            return True
        except Exception as e:
            print(f"Error restoring timestamps: {e}")
            return False

    def clone_timestamps(self,
                        source_file: str,
                        target_files: List[str]) -> Dict[str, TimestampInfo]:
        """
        Clone timestamps from source file to multiple target files

        Args:
            source_file: File to copy timestamps from
            target_files: Files to apply timestamps to

        Returns:
            Dictionary mapping target files to TimestampInfo
        """
        results = {}
        for target_file in target_files:
            try:
                info = self.spoof_to_match_file(target_file, source_file)
                results[target_file] = info
            except Exception as e:
                print(f"Error cloning to {target_file}: {e}")
                results[target_file] = None

        return results

    def get_timestamp_delta(self,
                           file1: str,
                           file2: str) -> float:
        """
        Get time difference between two files (in seconds)

        Args:
            file1: First file
            file2: Second file

        Returns:
            Difference in seconds (file1 - file2)
        """
        mtime1, _, _ = self.get_file_timestamps(file1)
        mtime2, _, _ = self.get_file_timestamps(file2)
        return mtime1 - mtime2

    @staticmethod
    def _get_system_reference_file() -> str:
        """
        Get standard system reference file for spoofing

        Returns:
            Path to system file
        """
        system = platform.system()

        if system == "Windows":
            # Common system files on Windows
            candidates = [
                "C:\\Windows\\System32\\kernel32.dll",
                "C:\\Windows\\System32\\ntdll.dll",
                "C:\\Windows\\notepad.exe",
            ]
        elif system == "Darwin":  # macOS
            candidates = [
                "/System/Library/CoreServices/Finder.app/Contents/MacOS/Finder",
                "/usr/bin/python3",
                "/bin/ls",
            ]
        else:  # Linux and others
            candidates = [
                "/bin/ls",
                "/bin/bash",
                "/usr/bin/python3",
                "/etc/passwd",
            ]

        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

        raise FileNotFoundError("Could not find suitable system reference file")

    def get_history(self) -> Dict[str, TimestampInfo]:
        """Get timestamp spoofing history"""
        return self.timestamp_history.copy()

    def clear_history(self) -> int:
        """Clear timestamp history and return count"""
        count = len(self.timestamp_history)
        self.timestamp_history.clear()
        return count


class SystemFileTimestampMatcher:
    """Match file timestamps to appear as system files"""

    def __init__(self):
        """Initialize system file matcher"""
        self.spoofer = TimestampSpoofer()
        self.system = platform.system()

    def match_to_system_library(self, target_file: str) -> TimestampInfo:
        """
        Make file appear as system library by matching timestamps

        Args:
            target_file: File to modify

        Returns:
            TimestampInfo object
        """
        if self.system == "Windows":
            system_lib = "C:\\Windows\\System32\\kernel32.dll"
        elif self.system == "Darwin":
            system_lib = "/usr/lib/libSystem.B.dylib"
        else:
            system_lib = "/lib/x86_64-linux-gnu/libc.so.6"

        if os.path.exists(system_lib):
            return self.spoofer.spoof_to_match_file(target_file, system_lib)

        raise FileNotFoundError(f"System library not found: {system_lib}")

    def match_to_system_binary(self, target_file: str) -> TimestampInfo:
        """
        Make file appear as system binary

        Args:
            target_file: File to modify

        Returns:
            TimestampInfo object
        """
        if self.system == "Windows":
            system_bin = "C:\\Windows\\System32\\cmd.exe"
        elif self.system == "Darwin":
            system_bin = "/usr/bin/python3"
        else:
            system_bin = "/bin/ls"

        if os.path.exists(system_bin):
            return self.spoofer.spoof_to_match_file(target_file, system_bin)

        raise FileNotFoundError(f"System binary not found: {system_bin}")

    def match_to_config_file(self, target_file: str) -> TimestampInfo:
        """
        Make file appear as system config file

        Args:
            target_file: File to modify

        Returns:
            TimestampInfo object
        """
        if self.system == "Windows":
            config_file = "C:\\Windows\\System.ini"
        elif self.system == "Darwin":
            config_file = "/etc/hosts"
        else:
            config_file = "/etc/passwd"

        if os.path.exists(config_file):
            return self.spoofer.spoof_to_match_file(target_file, config_file)

        raise FileNotFoundError(f"Config file not found: {config_file}")

    def get_spoofer(self) -> TimestampSpoofer:
        """Get underlying spoofer instance"""
        return self.spoofer


# Convenience functions

def spoof_to_reference(target_file: str, reference_file: str) -> TimestampInfo:
    """
    Quickly spoof target file to match reference file

    Args:
        target_file: File to modify
        reference_file: File to copy timestamps from

    Returns:
        TimestampInfo object
    """
    spoofer = TimestampSpoofer()
    return spoofer.spoof_to_match_file(target_file, reference_file)


def spoof_to_date(file_path: str, target_date: datetime) -> TimestampInfo:
    """
    Quickly spoof file to specific datetime

    Args:
        file_path: File to modify
        target_date: Target datetime

    Returns:
        TimestampInfo object
    """
    spoofer = TimestampSpoofer()
    return spoofer.spoof_to_datetime(file_path, target_date)


def spoof_batch_files(file_paths: List[str], reference_file: str) -> Dict[str, TimestampInfo]:
    """
    Spoof multiple files to match reference

    Args:
        file_paths: Files to modify
        reference_file: File to copy timestamps from

    Returns:
        Dictionary mapping file paths to TimestampInfo
    """
    spoofer = TimestampSpoofer()
    return spoofer.spoof_batch(file_paths, reference_file=reference_file)


if __name__ == "__main__":
    # Example usage
    print("=== Timestamp Spoofer Examples ===\n")

    # Example 1: Spoof to match system file
    print("Example 1: Spoof file to match system reference")
    spoofer = TimestampSpoofer()

    # Create a test file
    test_file = "/tmp/test_payload.txt"
    with open(test_file, 'w') as f:
        f.write("Test payload")

    try:
        # Get original timestamps
        orig_mtime, orig_atime, orig_ctime = spoofer.get_file_timestamps(test_file)
        print(f"Original mtime: {datetime.fromtimestamp(orig_mtime)}")
        print(f"Original atime: {datetime.fromtimestamp(orig_atime)}\n")

        # Spoof to system file
        system_file = "/bin/ls"
        if os.path.exists(system_file):
            info = spoofer.spoof_to_match_file(test_file, system_file)
            print(f"Spoofed to match: {system_file}")
            print(f"New mtime: {info.mtime_dt}")
            print(f"New atime: {info.atime_dt}\n")
        else:
            print("System reference file not found\n")

        # Example 2: Spoof with timestamp delta
        print("Example 2: Spoof with time delta")
        if os.path.exists(system_file):
            info2 = spoofer.spoof_with_delta(test_file, system_file, days_delta=-7)
            print(f"Spoofed to 7 days before {system_file}")
            print(f"New mtime: {info2.mtime_dt}\n")

        # Example 3: Spoof to specific datetime
        print("Example 3: Spoof to specific datetime")
        target_dt = datetime(2023, 1, 15, 12, 30, 0)
        info3 = spoofer.spoof_to_datetime(test_file, target_dt)
        print(f"Spoofed to: {target_dt}")
        print(f"Actual mtime: {info3.mtime_dt}\n")

        # Example 4: Clone timestamps to multiple files
        print("Example 4: Clone timestamps to batch files")
        test_files = ["/tmp/clone1.txt", "/tmp/clone2.txt", "/tmp/clone3.txt"]
        for tf in test_files:
            with open(tf, 'w') as f:
                f.write("Clone test")

        clone_results = spoofer.clone_timestamps(test_file, test_files)
        for fname, info in clone_results.items():
            if info:
                print(f"{fname}: {info.mtime_dt}")

        # Example 5: Restore original timestamps
        print("\nExample 5: Restore original timestamps")
        if spoofer.restore_timestamps(test_file):
            restored_mtime, _, _ = spoofer.get_file_timestamps(test_file)
            print(f"Restored mtime: {datetime.fromtimestamp(restored_mtime)}")

    finally:
        # Cleanup
        for f in [test_file] + test_files:
            if os.path.exists(f):
                os.remove(f)
