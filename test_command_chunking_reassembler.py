#!/usr/bin/env python3
"""
Test suite for command chunking and reassembly engine
"""

import pytest
import hashlib
import json
from command_chunking_reassembler import (
    ChunkingStrategy,
    ChunkMetadata,
    Chunk,
    CommandChunker,
    ChunkReassembler,
    CommandChunkingPipeline,
    FixedSizeChunking,
    DelimiterChunking,
    AdaptiveChunking,
    PayloadSafeChunking,
    chunk_command,
    reassemble_chunks,
    generate_chunking_report
)


class TestChunkMetadata:
    """Test ChunkMetadata class"""

    def test_metadata_creation(self):
        """Test metadata object creation"""
        meta = ChunkMetadata(
            chunk_id=1,
            total_chunks=5,
            command_hash="abc123",
            chunk_size=256,
            chunk_index=0,
            original_length=1280,
            checksum="def456"
        )
        assert meta.chunk_id == 1
        assert meta.total_chunks == 5

    def test_metadata_to_dict(self):
        """Test metadata serialization"""
        meta = ChunkMetadata(
            chunk_id=1,
            total_chunks=5,
            command_hash="abc123",
            chunk_size=256,
            chunk_index=0,
            original_length=1280,
            checksum="def456"
        )
        data = meta.to_dict()
        assert isinstance(data, dict)
        assert data['chunk_id'] == 1
        assert data['command_hash'] == "abc123"

    def test_metadata_from_dict(self):
        """Test metadata deserialization"""
        data = {
            'chunk_id': 1,
            'total_chunks': 5,
            'command_hash': "abc123",
            'chunk_size': 256,
            'chunk_index': 0,
            'original_length': 1280,
            'compressed': False,
            'compression_ratio': 1.0,
            'encoding': "utf-8",
            'checksum': "def456",
            'timestamp': 0,
            'extra_data': {}
        }
        meta = ChunkMetadata.from_dict(data)
        assert meta.chunk_id == 1
        assert meta.command_hash == "abc123"


class TestChunk:
    """Test Chunk class"""

    def test_chunk_creation(self):
        """Test chunk object creation"""
        meta = ChunkMetadata(
            chunk_id=1, total_chunks=5, command_hash="test",
            chunk_size=256, chunk_index=0, original_length=1280
        )
        chunk = Chunk(data="test_data", metadata=meta)
        assert chunk.data == "test_data"
        assert chunk.metadata.chunk_id == 1

    def test_chunk_serialization(self):
        """Test chunk to/from dict"""
        meta = ChunkMetadata(
            chunk_id=1, total_chunks=5, command_hash="test",
            chunk_size=256, chunk_index=0, original_length=1280,
            checksum="abc123"
        )
        chunk = Chunk(data="test_data", metadata=meta)
        chunk_dict = chunk.to_dict()

        restored = Chunk.from_dict(chunk_dict)
        assert restored.data == chunk.data
        assert restored.metadata.chunk_id == chunk.metadata.chunk_id


class TestFixedSizeChunking:
    """Test FixedSizeChunking strategy"""

    def test_basic_chunking(self):
        """Test basic fixed-size chunking"""
        chunker = FixedSizeChunking()
        data = "0123456789" * 10  # 100 chars
        chunks = chunker.chunk(data, 25)

        assert len(chunks) == 4
        assert len(chunks[0]) == 25
        assert len(chunks[-1]) == 25

    def test_uneven_chunks(self):
        """Test chunking with uneven division"""
        chunker = FixedSizeChunking()
        data = "0123456789" * 7  # 70 chars
        chunks = chunker.chunk(data, 25)

        assert len(chunks) == 3
        assert len(chunks[-1]) == 20

    def test_single_chunk(self):
        """Test data smaller than chunk size"""
        chunker = FixedSizeChunking()
        data = "small"
        chunks = chunker.chunk(data, 100)

        assert len(chunks) == 1
        assert chunks[0] == "small"

    def test_validation(self):
        """Test chunk validation"""
        chunker = FixedSizeChunking()
        assert chunker.validate_chunk("data") is True
        assert chunker.validate_chunk("") is False


