/**
 * File Obfuscator - Test Suite
 */

const FileObfuscator = require('./file-obfuscator');
const fs = require('fs');
const path = require('path');
const assert = require('assert');

// Test configuration
const TEST_DIR = '/tmp/obfuscator-tests';
const OUTPUT_DIR = path.join(TEST_DIR, 'output');

// Setup
function setup() {
  if (!fs.existsSync(TEST_DIR)) {
    fs.mkdirSync(TEST_DIR, { recursive: true });
  }
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }
}

// Cleanup
function cleanup() {
  try {
    const removeDir = (dir) => {
      if (fs.existsSync(dir)) {
        fs.readdirSync(dir).forEach(file => {
          const filePath = path.join(dir, file);
          if (fs.lstatSync(filePath).isDirectory()) {
            removeDir(filePath);
          } else {
            fs.unlinkSync(filePath);
          }
        });
        fs.rmdirSync(dir);
      }
    };
    removeDir(TEST_DIR);
  } catch (error) {
    console.warn('Cleanup warning:', error.message);
  }
}

/**
 * Test 1: Basic instantiation
 */
function test_instantiation() {
  const obfuscator = new FileObfuscator();
  assert(obfuscator instanceof FileObfuscator);
  assert(obfuscator.strategies.length > 0);
  console.log('✓ Test 1: Instantiation passed');
}

/**
 * Test 2: File obfuscation with mixed case
 */
function test_mixedCaseObfuscation() {
  const testFile = path.join(TEST_DIR, 'test_file.txt');
  const testContent = 'This is test content';
  fs.writeFileSync(testFile, testContent);

  const obfuscator = new FileObfuscator({ useMixedCase: true });
  const result = obfuscator.obfuscate(testFile, OUTPUT_DIR);

  assert(result.originalName === 'test_file.txt');
  assert(result.strategies.includes('mixedCaseNames'));

  const mixedCaseResult = result.obfuscatedPaths.find(p => p.strategy === 'mixedCaseNames');
  assert(mixedCaseResult !== undefined);
  assert(mixedCaseResult.obfuscatedName !== 'test_file.txt');
  assert(fs.existsSync(mixedCaseResult.location));

  console.log('✓ Test 2: Mixed case obfuscation passed');
}

/**
 * Test 3: Deep nesting
 */
function test_deepNesting() {
  const testFile = path.join(TEST_DIR, 'nested_test.txt');
  fs.writeFileSync(testFile, 'Nested content');

  const obfuscator = new FileObfuscator({ useNesting: true });
  const result = obfuscator.obfuscate(testFile, OUTPUT_DIR);

  const nestingResult = result.obfuscatedPaths.find(p => p.strategy === 'deepNesting');
  assert(nestingResult !== undefined);
  assert(nestingResult.nestingDepth === 6);
  assert(fs.existsSync(nestingResult.location));

  const depth = nestingResult.location.split(path.sep).length - OUTPUT_DIR.split(path.sep).length;
  assert(depth >= 6);

  console.log('✓ Test 3: Deep nesting passed');
}

/**
 * Test 4: Metadata manipulation
 */
function test_metadataManipulation() {
  const testFile = path.join(TEST_DIR, 'metadata_test.txt');
  fs.writeFileSync(testFile, 'Metadata test');

  const obfuscator = new FileObfuscator({ useMetadata: true });
  const result = obfuscator.obfuscate(testFile, OUTPUT_DIR);

  const metadataResult = result.obfuscatedPaths.find(p => p.strategy === 'metadataManipulation');
  assert(metadataResult !== undefined);
  assert(metadataResult.fakeTimestamp === '2020-01-01');

  const stats = fs.statSync(metadataResult.location);
  const modTime = new Date(stats.mtimeMs);
  assert(modTime.getFullYear() === 2020);

  console.log('✓ Test 4: Metadata manipulation passed');
}

/**
 * Test 5: Steganography embedding and extraction
 */
