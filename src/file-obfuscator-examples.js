/**
 * File Obfuscator - Usage Examples and Test Cases
 */

const FileObfuscator = require('./file-obfuscator');
const fs = require('fs');
const path = require('path');

/**
 * Example 1: Basic file obfuscation with all strategies
 */
function example1_basicObfuscation() {
  console.log('\n=== Example 1: Basic File Obfuscation ===\n');

  // Create a test file
  const testFile = '/tmp/example1_secret.txt';
  fs.writeFileSync(testFile, 'This is a secret message!');

  // Create obfuscator
  const obfuscator = new FileObfuscator({
    useMixedCase: true,
    useAttributes: true,
    useMetadata: true,
    useNesting: true,
    useSpecialChars: true
  });

  // Obfuscate the file
  const result = obfuscator.obfuscate(testFile, '/tmp/obfuscated');

  console.log('Original file:', testFile);
  console.log('Obfuscated paths:', result.obfuscatedPaths.length);
  result.obfuscatedPaths.forEach((p, i) => {
    console.log(`  ${i + 1}. [${p.strategy}] ${p.obfuscatedName || p.location}`);
  });

  return result;
}

/**
 * Example 2: Mixed case filename obfuscation
 */
function example2_mixedCaseNames() {
  console.log('\n=== Example 2: Mixed Case Name Obfuscation ===\n');

  const testFile = '/tmp/example2_config.txt';
  fs.writeFileSync(testFile, 'configuration data');

  const obfuscator = new FileObfuscator({ useMixedCase: true });

  // Apply only mixed case strategy
  const result = obfuscator.obfuscate(testFile, '/tmp/obfuscated');
  const mixedCaseResult = result.obfuscatedPaths.find(p => p.strategy === 'mixedCaseNames');

  if (mixedCaseResult) {
    console.log('Original name:', mixedCaseResult.originalName);
    console.log('Obfuscated name:', mixedCaseResult.obfuscatedName);
    console.log('File location:', mixedCaseResult.location);
  }

  return result;
}

/**
 * Example 3: Deep nesting strategy
 */
function example3_deepNesting() {
  console.log('\n=== Example 3: Deep Nesting Obfuscation ===\n');

  const testFile = '/tmp/example3_data.bin';
  fs.writeFileSync(testFile, Buffer.from([0x01, 0x02, 0x03, 0x04]));

  const obfuscator = new FileObfuscator({ useNesting: true });
  const result = obfuscator.obfuscate(testFile, '/tmp/obfuscated');

  const nestingResult = result.obfuscatedPaths.find(p => p.strategy === 'deepNesting');

  if (nestingResult) {
    console.log('Original file:', testFile);
    console.log('Hidden in directory:', nestingResult.nestingPath);
    console.log('Nesting depth:', nestingResult.nestingDepth);
    console.log('Final location:', nestingResult.location);
  }

  return result;
}

/**
 * Example 4: Steganography - embed file in carrier
 */
function example4_steganography() {
  console.log('\n=== Example 4: Steganography File Embedding ===\n');

  // Create a secret file
  const secretFile = '/tmp/example4_secret.txt';
  fs.writeFileSync(secretFile, 'TOP SECRET DATA');

  // Create an innocent-looking carrier file (e.g., a fake image)
  const carrierFile = '/tmp/example4_carrier.jpg';
  fs.writeFileSync(carrierFile, Buffer.from([0xFF, 0xD8, 0xFF, 0xE0])); // JPEG header

  // Embed secret in carrier
  const obfuscator = new FileObfuscator();
  const embedding = obfuscator.steganographyEmbed(
    secretFile,
    carrierFile,
    '/tmp/obfuscated/innocent_photo.jpg'
  );

  console.log('Strategy:', embedding.strategy);
  console.log('Carrier file:', embedding.carrierFile);
  console.log('Secret file:', embedding.secretFile);
  console.log('Combined size:', embedding.totalSize, 'bytes');
  console.log('Output:', embedding.outputPath);

  // Extract the secret back
  const carrierSize = fs.statSync(carrierFile).size;
  const extracted = obfuscator.steganographyExtract(
    embedding.outputPath,
    carrierSize,
    '/tmp/obfuscated/extracted_secret.txt'
  );

  console.log('\nExtraction:');
  console.log('Extracted file:', extracted.extractedFile);
  console.log('Secret size:', extracted.size, 'bytes');

  return embedding;
}

