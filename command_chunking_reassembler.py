#!/usr/bin/env python3
"""
Command Chunking and Reassembly Engine
Splits long commands into manageable chunks for transmission and reassembles them
Supports multiple chunking strategies and metadata preservation
"""

import hashlib
import struct
import json
import zlib
import random
import string
from typing import Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod


class ChunkingStrategy(Enum):
    """Chunking strategies for command splitting"""
    FIXED_SIZE = "fixed_size"
    DELIMITER = "delimiter"
    ADAPTIVE = "adaptive"
    PAYLOAD_SAFE = "payload_safe"


@dataclass
class ChunkMetadata:
    """Metadata for a chunk"""
    chunk_id: int
    total_chunks: int
    command_hash: str
    chunk_size: int
    chunk_index: int
    original_length: int
    compressed: bool = False
    compression_ratio: float = 1.0
    encoding: str = "utf-8"
    checksum: str = ""
    timestamp: int = 0
    extra_data: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict) -> 'ChunkMetadata':
        """Create from dictionary"""
        extra = data.pop('extra_data', {})
        obj = ChunkMetadata(**data)
        obj.extra_data = extra
        return obj


@dataclass
class Chunk:
    """Represents a single chunk of command data"""
    data: str
    metadata: ChunkMetadata

    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            "data": self.data,
            "metadata": self.metadata.to_dict()
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Chunk':
        """Create from dictionary"""
        return Chunk(
            data=data["data"],
            metadata=ChunkMetadata.from_dict(data["metadata"])
        )


class ChunkingStrategy_ABC(ABC):
    """Abstract base for chunking strategies"""

    @abstractmethod
    def chunk(self, data: str, chunk_size: int) -> List[str]:
        """Split data into chunks"""
        pass

    @abstractmethod
    def validate_chunk(self, chunk: str) -> bool:
        """Validate chunk format"""
        pass


class FixedSizeChunking(ChunkingStrategy_ABC):
    """Simple fixed-size chunking"""

    def chunk(self, data: str, chunk_size: int) -> List[str]:
        """Split into fixed-size chunks"""
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    def validate_chunk(self, chunk: str) -> bool:
        """Basic validation"""
        return len(chunk) > 0


class DelimiterChunking(ChunkingStrategy_ABC):
    """Chunking based on delimiters"""

    def __init__(self, delimiter: str = "\n"):
        self.delimiter = delimiter

    def chunk(self, data: str, chunk_size: int) -> List[str]:
        """Split by delimiter, respecting chunk size limits"""
        parts = data.split(self.delimiter)
        chunks = []
        current_chunk = ""

        for part in parts:
            potential = current_chunk + part + self.delimiter if current_chunk else part + self.delimiter

            if len(potential) <= chunk_size:
                current_chunk = potential
            else:
                if current_chunk:
                    chunks.append(current_chunk.rstrip(self.delimiter))
                # If single part exceeds chunk_size, force split it
                if len(part) > chunk_size:
                    sub_chunks = [part[i:i + chunk_size] for i in range(0, len(part), chunk_size)]
                    chunks.extend(sub_chunks)
                else:
                    current_chunk = part + self.delimiter

        if current_chunk:
            chunks.append(current_chunk.rstrip(self.delimiter))

        return chunks

    def validate_chunk(self, chunk: str) -> bool:
        """Validate delimiter chunking"""
        return len(chunk) > 0


class AdaptiveChunking(ChunkingStrategy_ABC):
    """Adaptive chunking based on content analysis"""

    def __init__(self, base_size: int = 256):
        self.base_size = base_size
        self.boundary_chars = {' ', '|', '&', ';', '\n', '\t'}

    def chunk(self, data: str, chunk_size: int) -> List[str]:
        """Split adaptively based on natural boundaries"""
        chunks = []
        current_chunk = ""

        for i, char in enumerate(data):
            current_chunk += char

            # Check if at boundary and chunk size is reached
            if (len(current_chunk) >= chunk_size and
                (char in self.boundary_chars or i == len(data) - 1)):
                chunks.append(current_chunk)
                current_chunk = ""
            # Force split if chunk exceeds max size
            elif len(current_chunk) > chunk_size * 1.5:
                chunks.append(current_chunk)
                current_chunk = ""

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def validate_chunk(self, chunk: str) -> bool:
        """Validate adaptive chunk"""
        return len(chunk) > 0 and not chunk.isspace()