function test_steganography() {
  const secretFile = path.join(TEST_DIR, 'secret.txt');
  const carrierFile = path.join(TEST_DIR, 'carrier.bin');
  const outputFile = path.join(OUTPUT_DIR, 'hidden.bin');
  const extractedFile = path.join(OUTPUT_DIR, 'extracted.txt');

  const secretContent = 'SECRET_DATA_12345';
  const carrierContent = Buffer.from([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46]);

  fs.writeFileSync(secretFile, secretContent);
  fs.writeFileSync(carrierFile, carrierContent);

  const obfuscator = new FileObfuscator();

  // Embed
  const embedding = obfuscator.steganographyEmbed(secretFile, carrierFile, outputFile);
  assert(fs.existsSync(outputFile));
  assert(embedding.strategy === 'steganography');

  // Extract
  const carrierSize = fs.statSync(carrierFile).size;
  const extraction = obfuscator.steganographyExtract(outputFile, carrierSize, extractedFile);
  assert(fs.existsSync(extractedFile));

  const extractedContent = fs.readFileSync(extractedFile, 'utf8');
  assert(extractedContent === secretContent);

  console.log('✓ Test 5: Steganography passed');
}

/**
 * Test 6: Polymorphic wrapping
 */
function test_polymorphicWrapping() {
  const testFile = path.join(TEST_DIR, 'wrap_test.bin');
  const originalContent = Buffer.from('TEST_PAYLOAD_DATA');
  fs.writeFileSync(testFile, originalContent);

  const obfuscator = new FileObfuscator();

  // Test Base64
  const base64Output = path.join(OUTPUT_DIR, 'wrapped.b64');
  const base64Result = obfuscator.createPolymorphicWrapper(testFile, base64Output, 'base64');
  assert(fs.existsSync(base64Output));
  assert(base64Result.type === 'base64');
  const base64Content = fs.readFileSync(base64Output, 'utf8');
  assert(Buffer.from(base64Content, 'base64').toString() === 'TEST_PAYLOAD_DATA');

  // Test Hex
  const hexOutput = path.join(OUTPUT_DIR, 'wrapped.hex');
  const hexResult = obfuscator.createPolymorphicWrapper(testFile, hexOutput, 'hex');
  assert(fs.existsSync(hexOutput));
  assert(hexResult.type === 'hex');

  // Test Chunks
  const chunksOutput = path.join(OUTPUT_DIR, 'wrapped.json');
  const chunksResult = obfuscator.createPolymorphicWrapper(testFile, chunksOutput, 'chunks');
  assert(fs.existsSync(chunksOutput));
  assert(chunksResult.type === 'chunks');

  console.log('✓ Test 6: Polymorphic wrapping passed');
}

/**
 * Test 7: Mapping and reports
 */
function test_mappingAndReports() {
  const file1 = path.join(TEST_DIR, 'file1.txt');
  const file2 = path.join(TEST_DIR, 'file2.txt');
  fs.writeFileSync(file1, 'Content 1');
  fs.writeFileSync(file2, 'Content 2');

  const obfuscator = new FileObfuscator({ useMixedCase: true });
  obfuscator.obfuscate(file1, OUTPUT_DIR);
  obfuscator.obfuscate(file2, OUTPUT_DIR);

  // Test mapping
  const mapping = obfuscator.getMapping();
  assert(Object.keys(mapping).length === 2);

  const mappingFile = path.join(OUTPUT_DIR, 'mapping.json');
  obfuscator.saveMapping(mappingFile);
  assert(fs.existsSync(mappingFile));

  const savedMapping = JSON.parse(fs.readFileSync(mappingFile, 'utf8'));
  assert(Object.keys(savedMapping).length === 2);

  // Test report
  const report = obfuscator.generateReport();
  assert(report.summary.totalFiles === 2);
  assert(report.summary.totalObfuscations > 0);

  const reportFile = path.join(OUTPUT_DIR, 'report.json');
  obfuscator.saveReport(reportFile);
  assert(fs.existsSync(reportFile));

  console.log('✓ Test 7: Mapping and reports passed');
}

/**
 * Test 8: Custom options
 */
function test_customOptions() {
  const testFile = path.join(TEST_DIR, 'custom_test.txt');
  fs.writeFileSync(testFile, 'Custom test');

  // Test with selective strategies
  const obfuscator = new FileObfuscator({
    useMixedCase: true,
    useNesting: true,
    useAttributes: false,
    useMetadata: false,
    useSpecialChars: false
  });

  const result = obfuscator.obfuscate(testFile, OUTPUT_DIR);

  // Should have mixed case and nesting
  const strategies = result.obfuscatedPaths.map(p => p.strategy);
  assert(strategies.includes('mixedCaseNames'));
  assert(strategies.includes('deepNesting'));
  assert(!strategies.includes('fileAttributes'));
  assert(!strategies.includes('metadataManipulation'));

  console.log('✓ Test 8: Custom options passed');
}

