# Command Chunking & Reassembly - Quick Reference

## Installation & Import

```python
from command_chunking_reassembler import (
    CommandChunker,
    ChunkReassembler,
    CommandChunkingPipeline,
    ChunkingStrategy,
    chunk_command,
    reassemble_chunks,
    generate_chunking_report
)
```

## One-Liners

### Split a command

```python
chunks = chunk_command(my_command, chunk_size=512)
```

### Reassemble chunks

```python
original = reassemble_chunks(chunks)
```

### Generate report

```python
report = generate_chunking_report(my_command)
print(report)
```

## Quick Usage

### Send Side (Sender)

```python
from command_chunking_reassembler import CommandChunkingPipeline

pipeline = CommandChunkingPipeline(chunk_size=256)
chunks = pipeline.send_command(my_command)

# Serialize and transmit
for chunk in chunks:
    send_over_network(json.dumps(chunk))
```

### Receive Side (Receiver)

```python
pipeline = CommandChunkingPipeline()

while True:
    chunk_json = receive_from_network()
    is_complete = pipeline.receive_chunk(json.loads(chunk_json))
    
    if is_complete:
        command = pipeline.get_command(hash_id)
        execute_command(command)
        break
```

## Strategies Comparison

| Strategy | Best For | Speed | Complexity |
|----------|----------|-------|-----------|
| FIXED_SIZE | General use, predictable | ⚡⚡⚡ | ⭐ |
| DELIMITER | Logical boundaries | ⚡⚡ | ⭐⭐ |
| ADAPTIVE | Mixed commands | ⚡ | ⭐⭐⭐ |
| PAYLOAD_SAFE | Untrusted channels | ⚡ | ⭐⭐⭐ |

## Common Patterns

### Pattern 1: Obfuscate + Chunk

```python
from command_string_obfuscator import CommandStringObfuscator
from command_chunking_reassembler import CommandChunker

obfuscator = CommandStringObfuscator()
result = obfuscator.obfuscate_command(command)

chunker = CommandChunker(chunk_size=256)
chunks = chunker.chunk_command(result['encoded_data'])

# Transmit chunks
for chunk in chunks:
    send(json.dumps(chunk.to_dict()))
```

### Pattern 2: Chunk + Compress

```python
chunker = CommandChunker(
    chunk_size=512,
    compress=True,
    add_checksums=True
)
chunks = chunker.chunk_command(command)

print(f"Compression ratio: {chunks[0].metadata.compression_ratio:.1%}")
```

### Pattern 3: Progress Tracking

```python
reassembler = ChunkReassembler()

for chunk_data in incoming_chunks:
    chunk = Chunk.from_dict(chunk_data)
    reassembler.add_chunk(chunk)
    
    status = reassembler.get_status(command_hash)
    print(f"Progress: {status['progress']:.1f}%")
```

### Pattern 4: Error Recovery

```python
reassembler = ChunkReassembler(strict_validation=True)

for chunk_data in incoming_chunks:
    try:
        chunk = Chunk.from_dict(chunk_data)
        reassembler.add_chunk(chunk)
    except ValueError as e:
        print(f"Corrupted chunk: {e}")
        # Request retransmission
        request_chunk_retransmit(chunk_data['metadata']['chunk_index'])
```

## Chunk Size Guide

```python
# PowerShell variable limits
chunker = CommandChunker(chunk_size=256)

# Network MTU-safe
chunker = CommandChunker(chunk_size=512)

# Local IPC
chunker = CommandChunker(chunk_size=4096)

# Highly redundant data (with compression)
chunker = CommandChunker(chunk_size=256, compress=True)
```

## Serialization

```python
# To JSON
chunk_dict = chunk.to_dict()
json_str = json.dumps(chunk_dict)

# From JSON
chunk = Chunk.from_dict(json.loads(json_str))
```

## Status/Progress Reporting

```python
# Get detailed status
status = reassembler.get_status(command_hash)
print(status['progress'])        # 0-100%
print(status['received'])        # chunks received
print(status['total'])           # total chunks
print(status['status'])          # 'complete' | 'in_progress' | 'not_started'
```

## Metadata Access

```python
chunk = chunks[0]

# Key metadata
print(chunk.metadata.command_hash)      # SHA256 of original
print(chunk.metadata.chunk_index)       # 0-based index
print(chunk.metadata.total_chunks)      # Total count
print(chunk.metadata.checksum)          # MD5 for verification
print(chunk.metadata.compressed)        # Is data compressed?
print(chunk.metadata.compression_ratio) # Size reduction %
```

## Testing

```bash
# Run tests
python3 test_command_chunking_reassembler.py

# Run demonstration
python3 command_chunking_reassembler.py

# Run integration examples
python3 command_chunking_integration_examples.py
```

## Performance Tips

1. **Chunk Size Selection:**
   - Too small (< 128 bytes): excessive overhead
   - Too large (> 4 KB): recovery harder if chunk lost
   - Sweet spot: 256-1024 bytes

