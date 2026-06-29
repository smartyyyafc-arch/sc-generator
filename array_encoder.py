#!/usr/bin/env python3
"""
Array Encoder: Chunks commands into hex arrays
Reverse of the Array Decoder patterns
Supports multiple output formats and chunking strategies

For authorized pentesting and security research
"""

import binascii
import base64
import string
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class EncodingType(Enum):
    """Encoding types for array elements"""
    HEX = "hex"
    BASE64 = "base64"
    MIXED = "mixed"
    OCTAL = "octal"


class OutputFormat(Enum):
    """Output formats for encoded arrays"""
    PYTHON = "python"      # Python list format
    VBS = "vbs"           # VBScript array format
    JAVASCRIPT = "js"     # JavaScript array format
    POWERSHELL = "ps"     # PowerShell array format
    BASH = "bash"         # Bash array format
    JSON = "json"         # JSON format
    C = "c"               # C/C++ array format


class ChunkingStrategy(Enum):
    """Chunking strategies"""
    SEQUENTIAL = "sequential"           # Standard sequential chunks
    RANDOM_ORDER = "random_order"       # Randomize chunk order
    VARIABLE_SIZE = "variable_size"     # Random chunk sizes
    INTERLEAVED = "interleaved"         # Interleave chunks
    NESTED = "nested"                   # Create nested arrays


@dataclass
class EncoderConfig:
    """Configuration for array encoder"""
    chunk_size: int = 16
    encoding_type: EncodingType = EncodingType.HEX
    output_format: OutputFormat = OutputFormat.PYTHON
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.SEQUENTIAL
    variable_name: str = "payload"
    randomize_names: bool = False
    add_comments: bool = True
    preserve_order: bool = True  # Only applicable if chunking_strategy != RANDOM_ORDER
    min_chunk_size: int = 8      # For VARIABLE_SIZE strategy
    max_chunk_size: int = 32     # For VARIABLE_SIZE strategy


