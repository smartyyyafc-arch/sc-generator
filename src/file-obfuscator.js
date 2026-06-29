/**
 * File Obfuscator - Advanced File Obfuscation Techniques
 *
 * Implements multiple obfuscation strategies:
 * 1. Alternate Data Streams (ADS) - Windows NTFS feature
 * 2. File Attributes - Hide, System, Archive flags
 * 3. Mixed Case Names - Confuse file lookups
 * 4. Null Byte Injection - Filename truncation tricks
 * 5. Special Characters - Use Unicode and special chars
 * 6. Metadata Manipulation - Modified timestamps
 * 7. Deep Nesting - Directory depth obfuscation
 * 8. Directory Junctions - Link-based hiding
 */

const fs = require('fs');
const path = require('path');
const { execSync, exec } = require('child_process');
const crypto = require('crypto');
const os = require('os');

class FileObfuscator {
  constructor(options = {}) {
    this.options = {
      platform: os.platform(),
      useADS: true,
      useMixedCase: true,
      useAttributes: true,
      useMetadata: true,
      useNesting: true,
      useSpecialChars: true,
      timestamp: options.timestamp || Date.now(),
      keyFile: options.keyFile || null,
      ...options
    };

    this.obfuscationMap = new Map();
    this.strategies = [];
    this._initializeStrategies();
  }

  /**
   * Initialize available obfuscation strategies based on platform
   */
  _initializeStrategies() {
    if (this.options.useADS && this.options.platform === 'win32') {
      this.strategies.push('alternateDataStreams');
    }
    if (this.options.useMixedCase) {
      this.strategies.push('mixedCaseNames');
    }
    if (this.options.useAttributes) {
      this.strategies.push('fileAttributes');
    }
    if (this.options.useMetadata) {
      this.strategies.push('metadataManipulation');
    }
    if (this.options.useNesting) {
      this.strategies.push('deepNesting');
    }
    if (this.options.useSpecialChars) {
      this.strategies.push('specialCharacters');
    }
  }

  /**
   * Main obfuscation method - applies multiple techniques
   */
  obfuscate(filePath, outputDir = null) {
    if (!fs.existsSync(filePath)) {
      throw new Error(`File not found: ${filePath}`);
    }

    const fileContent = fs.readFileSync(filePath);
    const fileName = path.basename(filePath);
    const dirName = outputDir || path.dirname(filePath);

    // Create obfuscation record
    const record = {
      originalPath: filePath,
      originalName: fileName,
      timestamp: this.options.timestamp,
      strategies: this.strategies,
      obfuscatedPaths: [],
      metadata: {
        size: fileContent.length,
        hash: this._hashFile(fileContent)
      }
    };

    // Apply each strategy
    for (const strategy of this.strategies) {
      try {
        const result = this[`_${strategy}`](filePath, fileContent, dirName);
        if (result) {
          record.obfuscatedPaths.push(result);
        }
      } catch (error) {
        console.warn(`Strategy ${strategy} failed:`, error.message);
      }
    }

    // Store mapping
    this.obfuscationMap.set(fileName, record);

    return record;
  }

  /**
   * Strategy 1: Alternate Data Streams (Windows NTFS only)
   * Stores hidden data in NTFS ADS
   */
  _alternateDataStreams(filePath, content, outputDir) {
    if (this.options.platform !== 'win32') {
      return null;
    }

    try {
      const fileName = path.basename(filePath);
      const adsPath = `${outputDir}\\${fileName}:Hidden:$DATA`;

      // Write to ADS using PowerShell
      const psScript = `
        [System.IO.File]::WriteAllBytes(
          '${adsPath}',
          [System.Text.Encoding]::UTF8.GetBytes([System.IO.File]::ReadAllText('${filePath}'))
        )
      `;

      execSync(`powershell -Command "${psScript}"`, { stdio: 'pipe' });

      return {
        strategy: 'alternateDataStreams',
        location: adsPath,
        type: 'NTFS ADS',
        description: 'Data stored in alternate data stream'
      };
    } catch (error) {
      console.warn('ADS strategy not available:', error.message);
      return null;
    }
  }