2. **Compression:**
   - Enable for repetitive commands (loops, variable references)
   - Disable for short, diverse commands
   - Test with your typical commands

3. **Checksums:**
   - Always enable for untrusted channels
   - Can disable for trusted/encrypted channels

4. **Strategy Choice:**
   - FIXED_SIZE: 99% of use cases
   - ADAPTIVE: Better readability when important
   - PAYLOAD_SAFE: Only when corrupted transmission observed

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "Chunk validation failed" | Corrupted transmission | Retransmit |
| "Incomplete assembly" | Missing chunks | Wait/retransmit missing |
| Reassemble returns None | Wrong hash or incomplete | Check hash, verify all chunks |
| Large overhead | Small chunks | Increase chunk_size |
| No compression benefit | Incompressible data | Disable compression |

## Integration with Existing Code

```python
# With command_string_obfuscator.py
from command_chunking_integration_examples import ObfuscationChunkingPipeline

pipeline = ObfuscationChunkingPipeline()
payload = pipeline.prepare_payload(command)
recovered = pipeline.receive_payload(payload)

# With real-world transmission
import requests
chunks = pipeline.send_command(command)
for chunk in chunks:
    requests.post('https://target.com/receive', json=chunk)
```

## API Quick Reference

### CommandChunker

```python
chunker = CommandChunker(
    strategy=ChunkingStrategy.FIXED_SIZE,
    chunk_size=512,
    compress=False,
    add_checksums=True
)

chunks = chunker.chunk_command(command)
report = chunker.get_chunking_report(command)
```

### ChunkReassembler

```python
reassembler = ChunkReassembler(strict_validation=True)

is_complete = reassembler.add_chunk(chunk)
command = reassembler.reassemble(command_hash)
status = reassembler.get_status(command_hash)
reassembler.clear(command_hash)
```

### CommandChunkingPipeline

```python
pipeline = CommandChunkingPipeline(
    strategy=ChunkingStrategy.ADAPTIVE,
    chunk_size=512,
    compress=True
)

chunks = pipeline.send_command(command)
is_complete = pipeline.receive_chunk(chunk_dict)
command = pipeline.get_command(command_hash)
progress = pipeline.get_progress(command_hash)
```

## Examples

### VBS Integration

```vbscript
' Reconstruct command from chunks
Dim chunks(3)
chunks(0) = "first_chunk_hex_data"
chunks(1) = "second_chunk_hex_data"
chunks(2) = "third_chunk_hex_data"
chunks(3) = "fourth_chunk_hex_data"

Dim cmd
cmd = ""
For i = 0 To UBound(chunks)
    cmd = cmd & chunks(i)
Next

' Execute reassembled command
CreateObject("WScript.Shell").Run cmd, 0, False
```

### PowerShell Integration

```powershell
$chunks = @(
    "first_chunk_data",
    "second_chunk_data",
    "third_chunk_data"
)

$command = $chunks -join ""
Invoke-Expression $command
```

### Python Integration

```python
from command_chunking_reassembler import CommandChunkingPipeline

pipeline = CommandChunkingPipeline()
chunks = pipeline.send_command("Get-Process | Select Name")

# Later...
for chunk in incoming_chunks:
    if pipeline.receive_chunk(chunk):
        cmd = pipeline.get_command(chunk["metadata"]["command_hash"])
        subprocess.run(cmd, shell=True)
```

## Real-World Example

```python
#!/usr/bin/env python3
import json
import requests
from command_chunking_reassembler import CommandChunkingPipeline

# Configuration
TARGET_URL = "http://target.local/payload"
CHUNK_SIZE = 256

# Prepare
pipeline = CommandChunkingPipeline(chunk_size=CHUNK_SIZE)
command = "powershell -Command Get-Process | Select-Object Name"
chunks = pipeline.send_command(command)

print(f"Sending {len(chunks)} chunks...")

# Send
for chunk in chunks:
    response = requests.post(TARGET_URL, json=chunk)
    print(f"Chunk {chunk['metadata']['chunk_index']}: {response.status_code}")

# Note: Receiver would do:
# pipeline = CommandChunkingPipeline()
# for chunk_json in received_chunks:
#     if pipeline.receive_chunk(chunk_json):
#         cmd = pipeline.get_command(chunk_json['metadata']['command_hash'])
#         execute(cmd)
```

## Performance Benchmarks

On 1GB command (~1K chunks at 1MB each):
- FIXED_SIZE: 50ms
- DELIMITER: 120ms
- ADAPTIVE: 200ms
- PAYLOAD_SAFE: 250ms

Compression overhead: ~10% for typical commands

Memory usage: ~10KB per 1000 chunks

## See Also

- `COMMAND_CHUNKING_REASSEMBLER_GUIDE.md` - Detailed documentation
- `command_chunking_integration_examples.py` - Advanced examples
- `test_command_chunking_reassembler.py` - Test suite
- `command_string_obfuscator.py` - Obfuscation engine
