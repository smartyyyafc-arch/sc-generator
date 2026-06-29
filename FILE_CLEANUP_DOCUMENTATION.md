# File Cleanup Handler with Secure Deletion

## Overview

The `FileCleanupHandler` provides secure file deletion capabilities with comprehensive trace removal. It implements industry-standard secure deletion methods including multi-pass overwriting, recycle bin clearing, and metadata removal.

## Features

### Core Capabilities
- **Multi-Pass Overwrite**: DoD 5220.22-M standard overwrite (3 passes by default: zeros, ones, random)
- **Recycle Bin Clearing**: Platform-specific trash/recycle bin cleanup (Windows, macOS, Linux)
- **Metadata Removal**: Timestamp and file metadata wiping
- **Trace Deletion**: Complete removal of file deletion traces
- **Cross-Platform Support**: Windows, macOS, and Linux compatibility
- **Dry-Run Mode**: Safe preview of operations before execution
- **Transaction Tracking**: Full operation logging and audit trails
- **Batch Operations**: Efficient deletion of multiple files
- **Retry Logic**: Automatic retry with exponential backoff
- **Context Manager**: Safe cleanup context management

## Installation

### JavaScript/Node.js
```bash
npm install # or copy file-cleanup-handler.js to your project
```

### TypeScript
```bash
npm install --save-dev typescript
# or copy file-cleanup-handler.ts to your project
```

## Usage

### Basic Usage

#### Single File Secure Delete
```javascript
const FileCleanupHandler = require('./file-cleanup-handler');

const handler = new FileCleanupHandler({ verbose: true });
handler.startTracking();

const success = await handler.secureDelete('/path/to/sensitive/file.txt');
const result = await handler.executeCleanup();

console.log('Cleanup result:', result);
```

#### Using Convenience Function
```javascript
const { secureDeleteFile } = require('./file-cleanup-handler');

const success = await secureDeleteFile('/path/to/file.txt', {
  verbose: true,
  overwritePasses: 3,
  clearRecycleBin: true,
});
```

### Batch Operations

#### Delete Multiple Files
```javascript
const { secureDeleteFiles } = require('./file-cleanup-handler');

const files = [
  '/path/to/file1.txt',
  '/path/to/file2.txt',
  '/path/to/file3.txt',
];

const result = await secureDeleteFiles(files, {
  verbose: true,
  overwritePasses: 3,
});

console.log(`Deleted: ${result.success}/${result.total} files`);
```

### Advanced Configuration

#### Custom Handler with Options
```javascript
const handler = new FileCleanupHandler({
  verbose: true,                // Enable detailed logging
  dryRun: true,                 // Preview operations without executing
  overwritePasses: 3,           // Number of overwrite passes
  clearRecycleBin: true,        // Clear system recycle bin
  wipeMetadata: true,           // Remove file metadata
  trackOperations: true,        // Track all operations
  maxRetries: 3,                // Retry failed operations
  retryDelayMs: 100,            // Delay between retries (exponential backoff)
  tempDir: '/tmp',              // Temporary directory
});

handler.startTracking();

// Perform deletions...
const deleted = await handler.secureDelete('/path/to/file.txt');

// Execute cleanup
const result = await handler.executeCleanup();
```

### Context Manager

#### Safe Cleanup Context
```javascript
const { withCleanupContext } = require('./file-cleanup-handler');

const { result, cleanup, report } = await withCleanupContext(
  async (handler) => {
    // All file operations are tracked
    await handler.secureDelete('/path/to/file1.txt');
    await handler.secureDelete('/path/to/file2.txt');
    
    // Cleanup is automatic at the end
    return 'operation completed';
  },
  { verbose: true, dryRun: false }
);

console.log('Result:', result);
console.log('Cleanup:', cleanup);
console.log('Report:', report);
```

## API Reference

### Class: FileCleanupHandler

#### Constructor
```javascript
new FileCleanupHandler(options?: FileCleanupOptions)
```

#### Methods

##### `startTracking(): void`
Start tracking file operations
```javascript
handler.startTracking();
```

##### `stopTracking(): void`
Stop tracking file operations
```javascript
handler.stopTracking();
```

##### `deleteFile(filePath: string, options?: {}): Promise<boolean>`
Delete a file with optional overwrite
```javascript
const success = await handler.deleteFile('/path/to/file.txt', {
  secure: true,
  overwritePasses: 3,
});
```

##### `secureDelete(filePath: string, options?: {}): Promise<boolean>`
Securely delete a file with all traces
```javascript
const success = await handler.secureDelete('/path/to/file.txt');
```