class PayloadSafeChunking(ChunkingStrategy_ABC):
    """Chunking that avoids payload-dangerous patterns"""

    DANGEROUS_CHARS = {'<', '>', '"', "'", '\\', '\x00', '\xff'}

    def __init__(self, max_consecutive_special: int = 3):
        self.max_consecutive_special = max_consecutive_special

    def chunk(self, data: str, chunk_size: int) -> List[str]:
        """Split while avoiding dangerous patterns"""
        chunks = []
        current_chunk = ""

        for char in data:
            # Check if adding this char would create dangerous pattern
            test_chunk = current_chunk + char

            if len(test_chunk) >= chunk_size:
                # Try to break at safe point before chunk_size
                safe_idx = self._find_safe_break(current_chunk, chunk_size)
                if safe_idx > 0:
                    chunks.append(current_chunk[:safe_idx])
                    current_chunk = current_chunk[safe_idx:] + char
                else:
                    chunks.append(current_chunk)
                    current_chunk = char
            else:
                current_chunk = test_chunk

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _find_safe_break(self, text: str, position: int) -> int:
        """Find safe break point before position"""
        # Ensure position is within bounds
        position = min(position, len(text) - 1)
        for i in range(position, -1, -1):
            if i < len(text) and text[i] not in self.DANGEROUS_CHARS and text[i].isprintable():
                return i + 1
        return max(1, len(text) // 2)  # Fall back to middle if no safe point found

    def validate_chunk(self, chunk: str) -> bool:
        """Validate chunk safety"""
        consecutive_special = 0
        for char in chunk:
            if char in self.DANGEROUS_CHARS:
                consecutive_special += 1
                if consecutive_special > self.max_consecutive_special:
                    return False
            else:
                consecutive_special = 0
        return len(chunk) > 0


class CommandChunker:
    """Splits commands into manageable chunks"""

    def __init__(self, strategy: ChunkingStrategy = ChunkingStrategy.FIXED_SIZE,
                 chunk_size: int = 512, compress: bool = False,
                 add_checksums: bool = True):
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.compress = compress
        self.add_checksums = add_checksums

        # Initialize strategy
        if strategy == ChunkingStrategy.FIXED_SIZE:
            self._chunker = FixedSizeChunking()
        elif strategy == ChunkingStrategy.DELIMITER:
            self._chunker = DelimiterChunking()
        elif strategy == ChunkingStrategy.ADAPTIVE:
            self._chunker = AdaptiveChunking(base_size=chunk_size)
        elif strategy == ChunkingStrategy.PAYLOAD_SAFE:
            self._chunker = PayloadSafeChunking()
        else:
            self._chunker = FixedSizeChunking()

    def chunk_command(self, command: str, compression_level: int = 6) -> List[Chunk]:
        """
        Split command into chunks with metadata

        Args:
            command: Command string to split
            compression_level: zlib compression level (0-9)

        Returns:
            List of Chunk objects
        """
        # Calculate original command hash
        command_hash = hashlib.sha256(command.encode()).hexdigest()
        original_length = len(command)

        # Compress if requested
        data_to_chunk = command
        compressed = False
        compression_ratio = 1.0

        if self.compress:
            compressed_data = zlib.compress(command.encode(), compression_level)
            # Only use compressed version if it's smaller
            if len(compressed_data) < len(command):
                data_to_chunk = compressed_data.hex()
                compressed = True
                compression_ratio = len(compressed_data) / len(command)

        # Perform chunking
        chunk_strings = self._chunker.chunk(data_to_chunk, self.chunk_size)

        # Create chunk objects with metadata
        chunks = []
        total_chunks = len(chunk_strings)

        for chunk_index, chunk_data in enumerate(chunk_strings):
            # Calculate checksum
            checksum = hashlib.md5(chunk_data.encode()).hexdigest() if self.add_checksums else ""

            metadata = ChunkMetadata(
                chunk_id=random.randint(10000, 99999),
                total_chunks=total_chunks,
                command_hash=command_hash,
                chunk_size=len(chunk_data),
                chunk_index=chunk_index,
                original_length=original_length,
                compressed=compressed,
                compression_ratio=compression_ratio,
                encoding="utf-8",
                checksum=checksum,
                extra_data={
                    "strategy": self.strategy.value,
                    "chunked_length": len(data_to_chunk)
                }
            )

            chunks.append(Chunk(data=chunk_data, metadata=metadata))

        return chunks

    def get_chunking_report(self, command: str) -> Dict:
        """Generate report on chunking"""
        chunks = self.chunk_command(command)

        return {
            "original_command": command,
            "original_length": len(command),
            "total_chunks": len(chunks),
            "chunk_size": self.chunk_size,
            "strategy": self.strategy.value,
            "compressed": chunks[0].metadata.compressed if chunks else False,
            "compression_ratio": chunks[0].metadata.compression_ratio if chunks else 1.0,
            "command_hash": chunks[0].metadata.command_hash if chunks else "",
            "chunks": [chunk.to_dict() for chunk in chunks]
        }


class ChunkReassembler:
    """Reassembles chunks back into original command"""

    def __init__(self, strict_validation: bool = True):
        self.strict_validation = strict_validation
        self._received_chunks: Dict[str, List[Chunk]] = {}

    def add_chunk(self, chunk: Chunk) -> bool:
        """
        Add a chunk to reassembly buffer

        Args:
            chunk: Chunk object to add

        Returns:
            True if command is complete and ready to reassemble
        """
        command_hash = chunk.metadata.command_hash

        if command_hash not in self._received_chunks:
            self._received_chunks[command_hash] = []

        # Validate chunk if strict mode
        if self.strict_validation:
            if not self._validate_chunk(chunk):
                raise ValueError(f"Chunk validation failed for {command_hash}")

        self._received_chunks[command_hash].append(chunk)

        # Check if complete
        total_expected = chunk.metadata.total_chunks
        received = len(self._received_chunks[command_hash])

        return received == total_expected

    def _validate_chunk(self, chunk: Chunk) -> bool:
        """Validate chunk integrity"""
        if not chunk.data:
            return False

        # Verify checksum if present
        if chunk.metadata.checksum:
            calculated = hashlib.md5(chunk.data.encode()).hexdigest()
            if calculated != chunk.metadata.checksum:
                return False

        return True

    def reassemble(self, command_hash: str) -> Optional[str]:
        """
        Reassemble chunks into original command

        Args:
            command_hash: Hash of command to reassemble

        Returns:
            Original command string or None if not complete
        """
        if command_hash not in self._received_chunks:
            return None

        chunks = self._received_chunks[command_hash]

        # Sort by chunk index
        chunks.sort(key=lambda c: c.metadata.chunk_index)

        # Verify we have all chunks
        if len(chunks) != chunks[0].metadata.total_chunks:
            return None

        # Concatenate chunk data
        reassembled_data = "".join([c.data for c in chunks])

        # Decompress if needed
        if chunks[0].metadata.compressed:
            try:
                reassembled_data = zlib.decompress(bytes.fromhex(reassembled_data)).decode()
            except Exception:
                return None

        return reassembled_data

    def get_status(self, command_hash: str) -> Dict:
        """Get reassembly status"""
        if command_hash not in self._received_chunks:
            return {
                "command_hash": command_hash,
                "status": "not_started",
                "received": 0,
                "total": 0,
                "progress": 0.0
            }

        chunks = self._received_chunks[command_hash]
        total = chunks[0].metadata.total_chunks if chunks else 0
        received = len(chunks)

        return {
            "command_hash": command_hash,
            "status": "complete" if received == total else "in_progress",
            "received": received,
            "total": total,
            "progress": (received / total * 100) if total > 0 else 0.0,
            "chunks": [
                {
                    "index": c.metadata.chunk_index,
                    "size": c.metadata.chunk_size,
                    "checksum": c.metadata.checksum
                }
                for c in chunks
            ]
        }

    def clear(self, command_hash: Optional[str] = None):
        """Clear reassembly buffer"""
        if command_hash:
            if command_hash in self._received_chunks:
                del self._received_chunks[command_hash]
        else:
            self._received_chunks.clear()


class CommandChunkingPipeline:
    """End-to-end chunking and reassembly pipeline"""

    def __init__(self, strategy: ChunkingStrategy = ChunkingStrategy.FIXED_SIZE,
                 chunk_size: int = 512, compress: bool = False):
        self.chunker = CommandChunker(
            strategy=strategy,
            chunk_size=chunk_size,
            compress=compress,
            add_checksums=True
        )
        self.reassembler = ChunkReassembler(strict_validation=True)

    def send_command(self, command: str) -> List[Dict]:
        """
        Prepare command for chunked transmission

        Returns:
            List of chunk dictionaries ready for transmission
        """
        chunks = self.chunker.chunk_command(command)
        return [chunk.to_dict() for chunk in chunks]

    def receive_chunk(self, chunk_dict: Dict) -> bool:
        """
        Process received chunk

        Returns:
            True if command is complete
        """
        chunk = Chunk.from_dict(chunk_dict)
        return self.reassembler.add_chunk(chunk)

    def get_command(self, command_hash: str) -> Optional[str]:
        """Retrieve reassembled command"""
        return self.reassembler.reassemble(command_hash)

    def get_progress(self, command_hash: str) -> Dict:
        """Get transfer progress"""
        return self.reassembler.get_status(command_hash)


# Convenience functions

def chunk_command(command: str, chunk_size: int = 512,
                  strategy: ChunkingStrategy = ChunkingStrategy.FIXED_SIZE,
                  compress: bool = False) -> List[Dict]:
    """Quick chunking"""
    chunker = CommandChunker(strategy=strategy, chunk_size=chunk_size, compress=compress)
    chunks = chunker.chunk_command(command)
    return [chunk.to_dict() for chunk in chunks]


def reassemble_chunks(chunks: List[Dict]) -> Optional[str]:
    """Quick reassembly"""
    if not chunks:
        return None

    reassembler = ChunkReassembler()
    command_hash = chunks[0]["metadata"]["command_hash"]

    for chunk_dict in chunks:
        chunk = Chunk.from_dict(chunk_dict)
        reassembler.add_chunk(chunk)

    return reassembler.reassemble(command_hash)


def generate_chunking_report(command: str, chunk_size: int = 512,
                             strategy: ChunkingStrategy = ChunkingStrategy.FIXED_SIZE) -> str:
    """Generate chunking analysis report"""
    chunker = CommandChunker(strategy=strategy, chunk_size=chunk_size)
    report = chunker.get_chunking_report(command)

    output = f"""
COMMAND CHUNKING REPORT
{'=' * 80}

Original Command:
  {report['original_command'][:100]}{'...' if len(report['original_command']) > 100 else ''}

Statistics:
  Original Length: {report['original_length']} bytes
  Chunking Strategy: {report['strategy'].upper()}
  Chunk Size: {report['chunk_size']} bytes
  Total Chunks: {report['total_chunks']}
  Compressed: {report['compressed']}
  Compression Ratio: {report['compression_ratio']:.2%}

Command Hash:
  {report['command_hash']}

Chunk Details:
"""

    for chunk_info in report['chunks']:
        meta = chunk_info['metadata']
        output += f"""
  Chunk {meta['chunk_index'] + 1}/{meta['total_chunks']}:
    ID: {meta['chunk_id']}
    Size: {meta['chunk_size']} bytes
    Checksum: {meta['checksum']}
    Data: {chunk_info['data'][:50]}{'...' if len(chunk_info['data']) > 50 else ''}
"""

    return output.strip()


if __name__ == "__main__":
    # Example usage
    test_command = "powershell.exe -NoProfile -WindowStyle Hidden -Command Write-Host 'This is a very long command that needs to be split into multiple chunks for safer transmission and processing'"

    print("=" * 80)
    print("COMMAND CHUNKING & REASSEMBLY DEMONSTRATION")
    print("=" * 80)

    # Test each strategy
    for strategy in ChunkingStrategy:
        print(f"\n{strategy.value.upper()} STRATEGY")
        print("-" * 80)

        try:
            # Create chunker
            chunker = CommandChunker(strategy=strategy, chunk_size=80, compress=False)
            chunks = chunker.chunk_command(test_command)

            print(f"Total Chunks: {len(chunks)}")
            for chunk in chunks[:3]:
                print(f"  Chunk {chunk.metadata.chunk_index + 1}: "
                      f"{chunk.data[:50]}... "
                      f"(size: {chunk.metadata.chunk_size}, "
                      f"checksum: {chunk.metadata.checksum[:8]}...)")
            if len(chunks) > 3:
                print(f"  ... and {len(chunks) - 3} more chunks")

            # Test reassembly
            reassembler = ChunkReassembler()
            for chunk in chunks:
                if reassembler.add_chunk(chunk):
                    print(f"Assembly complete!")
                    break

            reassembled = reassembler.reassemble(chunks[0].metadata.command_hash)
            if reassembled == test_command:
                print("✓ Reassembly successful - command matches original")
            else:
                print("✗ Reassembly failed - command mismatch")

        except Exception as e:
            print(f"Error with {strategy.value}: {e}")

    # Generate detailed report
    print("\n" + "=" * 80)
    print("DETAILED CHUNKING REPORT")
    print("=" * 80)
    print(generate_chunking_report(test_command, chunk_size=100,
                                   strategy=ChunkingStrategy.FIXED_SIZE))

    # Test pipeline
    print("\n" + "=" * 80)
    print("END-TO-END PIPELINE TEST")
    print("=" * 80)

    pipeline = CommandChunkingPipeline(strategy=ChunkingStrategy.ADAPTIVE, chunk_size=100)
    chunks_to_send = pipeline.send_command(test_command)
    print(f"Prepared {len(chunks_to_send)} chunks for transmission")

    # Simulate receiving chunks
    for i, chunk_dict in enumerate(chunks_to_send):
        is_complete = pipeline.receive_chunk(chunk_dict)
        progress = pipeline.get_progress(chunks_to_send[0]["metadata"]["command_hash"])
        print(f"Received chunk {i + 1}/{len(chunks_to_send)} "
              f"(Progress: {progress['progress']:.1f}%)")

    # Retrieve command
    command_hash = chunks_to_send[0]["metadata"]["command_hash"]
    recovered_command = pipeline.get_command(command_hash)
    if recovered_command == test_command:
        print("✓ Pipeline test successful - command recovered")
    else:
        print("✗ Pipeline test failed")
