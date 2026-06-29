# File Obfuscator - Advanced File Hiding & Obfuscation Tool

A comprehensive Node.js file obfuscation tool that implements 8 distinct obfuscation strategies to hide, obscure, and protect sensitive files across multiple operating systems.

## Quick Start

```javascript
const FileObfuscator = require('./src/file-obfuscator');

// Create obfuscator
const obfuscator = new FileObfuscator();

// Obfuscate a file
const result = obfuscator.obfuscate('sensitive.txt', '/output');

console.log(result);
// Result contains all obfuscated file paths and strategies used
```

## Features

### 🔒 8 Obfuscation Strategies

1. **Alternate Data Streams (ADS)** - Windows NTFS hidden data streams
2. **Mixed Case Names** - Randomized filename case combinations
3. **File Attributes** - Hidden/System flags or dot-prefix naming
4. **Metadata Manipulation** - Spoofed timestamps
5. **Deep Nesting** - Deeply nested directory structures
6. **Special Characters** - Unicode and zero-width character injection
7. **Steganography** - Embed files inside carrier files
8. **Polymorphic Wrapping** - Base64, Hex, or Chunked format transformation

### ✨ Key Capabilities

- **Multi-Platform**: Windows, macOS, Linux support
- **Selective Strategies**: Enable only needed obfuscation methods
- **Steganographic Embedding**: Hide files inside innocent-looking carriers
- **Polymorphic Transformation**: Convert files to alternative formats
- **Mapping & Tracking**: Record all obfuscations for recovery
- **Report Generation**: Detailed JSON reports of all operations
- **Content Preservation**: Original file content always preserved
- **Cross-Platform Compatible**: Works on Windows, macOS, and Linux

## Installation

```bash
# Clone or copy the repository
git clone <repo>
cd sc-generator

# Install dependencies (uses built-in Node.js modules)
npm install
```

## Usage

### Basic Obfuscation

```javascript
const FileObfuscator = require('./src/file-obfuscator');

const obfuscator = new FileObfuscator();
const result = obfuscator.obfuscate('/path/to/file.txt', '/output/dir');

console.log(result);
// {
//   originalPath: '/path/to/file.txt',
//   originalName: 'file.txt',
//   strategies: ['mixedCaseNames', 'deepNesting', ...],
//   obfuscatedPaths: [
//     { strategy: 'mixedCaseNames', location: '...' },
//     { strategy: 'deepNesting', location: '...' },
//     ...
//   ]
// }
```

### Custom Strategy Selection

```javascript
const obfuscator = new FileObfuscator({
  useMixedCase: true,      // Enable case randomization
  useAttributes: true,     // Enable file attributes
  useMetadata: true,       // Enable timestamp spoofing
  useNesting: true,        // Enable deep nesting
  useSpecialChars: true,   // Enable special characters
  useADS: false            // Disable ADS (Windows-specific)
});

obfuscator.obfuscate(filePath, outputDir);
```

### Steganographic Embedding

Hide a secret file inside an innocent-looking carrier file:

```javascript
// Embed secret.txt inside photo.jpg
const embedding = obfuscator.steganographyEmbed(
  'secret.txt',
  'photo.jpg',
  'hidden_photo.jpg'
);

// Later, extract the secret
const carrierSize = fs.statSync('photo.jpg').size;
obfuscator.steganographyExtract('hidden_photo.jpg', carrierSize, 'recovered_secret.txt');
```

### Polymorphic Wrapping

Transform files into alternative formats:

```javascript
// Base64 encoding
obfuscator.createPolymorphicWrapper('payload.exe', 'payload.b64', 'base64');

// Hexadecimal encoding
obfuscator.createPolymorphicWrapper('payload.exe', 'payload.hex', 'hex');

// Chunked JSON format
obfuscator.createPolymorphicWrapper('payload.exe', 'payload.json', 'chunks');
```

### Mapping & Recovery

```javascript
// Get mapping of all obfuscations
const mapping = obfuscator.getMapping();

// Save mapping to file
obfuscator.saveMapping('/output/mapping.json');

// Generate detailed report
const report = obfuscator.generateReport();
obfuscator.saveReport('/output/report.json');
```

### Command Line Interface

```bash
# Basic obfuscation
node src/file-obfuscator.js sensitive.txt /output

# With report generation
node src/file-obfuscator.js sensitive.txt /output --report

# Show help
node src/file-obfuscator.js --help
```

## Strategy Details

### 1. Mixed Case Names
- **Cross-Platform**: Yes
- **Example**: `config.txt` → `CoNfIg.txt`
- **Purpose**: Evade simple string matching and regex patterns
- **Recovery**: Requires mapping file

