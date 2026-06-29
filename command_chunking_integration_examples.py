#!/usr/bin/env python3
"""
Advanced integration examples for command chunking and reassembly
Demonstrates real-world usage patterns and workflows
"""

import json
import base64
import hashlib
from typing import List, Dict, Optional
from command_chunking_reassembler import (
    CommandChunker,
    ChunkReassembler,
    CommandChunkingPipeline,
    ChunkingStrategy,
    Chunk,
    ChunkMetadata
)
from command_string_obfuscator import (
    CommandStringObfuscator,
    CommandObfuscationConfig,
    EncodingMethod
)


class ObfuscationChunkingPipeline:
    """Integrates obfuscation with chunking for maximum stealth"""

    def __init__(self, encoding_method: EncodingMethod = EncodingMethod.BASE64,
                 chunk_size: int = 256, chunking_strategy: ChunkingStrategy = ChunkingStrategy.ADAPTIVE):
        self.obfuscator = CommandStringObfuscator(
            CommandObfuscationConfig(
                encoding_method=encoding_method,
                chunk_size=chunk_size // 2  # Pre-obfuscation chunk size
            )
        )
        self.chunker = CommandChunker(
            strategy=chunking_strategy,
            chunk_size=chunk_size,
            compress=True,
            add_checksums=True
        )
        self.reassembler = ChunkReassembler(strict_validation=True)

    def prepare_payload(self, command: str) -> Dict:
        """
        Complete payload preparation:
        1. Obfuscate command
        2. Chunk the obfuscated data
        3. Prepare for transmission

        Returns:
            Dictionary with payload info for transmission
        """
        # Step 1: Obfuscate
        obfuscation_result = self.obfuscator.obfuscate_command(command)
        obfuscated_data = obfuscation_result['encoded_data']

        # Step 2: Chunk
        chunks = self.chunker.chunk_command(obfuscated_data)

        # Step 3: Prepare transmission payload
        payload = {
            "command_hash": chunks[0].metadata.command_hash,
            "original_command": command,
            "obfuscation_method": obfuscation_result['metadata']['method'],
            "obfuscation_level": obfuscation_result['obfuscation_level'],
            "decoder_code": obfuscation_result['decoder_code'],
            "total_chunks": len(chunks),
            "chunk_size": chunks[0].metadata.chunk_size,
            "chunks": [chunk.to_dict() for chunk in chunks],
            "compression_ratio": chunks[0].metadata.compression_ratio if chunks else 1.0
        }

        return payload

    def receive_payload(self, payload: Dict) -> Optional[str]:
        """
        Complete payload reception and decoding:
        1. Reassemble chunks
        2. De-obfuscate
        3. Return original command

        Returns:
            Original command or None if assembly failed
        """
        # Step 1: Reassemble chunks
        chunks = [Chunk.from_dict(c) for c in payload['chunks']]

        for chunk in chunks:
            if not self.reassembler.add_chunk(chunk):
                continue

        command_hash = payload['command_hash']
        obfuscated_data = self.reassembler.reassemble(command_hash)

        if not obfuscated_data:
            return None

        # Step 2: De-obfuscate (would normally use embedded decoder)
        # For this example, we'll show the decoder code
        decoder_code = payload['decoder_code']

        # Step 3: Execute decoder in isolated context
        local_vars = {}
        exec(decoder_code, {"base64": base64, "bytes": bytes}, local_vars)

        if 'command' in local_vars:
            return local_vars['command']

        return None

    def get_transmission_report(self, payload: Dict) -> str:
        """Generate report on transmission payload"""
        report = f"""
OBFUSCATION & CHUNKING TRANSMISSION REPORT
{'=' * 80}

Original Command:
  {payload['original_command'][:100]}{'...' if len(payload['original_command']) > 100 else ''}

Obfuscation:
  Method: {payload['obfuscation_method'].upper()}
  Level: {payload['obfuscation_level']}/5

Chunking:
  Strategy: ADAPTIVE
  Total Chunks: {payload['total_chunks']}
  Chunk Size: {payload['chunk_size']} bytes
  Compression Ratio: {payload['compression_ratio']:.2%}

Payload Size:
  Original: {len(payload['original_command'])} bytes
  Obfuscated (before chunking): {sum(len(c['metadata']['chunked_length']) if isinstance(c['metadata'].get('chunked_length'), str) else c['metadata'].get('chunked_length', 0) for c in payload['chunks']) if payload['chunks'] else 'N/A'} bytes
  Total chunks data: {sum(len(c['data']) for c in payload['chunks'])} bytes

Decoder Code:
  {payload['decoder_code'][:200]}...

Command Hash:
  {payload['command_hash']}
"""
        return report


