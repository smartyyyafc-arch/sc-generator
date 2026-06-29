# Post-Installation Cleanup Handler Documentation

## Overview

The **Post-Installation Cleanup Handler** provides comprehensive post-installation cleanup functionality to securely remove installers, clear shell history, delete logs, clear caches, and remove temporary files. It's designed to eliminate installation traces and clean up system artifacts after application installation.

## Features

### Core Functionality
- **Installer Removal**: Securely delete installer files and directories
- **Shell History Clearing**: Remove history from bash, zsh, sh, fish, tcsh, and ksh
- **Command History Clearing**: Clear in-memory command history
- **Log Cleanup**: Remove installation-related log files
- **Cache Clearing**: Clean up installation cache directories
- **Temporary File Cleanup**: Remove recent temporary installation files
- **Recycle Bin Clearing**: Platform-specific trash/recycle bin clearing

### Security Features
- **Cryptographic Overwrite**: DoD 5220.22-M compliant multi-pass overwrite
- **Trace Removal**: Forensic cleanup of installation traces
- **Metadata Wiping**: Remove file timestamps and access information
- **Secure Deletion**: Optional secure deletion with configurable passes

### Reliability Features
- **Retry Logic**: Exponential backoff retry mechanism
- **Transaction Tracking**: Log all cleanup operations
- **Dry-Run Mode**: Preview cleanup operations without execution
- **Error Recovery**: Graceful error handling and continuation
- **Rollback Support**: Track and report failed operations

### Reporting Features
- **Detailed Statistics**: Track files deleted, histories cleared, etc.
- **Operation Logging**: Complete audit trail of all operations
- **Report Generation**: Export comprehensive cleanup reports
- **Success Metrics**: Calculate success rates and performance data

## Installation

### Node.js
```bash
npm install post-install-cleanup-handler
```

### Direct Usage
Simply copy the handler file to your project:
```bash
cp post-install-cleanup-handler.js your-project/
```

## Quick Start

### Basic Usage

```javascript
const PostInstallCleanupHandler = require('./post-install-cleanup-handler');

// Initialize handler
const handler = new PostInstallCleanupHandler({
  verbose: true,
  dryRun: false,
  profile: 'standard'
});

// Start tracking operations
handler.startTracking();

// Remove installer
await handler.removeInstaller('/path/to/installer.exe');

// Execute full cleanup
const result = await handler.executeCleanup();

console.log(`Cleanup completed: ${result.success}`);
console.log(`Files deleted: ${result.filesDeleted}`);
```

### Convenience Functions

```javascript
const { executePostInstallCleanup } = require('./post-install-cleanup-handler');

// One-line post-install cleanup
const { result, summary } = await executePostInstallCleanup('/tmp/installer.sh', {
  profile: 'standard'
});

console.log(`Profile: ${summary.profile}`);
console.log(`Success: ${result.success}`);
```

### Context Manager Pattern

```javascript
const { withCleanupContext } = require('./post-install-cleanup-handler');

const { result, cleanup, summary } = await withCleanupContext(
  async (handler) => {
    // Do post-install operations
    await handler.removeInstaller('/tmp/installer');
    return 'Installation complete';
  },
  { profile: 'standard' }
);

console.log(`Result: ${result}`);
console.log(`Cleanup: ${cleanup.success}`);
```

## Configuration Options

### Handler Options

```javascript
const handler = new PostInstallCleanupHandler({
  // Logging and Output
  verbose: false,                    // Enable detailed logging
  dryRun: false,                    // Preview without execution
  
  // Security Settings
  secureDelete: true,               // Use cryptographic overwrite
  overwritePasses: 3,               // Number of overwrite passes
  
  // Cleanup Components
  clearHistory: true,               // Clear shell history
  clearLogs: true,                 // Clear installation logs
  clearCache: true,                // Clear installation cache
  clearTemp: true,                 // Clear temporary files
  clearRecycleBin: true,           // Clear recycle bin/trash
  
  // Operation Settings
  maxRetries: 3,                    // Max retry attempts
  retryDelayMs: 100,               // Retry delay in milliseconds
  
  // Paths
  tempDir: os.tmpdir(),            // Temporary directory path
  homeDir: os.homedir(),           // Home directory path
  
  // Profile
  profile: 'standard'              // 'minimal', 'standard', or 'thorough'
});
```