### 2. Deep Nesting
- **Cross-Platform**: Yes
- **Depth**: 6 levels by default
- **Structure**: `d1a2b/d3c4d/d5e6f/d7g8h/d9i0j/d1k2l/file.txt`
- **Purpose**: Slow down directory scanning and antivirus tools
- **Recovery**: Directory traversal or mapping

### 3. File Attributes
- **Windows**: Hidden (+h) and System (+s) attributes
- **Unix/Linux**: Dot-prefix naming (`.filename`)
- **Purpose**: Hide from default directory listings
- **Recovery**: `attrib -h -s` or `ls -a`

### 4. Metadata Manipulation
- **Purpose**: Obscure actual creation/modification time
- **Default Time**: 2020-01-01
- **Recovery**: Carving or mapping
- **Note**: Forensics can still detect metadata changes

### 5. Steganography
- **Purpose**: Embed secret file inside innocent carrier
- **Formats**: Any binary file (images, documents)
- **Extraction**: Requires carrier original size and knowledge of technique
- **Advantage**: File appears legitimate to casual inspection

### 6. Polymorphic Wrapping
- **Formats**: Base64, Hex, Chunked JSON
- **Size Impact**: +33-100% depending on format
- **Recovery**: Base64/Hex decode or JSON parsing
- **Purpose**: Evade content-based signature detection

### 7. Special Characters
- **Characters**: Zero-width Unicode characters
- **Visibility**: Invisible to human inspection
- **Purpose**: Filename looks normal but is technically different
- **Detection**: Character analysis or file explorer

### 8. Alternate Data Streams
- **Platform**: Windows NTFS only
- **Access**: `filename.txt:stream:$DATA`
- **Purpose**: Hide data in alternate NTFS streams
- **Discovery**: PowerShell or `dir /s /a:s`

## Examples

### Example 1: Basic Obfuscation

```javascript
const obfuscator = new FileObfuscator();
obfuscator.obfuscate('malware.exe', '/output');
// Creates multiple obfuscated versions in /output
```

### Example 2: Multi-Layer Obfuscation

```javascript
// Step 1: Polymorphic wrap
obfuscator.createPolymorphicWrapper('payload.exe', 'step1.hex', 'hex');

// Step 2: Obfuscate the wrapper
const result = obfuscator.obfuscate('step1.hex', '/output');

// Step 3: Embed in carrier
obfuscator.steganographyEmbed(
  result.obfuscatedPaths[0].location,
  'innocent.doc',
  'final_carrier.doc'
);
```

### Example 3: Batch Processing

```javascript
const files = ['file1.txt', 'file2.txt', 'file3.txt'];

files.forEach(file => {
  obfuscator.obfuscate(file, '/output');
});

// Save consolidated report
obfuscator.saveReport('/output/batch_report.json');
obfuscator.saveMapping('/output/batch_mapping.json');
```

## Testing

Run the comprehensive test suite:

```bash
# Execute all tests
node src/file-obfuscator.test.js

# Output:
# ✓ Test 1: Instantiation passed
# ✓ Test 2: Mixed case obfuscation passed
# ✓ Test 3: Deep nesting passed
# ✓ Test 4: Metadata manipulation passed
# ✓ Test 5: Steganography passed
# ✓ Test 6: Polymorphic wrapping passed
# ✓ Test 7: Mapping and reports passed
# ✓ Test 8: Custom options passed
# ✓ Test 9: Hash consistency passed
# ✓ Test 10: Error handling passed
# ✓ Test 11: Content preservation passed
# ✓ Test 12: Multiple strategies passed
```

Run comprehensive examples:

```bash
node src/file-obfuscator-examples.js
```

## API Reference

### Constructor