  /**
   * Strategy 2: Mixed Case Names
   * Creates files with randomized case combinations that are hard to reference
   */
  _mixedCaseNames(filePath, content, outputDir) {
    const originalName = path.basename(filePath);
    const ext = path.extname(originalName);
    const nameWithoutExt = path.basename(originalName, ext);

    const obfuscatedName = this._generateMixedCaseName(nameWithoutExt) + ext;
    const newPath = path.join(outputDir, obfuscatedName);

    fs.writeFileSync(newPath, content);

    return {
      strategy: 'mixedCaseNames',
      originalName,
      obfuscatedName,
      location: newPath,
      type: 'Case Variation',
      description: 'Filename case randomized to confuse lookups'
    };
  }

  /**
   * Strategy 3: File Attributes (Windows/Unix)
   * Hides files using system attributes
   */
  _fileAttributes(filePath, content, outputDir) {
    const fileName = path.basename(filePath);
    const newPath = path.join(outputDir, fileName);

    fs.writeFileSync(newPath, content);

    try {
      if (this.options.platform === 'win32') {
        // Windows: Set hidden and system attributes
        execSync(`attrib +h +s "${newPath}"`, { stdio: 'pipe' });
      } else {
        // Unix: Dot-prefix for hidden files
        const hiddenPath = path.join(outputDir, '.' + fileName);
        fs.renameSync(newPath, hiddenPath);
        return {
          strategy: 'fileAttributes',
          originalName: fileName,
          obfuscatedName: '.' + fileName,
          location: hiddenPath,
          type: 'Hidden Attribute',
          description: 'File hidden using dot prefix (Unix) or hidden attribute (Windows)'
        };
      }

      return {
        strategy: 'fileAttributes',
        originalName: fileName,
        obfuscatedName: fileName,
        location: newPath,
        type: 'System Attributes',
        description: 'File hidden using system attributes (Windows)',
        attributes: '+h +s'
      };
    } catch (error) {
      console.warn('File attributes strategy failed:', error.message);
      return null;
    }
  }

  /**
   * Strategy 4: Metadata Manipulation
   * Modifies file timestamps and metadata to obscure origin
   */
  _metadataManipulation(filePath, content, outputDir) {
    const fileName = path.basename(filePath);
    const newPath = path.join(outputDir, `_${fileName}`);

    fs.writeFileSync(newPath, content);

    try {
      const fakeTime = new Date('2020-01-01').getTime();
      fs.utimesSync(newPath, fakeTime / 1000, fakeTime / 1000);

      return {
        strategy: 'metadataManipulation',
        originalName: fileName,
        obfuscatedName: `_${fileName}`,
        location: newPath,
        type: 'Metadata Spoofing',
        description: 'File timestamps modified to obscure creation time',
        fakeTimestamp: '2020-01-01'
      };
    } catch (error) {
      console.warn('Metadata manipulation strategy failed:', error.message);
      return null;
    }
  }

  /**
   * Strategy 5: Deep Nesting
   * Hides files in deeply nested directories
   */
  _deepNesting(filePath, content, outputDir) {
    const fileName = path.basename(filePath);
    const nesting = this._generateNestingPath(6);
    const nestedDir = path.join(outputDir, nesting);

    fs.mkdirSync(nestedDir, { recursive: true });
    const newPath = path.join(nestedDir, fileName);
    fs.writeFileSync(newPath, content);

    return {
      strategy: 'deepNesting',
      originalName: fileName,
      location: newPath,
      nestingDepth: 6,
      nestingPath: nesting,
      type: 'Directory Depth',
      description: 'File hidden in deeply nested directory structure'
    };
  }

  /**
   * Strategy 6: Special Characters
   * Uses Unicode and special characters in filenames
   */
  _specialCharacters(filePath, content, outputDir) {
    const fileName = path.basename(filePath);
    const ext = path.extname(fileName);
    const nameWithoutExt = path.basename(fileName, ext);

    // Create filename with special Unicode characters
    const obfuscatedName = this._generateSpecialCharName(nameWithoutExt) + ext;
    const newPath = path.join(outputDir, obfuscatedName);

    fs.writeFileSync(newPath, content);

    return {
      strategy: 'specialCharacters',
      originalName: fileName,
      obfuscatedName,
      location: newPath,
      type: 'Unicode Obfuscation',
      description: 'Filename contains Unicode and special characters',
      preview: obfuscatedName.substring(0, 50)
    };
  }

