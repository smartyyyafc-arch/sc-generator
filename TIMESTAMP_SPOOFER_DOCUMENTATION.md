# Timestamp Spoofer - File Timestamp Spoofing Module

## Overview

The Timestamp Spoofer module provides comprehensive file timestamp manipulation capabilities to match system files. This is useful for security research, penetration testing, and payload delivery scenarios where file metadata needs to be inconspicuous.

**Warning**: This tool is for authorized security testing and research only. Unauthorized modification of file timestamps may violate local laws.

## Features

- **Match Timestamps**: Copy timestamps from reference files to target files
- **Specific Timestamps**: Set file timestamps to specific Unix epoch times or datetime objects
- **Time Deltas**: Apply relative time adjustments (days, hours, minutes)
- **Batch Operations**: Spoof multiple files efficiently
- **Clone Timestamps**: Duplicate timestamps to multiple files simultaneously
- **Random Range**: Randomize timestamps within a date range
- **History Tracking**: Track all timestamp modifications with restore capability
- **System File Matching**: Match to standard system file timestamps
- **Selective Spoofing**: Modify only mtime, atime, or both

## Installation

The module is self-contained in `timestamp_spoofer.py` with only standard library dependencies.

```python
from timestamp_spoofer import TimestampSpoofer, SystemFileTimestampMatcher
```

## Core Classes

### TimestampSpoofer

Main class for all timestamp manipulation operations.

```python
from timestamp_spoofer import TimestampSpoofer

spoofer = TimestampSpoofer()
```

#### Methods

##### `get_file_timestamps(file_path: str) -> Tuple[float, float, float]`

Get current file timestamps as Unix epoch times.

```python
mtime, atime, ctime = spoofer.get_file_timestamps("/path/to/file.txt")
```

**Returns**: Tuple of (modification_time, access_time, change_time)

##### `get_file_timestamps_dt(file_path: str) -> Tuple[str, str, str]`

Get file timestamps as ISO format datetime strings.

```python
mtime_str, atime_str, ctime_str = spoofer.get_file_timestamps_dt("/path/to/file.txt")
# Returns: ('2023-06-15T14:30:00', '2023-06-15T14:30:00', '2023-06-15T14:30:00')
```

##### `spoof_to_match_file(target_file: str, reference_file: str, spoof_atime: bool = True, spoof_mtime: bool = True) -> TimestampInfo`

Copy timestamps from reference file to target file.

```python
info = spoofer.spoof_to_match_file("/tmp/payload.vbs", "/bin/ls")
print(f"Spoofed: {info.mtime_dt}")
```

**Args**:
- `target_file`: File to modify timestamps on
- `reference_file`: File to copy timestamps from
- `spoof_atime`: Also modify access time (default: True)
- `spoof_mtime`: Also modify modification time (default: True)

**Returns**: TimestampInfo object with before/after timestamps

##### `spoof_to_timestamp(file_path: str, target_timestamp: float, spoof_atime: bool = True, spoof_mtime: bool = True) -> TimestampInfo`

Set file timestamps to specific Unix epoch time.

```python
# Set to January 1, 2020
timestamp = datetime(2020, 1, 1).timestamp()
info = spoofer.spoof_to_timestamp("/tmp/old_file.txt", timestamp)
```

**Args**:
- `file_path`: File to modify
- `target_timestamp`: Unix epoch timestamp
- `spoof_atime`: Also modify access time
- `spoof_mtime`: Also modify modification time

**Returns**: TimestampInfo object

##### `spoof_to_datetime(file_path: str, target_datetime: datetime, spoof_atime: bool = True, spoof_mtime: bool = True) -> TimestampInfo`

Set file timestamps to specific datetime.

```python
from datetime import datetime

target = datetime(2019, 6, 15, 14, 30, 0)
info = spoofer.spoof_to_datetime("/tmp/payload.bat", target)
```

**Args**:
- `file_path`: File to modify
- `target_datetime`: Target datetime object
- `spoof_atime`: Also modify access time
- `spoof_mtime`: Also modify modification time