class RobustChunkingReceiver:
    """Robust receiver with error handling and retransmission"""

    def __init__(self, max_retries: int = 3):
        self.reassemblers: Dict[str, ChunkReassembler] = {}
        self.max_retries = max_retries
        self.retry_counts: Dict[str, int] = {}
        self.failed_chunks: Dict[str, List[int]] = {}

    def receive_chunk(self, chunk_dict: Dict) -> Dict:
        """
        Receive a chunk with error tracking

        Returns:
            Status dictionary with reception details
        """
        chunk = Chunk.from_dict(chunk_dict)
        command_hash = chunk.metadata.command_hash

        # Initialize tracking for this command
        if command_hash not in self.reassemblers:
            self.reassemblers[command_hash] = ChunkReassembler(strict_validation=True)
            self.retry_counts[command_hash] = 0
            self.failed_chunks[command_hash] = []

        status = {
            "command_hash": command_hash,
            "chunk_index": chunk.metadata.chunk_index,
            "status": "received",
            "error": None
        }

        try:
            is_complete = self.reassemblers[command_hash].add_chunk(chunk)

            if is_complete:
                status["status"] = "complete"
                status["progress"] = 100.0
            else:
                progress_status = self.reassemblers[command_hash].get_status(command_hash)
                status["progress"] = progress_status['progress']
                status["status"] = "in_progress"

        except ValueError as e:
            status["status"] = "checksum_failed"
            status["error"] = str(e)
            status["retry_count"] = self.retry_counts[command_hash]
            self.failed_chunks[command_hash].append(chunk.metadata.chunk_index)

            if self.retry_counts[command_hash] < self.max_retries:
                status["action"] = "request_retransmission"
                self.retry_counts[command_hash] += 1
            else:
                status["action"] = "abort"

        return status

    def get_reception_summary(self, command_hash: str) -> Dict:
        """Get detailed reception summary"""
        if command_hash not in self.reassemblers:
            return {
                "command_hash": command_hash,
                "status": "unknown",
                "summary": "No chunks received yet"
            }

        reassembler = self.reassemblers[command_hash]
        progress = reassembler.get_status(command_hash)

        summary = {
            "command_hash": command_hash,
            "total_chunks": progress['total'],
            "received_chunks": progress['received'],
            "missing_chunks": progress['total'] - progress['received'],
            "failed_chunks": self.failed_chunks[command_hash],
            "progress": progress['progress'],
            "status": progress['status'],
            "completion_chunks": [
                {
                    "index": c['index'],
                    "size": c['size'],
                    "checksum": c['checksum'][:8] + "..."
                }
                for c in progress['chunks']
            ]
        }

        return summary


