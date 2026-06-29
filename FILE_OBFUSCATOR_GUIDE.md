# File Obfuscator - Advanced File Obfuscation Techniques

## Overview

The File Obfuscator is a comprehensive Node.js tool that implements multiple file obfuscation strategies to hide, obscure, and protect sensitive files. It combines various techniques to make file detection, identification, and analysis difficult.

## Features

### 1. Alternate Data Streams (ADS)
- **Platform**: Windows NTFS only
- **Technique**: Stores hidden data in NTFS alternate data streams
- **Advantage**: Files are invisible to standard directory listings
- **Access**: Requires direct ADS syntax (e.g., `file.txt:stream:$DATA`)
- **Use Case**: Hiding malicious scripts or sensitive data in plain sight

```javascript
const obfuscator = new FileObfuscator({ useADS: true });
// Creates file:FileName:Hidden:$DATA alternate stream
```

### 2. Mixed Case Names
- **Cross-Platform**: Yes
- **Technique**: Randomizes file name case combinations
- **Advantage**: Confuses case-sensitive/insensitive lookups
- **Example**: `config.txt` → `CoNfIg.txt`
- **Use Case**: Evading simple string matching and pattern detection

```javascript
const obfuscator = new FileObfuscator({ useMixedCase: true });
// Original: important_file.exe
// Obfuscated: ImPoRtAnT_FiLe.exe
```

### 3. File Attributes
- **Windows**: Hidden (+h) and System (+s) attributes
- **Unix/Linux**: Dot-prefix naming (`.filename`)
- **Advantage**: Files are hidden from default directory views
- **Recovery**: Requires specific flags to unhide (`attrib -h -s` or `ls -a`)

```javascript
const obfuscator = new FileObfuscator({ useAttributes: true });
// Windows: attrib +h +s filename.txt
// Linux: .filename.txt
```

### 4. Metadata Manipulation
- **Technique**: Spoofs file timestamps (creation, modification, access)
- **Advantage**: Obscures when file was actually created/modified
- **Example**: Sets all timestamps to 2020-01-01
- **Detection**: Forensic analysis can still reveal file content metadata

```javascript
const obfuscator = new FileObfuscator({ useMetadata: true });
// Modifies atime, mtime to fake timestamps
```

### 5. Deep Nesting
- **Technique**: Creates deeply nested directory structures
- **Depth**: Configurable (default 6 levels)
- **Advantage**: Makes file discovery by tools difficult
- **Performance**: May slow down antivirus scans
- **Directory Depth**: `d1234/d5678/d9abc/d1def/d2ghi/d3jkl/`

```javascript
const obfuscator = new FileObfuscator({ useNesting: true });
// Creates 6-level deep nested directories
```

### 6. Special Characters
- **Technique**: Embeds zero-width Unicode characters in filenames
- **Characters**: Zero-width space, zero-width joiner, etc.
- **Advantage**: Files appear visually similar but are technically different
- **Example**: `file.txt` with invisible characters

```javascript
const obfuscator = new FileObfuscator({ useSpecialChars: true });
// Adds invisible Unicode characters to filenames
```

### 7. Steganography
- **Technique**: Embeds secret files inside carrier files
- **Carrier**: Can be image, document, or any binary file
- **Format**: Length-prefixed embedded data
- **Extraction**: Requires knowledge of carrier size and embedding method

```javascript
obfuscator.steganographyEmbed(secretFile, carrierFile, outputPath);
// Embeds secret.txt inside innocent_photo.jpg
```

### 8. Polymorphic Wrapping
- **Formats**: Base64, Hex, Chunked JSON
- **Advantage**: Transforms file format to avoid signature detection
- **Reversible**: Can be extracted/decoded
- **Use Case**: Evading content-based detection systems

```javascript
obfuscator.createPolymorphicWrapper(file, output, 'base64');
// Converts file to Base64 representation
```

## Installation

```bash
npm install
# or
node file-obfuscator.js <filePath> [outputDir] [options]
```

## Usage

### Basic Usage

```javascript
const FileObfuscator = require('./file-obfuscator');

// Create obfuscator with default options
const obfuscator = new FileObfuscator();

// Obfuscate a file
const result = obfuscator.obfuscate('/path/to/file.txt', '/output/dir');

console.log(result);
// {
//   originalPath: '/path/to/file.txt',
//   originalName: 'file.txt',
//   strategies: ['mixedCaseNames', 'fileAttributes', ...],
//   obfuscatedPaths: [...]
// }
```