**Returns**: TimestampInfo object

##### `spoof_with_delta(target_file: str, reference_file: str, days_delta: int = 0, hours_delta: int = 0, minutes_delta: int = 0) -> TimestampInfo`

Spoof target file to match reference file plus/minus time delta.

```python
# Spoof to 2 weeks after reference file
info = spoofer.spoof_with_delta(
    "/tmp/payload.ps1",
    "/etc/passwd",
    days_delta=14
)
```

**Args**:
- `target_file`: File to modify
- `reference_file`: File to base timestamps on
- `days_delta`: Days to add/subtract
- `hours_delta`: Hours to add/subtract
- `minutes_delta`: Minutes to add/subtract

**Returns**: TimestampInfo object

##### `randomize_within_range(file_path: str, start_timestamp: float, end_timestamp: float) -> TimestampInfo`

Set file timestamp to random value within date range.

```python
start = datetime(2022, 1, 1).timestamp()
end = datetime(2022, 12, 31).timestamp()
info = spoofer.randomize_within_range("/tmp/random.txt", start, end)
```

**Args**:
- `file_path`: File to modify
- `start_timestamp`: Start of range (Unix epoch)
- `end_timestamp`: End of range (Unix epoch)

**Returns**: TimestampInfo object

##### `spoof_batch(file_paths: List[str], reference_file: str = None, target_timestamp: float = None) -> Dict[str, TimestampInfo]`

Spoof timestamps for multiple files.

```python
files = ["/tmp/payload1.vbs", "/tmp/payload2.bat", "/tmp/payload3.ps1"]
results = spoofer.spoof_batch(files, reference_file="/bin/ls")

for file_path, info in results.items():
    if info:
        print(f"{file_path}: {info.mtime_dt}")
```

**Args**:
- `file_paths`: List of files to modify
- `reference_file`: File to copy timestamps from
- `target_timestamp`: Unix epoch timestamp (used if reference_file is None)

**Returns**: Dictionary mapping file paths to TimestampInfo

##### `clone_timestamps(source_file: str, target_files: List[str]) -> Dict[str, TimestampInfo]`

Clone timestamps from source file to multiple target files.

```python
source = "/bin/ls"
targets = ["/tmp/dll1.dll", "/tmp/dll2.dll", "/tmp/dll3.dll"]
results = spoofer.clone_timestamps(source, targets)
```

**Args**:
- `source_file`: File to copy timestamps from
- `target_files`: Files to apply timestamps to

**Returns**: Dictionary mapping target files to TimestampInfo

##### `get_timestamp_delta(file1: str, file2: str) -> float`

Calculate time difference between two files in seconds.

```python
delta = spoofer.get_timestamp_delta("/tmp/file1.txt", "/tmp/file2.txt")
print(f"Delta: {delta} seconds ({delta / 86400} days)")
```

**Args**:
- `file1`: First file
- `file2`: Second file

**Returns**: Time difference in seconds (file1 - file2)

##### `restore_timestamps(file_path: str) -> bool`

Restore file to original timestamps from history.

```python
success = spoofer.restore_timestamps("/tmp/payload.vbs")
```

**Args**:
- `file_path`: File to restore

**Returns**: True if restoration successful

##### `get_history() -> Dict[str, TimestampInfo]`

Get timestamp spoofing history.

```python
history = spoofer.get_history()
for file_path, info in history.items():
    print(f"{file_path}: original={info.original_mtime}, spoofed={info.spoofed_mtime}")
```

**Returns**: Dictionary of file paths to TimestampInfo

##### `clear_history() -> int`

Clear timestamp history.

```python
cleared_count = spoofer.clear_history()
print(f"Cleared {cleared_count} history entries")
```

**Returns**: Number of entries cleared

### SystemFileTimestampMatcher

Convenience class for matching files to system file timestamps.

```python
from timestamp_spoofer import SystemFileTimestampMatcher

matcher = SystemFileTimestampMatcher()
```

#### Methods

##### `match_to_system_binary(target_file: str) -> TimestampInfo`