class ChunkingStatistics:
    """Analyze chunking statistics and efficiency"""

    @staticmethod
    def analyze_strategy_efficiency(command: str, chunk_size: int) -> Dict:
        """
        Compare all chunking strategies for given command

        Returns:
            Dictionary with efficiency metrics for each strategy
        """
        results = {}

        for strategy in ChunkingStrategy:
            try:
                chunker = CommandChunker(
                    strategy=strategy,
                    chunk_size=chunk_size,
                    compress=False,
                    add_checksums=True
                )

                chunks = chunker.chunk_command(command)

                # Calculate metrics
                total_data_size = sum(len(c.data) for c in chunks)
                chunk_sizes = [len(c.data) for c in chunks]
                avg_chunk = sum(chunk_sizes) / len(chunk_sizes)
                size_variance = sum((s - avg_chunk) ** 2 for s in chunk_sizes) / len(chunk_sizes)

                results[strategy.value] = {
                    "total_chunks": len(chunks),
                    "total_data_size": total_data_size,
                    "average_chunk_size": avg_chunk,
                    "min_chunk_size": min(chunk_sizes),
                    "max_chunk_size": max(chunk_sizes),
                    "size_variance": size_variance,
                    "overhead_ratio": total_data_size / len(command),
                    "metadata_per_chunk": len(json.dumps(chunks[0].metadata.to_dict())),
                }
            except Exception as e:
                results[strategy.value] = {"error": str(e)}

        return results

    @staticmethod
    def compression_impact_analysis(command: str, chunk_size: int) -> Dict:
        """Analyze compression impact"""
        chunker_uncompressed = CommandChunker(
            chunk_size=chunk_size,
            compress=False
        )
        chunker_compressed = CommandChunker(
            chunk_size=chunk_size,
            compress=True
        )

        chunks_uncompressed = chunker_uncompressed.chunk_command(command)
        chunks_compressed = chunker_compressed.chunk_command(command)

        total_uncompressed = sum(len(c.data) for c in chunks_uncompressed)
        total_compressed = sum(len(c.data) for c in chunks_compressed)

        return {
            "original_size": len(command),
            "uncompressed_total": total_uncompressed,
            "compressed_total": total_compressed,
            "compression_savings": total_uncompressed - total_compressed,
            "compression_ratio": total_compressed / total_uncompressed,
            "uncompressed_chunks": len(chunks_uncompressed),
            "compressed_chunks": len(chunks_compressed),
            "is_beneficial": total_compressed < total_uncompressed
        }

    @staticmethod
    def generate_efficiency_report(command: str, chunk_size: int) -> str:
        """Generate detailed efficiency analysis report"""
        strategy_analysis = ChunkingStatistics.analyze_strategy_efficiency(command, chunk_size)
        compression_analysis = ChunkingStatistics.compression_impact_analysis(command, chunk_size)

        report = f"""
CHUNKING EFFICIENCY ANALYSIS
{'=' * 80}

Command Analysis:
  Original Length: {len(command)} bytes
  Command Sample: {command[:60]}{'...' if len(command) > 60 else ''}

Chunk Size: {chunk_size} bytes

STRATEGY COMPARISON
{'-' * 80}
"""

        for strategy, metrics in strategy_analysis.items():
            if 'error' in metrics:
                report += f"\n{strategy.upper()}:\n  Error: {metrics['error']}\n"
            else:
                report += f"""
{strategy.upper()}:
  Total Chunks: {metrics['total_chunks']}
  Total Data Size: {metrics['total_data_size']} bytes
  Average Chunk Size: {metrics['average_chunk_size']:.1f} bytes
  Min/Max: {metrics['min_chunk_size']}/{metrics['max_chunk_size']} bytes
  Size Variance: {metrics['size_variance']:.2f}
  Overhead Ratio: {metrics['overhead_ratio']:.3f}x
"""

        report += f"""

COMPRESSION ANALYSIS
{'-' * 80}
  Original Size: {compression_analysis['original_size']} bytes
  Uncompressed Total: {compression_analysis['uncompressed_total']} bytes
  Compressed Total: {compression_analysis['compressed_total']} bytes
  Compression Savings: {compression_analysis['compression_savings']} bytes
  Compression Ratio: {compression_analysis['compression_ratio']:.2%}
  Beneficial: {'Yes' if compression_analysis['is_beneficial'] else 'No'}

RECOMMENDATION
{'-' * 80}
"""

        # Find best strategy
        non_error_strategies = {k: v for k, v in strategy_analysis.items() if 'error' not in v}
        if non_error_strategies:
            best_strategy = min(non_error_strategies.items(),
                              key=lambda x: x[1]['size_variance'])[0]
            report += f"Recommended Strategy: {best_strategy.upper()}\n"
            report += "Rationale: Minimizes chunk size variance for optimal distribution\n"

        if compression_analysis['is_beneficial']:
            report += "Enable Compression: Yes (provides size reduction)\n"
        else:
            report += "Enable Compression: No (overhead outweighs benefits)\n"

        return report