  /**
   * Generate a mixed case version of a filename
   */
  _generateMixedCaseName(name) {
    return name.split('').map((char, i) =>
      i % 2 === 0 ? char.toUpperCase() : char.toLowerCase()
    ).join('');
  }

  /**
   * Generate a deeply nested path
   */
  _generateNestingPath(depth) {
    const parts = [];
    for (let i = 0; i < depth; i++) {
      parts.push(`d${this._randomString(4)}`);
    }
    return parts.join(path.sep);
  }

  /**
   * Generate a filename with special characters
   */
  _generateSpecialCharName(name) {
    const specialChars = ['‌', '‍', '‎', '‏', '​', '‌', '⁠'];
    let result = name;
    for (let i = 0; i < Math.min(3, name.length); i++) {
      result += specialChars[i % specialChars.length];
    }
    return result;
  }

  /**
   * Generate random string
   */
  _randomString(length) {
    return crypto.randomBytes(length).toString('hex').substring(0, length);
  }

  /**
   * Hash file content
   */
  _hashFile(content) {
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  /**
   * Create a steganographic carrier file
   * Embeds data inside an innocent-looking file
   */
  steganographyEmbed(secretFile, carrierFile, outputPath) {
    const secretContent = fs.readFileSync(secretFile);
    const carrierContent = fs.readFileSync(carrierFile);

    // Create combined file with length prefix
    const secretLength = Buffer.alloc(4);
    secretLength.writeUInt32LE(secretContent.length, 0);

    const combined = Buffer.concat([
      carrierContent,
      secretLength,
      secretContent
    ]);

    fs.writeFileSync(outputPath, combined);

    return {
      strategy: 'steganography',
      type: 'File Embedding',
      carrierFile: path.basename(carrierFile),
      secretFile: path.basename(secretFile),
      outputPath,
      totalSize: combined.length,
      description: 'Secret file embedded inside carrier file'
    };
  }

  /**
   * Extract steganographically embedded data
   */
  steganographyExtract(combinedFile, carrierOriginalSize, outputPath) {
    const combined = fs.readFileSync(combinedFile);

    // Read the secret length prefix
    const secretLength = combined.readUInt32LE(carrierOriginalSize);
    const secretStart = carrierOriginalSize + 4;
    const secretEnd = secretStart + secretLength;

    const secretContent = combined.slice(secretStart, secretEnd);
    fs.writeFileSync(outputPath, secretContent);

    return {
      strategy: 'steganography',
      type: 'Extraction',
      extractedFile: outputPath,
      size: secretLength,
      description: 'Secret file extracted from carrier'
    };
  }

  /**
   * Create a null-byte injection filename (some systems)
   */
  createNullByteFile(filePath, content, outputDir) {
    const fileName = path.basename(filePath);
    const ext = path.extname(fileName);
    const nameWithoutExt = path.basename(fileName, ext);

    // Create filename with null byte (may be truncated by filesystem)
    const obfuscatedName = `${nameWithoutExt}\x00.txt${ext}`;

    try {
      const newPath = path.join(outputDir, obfuscatedName);
      fs.writeFileSync(newPath, content);

      return {
        strategy: 'nullByteInjection',
        location: newPath,
        type: 'Null Byte',
        description: 'Filename contains null byte for truncation tricks'
      };
    } catch (error) {
      console.warn('Null byte strategy not supported:', error.message);
      return null;
    }
  }

  /**
   * Get the mapping of all obfuscated files
   */
  getMapping() {
    return Object.fromEntries(this.obfuscationMap);
  }

  /**
   * Save obfuscation mapping to a secure file
   */
  saveMapping(outputPath, encrypt = false) {
    const mapping = this.getMapping();
    let content = JSON.stringify(mapping, null, 2);

    if (encrypt && this.options.keyFile) {
      content = this._encrypt(content);
    }

    fs.writeFileSync(outputPath, content);
    return outputPath;
  }

  /**
   * Encrypt mapping content
   */
  _encrypt(content) {
    const key = crypto.randomBytes(32);
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);

    let encrypted = cipher.update(content);
    encrypted = Buffer.concat([encrypted, cipher.final()]);

    // Return both key and encrypted content (normally key would be stored separately)
    return JSON.stringify({
      encrypted: encrypted.toString('hex'),
      iv: iv.toString('hex'),
      key: key.toString('hex')
    });
  }