class ArrayEncoder:
    """Encodes commands/data into chunked hex arrays"""

    def __init__(self, config: EncoderConfig = None):
        self.config = config or EncoderConfig()
        self.var_counter = 0
        self.chunk_order = []
        self.chunks = []

    def _gen_var(self, prefix: str = "v") -> str:
        """Generate unique sequential variable name"""
        self.var_counter += 1
        return f"{prefix}_{self.var_counter}"

    def _gen_random_var(self, prefix: str = "v", length: int = 6) -> str:
        """Generate random-looking variable name"""
        chars = string.ascii_uppercase + string.ascii_lowercase
        return prefix + "".join(random.choices(chars, k=length))

    def _encode_to_hex(self, data: str) -> str:
        """Encode string to hex"""
        return binascii.hexlify(data.encode()).decode()

    def _encode_to_base64(self, data: str) -> str:
        """Encode string to base64"""
        return base64.b64encode(data.encode()).decode()

    def _encode_to_octal(self, data: str) -> str:
        """Encode string to octal representation"""
        hex_str = binascii.hexlify(data.encode()).decode()
        octal_parts = []
        for i in range(0, len(hex_str), 2):
            byte_val = int(hex_str[i:i+2], 16)
            octal_parts.append(oct(byte_val)[2:].zfill(3))
        return "".join(octal_parts)

    def _encode_chunk(self, chunk: str) -> str:
        """Encode a single chunk based on encoding type"""
        if self.config.encoding_type == EncodingType.HEX:
            return self._encode_to_hex(chunk)
        elif self.config.encoding_type == EncodingType.BASE64:
            return self._encode_to_base64(chunk)
        elif self.config.encoding_type == EncodingType.OCTAL:
            return self._encode_to_octal(chunk)
        elif self.config.encoding_type == EncodingType.MIXED:
            # Randomly choose encoding per chunk
            choice = random.choice([EncodingType.HEX, EncodingType.BASE64])
            if choice == EncodingType.HEX:
                return self._encode_to_hex(chunk)
            else:
                return self._encode_to_base64(chunk)
        else:
            return self._encode_to_hex(chunk)

    def _chunk_sequential(self, data: str) -> List[str]:
        """Create sequential chunks"""
        chunks = []
        for i in range(0, len(data), self.config.chunk_size):
            chunk = data[i:i + self.config.chunk_size]
            chunks.append(self._encode_chunk(chunk))
        return chunks

    def _chunk_variable_size(self, data: str) -> List[str]:
        """Create variable-sized chunks"""
        chunks = []
        pos = 0
        while pos < len(data):
            size = random.randint(self.config.min_chunk_size, self.config.max_chunk_size)
            chunk = data[pos:pos + size]
            chunks.append(self._encode_chunk(chunk))
            pos += size
        return chunks

    def _chunk_random_order(self, data: str) -> Tuple[List[str], List[int]]:
        """Create chunks with randomized order"""
        # First create sequential chunks
        chunks = self._chunk_sequential(data)
        original_indices = list(range(len(chunks)))

        if self.config.preserve_order:
            self.chunk_order = original_indices
            return chunks, original_indices

        # Randomize order
        shuffled_indices = original_indices.copy()
        random.shuffle(shuffled_indices)
        self.chunk_order = shuffled_indices

        # Return chunks in original order but store shuffle order
        return chunks, shuffled_indices

    def _chunk_interleaved(self, data: str) -> List[str]:
        """Create interleaved chunks (even then odd indices)"""
        # First create sequential chunks
        sequential = self._chunk_sequential(data)

        # Interleave: even indices, then odd indices
        interleaved = []
        for i in range(0, len(sequential), 2):
            interleaved.append(sequential[i])
        for i in range(1, len(sequential), 2):
            interleaved.append(sequential[i])

        return interleaved

    def _chunk_nested(self, data: str) -> List[List[str]]:
        """Create nested array structure"""
        sequential = self._chunk_sequential(data)
        # Group chunks into sub-arrays (e.g., 4 chunks per group)
        group_size = max(2, len(sequential) // 4)
        nested = []
        for i in range(0, len(sequential), group_size):
            nested.append(sequential[i:i + group_size])
        return nested

    def encode(self, data: str) -> Dict:
        """
        Encode data into chunks
        Returns dictionary with chunks and metadata
        """
        if self.config.chunking_strategy == ChunkingStrategy.SEQUENTIAL:
            chunks = self._chunk_sequential(data)
            return {
                "chunks": chunks,
                "count": len(chunks),
                "strategy": "sequential",
                "order": list(range(len(chunks)))
            }

        elif self.config.chunking_strategy == ChunkingStrategy.RANDOM_ORDER:
            chunks, order = self._chunk_random_order(data)
            return {
                "chunks": chunks,
                "count": len(chunks),
                "strategy": "random_order",
                "order": order
            }

        elif self.config.chunking_strategy == ChunkingStrategy.VARIABLE_SIZE:
            chunks = self._chunk_variable_size(data)
            return {
                "chunks": chunks,
                "count": len(chunks),
                "strategy": "variable_size",
                "order": list(range(len(chunks)))
            }

        elif self.config.chunking_strategy == ChunkingStrategy.INTERLEAVED:
            chunks = self._chunk_interleaved(data)
            return {
                "chunks": chunks,
                "count": len(chunks),
                "strategy": "interleaved",
                "order": list(range(len(chunks)))
            }

        elif self.config.chunking_strategy == ChunkingStrategy.NESTED:
            chunks = self._chunk_nested(data)
            return {
                "chunks": chunks,
                "count": len(chunks),
                "strategy": "nested",
                "order": list(range(len(chunks)))
            }

        else:
            chunks = self._chunk_sequential(data)
            return {
                "chunks": chunks,
                "count": len(chunks),
                "strategy": "sequential",
                "order": list(range(len(chunks)))
            }

    def to_python_list(self, chunks: List[str]) -> str:
        """Convert chunks to Python list format"""
        var_name = self._gen_random_var(self.config.variable_name) if self.config.randomize_names else self.config.variable_name

        list_items = [f'    "{chunk}"' for chunk in chunks]
        code = f"{var_name} = [\n"
        code += ",\n".join(list_items)
        code += "\n]\n"

        if self.config.add_comments:
            code = f"# Array encoder: {len(chunks)} chunks of {self.config.encoding_type.value}\n" + code

        return code

    def to_vbs_array(self, chunks: List[str]) -> str:
        """Convert chunks to VBScript array format"""
        var_name = self._gen_random_var(self.config.variable_name) if self.config.randomize_names else self.config.variable_name

        code = f"Dim {var_name}({len(chunks)-1})\n"

        if self.config.add_comments:
            code = f"' Array encoder: {len(chunks)} chunks of {self.config.encoding_type.value}\n" + code

        for i, chunk in enumerate(chunks):
            code += f'{var_name}({i}) = "{chunk}"\n'

        return code

    def to_javascript_array(self, chunks: List[str]) -> str:
        """Convert chunks to JavaScript array format"""
        var_name = self._gen_random_var(self.config.variable_name) if self.config.randomize_names else self.config.variable_name

        list_items = [f'    "{chunk}"' for chunk in chunks]
        code = f"const {var_name} = [\n"
        code += ",\n".join(list_items)
        code += "\n];\n"

        if self.config.add_comments:
            code = f"// Array encoder: {len(chunks)} chunks of {self.config.encoding_type.value}\n" + code

        return code

    def to_powershell_array(self, chunks: List[str]) -> str:
        """Convert chunks to PowerShell array format"""
        var_name = self._gen_random_var(self.config.variable_name) if self.config.randomize_names else self.config.variable_name

        list_items = [f'    "{chunk}"' for chunk in chunks]
        code = f"${var_name} = @(\n"
        code += ",\n".join(list_items)
        code += "\n)\n"

        if self.config.add_comments:
            code = f"# Array encoder: {len(chunks)} chunks of {self.config.encoding_type.value}\n" + code

        return code

    def to_bash_array(self, chunks: List[str]) -> str:
        """Convert chunks to Bash array format"""
        var_name = self._gen_random_var(self.config.variable_name) if self.config.randomize_names else self.config.variable_name

        code = f"{var_name}=(\n"
        for chunk in chunks:
            code += f'    "{chunk}"\n'
        code += ")\n"

        if self.config.add_comments:
            code = f"# Array encoder: {len(chunks)} chunks of {self.config.encoding_type.value}\n" + code

        return code

    def to_json(self, chunks: List[str]) -> str:
        """Convert chunks to JSON format"""
        import json

        data = {
            "payload": chunks,
            "count": len(chunks),
            "encoding": self.config.encoding_type.value,
            "chunk_size": self.config.chunk_size
        }

        return json.dumps(data, indent=2)

    def to_c_array(self, chunks: List[str]) -> str:
        """Convert chunks to C/C++ array format"""
        var_name = self._gen_random_var(self.config.variable_name) if self.config.randomize_names else self.config.variable_name

        code = f"const char* {var_name}[] = {{\n"

        for i, chunk in enumerate(chunks):
            code += f'    "{chunk}"'
            if i < len(chunks) - 1:
                code += ","
            code += "\n"

        code += "};\n"
        code += f"int {var_name}_len = {len(chunks)};\n"

        if self.config.add_comments:
            code = f"// Array encoder: {len(chunks)} chunks of {self.config.encoding_type.value}\n" + code

        return code

    def generate(self, data: str) -> str:
        """
        Encode data and generate output in specified format

        Args:
            data: Input command/data string

        Returns:
            Encoded array in specified output format
        """
        # Encode data into chunks
        encoded = self.encode(data)
        chunks = encoded["chunks"]

        # Convert to specified output format
        if self.config.output_format == OutputFormat.PYTHON:
            return self.to_python_list(chunks)

        elif self.config.output_format == OutputFormat.VBS:
            return self.to_vbs_array(chunks)

        elif self.config.output_format == OutputFormat.JAVASCRIPT:
            return self.to_javascript_array(chunks)

        elif self.config.output_format == OutputFormat.POWERSHELL:
            return self.to_powershell_array(chunks)

        elif self.config.output_format == OutputFormat.BASH:
            return self.to_bash_array(chunks)

        elif self.config.output_format == OutputFormat.JSON:
            return self.to_json(chunks)

        elif self.config.output_format == OutputFormat.C:
            return self.to_c_array(chunks)

        else:
            return self.to_python_list(chunks)


# Convenience functions
def encode_command_to_array(
    command: str,
    chunk_size: int = 16,
    encoding: str = "hex",
    output_format: str = "python",
    variable_name: str = "payload"
) -> str:
    """
    Convenience function to encode command to array

    Args:
        command: Command/data to encode
        chunk_size: Size of each chunk
        encoding: Encoding type ('hex', 'base64', 'mixed', 'octal')
        output_format: Output format ('python', 'vbs', 'js', 'ps', 'bash', 'json', 'c')
        variable_name: Name of output variable

    Returns:
        Encoded array as string

    Example:
        >>> code = encode_command_to_array("calc.exe", chunk_size=8, encoding="hex", output_format="vbs")
        >>> print(code)
    """
    try:
        enc_type = EncodingType[encoding.upper()]
    except KeyError:
        enc_type = EncodingType.HEX

    try:
        out_fmt = OutputFormat[output_format.upper()]
    except KeyError:
        out_fmt = OutputFormat.PYTHON

    config = EncoderConfig(
        chunk_size=chunk_size,
        encoding_type=enc_type,
        output_format=out_fmt,
        variable_name=variable_name,
        randomize_names=False
    )

    encoder = ArrayEncoder(config)
    return encoder.generate(command)


if __name__ == "__main__":
    # Example 1: Simple command with hex encoding to VBS
    print("=" * 60)
    print("Example 1: Hex encoding to VBScript")
    print("=" * 60)
    cmd1 = "calc.exe"
    config1 = EncoderConfig(
        chunk_size=8,
        encoding_type=EncodingType.HEX,
        output_format=OutputFormat.VBS,
        variable_name="cmd"
    )
    encoder1 = ArrayEncoder(config1)
    result1 = encoder1.generate(cmd1)
    print(result1)
    print()

    # Example 2: Longer command with base64 encoding to Python
    print("=" * 60)
    print("Example 2: Base64 encoding to Python")
    print("=" * 60)
    cmd2 = "powershell.exe -Command \"Write-Host 'Hello World'\""
    config2 = EncoderConfig(
        chunk_size=16,
        encoding_type=EncodingType.BASE64,
        output_format=OutputFormat.PYTHON,
        variable_name="encoded_command"
    )
    encoder2 = ArrayEncoder(config2)
    result2 = encoder2.generate(cmd2)
    print(result2)
    print()

    # Example 3: Command with variable-sized chunks
    print("=" * 60)
    print("Example 3: Variable-sized chunks to JSON")
    print("=" * 60)
    cmd3 = "cmd.exe /c ipconfig"
    config3 = EncoderConfig(
        chunk_size=16,
        encoding_type=EncodingType.HEX,
        output_format=OutputFormat.JSON,
        chunking_strategy=ChunkingStrategy.VARIABLE_SIZE,
        min_chunk_size=4,
        max_chunk_size=12
    )
    encoder3 = ArrayEncoder(config3)
    result3 = encoder3.generate(cmd3)
    print(result3)
    print()

    # Example 4: Using convenience function
    print("=" * 60)
    print("Example 4: Using convenience function")
    print("=" * 60)
    result4 = encode_command_to_array(
        "notepad.exe",
        chunk_size=6,
        encoding="hex",
        output_format="javascript",
        variable_name="payload"
    )
    print(result4)