# Demonstration functions

def demo_obfuscation_chunking_pipeline():
    """Demonstrate integrated obfuscation and chunking"""
    print("=" * 80)
    print("OBFUSCATION & CHUNKING PIPELINE DEMO")
    print("=" * 80)

    pipeline = ObfuscationChunkingPipeline(
        encoding_method=EncodingMethod.BASE64,
        chunk_size=256,
        chunking_strategy=ChunkingStrategy.ADAPTIVE
    )

    command = "powershell.exe -NoProfile -WindowStyle Hidden -Command " \
              "Write-Host 'Obfuscated and chunked command execution' | Out-Null"

    # Prepare
    print(f"\nOriginal Command ({len(command)} bytes):")
    print(f"  {command}\n")

    payload = pipeline.prepare_payload(command)

    print(f"Prepared {payload['total_chunks']} chunks for transmission")
    print(f"Compression: {payload['compression_ratio']:.2%}")
    print(f"Total payload size: {sum(len(c['data']) for c in payload['chunks'])} bytes\n")

    # Receive
    print("Receiving and reassembling chunks...")
    recovered = pipeline.receive_payload(payload)

    if recovered == command:
        print("✓ Successfully recovered original command!")
    else:
        print("✗ Command mismatch!")

    print(pipeline.get_transmission_report(payload))


def demo_robust_receiver():
    """Demonstrate robust receiver with error handling"""
    print("\n" + "=" * 80)
    print("ROBUST RECEIVER DEMO")
    print("=" * 80)

    receiver = RobustChunkingReceiver(max_retries=3)

    # Create test chunks
    chunker = CommandChunker(
        strategy=ChunkingStrategy.FIXED_SIZE,
        chunk_size=100,
        add_checksums=True
    )
    command = "test command " * 30
    chunks = chunker.chunk_command(command)

    print(f"\nReceiving {len(chunks)} chunks...\n")

    # Simulate reception with one chunk error
    for i, chunk in enumerate(chunks):
        chunk_dict = chunk.to_dict()

        # Corrupt one chunk for demonstration
        if i == len(chunks) // 2:
            print(f"  [Chunk {i}] Corrupting data...")
            chunk_dict['data'] = "corrupted_data"

        status = receiver.receive_chunk(chunk_dict)
        print(f"  [Chunk {status['chunk_index']}] {status['status']} - "
              f"Progress: {status.get('progress', 'N/A')}%")

        if status['status'] == 'checksum_failed':
            print(f"    -> {status['action']}")

    # Get summary
    command_hash = chunks[0].metadata.command_hash
    summary = receiver.get_reception_summary(command_hash)

    print(f"\nReception Summary:")
    print(f"  Total Chunks: {summary['total_chunks']}")
    print(f"  Received: {summary['received_chunks']}")
    print(f"  Failed: {len(summary['failed_chunks'])}")
    print(f"  Progress: {summary['progress']:.1f}%")
    print(f"  Status: {summary['status']}")


def demo_efficiency_analysis():
    """Demonstrate efficiency analysis"""
    print("\n" + "=" * 80)
    print("EFFICIENCY ANALYSIS DEMO")
    print("=" * 80)

    command = "powershell.exe -NoProfile -Command Get-Process | Where-Object {$_.Memory -gt 100MB} | Select-Object Name, Memory, ProcessID" * 3
    chunk_size = 256

    print(f"\nAnalyzing command chunking efficiency...")
    print(f"Command size: {len(command)} bytes")
    print(f"Target chunk size: {chunk_size} bytes\n")

    report = ChunkingStatistics.generate_efficiency_report(command, chunk_size)
    print(report)


if __name__ == "__main__":
    demo_obfuscation_chunking_pipeline()
    demo_robust_receiver()
    demo_efficiency_analysis()
