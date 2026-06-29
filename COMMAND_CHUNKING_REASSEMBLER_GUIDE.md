# Command Chunking and Reassembly Engine

## Overview

The Command Chunking and Reassembly Engine provides a comprehensive system for splitting long commands into manageable chunks for safer transmission and reassembling them on the receiving end. This is essential for:

- Avoiding command length limits in various execution environments
- Improving reliability of command transmission over unreliable channels
- Enabling progress tracking and partial recovery
- Supporting compression and integrity checking
- Cross-platform compatibility (PowerShell, VBS, Bash, Python)

## Core Components

### ChunkMetadata

Stores metadata about individual chunks:

```python
from command_chunking_reassembler import ChunkMetadata

metadata = ChunkMetadata(
    chunk_id=1,
    total_chunks=5,
    command_hash="abc123...",
    chunk_size=256,
    chunk_index=0,
    original_length=1280,
    compressed=False,
    compression_ratio=1.0,
    checksum="def456..."
)
```

**Key Fields:**
- `chunk_id`: Unique identifier for this chunk
- `total_chunks`: Total number of chunks for this command
- `command_hash`: SHA256 hash of original command
- `chunk_index`: Sequential index (0-based)
- `original_length`: Original command size in bytes
- `compressed`: Whether data is compressed
- `checksum`: MD5 checksum for integrity verification

### Chunk

Represents a single chunk with data and metadata:

```python
chunk = Chunk(
    data="chunk_data_here",
    metadata=ChunkMetadata(...)
)

# Serialize/deserialize
chunk_dict = chunk.to_dict()
restored = Chunk.from_dict(chunk_dict)
```

### Chunking Strategies

#### 1. FIXED_SIZE (Default)

Splits command into equal-sized chunks:

```python
from command_chunking_reassembler import CommandChunker, ChunkingStrategy

chunker = CommandChunker(
    strategy=ChunkingStrategy.FIXED_SIZE,
    chunk_size=512
)
chunks = chunker.chunk_command(command)
```

**Pros:** Simple, predictable, fast
**Cons:** May split in middle of words/commands

#### 2. DELIMITER

Splits on delimiters while respecting chunk size:

```python
chunker = CommandChunker(
    strategy=ChunkingStrategy.DELIMITER,
    chunk_size=512
)
```

**Pros:** Preserves logical boundaries
**Cons:** More complex logic, potentially slower

#### 3. ADAPTIVE

Intelligently splits based on natural boundaries (spaces, pipes, semicolons):

```python
chunker = CommandChunker(
    strategy=ChunkingStrategy.ADAPTIVE,
    chunk_size=512
)
```

**Pros:** Balances readability and performance
**Cons:** May not always find boundaries

#### 4. PAYLOAD_SAFE

Avoids dangerous character sequences that could corrupt payloads:

```python
chunker = CommandChunker(
    strategy=ChunkingStrategy.PAYLOAD_SAFE,
    chunk_size=512
)
```

**Pros:** Safer for untrusted channels
**Cons:** Slower, may create smaller chunks

## Usage Examples

### Basic Chunking

```python
from command_chunking_reassembler import CommandChunker, ChunkingStrategy

# Create chunker
chunker = CommandChunker(
    strategy=ChunkingStrategy.FIXED_SIZE,
    chunk_size=256,
    compress=False,
    add_checksums=True
)

# Split command
command = "powershell -Command Write-Host 'This is a long command...'"
chunks = chunker.chunk_command(command)

# Inspect chunks
for chunk in chunks:
    print(f"Chunk {chunk.metadata.chunk_index}: "
          f"Size={chunk.metadata.chunk_size}, "
          f"Hash={chunk.metadata.command_hash}")
```

### Basic Reassembly

```python
from command_chunking_reassembler import ChunkReassembler

# Create reassembler
reassembler = ChunkReassembler(strict_validation=True)

# Add chunks (can be out of order)
for chunk in chunks:
    is_complete = reassembler.add_chunk(chunk)
    if is_complete:
        print("All chunks received!")
        break

# Retrieve original command
command_hash = chunks[0].metadata.command_hash
recovered = reassembler.reassemble(command_hash)
assert recovered == original_command
```

### Compression

```python
# Enable compression for highly redundant commands
chunker = CommandChunker(
    strategy=ChunkingStrategy.FIXED_SIZE,
    chunk_size=256,
    compress=True  # Uses zlib
)

chunks = chunker.chunk_command(command)

# Check compression ratio
print(f"Compression ratio: {chunks[0].metadata.compression_ratio:.2%}")
```

### Checksum Validation