  /**
   * Decrypt mapping content
   */
  _decrypt(encryptedContent) {
    const data = JSON.parse(encryptedContent);
    const key = Buffer.from(data.key, 'hex');
    const iv = Buffer.from(data.iv, 'hex');
    const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);

    let decrypted = decipher.update(Buffer.from(data.encrypted, 'hex'));
    decrypted = Buffer.concat([decrypted, decipher.final()]);

    return decrypted.toString();
  }

  /**
   * Create a polymorphic file wrapper
   * Changes file appearance while maintaining functionality
   */
  createPolymorphicWrapper(originalFile, outputPath, wrapperType = 'base64') {
    const content = fs.readFileSync(originalFile);
    let wrapped;

    switch (wrapperType) {
      case 'base64':
        wrapped = Buffer.from(content).toString('base64');
        break;
      case 'hex':
        wrapped = content.toString('hex');
        break;
      case 'chunks':
        wrapped = this._createChunkedFormat(content);
        break;
      default:
        wrapped = content;
    }

    fs.writeFileSync(outputPath, wrapped);

    return {
      strategy: 'polymorphicWrapper',
      type: wrapperType,
      originalPath: originalFile,
      wrappedPath: outputPath,
      originalSize: content.length,
      wrappedSize: wrapped.length || wrapped.toString().length,
      description: 'File wrapped in alternative format for obfuscation'
    };
  }

  /**
   * Create a chunked format representation
   */
  _createChunkedFormat(content) {
    const chunks = [];
    const chunkSize = 16;

    for (let i = 0; i < content.length; i += chunkSize) {
      const chunk = content.slice(i, i + chunkSize);
      chunks.push(chunk.toString('hex'));
    }

    return JSON.stringify({
      type: 'chunked-hex',
      chunks,
      checksum: crypto.createHash('sha256').update(content).digest('hex')
    });
  }

  /**
   * Generate a comprehensive obfuscation report
   */
  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      platform: this.options.platform,
      strategiesUsed: this.strategies,
      fileCount: this.obfuscationMap.size,
      files: [],
      summary: {
        totalFiles: this.obfuscationMap.size,
        successfulStrategies: this.strategies.length,
        totalObfuscations: 0
      }
    };

    for (const [originalName, record] of this.obfuscationMap) {
      report.files.push({
        originalName: record.originalName,
        strategies: record.strategies,
        obfuscatedCount: record.obfuscatedPaths.length,
        details: record.obfuscatedPaths
      });
      report.summary.totalObfuscations += record.obfuscatedPaths.length;
    }

    return report;
  }

  /**
   * Save comprehensive report
   */
  saveReport(outputPath) {
    const report = this.generateReport();
    fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
    return outputPath;
  }
}

/**
 * CLI/Export interface
 */
module.exports = FileObfuscator;

// If run directly
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help') {
    console.log(`
File Obfuscator - Advanced File Obfuscation Tool

Usage: node file-obfuscator.js <filePath> [outputDir] [options]

Options:
  --help              Show this help message
  --report            Generate and save report
  --steganography     Use steganography embedding
  --all-strategies    Use all available strategies

Examples:
  node file-obfuscator.js secret.txt /tmp --report
  node file-obfuscator.js data.bin /output --all-strategies
    `);
    process.exit(0);
  }

  const filePath = args[0];
  const outputDir = args[1] || path.dirname(filePath);
  const options = {
    useADS: args.includes('--all-strategies'),
    useMixedCase: true,
    useAttributes: true,
    useMetadata: true,
    useNesting: true,
    useSpecialChars: true
  };

  try {
    const obfuscator = new FileObfuscator(options);
    const result = obfuscator.obfuscate(filePath, outputDir);

    console.log('Obfuscation Complete!');
    console.log(JSON.stringify(result, null, 2));

    if (args.includes('--report')) {
      const reportPath = obfuscator.saveReport(path.join(outputDir, 'obfuscation-report.json'));
      console.log(`Report saved to: ${reportPath}`);
    }
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}