## Cleanup Profiles

### Minimal Profile
- **Description**: Remove only installer and main logs
- **Features**:
  - Installer removal: Yes
  - Shell history clearing: No
  - Log clearing: Yes
  - Cache clearing: No
  - Temporary file clearing: No
  - Secure delete: No

```javascript
const handler = new PostInstallCleanupHandler({ profile: 'minimal' });
```

### Standard Profile (Default)
- **Description**: Remove installer, history, logs, and cache
- **Features**:
  - Installer removal: Yes
  - Shell history clearing: Yes
  - Log clearing: Yes
  - Cache clearing: Yes
  - Temporary file clearing: No
  - Secure delete: Yes (3-pass)

```javascript
const handler = new PostInstallCleanupHandler({ profile: 'standard' });
```

### Thorough Profile
- **Description**: Complete cleanup including temp files and forensic traces
- **Features**:
  - Installer removal: Yes
  - Shell history clearing: Yes
  - Log clearing: Yes
  - Cache clearing: Yes
  - Temporary file clearing: Yes
  - Secure delete: Yes (3-pass)

```javascript
const handler = new PostInstallCleanupHandler({ profile: 'thorough' });
```

## API Reference

### Constructor

```javascript
new PostInstallCleanupHandler(options)
```

Creates a new cleanup handler instance with optional configuration.

### Tracking Methods

#### `startTracking()`
Begin operation tracking.

```javascript
handler.startTracking();
```

#### `stopTracking()`
Stop operation tracking.

```javascript
handler.stopTracking();
```

#### `clearTracking()`
Clear all tracked operations.

```javascript
handler.clearTracking();
```

### Cleanup Methods

#### `removeInstaller(installerPath, options)`
Remove an installer file or directory with optional secure deletion.

```javascript
const removed = await handler.removeInstaller('/path/to/installer.exe');
```

**Parameters:**
- `installerPath` (string): Path to installer file or directory
- `options` (object, optional):
  - `secure` (boolean): Use secure deletion (default: from profile)

**Returns:** Boolean indicating success

#### `clearShellHistory()`
Clear shell history files from user home directory.

```javascript
const result = await handler.clearShellHistory();
```

**Clears:**
- `.bash_history`, `.bash_sessions`
- `.zsh_history`, `.zsh_sessions`
- `.sh_history`
- `.fish_history`
- `.history`, `.tcsh_history`, `.ksh_history`

**Returns:** Boolean indicating success

#### `clearCommandHistory()`
Clear in-memory command history (platform-specific).

```javascript
const result = await handler.clearCommandHistory();
```

**Returns:** Boolean indicating success

#### `clearInstallationLogs()`
Clear installation-related log files.

```javascript
const result = await handler.clearInstallationLogs();
```

**Returns:** Boolean indicating success

#### `clearCache()`
Clear installation cache directories.

```javascript
const result = await handler.clearCache();
```

**Returns:** Boolean indicating success

#### `clearTemporaryFiles()`
Clear recent temporary installation files.

```javascript
const result = await handler.clearTemporaryFiles();
```

**Returns:** Boolean indicating success

#### `clearRecycleBin()`
Clear system recycle bin/trash (platform-specific).

```javascript
const result = await handler.clearRecycleBin();
```

**Returns:** Boolean indicating success

#### `executeCleanup()`
Execute all pending cleanup operations based on profile.

```javascript
const result = await handler.executeCleanup();
```

**Returns:** Object with:
```javascript
{
  success: boolean,
  profile: string,
  filesDeleted: number,
  historiesCleared: number,
  totalTime: number,
  errors: array,
  summary: object
}
```

### Reporting Methods

#### `getOperations()`
Get all logged operations.

```javascript
const operations = handler.getOperations();
```

**Returns:** Array of operation entries

#### `getDeletedFiles()`
Get list of deleted files.