### Custom Options

```javascript
const obfuscator = new FileObfuscator({
  useADS: true,           // Enable ADS (Windows only)
  useMixedCase: true,     // Enable case randomization
  useAttributes: true,    // Enable file attributes
  useMetadata: true,      // Enable timestamp spoofing
  useNesting: true,       // Enable deep directory nesting
  useSpecialChars: true,  // Enable special characters
  timestamp: Date.now()   // Custom timestamp
});

obfuscator.obfuscate(filePath, outputDir);
```

### Steganography Embedding

```javascript
// Embed a secret file inside a carrier file
const embedding = obfuscator.steganographyEmbed(
  'secret.txt',
  'innocent_photo.jpg',
  'hidden_photo.jpg'
);

// Extract the secret back
const extracted = obfuscator.steganographyExtract(
  'hidden_photo.jpg',
  fs.statSync('innocent_photo.jpg').size,
  'recovered_secret.txt'
);
```

### Polymorphic Wrapping

```javascript
// Wrap file in Base64
obfuscator.createPolymorphicWrapper(
  'payload.exe',
  'payload.b64',
  'base64'
);

// Wrap in Hex
obfuscator.createPolymorphicWrapper(
  'payload.exe',
  'payload.hex',
  'hex'
);

// Wrap in Chunked JSON
obfuscator.createPolymorphicWrapper(
  'payload.exe',
  'payload.json',
  'chunks'
);
```

### Mapping and Reports

```javascript
// Get mapping of all obfuscated files
const mapping = obfuscator.getMapping();

// Save mapping to file
obfuscator.saveMapping('/output/mapping.json');

// Optionally encrypt the mapping
obfuscator.saveMapping('/output/mapping.json', true);

// Generate comprehensive report
const report = obfuscator.generateReport();
obfuscator.saveReport('/output/report.json');
```

## Command Line Usage

```bash
# Basic obfuscation
node file-obfuscator.js secret.txt /output

# Generate report
node file-obfuscator.js secret.txt /output --report

# Use all strategies
node file-obfuscator.js secret.txt /output --all-strategies

# Show help
node file-obfuscator.js --help
```

## Examples

### Example 1: Hide Malicious Script

```javascript
const obfuscator = new FileObfuscator({
  useMixedCase: true,
  useAttributes: true,
  useNesting: true
});

obfuscator.obfuscate('malware.ps1', '/hidden');
// Creates: HeIdEn/d1a2b/d3c4d/mAlWaRe.ps1 (hidden attributes)
```

### Example 2: Embed in Innocent File

```javascript
// Create innocent-looking carrier
fs.writeFileSync('readme.txt', 'This is just a readme file.');

// Embed malicious code
obfuscator.steganographyEmbed('payload.exe', 'readme.txt', 'readme_hidden.txt');
// File appears to be text document, contains executable
```

### Example 3: Multi-Layer Obfuscation

```javascript
// Step 1: Wrap in Base64
obfuscator.createPolymorphicWrapper('payload.exe', 'payload.b64', 'base64');

// Step 2: Obfuscate the wrapper
const result = obfuscator.obfuscate('payload.b64', '/output');

// Step 3: Embed in carrier
obfuscator.steganographyEmbed(result.obfuscatedPaths[0].location, 
  'innocent.doc', 'innocent_hidden.doc');

// File is now: wrapped → obfuscated → embedded
```

## Platform-Specific Behavior

### Windows
- **ADS Support**: Full support for alternate data streams
- **Attributes**: Hidden (+h) and System (+s) flags
- **Case**: NTFS case-insensitive but case-preserving
- **Special Chars**: Most Unicode characters supported in filenames

### macOS/Linux
- **ADS Support**: Not supported
- **Attributes**: Extended attributes (xattr) support
- **Case**: Case-sensitive filesystem
- **Dot Prefix**: Standard hidden file convention

## Security Considerations

### Strengths
1. **Multi-layer Protection**: Combines multiple obfuscation techniques
2. **Cross-platform**: Works on Windows, macOS, and Linux
3. **Reversible**: Can extract obfuscated files with knowledge of techniques
4. **Flexible**: Selective strategy enabling

### Limitations
1. **Not Encryption**: Does not provide cryptographic protection
2. **Content Unprotected**: File content is still readable if found
3. **Forensic Analysis**: Advanced forensics can still recover obfuscated files
4. **ADS Windows-Only**: Some strategies platform-specific

