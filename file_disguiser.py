#!/usr/bin/env python3
"""
File Disguiser - Hide file content by disguising file type with legitimate extensions.
Allows writing files with deceptive extensions (txt, doc, pdf, etc.) while preserving
the actual content.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Literal
from enum import Enum


class DisguiseType(Enum):
    """Supported disguise file types."""
    TXT = "txt"
    DOC = "doc"
    DOCX = "docx"
    PDF = "pdf"
    XLS = "xls"
    XLSX = "xlsx"
    PPT = "ppt"
    PPTX = "pptx"
    CSV = "csv"
    JSON = "json"
    LOG = "log"
    DAT = "dat"
    BIN = "bin"


class FileDisguiser:
    """
    A file writer that disguises file content with legitimate-looking extensions.
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the file disguiser.

        Args:
            base_dir: Base directory for disguised files. Defaults to current directory.
        """
        self.base_dir = Path(base_dir or ".")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.file_map = {}  # Maps disguised path to actual content metadata

    def write_disguised(
        self,
        filename: str,
        content: bytes | str,
        disguise_as: DisguiseType | str = DisguiseType.TXT,
        encoding: str = "utf-8"
    ) -> Path:
        """
        Write content to a file with a disguised extension.

        Args:
            filename: Original filename (without extension)
            content: File content (str or bytes)
            disguise_as: Type to disguise as (TXT, DOC, PDF, etc.)
            encoding: Text encoding if content is string

        Returns:
            Path to the disguised file
        """
        # Convert string content to bytes if needed
        if isinstance(content, str):
            content_bytes = content.encode(encoding)
        else:
            content_bytes = content

        # Determine disguise extension
        if isinstance(disguise_as, DisguiseType):
            ext = disguise_as.value
        else:
            ext = str(disguise_as).lstrip(".")

        # Create disguised filename
        disguised_filename = f"{filename}.{ext}"
        disguised_path = self.base_dir / disguised_filename

        # Write the file
        with open(disguised_path, "wb") as f:
            f.write(content_bytes)

        # Track the mapping
        self.file_map[str(disguised_path)] = {
            "original_name": filename,
            "disguise_ext": ext,
            "size": len(content_bytes),
            "content_type": type(content).__name__
        }

        return disguised_path

    def write_disguised_text(
        self,
        filename: str,
        text_content: str,
        disguise_as: DisguiseType | str = DisguiseType.TXT,
        encoding: str = "utf-8"
    ) -> Path:
        """
        Write text content to a disguised file.

        Args:
            filename: Original filename
            text_content: Text to write
            disguise_as: Type to disguise as
            encoding: Text encoding

        Returns:
            Path to the disguised file
        """
        return self.write_disguised(filename, text_content, disguise_as, encoding)

    def write_disguised_binary(
        self,
        filename: str,
        binary_content: bytes,
        disguise_as: DisguiseType | str = DisguiseType.BIN
    ) -> Path:
        """
        Write binary content to a disguised file.

        Args:
            filename: Original filename
            binary_content: Binary data to write
            disguise_as: Type to disguise as

        Returns:
            Path to the disguised file
        """
        return self.write_disguised(filename, binary_content, disguise_as)

    def read_disguised(self, disguised_path: str | Path) -> bytes:
        """
        Read content from a disguised file.

        Args:
            disguised_path: Path to the disguised file

        Returns:
            Raw file content as bytes
        """
        with open(disguised_path, "rb") as f:
            return f.read()

    def get_file_info(self, disguised_path: str | Path) -> dict:
        """
        Get metadata about a disguised file.

        Args:
            disguised_path: Path to the disguised file

        Returns:
            Dictionary with file metadata
        """
        path_str = str(disguised_path)
        if path_str in self.file_map:
            return self.file_map[path_str].copy()
        return {}

    def undisguise(
        self,
        disguised_path: str | Path,
        output_path: Optional[str | Path] = None
    ) -> Path:
        """
        Extract and save disguised file content to original filename.

        Args:
            disguised_path: Path to the disguised file
            output_path: Optional output path (defaults to original name)

        Returns:
            Path to the extracted file
        """
        content = self.read_disguised(disguised_path)

        if output_path is None:
            path_str = str(disguised_path)
            if path_str in self.file_map:
                original_name = self.file_map[path_str]["original_name"]
                output_path = self.base_dir / original_name
            else:
                # Fallback: remove last extension
                output_path = Path(str(disguised_path).rsplit(".", 1)[0])

        output_path = Path(output_path)
        with open(output_path, "wb") as f:
            f.write(content)

        return output_path

    def list_disguised_files(self) -> list[dict]:
        """
        List all disguised files with their metadata.

        Returns:
            List of dictionaries with file information
        """
        return list(self.file_map.values())


# Example usage and convenience functions
def create_disguised_payload(
    data: str | bytes,
    filename: str = "payload",
    disguise_as: str = "txt",
    output_dir: str = "."
) -> Path:
    """
    Quick function to create a disguised file.

    Args:
        data: Content to hide
        filename: Base filename
        disguise_as: File type to disguise as
        output_dir: Output directory

    Returns:
        Path to created file
    """
    disguiser = FileDisguiser(output_dir)
    return disguiser.write_disguised(filename, data, disguise_as)


def extract_disguised_file(
    disguised_path: str | Path,
    output_path: Optional[str | Path] = None
) -> Path:
    """
    Quick function to extract a disguised file.

    Args:
        disguised_path: Path to disguised file
        output_path: Where to save extracted content

    Returns:
        Path to extracted file
    """
    disguiser = FileDisguiser()
    return disguiser.undisguise(disguised_path, output_path)


if __name__ == "__main__":
    # Demonstration
    print("=== File Disguiser Demo ===\n")

    disguiser = FileDisguiser("./disguised_files")

    # Example 1: Hide Python code as TXT
    python_code = """
def secret_function():
    print("This is hidden Python code!")
    return 42
"""
    txt_file = disguiser.write_disguised_text("script", python_code, DisguiseType.TXT)
    print(f"✓ Created: {txt_file}")
    print(f"  Content: {disguiser.read_disguised(txt_file)[:50].decode()}...\n")

    # Example 2: Hide binary data as PDF
    binary_data = b"\x89PNG\r\n\x1a\n" + b"fake binary content here"
    pdf_file = disguiser.write_disguised_binary("image", binary_data, DisguiseType.PDF)
    print(f"✓ Created: {pdf_file}")
    print(f"  Size: {len(disguiser.read_disguised(pdf_file))} bytes\n")

    # Example 3: Hide JSON as LOG
    json_config = '{"api_key": "secret_key_12345", "endpoint": "https://api.example.com"}'
    log_file = disguiser.write_disguised_text("config", json_config, DisguiseType.LOG)
    print(f"✓ Created: {log_file}")
    print(f"  Info: {disguiser.get_file_info(log_file)}\n")

    # Example 4: List all disguised files
    print("=== All Disguised Files ===")
    for file_info in disguiser.list_disguised_files():
        print(f"  - {file_info['original_name']}.{file_info['disguise_ext']} ({file_info['size']} bytes)")

    print("\n✓ Demo complete!")
