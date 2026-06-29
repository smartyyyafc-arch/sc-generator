# File Obfuscator - Quick Start Guide

## 30-Second Setup

```javascript
const FileObfuscator = require('./src/file-obfuscator');
const obfuscator = new FileObfuscator();
obfuscator.obfuscate('secret.txt', '/output');
```

Done! Your file is now obfuscated with 5+ strategies.

## Common Use Cases

### Hide a Sensitive File

```javascript
const obfuscator = new FileObfuscator();
obfuscator.obfuscate('credentials.txt', './hidden');
```

**Result:** File hidden in deeply nested folder with randomized name

### Embed Secret in Innocent File

```javascript
const obfuscator = new FileObfuscator();
obfuscator.steganographyEmbed(
  'secret.txt',
  'readme.pdf',
  'readme_hidden.pdf'
);
```

**Result:** Secret embedded invisibly in PDF

### Convert to Different Format

```javascript
obfuscator.createPolymorphicWrapper(
  'malware.exe',
  'output.hex',
  'hex'  // or 'base64', 'chunks'
);
```

**Result:** File converted to hex/base64 format

### Generate Recovery Mapping

```javascript
obfuscator.obfuscate('file.txt', './output');
obfuscator.saveMapping('./output/mapping.json');
```

**Result:** JSON file with original→obfuscated mappings

## Obfuscation Strategies

| Strategy | Effect | Platform |
|----------|--------|----------|
| **Mixed Case** | `file.txt` → `FiLe.TxT` | All |
| **Deep Nesting** | Hidden in 6-level directories | All |
| **File Attributes** | Hidden from directory listings | All |
| **Metadata Spoofing** | Fake timestamps (2020-01-01) | All |
| **Special Characters** | Invisible Unicode in name | All |
| **Steganography** | Embed in carrier file | All |
| **Polymorphic Wrap** | Base64/Hex/JSON format | All |
| **ADS** | NTFS alternate streams | Windows |

## Configuration Examples

### Only Use Case Randomization

```javascript
new FileObfuscator({ useMixedCase: true })
```

### Deep Hiding with Multiple Strategies

```javascript
new FileObfuscator({
  useNesting: true,
  useMixedCase: true,
  useMetadata: true,
  useSpecialChars: true
})
```

### Minimal Obfuscation (Fast)

```javascript
new FileObfuscator({
  useMixedCase: true,
  useMetadata: false,
  useNesting: false,
  useSpecialChars: false
})
```

### Maximum Obfuscation (Slow)

```javascript
new FileObfuscator({
  useADS: true,
  useMixedCase: true,
  useAttributes: true,
  useMetadata: true,
  useNesting: true,
  useSpecialChars: true
})
```

## Command Line Examples

```bash
# Basic obfuscation
node src/file-obfuscator.js secret.txt ./output

# Generate report
node src/file-obfuscator.js secret.txt ./output --report

# All strategies
node src/file-obfuscator.js secret.txt ./output --all-strategies

# Help
node src/file-obfuscator.js --help
```

## API Cheatsheet

```javascript
const obf = new FileObfuscator();

// Obfuscate file
obf.obfuscate(filePath, outputDir);

// Embed in carrier
obf.steganographyEmbed(secret, carrier, output);

// Extract from carrier
obf.steganographyExtract(combined, carrierSize, output);

// Wrap file
obf.createPolymorphicWrapper(file, output, 'hex');

// Get mappings
obf.getMapping();

// Save mappings
obf.saveMapping(path);

// Generate report
obf.generateReport();
obf.saveReport(path);
```

## Understanding Output

### Obfuscation Result

```javascript
{
  originalPath: '/path/to/file.txt',
  originalName: 'file.txt',
  strategies: ['mixedCaseNames', 'deepNesting', ...],
  obfuscatedPaths: [
    {
      strategy: 'mixedCaseNames',
      originalName: 'file.txt',
      obfuscatedName: 'FiLe.TxT',
      location: '/output/FiLe.TxT'
    },
    {
      strategy: 'deepNesting',
      location: '/output/d1a2b/d3c4d/d5e6f/file.txt',
      nestingDepth: 6
    }
    // ... more strategies
  ]
}
```