/**
 * Example 5: Polymorphic file wrapping
 */
function example5_polymorphicWrapper() {
  console.log('\n=== Example 5: Polymorphic File Wrapping ===\n');

  const testFile = '/tmp/example5_payload.bin';
  fs.writeFileSync(testFile, 'Executable payload data');

  const obfuscator = new FileObfuscator();

  // Wrap in base64
  const base64Wrap = obfuscator.createPolymorphicWrapper(
    testFile,
    '/tmp/obfuscated/payload.b64',
    'base64'
  );

  console.log('Base64 Wrapping:');
  console.log('  Original size:', base64Wrap.originalSize, 'bytes');
  console.log('  Wrapped size:', base64Wrap.wrappedSize, 'bytes');
  console.log('  Location:', base64Wrap.wrappedPath);

  // Wrap in hex
  const hexWrap = obfuscator.createPolymorphicWrapper(
    testFile,
    '/tmp/obfuscated/payload.hex',
    'hex'
  );

  console.log('\nHex Wrapping:');
  console.log('  Original size:', hexWrap.originalSize, 'bytes');
  console.log('  Wrapped size:', hexWrap.wrappedSize, 'bytes');
  console.log('  Location:', hexWrap.wrappedPath);

  // Wrap in chunked format
  const chunkedWrap = obfuscator.createPolymorphicWrapper(
    testFile,
    '/tmp/obfuscated/payload.chunks.json',
    'chunks'
  );

  console.log('\nChunked Wrapping:');
  console.log('  Original size:', chunkedWrap.originalSize, 'bytes');
  console.log('  Wrapped size:', chunkedWrap.wrappedSize, 'bytes');
  console.log('  Location:', chunkedWrap.wrappedPath);

  return { base64Wrap, hexWrap, chunkedWrap };
}

/**
 * Example 6: Obfuscation with mapping and report
 */
function example6_mappingAndReport() {
  console.log('\n=== Example 6: Obfuscation Mapping and Report ===\n');

  // Create multiple test files
  const files = [
    { path: '/tmp/example6_file1.txt', content: 'Content 1' },
    { path: '/tmp/example6_file2.txt', content: 'Content 2' },
    { path: '/tmp/example6_file3.txt', content: 'Content 3' }
  ];

  files.forEach(f => fs.writeFileSync(f.path, f.content));

  const obfuscator = new FileObfuscator({
    useMixedCase: true,
    useMetadata: true,
    useNesting: true
  });

  // Obfuscate all files
  files.forEach(f => {
    obfuscator.obfuscate(f.path, '/tmp/obfuscated');
  });

  // Get mapping
  const mapping = obfuscator.getMapping();
  console.log('Files obfuscated:', Object.keys(mapping).length);
  console.log('\nMapping structure:');
  Object.entries(mapping).forEach(([name, record]) => {
    console.log(`  ${name}:`);
    console.log(`    - Strategies: ${record.strategies.join(', ')}`);
    console.log(`    - Obfuscations: ${record.obfuscatedPaths.length}`);
  });

  // Save mapping
  const mappingPath = '/tmp/obfuscated/mapping.json';
  obfuscator.saveMapping(mappingPath);
  console.log(`\nMapping saved to: ${mappingPath}`);

  // Generate and save report
  const reportPath = obfuscator.saveReport('/tmp/obfuscated/report.json');
  console.log(`Report saved to: ${reportPath}`);

  const report = obfuscator.generateReport();
  console.log('\nReport Summary:');
  console.log(`  Total files: ${report.summary.totalFiles}`);
  console.log(`  Total obfuscations: ${report.summary.totalObfuscations}`);
  console.log(`  Strategies used: ${report.strategiesUsed.join(', ')}`);

  return { mapping, report };
}

/**
 * Example 7: Custom options and selective strategies
 */