```javascript
const deleted = handler.getDeletedFiles();
```

**Returns:** Array of file objects with metadata

#### `getClearedHistories()`
Get list of cleared history files.

```javascript
const histories = handler.getClearedHistories();
```

**Returns:** Array of history file paths

#### `getFailedOperations()`
Get list of failed operations.

```javascript
const failed = handler.getFailedOperations();
```

**Returns:** Array of error entries

#### `getStatistics()`
Get cleanup statistics.

```javascript
const stats = handler.getStatistics();
```

**Returns:** Object with:
```javascript
{
  totalOperations: number,
  totalFilesDeleted: number,
  totalHistoriesCleared: number,
  totalOperationsFailed: number,
  successRate: number,
  profile: string,
  secureDeleteEnabled: boolean,
  overwritePasses: number
}
```

#### `getSummary()`
Get human-readable cleanup summary.

```javascript
const summary = handler.getSummary();
```

**Returns:** Object with:
```javascript
{
  title: string,
  timestamp: string,
  profile: string,
  profileDescription: string,
  filesDeleted: number,
  historiesCleared: number,
  operationsFailed: number,
  successRate: string,
  securityLevel: string
}
```

#### `exportReport()`
Export comprehensive cleanup report as JSON.

```javascript
const report = handler.exportReport();
```

**Returns:** Complete report object with all data

### Factory Functions

#### `initializeCleanupHandler(options)`
Initialize and return global cleanup handler.

```javascript
const handler = initializeCleanupHandler({ verbose: true });
```

#### `getCleanupHandler()`
Get global cleanup handler instance.

```javascript
const handler = getCleanupHandler();
```

#### `executePostInstallCleanup(installerPath, options)`
Execute complete post-install cleanup.

```javascript
const { result, report, summary } = await executePostInstallCleanup(
  '/path/to/installer',
  { profile: 'standard' }
);
```

#### `withCleanupContext(callback, options)`
Context manager for cleanup operations.

```javascript
const { result, cleanup, summary } = await withCleanupContext(
  async (handler) => {
    await handler.removeInstaller('/tmp/installer');
    return 'done';
  },
  { profile: 'standard' }
);
```

## Usage Examples

### Example 1: Basic Installer Removal
```javascript
const handler = new PostInstallCleanupHandler({ verbose: true });
handler.startTracking();

await handler.removeInstaller('/path/to/installer.sh');
const result = await handler.executeCleanup();

console.log(`Removed: ${result.filesDeleted} files`);
```

### Example 2: Dry-Run Mode
```javascript
const handler = new PostInstallCleanupHandler({
  verbose: true,
  dryRun: true  // Preview without execution
});

handler.startTracking();
await handler.removeInstaller('/tmp/installer.exe');
const result = await handler.executeCleanup();

// Files are not actually deleted
console.log('Dry run preview completed');
```

### Example 3: Custom Security Configuration
```javascript
const handler = new PostInstallCleanupHandler({
  verbose: true,
  secureDelete: true,
  overwritePasses: 7,  // High security
  maxRetries: 5,       // More resilient
  profile: 'thorough'
});

handler.startTracking();
const result = await handler.executeCleanup();
```

### Example 4: Error Handling
```javascript
const handler = new PostInstallCleanupHandler({
  verbose: true,
  maxRetries: 3,
  retryDelayMs: 200
});

handler.startTracking();

try {
  await handler.removeInstaller('/tmp/installer');
  const result = await handler.executeCleanup();
  
  if (!result.success) {
    const errors = handler.getFailedOperations();
    console.error('Some operations failed:', errors);
  }
} catch (error) {
  console.error('Cleanup error:', error);
}
```

### Example 5: Batch Cleanup
```javascript
const handler = new PostInstallCleanupHandler({ verbose: true });
handler.startTracking();

const installers = [
  '/opt/app/installer.sh',
  '/tmp/setup.exe',
  '/var/cache/app-installer'
];

for (const installer of installers) {
  await handler.removeInstaller(installer);
}

const result = await handler.executeCleanup();
const stats = handler.getStatistics();

console.log(`Cleanup completed: ${stats.totalFilesDeleted} files deleted`);
```