### Report Structure

```javascript
{
  timestamp: '2024-01-15T10:30:00.000Z',
  platform: 'win32',
  strategiesUsed: ['mixedCaseNames', 'deepNesting', ...],
  fileCount: 3,
  summary: {
    totalFiles: 3,
    totalObfuscations: 15,
    successfulStrategies: 6
  },
  files: [...]
}
```

## Running Tests

```bash
# Run all 12 tests
node src/file-obfuscator.test.js

# Run all 8 examples
node src/file-obfuscator-examples.js
```

## File Structure After Obfuscation

```
/output
├── FiLe.TxT                    # Mixed case
├── .file.txt                   # Hidden attribute
├── _file.txt                   # Metadata spoofed
├── d1a2b/d3c4d/.../file.txt   # Deep nesting
├── file‌‍‎.txt                  # Special chars (invisible)
├── mapping.json                # Recovery info
└── report.json                 # Statistics
```

## Performance Notes

| Operation | Speed | Output Size |
|-----------|-------|-------------|
| Mixed Case | Instant | Same |
| Nesting | Instant | Same |
| Steganography | ~50ms | +carrier |
| Polymorphic (Hex) | ~10ms | 2x |
| Polymorphic (Base64) | ~10ms | 1.33x |
| Full Obfuscation | ~100ms | 1-2x |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Files too visible | Enable more strategies |
| File too large | Avoid base64 format |
| Can't find files | Use mapping.json |
| Attributes not applied | Run as admin/root |
| Performance slow | Use fewer strategies |

## Recovery

### Finding Original File

```javascript
// Method 1: Use mapping
const mapping = obf.getMapping();
const record = mapping['original.txt'];
console.log(record.obfuscatedPaths);

// Method 2: Deep search
ls -R /output | grep -i original
```

### Extracting Embedded Secret

```javascript
const carrierSize = 1024; // original carrier size
obf.steganographyExtract('carrier.jpg', carrierSize, 'recovered.txt');
```

### Converting Back from Hex

```javascript
const hex = fs.readFileSync('file.hex', 'utf8');
const buffer = Buffer.from(hex, 'hex');
fs.writeFileSync('file.original', buffer);
```

## Best Practices

1. **Keep Mapping Secure** - Store mapping.json encrypted
2. **Use Multiple Strategies** - Don't rely on single technique
3. **Combine with Encryption** - Add cryptographic layer
4. **Regular Testing** - Verify recovery works
5. **Document Methods** - Remember what you used
6. **Clean Carriers** - Use innocent-looking files for steganography
7. **Avoid Patterns** - Use different obfuscations for different files
8. **Test Extraction** - Always verify you can recover

## Examples at a Glance

```javascript
// Example 1: Simple
new FileObfuscator().obfuscate('file.txt', '/out');

// Example 2: Hide in image
obf.steganographyEmbed('secret.txt', 'photo.jpg', 'stego.jpg');

// Example 3: Multi-layer
obf.createPolymorphicWrapper('file.exe', 'step1.hex', 'hex');
obf.obfuscate('step1.hex', '/output');

// Example 4: Batch process
files.forEach(f => obf.obfuscate(f, '/out'));
obf.saveReport('/out/batch.json');
```

## Next Steps

1. **Read Full Guide**: `FILE_OBFUSCATOR_GUIDE.md`
2. **Review Examples**: `src/file-obfuscator-examples.js`
3. **Run Tests**: `node src/file-obfuscator.test.js`
4. **Integrate**: Import in your project
5. **Customize**: Extend with your own strategies

---

For detailed documentation, see `FILE_OBFUSCATOR_GUIDE.md`