class TestDelimiterChunking:
    """Test DelimiterChunking strategy"""

    def test_delimiter_chunking(self):
        """Test chunking by delimiter"""
        chunker = DelimiterChunking(delimiter="|")
        data = "part1|part2|part3|part4|part5"
        chunks = chunker.chunk(data, 50)

        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk) <= 50

    def test_newline_delimiter(self):
        """Test chunking with newlines"""
        chunker = DelimiterChunking(delimiter="\n")
        data = "line1\nline2\nline3\nline4\nline5"
        chunks = chunker.chunk(data, 30)

        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk) <= 30

    def test_oversized_part(self):
        """Test handling of parts larger than chunk size"""
        chunker = DelimiterChunking(delimiter="|")
        data = "part1|" + "x" * 100 + "|part3"
        chunks = chunker.chunk(data, 50)

        assert len(chunks) >= 2
        # Large part should be split
        found_split = any(len(c) < 100 for c in chunks)
        assert found_split


class TestAdaptiveChunking:
    """Test AdaptiveChunking strategy"""

    def test_adaptive_boundary_detection(self):
        """Test adaptive chunking respects boundaries"""
        chunker = AdaptiveChunking(base_size=50)
        data = "command1 && command2 & command3 | command4"
        chunks = chunker.chunk(data, 50)

        assert len(chunks) > 0
        # All chunks should be valid
        for chunk in chunks:
            assert chunker.validate_chunk(chunk)

    def test_adaptive_with_long_command(self):
        """Test adaptive chunking with long command"""
        chunker = AdaptiveChunking(base_size=100)
        data = "powershell.exe -Command " + "x" * 200 + " -Verbose"
        chunks = chunker.chunk(data, 100)

        assert len(chunks) > 1


class TestPayloadSafeChunking:
    """Test PayloadSafeChunking strategy"""

    def test_payload_safe_chunks(self):
        """Test payload-safe chunking"""
        chunker = PayloadSafeChunking()
        data = 'echo "test" > file.txt; cat file.txt'
        chunks = chunker.chunk(data, 20)

        assert len(chunks) > 0
        for chunk in chunks:
            assert chunker.validate_chunk(chunk)

    def test_dangerous_char_detection(self):
        """Test detection of dangerous characters"""
        chunker = PayloadSafeChunking(max_consecutive_special=2)
        # This chunk has many dangerous chars but should still validate
        chunk = 'test"quote'
        assert chunker.validate_chunk(chunk)