/**
 * Test 9: Hash consistency
 */
function test_hashConsistency() {
  const testFile = path.join(TEST_DIR, 'hash_test.txt');
  const testContent = 'Hash test content';
  fs.writeFileSync(testFile, testContent);

  const obfuscator = new FileObfuscator();
  const result = obfuscator.obfuscate(testFile, OUTPUT_DIR);

  assert(result.metadata.hash !== undefined);
  assert(result.metadata.hash.length === 64); // SHA256 hex length

  // Verify hash is consistent
  const obfuscator2 = new FileObfuscator();
  const result2 = obfuscator2.obfuscate(testFile, OUTPUT_DIR);
  assert(result.metadata.hash === result2.metadata.hash);

  console.log('✓ Test 9: Hash consistency passed');
}

/**
 * Test 10: Error handling
 */
function test_errorHandling() {
  const obfuscator = new FileObfuscator();

  // Test non-existent file
  try {
    obfuscator.obfuscate('/non/existent/file.txt', OUTPUT_DIR);
    assert.fail('Should have thrown error');
  } catch (error) {
    assert(error.message.includes('File not found'));
  }

  console.log('✓ Test 10: Error handling passed');
}

/**
 * Test 11: File content preservation
 */
function test_contentPreservation() {
  const testFile = path.join(TEST_DIR, 'content_test.bin');
  const originalContent = Buffer.from([0x00, 0x01, 0x02, 0x03, 0xFF]);
  fs.writeFileSync(testFile, originalContent);

  const obfuscator = new FileObfuscator({ useNesting: true, useMixedCase: true });
  const result = obfuscator.obfuscate(testFile, OUTPUT_DIR);

  // Check that obfuscated files contain the same content
  result.obfuscatedPaths.forEach(obf => {
    if (fs.existsSync(obf.location)) {
      const obfuscatedContent = fs.readFileSync(obf.location);
      assert(obfuscatedContent.equals(originalContent));
    }
  });

  console.log('✓ Test 11: Content preservation passed');
}

/**
 * Test 12: Multiple strategy combinations
 */
function test_multipleStrategies() {
  const testFile = path.join(TEST_DIR, 'multi_test.txt');
  fs.writeFileSync(testFile, 'Multiple strategies test');

  const obfuscator = new FileObfuscator({
    useMixedCase: true,
    useAttributes: true,
    useMetadata: true,
    useNesting: true,
    useSpecialChars: true
  });

  const result = obfuscator.obfuscate(testFile, OUTPUT_DIR);

  // Should have multiple obfuscated paths
  assert(result.obfuscatedPaths.length >= 3);

  // All should be different
  const locations = result.obfuscatedPaths.map(p => p.location);
  const uniqueLocations = new Set(locations);
  assert(uniqueLocations.size === locations.length);

  console.log('✓ Test 12: Multiple strategies passed');
}

/**
 * Run all tests
 */
function runAllTests() {
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║   FILE OBFUSCATOR - TEST SUITE                             ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  setup();

  try {
    test_instantiation();
    test_mixedCaseObfuscation();
    test_deepNesting();
    test_metadataManipulation();
    test_steganography();
    test_polymorphicWrapping();
    test_mappingAndReports();
    test_customOptions();
    test_hashConsistency();
    test_errorHandling();
    test_contentPreservation();
    test_multipleStrategies();

    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║   ALL TESTS PASSED ✓                                       ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    return true;
  } catch (error) {
    console.error('\n✗ TEST FAILED:', error.message);
    console.error(error.stack);
    return false;
  } finally {
    cleanup();
  }
}

// Export tests
module.exports = {
  test_instantiation,
  test_mixedCaseObfuscation,
  test_deepNesting,
  test_metadataManipulation,
  test_steganography,
  test_polymorphicWrapping,
  test_mappingAndReports,
  test_customOptions,
  test_hashConsistency,
  test_errorHandling,
  test_contentPreservation,
  test_multipleStrategies,
  runAllTests
};

// Run if executed directly
if (require.main === module) {
  const success = runAllTests();
  process.exit(success ? 0 : 1);
}