### Recommendations
1. **Combine with Encryption**: Use alongside AES or other encryption
2. **Use Steganography**: Embed in innocent-looking carrier files
3. **Multi-layer Approach**: Use multiple techniques together
4. **Remove Metadata**: Strip creation dates and other metadata
5. **Regular Rotation**: Periodically change obfuscation methods

## Detection and Defense

### Detection Challenges
- Mixed case names evade regex pattern matching
- Deep nesting slows scanning tools
- Steganography looks like legitimate files
- Special characters bypass simple string searches

### Detection Methods (by Analysts)
1. **Entropy Analysis**: Detect anomalous file characteristics
2. **Behavioral Monitoring**: Track file access patterns
3. **Filesystem Scan**: Enumerate hidden files (`attrib -a`)
4. **ADS Enumeration**: Use `dir /s /a:s` to find streams
5. **Metadata Analysis**: Check file modification timestamps

## Performance Impact

- **Mixed Case**: Minimal impact
- **Attributes**: Negligible impact
- **Metadata**: Very fast
- **Deep Nesting**: May slow antivirus/scanning
- **Steganography**: Depends on carrier file size
- **Polymorphic Wrapping**: Small CPU overhead

## API Reference

### Constructor

```javascript
new FileObfuscator(options)
```

**Options:**
- `useADS` (bool): Enable alternate data streams
- `useMixedCase` (bool): Enable case randomization
- `useAttributes` (bool): Enable file attributes
- `useMetadata` (bool): Enable timestamp spoofing
- `useNesting` (bool): Enable deep directory nesting
- `useSpecialChars` (bool): Enable special characters
- `platform` (string): Override OS platform
- `timestamp` (number): Custom timestamp

### Methods

#### `obfuscate(filePath, outputDir)`
Obfuscate a file using configured strategies.

#### `steganographyEmbed(secretFile, carrierFile, outputPath)`
Embed secret file inside carrier file.

#### `steganographyExtract(combinedFile, carrierSize, outputPath)`
Extract embedded file from carrier.

#### `createPolymorphicWrapper(file, output, type)`
Wrap file in alternative format (base64, hex, chunks).

#### `getMapping()`
Get dictionary of all obfuscated files.

#### `saveMapping(outputPath, encrypt)`
Save obfuscation mapping to file.

#### `generateReport()`
Generate comprehensive obfuscation report.

#### `saveReport(outputPath)`
Save report to JSON file.

## Troubleshooting

### ADS Not Working
- **Issue**: Windows-specific feature, may not work on all NTFS versions
- **Solution**: Check `attrib /s` or use PowerShell to verify streams

### File Attributes Not Applying
- **Windows**: Requires appropriate permissions
- **Linux**: Requires filesystem support
- **Solution**: Run as administrator/root

### Polymorphic Wrapping Too Large
- **Issue**: Base64/Hex increase file size by 33-100%
- **Solution**: Use chunked format or compression

### Special Characters Not Displaying
- **Issue**: Terminal encoding may not support Unicode
- **Solution**: Use `ls -la` or file explorer to view actual filenames

## File Output Structure

```
/output
├── FiLeNaMe.txt           # Mixed case obfuscation
├── .hidden_file.txt        # Attribute obfuscation
├── _original_file.txt      # Metadata obfuscation
├── d1a2b
│   └── d3c4d
│       └── deep_file.txt   # Nesting obfuscation
├── mapping.json            # Obfuscation mapping
└── report.json             # Detailed report
```

## Advanced Topics

### Custom Strategies
Extend the class to add custom obfuscation:

```javascript
class CustomObfuscator extends FileObfuscator {
  _customStrategy(filePath, content, outputDir) {
    // Implement custom obfuscation
    return { /* result */ };
  }
}
```

### Encryption Integration
Combine with encryption:

```javascript
const encrypted = crypto.createCipheriv('aes-256-cbc', key, iv);
const obfuscated = obfuscator.obfuscate(filePath, outputDir);
// Encrypt obfuscated paths
```

### Batch Processing
Process multiple files:

```javascript
const files = fs.readdirSync(sourceDir);
files.forEach(file => {
  obfuscator.obfuscate(path.join(sourceDir, file), outputDir);
});

obfuscator.saveReport(path.join(outputDir, 'report.json'));
```

## License

This tool is provided for educational and authorized security testing purposes only.

## Disclaimer

This tool may be used for both legitimate security research and potentially malicious purposes. Users are responsible for ensuring their use complies with applicable laws and regulations.