class TestCommandChunker:
    """Test CommandChunker main class"""

    def test_chunk_command_basic(self):
        """Test basic command chunking"""
        chunker = CommandChunker(
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100
        )
        command = "powershell.exe -Command Write-Host 'Hello World'" * 5
        chunks = chunker.chunk_command(command)

        assert len(chunks) > 1
        assert all(isinstance(c, Chunk) for c in chunks)
        assert chunks[0].metadata.command_hash == chunks[-1].metadata.command_hash

    def test_chunk_metadata_correctness(self):
        """Test chunk metadata is correct"""
        chunker = CommandChunker(
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100
        )
        command = "test" * 100
        chunks = chunker.chunk_command(command)

        # All chunks should have same total count
        total = chunks[0].metadata.total_chunks
        assert all(c.metadata.total_chunks == total for c in chunks)

        # Indices should be sequential
        indices = [c.metadata.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_checksum_calculation(self):
        """Test checksum is calculated"""
        chunker = CommandChunker(
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100,
            add_checksums=True
        )
        command = "test_command"
        chunks = chunker.chunk_command(command)

        assert all(c.metadata.checksum for c in chunks)
        # Verify checksum is valid
        for chunk in chunks:
            expected = hashlib.md5(chunk.data.encode()).hexdigest()
            assert chunk.metadata.checksum == expected

    def test_compression(self):
        """Test command compression"""
        chunker = CommandChunker(
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100,
            compress=True
        )
        command = "test" * 1000  # Highly compressible
        chunks = chunker.chunk_command(command)

        assert chunks[0].metadata.compressed is True
        assert chunks[0].metadata.compression_ratio < 1.0

    def test_chunking_report(self):
        """Test chunking report generation"""
        chunker = CommandChunker(
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100
        )
        command = "test" * 50
        report = chunker.get_chunking_report(command)

        assert 'original_command' in report
        assert 'total_chunks' in report
        assert 'command_hash' in report
        assert 'chunks' in report
        assert len(report['chunks']) > 0


class TestChunkReassembler:
    """Test ChunkReassembler class"""

    def test_reassemble_simple(self):
        """Test simple reassembly"""
        # Create chunks
        chunker = CommandChunker(strategy=ChunkingStrategy.FIXED_SIZE, chunk_size=50)
        command = "This is a test command that needs to be reassembled"
        chunks = chunker.chunk_command(command)

        # Reassemble
        reassembler = ChunkReassembler()
        for chunk in chunks:
            reassembler.add_chunk(chunk)

        result = reassembler.reassemble(chunks[0].metadata.command_hash)
        assert result == command

    def test_reassemble_out_of_order(self):
        """Test reassembly with out-of-order chunks"""
        chunker = CommandChunker(strategy=ChunkingStrategy.FIXED_SIZE, chunk_size=50)
        command = "Out of order test " * 20
        chunks = chunker.chunk_command(command)

        # Add chunks out of order
        reassembler = ChunkReassembler()
        for chunk in reversed(chunks):
            reassembler.add_chunk(chunk)

        result = reassembler.reassemble(chunks[0].metadata.command_hash)
        assert result == command

    def test_reassemble_partial(self):
        """Test reassembly with missing chunks"""
        chunker = CommandChunker(strategy=ChunkingStrategy.FIXED_SIZE, chunk_size=50)
        command = "partial test " * 20
        chunks = chunker.chunk_command(command)

        # Add only some chunks
        reassembler = ChunkReassembler()
        for chunk in chunks[:-1]:  # Skip last chunk
            reassembler.add_chunk(chunk)

        result = reassembler.reassemble(chunks[0].metadata.command_hash)
        assert result is None

    def test_checksum_validation_fail(self):
        """Test checksum validation failure"""
        chunker = CommandChunker(
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=50,
            add_checksums=True
        )
        command = "checksum test " * 20
        chunks = chunker.chunk_command(command)

        # Corrupt a chunk
        chunks[0].metadata.checksum = "0" * 32

        reassembler = ChunkReassembler(strict_validation=True)
        with pytest.raises(ValueError):
            reassembler.add_chunk(chunks[0])

    def test_get_status(self):
        """Test status reporting"""
        chunker = CommandChunker(strategy=ChunkingStrategy.FIXED_SIZE, chunk_size=50)
        command = "status test " * 20
        chunks = chunker.chunk_command(command)

        reassembler = ChunkReassembler()
        hash_id = chunks[0].metadata.command_hash

        # Before any chunks
        status = reassembler.get_status(hash_id)
        assert status['status'] == 'not_started'
        assert status['progress'] == 0.0

        # After some chunks
        for chunk in chunks[:-1]:
            reassembler.add_chunk(chunk)

        status = reassembler.get_status(hash_id)
        assert status['status'] == 'in_progress'
        assert 0 < status['progress'] < 100

        # After all chunks
        reassembler.add_chunk(chunks[-1])
        status = reassembler.get_status(hash_id)
        assert status['status'] == 'complete'
        assert status['progress'] == 100.0

    def test_clear_buffer(self):
        """Test clearing reassembly buffer"""
        chunker = CommandChunker(strategy=ChunkingStrategy.FIXED_SIZE, chunk_size=50)
        command1 = "command 1 " * 10
        command2 = "command 2 " * 10

        chunks1 = chunker.chunk_command(command1)
        chunks2 = chunker.chunk_command(command2)

        reassembler = ChunkReassembler()
        for chunk in chunks1 + chunks2:
            reassembler.add_chunk(chunk)

        hash1 = chunks1[0].metadata.command_hash
        hash2 = chunks2[0].metadata.command_hash

        # Clear one
        reassembler.clear(hash1)
        status1 = reassembler.get_status(hash1)
        status2 = reassembler.get_status(hash2)

        assert status1['status'] == 'not_started'
        assert status2['received'] > 0


class TestCommandChunkingPipeline:
    """Test end-to-end pipeline"""

    def test_pipeline_full_cycle(self):
        """Test complete pipeline cycle"""
        pipeline = CommandChunkingPipeline(
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100
        )
        command = "powershell -Command Write-Host 'Test'" * 10

        # Send
        chunks_dict = pipeline.send_command(command)
        assert len(chunks_dict) > 0

        # Receive
        hash_id = chunks_dict[0]['metadata']['command_hash']
        for chunk_dict in chunks_dict:
            is_complete = pipeline.receive_chunk(chunk_dict)
            if is_complete:
                break

        # Get
        recovered = pipeline.get_command(hash_id)
        assert recovered == command

    def test_pipeline_progress_tracking(self):
        """Test progress tracking"""
        pipeline = CommandChunkingPipeline(
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100
        )
        command = "test" * 100

        chunks_dict = pipeline.send_command(command)
        hash_id = chunks_dict[0]['metadata']['command_hash']

        # Receive one chunk at a time
        for i, chunk_dict in enumerate(chunks_dict):
            pipeline.receive_chunk(chunk_dict)
            progress = pipeline.get_progress(hash_id)
            expected_progress = ((i + 1) / len(chunks_dict)) * 100
            assert abs(progress['progress'] - expected_progress) < 1


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_chunk_command_function(self):
        """Test chunk_command convenience function"""
        command = "test command " * 20
        chunks = chunk_command(command, chunk_size=100)

        assert len(chunks) > 0
        assert all('metadata' in c for c in chunks)
        assert all('data' in c for c in chunks)

    def test_reassemble_chunks_function(self):
        """Test reassemble_chunks convenience function"""
        command = "test command " * 20
        chunks = chunk_command(command, chunk_size=100)

        reassembled = reassemble_chunks(chunks)
        assert reassembled == command

    def test_generate_report_function(self):
        """Test report generation"""
        command = "test" * 50
        report = generate_chunking_report(command, chunk_size=100)

        assert "COMMAND CHUNKING REPORT" in report
        assert "Original Length" in report
        assert "Total Chunks" in report


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_command(self):
        """Test handling of empty command"""
        chunker = CommandChunker(strategy=ChunkingStrategy.FIXED_SIZE, chunk_size=100)
        with pytest.raises(Exception):
            chunker.chunk_command("")

    def test_very_large_chunk_size(self):
        """Test with chunk size larger than command"""
        chunker = CommandChunker(strategy=ChunkingStrategy.FIXED_SIZE, chunk_size=10000)
        command = "small"
        chunks = chunker.chunk_command(command)

        assert len(chunks) == 1
        assert chunks[0].data == "small"

    def test_chunk_size_one(self):
        """Test with chunk size of 1"""
        chunker = CommandChunker(strategy=ChunkingStrategy.FIXED_SIZE, chunk_size=1)
        command = "abc"
        chunks = chunker.chunk_command(command)

        assert len(chunks) == 3
        assert all(len(c.data) == 1 for c in chunks)

    def test_unicode_handling(self):
        """Test unicode character handling"""
        chunker = CommandChunker(strategy=ChunkingStrategy.FIXED_SIZE, chunk_size=50)
        command = "Unicode test: 你好世界 🚀 €£¥" * 5

        chunks = chunker.chunk_command(command)
        assert len(chunks) > 0

        reassembler = ChunkReassembler()
        for chunk in chunks:
            reassembler.add_chunk(chunk)

        result = reassembler.reassemble(chunks[0].metadata.command_hash)
        assert result == command

    def test_special_characters(self):
        """Test special character handling"""
        chunker = CommandChunker(strategy=ChunkingStrategy.FIXED_SIZE, chunk_size=50)
        command = 'test"quotes"and\'single\'and\\backslash\\and|pipe|' * 5

        chunks = chunker.chunk_command(command)
        reassembler = ChunkReassembler()
        for chunk in chunks:
            reassembler.add_chunk(chunk)

        result = reassembler.reassemble(chunks[0].metadata.command_hash)
        assert result == command


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