Make file appear as system binary by matching timestamps.

```python
info = matcher.match_to_system_binary("/tmp/disguised.exe")
```

##### `match_to_system_library(target_file: str) -> TimestampInfo`

Make file appear as system library.

```python
info = matcher.match_to_system_library("/tmp/fake.dll")
```

##### `match_to_config_file(target_file: str) -> TimestampInfo`

Make file appear as system config file.

```python
info = matcher.match_to_config_file("/tmp/config_fake")
```

##### `get_spoofer() -> TimestampSpoofer`

Get underlying spoofer instance.

```python
spoofer = matcher.get_spoofer()
```

### TimestampInfo (Data Class)

Stores timestamp information before and after spoofing.

```python
@dataclass
class TimestampInfo:
    file_path: str
    original_mtime: float           # Original modification time (Unix epoch)
    original_atime: float           # Original access time (Unix epoch)
    original_ctime: float           # Original change time (Unix epoch)
    spoofed_mtime: float            # New modification time (Unix epoch)
    spoofed_atime: float            # New access time (Unix epoch)
    spoofed_ctime: float            # New change time (Unix epoch)
    mtime_dt: str                   # Human readable modification time (ISO format)
    atime_dt: str                   # Human readable access time (ISO format)
    ctime_dt: str                   # Human readable change time (ISO format)
    spoof_success: bool             # Whether spoofing was successful
```

## Convenience Functions

Simplified functions for common operations:

### `spoof_to_reference(target_file: str, reference_file: str) -> TimestampInfo`

Quickly match target to reference file.

```python
from timestamp_spoofer import spoof_to_reference

info = spoof_to_reference("/tmp/payload.vbs", "/bin/ls")
```

### `spoof_to_date(file_path: str, target_date: datetime) -> TimestampInfo`

Quickly set file to specific datetime.

```python
from timestamp_spoofer import spoof_to_date
from datetime import datetime

target = datetime(2023, 1, 15, 10, 30, 0)
info = spoof_to_date("/tmp/file.txt", target)
```

### `spoof_batch_files(file_paths: List[str], reference_file: str) -> Dict[str, TimestampInfo]`

Spoof multiple files to match reference.

```python
from timestamp_spoofer import spoof_batch_files

files = ["/tmp/f1.txt", "/tmp/f2.txt", "/tmp/f3.txt"]
results = spoof_batch_files(files, "/bin/ls")
```

## Usage Examples

### Example 1: Basic Timestamp Spoofing

Make a payload file match a system file's timestamp:

```python
from timestamp_spoofer import TimestampSpoofer

spoofer = TimestampSpoofer()
info = spoofer.spoof_to_match_file("/tmp/payload.vbs", "/bin/ls")
print(f"Original: {info.mtime_dt}")
print(f"Spoofed: {info.mtime_dt}")
print(f"Success: {info.spoof_success}")
```

### Example 2: Spoof to Specific Date

Make file appear from specific point in time:

```python
from datetime import datetime
from timestamp_spoofer import spoof_to_date

target_date = datetime(2020, 1, 1, 0, 0, 0)
info = spoof_to_date("/tmp/old_payload.bat", target_date)
```

### Example 3: Batch Spoofing

Spoof multiple payload files at once:

```python
from timestamp_spoofer import spoof_batch_files

payloads = [
    "/tmp/payload1.ps1",
    "/tmp/payload2.vbs",
    "/tmp/payload3.bat"
]

results = spoof_batch_files(payloads, "/etc/passwd")
for file_path, info in results.items():
    if info:
        print(f"{file_path}: {info.mtime_dt}")
```

### Example 4: Clone Timestamps

Make multiple files appear to be from same time period:

```python
from timestamp_spoofer import TimestampSpoofer

spoofer = TimestampSpoofer()

# Clone from system DLL to payload files
source = "/System/Library/CoreServices/Finder.app"  # macOS
targets = ["/tmp/dll1.dll", "/tmp/dll2.dll"]

results = spoofer.clone_timestamps(source, targets)
```

### Example 5: Time Delta