function example7_customOptions() {
  console.log('\n=== Example 7: Custom Options and Selective Strategies ===\n');

  const testFile = '/tmp/example7_custom.txt';
  fs.writeFileSync(testFile, 'Custom obfuscation example');

  // Create obfuscator with specific strategies
  const obfuscator = new FileObfuscator({
    useMixedCase: true,
    useAttributes: false, // Disable attributes
    useMetadata: false,   // Disable metadata
    useNesting: true,
    useSpecialChars: true,
    timestamp: Date.now()
  });

  const result = obfuscator.obfuscate(testFile, '/tmp/obfuscated');

  console.log('Enabled strategies:', obfuscator.strategies);
  console.log('Strategies applied:', result.strategies);
  console.log('Obfuscated paths created:', result.obfuscatedPaths.length);

  result.obfuscatedPaths.forEach((p, i) => {
    console.log(`\n  Strategy ${i + 1}: ${p.strategy}`);
    console.log(`    Type: ${p.type}`);
    console.log(`    Description: ${p.description}`);
    if (p.obfuscatedName) {
      console.log(`    Name: ${p.obfuscatedName}`);
    }
  });

  return result;
}

/**
 * Example 8: Advanced obfuscation pipeline
 */
function example8_advancedPipeline() {
  console.log('\n=== Example 8: Advanced Obfuscation Pipeline ===\n');

  const testFile = '/tmp/example8_original.bin';
  const payload = Buffer.from('SENSITIVE_PAYLOAD_DATA_12345');
  fs.writeFileSync(testFile, payload);

  const obfuscator = new FileObfuscator({ useNesting: true, useMixedCase: true });

  // Step 1: Create polymorphic wrapper
  console.log('Step 1: Creating polymorphic wrapper...');
  const wrappedPath = '/tmp/obfuscated/step1_wrapped.hex';
  const wrapper = obfuscator.createPolymorphicWrapper(testFile, wrappedPath, 'hex');
  console.log(`  Result: ${path.basename(wrappedPath)}`);

  // Step 2: Obfuscate the wrapped file
  console.log('\nStep 2: Obfuscating wrapped file...');
  const obfuscated = obfuscator.obfuscate(wrappedPath, '/tmp/obfuscated');
  console.log(`  Obfuscated paths created: ${obfuscated.obfuscatedPaths.length}`);

  // Step 3: Create steganographic embedding
  console.log('\nStep 3: Creating steganographic carrier...');
  const carrierFile = '/tmp/example8_carrier.txt';
  fs.writeFileSync(carrierFile, 'This is an innocent readme file.');

  const finalObfuscatedFile = obfuscated.obfuscatedPaths.find(
    p => fs.existsSync(p.location)
  )?.location;

  if (finalObfuscatedFile) {
    const stego = obfuscator.steganographyEmbed(
      finalObfuscatedFile,
      carrierFile,
      '/tmp/obfuscated/step3_final_carrier.txt'
    );
    console.log(`  Result: ${path.basename(stego.outputPath)}`);
  }

  // Step 4: Generate report
  console.log('\nStep 4: Generating obfuscation report...');
  const report = obfuscator.generateReport();
  console.log(`  Files processed: ${report.summary.totalFiles}`);
  console.log(`  Total obfuscations: ${report.summary.totalObfuscations}`);

  return { wrapper, obfuscated, report };
}

/**
 * Run all examples
 */
function runAllExamples() {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║     FILE OBFUSCATOR - COMPREHENSIVE EXAMPLES              ║');
  console.log('╚════════════════════════════════════════════════════════════╝');

  // Ensure output directory exists
  if (!fs.existsSync('/tmp/obfuscated')) {
    fs.mkdirSync('/tmp/obfuscated', { recursive: true });
  }

  const results = {
    example1: example1_basicObfuscation(),
    example2: example2_mixedCaseNames(),
    example3: example3_deepNesting(),
    example4: example4_steganography(),
    example5: example5_polymorphicWrapper(),
    example6: example6_mappingAndReport(),
    example7: example7_customOptions(),
    example8: example8_advancedPipeline()
  };

  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║                   EXAMPLES COMPLETED                       ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  return results;
}

// Export for use as module
module.exports = {
  example1_basicObfuscation,
  example2_mixedCaseNames,
  example3_deepNesting,
  example4_steganography,
  example5_polymymorphicWrapper: example5_polymorphicWrapper,
  example6_mappingAndReport,
  example7_customOptions,
  example8_advancedPipeline,
  runAllExamples
};

// Run if executed directly
if (require.main === module) {
  try {
    runAllExamples();
  } catch (error) {
    console.error('Error running examples:', error);
    process.exit(1);
  }
}