```javascript
new FileObfuscator(options)
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| useADS | boolean | true | Enable alternate data streams (Windows) |
| useMixedCase | boolean | true | Enable case randomization |
| useAttributes | boolean | true | Enable file attributes |
| useMetadata | boolean | true | Enable timestamp spoofing |
| useNesting | boolean | true | Enable deep nesting |
| useSpecialChars | boolean | true | Enable special characters |
| platform | string | os.platform() | Override OS platform |
| timestamp | number | Date.now() | Custom timestamp |

### Methods

#### obfuscate(filePath, outputDir)
Obfuscate a file using configured strategies.

**Returns:** Object with original path, strategies used, and obfuscated paths.

#### steganographyEmbed(secretFile, carrierFile, outputPath)
Embed secret file inside carrier file.

**Returns:** Embedding result with metadata.

#### steganographyExtract(combinedFile, carrierSize, outputPath)
Extract embedded secret from carrier file.

**Returns:** Extraction result with recovered data.

#### createPolymorphicWrapper(file, output, type)
Wrap file in alternative format (base64, hex, chunks).

**Returns:** Wrapping result with size information.

#### getMapping()
Get dictionary of all obfuscated files.

**Returns:** Object mapping original names to obfuscation records.

#### saveMapping(outputPath, encrypt?)
Save obfuscation mapping to file.

**Returns:** Path to saved mapping file.

#### generateReport()
Generate comprehensive obfuscation report.

**Returns:** Report object with statistics and details.

#### saveReport(outputPath)
Save report to JSON file.

**Returns:** Path to saved report file.

## File Output Structure

```
/output
├── FiLeNaMe.txt              # Mixed case obfuscation
├── .hidden_file.txt          # File attributes obfuscation
├── _original_file.txt        # Metadata obfuscation
├── d1a2b/d3c4d/d5e6f/...    # Deep nesting obfuscation
├── file‌‍‎.txt               # Special characters obfuscation
├── mapping.json              # Obfuscation mapping
└── report.json               # Detailed report
```

## Platform-Specific Features

### Windows
- Full Alternate Data Streams (ADS) support
- Hidden (+h) and System (+s) attributes
- Case-insensitive but case-preserving NTFS
- Full Unicode filename support

### macOS
- Extended attributes support (xattr)
- Case-sensitive filesystem
- Dot-prefix hidden files
- Full Unicode support

### Linux
- Case-sensitive filesystem
- Dot-prefix hidden files
- Full Unicode support
- Extended attributes (xattr)

## Security Considerations

### Strengths
✓ Multi-layer obfuscation combining 8 techniques  
✓ Cross-platform compatibility  
✓ Reversible (can recover with mapping)  
✓ Flexible strategy selection  
✓ Steganographic embedding looks innocent  

### Limitations
✗ Not cryptographic - does not encrypt content  
✗ File content still readable if discovered  
✗ Advanced forensics can recover files  
✗ Some strategies platform-specific  
✗ Doesn't protect against content analysis  

### Recommendations
1. **Combine with Encryption**: Use AES or other crypto alongside
2. **Use Steganography**: Embed in innocent carrier files
3. **Multi-layer Approach**: Combine multiple strategies
4. **Remove Metadata**: Strip creation dates and signatures
5. **Regular Rotation**: Change obfuscation methods periodically

## Performance

| Strategy | CPU | Disk | Time |
|----------|-----|------|------|
| Mixed Case | Minimal | Minimal | ~1ms |
| Attributes | Negligible | None | ~1ms |
| Metadata | Fast | None | ~2ms |
| Deep Nesting | Minimal | Minimal | ~5ms |
| Steganography | Moderate | +carrier size | ~50ms |
| Polymorphic | Low | +33-100% | ~10ms |
| Special Chars | Minimal | Minimal | ~3ms |
| ADS | Minimal | Varies | ~10ms |

## Troubleshooting

### Issue: ADS not working
**Solution**: Verify Windows NTFS filesystem, check permissions

### Issue: Attributes not applying
**Solution**: Run with administrator/root privileges

### Issue: Polymorphic wrapper too large
**Solution**: Use chunked format or compression

### Issue: Special characters not visible
**Solution**: Use file explorer or terminal with Unicode support

## Advanced Usage

### Custom Strategy Extension

```javascript
class CustomObfuscator extends FileObfuscator {
  _customStrategy(filePath, content, outputDir) {
    // Implement custom logic
    return { strategy: 'custom', /* result */ };
  }
}
```

### Encryption Integration

```javascript
const crypto = require('crypto');

// Encrypt obfuscated files
const obfuscated = obfuscator.obfuscate(filePath, outputDir);
const encrypted = crypto.createCipheriv('aes-256-cbc', key, iv);
```

### Batch Operations

```javascript
const glob = require('glob');
const files = glob.sync('./sensitive/**/*');

files.forEach(file => {
  obfuscator.obfuscate(file, '/output');
});

obfuscator.saveReport('/output/batch_report.json');
```

## Files Included

- **src/file-obfuscator.js** - Main implementation (8 strategies)
- **src/file-obfuscator-examples.js** - 8 comprehensive examples
- **src/file-obfuscator.test.js** - 12-test suite with full coverage
- **FILE_OBFUSCATOR_GUIDE.md** - Detailed technical documentation
- **FILE_OBFUSCATOR_README.md** - This file

## License

Provided for educational and authorized security testing purposes.

## Disclaimer

This tool may be used for legitimate security research. Users are responsible for ensuring compliance with applicable laws and regulations.

---

**Version**: 1.0.0  
**Platform**: Node.js 12+  
**Dependencies**: Built-in Node.js modules only
