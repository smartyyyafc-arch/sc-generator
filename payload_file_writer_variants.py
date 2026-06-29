#!/usr/bin/env python3
"""
Payload File Writer Variants - Multiple Windows temp/data locations
Creates file writer implementations for %TEMP%, %APPDATA%, ProgramData, and other locations
For authorized pentesting and security research
"""

import os
import tempfile
import shutil
import json
import base64
import hashlib
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import random
import string
from abc import ABC, abstractmethod


class FileFormat(Enum):
    """Supported file formats for payload output"""
    VBS = "vbs"
    BAT = "bat"
    PS1 = "ps1"
    TEXT = "txt"
    BINARY = "bin"
    JSON = "json"
    ENCODED = "enc"


@dataclass
class PayloadMetadata:
    """Metadata associated with a written payload"""
    file_id: str
    original_size: int
    encoded_size: int
    encoding_type: str
    obfuscation_level: str
    timestamp: str
    format: str
    temp_path: str
    sha256_hash: str
    checksum: str
    location_type: str  # TEMP, APPDATA, ProgramData, etc.
    compression_ratio: float = 0.0


class BaseFileWriter(ABC):
    """Abstract base class for file writers"""

    def __init__(self, enable_obfuscation: bool = True):
        """Initialize base file writer"""
        self.enable_obfuscation = enable_obfuscation
        self.metadata_store: Dict[str, PayloadMetadata] = {}

    @abstractmethod
    def get_base_directory(self) -> Path:
        """Get the base directory for this writer variant"""
        pass

    @abstractmethod
    def get_location_type(self) -> str:
        """Get the location type identifier"""
        pass

    def create_temp_file(self,
                        suffix: str = ".vbs",
                        prefix: str = "payload_") -> str:
        """
        Create temporary file for payload

        Args:
            suffix: File extension (e.g., ".vbs", ".bat")
            prefix: File name prefix

        Returns:
            Path to temporary file
        """
        base_dir = self.get_base_directory()
        base_dir.mkdir(parents=True, exist_ok=True)

        fd, temp_path = tempfile.mkstemp(
            suffix=suffix,
            prefix=prefix,
            dir=str(base_dir)
        )
        os.close(fd)
        return temp_path

    def write_payload(self,
                     payload: str,
                     file_format: FileFormat = FileFormat.VBS,
                     obfuscation_level: str = "high",
                     encoding_type: str = "base64") -> Tuple[str, PayloadMetadata]:
        """
        Write payload to disk with obfuscation

        Args:
            payload: Payload content to write
            file_format: Output file format
            obfuscation_level: Level of obfuscation
            encoding_type: Encoding method

        Returns:
            Tuple of (file_path, metadata)
        """
        suffix = f".{file_format.value}"
        temp_path = self.create_temp_file(suffix=suffix)

        # Simple obfuscation (can be extended)
        obfuscated_payload = payload
        if self.enable_obfuscation:
            obfuscated_payload = self._apply_simple_obfuscation(payload)

        # Calculate checksums
        original_hash = hashlib.sha256(payload.encode()).hexdigest()

        # Write to file
        try:
            if file_format == FileFormat.BINARY:
                with open(temp_path, 'wb') as f:
                    f.write(obfuscated_payload.encode())
            else:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(obfuscated_payload)
        except IOError as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise IOError(f"Failed to write payload to {temp_path}: {e}")

        # Calculate file hash
        file_hash = self._calculate_file_hash(temp_path, file_format)

        # Generate file ID
        file_id = self._generate_file_id()

        # Create metadata
        metadata = PayloadMetadata(
            file_id=file_id,
            original_size=len(payload),
            encoded_size=len(obfuscated_payload),
            encoding_type=encoding_type,
            obfuscation_level=obfuscation_level,
            timestamp=datetime.now().isoformat(),
            format=file_format.value,
            temp_path=temp_path,
            sha256_hash=original_hash,
            checksum=file_hash,
            location_type=self.get_location_type(),
            compression_ratio=len(obfuscated_payload) / len(payload) if payload else 0.0
        )

        self.metadata_store[file_id] = metadata
        return temp_path, metadata

    def get_payload_info(self, file_id: str) -> Optional[PayloadMetadata]:
        """Get metadata for a payload"""
        return self.metadata_store.get(file_id)

    def cleanup_temp_file(self, file_id: str) -> bool:
        """Clean up temporary file"""
        if file_id not in self.metadata_store:
            return False

        try:
            temp_path = self.metadata_store[file_id].temp_path
            if os.path.exists(temp_path):
                os.remove(temp_path)
            del self.metadata_store[file_id]
            return True
        except Exception as e:
            print(f"Error cleaning up {file_id}: {e}")
            return False

    def cleanup_all(self) -> int:
        """Clean up all temporary files"""
        count = 0
        for file_id in list(self.metadata_store.keys()):
            if self.cleanup_temp_file(file_id):
                count += 1
        return count

    # Private helper methods

    def _apply_simple_obfuscation(self, payload: str) -> str:
        """Apply simple obfuscation"""
        # Can be overridden in subclasses
        return payload

    def _calculate_file_hash(self, file_path: str, file_format: FileFormat) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        try:
            if file_format == FileFormat.BINARY:
                with open(file_path, 'rb') as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        sha256_hash.update(line.encode())
        except Exception:
            pass
        return sha256_hash.hexdigest()

    def _generate_file_id(self) -> str:
        """Generate unique file ID"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))


class TempFileWriter(BaseFileWriter):
    r"""
    File writer using Windows %TEMP% directory
    Typically: C:\Users\<username>\AppData\Local\Temp
    """

    def get_base_directory(self) -> Path:
        r"""Get TEMP directory"""
        # On Windows: typically C:\Users\<username>\AppData\Local\Temp
        # On Linux/Mac: /tmp
        temp_dir = Path(tempfile.gettempdir())
        payload_dir = temp_dir / "sc-payloads"
        return payload_dir

    def get_location_type(self) -> str:
        """Return location type identifier"""
        return "%TEMP%"

    def _apply_simple_obfuscation(self, payload: str) -> str:
        """Apply VBS-specific obfuscation for TEMP location"""
        if payload.startswith("'") or "Script" in payload:
            # Add anti-debugging for VBS
            return f"On Error Resume Next\n{payload}"
        return payload


class AppDataFileWriter(BaseFileWriter):
    r"""
    File writer using Windows %APPDATA% directory
    Typically: C:\Users\<username>\AppData\Roaming
    """

    def __init__(self, enable_obfuscation: bool = True, app_name: str = "PayloadApp"):
        """
        Initialize AppData file writer

        Args:
            enable_obfuscation: Apply obfuscation
            app_name: Application name for subdirectory
        """
        super().__init__(enable_obfuscation)
        self.app_name = app_name

    def get_base_directory(self) -> Path:
        r"""Get APPDATA directory"""
        # On Windows: C:\Users\<username>\AppData\Roaming\<app_name>
        # Simulate by using a local directory
        appdata_dir = Path.home() / ".appdata-sim" / self.app_name
        return appdata_dir

    def get_location_type(self) -> str:
        r"""Return location type identifier"""
        return f"%APPDATA%\\{self.app_name}"

    def _apply_simple_obfuscation(self, payload: str) -> str:
        """Apply obfuscation appropriate for APPDATA persistence"""
        # APPDATA is often used for persistence - add registry access
        if payload.startswith("'") or "Script" in payload:
            return f"' Persistence mechanism\nOn Error Resume Next\n{payload}"
        return payload


class ProgramDataFileWriter(BaseFileWriter):
    r"""
    File writer using Windows ProgramData directory
    Typically: C:\ProgramData
    """

    def __init__(self, enable_obfuscation: bool = True, vendor_name: str = "VendorName"):
        """
        Initialize ProgramData file writer

        Args:
            enable_obfuscation: Apply obfuscation
            vendor_name: Vendor/program name for subdirectory
        """
        super().__init__(enable_obfuscation)
        self.vendor_name = vendor_name

    def get_base_directory(self) -> Path:
        r"""Get ProgramData directory"""
        # On Windows: C:\ProgramData\<vendor_name>
        # Simulate by using a local directory
        progdata_dir = Path.home() / ".programdata-sim" / self.vendor_name
        return progdata_dir

    def get_location_type(self) -> str:
        r"""Return location type identifier"""
        return f"ProgramData\\{self.vendor_name}"

    def _apply_simple_obfuscation(self, payload: str) -> str:
        """Apply obfuscation for system-wide payload location"""
        # ProgramData is system-wide and may require elevated privileges
        if payload.startswith("'") or "Script" in payload:
            return f"' System payload - elevated execution required\n{payload}"
        return payload


class LocalAppDataFileWriter(BaseFileWriter):
    r"""
    File writer using Windows %LOCALAPPDATA% directory
    Typically: C:\Users\<username>\AppData\Local
    """

    def __init__(self, enable_obfuscation: bool = True, app_name: str = "LocalApp"):
        """
        Initialize LocalAppData file writer

        Args:
            enable_obfuscation: Apply obfuscation
            app_name: Application name for subdirectory
        """
        super().__init__(enable_obfuscation)
        self.app_name = app_name

    def get_base_directory(self) -> Path:
        r"""Get LOCALAPPDATA directory"""
        # On Windows: C:\Users\<username>\AppData\Local\<app_name>
        # Simulate by using a local directory
        local_appdata = Path.home() / ".localappdata-sim" / self.app_name
        return local_appdata

    def get_location_type(self) -> str:
        r"""Return location type identifier"""
        return f"%LOCALAPPDATA%\\{self.app_name}"

    def _apply_simple_obfuscation(self, payload: str) -> str:
        """Apply obfuscation for local user data"""
        if payload.startswith("'") or "Script" in payload:
            return f"' Local user cache\n{payload}"
        return payload


class UserProfileFileWriter(BaseFileWriter):
    r"""
    File writer using Windows %USERPROFILE% directory
    Typically: C:\Users\<username>
    """

    def __init__(self, enable_obfuscation: bool = True, subdir: str = ".config"):
        """
        Initialize UserProfile file writer

        Args:
            enable_obfuscation: Apply obfuscation
            subdir: Subdirectory within user profile (starts with . for hidden)
        """
        super().__init__(enable_obfuscation)
        self.subdir = subdir

    def get_base_directory(self) -> Path:
        r"""Get USERPROFILE directory"""
        # On Windows: C:\Users\<username>\<subdir>
        userprofile = Path.home() / self.subdir
        return userprofile

    def get_location_type(self) -> str:
        r"""Return location type identifier"""
        return f"%USERPROFILE%\\{self.subdir}"

    def _apply_simple_obfuscation(self, payload: str) -> str:
        """Apply obfuscation for user profile location"""
        if payload.startswith("'") or "Script" in payload:
            return f"' Hidden in user profile\n{payload}"
        return payload


class WindowsSystemFileWriter(BaseFileWriter):
    r"""
    File writer using Windows System directories
    Typically: C:\Windows\Temp or C:\Windows\System32
    """

    def __init__(self, enable_obfuscation: bool = True, target_dir: str = "Temp"):
        """
        Initialize Windows System file writer

        Args:
            enable_obfuscation: Apply obfuscation
            target_dir: Target subdirectory (Temp, System32, etc.)
        """
        super().__init__(enable_obfuscation)
        self.target_dir = target_dir

    def get_base_directory(self) -> Path:
        r"""Get Windows System directory"""
        # On Windows: C:\Windows\<target_dir>
        # Simulate by using a local directory
        windows_sim = Path.home() / ".windows-sim" / self.target_dir
        return windows_sim

    def get_location_type(self) -> str:
        r"""Return location type identifier"""
        return f"C:\\Windows\\{self.target_dir}"

    def _apply_simple_obfuscation(self, payload: str) -> str:
        """Apply obfuscation for system directory"""
        if payload.startswith("'") or "Script" in payload:
            return f"' System directory payload - requires elevation\n{payload}"
        return payload


class RecycleBinFileWriter(BaseFileWriter):
    r"""
    File writer using Windows Recycle Bin directory
    Typically: C:\$Recycle.Bin (hidden)
    """

    def get_base_directory(self) -> Path:
        r"""Get Recycle Bin simulation directory"""
        recycle_bin = Path.home() / ".recycle-bin-sim"
        return recycle_bin

    def get_location_type(self) -> str:
        r"""Return location type identifier"""
        return r"C:\$Recycle.Bin"

    def _apply_simple_obfuscation(self, payload: str) -> str:
        """Apply obfuscation for hidden location"""
        if payload.startswith("'") or "Script" in payload:
            return f"' Hidden in Recycle Bin\nOn Error Resume Next\n{payload}"
        return payload


class PublicFileWriter(BaseFileWriter):
    r"""
    File writer using Windows Public directory
    Typically: C:\Users\Public
    """

    def __init__(self, enable_obfuscation: bool = True, subdir: str = "Shared"):
        """
        Initialize Public directory file writer

        Args:
            enable_obfuscation: Apply obfuscation
            subdir: Subdirectory within Public
        """
        super().__init__(enable_obfuscation)
        self.subdir = subdir

    def get_base_directory(self) -> Path:
        r"""Get Public directory"""
        # On Windows: C:\Users\Public\<subdir>
        # Simulate by using a local directory
        public_dir = Path.home() / ".public-sim" / self.subdir
        return public_dir

    def get_location_type(self) -> str:
        r"""Return location type identifier"""
        return f"C:\\Users\\Public\\{self.subdir}"

    def _apply_simple_obfuscation(self, payload: str) -> str:
        """Apply obfuscation for shared location"""
        return payload


class DownloadsFileWriter(BaseFileWriter):
    r"""
    File writer using Windows Downloads directory
    Typically: C:\Users\<username>\Downloads
    """

    def get_base_directory(self) -> Path:
        """Get Downloads directory"""
        # Try to find actual Downloads folder
        downloads = Path.home() / "Downloads"
        if not downloads.exists():
            downloads = Path.home() / ".downloads-sim"
        return downloads

    def get_location_type(self) -> str:
        r"""Return location type identifier"""
        return r"%USERPROFILE%\Downloads"

    def _apply_simple_obfuscation(self, payload: str) -> str:
        """Apply obfuscation for downloads location"""
        return payload


class CustomPathFileWriter(BaseFileWriter):
    """
    File writer using a custom path
    """

    def __init__(self, custom_path: str, enable_obfuscation: bool = True):
        """
        Initialize with custom path

        Args:
            custom_path: Custom directory path
            enable_obfuscation: Apply obfuscation
        """
        super().__init__(enable_obfuscation)
        self.custom_path = custom_path

    def get_base_directory(self) -> Path:
        """Get custom directory"""
        return Path(self.custom_path)

    def get_location_type(self) -> str:
        """Return location type identifier"""
        return self.custom_path


class FileWriterFactory:
    """Factory for creating file writer variants"""

    VARIANTS = {
        "temp": TempFileWriter,
        "appdata": AppDataFileWriter,
        "programdata": ProgramDataFileWriter,
        "localappdata": LocalAppDataFileWriter,
        "userprofile": UserProfileFileWriter,
        "system": WindowsSystemFileWriter,
        "recyclebin": RecycleBinFileWriter,
        "public": PublicFileWriter,
        "downloads": DownloadsFileWriter,
    }

    @classmethod
    def create(cls, variant: str, **kwargs) -> Optional[BaseFileWriter]:
        """
        Create a file writer variant

        Args:
            variant: Variant name (temp, appdata, programdata, etc.)
            **kwargs: Additional arguments for the variant

        Returns:
            File writer instance or None if variant not found
        """
        writer_class = cls.VARIANTS.get(variant.lower())
        if not writer_class:
            return None
        return writer_class(**kwargs)

    @classmethod
    def create_all(cls, enable_obfuscation: bool = True) -> Dict[str, BaseFileWriter]:
        """
        Create all file writer variants

        Args:
            enable_obfuscation: Enable obfuscation for all variants

        Returns:
            Dictionary of variant_name -> writer_instance
        """
        writers = {}
        writers["temp"] = TempFileWriter(enable_obfuscation)
        writers["appdata"] = AppDataFileWriter(enable_obfuscation)
        writers["programdata"] = ProgramDataFileWriter(enable_obfuscation)
        writers["localappdata"] = LocalAppDataFileWriter(enable_obfuscation)
        writers["userprofile"] = UserProfileFileWriter(enable_obfuscation)
        writers["system"] = WindowsSystemFileWriter(enable_obfuscation)
        writers["recyclebin"] = RecycleBinFileWriter(enable_obfuscation)
        writers["public"] = PublicFileWriter(enable_obfuscation)
        writers["downloads"] = DownloadsFileWriter(enable_obfuscation)
        return writers

    @classmethod
    def get_available_variants(cls) -> List[str]:
        """Get list of available variants"""
        return list(cls.VARIANTS.keys())


class MultiLocationPayloadWriter:
    """
    Write the same payload to multiple locations simultaneously
    """

    def __init__(self, variants: Optional[List[str]] = None):
        """
        Initialize multi-location writer

        Args:
            variants: List of variants to use, or None for all
        """
        if variants is None:
            self.writers = FileWriterFactory.create_all()
        else:
            self.writers = {}
            for variant in variants:
                writer = FileWriterFactory.create(variant)
                if writer:
                    self.writers[variant] = writer

    def write_to_all_locations(self,
                              payload: str,
                              file_format: FileFormat = FileFormat.VBS,
                              obfuscation_level: str = "high") -> Dict[str, Tuple[str, PayloadMetadata]]:
        """
        Write payload to all configured locations

        Args:
            payload: Payload content
            file_format: Output file format
            obfuscation_level: Obfuscation level

        Returns:
            Dictionary of variant -> (path, metadata) tuples
        """
        results = {}
        for variant_name, writer in self.writers.items():
            try:
                path, metadata = writer.write_payload(
                    payload,
                    file_format=file_format,
                    obfuscation_level=obfuscation_level
                )
                results[variant_name] = (path, metadata)
            except Exception as e:
                print(f"Error writing to {variant_name}: {e}")
                results[variant_name] = (None, None)

        return results

    def cleanup_all_locations(self) -> Dict[str, int]:
        """
        Clean up all temporary files from all locations

        Returns:
            Dictionary of variant -> number of files cleaned
        """
        results = {}
        for variant_name, writer in self.writers.items():
            results[variant_name] = writer.cleanup_all()
        return results

    def get_summary(self, results: Dict[str, Tuple[str, PayloadMetadata]]) -> Dict[str, any]:
        """
        Get summary of written payloads

        Args:
            results: Results from write_to_all_locations

        Returns:
            Summary dictionary
        """
        summary = {
            "total_locations": len(results),
            "successful_writes": 0,
            "locations": {}
        }

        for variant, (path, metadata) in results.items():
            if path and metadata:
                summary["successful_writes"] += 1
                summary["locations"][variant] = {
                    "path": path,
                    "location_type": metadata.location_type,
                    "file_id": metadata.file_id,
                    "size": metadata.encoded_size,
                    "format": metadata.format
                }
            else:
                summary["locations"][variant] = {"status": "failed"}

        return summary


if __name__ == "__main__":
    print("=== Payload File Writer Variants ===\n")

    # Example 1: Create individual variants
    print("Example 1: Create individual writer variants")
    print("-" * 50)

    temp_writer = FileWriterFactory.create("temp")
    appdata_writer = FileWriterFactory.create("appdata", app_name="TestApp")
    programdata_writer = FileWriterFactory.create("programdata", vendor_name="TestVendor")

    test_payload = 'Set objShell = CreateObject("WScript.Shell")\nobjShell.Run "calc.exe"'

    print(f"\nTEMP Writer: {temp_writer.get_location_type()}")
    temp_path, temp_meta = temp_writer.write_payload(test_payload, FileFormat.VBS, "high")
    print(f"  Path: {temp_path}")
    print(f"  File ID: {temp_meta.file_id}")
    print(f"  Location: {temp_meta.location_type}")

    print(f"\nAPPDATA Writer: {appdata_writer.get_location_type()}")
    appdata_path, appdata_meta = appdata_writer.write_payload(test_payload, FileFormat.VBS, "high")
    print(f"  Path: {appdata_path}")
    print(f"  File ID: {appdata_meta.file_id}")
    print(f"  Location: {appdata_meta.location_type}")

    print(f"\nProgramData Writer: {programdata_writer.get_location_type()}")
    progdata_path, progdata_meta = programdata_writer.write_payload(test_payload, FileFormat.VBS, "high")
    print(f"  Path: {progdata_path}")
    print(f"  File ID: {progdata_meta.file_id}")
    print(f"  Location: {progdata_meta.location_type}")

    # Example 2: Use factory to list all variants
    print("\n\nExample 2: Available writer variants")
    print("-" * 50)
    print("Available variants:")
    for variant in FileWriterFactory.get_available_variants():
        print(f"  - {variant}")

    # Example 3: Create all variants at once
    print("\n\nExample 3: Create all variants")
    print("-" * 50)
    all_writers = FileWriterFactory.create_all()
    print(f"Created {len(all_writers)} writer variants:")
    for variant_name, writer in all_writers.items():
        print(f"  - {variant_name}: {writer.get_location_type()}")

    # Example 4: Multi-location payload writing
    print("\n\nExample 4: Write payload to multiple locations")
    print("-" * 50)
    multi_writer = MultiLocationPayloadWriter(
        variants=["temp", "appdata", "localappdata", "userprofile"]
    )

    test_payload_multi = 'echo "Multi-location payload test"'
    results = multi_writer.write_to_all_locations(test_payload_multi, FileFormat.BAT, "high")

    summary = multi_writer.get_summary(results)
    print(f"\nSuccessfully wrote to {summary['successful_writes']}/{summary['total_locations']} locations")
    print("\nPayload locations:")
    for variant, info in summary["locations"].items():
        if "path" in info:
            print(f"  {variant}: {info['location_type']}")
            print(f"    Path: {info['path']}")
            print(f"    Size: {info['size']} bytes")
        else:
            print(f"  {variant}: {info['status']}")

    # Cleanup
    print("\n\nCleaning up temporary files...")
    cleanup_summary = multi_writer.cleanup_all_locations()
    total_cleaned = sum(cleanup_summary.values())
    print(f"Cleaned up {total_cleaned} temporary files")
    for variant, count in cleanup_summary.items():
        if count > 0:
            print(f"  {variant}: {count} files")