## Platform Support

### Windows
- Recycle bin clearing via `cmd /c rd`
- PowerShell history clearing
- MSI installer removal

### macOS
- Trash clearing via `rm`
- Bash/Zsh history files

### Linux
- Linux trash clearing via `rm`
- Multiple shell history file support

## Security Considerations

### Secure Deletion
The handler uses DoD 5220.22-M compliant multi-pass overwrite:
1. **Pass 1**: Overwrite with zeros (0x00)
2. **Pass 2**: Overwrite with ones (0xFF)
3. **Pass 3**: Overwrite with random data

### Metadata Wiping
- File timestamps reset to epoch
- Access times cleared
- File permissions may be reset

### Trace Removal
- Recycle bin/trash cleared
- Installation logs deleted
- Cache entries removed

## Error Handling

The handler includes comprehensive error handling:

```javascript
const handler = new PostInstallCleanupHandler();
handler.startTracking();

try {
  const result = await handler.executeCleanup();
  
  if (!result.success) {
    result.errors.forEach(error => {
      console.error(`Cleanup error: ${error}`);
    });
  }
} catch (error) {
  console.error(`Fatal error: ${error.message}`);
}

// Check individual operation failures
const failed = handler.getFailedOperations();
console.log(`${failed.length} operations failed`);
```

## Best Practices

1. **Use Dry-Run First**: Always test with `dryRun: true` before actual cleanup
2. **Enable Verbose Logging**: Use `verbose: true` during development
3. **Handle Errors**: Always check result.success and handle errors
4. **Profile Selection**: Choose appropriate profile for your use case
5. **Track Operations**: Keep tracking enabled for audit trails
6. **Export Reports**: Generate reports for compliance/audit purposes
7. **Verify Cleanup**: Check statistics to ensure cleanup completed

## Performance Considerations

- **Multi-Pass Overwrite**: Slower but more secure (standard: 3 passes)
- **Recursive Directory Deletion**: May be slow for large directories
- **Shell History Clearing**: Minimal performance impact
- **Cache Clearing**: May take time on large cache directories

## Troubleshooting

### Issue: Permission Denied Errors
**Solution:** Run with appropriate privileges
```bash
sudo node your-script.js
```

### Issue: Recycle Bin Not Clearing
**Solution:** May require admin rights on Windows
```bash
# Run command prompt as administrator
```

### Issue: Cleanup Taking Too Long
**Solution:** Reduce overwrite passes or skip thorough cleanup
```javascript
const handler = new PostInstallCleanupHandler({
  overwritePasses: 1,  // Faster, less secure
  profile: 'standard'   // Skip temp file cleanup
});
```

### Issue: History Files Not Found
**Solution:** Verify home directory path configuration
```javascript
const handler = new PostInstallCleanupHandler({
  homeDir: '/home/username'  // Explicit path
});
```

## Testing

Run the test suite:

```bash
npm test post-install-cleanup-handler.test.js
```

Test examples:

```bash
node post-install-cleanup-examples.js
```

## API Summary

| Method | Description | Returns |
|--------|-------------|---------|
| `removeInstaller()` | Remove installer file/directory | Promise<boolean> |
| `clearShellHistory()` | Clear shell history files | Promise<boolean> |
| `clearCommandHistory()` | Clear in-memory history | Promise<boolean> |
| `clearInstallationLogs()` | Clear log files | Promise<boolean> |
| `clearCache()` | Clear cache directories | Promise<boolean> |
| `clearTemporaryFiles()` | Clear temporary files | Promise<boolean> |
| `clearRecycleBin()` | Clear trash/recycle bin | Promise<boolean> |
| `executeCleanup()` | Execute all cleanup | Promise<Object> |
| `getStatistics()` | Get cleanup stats | Object |
| `getSummary()` | Get human summary | Object |
| `exportReport()` | Export full report | Object |

## License

This module is part of the sc-generator project.

## Support

For issues or questions, refer to the examples or documentation files.