Create file that appears to be modified after reference:

```python
from timestamp_spoofer import TimestampSpoofer

spoofer = TimestampSpoofer()

# Make payload appear 3 days after system file
info = spoofer.spoof_with_delta(
    "/tmp/payload.exe",
    "/Windows/System32/kernel32.dll",
    days_delta=3
)
```

### Example 6: Random Date Range

Randomize file timestamp within date range:

```python
from datetime import datetime
from timestamp_spoofer import TimestampSpoofer

spoofer = TimestampSpoofer()

# Random date in 2022
start = datetime(2022, 1, 1).timestamp()
end = datetime(2022, 12, 31).timestamp()

info = spoofer.randomize_within_range("/tmp/payload.txt", start, end)
```

### Example 7: Restore Original

Revert file to original timestamps after spoofing:

```python
from timestamp_spoofer import TimestampSpoofer

spoofer = TimestampSpoofer()

# Spoof
info = spoofer.spoof_to_timestamp("/tmp/file.txt", 1609459200)  # 2021-01-01

# ... do something ...

# Restore original
spoofer.restore_timestamps("/tmp/file.txt")
```

### Example 8: Track History

View all timestamp modifications:

```python
from timestamp_spoofer import TimestampSpoofer

spoofer = TimestampSpoofer()

# Perform multiple spoofing operations
spoofer.spoof_to_match_file("/tmp/file1.txt", "/bin/ls")
spoofer.spoof_to_match_file("/tmp/file2.txt", "/usr/bin/python3")

# Get history
history = spoofer.get_history()
for file_path, info in history.items():
    print(f"{file_path}:")
    print(f"  Original: {info.original_mtime}")
    print(f"  Spoofed:  {info.spoofed_mtime}")

# Clear history
count = spoofer.clear_history()
```

## Security Considerations

### Timestamp Consistency

When spoofing file timestamps:

1. **Consistency**: Spoofed files should have timestamps consistent with their supposed origin
2. **Clustering**: Related files (DLLs, drivers) should have similar timestamps
3. **OS Patterns**: Different OS versions have typical file age patterns

### Windows Patterns

- Windows XP files: Typically 2001-2006
- Windows Vista: 2006-2009
- Windows 7: 2009-2015
- Windows 10: 2015-present
- System DLLs: Usually very old (from OS installation)

### Linux Patterns

- System binaries: Vary by distribution, typically several years old
- Configuration files: Often older, updated infrequently
- User files: Recent (last few years)

## Testing

Run the test suite:

```bash
python3 -m unittest test_timestamp_spoofer -v
```

Run examples:

```bash
python3 timestamp_spoofer_examples.py
```

## API Reference Summary

| Method | Purpose | Returns |
|--------|---------|---------|
| `get_file_timestamps()` | Get current timestamps | (mtime, atime, ctime) |
| `spoof_to_match_file()` | Copy from reference | TimestampInfo |
| `spoof_to_timestamp()` | Set specific Unix time | TimestampInfo |
| `spoof_to_datetime()` | Set specific datetime | TimestampInfo |
| `spoof_with_delta()` | Apply time offset | TimestampInfo |
| `randomize_within_range()` | Random in range | TimestampInfo |
| `spoof_batch()` | Multiple files | Dict[str, TimestampInfo] |
| `clone_timestamps()` | Clone to multiple | Dict[str, TimestampInfo] |
| `get_timestamp_delta()` | Compare timestamps | float (seconds) |
| `restore_timestamps()` | Revert changes | bool |
| `get_history()` | View all changes | Dict[str, TimestampInfo] |
| `clear_history()` | Clear records | int (count) |

## Platform Support

- **Linux**: Full support using os.utime()
- **macOS**: Full support using os.utime()
- **Windows**: Full support using os.utime() (may require admin for system files)

## Limitations

- Change time (ctime) cannot be directly modified on most filesystems
- Some filesystems have limited timestamp resolution
- Network filesystems may have sync delays
- Admin/root privileges may be required for system files

## License

For authorized security research and testing only.