##### `secureDeleteBatch(filePaths: string[], options?: {}): Promise<BatchDeleteResult>`
Delete multiple files securely
```javascript
const result = await handler.secureDeleteBatch([
  '/path/to/file1.txt',
  '/path/to/file2.txt',
]);
```

##### `overwriteFileContents(filePath: string, passes?: number): Promise<boolean>`
Overwrite file contents without deletion
```javascript
await handler.overwriteFileContents('/path/to/file.txt', 3);
```

##### `clearRecycleBin(): Promise<boolean>`
Clear system recycle bin / trash
```javascript
await handler.clearRecycleBin();
```

##### `removeFileMetadata(filePath: string): Promise<boolean>`
Remove file metadata (timestamps, etc.)
```javascript
await handler.removeFileMetadata('/path/to/file.txt');
```

##### `executeCleanup(): Promise<CleanupResult>`
Execute all tracked cleanup operations
```javascript
const result = await handler.executeCleanup();
```

##### `getStatistics(): Statistics`
Get cleanup statistics
```javascript
const stats = handler.getStatistics();
console.log(`Success rate: ${stats.successRate * 100}%`);
```

##### `getSummary(): CleanupSummary`
Get human-readable cleanup summary
```javascript
const summary = handler.getSummary();
console.log(summary);
```

##### `exportReport(): CleanupReport`
Export comprehensive cleanup report
```javascript
const report = handler.exportReport();
fs.writeFileSync('cleanup_report.json', JSON.stringify(report, null, 2));
```

##### `getOperations(): OperationEntry[]`
Get all logged operations
```javascript
const operations = handler.getOperations();
```

##### `getDeletedFiles(): DeletedFileEntry[]`
Get list of deleted files
```javascript
const deleted = handler.getDeletedFiles();
```

##### `getFailedOperations(): FailedOperationEntry[]`
Get list of failed operations
```javascript
const failed = handler.getFailedOperations();
```

##### `clearTracking(): void`
Clear all tracking data
```javascript
handler.clearTracking();
```

## Configuration Options

```javascript
interface FileCleanupOptions {
  verbose?: boolean;           // Enable detailed logging (default: false)
  dryRun?: boolean;            // Preview without executing (default: false)
  overwritePasses?: number;    // Overwrite passes (default: 3)
  clearRecycleBin?: boolean;   // Clear recycle bin (default: true)
  wipeMetadata?: boolean;      // Wipe file metadata (default: true)
  trackOperations?: boolean;   // Track operations (default: true)
  maxRetries?: number;         // Max retry attempts (default: 3)
  retryDelayMs?: number;       // Retry delay in ms (default: 100)
  tempDir?: string;            // Temporary directory (default: os.tmpdir())
}
```

## Security Features

### Overwrite Standards
The handler implements DoD 5220.22-M standard secure deletion:
- **Pass 1**: Overwrite with zeros (0x00)
- **Pass 2**: Overwrite with ones (0xff)
- **Pass 3**: Overwrite with cryptographic random data

### Metadata Removal
- Resets file access time to epoch (1970-01-01)
- Resets file modification time to epoch
- Platform-specific ACL clearing attempts

### Recycle Bin Clearing
- **Windows**: Clears `$Recycle.bin` directory
- **macOS**: Clears `~/.Trash` directory
- **Linux**: Clears `~/.local/share/Trash` and `~/.Trash` directories

### Error Handling
- Automatic retry with exponential backoff
- Comprehensive error logging
- Graceful degradation if some operations fail
- Transaction-like behavior with rollback support

## Examples

### Example 1: Secure Delete with Verification
```javascript
const handler = new FileCleanupHandler({ verbose: true });
handler.startTracking();

const filePath = '/path/to/sensitive.txt';
console.log('File exists before:', fs.existsSync(filePath));

const deleted = await handler.secureDelete(filePath);
const result = await handler.executeCleanup();

console.log('File exists after:', fs.existsSync(filePath));
console.log('Deletion result:', result);
```

### Example 2: Batch Cleanup with Reporting
```javascript
const files = [
  '/path/to/temp1.tmp',
  '/path/to/temp2.tmp',
  '/path/to/cache.dat',
];

const handler = new FileCleanupHandler({
  verbose: false,
  overwritePasses: 5, // Higher security
});

handler.startTracking();
const results = await handler.secureDeleteBatch(files);

const report = handler.exportReport();
fs.writeFileSync(
  'cleanup_report.json',
  JSON.stringify(report, null, 2)
);

console.log('Cleanup report saved');
```

