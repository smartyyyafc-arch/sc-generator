# Command Chunking and Reassembly - Complete Index

## Quick Navigation

### For Beginners
1. Start with: **CHUNKING_QUICK_REFERENCE.md**
2. Then read: **COMMAND_CHUNKING_REASSEMBLER_GUIDE.md** - Overview section
3. Run: `python3 command_chunking_reassembler.py` for live demo

### For Integration
1. Read: **command_chunking_integration_examples.py** - Code examples
2. Review: **COMMAND_CHUNKING_REASSEMBLER_GUIDE.md** - Integration Patterns
3. Reference: **CHUNKING_QUICK_REFERENCE.md** - Code Patterns

### For Testing
1. Run: `python3 test_command_chunking_reassembler.py`
2. Run: `python3 command_chunking_integration_examples.py`
3. Run: `python3 command_chunking_reassembler.py`

### For Deep Dive
1. Read: **CHUNKING_REASSEMBLER_SUMMARY.md** - Full overview
2. Study: **COMMAND_CHUNKING_REASSEMBLER_GUIDE.md** - Comprehensive guide
3. Analyze: Source code with inline documentation

## File Descriptions

### Core Implementation

**command_chunking_reassembler.py** (1100+ lines)
- Main engine with all 4 strategies
- ChunkMetadata, Chunk, CommandChunker, ChunkReassembler, Pipeline
- Convenience functions
- Live demonstration code
- All production-ready

### Testing

**test_command_chunking_reassembler.py** (750+ lines)
- 40+ test cases
- All strategies tested
- Edge cases and error conditions
- Compression, checksums, Unicode handling
- Run with: `python3 test_command_chunking_reassembler.py`

### Integration Examples

**command_chunking_integration_examples.py** (600+ lines)
- ObfuscationChunkingPipeline integration
- RobustChunkingReceiver with error handling
- ChunkingStatistics and efficiency analysis
- Real-world patterns and workflows

### Documentation

**CHUNKING_QUICK_REFERENCE.md**
- One-liner examples
- Common patterns
- API quick reference
- Troubleshooting tips
- Integration snippets
- **Best for**: Quick lookup

**COMMAND_CHUNKING_REASSEMBLER_GUIDE.md**
- Comprehensive usage guide
- Strategy explanations
- All classes documented
- Integration patterns
- Error handling
- Performance considerations
- **Best for**: Learning

**CHUNKING_REASSEMBLER_SUMMARY.md**
- Implementation overview
- Key features
- Performance characteristics
- Test results
- Future enhancements
- **Best for**: Understanding scope

## Strategy Selection Guide

### FIXED_SIZE (Default)
```python
from command_chunking_reassembler import CommandChunker, ChunkingStrategy

chunker = CommandChunker(strategy=ChunkingStrategy.FIXED_SIZE, chunk_size=512)
```
- **Best for**: 99% of cases
- **Pros**: Simple, predictable, fast
- **Cons**: May split mid-word
- **Speed**: ⚡⚡⚡ Fastest

### DELIMITER
```python
chunker = CommandChunker(strategy=ChunkingStrategy.DELIMITER, chunk_size=512)
```
- **Best for**: Command pipelines, readable chunks
- **Pros**: Preserves logical boundaries
- **Cons**: More complex
- **Speed**: ⚡⚡ Moderate

### ADAPTIVE
```python
chunker = CommandChunker(strategy=ChunkingStrategy.ADAPTIVE, chunk_size=512)
```
- **Best for**: Mixed commands, natural boundaries important
- **Pros**: Intelligent splitting
- **Cons**: Slower
- **Speed**: ⚡ Slower

### PAYLOAD_SAFE
```python
chunker = CommandChunker(strategy=ChunkingStrategy.PAYLOAD_SAFE, chunk_size=512)
```
- **Best for**: Untrusted channels, avoiding corruption
- **Pros**: Maximally safe
- **Cons**: Slowest, may create smaller chunks
- **Speed**: ⚡ Slowest

## Common Code Patterns

### Quick Chunking
```python
from command_chunking_reassembler import chunk_command

chunks = chunk_command(my_command, chunk_size=512)
```

### Quick Reassembly
```python
from command_chunking_reassembler import reassemble_chunks

original = reassemble_chunks(chunks)
```

### Progress Tracking
```python
reassembler = ChunkReassembler()
for chunk in incoming_chunks:
    reassembler.add_chunk(chunk)
    status = reassembler.get_status(command_hash)
    print(f"Progress: {status['progress']:.1f}%")
```

### Obfuscation + Chunking
```python
from command_chunking_integration_examples import ObfuscationChunkingPipeline

pipeline = ObfuscationChunkingPipeline(chunk_size=256)
payload = pipeline.prepare_payload(command)
recovered = pipeline.receive_payload(payload)
```