```python
# Enable automatic checksums
chunker = CommandChunker(
    strategy=ChunkingStrategy.FIXED_SIZE,
    add_checksums=True
)

chunks = chunker.chunk_command(command)

# Reassembler validates automatically
reassembler = ChunkReassembler(strict_validation=True)
for chunk in chunks:
    reassembler.add_chunk(chunk)  # Throws error if checksum invalid
```

### Progress Tracking

```python
# Track reassembly progress
reassembler = ChunkReassembler()
command_hash = chunks[0].metadata.command_hash

# As chunks arrive
for chunk in incoming_chunks:
    reassembler.add_chunk(chunk)
    status = reassembler.get_status(command_hash)
    
    print(f"Progress: {status['progress']:.1f}% "
          f"({status['received']}/{status['total']})")
```

### End-to-End Pipeline

```python
from command_chunking_reassembler import CommandChunkingPipeline

# Initialize pipeline
pipeline = CommandChunkingPipeline(
    strategy=ChunkingStrategy.ADAPTIVE,
    chunk_size=512,
    compress=True
)

# Send side: prepare chunks for transmission
chunks_to_send = pipeline.send_command(command)

# Simulate transmission (e.g., over network)
# ...

# Receive side: process incoming chunks
for chunk_dict in chunks_to_send:
    is_complete = pipeline.receive_chunk(chunk_dict)
    if is_complete:
        print("Transfer complete!")

# Retrieve command
command_hash = chunks_to_send[0]["metadata"]["command_hash"]
recovered_command = pipeline.get_command(command_hash)
```

## Convenience Functions

### Quick Chunking

```python
from command_chunking_reassembler import chunk_command, ChunkingStrategy

# Simple chunking with default settings
chunks = chunk_command(
    command=my_command,
    chunk_size=512,
    strategy=ChunkingStrategy.FIXED_SIZE,
    compress=False
)
```

### Quick Reassembly

```python
from command_chunking_reassembler import reassemble_chunks

# Reassemble if all chunks available
recovered = reassemble_chunks(chunks)
```

### Generate Report

```python
from command_chunking_reassembler import generate_chunking_report

report = generate_chunking_report(
    command=my_command,
    chunk_size=512,
    strategy=ChunkingStrategy.FIXED_SIZE
)
print(report)
```

## Data Serialization

Chunks can be serialized for transmission:

```python
# To JSON
chunk_dict = chunk.to_dict()
json_str = json.dumps(chunk_dict)

# From JSON
recovered_dict = json.loads(json_str)
recovered_chunk = Chunk.from_dict(recovered_dict)
```

**Serialized Format:**

```json
{
  "data": "hex_or_text_data_here",
  "metadata": {
    "chunk_id": 12345,
    "total_chunks": 5,
    "command_hash": "sha256_hash_here",
    "chunk_size": 256,
    "chunk_index": 0,
    "original_length": 1280,
    "compressed": false,
    "compression_ratio": 1.0,
    "encoding": "utf-8",
    "checksum": "md5_hash_here",
    "timestamp": 0,
    "extra_data": {
      "strategy": "fixed_size",
      "chunked_length": 1280
    }
  }
}
```

## Error Handling

### Checksum Mismatch

```python
from command_chunking_reassembler import ChunkReassembler

reassembler = ChunkReassembler(strict_validation=True)

try:
    reassembler.add_chunk(corrupted_chunk)
except ValueError as e:
    print(f"Chunk validation failed: {e}")
```

### Incomplete Assembly

```python
reassembler = ChunkReassembler()

# Add only some chunks
for chunk in chunks[:-1]:  # Missing last chunk
    reassembler.add_chunk(chunk)

# Returns None if incomplete
recovered = reassembler.reassemble(command_hash)
if recovered is None:
    print("Incomplete assembly - missing chunks")
```

## Performance Considerations

### Chunk Size Selection

| Scenario | Recommended Size |
|----------|-----------------|
| PowerShell variable limits | 256-512 bytes |
| Network transmission | 1-4 KB |
| Local IPC | 4-16 KB |
| Highly redundant data | 2-4 KB (with compression) |

### Compression Impact

- **Highly repetitive commands:** 30-70% size reduction
- **Commands with environment variables:** 20-40% reduction
- **Short, diverse commands:** No benefit (may increase size)

```python
# Profile compression for your use case
chunker_no_compress = CommandChunker(compress=False)
chunker_compress = CommandChunker(compress=True)

chunks_uncompressed = chunker_no_compress.chunk_command(my_command)
chunks_compressed = chunker_compress.chunk_command(my_command)

total_uncompressed = sum(len(c.data) for c in chunks_uncompressed)
total_compressed = sum(len(c.data) for c in chunks_compressed)

print(f"Compression benefit: {(1 - total_compressed/total_uncompressed)*100:.1f}%")
```

## Integration with Command Obfuscation

Works seamlessly with `command_string_obfuscator.py`:

```python
from command_string_obfuscator import CommandStringObfuscator, EncodingMethod
from command_chunking_reassembler import CommandChunker, ChunkingStrategy

# Step 1: Obfuscate command
obfuscator = CommandStringObfuscator()
result = obfuscator.obfuscate_command(original_command)
obfuscated = result['encoded_data']

# Step 2: Chunk the obfuscated data
chunker = CommandChunker(
    strategy=ChunkingStrategy.PAYLOAD_SAFE,
    chunk_size=256
)
chunks = chunker.chunk_command(obfuscated)

# Transmission: send chunks
# ...

# Reception: reassemble chunks
reassembler = ChunkReassembler()
for chunk in received_chunks:
    reassembler.add_chunk(chunk)

recovered_obfuscated = reassembler.reassemble(chunks[0].metadata.command_hash)

# Step 3: Decode the obfuscated data (decoder generated by obfuscator)
decoded_command = base64.b64decode(recovered_obfuscated).decode()
```

## Testing

Run the built-in tests:

```bash
python3 -m pytest test_command_chunking_reassembler.py -v
```

Or use the demonstration mode:

```bash
python3 command_chunking_reassembler.py
```

## API Reference

### CommandChunker

```python
class CommandChunker:
    def __init__(self, 
                 strategy: ChunkingStrategy = ChunkingStrategy.FIXED_SIZE,
                 chunk_size: int = 512,
                 compress: bool = False,
                 add_checksums: bool = True)
    
    def chunk_command(self, command: str, 
                     compression_level: int = 6) -> List[Chunk]
    def get_chunking_report(self, command: str) -> Dict
```

### ChunkReassembler

```python
class ChunkReassembler:
    def __init__(self, strict_validation: bool = True)
    
    def add_chunk(self, chunk: Chunk) -> bool
    def reassemble(self, command_hash: str) -> Optional[str]
    def get_status(self, command_hash: str) -> Dict
    def clear(self, command_hash: Optional[str] = None)
```

### CommandChunkingPipeline

```python
class CommandChunkingPipeline:
    def __init__(self, 
                 strategy: ChunkingStrategy = ChunkingStrategy.FIXED_SIZE,
                 chunk_size: int = 512,
                 compress: bool = False)
    
    def send_command(self, command: str) -> List[Dict]
    def receive_chunk(self, chunk_dict: Dict) -> bool
    def get_command(self, command_hash: str) -> Optional[str]
    def get_progress(self, command_hash: str) -> Dict
```

## Security Considerations

1. **Integrity Verification:** Always enable checksums (`add_checksums=True`)
2. **Command Authenticity:** Pair with signature verification when possible
3. **Sensitive Data:** Use compression and encryption for sensitive commands
4. **Chunk Ordering:** Out-of-order reception is handled automatically
5. **Replay Protection:** Use timestamps (`ChunkMetadata.timestamp`) for replay detection

## Troubleshooting

### "Chunk validation failed"

Indicates checksum mismatch - chunk data corrupted in transmission:
- Enable retransmission logic
- Check network/channel reliability
- Consider re-ordering with redundancy

### "Incomplete assembly"

Missing chunks - not all chunks received:
- Increase timeout/wait period
- Implement chunk request/retransmit mechanism
- Monitor `get_status()` for progress

### "Reassemble returned None"

Check if:
- All chunks present: `status['progress'] == 100.0`
- Correct command_hash used
- Chunks not cleared prematurely

## Examples

### VBS Payload with Chunking

```python
from command_chunking_reassembler import CommandChunker, ChunkingStrategy

# Split long command
chunker = CommandChunker(
    strategy=ChunkingStrategy.FIXED_SIZE,
    chunk_size=200
)
command = "cmd.exe /c powershell -EncodedCommand ..." * 3
chunks = chunker.chunk_command(command)

# Generate VBS for each chunk
vbs_code = f"""
' Chunk reassembly and execution
Dim chunks({len(chunks)-1})
"""

for i, chunk in enumerate(chunks):
    vbs_code += f'chunks({i}) = "{chunk.data}"\n'

vbs_code += """
Dim reassembled
reassembled = ""
For i = LBound(chunks) To UBound(chunks)
    reassembled = reassembled & chunks(i)
Next

' Execute reassembled command
CreateObject("WScript.Shell").Run reassembled, 0, False
"""
```

### PowerShell Payload with Chunking

```python
from command_chunking_reassembler import CommandChunker

chunker = CommandChunker(chunk_size=300)
chunks = chunker.chunk_command(command)

ps_code = "$chunks = @(\n"
for chunk in chunks:
    ps_code += f'    "{chunk.data}"\n'
ps_code += ")\n"
ps_code += "$cmd = $chunks -join ''\n"
ps_code += "Invoke-Expression $cmd\n"
```