### Example 3: Context Manager with Error Handling
```javascript
try {
  const { result, cleanup, report } = await withCleanupContext(
    async (handler) => {
      const files = await getTemporaryFiles();
      await handler.secureDeleteBatch(files);
      return files.length;
    },
    { verbose: true, dryRun: false }
  );
  
  console.log(`Cleaned up ${result} files`);
  if (!cleanup.success) {
    console.warn('Some files could not be deleted');
  }
} catch (error) {
  console.error('Cleanup failed:', error);
}
```

### Example 4: Dry-Run Mode for Safety
```javascript
const handler = new FileCleanupHandler({
  verbose: true,
  dryRun: true,  // Preview only
  overwritePasses: 3,
});

handler.startTracking();

// These operations will be logged but not executed
await handler.secureDeleteBatch([
  '/path/to/file1.txt',
  '/path/to/file2.txt',
]);

// Check what would happen
const summary = handler.getSummary();
console.log('Preview:', summary);

// If satisfied, switch to actual deletion
handler.options.dryRun = false;
const result = await handler.executeCleanup();
```

## Differences from Standard File Deletion

### Standard `fs.unlink()`
- File data remains on disk
- Recoverable with forensic tools
- Fast but not secure
- No metadata cleanup

### FileCleanupHandler Secure Delete
- File data overwritten multiple times
- Unrecoverable with standard forensic tools
- Includes metadata removal
- Recycle bin clearing
- Trace removal
- Transaction tracking

## Performance Considerations

### Overwrite Passes
- **1 Pass**: Fast, minimal security
- **3 Passes**: Balanced (default)
- **5+ Passes**: Slower but higher security

### File Size Impact
- Larger files take longer to overwrite
- Memory-efficient streaming overwrite
- Batch operations process files sequentially

### Recycle Bin Clearing
- Platform-dependent performance
- May require elevated privileges (Windows)
- Non-critical operation failures are graceful

## Troubleshooting

### Permission Denied
```javascript
// May need elevated privileges
// Windows: Run as Administrator
// Linux/macOS: Use with sudo or check file permissions
```

### Recycle Bin Clear Fails
```javascript
// Non-critical - operation continues
// Check file permissions in trash directory
// Windows may require admin rights
```

### File Still Locked
```javascript
// File may be open in another process
// Close all handles to the file first
// Handler will retry up to `maxRetries` times
```

## Best Practices

1. **Use Dry-Run First**: Always test with `dryRun: true` before executing
2. **Verify Permissions**: Ensure write access to files and trash directories
3. **Backup Data**: Create backups before secure deletion
4. **Monitor Operations**: Use verbose mode during initial deployment
5. **Review Reports**: Export and review cleanup reports
6. **Handle Errors**: Check `result.success` and `result.errors`
7. **Close Files**: Ensure no handles are open before deletion
8. **Test Thoroughly**: Verify secure deletion with forensic tools

## Platform Specific Notes

### Windows
- Requires Windows 7 or later
- `$Recycle.bin` clearing may require administrator privileges
- File metadata removal is reliable
- Alternative: Use CCleaner for additional cleanup

### macOS
- Requires macOS 10.12 or later
- Trash clearing uses `rm -rf ~/.Trash/*`
- File metadata removal is reliable
- Alternative: Use Secure Empty Trash (built-in)

### Linux
- Supports various desktop environments
- Trash clearing checks multiple trash directories
- File metadata removal is reliable
- Alternative: Use `shred` or `wipe` utilities

## Testing

### Run Test Suite
```bash
node file-cleanup-handler.test.js
```

### Test Results
All 10 tests should pass:
1. Basic File Deletion
2. Secure Overwrite
3. Batch File Deletion
4. Statistics Tracking
5. Operation Logging
6. File Not Found Handling
7. Context Manager
8. Recycle Bin Clearing
9. Export Report
10. Convenience Functions

## Security Disclaimer

This handler implements standard secure deletion practices. However:

1. **Solid-State Drives (SSDs)**: Modern SSDs use wear-leveling, making secure deletion difficult
2. **Full-Disk Encryption**: Consider using FDE instead of file-level deletion
3. **Recovery Services**: Professional data recovery may still be possible
4. **Legal Compliance**: Check local regulations for data deletion requirements
5. **Verification**: Use forensic tools to verify deletion in critical applications

## License

This module is part of the SC Generator project.

## Contributing

Contributions, bug reports, and feature requests are welcome.

## Support

For issues or questions, refer to the project documentation or create an issue.
