# Timestamp Spoofer - Quick Start Guide

## Basic Usage

### Installation
```python
from timestamp_spoofer import TimestampSpoofer
spoofer = TimestampSpoofer()
```

### Match File to System File
```python
info = spoofer.spoof_to_match_file("/tmp/payload.vbs", "/bin/ls")
```

### Spoof to Specific Date
```python
from datetime import datetime

target = datetime(2020, 1, 15, 10, 30, 0)
info = spoofer.spoof_to_datetime("/tmp/old_file.txt", target)
```

### Spoof Multiple Files
```python
files = ["/tmp/payload1.vbs", "/tmp/payload2.bat"]
results = spoofer.spoof_batch(files, reference_file="/bin/ls")
```

## Common Scenarios

### Scenario 1: Hide Payload File Age
```python
from timestamp_spoofer import spoof_to_reference

# Make payload appear as old as system binary
spoof_to_reference("/tmp/payload.exe", "/bin/ls")
```

### Scenario 2: Create File Family
```python
# Make multiple files appear to be from same time
spoofer.clone_timestamps("/bin/ls", [
    "/tmp/dll1.dll",
    "/tmp/dll2.dll",
    "/tmp/dll3.dll"
])
```

### Scenario 3: Random Recent File
```python
from datetime import datetime, timedelta

# Random date in last 30 days
now = datetime.now()
start = (now - timedelta(days=30)).timestamp()
end = now.timestamp()

spoofer.randomize_within_range("/tmp/file.txt", start, end)
```

### Scenario 4: Restore After Testing
```python
# Spoof
spoofer.spoof_to_match_file("/tmp/test.txt", "/bin/ls")

# ... do something ...

# Restore
spoofer.restore_timestamps("/tmp/test.txt")
```

## Convenience Functions

### Quick Match
```python
from timestamp_spoofer import spoof_to_reference
spoof_to_reference("/tmp/payload.vbs", "/bin/ls")
```

### Quick Date Set
```python
from timestamp_spoofer import spoof_to_date
from datetime import datetime

spoof_to_date("/tmp/file.txt", datetime(2023, 1, 1))
```

### Quick Batch
```python
from timestamp_spoofer import spoof_batch_files

spoof_batch_files([
    "/tmp/file1.txt",
    "/tmp/file2.txt"
], "/bin/ls")
```

## Check Timestamps

### View Before/After
```python
info = spoofer.spoof_to_match_file(target, reference)
print(f"Original: {datetime.fromtimestamp(info.original_mtime)}")
print(f"Spoofed: {info.spoofed_mtime}")
```

### Compare Files
```python
delta = spoofer.get_timestamp_delta(file1, file2)
print(f"Difference: {delta} seconds")
```

### Get Raw Timestamps
```python
mtime, atime, ctime = spoofer.get_file_timestamps("/tmp/file.txt")
```

## Time Offsets

### Add Days
```python
spoofer.spoof_with_delta(
    "/tmp/target.txt",
    "/tmp/reference.txt",
    days_delta=7
)
```

### Subtract Hours
```python
spoofer.spoof_with_delta(
    "/tmp/target.txt",
    "/tmp/reference.txt",
    hours_delta=-5
)
```

### Multiple Units
```python
spoofer.spoof_with_delta(
    "/tmp/target.txt",
    "/tmp/reference.txt",
    days_delta=3,
    hours_delta=2,
    minutes_delta=30
)
```

## System File Matching

### Match to System Binary
```python
from timestamp_spoofer import SystemFileTimestampMatcher

matcher = SystemFileTimestampMatcher()
info = matcher.match_to_system_binary("/tmp/disguised.exe")
```

### Match to System Library
```python
info = matcher.match_to_system_library("/tmp/fake.dll")
```

### Match to Config File
```python
info = matcher.match_to_config_file("/tmp/config")
```

## History Tracking

### View Changes
```python
history = spoofer.get_history()
for path, info in history.items():
    print(f"{path}: {info.original_mtime} -> {info.spoofed_mtime}")
```

### Clear History
```python
count = spoofer.clear_history()
print(f"Cleared {count} entries")
```

## Platform-Specific Notes

### Windows
```python
# Match to Windows system files
spoof_to_reference(
    "C:\\payload.exe",
    "C:\\Windows\\System32\\kernel32.dll"
)
```

### Linux
```python
# Match to Linux system files
spoof_to_reference("/tmp/payload.elf", "/bin/bash")
```

### macOS
```python
# Match to macOS system files
spoof_to_reference("/tmp/payload", "/usr/bin/python3")
```

## Error Handling

```python
try:
    info = spoofer.spoof_to_match_file(target, reference)
except FileNotFoundError as e:
    print(f"File not found: {e}")
except IOError as e:
    print(f"Could not modify timestamps: {e}")
```

## Tips & Tricks

1. **Stealth**: Use old system file timestamps for payloads
2. **Clustering**: Keep related files' timestamps close together
3. **Randomization**: Vary timestamps to avoid patterns
4. **History**: Track changes for later restoration
5. **Batch**: Spoof multiple files at once for efficiency

## One-Liners

```python
# Quick spoofing
spoofer.spoof_to_match_file("/tmp/payload.vbs", "/bin/ls")

# Quick restore
spoofer.restore_timestamps("/tmp/payload.vbs")

# Check if spoofed correctly
delta = spoofer.get_timestamp_delta("/tmp/payload.vbs", "/bin/ls")
print(f"Match: {abs(delta) < 1}")
```

## Running Tests

```bash
# Run unit tests
python3 -m unittest test_timestamp_spoofer -v

# Run examples
python3 timestamp_spoofer_examples.py
```

## Further Reading

See `TIMESTAMP_SPOOFER_DOCUMENTATION.md` for detailed API reference.