### Error Handling
```python
try:
    reassembler.add_chunk(chunk)
except ValueError as e:
    print(f"Checksum failed: {e}")
    request_retransmit(chunk.metadata.chunk_index)
```

## Performance Tips

1. **Chunk Size Selection**:
   - PowerShell: 256-512 bytes
   - Network: 512-1024 bytes  
   - Local: 4-16 KB
   - With compression: 256-512 bytes

2. **Compression**:
   - Enable for repetitive commands
   - Disable for short, diverse commands
   - Test with your typical use case

3. **Checksums**:
   - Always enable for untrusted channels
   - Can disable for encrypted/trusted channels

4. **Strategy**:
   - Default FIXED_SIZE for 99% of cases
   - Use others only when specific needs justify performance cost

## Integration Checklist

- [ ] Review CHUNKING_QUICK_REFERENCE.md
- [ ] Run command_chunking_reassembler.py demo
- [ ] Read COMMAND_CHUNKING_REASSEMBLER_GUIDE.md
- [ ] Study command_chunking_integration_examples.py
- [ ] Choose chunking strategy
- [ ] Set chunk size
- [ ] Decide on compression
- [ ] Configure error handling
- [ ] Test with your commands
- [ ] Profile performance
- [ ] Deploy

## API Reference

### Main Classes

```python
CommandChunker(strategy, chunk_size, compress, add_checksums)
ChunkReassembler(strict_validation)
CommandChunkingPipeline(strategy, chunk_size, compress)
Chunk(data, metadata)
ChunkMetadata(...)
```

### Key Methods

```python
# Chunking
chunks = chunker.chunk_command(command, compression_level)
report = chunker.get_chunking_report(command)

# Reassembly
is_complete = reassembler.add_chunk(chunk)
command = reassembler.reassemble(command_hash)
status = reassembler.get_status(command_hash)

# Pipeline
chunks = pipeline.send_command(command)
is_complete = pipeline.receive_chunk(chunk_dict)
command = pipeline.get_command(command_hash)
progress = pipeline.get_progress(command_hash)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Chunk validation failed" | Retransmit chunk, check network |
| Reassembly returns None | Check command_hash, verify all chunks received |
| Large overhead | Increase chunk_size |
| No compression benefit | Disable compression for incompressible data |
| Slow performance | Use FIXED_SIZE strategy instead |

## Examples by Use Case

### Use Case: PowerShell Variable Limits
```python
chunker = CommandChunker(chunk_size=256)
chunks = chunker.chunk_command(command)
```

### Use Case: Network Transmission
```python
chunker = CommandChunker(chunk_size=512, compress=True)
pipeline = CommandChunkingPipeline(chunk_size=512, compress=True)
```

### Use Case: Obfuscated + Chunked
```python
from command_chunking_integration_examples import ObfuscationChunkingPipeline

pipeline = ObfuscationChunkingPipeline(chunk_size=256)
```

### Use Case: Error Recovery
```python
from command_chunking_integration_examples import RobustChunkingReceiver

receiver = RobustChunkingReceiver(max_retries=3)
```

### Use Case: Performance Analysis
```python
from command_chunking_integration_examples import ChunkingStatistics

report = ChunkingStatistics.generate_efficiency_report(command, chunk_size)
```

## Testing Commands

```bash
# Run all demonstrations
python3 command_chunking_reassembler.py
python3 command_chunking_integration_examples.py

# Run tests (requires pytest)
python3 -m pytest test_command_chunking_reassembler.py -v

# Profile specific command
python3 -c "from command_chunking_reassembler import generate_chunking_report; print(generate_chunking_report('your command'))"
```

## Related Files

- `command_string_obfuscator.py` - Obfuscation engine
- `test_command_string_obfuscator.py` - Obfuscation tests

## Key Metrics

- **Total Lines of Code**: 2,450+
- **Test Cases**: 40+
- **Chunking Strategies**: 4
- **Documentation Pages**: 3
- **Integration Examples**: 3+
- **Production Ready**: ✓ Yes

## Getting Help

1. **Quick answers**: CHUNKING_QUICK_REFERENCE.md
2. **Usage questions**: COMMAND_CHUNKING_REASSEMBLER_GUIDE.md
3. **Code examples**: command_chunking_integration_examples.py
4. **Implementation details**: command_chunking_reassembler.py (source)
5. **Testing**: test_command_chunking_reassembler.py

## Next Steps

1. **Learn**: Read CHUNKING_QUICK_REFERENCE.md (5 min)
2. **Explore**: Run `python3 command_chunking_reassembler.py` (2 min)
3. **Understand**: Read COMMAND_CHUNKING_REASSEMBLER_GUIDE.md (20 min)
4. **Integrate**: Study command_chunking_integration_examples.py (10 min)
5. **Implement**: Use in your project
6. **Test**: Run test suite
7. **Deploy**: Monitor and optimize

---

**Version**: 1.0
**Status**: Production Ready
**Last Updated**: 2025-06-29
